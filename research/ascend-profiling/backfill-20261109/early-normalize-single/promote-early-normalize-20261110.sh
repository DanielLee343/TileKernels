set -Eeuo pipefail
echo __EARLY_NORMALIZE_PROMOTE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
python3 - "$r" <<'PY'
from pathlib import Path
import json,hashlib,sys
r=Path(sys.argv[1]);p=r/'early-normalize-single-runs-20261110/normalize-n1-k8/hidev-npu0/attempt-001/detail';log=r/'early-normalize-audit-test-20261110.log';t=log.read_text();assert 'PASS rejects missing output, duplicate store, wrong CSV and output alias' in t and '__EARLY_NORMALIZE_AUDIT_TEST_END__' in t
f=p/'candidate-early-normalize-audit-20261110.json';x=json.loads(f.read_text());assert x['target']=='early/normalize-n1-k8' and x['dbi_requested_bytes']==36 and x['status']=='passed';o=p/'audit-result.json';assert not o.exists();o.write_bytes(f.read_bytes());(p/'early-normalize-audit-proof.json').write_text(json.dumps({'negative_test_sha256':hashlib.sha256(log.read_bytes()).hexdigest(),'audit_sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'new_application_replay_board':'8B:00.0'},indent=2)+'\n');print('PROMOTED EARLY CASTBACK',x['dbi_requested_bytes'])
PY
echo __EARLY_NORMALIZE_PROMOTE_END__
