# Unit 4 · Lesson 4.5 — Repository Pattern & Data Access Architecture

NPay iOS Engineering Masterclass · Part 1 + Part 2 · Complete Conceptual Lesson & Incremental Swift Labs

In Lesson 4.4, we introduced dependency injection. Our PaymentViewModel now depends on a PaymentService protocol instead of constructing DemoPaymentService itself.

Today, we'll take NPay one step closer to production architecture.

Our engineering question: How can NPay switch between in-memory data, local storage, and a backend API without rewriting its business logic or SwiftUI screens?

We'll learn the Repository Pattern from first principles, build a working in-memory repository, connect it to our ViewModel, and investigate the runtime behavior.

## Part 1 — Understanding and Building Repositories

## 1. The problem with our current NPay design

Our architecture currently looks like this:

PaymentsScreen

Displays payment UI

PaymentViewModel

Coordinates payment submission

DemoPaymentService

Handles simulated payment

NPayStore

Holds balance and transactions

This works for our local simulation.

But imagine NPay now needs to fetch transactions from a REST API, cache recent transactions in SwiftData, and display cached records when offline.

Should PaymentViewModel know whether the data came from SwiftData or a server?

No.

Should PaymentService contain SQL queries or URLSession request-building code?

Ideally, no.

We need a boundary that abstracts data access.

That's where a repository comes in.

## 2. What exactly is a repository?

A repository provides an application-facing interface for accessing and modifying domain data.

It hides how the underlying data is stored or retrieved.

For example:
```swift
let balance = try await repository.fetchBalance()
```

The caller doesn't need to know whether the repository uses an in-memory dictionary, a local database, or a remote API.

Repository versus service

| Repository | Service / Use case |
|---|---|
| Retrieves and stores domain data | Coordinates application behavior |
| Abstracts data sources | Enforces business workflows |
| fetchBalance() | sendPayment() |
| fetchTransactions() | Validate and execute transfer |
| saveTransaction() | Decide when to save and what to return |

This distinction is architectural, not enforced by Swift. In some applications, repository operations themselves represent meaningful atomic domain operations.

## 3. Our target NPay architecture

SwiftUI PaymentsScreen

User interaction and presentation

PaymentViewModel

Screen state and actions

PaymentService

Payment workflow

AccountRepository

Account data contract

Repository Implementation

In-memory today, persistent or remote later

We'll start with one repository that owns the demo account balance and transaction history.

This will replace the storage responsibility currently held by NPayStore, but we'll do so incrementally rather than deleting the existing application code immediately.

## 4. First concept — define domain models

Let's create a small, self-contained repository lab.

For this lesson, we'll use a transaction model called PaymentRecord to avoid conflicting with the existing Transaction model from Unit 3.

Create PaymentRecord.swift.
```swift
import Foundation

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
```

Why Sendable?

Sendable expresses that values can safely cross concurrency isolation boundaries under Swift's concurrency model.

Our structs contain value-type properties that are suitable for this purpose.

We'll investigate actors and Sendable in greater depth in Unit 8.

## 5. Define the repository contract

Create AccountRepository.swift.
```swift
import Foundation

enum AccountRepositoryError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
}
```

```swift
protocol AccountRepository: Sendable {
    func fetchSnapshot() async throws -> AccountSnapshot

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord
}
```

Why two methods?

fetchSnapshot() returns the current account state.

recordPayment() records a local demo transaction and updates the balance.

Notice that we haven't exposed saveTransaction() and updateBalance() as two independent calls.

That's intentional.

A payment and its corresponding balance update must remain consistent.

For this lab, the repository will provide one atomic operation within its in-memory state.

## 6. Build an in-memory repository

Create InMemoryAccountRepository.swift.
```swift
import Foundation

actor InMemoryAccountRepository: AccountRepository {

    private var balancePaise: Int
    private var transactions: [PaymentRecord] = []

    init(initialBalancePaise: Int = 2_500_000) {
        self.balancePaise = initialBalancePaise
    }

    func fetchSnapshot() async throws -> AccountSnapshot {
        AccountSnapshot(
            balancePaise: balancePaise,
            transactions: transactions
        )
    }

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord {

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty else {
            throw AccountRepositoryError.invalidRecipient
        }

        guard amountPaise > 0 else {
            throw AccountRepositoryError.invalidAmount
        }

        guard amountPaise <= balancePaise else {
            throw AccountRepositoryError.insufficientBalance
        }

        let payment = PaymentRecord(
            id: UUID(),
            recipient: trimmed,
            amountPaise: amountPaise,
            createdAt: .now
        )

        balancePaise -= amountPaise
        transactions.insert(payment, at: 0)

        return payment
    }
}
```

