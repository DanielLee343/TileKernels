"""Run the registered expert cases as one cold Default capture per case."""
import argparse
import csv
import ctypes
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import traceback

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "cases.json"
GROUPS = {"ArithmeticUtilization", "L2Cache", "Memory", "MemoryL0", "MemoryUB",
          "PipeUtilization", "ResourceConflictRatio"}


def save(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n")
    temporary.replace(path)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(case, torch):
    from tile_kernels.config import get_num_vec_cores

    seed = int.from_bytes(hashlib.sha256(case["id"].encode()).digest()[:8], "little")
    rng = torch.Generator(device="cpu").manual_seed(seed)
    cores = get_num_vec_cores()
    family = case["family"]
    if family == "engram_fused_weight":
        from tile_kernels.engram.engram_fused_weight_asc import get_engram_fused_weight_kernel_asc

        h = case["hidden"]
        host = tuple(torch.randn((4, h), generator=rng).to(torch.bfloat16) for _ in range(2))
        expected = (host[0].float() * host[1].float(),)
        kernel = get_engram_fused_weight_kernel_asc(h, 4, num_vec_cores=cores)
    elif family == "moe_topk_gate":
        from tile_kernels.moe.topk_gate_asc import get_topk_gate_kernel_asc
        n, experts, k = case["tokens"], case["experts"], case["topk"]
        scores = torch.randn((n, experts), generator=rng)
        host = (scores,)
        expected = (torch.argsort(scores, dim=-1, descending=True, stable=True)[:, :k].contiguous(),)
        kernel = get_topk_gate_kernel_asc(experts, k, num_vec_cores=cores)
    elif family == "engram_sinkhorn_step_reduce":
        from tile_kernels.engram.engram_sinkhorn_asc import get_engram_sinkhorn_step_reduce_kernel_asc
        partials, h = case["num_partials"], case["head_dim"]
        x = torch.rand((partials, h), generator=rng)
        host = (x,)
        expected = (x.sum(dim=0),)
        kernel = get_engram_sinkhorn_step_reduce_kernel_asc(h, partials, num_vec_cores=cores)
    elif family == "mhc_head_compute_mix_fwd":
        from tile_kernels.mhc.head_compute_mix_asc import mhc_head_compute_mix_fwd_asc
        from tile_kernels.mhc.head_compute_mix_kernel import _get_ascend_token_block_size
        n, mult, eps = case["tokens"], case["mhc_mult"], case["eps"]
        x = torch.randn((n, mult), generator=rng)
        scale = torch.randn((1,), generator=rng)
        base = torch.randn((mult,), generator=rng)
        host = (x, scale, base)
        expected = (torch.sigmoid(x * scale + base) + eps,)
        device = tuple(t.to("npu:0") for t in host)
        dummy = torch.empty_like(device[0])
        kernel = mhc_head_compute_mix_fwd_asc.compile(*device, dummy, mhc_pre_eps=eps,
                   token_block_size=_get_ascend_token_block_size(n, mult), num_vec_cores=cores)
        return kernel, host, device, expected
    elif family == "mhc_pre_apply_mix_fwd":
        from tile_kernels.mhc.pre_apply_mix_asc import mhc_pre_apply_mix_fwd_asc
        from tile_kernels.utils import align, ceil_div
        n, mult, h = case["tokens"], case["mhc_mult"], case["hidden"]
        x = torch.randn((n, mult, h), generator=rng).sigmoid().to(torch.bfloat16)
        mix = torch.randn((n, mult), generator=rng).softmax(dim=-1)
        host = (x, mix)
        expected = ((x.float() * mix.unsqueeze(-1)).sum(dim=1).to(torch.bfloat16),)
        device = tuple(t.to("npu:0") for t in host)
        dummy = torch.empty((n, h), dtype=torch.bfloat16, device="npu:0")
        h_blk = align(h if h <= 6144 else min(ceil_div(h, 2), 6144), 64)
        kernel = mhc_pre_apply_mix_fwd_asc.compile(*device, dummy, h_blk=h_blk, num_vec_cores=cores)
        return kernel, host, device, expected
    elif family == "mhc_fn_normw_merge_fwd":
        from tile_kernels.mhc.norm_fn_asc import mhc_fn_normw_merge_fwd_asc
        h = case["hidden_size"] * case["mhc_mult"]
        fn = torch.randn((24, h), generator=rng)
        normw = torch.randn((h,), generator=rng)
        host = (fn, normw)
        expected = (fn * normw,)
        device = tuple(t.to("npu:0") for t in host)
        dummy = torch.empty_like(device[0])
        kernel = mhc_fn_normw_merge_fwd_asc.compile(*device, dummy, mhc_mult3=24, hidden_block=256,
                                                    num_stages=3, num_vec_cores=cores)
        return kernel, host, device, expected
    elif family == "mhc_reduce_partials_and_rmsnorm_fwd":
        from tile_kernels.mhc.norm_fn_asc import mhc_reduce_partials_and_rmsnorm_fwd_asc
        n, h, mult = case["tokens"], case["hidden_size"], case["mhc_mult"]
        mul = torch.randn((1, n, 1, 24), generator=rng)
        sq = torch.rand((1, n, 1), generator=rng) + 0.5
        o_mul, o_sq = mul.sum(0), sq.sum(0)
        out = (o_mul * (o_sq / (mult * h) + 1e-6).rsqrt().unsqueeze(-1)).sum(-2)
        host = (mul, sq)
        expected = (o_mul, o_sq, out)
        device = tuple(t.to("npu:0") for t in host)
        dummy = tuple(torch.empty_like(t,device="npu:0") for t in expected)
        kernel = mhc_reduce_partials_and_rmsnorm_fwd_asc.compile(*device, *dummy,
                 rms_group_size=mult*h, rms_eps=1e-6, n_splits=1, num_vec_cores=cores)
        return kernel, host, device, expected
    elif family in ("mhc_expand_fwd", "mhc_expand_bwd"):
        from tile_kernels.mhc.expand_asc import expand_to_mhc_fwd_asc, expand_to_mhc_bwd_asc
        from tile_kernels.mhc.expand_kernel import _asc_fwd_h_blk, _asc_h_blk
        n, h, mult = case["tokens"], case["hidden"], case["mhc_mult"]
        if family == "mhc_expand_fwd":
            x = torch.randn((n, h), generator=rng).to(torch.bfloat16)
            expected = (x.unsqueeze(1).expand(n, mult, h).contiguous(),)
            native = expand_to_mhc_fwd_asc
            kwargs = dict(h_blk=_asc_fwd_h_blk(h, mult), num_stages=7, num_vec_cores=cores)
        else:
            x = torch.randn((n, mult, h), generator=rng).to(torch.bfloat16)
            expected = (x.float().sum(dim=1).to(torch.bfloat16),)
            native = expand_to_mhc_bwd_asc
            kwargs = dict(h_blk=_asc_h_blk(h), num_stages=3, num_vec_cores=cores)
        host = (x,)
        device = (x.to("npu:0"),)
        dummy = torch.empty(expected[0].shape, dtype=expected[0].dtype, device="npu:0")
        kernel = native.compile(*device, dummy, **kwargs)
        return kernel, host, device, expected
    elif family in ("mhc_sinkhorn_fwd", "mhc_sinkhorn_bwd"):
        from tile_kernels.torch.mhc import sinkhorn_normalize_ref
        from tile_kernels.mhc.sinkhorn_asc import mhc_sinkhorn_fwd_asc, mhc_sinkhorn_bwd_asc
        n, repeat, eps = case["tokens"], case["repeat"], case["eps"]
        x = torch.randn((n, 4, 4), generator=rng)
        if family == "mhc_sinkhorn_fwd":
            host = (x,)
            expected = (sinkhorn_normalize_ref(x, repeat, eps),)
            native = mhc_sinkhorn_fwd_asc
            kwargs = dict(repeat=repeat, eps=eps, token_block_size=4, num_vec_cores=cores)
        else:
            grad = torch.randn((n, 4, 4), generator=rng)
            ref_x = x.detach().requires_grad_(True)
            y = sinkhorn_normalize_ref(ref_x, repeat, eps)
            expected = (torch.autograd.grad(y, ref_x, grad)[0].detach(),)
            host = (grad, x)
            native = mhc_sinkhorn_bwd_asc
            kwargs = dict(repeat=repeat, eps=eps, token_block_size=8, num_vec_cores=cores)
        device = tuple(t.to("npu:0") for t in host)
        dummy = torch.empty_like(device[-1])
        kernel = native.compile(*device, dummy, **kwargs)
        return kernel, host, device, expected
    elif family == "mhc_post_fwd":
        from tile_kernels.mhc.post_asc import mhc_post_fwd_asc
        from tile_kernels.torch.mhc import mhc_post_ref
        from tile_kernels.utils import align, ceil_div
        n, h, mult = case["tokens"], case["hidden"], case["mhc_mult"]
        x = torch.randn((n, h), generator=rng).to(torch.bfloat16)
        residual = torch.randn((n, mult, h), generator=rng).to(torch.bfloat16)
        post = torch.randn((n, mult), generator=rng)
        comb = torch.randn((n, mult, mult), generator=rng)
        host = (comb, residual, post, x)
        ref = mhc_post_ref(x.unsqueeze(0), residual.unsqueeze(0), post.unsqueeze(0).unsqueeze(-1), comb.unsqueeze(0)).squeeze(0)
        expected = (ref,)
        device = tuple(t.to("npu:0") for t in host)
        dummy = torch.empty_like(residual, device="npu:0")
        h_blk = align(h if h <= 4096 else min(ceil_div(h, 2), 4096), 64)
        kernel = mhc_post_fwd_asc.compile(*device, dummy, h_blk=h_blk, num_vec_cores=cores)
        return kernel, host, device, expected
    elif family == "engram_sinkhorn_finalize":
        from tile_kernels.engram.engram_sinkhorn_asc import get_engram_sinkhorn_finalize_kernel_asc
        from tile_kernels.torch.engram import engram_sinkhorn_finalize_ref
        n, h, eps = case["num_rows"], case["head_dim"], case["eps"]
        matrix = torch.randn((n, h), generator=rng)
        row = torch.rand((n,), generator=rng)
        col = torch.rand((h,), generator=rng)
        host = (matrix, row, col)
        expected = (engram_sinkhorn_finalize_ref(matrix, row, col, eps, h ** 0.5),)
        kernel = get_engram_sinkhorn_finalize_kernel_asc(h, eps, h ** 0.5, num_vec_cores=cores)
    elif family == "mhc_reduce_partials_and_rmsnorm_bwd":
        from tile_kernels.mhc.norm_fn_asc import mhc_reduce_partials_and_rmsnorm_bwd_asc
        n, h, mult = case["tokens"], case["hidden_size"], case["mhc_mult"]
        grad = torch.randn((n, 24), generator=rng)
        mul = torch.randn((n, 1, 24), generator=rng).requires_grad_(True)
        sq = (torch.rand((n, 1), generator=rng) + 0.5).requires_grad_(True)
        ref = (mul * (sq / (mult * h) + 1e-6).rsqrt().unsqueeze(-1)).sum(-2)
        out_mul_grad, sq_grad = torch.autograd.grad(ref, (mul, sq), grad)
        host = (grad, mul.detach(), sq.detach())
        expected = (out_mul_grad.detach(), sq_grad.detach())
        device = tuple(t.to("npu:0") for t in host)
        dummy = tuple(torch.empty_like(t, device="npu:0") for t in expected)
        kernel = mhc_reduce_partials_and_rmsnorm_bwd_asc.compile(*device, *dummy,
                 rms_group_size=mult*h, rms_eps=1e-6, num_vec_cores=cores)
        return kernel, host, device, expected
    elif family == "moe_normalize_weight":
        from tile_kernels.moe.normalize_weight_asc import get_normalize_weight_kernel_asc
        from tile_kernels.torch.moe import normalize_weight

        n, k = case["tokens"], case["topk"]
        host = (torch.rand((n, k), generator=rng),)
        expected = normalize_weight(host[0])
        kernel = get_normalize_weight_kernel_asc(num_topk=k, num_vec_cores=cores)
    elif family == "quant_cast_back":
        from tilelang import language as T
        from tile_kernels.quant.cast_back_asc import get_cast_back_kernel_asc
        from tile_kernels.quant.common import get_cast_input_and_config

        n, h = case["tokens"], case["hidden"]
        quant = torch.randint(-5, 6, (n, h), generator=rng).to(torch.float8_e4m3fn)
        scale = torch.rand((n, h // 32), generator=rng) + 0.25
        host = (quant, scale)
        output_dtype = getattr(torch, case["output_dtype"])
        expected = ((quant.float() * scale.repeat_interleave(32, dim=1)).to(output_dtype),)
        device_quant = quant.view(torch.uint8).to("npu:0").view(torch.float8_e4m3fn)
        device_scale = scale.to("npu:0")
        x, sf, config = get_cast_input_and_config((device_quant, device_scale), (1, 32))
        kernel = get_cast_back_kernel_asc(h, config, T.dtype(output_dtype), num_vec_cores=cores)
        return kernel, host, (x, sf), expected
    elif family == "engram_hash":
        from tile_kernels.engram.engram_hash_asc import get_engram_hash_kernel_asc
        from tile_kernels.torch.engram import engram_hash_ref, make_offsets

        n, g = case["tokens"], case["ngram"]
        ids = torch.randint(0, 100000, (n, g), dtype=torch.int32, generator=rng)
        mult = torch.randint(0, 100000, (2, g), dtype=torch.int64, generator=rng)
        sizes = torch.randint(100000, 1000000, (2, g - 1, 8), dtype=torch.int32, generator=rng)
        mask = torch.rand(n, generator=rng) < 0.5 if case["mask"] else None
        host = (ids, mult, sizes, make_offsets(sizes), mask)
        expected = (engram_hash_ref(*host),)
        kernel = get_engram_hash_kernel_asc(g, 2, 8, has_image_token_mask=mask is not None, num_vec_cores=cores)
    else:
        raise ValueError(f"Unregistered family: {family}")
    return kernel, host, tuple(x.to("npu:0") if x is not None else None for x in host), expected


def describe(x, with_hash=False):
    if x is None:
        return None
    data = {"shape": list(x.shape), "dtype": str(x.dtype).removeprefix("torch."),
            "stride": list(x.stride()), "bytes": x.numel() * x.element_size()}
    if with_hash:
        data["sha256"] = hashlib.sha256(x.contiguous().view(-1).view(__import__("torch").uint8).numpy().tobytes()).hexdigest()
    return data


def compare(torch, actual, expected, family):
    result = []
    assert len(actual) == len(expected)
    for output_id, (gpu, ref) in enumerate(zip(actual, expected, strict=True)):
        out = gpu.cpu()
        assert out.shape == ref.shape and out.dtype == ref.dtype, (out.shape, ref.shape, out.dtype, ref.dtype)
        a, b = out.flatten().double(), ref.flatten().double()
        assert torch.isfinite(a).all() and torch.isfinite(b).all(), output_id
        norm_a, norm_b = torch.linalg.vector_norm(a).item(), torch.linalg.vector_norm(b).item()
        exact = torch.equal(out, ref)
        cosine = float(torch.dot(a, b)) / (norm_a * norm_b) if norm_a and norm_b else None
        maximum = (a - b).abs().max().item()
        if family == "mhc_post_fwd":
            diagnostic = bool(torch.isclose(a, b, rtol=0.016, atol=1e-5, equal_nan=False).all())
        elif family == "engram_sinkhorn_finalize":
            diagnostic = bool(torch.isclose(a, b, rtol=1.3e-6, atol=1e-5, equal_nan=False).all())
        elif family == "mhc_reduce_partials_and_rmsnorm_bwd":
            denominator = (a.square() + b.square()).sum().item()
            diagnostic = (0.0 if denominator == 0 else (a - b).square().sum().item() / denominator) < 1e-8
        elif family in ("mhc_sinkhorn_fwd", "mhc_sinkhorn_bwd", "engram_sinkhorn_step_reduce"):
            diagnostic = bool(torch.isclose(a, b, rtol=1.3e-6, atol=1e-5, equal_nan=False).all())
        elif family == "mhc_expand_bwd":
            diagnostic = bool(torch.isclose(a, b, rtol=2**-7, atol=2e-3, equal_nan=False).all())
        elif family == "mhc_head_compute_mix_fwd":
            diagnostic = bool(torch.isclose(a, b, rtol=1e-4, atol=1e-5, equal_nan=False).all())
        elif family == "mhc_pre_apply_mix_fwd":
            diagnostic = bool(torch.isclose(a, b, rtol=1e-3, atol=1e-2, equal_nan=False).all())
        elif family == "mhc_fn_normw_merge_fwd":
            diagnostic = bool(torch.isclose(a, b, rtol=1e-6, atol=1e-6, equal_nan=False).all())
        elif family == "mhc_reduce_partials_and_rmsnorm_fwd":
            diagnostic = bool(torch.isclose(a, b, rtol=1e-3, atol=1e-3, equal_nan=False).all())
        else:
            diagnostic = maximum <= 2e-6 if family == "moe_normalize_weight" else exact
        passed = diagnostic  # Require the stronger full-output diagnostic, not cosine alone.
        if not ref.is_floating_point():
            passed = exact and passed
        result.append({"output_id": output_id, "cosine_fp64": cosine, "max_abs_error": maximum,
                       "exact_equal": exact, "reference_diagnostic_passed": diagnostic, "passed": passed})
    return result


def target_range(torch, launch):
    for _ in range(5):
        launch()
    torch.npu.synchronize()
    library = Path(os.environ["ASCEND_HOME_PATH"]) / "tools/mstx/lib64/libms_tools_ext.so"
    api = ctypes.CDLL(str(library))
    start, end = api.mstxRangeStartA, api.mstxRangeEnd
    start.argtypes, start.restype = [ctypes.c_char_p, ctypes.c_void_p], ctypes.c_uint64
    end.argtypes, end.restype = [ctypes.c_uint64], None
    stream = ctypes.c_void_p(int(torch.npu.current_stream().npu_stream))
    handle = start(b"cold_call", stream)
    try:
        launch()
    finally:
        end(handle)
    torch.npu.synchronize()


def application(case, stage, directory):
    import torch
    import torch_npu  # registers the NPU backend

    torch.set_num_threads(min(8, os.cpu_count() or 1))
    torch.npu.set_device(0)
    kernel, host, device, expected = build(case, torch)
    output = tuple(torch.empty_like(x, device="npu:0") for x in expected)
    symbol = str(kernel.prim_func.attrs["global_symbol"])
    generated = directory / f"{stage}-kernel.cpp"
    generated.write_text(kernel.get_kernel_source())
    record = {"runtime_kernel": symbol + "_kernel", "native_symbol": symbol,
              "source_sha256": digest(generated), "inputs": [describe(x, True) for x in host],
              "device_inputs": [describe(x) for x in device], "outputs": [describe(x) for x in output]}
    def launch():
        kernel(*device, *output)

    if stage == "default":
        target_range(torch, launch)
    else:
        launch()
        torch.npu.synchronize()
    record["precision"] = compare(torch, output, expected, case["family"])
    record["status"] = "passed" if all(x["passed"] for x in record["precision"]) else "failed"
    save(directory / f"{stage}.json", record)
    return record["status"] == "passed"


def run(command, log, timeout):
    with log.open("w") as out:
        process = subprocess.Popen(command, stdout=out, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            return process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=10)
            return 124


def inspect_capture(directory, name):
    basic_path, = (directory / "capture").rglob("OpBasicInfo.csv")
    with basic_path.open(encoding="utf-8-sig", newline="") as source:
        info, = csv.DictReader(source)
    assert info["Op Name"] == name and info["Device Id"] == "0", info["Op Name"]
    assert info["Op Type"] == "vector" and 1 <= int(info["Block Dim"]) <= 56, (info["Op Type"], info["Block Dim"])
    file_map = {}
    for group in sorted(GROUPS):
        path = basic_path.with_name(group + ".csv")
        with path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.DictReader(source)
            keys = [(row["block_id"], row["sub_block_id"]) for row in reader]
        blocks = int(info["Block Dim"])
        assert len(keys) == blocks and set(keys) == {(str(i), "vector0") for i in range(blocks)}, group
        file_map[group] = {"path": str(path.relative_to(ROOT)), "sha256": digest(path),
                           "rows": len(keys), "fields": reader.fieldnames}
    file_map["OpBasicInfo"] = {"path": str(basic_path.relative_to(ROOT)), "sha256": digest(basic_path), "rows": 1}
    return {"device_id": info["Device Id"], "frequency": info["Current Freq"],
            "rated_frequency": info["Rated Freq"], "type": info["Op Type"], "blocks": int(info["Block Dim"]),
            "files": file_map}


def run_case(case):
    directory = ROOT / "cases" / case["id"]
    directory.mkdir(parents=True)
    # Limit peak host memory in this 32 GiB container until comparison is chunked.
    if case["family"] == "engram_sinkhorn_finalize" and case["num_rows"] * case["head_dim"] > 50_000_000:
        outcome = {"id": case["id"], "family": case["family"], "role": case["role"],
                   "status": "skipped", "reason": "host memory guard: more than 50M float32 input elements"}
        save(directory / "result.json", outcome)
        return outcome
    if case["family"] == "mhc_post_fwd" and case["tokens"] * case["hidden"] * case["mhc_mult"] > 50_000_000:
        outcome = {"id": case["id"], "family": case["family"], "role": case["role"],
                   "status": "skipped", "reason": "host memory guard: more than 50M residual elements"}
        save(directory / "result.json", outcome)
        return outcome
    # Serial execution: check for other visible work before each case.
    idle = subprocess.run(["npu-smi", "info", "-t", "proc-mem", "-i", "0"], text=True, capture_output=True, timeout=20)
    (directory / "device-before.txt").write_text(idle.stdout + idle.stderr)
    if idle.returncode != 0 or "No process in device." not in idle.stdout:
        outcome = {"id": case["id"], "family": case["family"], "role": case["role"],
                   "status": "skipped", "reason": "NPU not confirmed idle at start"}
        save(directory / "result.json", outcome)
        return outcome
    invoke = [sys.executable, "-B", __file__, "application", case["id"]]
    outcome = {"id": case["id"], "family": case["family"], "role": case["role"]}
    try:
        prepare = invoke + ["prepare"]
        outcome["prepare_rc"] = run(prepare, directory / "prepare.log", 300)
        assert outcome["prepare_rc"] == 0, "prepare failed"
        prep = json.loads((directory / "prepare.json").read_text())
        command = ["msprof", "op", f"--output={directory / 'capture'}", "--aic-metrics=Default",
                   "--replay-mode=kernel", "--mstx=true", "--mstx-include=cold_call",
                   f"--kernel-name={prep['runtime_kernel']}", "--launch-count=1", "--warm-up=5"]
        command += invoke + ["default"]
        outcome["default_command"] = command
        outcome["default_rc"] = run(command, directory / "default.log", 300)
        assert outcome["default_rc"] == 0, "Default command failed"
        launch = json.loads((directory / "default.json").read_text())
        assert launch["status"] == "passed", "post-replay full-output precision failed"
        assert launch["source_sha256"] == prep["source_sha256"] and launch["inputs"] == prep["inputs"], "prepare/replay mismatch"
        outcome["capture"] = inspect_capture(directory, prep["runtime_kernel"])
        after = subprocess.run(["npu-smi", "info", "-t", "proc-mem", "-i", "0"], text=True, capture_output=True, timeout=20)
        (directory / "device-after.txt").write_text(after.stdout + after.stderr)
        if after.returncode != 0 or "No process in device." not in after.stdout:
            outcome["status"] = "needs_review"
            outcome["reason"] = "NPU not confirmed idle after capture; possible interference"
        else:
            outcome["status"] = "admitted"
    except Exception as error:
        outcome.update(status="failed", reason=f"{type(error).__name__}: {error}")
    save(directory / "result.json", outcome)
    return outcome


def batch(manifest, phase):
    toolkit = Path("/workspace/tilekernels-env-20261101/src/TileKernels")
    rev = subprocess.check_output(["git", "-C", toolkit, "rev-parse", "HEAD"], text=True).strip()
    changes = subprocess.check_output(["git", "-C", toolkit, "status", "--porcelain"], text=True)
    op = subprocess.check_output(["msprof", "op", "--version"], text=True)
    device = subprocess.check_output(["npu-smi", "info"], text=True)
    assert rev == manifest["tilekernels_commit"] and not changes
    assert manifest["msopprof_commit"] in op and manifest["device_bus"] in device
    assert os.environ["ASCEND_HOME_PATH"].endswith("/cann-9.2.1"), os.environ["ASCEND_HOME_PATH"]
    save(ROOT / "environment.json", {"tilekernels_commit": rev, "profiler": op, "npu_smi": device,
                                     "cann": os.environ["ASCEND_HOME_PATH"], "manifest_sha256": digest(MANIFEST)})
    cases = manifest["cases"]
    assert len(cases) == manifest["capture_budget"] == len({c["id"] for c in cases})
    result_path = ROOT / "progress.json"
    if phase == "pilot":
        assert not result_path.exists()
        result = {"status": "running", "cases": []}
    else:
        result = json.loads(result_path.read_text())
        assert result["status"] == "pilot_finished"
        result["status"] = "running"
    passed_families = {c["family"] for c in result["cases"] if c["status"] == "admitted"}
    for case in cases:
        if bool(case.get("pilot")) != (phase == "pilot"):
            continue
        if phase == "remaining" and case["family"] not in passed_families:
            outcome = {k: case[k] for k in ("id", "family", "role")}
            outcome.update(status="skipped", reason="family pilot failed")
        else:
            outcome = run_case(case)
        result["cases"].append(outcome)
        save(result_path, result)
        print(case["id"], outcome["status"], outcome.get("reason", ""), flush=True)
    result["status"] = "pilot_finished" if phase == "pilot" else "finished"
    save(result_path, result)


def main():
    manifest = json.loads(MANIFEST.read_text())
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    run_batch = sub.add_parser("batch")
    run_batch.add_argument("phase", choices=("pilot", "remaining"))
    app = sub.add_parser("application")
    app.add_argument("case")
    app.add_argument("stage", choices=("prepare", "default"))
    args = parser.parse_args()
    if args.command == "batch":
        batch(manifest, args.phase)
        return
    case = next(c for c in manifest["cases"] if c["id"] == args.case)
    directory = ROOT / "cases" / case["id"]
    try:
        ok = application(case, args.stage, directory)
    except Exception:
        save(directory / f"{args.stage}.json", {"status": "failed", "error": traceback.format_exc()})
        raise
    raise SystemExit(0 if ok else 2)


if __name__ == "__main__":
    main()

