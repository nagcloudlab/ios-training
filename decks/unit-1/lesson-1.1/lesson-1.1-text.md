# Unit 1 · Lesson 1.1 — Inside the Swift Programming Language

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. Corrections and authored additions are
> listed at the end under "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

We've completed our iOS architecture foundation. Now we'll explore the language used to build iOS applications.

But rather than starting with let, var, and print(), let's begin with a more interesting question:

How does the Swift code we write become instructions that an Apple processor can execute?

Today we'll explore Swift's design philosophy, compiler, LLVM, type system, memory model, and how Swift differs from Java, Python, and JavaScript.

## 1. Why did Apple create Swift?

Imagine you're building PocketBank, a financial application.

You want a language that is:
- Fast enough for demanding native applications.
- Safe enough to prevent many common programming errors.
- Expressive enough to write understandable code.
- Capable of working with existing Apple frameworks.
- Suitable for modern concurrency and application development.

Apple introduced Swift in 2014. It was designed to offer a modern alternative to Objective-C while interoperating with existing Apple development technologies.

### The major Swift design goals

- **Performance** — Native compiled code and optimization
- **Safety** — Optionals, type checking, memory safety mechanisms
- **Expressiveness** — Concise syntax and powerful abstractions
- **Interoperability** — Integration with Apple frameworks and supported language interfaces

**Trainer insight.** Don't teach Swift as merely "Apple's version of Java." Swift has its own language design, including value semantics, protocol-oriented programming, optionals, automatic reference counting, and structured concurrency.

## 2. Is Swift compiled or interpreted?

Swift is primarily a compiled programming language.

Let's start with a simple example.

```swift
let amount = 500
let quantity = 3

let total = amount * quantity

print(total)
```

When building a native Swift application, source code goes through a compilation pipeline.

### Simplified Swift compilation pipeline

1. **Swift Source Code** — main.swift · .swift files
2. **Parsing & Semantic Analysis** — Syntax, types, declarations and diagnostics
3. **SIL** — Swift Intermediate Language
4. **LLVM IR** — Lower-level intermediate representation
5. **Machine Code** — Instructions for the target architecture
6. **Executable** — Linked binary and dependencies

Conceptual native compilation pipeline. Actual compilation involves additional passes, modules, optimization stages and linking details.

### What is SIL?

SIL stands for Swift Intermediate Language.

It is an intermediate representation designed specifically for Swift. It helps the compiler represent Swift language semantics and perform optimizations before lowering code further.

### What is LLVM?

LLVM is a compiler infrastructure project.

Swift uses LLVM infrastructure to optimize and generate native machine code for supported targets.

The important relationship is:

Swift source → Swift-specific compilation → LLVM-based code generation → native executable.

## 3. Swift versus Java versus Python versus JavaScript

Since you already have programming experience, comparison is one of the fastest ways to understand Swift.

| Feature | Swift | Java | Python | JavaScript |
|---|---|---|---|---|
| Typical execution | Native compilation | JVM bytecode/JIT | Interpreter/VM | Engine/JIT |
| Type system | Static | Static | Dynamic | Dynamic |
| Null handling | Explicit optionals | Nullable references | None | null, undefined |
| Memory management | ARC + value semantics | Garbage collection | Reference counting + GC in CPython | Garbage collection |
| Common app UI | SwiftUI, UIKit | Java UI ecosystems | Various frameworks | Web and other frameworks |

These are broad comparisons; language implementations and execution modes vary.

### Example: Declaring a variable — same idea, different languages

```swift
let balance = 25000
var customerName = "Ravi"
```

Swift uses let for an immutable binding and var for a mutable variable.

```java
final int balance = 25000;
String customerName = "Ravi";
```

```python
balance = 25000customer_name = "Ravi"
```

Swift also supports type inference. The compiler can infer that balance is an Int and customerName is a String.

## 4. Swift is strongly and statically typed

Consider this code:

```swift
var balance = 25000

balance = "Twenty five thousand"
```

This does not compile.

Why?

