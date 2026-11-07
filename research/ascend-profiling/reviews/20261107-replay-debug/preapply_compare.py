import importlib, json, sys
from pathlib import Path
import torch
import torch_npu
sys.path.insert(0,'/workspace/tilekernels-expert-unified-extra4-20261106')
import extra_mhc_pre_apply_bwd as a
root=Path('/workspace/tilekernels-replay-watch-20261107')

def check(x,mix,dy,initial,dx,dmix,reference,torch):
    totals={dev:[{'output':name,'mismatch':0,'max_abs':0.0} for name in ('dx','dmix')] for dev in ('cpu','npu')}
    n,m,h=x.shape
    for start in range(0,n,64):
        end=min(n,start+64)
        for dev in ('cpu','npu'):
            def to(t): return t[start:end].to('cpu') if dev=='cpu' else t[start:end]
            rx=to(x).float().unsqueeze(0).requires_grad_()
            rm=to(mix).unsqueeze(0).unsqueeze(-1).requires_grad_()
            gx,gm=torch.autograd.grad(reference(rx,rm),(rx,rm),to(dy).unsqueeze(0))
            wants=((to(initial).unsqueeze(0).float()+gx).bfloat16(),gm.squeeze(-1))
            got=(to(dx).unsqueeze(0),to(dmix).unsqueeze(0))
            for v,w,r in zip(got,wants,totals[dev]):
                assert torch.isfinite(v).all() and torch.isfinite(w).all(), (start,dev,r['output'],'nonfinite')
                diff=(v.float()-w.float()).abs()
                r['max_abs']=max(r['max_abs'],float(diff.max().item()))
                r['mismatch']+=int((diff > (0.01+0.001*w.float().abs())).sum().item())
    (root/'preapply-comparison.json').write_text(json.dumps(totals,indent=2)+'\n')
    if any(r['mismatch'] for v in totals.values() for r in v):
        raise RuntimeError('diagnostic comparison found nonzero mismatch count; see preapply-comparison.json')
    return [{'output':r['output'],'passed':True,'max_abs_error':r['max_abs']} for r in totals['cpu']]

a.verify_outputs=check
a.run('mhc_pre_apply_mix_bwd',{'n0':2,'n1':1024,'hidden':2560,'mhc_mult':4},'prepare',root/'preapply-record.json')
