import SwiftUI
import UIKit

// Lesson 3.2 evidence app. The complete code through 3.2 (assembled from the lesson's snippets onto the 3.1 complete
// code; see "Deck changes") runs below, compiled with -module-name NPay so printed routes read NPay.NPayRoute.
// The Section 7/12/13 experiments, NavigationPath and the router answer are separate types. Buttons are activated
// through accessibility (run.sh turns simulator accessibility on); fields are focused and typed into as in 2.11;
// Back pops the navigation controller that hosts the stack (the back button doesn't respond to accessibility
// activation in the simulator), which is what the back button does.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("flow") { ContentView().task { await flow() } }
            else if args.contains("pushpay") { ContentView().task { await wait(1.5); await press("Send Money") } }
            else if args.contains("typed") { ContentView().task { await wait(1.5); await press("Send Money"); await fill() } }
            else if args.contains("success") { ContentView().task { await wait(1.5); await press("Send Money"); await fill(); await press("Send Demo Payment") } }
            else if args.contains("home") { ContentView().task { await wait(1.5); await press("Send Money"); await fill(); await press("Send Demo Payment"); await press("Back to Dashboard") } }
            else if args.contains("history") { ContentView().task { await wait(1.5); await press("Send Money"); await fill(); await press("Send Demo Payment"); await press("Back to Dashboard"); await press("Transaction History") } }
            else if args.contains("pathlab") { PathLab().task { await pathlab() } }
            else if args.contains("twoshot") { PathLab().task { await wait(1.5); await press("Payment, then History") } }
            else if args.contains("mixed") { MixedPathLab().task { await mixed() } }
            else if args.contains("deep") { DeepLinkLab().task { await deep() } }
            else if args.contains("mixedshot") { MixedPathLab().task { await wait(1.5); await press("Mixed path") } }
            else if args.contains("router") { RouterContentView().task { await wait(1.5); await press("Send Money"); visible("after Send Money") } }
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
    var r: UIResponder? = deepestView()
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
    let keep = ["₹", "Sent to", "Payment", "History", "Route", "Depth", "Recorded", "Dashboard", "Coffee", "#"]
    let skip = ["Send Demo Payment", "Back to Dashboard", "Transaction History", "Open History", "Open Payment", "Payment, then History", "Mixed path"]
    var seen = Set<String>()
    let shown = labels().filter { l in keep.contains { l.contains($0) } && !skip.contains(l) && !l.hasPrefix("−") && !l.hasPrefix("+") }
    print("\(what): " + shown.filter { seen.insert($0).inserted }.prefix(7).joined(separator: " | "))
}
@MainActor func fill() async {
    await press("Recipient ID", quiet: true)
    await type("ravi@npay")
    await press("Amount (₹)", quiet: true)
    await type("1500.50")
}

// MARK: - Runs

@MainActor func flow() async {
    await wait(1.5)
    visible("launch")
    await press("Send Money")
    await fill()
    print("   Send Demo Payment \(enabled("Send Demo Payment"))")
    await press("Send Demo Payment")
    visible("success screen")
    await press("Back to Dashboard")
    visible("dashboard")
    await press("Transaction History")
    visible("history")
    await back()
}
@MainActor func pathlab() async {
    await wait(1.5)
    print("-- Open Payment"); await press("Open Payment", quiet: true)
    print("-- Show success"); await press("Show success", quiet: true)
    print("-- Home"); await press("Home", quiet: true)
    print("-- Payment, then History"); await press("Payment, then History", quiet: true)
    visible("   on screen")
    print("-- system Back"); await back()
    visible("   on screen")
    print("-- Pop (guarded)"); await press("Pop", quiet: true)
    print("-- Pop at root (guarded)"); await press("Pop at root", quiet: true)
    print("-- done")
}
@MainActor func mixed() async {
    await wait(1.5)
    print("-- Mixed path"); await press("Mixed path", quiet: true)
    await wait(1)
    visible("   on screen")
    print("-- system Back"); await back()
    visible("   on screen")
}
@MainActor func deep() async {
    await wait(2)
    visible("launch")
    await back()
    visible("after Back")
}

// MARK: - Experiments

struct PathLab: View {   // Sections 7 and 13: the path, printed after each action
    @State private var path: [NPayRoute] = []
    private let demoID = UUID(uuidString: "6F1C2A9E-3B7D-4E21-9C55-0A8B7F3D2E10")!

    var body: some View {
        NavigationStack(path: $path) {
            VStack(spacing: 16) {
                Button("Open Payment") { path.append(.payment) }
                Button("Open History") { path.append(.history) }
                Button("Payment, then History") {
                    path.append(.payment)
                    path.append(.history)
                }
                Button("Pop at root") {
                    if !path.isEmpty { path.removeLast() }
                }
            }
            .navigationTitle("Path lab")
            .navigationDestination(for: NPayRoute.self) { route in
                VStack(spacing: 16) {
                    Text("Route: \(String(describing: route))")
                    Text("Depth: \(path.count)")
                    Button("Show success") { path.append(.success(transactionID: demoID)) }
                    Button("Pop") { if !path.isEmpty { path.removeLast() } }
                    Button("Home") { path.removeAll() }
                }
            }
        }
        .onChange(of: path) { oldPath, newPath in
            print("Old path:", oldPath)
            print("New path:", newPath)
        }
    }
}

struct MixedPathLab: View {   // Section 8: NavigationPath holds different Hashable types
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            Button("Mixed path") {
                path.append(NPayRoute.history)
                path.append(42)
                path.append("ravi@npay")
                print("count:", path.count)
            }
            .navigationTitle("NavigationPath")
            .navigationDestination(for: NPayRoute.self) { route in
                Text("Route: \(String(describing: route))")
            }
            .navigationDestination(for: Int.self) { number in
                Text("Int destination #\(number)")
            }
            // no destination registered for String
        }
        .onChange(of: path) { _, newPath in print("path count now", newPath.count) }
    }
}

struct DeepLinkLab: View {   // Section 12: the visible destination is a function of the path
    @State private var path: [NPayRoute] = [.payment, .history]

    var body: some View {
        NavigationStack(path: $path) {
            Text("Dashboard")
                .navigationTitle("NPay")
                .navigationDestination(for: NPayRoute.self) { route in
                    Text("Route: \(String(describing: route))")
                        .navigationTitle(route == .payment ? "Payment" : "History")
                }
        }
        .onChange(of: path) { _, newPath in print("New path:", newPath) }
    }
}

// ===================== The Q&A's router (iOS 17+, Observation) =====================

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

struct RouterContentView: View {   // the Q&A's ContentView, renamed for the run

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

// ===================== Complete code through Lesson 3.2 =====================

// Navigation/NPayRoute.swift

enum NPayRoute: Hashable {
    case payment
    case history
    case success(transactionID: UUID)
}

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

// Screens/PaymentSuccessScreen.swift

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
