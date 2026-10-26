# Unit 3 · Lesson 3.11 — SwiftUI Performance, Lazy Loading & Rendering Internals

NPay iOS Engineering Masterclass · Advanced SwiftUI · Performance Engineering · Incremental Lab
In Lesson 3.10, we improved NPay's accessibility and localization.
Now we face a new engineering challenge.
Imagine NPay has 50,000 transactions. The user opens History, scrolls quickly, and searches for an older payment.
The interface begins to stutter.
Why does this happen, and how do we diagnose it instead of randomly changing code?
Today, we'll investigate SwiftUI's rendering pipeline, eager versus lazy containers, view identity, Observation, unnecessary computations, and Instruments.
Our goal is to make NPay's transaction history efficient while preserving all the features we've built.

## 1. Our NPay performance milestone

Transaction history workload

*(Interactive selector in the original: 100 · 1,000 · 50,000 records.)*

ScrollView + VStack + ForEach

ScrollView + LazyVStack + ForEach

List
Total model records
1,000
Container behavior
Eager layout

A regular VStack processes its children as part of eager layout, potentially creating substantial work for a large collection.
This is a conceptual workload comparison, not a measured benchmark. Actual memory, evaluation count, and frame time depend on the device and content.
Our task is to investigate which container suits NPay, rather than assuming one is always fastest.

## 2. First concept — SwiftUI performance is more than rendering

When NPay feels slow, several different kinds of work could be responsible.
Where performance problems can occur
Application state
Large updates or expensive computations
View evaluation
SwiftUI reevaluates dependent body descriptions
Layout
Views measure and position their content
Rendering
Drawing and compositing visual output
Display presentation
Frames reach the screen
Conceptual pipeline. SwiftUI may combine, skip, or schedule work differently from this simplified sequence.
Important distinction
These three statements are not equivalent:
- A view's body was evaluated.

- The view was laid out.

- Pixels were redrawn on the screen.

SwiftUI can evaluate a view description without requiring a complete visual redraw.
This is why counting body evaluations alone doesn't establish a performance problem.

## 3. First Xcode experiment — eager VStack

Let's create a small performance laboratory.
```swift
import SwiftUI

struct HistoryPerformanceLab: View {
    let transactions = Array(1...10_000)

    var body: some View {
        ScrollView {
            VStack(spacing: 8) {
                ForEach(transactions, id: \.self) { id in
                    Text("Transaction #\(id)")
                        .frame(
                            maxWidth: .infinity,
                            alignment: .leading
                        )
                        .padding()
                }
            }
        }
    }
}

#Preview {
    HistoryPerformanceLab()
}
```
Predict before running
What might happen when the view opens?
VStack is an eager layout container. For a large collection, it can create substantial layout and view-evaluation work.
But ForEach itself isn't necessarily the problem.
The surrounding layout container matters.

## 4. Replace VStack with LazyVStack

Change only one line:
```swift
VStack(spacing: 8)
```
to:
```swift
LazyVStack(spacing: 8)
```
Full example:
```swift
struct HistoryPerformanceLab: View {
    let transactions = Array(1...10_000)

    var body: some View {
        ScrollView {
            LazyVStack(spacing: 8) {
                ForEach(transactions, id: \.self) { id in
                    Text("Transaction #\(id)")
                        .frame(
                            maxWidth: .infinity,
                            alignment: .leading
                        )
                        .padding()
                }
            }
        }
    }
}
```
What changed?
LazyVStack can defer child creation and layout work until content is needed.
It is designed for scrollable collections where not every row needs to participate in layout immediately.
Important nuance
Lazy loading does not mean the entire transaction dataset is loaded lazily.
Our array still contains 10,000 records in memory.
LazyVStack concerns view layout and creation behavior, not automatic database pagination.

## 5. Three different kinds of laziness

This distinction is essential for senior iOS engineering.
Data loading
How many transactions are fetched or stored?
View creation
When does SwiftUI construct row content?
Rendering
Which visible content needs drawing or compositing?
For example, loading 50,000 transactions into an array and displaying them using LazyVStack doesn't eliminate the memory required for those model records.
Later, in Units 5 and 6, we'll introduce API pagination and persistent data fetching.

## 6. List versus LazyVStack

Our NPay History screen currently uses List.
Let's compare.
List    LazyVStack
Built-in scrolling    Usually inside ScrollView
Platform-adaptive row behavior    More custom layout control
Supports swipe actions and selection    Interactions built explicitly
Manages collection presentation    Lazy stack layout
Useful for standard histories    Useful for customized feeds
Which should NPay use?
For our transaction history, List is a good default.
We need transaction selection, potentially swipe actions, accessibility behavior, and large collections.
But we'll measure performance rather than assume it always outperforms every custom layout.

