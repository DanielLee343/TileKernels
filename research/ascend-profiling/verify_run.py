"""Check completed starter snapshots, including original profile table hashes."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--batch', choices=('starter', 'second', 'third', 'fourth'), default='starter')
args = parser.parse_args()
root = Path(__file__).resolve().parent / ('runs/hidev-20261106-' + args.batch)
progress = json.loads((root / 'progress.json').read_text(encoding='utf8'))
passed = failed = 0
for case in progress['cases']:
    folder = root / 'cases' / case['id']
    assert folder.is_dir(), folder
    if case['status'] != 'admitted':
        failed += 1
        continue
    before = json.loads((folder / 'prepare.json').read_text(encoding='utf8'))
    after = json.loads((folder / 'default.json').read_text(encoding='utf8'))
    assert before['status'] == after['status'] == 'passed'
    assert before['source_sha256'] == after['source_sha256']
    assert before['inputs'] == after['inputs']
    assert all(x['passed'] for x in before['precision'] + after['precision'])
    for item in case['capture']['files'].values():
        file = root / item['path']
        assert file.is_file(), file
        assert hashlib.sha256(file.read_bytes()).hexdigest() == item['sha256'], file
    passed += 1
print(f'RUN_SNAPSHOT_VERIFIED admitted={passed} other={failed} status={progress["status"]}')
