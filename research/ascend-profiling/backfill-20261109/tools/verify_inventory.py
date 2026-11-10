"""Independently reconcile target ledger to original capture index."""
import csv,json,hashlib
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
def rows(p):
    with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def check_parser_health(ledger,sweep,index):
    flagged={(x['target'],x['path']) for x in sweep['flagged']}
    for target,_reason in sweep['missing']:
        matching=[x for x in index['cases'] if x['target']==target]
        assert matching
        flagged.update((target,x['raw_dir']+'/profile.log') for x in matching)
    for row in ledger:
        if (row['target_id'],row['remote_detail_path']+'/profile.log') in flagged:
            assert row['per_core_requested_bytes_status']=='pending',(row['target_id'],row['remote_detail_path'])

def main():
    index=rows(ROOT/'outputs/expert-profile-inventory-20261109/captures.csv')
    ledger=rows(HERE/'targets.csv')
    original_batches={'tilekernels-default','tilekernels-precision','tilekernels-earlier','deepgemm-original','deepgemm-experimental'}
    actual=Counter((r['batch'],r['case'],r['profile_path']) for r in index if r['batch'] in original_batches)
    observed=Counter((r['batch'],r['case'],p) for r in ledger if r['batch'] in original_batches for p in r['original_profile_paths'].split(';'))
    assert actual==observed, (actual-observed,observed-actual)
    assert len(ledger)==1301
    assert len([r for r in ledger if r['batch'] in ('tilekernels-default','tilekernels-precision')])==1020
    assert len([r for r in ledger if r['batch']=='deepgemm-original'])==154
    early=[r for r in ledger if r['batch']=='tilekernels-earlier' and r['case'].startswith('rope-')]
    assert len(early)==40 and len({r['case'] for r in early})==20
    for case in {r['case'] for r in early}:
        subset=[r for r in early if r['case']==case]
        assert {r['target_id'].split('/')[-1] for r in subset}=={'call-0','call-1'}
        assert all(r['original_profile_paths'].split('/')[-1]==r['target_id'][-1] for r in subset)
    missing=[];wrong=[]
    for r in ledger:
        if r['original_default']=='missing':continue
        for p in r['original_opbasic_csv'].split(';'):
            path=ROOT/p
            if not path.is_file():missing.append(p);continue
            with path.open(encoding='utf-8-sig',newline='') as f: basic=list(csv.DictReader(f))
            if len(basic)!=1 or basic[0]['Op Name']!=r['op_name']:wrong.append(p)
        for p in r['original_memory_csv'].split(';'):
            if not (ROOT/p).is_file():missing.append(p)
    assert not missing and not wrong, {'missing':missing[:5],'wrong':wrong[:5]}
    sweep=json.loads((HERE/'hidev-parser-health-sweep.json').read_text(encoding='utf-8'))
    source=HERE/'hidev-capture-index.json';assert sweep['source_index_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
    check_parser_health(ledger,sweep,json.loads(source.read_text(encoding='utf-8')))
    result={'ledger_rows':len(ledger),'capture_index_rows_reconciled':sum(actual.values()),
            'early_rope_cases':20,'early_rope_targets':40,'all_original_op_and_memory_csv_exist_and_identity_matches':True,
            'ledger_sha256':hashlib.sha256((HERE/'targets.csv').read_bytes()).hexdigest()}
    (HERE/'inventory-verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS',json.dumps(result))
if __name__=='__main__':main()
