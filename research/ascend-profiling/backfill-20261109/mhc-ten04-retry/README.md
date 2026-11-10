# mHC 10-layer case 04 failed replay and retry

The application-replay capture command returned zero, but identity inspection correctly rejected the run: 2 of 9 application processes failed before the kernel call while allocating pinned host memory with ACL error 207001; 7 completed. The exact cause is not established. At a later check, the container reported about 677 GiB host memory available and a 64 MiB locked-memory limit; those observations do not prove which limit caused the failure. The failed run remains pending.

The original bundle contains the passed case 02 and failed case 04, 252 files and 16 CSV copies, independently verified on hidev and workstation; SHA256 `bb650b0b7f0404d45e27c379d8a7f513ea0f92be338f8830bb56f6e87b7266f2`. An exact-method retry is queued after independent existing tasks, without changing memory limits or case parameters. The remaining 10-layer/10-post batch starts only if the retry passes all checks.

The unchanged-method retry (attempt 002) subsequently passed identity checks in all nine processes and the output/byte audit, with 1,887,436,800 requested UB-to-GM bytes. Its bundle retains both attempts: 254 files and 16 CSV copies verified on both machines, SHA256 `0497c92fbb9bfc004e0730bd1bd83f962f08493e30d1a8819b2e1670b6da14fd`. The retry passing does not establish why the first host allocation failed.
