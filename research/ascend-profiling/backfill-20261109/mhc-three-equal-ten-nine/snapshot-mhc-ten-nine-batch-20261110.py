"""Snapshot attempted ten-nine batch targets, including failures."""
import importlib.util,subprocess,sys
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');names=['03','05','08','13','16','18','20'];prefix='unified-extra5__mhc_multilayer_recompute-'
spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=('extra-proxy-runs',);orig=m.scan_units
units=[x for x in orig(r) if x[1] in {prefix+n for n in names}];assert units
for _,label,path in units:subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True)
m.scan_units=lambda root:iter(units)
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-mhc-ten-nine-batch-20261110'];m.main()
