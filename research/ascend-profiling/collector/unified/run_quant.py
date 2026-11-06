"""Collect all registered quant modes serially, with one pilot per mode."""
import argparse
import base64
import csv
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT/'quant_cases.json'
METRICS = {'ArithmeticUtilization','L2Cache','Memory','MemoryL0','MemoryUB','PipeUtilization','ResourceConflictRatio'}


def save(path, data):
    q = path.with_suffix('.tmp')
    q.write_text(json.dumps(data, indent=2)+'\n')
    q.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, log, timeout=900):
    with log.open('w') as f:
        p = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGTERM)
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid, signal.SIGKILL)
                p.wait()
            return 124


def idle():
    p = subprocess.run(['npu-smi','info','-t','proc-mem','-i','0'], capture_output=True, text=True, timeout=20)
    return p.returncode == 0 and 'No process in device.' in p.stdout, p.stdout+p.stderr


def inspect_capture(directory, symbol):
    basic, = (directory/'capture').rglob('OpBasicInfo.csv')
    with basic.open(encoding='utf-8-sig', newline='') as f:
        info, = csv.DictReader(f)
    assert info['Op Name'] == symbol and info['Device Id'] == '0' and info['Op Type'] == 'vector', info
    blocks = int(info['Block Dim'])
    assert 1 <= blocks <= 56, blocks
    files = {'OpBasicInfo': {'path': str(basic.relative_to(ROOT)), 'sha256': digest(basic), 'rows': 1}}
    for name in sorted(METRICS):
        path=basic.with_name(name+'.csv')
        with path.open(encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            keys=[(row['block_id'],row['sub_block_id']) for row in reader]
            fields=reader.fieldnames
        assert len(keys)==blocks and set(keys)=={(str(i),'vector0') for i in range(blocks)}, (name,len(keys),blocks)
        files[name]={'path': str(path.relative_to(ROOT)), 'sha256': digest(path),'rows':len(keys),'fields':fields}
    return {'device_id':info['Device Id'],'frequency':info['Current Freq'],'rated_frequency':info['Rated Freq'],
            'type':info['Op Type'],'blocks':blocks,'files':files}


def run_case(case):
    folder=ROOT/'cases'/case['id']
    folder.mkdir(parents=True,exist_ok=False)
    result={'id':case['id'],'family':case['group'],'role':'discovery','plan_case_number':case['plan_case_number']}
    try:
        ok,txt=idle();(folder/'device-before.txt').write_text(txt);assert ok,'NPU not idle before capture'
        enc=base64.urlsafe_b64encode(json.dumps(case['params'],separators=(',',':')).encode()).decode()
        app=[sys.executable,'-B',str(ROOT/'quant_hook.py'),case['group'],enc]
        result['prepare_rc']=run(app+['prepare',str(folder/'prepare.json')],folder/'prepare.log')
        assert result['prepare_rc']==0,'upstream prepare/correctness failed'
        a=json.loads((folder/'prepare.json').read_text());assert a['status']=='passed' and a['matched']==1
        cmd=['msprof','op',f'--output={folder / "capture"}','--aic-metrics=Default','--replay-mode=kernel',
             '--mstx=true','--mstx-include=quant_target',f'--kernel-name={a["runtime_kernel"]}',
             '--launch-count=1','--warm-up=5']+app+['default',str(folder/'default.json')]
        result['default_command']=cmd
        result['default_rc']=run(cmd,folder/'default.log')
        assert result['default_rc']==0,'msprof command failed'
        b=json.loads((folder/'default.json').read_text());assert b['status']=='passed' and b['matched']==1
        assert a['source_sha256']==b['source_sha256'] and a['inputs']==b['inputs'],'source/input mismatch'
        result['capture']=inspect_capture(folder,a['runtime_kernel'])
        ok,txt=idle();(folder/'device-after.txt').write_text(txt)
        result['status']='admitted' if ok else 'needs_review'
        if not ok:result['reason']='NPU not idle after capture'
    except Exception as e:
        result.update(status='failed',reason=f'{type(e).__name__}: {e}')
    save(folder/'result.json',result)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['pilot','remaining']);args=parser.parse_args()
    manifest=json.loads(MANIFEST.read_text());cases=manifest['cases']
    assert len(cases)==120 and len({c['id'] for c in cases})==120
    source=Path('/workspace/tilekernels-env-20261101/src/TileKernels')
    commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    changed=subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
    version=subprocess.check_output(['msprof','op','--version'],text=True)
    device=subprocess.check_output(['npu-smi','info'],text=True)
    assert commit==manifest['source_commit'] and not changed
    assert manifest['msprof_commit'] in version and manifest['device_bus'] in device
    assert os.environ['ASCEND_HOME_PATH'].endswith('/cann-9.2.1')
    save(ROOT/'environment.json',{'source_commit':commit,'msprof':version,'device':device,'manifest_sha256':digest(MANIFEST),'hook_sha256':digest(ROOT/'quant_hook.py')})
    progress_path=ROOT/'progress.json'
    if args.phase=='pilot':
        assert not progress_path.exists()
        result={'status':'running','cases':[]}
    else:
        result=json.loads(progress_path.read_text());assert result['status']=='pilot_finished';result['status']='running'
    admitted={c['family'] for c in result['cases'] if c['status']=='admitted'}
    for c in cases:
        if bool(c['pilot']) != (args.phase=='pilot'):continue
        if args.phase=='remaining' and c['group'] not in admitted:
            folder=ROOT/'cases'/c['id'];folder.mkdir(parents=True,exist_ok=False)
            outcome={'id':c['id'],'family':c['group'],'role':'discovery','status':'skipped','reason':'mode pilot failed'}
            save(folder/'result.json',outcome)
        else:outcome=run_case(c)
        result['cases'].append(outcome);save(progress_path,result)
        print(c['id'],outcome['status'],outcome.get('reason',''),flush=True)
    result['status']='pilot_finished' if args.phase=='pilot' else 'finished';save(progress_path,result)


if __name__=='__main__':main()
