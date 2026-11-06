"""Profile the main pre-split backward kernel and check reduced gradients.

CLI: GROUP URLSAFE_BASE64_JSON_PARAMS prepare|default RECORD_JSON
The upstream wrapper's two partial reductions run outside the marked range.
"""
import argparse
import base64
import ctypes
import hashlib
import importlib
import json
import os
from pathlib import Path
import traceback

GROUP = 'mhc_pre_split_mixes_bwd'
RANGE_NAME = 'mhc_presplit_bwd_target'
PLAN_SHA256 = 'e0ec36c25b6f60afb8d19cd3a5839f4a226e0976c87c78de1d86fcf40b9048dd'
PLAN_SHAPES = ((1, 1001), (1, 1024), (1, 127), (1, 128), (1, 16384),
               (1, 16385), (1, 17), (1, 1), (1, 2049), (1, 257),
               (1, 4096), (1, 4097), (1, 511), (1, 512), (1, 513),
               (1, 64), (1, 8001), (2, 1001), (2, 1024), (2, 4096))


def validate_params(params):
    if not isinstance(params, dict) or set(params) != {'n0', 'n1', 'mhc_mult'}:
        raise ValueError('expected original pre-split backward parameters')
    n0, n1, mult = (params[k] for k in ('n0', 'n1', 'mhc_mult'))
    if any(type(v) is not int for v in (n0, n1, mult)) or mult != 4:
        raise ValueError('invalid pre-split backward contract')
    try:
        return PLAN_SHAPES.index((n0, n1)) + 1
    except ValueError:
        raise ValueError('shape is not a planned case') from None


def hash_tensor(tensor, torch):
    h = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        h.update(flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': h.hexdigest()}


def run(group, params, stage, record_path):
    state = {'group': group, 'params': params, 'stage': stage, 'matched': 0,
             'target_range': RANGE_NAME, 'plan_sha256': PLAN_SHA256,
             'capture_scope': 'one pre-split backward native kernel producing input grad and per-core partials',
             'outside_capture': 'forward preparation, scale/base partial reductions and full-output comparison',
             'device_validation': 'pending'}
    module = original = None
    try:
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('invalid group or stage')
        state['plan_case_number'] = validate_params(params)
        import torch
        import torch_npu  # noqa: F401
        module = importlib.import_module('tile_kernels.mhc.pre_split_mixes_asc')
        wrapper = importlib.import_module('tile_kernels.mhc.pre_split_mixes_kernel')
        reference_module = importlib.import_module('tile_kernels.torch.mhc')
        state['source_files_sha256'] = {
            'pre_split_mixes_asc.py': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
            'pre_split_mixes_kernel.py': hashlib.sha256(Path(wrapper.__file__).read_bytes()).hexdigest(),
            'torch_mhc.py': hashlib.sha256(Path(reference_module.__file__).read_bytes()).hexdigest(),
        }
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        generator = torch.Generator(device='cpu').manual_seed(42)
        n0, n1, m = params['n0'], params['n1'], params['mhc_mult']
        n = n0 * n1
        x = torch.randn((n0, n1, 24), dtype=torch.float32, generator=generator)
        scale = torch.randn((3,), dtype=torch.float32, generator=generator)
        base = torch.randn((24,), dtype=torch.float32, generator=generator)
        dpre = torch.randn((n0, n1, m, 1), dtype=torch.float32, generator=generator)
        dpost = torch.randn((n0, n1, m, 1), dtype=torch.float32, generator=generator)
        dcomb = torch.randn((n0, n1, m, m), dtype=torch.float32, generator=generator)
        dx, dscale, dbase = (t.to('npu:0') for t in (x, scale, base))
        gdpre, gdpost, gdcomb = (t.to('npu:0') for t in (dpre, dpost, dcomb))
        pre = torch.empty((n, m), dtype=torch.float32, device='npu:0')
        post = torch.empty_like(pre)
        comb = torch.empty((n, m * m), dtype=torch.float32, device='npu:0')
        wrapper.mhc_pre_split_mixes_fwd(dx.view(n, 24), dscale, dbase, pre, post, comb, 2.0, 0.01)
        input_grad = torch.empty_like(dx).view(n, 24)
        scale_grad = torch.empty_like(dscale)
        base_grad = torch.empty_like(dbase)
        original = module.mhc_pre_split_mixes_bwd_mhc4_asc

        def capture_native(*args, **kwargs):
            if state['matched'] or len(args) != 11:
                raise RuntimeError('expected one native call with ten tensor arguments and one scalar')
            compiled = original.compile(*args, **kwargs)
            symbol = str(compiled.prim_func.attrs['global_symbol'])
            state.update(matched=1, symbol=symbol, runtime_kernel=symbol + '_kernel',
                         source_sha256=hashlib.sha256(compiled.get_kernel_source().encode()).hexdigest(),
                         inputs=[hash_tensor(t, torch) for t in args[:7]],
                         native_kwargs={**kwargs, 'mhc_post_mult_value': args[10]})
            if stage == 'default':
                for _ in range(5):
                    original(*args, **kwargs)
                torch.npu.synchronize()
                api = ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'))
                start, end = api.mstxRangeStartA, api.mstxRangeEnd
                start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
                end.argtypes, end.restype = [ctypes.c_uint64], None
                stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
                handle = start(RANGE_NAME.encode(), stream)
                try:
                    result = original(*args, **kwargs)
                finally:
                    end(handle)
                torch.npu.synchronize()
                return result
            return original(*args, **kwargs)

        module.mhc_pre_split_mixes_bwd_mhc4_asc = capture_native
        wrapper.mhc_pre_split_mixes_bwd(gdpre.view(n, m), gdpost.view(n, m), gdcomb.view(n, m * m),
                                        dx.view(n, 24), post, dscale, dbase,
                                        input_grad, scale_grad, base_grad, 2.0)
        torch.npu.synchronize()
        if state['matched'] != 1:
            raise RuntimeError('target native call not observed')
        # Wrapper reduction happens after the hook returned and the MSTX range ended.
        rx, rs, rb = (t.clone().requires_grad_() for t in (x, scale, base))
        refs = reference_module.mhc_pre_split_mixes_ref(rx, rs, rb, m, 2.0, 0.01)
        expected = torch.autograd.grad(refs, (rx, rs, rb), (dpre, dpost, dcomb))
        state['precision'] = []
        for name, got, want in zip(('input_mixes_grad', 'scale_grad', 'base_grad'),
                                   (input_grad.view_as(dx), scale_grad, base_grad), expected, strict=True):
            actual = got.cpu()
            torch.testing.assert_close(actual, want, rtol=1e-5, atol=2e-5)
            state['precision'].append({'output': name, 'passed': True,
                                       'max_abs_error': float((actual - want).abs().max())})
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.mhc_pre_split_mixes_bwd_mhc4_asc = original
        Path(record_path).write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=[GROUP])
    parser.add_argument('params_b64')
    parser.add_argument('stage', choices=['prepare', 'default'])
    parser.add_argument('record')
    args = parser.parse_args()
    run(args.group, json.loads(base64.urlsafe_b64decode(args.params_b64.encode())),
        args.stage, Path(args.record))
