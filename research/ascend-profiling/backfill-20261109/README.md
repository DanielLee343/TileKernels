# Ascend expert profiling backfill — initial snapshot

This is an **incomplete, in-progress snapshot**. It contains the status ledger and
the first five hidev reduce captures, not all collected or planned raw profiles.
Later commits will add the remaining evidence and updated inventory.

- `initial-hidev/successful-reduce-01-05.tar.gz` preserves five separate
  MemoryDetail windows, associated logs, tool metadata, and provenance. Its
  SHA-256 is `07b54a4cd88d4171650ff98ac38118fa3cf9fe42e919bf3e4fda2431d144cf48`.
  All 217 regular-file members were compared with the extracted copies by
  size and SHA-256. `reduce-01-audit.json` records the first address audit.
- `initial-hidev/reduce-static-archive-bundle.tar.gz` contains all 20 completed
  hidev reduce case directories, including failures and separate attempts. The
  outer bundle SHA-256 is
  `4417a488db0206a5ed93827da3d7e640dd90aa585baa6f44ce59c02c0ad9d834`.
  Its inner manifest covers 908 files and 160 CSV copies. The inner archive was
  verified both on the capture host and after transfer. It includes the first
  five cases above; those files are intentionally retained in both snapshots.
- To verify the 20-case bundle, extract its outer tarball, then run
  `python tools/verify-archive.py expert-profile-backfill-20261109-reduce-static-archive`
  from this directory. The verifier also supports `--restore <new-directory>`.
- `initial-hidev/mhc-static-archive-bundle.tar.gz` snapshots the existing
  `mhc-runs/{second,third,fifth}` directories, including separate attempts and
  failures. Its SHA-256 is
  `21944c59034e819437cac98b62a5a895e19d12cd36c9a5bc8ea80b67a5e23a2d`.
  Its inner manifest covers 2,421 files and 400 CSV copies, verified on both
  hosts. This is the set present at snapshot time, not every planned mHC case.
- For either outer archive, `python tools/verify-outer-bundle.py <bundle> <sha256>`
  validates the outer hash and every inner file in a temporary directory.
- The following additional bundles snapshot the named capture directories,
  including failures and repeated attempts. Each has been scanned for private
  key/GitHub token markers and verified by its inner file manifest on both hosts.
  The bundle's presence does not imply that all planned cases passed:

  | Directory snapshot | SHA-256 |
  | --- | --- |
  | `fused-runs` | `5aef2ce49c48f95fdb4696bf88ba0dcadd8634197b8aaa163f5322093e2a7729` |
  | `topk-runs` | `b01128b296b994ee7cead3e01e601f12c8f534604988d580e0465664d6961445` |
  | `hash-runs` | `8e6fbab6e22c594054503a3876ffbf2c12733ba18179987d147f2e924f2ccd17` |
  | `classic-runs` | `e620a801e2369e4fefbc7c0d3232482d092e0fbd0c1a78e341fa7fe6613b10b6` |
  | `mega28-runs` | `88830966a7f7764a65c6065744dbb25c0eafba349ed794b3c75017f7048f240a` |
  | `unified-quant-runs` | `3ca536deba74666549cbea6ab6d9074cf35cea8636d9e0fe6a18a35efa72456e` |

  Each file is named `initial-hidev/<directory>-static-archive-bundle.tar.gz`.
  For example, the `hash-runs` snapshot contains 18 case directories, with
  incomplete captures kept as evidence. The `mega28-runs` data are the 28-Cube
  adapted implementation; address coverage is checked, but total traffic is
  not yet verified and some profiler replays failed.
- Two further point-in-time snapshots were taken while other case families
  continued collecting. They were scanned and verified on both hosts:

  | Directory snapshot | Files / CSV copies | SHA-256 |
  | --- | --- | --- |
  | `deepgemm-runs` | 1,769 / 312 | `ad56b6489e2fdeb6be7c85f0fb93ab366b99875ec5c7ac1622b3818b4f7a17fb` |
  | `extra-proxy-runs/unified-extra2` | 3,835 / 616 | `89e5c73c2b2a708f9264b4999c13448246f8590d7a9ce03b84ea77ce6d4b7ee6` |
  | `extra-proxy-runs/unified-extra` | 997 / 160 | `f67cea9861a4b21a20b987c5edcacdc37883620365aa9a3db7edff9208f78e4e` |
  | `extra-proxy-runs/unified-extra3` | 2,512 / 408 | `f7e09c37cadeec92f566308e4a1ee8abdba94046a8b290f0ef42e2a6e5058eb1` |
  | `extra-proxy-runs/unified-extra4` | 985 / 160 | `ef754afcce23bfe440b4608348eed3f4cd8275dc19b54e16d79113209ea48f6c` |
  | `extra-proxy-runs/unified-extra5` | 2,007 / 320 | `ae956fff4cb5dcd61e76adcf1a3e33532985300337603f24b942fc7ffd02bafc` |

  They are stored as `initial-hidev/<snapshot>-snapshot-archive-bundle.tar.gz`.
  The unified-extra5 snapshot includes mask tensors and input hashes for the
  Engram forward and backward captures. Additional cases and attempts collected
  afterward require a later snapshot.
