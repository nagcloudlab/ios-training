# Unit 4 · Lesson 4.7 — UI State Modeling & Async Payment Lifecycle

NPay iOS Engineering Masterclass · Part 1 + Part 2 · State Machines · Enums · async/await · MVVM Internals

In Lesson 4.6, we created SendPaymentUseCase and separated payment rules from SwiftUI.

Our architecture now follows:

PaymentsScreen → PaymentViewModel → SendPaymentUseCase → AccountRepository

But there's a new challenge.

When the user confirms a payment, the operation may take time. During that time, what should the screen display?

What happens if the payment fails? What if the user taps Confirm twice? What if the user navigates away while the operation is running?

Today, we'll learn to model these situations using an explicit UI state machine instead of multiple unrelated Boolean properties.

## Part 1 — Understanding UI State Machines

## 1. The problem with multiple Boolean flags

Imagine our ViewModel contains:
```swift
var isLoading = false
var isSuccess = false
var hasError = false
var isProcessing = false
```
These are four independent Boolean values.

That creates \(2^4 = 16\) possible combinations.

But most combinations don't make sense.

For example:

isLoading = true

isSuccess = true

hasError = true

isProcessing = false

Is NPay loading, successful, or failed?

The state is contradictory.

Interactive state experiment

Independent Boolean state

isLoading

isProcessing

isSuccess

hasError

Current combination

Idle

No obvious contradiction in this combination.

The issue is that unrelated Boolean properties allow invalid combinations to be represented.

## 2. Solution — model state using an enum

Instead of four Booleans, introduce one state:
```swift
enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success
    case failure
}
```
Now NPay can be in only one of these lifecycle states at a time.

Why is this better?

The enum represents mutually exclusive cases.

We can't accidentally set submitting and success simultaneously in the same enum value.

This connects directly to Unit 1, where we studied Swift enums and associated values.

## 3. Improve the enum with associated values

A successful payment should carry a receipt.

A failed payment should carry an error message.
```swift
enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
}
```
Now each state can carry relevant information.

For example:

state = .submitting

After success:

state = .success(record)

After failure:

state = .failure("Insufficient balance")

Senior engineer insight

An enum with associated values can represent a state machine much more precisely than multiple loosely related flags.

## 4. Visualize the payment lifecycle

NPay payment state machine

Idle

Waiting for user action

Validating

Check command and policy

Submitting

Awaiting payment operation

Success

PaymentRecord

Failure

Error information

Important nuance

This diagram shows the main submission flow.

In the real NPay application, form editing, review-sheet presentation, and payment execution are related but distinct state concerns.

We shouldn't force every UI detail into one enormous enum.

## 5. Interactive payment state machine

Let's simulate the lifecycle.

Current state

Idle

Idle

Ready for a new demo payment

Start paymentManual simulation of legal state transitions; no network request or payment is executed.

## 6. Model valid state transitions

A state machine is not just an enum.

It also defines which transitions are allowed.

For example:

| Current state | Event | Next state |
|---|---|---|
| Idle | Confirm payment | Validating |
| Validating | Validation passes | Submitting |
| Validating | Validation fails | Failure |
| Submitting | Operation succeeds | Success |
| Submitting | Operation fails | Failure |
| Failure | Retry or edit | Idle / Validating |
| Success | Start new payment | Idle |

Why does this matter?

Because application bugs often arise from unexpected transitions.

For example, the user shouldn't start another submission while the current submission is still processing.

## 7. Prevent duplicate submission

Let's add a computed property.

extension PaymentUIState {

var isBusy: Bool {

switch self {

case .validating, .submitting:

true

default:

false

}

}

}

Now the ViewModel can reject another submission:
```swift
guard !state.isBusy else {
    return
}
```
And SwiftUI can disable the button:

.disabled(viewModel.state.isBusy)

Important distinction

This protects the local UI workflow against overlapping submissions.

It does not guarantee financial idempotency.

A real payment backend must enforce idempotency using an authoritative request identifier.

## Part 2 — Integrating State Machines with MVVM

## 8. Build PaymentViewModel with explicit UI state

We'll extend our Lesson 4.6 ViewModel.