Because Swift inferred that balance has type Int. Assigning a String violates that type.

### Explore Swift type checking

```swift
balance = 30000
balance = "30000"
balance = 30000.5
```

Declared type: Int — Valid assignment

Swift doesn't silently convert arbitrary values between unrelated types.

For example:

```swift
let count: Int = 10
let price: Double = 99.5

let total = Double(count) * price
```

We explicitly convert count to Double.

**Trainer question.** Why is explicit conversion useful in financial software?

It makes potentially important representation changes visible and easier to review. However, financial calculations also require appropriate numeric representations; Double is not generally ideal for exact monetary arithmetic.

## 5. One of Swift's most important features: Optionals

Let's return to PocketBank.

Suppose we ask the server for a customer's nickname.

Some customers have a nickname. Others don't.

How should Swift represent that?

```swift
var nickname: String? = "Ravi"

nickname = nil
```

The ? means the variable can contain either a String value or no value.

Optional — two possible states: Has value / No value. `String?` → `Some("Ravi")`: the optional contains a String.

### Why is this important?

In many languages, null-related errors occur because code assumes a value exists.

Swift makes the possibility of absence explicit in the type system.

You generally must unwrap an optional before using the contained value as a nonoptional value.

```swift
let nickname: String? = "Ravi"

if let name = nickname {
    print("Hello, \(name)")
} else {
    print("No nickname available")
}
```

We'll cover optionals in much greater depth in Lesson 1.3.

## 6. Swift values versus references

This is another major language-design feature.

Consider two kinds of data:
- A bank transaction amount.
- A shared account session manager.

A transaction amount is naturally modeled as a value.

A session manager may need shared identity and controlled mutable state.

Swift supports both value types and reference types.

- **Value types** — Structs, enums and tuples. Assignment produces an independent logical value.
- **Reference types** — Classes and actors. Multiple references can refer to the same instance.

### Struct example

```swift
struct Account {
    var balance: Int
}

var accountA = Account(balance: 5000)
var accountB = accountA

accountB.balance = 9000

print(accountA.balance) // 5000
print(accountB.balance) // 9000
```

### Class example

```swift
class Account {
    var balance: Int

    init(balance: Int) {
        self.balance = balance
    }
}

let accountA = Account(balance: 5000)
let accountB = accountA

accountB.balance = 9000

print(accountA.balance) // 9000
```

**Trainer insight.** Do not simplify this to "struct lives on stack, class lives on heap." That is not a guaranteed rule in Swift. The correct distinction is value semantics versus reference semantics.

## 7. How does Swift manage memory?

Swift uses Automatic Reference Counting (ARC) to manage the lifetime of class instances.

We already studied this in Lesson 0.6.

The key idea is:

Class instance created → Strong references keep it alive → No remaining strong ownership → deinitialization

ARC is different from tracing garbage collection.

It also introduces ownership challenges, such as retain cycles.

We will revisit ARC when studying classes, closures, and concurrency.

## 8. Swift's protocol-oriented design

Swift encourages building abstractions using protocols.

Imagine PocketBank supports multiple account providers.

Instead of forcing every provider into one class inheritance hierarchy, we can define a protocol.

```swift
protocol BalanceProviding {
    func fetchBalance() async throws -> Decimal
}
```

Any suitable type can conform to this protocol.

```swift
struct MockBalanceService: BalanceProviding {
    func fetchBalance() async throws -> Decimal {
        Decimal(25000)
    }
}
```

This becomes useful for dependency injection, testing, modular architecture, and interchangeable implementations.

**Trainer question.** Is Swift purely object-oriented?

No. Swift supports multiple programming paradigms, including object-oriented, functional, generic, and protocol-oriented programming.

## 9. How Swift connects to iOS development

Now let's connect the language to the platform.

1. **Swift language** — Types, functions, structs, classes, protocols
2. **SwiftUI / UIKit** — Application interfaces and interaction
3. **Foundation and system APIs** — Networking, data, files and other capabilities
4. **Swift compiler and runtime** — Native code, runtime support and ARC
5. **iOS operating system** — Process execution, scheduling, memory and security
6. **Apple hardware** — Processor, memory, GPU and device capabilities

