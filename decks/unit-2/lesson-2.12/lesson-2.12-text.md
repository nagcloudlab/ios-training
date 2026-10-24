# Unit 2 · Lesson 2.12 — Build a Complete NPay Payment Flow

> Lesson text as shared, in two pieces: Part 1 (the flow overview and Sections 1–9, cut off inside the Section 9 code)
> and "Final NPay Integration" (Sections 1–5 with the complete runnable ContentView.swift, a test table, the
> architecture review and "Unit 2 completed"). Between them the text noted that the complete code was still pending.
> Interactive widgets are described in brackets. The deck (`index.html`, built by `tools/gen2_12.py`) follows both
> pieces. Simulator evidence and authored additions are listed at the end under "Deck changes".

NPay Engineering Lab · Unit 2 Capstone · SwiftUI Architecture & Internals

We've reached the final lesson of Unit 2. Until now, NPay has had several independent features: a balance card, a balance editor, payment input fields, quick actions, and transaction history. But there's one problem. When the user enters ₹1,500 and taps Continue Demo, NPay only prints a message. The balance and transaction history don't change. Today we'll connect those components into one working application flow.

**What we're building.** User enters payment (recipient and amount) → NPay validates (valid recipient, amount and available balance) → payment is simulated (local application logic — no real transfer) → balance updates (@State changes) → transaction is recorded (new identifiable transaction) → SwiftUI updates (BalanceCard and TransactionHistory reflect the result).

## 1. First, experience the complete NPay flow

[Interactive demonstration: a "Demo" wallet with Available Balance ₹25,000.00, a Send Money form (Recipient ID, Amount (₹), "Send Demo Payment"), Recent Transactions (Coffee Shop −₹250, Electricity Bill −₹1,200, Salary Credit +₹45,000) and "Reset demo".] Try sending ₹1,500 to ravi@npay. The balance becomes ₹23,500 and a new transaction appears. This is the behavior we want in our real NPay Xcode project.

## 2. Architecture problem — who should process the payment?

Currently, PaymentForm owns `@State private var recipient = ""` and `@State private var amountText = ""`. But ContentView owns `@State private var balance = 25000` and `@State private var transactions: [Transaction] = [...]`. How can the form request a payment without directly owning or modifying the balance? We'll use a closure, just as we did in Lesson 2.7.

[NPay — one-way data flow with actions: ContentView (owns balance and transactions) → PaymentForm (receives balance and onSend closure) → user taps Send (PaymentForm calls onSend(recipient, amount)) → ContentView processes the demo request (validates and updates owned state).]

**Why not put everything inside PaymentForm?** Because PaymentForm should be responsible for collecting input and presenting validation feedback. The parent coordinates the application's state. This is a stepping stone toward MVVM and application services in Unit 4.

## 3. First code change — define the action contract

```swift
struct PaymentForm: View {
    let availableBalance: Int
    let onSend: (String, Int) -> Bool

    @State private var recipient = ""
    @State private var amountText = ""

    // Remaining code...
}
```

**Why Int?** For this exercise, we'll represent payment amounts in paise, the smallest INR unit.

| Amount | Paise |
|---|---|
| ₹1 | 100 |
| ₹10.50 | 1,050 |
| ₹1,500 | 150,000 |

This avoids binary floating-point rounding in our simulated financial calculations. The closure `(String, Int) -> Bool` accepts a recipient and amount in paise, then returns whether the local demo operation succeeded.

## 4. Convert input to paise safely

We want to avoid `let amount = Double(amountText)!`. Force-unwrapping untrusted user input is unsafe, and Double is not an ideal money representation. Instead, we'll validate the decimal string and convert it into integer paise.

(Code: `func parsePaise(_ text: String) -> Int?` — regex `^[0-9]+(\.[0-9]{1,2})?$`; split on "." keeping empty pieces; `Int(parts[0])` for rupees; pad the fraction to two digits with "0"; `Int` of that for paise; `rupees.multipliedReportingOverflow(by: 100)` and `rupeePaise.addingReportingOverflow(paise)`, returning nil on overflow; return the total. The same code appears as `Money.parsePaise` in the complete code.)

**Why is this better?** It checks the input syntax, avoids forced unwraps, and rejects values that overflow Int. It also represents the parsed amount exactly in paise. This is still a teaching implementation. Production financial systems require more comprehensive monetary and transaction-domain handling.

## 5. Move NPay's balance to integer paise

