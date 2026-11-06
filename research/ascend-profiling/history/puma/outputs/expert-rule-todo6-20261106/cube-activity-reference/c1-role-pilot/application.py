"""Exact C1 task with one marked call, using the existing frozen implementations."""

import argparse
import ctypes
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import sys
import traceback


def digest(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=["cann", "triton"])
    parser.add_argument("stage", choices=["trace", "basic", "default"])
    parser.add_argument("--source-dir", required=True)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    record = {"status": "failed", "role": args.role, "stage": args.stage}
    try:
        source = Path(args.source_dir).resolve(strict=True)
        sys.path.insert(0, str(source))
        import fixture
        import numpy as np
        import torch
        import torch_npu

        inputs = [Path(args.fixture, name).read_bytes() for name in ("a.bin", "b.bin", "gold.bin")]
        if tuple(inputs) != fixture.fixture():
            raise ValueError("fixture differs from integer reference")
        record["fixture_sha256"] = [digest(data) for data in inputs]
        record["source_sha256"] = {name: digest((source / name).read_bytes())
                                   for name in ("run.py", "fixture.py", "matmul_demo.py")}
        torch.set_num_threads(8)
        torch.npu.set_device(0)
        host = [torch.from_numpy(np.frombuffer(data, dtype="<f2").copy().reshape(256, 256))
                for data in inputs[:2]]
        a, b = (tensor.to("npu:0") for tensor in host)
        if args.role == "cann":
            launch = lambda: torch.mm(a, b)
        else:
            from matmul_demo import tiled_matmul
            launch = lambda: tiled_matmul(a, b)
        if args.stage in ("basic", "default"):
            for _ in range(5):
                launch()
            torch.npu.synchronize()
        mstx = ctypes.CDLL(str(Path(os.environ["ASCEND_HOME_PATH"]) / "tools/mstx/lib64/libms_tools_ext.so"))
        start, end = mstx.mstxRangeStartA, mstx.mstxRangeEnd
        start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
        end.argtypes, end.restype = [ctypes.c_uint64], None
        stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
        handle = start(b"c1_exact_target", stream)
        try:
            result = launch()
        finally:
            end(handle)
        torch.npu.synchronize()
        data = result.cpu().contiguous().view(torch.uint8).numpy().tobytes()
        (out / "output.bin").write_bytes(data)
        (out / "proc-maps.txt").write_text(Path("/proc/self/maps").read_text())
        tensors = [a, b, result]
        record.update(
            exact=data == inputs[2], output_sha256=digest(data),
            tensors=[{"shape": list(t.shape), "stride": list(t.stride()),
                      "dtype": str(t.dtype), "format": int(torch_npu.get_npu_format(t))} for t in tensors],
            executable=sys.executable, ascend_home=os.path.realpath(os.environ["ASCEND_HOME_PATH"]),
            packages={name: importlib.metadata.version(name)
                      for name in (["torch", "torch-npu"] + (["triton"] if args.role == "triton" else []))},
        )
        if not record["exact"]:
            raise ValueError("full output differs from reference")
        record["status"] = "exact_pass_identity_unverified"
    except Exception:
        record["error"] = traceback.format_exc()
    (out / "result.json").write_text(json.dumps(record, indent=2) + "\n")
    if record["status"] != "exact_pass_identity_unverified":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
