# Unit 4 · Lesson 4.8 — Modular Project Structure & Feature-Based Architecture

NPay iOS Engineering Masterclass · Part 1 + Part 2 · Xcode Project Organization · Swift Modules · Access Control · Dependency Boundaries

In Lesson 4.7, we introduced a proper payment state machine using PaymentUIState, async/await, and MVVM.

Now our NPay application has grown considerably.

We have SwiftUI screens, ViewModels, domain models, use cases, repositories, dependency injection, routing, and shared components.

Our engineering question: How should we organize all this code so NPay can grow from a small application into a maintainable, multi-team iOS project?

We'll begin with simple Xcode folders, then understand real Swift modules, Swift Package Manager, access control, and dependency direction.

## Part 1 — Organizing NPay by Features

## 1. Our current problem

Imagine our project looks like this:
```text
NPay/
├── ContentView.swift
├── NPayStore.swift
├── PaymentViewModel.swift
├── PaymentService.swift
├── AccountRepository.swift
├── BalanceCard.swift
├── HistoryScreen.swift
├── PaymentReviewSheet.swift
├── SendPaymentUseCase.swift
├── PaymentPolicy.swift
├── NPayRouter.swift
└── ... 40 more Swift files
```
Everything is mixed together.

The compiler can still build it, but developers must spend more effort discovering which files belong to which feature.

Two common organization strategies

Layer-first

Views/

ViewModels/

Models/

Repositories/

Services/

Groups files by technical responsibility.

Feature-first

Features/Home/

Features/Payments/

Features/History/

Features/Profile/

Core/

Groups code by product capability.

For NPay, we'll use feature-first organization with internal architectural layers.

This is a practical compromise: each feature is easy to locate, while domain and infrastructure dependencies remain clearly separated.

## 2. Design the NPay project structure

Here's our target organization for Unit 4.
```text
NPay/
│
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
│   │
│   ├── Payments/
│   │   ├── PaymentsScreen.swift
│   │   ├── PaymentViewModel.swift
│   │   ├── PaymentReviewSheet.swift
│   │   └── PaymentSuccessScreen.swift
│   │
│   ├── History/
│   │   ├── HistoryScreen.swift
│   │   └── TransactionDetailScreen.swift
│   │
│   └── Profile/
│       ├── ProfileScreen.swift
│       └── AppearanceSettingsView.swift
│
├── Domain/
│   ├── Models/
│   │   ├── PaymentAmount.swift
│   │   ├── PaymentRecipient.swift
│   │   └── PaymentRecord.swift
│   │
│   ├── UseCases/
│   │   └── SendPaymentUseCase.swift
│   │
│   └── Repositories/
│       └── AccountRepository.swift
│
├── Data/
│   └── Repositories/
│       └── InMemoryAccountRepository.swift
│
├── DesignSystem/
│   ├── NPayTheme.swift
│   ├── NPayButton.swift
│   ├── NPayCard.swift
│   └── BalanceCard.swift
│
└── Resources/
├── Assets.xcassets
└── Localizable.xcstrings
```
Why this structure?

Features contains user-facing capabilities.

Domain contains business concepts and contracts.

Data contains concrete data-access implementations.

DesignSystem contains reusable visual components.

App assembles dependencies and coordinates application launch.

## 3. Does an Xcode folder create a Swift module?

No. This is an important distinction.

Moving files into folders or Xcode groups does not automatically create separate Swift modules.

All files belonging to the same application target generally compile into the same Swift module.

Folder organization versus module boundaries

Folders

Features/Payments

Domain/

Data/

Organization only

Modules

NPayDomain

NPayData

NPayApp

Compiler-enforced boundaries

Why does this matter?

Folders improve discoverability.

Modules can enforce access boundaries and explicit imports.

These solve related but different problems.

## 4. First Xcode lab — reorganize without changing behavior

Open the existing NPay project.

Create the folder structure above.

Move the existing Swift files into their appropriate locations.

For example:

