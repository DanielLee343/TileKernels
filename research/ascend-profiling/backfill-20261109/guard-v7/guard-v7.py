"""Guard one profiler on a selected tbe NPU; kill only its own process group."""
from pathlib import Path
import json,os,re,signal,subprocess,sys,time,traceback

def processes(device, log, state, run=subprocess.run, monotonic=time.monotonic, sleep=time.sleep):
    for attempt in range(3):
        now=monotonic()
        remaining=3-(now-state['last_success']) if state['last_success'] is not None else 3
        if remaining<=0.05:raise RuntimeError('monitor gap reached three seconds')
        timeout=min(0.65,remaining-0.05)
        try:
            q=run(['npu-smi','info','-t','proc-mem','-i',str(device)],capture_output=True,text=True,timeout=timeout)
            state['queries']+=1
            log.write(f'query={state["queries"]} attempt={attempt+1} timeout_s={timeout:.3f} rc={q.returncode}\n{q.stdout}{q.stderr}\n');log.flush()
            ids_raw=re.findall(r'Process id:\s*(\d+)',q.stdout,re.I)
            id_labels=re.findall(r'Process id\s*:',q.stdout,re.I)
            device_ids=re.findall(r'(?im)^\s*NPU ID\s*:\s*(\d+)\s*$',q.stdout)
            empty='No process in device.' in q.stdout
            explicit_error=bool(re.search(r'(?i)failed to query|does not support querying',q.stdout+'\n'+q.stderr))
            recognized=(q.returncode==0 and len(device_ids)==1 and int(device_ids[0])==device and
                        len(ids_raw)==len(id_labels) and not explicit_error and
                        ((bool(ids_raw) and not empty) or (not ids_raw and empty)))
            if not recognized:
                state['query_failures']+=1
                log.write('unrecognized or failed process query; not treated as a successful observation\n');log.flush()
            else:
                now=monotonic()
                if state['last_success'] is not None:
                    gap=now-state['last_success'];state['max_gap']=max(state['max_gap'],gap)
                    if gap>3:raise RuntimeError(f'monitor gap exceeded 3 seconds: {gap:.3f}')
                state['last_success']=now
                return {int(x) for x in ids_raw}
        except subprocess.TimeoutExpired:
            state['queries']+=1;state['query_failures']+=1;state['timeouts']+=1
            log.write(f'query={state["queries"]} attempt={attempt+1} timeout_s={timeout:.3f} TIMEOUT\n');log.flush()
        if attempt<2:sleep(.05)
    raise RuntimeError('three consecutive process queries failed')

def family(pid):
    rows=subprocess.check_output(['ps','-eo','pid=,ppid='],text=True,timeout=2)
    pairs=[tuple(map(int,row.split())) for row in rows.splitlines()];owned={pid}
    while True:
        new=owned|{child for child,parent in pairs if parent in owned}
        if new==owned:break
        owned=new
    # Device tools in containers can report a host PID rather than the PID
    # visible in this namespace. Include both values for our descendants.
    for child in list(owned):
        try:
            for line in Path(f'/proc/{child}/status').read_text().splitlines():
                if line.startswith('NSpid:'):owned.update(map(int,line.split()[1:]))
        except (FileNotFoundError, ProcessLookupError):pass
    return owned

def unexpected_processes(reported,current,seen,exists=lambda pid:Path(f'/proc/{pid}').exists()):
    unexpected=reported-current
    stale={pid for pid in unexpected if pid in seen and not exists(pid)}
    return unexpected-stale,stale

def main():
    if len(sys.argv)<4 or sys.argv[1] not in ('0','3','4'):raise SystemExit('usage: guard-v7.py {0|3|4} MODE_DIR COMMAND...')
    device=int(sys.argv[1]);mode=Path(sys.argv[2]);command=sys.argv[3:]
    if os.environ.get('ASCEND_RT_VISIBLE_DEVICES')!=str(device):raise RuntimeError('visible device differs from monitored device')
    mode.mkdir(parents=True,exist_ok=True)
    (mode/'command.json').write_text(json.dumps(command,indent=2)+'\n')
    state={'last_success':None,'max_gap':0.,'queries':0,'query_failures':0,'timeouts':0};proc=None;error=None;seen_owned=set();stale_owned=set()
    try:
        with (mode/'device-processes.txt').open('w') as log,(mode/'profile.log').open('w') as profile:
            if processes(device,log,state):raise RuntimeError('device busy before capture')
            proc=subprocess.Popen(command,stdout=profile,stderr=subprocess.STDOUT,start_new_session=True);deadline=time.monotonic()+int(os.environ.get('GUARD_DEADLINE_SECONDS','360'))
            try:
                while proc.poll() is None:
                    if time.monotonic()>deadline:raise RuntimeError('profile deadline exceeded')
                    if (mode/'profile.log').stat().st_size>int(os.environ.get('GUARD_MAX_LOG_BYTES',str(512*1024*1024))):
                        raise RuntimeError('profile log exceeds configured limit')
                    reported=processes(device,log,state);current=family(proc.pid);seen_owned.update(current)
                    unexpected,stale=unexpected_processes(reported,current,seen_owned);stale_owned.update(stale)
                    if stale:log.write(f'confirmed exited previously-owned PIDs: {sorted(stale)}\n');log.flush()
                    if unexpected:raise RuntimeError(f'unexpected device PIDs: {sorted(unexpected)}')
                    time.sleep(.5)
            finally:
                if proc.poll() is None:
                    os.killpg(proc.pid,signal.SIGTERM)
                    try:proc.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait(timeout=5)
            reported=processes(device,log,state);unexpected,stale=unexpected_processes(reported,set(),seen_owned);stale_owned.update(stale)
            if unexpected:raise RuntimeError(f'device busy after capture: {sorted(unexpected)}')
            if proc.returncode:raise RuntimeError(f'profiler exit {proc.returncode}')
            if os.environ.get('GUARD_REQUIRE_PROFILE','1')=='1' and 'Op profiling finish' not in (mode/'profile.log').read_text(errors='replace'):raise RuntimeError('missing finish marker')
    except Exception:
        error=traceback.format_exc();(mode/'guard-error.txt').write_text(error)
    summary={'device':device,'query_failures':state['query_failures'],'query_timeouts':state['timeouts'],'queries':state['queries'],
             'max_seconds_between_successful_queries':state['max_gap'],'max_allowed_gap_seconds':3.,
             'status':'failed' if error else 'passed','profiler_returncode':None if proc is None else proc.returncode,
             'exited_previously_owned_pids':sorted(stale_owned),
             'note':'sampled monitoring; brief work between polls cannot be ruled out'}
    (mode/'monitor-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if proc is not None:(mode/'profiler.status').write_text(str(proc.returncode)+'\n')
    if error:print(error,file=sys.stderr);return 1
    print('PASS',mode,flush=True);return 0
if __name__=='__main__':raise SystemExit(main())
