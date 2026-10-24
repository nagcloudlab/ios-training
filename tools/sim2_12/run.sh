#!/bin/sh
# Rebuild the Lesson 2.12 evidence app, run each experiment in the iOS Simulator,
# print its console, and save the screenshots used by decks/unit-2/lesson-2.12/ into img/. Run: sh tools/sim2_12/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-2/lesson-2.12/img
APPID=example.npay.lab12
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab12.app" && cp Info.plist "$TMP/NPayLab12.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator App.swift -o "$TMP/NPayLab12.app/NPayLab12"
codesign -s - "$TMP/NPayLab12.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab12.app"
# SwiftUI exposes accessibility elements only when accessibility is on; the app activates buttons through them
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true

run() {   # console output of one experiment
  echo "== $*"
  xcrun simctl launch --console-pty --terminate-running-process "$UDID" $APPID "$@" > "$TMP/log" 2>&1 < /dev/null &
  sleep ${WAIT:-5}; xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
  grep -av "^$APPID\|^objc\[" "$TMP/log" | xcrun swift-demangle --simplified || true
}
shot() {  # shot NAME full|crop ARGS...: screenshot, optionally crop to the content rows, scale to 900 px
  name=$1 mode=$2; shift 2
  xcrun simctl launch --terminate-running-process "$UDID" $APPID "$@" >/dev/null; sleep ${SHOTWAIT:-3}
  xcrun simctl io "$UDID" screenshot "$TMP/$name.png" >/dev/null 2>&1
  [ "$mode" = full ] || "$TMP/crop" "$TMP/$name.png" "$TMP/$name.png" 120 >/dev/null
  sips -Z 900 "$TMP/$name.png" --out "$IMG/$name.png" >/dev/null
}

WAIT=12 run pay; WAIT=16 run invalid; WAIT=6 run status

xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
cp ../../decks/unit-2/lesson-2.11/img/final.png "$IMG/before.png"   # where Lesson 2.11 ended
shot final full final
SHOTWAIT=10 shot paidtop full paidtop
SHOTWAIT=10 shot paidbottom full paidbottom
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
