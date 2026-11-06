"""A/B device runner. No device is contacted until CLI invocation on target host."""
import argparse,csv,datetime,decimal,hashlib,json,math,os,pathlib,subprocess,sys,time,traceback
ROOT=pathlib.Path(__file__).resolve().parent
CASESET=('I0','I16')
def strides(case):
 if case not in CASESET: raise ValueError(case)
 return (4096 if case=='I0' else 4112,4096)
SOURCE='49f59118eb7c7718c297c38f88f7d5dc441916500ca537464a0d86afbfdd2e60'
BINARY='a63c65a404e8c6918260b8f231d9a447e9b0fc57e2d264a8e9b72373ac712afc'
HOST='976a298b192ee6c9a209e067527496b00768f63890d276b25fc89384eb80a926'
INPUTS=['de4bacfab422cd53119861129b486bde426e790d8c26a34fda50671ceef694fd','98b7decd8bbb5d6283b774f82fa5a7a730ae01b1d043fff68d3c7919f3b4d318']
COMMIT='c1cf914a82e6901c679445f872051ce44ac2cc63'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):
 tmp=p.with_suffix(p.suffix+'.tmp'); tmp.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n',encoding='utf-8'); tmp.replace(p)
def command(argv,log,env=None):
 t=time.monotonic(); start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with log.open('w',encoding='utf-8') as f:
  try: code=subprocess.run(argv,stdout=f,stderr=subprocess.STDOUT,env=env,timeout=900).returncode
  except BaseException:
   f.write('\nInterrupted or timed out; see status.json\n'); raise
 return {'argv':argv,'returncode':code,'start_utc':start,'seconds':time.monotonic()-t}
def environment(out):
 assert os.environ.get('ASCEND_RT_VISIBLE_DEVICES')=='5'
 assert pathlib.Path(os.environ['ASCEND_HOME_PATH']).resolve()==pathlib.Path('/home/pkg/cann920/cann-9.2.0')
 repo='/data2/lyuze/tilekernels-cann920-20261106/src/TileKernels'
 assert subprocess.check_output(['git','-C',repo,'rev-parse','HEAD'],text=True).strip()==COMMIT
 assert not subprocess.check_output(['git','-C',repo,'status','--porcelain'],text=True).strip()
 board=subprocess.check_output(['npu-smi','info','-t','board','-i','5'],text=True); assert 'Ascend950PR' in board and '0000:E1:00.0' in board
 version=subprocess.check_output(['msprof','op','--version'],text=True,stderr=subprocess.STDOUT); assert '26.2.0 (884ac969494a186a9c63ac45c4c39ad7289b3215)' in version
 save(out/'environment.json',{'board':board,'msprof_op':version,'cann':os.environ['ASCEND_HOME_PATH'],'visible':'5','repo_commit':COMMIT,'runner_sha256':digest(pathlib.Path(__file__)),'wrapper_sha256':digest(ROOT/'rms_wrapper.py'),'reference_sha256':digest(ROOT/'frozen'/'bridge-rmsnorm.py'),'input_helper_sha256':digest(ROOT/'frozen'/'bridge-inputs.py')})
def process_snapshot(path):
 text=subprocess.check_output(['npu-smi','info','-t','proc-mem','-i','5'],text=True); path.write_text(text,encoding='utf-8'); return 'No process in device.' in text
def verify_record(rec,case):
 assert rec['status']=='passed' and rec['input_hashes']==INPUTS and rec['shape']==[128,4096] and rec['dtype']=='torch.bfloat16'
 stride,out=strides(case)
 assert rec['input_stride']==[stride,1] and rec['output_stride']==[out,1] and rec['output_shape']==[128,4096]
 assert len(rec['output_sha256'])==64
 assert rec['input_mod128']==0 and rec['output_mod128']==0
 for name,shape,stride_expected in [('input',rec['shape'],rec['input_stride']),('output',rec['output_shape'],rec['output_stride']),('weight',[4096],[1])]:
  a=rec['allocations'][name]; assert a['shape']==shape and a['stride']==stride_expected
  assert a['element_bytes']==2 and a['address']>0 and a['backing_address']>0 and a['backing_bytes']>0
  end=a['address']+2*(1+sum((n-1)*s for n,s in zip(shape,stride_expected)))
  assert a['backing_address']<=a['address']<end<=a['backing_address']+a['backing_bytes']
 assert all(rec['allocations'][name]['address']%128==0 for name in ('input','output','weight'))
 assert rec['runtime_kernel']=='norm_forward_kernel_kernel'
 assert rec['generated_source_sha256']==SOURCE and rec['device_binary_sha256']==BINARY and rec['host_binary_sha256']==HOST
 assert rec['checked']==524288 and rec['mismatch']==0 and all(rec[x] for x in ('guards_ok','all_written','input_unchanged','weight_unchanged'))