```text
PaymentViewModel.swift → Features/Payments/PaymentViewModel.swift
SendPaymentUseCase.swift → Domain/UseCases/SendPaymentUseCase.swift
InMemoryAccountRepository.swift → Data/Repositories/InMemoryAccountRepository.swift
```

Important rule

Do not change the business logic while reorganizing files.

After each small move, build the application.

This keeps structural refactoring separate from behavioral changes.

Xcode detail

Depending on your Xcode version, folders may be represented as filesystem-synchronized groups or traditional project groups.

Check that the files remain included in the correct target.

If a Swift file is not part of the app target, the compiler won't make its declarations available to that target.

## 5. How does the Swift compiler see our files?

Suppose the app target contains:

PaymentViewModel.swift

SendPaymentUseCase.swift

AccountRepository.swift

Even though these are separate files, they belong to one module.

A type declared in one file can generally be referenced from another file in that module, subject to Swift access control.

For example:
```swift
struct PaymentAmount {
    let paise: Int
}
```
Another file in the same module can use PaymentAmount without importing the file individually.

Connect to Unit 1

Swift imports modules, not individual .swift files.

That's why we write:
```swift
import SwiftUI
import Foundation
```
rather than:
```swift
import PaymentAmount.swift
```

## 6. Swift access control — why modules matter

Swift provides access levels including:

- private

- fileprivate

- internal

- package

- public

- open

Let's examine the most relevant ones.

| Access level | Typical visibility |
|---|---|
| private | Enclosing declaration and permitted extensions |
| fileprivate | Same source file |
| internal | Same module (default) |
| package | Same Swift package |
| public | Other modules can use the declaration |
| open | Allows external subclassing/overriding for eligible classes and members |

Example

public struct PaymentAmount {

public let paise: Int

}

This makes the type and property visible to importing modules.

But a public type doesn't automatically expose every initializer or member.

We must explicitly design its public API.

## 7. Behind the scenes — module compilation

Simplified Swift module build flow

Swift source files

Types, protocols, extensions, functions

Swift compiler

Parses and type-checks the module

Module interface / metadata

Exposes relevant declarations to importers

Compiled implementation

Produces code for linking

Application linking

Combines required modules and resources

Conceptual build pipeline. Exact compilation, module emission, optimization, and linking steps depend on build settings and target configuration.

## Part 2 — Swift Packages, Dependency Direction & Modular Architecture

## 8. Introduce Swift Package Manager

Swift Package Manager, or SPM, is Swift's package and dependency management system.

It can organize reusable code into targets and products.

For NPay, we might eventually extract:

NPayDomain

NPayData

NPayDesignSystem

into separate package targets.

Why?

To make dependencies explicit.

For example, NPayDomain shouldn't need to import SwiftUI.

NPayData may depend on NPayDomain.

The app depends on both.

## 9. Our target module dependency graph

NPay module relationships

NPayApp

SwiftUI screens, ViewModels, composition root

NPayData

Repository implementations

NPayDesignSystem

Reusable UI components

NPayDomain

Models, use cases, repository contracts

NPayData depends on NPayDomain; the design system can remain independent of the domain for general-purpose components. The app composes them.

Important architectural rule

Dependencies should not form cycles.

For example:

NPayDomain → NPayData → NPayDomain

would be an undesirable circular dependency.

Instead, the repository protocol belongs in the domain-facing contract layer, and the data implementation depends on that protocol.

## 10. Create a local Swift package

In Xcode, create a local Swift package named NPayCore.

The package can contain two library targets:
```text
NPayCore/
├── Package.swift
├── Sources/
│   ├── NPayDomain/
│   │   ├── PaymentAmount.swift
│   │   ├── PaymentRecipient.swift
│   │   ├── SendPaymentUseCase.swift
│   │   └── AccountRepository.swift
│   │
│   └── NPayData/
│       └── InMemoryAccountRepository.swift
│
└── Tests/
└── NPayDomainTests/
```
Example Package.swift

