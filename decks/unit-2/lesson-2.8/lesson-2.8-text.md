# Unit 2 · Lesson 2.8 — @State and Reactive UI

> Lesson text as shared, in two parts (Sections 1–11, cut off at the end of Section 11; then "Part 2: State
> Ownership, Identity & NPay Integration", Sections 12–18 and the final checkpoint). Interactive widgets are
> described in brackets. The deck (`index.html`, built by `tools/gen2_8.py`) follows Sections 1–18. Simulator
> evidence and authored additions are listed at the end under "Deck changes".

NPay iOS Engineering Masterclass · From Swift Value Semantics to SwiftUI State Management

We're restarting Lesson 2.8 completely, using our established learning method: **Build → Predict → Observe → Investigate → Experiment → Integrate.**

Today, we'll understand one of SwiftUI's most important concepts: @State. By the end, you should be able to explain how SwiftUI manages mutable state, why a view struct can be recreated without losing its state, and how a variable change becomes a visible screen update. We'll start with a small experiment and then integrate it into our existing NPay application.

## 1. The problem — our NPay balance cannot change

Until Lesson 2.7, our balance card contained `Text("₹25,000")`. The amount is hardcoded. But a payment application needs to display changing information.

Our new requirement: **When the user taps Add Demo ₹1,000, NPay should update its displayed balance immediately.** [Conceptual demonstration: the balance card with "Add Demo ₹1,000" and "Reset" — no real money is transferred.] Notice that the text changes automatically when the balance changes. How can we achieve this in SwiftUI?

## 2. Experiment 1 — Try a normal Swift variable

Replace ContentView.swift temporarily with:

```swift
import SwiftUI

struct ContentView: View {
    var balance = 25000

    var body: some View {
        VStack(spacing: 20) {
            Text("Balance: ₹\(balance)")

            Button("Add ₹1,000") {
                balance += 1000
            }
        }
    }
}
```

**Predict.** Will this compile? — Yes, because balance is declared with var / **No, because the button action cannot mutate the view's stored property in this context.** Correct. The code fails because the action cannot mutate an ordinary stored property of the view value.

**Why does it fail?** Remember Unit 1 — Swift structs have value semantics. For a normal struct, `var account = Account(balance: 25000); account.balance += 1000` works because account is mutable. But a SwiftUI view's body is a nonmutating computed property. The escaping button action cannot mutate an ordinary stored property of the view value. You may see an error such as: `Left side of mutating operator isn't mutable: 'self' is immutable`.

**Key insight.** A SwiftUI view struct is primarily a description of UI, not a mutable controller object.

## 3. Experiment 2 — Introduce @State

Change only one line: `var balance = 25000` → `@State private var balance = 25000`. Now the complete code:

```swift
import SwiftUI

struct ContentView: View {
    @State private var balance = 25000

    var body: some View {
        VStack(spacing: 20) {
            Text("Balance: ₹\(balance)")
                .font(.title)

            Button("Add Demo ₹1,000") {
                balance += 1000
            }
            .buttonStyle(.borderedProminent)
        }
    }
}

#Preview {
    ContentView()
}
```

Run it in Xcode. Tap the button. The balance increases. What changed? We didn't call a function to refresh the UI. We didn't manually replace a label. We simply updated a property. SwiftUI handled the interface update.

## 4. What exactly is @State?

@State is a SwiftUI property wrapper. It provides a way for a view to own local mutable state that participates in SwiftUI's update system.

| Part | Meaning |
|---|---|
| `@State` | SwiftUI property wrapper |
| `private` | Limits access to the declaring scope |
| `var` | Mutable property |
| `balance` | Property name |
| `25000` | Initial value |
| Inferred type | Int |

The underlying wrapper type is conceptually `State<Int>`. But how does a property wrapper work? Let's investigate using pure Swift.

## 5. Behind the scenes — property wrapper transformation

```swift
@propertyWrapper
struct NonNegative {
    private var storage: Int

    var wrappedValue: Int {
        get { storage }
        set { storage = max(0, newValue) }
    }

    init(wrappedValue: Int) {
        storage = max(0, wrappedValue)
    }
}

