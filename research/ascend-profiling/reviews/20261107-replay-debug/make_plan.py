"""Bind diagnostics to the exact 170 previously reviewed captures."""
import hashlib
import json
from pathlib import Path

REPO=Path(__file__).resolve().parents[4]
review=json.loads((REPO/'research/ascend-profiling/reviews/20261107-review/case-review.json').read_text())
items=[]
for case in review['cases']:
    if case['review_disposition']!='retain_inplace_restoration_review':
        continue
    for cap in case['captures']:
        result=json.loads((REPO/cap['result']).read_text())
        record=json.loads((REPO/cap['default']).read_text())
        cmd=result['default_command']
        assert cmd[:2]==['msprof','op'] and '--replay-mode=kernel' in cmd and '--warm-up=5' in cmd
        items.append({'family':case['family'],'case_id':case['case_id'],'capture_id':cap['capture_id'],
            'original_result':cap['result'],'original_default':cap['default'],
            'original_command':cmd,'expected_inputs':record['inputs'],
            'expected_source_sha256':record['source_sha256'],
            'expected_runtime_kernel':record['runtime_kernel']})
assert len(items)==170 and len({i['case_id'] for i in items})==150
items.sort(key=lambda i:(i['family'],i['capture_id']))
out=Path(__file__).with_name('plan.json')
out.write_text(json.dumps({'cases':items},indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(f'planned {len(items)} captures from {len({i["case_id"] for i in items})} cases; sha256={hashlib.sha256(out.read_bytes()).hexdigest()}')
