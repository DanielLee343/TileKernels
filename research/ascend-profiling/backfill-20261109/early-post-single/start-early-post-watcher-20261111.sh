set -Eeuo pipefail
echo __EARLY_POST_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-post-single-20261111-hidev-npu0";f="$r/snapshot-early-post-single-20261111.py";o=/workspace/expert-profile-backfill-20261109-early-post-single-20261111
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-post-single-20261111-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBwb3N0IGNhcHR1cmUgb3IgaXRzIHN0YW5kYWxvbmUgcHJlZmxpZ2h0IGZhaWx1cmUuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cyxzaHV0aWwKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO3E9ci8nZWFybHktcG9zdC1zaW5nbGUtMjAyNjExMTEtaGlkZXYtbnB1MCc7YXNzZXJ0IChxLydleGl0LnR4dCcpLmV4aXN0cygpCmlmIChxLydhdHRlbXB0LnR4dCcpLmV4aXN0cygpOgogZ3JvdXA9J2Vhcmx5LXBvc3Qtc2luZ2xlLXJ1bnMtMjAyNjExMTEnO2xhYmVsPSdtaGNfcG9zdF9id2Qtc3VwcC0wMSc7cGF0aD1yL2dyb3VwL2xhYmVsO3VuaXQ9cGF0aC8naGlkZXYtbnB1MCcvKHEvJ2F0dGVtcHQudHh0JykucmVhZF90ZXh0KCkuc3RyaXAoKTtldmlkZW5jZT11bml0LydxdWV1ZS1ldmlkZW5jZSc7YXNzZXJ0IG5vdCBldmlkZW5jZS5leGlzdHMoKTtldmlkZW5jZS5ta2RpcigpCiBmb3IgbiBpbiAoJ2V4aXQudHh0JywnY29uc29sZS5sb2cnLCdydW4uc2gnLCdhdHRlbXB0LnR4dCcpOnNodXRpbC5jb3B5MihxL24sZXZpZGVuY2UvbikKIGlmIChxLydwcmVmbGlnaHQnKS5pc19kaXIoKTpzaHV0aWwuY29weXRyZWUocS8ncHJlZmxpZ2h0JyxldmlkZW5jZS8ncHJlZmxpZ2h0JykKZWxzZTpncm91cD1xLm5hbWU7bGFiZWw9J3ByZWZsaWdodCc7cGF0aD1xCmFzc2VydCBwYXRoLmlzX2RpcigpO3NwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpO20uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKFsoZ3JvdXAsbGFiZWwscGF0aCldKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWVhcmx5LXBvc3Qtc2luZ2xlLTIwMjYxMTExJ107bS5tYWluKCkK' | base64 -d > "$f"
echo "6a9fbc8ddc26707bc51fd21d2de66b77c74c7abff7683ea630f12e5dcc6d171b  $f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-post-single-20261111-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-post-single-20261111;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-early-post-single-20261111.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-post-single-20261111.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-post-single-20261111.tar.gz";echo EARLY_POST_ARCHIVE_READY
' -- "$pid" > "$r/early-post-single-20261111-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-post-single-20261111-archive.pid";echo WATCHER_PID=$!
echo __EARLY_POST_WATCHER_END__
