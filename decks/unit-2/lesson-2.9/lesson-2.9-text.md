# Unit 2 · Lesson 2.9 — @Binding: How Two SwiftUI Views Share State

> Lesson text as shared, in two parts (Sections 1–11 plus the heading of 12; then "Part 2: @Binding Internals,
> Debugging & Assessment", Sections 12–17 and the final checkpoint). Interactive widgets are described in brackets.
> The deck (`index.html`, built by `tools/gen2_9.py`) follows Sections 1–17. Simulator evidence and authored
> additions are listed at the end under "Deck changes".

NPay Engineering Lab · Incremental Development · Property Wrappers → Data Flow → SwiftUI Internals

In Lesson 2.8, we made NPay's balance reactive using @State. Now we'll solve a new engineering problem: **What happens when a child view needs to change a value owned by its parent?** This introduces @Binding, one of SwiftUI's most important concepts. We'll understand how it works internally, implement it in NPay, and investigate how state flows between views.

## 1. The problem — NPay needs a balance editor

Currently, ContentView owns the demo balance (`@State private var balance = 25000`) and BalanceCard displays it (`BalanceCard(balance: balance)`). This works because BalanceCard only reads the balance. But suppose we want a separate component that can add or subtract demo money. [Mock-up: the balance card and a "Demo Balance Editor" with − ₹1,000 and + ₹1,000; both components reflect the same state.]

Notice that the editor changes the balance, while the balance card displays the updated value. We don't want two independent balance variables. We want one source of truth.

## 2. First experiment — why passing an Int is not enough

```swift
struct BalanceEditor: View {
    let balance: Int

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}
```

This fails to compile. Why? Because balance is declared with let. Even if we changed it to var, mutating an ordinary stored property of the view from this button action would not be the correct SwiftUI state-management pattern.

**Connect to Unit 1.** Remember value semantics. When you pass an Int to another struct, you're passing a value. Changing an independent copy would not automatically update the parent's state. We need a way for the child to access the parent's state storage.

## 3. Introducing @Binding

```swift
struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}
```

Now the child can modify a value owned elsewhere. But how does the parent provide access? Using `$balance`.

```swift
struct ContentView: View {
    @State private var balance = 25000

    var body: some View {
        BalanceEditor(balance: $balance)
    }
}
```

**What is happening?** ContentView owns the state. BalanceEditor receives a binding to that state. The child can read and write through the binding.

## 4. balance versus $balance

This is the most important syntax distinction. [@State private var balance = 25000 → balance: Int value; $balance: Binding<Int>.] `balance` accesses the wrapped state value. `$balance` accesses the projected value of @State, which is a `Binding<Int>`.

**Why the dollar sign?** Swift property wrappers can expose a projectedValue. For @State, that projected value provides a binding. This is a Swift language feature, not special syntax invented only for SwiftUI.

## 5. Behind the scenes — how does Binding work?

Conceptually, a binding provides access to a value through read and write operations. Imagine this simplified type:

```swift
// Teaching approximation, not Apple's implementation

struct SimpleBinding<Value> {
    let get: () -> Value
    let set: (Value) -> Void

    var wrappedValue: Value {
        get { get() }
        nonmutating set { set(newValue) }
    }
}
```

Notice something interesting. The setter is nonmutating. That means the binding value itself doesn't need to be mutated to change the underlying storage. It delegates the write to another location. This helps explain why a child SwiftUI view can update bound state.

**Important distinction.** A binding does not own the underlying state. It provides access to state owned elsewhere.

## 6. Interactive state-flow walkthrough

[NPay — parent-child data flow, a 6-step stepper; only step 1 was included: "ContentView owns @State — the parent stores the current demo balance." Conceptual SwiftUI data-flow model.]

**The key relationship.** Parent @State ↔ child @Binding. The arrow is bidirectional because the child can both read and write the parent's state. But ownership remains with the parent.

## 7. Why doesn't the child need its own @State?

Imagine this incorrect design:

```swift
struct BalanceEditor: View {
    @State private var balance = 25000

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}
```

Now the child owns an independent balance. The parent has another balance. They can diverge. [Two sources of truth: parent balance ₹25,000, child balance ₹26,000. One source of truth: parent owns balance, child uses Binding.]

**Senior engineer principle.** State ownership should be explicit. If multiple views need to read or modify the same local state, place ownership at an appropriate shared level and pass values or bindings as needed.

## 8. Incremental NPay implementation — create BalanceEditor

Create BalanceEditor.swift or temporarily place this struct in ContentView.swift.

```swift
import SwiftUI

struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        VStack(spacing: 12) {
            Text("Demo Balance Editor")
                .font(.headline)

            HStack(spacing: 12) {
                Button("− ₹1,000") {
                    balance = max(0, balance - 1000)
                }
                .buttonStyle(.bordered)

                Button("+ ₹1,000") {
                    balance += 1000
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}
```

**Why max(0, balance - 1000)?** This prevents the demo balance from becoming negative. In a real payment system, validation belongs in trusted domain and backend logic rather than relying only on UI controls.

## 9. Integrate BalanceEditor into ContentView

Our existing parent already owns `@State private var balance = 25000` and displays `BalanceCard(balance: balance)`. Now add `BalanceEditor(balance: $balance)`. The parent passes the value to the display component and a binding to the editor component. [ContentView owns @State balance → BalanceCard receives Int; BalanceEditor receives Binding<Int>.]

## 10. Complete NPay code — Lesson 2.9

(Code: the complete `ContentView.swift` — `ContentView` with `@State private var balance = 25000` and a `ScrollView` around `VStack(spacing: 24)`: the header, `BalanceCard(balance: balance)`, `BalanceEditor(balance: $balance)` and the `HStack(spacing: 12)` of three `QuickAction`s; `BalanceCard` as in 2.8; `BalanceEditor` as in Section 8; `QuickAction` as in 2.7; `#Preview`. It runs in `tools/sim2_9/App.swift`.)

We introduced ScrollView to keep the growing interface usable on smaller screens. We'll investigate scrollable containers deeply in the next lesson.

## 11. Deep experiment — build a Binding manually

```swift
BalanceEditor(
    balance: Binding(
        get: {
            balance
        },
        set: { newValue in
            balance = newValue
        }
    )
)
```

This is conceptually similar to passing `$balance`.

**Why is this useful?** It demonstrates that a binding represents a read/write connection to state. Custom bindings can also perform transformations or validation. However, avoid introducing unnecessary custom bindings when a simple `$balance` is sufficient.

## Part 2: @Binding Internals, Debugging & Assessment

We've implemented the NPay balance editor using @Binding. Our application now has a single balance owned by ContentView, displayed by BalanceCard, and modified by BalanceEditor. Let's complete the lesson by testing your understanding, investigating binding behavior, and verifying the implementation in Xcode.

## 12. Senior engineer knowledge check

1. Who owns the balance in our NPay design? — **ContentView** / BalanceEditor / Both independently
2. What is the type of $balance? — Int / **Binding<Int>** / State<Int>
3. Does @Binding own the underlying value? — Yes / **No**
4. What happens when BalanceEditor changes balance? — Only the child updates / **Parent-owned state changes** / A new independent balance is created
5. Why can @Binding work with a SwiftUI struct? — **It uses a nonmutating setter to write through to underlying storage** / It converts the struct into a class / It disables Swift type checking
6. What is the main risk of duplicating @State in both parent and child? — **Two inconsistent sources of truth** / A compiler crash / Automatic database writes
7. What does Binding(get:set:) provide? — **Explicit read/write closures** / A new process / Automatic persistence
8. Should a child receive @Binding if it only needs to display a value? — Always / **Usually no**

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 13. Behind the scenes — what does a binding actually contain?

(The teaching model `SimpleBinding<Value>` from Section 5 again, with `get { get() }` and `nonmutating set { set(newValue) }`.) Notice the generic parameter Value. For NPay: `Binding<Int>`. The binding's value type is Int.

**Why is nonmutating set important?** Normally, mutating a stored property in a struct requires mutable access to that struct. But a binding can forward writes to external storage. It doesn't need to mutate its own stored fields to change the underlying value.

`BalanceEditor.balance += 1000` (child writes to its bound property) → `Binding.wrappedValue` setter (write is forwarded through the binding) → ContentView @State storage (parent-owned state receives the new value) → SwiftUI dependency update (views depending on the balance can update). Conceptual flow; SwiftUI's internal binding storage is not publicly specified.

## 14. Experiment — build a custom Binding

Suppose NPay should never allow the demo balance to become negative. Instead of passing $balance directly, we can create a binding with a validating setter. Inside ContentView, define:

```swift
private var safeBalance: Binding<Int> {
    Binding(
        get: {
            balance
        },
        set: { newValue in
            balance = max(0, newValue)
        }
    )
}
```

Then pass it to the editor: `BalanceEditor(balance: safeBalance)`. Now writes through this binding are clamped to zero or above.

**What is happening internally?** The child doesn't know about the validation. It simply writes a new balance. The custom binding intercepts that write and applies the rule.

**Important production distinction.** This is useful for UI behavior, but it is not a secure financial validation mechanism. Real payment rules must be enforced by trusted domain and backend systems.

## 15. Debugging the Binding in Xcode

In BalanceEditor, set a breakpoint on `balance += 1000`. Run NPay. Tap + ₹1,000. When Xcode pauses, inspect the current balance. Then continue execution. The balance card should display the updated amount.

**What should we observe?** The child modifies the binding. The parent-owned state changes. SwiftUI updates the relevant view descriptions. No separate balance copy is created in the child.

## 16. Experiment — read-only value versus Binding

Read-only display:

```swift
struct BalanceCard: View {
    let balance: Int

    var body: some View {
        Text("₹\(balance)")
    }
}
```

Editable component:

```swift
struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}
```

The difference is intentional. BalanceCard only needs a value. BalanceEditor needs read/write access.

**Senior engineer rule.** Give a child view only the access it needs. If a child only displays information, pass a value. If it needs to modify parent-owned local state, pass a binding. This keeps ownership and data flow understandable.

## 17. Final NPay architecture

[One source of truth — two consumers: ContentView (@State balance = 25000) → BalanceCard (receives Int, read only) and BalanceEditor (receives Binding<Int>, read + write).] The key relationship: Parent State →(value)→ Display; Parent State ↔(binding)↔ Editor.

**Lesson 2.9 — Final checkpoint.** Our NPay application now has a balance card and a separate balance editor sharing one state value. You've learned @Binding, projected values, property wrappers, Binding<Value>, read/write closures, state ownership, validation, and parent-child data flow. Before moving forward, verify in Xcode that tapping + ₹1,000 updates the balance card and tapping − ₹1,000 decreases it without going below zero.

**Next — Lesson 2.10: ForEach, List and Collection Identity.** We'll introduce a real transaction model and build NPay's first transaction history, investigating Identifiable, stable IDs, view reuse, collection updates, and why unstable identity causes SwiftUI bugs.

## Deck changes

The deck (`index.html`, built by `tools/gen2_9.py`, 37 slides) follows Sections 1–17 (both parts), grouped into 8 Parts:
a balance editor (1), passing an Int (2), @Binding (3–4), how a binding works (5–6, 13), one source of truth (7),
NPay's BalanceEditor (8–10, 17), custom bindings (11, 14), access and debugging (15–16); then recap, review (12), next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_9/`, rerun with `sh tools/sim2_9/run.sh`;
buttons activated through accessibility, as in 2.7–2.8)
- Section 2: real swiftc errors: with `let`, "'balance' is a 'let' constant"; with `var`, "'self' is immutable".
- Section 4: printed `$balance: Binding<Int>` (parent), `balance: Int` and `_balance: Binding<Int>` (child); SDK excerpts `State.projectedValue: Binding<Value>` and `Binding.wrappedValue { get nonmutating set }`.
- Sections 5 and 13: the SimpleBinding teaching model was run on the Mac with an **authored** `Storage` class standing in for SwiftUI's storage; a `let` binding wrote 26000 through to the storage.
- Section 6: the 6-step walkthrough (only step 1 shared) is drawn as an **authored** 4-step write path, marked conceptual; prints in BalanceCard and BalanceEditor bodies showed both re-evaluated with the same value after +, +, −.
- Section 7: the incorrect design ran: child ₹26,000 vs parent ₹25,000, with a screenshot.
- Section 8: an editor started at ₹500 (**authored** start value): − clamped to 0; a second − left 0 and printed no further update.
- Sections 9–10: screenshots at launch (₹25,000) and after +, +, − (₹26,000); the slide summarises ContentView (with ScrollView); the full code is in the text.
- Section 11: the hand-built binding's setter printed 26000 and the card followed.
- Section 14: safeBalance given to an **authored** child that subtracts without clamping, from ₹500: it stored 0 for −500 and −1000.
- Section 15's breakpoint is described (not run).

**Authored (flagged)**
- Review: the text's 8 questions (answers authored), plus a predict item (₹500 − 1,000 twice) and a spaced item from 2.8.
- Outcomes, "Where we are", recap, "Where this goes next" (2.10 from the text), lab with expected results.
- Section 17's architecture shown in the integration diagram.

**Wording**
- "Senior engineer principle/rule" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding".
