set -Eeuo pipefail
echo __ROPE_INTERIM_16_17_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
printf %s IiIiU25hcHNob3Qgb25seSBmb3VyIGNvbXBsZXRlZCBSb1BFIGNhc2UgZGlyZWN0b3JpZXM7IG5ldmVyIHRvdWNoZXMgYWN0aXZlIGNhc2UuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cyxqc29uCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtuYW1lcz1bJzE2LXEnLCcxNi1rJywnMTctcScsJzE3LWsnXTtwcmVmaXg9J3VuaWZpZWQtZXh0cmE0X19yb3RhcnlfZW1iZWRkaW5nLScKc3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oJ2V4dHJhLXByb3h5LXJ1bnMnLCk7b3JpZz1tLnNjYW5fdW5pdHMKdW5pdHM9W3ggZm9yIHggaW4gb3JpZyhyKSBpZiB4WzFdIGluIHtwcmVmaXgrbiBmb3IgbiBpbiBuYW1lc31dO2Fzc2VydCBsZW4odW5pdHMpPT1sZW4obmFtZXMpCmZvciBfLGxhYmVsLHBhdGggaW4gdW5pdHM6CiBmb3VuZD1saXN0KHBhdGgucmdsb2IoJ2RldGFpbC9hdWRpdC1yZXN1bHQuanNvbicpKTthc3NlcnQgZm91bmQgYW5kIGFueShqc29uLmxvYWRzKGYucmVhZF90ZXh0KCkpWydzdGF0dXMnXT09J3Bhc3NlZCcgZm9yIGYgaW4gZm91bmQpLGxhYmVsCiBzdWJwcm9jZXNzLnJ1bihbc3lzLmV4ZWN1dGFibGUsJy1CJyxzdHIoci8nc2Nhbi1wdWJsaWMtYXJjaGl2ZS5weScpLHN0cihwYXRoKV0sY2hlY2s9VHJ1ZSkKbS5zY2FuX3VuaXRzPWxhbWJkYSByb290Oml0ZXIodW5pdHMpCmRlZiBub19zdXBwb3J0KHNvdXJjZSxvdXQpOgogcD1vdXQvJ3N1cHBvcnQuanNvbmwnO3Aud3JpdGVfYnl0ZXMoYicnKTtyZXR1cm4gMCxtLnNoYShwKQptLmNvcHlfc3VwcG9ydD1ub19zdXBwb3J0CnN5cy5hcmd2PVsnYXJjaGl2ZS1jYXB0dXJlcy5weScsJy0tcm9vdCcsc3RyKHIpLCctLW91dCcsJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktcm9wZS12Ny1pbnRlcmltLTE2cS0xN2snXTttLm1haW4oKQo= | base64 -d > "$r/archive-rope-v7-interim-16q-17k.py"
echo "4efe290d14795d3423018a27e9ad8ba38cfda5d809a86fa30a7f2ed86c676ddb  $r/archive-rope-v7-interim-16q-17k.py" | sha256sum -c -
test ! -e /workspace/expert-profile-backfill-20261109-rope-v7-interim-16q-17k;test ! -e "$r/rope-v7-interim-16q-17k.pid"
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-rope-v7-interim-16q-17k
 python3 -B "$r/archive-rope-v7-interim-16q-17k.py"
 python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/rope-v7-interim-16q-17k.tar.gz" "$(basename "$o")"
 sha256sum "$r/rope-v7-interim-16q-17k.tar.gz"
 echo INTERIM_ARCHIVE_READY
' > "$r/rope-v7-interim-16q-17k.log" 2>&1 < /dev/null &
echo "$!" > "$r/rope-v7-interim-16q-17k.pid";echo ARCHIVE_PID=$!
echo __ROPE_INTERIM_16_17_END__
