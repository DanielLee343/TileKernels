# Early RoPE Q independent replay

The new Q application replay matched historical inputs and generated source across nine processes and passed the post-replay reference. For this standalone window, output coverage, per-core requested UB-to-GM bytes (128 B) and same-window CSV agree. Negative tests rejected a missing output record, a duplicate record, a wrong CSV and an input/output alias. It is an application-replay observation, not a physical DRAM byte count.

The historical profiler had call IDs 0 and 1 but available evidence does not establish their Q/K mapping. Therefore neither historical call is promoted. The initial candidate incorrectly used call-0 as its target and is preserved as `early-rope-q-unverified-call-mapping.json` for the audit trail; the corrected independently scoped result is `early-rope-q-independent-audit.json`.

The earlier failed attempt and the new capture were archived before the standalone audit: 149 files, 16 CSV, independently verified on hidev and workstation, SHA256 `7497d0fc38b23b3368fdab8f927339a94c5af9ae60f7f6799c0e2832a7abc576`. The audit JSON and disassembly were saved separately after this archive was created.
