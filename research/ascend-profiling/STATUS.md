# Collection status

- Historical import: 140 selected original `OPPROF` directories and related metadata; verified through `MANIFEST.json` and the inventory. Historic profile status, hardware and warmup remain as recorded.
- Candidate plan: 50 task/mode groups, 20 planned cases each. Cases are not all implemented or validated on hidev; the total is not a count of compiled kernels.
- New `msprof op --aic-metrics=Default` collection: first 60 cases mapped across `engram_fused_weight`, `engram_hash`, and `moe_normalize_weight`. A snapshot of completed cases, including the three family pilots, is in `runs/hidev-20261106-starter/`; `python research/ascend-profiling/verify_run.py` checks the snapshot. Further cases were running serially on hidev at the time of that snapshot. At launch the host recorded physical PCI `0000:57:00.0`, CANN 9.2.1 and msopprof build `884ac969494a186a9c63ac45c4c39ad7289b3215`. Remote working directory: `/workspace/tilekernels-expert-profiles-20261106`. See the snapshot `progress.json` for its exact count and status; the remote can be newer.
- A second batch of 123 cases (TopK, Engram Sinkhorn reduction, mHC Sinkhorn forward/backward, mHC expand forward/backward, and 3 FP8 cast-back cases) has been prepared and queued to start after the first batch finishes. These adapters have offline structural checks but have not yet passed their on-device pilots. Remote directory: `/workspace/tilekernels-expert-profiles-second-20261106`; queue process checks the first batch terminal status. Do not report queued or skipped cases as successful captures.
- A third batch of 80 cases (mHC head compute mix forward, pre-apply mix forward, fn/normw merge forward, and partial-reduce/RMSNorm forward) is queued after the second batch. These adapters have offline checks only and will run one pilot per family. Remote directory: `/workspace/tilekernels-expert-profiles-third-20261106`.
- The other 737 planned cases do not yet have execution adapters in this repository. A plan row is not a launched job; implement and validate these adapters in subsequent batches.
- Held-out cases: the earlier `topk_gate` family was reserved for independent validation. Decide a replacement or retain the reserve before using those profiles to choose rules.

No claim of 1,000 successful profiles should be made until individual case status, correctness and target profile identity have been verified.

## Fourth batch started 2026-11-06

- The fourth manifest maps 40 additional original plan entries: Engram Sinkhorn finalize and mHC reduce/RMSNorm backward. Pilot runs are in progress on hidev; see the remote `progress.json` for authoritative state. The 50-million-element host memory guard records 4 large finalize entries as skipped pending a bounded-memory comparison. Skipped is not a completed profile.
- Across all four manifests, 303 plan rows have adapters; 697 plan rows still have no adapter. This is a plan mapping, not a count of accepted profiles.
- The first three batch results were verified and pushed to GitHub in commit `c1e86f7`. The fourth batch must be synced separately.

- The fifth manifest maps 20 additional mHC post forward entries, queued on hidev after the fourth batch. Seven over 50M residual elements are skipped pending a bounded-memory comparator. Five manifests now cover 323 original plan rows; 677 rows still lack adapters.

- The sixth manifest maps 20 additional mHC pre-split forward entries, queued after the fifth batch. Six manifests now map 343 original plan rows; 657 rows still lack adapters.
