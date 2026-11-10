set -Eeuo pipefail
echo __PRECISION_PREAPPLY_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-preapply10-20261110-hidev-npu0"
test ! -e "$q";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-preapply10-20261110-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/mhc-ten-nine-batch-20261110-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
test -f "$prev/exit.txt"
export TARGET_ID=unified-extra4/mhc_pre_apply_mix_bwd-10
export ATTEMPT=$(python3 - "$r/precision-proxy-runs/$TARGET_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
base="$r/precision-proxy-runs/$TARGET_ID/hidev-npu0";mkdir -p "$base";test ! -e "$base/$ATTEMPT";mkdir "$base/$ATTEMPT"
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-precision-preapply10-app-20261110.sh"
python3 -B "$r/inspect-precision-preapply10-app.py" "$TARGET_ID" "$ATTEMPT"
python3 -B "$r/audit-precision-preapply10-bytes.py" mhc_pre_apply_mix_bwd-10 "$ATTEMPT"
echo PRECISION_PREAPPLY10_OBSERVATION_ONLY_HISTORICAL_CPU_REFERENCE_FAILED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
echo __PRECISION_PREAPPLY_QUEUE_END__