What did we introduce?

This is our first repository implemented as a Swift actor.

The actor protects its mutable state from unsynchronized concurrent access.

Its methods can be called asynchronously from outside the actor.

Why is an actor useful here?

Imagine two payment requests arriving almost simultaneously.

Both need to inspect and modify the same balance.

Actor isolation allows the synchronous check-and-update portion of recordPayment to execute without another actor-isolated operation interleaving within it.

There is no await inside the critical check-and-update sequence, which matters for this guarantee.

## 7. Behind the scenes — actor isolation

Two concurrent payment requests

Unsafe conceptual flow

Actor-isolated flow

Starting balance: ₹2,000

Request A executes: ₹2,000 − ₹1,500 = ₹500

Request B checks ₹500 and is rejected

The actor serializes access to its isolated state for this non-suspending operation.

Conceptual ordering; actor scheduling doesn't guarantee that Request A always runs first.

Senior engineer insight

Actors prevent data races on their isolated state, but they don't automatically make a multi-step workflow atomic if it suspends between reading and writing.

We'll study actor reentrancy in Unit 8.

## 8. Test the repository without SwiftUI

Create an experiment function:
```swift
func runRepositoryLab() async throws {

    let repository = InMemoryAccountRepository()

    let before = try await repository.fetchSnapshot()

    print("Before:", before.balancePaise)

    let payment = try await repository.recordPayment(
        recipient: "ravi@npay",
        amountPaise: 150_050
    )

    print("Payment ID:", payment.id)

    let after = try await repository.fetchSnapshot()

    print("After:", after.balancePaise)
    print("Transactions:", after.transactions.count)
}
```

Expected output conceptually:

Before: 2500000

Payment ID: <generated UUID>

After: 2349950

Transactions: 1

We now have a functioning domain-data repository independent of SwiftUI.

## Part 2 — Repository Integration, Data Sources & Architecture Internals

## 9. Connect the repository to a payment service

In Lesson 4.4, we introduced PaymentService.

Now we'll create an implementation that uses the repository instead of accessing NPayStore directly.
```swift
import Foundation

@MainActor
final class RepositoryPaymentService: PaymentService {

    private let repository: any AccountRepository

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        let payment = try await repository.recordPayment(
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )

        return PaymentReceipt(
            transactionID: payment.id,
            recipient: payment.recipient,
            amountPaise: payment.amountPaise
        )
    }
}
```

What changed?

Previously:

DemoPaymentService → NPayStore

Now:

RepositoryPaymentService → AccountRepository

The service depends on an abstraction rather than a concrete storage implementation.

## 10. Complete NPay payment call chain

Payment submission sequence

PaymentsScreen

User confirms payment

PaymentViewModel

Calls service.send(request)

RepositoryPaymentService

Coordinates repository operation

AccountRepository

Abstract data-access contract

InMemoryAccountRepository

Validates and atomically updates local demo state

PaymentReceipt

Returned to ViewModel

NPayRouter

Navigates to success screen

The router is invoked after a successful result, not by the repository itself.

## 11. But how will the Dashboard see the new balance?

This is an important architecture question.

Our repository owns the balance.

Our SwiftUI dashboard needs to display it.

We should not create a second independent balance that becomes a competing source of truth.

Instead, the dashboard can load an account snapshot through the repository.

For example:
```swift
import SwiftUI

@MainActor
@Observable
final class DashboardViewModel {

    private let repository: any AccountRepository

    var balancePaise = 0
    var transactions: [PaymentRecord] = []

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func refresh() async throws {
        let snapshot = try await repository.fetchSnapshot()

        balancePaise = snapshot.balancePaise
        transactions = snapshot.transactions
    }
}
```

What changed?

The dashboard ViewModel owns presentation state derived from repository data.

The repository remains authoritative for the underlying demo account.

Important nuance

A snapshot doesn't update automatically when the repository changes.

We need a deliberate refresh mechanism, observable data stream, or shared application-level state coordinator.

For this lesson, we'll use explicit refresh calls.

In later units, we'll introduce more sophisticated synchronization patterns.

## 12. Repository versus data source

Now let's go deeper.

A repository is an application-facing abstraction.

A data source is a concrete mechanism for retrieving or storing information.

For example:

AccountRepository

Application-facing contract

