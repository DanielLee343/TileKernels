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

ROOT = Path(os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4])))
GROUPS = {'engram_sinkhorn_finalize': ('sinkhorn_finalize', False, False)}


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
    record_path = Path(record_path).with_name('application-' + str(os.getpid()) + '.json')
    import torch
    import torch_npu
    from tile_kernels.rand import set_seed
    torch.set_num_threads(min(8, os.cpu_count() or 1))
    torch.npu.set_device(0)
    random.seed(42)
    set_seed(42)
    family, sf_only, cast_only = GROUPS[group]
    module = importlib.import_module('tile_kernels.engram.engram_sinkhorn_asc')
    getter_name = 'get_engram_sinkhorn_finalize_kernel_asc'
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
                inputs = [tensors[0], tensors[1], tensors[2]]
                if cast_only:
                    inputs.append(tensors[-1])
                state.update(symbol=symbol, runtime_kernel=symbol + '_kernel',
                             source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                             inputs=[hash_tensor(t, torch) for t in inputs])
                if stage == 'default':
                    meta = []
                    for t in tensors:
                        if isinstance(t, torch.Tensor):
                            meta.append({'address': hex(t.data_ptr()), 'device': str(t.device), 'shape': list(t.shape), 'stride': list(t.stride()), 'dtype': str(t.dtype), 'element_size': t.element_size(), 'logical_bytes': t.numel() * t.element_size()})
                        else:
                            meta.append(None)
                    Path(record_path).with_name('tensor-addresses-' + str(os.getpid()) + '.json').write_text(json.dumps(meta, indent=2) + '\n')
                    Path(record_path).with_name('generated-kernel-' + str(os.getpid()) + '.cpp').write_text(kernel.get_kernel_source())
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
        test_path = ROOT / 'tests/engram/test_engram_sinkhorn.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_' + family, test_path)
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        params = dict(params)
        if isinstance(params.get('x_block_size'), list):
            params['x_block_size'] = tuple(params['x_block_size'])
        if isinstance(params.get('block_size'), list):
            params['block_size'] = tuple(params['block_size'])
        test_module.test_engram_sinkhorn_finalize(params)
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
