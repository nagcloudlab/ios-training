# Unit 3 · Lesson 3.5 — State Preservation Across Navigation

> Lesson text as shared, in two pieces: Sections 1–13 and "Part 2: State Preservation, Debugging & Architecture
> Review" (Sections 13–19). Interactive widgets are described in brackets. The deck (`index.html`, built by
> `tools/gen3_5.py`) follows both. The text ends by naming its next implementation checkpoint (integrating the shared
> draft into the complete app); that integration is **authored** and listed at the end. Evidence and authored additions
> are listed under "Deck changes".

NPay iOS Engineering Masterclass · SwiftUI Identity · State Lifetime · Navigation · Observation Internals

In Lesson 3.4, we introduced a payment-review sheet. NPay can now collect payment details, present a review, confirm a simulated transaction, and navigate to a success screen. Today we'll investigate a problem that becomes important as applications grow: what happens to the user's partially completed payment when they switch tabs, navigate away, or dismiss a sheet? Our goal is to preserve NPay's payment draft intentionally, rather than relying on incidental SwiftUI view lifetime.

## 1. Our NPay milestone

Imagine this user journey: (1) Open Payments. (2) Enter ravi@npay and ₹1,500. (3) Switch to History to check an earlier transaction. (4) Return to Payments. (5) Continue editing the same payment. Should the input disappear? No. For our NPay design, we'll preserve it until the user successfully completes the payment or explicitly discards the draft.

[Interactive simulation: Screen-local state / Shared draft state; Payments — NPay Demo, Recipient, Amount (₹), "Draft revision: 0"; tabs Payments, History. "The draft survives tab switching because its state belongs to a longer-lived owner."]

This distinction is essential: state preservation depends on ownership and identity, not merely whether a screen is visible.

## 2. First experiment — local @State

Let's begin with the familiar approach.

```swift
struct PaymentsScreen: View {
    @State private var recipient = ""
    @State private var amountText = ""

    var body: some View {
        VStack {
            TextField("Recipient", text: $recipient)

            TextField("Amount", text: $amountText)
        }
        .padding()
    }
}
```

This works. The user can type into both fields. But what happens when PaymentsScreen is removed from the hierarchy? If SwiftUI later establishes a new identity for the screen, its local @State values can be initialized again.

**Important nuance.** Switching tabs does not automatically mean local state is destroyed. A stable TabView can preserve tab-associated state across ordinary switches. However, if we need a payment draft to survive deliberate screen replacement or other navigation changes, we should give it a longer-lived owner.

## 3. View identity versus view value

Recall Lesson 2.8. SwiftUI views are value types. A view struct can be recreated while its associated @State remains alive.

[Three concepts that must not be confused: View value — a Swift struct describing part of the UI; View identity — how SwiftUI associates a logical view with its state; State storage — managed values associated with that identity.]

**Example.** Creating a new `PaymentsScreen()` struct value does not necessarily reset the state. But removing the screen from its structural position and later introducing a new identity can reset local state.

## 4. Experiment — force a state reset with .id()

Let's prove this behavior.

```swift
import SwiftUI

struct IdentityLab: View {
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            DraftEditor()
                .id(identity)

            Button("Replace View Identity") {
                identity = UUID()
            }
        }
        .padding()
    }
}

struct DraftEditor: View {
    @State private var recipient = ""

    var body: some View {
        VStack {
            TextField("Recipient", text: $recipient)
                .textFieldStyle(.roundedBorder)

            Text("Current: \(recipient)")
        }
    }
}

#Preview {
    IdentityLab()
}
```

**Practice.** Enter ravi@npay. Tap Replace View Identity. The field resets.

**Why?** Changing the explicit identity causes SwiftUI to treat the editor as a new logical view. Its local state is initialized for that new identity.

Trainer insight: Avoid generating random `.id(UUID())` values during normal body evaluation. Unstable identity can destroy useful state and cause unexpected UI behavior.

## 5. Solution — create a payment draft model

Instead of keeping the recipient and amount as independent screen-local properties, let's create a model representing the draft.

```swift
struct PaymentDraft {
    var recipient: String = ""
    var amountText: String = ""
}
```

This is an ordinary Swift struct. It contains the user's editable input. We deliberately store amountText as a string because the user may temporarily enter an incomplete amount such as "1500.". The draft model is separate from a validated payment request.