## 7. Behind the scenes — what happens while scrolling?

Lazy transaction history lifecycle
*(Interactive stepper in the original, 6 stages; only stage 1 was shared.)*
1. History opens
The container receives the transaction collection.

Conceptual lazy-container behavior. Exact caching, row lifetime, and reuse strategies are private implementation details.

## 8. View identity — why it matters for performance

Recall Lesson 2.10.
Our transaction model conforms to Identifiable.
```swift
struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}
```
Each transaction needs a stable ID.
But consider this incorrect implementation:
```swift
struct Transaction: Identifiable {
    var id: UUID {
        UUID()
    }

    let title: String
}
```
Every access generates a new identity.
SwiftUI may treat existing rows as entirely different logical elements during updates.
That can cause unnecessary work, lost row state, and unexpected animations.
Correct principle
Identity must represent the logical transaction, not the current rendering attempt.

## 9. Observation — does every state change update every view?

Our NPay application uses @Observable for its store.
Consider:
```swift
@MainActor
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []
}
```
Suppose BalanceCard reads only the balance.
And HistoryScreen reads the transactions.
Modern Observation allows SwiftUI to track relevant property accesses.
This can reduce unnecessary invalidation compared with broad object-level notifications.
But be careful
Observation doesn't guarantee that every unrelated view will never be evaluated.
Parent updates, structural changes, and other dependencies can still cause evaluations.
We should investigate actual behavior.

## 10. Experiment — inspect view evaluations

SwiftUI provides a diagnostic method:
```swift
Self._printChanges()
```
We can use it inside a view's body.
```swift
struct DebugTransactionRow: View {
    let title: String

    var body: some View {
        let _ = Self._printChanges()

        return Text(title)
            .padding()
    }
}
```
What does it show?
It can print information about why SwiftUI considers a view changed.
Important caution
This is a debugging aid, not a public performance metric or production logging strategy.
Do not conclude that a view is slow simply because its body was evaluated.

## 11. Expensive computations inside body

Consider:
```swift
var body: some View {
    let sorted = transactions.sorted {
        $0.date > $1.date
    }

    return List(sorted) { transaction in
        TransactionRow(transaction: transaction)
    }
}
```
This sorting expression executes whenever the body is evaluated.
For a small collection, it may be acceptable.
For a large collection, repeated sorting could become expensive.
Better architectural direction
Move expensive transformations to an appropriate data-processing layer, cache derived results when useful, or have the repository provide already sorted data.
But avoid premature optimization.
For our NPay demo, we'll measure first.

## 12. Understanding sorting complexity

A comparison sort typically has \(O(n \log n)\) complexity.
For 50,000 transactions, the number of comparisons can be substantial.
Illustrative n log₂(n) growth
Relative computational work, not measured runtime.

*(Bar chart in the original: n = 100, 1,000, 5,000, 10,000, 50,000.)*

This is not a timing benchmark.
The actual cost depends on data types, comparator work, hardware, memory behavior, and compiler optimizations.

## 13. Introduce transaction filtering

Let's add a search field to NPay History.
```swift
@State private var searchText = ""

private var filteredTransactions: [Transaction] {
    guard !searchText.isEmpty else {
        return transactions
    }

    return transactions.filter {
        $0.title.localizedCaseInsensitiveContains(
            searchText
        )
    }
}
```
Then:
```swift
List(filteredTransactions) { transaction in
    TransactionRow(transaction: transaction)
}
.searchable(text: $searchText)
```
What's happening?
Every time the search text changes, the filtered collection may be recomputed.
For a small local dataset, this is reasonable.
For large datasets, we may introduce debouncing, background processing, indexed searching, or server-side queries.
We'll study these techniques later.

## 14. Instruments — how to measure real performance

Xcode provides Instruments for profiling.
Open NPay and choose:
Product → Profile
Depending on the Xcode version, available instruments and templates may include:
- Time Profiler

- Allocations

- Leaks

- Animation Hitches

- SwiftUI-related profiling tools

What should we measure?
Metric    Why it matters
CPU usage    Detect expensive computations
Main-thread work    Find UI blocking
Memory allocations    Identify unnecessary memory growth
Animation hitches    Detect dropped or delayed frames
View update activity    Investigate repeated SwiftUI work
Senior engineer principle
Performance engineering should follow this loop:
Observe → Measure → Identify bottleneck → Change one thing → Measure again.

