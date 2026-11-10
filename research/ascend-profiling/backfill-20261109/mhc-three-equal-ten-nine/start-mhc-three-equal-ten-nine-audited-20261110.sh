set -Eeuo pipefail
echo __MHC_VARIANT_AUDITED_ARCHIVE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-three-equal-ten-nine-audited-20261110.py";o=/workspace/expert-profile-backfill-20261109-mhc-three-equal-ten-nine-audited-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/mhc-three-equal-ten-nine-audited-20261110.pid"
printf %s 'IiIiU25hcHNob3QgYXVkaXRlZCB0aHJlZS1sYXllciBlcXVhbC1wb3N0IGFuZCB0ZW4tbGF5ZXIgbmluZS1wb3N0IHJlcHJlc2VudGF0aXZlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO25hbWVzPVsnMDMnLCcxMCddO3ByZWZpeD0ndW5pZmllZC1leHRyYTVfX21oY19tdWx0aWxheWVyX3JlY29tcHV0ZS0nCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KCdleHRyYS1wcm94eS1ydW5zJywpO29yaWc9bS5zY2FuX3VuaXRzCnVuaXRzPVt4IGZvciB4IGluIG9yaWcocikgaWYgeFsxXSBpbiB7cHJlZml4K24gZm9yIG4gaW4gbmFtZXN9XTthc3NlcnQgbGVuKHVuaXRzKT09bGVuKG5hbWVzKQpmb3IgXyxsYWJlbCxwYXRoIGluIHVuaXRzOgogZm91bmQ9bGlzdChwYXRoLnJnbG9iKCdkZXRhaWwvYXVkaXQtcmVzdWx0Lmpzb24nKSk7YXNzZXJ0IGZvdW5kIGFuZCBhbnkoanNvbi5sb2FkcyhmLnJlYWRfdGV4dCgpKVsnc3RhdHVzJ109PSdwYXNzZWQnIGZvciBmIGluIGZvdW5kKSxsYWJlbAogc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LW1oYy10aHJlZS1lcXVhbC10ZW4tbmluZS1hdWRpdGVkLTIwMjYxMTEwJ107bS5tYWluKCkK' | base64 -d > "$f"
echo '8548059a9a5b53fd148ba4e6bae82fc673ab8249c3d1f6998e3743634af1fc43  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-mhc-three-equal-ten-nine-audited-20261110
 python3 -B "$r/snapshot-three-equal-ten-nine-audited-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/mhc-three-equal-ten-nine-audited-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/mhc-three-equal-ten-nine-audited-20261110.tar.gz";echo AUDITED_ARCHIVE_READY
' > "$r/mhc-three-equal-ten-nine-audited-20261110.log" 2>&1 < /dev/null &
echo "$!" > "$r/mhc-three-equal-ten-nine-audited-20261110.pid";echo ARCHIVE_PID=$!
echo __MHC_VARIANT_AUDITED_ARCHIVE_END__
