#!/usr/bin/env bash
set -Eeo pipefail
root=/workspace/expert-profile-backfill-20261109-hidev
dg=/workspace/deepgemm-ascend-20261107
case_id="${CASE_ID:?}";attempt="${ATTEMPT:?}"
[[ "$case_id" =~ ^paged[-_][a-z0-9_-]+$ ]] || exit 2
test "$case_id" = paged-sparse-fp8-q4-k256-h8-b8
target=paged_sparse_mqa_logits_impl
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG MSOPT_LOG_LEVEL
source "$dg/activate.sh"
set -u
test -d "$dg/cann-compat-quant"
export ASCEND_HOME_PATH="$dg/cann-compat-quant" BISHENG_HOME="$dg/cann-compat-quant"
export ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 GUARD_DEADLINE_SECONDS=900
export DG_JIT_CACHE_DIR="$root/deepgemm-cache/$case_id"
exec 9> /workspace/.puma-hidev-npu0.lock
flock -n 9
test "$(git -C "$dg/source" rev-parse HEAD)" = 3a35326271b069b8b5bf1a754435acd6cc91575b
test -z "$(git -C "$dg/source" status --porcelain --untracked-files=no)"
out="$root/deepgemm-runs/$case_id/hidev-npu0/$attempt"
test ! -e "$out";mkdir -p "$out/provenance"
timeout 10 npu-smi info -t board -i 0 > "$out/provenance/board.txt"
grep -qi '0000:8b:00.0' "$out/provenance/board.txt"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-before.txt"
msprof op --version > "$out/provenance/msprof-version.txt"
grep -q 884ac969494a186a9c63ac45c4c39ad7289b3215 "$out/provenance/msprof-version.txt"
git -C "$dg/source" rev-parse HEAD > "$out/provenance/commit.txt"
printf '%s\n' "$ASCEND_HOME_PATH" > "$out/provenance/cann-path.txt"
harness="$root/deepgemm-paged-reuse-address-harness/campaign-13/collect.py"
cp "$harness" "$out/provenance/frozen-collector.py"
cp "$root/deepgemm-paged-reuse-address-harness/campaign-13/cases.json" "$out/provenance/frozen-cases.json"
cp "$root/deepgemm-paged-reuse-address-harness/pilot-bf16/collect.py" "$out/provenance/frozen-base-collector.py"
cp "$root/deepgemm-paged-reuse-address-harness/replay-instrumentation.json" "$out/provenance/"
(cd "$out/provenance" && sha256sum *.py *.json *.txt > sha256.txt)
cd "$root"
export GUARD_REQUIRE_PROFILE=0
python -B guard-v6.py 0 "$out/prepare-monitor" \
 python -B "$harness" __worker "$case_id" prepare "$out/prepare.json" "$dg/source"
export GUARD_REQUIRE_PROFILE=1 MSOPT_LOG_LEVEL=0
python -B guard-v6.py 0 "$out/detail" \
 msprof op "--output=$out/detail/capture" --aic-metrics=MemoryDetail,Default --replay-mode=application \
 --mstx=true --mstx-include=dg_campaign_target "--kernel-name=*$target*" --launch-count=1 --warm-up=5 \
 python -B "$harness" __worker "$case_id" profile "$out/profile.json" "$dg/source"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-after.txt"
compgen -G "$out/profile-*.json" >/dev/null;compgen -G "$out/frozen-after-warmups-*.bin" >/dev/null;compgen -G "$out/frozen-addresses-*.json" >/dev/null
echo 'frozen collector replay captured; independent identity and byte audit pending'
