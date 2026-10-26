# Unit 4 · Lesson 4.10 — Complete NPay MVVM Integration & Architecture Review

NPay iOS Engineering Masterclass · Final Lesson · Part 1 + Part 2 · Architecture Capstone

We've reached the final lesson of Unit 4.

Across Lessons 4.1–4.9, we've learned MVVM, Observation, dependency injection, repositories, domain models, use cases, modularization, and automated testing.

Now we'll bring these concepts together into one coherent NPay architecture.

Our goal is to preserve everything we built in Unit 3 while replacing tightly coupled application logic with maintainable, testable components.

## Part 1 — Integrating NPay's Architecture

## 1. What are we building?

NPay

Architecture Demo

Available Balance

₹25,000.00

NPay Demo Account

Send Money

History

Home

Payments

History

Profile

Interactive representation of NPay's integrated behavior. The native SwiftUI implementation uses typed navigation, asynchronous use cases, and integer-paise money.

The user experience stays the same. What changes is the architecture behind it.

## 2. Final NPay architecture

NPay — Unit 4 architecture

Presentation

SwiftUI Views · PaymentViewModel · DashboardViewModel

Application

SendPaymentUseCase · PaymentPolicy

Domain

PaymentAmount · PaymentRecipient · AccountRepository

Infrastructure

InMemoryAccountRepository actor

Arrows indicate code dependency direction. Infrastructure implements the domain-facing repository contract.

Who owns what?

| Component | Responsibility |
|---|---|
| NPayRootView | Application UI composition |
| NPayRouter | Tabs and navigation |
| PaymentViewModel | Payment form and submission state |
| DashboardViewModel | Balance and recent transactions |
| SendPaymentUseCase | Payment application workflow |
| PaymentPolicy | Illustrative payment limits |
| AccountRepository | Domain data-access contract |
| InMemoryAccountRepository | Local simulated account state |
| NPayPreferences | Appearance preferences |

The most important rule is that each component should have a clear reason to change.

## 3. Final project structure

```text
NPay/
├── App/
│   ├── NPayApp.swift
│   ├── NPayRootView.swift
│   ├── NPayRouter.swift
│   └── NPayDependencies.swift
│
├── Features/
│   ├── Home/
│   │   ├── HomeScreen.swift
│   │   └── DashboardViewModel.swift
│   ├── Payments/
│   │   ├── PaymentsScreen.swift
│   │   ├── PaymentViewModel.swift
│   │   ├── PaymentReviewSheet.swift
│   │   └── PaymentSuccessScreen.swift
│   ├── History/
│   │   ├── HistoryScreen.swift
│   │   └── TransactionDetailScreen.swift
│   └── Profile/
│       └── ProfileScreen.swift
│
├── Domain/
│   ├── Models/
│   ├── UseCases/
│   └── Repositories/
│
├── Data/
│   └── InMemoryAccountRepository.swift
│
├── DesignSystem/
│   ├── NPayTheme.swift
│   ├── NPayButton.swift
│   └── NPayCard.swift
│
└── Tests/
├── DomainTests/
├── RepositoryTests/
├── UseCaseTests/
└── ViewModelTests/
```
This is the target organization. Moving code into folders alone does not create separate Swift modules.

## 4. End-to-end payment flow

Let's trace what happens when a user sends ₹1,500.50.

NPay runtime execution

Step 1 / 9

1. Enter details

PaymentsScreen binds recipient and amount to PaymentViewModel.

PreviousNext step

## 5. Behind the scenes — what happens at await?

Consider:
```swift
let record = try await sendPayment.execute(command)
```
This call crosses several boundaries.

The ViewModel is main-actor isolated.

The use case performs an asynchronous repository call.

The repository actor protects its mutable account state.

When the repository operation completes, the ViewModel can resume and update its presentation state.

Important distinction

await marks a potential suspension point. It doesn't guarantee that a new thread is created.

Actor isolation controls access to protected state, while Swift's concurrency runtime schedules asynchronous tasks.

This is the foundation for our future networking and concurrency units.

## 6. Final architecture integration checklist

