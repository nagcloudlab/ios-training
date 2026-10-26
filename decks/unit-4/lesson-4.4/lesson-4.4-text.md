# Unit 4 · Lesson 4.4 — Dependency Injection in iOS

NPay iOS Engineering Masterclass · Constructor Injection · Protocols · Composition Root · Runtime Internals

In Lesson 4.3, we learned how @Observable enables SwiftUI to react to ViewModel changes.

Now we'll solve a different problem.

Our PaymentViewModel currently depends on NPayStore:
```swift
@MainActor
@Observable
final class PaymentViewModel {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }
}
```
This works. But suppose tomorrow we replace local demo payments with a backend API.

Would we need to rewrite PaymentViewModel?

Our goal today is to make NPay's payment feature independent of how payments are implemented.

We'll learn dependency injection incrementally, beginning with ordinary Swift objects and progressing toward a testable MVVM architecture.

## 1. First, understand the problem

Imagine three environments for NPay:

One PaymentViewModel, three implementations

PaymentViewModel

Payment form state and submission coordination

PaymentService protocol

Defines the contract

Demo

Local simulation

Mock

Controlled test

API

Future backend

The ViewModel shouldn't need to know which implementation it receives.

That's the central idea behind dependency injection.

## 2. What is dependency injection?

A dependency is an object or capability another component needs to do its work.

Dependency injection means supplying that dependency from outside rather than constructing it internally.

Compare these two examples.

Without dependency injection
```swift
final class PaymentViewModel {
    private let service = DemoPaymentService()
}
```
The ViewModel creates its own dependency.

That means it's coupled to DemoPaymentService.

With dependency injection
```swift
final class PaymentViewModel {
    private let service: PaymentService

    init(service: PaymentService) {
        self.service = service
    }
}
```
Now the ViewModel receives its dependency.

The caller decides which implementation to supply.

Connect to Unit 1

This uses three familiar Swift concepts: protocols, initializer parameters, and reference/value types.

Dependency injection is primarily an architectural pattern, not a special SwiftUI feature.

## 3. Build our first dependency contract

Create PaymentService.swift.
```swift
import Foundation

struct PaymentRequest {
    let recipient: String
    let amountPaise: Int
}

struct PaymentReceipt {
    let transactionID: UUID
    let recipient: String
    let amountPaise: Int
}

@MainActor
protocol PaymentService {
    func send(_ request: PaymentRequest) async throws -> PaymentReceipt
}
```
Let's examine this carefully.

PaymentRequest represents the validated input we intend to submit.

PaymentReceipt represents the result returned after the operation.

PaymentService defines the behavior without specifying how it's implemented.

We use async throws because a future payment implementation may involve asynchronous work and failures. The @MainActor isolation is a deliberate simplification for this local lesson; we'll revisit concurrency boundaries when networking is introduced.

## 4. Create the demo implementation

Our demo service should use the existing shared NPayStore rather than creating a second balance.
```swift
import Foundation

enum PaymentServiceError: Error {
    case rejected
}

@MainActor
final class DemoPaymentService: PaymentService {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        guard let id = store.recordDemoPayment(
            recipient: request.recipient,
            amountPaise: request.amountPaise
        ) else {
            throw PaymentServiceError.rejected
        }

        return PaymentReceipt(
            transactionID: id,
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )
    }
}
```
This assumes the NPayStore.recordDemoPayment method from our earlier lessons returns an optional UUID.

What is important here?

DemoPaymentService doesn't own a new account balance.

It receives the same NPayStore instance that our Home and History screens use.

That preserves the single source of truth.

## 5. Behind the scenes — who creates whom?

Without dependency injection:

PaymentViewModel

Creates DemoPaymentService internally

Tightly coupled to implementation

With dependency injection:

NPay application composition root

Creates and connects objects

PaymentViewModel

DemoPaymentService

PaymentService contract

The ViewModel depends on the abstraction

The diagram distinguishes object creation from code dependencies. The composition root constructs the concrete service and supplies it to the ViewModel.

## 6. Refactor PaymentViewModel

