"""Snapshot three completed early SwiGLU cases while the queue runs."""
import importlib.util,subprocess,sys,json
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');group='early-rmsnorm-batch-runs-20261110';names=['rmsnorm-supp-04','rmsnorm-supp-05','rmsnorm-supp-06'];spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=(group,)
units=[(group,c,r/group/c) for c in names]
for _,label,path in units:
 found=list(path.rglob('detail/audit-result.json'));assert found and any(json.loads(x.read_text())['status']=='passed' for x in found),label
 subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True)
m.scan_units=lambda root:iter(units)
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-early-rmsnorm-interim-04-05-06'];m.main()
