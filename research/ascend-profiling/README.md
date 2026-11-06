# Ascend TileKernels profiling

This directory holds our profiling work and case plans, separate from the upstream TileKernels implementation. The source baseline is commit `c1cf914a82e6901c679445f872051ce44ac2cc63`.

- [Candidate case plan](history/puma/outputs/tilekernels-profile-case-plan-20261106/README.md): 50 task/mode groups and 1,000 proposed cases. These are not 1,000 verified distinct compiled kernels or completed measurements.
- [Historical inventory](history/puma/outputs/tilekernels-profile-inventory-reset-20261105/README.md): 11 families, 97 different task definitions and 140 selected Default captures. Its JSON paths resolve relative to `history/puma/`.
- [Research progress snapshot](history/puma/docs/专家规则体系-证据与建模TODO-20261105.md): historical research record; some original links point outside this partial snapshot. It is not a completed customer rule set.
- [MemoryDetail investigation](history/puma/outputs/hidev-memorydetail-20261106/ROOT-CAUSE.md): current evidence and limitations.
- [Collection status](STATUS.md): new runs and outstanding work.

## Evidence policy

The historical snapshot includes all files under the 140 selected original `OPPROF` directories, including binary records and CSVs, and selected associated metadata and generated source. It is approximately 29 MiB before Git compression. `history/puma/MANIFEST.json` records path, size and SHA-256; run `python research/ascend-profiling/verify_history.py` from any current directory to verify them and all inventory references. Files preserve their original bytes through `.gitattributes`.

The snapshot is curated, not a copy of every past experiment. Larger non-selected A5/control archives and unrelated customer profiling are not included. Some older reports reference material outside the snapshot; missing referenced files do not imply the experiment did not happen. Do not silently represent missing evidence as present.

Future runs should store their source commit, device/CANN/profiler, complete case parameters, command, correctness result, raw profile directory, status and hashes together. Do not commit credentials, private SSH keys, customer data, transient build caches or large opaque archives by default. Before omitting any large raw file, record its size, SHA-256 and recoverable storage location.

## Working across machines

Clone this private repository and `git pull` the branch containing the work. The A5 host uses an existing GitHub SSH key and port 443. The hidev execution environment is currently separate from this checkout; bind the exact code commit and record where full results were written. Historical paths inside captured logs describe their original machines and are not portable commands.

## Current limitations

The 1,000-case plan is a proposal; some choices are extensions of upstream tests and require compilation and correctness checks on the target device. Some historical records use different warmup, device or CANN conditions and must not be mixed without checking. A 20-case target does not imply complete coverage. The first 140 captures are not 140 independent cases. Existing customer-facing thresholds remain under investigation.
