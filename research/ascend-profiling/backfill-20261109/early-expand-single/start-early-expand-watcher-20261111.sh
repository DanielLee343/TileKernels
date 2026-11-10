set -Eeuo pipefail
echo __EARLY_EXPAND_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-expand-single-20261111-hidev-npu0";f="$r/snapshot-early-expand-single-20261111.py";o=/workspace/expert-profile-backfill-20261109-early-expand-single-20261111
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-expand-single-20261111-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBwb3N0IGNhcHR1cmUgb3IgaXRzIHN0YW5kYWxvbmUgcHJlZmxpZ2h0IGZhaWx1cmUuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cyxzaHV0aWwKZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO3E9ci8nZWFybHktZXhwYW5kLXNpbmdsZS0yMDI2MTExMS1oaWRldi1ucHUwJzthc3NlcnQgKHEvJ2V4aXQudHh0JykuZXhpc3RzKCkKaWYgKHEvJ2F0dGVtcHQudHh0JykuZXhpc3RzKCk6CiBncm91cD0nZWFybHktZXhwYW5kLXNpbmdsZS1ydW5zLTIwMjYxMTExJztsYWJlbD0nbWhjLWV4cGFuZC1md2QtYmYxNi1uNTEyLWg0MDk2LW00JztwYXRoPXIvZ3JvdXAvbGFiZWw7dW5pdD1wYXRoLydoaWRldi1ucHUwJy8ocS8nYXR0ZW1wdC50eHQnKS5yZWFkX3RleHQoKS5zdHJpcCgpO2V2aWRlbmNlPXVuaXQvJ3F1ZXVlLWV2aWRlbmNlJzthc3NlcnQgbm90IGV2aWRlbmNlLmV4aXN0cygpO2V2aWRlbmNlLm1rZGlyKCkKIGZvciBuIGluICgnZXhpdC50eHQnLCdjb25zb2xlLmxvZycsJ3J1bi5zaCcsJ2F0dGVtcHQudHh0Jyk6c2h1dGlsLmNvcHkyKHEvbixldmlkZW5jZS9uKQogaWYgKHEvJ3ByZWZsaWdodCcpLmlzX2RpcigpOnNodXRpbC5jb3B5dHJlZShxLydwcmVmbGlnaHQnLGV2aWRlbmNlLydwcmVmbGlnaHQnKQplbHNlOmdyb3VwPXEubmFtZTtsYWJlbD0ncHJlZmxpZ2h0JztwYXRoPXEKYXNzZXJ0IHBhdGguaXNfZGlyKCk7c3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oZ3JvdXAsKQpzdWJwcm9jZXNzLnJ1bihbc3lzLmV4ZWN1dGFibGUsJy1CJyxzdHIoci8nc2Nhbi1wdWJsaWMtYXJjaGl2ZS5weScpLHN0cihwYXRoKV0sY2hlY2s9VHJ1ZSk7bS5zY2FuX3VuaXRzPWxhbWJkYSByb290Oml0ZXIoWyhncm91cCxsYWJlbCxwYXRoKV0pCmRlZiBub19zdXBwb3J0KHNvdXJjZSxvdXQpOgogcD1vdXQvJ3N1cHBvcnQuanNvbmwnO3Aud3JpdGVfYnl0ZXMoYicnKTtyZXR1cm4gMCxtLnNoYShwKQptLmNvcHlfc3VwcG9ydD1ub19zdXBwb3J0CnN5cy5hcmd2PVsnYXJjaGl2ZS1jYXB0dXJlcy5weScsJy0tcm9vdCcsc3RyKHIpLCctLW91dCcsJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktZWFybHktZXhwYW5kLXNpbmdsZS0yMDI2MTExMSddO20ubWFpbigpCg==' | base64 -d > "$f"
echo "08c1b62e6c19f544dfc61e05978f58a060c9c92639eed382c26d55d480b353c5  $f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-expand-single-20261111-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-expand-single-20261111;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-early-expand-single-20261111.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-expand-single-20261111.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-expand-single-20261111.tar.gz";echo EARLY_EXPAND_ARCHIVE_READY
' -- "$pid" > "$r/early-expand-single-20261111-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-expand-single-20261111-archive.pid";echo WATCHER_PID=$!
echo __EARLY_EXPAND_WATCHER_END__
