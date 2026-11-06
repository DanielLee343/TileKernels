"""Profile one planned Ascend stochastic cast while running the upstream test.

The caller must validate the pinned checkout and compare prepare/default records.
This adapter marks only the first native cast call, not data generation or the
upstream statistical checks. A successful record alone is not profiler evidence.
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
GROUP = 'quant_cast'
SEED = 42


def normalize_params(params):
    """Convert the JSON shape without accepting a different cast contract."""
    keys = {'shape', 'in_dtype', 'out_dtype', 'stochastic_rounding'}
    if not isinstance(params, dict) or set(params) != keys:
        raise ValueError('quant_cast requires exactly the four planned fields')
    shape = params['shape']
    if (not isinstance(shape, (list, tuple)) or len(shape) != 1
            or type(shape[0]) is not int or shape[0] <= 0 or shape[0] % 4):
        raise ValueError('shape must contain one positive dimension divisible by 4')
    if (params['in_dtype'] != 'fp32' or params['out_dtype'] != 'bf16'
            or params['stochastic_rounding'] is not True):
        raise ValueError('Ascend planned cast requires stochastic fp32 to bf16')
    result = dict(params)
    result['shape'] = tuple(shape)
    return result


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
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('unsupported group or stage')
        params = normalize_params(params)
        state['params'] = params
        source_files = ('tests/quant/test_cast.py', 'tile_kernels/quant/cast_asc.py',
                        'tile_kernels/quant/cast_kernel.py', 'tile_kernels/rand/seed.py',
                        'tile_kernels/rand/randn_kernel.py', 'tile_kernels/testing/numeric.py',
                        'tile_kernels/testing/quant.py')
        state['source_files_sha256'] = {
            name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in source_files
        }
        sys.path.insert(0, str(ROOT))
        import torch
        import torch_npu  # noqa: F401 - registers the NPU backend
        import tile_kernels
        from tile_kernels.rand import set_seed

        if not Path(tile_kernels.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('tile_kernels was imported from a different checkout')
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(SEED)
        set_seed(SEED)

        module = importlib.import_module('tile_kernels.quant.cast_asc')
        if not Path(module.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('cast kernel was imported from a different checkout')
        original = module.get_cast_kernel_asc

        def replacement(*args, **kwargs):
            kernel = original(*args, **kwargs)
            if state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    if len(tensors) != 2 or tensors[0].numel() != params['shape'][0]:
                        raise RuntimeError('unexpected native cast arguments')
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[hash_tensor(tensors[0], torch)])
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

        module.get_cast_kernel_asc = replacement
        test_path = ROOT / 'tests/quant/test_cast.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_quant_cast', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream test: {test_path}')
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        test_module.test_cast_stochastic(params)
        if state['matched'] != 1:
            raise RuntimeError('target native cast call was not observed')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_cast_kernel_asc = original
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
