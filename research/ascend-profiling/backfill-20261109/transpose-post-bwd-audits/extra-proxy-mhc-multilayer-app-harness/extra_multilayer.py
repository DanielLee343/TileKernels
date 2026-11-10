"""Capture the native multilayer kernel while preserving its live pointer tables."""
import argparse,base64,ctypes,hashlib,importlib,importlib.util,json,os,random,traceback
from pathlib import Path
ROOT=Path((os.environ['TILEKERNELS_ROOT'] if 'TILEKERNELS_ROOT' in os.environ else str(Path(__file__).resolve().parents[4])))
GROUP='mhc_multilayer_recompute'

def tensor_hash(t,torch):
    if t is None:return None
    h=hashlib.sha256();x=t.detach().contiguous().view(-1)
    for off in range(0,x.numel(),1_000_000):h.update(x[off:off+1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'sha256':h.hexdigest()}

def run(group,params,stage,record):
    record = Path(record).with_name('application-' + str(os.getpid()) + '.json')
    required={'num_layers','num_post','hidden','bs','seq','mhc_mult'}
    if group!=GROUP or stage not in ('prepare','default') or set(params)!=required:
        raise ValueError('invalid group, stage or plan parameters')
    if (params['bs'],params['seq'],params['mhc_mult'])!=(1,8192,4):
        raise ValueError('upstream correctness test has a different input contract')
    import torch
    import torch_npu
    from tile_kernels.rand import set_seed
    torch.set_num_threads(min(8,os.cpu_count() or 1));torch.npu.set_device(0);random.seed(42);set_seed(42)
    mod=importlib.import_module('tile_kernels.mhc.multilayer_recompute_asc');orig=mod.mhc_multilayer_recompute_asc
    state={'matched':0,'stage':stage,'group':group,'params':params,'capture_scope':'one native multilayer kernel; pointer-table construction and reference kernels excluded'}
    test=None;orig_test_api=None
    try:
        spec=importlib.util.spec_from_file_location('_profile_upstream_multilayer',ROOT/'tests/mhc/test_multilayer_recompute.py')
        test=importlib.util.module_from_spec(spec);spec.loader.exec_module(test);orig_test_api=test.mhc_multilayer_recompute
        def api_proxy(initial,pre,layer,post,comb,layer_out,residual_out):
            if 'semantic_inputs' in state:raise RuntimeError('more than one multilayer API invocation')
            state['semantic_inputs']=[tensor_hash(initial,torch)]+[tensor_hash(t,torch) for seq in (pre,layer,post,comb) for t in seq]
            if stage=='default':
                def describe(t):return {'address':hex(t.data_ptr()),'device':str(t.device),'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'element_size':t.element_size(),'logical_bytes':t.numel()*t.element_size()}
                semantic={'initial':describe(initial),'pre':[describe(t) for t in pre],'layer':[describe(t) for t in layer],'post':[describe(t) for t in post],'comb':[describe(t) for t in comb],'layer_out':[describe(t) for t in layer_out],'residual_out':[describe(t) for t in residual_out]}
                Path(record).with_name('semantic-addresses-' + str(os.getpid()) + '.json').write_text(json.dumps(semantic,indent=2)+'\n')
            state['list_lengths']=[len(pre),len(layer),len(post),len(comb),len(layer_out),len(residual_out)]
            return orig_test_api(initial,pre,layer,post,comb,layer_out,residual_out)
        test.mhc_multilayer_recompute=api_proxy
        def native_proxy(*args,**kwargs):
            if state['matched']:raise RuntimeError('more than one target native launch')
            kernel=orig.compile(*args,**kwargs);symbol=str(kernel.prim_func.attrs['global_symbol'])
            if stage=='default':
                meta=[]
                for t in args:
                    if isinstance(t,torch.Tensor):meta.append({'address':hex(t.data_ptr()),'device':str(t.device),'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'element_size':t.element_size(),'logical_bytes':t.numel()*t.element_size()})
                    else:meta.append(None)
                Path(record).with_name('tensor-addresses-' + str(os.getpid()) + '.json').write_text(json.dumps(meta,indent=2)+'\n')
                Path(record).with_name('generated-kernel-' + str(os.getpid()) + '.cpp').write_text(kernel.get_kernel_source())
                for i,t in enumerate(args[1:]):
                    Path(record).with_name('pointer-table-' + str(i) + '-' + str(os.getpid()) + '.bin').write_bytes(t.detach().contiguous().cpu().numpy().tobytes())
            state.update(matched=1,symbol=symbol,runtime_kernel=symbol+'_kernel',
                source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                inputs=state['semantic_inputs'],native_kwargs=kwargs,
                pointer_table_lengths=[int(t.numel()) for t in args[1:]])
            if stage=='default':
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
        mod.mhc_multilayer_recompute_asc=native_proxy
        test.test_mhc_multilayer_recompute_correctness(params['num_layers'],params['num_post'],params['hidden'])
        assert state['matched']==1,'target native launch missing';state['status']='passed'
    except BaseException:
        state.update(status='failed',error=traceback.format_exc());raise
    finally:
        mod.mhc_multilayer_recompute_asc=orig
        if test is not None and orig_test_api is not None:test.mhc_multilayer_recompute=orig_test_api
        Path(record).write_text(json.dumps(state,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('group',choices=[GROUP]);p.add_argument('params_b64');p.add_argument('stage',choices=['prepare','default']);p.add_argument('record');a=p.parse_args()
    run(a.group,json.loads(base64.urlsafe_b64decode(a.params_b64.encode())),a.stage,a.record)
