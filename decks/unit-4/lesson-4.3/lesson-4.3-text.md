# Unit 4 · Lesson 4.3 — Swift Observation Framework Internals

NPay iOS Engineering Masterclass · @Observable · @State · @Bindable · Dependency Tracking · Runtime Internals

In Lesson 4.2, we built our first PaymentViewModel using @Observable.

We wrote:
```swift
@MainActor
@Observable
final class PaymentViewModel {
    var recipient = ""
    var amountText = ""
}
```

And SwiftUI automatically responded when the user edited the properties.

But we haven't answered the most interesting question:

How does SwiftUI know which property changed, which view depends on that property, and which part of the interface needs updating?

That's what we'll investigate today.

Our approach remains the same: predict → write Swift → run in Xcode → inspect internals → apply to NPay.

## 1. Our engineering problem

Imagine NPay has three independent areas:
- BalanceCard displays ₹25,000.
- PaymentForm displays the recipient.
- TransactionHistory displays transactions.
All three read the same NPayStore.

Now the user types one character into the recipient field.

Should SwiftUI unnecessarily update the balance and every transaction row?

Ideally, no.
What should update when recipient changes?
Recipient

BalanceCard

₹25,000
Unrelated

PaymentForm

Empty

Reads recipient

History

3 transactions
Unrelated

Input edits: 0. This demonstrates the intended dependency relationships, not actual SwiftUI body-evaluation counts.

Modern Observation makes property-level dependency tracking possible.

Let's discover how.

## 2. First experiment — without Observation

Create an ordinary Swift class.

```swift
import SwiftUI

final class CounterModel {
    var count = 0
}

struct CounterLab: View {
    @State private var model = CounterModel()

    var body: some View {
        VStack(spacing: 20) {
            Text("Count: \(model.count)")

            Button("Increment") {
                model.count += 1
            }
        }
    }
}

#Preview {
    CounterLab()
}
```

Predict
When you tap Increment, will the displayed count reliably update?

No.

The model is an ordinary reference-type object.

```swift
@State stores the reference, but mutating model.count doesn't itself provide SwiftUI with observable property-change notifications.
```

Other unrelated view updates might cause the new value to appear, but that's not a reliable reactive design.

## 3. Add @Observable

Now change only the model:

```swift
import SwiftUI

@Observable
final class CounterModel {
    var count = 0
}
```

Keep CounterLab unchanged.

Run it again.

Now the count should update when the button is tapped.
What changed?
We didn't manually call a refresh function.

We didn't publish a notification ourselves.

We introduced the @Observable macro, which enables the model to participate in Apple's Observation system.

## 4. What exactly is @Observable?

```swift
@Observable is a Swift macro.
```

It isn't a base class.

It isn't an ordinary protocol conformance that you manually implement.

The macro transforms the annotated type at compile time to provide observation support.

Conceptually:
Your Swift source

```swift
@Observable class CounterModel
```

Swift macro expansion

Adds observation tracking machinery

Compiled observable model

Property access and mutation participate in Observation

SwiftUI

Tracks relevant property dependencies

The compiler-generated details are important because they explain why we don't need to write observation notifications for every property.

## 5. Inspect macro expansion in Xcode

Let's investigate the compiler-generated code.

In Xcode, open:
```swift
@Observable
final class CounterModel {
    var count = 0
}
```

Use Xcode's macro expansion command, typically available through the editor context menu or an Expand Macro action.

The exact menu location depends on your Xcode version.

You'll see generated observation-related code.

The details can change between Swift versions, but the expansion commonly involves:
- Backing storage for tracked properties.
- An observation registrar.
- Property access tracking.
- Mutation tracking.
Conceptual expansion
This is intentionally simplified, not a copy of the exact compiler output.

```swift
final class CounterModel {
    private var storedCount = 0

    var count: Int {
        get {
            // Register observation access
            return storedCount
        }

        set {
            // Coordinate observed mutation
            storedCount = newValue
        }
    }
}
```

The real macro expansion is more sophisticated.

