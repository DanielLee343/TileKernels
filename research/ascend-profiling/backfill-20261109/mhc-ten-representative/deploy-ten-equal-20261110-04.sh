set -Eeuo pipefail
echo __TEN_EQUAL_DEPLOY_04_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-ten-equal-v2.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-ten-equal-v2.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-ten-equal-v2.py
echo "6948797a2ade66d8411b7c0250067761de27960bfab58cdd2f4883afef54567e  /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-ten-equal-v2.py" | sha256sum -c -
echo __TEN_EQUAL_DEPLOY_04_END__
