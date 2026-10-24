import SwiftUI
import UIKit

// Lesson 2.11 evidence app. Each launch argument runs one experiment from the lesson text.
// Fields are focused through their accessibility elements and text is entered with UIKeyInput.insertText,
// the protocol keyboards use to deliver text. run.sh turns simulator accessibility on so SwiftUI exposes elements.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("hello") { TextFieldExperiment().task { await hello() } }
            else if args.contains("types") { TypesDemo() }
            else if args.contains("typing") { ContentView().task { await typing() } }
            else if args.contains("paste") { ContentView().task { await paste() } }
            else if args.contains("over") { ContentView().task { await over() } }
            else if args.contains("balance") { ContentView().task { await balanceChange() } }
            else if args.contains("keyboard") { ContentView().task { await keyboard() } }
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
let recipientLabel = "Recipient ID (e.g. ravi@npay)"
let amountLabel = "Amount (₹)"

@MainActor func hello() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press("Enter your name")
    await type("Ravi")
}
@MainActor func typing() async {
    try? await Task.sleep(for: .seconds(1.5))
    report("Continue Demo")
    await press(recipientLabel)
    await type("ravi@npay")
    print("[type return: onSubmit]")
    (firstResponder() as? UIKeyInput)?.insertText("\n")
    try? await Task.sleep(for: .milliseconds(400))
    print("focused after return: \(firstResponder().map { "\(type(of: $0))" } ?? "none"), placeholder \((firstResponder() as? UITextField)?.placeholder ?? "?")")
    await type("1500")
    report("Continue Demo")
    await press("Continue Demo")
}
@MainActor func paste() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press(amountLabel)
    UIPasteboard.general.string = "1500"
    print("[paste \"1500\"]")
    (firstResponder() as? UITextField)?.paste(nil)
    try? await Task.sleep(for: .milliseconds(400))
}
@MainActor func over() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press(recipientLabel)
    await type("ravi@npay")
    await press(amountLabel)
    await type("25001")
    report("Continue Demo")
}
@MainActor func balanceChange() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press(recipientLabel)
    await type("ravi@npay")
    await press(amountLabel)
    await type("25500")
    report("Continue Demo")
    await press("+ ₹1,000")
    report("Continue Demo")
}
@MainActor func keyboard() async {
    try? await Task.sleep(for: .seconds(1.5))
    await press(amountLabel)
    await type("1500")
}

// Section 3: the smallest TextField
struct TextFieldExperiment: View {
    @State private var name = ""

    var body: some View {
        VStack(spacing: 20) {
            TextField("Enter your name", text: $name)
                .textFieldStyle(.roundedBorder)

            Text("Hello, \(name)")
        }
        .padding()
        .onChange(of: name) { _, new in print("name = \"\(new)\"") }
    }
}

// Sections 2 and 9: types
struct TypesDemo: View {
    @State private var amountText = ""
    @FocusState private var amountFocused: Bool
    var body: some View {
        TextField("Amount", text: $amountText)
            .focused($amountFocused)
            .task {
                print("$amountText:", type(of: $amountText))
                print("_amountFocused:", type(of: _amountFocused))
                print("$amountFocused:", type(of: $amountFocused))
            }
    }
}

// Where Lesson 2.10 ended: the 2.10 dashboard without the payment form
struct BeforeView: View {
    @State private var balance = 25000
    @State private var transactions: [Transaction] = [
        Transaction(id: UUID(), title: "Coffee Shop", amount: -250, date: "Today"),
        Transaction(id: UUID(), title: "Electricity Bill", amount: -1200, date: "Yesterday"),
        Transaction(id: UUID(), title: "Salary Credit", amount: 45000, date: "22 Oct")
    ]
    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                Image(systemName: "creditcard.fill").font(.system(size: 48)).foregroundStyle(.blue)
                Text("NPay").font(.largeTitle.bold()).foregroundStyle(.blue)
                Text("Payments made simple").font(.subheadline).foregroundStyle(.secondary)
                BalanceCard(balance: balance)
                BalanceEditor(balance: $balance)
                HStack(spacing: 12) {
                    QuickAction(symbol: "arrow.up.right", title: "Send") { }
                    QuickAction(symbol: "arrow.down.left", title: "Request") { }
                    QuickAction(symbol: "clock", title: "History") { }
                }
                Button("Add Demo Transaction") { }.buttonStyle(.borderedProminent)
                TransactionHistory(transactions: transactions)
            }
            .padding()
        }
    }
}

// ===================== The lesson's complete code (Lessons 2.1-2.11) =====================

// MARK: - Transaction Model

struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amount: Int
    let date: String
}

// MARK: - Main Dashboard

struct ContentView: View {

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

                // MARK: Branding

                Image(systemName: "creditcard.fill")
                    .font(.system(size: 48))
                    .foregroundStyle(.blue)

                Text("NPay")
                    .font(.largeTitle.bold())
                    .foregroundStyle(.blue)

                Text("Payments made simple")
                    .font(.subheadline)
                    .foregroundStyle(.secondary)

                // MARK: Balance

                BalanceCard(balance: balance)

                BalanceEditor(balance: $balance)

                // MARK: Quick Actions

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

                // MARK: Payment Form

                PaymentForm(
                    availableBalance: balance
                )

                // MARK: Transaction Actions

                Button("Add Demo Transaction") {
                    addDemoTransaction()
                }
                .buttonStyle(.borderedProminent)

                // MARK: History

                TransactionHistory(
                    transactions: transactions
                )
            }
            .padding()
        }
    }

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

// MARK: - Payment Form

struct PaymentForm: View {

    let availableBalance: Int

    @State private var recipient = ""
    @State private var amountText = ""

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {

            Text("Send Money · Demo")
                .font(.headline)

            // Recipient Input

            TextField(
                "Recipient ID (e.g. ravi@npay)",
                text: $recipient
            )
            .textInputAutocapitalization(.never)
            .autocorrectionDisabled()
            .textFieldStyle(.roundedBorder)
            .focused($focusedField, equals: .recipient)
            .submitLabel(.next)
            .onSubmit {
                focusedField = .amount
            }

            // Amount Input

            TextField(
                "Amount (₹)",
                text: $amountText
            )
            .keyboardType(.decimalPad)
            .textFieldStyle(.roundedBorder)
            .focused($focusedField, equals: .amount)
            .onChange(of: amountText) { oldValue, newValue in
                print("Old amount:", oldValue)
                print("New amount:", newValue)
            }

            // Validation Feedback

            if !amountText.isEmpty && !isValidAmount {
                Text("Enter a valid amount within your balance.")
                    .font(.caption)
                    .foregroundStyle(.red)
            }

            // Submit Button

            Button("Continue Demo") {
                focusedField = nil

                print("Demo payment request")
                print("Recipient:", recipient)
                print("Amount:", amountText)
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

    // MARK: Validation

    private var isValid: Bool {
        let trimmedRecipient =
            recipient.trimmingCharacters(
                in: .whitespacesAndNewlines
            )

        return !trimmedRecipient.isEmpty && isValidAmount
    }

    private var isValidAmount: Bool {

        let pattern = #"^[0-9]+(\.[0-9]{1,2})?$"#

        guard amountText.range(
            of: pattern,
            options: .regularExpression
        ) != nil else {
            return false
        }

        guard let amount = Decimal(
            string: amountText,
            locale: Locale(identifier: "en_US_POSIX")
        ) else {
            return false
        }

        return amount > 0
            && amount <= Decimal(availableBalance)
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
                TransactionRow(transaction: transaction)

                Divider()
            }
        }
    }
}
