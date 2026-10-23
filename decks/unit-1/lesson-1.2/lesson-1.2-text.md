# Unit 1 · Lesson 1.2 — Swift Variables, Constants & Type System

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. Corrections and authored additions are
> listed at the end under "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

In Lesson 1.1, we understood how Swift code is compiled into native machine instructions.

Now let's start writing Swift.

But instead of simply memorizing syntax, we'll answer a deeper question:

How does Swift know what kind of data we're storing, whether that data can change, and which operations are safe?

We'll continue building our fictional PocketBank application.

## 1. Our first problem — storing a bank account

Imagine PocketBank needs to represent:
- Customer name: Ravi
- Account number: PB1001
- Account balance: ₹25,000
- Account active: Yes

In Swift:

```swift
let customerName = "Ravi"
let accountNumber = "PB1001"
var balance = 25000
var isActive = true

print(customerName)
print(balance)
```

Notice two keywords: let and var.

These are fundamental to Swift.

## 2. let versus var

let creates a binding that cannot be reassigned after initialization.

var creates a mutable variable.

- **let** — Cannot be reassigned after initialization. `let accountId = "PB1001"`
- **var** — Can be assigned a new compatible value. `var balance = 25000`

### Interactive experiment

Can we change the balance? (let / var toggle: `{kind} balance = 25000` → attempt `balance = 30000` → ₹30,000. "Valid: the variable can be reassigned." Simulated Swift assignment behavior.)

**Trainer insight.** Prefer let when reassignment is unnecessary. It communicates intent and prevents accidental changes.

But there's a subtle distinction: let does not always mean that an entire object is immutable.

We'll examine that later when comparing structs and classes.

## 3. What is type inference?

Look at this code:

```swift
let name = "Ravi"
let age = 30
let balance = 25000.50
let isActive = true
```

We haven't explicitly declared the types.

Yet Swift knows them.

Why?

Because the compiler examines the expressions used to initialize the variables.

| Literal | Inferred type |
|---|---|
| "Ravi" | String |
| 30 | Int |
| 25000.50 | Double |
| true | Bool |

### Important concept

Swift supports static typing with type inference.

That means the compiler determines types during compilation. It does not mean a variable can freely change types at runtime.

```swift
var balance = 25000

balance = 30000       // Valid
// balance = "30000"   // Compiler error
```

## 4. Swift's fundamental data types

- **Int** — Whole numbers
- **Double** — Double-precision floating-point values
- **Float** — Single-precision floating-point values
- **Bool** — True or false
- **String** — Text
- **Character** — A single extended grapheme cluster

(Each card showed `{t.code}` — the examples were missing from the shared text.)

Swift also provides fixed-width integer types such as Int8, UInt16, Int32, and UInt64.

On modern 64-bit Apple platforms, Int is a 64-bit integer.

## 5. Financial calculations — a very important warning

Let's say PocketBank calculates a transfer amount.

Can we use Double for money?

Technically, yes, but binary floating-point values cannot represent many decimal fractions exactly.

For example, 0.1 and 0.2 are not exactly representable as binary floating-point numbers.

```swift
let a = 0.1
let b = 0.2

print(a + b == 0.3) // false
```

For monetary amounts, prefer an appropriate decimal representation or integer minor units, depending on your domain requirements.

For example:

```swift
let balanceInPaise: Int64 = 2_500_000

let transferInPaise: Int64 = 25_000

let remaining = balanceInPaise - transferInPaise

print(remaining) // 2475000 paise
```

Here, ₹25,000 is represented as 2,500,000 paise.

Using integer minor units can avoid binary floating-point rounding problems, although currency conversion, overflow, and rounding rules still require careful design.

## 6. Explicit type conversion

Swift does not freely mix numeric types.

```swift
let count: Int = 3
let price: Double = 99.5

// let total = count * price  // Error

let total = Double(count) * price

print(total) // 298.5
```

Why? Because Int and Double represent numbers differently.

The compiler requires us to make the conversion explicit.

**Trainer question.** What happens when converting 3.9 to Int?

```swift
let value = 3.9
let result = Int(value)

print(result) // 3
```

For a finite, representable value, conversion to Int truncates the fractional part toward zero.

It does not automatically round to the nearest integer.

## 7. Strings and interpolation

PocketBank needs to display dynamic information.

```swift
let customer = "Ravi"
let balance = 25000

let message = "Hello \(customer), your balance is ₹\(balance)"

print(message)
```

Swift uses \(...) for string interpolation.

This inserts a textual representation of an expression into a string.

### Strings are Unicode-aware

Swift's String is designed to work with Unicode text.

One important distinction for teaching: a Swift Character represents an extended grapheme cluster, which can consist of multiple Unicode scalars.

That matters when working with emojis and international languages.

## 8. Tuples — grouping values without a custom type

Suppose a function needs to return both an account number and a balance.

```swift
let account = (
    number: "PB1001",
    balance: 25000
)

print(account.number)
print(account.balance)
```

A tuple groups multiple values into one compound value.

Tuples are useful for small, temporary groupings.

For domain entities with meaningful behavior, validation, or long-term structure, a struct is often more appropriate.

## 9. Arrays, Sets and Dictionaries

Now imagine PocketBank needs to represent transactions and account information.

- **Array — ordered collection:** [0] ₹500, [1] ₹200, [2] ₹900
- **Set — unique elements:** UPI, CARD, NEFT
- **Dictionary — key/value pairs:** "Ravi" → 25000, "Meena" → 18000

