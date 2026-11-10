echo __MULTI_PROMOTE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;a=$(cat "$r/extra-mhc-multilayer-v2-smoke-hidev-npu0/attempt.txt");p="$r/extra-proxy-runs/unified-extra5/mhc_multilayer_recompute-01/hidev-npu0/$a/detail"
python3 - "$p" <<'PY'
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]);src=p/'candidate-audit-result.json';d=json.loads(src.read_text());assert d['target']=='unified-extra5/mhc_multilayer_recompute-01' and d['status']=='passed' and d['dbi_requested_bytes']==104857600
out=p/'audit-result.json';assert not out.exists();out.write_bytes(src.read_bytes());print('PROMOTED',hashlib.sha256(out.read_bytes()).hexdigest())
PY
echo __MULTI_PROMOTE_END__
