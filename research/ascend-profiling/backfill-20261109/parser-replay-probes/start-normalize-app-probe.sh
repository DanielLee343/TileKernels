#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_NORMALIZE_APP_PROBE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/classic-normalize-app-probe-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/classic-normalize-app-probe-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra-randn-app-probe-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export CASE_ID=normalize-04 CASE_BATCH=starter KERNEL_NAME=normalize_weight_kernel_kernel
export ATTEMPT=$(python3 - "$r/classic-runs/$CASE_BATCH/$CASE_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-normalize-app-probe.sh"
export BACKFILL_ROOT="$r"
python3 -B "$r/inspect-normalize-app-probe.py" "$CASE_BATCH/$CASE_ID" "$ATTEMPT"
echo NORMALIZE_APP_IDENTITY_CHECKED_ADDRESS_AUDIT_PENDING
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "SMOKE_PID=$!"
echo __START_NORMALIZE_APP_PROBE_END__
