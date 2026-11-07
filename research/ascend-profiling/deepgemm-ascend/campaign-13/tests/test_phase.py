import importlib.util
import json
from pathlib import Path
import unittest

root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('campaign_collector',root/'collect.py')
collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)


class SparsePhaseTest(unittest.TestCase):
    def test_metadata_phase_must_match_requested_phase(self):
        collector.validate_sparse_phase((('config',),True),'first')
        collector.validate_sparse_phase((('config',),False),'reuse')
        for state,phase in ((None,'first'),(((),True),'reuse'),(((),False),'first'),(((),True),'unknown')):
            with self.assertRaises(ValueError):collector.validate_sparse_phase(state,phase)

    def test_compiled_target_must_match_requested_phase(self):
        first='&deep_gemm::paged_sparse_mqa_logits_impl<true, false, 8, 8, 8448, 64>'
        reuse=first.replace('<true,','<false,')
        collector.validate_sparse_specialization(first,'first')
        collector.validate_sparse_specialization(reuse,'reuse')
        for source,phase in ((first,'reuse'),(reuse,'first'),('unrelated','first'),(first,'unknown')):
            with self.assertRaises(ValueError):collector.validate_sparse_specialization(source,phase)

    def test_grouped_manifest_has_supported_layouts_and_aligned_lengths(self):
        cases=json.loads((root/'cases-next.json').read_text())['cases']
        grouped=[c for c in cases if c.get('gemm_type') in ('m_grouped','k_grouped')]
        self.assertEqual(len(grouped),12)
        for case in grouped:
            if case['gemm_type']=='m_grouped':
                self.assertEqual(case['a_major'],'K')
                self.assertIn(case['trans'],('nt','nn'))
            else:
                self.assertEqual((case['trans'],case['a_major'],case['b_major']),('tn','MN','MN'))
                self.assertEqual(case['groups'],len(case['ks_cpu']))
                self.assertEqual(case['ks_cpu'],case['host_ks_cpu'])
                self.assertTrue(all(k>0 and k%256==0 for k in case['ks_cpu']))

    def test_profiler_error_overrides_successful_tool_exit(self):
        collector.validate_profiler_log('[INFO] Profiling running finished. All task success.')
        for log in ('[WARN] Child process exited with return value 1',
                    '[WARN] Child process exited with return value -11',
                    '[ERROR] Get profiling data failed.'):
            with self.assertRaises(RuntimeError):collector.validate_profiler_log(log)


if __name__=='__main__':unittest.main()
