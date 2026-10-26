# Unit 3 · Lesson 3.1 — NavigationStack: How iOS Navigation Works

> Lesson text as shared, in three pieces: Sections 1–11 (cut off at the knowledge check), "Part 2: Navigation Internals
> & Lab Completion" (Sections 11–17), and "Complete Working Code" (1–12). Interactive widgets are described in
> brackets. The deck (`index.html`, built by `tools/gen3_1.py`) follows all three. Simulator evidence and authored
> additions are listed at the end under "Deck changes".

## 1. The problem we're solving

Our Unit 2 application places everything inside one ScrollView. A user must scroll through the balance editor, quick actions, payment form, and transactions. We want a more natural experience.

[Before · Unit 2: NPay ₹25,000 — Balance Editor, Send Money Form, Transactions, all on one screen. After · Unit 3: NPay ₹25,000 — Send Money, History as separate destinations.]

The dashboard will become the starting point. Other features will live on separate screens.

## 2. First concept — NavigationStack

Let's begin with the smallest possible example. Create a new SwiftUI file named NavigationExperiment.swift:

```swift
import SwiftUI

struct NavigationExperiment: View {

    var body: some View {
        NavigationStack {
            NavigationLink("Send Money") {
                Text("NPay Payment Screen")
            }
            .navigationTitle("NPay")
        }
    }
}

#Preview {
    NavigationExperiment()
}
```

Run the preview and tap Send Money. You should navigate to a new screen.

**Understand the APIs**

| API | What it does |
|---|---|
| NavigationStack | Manages stack-based navigation |
| NavigationLink | Declares a navigation action |
| Destination closure | Provides destination view content |
| .navigationTitle() | Configures the navigation title |

**Important distinction.** NavigationStack is not a layout stack like VStack. A VStack arranges multiple children vertically. A NavigationStack manages a hierarchy of navigation destinations.

## 3. Behind the scenes — what happens when we tap?

We already studied the iOS event pipeline in Unit 0. Let's connect it to navigation.

[From tap to navigation transition — a 6-stage stepper; only Stage 1 was shared: "Touch event: iOS processes the user's interaction." Caption: "Conceptual flow; SwiftUI's private navigation implementation is not guaranteed."]

**What is actually pushed?** At the public API level, SwiftUI manages a navigation destination. You shouldn't assume it creates a new process, window, or particular UIKit view controller for every destination. The navigation takes place inside the existing NPay application.

## 4. Interactive navigation experiment

Try navigating between our NPay screens. [NPay navigation simulator: Depth: 1; Home — Available balance ₹25,000; Send Money, History.]

**What should you observe?** When we navigate to Send Money, the dashboard is no longer the visible destination. When we go Back, the dashboard returns. This is different from showing and hiding views inside a single VStack.

## 5. NavigationLink versus Button

```swift
Button("Send Money") {
    print("Send tapped")
}
```

A button represents an action. Now compare:

```swift
NavigationLink("Send Money") {
    PaymentScreen()
}
```

A navigation link declares a destination. Both are interactive, but they express different intentions.

**Why does this matter?** SwiftUI can provide navigation-specific behavior, transitions, and accessibility semantics when we use the appropriate navigation APIs. For an operation such as confirming a payment, use a button. For moving from Dashboard to PaymentScreen, use a navigation link.

## 6. Build our first real destination

Create PaymentScreen.swift:

```swift
import SwiftUI

struct PaymentScreen: View {

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "arrow.up.right.circle.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)

            Text("Send Money")
                .font(.title.bold())

            Text("NPay payment form will appear here.")
                .foregroundStyle(.secondary)
        }
        .padding()
        .navigationTitle("Send Money")
        .navigationBarTitleDisplayMode(.inline)
    }
}

#Preview {
    NavigationStack {
        PaymentScreen()
    }
}
```

**Why use a separate struct?** Because PaymentScreen represents a distinct application destination. This improves composition and prepares NPay for navigation-specific state and behavior.

