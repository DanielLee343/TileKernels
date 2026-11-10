set -Eeuo pipefail
echo __EARLY_CASTBACK_PROMOTE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
python3 - "$r" <<'PY'
from pathlib import Path
import json,hashlib,sys
r=Path(sys.argv[1]);p=r/'early-castback-single-runs-20261110/castback-n1-h128-bf16/hidev-npu0/attempt-001/detail';log=r/'early-castback-audit-test-20261110.log';t=log.read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and output alias' in t and '__EARLY_CASTBACK_AUDIT_TEST_END__' in t
f=p/'candidate-early-castback-audit-20261110.json';x=json.loads(f.read_text());assert x['target']=='early/castback-n1-h128-bf16' and x['dbi_requested_bytes']==256 and x['status']=='passed';o=p/'audit-result.json';assert not o.exists();o.write_bytes(f.read_bytes());(p/'early-castback-audit-proof.json').write_text(json.dumps({'negative_test_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'audit_sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'historical_kernel_replay_board':'0D:00.0','new_application_replay_board':'8B:00.0'},indent=2)+'\n');print('PROMOTED EARLY CASTBACK',x['dbi_requested_bytes'])
PY
echo __EARLY_CASTBACK_PROMOTE_END__
