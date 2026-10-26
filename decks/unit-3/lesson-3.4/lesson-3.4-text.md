# Unit 3 · Lesson 3.4 — Sheets, Alerts & Modal Presentation

> Lesson text as shared, in three pieces: Sections 1–14 (cut off inside Section 14's experiment list), "Part 2: Modal
> Lifecycle, Payment Confirmation & Debugging" (Sections 14–21), and a note offering the complete Lesson 3.4 code as a
> ZIP, which was not shared. Interactive widgets are described in brackets. The deck (`index.html`, built by
> `tools/gen3_4.py`) follows all three. The complete code at the end is **authored**: the text's sections assembled
> onto the 3.3 code, and run in the simulator. Evidence and authored additions are listed under "Deck changes".

NPay iOS Engineering Masterclass · Incremental Development · SwiftUI Presentation Internals

In Lesson 3.3, we built four tabs for NPay: Home, Payments, History, and Profile. We also introduced a shared NPayStore and NPayRouter. Now we're going to improve the payment experience. Currently, tapping Send Demo Payment immediately processes the transaction and navigates to the success screen. But what if the user entered the wrong recipient or amount? A payment application should let the user review the details before confirming.

Our engineering challenge: How can NPay temporarily present a payment-review screen without pushing another destination onto its navigation stack? We'll learn sheet, fullScreenCover, alert, confirmationDialog, presentation state, dismissal, and how SwiftUI manages modal presentation.

## 1. Our NPay milestone

We'll change the payment flow from Payment Form → Payment Success to Payment Form → Review Sheet → Confirm → Payment Success.

[Interactive demonstration: Send Money · NPay Demo; Recipient, Amount (₹), Review Payment; "Payment Recorded — ₹1500 sent to ravi@npay (demo)", Done; "Available demo balance: ₹23,500". Caption: "Illustrative modal flow. In Xcode, the review will appear as a native SwiftUI sheet."]

## 2. First concept — what is a sheet?

A sheet is a modal presentation. It appears over the current interface, typically allowing the user to complete a focused task without permanently navigating deeper into the current stack. SwiftUI provides `.sheet(isPresented:content:)`. Let's begin with a minimal example.

```swift
import SwiftUI

struct SheetExperiment: View {
    @State private var showSheet = false

    var body: some View {
        Button("Review Payment") {
            showSheet = true
        }
        .sheet(isPresented: $showSheet) {
            Text("Payment Review")
                .font(.title)
                .presentationDetents([.medium, .large])
        }
    }
}

#Preview {
    SheetExperiment()
}
```

**What happens?** When showSheet becomes true, SwiftUI presents the sheet. When the sheet is dismissed, the binding is updated accordingly. This is another example of state-driven UI.

## 3. Behind the scenes — how does .sheet() work?

[SwiftUI modal presentation pipeline — a 6-stage stepper; only Stage 1 was shared: "1. User taps Review. Button action executes." Caption: "Conceptual presentation flow. SwiftUI's internal presentation-controller implementation is not part of its public contract."]

**Important distinction.** A sheet is not a new iOS application process. It is a presentation within the running application's interface.

## 4. Sheet versus NavigationStack

| NavigationStack | Sheet |
|---|---|
| Pushes a navigation destination | Presents modal content |
| Used for hierarchical navigation | Used for focused temporary tasks |
| Back navigation | Dismissal |
| Managed by navigation path | Managed by presentation state |
| Example: History → Transaction Detail | Example: Payment → Review |

**Senior engineer question.** Should every new screen be presented using .sheet()? No. Use a navigation destination when the user is moving deeper into a hierarchy. Use a sheet when the user is performing a temporary, focused interaction.

## 5. @Environment(\.dismiss) — how does dismissal work?

Inside a sheet, SwiftUI provides an environment action for dismissal.

```swift
struct ReviewSheet: View {
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 20) {
            Text("Review Payment")

            Button("Cancel") {
                dismiss()
            }
        }
    }
}
```

**What's happening?** The sheet receives a dismiss action from its presentation environment. Calling `dismiss()` requests dismissal of the current presentation. It doesn't directly modify the parent's business state.

**Connect to Unit 2.** Remember environment propagation? SwiftUI uses environment values to provide contextual capabilities to descendants. Dismissal is one such capability.

## 6. presentationDetents — controlling sheet height

On supported iOS versions, we can configure sheet sizes.

```swift
.sheet(isPresented: $showSheet) {
    ReviewSheet()
        .presentationDetents([
            .medium,
            .large
        ])
}
```

This lets the sheet support medium and large presentation heights.

[Interactive detent explorer: Medium / Large; "Payment Review — Medium presentation". Caption: "Approximate visualization. Actual sheet dimensions depend on device, orientation, and presentation environment."]

## 7. What is .fullScreenCover()?

SwiftUI also provides full-screen modal presentation.

```swift
.fullScreenCover(isPresented: $showFullScreen) {
    Text("Full Screen Payment Flow")
}
```

A full-screen cover is useful when the presented experience should occupy the entire interface. For NPay, we might eventually use it for onboarding or a focused authentication flow. But our payment review is better suited to a sheet.

## 8. What is .alert()?

An alert presents important information or requests a simple decision. Example:

```swift
@State private var showAlert = false

Button("Delete Draft") {
    showAlert = true
}
.alert("Delete payment draft?", isPresented: $showAlert) {
    Button("Delete", role: .destructive) {
        print("Draft deleted")
    }

    Button("Cancel", role: .cancel) {}
} message: {
    Text("This action cannot be undone.")
}
```

**When should we use alerts?** Alerts are appropriate for concise, important messages or decisions. They are not intended for complex forms.

## 9. What is .confirmationDialog()?

A confirmation dialog presents a set of related actions or choices. For example:

```swift
@State private var showOptions = false

Button("Payment Options") {
    showOptions = true
}
.confirmationDialog(
    "Choose an action",
    isPresented: $showOptions
) {
    Button("Save Draft") {
        print("Draft saved")
    }

    Button("Discard", role: .destructive) {
        print("Draft discarded")
    }
}
```

| API | Best suited for |
|---|---|
| .sheet() | Custom temporary workflows |
| .fullScreenCover() | Immersive modal experiences |
| .alert() | Important messages or simple confirmations |
| .confirmationDialog() | Choosing among related actions |

## 10. NPay integration — introduce a payment review sheet

Now let's modify our existing PaymentsScreen. Previously, submitting the form immediately called `store.recordDemoPayment(...)`. Now we'll separate the process into two steps: (1) validate and present a review; (2) confirm and execute the local demo payment.

**Define a review model**

```swift
struct PaymentDraft: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}
```

We use Identifiable because SwiftUI provides an item-based sheet API.

```swift
.sheet(item: $reviewDraft) { draft in
    PaymentReviewSheet(draft: draft)
}
```

This is often cleaner than managing a separate boolean and a separate optional draft.

## 11. Build the PaymentReviewSheet

Create PaymentReviewSheet.swift.

```swift
import SwiftUI

struct PaymentReviewSheet: View {
    let draft: PaymentDraft
    let onConfirm: () -> Void

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: draft.recipient
            )

            LabeledContent(
                "Amount",
                value: Money.display(draft.amountPaise)
            )

            Button("Confirm Demo Payment") {
                onConfirm()
            }
            .buttonStyle(.borderedProminent)

            Button("Edit Details") {
                dismiss()
            }
            .buttonStyle(.bordered)
        }
        .padding()
        .presentationDetents([.medium, .large])
    }
}
```

**Important architectural detail.** PaymentReviewSheet doesn't own the account balance or transaction history. It displays a draft and exposes a confirmation action. The parent remains responsible for the actual demo operation.

## 12. Connect the sheet to PaymentsScreen

Inside PaymentsScreen, add `@State private var reviewDraft: PaymentDraft?`. When the form is valid and the user taps Review:

```swift
reviewDraft = PaymentDraft(
    recipient: recipient,
    amountPaise: amountPaise
)
```

Then attach:

```swift
.sheet(item: $reviewDraft) { draft in
    PaymentReviewSheet(draft: draft) {
        if let transactionID = store.recordDemoPayment(
            recipient: draft.recipient,
            amountPaise: draft.amountPaise
        ) {
            reviewDraft = nil
            router.showPaymentSuccess(transactionID)
        }
    }
}
```

**One important nuance.** We shouldn't assume that dismissing a sheet and pushing a navigation destination in the same synchronous update always produces the desired transition. In a polished implementation, we'd coordinate navigation with the sheet's onDismiss callback. We'll implement that in the complete Lesson 3.4 code checkpoint.

## 13. Behind the scenes — two independent state machines

[Navigation state versus presentation state: Navigation — NPayRouter, paymentsPath, Payment → Success; Modal presentation — PaymentsScreen, reviewDraft, No sheet → Review sheet.]

The router manages navigation destinations. The payment screen manages temporary presentation state. The store manages the demo transaction data. This separation makes the application easier to reason about.

## 14. Xcode experiments

Before closing the lesson, run these experiments: (1) Open Payments and enter a valid recipient and amount. (2) Tap Review Payment and observe the native sheet. (3) Swipe down to dismiss the sheet. (4) Open it again and tap Edit Details. (5) Change … [the first piece ends here]

## Part 2: Modal Lifecycle, Payment Confirmation & Debugging

NPay Engineering Lab · Continuing from Section 14. We've learned how SwiftUI presents sheets, alerts, confirmation dialogs, and full-screen covers. We've also introduced PaymentReviewSheet into NPay. Now we'll complete the lesson by investigating modal dismissal, state lifetime, duplicate-payment prevention, and coordination with programmatic navigation.

## 14. Xcode experiments — continued

Complete these experiments using the NPay application from Lesson 3.3.

| Experiment | What to observe |
|---|---|
| Open payment review | Native sheet appears |
| Swipe down | Sheet dismisses |
| Tap Edit Details | Returns to payment form |
| Change amount and reopen | Review reflects updated input |
| Confirm payment | Local transaction is recorded |
| Return to dashboard | Updated balance appears |

One particularly important experiment: change the available demo balance while a review is pending. At confirmation time, NPay must validate the amount again rather than trusting an earlier validation result.

## 15. The subtle problem — dismissing a sheet and navigating

Consider:

```swift
reviewDraft = nil
router.showPaymentSuccess(transactionID)
```

Both operations modify SwiftUI presentation state. The first requests dismissal of a sheet. The second requests navigation to a new destination. These are logically different transitions. SwiftUI coordinates both, but depending on the presentation hierarchy, requesting them together can lead to unexpected animation or presentation behavior.

**Better approach — use onDismiss.** We'll use a pending transaction ID to coordinate the transition.

```swift
@State private var reviewDraft: PaymentDraft?
@State private var pendingSuccessID: UUID?
```

Now attach the sheet:

```swift
.sheet(
    item: $reviewDraft,
    onDismiss: {
        guard let id = pendingSuccessID else {
            return
        }

        pendingSuccessID = nil
        router.showPaymentSuccess(id)
    }
) { draft in

    PaymentReviewSheet(draft: draft) {
        if let id = store.recordDemoPayment(
            recipient: draft.recipient,
            amountPaise: draft.amountPaise
        ) {
            pendingSuccessID = id
            reviewDraft = nil
        }
    }
}
```

**What changed?** We no longer request navigation immediately after setting reviewDraft to nil. Instead, we wait for the sheet's dismissal callback.

[Coordinated payment transition — a 6-stage stepper; only Stage 1 was shared: "1. Confirm tapped. PaymentReviewSheet invokes its confirmation closure."]

**Senior engineer insight.** A UI transition should be coordinated with the relevant presentation lifecycle, not arbitrary delays such as `DispatchQueue.main.asyncAfter`. Using fixed delays to synchronize animations is fragile.

## 16. Why confirmation must be idempotent

Now consider an important financial engineering problem. What if the user taps Confirm twice? In our local demo, that could potentially create two transactions if the confirmation action executes twice. We need to distinguish two ideas: UI protection — prevent repeated taps while processing; business idempotency — ensure the same logical payment request cannot be applied more than once. A disabled button can improve UI behavior, but it isn't sufficient to guarantee payment idempotency.

**UI protection example**

```swift
@State private var isProcessing = false

Button("Confirm Demo Payment") {
    guard !isProcessing else {
        return
    }

    isProcessing = true
    onConfirm()
}
.disabled(isProcessing)
```

This helps prevent repeated activation in the same view instance. But it does not establish durable idempotency.

**Production principle.** A real payment API should use a server-enforced idempotency mechanism, typically involving a stable request identifier and authoritative transaction handling. Our NPay demo will only model this concept locally.

## 17. What happens to sheet-local @State?

Suppose our review sheet contains `@State private var showDetails = false`. When the sheet is presented, SwiftUI associates that state with the sheet's view identity. When the sheet is dismissed and later recreated with a new identity, the state can reset.

[Interactive lifecycle experiment: "Sheet-local state lifetime — Present Review Sheet. Dismiss and reopen the sheet. This simulation resets the local expanded state for each new presentation."]

**What about the payment draft?** The payment draft belongs to the payment flow, not necessarily the sheet itself. If the user dismisses the review and returns to editing, we want the entered recipient and amount to remain. That state should stay in PaymentsScreen or another owner whose lifetime covers the editing workflow. We'll explore draft persistence more deeply in Lesson 3.5.

## 18. Prevent accidental dismissal

For some workflows, we may want to prevent swipe-to-dismiss. SwiftUI provides `.interactiveDismissDisabled()`. For example:

```swift
PaymentReviewSheet(draft: draft) {
    confirmPayment()
}
.interactiveDismissDisabled(isProcessing)
```

This prevents interactive dismissal while processing, where supported.

**Important nuance.** It does not guarantee that a presentation can never be dismissed. Application lifecycle changes and other system behavior still exist. Don't use modal presentation state as a security or transaction guarantee.

## 19. Behind the scenes — how presentation relates to the view hierarchy

A sheet is declared as a modifier on a view:

```swift
.sheet(item: $reviewDraft) { draft in
    PaymentReviewSheet(draft: draft)
}
```

The modifier describes a conditional presentation relationship. When the bound item becomes non-nil, SwiftUI coordinates presentation. When it becomes nil, SwiftUI coordinates dismissal.

[NPay modal architecture: PaymentsScreen (owns input and presentation state) → reviewDraft: PaymentDraft? (nil → no sheet · non-nil → sheet presented) → PaymentReviewSheet (temporary modal presentation).]

**Does .sheet() always create a new UIWindow?** No such guarantee exists in the public SwiftUI API. SwiftUI coordinates presentation through platform infrastructure, and its private implementation may change.

## 20. Senior engineer knowledge check

1. Why use sheet onDismiss before navigating to success? (To coordinate presentation and navigation transitions / To create a new process / To persist the payment)
2. Does disabling Confirm guarantee financial idempotency? (Yes / No)
3. Where should an editable payment draft live if it must survive sheet dismissal? (In a state owner outside the temporary sheet / Only inside the sheet)
4. What does sheet(item:) use to decide whether to present? (An optional Identifiable item / A network response only / A navigation path)
5. Does interactiveDismissDisabled guarantee that the app can never dismiss the sheet? (Yes / No)
6. Should payment processing live inside PaymentReviewSheet? (Yes / No)

## 21. Lesson 3.4 checkpoint

We've covered modal presentation, presentation state, sheet dismissal, detents, full-screen covers, alerts, confirmation dialogs, and how to coordinate payment confirmation with navigation. Our NPay payment flow now has a clear architecture: PaymentsScreen → PaymentReviewSheet → NPayStore → Sheet dismissal → NPayRouter → PaymentSuccessScreen. The complete Xcode integration is the remaining practical checkpoint: we need to combine these pieces into the working Lesson 3.3 project and verify the entire flow.

Next — Lesson 3.5: State Preservation Across Navigation. We'll investigate how to preserve payment drafts when switching tabs, dismissing sheets, or navigating between screens, and how to avoid accidental state resets.

## Complete Xcode code (note from the text)

[NPay — Unit 3, Lesson 3.4: Complete Xcode Code. Extends the 3.3 project; new feature: enter payment details, review them in a native sheet, confirm the demo transaction, and navigate to the success screen after the sheet dismisses. Payment flow: Payments tab (enter recipient and amount) → Review sheet (verify payment details) → Confirm (record one local demo transaction) → Sheet dismissal (coordinate presentation lifecycle) → Success screen (display transaction receipt). A ZIP (ContentView.swift, NPayApp.swift and a practice guide) was offered with the note that it had not been compiled. It was not shared; the code below replaces it.]

**Practice checklist** (Lesson 3.4 lab verification, 0 / 8)
- [ ] Open Payments and enter ravi@npay with ₹1,500.50
- [ ] Tap Review Payment and inspect the native sheet
- [ ] Dismiss the sheet and verify the form retains its input
- [ ] Reopen the sheet and confirm the demo payment
- [ ] Verify automatic navigation to Payment Success
- [ ] Return Home and verify balance ₹23,499.50
- [ ] Open History and inspect the new transaction
- [ ] Try invalid amounts and insufficient balance

Next: Lesson 3.5 — State Preservation Across Navigation. We'll preserve NPay payment drafts across tab switches and navigation changes, while investigating SwiftUI view identity and state lifetime.

## Complete code through Lesson 3.4 (authored)

Written from Sections 10–18 on top of the 3.3 code, and run unchanged in the simulator (`tools/sim3_4/App.swift`).
Everything except the three files below is unchanged from Lesson 3.3 (see `../lesson-3.3/lesson-3.3-text.md`).

Choices that go beyond the text (flagged): `isProcessing` lives in the sheet (Section 16), so the sheet applies
`interactiveDismissDisabled(isProcessing)` to its own content rather than the parent (Section 18); the keyboard is
dismissed before the review opens; on success the form is cleared in `onDismiss` before navigating; when the store
rejects the payment at confirm time, a flag is set and an alert ("Payment not recorded") is shown in `onDismiss`.

### Models/PaymentDraft.swift

```swift
import Foundation

struct PaymentDraft: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}
```

### Screens/PaymentsScreen.swift

```swift
import SwiftUI

struct PaymentsScreen: View {
    let store: NPayStore
    let router: NPayRouter

    @State private var recipient = ""
    @State private var amountText = ""

    @State private var reviewDraft: PaymentDraft?
    @State private var pendingSuccessID: UUID?
    @State private var paymentFailed = false
    @State private var showFailure = false

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    private var parsedAmount: Int? {
        Money.parsePaise(amountText)
    }

    private var isValid: Bool {
        let trimmed = recipient.trimmingCharacters(
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
                    text: $recipient
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
                    text: $amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )

                if !amountText.isEmpty && !isValid {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                Button("Review Payment") {
                    guard let amountPaise = parsedAmount else {
                        return
                    }

                    focusedField = nil
                    reviewDraft = PaymentDraft(
                        recipient: recipient,
                        amountPaise: amountPaise
                    )
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isValid)
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
            item: $reviewDraft,
            onDismiss: {
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    recipient = ""
                    amountText = ""
                    router.showPaymentSuccess(id)
                } else if paymentFailed {
                    paymentFailed = false
                    showFailure = true
                }
            }
        ) { draft in

            PaymentReviewSheet(draft: draft) {
                // The store validates again: the balance may have changed while the review was open
                if let id = store.recordDemoPayment(
                    recipient: draft.recipient,
                    amountPaise: draft.amountPaise
                ) {
                    pendingSuccessID = id
                } else {
                    paymentFailed = true
                }
                reviewDraft = nil
            }
        }
        .alert("Payment not recorded", isPresented: $showFailure) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("The amount is no longer within your available balance.")
        }
    }
}
```

### Screens/PaymentReviewSheet.swift

```swift
import SwiftUI

struct PaymentReviewSheet: View {
    let draft: PaymentDraft
    let onConfirm: () -> Void

    @State private var isProcessing = false

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: draft.recipient
            )

            LabeledContent(
                "Amount",
                value: Money.display(draft.amountPaise)
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

The deck (`index.html`, built by `tools/gen3_4.py`, 47 slides) follows all three pieces, grouped into 8 Parts: the
milestone (1), sheets (2–4), dismissal and detents (5, 6), covers, alerts, dialogs (7–9), NPay's review sheet (10–12),
dismiss then navigate (13, 15), safety in the sheet (14, 16–18), NPay after Lesson 3.4 (19, 21 and the complete code);
then recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_4/`, rerun with `sh tools/sim3_4/run.sh`; buttons
through accessibility and tabs selected as in 3.3; a swipe-down is reproduced by dismissing the presented controller,
which is what a completed swipe does; alert and dialog buttons run their action handlers. `PaymentsLab` hosts the real
PaymentsScreen with a store and router the driver can read.)
- SheetExperiment: `showSheet: true` on tap, `false` after the swipe-down; still one window with the sheet up
  (presented as an observation, not a contract). Screenshot at the medium detent.
