import importlib.util
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

RESEARCH=Path(__file__).resolve().parents[1]
REPO=RESEARCH.parents[1]
spec=importlib.util.spec_from_file_location('portable_profile',RESEARCH/'portable_profile.py')
portable=importlib.util.module_from_spec(spec)
spec.loader.exec_module(portable)


class PortableProfileTests(unittest.TestCase):
    def test_existing_manifests_include_starter_and_unified_cases(self):
        cases=portable.load_cases(REPO)
        self.assertEqual(cases['starter:fused-01']['case']['hidden'],256)
        self.assertEqual(cases['unified-extra4:mhc_pre_apply_mix_bwd-01']['case']['group'],'mhc_pre_apply_mix_bwd')
        self.assertEqual(cases['unified-quant:quant_per_block_cast-01']['adapter'],'quant_hook.py')
        self.assertGreaterEqual(len(cases),1020)

    def test_child_environment_uses_private_checkout_and_explicit_device(self):
        root=Path(tempfile.gettempdir())/'private-repo'
        with patch.dict(os.environ,{'PYTHONPATH':'/some/other/site'},clear=False):
            env=portable.child_environment(root,3)
        self.assertEqual(env['TILEKERNELS_ROOT'],str(root.resolve()))
        self.assertEqual(env['ASCEND_RT_VISIBLE_DEVICES'],'3')
        self.assertEqual(env['PYTHONPATH'].split(os.pathsep)[0],str(root.resolve()))

    def test_source_baseline_allows_research_commit_but_rejects_kernel_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            def git(*args):
                return subprocess.run(['git','-C',str(root),*args],capture_output=True,text=True,check=True).stdout.strip()
            git('init','-q');git('config','user.email','test@example.invalid');git('config','user.name','Test')
            (root/'tile_kernels').mkdir();(root/'tile_kernels'/'a.py').write_text('value = 1\n')
            (root/'tests').mkdir();(root/'tests'/'a.py').write_text('pass\n')
            (root/'pyproject.toml').write_text('[project]\n')
            git('add','.');git('commit','-qm','base');baseline=git('rev-parse','HEAD')
            (root/'research').mkdir();(root/'research'/'data.txt').write_text('data\n')
            git('add','.');git('commit','-qm','research')
            self.assertEqual(portable.verify_source_baseline(root,baseline),git('rev-parse','HEAD'))
            (root/'tile_kernels'/'a.py').write_text('value = 2\n')
            with self.assertRaisesRegex(RuntimeError,'source'):portable.verify_source_baseline(root,baseline)

    def test_unknown_case_fails_without_creating_output(self):
        with self.assertRaisesRegex(KeyError,'unknown'):
            portable.lookup_case(portable.load_cases(REPO),'starter:not-a-case')

    def test_only_recorded_numerical_mismatch_can_be_collected_as_failed_precision(self):
        record={'status':'failed','error':'AssertionError: Tensor-likes are not close!',
                'runtime_kernel':'kernel','inputs':[],'source_sha256':'abc'}
        self.assertTrue(portable.is_recorded_precision_failure(record))
        self.assertFalse(portable.is_recorded_precision_failure({**record,'error':'AssertionError: invalid shape'}))
        self.assertFalse(portable.is_recorded_precision_failure({**record,'runtime_kernel':None}))

    def test_adapters_with_explicit_source_root_follow_private_checkout(self):
        adapters=RESEARCH/'collector/unified'
        names=('extra_channel.py','extra_engram_gate_fwd.py','extra_engram_gate_bwd.py',
               'extra_cast_back.py','extra_cast_and_back.py','extra_lossless.py','extra_multilayer.py',
               'extra_norm_fwd.py','extra_moe_backward.py','extra_moe_forward.py','extra_finalize_retry.py',
               'extra_norm_bwd.py','extra_quant_cast.py','extra_post_fwd_retry.py','extra_engram_step.py',
               'extra_rope.py','extra_swiglu_bwd.py','extra_engram_grad.py','extra_engram_momentum.py',
               'extra_transpose.py','extra_swiglu_fwd.py','quant_hook.py')
        root=Path(tempfile.gettempdir())/'alternate-private-repo'
        with patch.dict(os.environ,{'TILEKERNELS_ROOT':str(root)},clear=False):
            for name in names:
                with self.subTest(adapter=name):
                    module=runpy.run_path(str(adapters/name),run_name='_portable_test_')
                    self.assertEqual(module['ROOT'],root)

    def test_allowed_precision_failure_remains_failed_in_record(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);adapter=root/'adapter.py';out=root/'out';out.mkdir()
            adapter.write_text("import json\nfrom pathlib import Path\ndef run(group,params,stage,record):\n"
                " Path(record).write_text(json.dumps({'status':'failed','error':'AssertionError: Tensor-likes are not close!',"
                "'runtime_kernel':'test','source_sha256':'abc','inputs':[]}))\n"
                " raise AssertionError('Tensor-likes are not close!')\n")
            fake=types.ModuleType('tile_kernels');fake.__file__=str(root/'tile_kernels/__init__.py')
            entry={'kind':'unified','case':{'group':'test','params':{}},'manifest':str(root/'cases.json'),'adapter':adapter.name}
            with patch.dict(sys.modules,{'tile_kernels':fake}),patch.object(portable,'load_cases',return_value={'test':entry}):
                portable.run_stage(root,'test','prepare',out,True)
            record=json.loads((out/'prepare.json').read_text())
            self.assertEqual(record['status'],'failed')
            self.assertIn('Tensor-likes are not close!',record['error'])


if __name__=='__main__':unittest.main()