This is the core implementation for today's lesson.
```swift
import SwiftUI

enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)

    var isBusy: Bool {
        switch self {
        case .validating, .submitting:
            true
        default:
            false
        }
    }
}

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    private(set) var state: PaymentUIState = .idle

    private let sendPayment: SendPaymentUseCase

    init(sendPayment: SendPaymentUseCase) {
        self.sendPayment = sendPayment
    }

    func submit(
        _ command: SendPaymentCommand
    ) async {

        guard !state.isBusy else {
            return
        }

        state = .validating

        // Command value objects were validated at creation.
        state = .submitting

        do {
            let record = try await sendPayment.execute(command)

            recipient = ""
            amountText = ""
            state = .success(record)

        } catch PaymentDomainError.insufficientBalance {
            state = .failure("Insufficient balance")

        } catch PaymentDomainError.limitExceeded {
            state = .failure("Demo payment limit exceeded")

        } catch {
            state = .failure("Unable to complete payment")
        }
    }

    func reset() {
        guard !state.isBusy else { return }
        state = .idle
    }
}
```
What changed?

Previously, we used several properties:

isSubmitting

errorMessage

successRecord

Now one enum represents the submission lifecycle.

The ViewModel becomes easier to reason about.

Important nuance

The .validating state is currently very brief because the command has already been validated during construction.

It may not become visibly rendered before .submitting.

That's fine. We shouldn't insert artificial delays merely to make every state visible.

## 9. Behind the scenes — async/await and UI state

Consider:

state = .submitting

```swift
let record = try await sendPayment.execute(command)
```

state = .success(record)

The await marks a possible suspension point.

While the operation is suspended, the main actor can execute other eligible work.

This allows SwiftUI to present the submitting state while the asynchronous operation is in progress.

But does await automatically create a background thread?

No.

async/await is a concurrency abstraction, not a guarantee that work runs on a particular background thread.

The execution behavior depends on actor isolation and the called operation.

## 10. Visualize the asynchronous lifecycle

PaymentViewModel execution

Main actor

state = .submitting

await useCase.execute()

Operation may suspend

Repository actor

Processes isolated demo account state

Awaited result

PaymentRecord or thrown error

Main actor

state = .success(record) or .failure(message)

SwiftUI

Displays the new state

## 11. Render UI based on the state

Now the SwiftUI view can switch over the ViewModel's state.

@ViewBuilder
```swift
private var statusContent: some View {
    switch viewModel.state {

    case .idle:
        EmptyView()

    case .validating:
        Text("Validating payment...")

    case .submitting:
        ProgressView("Processing demo payment...")

    case .success:
        Label(
            "Payment recorded",
            systemImage: "checkmark.circle.fill"
        )
        .foregroundStyle(.green)

    case .failure(let message):
        Text(message)
            .foregroundStyle(.red)
    }
}
```
Why use a switch?

The compiler helps ensure that we handle every enum case.

If we introduce another state later, Swift can help identify switches that need updating.

This is a major benefit of modeling state with enums.

## 12. Connect submission to the review sheet

Remember our Unit 3 payment-review flow.

We must submit the exact immutable command that the user reviewed.

The review sheet can call:

Task {

await viewModel.submit(command)

}

But there's an important design issue.

What if the user dismisses the sheet while the operation is running?

Or switches tabs?

We need a deliberate task-lifetime and presentation policy.

For this stage, we'll keep the review sheet visible while submission is busy and disable interactive dismissal.

.interactiveDismissDisabled(

viewModel.state.isBusy

)

This improves the UI experience, but it isn't a transaction guarantee.

We'll also coordinate navigation only after the ViewModel reaches success.

## 13. Observe success and navigate

We want:

Submitting → Success → Dismiss Review → Navigate to Receipt

One approach is to inspect the state after awaiting submission.

Task {

await viewModel.submit(command)

if case .success(let record) = viewModel.state {

pendingSuccessID = record.id

reviewDraft = nil

}

}

Then in the sheet's onDismiss:
```swift
if let id = pendingSuccessID {
    pendingSuccessID = nil
    router.showPaymentSuccess(id)
}
```
Why not navigate immediately?

Because the sheet may still be presented.

We want to coordinate the modal dismissal with the navigation transition.

Senior engineer nuance

A production implementation should associate the completion with a specific submission request, rather than relying only on reading a mutable shared state after an await. We'll strengthen that contract when integrating the full feature and testing overlapping lifecycle events.

## 14. What happens if the payment fails?

Suppose the repository throws:

AccountRepositoryError.insufficientBalance

The use case or service maps the failure appropriately.

The ViewModel sets:

state = .failure("Insufficient balance")

The review sheet remains open.

The user sees the error.

No success route is appended.

Why is this important?

Because the UI must represent the authoritative operation result.

A button tap doesn't mean a payment succeeded.

