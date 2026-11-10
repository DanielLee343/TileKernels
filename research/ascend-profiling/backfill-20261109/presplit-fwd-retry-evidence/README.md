# Pre-split forward repeat capture

For case 01 (`n=1001`), the checked generated code requires three output stores per 64-element tile, i.e. 48 stores. The first application replay captured 5 stores; this retry captured 14, with 12 at PC `0x3f4` and 2 at `0x400`, while the third expected store PC was absent. The retry parser reported `droppedRecord=0` and `memoryCorruption=0`; that does not establish completeness. The causal stage of the missing records is not established. No byte audit is promoted.

The archive preserves all three attempts, 173 files and 24 CSV copies; verified on hidev and workstation. SHA256 `873a5a2b48d620c958d9c0fa0b3e1187dafa3d5a3138acb2be39ea20e17b6c74`.
