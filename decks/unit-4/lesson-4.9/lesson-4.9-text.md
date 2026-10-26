# Unit 4 · Lesson 4.9 — Architecture Testing: XCTest, Swift Testing & Mock Dependencies

NPay iOS Engineering Masterclass · Part 1 + Part 2 · Incremental Labs · Test Architecture · Async Testing Internals

In Lesson 4.8, we organized NPay into modules:

NPayApp → NPayDomain ← NPayData

We also created PaymentViewModel, SendPaymentUseCase, and InMemoryAccountRepository.

Now we're going to answer a critical engineering question:

How can we prove that NPay correctly processes payments, handles insufficient balances, prevents duplicate submissions, and maintains consistent account state — without manually opening the iOS Simulator every time?

Today we'll build automated tests, investigate how they execute behind the scenes, and learn how professional iOS teams structure their testing strategy.

## Part 1 — Unit Testing from First Principles

## 1. Our NPay testing milestone

By the end of this lesson, we'll test four layers.

Domain Tests

PaymentAmount · PaymentRecipient · PaymentPolicy

Use Case Tests

SendPaymentUseCase · limits · failures

Repository Tests

Balance consistency · transaction records

ViewModel Tests

Submission states · errors · duplicate prevention

We'll start with small, deterministic tests and gradually move toward asynchronous ViewModel testing.

## 2. What is a unit test?

A unit test verifies a small, isolated piece of application behavior.

For example:
```swift
let amount = try PaymentAmount(paise: 150_050)
```
We want to verify that the amount is accepted.

And:

try PaymentAmount(paise: -100)

should throw an error.

A test has three conceptual stages

Arrange

Prepare inputs

Act

Execute behavior

Assert

Verify result

For NPay:

Arrange a payment amount.

Act by creating PaymentAmount.

Assert that it contains the expected paise.

## 3. XCTest versus Swift Testing

Apple supports two important testing approaches.

| XCTest | Swift Testing |
|---|---|
| Mature testing framework | Modern Swift-native testing framework |
| XCTestCase classes | @Test functions |
| XCTAssertEqual | #expect |
| XCTAssertThrowsError | #expect(throws:) |
| Supports UI testing | Primarily unit and integration tests |
| Common in existing codebases | Good choice for new Swift tests |

For NPay, we'll learn both.

Swift Testing is available with modern Swift toolchains, including Xcode 16 and later.

## 4. First XCTest lab — PaymentAmount

Create a test target in Xcode if one doesn't already exist.

Then create PaymentAmountTests.swift.
```swift
import XCTest
@testable import NPay

final class PaymentAmountTests: XCTestCase {

    func testValidAmount() throws {
        let amount = try PaymentAmount(paise: 150_050)

        XCTAssertEqual(amount.paise, 150_050)
    }

    func testZeroAmountRejected() {
        XCTAssertThrowsError(
            try PaymentAmount(paise: 0)
        )
    }

    func testNegativeAmountRejected() {
        XCTAssertThrowsError(
            try PaymentAmount(paise: -100)
        )
    }
}
```
Important module note

If PaymentAmount has moved into the separate NPayDomain module, replace:

@testable import NPay

with:

@testable import NPayDomain

The test target must also declare the appropriate dependency.

## 5. Run tests in Xcode

Use:

Product → Test or press ⌘U.

Xcode builds the test target, launches the appropriate test environment, executes the tests, and reports results.

Behind the scenes

Xcode Test Action

Starts the selected test plan

Build System

Compiles application and test modules

Test Runner

Loads and executes test code

Assertions

Compare actual and expected behavior

Test Report

Shows passed, failed and skipped tests

## 6. The same test using Swift Testing

Now create a Swift Testing version.
```swift
import Testing
@testable import NPay

struct PaymentAmountSwiftTests {

    @Test
    func validAmount() throws {
        let amount = try PaymentAmount(paise: 150_050)

        #expect(amount.paise == 150_050)
    }

    @Test
    func zeroAmountRejected() {
        #expect(throws: PaymentDomainError.self) {
            try PaymentAmount(paise: 0)
        }
    }
}
```
What's different?
```swift
@Test identifies a test function.
```
#expect evaluates an expectation and reports failures with useful expression details.

Swift Testing also supports parameterized tests, traits, and asynchronous testing.

## 7. Parameterized tests — test multiple values