```swift
// swift-tools-version: 5.9

import PackageDescription

let package = Package(
    name: "NPayCore",
    platforms: [
        .iOS(.v17)
    ],
    products: [
        .library(
            name: "NPayDomain",
            targets: ["NPayDomain"]
        ),
        .library(
            name: "NPayData",
            targets: ["NPayData"]
        )
    ],
    targets: [
        .target(
            name: "NPayDomain"
        ),
        .target(
            name: "NPayData",
            dependencies: ["NPayDomain"]
        ),
        .testTarget(
            name: "NPayDomainTests",
            dependencies: ["NPayDomain"]
        )
    ]
)
```
This is a valid starting manifest for the package structure. The source declarations must still be adjusted for cross-module visibility before the extracted application will compile.

## 11. Cross-module access control

Once PaymentAmount moves into NPayDomain, the app imports that module:
```swift
import NPayDomain
```
The domain type must be exposed appropriately.
```swift
import Foundation
```

public enum PaymentDomainError: Error {

case invalidAmount

}

public struct PaymentAmount: Equatable, Sendable {

public let paise: Int

public init(paise: Int) throws {

guard paise > 0 else {

throw PaymentDomainError.invalidAmount

}

self.paise = paise

}

}

Why explicitly declare public init?

Because a public struct's synthesized memberwise initializer is not automatically public.

If another module needs to create PaymentAmount, the public initializer must be provided.

This is a common issue when extracting code from one Xcode target into a package.

## 12. Importing NPayDomain into NPayData

Our data implementation now needs:
```swift
import NPayDomain
```
For example:

public actor InMemoryAccountRepository: AccountRepository {

// Implementation

}

To compile this across module boundaries, AccountRepository, its required methods, relevant domain types, and the concrete repository's initializer must have suitable access levels.

The compiler enforces these boundaries.

Why is this useful?

A developer cannot accidentally access an internal implementation detail from another module.

Module boundaries turn architectural intentions into compiler-checkable constraints.

## 13. Why not create 20 Swift packages immediately?

Modularity has costs.

Every module introduces public API decisions, dependency management, build configuration, and integration overhead.

For a small application, too many modules can make development harder.

Practical NPay strategy

We'll evolve in stages.

| Stage | Architecture |
|---|---|
| Current | One Xcode app target, organized by features |
| Next | Extract stable domain code into NPayDomain |
| Later | Extract data implementations into NPayData |
| Larger application | Introduce feature modules where justified |

This keeps the learning incremental and avoids unnecessary complexity.

## 14. Feature modules versus shared modules

Suppose NPay eventually has several teams.

One team owns Payments.

Another owns History.

A third owns Profile.

Feature modules can help establish ownership boundaries.

But shared code should be extracted carefully.

Example

NPayDesignSystem may contain:

NPayButton

NPayCard

NPayTheme

But a payment-specific component such as PaymentReviewSheet should usually remain in the Payments feature.

Senior engineer principle

Don't move code into a shared module simply because two files use it.

Extract shared abstractions when they represent a stable, meaningful contract.

## 15. Xcode build dependencies

When NPayApp imports NPayDomain, Xcode must build the domain module before compiling dependent app code.

Swift Package Manager and Xcode use the declared target dependency graph to determine build relationships.

Simplified build order

*(The text breaks here; Section 13 continues below.)*

---

## Part 2 (continued): Build Dependencies, Modularization & Architecture Testing

NPay iOS Engineering Masterclass · Continuing from Section 15 · Final Part of Lesson 4.8

We've organized NPay into feature-based folders and introduced Swift modules, Swift Package Manager, and access control.

Now we'll complete Lesson 4.8 by understanding how Xcode builds multiple modules, how Swift enforces architectural boundaries, and how to migrate NPay safely.

## 15. Xcode build dependencies — continued

Suppose our NPay project contains three modules:

- NPayDomain — domain models, business rules, and repository protocols.

- NPayData — concrete repository implementations.

- NPayApp — SwiftUI screens, ViewModels, and application composition.

Xcode needs to respect the declared dependency relationships.

Simplified build dependency graph

NPayDomain

No dependency on NPayData or SwiftUI

NPayData

Imports NPayDomain

NPayApp

Imports NPayDomain and NPayData

