"""Investigate existing paged sparse REUSE output stores without promoting it."""
import csv,hashlib,json,os,re,struct,subprocess,sys
from collections import Counter,defaultdict
from decimal import Decimal
from importlib.machinery import SourceFileLoader
from pathlib import Path
r=Path(os.environ.get('BACKFILL_ROOT','/workspace/expert-profile-backfill-20261109-hidev'));case='paged-sparse-fp8-q4-k256-h8-b8';p=r/'deepgemm-runs'/case/'hidev-npu0'/os.environ.get('AUDIT_ATTEMPT','attempt-003');invest=json.loads((p/'frozen-reuse-address-investigation.json').read_text());records=invest['records'];assert invest['processes']==len(records)>=2 and len(invest['distinct_after_warmups_sha256'])==1;rec=records[0];addr=json.loads((p/rec['addresses']).read_text());assert all(hashlib.sha256((p/z['addresses']).read_bytes()).hexdigest()==z['addresses_sha256'] for z in records);out=addr['returned'];meta=addr['kwargs']['metadata'];assert out['dtype']=='torch.bfloat16' and out['shape']==[4,128] and out['stride'][1]==1 and out['element_size']==2
base=int(out['address'],16);mbase=int(meta['address'],16);assert base+2*(1+sum((n-1)*s for n,s in zip(out['shape'],out['stride'])))<=mbase or mbase+meta['shape'][0]<=base
data=(p/rec['after_warmups']).read_bytes();assert hashlib.sha256(data).hexdigest()==rec['after_warmups_sha256'];assert len(data)==4076032
ko=0x4000;nr=56;blocks=28;ranges=[struct.unpack_from('<II',data,ko+8*i) for i in range(nr)];expected=defaultdict(list)
for block in range(blocks):
 sequence=[]
 for rid in (2*block,2*block+1):
  beg,end=ranges[rid];assert beg<=end;sequence+=list(range(beg,end))
 begins={}
 for idx in sequence:
  w=struct.unpack_from('<10I',data,ko+nr*8+idx*40);ctl=w[1];qbegin=w[2];numq=(ctl>>11)&7;assert 0<numq<=4 and qbegin+numq<=4
  if ctl&(1<<14):begins={i:w[6+i]&65535 for i in range(numq)}
  if ctl&(1<<15):
   assert len(begins)==numq
   for i in range(numq):
    desc=w[6+i];beg=begins[i];end=(desc&65535)+(desc>>16);assert 0<=beg<=end<=128
    if end>beg:
     lo=base+2*((qbegin+i)*out['stride'][0]+beg);expected[3*block+i//2].append((lo,lo+2*(end-beg)))
   begins={}
 assert not begins

def merge(xs):
 result=[]
 for lo,hi in sorted(xs):
  assert lo<hi
  if result:assert result[-1][1]<=lo,'overlap'
  if result and result[-1][1]==lo:result[-1]=(result[-1][0],hi)
  else:result.append((lo,hi))
 return result
expected={c:merge(v) for c,v in expected.items()};assert expected
R=SourceFileLoader('reduce',str(r/'audit-reduce-family.py')).load_module().REGEX
raw=(p/'detail/profile.log').read_text(errors='replace');events=R.findall(raw);stores=[v for v in raw.splitlines() if 'DBI record core:' in v and 'dst:(type:GM;' in v and 'src:(type:UB;' in v];assert len(events)==len(stores)>0
metrics=[v for v in raw.splitlines() if 'processedRecord:' in v];assert metrics
for line in metrics:
 for field in ('droppedRecord','memoryCopyFailed','invalidParam','overflow','invalidDataCount','memoryCorruption','invalidRecordType','outOfBoundsRead'):
  m=re.search(r'\b'+field+r'\s*:?\s*(\d+)',line);assert m and int(m.group(1))==0,(field,line)
 m=re.search(r'receivedPacket\s+(\d+),\s*processedPacket\s+(\d+)',line);assert m and m.group(1)==m.group(2)
 m=re.search(r'each record type process fail count\s+([0-9, ]+)',line);assert m and not any(int(v) for v in re.findall(r'\d+',m.group(1)))
actual=defaultdict(list);percore=Counter();rounded=Counter();pcs=set()
for c,pc,addr,stride,l1s,l2s,srcaddr,srcstride,srcl1s,srcl2s,burst,length,dtype,l1,l2,left,right in events:
 c=int(c);assert c%3 in (0,1) and c//3<blocks;pcs.add(int(pc,16));addr=int(addr,16);stride=int(stride);l1s=int(l1s);l2s=int(l2s);n=int(burst);length=int(length);l1=int(l1);l2=int(l2);assert n>0 and length>0 and l1>=1 and l2>=1 and int(left)==int(right)==0
 percore[c]+=n*length*l1*l2;rounded[c]+=(((n*length+31)//32)*32 if int(srcstride)==length else n*((length+31)//32)*32)*l1*l2
 for z in range(l2):
  for y in range(l1):
   for x in range(n):
    lo=addr+z*l2s+y*l1s+x*stride;actual[c].append((lo,lo+length))
assert {c:merge(v) for c,v in actual.items()}==expected
op,=list((p/'detail/capture').rglob('OpBasicInfo.csv'));binary=op.parent/'dump/aicore_binary.o';assert binary.is_file()
isa=subprocess.check_output(['/workspace/tilekernels-env-20261101/cann/cann-9.2.1/tools/bisheng_compiler/bin/llvm-objdump','-d',str(binary)],text=True)
for pc in pcs:assert any(re.match(r'^\s*'+format(pc,'x')+r':',line) and 'MOV_UB_TO_OUT' in line for line in isa.splitlines()),hex(pc)
with op.with_name('Memory.csv').open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
assert len(rows)==84
for j,row in enumerate(rows):
 group,role=divmod(j,3);assert int(row['block_id'])==group and row['sub_block_id']==('cube0','vector0','vector1')[role];v=row['UB_to_GM_datas(KB)']
 if role:
  total=rounded[3*group+role-1]
  if v not in ('NA',''):assert abs(Decimal(v)*1024-total)<=Decimal('0.000512')
  else:assert total==0
 else:assert v in ('NA','') or Decimal(v)==0
outdoc={'status':'investigation_only','case':case,'events':len(events),'pcs':[hex(x) for x in sorted(pcs)],'requested_bytes':sum(percore.values()),'output_ranges_match':True,'csv_match':True,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'scope':'new independent REUSE window; original historical post-warm metadata unrecorded, not promoted'}
(p/'reuse-output-investigation-v3.json').write_text(json.dumps(outdoc,indent=2)+'\n');print(json.dumps(outdoc,indent=2))
