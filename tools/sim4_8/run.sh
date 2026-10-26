#!/bin/sh
# Rebuild the Lesson 4.8 evidence app: build NPayCore (NPayDomain, NPayData) for the iOS Simulator with SwiftPM, compile
# the app's feature-folder sources against those modules, run the module and verification checks, and print the layout.
# Run: sh tools/sim4_8/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
export UDID
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
APPID=example.npay.lab48
TMP=$(mktemp -d)
APP="$TMP/NPayLab48.app"
mkdir -p "$APP" && cp Info.plist "$APP/"
( cd NPayCore && swift build --triple arm64-apple-ios17.0-simulator --sdk "$SDK" 2>&1 | grep -E "error|Compiling|Build complete" )
BUILD=NPayCore/.build/arm64-apple-ios-simulator/debug
xcrun actool Assets.xcassets --compile "$APP" --platform iphonesimulator --minimum-deployment-target 17.0 \
  --output-partial-info-plist "$TMP/assets.plist" >/dev/null
xcrun xcstringstool compile Localizable.xcstrings --output-directory "$APP"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay -D DEBUG \
  -I "$BUILD/Modules" $(find NPay Lab -name '*.swift' | sort) "$BUILD"/NPayDomain.build/*.o "$BUILD"/NPayData.build/*.o \
  -o "$APP/NPayLab48"
codesign -s - "$APP"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$APP"
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true
sh runone.sh 6 modules
sh runone.sh 22 verify | grep -v "^\[tab\|^\[focus\|^\[activate"
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "app sources: $(find NPay -name '*.swift' | wc -l | tr -d ' ') files in $(find NPay -type d -mindepth 1 | wc -l | tr -d ' ') folders; one module, NPay"
