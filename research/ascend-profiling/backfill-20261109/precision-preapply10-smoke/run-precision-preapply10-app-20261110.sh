#!/usr/bin/env bash
set -Eeo pipefail
root=/workspace/expert-profile-backfill-20261109-hidev;envdir=/workspace/tilekernels-env-20261101;repo="$envdir/src/TileKernels-private"
target="${TARGET_ID:?}";attempt="${ATTEMPT:?}";test "$target" = unified-extra4/mhc_pre_apply_mix_bwd-10
[[ "$target" =~ ^unified-extra[0-9]*/[A-Za-z0-9_.-]+$ && "$attempt" =~ ^attempt-[0-9]+$ ]] || exit 2
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh"
set -u
[[ "$(realpath "$ASCEND_HOME_PATH")" == *cann-9.2.1* ]]
export TILEKERNELS_ROOT="$repo" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$root/precision-preapply10-cache/$target"
export ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 MSOPT_LOG_LEVEL=0 GUARD_DEADLINE_SECONDS=900 GUARD_MAX_LOG_BYTES=536870912
exec 9> /workspace/.puma-hidev-npu0.lock;flock -n 9
test "$(git -C "$repo" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9
test -z "$(git -C "$repo" status --porcelain --untracked-files=no)"
out="$root/precision-proxy-runs/$target/hidev-npu0/$attempt/detail";test ! -e "$out";mkdir -p "$out/provenance"
python3 -B "$root/select-extra-proxy-case.py" "$root/precision-preapply10-cases.json" "$target" > "$out/provenance/selected.txt"
mapfile -t selected < "$out/provenance/selected.txt";test "${#selected[@]}" = 6
group=${selected[0]};adapter=${selected[1]};range=${selected[2]};kernel=${selected[3]};old="$repo/${selected[4]}";params=${selected[5]}
test "$group" = mhc_pre_apply_mix_bwd
test -f "$old";test -f "$root/extra-proxy-mhc-pre-apply-bwd-app-harness/$adapter"
echo "43b66f601ca77bf6b949c5e0e65a31622efaaa9caa85581089246ebe538e9e38  $old" | sha256sum -c -
old_result="$(dirname "$old")/capture-result.json"
echo "817168e5be4b04781ece79ae1847e7e633fa12f7b9b605d14f9d7c86211c36ad  $old_result" | sha256sum -c -
timeout 10 npu-smi info -t board -i 0 > "$out/provenance/board.txt";grep -qi '0000:8b:00.0' "$out/provenance/board.txt"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-before.txt"
msprof op --version > "$out/provenance/msprof-version.txt";grep -q 884ac969494a186a9c63ac45c4c39ad7289b3215 "$out/provenance/msprof-version.txt"
git -C "$repo" rev-parse HEAD > "$out/provenance/commit.txt";printf '%s\n' "$ASCEND_HOME_PATH" > "$out/provenance/cann-path.txt"
cp "$old" "$out/provenance/historical-capture-record.json"
cp "$old_result" "$out/provenance/historical-capture-result.json"
cp "$root/extra-proxy-mhc-pre-apply-bwd-app-harness/$adapter" "$root/precision-preapply10-cases.json" "$root/precision-preapply10-wrapper.py" "$root/extra-proxy-mhc-pre-apply-bwd-app-harness/provenance.json" "$root/extra-proxy-mhc-pre-apply-bwd-app-harness/replay-instrumentation.json" "$root/select-extra-proxy-case.py" "$root/guard-v7.py" "$root/run-precision-preapply10-app-20261110.sh" "$out/provenance/"
(cd "$out/provenance" && sha256sum *.py *.json *.sh *.txt > sha256.txt)
cd "$root";export GUARD_REQUIRE_PROFILE=1
python -B guard-v7.py 0 "$out" \
 msprof op "--output=$out/capture" --aic-metrics=MemoryDetail,Default --replay-mode=application \
 --mstx=true "--mstx-include=$range" "--kernel-name=$kernel" --launch-count=1 --warm-up=5 --kill=false \
 python -B "$root/precision-preapply10-wrapper.py" "$group" "$params" default "$out/application.json"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-after.txt"
compgen -G "$out/application-*.json" >/dev/null;compgen -G "$out/tensor-addresses-*.json" >/dev/null;compgen -G "$out/generated-kernel-*.cpp" >/dev/null
test -n "$(find "$out/capture" -name OpBasicInfo.csv -print -quit)";test -d "$TILELANG_CACHE_DIR"
find "$TILELANG_CACHE_DIR" -type f -exec sha256sum {} + | sort > "$out/cache-sha256.txt"
printf '%s\n' 'capture complete; identity, replay-state and address audits remain pending'
