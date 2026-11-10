# Variant retry evidence and queued repairs

The original 10-layer/9-post case 03 had one of nine application replay processes fail pinned-host allocation (ACL 207001); it remains unverified. Its 123-file, 8-CSV bundle was verified on hidev and workstation, SHA256 `3cd1966d1a6bb13bd95d9fed8bb0e67bebb16d2a4e30f4dd6c0d038ce8013b56`.

The original 3-layer/3-post case 10 was stopped when guard v6 could not recognize a device process query. The 91-file bundle has no CSV and was verified on both machines, SHA256 `89b8018f7e868a66135d1a1eb2d018cb404ee5b2f67c23d9b720f91cebfdfbd2`. It is queued for retry using the previously tested guard v7, which still fails closed on unrecognized device state.

The first precision-labelled post 04 smoke failed before kernel execution because the deployed shell script had CRLF line endings. Its three-file evidence bundle was verified on both machines, SHA256 `0abcacaaf89cc9f9ee8faaee3cdabc31bebf2105a47757412048c30c36eb4dbe`. The replacement has LF line endings and passed `bash -n`; retry retains the historical CPU reference failure and uses guard v7. All retries are queued sequentially and their results are not implied by their presence here.
