#!/usr/bin/env bash
set -Eeo pipefail
root=/workspace/expert-profile-backfill-20261109-hidev
envdir=/workspace/tilekernels-env-20261101
repo="$envdir/src/TileKernels-private"
case_id="${CASE_ID:?}";batch="${CASE_BATCH:?}";attempt="${ATTEMPT:?}";kernel="${KERNEL_NAME:?}"
[[ "$case_id" =~ ^[a-z0-9-]+$ && "$batch" =~ ^(starter|second|third|fourth|fifth|sixth)$ && "$kernel" =~ ^[a-zA-Z0-9_]+$ ]] || exit 2
cd "$root"
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh"
set -u
[[ "$(realpath "$ASCEND_HOME_PATH")" == *cann-9.2.1* ]]
export TILEKERNELS_ROOT="$repo" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$root/hash-cache/$case_id"
export ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 MSOPT_LOG_LEVEL=0 COLLECTOR_BATCH="$batch"
exec 9> /workspace/.puma-hidev-npu0.lock
flock -n 9
test "$(git -C "$repo" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9
test -z "$(git -C "$repo" status --porcelain --untracked-files=no)"
mode="$root/hash-app-probe-runs/$batch/$case_id/hidev-npu0/$attempt/detail"
test ! -e "$mode";mkdir -p "$mode/provenance"
msprof op --version > "$mode/provenance/msprof-version.txt"
grep -q 884ac969494a186a9c63ac45c4c39ad7289b3215 "$mode/provenance/msprof-version.txt"
timeout 10 npu-smi info -t board -i 0 > "$mode/provenance/board.txt"
grep -qi '0000:8b:00.0' "$mode/provenance/board.txt"
timeout 10 npu-smi info -t health -i 0 > "$mode/provenance/health-before.txt"
git -C "$repo" rev-parse HEAD > "$mode/provenance/commit.txt"
printf '%s\n' "$ASCEND_HOME_PATH" > "$mode/provenance/cann-path.txt"
cp "$root/hash-app-probe-harness"/*.py "$root/hash-app-probe-harness"/*.json guard-v6.py run-hidev-hash-app-probe.sh "$mode/provenance/"
(cd "$mode/provenance" && sha256sum *.py *.json *.sh *.txt > sha256.txt)
export CAPTURE_DIR="$mode"
set +e
"$envdir/venv/bin/python" -B guard-v6.py 0 "$mode" \
 msprof op "--output=$mode/capture" --aic-metrics=MemoryDetail,Default --replay-mode=application \
 --mstx=true --mstx-include=cold_call "--kernel-name=$kernel" --launch-count=1 --warm-up=5 --kill=false \
 "$envdir/venv/bin/python" -B "$root/hash-app-probe-harness/application.py" --case "$case_id" --mode detail
rc=$?
set -e
timeout 10 npu-smi info -t health -i 0 > "$mode/provenance/health-after.txt" || exit 1
if [ "$rc" -eq 0 ];then find "$TILELANG_CACHE_DIR" -type f -exec sha256sum {} + | sort > "$mode/cache-sha256.txt";fi
exit "$rc"
