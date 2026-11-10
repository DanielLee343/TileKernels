"""Capture named upstream DeepGEMM kernels using their upstream correctness tests."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent/'pilot-bf16'/'collect.py'
spec = importlib.util.spec_from_file_location('pilot_base', BASE)
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)


def worker(case, source, stage, output):
    if stage=='profile':output=str(Path(output).with_name('profile-'+str(os.getpid())+'.json'))
    import torch
    import torch_npu  # noqa: F401
    import deep_gemm
    sys.path.insert(0, str(Path(source)/'tests'))
    import test_attention as attention
    import test_layout as layout
    from generators import GemmType, Major
    seed = 7711
    random.seed(seed); torch.manual_seed(seed); torch.npu.manual_seed(seed)
    torch.npu.set_device(0); torch.set_num_threads(4)
    owner = deep_gemm._C if case['family']=='sleep' else deep_gemm
    original = getattr(owner, case['api'])
    calls=[]

    def describe(value):
        if isinstance(value, torch.Tensor):
            raw=value.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()
            return {'dtype':str(value.dtype),'shape':list(value.shape),'stride':list(value.stride()),
                    'sha256':hashlib.sha256(raw).hexdigest()}
        if isinstance(value, (tuple,list)):
            return [describe(x) for x in value]
        if isinstance(value, dict):return {str(k):describe(v) for k,v in sorted(value.items())}
        if value is None or isinstance(value,(str,int,float,bool)):return value
        return {'type':str(type(value))}

    def addresses(value):
        if isinstance(value, torch.Tensor):
            return {'device':str(value.device),'address':hex(value.data_ptr()),'dtype':str(value.dtype),
                    'shape':list(value.shape),'stride':list(value.stride()),'element_size':value.element_size()}
        if isinstance(value,(list,tuple)):return [addresses(x) for x in value]
        if isinstance(value,dict):return {str(k):addresses(v) for k,v in value.items()}
        return None

    def intercepted(*args, **kwargs):
        if calls:return original(*args, **kwargs)
        record={'args':describe(args),'kwargs':describe(kwargs)}; calls.append(record)
        if stage=='profile' and case['target']=='paged_sparse_mqa_logits_impl':
            m=kwargs['metadata'];raw=m.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes();Path(output).with_name('frozen-prewarm-'+str(os.getpid())+'.bin').write_bytes(raw)
        for _ in range(5):original(*args, **kwargs)
        torch.npu.synchronize()
        if stage=='profile' and case['target']=='paged_sparse_mqa_logits_impl':
            m=kwargs['metadata'];raw=m.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes();Path(output).with_name('frozen-after-warmups-'+str(os.getpid())+'.bin').write_bytes(raw)
            state=getattr(m,'_paged_sparse_mqa_state',None);Path(output).with_name('frozen-post-warmup-state-'+str(os.getpid())+'.json').write_text(json.dumps({'sha256':hashlib.sha256(raw).hexdigest(),'state_repr':repr(state)},indent=2)+'\n')
        if stage=='profile':
            lib=ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
            lib.mstxRangeStartA.argtypes=[ctypes.c_char_p,ctypes.c_void_p];lib.mstxRangeStartA.restype=ctypes.c_uint64
            lib.mstxRangeEnd.argtypes=[ctypes.c_uint64];lib.mstxRangeEnd.restype=None
            handle=lib.mstxRangeStartA(b'dg_campaign_target',ctypes.c_void_p(int(torch.npu.current_stream().npu_stream)))
            try:value=original(*args, **kwargs)
            finally:lib.mstxRangeEnd(handle)
        else:value=original(*args, **kwargs)
        torch.npu.synchronize()
        if stage=='profile' and case['target']=='paged_sparse_mqa_logits_impl':
            m=kwargs['metadata'];raw=m.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes();Path(output).with_name('frozen-after-target-'+str(os.getpid())+'.bin').write_bytes(raw)
            Path(output).with_name('frozen-addresses-'+str(os.getpid())+'.json').write_text(json.dumps({'args':addresses(args),'kwargs':addresses(kwargs),'returned':addresses(value)},indent=2)+'\n')
        return value

    setattr(owner,case['api'],intercepted)
    family=case['family']
    if family=='mqa':
        attention.run_mqa_logits_case(case['q'],case['k'],case['heads'],case['head_dim'],True,
                                      case['fp4'],getattr(attention.Mode,case['mode']))
        validation='upstream test_attention.run_mqa_logits_case'
    elif family=='paged_mqa':
        attention.run_paged_mqa_logits_case(case['batch'],case['heads'],case['head_dim'],case['k'],
            case['fp4'],[1]*case['batch'],case['page'],case['ascend_layout'],skip_prof=True)
        validation='upstream test_attention.run_paged_mqa_logits_case'
    elif family=='sparse':
        attention.run_sparse_mqa_logits_case(case['heads'],case['fp4'],case['paged'],case['q'],case['k'],
            case['sparse_block'],case['max_blocks'],True,num_repeats=1,page_kv=case['page'])
        validation='upstream sparse MQA vs full MQA and repeat checks'
    elif family=='transform':
        dtype={'float32':torch.float32,'int16':torch.int16}[case['dtype']]
        desc=(GemmType.Normal,dtype,getattr(Major,case['major']),case['mn'],case['k'],case['gran_mn'],None,256,None)
        sf,run,expected=layout.make_layout_case(desc);actual=run();torch.npu.synchronize();layout.check_layout(actual,expected)
        validation='upstream test_layout.check_layout exact output and strides'
    elif family=='sleep':
        original_call=lambda:deep_gemm._C.npu_sleep(case['cycles'],marker=case['marker'])
        original_call();torch.npu.synchronize()
        validation='auxiliary sleep completed and synchronized; no numerical output'
    else:raise ValueError('unknown family')
    if len(calls)!=1:raise ValueError('target API was never intercepted')
    Path(output).write_text(json.dumps({'case_id':case['id'],'stage':stage,'status':'passed',
        'seed':seed,'validation':validation,'target_input':calls[0]},indent=2)+'\n')


def inspect_profile(case, root, cache):
    basics=list(Path(root).rglob('OpBasicInfo.csv'))
    if len(basics)!=1:raise ValueError('expected one target profile, got '+str(len(basics)))
    row=base.read_csv(basics[0]);
    if len(row)!=1 or case['target'] not in row[0].get('Op Name',''):
        raise ValueError('unexpected target name')
    directory=basics[0].parent;binary=directory/'dump'/'aicore_binary.o'
    if not binary.is_file() or not list((directory/'dump').glob('DeviceProf*.bin')):
        raise ValueError('raw profile binary or data absent')
    sha=base.file_hash(binary)
    matches=[p for p in (Path(cache)/'cache').glob('*/kernel.o') if base.file_hash(p)==sha]
    if len(matches)!=1:raise ValueError('captured binary not uniquely identified in JIT cache')
    metrics={}
    for metric in base.METRICS:
        p=directory/(metric+'.csv'); rows=base.read_csv(p)
        keys=[(x.get('block_id'),x.get('sub_block_id')) for x in rows]
        if not keys or any(not all(x) for x in keys) or len(keys)!=len(set(keys)):
            raise ValueError('empty or duplicate metric rows: '+metric)
        metrics[metric]=len(rows)
    return {'op_name':row[0]['Op Name'],'op_type':row[0]['Op Type'],
            'jit_binary_sha256':sha,'jit_directory':str(matches[0].parent),'metric_rows':metrics}


def run_case(case, source, output, cache_root, device):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);result={'case':case,'status':'running'}
    try:
        idle,result['device_before']=base.device_idle(device)
        if not idle:raise RuntimeError('device busy')
        env=os.environ.copy();env['ASCEND_RT_VISIBLE_DEVICES']=str(device)
        cache=Path(cache_root)/case['id'];env['DG_JIT_CACHE_DIR']=str(cache);env['PYTHONDONTWRITEBYTECODE']='1'
        args=[sys.executable,'-B',str(Path(__file__).resolve()),'__worker',case['id']]
        pre=args+['prepare',str(output/'prepare.json'),str(source)]
        result['prepare_command']=pre;result['prepare_exit']=base.run_logged(pre,env,output/'prepare.log')
        if result['prepare_exit']:raise RuntimeError('upstream validation failed in prepare')
        command=['msprof','op','--output='+str(output/'profile'),'--aic-metrics=Default','--replay-mode=kernel',
                 '--mstx=true','--mstx-include=dg_campaign_target','--kernel-name=*'+case['target']+'*',
                 '--launch-count=1','--warm-up=5']+args+['profile',str(output/'profile.json'),str(source)]
        result['profile_command']=command;result['profile_exit']=base.run_logged(command,env,output/'profile.log')
        if result['profile_exit']:raise RuntimeError('profile process failed')
        a=json.loads((output/'prepare.json').read_text());b=json.loads((output/'profile.json').read_text())
        if a['status']!='passed' or b['status']!='passed' or a['target_input']!=b['target_input']:
            raise ValueError('upstream validation or target inputs changed between stages')
        result['capture']=inspect_profile(case,output/'profile',cache)
        dst=output/'jit';dst.mkdir();jit=Path(result['capture']['jit_directory'])
        for name in ('kernel.asc','kernel.o','meta.json'):
            if (jit/name).is_file():shutil.copy2(jit/name,dst/name)
        result['raw_files']={str(p.relative_to(output)):{'sha256':base.file_hash(p),'bytes':p.stat().st_size}
                             for p in (output/'profile').rglob('*') if p.is_file()}
        idle,result['device_after']=base.device_idle(device)
        if not idle:raise RuntimeError('device still busy after case')
        result['status']='passed'
    except Exception:result['status']='failed';result['error']=traceback.format_exc()
    (output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('__worker');p.add_argument('id');p.add_argument('stage');p.add_argument('output');p.add_argument('source')
    p=sub.add_parser('batch');p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--device',type=int,default=0);p.add_argument('--case',action='append')
    args=parser.parse_args();manifest=json.loads((ROOT/'cases.json').read_text());cases=manifest['cases']
    if args.action=='__worker':
        selected=[x for x in cases if x['id']==args.id]
        if len(selected)!=1:raise ValueError('unknown case')
        worker(selected[0],args.source,args.stage,args.output);return
    source=args.source.resolve();head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
    if head!=manifest['source_commit'] or dirty:raise RuntimeError('source mismatch or dirty')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    state={'source_commit':head,'cases_sha256':base.file_hash(ROOT/'cases.json'),
           'collector_sha256':base.file_hash(__file__),'base_collector_sha256':base.file_hash(BASE),'device':args.device,'cases':[]}
    selected=base.select_cases(cases,args.case)
    for case in selected:
        result=run_case(case,source,out/case['id'],args.cache_root.resolve(),args.device)
        state['cases'].append({'id':case['id'],'status':result['status']})
        (out/'batch.json').write_text(json.dumps(state,indent=2)+'\n')
        print(case['id'],result['status'],flush=True)
    if any(x['status']!='passed' for x in state['cases']):raise SystemExit(1)


if __name__=='__main__':main()
