# Unit 1 · Lesson 1.7 — Swift Generics & Error Handling

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. The text as shared **ends after Section 14**
> (no knowledge check or closing section). Corrections and authored additions are listed at the end under "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

In Lesson 1.6, we learned how protocols define common capabilities.

Now we'll answer two important questions:

1. How can we write one function that works with different data types without sacrificing type safety?
2. How should Swift handle an operation that might fail?

These lead us to Generics and Error Handling, two essential features for building production-quality iOS applications.

We'll continue using PocketBank.

## Part A — Swift Generics

### 1. The problem: Repeating the same logic

Imagine PocketBank needs to find the first element of a collection.

For transaction IDs:

```swift
func firstTransaction(_ values: [Int]) -> Int? {
    values.first
}
```

For customer names:

```swift
func firstCustomer(_ values: [String]) -> String? {
    values.first
}
```

Notice the problem. The logic is identical. Only the data type changes. Why should we write the same function repeatedly?

#### The generic solution

```swift
func firstElement<T>(_ values: [T]) -> T? {
    values.first
}

print(firstElement([10, 20, 30]) as Any)
print(firstElement(["Ravi", "Meena"]) as Any)
```

T is a generic type parameter. The compiler determines the concrete type when the function is called.

(Explore generic type substitution: Int / String / Bool — Input {variants[type].input} → firstElement<T> — T becomes Int → Result {variants[type].output})

**Trainer analogy.** Think of a reusable container. The container's design stays the same whether it holds books, documents, or tools. Generics let us define the reusable structure while preserving information about the actual type it contains.

### 2. Why not use Any everywhere?

You might ask: Why not simply accept any value?

```swift
func printValue(_ value: Any) {
    print(value)
}
```

Any can represent values of different types. But when using Any, the compiler knows less about the specific value. We may need runtime type checks or casts to perform type-specific operations.

Generics preserve relationships between types. Compare:

```swift
func identity<T>(_ value: T) -> T {
    value
}

let amount: Int = identity(100)
let name: String = identity("Ravi")
```

The compiler knows that the return type matches the input type.

**Key distinction:** Any provides type erasure; generics preserve type relationships.

### 3. Generic types

Generics aren't limited to functions. We can create generic structs, enums, and classes.

Imagine PocketBank needs a reusable API response wrapper.

```swift
struct APIResponse<T> {
    let data: T
    let statusCode: Int
}
```

Now the same wrapper can contain different response models.

```swift
struct Customer {
    let name: String
}

struct Account {
    let balance: Int
}

let customerResponse = APIResponse(
    data: Customer(name: "Ravi"),
    statusCode: 200
)

let accountResponse = APIResponse(
    data: Account(balance: 25000),
    statusCode: 200
)
```

We have one reusable type: APIResponse<T>. But different concrete instantiations: APIResponse<Customer> and APIResponse<Account>.

### 4. Generic constraints

Sometimes a generic function cannot work with absolutely every type. Suppose we want to compare two values.

```swift
func areEqual<T: Equatable>(_ a: T, _ b: T) -> Bool {
    a == b
}
```

Why do we need T: Equatable? Because Swift cannot assume every type supports equality comparison. The constraint tells the compiler that T must conform to the Equatable protocol.

Generic type T → Constraint: T conforms to Equatable → Equality operation is available

**Trainer connection.** This is where protocols and generics meet. Protocols describe capabilities. Generic constraints specify which capabilities a type must provide.

### 5. Associated types in protocols

Now let's go one level deeper. Suppose different repositories return different kinds of records. A transaction repository returns transactions. A customer repository returns customers. We want one common repository contract.

```swift
protocol Repository {
    associatedtype Item

    func fetchAll() async throws -> [Item]
}
```

associatedtype Item declares a type placeholder that each conforming type determines.

Example:

```swift
struct Customer {
    let name: String
}

struct CustomerRepository: Repository {
    func fetchAll() async throws -> [Customer] {
        [
            Customer(name: "Ravi"),
            Customer(name: "Meena")
        ]
    }
}
```

For CustomerRepository, the associated type Item is inferred as Customer.