def one(root,case,stage,ordinal):
 folder=root/f'{ordinal:02d}-{case}'; folder.mkdir(); status={'case':case,'phase':stage,'status':'started'}; save(folder/'status.json',status)
 try:
  status['idle_before']=process_snapshot(folder/'device-before.txt'); assert status['idle_before'], 'device busy before execution'
  env=dict(os.environ,TILELANG_CACHE_DIR=str(root/'cache'/case)); wrapper=[sys.executable,'-B',str(ROOT/'rms_wrapper.py'),case]
  if stage=='default':
   single=folder/'single'; single.mkdir()
   status['single_command']=command(wrapper+['prepare',str(single)],single/'execution.log',env)
   assert status['single_command']['returncode']==0
   verify_record(json.loads((single/'prepare.json').read_text()),case)
   status['idle_after_single']=process_snapshot(folder/'device-after-single.txt'); assert status['idle_after_single'], 'device busy after independent single check'
  cmd=wrapper+['prepare' if stage=='gate' else 'default',str(folder)]
  if stage=='default': cmd=['msprof','op',f'--output={folder / "capture"}','--aic-metrics=Default','--replay-mode=kernel','--mstx=true','--mstx-include=cold_call','--kernel-name=norm_forward_kernel_kernel','--launch-count=1','--warm-up=5']+cmd
  status['command']=command(cmd,folder/'execution.log',env); assert status['command']['returncode']==0
  rec=json.loads((folder/('prepare.json' if stage=='gate' else 'default.json')).read_text()); verify_record(rec,case)
  if stage=='default': status['metrics']=verify_capture(folder/'capture')
  status['idle_after']=process_snapshot(folder/'device-after.txt'); status['status']='passed' if status['idle_after'] else 'interference_possible'
 except BaseException as e:
  status['status']='interrupted' if isinstance(e,KeyboardInterrupt) else 'failed'; status['error']=traceback.format_exc(); raise
 finally:
  if (folder/'capture').exists(): save(folder/'capture-manifest.json',{str(p.relative_to(folder/'capture')):digest(p) for p in sorted((folder/'capture').rglob('*')) if p.is_file()})
  save(folder/'status.json',status)
 return status

def verify_capture(capture):
 def unique(name):
  found=list(capture.rglob(name)); assert len(found)==1,(name,found); return found[0]
 def rows(path):
  with path.open(newline='',encoding='utf-8-sig') as f: return list(csv.DictReader(f))
 basic,=rows(unique('OpBasicInfo.csv')); assert basic['Op Name']=='norm_forward_kernel_kernel' and basic['Op Type']=='vector' and int(basic['Block Dim'])==56 and basic['Device Id']=='5'
 assert digest(unique('aicore_binary.o'))==BINARY
 memory=rows(unique('Memory.csv')); pipe=rows(unique('PipeUtilization.csv'))
 def index(data):
  d={(r['block_id'],r['sub_block_id']):r for r in data}; assert len(d)==len(data)==56 and set(d)=={(str(i),'vector0') for i in range(56)}; return d
 m=index(memory); p=index(pipe); assert set(m)==set(p)
 totals={}
 for key,fields in ((m,('write_main_memory_datas(KB)','GM_to_UB_datas(KB)','aiv_mte2_instructions')),(p,('aiv_time(us)','aiv_mte2_time(us)','aiv_vec_time(us)'))):
  for field in fields:
   vals=[decimal.Decimal(r[field]) for r in key.values()]; assert all(v.is_finite() and v>=0 for v in vals); totals[field]=str(sum(vals))
 totals['write_bytes']=str(decimal.Decimal(totals['write_main_memory_datas(KB)'])*1024)
 return {'totals':totals,'frequency':basic['Current Freq']}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--run-root',type=pathlib.Path,required=True); args=ap.parse_args(); root=args.run_root.resolve(); root.mkdir(parents=True,exist_ok=False)
 environment(root)
 statuses=[]
 for i,case in enumerate(CASESET,1): statuses.append(one(root,case,'default',i))
 records=[json.loads((root/f'{i:02d}-{case}'/'default.json').read_text()) for i,case in enumerate(CASESET,1)]
 assert records[0]['input_hashes']==records[1]['input_hashes']
 assert records[0]['output_sha256']==records[1]['output_sha256'], 'outputs differ; retain records and investigate'
 a,b=[s['metrics']['totals'] for s in statuses]
 n_equal=decimal.Decimal(a['aiv_mte2_instructions'])==decimal.Decimal(b['aiv_mte2_instructions'])
 g_different=decimal.Decimal(a['GM_to_UB_datas(KB)'])!=decimal.Decimal(b['GM_to_UB_datas(KB)'])
 save(root/'pilot-result.json',{'n_equal':n_equal,'g_different':g_different,'eligible_for_separate_repeat_design':n_equal and g_different and all(s['status']=='passed' for s in statuses),'statuses':[s['status'] for s in statuses]})
if __name__=='__main__': main()
