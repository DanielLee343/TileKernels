"""Independently verify the pilot snapshot and every archived raw file."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = json.loads((ROOT/'cases.json').read_text())
    expected = {c['id']: c for c in manifest['cases']}
    assert len(expected) == len(manifest['cases'])
    seen = set(); raw_count = 0
    for batch in sorted((ROOT/'runs').iterdir()):
        if not batch.is_dir(): continue
        meta = json.loads((batch/'batch.json').read_text())
        assert meta['source_commit'] == manifest['source_commit']
        assert meta['manifest_sha256'] == sha(ROOT/'cases.json')
        assert meta['collector_sha256'] == sha(ROOT/'collect.py')
        for entry in meta['cases']:
            cid = entry['id']; assert cid in expected and cid not in seen
            root = batch/cid; result = json.loads((root/'result.json').read_text())
            before = json.loads((root/'prepare.json').read_text())
            after = json.loads((root/'profile.json').read_text())
            assert result['case'] == expected[cid]
            assert entry['status'] == result['status'] == before['status'] == after['status'] == 'passed'
            for record in (before, after):
                assert record['case_id'] == cid and record['threshold'] == 1e-5
                assert record['reference_finite'] and record['output_finite'] and record['diff'] < 1e-5
                assert record['checked_elements'] == expected[cid]['m']*expected[cid]['n']
                assert record['a_shape'] == [expected[cid]['m'], expected[cid]['k']]
                assert record['b_shape'] == [expected[cid]['n'], expected[cid]['k']]
                assert record['a_stride'] == [expected[cid]['k'], 1]
                assert record['b_stride'] == [expected[cid]['k'], 1]
                assert record['output_dtype'] == 'torch.'+expected[cid]['output_dtype']
            for key in ('input_a_sha256', 'input_b_sha256', 'reference_sha256', 'output_sha256'):
                assert before[key] == after[key]
            for name, item in result['raw_files'].items():
                path = (root/name).resolve(); assert path.is_relative_to(root.resolve())
                assert path.stat().st_size == item['bytes'] and sha(path) == item['sha256']
                raw_count += 1
            paths = list((root/'profile').rglob('OpBasicInfo.csv')); assert len(paths) == 1
            with paths[0].open(encoding='utf-8-sig', newline='') as f: rows = list(csv.DictReader(f))
            assert len(rows) == 1 and 'bf16_gemm_impl' in rows[0]['Op Name']
            assert rows[0]['Op Type'].lower() in ('cube', 'mix')
            assert sha(root/'jit/kernel.o') == sha(paths[0].parent/'dump/aicore_binary.o')
            seen.add(cid)
    assert seen == set(expected)
    print(f'PASS: {len(seen)} cases and {raw_count} raw profile files verified')


if __name__ == '__main__': main()
