#!/bin/sh
# Rebuild the Lesson 3.9 evidence app, run the labs in the iOS Simulator (light and dark system appearance) and save the
# screenshots used by decks/unit-3/lesson-3.9/ into img/. Run: sh tools/sim3_9/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
export UDID
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-3/lesson-3.9/img
APPID=example.npay.lab39
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab39.app" && cp Info.plist "$TMP/NPayLab39.app/"
xcrun actool Assets.xcassets --compile "$TMP/NPayLab39.app" --platform iphonesimulator --minimum-deployment-target 17.0 \
  --output-partial-info-plist "$TMP/assets.plist" >/dev/null
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay App.swift -o "$TMP/NPayLab39.app/NPayLab39"
codesign -s - "$TMP/NPayLab39.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab39.app"
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
xcrun simctl ui "$UDID" appearance light
run() { sh runone.sh "$1" "${2:-5}" | xcrun swift-demangle --simplified; }
shot() {  # shot NAME MODE full|crop [WAIT]
  xcrun simctl launch --terminate-running-process "$UDID" $APPID "$2" >/dev/null; sleep ${4:-3}
  xcrun simctl io "$UDID" screenshot "$TMP/$1.png" >/dev/null 2>&1
  [ "$3" = full ] || "$TMP/crop" "$TMP/$1.png" "$TMP/$1.png" 100 >/dev/null
  sips -Z 900 "$TMP/$1.png" --out "$IMG/$1.png" >/dev/null
}

echo "##### system appearance: light"
run envexp; run override; run precedence; run demokey; run traced 8; run flow 20
run relaunch1 9; run relaunch2 5
echo "== missing (no NPayPreferences in the environment)"
xcrun simctl launch --console-pty --terminate-running-process "$UDID" $APPID missing > "$TMP/missing" 2>&1 < /dev/null &
sleep 5; xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
grep -a "Fatal\|fatal\|No Observable\|environment" "$TMP/missing" | head -5 || true
shot envexp_light envexp full; shot override override full
shot sheetenv sheetenv full 5; shot sheetpref sheetpref full 5
shot settings s_settings full 7; shot home_dark s_home_dark full 8; shot history_dark s_history_dark full 8; shot nobadge s_nobadge full 8
shot home home full
echo "##### system appearance: dark"
xcrun simctl ui "$UDID" appearance dark; sleep 1
run envexp
shot envexp_dark envexp full
xcrun simctl ui "$UDID" appearance light

xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
