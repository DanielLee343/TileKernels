#!/usr/bin/env bash
set -u
cd /workspace/deepgemm-ascend-20261107
source ./activate.sh
export ASCEND_HOME_PATH=/workspace/deepgemm-ascend-20261107/cann-compat-quant
export BISHENG_HOME="$ASCEND_HOME_PATH"
export DG_JIT_CACHE_DIR=/workspace/deepgemm-ascend-20261107/campaign-cache/paged-sparse-first-1-q4-k256-h8-b8-p64
case_id=paged-sparse-first-1-q4-k256-h8-b8-p64
mkdir campaign-first-diagnostics
for entry in kernel5 kernel0 application5; do
    case "$entry" in
        kernel5) mode=kernel; warm=5 ;;
        kernel0) mode=kernel; warm=0 ;;
        application5) mode=application; warm=5 ;;
    esac
    mkdir "campaign-first-diagnostics/$entry"
    npu-smi info -t proc-mem -i 0 > "campaign-first-diagnostics/$entry/device-before.txt"
    if ! grep -Fq 'No process in device.' "campaign-first-diagnostics/$entry/device-before.txt"; then
        echo DEVICE_BUSY >> "campaign-first-diagnostics/$entry/result.txt"
        break
    fi
    msprof op --aic-metrics=Default --replay-mode="$mode" --warm-up="$warm" \
        --mstx=true --mstx-include=dg_campaign_target --kernel-name='*paged_sparse_mqa_logits_impl*' \
        --launch-count=1 --output="campaign-first-diagnostics/$entry/profile" \
        python -B campaign-13/diagnose_first.py __worker "$case_id" profile \
        "/workspace/deepgemm-ascend-20261107/campaign-first-diagnostics/$entry/profile.json" \
        /workspace/deepgemm-ascend-20261107/source > "campaign-first-diagnostics/$entry/profile.log" 2>&1
    rc=$?
    npu-smi info -t proc-mem -i 0 > "campaign-first-diagnostics/$entry/device-after.txt"
    printf 'msprof_rc=%s\napp_json=%s\n' "$rc" \
        "$(test -f "campaign-first-diagnostics/$entry/profile.json" && echo present || echo missing)" > "campaign-first-diagnostics/$entry/result.txt"
    cat "campaign-first-diagnostics/$entry/result.txt"
done
