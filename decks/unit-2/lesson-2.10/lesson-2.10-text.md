# Unit 2 · Lesson 2.10 — ForEach, List & Collection Identity

> Lesson text as shared, in three pieces: Part 1 (Sections 1–14, cut off in Section 14), "Part 2: Collection Updates,
> Identity & NPay Integration" (Sections 14–23), and "Complete Working Code" (the full ContentView.swift with a test
> table and architecture). Interactive widgets are described in brackets. The deck (`index.html`, built by
> `tools/gen2_10.py`) follows Sections 1–23. Simulator evidence and authored additions are listed at the end under
> "Deck changes".

NPay Engineering Lab · Incremental Development · Swift Collections → Identifiable → SwiftUI Identity → Rendering

Our NPay application can now display and edit a demo balance using @State and @Binding. But a payment application needs something more important: transaction history. Today we'll introduce SwiftUI's collection rendering system and investigate how it efficiently manages changing lists of views.

Our central engineering question: **When NPay displays 100 transactions, how does SwiftUI know which transaction is which—and what happens when one transaction is inserted, removed, or updated?**

We'll learn ForEach, List, Identifiable, stable identity, and collection updates while building NPay's first transaction history.

## 1. Our next NPay milestone

[Mock-up: the balance card, then "Recent Transactions — View all": Coffee Shop (Today, −₹250), Electricity Bill (Yesterday, −₹1,200), Salary Credit (22 Oct, +₹45,000).] **Milestone 2.10 — Transaction history using mock data.** We'll start with a simple collection and progressively make it dynamic.

## 2. First experiment — display a Swift array

```swift
let transactions = [
    "Coffee Shop",
    "Electricity Bill",
    "Salary Credit"
]
```

Can we write `VStack { for transaction in transactions { Text(transaction) } }`? No. A normal for statement isn't directly supported as a child-view-producing statement inside ViewBuilder in this way. Instead, SwiftUI provides ForEach.

```swift
VStack {
    ForEach(transactions, id: \.self) { transaction in
        Text(transaction)
    }
}
```

This creates a view description for each collection element.

**Why id: \.self?** SwiftUI needs an identity for each element. For unique strings, the string value itself can serve as the identity. But this approach becomes problematic when values are duplicated or mutable. We'll investigate that shortly.

## 3. What exactly is ForEach?

ForEach is a generic SwiftUI struct conforming to View. It takes a collection and a closure that produces view content for each element. Conceptually:

```swift
// Simplified conceptual signature

struct ForEach<Data, ID, Content>: View
where Data: RandomAccessCollection,
      ID: Hashable,
      Content: View {
    // ...
}
```

Three generic types: Data — the collection; ID — the identity type; Content — the view produced for each element.

**Connect to Unit 1.** Remember generic functions: `func printValue<T>(_ value: T) { print(value) }`. ForEach uses the same generic type-system capabilities, but applies them to declarative UI construction.

**Important distinction.** ForEach is not merely a normal Swift for loop. It is a SwiftUI view that represents a collection of child views and their identities.

## 4. Behind the scenes — how ForEach creates child views

`ForEach(transactions, id: \.self) { transaction in Text(transaction) }` — the trailing closure receives one element and produces a view description. [ForEach view construction: Swift array (contains transaction values) → ForEach (associates elements with stable identities) → content closure (produces Text(transaction) for each element) → SwiftUI collection hierarchy (tracks child views and their identities) → layout and rendering.] Conceptual pipeline. SwiftUI may evaluate content closures selectively, depending on container and update behavior.

## 5. Build our first Transaction model

```swift
struct Transaction {
    let id: UUID
    let title: String
    let amount: Int
    let date: String
}
```

(Mock data: three `Transaction(id: UUID(), …)` values — Coffee Shop −250 Today; Electricity Bill −1200 Yesterday; Salary Credit 45000 22 Oct.)

**Why does each transaction need an ID?** Because two transactions may have the same title, amount, and date. Identity should represent the transaction itself, not merely its displayed content.

## 6. Introducing Identifiable

Swift provides an Identifiable protocol. A type conforming to Identifiable exposes an id property. Update our model: `struct Transaction: Identifiable { … }`. Now SwiftUI can use each transaction's id as its identity: `ForEach(transactions) { transaction in Text(transaction.title) }`. We no longer need to explicitly write `id: \.id` because Transaction conforms to Identifiable.

**Trainer question.** Does Identifiable automatically create a UUID for every instance? No. The model must provide a suitable identity value. Some types can synthesize or inherit IDs through other mechanisms, but our struct explicitly stores one.

## 7. Stable identity — one of SwiftUI's deepest concepts

