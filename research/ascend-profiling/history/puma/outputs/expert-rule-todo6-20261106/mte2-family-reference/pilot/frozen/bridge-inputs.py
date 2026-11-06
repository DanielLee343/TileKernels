"""Concrete full-size inputs. NumPy only; BF16 is stored as raw uint16 bits."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
TASKS = ("swiglu", "rmsnorm", "rope", "sinkhorn", "mhc_post_bwd")
MANIFEST_SHA256 = "99286b53b120258d0b630ba5f7274cb0d9622075b8aaf204da43defdc8d54d48"
SEED = 20261101


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_manifest(cases):
    if len(cases) != 100 or len({c["id"] for c in cases}) != 100:
        raise ValueError("Expected exactly 100 distinct frozen case IDs")
    if Counter(c["task"] for c in cases) != Counter({t: 20 for t in TASKS}):
        raise ValueError("Expected 20 cases for each of the five tasks")
    for c in cases:
        if len(c["input_shapes"]) != len(c["input_dtypes"]):
            raise ValueError(c["id"] + ": shape/dtype count differs")
        nbytes = sum(math.prod(s) * {"float32": 4, "bfloat16": 2}[d]
                     for s, d in zip(c["input_shapes"], c["input_dtypes"]))
        if nbytes != c["logical_input_bytes"]:
            raise ValueError(c["id"] + ": input byte count differs")


def load_manifest():
    if sha256(ROOT / "manifest.json") != MANIFEST_SHA256:
        raise ValueError("manifest.json is not the frozen prediction manifest")
    cases = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["cases"]
    validate_manifest(cases)
    return cases


def bf16_bits(x):
    bits = np.asarray(x, dtype="<f4").view("<u4")
    rounded = bits + np.uint32(0x7fff) + ((bits >> 16) & np.uint32(1))
    result = (rounded >> 16).astype("<u2")
    # Preserve NaNs as NaNs, including payloads whose upper mantissa is zero.
    nan = (bits & 0x7fffffff) > 0x7f800000
    return np.where(nan, (bits >> 16).astype("<u2") | np.uint16(0x40), result).astype("<u2")


def make_arrays(case):
    seed_bytes = hashlib.sha256(f"{SEED}:{case['id']}".encode()).digest()[:8]
    rng = np.random.Generator(np.random.PCG64(int.from_bytes(seed_bytes, "little")))
    arrays = []
    for shape, dtype in zip(case["input_shapes"], case["input_dtypes"]):
        x = rng.random(tuple(shape), dtype=np.float32)
        x *= np.float32(2)
        x -= np.float32(1)
        arrays.append(bf16_bits(x) if dtype == "bfloat16" else x)
    if case["task"] == "rope":
        theta = arrays[2] * np.float32(np.pi)
        arrays[2], arrays[3] = np.cos(theta), np.sin(theta)
    if case["task"] == "mhc_post_bwd":
        # CANN's get_input requires a nonnegative doubly stochastic mix.
        # Normalize in FP64 on CPU, store FP32; no GPU work is timed here.
        matrix = (arrays[2].astype(np.float64) + 1.) * .5 + 1e-10
        for _ in range(100):
            matrix /= matrix.sum(-1, keepdims=True)
            matrix /= matrix.sum(-2, keepdims=True)
            if np.max(np.abs(matrix.sum(-1) - 1.)) < 1e-10:
                break
        arrays[2] = matrix.astype("<f4")
    return arrays


def write_case(case, path):
    path = Path(path)
    if path.exists():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = make_arrays(case)
    np.savez_compressed(path, **{f"arg{i}": x for i, x in enumerate(arrays)})
    return {"case_id": case["id"], "file": path.name, "sha256": sha256(path),
            "file_bytes": path.stat().st_size, "tensor_bytes": sum(x.nbytes for x in arrays)}


def read_case(case, path, record=None):
    path = Path(path)
    if record is not None:
        if record["case_id"] != case["id"] or sha256(path) != record["sha256"]:
            raise ValueError(case["id"] + ": input SHA256/case ID mismatch")
    with np.load(path, allow_pickle=False) as archive:
        keys = [f"arg{i}" for i in range(len(case["input_shapes"]))]
        if set(archive.files) != set(keys):
            raise ValueError(case["id"] + ": input tensor set mismatch")
        arrays = [archive[key] for key in keys]
    for x, shape, dtype in zip(arrays, case["input_shapes"], case["input_dtypes"]):
        storage = np.dtype("<u2" if dtype == "bfloat16" else "<f4")
        if list(x.shape) != shape or x.dtype != storage or not x.flags.c_contiguous:
            raise ValueError(case["id"] + ": input shape/storage dtype/layout mismatch")
    return arrays


def to_torch(arrays, case, device="cpu"):
    import torch
    result = []
    for x, dtype in zip(arrays, case["input_dtypes"]):
        # int16 view also supports torch versions without from_numpy(uint16).
        tensor = torch.from_numpy(x.view(np.int16) if dtype == "bfloat16" else x)
        if dtype == "bfloat16":
            tensor = tensor.view(torch.bfloat16)
        result.append(tensor.to(device=device))
    return result


def verify_all():
    cases = load_manifest()
    index = json.loads((ROOT / "input_index.json").read_text(encoding="utf-8"))
    by_id = {r["case_id"]: r for r in index["files"]}
    expected = {c["id"] for c in cases}
    actual = {p.stem for p in (ROOT / "data").glob("*.npz")}
    if len(index["files"]) != 100 or set(by_id) != expected or actual != expected:
        raise ValueError("Expected the complete 100-case file/index/manifest set")
    total = 0
    for i, c in enumerate(cases, 1):
        arrays = read_case(c, ROOT / "data" / f"{c['id']}.npz", by_id[c["id"]])
        if sum(x.nbytes for x in arrays) != c["logical_input_bytes"]:
            raise ValueError(c["id"] + ": tensor bytes mismatch")
        for x, dtype in zip(arrays, c["input_dtypes"]):
            finite = np.all((x & 0x7f80) != 0x7f80) if dtype == "bfloat16" else np.isfinite(x).all()
            if not finite:
                raise ValueError(c["id"] + ": nonfinite input")
        if c["task"] == "rope":
            np.testing.assert_allclose(arrays[2] ** 2 + arrays[3] ** 2, 1., atol=2e-7)
        if c["task"] == "mhc_post_bwd":
            np.testing.assert_allclose(arrays[2].sum(-1), 1., atol=3e-7)
            np.testing.assert_allclose(arrays[2].sum(-2), 1., atol=3e-7)
        total += sum(x.nbytes for x in arrays)
        print(f"verify {i}/100 {c['id']}", flush=True)
        del arrays
    return {"case_count": 100, "per_task": dict(Counter(c["task"] for c in cases)),
            "tensor_bytes": total, "manifest_sha256": MANIFEST_SHA256,
            "scope": "all full-size input files: SHA256, shapes, storage dtypes, finite values, RoPE unit circle, mHC stochastic mix"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "verify"))
    args = parser.parse_args()
    if args.command == "generate":
        if (ROOT / "input_index.json").exists() or any((ROOT / "data").glob("*.npz")):
            raise FileExistsError("Input files already exist; use verify to check the supplied data")
        records = []
        for i, c in enumerate(load_manifest(), 1):
            records.append(write_case(c, ROOT / "data" / f"{c['id']}.npz"))
            print(f"generate {i}/100 {c['id']}", flush=True)
        value = {"manifest_sha256": MANIFEST_SHA256, "seed": SEED, "numpy": np.__version__,
                 "rng": "PCG64; per-case seed SHA256(base_seed:case_id) first 8 bytes LE",
                 "data_regime": "finite uniform [-1,1); unit-circle RoPE cache; nonnegative doubly stochastic mHC mix; public source_value_range retained for provenance, not replayed",
                 "files": records}
        (ROOT / "input_index.json").write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    else:
        result = verify_all()
        (ROOT / "input_verification.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result))


if __name__ == "__main__":
    main()