The key insight is that ordinary-looking stored properties can become observable through compiler-generated accessors and tracking machinery.

## 6. How does SwiftUI know which property was read?

Consider:

```swift
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var recipient = ""
    var transactions: [String] = []
}
```

Now create two views.

```swift
struct BalanceView: View {
    let store: NPayStore

    var body: some View {
        Text("Balance: \(store.balancePaise)")
    }
}

struct RecipientView: View {
    let store: NPayStore

    var body: some View {
        Text("Recipient: \(store.recipient)")
    }
}
```

BalanceView reads balancePaise.

RecipientView reads recipient.

Observation can track those accesses while SwiftUI evaluates the relevant view descriptions.

When recipient changes, RecipientView has a relevant dependency.

BalanceView doesn't directly depend on recipient.
Important nuance
This doesn't guarantee that BalanceView.body can never be reevaluated for another reason.

Parent updates, identity changes, and other dependencies still matter.

Observation provides more precise dependency tracking, not an absolute prohibition on reevaluation.

## 7. Interactive dependency explorer

Which views depend on the changed property?

BalanceRecipientTransactions

BalanceCard

Reads: balance

PaymentForm

Reads: recipient, balance

HistoryScreen

Reads: transactions

DashboardSummary

Reads: balance, transactions

Check marks indicate direct dependencies in this simplified example, not guaranteed runtime invalidation or rendering events.

## 8. What is ObservationRegistrar?

When you inspect the macro expansion, you may encounter ObservationRegistrar.

This type participates in tracking property access and mutation for observable objects.

Conceptually, an observable model needs to answer two questions:

1. Which observable property is being accessed?
2. When is that property being mutated?

The registrar provides infrastructure for those operations.
Important distinction
ObservationRegistrar doesn't render the UI.

SwiftUI uses observation information to coordinate view invalidation and updates.

Rendering remains a separate framework responsibility.

## 9. How is this different from ObservableObject?

Before the modern Observation framework, SwiftUI commonly used:

```swift
import SwiftUI

final class OldPaymentModel: ObservableObject {
    @Published var recipient = ""
    @Published var amountText = ""
}
```

And a view:
@StateObject private var model = OldPaymentModel()

ObservableObject uses object-level change publishing through Combine's observation mechanisms.

The modern Observation framework can track individual property accesses.
| ObservableObject | @Observable |
|---|---|
| Protocol | Macro-based observation |
| @Published for commonly published properties | Stored properties tracked by macro transformation |
| Object-level change publisher | Property-access dependency tracking |
| @StateObject for owned objects | @State for owned observable objects |
| Combine-oriented mechanism | Observation framework |

Does this mean ObservableObject is obsolete?
No.

It remains useful for existing codebases, compatibility with older iOS versions, and APIs designed around it.

For our iOS 17+ NPay application, we'll continue with modern Observation.

## 10. @State, @Bindable, and @Observable together

These three are often confused.

Let's connect them.

```swift
@Observable
final class PaymentViewModel {
    var recipient = ""
}

struct PaymentScreen: View {
    @State private var viewModel = PaymentViewModel()

    var body: some View {
        @Bindable var viewModel = viewModel

        TextField(
            "Recipient",
            text: $viewModel.recipient
        )
    }
}
```

What does each one do?
| Mechanism | Responsibility |
|---|---|
| @Observable | Makes model properties observable |
| @State | Owns the model reference in SwiftUI state storage |
| @Bindable | Creates bindings to mutable observable properties |

Why don't we use @Binding directly?
@Binding represents a binding to a particular value.

@Bindable provides dynamic binding projections to properties of an observable model.

For example:
$viewModel.recipient

This produces a binding suitable for TextField.

## 11. Observation tracking and computed properties

Suppose our ViewModel contains:

```swift
@Observable
final class PaymentViewModel {
    var recipient = ""
    var amountText = ""

    var isValid: Bool {
        !recipient.isEmpty && !amountText.isEmpty
    }
}
```

