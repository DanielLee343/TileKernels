set -Eeuo pipefail
echo __PRECISION_BATCH_V2_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-preapply-batch-v2-20261110-hidev-npu0";f="$r/snapshot-precision-preapply-batch-v2-20261110.py";o=/workspace/expert-profile-backfill-20261109-precision-preapply-batch-v2-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/precision-preapply-batch-v2-20261110-archive.pid"
printf %s 'IiIiU25hcHNob3QgYWxsIGF0dGVtcHRlZCBwcmVjaXNpb24tbGFiZWxsZWQgcHJlLWFwcGx5IGNhc2VzLCBpbmNsdWRpbmcgZmFpbHVyZXMuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cwpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7Z3JvdXA9J3ByZWNpc2lvbi1wcm94eS1ydW5zJztzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPShncm91cCwpCmNhc2VzPVtmJ21oY19wcmVfYXBwbHlfbWl4X2J3ZC17aTowMmR9JyBmb3IgaSBpbiAoOSw2LDExLDEyLDE0LDE4LDIsNCldO3VuaXRzPVsoZ3JvdXAsJ3VuaWZpZWQtZXh0cmE0X18nK2Msci9ncm91cC8ndW5pZmllZC1leHRyYTQnL2MpIGZvciBjIGluIGNhc2VzIGlmIChyL2dyb3VwLyd1bmlmaWVkLWV4dHJhNCcvYykuaXNfZGlyKCldO2Fzc2VydCB1bml0cwpmb3IgXyxfLHBhdGggaW4gdW5pdHM6c3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LXByZWNpc2lvbi1wcmVhcHBseS1iYXRjaC12Mi0yMDI2MTExMCddO20ubWFpbigpCg==' | base64 -d > "$f"
echo 'c802d5295b998df419df6d07e12ad6b70dd6aeb9d780c150e030972008d7457b  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-preapply-batch-v2-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-precision-preapply-batch-v2-20261110;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-precision-preapply-batch-v2-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/precision-preapply-batch-v2-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/precision-preapply-batch-v2-20261110.tar.gz";echo PRECISION_BATCH_V2_ARCHIVE_READY
' -- "$pid" > "$r/precision-preapply-batch-v2-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/precision-preapply-batch-v2-20261110-archive.pid";echo WATCHER_PID=$!
echo __PRECISION_BATCH_V2_WATCHER_END__
