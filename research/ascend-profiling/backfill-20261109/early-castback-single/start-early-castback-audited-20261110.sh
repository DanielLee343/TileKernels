set -Eeuo pipefail
echo __EARLY_CASTBACK_AUDITED_ARCHIVE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-castback-audited-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-castback-audited-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-castback-audited-20261110.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBjYXN0YmFjayBzaW5nbGUtY2FsbCBwcm9iZSwgaW5jbHVkaW5nIGZhaWx1cmVzLiIiIgppbXBvcnQgaW1wb3J0bGliLnV0aWwsc3VicHJvY2VzcyxzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1jYXN0YmFjay1zaW5nbGUtcnVucy0yMDI2MTExMCc7bGFiZWw9J2Nhc3RiYWNrLW4xLWgxMjgtYmYxNic7cGF0aD1yL2dyb3VwL2xhYmVsO2Fzc2VydCBwYXRoLmlzX2RpcigpCnNwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKc3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpO20uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKFsoZ3JvdXAsbGFiZWwscGF0aCldKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWVhcmx5LWNhc3RiYWNrLWF1ZGl0ZWQtMjAyNjExMTAnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '7e06ffe83e27602194115ab9d03a401b1b48a715989bb8bdf9e7026565c8310a  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-castback-audited-20261110
 python3 -B "$r/snapshot-early-castback-audited-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-castback-audited-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-castback-audited-20261110.tar.gz";echo EARLY_AUDITED_ARCHIVE_READY
' > "$r/early-castback-audited-20261110.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-castback-audited-20261110.pid";echo ARCHIVE_PID=$!
echo __EARLY_CASTBACK_AUDITED_ARCHIVE_END__
