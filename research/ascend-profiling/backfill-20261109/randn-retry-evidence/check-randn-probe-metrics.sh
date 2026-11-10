echo __RANDN_METRICS_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
for a in "$r"/extra-proxy-runs/unified-extra2/randn-04/hidev-npu0/attempt-*/detail/profile.log;do test -f "$a" || continue;echo "$a";grep 'processedRecord:' "$a" | tail -n 1;done
echo __RANDN_METRICS_END__
