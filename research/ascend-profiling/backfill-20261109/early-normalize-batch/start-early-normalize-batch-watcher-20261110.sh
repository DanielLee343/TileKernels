set -Eeuo pipefail
echo __EARLY_NORMALIZE_BATCH_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-normalize-batch-20261110-hidev-npu0";f="$r/snapshot-early-normalize-batch-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-normalize-batch-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-normalize-batch-20261110-archive.pid"
printf %s 'IiIiU25hcHNob3QgYWxsIGF0dGVtcHRlZCBlYXJseSBub3JtYWxpemUgY2FzZXMsIGluY2x1ZGluZyBmYWlsdXJlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtncm91cD0nZWFybHktbm9ybWFsaXplLWJhdGNoLXJ1bnMtMjAyNjExMTAnO3NwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCk7b3JpZz1tLnNjYW5fdW5pdHMKdW5pdHM9bGlzdChvcmlnKHIpKTthc3NlcnQgdW5pdHMKZm9yIF8sXyxwYXRoIGluIHVuaXRzOnN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1lYXJseS1ub3JtYWxpemUtYmF0Y2gtMjAyNjExMTAnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '054742d137a56ecc2d8618e3ecfcd7cb7e0b168f97e96bac2a0d429f62b1d178  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-normalize-batch-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-normalize-batch-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-early-normalize-batch-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-normalize-batch-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-normalize-batch-20261110.tar.gz";echo EARLY_NORMALIZE_BATCH_ARCHIVE_READY
' -- "$pid" > "$r/early-normalize-batch-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-normalize-batch-20261110-archive.pid";echo WATCHER_PID=$!
echo __EARLY_NORMALIZE_BATCH_WATCHER_END__
