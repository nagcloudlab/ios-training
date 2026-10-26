#!/bin/sh
# Rebuild the Lesson 3.5 evidence app, run each experiment in the iOS Simulator,
# print its console, and save the screenshots used by decks/unit-3/lesson-3.5/ into img/. Run: sh tools/sim3_5/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-3/lesson-3.5/img
APPID=example.npay.lab35
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab35.app" && cp Info.plist "$TMP/NPayLab35.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay App.swift -o "$TMP/NPayLab35.app/NPayLab35"
codesign -s - "$TMP/NPayLab35.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab35.app"
# SwiftUI exposes accessibility elements only when accessibility is on; the app activates links and buttons through them
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true

run() {   # console output of one experiment
  echo "== $*"
  xcrun simctl launch --console-pty --terminate-running-process "$UDID" $APPID "$@" > "$TMP/log" 2>&1 < /dev/null &
  sleep ${WAIT:-6}; xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
  grep -av "^$APPID\|^objc\[" "$TMP/log" | xcrun swift-demangle --simplified || true
}
shot() {  # shot NAME full|crop ARGS...: screenshot, optionally crop to the content rows, scale to 900 px
  name=$1 mode=$2; shift 2
  xcrun simctl launch --terminate-running-process "$UDID" $APPID "$@" >/dev/null; sleep ${SHOTWAIT:-3}
  xcrun simctl io "$UDID" screenshot "$TMP/$name.png" >/dev/null 2>&1
  [ "$mode" = full ] || "$TMP/crop" "$TMP/$name.png" "$TMP/$name.png" 120 >/dev/null
  sips -Z 900 "$TMP/$name.png" --out "$IMG/$name.png" >/dev/null
}

[ -n "$ONLYSHOT" ] && { SHOTWAIT=${SHOTWAIT:-8} shot ${NAME:-$ONLYSHOT} ${MODE:-full} $ONLYSHOT; exit 0; }
[ -n "$ONLY" ] && { WAIT=${WAIT:-10} run $ONLY; exit 0; }
WAIT=10 run localtab; WAIT=10 run localswap; WAIT=10 run value; WAIT=10 run idlab; WAIT=10 run unstable; WAIT=10 run draftexp
WAIT=40 run flow
# Experiment 8: restart the app
WAIT=12 run restart1; WAIT=6 run restart2

if [ -z "$NOSHOTS" ]; then
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
SHOTWAIT=7 shot idbefore crop s_idbefore
SHOTWAIT=8 shot idafter crop s_idafter
SHOTWAIT=8 shot draftexp crop s_draftexp
SHOTWAIT=9 shot typed full s_typed
SHOTWAIT=12 shot back full s_back
SHOTWAIT=11 shot review full s_review
SHOTWAIT=17 shot cleared full s_cleared
SHOTWAIT=11 shot discard full s_discard
fi
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
