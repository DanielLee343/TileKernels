import copy
import unittest

from analyze import calculate


class ActivityTests(unittest.TestCase):
    def setUp(self):
        self.case = {"id": "small", "op": "mm", "shape": [2, 3, 4], "dtype": "float16"}
        self.basic = [{"Op Type": "cube", "Block Dim": "2", "Device Id": "6",
                       "Current Freq": "1650", "Task Duration(us)": "1"}]
        self.pipe = [
            {"block_id": "0", "sub_block_id": "cube0", "aic_cube_time(us)": "0.1", "aic_time(us)": "1"},
            {"block_id": "1", "sub_block_id": "cube0", "aic_cube_time(us)": "0.2", "aic_time(us)": "1"},
        ]

    def test_calculation_is_case_level_and_row_order_independent(self):
        result = calculate(self.case, self.basic, self.pipe)
        self.assertEqual(result["sum_cube_activity_us"], "0.3")
        self.assertEqual(result["nominal_macs"], 24)
        self.assertEqual(result["cube_activity_us_per_gmac"], "12500000.0")
        self.assertEqual(result, calculate(self.case, self.basic, list(reversed(self.pipe))))

    def test_batch_work_is_included(self):
        self.case.update(op="bmm", shape=[5, 2, 3, 4])
        self.assertEqual(calculate(self.case, self.basic, self.pipe)["nominal_macs"], 120)

    def test_missing_or_duplicated_rows_are_rejected(self):
        for rows in (self.pipe[:1], [self.pipe[0], self.pipe[0]]):
            with self.assertRaises(ValueError):
                calculate(self.case, self.basic, rows)

    def test_na_and_activity_exceeding_row_time_are_rejected(self):
        for value in ("NA", "NaN", "-0.1", "1.1"):
            rows = copy.deepcopy(self.pipe)
            rows[0]["aic_cube_time(us)"] = value
            with self.assertRaises((ValueError, ArithmeticError)):
                calculate(self.case, self.basic, rows)

    def test_unknown_contract_is_rejected(self):
        self.case["dtype"] = "int8"
        with self.assertRaises(ValueError):
            calculate(self.case, self.basic, self.pipe)


if __name__ == "__main__":
    unittest.main()
