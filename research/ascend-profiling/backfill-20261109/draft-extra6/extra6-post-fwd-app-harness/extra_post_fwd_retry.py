"""Run the upstream mHC post test and capture its forward kernel."""
import argparse,base64,ctypes,hashlib,importlib,importlib.util,json,os,random,traceback
from pathlib import Path
ROOT=Path(os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4])))
GROUP='mhc_post_fwd'

def tensor_hash(t,torch):
    if t is None:return None
    h=hashlib.sha256();x=t.detach().contiguous().view(-1)
    for off in range(0,x.numel(),1_000_000):h.update(x[off:off+1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'sha256':h.hexdigest()}

def run(group,params,stage,record):
    record = Path(record).with_name('application-' + str(os.getpid()) + '.json')
    if group!=GROUP or stage not in ('prepare','default') or set(params)!={'n0','n1','hidden','mhc_mult'} or params['mhc_mult']!=4:
        raise ValueError('invalid group, stage or original parameters')
    import torch
    import torch_npu
    from tile_kernels.rand import set_seed
    torch.set_num_threads(min(8,os.cpu_count() or 1));torch.npu.set_device(0);random.seed(42);set_seed(42)
    mod=importlib.import_module('tile_kernels.mhc.post_asc');orig=mod.mhc_post_fwd_asc
    state={'matched':0,'stage':stage,'group':group,'params':params,'capture_scope':'post forward native kernel only'}
    try:
        def native_proxy(*args,**kwargs):
            if state['matched']:return orig(*args,**kwargs)
            kernel=orig.compile(*args,**kwargs);symbol=str(kernel.prim_func.attrs['global_symbol'])
            state.update(matched=1,symbol=symbol,runtime_kernel=symbol+'_kernel',
                source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                inputs=[tensor_hash(t,torch) for t in args[:4]],native_kwargs=kwargs)
            if stage=='default':
                meta=[]
                for t in args:
                    if isinstance(t,torch.Tensor):meta.append({'address':hex(t.data_ptr()),'device':str(t.device),'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'element_size':t.element_size(),'logical_bytes':t.numel()*t.element_size()})
                    else:meta.append(None)
                Path(record).with_name('tensor-addresses-'+str(os.getpid())+'.json').write_text(json.dumps(meta,indent=2)+'\n')
                Path(record).with_name('generated-kernel-'+str(os.getpid())+'.cpp').write_text(kernel.get_kernel_source())
                for _ in range(5):orig(*args,**kwargs)
                torch.npu.synchronize()
                api=ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
                start,end=api.mstxRangeStartA,api.mstxRangeEnd
                start.argtypes,start.restype=[ctypes.c_char_p,ctypes.c_void_p],ctypes.c_uint64
                end.argtypes,end.restype=[ctypes.c_uint64],None
                stream=ctypes.c_void_p(int(torch.npu.current_stream().npu_stream));handle=start(b'quant_target',stream)
                try:out=orig(*args,**kwargs)
                finally:end(handle)
                torch.npu.synchronize();return out
            return orig(*args,**kwargs)
        mod.mhc_post_fwd_asc=native_proxy
        spec=importlib.util.spec_from_file_location('_profile_upstream_post',ROOT/'tests/mhc/test_post.py')
        test=importlib.util.module_from_spec(spec);spec.loader.exec_module(test)
        test.test_mhc_post_comprehensive(params['n0'],params['n1'],params['hidden'])
        assert state['matched']==1,'target native launch missing';state['status']='passed'
    except BaseException:
        state.update(status='failed',error=traceback.format_exc());raise
    finally:
        mod.mhc_post_fwd_asc=orig
        Path(record).write_text(json.dumps(state,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('group',choices=[GROUP]);p.add_argument('params_b64');p.add_argument('stage',choices=['prepare','default']);p.add_argument('record');a=p.parse_args()
    run(a.group,json.loads(base64.urlsafe_b64decode(a.params_b64.encode())),a.stage,a.record)
