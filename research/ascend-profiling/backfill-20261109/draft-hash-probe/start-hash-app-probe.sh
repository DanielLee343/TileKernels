#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_HASH_APP_PROBE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/hash-app-probe-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/hash-app-probe-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra6-post-fwd-app-queue-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export CASE_ID=hash-15 CASE_BATCH=starter KERNEL_NAME=engram_hash_kernel_asc_kernel
export ATTEMPT=$(python3 - "$r/hash-app-probe-runs/starter/hash-15/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-hash-app-probe.sh"
python3 -B "$r/inspect-hash-app-probe.py" "$ATTEMPT"
echo HASH_APP_PROBE_INSPECTED_NO_AUTO_ADMISSION
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "PROBE_PID=$!"
echo __START_HASH_APP_PROBE_END__