This is why we studied iOS architecture before Swift syntax.

You now know where Swift fits within the overall system.

## 10. Trainer-level knowledge check

1. Does Swift always execute through a JVM-like virtual machine? — **No.** Swift is commonly compiled to native machine code for Apple platforms.
2. Does assigning a struct always create a separate logical value? — **Yes.** Swift structs have value semantics, even though storage copying may be optimized.
3. Can Swift infer variable types? — **Yes.** Swift supports static type inference.
4. Does async automatically create a background thread? — **No.** Async supports suspension; it does not automatically imply a new thread.
5. Are protocols useful for dependency injection? — **Yes.** Protocols can define abstractions that allow interchangeable implementations.

## Lesson 1.1 — Final understanding

You should now be able to explain:
- Why Swift was created and what problems it addresses.
- How Swift source code becomes native machine code.
- The role of SIL and LLVM.
- Static typing and type inference.
- Optionals and explicit absence.
- Value versus reference semantics.
- ARC and memory ownership.
- Protocol-oriented design.
- How Swift integrates with iOS frameworks.

## Next — Lesson 1.2: Variables, Constants & Swift's Type System

We'll go deeper into actual Swift programming, using PocketBank examples.

Our next lesson will cover let versus var, type inference, numeric types, strings, tuples, collections, type conversion, and the difference between mutability and value semantics.

We'll also begin building a small PocketBank

*(text ends here as shared)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_1.py`) follows this text, with these changes.

**Corrections and canon**
- PocketBank → NPay throughout.
- Money uses the course canon: the `Account` examples hold `balanceMinor: Int64` (paise; 500,000 = ₹5,000), and the protocol returns `Balance` with `balanceMinor` instead of `Decimal` (the text's `Decimal(25000)` becomes `Balance(balanceMinor: 2_500_000)`, ₹25,000). Blank lines are trimmed so each snippet stays ≤12 lines.
- The Python declaration (`balance = 25000customer_name = "Ravi"`, a formatting slip) is shown on two lines.
- Notes add: `swift main.swift` still compiles before running (no bytecode VM); closures are reference types too; a struct holding a class reference copies the reference (review question 3); the stack/heap point links back to Lesson 0.6.
- The explicit-conversion slide connects "Double is not ideal for money" to NPay's paise-in-`Int64` rule.

**"Trainer" material**
- "Not Apple's version of Java" and "struct on stack / class on heap" became student-facing callouts (a rule and the slide's misconception).
- The two trainer questions (explicit conversion in finance; is Swift purely object-oriented?) moved into the review.

**Authored additions (flagged)**
- Outcomes slide (from the text's "Final understanding") and a "Where we are" slide using the text's Section 9 stack, with a Last time / Today bridge to Lesson 0.10.
- Compiler brackets on the pipeline diagram (Swift frontend / LLVM / linker).
- "What SIL and LLVM do" evidence table: real `swiftc -O` output for the text's example (Swift 6.3, arm64): `smul_with_overflow_Int64` in SIL, `store i64 1500` in LLVM IR, `mov w20, #1500` in assembly.
- Type-checking slide shows the real compiler messages for the text's three assignments.
- Memory pictures under each Account example (two values for the struct; two references to one instance for the class), and the protocol diagram (`DashboardViewModel` → `BalanceProviding` ← `BalanceService`, `MockBalanceService`).
- Recap slide.
- Review: 8 questions — the text's 5, its two trainer questions, and a multiple-choice on pipeline order. Question 8 (async and threads) is a spaced item from Lesson 0.5.
- "Where this goes next": 1.2, 1.3, 1.5, 1.6, 1.8, 1.9.
- Swift command-line lab "See the pipeline yourself" (build and run; find the stages with `-emit-sil`, `-emit-ir`, `-S`; break the type and read the error).
- End slide: "Next: Lesson 1.2 — Variables, Constants & Swift's Type System".
