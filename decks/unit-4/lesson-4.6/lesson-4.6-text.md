# Unit 4 · Lesson 4.6 — Domain Models, Use Cases & Clean Architecture

NPay iOS Engineering Masterclass · Part 1 + Part 2 · Incremental Swift Labs · Architecture Internals

In Lesson 4.5, we created AccountRepository and implemented it using a Swift actor.

Our NPay architecture now looks like this:

PaymentsScreen → PaymentViewModel → PaymentService → AccountRepository

But there's an important architectural question we haven't answered:

Who owns the actual business rules of sending money?

Should the ViewModel validate payment limits? Should the repository decide whether a payment is allowed? Or should we create a dedicated component that represents the business operation?

Today, we'll introduce domain models, use cases, and the dependency rule.

By the end, NPay will have a dedicated SendPaymentUseCase that coordinates a payment without depending on SwiftUI.

## Part 1 — Domain Modeling & Use Cases

## 1. Our NPay engineering milestone

Architecture evolution

PaymentsScreen

Collect input and display results

PaymentViewModel

Manage screen state

SendPaymentUseCase

Execute application-level payment rules

AccountRepository

Provide account operations

InMemoryAccountRepository

Store and update demo account data

The new component is SendPaymentUseCase.

It represents the application operation: send money to a recipient.

## 2. What is a domain model?

A domain model represents concepts belonging to the business.

In NPay, examples include:

- Money

- Account

- Payment

- Recipient

- Transaction

- Payment status

These concepts exist independently of SwiftUI, Xcode, or a particular database.

Compare UI data and domain data

Our payment form contains:
```swift
var amountText = "1500.50"
```
This is UI editing state.

But our payment domain should use:
```swift
let amountPaise = 150_050
```
This is a validated monetary quantity.

Why separate them?

Because "1500." may be valid intermediate text while the user is typing, but it isn't necessarily a completed payment amount.

The domain model should represent meaningful business values rather than arbitrary input text.

## 3. Build a Money value object

Let's improve our existing money model.

Until now, Money was a formatting utility.

For this lesson, we'll introduce a dedicated value type named PaymentAmount to avoid conflicts with the existing Money enum.
```swift
import Foundation

struct PaymentAmount: Equatable, Sendable {
    let paise: Int

    init(paise: Int) throws {
        guard paise > 0 else {
            throw PaymentDomainError.invalidAmount
        }

        self.paise = paise
    }
}

enum PaymentDomainError: Error {
    case invalidAmount
    case invalidRecipient
    case insufficientBalance
    case limitExceeded
}
```
What changed?

Previously, any integer could represent a payment amount.

Now PaymentAmount guarantees that its stored value is positive when created through its initializer.

This is a domain invariant.

Senior engineer insight

A value object should make invalid states difficult or impossible to represent.

But one invariant doesn't cover every business rule. A positive payment amount can still exceed the user's balance or transaction limit.

## 4. Build a Recipient value object

Now let's create a validated recipient.
```swift
import Foundation

struct PaymentRecipient: Equatable, Sendable {
    let identifier: String

    init(_ identifier: String) throws {
        let trimmed = identifier.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty else {
            throw PaymentDomainError.invalidRecipient
        }

        self.identifier = trimmed
    }
}
```
This establishes a minimal invariant: the recipient identifier cannot be empty.

For a real UPI payment application, recipient validation would involve additional rules and authoritative verification.

Our NPay project remains a local simulation.

## 5. Build a domain payment request

```swift
struct SendPaymentCommand: Sendable {
    let recipient: PaymentRecipient
    let amount: PaymentAmount
}
```
Notice that the command doesn't contain a SwiftUI Binding, TextField, or View.

It represents a meaningful application request.

UI to domain conversion

TextField

"1500.50"

Money.parsePaise

150050

PaymentAmount

Validated positive amount

SendPaymentCommand

Recipient + amount

SendPaymentUseCase

Executes the operation

## 6. What is a use case?

A use case represents an operation the application supports.

For example:

SendPaymentUseCase

FetchBalanceUseCase

FetchTransactionHistoryUseCase

A use case coordinates the rules and dependencies needed to perform that operation.

It is not a screen.

