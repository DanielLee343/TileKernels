set -Eeuo pipefail
echo __PREAPPLY_13_17_INTERIM_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-preapply-v2-interim-13-17
printf %s IiIiU25hcHNob3Qgb25seSB0aGUgZm91ciBsaXN0ZWQgY29tcGxldGVkIHByZS1hcHBseSBiYWNrd2FyZCBjYXNlIGRpcmVjdG9yaWVzLiIiIgppbXBvcnQgaW1wb3J0bGliLnV0aWwsc3VicHJvY2VzcyxzeXMsanNvbgpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7bmFtZXM9WycxMycsJzE1JywnMTYnLCcxNyddO3ByZWZpeD0ndW5pZmllZC1leHRyYTRfX21oY19wcmVfYXBwbHlfbWl4X2J3ZC0nCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KCdleHRyYS1wcm94eS1ydW5zJywpO29yaWc9bS5zY2FuX3VuaXRzCnVuaXRzPVt4IGZvciB4IGluIG9yaWcocikgaWYgeFsxXSBpbiB7cHJlZml4K24gZm9yIG4gaW4gbmFtZXN9XTthc3NlcnQgbGVuKHVuaXRzKT09bGVuKG5hbWVzKQpmb3IgXyxsYWJlbCxwYXRoIGluIHVuaXRzOgogZm91bmQ9bGlzdChwYXRoLnJnbG9iKCdkZXRhaWwvYXVkaXQtcmVzdWx0Lmpzb24nKSk7YXNzZXJ0IGZvdW5kIGFuZCBhbnkoanNvbi5sb2FkcyhmLnJlYWRfdGV4dCgpKVsnc3RhdHVzJ109PSdwYXNzZWQnIGZvciBmIGluIGZvdW5kKSxsYWJlbAogc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LXByZWFwcGx5LXYyLWludGVyaW0tMTMtMTcnXTttLm1haW4oKQo= | base64 -d > "$r/archive-mhc-preapply-v2-interim-13-17.py"
echo "376edaee7b32634242a826d50e8127e3852c03f849b64ab1f429922439da8871  $r/archive-mhc-preapply-v2-interim-13-17.py" | sha256sum -c -
test ! -e "$o";test ! -e "$r/preapply-v2-interim-13-17.pid"
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-preapply-v2-interim-13-17
 python3 -B "$r/archive-mhc-preapply-v2-interim-13-17.py"
 python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/preapply-v2-interim-13-17.tar.gz" "$(basename "$o")"
 sha256sum "$r/preapply-v2-interim-13-17.tar.gz";echo INTERIM_ARCHIVE_READY
' > "$r/preapply-v2-interim-13-17.log" 2>&1 < /dev/null &
echo "$!" > "$r/preapply-v2-interim-13-17.pid";echo ARCHIVE_PID=$!
echo __PREAPPLY_13_17_INTERIM_END__
