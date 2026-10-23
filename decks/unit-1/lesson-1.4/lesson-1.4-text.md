# Unit 1 · Lesson 1.4 — Swift Functions, Parameters & Closures

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. The text as shared **ends partway through
> Section 16** (no knowledge check or closing section). Corrections and authored additions are listed at the end under
> "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

We've learned variables, types, and Optionals. Now we'll explore how Swift organizes executable logic.

This lesson is especially important because functions and closures appear everywhere in iOS development: SwiftUI buttons, networking, event handling, asynchronous operations, and dependency injection.

We'll continue using PocketBank.

## 1. The problem — repeated business logic

Imagine PocketBank needs to calculate a transaction fee.

The rule is simple: a 2% fee on the transfer amount.

Without functions, we might repeat the same calculation throughout the application.

```swift
let fee1 = 1000 * 0.02
let fee2 = 2500 * 0.02
let fee3 = 5000 * 0.02
```

What happens if the fee changes from 2% to 3%?

We would need to update the calculation everywhere.

A function solves this problem by giving reusable logic a name.

Input — Transfer amount → Function — Calculate fee → Output — Fee amount

## 2. Your first Swift function

```swift
func calculateFee(amount: Double) -> Double {
    return amount * 0.02
}

let fee = calculateFee(amount: 1000)
print(fee) // 20.0
```

Let's break down the syntax.

| Part | Meaning |
|---|---|
| func | Declares a function |
| calculateFee | Function name |
| amount: Double | Parameter and its type |
| -> Double | Return type |
| return | Returns a result |

(Interactive function simulator: transfer amount ₹1,000, fee rate 2%, `calculateFee(amount: {amount})` → calculated fee ₹20.00. Illustrative fee calculator; production monetary calculations should use suitable exact representations and rounding rules.)

## 3. Parameters versus arguments

These terms are often confused.

```swift
func greet(name: String) {
    print("Hello, \(name)")
}

greet(name: "Ravi")
```

name in the function declaration is a parameter.

"Ravi" passed during the function call is an argument.

**Trainer analogy.** A function is like a machine. A parameter describes what kind of input the machine accepts. An argument is the actual item supplied when operating it.

## 4. Swift's external and internal parameter names

Swift has a distinctive feature: parameters can have both external argument labels and internal names.

```swift
func transfer(
    from source: String,
    to destination: String,
    amount: Int
) {
    print("\(source) → \(destination): \(amount)")
}

transfer(
    from: "PB1001",
    to: "PB2002",
    amount: 500
)
```

| External label | Internal name |
|---|---|
| from | source |
| to | destination |
| amount | amount |

External labels make function calls readable.

Internal names make the implementation understandable.

### Why is this useful?

Compare `transfer("PB1001", "PB2002", 500)` with `transfer(from: "PB1001", to: "PB2002", amount: 500)`.

The second call communicates intent much more clearly.

## 5. Omitting argument labels with _

Sometimes an argument label is unnecessary.

```swift
func square(_ number: Int) -> Int {
    number * number
}

print(square(5)) // 25
```

The underscore means callers do not provide an external argument label for that parameter.

Without the underscore, the call would ordinarily require the parameter's external label.

## 6. Functions can return multiple values

Swift functions can return tuples.

```swift
func accountSummary() -> (
    balance: Int,
    isActive: Bool
) {
    (balance: 25000, isActive: true)
}

let result = accountSummary()

print(result.balance)
print(result.isActive)
```

This is useful for small grouped results.

For a stable domain model with meaningful behavior, a dedicated struct is often a better choice.

## 7. Default parameter values

Imagine a function that calculates a fee using a default rate.

```swift
func calculateFee(
    amount: Double,
    rate: Double = 0.02
) -> Double {
    amount * rate
}

print(calculateFee(amount: 1000))             // 20
print(calculateFee(amount: 1000, rate: 0.03)) // 30
```

Default parameters reduce repeated arguments while allowing customization.

