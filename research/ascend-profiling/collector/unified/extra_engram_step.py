"""Run the upstream Engram Sinkhorn step check with one marked native launch.

The caller validates the pinned checkout and captures. Kernel replay semantics
for the mutable row-scale buffer have not been established.
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

ROOT = Path(os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4])))
GROUP = 'engram_sinkhorn_step'
SEED = 42


def validate_params(group, p):
    if group != GROUP or not isinstance(p, dict) or set(p) != {'num_rows', 'head_dim', 'eps'}:
        raise ValueError('invalid Sinkhorn step group or parameter schema')
    if type(p['num_rows']) is not int or p['num_rows'] <= 0:
        raise ValueError('num_rows must be a positive integer')
    if type(p['head_dim']) is not int or p['head_dim'] <= 0 or p['head_dim'] % 256:
        raise ValueError('head_dim must be a positive multiple of 256')
    if type(p['eps']) not in (float, int) or p['eps'] != 1e-20:
        raise ValueError('unsupported planned eps')
    return dict(p)


def hash_tensor(t, torch):
    h = hashlib.sha256()
    flat = t.detach().contiguous().view(-1)
    for offset in range(0, flat.numel(), 1_000_000):
        h.update(flat[offset:offset + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(t.shape), 'stride': list(t.stride()), 'dtype': str(t.dtype), 'sha256': h.hexdigest()}


def run(group, params, stage, record_path):
    state = {'group': group, 'stage': stage, 'seed': SEED, 'matched': 0,
             'profiler_replay_state': 'unverified'}
    module = original = None
    try:
        if stage not in ('prepare', 'default'):
            raise ValueError('unsupported stage')
        params = validate_params(group, params)
        state['params'] = params
        files = ('tests/engram/test_engram_sinkhorn.py', 'tile_kernels/engram/engram_sinkhorn_kernel.py',
                 'tile_kernels/engram/engram_sinkhorn_asc.py', 'tile_kernels/torch/engram.py',
                 'tile_kernels/testing/numeric.py', 'tile_kernels/rand/seed.py', 'tile_kernels/rand/randn_kernel.py')
        state['source_files_sha256'] = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
        sys.path.insert(0, str(ROOT))
        import torch
        import torch_npu  # noqa: F401
        import tile_kernels
        from tile_kernels.config import get_num_vec_cores
        from tile_kernels.rand import set_seed
        if not Path(tile_kernels.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('tile_kernels imported from a different checkout')
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(SEED)
        set_seed(SEED)
        module = importlib.import_module('tile_kernels.engram.engram_sinkhorn_asc')
        if not Path(module.__file__).resolve().is_relative_to(ROOT.resolve()):
            raise RuntimeError('kernel imported from a different checkout')
        original = module.get_engram_sinkhorn_step_kernel_asc

        def replacement(*args, **kwargs):
            expected = (params['head_dim'], params['eps'], get_num_vec_cores())
            if args != expected or kwargs:
                raise RuntimeError('native Sinkhorn step configuration does not match the plan')
            kernel = original(*args, **kwargs)
            if state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    if (len(tensors) != 5 or tuple(tensors[0].shape) != (params['num_rows'], params['head_dim'])
                            or tuple(tensors[1].shape) != (params['num_rows'],)
                            or tuple(tensors[2].shape) != (params['head_dim'],)
                            or tuple(tensors[3].shape) != (params['num_rows'],)
                            or tuple(tensors[4].shape) != (expected[-1], params['head_dim'])
                            or any(t.dtype != torch.float32 for t in tensors)):
                        raise RuntimeError('unexpected native Sinkhorn step arguments')
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[hash_tensor(tensors[i], torch) for i in (0, 1, 2)],
                                 input_roles=['matrix', 'row_scale_before', 'col_scale'], num_vec_cores=expected[-1],
                                 warmup_state='separate_copy_reset_before_each_launch')
                    if stage == 'default':
                        warm_rows = tensors[1].clone()
                        warm_row_norm = torch.empty_like(tensors[3])
                        warm_partial = torch.empty_like(tensors[4])
                        for _ in range(5):
                            warm_rows.copy_(tensors[1])
                            kernel(tensors[0], warm_rows, tensors[2], warm_row_norm, warm_partial)
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

        module.get_engram_sinkhorn_step_kernel_asc = replacement
        spec = importlib.util.spec_from_file_location('_profile_engram_step', ROOT / 'tests/engram/test_engram_sinkhorn.py')
        if spec is None or spec.loader is None:
            raise RuntimeError('cannot load upstream Engram test')
        test = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test)
        test.test_engram_sinkhorn_step(params)
        if state['matched'] != 1:
            raise RuntimeError('target native Sinkhorn step call was not observed')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_engram_sinkhorn_step_kernel_asc = original
        Path(record_path).write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=[GROUP])
    parser.add_argument('params_b64')
    parser.add_argument('stage', choices=['prepare', 'default'])
    parser.add_argument('record')
    args = parser.parse_args()
    run(args.group, json.loads(base64.urlsafe_b64decode(args.params_b64.encode())), args.stage, Path(args.record))
