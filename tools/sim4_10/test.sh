#!/bin/sh
# Lesson 4.9: run NPayCore's tests (XCTest + Swift Testing) with coverage, then the app's payment-feature tests.
# Run: sh tools/sim4_10/test.sh
cd "$(dirname "$0")"
( cd NPayCore && swift test --enable-code-coverage 2>&1 | grep -E "Executed [0-9]+ tests|Test run with|✘" | sort -u
  BIN=.build/arm64-apple-macosx/debug/NPayCorePackageTests.xctest/Contents/MacOS/NPayCorePackageTests
  xcrun llvm-cov report "$BIN" -instr-profile=.build/arm64-apple-macosx/debug/codecov/default.profdata \
    -ignore-filename-regex="Tests|\.build" | sed -E 's|^.*/Sources/||' | awk '/swift|TOTAL/ {print "coverage:", $1, "lines", $(NF-3)}' )
( cd NPayAppTests && swift test 2>&1 | grep -E "Test run with|✘" )
