"""Prepare and validate the preregistered full-size single-kernel cases."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import torch
import torch_npu
from tilelang import language as T
from tile_kernels.config import get_num_vec_cores
from tile_kernels.quant.common import get_cast_output_config

ROOT = Path(__file__).resolve().parent
FROZEN = ROOT / 'frozen'
CASES = {'I0': (128,4096,4096), 'I16': (128,4096,4112), 'P0': (128,4096,4096), 'P16': (128,4096,4096), 'P32': (128,4096,4096), 'P64': (128,4096,4096), 'D1': (128, 4096, 4096), 'D2': (128, 4096, 4112),
         'D3': (128, 5120, 5120), 'D4': (128, 7168, 7168), 'D5': (1024, 4096, 4096)}
HISTORICAL = {
    'B-L': ['36f05ef4dd57d90cefc2b453a64eb99e8c9807d5399d54baf689e34f0fd4ac73',
            'ea4e7901ee0907567355ba7bc92259c504b80eab740d8832aa49dda5781d1094'],
    'B-H': ['a71adb836103afdfa06e00d457209745dc2369d0734dfb9001811d67377769b6'],
}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tensor_hash(tensor):
    data = tensor.detach().cpu().contiguous().view(-1).view(torch.uint8).numpy().tobytes()
    return hashlib.sha256(data).hexdigest()


def guarded_tensor(host, stride=None):
    rows, cols = host.shape
    stride = stride or cols
    storage = torch.full((128 + rows * stride,), -127, dtype=host.dtype, device='npu:0')
    tensor = storage.as_strided((rows, cols), (stride, 1), storage_offset=64)
    tensor.copy_(host)
    return storage, tensor


def check_guard(storage, rows, cols, stride):
    data = storage.cpu()
    guards = torch.cat((data[:64], data[64 + rows * stride:]))
    if stride > cols:
        guards = torch.cat((guards, data[64:64 + rows * stride].view(rows, stride)[:, cols:].flatten()))
    return bool(torch.all(guards == -127)), guards.numel()


def target_range(launch):
    library = Path(os.environ['ASCEND_HOME_PATH']) / 'tools/mstx/lib64/libms_tools_ext.so'
    api = ctypes.CDLL(str(library))
    start, end = api.mstxRangeStartA, api.mstxRangeEnd
    start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
    end.argtypes, end.restype = [ctypes.c_uint64], None
    stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
    mark = start(b'cold_call', stream)
    try:
        launch()
    finally:
        end(mark)
    torch.npu.synchronize()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('case', choices=tuple(HISTORICAL) + tuple(CASES))
    parser.add_argument('stage', choices=('prepare', 'default'))
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    torch.set_num_threads(8)
    torch.npu.set_device(0)
    inputs_module = load_module('frozen_inputs', FROZEN / 'bridge-inputs.py')
    reference = load_module('cann_rmsnorm', FROZEN / 'bridge-rmsnorm.py')
    case = args.case
    if case == 'B-L':
        cases = json.loads((FROZEN / 'bridge-cases.json').read_text())['cases']
        old = next(x['case'] for x in cases if x['case']['id'] == 'rmsnorm-supp-04')
        host_x, host_w = inputs_module.to_torch(inputs_module.make_arrays(old), old)
        stride = 512
    elif case == 'B-H':
        old = json.loads((FROZEN / 'validation-cases.json').read_text())['entries']['E3']
        host_x, = inputs_module.to_torch(inputs_module.make_arrays(old), old)
        host_w = None
        stride = 4096
    else:
        rows, hidden, stride = CASES[case]
        generator = torch.Generator().manual_seed(20261106)
        host_x = (torch.rand((rows, hidden), generator=generator) * 2 - 1).bfloat16()
        host_w = (torch.rand((hidden,), generator=generator) * 2 - 1).bfloat16()
    hosts = [host_x] + ([host_w] if host_w is not None else [])
    input_hashes = [tensor_hash(tensor) for tensor in hosts]
    if case in HISTORICAL:
        assert input_hashes == HISTORICAL[case], (case, input_hashes)
    rows, hidden = host_x.shape
    x_storage, x = guarded_tensor(host_x, stride)
    input_before = x_storage.cpu().clone()
    weight_storage = weight = None
    if host_w is not None:
        weight_storage, weight2d = guarded_tensor(host_w.unsqueeze(0))
        weight = weight2d.squeeze(0)
        weight_before = weight_storage.cpu().clone()
    if case == 'B-H':
        from tile_kernels.mhc.expand_asc import expand_to_mhc_fwd_asc
        out_storage, out2d = guarded_tensor(torch.full((rows * 4, hidden), -127, dtype=host_x.dtype))
        out = out2d.view(rows, 4, hidden)
        factory = expand_to_mhc_fwd_asc
        native_inputs = (x, out)
        kwargs = {'h_blk': 2048, 'num_stages': 7, 'num_vec_cores': get_num_vec_cores()}
        kernel = factory.compile(*native_inputs, **kwargs)
        _, arguments = factory.func.parse_args(*native_inputs, **kwargs)
        launch = lambda: kernel(*arguments.values())
        expected = host_x.unsqueeze(1).expand(rows, 4, hidden).contiguous()
        out_rows, out_stride = rows * 4, hidden
    elif case == 'B-L':
        from tile_kernels.quant.norm_forward_asc import get_norm_forward_kernel_asc
        out_storage, out = guarded_tensor(torch.full_like(host_x, -127), stride)
        cfg = get_cast_output_config('fp32', (1, 1), False, False, False)
        kernel = get_norm_forward_kernel_asc(hidden=hidden, with_weight=True, with_residual=False,
            eps=1e-6, out_scale=1.0, x_dtype=T.dtype(x.dtype), out_config=cfg,
            with_out_bf16=False, with_rstd=False, num_vec_cores=get_num_vec_cores())
        launch = lambda: kernel(x.unsqueeze(0), out.unsqueeze(0), None, None, weight, None, None, None)
        expected = reference.rms_norm(host_x, host_w, epsilon=1e-6)
        out_rows, out_stride = rows, stride
    else:
        from tile_kernels.quant.norm_forward_kernel import norm_forward
        out_stride = 4096 if case in ('I0', 'I16') else (4096 + int(case[1:]) if case.startswith('P') else stride)
        out_storage, out = guarded_tensor(torch.full_like(host_x, -127), out_stride)
        def launch():
            result = norm_forward(x, weight, eps=1e-6, residual=None, out_scale=1.0,
                                  out=out, residual_out=None, with_rstd=False)
            assert result[0] is out and result[1] is None and result[2] is x
        expected = reference.rms_norm(host_x, host_w, epsilon=1e-6)
        out_rows = rows
    for _ in range(5 if args.stage == "default" else 0):
        launch()
    torch.npu.synchronize()
    if args.stage == 'default':
        target_range(launch)
    else:
        launch()
        torch.npu.synchronize()
    actual = out.cpu()
    if case == 'B-H':
        match = actual.view(torch.int16) == expected.view(torch.int16)
    else:
        rtol, atol = (2**-13, 2e-5) if actual.dtype == torch.float32 else (2**-7, 2e-3)
        match = torch.isclose(actual, expected, rtol=rtol, atol=atol, equal_nan=False)
    x_unchanged = torch.equal(x_storage.cpu(), input_before)
    w_unchanged = weight_storage is None or torch.equal(weight_storage.cpu(), weight_before)
    guards, guard_count = check_guard(out_storage, out_rows, hidden, out_stride)
    written = bool((actual != -127).all())
    assert actual.shape == expected.shape and actual.dtype == expected.dtype
    differences = (actual.float() - expected.float()).abs()
    denominator = expected.float().abs()
    relative = differences / torch.clamp_min(denominator, torch.finfo(torch.float32).tiny)
    data = {'case': case, 'stage': args.stage, 'input_hashes': input_hashes,
            'shape': list(x.shape), 'dtype': str(x.dtype), 'input_stride': list(x.stride()),
            'output_shape': list(out.shape), 'output_stride': list(out.stride()), 'output_sha256': tensor_hash(actual),
            'input_mod128': x.data_ptr() % 128, 'output_mod128': out.data_ptr() % 128,
            'checked': match.numel(), 'mismatch': int((~match).sum()),
            'max_abs_error': float(differences.max()), 'max_relative_error': float(relative.max()),
            'guards_ok': guards, 'guard_elements': guard_count, 'all_written': written,
            'input_unchanged': x_unchanged, 'weight_unchanged': w_unchanged,
            'device': torch.npu.get_device_name(0), 'visible': os.environ.get('ASCEND_RT_VISIBLE_DEVICES')}
    def allocation(t, backing):
        return {'address': int(t.data_ptr()), 'shape': list(t.shape), 'stride': list(t.stride()),
                'element_bytes': t.element_size(), 'backing_address': int(backing.data_ptr()),
                'backing_bytes': backing.numel() * backing.element_size()}
    data['allocations'] = {'input': allocation(x, x_storage), 'output': allocation(out, out_storage),
                           'weight': allocation(weight, weight_storage) if weight is not None else None}
    if case in ('B-H', 'B-L'):
        source = kernel.get_kernel_source()
        (args.output / f'{args.stage}-kernel.cpp').write_text(source)
        data['source_sha256'] = hashlib.sha256(source.encode()).hexdigest()
        data['runtime_kernel'] = str(kernel.prim_func.attrs['global_symbol']) + '_kernel'
    else:
        data['runtime_kernel'] = 'norm_forward_kernel_kernel'
    cache = Path(os.environ['TILELANG_CACHE_DIR'])
    sources = list(cache.rglob('device_kernel.asc'))
    binaries = list(cache.rglob('kernel.aibin'))
    hosts = list(cache.rglob('executable.so'))
    assert len(sources) == len(binaries) == len(hosts) == 1, (sources, binaries, hosts)
    data['generated_source_sha256'] = hashlib.sha256(sources[0].read_bytes()).hexdigest()
    data['device_binary_sha256'] = hashlib.sha256(binaries[0].read_bytes()).hexdigest()
    data['host_binary_sha256'] = hashlib.sha256(hosts[0].read_bytes()).hexdigest()
    data['status'] = 'passed' if bool(match.all()) and guards and written and x_unchanged and w_unchanged else 'failed'
    (args.output / f'{args.stage}.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data), flush=True)
    assert data['status'] == 'passed', data


if __name__ == '__main__':
    main()