Only a successful operation result does.

## 15. Cancellation — an advanced lifecycle problem

Imagine the user starts a payment and then leaves the screen.

Should the operation be canceled?

For an ordinary search request, cancellation may be straightforward.

For a financial payment, cancellation is more complicated.

Once a payment request has reached an authoritative backend, canceling the local Swift task doesn't necessarily cancel the financial operation.

Important principle

Task cancellation is not transaction reversal.

The application may need to query the payment status before deciding whether to retry or show failure.

For our in-memory demo, we'll keep the operation simple.

We'll explore cancellation and structured

*(The text breaks here; Section 13 continues below.)*

---

## Part 2 (continued): Cancellation, State Consistency & MVVM Testing

NPay iOS Engineering Masterclass · Continuing from Section 15 · Final Part of Lesson 4.7

We've implemented PaymentUIState with idle, validating, submitting, success, and failure.

Now we'll complete the lesson by investigating three senior-level engineering problems:

1. What happens when a payment is canceled while executing?

2. How do we prevent stale asynchronous results from corrupting the UI?

3. How do we test every state transition without launching SwiftUI?

## 15. Cancellation — continued

Consider this code:

Task {

await viewModel.submit(command)

}

The task begins an asynchronous payment operation.

But what if the user switches to History before the operation finishes?

The ViewModel may still receive a result.

Important distinction

Canceling a Swift task doesn't automatically undo an external payment.

A payment backend may have already accepted the request.

For financial operations, the application must distinguish:

- Cancellation of local UI work.

- Cancellation of a network request.

- Actual payment cancellation or reversal.

- Unknown payment status requiring reconciliation.

These are not interchangeable.

## 16. Model cancellation and unknown outcomes

Our initial state enum was:
```swift
enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
}
```
For a real payment application, we may also need a state representing an uncertain outcome.

Let's introduce:

case statusUnknown

This means the application cannot currently determine whether the operation completed.

It does not mean the payment failed.

NPay payment outcome model

Submitting

Request is in progress

Success

Confirmed record

Failure

Definitive rejection

Unknown

Needs status check

Why is this important?

Imagine NPay sends a payment request.

The server records the payment.

But the network connection drops before the response reaches the iPhone.

The app cannot safely conclude that the payment failed.

Blindly retrying could create a duplicate operation unless the backend enforces idempotency.

## 17. Improve the UI state enum

We'll extend our state machine.
```swift
enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown

    var isBusy: Bool {
        switch self {
        case .validating, .submitting:
            true
        default:
            false
        }
    }
}
```
Now the UI can represent an uncertain outcome explicitly.

For example:

case .statusUnknown:

ContentUnavailableView {

Label(

"Payment status unavailable",

systemImage: "questionmark.circle"

)

} description: {

Text(

"Check transaction status before retrying."

)

}

This is more accurate than displaying a generic failure for every network error.

## 18. Stale asynchronous results

Now consider another problem.

The user submits Payment A.

Before it completes, the user navigates away and begins a different payment flow.

Then Payment A finishes.

Should its result automatically update the new payment screen?

Not necessarily.

We need to associate asynchronous results with the operation that created them.

Introduce a request identifier
```swift
struct PaymentSubmission: Identifiable {
    let id: UUID
    let command: SendPaymentCommand
}
```
The ViewModel can track the active submission.
```swift
private var activeSubmissionID: UUID?
```
When a submission starts:
```swift
let submissionID = UUID()
```
activeSubmissionID = submissionID

When the operation completes, verify that its result still belongs to the active UI workflow.
```swift
guard activeSubmissionID == submissionID else {
    return
}
```
Important distinction

This protects the presentation layer against stale results.

It does not cancel or reverse the underlying payment operation.

## 19. Behind the scenes — stale-result protection

Two asynchronous UI workflows

Step 1 / 6

Payment A starts

ViewModel stores activeSubmissionID = A.

PreviousNext step

Senior engineer insight

A request ID used to associate UI results is different from a server-enforced idempotency key.

They may be related in a production design, but they serve different purposes.

## 20. A safer ViewModel submission contract

Our previous method returned Void and required the caller to inspect mutable state after awaiting it.

Let's improve that contract.

We'll return the specific operation result.
```swift
enum PaymentSubmissionResult {
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown
}
```
Now the ViewModel can return a result that belongs to the exact submitted command.