## 15. NPay performance lab — generate 50,000 transactions

Let's create a deterministic dataset for experiments.
```swift
import Foundation

func makeDemoTransactions(
    count: Int
) -> [Transaction] {
    (0..<count).map { index in
        Transaction(
            id: UUID(),
            title: "Demo Transaction \(index)",
            amountPaise: -(index + 1) * 100,
            date: Date().addingTimeInterval(
                -Double(index) * 60
            )
        )
    }
}
```
Why generate data once?
We should avoid creating 50,000 transactions inside body.
That would repeat expensive work during view evaluations.
Instead, generate the dataset when setting up the experiment and retain it in an appropriate state owner.
One important caveat
Generating 50,000 UUIDs and models itself takes time and memory.
When profiling scrolling, separate dataset-generation cost from the cost of displaying and navigating the list.

## 16. Practical experiment — compare three containers

Create a test screen that can switch between:
- ScrollView + VStack

- ScrollView + LazyVStack

- List

Use the same transaction dataset and row design.
Measure startup responsiveness, scrolling smoothness, memory usage, and CPU activity.
What result should we expect?
VStack may become expensive with large collections.
LazyVStack and List are designed to manage larger scrolling collections more efficiently.
But the exact result depends on the view hierarchy and workload.

## 17. Performance and animation

Remember Lesson 3.6.
We added animations to NPay's transaction updates.
But animating thousands of rows at once can create unnecessary work.
For example:
```swift
withAnimation {
    transactions = newTransactions
}
```
If newTransactions contains a large number of structural changes, the animation may become expensive or visually overwhelming.
Better principle
Animate meaningful, localized changes.
Avoid animating massive collection replacements merely because animation is available.

## 18. Xcode debugging checklist

*(Part 1 of the text ends here; Part 2 continues Section 18.)*

---

## Part 2: Performance Lab, Profiling & Senior Engineer Review

NPay iOS Engineering Masterclass · Continuing from Section 18
We've explored SwiftUI's rendering pipeline, VStack versus LazyVStack, List, stable identity, Observation, and expensive computations.
Now let's complete Lesson 3.11 with practical performance experiments and a deeper investigation into why an application can feel slow even when SwiftUI's rendering is efficient.

## 18. Xcode performance lab — continued

We'll use the same NPay transaction dataset to compare three layouts.
NPay performance lab
*(Interactive checklist in the original.)*
Generate 1,000 demo transactions once, outside body
Test ScrollView + VStack
Test ScrollView + LazyVStack
Test List
Repeat using 10,000 transactions
Profile scrolling with Instruments
Compare CPU, allocations, and animation hitches
Record observations before optimizing
Important testing rule
Use the same dataset, row implementation, device, and build configuration for each comparison.
Run each scenario more than once. Prefer profiling a Release configuration on a physical device when investigating production performance.

## 19. Complete runnable performance experiment

Create a new SwiftUI file named HistoryPerformanceLab.swift.
This is a standalone experiment; it doesn't replace your NPay dashboard.
```swift
import SwiftUI

struct HistoryPerformanceLab: View {

    enum Container: String, CaseIterable {
        case eager = "VStack"
        case lazy = "LazyVStack"
        case list = "List"
    }

    @State private var selected: Container = .list

    @State private var records: [Int] =
        Array(0..<10_000)

    var body: some View {
        VStack(spacing: 12) {

            Picker("Container", selection: $selected) {
                ForEach(Container.allCases, id: \.self) { option in
                    Text(option.rawValue)
                        .tag(option)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)

            Group {
                switch selected {

                case .eager:
                    ScrollView {
                        VStack(spacing: 0) {
                            rows
                        }
                    }

                case .lazy:
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            rows
                        }
                    }

                case .list:
                    List(records, id: \.self) { id in
                        PerformanceRow(id: id)
                    }
                }
            }
        }
        .navigationTitle("Performance Lab")
    }

    @ViewBuilder
    private var rows: some View {
        ForEach(records, id: \.self) { id in
            PerformanceRow(id: id)
        }
    }
}

struct PerformanceRow: View {
    let id: Int

    var body: some View {
        HStack {
            Image(systemName: "creditcard")
                .foregroundStyle(.blue)

            Text("Transaction #\(id)")

            Spacer()

            Text("₹250")
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}

#Preview {
    NavigationStack {
        HistoryPerformanceLab()
    }
}
```
How to run
Open the preview, then select VStack, LazyVStack, and List.
Scroll through each version.
For reliable measurements, run the application rather than relying only on Xcode Preview.
What should you expect?
VStack can incur substantial eager layout work.
LazyVStack and List can reduce the amount of child content needed for the visible region.
But don't invent timing results. Record what actually happens on your device.

