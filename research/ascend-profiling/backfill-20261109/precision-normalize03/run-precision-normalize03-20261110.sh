#!/usr/bin/env bash
set -Eeo pipefail
root=/workspace/expert-profile-backfill-20261109-hidev;envdir=/workspace/tilekernels-env-20261101;repo="$envdir/src/TileKernels-private";h="$root/precision-normalize03-harness-20261110"
attempt="${ATTEMPT:?}";[[ "$attempt" =~ ^attempt-[0-9]+$ ]]
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD MEMORYCHART_ROOT MEMORYCHART_LOG
source "$envdir/activate.sh";set -u
[[ "$(realpath "$ASCEND_HOME_PATH")" == *cann-9.2.1* ]]
export TILEKERNELS_ROOT="$repo" TILELANG_DEFAULT_TARGET=ascend TILELANG_CACHE_DIR="$root/precision-normalize03-cache-20261110" ASCEND_RT_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 MSOPT_LOG_LEVEL=0 GUARD_DEADLINE_SECONDS=900 GUARD_MAX_LOG_BYTES=536870912 COLLECTOR_BATCH=starter
exec 9> /workspace/.puma-hidev-npu0.lock;flock -n 9
test "$(git -C "$repo" rev-parse HEAD)" = bb866a442c59464902dc2e93916ceea82e7471d9;test -z "$(git -C "$repo" status --porcelain --untracked-files=no)"
out="$root/precision-normalize03-runs-20261110/normalize-03/hidev-npu0/$attempt/detail";test ! -e "$out";mkdir -p "$out/provenance"
old="$repo/research/ascend-profiling/reviews/20261107-finalize/capture-evidence/cases/normalize-03/capture-record.json";res="$(dirname "$old")/capture-result.json"
python3 - "$h/history.json" "$old" "$res" <<'PY'
import hashlib,json,sys
from pathlib import Path
v=json.loads(Path(sys.argv[1]).read_text())
for f,key in ((sys.argv[2],'capture_record_sha256'),(sys.argv[3],'capture_result_sha256')):assert hashlib.sha256(Path(f).read_bytes()).hexdigest()==v[key]
a=json.loads(Path(sys.argv[2]).read_text());assert a['reference_check']=='failed';print('HISTORICAL_PRECISION_FAILURE_AND_HASHES_VERIFIED')
PY
timeout 10 npu-smi info -t board -i 0 > "$out/provenance/board.txt";grep -qi '0000:8b:00.0' "$out/provenance/board.txt"
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-before.txt"
msprof op --version > "$out/provenance/msprof-version.txt";grep -q 884ac969494a186a9c63ac45c4c39ad7289b3215 "$out/provenance/msprof-version.txt"
git -C "$repo" rev-parse HEAD > "$out/provenance/commit.txt";printf '%s\n' "$ASCEND_HOME_PATH" > "$out/provenance/cann-path.txt"
cp "$old" "$out/provenance/historical-capture-record.json";cp "$res" "$out/provenance/historical-capture-result.json"
cp "$h"/*.py "$h"/*.json "$root/guard-v7.py" "$root/run-precision-normalize03-20261110.sh" "$out/provenance/"
(cd "$out/provenance" && sha256sum * > sha256.txt)
cd "$root";export GUARD_REQUIRE_PROFILE=1 CAPTURE_DIR="$out"
python -B guard-v7.py 0 "$out" \
 msprof op "--output=$out/capture" --aic-metrics=MemoryDetail,Default --replay-mode=application \
 --mstx=true --mstx-include=cold_call --kernel-name=normalize_weight_kernel_kernel --launch-count=1 --warm-up=5 --kill=false \
 python -B "$h/application.py" --case normalize-03 --mode detail
timeout 10 npu-smi info -t health -i 0 > "$out/provenance/health-after.txt"
compgen -G "$out/metadata-*/application.json" >/dev/null;test -n "$(find "$out/capture" -name OpBasicInfo.csv -print -quit)";test -d "$TILELANG_CACHE_DIR"
find "$TILELANG_CACHE_DIR" -type f -exec sha256sum {} + | sort > "$out/cache-sha256.txt"
printf '%s\n' 'precision-labelled capture complete; identity and byte audits remain pending'
