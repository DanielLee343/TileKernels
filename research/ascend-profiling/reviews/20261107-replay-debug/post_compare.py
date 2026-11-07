import json, sys
from pathlib import Path
import torch
import torch_npu
sys.path.insert(0,'/workspace/tilekernels-expert-unified-extra2-20261106')
import extra_mhc_post_bwd as a
root=Path('/workspace/tilekernels-replay-watch-20261107')

def check(inputs,outputs,reference,torch):
    x,residual,post,comb,dout=inputs
    n0,n1,m,h=residual.shape;n=n0*n1
    flat_in=(x.view(n,h),residual.view(n,m,h),post.view(n,m,1),comb.view(n,m,m),dout.view(n,m,h))
    flat_out=(outputs[0].view(n,h),outputs[1].view(n,m,h),outputs[2].view(n,m,1),outputs[3].view(n,m,m))
    names=('grad_x','grad_residual','grad_post_layer_mix','grad_comb_res_mix')
    totals={dev:[{'output':name,'mismatch':0,'max_abs':0.0} for name in names] for dev in ('cpu','npu')}
    for start in range(0,n,64):
        end=min(n,start+64)
        for dev in ('cpu','npu'):
            def to(t): return t[start:end].cpu().unsqueeze(0) if dev=='cpu' else t[start:end].unsqueeze(0)
            host=[to(t) for t in flat_in]
            refs=[v.detach().requires_grad_() for v in host[:4]]
            want=torch.autograd.grad(reference(*refs),refs,host[4])
            for i,(value,expected,r) in enumerate(zip(flat_out,want,totals[dev])):
                got=to(value)
                assert torch.isfinite(got).all() and torch.isfinite(expected).all(), (start,dev,r['output'],'nonfinite')
                rtol,atol=(torch.testing._comparison.default_tolerances(got,expected) if i<2 else (1e-4,1e-4))
                diff=(got.float()-expected.float()).abs()
                r['mismatch']+=int((diff>atol+rtol*expected.float().abs()).sum().item())
                r['max_abs']=max(r['max_abs'],float(diff.max().item()))
    (root/'post-comparison.json').write_text(json.dumps(totals,indent=2)+'\n')
    if any(r['mismatch'] for v in totals.values() for r in v):
        raise RuntimeError('diagnostic comparison found nonzero mismatch count; see post-comparison.json')
    return [{'output':r['output'],'passed':True,'max_abs_error':r['max_abs']} for r in totals['cpu']]

a.verify_outputs=check
a.run('mhc_post_bwd',{'n0':2,'n1':4096,'hidden':7168,'mhc_mult':4},'prepare',root/'post-record.json')
