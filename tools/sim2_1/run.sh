#!/bin/sh
# Rebuild the Lesson 2.1 evidence app, run each experiment in the iOS Simulator, print its console,
# and save the screenshots used by decks/unit-2/lesson-2.1/ into img/. Run: sh tools/sim2_1/run.sh
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
IMG=../../decks/unit-2/lesson-2.1/img
TMP=$(mktemp -d)
mkdir "$TMP/NPayLab.app" && cp Info.plist "$TMP/NPayLab.app/" && cp -R ta.lproj "$TMP/NPayLab.app/"
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator App.swift -o "$TMP/NPayLab.app/NPayLab"
codesign -s - "$TMP/NPayLab.app"
xcrun swiftc -O crop.swift -o "$TMP/crop"
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" "$TMP/NPayLab.app"

run() {   # console output of one experiment
  echo "== $*"
  xcrun simctl launch --console-pty --terminate-running-process "$UDID" example.npay.lab "$@" > "$TMP/log" 2>&1 < /dev/null &
  sleep 5; xcrun simctl terminate "$UDID" example.npay.lab 2>/dev/null || true
  grep -av '^example' "$TMP/log" || true
}
shot() {  # shot NAME full|crop ARGS...: screenshot, optionally crop to the content rows, scale to 900 px
  name=$1 mode=$2; shift 2
  xcrun simctl launch --terminate-running-process "$UDID" example.npay.lab "$@" >/dev/null; sleep 3
  xcrun simctl io "$UDID" screenshot "$TMP/$name.png" >/dev/null 2>&1
  [ "$mode" = full ] || "$TMP/crop" "$TMP/$name.png" "$TMP/$name.png" 120 >/dev/null
  sips -Z 900 "$TMP/$name.png" --out "$IMG/$name.png" >/dev/null
}

run measure; run types; run order; run unicode; run final
xcrun simctl ui "$UDID" content_size accessibility-extra-large; run final; xcrun simctl ui "$UDID" content_size large

xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
shot hello full hello
shot topleading full topleading
shot measure crop measure
shot order crop order
shot unicode crop unicode
shot l10n-en crop l10n
shot l10n-ta crop l10n -AppleLanguages "(ta)" -AppleLocale ta_IN
shot final crop final
xcrun simctl ui "$UDID" content_size accessibility-extra-large
shot final-ax crop final
xcrun simctl ui "$UDID" content_size large
xcrun simctl terminate "$UDID" example.npay.lab 2>/dev/null || true
echo "screenshots in $IMG"
