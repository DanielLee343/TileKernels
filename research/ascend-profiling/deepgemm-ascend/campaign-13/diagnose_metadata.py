"""Save FIRST metadata after the target call; keep upstream checks unchanged."""
import hashlib
import os
from pathlib import Path
import runpy
import sys

import torch
import torch_npu  # noqa: F401
import deep_gemm

original=deep_gemm._C._fp8_fp4_paged_sparse_mqa_logits
first_count=0


def traced(*args,**kwargs):
    global first_count
    result=original(*args,**kwargs)
    is_first=args[4] if len(args)>4 else kwargs['is_first']
    if is_first:
        first_count+=1
        if first_count==6:
            torch.npu.synchronize()
            metadata=args[3] if len(args)>3 else kwargs['metadata']
            data=metadata.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
            target=Path(os.environ['DG_METADATA_DUMP']);target.write_bytes(data)
            print('METADATA_AFTER_FIRST',len(data),hashlib.sha256(data).hexdigest(),str(target),flush=True)
    return result


deep_gemm._C._fp8_fp4_paged_sparse_mqa_logits=traced
script=Path(__file__).resolve().parent/'diagnose_first.py'
sys.argv[0]=str(script)
runpy.run_path(str(script),run_name='__main__')