- `initial-hidev/norm-backward-snapshot-archive-bundle.tar.gz` is a later
  snapshot of all 20 Norm backward case directories. It contains 1,210 raw
  files and 160 CSV copies, including the application-replay attempts. Its
  outer SHA-256 is
  `1801eae55c65da87e3a52fb4e357d94b5ea258f5908ba4fc92a85b942e5bc17b`.
  Its individual file hashes have been checked on both hosts. Application
  replay and earlier kernel-replay Default are distinct collection windows.
- `initial-hidev/mqa-completed-snapshot-archive-bundle.tar.gz` contains the
  18 ordinary and paged MQA case directories with 921 files and 160 CSV
  copies, including the measured bounds. Its outer SHA-256 is
  `272a65fe70a36fd1ce5ae0c9ca380ae0cf012bea0f1bdd52a2994e93bdacc486`.
  Its individual file hashes have been checked on both hosts.
- `initial-hidev/moe-backward-snapshot-archive-bundle.tar.gz` contains 20
  MoE backward case directories, 1,017 files and 160 CSV copies, including
  the initial failed and subsequent successful audit for case 02. Its SHA-256
  is `bc869c7262fc9f5cacb0f22896a3bdeec1a042ed572e35fd2b4a45bb6e6d90fd`.
  Its individual file hashes have been checked on both hosts.
- `initial-hidev/kgroup-sparse-randn-snapshot-archive-bundle.tar.gz` contains
  four K-group cases, eight non-paged sparse MQA cases and two randn attempts:
  633 files and 112 CSV copies. The randn attempts have dropped address records
  and remain unaudited. The SHA-256 is
  `4018ae8c52d8fe730a01a93f31b01f5a133917fed20a235e85353c388c89d1f0`.
  Its individual file hashes have been checked on both hosts.
- `initial-hidev/final-deepgemm-smokes-snapshot-archive-bundle.tar.gz` holds
  one large BF16 GEMM, four M=1 pilots and two paged-sparse attempts: 290 files
  and 48 CSV copies. The two paged-sparse attempts remain unaudited: the REUSE
  metadata identity differs from history; FIRST's required range replay is
  incompatible with MemoryDetail. Bundle SHA-256:
  `0e099cbefda01fc765364c350de31810794067fac87e10fca18c31d02fa8f136`.
  Its individual file hashes have been checked on both hosts.
- `initial-hidev/runner-version-evidence.tar.gz` records actual wrapper versions
  for several earlier captures where the per-attempt provenance copied the
  generic wrapper instead of the specialized wrapper. Its README maps groups
  and cases to the saved versions; `sha256.txt` verifies each saved wrapper.
  Bundle SHA-256:
  `c050d210a45cbb5913dd2da3728dfcf64239e66d4c7c90b2c654ff72528e8fff`.
- `initial-hidev/support-snapshot.tar.gz` contains 797 point-in-time replay
  scripts, harness and input manifests, and historical bindings; its file
  manifest is verified by `python tools/verify-support-snapshot.py <bundle>`.
  Bundle SHA-256:
  `50b16f559ed6d9cdb1455fd429c9617e6ed5f75f7b32dd15a8c12da870821e3a`.
  This is a snapshot of the collection environment, not a portable CANN or
  Python runtime, and later scripts require a subsequent snapshot.
- `initial-hidev/support-snapshot-v2.tar.gz` is a later snapshot with 864
  scripts, harness files and manifests, including the application-replay,
  random-number and paged-MQA harnesses. Verify individual file hashes with
  `python tools/verify-support-snapshot.py <bundle>`. Bundle SHA-256:
  `43ae8f300bc6b070969690dfbf93c70887076e5f797de70a7d46fb72613e2724`.
  It is not a portable CANN or Python runtime; scripts added after this
  snapshot require a later archive.
