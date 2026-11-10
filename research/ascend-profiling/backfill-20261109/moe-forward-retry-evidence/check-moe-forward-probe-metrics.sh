echo __MOE_FORWARD_METRICS_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
for a in "$r"/extra-proxy-runs/unified-extra3/moe_topk_gate_forward-01/hidev-npu0/attempt-*/detail/profile.log;do test -f "$a" || continue;echo "$a";grep 'processedRecord:' "$a" | tail -n 1;done
echo __MOE_FORWARD_METRICS_END__