Unit 4 Capstone Verification

0 / 14

All four NPay tabs launch correctly

NavigationStack and typed routes work

Payment draft survives tab switching

Review sheet displays immutable payment details

ViewModel uses explicit submission states

SendPaymentUseCase applies payment policy

Repository atomically updates local demo state

Duplicate overlapping submissions are rejected

Success navigation occurs after sheet dismissal

Dashboard refreshes after a successful payment

History displays the new transaction

Appearance preferences work across tabs

VoiceOver labels and accessibility IDs are present

Domain, repository and ViewModel tests pass

## Part 2 — Architecture Review & Production Readiness

## 7. What have we improved since Unit 3?

| Unit 3 | Unit 4 |
|---|---|
| Shared NPayStore handles payment behavior | PaymentViewModel coordinates feature state |
| Store validates and records payments | Use case defines application workflow |
| In-memory store holds transactions | Repository abstracts account operations |
| Direct concrete dependencies | Constructor injection and protocols |
| UI-driven error handling | Explicit state-machine modeling |
| Mostly manual verification | Unit and integration tests |
| Large app target | Feature folders and optional modules |

The visible interface may look almost identical.

But the internal design is significantly easier to test and extend.

## 8. Architecture risks still remaining

Even with MVVM and Clean Architecture, our demo application has limitations.

No real backend

Payments are simulated in memory.

No durable persistence

Account state is lost when the repository instance is destroyed.

No authentication

The demo has no verified user identity.

No server-enforced idempotency

The local submission guard doesn't prevent distributed duplicates.

No authoritative status reconciliation

Unknown remote payment outcomes aren't implemented yet.

These are exactly the concerns we'll address in later units.

## 9. Senior engineer architecture review

*(The text breaks here; Section 13 continues below.)*

---

Unit 4 · Lesson 4.10 — Final Part: Architecture Assessment & Unit Completion

NPay iOS Engineering Masterclass · Continuing from Section 9

We've completed the NPay MVVM architecture walkthrough, including presentation, domain, repositories, dependency injection, and the end-to-end payment flow.

Now we'll finish the final architecture assessment, review the complete learning journey, and establish what must be verified before Unit 5.

## 9. Senior engineer architecture review

Unit 4 — Final Engineering Assessment

*(Interactive quiz in the original.)*

**1. Which component should own SwiftUI layout?**

PaymentsScreen

SendPaymentUseCase

AccountRepository

**2. Which component should enforce application-level payment policy?**

PaymentViewModel

SendPaymentUseCase / PaymentPolicy

NPayRouter

**3. Why should AccountRepository be an abstraction?**

To separate application logic from storage details

To generate animations

To replace all tests

**4. What protects the in-memory balance update from interleaving?**

Actor-isolated non-suspending operation

TextField validation

TabView

**5. Does actor isolation automatically provide backend idempotency?**

Yes

No

**6. What should happen after a confirmed payment but failed dashboard refresh?**

Treat payment as failed

Preserve success and report refresh failure separately

Submit payment again

**7. Which component should manage navigation paths?**

NPayRouter

AccountRepository

PaymentPolicy

**8. Why use an immutable payment command for confirmation?**

To submit exactly what the user reviewed

To improve rendering speed

To eliminate all concurrency issues

**9. What does dependency injection improve?**

Replaceability and testability

Automatic database persistence

Automatic payment security

**10. Can a domain module depend on SwiftUI?**

It should generally remain independent

It must always import SwiftUI

Only when using NavigationStack

Submit assessment

## 10. Unit 4 — Complete learning summary

We've covered all ten lessons.

| Lesson | Topic | Main NPay concept |
|---|---|---|
| 4.1 | Architecture fundamentals | Separation of concerns |
| 4.2 | MVVM | PaymentViewModel |
| 4.3 | Observation | @Observable, @Bindable |
| 4.4 | Dependency injection | Protocol-based services |
| 4.5 | Repository pattern | Actor-isolated account data |
| 4.6 | Domain models and use cases | SendPaymentUseCase |
| 4.7 | UI state modeling | Explicit payment lifecycle |
| 4.8 | Modular architecture | Feature folders and Swift packages |
| 4.9 | Architecture testing | Unit, async, integration tests |
| 4.10 | Final integration | End-to-end MVVM architecture |

