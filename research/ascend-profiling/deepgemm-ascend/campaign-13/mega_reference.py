"""Single-rank MegaMoE reference assembled from upstream GEMM and SwiGLU.

This is for a separately documented 28-core port experiment, not a claim that
the unmodified 32-core MegaMoE implementation ran on this board.
"""
import importlib.util
from pathlib import Path
import sys


def reference(case, source):
    import torch
    import deep_gemm
    from test_mega_moe import make_npu_fp4

    source=Path(source)
    ops_dir=source/'third-party/tilelang_ops'
    if 'tilelang_ops' not in sys.modules:
        spec=importlib.util.spec_from_file_location('tilelang_ops',ops_dir/'swiglu_apply_weight_to_fp8.py',
                                                  submodule_search_locations=[str(ops_dir)])
        module=importlib.util.module_from_spec(spec);sys.modules['tilelang_ops']=module;spec.loader.exec_module(module)
    swiglu=sys.modules['tilelang_ops'].swiglu_apply_weight_to_fp8
    buf=case.buffer
    tokens=case.y.shape[0];hidden=buf.hidden;intermediate=buf.intermediate_hidden;experts=buf.num_experts
    l1=make_npu_fp4((experts,2*intermediate,hidden),20000)
    l2=make_npu_fp4((experts,hidden,intermediate),21000)
    route_idx=case.topk_idx;route_weights=case.topk_weights
    result=torch.zeros((tokens,hidden),dtype=torch.float32,device='npu')
    for expert in range(experts):
        pairs=torch.nonzero(route_idx==expert,as_tuple=False)
        if not pairs.numel():continue
        rows=pairs[:,0].long();slots=pairs[:,1].long()
        xbytes=buf.x[:tokens].view(torch.uint8).index_select(0,rows).contiguous()
        x=xbytes.view(torch.float8_e4m3fn)
        sf=buf.x_sf[:tokens].index_select(0,rows).contiguous()
        mid=torch.empty((rows.numel(),2*intermediate),dtype=torch.bfloat16,device='npu')
        deep_gemm.fp8_fp4_gemm_nt((x,sf),(l1[0][expert],l1[1][expert]),mid,recipe=(1,1,32))
        weights=route_weights[rows,slots].contiguous()
        activation=swiglu(mid,topk_weights=weights,clamp_value=case.activation_clamp)
        partial=torch.empty((rows.numel(),hidden),dtype=torch.bfloat16,device='npu')
        deep_gemm.fp8_fp4_gemm_nt(activation,(l2[0][expert],l2[1][expert]),partial,recipe=(1,1,32))
        result.index_add_(0,rows,partial.float())
    return result.to(torch.bfloat16)
