#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_FINALIZE_EXTRA6_APP_SMOKE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra6-finalize-app-smoke-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra6-finalize-app-smoke-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/deepgemm-paged-reuse-frozen-inspection-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export TARGET_ID=unified-extra6/finalize-13-retry
export ATTEMPT=$(python3 - "$r/extra-proxy-runs/$TARGET_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-extra-finalize-extra6-app.sh"
python3 -B "$r/inspect-finalize-extra6-app.py" "$TARGET_ID" "$ATTEMPT"
echo FINALIZE_EXTRA6_IDENTIFIED_BYTE_AUDIT_PENDING
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "SMOKE_PID=$!"
echo __START_FINALIZE_EXTRA6_APP_SMOKE_END__
