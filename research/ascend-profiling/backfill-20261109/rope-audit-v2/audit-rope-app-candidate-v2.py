"""Audit RoPE target in-place output under application replay."""
import csv,hashlib,itertools,json,os,re,subprocess,sys
from collections import Counter
from decimal import Decimal
from importlib.machinery import SourceFileLoader
from pathlib import Path
from rope_interval_lookup import locate

root=Path(os.environ.get('BACKFILL_ROOT','/workspace/expert-profile-backfill-20261109-hidev'))
case,attempt=sys.argv[1:];assert re.fullmatch(r'rotary_embedding-(0[1-9]|1[0-9]|20)-(q|k)',case) and re.fullmatch(r'attempt-[0-9]+',attempt)
p=root/'extra-proxy-runs'/'unified-extra4'/case/'hidev-npu0'/attempt/'detail'
ident=json.loads((p/'capture-inspection.json').read_text());assert ident['status']=='capture_identified_address_audit_pending'
assert ident['correctness']=='passed' and ident['historical_input_and_source_match']
assert all(d=='0' and m=='0' for _,d,m in ident['parser_metrics']) and ident['parser_metrics']
pid=ident['representative_pid'];a=json.loads((p/('tensor-addresses-'+pid+'.json')).read_text());assert len(a)==4 and all(a[:3]) and a[3] is None
old=json.loads((p/'provenance/historical-default.json').read_text());records=ident['application_records'];assert len(records)>=2
for rec in records:
 for name,key in ((rec['application'],'application_sha256'),(rec['addresses'],'addresses_sha256'),(rec['source'],'source_sha256')):
  assert hashlib.sha256((p/name).read_bytes()).hexdigest()==rec[key],name
 app=json.loads((p/rec['application']).read_text());assert app['status']=='passed' and app['inputs']==old['inputs'] and app['source_sha256']==records[0]['source_sha256']
 assert json.loads((p/rec['addresses']).read_text())==a
manifest=json.loads((p/'provenance/cases.json').read_text())['cases'];selected,=(x for x in manifest if x['target_id']=='unified-extra4/'+case)
params=selected['params'];cores=28
assert a[0]['shape']==[1,params['seqlen'],params['nheads'],params['dim']]
assert a[0]['dtype']=={'bf16':'torch.bfloat16','fp32':'torch.float32'}[params['dtype']]
outputs=[a[0]];names=['x']
def span(t):
 lo=int(t['address'],16);hi=lo+t['element_size']*(1+sum((n-1)*stride for n,stride in zip(t['shape'],t['stride'])))
 return lo,hi
inputs=a[1:3]
for i,x in enumerate(outputs):
 for y in inputs+outputs[i+1:]:
  l1,h1=span(x);l2,h2=span(y);assert h1<=l2 or h2<=l1,'input/output buffer overlap'
source=(p/('generated-kernel-'+pid+'.cpp')).read_text();lines=[x for x in source.splitlines() if 'asc_copy_ub2gm_align(' in x]
assert len(lines)==1 and 'block_idx' in source
for name in names:
 matches=[x for x in lines if re.search(r'(?<![A-Za-z0-9_])'+re.escape(name)+r'\s*\[',x.split('(__ubuf__',1)[0])]
 assert len(matches)==1,(name,len(matches))
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
def read(path):
 with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
