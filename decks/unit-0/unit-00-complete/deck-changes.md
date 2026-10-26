# Unit 00 complete deck: changes from Lessons 0.1–0.10

One full-day, code-free deck (142 slides) built by `tools/gen0_all.py` from the ten Unit 00 decks, which are unchanged. Focus: iOS architecture only; Swift code starts in Unit 01.

## Structure
Title → Outcomes → "One day with NPay" (0.10) → "Ten Parts, one app" → Parts 1–10 → Wrap-up → End.
Each Part: divider (lesson map) → content → recap (the source lesson's three takeaways as cards, without the NPay map; user: simplify) → two "Check your understanding" questions (user decision: questions after every Part instead of one review section).

| Part | Topic | Source |
|---|---|---|
| 1 | The big picture | 0.1 Part 1, 0.2 |
| 2 | From tap to first frame | 0.1 Parts 2–6 + wrap-up (incl. the launch myths) |
| 3 | The app lifecycle | 0.3 |
| 4 | Hearing lifecycle events (SwiftUI only) | 0.4 |
| 5 | Main thread & rendering | 0.5 |
| 6 | Memory & ARC | 0.6 |
| 7 | Security | 0.7 |
| 8 | Networking | 0.8 (+ 0.10's UI = f(state)) |
| 9 | Data storage | 0.9 |
| 10 | End to end | 0.10 |
| Wrap-up | Where this goes next, checkpoint + rubric (0.10) | |

## Removed
- All Swift code slides (about 35), the Swift reading kit (0.1), the code labs (0.5, 0.6, 0.8) and the per-lesson labs.
- Per-lesson title, outcomes, "Where we are", "Where this goes next" and end slides (one set for the whole day instead).
- Duplicates in 0.10: launch in seven steps, the tap simulation, active-to-terminated table, the entry point, the request and ownership recalls; "Ten connected lessons".
- LIVE DEMO notes (they wrote code). JSON and HTTP message windows are kept: they show data, not code.
- 0.3's "One process, several scenes": Part 1's added slide ("Why a scene is separate from the process") teaches it; Part 3 keeps the hotel-suite analogy as the reminder.
- 0.1's "Measure, don't guess" (user request).
- 0.3's "NPay through five moments" (user decision): the two-track slide walks the same moments.
- Part 4 (user: SwiftUI only): 0.4's UIKit slides (delegate flow, two windows, UIKit vs SwiftUI comparison, event map, which approach when) and the AppDelegate question (replaced by 0.4's App-level scenePhase question); the recap's UIKit line reworded.
- 0.5's "Main thread vs MainActor" (user: actors appeared without introduction; Unit 01 · 1.9 teaches them). Elsewhere "main actor" now reads "main thread".
- 0.5's "Waiting vs computing" (Part 5 re-check): "Three things called background" already contrasts waiting and computing.
- Part 6 audit: 0.6's "Not simply stack versus heap" (a Swift-compiler nuance before values and objects are introduced) and the "strong vs weak vs unowned" table (unowned is Unit 01 · 1.8).

## Redrawn without code (authored)
- MVVM for a balance screen (0.2): code windows → three role cards.
- Where NPay's own code begins (replaces 0.1's @main slide): entry point → App → Scene → root view, one plain caption per click, then three takeaways (once per launch; one window, one scene; still a description).
- **Blocking vs non-blocking waits** (0.5's "One action that freezes the app"): rebuilt as the user's view: two phones pressing Refresh balance, blocking wait (taps get no response, main thread blocked 3 s) vs non-blocking wait ("Updating…", still scrolls, main thread free), then the answer arriving on the non-blocking phone (₹24,750, "updated"); rule "Same 3-second wait. Only where it happens decides whether the app freezes."
- Where do values live? (0.6): code → a worded example.
- Two objects that never let go (0.6): code → four bullets; fix worded.
- A ViewModel in the request path (0.8): code → the ViewModel's four duties.
- UI = f(state) (0.10, moved to Part 8): the Swift type removed, the JSON kept.
- Where an app keeps its files (0.9): code column removed.

## Added at the user's request
- Part 1, after "Installed app ≠ running process ≠ scene": **Why a scene is separate from the process**: iPhone (one process, one scene) vs iPad (one process, two scenes; A active, B in the background), plus three points.
- Part 1, **iOS platform layers, and what each does for NPay** (0.1's layer stack): a "What it does for NPay" column per layer; the opening sentences became a closing callout ("NPay asks through Apple's APIs; iOS decides").
- Part 1, **iOS architecture vs your app's architecture** (0.2): the original table paired unrelated items row by row (Operating system / View, Kernel / ViewModel …); rewritten so each row compares one aspect (who designs it, what it organises, main parts, can you change it, NPay example). The Lesson 0.2 deck still has the old table.
- Part 2, **SpringBoard handles the tap** (0.1): three numbered cards, one per click, each lighting its part of the drawing (SpringBoard → NPay not started → launch coordinator / process alive?).
- Part 2, **The compilation pipeline** (0.1): the teal moves through the six stages with one NPay caption per step; the Mach-O internals list is replaced by three points (compiled ahead of time, signed, ships in NPay.app).
- Part 2, **dyld: the dynamic loader** (0.1): four clicks walk the teal down the drawing (executable → dependencies → map + bind → app entry) with a numbered card each, then the "never compiles" callout.
- Part 2, **From view values to a screen** (0.1): code-style labels (`Text("NPay")`, `VStack` …) replaced by plain words (Window, Dashboard screen, Vertical stack, Title, Label, Balance, Button).
- Part 2, **The first-frame journey** (0.1): one stage per click with an NPay caption, then the main-thread lane, then the takeaway; an NPay phone beside the caption builds up per stage (inactive window → description → all new → layout boxes → drawn screen → active); the `body` line removed.
- Part 2, **After the first frame, iOS decides** (0.1): one numbered card per click beside the state diagram (inactive, active, background, suspended, terminated) and a closing rule; the demo table, the process/scene footnote and the Swift code in the notes removed.
- Part 2, **What a cold launch costs** (0.1): the table (two rows identical in both columns) replaced by two lanes, cold launch (5 steps) vs warm activation ("already done" + 2 steps), then two cards: a cold launch rebuilds memory; what slows the first frame. Kicker marked illustrative; no timing numbers.
- Part 3, **NPay's suite in the hotel** (0.3): the analogy now carries the states: two rooms (Balance, Transfer) whose lights show scene phases (on active, dimmed inactive, off background), and what management can do to the whole suite (locked = suspended, cleared = terminated); one key line per click, then "Rooms have lights: scene phases. The suite can be locked or cleared: process conditions."
- Part 3, **Scene states vs process conditions** (0.3): the two lists redrawn as two tracks over six NPay moments, revealed one moment per click with a teal band on the current one, then a bracket "same scene phase, different process condition" over Home Screen / Minutes later (scene phase: inactive → active → inactive → background → background → none; process: running … running briefly → suspended → terminated), then the "Watch the words" rule.
- Part 3, **Each transition, and what NPay should do** (authored; replaces 0.3's "A typical single-scene iPhone app", which repeated Part 2's preview and the two-track slide): six cards, one per click (launch, inactive, background, suspended, terminated, return), each with what NPay should do, then the design rule "Save as you go. Never wait for a goodbye."
- Part 3, **Coming back to NPay** (0.3): two phones show what the user finds after returning with a half-typed ₹1,500 transfer: process survived (all in memory) vs process ended (rebuilt from the saved draft + a fresh balance, the orange only from that click); closing design goal "looks the same either way".
- Part 3, slides on the device, background modes, memory pressure and jetsam (0.3): NPay put into the examples (NPay suspended as the teal app; "Messaging and NPay terminated"); a third card "NPay needs neither" on background capabilities; jetsam's definition shortened and its four points said in NPay terms.
- Part 4 (user: focus on SwiftUI): divider lead "How a SwiftUI app hears what iOS decides"; 0.4's UIKit-to-SwiftUI timeline replaced by **How a SwiftUI app hears lifecycle events** (authored; a first flow-diagram version was found confusing): three phones, one per click: NPay on screen (scenePhase active → refresh the balance), Notification Center pulled down (inactive → pause time-sensitive work), Home Screen (background → save the draft, hide the balance); then "one value, scenePhase; no suspended".
- Part 4, **scenePhase in a View vs in the App** (0.4): redrawn as an iPad with one NPay process and two windows (balance on screen, transfer in the background); clicks show window A's view reading active, window B's view reading background, the App reading active; the table replaced by two cards (read in a View: this window only; read in the App: all windows combined).
- Part 5, **The main thread is the head chef** (0.5): redrawn as two lanes over time (main thread = head chef, background = prep cooks): a Refresh balance tap, scrolling and frames on the main thread; the fetch handed to the back; the result returned to show ₹24,750; one caption per click; the analogy box folded into the lane labels and notes.
- Part 5, **What is a RunLoop?** (0.5's "The RunLoop cycle", rebuilt after the user found it unclear): one full-width drawing: the loop on the left (Sleep → Event → Run code → again) and, on the right, the same loop unrolled as the main thread over time, their teal moving together; a one-line definition above; then the main thread as a timeline: sleeping, woken by a Refresh tap (NPay's code runs), sleeping, a scroll and a timer, sleeping; then the slow case (Refresh blocks 3 s, a new tap waits); rule "wait → handle → wait: the next event runs only when your code returns".
- Part 5 audit: **One tap, eight steps** rebuilt as three owner lanes (iOS, NPay's main thread, SwiftUI) with one NPay caption per click; **Main thread vs MainActor** cut to three plain rows (what it is, who enforces it, NPay example); **Three things called "background"** in NPay examples (waiting, computing, after the user leaves); the rendering slide rebuilt as **From ₹25,000 to ₹24,750** (one stage per click with an NPay phone: only the balance and a new Coffee row are reconciled and redrawn; takeaway "only what changed is redrawn"); **Where each kind of work belongs** as NPay tasks, the Swift 6.2 code footnote removed; the two review questions reworded without API names.
- Part 5 re-check: Swift-concurrency terms that had not been introduced removed (the threads slide's "a task is not a thread" callout → NPay's own threads; "async task" in the background rule; "await/async" in the recap; "suspends" for a download in a question, since "suspended" means a paused app in Part 3).
- Part 5, **One refresh, one deadline** (0.5): redrawn as NPay's list scrolling against the display's ticks over a tenth of a second: 60 Hz ticks, a frame per tick, 120 Hz (twice the ticks, half the time), then one late frame repeating the old picture (stutter); kicker illustrative.
- Part 5, **Does the work fit the frame?** (0.5): the three timing cases (repeating the deadline slide) replaced by NPay work on 60 Hz frames: scrolling fits; sorting 50,000 transactions on the main thread misses three frames; the sort on another thread lets every frame fit and shows the sorted list when ready; rule "Too big for one frame? Move it off the main thread." Illustrative.
- Part 6 audit: **What lives where in NPay's memory** (each region with what NPay keeps there, one per click, then the kitchen analogy); **Copied vs shared** replaces the Swift struct-vs-class table, drawn with NPay's phones (the ₹1,500 payment copied to the Review screen, the form edited to ₹2,000 while the copy keeps ₹1,500; Home and History phones sharing one Account object that a payment changes once, both showing ₹24,750); **Counting strong references** as an NPay story (Home holds the account: 1; the payment sheet too: 2; the sheet closes: 1, still alive; sign out: 0, freed by ARC); **Strong and weak references** as an NPay story (Home holds the account strongly; a balance banner points weakly; sign-out frees the account and the banner's link becomes empty; unowned removed); **A closure that holds on** explains a closure in plain words instead of `[weak self]`; **Three memory tools** simplified from a 4-column table to three cards (Memory Graph, Allocations, Leaks: one question and one NPay example each) plus the "Leaks only finds unreachable memory" warning; deinit/nil/instance/capture wording made plain; recap and questions without Swift keywords.
- Part 6 re-audit: **Two objects that never let go** redrawn with NPay's own objects (the account holds its card, the card points back; sign-out leaves both alive; a weak back-link frees both) instead of person/apartment; **Leak vs high usage** in plain words; **Where do values live?** diagram labelled with NPay values (amount, fee, total on the stack; Account, transaction list, DashboardViewModel on the heap); recap card "Copied vs shared".

## Authored frame
Title, outcomes, agenda, ten Part dividers, end slide, and their notes. References to "Lesson 0.x" now name the Part; spaced-review stems name the Part.

## Review questions (two per Part)
0.1#35, 0.2#20 · 0.1#37, 0.1#42 · 0.3#27, 0.3#29 · 0.4#27, 0.4#29 · 0.5#35, 0.5#39 · 0.6#37, 0.6#39 · 0.7#23, 0.7#26 · 0.8#27, 0.8#30 (spaced, Part 5) · 0.9#24, 0.9#28 · 0.10#32, 0.10#35. No code questions; 4 of 20 are "No".
