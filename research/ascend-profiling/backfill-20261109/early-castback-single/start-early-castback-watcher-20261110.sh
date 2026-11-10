set -Eeuo pipefail
echo __EARLY_CASTBACK_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-castback-single-20261110-hidev-npu0";f="$r/snapshot-early-castback-single-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-castback-single-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-castback-single-20261110-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBjYXN0YmFjayBzaW5nbGUtY2FsbCBwcm9iZSwgaW5jbHVkaW5nIGZhaWx1cmVzLiIiIgppbXBvcnQgaW1wb3J0bGliLnV0aWwsc3VicHJvY2VzcyxzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1jYXN0YmFjay1zaW5nbGUtcnVucy0yMDI2MTExMCc7bGFiZWw9J2Nhc3RiYWNrLW4xLWgxMjgtYmYxNic7cGF0aD1yL2dyb3VwL2xhYmVsO2Fzc2VydCBwYXRoLmlzX2RpcigpCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpO20uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKFsoZ3JvdXAsbGFiZWwscGF0aCldKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWVhcmx5LWNhc3RiYWNrLXNpbmdsZS0yMDI2MTExMCddO20ubWFpbigpCg==' | base64 -d > "$f"
echo '223e8d2b9b5a9805ddefc79a4c2c15ad8efb4ab88974df71d7278251e652908b  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-castback-single-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-castback-single-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";test -f "$q/attempt.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/early-castback-single-runs-20261110/castback-n1-h128-bf16/hidev-npu0/$attempt";test -d "$unit"
 cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-early-castback-single-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-castback-single-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-castback-single-20261110.tar.gz";echo EARLY_CASTBACK_ARCHIVE_READY
' -- "$pid" > "$r/early-castback-single-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-castback-single-20261110-archive.pid";echo WATCHER_PID=$!
echo __EARLY_CASTBACK_WATCHER_END__
