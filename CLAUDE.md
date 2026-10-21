# iOS Training — Slide Deck Engine

## What this is
A slide deck engine for a 130-lesson iOS development training course (13 units, 10 lessons each). NPay is the running example app throughout.

## Architecture
- `shared/deck.css` — Design system: 50+ CSS components, animation system, 1280x720 canvas scaled to fit, print styles, reduced-motion support
- `shared/deck.js` — Slide engine: keyboard/touch navigation, step-by-step reveal, `data-lit` step-driven highlighting, Swift syntax highlighting, speaker notes (S key), slide overview (O key), fullscreen (F key)
- Footer shows a `click n / total` counter on slides with steps (hidden in print), so the presenter knows how many clicks remain.
- `shared/art.js` — Illustration library: injects SVG `<symbol>`s (`#i-phone`, `#i-gear`, `#i-kernel`, … and `#d-iphone`). Inline-injected so decks work from file://. Load before deck.js.
- `tools/` — generators for Lessons 0.2+ (`gen02.py` holds shared helpers), `build.sh` to regenerate, `structure.py` + `mkaudit.py` checks. Edit the generator, never the generated HTML. See `tools/README.md`.
- `decks/<lesson>/index.html` — Each deck is just HTML content + shared imports. Zero build step.
- `decks/<lesson>/lesson-X.Y.md` — the lesson's source document (source of truth for content). Kept next to the deck for the user's later study; cross-check every deck against it.

