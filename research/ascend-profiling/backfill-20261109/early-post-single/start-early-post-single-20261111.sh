set -Eeuo pipefail
echo __EARLY_POST_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-post-single-20261111-hidev-npu0"
test ! -e "$q";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-post-single-20261111-hidev-npu0";envdir=/workspace/tilekernels-env-20261101
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/early-normalize-batch-20261110-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
test -f "$prev/exit.txt"
(
 unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
 source "$envdir/activate.sh";set -u
 export TILEKERNELS_ROOT="$envdir/src/TileKernels-private" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$r/early-post-preflight-cache-20261111" ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 GUARD_REQUIRE_PROFILE=0 GUARD_DEADLINE_SECONDS=900
 exec 9> /workspace/.puma-hidev-npu0.lock;flock -n 9
 test "$(git -C "$TILEKERNELS_ROOT" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9
 test -z "$(git -C "$TILEKERNELS_ROOT" status --porcelain --untracked-files=no)"
 "$envdir/venv/bin/python" -B "$r/guard-v7.py" 0 "$q/preflight" "$envdir/venv/bin/python" -B "$r/early-post-single-harness-20261111/profile_case.py" --case-id mhc_post_bwd-supp-01 --mode prepare --result "$q/preflight/application.json"
 "$envdir/venv/bin/python" -B - "$q/preflight" <<'PY'
import glob,json,sys
files=glob.glob(sys.argv[1]+'/process-*/application.json');assert len(files)==1
x=json.load(open(files[0]));assert x['status']=='passed' and x['correctness']['status']=='passed',x
print('EARLY_POST_PREFLIGHT_CORRECTNESS_PASSED')
PY
)
export ATTEMPT=attempt-001
base="$r/early-post-single-runs-20261111/mhc_post_bwd-supp-01/hidev-npu0";mkdir -p "$base";test ! -e "$base/$ATTEMPT";mkdir "$base/$ATTEMPT"
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-early-post-single-20261111.sh"
python3 -B "$r/inspect-early-post-single-20261111.py" "$ATTEMPT"
python3 -B "$r/audit-early-post-single-20261111.py" "$ATTEMPT"
bash "$r/test-early-post-audit-20261111.sh" > "$r/early-post-audit-test-20261111.log" 2>&1
bash "$r/promote-early-post-20261111.sh"
echo EARLY_POST_AUDITED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __EARLY_POST_QUEUE_END__