We'll keep the input properties and validation concepts from Lesson 4.2, but replace the direct store dependency with a service.
```swift
import SwiftUI

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?
    var isSubmitting = false

    private let service: any PaymentService

    init(service: any PaymentService) {
        self.service = service
    }

    func submit() async -> PaymentReceipt? {
        guard !isSubmitting else {
            return nil
        }

        guard let amount = Money.parsePaise(amountText),
              amount > 0,
              !recipient.trimmingCharacters(
                in: .whitespacesAndNewlines
              ).isEmpty else {
            errorMessage = "Check your payment details."
            return nil
        }

        let request = PaymentRequest(
            recipient: recipient.trimmingCharacters(
                in: .whitespacesAndNewlines
            ),
            amountPaise: amount
        )

        isSubmitting = true
        defer { isSubmitting = false }

        do {
            let receipt = try await service.send(request)

            recipient = ""
            amountText = ""
            errorMessage = nil

            return receipt
        } catch {
            errorMessage = "Payment could not be completed."
            return nil
        }
    }
}
```
Notice that the ViewModel no longer knows about DemoPaymentService or NPayStore.

It only knows about PaymentService.

The service implementation remains responsible for enforcing balance and payment rules at execution time.

For now, this is a standalone submission experiment. We'll reconnect the review-sheet snapshot and confirmation flow during integration rather than allowing the ViewModel to bypass payment review.

## 7. Why use any PaymentService?

In Swift, PaymentService is a protocol.

When we write:
```swift
private let service: any PaymentService
```
we're storing a value whose concrete type conforms to that protocol.

The concrete implementation could be:

DemoPaymentService

MockPaymentService

The any keyword makes existential type usage explicit.

Is a protocol required for all dependency injection?

No.

You can inject concrete types directly.

Protocols are useful when multiple implementations, testing, or abstraction boundaries justify them.

Creating a protocol for every class can add unnecessary complexity.

## 8. Create a mock payment service

Now let's see why dependency injection is useful.
```swift
import Foundation

@MainActor
final class MockPaymentService: PaymentService {

    var shouldFail = false
    private(set) var requests: [PaymentRequest] = []

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        requests.append(request)

        if shouldFail {
            throw PaymentServiceError.rejected
        }

        return PaymentReceipt(
            transactionID: UUID(),
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )
    }
}
```
We can now test the ViewModel without modifying a real store or making a network request.

The mock records the requests it receives and can deliberately fail.

## 9. Interactive dependency injection experiment

Choose the injected payment implementation

DemoPaymentService — local transaction

MockPaymentService — forced success

MockPaymentService — forced failure

Unchanged ViewModel call

await viewModel.submit()

Simulate submission

The ViewModel contract remains unchanged. Only the injected implementation differs.

## 10. The composition root — where dependencies are assembled

Let's create a small factory.
```swift
@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        store: NPayStore
    ) -> PaymentViewModel {

        let service = DemoPaymentService(store: store)

        return PaymentViewModel(service: service)
    }
}
```
The factory centralizes construction.

For our existing tab-based application, the root owns NPayStore and can use the factory to create a stable payment ViewModel.

For example, a payment feature root can own the ViewModel using @State and pass it to PaymentsScreen.

We must avoid creating the ViewModel repeatedly inside body, and preserve the intended draft lifetime across tab changes.

## 11. Constructor injection versus environment injection

We've now learned two dependency injection approaches.

| Constructor injection | Environment injection |
|---|---|
| Dependency passed in initializer | Dependency supplied through view hierarchy |
| Explicit at call site | Convenient for descendants |
| Good for ViewModels and services | Good for shared UI context |
| Easy to reason about required dependencies | Requires deliberate environment setup |

For NPay, we'll generally use constructor injection for payment services and repositories, while retaining environment injection for appropriate presentation preferences.

Neither mechanism automatically manages persistence or application security.

## 12. Behind the scenes — dependency lifetime and ARC

Consider:

let service = DemoPaymentService(store: store)

let viewModel = PaymentViewModel(service: service)

Both are reference-type objects.

The ViewModel holds a strong reference to its service, and the service holds a strong reference to the store.

PaymentViewModel

DemoPaymentService

NPayStore

Strong reference relationships in this example. The application root also owns the shared store.

This chain doesn't inherently create a retain cycle because the store doesn't reference the ViewModel.

ARC releases objects when their strong ownership relationships no longer keep them alive.

