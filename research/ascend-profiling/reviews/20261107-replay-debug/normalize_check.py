import hashlib, json
from pathlib import Path
import torch
import torch_npu
from tile_kernels.moe.normalize_weight_kernel import normalize_weight as kernel_op
from tile_kernels.torch.moe import normalize_weight as reference_op

torch.npu.set_device(0)
torch.set_num_threads(8)
results=[]
for cid,n in (('normalize-03',127),('normalize-16',128),('normalize-20',4001)):
    seed=int.from_bytes(hashlib.sha256(cid.encode()).digest()[:8], 'little')
    rng=torch.Generator(device='cpu').manual_seed(seed)
    x=torch.rand((n,32),generator=rng)
    sha=hashlib.sha256(x.contiguous().view(-1).view(torch.uint8).numpy().tobytes()).hexdigest()
    dx=x.to('npu:0')
    actual=kernel_op(dx)
    device=reference_op(dx)
    cpu=reference_op(x)
    torch.npu.synchronize()
    row={'id':cid,'input_sha256':sha,'shape':[n,32],'results':[]}
    for name,a,b,c in zip(('denominator','weights'),actual,device,cpu):
        a=a.cpu();b=b.cpu()
        assert torch.isfinite(a).all() and torch.isfinite(b).all() and torch.isfinite(c).all(), (cid,name,'nonfinite')
        difdev=(a.double()-b.double()).abs();difcpu=(a.double()-c.double()).abs()
        row['results'].append({'output':name,
          'max_abs_vs_npu':difdev.max().item(), 'num_over_2e-6_vs_npu':int((difdev>2e-6).sum().item()),
          'max_abs_vs_cpu':difcpu.max().item(), 'num_over_2e-6_vs_cpu':int((difcpu>2e-6).sum().item())})
    results.append(row)
Path('/workspace/tilekernels-replay-watch-20261107/normalize-comparison.json').write_text(json.dumps(results,indent=2)+'\n')
