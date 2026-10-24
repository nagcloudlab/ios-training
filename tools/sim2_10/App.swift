import SwiftUI
import UIKit

// Lesson 2.10 evidence app. Each launch argument runs one experiment from the lesson text.
// Buttons are activated through their accessibility elements (the path VoiceOver uses); run.sh turns simulator
// accessibility on so SwiftUI exposes them.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            let flagThenInsert = ["Flag Coffee Shop", "Insert Mobile Recharge"]
            if args.contains("types") { TypesDemo() }
            else if args.contains("stable") { StableList().task { await activate(flagThenInsert) } }
            else if args.contains("index") { IndexList().task { await activate(flagThenInsert) } }
            else if args.contains("unstable") { UnstableList().task { await activate(flagThenInsert) } }
            else if args.contains("rowchanges") { ChangesList().task { await activate(["Add Demo Transaction"]) } }
            else if args.contains("eager") { CountList(kind: "VStack") }
            else if args.contains("lazy") { CountList(kind: "LazyVStack") }
            else if args.contains("list") { CountList(kind: "List") }
            else if args.contains("bottom") { ContentView().defaultScrollAnchor(.bottom) }
            else if args.contains("added") { ContentView().defaultScrollAnchor(.bottom).task { await activate(["Add Demo Transaction"]) } }
            else if args.contains("final") { ContentView() }
            else { BeforeView() }
        }
    }
}

@MainActor func elements() -> [NSObject] {
    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
          let window = scene.windows.first else { return [] }
    var found: [NSObject] = []
    func walk(_ o: NSObject, _ depth: Int) {
        guard depth < 40 else { return }
        if let els = o.accessibilityElements as? [NSObject] { for e in els { found.append(e); walk(e, depth + 1) } }
        if let v = o as? UIView { for s in v.subviews { walk(s, depth + 1) } }
    }
    walk(window, 0)
    return found
}

@MainActor func activate(_ labels: [String]) async {
    try? await Task.sleep(for: .seconds(1.5))
    for label in labels {
        guard let e = elements().first(where: { $0.accessibilityLabel == label }) else { print("no element \(label)"); continue }
        print("[activate \"\(label)\"]")
        _ = e.accessibilityActivate()
        try? await Task.sleep(for: .milliseconds(500))
    }
}

// Where Lesson 2.9 ended
struct BeforeView: View {
    @State private var balance = 25000
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                Image(systemName: "creditcard.fill").font(.system(size: 48)).foregroundStyle(.blue)
                Text("NPay").font(.largeTitle.bold()).foregroundStyle(.blue)
                Text("Payments made simple").font(.subheadline).foregroundStyle(.secondary)
                BalanceCard(balance: balance)
                VStack(spacing: 12) {
                    Text("Demo Balance Editor").font(.headline)
                    HStack(spacing: 12) {
                        Button("− ₹1,000") { }.buttonStyle(.bordered)
                        Button("+ ₹1,000") { }.buttonStyle(.borderedProminent)
                    }
                }
                .padding()
                HStack(spacing: 12) {
                    QuickAction(symbol: "arrow.up.right", title: "Send") { }
                    QuickAction(symbol: "arrow.down.left", title: "Request") { }
                    QuickAction(symbol: "clock", title: "History") { }
                }
            }
            .padding()
        }
    }
}

// Sections 3 and 6: types
struct TypesDemo: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let names = ["Coffee Shop", "Electricity Bill", "Salary Credit"]
                let a = ForEach(names, id: \.self) { transaction in
                    Text(transaction)
                }
                let b = ForEach(mockTransactions()) { transaction in
                    TransactionRow(transaction: transaction)
                }
                print("ForEach(strings, id: \\.self):", type(of: a))
                print("ForEach(transactions):", type(of: b))
            }
    }
}

func mockTransactions() -> [Transaction] {
    [
        Transaction(id: UUID(), title: "Coffee Shop", amount: -250, date: "Today"),
        Transaction(id: UUID(), title: "Electricity Bill", amount: -1200, date: "Yesterday"),
        Transaction(id: UUID(), title: "Salary Credit", amount: 45000, date: "22 Oct")
    ]
}

