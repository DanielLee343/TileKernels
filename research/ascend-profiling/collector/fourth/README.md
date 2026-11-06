# Fourth batch: pending on-device validation

40 original plan entries: 20 Engram Sinkhorn finalize and 20 mHC reduce/RMSNorm backward. Each family starts with an on-device pilot. Finalize follows upstream full-output tolerance; RMSNorm backward follows the upstream normalized squared-error tolerance. Finalize entries above 50 million matrix elements are recorded as skipped pending a bounded-memory comparator; this is a safety guard, not evidence of invalidity.
