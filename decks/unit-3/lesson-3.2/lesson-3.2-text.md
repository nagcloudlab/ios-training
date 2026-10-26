# Unit 3 · Lesson 3.2 — Typed Routes & Programmatic Navigation

> Lesson text as shared, in three pieces: Sections 1–14 with the checkpoint; a follow-up Q&A ("don't we have a routing
> module here?", 1–5); and a note offering a complete project ZIP through 3.2, which was not shared. Interactive widgets
> are described in brackets. The deck (`index.html`, built by `tools/gen3_2.py`) follows all three. The complete code
> at the end is **authored**: the text's snippets assembled onto the 3.1 complete code, and run in the simulator.
> Evidence and authored additions are listed under "Deck changes".

NPay Engineering Lab · NavigationStack → Route Enum → NavigationPath → State-Driven Navigation

In Lesson 3.1, we built three working NPay screens: Dashboard, Send Money, and Transaction History. We used NavigationLink to move between them. But now consider a more advanced requirement: after a successful demo payment, NPay should automatically navigate to a Payment Success screen. There is no navigation link for the user to tap. The application itself must initiate navigation. How does SwiftUI navigate in response to application logic? That's what we'll investigate today.

## 1. Our NPay milestone

[New navigation journey: NPay Dashboard (user chooses Send Money) → Payment Screen (user enters ₹1,500 and recipient) → Payment processing (local demo validates and records payment) → Payment Success (application navigates automatically) → Back to Dashboard (return to the updated balance).]

We'll preserve the existing NPay balance and transactions. Only the navigation behavior changes.

## 2. Why NavigationLink alone isn't enough

Previously:

```swift
NavigationLink {
    PaymentScreen()
} label: {
    Text("Send Money")
}
```

This is destination-based navigation. The link declares where the user goes when they activate it. But after a payment succeeds, we want to navigate from code. We could try to control this with multiple booleans, but as the application grows, that becomes difficult to manage. Instead, we'll model navigation as state.

## 3. Introducing a typed route

Let's define the destinations our NPay application understands.

```swift
enum NPayRoute: Hashable {
    case payment
    case history
    case success(transactionID: UUID)
}
```

This is an ordinary Swift enum with associated values. Connect it to Unit 1. Hashable allows route values to participate in SwiftUI's navigation path system. The success route carries a transaction identifier.

**Why carry an ID instead of the entire Transaction?** Because navigation should usually identify the destination and the data needed to resolve it. Passing a stable ID avoids coupling the route to an entire mutable transaction object.

[Typed navigation destinations: .payment — Payment form; .history — Transactions; .success(id) — Receipt.]

## 4. NavigationStack with a path

Now introduce:

```swift
@State private var path: [NPayRoute] = []
```

And:

```swift
NavigationStack(path: $path) {
    // Dashboard
}
```

Notice `$path`. This is a binding to the array that represents the navigation path. The stack can read and update it as navigation occurs.

**What does the array mean?** An empty array represents the root destination: `[]`. After navigating to Payment: `[.payment]`. After navigating to Success: `[.payment, .success(transactionID: id)]`. The array models the destinations above the root.

## 5. Interactive navigation-path explorer

[Observe the navigation state: Dashboard; buttons Open Payment, Open History. "Path depth above root: 0. Pushing appends a route; popping removes the last route; returning home clears the path."]

This is the essence of state-driven navigation.

## 6. Register destinations using navigationDestination

SwiftUI needs to know which view corresponds to each route. We register the mapping:

```swift
.navigationDestination(for: NPayRoute.self) { route in
    switch route {
    case .payment:
        PaymentScreen()

    case .history:
        HistoryScreen()

    case .success(let transactionID):
        PaymentSuccessScreen(
            transactionID: transactionID
        )
    }
}
```

This example shows the routing structure; the actual screen initializers will still need the dependencies we established in Lesson 3.1.

**What happens internally?** SwiftUI associates the route type with a destination builder. When a route becomes active, SwiftUI can construct the appropriate destination view. The route acts as a typed description of navigation intent.

## 7. Programmatic navigation — append a route

To navigate to Payment: `path.append(.payment)`. To navigate to History: `path.append(.history)`. To navigate to Success: `path.append(.success(transactionID: id))`. To go back one destination: `path.removeLast()`. To return to the dashboard: `path.removeAll()`.

**Important safety detail.** Don't call `removeLast()` on an empty array. Use a guard when necessary:

```swift
if !path.isEmpty {
    path.removeLast()
}
```

## 8. What is NavigationPath?

We've used `@State private var path: [NPayRoute] = []`. SwiftUI also provides NavigationPath: `@State private var path = NavigationPath()`. NavigationPath can hold heterogeneous Hashable route values. For example, a path might contain different kinds of destination identifiers.

| Typed array | NavigationPath |
|---|---|
| [NPayRoute] | Type-erased path |
| One route type | Can hold multiple Hashable types |
| Strong compile-time route modeling | More flexible heterogeneous routing |
| Simple switch-based destination handling | Type-specific destination registrations |
| Good for our NPay example | Useful for more heterogeneous navigation |

Our recommendation for NPay: use `[NPayRoute]` for now. It's easier to reason about and keeps our route model explicit.

## 9. Build the Payment Success screen

Create PaymentSuccessScreen.swift.

```swift
import SwiftUI

struct PaymentSuccessScreen: View {
    let transactionID: UUID
    let onDone: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 72))
                .foregroundStyle(.green)

            Text("Payment Recorded")
                .font(.title.bold())

            Text("Your demo payment was successful.")
                .foregroundStyle(.secondary)

            Text(transactionID.uuidString)
                .font(.caption2.monospaced())
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            Button("Back to Dashboard") {
                onDone()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .navigationTitle("Payment Success")
        .navigationBarBackButtonHidden()
    }
}
```

The success screen receives a transaction ID and a closure to return home. It doesn't own the application's navigation path. The parent remains responsible for navigation state.

## 10. Connect payment success to navigation

Our existing sendDemoPayment method returns Bool. But now we want the transaction ID. Let's improve the contract:

```swift
private func sendDemoPayment(
    to recipient: String,
    amountPaise: Int
) -> UUID? {

    let trimmed = recipient.trimmingCharacters(
        in: .whitespacesAndNewlines
    )

    guard !trimmed.isEmpty,
          amountPaise > 0,
          amountPaise <= balancePaise else {
        return nil
    }

    let transactionID = UUID()

    balancePaise -= amountPaise

    transactions.insert(
        Transaction(
            id: transactionID,
            title: "Sent to \(trimmed)",
            amountPaise: -amountPaise,
            date: .now
        ),
        at: 0
    )

    return transactionID
}
```

Now a successful local payment produces a transaction ID. The navigation flow can use it:

```swift
if let id = sendDemoPayment(
    to: recipient,
    amountPaise: amountPaise
) {
    path.append(.success(transactionID: id))
}
```

**Why is this design better?** Payment processing returns a meaningful result. Navigation responds to that result. The payment logic doesn't need to know about SwiftUI screens.

## 11. How does the PaymentScreen communicate success?

Update the action contract: `let onSend: (String, Int) -> UUID?`. Then inside the Send button:

```swift
Button("Send Demo Payment") {
    guard let amount = parsedAmount else {
        return
    }

    if let transactionID = onSend(
        recipient,
        amount
    ) {
        focusedField = nil
        onPaymentSuccess(transactionID)
    }
}
```

Add another closure: `let onPaymentSuccess: (UUID) -> Void`. The parent supplies navigation behavior.

[Conceptually: PaymentScreen (collects user input) → onSend (requests demo payment) → ContentView (validates and records transaction) → Transaction ID (returned on success) → onPaymentSuccess (requests navigation) → NavigationStack (displays success destination).]

## 12. Behind the scenes — navigation is state

Let's connect navigation to Lesson 2.8. We learned UI = f(State). Navigation follows the same principle: Visible Destination = f(Navigation Path). When path changes, SwiftUI updates the navigation presentation. The application isn't directly pushing a UIKit view controller. Instead, it changes declarative navigation state. SwiftUI handles the corresponding transition.

## 13. Xcode experiments

Run these in your NPay project:
1. Start with an empty path and navigate to Payment.
2. After a successful demo payment, append the success route.
3. Print the path after each navigation action.
4. Use `path.removeAll()` to return to Dashboard.
5. Attempt to append two routes sequentially and observe the navigation behavior.
6. Compare `[NPayRoute]` with NavigationPath.

**Debugging tip.** You can observe changes:

```swift
.onChange(of: path) { oldPath, newPath in
    print("Old path:", oldPath)
    print("New path:", newPath)
}
```

This is useful for understanding how navigation state evolves.

## 14. Senior engineer knowledge check

1. What is a typed navigation route? (A Swift type representing a destination / A network URL / A UIKit thread)
2. Why does NPayRoute conform to Hashable? (To support navigation path values / To enable HTTP requests / To create animations)
3. What does `path.append(.payment)` do? (Adds a navigation destination / Starts a new process / Creates a database record)
4. What does `path.removeAll()` represent? (Return to root / Delete all transactions / Terminate the app)
5. Why return a transaction ID from payment logic? (To identify the successful transaction / To increase the balance / To create a thread)
6. Does NavigationPath require every element to have the same concrete type? (Yes / No)

**Lesson 3.2 checkpoint.** We've learned typed route enums, Hashable navigation values, `[NPayRoute]`, NavigationPath, navigationDestination, and programmatic push/pop navigation. Our next practical milestone is to integrate the complete route-based flow into NPay's existing Xcode project, preserving all the working Unit 2 features.

Next — Lesson 3.3: TabView and Multi-Tab Navigation, where we'll build Home, Payments, History, and Profile tabs while keeping navigation state and shared account data consistent.

## Q&A: don't we have a routing module here?

Yes, SwiftUI has a built-in navigation system, but it doesn't have a separate routing module like Angular Router or React Router. In iOS, navigation is handled primarily through the SwiftUI framework.

### 1. Routing comparison

| Framework | Routing mechanism |
|---|---|
| Angular | Angular Router |
| React | React Router (external library) |
| Flutter | Navigator / Router |
| SwiftUI | NavigationStack + navigationDestination |
| UIKit | UINavigationController |

In SwiftUI, we write `import SwiftUI`. No separate router package is required.

### 2. Does SwiftUI have a Router class?

Not a built-in application-level Router class. SwiftUI provides the navigation primitives. We can build our own Router to centralize navigation. For example, in NPay:

```swift
enum NPayRoute: Hashable {
    case payment
    case history
    case success(UUID)
}
```

Then create a router:

```swift
import SwiftUI

@MainActor
@Observable
final class NPayRouter {

    var path: [NPayRoute] = []

    func push(_ route: NPayRoute) {
        path.append(route)
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func popToRoot() {
        path.removeAll()
    }
}
```

This uses Apple's Observation framework, available on iOS 17 and later.

### 3. How do we connect it to NavigationStack?

```swift
import SwiftUI

struct ContentView: View {

    @State private var router = NPayRouter()

    var body: some View {
        @Bindable var router = router

        NavigationStack(path: $router.path) {
            VStack(spacing: 20) {

                Button("Send Money") {
                    router.push(.payment)
                }

                Button("History") {
                    router.push(.history)
                }
            }
            .navigationDestination(for: NPayRoute.self) { route in
                switch route {
                case .payment:
                    Text("Payment Screen")

                case .history:
                    Text("History Screen")

                case .success(let id):
                    Text("Payment Success: \(id.uuidString)")
                }
            }
        }
    }
}
```

### 4. Architecture behind the scenes

[NPay View (user taps Send Money) → NPayRouter (push(.payment)) → Navigation Path (stores [.payment]) → NavigationStack (observes the bound path) → navigationDestination (resolves .payment to PaymentScreen).]

### 5. Should we introduce a Router in NPay?

Yes, as the application grows. But it's important to understand the native navigation primitives first. For NPay, I'd introduce a NPayRouter when we begin coordinating navigation across multiple screens and tabs. Our architecture would eventually look like:

```
NPayApp
   |
   +-- NPayRouter
   |      |
   |      +-- NavigationStack
   |      +-- NavigationPath
   |      +-- Route resolution
   |
   +-- Features
          +-- Dashboard
          +-- Payments
          +-- History
          +-- Profile
```

One important distinction: the router manages where the user goes, not payment processing or business logic. We'll use native NavigationStack underneath, with our own router abstraction on top. That will prepare NPay for larger-scale iOS architecture without introducing unnecessary dependencies.

## Complete project through 3.2 (note from the text)

[The text offered "NPay — Complete Project Through 3.2" as a ZIP (NPayApp.swift, ContentView.swift, a README and an XcodeGen configuration) with a feature table: dashboard, balance editor, payment form, transactions, NavigationStack and typed routes, route array and navigationDestination, a payment success screen with transaction ID, return to dashboard by clearing the path. Practical test: send ₹1,500.50 to ravi@npay; ₹25,000.00 − ₹1,500.50 = ₹23,499.50; NPay navigates to the confirmation screen; returning to the dashboard shows the updated balance and History contains the new transaction. The note said the ZIP had not been compiled. The ZIP itself was not shared; the code below replaces it.]

## Complete code through Lesson 3.2 (authored)

Assembled from the text's Sections 3, 6, 9, 10, 11 and 13 onto the Lesson 3.1 complete code, and run unchanged in the
simulator (`tools/sim3_2/App.swift`). Unchanged from 3.1: NPayApp.swift, Models/Money.swift, Models/Transaction.swift,
Components/BalanceCard.swift, Components/BalanceEditor.swift, Components/TransactionRow.swift,
Screens/HistoryScreen.swift (see `../lesson-3.1/lesson-3.1-text.md`).

```
NPay/
├── NPayApp.swift
├── ContentView.swift                 changed: path, destinations, sendDemoPayment → UUID?
├── Navigation/
│   └── NPayRoute.swift                new
├── Models/            Money.swift, Transaction.swift
├── Components/        BalanceCard.swift, BalanceEditor.swift, TransactionRow.swift
└── Screens/
    ├── PaymentScreen.swift            changed: onSend → UUID?, onPaymentSuccess; alert removed
    ├── PaymentSuccessScreen.swift     new (Section 9)
    └── HistoryScreen.swift
```

### Navigation/NPayRoute.swift

```swift
import Foundation

enum NPayRoute: Hashable {
    case payment
    case history
    case success(transactionID: UUID)
}
```

### Screens/PaymentScreen.swift

```swift
import SwiftUI

struct PaymentScreen: View {
    let availableBalancePaise: Int
    let onSend: (String, Int) -> UUID?
    let onPaymentSuccess: (UUID) -> Void

    @State private var recipient = ""
    @State private var amountText = ""

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    private var parsedAmount: Int? {
        Money.parsePaise(amountText)
    }

    private var isValid: Bool {
        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              let amount = parsedAmount else {
            return false
        }

        return amount > 0
            && amount <= availableBalancePaise
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text("Send Money")
                    .font(.title.bold())

                Text(
                    "Available: \(Money.display(availableBalancePaise))"
                )
                .foregroundStyle(.secondary)

                TextField(
                    "Recipient ID",
                    text: $recipient
                )
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .recipient
                )
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .amount
                }

                TextField(
                    "Amount (₹)",
                    text: $amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )

                if !amountText.isEmpty && !isValid {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                Button("Send Demo Payment") {
                    guard let amount = parsedAmount else {
                        return
                    }

                    if let transactionID = onSend(
                        recipient,
                        amount
                    ) {
                        focusedField = nil
                        onPaymentSuccess(transactionID)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isValid)
            }
            .padding()
        }
        .navigationTitle("Send Money")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()

                Button("Done") {
                    focusedField = nil
                }
            }
        }
    }
}
```

### Screens/PaymentSuccessScreen.swift

```swift
import SwiftUI

struct PaymentSuccessScreen: View {
    let transactionID: UUID
    let onDone: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 72))
                .foregroundStyle(.green)

            Text("Payment Recorded")
                .font(.title.bold())

            Text("Your demo payment was successful.")
                .foregroundStyle(.secondary)

            Text(transactionID.uuidString)
                .font(.caption2.monospaced())
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            Button("Back to Dashboard") {
                onDone()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .navigationTitle("Payment Success")
        .navigationBarBackButtonHidden()
    }
}
```

### ContentView.swift

```swift
import SwiftUI

struct ContentView: View {

    @State private var balancePaise = 2_500_000

    @State private var path: [NPayRoute] = []

    @State private var transactions: [Transaction] = [
        Transaction(
            id: UUID(),
            title: "Coffee Shop",
            amountPaise: -25_000,
            date: .now
        ),
        Transaction(
            id: UUID(),
            title: "Electricity Bill",
            amountPaise: -120_000,
            date: .now
        ),
        Transaction(
            id: UUID(),
            title: "Salary Credit",
            amountPaise: 4_500_000,
            date: .now
        )
    ]

    var body: some View {
        NavigationStack(path: $path) {
            ScrollView {
                VStack(spacing: 24) {

                    Image(systemName: "creditcard.fill")
                        .font(.system(size: 48))
                        .foregroundStyle(.blue)

                    Text("NPay")
                        .font(.largeTitle.bold())
                        .foregroundStyle(.blue)

                    Text("Payments made simple")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)

                    BalanceCard(
                        balancePaise: balancePaise
                    )

                    BalanceEditor(
                        balancePaise: $balancePaise
                    )

                    // Navigate to payment screen

                    Button {
                        path.append(.payment)
                    } label: {
                        Label(
                            "Send Money",
                            systemImage: "arrow.up.right"
                        )
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            Color.blue.opacity(0.1),
                            in: RoundedRectangle(cornerRadius: 12)
                        )
                    }

                    // Navigate to history screen

                    Button {
                        path.append(.history)
                    } label: {
                        Label(
                            "Transaction History",
                            systemImage: "clock"
                        )
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(
                            Color.blue.opacity(0.1),
                            in: RoundedRectangle(cornerRadius: 12)
                        )
                    }

                    // Dashboard recent transactions

                    VStack(alignment: .leading, spacing: 12) {
                        Text("Recent Transactions")
                            .font(.headline)

                        ForEach(transactions.prefix(3)) { transaction in
                            TransactionRow(
                                transaction: transaction
                            )

                            Divider()
                        }
                    }
                    .frame(
                        maxWidth: .infinity,
                        alignment: .leading
                    )
                }
                .padding()
            }
            .navigationTitle("NPay")
            .navigationDestination(for: NPayRoute.self) { route in
                switch route {
                case .payment:
                    PaymentScreen(
                        availableBalancePaise: balancePaise,
                        onSend: sendDemoPayment,
                        onPaymentSuccess: { transactionID in
                            path.append(.success(transactionID: transactionID))
                        }
                    )

                case .history:
                    HistoryScreen(
                        transactions: transactions
                    )

                case .success(let transactionID):
                    PaymentSuccessScreen(
                        transactionID: transactionID,
                        onDone: {
                            path.removeAll()
                        }
                    )
                }
            }
        }
        // Debugging (Section 13): watch the navigation state evolve
        .onChange(of: path) { oldPath, newPath in
            print("Old path:", oldPath)
            print("New path:", newPath)
        }
    }

    // MARK: - Demo Payment

    private func sendDemoPayment(
        to recipient: String,
        amountPaise: Int
    ) -> UUID? {

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              amountPaise > 0,
              amountPaise <= balancePaise else {
            return nil
        }

        let transactionID = UUID()

        balancePaise -= amountPaise

        transactions.insert(
            Transaction(
                id: transactionID,
                title: "Sent to \(trimmed)",
                amountPaise: -amountPaise,
                date: .now
            ),
            at: 0
        )

        return transactionID
    }
}

#Preview {
    ContentView()
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_2.py`, 48 slides) follows all three pieces, grouped into 8 Parts: the new
requirement (intro, 1), navigation as state (2, 3), the navigation path (4, 5, 7, 13), register destinations (6),
NavigationPath (8), the payment success flow (9–11 and the complete code), navigation is state (12, 13), do we need a
router? (Q&A 1–5); then recap, review, next, lab, end. Section 5's interactive explorer is replaced by a real one.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_2/`, rerun with `sh tools/sim3_2/run.sh`; compiled with
`-module-name NPay` so printed routes read `NPay.NPayRoute…`; buttons through accessibility, Back by popping the hosting
navigation controller, as in 3.1)
- The practical test, run: ₹25,000.00 → ₹1,500.50 to ravi@npay → path `[.payment]` → `[.payment, .success(transactionID:
  DFE60279-…)]` with no tap → Back to Dashboard: `[]`, ₹23,499.50 → History: "Sent to ravi@npay", -₹1,500.50 on top.
  Screenshots of each step; the success screen has no back button.
