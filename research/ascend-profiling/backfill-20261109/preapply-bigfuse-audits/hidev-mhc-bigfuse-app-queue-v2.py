"""Capture mHC pre-big-fuse forward cases serially; stop on any failed inspection/audit."""
import fcntl,json,os,re,subprocess,sys,time
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');q=root/'extra-mhc-bigfuse-app-queue-v2-hidev-npu0';q.mkdir(exist_ok=True)
lock=(q/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
items=[x for x in json.loads((root/'extra-proxy-mhc-big-fuse-app-harness/cases.json').read_text())['cases'] if x['group']=='mhc_pre_big_fuse_fwd'];assert len(items)==20
for x in items:
 case=x['id'];target=x['target_id'];assert target=='unified-extra3/'+case
 base=root/'extra-proxy-runs'/target/'hidev-npu0';attempts=sorted(base.glob('attempt-*')) if base.exists() else []
 if any((a/'detail/audit-result.json').exists() and json.loads((a/'detail/audit-result.json').read_text()).get('status')=='passed' for a in attempts):
  print(target,'already audited; skip',flush=True);continue
 indices=[int(a.name.removeprefix('attempt-')) for a in attempts if re.fullmatch(r'attempt-\d+',a.name)]
 attempt=f'attempt-{max(indices,default=0)+1:03d}';out=base/attempt;out.mkdir(parents=True,exist_ok=False)
 status={'target':target,'attempt':attempt,'status':'running','started_unix':time.time()}
 (out/'queue-status.json').write_text(json.dumps(status,indent=2)+'\n')
 env=os.environ.copy();env.update(TARGET_ID=target,ATTEMPT=attempt)
 stages=[('capture',['bash',str(root/'run-hidev-extra-mhc-big-fuse-app.sh')]),
         ('inspection',[sys.executable,'-B',str(root/'inspect-mhc-big-fuse-app.py'),target,attempt]),
         ('audit',[sys.executable,'-B',str(root/'audit-mhc-big-fuse-app-candidate.py'),case,attempt])]
 for stage,cmd in stages:
  with (out/(stage+'-console.log')).open('w') as f:r=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  status[stage+'_exit']=r.returncode
  if r.returncode:status['status']=stage+'_failed';break
 else:
  candidate=out/'detail/candidate-audit-result.json';final=out/'detail/audit-result.json'
  data=json.loads(candidate.read_text());assert data['target']==target and data['status']=='passed' and not final.exists()
  final.write_bytes(candidate.read_bytes());status['status']='passed'
 status['finished_unix']=time.time();tmp=out/'queue-status.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(out/'queue-status.json')
 print(target,status['status'],flush=True)
 if status['status']!='passed':sys.exit(1)
print('ALL_MHC_BIGFUSE_APP_SELECTED_AUDITED',flush=True)
