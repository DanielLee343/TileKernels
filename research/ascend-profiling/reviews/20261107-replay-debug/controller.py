"""Run independent, single-device replay diagnostics, never replace captures."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import signal
import subprocess
import time

ROOT=Path('/workspace/tilekernels-replay-watch-batch-v2-20261107')
PROF='/workspace/tilekernels-env-20261101/cann/cann-9.2.1/tools/msopprof/lib64/libmsopprof_injection.so'
SHIM=str(ROOT/'restore_watch.so')
PYTHON='/workspace/tilekernels-env-20261101/venv/bin/python'

def save(path,data):
    tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(data,indent=2)+'\n')
    tmp.replace(path)

def idle():
    r=subprocess.run(['npu-smi','info','-t','proc-mem','-i','0'],capture_output=True,text=True,timeout=30)
    return r.returncode==0 and 'No process in device.' in r.stdout

def run_case(item):
    out=ROOT/'cases'/item['capture_id']
    out.mkdir(parents=True,exist_ok=False)
    result={'case_id':item['case_id'],'capture_id':item['capture_id'],'family':item['family'],'started':time.time()}
    try:
        command=item['original_command']
        i=command.index(PYTHON)
        assert command[i+1]=='-B' and command[i+5]=='default'
        prefix=[('--output='+str(out/'capture')) if x.startswith('--output=') else x for x in command[:i]]
        adapter,group,params=command[i+2],command[i+3],command[i+4]
        cmd=prefix+['env',f'LD_PRELOAD={SHIM}:{PROF}',PYTHON,'-B',str(ROOT/'trace_adapter.py'),
                    adapter,group,params,'default',str(out/'record.json')]
        env=os.environ.copy()
        env.update(REPLAY_WATCH_FAMILY=item['family'],REPLAY_WATCH_DIR=str(out))
        result['command']=cmd
        with (out/'run.log').open('w') as log:
            process=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try: returncode=process.wait(timeout=600)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid,signal.SIGTERM)
                try: process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid,signal.SIGKILL);process.wait()
                raise TimeoutError('profile timed out; terminated the diagnostic process group')
        result['returncode']=returncode
        assert returncode==0, f'profile returned {returncode}'
        actual=json.loads((out/'record.json').read_text())
        result['same_inputs']=actual.get('inputs')==item['expected_inputs']
        result['same_source']=actual.get('source_sha256')==item['expected_source_sha256']
        result['same_kernel']=actual.get('runtime_kernel')==item['expected_runtime_kernel']
        result['original_test_passed']=actual.get('status')=='passed'
        assert all(result[x] for x in ('same_inputs','same_source','same_kernel','original_test_passed')),'identity or correctness mismatch'
        samples=json.loads((out/'watch-metadata.json').read_text())
        rows=[[int(x) for x in line.split()] for line in (out/'watch.log').read_text().splitlines()]
        assert samples and rows and all(len(row)==10 for row in rows), 'missing or malformed restore observations'
        counts=Counter(row[0] for row in rows)
        assert min(counts.values())==len(samples) and max(counts.values())==len(samples),'incomplete restore observation'
        assert len(counts)>=2,'fewer than two observed restore calls'
        assert all(row[2]==1 and row[3]==row[4]==row[5]==row[6]==0 and row[9]==0 for row in rows),'restore/copy/mismatch error'
        coverage=[]
        for line in (out/'coverage.log').read_text().splitlines():
            call,index,base,size,snapshot,success=line.split()
            coverage.append((int(call),int(index),int(base,16),int(size),int(snapshot,16),int(success)))
        for row in rows:
            sample=samples[row[1]]
            matches=[r for r in coverage if r[0]==row[0] and r[1]==row[1] and r[5]==1]
            assert any(r[2]<=sample['tensor_address'] and
                       sample['tensor_address']+sample['span_bytes']<=r[2]+r[3] for r in matches), 'mutable tensor span not covered by observed restored allocation'
        result.update(status='sampled_restore_pass',sample_count=len(samples),restore_call_count=len(counts),
                      sample_bytes=sum(s['sample_bytes'] for s in samples),
                      watched_tensor_spans_covered=True,
                      observed_changed_before_restore=any(row[8]>0 for row in rows),
                      note='Only sampled ranges checked; instrumentation perturbs profile data.')
    except BaseException as exc:
        result.update(status='failed',reason=f'{type(exc).__name__}: {exc}')
    save(out/'result.json',result)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--pilots',action='store_true');parser.add_argument('--limit',type=int);args=parser.parse_args()
    all_cases=json.loads((ROOT/'plan.json').read_text())['cases']
    if args.pilots:
        seen=set();cases=[]
        for item in all_cases:
            if item['family'] not in seen:
                seen.add(item['family']);cases.append(item)
    else:cases=all_cases
    if args.limit is not None: cases=cases[:args.limit]
    results=[]
    for item in cases:
        result_file=ROOT/'cases'/item['capture_id']/'result.json'
        if result_file.exists():
            results.append(json.loads(result_file.read_text()));continue
        if not idle():
            save(ROOT/'progress.json',{'status':'stopped_device_busy','results':results,'next':item['capture_id']})
            raise SystemExit('Device busy; stopped before starting next case')
        result=run_case(item);results.append(result)
        counts=Counter(x['status'] for x in results)
        save(ROOT/'progress.json',{'status':'running','counts':dict(counts),'last':item['capture_id'],'results':results})
        if len(results)>=3 and all(x['status']=='failed' for x in results[-3:]):
            save(ROOT/'progress.json',{'status':'stopped_three_failures','counts':dict(counts),'results':results})
            raise SystemExit('Three successive diagnostic failures; stopped for investigation')
    save(ROOT/'progress.json',{'status':'finished','counts':dict(Counter(x['status'] for x in results)),'results':results})