Dependency injection doesn't eliminate ARC concerns, but explicit ownership helps us reason about them.

## 13. Xcode practical lab

Create these files in your NPay project:
```text
NPay/
├── Domain/
│   ├── PaymentRequest.swift
│   └── PaymentService.swift
├── Services/
│   ├── DemoPaymentService.swift
│   └── MockPaymentService.swift
├── Features/Payments/
│   └── PaymentViewModel.swift
└── App/
    └── NPayFactory.swift
```
Keep the existing NPayStore, router, and screens.

For the first experiment, instantiate the ViewModel using the demo service. Then replace it with the mock and observe the result.

Do not delete the payment review flow; this lab focuses on changing the dependency behind the submission operation.

Verification checklist

Lesson 4.4 lab progress

0 / 10

Define PaymentRequest and PaymentReceipt

Define the PaymentService protocol

Implement DemoPaymentService using the existing store

Implement MockPaymentService

Inject the service into PaymentViewModel

Verify a demo payment updates the shared balance

Verify the mock can return success

Verify the mock can return failure

Verify errorMessage updates correctly

Confirm the ViewModel contains no concrete service construction

## 14. Senior engineer knowledge check

*(Part 1 ends here; Part 2 restarts at Section 14.)*

---

## Part 2: Dependency Injection Internals & Engineering Review

NPay iOS Engineering Masterclass · Continuing from Section 14

We've created PaymentService, implemented demo and mock services, and injected them into PaymentViewModel.

Now we'll finish the lesson by investigating dependency ownership, object lifetimes, testing, and the difference between dependency injection and dependency inversion.

## 14. Senior engineer knowledge check

Dependency Injection Assessment

*(Interactive quiz in the original.)*

**1. What is dependency injection?**

Supplying dependencies from outside a component

Creating every dependency inside the ViewModel

Storing dependencies in UserDefaults

**2. Does dependency injection always require a protocol?**

Yes

No

**3. Why use a MockPaymentService?**

To control behavior during testing

To replace the iOS runtime

To persist transactions automatically

**4. Who should create DemoPaymentService?**

The composition root or factory

Every TextField

BalanceCard

**5. Should DemoPaymentService create an independent NPayStore?**

Yes

No

**6. Does dependency injection automatically prevent retain cycles?**

Yes

No

**7. What does any PaymentService represent?**

An existential value conforming to PaymentService

A new background thread

A SwiftUI navigation destination

## 15. Dependency Injection versus Dependency Inversion

These terms sound similar, but they describe different ideas.

Dependency Injection (DI) is a technique for supplying dependencies to a component.

Dependency Inversion Principle (DIP) is a design principle: high-level policy should not depend directly on low-level implementation details; both should depend on appropriate abstractions.

Before dependency inversion

PaymentViewModel

High-level presentation behavior

DemoPaymentService

Concrete implementation dependency

After dependency inversion

PaymentViewModel

PaymentService protocol

Abstraction

DemoPaymentService

Conforms to the abstraction

Arrows represent source-code dependencies and protocol conformance, not the runtime sequence of method calls.

Important insight

Dependency injection and dependency inversion often work together, but neither automatically guarantees the other.

You can inject a concrete class without introducing a protocol.

You can also define an abstraction but still construct the concrete implementation inside the consumer, undermining the intended separation.

## 16. What actually happens at runtime?

Consider:

let service = DemoPaymentService(store: store)

let viewModel = PaymentViewModel(

service: service

)

Then:

await viewModel.submit()

Let's trace the call.

NPay runtime dependency flow

*(Interactive stepper in the original, 7 stages; only stage 1 was shared.)*

1. Composition root creates objects

NPayStore, DemoPaymentService, and PaymentViewModel are assembled.

PreviousNext step

Does any PaymentService create a new service instance?

No.

Assigning a class instance to an existential-typed property does not construct a new service object.

The existential holds a value conforming to the protocol and supports calling its requirements. The precise compiler representation and dispatch optimizations are implementation details.

## 17. Dependency lifetimes — transient, feature, application

Dependency injection also requires us to think about object lifetime.

| Lifetime | NPay example |
|---|---|
| Transient | A short-lived payment validation helper |
| Feature | PaymentViewModel for an active payment workflow |
| Application | Shared NPayStore and NPayRouter owned by the root |