**Important design distinction.** A draft represents incomplete user input. A payment request represents validated domain data. We shouldn't confuse the two.

## 6. Where should the draft live?

Our Unit 3.3 architecture introduced NPayStore. We can extend it:

```swift
@MainActor
@Observable
final class NPayStore {

    var balancePaise = 2_500_000

    var transactions: [Transaction] = []

    var paymentDraft = PaymentDraft()

    // Existing payment logic...
}
```

Now the draft belongs to the shared application store. Because NPayRootView owns the store, the draft can survive ordinary tab switches and screen recreation within that root's lifetime.

[NPayRootView (owns NPayStore) → NPayStore.paymentDraft (recipient + amount text) → PaymentsScreen (reads and edits shared draft).]

## 7. Connect the draft using @Bindable

Our store uses the Observation framework. Inside PaymentsScreen:

```swift
struct PaymentsScreen: View {
    @Bindable var store: NPayStore

    var body: some View {
        VStack(spacing: 16) {
            TextField(
                "Recipient",
                text: $store.paymentDraft.recipient
            )

            TextField(
                "Amount",
                text: $store.paymentDraft.amountText
            )
        }
        .textFieldStyle(.roundedBorder)
        .padding()
    }
}
```

**What is @Bindable?** @Bindable provides binding access to mutable properties of an observable object. This is different from @State. @State can own an observable object in the view hierarchy. @Bindable provides bindings to its mutable properties. @Observable makes the object participate in Observation. We'll explore the compiler and Observation internals deeply in Unit 4. For now, focus on the ownership relationship.

## 8. Behind the scenes — what happens when the user types?

[Shared draft update pipeline — a 6-stage stepper; only Stage 1 was shared: "1. User types recipient. TextField receives the edited string."]

## 9. When should we clear the payment draft?

We need an explicit rule. For NPay: switching tabs should preserve the draft; dismissing the review sheet should preserve the draft; navigating to History should preserve the draft; completing a successful demo payment should clear the draft; tapping Discard Draft should clear the draft. We can implement:

```swift
func clearPaymentDraft() {
    paymentDraft = PaymentDraft()
}
```

Call this after the payment has been successfully recorded.

**Why not clear it when the review sheet dismisses?** Because dismissal might mean the user wants to correct the amount. Clearing the draft at that point would lose useful input.

## 10. The deeper question — does shared state survive app termination?

No, not automatically. Our NPayStore is an in-memory object. If the app terminates, the draft isn't guaranteed to survive. There are several different persistence lifetimes:

| Storage | Typical lifetime |
|---|---|
| View-local @State | While associated view identity survives |
| Shared observable store | While store instance survives |
| SceneStorage | Supports scene state restoration |
| AppStorage | Persists simple preference-like values |
| SwiftData | Persistent structured data |

We'll study persistence properly in Unit 6. For payment drafts, we must also consider privacy and security before storing recipient or financial information persistently.

## 11. Architecture improvement — separate draft from payment processing

Our store now contains both `var paymentDraft = PaymentDraft()` and `func recordDemoPayment(...)`. These are different responsibilities. The draft represents editing state. The payment method represents application behavior. For now, combining them in the shared store is acceptable for learning. In Unit 4, we'll introduce dedicated ViewModels and use cases.

## 12. Xcode experiments

Run these in your existing NPay project: (1) Enter a recipient and amount in Payments. (2) Switch to History and return. (3) Verify that the draft remains. (4) Open the review sheet and dismiss it. (5) Verify that the draft remains. (6) Confirm a successful demo payment. (7) Verify that the draft clears. (8) Restart the application and observe the difference between in-memory state and durable persistence.

**Debugging tip.** Add:

```swift
.onChange(of: store.paymentDraft.recipient) {
    oldValue, newValue in

    print("Recipient changed:", oldValue, "→", newValue)
}
```

This can help you observe how the shared draft changes during editing.

## 13. Senior engineer knowledge check

