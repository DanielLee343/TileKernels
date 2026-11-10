set -Eeuo pipefail
echo __POST_INTERIM_61004_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-post-interim-cann6-supp10-04.py";o=/workspace/expert-profile-backfill-20261109-early-post-interim-cann6-supp10-04
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-post-interim-cann6-supp10-04.pid"
printf %s 'IiIiU25hcHNob3QgdGhyZWUgY29tcGxldGVkIGVhcmx5IFN3aUdMVSBjYXNlcyB3aGlsZSB0aGUgcXVldWUgcnVucy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1wb3N0LWJhdGNoLXJ1bnMtMjAyNjExMTEnO25hbWVzPVsnbWhjX3Bvc3RfYndkLWNhbm4tNicsJ21oY19wb3N0X2J3ZC1zdXBwLTEwJywnbWhjX3Bvc3RfYndkLXN1cHAtMDQnXTtzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPShncm91cCwpCnVuaXRzPVsoZ3JvdXAsYyxyL2dyb3VwL2MpIGZvciBjIGluIG5hbWVzXQpmb3IgXyxsYWJlbCxwYXRoIGluIHVuaXRzOgogZm91bmQ9bGlzdChwYXRoLnJnbG9iKCdkZXRhaWwvYXVkaXQtcmVzdWx0Lmpzb24nKSk7YXNzZXJ0IGZvdW5kIGFuZCBhbnkoanNvbi5sb2Fkcyh4LnJlYWRfdGV4dCgpKVsnc3RhdHVzJ109PSdwYXNzZWQnIGZvciB4IGluIGZvdW5kKSxsYWJlbAogc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWVhcmx5LXBvc3QtaW50ZXJpbS1jYW5uNi1zdXBwMTAtMDQnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo 'bb47e5885224e690a6c9ecad6de94e0fcbb91c7805590cfcd3859e74f04ab389  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-post-interim-cann6-supp10-04
 python3 -B "$r/snapshot-early-post-interim-cann6-supp10-04.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-post-interim-cann6-supp10-04.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-post-interim-cann6-supp10-04.tar.gz";echo POST_INTERIM_61004_READY
' > "$r/early-post-interim-cann6-supp10-04.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-post-interim-cann6-supp10-04.pid";echo ARCHIVE_PID=$!
echo __POST_INTERIM_61004_END__
