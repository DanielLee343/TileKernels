"""Independently compare exported XLSX cells against frozen JSONL rows."""
import json,math,sys
from itertools import zip_longest
from pathlib import Path
from openpyxl import load_workbook
folder=Path(sys.argv[1]);capture=sys.argv[2]=='capture';book=load_workbook(folder/('staged-capture.xlsx' if capture else 'staged-detail.xlsx'),read_only=True,data_only=False);total=0
for kind,sheet in [('vector','Vector'),('cube','Cube'),('mix','CV融合')]:
 with (folder/(kind+('-capture' if capture else '')+'.jsonl')).open(encoding='utf8') as f:
  header=json.loads(next(f));stream=(json.loads(x) for x in f);rows=book[sheet].iter_rows(min_row=4,max_col=len(header),values_only=True)
  actual=next(rows);assert list(actual)==header,(sheet,'header')
  count=0
  for rownum,(expected,observed) in enumerate(zip_longest(stream,rows),5):
   assert expected is not None and observed is not None,(sheet,rownum,'row count')
   for j,(a,b) in enumerate(zip(expected,observed)):
    if isinstance(a,(int,float)) and not isinstance(a,bool) and isinstance(b,(int,float)) and not isinstance(b,bool):assert math.isclose(a,b,rel_tol=1e-13,abs_tol=1e-12),(sheet,rownum,j,a,b)
    else:assert a==b or (a in (None,'') and b is None),(sheet,rownum,j,a,b)
   count+=1
  total+=count;print(sheet,'verified rows',count,flush=True)
print('ALL_VALUES_VERIFIED',total,flush=True)