- Path explorer (a lab screen + Section 13's `onChange`): Open Payment, Show success, Home, two appends in one action
  (one change, lands on History at depth 2), system Back (the stack wrote `[.payment]` back into the array), guarded pops.
- Section 12, authored experiment: a path that starts as `[.payment, .history]` launches straight into History; Back
  prints `[.payment]`.
- NavigationPath (authored experiment): a route, `42` and `"ravi@npay"` with destinations for the route and `Int` only:
  count 3; the String shows a yellow warning symbol; after Back, "Int destination #42". Interface excerpt (count,
  isEmpty, codable, append, `removeLast(_:)`; no `removeAll`, no element access) from the iOS 26.5 SDK.
- The Q&A's router code run unchanged (`ContentView` renamed `RouterContentView`): Send Money pushed "Payment Screen".
- Mac runs: route arrays printed; route equality (same ID true, different ID false); the guarded pop on `[]` does
  nothing and the unguarded one traps with "Can't remove last element from an empty collection".
- swiftc: without `Hashable` (and with the UUID case), "no exact matches in call to initializer … requires that
  'NPayRoute' conform to 'Hashable'" and the `navigationDestination(for:destination:)` error. Without the UUID case it
  compiles (simple enums are Hashable automatically; noted on the slide).

**Authored (flagged)**
- The complete code through 3.2 (above) and the "wire it up" and project slides; the dashboard's links became buttons
  that `append` routes, as in the text's Section 7 and Q&A.
- The experiments listed above (launch with a path, mixed NavigationPath, the path lab), the Section 13 results table,
  and the "Hashable is required" slide.
- Section 11's chain shown as a stepped diagram, marked conceptual.
- Review: the text's 6 questions (options reordered so answers vary) plus two predict items (system Back; `removeLast` on
  `[]`) and a spaced item from 3.1; 2 of 9 verdicts are "No".
- Outcomes, "Where we are" (strip now names 3.3 TabView, from this text), recap, "Where this goes next" (3.3 from the
  text; the router "later", when navigation spans tabs, as the Q&A says; Unit 4), lab, end slide.

**Wording**
- "Senior engineer knowledge check" became "Check your understanding". The Q&A's first-person advice ("I'd introduce…")
  became neutral.
