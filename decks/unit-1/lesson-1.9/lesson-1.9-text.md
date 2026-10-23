# Unit 1 · Lesson 1.9 — Swift Concurrency Masterclass

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). The text as shared **stops partway through Section 11** (the lost-update example ends at "NEXT"). The
> request that came with it asked for actors, MainActor, Sendable and data races as well; those parts of the deck are
> authored and listed under "Deck changes" at the end.

Request: Start Lesson 1.9: Teach Swift concurrency deeply using PocketBank, including async/await, Tasks vs threads, structured concurrency, async let, task groups, cancellation, actors, MainActor, Sendable and data races, with incremental visuals, examples and trainer notes.

Unit 1 · Lesson 1.9 — Swift Concurrency Masterclass
Swift Language Mastery · Senior Developer & Trainer Edition · PocketBank Case Study

Today we'll explore one of the most important areas of modern iOS engineering: Swift Concurrency.

This lesson connects what we learned about threads, RunLoop, SwiftUI, ARC, and networking.

Our central question is:

How can PocketBank perform multiple operations simultaneously without freezing the interface or corrupting shared data?

We'll learn in a story-driven sequence, starting with a simple problem and gradually introducing async/await, Tasks, structured concurrency, cancellation, actors, and Sendable.

## 1. The problem — PocketBank's slow dashboard

Imagine a user opens PocketBank. The dashboard needs three pieces of information:

- Account balance — 2 seconds
- Recent transactions — 3 seconds
- Customer profile — 1 second

These are illustrative network durations.

If we execute the operations sequentially, the user waits for all three.

(Sequential execution timeline: Balance, Transactions, Profile; 0 seconds → 6 seconds. Total elapsed time: approximately 6 seconds. Assumes independent operations, fixed durations, and negligible processing overhead.)

Can we improve this? Yes. If the operations are independent, we can initiate them concurrently.

## 2. Concurrency versus parallelism

Before writing code, understand these two terms.

Concurrency means multiple tasks can make progress during overlapping periods.

Parallelism means multiple computations are actually executing at the same instant.

(Concurrency / Parallelism toggle. One execution resource, interleaved work: A B A B A B. Tasks take turns progressing. They need not execute simultaneously.)

**Trainer analogy.** Imagine a chef preparing two dishes. Concurrency: One chef alternates between dishes while one is cooking. Parallelism: Two chefs work on different dishes simultaneously.

Swift Concurrency supports organizing concurrent work. Whether execution is parallel depends on scheduling, isolation, and available resources.

## 3. Threads versus Tasks

This is one of the most important distinctions.

- **Thread** — Operating-system execution resource. Has execution state and a stack; scheduled by the OS.
- **Swift Task** — Language-level unit of asynchronous work. Can suspend and later resume on an appropriate executor.

A Swift task is not permanently assigned to one operating-system thread.

When a task suspends at an asynchronous operation, its thread can execute other work.

Task A starts executing → Task A reaches await and suspends → Thread becomes available for other work → Task A resumes when the awaited operation completes

**Trainer rule:** Never teach Task {} as equivalent to creating a new thread.

## 4. Why async/await exists

Consider a network request. The application sends a request, then waits for the server. During that wait, the CPU doesn't need to continuously execute instructions for the request.

Traditional synchronous code might block a thread. Modern asynchronous APIs allow the calling task to suspend.

```swift
func fetchBalance() async throws -> Int {
    try await Task.sleep(for: .seconds(2))
    return 25000
}
```

Let's understand the keywords. async means the function can suspend. await marks a potential suspension point. throws means the function can fail. try acknowledges a possible thrown error.

**Important distinction.** await does not necessarily mean a network request or delay is happening. It marks a call to asynchronous functionality that may suspend.

## 5. How async/await keeps the UI responsive

Imagine a SwiftUI button:

```swift
Button("Load Balance") {
    Task {
        do {
            let balance = try await fetchBalance()
            print(balance)
        } catch {
            print(error)
        }
    }
}
```

The button action creates a task. The task calls the asynchronous function. When Task.sleep suspends, the executing thread is free to handle other work.

(Blocking versus suspension: Async suspension / Blocking sleep. Task can suspend. The asynchronous task waits without monopolizing the executing thread. The main thread can remain responsive.)

**Trainer insight.** async does not automatically make CPU-heavy work safe. An asynchronous function can still contain expensive synchronous computation that blocks the executor on which it runs.

## 6. Sequential await versus concurrent async let

Now return to our three PocketBank API requests.

Sequential:

```swift
let balance = try await fetchBalance()
let transactions = try await fetchTransactions()
let profile = try await fetchProfile()
```

The second call starts only after the first completes. The third starts after the second.

If they are independent, use async let.

```swift
async let balance = fetchBalance()
async let transactions = fetchTransactions()
async let profile = fetchProfile()

let dashboard = try await (
    balance,
    transactions,
    profile
)
```

These child tasks can progress concurrently.

(Compare dashboard loading strategies: Sequential / Concurrent. Balance, Transactions, Profile. Illustrative total duration 3 seconds. Assumes independent requests, ideal overlap, and negligible overhead. Actual performance depends on network and server behavior.)

**Why only 3 seconds?** Because the longest operation takes 3 seconds. When independent requests overlap perfectly, total duration is approximately the duration of the slowest operation rather than the sum.

## 7. Structured concurrency

Now we reach the architectural principle behind modern Swift concurrency.

Structured concurrency means child tasks belong to a defined parent scope. Their lifetimes and error propagation are governed by that structure.

Parent Task — Load Dashboard → Balance, Transactions, Profile → Parent scope completes after children finish

**Why does this matter?** Structured concurrency makes it easier to reason about task lifetimes, cancellation, and error propagation. A parent task cannot simply abandon unfinished structured child tasks when leaving their scope. This is different from launching unrelated work with no clear ownership.

