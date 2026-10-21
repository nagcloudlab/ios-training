#!/bin/sh
# Regenerate Lessons 0.2–0.10 from their generators (Lesson 0.1 is hand-edited HTML).
# Run from the repo root:  sh tools/build.sh
# Then check:  python3 tools/structure.py decks/*/index.html
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python3}
$PY tools/gen02.py decks/lesson-0.2/index.html
$PY tools/post02_text.py            # keeps only the lesson text's slides (reads/writes decks/lesson-0.2/index.html)
for n in 3 4 5 6 7 8 9; do
  $PY tools/gen0$n.py decks/lesson-0.$n/index.html
done
$PY tools/gen10.py decks/lesson-0.10/index.html