```swift
var transactions = [500, 200, 900]

let paymentMethods: Set<String> = [
    "UPI", "CARD", "NEFT"
]

var balances: [String: Int] = [
    "Ravi": 25000,
    "Meena": 18000
]
```

### Important details

Arrays preserve element order. Sets store unique elements and do not guarantee a particular iteration order. Dictionaries map unique keys to values; dictionary lookup returns an optional because the requested key may not exist.

We'll explore collections and their performance characteristics in later lessons.

## 10. The deeper meaning of let with classes

Earlier, we said let prevents reassignment.

But consider this example:

```swift
class BankAccount {
    var balance = 25000
}

let account = BankAccount()

account.balance = 30000 // Valid
```

Why is this allowed?

Because account is a constant reference to a class instance.

We cannot reassign the reference to a different instance, but the referenced object's mutable properties can still change.

Compare that with a struct:

```swift
struct BankAccount {
    var balance = 25000
}

let account = BankAccount()

// account.balance = 30000 // Error
```

With a struct, the constant binding prevents mutation of the value's stored properties.

| Declaration | Can reassign variable? | Can modify a mutable property? |
|---|---|---|
| let + struct | No | No |
| var + struct | Yes | Yes |
| let + class | No | Yes |
| var + class | Yes | Yes |

This assumes the property itself is declared mutable and is otherwise accessible.

This is one of the most important Swift interview and teaching concepts.

## 11. Practical PocketBank model

Let's combine today's concepts into a small model.

```swift
import Foundation

struct BankAccount {
    let accountNumber: String
    let customerName: String
    var balanceInPaise: Int64
    var isActive: Bool

    mutating func deposit(_ amountInPaise: Int64) {
        guard amountInPaise > 0 else { return }

        let (newBalance, overflow) =
            balanceInPaise.addingReportingOverflow(amountInPaise)

        guard !overflow else { return }

        balanceInPaise = newBalance
    }
}

var account = BankAccount(
    accountNumber: "PB1001",
    customerName: "Ravi",
    balanceInPaise: 2_500_000,
    isActive: true
)

account.deposit(50_000)

print(account.balanceInPaise)
```

This example introduces a new keyword: mutating.

Struct methods that modify stored properties must be marked mutating.

The model also checks for positive deposits and integer overflow. A production banking system would use explicit errors and server-side transaction processing rather than silently returning for invalid operations.

## 12. Trainer-level knowledge check

1. Can a Swift variable inferred as Int later hold a String? — **No.** Swift is statically typed. The variable's inferred type remains Int.
2. Can a let-bound class instance have a mutable property changed? — **Yes.** The reference cannot be reassigned, but mutable properties of the referenced instance can change.
3. Does a Set guarantee its elements will be iterated in insertion order? — **No.** Swift Set does not guarantee a stable insertion-order iteration sequence.
4. Is Double generally ideal for exact financial amounts? — **No.** Binary floating-point cannot represent many decimal fractions exactly.
5. Must a struct method that modifies its stored properties be marked mutating? — **Yes.** A mutating method is required to modify a value type's stored state from an instance method.

## Lesson 1.2 — What you should be able to teach

You should now understand how Swift handles declarations, static typing, inference, numeric values, strings, tuples, collections, and mutability.

More importantly, you should be able to explain why Swift's type system prevents certain mistakes

*(text ends here as shared)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_2.py`) follows this text, with these changes.

**Corrections and canon**
- PocketBank → NPay; account number `PB1001` → `NP1001`.
- The model uses the course's money name `balanceMinor` (the text's `balanceInPaise`); the Part 5 example uses `balanceMinor` / `transferMinor`. The slide model keeps `accountNumber` and `balanceMinor`; the full model with `customerName` and `isActive` is in the LIVE DEMO notes.
- "On modern 64-bit Apple platforms, Int is 64-bit" → "On iPhone and Mac, Int is 64-bit" (Apple Watch's arm64_32 has a 32-bit Int; noted in speaker notes).
- "One of the most important Swift interview and teaching concepts" → interview framing removed (corporate course).
- The text's type cards had missing examples (`{t.code}`); the deck adds one example per type.

**Interactive / trainer material**
- The let/var toggle became a side-by-side slide with the real compiler message for `let`.
- "Prefer let" trainer insight became a rule callout. The `Int(3.9)` trainer question became teaching content (with `Int(-3.9)` and `.rounded()`) and a predict-the-output review question.

**Authored additions (flagged)**
- Outcomes, "Where we are" (Swift stack, bridge to 1.1), recap.
- Real compiler messages (Swift 6.3) for: assigning to a `let`, `Int * Double`, `let` struct property; real outputs for `0.1 + 0.2`, `Int(-3.9)`, `Int(3.9.rounded())`, the 🇮🇳 flag (1 Character, 2 Unicode scalars), dictionary lookup (`Optional(25000)`, `nil`), and two runs of the same `Set` printing different orders.
- Diagrams: the account card, a truncation number line, the flag's scalars, the three collections, and memory pictures under the let class/struct code.
- Model guards and the "Production" card point to 1.7 for thrown errors; interpolation slide notes that ₹25,000 formatting belongs in the ViewModel (Lesson 0.2).
- Review: 8 questions — the text's 5, a multiple-choice on the type of `25000.50`, predict-the-output `Int(-3.9)`, and a spaced item from 1.1 (which compiler stage rejects `balance = "30000"`).
- "Where this goes next": 1.3, 1.4, 1.5, 1.7, 1.10.
- Swift command-line lab "Grow the NPay account" (add `withdraw`, test predictions, run a Set twice, read the `let` error).
- End slide: "Next: Lesson 1.3 — Optionals & Safe Unwrapping".
