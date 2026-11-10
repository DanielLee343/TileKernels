echo __MHC_TEN_PROMOTE_BEGIN__
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;p="$r/extra-proxy-runs/unified-extra5/mhc_multilayer_recompute-02/hidev-npu0/attempt-001/detail"
python3 - "$p" "$r/mhc-ten-test.log" <<'PY'
import hashlib,json,sys
from pathlib import Path
p=Path(sys.argv[1]);test=Path(sys.argv[2]);txt=test.read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and changed pointer table' in txt and '__MHC_TEN_AUDIT_TEST_END__' in txt
src=p/'candidate-audit-ten-result.json';a=json.loads(src.read_text());assert a['target']=='unified-extra5/mhc_multilayer_recompute-02' and a['status']=='passed' and a['dbi_requested_bytes']==1048576000
out=p/'audit-result.json';assert not out.exists();out.write_bytes(src.read_bytes());proof={'scope':'10 layers / 10 post, case 02 only','missing_output_test_indices':[0,9,10,19],'test_log_sha256':hashlib.sha256(test.read_bytes()).hexdigest(),'audit_result_sha256':hashlib.sha256(out.read_bytes()).hexdigest()};(p/'ten-audit-proof.json').write_text(json.dumps(proof,indent=2)+'\n');print('PROMOTED',proof['audit_result_sha256'])
PY
echo __MHC_TEN_PROMOTE_END__
