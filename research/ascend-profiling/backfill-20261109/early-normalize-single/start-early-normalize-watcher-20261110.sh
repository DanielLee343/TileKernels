set -Eeuo pipefail
echo __EARLY_NORMALIZE_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-normalize-single-20261110-hidev-npu0";f="$r/snapshot-early-normalize-single-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-normalize-single-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-normalize-single-20261110-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBybXNub3JtIHNpbmdsZS1jYWxsIHByb2JlLCBpbmNsdWRpbmcgZmFpbHVyZXMuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cwpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7Z3JvdXA9J2Vhcmx5LW5vcm1hbGl6ZS1zaW5nbGUtcnVucy0yMDI2MTExMCc7bGFiZWw9J25vcm1hbGl6ZS1uMS1rOCc7cGF0aD1yL2dyb3VwL2xhYmVsO2Fzc2VydCBwYXRoLmlzX2RpcigpCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpO20uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKFsoZ3JvdXAsbGFiZWwscGF0aCldKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWVhcmx5LW5vcm1hbGl6ZS1zaW5nbGUtMjAyNjExMTAnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '2101d6e91b4c6dc8450d4cf302c5ab8f30c4c4b30bd80566cad5076ee6d8f6f4  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-normalize-single-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-normalize-single-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";test -f "$q/attempt.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/early-normalize-single-runs-20261110/normalize-n1-k8/hidev-npu0/$attempt";test -d "$unit"
 cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-early-normalize-single-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-normalize-single-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-normalize-single-20261110.tar.gz";echo EARLY_NORMALIZE_ARCHIVE_READY
' -- "$pid" > "$r/early-normalize-single-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-normalize-single-20261110-archive.pid";echo WATCHER_PID=$!
echo __EARLY_NORMALIZE_WATCHER_END__