DefaultAccountRepository

Coordinates data access and caching policy

LocalDataSource

SwiftData / cache

RemoteDataSource

REST API

This is our future architecture.

We won't implement SwiftData or URLSession today because those belong to Units 5 and 6.

But the repository abstraction prepares us for them.

## 13. Cache-first versus network-first repositories

Suppose NPay needs to display transaction history.

There are different strategies.

Cache-first

Network-first

Cache-first

1. Read local cached transactions.

2. Display cached history quickly.

3. Refresh from the server when appropriate.

4.

*(The text breaks here; Section 13 continues below.)*

---

## Part 2 (continued): Repository Internals, Caching & Integration

NPay iOS Engineering Masterclass · Continuing from Section 13

We've built AccountRepository, implemented it using a Swift actor, and connected it to RepositoryPaymentService and DashboardViewModel.

Now we'll complete the lesson by investigating caching strategies, consistency, dependency injection, error handling, and how repositories fit into the final NPay architecture.

## 13. Cache-first versus network-first — continued

Imagine NPay has 10,000 transactions.

When the user opens History, should we always wait for the backend?

Not necessarily. We might show cached data while fetching updated records.

Cache-first

Network-first

Cache-first

Local cache

Read stored transaction history

SwiftUI

Display cached records

Remote API

Fetch authoritative updates

Repository

Reconcile and update cache

SwiftUI

Display refreshed history

Cache-first can improve perceived responsiveness, but cached financial data must be clearly distinguished from authoritative current data.

Which strategy should NPay use?

It depends on the operation.

| Data or operation | Suitable approach |
|---|---|
| Transaction history | Cached display with background refresh, when appropriate |
| Profile preferences | Local persistence with synchronization as needed |
| Available balance | Authoritative server value, with clearly identified cached values if shown |
| Payment execution | Server-authoritative operation, not an offline cache mutation |
| Payment status | Reconcile against authoritative transaction status |

Critical principle: A real payment application must not treat a locally cached balance as authorization to transfer money.

Our in-memory repository is only a simulation.

## 14. Repository consistency — a subtle engineering problem

Let's examine an unsafe design.
```swift
let balance = try await repository.fetchBalance()

guard balance >= amount else {
    throw PaymentError.insufficientBalance
}

try await repository.saveTransaction(payment)
try await repository.updateBalance(balance - amount)
```

This has two problems.

First, the balance can change between reading it and updating it.

Second, saving the transaction might succeed while updating the balance fails.

We could end up with inconsistent records.

Better approach for our local NPay lab

Our repository exposes:
```swift
func recordPayment(
    recipient: String,
    amountPaise: Int
) async throws -> PaymentRecord
```

The actor implementation performs validation and state mutation together, without suspension points inside the critical section.

Atomic local demo operation

Check recipient and amount

Reject invalid requests

Check current balance

Read actor-isolated balance

Create transaction

Generate payment record

Deduct balance

Update the same isolated state

Insert transaction

Update local history

Return receipt

Report the completed demo operation

Does this make it production-ready?

No.

Actor isolation protects the in-memory state of that actor instance. It doesn't provide durable database transactions, cross-device consistency, or server-enforced payment authorization.

Those guarantees must come from the appropriate backend and persistence architecture.

## 15. Repository errors — don't hide failure details

Our repository defines:
```swift
enum AccountRepositoryError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
}
```

This is better than returning nil for every failure.

Why?

Because the caller can distinguish different causes.

Let's improve our payment service error handling.
```swift
import Foundation

enum PaymentError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
    case unknown
}

@MainActor
final class RepositoryPaymentService: PaymentService {
    private let repository: any AccountRepository

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {
        do {
            let payment = try await repository.recordPayment(
                recipient: request.recipient,
                amountPaise: request.amountPaise
            )

            return PaymentReceipt(
                transactionID: payment.id,
                recipient: payment.recipient,
                amountPaise: payment.amountPaise
            )
        } catch AccountRepositoryError.invalidRecipient {
            throw PaymentError.invalidRecipient
        } catch AccountRepositoryError.invalidAmount {
            throw PaymentError.invalidAmount
        } catch AccountRepositoryError.insufficientBalance {
            throw PaymentError.insufficientBalance
        } catch {
            throw PaymentError.unknown
        }
    }
}
```

This version replaces the earlier RepositoryPaymentService; don't keep both declarations in the same target.

Why map errors?

Because the payment feature shouldn't necessarily expose internal storage or networking errors directly to the UI.

