"""Snapshot six completed workbook windows; no new profiling."""
import importlib.util,subprocess,sys
from pathlib import Path
r=Path('/workspace/expert-profile-backfill-20261109-hidev');spec=importlib.util.spec_from_file_location('archive_captures',r/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
extra=[('unified-extra2','mhc_post_bwd-01'),('unified-extra4','mhc_pre_apply_mix_bwd-01'),('unified-extra3','mhc_pre_big_fuse_fwd-01'),('unified-extra4','quant_batched_transpose_weight_sf-01')];deep=['mgroup-fp8fp4-nn-g4-m128-n256-k512','mgroup-fp8fp4-nt-g8-m32-n256-k512']
units=[('extra-proxy-runs',a+'__'+b,r/'extra-proxy-runs'/a/b) for a,b in extra]+[('deepgemm-runs',c,r/'deepgemm-runs'/c) for c in deep];assert all(p.is_dir() for _,_,p in units)
for _,_,p in units:subprocess.run([sys.executable,'-B',str(r/'scan-public-archive.py'),str(p)],check=True)
m.GROUPS=('extra-proxy-runs','deepgemm-runs');m.scan_units=lambda root:iter(units)
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(r),'--out','/workspace/expert-profile-backfill-20261109-workbook-six-windows-20261110'];m.main()
