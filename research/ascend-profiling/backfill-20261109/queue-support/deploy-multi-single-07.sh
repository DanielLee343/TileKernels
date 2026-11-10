echo __MULTI_DEPLOY_07_BEGIN__
base64 -d /workspace/expert-profile-backfill-20261109-hidev/archive-after-app-queue-v20.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/archive-after-app-queue-v20.py
echo "c9c8d04b2a0e45d3754a3c69cde042f79f8c9eef9b7157cd3acd5068c4aeecf8  /workspace/expert-profile-backfill-20261109-hidev/archive-after-app-queue-v20.py" | sha256sum -c -
echo __MULTI_DEPLOY_07_END__
