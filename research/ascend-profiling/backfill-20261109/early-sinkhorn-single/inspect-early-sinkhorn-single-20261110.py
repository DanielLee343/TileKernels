"""Validate single-call early Sinkhorn replay against historical identity."""
import csv,hashlib,json,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');attempt,=sys.argv[1:];assert re.fullmatch(r'attempt-\d+',attempt)
p=root/'early-sinkhorn-single-runs-20261110/sinkhorn-cann-1/hidev-npu0'/attempt/'detail';h=p/'provenance/harness/historical';old=json.loads((h/'default.json').read_text());prep=json.loads((h/'prepare.json').read_text());assert old['status']=='passed' and prep['status']=='passed' and prep['correctness']['status']=='passed'
command=json.loads((p/'command.json').read_text());assert '--replay-mode=application' in command and '--mstx-include=cold_call' in command and '--warm-up=5' in command
apps=sorted(p.glob('process-*/application.json'));assert len(apps)>=2
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();records=[];addresses=None
for f in apps:
 pid=f.parent.name.removeprefix('process-');assert pid.isdigit();a=json.loads(f.read_text());assert a['status']=='passed' and a['case']==old['case'] and a['input_sha256']==old['input_sha256']
 assert a['post_replay_output_check']['status']=='passed' and a['native_roles']==['single'] and len(a['native'])==1
 x,=a['native'];y=old['native'];assert x['role']=='single' and [x['global_symbol']]==y['global_symbols'] and x['kwargs']==y['kwargs']
 actual=f.parent/'launch-single-kernel.cpp';historical=h/'launch-kernel.cpp';assert sha(actual)==x['source_sha256'] and sha(historical)==y['source_sha256']
 old_text=historical.read_text().replace(r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/',r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/');assert actual.read_text()==old_text,'generated source differs beyond checkout path'
 assert a['target_calls'][0]['actual_profile_ranges']==['cold_call'];device=a['device_args'];assert set(device)=={'single'} and device['single'][0] and device['single'][1]
 if addresses is None:addresses=device
 else:assert device==addresses,'application process device arguments differ'
 records.append({'pid':pid,'application':str(f.relative_to(p)),'application_sha256':sha(f),'source':str(actual.relative_to(p)),'source_sha256':sha(actual)})
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=csv.DictReader(f)
assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==('mhc_sinkhorn_fwd_asc_kernel','vector','56','0')
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary);assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
log=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',log);assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
result={'target':'early/sinkhorn-cann-1','status':'capture_identified_address_audit_pending','correctness':'passed_new_post_replay_reference','historical_input_and_source_match':True,'capture_binary_sha256':bsha,'parser_metrics':metrics,'representative_pid':records[0]['pid'],'application_records':records,'scope':'one single-call application replay with historical input and generated source; old replay window and board separate'}
(p/'capture-inspection.json').write_text(json.dumps(result,indent=2)+'\n');print('EARLY_SINKHORN_IDENTITY_VALIDATED',len(records),'BYTE_AUDIT_PENDING')
