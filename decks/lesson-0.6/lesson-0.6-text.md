# Lesson 0.6 — iOS Memory Architecture & ARC

*iOS Architecture Mastery · Foundation Series* (Parts 1–13, including "Part 2: Closure Retain Cycles, Memory Leaks & Instruments")

> Lesson text as shared; the deck (`index.html`) uses only this text. "Trainer" material became speaker notes;
> the knowledge check became the review. Outcomes = the lesson's "what you should now be able to teach".
> **Authored for the deck** (flagged): the ARC counter sequence 3 → 2 → 1 → 0 (the text's widget starts at 2), the
> click-by-click states of the retain-cycle and capture experiments, review answers and traps. The text's end breaks
> off at "how iOS protects applications from one another"; the deck's end slide uses that as the next topic.

**Question:** Who creates objects in memory, who owns them, and who destroys them?

## Outcomes
Why Swift distinguishes value and reference semantics · how ARC manages class-instance lifetimes · why strong-reference cycles occur · how weak and unowned differ · why closures and timers can retain objects · how to investigate unexpected retention in Xcode.

## 1. Why does an app need memory?
A shopping app needs memory for products, cart, user, images, network responses, UI state. Some data lives only while a function runs; other data survives many calls. Regions (conceptual, in virtual memory): code/text · global & static data · heap · thread stacks · other mapped memory. **Analogy:** an office building is the address space; temporary desks for immediate work, shared storage for longer-lived things. The OS provides virtual memory; the runtime and app manage allocations.

## 2. Stack versus heap
```swift
func calculateTotal() {
    let price = 100
    let quantity = 3
    let total = price * quantity

    print(total)
}

calculateTotal()
```
Stack: call frame, temporary values, return information (efficient for call-related storage). Heap: dynamically allocated objects and shared storage (flexible; needs allocation and lifetime management).
**Swift nuance:** a struct is not guaranteed to live on the stack, and a class reference variable is not necessarily on the heap. The reliable distinction is **value semantics vs reference semantics**.

## 3. Structs versus classes
Struct (value type):
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
Independent values: changing accountB leaves accountA at ₹5,000.
Class (reference type):
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
print(accountB.balance) // 9000
```
Both variables reference the same instance: both show ₹9,000.

| Struct | Class |
|---|---|
| Value semantics | Reference semantics |
| Assignment produces independent values | Assignment shares an instance |
| No class inheritance | Supports inheritance |
| No identity by default | Has object identity |
| Can use mutating methods | Can mutate properties through shared references |
| Not managed as a class instance by ARC | Class instance lifetime managed by ARC |

Copy-on-write: value types may share storage internally; value semantics does not always mean copying all bytes immediately.

## 4. Automatic Reference Counting
ARC tracks strong references to a class instance; with none left, it can be deinitialized. **Analogy:** a rented conference room; each strong reference holds a booking. *Authored:* the deck's counter goes 3 → 2 → 1 → 0 (deinit can run). Real reference-count operations may be optimized.
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

var customer1: Customer? = Customer(name: "Ravi")
var customer2 = customer1

customer1 = nil
// Object is still alive through customer2

customer2 = nil
// No strong references remain
// deinit can execute
```
Setting one variable to nil does not necessarily destroy the instance; it survives while another strong reference retains it.

## 5. Strong, weak and unowned
**Strong:** keeps the instance alive; the default. **Weak:** does not; optional, becomes nil on deallocation. **Unowned:** does not retain; assumes the instance is alive whenever accessed, or it can crash. A parent strongly owns a child; a child may weakly reference its parent. Use unowned only with a guaranteed lifetime. Do not replace every strong reference with weak.

## 6. Retain cycles
Two people holding hands and refusing to let go:
```swift
class Person {
    var apartment: Apartment?
}

class Apartment {
    var tenant: Person?
}

var person: Person? = Person()
var apartment: Apartment? = Apartment()

person?.apartment = apartment
apartment?.tenant = person

person = nil
apartment = nil
```
After the outside variables are nil, both instances still retain each other. Fix:
```swift
class Person {
    var apartment: Apartment?

    deinit {
        print("Person deinitialized")
    }
}

class Apartment {
    weak var tenant: Person?

    deinit {
        print("Apartment deinitialized")
    }
}
```

## 7. Retain cycles in closures
```swift
class ProfileViewModel {

    var onUpdate: (() -> Void)?

    func configure() {
        onUpdate = {
            print(self)
        }
    }

    deinit {
        print("ProfileViewModel destroyed")
    }
}
```
The ViewModel owns its closure; the closure captures self strongly; both stay alive even without an external owner. Fix:
```swift
class ProfileViewModel {

    var onUpdate: (() -> Void)?

    func configure() {
        onUpdate = { [weak self] in
            guard let self else { return }
            print(self)
        }
    }

    deinit {
        print("ProfileViewModel destroyed")
    }
}
```
`[weak self]` stops the capture retaining the ViewModel; `guard let self` takes a temporary strong reference while running.

## 8. Strong versus weak capture
Strong capture: releasing the external owner leaves the ViewModel alive in a cycle. Weak capture: it is deallocated. `[weak self]` is not mandatory for every closure; it matters for escaping closures that create an unwanted cycle or extend a lifetime.

## 9. Weak versus unowned
| Property | strong | weak | unowned |
|---|---|---|---|
| Keeps object alive | Yes | No | No |
| Becomes nil on deallocation | No | Yes | No (ordinary unowned) |
| Common usage | Ownership | Optional back-reference | Guaranteed lifetime relationship |
| Risk | Retain cycle | Reference may be nil | Invalid access may crash |

Apartment and tenant: weak (the tenant can move out). Credit card and customer: unowned candidate, if the card cannot exist without its customer.
```swift
class Customer {
    let name: String
    var card: CreditCard?

    init(name: String) {
        self.name = name
    }
}

class CreditCard {
    let number: String
    unowned let customer: Customer

    init(number: String, customer: Customer) {
        self.number = number
        self.customer = customer
    }
}
```
Safe only if the card is never accessed after its customer is deallocated. Teach weak first.

## 10. Memory leak versus high memory usage
A **leak**: memory stays allocated though no longer needed and cannot be reclaimed through the intended ownership path. **High usage** may be legitimate (caching) or excessive. An image cache is not a leak, but an unbounded one can still cause memory problems; a small repeated leak can cause serious pressure.

## 11. Detecting leaks with Xcode
**Memory Graph Debugger:** object relationships and unexpectedly alive instances. **Allocations:** allocation patterns, lifetimes, growth. **Leaks:** certain leaked allocations (objects reachable through a cycle may not be reported).
Demo: open a screen with a ViewModel, navigate away, check deinit, inspect the memory graph, find the strong-reference chain. A missing deinit alone does not prove a leak.
Sequence: reproduce → observe growth or missing deinit → inspect Memory Graph → identify the unexpected strong reference → correct ownership or lifecycle → repeat and verify.

## 12. Real-world example: Timer retain cycle
```swift
class DashboardController {

    var timer: Timer?

    func startTimer() {
        timer = Timer.scheduledTimer(
            withTimeInterval: 1,
            repeats: true
        ) { _ in
            self.refreshDashboard()
        }
    }

    func refreshDashboard() {
        print("Refreshing...")
    }

    deinit {
        timer?.invalidate()
        print("Dashboard destroyed")
    }
}
```
The timer infrastructure retains the timer, the timer its closure, the closure self; the controller also holds the timer. deinit cleanup cannot help if the cycle stops deinit running. Safer:
```swift
func startTimer() {
    timer = Timer.scheduledTimer(
        withTimeInterval: 1,
        repeats: true
    ) { [weak self] _ in
        self?.refreshDashboard()
    }
}

func stopTimer() {
    timer?.invalidate()
    timer = nil
}
```
Weak capture addresses ownership of self; explicit invalidation addresses the timer's continuing activity.

## 13. Check your understanding
1. Does assigning a struct always create an immediate deep copy? **No** (copy-on-write may share storage).
2. What keeps a class instance alive under ARC? **Strong references.**
3. Can two instances that strongly retain each other stay alive after external references disappear? **Yes** (a retain cycle).
4. Should every closure capture self weakly? **No.**

**Next:** how iOS protects applications from one another.
