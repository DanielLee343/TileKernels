# mHC three-layer / two-post representative

Case 09 passed input/source identity across nine application processes. Its three layer-input and two residual output buffers were each checked for complete nonoverlapping writes; 461,373,440 requested UB-to-GM bytes match the output intervals and per-core CSV. Negative tests separately removed a write from each of the five outputs, duplicated a write, changed a CSV total and altered a pointer table; all were rejected. These are requested bytes, not physical DRAM bytes.

The snapshot includes 136 files and 8 CSV copies; independently verified on hidev and workstation. SHA256 `ec605ccdf271791ae929ca97793263f487208c9c7a31c691ec644340eced2dda`. This covers case 09 only; 10/9 and 3/3 configurations require separate observations.
