"""Profile one planned cast-back case using its unmodified upstream test.

The external runner must validate the pinned checkout, select the remaining
plan rows, compare prepare/default records, and inspect the profiler capture.
Input-generation and reference kernels run outside the marked target range.
"""

import argparse
import base64
import ctypes
import hashlib
import importlib
import importlib.util
import json
import os
from pathlib import Path
import random
import sys
import traceback


ROOT = Path('/workspace/tilekernels-env-20261101/src/TileKernels')
GROUPS = {'quant_cast_back_per_token', 'quant_cast_back_block'}
SEED = 42


def validate_params(group, params):
    """Reject unsupported contracts without changing a plan parameter."""
    common = {'num_tokens', 'hidden', 'fmt', 'out_dtype',
              'use_tma_aligned_col_major_sf', 'round_sf',
              'use_packed_ue8m0', 'num_per_channels'}
    if group not in GROUPS or not isinstance(params, dict):
        raise ValueError('unsupported cast-back group or parameters')
    expected = common | ({'use_e4m3_sf'} if group == 'quant_cast_back_per_token' else {'num_per_tokens'})
    if set(params) != expected:
        raise ValueError('cast-back parameters do not match the planned schema')
    n, hidden = params['num_tokens'], params['hidden']
    if type(n) is not int or n <= 0 or type(hidden) is not int or hidden <= 0 or hidden % 64:
        raise ValueError('positive token count and hidden divisible by 64 required')
    for key in ('use_tma_aligned_col_major_sf', 'round_sf', 'use_packed_ue8m0'):
        if type(params[key]) is not bool:
            raise ValueError(f'{key} must be bool')
    if params['fmt'] not in ('e2m1', 'e4m3') or params['out_dtype'] not in ('bf16', 'fp32'):
        raise ValueError('unsupported input or output dtype')
    if params['use_packed_ue8m0'] and not params['round_sf']:
        raise ValueError('packed UE8M0 requires rounded scales')
    channels = params['num_per_channels']
    if type(channels) is not int:
        raise ValueError('num_per_channels must be an integer')
    if group == 'quant_cast_back_per_token':
        if (channels != 32 or hidden % 128 or params['use_e4m3_sf'] is not False):
            raise ValueError('Ascend per-token generator requires 32 channels, hidden divisible by 128, and no E4M3 scales')
    else:
        if type(params['num_per_tokens']) is not int or (params['num_per_tokens'], channels) not in ((32, 1), (32, 32)):
            raise ValueError('Ascend block cast-back supports (32,1) and (32,32)')
        if channels == 1 and params['use_tma_aligned_col_major_sf']:
            raise ValueError('column-major scales are unsupported for per-channel cast-back')
    return dict(params)


def hash_tensor(t, torch):
    h = hashlib.sha256()
    view = t.detach().contiguous().view(-1)
    for offset in range(0, view.numel(), 1_000_000):
        data = view[offset:offset + 1_000_000].view(torch.uint8).cpu().numpy().tobytes()
        h.update(data)
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
        source_files = ('tests/quant/test_cast_back.py', 'tile_kernels/quant/cast_back_asc.py',
                        'tile_kernels/quant/cast_back_kernel.py', 'tile_kernels/quant/common.py',
                        'tile_kernels/quant/per_token_cast_asc.py', 'tile_kernels/quant/per_token_cast_kernel.py',
                        'tile_kernels/torch/cast.py', 'tile_kernels/rand/seed.py',
                        'tile_kernels/rand/randn_kernel.py', 'tile_kernels/testing/numeric.py')
        state['source_files_sha256'] = {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in source_files
        }
        sys.path.insert(0, str(ROOT))
        import torch
        import torch_npu  # noqa: F401 - registers the NPU backend
        import tile_kernels
        from tilelang import language as T
        from tile_kernels.rand import set_seed

        if not Path(tile_kernels.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('tile_kernels was imported from a different checkout')
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(SEED)
        set_seed(SEED)

        module = importlib.import_module('tile_kernels.quant.cast_back_asc')
        if not Path(module.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('cast-back kernel was imported from a different checkout')
        original = module.get_cast_back_kernel_asc

        def replacement(*args, **kwargs):
            config = kwargs.get('in_config')
            block = ((1, 32) if group == 'quant_cast_back_per_token'
                     else (params['num_per_tokens'], params['num_per_channels']))
            data_dtype = torch.int8 if params['fmt'] == 'e2m1' else torch.float8_e4m3fn
            out_dtype = torch.bfloat16 if params['out_dtype'] == 'bf16' else torch.float32
            if (args or config is None or kwargs.get('hidden') != params['hidden']
                    or config.sf_block != block or config.torch_dtype != data_dtype
                    or config.use_tma_aligned_col_major_sf != params['use_tma_aligned_col_major_sf']
                    or config.use_packed_ue8m0 != params['use_packed_ue8m0']
                    or config.use_e4m3_sf or kwargs.get('out_dtype') != T.dtype(out_dtype)):
                raise RuntimeError('native cast-back configuration does not match the plan')
            kernel = original(*args, **kwargs)
            if state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    if len(tensors) != 3 or tensors[0].shape[0] != params['num_tokens']:
                        raise RuntimeError('unexpected native cast-back arguments')
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[hash_tensor(tensors[0], torch), hash_tensor(tensors[1], torch)])
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

        module.get_cast_back_kernel_asc = replacement
        test_path = ROOT / 'tests/quant/test_cast_back.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_cast_back', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream test: {test_path}')
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        test = test_module.test_cast_back_per_token if group == 'quant_cast_back_per_token' else test_module.test_cast_back
        test(params)
        if state['matched'] != 1:
            raise RuntimeError('target native cast-back call was not observed')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_cast_back_kernel_asc = original
        Path(record_path).write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=sorted(GROUPS))
    parser.add_argument('params_b64')
    parser.add_argument('stage', choices=['prepare', 'default'])
    parser.add_argument('record')
    args = parser.parse_args()
    run(args.group, json.loads(base64.urlsafe_b64decode(args.params_b64.encode())),
        args.stage, Path(args.record))
