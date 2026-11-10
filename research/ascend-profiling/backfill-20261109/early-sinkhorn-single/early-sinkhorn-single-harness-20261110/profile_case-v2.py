"""Native frozen call, full-shape checking, explicit L2 flush before counted calls."""
import argparse,ctypes,hashlib,json,os,sys,time,traceback
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'frozen'))
from inputs import make_arrays,to_torch,sha256

def save(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix('.tmp');t.write_text(json.dumps(v,indent=2)+'\n');t.replace(p)

def main():
 p=argparse.ArgumentParser();p.add_argument('--case-id',required=True);p.add_argument('--mode',choices=('prepare','launch'),required=True)
 p.add_argument('--result',type=Path,required=True);p.add_argument('--launches',type=int,default=1);p.add_argument('--flush-policy',choices=('hardware_api','profiler_replay'),default='profiler_replay');a=p.parse_args()
 a.result=a.result.parent/('process-'+str(os.getpid()))/'application.json'
 c=next(c for c in json.loads((ROOT/'selected_cases.json').read_text())['cases'] if c['id']==a.case_id)
 r={'case_id':c['id'],'case':c,'mode':a.mode,'status':'running','started_utc':datetime.now(timezone.utc).isoformat(),
    'wrapper_sha256':sha256(Path(__file__)),'input_generator_sha256':sha256(ROOT/'frozen/inputs.py'),
    'application_warmup_calls':5 if a.mode=='launch' else 0,'profiling_in_wrapper':False,
    'flush_policy':a.flush_policy,'cold_boundary':'application replay; profiler does not clear L2; Q and K have separate MSTX ranges',
    'flush_events':[],'target_calls':[]}
 save(a.result,r)
 try:
  import torch,torch_npu
  from tilelang import language as T
  from tile_kernels.config import get_num_vec_cores,get_token_alignment,is_ascend
  from tile_kernels.quant.common import get_cast_output_config
  assert is_ascend() and torch.npu.is_available();torch.npu.set_device(0);torch.set_num_threads(min(8,os.cpu_count() or 1))
  arrays=make_arrays(c);host=to_torch(arrays,c);r['input_sha256']=[hashlib.sha256(x.tobytes()).hexdigest() for x in arrays]
  tensors=[x.to('npu:0') for x in host]
  assert sum(x.numel()*x.element_size() for x in tensors)==c['logical_input_bytes']
  kernels=[];calls=[];native=[]
  def register(role,kernel,args,factory,kwargs):
   source=kernel.get_kernel_source();symbol=str(kernel.prim_func.attrs['global_symbol'])
   f=a.result.parent/f'{a.mode}-{role}-kernel.cpp';f.parent.mkdir(parents=True,exist_ok=True);f.write_text(source)
   native.append({'role':role,'global_symbol':symbol,'factory':factory,'kwargs':kwargs,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'source_file':str(f)})
   kernels.append(kernel);calls.append((kernel,args))
   values=[]
   for t in args:
    if isinstance(t,torch.Tensor):values.append({'address':hex(t.data_ptr()),'device':str(t.device),'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'element_size':t.element_size(),'logical_bytes':t.numel()*t.element_size()})
    else:values.append(None)
   r.setdefault('device_args',{})[role]=values
  if c['task']=='swiglu':
   from tile_kernels.quant.swiglu_forward_asc import get_swiglu_forward_kernel_asc
   x=tensors[0];out=torch.empty(c['output_shapes'][0],dtype=x.dtype,device=x.device)
   fmt='bf16' if x.dtype==torch.bfloat16 else 'fp32';config=get_cast_output_config(fmt,(1,1),False,False,False)
   kwargs=dict(hidden=x.shape[-1]//2,num_experts=0,alignment=get_token_alignment(),with_weight=False,with_routed_scaling=False,clamp_value=None,count_clamp=False,in_dtype=T.dtype(x.dtype),out_config=config,num_vec_cores=get_num_vec_cores())
   k=get_swiglu_forward_kernel_asc(**kwargs);register('single',k,[x,out,None,None,None,1.0,None],'tile_kernels.quant.swiglu_forward_asc.get_swiglu_forward_kernel_asc',{k:str(v) for k,v in kwargs.items()});outputs=(out,)
  elif c['task']=='sinkhorn':
   from tile_kernels.mhc.sinkhorn_asc import mhc_sinkhorn_fwd_asc as sinkhorn_factory
   x=tensors[0];out=torch.empty_like(x);args=[x,out]
   kwargs={'repeat':c['attrs']['iter_step'],'eps':c['attrs']['eps'],'token_block_size':4,'num_vec_cores':get_num_vec_cores()}
   kernel=sinkhorn_factory.compile(*args,**kwargs);_,kernel_args=sinkhorn_factory.func.parse_args(*args,**kwargs)
   register('single',kernel,list(kernel_args.values()),'tile_kernels.mhc.sinkhorn_asc.mhc_sinkhorn_fwd_asc',kwargs);outputs=(out,)
  elif c['task']=='rmsnorm':
   from tile_kernels.quant.norm_forward_asc import get_norm_forward_kernel_asc
   x,weight=tensors;out=torch.empty_like(x);batched=lambda t:t.unsqueeze(0) if x.ndim==2 else t
   fmt='bf16' if x.dtype==torch.bfloat16 else 'fp32';config=get_cast_output_config(fmt,(1,1),False,False,False)
   kwargs=dict(hidden=x.shape[-1],with_weight=True,with_residual=False,eps=c['attrs']['epsilon'],out_scale=1.0,x_dtype=T.dtype(x.dtype),out_config=config,with_out_bf16=False,with_rstd=False,num_vec_cores=get_num_vec_cores())
   k=get_norm_forward_kernel_asc(**kwargs);register('single',k,[batched(x),batched(out),None,None,weight,None,None,None],'tile_kernels.quant.norm_forward_asc.get_norm_forward_kernel_asc',{k:str(v) for k,v in kwargs.items()});outputs=(out,)
  else:
   from tile_kernels.transform.rope_asc import get_rope_kernel_asc
   q,k,cos,sin=tensors;cache=torch.cat((cos,sin),dim=-1).contiguous()
   for role,x in (('Q',q),('K',k)):
    kwargs=dict(dtype=T.dtype(x.dtype),positions_dtype=T.int32,nheads=x.shape[2],rotary_dim=x.shape[-1],has_position_tensor=False,interleaved=c['attrs']['rotaryMode']=='interleaved',conjugate=False,cos_sin_stride=cache.stride(0),x_stride_0=x.stride(1),x_stride_1=x.stride(2))
    kernel=get_rope_kernel_asc(**kwargs);register(role,kernel,[x,cache,None,0],'tile_kernels.transform.rope_asc.get_rope_kernel_asc',{k:str(v) for k,v in kwargs.items()})
   outputs=(q,k)
  r['native']=native;r['native_roles']=[n['role'] for n in native];save(a.result,r)
  def launch():
   for kernel,args in calls:kernel(*args)
  def reset_inputs():
   if c['task']=='rope':
    tensors[0].copy_(host[0]);tensors[1].copy_(host[1])
  torch.npu.synchronize()
  if a.mode=='prepare':
   launch();torch.npu.synchronize()
   assert len(outputs)==len(c['output_shapes'])
   for x,s,d in zip(outputs,c['output_shapes'],c['output_dtypes']):assert list(x.shape)==s and x.dtype==getattr(torch,d)
   r['outputs']=[{'shape':list(x.shape),'dtype':str(x.dtype).removeprefix('torch.'),'elements':x.numel()} for x in outputs]
   from adapters import cann_reference
   metrics=[{'output':i,'checked_elements':0,'mismatch_elements':0,'max_abs_error':0.,'rtol':2**-7 if d=='bfloat16' else 2**-13,'atol':2e-3 if d=='bfloat16' else 2e-5} for i,d in enumerate(c['output_dtypes'])]
   def compare(actual,expected,i):
    m=metrics[i];assert actual.shape==expected.shape and actual.dtype==expected.dtype
    delta=(actual.double()-expected.double()).abs();m['checked_elements']+=actual.numel();m['mismatch_elements']+=int((~torch.isclose(actual,expected,rtol=m['rtol'],atol=m['atol'],equal_nan=False)).sum());m['max_abs_error']=max(m['max_abs_error'],float(delta.max()))
   if c['task']=='rope':
    for b in range(host[0].shape[0]):
     for s in range(0,host[0].shape[1],64):
      ins=[host[0][b:b+1,s:s+64],host[1][b:b+1,s:s+64],host[2][s:s+64],host[3][s:s+64]]
      ref=cann_reference(c,ins)
      for i,x in enumerate(outputs):compare(x[b:b+1,s:s+64].cpu(),ref[i],i)
   elif c['task']=='sinkhorn':
    for off in range(0,host[0].shape[0],256):compare(outputs[0][off:off+256].cpu(),cann_reference(c,[host[0][off:off+256]])[0],0)
   else:
    h=host[0].shape[-1];flat=host[0].reshape(-1,h);oflat=outputs[0].reshape(-1,outputs[0].shape[-1])
    for start in range(0,len(flat),256):
     ins=[flat[start:start+256]]+([host[1]] if c['task']=='rmsnorm' else [])
     compare(oflat[start:start+256].cpu(),cann_reference(c,ins)[0],0)
   r['correctness']={'status':'passed' if not any(m['mismatch_elements'] for m in metrics) else 'failed','scope':'all elements of all full-shape outputs; original frozen CANN CPU reference in row/token chunks; finite inputs, not full CANN benchmark contract','metrics':metrics}
  else:
   # Five full application calls precede collection. No device-wide L2 flush
   # occurs in this application-replay probe; Q and K use separate ranges.
   for _ in range(5):reset_inputs();launch()
   torch.npu.synchronize()
   lib=ctypes.CDLL('libascendcl.so');flush=lib.aclrtDeviceL2CacheFlush;flush.argtypes=[ctypes.c_void_p];flush.restype=ctypes.c_int
   mstx_path=Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'
   mstx=ctypes.CDLL(str(mstx_path));start_range=mstx.mstxRangeStartA;start_range.argtypes=[ctypes.c_char_p,ctypes.c_void_p];start_range.restype=ctypes.c_uint64
   end_range=mstx.mstxRangeEnd;end_range.argtypes=[ctypes.c_uint64];end_range.restype=None
   stream_ptr=int(torch.npu.current_stream().npu_stream)
   r['mstx_api']={'library':str(mstx_path),'start':'mstxRangeStartA','end':'mstxRangeEnd','stream_pointer':stream_ptr,'domain_api':False}
   for index in range(a.launches):
    reset_inputs();torch.npu.synchronize()
    if a.flush_policy=='hardware_api':
     begin=time.monotonic_ns();rc=int(flush(None));end=time.monotonic_ns()
     r['flush_events'].append({'call_index':index,'api':'aclrtDeviceL2CacheFlush','returncode':rc,'start_monotonic_ns':begin,'end_monotonic_ns':end,'outside_mstx_range':True})
     assert rc==0,f'L2 flush returned {rc}'
    else:
     r['flush_events'].append({'call_index':index,'api':'no profiler-managed L2 clear in application replay','returncode':None,'outside_mstx_range':True,'application_trace_cold':False})
    label='cold_call' if a.launches==1 else f'cold_call_{index}'
    if c['task'] == 'rope':
     for native_item,(kernel,args) in zip(native,calls):
      role=native_item['role'];handle=int(start_range(('early_'+role).encode(),ctypes.c_void_p(stream_ptr)))
      kernel(*args)
      end_range(handle)
    else:
     handle=int(start_range(label.encode(),ctypes.c_void_p(stream_ptr)))
     launch()
     end_range(handle)
    torch.npu.synchronize()
    r['target_calls'].append({'index':index,'mstx_range':None if c['task']=='rope' else label,'mstx_range_id':None if c['task']=='rope' else handle,'roles':r['native_roles'],'flush_index':index,'no_flush_between_roles':True,'actual_profile_ranges':['early_Q','early_K'] if c['task']=='rope' else [label]})
   if c['task']=='rope' and a.launches==1:
    from adapters import cann_reference
    checks=[{'role':role,'checked_elements':0,'mismatch_elements':0,'max_abs_error':0.} for role in ('Q','K')]
    for b in range(host[0].shape[0]):
     for s in range(0,host[0].shape[1],64):
      ref=cann_reference(c,[host[0][b:b+1,s:s+64],host[1][b:b+1,s:s+64],host[2][s:s+64],host[3][s:s+64]])
      for i,x in enumerate(outputs):
       actual=x[b:b+1,s:s+64].cpu();item=checks[i];rtol,atol=(2**-7,2e-3) if x.dtype==torch.bfloat16 else (2**-13,2e-5)
       item['checked_elements']+=actual.numel();item['mismatch_elements']+=int((~torch.isclose(actual,ref[i],rtol=rtol,atol=atol,equal_nan=False)).sum());item['max_abs_error']=max(item['max_abs_error'],float((actual.double()-ref[i].double()).abs().max()))
    r['post_replay_output_check']={'status':'passed' if not any(v['mismatch_elements'] for v in checks) else 'failed','scope':'all original Q and K elements compared against one-call CANN reference after range replay; detects repeated in-place rotation','metrics':checks}
   if c['task']=='sinkhorn' and a.launches==1:
    from adapters import cann_reference
    checked=0;bad=0;maximum=0.0
    for off in range(0,host[0].shape[0],256):
     expected=cann_reference(c,[host[0][off:off+256]])[0];actual=outputs[0][off:off+256].cpu()
     assert actual.shape==expected.shape and actual.dtype==expected.dtype
     checked+=actual.numel();bad+=int((~torch.isclose(actual,expected,rtol=2**-13,atol=2e-5,equal_nan=False)).sum());maximum=max(maximum,float((actual.double()-expected.double()).abs().max()))
    r['post_replay_output_check']={'status':'passed' if not bad else 'failed','checked_elements':checked,'mismatch_elements':bad,'max_abs_error':maximum,'scope':'all output elements compared with frozen CANN CPU reference after the target call'}
    assert not bad,'post-replay reference failed'
   if c['task']=='rmsnorm' and a.launches==1:
    from adapters import cann_reference
    inp=host[0].reshape(-1,host[0].shape[-1]);out=outputs[0].reshape(-1,outputs[0].shape[-1]);checked=0;bad=0;maximum=0.0
    for off in range(0,len(inp),256):
     expected=cann_reference(c,[inp[off:off+256],host[1]])[0];actual=out[off:off+256].cpu();rtol,atol=(2**-7,2e-3) if actual.dtype==torch.bfloat16 else (2**-13,2e-5)
     assert actual.shape==expected.shape and actual.dtype==expected.dtype
     checked+=actual.numel();bad+=int((~torch.isclose(actual,expected,rtol=rtol,atol=atol,equal_nan=False)).sum());maximum=max(maximum,float((actual.double()-expected.double()).abs().max()))
    r['post_replay_output_check']={'status':'passed' if not bad else 'failed','checked_elements':checked,'mismatch_elements':bad,'max_abs_error':maximum,'scope':'all output elements compared with frozen CANN CPU reference after the target call'}
    assert not bad,'post-replay reference failed'
   r['correctness']={'status':'separate_prepare_process','scope':'no reference work in target range'}
  r['status']='passed'
 except Exception as e:
  r.update(status='failed',error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());traceback.print_exc()
 r['finished_utc']=datetime.now(timezone.utc).isoformat();save(a.result,r)
 print(json.dumps({'case_id':c['id'],'mode':a.mode,'status':r['status'],'correctness':r.get('correctness'),'flush_events':r['flush_events']},ensure_ascii=False),flush=True)
 return 0 if r['status']=='passed' else 1
if __name__=='__main__':sys.exit(main())
