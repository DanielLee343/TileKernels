"""Capture the mHC head backward native kernel, not its partial reductions.

CLI: GROUP URLSAFE_BASE64_JSON_PARAMS prepare|default RECORD_JSON
The parameters must match one of the 20 rows in the pinned original plan.
The caller is responsible for profiler invocation and capture inspection.
"""

import argparse
import base64
import ctypes
import hashlib
import json
import os
from pathlib import Path
import traceback


GROUP = 'mhc_head_compute_mix_bwd'
PLAN_SHA256 = 'e0ec36c25b6f60afb8d19cd3a5839f4a226e0976c87c78de1d86fcf40b9048dd'
PLAN_SHAPES = (
    (1, 1), (2, 24576), (1, 1001), (2, 4096), (1, 1024),
    (1, 127), (1, 128), (1, 16384), (1, 16385), (1, 17),
    (1, 2049), (1, 257), (1, 4097), (1, 511), (1, 512),
    (1, 513), (1, 64), (1, 8001), (1, 24576), (1, 4096),
)


def validate_params(params):
    if not isinstance(params, dict) or set(params) != {'n0', 'n1', 'mhc_mult', 'eps'}:
        raise ValueError('expected n0, n1, mhc_mult, eps from the original plan')
    n0, n1, mult, eps = (params[k] for k in ('n0', 'n1', 'mhc_mult', 'eps'))
    if (type(n0) is not int or type(n1) is not int or type(mult) is not int
            or type(eps) not in (int, float) or mult != 4 or eps != 0.01):
        raise ValueError('invalid planned mHC head backward parameters')
    try:
        return PLAN_SHAPES.index((n0, n1)) + 1
    except ValueError:
        raise ValueError('shape is not a planned mHC head backward case') from None


def hash_tensor(tensor, torch):
    h = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for offset in range(0, flat.numel(), 1_000_000):
        h.update(flat[offset:offset + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': h.hexdigest()}


def run(group, params, stage, record_path):
    state = {'matched': 0, 'stage': stage, 'group': group, 'params': params,
             'plan_sha256': PLAN_SHA256, 'capture_scope': 'head backward native kernel only',
             'outside_capture': 'scale/base partial reductions and full-output reference check'}
    module = original = None
    try:
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('invalid group or stage')
        state['plan_case_number'] = validate_params(params)
        import torch
        import torch_npu  # noqa: F401
        import tile_kernels.mhc.head_compute_mix_asc as module
        from tile_kernels.config import get_num_vec_cores
        from tile_kernels.mhc.head_compute_mix_kernel import mhc_head_compute_mix_bwd
        from tile_kernels.torch.mhc import mhc_head_compute_mix_ref

        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        generator = torch.Generator(device='cpu').manual_seed(42)
        n, mult = params['n0'] * params['n1'], params['mhc_mult']
        host_x = torch.randn((n, mult), dtype=torch.float32, generator=generator)
        host_scale = torch.randn((1,), dtype=torch.float32, generator=generator)
        host_base = torch.randn((mult,), dtype=torch.float32, generator=generator)
        host_grad = torch.randn((n, mult), dtype=torch.float32, generator=generator)
        host_inputs = (host_grad, host_x, host_scale, host_base)
        grad, x, scale, base = (t.to('npu:0') for t in host_inputs)
        dx = torch.empty_like(x)
        cores = get_num_vec_cores()
        scale_partial = torch.empty((cores, 1), dtype=torch.float32, device=x.device)
        base_partial = torch.empty((cores, mult), dtype=torch.float32, device=x.device)
        original = module.mhc_head_compute_mix_bwd_asc

        def capture_native(*args, **kwargs):
            if state['matched']:
                raise RuntimeError('more than one native call observed')
            kernel = original.compile(*args, **kwargs)
            symbol = str(kernel.prim_func.attrs['global_symbol'])
            state.update(matched=1, symbol=symbol, runtime_kernel=symbol + '_kernel',
                         source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                         inputs=[hash_tensor(t, torch) for t in args[:4]],
                         native_kwargs=kwargs)
            if stage == 'default':
                for _ in range(5):
                    kernel(*args)
                torch.npu.synchronize()
                api = ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'))
                start, end = api.mstxRangeStartA, api.mstxRangeEnd
                start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
                end.argtypes, end.restype = [ctypes.c_uint64], None
                stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
                handle = start(b'mhc_head_bwd_target', stream)
                try:
                    result = kernel(*args)
                finally:
                    end(handle)
                torch.npu.synchronize()
                return result
            return kernel(*args)

        module.mhc_head_compute_mix_bwd_asc = capture_native
        mhc_head_compute_mix_bwd(grad, x, scale, base, dx, scale_partial, base_partial, cores)
        torch.npu.synchronize()
        if state['matched'] != 1:
            raise RuntimeError('target native call not observed')

        # Sum the actual partial buffers after the marked range, as in the
        # upstream test wrapper, then compare all three complete gradients.
        actual = (dx.cpu(), scale_partial.cpu().sum(0), base_partial.cpu().sum(0))
        ref_x = host_x.clone().requires_grad_()
        ref_scale = host_scale.clone().requires_grad_()
        ref_base = host_base.clone().requires_grad_()
        ref = mhc_head_compute_mix_ref(ref_x, ref_scale, ref_base, params['eps'])
        expected = torch.autograd.grad(ref, (ref_x, ref_scale, ref_base), host_grad)
        state['precision'] = []
        for name, got, want in zip(('input_mix_grad', 'scale_grad', 'base_grad'), actual, expected):
            torch.testing.assert_close(got, want, rtol=1e-4, atol=1e-5)
            state['precision'].append({'output': name, 'passed': True,
                                       'max_abs_error': float((got - want).abs().max())})
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.mhc_head_compute_mix_bwd_asc = original
        record_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=[GROUP])
    parser.add_argument('params_b64')
    parser.add_argument('stage', choices=['prepare', 'default'])
    parser.add_argument('record')
    args = parser.parse_args()
    run(args.group, json.loads(base64.urlsafe_b64decode(args.params_b64.encode())),
        args.stage, Path(args.record))
