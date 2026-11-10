#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_MHC_PREAPPLY_BWD_V2_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-mhc-pre-apply-bwd-app-queue-v2-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-mhc-pre-apply-bwd-app-queue-v2-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra-mhc-post-bwd-app-queue-v2-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
python3 -B "$r/hidev-mhc-preapply-bwd-app-queue-v2.py"
echo ALL_MHC_PREAPPLY_BWD_V2_QUEUE_AUDITED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "QUEUE_PID=$!"
echo __START_MHC_PREAPPLY_BWD_V2_QUEUE_END__
