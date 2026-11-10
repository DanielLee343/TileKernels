set -Eeuo pipefail
echo __PRECISION_POST04_DEPLOY_15_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/snapshot-precision-post04-smoke.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/snapshot-precision-post04-smoke.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/snapshot-precision-post04-smoke.py
echo "4e3bd63a9fff418094bafb137200c5cd2acb1bbf424fbf40073a692f71e9eb30  /workspace/expert-profile-backfill-20261109-hidev/snapshot-precision-post04-smoke.py" | sha256sum -c -
echo __PRECISION_POST04_DEPLOY_15_END__