It is not a database table.

It is not necessarily a network request.

Why introduce it?

Because sending money is a business operation that should remain meaningful even if we replace SwiftUI with another presentation technology.

## 7. Build SendPaymentUseCase

We'll use the AccountRepository contract from Lesson 4.5.
```swift
import Foundation

struct SendPaymentUseCase {
    let repository: any AccountRepository

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        let snapshot = try await repository.fetchSnapshot()

        guard command.amount.paise <= snapshot.balancePaise else {
            throw PaymentDomainError.insufficientBalance
        }

        let perPaymentLimitPaise = 100_000_00

        guard command.amount.paise <= perPaymentLimitPaise else {
            throw PaymentDomainError.limitExceeded
        }

        return try await repository.recordPayment(
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise
        )
    }
}
```
What does this do?

The use case:

1. Retrieves the current account snapshot.

2. Checks the available balance.

3. Applies an illustrative per-payment limit of ₹1,00,000.

4. Requests the repository to record the demo payment.

5. Returns the resulting payment record.

The limit is a learning example, not a statement of actual UPI limits.

Important concurrency detail

The balance check inside the use case is useful for expressing the rule, but it isn't sufficient as the final consistency guarantee.

Another operation could change the balance between fetchSnapshot() and recordPayment().

That's why our repository must revalidate the current balance atomically when recording the payment.

## 8. Why not put every rule inside the repository?

Because repositories and use cases have different responsibilities.

The use case represents application policy.

The repository protects data integrity and performs data operations.

Some validation must be enforced at both boundaries for different reasons.

For example:

| Rule | Use case | Repository |
|---|---|---|
| Amount must be positive | Domain value object | Defensive validation |
| Recipient must be nonempty | Domain value object | Defensive validation |
| Per-payment policy limit | Use-case policy | Authoritative enforcement may also be required |
| Sufficient current balance | Preliminary check | Atomic final check |
| Record transaction | Requests operation | Performs operation |

The exact division depends on the domain and backend contract.

For a real payment system, authoritative limits and balance checks belong on the trusted backend.

## 9. Behind the scenes — use-case execution

NPay payment operation

*(Interactive stepper in the original, 7 stages; only stage 1 was shared.)*

1. ViewModel prepares command

Parses user input into domain values.

BackNext step

## Part 2 — Clean Architecture, Dependency Direction & NPay Integration

## 10. What is the Dependency Rule?

Clean Architecture emphasizes that source-code dependencies should point toward the application's core policies.

The domain layer should not depend on SwiftUI, URLSession, or a particular database framework.

NPay dependency direction

Presentation

SwiftUI + PaymentViewModel

Application

SendPaymentUseCase

Domain

PaymentAmount · PaymentRecipient · Repository contract

Infrastructure

InMemoryAccountRepository

Arrows indicate source-code dependencies. Runtime calls can flow outward to infrastructure through domain-owned abstractions.

Important insight

InMemoryAccountRepository implements the repository protocol.

The use case depends on that protocol, not on the concrete implementation.

This is dependency inversion in practice.

## 11. A practical architecture improvement

Our current use case has a concrete SendPaymentUseCase struct.

That's fine.

We don't need a protocol for every use case.

But if we want to mock the use case in ViewModel tests, we could introduce a protocol.

For now, we'll keep the design simple.

NPay rule

Use abstractions where they provide meaningful testability or replaceability.

Avoid creating unnecessary layers just to imitate a diagram.

## 12. Connect the ViewModel to the use case

We'll now replace the direct PaymentService dependency with SendPaymentUseCase for this experiment.
```swift
import SwiftUI

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?
    var isSubmitting = false

    private let sendPayment: SendPaymentUseCase

    init(sendPayment: SendPaymentUseCase) {
        self.sendPayment = sendPayment
    }

    func submit() async -> PaymentRecord? {

        guard !isSubmitting else {
            return nil
        }

        isSubmitting = true
        defer { isSubmitting = false }

        do {
            guard let paise = Money.parsePaise(amountText) else {
                throw PaymentDomainError.invalidAmount
            }

            let command = SendPaymentCommand(
                recipient: try PaymentRecipient(recipient),
                amount: try PaymentAmount(paise: paise)
            )

            let result = try await sendPayment.execute(command)

            recipient = ""
            amountText = ""
            errorMessage = nil

            return result

        } catch PaymentDomainError.insufficientBalance {
            errorMessage = "Insufficient balance"
        } catch PaymentDomainError.limitExceeded {
            errorMessage = "Payment exceeds demo limit"
        } catch {
            errorMessage = "Unable to complete payment"
        }

        return nil
    }
}
```
This replaces the Lesson 4.4 PaymentViewModel for the architecture experiment. Don't keep two classes with the same name in the same target.