## 20. Why can the UI freeze even with LazyVStack?

Consider:
```swift
Button("Load Transactions") {

    let records = makeDemoTransactions(
        count: 50_000
    )

    transactions = records
}
```
Suppose makeDemoTransactions takes significant CPU time.
If that work runs synchronously on the main actor, the UI may become unresponsive during generation.
Even if the transaction list uses LazyVStack, the expensive data-generation work can still block interaction.
Behind the scenes
User taps Load
Button action executes
Main actor runs expensive work
50,000 model records generated synchronously
UI work waits
Input handling and presentation can be delayed
Generation finishes
State receives the new collection
SwiftUI updates
The list displays the new records
Senior engineer principle
A lazy view container cannot fix expensive synchronous application logic.
Later, we'll use Swift concurrency to move suitable CPU-bound work away from the main actor while keeping UI updates correctly isolated.

## 21. Understanding frame budgets

A display refreshing at 60 Hz has approximately:
\[ \frac{1000}{60} = 16.67\text{ ms} \]
between refresh opportunities.
At 120 Hz:
\[ \frac{1000}{120} = 8.33\text{ ms} \]
These values are useful reference intervals, not guaranteed CPU budgets for your SwiftUI code.
Display refresh intervals
Time between refreshes
Theoretical intervals at fixed refresh rates

*(Bar chart in the original: 60 Hz, 90 Hz, 120 Hz.)*

If the application performs too much work during a critical update, frames can miss presentation deadlines, producing visible hitches.
Important nuance
SwiftUI layout, rendering, GPU work, and display scheduling involve multiple systems.
You cannot assume the entire frame interval is available exclusively for your code.

## 22. The cost of filtering transactions on every keystroke

Our History screen uses:
```swift
transactions.filter {
    $0.title.localizedCaseInsensitiveContains(searchText)
}
```
For 100 transactions, this is usually inexpensive.
For 50,000 transactions, repeated filtering on every edit may become noticeable.
Let's distinguish two strategies.
Strategy A — Immediate filtering
```swift
.onChange(of: searchText) {
    updateResults()
}
```
Every accepted text change can trigger filtering.
Strategy B — Debounced filtering
Wait until the user has paused typing before performing expensive work.
We'll implement debouncing properly when we cover Swift concurrency.
For now, understand the principle: reduce unnecessary expensive operations, not merely the number of view descriptions.

## 23. Performance diagnosis — choose the correct fix

NPay performance diagnosis
*(Interactive exercise in the original, 4 scenarios; only scenario 1 was shared.)*
History takes a long time to open with 50,000 rows in VStack.

Use a lazy collection container

Add more animations

Generate new UUIDs

## 24. Senior engineer knowledge check

SwiftUI Performance Assessment
*(Interactive quiz in the original.)*

**1. Does LazyVStack automatically paginate backend data?**

Yes

No

**2. Does every body evaluation mean a full pixel redraw?**

Yes

No

**3. What is the main purpose of Instruments?**

Measure application behavior

Generate SwiftUI views

Replace the compiler

**4. Can unstable IDs harm collection performance?**

Yes

No

**5. Can synchronous CPU work block UI responsiveness?**

Yes

No

**6. Should we optimize before measuring?**

Yes

No

## 25. Lesson 3.11 — Final NPay checkpoint

We've completed the conceptual coverage of SwiftUI performance engineering.
You should now understand the differences between eager and lazy containers, data loading and view creation, view evaluation and rendering, stable identity, Observation, main-actor blocking, and performance profiling.
Our NPay History screen can be improved with efficient collection presentation and measured optimizations.
Unit 3 progress
Conceptual lessons covered
11 / 12

Next — Lesson 3.12: Complete Unit 3 NPay Integration & Architecture Review.
We'll consolidate all the features we've built: typed navigation, four tabs, review sheets, payment drafts, animations, reusable components, adaptive layouts, environment-based preferences, accessibility, localization, and efficient transaction history.
We'll also review the complete NPay architecture before advancing to Unit 4 — MVVM and Application Architecture.

## Integration through Lesson 3.11 (authored)

