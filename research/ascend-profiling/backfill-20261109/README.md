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

  They are stored as `initial-hidev/<snapshot>-snapshot-archive-bundle.tar.gz`.
  Additional cases and attempts collected afterward require a later snapshot.
- `initial-hidev/runner-version-evidence.tar.gz` records actual wrapper versions
  for several earlier captures where the per-attempt provenance copied the
  generic wrapper instead of the specialized wrapper. Its README maps groups
  and cases to the saved versions; `sha256.txt` verifies each saved wrapper.
  Bundle SHA-256:
  `c050d210a45cbb5913dd2da3728dfcf64239e66d4c7c90b2c654ff72528e8fff`.
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