// Sections 9, 10, 15, 16: row-local state under three kinds of identity
struct FlagRow: View {
    let title: String
    @State private var flagged = false
    var body: some View {
        let _ = print("  row \(title): flagged = \(flagged)")
        HStack {
            Text(title)
            Spacer()
            if flagged { Image(systemName: "flag.fill").foregroundStyle(.orange) }
            Button(flagged ? "Unflag \(title)" : "Flag \(title)") { flagged.toggle() }
                .labelStyle(.iconOnly)
                .font(.caption)
        }
        .padding(.vertical, 6)
    }
}

struct InsertButton: View {
    let insert: () -> Void
    var body: some View {
        Button("Insert Mobile Recharge", action: insert).buttonStyle(.borderedProminent)
    }
}

struct StableList: View {
    @State private var items = mockTransactions()
    var body: some View {
        VStack {
            Text("ForEach(items)  // stable id").font(.caption.monospaced()).foregroundStyle(.secondary)
            ForEach(items) { t in FlagRow(title: t.title) }
            InsertButton { items.insert(Transaction(id: UUID(), title: "Mobile Recharge", amount: -399, date: "Today"), at: 0) }
        }
        .padding()
    }
}

struct IndexList: View {
    @State private var items = mockTransactions()
    var body: some View {
        VStack {
            Text("ForEach(items.indices, id: \\.self)").font(.caption.monospaced()).foregroundStyle(.secondary)
            ForEach(items.indices, id: \.self) { index in
                FlagRow(title: items[index].title)
            }
            InsertButton { items.insert(Transaction(id: UUID(), title: "Mobile Recharge", amount: -399, date: "Today"), at: 0) }
        }
        .padding()
    }
}

struct UnstableTransaction: Identifiable {
    var id: UUID {
        UUID()
    }

    let title: String
}

struct UnstableList: View {
    @State private var items = mockTransactions().map { UnstableTransaction(title: $0.title) }
    var body: some View {
        VStack {
            Text("var id: UUID { UUID() }").font(.caption.monospaced()).foregroundStyle(.secondary)
            ForEach(items) { t in FlagRow(title: t.title) }
            InsertButton { items.insert(UnstableTransaction(title: "Mobile Recharge"), at: 0) }
        }
        .padding()
    }
}

// Section 21: _printChanges in a row
struct ChangesRow: View {
    let transaction: Transaction
    var body: some View {
        let _ = Self._printChanges()

        return HStack {
            Text(transaction.title)
            Spacer()
            Text("\(transaction.amount)")
        }
    }
}
struct ChangesList: View {
    @State private var transactions = mockTransactions()
    var body: some View {
        VStack {
            ForEach(transactions) { t in ChangesRow(transaction: t) }
            Button("Add Demo Transaction") {
                transactions.insert(Transaction(id: UUID(), title: "Mobile Recharge", amount: -399, date: "Today"), at: 0)
            }
        }
        .padding()
    }
}

// Section 17: how many row bodies does each container evaluate for 1,000 transactions?
@MainActor final class BodyCount { static var n = 0 }
struct CountedRow: View {
    let transaction: Transaction
    var body: some View {
        let _ = BodyCount.n += 1
        TransactionRow(transaction: transaction)
    }
}
struct CountList: View {
    let kind: String
    let items: [Transaction] = (1...1000).map {
        Transaction(id: UUID(), title: "Transaction \($0)", amount: -$0, date: "Today")
    }
    var body: some View {
        Group {
            switch kind {
            case "VStack":
                ScrollView { VStack { ForEach(items) { CountedRow(transaction: $0) } } }
            case "LazyVStack":
                ScrollView { LazyVStack { ForEach(items) { CountedRow(transaction: $0) } } }
            default:
                List(items) { CountedRow(transaction: $0) }
            }
        }
        .task {
            try? await Task.sleep(for: .seconds(2))
            print("\(kind): \(BodyCount.n) of 1,000 row bodies evaluated")
        }
    }
}

