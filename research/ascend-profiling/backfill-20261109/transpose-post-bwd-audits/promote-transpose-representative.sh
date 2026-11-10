set -Eeuo pipefail
echo __PROMOTE_TRANSPOSE_REP_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;p="$r/extra-proxy-runs/unified-extra4/quant_batched_transpose_weight_sf-01/hidev-npu0/attempt-001/detail"
grep -q '^PASS rejects missing output, duplicate store, wrong CSV, pointer-table mismatch and output alias$' "$r/transpose-audit-test-green.log"
python3 - "$p" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);a=p/'candidate-audit-result.json';b=p/'audit-result.json';d=json.loads(a.read_text());assert d['status']=='passed' and d['target']=='unified-extra4/quant_batched_transpose_weight_sf-01' and d['dbi_requested_bytes']==2048 and not b.exists();b.write_bytes(a.read_bytes());print('PROMOTED',d['target'],d['dbi_requested_bytes'])
PY
echo __PROMOTE_TRANSPOSE_REP_END__
