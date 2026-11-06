"""Capture the planned fn/normw backward with real in-place grad inputs.

CLI: GROUP URLSAFE_BASE64_JSON_PARAMS prepare|default RECORD_JSON
Application warmups use separate clones; profiler replay restoration is unknown.
"""
import argparse
import base64
import ctypes
import hashlib
import importlib
import json
import os
from pathlib import Path
import traceback

GROUP = 'mhc_fn_normw_merge_bwd'
RANGE_NAME = 'mhc_normw_bwd_target'
PLAN_SHA256 = 'e0ec36c25b6f60afb8d19cd3a5839f4a226e0976c87c78de1d86fcf40b9048dd'
PLAN_HIDDEN = (64, 8192, 1024, 128, 1280, 1536, 1792, 192, 2048, 256, 2560,
               3072, 320, 3584, 384, 4096, 4608, 512, 5120, 6144)


def validate_params(params):
    if not isinstance(params, dict) or set(params) != {'hidden_size', 'mhc_mult', 'dtype'}:
        raise ValueError('expected original fn/normw backward parameters')
    hidden, mult, dtype = (params[k] for k in ('hidden_size', 'mhc_mult', 'dtype'))
    if type(hidden) is not int or type(mult) is not int or mult != 4 or dtype != 'fp32':
        raise ValueError('invalid fn/normw backward contract')
    try:
        return PLAN_HIDDEN.index(hidden) + 1
    except ValueError:
        raise ValueError('hidden size is not a planned case') from None


def hash_tensor(tensor, torch):
    h = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        h.update(flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': h.hexdigest()}


def calc_diff(actual, expected, torch):
    delta = actual.float() - expected.float()
    numerator = (delta * delta).sum()
    denominator = (actual.float().square() + expected.float().square()).sum()
    return float(torch.where(denominator == 0, 0.0, numerator / denominator))


def run(group, params, stage, record_path):
    state = {'group': group, 'params': params, 'stage': stage, 'matched': 0,
             'target_range': RANGE_NAME, 'plan_sha256': PLAN_SHA256,
             'capture_scope': 'one fn/normw backward native kernel',
             'output_semantics': 'fn_grad and normw_grad accumulate into nonzero input buffers',
             'warmup_policy': 'separate copies of both gradient buffers',
             'profiler_replay_state': 'unverified' if stage == 'default' else 'not_applicable',
             'device_validation': 'pending'}
    module = original = None
    try:
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('invalid group or stage')
        state['plan_case_number'] = validate_params(params)
        import torch
        import torch_npu  # noqa: F401
        module = importlib.import_module('tile_kernels.mhc.norm_fn_asc')
        wrapper = importlib.import_module('tile_kernels.mhc.norm_fn_kernel')
        state['source_files_sha256'] = {
            'norm_fn_asc.py': hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest(),
            'norm_fn_kernel.py': hashlib.sha256(Path(wrapper.__file__).read_bytes()).hexdigest(),
        }
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        generator = torch.Generator(device='cpu').manual_seed(42)
        h = params['hidden_size'] * params['mhc_mult']
        fn = torch.randn((24, h), dtype=torch.float32, generator=generator)
        normw = torch.randn((h,), dtype=torch.float32, generator=generator)
        dy = torch.randn((24, h), dtype=torch.float32, generator=generator)
        fn_initial = torch.randn((24, h), dtype=torch.float32, generator=generator)
        normw_initial = torch.randn((h,), dtype=torch.float32, generator=generator)
        host = (fn, normw, dy, fn_initial, normw_initial)
        device = tuple(t.to('npu:0') for t in host)
        original = module.mhc_fn_normw_merge_bwd_asc

        def capture_native(*args, **kwargs):
            if state['matched'] or len(args) != 5:
                raise RuntimeError('expected one native call with five tensor arguments')
            compiled = original.compile(*args, **kwargs)
            symbol = str(compiled.prim_func.attrs['global_symbol'])
            state.update(matched=1, symbol=symbol, runtime_kernel=symbol + '_kernel',
                         source_sha256=hashlib.sha256(compiled.get_kernel_source().encode()).hexdigest(),
                         inputs=[hash_tensor(t, torch) for t in args], native_kwargs=kwargs,
                         mutable_input_indices=[3, 4])
            if stage == 'default':
                warmup = (*args[:3], args[3].clone(), args[4].clone())
                for _ in range(5):
                    original(*warmup, **kwargs)
                torch.npu.synchronize()
                del warmup
                api = ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'))
                start, end = api.mstxRangeStartA, api.mstxRangeEnd
                start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
                end.argtypes, end.restype = [ctypes.c_uint64], None
                stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
                handle = start(RANGE_NAME.encode(), stream)
                try:
                    result = original(*args, **kwargs)
                finally:
                    end(handle)
                torch.npu.synchronize()
                return result
            return original(*args, **kwargs)

        module.mhc_fn_normw_merge_bwd_asc = capture_native
        wrapper.mhc_fn_normw_merge_bwd(*device)
        torch.npu.synchronize()
        if state['matched'] != 1:
            raise RuntimeError('target native call not observed')
        expected = (fn_initial + dy * normw, normw_initial + (dy * fn).sum(0))
        state['precision'] = []
        for name, got, want in zip(('fn_grad', 'normw_grad'), device[3:], expected, strict=True):
            diff = calc_diff(got.cpu(), want, torch)
            passed = diff < 1e-8
            state['precision'].append({'output': name, 'passed': passed, 'calc_diff': diff, 'threshold': 1e-8})
            if not passed:
                raise AssertionError(f'{name}: upstream calc_diff threshold failed: {diff}')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        if stage == 'default':
            state['failure_interpretation'] = 'Check profiler replay restoration before attributing failure to kernel.'
        raise
    finally:
        if module is not None and original is not None:
            module.mhc_fn_normw_merge_bwd_asc = original
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
