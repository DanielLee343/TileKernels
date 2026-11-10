set -Eeuo pipefail
echo __PRECISION_POST04_DEPLOY_02_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/precision-post04-cases.json
base64 -d /workspace/expert-profile-backfill-20261109-hidev/precision-post04-cases.json.b64 > /workspace/expert-profile-backfill-20261109-hidev/precision-post04-cases.json
echo "bbfc28e7fbbe26016e257e34a19cbaa9b5979493a29acda3cded3b77677b7641  /workspace/expert-profile-backfill-20261109-hidev/precision-post04-cases.json" | sha256sum -c -
echo __PRECISION_POST04_DEPLOY_02_END__
