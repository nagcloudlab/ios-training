import SwiftUI
import UIKit

// Lesson 3.3 evidence app. The text's TabExperiment and Section 4 selection example, and the complete code through
// 3.3 (assembled from the text's Sections 9-18 onto the 3.2 code; see "Deck changes") run below. TracedRootView is
// NPayRootView plus onChange prints; the lifetime, Observation and router-only experiments are separate types.
// Buttons are activated through accessibility (run.sh turns it on); fields are focused and typed into as in 2.11.
// Two driver details: tab buttons and the back button don't respond to accessibility activation in the simulator, so
// a tab is selected the way a tap does (ask the tab bar controller's delegate, select, tell the delegate) and Back pops
// the hosting navigation controller.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("tabexp") { TabExperiment() }
            else if args.contains("tabexphistory") { TabExperiment().task { await wait(1.5); await selectTab("History") } }
            else if args.contains("selection") { SelectionLab().task { await selection() } }
            else if args.contains("trace") { TracedRootView().task { await traceRun() } }
            else if args.contains("lifetime") { LifetimeLab().task { await lifetime() } }
            else if args.contains("observe") { ObservationLab().task { await observe() } }
            else if args.contains("draft") { NPayRootView().task { await draft() } }
            else if args.contains("verify") { NPayRootView().task { await verify() } }
            // screenshots of the unchanged NPayRootView
            else if args.contains("s_payments") { NPayRootView().task { await wait(1.5); await selectTab("Payments") } }
            else if args.contains("s_typed") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill() } }
            else if args.contains("s_success") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Send Demo Payment") } }
            else if args.contains("s_home") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Send Demo Payment"); await press("Back to Dashboard") } }
            else if args.contains("s_history") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Send Demo Payment"); await press("Back to Dashboard"); await selectTab("History") } }
            else if args.contains("s_detail") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Send Demo Payment"); await press("Back to Dashboard"); await selectTab("History"); await pressRow("Sent to ravi@npay") } }
            else if args.contains("s_account") { NPayRootView().task { await wait(1.5); await press("Account Details") } }
            else if args.contains("s_keep") { NPayRootView().task { await wait(1.5); await press("Account Details"); await selectTab("History"); await pressRow("Coffee Shop"); await selectTab("Home") } }
            else if args.contains("s_profile") { NPayRootView().task { await wait(1.5); await selectTab("Profile") } }
            else if args.contains("s_settings") { NPayRootView().task { await wait(1.5); await selectTab("Profile"); await press("Settings") } }
            else { NPayRootView() }
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
@MainActor func element(_ label: String) -> NSObject? { elements().last { $0.accessibilityLabel == label && !String(describing: Swift.type(of: $0)).contains("TabButton") } }
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
@MainActor func tabBarController() -> UITabBarController? {
    func find(_ vc: UIViewController?) -> UITabBarController? {
        guard let vc else { return nil }
        if let t = vc as? UITabBarController { return t }
        for c in vc.children { if let t = find(c) { return t } }
        return find(vc.presentedViewController)
    }
    for w in allWindows() { if let t = find(w.rootViewController) { return t } }
    return nil
}
@MainActor func selectTab(_ title: String) async {
    // Tab buttons don't respond to accessibility activation in the simulator; select the tab as a tap does:
    // ask the delegate, select, tell the delegate.
    guard let tbc = tabBarController(), let vcs = tbc.viewControllers,
          let vc = vcs.first(where: { $0.tabBarItem.title == title }) else { print("no tab \(title)"); return }
    print("[tab \"\(title)\"]")
    if tbc.delegate?.tabBarController?(tbc, shouldSelect: vc) ?? true {
        tbc.selectedViewController = vc
        tbc.delegate?.tabBarController?(tbc, didSelect: vc)
    }
    await wait(1.2)
}
@MainActor func pressRow(_ prefix: String) async {   // a List row containing a label that starts with prefix
    guard let e = elements().last(where: { ($0.accessibilityLabel ?? "").hasPrefix(prefix) && !String(describing: Swift.type(of: $0)).contains("Tab") }) else { print("no row \(prefix)"); return }
    print("[activate row \"\(prefix)…\"]")
    _ = e.accessibilityActivate()
    await wait(1.2)
}
@MainActor func visible(_ what: String) {
    let keep = ["₹", "Sent to", "Recorded", "Account", "Holder", "Coffee", "Screen", "Title", "Amount", "Profile", "NPay Demo User", "Count"]
    let skip = ["Send Demo Payment", "Back to Dashboard", "Amount (₹)", "Account Details"]
    var seen = Set<String>()
    let shown = labels().filter { l in keep.contains { l.contains($0) } && !skip.contains(l) && !l.hasPrefix("Available Balance") }
    print("\(what): " + shown.filter { seen.insert($0).inserted }.prefix(6).joined(separator: " | "))
}
@MainActor func fill() async {
    await press("Recipient ID", quiet: true)
    await type("ravi@npay")
    await press("Amount (₹)", quiet: true)
    await type("1500.50")
}