The computed property reads two observable stored properties.

When SwiftUI evaluates:
.disabled(!viewModel.isValid)

the getter reads recipient and amountText.

Those underlying accesses can become tracked dependencies.
Why is this useful?
We don't need to maintain a separate isValid stored flag.

The computed property reflects the current source values.

## 12. What about properties that should not be observed?

Not every property belongs in Observation.

Suppose the ViewModel has a logger.

```swift
@Observable
final class PaymentViewModel {
    var recipient = ""

    @ObservationIgnored
    private let logger = Logger(
        subsystem: "com.example.npay",
        category: "Payments"
    )
}
```

For this example, import OSLog to use Logger.
What does @ObservationIgnored do?
It excludes the annotated property from Observation's tracking transformation.

This is useful for implementation details that aren't intended to drive UI updates.
Important nuance
Ignoring a property doesn't automatically make it thread-safe or change its ownership behavior.

It only affects observation participation.

## 13. NPay experiment — count body evaluations

Let's create two child views that read different properties.

```swift
import SwiftUI

@Observable
final class DemoStore {
    var balance = 25000
    var recipient = ""
}

struct ObservationLab: View {
    @State private var store = DemoStore()

    var body: some View {
        VStack(spacing: 24) {
            BalanceDisplay(store: store)
            RecipientEditor(store: store)
        }
        .padding()
    }
}

struct BalanceDisplay: View {
    let store: DemoStore

    var body: some View {
        let _ = Self._printChanges()

        return Text("Balance: \(store.balance)")
    }
}

struct RecipientEditor: View {
    @Bindable var store: DemoStore

    var body: some View {
        let _ = Self._printChanges()

        return TextField(
            "Recipient",
            text: $store.recipient
        )
        .textFieldStyle(.roundedBorder)
    }
}

#Preview {
    ObservationLab()
}
```

Run the experiment
Open the debug console.

Type into the recipient field.

Observe the diagnostic messages.
What should you investigate?
Does RecipientEditor update?

Does BalanceDisplay need to update for the recipient change?

Are there additional updates caused by the parent or text-input system?

Don't assume a fixed number of evaluations. Inspect what your actual Xcode environment reports.

## 14. Observation and performance

Property-level tracking can reduce unnecessary view invalidation.

But it doesn't automatically make every application fast.

Consider:
```swift
var filteredTransactions: [Transaction] {
    transactions.filter {
        $0.title.contains(searchText)
    }
}
```

Even with Observation, this computation can be expensive for large collections.

Observation tracks dependencies.

It doesn't automatically cache arbitrary computed properties or optimize their algorithms.
Senior engineer principle
Observation improves update coordination; it does not replace performance engineering.

## 15. Thread safety and @MainActor

Our real PaymentViewModel uses:
```swift
@MainActor
@Observable
final class PaymentViewModel {
    var recipient = ""
    var amountText = ""
}
```

Why?

Because this ViewModel manages UI-facing mutable state.

Main-actor isolation makes its mutation rules explicit.
Important distinction
```swift
@Observable doesn't automatically make an object thread-safe.
```

Observation and actor isolation solve different problems.
| Observation | Actor isolation |
|---|---|
| Tracks property access and changes | Controls concurrent access |
| Supports reactive UI updates | Helps prevent data races |
| Does not guarantee thread safety | Does not automatically render UI |

We'll explore concurrency and actor isolation in depth in Unit 8.

## 16. Behind the scenes — complete NPay Observation flow

From user input to UI update
*(Interactive stepper in the original, 6 stages; only stage 1 was shared.)*

1. User edits amount

TextField receives new input.

*(Part 1 ends here; Part 2 restarts at Section 16.)*

---

## Part 2: Observation Internals, Debugging & Senior Engineer Review

NPay iOS Engineering Masterclass · Continuing from Section 16

We've investigated how @Observable transforms Swift classes, how SwiftUI tracks property reads, and how @Bindable connects observable models to user input.

Now let's complete the lesson by examining the full observation lifecycle, dependency tracking, nested models, and common engineering mistakes.

