#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_PRESPLIT_FWD_V2_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/classic-presplit-fwd-v2-smoke-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/classic-presplit-fwd-v2-smoke-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra-mhc-presplit-bwd-v2-smoke-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export CASE_ID=presplit-fwd-01 CASE_BATCH=sixth KERNEL_NAME=mhc_pre_split_mixes_fwd_simd_mhc4_asc_kernel
export ATTEMPT=$(python3 - "$r/classic-runs/$CASE_BATCH/$CASE_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-presplit-app.sh"
export BACKFILL_ROOT="$r"
python3 -B "$r/inspect-presplit-fwd-app-v2.py" "$CASE_BATCH/$CASE_ID" "$ATTEMPT"
export BACKFILL_OBJDUMP=/workspace/tilekernels-env-20261101/cann/cann-9.2.1/tools/bisheng_compiler/bin/llvm-objdump
python3 -B "$r/audit-presplit-fwd-app-candidate.py" "$CASE_ID" "$ATTEMPT"
echo PRESPLIT_FWD_IDENTITY_CHECKED_ADDRESS_AUDIT_PENDING
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "SMOKE_PID=$!"
echo __START_PRESPLIT_FWD_V2_END__
