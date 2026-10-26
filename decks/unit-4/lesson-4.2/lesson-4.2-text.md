# Unit 4 · Lesson 4.2 — MVVM Internals: Building NPay's First ViewModel

NPay iOS Engineering Masterclass · Incremental Refactoring · SwiftUI · MVVM · State Ownership

In Lesson 4.1, we extracted payment validation from SwiftUI into a standalone PaymentValidator.

Now we're going to introduce one of the most important concepts in professional iOS development: the ViewModel.

We'll build it incrementally, understand how it works behind the scenes, and connect it to our existing NPay application.

## 1. Our engineering problem

Currently, our PaymentsScreen performs several responsibilities:
```swift
struct PaymentsScreen: View {
    // Reads payment draft
    // Validates form
    // Presents review sheet
    // Calls NPayStore
    // Handles payment results
    // Coordinates navigation
}
```

This works, but the screen is doing too much.

What if tomorrow we add transaction limits, loading indicators, network errors, and biometric verification?

Our SwiftUI view would become increasingly complex.

The solution: Move screen-specific state and behavior into a PaymentViewModel, leaving the SwiftUI view focused on presentation.
Before and after MVVM
Before
PaymentsScreen

UI + validation + actions + state

NPayStore

After
PaymentsScreen

PaymentViewModel

PaymentValidator + NPayStore

## 2. What exactly is a ViewModel?

A ViewModel is an object that prepares and manages the state and behavior needed by a particular screen or feature.

For NPay, it might expose:
```swift
viewModel.recipient
viewModel.amountText
viewModel.isValid
viewModel.errorMessage
viewModel.submitPayment()
```

The SwiftUI view doesn't need to know every validation rule.

It simply reads the ViewModel's state and calls its methods.
Responsibilities
| PaymentsScreen | PaymentViewModel |
|---|---|
| TextField layout | Editable payment data |
| Buttons and colors | Validation state |
| Review sheet presentation | Preparing payment requests |
| Keyboard focus | Submission coordination |
| Navigation presentation | Payment result |
| Accessibility labels | User-facing error state |

Notice that the ViewModel doesn't decide where buttons are positioned or what colors they use.

Those remain presentation responsibilities.

## 3. First experiment — a ViewModel without SwiftUI

Let's begin with a simple class.

Create PaymentViewModel.swift.

```swift
import Foundation

@MainActor
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""

    var isValid: Bool {
        !recipient.isEmpty && !amountText.isEmpty
    }
}
```

This is ordinary Swift.

It has properties and a computed property.
Why a class?
A ViewModel often needs stable reference identity while its state changes.

A class provides reference semantics.
Why @MainActor?
The ViewModel manages state that will be consumed by the user interface.

Main-actor isolation helps coordinate those mutations safely with UI-related work.
Important nuance
```swift
@MainActor does not mean every operation is automatically fast.
```

Expensive synchronous work on the main actor can still block UI responsiveness.

## 4. The missing piece — how will SwiftUI observe changes?

Our class currently has no Observation support.

Let's add @Observable.

```swift
import SwiftUI

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""

    var isValid: Bool {
        !recipient.isEmpty && !amountText.isEmpty
    }
}
```

What is @Observable?
```swift
@Observable is a macro from Apple's Observation framework.
```

It enables observation of relevant property accesses and changes.

SwiftUI can use this to update views that depend on observable properties.
Behind the scenes
Conceptually, the macro expands the type to support observation tracking.

It isn't simply a runtime flag.

The compiler generates additional machinery that participates in the Observation system.

We'll examine this in much greater detail in Lesson 4.3.

## 5. Connect PaymentViewModel to SwiftUI

Now create a small experimental view.

```swift
import SwiftUI

struct PaymentMVVMLab: View {

    @State private var viewModel = PaymentViewModel()

    var body: some View {
        @Bindable var viewModel = viewModel

        VStack(spacing: 20) {

            TextField(
                "Recipient",
                text: $viewModel.recipient
            )
            .textFieldStyle(.roundedBorder)

            TextField(
                "Amount",
                text: $viewModel.amountText
            )
            .textFieldStyle(.roundedBorder)

            Button("Continue") {
                print("Payment requested")
            }
            .disabled(!viewModel.isValid)
        }
        .padding()
    }
}

#Preview {
    PaymentMVVMLab()
}
```