Instead of writing separate tests for every invalid amount, use a parameterized test.
```swift
import Testing
@testable import NPay

struct PaymentAmountParameterizedTests {

    @Test(arguments: [0, -1, -100, -50_000])
    func rejectsNonPositiveAmounts(paise: Int) {
        #expect(throws: PaymentDomainError.self) {
            try PaymentAmount(paise: paise)
        }
    }
}
```
This runs the test with multiple inputs.

Why is this useful?

Payment validation often has boundary conditions.

Parameterized tests help cover many values without duplicating test structure.

## 8. Boundary-value testing

Consider our illustrative payment limit of ₹1,00,000.

The policy accepts amounts up to 10,000,000 paise.

Which values should we test?

Payment limit boundary explorer

Payment amount

₹1,00,000

Accepted by policy

Illustrative per-payment limit: ₹1,00,000

Important boundary values

- Just below the limit.

- Exactly at the limit.

- Just above the limit.

This testing technique is called boundary-value analysis.

## 9. Test PaymentPolicy

```swift
import Testing
@testable import NPay

struct PaymentPolicyTests {

    let policy = PaymentPolicy(
        maximumPerPaymentPaise: 10_000_000
    )

    @Test
    func acceptsAmountAtLimit() throws {
        let amount = try PaymentAmount(
            paise: 10_000_000
        )

        try policy.validate(amount)
    }

    @Test
    func rejectsAmountAboveLimit() throws {
        let amount = try PaymentAmount(
            paise: 10_000_001
        )

        #expect(throws: PaymentDomainError.self) {
            try policy.validate(amount)
        }
    }
}
```
What are we proving?

The policy behaves correctly at its boundaries.

We don't need a ViewModel, repository, or SwiftUI screen to test it.

## Part 2 — Repository, Use Case & ViewModel Testing

## 10. Test our actor-based repository

Our repository is a Swift actor.

Therefore, test methods calling it use async/await.
```swift
import Testing
@testable import NPay

struct AccountRepositoryTests {

    @Test
    func paymentUpdatesBalanceAndHistory() async throws {

        let repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000
        )

        let payment = try await repository.recordPayment(
            recipient: "ravi@npay",
            amountPaise: 150_050
        )

        let snapshot = try await repository.fetchSnapshot()

        #expect(payment.amountPaise == 150_050)
        #expect(snapshot.balancePaise == 2_349_950)
        #expect(snapshot.transactions.count == 1)
    }
}
```
What does this test verify?

The repository updates balance and transaction history consistently for a successful local demo payment.

## 11. Test insufficient balance

```swift
@Test
func insufficientBalanceDoesNotChangeState() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 10_000
    )

    do {
        _ = try await repository.recordPayment(
            recipient: "ravi@npay",
            amountPaise: 50_000
        )

        Issue.record("Expected insufficient balance")
    } catch AccountRepositoryError.insufficientBalance {
        // Expected rejection.
    }

    let snapshot = try await repository.fetchSnapshot()

    #expect(snapshot.balancePaise == 10_000)
    #expect(snapshot.transactions.isEmpty)
}
```
Senior engineer insight

A test should verify not only that an error occurred, but also that rejected operations did not partially mutate account state.

## 12. Test concurrent payments

Let's simulate two payments attempting to spend the same balance.
```swift
@Test
func concurrentPaymentsDoNotOverdraw() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 200_000
    )

    async let first = Result {
        try await repository.recordPayment(
            recipient: "a@npay",
            amountPaise: 150_000
        )
    }

    async let second = Result {
        try await repository.recordPayment(
            recipient: "b@npay",
            amountPaise: 150_000
        )
    }

    let results = await [first, second]

    let successCount = results.filter {
        if case .success = $0 { return true }
        return false
    }.count

    let snapshot = try await repository.fetchSnapshot()

    #expect(successCount == 1)
    #expect(snapshot.balancePaise == 50_000)
    #expect(snapshot.transactions.count == 1)
}
```
Important correction for Xcode

The standard synchronous Result initializer cannot directly accept an asynchronous throwing closure.

