# Unit 1 · Lesson 1.8 — Swift ARC, Ownership & Memory Management

> Lesson text as shared; the deck (`index.html`) is built from this text. **PocketBank is renamed NPay** (the course's
> running app). "Trainer" material became speaker notes or review questions. Corrections and authored additions are
> listed at the end under "Deck changes".

Swift Language Mastery · Senior Developer & Trainer Edition

We've already explored memory architecture in Lesson 0.6. Now we'll go deeper into how Swift actually manages object lifetimes, with runnable examples and the ownership decisions you make when developing iOS applications.

Today's central question:

Why does a Swift object sometimes stay alive even after the screen that created it has disappeared?

We'll investigate this through PocketBank.

## 1. Our story — a screen that refuses to die

Imagine PocketBank has a transaction-history screen.

Every time the user opens it, a TransactionViewModel is created.

When the user navigates away, we expect that ViewModel to be released—assuming nothing else needs it.

But something strange happens.

(Memory leak investigation — Ownership design / Retain cycle; Strong capture / Weak capture. Simulated retained ViewModels after navigation: 0. "Each visit leaves behind a ViewModel retained by a simulated strong-reference cycle." Open and close transaction screen / Reset experiment. Conceptual simulation, not actual Swift memory allocation or Instruments measurements.)

This is a common class of iOS memory-management problem.

To understand it, we need to revisit ARC.

## 2. What exactly is ARC?

ARC stands for Automatic Reference Counting.

Swift uses ARC to manage the lifetimes of class instances.

When a class instance is created, strong references can keep it alive.

When the instance no longer has any strong references, it can be deinitialized.

Class instance created → Strong references retain instance → Last strong reference released → deinitialization

### Important nuance

ARC is automatic, but that doesn't mean programmers can ignore ownership.

The compiler inserts and optimizes reference-management operations. The language's ownership rules determine which references keep an instance alive.

## 3. Observe object creation and destruction

Let's create a class with an initializer and deinitializer.

```swift
class Customer {
    let name: String

    init(name: String) {
        self.name = name
        print("Customer created")
    }

    deinit {
        print("Customer destroyed")
    }
}

func testCustomer() {
    let customer = Customer(name: "Ravi")
    print(customer.name)
}

testCustomer()
```

Expected conceptual output:

```
Customer created
Ravi
Customer destroyed
```

The object is no longer needed after the function's scope, assuming no references escape.

The compiler can optimize lifetime management, so avoid teaching reference counts as a fixed sequence of literal runtime instructions.

## 4. Strong references — the default

Consider:

```swift
class Customer {
    let name: String

    init(name: String) {
        self.name = name
    }

    deinit {
        print("Customer released")
    }
}

var customerA: Customer? = Customer(name: "Ravi")
var customerB = customerA

customerA = nil
```

Does the object get destroyed?

No. customerB still strongly references it.

(Strong-reference ownership: Customer instance — 2 conceptual strong references — Object retained. customerA [x], customerB [x], customerC [ ]. Reset.)

**Trainer takeaway:** Setting one variable to nil releases that reference. It doesn't necessarily destroy the referenced object.

## 5. Why strong-reference cycles occur

Now consider two objects.

A Customer owns an Account.

The Account also strongly references the Customer.

```swift
class Customer {
    var account: Account?
}

class Account {
    var owner: Customer?
}

var customer: Customer? = Customer()
var account: Account? = Account()

customer?.account = account
account?.owner = customer

customer = nil
account = nil
```

Both instances still strongly reference one another.

This is a strong-reference cycle.

ARC does not automatically detect and break arbitrary cycles.

We must design the ownership relationship correctly.

## 6. Breaking cycles with weak references

Suppose the customer owns the account, but the account only needs to know which customer owns it.

We can make the account's back-reference weak.

```swift
class Customer {
    var account: Account?
}

class Account {
    weak var owner: Customer?
}
```

Now the relationship becomes: Customer — strongly owns → Account — weakly references Customer.

The weak reference does not keep the Customer alive.

If the Customer is deallocated, the weak reference becomes nil.

## 7. Weak versus unowned

Swift provides two common non-owning reference forms.

| Weak | Unowned |
|---|---|
| Does not retain object | Does not retain object |
| Normally optional | Commonly nonoptional |
| Automatically becomes nil | Does not safely become nil in ordinary unowned usage |
| Suitable when target may disappear | Suitable when target must outlive reference usage |
| Safe nil handling | Invalid access can trap |

Example: Weak

```swift
class Account {
    weak var owner: Customer?
}
```

Example: Unowned

```swift
class CreditCard {
    unowned let customer: Customer

    init(customer: Customer) {
        self.customer = customer
    }
}
```

Use unowned only when the lifetime relationship guarantees that the referenced object remains alive whenever accessed.

## 8. Closures can retain self

This is especially important in SwiftUI and UIKit applications.

```swift
class DashboardViewModel {

    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = {
            self.refresh()
        }
    }

    func refresh() {
        print("Refreshing dashboard")
    }
}
```

The ViewModel owns onRefresh. The closure captures self strongly. That creates a cycle.

Fix:

```swift
func configure() {
    onRefresh = { [weak self] in
        self?.refresh()
    }
}
```

The closure no longer retains the ViewModel through its capture.

**Trainer insight.** Weak capture is not required for every closure. A nonescaping closure executed immediately often doesn't create a problematic ownership relationship. The critical question is: Who owns the closure, how long does it live, and what does it capture?

