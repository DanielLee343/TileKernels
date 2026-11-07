import json
import os
import sys
from pathlib import Path

sys.path.insert(0, '/workspace/tilekernels-expert-unified-extra-20261106')
import extra_engram_grad as adapter

outdir = Path('/workspace/tilekernels-replay-review-20261107')
original = adapter.invoke_target

def compare(kernel, tensors, stage, torch, state):
    initial = [x.clone() for x in tensors[3:]]
    result = original(kernel, tensors, stage, torch, state)
    actual = [x.clone() for x in tensors[3:]]
    once = [x.clone() for x in initial]
    twice = [x.clone() for x in initial]
    kernel(*tensors[:3], *once)
    kernel(*tensors[:3], *twice)
    kernel(*tensors[:3], *twice)
    torch.npu.synchronize()
    import hashlib
    def digest(x):
        return hashlib.sha256(x.detach().contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()
    info = []
    for a, b, c in zip(actual, once, twice):
        info.append({'actual_sha256':digest(a),'once_sha256':digest(b),'twice_sha256':digest(c),
                     'actual_differs_once':int(torch.count_nonzero(a != b).item()),
                     'once_differs_twice':int(torch.count_nonzero(b != c).item())})
    (outdir / 'comparison.json').write_text(json.dumps(info, indent=2))
    return result

adapter.invoke_target = compare
adapter.run('engram_grad_w_reduce', {'hidden': 1024}, 'default', outdir / 'record.json')
