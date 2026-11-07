"""Profile the fixed-shape SwiGLU backward extension in the candidate plan.

The caller selects original plan rows, verifies the pinned checkout, compares
prepare/default records and inspects the profiler capture.
"""

import argparse
import base64
import ctypes
import hashlib
import importlib
import json
import os
from pathlib import Path
import random
import sys
import traceback


ROOT = Path(os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4])))
GROUP = 'quant_swiglu_backward'
SEED = 42


def expert_prefix(num_tokens, num_experts, alignment):
    if type(num_tokens) is not int or num_tokens <= 0:
        raise ValueError('num_tokens must be a positive integer')
    if (num_experts, alignment) == (0, 1):
        return None
    if (num_experts, alignment) != (4, 256) or num_tokens % 1024:
        raise ValueError('four equal expert segments must each align to 256')
    return [num_tokens * i // 4 for i in range(1, 5)]


def validate_params(group, params):
    keys = {'num_tokens', 'hidden', 'fmt', 'with_weights', 'num_experts', 'alignment',
            'clamp_value', 'routed_scaling_factor', 'num_per_channels', 'round_sf',
            'use_tma_aligned_col_major_sf', 'use_packed_ue8m0', 'do_recompute'}
    if group != GROUP or not isinstance(params, dict) or set(params) != keys:
        raise ValueError('SwiGLU backward parameters do not match the planned schema')
    if type(params['hidden']) is not int or params['hidden'] <= 0 or params['hidden'] % 128:
        raise ValueError('hidden must be a positive multiple of 128')
    if type(params['num_experts']) is not int or type(params['alignment']) is not int:
        raise ValueError('num_experts and alignment must be integers')
    expert_prefix(params['num_tokens'], params['num_experts'], params['alignment'])
    for key in ('with_weights', 'round_sf', 'use_tma_aligned_col_major_sf', 'use_packed_ue8m0', 'do_recompute'):
        if type(params[key]) is not bool:
            raise ValueError(f'{key} must be bool')
    if params['clamp_value'] not in (None, 0.5) or isinstance(params['clamp_value'], bool):
        raise ValueError('unsupported planned clamp value')
    if params['routed_scaling_factor'] != (2.5 if params['with_weights'] else None):
        raise ValueError('routed scaling does not match the plan')
    if params['do_recompute'] != params['with_weights']:
        raise ValueError('planned extension ties recompute to with_weights')
    if params['use_tma_aligned_col_major_sf'] or params['use_packed_ue8m0']:
        raise ValueError('the planned extension uses row-major non-packed scales')
    if params['fmt'] == 'e4m3':
        if (type(params['num_per_channels']) is not int or params['num_per_channels'] != 32
                or not params['round_sf'] or params['num_tokens'] % 128):
            raise ValueError('planned E4M3 requires per-32 rounded scales and token count divisible by 128')
    elif params['fmt'] in ('bf16', 'fp32'):
        if params['num_per_channels'] is not None or params['round_sf']:
            raise ValueError('unquantized output does not use scale factors')
    else:
        raise ValueError('unsupported output format')
    return dict(params)


def hash_tensor(t, torch):
    if t is None:
        return None
    h = hashlib.sha256()
    view = t.detach().contiguous().view(-1)
    for offset in range(0, view.numel(), 1_000_000):
        h.update(view[offset:offset + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(t.shape), 'stride': list(t.stride()),
            'dtype': str(t.dtype), 'sha256': h.hexdigest()}


def extract(values, fmt, with_weights, has_act_out):
    values = list(values)
    expected_len = 1 + (fmt == 'e4m3') + with_weights + has_act_out
    if len(values) != expected_len:
        raise ValueError('unexpected SwiGLU backward result arity')
    x_grad = values.pop(0)
    x_grad_fp8 = values.pop(0) if fmt == 'e4m3' else None
    weight_grad = values.pop(0) if with_weights else None
    act_out = values.pop(0) if has_act_out else None
    return x_grad, x_grad_fp8, weight_grad, act_out


def run(group, params, stage, record_path):
    state = {'group': group, 'stage': stage, 'seed': SEED, 'matched': 0}
    module = original = None
    try:
        if stage not in ('prepare', 'default'):
            raise ValueError('unsupported stage')
        params = validate_params(group, params)
        state['params'] = params
        prefix = expert_prefix(params['num_tokens'], params['num_experts'], params['alignment'])
        state['expert_prefix'] = prefix
        source_files = ('tests/quant/test_swiglu_backward.py', 'tile_kernels/quant/swiglu_backward_asc.py',
                        'tile_kernels/quant/swiglu_backward_kernel.py', 'tile_kernels/quant/common.py',
                        'tile_kernels/quant/per_token_cast_asc.py', 'tile_kernels/quant/per_token_cast_kernel.py',
                        'tile_kernels/quant/cast_back_asc.py', 'tile_kernels/quant/cast_back_kernel.py',
                        'tile_kernels/torch/swiglu.py', 'tile_kernels/torch/cast.py',
                        'tile_kernels/testing/numeric.py', 'tile_kernels/rand/seed.py',
                        'tile_kernels/rand/randn_kernel.py')
        state['source_files_sha256'] = {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in source_files
        }
        sys.path.insert(0, str(ROOT))
        import torch
        import torch_npu  # noqa: F401 - registers the NPU backend
        import tile_kernels
        from tilelang import language as T
        from tile_kernels.config import get_num_vec_cores, set_token_alignment
        from tile_kernels.rand import randn, set_seed
        from tile_kernels.testing.numeric import assert_equal

        if not Path(tile_kernels.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('tile_kernels was imported from a different checkout')
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(SEED)
        set_seed(SEED)
        set_token_alignment(params['alignment'])
        n, hidden = params['num_tokens'], params['hidden']
        input_dtype = torch.float32 if params['fmt'] == 'fp32' else torch.bfloat16
        x = randn((n, hidden * 2), dtype=input_dtype, device='npu:0')
        if params['fmt'] == 'e4m3':
            # Preserve the upstream generator's unrounded per-token input quantization.
            x = tile_kernels.quant.per_token_cast(x, 'e4m3', num_per_channels=32)
        act_grad = randn((n, hidden), dtype=input_dtype, device='npu:0')
        weights = torch.rand((n,), dtype=torch.float32, device='npu:0') if params['with_weights'] else None
        psum = None if prefix is None else torch.tensor(prefix, dtype=torch.int32, device='npu:0')
        x_data, x_sf = x if isinstance(x, tuple) else (x, None)

        module = importlib.import_module('tile_kernels.quant.swiglu_backward_asc')
        if not Path(module.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('SwiGLU kernel was imported from a different checkout')
        original = module.get_swiglu_backward_kernel_asc

        def replacement(*args, **kwargs):
            config = kwargs.get('out_config')
            out_dtype = {'bf16': torch.bfloat16, 'fp32': torch.float32, 'e4m3': torch.float8_e4m3fn}[params['fmt']]
            native_x_dtype = torch.float8_e4m3fn if params['fmt'] == 'e4m3' else input_dtype
            expected = (hidden, params['num_experts'], params['alignment'], params['with_weights'],
                        params['routed_scaling_factor'] is not None, params['clamp_value'] is not None)
            if (args != expected or config is None or config.torch_dtype != out_dtype
                    or config.sf_block != (1, params['num_per_channels'] or 1)
                    or config.round_sf != params['round_sf']
                    or config.use_tma_aligned_col_major_sf != params['use_tma_aligned_col_major_sf']
                    or config.use_packed_ue8m0 != params['use_packed_ue8m0']
                    or kwargs.get('x_dtype') != T.dtype(native_x_dtype)
                    or kwargs.get('act_x_grad_dtype') != T.dtype(input_dtype)
                    or kwargs.get('do_recompute') != params['do_recompute']
                    or kwargs.get('num_vec_cores') != get_num_vec_cores()):
                raise RuntimeError('native SwiGLU backward configuration does not match the plan')
            kernel = original(*args, **kwargs)
            if state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    expected_scale = params['routed_scaling_factor'] if params['with_weights'] else 1.0
                    expected_clamp = params['clamp_value'] if params['clamp_value'] is not None else 0
                    if (len(tensors) != 12 or tuple(tensors[0].shape) != (n, hidden * 2)
                            or tensors[0].data_ptr() != x_data.data_ptr() or tensors[1] is not x_sf
                            or tensors[2].data_ptr() != act_grad.data_ptr() or tensors[3] is not weights
                            or tensors[4] != expected_scale or tensors[5] is not psum
                            or (tensors[6] is not None) != params['do_recompute']
                            or (tensors[7] is not None) != (params['fmt'] == 'e4m3')
                            or (tensors[8] is not None) != (params['fmt'] == 'e4m3')
                            or (tensors[10] is not None) != params['with_weights'] or tensors[11] != expected_clamp):
                        raise RuntimeError('unexpected native SwiGLU backward arguments')
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[hash_tensor(tensors[i], torch) for i in (0, 1, 2, 3, 5)],
                                 routed_scaling_factor=tensors[4], clamp_value=tensors[11],
                                 num_vec_cores=kwargs['num_vec_cores'])
                    if stage == 'default':
                        for _ in range(5):
                            kernel(*tensors)
                        torch.npu.synchronize()
                        lib = Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'
                        api = ctypes.CDLL(str(lib))
                        start, end = api.mstxRangeStartA, api.mstxRangeEnd
                        start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
                        end.argtypes, end.restype = [ctypes.c_uint64], None
                        stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
                        handle = start(b'quant_target', stream)
                        try:
                            result = kernel(*tensors)
                        finally:
                            end(handle)
                        torch.npu.synchronize()
                        return result
                    return kernel(*tensors)

            return Proxy()

        module.get_swiglu_backward_kernel_asc = replacement
        common = dict(x=x, act_x_grad=act_grad, fmt=params['fmt'], psum_num_tokens_per_expert=psum,
                      topk_weights=weights, routed_scaling_factor=params['routed_scaling_factor'],
                      clamp_value=params['clamp_value'], do_recompute=params['do_recompute'])
        if params['fmt'] == 'e4m3':
            actual = tile_kernels.quant.swiglu_backward_and_per_token_cast(
                **common, num_per_channels=32, round_sf=params['round_sf'],
                use_tma_aligned_col_major_sf=params['use_tma_aligned_col_major_sf'],
                use_packed_ue8m0=params['use_packed_ue8m0'])
            x_fp32 = tile_kernels.quant.cast_back(x, 'fp32', x_block_size=(1, 32))
        else:
            actual = tile_kernels.quant.swiglu_backward(**common)
            x_fp32 = x.float()
        ref = tile_kernels.torch.swiglu_backward(
            x_fp32, act_grad, psum_num_tokens_per_expert=psum, topk_weights=weights,
            routed_scaling_factor=params['routed_scaling_factor'], clamp_value=params['clamp_value'],
            alignment=params['alignment'])
        x_grad, quant_grad, weight_grad, act_out = extract(actual, params['fmt'], params['with_weights'], params['do_recompute'])
        x_grad_full, _, weight_grad_ref, act_out_ref = extract(ref, 'bf16', params['with_weights'], True)
        out_dtype = torch.float32 if params['fmt'] == 'fp32' else torch.bfloat16
        assert_equal(x_grad, x_grad_full.to(out_dtype))
        if params['fmt'] == 'e4m3':
            quant_ref = tile_kernels.torch.cast(
                x_grad_full, 'e4m3', block_size=(1, 32), round_sf=params['round_sf'],
                use_tma_aligned_col_major_sf=params['use_tma_aligned_col_major_sf'],
                use_packed_ue8m0=params['use_packed_ue8m0'])
            actual_dequant = tile_kernels.torch.cast_back(quant_grad, 'fp32', block_size=(1, 32))
            ref_dequant = tile_kernels.torch.cast_back(quant_ref, 'fp32', block_size=(1, 32))
            assert_equal(actual_dequant, ref_dequant)
        if params['with_weights']:
            torch.testing.assert_close(weight_grad, weight_grad_ref, atol=1e-4, rtol=1e-4)
        if params['do_recompute']:
            assert_equal(act_out, act_out_ref.to(out_dtype))
        if state['matched'] != 1:
            raise RuntimeError('target native SwiGLU backward call was not observed')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_swiglu_backward_kernel_asc = original
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
