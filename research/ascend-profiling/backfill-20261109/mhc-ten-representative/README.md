# mHC recompute ten-layer representative

Case 02 has 10 layers and 10 post layers. All nine application replay processes matched the historical input and source. All 20 output buffers were checked, with 1,048,576,000 requested UB-to-GM bytes matching output coverage and same-window per-core CSV. Negative tests remove one output record from each of the first/last layer for both output classes, duplicate one record, change a CSV total and alter a pointer table. The tests reject all modifications. This is requested traffic, not physical DRAM bytes.

The 136-file, 8-CSV bundle contains the capture and post-audit result and was verified on hidev and workstation. SHA256 `417d40299cde6b51932bd180e0307f2ecee1c77f32fb8ee72abe4d33fa266929`. The six other fixed-plan 10/10 cases are queued with this audit, after the post-backward queue; each must pass separately. 10/9 and 3-layer cases require separate validation. Unique deployment paths refuse overwrites.
