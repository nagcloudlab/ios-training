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
- Lesson 0.1 (iOS Architecture & App Startup): 48 slides. Sources: `decks/lesson-0.1/lesson-0.1.md` (production brief) and `decks/lesson-0.1/lesson-0.1-text.md` (study companion: the full lesson text extended to match the deck part by part; keep it in sync when slides change). Parts follow the text's 7 sections: 1 big picture (app diagram, bundle/process/scene, hotel, layers), 2 the tap (hook, 7-step launch, SpringBoard, cold/warm), 3 process (memory, program/process/thread), 4 where Swift begins (build, dyld, @main), 5 SwiftUI screen (view, tree, first frame), 6 lifecycle (states, scenePhase), 7 practice (LifecycleLab, exercises); Wrap-up (performance, full journey, myths, 11-question review, challenge). All Swift typechecks (Swift 6 mode).
- Lesson 0.2 (iOS App Architecture: Who Does What?): 18 slides, built **only** from `decks/lesson-0.2/lesson-0.2-text.md` (the earlier brief `lesson-0.2.md` is not used). Parts 1–5 = the text's sections: five responsibilities (Check Balance hero + diagram), iOS vs app architecture table, 8-step Check Balance walkthrough (steps 2–8 authored), UIKit vs SwiftUI + live state demo, MVVM in words; then the text's 3 knowledge-check questions and an end slide listing Lesson 0.3 topics. Built by `tools/` (gen02.py + post02_text.py).
- Lesson 0.3 (iOS Application Lifecycle Deep Dive): 27 slides from `decks/lesson-0.3/lesson-0.3-text.md` only; Part 8 adds two short authored snippets (AppDelegate vs SwiftUI App). Parts 1–8 = the text's sections (mall analogy, process vs scene, states, NPay lifecycle simulator, cold/warm, suspension, memory pressure + jetsam, design for termination, UIKit vs SwiftUI); 1 review question (the text's timer question). Text is truncated in Part 8; simulator scenarios 2–5 and memory levels 65/90% are authored. Built by tools/gen03.py.
- Lesson 0.4 (SwiftUI App Lifecycle vs UIKit AppDelegate): 27 slides from `decks/lesson-0.4/lesson-0.4-text.md` only. Parts 1–8 = the text's sections (evolution timeline, AppDelegate flow + code, SceneDelegate windows + code, SwiftUI App + scenePhase, comparison table, 5-event UIKit/SwiftUI map, delegate adaptor, choosing); 4 review questions (Check your understanding); 5 code snippets (BankingApp renamed NPayApp), all typecheck against the iOS SDK. Authored: outcomes, events 1/3/4/5, review answers. Built by tools/gen04.py.
- Lesson 0.5 (Main Thread, RunLoop & Event Handling): 37 slides from `decks/lesson-0.5/lesson-0.5-text.md` only; Parts 1–13 = the text's sections (main thread, process vs thread, RunLoop cycle, 8-step tap journey, blocking + async, main thread vs MainActor, background work, frame budget, rendering pipeline, frame experiment, async vs parallel, what runs where, Instruments); outcomes = the text's final takeaways; 4 review questions. 5 snippets typecheck in context (iOS SDK, Swift 6). Authored: tap steps 1–5/7/8, non-blocking lane, two frame cases, review answers. Built by tools/gen05.py.
- Lesson 0.6 (iOS Memory Architecture & ARC): 41 slides from `decks/lesson-0.6/lesson-0.6-text.md` only; Parts 1–12 = the text's sections (process memory, stack vs heap, struct vs class, ARC counter, strong/weak/unowned, retain cycle, closure cycles, capture experiment, weak vs unowned, leak vs high usage, Xcode tools + 6-step sequence, Timer cycle); 4 review questions; 11 snippets typecheck (Swift 6). Authored: ARC 3→0 sequence, experiment states, review answers. Built by tools/gen06.py.
- Lesson 0.7 (iOS Security Architecture): 27 slides from `decks/lesson-0.7/lesson-0.7-text.md` only (text's PocketBank renamed NPay); Parts 1–9 = the text's sections (least privilege, security layers + airport, sandbox explorer, entitlements + vs permissions table, camera flow, code signing, UserDefaults vs Keychain, Secure Enclave, secure login); 4 review questions. Built by tools/gen07.py.
- **Tables**: show a table whole (no per-row steps); keep any closing callout as the one click.
- Demo deck: component showcase (19 slides). The old multi-colour premium SVG demo was removed.
- Visual strategy: DECIDED — hand-built SVG via `shared/art.js` + `svg.art` classes, one-accent palette (no AI images for teaching diagrams). Lesson 0.1 fully converted: every diagram slide (4, 6, 7, 10, 11, 12, 14, 17, 18, 22, 23, 25, 32, 33) uses `svg.art`; analogy callouts use line icons (`#i-book`, `#i-building`, `#i-stage`), no emoji. No slide overflows the footer with all steps shown.
