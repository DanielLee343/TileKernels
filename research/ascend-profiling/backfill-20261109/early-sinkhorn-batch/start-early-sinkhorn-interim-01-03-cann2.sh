set -Eeuo pipefail
echo __SINKHORN_INTERIM_0103CANN2_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-sinkhorn-interim-01-03-cann2.py";o=/workspace/expert-profile-backfill-20261109-early-sinkhorn-interim-01-03-cann2
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-sinkhorn-interim-01-03-cann2.pid"
printf %s 'IiIiU25hcHNob3QgdGhyZWUgY29tcGxldGVkIGVhcmx5IFN3aUdMVSBjYXNlcyB3aGlsZSB0aGUgcXVldWUgcnVucy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzLGpzb24KZnJvbSBwYXRobGliIGltcG9ydCBQYXRoCnI9UGF0aCgnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1oaWRldicpO2dyb3VwPSdlYXJseS1zaW5raG9ybi1iYXRjaC1ydW5zLTIwMjYxMTEwJztuYW1lcz1bJ3Npbmtob3JuLXN1cHAtMDEnLCdzaW5raG9ybi1zdXBwLTAzJywnc2lua2hvcm4tY2Fubi0yJ107c3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oZ3JvdXAsKQp1bml0cz1bKGdyb3VwLGMsci9ncm91cC9jKSBmb3IgYyBpbiBuYW1lc10KZm9yIF8sbGFiZWwscGF0aCBpbiB1bml0czoKIGZvdW5kPWxpc3QocGF0aC5yZ2xvYignZGV0YWlsL2F1ZGl0LXJlc3VsdC5qc29uJykpO2Fzc2VydCBmb3VuZCBhbmQgYW55KGpzb24ubG9hZHMoeC5yZWFkX3RleHQoKSlbJ3N0YXR1cyddPT0ncGFzc2VkJyBmb3IgeCBpbiBmb3VuZCksbGFiZWwKIHN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcih1bml0cykKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1lYXJseS1zaW5raG9ybi1pbnRlcmltLTAxLTAzLWNhbm4yJ107bS5tYWluKCkK' | base64 -d > "$f"
echo 'c621fd30365e1f5cb639ba05298a4b733fe85b90a9bfb1168dc31c26fbdfe47d  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-sinkhorn-interim-01-03-cann2
 python3 -B "$r/snapshot-early-sinkhorn-interim-01-03-cann2.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-sinkhorn-interim-01-03-cann2.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-sinkhorn-interim-01-03-cann2.tar.gz";echo SINKHORN_INTERIM_0103CANN2_READY
' > "$r/early-sinkhorn-interim-01-03-cann2.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-sinkhorn-interim-01-03-cann2.pid";echo ARCHIVE_PID=$!
echo __SINKHORN_INTERIM_0103CANN2_END__
