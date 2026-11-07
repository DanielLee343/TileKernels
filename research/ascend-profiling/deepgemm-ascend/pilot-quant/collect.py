"""Collect DeepGEMM low-precision GEMM profiles using upstream input generators."""
import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parent
BASE_PATH = ROOT.parent/'pilot-bf16/collect.py'
spec = importlib.util.spec_from_file_location('bf16_pilot', BASE_PATH)
base = importlib.util.module_from_spec(spec); spec.loader.exec_module(base)


def validate_case(case):
    mapping = {('fp8','fp8'): ('fp8_gemm','fp8_gemm_impl'),
               ('fp4','fp4'): ('fp4_gemm','fp8_gemm_impl'),
               ('fp8','fp4'): ('fp8_dequant_gemm','fp8_dequant_gemm_impl')}
    if (not isinstance(case.get('id'), str) or not case['id'] or
        any(not isinstance(case.get(x), int) or case[x] <= 0 for x in ('m','n','k')) or
        mapping.get((case.get('a_dtype'),case.get('b_dtype'))) != (case.get('jit_prefix'),case.get('kernel_marker'))):
        raise ValueError('case outside low-precision GEMM contract')


def parse_kernel_symbol(readelf_output, marker):
    names = set(re.findall(r'\.ascend\.meta\.([^\s]+)', readelf_output))
    targets = [x for x in names if marker in x]
    if len(targets) != 1: raise ValueError('ELF does not contain exactly one target symbol')
    return targets[0]


def validate_stages(before, after, case_id):
    base.validate_stages(before, after, case_id)
    for key in ('target_sha256','target_symbol'):
        if not before.get(key) or before[key] != after.get(key): raise ValueError('target mismatch: '+key)


def find_target(case, cache):
    matches = list((Path(cache)/'cache').glob(case['jit_prefix']+'.*/kernel.o'))
    if len(matches) != 1: raise ValueError('expected exactly one target JIT binary: '+str(matches))
    path = matches[0]
    result = subprocess.run(['readelf','-SW',str(path)],capture_output=True,text=True,check=True)
    return path, parse_kernel_symbol(result.stdout, case['kernel_marker'])


def inspect_capture(profile, case, expected_sha):
    files = list(Path(profile).rglob('OpBasicInfo.csv'))
    if len(files)!=1: raise ValueError('expected one captured target, got '+str(len(files)))
    rows = base.read_csv(files[0])
    if len(rows)!=1 or rows[0].get('Op Type','').lower() not in ('cube','mix') or case['kernel_marker'] not in rows[0].get('Op Name',''):
        raise ValueError('unexpected kernel type or identity')
    metrics={}
    for metric in base.METRICS:
        path=files[0].with_name(metric+'.csv'); records=base.read_csv(path)
        keys=[(r.get('block_id'),r.get('sub_block_id')) for r in records]
        if not keys or any(not all(x) for x in keys) or len(set(keys))!=len(keys):
            raise ValueError('missing or duplicate metric rows: '+metric)
        metrics[metric]={'rows':len(records),'sha256':base.file_hash(path)}
    pipes=base.read_csv(files[0].with_name('PipeUtilization.csv'))
    cube=[r for r in pipes if str(r.get('sub_block_id','')).startswith('cube')]
    active=[r for r in cube if r.get('aic_cube_time(us)') not in (None,'','NA') and float(r['aic_cube_time(us)'])>0]
    if not active: raise ValueError('no Cube activity')
    dump=files[0].parent/'dump';binary=dump/'aicore_binary.o'
    if not binary.is_file() or not list(dump.glob('DeviceProf*.bin')) or base.file_hash(binary)!=expected_sha:
        raise ValueError('missing raw data or captured binary mismatch')
    return {'op_name':rows[0]['Op Name'],'op_type':rows[0]['Op Type'].lower(),
            'block_dim':rows[0].get('Block Dim'),'mix_block_dim':rows[0].get('Mix Block Dim'),
            'cube_rows':len(cube),'cube_active_rows':len(active),'binary_sha256':expected_sha,'metrics':metrics}


