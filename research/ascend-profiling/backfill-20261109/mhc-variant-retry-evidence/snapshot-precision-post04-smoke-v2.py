"""Archive the precision-labelled post04 smoke, including failures."""
import importlib.util,subprocess,sys
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');path=r/'precision-proxy-runs/unified-extra2/mhc_post_bwd-04';assert path.is_dir()
spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=('precision-proxy-runs',)
subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True)
m.scan_units=lambda root:iter([('precision-proxy-runs','unified-extra2__mhc_post_bwd-04',path)])
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-precision-post04-smoke-v2-evidence'];m.main()
