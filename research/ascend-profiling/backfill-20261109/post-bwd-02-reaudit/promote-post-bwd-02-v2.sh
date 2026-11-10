echo __POST_BWD_02_REAUDIT_PROMOTE_BEGIN__
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;p="$r/extra-proxy-runs/unified-extra2/mhc_post_bwd-02/hidev-npu0/attempt-001"
python3 - "$p" "$r/post-bwd-02-v2-test.log" <<'PY'
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]);test=Path(sys.argv[2]);txt=test.read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and output alias' in txt and '__POST_BWD_02_V2_TEST_END__' in txt
status=json.loads((p/'queue-status.json').read_text());assert status['status']=='audit_failed' and status['audit_exit']==1
d=p/'detail';src=d/'candidate-audit-result-v2.json';a=json.loads(src.read_text());assert a['target']=='unified-extra2/mhc_post_bwd-02' and a['status']=='passed' and a['dbi_requested_bytes']==1175715840 and len(a['dbi_pc'])==6
out=d/'audit-result.json';assert not out.exists();out.write_bytes(src.read_bytes())
proof={'old_queue_status_preserved':status,'reason':'four source stores compile to six static instruction PCs; all six observed; output coverage and pair totals pass','audit_script':'audit-mhc-post-bwd-app-candidate-v2.py','test_log_sha256':hashlib.sha256(test.read_bytes()).hexdigest(),'audit_result_sha256':hashlib.sha256(out.read_bytes()).hexdigest()};(d/'reaudit-proof-v2.json').write_text(json.dumps(proof,indent=2)+'\n');print('PROMOTED',proof['audit_result_sha256'])
PY
echo __POST_BWD_02_REAUDIT_PROMOTE_END__
