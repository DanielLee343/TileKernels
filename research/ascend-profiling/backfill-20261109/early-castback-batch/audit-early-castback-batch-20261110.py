"""Candidate audit for one early single-call castback; preserve replay windows."""
import csv,hashlib,json,re,struct,subprocess,sys
from collections import Counter
from decimal import Decimal
from importlib.machinery import SourceFileLoader
from pathlib import Path
from rope_interval_lookup import locate
from strided_tensor_intervals import intervals
root=Path(__import__('os').environ.get('BACKFILL_ROOT','/workspace/expert-profile-backfill-20261109-hidev'));case,attempt=sys.argv[1:];assert case in ('castback-n1-h128-bf16','castback-n512-h2048-bf16','castback-n512-h2048-fp32','castback-n8001-h2048-fp32');assert re.fullmatch(r'attempt-\d+',attempt)
p=root/('early-castback-single-runs-20261110' if case=='castback-n1-h128-bf16' else 'early-castback-batch-runs-20261110')/case/'hidev-npu0'/attempt/'detail';ident=json.loads((p/'capture-inspection.json').read_text());assert ident['status']=='capture_identified_address_audit_pending' and ident['correctness']=='passed' and ident['historical_input_and_source_match']
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();records=ident['application_records'];assert len(records)>=2
rep=next(x for x in records if x['pid']==ident['representative_pid']);addresses=json.loads((p/rep['addresses']).read_text());inputs=addresses['inputs'];outputs=addresses['outputs'];assert len(inputs)==2 and len(outputs)==1 and outputs[0]['shape']==json.loads((p/'provenance/historical-default.json').read_text())['outputs'][0]['shape'] and outputs[0]['logical_bytes']==json.loads((p/'provenance/historical-default.json').read_text())['outputs'][0]['bytes']
for rec in records:
 for key in ('application','addresses','source'):assert sha(p/rec[key])==rec[key+'_sha256'],key
 assert json.loads((p/rec['addresses']).read_text())==addresses
def bounds(t):
 assert t['shape'] and all(n>0 for n in t['shape']) and all(s>=0 for s in t['stride'])
 lo=int(t['address'],16);return lo,lo+t['element_size']*(1+sum((n-1)*s for n,s in zip(t['shape'],t['stride'])))
for i,x in enumerate(outputs):
 for y in inputs+outputs[i+1:]:
  lo,hi=bounds(x);a,b=bounds(y);assert hi<=a or b<=lo,'output overlaps input or another output'
expected=[intervals(t['shape'],t['stride'],t['element_size'],int(t['address'],16)) for t in outputs];starts=[[lo for lo,_ in x] for x in expected]
source=(p/rep['source']).read_text();stores=[v for v in source.splitlines() if 'asc_copy_ub2gm_align(' in v];assert len(stores)==1 and any('out[' in line for line in stores)
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
def read(f):
 with f.open(encoding='utf-8-sig',newline='') as q:return list(csv.DictReader(q))
basic,=read(op);assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==('cast_back_kernel_ascend_kernel','vector','56','0')
binary=op.parent/'dump/aicore_binary.o';assert sha(binary)==ident['capture_binary_sha256']
isa=subprocess.check_output(['/workspace/tilekernels-env-20261101/cann/cann-9.2.1/tools/bisheng_compiler/bin/llvm-objdump','-d',str(binary)],text=True);(p/'device-kernel.isa').write_text(isa)
log=(p/'profile.log').read_text(errors='replace');metrics=[x for x in log.splitlines() if 'processedRecord:' in x];assert metrics
for line in metrics:
 for field in ('droppedRecord','memoryCopyFailed','invalidParam','overflow','invalidDataCount','memoryCorruption','invalidRecordType','outOfBoundsRead'):
  m=re.search(r'\b'+field+r'\s*:?\s*(\d+)',line);assert m and int(m.group(1))==0,(field,line)
 m=re.search(r'receivedPacket\s+(\d+),\s*processedPacket\s+(\d+)',line);assert m and m.group(1)==m.group(2)
 m=re.search(r'each record type process fail count\s+([0-9, ]+)',line);assert m and not any(int(v) for v in re.findall(r'\d+',m.group(1)))
R=SourceFileLoader('r',str(root/'audit-reduce-family.py')).load_module().REGEX;events=R.findall(log);lines=[x for x in log.splitlines() if 'DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x];assert len(events)==len(lines)>0
actual=[[] for _ in outputs];percore=Counter();rounded=Counter();pcs=set()
for c,pc,addr,stride,l1s,l2s,srcaddr,srcstride,srcl1s,srcl2s,burst,length,dtype,l1,l2,left,right in events:
 c=int(c);assert c%3 in (0,1) and c//3<28;pcs.add(int(pc,16));addr=int(addr,16);stride=int(stride);l1s=int(l1s);l2s=int(l2s);n=int(burst);length=int(length);l1=int(l1);l2=int(l2)
 assert n>0 and length>0 and l1>=1 and l2>=1 and int(left)==int(right)==0
 percore[c]+=n*length*l1*l2;rounded[c]+=(((n*length+31)//32)*32 if int(srcstride)==length else n*((length+31)//32)*32)*l1*l2
 for z in range(l2):
  for y in range(l1):
   for x in range(n):
    lo=addr+z*l2s+y*l1s+x*stride;hi=lo+length;matches=locate(expected,starts,lo,hi);assert len(matches)==1,(hex(lo),hex(hi),matches);actual[matches[0]].append((lo,hi))
def merge(xs):
 out=[]
 for lo,hi in sorted(xs):
  assert lo<hi
  if out:assert out[-1][1]<=lo,'duplicate or overlapping write'
  if out and out[-1][1]==lo:out[-1]=(out[-1][0],hi)
  else:out.append((lo,hi))
 return out
assert all(merge(actual[i])==expected[i] for i in range(len(outputs)))
isa_pcs={int(m.group(1),16) for line in isa.splitlines() if (m:=re.match(r'^\s*([0-9a-f]+):.*\bMOV_UB_TO_OUT',line))};assert pcs and pcs==isa_pcs,(pcs,isa_pcs)
mem=read(op.with_name('Memory.csv'));assert len(mem)==56
for j,row in enumerate(mem):
 assert int(row['block_id'])==j and row['sub_block_id']=='vector0';v=row['UB_to_GM_datas(KB)'];total=rounded[3*j]+rounded[3*j+1] if j<28 else None
 if j<28 and v not in ('NA',''):assert abs(Decimal(v)*1024-total)<=Decimal('0.000512'),(j,v,total)
 elif j<28:assert total==0
 else:assert v in ('NA','')
logical=sum(t['logical_bytes'] for t in outputs);assert sum(percore.values())==logical
result={'target':'early/'+case,'status':'passed','device':'hidev NPU 0','correctness':'passed','historical_input_and_source_match':True,'runtime_kernel':basic['Op Name'],'dbi_requested_bytes':sum(percore.values()),'output_logical_bytes':logical,'per_vector_block_requested_bytes':{i:percore[3*(i//2)+i%2] for i in range(56)},'capture_binary_sha256':sha(binary),'dbi_pc':[hex(x) for x in sorted(pcs)],'csv_pair_totals_match':True,'application_processes':len(records),'replay_mode':'application','scope':'new application replay on 8B:00; single-call historical kernel replay on 0D:00 remains separate; requested AIV UB to GM bytes, not physical DRAM writes'}
(p/'candidate-early-castback-batch-audit-20261110.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS early castback',logical)
