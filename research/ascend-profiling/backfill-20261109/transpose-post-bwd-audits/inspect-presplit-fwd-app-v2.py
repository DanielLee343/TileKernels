"""Identify every independent application replay for one pre-split forward case."""
import csv,hashlib,json,os,re,sys
from pathlib import Path
root=Path(os.environ['BACKFILL_ROOT']);repo=Path('/workspace/tilekernels-env-20261101/src/TileKernels-private');target,attempt=sys.argv[1:];assert re.fullmatch(r'sixth/presplit-fwd-(0[1-9]|1[0-9]|20)',target)
batch,case=target.split('/');items=json.loads((root/'classic-pending.json').read_text());item,=(x for x in items if x['target']==target)
p=root/'classic-runs'/batch/case/'hidev-npu0'/attempt/'detail';old_path=repo/item['metadata_repo_path'];old=json.loads(old_path.read_text());sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(old_path)==item['metadata_sha256'] and old['source_sha256']==item['source_sha256'];old_source=old_path.parent/'default-kernel.cpp';assert sha(old_source)==old['source_sha256']
old_text=old_source.read_text().replace(r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/',r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/')
command=json.loads((p/'command.json').read_text());assert '--replay-mode=application' in command and '--warm-up=5' in command
apps=sorted(p.glob('metadata-*/application.json'));assert len(apps)>=2;records=[];addresses=None
for f in apps:
 pid=f.parent.name.removeprefix('metadata-');assert pid.isdigit();a=json.loads(f.read_text());src=f.parent/'default-kernel.cpp'
 assert a['status']==old['status']=='passed' and a['visible_devices']=='0'
 plan=json.loads((root/'classic-presplit-app-harness/cases_sixth.json').read_text());expected_case,=(x for x in plan['cases'] if x['id']==case);assert a['case']==expected_case and expected_case['id']==item['case']
 for key in ('runtime_kernel','inputs','outputs'):assert a[key]==old[key],key
 assert a['runtime_kernel']==item['kernel'] and sha(src)==a['source_sha256'] and src.read_text()==old_text
 current=(a['device_input_addresses'],a['device_output_addresses'])
 if addresses is None:addresses=current
 else:assert current==addresses,'addresses differ across application replay processes'
 records.append({'pid':pid,'application':str(f.relative_to(p)),'application_sha256':sha(f),'source':str(src.relative_to(p)),'source_sha256':sha(src)})
m=json.loads((p/'monitor-summary.json').read_text());assert m['status']=='passed' and m['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=list(csv.DictReader(f))
assert basic['Op Name']==item['kernel'] and basic['Device Id']=='0' and basic['Op Type']=='vector' and basic['Block Dim']=='56';assert op.with_name('Memory.csv').is_file()
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary);assert any(s.startswith(bsha+' ') and s.rstrip().endswith('/kernel.aibin') for s in (p/'cache-sha256.txt').read_text().splitlines())
log=(p/'profile.log').read_text(errors='replace');stores=[x for x in log.splitlines() if 'DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x];metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',log);assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
out={'target':target,'status':'capture_identified_address_audit_pending','correctness':'passed','historical_true_inputs_and_source_match':True,'source_comparison':'exact after substituting diagnostic checkout path','capture_binary_sha256':bsha,'raw_ub_to_gm_events':len(stores),'parser_metrics':metrics,'representative_pid':records[0]['pid'],'application_records':records,'scope':'application replay; all observed process inputs and addresses checked, output coverage still needs independent audit'}
(p/'capture-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print('PRESPLIT_APP_PROCESSES_VALIDATED',len(records),'EVENTS',len(stores))
