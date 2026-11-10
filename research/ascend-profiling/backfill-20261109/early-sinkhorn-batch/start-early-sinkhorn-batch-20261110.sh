set -Eeuo pipefail
echo __EARLY_SINKHORN_BATCH_START_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-batch-20261110-hidev-npu0"
test ! -e "$q";test -f "$r/queue-early-sinkhorn-batch-20261110.py";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-batch-20261110-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
python3 -B "$r/queue-early-sinkhorn-batch-20261110.py"
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __EARLY_SINKHORN_BATCH_START_END__
