#!/bin/sh
# Lesson 4.9 experiments on throwaway copies: (1) a boundary bug in PaymentPolicy with and without the at-limit test,
# (2) PaymentViewModel without its busy guard: the duplicate-submission test never finishes (capped at 40 s).
# Run: sh tools/sim4_9/experiments.sh
cd "$(dirname "$0")"
T=$(mktemp -d)
rsync -a --exclude .build ./ "$T/s/"
cd "$T/s/NPayCore"
sed -i '' 's/guard amount.paise <= maximumPerPaymentPaise else/guard amount.paise < maximumPerPaymentPaise else/' Sources/NPayDomain/SendPaymentUseCase.swift
cov() { xcrun llvm-cov report .build/arm64-apple-macosx/debug/NPayCorePackageTests.xctest/Contents/MacOS/NPayCorePackageTests \
  -instr-profile=.build/arm64-apple-macosx/debug/codecov/default.profdata -ignore-filename-regex="Tests|\.build" | awk '/TOTAL/ {print "   coverage TOTAL lines", $(NF-3)}'; }
echo "== '<=' changed to '<' in PaymentPolicy"
swift test --enable-code-coverage 2>&1 | grep -E "✘ Test acceptsAmountAtLimit\(\) recorded|Test run with" | sed -E 's/ after [0-9.]+ seconds//' | sort -u
echo "== same bug, acceptsAmountAtLimit removed"
/usr/bin/python3 - <<'PY'
p = 'Tests/NPayDomainTests/PaymentPolicyTests.swift'; s = open(p).read()
a = s.index('    @Test\n    func acceptsAmountAtLimit'); b = s.index('    @Test\n    func rejectsAmountAboveLimit')
open(p, 'w').write(s[:a] + s[b:])
PY
swift test --enable-code-coverage 2>&1 | grep -E "Test run with" | sed -E 's/ after [0-9.]+ seconds//'; cov
echo "== PaymentViewModel without its busy guard"
cd "$T/s"
/usr/bin/python3 - <<'PY'
p = 'NPay/Features/Payments/PaymentViewModel.swift'; s = open(p).read()
open(p, 'w').write(s.replace('        guard !state.isBusy else {\n            return .failure("A payment is already processing")\n        }\n', ''))
PY
cd NPayAppTests && swift build --build-tests >/dev/null 2>&1
START=$(date +%s); perl -e 'alarm 40; exec @ARGV' swift test --filter duplicateSubmissionIsRejected >/dev/null 2>&1
echo "   duplicateSubmissionIsRejected: no result; stopped after $(( $(date +%s) - START )) s"
