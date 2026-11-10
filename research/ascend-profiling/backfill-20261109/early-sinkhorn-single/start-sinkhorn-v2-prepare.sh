set -Eeuo pipefail
echo __SINKHORN_V2_PREPARE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-v2-prepare-20261110-hidev-npu0"
test ! -e "$q";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/early-sinkhorn-v2-prepare-20261110-hidev-npu0";envdir=/workspace/tilekernels-env-20261101
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh";set -u
export TILEKERNELS_ROOT="$envdir/src/TileKernels-private" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$r/early-sinkhorn-v2-cache-20261110" ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 GUARD_REQUIRE_PROFILE=0 GUARD_DEADLINE_SECONDS=900
exec 9> /workspace/.puma-hidev-npu0.lock;flock -n 9
test "$(git -C "$TILEKERNELS_ROOT" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9
test -z "$(git -C "$TILEKERNELS_ROOT" status --porcelain --untracked-files=no)"
"$envdir/venv/bin/python" -B "$r/guard-v7.py" 0 "$q/detail" "$envdir/venv/bin/python" -B "$r/early-sinkhorn-v2-harness-20261110/profile_case.py" --case-id sinkhorn-cann-1 --mode prepare --result "$q/detail/application.json"
"$envdir/venv/bin/python" -B - "$q/detail" <<'PY'
import glob,json,sys
files=glob.glob(sys.argv[1]+'/process-*/application.json');assert len(files)==1
x=json.load(open(files[0]));assert x['status']=='passed' and x['correctness']['status']=='passed',x
print('SINKHORN_V2_PREPARE_CORRECTNESS_PASSED')
PY
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __SINKHORN_V2_PREPARE_END__