Logical dependency ordering. Independent targets can be built concurrently; this is not a guarantee of strictly sequential compilation.

What happens when we build?

1. Swift Package Manager resolves the package dependency graph.

2. Xcode determines which targets require compilation.

3. Swift compiles source files into their respective modules.

4. The application target compiles against the imported module interfaces.

5. The linker and build system assemble the application and its required resources.

Important distinction

A Swift module is a compilation and visibility boundary.

It isn't automatically a separate process, container, or microservice.

## 16. Why dependency direction matters

Consider this architecture:

NPayApp → NPayData → NPayDomain

That is acceptable when the application composes the concrete data implementation and the domain contracts.

But this would be problematic:

NPayDomain → NPayData

NPayData → NPayDomain

It creates a circular module dependency.

Swift Package Manager requires an acyclic target dependency graph.

How do we avoid it?

The repository protocol belongs in NPayDomain.

The implementation belongs in NPayData.

The application creates the implementation and supplies it to the use case.

Dependency inversion across modules

NPayDomain

AccountRepository protocol

NPayData

InMemoryAccountRepository conforms to the protocol

NPayApp

Composition root constructs dependencies

The domain remains independent of infrastructure.

That's the central architectural boundary.

## 17. Complete NPayDomain public contract

Let's build a small, compile-ready domain module example.

Create Sources/NPayDomain/AccountRepository.swift.
```swift
import Foundation
```

public struct PaymentRecord: Identifiable, Sendable {

public let id: UUID

public let recipient: String

public let amountPaise: Int

public let createdAt: Date

public init(

id: UUID,

recipient: String,

amountPaise: Int,

createdAt: Date

) {

self.id = id

self.recipient = recipient

self.amountPaise = amountPaise

self.createdAt = createdAt

}

}

public struct AccountSnapshot: Sendable {

public let balancePaise: Int

public let transactions: [PaymentRecord]

public init(

balancePaise: Int,

transactions: [PaymentRecord]

) {

self.balancePaise = balancePaise

self.transactions = transactions

}

}

public enum AccountRepositoryError: Error {

case invalidRecipient

case invalidAmount

case insufficientBalance

}

public protocol AccountRepository: Sendable {

func fetchSnapshot() async throws -> AccountSnapshot

func recordPayment(

recipient: String,

amountPaise: Int

) async throws -> PaymentRecord

}

What changed from Lesson 4.5?

We added public to the types and requirements intended for use across module boundaries.

We also provided explicit public initializers.

Without those, declarations might be inaccessible to the importing module.

## 18. Complete NPayData repository implementation

Create Sources/NPayData/InMemoryAccountRepository.swift.
```swift
import Foundation
import NPayDomain
```

public actor InMemoryAccountRepository: AccountRepository {

private var balancePaise: Int

private var transactions: [PaymentRecord] = []

public init(initialBalancePaise: Int = 2_500_000) {

self.balancePaise = initialBalancePaise

}

public func fetchSnapshot() async throws -> AccountSnapshot {

AccountSnapshot(

balancePaise: balancePaise,

transactions: transactions

)

}

public func recordPayment(

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

let record = PaymentRecord(

id: UUID(),

recipient: trimmed,

amountPaise: amountPaise,

createdAt: .now

)

balancePaise -= amountPaise

transactions.insert(record, at: 0)

return record

}

}

Important engineering detail

NPayData imports NPayDomain.

But NPayDomain does not import NPayData.

This is how we enforce the intended dependency direction.

## 19. Build the application composition root

Inside the NPay application target:
```swift
import SwiftUI
import NPayDomain
import NPayData

@MainActor
final class NPayDependencies {

    let repository: any AccountRepository

    init() {
        repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000
        )
    }
}
```
Now the application knows about both the domain abstraction and the concrete data implementation.

The domain doesn't know which repository implementation the application selected.

Why is this important?

Later, we can replace:

InMemoryAccountRepository()

with an API-backed implementation.

The domain-facing repository contract can remain unchanged if it still accurately represents the required behavior.

## 20. Test the module boundaries

