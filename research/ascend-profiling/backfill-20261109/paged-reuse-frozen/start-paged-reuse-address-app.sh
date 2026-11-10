#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_PAGED_REUSE_ADDRESS_APP_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/deepgemm-paged-reuse-address-app-smoke-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/deepgemm-paged-reuse-address-app-smoke-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra-moe-forward-app-probe-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export CASE_ID=paged-sparse-fp8-q4-k256-h8-b8
export ATTEMPT=$(python3 - "$r/deepgemm-runs/$CASE_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-paged-reuse-address-app.sh"
echo PAGED_REUSE_ADDRESS_APP_CAPTURED_IDENTITY_PENDING
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "SMOKE_PID=$!"
echo __START_PAGED_REUSE_ADDRESS_APP_END__