// The lesson's complete code (Lessons 2.1-2.10)

// MARK: - Transaction Model

struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amount: Int
    let date: String
}

// MARK: - Main Dashboard

struct ContentView: View {

    // Parent owns the state
    @State private var balance = 25000

    @State private var transactions: [Transaction] = [
        Transaction(
            id: UUID(),
            title: "Coffee Shop",
            amount: -250,
            date: "Today"
        ),
        Transaction(
            id: UUID(),
            title: "Electricity Bill",
            amount: -1200,
            date: "Yesterday"
        ),
        Transaction(
            id: UUID(),
            title: "Salary Credit",
            amount: 45000,
            date: "22 Oct"
        )
    ]

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {

                // NPay branding
                Image(systemName: "creditcard.fill")
                    .font(.system(size: 48))
                    .foregroundStyle(.blue)

                Text("NPay")
                    .font(.largeTitle.bold())
                    .foregroundStyle(.blue)

                Text("Payments made simple")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                // Display parent-owned balance
                BalanceCard(balance: balance)

                // Child modifies balance through Binding
                BalanceEditor(balance: $balance)

                // Interactive quick actions
                HStack(spacing: 12) {

                    QuickAction(
                        symbol: "arrow.up.right",
                        title: "Send"
                    ) {
                        print("Send tapped")
                    }

                    QuickAction(
                        symbol: "arrow.down.left",
                        title: "Request"
                    ) {
                        print("Request tapped")
                    }

                    QuickAction(
                        symbol: "clock",
                        title: "History"
                    ) {
                        print("History tapped")
                    }
                }

                // Add a mock transaction
                Button("Add Demo Transaction") {
                    addDemoTransaction()
                }
                .buttonStyle(.borderedProminent)

                // Transaction history
                TransactionHistory(
                    transactions: transactions
                )
            }
            .padding()
        }
    }

    // MARK: - Actions

    private func addDemoTransaction() {
        let transaction = Transaction(
            id: UUID(),
            title: "Mobile Recharge",
            amount: -399,
            date: "Today"
        )

        transactions.insert(transaction, at: 0)
    }
}

// MARK: - Balance Card

struct BalanceCard: View {
    let balance: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {

            Text("Available Balance")
                .font(.subheadline)

            Text(
                balance,
                format: .currency(code: "INR")
                    .precision(.fractionLength(0))
            )
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

// MARK: - Balance Editor

struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        VStack(spacing: 12) {

            Text("Demo Balance Editor")
                .font(.headline)

            HStack(spacing: 12) {

                Button("− ₹1,000") {
                    balance = max(0, balance - 1000)
                }
                .buttonStyle(.bordered)

                Button("+ ₹1,000") {
                    balance += 1000
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

// MARK: - Quick Action

struct QuickAction: View {
    let symbol: String
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {

                Image(systemName: symbol)
                    .font(.title2)

                Text(title)
                    .font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(.blue)
        .background(
            Color.blue.opacity(0.08),
            in: RoundedRectangle(cornerRadius: 12)
        )
    }
}

// MARK: - Transaction Row

struct TransactionRow: View {
    let transaction: Transaction

    var body: some View {
        HStack(spacing: 12) {

            Image(systemName: "creditcard")
                .font(.title2)
                .foregroundStyle(.blue)

            VStack(alignment: .leading, spacing: 4) {

                Text(transaction.title)
                    .font(.headline)

                Text(transaction.date)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }

            Spacer()

            Text(
                transaction.amount,
                format: .currency(code: "INR")
                    .precision(.fractionLength(0))
            )
            .font(.subheadline.bold())
            .foregroundStyle(
                transaction.amount >= 0
                    ? Color.green
                    : Color.primary
            )
        }
        .padding(.vertical, 8)
    }
}

// MARK: - Transaction History

struct TransactionHistory: View {
    let transactions: [Transaction]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {

            Text("Recent Transactions")
                .font(.headline)

            ForEach(transactions) { transaction in
                TransactionRow(
                    transaction: transaction
                )

                Divider()
            }
        }
    }
}
