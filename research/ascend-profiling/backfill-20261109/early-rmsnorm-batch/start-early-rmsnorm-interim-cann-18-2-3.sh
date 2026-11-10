set -Eeuo pipefail
echo __RMSNORM_INTERIM_CANN1823_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-rmsnorm-interim-cann-18-2-3.py";o=/workspace/expert-profile-backfill-20261109-early-rmsnorm-interim-cann-18-2-3
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-rmsnorm-interim-cann-18-2-3.pid"
printf %s 'IiIiU25hcHNob3QgdGhyZWUgY29tcGxldGVkIGVhcmx5IFN3aUdMVSBjYXNlcyB3aGlsZSB0aGUgcXVldWUgcnVucy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1ybXNub3JtLWJhdGNoLXJ1bnMtMjAyNjExMTAnO25hbWVzPVsncm1zbm9ybS1jYW5uLTE4Jywncm1zbm9ybS1jYW5uLTInLCdybXNub3JtLWNhbm4tMyddO3NwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKdW5pdHM9Wyhncm91cCxjLHIvZ3JvdXAvYykgZm9yIGMgaW4gbmFtZXNdCmZvciBfLGxhYmVsLHBhdGggaW4gdW5pdHM6CiBmb3VuZD1saXN0KHBhdGgucmdsb2IoJ2RldGFpbC9hdWRpdC1yZXN1bHQuanNvbicpKTthc3NlcnQgZm91bmQgYW5kIGFueShqc29uLmxvYWRzKHgucmVhZF90ZXh0KCkpWydzdGF0dXMnXT09J3Bhc3NlZCcgZm9yIHggaW4gZm91bmQpLGxhYmVsCiBzdWJwcm9jZXNzLnJ1bihbc3lzLmV4ZWN1dGFibGUsJy1CJyxzdHIoci8nc2Nhbi1wdWJsaWMtYXJjaGl2ZS5weScpLHN0cihwYXRoKV0sY2hlY2s9VHJ1ZSkKbS5zY2FuX3VuaXRzPWxhbWJkYSByb290Oml0ZXIodW5pdHMpCmRlZiBub19zdXBwb3J0KHNvdXJjZSxvdXQpOgogcD1vdXQvJ3N1cHBvcnQuanNvbmwnO3Aud3JpdGVfYnl0ZXMoYicnKTtyZXR1cm4gMCxtLnNoYShwKQptLmNvcHlfc3VwcG9ydD1ub19zdXBwb3J0CnN5cy5hcmd2PVsnYXJjaGl2ZS1jYXB0dXJlcy5weScsJy0tcm9vdCcsc3RyKHIpLCctLW91dCcsJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktZWFybHktcm1zbm9ybS1pbnRlcmltLWNhbm4tMTgtMi0zJ107bS5tYWluKCkK' | base64 -d > "$f"
echo 'a3bac5259dbf9579eb17fdfe3a5517bf5b6d6ea8e4863dba7457cec790762373  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-rmsnorm-interim-cann-18-2-3
 python3 -B "$r/snapshot-early-rmsnorm-interim-cann-18-2-3.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-rmsnorm-interim-cann-18-2-3.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-rmsnorm-interim-cann-18-2-3.tar.gz";echo RMSNORM_INTERIM_CANN1823_READY
' > "$r/early-rmsnorm-interim-cann-18-2-3.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-rmsnorm-interim-cann-18-2-3.pid";echo ARCHIVE_PID=$!
echo __RMSNORM_INTERIM_CANN1823_END__