// MARK: - Runs

@MainActor func selection() async {
    await wait(1.5)
    await selectTab("History")
    await selectTab("Home")
    await press("View All Transactions")
}
@MainActor func traceRun() async {
    await wait(1.5)
    print("-- Home: Account Details"); await press("Account Details", quiet: true)
    print("-- History tab, open Coffee Shop"); await selectTab("History"); await pressRow("Coffee Shop")
    print("-- Home tab again"); await selectTab("Home")
    visible("   on screen")
    print("-- Payments tab: pay ₹1,500.50"); await selectTab("Payments"); await fill(); await press("Send Demo Payment", quiet: true)
    print("-- Back to Dashboard"); await press("Back to Dashboard", quiet: true)
    visible("   on screen")
}
@MainActor func lifetime() async {
    await wait(1.5)
    print("-- History tab"); await selectTab("History")
    print("-- Home tab"); await selectTab("Home")
    print("-- History tab"); await selectTab("History")
    print("-- done")
}
@MainActor func observe() async {
    await wait(1.5)
    print("-- History tab (built)"); await selectTab("History")
    print("-- Profile tab (built)"); await selectTab("Profile")
    print("-- Home tab, Pay ₹1,500.50"); await selectTab("Home"); await press("Pay ₹1,500.50", quiet: true)
    print("-- done")
}
@MainActor func draft() async {
    await wait(1.5)
    await selectTab("Payments"); await fill()
    print("amount field: \"\(textField("Amount (₹)")?.text ?? "?")\"")
    await selectTab("History")
    await selectTab("Payments")
    print("after History and back, amount field: \"\(textField("Amount (₹)")?.text ?? "?")\", recipient: \"\(textField("Recipient ID")?.text ?? "?")\"")
}
@MainActor func verify() async {
    await wait(1.5)
    visible("1. Home")
    for t in ["Payments", "History", "Profile", "Home"] { await selectTab(t) }
    await selectTab("Payments"); await fill()
    print("   Send Demo Payment \(enabled("Send Demo Payment"))")
    await press("Send Demo Payment")
    visible("2. after Send")
    await press("Back to Dashboard")
    visible("3. Home")
    await selectTab("History")
    await pressRow("Sent to ravi@npay")
    visible("4. detail")
    await selectTab("Home")
    visible("5. Home again")
}

// MARK: - Experiments

struct TabExperiment: View {   // Section 2
    var body: some View {
        TabView {
            Text("Home Screen")
                .tabItem {
                    Label("Home", systemImage: "house")
                }

            Text("History Screen")
                .tabItem {
                    Label("History", systemImage: "clock")
                }
        }
    }
}

struct SelectionLab: View {   // Sections 4 and 6
    @State private var selectedTab: NPayTab = .home

