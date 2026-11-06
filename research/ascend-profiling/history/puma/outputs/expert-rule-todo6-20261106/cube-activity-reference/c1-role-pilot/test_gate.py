import copy
import unittest

from gate import check_basic, check_pipe, check_records, check_trace


class GateTests(unittest.TestCase):
    def setUp(self):
        self.hashes = ["a", "b", "gold"]
        self.exact = {"status": "exact_pass_role_and_runtime_unverified", "exact": True,
                      "role": "cann", "fixture_sha256": self.hashes, "output_sha256": "gold",
                      "output_shape": [256, 256], "output_dtype": "torch.float16",
                      "output_stride": [256, 1], "output_format": 2,
                      "inputs": [{"stride": [256, 1], "format": 2} for _ in range(2)]}
        tensor = {"shape": [256, 256], "stride": [256, 1], "dtype": "torch.float16", "format": 2}
        self.stage = {"status": "exact_pass_identity_unverified", "exact": True, "role": "cann",
                      "stage": "trace", "fixture_sha256": self.hashes, "output_sha256": "gold",
                      "tensors": [copy.deepcopy(tensor) for _ in range(3)]}
        self.task = {"Op Name": "trace-name", "Task Type": "AI_CORE", "Task ID": "1", "Stream ID": "2",
                     "Block Num": "2", "Mix Block Num": "0"}
        self.basic = {"Op Name": "kernel-name", "Op Type": "cube", "Device Id": "6",
                      "Block Dim": "2", "Mix Block Dim": "NA"}
        self.pipe = [
            {"block_id": "0", "sub_block_id": "cube0", "aic_cube_time(us)": "0.1", "aic_time(us)": "1"},
            {"block_id": "1", "sub_block_id": "cube0", "aic_cube_time(us)": "0.2", "aic_time(us)": "1"},
        ]

    def test_contract_accepts_expected_output(self):
        check_records(self.exact, self.stage, "cann", "trace", self.hashes, 2)

    def test_wrong_data_and_non_nd_are_rejected(self):
        for field, value in (("output_sha256", "wrong"), ("exact", False)):
            changed = copy.deepcopy(self.stage)
            changed[field] = value
            with self.assertRaises(ValueError):
                check_records(self.exact, changed, "cann", "trace", self.hashes, 2)
        changed = copy.deepcopy(self.stage)
        changed["tensors"][0]["format"] = 9
        with self.assertRaises(ValueError):
            check_records(self.exact, changed, "cann", "trace", self.hashes, 2)

    def test_trace_rejects_additional_task_and_mixed_work(self):
        self.assertEqual(check_trace([self.task]), self.task)
        for rows in ([self.task, self.task], [{**self.task, "Mix Block Num": "1"}],
                     [{**self.task, "Task Type": "AIV"}]):
            with self.assertRaises(ValueError):
                check_trace(rows)

    def test_basic_type_device_dimensions_and_kernel(self):
        self.assertEqual(check_basic([self.basic], self.task, 6)["Op Name"], "kernel-name")
        for changed in ({**self.basic, "Op Type": "vector"}, {**self.basic, "Device Id": "5"},
                        {**self.basic, "Block Dim": "3"}, {**self.basic, "Mix Block Dim": "1"}):
            with self.assertRaises(ValueError):
                check_basic([changed], self.task, 6)
        with self.assertRaises(ValueError):
            check_basic([self.basic], self.task, 6, "another-kernel")

    def test_pipe_rows_and_activity(self):
        self.assertEqual(check_pipe(self.pipe, 2), "0.3")
        for changed in (self.pipe[:1], [self.pipe[0], self.pipe[0]],
                        [{**self.pipe[0], "aic_cube_time(us)": "NaN"}, self.pipe[1]],
                        [{**self.pipe[0], "aic_cube_time(us)": "2"}, self.pipe[1]]):
            with self.assertRaises((ValueError, ArithmeticError)):
                check_pipe(changed, 2)


if __name__ == "__main__":
    unittest.main()
