#!/bin/sh
# Rebuild the Lesson 3.7 evidence app (twice: normal tokens and -D ALTTOKENS), run the labs in the iOS Simulator and
# save the screenshots used by decks/unit-3/lesson-3.7/ into img/. Run: sh tools/sim3_7/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-3/lesson-3.7/img
APPID=example.npay.lab37
TMP=$(mktemp -d)
mkdir -p "$IMG"
build() {  # build [flags]: compile, add the asset catalog, sign, install
  rm -rf "$TMP/NPayLab37.app"; mkdir -p "$TMP/NPayLab37.app" && cp Info.plist "$TMP/NPayLab37.app/"
  xcrun actool Assets.xcassets --compile "$TMP/NPayLab37.app" --platform iphonesimulator --minimum-deployment-target 17.0 \
    --output-partial-info-plist "$TMP/assets.plist" >/dev/null
  xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay "$@" App.swift -o "$TMP/NPayLab37.app/NPayLab37"
  codesign -s - "$TMP/NPayLab37.app"
  xcrun simctl install "$UDID" "$TMP/NPayLab37.app"
}
run() {   # console output of one experiment (one launch, in its own shell)
  sh runone.sh "$1" "${WAIT:-5}" | xcrun swift-demangle --simplified
}
shot() {  # shot NAME MODE: screenshot of one launch, scaled to 900 px
  xcrun simctl launch --terminate-running-process "$UDID" $APPID "$2" >/dev/null; sleep ${SHOTWAIT:-3}
  xcrun simctl io "$UDID" screenshot "$TMP/$1.png" >/dev/null 2>&1
  sips -Z 900 "$TMP/$1.png" --out "$IMG/$1.png" >/dev/null
}
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4

build
run types; run labels; WAIT=8 run changes
run dynamic
xcrun simctl ui "$UDID" content_size accessibility-extra-extra-extra-large; sleep 1
run dynamic
shot catalog_ax catalog
xcrun simctl ui "$UDID" content_size large; sleep 1
shot catalog catalog
shot home home
SHOTWAIT=5 shot payments s_payments
SHOTWAIT=9 shot valid s_valid
SHOTWAIT=10 shot review s_review
SHOTWAIT=12 shot success s_success
xcrun simctl ui "$UDID" appearance dark; sleep 1
shot catalog_dark catalog
shot home_dark home
xcrun simctl ui "$UDID" appearance light
build -D ALTTOKENS
shot catalog_alt catalog
shot home_alt home

xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
