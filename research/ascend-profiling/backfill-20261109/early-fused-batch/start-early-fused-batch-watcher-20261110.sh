set -Eeuo pipefail
echo __EARLY_FUSED_BATCH_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-fused-batch-20261110-hidev-npu0";f="$r/snapshot-early-fused-batch-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-fused-batch-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-fused-batch-20261110-archive.pid"
printf %s 'IiIiU25hcHNob3QgYWxsIGF0dGVtcHRlZCBlYXJseSBmdXNlZCBjYXNlcywgaW5jbHVkaW5nIGZhaWx1cmVzLiIiIgppbXBvcnQgaW1wb3J0bGliLnV0aWwsc3VicHJvY2VzcyxzeXMKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1mdXNlZC1iYXRjaC1ydW5zLTIwMjYxMTEwJztzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPShncm91cCwpO29yaWc9bS5zY2FuX3VuaXRzCnVuaXRzPWxpc3Qob3JpZyhyKSk7YXNzZXJ0IHVuaXRzCmZvciBfLF8scGF0aCBpbiB1bml0czpzdWJwcm9jZXNzLnJ1bihbc3lzLmV4ZWN1dGFibGUsJy1CJyxzdHIoci8nc2Nhbi1wdWJsaWMtYXJjaGl2ZS5weScpLHN0cihwYXRoKV0sY2hlY2s9VHJ1ZSkKbS5zY2FuX3VuaXRzPWxhbWJkYSByb290Oml0ZXIodW5pdHMpCmRlZiBub19zdXBwb3J0KHNvdXJjZSxvdXQpOgogcD1vdXQvJ3N1cHBvcnQuanNvbmwnO3Aud3JpdGVfYnl0ZXMoYicnKTtyZXR1cm4gMCxtLnNoYShwKQptLmNvcHlfc3VwcG9ydD1ub19zdXBwb3J0CnN5cy5hcmd2PVsnYXJjaGl2ZS1jYXB0dXJlcy5weScsJy0tcm9vdCcsc3RyKHIpLCctLW91dCcsJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktZWFybHktZnVzZWQtYmF0Y2gtMjAyNjExMTAnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '17365030e0fb5c97000913d4525867aa40d316f29f79af64d420897113215257  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-fused-batch-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-fused-batch-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-early-fused-batch-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-fused-batch-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-fused-batch-20261110.tar.gz";echo EARLY_FUSED_BATCH_ARCHIVE_READY
' -- "$pid" > "$r/early-fused-batch-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-fused-batch-20261110-archive.pid";echo WATCHER_PID=$!
echo __EARLY_FUSED_BATCH_WATCHER_END__
