#!/usr/bin/env bash
set -Eeuo pipefail
echo __TEN04_RETRY_START_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten04-retry-smoke-hidev-npu0";which=mhc-ten04-retry;o="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
test ! -e "$q";test ! -e "$o";test ! -e "$r/$which-queue-archive.pid";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten04-retry-smoke-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/precision-post04-smoke-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export TARGET_ID=unified-extra5/mhc_multilayer_recompute-04
base="$r/extra-proxy-runs/$TARGET_ID/hidev-npu0"
export ATTEMPT=$(python3 - "$base" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
test ! -e "$base/$ATTEMPT";mkdir -p "$base/$ATTEMPT";printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-extra-mhc-multilayer-app.sh"
python3 -B "$r/inspect-mhc-multilayer-app.py" "$TARGET_ID" "$ATTEMPT"
python3 -B "$r/audit-mhc-multilayer-ten-equal-v2.py" mhc_multilayer_recompute-04 "$ATTEMPT"
python3 - "$base/$ATTEMPT/detail" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);s=p/'candidate-audit-ten-result.json';x=json.loads(s.read_text());assert x['target']=='unified-extra5/mhc_multilayer_recompute-04' and x['status']=='passed';out=p/'audit-result.json';assert not out.exists();out.write_bytes(s.read_bytes())
PY
echo TEN04_RETRY_ALL_CHECKS_PASSED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;q=$1;pid=$2;which=mhc-ten04-retry
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 test -f "$q/exit.txt";cat "$q/exit.txt";attempt=$(cat "$q/attempt.txt")
 unit="$r/extra-proxy-runs/unified-extra5/mhc_multilayer_recompute-04/hidev-npu0/$attempt"
 test -d "$unit";cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 o="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
 python3 -B "$r/snapshot-mhc-ten04-retry-20261110.py" "$which";python3 -B "$r/verify-archive.py" "$o"
 tar -C /workspace -czf "$r/$which-queue-snapshot-archive-bundle.tar.gz" "$(basename "$o")"
 sha256sum "$r/$which-queue-snapshot-archive-bundle.tar.gz";echo AFTER_QUEUE_ARCHIVE_READY
' -- "$q" "$pid" > "$r/$which-queue-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/$which-queue-archive.pid";echo ARCHIVE_PID=$!
echo __TEN04_RETRY_START_END__