What changed?

The ViewModel no longer calls the repository directly.

It delegates the application operation to a use case.

The use case coordinates business rules and data access.

## 13. Build the composition root

Let's assemble our dependencies.
```swift
@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        repository: any AccountRepository
    ) -> PaymentViewModel {

        let useCase = SendPaymentUseCase(
            repository: repository
        )

        return PaymentViewModel(
            sendPayment: useCase
        )
    }
}
```
The root can create one repository instance and pass it to the factory.

The ViewModel doesn't know which repository implementation is being used.

## 14. Test the use case independently

Let's create a simple experiment.
```swift
func runUseCaseLab() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 2_500_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 150_050)
    )

    let result = try await useCase.execute(command)

    print("Payment:", result.id)

    let snapshot = try await repository.fetchSnapshot()

    print("Balance:", snapshot.balancePaise)
}
```
Expected balance:

Initial balance

₹25,000.00

Payment

−₹1,500.50

Final balance

₹23,499.50

## 15. Test a business rule

Let's test the illustrative ₹1,00,000 payment limit.
```swift
func testPaymentLimit() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 20_000_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 15_000_000)
    )

    do {
        _ = try await useCase.execute(command)
        assertionFailure("Expected limitExceeded")
    } catch PaymentDomainError.limitExceeded {
        print("Payment limit enforced")
    }
}
```
Important lesson

This test verifies an application policy without involving SwiftUI.

We don't need a Simulator, payment form, or navigation stack.

That's a major benefit of separating use cases from presentation.

## 16. A deeper issue — payment limits and concurrency

Our use case checks the payment limit before recording the transaction.

But imagine two concurrent requests.

Each passes the use-case checks.

The repository then records them sequentially.

The repository's atomic balance check protects against overdrawing the local demo account.

However, if we introduce a daily cumulative payment limit, the repository or

*(The text breaks here; Section 13 continues below.)*

---

## Part 2 (continued): Business Rule Consistency, Integration & Architecture Mastery

NPay iOS Engineering Masterclass · Continuing from Section 16 · Final Part of Lesson 4.6

We've built domain value objects, SendPaymentCommand, SendPaymentUseCase, and an actor-based AccountRepository.

Now let's finish the lesson by solving one of the most important problems in payment application architecture:

What happens when multiple payment requests execute concurrently, and which layer must enforce business rules?

## 16. Payment limits and concurrency — continued

Our current use case performs these checks:
```swift
let snapshot = try await repository.fetchSnapshot()

guard command.amount.paise <= snapshot.balancePaise else {
    throw PaymentDomainError.insufficientBalance
}
```
But imagine two payments start almost simultaneously.

Both retrieve the same account balance before either payment is recorded.

Interactive experiment

NPay concurrent payment simulator

Starting balance

₹2,000

Payment A — ₹1500

Payment B — ₹1500

Separate checksAtomic operation

Execute simulationIllustrative execution ordering. Real actor scheduling can choose either request first.

What did we learn?

Checking a balance in a use case is useful for early validation, but the final check and state mutation must be coordinated atomically at the authoritative boundary.

Our in-memory actor repository already provides this protection for its non-suspending check-and-update operation.

## 17. What about a daily transaction limit?

Suppose NPay introduces a hypothetical daily outgoing-payment limit of ₹50,000.

A single-payment limit isn't enough.

The application must also consider previous payments.

For example:

| Payment | Amount | Daily outgoing total |
|---|---|---|
| First | ₹20,000 | ₹20,000 |
| Second | ₹15,000 | ₹35,000 |
| Third | ₹20,000 | ₹55,000 |

