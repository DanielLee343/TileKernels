"""Verify archived case identities and raw bytes; report failures without hiding them."""
import hashlib
import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

paths=sorted((root/'runs').glob('campaign-*/*/result.json'))
if not paths:raise SystemExit('no archived results')
ok=[];fail=[];count=0
for p in paths:
    result=json.loads(p.read_text());case=result['case'];case_id=case['id']
    if p.parent.name!=case_id:raise ValueError('case directory mismatch: '+case_id)
    if result['status']!='passed':fail.append((case_id,result.get('error','')));continue
    before=json.loads((p.parent/'prepare.json').read_text());after=json.loads((p.parent/'profile.json').read_text())
    if any(x['case_id']!=case_id or x['status']!='passed' for x in (before,after)):
        raise ValueError('upstream validation missing: '+case_id)
    if before['target_input']!=after['target_input']:raise ValueError('target input mismatch: '+case_id)
    capture=result['capture']
    if case['target'] not in capture['op_name']:raise ValueError('kernel mismatch: '+case_id)
    if sha(p.parent/'jit/kernel.o')!=capture['jit_binary_sha256']:raise ValueError('binary mismatch: '+case_id)
    for name,meta in result['raw_files'].items():
        q=p.parent/name
        if not q.is_file() or q.stat().st_size!=meta['bytes'] or sha(q)!=meta['sha256']:
            raise ValueError('raw file mismatch: '+str(q))
        count+=1
    if not result['raw_files']:raise ValueError('missing raw files: '+case_id)
    ok.append((case_id,case['target']))
diagnostic_count=0
manifest=root/'diagnostic-file-hashes.json'
if manifest.is_file():
    for name,meta in json.loads(manifest.read_text()).items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file() or path.stat().st_size!=meta['bytes'] or sha(path)!=meta['sha256']:
            raise ValueError('diagnostic file mismatch: '+str(path))
        diagnostic_count+=1
print(json.dumps({'passed_captures':len(ok),'unique_passed_case_ids':len({x[0] for x in ok}),
                  'target_names':sorted({x[1] for x in ok}),
                  'failed_attempts':len(fail),'failed_ids':sorted({x[0] for x in fail}),
                  'raw_files_checked':count,'diagnostic_files_checked':diagnostic_count},indent=2))
if '--require-all-passed' in sys.argv and fail:raise SystemExit(1)
