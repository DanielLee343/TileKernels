set -Eeuo pipefail
echo __SINKHORN_INTERIM_CANN151617_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-sinkhorn-interim-cann-15-16-17.py";o=/workspace/expert-profile-backfill-20261109-early-sinkhorn-interim-cann-15-16-17
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-sinkhorn-interim-cann-15-16-17.pid"
printf %s 'IiIiU25hcHNob3QgdGhyZWUgY29tcGxldGVkIGVhcmx5IFN3aUdMVSBjYXNlcyB3aGlsZSB0aGUgcXVldWUgcnVucy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1zaW5raG9ybi1iYXRjaC1ydW5zLTIwMjYxMTEwJztuYW1lcz1bJ3Npbmtob3JuLWNhbm4tMTUnLCdzaW5raG9ybi1jYW5uLTE2Jywnc2lua2hvcm4tY2Fubi0xNyddO3NwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKdW5pdHM9Wyhncm91cCxjLHIvZ3JvdXAvYykgZm9yIGMgaW4gbmFtZXNdCmZvciBfLGxhYmVsLHBhdGggaW4gdW5pdHM6CiBmb3VuZD1saXN0KHBhdGgucmdsb2IoJ2RldGFpbC9hdWRpdC1yZXN1bHQuanNvbicpKTthc3NlcnQgZm91bmQgYW5kIGFueShqc29uLmxvYWRzKHgucmVhZF90ZXh0KCkpWydzdGF0dXMnXT09J3Bhc3NlZCcgZm9yIHggaW4gZm91bmQpLGxhYmVsCiBzdWJwcm9jZXNzLnJ1bihbc3lzLmV4ZWN1dGFibGUsJy1CJyxzdHIoci8nc2Nhbi1wdWJsaWMtYXJjaGl2ZS5weScpLHN0cihwYXRoKV0sY2hlY2s9VHJ1ZSkKbS5zY2FuX3VuaXRzPWxhbWJkYSByb290Oml0ZXIodW5pdHMpCmRlZiBub19zdXBwb3J0KHNvdXJjZSxvdXQpOgogcD1vdXQvJ3N1cHBvcnQuanNvbmwnO3Aud3JpdGVfYnl0ZXMoYicnKTtyZXR1cm4gMCxtLnNoYShwKQptLmNvcHlfc3VwcG9ydD1ub19zdXBwb3J0CnN5cy5hcmd2PVsnYXJjaGl2ZS1jYXB0dXJlcy5weScsJy0tcm9vdCcsc3RyKHIpLCctLW91dCcsJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktZWFybHktc2lua2hvcm4taW50ZXJpbS1jYW5uLTE1LTE2LTE3J107bS5tYWluKCkK' | base64 -d > "$f"
echo 'a0c4a96e0ae46e6965120ac8309906c48cac7865f57c288aa4f2e471bd4ad237  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-sinkhorn-interim-cann-15-16-17
 python3 -B "$r/snapshot-early-sinkhorn-interim-cann-15-16-17.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-sinkhorn-interim-cann-15-16-17.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-sinkhorn-interim-cann-15-16-17.tar.gz";echo SINKHORN_INTERIM_CANN151617_READY
' > "$r/early-sinkhorn-interim-cann-15-16-17.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-sinkhorn-interim-cann-15-16-17.pid";echo ARCHIVE_PID=$!
echo __SINKHORN_INTERIM_CANN151617_END__