The third payment should be rejected under this hypothetical rule.

Where should this rule live?

The policy definition belongs in the domain/application layer.

However, enforcement must occur where the authoritative transaction state can be checked and updated consistently.

For our actor-based simulation, that could mean passing the policy into a repository operation that checks cumulative spending and records the new payment without an intervening suspension.

For a production payment system, the trusted backend must enforce the rule.

Architecture principle: Business rules should be clearly expressed in the domain, but concurrency-sensitive invariants must also be enforced at the authoritative mutation boundary.

## 18. Improve our use-case design

Our original SendPaymentUseCase performs an early balance check, then records the payment.

That works for teaching, but it duplicates some validation and can introduce stale-data assumptions.

Let's improve it by separating static policy validation from the repository's authoritative balance check.
```swift
import Foundation

struct PaymentPolicy: Sendable {
    let maximumPerPaymentPaise: Int

    func validate(_ amount: PaymentAmount) throws {
        guard amount.paise <= maximumPerPaymentPaise else {
            throw PaymentDomainError.limitExceeded
        }
    }
}

struct SendPaymentUseCase {
    let repository: any AccountRepository
    let policy: PaymentPolicy

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        try policy.validate(command.amount)

        return try await repository.recordPayment(
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise
        )
    }
}
```
This replaces the earlier SendPaymentUseCase implementation.

What changed?

The use case now performs the payment-policy check, then delegates the atomic account mutation to the repository.

The repository remains responsible for validating the current balance.

Why is this better?

The use case doesn't make a potentially stale balance decision based on a previously fetched snapshot.

The policy is also independently testable.

For our demo, configure it as:
```swift
let policy = PaymentPolicy(
    maximumPerPaymentPaise: 10_000_000
)
```
That's ₹1,00,000 in paise, used solely as an illustrative limit.

## 19. Update the NPay composition root

Now the use case needs both the repository and the payment policy.
```swift
@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        repository: any AccountRepository
    ) -> PaymentViewModel {

        let policy = PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )

        let useCase = SendPaymentUseCase(
            repository: repository,
            policy: policy
        )

        return PaymentViewModel(
            sendPayment: useCase
        )
    }
}
```
Notice that PaymentViewModel doesn't construct the repository or payment policy.

The composition root assembles those dependencies.

This preserves dependency injection.

## 20. Connect the use case to NPay's payment-review flow

Remember Unit 3.4:

Payment Form → Review Sheet → Confirm → Payment Success

We must preserve this behavior.

The important rule is that opening the review sheet does not execute a payment.

Only confirmation does.

PaymentsScreen

User enters recipient and amount

PaymentViewModel

Parses and prepares validated request

PaymentReviewSheet

Displays immutable review snapshot

Confirm action

User authorizes the local demo operation

SendPaymentUseCase

Applies policy and invokes repository

AccountRepository

Atomically validates and records payment

NPayRouter

Navigates to success after dismissal

Important integration correction

Our earlier PaymentViewModel.submit() reads mutable form fields directly. For a review-confirmation flow, we should instead submit the exact immutable request the user reviewed.

For example, introduce:
```swift
func submit(
    _ command: SendPaymentCommand
) async -> PaymentRecord? {

    guard !isSubmitting else {
        return nil
    }

    isSubmitting = true
    defer { isSubmitting = false }

    do {
        let result = try await sendPayment.execute(command)

        recipient = ""
        amountText = ""
        errorMessage = nil

        return result
    } catch {
        errorMessage = "Unable to complete demo payment"
        return nil
    }
}
```
This method belongs inside the existing PaymentViewModel and replaces the previous parameterless submission method for this flow.

The review sheet can receive a validated command snapshot and pass that same command back on confirmation.

This prevents a mismatch between what the user reviewed and what the ViewModel submits.

The repository must still revalidate its authoritative state.

## 21. How should navigation work after asynchronous submission?

We learned in Lesson 3.4 that modal dismissal and navigation should be coordinated.

The flow is:

1. The user confirms the reviewed command.

2. The ViewModel calls await sendPayment.execute(command).

3. On success, the payment record's ID is stored as a pending navigation result.

4. The review sheet is dismissed.

