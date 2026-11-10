"""Build an auditable target ledger; candidates are not assumed reusable."""
import csv, json, hashlib
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = ROOT / 'TileKernels-private/research/ascend-profiling'
INDEX = ROOT / 'outputs/expert-profile-inventory-20261109/captures.csv'
RECAP = ROOT / 'outputs/gcm-profile-screen-20261108/mte3-x1-x3/tbe-recapture/case-status.csv'
DEEP = ROOT / 'outputs/cube-rule02-deepgemm-20261107/audit.json'
FIELDS = 'UB_to_GM_datas(KB);UB_to_GM_bw_usage_rate(%);aiv_mte3_active_bw(GB/s);aiv_ub_read_bw_gm(GB/s);aiv_ub_to_gm_bw(GB/s)'

def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def rows(p):
    with p.open(encoding='utf-8-sig', newline='') as f: return list(csv.DictReader(f))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    allrows = rows(INDEX); recaps = {x['case']:x for x in rows(RECAP)}
    target_recap = {x['target_id']:x for x in allrows if x['batch']=='tbe-mhc' and x['mode']=='MemoryDetail+DEBUG'}
    new_path=HERE/'new-captures.json'
    new_captures=load(new_path) if new_path.exists() else {}
    hidev_path=HERE/'new-captures-hidev.json'
    hidev_captures=load(hidev_path) if hidev_path.exists() else {}
    precision_meta_path=HERE/'precision-capture-metadata-index.json'
    precision_meta={x['target']:x for x in load(precision_meta_path)['cases']} if precision_meta_path.exists() else {}
    assert not precision_meta or len(precision_meta)==13
    parser_sweep_path=HERE/'hidev-parser-health-sweep.json'
    parser_sweep=load(parser_sweep_path) if parser_sweep_path.exists() else {'flagged':[],'missing':[]}
    parser_flags={(x['target'],x['path']):x for x in parser_sweep['flagged']}
    assert len(parser_flags)==len(parser_sweep['flagged'])
    if parser_sweep_path.exists():
        parser_index_path=HERE/'hidev-capture-index.json'
        assert parser_sweep.get('source_index_sha256')==sha(parser_index_path), 'parser sweep must correspond to the imported index'
        parser_index=load(parser_index_path);assert parser_sweep['source_index_cases']==len(parser_index['cases'])
        for target,reason in parser_sweep['missing']:
            matching=[x for x in parser_index['cases'] if x['target']==target];assert matching
            for item in matching:
                path=item['raw_dir']+'/profile.log'
                parser_flags.setdefault((target,path),{'target':target,'path':path,'errors':['parser summary not checked: '+reason]})
    deep_new_path=HERE/'deepgemm-new-captures.json'
    deep_new=load(deep_new_path) if deep_new_path.exists() else {}
    head_path=HERE/'historical-head-no-ub-gm.json'
    head_no_ub_gm={x['target']:x for x in load(head_path)['cases']} if head_path.exists() else {}
    assert not head_no_ub_gm or len(head_no_ub_gm)==20
    head_bwd_path=HERE/'head-bwd-static-audit.json'
    head_bwd_no_ub_gm={x['target']:x for x in load(head_bwd_path)['cases']} if head_bwd_path.exists() else {}
    assert not head_bwd_no_ub_gm or len(head_bwd_no_ub_gm)==20
    sleep_path=HERE/'deepgemm-sleep-static-audit.json'
    sleep_no_ub_gm={x['target']:x for x in load(sleep_path)['cases']} if sleep_path.exists() else {}
    assert not sleep_no_ub_gm or len(sleep_no_ub_gm)==4
    paged_path=HERE/'deepgemm-paged-prepare-static-audit.json'
    paged_no_ub_gm={x['target']:x for x in load(paged_path)['cases']} if paged_path.exists() else {}
    assert not paged_no_ub_gm or len(paged_no_ub_gm)==8
    direct_path=HERE/'deepgemm-dequant-direct-static-audit.json'
    direct_no_ub_gm={x['target']:x for x in load(direct_path)['cases']} if direct_path.exists() else {}
    assert not direct_no_ub_gm or len(direct_no_ub_gm)==9
    pilot_direct_path=HERE/'deepgemm-pilot-direct-static-audit.json'
    pilot_direct_no_ub_gm={x['target']:x for x in load(pilot_direct_path)['cases']} if pilot_direct_path.exists() else {}
    assert not pilot_direct_no_ub_gm or len(pilot_direct_no_ub_gm)==3
    sparse_path=HERE/'deepgemm-sparse-meta-static-audit.json'
    sparse_no_ub_gm={x['target']:x for x in load(sparse_path)['cases']} if sparse_path.exists() else {}
    assert not sparse_no_ub_gm or len(sparse_no_ub_gm)==8
    mega_path=HERE/'mega28-dbi-index.json'
    mega_dbi={x['case']:x for x in load(mega_path)['cases']} if mega_path.exists() else {}
    assert len(target_recap)==len(recaps)==23 and set(target_recap)==set(recaps)
    deep = load(DEEP); deep_by_key={(x['campaign']+'/'+x['id']):x for x in deep['cases']}
    experimental_by_key={(x['campaign']+'/'+x['id']):x for x in deep['experimental']}
    earlier_path=ROOT/'outputs/tilekernels-profile-inventory-reset-20261105/inventory.json'
    earlier_document=load(earlier_path)
    earlier=earlier_document['cases']
    earlier_tables={str(Path(v['files']['OpBasicInfo']['path']).parent).replace('\\','/'):v['files'] for v in earlier_document['profiles']}
    assert len(deep_by_key)==154
    specs={}
    for p in BASE.glob('collector/**/*cases.json'):
        try:
            for x in load(p).get('cases',[]): specs.setdefault(x['id'],[]).append((p,x))
        except (ValueError, AttributeError): pass
    groups=defaultdict(list)
    for x in allrows:
        if x['batch'] in ('tilekernels-default','tilekernels-precision','deepgemm-original','deepgemm-experimental','tilekernels-earlier'):
            # RoPE Q and K may share case and op name but are separate targets.
            identity = x['target_id'] if x['batch'] in ('tilekernels-default','tilekernels-precision') else x['op_name']
            if x['batch']=='tilekernels-earlier' and x['case'].startswith('rope-'):
                call_index=x['profile_path'].rstrip('/').split('/')[-1]
                assert call_index in ('0','1'), x['profile_path']
                identity += '/call-'+call_index
            groups[(x['batch'],x['case'],identity)].append(x)
    ledger=[]
    for (batch,case,_identity), entries in sorted(groups.items()):
        x=entries[0]; op=x['op_name']; target=x['target_id']; reused=''; status='pending'; note=''; spec=''; spec_path='';remote_detail='';secondary_detail='';scope=''
        if batch=='tilekernels-earlier' and case.startswith('rope-'):
            target += '/call-'+x['profile_path'].rstrip('/').split('/')[-1]
        if batch.startswith('tilekernels-') and batch!='tilekernels-earlier':
            if batch=='tilekernels-precision' and precision_meta:
                m=precision_meta[target]
                assert sha(ROOT/m['capture_record'])==m['capture_record_sha256']
                assert sha(ROOT/m['capture_result'])==m['capture_result_sha256']
                note+='; historical capture-record includes input/source hashes; original CPU reference failed; replay identity and accuracy label must be checked separately'
            lookup=target.split('/')[-1]
            candidates=specs.get(lookup,[])
            if len(candidates)==1: spec_path=str(candidates[0][0].relative_to(ROOT)); spec=json.dumps(candidates[0][1],ensure_ascii=False,sort_keys=True)
            elif candidates:
                unique={json.dumps(v,sort_keys=True) for _,v in candidates}
                if len(unique)==1: spec_path=';'.join(str(p.relative_to(ROOT)) for p,_ in candidates); spec=next(iter(unique))
                else: note='multiple case specifications require disambiguation'
            if target in target_recap:
                r=recaps[target]; assert r['same_input_and_source_as_history']=='True'
                reused=target_recap[target]['evidence']; status='existing_dbi_audited'
                scope='tbe detail window'
            if target in new_captures:
                new=new_captures[target];audit=load(ROOT/new['audit'])
                assert audit['correctness']=='passed' and audit['historical_input_and_source_match']
                assert audit.get('runtime_kernel',op)==op and audit['device'] in (new['device'],new['device'].split()[-1])
                assert audit.get('case',target.split('/')[-1]) in (target.split('/')[-1],case)
                reused=new['audit'];remote_detail=new['remote_detail'];status='new_dbi_audited'
                scope='tbe detail window'
            if target in hidev_captures:
                new=hidev_captures[target];audit=load(ROOT/new['audit'])
                assert audit['status']=='passed' and audit['correctness']=='passed' and audit['historical_input_and_source_match']
                assert audit.get('runtime_kernel',op)==op and new['health']=='Alarm 8C4BA00C'
                assert audit.get('target',target)==target and audit.get('case',target.split('/')[-1])==target.split('/')[-1]
                if status=='pending':
                    reused=new['audit'];remote_detail=new['remote_detail'];status='new_dbi_audited_alarm'
                    scope='hidev detail window, device Alarm 8C4BA00C'
                else:secondary_detail=new['remote_detail']
                if audit.get('simt_tail_tokens',0):
                    note+=f"; {audit['simt_tail_tokens']} tail tokens use SIMT direct GM stores, excluded from UB-to-GM request bytes"
                if 'masked_tokens' in audit:
                    note+=f"; {audit['masked_tokens']} masked tokens; statistics only written for unmasked tokens"
                if audit.get('replay_mode')=='application':
                    if status=='new_dbi_audited_alarm':scope='hidev application-replay detail window, device Alarm 8C4BA00C'
                    note+='; application-replay byte window is separate from historical kernel-replay Default'
                if new.get('reaudit_status'):
                    reaudit=new['reaudit_status'];assert reaudit['status']=='passed'
                    note+=f"; previous {reaudit['previous_status']}, re-audit passed: {reaudit['reason']}"
            if target in head_no_ub_gm:
                evidence=head_no_ub_gm[target]
                assert status=='pending' and evidence['status']=='aiv_ub_to_gm_not_applicable' and evidence['correctness']=='passed'
                assert op=='mhc_head_compute_mix_fwd_asc_kernel'
                reused=str(head_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='historical captured binary and source; SIMT directly writes GM'
                note='no UB-to-GM movement instruction in captured binary; does not mean no GM writes'
            if target in head_bwd_no_ub_gm:
                evidence=head_bwd_no_ub_gm[target]
                assert status=='pending' and evidence['status']=='aiv_ub_to_gm_not_applicable' and evidence['correctness']=='passed'
                assert op=='mhc_head_compute_mix_bwd_asc_kernel' and len(entries)==1
                assert sha(ROOT/entries[0]['profile_path']/'dump/aicore_binary.o')==evidence['binary_sha256']
                reused=str(head_bwd_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='exact historical binary and source; SIMT directly writes GM'
                note='no UB-to-GM movement instruction; direct SIMT GM stores exist'
        elif batch=='tilekernels-earlier':
            spec=json.dumps(earlier[case]['definition'],ensure_ascii=False,sort_keys=True)
            spec_path=str(earlier_path.relative_to(ROOT))
            if case=='swiglu-supp-05':
                reused='outputs/gcm-profile-screen-20261108/mte3-x1-x3/byte-smoke/tbe/dbi-address-audit.json';status='existing_dbi_audited'
                scope='tbe detail window'
            else: note='earlier task contract and main-archive overlap require verification'
            early_castback_sizes={'castback-n1-h128-bf16':256,'castback-n512-h2048-bf16':2097152,'castback-n512-h2048-fp32':4194304,'castback-n8001-h2048-fp32':65544192}
            if case in early_castback_sizes:
                single=case=='castback-n1-h128-bf16'
                audit_path=HERE/('early-castback-single-audit-result-20261110.json' if single else 'early-'+case+'-audit-result-20261110.json')
                if audit_path.exists():
                    audit=load(audit_path)
                    assert target==case and audit['target']=='early/'+case and audit['status']=='passed'
                    assert audit['correctness']=='passed' and audit['historical_input_and_source_match'] is True
                    assert audit['dbi_requested_bytes']==audit['output_logical_bytes']==early_castback_sizes[case] and audit['replay_mode']=='application'
                    group='early-castback-single-runs-20261110' if single else 'early-castback-batch-runs-20261110'
                    reused=str(audit_path.relative_to(ROOT));remote_detail='/workspace/expert-profile-backfill-20261109-hidev/'+group+'/'+case+'/hidev-npu0/attempt-001/detail'
                    status='new_dbi_audited_alarm';scope='new hidev application-replay detail window; historical kernel replay and physical board separate; device Alarm 8C4BA00C'
                    note='single historical call; matched input hashes and generated source; separate replay windows'
            if case.startswith('swiglu-'):
                audit_path=HERE/('early-'+case+'-audit-result-20261110.json')
                if audit_path.exists():
                    audit=load(audit_path);definition=earlier[case]['definition'];dtype,=definition['output_dtypes'];shape,=definition['output_shapes'];size={'float32':4,'bfloat16':2}[dtype]*__import__('math').prod(shape)
                    assert target==case and audit['target']=='early/'+case and audit['status']=='passed'
                    assert audit['correctness']=='passed' and audit['historical_input_and_source_match'] is True
                    assert audit['dbi_requested_bytes']==audit['output_logical_bytes']==size and audit['replay_mode']=='application'
                    group='early-swiglu-single-runs-20261110' if case=='swiglu-supp-01' else 'early-swiglu-batch-runs-20261110'
                    reused=str(audit_path.relative_to(ROOT));remote_detail='/workspace/expert-profile-backfill-20261109-hidev/'+group+'/'+case+'/hidev-npu0/attempt-001/detail'
                    status='new_dbi_audited_alarm';scope='new hidev application-replay detail window; historical replay and physical board separate; device Alarm 8C4BA00C'
                    note='single historical call; matched input hashes and generated source; separate replay windows'
            if case.startswith('rmsnorm-'):
                audit_path=HERE/('early-'+case+'-audit-result-20261110.json')
                if audit_path.exists():
                    audit=load(audit_path);definition=earlier[case]['definition'];dtype,=definition['output_dtypes'];shape,=definition['output_shapes'];size={'float32':4,'bfloat16':2}[dtype]*__import__('math').prod(shape)
                    assert target==case and audit['target']=='early/'+case and audit['status']=='passed'
                    assert audit['correctness']=='passed' and audit['historical_input_and_source_match'] is True
                    assert audit['dbi_requested_bytes']==audit['output_logical_bytes']==size and audit['replay_mode']=='application'
                    group='early-rmsnorm-single-runs-20261110' if case=='rmsnorm-supp-01' else 'early-rmsnorm-batch-runs-20261110'
                    reused=str(audit_path.relative_to(ROOT));remote_detail='/workspace/expert-profile-backfill-20261109-hidev/'+group+'/'+case+'/hidev-npu0/attempt-001/detail'
                    status='new_dbi_audited_alarm';scope='new hidev application-replay detail window; historical replay and physical board separate; device Alarm 8C4BA00C'
                    note='single historical call; matched input hashes and generated source; separate replay windows'
            if case=='sinkhorn-cann-1':
                audit_path=HERE/'early-sinkhorn-cann-1-audit-result-20261110.json'
                if audit_path.exists():
                    audit=load(audit_path);definition=earlier[case]['definition'];dtype,=definition['output_dtypes'];shape,=definition['output_shapes'];size={'float32':4}[dtype]*__import__('math').prod(shape)
                    assert target==case and audit['target']=='early/'+case and audit['status']=='passed'
                    assert audit['correctness']=='passed' and audit['historical_input_and_source_match'] is True
                    assert audit['dbi_requested_bytes']==audit['output_logical_bytes']==size and audit['replay_mode']=='application'
                    group='early-sinkhorn-single-runs-20261110'
                    reused=str(audit_path.relative_to(ROOT));remote_detail='/workspace/expert-profile-backfill-20261109-hidev/'+group+'/'+case+'/hidev-npu0/attempt-002/detail'
                    status='new_dbi_audited_alarm';scope='new hidev application-replay detail window; historical replay and physical board separate; device Alarm 8C4BA00C'
                    note='new warmup5 single-call capture; old warmup0 profile only reference; matched input hashes and generated source; separate replay windows'
            if case.startswith('rope-'):
                note+='; original range capture call index only; Q/K mapping not inferred'
        elif batch=='deepgemm-original':
            v=deep_by_key[case]; spec=json.dumps(v['case'],ensure_ascii=False,sort_keys=True);spec_path='outputs/cube-rule02-deepgemm-20261107/audit.json'
            if x['op_type']=='cube': status='aiv_not_applicable'
            elif case in sleep_no_ub_gm:
                evidence=sleep_no_ub_gm[case]
                assert x['op_type']=='mix' and op=='sleep_impl' and len(entries)==1
                binary=ROOT/entries[0]['profile_path']/'dump/aicore_binary.o'
                assert sha(binary)==evidence['binary_sha256'] and evidence['status']=='aiv_ub_to_gm_not_applicable'
                reused=str(sleep_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='exact historical binary and pinned source; no AIV UB-to-GM instruction'
                note='sleep auxiliary kernel; original profile preserved; does not imply all memory activity is absent'
            elif case in paged_no_ub_gm:
                evidence=paged_no_ub_gm[case]
                assert x['op_type']=='vector' and 'paged_sparse_mqa_prepare_impl' in op and len(entries)==1
                binary=ROOT/entries[0]['profile_path']/'dump/aicore_binary.o'
                assert sha(binary)==evidence['binary_sha256'] and evidence['status']=='aiv_ub_to_gm_not_applicable' and evidence['correctness']=='passed'
                reused=str(paged_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='exact historical binary and pinned source; no AIV UB-to-GM instruction; SIMT GM stores exist'
                note='direct SIMT writes are outside this field and must not be interpreted as zero GM writes'
            elif case in direct_no_ub_gm:
                evidence=direct_no_ub_gm[case]
                assert x['op_type']=='mix' and 'fp8_dequant_gemm_impl' in op and len(entries)==1
                binary=ROOT/entries[0]['profile_path']/'dump/aicore_binary.o'
                assert sha(binary)==evidence['binary_sha256'] and evidence['status']=='aiv_ub_to_gm_not_applicable' and evidence['correctness']=='passed'
                reused=str(direct_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='exact historical binary and direct-store specialization; AIV UB-to-L1 and Cube L0C-to-GM'
                note='no AIV UB-to-GM transfer; Cube output writes and AIV UB-to-L1 transfers are present'
            elif case in pilot_direct_no_ub_gm:
                evidence=pilot_direct_no_ub_gm[case]
                assert x['op_type']=='mix' and 'fp8_dequant_gemm_impl' in op and len(entries)==1
                binary=ROOT/entries[0]['profile_path']/'dump/aicore_binary.o'
                assert sha(binary)==evidence['binary_sha256'] and evidence['status']=='aiv_ub_to_gm_not_applicable' and evidence['correctness']=='passed'
                reused=str(pilot_direct_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='exact historical binary and direct-store specialization; AIV UB-to-L1 and Cube L0C-to-GM'
                note='no AIV UB-to-GM transfer; Cube output writes and AIV UB-to-L1 transfers are present'
            elif case in sparse_no_ub_gm:
                evidence=sparse_no_ub_gm[case]
                assert x['op_type']=='vector' and 'sparse_mqa_logits_metadata26sparse_mqa_logits_metadata' in op and len(entries)==1
                binary=ROOT/entries[0]['profile_path']/'dump/aicore_binary.o'
                assert sha(binary)==evidence['binary_sha256'] and evidence['status']=='aiv_ub_to_gm_not_applicable' and evidence['correctness']=='passed'
                reused=str(sparse_path.relative_to(ROOT));status='aiv_ub_to_gm_not_applicable'
                scope='exact historical binary and pinned source; no AIV UB-to-GM instruction; SIMT and scalar GM access exist'
                note='resolved indirect calls and checked the complete saved binary; direct GM stores are outside this field'
            elif case in deep_new:
                new=deep_new[case];audit=load(ROOT/new['audit'])
                assert audit['status']=='passed' and audit['case']==case and audit['correctness']=='passed'
                assert (audit.get('historical_target_input_and_jit_source_match') is True or
                        audit.get('historical_true_inputs_and_jit_source_match') is True)
                assert new['health']=='Alarm 8C4BA00C'
                reused=new['audit'];remote_detail=new['remote_detail'];status='new_dbi_audited_alarm'
                scope='hidev detail window, device Alarm 8C4BA00C'
                if audit.get('replay_mode')=='application':
                    scope='hidev application-replay detail window; separate from historical replay; device Alarm 8C4BA00C'
        elif batch=='deepgemm-experimental':
            v=experimental_by_key[case]; spec=json.dumps(v['case'],ensure_ascii=False,sort_keys=True)
            spec_path='outputs/cube-rule02-deepgemm-20261107/audit.json'
            note='28-core adapted experiment; not original expert implementation'
            name=case.split('/')[-1]
            if name in mega_dbi:
                rec=mega_dbi[name];audit=rec['audit']
                assert audit['status']=='dbi_window_correct_output_covered_scratch_completeness_unverified' and audit['correctness']=='passed'
                assert audit['historical_input_and_output_hashes_match'] and rec['health']=='Alarm 8C4BA00C'
                reused=str(mega_path.relative_to(ROOT));remote_detail=rec['raw_dir']+'/detail';status='dbi_window_scratch_unverified'
                scope='28-core port; application replay DBI stage only; scratch coverage unverified'
                scratch=rec.get('scratch_coverage')
                if scratch:
                    assert scratch['case']==name and scratch['dbi_pid']==audit['dbi_pid']
                    assert scratch['status']=='expected_workspace_and_output_bytes_covered_once'
                    status='dbi_window_coverage_verified_traffic_unverified'
                    scope='28-core port; DBI stage expected workspace and output addresses covered; duplicate-write traffic completeness unverified'
                if audit['other_replay_failures']:note+='; other PMU replays failed and must not be combined'
        flag=parser_flags.get((target,remote_detail+'/profile.log'))
        if flag and remote_detail and flag['path']==remote_detail+'/profile.log' and status=='new_dbi_audited_alarm':
            status='pending';scope='';note+='; parser health sweep: '+', '.join(flag['errors'])+'; original audit retained, capture not admitted'
        op_paths=[]; memory_paths=[]
        for entry in entries:
            folder=entry['profile_path']
            if batch=='tilekernels-earlier':
                files=earlier_tables[folder]
                op_paths.append(files['OpBasicInfo']['path']);memory_paths.append(files['Memory']['path'])
            else:
                op_paths.append(folder+'/OpBasicInfo.csv');memory_paths.append(folder+'/Memory.csv')
        ledger.append(dict(batch=batch,case=case,target_id=target,op_name=op,op_type=x['op_type'],
            input_spec=spec,input_spec_source=spec_path,original_profile_paths=';'.join(y['profile_path'] for y in entries),
            original_opbasic_csv=';'.join(op_paths),original_memory_csv=';'.join(memory_paths),
            original_evidence=';'.join(sorted({y['evidence'] for y in entries})),original_default='present',
            missing_fields='' if status in ('aiv_not_applicable','aiv_ub_to_gm_not_applicable') else FIELDS,
            per_core_requested_bytes_status=status,existing_log_evidence=reused,
            byte_data_scope=scope,remote_detail_path=remote_detail,secondary_detail_path=secondary_detail,notes=note))
    mega=['mega-h256-i512-e4-top2-t16','mega-h256-i512-e4-top2-t64','mega-h512-i1024-e8-top4-t64','mega-h512-i512-e8-top2-t32']
    case_manifest={}
    for p in (BASE/'deepgemm-ascend/campaign-13').glob('cases*.json'):
        for v in load(p).get('cases',[]):
            if v['id'] in mega: case_manifest.setdefault(v['id'],(p,v))
    assert set(case_manifest)==set(mega)
    for case in mega:
        p,v=case_manifest[case]
        ledger.append(dict(batch='deepgemm-original-missing',case='campaign-13/'+case,target_id='campaign-13/'+case,
            op_name='mega_moe_impl',op_type='mix',input_spec=json.dumps(v,sort_keys=True),input_spec_source=str(p.relative_to(ROOT)),
            original_profile_paths='',original_opbasic_csv='',original_memory_csv='',original_evidence='original requires 32 Cube cores; see campaign-13/STATUS.md',
            original_default='missing',missing_fields='entire Default;'+FIELDS,per_core_requested_bytes_status='blocked_32_cube_required',
            existing_log_evidence='',byte_data_scope='',remote_detail_path='',secondary_detail_path='',notes='28-core adapted experiment remains separate'))
    early_rope=[x for x in ledger if x['batch']=='tilekernels-earlier' and x['case'].startswith('rope-')]
    assert len(early_rope)==40 and len({x['case'] for x in early_rope})==20
    assert all({x['target_id'].rsplit('/',1)[-1] for x in early_rope if x['case']==case}=={'call-0','call-1'} for case in {x['case'] for x in early_rope})
    out=HERE/'targets.csv'
    with out.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
    counts=Counter((x['batch'],x['per_core_requested_bytes_status']) for x in ledger)
    summary={'rows':len(ledger),'counts':{' | '.join(k):v for k,v in sorted(counts.items())},
             'inputs':{str(p.relative_to(ROOT)):sha(p) for p in (INDEX,RECAP,DEEP,earlier_path,new_path,hidev_path,precision_meta_path,parser_sweep_path,HERE/'early-castback-single-audit-result-20261110.json',*sorted(HERE.glob('early-swiglu-*-audit-result-20261110.json')),*sorted(HERE.glob('early-rmsnorm-*-audit-result-20261110.json')),*sorted(HERE.glob('early-sinkhorn-*-audit-result-20261110.json')),*(HERE/('early-'+c+'-audit-result-20261110.json') for c in ('castback-n512-h2048-bf16','castback-n512-h2048-fp32','castback-n8001-h2048-fp32')),deep_new_path,head_path,head_bwd_path,sleep_path,paged_path,direct_path,pilot_direct_path,sparse_path,mega_path) if p.exists()},
             'unresolved_contract_duplicates':'early records require exact input and target comparison; retained separately',
             'raw_bytes_scope':'requested UB to GM bytes, not physical DRAM writes',
             'bandwidth_fields':'not reconstructed without verified tool formula and same-window denominator'}
    (HERE/'inventory-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
