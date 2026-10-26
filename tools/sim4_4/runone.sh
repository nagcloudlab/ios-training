#!/bin/sh
# Run one experiment: sh runone.sh WAIT MODE [launch arguments...]
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
APPID=example.npay.lab44
LOG=$(mktemp); W=$1; shift
xcrun simctl launch --console-pty --terminate-running-process "$UDID" $APPID "$@" > "$LOG" 2>&1 < /dev/null &
sleep "$W"; xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
echo "== $*"; grep -av "^$APPID\|^objc\[" "$LOG"
