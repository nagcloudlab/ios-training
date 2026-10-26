import SwiftUI
import UIKit

// Lesson 3.1 evidence app. The lesson's NavigationExperiment and complete code (Money, Transaction, BalanceCard,
// BalanceEditor, TransactionRow, PaymentScreen, HistoryScreen, ContentView) run unchanged below; the experiments
// from Sections 9, 13, 14 and 16 are separate types. Links and buttons are activated through accessibility (run.sh
// turns simulator accessibility on); fields are focused as a tap would and text entered with UIKeyInput.insertText.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("exp") { NavigationExperiment() }
            else if args.contains("exppushed") { NavigationExperiment().task { await wait(1.5); await press("Send Money") } }
            else if args.contains("pushpay") { ContentView().task { await wait(1.5); await press("Send Money") } }
            else if args.contains("pushhistory") { ContentView().task { await wait(1.5); await press("Transaction History") } }
            else if args.contains("alert") { ContentView().task { await pay(stop: true) } }
            else if args.contains("paid") { ContentView().task { await pay(stop: false) } }
            else if args.contains("paidhistory") { ContentView().task { await pay(stop: false); await press("Transaction History") } }
            else if args.contains("verify") { ContentView().task { await verify() } }
            else if args.contains("counter") { CounterDashboard().task { await counter() } }
            else if args.contains("trace") { TraceDashboard().task { await trace() } }
            else if args.contains("owner") { OwnerDashboard().task { await owner() } }
            else if args.contains("service") { ServiceDashboard().task { await service() } }
            else { ContentView() }
        }
    }
}

// MARK: - Driving helpers