5. The sheet's onDismiss callback invokes router.showPaymentSuccess(id).

On failure, the review sheet should remain open or display an appropriate error. It must not navigate to success.

Senior engineer insight

An asynchronous operation can complete after the user has navigated elsewhere. The feature must deliberately manage cancellation, task lifetime, and presentation state.

We'll model those states in Lesson 4.7.

## 22. Unit tests for the domain policy

We can test PaymentPolicy without SwiftUI or a repository.
```swift
import Foundation

func testPaymentPolicy() throws {
    let policy = PaymentPolicy(
        maximumPerPaymentPaise: 10_000_000
    )

    let valid = try PaymentAmount(
        paise: 150_050
    )

    try policy.validate(valid)

    let excessive = try PaymentAmount(
        paise: 15_000_000
    )

    do {
        try policy.validate(excessive)
        assertionFailure("Expected limitExceeded")
    } catch PaymentDomainError.limitExceeded {
        print("Limit correctly enforced")
    }
}
```
What are we testing?

The domain policy, independently of presentation, navigation, networking, and storage.

That's a central benefit of Clean Architecture.

## 23. Senior engineer knowledge check

Clean Architecture Assessment

*(Interactive quiz in the original.)*

**1. What is a domain value object?**

A type representing a domain concept and its invariants

A SwiftUI screen

A database connection

**2. Should SendPaymentUseCase import SwiftUI?**

Yes

No

**3. Why is an early balance check insufficient for final payment authorization?**

The balance may change before mutation

SwiftUI doesn't support integers

Repositories cannot throw errors

**4. Where should the authoritative balance check occur?**

At the atomic mutation boundary

Inside BalanceCard

Only inside TextField validation

**5. Why submit the immutable reviewed command?**

To ensure the submitted data matches what was reviewed

To improve animation speed

To eliminate all concurrency issues

**6. Does actor isolation automatically enforce payment idempotency?**

Yes

No

**7. What should happen if payment submission fails?**

Show an error and avoid success navigation

Navigate to success anyway

Clear the account balance

**8. Can PaymentPolicy be tested without launching SwiftUI?**

Yes

No

Lesson 4.6 — Completed

We've now finished both parts of Domain Models, Use Cases & Clean Architecture, including:

- Domain value objects and invariants.

- Immutable payment commands.

- Use-case responsibilities.

- Dependency direction and repository abstractions.

- Concurrency-sensitive balance checks.

- Payment-policy enforcement.

- ViewModel integration and asynchronous confirmation.

- Independent domain testing.

Unit 4 progress

6 / 10 lessons

60% of Unit 4 covered conceptually; consolidated Xcode integration remains pending.

Next — Lesson 4.7: UI State Modeling. We'll model NPay's payment lifecycle using idle, validating, submitting, success, and failure states, and investigate how enums, async/await, Observation, and SwiftUI work together to prevent inconsistent UI states.

## Integration through Lesson 4.6 (authored)

Sections 12, 13, 19 and 20 are applied to NPay with the review flow kept (section 20). One addition is needed: NPay's
Home and History still read `NPayStore`, so the use case runs on an **adapter repository over NPayStore**
(`NPayStoreAccountRepository`, ours). The store checks and records in one main-actor call.
- **New types:** the domain types (sections 3–5) and Lesson 4.5's repository contract join the app. `PaymentPolicy` and
  `SendPaymentUseCase` are section 18's version.
- **Factory:** `NPayFactory.makePaymentViewModel(repository:availableBalance:)`. Section 19's factory plus 4.4's
  read-only balance closure (ours), which keeps 4.2's form validation and the "Available" line.
- **ViewModel:**
  - `prepareCommand()` (ours) parses the form into a `SendPaymentCommand`, wrapped in `ValidatedPaymentRequest`
    (now `{ id, command }`).
  - The review sheet shows the command, and Confirm runs `await viewModel.submit(request.command)` (section 20).
  - On failure the sheet closes and the inline error shows, with no navigation (section 21).
- **Leftovers:** Lesson 4.4's `PaymentService`, `DemoPaymentService` and `MockPaymentService` are still in the project,
  unused by the payment ViewModel.

