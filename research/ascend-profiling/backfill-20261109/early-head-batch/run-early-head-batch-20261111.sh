#!/usr/bin/env bash
set -Eeo pipefail
root=/workspace/expert-profile-backfill-20261109-hidev;envdir=/workspace/tilekernels-env-20261101;repo="$envdir/src/TileKernels-private";case_id="${CASE_ID:?}";[[ "$case_id" =~ ^head-fp32-(1001|1024)$ ]];h="$root/early-head-batch-harness-20261111/$case_id"
attempt="${ATTEMPT:?}";[[ "$attempt" =~ ^attempt-[0-9]+$ ]]
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh";set -u
[[ "$(realpath "$ASCEND_HOME_PATH")" == *cann-9.2.1* ]]
export TILEKERNELS_ROOT="$repo" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$root/early-head-batch-cache-20261111/$case_id" ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 MSOPT_LOG_LEVEL=0 GUARD_DEADLINE_SECONDS=900 GUARD_MAX_LOG_BYTES=536870912
exec 9> /workspace/.puma-hidev-npu0.lock;flock -n 9
test "$(git -C "$repo" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9
test -z "$(git -C "$repo" status --porcelain --untracked-files=no)"
out="$root/early-head-batch-runs-20261111/$case_id/hidev-npu0/$attempt/detail";test ! -e "$out";mkdir -p "$out/provenance"
timeout 10 npu-smi info -t board -i 0 > "$out/provenance/board.txt";grep -qi '0000:8b:00.0' "$out/provenance/board.txt"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-before.txt"
msprof op --version > "$out/provenance/msprof-version.txt";grep -q 884ac969494a186a9c63ac45c4c39ad7289b3215 "$out/provenance/msprof-version.txt"
git -C "$repo" rev-parse HEAD > "$out/provenance/commit.txt";printf '%s\n' "$ASCEND_HOME_PATH" > "$out/provenance/cann-path.txt"
cp "$h"/*.py "$h"/*.json "$h"/*.cpp "$root/guard-v7.py" "$root/run-early-head-batch-20261111.sh" "$out/provenance/"
(cd "$out/provenance" && sha256sum * > sha256.txt)
cd "$root";export GUARD_REQUIRE_PROFILE=1
python -B guard-v7.py 0 "$out" \
 msprof op "--output=$out/capture" --aic-metrics=MemoryDetail,Default --replay-mode=application \
 --mstx=true --mstx-include=cold_call --kernel-name=mhc_head_compute_mix_fwd_asc_kernel --launch-count=1 --warm-up=5 --kill=false \
 python -B "$h/early-head-app.py" "$out"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-after.txt"
compgen -G "$out/application-*.json" >/dev/null;compgen -G "$out/tensor-addresses-*.json" >/dev/null;compgen -G "$out/generated-kernel-*.cpp" >/dev/null
test -n "$(find "$out/capture" -name OpBasicInfo.csv -print -quit)";test -d "$TILELANG_CACHE_DIR"
find "$TILELANG_CACHE_DIR" -type f -exec sha256sum {} + | sort > "$out/cache-sha256.txt"
printf '%s\n' 'capture complete; identity, replay-state and address audits remain pending'