## 7. Add the History destination

Create HistoryScreen.swift:

```swift
import SwiftUI

struct HistoryScreen: View {

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 64))
                .foregroundStyle(.blue)

            Text("Transaction History")
                .font(.title.bold())

            Text("NPay transaction history will appear here.")
                .foregroundStyle(.secondary)
        }
        .padding()
        .navigationTitle("History")
    }
}

#Preview {
    NavigationStack {
        HistoryScreen()
    }
}
```

We now have two independent destination views.

## 8. Integrate with our existing NPay dashboard

Our Unit 2 ContentView currently contains the balance, payment form, and transaction history. For this first navigation lab, we won't move all that functionality at once. We'll introduce the navigation container and links. Wrap the existing dashboard content:

```swift
NavigationStack {
    ScrollView {
        VStack(spacing: 24) {
            // Existing dashboard content
        }
        .padding()
    }
    .navigationTitle("NPay")
}
```

Then add:

```swift
NavigationLink {
    PaymentScreen()
} label: {
    Label(
        "Open Send Money",
        systemImage: "arrow.up.right"
    )
}

NavigationLink {
    HistoryScreen()
} label: {
    Label(
        "Open History",
        systemImage: "clock"
    )
}
```

Place these links inside the dashboard's VStack. Run NPay. Tap each link and verify that the Back navigation works.

## 9. Behind the scenes — state ownership across screens

Our existing NPay application owns:

```swift
@State private var balancePaise = 2_500_000
@State private var transactions: [Transaction] = []
```

The dashboard should remain the state owner for this stage of learning. When we later move the actual payment form to PaymentScreen, we'll pass:

```swift
PaymentScreen(
    availableBalancePaise: balancePaise,
    onSend: sendDemoPayment
)
```

Similarly, HistoryScreen will receive the transaction collection. We won't create independent balances in each screen.

[ContentView (owns balance and transactions) → PaymentScreen (receives balance and payment action), HistoryScreen (receives transaction data).]

**Senior engineer question.** What happens if PaymentScreen creates its own @State balancePaise? It becomes a separate state owner. That could cause the payment screen and dashboard to show inconsistent balances.

## 10. Xcode experiments

Complete these before advancing:
1. Open PaymentScreen and return using Back.
2. Open HistoryScreen and return using Back.
3. Add `@State private var counter = 0` to PaymentScreen and observe its lifetime when navigating away and back.
4. Command-click NavigationStack and inspect the SwiftUI API.
5. Set a breakpoint in the destination's body to investigate when SwiftUI evaluates it.

Remember that a destination view's body may be evaluated multiple times; that doesn't mean a new iOS process is created.

## Part 2: Navigation Internals & Lab Completion

NPay Engineering Lab · Continuing from Section 11. We've introduced NavigationStack, created PaymentScreen and HistoryScreen, and connected them to NPay. Let's finish the knowledge check, then investigate navigation state, view lifetime, memory, and debugging before closing Lesson 3.1.

## 11. Senior engineer knowledge check

[Navigation Engineering Assessment, 0 / 7 answered; the first piece showed questions 1–5.]
1. What does NavigationStack manage? (Vertical layout / Navigation hierarchy / Thread scheduling)
2. Does navigation create a new application process? (Yes / No)
3. Which API best expresses moving to another screen? (NavigationLink / Spacer / Text)
4. Should every destination create its own independent account balance? (Yes / No)
5. Can destination-local @State reset after the destination is popped and recreated? (Yes / No)
6. Is NavigationStack the same kind of layout container as VStack? (Yes / No)
7. Does NavigationLink necessarily create its destination's body immediately? (Yes / No)

## 12. Behind the scenes — what happens to the previous screen?

When we navigate from Dashboard to PaymentScreen, the dashboard stops being the visible destination. But that doesn't necessarily mean the dashboard's view state is destroyed. NavigationStack manages the navigation hierarchy, including the active destination and its relationship to previous destinations.