Imagine NPay receives updated transaction data from an API. The first response contains TXN-101 Coffee Shop, TXN-102 Electricity Bill, TXN-103 Salary Credit. Now a new transaction arrives: TXN-104 Mobile Recharge (new), then TXN-101, TXN-102, TXN-103. SwiftUI can use stable IDs to understand that one element was inserted while the existing elements retain their identities.

**Important nuance.** We shouldn't claim that SwiftUI always uses one specific public diffing algorithm. Its internal update mechanisms are not fully specified. But stable identity is a fundamental requirement for predictable collection behavior.

## 8. Interactive identity experiment

[NPay transaction collection #101 / #102 / #103 with "Insert transaction", "Remove first", "Reset" — each item retains its ID even when its position changes.] **What should you understand?** Collection position and collection identity are different. A transaction moving from index 0 to index 1 is still the same transaction if its identity remains stable.

## 9. Why is using array indices dangerous?

```swift
ForEach(transactions.indices, id: \.self) { index in
    Text(transactions[index].title)
}
```

This can work in certain cases, but it uses positions as identity. If items are inserted, removed, or reordered, positions can refer to different logical transactions. That can cause incorrect state association or unexpected animation behavior.

**Senior engineer rule.** For dynamic domain collections, prefer stable domain IDs. For NPay, transaction IDs should come from the transaction model or trusted backend rather than the current array index.

## 10. Why is generating UUID inside the ID getter dangerous?

```swift
struct Transaction: Identifiable {
    var id: UUID {
        UUID()
    }

    let title: String
}
```

Every time id is read, it returns a different UUID. That makes identity unstable. A better model: `struct Transaction: Identifiable { let id = UUID(); let title: String }`. Now each instance has a stable ID for its lifetime.

**Important production detail.** If transactions are reconstructed from an API response, use a stable backend transaction identifier. Generating a new UUID every time data is decoded can make the same logical transaction appear new on every refresh.

## 11. ForEach versus List

ForEach creates a collection of child view descriptions. It does not independently provide a scrolling list interface (`VStack { ForEach(transactions) { … } }`). List is a higher-level SwiftUI container designed for presenting collections of data (`List(transactions) { transaction in Text(transaction.title) }`). List provides platform-adaptive list behavior, including scrolling and support for features such as selection, swipe actions, and editing.

| Feature | ForEach | List |
|---|---|---|
| Role | Generates child view descriptions | Presents a list interface |
| Scrolling | Not by itself | Built in |
| Row styling | Determined by parent | List-specific styling |
| Editing support | Depends on parent | Built-in list capabilities |
| Identity | Important | Important |

**Trainer question.** Is ForEach simply a replacement for a normal Swift for loop everywhere? No. It is specifically a SwiftUI view for describing repeated child content.

## 12. Build a reusable TransactionRow

(Code: `struct TransactionRow: View { let transaction: Transaction }` — `HStack(spacing: 12)` with `Image(systemName: "creditcard")` (.title2, blue), a leading `VStack(spacing: 4)` of the title (.headline) and date (.caption, secondary), `Spacer()`, and the amount as INR currency with no fraction digits (.subheadline.bold(), green when ≥ 0 else primary); `.padding(.vertical, 8)`.)

What did we reuse? HStack for horizontal arrangement; VStack for title and date; Spacer to separate description from amount; text formatting for currency; conditional foreground styling; a custom SwiftUI view for reusable presentation.

## 13. Integrate transaction history into NPay

Define the model; add `@State private var transactions = [ … ]` mock data to ContentView; add a transaction section below the balance editor and quick actions:

```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Recent Transactions")
        .font(.headline)

    ForEach(transactions) { transaction in
        TransactionRow(transaction: transaction)

        Divider()
    }
}
```

Because our current NPay screen already uses ScrollView, we can use ForEach inside the existing vertical layout. We'll explore List separately to avoid nesting competing scrolling containers.

## 14. Behind the scenes — what happens when a transaction arrives?

Imagine we add a transaction: `transactions.insert(Transaction(id: UUID(), title: "Mobile Recharge", amount: -399, date: "Today"), at: 0)`. The state collection changes. SwiftUI recognizes that the view description depends on the collection. It can then [Part 1 cut off here; Part 2 continues:]

[Transaction update — a 6-stage stepper; only stage 1 was included: "New transaction arrives — NPay receives or creates a transaction with a stable identifier, such as TXN-104." Conceptual update flow.]

**The important distinction.** When the array changes, SwiftUI doesn't necessarily destroy and recreate every visible row. Stable identity helps the framework preserve the association between a logical transaction and its view state. However, stable identity does not guarantee that a row's body will never be reevaluated. Identity preservation and view evaluation are different concerns.

## 15. Experiment — stable ID versus array index

| Index | Transaction ID | Title |
|---|---|---|
| 0 | TXN-101 | Coffee Shop |
| 1 | TXN-102 | Electricity Bill |
| 2 | TXN-103 | Salary Credit |

Insert a transaction at the beginning: index 0 TXN-104 Mobile Recharge, 1 TXN-101 Coffee Shop, 2 TXN-102 Electricity Bill, 3 TXN-103 Salary Credit. The original Coffee Shop transaction moved from index 0 to index 1. But its identity remains TXN-101. [Interactive identity investigation: Stable transaction ID / Array index toggle; "Insert transaction at index 0".]

**Senior engineer insight.** Array indices are positions. Transaction IDs are identities. These concepts should not be confused.

## 16. Why unstable identity can cause surprising bugs

(The computed `var id: UUID { UUID() }` model again.) This is dangerous because every read of id produces a new UUID. SwiftUI may treat the same logical transaction as a different element across updates. Possible consequences include lost row-local state, unexpected transitions, and inefficient updates. Correct approach: `struct Transaction: Identifiable { let id: UUID; let title: String }` — the ID is stored and remains stable for that transaction.

**Production architecture note.** When NPay receives transactions from a backend, use the backend's stable transaction identifier. A UUID generated during every refresh is not a suitable replacement for a persistent transaction identity.

## 17. ForEach versus List — what actually changes?

```swift
ScrollView {
    VStack {
        ForEach(transactions) { transaction in
            TransactionRow(transaction: transaction)
        }
    }
}
```

This gives us control over layout, but the ordinary VStack constructs its child view descriptions eagerly as part of its layout.

```swift
List(transactions) { transaction in
    TransactionRow(transaction: transaction)
}
```

List provides platform-adaptive list behavior and manages scrolling, row presentation, and collection-related interactions. For larger collections, List or lazy containers can be more suitable than an eager VStack.

**Important distinction.** ForEach does not itself guarantee lazy loading. The surrounding container strongly influences view creation and layout behavior.

## 18. NPay practical — make transactions dynamic

Add transaction state (`@State private var transactions: [Transaction] = [ … ]`) and a button that inserts a mock transaction:

```swift
Button("Add Demo Transaction") {
    let newTransaction = Transaction(
        id: UUID(),
        title: "Mobile Recharge",
        amount: -399,
        date: "Today"
    )

    transactions.insert(newTransaction, at: 0)
}
.buttonStyle(.borderedProminent)
```

**What happens?** When the button is tapped, the array changes. SwiftUI reevaluates the relevant view descriptions. ForEach uses each transaction's stable ID to associate elements with their views. The new transaction appears at the top.

## 19. Build the transaction history component

```swift
struct TransactionHistory: View {
    let transactions: [Transaction]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Transactions")
                .font(.headline)

            ForEach(transactions) { transaction in
                TransactionRow(transaction: transaction)

                Divider()
            }
        }
    }
}
```

Then use `TransactionHistory(transactions: transactions)`. **Why use let transactions?** Because this component only displays transaction data. It doesn't need to modify the array. The parent owns the state. This is the same design principle we used with BalanceCard and BalanceEditor.

## 20. One subtle problem — why is Divider inside ForEach?

Our current code produces a row and a divider for each transaction. That means the final transaction also has a divider underneath it. For a small demo, that's acceptable. For a polished application, we might want dividers only between rows. We can handle this through indexing, row styling, or a different container. But be careful not to use array indices as the logical identity of dynamic transactions. Indexing for presentation is different from using indices as identity.

## 21. Xcode experiment — observe row updates

```swift
var body: some View {
    let _ = Self._printChanges()

    return HStack {
        Text(transaction.title)
        Spacer()
        Text("\(transaction.amount)")
    }
}
```

Run NPay. Tap Add Demo Transaction. Observe the debug console. **What should you learn?** SwiftUI may reevaluate row descriptions as collection state changes. But body evaluation doesn't necessarily mean a row was destroyed or that its pixels were completely redrawn. Use diagnostics to understand behavior rather than assuming every evaluation is a performance problem.

## 22. Senior engineer knowledge check

1. What does ForEach need to track dynamic elements? — **Stable identity** / Only array index / A separate thread
2. Does ForEach automatically provide scrolling? — Yes / **No**
3. Is a computed id that returns UUID() on every access safe? — Yes / **No**
4. Does ForEach guarantee lazy view creation? — Yes / **No**
5. Should a read-only TransactionHistory own an independent copy of mutable transaction state? — Yes / **No**
6. Does stable identity guarantee body never runs again? — Yes / **No**

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 23. Lesson 2.10 — Final NPay checkpoint

Our NPay application now has a dynamic transaction collection and a reusable transaction history component. You should be able to explain ForEach, List, Identifiable, stable IDs, collection updates, and why identity matters for SwiftUI state management. [Current architecture: ContentView (owns balance and transactions) → BalanceCard (displays balance), BalanceEditor (edits balance via Binding), QuickAction (handles action closures), TransactionHistory (displays transaction collection).]

**Next — Lesson 2.11: TextField, Input Validation & Focus Management.** We'll add a payment amount input to NPay and investigate how text input moves from the iOS keyboard through SwiftUI bindings into application state, including validation, focus, and keyboard behavior.

## Complete working code (Lessons 2.1–2.10)

(Code: the complete `ContentView.swift` — `Transaction: Identifiable`; `ContentView` with `@State balance = 25000` and `@State transactions` (three mock transactions), a `ScrollView` → `VStack(spacing: 24)` of the header, `BalanceCard(balance:)`, `BalanceEditor(balance: $balance)`, the three `QuickAction`s, an "Add Demo Transaction" button calling `addDemoTransaction()` (inserts Mobile Recharge −399 at 0) and `TransactionHistory(transactions:)`; `BalanceCard`; `BalanceEditor` (now with a pale blue rounded background); `QuickAction`; `TransactionRow`; `TransactionHistory`; `#Preview`. It runs unchanged in `tools/sim2_10/App.swift`.)

What to verify in Xcode:

| Test | Expected behavior |
|---|---|
| Add ₹1,000 | Balance increases |
| Subtract ₹1,000 | Balance decreases, minimum zero |
| Send / Request / History | Messages appear in debug console |
| Add Demo Transaction | New Mobile Recharge row appears at the top |
| Scroll | Full dashboard remains accessible |

Current architecture: ContentView (@State balance, @State transactions) → BalanceCard (let balance: Int), BalanceEditor (@Binding balance), QuickAction × 3 (action: () -> Void), TransactionHistory (ForEach(transactions) → TransactionRow).

**One important design note.** The balance editor and transaction history are independent demonstrations for now. Adding a transaction does not deduct money from the balance. We'll connect payment input, validation, and transaction behavior in subsequent lessons.

## Deck changes

The deck (`index.html`, built by `tools/gen2_10.py`, 37 slides) follows Sections 1–23 and the complete code, grouped into
8 Parts: transaction history (1), ForEach (2–4), Transaction and Identifiable (5–6), stable identity (7–8, 14–15),
when identity breaks (9–10, 15–16), ForEach vs List (11, 17), NPay's transaction history (12–13, 18–20), observe updates
and checkpoint (21, 23); then recap, review (22), next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_10/`, rerun with `sh tools/sim2_10/run.sh`;
buttons activated through accessibility; the complete code runs unchanged)
- Section 2: the real swiftc error for a `for` loop in a VStack: "closure containing control flow statement cannot be used with result builder 'ViewBuilder'".
- Section 3: SDK excerpts (`ForEach<Data, ID, Content> where Data : RandomAccessCollection, ID : Hashable`, the View conformance, the Identifiable initializer); printed `ForEach<Array<String>, String, Text>` and `ForEach<Array<Transaction>, UUID, TransactionRow>`.
- Sections 8–10, 15–16 (the explorers are replaced by one **authored** experiment): a row with its own `@State` flag; flag Coffee Shop, then insert Mobile Recharge at 0, under three identities. Stable id: the flag stays on Coffee Shop and only the new row's body ran. Indices: the flag moves to Mobile Recharge. Computed `var id: UUID { UUID() }`: the flag is lost. Screenshots of all three. On the Mac, a computed id read twice was not equal; a stored id was.
- Section 14: the 6-stage update stepper (only stage 1 shared) is drawn with **authored** stages 2–6, marked conceptual.
- Section 17: measured row bodies for 1,000 transactions: VStack in a ScrollView 1,000; LazyVStack 12; List 9.
- Section 21: `_printChanges` in a test row (named ChangesRow) printed "@self changed." ×3 at launch and ×1 for the inserted row.
- Sections 1, 18–20 and the complete code: screenshots before (2.9), scrolled to the bottom at launch, and after Add Demo Transaction.
- The TransactionRow slide joins some modifiers onto one line to fit; the full code is in the text.

**Authored (flagged)**
- Review: the text's 6 questions (answers authored; questions 2 and 4 rephrased as multiple choice to keep the No answers below half), plus a predict item (index-based flag) and a spaced item from 2.9.
- Outcomes, "Where we are", recap, "Where this goes next" (2.11 from the text), lab with expected results.
- The progress strip now has 11 lessons (2.11 named by the text); `unit1.py`'s `progress()` sizes itself to the count (Unit 01 output unchanged).

**Wording**
- "Trainer question" / "Senior engineer rule/insight" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding".
