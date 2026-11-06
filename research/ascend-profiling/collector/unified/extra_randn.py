"""Capture one randn launch and check the upstream random-number contract.

The public API rejects NPU graph capture.  msprof kernel replay is a different
mechanism; whether replay changes random output is not established here.
"""

import argparse
import base64
import ctypes
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import traceback


GROUP = 'randn'
RANGE_NAME = 'quant_target'
USER_SEED = 42
DISTRIBUTION_MIN_ELEMENTS = 1024 * 1024


def distribution_status(numel, mean, std, positive_fraction):
    """Use the same sample-size gate and strict thresholds as upstream."""
    if numel < DISTRIBUTION_MIN_ELEMENTS:
        return 'not_applicable'
    if not all(math.isfinite(v) for v in (mean, std, positive_fraction)):
        return 'failed'
    return ('passed' if abs(mean) < 0.02 and abs(std - 1.0) < 0.02
            and abs(positive_fraction - 0.5) < 0.02 else 'failed')


def mstx_range(torch):
    library = Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'
    api = ctypes.CDLL(str(library))
    start, end = api.mstxRangeStartA, api.mstxRangeEnd
    start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
    end.argtypes, end.restype = [ctypes.c_uint64], None
    stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
    return api, start(RANGE_NAME.encode(), stream), end


def invoke_target(kernel, output, seed, stage, torch, state, range_factory=mstx_range):
    if stage == 'prepare':
        state['target_native_calls'] += 1
        return kernel(output, seed)
    if stage != 'default':
        raise ValueError(f'unknown stage: {stage}')
    # The public API's seed reservation happens once.  Warmups must not
    # reserve more seeds or overwrite the target output.
    warmup_output = torch.empty_like(output)
    for _ in range(5):
        kernel(warmup_output, seed)
        state['application_warmup_native_calls'] += 1
    torch.npu.synchronize()
    api, handle, end = range_factory(torch)
    try:
        state['target_native_calls'] += 1
        result = kernel(output, seed)
    finally:
        end(handle)
    torch.npu.synchronize()
    return result


def run(group, params, stage, record_path):
    if group != GROUP or stage not in ('prepare', 'default'):
        raise ValueError(f'unsupported group or stage: {group!r}, {stage!r}')
    if set(params) != {'shape', 'dtype'} or params['dtype'] not in ('bf16', 'fp32'):
        raise ValueError(f'invalid randn plan parameters: {params!r}')
    shape = params['shape']
    if not isinstance(shape, (list, tuple)) or not shape or any(type(n) is not int or n <= 0 for n in shape):
        raise ValueError(f'expected a nonempty positive shape: {shape!r}')

    import torch
    import torch_npu  # noqa: F401 -- registers the NPU backend
    from tile_kernels import rand

    record_path = Path(record_path)
    shape = tuple(shape)
    dtype = torch.bfloat16 if params['dtype'] == 'bf16' else torch.float32
    numel = math.prod(shape)
    state = {
        'group': group, 'params': params, 'stage': stage, 'matched': 0,
        'target_native_calls': 0, 'application_warmup_native_calls': 0,
        'verification_native_calls': 0, 'target_range': RANGE_NAME,
        'user_seed': USER_SEED, 'shape': list(shape), 'dtype': str(dtype),
        'graph_capture': 'prohibited_by_public_ascend_api',
        'profiler_replay_randomness': 'unverified' if stage == 'default' else 'not_applicable',
        'profiler_replay_note': 'Kernel replay must not be treated as NPU graph capture or as fresh random sampling.',
        'finite': 'not_run', 'seed_repeatability': 'not_run',
        'distribution': {'status': 'not_run', 'minimum_elements': DISTRIBUTION_MIN_ELEMENTS},
    }
    module = None
    original = None
    try:
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        module = importlib.import_module('tile_kernels.rand.randn_asc')
        original = module.get_randn_kernel_asc

        def replacement(*args, **kwargs):
            kernel = original(*args, **kwargs)

            class Proxy:
                def __call__(self, output, launch_seed):
                    seed = int(launch_seed)
                    if state['matched']:
                        state['verification_native_calls'] += 1
                        state['verification_launch_seed'] = seed
                        if state['verification_native_calls'] != 1:
                            raise RuntimeError('unexpected additional randn native call')
                        return kernel(output, launch_seed)
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    state.update(symbol=symbol, native_symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 launch_seed=seed,
                                 inputs=[{'shape': list(shape), 'dtype': str(dtype), 'user_seed': USER_SEED,
                                          'launch_seed': seed}],
                                 native_config={'dtype': str(args[0]), 'num_vec_cores': int(args[1]),
                                                'block_size': int(args[2]), 'num_stages': int(args[3]),
                                                'tile_size': int(args[4]), 'unroll_factor': int(args[5])})
                    return invoke_target(kernel, output, launch_seed, stage, torch, state)

            return Proxy()

        module.get_randn_kernel_asc = replacement
        rand.set_seed(USER_SEED)
        first = rand.randn(shape, dtype=dtype, device='npu:0')
        if tuple(first.shape) != shape or first.dtype != dtype or first.device.type != 'npu':
            raise AssertionError('randn output shape, dtype or device differs from request')
        state['finite'] = 'passed' if bool(torch.isfinite(first).all().item()) else 'failed'
        if state['finite'] != 'passed':
            raise AssertionError('randn output has non-finite values')

        rand.set_seed(USER_SEED)
        repeated = rand.randn_like(first)
        if tuple(repeated.shape) != shape or repeated.dtype != dtype or repeated.device != first.device:
            raise AssertionError('randn_like output shape, dtype or device differs from request')
        state['seed_repeatability'] = 'passed' if bool(torch.equal(first, repeated)) else 'failed'
        if state['seed_repeatability'] != 'passed':
            raise AssertionError('identical seed did not reproduce the full random output')
        if state['matched'] != 1 or state['target_native_calls'] != 1 or state['verification_native_calls'] != 1:
            raise RuntimeError('unexpected number of target or verification native calls')
        if state['verification_launch_seed'] != state['launch_seed']:
            raise AssertionError('identical user seed did not produce an identical launch seed')

        if numel >= DISTRIBUTION_MIN_ELEMENTS:
            sample = first.float()
            mean = float(sample.mean().item())
            std = float(sample.std().item())
            positive = float((sample > 0).float().mean().item())
            status = distribution_status(numel, mean, std, positive)
            state['distribution'].update(status=status, mean=mean, std=std, positive_fraction=positive,
                                         thresholds={'absolute_mean_lt': 0.02, 'absolute_std_minus_one_lt': 0.02,
                                                     'absolute_positive_fraction_minus_half_lt': 0.02})
            if status != 'passed':
                raise AssertionError('randn distribution did not meet upstream thresholds')
        else:
            state['distribution'].update(status='not_applicable', reason='sample smaller than upstream threshold')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_randn_kernel_asc = original
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
