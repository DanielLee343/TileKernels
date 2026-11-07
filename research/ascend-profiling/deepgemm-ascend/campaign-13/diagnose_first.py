"""Log the upstream equality failure without changing its pass/fail outcome."""
import json
from pathlib import Path
import runpy
import sys

import torch
import torch_npu  # noqa: F401

original_equal=torch.equal


def traced_equal(a,b):
    same=original_equal(a,b)
    if not same and a.shape==b.shape and a.dtype.is_floating_point and b.dtype.is_floating_point:
        af=a.detach().float().cpu();bf=b.detach().float().cpu();delta=(af-bf).abs()
        finite=torch.isfinite(af)&torch.isfinite(bf)
        payload={'elements':a.numel(),'different':int((af!=bf).sum()),
                 'nonfinite_a':int((~torch.isfinite(af)).sum()),'nonfinite_b':int((~torch.isfinite(bf)).sum()),
                 'max_abs_finite':float(delta[finite].max()) if bool(finite.any()) else None,
                 'mean_abs_finite':float(delta[finite].mean()) if bool(finite.any()) else None,
                 'a_first8':af.flatten()[:8].tolist(),'b_first8':bf.flatten()[:8].tolist(),
                 'a_zero_count':int((af==0).sum()),'b_zero_count':int((bf==0).sum())}
        print('EQUALITY_DIAGNOSTIC',json.dumps(payload),flush=True)
    return same


torch.equal=traced_equal
script=Path(__file__).resolve().parent/'collect.py'
sys.argv[0]=str(script)
runpy.run_path(str(script),run_name='__main__')