- `initial-hidev/support-snapshot-v3.tar.gz` contains 907 scripts, harness
  files and manifests, including the paged-MQA context-length harness. Its
  SHA-256 is `8beed55b2ea3b8d57c654bd6b44bd62f8247d2126a565e49b9fcaf790b4b9fc2`.
  Verify its contents using `python tools/verify-support-snapshot.py <bundle>`.
  It is a point-in-time support snapshot, not a portable CANN/Python runtime.
- `initial-hidev/support-snapshot-v4.tar.gz` contains 977 support files,
  including the K-group and sparse-MQA harnesses and the saved negative-test
  logs. Its SHA-256 is
  `7f36e9a603377fcda6b55b54be43f2f9f435bb58de4a47323e082ada37bf9a4d`.
  Verify it using `python tools/verify-support-snapshot.py <bundle>`.
  It is a point-in-time support snapshot, not a portable CANN/Python runtime.
- `initial-hidev/support-snapshot-v5.tar.gz` contains 1,034 support files,
  including additional audit tests and the paged-sparse harness. Its SHA-256
  is `91652d35fb92ef664053f788293afb0ab225345926bfd846b35666292a9c2dee`.
  Verify it using `python tools/verify-support-snapshot.py <bundle>`.
  It is a point-in-time support snapshot, not a portable CANN/Python runtime.
- `initial-hidev/support-snapshot-v6.tar.gz` contains 1,089 support files,
  including the normal and pilot GEMM harnesses and their negative-test logs.
  Its SHA-256 is
  `c09320a224661a0054c77db85c0cc7cb77b3f9f0cc437b7b68c284464320fbc6`.
  Verify it using `python tools/verify-support-snapshot.py <bundle>`.
  It is a point-in-time support snapshot, not a portable CANN/Python runtime.
- `initial-hidev/local-reproduction-snapshot.tar.gz` contains 948 local audit,
  preparation and verification scripts plus point-in-time progress documents.
  Its SHA-256 is
  `529903ec79648bdce633233c40520f99e766c54daee9c207f50306b2d675345e`.
  Verify it using `python tools/verify-local-reproduction.py <bundle>`. Paths
  refer to the original workspace and collection hosts; the data and runtime
  are separate, and subsequent scripts and progress require a later snapshot.
- `inventory/targets.csv` and `inventory/inventory-summary.json` are a point-in-time
  snapshot. Paths in the ledger refer to the collection workspaces; a ledger row
  does not mean its raw capture is included in this commit. Statuses distinguish
  audited, pending, and not-applicable cases. The accompanying capture indexes
  record per-file hashes and remote paths at the same inventory refresh; some
  indexed captures were created after the raw-archive snapshots above.
- The hidev 950PR reported alarm `8C4BA00C` during this collection. An earlier
  same-contract reduce-01 timing smoke was close to its prior reference; that
  check does not establish the validity of all other hardware measurements.
- The audited byte field is the requested AIV UB-to-GM transfer volume in the
  specific replay window. It is not a measurement of physical DRAM write traffic.

- `initial-hidev/support-snapshot-v7.tar.gz` contains 1,157 point-in-time support files, including application-replay harnesses for Engram gradient, Sinkhorn step and momentum, and paged sparse MQA. Capture windows are archived separately; the bundle does not contain the complete runtime. SHA-256: `6b006590da69f1b10d6a8150c89a439866065008c857c28b9a557fd0e666fae5`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

- `initial-hidev/support-snapshot-v9.tar.gz` contains 1,179 support files, including corrected application-replay Sinkhorn queue scripts and inspectors plus RoPE and cast-and-back adapters. The older v7 Sinkhorn queue targets and inspectors used the wrong `unified-extra` prefix; use the v2 scripts in v9 with the correct `unified-extra5` target. The queued captures were not yet completed at the snapshot. SHA-256: `006f51428b41b99c2b7b7feae7508dea828db4fd0fc9a7d252a253c08f261f25`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

- `initial-hidev/engram-grad-app-snapshot-archive-bundle.tar.gz` contains all 20 Engram gradient application-replay captures (1,516 files; 160 CSV copies). All 20 passed address and per-core requested-byte checks. The archive is independently verified on both hosts; SHA-256: `8f9997ad0006fc11aa39f78b36449452031e57833a7f33e3b0dd50ea62aa06a0`. Application replay is a separate observation window; it must not be combined with historical kernel-replay metrics as if they were the same run.