The service translates repository failures into payment-domain failures.

The ViewModel can then convert those failures into appropriate user-facing messages.

## 16. Behind the scenes — error propagation

NPay insufficient-balance flow

Repository

Throws AccountRepositoryError.insufficientBalance

PaymentService

Maps it to PaymentError.insufficientBalance

PaymentViewModel

Updates its presentation error state

PaymentsScreen

Displays an accessible error message

Senior engineer insight

Errors should become more meaningful as they move toward the user interface.

But avoid throwing away information needed for debugging. Infrastructure diagnostics can be logged separately without exposing sensitive implementation details to users.

## 17. Dependency injection — one repository, multiple ViewModels

Now let's assemble the application dependencies.

Our Dashboard and Payments features must use the same repository instance.
```swift
import Foundation

@MainActor
final class NPayDependencies {

    let repository: any AccountRepository
    let paymentService: any PaymentService

    init() {
        let repository = InMemoryAccountRepository()

        self.repository = repository
        self.paymentService = RepositoryPaymentService(
            repository: repository
        )
    }

    func makeDashboardViewModel() -> DashboardViewModel {
        DashboardViewModel(repository: repository)
    }

    func makePaymentViewModel() -> PaymentViewModel {
        PaymentViewModel(service: paymentService)
    }
}
```

What changed?

The dependency container creates one repository.

Both ViewModels use dependencies connected to that same repository.

NPayDependencies

Creates and owns one repository

DashboardViewModel

Reads snapshots

PaymentViewModel

Submits through service

InMemoryAccountRepository

One authoritative local demo state

Important limitation

Using one repository prevents independent data sources, but it doesn't automatically refresh every ViewModel's cached presentation snapshot.

The dashboard must still refresh after a payment, or subscribe to an appropriate state-update mechanism.

## 18. Incremental integration lab — refresh the dashboard

For now, we'll use explicit refresh.

After a payment succeeds:
```swift
let receipt = await paymentViewModel.submit()

if receipt != nil {
    try? await dashboardViewModel.refresh()
}
```

This demonstrates the coordination concept.

However, silently ignoring refresh errors with try? isn't ideal for production.

A more robust application would preserve the successful payment result and independently handle a failed dashboard refresh.

Why separate these outcomes?

Because a payment might succeed even if a subsequent balance-refresh request fails.

We must never interpret a failed UI refresh as proof that the payment failed.

That distinction becomes critical when we introduce networking.

## 19. Testing the repository

Let's create a deterministic test.
```swift
import Foundation

func testRepositoryPayment() async throws {
    let repository = InMemoryAccountRepository(
        initialBalancePaise: 200_000
    )

    let payment = try await repository.recordPayment(
        recipient: "ravi@npay",
        amountPaise: 50_000
    )

    let snapshot = try await repository.fetchSnapshot()

    assert(payment.amountPaise == 50_000)
    assert(snapshot.balancePaise == 150_000)
    assert(snapshot.transactions.count == 1)

    print("Repository test passed")
}
```

Test insufficient balance
```swift
func testInsufficientBalance() async throws {
    let repository = InMemoryAccountRepository(
        initialBalancePaise: 10_000
    )

    do {
        _ = try await repository.recordPayment(
            recipient: "ravi@npay",
            amountPaise: 50_000
        )

        assertionFailure("Expected insufficient balance")
    } catch AccountRepositoryError.insufficientBalance {
        print("Correctly rejected")
    }

    let snapshot = try await repository.fetchSnapshot()

    assert(snapshot.balancePaise == 10_000)
    assert(snapshot.transactions.isEmpty)
}
```

The repository should reject the payment without modifying the account state.

We'll convert these examples into proper automated tests in Lesson 4.9.

## 20. The next challenge — duplicate payment requests

Our repository is actor-isolated.

But suppose the same logical payment request is submitted twice, sequentially.

The actor can safely execute both requests.

That doesn't mean the user intended two payments.

Important distinction

Concurrency safety is not the same as idempotency.

Actor isolation prevents unsafe concurrent access to its state.

Idempotency prevents the same logical request from being applied more than once.

For a production payment system, the backend must enforce idempotency using an appropriate request identifier and authoritative transaction records.

We'll revisit this when implementing payment use cases and networking.

## 21. Senior engineer knowledge check

Repository Architecture Assessment

*(Interactive quiz in the original.)*

**1. What does a repository primarily abstract?**

Data access and persistence detailsSwiftUI colorsNavigation animations