basic,=read(op);assert basic['Op Type']=='vector' and int(basic['Block Dim'])==2*cores and basic['Device Id']=='0'
binary=op.parent/'dump/aicore_binary.o';assert hashlib.sha256(binary.read_bytes()).hexdigest()==ident['capture_binary_sha256']
isa=subprocess.check_output(['/workspace/tilekernels-env-20261101/cann/cann-9.2.1/tools/bisheng_compiler/bin/llvm-objdump','-d',str(binary)],text=True)
(p/'device-kernel.isa').write_text(isa)
R=SourceFileLoader('r',str(root/'audit-reduce-family.py')).load_module().REGEX
log=(p/'profile.log').read_text(errors='replace');events=R.findall(log)
stores=[x for x in log.splitlines() if 'DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x]
assert len(events)==len(stores)>0
def merge(intervals):
 out=[]
 for lo,hi in sorted(intervals):
  assert lo<hi
  if out and lo<out[-1][1]:raise AssertionError(('overlap',lo,hi,out[-1]))
  if out and lo==out[-1][1]:out[-1]=(out[-1][0],hi)
  else:out.append((lo,hi))
 return out
expected=[]
for item in outputs:
 shape=item['shape'];stride=item['stride'];size=item['element_size'];base=int(item['address'],16)
 assert shape and len(shape)==len(stride) and stride[-1]==1 and all(x>0 for x in shape) and all(x>=0 for x in stride)
 assert __import__('math').prod(shape[:-1])<=1000000
 intervals=[]
 for coords in itertools.product(*(range(n) for n in shape[:-1])):
  lo=base+size*sum(c*s for c,s in zip(coords,stride));intervals.append((lo,lo+shape[-1]*size))
 expected.append(merge(intervals))
starts=[[lo for lo,_ in intervals] for intervals in expected]
actual=[[] for _ in outputs];percore=Counter();rounded=Counter();pcs=set()
for c,pc,addr,stride,l1s,l2s,srcaddr,srcstride,srcl1s,srcl2s,burst,length,dtype,l1,l2,left,right in events:
 c=int(c);assert c%3 in (0,1) and c//3<cores;pcs.add(int(pc,16));addr=int(addr,16)
 stride=int(stride);l1s=int(l1s);l2s=int(l2s);n=int(burst);length=int(length);l1=int(l1);l2=int(l2)
 assert n>0 and length>0 and l1>=1 and l2>=1 and int(left)==int(right)==0
 percore[c]+=n*length*l1*l2
 rounded[c]+=(((n*length+31)//32)*32 if int(srcstride)==length else n*((length+31)//32)*32)*l1*l2
 for z in range(l2):
  for y in range(l1):
   for x in range(n):
    lo=addr+z*l2s+y*l1s+x*stride;hi=lo+length
    candidates=locate(expected,starts,lo,hi)
    assert len(candidates)==1,(hex(lo),hex(hi),candidates);actual[candidates[0]].append((lo,hi))
assert all(merge(actual[i])==expected[i] for i in range(len(outputs)))
for pc in pcs:assert any(re.match(r'^\s*'+format(pc,'x')+r':',line) and 'MOV_UB_TO_OUT' in line for line in isa.splitlines()),hex(pc)
mem=read(op.with_name('Memory.csv'));assert len(mem)==2*cores
for j,row in enumerate(mem):
 assert int(row['block_id'])==j and row['sub_block_id']=='vector0';value=row['UB_to_GM_datas(KB)'];total=rounded[3*j]+rounded[3*j+1] if j<cores else None
 if j<cores and value not in ('NA',''):assert abs(Decimal(value)*1024-total)<=Decimal('0.000512'),(j,value,total)
 elif j<cores:assert total==0
 else:assert value in ('NA','')
result={'target':'unified-extra4/'+case,'status':'passed','device':'hidev NPU 0','correctness':'passed',
 'historical_input_and_source_match':True,'runtime_kernel':basic['Op Name'],'dbi_requested_bytes':sum(percore.values()),
 'output_logical_bytes':sum(item['logical_bytes'] for item in outputs),'per_vector_block_requested_bytes':{i:percore[3*(i//2)+i%2] for i in range(2*cores)},
 'capture_binary_sha256':ident['capture_binary_sha256'],'dbi_pc':[hex(x) for x in sorted(pcs)],'csv_pair_totals_match':True,
 'application_processes':len(ident['application_records']),'replay_mode':'application',
 'scope':'application replay; all observed processes passed upstream test and matched initial input hash; RoPE target tensor is intentionally updated in place; stride gaps are excluded; requested UB to GM bytes, not physical DRAM transactions'}
assert result['dbi_requested_bytes']==result['output_logical_bytes']
(p/'candidate-audit-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',case,result['dbi_requested_bytes'])
