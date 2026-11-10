"""Map frozen CANN-order tensors to genuine TileKernels entry points."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent
GOLDEN_NAMES = {"swiglu": "swi_glu", "rmsnorm": "rms_norm", "rope": "apply_rotary_pos_emb",
                "sinkhorn": "mhc_sinkhorn", "mhc_post_bwd": "mhc_post_grad"}


def native_api():
    from tile_kernels.config import is_ascend
    if not is_ascend():
        raise RuntimeError("This handoff requires the TileKernels Ascend backend")
    from tile_kernels.quant.swiglu_forward_kernel import swiglu_forward
    from tile_kernels.quant.norm_forward_kernel import norm_forward
    from tile_kernels.transform.rope_kernel import apply_rotary
    from tile_kernels.mhc.sinkhorn_kernel import mhc_sinkhorn_fwd
    from tile_kernels.mhc.post_kernel import mhc_post_bwd
    return SimpleNamespace(swiglu=swiglu_forward, norm=norm_forward, rope=apply_rotary,
                           sinkhorn=mhc_sinkhorn_fwd, post=mhc_post_bwd)


def cann_reference(case, tensors):
    task = case["task"]
    path = ROOT / "vendor/cann_refs" / f"{task}.py"
    spec = importlib.util.spec_from_file_location("handoff_cann_" + task, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    value = getattr(module, GOLDEN_NAMES[task])(*tensors, **case["attrs"])
    return tuple(value) if isinstance(value, (list, tuple)) else (value,)


def prepare(case, tensors, api=None):
    """Return (launch, outputs). All data/layout preparation precedes launch.

    outputs() is always in prediction order. No mathematical reference is
    called inside launch; only real device APIs run during measurement.
    """
    import torch
    api = native_api() if api is None else api
    task, attrs = case["task"], case["attrs"]
    last = [None]
    if task == "swiglu":
        fmt = "bf16" if tensors[0].dtype == torch.bfloat16 else "fp32"
        def launch():
            last[0] = (api.swiglu(tensors[0], fmt=fmt),)
    elif task == "rmsnorm":
        x, weight = tensors
        out = torch.empty_like(x)
        # Native norm_forward accepts both 2D and 3D; keep original rank.
        def launch():
            result = api.norm(x, weight, eps=attrs["epsilon"], out=out, with_rstd=False)
            last[0] = (result[0],)
    elif task == "rope":
        query, key, cosine, sine = tensors
        cache = torch.cat((cosine, sine), dim=-1).contiguous()
        def launch():
            api.rope(query, cache, key=key, interleaved=attrs["rotaryMode"] == "interleaved")
            last[0] = (query, key)
    elif task == "sinkhorn":
        x = tensors[0]
        out = torch.empty_like(x)
        def launch():
            api.sinkhorn(x, out, repeat=attrs["iter_step"], eps=attrs["eps"])
            last[0] = (out,)
    elif task == "mhc_post_bwd":
        dy, residual, comb, x, post = tensors
        post_view = post.unsqueeze(-1)
        def launch():
            dx, dr, dp, dc = api.post(x, residual, post_view, comb, dy)
            # CANN prediction order: d_residual, d_comb, d_x, d_post.
            last[0] = (dr, dc, dx, dp.squeeze(-1))
    else:
        raise ValueError("Unknown task: " + task)
    def outputs():
        if last[0] is None:
            raise RuntimeError("Call launch before reading outputs")
        return last[0]
    return launch, outputs