For this local demo, the repository provides definitive success or failure. We won't invent an unknown outcome for its ordinary validation errors.
```swift
@MainActor
func submit(
    _ command: SendPaymentCommand
) async -> PaymentSubmissionResult {

    guard !state.isBusy else {
        return .failure("A payment is already processing")
    }

    state = .validating
    state = .submitting

    do {
        let record = try await sendPayment.execute(command)

        state = .success(record)
        recipient = ""
        amountText = ""

        return .success(record)

    } catch PaymentDomainError.insufficientBalance {
        let message = "Insufficient balance"
        state = .failure(message)
        return .failure(message)

    } catch PaymentDomainError.limitExceeded {
        let message = "Demo payment limit exceeded"
        state = .failure(message)
        return .failure(message)

    } catch {
        let message = "Unable to complete demo payment"
        state = .failure(message)
        return .failure(message)
    }
}
```
This replaces the earlier submit(_:) method for the local demo.

What improved?

The caller receives a specific result rather than reading a potentially changed shared state.

The ViewModel still publishes UI state for rendering.

The two responsibilities are complementary.

For a real network implementation, errors must be classified carefully. An ambiguous transport failure should not automatically be mapped to a definitive payment failure.

## 21. Connect the result to the review sheet

Now the presentation coordinator can write:

Task {

let result = await viewModel.submit(command)

switch result {

case .success(let record):

pendingSuccessID = record.id

reviewDraft = nil

case .failure:

// Keep the review sheet visible.

// The ViewModel exposes the error state.

break

case .statusUnknown:

// Present a status-check workflow.

break

}

}

This preserves our existing NPay navigation design.

On success, the sheet dismisses and its onDismiss callback navigates to the receipt.

On failure, the user stays in the payment flow.

On unknown status, the application must not claim success or failure without reconciliation.

## 22. Testing the state machine

We want to verify legal transitions.

For example:

| Scenario | Expected state |
|---|---|
| Initial ViewModel | idle |
| Submission starts | submitting |
| Repository succeeds | success(record) |
| Repository rejects | failure(message) |
| Definitively unknown remote outcome | statusUnknown |

A simple failure test

Using our existing repository:
```swift
@MainActor
func testPaymentFailureState() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 10_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository,
        policy: PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )
    )

    let viewModel = PaymentViewModel(
        sendPayment: useCase
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 50_000)
    )

    let result = await viewModel.submit(command)

    if case .failure = result {
        print("Correct failure result")
    } else {
        assertionFailure("Expected failure")
    }

    if case .failure = viewModel.state {
        print("Correct UI state")
    } else {
        assertionFailure("Expected failure state")
    }
}
```
This verifies that the ViewModel reports failure and does not navigate or fabricate a successful receipt.

## 23. Why not store everything in one enormous enum?

Our PaymentUIState models submission status.

But NPay also has:

- Text-field focus.

- Review-sheet visibility.

- Navigation paths.

- Appearance preferences.

- Payment draft data.

Should we combine all of them into one enum?

No.

That would produce an overly complex state machine.

Better architecture

Payment Feature

Form state

Recipient and amount

Submission state

Idle, busy, result

Presentation state

Review sheet

Navigation state

Success route

The goal is not to minimize the number of state variables at all costs.

The goal is to make invalid combinations difficult to represent while keeping independent concerns separate.

## 24. Senior engineer knowledge check

UI State Modeling Assessment

*(Interactive quiz in the original.)*

**1. Why use an enum for payment lifecycle state?**

To represent mutually exclusive states

To create more threads

To replace the repository

**2. Does await guarantee that code runs on a background thread?**

Yes

No

**3. Does canceling a Swift task necessarily reverse a payment?**

Yes

No

**4. What does statusUnknown represent?**

The app cannot determine the authoritative outcome

Definitive payment failure

Guaranteed success

**5. Why return PaymentSubmissionResult from submit()?**

To associate the result with that invocation

To replace SwiftUI rendering

To persist data automatically

**6. Should a failed payment navigate to the success screen?**

Yes

No

**7. Does a UI submission guard guarantee server-side idempotency?**

Yes

No

**8. Should form focus and navigation paths be forced into PaymentUIState?**

Yes

No

Lesson 4.7 — Completed

We've completed both parts of UI State Modeling, including state machines, associated-value enums, async/await, submission guards, cancellation semantics, unknown payment outcomes, stale-result protection, and ViewModel testing.

## Integration through Lesson 4.7 (authored)

