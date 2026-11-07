"""Generate a small case index; never overwrite original records."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
cap=root/'capture-evidence';accuracy=root/'accuracy-evidence'
previous=root.parent/'20261107-replay-debug/evidence'
plan=json.loads((root/'accuracy-plan.json').read_text())['cases']
normal={x['id']:x for x in json.loads((previous/'normalize-comparison.json').read_text())}
post=json.loads((previous/'post-comparison.json').read_text())
items=[]
for item in plan:
    cid=item['id'];result=json.loads((cap/'cases'/cid/'capture-result.json').read_text())
    if item['family']=='moe_normalize_weight':
        comp=normal[cid]['results']
        npu=[{'output':x['output'],'mismatch':x['num_over_2e-6_vs_npu'],'max_abs':x['max_abs_vs_npu']} for x in comp]
        scope='same-input NPU PyTorch reference; atol 2e-6, rtol 0'
    elif item['family']=='mhc_pre_apply_mix_bwd':
        comp=json.loads((accuracy/'cases'/cid/'reference-comparison.json').read_text())
        npu=comp['npu']
        scope='same-input NPU FP32 autograd in token chunks; nonzero initial gradient; atol 1e-2, rtol 1e-3'
    else:
        npu=post['npu']
        scope='same-input NPU autograd in token chunks; output-specific upstream tolerances'
    mismatches=sum(x['mismatch'] for x in npu)
    items.append({'case_id':cid,'family':item['family'],'params':item.get('params',item.get('case')),
       'profile_status':'captured_default','original_cpu_reference':result['original_cpu_reference'],
       'npu_reference_status':'mismatch' if mismatches else 'passed_chunked_comparison',
       'npu_reference_scope':scope,'npu_outputs':npu,'source_and_input_match':True,
       'profile_evidence':str(Path('capture-evidence')/'cases'/cid/'capture-result.json')})
out={'cases':items,'counts':{'profiles':len(items),'npu_reference_mismatch':sum(x['npu_reference_status']=='mismatch' for x in items),
    'npu_reference_chunked_pass':sum(x['npu_reference_status']=='passed_chunked_comparison' for x in items)},
    'limitation':'mHC pre-apply uses nonzero initial gradient; upstream test uses zero. Post uses chunked NPU reference instead of full-shape upstream reference. Do not infer global correctness.'}
(root/'summary.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('SUMMARY GENERATED',json.dumps(out['counts'],sort_keys=True))
