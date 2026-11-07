"""Recheck the frozen input or collect a profile independently of accuracy."""
import importlib.util
import json
import os
from pathlib import Path
import sys
import traceback

ROOT=Path('/workspace/tilekernels-finalize-20261107')
STARTER=Path('/workspace/tilekernels-expert-profiles-20261106/collect.py')
ADAPTERS={
 'mhc_pre_apply_mix_bwd':Path('/workspace/tilekernels-expert-unified-extra4-20261106/extra_mhc_pre_apply_bwd.py'),
 'mhc_post_bwd':Path('/workspace/tilekernels-expert-unified-extra2-20261106/extra_mhc_post_bwd.py'),
}

def load(path):
    spec=importlib.util.spec_from_file_location('_frozen_adapter',path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def check_pre(x,mix,dy,initial,dx,dmix,reference,torch):
    totals={dev:[{'output':name,'mismatch':0,'max_abs':0.0} for name in ('dx','dmix')] for dev in ('cpu','npu')}
    n,m,h=x.shape
    for start in range(0,n,64):
        end=min(n,start+64)
        for dev in ('cpu','npu'):
            def to(t):return t[start:end].cpu() if dev=='cpu' else t[start:end]
            rx=to(x).float().unsqueeze(0).requires_grad_()
            rm=to(mix).unsqueeze(0).unsqueeze(-1).requires_grad_()
            gx,gm=torch.autograd.grad(reference(rx,rm),(rx,rm),to(dy).unsqueeze(0))
            expected=((to(initial).unsqueeze(0).float()+gx).bfloat16(),gm.squeeze(-1))
            got=(to(dx).unsqueeze(0),to(dmix).unsqueeze(0))
            for val,want,r in zip(got,expected,totals[dev]):
                assert torch.isfinite(val).all() and torch.isfinite(want).all(),(start,dev,r['output'],'nonfinite')
                diff=(val.float()-want.float()).abs()
                r['max_abs']=max(r['max_abs'],float(diff.max().item()))
                r['mismatch']+=int((diff > (0.01+0.001*want.float().abs())).sum().item())
    Path(os.environ['ACCURACY_REPORT']).write_text(json.dumps(totals,indent=2)+'\n')
    if any(r['mismatch'] for v in totals.values() for r in v):
        raise AssertionError('full CPU/NPU precision diagnostics found mismatches; see reference-comparison.json')
    return [{'output':x['output'],'passed':True,'max_abs_error':x['max_abs']} for x in totals['cpu']]

def accuracy(item,out):
    assert item['family']=='mhc_pre_apply_mix_bwd'
    mod=load(ADAPTERS[item['family']]);mod.verify_outputs=check_pre
    report=out/'reference-comparison.json'
    assert not report.exists(),'refusing to reuse a stale reference comparison'
    os.environ['ACCURACY_REPORT']=str(report)
    try:
        mod.run(item['family'],item['params'],'prepare',out/'accuracy-record.json')
    except AssertionError:
        # Mismatches are evidence, not a process failure if the full report exists.
        if not report.is_file():raise

def capture(item,out):
    if item['family']=='moe_normalize_weight':
        mod=load(STARTER)
        passed=mod.application(item['case'],'default',out)
        original=json.loads((out/'default.json').read_text())
        original['profile_capture_process']='completed'
        original['reference_check']='passed' if passed else 'failed'
        (out/'capture-record.json').write_text(json.dumps(original,indent=2)+'\n')
        return
    mod=load(ADAPTERS[item['family']]);real=mod.verify_outputs;failure=[]
    def inspect(*args):
        try:return real(*args)
        except AssertionError:
            failure.append(traceback.format_exc())
            return [{'passed':False,'reference':'original CPU chunk','error':failure[-1]}]
    mod.verify_outputs=inspect
    pending=out/'capture-record.pending.json'
    mod.run(item['family'],item['params'],'default',pending)
    record=json.loads(pending.read_text())
    record['reference_check']='failed' if failure else 'passed'
    record['status']='profiled_precision_failed' if failure else 'profiled_precision_passed'
    (out/'capture-record.json').write_text(json.dumps(record,indent=2)+'\n')
    pending.unlink()

if __name__=='__main__':
    action,cid=sys.argv[1:]
    plan=json.loads((ROOT/'accuracy-plan.json').read_text())['cases']
    item=next(x for x in plan if x['id']==cid)
    out=ROOT/'cases'/cid;out.mkdir(parents=True,exist_ok=True)
    if action=='check':accuracy(item,out)
    elif action=='capture':capture(item,out)
    else:raise ValueError(action)
