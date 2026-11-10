"""Candidate extra6 Sinkhorn finalize per-block byte audit; no automatic admission."""
import csv,hashlib,json,os,re,subprocess,sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from importlib.machinery import SourceFileLoader
root=Path(os.environ['BACKFILL_ROOT']);R=SourceFileLoader('reduce_audit',str(root/'audit-reduce-family.py')).load_module().REGEX
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
case,attempt=sys.argv[1:];assert re.fullmatch(r'finalize-(02|13|17|19)-retry',case)
p=root/'extra-proxy-runs/unified-extra6'/case/'hidev-npu0'/attempt/'detail';identity=json.loads((p/'capture-inspection.json').read_text())
assert identity['status']=='capture_identified_address_audit_pending' and identity['correctness']=='passed' and identity['historical_input_and_source_match']
representative=next(x for x in identity['application_records'] if x['pid']==identity['representative_pid'])
args=json.loads((p/representative['addresses']).read_text());assert len(args)==4 and all(args)
a=args[3];assert a['dtype']=='torch.float32' and len(a['shape'])==2;n,d=a['shape'];width=d*4
assert a['logical_bytes']==n*width and a['stride']==[d,1]
base=int(a['address'],16);end=base+a['logical_bytes']
for t in args[:3]:
 assert t['stride'] and all(x>=0 for x in t['stride']);lo=int(t['address'],16);hi=lo+(1+sum((dim-1)*stride for dim,stride in zip(t['shape'],t['stride'])))*t['element_size'];assert end<=lo or hi<=base
code=(p/representative['source']).read_text();assert code.count('asc_copy_ub2gm_align(')==1 and '((w * 56) + ((int32_t)block_idx)) < num_rows' in code
line=next(x for x in code.splitlines() if 'asc_copy_ub2gm_align(' in x)
assert f'(int64_t){d}' in line and f'(int64_t){56*d}' in line and re.search(r',\s*1,\s*'+str(width)+r',\s*static_cast<asc_store_l2_cache_mode>',line)
op,=list((p/'capture').rglob('OpBasicInfo.csv'));basic,=read(op)
assert (basic['Op Type'],basic['Block Dim'],basic['Device Id'])==('vector','56','0') and basic['Op Name']=='engram_sinkhorn_finalize_kernel_asc_kernel'
binary=op.parent/'dump/aicore_binary.o';assert sha(binary)==identity['capture_binary_sha256']
isa=subprocess.check_output([os.environ['BACKFILL_OBJDUMP'],'-d',str(binary)],text=True);(p/'device-kernel.isa').write_text(isa)
raw=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',raw);assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
stores=[x for x in raw.splitlines() if 'DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x];rec=R.findall(raw);assert len(stores)==len(rec)==n,(len(stores),len(rec),n)
hits=Counter();blocks=Counter();pcs=set()
for c,pc,addr,stride,l1s,l2s,srcaddr,srcstride,srcl1s,srcl2s,burst,length,dtype,l1,l2,left,right in rec:
 c=int(c);row,rem=divmod(int(addr,16)-base,width);assert 0<=row<n and rem==0
 assert (int(burst),int(length),int(l1),int(l2),int(left),int(right))==(1,width,1,1,0,0)
 block=row%56;assert (c//3,c%3)==divmod(block,2);hits[row]+=1;blocks[block]+=width;pcs.add(int(pc,16))
assert hits==Counter(range(n))
for pc in pcs:assert any(re.match(r'^\s*'+format(pc,'x')+r':',line) and 'MOV_UB_TO_OUT' in line for line in isa.splitlines())
mem=read(op.with_name('Memory.csv'));assert len(mem)==56
for j,row in enumerate(mem):
 assert int(row['block_id'])==j and row['sub_block_id']=='vector0';value=row['UB_to_GM_datas(KB)'];expected=blocks[2*j]+blocks[2*j+1] if j<28 else None
 if j<28 and value not in ('NA',''):assert abs(Decimal(value)*1024-expected)<=Decimal('0.000512')
 elif j<28:assert expected==0
 else:assert value in ('NA','')
result={'target':'unified-extra6/'+case,'status':'passed','device':'hidev NPU 0','correctness':'passed','historical_input_and_source_match':True,'runtime_kernel':basic['Op Name'],'dbi_requested_bytes':sum(blocks.values()),'output_logical_bytes':n*width,'per_vector_block_requested_bytes':{i:blocks[i] for i in range(56)},'capture_binary_sha256':sha(binary),'dbi_pc':[hex(x) for x in sorted(pcs)],'csv_pair_totals_match':True,'scope':'application replay; requested UB to GM bytes, not physical DRAM writes'}
(p/'candidate-audit-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',case,sum(blocks.values()))
