"""Prototype: reuse the upstream quant test and isolate one native TileLang call.

This is a pilot, not a complete or production collection runner. Each case
must pass upstream correctness and a separate profiler-identity inspection.
"""
import argparse
import base64
import ctypes
import hashlib
import importlib
import importlib.util
import json
import os
import random
from pathlib import Path
import traceback

ROOT = Path('/workspace/tilekernels-env-20261101/src/TileKernels')
GROUPS = {'quant_per_channel_cast': ('channel', False, False)}


def hash_tensor(t, torch):
    if t is None:
        return None
    # Hash contents in bounded chunks instead of copying the whole tensor to host.
    h = hashlib.sha256()
    view = t.detach().contiguous().view(-1)
    for off in range(0, view.numel(), 1_000_000):
        data = view[off:off + 1_000_000].view(torch.uint8).cpu().numpy().tobytes()
        h.update(data)
    return {'shape': list(t.shape), 'stride': list(t.stride()), 'dtype': str(t.dtype), 'sha256': h.hexdigest()}


def run(group, params, stage, record_path):
    import torch
    import torch_npu
    from tile_kernels.rand import set_seed
    torch.set_num_threads(min(8, os.cpu_count() or 1))
    torch.npu.set_device(0)
    random.seed(42)
    set_seed(42)
    family, sf_only, cast_only = GROUPS[group]
    module = importlib.import_module('tile_kernels.quant.per_' + family + '_cast_asc')
    getter_name = 'get_per_' + family + '_cast_kernel_asc'
    original = getattr(module, getter_name)
    state = {'matched': 0, 'stage': stage}

    def replacement(*args, **kwargs):
        kernel = original(*args, **kwargs)
        matches = True
        if not matches or state['matched']:
            return kernel
        class Proxy:
            def __call__(self, *tensors):
                if state['matched']:
                    return kernel(*tensors)
                state['matched'] += 1
                symbol = str(kernel.prim_func.attrs['global_symbol'])
                inputs = [tensors[0], tensors[3]]
                if cast_only:
                    inputs.append(tensors[-1])
                state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                             source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                             inputs=[hash_tensor(t, torch) for t in inputs])
                if stage == 'default':
                    for _ in range(5):
                        kernel(*tensors)
                    torch.npu.synchronize()
                    api = ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'))
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

    setattr(module, getter_name, replacement)
    try:
        test_path = ROOT / ('tests/quant/test_per_' + family + '_cast.py')
        spec = importlib.util.spec_from_file_location('_profile_upstream_' + family, test_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        params = dict(params)
        if isinstance(params.get('x_block_size'), list):
            params['x_block_size'] = tuple(params['x_block_size'])
        if isinstance(params.get('block_size'), list):
            params['block_size'] = tuple(params['block_size'])
        getattr(test_module, 'test_per_' + family + '_cast')(params)
        assert state['matched'] == 1, f'target call not observed: {group}'
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        setattr(module, getter_name, original)
        record_path.write_text(json.dumps(state, indent=2) + '\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('group', choices=GROUPS)
    p.add_argument('params_b64')
    p.add_argument('stage', choices=['prepare', 'default'])
    p.add_argument('record')
    a = p.parse_args()
    run(a.group, json.loads(base64.urlsafe_b64decode(a.params_b64.encode())), a.stage, Path(a.record))