## 8. What is a closure?

Now we reach one of Swift's most important concepts.

A closure is a self-contained block of functionality that can be passed around and executed later.

Think of a closure as an executable instruction package.

Functions are also closures in the broad Swift language sense, but closure expressions are especially useful for inline behavior.

Create a block of executable logic → Store or pass it → Execute it when needed

### First closure

```swift
let greet = {
    print("Hello from a closure")
}

greet()
```

The closure is assigned to a constant and then called like a function.

## 9. Closure syntax

Let's create a closure that accepts two numbers and returns their sum.

```swift
let add: (Int, Int) -> Int = { a, b in
    return a + b
}

print(add(10, 20)) // 30
```

Read the syntax:
- (Int, Int) -> Int describes the closure type.
- { ... } contains the closure expression.
- a, b are the parameters.
- in separates parameters from the body.
- return a + b produces the result.

- **Function** — Named reusable behavior. `func add(...)`
- **Closure expression** — Inline executable value. `{ a, b in ... }`

## 10. Why closures matter in iOS

Imagine PocketBank has a button.

When the user taps the button, we want to execute some code.

```swift
Button("Check Balance") {
    print("Button tapped")
}
```

The code inside { ... } is a closure.

SwiftUI receives that closure and invokes it when the button is activated.

This is the bridge between Swift language fundamentals and event-driven UI programming.

User taps Button → SwiftUI recognizes activation → Action closure executes → Application logic runs

## 11. Passing closures into functions

Let's create a function that accepts another operation.

```swift
func performOperation(
    a: Int,
    b: Int,
    operation: (Int, Int) -> Int
) -> Int {
    operation(a, b)
}

let result = performOperation(
    a: 10,
    b: 5,
    operation: { x, y in
        x + y
    }
)

print(result) // 15
```

The operation parameter is itself a function-like value.

This allows behavior to be supplied dynamically.

**Trainer question.** Why is this powerful? Because the same function can work with different operations without changing its implementation.

## 12. Trailing closure syntax

Swift provides a cleaner syntax when the final argument is a closure.

```swift
let result = performOperation(a: 10, b: 5) {
    x, y in
    x + y
}
```

This is called trailing closure syntax.

It is extremely common in SwiftUI. For example:

```swift
Button("Transfer") {
    print("Transfer tapped")
}
```

The closure is placed after the function's parentheses, making the call more readable.

## 13. Closures capture surrounding values

Now comes the deeper concept.

A closure can use values from the environment in which it was created.

```swift
func makeCounter() -> () -> Int {
    var count = 0

    return {
        count += 1
        return count
    }
}

let counter = makeCounter()

print(counter()) // 1
print(counter()) // 2
print(counter()) // 3
```

Notice something interesting.

The makeCounter() function has finished executing.

Yet the closure still remembers count.

This is called capturing values.

(Interactive closure capture simulator: captured variable count = 0; Call counter() → returned value; Create a new counter. Conceptual simulation of a closure maintaining captured state.)

**Trainer insight.** Captured state can outlive the function call that created the closure. This is also why closures can create memory ownership problems when they strongly capture class instances.

## 14. Escaping versus nonescaping closures

This is an advanced but important Swift concept.

A nonescaping closure is guaranteed not to outlive the function call in which it is passed.

An escaping closure may be stored or executed after that function returns.

```swift
func executeNow(action: () -> Void) {
    action()
}
```

The closure is executed during the function call.

Now consider:

```swift
class TaskManager {
    var savedAction: (() -> Void)?

    func register(action: @escaping () -> Void) {
        savedAction = action
    }
}
```

The closure is stored for later execution.

Therefore, it must be marked @escaping in the parameter declaration.

### Why does this matter?

Escaping closures can extend the lifetime of captured objects.

That is where strong reference cycles can occur.

## 15. Closures and ARC

Let's connect Lesson 1.4 to Lesson 0.6.

```swift
class DashboardViewModel {

    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = {
            self.refresh()
        }
    }

    func refresh() {
        print("Refreshing")
    }
}
```

