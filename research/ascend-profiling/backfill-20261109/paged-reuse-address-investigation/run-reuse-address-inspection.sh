echo __REUSE_ADDR_INSPECT_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev
source /workspace/tilekernels-env-20261101/activate.sh
python -B "$r/inspect-paged-reuse-address-app.py" paged-sparse-fp8-q4-k256-h8-b8 attempt-003
echo __REUSE_ADDR_INSPECT_END__
