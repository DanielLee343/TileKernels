"""Serially check and capture the 13 frozen cases on idle hidev."""
import argparse
from collections import Counter
import csv
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT=Path('/workspace/tilekernels-finalize-20261107')
WORKER=ROOT/'accuracy_worker.py'
PYTHON='/workspace/tilekernels-env-20261101/venv/bin/python'
METRICS=('OpBasicInfo','ArithmeticUtilization','L2Cache','Memory','MemoryL0','MemoryUB','PipeUtilization','ResourceConflictRatio')

def save(path,data):
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');tmp.replace(path)

def idle():
    p=subprocess.run(['npu-smi','info','-t','proc-mem','-i','0'],capture_output=True,text=True,timeout=30)
    return p.returncode==0 and 'No process in device.' in p.stdout

def execute(cmd,log,timeout=1800):
    with log.open('w') as f:
        proc=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        try:return proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid,signal.SIGTERM)
            try:proc.wait(timeout=20)
            except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
            raise TimeoutError(f'process exceeded {timeout}s and was terminated')

def inspect_capture(item,out):
    rec=json.loads((out/'capture-record.json').read_text())
    assert rec['source_sha256']==item['expected_source_sha256'],'generated source changed'
    assert rec['inputs']==item['expected_inputs'],'target input identity changed'
    assert rec['runtime_kernel']==item['runtime_kernel'],'target kernel changed'
    metrics={}
    for name in METRICS:
        files=list((out/'capture').rglob(name+'.csv'))
        assert len(files)==1,(name,len(files))
        file=files[0];raw=file.read_bytes()
        assert raw,(name,'empty')
        with file.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
        assert rows,(name,'no rows')
        metrics[name]={'path':str(file.relative_to(ROOT)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'rows':len(rows)}
        if name=='OpBasicInfo':
            assert len(rows)==1 and rows[0]['Op Name']==item['runtime_kernel'], 'unexpected OpBasicInfo target'
            assert rows[0]['Op Type']=='vector' and rows[0]['Block Dim']=='56','unexpected device execution'
    return {'same_source':True,'same_inputs':True,'same_kernel':True,
            'original_cpu_reference':rec['reference_check'],'metrics':metrics}

def run(item,action):
    out=ROOT/'cases'/item['id'];out.mkdir(parents=True,exist_ok=True)
    result={'id':item['id'],'family':item['family'],'phase':action,'started':time.time()}
    try:
        if action=='capture':
            cmd=['msprof','op',f'--output={out/"capture"}','--aic-metrics=Default','--replay-mode=kernel',
                '--mstx=true',f'--mstx-include={item["range"]}',f'--kernel-name={item["runtime_kernel"]}',
                '--launch-count=1','--warm-up=5',PYTHON,'-B',str(WORKER),'capture',item['id']]
        else:cmd=[PYTHON,'-B',str(WORKER),'check',item['id']]
        result['command']=cmd;rc=execute(cmd,out/(action+'.log'))
        result['returncode']=rc;assert rc==0,f'{action} returned {rc}'
        if action=='capture':result.update(inspect_capture(item,out))
        else:
            record=json.loads((out/'accuracy-record.json').read_text())
            assert record['source_sha256']==item['expected_source_sha256'] and record['inputs']==item['expected_inputs'],'original identity mismatch'
            comparison=json.loads((out/'reference-comparison.json').read_text())
            result.update(same_source=True,same_inputs=True,comparison=comparison)
        result['status']='completed'
    except Exception as exc:
        result.update(status='failed',reason=f'{type(exc).__name__}: {exc}')
    save(out/(action+'-result.json'),result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=('capture','check'));p.add_argument('--limit',type=int);p.add_argument('--case');args=p.parse_args()
    plan=json.loads((ROOT/'accuracy-plan.json').read_text())['cases']
    if args.phase=='check':plan=[x for x in plan if x['family']=='mhc_pre_apply_mix_bwd']
    if args.case:
        plan=[x for x in plan if x['id']==args.case]
        assert len(plan)==1,'unknown case for phase'
    if args.limit is not None:plan=plan[:args.limit]
    results=[]
    for item in plan:
        file=ROOT/'cases'/item['id']/(args.phase+'-result.json')
        if file.exists():results.append(json.loads(file.read_text()));continue
        if not idle():
            save(ROOT/(args.phase+'-progress.json'),{'status':'stopped_device_busy','results':results,'next':item['id']})
            raise SystemExit('device busy')
        result=run(item,args.phase);results.append(result)
        save(ROOT/(args.phase+'-progress.json'),{'status':'running','counts':dict(Counter(x['status'] for x in results)),
                                               'last':item['id'],'results':results})
        if len(results)>=3 and all(x['status']=='failed' for x in results[-3:]):
            save(ROOT/(args.phase+'-progress.json'),{'status':'stopped_three_failures','results':results})
            raise SystemExit('three consecutive failures')
    save(ROOT/(args.phase+'-progress.json'),{'status':'finished','counts':dict(Counter(x['status'] for x in results)),
                                           'results':results})
