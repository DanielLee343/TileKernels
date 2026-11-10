echo __HEAD_SOURCE_BIND_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;d="$r/early-head-batch-runs-20261111/head-fp32-1001/hidev-npu0/attempt-001/detail";cache="$r/early-head-batch-cache-20261111/head-fp32-1001"
find "$cache" -name device_kernel.asc -exec sha256sum {} +
find "$d" -maxdepth 1 -name 'generated-kernel-*.cpp' -exec sha256sum {} + | head -n 2
python3 -B "$r/audit-early-head-batch-20261111.py" head-fp32-1001 attempt-001
echo __HEAD_SOURCE_BIND_END__
