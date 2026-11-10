# Application replay proof and queued work

`transpose-post-bwd-proof-20261110.tar.gz`, SHA256 `18811f8aa7c8c44833df8a13430c5a3f5267422bc1b75345151065edc4575fe6`, contains representative audit scripts, adversarial test results, original and fixed harness hashes, and the two representative audit outcomes. Raw collection data are preserved on hidev and archived separately; batch queue snapshots are pending. Bytes refer to requested AIV UB-to-GM transfers, not physical DRAM writes.

`mhc_pre_split_mixes_bwd-01` remains pending due to parser record loss and memoryCorruption. `presplit-fwd-01` has incomplete observed output stores despite zero parser-reported drops; identity was rechecked against the frozen case plan, historical input hashes and source. No completeness claim is made. The failed multilayer replay is preserved and the corrected adapter is queued for a new attempt.