struct Account {
    @NonNegative var balance = 25000
}

var account = Account()
account.balance = -500

print(account.balance) // 0
```

**What does Swift do?** The compiler transforms property-wrapper syntax into backing storage and accessors. Conceptually:

```swift
struct Account {
    private var _balance =
        NonNegative(wrappedValue: 25000)

    var balance: Int {
        get { _balance.wrappedValue }
        set { _balance.wrappedValue = newValue }
    }
}
```

This is a teaching approximation of the compiler transformation.

**Connect to @State.** When we write `@State private var balance = 25000`, Swift uses property-wrapper mechanisms to expose the wrapped value. But SwiftUI's State wrapper does something additional: it integrates with framework-managed state storage and dependency updates.

## 6. The big mystery — where is @State stored?

This is the most important concept of the lesson. Remember `struct ContentView: View`. A struct is a value type. SwiftUI can recreate view values during normal updates. Yet the balance doesn't reset to ₹25,000 each time. Why? Because SwiftUI associates state storage with the view's identity.

[View value versus persistent UI state: ContentView value (may be recreated) → SwiftUI state-management machinery (associates storage with view identity) → balance = 26000 (survives normal view reevaluations while identity is maintained). Conceptual model.]

**Trainer analogy.** Think of a view as a form template. SwiftUI can recreate the form description. But the current values entered into the form are maintained separately in associated state storage. Recreating the description doesn't automatically reset those values.

**Important distinction.** @State is not durable persistence. It does not automatically save data to disk. If NPay terminates, the value is not guaranteed to survive. We'll learn persistence later.

## 7. What happens when balance changes?

[NPay — state update pipeline, a 6-stage stepper; only stage 1 was included: "User taps Add Money — iOS input infrastructure delivers the interaction." Conceptual SwiftUI update flow.]

**Key mental model.** UI = f(State). The interface description depends on current state. When state changes, SwiftUI updates the presentation as needed.

## 8. Does SwiftUI recreate the entire screen?

Not necessarily. A state change may cause relevant view descriptions to be reevaluated. But view evaluation is different from physical rendering. [Observe which content changes: NPay / ₹26,000 / Send · Request · History — the balance content changes while other displayed information remains the same.]

**Important distinction.** View initialization ≠ body evaluation ≠ layout ≠ rendering. SwiftUI can manage these stages independently.

## 9. Xcode investigation — observe body evaluation

```swift
var body: some View {
    let _ = Self._printChanges()

    return VStack(spacing: 20) {
        Text("₹\(balance)")

        Button("Add Money") {
            balance += 1000
        }
    }
}
```

Run the application. Tap Add Money. Observe the Xcode debug console. `Self._printChanges()` can help identify why SwiftUI is evaluating the view's body.

**Trainer question.** If the console shows multiple body evaluations, does that mean the entire screen was redrawn multiple times? No. The diagnostic concerns view updates, not a one-to-one count of display frames.

## 10. Integrate @State into our existing NPay application

We already have: NPay header; BalanceCard; Send, Request and History buttons; reusable QuickAction component. We'll change only the parts needed for state-driven balance updates.

**Step A — Make BalanceCard receive a balance.** Previously `struct BalanceCard: View { var body: some View { Text("₹25,000") } }`. Change it to:

```swift
struct BalanceCard: View {
    let balance: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Available Balance")
                .font(.subheadline)

            Text(
                balance,
                format: .currency(code: "INR")
                    .precision(.fractionLength(0))
            )
            .font(.largeTitle.bold())