Sections 8, 11, 12, 17, 20 and 21 are applied to NPay:
- `PaymentUIState` (with `statusUnknown`) and `PaymentSubmissionResult` are added.
- The ViewModel replaces `isSubmitting` and `errorMessage` with `state`. `submit(_:)` returns a result (section 20).
  `reset()` runs before each new review.
- The review sheet takes the ViewModel and renders `statusContent` (section 11 plus the `statusUnknown` case). It
  disables Confirm and blocks interactive dismissal while busy (section 12). On failure it stays open showing the
  message (section 14).
- Confirm switches on the returned result (section 21): success stores the ID and dismisses; onDismiss navigates.
- The Payments screen's inline ViewModel error is removed (errors now show in the sheet). The "Enter a valid amount…"
  message stays.

Two fixes are ours, both found by running the text's design:
1. **`SendPaymentUseCase` maps `AccountRepositoryError` to `PaymentDomainError`.** Section 14 assumes the use case or
   service does this; 4.6's use case didn't, so a refused payment showed "Unable to complete demo payment".
2. **Edit Details is disabled while busy.** `interactiveDismissDisabled` only blocks the swipe; the sheet's own button
   could still dismiss it mid-payment.

The full app is `tools/sim4_7/App.swift`, below the "Complete code through Lesson 4.7" marker. The `#if DEBUG` lines
(the latency wrapper) are evidence hooks, not NPay code.

```swift
// Features/Payments/PaymentUIState.swift (Lesson 4.7, sections 17 and 20)

enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown

    var isBusy: Bool {
        switch self {
        case .validating, .submitting:
            true
        default:
            false
        }
    }
}

enum PaymentSubmissionResult {
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown
}

// Features/Payments/PaymentViewModel.swift (Lesson 4.7: one state replaces isSubmitting and errorMessage)

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    private(set) var state: PaymentUIState = .idle

    private let sendPayment: SendPaymentUseCase
    private let availableBalance: @MainActor () -> Int   // integration (ours): read-only balance

    init(
        sendPayment: SendPaymentUseCase,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) {
        self.sendPayment = sendPayment
        self.availableBalance = availableBalance
    }

    var availableBalancePaise: Int {
        availableBalance()
    }

    var parsedAmountPaise: Int? {
        Money.parsePaise(amountText)
    }

    // Lesson 4.2, section 7
    func validate(
        availableBalancePaise: Int
    ) -> Bool {

        guard let amount = parsedAmountPaise else {
            return false
        }

        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amount,
                balancePaise: availableBalancePaise
            )

            return true
        } catch {
            return false
        }
    }

    // Lesson 4.6 integration (ours): the immutable command the sheet shows and Confirm submits
    func prepareCommand() -> ValidatedPaymentRequest? {
        guard let paise = parsedAmountPaise,
              validate(availableBalancePaise: availableBalancePaise),
              let recipient = try? PaymentRecipient(recipient),
              let amount = try? PaymentAmount(paise: paise) else {
            return nil
        }

        return ValidatedPaymentRequest(
            command: SendPaymentCommand(recipient: recipient, amount: amount)
        )
    }

    // Section 20: returns the result of this submission; publishes state for rendering
    func submit(
        _ command: SendPaymentCommand
    ) async -> PaymentSubmissionResult {

        guard !state.isBusy else {
            return .failure("A payment is already processing")
        }

        state = .validating
        state = .submitting

        do {
            let record = try await sendPayment.execute(command)

            state = .success(record)
            recipient = ""
            amountText = ""

            return .success(record)

        } catch PaymentDomainError.insufficientBalance {
            let message = "Insufficient balance"
            state = .failure(message)
            return .failure(message)

        } catch PaymentDomainError.limitExceeded {
            let message = "Demo payment limit exceeded"
            state = .failure(message)
            return .failure(message)

        } catch {
            let message = "Unable to complete demo payment"
            state = .failure(message)
            return .failure(message)
        }
    }

    // Section 8
    func reset() {
        guard !state.isBusy else { return }
        state = .idle
    }

    // Lesson 3.4's Discard Draft
    func discardDraft() {
        recipient = ""
        amountText = ""
        reset()
    }
}

// Screens/PaymentReviewSheet.swift (shows the reviewed command and the submission state)

struct PaymentReviewSheet: View {
    let request: ValidatedPaymentRequest
    let viewModel: PaymentViewModel
    let onConfirm: () -> Void

    @Environment(\.dismiss) private var dismiss

    // Lesson 4.7, sections 11 and 17: render the submission state
    @ViewBuilder
    private var statusContent: some View {
        switch viewModel.state {

        case .idle:
            EmptyView()

        case .validating:
            Text("Validating payment...")

        case .submitting:
            ProgressView("Processing demo payment...")

        case .success:
            Label(
                "Payment recorded",
                systemImage: "checkmark.circle.fill"
            )
            .foregroundStyle(.green)

        case .failure(let message):
            Text(message)
                .foregroundStyle(.red)

        case .statusUnknown:
            ContentUnavailableView {
                Label(
                    "Payment status unavailable",
                    systemImage: "questionmark.circle"
                )
            } description: {
                Text(
                    "Check transaction status before retrying."
                )
            }
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: request.command.recipient.identifier
            )

            LabeledContent(
                "Amount",
                value: Money.display(request.command.amount.paise)
            )

            statusContent

            NPayButton("Confirm Demo Payment") {
                onConfirm()
            }
            .disabled(viewModel.state.isBusy)

            Button("Edit Details") {
                dismiss()
            }
            .buttonStyle(.bordered)
            .disabled(viewModel.state.isBusy)   // Lesson 4.7 (ours): the sheet stays while busy (section 12)
        }
        .padding()
        .presentationDetents([.medium, .large])
        .interactiveDismissDisabled(
            viewModel.state.isBusy
        )
    }
}
```

