import SwiftUI
import UIKit

// Lesson 2.12 evidence app (Unit 2 capstone). The lesson's complete ContentView.swift runs unchanged below.
// Fields are focused as a tap would and text entered with UIKeyInput.insertText; buttons are activated through
// accessibility. run.sh turns simulator accessibility on so SwiftUI exposes elements.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("pay") { ContentView().task { await pay() } }
            else if args.contains("paidtop") { ContentView().task { await pay(quiet: true) } }
            else if args.contains("paidbottom") { ContentView().defaultScrollAnchor(.bottom).task { await pay(quiet: true) } }
            else if args.contains("invalid") { ContentView().task { await invalid() } }
            else if args.contains("status") { ContentView().task { await status() } }
            else if args.contains("final") { ContentView() }
            else { ContentView() }
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
@MainActor func element(_ label: String) -> NSObject? { elements().first { $0.accessibilityLabel == label } }
@MainActor func textField(_ placeholder: String) -> UITextField? {
    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene else { return nil }
    func find(_ v: UIView) -> UITextField? {
        if let f = v as? UITextField, f.placeholder == placeholder { return f }
        for s in v.subviews { if let f = find(s) { return f } }
        return nil
    }
    for w in scene.windows { if let f = find(w) { return f } }
    return nil
}
@MainActor func press(_ label: String) async {
    if let field = textField(label) {          // a TextField: focus it, as a tap would
        print("[focus \"\(label)\"]")
        _ = field.becomeFirstResponder()
        try? await Task.sleep(for: .milliseconds(500))
        return
    }
    guard let e = element(label) else { print("no element \(label)"); return }
    print("[activate \"\(label)\"]")
    _ = e.accessibilityActivate()
    try? await Task.sleep(for: .milliseconds(500))
}
@MainActor func firstResponder() -> UIView? {
    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene else { return nil }
    func find(_ v: UIView) -> UIView? {
        if v.isFirstResponder { return v }
        for s in v.subviews { if let f = find(s) { return f } }
        return nil
    }
    for w in scene.windows { if let f = find(w) { return f } }
    return nil
}
@MainActor func type(_ text: String) async {
    guard let input = firstResponder() as? (UIView & UIKeyInput) else { print("no focused text input"); return }
    print("[type \"\(text)\" into \(type(of: input))]")
    for ch in text {
        input.insertText(String(ch))
        try? await Task.sleep(for: .milliseconds(150))
    }
}
@MainActor func report(_ label: String) {
    guard let e = element(label) else { print("no element \(label)"); return }
    print("\"\(label)\" enabled: \(!e.accessibilityTraits.contains(.notEnabled))")
}
@MainActor func show(_ what: String) {
    let money = elements().compactMap { $0.accessibilityLabel }.filter { $0.contains("₹") || $0.hasPrefix("Sent to") || $0.hasPrefix("Demo") || $0.hasPrefix("Use the") || $0.hasPrefix("Request") || $0.hasPrefix("Invalid") }
    print("\(what): " + money.prefix(6).joined(separator: " | "))
}
@MainActor func setAmount(_ s: String) async {
    await press("Amount (₹)")
    // clear, then type
    if let f = textField("Amount (₹)") { while f.hasText { f.deleteBackward() } }
    await type(s)
}

@MainActor func pay(quiet: Bool = false) async {
    try? await Task.sleep(for: .seconds(1.5))
    if !quiet { show("before"); report("Send Demo Payment") }
    await press("Recipient ID")
    await type("ravi@npay")
    await press("Amount (₹)")
    await type("1500")
    if !quiet { report("Send Demo Payment") }
    await press("Send Demo Payment")
    try? await Task.sleep(for: .milliseconds(500))
    if quiet, let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
        // the keyboard scrolled the form into view; scroll back to the top so the balance shows
        func scrollViews(_ v: UIView) -> [UIScrollView] { (v as? UIScrollView).map { [$0] } ?? [] + v.subviews.flatMap(scrollViews) }
        for w in scene.windows { for sv in scrollViews(w) where ProcessInfo.processInfo.arguments.contains("paidtop") {
            sv.setContentOffset(CGPoint(x: 0, y: -sv.adjustedContentInset.top), animated: false) } }
    }
    if !quiet {
        show("after")
        print("recipient field now \"\(textField("Recipient ID")?.text ?? "?")\", amount field \"\(textField("Amount (₹)")?.text ?? "?")\"")
    }
}
@MainActor func invalid() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press("Recipient ID")
    await type("ravi@npay")
    for s in ["0", "12.345", "25000.01", "25000"] {
        await setAmount(s)
        report("Send Demo Payment")
    }
    await press("+ ₹1,000")
    show("after + ₹1,000")
    await setAmount("25000.01")
    report("Send Demo Payment")
}
@MainActor func status() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press("Request")
    show("after Request")
}

// ===================== The lesson's complete ContentView.swift =====================

// MARK: - Money Formatting

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

// MARK: - Transaction Model

struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}

// MARK: - Main Dashboard

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

    @State private var statusMessage: String?

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {

                // Branding

                Image(systemName: "creditcard.fill")
                    .font(.system(size: 48))
                    .foregroundStyle(.blue)

                Text("NPay")
                    .font(.largeTitle.bold())
                    .foregroundStyle(.blue)

                Text("Payments made simple")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                // Balance

                BalanceCard(balancePaise: balancePaise)

                BalanceEditor(
                    balancePaise: $balancePaise
                )

                // Quick Actions

                HStack(spacing: 12) {
                    QuickAction(
                        symbol: "arrow.up.right",
                        title: "Send"
                    ) {
                        statusMessage = "Use the form below to send."
                    }

                    QuickAction(
                        symbol: "arrow.down.left",
                        title: "Request"
                    ) {
                        statusMessage = "Request feature coming soon."
                    }

                    QuickAction(
                        symbol: "clock",
                        title: "History"
                    ) {
                        statusMessage = "Scroll down for history."
                    }
                }

                // Payment Form

                PaymentForm(
                    availableBalancePaise: balancePaise
                ) { recipient, amountPaise in
                    sendDemoPayment(
                        to: recipient,
                        amountPaise: amountPaise
                    )
                }

                if let statusMessage {
                    Text(statusMessage)
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }

                // Transaction History

                TransactionHistory(
                    transactions: transactions
                )
            }
            .padding()
        }
    }

    // MARK: - Demo Payment Logic

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
            statusMessage = "Invalid payment request."
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

        statusMessage = "Demo payment recorded."
        return true
    }
}

// MARK: - Balance Card

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

// MARK: - Balance Editor

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
                    balancePaise += 100_000
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

// MARK: - Payment Form

struct PaymentForm: View {
    let availableBalancePaise: Int
    let onSend: (String, Int) -> Bool

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
        VStack(alignment: .leading, spacing: 16) {
            Text("Send Money · Demo")
                .font(.headline)

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
                    recipient = ""
                    amountText = ""
                    focusedField = nil
                }
            }
            .buttonStyle(.borderedProminent)
            .disabled(!isValid)
        }
        .padding()
        .background(
            Color.blue.opacity(0.06),
            in: RoundedRectangle(cornerRadius: 16)
        )
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

// MARK: - Transaction Row

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

// MARK: - Transaction History

struct TransactionHistory: View {
    let transactions: [Transaction]

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Recent Transactions")
                .font(.headline)

            if transactions.isEmpty {
                Text("No transactions yet.")
                    .foregroundStyle(.secondary)
            }

            ForEach(transactions) { transaction in
                TransactionRow(transaction: transaction)

                Divider()
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }
}
