set -Eeuo pipefail
echo __ROPE_AUDIT_V2_BASELINE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
t=$(mktemp -d "$r/rope-v2-baseline.XXXXXXXX");trap 'rm -rf -- "$t"' EXIT
b=extra-proxy-runs/unified-extra4/rotary_embedding-01-q/hidev-npu0/attempt-001
mkdir -p "$t/$(dirname "$b")";cp -a "$r/$b" "$t/$b";cp "$r/audit-reduce-family.py" "$t/"
BACKFILL_ROOT="$t" python3 -B "$r/audit-rope-app-candidate-v2.py" rotary_embedding-01-q attempt-001
python3 - "$r/$b/detail/audit-result.json" "$t/$b/detail/candidate-audit-result.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]));y=json.load(open(sys.argv[2]));assert x==y,(set(x)^set(y),[(k,x[k],y[k]) for k in x.keys()&y.keys() if x[k]!=y[k]])
print('PASS original and accelerated audit output exactly identical')
PY
echo __ROPE_AUDIT_V2_BASELINE_END__
