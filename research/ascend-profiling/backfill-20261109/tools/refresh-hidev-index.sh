#!/usr/bin/env bash
set -e
printf '%s\n' __HIDEV_INDEX_REFRESH_BEGIN__
root=/workspace/expert-profile-backfill-20261109-hidev
python3 -B "$root/summarize-hidev.py"
gzip -n -c "$root/hidev-capture-index.json" > "$root/hidev-capture-index.json.gz"
python3 -B "$root/sweep-parser-health-v2.py" > "$root/parser-health-sweep.log"
sha256sum "$root/hidev-capture-index.json.gz" "$root/hidev-parser-health-sweep.json"
printf '%s\n' __HIDEV_INDEX_REFRESH_END__
