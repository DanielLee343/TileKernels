echo __NORMALIZE_PROBE_METRICS_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
for a in "$r"/classic-runs/starter/normalize-04/hidev-npu0/attempt-*/detail/profile.log;do test -f "$a" || continue;echo "$a";grep 'processedRecord:' "$a" | tail -n 1;done
echo __NORMALIZE_PROBE_METRICS_END__
