"""Inventory historical case metadata without asserting cross-batch equivalence."""
import csv,hashlib,json
from collections import Counter
from pathlib import Path
root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent
with (here/'targets.csv').open(encoding='utf-8-sig',newline='') as f:rows=[r for r in csv.DictReader(f) if r['batch']=='tilekernels-earlier' and r['per_core_requested_bytes_status']=='pending']
result=[]
for r in rows:
 p=root/r['original_profile_paths'].split(';')[0];found=None
 for up in [p,*p.parents[:10]]:
  for name in ('default.json','metadata/default.json'):
   f=up/name
   if f.is_file():found=f;break
  if found:break
 item={'target':r['target_id'],'metadata':None,'input_info_present':False,'all_input_hashes_present':False,'source_identity_present':False}
 if found:
  d=json.loads(found.read_text(encoding='utf-8-sig'));inp=d.get('inputs') or d.get('input_sha256');source=d.get('source_sha256');native=d.get('native');is_hash=lambda x:isinstance(x,str) and len(x)==64
  source_ok=is_hash(source) or (isinstance(native,dict) and is_hash(native.get('source_sha256'))) or (isinstance(native,list) and bool(native) and all(isinstance(x,dict) and is_hash(x.get('source_sha256')) for x in native))
  hashes=d.get('input_sha256');items=d.get('inputs')
  full=(isinstance(hashes,list) and bool(hashes) and all(isinstance(x,str) and len(x)==64 for x in hashes)) or (isinstance(items,list) and bool(items) and all(isinstance(x,dict) and isinstance(x.get('sha256'),str) and len(x['sha256'])==64 for x in items))
  item.update(metadata=found.relative_to(root).as_posix(),metadata_sha256=hashlib.sha256(found.read_bytes()).hexdigest(),input_info_present=bool(inp),all_input_hashes_present=bool(full),source_identity_present=bool(source_ok),metadata_status=d.get('status'))
 result.append(item)
summary={'input_info_and_source':sum(x['input_info_present'] and x['source_identity_present'] for x in result),'all_input_hashes_and_source':sum(x['all_input_hashes_present'] and x['source_identity_present'] for x in result)}
out={'scope':'historical metadata presence only; not proof of matching another case, device, replay or correctness','count':len(result),'summary':summary,'records':result}
(here/'early-metadata-inventory.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({'count':len(result),'summary':summary}))
