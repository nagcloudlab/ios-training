# Unit 1 · Lesson 1.5 — Swift Structs vs Classes: Value & Reference Semantics

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. Corrections and authored additions are
> listed at the end under "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

In our previous lesson, we learned functions and closures. Now we'll explore one of Swift's most important design decisions:

When should we create a struct, and when should we create a class?

This question appears in almost every serious iOS application, particularly when designing models, SwiftUI state, ViewModels, and shared services.

We'll learn through one PocketBank story.

## 1. The problem — two account screens

Imagine PocketBank displays the same account information in two places:
- Dashboard — shows account balance.
- Transfer screen — allows the user to prepare a transfer.

Both screens initially display ₹25,000.

Now the transfer screen changes its local balance value to ₹20,000.

Should the dashboard balance also change?

The answer depends on how we model and share the data.

(Two screens, one account — Struct / Class toggle. Dashboard balance ₹25,000; Transfer screen balance ₹25,000. "Modify transfer-screen balance −₹5,000": the two screens hold independent struct values; modifying one copy does not change the other. Reset. Conceptual Swift semantics simulation, not a real banking transaction or SwiftUI synchronization implementation.)

This leads to two fundamental concepts:

Value semantics — independent logical values.

Reference semantics — shared object identity.

## 2. Struct — value semantics

Consider:

```swift
struct Account {
    var balance: Int
}

var accountA = Account(balance: 25000)
var accountB = accountA

accountB.balance = 20000

print(accountA.balance) // 25000
print(accountB.balance) // 20000
```

When we assign accountA to accountB, we get an independent logical value.

(Original struct value — ₹25,000 → Assignment: accountB = accountA → accountA ₹25,000, accountB ₹20,000)

### Important nuance

Value semantics does not necessarily mean Swift immediately duplicates every byte of storage.

Swift can optimize value copying, including through copy-on-write techniques.

The guarantee is that changes to one logical value do not unexpectedly mutate another independent value.

## 3. Class — reference semantics

Now change struct to class.

```swift
class Account {
    var balance: Int

    init(balance: Int) {
        self.balance = balance
    }
}

let accountA = Account(balance: 25000)
let accountB = accountA

accountB.balance = 20000

print(accountA.balance) // 20000
print(accountB.balance) // 20000
```

Here, both variables reference the same object.

(accountA, accountB → One Account instance ₹20,000)

**Trainer question.** Why can we modify accountB.balance even though accountB is declared with let?

Because let prevents reassigning the reference. It does not necessarily make the referenced class instance immutable.

## 4. Struct versus class — complete comparison

| Feature | Struct | Class |
|---|---|---|
| Semantics | Value | Reference |
| Identity | No class-style identity | Object identity |
| Inheritance | No class inheritance | Supports inheritance |
| ARC | Not directly ARC-managed as a class instance | Class instance managed by ARC |
| Deinitializer | No deinit | Supports deinit |
| Mutating methods | Require mutating | No mutating keyword |
| Default memberwise initializer | Generally synthesized | Not automatically synthesized in the same way |
| Typical use | Data models and values | Shared identity and reference-based services |

**Trainer warning:** Don't teach "struct = stack" and "class = heap" as a universal rule. Storage placement is an implementation detail, not the core language semantic distinction.

## 5. How does Swift handle struct mutation?

Structs are value types.

When an instance method changes the struct's stored properties, the method must be marked mutating.

```swift
struct Account {
    var balance: Int

    mutating func deposit(_ amount: Int) {
        balance += amount
    }
}

var account = Account(balance: 25000)
account.deposit(5000)

print(account.balance) // 30000
```

Without mutating, the method cannot modify balance.

**Why?** Because the method is changing the value represented by the struct instance. The mutating keyword makes that intent explicit.

## 6. What is an initializer?

A class generally requires explicit initialization for stored properties that don't have default values.

```swift
class Customer {
    let id: String
    var name: String

    init(id: String, name: String) {
        self.id = id
        self.name = name
    }
}
```

The init method establishes the initial state of the instance.

Structs often receive a synthesized memberwise initializer.

```swift
struct Customer {
    let id: String
    var name: String
}

let customer = Customer(
    id: "C1001",
    name: "Ravi"
)
```

We'll explore initialization rules, designated initializers, convenience initializers, and two-phase class initialization in a dedicated lesson.

## 7. Identity versus equality

Two class instances can contain the same data but still be different objects.

```swift
class Customer {
    let name: String

    init(name: String) {
        self.name = name
    }
}

let a = Customer(name: "Ravi")
let b = Customer(name: "Ravi")
let c = a

print(a === b) // false
print(a === c) // true
```

=== checks whether two class references identify the same instance.

It does not compare the values of their properties.

For value equality, types can conform to Equatable.

```swift
struct Customer: Equatable {
    let name: String
}

let a = Customer(name: "Ravi")
let b = Customer(name: "Ravi")

print(a == b) // true
```

## 8. Copy-on-write — an important Swift optimization

Swift collections such as Array use copy-on-write behavior.

Imagine:

```swift
var a = [10, 20, 30]
var b = a

b.append(40)

print(a) // [10, 20, 30]
print(b) // [10, 20, 30, 40]
```

The two arrays have value semantics.

But Swift can initially share their underlying storage and create separate storage when a mutation requires it.