## 9. Timers and ownership

A repeating timer can retain its callback.

If the callback strongly captures a controller, the controller may remain alive longer than intended.

```swift
class DashboardController {

    var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(
            withTimeInterval: 1,
            repeats: true
        ) { [weak self] _ in
            self?.refresh()
        }
    }

    func refresh() {
        print("Refresh")
    }

    func stop() {
        timer?.invalidate()
        timer = nil
    }
}
```

This example uses weak capture and explicit invalidation.

These address different concerns:
- Weak capture prevents the callback from strongly retaining the controller.
- Invalidation stops the timer when it is no longer needed.

## 10. ARC versus garbage collection

Developers coming from Java often ask this.

| ARC | Tracing garbage collection |
|---|---|
| Manages lifetimes through reference ownership | Finds reachable and unreachable objects |
| Can release objects promptly when ownership ends | Reclamation timing depends on collector |
| Strong cycles can remain retained | Many tracing collectors reclaim unreachable cycles |
| Used for Swift class instances | Used in Java and many other runtimes |

This comparison is simplified. Actual memory management systems use optimizations and additional mechanisms.

**Trainer question.** Does ARC mean Swift applications can never leak memory? No. Strong-reference cycles and unintended long-lived references can still cause memory retention.

## 11. How to investigate memory leaks

In Xcode, use the Memory Graph Debugger and Instruments.

(The shared text contains an empty diagram here, with a stray "7".)

A useful investigation process:
1. Reproduce the suspected leak.
2. Navigate away from the screen.
3. Observe whether expected objects deinitialize.
4. Inspect the Memory Graph.
5. Identify unexpected strong-reference chains.
6. Correct ownership.
7. Repeat the experiment and verify.

A missing deinit message alone does not prove a leak. The object may still be legitimately retained.

## 12. Senior engineer challenge

Imagine a SwiftUI ViewModel starts a long-running asynchronous task.

The task captures the ViewModel strongly.

Will [weak self] always solve the lifetime problem?

Not necessarily.

Even with weak capture, promoting self to a strong reference for the duration of a long asynchronous operation can keep the object alive until that operation completes.

Correct task cancellation, ownership design, and lifecycle management are also important.

We'll study this deeply in the next lesson on Swift concurrency.

## 13. Knowledge check

1. Does ARC automatically collect every strong-reference cycle? (Yes / No)
2. Does weak ownership keep an object alive? (Yes / No)
3. Should every closure capture self weakly? (Yes / No)
4. Can a timer retain a callback closure? (Yes / No)
5. Does a missing deinit message always prove a leak? (Yes / No)

## Lesson 1.8 — Final understanding

You should now be able to explain ARC, object ownership, weak and unowned references, closure capture, retain cycles, and how to investigate memory retention.

The next lesson connects all these concepts to modern asynchronous Swift programming.

## Deck changes

The deck (`index.html`, built by `tools/gen1_8.py`) follows this text, with these changes.

**Structure**
- The text's 13 sections are grouped into **7 Parts** (1–2 the story and ARC; 3–4 lifetimes and strong references; 5–6 cycles and weak; 7 weak vs unowned, plus non-copyable types; 8–9 closures and timers; 10–11 ARC vs GC and investigating leaks; 12 async tasks). Kickers name the text section.

**Real evidence instead of simulators**
- The "screen that refuses to die" simulator became a real count: three visits with a strong closure capture leave **3** `TransactionViewModel`s alive; with `[weak self]`, **0**.
- The strong-reference simulator became real output ("Meena created", "a = nil", "Meena destroyed", "b = nil").
- Customer/Account cycle run for real: nothing prints; with `weak var owner`, "Customer destroyed" and the owner becomes `nil`.
- `unowned` read after deallocation: real trap message.
- Section 12 run for real: with `[weak self]` then `guard let self`, "export finished" prints after the screen closed, and only then `deinit`. With task cancellation, `deinit` comes first (lab).

**Corrections and canon**
- PocketBank → NPay. Classes are `final`; ViewModels and the timer controller are `@MainActor` (course canon; verified to compile against the iOS 26.5 SDK in Swift 6). The timer callback is split over lines for the slide.
- The empty diagram and stray "7" in Section 11 became a seven-step checklist slide with the tools named.
- "Trainer takeaway/insight" became rule callouts; the trainer question (can Swift apps leak?) became a callout.

**Authored additions (flagged)**
- Outcomes, "Where we are" (Unit 01 progress strip, bridge to 1.7), recap.
- `unowned(unsafe)` is undefined behaviour (answers the question left open in Lesson 0.6).
- A slide on non-copyable types (`~Copyable`, `consuming`), promised in Lesson 1.5: real output "uploading with token 1", "token 1 released", and the error "'token' consumed more than once".
- Timer ownership diagram (run loop → timer → closure, weak to the controller).
- Review: 8 questions — the text's 5, a predict-the-output (`customerA = nil` does not print deinit), a multiple-choice on reading `unowned` after deallocation, and a spaced item from 1.5 (ARC manages class instances, not struct values).
- "Where this goes next": 1.9, 8.3, 8.8, 8.9, 9.7.
- Swift command-line lab "Make it leak, then prove the fix" (live count, cycle, unowned trap, export task with cancellation — verified).
- End slide: "Next: Lesson 1.9 — Swift Concurrency: Tasks, Actors & Sendable".
