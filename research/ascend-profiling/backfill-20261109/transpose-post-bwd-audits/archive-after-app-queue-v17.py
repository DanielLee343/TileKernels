"""Snapshot a finished queue's attempted cases, including failures."""
import importlib.util,subprocess,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');which,=sys.argv[1:]
filters={'transpose-v2':('extra-proxy-runs','unified-extra4__quant_batched_transpose_weight_sf-'),'rope-v7':('extra-proxy-runs','unified-extra4__rotary_embedding-'),'early-rope-app-probe':('early-rope-app-probe-runs','rope-supp-01-Q'),'hash-app-probe':('hash-app-probe-runs','starter__hash-15'),'post-fwd-extra6':('extra-proxy-runs','unified-extra6__post-fwd-'),'finalize-extra6':('extra-proxy-runs','unified-extra6__finalize-'),'paged-reuse-frozen':('deepgemm-runs','paged-sparse-fp8-q4-k256-h8-b8'),'momentum-v2':('extra-proxy-runs','unified-extra5__engram_sinkhorn_momentum_update-'),'presplit-fwd':('classic-runs','sixth__presplit-fwd-'),'mhc-pre-apply-bwd':('extra-proxy-runs','unified-extra4__mhc_pre_apply_mix_bwd-'),'mhc-multilayer':('extra-proxy-runs','unified-extra5__mhc_multilayer_recompute-'),'mhc-big-fuse':('extra-proxy-runs','unified-extra3__mhc_pre_big_fuse_fwd-'),'mhc-presplit-bwd':('extra-proxy-runs','unified-extra5__mhc_pre_split_mixes_bwd-'),'mhc-post-bwd':('extra-proxy-runs','unified-extra2__mhc_post_bwd-'),'transpose':('extra-proxy-runs','unified-extra4__quant_batched_transpose_weight_sf-'),'mhc-normw-bwd':('extra-proxy-runs','unified-extra5__mhc_fn_normw_merge_bwd-'),'step':('extra-proxy-runs','unified-extra5__engram_sinkhorn_step-'),'momentum':('extra-proxy-runs','unified-extra5__engram_sinkhorn_momentum_update-'),'cast':('extra-proxy-runs','unified-extra4__quant_per_token_cast_and_cast_back-'),'rope':('extra-proxy-runs','unified-extra4__rotary_embedding-'),'paged-first':('deepgemm-runs','paged-sparse-first-')}
assert which in filters;group,prefix=filters[which]
spec=importlib.util.spec_from_file_location('archive_captures',root/'archive-captures.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.GROUPS=(group,);original=m.scan_units
units=([('hash-app-probe-runs','starter__hash-15',root/'hash-app-probe-runs/starter/hash-15')] if which=='hash-app-probe' and (root/'hash-app-probe-runs/starter/hash-15').is_dir() else [x for x in original(root) if x[1].startswith(prefix)]);assert units
for _,_,path in units:subprocess.run([sys.executable,'-B',str(root/'scan-public-archive.py'),str(path)],check=True)
m.scan_units=lambda r:iter(units)
def no_support(source,out):
 p=out/'support.jsonl';p.write_bytes(b'');return 0,m.sha(p)
m.copy_support=no_support
sys.argv=['archive-captures.py','--root',str(root),'--out',f'/workspace/expert-profile-backfill-20261109-{which}-queue-snapshot-archive'];m.main()
