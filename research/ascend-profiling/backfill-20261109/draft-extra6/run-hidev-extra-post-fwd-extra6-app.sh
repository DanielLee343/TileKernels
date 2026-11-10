#!/usr/bin/env bash
set -Eeo pipefail
root=/workspace/expert-profile-backfill-20261109-hidev;envdir=/workspace/tilekernels-env-20261101;repo="$envdir/src/TileKernels-private"
target="${TARGET_ID:?}";attempt="${ATTEMPT:?}"
[[ "$target" =~ ^unified-extra[0-9]*/[A-Za-z0-9_.-]+$ && "$attempt" =~ ^attempt-[0-9]+$ ]] || exit 2
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh"
set -u
[[ "$(realpath "$ASCEND_HOME_PATH")" == *cann-9.2.1* ]]
export TILEKERNELS_ROOT="$repo" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$root/extra-proxy-cache/$target"
export ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 MSOPT_LOG_LEVEL=0 GUARD_DEADLINE_SECONDS=900 GUARD_MAX_LOG_BYTES=536870912
exec 9> /workspace/.puma-hidev-npu0.lock;flock -n 9
test "$(git -C "$repo" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9
test -z "$(git -C "$repo" status --porcelain --untracked-files=no)"
out="$root/extra-proxy-runs/$target/hidev-npu0/$attempt/detail";test ! -e "$out";mkdir -p "$out/provenance"
python3 -B "$root/select-extra-proxy-case.py" "$root/extra6-post-fwd-app-harness/cases.json" "$target" > "$out/provenance/selected.txt"
mapfile -t selected < "$out/provenance/selected.txt";test "${#selected[@]}" = 6
group=${selected[0]};adapter=${selected[1]};range=${selected[2]};kernel=${selected[3]};old="$repo/${selected[4]}";params=${selected[5]}
test "$group" = mhc_post_fwd
test -f "$old";test -f "$root/extra6-post-fwd-app-harness/$adapter"
timeout 10 npu-smi info -t board -i 0 > "$out/provenance/board.txt";grep -qi '0000:8b:00.0' "$out/provenance/board.txt"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-before.txt"
msprof op --version > "$out/provenance/msprof-version.txt";grep -q 884ac969494a186a9c63ac45c4c39ad7289b3215 "$out/provenance/msprof-version.txt"
git -C "$repo" rev-parse HEAD > "$out/provenance/commit.txt";printf '%s\n' "$ASCEND_HOME_PATH" > "$out/provenance/cann-path.txt"
cp "$old" "$out/provenance/historical-default.json"
cp "$root/extra6-post-fwd-app-harness/$adapter" "$root/extra6-post-fwd-app-harness/cases.json" "$root/extra6-post-fwd-app-harness/provenance.json" "$root/extra6-post-fwd-app-harness/replay-instrumentation.json" "$root/select-extra-proxy-case.py" "$root/guard-v6.py" "$root/run-hidev-extra-post-fwd-extra6-app.sh" "$out/provenance/"
(cd "$out/provenance" && sha256sum *.py *.json *.sh *.txt > sha256.txt)
cd "$root";export GUARD_REQUIRE_PROFILE=1
python -B guard-v6.py 0 "$out" \
 msprof op "--output=$out/capture" --aic-metrics=MemoryDetail,Default --replay-mode=application \
 --mstx=true "--mstx-include=$range" "--kernel-name=$kernel" --launch-count=1 --warm-up=5 --kill=false \
 python -B "$root/extra6-post-fwd-app-harness/$adapter" "$group" "$params" default "$out/application.json"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-after.txt"
compgen -G "$out/application-*.json" >/dev/null;compgen -G "$out/tensor-addresses-*.json" >/dev/null;compgen -G "$out/generated-kernel-*.cpp" >/dev/null
test -n "$(find "$out/capture" -name OpBasicInfo.csv -print -quit)";test -d "$TILELANG_CACHE_DIR"
find "$TILELANG_CACHE_DIR" -type f -exec sha256sum {} + | sort > "$out/cache-sha256.txt"
printf '%s\n' 'capture complete; identity, replay-state and address audits remain pending'
