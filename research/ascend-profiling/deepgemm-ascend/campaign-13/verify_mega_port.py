"""Verify the isolated 28-Cube MegaMoE evidence, separately from expert data."""
import hashlib
import json
import os
from pathlib import Path

root = Path(__file__).resolve().parent / 'runs/mega-port28-experiment'
if os.name == 'nt':
    root = Path('\\\\?\\' + str(root))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

manifest = json.loads((root / 'evidence-manifest.json').read_text())
for name, expected in manifest.items():
    path = root / name
    assert path.is_file() and path.stat().st_size == expected['bytes'] and sha(path) == expected['sha256'], name

case_dirs = [root / 'smoke-range0', *(p for p in (root / 'cases').iterdir() if p.is_dir()), root / 'repeat-range0-2']
cases = []
raw_count = 0
for path in case_dirs:
    result = json.loads((path / 'result.json').read_text())
    assert result['status'] == 'passed' and result['experimental_port']
    assert result['replay_mode'] == 'range' and result['profiler_warmup'] == 0
    assert result['capture']['op_type'] == 'mix'
    for name, expected in result['raw_files'].items():
        raw = path / name
        assert raw.stat().st_size == expected['bytes'] and sha(raw) == expected['sha256'], str(raw)
        raw_count += 1
    before = json.loads((path / 'prepare.json').read_text())
    after = json.loads((path / 'profile.json').read_text())
    for key in ('input_hashes', 'reference_sha256', 'output_sha256'):
        assert before[key] == after[key], (str(path), key)
    c = result['case']
    zero = hashlib.sha256(bytes(c['tokens'] * c['hidden'] * 2)).hexdigest()
    assert before['output_sha256'] != zero, 'nonzero-input output was all zero: ' + str(path)
    cases.append((c['id'], before, result))

first, repeat = cases[0], cases[-1]
assert first[0] == repeat[0]
for key in ('input_hashes', 'reference_sha256', 'output_sha256'):
    assert first[1][key] == repeat[1][key], key
assert first[2]['capture']['jit_binary_sha256'] == repeat[2]['capture']['jit_binary_sha256']
binary = next((root / 'artifacts').glob('_C*.so'))
build = json.loads((root / 'build-result.json').read_text())
assert sha(binary) == build['extension_sha256']
print(json.dumps({'evidence_files': len(manifest), 'raw_files': raw_count,
                  'captures': len(cases), 'unique_cases': len({c[0] for c in cases}),
                  'repeated_input_output_and_jit_match': True}, indent=2))
