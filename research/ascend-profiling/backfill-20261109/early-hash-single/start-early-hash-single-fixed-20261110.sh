set -Eeuo pipefail
echo __EARLY_HASH_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-hash-single-20261110-hidev-npu0"
test ! -e "$q";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-hash-single-20261110-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/early-fused3584-single-20261110-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
test -f "$prev/exit.txt"
export ATTEMPT=attempt-001
base="$r/early-hash-single-runs-20261110/hash-n1-g3/hidev-npu0";mkdir -p "$base";test ! -e "$base/$ATTEMPT";mkdir "$base/$ATTEMPT"
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-early-hash-single-20261110.sh"
python3 -B "$r/inspect-early-hash-single-20261110.py" "$ATTEMPT"
python3 -B "$r/audit-early-hash-single-20261110.py" "$ATTEMPT"
bash "$r/test-early-hash-audit-20261110.sh" > "$r/early-hash-audit-test-20261110.log" 2>&1
bash "$r/promote-early-hash-20261110.sh"
echo EARLY_HASH_AUDITED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __EARLY_HASH_QUEUE_END__