[Navigation stack state: PaymentScreen — currently visible destination; Dashboard — previous destination in navigation hierarchy.]

**Important distinction.** A view being off-screen is not the same as its state being discarded. State preservation depends on identity and navigation lifetime. SwiftUI does not guarantee that every previous screen remains as a permanently allocated UIKit view controller.

## 13. Experiment — observe destination state lifetime

Replace PaymentScreen temporarily with:

```swift
import SwiftUI

struct PaymentScreen: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Payment Screen")
                .font(.title)

            Text("Count: \(count)")
                .font(.headline)

            Button("Increment") {
                count += 1
            }
            .buttonStyle(.borderedProminent)
        }
        .navigationTitle("Payment")
    }
}
```

**Run this experiment.** Navigate to PaymentScreen. Tap Increment three times. Go Back. Navigate to PaymentScreen again. What happens to count? Typically, when the destination is popped and a new destination identity is established on the next push, the local state starts again at zero.

**Why?** Because the original destination's state lifetime ended when it was removed from the navigation hierarchy. We'll learn how to preserve drafts across navigation in Lesson 3.5.

## 14. Debugging navigation in Xcode

Set a breakpoint inside PaymentScreen.body or use `let _ = Self._printChanges()`. For example:

```swift
var body: some View {
    let _ = Self._printChanges()

    return VStack {
        Text("Payment Screen")
    }
}
```

Navigate into PaymentScreen. Observe the debug console. Navigate Back and open it again.

**What should you learn?** SwiftUI may evaluate a destination's body multiple times. Body evaluation does not necessarily mean a new process, new window, or entirely new rendering surface was created.

## 15. NavigationStack versus UINavigationController

In UIKit, navigation is commonly implemented using UINavigationController. SwiftUI offers NavigationStack as a declarative navigation abstraction.

| UIKit | SwiftUI |
|---|---|
| UINavigationController | NavigationStack |
| pushViewController | NavigationLink or path update |
| popViewController | Back navigation or path update |
| UIViewController objects | View descriptions and navigation state |
| Imperative navigation API | Declarative navigation API |

**Senior engineer insight.** SwiftUI may integrate with UIKit internally on iOS, but you should not assume a fixed one-to-one mapping between SwiftUI destinations and UIKit view controllers. Use the public navigation APIs unless you have a specific interoperability requirement.

## 16. What happens to memory when navigating?

Let's connect this to Unit 0 and Unit 1. When a destination appears, it may create state, load resources, or reference services. When it disappears, some resources may become eligible for release. But disappearing from the screen is not a guarantee of immediate deallocation. SwiftUI manages view lifetime and state according to its hierarchy. ARC manages the lifetime of referenced class instances.

**Example.** If PaymentScreen creates a reference-type service and a closure retains that service, its lifetime depends on the actual ownership relationships. This is why we must understand closure capture and reference cycles. We'll investigate these issues more deeply when we introduce ViewModels.

## 17. Final NPay architecture for Lesson 3.1

[NPayApp — application entry point → NavigationStack — navigation container → ContentView / Dashboard — owns NPay demo state → PaymentScreen — destination; HistoryScreen — destination.]

**Lesson 3.1 complete.** We've covered NavigationStack, NavigationLink, destination creation, navigation hierarchy, view identity, state lifetime, UIKit comparisons, memory considerations, and Xcode debugging. Our NPay application can now navigate from the dashboard to two placeholder destinations.

Next — Lesson 3.2: Typed Routes & Programmatic Navigation. We'll replace simple destination links with a typed route model, learn how NavigationPath and navigationDestination work, and implement navigation to a payment confirmation screen after a successful simulated payment.

## NPay — Unit 3, Lesson 3.1: Complete Working Code

Goal: Convert our Unit 2 single-screen NPay application into a multi-screen application using NavigationStack and NavigationLink. We'll preserve the working demo balance, balance editor, payment simulation, and transaction history. The main change is that Send Money and History move to separate screens.

