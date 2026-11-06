"""Profile the fixed-shape SwiGLU forward extension in the candidate plan.

The caller selects plan rows, verifies the pinned checkout, compares records,
and inspects the profiler capture. Only the target native launch is marked.
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


ROOT = Path('/workspace/tilekernels-env-20261101/src/TileKernels')
GROUP = 'quant_swiglu_forward'
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
            'use_tma_aligned_col_major_sf', 'use_packed_ue8m0'}
    if group != GROUP or not isinstance(params, dict) or set(params) != keys:
        raise ValueError('SwiGLU parameters do not match the planned schema')
    if type(params['hidden']) is not int or params['hidden'] <= 0 or params['hidden'] % 128:
        raise ValueError('hidden must be a positive multiple of 128')
    if type(params['num_experts']) is not int or type(params['alignment']) is not int:
        raise ValueError('num_experts and alignment must be integers')
    expert_prefix(params['num_tokens'], params['num_experts'], params['alignment'])
    for key in ('with_weights', 'round_sf', 'use_tma_aligned_col_major_sf', 'use_packed_ue8m0'):
        if type(params[key]) is not bool:
            raise ValueError(f'{key} must be bool')
    if params['clamp_value'] not in (None, 0.5) or isinstance(params['clamp_value'], bool):
        raise ValueError('unsupported planned clamp value')
    if params['routed_scaling_factor'] != (2.5 if params['with_weights'] else None):
        raise ValueError('routed scaling does not match the plan')
    if params['use_tma_aligned_col_major_sf'] or params['use_packed_ue8m0']:
        raise ValueError('the planned extension uses row-major non-packed scales')
    if params['fmt'] == 'e4m3':
        if type(params['num_per_channels']) is not int or params['num_per_channels'] != 32 or not params['round_sf']:
            raise ValueError('planned E4M3 output requires per-32 rounded scales')
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
        state['clamped_count_enabled'] = False
        source_files = ('tile_kernels/quant/swiglu_forward_asc.py', 'tile_kernels/quant/swiglu_forward_kernel.py',
                        'tile_kernels/quant/common.py', 'tile_kernels/torch/swiglu.py',
                        'tile_kernels/torch/cast.py', 'tile_kernels/testing/numeric.py',
                        'tile_kernels/rand/seed.py', 'tile_kernels/rand/randn_kernel.py')
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
        # Follow the upstream forward generator's weight-then-x random order.
        weights = randn((n,), dtype=torch.float32, device='npu:0') if params['with_weights'] else None
        x = randn((n, hidden * 2), dtype=torch.bfloat16, device='npu:0')
        psum = None if prefix is None else torch.tensor(prefix, dtype=torch.int32, device='npu:0')

        module = importlib.import_module('tile_kernels.quant.swiglu_forward_asc')
        if not Path(module.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('SwiGLU kernel was imported from a different checkout')
        original = module.get_swiglu_forward_kernel_asc

        def replacement(*args, **kwargs):
            config = kwargs.get('out_config')
            dtype = {'bf16': torch.bfloat16, 'fp32': torch.float32, 'e4m3': torch.float8_e4m3fn}[params['fmt']]
            expected = (hidden, params['num_experts'], params['alignment'], params['with_weights'],
                        params['routed_scaling_factor'] is not None, params['clamp_value'], False)
            if (args != expected or config is None or config.torch_dtype != dtype
                    or config.sf_block != (1, params['num_per_channels'] or 1)
                    or config.round_sf != params['round_sf']
                    or config.use_tma_aligned_col_major_sf != params['use_tma_aligned_col_major_sf']
                    or config.use_packed_ue8m0 != params['use_packed_ue8m0']
                    or kwargs.get('in_dtype') != T.dtype(torch.bfloat16)
                    or kwargs.get('num_vec_cores') != get_num_vec_cores()):
                raise RuntimeError('native SwiGLU configuration does not match the plan')
            kernel = original(*args, **kwargs)
            if state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    expected_scale = params['routed_scaling_factor'] if params['with_weights'] else 1.0
                    if (len(tensors) != 7 or tuple(tensors[0].shape) != (n, hidden * 2)
                            or tensors[3] is not psum or tensors[4] is not weights
                            or tensors[5] != expected_scale or tensors[6] is not None):
                        raise RuntimeError('unexpected native SwiGLU arguments')
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[hash_tensor(tensors[0], torch), hash_tensor(tensors[3], torch),
                                         hash_tensor(tensors[4], torch)],
                                 routed_scaling_factor=tensors[5], num_vec_cores=kwargs['num_vec_cores'])
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

        module.get_swiglu_forward_kernel_asc = replacement
        common = dict(x=x, fmt=params['fmt'], psum_num_tokens_per_expert=psum,
                      topk_weights=weights, routed_scaling_factor=params['routed_scaling_factor'],
                      clamp_value=params['clamp_value'], clamped_count=None)
        if params['fmt'] == 'e4m3':
            actual = tile_kernels.quant.swiglu_forward_and_per_token_cast(
                **common, num_per_channels=params['num_per_channels'], round_sf=params['round_sf'],
                use_tma_aligned_col_major_sf=params['use_tma_aligned_col_major_sf'],
                use_packed_ue8m0=params['use_packed_ue8m0'])
        else:
            actual = tile_kernels.quant.swiglu_forward(**common)
        ref = tile_kernels.torch.swiglu_forward(x, psum, weights, params['routed_scaling_factor'], params['clamp_value'], None)
        if params['fmt'] == 'e4m3':
            ref = tile_kernels.torch.cast(ref, 'e4m3', (1, 32), round_sf=params['round_sf'],
                                          use_tma_aligned_col_major_sf=params['use_tma_aligned_col_major_sf'],
                                          use_packed_ue8m0=params['use_packed_ue8m0'])
            if not isinstance(actual, tuple) or len(actual) != 2:
                raise RuntimeError('expected quantized output and scale')
            assert_equal(actual[0], ref[0])
            assert_equal(actual[1], ref[1])
        else:
            if params['fmt'] == 'bf16':
                ref = ref.bfloat16()
            assert_equal(actual, ref)
        if state['matched'] != 1:
            raise RuntimeError('target native SwiGLU call was not observed')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_swiglu_forward_kernel_asc = original
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