**2. Does LazyVStack automatically provide database pagination?**

YesNo

**3. Why expose recordPayment as one operation?**

To keep the local balance and transaction update consistentTo create more ViewModelsTo avoid using protocols

**4. Does actor isolation automatically provide durable database transactions?**

YesNo

**5. Should DashboardViewModel and PaymentViewModel use independent account repositories?**

YesNo

**6. Does a successful payment guarantee a subsequent dashboard refresh will succeed?**

YesNo

**7. Does actor isolation automatically prevent duplicate logical payment requests?**

YesNo

Lesson 4.5 — Final checkpoint

We've completed both parts of the Repository Pattern lesson, including repository contracts, actor-isolated in-memory storage, data-source abstraction, caching strategies, consistency, typed errors, dependency injection, and repository testing.

## Integration through Lesson 4.5

No change to NPay's code. The text builds the repository "incrementally rather than deleting the existing application
code", so NPay still runs on NPayStore and 4.4's `DemoPaymentService`. The repository code runs:
- on the Mac, compiled together with NPay's `Money` and 4.4's contract and ViewModel;
- in a small simulator lab next to NPay (`tools/sim4_5/App.swift`).

## Deck changes

The deck (`index.html`, built by `tools/gen4_5.py`, 39 slides) has 7 Parts:
1. The problem (sections 1, 2).
2. The contract (3, 4, 5).
3. An actor-backed repository (6, 7, 8, 19).
4. Service on a repository (9, 10, 15, 16).
5. One repository, two ViewModels (11, 17, 18).
6. Data sources and caching (12, 13).
7. Consistency and idempotency (14, 20).

Then recap, review, next, lab and end. Section 9's RepositoryPaymentService is shown in section 15's error-mapping
version, which the text says replaces it.

**Evidence: Mac** (the text's code, Swift 6, Debug so `assert` is active)
- Section 8: Before 2500000; a payment ID; After 2349950; Transactions 1.
- Section 19: "Repository test passed", "Correctly rejected".
- Section 7: two concurrent ₹1,500 payments from ₹2,000 → one recorded, one `insufficientBalance`; balance ₹500.
- Ours: 1,000 concurrent ₹1 payments from ₹500 → 500 recorded, 500 rejected, balance 0.
- Section 14 (ours, the text's unsafe shape built on an actor, with a 20 ms await between read and write): two ₹1,500
  payments at once from ₹2,000 → both accepted, 2 transactions totalling ₹3,000, balance ₹500.
- Sections 15–16: the service rethrows `insufficientBalance` / `invalidRecipient` as `PaymentError`. Lesson 4.4's
  ViewModel still shows "Payment could not be completed." (noted on a slide; specific messages come in 4.7).
- Sections 11/17/18:
  - A new DashboardViewModel shows 0 before its first refresh.
  - After a payment it still shows 2500000 until `refresh()`, then 2349950 and 1 transaction.
  - A dashboard on its own repository shows 2500000.
- Section 20: the same request twice in sequence → 2 transactions, balance 2,199,900.

**Evidence: simulator** (`sh tools/sim4_5/run.sh`): our lab screen pays ₹1,500.50 through one NPayDependencies.
- Without refresh: it shows ₹25,000.00 and "Payments: 0" while the repository holds 2,349,950 and 1.
- With section 18's refresh: ₹23,499.50 and "Payments: 1" (screenshots).

**Authored (flagged)**
- Every run above. The concurrent stress test. The split workflow for section 14 (the text shows only the unsafe calls,
  which don't exist on our repository). The simulator lab screen.
- Diagrams for sections 1, 3, 10 and 12, from the text's lists.
- The section 7 and 13 interactive widgets, replaced by measured runs and a strategy table.
- Review: the text's 7 questions (options reordered) plus three more:
  - two predict items (the split workflow, the stale dashboard);
  - a spaced item from 4.4.
  - Question 2 (LazyVStack) is the text's own and is marked as spaced review from 3.11.
  - 5 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab.
- The end slide's "Next: Lesson 4.6 — Domain Models & Use Cases", from the 4.1 text's Unit 4 sequence; this text has no
  next-lesson line.

**Snippets**
- Section 14's unsafe example calls `fetchBalance`, `saveTransaction` and `updateBalance`, which the repository
  deliberately doesn't have (an illustration).
- Section 6's actor is condensed on the slide.
- Every other snippet compiles (Swift 6, full compile).

**Wording**
- "Senior engineer insight / knowledge check" became neutral labels and "Check your understanding".
