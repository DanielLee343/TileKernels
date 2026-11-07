"""Run isolated experimental 28-core MegaMoE with a single-rank reference."""
import argparse
import ctypes
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('pilot_base',ROOT.parent/'pilot-bf16/collect.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)


def worker(case,source,stage,output):
    import torch
    import torch_npu  # noqa: F401
    import torch.distributed as dist
    import deep_gemm
    sys.path.insert(0,str(Path(source)/'tests'))
    import test_mega_moe
    from deep_gemm.testing.envs import init_dist
    from mega_reference import reference
    from utils import calc_diff

    build=json.loads((Path(source).parent/'build-result.json').read_text())
    if build.get('status')!='built' or base.file_hash(deep_gemm._C.__file__)!=build.get('extension_sha256'):
        raise ValueError('running extension is not the isolated 28-core port')
    if deep_gemm.get_num_sms()!=28:raise ValueError('expected physical 28-Cube board')
    os.environ.setdefault('MASTER_PORT','18361');torch.set_num_threads(4)
    _,world,group=init_dist(0,1)
    if world!=1:raise ValueError('requires one rank')
    obj=None
    try:
        obj=test_mega_moe.MegaMoECase(group,case['hidden'],case['intermediate'],case['experts'],
            case['topk'],case['tokens'],num_shared_experts=0,with_baseline=False)
        obj.create_inputs(case['tokens'])
        def digest(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
        original_data=obj.buffer.x[:case['tokens']].view(torch.uint8).clone()
        tensors={'x':digest(original_data),'sf':digest(obj.buffer.x_sf[:case['tokens']]),
                 'routes':digest(obj.topk_idx),'route_weights':digest(obj.topk_weights),
                 'l1_weights':digest(obj.transformed_l1_weights[0]),'l1_sf':digest(obj.transformed_l1_weights[1]),
                 'l2_weights':digest(obj.transformed_l2_weights[0]),'l2_sf':digest(obj.transformed_l2_weights[1])}
        obj.buffer.x[:case['tokens']].view(torch.uint8).zero_();obj.y.fill_(float('nan'))
        zero=obj.run_fused();torch.npu.synchronize()
        if not bool(torch.isfinite(zero).all()) or not bool((zero==0).all()):raise ValueError('zero-input reference failed')
        expected_counts=torch.bincount(obj.topk_idx.flatten(),minlength=case['experts']).to(torch.int32)
        if not torch.equal(obj.buffer.expert_recv_count.reshape(-1),expected_counts):raise ValueError('route counts failed')
        obj.buffer.x[:case['tokens']].view(torch.uint8).copy_(original_data)
        expected=reference(obj,source);torch.npu.synchronize()
        for _ in range(5):obj.run_fused()
        torch.npu.synchronize();obj.y.fill_(float('nan'))
        if stage=='profile':
            lib=ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
            lib.mstxRangeStartA.argtypes=[ctypes.c_char_p,ctypes.c_void_p];lib.mstxRangeStartA.restype=ctypes.c_uint64
            lib.mstxRangeEnd.argtypes=[ctypes.c_uint64];lib.mstxRangeEnd.restype=None
            handle=lib.mstxRangeStartA(b'dg_mega_port',ctypes.c_void_p(int(torch.npu.current_stream().npu_stream)))
            try:actual=obj.run_fused()
            finally:lib.mstxRangeEnd(handle)
        else:actual=obj.run_fused()
        torch.npu.synchronize()
        if not bool(torch.isfinite(actual).all()):raise ValueError('nonfinite output')
        diff=calc_diff(actual,expected);af=actual.float();ef=expected.float()
        token=((af-ef).square().sum(dim=1)/(af.square()+ef.square()).sum(dim=1).clamp_min(1e-30)).max().item()
        if not math.isfinite(diff) or diff>=5e-6 or not math.isfinite(token) or token>=5e-6:
            raise ValueError(f'nonzero reference failed global={diff} max_token={token}')
        expected_hash=digest(expected);actual_hash=digest(actual)
        Path(output).write_text(json.dumps({'status':'passed','case_id':case['id'],'stage':stage,
            'experimental_port':True,'input_hashes':tensors,'zero_and_counts_passed':True,
            'reference':'single-rank expert-wise upstream fp8xfp4 GEMM + upstream TileLang SwiGLU quant + fp32 combine',
            'reference_sha256':expected_hash,'output_sha256':actual_hash,'diff':diff,'max_token_diff':token,
            'threshold':5e-6,'max_abs_error':float((af-ef).abs().max())},indent=2)+'\n')
    finally:
        if obj is not None:obj.destroy()
        dist.destroy_process_group()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker',action='store_true')
    parser.add_argument('--case',required=True);parser.add_argument('--stage');parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--device',type=int,default=0)
    args=parser.parse_args();cases=json.loads((ROOT/'cases.json').read_text())['cases'];matches=[c for c in cases if c['id']==args.case]
    if len(matches)!=1 or matches[0]['family']!='mega':raise ValueError('unknown MegaMoE case')
    case=matches[0]
    if args.worker:worker(case,args.source,args.stage,args.output);return
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False);state={'case':case,'status':'running','experimental_port':True}
    try:
        idle,state['device_before']=base.device_idle(args.device)
        if not idle:raise RuntimeError('device busy')
        build=json.loads((args.source.resolve().parent/'build-result.json').read_text())
        if build.get('status')!='built':raise RuntimeError('isolated port build not verified')
        state['build']=build;state['runner_sha256']=base.file_hash(__file__)
        state['reference_sha256']=base.file_hash(ROOT/'mega_reference.py')
        state['source_test_sha256']=base.file_hash(args.source/'tests/test_mega_moe.py')
        state['upstream_swiglu_sha256']=base.file_hash(args.source/'third-party/tilelang_ops/swiglu_apply_weight_to_fp8.py')
        env=os.environ.copy();env['ASCEND_RT_VISIBLE_DEVICES']=str(args.device);env['PYTHONDONTWRITEBYTECODE']='1'
        env['DG_JIT_CACHE_DIR']=str(out/'cache')
        common=[sys.executable,'-B',str(Path(__file__).resolve()),'--worker','--case',args.case,'--source',str(args.source.resolve())]
        pre=common+['--stage','prepare','--output',str(out/'prepare.json')]
        state['prepare_command']=pre;state['prepare_exit']=base.run_logged(pre,env,out/'prepare.log',timeout=180)
        if state['prepare_exit']:raise RuntimeError('prepare failed')
        command=['msprof','op','--output='+str(out/'profile'),'--aic-metrics=Default','--replay-mode=kernel',
            '--mstx=true','--mstx-include=dg_mega_port','--kernel-name=*mega_moe_impl*','--launch-count=1','--warm-up=5']
        command+=common+['--stage','profile','--output',str(out/'profile.json')]
        state['profile_command']=command;state['profile_exit']=base.run_logged(command,env,out/'profile.log',timeout=180)
        if state['profile_exit']:raise RuntimeError('profile failed')
        a=json.loads((out/'prepare.json').read_text());b=json.loads((out/'profile.json').read_text())
        for k in ('input_hashes','reference_sha256','output_sha256'):
            if a[k]!=b[k]:raise ValueError('prepare/profile mismatch: '+k)
        basics=list((out/'profile').rglob('OpBasicInfo.csv'))
        if len(basics)!=1:raise ValueError('missing unique profile')
        rows=base.read_csv(basics[0]);row=rows[0]
        if len(rows)!=1 or 'mega_moe_impl' not in row['Op Name']:raise ValueError('wrong kernel')
        dump=basics[0].parent/'dump';binary=dump/'aicore_binary.o'
        if not binary.is_file() or not list(dump.glob('DeviceProf*.bin')):raise ValueError('raw profile missing')
        sha=base.file_hash(binary);matches=[p for p in (out/'cache/cache').glob('*/kernel.o') if base.file_hash(p)==sha]
        if len(matches)!=1:raise ValueError('captured target binary mismatch')
        dst=out/'jit';dst.mkdir()
        for name in ('kernel.asc','kernel.o','meta.json'):
            p=matches[0].parent/name
            if p.is_file():shutil.copy2(p,dst/name)
        for metric in base.METRICS:
            if not base.read_csv(basics[0].with_name(metric+'.csv')):raise ValueError('missing metric '+metric)
        state['capture']={'op_name':row['Op Name'],'op_type':row['Op Type'],'jit_binary_sha256':sha}
        state['raw_files']={str(p.relative_to(out)):{'sha256':base.file_hash(p),'bytes':p.stat().st_size}
                            for p in (out/'profile').rglob('*') if p.is_file()}
        idle,state['device_after']=base.device_idle(args.device)
        if not idle:raise RuntimeError('device remains busy')
        state['status']='passed'
    except Exception:state['status']='failed';state['error']=traceback.format_exc()
    (out/'result.json').write_text(json.dumps(state,indent=2)+'\n');print(args.case,state['status'],flush=True)
    if state['status']!='passed':raise SystemExit(1)


if __name__=='__main__':main()
