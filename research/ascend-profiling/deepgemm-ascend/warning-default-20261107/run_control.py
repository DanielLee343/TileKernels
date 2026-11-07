"""Run the pre-registered missing-vs-explicit-default kernel.json control."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import traceback

CASES = ('bf16-m1-n576-k7168', 'bf16-m1-n32768-k512')
SEQUENCE = ('A', 'B', 'B', 'A', 'A', 'B')


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--collector', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    project = args.project.resolve(); collector = args.collector.resolve(); output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    state = {'status': 'preparing', 'sequence': SEQUENCE, 'cases': {}, 'runs': []}
    report = output/'control.json'
    try:
        for cid in CASES:
            matches = list((collector.parent/'runs').glob('*/'+cid+'/result.json'))
            if len(matches) != 1: raise RuntimeError('expected one initial case record: '+cid)
            record = json.loads(matches[0].read_text())
            if record['status'] != 'passed': raise RuntimeError('original case did not pass: '+cid)
            original = Path(record['capture']['jit_directories'][0]).resolve()
            if not original.is_relative_to((project/'jit-cache/cache').resolve()):
                raise RuntimeError('unexpected original JIT cache')
            if (original/'kernel.json').exists(): raise RuntimeError('original cache already contains kernel.json')
            digest = sha(original/'kernel.o')
            if digest != record['capture']['binary_sha256']: raise RuntimeError('original binary hash mismatch')
            state['cases'][cid] = {'original': str(original), 'binary_sha256': digest,
                                   'original_op_type': record['capture']['op_type']}
            for arm in ('A', 'B'):
                dest = output/'caches'/arm/'cache'/original.name
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(original, dest)
                for name in ('kernel.o', 'kernel.asc', 'meta.json'):
                    if sha(dest/name) != sha(original/name): raise RuntimeError('cache copy mismatch')
                if arm == 'B': (dest/'kernel.json').write_text(json.dumps({'magic': 'RT_DEV_BINARY_MAGIC_ELF'})+'\n')
        state['status'] = 'running'; report.write_text(json.dumps(state, indent=2)+'\n')
        for cid in CASES:
            for index, arm in enumerate(SEQUENCE, 1):
                run_id = cid+'-'+str(index)+'-'+arm
                path = output/'runs'/run_id
                env = os.environ.copy(); env['DG_JIT_CACHE_DIR'] = str(output/'caches'/arm)
                cmd = [sys.executable, '-B', str(collector), 'batch', '--source', str(project/'source'),
                       '--output', str(path), '--device', '0', '--case', cid]
                log = output/(run_id+'.log')
                with log.open('w') as stream:
                    child = subprocess.Popen(cmd, env=env, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
                    try: rc = child.wait(timeout=900)
                    except subprocess.TimeoutExpired:
                        os.killpg(child.pid, signal.SIGTERM)
                        try: child.wait(timeout=10)
                        except subprocess.TimeoutExpired: os.killpg(child.pid, signal.SIGKILL); child.wait()
                        raise TimeoutError('profile timed out: '+run_id)
                detail = {'id': run_id, 'case': cid, 'arm': arm, 'exit': rc}
                state['runs'].append(detail); report.write_text(json.dumps(state, indent=2)+'\n')
                print(run_id, rc, flush=True)
                if rc: raise RuntimeError('profile failed: '+run_id)
                result = json.loads((path/cid/'result.json').read_text())
                log_text = (path/cid/'profile.log').read_text(errors='replace')
                warning = 'Kernel JSON path not exist' in log_text
                if result['status'] != 'passed' or warning != (arm == 'A'):
                    raise RuntimeError('unexpected status or warning for '+run_id)
                if result['capture']['binary_sha256'] != state['cases'][cid]['binary_sha256']:
                    raise RuntimeError('different binary for '+run_id)
        state['status'] = 'completed'
    except Exception:
        state['status'] = 'failed'; state['error'] = traceback.format_exc()
        raise
    finally: report.write_text(json.dumps(state, indent=2)+'\n')


if __name__ == '__main__': main()
