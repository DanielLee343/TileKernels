"""Index captured cases and raw evidence hashes without mutating capture directories."""
import hashlib,json,time
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');results=[]
for group in ('runs','mhc-runs','fused-runs','topk-runs','hash-runs','classic-runs','deepgemm-runs','unified-quant-runs','extra-proxy-runs'):
 base=root/group
 if not base.exists():continue
 for audit in sorted(base.rglob('audit-result.json')):
  d=audit.parent;a=json.loads(audit.read_text());p=d.parent
  status=p/'queue-status.json';app=(d/'application.json' if group in ('unified-quant-runs','extra-proxy-runs') else d/'metadata/application.json');monitor=d/'monitor-summary.json'
  app_replay=(a.get('replay_mode')=='application')
  if app_replay:
   ident=json.loads((d/'capture-inspection.json').read_text());rep=next(x for x in ident['application_records'] if x['pid']==ident['representative_pid']);app=d/rep['application']
  if not app.exists() or not monitor.exists():continue
  files=[audit,app,monitor,d/'command.json',d/'profile.log',d/'device-kernel.isa',d/'provenance/health-before.txt',d/'provenance/health-after.txt']
  files+=list((d/'capture').rglob('OpBasicInfo.csv'))+list((d/'capture').rglob('Memory.csv'))
  if group in ('unified-quant-runs','extra-proxy-runs'):
   files += [d/'capture-inspection.json']+list((d/'capture').rglob('aicore_binary.o'))
   if not app_replay:files += [d/'tensor-addresses.json',d/'generated-kernel.cpp']
  if app_replay:
   files += [d/'capture-inspection.json']
   for rec in ident['application_records']:
    files += [d/rec[k] for k in ('application','addresses','source') if k in rec]
  if (d/'mask-uint8.bin').exists():files.append(d/'mask-uint8.bin')
  reaudit=d/'reaudit-status.json'
  if reaudit.exists():files.append(reaudit)
  hashes={str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest() for x in files if x.is_file()}
  health=(d/'provenance/health-before.txt').read_text(errors='replace')
  target=a['target'] if 'target' in a else 'second/'+a['case']
  results.append({'target':target,'audit':a,'queue_status':json.loads(status.read_text()) if status.exists() else None,
    'reaudit_status':json.loads(reaudit.read_text()) if reaudit.exists() else None,
    'device_health':'Alarm 8C4BA00C' if '8C4BA00C' in health else 'see raw health record',
    'raw_dir':str(d),'files_sha256':hashes})
out={'created_unix':time.time(),'count':len(results),'cases':results,
     'scope':'separate hidev capture windows; alert state preserved; requested bytes are not DRAM bytes'}
(root/'hidev-capture-index.json').write_text(json.dumps(out,indent=2)+'\n')
print('indexed',len(results),'audited captures')