## Deck changes

The text came in three pieces: Part 1 (sections 1–7), Part 2 (8–15, breaking inside 15), and a continuation (15–24).

The deck (`index.html`, built by `tools/gen4_7.py`, 40 slides) has 7 Parts:
1. From flags to an enum (sections 1, 2, 3).
2. The state machine (4, 5, 6, 7).
3. State in the ViewModel (8, 9, 10).
4. Rendering and the review sheet (11, 12, 13, 14, 21).
5. Cancellation and unknown outcomes (15, 16, 17).
6. Stale results (18, 19, 20, 21).
7. Testing and scope (22, 23).

Then recap, review, next, lab and end.

**Evidence: Mac** (the text's ViewModel, section 20's `submit`, on 4.6's use case; Swift 6, Debug)
- States a view observes (Observation tracking, 200 ms latency, ours): `[submitting, success(150050)]`. `.validating`
  is never observable; 50 ms in, the state is `submitting`, `isBusy` true.
- Two concurrent submits: one success, the other "A payment is already processing", 1 payment recorded.
- ₹500 from ₹100 → "Unable to complete demo payment" (the unmapped repository error). Over the limit → "Demo payment
  limit exceeded".
- Section 22's test prints "Correct failure result" and "Correct UI state". It passes with the generic message (noted).
- Cancellation (ours, `Task.cancel()` 50 ms in):
  - Cancelled before recording → failure, 0 payments.
  - Cancelled after recording but before the reply → **failure, yet 1 payment recorded** (2349950). This is section
    16's statusUnknown case.
- Stale results (ours, section 18's check on a copy of the ViewModel, `startOver()` ours):
  - Without the check, the new flow shows `success(150050)` from payment A.
  - With the check it stays `idle`. Payment A is recorded either way.

**Evidence: simulator** (`sh tools/sim4_7/run.sh`)
- ₹1,500.50 → the sheet closes, Payment Recorded, 2349950.
- A refused payment (₹20,000, ₹10,000 removed during review) → the sheet stays with "Insufficient balance", no route.
  Edit Details keeps the draft.
- With 3 s latency (evidence hook), 0.8 s after Confirm: "Processing demo payment...", Confirm disabled, Edit Details
  disabled, swipe-to-dismiss blocked. Then Payment Recorded.
- Screenshots: submitting, failure.

**Authored (flagged)**
- The integration and both fixes; every run, including the latency, cancellation and stale-result harnesses.
- Diagrams for sections 4, 10 and 23.
- Interactive widgets (sections 1, 5, 19) replaced by arithmetic, the transition table and measured runs.
- Review: the text's 8 questions (options reordered) plus three more:
  - two predict items (observable states; the unmapped message);
  - a spaced item from 4.6.
  - 5 of 11 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab.
- The end slide's "Next: Lesson 4.8 — Modular Project Structure", from the 4.1 sequence; this text has no next-lesson
  line.

**Snippets:** the enum, `isBusy` and section 8's ViewModel compile. Some slide excerpts are condensed:
- section 20's `submit` and the `statusContent` switch (the full versions are above and compile in the app);
- the one-line catch shown as our fix.

**Wording**
- "Senior engineer insight / nuance / knowledge check" became neutral labels and "Check your understanding".
