set -Eeuo pipefail
echo __PROMOTE_BIGFUSE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
test "$(cat "$r/mhc-bigfuse-audit-test.rc")" = 0
grep -Fxq 'PASS rejects missing output, duplicate store, wrong CSV and output alias' "$r/mhc-bigfuse-audit-test.log"
python3 - "$r" <<'PY'
import json,sys
from pathlib import Path
r=Path(sys.argv[1]);p=r/'extra-proxy-runs/unified-extra3/mhc_pre_big_fuse_fwd-01/hidev-npu0/attempt-001/detail';a=p/'candidate-audit-result.json';b=p/'audit-result.json';d=json.loads(a.read_text());assert d['status']=='passed' and d['target']=='unified-extra3/mhc_pre_big_fuse_fwd-01' and d['dbi_requested_bytes']==1343760 and not b.exists();b.write_bytes(a.read_bytes());print('PROMOTED',d['target'],d['dbi_requested_bytes'])
PY
echo __PROMOTE_BIGFUSE_END__
