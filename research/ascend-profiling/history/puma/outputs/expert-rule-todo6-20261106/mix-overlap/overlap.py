"""Interval arithmetic and conservative inspection of observed msprof task trace."""
import argparse,hashlib,json,math
from decimal import Decimal,InvalidOperation
from pathlib import Path

def _merged(intervals):
 out=[]
 for item in intervals:
  if not isinstance(item,(tuple,list)) or len(item)!=2: raise ValueError('interval must contain two endpoints')
  a,b=item
  if any(isinstance(x,bool) or not isinstance(x,(int,float,Decimal)) or not math.isfinite(x) for x in (a,b)) or a>=b: raise ValueError('invalid interval')
  out.append((a,b))
 merged=[]
 for a,b in sorted(out):
  if merged and a<=merged[-1][1]: merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
  else: merged.append((a,b))
 return merged

def overlap(a,b):
 a,b=_merged(a),_merged(b); i=j=0; intersection=0
 while i<len(a) and j<len(b):
  x,y=a[i]; z,w=b[j]; intersection+=max(0,min(y,w)-max(x,z))
  if y<w: i+=1
  else: j+=1
 ta=sum(y-x for x,y in a); tb=sum(y-x for x,y in b)
 return {'a':ta,'b':tb,'intersection':intersection,'union':ta+tb-intersection}

def inspect_trace(events,task,stream,name):
 missing=['AIC activity intervals','AIV activity intervals','AIC/AIV wait intervals','common clock and synchronization evidence','interval-to-physical-target-call and role mapping','coverage and loss evidence']
 if isinstance(events,dict) and events.get('profilingType')=='op' and events.get('schemaVersion')==1 and isinstance(events.get('traceEvents'),list):
  rows=events['traceEvents']; x=[e for e in rows if isinstance(e,dict) and e.get('ph')=='X']
  return {'status':'reference_insufficient','reason':'op pipe trace has no verified cross-role call, clock, coverage or event semantics','schema':'msopprof-op-v1','displayTimeUnit':events.get('displayTimeUnit'),'event_count':len(rows),'interval_event_count':len(x),'event_names':sorted({str(e.get('name')) for e in x}),'pids':sorted({str(e.get('pid')) for e in x}),'missing':missing}
 if not isinstance(events,list) or type(task) is not int or type(stream) is not int or not isinstance(name,str) or not name: return {'status':'reference_insufficient','reason':'invalid trace or selector','missing':missing}
 matches=[e for e in events if isinstance(e,dict) and e.get('ph')=='X' and e.get('name')==name and isinstance(e.get('args'),dict) and e['args'].get('Task Id')==task and e['args'].get('Physic Stream Id')==stream and e['args'].get('Task Type') in ('MIX_AIC','AI_CORE')]
 if len(matches)!=1: return {'status':'reference_insufficient','reason':'target task absent or ambiguous','matches':len(matches),'missing':missing}
 e=matches[0]
 try:
  ts,dur=Decimal(str(e['ts'])),Decimal(str(e['dur']))
  if not ts.is_finite() or not dur.is_finite() or dur<=0: raise ValueError()
 except (InvalidOperation,KeyError,ValueError): return {'status':'reference_insufficient','reason':'invalid target task interval','missing':missing}
 return {'status':'reference_insufficient','reason':'task-level interval is not pipe or wait activity; no supported synchronized activity schema found','task_event':{'name':name,'task_id':task,'stream_id':stream,'task_type':e['args']['Task Type'],'ts':str(ts),'dur':str(dur)},'missing':missing}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('trace',type=Path); ap.add_argument('--task',required=True,type=int); ap.add_argument('--stream',required=True,type=int); ap.add_argument('--name',required=True); args=ap.parse_args()
 try:
  raw=args.trace.read_bytes(); data=json.loads(raw.decode('utf-8-sig')); result=inspect_trace(data,args.task,args.stream,args.name); result['trace_sha256']=hashlib.sha256(raw).hexdigest(); print(json.dumps(result,indent=2,ensure_ascii=False))
 except (OSError,ValueError,UnicodeError) as e: print(json.dumps({'status':'reference_insufficient','reason':str(e)})); raise SystemExit(2)
if __name__=='__main__': main()