Now let's deliberately introduce an architectural violation.

Inside NPayDomain, try:
```swift
import NPayData
```
What happens?

If NPayDomain doesn't declare a dependency on NPayData, the module won't be available to import in a correctly isolated package build.

This is useful.

The compiler and package dependency graph can help prevent forbidden architectural dependencies.

Another experiment

Remove public from:

public struct PaymentRecord

Then try to use PaymentRecord from NPayApp.

The compiler will report an access-control problem.

This demonstrates that module boundaries are enforceable rather than merely documented.

## 21. Should every NPay feature become a module?

No.

Let's compare two possible approaches.

Choose a modularization strategy

Small appGrowing appMulti-team app

Single app target

Organize by feature folders and keep the build simple.

Best when the codebase is manageable and module boundaries offer limited additional value.

Senior engineer principle

Modularization should solve a real maintenance, ownership, dependency, or build problem.

More modules don't automatically mean better architecture.

## 22. Migration strategy — don't break NPay

We have an existing SwiftUI application with many lessons of incremental functionality.

A safe migration plan is:

| Step | Action | Verification |
|---|---|---|
| 1 | Reorganize Swift files into feature folders | App builds |
| 2 | Extract domain models | Domain target builds |
| 3 | Extract repository protocol | App imports NPayDomain |
| 4 | Extract in-memory repository | NPayData builds |
| 5 | Update composition root | Shared repository instance |
| 6 | Run payment integration test | Balance and history correct |
| 7 | Verify all four tabs | No navigation regression |

Important warning

Don't simultaneously rename every type, move every file, rewrite navigation, and change the payment workflow.

Make one architectural change at a time.

Build and test after each step.

## 23. NPay module verification lab

Lesson 4.8 integration checklist

*(Interactive checklist in the original.)*

Create NPayCore local Swift package

Add NPayDomain target

Add NPayData target

Declare NPayData dependency on NPayDomain

Move PaymentRecord and AccountRepository into NPayDomain

Expose required public initializers and types

Move InMemoryAccountRepository into NPayData

Import both modules from NPayApp

Create one repository in the composition root

Verify a demo payment updates balance and history

Check no circular module dependencies

Run the application on the iOS Simulator

## 24. Senior engineer knowledge check

Modular Architecture Assessment

*(Interactive quiz in the original.)*

**1. Does moving a Swift file into an Xcode folder create a new module?**

Yes

No

**2. What does internal mean in Swift?**

Visible within the same module

Visible only in one function

Visible to every module

**3. Why must NPayData import NPayDomain?**

It uses domain models and repository contracts

It needs SwiftUI previews

It creates navigation routes

**4. Should NPayDomain import NPayData?**

Yes

No

**5. Does a public Swift struct automatically have a public memberwise initializer?**

Yes

No

**6. Can Swift Package Manager targets have circular dependencies?**

Yes

No

**7. Should every small feature automatically become a separate package?**

Yes

No

Lesson 4.8 — Completed

We've now covered both parts of modular project architecture: feature-based organization, Xcode targets, Swift modules, access control, Swift Package Manager, dependency graphs, and safe migration.

Unit 4 progress

8 / 10 lessons

80% conceptually complete. Full Xcode integration still requires verification.

Next — Lesson 4.9: Architecture Testing. We'll write proper Swift tests for NPay's domain models, use cases, repositories, and ViewModels, using XCTest and Swift Testing, mocks, async tests, and dependency injection.

After that, Lesson 4.10 will consolidate Unit 4 into a complete MVVM-based NPay application.

## Integration through Lesson 4.8 (authored)

