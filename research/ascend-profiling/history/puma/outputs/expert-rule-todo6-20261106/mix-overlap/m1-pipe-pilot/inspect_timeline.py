"""Inventory an msopprof PipeTimeline capture without inferring overlap."""
import argparse
import collections
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import struct


CHANNEL = re.compile(r"^core(\d+)\.(cubecore|veccore0|veccore1)$")
TYPES = {0: "cubecore", 1: "veccore0", 2: "veccore1"}
HEADER = struct.Struct("<HHI")
BUFFER_SIZE = 2 * 1024 * 1024
CHUNK_SIZE = HEADER.size + BUFFER_SIZE


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for data in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(data)
    return digest.hexdigest()


def inspect_trace(path):
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or data.get("profilingType") != "op" or data.get("schemaVersion") != 1:
        raise ValueError("unsupported trace schema")
    events = data.get("traceEvents")
    if not isinstance(events, list):
        raise ValueError("traceEvents is not a list")
    counts = collections.Counter()
    pipes = collections.defaultdict(collections.Counter)
    unrecognized = []
    invalid = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            invalid.append(index)
            continue
        if event.get("ph") != "X":
            continue
        pid = event.get("pid")
        match = CHANNEL.fullmatch(pid) if isinstance(pid, str) else None
        if not match:
            unrecognized.append(index)
            continue
        ts, duration = event.get("ts"), event.get("dur")
        values = (ts, duration)
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
               for value in values) or ts < 0 or duration < 0:
            invalid.append(index)
            continue
        counts[pid] += 1
        pipes[pid][str(event.get("tid"))] += 1
    return {
        "sha256": sha256(path),
        "schema_version": data["schemaVersion"],
        "display_time_unit": data.get("displayTimeUnit"),
        "events_total": len(events),
        "events_by_channel": dict(sorted(counts.items())),
        "pipes_by_channel": {key: dict(sorted(value.items())) for key, value in sorted(pipes.items())},
        "unrecognized_complete_event_indices": unrecognized,
        "invalid_event_indices": invalid,
    }


def inspect_raw(path):
    file_bytes = path.stat().st_size
    if file_bytes == 0 or file_bytes % CHUNK_SIZE:
        raise ValueError(f"{path.name}: incomplete raw chunk")
    channels = collections.defaultdict(list)
    with path.open("rb") as source:
        while source.tell() < file_bytes:
            header = source.read(HEADER.size)
            core_id, core_type, valid_len = HEADER.unpack(header)
            if core_type not in TYPES or core_id >= 6 or valid_len > BUFFER_SIZE or valid_len % 4:
                raise ValueError(f"{path.name}: invalid channel header")
            channels[f"core{core_id}.{TYPES[core_type]}"].append(valid_len)
            source.seek(BUFFER_SIZE, 1)
    return {"sha256": sha256(path), "bytes": file_bytes,
            "valid_bytes_by_channel": dict(sorted(channels.items()))}


def inspect_capture(root):
    root = Path(root)
    if not root.is_dir():
        raise ValueError("capture directory does not exist")
    basic_path = root / "OpBasicInfo.csv"
    trace_path = root / "trace.json"
    raw_paths = sorted((root / "dump").glob("timeline.bin.*"))
    missing = [str(path.relative_to(root)) for path in (basic_path, trace_path) if not path.is_file()]
    if not raw_paths:
        missing.append("dump/timeline.bin.*")
    result = {"status": "measurement_only", "missing": missing,
              "target_identity_independently_verified": False,
              "clock_synchronization_verified": False,
              "coverage_complete_verified": False,
              "loss_absent_verified": False,
              "cross_channel_overlap": None}
    if basic_path.is_file():
        with basic_path.open(encoding="utf-8-sig", newline="") as source:
            result["basic"] = {"sha256": sha256(basic_path), "rows": list(csv.DictReader(source))}
    if trace_path.is_file():
        result["trace"] = inspect_trace(trace_path)
    result["raw"] = {path.name: inspect_raw(path) for path in raw_paths}
    raw_channels = {channel for raw in result["raw"].values() for channel in raw["valid_bytes_by_channel"]}
    trace_channels = set(result.get("trace", {}).get("events_by_channel", {}))
    result["raw_channels_without_trace_events"] = sorted(raw_channels - trace_channels)
    result["trace_channels_without_raw_header"] = sorted(trace_channels - raw_channels)
    if missing:
        result["status"] = "incomplete"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path, help="one OPPROF directory")
    args = parser.parse_args()
    try:
        print(json.dumps(inspect_capture(args.capture), indent=2, ensure_ascii=False))
    except (OSError, ValueError, json.JSONDecodeError, struct.error) as error:
        print(json.dumps({"status": "invalid", "error": str(error)}, ensure_ascii=False))
        raise SystemExit(2) from error


if __name__ == "__main__":
    main()
