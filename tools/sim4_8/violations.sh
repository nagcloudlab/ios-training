#!/bin/sh
# Lesson 4.8, section 20: build NPayCore four times, each with one boundary violation, and print the compiler's errors.
# Run: sh tools/sim4_8/violations.sh
cd "$(dirname "$0")"
TMP=$(mktemp -d)
for v in noinit importdata notpublic cycle; do rsync -a --exclude .build NPayCore/ "$TMP/$v/"; done
/usr/bin/python3 - "$TMP" <<'PY'
import sys
t = sys.argv[1]
def edit(path, old, new):
    s = open(path).read(); assert old in s, (path, old[:40]); open(path, 'w').write(s.replace(old, new, 1))
# 1. PaymentRecord without its explicit public init (the memberwise init is internal)
p = f'{t}/noinit/Sources/NPayDomain/AccountRepository.swift'; s = open(p).read()
a = s.index('    public init(\n        id: UUID'); b = s.index('    }\n}\n', a) + 8
open(p, 'w').write(s[:a].rstrip() + '\n}\n' + s[b:])
# 2. NPayDomain imports NPayData without declaring a dependency
edit(f'{t}/importdata/Sources/NPayDomain/PaymentAmount.swift', 'import Foundation', 'import Foundation\nimport NPayData')
# 3. PaymentRecord no longer public
edit(f'{t}/notpublic/Sources/NPayDomain/AccountRepository.swift', 'public struct PaymentRecord', 'struct PaymentRecord')
# 4. NPayDomain depends on NPayData, which depends on NPayDomain
edit(f'{t}/cycle/Package.swift', '            name: "NPayDomain"\n', '            name: "NPayDomain",\n            dependencies: ["NPayData"]\n')
PY
for v in noinit importdata notpublic cycle; do
  echo "== $v"
  ( cd "$TMP/$v" && swift build 2>&1 | grep -E "error:" | grep -v "emit-module command failed" | sed -E 's|.*/Sources/|Sources/|' | sort -u | head -3 )
done
