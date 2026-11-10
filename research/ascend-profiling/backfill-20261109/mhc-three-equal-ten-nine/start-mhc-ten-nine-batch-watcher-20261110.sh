set -Eeuo pipefail
echo __TEN_NINE_BATCH_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten-nine-batch-20261110-hidev-npu0";f="$r/snapshot-mhc-ten-nine-batch-20261110.py";o=/workspace/expert-profile-backfill-20261109-mhc-ten-nine-batch-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/mhc-ten-nine-batch-20261110-archive.pid"
printf %s 'IiIiU25hcHNob3QgYXR0ZW1wdGVkIHRlbi1uaW5lIGJhdGNoIHRhcmdldHMsIGluY2x1ZGluZyBmYWlsdXJlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtuYW1lcz1bJzAzJywnMDUnLCcwOCcsJzEzJywnMTYnLCcxOCcsJzIwJ107cHJlZml4PSd1bmlmaWVkLWV4dHJhNV9fbWhjX211bHRpbGF5ZXJfcmVjb21wdXRlLScKc3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oJ2V4dHJhLXByb3h5LXJ1bnMnLCk7b3JpZz1tLnNjYW5fdW5pdHMKdW5pdHM9W3ggZm9yIHggaW4gb3JpZyhyKSBpZiB4WzFdIGluIHtwcmVmaXgrbiBmb3IgbiBpbiBuYW1lc31dO2Fzc2VydCB1bml0cwpmb3IgXyxsYWJlbCxwYXRoIGluIHVuaXRzOnN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1taGMtdGVuLW5pbmUtYmF0Y2gtMjAyNjExMTAnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '2f34826098ccd72a8a12216051df951b98fd8f052ead96eb549c4e06653f84e1  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten-nine-batch-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-mhc-ten-nine-batch-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-mhc-ten-nine-batch-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/mhc-ten-nine-batch-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/mhc-ten-nine-batch-20261110.tar.gz";echo BATCH_ARCHIVE_READY
' -- "$pid" > "$r/mhc-ten-nine-batch-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/mhc-ten-nine-batch-20261110-archive.pid";echo WATCHER_PID=$!
echo __TEN_NINE_BATCH_WATCHER_END__
