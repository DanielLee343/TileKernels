"""Identify hash-15 application replay and record full parser health, without promotion."""
import csv,hashlib,json,os,re,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');attempt,=sys.argv[1:];assert re.fullmatch(r'attempt-\d+',attempt);target='starter/hash-15'
p=root/'hash-app-probe-runs/starter/hash-15/hidev-npu0'/attempt/'detail';old_path=root/'hash-history/hash-15/default.json';old=json.loads(old_path.read_text());item,=(x for x in json.loads((root/'hash-pending.json').read_text()) if x['target']==target)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert sha(old_path)==item['metadata_sha256'];old_source=old_path.parent/'default-kernel.cpp';assert sha(old_source)==old['source_sha256']
old_text=old_source.read_text().replace(r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/',r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/')
command=json.loads((p/'command.json').read_text());assert '--replay-mode=application' in command and '--warm-up=5' in command
apps=sorted(p.glob('metadata-*/application.json'));assert len(apps)>=2;records=[];addresses=None
for f in apps:
 pid=f.parent.name.removeprefix('metadata-');assert pid.isdigit();a=json.loads(f.read_text());src=f.parent/'default-kernel.cpp'
 assert a['status']==old['status']=='passed' and a['visible_devices']=='0'
 plan=json.loads((root/'hash-app-probe-harness/cases_starter.json').read_text());expected_case,=(x for x in plan['cases'] if x['id']=='hash-15');assert a['case']==expected_case
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
fields=('droppedRecord','memoryCopyFailed','invalidParam','overflow','invalidDataCount','memoryCorruption','invalidRecordType','outOfBoundsRead');errors=[];summaries=[]
with (p/'profile.log').open(errors='replace') as f:
 for line in f:
  if 'processedRecord:' not in line:continue
  summaries.append(line.strip())
  for key in fields:
   v=re.search(r'\b'+key+r'\s*:?\s*(\d+)',line)
   if not v or int(v.group(1)):errors.append(key+'='+ (v.group(1) if v else 'missing'))
  v=re.search(r'receivedPacket\s+(\d+),\s*processedPacket\s+(\d+)',line)
  if not v or v.group(1)!=v.group(2):errors.append('packet mismatch/missing')
  v=re.search(r'each record type process fail count\s+([0-9, ]+)',line)
  if not v or any(int(x) for x in re.findall(r'\d+',v.group(1))):errors.append('per-type failures/missing')
if not summaries:errors.append('parser summary missing')
out={'target':target,'status':'capture_identified_address_audit_pending' if not errors else 'capture_identified_parser_incomplete','historical_true_inputs_and_source_match':True,'capture_binary_sha256':bsha,'parser_errors':sorted(set(errors)),'parser_summaries':summaries,'representative_pid':records[0]['pid'],'application_records':records,'scope':'application replay; no byte audit or admission; old kernel replay stays separate'}
(p/'capture-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'target':target,'status':out['status'],'parser_errors':out['parser_errors'],'processes':len(records)},indent=2))