(Copy-on-write visualization: Array A [10, 20, 30], Array B [10, 20, 30], potentially shared underlying storage. "Append 40 to Array B". Conceptual copy-on-write behavior; actual storage optimizations depend on implementation details.)

**Trainer insight.** Copy-on-write combines the programmer-facing simplicity of value semantics with opportunities for efficient storage reuse. This is one reason Swift encourages value types for many data models.

## 9. Classes and ARC

Classes introduce reference ownership.

```swift
class Customer {
    let name: String

    init(name: String) {
        self.name = name
        print("Created")
    }

    deinit {
        print("Destroyed")
    }
}

var customer: Customer? = Customer(name: "Ravi")
customer = nil
```

When the last strong reference to a class instance is released, ARC can deinitialize it.

But strong-reference cycles can prevent deinitialization.

We covered these in Lesson 0.6; now you can see why they are specifically relevant to reference types.

## 10. What about SwiftUI?

SwiftUI's View protocol is commonly implemented using structs.

```swift
import SwiftUI

struct BalanceView: View {
    let balance: Int

    var body: some View {
        Text("₹\(balance)")
    }
}
```

This does not mean SwiftUI copies and redraws the entire screen every time a struct value changes.

SwiftUI uses view values as descriptions of the desired interface and manages identity, state, and rendering internally.

### Important architecture distinction

A SwiftUI view struct can be recreated frequently.

But persistent view-associated state can be managed separately by SwiftUI.

That's why understanding view identity and property wrappers becomes essential in later lessons.

## 11. When should we choose a struct or class?

(Interactive design decision: Transaction record / Shared session manager / SwiftUI screen description / Observable ViewModel / Currency amount → e.g. "Prefer struct: A transaction record is naturally a value representing data.")

### Practical rule

Start with a struct when you need independent values. Choose a class when reference identity or shared ownership is genuinely part of the design.

This is a useful starting guideline, not an absolute law.

## 12. PocketBank domain model

Let's combine the concepts.

```swift
struct Money {
    let amountInPaise: Int64
    let currency: String
}

struct Transaction {
    let id: String
    let amount: Money
    let description: String
}

final class SessionManager {
    private(set) var isLoggedIn = false

    func login() {
        isLoggedIn = true
    }

    func logout() {
        isLoggedIn = false
    }
}
```

Why these choices?

Money and Transaction represent domain values.

SessionManager represents a service with shared identity and mutable session state.

A real banking implementation would require stronger domain validation and secure session handling.

## 13. Trainer-level knowledge check

1. Does assigning a class instance to another variable create a new instance?
2. Do structs guarantee independent logical values after assignment?
3. Does a let-bound class reference make every property immutable?
4. Does Swift Array use copy-on-write optimization?
5. Should every iOS model be a class?

*(text ends here as shared)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_5.py`) follows this text, with these changes.

**Structure**
- The text's 12 sections are grouped into **8 Parts** (1 two screens; 2–3 struct and class; 4 comparison; 5–6 mutating and init; 7 identity and equality; 8 copy-on-write; 9–10 ARC and SwiftUI; 11–12 choosing and the NPay model). Each slide's kicker names its text section.

**Corrections and canon**
- PocketBank → NPay. Amounts in whole paise (`balanceMinor: Int64`, 2,500,000 = ₹25,000), as in Lessons 1.2 and 1.4. Classes in examples are `final`.
- Comparison table: "No deinit" for structs now carries a footnote — non-copyable structs (`~Copyable`, Swift 5.9+) can have a `deinit` (verified); ownership is Lesson 1.8. "Not directly ARC-managed" keeps the nuance that class references *inside* a struct are still ARC-managed (notes).
- Copy-on-write is described as built into the standard collections (Array, Dictionary, Set, String); custom structs get it only if they implement it.
- `BalanceView` takes `balanceText` formatted by the ViewModel (Lesson 0.2) instead of interpolating `₹\(balance)`.
- Model: `Money.amountInPaise` → `amountMinor` (course naming); `Money` and `Transaction` are `Equatable`.

**Interactive / trainer material**
- The two-screens simulator became a stepped diagram (struct: only the transfer screen changes; class: both screens and the shared instance show ₹20,000).
- The copy-on-write visualizer became a stepped diagram plus a **measured** result: `withUnsafeBufferPointer` base addresses are equal before `b.append(40)` (true) and different after (false).
- The design-decision explorer became a table (5 NPay types → struct/class, with reasons).
- Trainer question (let class reference) → notes and review; trainer warning (stack/heap) → misconception callout.

**Authored additions (flagged)**
- Outcomes, "Where we are" (Unit 01 progress strip, bridge to 1.4), recap.
- Real compiler messages (Swift 6.3): a non-`mutating` method changing a property; a class with no initializers.
- Real outputs: `Created` / `Destroyed`; `a === b` false, `a === c` true; Equatable `==` true.
- Review: 8 questions — the text's 5 open questions (yes/no), a multiple-choice on which NPay type should be a class, predict `a === b, a === c`, and a spaced item from 1.4 (a closure sees a later change to a captured variable: prints 2).
- "Where this goes next": 1.6, 1.8, 1.10, 3.1, 3.2.
- Swift command-line lab "Model NPay's types" (copy a Transaction, share a SessionManager, observe deinit, measure copy-on-write).
- End slide: "Next: Lesson 1.6 — Protocols, Extensions & Protocol-Oriented Design".
