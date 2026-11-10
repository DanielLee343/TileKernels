"""Archive early rmsnorm single-call probe, including failures."""
import importlib.util,subprocess,sys
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');group='early-hash-single-runs-20261110';label='hash-n1-g3';path=r/group/label;assert path.is_dir()
spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=(group,)
subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True);m.scan_units=lambda root:iter([(group,label,path)])
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-early-hash-single-20261110'];m.main()
