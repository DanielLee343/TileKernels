set -Eeuo pipefail
echo __PRECISION_POST04_DEPLOY_10_BEGIN__
test ! -e /workspace/expert-profile-backfill-20261109-hidev/inspect-precision-post04-app.py
base64 -d /workspace/expert-profile-backfill-20261109-hidev/inspect-precision-post04-app.py.b64 > /workspace/expert-profile-backfill-20261109-hidev/inspect-precision-post04-app.py
echo "d098e25707865defd7429e52d1990a8de826f43a22e4bad1425b9bd02bacabd9  /workspace/expert-profile-backfill-20261109-hidev/inspect-precision-post04-app.py" | sha256sum -c -
echo __PRECISION_POST04_DEPLOY_10_END__
