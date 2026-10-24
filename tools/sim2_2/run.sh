#!/bin/sh
# Rebuild the Lesson 2.2 evidence app (with its asset catalog), run each experiment in the iOS Simulator,
# print its console, and save the screenshots used by decks/unit-2/lesson-2.2/ into img/. Run: sh tools/sim2_2/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-2/lesson-2.2/img
APPID=example.npay.lab2
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab2.app" && cp Info.plist "$TMP/NPayLab2.app/"
xcrun actool Assets.xcassets --compile "$TMP/NPayLab2.app" --platform iphonesimulator --minimum-deployment-target 17.0 \
  --output-partial-info-plist "$TMP/assets.plist" >/dev/null
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator App.swift -o "$TMP/NPayLab2.app/NPayLab2"
codesign -s - "$TMP/NPayLab2.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab2.app"

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

run symbol; run invalid; run sizes; run sharp; run types; run assets
echo "== SwiftUI messages in the system log (Xcode shows these in its console)"
xcrun simctl spawn "$UDID" log show --last 2m --style compact \
  --predicate 'process == "NPayLab2" AND category == "Invalid Configuration"' | sed -E 's/.*\] //; s/ for \/.*/ for <app bundle>/' | grep -a '^No ' | sort -u

xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
shot symbol crop symbol
shot library crop library
shot invalid full invalid
shot sizes crop sizes
shot sharp crop sharp
shot colors crop colors
shot assets crop assets
shot before full before
shot final full final
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
echo "screenshots in $IMG"
