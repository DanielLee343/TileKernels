# Early RoPE Q replay probe

The first attempt captured data but all nine application processes failed the correctness check because the archived harness omitted `frozen/vendor/cann_refs/rope.py`; case descriptors and input hashes matched the earlier data. The failure is preserved and not counted as passed. Its raw archive was verified on both machines: 74 files, 8 CSVs, SHA256 `e4b4ea5eb5d23015cacbbb84949bfee76cd1143b99a349d08dad476449abc765`.

The corrected harness restores the original frozen CANN CPU reference and its license; its file SHA256 `1ca6534ef87e89bdbee87844866188e3d1bbb1fcd338e8ada7c0cdc4d7162f7a` matches the original source lock. No kernel or input was changed. `early-rope-v2-deploy.tar.gz` SHA256 is `d2275df718fe1db021468a9d4544f74f722351b9c8ba109ee39d61f4e74b838a`; all 13 harness files were byte-verified against the local copy. The retry is queued, not yet validated.
