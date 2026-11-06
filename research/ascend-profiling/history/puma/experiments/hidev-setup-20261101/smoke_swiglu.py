"""One native TileKernels Ascend smoke; no benchmark or model claims."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import torch
import torch_npu
import tilelang
import tile_kernels
from tile_kernels.config import get_num_vec_cores, is_ascend
from tile_kernels.quant.swiglu_forward_kernel import swiglu_forward

ROOT = Path(__file__).resolve().parent
assert is_ascend(), "TileKernels must select Ascend"
assert torch.npu.is_available(), "NPU unavailable"
torch.npu.set_device(0)
generator = torch.Generator().manual_seed(20261101)
host = (torch.rand((128, 4096), generator=generator) * 2 - 1).bfloat16()
left, right = host.float().chunk(2, dim=-1)
expected = (torch.nn.functional.silu(left) * right).bfloat16()
x = host.to('npu:0')
y = swiglu_forward(x, fmt='bf16')
torch.npu.synchronize()
assert y.device.type == 'npu'
assert list(y.shape) == [128, 2048] and y.dtype == torch.bfloat16
actual = y.cpu()
torch.testing.assert_close(actual, expected, rtol=2**-7, atol=2e-3, equal_nan=False)
cache = Path(os.environ['TILELANG_CACHE_DIR'])
generated = [str(p.relative_to(cache)) for p in cache.rglob('*')
             if p.is_file() and p.suffix in ('.aibin', '.cpp', '.cc', '.so', '.cce')]
assert generated, "Expected native compilation/cache artifacts"
metadata = {
    'status': 'passed', 'scope': 'one native TileKernels SwiGLU Ascend smoke; finite input correctness only; no performance or all-case claim',
    'python': sys.version, 'torch': torch.__version__, 'torch_npu': torch_npu.__version__,
    'tilelang': tilelang.__version__, 'tilelang_file': tilelang.__file__,
    'tilekernels_file': tile_kernels.__file__,
    'tilekernels_commit': subprocess.check_output(['git', '-C', str(ROOT/'src/TileKernels'), 'rev-parse', 'HEAD'], text=True).strip(),
    'device': torch.npu.get_device_name(0), 'vector_cores': get_num_vec_cores(),
    'input_shape': [128, 4096], 'output_shape': [128, 2048], 'dtype': 'bfloat16',
    'seed': 20261101, 'output_elements_checked': actual.numel(),
    'max_absolute_error': (actual.float()-expected.float()).abs().max().item(),
    'rtol': 2**-7, 'atol': 2e-3, 'generated_native_files': generated,
    'ASCEND_HOME_PATH': os.environ.get('ASCEND_HOME_PATH'),
    'cuda_available': torch.cuda.is_available(), 'torch_cuda_build': torch.version.cuda,
}
(ROOT/'smoke-result.json').write_text(json.dumps(metadata, indent=2)+'\n')
print(json.dumps(metadata, indent=2), flush=True)
