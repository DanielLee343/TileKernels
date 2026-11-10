# Precision-labelled post backward case 04 replay smoke

This is a queued investigation, not an accuracy-passing sample. The historical `capture-record.json` includes input and source hashes and records a failed CPU reference. The original review separately records a passing NPU chunked reference; the two results are retained as distinct evidence. The scripts replay the exact planned parameters, preserve assertion mismatches as explicit reference failures in each process, require input/source hashes to match the historical record, and observe requested UB-to-GM bytes. Unexpected exceptions still propagate. Historical Default and the new application-replay window remain separate; they were collected on distinct device identities.

The smoke is queued after the three mHC variant smokes. Its byte result, if any, is marked `precision_labelled_bytes_observed` and is not promoted as an accuracy-passing expert audit. The unique deployment files reject pre-existing targets and hash-check payloads. This script set assumes the pinned hidev environment and existing adapter.

## Same-input replay observation

Nine application processes matched historical input and source identity; all nine CPU reference checks failed. Four output intervals and 587,857,920 requested UB-to-GM bytes were observed and checked against per-core CSV; negative tests rejected missing writes, duplicate writes, wrong CSV and output alias. This is a byte observation, not an accuracy pass; the original precision-failed status remains. Historical 57:00 and current 8B:00 devices and replay windows remain separate. Archive: 88 files / 8 CSV; SHA256 `40fd97f97573aa5353f0a20225a61fd6d81fbd1c72ffd302cc033bcc65939722`. Negative test logs in `../mhc-three-equal-ten-nine/mhc-variant-negative-tests-20261110.tar.gz`.
