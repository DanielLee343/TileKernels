"""Collect a bounded, auditable batch of DeepGEMM-Ascend BF16 NT cases."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parent
METRICS = ('ArithmeticUtilization', 'L2Cache', 'Memory', 'MemoryL0', 'MemoryUB',
           'PipeUtilization', 'ResourceConflictRatio')
BASELINE = '3a35326271b069b8b5bf1a754435acd6cc91575b'
THRESHOLD = 1e-5


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_case(case):
    if (not isinstance(case.get('id'), str) or not case['id'] or
        any(not isinstance(case.get(x), int) or case[x] <= 0 for x in ('m', 'n', 'k')) or
        case.get('layout') != 'nt' or case.get('accumulate') is not False or
        case.get('output_dtype') not in ('bfloat16', 'float32') or
        not isinstance(case.get('seed'), int)):
        raise ValueError('case is outside the BF16 NT non-accumulating contract')


def select_cases(cases, requested):
    if not requested: return cases
    if len(set(requested)) != len(requested): raise ValueError('duplicate selected case')
    result = [c for c in cases if c['id'] in requested]
    if len(result) != len(requested): raise ValueError('unknown selected case')
    return result


def validate_stage(record, case_id):
    if (record.get('status') != 'passed' or record.get('case_id') != case_id or
        record.get('output_finite') is not True or record.get('reference_finite') is not True or
        record.get('threshold') != THRESHOLD):
        raise ValueError('accuracy or stage identity failed')
    diff = record.get('diff')
    if not isinstance(diff, (int, float)) or not math.isfinite(diff) or diff >= THRESHOLD:
        raise ValueError('accuracy difference exceeds threshold')
    for key in ('input_a_sha256', 'input_b_sha256', 'reference_sha256', 'output_sha256'):
        if not record.get(key): raise ValueError('missing tensor digest: ' + key)


def validate_stages(before, after, case_id):
    validate_stage(before, case_id); validate_stage(after, case_id)
    for key in ('input_a_sha256', 'input_b_sha256', 'reference_sha256', 'output_sha256'):
        if before[key] != after[key]: raise ValueError('stage mismatch: ' + key)


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))


def inspect_capture(profile_root, jit_root):
    files = list(Path(profile_root).rglob('OpBasicInfo.csv'))
    if len(files) != 1: raise ValueError('expected one captured kernel; found ' + str(len(files)))
    basic = read_csv(files[0])
    if len(basic) != 1: raise ValueError('expected one OpBasicInfo record')
    item = basic[0]; kind = item.get('Op Type', '').lower()
    if kind not in ('cube', 'mix') or 'bf16_gemm_impl' not in item.get('Op Name', ''):
        raise ValueError('captured kernel is not the expected Cube GEMM')
    records = {}
    for name in METRICS:
        path = files[0].with_name(name + '.csv'); rows = read_csv(path)
        if not rows: raise ValueError('empty metric table: ' + name)
        keys = [(r.get('block_id'), r.get('sub_block_id')) for r in rows]
        if any(not all(k) for k in keys) or len(keys) != len(set(keys)):
            raise ValueError('invalid metric row keys: ' + name)
        records[name] = {'rows': len(rows), 'sha256': file_hash(path)}
    pipes = read_csv(files[0].with_name('PipeUtilization.csv'))
    cube_rows = [r for r in pipes if str(r.get('sub_block_id', '')).startswith('cube')]
    active = [r for r in cube_rows if r.get('aic_cube_time(us)') not in ('', 'NA', None)
              and float(r['aic_cube_time(us)']) > 0]
    if not active: raise ValueError('no nonzero Cube activity in PipeUtilization')
    dump = files[0].parent / 'dump'; binary = dump / 'aicore_binary.o'
    if not list(dump.glob('DeviceProf*.bin')) or not binary.is_file():
        raise ValueError('original device profiler files or captured binary missing')
    digest = file_hash(binary)
    matched = [p.parent for p in Path(jit_root).rglob('kernel.o') if file_hash(p) == digest]
    if not matched: raise ValueError('captured binary does not match any JIT binary')
    for p in matched:
        if not (p/'kernel.asc').is_file() or not (p/'meta.json').is_file():
            raise ValueError('matched JIT source or metadata is missing')
    return {'op_name': item['Op Name'], 'op_type': kind, 'block_dim': item.get('Block Dim'),
            'mix_block_dim': item.get('Mix Block Dim'), 'cube_rows': len(cube_rows),
            'cube_active_rows': len(active), 'binary_sha256': digest,
            'jit_directories': [str(p) for p in matched], 'metrics': records}


def worker(case, stage, out):
    import ctypes
    import torch
    import torch_npu  # noqa: F401
    import deep_gemm
    validate_case(case)
    torch.set_num_threads(4); torch.manual_seed(case['seed']); torch.npu.set_device(0)
    m, n, k = (case[x] for x in ('m', 'n', 'k'))
    a_cpu = torch.randn(m, k, dtype=torch.float32).to(torch.bfloat16)
    b_cpu = torch.randn(n, k, dtype=torch.float32).to(torch.bfloat16)
    dtype = torch.bfloat16 if case['output_dtype'] == 'bfloat16' else torch.float32
    expected = (a_cpu.float() @ b_cpu.float().T).to(dtype)
    a, b = a_cpu.npu(), b_cpu.npu()
    output = torch.empty((m, n), dtype=dtype, device='npu')
    def launch(): deep_gemm.bf16_gemm_nt(a, b, output)
    for _ in range(5): launch()
    torch.npu.synchronize()
    if stage == 'profile':
        api = ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
        api.mstxRangeStartA.argtypes = [ctypes.c_char_p, ctypes.c_void_p]
        api.mstxRangeStartA.restype = ctypes.c_uint64
        api.mstxRangeEnd.argtypes = [ctypes.c_uint64]; api.mstxRangeEnd.restype = None
        handle = api.mstxRangeStartA(b'deepgemm_target', ctypes.c_void_p(int(torch.npu.current_stream().npu_stream)))
        try: launch()
        finally: api.mstxRangeEnd(handle)
    else: launch()
    torch.npu.synchronize(); actual = output.cpu(); actual_f = actual.float(); expected_f = expected.float()
    finite_output = bool(torch.isfinite(actual_f).all().item())
    finite_expected = bool(torch.isfinite(expected_f).all().item())
    denominator = (actual_f * actual_f + expected_f * expected_f).sum()
    diff = float((1 - 2 * (actual_f * expected_f).sum() / denominator).item()) if denominator.item() else 0.0
    def tensor_hash(t): return hashlib.sha256(t.contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
    record = {'case_id': case['id'], 'stage': stage, 'input_a_sha256': tensor_hash(a_cpu),
              'input_b_sha256': tensor_hash(b_cpu), 'reference_sha256': tensor_hash(expected),
              'output_sha256': tensor_hash(actual), 'output_finite': finite_output,
              'reference_finite': finite_expected, 'diff': diff, 'threshold': THRESHOLD,
              'max_abs_error': float((actual_f - expected_f).abs().max().item()),
              'checked_elements': m*n, 'a_shape': list(a.shape), 'b_shape': list(b.shape),
              'a_stride': list(a.stride()), 'b_stride': list(b.stride()), 'output_dtype': str(dtype),
              'reference': 'CPU FP32 matmul of BF16 inputs, rounded to output dtype'}
    record['status'] = 'passed' if finite_output and finite_expected and math.isfinite(diff) and diff < THRESHOLD else 'failed'
    Path(out).write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    if record['status'] != 'passed': raise ValueError('accuracy check failed')


def run_logged(cmd, env, log, timeout=900):
    with Path(log).open('w') as stream:
        process = subprocess.Popen(cmd, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
        try: return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired: os.killpg(process.pid, signal.SIGKILL); process.wait()
            raise TimeoutError('subprocess timed out; its process group was stopped')


def device_idle(device):
    result = subprocess.run(['npu-smi', 'info', '-t', 'proc-mem', '-i', str(device)],
                            capture_output=True, text=True, timeout=30)
    return result.returncode == 0 and 'No process in device.' in result.stdout, result.stdout + result.stderr


def run_case(case, source, output, device):
    validate_case(case); output = Path(output); output.mkdir(parents=True, exist_ok=False)
    state = {'case': case, 'status': 'running', 'source_commit': BASELINE, 'physical_device': device}
    result_file = output/'result.json'
    try:
        ok, status = device_idle(device); state['device_before'] = status
        if not ok: raise RuntimeError('selected device busy or status unavailable')
        env = os.environ.copy(); env['ASCEND_RT_VISIBLE_DEVICES'] = str(device); env['PYTHONDONTWRITEBYTECODE'] = '1'
        common = [sys.executable, '-B', str(Path(__file__).resolve()), '__worker', case['id']]
        prepare = common + ['prepare', str(output/'prepare.json')]
        state['prepare_command'] = prepare
        rc = run_logged(prepare, env, output/'prepare.log'); state['prepare_exit'] = rc
        if rc: raise RuntimeError('pre-profile accuracy check failed; see prepare.log')
        before = json.loads((output/'prepare.json').read_text()); validate_stage(before, case['id'])
        command = ['msprof', 'op', '--output='+str(output/'profile'), '--aic-metrics=Default',
                   '--replay-mode=kernel', '--mstx=true', '--mstx-include=deepgemm_target',
                   '--launch-count=1', '--warm-up=5'] + common + ['profile', str(output/'profile.json')]
        state['profile_command'] = command
        rc = run_logged(command, env, output/'profile.log'); state['profile_exit'] = rc
        if rc: raise RuntimeError('profile failed; see profile.log')
        after = json.loads((output/'profile.json').read_text()); validate_stages(before, after, case['id'])
        state['capture'] = inspect_capture(output/'profile', Path(env['DG_JIT_CACHE_DIR'])/'cache')
        jit = Path(state['capture']['jit_directories'][0]); dst = output/'jit'; dst.mkdir()
        for name in ('kernel.asc', 'kernel.o', 'meta.json'): shutil.copy2(jit/name, dst/name)
        raw = [p for p in (output/'profile').rglob('*') if p.is_file()]
        state['raw_files'] = {str(p.relative_to(output)): {'sha256': file_hash(p), 'bytes': p.stat().st_size} for p in raw}
        state['device_idle_after'], state['device_after'] = device_idle(device)
        state['status'] = 'passed' if state['device_idle_after'] else 'captured_device_review'
    except Exception:
        state['status'] = 'failed'; state['error'] = traceback.format_exc()
    finally: result_file.write_text(json.dumps(state, indent=2) + '\n')
    return state


def main():
    parser = argparse.ArgumentParser(); sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('__worker'); p.add_argument('case_id'); p.add_argument('stage', choices=('prepare', 'profile')); p.add_argument('out')
    p = sub.add_parser('batch'); p.add_argument('--source', type=Path, required=True); p.add_argument('--output', type=Path, required=True); p.add_argument('--device', type=int, default=0); p.add_argument('--case', action='append')
    args = parser.parse_args(); manifest = json.loads((ROOT/'cases.json').read_text()); cases = manifest['cases']
    for case in cases: validate_case(case)
    if args.action == '__worker':
        found = [c for c in cases if c['id'] == args.case_id]
        if len(found) != 1: raise ValueError('unknown or duplicate case ID')
        worker(found[0], args.stage, args.out); return
    cases = select_cases(cases, args.case)
    head = subprocess.check_output(['git', '-C', str(args.source), 'rev-parse', 'HEAD'], text=True).strip()
    status = subprocess.check_output(['git', '-C', str(args.source), 'status', '--porcelain'], text=True)
    if head != BASELINE or status: raise RuntimeError('DeepGEMM source version or worktree differs from baseline')
    output = args.output.resolve(); output.mkdir(parents=True, exist_ok=False)
    metadata = {'source': str(args.source.resolve()), 'source_commit': head, 'source_status': status,
                'source_submodules': subprocess.check_output(['git', '-C', str(args.source), 'submodule', 'status'], text=True),
                'manifest_sha256': file_hash(ROOT/'cases.json'), 'collector_sha256': file_hash(__file__),
                'device': args.device, 'python': sys.version, 'cases': []}
    (output/'batch.json').write_text(json.dumps(metadata, indent=2) + '\n')
    for case in cases:
        state = run_case(case, args.source, output/case['id'], args.device)
        metadata['cases'].append({'id': case['id'], 'status': state['status']})
        (output/'batch.json').write_text(json.dumps(metadata, indent=2) + '\n')
        print(case['id'], state['status'], flush=True)
    if any(x['status'] != 'passed' for x in metadata['cases']): raise SystemExit(1)


if __name__ == '__main__': main()
