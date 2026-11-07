"""Independently check transferred, per-capture replay evidence."""
from collections import Counter
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
repo=root.parents[3]
ev=root/'replay-evidence'
plan=json.loads((root.parent/'20261107-replay-debug/plan.json').read_text())['cases']
manifest=json.loads((ev/'manifest.json').read_text())
for name,item in manifest.items():
    raw=(ev/name).read_bytes()
    assert len(raw)==item['bytes'] and hashlib.sha256(raw).hexdigest()==item['sha256'],name
assert len(manifest)==851
progress=json.loads((ev/'progress.json').read_text());assert progress['status']=='finished'
assert len(plan)==170 and len({x['case_id'] for x in plan})==150
byid={x['capture_id']:x for x in plan};assert len(byid)==170
folders={p.name:p for p in (ev/'cases').iterdir() if p.is_dir()};assert set(folders)==set(byid)
not_changed=[];calls=0
for cid,item in byid.items():
    d=folders[cid]
    result=json.loads((d/'result.json').read_text())
    record=json.loads((d/'record.json').read_text())
    assert result['capture_id']==cid and result['status']=='sampled_restore_pass' and result['returncode']==0
    assert record['status']=='passed' and record['inputs']==item['expected_inputs']
    assert record['source_sha256']==item['expected_source_sha256'] and record['runtime_kernel']==item['expected_runtime_kernel']
    original=json.loads((repo/item['original_default']).read_text())
    assert original['inputs']==record['inputs'] and original['source_sha256']==record['source_sha256']
    samples=json.loads((d/'watch-metadata.json').read_text())
    assert [s['index'] for s in samples]==list(range(len(samples)))
    rows=[[int(x) for x in line.split()] for line in (d/'watch.log').read_text().splitlines()]
    coverage=[]
    for line in (d/'coverage.log').read_text().splitlines():
        call,index,base,size,snapshot,success=line.split()
        coverage.append((int(call),int(index),int(base,16),int(size),int(snapshot,16),int(success)))
    counts=Counter(row[0] for row in rows);assert len(counts)>=2
    assert all(c==len(samples) for c in counts.values())
    assert all(len(row)==10 and row[2]==1 and row[3]==row[4]==row[5]==row[6]==0 and row[9]==0 for row in rows)
    for row in rows:
        s=samples[row[1]]
        assert 0<s['sample_bytes']<=4096 and s['sample_offset']+s['sample_bytes']<=s['span_bytes']
        assert any(c[0]==row[0] and c[1]==row[1] and c[5]==1 and c[2]<=s['tensor_address'] and
                   s['tensor_address']+s['span_bytes']<=c[2]+c[3] for c in coverage)
    calls+=len(counts)
    changed=any(row[8]>0 for row in rows)
    assert changed==result['observed_changed_before_restore']
    if not changed:not_changed.append(cid)
assert sorted(not_changed)==['moe_topk_gate_forward-04','moe_topk_gate_forward-09']
control=root/'full-control-evidence'
cm=json.loads((control/'manifest.json').read_text());assert len(cm)==17
for name,item in cm.items():
    b=(control/name).read_bytes()
    assert len(b)==item['bytes'] and hashlib.sha256(b).hexdigest()==item['sha256'],name
summary=json.loads((control/'full-control-summary.json').read_text());assert summary['status']=='completed'
assert {x['capture_id'] for x in summary['results']}==set(not_changed)
for cid in not_changed:
    d=control/'cases'/cid
    result=json.loads((d/'full-control-result.json').read_text())
    rec=json.loads((d/'record.json').read_text())
    s=json.loads((d/'watch-metadata.json').read_text())
    rows=[[int(x) for x in line.split()] for line in (d/'watch.log').read_text().splitlines()]
    assert result['status']=='sampled_restore_pass' and result['full_buffer_unchanged']
    assert rec['inputs']==byid[cid]['expected_inputs'] and rec['source_sha256']==byid[cid]['expected_source_sha256']
    assert len(s)==1 and s[0]['sample_offset']==0 and s[0]['sample_bytes']==s[0]['span_bytes']==result['bytes_checked']
    assert len(rows)>=2 and all(len(r)==10 and r[2]==1 and r[3]==r[4]==r[5]==r[6]==0 and r[8]==r[9]==0 for r in rows)
assert json.loads((folders['moe_topk_gate_forward-02']/'result.json').read_text())['observed_changed_before_restore']
old=json.loads((root.parent/'20261107-review/case-review.json').read_text())['cases']
assessment=json.loads((root/'replay-assessment.json').read_text())
new={x['case_id']:x for x in assessment['cases']}
assert len(new)==len(old)==220 and set(new)=={x['case_id'] for x in old}
assert assessment['counts']=={'cases':220,'restoration_supported':150,'not_applicable':70}
for entry in old:
    a=new[entry['case_id']]
    assert a['family']==entry['family'] and a['params']==entry['params']
    assert {x['capture_id'] for x in a['captures']}=={x['capture_id'] for x in entry['captures']}
    if entry['review_disposition']=='retain_inplace_restoration_review':
        assert a['replay_review']=='instrumented_retest_supports_restore'
        for c in a['captures']:
            assert c['capture_id'] in byid
            assert c['result']==('full_buffer_unchanged' if c['capture_id'] in not_changed else 'sampled_values_restored')
    else:
        assert a['replay_review']=='inplace_restore_not_applicable'
        assert all(c['result']=='original_inplace_restore_concern_not_applicable' for c in a['captures'])
print(f'REPLAY ACCEPTANCE PASS: 150 cases, 170 captures, {calls} restore calls, 168 with observed change, 2 full-buffer unchanged')
