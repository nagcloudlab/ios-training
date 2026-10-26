#!/bin/sh
# Rebuild the Lesson 3.6 evidence app, run each experiment in the iOS Simulator,
# print its console, and save the frames used by decks/unit-3/lesson-3.6/ into img/. Run: sh tools/sim3_6/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-3/lesson-3.6/img
APPID=example.npay.lab36
TMP=$(mktemp -d)
mkdir -p "$IMG" "$TMP/NPayLab36.app" && cp Info.plist "$TMP/NPayLab36.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator -module-name NPay App.swift -o "$TMP/NPayLab36.app/NPayLab36"
codesign -s - "$TMP/NPayLab36.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab36.app"
# SwiftUI exposes accessibility elements only when accessibility is on; the app activates links and buttons through them
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool true

# One launch per experiment (runone.sh); frames the app captures are copied into img/
sh runone.sh circle 6 circle
sh runone.sh curves 12
sh runone.sh interrupt 6
sh runone.sh number 5
sh runone.sh success 5 success
sh runone.sh noanim 5 noanim
sh runone.sh lab 6 lab
sh runone.sh ids 6
# Reduce Motion on, then off again
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ReduceMotionEnabled -bool true
sh runone.sh reduced 5 reduced
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ReduceMotionEnabled -bool false
xcrun simctl terminate "$UDID" $APPID 2>/dev/null || true
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility ApplicationAccessibilityEnabled -bool false
xcrun simctl spawn "$UDID" defaults write com.apple.Accessibility AccessibilityEnabled -bool false
echo "screenshots in $IMG"
