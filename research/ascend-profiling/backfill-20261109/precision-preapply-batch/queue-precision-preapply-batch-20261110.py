"""Observe byte records for precision-labelled pre-apply cases without accuracy promotion."""
import fcntl,json,os,re,subprocess,sys,time
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');q=r/'precision-preapply-batch-20261110-hidev-npu0';lock=(q/'queue.lock').open('w');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
test=(r/'precision-preapply-batch-audit-test-20261110.log').read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and output alias' in test and '__PRECISION_PREAPPLY_BATCH_AUDIT_TEST_END__' in test
for num in (9,6,11,12,14,18,2,4):
 case=f'mhc_pre_apply_mix_bwd-{num:02d}';target='unified-extra4/'+case;base=r/'precision-proxy-runs'/target/'hidev-npu0';ids=[int(x.name[8:]) for x in base.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)];attempt=f'attempt-{max(ids,default=0)+1:03d}';out=base/attempt;out.mkdir(parents=True,exist_ok=False);status={'target':target,'attempt':attempt,'status':'running','started_unix':time.time()};(out/'queue-status.json').write_text(json.dumps(status,indent=2)+'\n');env=os.environ.copy();env.update(TARGET_ID=target,ATTEMPT=attempt)
 stages=[('capture',['bash',str(r/'run-precision-preapply-batch-20261110.sh')]),('inspection',[sys.executable,'-B',str(r/'inspect-precision-preapply-batch-20261110.py'),target,attempt]),('audit',[sys.executable,'-B',str(r/'audit-precision-preapply-batch-20261110.py'),case,attempt])]
 for stage,cmd in stages:
  with (out/(stage+'-console.log')).open('w') as f:result=subprocess.run(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  status[stage+'_exit']=result.returncode
  if result.returncode:status['status']=stage+'_failed';break
 else:
  audit=json.loads((out/'detail/precision-preapply-batch-byte-observation.json').read_text());assert audit['target']==target and audit['status']=='precision_labelled_bytes_observed' and audit['correctness']=='historical_cpu_reference_failed';assert not (out/'detail/audit-result.json').exists();status['status']='bytes_observed_precision_failed_historical'
 status['finished_unix']=time.time();tmp=out/'queue-status.tmp';tmp.write_text(json.dumps(status,indent=2)+'\n');tmp.replace(out/'queue-status.json');print(target,status['status'],flush=True)
 if status['status']!='bytes_observed_precision_failed_historical':sys.exit(1)
print('PRECISION_PREAPPLY_BATCH_OBSERVATIONS_COMPLETE',flush=True)