For a compile-ready version, use a helper:
```swift
func attemptPayment(
    repository: InMemoryAccountRepository,
    recipient: String,
    amountPaise: Int
) async -> Result<PaymentRecord, Error> {
    do {
        let record = try await repository.recordPayment(
            recipient: recipient,
            amountPaise: amountPaise
        )
        return .success(record)
    } catch {
        return .failure(error)
    }
}
```
Then:
```swift
@Test
func concurrentPaymentsDoNotOverdraw() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 200_000
    )

    async let first = attemptPayment(
        repository: repository,
        recipient: "a@npay",
        amountPaise: 150_000
    )

    async let second = attemptPayment(
        repository: repository,
        recipient: "b@npay",
        amountPaise: 150_000
    )

    let results = await [first, second]

    let successCount = results.filter {
        if case .success = $0 { return true }
        return false
    }.count

    let snapshot = try await repository.fetchSnapshot()

    #expect(successCount == 1)
    #expect(snapshot.balancePaise == 50_000)
    #expect(snapshot.transactions.count == 1)
}
```
Use this corrected version, not the earlier illustrative snippet.

## 13. Test SendPaymentUseCase

Our use case coordinates domain policy and repository access.
```swift
@Test
func useCaseEnforcesPaymentLimit() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 20_000_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository,
        policy: PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 15_000_000)
    )

    do {
        _ = try await useCase.execute(command)
        Issue.record("Expected limitExceeded")
    } catch PaymentDomainError.limitExceeded {
        // Expected.
    }

    let snapshot = try await repository.fetchSnapshot()

    #expect(snapshot.transactions.isEmpty)
}
```
Why test both policy and use case?

The policy test verifies the rule itself.

The use-case test verifies that the application operation actually applies the rule.

Both are useful, but they test different boundaries.

## 14. Test PaymentViewModel with a mock use case

Our current PaymentViewModel depends on a concrete SendPaymentUseCase struct.

That's fine for production code, but it makes isolated ViewModel tests less flexible.

We have two choices:

1. Use a real use case with an in-memory repository.

2. Introduce a use-case protocol and inject a mock.

For this lesson, let's introduce a small protocol.
```swift
protocol SendPaymentExecuting: Sendable {
    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord
}
```
Make our use case conform:

extension SendPaymentUseCase: SendPaymentExecuting {}

Then change the ViewModel dependency:
```swift
private let sendPayment: any SendPaymentExecuting
```
And its initializer:
```swift
init(sendPayment: any SendPaymentExecuting) {
    self.sendPayment = sendPayment
}
```
Now the ViewModel can accept a mock.

## 15. Build a mock use case

```swift
import Foundation

struct MockSendPaymentUseCase: SendPaymentExecuting {

    let shouldFail: Bool

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        if shouldFail {
            throw PaymentDomainError.insufficientBalance
        }

        return PaymentRecord(
            id: UUID(),
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise,
            createdAt: .now
        )
    }
}
```
This mock can deterministically simulate success or failure.

It doesn't require a repository or database.

## 16. Test ViewModel success state

```swift
import Testing
@testable import NPay

@MainActor
struct PaymentViewModelTests {

    @Test
    func successfulPaymentUpdatesState() async throws {

        let mock = MockSendPaymentUseCase(
            shouldFail: false
        )

        let viewModel = PaymentViewModel(
            sendPayment: mock
        )

        let command = SendPaymentCommand(
            recipient: try PaymentRecipient("ravi@npay"),
            amount: try PaymentAmount(paise: 150_050)
        )

        let result = await viewModel.submit(command)

        if case .success(let record) = result {
            #expect(record.amountPaise == 150_050)
        } else {
            Issue.record("Expected success")
        }

        if case .success = viewModel.state {
            // Correct state.
        } else {
            Issue.record("Expected success UI state")
        }
    }
}
```
What are we verifying?

The ViewModel:

- Calls the use case.

- Receives the result.

- Returns success.

- Updates its observable UI state.

We don't need to display the payment screen.

## 17. Test ViewModel failure state

*(The text breaks here; Section 13 continues below.)*

---

## Part 2 (continued): ViewModel Testing, Async Tests & Test Architecture

NPay iOS Engineering Masterclass · Continuing from Section 17 · Final Part of Lesson 4.9

We've tested our domain models, payment policy, actor-based repository, concurrent transactions, and successful ViewModel submissions.

Now we'll complete Lesson 4.9 by testing failure states, duplicate submissions, asynchronous operations, and the overall testing strategy for NPay.

## 17. Test PaymentViewModel failure state

In the previous section, we created MockSendPaymentUseCase.

It can deliberately throw an insufficient-balance error.