#### Why is this important?

Associated types let protocols express relationships involving types without hardcoding one concrete model. This is fundamental to Swift's standard library and SwiftUI.

## Part B — Swift Error Handling

### 6. The problem: A bank transfer can fail

Imagine a customer tries to transfer ₹10,000. Several things could go wrong:
- The amount is invalid.
- The account has insufficient funds.
- The account is inactive.
- The network request fails.
- The backend rejects the operation.

How should Swift represent these failures? A common approach is to define an error type.

```swift
enum TransferError: Error {
    case invalidAmount
    case insufficientFunds
    case accountInactive
}
```

Swift's Error protocol marks values that can represent failures.

### 7. Throwing functions

A function that can throw an error uses the throws keyword.

```swift
func validateTransfer(
    amount: Int,
    balance: Int
) throws {
    guard amount > 0 else {
        throw TransferError.invalidAmount
    }

    guard amount <= balance else {
        throw TransferError.insufficientFunds
    }
}
```

Notice the difference between returning a normal result and throwing an error. A throwing function either completes normally or exits by throwing an error.

(Interactive transfer validation: available balance ₹25,000, transfer amount ₹10,000, [x] Account active → Validation successful. Client-side validation simulation only. Actual transfers require server-side authorization and transactional processing.)

### 8. do, try and catch

How does the caller handle a throwing function?

```swift
do {
    try validateTransfer(
        amount: 10000,
        balance: 25000
    )

    print("Validation successful")

} catch TransferError.invalidAmount {
    print("Invalid transfer amount")

} catch TransferError.insufficientFunds {
    print("Insufficient funds")

} catch {
    print("Unexpected error: \(error)")
}
```

| Keyword | Meaning |
|---|---|
| throws | Declares that a function can throw |
| throw | Produces an error |
| try | Marks a call that may throw |
| do | Creates a scope for handling throwing operations |
| catch | Handles matching errors |

**Trainer analogy.** Imagine airport security screening. If everything is valid, the passenger proceeds. If a rule is violated, the process stops and a specific error condition is reported. The caller decides how to respond to that failure.

### 9. try? versus try!

Swift provides three common ways to call a throwing function.

- **try** — propagate or handle errors: `let result = try someThrowingFunction()`. The error must be handled or propagated from an appropriate throwing context.
- **try?** — convert failure to nil: `let result = try? someThrowingFunction()`. If the operation throws, the expression produces nil. Error details are discarded.
- **try!** — assert that no error will occur: `let result = try! someThrowingFunction()`. If the operation throws, execution traps at runtime.

**Trainer rule.** Use try! only when failure is genuinely impossible under a justified invariant. Do not use it to avoid writing error-handling code.

### 10. Error propagation

A function can allow an error to travel upward to its caller.

```swift
func performTransfer() throws {
    try validateTransfer(
        amount: 10000,
        balance: 25000
    )

    print("Transfer validation completed")
}
```

Here, performTransfer() is also marked throws. It does not need to catch the validation error itself. The caller can decide how to handle it.

View calls ViewModel → ViewModel calls Service → Service throws an error → ViewModel handles or propagates error

A good architecture decides which layer should handle which errors. For example, a networking service may identify an HTTP failure, while the ViewModel decides what user-facing message to display.

### 11. Result type — success or failure as a value

Swift also provides Result.

```swift
func validate(
    amount: Int
) -> Result<String, TransferError> {

    guard amount > 0 else {
        return .failure(.invalidAmount)
    }

    return .success("Valid transfer")
}
```

Result<Success, Failure> represents one of two cases: .success(value), .failure(error). The failure type must conform to Error.

#### How is Result different from throws?

throws expresses failure through control flow. Result represents success or failure as an ordinary value that can be stored, returned, or passed around. Both are useful, depending on the API design.

### 12. Async throwing functions

Now connect error handling with networking.

```swift
func fetchBalance() async throws -> Int {
    // Illustrative asynchronous operation
    try await Task.sleep(for: .seconds(1))
    return 25000
}
```

The function is both: async — it can suspend; throws — it can fail.

