"""Independently validate the copied pilot diagnostics against frozen plan."""
from collections import Counter
import json
from pathlib import Path

root=Path(__file__).resolve().parent
plan=json.loads((root/'plan.json').read_text())['cases']
by_id={x['capture_id']:x for x in plan}
dirs=sorted((root/'pilot-evidence/cases').iterdir())
assert len(dirs)==9
families=set()
for folder in dirs:
    item=by_id[folder.name];families.add(item['family'])
    record=json.loads((folder/'record.json').read_text())
    assert record['status']=='passed'
    assert record['inputs']==item['expected_inputs']
    assert record['source_sha256']==item['expected_source_sha256']
    assert record['runtime_kernel']==item['expected_runtime_kernel']
    samples=json.loads((folder/'watch-metadata.json').read_text())
    rows=[[int(x) for x in line.split()] for line in (folder/'watch.log').read_text().splitlines()]
    coverage=[]
    for line in (folder/'coverage.log').read_text().splitlines():
        call,index,base,size,snapshot,success=line.split()
        coverage.append((int(call),int(index),int(base,16),int(size),int(snapshot,16),int(success)))
    counts=Counter(row[0] for row in rows)
    assert len(counts)>=2 and all(c==len(samples) for c in counts.values())
    assert all(row[2]==1 and row[3]==row[4]==row[5]==row[6]==0 and row[9]==0 for row in rows)
    assert any(row[8]>0 for row in rows),'negative control did not show changed bytes'
    for row in rows:
        s=samples[row[1]]
        assert any(c[0]==row[0] and c[1]==row[1] and c[5]==1 and c[2]<=s['tensor_address'] and
            s['tensor_address']+s['span_bytes']<=c[2]+c[3] for c in coverage)
assert len(families)==9
print('PASS: nine families; source/input identity, restore coverage, sample checks, negative controls')
