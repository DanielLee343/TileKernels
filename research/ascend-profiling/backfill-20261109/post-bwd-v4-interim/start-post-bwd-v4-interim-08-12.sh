set -Eeuo pipefail
echo __POST_BWD_08_12_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-post-bwd-v4-interim-08-12;f="$r/snapshot-post-bwd-v4-interim-08-12.py"
test ! -e "$f";test ! -e "$o";test ! -e "$r/post-bwd-v4-interim-08-12.pid"
printf %s IiIiU25hcHNob3QgbGlzdGVkIGNvbXBsZXRlZCBtSEMgcG9zdCBiYWNrd2FyZCBjYXNlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO25hbWVzPVsnMDgnLCAnMDknLCAnMTAnLCAnMTEnLCAnMTInXTtwcmVmaXg9J3VuaWZpZWQtZXh0cmEyX19taGNfcG9zdF9id2QtJwpzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPSgnZXh0cmEtcHJveHktcnVucycsKTtvcmlnPW0uc2Nhbl91bml0cwp1bml0cz1beCBmb3IgeCBpbiBvcmlnKHIpIGlmIHhbMV0gaW4ge3ByZWZpeCtuIGZvciBuIGluIG5hbWVzfV07YXNzZXJ0IGxlbih1bml0cyk9PWxlbihuYW1lcykKZm9yIF8sbGFiZWwscGF0aCBpbiB1bml0czoKIGZvdW5kPWxpc3QocGF0aC5yZ2xvYignZGV0YWlsL2F1ZGl0LXJlc3VsdC5qc29uJykpO2Fzc2VydCBmb3VuZCBhbmQgYW55KGpzb24ubG9hZHMoZi5yZWFkX3RleHQoKSlbJ3N0YXR1cyddPT0ncGFzc2VkJyBmb3IgZiBpbiBmb3VuZCksbGFiZWwKIHN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1wb3N0LWJ3ZC12NC1pbnRlcmltLTA4LTEyJ107bS5tYWluKCkK | base64 -d > "$f"
echo "0ff85ccbca62a4c33fde69a0ed560fdc77a37595de36bc914959ea5b121b4d64  $f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-post-bwd-v4-interim-08-12
 python3 -B "$r/snapshot-post-bwd-v4-interim-08-12.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/post-bwd-v4-interim-08-12.tar.gz" "$(basename "$o")"
 sha256sum "$r/post-bwd-v4-interim-08-12.tar.gz";echo INTERIM_ARCHIVE_READY
' > "$r/post-bwd-v4-interim-08-12.log" 2>&1 < /dev/null &
echo "$!" > "$r/post-bwd-v4-interim-08-12.pid";echo ARCHIVE_PID=$!
echo __POST_BWD_08_12_END__
