#!/usr/bin/env bash
set -Eeo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev
out="$r/moe-topk-original-store-20261111"
envdir=/workspace/tilekernels-env-20261101
repo="$envdir/src/TileKernels-private"
harness="$r/extra-proxy-moe-forward-app-probe-harness"
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh"
export PYTHONPATH="$repo" TILEKERNELS_ROOT="$repo" TILELANG_DEFAULT_TARGET=ascend
export ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1
exec 9>/workspace/.puma-hidev-npu0.lock
flock -w 600 9
[[ "$(git -C "$repo" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9 ]]
[[ -z "$(git -C "$repo" status --porcelain --untracked-files=no)" ]]
git -C "$repo" rev-parse HEAD > "$out/commit.txt"
npu-smi info -t proc-mem -i 0 > "$out/device-before.txt"
grep -q 'No process in device' "$out/device-before.txt"
for index in $(seq -w 1 20); do
    case_id="moe_topk_gate_forward-$index"
    target="unified-extra3/$case_id"
    case_out="$out/$case_id"
    mkdir "$case_out"
    python -B "$r/select-extra-proxy-case.py" "$harness/cases.json" "$target" > "$case_out/selected.txt"
    mapfile -t fields < "$case_out/selected.txt"
    test "${fields[0]}" = moe_topk_gate_forward
    export TILELANG_CACHE_DIR="$r/extra-proxy-cache/$target"
    if timeout 240 python -B "$harness/${fields[1]}" "${fields[0]}" "${fields[5]}" default "$case_out/application.json" > "$case_out/console.log" 2>&1; then
        echo "$case_id completed"
    else
        echo "$case_id failed, see console.log"
    fi
done
npu-smi info -t proc-mem -i 0 > "$out/device-after.txt"
