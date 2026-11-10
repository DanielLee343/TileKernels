set -Eeuo pipefail
echo __EARLY_SWIGLU_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-swiglu-single-20261110-hidev-npu0";f="$r/snapshot-early-swiglu-single-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-swiglu-single-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-swiglu-single-20261110-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBzd2lnbHUgc2luZ2xlLWNhbGwgcHJvYmUsIGluY2x1ZGluZyBmYWlsdXJlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtncm91cD0nZWFybHktc3dpZ2x1LXNpbmdsZS1ydW5zLTIwMjYxMTEwJztsYWJlbD0nc3dpZ2x1LXN1cHAtMDEnO3BhdGg9ci9ncm91cC9sYWJlbDthc3NlcnQgcGF0aC5pc19kaXIoKQpzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPShncm91cCwpCnN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKTttLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcihbKGdyb3VwLGxhYmVsLHBhdGgpXSkKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1lYXJseS1zd2lnbHUtc2luZ2xlLTIwMjYxMTEwJ107bS5tYWluKCkK' | base64 -d > "$f"
echo '2945242b0fb51e7ea5c3a6493615537e7ba9aeaa01b0e5da87f66180b939a825  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-swiglu-single-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-swiglu-single-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";test -f "$q/attempt.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/early-swiglu-single-runs-20261110/swiglu-supp-01/hidev-npu0/$attempt";test -d "$unit"
 cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-early-swiglu-single-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-swiglu-single-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-swiglu-single-20261110.tar.gz";echo EARLY_SWIGLU_ARCHIVE_READY
' -- "$pid" > "$r/early-swiglu-single-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-swiglu-single-20261110-archive.pid";echo WATCHER_PID=$!
echo __EARLY_SWIGLU_WATCHER_END__