@MainActor func wait(_ s: Double) async { try? await Task.sleep(for: .seconds(s)) }
@MainActor func allWindows() -> [UIWindow] {
    UIApplication.shared.connectedScenes.compactMap { $0 as? UIWindowScene }.flatMap { $0.windows }
}
@MainActor func elements() -> [NSObject] {
    var found: [NSObject] = []
    func walk(_ o: NSObject, _ depth: Int) {
        guard depth < 60 else { return }
        if let els = o.accessibilityElements as? [NSObject] { for e in els { found.append(e); walk(e, depth + 1) } }
        if let v = o as? UIView {
            if v.isAccessibilityElement, v.accessibilityLabel != nil { found.append(v) }
            for s in v.subviews where !s.isHidden { walk(s, depth + 1) }
        }
    }
    for w in allWindows() { walk(w, 0) }
    return found
}
@MainActor func labels() -> [String] { elements().compactMap { $0.accessibilityLabel }.filter { !$0.isEmpty } }
@MainActor func element(_ label: String) -> NSObject? { elements().last { $0.accessibilityLabel == label } }
@MainActor func textField(_ placeholder: String) -> UITextField? {
    func find(_ v: UIView) -> UITextField? {
        if let f = v as? UITextField, f.placeholder == placeholder { return f }
        for s in v.subviews { if let f = find(s) { return f } }
        return nil
    }
    for w in allWindows() { if let f = find(w) { return f } }
    return nil
}
@MainActor func press(_ label: String, quiet: Bool = false) async {
    if let field = textField(label) {
        if !quiet { print("[focus \"\(label)\"]") }
        _ = field.becomeFirstResponder()
        await wait(0.5)
        return
    }
    guard let e = element(label) else { print("no element \(label)"); return }
    if !quiet { print("[activate \"\(label)\"]") }
    _ = e.accessibilityActivate()
    await wait(1.2)
}
@MainActor func back() async {
    // Accessibility activation of the back button returns false in the simulator and real taps can't be scripted,
    // so Back is driven by popping the navigation controller that hosts the stack on this iOS version: the same
    // pop the back button and the edge swipe perform. (Test-driver detail, not an API to use in an app.)
    var r: UIResponder? = textField("Recipient ID") ?? deepestView()
    while let x = r {
        if let nav = x as? UINavigationController, nav.viewControllers.count > 1 {
            nav.popViewController(animated: true)
            print("[Back]")
            await wait(1.2)
            return
        }
        r = x.next
    }
    print("no navigation controller to pop")
}
@MainActor func alertButton(_ title: String) async {
    // Alert buttons don't respond to accessibility activation here either; the driver runs the action's handler
    // and dismisses the alert, which is what a tap on the button does.
    guard let alert = allWindows().compactMap({ w -> UIAlertController? in
        var vc = w.rootViewController
        while let p = vc?.presentedViewController { vc = p }
        return vc as? UIAlertController
    }).first, let action = alert.actions.first(where: { $0.title == title }) else { print("no alert button \(title)"); return }
    typealias Handler = @convention(block) (UIAlertAction) -> Void
    let handler = action.value(forKey: "handler").map { unsafeBitCast($0 as AnyObject, to: Handler.self) }
    print("[alert: \(title)]")
    alert.dismiss(animated: true) { handler?(action) }
    await wait(1.5)
}
@MainActor func deepestView() -> UIView? {
    var v: UIView? = allWindows().first
    while let s = v?.subviews.last { v = s }
    return v
}
@MainActor func firstResponder() -> UIView? {
    func find(_ v: UIView) -> UIView? {
        if v.isFirstResponder { return v }
        for s in v.subviews { if let f = find(s) { return f } }
        return nil
    }
    for w in allWindows() { if let f = find(w) { return f } }
    return nil
}
@MainActor func type(_ text: String) async {
    guard let input = firstResponder() as? (UIView & UIKeyInput) else { print("no focused text input"); return }
    for ch in text { input.insertText(String(ch)); try? await Task.sleep(for: .milliseconds(120)) }
}
@MainActor func setAmount(_ s: String) async {
    await press("Amount (₹)", quiet: true)
    if let f = textField("Amount (₹)") { while f.hasText { f.deleteBackward() } }
    await type(s)
}
@MainActor func enabled(_ label: String) -> String {
    guard let e = element(label) else { return "missing" }
    return e.accessibilityTraits.contains(.notEnabled) ? "disabled" : "enabled"
}
@MainActor func visible(_ what: String) {
    let interesting = labels().filter { $0.contains("₹") || $0.hasPrefix("Sent to") || $0.hasPrefix("Count") || $0.hasPrefix("Coffee") || $0.hasPrefix("Salary") || $0.hasPrefix("Electricity") || $0.contains("Screen") || $0.hasPrefix("Demo Payment") }
    var seen = Set<String>()
    print("\(what): " + interesting.filter { seen.insert($0).inserted }.prefix(8).joined(separator: " | "))
}

// MARK: - Runs

@MainActor func pay(stop: Bool) async {
    await wait(1.5)
    await press("Send Money", quiet: true)
    await press("Recipient ID", quiet: true)
    await type("ravi@npay")
    await press("Amount (₹)", quiet: true)
    await type("1500")
    await press("Send Demo Payment", quiet: true)
    if stop { return }
    await alertButton("Done")
}
@MainActor func verify() async {
    await wait(1.5)
    visible("1. launch")
    await press("Send Money")
    visible("2. pushed")
    await back()
    visible("3. back")
    await press("Send Money")
    await press("Recipient ID")
    await type("ravi@npay")
    for s in ["0", "12.345", "25000.01", "1500"] {
        await setAmount(s)
        print("   amount \"\(s)\": Send Demo Payment \(enabled("Send Demo Payment"))")
    }
    await press("Send Demo Payment")
    visible("4. alert")
    await alertButton("Done")
    visible("5. after Done")
    await press("Transaction History")
    visible("6. history")
    await back()
    await press("+ ₹1,000")
    visible("7. after + ₹1,000")
    await press("Send Money")
    visible("8. payment screen")
}
@MainActor func counter() async {
    await wait(1.5)
    await press("Send Money")
    for _ in 1...3 { await press("Increment", quiet: true) }
    visible("after 3 taps")
    await back()
    await press("Send Money")
    visible("pushed again")
}
@MainActor func trace() async {
    await wait(1.5)
    print("-- tap Send Money")
    await press("Send Money", quiet: true)
    await wait(0.5)
    print("-- tap Back")
    await back()
    await wait(0.5)
    print("-- tap Send Money again")
    await press("Send Money", quiet: true)
    await wait(0.5)
}
@MainActor func owner() async {
    await wait(1.5)
    visible("dashboard")
    await press("Send Money")
    await press("Pay ₹1,500")
    visible("payment screen")
    await back()
    visible("dashboard again")
}
@MainActor func service() async {
    await wait(1.5)
    print("-- tap Send Money")
    await press("Send Money", quiet: true)
    print("-- tap Back")
    await back()
    await wait(1)
    print("-- done")
}
// MARK: - Experiments (Sections 9, 13, 14, 16)