Run this in Xcode.

Type a recipient and an amount.

Observe when Continue becomes enabled.
What did we introduce?
- @State owns the observable ViewModel instance.
- @Bindable provides bindings to its editable properties.
- TextField writes through those bindings.
- SwiftUI tracks the ViewModel properties read by the view.

## 6. Behind the scenes — TextField to ViewModel

NPay MVVM input pipeline
*(Interactive stepper in the original, 6 stages; only stage 6 was shared.)*

6. Continue button updates
Its disabled state reflects viewModel.isValid.

## 7. Introduce proper payment validation

Our initial isValid only checks whether the fields are nonempty.

That's insufficient.

We already created PaymentValidator in Lesson 4.1.

Let's connect it.

First, parse the entered amount:

```swift
var parsedAmountPaise: Int? {
    Money.parsePaise(amountText)
}
```

Then validate against the balance:

```swift
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
```

What changed?
The ViewModel coordinates validation.

The validator owns the rules.

The SwiftUI view only asks for the result.

This is a meaningful separation of concerns.

## 8. How does the ViewModel communicate with NPayStore?

Our existing store owns the demo balance and transactions.

For now, we'll keep it as the source of truth.

The ViewModel can receive a store dependency through its initializer.

```swift
@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?

    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }
}
```

Why initializer injection?
Because the ViewModel explicitly declares the dependency it needs.

We don't want it to create a new independent store.

Incorrect:
```swift
private let store = NPayStore()
```

That could create a separate balance and transaction collection.

Correct:
```swift
init(store: NPayStore) {
    self.store = store
}
```

Now the ViewModel uses the same store instance as the rest of NPay.

## 9. Build the payment submission method

Let's add a method that performs a demo payment through the store.

```swift
func submitPayment() -> UUID? {

    guard let amount = Money.parsePaise(amountText) else {
        errorMessage = "Invalid amount"
        return nil
    }

    do {
        try PaymentValidator().validate(
            recipient: recipient,
            amountPaise: amount,
            balancePaise: store.balancePaise
        )
    } catch {
        errorMessage = "Payment validation failed"
        return nil
    }

    guard let transactionID = store.recordDemoPayment(
        recipient: recipient,
        amountPaise: amount
    ) else {
        errorMessage = "Unable to record payment"
        return nil
    }

    recipient = ""
    amountText = ""
    errorMessage = nil

    return transactionID
}
```

What does this method do?
It coordinates the workflow.

The validator checks the rules.

The store records the demo transaction.

The ViewModel updates its presentation state.

It returns the transaction ID so the caller can coordinate navigation.
Important design note
We're deliberately keeping navigation outside the ViewModel for now.

The router remains responsible for where the user goes.

## 10. The subtle issue — who owns the ViewModel?

In our small lab:
```swift
@State private var viewModel = PaymentViewModel()
```

This is appropriate when the view owns the model instance.

But our real NPay application has a shared NPayStore.

We should construct the ViewModel with the existing store.

One approach is to create it in a parent composition view and pass it down.

```swift
struct PaymentsFeatureRoot: View {
    @State private var viewModel: PaymentViewModel

    init(store: NPayStore) {
        _viewModel = State(
            initialValue: PaymentViewModel(store: store)
        )
    }

    var body: some View {
        PaymentsScreen(viewModel: viewModel)
    }
}
```

Why use _viewModel?
Because we're initializing the property wrapper's storage.

This is different from assigning to the wrapped property after initialization.
Important lifecycle nuance
```swift
@State preserves its stored value while the view identity remains stable.
```

If the parent later passes a different store instance to the same identity, the original state-owned ViewModel may remain. Dependencies should therefore be stable for that ownership lifetime, or the ownership design must explicitly handle replacement.

## 11. How does this connect to our payment-review sheet?

Remember Lesson 3.4.

Our flow is:

Payment Form → Review Sheet → Confirm → Success

The ViewModel should not immediately process the payment when the user taps Review.

Instead, it should prepare validated input.

Then the review sheet displays the snapshot.

Only after confirmation should the ViewModel submit the payment.
Proposed API
```swift
func preparePayment() -> PaymentDraft?
```

and:
```swift
func confirmPayment(_ draft: PaymentDraft) -> UUID?
```

This is cleaner than having a single method that both validates and executes immediately.
Why?
Because review and confirmation are distinct user actions.

