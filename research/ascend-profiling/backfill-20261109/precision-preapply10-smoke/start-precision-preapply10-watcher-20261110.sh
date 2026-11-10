set -Eeuo pipefail
echo __PRECISION_PREAPPLY_WATCHER_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-preapply10-20261110-hidev-npu0";f="$r/snapshot-precision-preapply10-20261110.py";o=/workspace/expert-profile-backfill-20261109-precision-preapply10-20261110-evidence
test ! -e "$f";test ! -e "$o";test ! -e "$r/precision-preapply10-20261110-archive.pid"
printf %s 'IiIiQXJjaGl2ZSB0aGUgcHJlY2lzaW9uLWxhYmVsbGVkIHByZWFwcGx5MTAgc21va2UsIGluY2x1ZGluZyBmYWlsdXJlcy4iIiIKaW1wb3J0IGltcG9ydGxpYi51dGlsLHN1YnByb2Nlc3Msc3lzCmZyb20gcGF0aGxpYiBpbXBvcnQgUGF0aApyPVBhdGgoJy93b3Jrc3BhY2UvZXhwZXJ0LXByb2ZpbGUtYmFja2ZpbGwtMjAyNjExMDktaGlkZXYnKTtwYXRoPXIvJ3ByZWNpc2lvbi1wcm94eS1ydW5zL3VuaWZpZWQtZXh0cmE0L21oY19wcmVfYXBwbHlfbWl4X2J3ZC0xMCc7YXNzZXJ0IHBhdGguaXNfZGlyKCkKc3BlYz1pbXBvcnRsaWIudXRpbC5zcGVjX2Zyb21fZmlsZV9sb2NhdGlvbignYXJjaGl2ZV9jYXB0dXJlcycsci8nYXJjaGl2ZS1jYXB0dXJlcy5weScpO209aW1wb3J0bGliLnV0aWwubW9kdWxlX2Zyb21fc3BlYyhzcGVjKTtzcGVjLmxvYWRlci5leGVjX21vZHVsZShtKTttLkdST1VQUz0oJ3ByZWNpc2lvbi1wcm94eS1ydW5zJywpCnN1YnByb2Nlc3MucnVuKFtzeXMuZXhlY3V0YWJsZSwnLUInLHN0cihyLydzY2FuLXB1YmxpYy1hcmNoaXZlLnB5Jyksc3RyKHBhdGgpXSxjaGVjaz1UcnVlKQptLnNjYW5fdW5pdHM9bGFtYmRhIHJvb3Q6aXRlcihbKCdwcmVjaXNpb24tcHJveHktcnVucycsJ3VuaWZpZWQtZXh0cmE0X19taGNfcHJlX2FwcGx5X21peF9id2QtMTAnLHBhdGgpXSkKZGVmIG5vX3N1cHBvcnQoc291cmNlLG91dCk6CiBwPW91dC8nc3VwcG9ydC5qc29ubCc7cC53cml0ZV9ieXRlcyhiJycpO3JldHVybiAwLG0uc2hhKHApCm0uY29weV9zdXBwb3J0PW5vX3N1cHBvcnQKc3lzLmFyZ3Y9WydhcmNoaXZlLWNhcHR1cmVzLnB5JywnLS1yb290JyxzdHIociksJy0tb3V0JywnL3dvcmtzcGFjZS9leHBlcnQtcHJvZmlsZS1iYWNrZmlsbC0yMDI2MTEwOS1wcmVjaXNpb24tcHJlYXBwbHkxMC0yMDI2MTExMC1ldmlkZW5jZSddO20ubWFpbigpCg==' | base64 -d > "$f"
echo '1923a63b1c2797ad39ad1d5502b2132b405a058f2b31f0bec4d5a0a73875a0c3  '"$f" | sha256sum -c -
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-preapply10-20261110-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-precision-preapply10-20261110-evidence;pid=$1
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";test -f "$q/attempt.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/precision-proxy-runs/unified-extra4/mhc_pre_apply_mix_bwd-10/hidev-npu0/$attempt";test -d "$unit"
 cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-precision-preapply10-20261110.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/precision-preapply10-20261110-evidence.tar.gz" "$(basename "$o")"
 sha256sum "$r/precision-preapply10-20261110-evidence.tar.gz";echo PRECISION_PREAPPLY_ARCHIVE_READY
' -- "$pid" > "$r/precision-preapply10-20261110-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/precision-preapply10-20261110-archive.pid";echo WATCHER_PID=$!
echo __PRECISION_PREAPPLY_WATCHER_END__