Calling it requires:

```swift
do {
    let balance = try await fetchBalance()
    print(balance)
} catch {
    print("Failed: \(error)")
}
```

try and await address different concerns. try acknowledges possible failure. await marks a potential suspension point.

### 13. Generics and errors together — a reusable API service

Let's combine the concepts.

```swift
import Foundation

struct APIClient {

    func fetch<T: Decodable>(
        from url: URL,
        as type: T.Type
    ) async throws -> T {

        let (data, response) =
            try await URLSession.shared.data(from: url)

        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(
            T.self,
            from: data
        )
    }
}
```

Why is this powerful? The same method can decode different response models. For example:

```swift
struct Customer: Decodable {
    let name: String
}

struct Balance: Decodable {
    let amount: Int
}
```

Both models can use the same generic networking function. The generic constraint T: Decodable ensures that the response type supports decoding. This is a common pattern in real Swift networking layers.

### 14. Senior engineer design discussion

Imagine the API returns HTTP 401 Unauthorized. Should the generic networking service immediately navigate to the login screen?

Usually, no.

The networking layer should report a meaningful authentication failure. A higher-level session or application coordinator can decide whether reauthentication is required. The UI layer then presents the appropriate screen.

This separation makes the system easier to test and maintain.

*(text ends here as shared — no knowledge check or closing section)*

## Deck changes

The deck (`index.html`, built by `tools/gen1_7.py`) follows this text, with these changes.

**Structure**
- The text's 14 sections (Part A generics A1–A5, Part B errors B6–B14) are grouped into **8 Parts**: generic functions (A1–A2); generic types and constraints (A3–A4); associated types (A5); errors and throwing (B6–B7); handling errors (B8–B9); propagation and Result (B10–B11); async throws and the generic API client (B12–B13); errors across layers (B14). Kickers name the text section.
- The text ends after Section 14; the recap, review, "Where this goes next", lab and end slide are authored.

**Corrections and canon**
- PocketBank → NPay. Amounts in paise (`Int64`): `Account.balanceMinor`, `validateTransfer(amountMinor:balanceMinor:...)` (₹10,000 = 1,000,000 paise against ₹25,000), `fetchBalance() -> Int64`, `Balance.balanceMinor` instead of `amount: Int`.
- `validateTransfer` gains `isActive:` and an `accountInactive` guard, matching the text's simulator (which had an "Account active" checkbox the code lacked).
- Status check written `(200..<300)` (course canon; same meaning as the text's `200...299`). `fetch(_:from:)` takes the type first.
- Airport and container analogies dropped (the course keeps two analogies).

**Real evidence instead of simulators**
- Generic substitution simulator → table of real outputs (`Optional(10)`, `Optional("Ravi")`, `Optional(true)`).
- Transfer validation simulator → four real runs through the do/catch: ₹10,000 → "Validation successful"; ₹0 → "Invalid transfer amount"; ₹30,000 → "Insufficient funds"; inactive → "Unexpected error: accountInactive" (no specific catch, so the general one handles it).
- Real compiler messages (Swift 6.3): `Any` + 1; `==` on an unconstrained `T`; a throwing call without `try`. Real `try!` trap message. Real `Result` output.

**Authored additions (flagged)**
- Outcomes, "Where we are" (Unit 01 progress strip, bridge to 1.6), recap.
- Associated-type diagram (CustomerRepository, TransactionRepository); propagation diagram (View → ViewModel → Service, error travels up); 401 layering diagram with an `APIError` enum (`unauthorized`, `server(status:)`, `decoding`).
- Review: 8 questions (what T becomes, why `T: Equatable`, predict the ₹0 do/catch, `try!` crash, Result vs throws, 401 layering, `try?` gives nil, and a spaced item from 1.6: a `some Repository` function cannot return two types).
- "Where this goes next": 1.9, 1.10, 4.8, 5.4, 5.5.
- Swift command-line lab "Validate and decode" (validateTransfer with four cases, a Result version, a generic `decode<T: Decodable>` with a broken key).
- End slide: "Next: Lesson 1.8 — ARC, Ownership & Memory Management".