struct CounterDashboard: View {   // Section 13: PaymentScreen replaced temporarily
    var body: some View {
        NavigationStack {
            NavigationLink("Send Money") { CounterPaymentScreen() }
                .navigationTitle("NPay")
        }
    }
}
struct CounterPaymentScreen: View {   // the text's temporary PaymentScreen, renamed for the run
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

struct TraceDashboard: View {   // Section 14: when do init and body run?
    var body: some View {
        let _ = print("Dashboard.body")
        NavigationStack {
            NavigationLink("Send Money") { TracePaymentScreen() }
                .navigationTitle("NPay")
        }
        .onAppear { print("Dashboard: pid \(ProcessInfo.processInfo.processIdentifier), windows \(allWindows().count)") }
    }
}
struct TracePaymentScreen: View {
    init() { print("PaymentScreen.init") }

    var body: some View {
        let _ = Self._printChanges()
        let _ = print("PaymentScreen.body")
        return VStack {
            Text("Payment Screen")
        }
        .onAppear { print("PaymentScreen: pid \(ProcessInfo.processInfo.processIdentifier), windows \(allWindows().count)") }
        .onDisappear { print("PaymentScreen.onDisappear") }
    }
}

struct OwnerDashboard: View {   // Section 9's question: PaymentScreen creates its own @State balancePaise
    @State private var balancePaise = 2_500_000

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                BalanceCard(balancePaise: balancePaise)
                NavigationLink("Send Money") { OwnBalancePaymentScreen(startPaise: balancePaise) }
            }
            .padding()
            .navigationTitle("NPay")
        }
    }
}
struct OwnBalancePaymentScreen: View {
    @State private var balancePaise: Int   // a second, independent owner

    init(startPaise: Int) { _balancePaise = State(initialValue: startPaise) }

    var body: some View {
        VStack(spacing: 20) {
            Text("Available: \(Money.display(balancePaise))")
            Button("Pay ₹1,500") { balancePaise -= 150_000 }
                .buttonStyle(.borderedProminent)
        }
        .navigationTitle("Send Money")
    }
}

final class DemoPaymentService {
    init() { print("DemoPaymentService init") }
    deinit { print("DemoPaymentService deinit") }
}
struct ServiceDashboard: View {
    var body: some View {
        NavigationStack {
            NavigationLink("Send Money") { ServicePaymentScreen() }
                .navigationTitle("NPay")
        }
    }
}
struct ServicePaymentScreen: View {
    @State private var service: DemoPaymentService?

    var body: some View {
        Text("Payment Screen")
            .onAppear { if service == nil { service = DemoPaymentService() } }
            .onDisappear { print("ServicePaymentScreen.onDisappear") }
            .navigationTitle("Payment")
    }
}

// ===================== Section 2: NavigationExperiment.swift =====================

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

// ===================== The lesson's complete code =====================

// Models/Money.swift

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

// Models/Transaction.swift

struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}

// Components/BalanceCard.swift

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

// Components/BalanceEditor.swift

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

// Components/TransactionRow.swift

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

// Screens/PaymentScreen.swift

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

// Screens/HistoryScreen.swift

struct HistoryScreen: View {
    let transactions: [Transaction]

    var body: some View {
        List(transactions) { transaction in
            TransactionRow(transaction: transaction)
        }
        .navigationTitle("History")
    }
}

// ContentView.swift

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
