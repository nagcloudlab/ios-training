# Unit 1 · Lesson 1.10 — Build PocketBank's Domain Model

> Lesson text as shared (two parts, plus a follow-up Q&A about practising on Windows); the deck (`index.html`) is built
> from it. **PocketBank is renamed NPay** (the course's running app). The lesson's code is verified as a Swift package,
> `NPayCore`, with Swift Testing tests. Corrections and authored additions are listed at the end under "Deck changes".

Swift Language Mastery · Final Integration Lesson · Senior Developer & Trainer Edition

We've now explored Swift types, Optionals, functions, closures, structs, classes, protocols, generics, errors, ARC, and concurrency.

Today, we'll connect these concepts by designing the core engine of PocketBank.

Our goal is to build a small but well-structured Swift banking simulation, not just write disconnected examples.

## 1. The engineering challenge

PocketBank needs to support the following capabilities:
- Create bank accounts.
- Represent money accurately.
- Deposit and withdraw money.
- Validate transfers.
- Store transaction records.
- Load account information asynchronously.
- Prevent unsafe concurrent modifications.
- Handle failures explicitly.

Before writing code, let's decide which Swift features belong where.

## 2. Architecture first — identify the responsibilities

(PocketBank domain architecture: Application / ViewModel — coordinates user actions → BankingService protocol — defines supported operations → BankLedger actor — protects shared account state → Account — value model; Transaction — value model. In-memory learning architecture. Production banking requires server-side authoritative ledgers, authentication, durable transactions and audit controls.)

**Trainer question.** Why don't we put everything into one BankAccount class? Because account data, validation, transaction processing, and shared-state synchronization are different responsibilities. Separating them makes the design easier to reason about, test, and extend.

## 3. Start with Money — a value object

Money should be represented carefully. For this learning project, we'll support INR using integer paise.

```swift
struct Money: Equatable, Sendable {
    let paise: Int64

    init(paise: Int64) {
        self.paise = paise
    }

    var rupees: Decimal {
        Decimal(paise) / Decimal(100)
    }
}
```

Why a struct? Because a monetary amount is naturally a value.

Why Int64? Because it allows exact integer representation of paise within its numeric range.

Why Sendable? Because this immutable value can safely cross Swift concurrency isolation boundaries.

(Interactive money explorer: stored amount 25,00,000 paise → displayed amount ₹25,000.00. Integer minor units → formatted rupees.)

## 4. Model the account

```swift
struct BankAccount: Identifiable, Sendable {
    let id: String
    let customerName: String
    var balance: Money
    var isActive: Bool
}
```

| Property | Why? |
|---|---|
| id | Unique account identifier |
| customerName | Account holder's display name |
| balance | Monetary value |
| isActive | Account status |
| Identifiable | Standard identity contract |
| Sendable | Supports safe transfer across concurrency boundaries |

The account is a value model. The shared mutable collection of accounts will be owned by an actor.

## 5. Model transactions

Every deposit, withdrawal, or transfer should produce a transaction record.

```swift
enum TransactionType: String, Sendable {
    case deposit
    case withdrawal
    case transfer
}

struct Transaction: Identifiable, Sendable {
    let id: UUID
    let accountId: String
    let type: TransactionType
    let amount: Money
    let timestamp: Date
}
```

We use an enum because the transaction type belongs to a known set of valid cases. This is safer than relying on arbitrary strings such as "Deposit", "deposit", or "DEPOSIT".

## 6. Define banking errors

```swift
enum BankingError: Error {
    case accountNotFound
    case accountInactive
    case invalidAmount
    case insufficientFunds
    case sameAccountTransfer
    case arithmeticOverflow
}
```

These cases represent domain failures.

**Trainer insight.** A good error model describes why an operation failed. Avoid returning only false for every failure. A boolean often loses important information.

## 7. Define the service contract

```swift
protocol BankingService: Sendable {
    func balance(for accountId: String) async throws -> Money
    func deposit(_ amount: Money, into accountId: String) async throws
    func withdraw(_ amount: Money, from accountId: String) async throws
    func transfer(_ amount: Money, from sourceId: String, to destinationId: String) async throws
}
```

The protocol describes what the banking service can do. It does not specify how those operations are implemented. Later, we could create a mock service, an in-memory service, or a network-backed implementation.

## 8. Why use an actor for the ledger?

Suppose two tasks attempt to withdraw money from the same account. Without appropriate synchronization, both might read the same original balance and independently approve their withdrawals.

An actor helps protect its isolated mutable state from unsynchronized concurrent access.

(Actor isolation concept: Task A, Task B → BankLedger actor — isolated mutable account state — accounts dictionary.)

An actor serializes access to its isolated state, but it is not automatically a database transaction system. An actor method can also be reentrant across suspension points. For our in-memory transfer operation, we'll deliberately avoid await between validation and mutation.

## 9. Implement the BankLedger actor

(Code: `actor BankLedger: BankingService` with `private var accounts: [String: BankAccount]`, `init(accounts:)`, `balance(for:) throws -> Money`, and `deposit(_:into:) throws` validating amount > 0, account exists, account active, and `addingReportingOverflow`.)

Notice that the actor's methods don't need to be explicitly declared async when they contain no suspension points. However, callers outside the actor's isolation normally use await to access these methods. The protocol's asynchronous requirements can be satisfied by actor-isolated implementations under appropriate Swift concurrency rules.

## 10. Implement withdrawal

(Code: `extension BankLedger { func withdraw(_:from:) throws }` validating amount > 0, account exists, active, sufficient funds, then subtracting.)

**Why does validation order matter?** We must confirm that the account exists, is active, and has sufficient funds before modifying its balance. For nonnegative balances and a positive withdrawal amount no greater than the balance, the subtraction is safe within the Int64 range.

## 11. Implement transfer — the most important operation

A transfer modifies two accounts. The source balance decreases. The destination balance increases. Both changes must be treated as one logical operation.

(Transfer between accounts: Ravi before ₹25,000 → ₹20,000 (source); Meena before ₹10,000 → ₹15,000 (destination); transfer amount ₹5,000. Combined balance remains ₹35,000 in this zero-fee example. Conceptual transfer simulation, not a real banking transaction.)

(Code: `transfer(_:from:to:) throws` — reject same account, invalid amount, missing accounts, inactive accounts, insufficient funds, destination overflow; then update both accounts.)

**Why is this safe within our simulation?** The actor protects its isolated account dictionary. The method performs validation and mutation without an await suspension point. That prevents other actor-isolated operations from interleaving with this transfer's critical section. But this is still only an in-memory simulation. It does not provide durable ACID transactions, distributed consistency, or protection against process termination.

## 12. Use the service from application code

(Code: create a ledger with PB1001 Ravi 2,500,000 paise and PB2002 Meena 1,000,000 paise; in a Task, transfer 500,000 paise and print both balances' `rupees`.)

Expected balances: Ravi: ₹20,000; Meena: ₹15,000.

## 13. Where do transactions fit?

Our current ledger updates balances but doesn't yet record transaction history. A stronger design would store transaction records alongside account changes.

```swift
struct LedgerEntry: Sendable {
    let id: UUID
    let accountId: String
    let amountInPaise: Int64
    let timestamp: Date
}
```

For a transfer, we could create a debit entry and a credit entry. In a production system, the ledger entries and account state must be committed durably and consistently. This leads to concepts such as double-entry bookkeeping, idempotency, auditability, and transactional databases. Those are backend architecture concerns, not guarantees provided by Swift actors alone.

## 14. Testing the domain model (Part 2 completes it)

One advantage of separating domain logic from SwiftUI is that we can test it without launching an iPhone interface.

(Code: Swift Testing `@Test func transferMovesMoney() async throws` creating accounts A (Ravi ₹25,000) and B (Meena ₹10,000), transferring 500,000 paise, then `#expect(a.paise == 2_000_000)` and `#expect(b.paise == 1_500_000)`.)

Create test accounts → Execute transfer → Read updated balances (actor-isolated calls using await) → Verify expectations.

@Test identifies a test using Swift Testing. #expect verifies that a condition holds and reports a test failure if it doesn't.

**Trainer insight:** A successful test demonstrates correctness for the tested scenario. It doesn't prove the entire banking system is correct.

## 15. Test failure scenarios

(Code: `@Test func insufficientFundsThrows()` with A ₹1,000, B ₹500, transferring ₹2,000 inside `await #expect(throws: BankingError.self) { … }`.)

This checks that the transfer throws a BankingError. For more precise testing, we'd verify that the error is specifically .insufficientFunds, and that neither balance changed.

| Scenario | Expected result |
|---|---|
| Valid deposit | Balance increases |
| Negative deposit | Rejected |
| Valid withdrawal | Balance decreases |
| Insufficient funds | Rejected |
| Inactive account | Rejected |
| Same-account transfer | Rejected |
| Destination overflow | Rejected |
| Valid transfer | Both balances updated |
| Failed transfer | Neither balance changes |

## 16. The concurrency challenge

Task A transfers ₹7,000 from Ravi. Task B transfers ₹6,000 from Ravi. Ravi has only ₹10,000. Both transfers cannot succeed.

(Concurrent withdrawal experiment: actor-isolated / unsafe read-modify-write. Conceptual concurrency simulation, not actual parallel Swift execution.)

**Critical detail about actors.** An actor prevents unsynchronized access to its isolated mutable state. But actors are reentrant across suspension points.

```swift
actor AccountStore {
    var balance = 10000

    func withdraw(_ amount: Int) async throws {
        guard balance >= amount else {
            throw BankingError.insufficientFunds
        }

        await performExternalCheck()

        balance -= amount
    }
}
```

This design is unsafe if another operation can change balance while the task is suspended. After the await, the earlier validation may no longer be valid.

**Trainer rule:** Never assume actor isolation automatically makes a multi-step asynchronous business operation atomic.

## 17. The actor reentrancy problem — visually

(Step 1 / 5: Task A enters actor; reads balance ₹10,000 and validates a ₹7,000 withdrawal. …)

**How do we fix this?** Keep critical validation and mutation together without suspension, or revalidate state after an await using an appropriate concurrency-control strategy. For a real banking backend, this problem requires transactional database design and business-level consistency guarantees.

## 18. Our final PocketBank architecture

SwiftUI View (user interaction and presentation) → ViewModel (observable state and asynchronous coordination) → BankingService protocol (abstraction and dependency injection) → BankLedger actor (protects in-memory shared mutable state) → Money, Account, Transaction (structs).

| Swift concept | PocketBank usage |
|---|---|
| Struct | Money, Account, Transaction |
| Enum | TransactionType, BankingError |
| Protocol | BankingService |
| Generics | Reusable repositories and API responses |
| Optionals | Missing account or customer information |
| Throws | Invalid operations and business failures |
| Async/await | Asynchronous service calls |
| Actor | Isolated mutable account state |
| Sendable | Safe data transfer across isolation boundaries |
| ARC | Lifetime of reference-type services and ViewModels |

## 19. Senior engineer architecture review

1. Can this in-memory actor replace a bank's production database?
2. Can an actor method still have a logical race?
3. Why is Money a struct rather than a class?
4. Why should ViewModel depend on BankingService?
5. Why do we need server-side validation if the iOS app validates transfers?

## Unit 1 — Swift Language Mastery Complete

Lessons 1.1–1.10. You've covered Swift's type system, Optionals, functions, closures, structs, classes, protocols, generics, error handling, ARC, concurrency, and domain modeling. The next essential step is implementing and testing these concepts in Xcode.

Next — Unit 2: SwiftUI & iOS Interface Development (the shared text lists: declarative UI, view hierarchy and layout, @State/@Binding/@Observable, navigation, lists/forms/controls, MVVM, API-driven UI, persistence and state restoration, UI testing and accessibility, complete PocketBank interface). Next lesson: 2.1 — How SwiftUI Works Internally.

## Follow-up Q&A — practising Unit 1 on Windows

Almost everything from Unit 1 can be practised on Windows with the Swift toolchain (VS Code + the Swift extension), using Swift Package Manager: `swift package init --type executable`, `swift run`, `swift build`, `swift test`. SwiftUI, UIKit, the iOS Simulator and iOS app builds need macOS. Recommendation: a platform-independent "Unit 1 Swift Core Labs" package that Windows and macOS participants both run; move to macOS for Unit 2.

*(text ends here as shared)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_10.py`) follows this text, with these changes.

**Verification**
- The lesson's code was built as a Swift package, `NPayCore` (Swift 6, swift-tools-version 6.0), and tested with Swift Testing: **8 tests passed** — the text's two tests, a precise insufficient-funds test (exact error, both balances unchanged), same-account, inactive destination, destination overflow, negative deposit, and a concurrent ₹7,000 + ₹6,000 transfer from ₹10,000 (exactly one succeeds).
- The `BankLedger` actor's synchronous `throws` methods satisfy the protocol's `async throws` requirements (verified).
- Section 12 run for real: prints `Ravi: 20000`, `Meena: 15000` (`rupees` is a `Decimal`; "₹20,000" formatting stays in the ViewModel); a further ₹90,000 transfer prints `Transfer failed: insufficientFunds`.
- Section 16's reentrancy example run for real: "check, await, change" → both withdrawals succeed, balance **−₹3,000**; "await first, then check and change" → one rejected, ₹4,000 left.

**Structure**
- 19 sections grouped into **8 Parts**: architecture (1–2); values (3–6); contract (7); the actor (8–10); transfers and history (11–13); testing (14–15); reentrancy (16–17); architecture (18). Section 19's five questions became the **Architecture review** (plus three authored questions).

**Corrections and canon**
- PocketBank → NPay; accounts `PB1001`/`PB2002` → `NP1001`/`NP2002`. `LedgerEntry.amountInPaise` → `amountPaise` (signed: debit negative, credit positive).
- The text's Unit 2 list and "2.1 — How SwiftUI Works Internally" are replaced by the curriculum plan's Unit 02 (SwiftUI Fundamentals) and Lesson 2.1 "Declarative UI, View & body".
- The Windows Q&A became one "Practice anywhere" slide (SwiftPM `init`/`build`/`test`; Windows via the swift.org toolchain and VS Code; SwiftUI needs macOS). Verified on macOS only; Windows support is per swift.org.
- The interactive simulators (money explorer, transfer, concurrent withdrawal, reentrancy stepper) became stepped diagrams with the real numbers above.

**Authored additions (flagged)**
- Outcomes, "Where we are" (bridge to 1.9), recap.
- Review additions: predict the concurrent transfers (exactly one succeeds), the most precise failure test, and a spaced item from 1.9 (async let duration).
- "Unit 01 complete" slide; "Where this goes next": 2.1, 2.2, 4.3, 4.5, 8.4, 9.2.
- Lab = **Unit 01 checkpoint** (the plan's deliverable): build NPayCore, make the tests pass, add deposit/withdrawal tests, stretch: ledger entries; rubric in the notes.
- End slide: "Next: Unit 02 — SwiftUI Fundamentals, Lesson 2.1: Declarative UI, View & body".
