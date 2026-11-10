set -Eeuo pipefail
echo __EARLY_SINKHORN_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-single-20261110-hidev-npu0"
test ! -e "$q";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-single-20261110-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/precision-normalize03-20261110-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
test -f "$prev/exit.txt"
export ATTEMPT=attempt-001
base="$r/early-sinkhorn-single-runs-20261110/sinkhorn-cann-1/hidev-npu0";mkdir -p "$base";test ! -e "$base/$ATTEMPT";mkdir "$base/$ATTEMPT"
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-early-sinkhorn-single-20261110.sh"
python3 -B "$r/inspect-early-sinkhorn-single-20261110.py" "$ATTEMPT"
echo EARLY_SINKHORN_IDENTITY_ONLY_BYTE_AUDIT_PENDING
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __EARLY_SINKHORN_QUEUE_END__
