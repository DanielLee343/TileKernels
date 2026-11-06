"""Run upstream batched scale-transpose test and capture its native launch."""
import argparse,base64,ctypes,hashlib,importlib,importlib.util,json,os,random,traceback
from pathlib import Path
ROOT=Path('/workspace/tilekernels-env-20261101/src/TileKernels')
GROUP='quant_batched_transpose_weight_sf'

def digest_tensor(t,torch):
    if t is None:return None
    h=hashlib.sha256();x=t.detach().contiguous().view(-1)
    for off in range(0,x.numel(),1_000_000):h.update(x[off:off+1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'sha256':h.hexdigest()}

def run(group,params,stage,record):
    if group!=GROUP or stage not in ('prepare','default') or set(params)!={'block_size','weight_configs'}:
        raise ValueError('invalid group, stage, or original case parameters')
    import torch
    import torch_npu
    import tile_kernels
    from tile_kernels.rand import set_seed
    torch.set_num_threads(min(8,os.cpu_count() or 1));torch.npu.set_device(0);random.seed(42);set_seed(42)
    mod=importlib.import_module('tile_kernels.quant.batched_transpose_weight_sf_asc')
    orig_factory=mod.get_batched_transpose_weight_sf_kernel_asc
    orig_api=tile_kernels.quant.batched_transpose_weight_sf
    state={'matched':0,'stage':stage,'group':group,'params':params,'range':'quant_target'}
    try:
        def api_proxy(sf,block_size,transpose_sf1s,outs):
            if 'source_sf' not in state:
                state['source_sf']=[digest_tensor(t,torch) for t in sf]
                state['transpose_sf1s']=list(transpose_sf1s)
            return orig_api(sf,block_size,transpose_sf1s,outs)
        tile_kernels.quant.batched_transpose_weight_sf=api_proxy
        def factory_proxy(*args,**kwargs):
            kernel=orig_factory(*args,**kwargs)
            if state['matched']:return kernel
            class Proxy:
                def __call__(self,*tensors):
                    if state['matched']:return kernel(*tensors)
                    if len(tensors)!=4:raise ValueError('unexpected transpose kernel call')
                    state['matched']=1;symbol=str(kernel.prim_func.attrs['global_symbol'])
                    # ptrs contains process-specific addresses; the semantic input SF
                    # content, descriptor arrays and scalar task count are recorded.
                    state.update(symbol=symbol,runtime_kernel=symbol+'_kernel',
                        source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                        inputs=state['source_sf']+[digest_tensor(tensors[0],torch),digest_tensor(tensors[1],torch)],
                        scalar_inputs={'num_tasks':int(tensors[3]),'transpose_sf1s':state['transpose_sf1s']})
                    if stage=='default':
                        for _ in range(5):kernel(*tensors)
                        torch.npu.synchronize()
                        api=ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
                        start,end=api.mstxRangeStartA,api.mstxRangeEnd
                        start.argtypes,start.restype=[ctypes.c_char_p,ctypes.c_void_p],ctypes.c_uint64
                        end.argtypes,end.restype=[ctypes.c_uint64],None
                        stream=ctypes.c_void_p(int(torch.npu.current_stream().npu_stream));handle=start(b'quant_target',stream)
                        try:out=kernel(*tensors)
                        finally:end(handle)
                        torch.npu.synchronize();return out
                    return kernel(*tensors)
            return Proxy()
        mod.get_batched_transpose_weight_sf_kernel_asc=factory_proxy
        spec=importlib.util.spec_from_file_location('_profile_upstream_transpose',ROOT/'tests/quant/test_batched_transpose_weight_sf.py')
        test=importlib.util.module_from_spec(spec);spec.loader.exec_module(test)
        test.test_batched_transpose_weight_sf(params['block_size'],[tuple(c) for c in params['weight_configs']])
        assert state['matched']==1,'target native call missing';state['status']='passed'
    except BaseException:
        state.update(status='failed',error=traceback.format_exc());raise
    finally:
        tile_kernels.quant.batched_transpose_weight_sf=orig_api
        mod.get_batched_transpose_weight_sf_kernel_asc=orig_factory
        Path(record).write_text(json.dumps(state,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('group',choices=[GROUP]);p.add_argument('params_b64');p.add_argument('stage',choices=['prepare','default']);p.add_argument('record');a=p.parse_args()
    run(a.group,json.loads(base64.urlsafe_b64decode(a.params_b64.encode())),a.stage,a.record)
