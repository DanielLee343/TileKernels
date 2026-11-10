"""Index original precision-labelled capture records without changing their status."""
import csv,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with (here/'targets.csv').open(encoding='utf-8-sig',newline='') as f:rows=[x for x in csv.DictReader(f) if x['batch']=='tilekernels-precision']
items=[]
for row in rows:
 profile=root/row['original_profile_paths'];case=profile.parent.parent;rp=case/'capture-record.json';sp=case/'capture-result.json'
 record=json.loads(rp.read_text(encoding='utf-8-sig'));result=json.loads(sp.read_text(encoding='utf-8-sig'))
 assert result['id']==row['target_id'] and result['status']=='completed' and all(result[k] is True for k in ('same_source','same_inputs','same_kernel'))
 assert record['runtime_kernel']==row['op_name'] and record['inputs'] and record['source_sha256'] and record.get('reference_check')=='failed' and result['original_cpu_reference']=='failed'
 metric=result['metrics']['OpBasicInfo'];op=profile/'OpBasicInfo.csv';assert sha(op)==metric['sha256']
 items.append({'target':row['target_id'],'capture_record':rp.relative_to(root).as_posix(),'capture_record_sha256':sha(rp),'capture_result':sp.relative_to(root).as_posix(),'capture_result_sha256':sha(sp),'input_count':len(record['inputs']),'source_sha256':record['source_sha256'],'record_status':record['status'],'original_cpu_reference':'failed','source_input_match_reported':True,'original_opbasic_sha256':sha(op),'scope':'historical record available; a new replay must independently match hashes and retain reference failure label'})
assert len(items)==13 and len({x['target'] for x in items})==13
out={'cases':items,'count':len(items),'scope':'metadata availability only; no byte audit or accuracy pass implied'}
(here/'precision-capture-metadata-index.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print('PASS metadata indexed',len(items),'all original CPU references failed')
