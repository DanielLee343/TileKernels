#!/usr/bin/env bash
set -Eeuo pipefail
echo __PRECISION_POST04_START_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-post04-smoke-hidev-npu0";o=/workspace/expert-profile-backfill-20261109-precision-post04-smoke-evidence
test ! -e "$q";test ! -e "$o";test ! -e "$r/precision-post04-smoke-archive.pid";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-post04-smoke-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra-mhc-variant-three-three-smoke-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export TARGET_ID=unified-extra2/mhc_post_bwd-04
base="$r/precision-proxy-runs/$TARGET_ID/hidev-npu0"
export ATTEMPT=$(python3 - "$base" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
mkdir -p "$base";test ! -e "$base/$ATTEMPT";mkdir "$base/$ATTEMPT"
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-precision-post04-app.sh"
python3 -B "$r/inspect-precision-post04-app.py" "$TARGET_ID" "$ATTEMPT"
python3 -B "$r/audit-precision-post04-bytes.py" mhc_post_bwd-04 "$ATTEMPT"
echo PRECISION_POST04_OBSERVATION_ONLY_HISTORICAL_CPU_REFERENCE_FAILED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q=$1;pid=$2
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/precision-proxy-runs/unified-extra2/mhc_post_bwd-04/hidev-npu0/$attempt"
 test -d "$unit";cp "$q/exit.txt" "$unit/queue-exit.txt";cp "$q/console.log" "$unit/queue-console.log";cp "$q/run.sh" "$unit/queue-run.sh"
 o=/workspace/expert-profile-backfill-20261109-precision-post04-smoke-evidence
 python3 -B "$r/snapshot-precision-post04-smoke.py";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/precision-post04-smoke-evidence.tar.gz" "$(basename "$o")"
 sha256sum "$r/precision-post04-smoke-evidence.tar.gz";echo AFTER_QUEUE_ARCHIVE_READY
' -- "$q" "$pid" > "$r/precision-post04-smoke-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/precision-post04-smoke-archive.pid";echo ARCHIVE_PID=$!
echo __PRECISION_POST04_START_END__
