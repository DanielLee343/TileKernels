"""Bind a new replay to historical inputs/source and inspect its exact binary."""
import csv,hashlib,json,re,subprocess,sys
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');case,attempt=sys.argv[1:];assert case in ('head-fp32-1001','head-fp32-1024') and re.fullmatch(r'attempt-\d+',attempt)
p=root/'early-head-batch-runs-20261111'/case/'hidev-npu0'/attempt/'detail';old=json.loads((p/'provenance/historical-default.json').read_text());assert old['status']=='passed'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest();assert sha(p/'provenance/historical-default-kernel.cpp')==old['source_sha256'];records=[]
for f in sorted(p.glob('application-*.json')):
 a=json.loads(f.read_text());pid=f.stem.removeprefix('application-');sf=p/('generated-kernel-'+pid+'.cpp');assert pid.isdigit() and a['status']=='passed' and a['inputs']==old['inputs'] and a['post_reference_mismatch_elements']==0
 assert a['runtime_kernel']=='mhc_head_compute_mix_fwd_asc_kernel' and a['source_sha256']==sha(sf)
 text=sf.read_text();new=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels-private\/';previous=r'\/workspace\/tilekernels-env-20261101\/src\/TileKernels\/'
 normalized=hashlib.sha256(text.replace(new,previous).encode()).hexdigest();assert a['source_sha256']==old['source_sha256'] or (new in text and normalized==old['source_sha256'])
 assert a['output']['shape']==old['output']['shape'] and a['output']['dtype']==old['output']['dtype'];records.append({'pid':pid,'application':f.name,'application_sha256':sha(f),'source':sf.name,'source_sha256':sha(sf)})
assert len(records)>=2
monitor=json.loads((p/'monitor-summary.json').read_text());assert monitor['status']=='passed' and monitor['max_seconds_between_successful_queries']<=3
op,=list((p/'capture').rglob('OpBasicInfo.csv'))
with op.open(encoding='utf-8-sig',newline='') as f:basic,=csv.DictReader(f)
assert (basic['Op Name'],basic['Op Type'],basic['Block Dim'],basic['Device Id'])==('mhc_head_compute_mix_fwd_asc_kernel','vector','56','0')
binary=op.parent/'dump/aicore_binary.o';bsha=sha(binary);assert any(x.startswith(bsha+' ') and x.rstrip().endswith('/kernel.aibin') for x in (p/'cache-sha256.txt').read_text().splitlines())
source=(p/records[0]['source']).read_text();assert '__simt_vf__' in source and 'output_mix[' in source and not re.search(r'asc_copy_ub2gm|copy_ubuf_to_gm',source,re.I)
isa=subprocess.check_output(['/workspace/tilekernels-env-20261101/cann/cann-9.2.1/tools/bisheng_compiler/bin/llvm-objdump','-d',str(binary)],text=True);(p/'device-kernel.isa').write_text(isa)
assert not re.search(r'MOV_UB_TO_OUT|UBUF_TO_GM',isa,re.I) and re.search(r'\bSTG\.',isa)
log=(p/'profile.log').read_text(errors='replace');assert not any('DBI record core:' in x and 'dst:(type:GM;' in x and 'src:(type:UB;' in x for x in log.splitlines())
result={'target':'early/'+case,'status':'aiv_ub_to_gm_not_applicable','device':'hidev NPU 0','correctness':'passed','historical_input_and_source_match':True,'capture_binary_sha256':bsha,'application_processes':len(records),'application_records':records,'evidence':'new captured source and device ISA have no UB-to-GM move; SIMT STG exists','scope':'new application replay only; SIMT writes GM directly; not zero total GM traffic; historical original binary was not available','replay_mode':'application'}
(p/'audit-result.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',case,result['status'])