## 8. Task groups — dynamic concurrency

async let works well when the number of concurrent operations is known.

What if PocketBank needs to fetch balances for a dynamic list of accounts? We can use a task group.

```swift
func fetchAllBalances(
    accountIds: [String]
) async throws -> [Int] {

    try await withThrowingTaskGroup(of: Int.self) { group in

        for id in accountIds {
            group.addTask {
                try await fetchBalance(for: id)
            }
        }

        var balances: [Int] = []

        for try await balance in group {
            balances.append(balance)
        }

        return balances
    }
}
```

fetchBalance(for:) is an application-specific async function that we would implement separately.

**Important behavior.** Task-group results are collected in completion order, not necessarily the order in which tasks were added. If order matters, include an index or identifier in each result and reconstruct the intended ordering.

**Trainer question.** Should we always launch thousands of network requests simultaneously? No. Real systems need concurrency limits, rate-limit awareness, resource management, and backpressure.

## 9. Task cancellation

Imagine the user opens the transaction-history screen. A network request begins. Before it finishes, the user navigates away.

Should the application always continue the work? Not necessarily.

Swift tasks support cooperative cancellation.

```swift
func loadTransactions() async throws {
    try Task.checkCancellation()

    let transactions = try await fetchTransactions()

    try Task.checkCancellation()

    print(transactions)
}
```

Task.checkCancellation() throws CancellationError if the current task has been cancelled.

**Key principle.** Cancellation is cooperative. Requesting cancellation does not forcibly stop arbitrary synchronous code. The task or the asynchronous APIs it calls must respond appropriately.

## 10. SwiftUI .task and lifecycle-aware work

SwiftUI provides the .task modifier.

```swift
struct TransactionView: View {

    var body: some View {
        Text("Transactions")
            .task {
                await loadTransactions()
            }
    }

    func loadTransactions() async {
        // Perform asynchronous loading.
    }
}
```

SwiftUI manages the task's lifecycle in relation to the view. When the view disappears, SwiftUI can cancel the task.

But remember: cancellation is cooperative, so application code and called APIs must handle it appropriately.

This is often preferable to creating long-lived unstructured tasks without a clear ownership strategy.

## 11. What is a data race?

Now let's explore the problem that concurrency can introduce.

Suppose two tasks modify the same account balance simultaneously. Both read ₹25,000. Task A adds ₹5,000. Task B subtracts ₹3,000.

If updates are not synchronized, one task may overwrite the other's work.

(Interactive lost-update example. Initial balance ₹25,000. Task A: reads ₹25,000, calculates ₹30,000. Task B: reads ₹25,000, calculates ₹22,000. Both tasks have read the same initial value. Stored balance … NEXT)

*(text ends here as shared)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_9.py`) follows this text, with these changes.

**Structure**
- 8 Parts: the slow dashboard and concurrency vs parallelism (1–2); tasks, threads and async/await (3–4); responsive UI (5); async let and structured concurrency (6–7); task groups (8); cancellation and `.task` (9–10); data races and actors (11 + authored); MainActor and Sendable (authored). Kickers name the text section or say "authored".
- The text stops inside Section 11. Actors, MainActor and Sendable — requested together with the text — plus the recap, review, "Where this goes next", lab and end slide are authored.

**Real measurements instead of simulators** (macOS, 18 cores, `Task.sleep` standing in for the network)
- Sequential dashboard **6.2 s**, `async let` **3.2 s**.
- **10,000** tasks each waiting 1 s finished in **1.08 s** (tasks are not threads).
- **40** tasks each *blocking* 1 s took **3.0 s** (blocked tasks hold pool threads); Swift 6 refuses `Thread.sleep` in async code ("class method 'sleep' is unavailable from asynchronous contexts").
- Task group: added NP1001 (3 s), NP1002 (1 s), NP1003 (2 s) → returned NP1002, NP1003, NP1001.
- Cancellation 0.2 s in → `CancellationError`.
- Lost update: 1,000 concurrent ₹1 deposits on unprotected state → ₹25,598 and ₹25,578 instead of ₹26,000 (one run correct); with an `actor`, ₹26,000 every run.
- Real Swift 6 errors: sharing a class across child tasks ("passing closure as a 'sending' parameter risks causing data races…"), a global mutable var ("not concurrency-safe"), mutating a `@MainActor` property from a nonisolated context.

**Corrections and canon**
- PocketBank → NPay. Balance in paise (`Int64`, 2,500,000). Button "Load Balance" → "Refresh balance". `TransactionView` → `TransactionHistoryView`. Task-group results carry the account id so the order can be rebuilt (the text's version returned bare `Int`s).
- The chef analogy is kept and tied to the course's restaurant-kitchen analogy.
- "Trainer rule/insight/question" became callouts.

**Authored additions (flagged)**
- Outcomes, "Where we are" (bridge to 1.8's export task and 1.6's Sendable), recap.
- Actors: `actor Account` with `deposit`, the measured fix, reentrancy pointer (8.4).
- `@MainActor @Observable DashboardViewModel` with `refresh()`; Sendable table (value types, actors, immutable final classes, not-Sendable classes) and the explanation of Lesson 1.6's `BalanceProviding: Sendable`.
- Review: 8 questions (Task vs thread, async let duration, task-group order, cancel semantics, async and CPU work, which prevents lost updates, MainActor from nonisolated code, and a spaced item from 1.8).
- "Where this goes next": 1.10, 8.1, 8.2, 8.3, 8.4, 8.5.
- Swift command-line lab "Measure NPay's dashboard".
- End slide: "Next: Lesson 1.10 — NPay Domain Model, Actor Ledger & Tests".
