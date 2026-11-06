# Collection status

- Historical import: 140 selected original `OPPROF` directories and related metadata; verified through `MANIFEST.json` and the inventory. Historic profile status, hardware and warmup remain as recorded.
- Candidate plan: 50 task/mode groups, 20 planned cases each. Cases are not all implemented or validated on hidev; the total is not a count of compiled kernels.
- New `msprof op --aic-metrics=Default` collection: first 60 cases mapped across `engram_fused_weight`, `engram_hash`, and `moe_normalize_weight`. Pilot results `fused-01`, `hash-01`, and `normalize-01` were admitted; the remaining 57 are running serially on hidev. At launch the host recorded physical PCI `0000:57:00.0`, CANN 9.2.1 and msopprof build `884ac969494a186a9c63ac45c4c39ad7289b3215`. Remote working directory: `/workspace/tilekernels-expert-profiles-20261106`. These results have not yet been copied into Git; inspect the live `progress.json` for newer status.
- The other 940 planned cases do not yet have execution adapters in this repository. A plan row is not a launched job; implement and validate these adapters and queue them after the first batch.
- Held-out cases: the earlier `topk_gate` family was reserved for independent validation. Decide a replacement or retain the reserve before using those profiles to choose rules.

No claim of 1,000 successful profiles should be made until individual case status, correctness and target profile identity have been verified.