[State Preservation Assessment, 0 / 6 answered; the first piece showed the same six questions.]
1. Does recreating a SwiftUI view struct necessarily reset @State? (Yes / No)
2. What can changing a view's explicit .id() cause? (State identity reset / Automatic persistence / A new iOS process)
3. Why place the NPay draft in a shared store? (To give it a lifetime beyond one screen / To encrypt it automatically / To create a new thread)
4. What does @Bindable provide? (Bindings to mutable observable properties / Database persistence / Background execution)
5. Should dismissing a review sheet automatically erase the payment draft? (Yes / No)
6. Does an in-memory NPayStore automatically survive app termination? (Yes / No)

## Part 2: State Preservation, Debugging & Architecture Review

NPay Engineering Lab · Continuing from Section 13. We've learned why SwiftUI state can survive view recreation, why identity matters, and how a shared NPayStore can preserve payment drafts across navigation. Let's finish the senior-engineer assessment and investigate one final important concept: the difference between preserving state and persisting state.

## 14. State preservation versus persistence

These two concepts are frequently confused. State preservation means keeping a value while the relevant state owner remains alive. Persistence means storing information so it can be recovered after the state owner or application process is destroyed.

| Mechanism | Survives |
|---|---|
| @State | Normal updates while view identity survives |
| Shared NPayStore | Navigation changes while store instance survives |
| @SceneStorage | Can restore simple scene state across supported lifecycle restoration |
| @AppStorage | Persists simple values through UserDefaults |
| SwiftData | Persists structured records to local storage |

**Important distinction.** Even if a draft survives switching between tabs, that doesn't mean it survives force-quitting NPay. For our Unit 3 application, we'll deliberately preserve the draft in memory. Durable persistence comes in Unit 6.

## 15. A deeper experiment — reset the child, preserve the draft

This experiment demonstrates why moving state ownership upward matters.

```swift
import SwiftUI

@MainActor
@Observable
final class DraftStore {
    var recipient = ""
}

struct DraftIdentityExperiment: View {
    @State private var store = DraftStore()
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            DraftChild(store: store)
                .id(identity)

            Button("Recreate Child Identity") {
                identity = UUID()
            }

            Text("Store value: \(store.recipient)")
        }
        .padding()
    }
}

struct DraftChild: View {
    @Bindable var store: DraftStore

    var body: some View {
        TextField(
            "Recipient",
            text: $store.recipient
        )
        .textFieldStyle(.roundedBorder)
    }
}

#Preview {
    DraftIdentityExperiment()
}
```

**Run the experiment.** Enter ravi@npay. Tap Recreate Child Identity. The child receives a new SwiftUI identity, but the recipient remains.

**Why?** Because the recipient is not stored in the child's local @State. It belongs to the shared DraftStore, which is still alive in the parent.

[Parent (owns DraftStore) → Child identity changes (child-local state may reset) → DraftStore remains (recipient is preserved).]

## 16. Should every state property go into NPayStore?

No. Moving all state into one global object can create unnecessary coupling. We should decide ownership based on intended lifetime and sharing requirements.

| State | Recommended owner |
|---|---|
| Current balance | Shared NPayStore |
| Transaction collection | Shared NPayStore |
| Payment draft | Shared feature-level store |
| Review sheet visibility | PaymentsScreen |
| Focused text field | PaymentsScreen |
| Temporary animation state | Relevant component |
| Selected tab | NPayRouter |
| Navigation paths | NPayRouter |

**Senior engineer principle.** Keep state as local as possible, but as shared as necessary. For now, keeping the draft inside NPayStore is a practical learning step. Later, we can introduce a dedicated payment-flow model.

## 17. What happens if two screens edit the same draft?

Suppose both PaymentsScreen and another payment editor receive bindings to the same draft. They can both read and write the same underlying value. That may be intentional, but it introduces coordination questions: Which screen owns the user's editing workflow? Should edits made in one screen immediately appear in another? What happens if the user discards the draft? Can a review sheet show stale values after the draft changes?

For our NPay design, we'll create an immutable PaymentDraft snapshot when the review sheet opens. That snapshot represents what the user is reviewing. At confirmation time, we'll validate the payment again against the current store balance. This separates editable draft state from confirmed payment input.

## 18. Debugging state preservation in Xcode

Add a diagnostic to PaymentsScreen:

```swift
.onChange(of: store.paymentDraft.recipient) {
    oldValue, newValue in

    print("Draft changed:")
    print("Old:", oldValue)
    print("New:", newValue)
}
```

