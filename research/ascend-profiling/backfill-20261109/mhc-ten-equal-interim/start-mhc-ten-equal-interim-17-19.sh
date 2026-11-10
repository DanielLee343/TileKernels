set -Eeuo pipefail
echo __MHC_TEN_EQUAL_17_19_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-mhc-ten-equal-interim-17-19;f="$r/snapshot-mhc-ten-equal-interim-17-19.py"
test ! -e "$f";test ! -e "$o";test ! -e "$r/mhc-ten-equal-interim-17-19.pid"
printf %s IiIiU25hcHNob3QgY29tcGxldGVkIHRlbi1sYXllciBlcXVhbC1wb3N0IGNhc2VzLiIiIgppbXBvcnQgaW1wb3J0bGliLnV0aWwsc3VicHJvY2VzcyxzeXMsanNvbgpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7bmFtZXM9WycxNycsICcxOSddO3ByZWZpeD0ndW5pZmllZC1leHRyYTVfX21oY19tdWx0aWxheWVyX3JlY29tcHV0ZS0nCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KCdleHRyYS1wcm94eS1ydW5zJywpO29yaWc9bS5zY2FuX3VuaXRzCnVuaXRzPVt4IGZvciB4IGluIG9yaWcocikgaWYgeFsxXSBpbiB7cHJlZml4K24gZm9yIG4gaW4gbmFtZXN9XTthc3NlcnQgbGVuKHVuaXRzKT09bGVuKG5hbWVzKQpmb3IgXyxsYWJlbCxwYXRoIGluIHVuaXRzOgogZm91bmQ9bGlzdChwYXRoLnJnbG9iKCdkZXRhaWwvYXVkaXQtcmVzdWx0Lmpzb24nKSk7YXNzZXJ0IGZvdW5kIGFuZCBhbnkoanNvbi5sb2FkcyhmLnJlYWRfdGV4dCgpKVsnc3RhdHVzJ109PSdwYXNzZWQnIGZvciBmIGluIGZvdW5kKSxsYWJlbAogc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LW1oYy10ZW4tZXF1YWwtaW50ZXJpbS0xNy0xOSddO20ubWFpbigpCg== | base64 -d > "$f"
echo "2eaf33dc8e43e77788c2589a7a69890540eb5a47c18a03a15e27a14807d940f5  $f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-mhc-ten-equal-interim-17-19
 python3 -B "$r/snapshot-mhc-ten-equal-interim-17-19.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/mhc-ten-equal-interim-17-19.tar.gz" "$(basename "$o")"
 sha256sum "$r/mhc-ten-equal-interim-17-19.tar.gz";echo INTERIM_ARCHIVE_READY
' > "$r/mhc-ten-equal-interim-17-19.log" 2>&1 < /dev/null &
echo "$!" > "$r/mhc-ten-equal-interim-17-19.pid";echo ARCHIVE_PID=$!
echo __MHC_TEN_EQUAL_17_19_END__
