#!/bin/sh
# Rebuild the Lesson 2.3 evidence app, run each experiment in the iOS Simulator,
# print its console, and save the screenshots used by decks/unit-2/lesson-2.3/ into img/. Run: sh tools/sim2_3/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-2/lesson-2.3/img
APPID=example.npay.lab3
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab3.app" && cp Info.plist "$TMP/NPayLab3.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator App.swift -o "$TMP/NPayLab3.app/NPayLab3"
codesign -s - "$TMP/NPayLab3.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab3.app"

run() {   # console output of one experiment
  echo "== $*"
  xcrun simctl launch --console-pty --terminate-running-process "$UDID" $APPID "$@" > "$TMP/log" 2>&1 < /dev/null &
  sleep 5; xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
  grep -av "^$APPID" "$TMP/log" || true
}
shot() {  # shot NAME full|crop ARGS...: screenshot, optionally crop to the content rows, scale to 900 px
  name=$1 mode=$2; shift 2
  xcrun simctl launch --terminate-running-process "$UDID" $APPID "$@" >/dev/null; sleep 3
  xcrun simctl io "$UDID" screenshot "$TMP/$name.png" >/dev/null 2>&1
  [ "$mode" = full ] || "$TMP/crop" "$TMP/$name.png" "$TMP/$name.png" 120 >/dev/null
  sips -Z 900 "$TMP/$name.png" --out "$IMG/$name.png" >/dev/null
}

run types; run borders20; run borders50; run padA; run padB; run hug; run fill; run calc
xcrun simctl ui "$UDID" content_size accessibility-extra-large; run calc; xcrun simctl ui "$UDID" content_size large

xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
shot before full before
shot borders20 crop borders20
shot borders50 crop borders50
shot padA crop padA
shot padB crop padB
shot align crop align
shot hug full hug
shot fill full fill
shot calc crop calc
shot final full final
xcrun simctl ui "$UDID" content_size accessibility-extra-large
shot calc-ax crop calc
shot final-ax full final
xcrun simctl ui "$UDID" content_size large
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
echo "screenshots in $IMG"
