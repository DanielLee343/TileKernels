set -Eeuo pipefail
echo __TEN_EQUAL_DEPLOY_06_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/queue-mhc-multilayer-ten-equal.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/queue-mhc-multilayer-ten-equal.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/queue-mhc-multilayer-ten-equal.py
echo "2ba9f76d7eb6615f652bb5d1257e3771cbd8616e3da5de99997f40f437b611fc  /workspace/expert-profile-backfill-20261109-hidev/queue-mhc-multilayer-ten-equal.py" | sha256sum -c -
echo __TEN_EQUAL_DEPLOY_06_END__
