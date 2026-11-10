#!/usr/bin/env bash
set -Eeuo pipefail
echo __MHC_RETRY_TEN_NINE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten-nine-retry-smoke-hidev-npu0";which=mhc-ten-nine-retry;out="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
test ! -e "$q";test ! -e "$out";test ! -e "$r/$which-queue-archive.pid";mkdir "$q"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/mhc-ten-nine-retry-smoke-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/mhc-three-three-retry-smoke-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
export TARGET_ID=unified-extra5/mhc_multilayer_recompute-03
export ATTEMPT=$(python3 - "$r/extra-proxy-runs/$TARGET_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
p=Path(sys.argv[1]);ids=[int(x.name[8:]) for x in p.glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
base="$r/extra-proxy-runs/$TARGET_ID/hidev-npu0";mkdir -p "$base";test ! -e "$base/$ATTEMPT";mkdir "$base/$ATTEMPT"
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-mhc-multilayer-guard7-20261110.sh"
python3 -B "$r/inspect-mhc-multilayer-app.py" "$TARGET_ID" "$ATTEMPT"
echo MHC_VARIANT_CAPTURE_IDENTITY_ONLY_BYTE_AUDIT_PENDING
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo QUEUE_PID=$!
pid=$(cat "$q/pid")
nohup ionice -c 3 nice -n 15 bash -c '
 set -Eeuo pipefail
 r=/workspace/expert-profile-backfill-20261109-hidev;which=$1;q=$2;pid=$3
 while ps -p "$pid" -o args= | grep -Fq "$q/run.sh";do sleep 10;done
 out="/workspace/expert-profile-backfill-20261109-$which-queue-snapshot-archive"
 test -f "$q/exit.txt";cat "$q/exit.txt"
 attempt=$(cat "$q/attempt.txt");unit="$r/extra-proxy-runs/unified-extra5/mhc_multilayer_recompute-03/hidev-npu0/$attempt"
 test -d "$unit";cp "$q/exit.txt" "$unit/retry-queue-exit.txt";cp "$q/console.log" "$unit/retry-queue-console.log";cp "$q/run.sh" "$unit/retry-queue-run.sh"
 python3 -B "$r/snapshot-mhc-retry-variants-20261110.py" "$which"
 python3 -B "$r/verify-archive.py" "$out"
 tar -C /workspace -czf "$r/$which-queue-snapshot-archive-bundle.tar.gz" "$(basename "$out")"
 sha256sum "$r/$which-queue-snapshot-archive-bundle.tar.gz";echo AFTER_QUEUE_ARCHIVE_READY
' -- "$which" "$q" "$pid" > "$r/$which-queue-archive.log" 2>&1 < /dev/null &
echo "$!" > "$r/$which-queue-archive.pid";echo ARCHIVE_PID=$!
echo __MHC_RETRY_TEN_NINE_END__