The architecture should reflect that distinction.

## 12. Refactor PaymentViewModel into two stages

We'll define a validated payment request.

```swift
struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}
```

Now prepare the request:

```swift
func preparePayment() -> ValidatedPaymentRequest? {

    guard let amount = Money.parsePaise(amountText) else {
        errorMessage = "Invalid amount"
        return nil
    }

    do {
        try PaymentValidator().validate(
            recipient: recipient,
            amountPaise: amount,
            balancePaise: store.balancePaise
        )

        errorMessage = nil

        return ValidatedPaymentRequest(
            recipient: recipient,
            amountPaise: amount
        )

    } catch {
        errorMessage = "Please check payment details"
        return nil
    }
}
```

Then confirm:

```swift
func confirmPayment(
    _ request: ValidatedPaymentRequest
) -> UUID? {

    // Revalidate against current balance.
    do {
        try PaymentValidator().validate(
            recipient: request.recipient,
            amountPaise: request.amountPaise,
            balancePaise: store.balancePaise
        )
    } catch {
        errorMessage = "Payment details are no longer valid"
        return nil
    }

    guard let id = store.recordDemoPayment(
        recipient: request.recipient,
        amountPaise: request.amountPaise
    ) else {
        errorMessage = "Demo payment failed"
        return nil
    }

    recipient = ""
    amountText = ""
    errorMessage = nil

    return id
}
```

Why validate twice?
Because the available balance can change between opening the review sheet and confirming.

The first validation improves the user experience.

The second validation protects the application operation against stale input.

The store must still enforce its own rules as the final authority for this local simulation.

## 13. ViewModel versus Store — what's the difference?

| PaymentViewModel | NPayStore |
|---|---|
| Owns payment form state | Owns demo account state |
| Exposes validation feedback | Owns transaction collection |
| Prepares review requests | Records demo payments |
| Coordinates submission | Updates balance |
| Has screen/feature lifetime | Has application-root lifetime |

Important distinction
A ViewModel isn't automatically a repository or a domain service.

Its primary responsibility is to coordinate the state and behavior needed by a feature's presentation.

## 14. Senior engineer experiment — ViewModel identity

Let's investigate whether the ViewModel is recreated.

Add an initializer log:

```swift
init(store: NPayStore) {
    self.store = store
    print("PaymentViewModel initialized")
}
```

Now navigate between tabs.

Observe when initialization occurs.
What should you learn?
SwiftUI view structs can be recreated without necessarily recreating the state-owned ViewModel.

But if the owning view identity is removed and reestablished, the ViewModel can be initialized again.

This connects directly to our Unit 3 state-lifetime lessons.

## 15. Debugging Observation

Inside PaymentsScreen.body, temporarily add:
let _ = Self._printChanges()

Then type into the recipient field.

Observe the console.
Important nuance
A body evaluation doesn't necessarily mean SwiftUI recreated the ViewModel.

The view description and the ViewModel object have different lifetimes.

## 16. Architecture checkpoint

NPay payment architecture after Lesson 4.2

*(Part 1 ends here; Part 2 restarts at Section 16.)*

---

## Part 2: ViewModel Lifecycle, Integration & Engineering Review

NPay iOS Engineering Masterclass · Continuing from Section 16

We've created PaymentViewModel, introduced @Observable, connected it to NPayStore, and separated payment preparation from confirmation.

Now let's complete the lesson by understanding how a ViewModel lives in memory, how SwiftUI observes it, and how it fits into NPay's existing architecture.

## 16. Complete payment architecture

NPay — MVVM payment flow
PaymentsScreen

TextFields, buttons, focus, review sheet

PaymentViewModel

Form state, validation coordination, error feedback

PaymentValidator

Pure Swift payment validation rules

NPayStore

Shared demo balance and transaction state

NPayRouter

Navigates to payment success

Conceptual responsibility flow. The router is invoked by the presentation coordinator after the ViewModel reports success; it is not a data dependency of the store.
Important distinction
The ViewModel coordinates the payment feature, but it does not render views or own the application's navigation hierarchy.

The store manages the simulated account state.

The router manages navigation.

## 17. ViewModel lifecycle — who creates it, who retains it?

Let's revisit our implementation:
```swift
@State private var viewModel: PaymentViewModel
```

