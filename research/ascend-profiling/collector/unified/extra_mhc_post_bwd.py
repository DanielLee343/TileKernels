"""Profile one planned mHC post backward native kernel.

CLI: GROUP URLSAFE_BASE64_JSON_PARAMS prepare|default RECORD_JSON
Inputs and all outputs are checked in bounded CPU token chunks.  The original
TileLang callable handles its four returned tensors; its JIT behavior and
profiler identity still require validation in the target environment.
"""

import argparse
import base64
import ctypes
import hashlib
import json
import os
from pathlib import Path
import traceback


GROUP = 'mhc_post_bwd'
RANGE_NAME = 'mhc_post_bwd_target'
PLAN_SHA256 = 'e0ec36c25b6f60afb8d19cd3a5839f4a226e0976c87c78de1d86fcf40b9048dd'
PLAN_SHAPES = (
    (1, 512, 1280), (2, 8192, 7168), (1, 1024, 1280), (2, 4096, 7168),
    (1, 2048, 1280), (1, 512, 7168), (1, 4096, 2560), (1, 1024, 5120),
    (2, 4096, 1280), (2, 8192, 2560), (2, 4096, 5120), (2, 8192, 1280),
    (1, 1024, 2560), (1, 2048, 2560), (1, 512, 2560), (1, 2048, 5120),
    (1, 512, 5120), (2, 8192, 5120), (1, 1024, 7168), (1, 2048, 7168),
)
CHUNK_TOKENS = 64


def validate_params(params):
    if not isinstance(params, dict) or set(params) != {'n0', 'n1', 'hidden', 'mhc_mult'}:
        raise ValueError('expected n0, n1, hidden, mhc_mult from original plan')
    n0, n1, hidden, mult = (params[k] for k in ('n0', 'n1', 'hidden', 'mhc_mult'))
    if any(type(v) is not int for v in (n0, n1, hidden, mult)) or mult != 4:
        raise ValueError('invalid planned mHC post backward parameters')
    try:
        return PLAN_SHAPES.index((n0, n1, hidden)) + 1
    except ValueError:
        raise ValueError('shape is not a planned mHC post backward case') from None


