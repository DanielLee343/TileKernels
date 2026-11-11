"""Evaluate emitted TopK store sizes against original PMU and binary evidence."""

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def read_json(p):
    return json.loads(p.read_text())


def split_arguments(value):
    arguments = []
    depth = 0
    start = 0
    for i, char in enumerate(value):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == ',' and depth == 0:
            arguments.append(value[start:i].strip())
            start = i + 1
    assert depth == 0
    return arguments + [value[start:].strip()]


def store_functions(source):
    stores = []
    parents = []
    for line in source.splitlines():
        code = line.strip()
        depth = len(line) - len(line.lstrip())
        while parents and parents[-1][0] >= depth:
            parents.pop()
        if code.endswith('{') and re.match(r'^(for|if) \(', code):
            parents.append((depth, code))
        if not code.startswith('asc_copy_ub2gm_align('):
            continue
        assert code.endswith(');') and len(parents) >= 2
        assert parents[0][1].startswith('for (int32_t w = 0;')
        assert all('else' not in text for _, text in parents)
        dst, _, bursts, width, _, _, pitch = split_arguments(code.removeprefix('asc_copy_ub2gm_align(')[:-2])
        tensor, = re.findall(r'\b(topk_idx_view|unmapped_idx_view|topk_weights|scores)\b', dst)
        stores.append((tensor, [text for _, text in parents], bursts, width, pitch))
    return stores


def evaluate(stores, n, stride, folder):
    impl = ['#include <algorithm>', '#include <cstdint>', '#include <iostream>',
            'using std::min; using std::max;', 'int main() {',
            f'const int32_t num_tokens = {n};', f'const int32_t unmapped_topk_idx_stride = {stride};',
            'for (int32_t block_idx = 0; block_idx < 56; ++block_idx) {']
    for i, (_, parents, bursts, width, pitch) in enumerate(stores):
        impl.extend(parents)
        impl.append(f'std::cout << block_idx << " " << {i} << " " << ({bursts}) << " "'
                    f' << ({width}) << " " << ({pitch}) << "\\n";')
        impl.extend('}' for _ in parents)
    impl.extend(['}', '}'])
    cpp = folder / 'store-evaluation.cpp'
    binary = folder / 'store-evaluation'
    cpp.write_text('\n'.join(impl) + '\n')
    subprocess.run(['g++', '-std=c++17', '-O2', str(cpp), '-o', str(binary)], check=True)
    try:
        result = subprocess.check_output([binary], text=True)
    finally:
        binary.unlink()
    return [tuple(map(int, line.split())) for line in result.splitlines()]


def audit(case, runs, original, objdump):
    new = runs / case
    application, = new.glob('application-*.json')
    generated, = new.glob('generated-kernel-*.cpp')
    identity = read_json(application)
    history = read_json(original / case / 'default.json')
    assert identity['status'] == history['status'] == 'passed'
    assert identity['correctness'] == history['correctness'] == 'passed_upstream_full_moe_forward_test'
    assert identity['matched'] == history['matched'] == 1 and identity['target_native_calls'] == 1
    for key in ('params', 'inputs', 'runtime_kernel', 'route_counts', 'scalar_inputs'):
        assert identity[key] == history[key], key
    original_cpp = generated.read_bytes()
    assert sha(generated) == identity['source_sha256']
    upstream = rb'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/'
    checkout = rb'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/'
    assert history['source_sha256'] in (sha(generated), hashlib.sha256(original_cpp.replace(checkout, upstream)).hexdigest())
    addresses, = new.glob('tensor-addresses-*.json')
    buffers = read_json(addresses)
    n = buffers[0]['shape'][0]
    stride = buffers[9]['stride'][0] if buffers[9] else 0
    outputs = {name: buffers[index]['logical_bytes'] for name, index in
               [('topk_idx_view', 8), ('unmapped_idx_view', 9), ('topk_weights', 10), ('scores', 11)]
               if buffers[index] is not None}
    stores = store_functions(original_cpp.decode())
    assert set(outputs) == {s[0] for s in stores}
    events = evaluate(stores, n, stride, new)
    memory, = (original / case / 'capture').rglob('Memory.csv')
    binary, = (original / case / 'capture').rglob('aicore_binary.o')
    isa = subprocess.check_output([objdump, '-d', binary], text=True)
    pcs = re.findall(r'^\s*([0-9a-f]+):[^\n]*\b(MOV_\w+_TO_OUT\w*)\b', isa, re.MULTILINE)
    assert len(pcs) == len(stores) and all(op == 'MOV_UB_TO_OUT_ALIGN_V2' for _, op in pcs), pcs
    counters, requested, ub, by_output = Counter(), Counter(), Counter(), Counter()
    for block, index, bursts, width, pitch in events:
        assert 0 <= block < 56 and bursts > 0 and width > 0 and pitch >= width
        counters[block] += 1
        requested[block] += bursts * width
        ub[block] += ((bursts * width + 31) // 32) * 32 if pitch == width else bursts * (((width + 31) // 32) * 32)
        by_output[stores[index][0]] += bursts * width
    assert by_output == outputs, (by_output, outputs)
    with memory.open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 56
    for i, row in enumerate(rows):
        assert row['block_id'] == str(i) and row['sub_block_id'] == 'vector0'
        assert int(row['aiv_mte3_instructions']) == 2 + counters[i], (i, row['aiv_mte3_instructions'], counters[i])
    return {'case': case, 'verified_cores': 56, 'binary_sha256': sha(binary), 'memory_sha256': sha(memory),
            'historical_source_sha256': history['source_sha256'], 'generated_source_sha256': sha(generated),
            'source_pcs': [pc for pc, _ in pcs], 'output_requested_bytes': by_output,
            'requested_bytes': {i: requested[i] for i in range(56)}, 'ub_side_bytes': {i: ub[i] for i in range(56)}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path)
    parser.add_argument('original', type=Path)
    parser.add_argument('objdump', type=Path)
    parser.add_argument('cases', nargs='+')
    args = parser.parse_args()
    for case in args.cases:
        result = audit(case, args.runs, args.original, args.objdump)
        (args.runs / case / 'original-store-audit.json').write_text(json.dumps(result, indent=2) + '\n')
        print(case, sum(result['requested_bytes'].values()), sum(result['ub_side_bytes'].values()), flush=True)
