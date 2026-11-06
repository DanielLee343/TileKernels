# First hidev Default batch

The 60 cases correspond to the first candidate-plan groups `engram_fused_weight`, `engram_hash`, and `moe_normalize_weight` (20 per group). They are a partial campaign; all other 940 cases remain pending.

`collect.py` is adapted from the existing 4A collector. Each case has one prepare, five application warmups, MSTX `cold_call`, msprof op Default kernel replay, five profiler warmups, and full-output correctness plus matching source/input hashes. Captures are one each, not independent repeats. Before and after snapshots only detect visible contention at those moments. If a family pilot fails, its remaining cases are skipped.

Run `batch pilot` followed by `batch remaining` in the dedicated hidev directory after activating the pinned environment and checking the physical device. Each case preserves the raw `capture/` directory, metadata, logs and `result.json`. Candidate plan identity is included in cases.json.
