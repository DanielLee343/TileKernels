"""One frozen SwiGLU case; no nested profiler, no change to kernel or models."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import time

import torch
import torch_npu
from tilelang import language as T
from tile_kernels.config import get_num_vec_cores, get_token_alignment, is_ascend
from tile_kernels.quant.common import get_cast_output_config
from tile_kernels.quant.swiglu_forward_asc import get_swiglu_forward_kernel_asc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('baseline', 'launch'), required=True)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--launches', type=int, default=1)
    parser.add_argument('--iterations', type=int, default=100)
    parser.add_argument('--rounds', type=int, default=3)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    frozen = json.loads((root/'case-and-prediction.json').read_text())
    case = frozen['case']
    assert case['id'] == 'swiglu-supp-05'
    assert is_ascend() and torch.npu.is_available()
    torch.npu.set_device(0)
    generator = torch.Generator().manual_seed(20261101)
    host = (torch.rand(case['input_shapes'][0], generator=generator)*2-1).to(torch.bfloat16)
    left, right = host.float().chunk(2, dim=case['attrs']['dim'])
    reference = (torch.nn.functional.silu(left)*right).to(host.dtype)
    x = host.to('npu:0')
    y = torch.empty(case['output_shapes'][0], dtype=x.dtype, device=x.device)
    assert x.numel()*x.element_size() == case['logical_input_bytes']
    assert y.numel()*y.element_size() == case['logical_output_bytes']
    config = get_cast_output_config('bf16', (1, 1), False, False, False)
    # Same factory/arguments as upstream swiglu_forward. Output is preallocated
    # so the profiled phase contains only native launches, without torch ops.
    kernel = get_swiglu_forward_kernel_asc(
        hidden=host.shape[-1]//2, num_experts=0, alignment=get_token_alignment(),
        with_weight=False, with_routed_scaling=False, clamp_value=None,
        count_clamp=False, in_dtype=T.dtype(x.dtype), out_config=config,
        num_vec_cores=get_num_vec_cores())
    source = kernel.get_kernel_source()
    (root/'metadata/kernel_source.cpp').write_text(source)
    symbol = str(kernel.prim_func.attrs['global_symbol'])
    metadata = {
        'case_id': case['id'], 'case': case, 'mode': args.mode,
        'seed': 20261101, 'native_global_symbol': symbol,
        'kernel_source_sha256': hashlib.sha256(source.encode()).hexdigest(),
        'wrapper_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'native_factory': 'tile_kernels.quant.swiglu_forward_asc.get_swiglu_forward_kernel_asc',
        'native_argument_order': ['x','out','out_sf=None','psum=None','topk=None','routed_scaling_factor=1.0','clamped_count=None'],
        'vector_core_count': get_num_vec_cores(), 'profiling_in_wrapper': False,
        'cache_regime': 'no application L2 flush; no hot-cache claim; outer profiler replay must be recorded separately',
        'tilekernels_commit': subprocess.check_output(['git','-C','/workspace/tilekernels-env-20261101/src/TileKernels','rev-parse','HEAD'],text=True).strip(),
        'prepared_utc_unix': time.time(),
    }
    def launch():
        kernel(x, y, None, None, None, 1.0, None)
    def check():
        actual = y.cpu()
        torch.testing.assert_close(actual, reference, rtol=2**-7, atol=2e-3, equal_nan=False)
        return {'status':'passed_finite_full_shape','output_elements':actual.numel(),
                'max_abs_error':(actual.float()-reference.float()).abs().max().item(),
                'rtol':2**-7,'atol':2e-3,'scope':'finite full-shape check; not full CANN benchmark contract'}
    torch.npu.synchronize()
    if args.mode == 'baseline':
        launch()
        torch.npu.synchronize()
        metadata['correctness'] = check()
        for _ in range(5): launch()
        torch.npu.synchronize()
        samples = []
        for _ in range(args.rounds):
            start = torch.npu.Event(enable_timing=True)
            end = torch.npu.Event(enable_timing=True)
            start.record()
            for _ in range(args.iterations): launch()
            end.record()
            end.synchronize()
            samples.append(start.elapsed_time(end)*1000/args.iterations)
        metadata['event_baseline'] = {
            'samples_us_per_call': samples, 'median_us_per_call':statistics.median(samples),
            'iterations_per_round':args.iterations,'rounds':args.rounds,'warmup_launches':6,
            'definition':'NPU event span divided by launch count; includes launch gaps/host dispatch effects; not pure kernel body or Vector active time',
            'msprof_enabled':False,'l2_flush':False}
    else:
        # JIT and correctness were prepared in the separate baseline process.
        # This process loads that cache before its only profiled native launch.
        metadata['target_launch_count'] = args.launches
        metadata['warmup_launches_in_application'] = 0
        metadata['mstx_ranges'] = []
        for i in range(args.launches):
            label = f"{case['id']}/target/{i}"
            handle = torch_npu.npu.mstx.range_start(label)
            launch()
            torch.npu.synchronize()
            torch_npu.npu.mstx.range_end(handle)
            metadata['mstx_ranges'].append(label)
        metadata['correctness'] = check()
    args.result.parent.mkdir(parents=True, exist_ok=True)
    args.result.write_text(json.dumps(metadata, indent=2)+'\n')
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == '__main__':
    main()
