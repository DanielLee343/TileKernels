"""Reuse the pinned case builder and precision check for one capture mode."""
import argparse,json,os,importlib
from pathlib import Path

def main():
 p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--mode',required=True,choices=('default','detail'));a=p.parse_args()
 root=Path(__file__).resolve().parent
 batch=os.environ.get('COLLECTOR_BATCH','second')
 collector=importlib.import_module('collector' if batch=='second' else 'collector_'+batch)
 manifest='cases.json' if batch=='second' else 'cases_'+batch+'.json'
 cases=json.loads((root/manifest).read_text(encoding='utf-8'))['cases']
 case=next(c for c in cases if c['id']==a.case)
 import torch,torch_npu
 torch.set_num_threads(min(8,os.cpu_count() or 1));torch.npu.set_device(0)
 out=Path(os.environ['CAPTURE_DIR'])/('metadata-'+str(os.getpid()));out.mkdir(parents=True,exist_ok=False)
 kernel,host,device,expected=collector.build(case,torch)
 output=tuple(torch.empty_like(x,device='npu:0') for x in expected)
 symbol=str(kernel.prim_func.attrs['global_symbol']);src=out/'default-kernel.cpp'
 src.write_text(kernel.get_kernel_source())
 record={'case':case,'mode':a.mode,'runtime_kernel':symbol+'_kernel','native_symbol':symbol,
         'source_sha256':collector.digest(src),'inputs':[collector.describe(x,True) for x in host],
         'device_inputs':[collector.describe(x) for x in device],
         'device_input_addresses':[hex(x.data_ptr()) if x is not None else None for x in device],
         'outputs':[collector.describe(x) for x in output],
         'device_output_addresses':[hex(x.data_ptr()) for x in output],
         'application_warmup_native_calls':5,'target_launch_count':1,
         'visible_devices':os.environ.get('ASCEND_RT_VISIBLE_DEVICES'),
         'tensor_bytes_semantics':'logical tensor size; not physical transport'}
 def launch():kernel(*device,*output)
 collector.target_range(torch,launch)
 record['precision']=collector.compare(torch,output,expected,case['family'])
 record['status']='passed' if all(x['passed'] for x in record['precision']) else 'failed'
 (out/'application.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record,indent=2),flush=True)
 assert record['status']=='passed','full-output correctness check failed'
if __name__=='__main__':main()
