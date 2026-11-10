# MoE top-k forward case 01 application replay probe

Nine application replay processes passed the input/source identity check. The parser reported 3,462 dropped records and `memoryCorruption=10` (a parser record-header mismatch counter; not evidence of hardware memory damage) in the retry. The two earlier captures reported 3,607/14 and 3,384/9 respectively. The diagnostic exit status only means the probe completed; the case remains pending and no complete byte audit is claimed.

All three attempts are included: 161 files and 24 CSV copies, independently verified on hidev and workstation; SHA256 `7bb384125d75c16a6854334a6022e06c8b2b4595f12c035801c4150b12643e84`.
