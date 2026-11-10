"""Serial early castback captures; preserve separate application windows."""
import fcntl,json,os,subprocess,sys,time
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');q=r/'early-hash-batch-rest-20261110-hidev-npu0';lock=(q/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
test=(r/'early-hash-batch-audit-test-20261110.log').read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and output alias' in test and '__EARLY_HASH_BATCH_AUDIT_TEST_END__' in test
failures=[]
for case in ('hash-n512-g4-mask','hash-n8001-g4'):
 attempt='attempt-001';out=r/'early-hash-batch-runs-20261110'/case/'hidev-npu0'/attempt;out.mkdir(parents=True,exist_ok=False);status={'target':'early/'+case,'attempt':attempt,'status':'running','started_unix':time.time()};(out/'queue-status.json').write_text(json.dumps(status,indent=2)+'\n');env=os.environ.copy();env.update(CASE_ID=case,ATTEMPT=attempt)
 stages=[('capture',['bash',str(r/'run-early-hash-batch-20261110.sh')]),('inspection',[sys.executable,'-B',str(r/'inspect-early-hash-batch-20261110.py'),case,attempt]),('audit',[sys.executable,'-B',str(r/'audit-early-hash-batch-20261110.py'),case,attempt])]
 for stage,cmd in stages:
  with (out/(stage+'-console.log')).open('w') as f:result=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  status[stage+'_exit']=result.returncode
  if result.returncode:status['status']=stage+'_failed';break
 else:
  cand=out/'detail/candidate-early-hash-batch-audit-20261110.json';final=out/'detail/audit-result.json';audit=json.loads(cand.read_text());assert audit['target']=='early/'+case and audit['status']=='passed' and not final.exists();final.write_bytes(cand.read_bytes());status['status']='passed'
 status['finished_unix']=time.time();tmp=out/'queue-status.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(out/'queue-status.json');print(case,status['status'],flush=True)
 if status['status']!='passed':
  failures.append((case,status['status']))
  if status['status']=='capture_failed':sys.exit(1)
print('EARLY_HASH_REST_FINISHED',failures,flush=True)
if failures:sys.exit(1)