def hash_tensor(tensor, torch):
    digest = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        digest.update(flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': digest.hexdigest()}


def random_device_tensor(shape, dtype, generator, torch):
    """Generate fixed inputs in bounded host chunks without reducing shape."""
    output = torch.empty(shape, dtype=dtype, device='npu:0')
    rows = output.view(-1, *shape[2:])
    for start in range(0, rows.shape[0], CHUNK_TOKENS):
        count = min(CHUNK_TOKENS, rows.shape[0] - start)
        host = torch.randn((count, *shape[2:]), dtype=dtype, generator=generator)
        rows[start:start + count].copy_(host)
    return output


def verify_outputs(inputs, outputs, reference, torch):
    """Compare every element with the upstream torch reference and tolerances."""
    x, residual, post, comb, d_out = inputs
    n0, n1, mult, hidden = residual.shape
    n = n0 * n1
    expected_shapes = (x.shape, residual.shape, post.shape, comb.shape)
    expected_dtypes = (x.dtype, residual.dtype, post.dtype, comb.dtype)
    if len(outputs) != 4:
        raise RuntimeError(f'expected four gradient outputs, got {len(outputs)}')
    for out, shape, dtype in zip(outputs, expected_shapes, expected_dtypes, strict=True):
        if out.shape != shape or out.dtype != dtype:
            raise RuntimeError('gradient output shape or dtype differs from the input contract')
    flat_inputs = (x.view(n, hidden), residual.view(n, mult, hidden), post.view(n, mult, 1),
                   comb.view(n, mult, mult), d_out.view(n, mult, hidden))
    flat_outputs = (outputs[0].view(n, hidden), outputs[1].view(n, mult, hidden),
                    outputs[2].view(n, mult, 1), outputs[3].view(n, mult, mult))
    names = ('grad_x', 'grad_residual', 'grad_post_layer_mix', 'grad_comb_res_mix')
    maxima = [0.0] * 4
    for start in range(0, n, CHUNK_TOKENS):
        end = min(n, start + CHUNK_TOKENS)
        host = [t[start:end].cpu().unsqueeze(0) for t in flat_inputs]
        refs = [t.detach().requires_grad_() for t in host[:4]]
        out = reference(*refs)
        expected = torch.autograd.grad(out, refs, host[4])
        for i, (got_device, want) in enumerate(zip(flat_outputs, expected, strict=True)):
            got = got_device[start:end].cpu().unsqueeze(0)
            if i < 2:
                torch.testing.assert_close(got, want)  # upstream BF16 defaults
            else:
                torch.testing.assert_close(got, want, atol=1e-4, rtol=1e-4)
            maxima[i] = max(maxima[i], float((got.float() - want.float()).abs().max()))
    return [{'output': name, 'passed': True, 'max_abs_error': maximum}
            for name, maximum in zip(names, maxima, strict=True)]


def run(group, params, stage, record_path):
    state = {'matched': 0, 'stage': stage, 'group': group, 'params': params,
             'plan_sha256': PLAN_SHA256, 'target_range': RANGE_NAME,
             'capture_scope': 'post backward native kernel only',
             'correctness_scope': 'all four outputs, CPU autograd per token chunk',
             'jit_output_protocol': 'native JIT callable returns four tensors; device validation pending'}
    module = original = None
    try:
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('invalid group or stage')
        state['plan_case_number'] = validate_params(params)
        import torch
        import torch_npu  # noqa: F401
        import tile_kernels.mhc.post_asc as module
        from tile_kernels.mhc.post_kernel import mhc_post_bwd
        from tile_kernels.torch.mhc import mhc_post_ref

        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        generator = torch.Generator(device='cpu').manual_seed(42)
        n0, n1, h, mult = (params[k] for k in ('n0', 'n1', 'hidden', 'mhc_mult'))
        x = random_device_tensor((n0, n1, h), torch.bfloat16, generator, torch)
        residual = random_device_tensor((n0, n1, mult, h), torch.bfloat16, generator, torch)
        post = random_device_tensor((n0, n1, mult, 1), torch.float32, generator, torch)
        comb = random_device_tensor((n0, n1, mult, mult), torch.float32, generator, torch)
        d_out = random_device_tensor((n0, n1, mult, h), torch.bfloat16, generator, torch)
        original = module.mhc_post_bwd_asc

        def capture_native(*args, **kwargs):
            if state['matched']:
                raise RuntimeError('more than one native call observed')
            compiled = original.compile(*args, **kwargs)
            symbol = str(compiled.prim_func.attrs['global_symbol'])
            state.update(matched=1, symbol=symbol, runtime_kernel=symbol + '_kernel',
                         source_sha256=hashlib.sha256(compiled.get_kernel_source().encode()).hexdigest(),
                         inputs=[hash_tensor(t, torch) for t in args], native_kwargs=kwargs)

            # Calling the original decorated function preserves its T.empty
            # return handling; do not invent positional output parameters.
            if stage == 'default':
                for _ in range(5):
                    warmup = original(*args, **kwargs)
                    torch.npu.synchronize()
                    del warmup
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
            else:
                result = original(*args, **kwargs)
            if not isinstance(result, (tuple, list)) or len(result) != 4:
                raise RuntimeError('native JIT did not return four outputs')
            return result

        module.mhc_post_bwd_asc = capture_native
        outputs = mhc_post_bwd(x, residual, post, comb, d_out)
        torch.npu.synchronize()
        if state['matched'] != 1:
            raise RuntimeError('target native call not observed')
        state['precision'] = verify_outputs((x, residual, post, comb, d_out), outputs, mhc_post_ref, torch)
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.mhc_post_bwd_asc = original
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
