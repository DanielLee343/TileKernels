# Paged sparse REUSE independent replay investigation

The new application replay recorded nine processes. Each matched the historical recorded pre-warm metadata and JIT source. All new post-warm metadata hashes agree with each other, but differ from a separate earlier REUSE window. The mapping, ranges, physical indices, 28 active descriptors, 37,888 active data bytes and 1,184 active scale bytes match that separate window; 64,959 bytes in the full compact region differ.

In the new window, 52 output events total 1,024 requested UB-to-GM bytes; output ranges and same-window CSV agree. Negative tests rejected missing/duplicate events, wrong CSV, parser errors and output/metadata alias. This is an independent observation. Historical target-time post-warm metadata was not recorded, so the original case and all eight REUSE cases remain pending. Requested bytes are not physical DRAM writes.

The raw bundle includes the earlier and current attempts before these later analysis files were generated: 229 files, 24 CSV copies, independently verified on hidev and workstation; SHA256 `a8d015252195418656ba9306fa08590a93a9a2b7b4078e4cb390fcb657045c36`. Analysis JSON and comparison log are saved separately.
