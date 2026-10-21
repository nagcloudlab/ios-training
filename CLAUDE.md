# iOS Training — Slide Deck Engine

## What this is
A slide deck engine for a 130-lesson iOS development training course (13 units, 10 lessons each). PocketBank is the running example app throughout.

## Architecture
- `shared/deck.css` — Design system: 50+ CSS components, animation system, 1280x720 canvas scaled to fit, print styles, reduced-motion support
- `shared/deck.js` — Slide engine: keyboard/touch navigation, step-by-step reveal, Swift syntax highlighting, speaker notes (S key), slide overview (O key), fullscreen (F key)
- `decks/<lesson>/index.html` — Each deck is just HTML content + two shared imports. Zero build step.

## Design rules
- **Palette**: Navy (#0f172a) + Teal (#0d9488) + White. Orange (#ea580c) for rare emphasis only.
- **Fonts**: DM Sans (body/headings) + IBM Plex Mono (code) via Google Fonts
- **All slides white** except `.slide.title` and `.slide.end` (navy background)
- **Cards**: prefer `.card.accent` (teal left border). Avoid rainbow-colored cards.
- **Diagrams**: use CSS components (`.flow`, `.vflow`, `.layers`) — keep simple, max 2 accent colors
- **Teaching pattern**: predict -> reveal -> explain -> connect. Question first, answer on `.step` reveal.
- **Student-facing only**: no trainer language ("Ask your participants", "Trainer Moment", etc.) in slide content
- **Speaker notes**: `<aside class="notes-src">` inside each slide with SAY/ASK/EXPECT/CONNECT labels

## Key components
- `.step` — incremental reveal on click
- `.flow` / `.vflow` — horizontal/vertical flow diagrams with `.box` and `.arrow`
- `.flow-anim` / `.vflow-anim` / `.layers-anim` — animated sequential reveal
- `.cw` > `.ch` > `.cb` — code window with traffic-light dots, filename, auto Swift highlighting
- `.predict` / `.answer` — teaching Q&A pattern
- `.analogy` / `.misconception` / `.takeaway` / `.rule` / `.tip` / `.warn` — callout types
- `.card.accent` — standard content card with teal left border
- `.layers` > `.layer` — stacked architecture diagram
- `.tbl` — clean data table
- `.anim-*` — entrance animations (triggered when `.step.shown`)

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
- Lesson 0.1 (iOS Architecture & App Startup): 26 slides, all 10 acts, speaker notes throughout
- Demo decks: component showcase (19 slides) + premium SVG demo (6 slides)
- Visual strategy for diagrams/images: pending user decision (AI images vs improved CSS approach)
