"""Identity check for one historical RoPE Q replay; never promotes a byte audit."""
import csv,hashlib,json,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');attempt,=sys.argv[1:];assert re.fullmatch(r'attempt-\d+',attempt)
p=root/'early-rope-app-probe-runs/rope-supp-01-Q/hidev-npu0'/attempt/'detail';h=p/'provenance/harness/historical';old=json.loads((h/'default.json').read_text());prep=json.loads((h/'prepare.json').read_text());assert old['status']=='passed'
command=json.loads((p/'command.json').read_text());assert '--replay-mode=application' in command and '--mstx-include=early_Q' in command and '--warm-up=5' in command
apps=sorted(p.glob('process-*/application.json'));assert len(apps)>=2
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();records=[];addresses=None
for f in apps:
 pid=f.parent.name.removeprefix('process-');assert pid.isdigit();a=json.loads(f.read_text());assert a['status']=='passed' and a['case']==old['case'] and a['input_sha256']==old['input_sha256']
 assert a['post_replay_output_check']['status']=='passed' and a['native_roles']==['Q','K'] and len(a['native'])==len(old['native'])==2
 for x,y in zip(a['native'],old['native']):
  assert x['role']==y['role'] and x['global_symbol']==y['global_symbol'] and x['kwargs']==y['kwargs']
  actual=f.parent/('launch-'+x['role']+'-kernel.cpp');historical=h/('launch-'+x['role']+'-kernel.cpp');assert sha(actual)==x['source_sha256'] and sha(historical)==y['source_sha256']
  old_text=historical.read_text().replace(r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/',r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/')
  assert actual.read_text()==old_text,'generated source differs beyond checkout path'
 assert a['target_calls'][0]['actual_profile_ranges']==['early_Q','early_K']
 device=a['device_args'];assert set(device)=={'Q','K'} and device['Q'][0] and device['K'][0]
 if addresses is None:addresses=device
 else:assert device==addresses,'application process device arguments differ'
 records.append({'pid':pid,'application':str(f.relative_to(p)),'application_sha256':sha(f),'sources':{z:sha(f.parent/('launch-'+z+'-kernel.cpp')) for z in ('Q','K')}})
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=list(csv.DictReader(f))
assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==('_rope_kernel_kernel','vector','56','0') and op.with_name('Memory.csv').is_file()
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary);assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
metrics=[]
with (p/'profile.log').open(errors='replace') as f:
 for line in f:
  if 'processedRecord:' in line:metrics.append(line.strip())
assert metrics,'parser summary missing'
result={'target':'rope-supp-01/call-0','status':'capture_identified_address_audit_pending','historical_input_and_source_match':True,'correctness':'passed_new_post_replay_reference','historical_prepare_status':prep.get('status'),'capture_binary_sha256':bsha,'parser_summaries':metrics,'representative_pid':records[0]['pid'],'application_records':records,'scope':'application replay with separate Q and K MSTX ranges; historical range-replay window remains separate; byte coverage not audited'}
(p/'capture-inspection.json').write_text(json.dumps(result,indent=2)+'\n');print('EARLY_ROPE_Q_IDENTITY_VALIDATED',len(records),'BYTE_AUDIT_PENDING')