## 16. Behind the scenes — complete NPay Observation flow

From TextField input to updated UI
*(Interactive stepper in the original, 6 stages; only stage 1 was shared.)*

1. User edits amount

TextField receives new text through the iOS input system.

PreviousNext step

The important principle
SwiftUI doesn't require you to call:
refreshPaymentScreen()

Instead, the screen declares its dependencies by reading observable properties during view evaluation.

SwiftUI uses that information to coordinate updates.

## 17. Deep concept — observation follows property reads

Let's create a simple observable model.

```swift
import Observation

@Observable
final class NPayMetrics {
    var balance = 25000
    var transactionCount = 10
}
```

Now imagine a view that reads only:
```swift
Text("\(metrics.balance)")
```

It has a dependency on balance.

But another view reads:
```swift
Text("\(metrics.transactionCount)")
```

That view has a different dependency.
Interactive dependency explorer

Change BalanceChange Transaction Count

BalanceCard

Reads balance

Dependent

TransactionCount

Reads transactionCount

Unrelated

DashboardSummary

Reads balance and transactionCount

Dependent

Direct dependency relationships, not guaranteed body-evaluation counts.
What about computed properties?
Suppose:
```swift
var summary: String {
    "\(balance) — \(transactionCount)"
}
```

When a view reads summary, the getter accesses both underlying observable properties.

Those accesses can become tracked dependencies.

This is why computed properties work naturally with Observation.

## 18. Nested observable models

Now let's introduce a more realistic NPay architecture.

Suppose our application has separate models for account and payments.

```swift
import Observation

@Observable
final class AccountModel {
    var balancePaise = 2_500_000
}

@Observable
final class PaymentModel {
    var recipient = ""
    var amountText = ""
}

@Observable
final class NPayAppState {
    var account = AccountModel()
    var payment = PaymentModel()
}
```

A SwiftUI view can read:
appState.account.balancePaise

or:
appState.payment.recipient

What happens behind the scenes?
The property-access chain can involve observations of both the parent reference and the nested observable property.

This supports fine-grained updates across composed models.
Important nuance
Nested Observation is not the same as recursively publishing every property change through the parent.

Dependencies depend on which observable properties are actually accessed.

## 19. Observation does not automatically imply persistence

Suppose we update:
```swift
viewModel.recipient = "ravi@npay"
```

The interface responds.

But does the value automatically get saved to disk?

No.

Observation is about tracking changes.

Persistence is about storing data durably.
| Mechanism | Responsibility |
|---|---|
| @Observable | Tracks observable changes |
| @State | Owns state in the SwiftUI hierarchy |
| @Bindable | Exposes mutable bindings |
| SwiftData | Persists structured local data |
| UserDefaults | Persists simple preferences |
| Keychain | Stores appropriate secrets securely |

We'll introduce persistent repositories in Unit 6.

## 20. Common mistake — creating ViewModels inside body

Consider:

```swift
struct PaymentsScreen: View {
    var body: some View {
        let viewModel = PaymentViewModel()

        return TextField(
            "Recipient",
            text: Binding(
                get: { viewModel.recipient },
                set: { viewModel.recipient = $0 }
            )
        )
    }
}
```

This is a poor ownership design.

Every time the body is evaluated, the expression can construct another ViewModel.

The user's draft may be lost, and the model's lifetime becomes difficult to reason about.
Better approach
```swift
@State private var viewModel = PaymentViewModel()
```

Or receive a ViewModel created by a stable parent.

Remember: ViewModel ownership is a lifecycle decision, not merely a syntax choice.

## 21. Common mistake — confusing Observation with thread safety

Consider:
```swift
@Observable
final class PaymentViewModel {
    var amountText = ""
}
```

The macro makes the model observable.

It does not automatically serialize concurrent mutations or prevent data races.

For UI-facing state, use appropriate actor isolation.

```swift
import Observation

@MainActor
@Observable
final class PaymentViewModel {
    var amountText = ""
}
```

