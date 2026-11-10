"""Serial old-head replay; preserve source and binary evidence."""
import fcntl,json,os,subprocess,sys,time
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');q=r/'early-head-batch-20261111-hidev-npu0';lock=(q/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);failures=[]
for case in ('head-fp32-1001','head-fp32-1024'):
 attempt='attempt-001';out=r/'early-head-batch-runs-20261111'/case/'hidev-npu0'/attempt;out.mkdir(parents=True,exist_ok=False);status={'target':'early/'+case,'attempt':attempt,'status':'running','started_unix':time.time()};(out/'queue-status.json').write_text(json.dumps(status,indent=2)+'\n');env=os.environ.copy();env.update(CASE_ID=case,ATTEMPT=attempt)
 stages=[('capture',['bash',str(r/'run-early-head-batch-20261111.sh')]),('audit',[sys.executable,'-B',str(r/'audit-early-head-batch-20261111.py'),case,attempt])]
 for stage,cmd in stages:
  with (out/(stage+'-console.log')).open('w') as f:result=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  status[stage+'_exit']=result.returncode
  if result.returncode:status['status']=stage+'_failed';break
 else:
  audit=json.loads((out/'detail/audit-result.json').read_text());assert audit['target']=='early/'+case and audit['status']=='aiv_ub_to_gm_not_applicable';status['status']='not_applicable_verified_new_window'
 status['finished_unix']=time.time();tmp=out/'queue-status.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(out/'queue-status.json');print(case,status['status'],flush=True)
 if status['status']!='not_applicable_verified_new_window':
  failures.append((case,status['status']))
  if status['status']=='capture_failed':sys.exit(1)
print('EARLY_HEAD_BATCH_FINISHED',failures,flush=True)
if failures:sys.exit(1)
