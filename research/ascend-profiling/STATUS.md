# Collection status

- Historical import: 140 selected original `OPPROF` directories and related metadata; verified through `MANIFEST.json` and the inventory. Historic profile status, hardware and warmup remain as recorded.
- Candidate plan: 50 task/mode groups, 20 planned cases each. Cases are not all implemented or validated on hidev; the total is not a count of compiled kernels.
- New `msprof op --aic-metrics=Default` collection: preparation in progress. Each completed batch must be recorded below with the exact success/failure and path.
- Held-out cases: the earlier `topk_gate` family was reserved for independent validation. Decide a replacement or retain the reserve before using those profiles to choose rules.

No claim of 1,000 successful profiles should be made until individual case status, correctness and target profile identity have been verified.