def worker(case, stage, out, source):
    import ctypes
    import torch
    import torch_npu  # noqa: F401
    import deep_gemm
    sys.path.insert(0,str(Path(source)/'tests'))
    from generators import GemmTestDesc, GemmType, Major
    validate_case(case);torch.npu.set_device(0);torch.set_num_threads(4)
    dtype={'fp8':torch.float8_e4m3fn,'fp4':torch.float4_e2m1fn_x2}
    desc=GemmTestDesc(GemmType.Normal,dtype[case['a_dtype']],dtype[case['b_dtype']],torch.bfloat16,
                      (case['m'],case['n'],case['k']),Major.K,Major.K,accumulate=False,recipe=(1,1,32))
    _,a,b,_,reference,_=desc.generate()
    output=torch.empty_like(reference)
    def launch():deep_gemm.fp8_fp4_gemm_nt(a,b,output,recipe=(1,1,32))
    for _ in range(5):launch()
    torch.npu.synchronize()
    binary,symbol=find_target(case,os.environ['DG_JIT_CACHE_DIR'])
    if stage=='profile':
        api=ctypes.CDLL(str(Path(os.environ['ASCEND_HOME_PATH'])/'tools/mstx/lib64/libms_tools_ext.so'))
        api.mstxRangeStartA.argtypes=[ctypes.c_char_p,ctypes.c_void_p];api.mstxRangeStartA.restype=ctypes.c_uint64
        api.mstxRangeEnd.argtypes=[ctypes.c_uint64];api.mstxRangeEnd.restype=None
        handle=api.mstxRangeStartA(b'deepgemm_quant_target',ctypes.c_void_p(int(torch.npu.current_stream().npu_stream)))
        try:launch()
        finally:api.mstxRangeEnd(handle)
    else:launch()
    torch.npu.synchronize(); actual=output.cpu(); expected=reference.cpu(); af=actual.float(); ef=expected.float()
    finite_output=bool(torch.isfinite(af).all().item());finite_expected=bool(torch.isfinite(ef).all().item())
    denominator=(af*af+ef*ef).sum();diff=float((1-2*(af*ef).sum()/denominator).item()) if denominator.item() else 0.0
    def tensor_hash(t):return hashlib.sha256(t.detach().cpu().contiguous().view(torch.uint8).numpy().tobytes()).hexdigest()
    def describe(item):
        return [{'shape':list(t.shape),'stride':list(t.stride()),'dtype':str(t.dtype),'sha256':tensor_hash(t)} for t in item]
    da,db=describe(a),describe(b)
    def combined(items):return hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest()
    record={'case_id':case['id'],'stage':stage,'input_a':da,'input_b':db,'input_a_sha256':combined(da),
            'input_b_sha256':combined(db),'reference_sha256':tensor_hash(expected),'output_sha256':tensor_hash(actual),
            'output_finite':finite_output,'reference_finite':finite_expected,'diff':diff,'threshold':base.THRESHOLD,
            'max_abs_error':float((af-ef).abs().max().item()),'checked_elements':case['m']*case['n'],
            'target_sha256':base.file_hash(binary),'target_symbol':symbol,'target_path':str(binary),
            'reference':'upstream GemmTestDesc.generate, NPU FP32 decoded matmul rounded to BF16'}
    record['status']='passed' if finite_output and finite_expected and math.isfinite(diff) and diff<base.THRESHOLD else 'failed'
    Path(out).write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    if record['status']!='passed':raise ValueError('precision failed')


