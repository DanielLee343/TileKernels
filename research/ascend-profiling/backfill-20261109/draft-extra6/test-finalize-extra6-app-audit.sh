#!/usr/bin/env bash
set -Eeuo pipefail
echo __FINALIZE_EXTRA6_AUDIT_TEST_BEGIN__
root=/workspace/expert-profile-backfill-20261109-hidev
tmp=$(mktemp -d "$root/finalize-extra6-audit-test.XXXXXXXX");trap 'rm -rf -- "$tmp"' EXIT
attempt="${AUDIT_ATTEMPT:?}"
[[ "$attempt" =~ ^attempt-[0-9]+$ ]]
base=extra-proxy-runs/unified-extra6/finalize-13-retry/hidev-npu0/$attempt
mkdir -p "$tmp/$(dirname "$base")";cp -a "$root/$base" "$tmp/$base";cp "$root/audit-reduce-family.py" "$tmp/";export BACKFILL_ROOT="$tmp"
run_audit(){ python3 -B "$root/audit-finalize-extra6-app-candidate.py" finalize-13-retry "$attempt"; }
run_audit
d="$tmp/$base/detail";cp "$d/profile.log" "$tmp/profile.log";cp "$d/capture-inspection.json" "$tmp/inspection.json"
for index in 3;do
 cp "$tmp/profile.log" "$d/profile.log"
 python3 - "$d" "$index" <<'PY'
from pathlib import Path
import json,re,sys
d=Path(sys.argv[1]);ident=json.loads((d/'capture-inspection.json').read_text());a=json.loads((d/('tensor-addresses-'+ident['representative_pid']+'.json')).read_text());t=a[int(sys.argv[2])]
lo=int(t['address'],16);hi=lo+t['logical_bytes'];p=d/'profile.log';lines=p.read_text().splitlines(keepends=True)
for i,s in enumerate(lines):
 m=re.search(r'DBI record core:.*dst:\(type:GM;addr:(0x[0-9a-f]+)',s)
 if m and lo<=int(m.group(1),16)<hi:del lines[i];break
else:raise RuntimeError('no store for output '+sys.argv[2])
p.write_text(''.join(lines))
PY
 if run_audit > "$tmp/missing-$index.out" 2>&1;then echo "MISSING_OUTPUT_${index}_UNDETECTED";exit 1;fi
done
cp "$tmp/profile.log" "$d/profile.log"
python3 - "$d/profile.log" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]);lines=p.read_text().splitlines(keepends=True);i=next(i for i,s in enumerate(lines) if 'DBI record core:' in s and 'dst:(type:GM;' in s and 'src:(type:UB;' in s);lines.insert(i,lines[i]);p.write_text(''.join(lines))
PY
if run_audit > "$tmp/duplicate.out" 2>&1;then echo DUPLICATE_STORE_UNDETECTED;exit 1;fi
cp "$tmp/profile.log" "$d/profile.log"
mem=$(find "$d/capture" -name Memory.csv -print -quit);cp "$mem" "$tmp/memory.csv"
python3 - "$mem" <<'PY'
from pathlib import Path
import csv,io,sys
p=Path(sys.argv[1]);r=csv.DictReader(io.StringIO(p.read_text(encoding='utf-8-sig')));rows=list(r)
row=next(x for x in rows if x['UB_to_GM_datas(KB)'] not in ('NA',''));row['UB_to_GM_datas(KB)']=str(float(row['UB_to_GM_datas(KB)'])+1)
with p.open('w',encoding='utf8',newline='') as f:w=csv.DictWriter(f,fieldnames=r.fieldnames);w.writeheader();w.writerows(rows)
PY
if run_audit > "$tmp/csv.out" 2>&1;then echo WRONG_CSV_UNDETECTED;exit 1;fi
cp "$tmp/memory.csv" "$mem"
python3 - "$d" <<'PY'
from pathlib import Path
import hashlib,json,sys
d=Path(sys.argv[1]);p=d/'capture-inspection.json';ident=json.loads(p.read_text())
for rec in ident['application_records']:
 f=d/rec['addresses'];a=json.loads(f.read_text());a[3]['address']=a[0]['address'];f.write_text(json.dumps(a));rec['addresses_sha256']=hashlib.sha256(f.read_bytes()).hexdigest()
p.write_text(json.dumps(ident))
PY
if run_audit > "$tmp/alias.out" 2>&1;then echo INPUT_ALIAS_UNDETECTED;exit 1;fi
echo 'PASS rejects missing outputs, duplicate record, wrong CSV and unauthorized input/output alias'
echo __FINALIZE_EXTRA6_AUDIT_TEST_END__