    var body: some View {
        TabView(selection: $selectedTab) {
            Button("View All Transactions") {
                selectedTab = .history
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            Text("Payments")
                .tabItem {
                    Label("Payments", systemImage: "arrow.up.right")
                }
                .tag(NPayTab.payments)

            Text("History")
                .tabItem {
                    Label("History", systemImage: "clock")
                }
                .tag(NPayTab.history)

            Text("Profile")
                .tabItem {
                    Label("Profile", systemImage: "person")
                }
                .tag(NPayTab.profile)
        }
        .onChange(of: selectedTab) { oldTab, newTab in
            print("selectedTab:", oldTab, "→", newTab)
        }
    }
}

struct TracedRootView: View {   // NPayRootView plus prints of the router's state
    @State private var router = NPayRouter()
    @State private var store = NPayStore()

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {
            NavigationStack(path: $router.homePath) {
                HomeScreen(store: store, router: router)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem { Label("Home", systemImage: "house") }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsScreen(store: store, router: router)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem { Label("Payments", systemImage: "arrow.up.right") }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen(transactions: store.transactions)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem { Label("History", systemImage: "clock") }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem { Label("Profile", systemImage: "person") }
            .tag(NPayTab.profile)
        }
        .onChange(of: router.selectedTab) { _, tab in print("   selectedTab:", tab) }
        .onChange(of: router.homePath) { _, p in print("   homePath:", p.map(short)) }
        .onChange(of: router.paymentsPath) { _, p in print("   paymentsPath:", p.map(short)) }
        .onChange(of: router.historyPath) { _, p in print("   historyPath:", p.map(short)) }
    }

    private func short(_ r: NPayRoute) -> String {
        switch r {
        case .accountDetails: "accountDetails"
        case .paymentSuccess(let id): "paymentSuccess(\(id.uuidString.prefix(8))…)"
        case .transactionDetails(let id): "transactionDetails(\(id.uuidString.prefix(8))…)"
        case .settings: "settings"
        }
    }

    @ViewBuilder
    private func destination(_ route: NPayRoute) -> some View {
        switch route {
        case .accountDetails: AccountDetailsScreen(balancePaise: store.balancePaise)
        case .paymentSuccess(let id): PaymentSuccessScreen(transactionID: id, onDone: { router.returnHome() })
        case .transactionDetails(let id):
            if let t = store.transactions.first(where: { $0.id == id }) { TransactionDetailScreen(transaction: t) }
        case .settings: SettingsScreen()
        }
    }
}

struct LifetimeLab: View {   // Section 8: when is each tab built, and does it stay?
    var body: some View {
        TabView {
            Probe(name: "Home").tabItem { Label("Home", systemImage: "house") }
            Probe(name: "Payments").tabItem { Label("Payments", systemImage: "arrow.up.right") }
            Probe(name: "History").tabItem { Label("History", systemImage: "clock") }
            Probe(name: "Profile").tabItem { Label("Profile", systemImage: "person") }
        }
    }
}
struct Probe: View {
    let name: String
    @State private var made = Date.now.formatted(.dateTime.minute().second())
    var body: some View {
        let _ = print("   \(name).body")
        Text("\(name) Screen")
            .onAppear { print("   \(name).onAppear (state from \(made))") }
            .onDisappear { print("   \(name).onDisappear") }
    }
}

@MainActor @Observable final class LabStore {   // Section 16: which tabs re-evaluate after a payment?
    var balancePaise = 2_500_000
    var transactions: [String] = ["Coffee Shop"]
    var profileName = "NPay Demo User"
}
struct ObservationLab: View {
    @State private var store = LabStore()
    var body: some View {
        TabView {
            BalanceTab(store: store).tabItem { Label("Home", systemImage: "house") }
            ListTab(store: store).tabItem { Label("History", systemImage: "clock") }
            NameTab(store: store).tabItem { Label("Profile", systemImage: "person") }
        }
    }
}
struct BalanceTab: View {   // reads balancePaise
    let store: LabStore
    var body: some View {
        let _ = print("   BalanceTab.body (reads balancePaise)")
        VStack {
            Text(Money.display(store.balancePaise))
            Button("Pay ₹1,500.50") {
                store.balancePaise -= 150_050
                store.transactions.insert("Sent to ravi@npay", at: 0)
            }
        }
    }
}
struct ListTab: View {   // reads transactions
    let store: LabStore
    var body: some View {
        let _ = print("   ListTab.body (reads transactions)")
        Text(store.transactions.joined(separator: ", "))
    }
}
struct NameTab: View {   // reads profileName only
    let store: LabStore
    var body: some View {
        let _ = print("   NameTab.body (reads profileName)")
        Text(store.profileName)
    }
}

// ===================== Complete code through Lesson 3.3 =====================

// App/NPayRouter.swift

enum NPayTab: Hashable {
    case home
    case payments
    case history
    case profile
}

enum NPayRoute: Hashable {
    case accountDetails
    case paymentSuccess(UUID)
    case transactionDetails(UUID)
    case settings
}

@MainActor
@Observable
final class NPayRouter {

