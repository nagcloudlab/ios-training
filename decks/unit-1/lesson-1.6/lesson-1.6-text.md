# Unit 1 · Lesson 1.6 — Swift Protocols, Extensions & Protocol-Oriented Programming

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. The text as shared **ends after Section 13**
> (no knowledge check or closing section). Corrections and authored additions are listed at the end under "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

In Lesson 1.5, we learned the difference between structs and classes.

Now let's solve a new architectural problem.

How can different Swift types provide the same capability without inheriting from the same parent class?

This is where Swift's protocol-oriented programming becomes powerful.

We'll continue with PocketBank and learn how protocols help us build flexible, testable iOS applications.

## 1. The problem — multiple payment methods

Imagine PocketBank supports three payment methods:
- UPI
- Credit card
- Bank transfer

Each payment method behaves differently, but all must support a common operation: making a payment.

(PocketBank Payment Screen: UPI / Card / Bank → Common capability: Pay. Different implementations, same contract.)

The challenge is to define a common contract without forcing every payment method into one class hierarchy.

## 2. What is a protocol?

A protocol defines requirements that conforming types must satisfy.

Think of it as a contract.

For example:

```swift
protocol PaymentMethod {
    func pay(amount: Int)
}
```

This protocol says: any type conforming to PaymentMethod must provide a pay(amount:) operation.

It does not specify how payment processing works.

That responsibility belongs to each conforming type.

**Trainer analogy.** Think of a USB interface. Different devices can provide the same interface while implementing very different internal behavior. A protocol similarly defines a common programming interface without requiring identical implementations.

## 3. Implementing a protocol

Let's create a UPI payment type.

```swift
struct UPIPayment: PaymentMethod {

    func pay(amount: Int) {
        print("UPI payment: ₹\(amount)")
    }
}
```

Now a card payment type:

```swift
struct CardPayment: PaymentMethod {

    func pay(amount: Int) {
        print("Card payment: ₹\(amount)")
    }
}
```

Both types satisfy the same contract.

(PaymentMethod protocol: pay(amount: Int) ← UPIPayment, CardPayment)

Important: Protocol conformance does not imply class inheritance.

Both structs can conform to the same protocol.

## 4. Polymorphism through protocols

Now imagine a payment-processing function.

We don't want to write separate processing logic for every payment type.

```swift
func processPayment(
    using method: any PaymentMethod,
    amount: Int
) {
    method.pay(amount: amount)
}

processPayment(
    using: UPIPayment(),
    amount: 1000
)

processPayment(
    using: CardPayment(),
    amount: 2000
)
```

The function accepts any value conforming to PaymentMethod.

This is polymorphism: different concrete implementations can be used through a common interface.

(Protocol polymorphism simulator: UPIPayment / CardPayment / BankTransferPayment, amount ₹1,000, Call processPayment(). Simulation of method dispatch only. No real payment is processed.)

**Trainer insight.** The caller depends on a protocol contract rather than a specific payment implementation. This reduces coupling and makes code easier to extend and test.

## 5. Protocols can require properties

Protocols are not limited to functions.

They can also require properties.

```swift
protocol BankAccount {
    var accountNumber: String { get }
    var balance: Int { get set }
}
```

Here:
- { get } means the property must be readable.
- { get set } means the property must be readable and writable.

A conforming type must satisfy these requirements.

```swift
struct SavingsAccount: BankAccount {
    let accountNumber: String
    var balance: Int
}
```

A read-only property requirement can be satisfied by a property that also supports writing, but a read-write requirement needs appropriate mutability.

## 6. Protocols versus class inheritance

Let's compare two design approaches.

- **Class inheritance** — BasePayment → UPIPayment. Shares behavior and implementation through a class hierarchy.
- **Protocol conformance** — PaymentMethod → UPIPayment. Defines a shared capability without requiring inheritance.

| Feature | Protocol | Class inheritance |
|---|---|---|
| Structs can participate | Yes | No |
| Classes can participate | Yes | Yes |
| Multiple relationships | Multiple protocols | One superclass |
| Defines requirements | Yes | Through base class design |
| Shares implementation | Protocol extensions | Inherited methods and properties |
| Main purpose | Abstraction and capabilities | Shared identity, behavior and specialization |

