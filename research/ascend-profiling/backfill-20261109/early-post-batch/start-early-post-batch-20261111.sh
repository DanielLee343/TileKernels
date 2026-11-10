set -Eeuo pipefail
echo __EARLY_POST_BATCH_START_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-post-batch-20261111-hidev-npu0"
test ! -e "$q";grep -Fq '__EARLY_POST_BATCH_AUDIT_TEST_END__' "$r/early-post-batch-audit-test-20261111.log";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-post-batch-20261111-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
python3 -B "$r/queue-early-post-batch-20261111.py"
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __EARLY_POST_BATCH_START_END__
