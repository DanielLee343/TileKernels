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
- `inventory/targets.csv` and `inventory/inventory-summary.json` are a point-in-time
  snapshot. Paths in the ledger refer to the collection workspaces; a ledger row
  does not mean its raw capture is included in this commit. Statuses distinguish
  audited, pending, and not-applicable cases.
- The hidev 950PR reported alarm `8C4BA00C` during this collection. An earlier
  same-contract reduce-01 timing smoke was close to its prior reference; that
  check does not establish the validity of all other hardware measurements.
- The audited byte field is the requested AIV UB-to-GM transfer volume in the
  specific replay window. It is not a measurement of physical DRAM write traffic.
