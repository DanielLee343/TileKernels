set -Eeuo pipefail
echo __PRECISION_POST04_DEPLOY_07_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/run-precision-post04-app.sh
base64 -d /workspace/expert-profile-backfill-20261109-hidev/run-precision-post04-app.sh.b64 > /workspace/expert-profile-backfill-20261109-hidev/run-precision-post04-app.sh
echo "4672578c87c653d37690d4c9e36ccd069de6f0378ef81a8e1ca059b31ea0c0ee  /workspace/expert-profile-backfill-20261109-hidev/run-precision-post04-app.sh" | sha256sum -c -
echo __PRECISION_POST04_DEPLOY_07_END__
