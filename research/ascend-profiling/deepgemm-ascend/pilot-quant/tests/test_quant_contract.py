import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('quant_collector', ROOT/'collect.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


class QuantContractTests(unittest.TestCase):
    def test_symbol_extraction_requires_one_expected_target(self):
        good = '  [ 5] .ascend.meta._ZN9deep_gemm14fp8_gemm_impl_test NOTE 0000\n'
        self.assertEqual(module.parse_kernel_symbol(good, 'fp8_gemm_impl'), '_ZN9deep_gemm14fp8_gemm_impl_test')
        with self.assertRaises(ValueError): module.parse_kernel_symbol(good, 'fp8_dequant_gemm_impl')
        with self.assertRaises(ValueError): module.parse_kernel_symbol(good + good.replace('_test', '_other'), 'fp8_gemm_impl')

    def test_case_dispatch_must_match_dtype_combination(self):
        cases = json.loads((ROOT/'cases.json').read_text())['cases']
        self.assertEqual(len({case['id'] for case in cases}), len(cases))
        for pair in (('fp8','fp8'),('fp4','fp4'),('fp8','fp4')):
            self.assertEqual(len([case for case in cases if (case['a_dtype'],case['b_dtype']) == pair]), 4)
        for case in cases: module.validate_case(case)
        with self.assertRaises(ValueError): module.validate_case({**cases[0], 'jit_prefix':'fp4_gemm'})
        with self.assertRaises(ValueError): module.validate_case({**cases[0], 'a_dtype':'fp4','b_dtype':'fp8'})

    def test_stage_identity_detects_different_target(self):
        item = {'status':'passed','case_id':'c','input_a_sha256':'a','input_b_sha256':'b',
                'reference_sha256':'r','output_sha256':'d','target_sha256':'x',
                'target_symbol':'fp8_gemm_impl','diff':0.0,'threshold':1e-5,
                'output_finite':True,'reference_finite':True}
        module.validate_stages(item,item,'c')
        with self.assertRaises(ValueError): module.validate_stages(item,{**item,'target_sha256':'y'},'c')
        with self.assertRaises(ValueError): module.validate_stages(item,{**item,'diff':1e-4},'c')


if __name__ == '__main__': unittest.main()