These are design choices, not automatic SwiftUI service scopes.

Why does lifetime matter?

Suppose each payment screen creates a new NPayStore.

The balance could become inconsistent between Home and Payments.

Conversely, making every temporary UI helper application-wide would unnecessarily extend its lifetime.

The correct lifetime should match the responsibility.

## 18. Testing dependency injection without SwiftUI

Let's test our ViewModel with a mock service.

The mock from Part 1 records requests and can deliberately fail.
```swift
import Foundation

@MainActor
func runPaymentViewModelLab() async {
    let mock = MockPaymentService()

    let viewModel = PaymentViewModel(
        service: mock
    )

    viewModel.recipient = "ravi@npay"
    viewModel.amountText = "1500.50"

    let receipt = await viewModel.submit()

    assert(receipt != nil)
    assert(mock.requests.count == 1)
    assert(mock.requests[0].amountPaise == 150_050)

    print("PaymentViewModel test passed")
}
```
What does this prove?

The ViewModel can submit a payment through its protocol dependency.

The mock captures the request.

We can verify that ₹1,500.50 was converted into 150,050 paise.

We didn't need to launch NPay, display a sheet, or make a network request.

Failure-path experiment
```swift
@MainActor
func runPaymentFailureLab() async {
    let mock = MockPaymentService()
    mock.shouldFail = true

    let viewModel = PaymentViewModel(
        service: mock
    )

    viewModel.recipient = "ravi@npay"
    viewModel.amountText = "1500"

    let receipt = await viewModel.submit()

    assert(receipt == nil)
    assert(viewModel.errorMessage != nil)
    assert(viewModel.isSubmitting == false)

    print("Failure-path test passed")
}
```
This is the main benefit of our design: we can test success and failure deterministically without changing the ViewModel's implementation.

These examples use assertions for learning. We'll introduce a proper automated test suite in Lesson 4.9.

## 19. Should NPay use a dependency injection framework?

Not yet.

Our application currently needs only a few shared dependencies.

A simple factory or composition root is sufficient.

For example:
```swift
@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        store: NPayStore
    ) -> PaymentViewModel {

        let service = DemoPaymentService(
            store: store
        )

        return PaymentViewModel(
            service: service
        )
    }
}
```
A dependency injection container may become useful when construction rules, scopes, and dependency graphs grow complex.

But introducing a framework too early can hide the very ownership and initialization concepts we're trying to master.

## 20. A subtle issue — protocol abstractions are not always free

Using protocols can improve flexibility and testability.

However, every abstraction adds a contract that must be maintained.

Suppose NPay has only one simple, stable formatter.

Creating a protocol, factory, mock, and container for it might add more complexity than value.

Practical decision

Use a protocol when it provides a meaningful boundary, such as replacing a payment implementation, isolating infrastructure, or testing important behavior.

Prefer a concrete type when the dependency is simple and unlikely to benefit from multiple implementations.

Good architecture is about useful boundaries, not maximizing the number of protocols.

## 21. Final NPay architecture after Lesson 4.4

NPayRootView / Composition Root

Owns shared application dependencies

PaymentsScreen

SwiftUI presentation

PaymentViewModel

Form state and submission coordination

PaymentService protocol

Abstract payment contract

DemoPaymentService

Uses shared NPayStore

Our PaymentViewModel is now independent of the concrete demo payment implementation.

When we introduce a backend in Unit 5, we'll have a clearer boundary for changing infrastructure without rewriting the SwiftUI payment screen.

Lesson 4.4 — Final checkpoint

We've completed dependency injection, dependency inversion, constructor injection, protocol existentials, mock implementations, composition roots, dependency lifetimes, and deterministic testing.

The lesson's architectural code is ready to integrate with the existing NPay project. The full payment-review and navigation flow still needs to be connected to the asynchronous ViewModel contract and verified in Xcode.

Unit 4: 4 of 10 lessons covered conceptually

40%

Next — Lesson 4.5: Repository Pattern. We'll separate NPay's data-access responsibilities from payment behavior, introduce repository protocols and implementations, and investigate how the same ViewModel can work with in-memory, cached, and eventually API-backed data sources.

## Integration through Lesson 4.4 (authored)

