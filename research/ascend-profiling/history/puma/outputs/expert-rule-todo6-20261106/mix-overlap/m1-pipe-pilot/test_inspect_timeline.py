import json
from pathlib import Path
import struct
import tempfile
import unittest

import inspect_timeline as pilot


class InspectTimelineTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "dump").mkdir()
        (self.root / "OpBasicInfo.csv").write_text("Op Name,Op Type\ntarget,mix\n", encoding="utf-8")

    def trace(self, events):
        data = {"profilingType": "op", "schemaVersion": 1, "displayTimeUnit": "ns", "traceEvents": events}
        (self.root / "trace.json").write_text(json.dumps(data), encoding="utf-8")

    def raw(self, records):
        with (self.root / "dump" / "timeline.bin.0").open("wb") as target:
            for core, kind, length in records:
                target.write(struct.pack("<HHI", core, kind, length))
                target.write(bytes(pilot.BUFFER_SIZE))

    def test_present_both_roles_does_not_claim_cross_channel_overlap(self):
        self.trace([{"ph": "X", "pid": "core0.cubecore", "tid": "CUBE", "ts": 1, "dur": 2},
                    {"ph": "X", "pid": "core0.veccore0", "tid": "VECTOR", "ts": 1, "dur": 2}])
        self.raw([(0, 0, 16), (0, 1, 8)])
        result = pilot.inspect_capture(self.root)
        self.assertEqual(result["status"], "measurement_only")
        self.assertEqual(set(result["trace"]["events_by_channel"]), {"core0.cubecore", "core0.veccore0"})
        self.assertFalse(result["clock_synchronization_verified"])
        self.assertFalse(result["coverage_complete_verified"])
        self.assertIsNone(result["cross_channel_overlap"])

    def test_missing_raw_is_incomplete(self):
        self.trace([])
        result = pilot.inspect_capture(self.root)
        self.assertEqual(result["status"], "incomplete")
        self.assertIn("dump/timeline.bin.*", result["missing"])

    def test_truncated_or_invalid_raw_rejected(self):
        raw = self.root / "dump" / "timeline.bin.0"
        raw.write_bytes(b"short")
        with self.assertRaises(ValueError):
            pilot.inspect_raw(raw)
        self.raw([(6, 0, 4)])
        with self.assertRaises(ValueError):
            pilot.inspect_raw(raw)

    def test_unrecognized_and_invalid_events_are_preserved_as_indices(self):
        self.trace([{"ph": "X", "pid": "unknown", "tid": "CUBE", "ts": 1, "dur": 2},
                    {"ph": "X", "pid": "core0.cubecore", "tid": "CUBE", "ts": -1, "dur": 2}])
        self.raw([(0, 0, 4)])
        result = pilot.inspect_capture(self.root)
        self.assertEqual(result["trace"]["unrecognized_complete_event_indices"], [0])
        self.assertEqual(result["trace"]["invalid_event_indices"], [1])
        self.assertEqual(result["raw_channels_without_trace_events"], ["core0.cubecore"])

    def test_repeated_raw_chunk_keeps_both_lengths(self):
        self.raw([(1, 0, 4), (1, 0, 8)])
        result = pilot.inspect_raw(self.root / "dump" / "timeline.bin.0")
        self.assertEqual(result["valid_bytes_by_channel"]["core1.cubecore"], [4, 8])


if __name__ == "__main__":
    unittest.main()
