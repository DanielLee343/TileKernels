"""Capture 10-layer 9-post mHC recompute cases serially; stop on any failed inspection/audit."""
import fcntl,json,os,re,subprocess,sys,time
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');q=root/'mhc-ten-nine-batch-20261110-hidev-npu0';q.mkdir(exist_ok=True)
lock=(q/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
items=[x for x in json.loads((root/'extra-proxy-mhc-multilayer-app-harness/cases.json').read_text())['cases'] if x['group']=='mhc_multilayer_recompute' and x['params']['num_layers']==10 and x['params']['num_post']==9]
expected={f'mhc_multilayer_recompute-{i:02d}' for i in (3,5,8,13,16,18,20)}
actual=[x['id'] for x in items];assert len(actual)==len(set(actual)) and set(actual)==expected, (sorted(expected-set(actual)),sorted(set(actual)-expected))
for x in items:
 case=x['id'];target=x['target_id'];assert target=='unified-extra5/'+case
 base=root/'extra-proxy-runs'/target/'hidev-npu0';attempts=sorted(base.glob('attempt-*')) if base.exists() else []
 if any((a/'detail/audit-result.json').exists() and json.loads((a/'detail/audit-result.json').read_text()).get('status')=='passed' for a in attempts):
  print(target,'already audited; skip',flush=True);continue
 indices=[int(a.name.removeprefix('attempt-')) for a in attempts if re.fullmatch(r'attempt-\d+',a.name)]
 attempt=f'attempt-{max(indices,default=0)+1:03d}';out=base/attempt;out.mkdir(parents=True,exist_ok=False)
 status={'target':target,'attempt':attempt,'status':'running','started_unix':time.time()}
 (out/'queue-status.json').write_text(json.dumps(status,indent=2)+'\n')
 env=os.environ.copy();env.update(TARGET_ID=target,ATTEMPT=attempt)
 stages=[('capture',['bash',str(root/'run-mhc-multilayer-guard7-20261110.sh')]),
         ('inspection',[sys.executable,'-B',str(root/'inspect-mhc-multilayer-app.py'),target,attempt]),
         ('audit',[sys.executable,'-B',str(root/'audit-mhc-ten-nine-batch-20261110.py'),case,attempt])]
 for stage,cmd in stages:
  with (out/(stage+'-console.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  status[stage+'_exit']=r.returncode
  if r.returncode:status['status']=stage+'_failed';break
 else:
  candidate=out/'detail/candidate-audit-ten-nine-result.json';final=out/'detail/audit-result.json'
  data=json.loads(candidate.read_text());assert data['target']==target and data['status']=='passed' and not final.exists()
  final.write_bytes(candidate.read_bytes());status['status']='passed'
 status['finished_unix']=time.time();tmp=out/'queue-status.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(out/'queue-status.json')
 print(target,status['status'],flush=True)
 if status['status']!='passed':sys.exit(1)
print('ALL_MHC_TEN_NINE_SELECTED_AUDITED',flush=True)
