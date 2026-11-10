set -Eeuo pipefail
echo __PRECISION_POST04_DEPLOY_04_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/precision-post04-wrapper.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/precision-post04-wrapper.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/precision-post04-wrapper.py
echo "aaaec89e834799748bd2264aef6e48e3fa3bf34fbf49b195efe1807137f931b6  /workspace/expert-profile-backfill-20261109-hidev/precision-post04-wrapper.py" | sha256sum -c -
echo __PRECISION_POST04_DEPLOY_04_END__
