from pathlib import Path
import csv,json,collections,re
out=Path('outputs/expert-profile-backfill-20261109');early=json.loads((out/'early-metadata-inventory.json').read_text())['records']
with (out/'targets.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
def digests(x):
 if not isinstance(x,list):return None
 vals=[]
 for y in x:
  if y is None:continue
  if isinstance(y,str) and re.fullmatch('[0-9a-f]{64}',y):vals.append(y);continue
  if isinstance(y,dict):
   z=y.get('tensor',y)
   if z is None:continue
   if isinstance(z,dict) and re.fullmatch('[0-9a-f]{64}',str(z.get('sha256',''))):vals.append(z['sha256']);continue
  return None
 return tuple(sorted(vals)) if vals else None
lookup=collections.defaultdict(list);main_count=0
for x in rows:
 if x['batch']!='tilekernels-default' or not x['original_profile_paths']:continue
 path=Path(x['original_profile_paths'].split('|')[0]).parents[1]/'default.json'
 if not path.is_file():continue
 d=json.loads(path.read_text(encoding='utf8'));src=d.get('source_sha256');hs=digests(d.get('inputs'))
 if d.get('status')=='passed' and src and hs:lookup[(src,hs)].append(x['target_id']);main_count+=1
matches=[];n=0
for x in early:
 d=json.loads(Path(x['metadata']).read_text(encoding='utf8'));native=d.get('native');src=d.get('source_sha256') or (native.get('source_sha256') if isinstance(native,dict) else None);hs=digests(d.get('input_sha256') or d.get('inputs'))
 if d.get('status')!='passed' or not x['all_input_hashes_present'] or not src or not hs:continue
 n+=1
 if z:=lookup.get((src,hs)):matches.append({'early_target':x['target'],'main_candidates':z})
result={'scope':'conservative fingerprint screen only; exact source hash and multiset of recorded input hashes; omits source path normalization, order and semantic mapping; no profiles reused','main_indexed':main_count,'early_indexed':n,'matches':matches}
(out/'early-source-input-fingerprint-screen.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
