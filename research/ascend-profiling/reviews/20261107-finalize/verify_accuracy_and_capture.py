"""Independently verify all 13 captures and recorded reference comparisons."""
import csv
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parent
cap=root/'capture-evidence';accuracy=root/'accuracy-evidence'
previous=root.parent/'20261107-replay-debug/evidence'
plan=json.loads((root/'accuracy-plan.json').read_text())['cases']
assert len(plan)==13 and len({x['id'] for x in plan})==13
for folder,expected in ((cap,301),(accuracy,37)):
    manifest=json.loads((folder/'manifest.json').read_text())
    assert len(manifest)==expected,(folder,len(manifest))
    for name,meta in manifest.items():
        b=(folder/name).read_bytes()
        assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256'],name
assert json.loads((cap/'capture-progress.json').read_text())['status']=='finished'
assert json.loads((accuracy/'check-progress.json').read_text())['status']=='finished'
normal={x['id']:x for x in json.loads((previous/'normalize-comparison.json').read_text())}
post=json.loads((previous/'post-comparison.json').read_text())
post_record=json.loads((previous/'post-record.json').read_text())
expected_metrics={'OpBasicInfo','ArithmeticUtilization','L2Cache','Memory','MemoryL0','MemoryUB','PipeUtilization','ResourceConflictRatio'}
counts={'npu_reference_mismatch':0,'npu_reference_pass':0}
summary=json.loads((root/'summary.json').read_text())
summary_cases={x['case_id']:x for x in summary['cases']}
assert set(summary_cases)=={x['id'] for x in plan}
for item in plan:
    cid=item['id'];folder=cap/'cases'/cid
    result=json.loads((folder/'capture-result.json').read_text())
    record=json.loads((folder/'capture-record.json').read_text())
    assert result['id']==cid and result['status']=='completed' and result['returncode']==0
    assert result['same_source'] and result['same_inputs'] and result['same_kernel']
    assert record['source_sha256']==item['expected_source_sha256'] and record['inputs']==item['expected_inputs']
    assert record['runtime_kernel']==item['runtime_kernel']
    assert result['original_cpu_reference']==record['reference_check']=='failed'
    assert set(result['metrics'])==expected_metrics
    for name,meta in result['metrics'].items():
        file=cap/meta['path'];b=file.read_bytes()
        assert len(b)==meta['bytes'] and hashlib.sha256(b).hexdigest()==meta['sha256']
        with file.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        assert len(rows)==meta['rows']
        if name=='OpBasicInfo':
            assert len(rows)==1 and rows[0]['Op Name']==item['runtime_kernel'] and rows[0]['Block Dim']=='56'
        else:
            assert len(rows)==56 and {int(x['block_id']) for x in rows}==set(range(56))
            assert {x['sub_block_id'] for x in rows}=={'vector0'}
    if item['family']=='moe_normalize_weight':
        n=normal[cid];assert n['input_sha256']==item['expected_inputs'][0]['sha256']
        failures=sum(x['num_over_2e-6_vs_npu'] for x in n['results'])
        reference='same-input NPU PyTorch; original tolerance'
    elif item['family']=='mhc_pre_apply_mix_bwd':
        d=accuracy/'cases'/cid
        comparison=json.loads((d/'reference-comparison.json').read_text())
        state=json.loads((d/'accuracy-record.json').read_text())
        check=json.loads((d/'check-result.json').read_text())
        assert check['id']==cid and check['status']=='completed' and check['same_inputs'] and check['same_source']
        assert check['comparison']==comparison and state['inputs']==item['expected_inputs']
        assert state['source_sha256']==item['expected_source_sha256']
        failures=sum(x['mismatch'] for x in comparison['npu'])
        reference='same-input NPU FP32 autograd, nonzero initial gradient, token chunks; upstream tolerance'
    else:
        assert cid=='mhc_post_bwd-04' and post_record['inputs']==item['expected_inputs']
        assert post_record['source_sha256']==item['expected_source_sha256']
        failures=sum(x['mismatch'] for x in post['npu'])
        reference='same-input NPU autograd in token chunks; upstream tolerance'
    key='npu_reference_mismatch' if failures else 'npu_reference_pass';counts[key]+=1
    entry=summary_cases[cid]
    assert entry['profile_status']=='captured_default' and entry['original_cpu_reference']=='failed'
    assert sum(x['mismatch'] for x in entry['npu_outputs'])==failures
    assert entry['npu_reference_status']==('mismatch' if failures else 'passed_chunked_comparison')
    print(cid,'profile=complete','original_cpu=failed','npu_mismatches='+str(failures),reference)
print('REFERENCE RESULTS',counts)
assert summary['counts']=={'profiles':13,'npu_reference_mismatch':counts['npu_reference_mismatch'],
                           'npu_reference_chunked_pass':counts['npu_reference_pass']}
print('ACCURACY AND CAPTURE ACCEPTANCE PASS: 13 profiles, 9 pre-apply checks, 3 normalize checks, 1 post check')