Now access to the ViewModel is governed by main-actor isolation.
Important distinction
Observation answers: What changed?

Actor isolation answers: Who may access or mutate this state, and under what concurrency rules?

These are independent concerns.

## 22. Debugging Observation in Xcode

Let's create a small experiment.

```swift
import SwiftUI

@MainActor
@Observable
final class ObservationDemo {
    var balance = 25000
    var recipient = ""
}

struct ObservationDebugLab: View {
    @State private var model = ObservationDemo()

    var body: some View {
        VStack(spacing: 20) {
            BalanceDebugView(model: model)
            RecipientDebugView(model: model)
        }
        .padding()
    }
}

struct BalanceDebugView: View {
    let model: ObservationDemo

    var body: some View {
        let _ = Self._printChanges()

        return Text("₹\(model.balance)")
    }
}

struct RecipientDebugView: View {
    @Bindable var model: ObservationDemo

    var body: some View {
        let _ = Self._printChanges()

        return TextField(
            "Recipient",
            text: $model.recipient
        )
        .textFieldStyle(.roundedBorder)
    }
}

#Preview {
    ObservationDebugLab()
}
```

Run the experiment

1. Open the preview.
2. Open the debug console.

3. Type ravi@npay.
4. Observe the diagnostic messages.

5. Add a button to modify balance.
6. Compare which views report changes.

What should you learn?
SwiftUI can track different observable dependencies for different views.

But _printChanges() is a debugging aid, not a guaranteed rendering or performance measurement.

## 23. Observation and performance — when is it useful?

Imagine NPay's dashboard has many components.
NPayStore

Observable state

BalanceCard

Reads balance

PaymentForm

Reads draft

HistoryList

Reads transactions

Profile

Reads preferences

Property-level tracking can help SwiftUI avoid invalidating unrelated views solely because another property changed.

But performance still depends on layout complexity, expensive calculations, collection identity, and main-thread work.

Observation is one optimization mechanism, not a replacement for profiling.

## 24. Senior engineer knowledge check

Observation Engineering Assessment

*(Interactive quiz in the original.)*

**1. What does @Observable primarily provide?**

Property observation support

Database persistence

Automatic thread safety

**2. Does @Observable automatically save values to disk?**

Yes

No

**3. Can a computed property participate in Observation dependencies?**

Yes

No

**4. Why avoid constructing ViewModels inside body?**

Unstable ownership and possible state loss

Because classes cannot be initialized there

Because SwiftUI prohibits all local variables

**5. Does @MainActor serve the same purpose as @Observable?**

Yes

No

**6. Does every observed mutation necessarily cause a full-screen redraw?**

Yes

No

**7. Can different views track different properties of the same observable model?**

Yes

No

Lesson 4.3 — Final checkpoint
We've completed the conceptual coverage of Apple's Observation framework, including macro expansion, property-access tracking, computed dependencies, nested observable models, ViewModel ownership, @ObservationIgnored, actor isolation, and debugging.

Our NPay architecture now has a clearer reactive model:

User Input → Binding → Observable ViewModel → Dependency Tracking → SwiftUI Update.
Unit 4 progress

3 of 10 lessons covered

30%

Next — Lesson 4.4: Dependency Injection in iOS. We'll learn constructor injection, protocol-based dependencies, composition roots, environment injection, and how to replace NPay's demo payment service with a mock implementation for testing—without changing the SwiftUI screen.

## Integration through Lesson 4.3

No change to NPay's code: the text applies Observation concepts to the 4.2 app. The evidence app
(`tools/sim4_3/App.swift`) compiles the 4.2 NPay unchanged next to the labs.

## Deck changes

The deck (`index.html`, built by `tools/gen4_3.py`, 43 slides) has 8 Parts:
1. Why Observation (sections 1, 2, 3).
2. Inside the macro (4, 5, 8).
3. Dependencies follow reads (6, 7, 13, 22, 17).
4. ObservableObject (9).
5. Owning and binding (10, 20).
6. Computed, ignored, nested (11, 12, 18).
7. What Observation isn't (14, 15, 19, 21, 23).
8. The full flow, in NPay (16).