- `initial-hidev/representatives-v2-snapshot-archive-bundle.tar.gz` preserves eight finished or failed representative capture units (624 files, 72 CSV copies), including paged sparse FIRST, Sinkhorn step/momentum, RoPE Q, cast-and-back, and unsuccessful Normalize/MoE attempts. A captured process alone does not mean its counters passed validation; consult the ledger. SHA-256: `96b5ed463784190202b58bcb879ab2d1311b39ca2db1de28223d158b727e435a`.

- `initial-hidev/support-snapshot-v10.tar.gz` contains 1,210 point-in-time support files, including the current application replay queues, source-aware audits, and negative-test logs. SHA-256: `117612956039cba1df7b14369ea15a4a3facebbc118ecf4d6b4eaec17bd33701`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

The refreshed inventory is a point-in-time ledger. Do not treat an inventory entry alone as proof that a later capture window has already been published; check the listed archive and snapshot time.

- `initial-hidev/support-snapshot-v11.tar.gz` contains 1,224 point-in-time support files, adding mHC fn/normw backward replay preparation and automated batch-archive watchers. The mHC smoke and its draft audit were queued, not validated, at snapshot time. SHA-256: `30a4c389d164cfba8595306f8212435fee4da46f9d900eb1ecc920b6d49c3fd0`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

- `initial-hidev/support-snapshot-v12.tar.gz` contains 1,252 point-in-time support files, adding queued batched-transpose, mHC post backward and mHC pre-split backward replay adapters and their identity checks. Those smokes had not run at snapshot time. SHA-256: `93cac5d2c35e5280b8c7147ba0618ed15c607405017550d9605c7b468bde44b2`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

- `initial-hidev/support-snapshot-v13.tar.gz` contains 1,280 point-in-time support files, adding mHC big-fuse, multilayer and pre-apply backward replay adapters and identity checks. These representative smokes were queued and not validated at snapshot time. SHA-256: `92ee0f2790726314076120bc0f28e780bb02e3176df928e85c41fe7c5f427951`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

- `initial-hidev/step-queue-snapshot-archive-bundle.tar.gz` contains the completed Sinkhorn step application-replay batch: 20 cases, 1,516 files and 160 CSV copies, each verified at source and destination. SHA-256: `a7e18edaacac5f6d12d96c466300e7877b46baa1ba826dd86e13f1828e66aac5`. This application-replay window is distinct from historical Default.

- `initial-hidev/paged-first-queue-snapshot-archive-bundle.tar.gz` contains four FIRST paged sparse application-replay cases (FP8 and FP4), including compact workspace and logits audits: 512 files and 32 CSV copies verified at source and destination. SHA-256: `45f496f1ce13129f73b34070183dd6bcfffdd893b9ea4731bf2b5a8e62ea1d6f`. The later three cases and their negative-test logs are indexed in `inventory/deepgemm-paged-first-queue-index.json` and support snapshot v14.

- `initial-hidev/momentum-reaudit-snapshot-archive-bundle.tar.gz` preserves momentum cases 01 and 02, including case 02 original audit failure and its separate successful re-audit: 153 files, 16 CSV copies. SHA-256: `582bd80c2359127525fd500916a6be6d2e240351f153e22cc8aade6fe61d61fc`.

- `initial-hidev/support-snapshot-v14.tar.gz` contains 1,309 point-in-time support files, including per-case paged FIRST negative-test logs and the momentum large-tensor re-audit evidence. The pre-split forward application-replay probe is queued and not yet validated. SHA-256: `7ebf5f0072eb13eb2c1c68e3a5d5753872f3756daa5fc2af85cf0a9489dbd3a5`. Verify with `python tools/verify-support-snapshot.py <bundle>`.

- `initial-hidev/support-snapshot-v15.tar.gz` contains 1,323 point-in-time support files, including the REUSE metadata timing comparison logs and an instrumented frozen-collector reconstruction queued to capture prewarm, post-warmup, and post-target metadata. The reconstruction had not run at snapshot time, and the eight historical REUSE cases remain pending. SHA-256: `0c026828d71515439aba877dbf8163495b8d20b5a6bfa964dbaeab5541569a90`. Verify with `python tools/verify-support-snapshot.py <bundle>`.
