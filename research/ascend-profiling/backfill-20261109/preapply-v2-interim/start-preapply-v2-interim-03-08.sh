set -Eeuo pipefail
echo __PREAPPLY_INTERIM_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-preapply-v2-interim-03-08
printf %s IiIiU25hcHNob3Qgb25seSBmaXZlIGNvbXBsZXRlZCB0cmFuc3Bvc2UgY2FzZSBkaXJlY3RvcmllczsgbmV2ZXIgdG91Y2hlcyBhY3RpdmUgY2FzZS4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO25hbWVzPVsnMDMnLCcwNScsJzA3JywnMDgnXTtwcmVmaXg9J3VuaWZpZWQtZXh0cmE0X19taGNfcHJlX2FwcGx5X21peF9id2QtJwpzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPSgnZXh0cmEtcHJveHktcnVucycsKTtvcmlnPW0uc2Nhbl91bml0cwp1bml0cz1beCBmb3IgeCBpbiBvcmlnKHIpIGlmIHhbMV0gaW4ge3ByZWZpeCtuIGZvciBuIGluIG5hbWVzfV07YXNzZXJ0IGxlbih1bml0cyk9PWxlbihuYW1lcykKZm9yIF8sbGFiZWwscGF0aCBpbiB1bml0czoKIGZvdW5kPWxpc3QocGF0aC5yZ2xvYignZGV0YWlsL2F1ZGl0LXJlc3VsdC5qc29uJykpO2Fzc2VydCBmb3VuZCBhbmQgYW55KGpzb24ubG9hZHMoZi5yZWFkX3RleHQoKSlbJ3N0YXR1cyddPT0ncGFzc2VkJyBmb3IgZiBpbiBmb3VuZCksbGFiZWwKIHN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1wcmVhcHBseS12Mi1pbnRlcmltLTAzLTA4J107bS5tYWluKCkK | base64 -d > "$r/archive-mhc-preapply-v2-interim-03-08.py"
echo "0ad46f5a3fbd05a4d4ad310ffa4512ca53fe37cbff466594349c2a4f9dd61f92  $r/archive-mhc-preapply-v2-interim-03-08.py" | sha256sum -c -
test ! -e "$o";test ! -e "$r/preapply-v2-interim-03-08.pid"
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-preapply-v2-interim-03-08
 python3 -B "$r/archive-mhc-preapply-v2-interim-03-08.py"
 python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/preapply-v2-interim-03-08.tar.gz" "$(basename "$o")"
 sha256sum "$r/preapply-v2-interim-03-08.tar.gz";echo INTERIM_ARCHIVE_READY
' > "$r/preapply-v2-interim-03-08.log" 2>&1 < /dev/null &
echo "$!" > "$r/preapply-v2-interim-03-08.pid";echo ARCHIVE_PID=$!
echo __PREAPPLY_INTERIM_END__
