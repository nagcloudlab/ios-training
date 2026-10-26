#!/bin/sh
# Run one experiment of run.sh (and copy its frames): sh runone.sh MODE WAIT [frames]
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
APPID=example.npay.lab39; IMG=../../decks/unit-3/lesson-3.9/img
LOG=$(mktemp)
xcrun simctl launch --console-pty --terminate-running-process "$UDID" $APPID "$1" > "$LOG" 2>&1 < /dev/null &
sleep "$2"; xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
echo "== $1"; grep -av "^$APPID\|^objc\[" "$LOG"
if [ -n "$3" ]; then
  C=$(xcrun simctl get_app_container "$UDID" $APPID data)
  for f in "$C"/tmp/$3*.png; do sips -Z 600 "$f" --out "$IMG/$(basename "$f")" >/dev/null; done
fi
