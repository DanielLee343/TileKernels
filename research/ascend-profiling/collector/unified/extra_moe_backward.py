"""Capture one planned MoE backward call within the upstream correctness test.

Fixed routing is a forward-input property, not a backward kernel specialization.
Track the test's fixture branch explicitly and mark only the requested branch.
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
GROUP = 'moe_topk_gate_backward'
RANGE_NAME = 'quant_target'
INTEGER_FIELDS = {'num_tokens', 'num_padded_tokens', 'num_seqs', 'num_topk',
                  'num_routed_experts', 'num_shared_experts'}
BOOLEAN_FIELDS = {'bias_exists', 'image_bias_exists', 'aux_exists', 'fix_routing'}


def validate_params(params):
    if set(params) != INTEGER_FIELDS | BOOLEAN_FIELDS:
        raise ValueError('MoE backward plan must specify exactly all required parameters')
    if any(type(params[key]) is not int for key in INTEGER_FIELDS):
        raise ValueError('MoE size parameters must be integers')
    if any(type(params[key]) is not bool for key in BOOLEAN_FIELDS):
        raise ValueError('MoE feature parameters must be booleans')
    tokens, padded, seqs = (params[k] for k in ('num_tokens', 'num_padded_tokens', 'num_seqs'))
    topk, experts = params['num_topk'], params['num_routed_experts']
    if tokens <= 0 or padded < 0 or seqs <= 0 or topk <= 0 or topk >= experts or topk > 32:
        raise ValueError('invalid token, sequence or top-k size for the upstream fixture')
    if params['num_shared_experts'] not in (1, 2):
        raise ValueError('unsupported upstream shared-expert configuration')


def should_capture(current_fix_routing, requested_fix_routing, matched):
    return (type(current_fix_routing) is bool and current_fix_routing == requested_fix_routing
            and matched == 0)


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
    if len(tensors) != 8:
        raise ValueError(f'expected 8 native arguments, got {len(tensors)}')
    if stage == 'prepare':
        state['target_native_calls'] += 1
        return kernel(*tensors)
    if stage != 'default':
        raise ValueError(f'unknown stage: {stage}')
    # The output is overwritten.  Use another output for all warmup calls.
    warm = list(tensors)
    warm[6] = torch.empty_like(tensors[6])
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
        'target_range': RANGE_NAME, 'requested_fix_routing': params['fix_routing'],
        'current_fixture_fix_routing': None, 'seed': 42, 'correctness': 'not_run',
        'output_semantics': 'grad_logits is overwritten; no input is intentionally mutated',
        'profiler_replay_state': 'unverified' if stage == 'default' else 'not_applicable',
        'profiler_replay_note': 'The actual replay count and output-buffer behavior require on-device verification.',
    }
    record_path = Path(record_path)
    module = None
    original = None
    try:
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(42)
        set_seed(42)
        module = importlib.import_module('tile_kernels.moe.moe_topk_gate_backward_asc')
        original = module.get_moe_topk_gate_backward_kernel_asc

        def replacement(*args, **kwargs):
            kernel = original(*args, **kwargs)
            if not should_capture(state['current_fixture_fix_routing'], params['fix_routing'], state['matched']):
                return kernel
            if len(args) != 3 or args[2] != params['aux_exists']:
                raise RuntimeError('unexpected backward native specialization')

            class Proxy:
                def __call__(self, *tensors):
                    if state['matched']:
                        return kernel(*tensors)
                    state['matched'] = 1
                    symbol = str(kernel.prim_func.attrs['global_symbol'])
                    names = ('scores', 'topk_idx', 'topk_weights', 'grad_topk_weights', 'mask', 'grad_scores_sum')
                    state.update(symbol=symbol, native_symbol=symbol, runtime_kernel=symbol + '_kernel',
                                 source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                                 inputs=[{'name': name, 'tensor': hash_tensor(tensors[i], torch)}
                                         for i, name in enumerate(names)],
                                 routed_scaling_factor=float(tensors[7]),
                                 captured_fix_routing=state['current_fixture_fix_routing'])
                    return invoke_target(kernel, tensors, stage, torch, state)

            return Proxy()

        module.get_moe_topk_gate_backward_kernel_asc = replacement
        test_path = ROOT / 'tests/moe/test_moe_topk_gate_backward.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_moe_backward', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream test: {test_path}')
        test_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(test_module)
        original_get_kwargs = test_module.get_kwargs

        def track_fixture(test_params, fix_routing):
            if type(fix_routing) is not bool:
                raise ValueError('unexpected fixed-routing value in upstream test')
            kwargs = original_get_kwargs(test_params, fix_routing)
            state['current_fixture_fix_routing'] = fix_routing
            if fix_routing == params['fix_routing']:
                names = ('mask', 'bias', 'image_bias', 'image_token_mask', 'fix_routing_mask', 'unmapped_topk_idx')
                state['routing_fixture_inputs'] = [{'name': name, 'tensor': hash_tensor(kwargs[name], torch)}
                                                    for name in names]
            return kwargs

        test_module.get_kwargs = track_fixture
        test_module.test_moe_topk_gate_backward(dict(params))
        if (state['matched'] != 1 or state['target_native_calls'] != 1
                or state.get('captured_fix_routing') != params['fix_routing']):
            raise RuntimeError('did not observe one target call in the planned routing branch')
        state['correctness'] = 'passed_upstream_full_moe_backward_test'
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.get_moe_topk_gate_backward_kernel_asc = original
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
