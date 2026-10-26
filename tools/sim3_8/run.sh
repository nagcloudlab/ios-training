#!/bin/sh
# Rebuild the Lesson 3.8 evidence app, run the labs on an iPhone 17, an iPhone SE (3rd generation) and an iPad Air
# 11-inch (created if missing), at two text sizes and in landscape, and save the screenshots used by
# decks/unit-3/lesson-3.8/ into img/. Run: sh tools/sim3_8/run.sh
set -e
cd "$(dirname "$0")"
IPHONE=$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')
device() {  # device NAME TYPE: the UDID of a named simulator, created on first use
  u=$(xcrun simctl list devices available | grep -m1 "$1 (" | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')
  [ -n "$u" ] || u=$(xcrun simctl create "$1" "$2" com.apple.CoreSimulator.SimRuntime.iOS-26-5)
  echo "$u"
}
SE=$(device "NPay iPhone SE" com.apple.CoreSimulator.SimDeviceType.iPhone-SE-3rd-generation)
IPAD=$(device "NPay iPad Air 11" com.apple.CoreSimulator.SimDeviceType.iPad-Air-11-inch-M4)
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-3/lesson-3.8/img
APPID=example.npay.lab38
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab38.app" && cp Info.plist "$TMP/NPayLab38.app/"
xcrun actool Assets.xcassets --compile "$TMP/NPayLab38.app" --platform iphonesimulator --minimum-deployment-target 17.0 \
  --output-partial-info-plist "$TMP/assets.plist" >/dev/null
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay App.swift -o "$TMP/NPayLab38.app/NPayLab38"
codesign -s - "$TMP/NPayLab38.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
prepare() {  # prepare UDID: boot, install, accessibility on, clean status bar
  xcrun simctl boot "$1" 2>/dev/null || true
  xcrun simctl bootstatus "$1" -b >/dev/null
  xcrun simctl install "$1" "$TMP/NPayLab38.app"
  xcrun simctl spawn "$1" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
  xcrun simctl spawn "$1" defaults write com.apple.Accessibility AccessibilityEnabled -bool true
  xcrun simctl status_bar "$1" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
  xcrun simctl ui "$1" content_size large
}
run() {   # run UDID MODE [WAIT]: console output of one launch (own shell)
  UDID=$1 sh runone.sh "$2" "${3:-5}" | xcrun swift-demangle --simplified
}
shot() {  # shot UDID NAME MODE full|crop [WAIT]
  xcrun simctl launch --terminate-running-process "$1" $APPID "$3" >/dev/null; sleep ${5:-3}
  xcrun simctl io "$1" screenshot "$TMP/$2.png" >/dev/null 2>&1
  [ "$4" = full ] || "$TMP/crop" "$TMP/$2.png" "$TMP/$2.png" 100 >/dev/null
  sips -Z 900 "$TMP/$2.png" --out "$IMG/$2.png" >/dev/null
}
big() { xcrun simctl ui "$1" content_size accessibility-extra-extra-extra-large; sleep 1; }
normal() { xcrun simctl ui "$1" content_size large; sleep 1; }

prepare "$IPHONE"
echo "##### iPhone 17"
run "$IPHONE" proposal; run "$IPHONE" geo; run "$IPHONE" geoland 6; run "$IPHONE" geoscroll; run "$IPHONE" qa 6; run "$IPHONE" qaland 7; run "$IPHONE" identity 12
shot "$IPHONE" order order crop; shot "$IPHONE" geoscroll geoscroll full; shot "$IPHONE" safe safe full
shot "$IPHONE" qa_geo qageo crop 4; shot "$IPHONE" qa_fit qafit crop 4; shot "$IPHONE" home home full
shot "$IPHONE" homeland homeland full 5; sips -r 270 "$IMG/homeland.png" >/dev/null   # the framebuffer stays portrait
big "$IPHONE"; echo "##### iPhone 17, largest accessibility text"
run "$IPHONE" qa 6
shot "$IPHONE" qa_geo_ax qageo crop 4; shot "$IPHONE" qa_fit_ax qafit crop 4; shot "$IPHONE" home_ax home full
normal "$IPHONE"

prepare "$SE"
echo "##### iPhone SE (3rd generation)"
run "$SE" geo; run "$SE" qa 6
shot "$SE" home_se home full; shot "$SE" qa_geo_se qageo crop 4; shot "$SE" qa_fit_se qafit crop 4
big "$SE"; echo "##### iPhone SE, largest accessibility text"; run "$SE" qa 6; normal "$SE"

prepare "$IPAD"
echo "##### iPad Air 11-inch"
run "$IPAD" geo; run "$IPAD" qa 6; run "$IPAD" geoland 6
shot "$IPAD" home_ipad home full

for u in "$IPHONE" "$SE" "$IPAD"; do
  xcrun simctl terminate "$u" $APPID 2>/dev/null || true
  xcrun simctl spawn "$u" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
  xcrun simctl spawn "$u" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
done
xcrun simctl shutdown "$SE" 2>/dev/null || true; xcrun simctl shutdown "$IPAD" 2>/dev/null || true
echo "screenshots in $IMG"
