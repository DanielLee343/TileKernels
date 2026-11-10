#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_MHC_MULTILAYER_V2_AFTER_QUEUE_ARCHIVE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
for entry in 'mhc-multilayer-v2|extra-mhc-multilayer-v2-smoke-hidev-npu0';do
 IFS='|' read -r which name <<< "$entry";q="$r/$name";pid=$(cat "$q/pid");out="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
 test ! -e "$out";test ! -e "$r/$which-queue-archive.pid"
 nohup ionice -c 3 nice -n 15 bash -c '
  set -Eeuo pipefail
  r=/workspace/expert-profile-backfill-20261109-hidev;which=$1;q=$2;pid=$3
  while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
  out="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
  test -f "$q/exit.txt";cat "$q/exit.txt"
  python3 -B "$r/archive-after-app-queue-v18.py" "$which"
  python3 -B "$r/verify-archive.py" "$out"
  tar -C /workspace -czf "$r/$which-queue-snapshot-archive-bundle.tar.gz" "$(basename "$out")"
  sha256sum "$r/$which-queue-snapshot-archive-bundle.tar.gz"
  echo AFTER_QUEUE_ARCHIVE_READY
 ' -- "$which" "$q" "$pid" > "$r/$which-queue-archive.log" 2>&1 < /dev/null &
 echo "$!" > "$r/$which-queue-archive.pid";echo "$which ARCHIVE_PID=$!"
done
echo __START_MHC_MULTILAYER_V2_AFTER_QUEUE_ARCHIVE_END__
