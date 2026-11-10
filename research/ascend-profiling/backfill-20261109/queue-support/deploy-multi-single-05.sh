echo __MULTI_DEPLOY_05_BEGIN__
base64 -d /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-app-candidate-v2.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-app-candidate-v2.py
echo "1367cef012e8f5a6acb4c10545fd68eb1bbfae4c6178afb53333580441bda15a  /workspace/expert-profile-backfill-20261109-hidev/audit-mhc-multilayer-app-candidate-v2.py" | sha256sum -c -
echo __MULTI_DEPLOY_05_END__
