"""Offline admission checks for the C1 role and Default field pilot."""

import argparse
import csv
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path


ROLES = ("cann", "triton")
COMPUTE_PREFIX = ("AI_", "AIC", "AIV", "MIX", "HCCL", "DSA", "SDMA")
EXPECTED_SOURCES = {
    "run.py": "cea1822476618578a11004d30909d3ff57c7417829da3ecea0449d51d7c4f838",
    "fixture.py": "f3bbead8a517852e5573b639f8252dec14a1da91c824c97ffae1ab303251afd7",
    "matmul_demo.py": "340d51f935e3ad47d2f13c3f374a47c201c9d6afd3fb845d61fdb21b2d8661fc",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def table(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def one_file(directory, pattern):
    files = list(directory.rglob(pattern))
    if len(files) != 1:
        raise ValueError(f"expected one {pattern}: {directory} has {len(files)}")
    return files[0]


def check_records(exact, stage, role, stage_name, expected_hashes, nd):
    if exact["status"] != "exact_pass_role_and_runtime_unverified" or not exact["exact"]:
        raise ValueError("independent full output failed")
    if stage["status"] != "exact_pass_identity_unverified" or not stage["exact"]:
        raise ValueError("profiled full output failed")
    if exact["role"] != role or stage["role"] != role or stage["stage"] != stage_name:
        raise ValueError("role or stage mismatch")
    if exact["fixture_sha256"] != expected_hashes or stage["fixture_sha256"] != expected_hashes:
        raise ValueError("fixture mismatch")
    if exact["output_sha256"] != expected_hashes[2] or stage["output_sha256"] != expected_hashes[2]:
        raise ValueError("output mismatch")
    if exact["output_shape"] != [256, 256] or exact["output_dtype"] != "torch.float16":
        raise ValueError("independent output metadata mismatch")
    if exact["output_stride"] != [256, 1] or exact["output_format"] != nd:
        raise ValueError("independent output layout mismatch")
    if len(exact["inputs"]) != 2 or any(x["stride"] != [256, 1] or x["format"] != nd for x in exact["inputs"]):
        raise ValueError("independent input layout mismatch")
    for tensor in stage["tensors"]:
        if tensor != {"shape": [256, 256], "stride": [256, 1], "dtype": "torch.float16", "format": nd}:
            raise ValueError("profiled tensor metadata mismatch")
    if len(stage["tensors"]) != 3:
        raise ValueError("profiled tensor count mismatch")


def check_trace(rows):
    tasks = [row for row in rows if row["Task Type"].upper().startswith(COMPUTE_PREFIX)]
    if len(tasks) != 1 or tasks[0]["Task Type"].upper() != "AI_CORE":
        raise ValueError("expected one AI_CORE computational task")
    task = tasks[0]
    if int(task["Block Num"]) <= 0 or int(task.get("Mix Block Num") or 0) != 0:
        raise ValueError("invalid trace task dimensions")
    return {key: task[key] for key in ("Op Name", "Task Type", "Task ID", "Stream ID", "Block Num", "Mix Block Num")}


def check_basic(rows, task, physical_card, expected_kernel=None):
    if len(rows) != 1:
        raise ValueError("expected one BasicInfo row")
    info = rows[0]
    if info["Op Type"] != "cube" or info["Device Id"] != str(physical_card):
        raise ValueError("pure Cube identity or physical card mismatch")
    if int(info["Block Dim"]) != int(task["Block Num"]):
        raise ValueError("trace and BasicInfo dimensions disagree")
    if info["Mix Block Dim"] not in ("NA", "", "0"):
        raise ValueError("unexpected mixed role")
    if expected_kernel is not None and info["Op Name"] != expected_kernel:
        raise ValueError("Default target identity differs from BasicInfo")
    return info


def check_pipe(rows, block_dim):
    if len(rows) != int(block_dim):
        raise ValueError("PipeUtilization row count mismatch")
    keys = set()
    activity = Decimal(0)
    for row in rows:
        key = (row["block_id"], row["sub_block_id"])
        if key in keys or key[1] != "cube0":
            raise ValueError("duplicate or non-Cube pipe row")
        keys.add(key)
        value = Decimal(row["aic_cube_time(us)"])
        duration = Decimal(row["aic_time(us)"])
        if not value.is_finite() or not duration.is_finite() or value < 0 or duration <= 0 or value > duration:
            raise ValueError("invalid pipe activity")
        activity += value
    if activity <= 0:
        raise ValueError("Cube activity absent")
    return str(activity)


def check_maps(path, cann_root):
    root = os.path.realpath(cann_root) + os.sep
    libraries = {}
    for line in path.read_text().splitlines():
        parts = line.split(None, 5)
        if len(parts) < 6:
            continue
        name = parts[5]
        for library in ("libascendcl.so", "libruntime.so"):
            if library in Path(name).name:
                if name.endswith(" (deleted)") or not os.path.realpath(name).startswith(root):
                    raise ValueError(f"unexpected runtime mapping: {name}")
                libraries[os.path.realpath(name)] = sha(Path(name))
    if not all(any(name in Path(path).name for path in libraries) for name in ("libascendcl.so", "libruntime.so")):
        raise ValueError("required runtime mappings missing")
    return libraries


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["roles", "defaults"])
    parser.add_argument("--root", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--nd-format", required=True, type=int)
    parser.add_argument("--physical-card", required=True)
    parser.add_argument("--cann-root", required=True)
    args = parser.parse_args()
    root = Path(args.root)
    expected = [sha(Path(args.fixture, name)) for name in ("a.bin", "b.bin", "gold.bin")]
    findings = []
    for role in ROLES:
        home = root / role
        exact = json.loads((home / "exact/result.json").read_text())
        if sha(home / "exact/output.bin") != expected[2]:
            raise ValueError("independent output bytes mismatch")
        if os.path.realpath(exact["ascend_home"]) != os.path.realpath(args.cann_root):
            raise ValueError("wrong independent CANN home")
        exact_mappings = check_maps(home / "exact/proc-maps.txt", args.cann_root)
        stages = ("trace", "basic") if args.phase == "roles" else ("trace", "basic", "default")
        loaded = {}
        for stage in stages:
            folder = home / f"{stage}-app"
            record = json.loads((folder / "result.json").read_text())
            check_records(exact, record, role, stage, expected, args.nd_format)
            if sha(folder / "output.bin") != expected[2]:
                raise ValueError("profiled output bytes mismatch")
            if os.path.realpath(record["ascend_home"]) != os.path.realpath(args.cann_root):
                raise ValueError("wrong CANN home")
            if os.path.realpath(record["executable"]) != os.path.realpath(exact["executable"]):
                raise ValueError("Python environment changed across stages")
            if record["packages"] != exact["packages"]:
                raise ValueError("package version changed across stages")
            if record["source_sha256"] != EXPECTED_SOURCES:
                raise ValueError("frozen implementation source changed")
            record["runtime_mapping_sha256"] = check_maps(folder / "proc-maps.txt", args.cann_root)
            if record["runtime_mapping_sha256"] != exact_mappings:
                raise ValueError("runtime mappings changed across stages")
            loaded[stage] = record
        if len({json.dumps(v["source_sha256"], sort_keys=True) for v in loaded.values()}) != 1:
            raise ValueError("implementation source changed across stages")
        summary = one_file(home / "trace", "op_summary_*.csv")
        task = check_trace(table(summary))
        basic_path = one_file(home / "basic", "OpBasicInfo.csv")
        info = check_basic(table(basic_path), task, args.physical_card)
        item = {"role": role, "trace_task": task, "basic_kernel": info["Op Name"],
                "trace_summary_sha256": sha(summary), "basic_info_sha256": sha(basic_path),
                "runtime_mappings": {stage: loaded[stage]["runtime_mapping_sha256"] for stage in stages}}
        if args.phase == "defaults":
            default_info_path = one_file(home / "default", "OpBasicInfo.csv")
            default_info = check_basic(table(default_info_path), task, args.physical_card, info["Op Name"])
            pipe_path = one_file(home / "default", "PipeUtilization.csv")
            item.update(default_info_sha256=sha(default_info_path), pipe_sha256=sha(pipe_path),
                        cube_activity_us=check_pipe(table(pipe_path), default_info["Block Dim"]))
        findings.append(item)
    if findings[0]["runtime_mappings"]["trace"] != findings[1]["runtime_mappings"]["trace"]:
        raise ValueError("CANN runtime mappings differ between arms")
    print(json.dumps({"status": "role_pilot_only", "phase": args.phase, "nd_format_value": args.nd_format,
                      "fixture_sha256": expected, "arms": findings}, indent=2))


if __name__ == "__main__":
    main()
