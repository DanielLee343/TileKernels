echo __THREE_THREE_FAIL_BEGIN__
r=/workspace/expert-profile-backfill-20261109-hidev;q="$r/extra-mhc-variant-three-three-smoke-hidev-npu0";cat "$q/exit.txt";cat "$q/attempt.txt";tail -n 30 "$q/console.log" | cut -c1-400
f="$r/mhc-variant-three-three-queue-archive.log";test ! -f "$f" || tail -n 6 "$f"
echo __THREE_THREE_FAIL_END__
