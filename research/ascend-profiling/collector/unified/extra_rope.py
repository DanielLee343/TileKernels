"""Capture one of the two in-place Q/K RoPE launches in the upstream 3D test."""
import argparse
import base64
import ctypes
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import traceback

ROOT=Path('/workspace/tilekernels-env-20261101/src/TileKernels')
RANGE='quant_target'


def tensor_hash(t,torch):
    if t is None:return None
    h=hashlib.sha256();x=t.detach().contiguous().view(-1)
    for off in range(0,x.numel(),1_000_000):h.update(x[off:off+1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'sha256':h.hexdigest()}


def run(group,params,stage,record):
    if group not in ('rotary_embedding_q','rotary_embedding_k') or stage not in ('prepare','default'):
        raise ValueError('invalid group or stage')
    expected_keys={'nheads','dim','dtype','interleaved','conjugate','head_split','seqlen','seqlen_total'}
    if set(params)!=expected_keys or params['seqlen']!=2001 or params['seqlen_total']!=8192:
        raise ValueError('unsupported original plan parameters')
    import torch
    import torch_npu
    module=importlib.import_module('tile_kernels.transform.rope_asc');original=module.get_rope_kernel_asc
    wanted=0 if group.endswith('_q') else 1
    state={'matched':0,'stage':stage,'group':group,'params':params,'target_role':'query' if wanted==0 else 'key',
           'profiler_replay_state':'unverified' if stage=='default' else 'not_applicable',
           'output_semantics':'target input tensor is updated in place','native_launch_seen':0}
    try:
        torch.set_num_threads(min(8,os.cpu_count() or 1));torch.npu.set_device(0)
        def replacement(*args,**kwargs):
            kernel=original(*args,**kwargs)
            class Proxy:
                def __call__(self,*tensors):
                    i=state['native_launch_seen'];state['native_launch_seen']+=1
                    if i!=wanted:return kernel(*tensors)
                    state['matched']+=1
                    symbol=str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol,runtime_kernel=symbol+'_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[tensor_hash(t,torch) for t in tensors[:3]],
                                 scalar_inputs={'seqlen_offset':int(tensors[3])})
                    if stage=='default':
                        original_x=tensors[0]
                        temp=torch.empty_strided(original_x.shape,original_x.stride(),dtype=original_x.dtype,device=original_x.device)
                        temp.copy_(original_x)
                        for _ in range(5):kernel(temp,*tensors[1:])
                        torch.npu.synchronize()
                        api=ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
                        start,end=api.mstxRangeStartA,api.mstxRangeEnd
                        start.argtypes,start.restype=[ctypes.c_char_p,ctypes.c_void_p],ctypes.c_uint64
                        end.argtypes,end.restype=[ctypes.c_uint64],None
                        stream=ctypes.c_void_p(int(torch.npu.current_stream().npu_stream));handle=start(RANGE.encode(),stream)
                        try:out=kernel(*tensors)
                        finally:end(handle)
                        torch.npu.synchronize();return out
                    return kernel(*tensors)
            return Proxy()
        module.get_rope_kernel_asc=replacement
        test=ROOT/'tests/transform/test_rope.py';spec=importlib.util.spec_from_file_location('_profile_upstream_rope',test)
        x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
        dtype={'bf16':torch.bfloat16,'fp32':torch.float32}[params['dtype']]
        x.test_rotary_embedding_3d(params['nheads'],params['dim'],params['interleaved'],params['conjugate'],dtype,params['head_split'])
        assert state['matched']==1 and state['native_launch_seen']==2,'expected Q and K native calls'
        state['status']='passed'
    except BaseException:
        state.update(status='failed',error=traceback.format_exc());raise
    finally:
        module.get_rope_kernel_asc=original
        Path(record).write_text(json.dumps(state,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('group',choices=['rotary_embedding_q','rotary_embedding_k']);p.add_argument('params_b64');p.add_argument('stage',choices=['prepare','default']);p.add_argument('record');a=p.parse_args()
    run(a.group,json.loads(base64.urlsafe_b64decode(a.params_b64.encode())),a.stage,a.record)