Let's verify that PaymentViewModel correctly translates this into UI state.
```swift
import Testing
@testable import NPay

@MainActor
struct PaymentFailureTests {

    @Test
    func insufficientBalanceUpdatesFailureState() async throws {

        let mock = MockSendPaymentUseCase(
            shouldFail: true
        )

        let viewModel = PaymentViewModel(
            sendPayment: mock
        )

        let command = SendPaymentCommand(
            recipient: try PaymentRecipient("ravi@npay"),
            amount: try PaymentAmount(paise: 150_050)
        )

        let result = await viewModel.submit(command)

        if case .failure(let message) = result {
            #expect(message == "Insufficient balance")
        } else {
            Issue.record("Expected failure result")
        }

        if case .failure(let message) = viewModel.state {
            #expect(message == "Insufficient balance")
        } else {
            Issue.record("Expected failure UI state")
        }
    }
}
```
What does this test prove?

The ViewModel correctly handles an application error without requiring SwiftUI.

The use case throws.

The ViewModel catches the error.

The ViewModel exposes an appropriate failure state.

This is a unit test of presentation behavior, not a UI automation test.

## 18. Test duplicate submission prevention

Our ViewModel contains:
```swift
guard !state.isBusy else {
    return .failure("A payment is already processing")
}
```
We need to verify that two overlapping calls don't both execute the use case.

First, create a controllable mock

A reliable async test needs to control when the dependency completes.

Create SuspendedPaymentUseCase.swift in the test target.
```swift
import Foundation

actor SuspendedPaymentUseCase: SendPaymentExecuting {

    private var continuation:
        CheckedContinuation<PaymentRecord, Error>?

    private var invocationCount = 0

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        invocationCount += 1

        return try await withCheckedThrowingContinuation {
            continuation = $0
        }
    }

    func calls() -> Int {
        invocationCount
    }

    func succeed() {
        continuation?.resume(
            returning: PaymentRecord(
                id: UUID(),
                recipient: "ravi@npay",
                amountPaise: 150_050,
                createdAt: .now
            )
        )

        continuation = nil
    }
}
```
Why use a continuation?

withCheckedThrowingContinuation allows a callback-style completion to be represented as an asynchronous operation.

In our test, we deliberately hold the operation open.

The ViewModel remains in .submitting until the mock completes.

Important caution

Every checked continuation must be resumed exactly once.

A production-quality test double should handle unexpected cancellation and cleanup so no test remains suspended indefinitely.

## 19. Run the duplicate-submission test

```swift
import Testing

@MainActor
@Test
func duplicateSubmissionIsRejected() async throws {

    let mock = SuspendedPaymentUseCase()

    let viewModel = PaymentViewModel(
        sendPayment: mock
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 150_050)
    )

    let firstTask = Task {
        await viewModel.submit(command)
    }

    // Wait until the mock has received the first call.
    while await mock.calls() == 0 {
        await Task.yield()
    }

    let secondResult = await viewModel.submit(command)

    if case .failure = secondResult {
        // Expected local rejection.
    } else {
        Issue.record("Expected duplicate rejection")
    }

    #expect(await mock.calls() == 1)

    await mock.succeed()

    let firstResult = await firstTask.value

    if case .success = firstResult {
        // Expected.
    } else {
        Issue.record("Expected first payment to succeed")
    }
}
```
What does this prove?

While the first payment is suspended, the ViewModel remains busy.

The second submission is rejected before calling the use case.

Only one request reaches the dependency.

Senior engineer nuance

This verifies local overlapping-submission protection. It does not establish durable payment idempotency.

Also, the polling loop is a teaching shortcut. A robust test suite should use explicit synchronization and bounded waits so a regression cannot hang the test indefinitely.

## 20. Why should asynchronous tests avoid arbitrary sleeps?

Consider:
```swift
try await Task.sleep(for: .seconds(1))
```
Developers sometimes use this to wait for asynchronous work.

But fixed delays are fragile.

On a fast machine, the test wastes time.

On a slow machine, one second may not be enough.

Better testing strategy

Use controlled dependencies, continuations, expectations, or other synchronization mechanisms.

Async test reliability

| Approach | Reliability |
|---|---|
| Arbitrary sleep | Timing-dependent |
| Controlled mock completion | Deterministic when correctly synchronized |
| Test expectations | Explicitly await an event |
| Injected clock | Useful for retry and debounce testing |

We'll use clock injection later when implementing retry policies and search debouncing.

## 21. Behind the scenes — how an async test executes

NPay asynchronous test lifecycle

*(Interactive stepper in the original, 8 stages; only stage 1 was shared.)*

1. Test runner starts

Swift Testing invokes the asynchronous test.

PreviousNext step

## 22. Unit tests versus integration tests versus UI tests

These tests serve different purposes.

