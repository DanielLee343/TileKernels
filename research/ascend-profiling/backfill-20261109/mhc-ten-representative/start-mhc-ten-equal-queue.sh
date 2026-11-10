#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_MHC_TEN_EQUAL_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-mhc-multilayer-ten-equal-queue-hidev-npu0";which=mhc-ten-equal-v1;out="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
test ! -e "$q";test ! -e "$out";test ! -e "$r/$which-queue-archive.pid";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-mhc-multilayer-ten-equal-queue-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra-mhc-post-bwd-app-queue-v4-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
python3 -B "$r/queue-mhc-multilayer-ten-equal.py"
echo ALL_MHC_TEN_EQUAL_AUDITED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;which=$1;q=$2;pid=$3
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 out="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-mhc-ten-equal-v1.py" "$which"
 python3 -B "$r/verify-archive.py" "$out"
 tar -C /workspace -czf "$r/$which-queue-snapshot-archive-bundle.tar.gz" "$(basename "$out")"
 sha256sum "$r/$which-queue-snapshot-archive-bundle.tar.gz";echo AFTER_QUEUE_ARCHIVE_READY
' -- "$which" "$q" "$pid" > "$r/$which-queue-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/$which-queue-archive.pid";echo ARCHIVE_PID=$!
echo __START_MHC_TEN_EQUAL_END__