Unit 4 conceptual progress

100%

All 10 lessons covered. Complete Xcode source integration and build verification remain outstanding.

## 11. What should the final NPay application demonstrate?

Expected end-to-end payment scenario

Initial demo balance

₹25,000.00

Payment to ravi@npay

−₹1,500.50

Expected balance

₹23,499.50

The balance and transaction history must be derived from the same repository state.

Final integration verification

NPay Unit 4 acceptance checklist

0 / 10

App launches with Home, Payments, History, and Profile tabs

Payment form binds to PaymentViewModel

Payment review preserves an immutable command

SendPaymentUseCase enforces demo payment policy

Repository updates balance and transaction history

Submission state moves to success or failure correctly

Success navigation occurs after sheet dismissal

Dashboard and History refresh from the shared repository

Appearance, accessibility, and adaptive layouts still work

Unit and integration tests pass in Xcode

## 12. What's next in our NPay roadmap?

Unit 5 — Networking & REST API Integration

We'll introduce URLSession, HTTP, Codable, async/await, API error handling, and repository-backed networking.

Unit 6 — Persistence & Offline Data

We'll introduce SwiftData, local storage, caching, and data synchronization.

Units 7–12 — Production Engineering

Authentication, security, advanced concurrency, automated testing, debugging, performance, UIKit integration, CI/CD, distribution, and the final capstone.

Unit 4 is conceptually complete. Before introducing real networking, the remaining practical milestone is to consolidate the Unit 3 and Unit 4 code into one runnable Xcode project and verify its tests.

Our next lesson is Unit 5 · Lesson 5.1 — How iOS Networking Works Behind the Scenes, where we'll follow a request from URLSession through HTTP, DNS, TLS, the network stack, and back into NPay's ViewModel.

## Integration through Lesson 4.10 (authored)

The text names the consolidated project and its tests as "still outstanding". Here it is built and verified in
`tools/sim4_10/`, the 4.9 layout plus one change: **one source of truth**.
- `App/NPayDependencies.swift` creates one `InMemoryAccountRepository` (NPayData) and builds `DashboardViewModel` and
  `PaymentViewModel` from it. This is the shape from Lesson 4.5, section 17.
- `Features/Home/DashboardViewModel.swift` is 4.5's ViewModel moved into the app. It adds `reload()` and
  `refreshFailed`, so a failed refresh never turns a confirmed payment into a failure (the text's assessment,
  question 6), and `displayTransactions` for the existing rows.
- Home, History, AccountDetails and transaction details read the dashboard. Payments writes through the use case to
  the same repository and awaits `dashboard.reload()` after success. NPayRootView owns `NPayDependencies` and the
  dashboard, and loads the first snapshot in `.task`.
- NPayStore and the 4.6 `NPayStoreAccountRepository` adapter are deleted.
- NPayData's `InMemoryAccountRepository.init` gains an optional `transactions:` parameter (defaulting to empty, so
  every earlier call compiles), used to keep Unit 3's demo history. The Salary Credit row is dropped, because the
  repository records outgoing payments only. History rows read "Sent to …".