Here, the ViewModel strongly owns the closure, and the closure strongly captures the ViewModel.

That creates a retain cycle.

Fix:

```swift
func configure() {
    onRefresh = { [weak self] in
        self?.refresh()
    }
}
```

Important: Weak capture is appropriate when needed to avoid an unwanted ownership relationship. Not every closure requires [weak self].

## 16. Higher-order functions — map, filter and reduce

Swift collections support powerful functions that accept closures.

Suppose PocketBank has transaction amounts:

```swift
let transactions = [500, 1200, 300, 2500]
```

map — transform each element

```swift
let doubled = transactions.map { $0 * 2 }

print(doubled)
// [1000, 2400, 600, 5000]
```

filter — select matching elements

```swift
let large = transactions.filter { $0 > 1000 }

print(large)
// [1200, 2500]
```

reduce — combine elements

```swift
let total = transactions.reduce(0) { result, value in
    result + value
}

print(total) // 4500
```

(Explore higher-order functions: map / filter / reduce. Original values 500, 1200, 300, 2500.)

*(text ends here as shared — no knowledge check or closing section)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_4.py`) follows this text, with these changes.

**Structure**
- The text's 16 short sections are grouped into **8 Parts** (1–2 functions; 3–5 parameters and labels; 6–7 returns and defaults; 8–9 closures; 10–12 closures in iOS; 13 capture; 14–15 escaping and ARC; 16 map/filter/reduce). Each slide's kicker names its text section. One divider per section would have given 16 dividers for ~20 content slides.
- The text ends partway through Section 16; the recap, review, "Where this goes next", lab and end slide are authored.

**Corrections and canon**
- PocketBank → NPay; accounts `PB1001`/`PB2002` → `NP1001`/`NP2002`; button "Check Balance" → "Refresh balance" (inside a `DashboardView`).
- Money in whole paise (`Int64`, Lesson 1.2) instead of `Double`: `calculateFee(amountMinor:)` returns `amountMinor * 2 / 100` (100,000 paise → 2,000 = ₹20); the default parameter is `percent: Int64 = 2`; `transfer(..., amountMinor:)`; `accountSummary()` returns `balanceMinor`. Notes say integer division truncates and a real fee needs an explicit rounding rule (1.10).
- `DashboardViewModel` is `@MainActor final class` (course canon) with a `deinit`, so the retain cycle can be shown running.

**Interactive / trainer material**
- The fee simulator became a table of real outputs (₹1,000 → ₹20, ₹2,500 → ₹50, ₹5,000 → ₹100).
- The closure-capture simulator became a stepped diagram of the captured `count` (1, 2, 3; a new counter starts at 1).
- The higher-order-function explorer became a stepped diagram (map, filter, reduce).
- The machine analogy and the "why is this powerful?" trainer question became notes and a card.

**Authored additions (flagged)**
- Outcomes, "Where we are" (bridge to 1.3), recap.
- Real compiler messages (Swift 6.3): missing argument labels, extraneous label `number:`, and assigning a non-escaping parameter to an `@escaping` closure.
- Run evidence for the retain cycle: with strong `self`, setting the ViewModel to `nil` prints nothing (leaked); with `[weak self]`, `DashboardViewModel deinit` prints (freed).
- `performOperation(..., operation: *)` gives 50; `filter { $0 > 1000 }.reduce(0, +)` gives 3700.
- Review: 8 questions (labels, `_`, default parameter, two counters, `@escaping`, `[weak self]`, chained filter/reduce, and a spaced item from 1.3: calling an optional closure with `?()`).
- "Where this goes next": 1.5, 1.7, 1.8, 1.9, 2.3.
- Swift command-line lab "NPay fee toolkit" (fees with a default rate, filter/map/reduce over transfers, a receipt counter, the retain-cycle demo).
- End slide: "Next: Lesson 1.5 — Structs, Classes & Value Semantics".
