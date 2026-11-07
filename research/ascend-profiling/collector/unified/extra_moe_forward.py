"""Capture the requested routing mode while running the upstream MoE test.

The upstream correctness test exercises both fixed and non-fixed routing.  We
mark only the first native launch matching the plan's fix_routing value; its
remaining calls, reference computation and checks stay outside the MSTX range.
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


ROOT = Path(os.environ.get('TILEKERNELS_ROOT', str(Path(__file__).resolve().parents[4])))
GROUP = 'moe_topk_gate_forward'
RANGE_NAME = 'quant_target'
INTEGER_FIELDS = {'num_tokens', 'num_padded_tokens', 'num_topk', 'num_routed_experts', 'num_shared_experts'}
BOOLEAN_FIELDS = {'bias_exists', 'image_bias_exists', 'force_random_exists', 'use_shared_as_routed',
                  'scores_exists', 'fix_routing'}


def validate_params(params):
    if set(params) != INTEGER_FIELDS | BOOLEAN_FIELDS:
        raise ValueError('MoE forward plan must specify exactly all required parameters')
    if any(type(params[key]) is not int for key in INTEGER_FIELDS):
        raise ValueError('MoE size parameters must be integers')
    if any(type(params[key]) is not bool for key in BOOLEAN_FIELDS):
        raise ValueError('MoE feature parameters must be booleans')
    tokens, padded, topk = (params[k] for k in ('num_tokens', 'num_padded_tokens', 'num_topk'))
    experts, shared = params['num_routed_experts'], params['num_shared_experts']
    if tokens <= 0 or padded < 0 or topk <= 0 or topk >= experts:
        raise ValueError('invalid token, padding or top-k size for the upstream input fixture')
    if shared not in (1, 2) or topk + (shared if params['use_shared_as_routed'] else 0) > 32:
        raise ValueError('Ascend physical top-k or shared-expert limit exceeded')


def matches_plan(native_factory_args, requested_fix_routing):
    # The wrapper calls the native factory with fixed-routing existence as
    # its sixth positional argument; do not infer this from the inputs later.
    if len(native_factory_args) < 6 or type(native_factory_args[5]) is not bool:
        raise ValueError('unexpected MoE native factory signature')
    return native_factory_args[5] == requested_fix_routing


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
    if len(tensors) != 16:
        raise ValueError(f'expected 16 native arguments, got {len(tensors)}')
    if stage == 'prepare':
        state['target_native_calls'] += 1
        return kernel(*tensors)
    if stage != 'default':
        raise ValueError(f'unknown stage: {stage}')
    # unmapped_topk_idx is an input when fixed routing is on and is also an
    # output.  The other output buffers must likewise be separate from target.
    warm = list(tensors)
    for index in (8, 10, 11):
        if warm[index] is not None:
            warm[index] = torch.empty_like(warm[index])
    if warm[9] is not None:
        warm[9] = warm[9].clone()
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


def route_counts(tensors, torch):
    mask, fixed, random_mask = tensors[4], tensors[5], tensors[12]
    n = tensors[0].shape[0]
    valid = mask if mask is not None else torch.ones(n, dtype=torch.bool, device=tensors[0].device)
    active_random = (random_mask & valid) if random_mask is not None else None
    active_fixed = (fixed & valid) if fixed is not None else None
    if active_fixed is not None and active_random is not None:
        active_fixed = active_fixed & ~active_random
    return {'valid_tokens': int(valid.sum().item()),
            'force_random_tokens': int(active_random.sum().item()) if active_random is not None else 0,
            'fixed_routing_tokens': int(active_fixed.sum().item()) if active_fixed is not None else 0}


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
        'target_range': RANGE_NAME, 'requested_fix_routing': params['fix_routing'],
        'seed': 42, 'correctness': 'not_run',
        'profiler_replay_state': 'unverified' if stage == 'default' else 'not_applicable',
        'profiler_replay_note': 'unmapped_topk_idx is an input/output; buffer restoration must be checked on-device',
    }
    record_path = Path(record_path)
    module = None
    original = None
    try:
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(42)
        set_seed(42)
        module = importlib.import_module('tile_kernels.moe.moe_topk_gate_forward_asc')
        original = module.get_moe_topk_gate_forward_kernel_asc

        def replacement(*args, **kwargs):
            kernel = original(*args, **kwargs)
            matches = matches_plan(args, params['fix_routing'])
            if not matches or state['matched']:
                return kernel

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    names = ('logits', 'bias', 'image_bias', 'image_token_mask', 'mask', 'fix_routing_mask',
                             'to_physical_map', 'logical_count', 'unmapped_topk_idx', 'force_random')
                    indices = (0, 1, 2, 3, 4, 5, 6, 7, 9, 12)
                    inputs = [{'name': name, 'tensor': hash_tensor(tensors[i], torch)}
                              for name, i in zip(names, indices, strict=True)]
                    state.update(symbol=symbol, native_symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=inputs, route_counts=route_counts(tensors, torch),
                                 scalar_inputs={'num_shared_experts': int(tensors[13]),
                                                'routed_scaling_factor': float(tensors[14]),
                                                'ep_rank': int(tensors[15])})
                    return invoke_target(kernel, tensors, stage, torch, state)

            return Proxy()

        module.get_moe_topk_gate_forward_kernel_asc = replacement
        test_path = ROOT / 'tests/moe/test_moe_topk_gate_forward.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_moe_forward', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream test: {test_path}')
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        test_module.test_moe_topk_gate_forward(dict(params))
        if state['matched'] != 1 or state['target_native_calls'] != 1:
            raise RuntimeError('did not observe exactly one target native call')
        state['correctness'] = 'passed_upstream_full_moe_forward_test'
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        if stage == 'default':
            state['failure_interpretation'] = ('Replay semantics remain unverified; investigate input/output buffer '
                                               'mutation before attributing a mismatch to the kernel.')
        raise
    finally:
        if module is not None and original is not None:
            module.get_moe_topk_gate_forward_kernel_asc = original
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
