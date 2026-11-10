"""Capture the original planned case while recording, not suppressing, reference failure."""
import base64,importlib.util,json,os,sys,traceback
from pathlib import Path
root=Path('/workspace/expert-profile-backfill-20261109-hidev');path=root/'extra-proxy-mhc-post-bwd-app-harness/extra_mhc_post_bwd.py'
spec=importlib.util.spec_from_file_location('precision_post04_adapter',path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
original=mod.verify_outputs;failures=[]
def capture_reference(*args):
 try:return original(*args)
 except AssertionError:
  failures.append(traceback.format_exc());return [{'passed':False,'reference':'original CPU chunk','error':failures[-1]}]
mod.verify_outputs=capture_reference
group,encoded,stage,record=sys.argv[1:];assert group=='mhc_post_bwd' and stage=='default'
params=json.loads(base64.urlsafe_b64decode(encoded.encode()));assert mod.validate_params(params)==4
mod.run(group,params,stage,Path(record))
f=Path(record).with_name('application-'+str(os.getpid())+'.json');state=json.loads(f.read_text());assert state['status']=='passed' and state['matched']==1
state['reference_check']='failed' if failures else 'passed';state['status']='profiled_precision_failed' if failures else 'profiled_precision_passed';state['precision_failure_preserved']=bool(failures)
f.write_text(json.dumps(state,indent=2)+'\n',encoding='utf-8')
