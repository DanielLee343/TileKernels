# Second hidev batch (pending pilot)

123 selected plan rows: 20 topk gate, 20 Engram Sinkhorn partial-reduce, 20 mHC Sinkhorn forward, 20 mHC Sinkhorn backward, 20 mHC expand forward, 20 mHC expand backward, and 3 compatible FP8 per-token cast-back cases. These are not yet device-validated. The other 17 cast-back cases use different formats/layouts and require a separate adapter.

The first 60-case batch must reach its terminal state before this batch starts. Each family has one pilot; the collector only continues a family after its pilot passes. The collector permits a variable vector block dimension because partial-reduce selects fewer than 56 blocks. Full output is checked with exact equality for topk, expand forward and cast-back; explicit tolerances are recorded in the collector for Sinkhorn and expand backward.

These topk cases include a former holdout family; keep them isolated from threshold selection if using them as blind test data.
