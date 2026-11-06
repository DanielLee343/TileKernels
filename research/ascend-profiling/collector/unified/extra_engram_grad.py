"""Profile one upstream Engram weight-gradient reduction test case.

The MSTX range contains one invocation of the upstream native kernel.  The
five application warmups use separate gradient buffers; profiler kernel replay
semantics are deliberately recorded as unverified until measured on-device.
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
import traceback


ROOT = Path('/workspace/tilekernels-env-20261101/src/TileKernels')
GROUP = 'engram_grad_w_reduce'
RANGE_NAME = 'quant_target'


def hash_tensor(tensor, torch):
    digest = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        chunk = flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes()
        digest.update(chunk)
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': digest.hexdigest()}


def mstx_range(torch):
    library = Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'
    api = ctypes.CDLL(str(library))
    start, end = api.mstxRangeStartA, api.mstxRangeEnd
    start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
    end.argtypes, end.restype = [ctypes.c_uint64], None
    stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
    return api, start(RANGE_NAME.encode(), stream), end


def invoke_target(kernel, tensors, stage, torch, state, range_factory=mstx_range):
    """Invoke one logical target; preserve target outputs during host warmup."""
    if len(tensors) != 5:
        raise ValueError(f'expected 5 native tensor arguments, got {len(tensors)}')
    if stage == 'prepare':
        state['target_native_calls'] += 1
        return kernel(*tensors)
    if stage != 'default':
        raise ValueError(f'unknown stage: {stage}')

    # These are accumulated in-place.  Never warm up on the target buffers.
    warmup_tensors = (*tensors[:3], tensors[3].clone(), tensors[4].clone())
    for _ in range(5):
        kernel(*warmup_tensors)
        state['application_warmup_native_calls'] += 1
    torch.npu.synchronize()
    # Keep the CDLL alive until after mstxRangeEnd.
    api, handle, end = range_factory(torch)
    try:
        state['target_native_calls'] += 1
        result = kernel(*tensors)
    finally:
        end(handle)
    torch.npu.synchronize()
    return result


def run(group, params, stage, record_path):
    if group != GROUP:
        raise ValueError(f'unsupported group: {group}')
    if stage not in ('prepare', 'default'):
        raise ValueError(f'unsupported stage: {stage}')
    if set(params) != {'hidden'} or not isinstance(params['hidden'], int) or params['hidden'] <= 0 or params['hidden'] % 64:
        raise ValueError(f'invalid grad_w_reduce plan parameters: {params!r}')

    import torch
    import torch_npu  # noqa: F401 -- registers the NPU backend
    from tile_kernels.config import get_num_vec_cores
    from tile_kernels.rand import set_seed

    record_path = Path(record_path)
    state = {
        'group': group, 'params': params, 'stage': stage, 'matched': 0,
        'target_native_calls': 0, 'application_warmup_native_calls': 0,
        'target_range': RANGE_NAME,
        'output_semantics': 'gradient buffers are inputs and are accumulated in place',
        'warmup_policy': 'five launches on separate gradient clones' if stage == 'default' else 'none',
        'profiler_replay_state': 'unverified' if stage == 'default' else 'not_applicable',
        'profiler_replay_note': 'A passing upstream check does not establish profiler buffer restoration.',
        'correctness': 'not_run',
    }
    module = None
    original = None
    try:
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(42)
        set_seed(42)  # also seeds torch, matching the existing unified quant adapter
        module = importlib.import_module('tile_kernels.engram.engram_grad_w_reduce_asc')
        original = module.get_engram_grad_w_reduce_kernel_asc

        def replacement(*args, **kwargs):
            kernel = original(*args, **kwargs)

            class Proxy:
                def __call__(self, *tensors):
                    state['matched'] += 1
                    if state['matched'] != 1:
                        raise RuntimeError('upstream test invoked the target native kernel more than once')
                    cores = get_num_vec_cores()
                    if cores % 4 or tensors[0].shape[0] != cores // 4:
                        raise RuntimeError('upstream partial count does not match the current backward kernel')
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, native_symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[hash_tensor(t, torch) for t in tensors],
                                 vector_cores=cores, partials=tensors[0].shape[0],
                                 mutable_input_indices=[3, 4])
                    return invoke_target(kernel, tensors, stage, torch, state)

            return Proxy()

        module.get_engram_grad_w_reduce_kernel_asc = replacement
        test_path = ROOT / 'tests/engram/test_engram_grad_w_reduce.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_engram_grad', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream test: {test_path}')
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        test_module.test_engram_grad_w_reduce(dict(params))
        if state['matched'] != 1 or state['target_native_calls'] != 1:
            raise RuntimeError('did not observe exactly one target native call')
        state['correctness'] = 'passed_upstream_full_output_rtol_1e-4_atol_1e-4'
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        if stage == 'default':
            state['failure_interpretation'] = ('Do not infer a kernel defect without checking whether profiler '
                                               'replay mutated the in-place target buffers.')
        raise
    finally:
        if module is not None and original is not None:
            module.get_engram_grad_w_reduce_kernel_asc = original
        record_path.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('group', choices=[GROUP])
    parser.add_argument('params_b64')
    parser.add_argument('stage', choices=['prepare', 'default'])
    parser.add_argument('record')
    args = parser.parse_args()
    params = json.loads(base64.urlsafe_b64decode(args.params_b64.encode()))
    run(args.group, params, args.stage, Path(args.record))
