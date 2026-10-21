# Unit 00 — iOS Architecture Foundations: Deep Audit

Branch: `slide-rework` · Scope: Lessons 0.1–0.10 (decks, generators, study companions) · Status: **applied 2026-10-21** (all ten lessons; see each `lesson-0.X-text.md` → "Deck changes after the Unit 00 audit"). Open decisions are listed in §7.

Three tracks: **(A) technical accuracy**, **(B) teaching flow & coverage**, checked against the curriculum plan (`complete-ios-mastery-all-units-lessons.md`), and **(C) slide visuals**. Each finding has a priority:

- **P0** — wrong or won't compile; fix before anyone sees it
- **P1** — weakens the unit noticeably (overlap, missing bridge, inconsistency)
- **P2** — improvement / enrichment

---

## 1. Verdict in one paragraph

The unit is broadly correct and the launch → process → main thread → memory → security → network → storage arc is the right spine. The main problems are not factual but structural: **the same ideas are taught 3–4 times** (lifecycle, the Refresh-balance request, token-in-UserDefaults), **lessons don't hand off to each other**, **NPay is inconsistent across lessons** (money type, ViewModel shape, view names), and the decks are **long on dividers and short on practice** — only 0.1 has hands-on work, reviews are ~85 % "No" answers, and there are no recap slides. A handful of technical claims are outdated or wrong (Secure Enclave/Keychain, launch order, Swift 6 Timer code, status-code check). Measured against the curriculum plan, Unit 00 lacks the per-lesson labs and the unit checkpoint. Many "missing" topics belong to later units and need only a forward pointer.

---

## 2. Technical accuracy (Track A)

### P0 — wrong or doesn't compile

| Lesson / slide | Issue | Fix |
|---|---|---|
| 0.7 s19, s26 | Says Keychain items are stored in the Secure Enclave. They are not: the SE protects the class keys and holds P-256 private keys only. | Keychain = encrypted DB protected by keys the SE guards; SE = key operations that never leave the chip. |
| 0.6 s34–35 | Timer example fails under Swift 6: `@Sendable` closure captures a non-Sendable class. | `@MainActor` class + `MainActor.assumeIsolated`, or replace with a `Task` loop. |
| 0.1 s23, s25 · 0.3 s8 | Launch order wrong: scene goes *inactive* → first frame → *active*. | Reorder the stepper and note. |
| 0.8 · 0.10 s12 | `statusCode == 200` | `(200..<300).contains(statusCode)` |
| 0.8 | do/catch around no throwing call (compiler warning). | Make the call throwing or drop the do/catch. |
| 0.5 s19 note | "Fixed refresh rate". ProMotion adapts 10–120 Hz. | Say "up to 120 Hz, adaptive". |

### P1 — misleading or outdated

| Lesson / slide | Issue |
|---|---|
| 0.1 s5 | "Scene: On screen" too narrow — a scene can exist in background / be unattached. |
| 0.2 | ViewModel lacks `@MainActor final class`. |
| 0.3 / 0.4 | UISceneDelegate framed as optional ("may also use"). Apple is making the scene lifecycle mandatory (TN3187, after iOS 26). |
| 0.3 / 0.4 | `scenePhase` in the `App` (aggregate of all scenes) vs in a `View` (that scene) never explained. |
| 0.5 s15 | "MainActor can suspend" — the real lesson is **actor reentrancy** (state can change across `await`). |
| 0.5 s18 | File I/O presented as async; most file APIs are synchronous and block the thread. |
| 0.5 s29 | Missing Swift 6.2: `@concurrent`, `nonisolated(nonsending)` default. |
| 0.6 s11, s37 | Copy-on-write implied for all structs; it's a property of the standard collections (and types that implement it). |
| 0.6 s7 | It's the class *instance* that may be stack-promoted, not "the class". |
| 0.6 s16 | `unowned` traps on access after deinit; `unowned(unsafe)` is undefined behaviour — slide blurs them. |
| 0.6 s31 | Leaks *does* find unreachable cycles; what it misses is still-reachable abandoned memory (use Memory Graph / generations). |
| 0.6 s34 | The run loop retains a scheduled Timer; "the controller holds it" is the misleading half. |
| 0.7 s13 | Missing usage-description string **crashes** the app; after Deny the app can only send the user to Settings. |
| 0.8 | Background URLSession supports upload/download only; user force-quit cancels transfers. |
| 0.8 | "Idempotent" used but never defined (GET/PUT/DELETE yes; POST no; PATCH not guaranteed). |
| 0.9 | `urls(for:).first!` + `appendingPathComponent` → `URL.documentsDirectory.appending(path:)`. |
| 0.9 | Documents is backed up and can be user-visible in Files; app data belongs in Application Support with `.completeFileProtection`. |
| 0.9 | `Decimal` in SwiftData is risky; `@Model` objects are not Sendable. |
| 0.9 | `@State` lives with view identity, not "with the app". |