In the parent initializer:
```swift
init(store: NPayStore) {
    _viewModel = State(
        initialValue: PaymentViewModel(store: store)
    )
}
```

This establishes the parent as the ViewModel's state owner.
Behind the scenes
PaymentsFeatureRoot

Owns @State storage

PaymentViewModel instance

Stable reference while owner identity survives

PaymentsScreen

Reads ViewModel state and creates bindings

SwiftUI can reevaluate PaymentsScreen.body many times without creating a new ViewModel.

The ViewModel's lifetime is connected to its owning state storage, not to the number of times body executes.
Important caveat
The PaymentViewModel(store:) initializer expression can be evaluated when a parent view value is initialized, even if SwiftUI retains existing @State storage for the same identity. Do not rely on the number of initializer log messages alone to prove object lifetime.

## 18. Why is @State appropriate for an observable ViewModel?

In older SwiftUI applications, you frequently see:
@StateObject private var viewModel = PaymentViewModel()

That pattern is used with ObservableObject.

In modern iOS 17+ Observation-based applications:
```swift
@State private var viewModel = PaymentViewModel()
```

is appropriate when the view owns the observable instance.
Comparison
| Older observation model | Modern Observation |
|---|---|
| ObservableObject | @Observable |
| @Published | Observable stored properties |
| @StateObject | @State for owned observable models |
| @ObservedObject | Ordinary observable references, with @Bindable when bindings are needed |
| @EnvironmentObject | @Environment(Model.self) |

These are common corresponding patterns, not exact one-to-one replacements in every situation.

We'll examine their runtime behavior in Lesson 4.3.

## 19. What happens when the ViewModel property changes?

Suppose the user enters ravi@npay.
```swift
viewModel.recipient = "ravi@npay"
```

SwiftUI's Observation system tracks property access and mutation.

Views that depend on the changed property can be invalidated and reevaluated.
Interactive state-flow simulation
NPay PaymentViewModel state
Recipient

Amount

Derived ViewModel state
Recipient valid

Amount syntax valid

Continue Demo
Conceptual binding and derived-state demonstration; balance validation and actual payment processing are omitted here.
Senior engineer insight
A computed property such as isValid doesn't necessarily need its own stored observable value.

It can derive its result from the underlying properties.

Avoid storing duplicate state unless there is a specific reason.

## 20. Why shouldn't a ViewModel store every derived value?

Consider:
```swift
var recipient = ""
var amountText = ""
var isValid = false
```

Now the ViewModel must keep isValid synchronized whenever either input changes.

That creates additional opportunities for inconsistency.

Instead:
```swift
var isValid: Bool {
    !recipient.isEmpty && !amountText.isEmpty
}
```

This ensures validation reflects the current values.

For expensive derived computations, caching may be appropriate, but simple derived state is usually best expressed as a computed property.

## 21. The ViewModel should expose errors, not alerts

Suppose a payment fails.

Should the ViewModel directly call SwiftUI's .alert()?

No.

.alert() is a view modifier.

The ViewModel can expose an error state:
```swift
var errorMessage: String?
```

Then the SwiftUI view decides how to present it.

For example:

```swift
if let errorMessage = viewModel.errorMessage {
    Text(errorMessage)
        .font(.caption)
        .foregroundStyle(.red)
}
```

Later, we'll use a more structured error type rather than only a string.
Separation of responsibilities
The ViewModel determines that an error occurred.

The View decides whether to display inline text, an alert, or another accessible presentation.

## 22. Does a ViewModel need to know about NPayRouter?

Not necessarily.

There are different architectural approaches.

One approach injects a router into the ViewModel.

Another approach lets the ViewModel return a result, while the view or a coordinator performs navigation.

For our NPay curriculum, we'll use the second approach initially.
```swift
if let transactionID = viewModel.confirmPayment(request) {
    router.showPaymentSuccess(transactionID)
}
```

This keeps the ViewModel focused on payment behavior.

It also makes testing easier because the ViewModel doesn't need a navigation system to test payment validation and submission.

## 23. Memory and ARC — what happens when the screen disappears?

Our PaymentViewModel is a class.

Therefore, Swift's Automatic Reference Counting participates in managing its lifetime.

If the owning state storage releases the ViewModel and no other strong references remain, the instance can be deinitialized.
Experiment
Add:

```swift
deinit {
    print("PaymentViewModel deinitialized")
}
```

