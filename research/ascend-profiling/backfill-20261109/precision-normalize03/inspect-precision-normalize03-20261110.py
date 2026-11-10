"""Inspect precision-labelled normalize replay without changing its precision label."""
import csv,hashlib,json,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');attempt,=sys.argv[1:];assert re.fullmatch(r'attempt-\d+',attempt)
p=root/'precision-normalize03-runs-20261110/normalize-03/hidev-npu0'/attempt/'detail';old=json.loads((p/'provenance/historical-capture-record.json').read_text());assert old['reference_check']=='failed'
cmd=json.loads((p/'command.json').read_text());assert '--replay-mode=application' in cmd and '--warm-up=5' in cmd
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();records=[];first=None
for f in sorted(p.glob('metadata-*/application.json')):
 a=json.loads(f.read_text());pid=f.parent.name.removeprefix('metadata-');assert pid.isdigit();src=f.parent/'default-kernel.cpp';assert src.is_file()
 assert a['status'] in ('profiled_precision_failed','profiled_precision_passed') and a['reference_check'] in ('failed','passed') and (a['status']=='profiled_precision_failed')==(a['reference_check']=='failed')
 assert a['runtime_kernel']==old['runtime_kernel'] and a['inputs']==old['inputs'] and a['outputs']==old['outputs'] and sha(src)==a['source_sha256']
 text=src.read_text();norm=text.replace(r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/',r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/');assert a['source_sha256']==old['source_sha256'] or hashlib.sha256(norm.encode()).hexdigest()==old['source_sha256']
 addr=(a['device_input_addresses'],a['device_output_addresses']);assert len(addr[0])==1 and len(addr[1])==2
 if first is None:first=addr
 else:assert addr==first
 records.append({'pid':pid,'reference_check':a['reference_check'],'application':str(f.relative_to(p)),'application_sha256':sha(f),'source':str(src.relative_to(p)),'source_sha256':sha(src)})
assert len(records)>=2
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=csv.DictReader(f)
assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==(old['runtime_kernel'],'vector','56','0')
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary);assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
log=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',log);assert metrics
result={'target':'starter/normalize-03','status':'precision_labelled_identity_checked_byte_audit_pending','correctness':'historical_cpu_reference_failed','historical_input_and_source_match':True,'capture_binary_sha256':bsha,'parser_metrics':metrics,'parser_health':'failed' if any(d!='0' or m!='0' for _,d,m in metrics) else 'unverified_other_counters','representative_pid':records[0]['pid'],'application_records':records,'new_reference_checks':[x['reference_check'] for x in records],'scope':'precision-labelled application replay; no byte completeness or precision promotion'}
(p/'capture-inspection.json').write_text(json.dumps(result,indent=2)+'\n');print('PRECISION_NORMALIZE03_IDENTIFIED',len(records),'PARSER',result['parser_health'],'REF',[x['reference_check'] for x in records])
