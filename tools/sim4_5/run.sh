#!/bin/sh
# Rebuild the Lesson 4.5 evidence app (the repository lab), pay with and without the explicit dashboard refresh and save the screenshots used by decks/unit-4/lesson-4.5/ into img/.
# Run: sh tools/sim4_5/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
export UDID
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-4/lesson-4.5/img
APPID=example.npay.lab45
TMP=$(mktemp -d)
APP="$TMP/NPayLab45.app"
mkdir -p "$IMG" "$APP" && cp Info.plist "$APP/"
xcrun actool Assets.xcassets --compile "$APP" --platform iphonesimulator --minimum-deployment-target 17.0 \
  --output-partial-info-plist "$TMP/assets.plist" >/dev/null
xcrun xcstringstool compile Localizable.xcstrings --output-directory "$APP"   # en.lproj, ta.lproj, hi.lproj
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay -D DEBUG App.swift -o "$APP/NPayLab45"
codesign -s - "$APP"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$APP"
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
xcrun simctl ui "$UDID" appearance light
EN="-AppleLanguages (en) -AppleLocale en_IN"
TA="-AppleLanguages (ta) -AppleLocale ta_IN"
HI="-AppleLanguages (hi) -AppleLocale hi_IN"
RTL="-AppleTextDirection YES -NSForceRightToLeftWritingDirection YES"
shot() {  # shot NAME full|crop WAIT MODE [args...]
  name=$1 mode=$2 w=$3; shift 3
  xcrun simctl launch --terminate-running-process "$UDID" $APPID "$@" >/dev/null; sleep "$w"
  xcrun simctl io "$UDID" screenshot "$TMP/$name.png" >/dev/null 2>&1
  [ "$mode" = full ] || "$TMP/crop" "$TMP/$name.png" "$TMP/$name.png" 100 >/dev/null
  sips -Z 900 "$TMP/$name.png" --out "$IMG/$name.png" >/dev/null
}

sh runone.sh 8 norefresh; sh runone.sh 8 refresh
shot norefresh crop 7 norefresh; shot refresh crop 7 refresh
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
