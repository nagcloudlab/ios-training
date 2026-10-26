# Unit 4 · Lesson 4.1 — Why iOS Applications Need Architecture

NPay iOS Engineering Masterclass · MVVM · Separation of Concerns · SwiftUI Internals

We've completed the conceptual journey through Unit 3. NPay now has a defined architecture for navigation, payment forms, review sheets, transaction history, and shared state.

Before adding networking and databases, we need to improve how NPay's code is organized.

Our engineering question: Why does an application that works perfectly with 500 lines of code become difficult to maintain at 50,000 lines?

Today, we'll learn MVC, MVVM, and Clean Architecture through the problems in our existing NPay design.

## 1. The problem with our current NPay architecture

Our current NPayStore handles several responsibilities:
```swift
@MainActor
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []
    var paymentDraft = PaymentDraft()

    func recordDemoPayment(
        recipient: String,
        amountPaise: Int
    ) -> UUID? {
        // Validate recipient
        // Validate amount
        // Check balance
        // Deduct money
        // Create transaction
        // Update history
    }
}
```

This works for a learning prototype.

But imagine NPay now needs a backend API, biometric authentication, transaction persistence, payment limits, and retry handling.

If we keep adding everything to NPayStore, it becomes a large object with too many responsibilities.
Current architecture — growing responsibilities
NPayStore

Application state + payment logic

Balance

Transactions

Payment validation

Payment execution

Draft state

Future networking

What could go wrong?
If we change payment validation, we might accidentally affect unrelated state.

If we want to test payment logic, we may need to construct the entire store.

If we replace local demo payments with an API, the UI could become tightly coupled to networking.

Architecture helps us manage these dependencies.

## 2. What is application architecture?

Application architecture defines how responsibilities are divided and how components communicate.

For NPay, we want to separate:
- Presentation — what the user sees.
- Presentation state — what the screen needs to display.
- Business rules — what makes a payment valid.
- Data access — where account and transaction information comes from.
- Navigation — where the user goes next.
These responsibilities should have clear boundaries.

## 3. MVC versus MVVM versus Clean Architecture

MVC
View

Controller

Model

MVVM
View

ViewModel

Model

Clean
UI

Use Cases

Domain

These are simplified teaching diagrams. Real architectures include additional relationships and dependencies.
MVC
Model–View–Controller is historically common in UIKit applications.

The controller coordinates user interaction and updates between views and models.
MVVM
Model–View–ViewModel separates screen presentation from the state and behavior needed by that screen.

This fits naturally with SwiftUI's state-driven approach.
Clean Architecture
Clean Architecture emphasizes dependency direction and separation of business rules from external technologies.

It can complement MVVM rather than replace it.

For NPay, we'll use MVVM for presentation, with domain use cases and repository abstractions introduced incrementally.

## 4. Our target NPay architecture

NPay — Architecture direction
SwiftUI View

PaymentsScreen — renders the form

ViewModel

PaymentViewModel — manages form state and submission

Use Case

SendPaymentUseCase — applies payment rules

Repository Protocol

PaymentRepository — abstracts payment operations

Implementation

DemoPaymentRepository now; API implementation later

This is the direction we'll build toward across Unit 4.

## 5. First refactoring experiment — move validation out of the View

Let's start small.

Our current payment form validates the amount inside the SwiftUI view.

We'll extract a pure Swift validation function.

```swift
import Foundation

enum PaymentValidationError: Error {
    case emptyRecipient
    case invalidAmount
    case insufficientBalance
}

struct PaymentValidator {

    func validate(
        recipient: String,
        amountPaise: Int,
        balancePaise: Int
    ) throws {

        guard !recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        ).isEmpty else {
            throw PaymentValidationError.emptyRecipient
        }

        guard amountPaise > 0 else {
            throw PaymentValidationError.invalidAmount
        }

        guard amountPaise <= balancePaise else {
            throw PaymentValidationError.insufficientBalance
        }
    }
}
```

What changed?
The validation rules no longer depend on SwiftUI.

We can call them from a ViewModel, use case, or unit test.

This is our first step toward testable architecture.

## 6. Test the validator without launching NPay

```swift
let validator = PaymentValidator()

do {
    try validator.validate(
        recipient: "ravi@npay",
        amountPaise: 150_000,
        balancePaise: 2_500_000
    )

    print("Valid payment")
} catch {
    print("Validation failed:", error)
}
```

Why is this important?
We can test business rules without rendering a screen or starting a Simulator.

That's one of the major benefits of separating domain logic from presentation.

## 7. Behind the scenes — how MVVM changes state flow

In Unit 3, our view could call the shared store directly.

With MVVM, the view delegates screen behavior to a ViewModel.
Payment submission flow
User taps Confirm

SwiftUI Button action

PaymentViewModel

Coordinates submission and exposes UI state

SendPaymentUseCase

Executes payment application rules

PaymentRepository

Performs the payment operation

ViewModel receives result

Updates success or error state

SwiftUI updates

Displays the appropriate result

The ViewModel doesn't need to know about the physical layout of the payment screen.

The SwiftUI view doesn't need to know whether the repository uses in-memory data or an API.

## 8. Why protocols matter

Suppose NPay initially uses an in-memory payment repository.

Later, we replace it with a network-backed implementation.

We don't want to rewrite every ViewModel.

Define an abstraction:

```swift
protocol PaymentRepository {
    func sendPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> UUID
}
```

Now different implementations can conform to the same contract.

For example:
```swift
struct DemoPaymentRepository: PaymentRepository {
    func sendPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> UUID {
        UUID()
    }
}
```

