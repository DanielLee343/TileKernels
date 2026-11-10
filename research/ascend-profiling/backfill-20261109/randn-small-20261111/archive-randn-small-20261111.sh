#!/usr/bin/env bash
set -Eeuo pipefail
echo __ARCHIVE_RANDN_SMALL_20261111_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
q="$r/randn-small-probe-20261111"
test "$(cat "$q/exit.txt")" = 0
attempt=$(cat "$q/attempt.txt")
unit="extra-proxy-runs/unified-extra2/randn-01/hidev-npu0/$attempt"
test ! -e "$r/randn-small-20261111.tar.gz"
python3 -B "$r/scan-public-archive.py" "$q"
python3 -B "$r/scan-public-archive.py" "$r/$unit"
python3 - "$r" "$unit" <<'PY'
import hashlib,json,sys
from pathlib import Path
r=Path(sys.argv[1]); unit=Path(sys.argv[2]); q=r/'randn-small-probe-20261111'
files=sorted([p for base in (q,r/unit) for p in base.rglob('*') if p.is_file() and p.name!='manifest.json'])
manifest={p.relative_to(r).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
(q/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('FILES',len(files),'CSV',sum(p.suffix=='.csv' for p in files))
PY
tar -C "$r" -czf "$r/randn-small-20261111.tar.gz" "randn-small-probe-20261111" "$unit"
sha256sum "$r/randn-small-20261111.tar.gz"
stat -c 'ARCHIVE_BYTES %s' "$r/randn-small-20261111.tar.gz"
echo __ARCHIVE_RANDN_SMALL_20261111_END__
