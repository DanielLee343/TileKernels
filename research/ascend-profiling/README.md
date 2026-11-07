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

The starter batch can be synchronized from this workstation's existing authenticated hidev tmux pane:

```powershell
python -B research/ascend-profiling/sync_hidev.py --push
```

Add `--watch` to synchronize again as completed cases appear until that batch finishes. This transport currently requires the existing `D:/puma_v2` helper, WSL `archlinux`, and tmux pane `0:0.0`. `--push` checks that `main` matches the remote and the Git index is clean before committing only the starter run directory; it stops on a conflict. This is a workstation-specific transfer helper, while the committed files are portable.

For the queued second or third batch, add `--batch second` or `--batch third`; use `verify_run.py --batch second` or `--batch third` to verify its downloaded snapshot. Do not run simultaneous pushes from multiple sync processes; let each preceding batch's sync finish first.

## Working across machines

Clone this private repository and `git pull` the branch containing the work. Historical paths inside captured logs describe their original machines and are not portable commands. The batch controllers under `collector/` are archived historical tools; their preflight paths and platform assumptions are not portable.

For a new capture, activate the host's TileLang environment and use the portable single-case entry point. On A5 use `/data2/lyuze/tilekernels-env-20261107/activate.sh`; on hidev use `/workspace/tilekernels-env-20261101/activate.sh`. The repository whose copy of the script is invoked supplies the source and manifests.

```bash
python research/ascend-profiling/portable_profile.py list
python research/ascend-profiling/portable_profile.py run starter:fused-01 --device 0 --output /absolute/path/to/new-output
```

Each run requires an idle selected device and a new output directory. It records preparation and collection logs, numerical-check status, raw profiler files and comparison with archived input and generated-source hashes where available. `--allow-precision-failure` collects explicitly recorded numerical mismatches only; the recorded accuracy status remains failed. A successful smoke test covers the tested case and environment; it does not establish that all 1,000 planned cases run on every host.

The A5 activation file explicitly sets `BISHENG_HOME` to the activated CANN 9.2 installation and prepends the local GCC 15 C++ include paths. This prevents the shell's old CANN 9.1 compiler and GCC 10 headers from being selected. The two host smoke captures and their raw data are stored in `smoke-evidence/20261107/`; they use the same case but different CANN versions, so their measured performance must not be treated as directly interchangeable.

## Current limitations

The 1,000-case plan is a proposal; some choices are extensions of upstream tests and require compilation and correctness checks on the target device. Some historical records use different warmup, device or CANN conditions and must not be mixed without checking. A 20-case target does not imply complete coverage. The first 140 captures are not 140 independent cases. Existing customer-facing thresholds remain under investigation.
