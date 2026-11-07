"""Rerun both unchanged MoE cases, checking all bytes of their mutable buffer."""
import importlib.util
import json
from pathlib import Path

root=Path('/workspace/tilekernels-finalize-20261107/full-control')
spec=importlib.util.spec_from_file_location('_replay_controller',root/'controller.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
mod.ROOT=root;mod.SHIM=str(root/'restore_watch.so')
plan=json.loads((root/'plan.json').read_text())['cases']
assert {x['capture_id'] for x in plan}=={'moe_topk_gate_forward-04','moe_topk_gate_forward-09'}
results=[]
for item in plan:
    if not mod.idle():raise RuntimeError('NPU busy; stopped before full-buffer control')
    r=mod.run_case(item);results.append(r)
    if r['status']!='sampled_restore_pass':raise RuntimeError(f'control failed: {r}')
    p=root/'cases'/item['capture_id']
    samples=json.loads((p/'watch-metadata.json').read_text())
    rows=[[int(x) for x in line.split()] for line in (p/'watch.log').read_text().splitlines()]
    assert len(samples)==1 and samples[0]['sample_offset']==0 and samples[0]['sample_bytes']==samples[0]['span_bytes']
    assert all(row[8]==0 and row[9]==0 for row in rows),'fixed-routing target changed'
    r['full_buffer_unchanged']=True;r['bytes_checked']=samples[0]['span_bytes']
    (p/'full-control-result.json').write_text(json.dumps(r,indent=2)+'\n')
(root/'full-control-summary.json').write_text(json.dumps({'status':'completed','results':results},indent=2)+'\n')
