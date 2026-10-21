# Lesson 0.5 — Main Thread, RunLoop & Event Handling

*iOS Architecture Mastery · Foundation Series* (Parts 1–14, including "Part 2: Rendering, Concurrency & Performance")

> Lesson text as shared; the deck (`index.html`) uses only this text. The banking app is **NPay**. "Trainer"
> material became speaker notes; the trainer questions and the knowledge check became the review.
> **Authored for the deck** (flagged): event-journey steps 1–5, 7 and 8 (the text shows only step 6, "State
> changes"); the non-blocking timeline lane; the 20 ms at 60 Hz and 10 ms at 120 Hz frame cases (the text shows
> 10 ms at 60 Hz); review answers and traps. Section 8 of the text breaks off at "animation or"; its Instruments
> content continues in section 13.

**Question:** When a user taps a button on an iPhone, how does that touch become Swift code, and how does the screen change?

## Outcomes (the lesson's final takeaways)
The main thread handles critical UI work · a RunLoop supports event-driven execution · touch events travel through iOS and UI frameworks before reaching Swift code · SwiftUI responds to state with declarative view updates · blocking the main thread damages responsiveness · Swift concurrency tasks and OS threads are different · performance must be measured, not guessed.

## 1. The main thread
A restaurant with one receptionist: they receive customers and coordinate service; if they start cooking a complicated meal, customers wait. The receptionist is the main thread.
User interface (touch, scroll, text input, navigation) → main thread (tap, layout, UI update) · background execution (networking, file I/O, expensive computations). UIKit requires its UI APIs on the main thread; SwiftUI has main-actor isolation requirements for UI state and updates.
**Rule:** keep the main thread responsive; no expensive synchronous work in button actions or UI callbacks.

## 2. Process versus thread
A process is the app's execution environment; a thread is a path of execution within it. NPay process → main thread (UI events, rendering coordination), other threads (system and app work), shared resources (heap, loaded code, open files, network resources). Threads share the address space; each has its own stack and scheduling state. **An asynchronous Swift task is not a thread**; tasks may suspend without blocking an OS thread.

## 3. What is a RunLoop?
A mechanism that lets a thread wait for and process work: input events, timers, scheduled callbacks. The main thread's run loop takes part in event processing. Cycle: wait for work → receive an event → dispatch the callback → return to waiting. (The real Core Foundation RunLoop has modes, input sources, observers, timers and dispatch-queue integration.) It can only process events when execution returns to it, so a blocking callback stalls other main-thread work.

## 4. Follow a button tap (8 steps)
1. *Authored:* Touch — the touchscreen detects the contact. 2. *Authored:* iOS delivers an event to the app. 3. *Authored:* the main run loop picks it up. 4. *Authored:* the framework hit-tests the control. 5. *Authored:* your Button action runs on the main actor. 6. **State changes** — SwiftUI's state-tracking machinery detects that UI-relevant information changed. 7. *Authored:* SwiftUI evaluates, reconciles and lays out views. 8. *Authored:* the new frame is displayed.
Deliberately simplified: a SwiftUI Button does not read raw touchscreen events; the OS and frameworks do.

## 5. Why blocking the main thread freezes an app
```swift
Button("Load Report") {
    Thread.sleep(forTimeInterval: 3)
    reportLoaded = true
}
```
The action runs on the main actor; `Thread.sleep` blocks for three seconds and other main-thread work cannot proceed (illustrative timeline: blocked 0–3 s, free after). Use asynchronous APIs instead:
```swift
Button("Load Report") {
    Task {
        isLoading = true
        do {
            let report = try await reportService.load()
            currentReport = report
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}
```
`await` lets the task suspend without blocking the main thread. **Nuance:** async does not move CPU-intensive work off the main actor.

## 6. Main thread versus MainActor
| Main thread | MainActor |
|---|---|
| Operating-system thread | Swift concurrency global actor |
| Executes UI event processing | Serializes access to main-actor-isolated code |
| Exists at runtime | Enforced through Swift's actor isolation model |
| Can be blocked by synchronous work | Can suspend at await points |
| Used by UIKit | Commonly used for SwiftUI UI-related state |

Mental model: MainActor is a concurrency isolation mechanism that coordinates main-thread-bound work.
```swift
@MainActor
@Observable
class BalanceViewModel {
    var balance: Decimal = 0

    func updateBalance(_ newBalance: Decimal) {
        balance = newBalance
    }
}
```
`@MainActor` provides isolation, not speed.

## 7. Background work — not all work is the same
Asynchronous I/O (wait without occupying a thread) · CPU-bound parallel work (needs CPU away from the main actor) · iOS background execution (allowed after leaving the foreground, under system policies). An async task does not mean iOS lets it continue after suspension.

## 8. Rendering pipeline and frame budget
At 60 Hz one refresh interval is about 16.67 ms; at 120 Hz about 8.33 ms. The app does not get the whole interval: the system also needs time for layout, rendering and compositing. Missing the deadline causes stutter or dropped frames.

