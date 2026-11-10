#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_FINALIZE_EXTRA6_APP_QUEUE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra6-finalize-app-queue-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra6-finalize-app-queue-hidev-npu0"
trap 'rc=$?;printf "exit=%s at=%s\n" "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"' EXIT
prev="$r/extra6-finalize-app-smoke-hidev-npu0";pid=$(cat "$prev/pid")
while ps -p "$pid" -o args= | grep -Fq "$prev/run.sh";do sleep 10;done
grep -q '^exit=0 ' "$prev/exit.txt";attempt=$(cat "$prev/attempt.txt")
unset LD_LIBRARY_PATH PYTHONPATH LD_PRELOAD
source /workspace/tilekernels-env-20261101/activate.sh
export BACKFILL_ROOT="$r" BACKFILL_OBJDUMP="$ASCEND_HOME_PATH/tools/bisheng_compiler/bin/llvm-objdump" AUDIT_ATTEMPT="$attempt"
python3 -B "$r/audit-finalize-extra6-app-candidate.py" finalize-13-retry "$attempt"
bash "$r/test-finalize-extra6-app-audit.sh" > "$r/finalize-extra6-app-audit-test.log" 2>&1
cat "$r/finalize-extra6-app-audit-test.log"
grep -q '^PASS rejects missing outputs, duplicate record, wrong CSV and unauthorized input/output alias$' "$r/finalize-extra6-app-audit-test.log"
python3 - "$r" "$attempt" <<'PY'
import json,sys
from pathlib import Path
r=Path(sys.argv[1]);p=r/'extra-proxy-runs/unified-extra6/finalize-13-retry/hidev-npu0'/sys.argv[2]/'detail';a=p/'candidate-audit-result.json';b=p/'audit-result.json';d=json.loads(a.read_text());assert d['status']=='passed' and d['target']=='unified-extra6/finalize-13-retry' and not b.exists();b.write_bytes(a.read_bytes());print('PROMOTED',d['target'],d['dbi_requested_bytes'])
PY
python3 -B "$r/hidev-finalize-extra6-app-queue.py"
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "QUEUE_PID=$!"
echo __START_FINALIZE_EXTRA6_APP_QUEUE_END__
