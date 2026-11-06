"""Offline P05 calibration primitives; only A/B development adapter is admitted."""
import argparse,hashlib,importlib.util,json,sys
from decimal import Decimal,InvalidOperation
from pathlib import Path
SPLITS=('development','calibration','holdout','positive_control','negative_control')
FORMULAS=('contiguous_128_v1','per_verified_segment_128_v1')
def required_id(v): return isinstance(v,str) and bool(v.strip()) and v.lower() not in ('unknown','na','n/a')
def validate_registry(reg):
 if not isinstance(reg,dict) or any(not required_id(reg.get(k)) for k in ('device','condition')): raise ValueError('missing device or physical condition')
 if reg.get('formula') not in FORMULAS or reg.get('response') not in ('difference','ratio'): raise ValueError('unsupported fixed formula/response')
 cases=reg.get('cases')
 if not isinstance(cases,list) or not cases: raise ValueError('empty case registry')
 ids=set(); families={}
 for c in cases:
  if any(not required_id(c.get(k)) for k in ('id','family')) or c.get('split') not in SPLITS: raise ValueError('unknown case identity or split')
  if c['id'] in ids: raise ValueError('duplicate case')
  ids.add(c['id']); old=families.setdefault(c['family'],c['split'])
  if old!=c['split']: raise ValueError('implementation family leaks across splits')
 return reg
def reference(offset,length):
 if type(offset) is not int or not 0<=offset<128 or type(length) is not int or length<=0: raise ValueError('invalid offset or logical length')
 return ((offset+length+127)//128)*128
def segment_reference(segments,expected_ranges,allocation_bytes,base_offset,external_writes):
 """Pure geometry; caller must independently verify range identities and write scope."""
 if type(allocation_bytes) is not int or allocation_bytes<=0 or type(base_offset) is not int or not 0<=base_offset<128 or external_writes!='none_verified': raise ValueError('unknown allocation, offset or external writes')
 def checked(values):
  if not isinstance(values,(list,tuple)) or not values:raise ValueError('empty ranges')
  result=[]
  for v in values:
   if not isinstance(v,(list,tuple)) or len(v)!=2:raise ValueError('invalid range')
   start,length=v
   if type(start) is not int or type(length) is not int or start<0 or length<=0 or start+length>allocation_bytes:raise ValueError('range outside allocation')
   result.append((start,start+length))
  result.sort()
  if any(a[1]>b[0] for a,b in zip(result,result[1:])):raise ValueError('overlapping or duplicate range')
  return result
 def merged(ranges):
  out=[]
  for start,end in ranges:
   if out and out[-1][1]==start:out[-1]=(out[-1][0],end)
   else:out.append((start,end))
  return out
 actual=checked(segments); expected=checked(expected_ranges)
 if merged(actual)!=merged(expected):raise ValueError('missing or unexpected valid bytes')
 return sum(reference((base_offset+start)%128,end-start) for start,end in actual)
def number(x):
 try:r=Decimal(str(x))
 except (InvalidOperation,ValueError) as e:raise ValueError('nonfinite input') from e
 if not r.is_finite():raise ValueError('nonfinite input')
 return r
def aggregate(repeats,device,formula,response):
 if not repeats:raise ValueError('no repeats')
 seen=set(); values=[]
 for row in repeats:
  if row.get('device')!=device or row.get('formula')!=formula:raise ValueError('mixed device or formula')
  key=row.get('capture_sha256')
  if not required_id(key) or key in seen:raise ValueError('missing/duplicate capture identity')
  seen.add(key); w=number(row['w']); r=number(row['r'])
  if w<0 or r<=0:raise ValueError('invalid W or R')
  values.append(w-r if response=='difference' else w/r-1)
 return values
def aggregate_cases(cases,device,formula,response):
 seen=set()
 for rows in cases.values():
  for row in rows:
   key=row.get('capture_sha256')
   if key in seen:raise ValueError('capture reused across cases')
   seen.add(key)
 return {key:aggregate(rows,device,formula,response) for key,rows in cases.items()}
def calibrate(cases):
 if not cases or any(len(values)<3 for values in cases.values()):raise ValueError('need at least three repeats per calibration case')
 # One case-level worst repeat first; independent cases have equal status.
 return max(max(values) for values in cases.values())
def summarize(cases):
 if not cases or any(len(values)<3 for values in cases.values()):raise ValueError('need three repeats per case')
 return {key:{'repeats':values[:], 'minimum':min(values), 'maximum':max(values)} for key,values in cases.items()}
def check_holdout(cases,boundary):
 summary=summarize(cases); b=number(boundary)
 flags={key:item['maximum']>b for key,item in summary.items()}
 return {'boundary_fixed':b,'cases':summary,'false_positive_cases':sum(flags.values()),'case_count':len(flags),'per_case_flags':flags}
def development_ab(root):
 p=Path(__file__).resolve().parents[2]/'expert-rule-todo5-20261106/p05-ab-analysis/analysis.py'
 if hashlib.sha256(p.read_bytes()).hexdigest()!='2483e02701393ff5073232c4af43c5165344da8dacbabed065c907936d3de0da': raise ValueError('A/B validator version changed')
 spec=importlib.util.spec_from_file_location('frozen_ab',p); mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 out=mod.analyze(root)
 return {'source':'A/B existing validator','role':'development only','A_status':out['A']['status'],'B_status':out['B']['status'],'runs':[{'ordinal':r['ordinal'],'case':r['case'],'repeat':r['repeat'],'eligible':r['eligible'],'memory_sha256':r.get('memory_sha256'),'memory_path':r.get('memory_path')} for r in out['runs']]}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('registry',type=Path); ap.add_argument('--freeze-sha256',required=True); ap.add_argument('--ab-root',type=Path); args=ap.parse_args()
 try:
  raw=args.registry.read_bytes(); digest=hashlib.sha256(raw).hexdigest()
  if digest!=args.freeze_sha256:raise ValueError('registry hash mismatch')
  reg=validate_registry(json.loads(raw.decode('utf-8-sig')))
  # This is not proof that registry was frozen before any outcome was inspected.
  out={'status':'reference_insufficient','registry_sha256':digest,'case_counts':{s:sum(c['split']==s for c in reg['cases']) for s in SPLITS},'formula':reg['formula'],'response':reg['response'],'boundary':None,'promotion':'prohibited','reason':'no verified independent calibration adapter or freeze-before-access evidence; no holdout or customer measurements read','required':'precommitted case/implementation identities, validated same-capture raw data and formula applicability, independent calibration case adapter'}
  if args.ab_root:out['development']=development_ab(args.ab_root)
  print(json.dumps(out,indent=2,ensure_ascii=False))
 except (OSError,ValueError,KeyError,TypeError) as e: print(json.dumps({'status':'reference_insufficient','reason':str(e)})); raise SystemExit(2)
if __name__=='__main__':main()
