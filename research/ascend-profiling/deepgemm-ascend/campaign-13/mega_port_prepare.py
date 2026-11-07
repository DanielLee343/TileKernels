"""Build a separately labeled experimental 28-Cube MegaMoE package on hidev.

Run only when no profile is collecting: the host compiler can disturb timing.
This never modifies the original checkout, package, or its JIT cache.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import traceback


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    root=Path('/workspace/deepgemm-ascend-20261107')
    source=root/'source';port=root/'mega-port28-experiment';copy=port/'source';package=port/'packages'
    if port.exists():raise RuntimeError('experiment already exists: '+str(port))
    commit=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    dirty=subprocess.check_output(['git','-C',str(source),'status','--porcelain'],text=True)
    if commit!='3a35326271b069b8b5bf1a754435acd6cc91575b' or dirty:
        raise RuntimeError('original checkout mismatch')
    port.mkdir();record={'source_commit':commit,'status':'building','experimental':True}
    record_path=port/'build-result.json'
    try:
        shutil.copytree(source,copy,symlinks=True,ignore=shutil.ignore_patterns('.git','build','*.egg-info','__pycache__'))
        orig=source/'deep_gemm/include/deep_gemm/common.hpp';header=copy/'deep_gemm/include/deep_gemm/common.hpp'
        text=header.read_text();old='inline constexpr uint32_t kNumAICores = 32;'
        if text.count(old)!=1:raise RuntimeError('unexpected original kNumAICores definition')
        header.write_text(text.replace(old,'inline constexpr uint32_t kNumAICores = 28;'))
        record.update({'original_header_sha256':digest(orig),'patched_header_sha256':digest(header),
                       'change':'kNumAICores 32 -> 28 in isolated source copy'})
        env=os.environ.copy();env['DG_USE_LOCAL_VERSION']='0';env['MAX_JOBS']='2';env['PIP_DISABLE_PIP_VERSION_CHECK']='1'
        cmd=[sys.executable,'-m','pip','install','--no-build-isolation','--no-deps','--no-cache-dir','--target',str(package),str(copy)]
        record['command']=cmd;record_path.write_text(json.dumps(record,indent=2)+'\n')
        with (port/'build.log').open('w') as log:
            result=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1200)
        if result.returncode:raise RuntimeError('build failed: '+str(result.returncode))
        installed=package/'deep_gemm/include/deep_gemm/common.hpp'
        if digest(installed)!=digest(header):raise RuntimeError('installed header differs from patched source')
        if digest(orig)!=record['original_header_sha256']:raise RuntimeError('original header changed')
        binaries=list((package/'deep_gemm').glob('_C*.so'))
        if len(binaries)!=1:raise RuntimeError('expected one compiled extension')
        record['extension_sha256']=digest(binaries[0]);record['status']='built'
    except Exception:
        record['status']='failed';record['error']=traceback.format_exc()
    record_path.write_text(json.dumps(record,indent=2)+'\n')
    print(record['status'],flush=True)
    if record['status']!='built':raise SystemExit(1)


if __name__=='__main__':main()
