"""Run one pinned mHC pre-big-fuse plan row with upstream exact checks.

CLI: GROUP URLSAFE_BASE64_JSON_PARAMS prepare|default RECORD_JSON
No input padding or size fallback is applied.  The upstream data generator,
GEMM-partials reference, and unfused reference run outside the MSTX range.
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


GROUP = 'mhc_pre_big_fuse_fwd'
RANGE_NAME = 'mhc_big_fuse_target'
PLAN_SHA256 = 'e0ec36c25b6f60afb8d19cd3a5839f4a226e0976c87c78de1d86fcf40b9048dd'
PLAN_SHAPES = (
    (509, 1280), (8192, 5120), (1021, 1280), (512, 5120), (1024, 2560),
    (2048, 4096), (1021, 4160), (1024, 1280), (2048, 1280), (512, 1280),
    (8192, 1280), (1021, 2560), (2048, 2560), (509, 2560), (512, 2560),
    (8192, 2560), (1021, 4096), (1024, 4096), (509, 4096), (512, 4096),
)


def validate_params(params):
    if not isinstance(params, dict) or set(params) != {'n1', 'hidden_size', 'mhc_mult', 'repeat', 'n_splits'}:
        raise ValueError('expected original pre-big-fuse plan parameters')
    n, h, mult, repeat, splits = (params[k] for k in ('n1', 'hidden_size', 'mhc_mult', 'repeat', 'n_splits'))
    if any(type(v) is not int for v in (n, h, mult, repeat, splits)) or (mult, repeat, splits) != (4, 10, 1):
        raise ValueError('invalid pre-big-fuse parameter contract')
    try:
        return PLAN_SHAPES.index((n, h)) + 1
    except ValueError:
        raise ValueError('shape is not a planned pre-big-fuse case') from None


def digest_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def hash_tensor(tensor, torch):
    digest = hashlib.sha256()
    flat = tensor.detach().contiguous().view(-1)
    for start in range(0, flat.numel(), 1_000_000):
        digest.update(flat[start:start + 1_000_000].view(torch.uint8).cpu().numpy().tobytes())
    return {'shape': list(tensor.shape), 'stride': list(tensor.stride()),
            'dtype': str(tensor.dtype), 'sha256': digest.hexdigest()}


def run(group, params, stage, record_path):
    state = {'matched': 0, 'stage': stage, 'group': group, 'params': params,
             'plan_sha256': PLAN_SHA256, 'target_range': RANGE_NAME,
             'capture_scope': 'one pre-big-fuse native kernel',
             'outside_capture': 'upstream input generation, GEMM partials and unfused reference',
             'correctness_scope': 'all three outputs, upstream torch.equal',
             'padding': False, 'device_validation': 'pending'}
    module = original = None
    try:
        if group != GROUP or stage not in ('prepare', 'default'):
            raise ValueError('invalid group or stage')
        state['plan_case_number'] = validate_params(params)
        import torch
        import torch_npu  # noqa: F401
        import tile_kernels
        from tile_kernels.rand import set_seed
        module = importlib.import_module('tile_kernels.mhc.pre_big_fuse_asc')
        wrapper = importlib.import_module('tile_kernels.mhc.pre_big_fuse_kernel')
        test_path = Path(tile_kernels.__file__).resolve().parent.parent / 'tests/mhc/test_pre_big_fuse.py'
        spec = importlib.util.spec_from_file_location('_profile_upstream_pre_big_fuse', test_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f'cannot load upstream tests: {test_path}')
        upstream = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(upstream)
        state['source_files_sha256'] = {
            'test_pre_big_fuse.py': digest_file(test_path),
            'pre_big_fuse_kernel.py': digest_file(wrapper.__file__),
            'pre_big_fuse_asc.py': digest_file(module.__file__),
        }
        torch.set_num_threads(min(8, os.cpu_count() or 1))
        torch.npu.set_device(0)
        random.seed(42)
        set_seed(42)
        test_data = upstream.generate_big_fuse_test_data(
            n1=params['n1'], mhc_mult=params['mhc_mult'], hidden_size=params['hidden_size'],
            sinkhorn_repeat=params['repeat'], n_splits=params['n_splits'])
        mul, sq = upstream.make_gemm_partials(test_data['residual'], test_data['fn'], params['n_splits'])
        if mul.shape[0] != params['n_splits'] or sq.shape[0] != params['n_splits']:
            raise RuntimeError('GEMM partial count does not match plan')
        post, comb, layer, launch = upstream.make_big_fuse_runner(mul, sq, test_data)
        original = module.mhc_pre_big_fuse_fwd_asc

        def capture_native(*args, **kwargs):
            if state['matched']:
                raise RuntimeError('more than one target call observed')
            if len(args) != 13:
                raise RuntimeError(f'expected eight tensors and five scalar parameters, got {len(args)}')
            kernel = original.compile(*args, **kwargs)
            symbol = str(kernel.prim_func.attrs['global_symbol'])
            state.update(matched=1, symbol=symbol, runtime_kernel=symbol + '_kernel',
                         source_sha256=hashlib.sha256(kernel.get_kernel_source().encode()).hexdigest(),
                         inputs=[hash_tensor(t, torch) for t in args[:5]],
                         native_kwargs={**kwargs, 'rms_eps': args[8], 'mhc_pre_eps': args[9],
                                        'mhc_sinkhorn_eps': args[10], 'mhc_post_mult_value': args[11],
                                        'sinkhorn_repeat': args[12]})
            if stage == 'default':
                for _ in range(5):
                    original(*args, **kwargs)
                torch.npu.synchronize()
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

        module.mhc_pre_big_fuse_fwd_asc = capture_native
        launch()
        torch.npu.synchronize()
        if state['matched'] != 1:
            raise RuntimeError('target native call not observed')
        expected = upstream.big_fuse_reference(mul, sq, test_data)
        state['precision'] = []
        for name, got, want in zip(('post_mix', 'comb_mix', 'layer_input'), (post, comb, layer), expected, strict=True):
            passed = bool(torch.equal(got, want))
            state['precision'].append({'output': name, 'passed': passed, 'comparison': 'torch.equal'})
            if not passed:
                raise AssertionError(f'{name} does not match upstream exact reference')
        state['status'] = 'passed'
    except BaseException:
        state.update(status='failed', error=traceback.format_exc())
        raise
    finally:
        if module is not None and original is not None:
            module.mhc_pre_big_fuse_fwd_asc = original
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