### 1. Xcode project structure

```
NPay/
├── NPayApp.swift
├── ContentView.swift
├── Models/
│   ├── Money.swift
│   └── Transaction.swift
├── Components/
│   ├── BalanceCard.swift
│   ├── BalanceEditor.swift
│   └── TransactionRow.swift
└── Screens/
    ├── PaymentScreen.swift
    └── HistoryScreen.swift
```

You can use Xcode's New File → Swift File. The folders are organizational; ensure each source file belongs to the NPay target. Remove or replace duplicate type definitions from the old ContentView.swift.

### 2. NPayApp.swift

Our application entry point stays simple.

```swift
import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

### 3. Models/Money.swift

We continue using integer paise for money calculations.

```swift
import Foundation

enum Money {
    static func display(_ paise: Int) -> String {
        let value = Decimal(paise) / Decimal(100)

        return value.formatted(
            .currency(code: "INR")
                .locale(Locale(identifier: "en_IN"))
        )
    }

    static func parsePaise(_ text: String) -> Int? {
        let pattern = #"^[0-9]+(\.[0-9]{1,2})?$"#

        guard text.range(
            of: pattern,
            options: .regularExpression
        ) != nil else {
            return nil
        }

        let parts = text.split(
            separator: ".",
            omittingEmptySubsequences: false
        )

        guard let rupees = Int(parts[0]) else {
            return nil
        }

        let fraction = parts.count > 1
            ? String(parts[1])
            : ""

        let padded = fraction.padding(
            toLength: 2,
            withPad: "0",
            startingAt: 0
        )

        guard let paise = Int(padded) else {
            return nil
        }

        let (rupeePaise, overflow1) =
            rupees.multipliedReportingOverflow(by: 100)

        guard !overflow1 else {
            return nil
        }

        let (total, overflow2) =
            rupeePaise.addingReportingOverflow(paise)

        guard !overflow2 else {
            return nil
        }

        return total
    }
}
```

### 4. Models/Transaction.swift

```swift
import Foundation

struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}
```

### 5. Components/BalanceCard.swift

```swift
import SwiftUI

struct BalanceCard: View {
    let balancePaise: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Available Balance")
                .font(.subheadline)

            Text(Money.display(balancePaise))
                .font(.largeTitle.bold())

            Text("NPay Demo Account")
                .font(.caption)
        }
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(24)
        .background(
            .blue,
            in: RoundedRectangle(cornerRadius: 20)
        )
    }
}
```

### 6. Components/BalanceEditor.swift

```swift
import SwiftUI

struct BalanceEditor: View {
    @Binding var balancePaise: Int