- Full-screen cover, alert and confirmation dialog screenshots; the alert's Delete printed "Draft deleted"; the dialog
  listed Save Draft, Discard and a system-added Cancel; Save Draft printed "Draft saved".
- Section 12 vs Section 15, polled every 10 ms after Confirm: the same-update version had `paymentsPath` 1 while the
  sheet was still shown (9 ms); the onDismiss version kept it at 0 until the sheet was gone (588 ms). Both ended on
  Payment Success on iOS 26.5; the slide says so.
- Double Confirm (two activations back to back): without `isProcessing` 3 → 5 transactions, ₹21,999.00; with it 3 → 4,
  ₹23,499.50.
- Balance lowered to ₹1,000 while reviewing ₹1,500.50: nothing recorded, no navigation, the "Payment not recorded"
  alert (screenshot).
- Sheet-local `@State`: "Details expanded", then "Details collapsed" after closing and presenting again.
- Edit Details and swipe-down both left the form with "ravi@npay" and "1500.50".
- The 8-item checklist, all run: sheet showed Recipient ravi@npay and Amount ₹1,500.50; Payment Success after the sheet;
  Home ₹23,499.50; History "Sent to ravi@npay", -₹1,500.50; 0, 12.345 and 30000 keep Review Payment disabled.
  Screenshots of each step.

**Authored (flagged)**
- The complete code (choices listed above) and the slides that show it.
- Section 3's stages 2–6 and Section 15's coordinated-transition stages 2–6 (only stage 1 of each shared), marked
  conceptual.
- The experiments above (the text asks for the balance-change one; the timing poll, double tap and sheet-local state
  runs are ours), and the experiment harnesses `NaiveLab` (Section 12's code) and `UnguardedLab`.
- Review: the text's 6 questions (options reordered so answers vary) plus two predict items (double confirm; balance
  drop while reviewing) and a spaced item from 3.3; 3 of 9 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.5 as the text names it; Unit 5 for server-side idempotency,
  the curriculum's "HTTP, REST & idempotency"; Unit 4), lab, end slide.

**Wording**
- "Senior engineer question / insight / knowledge check" became neutral callouts and "Check your understanding".