Then test: (1) Enter a recipient. (2) Switch to History. (3) Return to Payments. (4) Verify the recipient remains. (5) Open and dismiss the review sheet. (6) Confirm a successful demo payment. (7) Verify the draft clears. You can also set breakpoints inside `clearPaymentDraft()` and `recordDemoPayment()` to investigate exactly when state changes.

## 19. Final NPay architecture — Lesson 3.5

[NPayRootView (owns shared application objects) → NPayRouter (tabs and navigation paths), NPayStore (balance, transactions, draft) → PaymentsScreen (edits shared draft through @Bindable).]

**Lesson 3.5 checkpoint.** We've now covered state preservation, view identity, explicit identity resets, shared observable state, @Bindable, draft ownership, and the difference between in-memory preservation and durable persistence. Our next implementation checkpoint is to integrate the shared PaymentDraft into the complete NPay application, preserving input across tab switches and sheet dismissal.

Next — Lesson 3.6: SwiftUI Animations & Transitions. We'll animate NPay's balance updates, payment confirmation, and success feedback while investigating transactions, interpolation, view identity, and the rendering pipeline.

## Integration through Lesson 3.5 (authored)

The text's checkpoint, done: the shared draft integrated into the Lesson 3.4 code and run in the simulator
(`tools/sim3_5/App.swift`). Everything else is unchanged from Lesson 3.4 (see `../lesson-3.4/lesson-3.4-text.md`).

Choices that go beyond the text (flagged):
- **Name clash.** Lesson 3.4's review model and this lesson's editable draft are both called `PaymentDraft`; together
  they fail with "invalid redeclaration of 'PaymentDraft'". The editable input keeps the name `PaymentDraft`; 3.4's
  review snapshot is renamed `PaymentReview` (and `reviewDraft` → `review`).
