"""Snapshot completed precision-labelled cases and initial 09 failure."""
import importlib.util,subprocess,sys,json
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');group='precision-proxy-runs';names=[f'mhc_pre_apply_mix_bwd-{i:02d}' for i in (9,6,11,12)];spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=(group,)
units=[(group,'unified-extra4__'+c,r/group/'unified-extra4'/c) for c in names]
for _,label,path in units:
 found=list(path.rglob('detail/precision-preapply-batch-byte-observation-v2.json'));assert found and any(json.loads(x.read_text())['status']=='precision_labelled_bytes_observed' for x in found),label
 subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(path)],check=True)
m.scan_units=lambda root:iter(units)
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-precision-preapply-interim-09-06-11-12'];m.main()
