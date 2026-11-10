"""Inspect precision-labelled pre-apply backward application replay; never promote a failed reference."""
import csv,hashlib,json,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');target,attempt=sys.argv[1:]
assert re.fullmatch(r'unified-extra4/mhc_pre_apply_mix_bwd-(0[1-9]|1[0-9]|20)',target) and re.fullmatch(r'attempt-[0-9]+',attempt)
p=root/'precision-proxy-runs'/target/'hidev-npu0'/attempt/'detail'
old=json.loads((p/'provenance/historical-capture-record.json').read_text());command=json.loads((p/'command.json').read_text())
assert '--replay-mode=application' in command and '--replay-mode=kernel' not in command and '--warm-up=5' in command
apps=sorted(p.glob('application-*.json'));assert len(apps)>=2
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
records=[];addresses=None;source_sha=None;comparison=None
for f in apps:
 a=json.loads(f.read_text());pid=f.stem.removeprefix('application-');assert pid.isdigit()
 af=p/('tensor-addresses-'+pid+'.json');sf=p/('generated-kernel-'+pid+'.cpp');assert af.is_file() and sf.is_file()
 assert old['status']=='profiled_precision_failed' and old['reference_check']=='failed' and a['status'] in ('profiled_precision_failed','profiled_precision_passed') and a['matched']==old['matched']==1
 assert a['reference_check'] in ('failed','passed') and (a['status']=='profiled_precision_failed')==(a['reference_check']=='failed') and bool(a['precision_failure_preserved'])==(a['reference_check']=='failed')
 assert a['inputs']==old['inputs'] and a['params']==old['params'] and a['source_files_sha256']==old['source_files_sha256'] and a['native_kwargs']==old['native_kwargs'] and a['runtime_kernel']==old['runtime_kernel'] and a['source_sha256']==sha(sf)
 text=sf.read_text();new=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/';previous=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/'
 normalized=hashlib.sha256(text.replace(new,previous).encode()).hexdigest()
 assert a['source_sha256']==old['source_sha256'] or (text.count(new)>0 and normalized==old['source_sha256'])
 current=json.loads(af.read_text());assert len(current)==4 and all(current)
 if addresses is None:addresses=current;source_sha=sha(sf);comparison='exact' if source_sha==old['source_sha256'] else 'diagnostic checkout path normalized'
 else:assert current==addresses and sha(sf)==source_sha,'process addresses or generated source differ'
 of=p/('output-addresses-'+pid+'.json');assert of.is_file();outputs=json.loads(of.read_text());assert len(outputs)==1 and all(outputs)
 if len(records)==0: first_outputs=outputs
 else: assert outputs==first_outputs,'output addresses differ across application replay processes'
 records.append({'reference_check':a['reference_check'],'pid':pid,'application':f.name,'application_sha256':sha(f),'addresses':af.name,'addresses_sha256':sha(af),'source':sf.name,'source_sha256':sha(sf),'output_addresses':of.name,'output_addresses_sha256':sha(of)})
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=csv.DictReader(f)
assert basic['Op Name']==old['runtime_kernel'] and basic['Op Type']=='vector' and basic['Block Dim']=='56' and basic['Device Id']=='0'
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary)
assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
log=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',log)
assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
result={'target':target,'status':'precision_labelled_identity_checked_byte_audit_pending','correctness':'historical_cpu_reference_failed','historical_input_and_source_match':True,
 'source_comparison':comparison,'capture_binary_sha256':bsha,'parser_metrics':metrics,'representative_pid':records[0]['pid'],'application_records':records,
 'new_reference_checks':[x['reference_check'] for x in records],'scope':'precision-labelled pre-apply backward application replay; historical CPU reference failed; replay reference outcomes retained separately; not an accuracy-passing expert sample'}
(p/'capture-inspection.json').write_text(json.dumps(result,indent=2)+'\n');print('PRECISION_PREAPPLY10_IDENTIFIED',len(records),'REFERENCE_CHECKS',[x['reference_check'] for x in records])
