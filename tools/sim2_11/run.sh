#!/bin/sh
# Rebuild the Lesson 2.11 evidence app, run each experiment in the iOS Simulator,
# print its console, and save the screenshots used by decks/unit-2/lesson-2.11/ into img/. Run: sh tools/sim2_11/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-2/lesson-2.11/img
APPID=example.npay.lab11
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab11.app" && cp Info.plist "$TMP/NPayLab11.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator App.swift -o "$TMP/NPayLab11.app/NPayLab11"
codesign -s - "$TMP/NPayLab11.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab11.app"
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

run types; WAIT=7 run hello; WAIT=12 run typing; WAIT=7 run paste; WAIT=10 run over; WAIT=10 run balance

xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
shot before full before
shot final full final
SHOTWAIT=6 shot hello crop hello
SHOTWAIT=9 shot over full over
SHOTWAIT=11 shot typing full typing
SHOTWAIT=6 shot keyboard full keyboard
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
