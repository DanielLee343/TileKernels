set -Eeuo pipefail
echo __EARLY_SINKHORN_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-single-20261110-hidev-npu0";f="$r/snapshot-early-sinkhorn-single-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-sinkhorn-single-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-sinkhorn-single-20261110-archive.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBybXNub3JtIHNpbmdsZS1jYWxsIHByb2JlLCBpbmNsdWRpbmcgZmFpbHVyZXMuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cwpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7Z3JvdXA9J2Vhcmx5LXNpbmtob3JuLXNpbmdsZS1ydW5zLTIwMjYxMTEwJztsYWJlbD0nc2lua2hvcm4tY2Fubi0xJztwYXRoPXIvZ3JvdXAvbGFiZWw7YXNzZXJ0IHBhdGguaXNfZGlyKCkKc3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oZ3JvdXAsKQpzdWJwcm9jZXNzLnJ1bihbc3lzLmV4ZWN1dGFibGUsJy1CJyxzdHIoci8nc2Nhbi1wdWJsaWMtYXJjaGl2ZS5weScpLHN0cihwYXRoKV0sY2hlY2s9VHJ1ZSk7bS5zY2FuX3VuaXRzPWxhbWJkYSByb290Oml0ZXIoWyhncm91cCxsYWJlbCxwYXRoKV0pCmRlZiBub19zdXBwb3J0KHNvdXJjZSxvdXQpOgogcD1vdXQvJ3N1cHBvcnQuanNvbmwnO3Aud3JpdGVfYnl0ZXMoYicnKTtyZXR1cm4gMCxtLnNoYShwKQptLmNvcHlfc3VwcG9ydD1ub19zdXBwb3J0CnN5cy5hcmd2PVsnYXJjaGl2ZS1jYXB0dXJlcy5weScsJy0tcm9vdCcsc3RyKHIpLCctLW91dCcsJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktZWFybHktc2lua2hvcm4tc2luZ2xlLTIwMjYxMTEwJ107bS5tYWluKCkK' | base64 -d > "$f"
echo 'cb60bc6f54ebfe893bea7ea6bab799a06823311903974cadff76a99ca3b5469d  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-single-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-sinkhorn-single-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";test -f "$q/attempt.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/early-sinkhorn-single-runs-20261110/sinkhorn-cann-1/hidev-npu0/$attempt";test -d "$unit"
 cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-early-sinkhorn-single-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-sinkhorn-single-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-sinkhorn-single-20261110.tar.gz";echo EARLY_SINKHORN_ARCHIVE_READY
' -- "$pid" > "$r/early-sinkhorn-single-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-sinkhorn-single-20261110-archive.pid";echo WATCHER_PID=$!
echo __EARLY_SINKHORN_WATCHER_END__
