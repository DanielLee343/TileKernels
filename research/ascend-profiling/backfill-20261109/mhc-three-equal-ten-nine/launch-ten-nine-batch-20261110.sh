set -Eeuo pipefail
echo __TEN_NINE_BATCH_START_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten-nine-batch-20261110-hidev-npu0"
test ! -e "$q"
python3 -B "$r/audit-mhc-ten-nine-batch-20261110.py" mhc_multilayer_recompute-03 attempt-002
mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten-nine-batch-20261110-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/precision-post04-v2-smoke-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
test -f "$prev/exit.txt"
python3 -B "$r/queue-mhc-ten-nine-batch-20261110.py"
echo ALL_TEN_NINE_BATCH_COMPLETE
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __TEN_NINE_BATCH_START_END__
