set -Eeuo pipefail
echo __EARLY_HEAD_V2_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-head-batch-v2-20261111-hidev-npu0";f="$r/snapshot-early-head-batch-v2-20261111.py";o=/workspace/expert-profile-backfill-20261109-early-head-batch-v2-20261111
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-head-batch-v2-20261111-archive.pid"
printf %s 'IiIiU25hcHNob3QgYWxsIGF0dGVtcHRlZCBlYXJseSBoZWFkIGNhc2VzLCBpbmNsdWRpbmcgZmFpbHVyZXMuIiIiCmltcG9ydCBpbXBvcnRsaWIudXRpbCxzdWJwcm9jZXNzLHN5cwpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7Z3JvdXA9J2Vhcmx5LWhlYWQtYmF0Y2gtcnVucy0yMDI2MTExMSc7c3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oZ3JvdXAsKTtvcmlnPW0uc2Nhbl91bml0cwp1bml0cz1saXN0KG9yaWcocikpO2Fzc2VydCB1bml0cwpmb3IgXyxfLHBhdGggaW4gdW5pdHM6c3VicHJvY2Vzcy5ydW4oW3N5cy5leGVjdXRhYmxlLCctQicsc3RyKHIvJ3NjYW4tcHVibGljLWFyY2hpdmUucHknKSxzdHIocGF0aCldLGNoZWNrPVRydWUpCm0uc2Nhbl91bml0cz1sYW1iZGEgcm9vdDppdGVyKHVuaXRzKQpkZWYgbm9fc3VwcG9ydChzb3VyY2Usb3V0KToKIHA9b3V0LydzdXBwb3J0Lmpzb25sJztwLndyaXRlX2J5dGVzKGInJyk7cmV0dXJuIDAsbS5zaGEocCkKbS5jb3B5X3N1cHBvcnQ9bm9fc3VwcG9ydApzeXMuYXJndj1bJ2FyY2hpdmUtY2FwdHVyZXMucHknLCctLXJvb3QnLHN0cihyKSwnLS1vdXQnLCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWVhcmx5LWhlYWQtYmF0Y2gtdjItMjAyNjExMTEnXTttLm1haW4oKQo=' | base64 -d > "$f"
echo '6ec328721d9f561e654f92af76c27f0ddf5549632e451f1c98f4d65408611992  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-head-batch-v2-20261111-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-early-head-batch-v2-20261111;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 python3 -B "$r/snapshot-early-head-batch-v2-20261111.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-head-batch-v2-20261111.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-head-batch-v2-20261111.tar.gz";echo EARLY_HEAD_V2_ARCHIVE_READY
' -- "$pid" > "$r/early-head-batch-v2-20261111-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-head-batch-v2-20261111-archive.pid";echo WATCHER_PID=$!
echo __EARLY_HEAD_V2_WATCHER_END__