```swift
// App/NPayDependencies.swift
import SwiftUI
import NPayDomain
import NPayData

// Lesson 4.10 (section 3; 4.5's NPayDependencies): one repository for the whole app; Home, History and Payments all
// read and write the same account state through it.
@MainActor
final class NPayDependencies {

    let repository: any AccountRepository

    init() {
        repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000,
            transactions: NPayDependencies.demoHistory
        )
    }

    // Unit 3's two demo payments (ours: the repository models outgoing payments only)
    static let demoHistory = [
        PaymentRecord(id: UUID(), recipient: "Coffee Shop", amountPaise: 25_000, createdAt: .now),
        PaymentRecord(id: UUID(), recipient: "Electricity Bill", amountPaise: 120_000, createdAt: .now)
    ]

    func makeDashboardViewModel() -> DashboardViewModel {
        DashboardViewModel(repository: repository)
    }

    func makePaymentViewModel(
        availableBalance: @escaping @MainActor () -> Int
    ) -> PaymentViewModel {
        NPayFactory.makePaymentViewModel(
            repository: repository,
            availableBalance: availableBalance
        )
    }
}

// Features/Home/DashboardViewModel.swift
import SwiftUI
import NPayDomain

// Lesson 4.5, section 11 (moved into the app in 4.10): presentation state derived from the repository
@MainActor
@Observable
final class DashboardViewModel {

    private let repository: any AccountRepository

    var balancePaise = 0
    var transactions: [PaymentRecord] = []
    var refreshFailed = false   // Lesson 4.10 (ours): reported separately from any payment result

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func refresh() async throws {
        let snapshot = try await repository.fetchSnapshot()

        balancePaise = snapshot.balancePaise
        transactions = snapshot.transactions
    }

    // Lesson 4.10 (ours): a failed refresh never turns a confirmed payment into a failure
    func reload() async {
        do {
            try await refresh()
            refreshFailed = false
        } catch {
            refreshFailed = true
        }
    }

    // The existing rows and screens display Transaction values
    var displayTransactions: [Transaction] {
        transactions.map {
            Transaction(id: $0.id, title: "Sent to \($0.recipient)", amountPaise: -$0.amountPaise, date: $0.createdAt)
        }
    }
}
```

## Deck changes

The text came in three pieces: Part 1 (sections 1–6), Part 2 (7–9, breaking inside 9), and a final part (9–12).

The deck (`index.html`, built by `tools/gen4_10.py`, 37 slides) has 6 Parts:
1. The final architecture (sections 1, 2, 3).
2. One source of truth (the integration; sections 2 and 11, question 6).
3. One payment, end to end (4, 5).
4. Verification (6, 11).
5. Architecture review (7, 8).
6. Unit 4 complete (10, 12).

Then recap, review, next, lab and end.

**Evidence** (`sh tools/sim4_10/run.sh`, `sh tools/sim4_10/test.sh`)
- Trace:
  - At launch the repository and the dashboard both hold 2,500,000 and 2 payments.
  - Typing changes only the form. The sheet shows ravi@npay and ₹1,500.50.
  - After Confirm: repository 2,349,950 paise and 3 payments, sheet dismissed, paymentsPath 1, Payment Recorded.
  - Dashboard 2,349,950, 3; Home ₹23,499.50.
- Checklist (section 6, 14 items): all pass.
  - Tabs, typed routes (Home → account details, History → transaction details), the draft across tabs, the sheet
    details.
  - The submitting state with 3 s latency (debug hook).
  - Two Confirm activations → 1 payment. Success after dismissal. Dashboard = repository.
  - History's first row "Sent to ravi@npay". Dark in all four tabs. Four accessibility IDs, no unlabelled fields.
  - Policy and atomicity are covered by tests.
- Tests:
  - NPayCore: XCTest 3; Swift Testing 12; coverage 92.23%.
  - NPayAppTests: 6 Swift Testing tests, including our two DashboardViewModel tests (snapshot until reload; a failed
    refresh keeps the snapshot and sets `refreshFailed`).
- Screenshots: Home before and after, the review sheet, History after.

**Authored (flagged)**
- The one-repository integration, `reload()` / `refreshFailed`, the NPayData seed parameter, the deletions, the
  dashboard tests and every run.
- Section 4's trace (only step 1 of 9 was shared).
- Diagrams for sections 2 and 8.
- The "measured along the way" figures from earlier lessons.
- Review: the text's 10 questions (options reordered) plus a spaced item from 4.9. 1 of 11 verdicts is "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab, end slide (next: Unit 5 · Lesson 5.1, from the text).

**Snippets:** `NPayDependencies` and `DashboardViewModel` are the app's compiled code. The `reload` excerpt on the
slide is condensed.

**Wording**
- "Senior engineer architecture review" became "Check your understanding".
