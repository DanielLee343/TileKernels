"""Reproduce a descriptive Cube activity cost from the three opened C1/C2 cases."""

import csv
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[3]
ARCHIVE = ROOT / "outputs/expert-rule-todo5-20261106/cube-mix-site-20261106/c1c2-c3-evidence.tar.gz"
EXPECTED_ARCHIVE = "7d997ab5d2dfe9ddefcbbf376babf26c113b49ffec44c6aa2b7a57a1abfef016"
PREFIX = "expert-rule-cube-mix-site-20261106/pack-sitefix-v2/c1-c2/"
CASES = ("mm-fp16-square", "mm-fp16-tail", "bmm-fp16-regular")


def parse_csv(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))


def calculate(case, basic, pipe):
    if case["dtype"] != "float16" or case["op"] not in ("mm", "bmm"):
        raise ValueError("unsupported task")
    shape = case["shape"]
    if len(shape) != (3 if case["op"] == "mm" else 4):
        raise ValueError("unsupported dimensions")
    if any(not isinstance(value, int) or value <= 0 for value in shape):
        raise ValueError("invalid dimensions")
    if len(basic) != 1 or basic[0]["Op Type"] != "cube":
        raise ValueError("expected one Cube target")
    record = basic[0]
    blocks = int(record["Block Dim"])
    if blocks != len(pipe):
        raise ValueError("missing or extra Cube rows")
    if record["Device Id"] != "6" or record["Current Freq"] != "1650":
        raise ValueError("unexpected device or frequency")
    observed_keys = set()
    activity = Decimal(0)
    active_count = 0
    for row in pipe:
        key = (row["block_id"], row["sub_block_id"])
        if key in observed_keys or key[1] != "cube0":
            raise ValueError("duplicate or non-Cube row")
        observed_keys.add(key)
        value = Decimal(row["aic_cube_time(us)"])
        row_time = Decimal(row["aic_time(us)"])
        if not value.is_finite() or not row_time.is_finite() or value < 0 or row_time <= 0 or value > row_time:
            raise ValueError("invalid activity")
        activity += value
        active_count += value > 0
    if activity <= 0:
        raise ValueError("no Cube activity")
    b = 1 if case["op"] == "mm" else shape[0]
    m, k, n = shape[-3:]
    macs = b * m * k * n
    nominal_flops = 2 * macs
    return {
        "case": case["id"], "dtype": case["dtype"], "op": case["op"],
        "shape": shape, "rows": len(pipe), "active_rows": active_count,
        "block_dim": blocks, "device_id": record["Device Id"],
        "frequency_mhz": record["Current Freq"],
        "task_duration_us": record["Task Duration(us)"],
        "sum_cube_activity_us": str(activity), "nominal_macs": macs,
        "nominal_flops_2_per_mac": nominal_flops,
        "cube_activity_us_per_gmac": str(activity * Decimal(10**9) / macs),
        "nominal_tflop_per_cube_active_second": str(Decimal(nominal_flops) / activity / Decimal(10**6)),
        "status": "development_descriptive_only",
    }


def main():
    archive_hash = hashlib.file_digest(ARCHIVE.open("rb"), "sha256").hexdigest()
    if archive_hash != EXPECTED_ARCHIVE:
        raise ValueError("archive hash mismatch")
    with tarfile.open(ARCHIVE, "r:gz") as archive:
        def member_bytes(name):
            data = archive.extractfile(name)
            if data is None:
                raise ValueError("missing archive member")
            return data.read()

        cases_bytes = member_bytes(PREFIX + "cases.json")
        cases = {item["id"]: item for item in json.loads(cases_bytes)["cases"] if item["id"] in CASES}
        results = []
        inputs = {}
        for name in CASES:
            inputs[name] = {}
            tables = []
            for filename in ("OpBasicInfo.csv", "PipeUtilization.csv"):
                prefix = PREFIX + "cases/" + name + "/capture/"
                matches = [item for item in archive.getnames() if item.startswith(prefix) and item.endswith("/" + filename)]
                if len(matches) != 1:
                    raise ValueError(f"expected one {name} {filename}")
                data = member_bytes(matches[0])
                inputs[name][filename] = {"member": matches[0], "sha256": hashlib.sha256(data).hexdigest()}
                tables.append(parse_csv(data))
            results.append(calculate(cases[name], *tables))
    print(json.dumps({"archive_sha256": archive_hash,
                      "cases_json_sha256": hashlib.sha256(cases_bytes).hexdigest(),
                      "inputs": inputs, "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
