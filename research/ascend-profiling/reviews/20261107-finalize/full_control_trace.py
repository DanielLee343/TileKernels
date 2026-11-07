"""Trace adapter entry before its marked launch; never use instrumented timing."""
import ctypes
import json
import os
from pathlib import Path
import runpy
import sys

FAMILY = os.environ['REPLAY_WATCH_FAMILY']
OUT = Path(os.environ['REPLAY_WATCH_DIR'])
ADAPTER = Path(sys.argv[1]).resolve()
INDICES = {
    'engram_grad_w_reduce': (3,4),
    'engram_sinkhorn_momentum_update': (1,),
    'engram_sinkhorn_step': (1,),
    'mhc_fn_normw_merge_bwd': (3,4),
    'mhc_pre_apply_mix_bwd': (3,),
    'moe_topk_gate_forward': (9,),
    'quant_norm_backward': (7,),
    'quant_per_token_cast_and_cast_back': (0,),
    'rotary_embedding': (0,),
}

def register(frame):
    import torch
    tensors=frame.f_locals.get('tensors',frame.f_locals.get('args'))
    if not isinstance(tensors,tuple):
        raise RuntimeError('target native tensor arguments are unavailable')
    torch.npu.synchronize()
    library=ctypes.CDLL(None)
    copy=library.aclrtMemcpy
    copy.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int]
    copy.restype=ctypes.c_int
    rows=[];metadata=[];index=0
    for tensor_index in INDICES[FAMILY]:
        t=tensors[tensor_index]
        if t is None or not isinstance(t,torch.Tensor) or t.numel()==0:
            raise RuntimeError(f'missing mutable tensor {tensor_index}')
        if any(s<0 for s in t.stride()):
            raise RuntimeError('negative strides are unsupported')
        span=(1+sum((d-1)*s for d,s in zip(t.shape,t.stride()))) * t.element_size()
        # These two fixed-routing buffers are small. Check every byte, including
        # any stride gaps, on every observed restore rather than sampling.
        if FAMILY=='moe_topk_gate_forward' and span<=65536:
            length=span;offsets=[0]
        else:
            length=min(4096,span)
            offsets=sorted(set((0,max(0,(span-length)//2),span-length)))
        for offset in offsets:
            b=ctypes.create_string_buffer(length)
            address=t.data_ptr()+offset
            rc=copy(b,length,address,length,2)
            if rc: raise RuntimeError(f'initial device-to-host copy failed: {rc}')
            baseline=OUT/f'baseline-{index}.bin'
            baseline.write_bytes(b.raw)
            rows.append(f'{index} {address:x} {length} {baseline}')
            metadata.append({'index':index,'tensor_index':tensor_index,'tensor_address':t.data_ptr(),'shape':list(t.shape),
              'stride':list(t.stride()),'dtype':str(t.dtype),'span_bytes':span,
              'sample_offset':offset,'sample_bytes':length})
            index+=1
    (OUT/'watch-config.txt').write_text('\n'.join(rows)+'\n')
    (OUT/'watch-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    os.environ['REPLAY_WATCH_CONFIG']=str(OUT/'watch-config.txt')
    os.environ['REPLAY_WATCH_LOG']=str(OUT/'watch.log')
    os.environ['REPLAY_WATCH_COVERAGE']=str(OUT/'coverage.log')

def trace(frame,event,arg):
    if frame.f_code.co_filename!=str(ADAPTER):
        return None
    if event=='line':
        line=SOURCE[frame.f_lineno-1]
        if ('handle = start(' in line or 'handle=start(' in line or
            'handle, end = range_factory(' in line):
            register(frame)
            sys.settrace(None)
            return None
    return trace

SOURCE=ADAPTER.read_text().splitlines()
sys.argv=[str(ADAPTER),*sys.argv[2:]]
sys.settrace(trace)
runpy.run_path(str(ADAPTER),run_name='__main__')
