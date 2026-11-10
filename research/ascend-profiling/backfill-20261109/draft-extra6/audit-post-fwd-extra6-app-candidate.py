"""Candidate extra6 post forward per-block requested-byte audit."""
import csv,hashlib,json,os,re,subprocess,sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from importlib.machinery import SourceFileLoader
root=Path(os.environ['BACKFILL_ROOT']);R=SourceFileLoader('reduce_audit',str(root/'audit-reduce-family.py')).load_module().REGEX
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 with p.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
case,attempt=sys.argv[1:];assert re.fullmatch(r'post-fwd-(02|04|10|11|12|18|20)-retry',case)
p=root/'extra-proxy-runs/unified-extra6'/case/'hidev-npu0'/attempt/'detail';ident=json.loads((p/'capture-inspection.json').read_text());assert ident['status']=='capture_identified_address_audit_pending' and ident['correctness']=='passed' and ident['historical_input_and_source_match']
rep=next(x for x in ident['application_records'] if x['pid']==ident['representative_pid']);args=json.loads((p/rep['addresses']).read_text());assert len(args)==5 and all(args)
out=args[4];assert out['dtype']=='torch.bfloat16' and len(out['shape'])==3;n,m,h=out['shape'];assert n>=56 and m==4 and out['stride']==[m*h,h,1] and out['logical_bytes']==n*m*h*2
base=int(out['address'],16);end=base+out['logical_bytes']
for a in args[:4]:
 lo=int(a['address'],16);hi=lo+(1+sum((dim-1)*stride for dim,stride in zip(a['shape'],a['stride'])))*a['element_size'];assert end<=lo or hi<=base
rowbytes=m*h*2;code=(p/rep['source']).read_text();assert code.count('asc_copy_ub2gm_align(')==1;line=next(x for x in code.splitlines() if 'asc_copy_ub2gm_align(' in x)
match=re.search(r',\s*(\d+),\s*(\d+),\s*static_cast<asc_store_l2_cache_mode>\(\d+\),\s*(\d+),\s*(\d+)\);',line);assert match
nburst,width,dst_stride,src_stride=map(int,match.groups());assert rowbytes%(nburst*width)==0;tiles=rowbytes//(nburst*width);assert f'/ num_tokens) < {tiles})' in code and (dst_stride==h*2 or nburst==1)
op,=list((p/'capture').rglob('OpBasicInfo.csv'));basic,=read(op);assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==('mhc_post_fwd_asc_kernel','vector','56','0')
binary=op.parent/'dump/aicore_binary.o';assert sha(binary)==ident['capture_binary_sha256'];isa=subprocess.check_output([os.environ['BACKFILL_OBJDUMP'],'-d',str(binary)],text=True);(p/'device-kernel.isa').write_text(isa)
raw=(p/'profile.log').read_text(errors='replace');metrics=re.findall(r'processedRecord: (\d+), droppedRecord: (\d+).*?memoryCorruption (\d+)',raw);assert metrics and all(d=='0' and m=='0' for _,d,m in metrics)
stores=[x for x in raw.splitlines() if 'DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x];rec=R.findall(raw);assert len(stores)==len(rec)==n*tiles
segments=Counter();blocks=Counter();pcs=set();requests=Counter()
for c,pc,addr,stride,l1s,l2s,srcaddr,srcstride,srcl1s,srcl2s,burst,length,dtype,l1,l2,left,right in rec:
 c=int(c);row,offset=divmod(int(addr,16)-base,rowbytes);tile,remain=divmod(offset,width);assert 0<=row<n and 0<=tile<tiles and remain==0
 block=(row+tile*n)%56;assert (c//3,c%3)==divmod(block,2)
 assert (int(burst),int(length),int(stride),int(l1),int(l2),int(left),int(right))==(nburst,width,dst_stride,1,1,0,0) and int(srcstride)==src_stride
 for b in range(nburst):start=offset+b*dst_stride;assert start+width<=rowbytes;segments[(row,tile,b)]+=1
 blocks[block]+=nburst*width;requests[block]+=1;pcs.add(int(pc,16))
assert len(segments)==n*tiles*nburst and all(v==1 for v in segments.values())
intervals=sorted((tile*width+b*dst_stride,tile*width+b*dst_stride+width) for tile in range(tiles) for b in range(nburst));assert intervals[0][0]==0 and intervals[-1][1]==rowbytes and all(x[1]==y[0] for x,y in zip(intervals,intervals[1:]))
assert set(blocks)==set(range(56))
for b in range(56):assert requests[b]==max(0,(n*tiles+55-b)//56)
for pc in pcs:assert any(re.match(r'^\s*'+format(pc,'x')+r':',line) and 'MOV_UB_TO_OUT' in line for line in isa.splitlines())
mem=read(op.with_name('Memory.csv'));assert len(mem)==56
for i,row in enumerate(mem):
 assert int(row['block_id'])==i and row['sub_block_id']=='vector0';value=row['UB_to_GM_datas(KB)']
 if i<28:assert value not in ('NA','') and abs(Decimal(value)*1024-(blocks[2*i]+blocks[2*i+1]))<=Decimal('0.000512')
 else:assert value in ('NA','')
result={'target':'unified-extra6/'+case,'status':'passed','device':'hidev NPU 0','correctness':'passed','historical_input_and_source_match':True,'runtime_kernel':basic['Op Name'],'dbi_requested_bytes':sum(blocks.values()),'output_logical_bytes':out['logical_bytes'],'per_vector_block_requested_bytes':dict(blocks),'capture_binary_sha256':sha(binary),'dbi_pc':[hex(x) for x in sorted(pcs)],'csv_pair_totals_match':True,'replay_mode':'application','scope':'application replay; requested UB to GM bytes, not physical DRAM writes'}
(p/'candidate-audit-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',case,sum(blocks.values()))
