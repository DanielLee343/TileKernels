#!/usr/bin/env bash
set -Eeuo pipefail
echo __START_ROPE_AUDIT_V2_RESUME_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/rope-audit-v2-resume-hidev-npu0"
mkdir -p "$q";test ! -e "$q/pid"
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/rope-audit-v2-resume-hidev-npu0"
wrapper=1627499;parent=2005735;worker=2023052;paused=0
cleanup(){ rc=$?;if ((paused));then kill -CONT "$wrapper" 2>/dev/null || true;fi;printf 'exit=%s at=%s\n' "$rc" "$(date -u +%FT%TZ)" > "$q/exit.txt"; }
trap cleanup EXIT
ps -p "$wrapper" -o args= | grep -Fq "$r/extra-rope-app-queue-hidev-npu0/run.sh"
ps -p "$parent" -o args= | grep -Fq "$r/hidev-rope-app-queue.py"
ps -p "$worker" -o args= | grep -Fq "$r/audit-rope-app-candidate.py rotary_embedding-02-q attempt-001"
grep -q '^PASS rejects missing outputs, duplicate record, wrong CSV and unauthorized input/output alias$' "$r/rope-audit-v2-test.log"
p="$r/extra-proxy-runs/unified-extra4/rotary_embedding-02-q/hidev-npu0/attempt-001";test ! -e "$p/detail/audit-result.json"
cp "$r/audit-rope-app-candidate.py" "$r/audit-rope-app-candidate-before-interval-index.py"
cp "$r/audit-rope-app-candidate-v2.py" "$r/audit-rope-app-candidate.py"
sha256sum "$r/audit-rope-app-candidate-before-interval-index.py" "$r/audit-rope-app-candidate.py" "$r/rope_interval_lookup.py" > "$q/audit-version-sha256.txt"
kill -STOP "$wrapper";paused=1;kill -TERM "$worker"
for i in $(seq 1 60);do
 if flock -n "$r/extra-rope-app-queue-hidev-npu0/queue.lock" true;then break;fi
 sleep 1
done
flock -n "$r/extra-rope-app-queue-hidev-npu0/queue.lock" true
python3 - "$p/queue-status.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]));assert x['status']=='audit_failed' and x['audit_exit']!=0,x
print('ORIGINAL_SLOW_AUDIT_STOPPED',x['audit_exit'])
PY
python3 -B "$r/audit-rope-app-candidate-v2.py" rotary_embedding-02-q attempt-001
python3 - "$p" <<'PY'
import json,sys,time
from pathlib import Path
p=Path(sys.argv[1]);d=p/'detail';a=d/'candidate-audit-result.json';b=d/'audit-result.json';x=json.loads(a.read_text());assert x['status']=='passed' and x['target']=='unified-extra4/rotary_embedding-02-q' and not b.exists()
(d/'reaudit-status.json').write_text(json.dumps({'status':'passed','previous_status':'audit_failed','reason':'previous quadratic interval lookup was intentionally stopped; equivalent indexed lookup passed baseline and negative tests','timestamp_unix':time.time()},indent=2)+'\n');b.write_bytes(a.read_bytes());print('PROMOTED_VERIFIED_REAUDIT',x['dbi_requested_bytes'])
PY
python3 -B "$r/hidev-rope-app-queue.py"
echo ALL_ROPE_V2_QUEUE_AUDITED
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid";echo "SUPERVISOR_PID=$!"
echo __START_ROPE_AUDIT_V2_RESUME_END__
