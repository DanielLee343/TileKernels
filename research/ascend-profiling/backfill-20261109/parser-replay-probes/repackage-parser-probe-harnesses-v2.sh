set -Eeuo pipefail
echo __PROBE_HARNESS_V2_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;stage="$r/parser-probe-harnesses-20261110"
test -d "$stage";test ! -e "$r/parser-probe-harnesses-20261110-v2.tar.gz"
(cd "$stage" && find . -type f ! -name files.sha256 -print0 | sort -z | xargs -0 sha256sum > files.sha256)
(cd "$stage" && sha256sum -c files.sha256 | tail -n 2)
tar -C "$r" -czf "$r/parser-probe-harnesses-20261110-v2.tar.gz" "$(basename "$stage")"
sha256sum "$r/parser-probe-harnesses-20261110-v2.tar.gz"
echo __PROBE_HARNESS_V2_END__
