# Private checkout verification, 2026-11-07

The two `a5` and `hidev` captures were completed before removal of the old official checkouts. Both used `starter:fused-01`, passed the recorded numerical check, and matched the archived input and generated-source hashes. Their raw data are retained unchanged. The host CANN versions differ: A5 used 9.2.0; hidev used 9.2.1.

After removal, `hidev-after-delete` passed the same complete capture. On A5, the same case prepared and passed its numerical check after removal, but two new profiler attempts on devices 7 and 1 stalled in the device task and were stopped. These attempts do not establish a successful post-removal profiler capture or the cause of the device wait. Earlier complete A5 evidence is in `a5/`.

The two `*-official-deletion.json` files record the exact deleted checkout paths, old and private commits, and deletion time. Private repository files were checked against the Git index independently on both hosts before deletion. Historical batch controllers retain original host assumptions; use the documented portable entry point for new captures.
