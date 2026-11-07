import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('pilot', ROOT / 'collect.py')
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)


class VerdictTests(unittest.TestCase):
    def setUp(self):
        self.stage = {'status': 'passed', 'case_id': 'c1', 'input_a_sha256': 'a',
                      'input_b_sha256': 'b', 'reference_sha256': 'ref',
                      'output_sha256': 'out', 'diff': 1e-7, 'threshold': 1e-5,
                      'output_finite': True, 'reference_finite': True}

    def test_precision_or_nonfinite_is_not_admitted(self):
        pilot.validate_stage(self.stage, 'c1')
        for edit in ({'diff': 1e-5}, {'output_finite': False},
                     {'diff': float('nan')}, {'status': 'failed'}):
            with self.subTest(edit=edit), self.assertRaises(ValueError):
                pilot.validate_stage({**self.stage, **edit}, 'c1')

    def test_replay_must_match_input_reference_and_output(self):
        pilot.validate_stages(self.stage, self.stage, 'c1')
        for key in ('input_a_sha256', 'input_b_sha256', 'reference_sha256', 'output_sha256'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                pilot.validate_stages(self.stage, {**self.stage, key: 'different'}, 'c1')

    def test_capture_requires_cube_target_and_matching_device_binary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); capture = root / 'profile' / 'OPPROF_1'; capture.mkdir(parents=True)
            jit = root / 'jit' / 'gemm'; jit.mkdir(parents=True)
            (jit / 'kernel.o').write_bytes(b'expected binary')
            (jit / 'kernel.asc').write_text('expected source')
            (jit / 'meta.json').write_text('{}')
            dump = capture / 'dump'; dump.mkdir()
            (dump / 'aicore_binary.o').write_bytes(b'expected binary')
            (dump / 'DeviceProf1.bin').write_bytes(b'raw')
            def table(name, rows):
                with (capture / name).open('w', newline='') as f:
                    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
            basic = {'Op Name': '_Zbf16_gemm_impl', 'Op Type': 'cube', 'Block Dim': '1'}
            table('OpBasicInfo.csv', [basic])
            for metric in pilot.METRICS:
                table(metric + '.csv', [{'block_id': '0', 'sub_block_id': 'cube0',
                                        'aic_cube_time(us)': '0.3'}])
            result = pilot.inspect_capture(root / 'profile', root / 'jit')
            self.assertEqual(result['op_type'], 'cube')
            self.assertEqual(result['cube_active_rows'], 1)
            table('OpBasicInfo.csv', [{**basic, 'Op Type': 'vector'}])
            with self.assertRaises(ValueError): pilot.inspect_capture(root / 'profile', root / 'jit')
            table('OpBasicInfo.csv', [basic])
            (dump / 'aicore_binary.o').write_bytes(b'wrong binary')
            with self.assertRaises(ValueError): pilot.inspect_capture(root / 'profile', root / 'jit')

    def test_cases_have_bounded_known_contract(self):
        cases = json.loads((ROOT / 'cases.json').read_text())['cases']
        self.assertEqual(len(cases), 6)
        for case in cases: pilot.validate_case(case)
        with self.assertRaises(ValueError): pilot.validate_case({**cases[0], 'accumulate': True})

    def test_case_selection_rejects_unknown_and_duplicates(self):
        cases = [{'id': 'a'}, {'id': 'b'}]
        self.assertEqual(pilot.select_cases(cases, ['b']), [cases[1]])
        with self.assertRaises(ValueError): pilot.select_cases(cases, ['missing'])
        with self.assertRaises(ValueError): pilot.select_cases(cases, ['a', 'a'])


if __name__ == '__main__': unittest.main()
