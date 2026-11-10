"""Inspect one historical single-call castback application replay."""
import csv,hashlib,json,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');attempt,=sys.argv[1:];assert re.fullmatch(r'attempt-\d+',attempt)
p=root/'early-castback-single-runs-20261110/castback-n1-h128-bf16/hidev-npu0'/attempt/'detail';old=json.loads((p/'provenance/historical-default.json').read_text());cmd=json.loads((p/'command.json').read_text());assert '--replay-mode=application' in cmd and '--warm-up=5' in cmd
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(p/'provenance/historical-default-kernel.cpp')==old['source_sha256']
records=[];first=None;source_hash=None;comparison=None
for f in sorted(p.glob('application-*.json')):
 a=json.loads(f.read_text());pid=f.stem.removeprefix('application-');assert pid.isdigit() and a['status']==old['status']=='passed'
 sf=p/('generated-kernel-'+pid+'.cpp');af=p/('tensor-addresses-'+pid+'.json');assert sf.is_file() and af.is_file();assert a['inputs']==old['inputs'] and a['runtime_kernel']==old['runtime_kernel'] and a['source_sha256']==sha(sf) and a['device_inputs']==old['device_inputs'] and a['outputs']==old['outputs']
 text=sf.read_text();new=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/';previous=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/'
 normalized=hashlib.sha256(text.replace(new,previous).encode()).hexdigest();assert a['source_sha256']==old['source_sha256'] or (text.count(new)>0 and normalized==old['source_sha256'])
 addresses=json.loads(af.read_text());assert len(addresses['inputs'])==2 and len(addresses['outputs'])==1
 if first is None:first=addresses;source_hash=sha(sf);comparison='exact' if source_hash==old['source_sha256'] else 'diagnostic checkout path normalized'
 else:assert addresses==first and sha(sf)==source_hash
 records.append({'pid':pid,'application':f.name,'application_sha256':sha(f),'addresses':af.name,'addresses_sha256':sha(af),'source':sf.name,'source_sha256':sha(sf)})
assert len(records)>=2
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=csv.DictReader(f)
assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==(old['runtime_kernel'],'vector','56','0')
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary);assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
log=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',log);assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
r={'target':'early/castback-n1-h128-bf16','status':'capture_identified_address_audit_pending','correctness':'passed','historical_input_and_source_match':True,'source_comparison':comparison,'capture_binary_sha256':bsha,'parser_metrics':metrics,'representative_pid':records[0]['pid'],'application_records':records,'scope':'single-call application replay; historical Default kernel replay and board remain separate'}
(p/'capture-inspection.json').write_text(json.dumps(r,indent=2)+'\n');print('EARLY_CASTBACK_IDENTITY_VALIDATED',len(records))
