import json, hashlib
from pathlib import Path
from collections import defaultdict
import numpy as np
root=Path(__file__).resolve().parents[2]; out=Path(__file__).resolve().parent
src=root/'expert-rule-todo3a-20261106/evidence.json'
data=json.loads(src.read_text(encoding='utf-8-sig'))
rows=[x for x in data['captures'] if x['group']=='0000:8B:00.0' and x['family'] in ('rmsnorm','swiglu')]
assert len(rows)==32 and len({x['case'] for x in rows})==32
result={'input_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'families':{}}
for family in ('rmsnorm','swiglu'):
 rs=[x for x in rows if x['family']==family]; unknown=[x['case'] for x in rs if not x['source_hashes']]; rs=[x for x in rs if x['source_hashes']]
 # Connected components prevent leakage even if hash lists overlap.
 groups=[]
 for x in rs:
  matches=[g for g in groups if g['hashes'].intersection(x['source_hashes'])]
  g={'hashes':set(x['source_hashes']),'rows':[x]}
  for old in matches: g['hashes'].update(old['hashes']);g['rows']+=old['rows'];groups.remove(old)
  groups.append(g)
 def mat(xs,m):
  return np.array([[x['N']] if m=='N' else [x['G']] if m=='G' else [1,x['N'],x['G']] for x in xs],float)
 predictions={m:[] for m in ('N','G','intercept_N_G','median_A')}
 for g in groups:
  test=g['rows']; train=[x for x in rs if x not in test]
  for m in predictions:
   if m=='median_A': ys=np.full(len(test),np.median([x['A'] for x in train]))
   else:
    X=mat(train,m); scale=np.maximum(np.linalg.norm(X,axis=0),1e-30); coef=np.linalg.lstsq(X/scale,np.array([x['A'] for x in train]),rcond=None)[0]/scale; ys=mat(test,m)@coef
   for x,y in zip(test,ys):
    d={'case':x['case'],'hashes':sorted(g['hashes']),'actual':x['A'],'predicted':float(y),'relative_error':float((y-x['A'])/x['A'])}
    d.update({v+'_outside':bool(x[v]<min(t[v] for t in train) or x[v]>max(t[v] for t in train)) for v in ('G','N')}); predictions[m].append(d)
 stats={}
 for m,ps in predictions.items():
  err=np.array([p['relative_error'] for p in ps]); stats[m]={'median_abs':float(np.median(abs(err))),'p90_abs':float(np.quantile(abs(err),.9)),'median_signed':float(np.median(err)),'negative_predictions':sum(p['predicted']<=0 for p in ps),'predictions':ps}
 p=predictions['G']; result['families'][family]={'cases':len(rs),'groups':len(groups),'unknown_hash_cases':unknown,'group_sizes':sorted([len(g['rows']) for g in groups],reverse=True),'ranges':{v:[min(x[v] for x in rs),max(x[v] for x in rs)] for v in ('G','N')},'log_G_N_correlation':float(np.corrcoef(np.log([x['G'] for x in rs]),np.log([x['N'] for x in rs]))[0,1]),'outside_either':sum(x['G_outside'] or x['N_outside'] for x in p),'outside_cases':[x['case'] for x in p if x['G_outside'] or x['N_outside']],'models':stats}
(out/'results.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(result,indent=2,ensure_ascii=False))