            Text("NPay Demo Account")
                .font(.caption)
        }
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(24)
        .background(
            .blue,
            in: RoundedRectangle(cornerRadius: 20)
        )
    }
}
```

Notice that BalanceCard doesn't own mutable balance state. It receives a value from its parent.

**Step B — Let ContentView own the state.** Add `@State private var balance = 25000`. Then replace `BalanceCard()` with `BalanceCard(balance: balance)`.

**Step C — Add the button.** Below the balance card, add:

```swift
Button("Add Demo ₹1,000") {
    balance += 1000
}
.buttonStyle(.borderedProminent)
```

Now NPay updates the displayed balance automatically.

## 11. State ownership — a foundational architecture decision

Why does ContentView own the state instead of BalanceCard? Because ContentView coordinates the button and the balance display. [ContentView owns @State balance → BalanceCard reads balance; Add Money button changes balance.]

This is an example of one-way data flow. The parent owns the state and supplies values to child views. Actions cause state changes, which drive new UI descriptions. We'll explore two-way bindings in Lesson [text cut off here]

## Part 2: State Ownership, Identity & NPay Integration

We've established that ContentView owns the balance using @State, while BalanceCard receives it as a read-only value. Now we'll finish Lesson 2.8 by investigating how SwiftUI preserves state, what causes state to reset, and how to debug state-driven updates.

## 12. The complete NPay implementation

(Code: the complete `ContentView.swift` — `ContentView` with `@State private var balance = 25000`, `VStack(spacing: 24)` with the header, `BalanceCard(balance: balance)`, the "Add Demo ₹1,000" button (`.borderedProminent`) and the `HStack(spacing: 12)` of three `QuickAction`s printing their names; `BalanceCard` as in Step A; `QuickAction` as in Lesson 2.7; `#Preview`. It runs in `tools/sim2_8/App.swift`.)

**Expected behavior.** Run NPay using Command + R. Each tap on Add Demo ₹1,000 should increase the displayed balance by ₹1,000. The other three actions should continue printing messages in Xcode's debug console.

## 13. Why doesn't @State reset when body runs again?

Suppose we tap Add Money three times. The balance becomes ₹28,000. SwiftUI may reevaluate ContentView.body. Why doesn't `@State private var balance = 25000` reset the balance? Because 25000 is the initial value used when SwiftUI establishes the state for that view identity. It is not an instruction to assign 25000 every time body is evaluated.

[View recreation versus state preservation: "Add ₹1,000"; "View description may be recreated"; "Simulate new state identity". Conceptual simulation of state lifetime, not the actual SwiftUI runtime.]

**Trainer analogy.** Imagine a hotel room. The room's sign can be replaced, but the guest's belongings remain associated with the room. Similarly, SwiftUI can recreate a view description while preserving the state associated with that view's identity.

## 14. When does @State reset?

State is tied to view identity. If SwiftUI treats a view as a different identity, its local state can be initialized again.

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 16) {
            Text("Count: \(count)")

            Button("Increment") {
                count += 1
            }
        }
    }
}
```

Now use it inside a parent:

```swift
struct IdentityExperiment: View {
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            CounterView()
                .id(identity)

            Button("Replace Identity") {
                identity = UUID()
            }
        }
    }
}
```

**Experiment.** Run the preview (`#Preview { IdentityExperiment() }`). Tap Increment several times. Then tap Replace Identity. The counter should reset.

**Why?** Changing `.id(identity)` gives SwiftUI a different explicit identity for CounterView. The previous local state is no longer associated with the new view identity.

**Senior engineer insight.** Avoid assigning a new random `.id(UUID())` during every body evaluation. It can cause unnecessary state resets and view replacement.

## 15. What does $balance mean?

`balance` accesses the wrapped value. `$balance` accesses the projected value, which for @State is a `Binding<Int>`. [@State balance → SwiftUI-managed state; balance → Int value; $balance → Binding<Int>.] We'll use this in the next lesson to let a child view edit state owned by its parent.

## 16. Debugging @State in Xcode

Add a breakpoint to `balance += 1000`. Run NPay and tap Add Money. When Xcode pauses, inspect the current value. You can also use the LLDB console: `po balance`. Depending on the current debug context and compiler optimization, LLDB may be able to evaluate the property.

**Another experiment.** Add `let _ = Self._printChanges()` inside ContentView.body. Observe the debug console when the state changes. Remember: body evaluation is not equivalent to a full-screen redraw.

## 17. Important architecture decision — should NPay's real balance use @State?

For our current demo, `@State private var balance = 25000` is appropriate because we're learning local UI state. But in a real payment application, the authoritative balance would come from a trusted backend system. A production architecture might look like: trusted backend (authoritative account balance) → networking service (fetches authenticated balance data) → ViewModel / application state (manages loading, errors and displayed data) → BalanceCard (displays the current balance).

