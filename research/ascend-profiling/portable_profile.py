"""Run an archived case from this private checkout on a chosen Ascend device.

The case input and native launch remain those of the archived adapter. Profiles
from a different device or software stack are new measurements, not a rewrite
of the original hidev results.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import traceback

RESEARCH=Path(__file__).resolve().parent
REPO=RESEARCH.parents[1]
SOURCE_BASE='c1cf914a82e6901c679445f872051ce44ac2cc63'
METRICS=('ArithmeticUtilization','L2Cache','Memory','MemoryL0','MemoryUB','PipeUtilization','ResourceConflictRatio')

def load_cases(repo):
    collector=Path(repo)/'research/ascend-profiling/collector'
    cases={}
    for batch in ('starter','second','third','fourth','fifth','sixth'):
        manifest=collector/batch/'cases.json'
        for case in json.loads(manifest.read_text())['cases']:
            key=batch+':'+case['id']
            assert key not in cases,key
            cases[key]={'kind':'base','batch':batch,'case':case,'manifest':str(manifest),'range':'cold_call'}
    for name in ('quant','extra','extra2','extra3','extra4','extra5','extra6'):
        filename='quant_cases.json' if name=='quant' else name+'_cases.json'
        manifest=collector/'unified'/filename
        for case in json.loads(manifest.read_text())['cases']:
            key='unified-'+name+':'+case['id']
            assert key not in cases,key
            cases[key]={'kind':'unified','batch':'unified-'+name,'case':case,'manifest':str(manifest),
                        'adapter':case.get('adapter','quant_hook.py'),'range':case.get('range','quant_target')}
    return cases

def lookup_case(cases,key):
    if key not in cases:raise KeyError('unknown case: '+key)
    return cases[key]

def child_environment(repo,device):
    env=os.environ.copy();root=str(Path(repo).resolve())
    env['TILEKERNELS_ROOT']=root
    env['ASCEND_RT_VISIBLE_DEVICES']=str(device)
    env['PYTHONPATH']=root+(os.pathsep+env['PYTHONPATH'] if env.get('PYTHONPATH') else '')
    env['PYTHONDONTWRITEBYTECODE']='1'
    return env

def verify_source_baseline(repo,baseline=SOURCE_BASE):
    def git(*args):
        return subprocess.run(['git','-C',str(repo),*args],capture_output=True,text=True)
    head=git('rev-parse','HEAD')
    if head.returncode:raise RuntimeError('source checkout is not a Git repository')
    if git('merge-base','--is-ancestor',baseline,'HEAD').returncode:
        raise RuntimeError('source baseline is not an ancestor of this checkout')
    paths=('tile_kernels','tests','pyproject.toml')
    if git('diff','--quiet',baseline,'HEAD','--',*paths).returncode:
        raise RuntimeError('source differs from the recorded baseline')
    changed=git('status','--porcelain=v1','--untracked-files=all','--',*paths)
    if changed.returncode or changed.stdout.strip():raise RuntimeError('source worktree has local changes')
    return head.stdout.strip()

def is_recorded_precision_failure(record):
    return (record.get('status')=='failed' and 'Tensor-likes are not close!' in str(record.get('error',''))
            and bool(record.get('runtime_kernel')) and 'inputs' in record and bool(record.get('source_sha256')))

def load_module(path):
    spec=importlib.util.spec_from_file_location('_portable_capture_adapter',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def run_stage(repo,key,stage,out,allow_precision_failure):
    entry=lookup_case(load_cases(repo),key);case=entry['case'];record=out/(stage+'.json')
    sys.path.insert(0,str(repo))
    import tile_kernels
    if not Path(tile_kernels.__file__).resolve().is_relative_to(Path(repo).resolve()):
        raise RuntimeError('tile_kernels did not import from the private checkout')
    if entry['kind']=='base':
        module=load_module(Path(entry['manifest']).parent/'collect.py')
        passed=module.application(case,stage,out)
        if not passed and not allow_precision_failure:raise RuntimeError('precision check failed')
        return
    module=load_module(Path(entry['manifest']).parent/entry['adapter'])
    try:module.run(case['group'],case['params'],stage,record)
    except AssertionError:
        if not allow_precision_failure or not record.is_file():raise
        if not is_recorded_precision_failure(json.loads(record.read_text())):raise

def idle(device):
    cmd=['npu-smi','info','-t','proc-mem','-i',str(device)]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    return result.returncode==0 and 'No process in device.' in result.stdout,result.stdout+result.stderr

def run_logged(cmd,env,path,timeout):
    with path.open('w') as output:
        result=subprocess.run(cmd,env=env,stdout=output,stderr=subprocess.STDOUT,timeout=timeout)
    return result.returncode

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def inspect_capture(out,symbol):
    files=list((out/'capture').rglob('OpBasicInfo.csv'))
    if len(files)!=1:raise RuntimeError('expected exactly one target OpBasicInfo.csv')
    basic=files[0]
    with basic.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
    if len(rows)!=1 or rows[0]['Op Name']!=symbol:raise RuntimeError('captured kernel identity differs')
    result={'OpBasicInfo':{'path':str(basic.relative_to(out)),'sha256':sha(basic),'rows':1}}
    for metric in METRICS:
        path=basic.with_name(metric+'.csv')
        with path.open(encoding='utf-8-sig',newline='') as f:rows=list(csv.DictReader(f))
        if not rows:raise RuntimeError('empty metric table: '+metric)
        keys=[(r['block_id'],r['sub_block_id']) for r in rows]
        if len(keys)!=len(set(keys)):raise RuntimeError('duplicate block rows: '+metric)
        result[metric]={'path':str(path.relative_to(out)),'sha256':sha(path),'rows':len(rows)}
    bins=sorted(str(x.relative_to(out)) for x in (out/'capture').rglob('DeviceProf*.bin'))
    if not bins:raise RuntimeError('no original DeviceProf binary files')
    return {'metrics':result,'device_profiler_binaries':bins}

def run_case(repo,key,device,out,allow_precision_failure=False):
    entry=lookup_case(load_cases(repo),key);head=verify_source_baseline(repo)
    ok,before=idle(device)
    if not ok:raise RuntimeError('selected NPU is busy or its status could not be verified')
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=False)
    env=child_environment(repo,device)
    result={'case':key,'case_parameters':entry['case'],'source_commit':head,'source_baseline':SOURCE_BASE,
            'physical_device':device,'source_root':str(repo),'device_before':before,'status':'running'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    try:
        version=subprocess.run(['msprof','op','--version'],env=env,capture_output=True,text=True,timeout=30)
        if version.returncode:raise RuntimeError('msprof op is not available')
        result.update(msprof_version=version.stdout+version.stderr,cann=os.environ.get('ASCEND_HOME_PATH'),
                      python=sys.version,allow_precision_failure=allow_precision_failure)
        executable=[sys.executable,'-B',str(Path(__file__).resolve()),'__stage',key]
        opt=['--output',str(out)]+(['--allow-precision-failure'] if allow_precision_failure else [])
        prepare=executable+['prepare']+opt
        rc=run_logged(prepare,env,out/'prepare.log',1800)
        result['prepare_rc']=rc
        if rc:raise RuntimeError('preparation failed; see prepare.log')
        before_record=json.loads((out/'prepare.json').read_text())
        symbol=before_record['runtime_kernel']
        command=['msprof','op',f'--output={out/"capture"}','--aic-metrics=Default','--replay-mode=kernel',
                 '--mstx=true',f'--mstx-include={entry["range"]}',f'--kernel-name={symbol}',
                 '--launch-count=1','--warm-up=5']+executable+['default']+opt
        result['default_command']=command
        rc=run_logged(command,env,out/'default.log',1800);result['default_rc']=rc
        if rc:raise RuntimeError('profile collection failed; see default.log')
        after_record=json.loads((out/'default.json').read_text())
        if before_record['source_sha256']!=after_record['source_sha256'] or before_record['inputs']!=after_record['inputs']:
            raise RuntimeError('input or generated kernel changed between preparation and profile')
        result.update(capture=inspect_capture(out,symbol),precision_prepare=before_record.get('status'),
                      precision_default=after_record.get('status'),runtime_kernel=symbol)
        original=RESEARCH/'runs'/('hidev-20261106-'+entry['batch'])/'cases'/entry['case']['id']/'prepare.json'
        if original.is_file():
            old=json.loads(original.read_text())
            result['archived_input_match']=old.get('inputs')==before_record.get('inputs')
            result['archived_generated_source_match']=old.get('source_sha256')==before_record.get('source_sha256')
        else:result['archived_input_match']=None;result['archived_generated_source_match']=None
        result['device_idle_after'],result['device_after']=idle(device)
        result['status']='profile_captured' if result['device_idle_after'] else 'profile_captured_device_review'
    except Exception:
        result.update(status='failed',error=traceback.format_exc())
        raise
    finally:(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    p=sub.add_parser('list');p.add_argument('--json',action='store_true')
    p=sub.add_parser('run');p.add_argument('case');p.add_argument('--device',type=int,default=0);p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-precision-failure',action='store_true')
    p=sub.add_parser('__stage');p.add_argument('case');p.add_argument('stage',choices=('prepare','default'));p.add_argument('--output',type=Path,required=True);p.add_argument('--allow-precision-failure',action='store_true')
    args=parser.parse_args()
    if args.action=='list':
        cases=load_cases(REPO)
        print(json.dumps(sorted(cases),indent=2) if args.json else '\n'.join(sorted(cases)));return
    if args.action=='__stage':run_stage(REPO,args.case,args.stage,args.output,args.allow_precision_failure);return
    result=run_case(REPO,args.case,args.device,args.output,args.allow_precision_failure)
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
