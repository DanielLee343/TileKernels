set -Eeuo pipefail
echo __SWIGLU_INTERIM_C218C3_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-swiglu-interim-c2-18-c3.py";o=/workspace/expert-profile-backfill-20261109-early-swiglu-interim-c2-18-c3
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-swiglu-interim-c2-18-c3.pid"
printf %s 'IiIiU25hcHNob3QgdGhyZWUgY29tcGxldGVkIGVhcmx5IFN3aUdMVSBjYXNlcyB3aGlsZSB0aGUgcXVldWUgcnVucy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1zd2lnbHUtYmF0Y2gtcnVucy0yMDI2MTExMCc7bmFtZXM9Wydzd2lnbHUtY2Fubi0yJywnc3dpZ2x1LXN1cHAtMTgnLCdzd2lnbHUtY2Fubi0zJ107c3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oZ3JvdXAsKQp1bml0cz1bKGdyb3VwLGMsci9ncm91cC9jKSBmb3IgYyBpbiBuYW1lc10KZm9yIF8sbGFiZWwscGF0aCBpbiB1bml0czoKIGZvdW5kPWxpc3QocGF0aC5yZ2xvYignZGV0YWlsL2F1ZGl0LXJlc3VsdC5qc29uJykpO2Fzc2VydCBmb3VuZCBhbmQgYW55KGpzb24ubG9hZHMoeC5yZWFkX3RleHQoKSlbJ3N0YXR1cyddPT0ncGFzc2VkJyBmb3IgeCBpbiBmb3VuZCksbGFiZWwKIHN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1lYXJseS1zd2lnbHUtaW50ZXJpbS1jMi0xOC1jMyddO20ubWFpbigpCg==' | base64 -d > "$f"
echo '14f237f09323283860ad78a2503be26ec9957bdc740f449109c075db339ab304  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-swiglu-interim-c2-18-c3
 python3 -B "$r/snapshot-early-swiglu-interim-c2-18-c3.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-swiglu-interim-c2-18-c3.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-swiglu-interim-c2-18-c3.tar.gz";echo SWIGLU_INTERIM_C218C3_READY
' > "$r/early-swiglu-interim-c2-18-c3.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-swiglu-interim-c2-18-c3.pid";echo ARCHIVE_PID=$!
echo __SWIGLU_INTERIM_C218C3_END__
