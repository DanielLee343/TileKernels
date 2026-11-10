"""Capture pending early single-call Sinkhorn cases, smallest first."""
import fcntl,json,os,subprocess,sys,time
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');q=r/'early-sinkhorn-batch-20261110-hidev-npu0';lock=(q/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
items=json.loads((r/'early-sinkhorn-batch-harness-20261110/selected_cases.json').read_text())['cases'];assert len(items)==19 and len({x['id'] for x in items})==19 and all(x['task']=='sinkhorn' for x in items)
for item in sorted(items,key=lambda x:(x['id']!='sinkhorn-supp-02',x['logical_input_bytes'])):
 case=item['id'];attempt='attempt-001';out=r/'early-sinkhorn-batch-runs-20261110'/case/'hidev-npu0'/attempt;out.mkdir(parents=True,exist_ok=False);status={'target':'early/'+case,'attempt':attempt,'status':'running','started_unix':time.time()};(out/'queue-status.json').write_text(json.dumps(status,indent=2)+'\n');env=os.environ.copy();env.update(CASE_ID=case,ATTEMPT=attempt)
 stages=[('capture',['bash',str(r/'run-early-sinkhorn-batch-20261110.sh')]),('inspection',[sys.executable,'-B',str(r/'inspect-early-sinkhorn-batch-20261110.py'),case,attempt]),('audit',[sys.executable,'-B',str(r/'audit-early-sinkhorn-batch-20261110.py'),case,attempt])]
 for stage,cmd in stages:
  with (out/(stage+'-console.log')).open('w') as f:result=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  status[stage+'_exit']=result.returncode
  if result.returncode:status['status']=stage+'_failed';break
 else:
  cand=out/'detail/candidate-early-sinkhorn-batch-audit-20261110.json';final=out/'detail/audit-result.json';audit=json.loads(cand.read_text());assert audit['target']=='early/'+case and audit['status']=='passed' and not final.exists()
  testlog=r/'early-sinkhorn-batch-audit-test-20261110.log'
  if case=='sinkhorn-supp-02':
   with testlog.open('w') as f:neg=subprocess.run(['bash',str(r/'test-early-sinkhorn-batch-audit-20261110.sh')],stdout=f,stderr=subprocess.STDOUT)
   status['negative_test_exit']=neg.returncode
   if neg.returncode:status['status']='negative_test_failed'
  if status['status']=='running':
   test=testlog.read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and output alias' in test and '__EARLY_SINKHORN_BATCH_AUDIT_TEST_END__' in test
   final.write_bytes(cand.read_bytes());status['status']='passed'
 status['finished_unix']=time.time();tmp=out/'queue-status.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(out/'queue-status.json');print(case,status['status'],flush=True)
 if status['status']!='passed':sys.exit(1)
print('EARLY_SINKHORN_BATCH_AUDITED',flush=True)
