"""Snapshot only the four listed completed pre-apply backward case directories."""
import importlib.util,subprocess,sys,json
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');names=['13','15','16','17'];prefix='unified-extra4__mhc_pre_apply_mix_bwd-'
spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=('extra-proxy-runs',);orig=m.scan_units
units=[x for x in orig(r) if x[1] in {prefix+n for n in names}];assert len(units)==len(names)
for _,label,path in units:
 found=list(path.rglob('detail/audit-result.json'));assert found and any(json.loads(f.read_text())['status']=='passed' for f in found),label
 subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True)
m.scan_units=lambda root:iter(units)
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-preapply-v2-interim-13-17'];m.main()