The text leaves this step open: "the full payment-review and navigation flow still needs to be connected to the
asynchronous ViewModel contract and verified in Xcode". Here it is connected and verified.
- `PaymentsFeatureRoot` gets its ViewModel from `NPayFactory.makePaymentViewModel(store:)`.
- The review sheet's Confirm now runs `Task { pendingSuccessID = await viewModel.submit()?.transactionID; review = nil }`.
  The sheet's `isProcessing` and the ViewModel's `isSubmitting` both guard against a double confirm.
- To keep Lesson 4.2's balance validation and the "Available" line without giving the ViewModel the store, the factory
  also passes a read-only `availableBalance` closure (`{ store.balancePaise }`). It defaults to `.max`, so the text's
  `PaymentViewModel(service:)` still compiles. This closure is ours.
- `preparePayment()` keeps the 4.2 snapshot for the sheet. `submit()` sends the form's current values; they are the
  same values, because the sheet is modal.
- The 4.2 `confirmPayment(_:)` is replaced by `submit()`. Failures show the ViewModel's inline `errorMessage`.
- `MockPaymentService` lives in the app's Services folder, as section 13 lists. The `#if DEBUG` lines are evidence
  hooks for the test driver, not NPay code.

The full app is `tools/sim4_4/App.swift`, below the "Complete code through Lesson 4.4" marker.

```swift
// Domain/PaymentRequest.swift and Domain/PaymentService.swift (Lesson 4.4, section 3)

struct PaymentRequest {
    let recipient: String
    let amountPaise: Int
}

struct PaymentReceipt {
    let transactionID: UUID
    let recipient: String
    let amountPaise: Int
}

@MainActor
protocol PaymentService {
    func send(_ request: PaymentRequest) async throws -> PaymentReceipt
}

// Services/DemoPaymentService.swift (section 4: uses the shared NPayStore)

enum PaymentServiceError: Error {
    case rejected
}

@MainActor
final class DemoPaymentService: PaymentService {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        guard let id = store.recordDemoPayment(
            recipient: request.recipient,
            amountPaise: request.amountPaise
        ) else {
            throw PaymentServiceError.rejected
        }

        return PaymentReceipt(
            transactionID: id,
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )
    }
}

// Services/MockPaymentService.swift (section 8)

@MainActor
final class MockPaymentService: PaymentService {

    var shouldFail = false
    private(set) var requests: [PaymentRequest] = []

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        requests.append(request)

        if shouldFail {
            throw PaymentServiceError.rejected
        }

        return PaymentReceipt(
            transactionID: UUID(),
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )
    }
}

// App/NPayFactory.swift (section 10, the composition point for the payment feature)

@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        store: NPayStore
    ) -> PaymentViewModel {

        #if DEBUG
        if let service = NPayDebug.paymentService {   // evidence hook: the lab driver swaps in a mock
            return PaymentViewModel(service: service, availableBalance: { store.balancePaise })
        }
        #endif

        let service = DemoPaymentService(store: store)

        // Integration (ours): the form also reads the balance, for Lesson 4.2's validation and display
        return PaymentViewModel(service: service, availableBalance: { store.balancePaise })
    }
}

// Features/Payments/ValidatedPaymentRequest.swift (Lesson 4.2, section 12)

struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}

// Features/Payments/PaymentViewModel.swift (Lesson 4.4: a PaymentService replaces the NPayStore dependency)

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?
    var isSubmitting = false

    private let service: any PaymentService
    private let availableBalance: @MainActor () -> Int   // integration (ours): read-only balance

    init(
        service: any PaymentService,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) {
        self.service = service
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

    // Lesson 4.2, section 12: the review snapshot (no payment yet)
    func preparePayment() -> ValidatedPaymentRequest? {

        guard let amount = parsedAmountPaise,
              validate(availableBalancePaise: availableBalancePaise) else {
            errorMessage = "Please check payment details"
            return nil
        }

        errorMessage = nil

        return ValidatedPaymentRequest(
            recipient: recipient,
            amountPaise: amount
        )
    }

    // Lesson 4.4, section 6: submission through the injected service
    func submit() async -> PaymentReceipt? {
        guard !isSubmitting else {
            return nil
        }

        guard let amount = Money.parsePaise(amountText),
              amount > 0,
              !recipient.trimmingCharacters(
                in: .whitespacesAndNewlines
              ).isEmpty else {
            errorMessage = "Check your payment details."
            return nil
        }

        let request = PaymentRequest(
            recipient: recipient.trimmingCharacters(
                in: .whitespacesAndNewlines
            ),
            amountPaise: amount
        )

        isSubmitting = true
        defer { isSubmitting = false }

        do {
            let receipt = try await service.send(request)

            recipient = ""
            amountText = ""
            errorMessage = nil

            return receipt
        } catch {
            errorMessage = "Payment could not be completed."
            return nil
        }
    }

    // Lesson 3.4's Discard Draft
    func discardDraft() {
        recipient = ""
        amountText = ""
        errorMessage = nil
    }
}

// Features/Payments/PaymentsFeatureRoot.swift
_viewModel = State(
    initialValue: NPayFactory.makePaymentViewModel(store: store)
)

// Screens/PaymentsScreen.swift: the review sheet's Confirm
PaymentReviewSheet(request: request) {
    Task {
        pendingSuccessID = await viewModel.submit()?.transactionID
        self.review = nil
    }
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen4_4.py`, 40 slides) has 7 Parts:
1. The problem (sections 1, 2).
2. The contract and the demo (3, 4).
3. Creation versus dependency (5, 15).
4. The refactored ViewModel (6, 7, 16).
5. Mocks and testing (8, 9, 18).
6. Composition and lifetime (10, 11, 12, 17, 19).
7. Dependency injection in NPay (13, 20, 21 and the integration).