The client must not treat a locally incremented balance as a real financial transaction. We'll introduce networking, secure authentication, and proper domain models in later units.

## 18. Senior engineer knowledge check

1. What is @State? — **A SwiftUI property wrapper** / A database / A background thread
2. Does @State automatically persist across app termination? — Yes / **No**
3. Can a view struct be recreated while its @State survives? — **Yes** / No
4. What can happen when a view's identity changes? — **Its local state may reset** / The entire iOS process must restart
5. What does $balance provide for @State? — **A Binding<Int>** / A second independent Int / A database connection
6. Should a production payment balance be changed only by incrementing local @State? — Yes / **No**

(Answers in bold were not marked in the shared text, apart from Experiment 1's prediction; they follow from the lesson.)

**Lesson 2.8 — Final checkpoint.** NPay now has a state-driven demo balance, while the Send, Request and History buttons remain functional. You should be able to explain why @State works with a Swift struct, how SwiftUI preserves state across normal view updates, why identity matters, and how a state change becomes a visible UI update.

**Next — Lesson 2.9: @Binding and Two-Way State Communication.** We'll create a separate NPay balance editor and investigate how a child view can modify state owned by its parent without creating a second independent copy.

## Deck changes

The deck (`index.html`, built by `tools/gen2_8.py`, 37 slides) follows Sections 1–18 (both parts), grouped into 8 Parts:
the problem (1), a normal variable (2), @State (3–4), property wrappers (5), where state lives (6, 13), from change to
screen (7–9, 16), state in NPay (10–12, 17), identity and $balance (14–15); then recap, review (18), next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_8/`, rerun with `sh tools/sim2_8/run.sh`;
buttons activated through accessibility, as in 2.7)
- Section 2: the real compiler error from swiftc (iOS 26.5 SDK): "left side of mutating operator isn't mutable: 'self' is immutable".
- Section 3: with a print in body, three activations printed balance 25000 → 26000 → 27000 → 28000.
- Section 4: printed types `balance: Int`, `_balance: State<Int>`, `$balance: Binding<Int>`.
- Section 5: the NonNegative example compiled and printed `0` (Mac, swiftc).
- Sections 6 and 13: an **authored** `Survivor` view printed when its struct was created; after three adds, two new struct values were created by the parent and both saw balance 28000.
- Section 7: the 6-stage pipeline (only stage 1 shared) is drawn with **authored** stages 2–6, marked conceptual.
- Section 9: `_printChanges` printed "@self, @identity, _balance changed." at launch, then "_balance changed." per activation.
- Sections 10–12: the currency format printed ₹25,000; BalanceCard's body ran with 26000/27000/28000; Send still printed "Send tapped"; screenshots of the final code at ₹25,000 and after three taps at ₹28,000. BalanceCard's code on the slide notes "same modifiers as 2.6" to fit; the full code is in the text and `App.swift`.
- Section 14: Increment ×3 then Replace Identity: count 3 → 0, with before/after screenshots.
- Section 16's `po balance` is described (not run).
- Section 11 is cut off at "two-way bindings in Lesson"; Part 2's ending names 2.9.

**Course canon note.** This restarted Unit 02 uses whole rupees in an `Int` (as the text does). Unit 01 and the course canon store money as paise in `Int64` with the ViewModel formatting it; the Section 17 slide's notes say so.

**Authored (flagged)**
- Review: the text's 6 questions (answers authored; Experiment 1's prediction answer was given in the text), plus a predict item (identity reset) and a spaced item from 2.7.
- Outcomes, "Where we are", recap, "Where this goes next" (2.9 from the text), lab with expected results.
- Sections 11 and 17's diagrams drawn from the text's descriptions.

**Wording**
- "Trainer analogy" / "Trainer question" / "Senior engineer insight" became neutral callouts or notes; "Senior engineer knowledge check" became "Check your understanding". The hotel analogy (Section 13) stays in the notes, consistent with the course's hotel analogy.
