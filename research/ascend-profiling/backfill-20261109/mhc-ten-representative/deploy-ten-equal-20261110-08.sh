set -Eeuo pipefail
echo __TEN_EQUAL_DEPLOY_08_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/snapshot-mhc-ten-equal-v1.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/snapshot-mhc-ten-equal-v1.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/snapshot-mhc-ten-equal-v1.py
echo "97a8801da1da72e3e6b29d98e68f713d3f302dc92037462b2049386fcd0b459a  /workspace/expert-profile-backfill-20261109-hidev/snapshot-mhc-ten-equal-v1.py" | sha256sum -c -
echo __TEN_EQUAL_DEPLOY_08_END__