    var selectedTab: NPayTab = .home

    var homePath: [NPayRoute] = []
    var paymentsPath: [NPayRoute] = []
    var historyPath: [NPayRoute] = []
    var profilePath: [NPayRoute] = []

    func select(_ tab: NPayTab) {
        selectedTab = tab
    }

    func showPaymentSuccess(_ id: UUID) {
        selectedTab = .payments
        paymentsPath.append(.paymentSuccess(id))
    }

    func returnHome() {
        paymentsPath.removeAll()
        selectedTab = .home
    }
}

// Store/NPayStore.swift

@MainActor
@Observable
final class NPayStore {

    var balancePaise = 2_500_000

    var transactions: [Transaction] = [
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

    func recordDemoPayment(
        recipient: String,
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

        let id = UUID()

        balancePaise -= amountPaise

        transactions.insert(
            Transaction(
                id: id,
                title: "Sent to \(trimmed)",
                amountPaise: -amountPaise,
                date: .now
            ),
            at: 0
        )

        return id
    }
}

// App/NPayRootView.swift

struct NPayRootView: View {

    @State private var router = NPayRouter()
    @State private var store = NPayStore()

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {

            NavigationStack(path: $router.homePath) {
                HomeScreen(store: store, router: router)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsScreen(
                    store: store,
                    router: router
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Payments", systemImage: "arrow.up.right")
            }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen(
                    transactions: store.transactions
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
    }

    // One mapping from route to screen, registered in every tab's stack
    @ViewBuilder
    private func destination(_ route: NPayRoute) -> some View {
        switch route {
        case .accountDetails:
            AccountDetailsScreen(balancePaise: store.balancePaise)

        case .paymentSuccess(let id):
            PaymentSuccessScreen(
                transactionID: id,
                onDone: { router.returnHome() }
            )

        case .transactionDetails(let id):
            if let transaction = store.transactions.first(where: { $0.id == id }) {
                TransactionDetailScreen(transaction: transaction)
            } else {
                ContentUnavailableView(
                    "Transaction not found",
                    systemImage: "questionmark.circle"
                )
            }

        case .settings:
            SettingsScreen()
        }
    }
}

// Models/Money.swift and Models/Transaction.swift: unchanged from Lesson 3.1

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

struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}

// Components/BalanceCard.swift and Components/TransactionRow.swift: unchanged from Lesson 3.1

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

// Screens/HomeScreen.swift

struct HomeScreen: View {
    let store: NPayStore
    let router: NPayRouter

    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                BalanceCard(balancePaise: store.balancePaise)