The full app is `tools/sim4_6/App.swift`, below the "Complete code through Lesson 4.6" marker. The `#if DEBUG` lines are
evidence hooks, not NPay code.

```swift
// Domain/PaymentAmount.swift, PaymentRecipient.swift, SendPaymentCommand.swift (Lesson 4.6, sections 3-5)

struct PaymentAmount: Equatable, Sendable {
    let paise: Int

    init(paise: Int) throws {
        guard paise > 0 else {
            throw PaymentDomainError.invalidAmount
        }

        self.paise = paise
    }
}

enum PaymentDomainError: Error {
    case invalidAmount
    case invalidRecipient
    case insufficientBalance
    case limitExceeded
}

struct PaymentRecipient: Equatable, Sendable {
    let identifier: String

    init(_ identifier: String) throws {
        let trimmed = identifier.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty else {
            throw PaymentDomainError.invalidRecipient
        }

        self.identifier = trimmed
    }
}

struct SendPaymentCommand: Sendable {
    let recipient: PaymentRecipient
    let amount: PaymentAmount
}

// Domain/AccountRepository.swift (Lesson 4.5, sections 4-5)

struct PaymentRecord: Identifiable, Sendable {
    let id: UUID
    let recipient: String
    let amountPaise: Int
    let createdAt: Date
}

struct AccountSnapshot: Sendable {
    let balancePaise: Int
    let transactions: [PaymentRecord]
}

enum AccountRepositoryError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
}

protocol AccountRepository: Sendable {
    func fetchSnapshot() async throws -> AccountSnapshot

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord
}

// Data/NPayStoreAccountRepository.swift (integration, ours): the repository contract over NPay's existing store, so
// Home and History keep one source of truth while payments go through the use case
@MainActor
final class NPayStoreAccountRepository: AccountRepository {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func fetchSnapshot() async throws -> AccountSnapshot {
        AccountSnapshot(
            balancePaise: store.balancePaise,
            transactions: store.transactions
                .filter { $0.amountPaise < 0 }
                .map { PaymentRecord(id: $0.id, recipient: $0.title, amountPaise: -$0.amountPaise, createdAt: $0.date) }
        )
    }

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord {
        let trimmed = recipient.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw AccountRepositoryError.invalidRecipient }
        guard amountPaise > 0 else { throw AccountRepositoryError.invalidAmount }

        // The store checks the balance and records the payment in one main-actor call (no suspension)
        guard let id = store.recordDemoPayment(recipient: trimmed, amountPaise: amountPaise) else {
            throw AccountRepositoryError.insufficientBalance
        }
        return PaymentRecord(id: id, recipient: trimmed, amountPaise: amountPaise, createdAt: .now)
    }
}

// Application/PaymentPolicy.swift and SendPaymentUseCase.swift (Lesson 4.6, section 18)

struct PaymentPolicy: Sendable {
    let maximumPerPaymentPaise: Int

    func validate(_ amount: PaymentAmount) throws {
        guard amount.paise <= maximumPerPaymentPaise else {
            throw PaymentDomainError.limitExceeded
        }
    }
}

struct SendPaymentUseCase {
    let repository: any AccountRepository
    let policy: PaymentPolicy

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        try policy.validate(command.amount)

        return try await repository.recordPayment(
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise
        )
    }
}

// App/NPayFactory.swift (Lesson 4.6, section 19; availableBalance is ours, for Lesson 4.2's form validation)

@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        repository: any AccountRepository,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) -> PaymentViewModel {

        let policy = PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )

        let useCase = SendPaymentUseCase(
            repository: repository,
            policy: policy
        )

        return PaymentViewModel(
            sendPayment: useCase,
            availableBalance: availableBalance
        )
    }
}

// Features/Payments/ValidatedPaymentRequest.swift (now wraps the immutable command the user reviews)

struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let command: SendPaymentCommand
}

// Features/Payments/PaymentViewModel.swift (Lesson 4.6: a SendPaymentUseCase replaces the PaymentService)

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?
    var isSubmitting = false

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

    // Integration (ours): parse the form into domain values, the snapshot the sheet shows and Confirm submits
    func prepareCommand() -> ValidatedPaymentRequest? {
        do {
            guard let paise = parsedAmountPaise,
                  validate(availableBalancePaise: availableBalancePaise) else {
                throw PaymentDomainError.invalidAmount
            }

            let command = SendPaymentCommand(
                recipient: try PaymentRecipient(recipient),
                amount: try PaymentAmount(paise: paise)
            )

            errorMessage = nil
            return ValidatedPaymentRequest(command: command)
        } catch {
            errorMessage = "Please check payment details"
            return nil
        }
    }

    // Lesson 4.6, section 20: submit exactly the command the user reviewed
    func submit(
        _ command: SendPaymentCommand
    ) async -> PaymentRecord? {

        guard !isSubmitting else {
            return nil
        }

        isSubmitting = true
        defer { isSubmitting = false }

        do {
            let result = try await sendPayment.execute(command)

            recipient = ""
            amountText = ""
            errorMessage = nil

            return result
        } catch {
            errorMessage = "Unable to complete demo payment"
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
```

