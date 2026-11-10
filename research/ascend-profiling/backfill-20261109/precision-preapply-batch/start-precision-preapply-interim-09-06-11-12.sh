set -Eeuo pipefail
echo __PRECISION_INTERIM_ARCHIVE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-precision-preapply-interim-09-06-11-12.py";o=/workspace/expert-profile-backfill-20261109-precision-preapply-interim-09-06-11-12
test ! -e "$f";test ! -e "$o";test ! -e "$r/precision-preapply-interim-09-06-11-12.pid"
printf %s 'IiIiU25hcHNob3QgY29tcGxldGVkIHByZWNpc2lvbi1sYWJlbGxlZCBjYXNlcyBhbmQgaW5pdGlhbCAwOSBmYWlsdXJlLiIiIgppbXBvcnQgaW1wb3J0bGliLnV0aWwsc3VicHJvY2VzcyxzeXMsanNvbgpmcm9tIHBhdGhsaWIgaW1wb3J0IFBhdGgKcj1QYXRoKCcvd29ya3NwYWNlL2V4cGVydC1wcm9maWxlLWJhY2tmaWxsLTIwMjYxMTA5LWhpZGV2Jyk7Z3JvdXA9J3ByZWNpc2lvbi1wcm94eS1ydW5zJztuYW1lcz1bZidtaGNfcHJlX2FwcGx5X21peF9id2Qte2k6MDJkfScgZm9yIGkgaW4gKDksNiwxMSwxMildO3NwZWM9aW1wb3J0bGliLnV0aWwuc3BlY19mcm9tX2ZpbGVfbG9jYXRpb24oJ2FyY2hpdmVfY2FwdHVyZXMnLHIvJ2FyY2hpdmUtY2FwdHVyZXMucHknKTttPWltcG9ydGxpYi51dGlsLm1vZHVsZV9mcm9tX3NwZWMoc3BlYyk7c3BlYy5sb2FkZXIuZXhlY19tb2R1bGUobSk7bS5HUk9VUFM9KGdyb3VwLCkKdW5pdHM9Wyhncm91cCwndW5pZmllZC1leHRyYTRfXycrYyxyL2dyb3VwLyd1bmlmaWVkLWV4dHJhNCcvYykgZm9yIGMgaW4gbmFtZXNdCmZvciBfLGxhYmVsLHBhdGggaW4gdW5pdHM6CiBmb3VuZD1saXN0KHBhdGgucmdsb2IoJ2RldGFpbC9wcmVjaXNpb24tcHJlYXBwbHktYmF0Y2gtYnl0ZS1vYnNlcnZhdGlvbi12Mi5qc29uJykpO2Fzc2VydCBmb3VuZCBhbmQgYW55KGpzb24ubG9hZHMoeC5yZWFkX3RleHQoKSlbJ3N0YXR1cyddPT0ncHJlY2lzaW9uX2xhYmVsbGVkX2J5dGVzX29ic2VydmVkJyBmb3IgeCBpbiBmb3VuZCksbGFiZWwKIHN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1wcmVjaXNpb24tcHJlYXBwbHktaW50ZXJpbS0wOS0wNi0xMS0xMiddO20ubWFpbigpCg==' | base64 -d > "$f"
echo 'bfbf7fab3224079e165f4cd36b6e814229da4f898904e8471e3fa28705815048  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-precision-preapply-interim-09-06-11-12
 python3 -B "$r/snapshot-precision-preapply-interim-09-06-11-12.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/precision-preapply-interim-09-06-11-12.tar.gz" "$(basename "$o")"
 sha256sum "$r/precision-preapply-interim-09-06-11-12.tar.gz";echo PRECISION_INTERIM_ARCHIVE_READY
' > "$r/precision-preapply-interim-09-06-11-12.log" 2>&1 < /dev/null &
echo "$!" > "$r/precision-preapply-interim-09-06-11-12.pid";echo ARCHIVE_PID=$!
echo __PRECISION_INTERIM_ARCHIVE_END__
