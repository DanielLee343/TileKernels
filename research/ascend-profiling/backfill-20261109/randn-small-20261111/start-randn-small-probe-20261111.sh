#!/usr/bin/env bash
set -Eeuo pipefail
echo __RANDN_SMALL_20261111_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
q="$r/randn-small-probe-20261111"
mkdir "$q"
sed "s/assert target=='unified-extra2\/randn-04' and re.fullmatch/assert target=='unified-extra2\/randn-01' and re.fullmatch/" "$r/inspect-randn-app-probe.py" > "$q/inspect.py"
grep -F "assert target=='unified-extra2/randn-01'" "$q/inspect.py" > /dev/null
cat > "$q/run.sh" <<'SH'
#!/usr/bin/env bash
set -Eeuo pipefail
r=/workspace/expert-profile-backfill-20261109-hidev
q="$r/randn-small-probe-20261111"
trap 'rc=$?; printf "%s\n" "$rc" > "$q/exit.txt"' EXIT
export TARGET_ID=unified-extra2/randn-01
export ATTEMPT=$(python3 - "$r/extra-proxy-runs/$TARGET_ID/hidev-npu0" <<'PY'
from pathlib import Path
import re,sys
ids=[int(x.name[8:]) for x in Path(sys.argv[1]).glob('attempt-*') if re.fullmatch(r'attempt-\d+',x.name)]
print(f'attempt-{max(ids,default=0)+1:03d}')
PY
)
printf '%s\n' "$ATTEMPT" > "$q/attempt.txt"
bash "$r/run-hidev-extra-randn-app-probe.sh"
python3 -B "$q/inspect.py" "$TARGET_ID" "$ATTEMPT"
SH
nohup bash "$q/run.sh" > "$q/console.log" 2>&1 < /dev/null &
echo "$!" > "$q/pid"
echo "probe_pid=$!"
echo __RANDN_SMALL_20261111_END__