Then navigate between tabs and observe the console.
Important nuance
Switching tabs does not necessarily destroy the owning view identity.

Therefore, the ViewModel may remain alive.

Also, ARC deinitialization timing depends on actual reference ownership.

Do not assume a screen disappearing means its ViewModel is immediately released.

## 24. Avoiding reference cycles

Suppose the ViewModel stores a closure that captures the ViewModel strongly.

That can create a reference cycle.

For example, conceptually:
```swift
viewModel.callback = {
    viewModel.performAction()
}
```

If the ViewModel strongly owns the closure and the closure strongly captures the ViewModel, neither may be released.

In appropriate circumstances, a weak capture can break the cycle:
```swift
viewModel.callback = { [weak viewModel] in
    viewModel?.performAction()
}
```

Connect to Unit 1
This is why we studied ARC, strong references, weak references, and escaping closures.

SwiftUI does not eliminate reference-cycle risks in reference-type models.

## 25. Xcode practical verification

Lesson 4.2 lab checklist

*(Interactive checklist in the original.)*

- [ ] Create PaymentViewModel.swift
- [ ] Mark the ViewModel @MainActor and @Observable
- [ ] Move recipient and amountText into the ViewModel
- [ ] Bind TextFields using @Bindable
- [ ] Use PaymentValidator for domain validation
- [ ] Inject the existing NPayStore
- [ ] Prepare an immutable review request
- [ ] Confirm the demo payment through the ViewModel
- [ ] Return a transaction ID on success
- [ ] Keep navigation in NPayRouter
- [ ] Test ViewModel lifetime with logging
- [ ] Verify balance and history remain consistent

## 26. Senior engineer knowledge check

MVVM Engineering Assessment

*(Interactive quiz in the original.)*

**1. Does SwiftUI recreate the ViewModel every time body executes?**

Yes

No

**2. What is the purpose of @Bindable?**

Create bindings to observable properties

Create a database

Start a network request

**3. Why prefer computed validation over duplicated stored flags?**

To avoid synchronization errors

To disable Observation

To increase memory usage

**4. Should the ViewModel directly construct SwiftUI alert views?**

Yes

No

**5. Does @MainActor guarantee that expensive synchronous code won't block UI?**

Yes

No

**6. Can a ViewModel class participate in ARC reference cycles?**

Yes

No

Lesson 4.2 complete
We've covered ViewModel responsibilities, Observation, @Bindable, ViewModel ownership, initializer injection, derived state, error presentation, navigation coordination, ARC, and lifecycle debugging.

Our NPay architecture is evolving from a shared-store-driven interface into a maintainable MVVM design.

Next — Lesson 4.3: Observation Framework Internals. We'll investigate how @Observable works behind the scenes, how property access tracking differs from ObservableObject, how SwiftUI decides which views to invalidate, and how to debug Observation behavior in NPay.

## Integration through Lesson 4.2 (authored)