                HStack(spacing: 12) {
                    Button {
                        router.select(.payments)
                    } label: {
                        Label("Send Money", systemImage: "arrow.up.right")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                Color.blue.opacity(0.1),
                                in: RoundedRectangle(cornerRadius: 12)
                            )
                    }

                    Button {
                        router.select(.history)
                    } label: {
                        Label("History", systemImage: "clock")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(
                                Color.blue.opacity(0.1),
                                in: RoundedRectangle(cornerRadius: 12)
                            )
                    }
                }

                NavigationLink(value: NPayRoute.accountDetails) {
                    Label("Account Details", systemImage: "person.text.rectangle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                VStack(alignment: .leading, spacing: 12) {
                    Text("Recent Transactions")
                        .font(.headline)

                    ForEach(store.transactions.prefix(3)) { transaction in
                        TransactionRow(transaction: transaction)
                        Divider()
                    }
                }
                .frame(maxWidth: .infinity, alignment: .leading)
            }
            .padding()
        }
        .navigationTitle("NPay")
    }
}

struct AccountDetailsScreen: View {
    let balancePaise: Int

    var body: some View {
        List {
            LabeledContent("Account", value: "NPay Demo Account")
            LabeledContent("Holder", value: "NPay Demo User")
            LabeledContent("Available", value: Money.display(balancePaise))
        }
        .navigationTitle("Account Details")
    }
}

// Screens/PaymentsScreen.swift (the 3.2 PaymentScreen as a tab: it reads the store and asks the router)

struct PaymentsScreen: View {
    let store: NPayStore
    let router: NPayRouter

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
            && amount <= store.balancePaise
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text(
                    "Available: \(Money.display(store.balancePaise))"
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

                    if let id = store.recordDemoPayment(
                        recipient: recipient,
                        amountPaise: amount
                    ) {
                        focusedField = nil
                        recipient = ""
                        amountText = ""
                        router.showPaymentSuccess(id)
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!isValid)
            }
            .padding()
        }
        .navigationTitle("Payments")
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

// Screens/PaymentSuccessScreen.swift: unchanged from Lesson 3.2

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

// Screens/HistoryScreen.swift (rows now push transaction details)

struct HistoryScreen: View {
    let transactions: [Transaction]

    var body: some View {
        List(transactions) { transaction in
            NavigationLink(value: NPayRoute.transactionDetails(transaction.id)) {
                TransactionRow(transaction: transaction)
            }
        }
        .navigationTitle("History")
    }
}

// Screens/TransactionDetailScreen.swift

struct TransactionDetailScreen: View {
    let transaction: Transaction

    var body: some View {
        List {
            LabeledContent("Title", value: transaction.title)
            LabeledContent("Amount", value: Money.display(transaction.amountPaise))
            LabeledContent(
                "Date",
                value: transaction.date.formatted(date: .abbreviated, time: .shortened)
            )
            LabeledContent("ID") {
                Text(transaction.id.uuidString)
                    .font(.caption2.monospaced())
            }
        }
        .navigationTitle("Transaction")
    }
}

// Screens/ProfileScreen.swift

struct ProfileScreen: View {
    var body: some View {
        List {
            Section {
                HStack(spacing: 16) {
                    Image(systemName: "person.crop.circle.fill")
                        .font(.system(size: 48))
                        .foregroundStyle(.blue)

                    VStack(alignment: .leading, spacing: 4) {
                        Text("NPay Demo User")
                            .font(.headline)
                        Text("Account settings and preferences")
                            .font(.caption)
                            .foregroundStyle(.secondary)
                    }
                }
            }

            NavigationLink(value: NPayRoute.settings) {
                Label("Settings", systemImage: "gearshape")
            }
        }
        .navigationTitle("Profile")
    }
}

struct SettingsScreen: View {
    @State private var notifications = true

    var body: some View {
        List {
            Toggle("Payment notifications", isOn: $notifications)
            LabeledContent("Version", value: "Lesson 3.3 demo")
        }
        .navigationTitle("Settings")
    }
}