Our current balance is `@State private var balance = 25000`. For consistency, we'll change it to `@State private var balancePaise = 2_500_000`, which represents ₹25,000. Our Transaction model will also store amounts in paise:

```swift
struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}
```

**Why use Date instead of String?** Because dates should be represented as date values in the domain model. Formatting "Today" or "Yesterday" is a presentation concern. This is another step toward separating domain data from UI formatting.

## 6. Implement the demo payment operation

(Code: `private func sendDemoPayment(to recipient: String, amountPaise: Int) -> Bool` in ContentView — guard the recipient is not empty and `0 < amountPaise <= balancePaise`, else return false; `balancePaise -= amountPaise`; insert `Transaction(id: UUID(), title: "Sent to \(recipient)", amountPaise: -amountPaise, date: Date())` at 0; return true. The complete code's version trims the recipient and sets a status message.)

**Important engineering detail.** Both the balance and transaction collection are updated in one synchronous operation. That keeps our local demo state consistent during the action. This is not a database transaction and provides no durable atomicity across crashes or devices. We'll address authoritative backend transactions later.

## 7. Connect PaymentForm to ContentView

```swift
PaymentForm(
    availableBalance: balancePaise
) { recipient, amountPaise in

    sendDemoPayment(
        to: recipient,
        amountPaise: amountPaise
    )
}
```

The form doesn't need direct access to the parent's transaction array. It sends a request through the closure. The parent decides whether to accept it.

## 8. Behind the scenes — complete payment event flow

[Trace a ₹1,500 demo payment — a 7-stage stepper; only stage 1 was included: "TextField receives input — recipient and amount strings are updated through bindings."]

**Trainer-level question.** Does SwiftUI guarantee that two separate @State mutations are durable and atomic like a database transaction? No. SwiftUI state management coordinates UI updates. It is not a financial transaction engine.

## 9. Complete core code for Lesson 2.12

(Core code: Transaction, a ContentView with `balancePaise`, an empty `transactions` array, `BalanceCard(balancePaise:)`, `PaymentForm(availableBalance:) { … sendDemoPayment … }`, `TransactionHistory`, and `sendDemoPayment` with trimming — cut off inside `BalanceCard`. The note that followed: "Not yet … the complete integrated NPay code was cut off", then "next".)

## Final NPay Integration

We're finishing Unit 2 with a complete, runnable NPay application. This version preserves our work from Lessons 2.1–2.11 and connects the components into a working local payment simulation.

### 1. What NPay can do now

[Mock-up: NPay, Payments made simple; Available Balance ₹25,000.00, NPay Demo Account; Send / Request / History; Send Money · Demo (Recipient ID, Amount (₹), Send Demo Payment); Recent Transactions — "Your simulated payments will appear here."] We'll keep all the code in one file for now so you can run and inspect it easily. In Unit 3, we'll organize the application into separate files and screens.

### 2. Complete ContentView.swift

Replace the contents of ContentView.swift. This version uses integer paise for all monetary calculations and does not connect to a bank or payment service.

(Code: `enum Money` with `display(_ paise:)` — `Decimal(paise) / 100` formatted as INR currency in the en_IN locale — and `parsePaise(_:)` as in Section 4; `Transaction` with `amountPaise: Int` and `date: Date`; `ContentView` with `@State balancePaise = 2_500_000`, three mock transactions in paise dated `.now`, `@State statusMessage: String?`; a ScrollView of the header, `BalanceCard(balancePaise:)`, `BalanceEditor(balancePaise: $balancePaise)` (±100_000 paise, minimum 0), three QuickActions that set status messages ("Use the form below to send.", "Request feature coming soon.", "Scroll down for history."), `PaymentForm(availableBalancePaise:) { sendDemoPayment(...) }`, the optional status text, and `TransactionHistory`; `sendDemoPayment` trims, validates, subtracts, inserts "Sent to …" and sets "Demo payment recorded." or "Invalid payment request."; `PaymentForm` with `onSend: (String, Int) -> Bool`, `parsedAmount` via `Money.parsePaise`, `isValid`, the two TextFields with focus handling, the red validation caption, a "Send Demo Payment" button that calls `onSend` and clears the form on success, `.disabled(!isValid)`, and the keyboard Done toolbar; `TransactionRow` with an arrow symbol (down-left green for credits, up-right blue for debits), the date formatted as day and abbreviated month, and `Money.display`; `TransactionHistory` with a "No transactions yet." empty state. Keep NPayApp.swift with `WindowGroup { ContentView() }`. It runs unchanged in `tools/sim2_12/App.swift`.)

### 3. Verify the complete payment flow

| Test | Expected behavior |
|---|---|
| Starting balance | ₹25,000.00 |
| Enter ravi@npay and 1500 | Send button enabled |
| Tap Send Demo Payment | Balance becomes ₹23,500.00 |
| Inspect history | New Sent to ravi@npay transaction appears |
| Enter 0 | Send button disabled |
| Enter amount above balance | Send button disabled |
| Enter 12.345 | Send button disabled |
| Tap Add ₹1,000 | Balance increases by ₹1,000 |
| Tap Request | Shows a demo status message |

All operations are local simulations. No actual financial transaction occurs.

### 4. Architecture review — what have we built?

[NPay Unit 2 architecture: ContentView (owns @State balance, transactions, status) → BalanceCard (read-only balance), BalanceEditor (binding to balance), QuickAction (reusable action closure), PaymentForm (input, validation, focus), TransactionHistory (ForEach + stable identity); local demo payment logic (validates, updates balance, inserts transaction).]

**What happens behind the scenes?** TextField → Binding → @State → Button action → onSend closure → ContentView validation → State mutation → SwiftUI update → BalanceCard + TransactionHistory. This connects nearly every concept we've learned in Unit 2.

### 5. Senior engineer review

Our application works as a learning prototype, but it is not production-ready. The main architectural limitations are that payment rules still live in ContentView, balance changes are local and not persisted, transaction records are mock data, and there is no authentication, networking, server authority, or automated test suite. Also, the balance editor is deliberately a teaching control. A production banking app must never let the user directly change an authoritative balance. These limitations are intentional: future units will address them incrementally.

**Unit 2 completed.**

## Deck changes

The deck (`index.html`, built by `tools/gen2_12.py`, 33 slides) follows both pieces, grouped into 7 Parts: the goal
(overview, 1), who processes the payment (2–3, 7), money in paise (3–5), the payment operation (6, 8), run and verify
(final 2–3), architecture review (final 4–5), and an **authored** Unit 2 review map; then recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_12/`, rerun with `sh tools/sim2_12/run.sh`; the complete
ContentView.swift runs unchanged, driven by text input (UIKeyInput) and accessibility activation as in 2.11)
- The flow: ₹25,000.00 → ₹23,500.00 after sending ₹1,500 to ravi@npay; "Sent to ravi@npay" on top of the history; "Demo payment recorded."; both fields cleared; screenshots at the top (scrolled back after the keyboard moved the view) and at the bottom.
- The text's verification table, every row run: 0, 12.345 and 25000.01 keep Send disabled; 25000 enables it; "+ ₹1,000" gives ₹26,000.00 and then 25000.01 is accepted; Request shows "Request feature coming soon." (Send and History status messages not separately run.)
- `parsePaise` (Mac, swiftc): "1" 100, "10.50" 1050, "1500" 150000, "0.5" 50, "12.345" nil, "-500" nil, "92233720368547759" nil (the × 100 overflow check; **added** case).
- `Money.display` (Mac): ₹25,000.00, ₹23,500.00, -₹250.00, ₹10.50, and ₹12,34,56,789.00 for 12,345,678,900 paise (en_IN grouping; **added** case).
- `type(of: onSend)` printed `(String, Int) -> Bool`.
- The "before" screenshot is Lesson 2.11's final screen.

**Authored (flagged)**
- Section 8's 7-stage trace (only stage 1 shared), marked conceptual.
- The text has no knowledge check: all 9 review questions are authored (including two predict items and a spaced item from 2.11).
- Part 7 "Unit 2 in one picture": a table mapping each Unit 2 lesson to its place in the final app.
- Outcomes, "Where we are", recap, "Where this goes next" (Unit 3 and Unit 4 named in the text; later units from the review's limitations), lab, end slide "Next: Unit 03 — Advanced SwiftUI & Navigation" (the curriculum's Unit 03 title).
- Slide code is condensed (one-line guards, `// body: …` in place of the text's "Remaining code...") and typechecks; the full code is in the text and `App.swift`.

**Canon note.** 2.12 moves NPay to integer paise (`Int`), in line with the course canon (Unit 01 uses `Int64` paise); 2.8–2.11 used whole rupees as their texts did.

**Wording**
- "Trainer-level question" / "Senior engineer review" became neutral callouts. The note between the pieces ("done? Not yet…") is not part of the deck.
