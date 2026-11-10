# Frozen paged sparse REUSE reproduction

The original collector order was reproduced on hidev with per-process snapshots before warmup, after five warmups, and after the target. Nine application processes passed correctness, matched the historical prewarm input hash and JIT source, and had identical post-warmup metadata hashes. The old experiment did not record its own post-warmup snapshot.

The new post-warmup snapshot differs in full SHA256 from the later independent REUSE capture, but mapping, ranges, physical indices, 28 active descriptors, 37,888 active data bytes, and 1,184 active scale bytes match; 115,856 bytes differ in the overall compact region. The source-documented scale transpose was used in the comparison. This is not proof of the unrecorded original post-warmup state. The byte audit remains pending. A further run that records per-process input and output addresses is queued; it has not run.

The raw archive was independently verified on server and workstation: 132 files and 16 CSVs; archive SHA256 `5561df6382f3dc93e32576ae54ff18451f651804627e618d06e8580995d9c5d0`.

A separate existing REUSE window had 52 observed UB-to-GM store events, 1,024 requested bytes, matching the expected output ranges and CSV. This is an exploratory offline check; negative tests, complete parser gates and the historical post-warm state remain unresolved, so it is not promoted.
