# Parser-health replay probes

These are queued experiments, not completed audits. Fixed-input randn, normalize and MoE forward cases previously had parser loss under kernel replay; the queued application-mode probes retain per-process metadata and compare source and initial input. Parser metrics alone cannot establish complete dynamic address coverage. `parser-probe-harnesses-20261110-v2.tar.gz` was verified against 27 per-file SHA256 checks; archive SHA256 `de28fd97a909cceb862b82022bddbfbb52faf7ca4ab6d58961fafac5051c3ca1`.

Pre-split forward currently has three static output-store PCs but only one appears in recorded events, with five records despite parser reported zero drops. Its repeat is queued and no completeness assertion is made.
