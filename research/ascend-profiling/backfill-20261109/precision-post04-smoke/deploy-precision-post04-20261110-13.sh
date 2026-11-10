set -Eeuo pipefail
echo __PRECISION_POST04_DEPLOY_13_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/audit-precision-post04-bytes.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/audit-precision-post04-bytes.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/audit-precision-post04-bytes.py
echo "52093ba163e19abd40529b09ed00a75138165177083c9885d2fc7293ef0f3983  /workspace/expert-profile-backfill-20261109-hidev/audit-precision-post04-bytes.py" | sha256sum -c -
echo __PRECISION_POST04_DEPLOY_13_END__
