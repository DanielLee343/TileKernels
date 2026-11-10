set -Eeuo pipefail
echo __PRECISION_NORMALIZE_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-normalize03-20261110-hidev-npu0";f="$r/snapshot-precision-normalize03-20261110.py";o=/workspace/expert-profile-backfill-20261109-precision-normalize03-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/precision-normalize03-20261110-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBwcmVjaXNpb24tbGFiZWxsZWQgbm9ybWFsaXplMDMgcHJvYmUsIGluY2x1ZGluZyBmYWlsdXJlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtncm91cD0ncHJlY2lzaW9uLW5vcm1hbGl6ZTAzLXJ1bnMtMjAyNjExMTAnO2xhYmVsPSdub3JtYWxpemUtMDMnO3BhdGg9ci9ncm91cC9sYWJlbDthc3NlcnQgcGF0aC5pc19kaXIoKQpzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPShncm91cCwpCnN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKTttLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcihbKGdyb3VwLGxhYmVsLHBhdGgpXSkKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1wcmVjaXNpb24tbm9ybWFsaXplMDMtMjAyNjExMTAnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '38f221ba5e8857b1e7f6c1289c8f41cecd5b6f462d7fb9ef77b1d560d5d75a6b  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-normalize03-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-precision-normalize03-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";test -f "$q/attempt.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/precision-normalize03-runs-20261110/normalize-03/hidev-npu0/$attempt";test -d "$unit"
 cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-precision-normalize03-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/precision-normalize03-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/precision-normalize03-20261110.tar.gz";echo PRECISION_NORMALIZE_ARCHIVE_READY
' -- "$pid" > "$r/precision-normalize03-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/precision-normalize03-20261110-archive.pid";echo WATCHER_PID=$!
echo __PRECISION_NORMALIZE_WATCHER_END__
