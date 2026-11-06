"""Verify imported bytes and selected historical profile index, without NPU."""
from hashlib import sha256
import json
from pathlib import Path

root = Path(__file__).resolve().parent / 'history' / 'puma'
manifest = json.loads((root / 'MANIFEST.json').read_text(encoding='utf8'))
for relative, info in manifest['files'].items():
    path = root / relative
    assert path.is_file(), path
    assert path.stat().st_size == info['size'], path
    assert sha256(path.read_bytes()).hexdigest() == info['sha256'], path
index = json.loads((root / 'outputs/tilekernels-profile-inventory-reset-20261105/inventory.json').read_text(encoding='utf8'))
assert len(index['profiles']) == index['selected_expert_default_captures'] == 140
profile_dirs = set()
for profile in index['profiles']:
    for info in profile['files'].values():
        path = root / info['path']
        assert path.is_file(), path
        assert sha256(path.read_bytes()).hexdigest() == info['sha256'], path
        profile_dirs.add(path.parent)
assert len(profile_dirs) == 140
plan = json.loads((root / 'outputs/tilekernels-profile-case-plan-20261106/cases.json').read_text(encoding='utf8'))
assert len(plan['groups']) == 50
assert sum(len(g['cases']) for g in plan['groups']) == 1000
print('HISTORICAL_EVIDENCE_VERIFIED')
