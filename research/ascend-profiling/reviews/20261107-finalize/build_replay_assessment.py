"""Generate a non-destructive, per-case replay review overlay for 220 cases."""
import json
from pathlib import Path

root=Path(__file__).resolve().parent
old=json.loads((root.parent/'20261107-review/case-review.json').read_text())['cases']
cases=[]
for entry in old:
    cid=entry['case_id'];caps=[]
    for cap in entry['captures']:
        capture_id=cap['capture_id']
        if entry['review_disposition']=='retain_inplace_restoration_review':
            d=root/'replay-evidence/cases'/capture_id
            result=json.loads((d/'result.json').read_text())
            assert result['status']=='sampled_restore_pass'
            control=capture_id in ('moe_topk_gate_forward-04','moe_topk_gate_forward-09')
            caps.append({'capture_id':capture_id,'original_default':cap['default'],
                'result':'full_buffer_unchanged' if control else 'sampled_values_restored',
                'restore_call_count':result['restore_call_count'],
                'evidence':f'replay-evidence/cases/{capture_id}/result.json',
                'full_buffer_control':f'full-control-evidence/cases/{capture_id}/full-control-result.json' if control else None})
        else:
            caps.append({'capture_id':capture_id,'original_default':cap['default'],
                         'result':'original_inplace_restore_concern_not_applicable'})
    cases.append({'case_id':cid,'family':entry['family'],'params':entry['params'],
        'replay_review':'instrumented_retest_supports_restore' if entry['review_disposition']=='retain_inplace_restoration_review' else 'inplace_restore_not_applicable',
        'captures':caps})
assert len(cases)==220 and sum(x['replay_review']=='instrumented_retest_supports_restore' for x in cases)==150
output={'counts':{'cases':220,'restoration_supported':150,'not_applicable':70},'cases':cases,
        'scope':'Independent instrumented rerun; content sampled except two full-buffer controls. Original status and raw performance profiles remain unchanged.'}
(root/'replay-assessment.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
print('REPLAY ASSESSMENT GENERATED: 220 cases, 150 supported, 70 not applicable')