The text ships no complete code for this lesson. The integrated NPay app is the Lesson 3.10 code plus Section 13's search
in the real History screen; everything else is unchanged. The full app, including the 3.10 code, is
`tools/sim3_11/App.swift` (below the "Complete code through Lesson 3.11" marker). The lab code (HistoryPerformanceLab,
PerformanceRow, makeDemoTransactions) stays out of the app, as Section 19 says.

```swift
// Screens/HistoryScreen.swift
struct HistoryScreen: View {
    let transactions: [Transaction]

    @State private var searchText = ""

    // section 13: recomputed when the search text (or the transactions) change
    private var filteredTransactions: [Transaction] {
        guard !searchText.isEmpty else {
            return transactions
        }

        return transactions.filter {
            $0.title.localizedCaseInsensitiveContains(
                searchText
            )
        }
    }

    var body: some View {
        List(filteredTransactions) { transaction in
            NavigationLink(value: NPayRoute.transactionDetails(transaction.id)) {
                TransactionRow(transaction: transaction)
            }
        }
        .searchable(text: $searchText)
        .accessibilityIdentifier(NPayAccessibilityID.transactionList)
        .navigationTitle("History")
    }
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_11.py`, 49 slides) covers Sections 1–25, grouped into 8 Parts: what
"slow" means (1, 2), eager and lazy (3, 4, 5), List and scrolling (6, 7), identity and Observation (8, 9, 10), work
inside body (11, 12, 13, 22), measuring (14, 15, 16, 18, 19), the main actor and frames (17, 20, 21), diagnosis and
NPay (23, 25 and the integration). Then recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5, **Debug build**; app in `tools/sim3_11/`, rerun with
`sh tools/sim3_11/run.sh`; one launch per experiment). Counts come from counters inside row bodies, sorts and filters.
Memory is the process `phys_footprint` read with `task_info`. Frames are `CADisplayLink` callbacks. All of it is
indicative simulator data, not device benchmarks. Instruments was **not** run: the text recommends a Release build on a
physical device.
- Containers, 10,000 records, the Section 19 row. Row bodies on open, then after scrolling to the end, then footprint:
  - VStack: 10,000, then 10,000, ~1 GB.
  - LazyVStack: 15, then 31, ~39–41 MB.
  - List: 9, then 25, ~39–45 MB.
- Identity: 20 rows in a List, then one unrelated parent change. With a stable id, 0 rows appeared again. With
  Section 8's computed `UUID()` id, every visible row appeared again (13–26 onAppear calls per run).
- Observation (Section 9's store, two readers):
  - Appending a transaction ran only the history body.
  - Changing the balance ran only the balance body.
  - Assigning the same balance ran neither.
- `_printChanges`: Section 10's row printed "DebugTransactionRow: @self changed." on first appearance.
- Sort in body plus search over 50,000 records: typing "4999" (4 keystrokes) ran 4 sorts and 4 filters of all 50,000.
- Section 20's synchronous Load: 0 display frames were delivered while the action ran (about 30 per 0.5 s when idle).
  - 50,000 records: action 0.02 s, footprint 37 → 46 MB.
  - Repeated with 500,000: action ~0.2 s, longest frame gap ~0.25 s, footprint 37 → 94 MB.
  - These durations are labelled on the slide as simulator runs.
- Screenshots: the Section 19 lab (List), and the integrated History searching "Coffee".

**Authored (flagged)**
- Every experiment and counter, and the 500,000-record repeat. The instrumented copies wrap the text's code with
  counters, and the slide code stays the text's.
- Section 7: stages 2–6 of the scrolling lifecycle (only stage 1 was shared). The measured scroll counts.
- Section 23: scenarios 2–4 of the diagnosis table (only scenario 1 was shared), drawn from Sections 8, 13/22 and 20.
- The Section 1 workload table's per-size expectations, summarised from the text's own wording.
- Section 12's chart, redrawn from n log₂ n values; Section 21's chart, redrawn from 1000/Hz.
- Section 19 is shown as an excerpt (the container switch) beside a screenshot. The full code is in the notes as a LIVE
  DEMO.
- The integration (History search), the "NPay after 3.11" slide, outcomes, "Where we are", recap, "Where this goes
  next", lab and end slide.
- Review: the text's 6 questions, plus three more:
  - Predict: VStack rows on open; sorts per keystroke.
  - Multiple choice: which body runs on append.
  - Spaced item from 3.10 (is accessibilityIdentifier spoken?).
  - 4 of 10 verdicts are "No".

**Wording**
- "Senior engineer principle / knowledge check" became neutral callouts and "Check your understanding".