## Design rules
- **Palette**: Navy (#0f172a) + Teal (#0d9488) + White. Orange (#ea580c) for rare emphasis only.
- **Fonts**: DM Sans (body/headings) + IBM Plex Mono (code) via Google Fonts
- **All slides white** except `.slide.title` and `.slide.end` (navy background). Lessons are organized into numbered **Parts** (kicker "Part N · topic"), matching the numbered sections of the lesson text; each part opens with a white `.slide.chapter` divider. Closing material goes under "Wrap-up". Never "Act" or "Chapter".
- **Overview titles** come from the slide's h1/h2; a slide without a heading needs `data-title`.
- **Cards**: prefer `.card.accent` (teal left border). Avoid rainbow-colored cards.
- **Illustrations — "everything grey, one thing teal"**: drawings are slate line art; teal marks only the current focus; orange only for a failure/hot path (max one per slide). Never hard-code hex in an `svg.art` — use the state classes. Legacy tokens (`--blue`, `--green`, `--red`, `--amber`, `--violet`) are remapped to slate/teal/orange so old markup can't add hues.
- **Diagrams**: prefer `svg.art` illustrations (see Lesson 0.1 slides 7, 11, 23 as reference). CSS `.flow`/`.vflow`/`.layers` are fine for simple cases.
- **Boxes vs lines**: diagram boxes are soft tiles (light fill, light border); `.wire` connectors are darker slate lines; `.wire.faint` for background guides such as sequence lifelines. Never make box borders and arrows the same grey.
- **Step-driven focus**: `data-lit="N" | "N-M" | "N+"` adds `.lit` while N steps are shown; `<i class="step cue"></i>` advances focus without revealing content. Move the teal through one drawing instead of adding new boxes.
- **Lesson scope**: build each deck only from the lesson text the user shares. Don't add slides from other briefs or invent extra content; anything authored to fill a gap gets flagged.
- **Code on slides**: short, simple snippets (roughly up to ~12 lines) are fine when they help. Longer code is written in the live demo; put its script in the speaker notes under a LIVE DEMO label. Every snippet must typecheck.
- **Teaching pattern**: content slides teach (reveal -> explain -> connect) and carry no predict questions. All predict questions live in a **"Check your understanding" review section** near the end (after the myths slide, before Practice): one `.slide.question` per question: `.q-top` (kicker "Check your understanding · n of N" + `.q-dots` progress), no h2 (overview title comes from `data-title`), `.q-row` with a `.q-card` (`.q-icon`, "Question" label, `.q-text`) and a dashed `.q-panel` whose `.q-ans.step` reveals `.q-verdict` pill, `.q-why` and `.q-trap` ("Common trap: …").
- **Audience**: corporate training. No interview framing ("interview questions", "you could be asked"); review questions are always "Check your understanding".
- **Student-facing only**: no trainer language ("Ask your participants", "Trainer Moment", etc.) in slide content
- **Speaker notes**: `<aside class="notes-src">` inside every slide (chapters and end slide included) with SAY/ASK/EXPECT/CONNECT labels
- **Orange budget**: at most one orange element per slide (`.misconception`, `.warn`, `.alert`). For several myths, use a Myth/Reality `.tbl`.
- **Facts**: no benchmark or timing numbers (no "X ms" launch claims). Never name private daemons, IPC hops or undocumented ordering (e.g. no RunningBoard/launchd on slides). Kicker of any diagram of undocumented iOS internals ends with `· conceptual`.

## Key components
- `.step` — incremental reveal on click
- `.flow` / `.vflow` — horizontal/vertical flow diagrams with `.box` and `.arrow`
- `.flow-anim` / `.vflow-anim` / `.layers-anim` — animated sequential reveal
- `.cw` > `.ch` > `.cb` — code window with traffic-light dots, filename, auto Swift highlighting
- `.slide.question` > `.q-row` > `.q-card` + `.q-panel` > `.q-ans.step` — review Q&A slide (question, answer on click)
- `.analogy` / `.misconception` / `.takeaway` / `.rule` / `.tip` / `.warn` — callout types
- `.card.accent` — standard content card with teal left border
- `.layers` > `.layer` — stacked architecture diagram
- `.tbl` — clean data table
- `.points` — row of 3 short points, each `<div><svg><use href="#i-…"/></svg><span><b>title</b><small>detail</small></span></div>`; use instead of a run-on sentence inside a callout
- `data-label` on `.tip`/`.rule`/`.warn` replaces the generic TIP/REMEMBER/WATCH OUT label (e.g. `data-label="SpringBoard"`)
- `.anim-*` — entrance animations (triggered when `.step.shown`)
- `.q-opts` / `.q-code` — multiple-choice options and code lines inside a `.q-card` (generated by `qhtml()`)
- `.partmap` — automatic lesson map on every `.slide.chapter` (deck.js); keep divider kickers and h2s short
- `.bridge` — Last time / Today pair on the "Where we are" slide; `ol.lab` — lab steps
- `svg.art` > `g.nd` (`.sh` shape + `<use href="#i-…">` + `text`/`text.sm`) — illustration node; modifiers `.lit` `.solid` `.ghost` `.alert` `.pass` (teal sweeps through once, stagger with `--d`); `.wire` (`.lit`, `.dash`), `.fade` (visible only when lit), `.mute`, `.ring`, `.travel` (animated dot, hidden under reduced motion)

## Curriculum
130 lessons across 13 units. Full curriculum in user's local file `complete-ios-mastery-all-units-lessons.md`. Units:
- 00: iOS Architecture Foundations
- 01: Swift Language Mastery
- 02: SwiftUI Fundamentals
- 03: Advanced SwiftUI & Navigation
- 04: Application Architecture & MVVM
- 05: Networking & API Integration
- 06: Persistence & Offline-First
- 07: Security, Privacy & Authentication
- 08: Advanced Concurrency & Performance
- 09: Testing, Debugging & Quality
- 10: UIKit & Platform Integration
- 11: Build, Delivery & App Store
- 12: Advanced iOS Architecture & Capstone

## Current status
- Engine: complete and audited
- **Unit 00 reworked after the audit** (`docs/unit-00-audit.md`, aligned with the curriculum plan `complete-ios-mastery-all-units-lessons.md`). Every lesson now follows one structure: Title → Outcomes → "Where we are" (`map_slide`: the shared NPay architecture map + Last time / Today bridge) → Parts (dividers show an automatic lesson map) → Recap (`recap_slide`) → Check your understanding (4–8 questions, mixed verdicts, multiple choice via `qhtml`, predict-the-output, one spaced item from an earlier lesson) → Where this goes next (`next_slide`, later plan lessons) → Lab (`lab_slide`; concept labs, Swift CLI labs in 0.5/0.6/0.8, Unit 00 checkpoint + rubric in 0.10) → End slide with "Next: …".
- **NPay canon** (all lessons): ₹25,000; "Refresh balance"; `NPayApp`, `DashboardView`, `@MainActor @Observable final class DashboardViewModel` (owned via `@State`), `BalanceService`, `Balance` with `balanceMinor: Int64` (ViewModel formats currency); `(200..<300)` status check; launch = scene connects inactive → first frame → active; statement PDF in Caches, app data in Application Support. Two analogies only: hotel (platform & security) and restaurant kitchen (inside the process).
- **Topic ownership** inside Unit 00: 0.2 "body is a description"; 0.3 process vs scene + states; 0.4 `scenePhase` (App vs View); 0.6 memory regions; 0.7 "token in UserDefaults?"; 0.8 the request journey + login flow. Topics owned by later units get a one-line forward pointer, not a slide.
- Slide counts: 0.1 48 · 0.2 25 · 0.3 33 · 0.4 33 · 0.5 42 · 0.6 44 · 0.7 30 · 0.8 34 · 0.9 31 · 0.10 39. Each `lesson-0.X-text.md` (0.2–0.10) keeps the user's text and ends with "Deck changes after the Unit 00 audit" listing corrections, cuts and every authored addition; 0.1's study companion is kept in sync with its deck.
- Lesson 0.1 is hand-edited HTML (`decks/lesson-0.1/index.html`); 0.2–0.10 are generated by `tools/gen02.py`…`gen10.py` (+ `post02_text.py`). Shared Unit 00 helpers (`archmap`, `map_slide`, `recap_slide`, `next_slide`, `lab_slide`, `qhtml`) live in `gen02.py` above `S = []`.
- Steppers: the last step's state stays shown (`N+`) when a closing callout follows, so the final detail doesn't disappear on the last click.
- **Tables**: show a table whole (no per-row steps); keep any closing callout as the one click.
- Demo deck: component showcase (19 slides). The old multi-colour premium SVG demo was removed.
- Visual strategy: DECIDED — hand-built SVG via `shared/art.js` + `svg.art` classes, one-accent palette (no AI images for teaching diagrams). Lesson 0.1 fully converted: every diagram slide (4, 6, 7, 10, 11, 12, 14, 17, 18, 22, 23, 25, 32, 33) uses `svg.art`; analogy callouts use line icons (`#i-book`, `#i-building`, `#i-stage`), no emoji. No slide overflows the footer with all steps shown.