NPay testing layers

UI Tests

Complete user journeys

Integration Tests

ViewModel + use case + repository

Unit Tests

Value objects, policies, isolated ViewModels

Examples

A unit test checks that PaymentAmount rejects zero.

An integration test verifies that sending ₹1,500.50 updates the shared account repository and creates one transaction.

A UI test opens NPay, enters a recipient, reviews the payment, confirms it, and verifies the success screen.

We'll cover UI automation in depth in Unit 9.

## 23. Integration test — complete NPay payment operation

Let's test the real domain and repository components together.
```swift
import Testing
@testable import NPay

@Test
func paymentIntegrationTest() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 2_500_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository,
        policy: PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 150_050)
    )

    let payment = try await useCase.execute(command)

    let snapshot = try await repository.fetchSnapshot()

    #expect(payment.amountPaise == 150_050)
    #expect(snapshot.balancePaise == 2_349_950)
    #expect(snapshot.transactions.count == 1)
    #expect(snapshot.transactions.first?.id == payment.id)
}
```
What are we testing?

Multiple real components working together:

SendPaymentUseCase → AccountRepository → InMemoryAccountRepository

This catches integration problems that isolated mocks might miss.

## 24. Test coverage — what does 100% mean?

Test coverage measures which portions of code were exercised during tests.

But 100% line coverage doesn't mean the application is correct.

Consider:

if amount > balance {

throw PaymentError.insufficientBalance

}

A test that executes only the valid-payment path may cover surrounding code but fail to verify the rejection behavior.

Better approach

Test meaningful behaviors and boundaries.

For NPay, important scenarios include:

- Valid payment.

- Zero and negative amounts.

- Empty recipient.

- Insufficient balance.

- Payment exactly at the limit.

- Payment above the limit.

- Concurrent requests.

- Duplicate submission.

- Repository failure.

- Unknown remote outcome, once networking exists.

Coverage is a useful signal, but it isn't a substitute for well-designed assertions.

## 25. Xcode test organization

A practical structure:
```text
NPayTests/
├── Domain/
│   ├── PaymentAmountTests.swift
│   ├── PaymentRecipientTests.swift
│   └── PaymentPolicyTests.swift
│
├── UseCases/
│   └── SendPaymentUseCaseTests.swift
│
├── Repositories/
│   └── InMemoryAccountRepositoryTests.swift
│
├── ViewModels/
│   └── PaymentViewModelTests.swift
│
└── TestDoubles/
├── MockSendPaymentUseCase.swift
└── SuspendedPaymentUseCase.swift
```
If you've extracted NPayDomain and NPayData into separate Swift package targets, tests can also live in the relevant package test targets.

Xcode practice

Run tests with ⌘U.

Use the Test Navigator to inspect individual results.

Use code coverage reports to identify untested paths.

Use breakpoints inside tests to inspect the ViewModel and repository state.

## 26. Final Unit 4.9 lab checklist

NPay Architecture Testing Lab

*(Interactive checklist in the original.)*

Create a Swift Testing target

Test PaymentAmount valid and invalid values

Test PaymentPolicy boundary values

Test PaymentRecipient validation

Test successful repository payment

Test insufficient balance without partial mutation

Test concurrent payments

Test SendPaymentUseCase policy enforcement

Test PaymentViewModel success

Test PaymentViewModel failure

Test overlapping submission protection

Run the complete test suite using ⌘U

Inspect coverage and failed-test diagnostics

## 27. Senior engineer knowledge check

Architecture Testing Assessment

*(Interactive quiz in the original.)*

**1. What is the main purpose of a unit test?**

Verify a small behavior in isolation

Test only UI animations

Replace the compiler

**2. Why use mocks in ViewModel tests?**

To control dependency behavior

To generate real payments

To replace SwiftUI rendering

**3. Does 100% line coverage guarantee correctness?**

Yes

No

**4. Why avoid arbitrary sleeps in async tests?**

They create timing-dependent tests

They disable actors

They prevent compilation

**5. What does an integration test verify?**

Multiple components working together

Only one pure function

Only app icon rendering

**6. Should rejected payments leave the repository state unchanged?**

Yes

No

**7. Does local duplicate-submission protection guarantee backend idempotency?**

Yes

No

Lesson 4.9 — Completed

We've now covered XCTest, Swift Testing, parameterized tests, boundary testing, actor-based repository tests, async mocks, ViewModel state tests, concurrency tests, integration tests, and coverage

