"""Capture the native engram_gate_fwd kernel inside its full upstream correctness test."""

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
GROUP = 'engram_gate_fwd'
RANGE_NAME = 'quant_target'
INPUT_NAMES = ['hidden_states','kv','weight_fused','image_token_mask']
OUTPUT_INDICES = [4,5,6,7,8]
HIDDEN_MULTIPLE = 128


def validate_params(params):
    if set(params) != {'num_tokens', 'hc', 'hidden', 'with_mask'}:
        raise ValueError('Engram gate plan must specify exactly all required parameters')
    if any(type(params[k]) is not int for k in ('num_tokens', 'hc', 'hidden')) or type(params['with_mask']) is not bool:
        raise ValueError('invalid Engram gate parameter types')
    if params['num_tokens'] <= 0 or params['hc'] != 4 or params['hidden'] <= 0 or params['hidden'] % HIDDEN_MULTIPLE:
        raise ValueError('planned shape violates the Ascend kernel constraints')


def matches_capture(args, kwargs, params):
    if len(args) != 6 or set(kwargs) != {'has_image_token_mask', 'inplace', 'num_vec_cores'}:
        raise RuntimeError('unexpected forward native factory signature')
    if args[5] is not True or kwargs['inplace'] is not False:
        return False
    if args[0] != params['hidden'] or args[4] != params['hc'] or kwargs['has_image_token_mask'] != params['with_mask']:
        raise RuntimeError('forward specialization differs from planned case')
    return True


def hash_tensor(tensor, torch):
    if tensor is None:
        return None
    digest = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        digest.update(flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
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
    if len(tensors) != 9 or any(tensors[i] is None for i in OUTPUT_INDICES):
        raise ValueError('unexpected native output arguments')
    if stage == 'prepare':
        state['target_native_calls'] += 1
        return kernel(*tensors)
    if stage != 'default':
        raise ValueError(f'unknown stage: {stage}')
    warm = list(tensors)
    for index in OUTPUT_INDICES:
        warm[index] = torch.empty_like(tensors[index])
    for _ in range(5):
        kernel(*warm)
        state['application_warmup_native_calls'] += 1
    torch.npu.synchronize()
    api, handle, end = range_factory(torch)
    try:
        state['target_native_calls'] += 1
        result = kernel(*tensors)
    finally:
        end(handle)
    torch.npu.synchronize()
    return result


def run(group, params, stage, record_path):
    if group != GROUP or stage not in ('prepare', 'default'):
        raise ValueError(f'unsupported group or stage: {group!r}, {stage!r}')
    validate_params(params)
    import torch
    import torch_npu  # noqa: F401 -- registers the NPU backend
    from tile_kernels.rand import set_seed

    state = {
        'group': group, 'params': params, 'stage': stage, 'matched': 0,
        'target_native_calls': 0, 'application_warmup_native_calls': 0,
        'target_range': RANGE_NAME, 'seed': 42, 'correctness': 'not_run',
        'capture_mode': {'save_for_backward': True, 'inplace': False},
        'mode_scope': 'only save_for_backward=True and inplace=False are profiled',
        'correctness_scope': 'saved statistics are checked only on unmasked tokens, as in the upstream test',
        'output_semantics': 'separate output buffers; inputs are not intentionally mutated',
        'profiler_replay_state': 'unverified' if stage == 'default' else 'not_applicable',
        'profiler_replay_note': 'Actual profiler replay and buffer behavior require on-device verification.',
    }
    record_path = Path(record_path)
    module = None
    original = None
    try:
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(42)
        set_seed(42)
        module = importlib.import_module('tile_kernels.engram.engram_gate_fwd_asc')
        original = module.get_engram_gate_fwd_kernel_asc

        def replacement(*args, **kwargs):
            kernel = original(*args, **kwargs)
            if not matches_capture(args, kwargs, params):
                return kernel
            native_config = {'hidden': int(args[0]), 'eps': float(args[1]), 'scalar': float(args[2]),
                             'clamp_value': float(args[3]), 'hc': int(args[4]), 'save_for_backward': True,
                             'inplace': False, 'has_image_token_mask': bool(kwargs['has_image_token_mask']),
                             'num_vec_cores': int(kwargs['num_vec_cores'])}
            if state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, native_symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[{'name': name, 'tensor': hash_tensor(tensors[i], torch)}
                                         for i, name in enumerate(INPUT_NAMES)],
                                 native_config=native_config,
                                 outputs=[{'shape': list(tensors[i].shape), 'dtype': str(tensors[i].dtype)}
                                          for i in OUTPUT_INDICES])
                    return invoke_target(kernel, tensors, stage, torch, state)

            return Proxy()

        module.get_engram_gate_fwd_kernel_asc = replacement
        test_path = ROOT / 'tests/engram/test_engram_gate_fwd.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_engram_gate_fwd', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream test: {test_path}')
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        test_module.test_engram_gate_fwd(dict(params))
        if state['matched'] != 1 or state['target_native_calls'] != 1:
            raise RuntimeError('did not observe exactly one target native call')
        state['correctness'] = 'passed_upstream_full_engram_gate_fwd_test'
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_engram_gate_fwd_kernel_asc = original
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

