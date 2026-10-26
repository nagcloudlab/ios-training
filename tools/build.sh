#!/bin/sh
# Regenerate Lessons 0.2–0.10, 1.1–1.10, 2.1–2.12 and 3.1–3.10 from their generators (Lesson 0.1 is hand-edited HTML).
# Run from the repo root:  sh tools/build.sh
# Then check:  python3 tools/structure.py decks/*/index.html
set -e
cd "$(dirname "$0")/.."
PY=${PY:-python3}
$PY tools/gen02.py decks/unit-0/lesson-0.2/index.html
$PY tools/post02_text.py            # keeps only the lesson text's slides (reads/writes decks/unit-0/lesson-0.2/index.html)
for n in 3 4 5 6 7 8 9; do
  $PY tools/gen0$n.py decks/unit-0/lesson-0.$n/index.html
done
$PY tools/gen10.py decks/unit-0/lesson-0.10/index.html
$PY tools/gen0_all.py decks/unit-0/unit-00-complete/index.html   # merged code-free Unit 00 (reads the ten decks above)
$PY tools/gen1_1.py decks/unit-1/lesson-1.1/index.html
$PY tools/gen1_2.py decks/unit-1/lesson-1.2/index.html
$PY tools/gen1_3.py decks/unit-1/lesson-1.3/index.html
$PY tools/gen1_4.py decks/unit-1/lesson-1.4/index.html
$PY tools/gen1_5.py decks/unit-1/lesson-1.5/index.html
$PY tools/gen1_6.py decks/unit-1/lesson-1.6/index.html
$PY tools/gen1_7.py decks/unit-1/lesson-1.7/index.html
$PY tools/gen1_8.py decks/unit-1/lesson-1.8/index.html
$PY tools/gen1_9.py decks/unit-1/lesson-1.9/index.html
$PY tools/gen1_10.py decks/unit-1/lesson-1.10/index.html
$PY tools/gen2_1.py decks/unit-2/lesson-2.1/index.html
$PY tools/gen2_2.py decks/unit-2/lesson-2.2/index.html
$PY tools/gen2_3.py decks/unit-2/lesson-2.3/index.html
$PY tools/gen2_4.py decks/unit-2/lesson-2.4/index.html
$PY tools/gen2_5.py decks/unit-2/lesson-2.5/index.html
$PY tools/gen2_6.py decks/unit-2/lesson-2.6/index.html
$PY tools/gen2_7.py decks/unit-2/lesson-2.7/index.html
$PY tools/gen2_8.py decks/unit-2/lesson-2.8/index.html
$PY tools/gen2_9.py decks/unit-2/lesson-2.9/index.html
$PY tools/gen2_10.py decks/unit-2/lesson-2.10/index.html
$PY tools/gen2_11.py decks/unit-2/lesson-2.11/index.html
$PY tools/gen2_12.py decks/unit-2/lesson-2.12/index.html
$PY tools/gen3_1.py decks/unit-3/lesson-3.1/index.html
$PY tools/gen3_2.py decks/unit-3/lesson-3.2/index.html
$PY tools/gen3_3.py decks/unit-3/lesson-3.3/index.html
$PY tools/gen3_4.py decks/unit-3/lesson-3.4/index.html
$PY tools/gen3_5.py decks/unit-3/lesson-3.5/index.html
$PY tools/gen3_6.py decks/unit-3/lesson-3.6/index.html
$PY tools/gen3_7.py decks/unit-3/lesson-3.7/index.html
$PY tools/gen3_8.py decks/unit-3/lesson-3.8/index.html
$PY tools/gen3_9.py decks/unit-3/lesson-3.9/index.html
$PY tools/gen3_10.py decks/unit-3/lesson-3.10/index.html
$PY tools/gen3_11.py decks/unit-3/lesson-3.11/index.html
$PY tools/gen3_12.py decks/unit-3/lesson-3.12/index.html
$PY tools/gen4_1.py decks/unit-4/lesson-4.1/index.html
$PY tools/gen4_2.py decks/unit-4/lesson-4.2/index.html
$PY tools/gen4_3.py decks/unit-4/lesson-4.3/index.html
$PY tools/gen4_4.py decks/unit-4/lesson-4.4/index.html
$PY tools/gen4_5.py decks/unit-4/lesson-4.5/index.html
$PY tools/gen4_6.py decks/unit-4/lesson-4.6/index.html
$PY tools/gen4_7.py decks/unit-4/lesson-4.7/index.html
$PY tools/gen4_8.py decks/unit-4/lesson-4.8/index.html
$PY tools/gen4_9.py decks/unit-4/lesson-4.9/index.html
$PY tools/gen4_10.py decks/unit-4/lesson-4.10/index.html