## Integration through Lesson 4.9 (authored)

Everything is in `tools/sim4_9/`:
- **The app (`NPay/`):** section 14's change is applied. A new `Features/Payments/SendPaymentExecuting.swift` holds
  the protocol plus `extension SendPaymentUseCase: SendPaymentExecuting {}`, and PaymentViewModel holds
  `any SendPaymentExecuting`. `run.sh` rebuilds and re-verifies the app (payment ₹23,499.50, four tabs).
- **NPayCore's tests:**
  - `Tests/NPayDomainTests`: the XCTest class (section 4), Swift Testing (6), parameterized (7), policy boundaries (9),
    and PaymentRecipient tests (ours, a lab-checklist item).
  - `Tests/NPayDataTests`: a new test target (ours) depending on NPayDomain and NPayData. It holds the repository tests
    (10, 11, 12 with the corrected `attemptPayment`), the use-case test (13) and the integration test (23).
- **`NPayAppTests/` (ours):** the text uses `@testable import NPay` from an Xcode test target; this repo has no Xcode
  project. This package compiles the app's own payment files, symlinked from `NPay/`, into a module `NPayPayments`.
  - The tests use `@testable import NPayPayments` plus `import NPayDomain`, because the domain types live in that
    module since 4.8.
  - It holds `MockSendPaymentUseCase` (15), `SuspendedPaymentUseCase` (18), the ViewModel tests (16, 17, 19), and our
    real-chain message test.
- **`test.sh`** runs both packages with coverage. **`experiments.sh`** runs the planted bug and the missing guard on
  throwaway copies.

## Deck changes

The text came in three pieces: Part 1 (sections 1–9), Part 2 (10–17, breaking inside 17), and a continuation (17–27).

The deck (`index.html`, built by `tools/gen4_9.py`, 40 slides) has 8 Parts:
1. Unit testing (sections 1, 2, 3).
2. First tests (4, 5, 6).
3. Parameters and boundaries (7, 8, 9).
4. Repository and use case (10, 11, 12, 13, 23).
5. ViewModel tests with mocks (14, 15, 16, 17).
6. Async tests (18, 19, 20, 21).
7. Layers and coverage (22, 24).
8. Organizing tests (25, 26).

Then recap, review, next, lab and end.

**Evidence** (`sh tools/sim4_9/test.sh`, `sh tools/sim4_9/experiments.sh`)
- **NPayCore:** XCTest "Executed 3 tests, with 0 failures". Swift Testing "Test run with 12 tests in 5 suites passed".
  The parameterized tests ran with 4 and 3 cases.
- **NPayAppTests:** "Test run with 4 tests in 2 suites passed" (success, failure, duplicate, real chain).
- **Section 12's first snippet** (`Result { try await … }`): "cannot pass function of type '() async throws ->
  PaymentRecord' to parameter expecting synchronous function type". This confirms the text's correction.
- **Coverage** (`swift test --enable-code-coverage`, `llvm-cov report`): InMemoryAccountRepository 95.00%,
  AccountRepository / PaymentAmount / PaymentRecipient 100.00%, SendPaymentUseCase 82.35%, total 92.16%.
- **Planted bug** (`<=` → `<` in PaymentPolicy):
  - The suite fails exactly `acceptsAmountAtLimit()` ("Caught error: .limitExceeded").
  - With that test removed, 11 tests pass and coverage is unchanged (82.35% / 92.16%).
- **No `isBusy` guard:** `duplicateSubmissionIsRejected` never finishes (stopped after 40 s). With the guard it passes
  in under a second.

**Authored (flagged)**
- The app change's file placement, the NPayDataTests target, NPayAppTests, the recipient tests, the real-chain test,
  both scripts and every run.
- The section 1 and 22 diagrams.
- Section 5's test-action flow (from the text's list).
- The interactive widgets (sections 8, 21), replaced by the boundary tests and the measured hang.
- Review: the text's 7 questions (options reordered) plus three more:
  - two predict items (bug + coverage; missing guard);
  - a spaced item from 4.8.
  - 2 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab.
- The end slide's "Next: Lesson 4.10 — Unit 4 Integration Lab", from the 4.1 sequence; this text ends without a
  next-lesson line.

**Snippets:** every test on the slides was compiled and run. Some slides show condensed excerpts (sections 11, 12,
14–15, 17); the full files are in `tools/sim4_9/`.

**Wording**
- "Senior engineer insight / nuance / knowledge check" became neutral labels and "Check your understanding".