This particular implementation is only a contract demonstration: it returns an ID but doesn't update the NPay balance or history. We'll connect a real in-memory demo repository to shared account state in a later lesson.
Connect to Unit 1
We're using protocol-oriented programming, asynchronous functions, throwing functions, and dependency abstraction.

These Swift fundamentals are central to scalable iOS architecture.

## 9. Unit 4 learning sequence

| Lesson | Topic | NPay implementation |
|---|---|---|
| 4.1 | Architecture fundamentals | Extract payment validation |
| 4.2 | MVVM internals | PaymentViewModel |
| 4.3 | Observation framework | Observable ViewModels |
| 4.4 | Dependency injection | Inject repositories and services |
| 4.5 | Repository pattern | Demo payment repository |
| 4.6 | Domain models and use cases | SendPaymentUseCase |
| 4.7 | UI state modeling | Loading, success, error |
| 4.8 | Modular project structure | Feature organization |
| 4.9 | Architecture testing | ViewModel and use-case tests |
| 4.10 | Integration lab | Complete MVVM NPay |

## 10. Xcode lab — first architecture refactoring

For this lesson, don't rewrite the entire application.

Instead, create a new file:

PaymentValidator.swift

Move the validation logic into it.

Then call the validator from your existing payment submission code.

Verify that valid payments still succeed and invalid payments are rejected.

This is an important practice: refactor the architecture while preserving observable behavior.

## 11. Senior engineer knowledge check

**1. What is the main responsibility of a ViewModel?**

Manage screen state and presentation behavior

Draw pixels manually

Store Xcode build settings

**2. Can MVVM and Clean Architecture be used together?**

Yes

No

**3. Why extract PaymentValidator from SwiftUI?**

To make rules independently testable

To create a new process

To improve SF Symbols

**4. What does a repository protocol provide?**

An abstraction for data operations

A tab bar

A new application window

**5. Should a ViewModel directly control pixel rendering?**

Yes

No

Lesson 4.1 checkpoint
We've introduced MVC, MVVM, Clean Architecture, domain validation, repository protocols, and separation of concerns.

Our first architectural improvement is extracting payment validation into a testable Swift component.

Next — Lesson 4.2: MVVM Internals & PaymentViewModel. We'll build NPay's first observable ViewModel and investigate how SwiftUI observes it, how state flows through the architecture, and how a ViewModel differs from the shared application store.

## Integration through Lesson 4.1 (authored)

Section 10's lab, applied to NPay: `PaymentValidator` (section 5, unchanged) is a new file, `Domain/PaymentValidator.swift`.
Both places that repeated the rules now call it. The full app is `tools/sim4_1/App.swift`, below the "Complete code
through Lesson 4.1" marker.

```swift
// Screens/PaymentsScreen.swift
    // Lesson 4.1: the screen asks PaymentValidator instead of repeating the rules
    private var isValid: Bool {
        guard let amount = parsedAmount else {
            return false
        }

// Store/NPayStore.swift, inside recordDemoPayment(recipient:amountPaise:)
        // Lesson 4.1: the rules live in PaymentValidator
        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amountPaise,
                balancePaise: balancePaise
            )
        } catch {
            return nil
        }

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )
```

## Deck changes

The deck (`index.html`, built by `tools/gen4_1.py`, 36 slides) has 7 Parts:
1. The problem (section 1).
2. What architecture is (2, 3).
3. Where we're heading (4, 7).
4. First refactoring (5, 6).
5. Protocols (8).
6. Refactor safely (10).
7. Unit 4 roadmap (9).

Then recap, review, next, lab and end.

**Evidence**
- Section 6 (Mac, swiftc): "Valid payment". More cases, run the same way:
  - blank recipient → emptyRecipient;
  - 0 and −100 → invalidAmount;
  - 3,000,000 of 2,500,000 → insufficientBalance;
  - the whole balance → valid.
- Swift Testing: the validator in a small Swift package (`NPayPayments`, not in the repo) with five tests; `swift test`
  passed all five.
- Section 8 (Mac): `DemoPaymentRepository` called through the protocol returned a UUID; the balance was unchanged.
- Section 1: sizes counted in the 3.12 code:
  - NPayStore: 63 lines.
  - PaymentsScreen: 160 lines, 6 state properties, 14 uses of the store.
  - NPayRootView: 92 lines.
- Section 10 (iPhone 17 simulator; `sh tools/sim4_1/run.sh`): one behaviour script, run on the 3.12 code and on the
  refactored code, gave **identical** results:
  - empty, blank, zero and ₹30,000 → Review disabled with the message;
  - ₹25,000 and ₹1,500.50 → enabled;
  - after paying ₹1,500.50: 2,349,950 paise, 4 transactions, Home ₹23,499.50;
  - the store refuses "" ₹1, ₹30,000 and ₹0.
- The run surfaced that the amount message also appears for an empty recipient (unchanged behaviour; noted on a slide).

**Authored (flagged)**
- The integration above; the before/after script; the extra validator cases; the Swift Testing package; the size table.
- Section 1's diagram responsibilities, from the text's list; the "In NPay today" card on Section 2's slide.
- Section 3's comparison cards, condensed from the text's paragraphs.
- Section 7's flow is labelled conceptual (no use case or repository exists in NPay yet).
- Review: the text's 5 questions (options reordered so answers vary) plus four more:
  - two predict items (whole-balance boundary, blank recipient);
  - the demo repository's effect;
  - a spaced item from 3.12.
- Outcomes, "Where we are" (Unit 4 strip named from section 9), recap, "Where this goes next", lab, end slide.

**Snippets**
- Section 1's NPayStore is the text's outline (its method body is comments only), shown as an outline; it doesn't
  compile as written.
- Every other slide snippet typechecks.

**Wording**
- "Senior engineer knowledge check" became "Check your understanding".
