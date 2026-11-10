echo __PRECISION_POST04_FAILURE_ARCHIVE_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/precision-post04-smoke-hidev-npu0";cat "$q/exit.txt";cat "$q/attempt.txt";tail -n 12 "$q/console.log";f="$r/precision-post04-smoke-archive.log";test ! -f "$f" || tail -n 8 "$f"
echo __PRECISION_POST04_FAILURE_ARCHIVE_END__
