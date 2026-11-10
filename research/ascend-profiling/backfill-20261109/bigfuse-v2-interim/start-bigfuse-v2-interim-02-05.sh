set -Eeuo pipefail
echo __BIGFUSE_02_05_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-bigfuse-v2-interim-02-05
printf %s IiIiU25hcHNob3QgdGhlIGxpc3RlZCBjb21wbGV0ZWQgYmlnLWZ1c2UgY2FzZSBkaXJlY3Rvcmllcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO25hbWVzPVsnMDInLCAnMDMnLCAnMDQnLCAnMDUnXTtwcmVmaXg9J3VuaWZpZWQtZXh0cmEzX19taGNfcHJlX2JpZ19mdXNlX2Z3ZC0nCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KCdleHRyYS1wcm94eS1ydW5zJywpO29yaWc9bS5zY2FuX3VuaXRzCnVuaXRzPVt4IGZvciB4IGluIG9yaWcocikgaWYgeFsxXSBpbiB7cHJlZml4K24gZm9yIG4gaW4gbmFtZXN9XTthc3NlcnQgbGVuKHVuaXRzKT09bGVuKG5hbWVzKQpmb3IgXyxsYWJlbCxwYXRoIGluIHVuaXRzOgogZm91bmQ9bGlzdChwYXRoLnJnbG9iKCdkZXRhaWwvYXVkaXQtcmVzdWx0Lmpzb24nKSk7YXNzZXJ0IGZvdW5kIGFuZCBhbnkoanNvbi5sb2FkcyhmLnJlYWRfdGV4dCgpKVsnc3RhdHVzJ109PSdwYXNzZWQnIGZvciBmIGluIGZvdW5kKSxsYWJlbAogc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWJpZ2Z1c2UtdjItaW50ZXJpbS0wMi0wNSddO20ubWFpbigpCg== | base64 -d > "$r/archive-bigfuse-v2-interim-02-05.py"
echo "9b2f30a115b15e2c1795815e17b1bce8d5d9444fd08c1a506af5f7d6558dcb63  $r/archive-bigfuse-v2-interim-02-05.py" | sha256sum -c -
test ! -e "$o";test ! -e "$r/bigfuse-v2-interim-02-05.pid"
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-bigfuse-v2-interim-02-05
 python3 -B "$r/archive-bigfuse-v2-interim-02-05.py"
 python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/bigfuse-v2-interim-02-05.tar.gz" "$(basename "$o")"
 sha256sum "$r/bigfuse-v2-interim-02-05.tar.gz";echo INTERIM_ARCHIVE_READY
' > "$r/bigfuse-v2-interim-02-05.log" 2>&1 < /dev/null &
echo "$!" > "$r/bigfuse-v2-interim-02-05.pid";echo ARCHIVE_PID=$!
echo __BIGFUSE_02_05_END__