def run_case(case,source,output,device,cache_root):
    output=Path(output);output.mkdir(parents=True,exist_ok=False);result=output/'result.json'
    state={'case':case,'status':'running','source_commit':base.BASELINE,'physical_device':device}
    try:
        ok,state['device_before']=base.device_idle(device)
        if not ok:raise RuntimeError('device busy or status unavailable')
        env=os.environ.copy();env['ASCEND_RT_VISIBLE_DEVICES']=str(device);env['PYTHONDONTWRITEBYTECODE']='1'
        env['DG_JIT_CACHE_DIR']=str(Path(cache_root)/case['id'])
        common=[sys.executable,'-B',str(Path(__file__).resolve()),'__worker',case['id']]
        prepare=common+['prepare',str(output/'prepare.json'),str(source)]
        state['prepare_command']=prepare;rc=base.run_logged(prepare,env,output/'prepare.log');state['prepare_exit']=rc
        if rc:raise RuntimeError('prepare failed: see prepare.log')
        before=json.loads((output/'prepare.json').read_text());base.validate_stage(before,case['id'])
        command=['msprof','op','--output='+str(output/'profile'),'--aic-metrics=Default','--replay-mode=kernel',
                 '--mstx=true','--mstx-include=deepgemm_quant_target','--kernel-name=*'+case['kernel_marker']+'*',
                 '--launch-count=1','--warm-up=5']+common+['profile',str(output/'profile.json'),str(source)]
        state['profile_command']=command;rc=base.run_logged(command,env,output/'profile.log');state['profile_exit']=rc
        if rc:raise RuntimeError('profile failed: see profile.log')
        after=json.loads((output/'profile.json').read_text());validate_stages(before,after,case['id'])
        state['capture']=inspect_capture(output/'profile',case,before['target_sha256'])
        target=Path(before['target_path']).parent;dst=output/'jit';dst.mkdir()
        for name in ('kernel.asc','kernel.o','meta.json'):shutil.copy2(target/name,dst/name)
        state['raw_files']={str(p.relative_to(output)):{'sha256':base.file_hash(p),'bytes':p.stat().st_size}
                            for p in (output/'profile').rglob('*') if p.is_file()}
        state['device_idle_after'],state['device_after']=base.device_idle(device)
        state['status']='passed' if state['device_idle_after'] else 'captured_device_review'
    except Exception:
        state['status']='failed';state['error']=traceback.format_exc()
    finally:result.write_text(json.dumps(state,indent=2)+'\n')
    return state


def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('__worker');p.add_argument('case_id');p.add_argument('stage',choices=('prepare','profile'));p.add_argument('out');p.add_argument('source')
    p=sub.add_parser('batch');p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--cache-root',type=Path,required=True);p.add_argument('--device',type=int,default=0);p.add_argument('--case',action='append')
    args=parser.parse_args();manifest=json.loads((ROOT/'cases.json').read_text());cases=manifest['cases']
    for case in cases:validate_case(case)
    if args.action=='__worker':
        found=[c for c in cases if c['id']==args.case_id]
        if len(found)!=1:raise ValueError('unknown case')
        worker(found[0],args.stage,args.out,args.source);return
    cases=base.select_cases(cases,args.case)
    head=subprocess.check_output(['git','-C',str(args.source),'rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(['git','-C',str(args.source),'status','--porcelain'],text=True)
    if head!=base.BASELINE or dirty:raise RuntimeError('source differs from baseline')
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=False)
    state={'source_commit':head,'source_status':dirty,'source_submodules':subprocess.check_output(['git','-C',str(args.source),'submodule','status'],text=True),'manifest_sha256':base.file_hash(ROOT/'cases.json'),'collector_sha256':base.file_hash(__file__),'base_collector_sha256':base.file_hash(BASE_PATH),'device':args.device,'python':sys.version,'cases':[]}
    (out/'batch.json').write_text(json.dumps(state,indent=2)+'\n')
    for case in cases:
        result=run_case(case,args.source,out/case['id'],args.device,args.cache_root.resolve())
        state['cases'].append({'id':case['id'],'status':result['status']});(out/'batch.json').write_text(json.dumps(state,indent=2)+'\n');print(case['id'],result['status'],flush=True)
    if any(x['status']!='passed' for x in state['cases']):raise SystemExit(1)


if __name__=='__main__':main()