## 9. How an iPhone draws a screen
NPay balance ₹5,000 → ₹6,000: state changes → SwiftUI evaluates views → reconciliation → layout → graphics rendering → display. `body` is a description of UI, not a drawing function; recomputing it does not mean every element is redrawn.

## 10. Why frames drop
10 ms of work at 60 Hz fits within the 16.67 ms interval (other system work still needs time). *Authored:* 20 ms at 60 Hz and 10 ms at 120 Hz miss the deadline. Avoid expensive synchronous main-thread work, minimize unnecessary UI computation, measure before optimizing.

## 11. Async versus parallel execution
Downloading a profile is mostly waiting (asynchronous I/O); processing a million records is mostly computing (CPU-bound).
```swift
func fetchProfile() async throws -> Data {
    let url = URL(string: "https://example.com/profile")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}
```
```swift
@MainActor
func calculateTotal() async -> Int {
    var total = 0
    for number in 1...10_000_000 {
        total += number % 7
    }
    return total
}
```
The second is async but does synchronous CPU work on the main actor with no suspension point. **async enables suspension; it does not guarantee a background thread.**

## 12. What should run where?
| Work | Preferred approach |
|---|---|
| Button handling | Main actor |
| UI state changes | Main actor or appropriate SwiftUI isolation |
| HTTP request | URLSession async API |
| Expensive image processing | Non-main-actor execution |
| Large data transformations | Appropriate background executor or parallel processing |
| Saving persistent data | Storage API with suitable concurrency |
| Scheduled work after app backgrounding | Approved iOS background APIs |

Background thread execution and iOS background-mode execution are different concepts.

## 13. Measure with Xcode Instruments
Time Profiler (CPU time) · Hangs (unresponsive periods) · Allocations · Leaks · SwiftUI profiling tools where supported. Method: show a slow app, measure, make a targeted change, measure again.

## 14. Check your understanding
1. Does every SwiftUI body evaluation redraw the entire screen? **No.**
2. Does async automatically mean background-thread execution? **No.**
3. Most likely to freeze the UI: awaiting URLSession data, `Thread.sleep` on the main thread, or a small `@State` update? **Thread.sleep on the main thread.**
4. Does `@MainActor` make a slow calculation faster? **No** — isolation, not acceleration.

**Next: Lesson 0.6 — iOS Memory Architecture & ARC:** stack vs heap, structs vs classes, reference counting, strong and weak references, retain cycles, memory leaks.

## Deck changes after the Unit 00 audit

The deck (`index.html`, built by `tools/gen05.py`) now differs from the text above as follows. Items marked *authored* are not in the original text.

**Corrections**
- Main thread vs MainActor table: "MainActor can suspend at await points" became "code waiting at `await` lets other main-actor work run first", plus a line on **actor reentrancy** (state can change across `await`; re-check it), pointing to Unit 08 · 8.4.
- Three kinds of work: asynchronous I/O now means **network** requests. Most file APIs (`Data(contentsOf:)`, `write(to:)`) are synchronous, so large reads and writes stay off the main actor.
- Frame budget: the display does not refresh at a fixed rate. It is 60 Hz, or up to 120 Hz on ProMotion displays, which adapt their rate.
- Where work runs: a one-line pointer to Swift 6.2's `@concurrent` and `nonisolated(nonsending)` (Units 01 · 1.9, 08 · 8.1). Concept only. *Authored.*
- No trainer language: the Instruments method now reads "Reproduce the slow path, measure, one targeted change, measure again".

**Consistency (NPay canon)**
- Analogy: the receptionist became the course's restaurant-kitchen analogy. The main thread is the head chef who plates every dish, the RunLoop is the order rail, and a frame is a dish sent out each tick.
- Examples are NPay throughout: the "Refresh balance" button (blocking and async versions), `DashboardViewModel` (`@MainActor @Observable final`, formatting `balanceMinor` paise as INR), `fetchBalance()` from `api.npay.example`, `totalSpent` over a million transactions, and a balance change from ₹25,000 to ₹24,750.
- "body is a description" is labelled as a recall from Lesson 0.2, which owns that idea.

**Added** (*authored*)
- "Where we are" slide: the shared NPay map (Main thread lit), with a Last time (0.4) / Today bridge.
- LIVE DEMO in Part 4: a breakpoint in the Refresh balance action, reading the main-thread backtrace (run loop → event dispatch → SwiftUI → closure).
- Recap slide (map + three points).
- Review: five questions with mixed verdicts — multiple choice (what freezes the UI: B, `Thread.sleep`), predict-the-output (1, 2, 3 with a new `Task`), async ≠ background (No), reentrancy (Yes), and a spaced review from 0.2 (`body` redraw: No).
- "Where this goes next": 1.9, 3.9, 8.1, 8.4, 8.7.
- Lab, "Predict the print order": a Swift command-line exercise. With `await`, it prints A, C, B, D, E; with a blocking call it prints A, C, D, B, E. Both versions were compiled and run under Swift 6; the full starter file is in the notes.
- The end slide names the next lesson: Lesson 0.6 — iOS Memory Architecture & ARC.
