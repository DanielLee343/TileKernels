set -Eeuo pipefail
echo __EARLY_SWIGLU_AUDITED_ARCHIVE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;f="$r/snapshot-early-swiglu-audited-20261110.py";o=/workspace/expert-profile-backfill-20261109-early-swiglu-audited-20261110
test ! -e "$f";test ! -e "$o";test ! -e "$r/early-swiglu-audited-20261110.pid"
printf %s 'IiIiQXJjaGl2ZSBlYXJseSBzd2lnbHUgc2luZ2xlLWNhbGwgcHJvYmUsIGluY2x1ZGluZyBmYWlsdXJlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtncm91cD0nZWFybHktc3dpZ2x1LXNpbmdsZS1ydW5zLTIwMjYxMTEwJztsYWJlbD0nc3dpZ2x1LXN1cHAtMDEnO3BhdGg9ci9ncm91cC9sYWJlbDthc3NlcnQgcGF0aC5pc19kaXIoKQpzcGVjPWltcG9ydGxpYi51dGlsLnNwZWNfZnJvbV9maWxlX2xvY2F0aW9uKCdhcmNoaXZlX2NhcHR1cmVzJyxyLydhcmNoaXZlLWNhcHR1cmVzLnB5Jyk7bT1pbXBvcnRsaWIudXRpbC5tb2R1bGVfZnJvbV9zcGVjKHNwZWMpO3NwZWMubG9hZGVyLmV4ZWNfbW9kdWxlKG0pO20uR1JPVVBTPShncm91cCwpCnN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKTttLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcihbKGdyb3VwLGxhYmVsLHBhdGgpXSkKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1lYXJseS1zd2lnbHUtYXVkaXRlZC0yMDI2MTExMCddO20ubWFpbigpCg==' | base64 -d > "$f"
echo '778cff04a3909bb4244c703b14b25e989cecea1ff7dc767daad989d3a80865b4  '"$f" | sha256sum -c -
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;o=/workspace/expert-profile-backfill-20261109-early-swiglu-audited-20261110
 python3 -B "$r/snapshot-early-swiglu-audited-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/early-swiglu-audited-20261110.tar.gz" "$(basename "$o")"
 sha256sum "$r/early-swiglu-audited-20261110.tar.gz";echo EARLY_SWIGLU_AUDITED_ARCHIVE_READY
' > "$r/early-swiglu-audited-20261110.log" 2>&1 < /dev/null &
echo "$!" > "$r/early-swiglu-audited-20261110.pid";echo ARCHIVE_PID=$!
echo __EARLY_SWIGLU_AUDITED_ARCHIVE_END__