NPay refactored around `PaymentViewModel`:
- The payment form state (`recipient`, `amountText`) moves from NPayStore into the ViewModel. NPayStore loses
  `paymentDraft` and `clearPaymentDraft()` (Lesson 3.5's draft).
- `ValidatedPaymentRequest` replaces Lesson 3.4's `PaymentReview`.
- `PaymentsFeatureRoot` owns the ViewModel with `_viewModel = State(initialValue:)`. It also takes the router and
  passes it to the screen, which navigates on success (section 22).
- The 3.4 failure alert is replaced by the ViewModel's inline `errorMessage` (section 21).
- The Payments tab shows `PaymentsFeatureRoot(store:router:)`.

The full app is `tools/sim4_2/App.swift`, below the "Complete code through Lesson 4.2" marker. The init/deinit prints
are the text's section 14/23 experiments. The `#if DEBUG` lines are evidence hooks for the test driver, not NPay code.

```swift
// Features/Payments/ValidatedPaymentRequest.swift (Lesson 4.2, section 12; replaces Lesson 3.4's PaymentReview)

struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}

// Features/Payments/PaymentViewModel.swift (Lesson 4.2: the form state moves here from NPayStore)

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?

    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
        print("PaymentViewModel initialized")   // section 14 experiment
        #if DEBUG
        NPayDebug.track(self)
        #endif
    }

    deinit {
        print("PaymentViewModel deinitialized")   // section 23 experiment
    }

    var availableBalancePaise: Int {
        store.balancePaise
    }

    var parsedAmountPaise: Int? {
        Money.parsePaise(amountText)
    }

    // Section 7: the validator owns the rules; the ViewModel coordinates
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

    // Section 12, stage 1: validate and prepare an immutable review request
    func preparePayment() -> ValidatedPaymentRequest? {

        guard let amount = Money.parsePaise(amountText) else {
            errorMessage = "Invalid amount"
            return nil
        }

        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amount,
                balancePaise: store.balancePaise
            )

            errorMessage = nil

            return ValidatedPaymentRequest(
                recipient: recipient,
                amountPaise: amount
            )

        } catch {
            errorMessage = "Please check payment details"
            return nil
        }
    }

    // Section 12, stage 2: revalidate, record, clear the form
    func confirmPayment(
        _ request: ValidatedPaymentRequest
    ) -> UUID? {

        // Revalidate against current balance.
        do {
            try PaymentValidator().validate(
                recipient: request.recipient,
                amountPaise: request.amountPaise,
                balancePaise: store.balancePaise
            )
        } catch {
            errorMessage = "Payment details are no longer valid"
            return nil
        }

        guard let id = store.recordDemoPayment(
            recipient: request.recipient,
            amountPaise: request.amountPaise
        ) else {
            errorMessage = "Demo payment failed"
            return nil
        }

        recipient = ""
        amountText = ""
        errorMessage = nil

        return id
    }

    // Lesson 3.4's Discard Draft, now a ViewModel action
    func discardDraft() {
        recipient = ""
        amountText = ""
        errorMessage = nil
    }
}

// Features/Payments/PaymentsFeatureRoot.swift (section 10; also passes the router for navigation, section 22)

struct PaymentsFeatureRoot: View {
    @State private var viewModel: PaymentViewModel
    let router: NPayRouter

    init(store: NPayStore, router: NPayRouter) {
        _viewModel = State(
            initialValue: PaymentViewModel(store: store)
        )
        self.router = router
    }

    var body: some View {
        PaymentsScreen(viewModel: viewModel, router: router)
    }
}

// Screens/PaymentsScreen.swift (presentation only: layout, focus, the review sheet, navigation on success)

struct PaymentsScreen: View {
    @Bindable var viewModel: PaymentViewModel
    let router: NPayRouter

    @State private var review: ValidatedPaymentRequest?
    @State private var pendingSuccessID: UUID?
    @State private var confirmDiscard = false

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    var body: some View {
        #if DEBUG
        let _ = NPayDebug.logChanges ? Self._printChanges() : ()   // section 15 experiment
        #endif

        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text(
                    "Available: \(Money.display(viewModel.availableBalancePaise))"
                )
                .foregroundStyle(.secondary)

                TextField(
                    "Recipient ID",
                    text: $viewModel.recipient
                )
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .recipient
                )
                .accessibilityIdentifier(NPayAccessibilityID.recipientField)
                .accessibilityLabel("Recipient")
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .amount
                }

                TextField(
                    "Amount (₹)",
                    text: $viewModel.amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )
                .accessibilityIdentifier(NPayAccessibilityID.amountField)
                .accessibilityLabel("Amount in rupees")

                // Section 21: the ViewModel reports the error; the view decides how to show it
                if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundStyle(.red)
                } else if !viewModel.amountText.isEmpty
                            && !viewModel.validate(availableBalancePaise: viewModel.availableBalancePaise) {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                NPayButton("Review Payment", symbol: "doc.text.magnifyingglass") {
                    focusedField = nil
                    review = viewModel.preparePayment()
                }
                .disabled(!viewModel.validate(availableBalancePaise: viewModel.availableBalancePaise))
                .accessibilityIdentifier(NPayAccessibilityID.sendButton)

                Button("Discard Draft", role: .destructive) {
                    confirmDiscard = true
                }
                .disabled(viewModel.recipient.isEmpty && viewModel.amountText.isEmpty)
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
                // Section 22: the ViewModel returned an ID; the view asks the router to navigate
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    router.showPaymentSuccess(id)
                }
            }
        ) { request in

            PaymentReviewSheet(request: request) {
                pendingSuccessID = viewModel.confirmPayment(request)
                self.review = nil
            }
        }
        .alert("Discard payment draft?", isPresented: $confirmDiscard) {
            Button("Discard", role: .destructive) {
                viewModel.discardDraft()
            }

            Button("Cancel", role: .cancel) {}
        }
    }
}

// Screens/PaymentReviewSheet.swift (shows the validated request, not the live form)

struct PaymentReviewSheet: View {
    let request: ValidatedPaymentRequest
    let onConfirm: () -> Void

    @State private var isProcessing = false

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: request.recipient
            )

            LabeledContent(
                "Amount",
                value: Money.display(request.amountPaise)
            )

            NPayButton("Confirm Demo Payment") {
                guard !isProcessing else {
                    return
                }

                isProcessing = true
                onConfirm()
            }
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

The deck (`index.html`, built by `tools/gen4_2.py`, 46 slides) has 8 Parts:
1. Why a ViewModel (sections 1, 2).
2. A first ViewModel (3, 4).
3. Binding a view to it (5, 6).
4. Rules and dependencies (7, 8).
5. Submitting in two stages (9, 11, 12).
6. Ownership and lifetime (10, 13, 14, 15, 17, 18).
7. State, errors, navigation (19, 20, 21, 22).
8. Memory and integration (23, 24, 16, 25).

Then recap, review, next, lab and end. Part 2 of the text restarts at Section 16; Part 1's unfinished Section 16
("Architecture checkpoint") is covered by Part 2's Section 16.

**Evidence** (iPhone 17 simulator; `sh tools/sim4_2/run.sh`, one launch per experiment). The text's first ViewModel
(sections 4–5) is renamed `LabPaymentViewModel` in the evidence app so it can coexist with the integrated one.
- Section 5 lab: Continue disabled → disabled with only a recipient → enabled with "1" → disabled when cleared →
  **enabled with "abc"** → "Payment requested".
- Section 7: the non-empty `isValid` accepts "abc", a blank recipient, ₹30,000 and 0; `validate(availableBalancePaise:)`
  rejects all four.
- Section 8: a ViewModel with `private let store = NPayStore()` paid ₹1,500.50 into its own store (2,349,950).
  NPay's store stayed at 2,500,000 and Home showed ₹25,000.00. With the injected store, Home showed ₹23,499.50.
- Section 12: prepare ₹20,000, then ₹10,000 recorded elsewhere (balance 1,500,000), then Confirm. The balance was
  unchanged, the sheet closed, and "Payment details are no longer valid" appeared (screenshot).
- Sections 14/17: over six tab switches the initializer ran 7 times, and 9 times after typing and leaving. The draft "ra"
  was kept. At most one extra instance was alive briefly, and each extra one deinitialized at once.
- Section 15: typing two characters printed "PaymentsScreen: \PaymentViewModel.recipient changed." twice.
- Section 23: switching tabs never deinitialized the draft-holding ViewModel. A lab `if` removing PaymentsFeatureRoot
  printed "PaymentViewModel deinitialized"; reopening created a new one.
- Section 24 (Mac): a strong self-capture gave no deinit; a weak capture deinitialized.
- Section 25: the draft kept across tabs, then 2,349,950 paise, 4 transactions, the router pushed success, Home
  ₹23,499.50, History "Sent to ravi@npay" on top, and an empty form after success.
- Section 1: sizes before → after:
  - PaymentsScreen: 160 → 120 lines; 6 → 4 state properties; 14 → 0 uses of the store.
  - PaymentViewModel: 117 lines.

**Authored (flagged)**
- The integration above, and every experiment.
- Section 6: stages 1–5 of the input pipeline (only stage 6 was shared).
- Section 13's "moved in our code" card. The `PaymentsFeatureRoot(store:router:)` signature: the text's takes only
  the store.
- Review: the text's 6 questions (options reordered) plus three more:
  - two predict items (a private store; init count vs kept draft);
  - a spaced item from 4.1.
  - 3 of 9 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab, end slide.

**Snippets**
- Outlines are shown as outlines and don't compile alone: section 2's property list, section 12's method signatures
  (the full methods are in the text and in the app), and section 20's stored-vs-computed pair (both `isValid`s).
- Section 9's `submitPayment()` is condensed on the slide.
- Every other slide snippet typechecks. The full ViewModel compiles in the app.

**Wording**
- "Senior engineer experiment / insight / knowledge check" became neutral labels and "Check your understanding".