Swift classes support single class inheritance but can conform to multiple protocols.

## 7. Protocol extensions — shared behavior

Now imagine every payment method needs a common logging function.

Instead of implementing it repeatedly, we can add a protocol extension.

```swift
protocol PaymentMethod {
    func pay(amount: Int)
}

extension PaymentMethod {
    func logPayment(amount: Int) {
        print("Payment initiated: ₹\(amount)")
    }
}
```

Now conforming types can use the extension method.

```swift
struct UPIPayment: PaymentMethod {
    func pay(amount: Int) {
        logPayment(amount: amount)
        print("Processing UPI payment")
    }
}
```

**Why is this powerful?** Protocols define capabilities. Extensions can provide shared behavior. This supports composition without requiring a deep class hierarchy.

## 8. Default protocol implementations

A protocol extension can also provide a default implementation of a protocol requirement.

```swift
protocol PaymentMethod {
    func validate(amount: Int) -> Bool
}

extension PaymentMethod {
    func validate(amount: Int) -> Bool {
        amount > 0
    }
}

struct UPIPayment: PaymentMethod {
}
```

UPIPayment satisfies the requirement through the default implementation.

### Important dispatch nuance

A method declared as a protocol requirement and implemented through an extension can participate in protocol witness dispatch.

A method defined only in a protocol extension, without being declared as a requirement, has different dispatch behavior when called through a protocol-typed value.

This is an advanced Swift concept worth demonstrating later because it can surprise developers coming from Java.

## 9. What is an extension?

An extension adds functionality to an existing type.

For example, suppose we want an Int helper for formatting a fictional amount in rupees.

```swift
extension Int {
    var rupeesText: String {
        "₹\(self)"
    }
}

let amount = 500

print(amount.rupeesText) // ₹500
```

Extensions can add computed properties, methods, initializers in supported contexts, protocol conformances, and more.

They cannot generally add new stored properties to an existing struct or class.

**Trainer question.** Can we extend a type whose original source code we don't own? Yes. Swift extensions can add functionality to accessible types, subject to language rules and access restrictions.

## 10. Protocol composition

Suppose PocketBank requires a service that can both process payments and generate receipts.

We can define two protocols.

```swift
protocol PaymentProcessing {
    func process(amount: Int)
}

protocol ReceiptGenerating {
    func generateReceipt() -> String
}
```

Now we can require both capabilities:

```swift
func completePayment(
    using service: any PaymentProcessing & ReceiptGenerating,
    amount: Int
) {
    service.process(amount: amount)
    print(service.generateReceipt())
}
```

The & operator expresses protocol composition.

This lets us require multiple capabilities without inventing an unnecessary combined superclass.

## 11. any versus some — important modern Swift

You've seen this syntax: `any PaymentMethod`

Swift also supports: `some PaymentMethod`

These are not identical.

(Understand the difference — any / some. Opaque type: the underlying concrete type is hidden from the caller but remains a specific type determined by the implementation. In an opaque return type, all return paths must agree on the same underlying concrete type.)

Example using any:

```swift
var method: any PaymentMethod = UPIPayment()
method = CardPayment()
```

Example using some:

```swift
func defaultPayment() -> some PaymentMethod {
    UPIPayment()
}
```

The function promises to return a specific concrete type conforming to PaymentMethod, while hiding that type from the caller.

This distinction becomes especially important in SwiftUI, where you'll frequently see: `var body: some View`

## 12. Why SwiftUI uses protocols

Remember our SwiftUI application?

```swift
struct DashboardView: View {
    var body: some View {
        Text("PocketBank")
    }
}
```

View is a protocol.

DashboardView is a struct conforming to that protocol.

This is a direct application of protocol-oriented design.

SwiftUI builds interfaces by composing values that conform to View.

**Trainer connection.** Now participants can understand why SwiftUI uses: `struct DashboardView: View`, `var body: some View`, View modifiers, generic view composition. These are not arbitrary framework conventions. They build on Swift's protocol and generic type system.

## 13. Protocols and dependency injection

Let's connect protocols to application architecture.

Suppose PocketBank's ViewModel fetches account balances.

We don't want the ViewModel tightly coupled to a specific network service.

