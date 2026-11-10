#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_ROPE_V7_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-rope-app-v7-queue-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-rope-app-v7-queue-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/early-rope-app-probe-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
python3 -B "$r/test-guard-v7.py"
python3 -B "$r/hidev-rope-app-v7-queue.py"
echo ALL_ROPE_V7_QUEUE_AUDITED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "QUEUE_PID=$!"
echo __START_ROPE_V7_QUEUE_END__
