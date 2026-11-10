"""Check one extra6 finalize application replay; does not promote byte completeness."""
import csv, hashlib, json, re, sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');target,attempt=sys.argv[1:]
assert re.fullmatch(r'unified-extra6/finalize-(02|13|17|19)-retry',target) and re.fullmatch(r'attempt-[0-9]+',attempt)
p=root/'extra-proxy-runs'/target/'hidev-npu0'/attempt/'detail';old=json.loads((p/'provenance/historical-default.json').read_text());command=json.loads((p/'command.json').read_text())
assert '--replay-mode=application' in command and '--warm-up=5' in command
apps=sorted(p.glob('application-*.json'));assert len(apps)>=2
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records=[];addresses=None;source_sha=None
for f in apps:
 a=json.loads(f.read_text());pid=f.stem.removeprefix('application-');assert pid.isdigit()
 af=p/('tensor-addresses-'+pid+'.json');sf=p/('generated-kernel-'+pid+'.cpp');assert af.is_file() and sf.is_file()
 assert a['status']==old['status']=='passed' and a['matched']==old['matched']==1
 assert a['inputs']==old['inputs'] and a['runtime_kernel']==old['runtime_kernel'] and a['source_sha256']==sha(sf)
 text=sf.read_text();new=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/';previous=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/'
 assert a['source_sha256']==old['source_sha256'] or (text.count(new)>0 and hashlib.sha256(text.replace(new,previous).encode()).hexdigest()==old['source_sha256'])
 current=json.loads(af.read_text());assert len(current)==4 and all(current)
 if addresses is None:addresses=current;source_sha=sha(sf)
 else:assert current==addresses and sha(sf)==source_sha,'process arguments or source differ'
 records.append({'pid':pid,'application':f.name,'application_sha256':sha(f),'addresses':af.name,'addresses_sha256':sha(af),'source':sf.name,'source_sha256':sha(sf)})
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=csv.DictReader(f)
assert basic['Op Name']==old['runtime_kernel'] and basic['Op Type']=='vector' and basic['Block Dim']=='56' and basic['Device Id']=='0'
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary)
assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
log=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',log)
assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
result={'target':target,'status':'capture_identified_address_audit_pending','correctness':'passed','historical_input_and_source_match':True,'capture_binary_sha256':bsha,'parser_metrics':metrics,'representative_pid':records[0]['pid'],'application_records':records,'scope':'application replay; input/source check only; byte completeness not yet checked'}
(p/'capture-inspection.json').write_text(json.dumps(result,indent=2)+'\n');print('APP_REPLAY_PROCESSES_VALIDATED',len(records),'BYTE_AUDIT_PENDING')
