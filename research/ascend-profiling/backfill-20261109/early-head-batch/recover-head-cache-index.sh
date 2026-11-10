echo __HEAD_RECOVERY_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;d="$r/early-head-batch-runs-20261111/head-fp32-1001/hidev-npu0/attempt-001/detail";cache="$r/early-head-batch-cache-20261111/head-fp32-1001"
test -d "$cache";test ! -e "$d/cache-sha256.txt";find "$cache" -type f -exec sha256sum {} + | sort > "$d/cache-sha256.txt"
bin=$(find "$d/capture" -name aicore_binary.o -print -quit);test -n "$bin";sha256sum "$bin";grep 'kernel.aibin$' "$d/cache-sha256.txt" || true
find "$cache" -name device_kernel.asc -print | head -n 10
echo __HEAD_RECOVERY_END__