    var body: some View {
        VStack(spacing: 12) {
            Text("Demo Balance Editor")
                .font(.headline)

            HStack(spacing: 12) {
                Button("− ₹1,000") {
                    balancePaise = max(
                        0,
                        balancePaise - 100_000
                    )
                }
                .buttonStyle(.bordered)

                Button("+ ₹1,000") {
                    let (next, overflow) =
                        balancePaise.addingReportingOverflow(100_000)

                    if !overflow {
                        balancePaise = next
                    }
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
        .background(
            Color.blue.opacity(0.06),
            in: RoundedRectangle(cornerRadius: 16)
        )
    }
}
```

### 7. Components/TransactionRow.swift

```swift
import SwiftUI

struct TransactionRow: View {
    let transaction: Transaction

    var body: some View {
        HStack(spacing: 12) {
            Image(
                systemName: transaction.amountPaise >= 0
                    ? "arrow.down.left"
                    : "arrow.up.right"
            )
            .font(.title2)
            .foregroundStyle(
                transaction.amountPaise >= 0
                    ? Color.green
                    : Color.blue
            )

            VStack(alignment: .leading, spacing: 4) {
                Text(transaction.title)
                    .font(.headline)

                Text(
                    transaction.date,
                    format: .dateTime
                        .day()
                        .month(.abbreviated)
                )
                .font(.caption)
                .foregroundStyle(.secondary)
            }

            Spacer()

            Text(Money.display(transaction.amountPaise))
                .font(.subheadline.bold())
                .foregroundStyle(
                    transaction.amountPaise >= 0
                        ? Color.green
                        : Color.primary
                )
        }
        .padding(.vertical, 8)
    }
}
```

### 8. Screens/PaymentScreen.swift

This is our first real navigation destination. It receives the current balance and a payment action from the dashboard.

```swift
import SwiftUI

struct PaymentScreen: View {
    let availableBalancePaise: Int
    let onSend: (String, Int) -> Bool

    @State private var recipient = ""
    @State private var amountText = ""
    @State private var showSuccess = false

    @FocusState private var focusedField: Field?

    @Environment(\.dismiss) private var dismiss

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

                    let succeeded = onSend(
                        recipient,
                        amount
                    )

                    if succeeded {
                        focusedField = nil
                        showSuccess = true
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isValid)
            }
            .padding()
        }
        .navigationTitle("Send Money")
        .navigationBarTitleDisplayMode(.inline)
        .alert("Demo Payment Successful", isPresented: $showSuccess) {
            Button("Done") {
                dismiss()
            }
        } message: {
            Text("Your simulated payment was recorded.")
        }
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

New concept: `@Environment(\.dismiss)` lets a destination request dismissal. The alert provides basic feedback; we'll study sheets and alerts in Lesson 3.4.

### 9. Screens/HistoryScreen.swift

This screen receives the same transaction data owned by ContentView.

```swift
import SwiftUI

struct HistoryScreen: View {
    let transactions: [Transaction]

    var body: some View {
        List(transactions) { transaction in
            TransactionRow(transaction: transaction)
        }
        .navigationTitle("History")
    }
}
```

Notice that we're using List instead of manually building a ScrollView and ForEach. We already learned both in Unit 2.

### 10. ContentView.swift — Main dashboard

This is where everything comes together.

```swift
import SwiftUI

struct ContentView: View {

    @State private var balancePaise = 2_500_000

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
        NavigationStack {
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

                    NavigationLink {
                        PaymentScreen(
                            availableBalancePaise: balancePaise,
                            onSend: sendDemoPayment
                        )
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

                    NavigationLink {
                        HistoryScreen(
                            transactions: transactions
                        )
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
        }
    }

    // MARK: - Demo Payment

    private func sendDemoPayment(
        to recipient: String,
        amountPaise: Int
    ) -> Bool {

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty,
              amountPaise > 0,
              amountPaise <= balancePaise else {
            return false
        }

        balancePaise -= amountPaise

        transactions.insert(
            Transaction(
                id: UUID(),
                title: "Sent to \(trimmed)",
                amountPaise: -amountPaise,
                date: .now
            ),
            at: 0
        )

        return true
    }
}

#Preview {
    ContentView()
}
```

### 11. Expected NPay screens

[Dashboard: NPay, Balance ₹25,000, Send Money →, History →, Recent transactions. Payment: ‹ NPay, Send Money, Available ₹25,000, Recipient ID, Amount (₹), Send Demo. History: ‹ NPay, History, Coffee Shop, Electricity Bill, Salary Credit.]

### 12. Xcode verification checklist

[Lesson 3.1 practical verification, 0 / 8]
- [ ] NPay launches to the dashboard
- [ ] Send Money opens PaymentScreen
- [ ] Back returns to the dashboard
- [ ] A valid demo payment reduces the balance
- [ ] Successful payment appears in recent transactions
- [ ] HistoryScreen displays the same transaction collection
- [ ] Invalid payment amounts cannot be submitted
- [ ] Balance editor updates the shared demo balance

**What we've achieved.** Our NPay application now has three real screens sharing the same logical demo state. We've retained the payment simulation while introducing NavigationStack, NavigationLink, and destination views.

One design limitation remains intentional: ContentView still owns the payment and transaction state. In Unit 4, we'll move that responsibility into a dedicated application architecture.

Next: Lesson 3.2 — Typed Routes, NavigationPath, and Programmatic Navigation. We'll learn how to control navigation through state rather than relying only on NavigationLink destination closures.

## Deck changes

The deck (`index.html`, built by `tools/gen3_1.py`, 44 slides) follows all three pieces, grouped into 8 Parts: the problem
(1), NavigationStack & NavigationLink (2, 5), behind the tap (3, 12), build the destinations (6–8), state across screens
(9), destination lifetime (10, 13, 14), UIKit and memory (15, 16), NPay after Lesson 3.1 (17 and the complete code); then
recap, review, next, lab, end. Section 4's interactive simulator is replaced by the real screens; Section 11's questions
are in the review.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_1/`, rerun with `sh tools/sim3_1/run.sh`; the
NavigationExperiment and the complete code run unchanged)
- Links and buttons are activated through accessibility; fields are focused and typed into as in 2.11. Two driver details:
  the back button and the alert's buttons don't respond to accessibility activation in the simulator, so Back pops the
  navigation controller that hosts the stack (what the back button does), and the alert's Done runs its action handler
  (so the lesson's `dismiss()` really runs). Stated in `App.swift`, not on slides.
- NavigationExperiment: launch and after Send Money (screenshots).
- The 8-item checklist, every item run: ₹25,000.00 → ₹23,500.00 after ravi@npay ₹1,500; "Sent to ravi@npay" in recent
  transactions and on top of History; 0, 12.345 and 25000.01 keep Send disabled; + ₹1,000 gives ₹24,500.00 on the
  dashboard and on the payment screen. Screenshots: dashboard, Send Money, History (before/after), the alert, back on
  the dashboard after Done. The "before" picture is Lesson 2.12's starting screen.
- While the alert was up, the still-pushed PaymentScreen already read "Available: ₹23,500.00" (destinations receive the
  owner's current value).
- Section 13 counter (the type renamed `CounterPaymentScreen` for the run): Count: 3 → Back → push → Count: 0.
- Section 14 trace: `PaymentScreen.init` printed when the dashboard's body ran, before any tap; `_printChanges` and body
  only on each push; no new init on the second push. The SDK's `NavigationLink.init(destination:label:)` calls
  `destination()` immediately (interface excerpt). Same pid and one window on both screens.
- Command-click: `NavigationStack<Data, Root>` with `init(root:)` (Data == NavigationPath) and `init(path:root:)` from
  the iOS 26.5 SDK interface (simplified).

**Authored (flagged)**
- Section 3's stages 2–6 (only stage 1 shared), marked conceptual with the text's caption.
- Section 9's question run as an experiment (`OwnBalancePaymentScreen`, a second `@State` owner): ₹23,500.00 on the
  payment screen, ₹25,000.00 back on the dashboard.
- Section 16 experiment (`DemoPaymentService` kept in a destination's `@State`): init on push, deinit right after Back,
  presented as "here", not a guarantee.
- The "Xcode experiments" slide (Section 10) with a results column from the runs above.
- Review: the text's 7 questions plus a predict item (the counter) and a spaced item from 2.9; 4 of 9 verdicts are "No".
- Outcomes, "Where we are" (a Unit 03 strip naming only 3.1 and 3.2; the other slots stay blank until their texts
  arrive, since the texts differ from the curriculum plan), recap, "Where this goes next" (3.2, 3.4, 3.5 and Unit 4 as
  the text names them), lab, end slide.
- Slide code is condensed in places (PaymentScreen's body as a comment, Label arguments wrapped) and typechecks; the
  full code is above and in `App.swift`.

**Wording**
- "Senior engineer question / insight / checkpoint" became neutral callouts and "Check your understanding".