### Cross-lesson contradictions (P1)

| Topic | Variants found | Standardize on |
|---|---|---|
| Money type | `Decimal`, `Int`, `Int64` minor units, `"balance": 25000` | `balanceMinor: Int64` in model/JSON; format in ViewModel |
| ViewModel declaration | 3 different shapes | `@MainActor @Observable final class DashboardViewModel`, owned via `@State` |
| `scenePhase` placement | App vs View, unexplained | 0.4 owns it, teaches both |
| Launch order | 3 versions | the corrected order above |
| Frame rate | 60 fixed / 120 / unspecified | "60 Hz, up to 120 Hz on ProMotion" |
| Where the statement PDF lives | Documents vs Caches | Caches (re-downloadable) |

---

## 3. Teaching flow & coverage (Track B)

### 3.1 Overlap — the same thing taught repeatedly (P1)

| Concept | Taught in | Owner | Action |
|---|---|---|---|
| App lifecycle states | 0.1 Part 6 (s24–26), 0.3, 0.3 s23–24, 0.4 | **0.3** (process vs scene), **0.4** (`scenePhase`) | Cut 0.1 Part 6 to a one-slide preview; cut 0.3 s23–24 |
| Memory regions (stack/heap) | 0.1 s14–15, 0.6 | **0.6** | Cut from 0.1 |
| "body is a description" | 0.1, 0.2, 0.4 | **0.2** | Others reference it |
| Refresh-balance request walkthrough | 0.1, 0.8 s5–6, 0.8 journey, 0.10 s10 + s12 | **0.8** journey | Cut 0.8 s5–6; merge 0.10 s10/s12 |
| Token in UserDefaults? | 0.7, 0.9, 0.10 ×2 | **0.7** | Later lessons recall it in one line |
| `unowned`, copy-on-write | 0.6 | **Unit 01** (1.5, 1.8) | Defer; 0.6 keeps `weak` only |

### 3.2 Bridges between lessons (P1)

