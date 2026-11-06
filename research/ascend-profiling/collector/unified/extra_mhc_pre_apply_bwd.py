"""Profile one planned pre-apply backward native call with in-place gradients.

CLI: GROUP URLSAFE_BASE64_JSON_PARAMS prepare|default RECORD_JSON
The marked call accumulates into a nonzero x_grad.  Application warmup uses a
separate buffer; profiler kernel replay restoration remains unverified.
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


GROUP = 'mhc_pre_apply_mix_bwd'
RANGE_NAME = 'mhc_pre_apply_bwd_target'
PLAN_SHA256 = 'e0ec36c25b6f60afb8d19cd3a5839f4a226e0976c87c78de1d86fcf40b9048dd'
PLAN_SHAPES = (
    (1, 128, 1280), (1, 8001, 7168), (1, 1024, 1280), (2, 4096, 7168),
    (1, 4096, 1280), (2, 1024, 7168), (1, 512, 2560), (1, 1024, 4096),
    (1, 1024, 5120), (2, 1024, 2560), (2, 4096, 4096), (2, 4096, 5120),
    (1, 512, 1280), (1, 8001, 1280), (2, 1024, 1280), (1, 128, 2560),
    (1, 4096, 2560), (1, 8001, 2560), (1, 128, 4096), (1, 512, 4096),
)
CHUNK_TOKENS = 64


def validate_params(params):
    if not isinstance(params, dict) or set(params) != {'n0', 'n1', 'hidden', 'mhc_mult'}:
        raise ValueError('expected original pre-apply backward plan parameters')
    n0, n1, hidden, mult = (params[k] for k in ('n0', 'n1', 'hidden', 'mhc_mult'))
    if any(type(v) is not int for v in (n0, n1, hidden, mult)) or mult != 4:
        raise ValueError('invalid pre-apply backward parameter contract')
    try:
        return PLAN_SHAPES.index((n0, n1, hidden)) + 1
    except ValueError:
        raise ValueError('shape is not a planned pre-apply backward case') from None


def hash_tensor(tensor, torch):
    digest = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        digest.update(flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': digest.hexdigest()}


def random_device_tensor(shape, dtype, generator, torch, transform=None):
    output = torch.empty(shape, dtype=dtype, device='npu:0')
    for start in range(0, shape[0], CHUNK_TOKENS):
        count = min(CHUNK_TOKENS, shape[0] - start)
        host = torch.randn((count, *shape[1:]), dtype=dtype, generator=generator)
        if transform == 'sigmoid':
            host = host.sigmoid()
        elif transform == 'softmax':
            host = host.softmax(-1)
        output[start:start + count].copy_(host)
    return output


def verify_outputs(x, mix, dy, initial, dx, dmix, reference, torch):
    n, mult, hidden = x.shape
    if dx.shape != x.shape or dx.dtype != x.dtype or dmix.shape != mix.shape or dmix.dtype != mix.dtype:
        raise RuntimeError('gradient output shape or dtype mismatch')
    maxima = [0.0, 0.0]
    for start in range(0, n, CHUNK_TOKENS):
        end = min(n, start + CHUNK_TOKENS)
        # Compute the derivative in FP32, then add the original BF16 buffer
        # before rounding, as the Ascend in-place implementation does.
        rx = x[start:end].cpu().float().unsqueeze(0).requires_grad_()
        rm = mix[start:end].cpu().unsqueeze(0).unsqueeze(-1).requires_grad_()
        grad = dy[start:end].cpu().unsqueeze(0)
        ref = reference(rx, rm)
        gx, gm = torch.autograd.grad(ref, (rx, rm), grad)
        expected_x = (initial[start:end].cpu().unsqueeze(0).float() + gx).bfloat16()
        expected_mix = gm.squeeze(-1)
        actual_x = dx[start:end].cpu().unsqueeze(0)
        actual_mix = dmix[start:end].cpu().unsqueeze(0)
        for i, (got, want) in enumerate(((actual_x, expected_x), (actual_mix, expected_mix))):
            torch.testing.assert_close(got, want, atol=1e-2, rtol=1e-3)
            maxima[i] = max(maxima[i], float((got.float() - want.float()).abs().max()))
    return [{'output': name, 'passed': True, 'max_abs_error': error}
            for name, error in zip(('x_grad_accumulated', 'mix_grad'), maxima, strict=True)]


def run(group, params, stage, record_path):
    state = {'matched': 0, 'stage': stage, 'group': group, 'params': params,
             'plan_sha256': PLAN_SHA256, 'target_range': RANGE_NAME,
             'capture_scope': 'one pre-apply backward native kernel',
             'output_semantics': 'x_grad is nonzero input and accumulated in place; mix_grad is returned',
             'warmup_policy': 'separate x_grad clone',
             'profiler_replay_state': 'unverified' if stage == 'default' else 'not_applicable',
             'device_validation': 'pending'}
    module = original = None
    try:
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('invalid group or stage')
        state['plan_case_number'] = validate_params(params)
        import torch
        import torch_npu  # noqa: F401
        module = importlib.import_module('tile_kernels.mhc.pre_apply_mix_asc')
        wrapper = importlib.import_module('tile_kernels.mhc.pre_apply_mix_kernel')
        reference_module = importlib.import_module('tile_kernels.torch.mhc')
        state['source_files_sha256'] = {
            'pre_apply_mix_asc.py': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
            'pre_apply_mix_kernel.py': hashlib.sha256(Path(wrapper.__file__).read_bytes()).hexdigest(),
            'torch_mhc.py': hashlib.sha256(Path(reference_module.__file__).read_bytes()).hexdigest(),
        }
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        generator = torch.Generator(device='cpu').manual_seed(42)
        n, mult, h = params['n0'] * params['n1'], params['mhc_mult'], params['hidden']
        x = random_device_tensor((n, mult, h), torch.bfloat16, generator, torch, 'sigmoid')
        mix = random_device_tensor((n, mult), torch.float32, generator, torch, 'softmax')
        dy = random_device_tensor((n, h), torch.bfloat16, generator, torch)
        initial = random_device_tensor((n, mult, h), torch.bfloat16, generator, torch)
        dx = initial.clone()
        original = module.mhc_pre_apply_mix_bwd_asc

        def capture_native(*args, **kwargs):
            if state['matched'] or len(args) != 4:
                raise RuntimeError('expected one native call with four tensor arguments')
            compiled = original.compile(*args, **kwargs)
            symbol = str(compiled.prim_func.attrs['global_symbol'])
            state.update(matched=1, symbol=symbol, runtime_kernel=symbol + '_kernel',
                         source_sha256=hashlib.sha256(compiled.get_kernel_source().encode()).hexdigest(),
                         inputs=[hash_tensor(t, torch) for t in args], native_kwargs=kwargs,
                         mutable_input_indices=[3])
            if stage == 'default':
                warmup_dx = args[3].clone()
                for _ in range(5):
                    original(*args[:3], warmup_dx, **kwargs)
                torch.npu.synchronize()
                del warmup_dx
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

        module.mhc_pre_apply_mix_bwd_asc = capture_native
        dmix = wrapper.mhc_pre_apply_mix_bwd(dy, x, mix, dx)
        torch.npu.synchronize()
        if state['matched'] != 1:
            raise RuntimeError('target native call not observed')
        state['precision'] = verify_outputs(x, mix, dy, initial, dx, dmix,
                                            reference_module.mhc_pre_apply_mix_ref, torch)
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        if stage == 'default':
            state['failure_interpretation'] = 'Check profiler replay restoration before attributing failure to kernel.'
        raise
    finally:
        if module is not None and original is not None:
            module.mhc_pre_apply_mix_bwd_asc = original
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
