#!/bin/sh
# Rebuild the Lesson 2.1 evidence app, run each scenario in the iOS Simulator, print its console,
# and save dashboard screenshots to decks/unit-2/lesson-2.1/img/. Run from the repo root.
set -e
cd "$(dirname "$0")"
UDID=${UDID:-$(xcrun simctl list devices available | grep -m1 'iPhone 17 (' | sed -E 's/.*\(([0-9A-F-]+)\).*/\1/')}
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
rm -rf NPayLab.app && mkdir NPayLab.app && cp Info.plist NPayLab.app/
xcrun swiftc -swift-version 6 -parse-as-library -sdk "$SDK" -target arm64-apple-ios17.0-simulator App.swift -o NPayLab.app/NPayLab
codesign -s - NPayLab.app
xcrun simctl boot "$UDID" 2>/dev/null || true
xcrun simctl bootstatus "$UDID" -b >/dev/null
xcrun simctl install "$UDID" NPayLab.app
for sc in body changes identity uuid stableid; do
  echo "== $sc"
  xcrun simctl launch --console-pty --terminate-running-process "$UDID" example.npay.lab $sc > /tmp/npaylab.log 2>&1 &
  sleep 5; xcrun simctl terminate "$UDID" example.npay.lab 2>/dev/null || true
  grep -v '^example' /tmp/npaylab.log
done
xcrun simctl status_bar "$UDID" override --time 9:41 --batteryState charged --batteryLevel 100 --cellularBars 4
for sc in dash tapped; do
  xcrun simctl launch --terminate-running-process "$UDID" example.npay.lab $sc >/dev/null; sleep 3
  xcrun simctl io "$UDID" screenshot "/tmp/$sc.png" >/dev/null
  sips -Z 900 "/tmp/$sc.png" --out "../../decks/unit-2/lesson-2.1/img/$sc.png" >/dev/null
done
rm -rf NPayLab.app