- Openers of **0.3, 0.5, 0.6, 0.7** don't reference the previous lesson. Add a "Last time → today" opener.
- **0.7, 0.8** end slides lack a "Next:" line.
- **0.3** end slide promises content it already covered.
- **0.7 s21** (secure login flow) belongs in **0.8** (it's a network flow using the Keychain).

### 3.3 NPay consistency (P1)

- One amount (**₹25,000**), one action (**"Refresh balance"**), one cast: `DashboardView`, `DashboardViewModel`, `BalanceService`, `balanceMinor`.
- 0.4 uses `ContentView`; 0.3 / 0.5 / 0.6 use non-NPay examples → convert.
- ~10 analogies, some conflicting (hotel, restaurant, mall, airport, AppDelegate-as-manager…). Keep **two spines**: *hotel* for the platform & security boundary, *restaurant kitchen* for inside the process. Drop mall, airport, manager.
- NPay is the course name (user decision). Remaining "PocketBank" mentions in the repo are only "renamed NPay" provenance notes; the curriculum plan file still says PocketBank throughout.

### 3.4 Rule violations (P1)

- Trainer language on slides: **0.6 s27**, **0.5 s31**.
- **0.1 s28** lab table missing the Home Screen row.
- **0.2** claims "no coding" but s14 is a demo.
- **0.3 s2** is an agenda, not outcomes; **0.10** has no outcomes slide.

### 3.5 Practice & assessment (P1 — biggest effectiveness gap)

- Only 0.1 has hands-on work.
- Reviews: ~85 % of answers are "No"; 0.3 has 1 question; every 0.10 item is "Problem: …". Predictable → low retrieval value.
- Recaps live only in speaker notes.

**Per-lesson demo / lab ideas**

| Lesson | Hands-on |
|---|---|
| 0.1 | Bundle tour: Show Package Contents on NPay.app, read Info.plist |
| 0.2 | Refactor a fat view into View + ViewModel + Service |
| 0.3 | Lifecycle lab with `Logger`; run **without the debugger** to see real suspension |
| 0.4 | Predict-the-print-order exercise (App init, scene, onAppear, scenePhase) |
| 0.5 | Breakpoint in a Button action → read the backtrace; Instruments Hangs trace of a blocking call |
| 0.6 | Leaky screen → Memory Graph, fix with `[weak self]`, re-verify |
| 0.7 | Remove `NSCameraUsageDescription` → crash; `codesign -d --entitlements - NPay.app` |
| 0.8 | Mock JSON + Network Link Conditioner (100 % loss, 3G) to drive the failure explorer |
| 0.9 | `xcrun simctl get_app_container` → open the prefs plist → plaintext token |
| 0.10 | "Broken NPay" project with 5 planted architecture bugs to find |

---

## 4. Alignment with the curriculum plan (`complete-ios-mastery-all-units-lessons.md`)

The plan changes how to read the "beyond the texts" ideas. Three constraints from it:

- **Units 0–1 are "concepts plus Swift CLI exercises"**, runnable without Xcode. Native iOS projects start in Unit 02 (2.2 Xcode projects, simulator & previews).
- **Unit 00 deliverable:** "Explain tap-to-first-frame and end-to-end iOS architecture." The checkpoint is "build *or explain* a feature … answer architecture questions."
- **Scope control:** concurrency, security and identity "recur intentionally: first as conceptual foundations, then as implementation". Repetition *across* units is by design. Repetition *inside* Unit 00 (§3.1) is still a problem.

### 4.1 Topics another unit owns: point to it, don't teach it

| Topic I suggested adding | Owned by | In Unit 00 |
|---|---|---|
| Xcode targets/schemes, bundle, signing, LLDB | 2.2, 9.7, 11.1, 11.3 | **No Toolchain lesson.** Keep 0.7's conceptual signing. |
| DI, composition root, a first test | 4.5, 9.2 | One "Coming in Unit 04" line in 0.2 |
| `beginBackgroundTask`, BGTaskScheduler | 10.7 | Forward pointer in lifecycle |
| Deep / universal links, launch from notification | 10.6, 10.8 | One line: "launches don't always start with a tap" |
| Widgets, extensions, App Groups | 10.9 | One line in 0.7: extensions are separate sandboxed processes |
| Privacy manifest, ATT, submission rules | 11.8 | None |
| ATS, certificate trust | 7.6 | One line in 0.8's HTTPS part |
| Keychain accessibility, Secure Enclave APIs | 7.3, 7.5 | Fix the factual error only |
| Data Protection classes, backups | 6.5 | Fix the directory guidance only |
| `@SceneStorage`, state restoration, drafts | 6.9 | Pointer from 0.9's termination-draft part |
| Idempotency, background sessions | 5.1, 5.8 | Define idempotent in one line (the deck already uses the word) |
| Sendable, reentrancy, `@concurrent` | 1.9, 8.4, 8.5 | Correct 0.5 s15 wording; point to 1.9 / 8.4 |
| `unowned`, copy-on-write, ownership | 1.5, 1.8 | Defer, as in §3.1 |
| View identity, `@Observable` ownership | 3.1, 3.2 | Fix the `@State` wording only |
| MetricKit, observability | 9.9, 12.5 | None |
| Accessibility, localization | 2.9, 12.6 | None |

**Proposal: a "Where this goes next" slide in each lesson's wrap-up**, listing the later lessons that build on it (for example, 0.8 → 5.1, 5.2, 5.8, 7.6). This links the unit to the roadmap and replaces the urge to cram topics in.

### 4.2 What Unit 00 still lacks against the plan

| Plan requirement | Current state | Gap |
|---|---|---|
| Each lesson: … **prediction question → practical lab → review** | Predictions and reviews exist; a lab only in 0.1 | **Labs in 0.2–0.10** |
| "Swift CLI exercises" for Units 0–1 | None after 0.1 | Concept labs + small CLI Swift where it fits (below) |
| Unit checkpoint: explain a feature, answer architecture questions | 0.10 has a 5-question review | Add a **checkpoint exercise** with a rubric |
| Deliverable: explain tap-to-first-frame end to end | Spread over 0.1 / 0.5 / 0.10 | One **architecture map** students annotate (V9) |
| "Progressively animated architecture diagrams" | Per-lesson diagrams | The shared NPay map, zoomed per lesson (V9) |
| Server is authoritative; demo logic isn't production | 0.8 "balance ownership" | Recall it in 0.9 (cache vs source of truth) and 0.10 |
| Private internals labelled conceptual | Done (`· conceptual` kickers) | — |
| A Markdown teaching guide per lesson | `lesson-0.X-text.md` for each | Bring them in line with any slide changes |

### 4.3 Labs that fit "concepts + CLI" (no Xcode project required)

Trainer demos in Xcode remain as LIVE DEMO notes. The student work is:

| Lesson | Student lab |
|---|---|
| 0.1 | Order the launch cards (tap → … → first frame); label the NPay bundle contents from a listing |
| 0.2 | Sort NPay responsibilities into View / ViewModel / Service / Model; mark each "who does what" |
| 0.3 | Scenario cards: predict the state after each event (call arrives, Home, memory pressure, relaunch) |
| 0.4 | Map 5 events: AppDelegate / SceneDelegate / SwiftUI `scenePhase` columns |
| 0.5 | **CLI:** predict the print order of sync, `Task`, `await` and `MainActor` code, then run `swift` |
| 0.6 | **CLI:** class with `deinit` + closure cycle; predict which `deinit` prints; fix with `[weak self]` |
| 0.7 | Threat table: for each NPay item, where it lives and what protects it (sandbox, Keychain, entitlement) |
| 0.8 | **CLI:** decode a sample balance JSON with `Codable`; classify status codes and failures |
| 0.9 | Storage chooser: 10 NPay data items → UserDefaults / Keychain / SwiftData / file / cache |
| 0.10 | **Checkpoint:** explain "Refresh balance" end to end on the blank map; peer review with a rubric |

The CLI labs need Swift only (macOS, Linux or Windows), matching the plan's delivery note.

### 4.4 Teaching formats (revised)

- **Running NPay project:** begin in Unit 01 (the plan's Swift Package with Money/Account/Ledger), not Unit 00.
- **Reviews:** distractor multiple choice, predict-the-output, and 1–2 spaced items from earlier lessons. This keeps the plan's "prediction question" without all-"No" answers.
- **Bug hunts** on short snippets (5–8 lines), which the plan's "real code" allows.
- **Accumulating one-page handout:** the NPay map, one region added per lesson. This doubles as the Unit 00 deliverable.
- **Lesson order:** keep the plan's 0.1–0.10 order. The Toolchain lesson and the 0.3+0.4 merge are **withdrawn**; instead give 0.3 and 0.4 clear ownership (§3.1).

---

## 5. Slide visuals (Track C)

### 5.1 Metrics

| Lesson | Slides | Content | Dividers | Diagram | Code | Text-only | Clicks | Notes words | Longest code |
|---|---|---|---|---|---|---|---|---|---|
| 0.1 | 48 | 26 | 9 | 14 | 3 | 5 | 88 | 3169 | 24 |
| 0.2 | 19 | 8 | 6 | 4 | 1 | 2 | 27 | 1061 | 7 |
| 0.3 | 27 | 15 | 9 | 7 | 1 | 6 | 47 | 1571 | 11 |
| 0.4 | 27 | 12 | 9 | 4 | 5 | 2 | 43 | 1121 | 27 |
| 0.5 | 37 | 17 | 14 | 8 | 5 | 3 | 48 | 1790 | 14 |
| 0.6 | 41 | 22 | 13 | 10 | 11 | 5 | 60 | 1923 | 22 |
| 0.7 | 27 | 11 | 10 | 8 | 0 | 2 | 42 | 1294 | 0 |
| 0.8 | 30 | 13 | 11 | 7 | 3 | 2 | 49 | 1310 | 24 |
| 0.9 | 26 | 10 | 10 | 6 | 3 | 1 | 30 | 1190 | 14 |
| 0.10 | 36 | 16 | 13 | 9 | 3 | 4 | 91 | 1567 | 27 |

Snippets over the ~12-line rule: 0.1 (24), 0.4 (27), 0.6 (22), 0.8 (24), 0.10 (27).

### 5.2 Findings

| # | Finding | Priority | Proposal |
|---|---|---|---|
| V1 | **Divider bloat.** 0.10 has 13 dividers for 16 content slides; 0.5 14/37; 0.6 13/41. Plain white "Part N" slides break momentum. | P1 | 4–6 parts per lesson. Divider shows a **part map** (all parts, current one teal, done ones ticked) — doubles as progress and recap. |
| V2 | **No recap slides.** | P1 | One recap slide per part or per lesson: the accumulating NPay diagram with today's layer highlighted. |
| V3 | **Empty vertical space.** Many slides are vertically centred with a small block of content. | P2 | Top-align content under the heading; give diagrams the freed height. |
| V4 | **Plain text-card slides** (0.4 s21, 0.6 s16/s31, 0.7 s11/s17, 0.9 s20). | P2 | Convert each to a diagram, comparison table, or phone mock. |
| V5 | **NPay phone mock underused** — the strongest visual anchor. | P2 | Use it at every lesson open/close and wherever a user action starts a flow (tap Refresh, camera prompt, login). |
| V6 | **Code-heavy 0.6** (11 code slides) and 5 over-long snippets. | P1 | Trim to ≤12 lines with `data-lit` highlights; move full code to LIVE DEMO notes. |
| V7 | **Multi-colour syntax highlighting** clashes with the one-accent palette. | P2 | Navy text, teal keywords, slate comments, one string tone. |
| V8 | **0.10 click count (91)** — highest in the unit for a 16-slide lesson. | P2 | Show tables/diagrams whole where the reveal adds no prediction moment. |
| V9 | **One lesson-wide diagram missing.** Each lesson draws its own boxes; nothing visually ties the unit together. | P1 | A single **NPay architecture map** (device → OS → process → main thread → View/VM/Service → Keychain/Network/Storage) reused in every lesson, zoomed to that lesson's region. This is the "good overview of iOS Architecture Foundations". |

---

## 6. Top 10 (recommended order of work, aligned with the plan)

1. **P0 fixes:** Secure Enclave, Swift 6 Timer, launch order, status codes, do/catch, refresh rate.
2. **Standardize NPay:** money type, ViewModel shape, names, ₹25,000, two analogies.
3. **NPay architecture map** (V9) + part-map dividers (V1) + recap slides (V2). This serves the plan's deliverable and its "progressively animated diagrams".
4. **Cut the in-unit overlaps:** 0.1 Part 6 and s14–15; 0.3 s23–24; 0.8 s5–6; merge 0.10 s10/s12.
5. **Bridges + "Where this goes next" slides** that link each lesson to the later lessons that build on it (§4.1).
6. **Outcomes & rule fixes:** 0.3 and 0.10 outcomes, trainer language, 0.1 s28 row, 0.2 "no coding".
7. **Labs for 0.2–0.10** (§4.3): concept labs + 3 Swift CLI labs.
8. **Better reviews:** distractors, predict-the-output, spaced items.
9. **P1 accuracy items** (§2), fixed in place, with deeper treatment left to the owning unit.
10. **Unit 00 checkpoint** in 0.10: annotate the map and review it against a rubric.

Items 1–6 change existing slides only. Items 7, 8 and 10 add authored content, so they are flagged per the lesson-scope rule.

---

## 7. Open decisions after applying

- **0.5 frame-interval numbers** (16.67 ms / 8.33 ms, 10 ms and 20 ms work cases) are kept: they are interval arithmetic from the lesson text, labelled illustrative, not benchmark claims. Removing them would take out most of Parts 8 and 10.
- **Divider count** stays tied to the text's sections (CLAUDE.md rule); each divider now carries the automatic lesson map, so it works as progress and recap. 0.5 still has 13 parts.
- **0.10** has 11 parts after merging the tap and request stages; the recap lights only the sandbox outline ("one thing teal").
- **0.1** keeps a Part 6 divider with one lifecycle preview slide so the text's 7 sections stay on the lesson map.
- **0.10 stage eight** still uses the text's `TransactionViewModel` name for the memory example.