Then recap, review, next, lab and end. Part 2 restarts at Section 14; the knowledge check (section 14) is in the review.

**Evidence**
- **Mac:** the text's code compiled with NPay's real `NPayStore`, `Money` and `PaymentValidator` (Swift 6, Debug, so
  `assert` is active).
  - Section 18: "PaymentViewModel test passed", "Failure-path test passed".
  - Section 9, one `submit()` against each service:
    - Demo → receipt ₹1,500.50, store 2,349,950 paise and 4 transactions.
    - Mock success → receipt; mock failure → "Payment could not be completed.".
    - Demo with ₹30,000 → "Payment could not be completed." (the store refused).
    - Mock with "abc" → "Check your payment details.", nothing sent.
  - Section 16: the ViewModel's stored service is the same object (`===` via Mirror). `MemoryLayout<any
    PaymentService>.size` is 40 bytes and a class reference is 8 (labelled an implementation detail).
  - Section 12: a factory-built ViewModel leaving scope → PaymentViewModel deinit, DemoPaymentService deinit; the store
    survived.
  - Ours: two concurrent submits with a slow mock (300 ms) → 1 receipt, 1 request.
- **Simulator** (`sh tools/sim4_4/run.sh`):
  - Demo → success, ₹23,499.50, "Sent to ravi@npay", form cleared.
  - Succeeding mock → success screen, Home still ₹25,000.00, no new row, `mock.requests` [ravi@npay 150050].
  - Failing mock → inline "Payment could not be completed.", no navigation, draft kept.
  - Stale review (₹20,000 open, ₹10,000 recorded elsewhere) → the same error, balance unchanged.
  - Screenshots: mock success, mock failure.
- **Checklist:** "no concrete service construction in the ViewModel": 0 occurrences of `DemoPaymentService` or
  `NPayStore` in the integrated `PaymentViewModel`.

**Authored (flagged)**
- The integration above; all the runs; the slow-mock double submit.
- Section 5's diagram, drawn from the text's two lists.
- Section 16's trace (only stage 1 of 7 was shared) is taught through the identity and ARC runs instead of a stepper.
- Section 9's interactive experiment, replaced by the measured table.
- Review: the text's 7 questions (options reordered) plus three more:
  - two predict items (mock success balance; "abc" requests);
  - a spaced item from 4.3.
  - 4 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab, end slide.

**Snippets**
- Section 2's "without injection" example uses a no-argument `DemoPaymentService()` that the later code doesn't have
  (an illustration).
- Section 6's `submit()` is condensed on the slide; the full version is above and in the app.
- Every other snippet compiles (full compile, Swift 6).

**Wording**
- "Senior engineer knowledge check / insight" became neutral labels and "Check your understanding".