(BalanceViewModel → BalanceProviding protocol ← LiveBalanceService (Real API), MockBalanceService (Testing))

```swift
protocol BalanceProviding {
    func fetchBalance() async throws -> Int
}

struct MockBalanceService: BalanceProviding {
    func fetchBalance() async throws -> Int {
        25000
    }
}

@MainActor
final class BalanceViewModel {
    private let service: any BalanceProviding

    init(service: any BalanceProviding) {
        self.service = service
    }

    func loadBalance() async throws -> Int {
        try await service.fetchBalance()
    }
}
```

The ViewModel depends on the protocol, not the concrete implementation.

That makes it easier to replace the real networking service with a mock during testing.

*(text ends here as shared — no knowledge check or closing section)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_6.py`) follows this text, with these changes.

**Structure**
- The text's 13 sections are grouped into **8 Parts** (36 slides) (1–2 protocols; 3–4 conformance and polymorphism; 5 property requirements; 6 protocols vs inheritance; 7–8 protocol extensions, defaults and dispatch; 9 extensions; 10–11 composition, any and some; 12–13 SwiftUI and dependency injection). Kickers name the text section.
- The text ends after Section 13; the recap, review, "Where this goes next", lab and end slide are authored.

**Corrections and canon**
- **Section 13 code does not compile in Swift 6:** `sending 'self.service' risks causing data races`. Fixed by `protocol BalanceProviding: Sendable` (verified); the slide shows the error and points to Lesson 1.9.
- Section 13 uses the course names: `DashboardViewModel`, `BalanceService` (was `BalanceViewModel`, `LiveBalanceService`), and returns `Balance` (`balanceMinor`, ₹25,000) instead of `Int`, matching Lessons 0.8 and 1.1.
- Amounts are paise (`amountMinor: Int64`) throughout; the `Int` extension becomes `extension Int64 { var rupeesText }` (50,000 paise → "₹500"), with a note that real formatting belongs in the ViewModel.
- The USB analogy is dropped (the course keeps two analogies); "Trainer connection: now participants can understand…" became student-facing cards.

**Real evidence instead of simulations**
- The dispatch nuance (Section 8) is demonstrated: with `CardPayment` seen as `card` and as `any PaymentMethod`, the requirement `validate` calls the card's version both times (`false`), while the extension-only `label()` returns `"card"` vs `"payment"`.
- Protocol composition (Section 10) is made concrete: `UPIService` conforms to both protocols and is accepted (real output "UPI: ₹500 paid", "Receipt NP-R1"); `CashCounter` only takes payments and is rejected (`argument type 'CashCounter' does not conform to expected type 'ReceiptGenerating'`).
- Real compiler messages (Swift 6.3): `let` for a `{ get set }` requirement (does not conform), stored property in an extension, mixed return types from `some PaymentMethod`.
- The polymorphism simulator became real output ("UPI payment: ₹1000", "Card payment: ₹2000"); the any/some explorer became **two slides built on real output**: (1) `any` — a mixed `[any PaymentMethod]` array of a UPI and a card payment, each calling its own `pay` ("UPI ₹500", "Card ₹500"), and the same array written with `some` failing to compile (`conflicting arguments to generic parameter ('UPIPayment' vs. 'CardPayment')`); (2) `some` — a small `DashboardView` whose real `body` type, printed by running it, is `VStack<TupleView<(Text, Button<Text>)>>`, which `some View` lets you avoid writing; plus `defaultPayment() -> some PaymentMethod`.

**Authored additions (flagged)**
- Outcomes, "Where we are" (Unit 01 progress strip, bridge to 1.5), recap.
- Review: 8 questions (what a protocol defines, struct conformance, single inheritance, dispatch predict-the-output, stored properties in extensions, any vs some, `{ get set }` vs `let`, and a spaced item from 1.5: what `==` compares).
- "Where this goes next": 1.7, 1.9, 3.5, 4.5, 9.4.
- Swift command-line lab "NPay payment methods" (three conformers, a default `validate`, the card's ₹100 minimum, and moving `validate` out of the protocol to see the dispatch change — verified: the card then pays).
- End slide: "Next: Lesson 1.7 — Generics & Error Handling".