Then recap, review, next, lab and end. Part 2 restarts at Section 16; Part 1's unfinished Section 16 is covered by Part 2's.

**Evidence**
- **Section 5:** the real expansion, from `swiftc -Xfrontend -dump-macro-expansions` (Swift 6.3.3), condensed on the slide:
  - `_$observationRegistrar`, `@ObservationTracked`, `_count`;
  - `get` → `access(keyPath:)`; `set` → `shouldNotifyObservers` + `withMutation(keyPath:)`;
  - `extension CounterModel: nonisolated Observation.Observable`.
  - For Equatable values `shouldNotifyObservers` is `lhs != rhs`.
- **Section 12:** `recipient` gets `@ObservationTracked`; the `@ObservationIgnored` logger gets nothing.
- **NPay's PaymentViewModel:** `recipient`, `amountText`, `errorMessage` tracked; `let store` and computed properties are
  not.
- **Sections 15/21 (full compile, Swift 6):**
  - Two tasks writing a plain `@Observable` class → "passing closure as a 'sending' parameter risks causing data races…"
    (not reported by `-typecheck`).
  - With `@MainActor` → "main actor-isolated property 'amountText' can not be mutated from a nonisolated context".
  - With `await MainActor.run` → compiles.
- **Simulator** (`sh tools/sim4_3/run.sh`):
  - Sections 2–3: a plain class reaches count 3 while the screen shows "Count: 0"; with `@Observable`, "Count: 3"
    (screenshots).
  - Section 13: typing "ravi" printed `RecipientEditor: \DemoStore.recipient changed.` ×4 and no BalanceDisplay lines.
  - Section 22: `\ObservationDemo.recipient` ×9 for "ravi@npay"; `\ObservationDemo.balance` ×2 for two ₹100 taps (the
    button is ours).
  - Section 9 (ours): the same lab with ObservableObject/@Published printed `_store changed` for **both** views on every
    change (×5 each).
  - Section 17: balance → Balance + Summary; transactionCount → Count + Summary; same value → nothing.
  - Section 11: with an empty recipient, setting `amountText` re-ran the Continue button **0** times (`&&`
    short-circuit), then `recipient` → 1.
  - Section 18:
    - Changing `recipient` → only the payment view; changing `amountText` (read by no view) → none.
    - Changing `balancePaise` → only the account view.
    - Replacing `account` / `payment` with new instances → only the view that reads it.
  - Section 12: an ignored `var note` changed with no body run (screen stale) until a tracked property changed.
  - Section 20: typing "ravi" created 4 ViewModels while the field showed "ravi". One unrelated parent update (button
    ours) blanked the field.

**Renamed in the evidence app** (names clash with NPay): section 2's plain class is `PlainCounterModel`; section 20's
screen and ViewModel are `BodyViewModelScreen` / `LabPaymentViewModel`, with a `tick` parameter so the lab's parent can
re-render it.

**Authored (flagged)**
- The ObservableObject comparison lab, the body counters, the scripted edits, and the extra rows: same value, unread
  property, model replacement, ignored `var`.
- Section 1's diagram; the section 4 cards.
- Section 16: stages 2–6 of the flow (only stage 1 was shared).
- The race example for section 21.
- Review: the text's 7 questions (options reordered) plus three more:
  - two predict items (plain counter, short-circuit);
  - a spaced item from 4.2.
  - 3 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab, end slide.

**Not used**
- The conceptual expansion of section 5, replaced by the real compiler output.
- The interactive dependency explorers (sections 1, 7, 17), replaced by measured counts.
- The section 6 two-view example is taught with section 13's runnable version.

**Snippets:** every slide snippet typechecks. The section 21 race example compiles only with `-typecheck`; a full
compile reports the data-race error, which is its point.

**Wording**
- "Senior engineer principle / knowledge check" became neutral labels and "Check your understanding".
