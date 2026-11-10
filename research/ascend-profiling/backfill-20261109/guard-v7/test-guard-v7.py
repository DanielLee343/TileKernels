"""Guard must reject or retry malformed NPU listings without relaxing the 3s limit."""
import importlib.util,io,subprocess
from pathlib import Path
p=Path(__file__).with_name('guard-v7.py');spec=importlib.util.spec_from_file_location('guardv7',p);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
class Clock:
 def __init__(self):self.value=0.0
 def now(self):return self.value
 def sleep(self,x):self.value+=x
 def run(self,outputs):
  it=iter(outputs)
  def fn(*a,**k):
   self.value+=0.1;v=next(it)
   if isinstance(v,Exception):raise v
   if isinstance(v,tuple):return subprocess.CompletedProcess(a[0],0,*v)
   return subprocess.CompletedProcess(a[0],0,v,'')
  return fn
bad='\tNPU ID : 0\nFailed to query npu chip: 0 info.\nThis device does not support querying proc-mem.\n'
good='\tNPU ID : 0\n\tProcess id:123 Process name:python Process memory(MB):10\n'
empty='\tNPU ID : 0\n\tNo process in device.\n'
def state():return {'last_success':0.,'max_gap':0.,'queries':0,'query_failures':0,'timeouts':0}
c=Clock();s=state();assert g.processes(0,io.StringIO(),s,run=c.run([bad,good]),monotonic=c.now,sleep=c.sleep)=={123};assert s['queries']==2 and s['query_failures']==1 and s['max_gap']>=0.2
for invalid in (bad,'', 'NPU ID : 1\nNo process in device.', 'NPU ID : 0\nProcess id:garbled\n',good+'No process in device.\n',(good,'Failed to query npu chip')):
 c=Clock();s=state()
 try:g.processes(0,io.StringIO(),s,run=c.run([invalid]*3),monotonic=c.now,sleep=c.sleep)
 except RuntimeError:pass
 else:raise AssertionError('invalid listing accepted: '+repr(invalid))
 assert s['last_success']==0 and s['query_failures']==3
c=Clock();s=state();assert g.processes(0,io.StringIO(),s,run=c.run([empty]),monotonic=c.now,sleep=c.sleep)==set()
c=Clock();s=state();s['last_success']=-2.94
try:g.processes(0,io.StringIO(),s,run=c.run([bad,good]),monotonic=c.now,sleep=c.sleep)
except RuntimeError:pass
else:raise AssertionError('three-second limit was relaxed')
c=Clock();s=state();timeout=subprocess.TimeoutExpired(['npu-smi'],0.65)
assert g.processes(0,io.StringIO(),s,run=c.run([timeout,empty]),monotonic=c.now,sleep=c.sleep)==set();assert s['timeouts']==1 and s['query_failures']==1
c=Clock();s=state()
try:g.processes(0,io.StringIO(),s,run=c.run([timeout,timeout,timeout]),monotonic=c.now,sleep=c.sleep)
except RuntimeError:pass
else:raise AssertionError('three timeouts accepted')
assert s['timeouts']==3 and s['last_success']==0
assert g.unexpected_processes({101,999},{100},{100,101},exists=lambda p:False)==({999},{101})
print('PASS malformed-query retry, fail-closed, PID handling and 3-second limit')