## Deck changes

The text came in three pieces: Part 1 (sections 1–9), Part 2 (10–16, breaking inside 16), and a continuation (16–23).
Two chat lines between the pieces ("done?" and a summary of what remained) are not lesson content and are removed above.

The deck (`index.html`, built by `tools/gen4_6.py`, 39 slides) has 7 Parts:
1. Domain models (sections 1, 2).
2. Value objects (3, 4, 5).
3. Use cases (6, 7, 8).
4. Testing the domain (9, 14, 15, 22).
5. The dependency rule (10, 11).
6. Rules under concurrency (16, 17, 18).
7. Into NPay (12, 13, 19, 20, 21).

Then recap, review, next, lab and end.

**Evidence: Mac** (the text's code, Swift 6, Debug)
- Value objects: 150050 accepted; 0 and −100 → invalidAmount; "  ravi@npay " → "ravi@npay"; blank → invalidRecipient.
- Section 14 → Balance 2349950. Section 15 → "Payment limit enforced". Section 22 → "Limit correctly enforced".
- Section 16, two ₹1,500 at once from ₹2,000 through version 1 and section 12's ViewModel:
  - As run, the early checks didn't overlap: B got "Insufficient balance" from the early check.
  - With 20 ms of latency in `fetchSnapshot` (ours), both early checks passed. The repository's atomic check caught the
    second (balance ₹500), but its `AccountRepositoryError` isn't mapped by the use case, so the user saw "Unable to
    complete payment".
- Section 17 (ours): three ₹20,000 payments at once, daily limit ₹50,000.
  - Checked from a snapshot → 3 accepted (₹60,000).
  - Checked inside one actor call → 2 accepted (₹40,000).
- Section 20: reviewed ₹1,500.50, then the field changed to 2000.
  - Section 12's `submit()` paid 200000.
  - `submit(reviewedCommand)` paid 150050.
  - Section 20's version shows "Unable to complete demo payment" for both insufficient balance and over-limit.

**Evidence: simulator** (`sh tools/sim4_6/run.sh`)
- A ₹1,500.50 payment → Payment Recorded, ₹23,499.50, History "Sent to ravi@npay", form cleared.
- A stale review (₹20,000, ₹10,000 removed during review) → "Unable to complete demo payment", no navigation, balance
  unchanged, draft kept.
- Screenshots: the review sheet showing the command, the stale failure.

**Renamed in the Mac lab** (both versions coexist): section 7's use case is `SnapshotSendPaymentUseCase`, and section
12's ViewModel is `Section12PaymentViewModel`.

**Authored (flagged)**
- The integration above and every run, including the latency wrapper and the daily-limit repository.
- Diagrams for sections 1, 5, 10 and 21.
- Section 9's stepper (only stage 1 was shared) and section 16's interactive simulator, replaced by measured runs.
- Review: the text's 8 questions (options reordered) plus three more:
  - two predict items (snapshot-based daily limit; field changed after review);
  - a spaced item from 4.5.
  - 3 of 11 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab, end slide.

**Snippets:** every slide snippet compiles (Swift 6, full compile).

**Wording**
- "Senior engineer insight / knowledge check" became neutral labels and "Check your understanding".