The lesson's lab, done for real in `tools/sim4_8/`:
- **`NPayCore/`** is the text's package. `Package.swift` follows section 10 plus `.macOS(.v14)` (ours; without it,
  `swift build` and `swift test` fail on the Mac because `.now` needs macOS 12).
  - `NPayDomain`: `PaymentAmount.swift`, `PaymentRecipient.swift`, `SendPaymentUseCase.swift` (with `SendPaymentCommand`
    and `PaymentPolicy`), `AccountRepository.swift` (section 17, verbatim).
  - `NPayData`: `InMemoryAccountRepository.swift` (section 18, verbatim).
  - `Tests/NPayDomainTests`: two Swift Testing tests (ours).
  - Ours: the public versions of `PaymentRecipient`, `SendPaymentCommand`, `PaymentPolicy`, `SendPaymentUseCase`, and
    the full `PaymentDomainError` (section 11 shows only `invalidAmount`). `SendPaymentUseCase` keeps 4.7's error
    mapping.
- **`NPay/`** is the app's code split into the section 2 folders (31 files):
  - App, Features/{Home, Payments, History, Profile}, Domain (the app's own Money, Transaction, PaymentValidator),
    Data (NPayStore and the NPayStoreAccountRepository adapter), DesignSystem.
  - The domain types now come from `import NPayDomain`.
  - Lesson 4.4's unused PaymentService, DemoPaymentService and MockPaymentService were removed (unused since 4.6).
- **`Lab/`** holds the evidence driver and its helpers.
- **`run.sh`** cross-builds NPayCore for the iOS Simulator with SwiftPM, compiles every app file against its modules,
  and links the package objects.
- **`violations.sh`** builds four broken copies of the package (section 20).

## Deck changes

The text came in three pieces: Part 1 (sections 1–7), Part 2 (8–15, breaking inside 15), and a continuation (15–24).

The deck (`index.html`, built by `tools/gen4_8.py`, 35 slides) has 7 Parts:
1. Organizing by feature (sections 1, 2).
2. Folders are not modules (3, 4, 5).
3. Access control and modules (6, 7).
4. A Swift package (8, 9, 10, 15).
5. Crossing the boundary (11, 12, 17, 18).
6. Dependency direction (16, 19, 20).
7. How far to modularize (13, 14, 21, 22, 23).

Then recap, review, next, lab and end.

**Evidence**
- Before: 1 file, 1,543 lines of app code (4.7's evidence app). After: 31 files in 10 folders.
- `String(reflecting:)` in the running app: NPay.PaymentsScreen, NPay.NPayStore, NPay.Money, NPayDomain.PaymentAmount,
  NPayDomain.SendPaymentUseCase, NPayData.InMemoryAccountRepository.
- `swift build` (Mac) with the text's manifest fails on `.now`. With `.macOS(.v14)`: NPayDomain compiles, then NPayData,
  "Build complete!"; `swift test` passes 2 tests. The iOS Simulator cross-build succeeds.
- `violations.sh`:
  - No public init on PaymentRecord → NPayData: "'PaymentRecord' initializer is inaccessible due to 'internal'
    protection level".
  - PaymentRecord not public → NPayDomain itself: "property / initializer / method cannot be declared public because
    its type uses an internal type". The text expected the error in the app.
  - `import NPayData` in NPayDomain → "no such module 'NPayData'".
  - A declared cycle → "cyclic dependency declaration found: NPayData -> NPayDomain -> NPayData".
- From the app: an NPayDomain use case on an NPayData repository recorded 150050, balance 2349950.
- The reorganized NPay in the simulator: a payment ends at 2,349,950 paise and 4 transactions. All four tabs open
  (NPay with ₹23,499.50, Payments, History with "Sent to ravi@npay", Profile).

**Authored (flagged)**
- The package's extra public types, the macOS platform, the tests, the folder split, the deletion of the 4.4 services,
  the violation script and every run.
- Diagrams for sections 7 and 9; the migration table's "Verified" column.
- The section 21 strategy chooser, summarized.
- Review: the text's 7 questions (options reordered) plus three more:
  - two predict items (where the non-public error appears; the manifest on a Mac);
  - a spaced item from 4.7.
  - 5 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next", lab, end slide.

**Snippets:** the composition root (section 19) typechecks against the built package. The public `PaymentRecord` and
protocol compile. The manifest on the slide is condensed; the full file is `tools/sim4_8/NPayCore/Package.swift`.

**Wording**
- "Senior engineer principle / knowledge check" became neutral labels and "Check your understanding".
