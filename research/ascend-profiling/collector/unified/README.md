# Shared profile runner investigation (2026-11-06)

The 657 unmapped plan entries comprise 100 Engram, 140 mHC, 40 MoE, 337 quant, 20 randn and 20 RoPE entries, across 33 plan groups. This is a candidate inventory, not a claim that all entries are supported or runnable.

The common work is reading the immutable plan, generating inputs, validating outputs, isolating the intended native launch with MSTX, invoking msprof Default, checking the kernel identity and raw metric tables, and saving status and hashes. The differing work is input and output semantics. Existing upstream tests and their references can be reused only when the test exercises the exact planned mode and parameters.

## Device-validated prototype

`quant_hook.py` wraps the native factory used by upstream per-token/per-block quant tests and marks the first matching mode (normal, scale-only or precomputed scale). The standalone hidev pilot captured `per_token_cast_kernel_kernel`, and prepare/replay source and full input hashes matched while the upstream test passed. The first profiler invocation failed because spaced JSON was split by the profiler; URL-safe base64 fixed that error. This validates one case, not all six modes or all 120 cases.

`run_quant.py` handles 120 original plan rows across six modes. It pilots each mode; a failed pilot causes the rest of that mode to be explicitly skipped, not claimed as profiled. Each attempt uses a fresh process, records errors, verifies all target CSV identity and hashes, and captures only one named vector kernel. `sync_unified_quant.py` transfers verified snapshots. The upstream tests may execute input-generation and reference kernels outside the marked range.

## Required further handling

- Original plan rows are not all fully specified call contracts. Engram gate fwd omits save/inplace mode; those must be explicitly recorded rather than treated as all three modes.
- MoE test benchmark wrappers hardcode fix_routing=False: do not use them for plan entries with True.
- Backward and mutable buffers require reset/replay semantics; profiler kernel replay must not be equated with NPU graph capture.
- RoPE Q/K are two in-place target launches; label each. randn and stochastic rounding need their upstream reproducibility/distribution checks.
- mHC backward can include additional partial reductions outside the native kernel; report the capture scope precisely. Multilayer recompute constructs device address tables.
- Cgroup host limit is 32 GiB; large inputs require bounded-memory validation, not shrinking the planned shape. A failed/unsupported case remains visible and must not be counted as successful.

Other 537 plan rows do not have an implemented shared runner. Previous 3 failed correctness cases and 11 memory-guard skips remain separate from the 657 unmapped rows.

The initial 120-case queue was stopped after its per-block pilot exposed nondeterministic Python `random` state. Its failed and in-flight data remain on hidev at `/workspace/tilekernels-expert-unified-quant-20261106`. The hook now fixes both the upstream Torch/TileKernels RNG and Python RNG. A separate per-block pilot then passed reference validation and matched prepare/profile input and source hashes. The original run is never overwritten.

A subsequent `run_extra.py` manifest queues 60 original plan rows: stochastic cast, mHC head backward, and Engram gradient reduction (20 each). These adapters are static-checked only until their hidev pilots finish. Head backward captures its native kernel; its partial reductions and reference comparison happen outside capture. Engram gradient accumulation uses separate warmup buffers and is marked `needs_review` even if correctness passes, until profiler replay restoration is independently checked.

Both sync watchers retry temporary transfer failures. They only auto-push a previously failed local commit when every unpushed commit is a sync commit and every changed file belongs to that watcher’s run directory.

A third shared manifest queues 117 additional rows: per-channel cast, lossless block cast, remaining cast-back cases, randn, and mHC post backward. These modes are pending device pilots; full shapes and original parameters are retained. randn explicitly records that profiler replay is not proof of fresh random samples. mHC post backward uses bounded host-memory generation and validation but still requires the full NPU allocation.

A fourth shared manifest queues 100 more original rows: norm forward/backward, mHC big fuse forward, MoE topk forward and SwiGLU forward. These modes have not yet passed hidev pilots. Each case is attempted separately even if its mode pilot fails; failures are recorded. Stateful replay cases require review. All four shared manifests cover 397 of the 657 previously unmapped rows; 260 still need adapters.

A fifth shared manifest contains 120 additional original plan rows across six modes, expressed as 140 capture tasks because each of the 20 RoPE cases has distinct Q and K launches. These modes are pending device pilots; stateful replay remains flagged for review. The five shared manifests map 517 of 657 previously unmapped plan rows; 140 still need adapters.
