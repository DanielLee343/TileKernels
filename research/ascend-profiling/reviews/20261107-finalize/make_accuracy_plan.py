"""Freeze the original 13 case inputs, parameters and source identity."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[4]
base=root/'research/ascend-profiling'
starter=json.loads((base/'collector/starter/cases.json').read_text())['cases']
plans={x['id']:x for x in starter}
items=[]
for cid in ('normalize-03','normalize-16','normalize-20'):
    p=base/'runs/hidev-20261106-starter/cases'/cid/'prepare.json'
    a=json.loads(p.read_text())
    items.append({'id':cid,'family':'moe_normalize_weight','case':plans[cid],
                  'expected_source_sha256':a['source_sha256'],'expected_inputs':a['inputs'],
                  'runtime_kernel':a['runtime_kernel'],'range':'cold_call'})
for number in (2,4,6,9,10,11,12,14,18):
    cid=f'mhc_pre_apply_mix_bwd-{number:02d}'
    p=base/'runs/hidev-20261106-unified-extra4/cases'/cid/'prepare.json'
    a=json.loads(p.read_text())
    items.append({'id':cid,'family':'mhc_pre_apply_mix_bwd','params':a['params'],
                  'expected_source_sha256':a['source_sha256'],'expected_inputs':a['inputs'],
                  'runtime_kernel':a['runtime_kernel'],'range':a['target_range']})
cid='mhc_post_bwd-04'
p=base/'runs/hidev-20261106-unified-extra2/cases'/cid/'prepare.json'
a=json.loads(p.read_text())
items.append({'id':cid,'family':'mhc_post_bwd','params':a['params'],
              'expected_source_sha256':a['source_sha256'],'expected_inputs':a['inputs'],
              'runtime_kernel':a['runtime_kernel'],'range':a['target_range']})
assert len(items)==13 and len({x['id'] for x in items})==13
Path(__file__).with_name('accuracy-plan.json').write_text(json.dumps({'cases':items},indent=2,sort_keys=True)+'\n')
print('planned 13 original cases')
