#!/usr/bin/env bash
set -Eeuo pipefail
echo __MHC_THREE_EQUAL_AUDIT_TEST_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
t=$(mktemp -d "$r/mhc-three-equal-audit-test.XXXXXXXX");trap 'rm -rf -- "$t"' EXIT
b=extra-proxy-runs/unified-extra5/mhc_multilayer_recompute-10/hidev-npu0/attempt-002
mkdir -p "$t/$(dirname "$b")";cp -a "$r/$b" "$t/$b";cp "$r/audit-reduce-family.py" "$t/";export BACKFILL_ROOT="$t"
run_audit(){ python3 -B "$r/audit-mhc-three-equal-20261110.py" mhc_multilayer_recompute-10 attempt-002; }
run_audit
d="$t/$b/detail";cp "$d/profile.log" "$t/original.log";cp "$d/capture-inspection.json" "$t/original-ident.json"
for i in 0 2 3 5;do
 cp "$t/original.log" "$d/profile.log"
 python3 - "$d" "$i" <<'PY'
from pathlib import Path
import json,re,sys
d=Path(sys.argv[1]);ident=json.loads((d/'capture-inspection.json').read_text());rec=next(x for x in ident['application_records'] if x['pid']==ident['representative_pid']);sem=json.loads((d/rec['semantic_addresses']).read_text());o=(sem['layer_out']+sem['residual_out'])[int(sys.argv[2])];lo=int(o['address'],16);hi=lo+o['logical_bytes'];p=d/'profile.log';lines=p.read_text().splitlines(keepends=True)
for i,s in enumerate(lines):
 m=re.search(r'DBI record core:.*dst:\(type:GM;addr:(0x[0-9a-f]+)',s)
 if m and lo<=int(m.group(1),16)<hi:del lines[i];break
else:raise RuntimeError('no output store')
p.write_text(''.join(lines))
PY
 if run_audit > "$t/missing-$i.out" 2>&1;then echo MISSING_OUTPUT_UNDETECTED;exit 1;fi
done
cp "$t/original.log" "$d/profile.log"
python3 - "$d/profile.log" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text().splitlines(keepends=True);i=next(i for i,v in enumerate(s) if 'DBI record core:' in v and 'dst:(type:GM;' in v and 'src:(type:UB;' in v);s.insert(i,s[i]);p.write_text(''.join(s))
PY
if run_audit > "$t/duplicate.out" 2>&1;then echo DUPLICATE_UNDETECTED;exit 1;fi
cp "$t/original.log" "$d/profile.log"
mem=$(find "$d/capture" -name Memory.csv -print -quit);cp "$mem" "$t/memory.csv"
python3 - "$mem" <<'PY'
from pathlib import Path
import csv,io,sys
p=Path(sys.argv[1]);r=csv.DictReader(io.StringIO(p.read_text(encoding='utf-8-sig')));rows=list(r);row=next(x for x in rows if x['UB_to_GM_datas(KB)'] not in ('NA',''));row['UB_to_GM_datas(KB)']=str(float(row['UB_to_GM_datas(KB)'])+1)
with p.open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=r.fieldnames);w.writeheader();w.writerows(rows)
PY
if run_audit > "$t/csv.out" 2>&1;then echo WRONG_CSV_UNDETECTED;exit 1;fi
cp "$t/memory.csv" "$mem"
python3 - "$d" <<'PY'
from pathlib import Path
import json,sys
d=Path(sys.argv[1]);ident=json.loads((d/'capture-inspection.json').read_text());rec=ident['application_records'][0];p=d/rec['pointer_tables'][0]['name'];blob=bytearray(p.read_bytes());blob[0]^=1;p.write_bytes(blob)
PY
if run_audit > "$t/pointer.out" 2>&1;then echo BAD_POINTER_UNDETECTED;exit 1;fi
echo 'PASS rejects missing output, duplicate store, wrong CSV and changed pointer table'
echo __MHC_THREE_EQUAL_AUDIT_TEST_END__
