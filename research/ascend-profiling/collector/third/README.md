# Third hidev batch (pending pilot)

80 candidate cases: 20 each for mHC head compute mix forward, pre-apply mix forward, fn/normw merge forward and partial reduce/RMSNorm forward. These adapters use full-output CPU PyTorch references and per-family pilots. They have not yet been validated on hidev. The batch is serially queued after the second batch; pilot failures skip the relevant family.

The test tolerances for head and pre-apply follow the source tests; the partial-reduce reference uses the source test tolerance. Cross-run identity checks and the raw Default capture are retained.
