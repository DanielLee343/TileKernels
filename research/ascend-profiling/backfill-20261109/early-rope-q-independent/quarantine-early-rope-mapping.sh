echo __EARLY_ROPE_QUARANTINE_BEGIN__
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;p="$r/early-rope-app-probe-runs/rope-supp-01-Q/hidev-npu0/attempt-002/detail"
test -f "$p/candidate-audit-result.json";test ! -e "$p/candidate-audit-unverified-call-mapping.json";test ! -e "$p/audit-result.json"
mv -- "$p/candidate-audit-result.json" "$p/candidate-audit-unverified-call-mapping.json"
sha256sum "$p/candidate-audit-unverified-call-mapping.json" "$p/candidate-audit-q-independent.json"
echo __EARLY_ROPE_QUARANTINE_END__
