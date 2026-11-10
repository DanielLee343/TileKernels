# Hash application replay comparison

The first inspection failed because it assumed the historical metadata contained a case field. The corrected inspection matched the new process case to the frozen case plan and matched historical inputs and source. All nine application processes passed identity and correctness checks. The parser still reported `droppedRecord=20`; the historical kernel replay for the same case reported 9 drops. Neither is complete and the case remains pending.

The raw snapshot was independently verified on server and workstation: 58 files, 8 CSVs; SHA256 `ea067e90a529044ef07072613387f13cb4fb8e53302637fee1fe3bb035ef5a10`. The snapshot was created before corrected inspection; that inspection and its script are preserved alongside it.
