#!/usr/bin/env bash
set -Eeuo pipefail
echo __REUSE_OUTPUT_AUDIT_TEST_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;t=$(mktemp -d "$r/reuse-output-test.XXXXXXXX");trap 'rm -rf -- "$t"' EXIT
b=deepgemm-runs/paged-sparse-fp8-q4-k256-h8-b8/hidev-npu0/attempt-001
mkdir -p "$t/$(dirname "$b")";cp -a "$r/$b" "$t/$b";cp "$r/audit-reduce-family.py" "$t/";export BACKFILL_ROOT="$t"
run_audit(){ python3 -B "$r/investigate-paged-reuse-output-v2.py"; }
run_audit
p="$t/$b";cp "$p/detail/profile.log" "$t/original.log"
python3 - "$p/detail/profile.log" missing <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text().splitlines(keepends=True);i=next(i for i,v in enumerate(s) if 'DBI record core:' in v and 'dst:(type:GM;' in v and 'src:(type:UB;' in v)
if sys.argv[2]=='missing':del s[i]
else:s.insert(i,s[i])
p.write_text(''.join(s))
PY
if run_audit > "$t/missing.out" 2>&1;then echo MISSING_UNDETECTED;exit 1;fi
cp "$t/original.log" "$p/detail/profile.log"
python3 - "$p/detail/profile.log" duplicate <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text().splitlines(keepends=True);i=next(i for i,v in enumerate(s) if 'DBI record core:' in v and 'dst:(type:GM;' in v and 'src:(type:UB;' in v);s.insert(i,s[i]);p.write_text(''.join(s))
PY
if run_audit > "$t/duplicate.out" 2>&1;then echo DUPLICATE_UNDETECTED;exit 1;fi
cp "$t/original.log" "$p/detail/profile.log"
mem=$(find "$p/detail/capture" -name Memory.csv -print -quit);cp "$mem" "$t/memory.csv"
python3 - "$mem" <<'PY'
from pathlib import Path
import csv,sys
p=Path(sys.argv[1]);f=p.open(encoding='utf-8-sig',newline='');r=csv.DictReader(f);rows=list(r);fields=r.fieldnames;f.close();row=next(x for x in rows if x['sub_block_id']=='vector0' and x['UB_to_GM_datas(KB)'] not in ('NA',''));row['UB_to_GM_datas(KB)']=str(float(row['UB_to_GM_datas(KB)'])+1)
with p.open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
PY
if run_audit > "$t/csv.out" 2>&1;then echo BAD_CSV_UNDETECTED;exit 1;fi
cp "$t/memory.csv" "$mem"
python3 - "$p/detail/profile.log" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text();assert 'droppedRecord: 0' in s;p.write_text(s.replace('droppedRecord: 0','droppedRecord: 1',1))
PY
if run_audit > "$t/parser.out" 2>&1;then echo BAD_PARSER_UNDETECTED;exit 1;fi
cp "$t/original.log" "$p/detail/profile.log"
python3 - "$p/profile-addresses.json" <<'PY'
from pathlib import Path
import json,sys
p=Path(sys.argv[1]);x=json.loads(p.read_text());x[0]['returned']['address']=x[0]['kwargs']['metadata']['address'];p.write_text(json.dumps(x))
PY
if run_audit > "$t/alias.out" 2>&1;then echo OUTPUT_ALIAS_UNDETECTED;exit 1;fi
echo 'PASS rejects missing, duplicate, wrong CSV, parser errors and output alias'
echo __REUSE_OUTPUT_AUDIT_TEST_END__
