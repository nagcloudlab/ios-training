#!/bin/sh
# Rebuild the Lesson 3.4 evidence app, run each experiment in the iOS Simulator,
# print its console, and save the screenshots used by decks/unit-3/lesson-3.4/ into img/. Run: sh tools/sim3_4/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-3/lesson-3.4/img
APPID=example.npay.lab34
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab34.app" && cp Info.plist "$TMP/NPayLab34.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay App.swift -o "$TMP/NPayLab34.app/NPayLab34"
codesign -s - "$TMP/NPayLab34.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab34.app"
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

[ -n "$ONLYSHOT" ] && { SHOTWAIT=${SHOTWAIT:-8} shot $ONLYSHOT full $ONLYSHOT; exit 0; }
[ -n "$ONLY" ] && { WAIT=${WAIT:-10} run $ONLY; exit 0; }
WAIT=8 run sheetexp; WAIT=8 run alert; WAIT=8 run dialog; WAIT=10 run localstate; WAIT=16 run timeline; WAIT=8 run naive
WAIT=14 run revalidate; WAIT=14 run doubleguard; WAIT=8 run doubleraw; WAIT=34 run verify

if [ -z "$NOSHOTS" ]; then
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
cp ../../decks/unit-3/lesson-3.3/img/typed.png "$IMG/before.png"   # Lesson 3.3: Send Demo Payment records at once
SHOTWAIT=5 shot sheetexp full s_sheetexp
SHOTWAIT=5 shot cover full s_cover
SHOTWAIT=5 shot alert full s_alert
SHOTWAIT=5 shot dialog full s_dialog
SHOTWAIT=9 shot typed full s_typed
SHOTWAIT=11 shot review full s_review
SHOTWAIT=13 shot edit full s_edit
SHOTWAIT=14 shot success full s_success
SHOTWAIT=16 shot home full s_home
SHOTWAIT=18 shot history full s_history
SHOTWAIT=14 shot failure full s_failure
fi
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