- The draft is cleared in the confirm closure, right after the store records the payment (Section 9: "after the
  payment has been successfully recorded"); the sheet keeps showing its snapshot.
- Discard Draft asks first, with an alert ("Discard payment draft?", 3.4's alert pattern), and is disabled when the
  draft is empty.
- The Section 18 diagnostic is kept in PaymentsScreen.

### Models/PaymentDraft.swift and Models/PaymentReview.swift

```swift
import Foundation

// Models/PaymentDraft.swift (Lesson 3.5: the editable input)

struct PaymentDraft {
    var recipient: String = ""
    var amountText: String = ""
}

// Models/PaymentReview.swift (Lesson 3.4's review snapshot, renamed: both lessons call it PaymentDraft)

struct PaymentReview: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}
```

### Store/NPayStore.swift (additions)

```swift
    var paymentDraft = PaymentDraft()

    func clearPaymentDraft() {
        paymentDraft = PaymentDraft()
    }
```

### Screens/PaymentsScreen.swift

```swift
import SwiftUI

struct PaymentsScreen: View {
    @Bindable var store: NPayStore
    let router: NPayRouter

    @State private var review: PaymentReview?
    @State private var pendingSuccessID: UUID?
    @State private var paymentFailed = false
    @State private var showFailure = false
    @State private var confirmDiscard = false

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    private var parsedAmount: Int? {
        Money.parsePaise(store.paymentDraft.amountText)
    }

    private var isValid: Bool {
        let trimmed = store.paymentDraft.recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              let amount = parsedAmount else {
            return false
        }

        return amount > 0
            && amount <= store.balancePaise
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text(
                    "Available: \(Money.display(store.balancePaise))"
                )
                .foregroundStyle(.secondary)

                TextField(
                    "Recipient ID",
                    text: $store.paymentDraft.recipient
                )
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .recipient
                )
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .amount
                }

                TextField(
                    "Amount (₹)",
                    text: $store.paymentDraft.amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )

                if !store.paymentDraft.amountText.isEmpty && !isValid {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                Button("Review Payment") {
                    guard let amountPaise = parsedAmount else {
                        return
                    }

                    focusedField = nil
                    // An immutable snapshot of what the user is reviewing
                    review = PaymentReview(
                        recipient: store.paymentDraft.recipient,
                        amountPaise: amountPaise
                    )
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isValid)

                Button("Discard Draft", role: .destructive) {
                    confirmDiscard = true
                }
                .disabled(store.paymentDraft.recipient.isEmpty && store.paymentDraft.amountText.isEmpty)
            }
            .padding()
        }
        .navigationTitle("Payments")
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()

                Button("Done") {
                    focusedField = nil
                }
            }
        }
        .sheet(
            item: $review,
            onDismiss: {
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    router.showPaymentSuccess(id)
                } else if paymentFailed {
                    paymentFailed = false
                    showFailure = true
                }
            }
        ) { review in

            PaymentReviewSheet(review: review) {
                // The store validates again against the current balance
                if let id = store.recordDemoPayment(
                    recipient: review.recipient,
                    amountPaise: review.amountPaise
                ) {
                    store.clearPaymentDraft()   // recorded: the draft is done
                    pendingSuccessID = id
                } else {
                    paymentFailed = true
                }
                self.review = nil
            }
        }
        .alert("Payment not recorded", isPresented: $showFailure) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("The amount is no longer within your available balance.")
        }
        .alert("Discard payment draft?", isPresented: $confirmDiscard) {
            Button("Discard", role: .destructive) {
                store.clearPaymentDraft()
            }

            Button("Cancel", role: .cancel) {}
        }
        // Diagnostic (Section 18): watch the shared draft change
        .onChange(of: store.paymentDraft.recipient) { oldValue, newValue in
            print("Draft changed:")
            print("Old:", oldValue)
            print("New:", newValue)
        }
    }
}
```

### Screens/PaymentReviewSheet.swift

```swift
import SwiftUI

struct PaymentReviewSheet: View {
    let review: PaymentReview
    let onConfirm: () -> Void

    @State private var isProcessing = false

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: review.recipient
            )

            LabeledContent(
                "Amount",
                value: Money.display(review.amountPaise)
            )

            Button("Confirm Demo Payment") {
                guard !isProcessing else {
                    return
                }

                isProcessing = true
                onConfirm()
            }
            .buttonStyle(.borderedProminent)
            .disabled(isProcessing)

            Button("Edit Details") {
                dismiss()
            }
            .buttonStyle(.bordered)
        }
        .padding()
        .presentationDetents([.medium, .large])
        .interactiveDismissDisabled(isProcessing)
    }
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_5.py`, 42 slides) follows both pieces, grouped into 8 Parts: the milestone
(1), local @State (2), value, identity, state (3, 4), a draft model (5, 6, 11, 17's naming), @Bindable (7, 8), when to
clear (9, 12, 18), preservation vs persistence (10, 14, 15), choosing owners (16, 17, 19); then recap, review, next,
lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_5/`, rerun with `sh tools/sim3_5/run.sh`; the text's
IdentityLab and DraftIdentityExperiment run verbatim; driver as in 3.4)
- Section 2's local-@State screen: kept across a TabView switch ("ravi@npay"); emptied after an if/else replaced the
  screen and brought it back.
- Section 3, authored experiment: an editor whose `init` prints, inside a parent re-rendered twice: three inits, the field
  still "ravi@npay".
- IdentityLab: "Current: ravi@npay", then empty after Replace View Identity (cropped screenshots).
- Section 4's warning, authored experiment: `DraftEditor().id(UUID())` next to a counter; one unrelated tap emptied the
  field.
- DraftIdentityExperiment: "Store value: ravi@npay" before and after Recreate Child Identity; the field kept the text.
- Experiments 1–7 with the Section 18 diagnostic on the integrated app: one "Draft changed" per keystroke; nothing on the
  History round trip or the sheet swipe-down (fields still "ravi@npay", "1500"); one change to empty on the recorded
  payment; Discard Draft → Discard cleared it. Experiment 8: after terminating and relaunching, both fields empty.
- swiftc (Mac): the two `PaymentDraft` declarations together → "invalid redeclaration of 'PaymentDraft'".

**Authored (flagged)**
- The integration (choices listed above) and the slides that show it; the `PaymentReview` rename.
- Section 8's stages 2–6 (only stage 1 shared), marked conceptual.
- The experiments marked authored above.
- Review: the text's 6 questions (options reordered so answers vary) plus two predict items (unstable `.id(UUID())`;
  the child recreated over a store) and a spaced item from 3.4; 3 of 9 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.6 as the text names it; Unit 4 and Unit 6 as the text
  says), lab, end slide.

**Wording**
- "Trainer insight" and "Senior engineer principle / knowledge check" became neutral callouts and "Check your
  understanding".
