import SwiftUI
import UIKit

// Lesson 4.6 evidence app: NPay's payment feature on SendPaymentUseCase (PaymentPolicy + AccountRepository). The
// repository is an adapter over NPayStore (ours), so Home and History keep one source of truth. The review sheet shows
// the immutable SendPaymentCommand and Confirm submits that same command. A DEBUG-only hook gives the driver the store.
@main
struct LabApp: App {
    init() { setvbuf(stdout, nil, _IONBF, 0) }

    var body: some Scene {
        WindowGroup {
            let a = ProcessInfo.processInfo.arguments
            NPayRootView().task {
                if a.contains("pay") { await pay() }
                else if a.contains("stale") { await stale(quiet: false) }
                else if a.contains("s_review") { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment", quiet: true) }
                else if a.contains("s_stale") { await stale(quiet: true) }
            }
        }
    }
}

@MainActor enum NPayDebug {
    static var router: NPayRouter?
    static var store: NPayStore?
    static var preferences: NPayPreferences?
    static var paymentService: (any PaymentService)?
    static func attach(_ r: NPayRouter, _ s: NPayStore, _ p: NPayPreferences) { router = r; store = s; preferences = p }
}

@MainActor func texts() -> [String] {
    var seen = Set<String>()
    return elements().flatMap { [$0.accessibilityLabel ?? "", $0.accessibilityValue ?? ""] }.filter { !$0.isEmpty && seen.insert($0).inserted }
}

@MainActor func pay() async {
    await wait(1.5)
    guard let store = NPayDebug.store else { return }
    await selectTab("Payments")
    await fill()
    await press("Review Payment", quiet: true)
    print("review sheet: " + texts().filter { $0 == "ravi@npay" || $0 == "₹1,500.50" }.joined(separator: ", "))
    await press("Confirm Demo Payment", quiet: true)
    await wait(1.5)
    print("after Confirm: \(labels().contains("Payment Recorded") ? "Payment Recorded" : "?"), sheet \(presented() == nil ? "closed" : "open"), paymentsPath \(NPayDebug.router?.paymentsPath.count ?? -1)")
    print("store: balancePaise \(store.balancePaise), transactions \(store.transactions.count)")
    await press("Back to Dashboard", quiet: true)
    print("Home: " + (labels().first { $0.contains("Available Balance") } ?? "?"))
    await selectTab("History")
    print("History top: " + (labels().first { $0.hasPrefix("Sent to") } ?? "?"))
    await selectTab("Payments")
    print("form afterwards: \(fields())")
}

@MainActor func stale(quiet: Bool) async {
    await wait(1.5)
    guard let store = NPayDebug.store else { return }
    await selectTab("Payments")
    await fill("20000")
    await press("Review Payment", quiet: true)
    _ = store.recordDemoPayment(recipient: "Electricity Board", amountPaise: 1_000_000)
    await press("Confirm Demo Payment", quiet: true)
    await wait(1.5)
    if !quiet {
        print("review ₹20,000; meanwhile ₹10,000 left; Confirm: balancePaise \(store.balancePaise), paymentsPath \(NPayDebug.router?.paymentsPath.count ?? -1)")
        print("screen: " + texts().filter { $0.contains("Unable") }.joined() + "; form \(fields())")
    }
}

@MainActor func alertButton(_ title: String) async {
    // Alert and dialog buttons don't respond to accessibility activation here; run the action's handler and dismiss,
    // which is what a tap on the button does.
    guard let alert = allWindows().compactMap({ w -> UIAlertController? in
        var vc = w.rootViewController
        while let p = vc?.presentedViewController { vc = p }
        return vc as? UIAlertController
    }).first, let action = alert.actions.first(where: { $0.title == title }) else { print("no alert button \(title)"); return }
    typealias Handler = @convention(block) (UIAlertAction) -> Void
    let handler = action.value(forKey: "handler").map { unsafeBitCast($0 as AnyObject, to: Handler.self) }
    print("[tap \"\(title)\"]")
    alert.dismiss(animated: true) { handler?(action) }
    await wait(1.5)
}
@MainActor func presented() -> UIViewController? {
    var vc = allWindows().first?.rootViewController
    var top: UIViewController?
    while let p = vc?.presentedViewController { top = p; vc = p }
    return top
}
@MainActor func dismissSheet() async {   // what a completed swipe-down does: the presented controller is dismissed
    guard let p = presented() else { print("nothing presented"); return }
    print("[swipe down]")
    p.dismiss(animated: true)
    await wait(1.2)
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
    let keep = ["₹", "Sent to", "Recorded", "Recipient", "Amount", "Current", "Store value", "Details"]
    let skip = ["Amount (₹)", "Recipient ID", "Review Payment", "Confirm Demo Payment", "Edit Details", "Back to Dashboard"]
    var seen = Set<String>()
    let shown = labels().filter { l in keep.contains { l.contains($0) } && !skip.contains(l) && !l.hasPrefix("Available Balance") }
    print("\(what): " + shown.filter { seen.insert($0).inserted }.prefix(6).joined(separator: " | "))
}
@MainActor func fill(_ amount: String = "1500.50") async {
    await press("Recipient ID", quiet: true)
    await type("ravi@npay")
    await press("Amount (₹)", quiet: true)
    await type(amount)
}
@MainActor func fields() -> String {
    "recipient \"\(textField("Recipient ID")?.text ?? "?")\", amount \"\(textField("Amount (₹)")?.text ?? "?")\""
}



@MainActor func style() -> String {
    switch allWindows().first?.traitCollection.userInterfaceStyle {
    case .dark: "dark"
    case .light: "light"
    default: "unspecified"
    }
}
@MainActor func toAppearance() async {
    await wait(1.5)
    await selectTab("Profile")
    await press("Appearance", quiet: true)
}
@MainActor func findViews<T: UIView>(_ type: T.Type) -> [T] {
    func walk(_ v: UIView) -> [T] { ((v as? T).map { [$0] } ?? []) + v.subviews.flatMap(walk) }
    return allWindows().flatMap { walk($0) }
}
@MainActor func segment(_ title: String) async {   // select a segment as a tap does
    guard let control = findViews(UISegmentedControl.self).first,
          let i = (0..<control.numberOfSegments).first(where: { control.titleForSegment(at: $0) == title }) else { print("no segment \(title)"); return }
    print("[segment \"\(title)\"]")
    control.selectedSegmentIndex = i
    control.sendActions(for: .valueChanged)
    await wait(1.2)
}
@MainActor func toggleSwitch(_ label: String) async {
    if let e = element(label), e.accessibilityActivate() { print("[toggle \"\(label)\"]"); await wait(1); return }
    guard let s = findViews(UISwitch.self).first else { print("no switch"); return }
    print("[toggle \"\(label)\"]")
    s.setOn(!s.isOn, animated: true)
    s.sendActions(for: .valueChanged)
    await wait(1.2)
}


// ===================== Complete code through Lesson 4.6 (SendPaymentUseCase) =====================

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
    case appearance
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

// App/NPayAccessibilityID.swift (section 24)

enum NPayAccessibilityID {
    static let balanceCard = "npay.balanceCard"
    static let recipientField = "npay.recipientField"
    static let amountField = "npay.amountField"
    static let sendButton = "npay.sendButton"
    static let transactionList = "npay.transactionList"
}

// App/NPayPreferences.swift (section 17)

enum NPayAppearance: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var title: String {
        rawValue.capitalized
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system:
            return nil
        case .light:
            return .light
        case .dark:
            return .dark
        }
    }
}

@MainActor
@Observable
final class NPayPreferences {
    var appearance: NPayAppearance = .system
    var showDemoBadge = true
}

// Screens/AppearanceSettingsView.swift (section 19)

struct AppearanceSettingsView: View {

    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        @Bindable var preferences = preferences

        Form {
            Section("Appearance") {
                Picker(
                    "Theme",
                    selection: $preferences.appearance
                ) {
                    ForEach(NPayAppearance.allCases) { option in
                        Text(option.title)
                            .tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section("Display") {
                Toggle(
                    "Show Demo Badge",
                    isOn: $preferences.showDemoBadge
                )
            }
        }
        .navigationTitle("Appearance")
    }
}

// Domain/PaymentValidator.swift (Lesson 4.1, section 5)

enum PaymentValidationError: Error {
    case emptyRecipient
    case invalidAmount
    case insufficientBalance
}

struct PaymentValidator {

    func validate(
        recipient: String,
        amountPaise: Int,
        balancePaise: Int
    ) throws {

        guard !recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        ).isEmpty else {
            throw PaymentValidationError.emptyRecipient
        }

        guard amountPaise > 0 else {
            throw PaymentValidationError.invalidAmount
        }

        guard amountPaise <= balancePaise else {
            throw PaymentValidationError.insufficientBalance
        }
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

    // Lesson 4.2: the payment form state moved to PaymentViewModel

    func recordDemoPayment(
        recipient: String,
        amountPaise: Int
    ) -> UUID? {

        // Lesson 4.1: the rules live in PaymentValidator
        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amountPaise,
                balancePaise: balancePaise
            )
        } catch {
            return nil
        }

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

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
    @State private var preferences = NPayPreferences()

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
                PaymentsFeatureRoot(   // Lesson 4.2: owns the PaymentViewModel
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
        .environment(preferences)
        .preferredColorScheme(
            preferences.appearance.colorScheme
        )
        #if DEBUG
        .onAppear { NPayDebug.attach(router, store, preferences) }   // evidence hook for the lab driver; not part of NPay
        #endif
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

        case .appearance:
            AppearanceSettingsView()
        }
    }
}

// DesignSystem/NPayTheme.swift (section 3)

enum NPayTheme {

    enum Colors {
        static let primary = Color(
            red: 0.10,
            green: 0.34,
            blue: 0.65
        )

        static let success = Color.green

        static let cardBackground =
            Color.blue.opacity(0.06)
    }

    enum Spacing {
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
    }

    enum Radius {
        static let small: CGFloat = 10
        static let card: CGFloat = 18
    }
}

// DesignSystem/NPayButton.swift (section 17)

struct NPayButton: View {
    let title: String
    let symbol: String?
    let action: () -> Void

    init(
        _ title: String,
        symbol: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.symbol = symbol
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                if let symbol {
                    Image(systemName: symbol)
                }

                Text(title)
            }
            .font(.headline)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(
                cornerRadius: NPayTheme.Radius.small
            )
        )
    }
}

// DesignSystem/NPayCard.swift (section 7)

struct NPayCard<Content: View>: View {

    @ViewBuilder let content: Content

    var body: some View {
        content
            .padding(NPayTheme.Spacing.medium)
            .frame(maxWidth: .infinity)
            .background(
                NPayTheme.Colors.cardBackground,
                in: RoundedRectangle(
                    cornerRadius: NPayTheme.Radius.card
                )
            )
    }
}

// DesignSystem/NPayCardModifier.swift (section 9)

struct NPayCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(
                NPayTheme.Colors.cardBackground,
                in: RoundedRectangle(cornerRadius: 18)
            )
    }
}

extension View {
    func npayCardStyle() -> some View {
        modifier(NPayCardModifier())
    }
}

// DesignSystem/NPaySectionHeader.swift (section 10)

struct NPaySectionHeader: View {
    let title: String
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        HStack {
            Text(title)
                .font(.headline)

            Spacer()

            if let actionTitle,
               let action {
                Button(actionTitle, action: action)
                    .font(.subheadline)
            }
        }
    }
}

// Components/QuickAction.swift (Lesson 2.7's component, back for the quick actions)

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

// Components/NPayQuickActions.swift (section 19)

struct NPayQuickActions: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) {
                actionViews
            }

            VStack(spacing: 12) {
                actionViews
            }
        }
    }

    @ViewBuilder
    private var actionViews: some View {
        QuickAction(
            symbol: "arrow.up.right",
            title: "Send",
            action: onSend
        )

        QuickAction(
            symbol: "arrow.down.left",
            title: "Request",
            action: onRequest
        )

        QuickAction(
            symbol: "clock",
            title: "History",
            action: onHistory
        )
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

    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {

            Text("Available Balance")
                .font(.subheadline)

            Text(Money.display(balancePaise))
                .font(.largeTitle.bold())
                .contentTransition(.numericText())
                .animation(
                    .easeInOut(duration: 0.4),
                    value: balancePaise
                )

            if preferences.showDemoBadge {
                Text("DEMO ACCOUNT")
                    .font(.caption.bold())
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(
                        .white.opacity(0.18),
                        in: Capsule()
                    )
            }
        }
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(24)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(cornerRadius: NPayTheme.Radius.card)
        )
        .accessibilityElement(children: .combine)
        .accessibilityIdentifier(NPayAccessibilityID.balanceCard)
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
        // section 21: one element, read as meaning rather than layout
        .accessibilityElement(children: .ignore)
        .accessibilityLabel(transaction.title)
        .accessibilityValue(
            Money.display(transaction.amountPaise)
        )
    }
}

// Screens/HomeScreen.swift

struct HomeScreen: View {
    let store: NPayStore
    let router: NPayRouter

    @State private var showRequestInfo = false

    var body: some View {
        ScrollView {
            VStack(spacing: NPayTheme.Spacing.large) {
                BalanceCard(balancePaise: store.balancePaise)

                NPayQuickActions(
                    onSend: { router.select(.payments) },
                    onRequest: { showRequestInfo = true },
                    onHistory: { router.select(.history) }
                )

                NavigationLink(value: NPayRoute.accountDetails) {
                    Label("Account Details", systemImage: "person.text.rectangle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                NPayCard {
                    VStack(alignment: .leading, spacing: 12) {
                        NPaySectionHeader(
                            title: "Recent Transactions",
                            actionTitle: "View All"
                        ) {
                            router.select(.history)
                        }

                        ForEach(store.transactions.prefix(3)) { transaction in
                            TransactionRow(transaction: transaction)
                        }
                    }
                }
            }
            .padding()
        }
        .navigationTitle("NPay")
        .alert("Request money", isPresented: $showRequestInfo) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("Requests aren't part of the demo yet.")
        }
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

// Domain/PaymentRequest.swift and Domain/PaymentService.swift (Lesson 4.4; still in the project, no longer used by the payment ViewModel)

struct PaymentRequest {
    let recipient: String
    let amountPaise: Int
}

struct PaymentReceipt {
    let transactionID: UUID
    let recipient: String
    let amountPaise: Int
}

@MainActor
protocol PaymentService {
    func send(_ request: PaymentRequest) async throws -> PaymentReceipt
}

// Services/DemoPaymentService.swift (section 4: uses the shared NPayStore)

enum PaymentServiceError: Error {
    case rejected
}

@MainActor
final class DemoPaymentService: PaymentService {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        guard let id = store.recordDemoPayment(
            recipient: request.recipient,
            amountPaise: request.amountPaise
        ) else {
            throw PaymentServiceError.rejected
        }

        return PaymentReceipt(
            transactionID: id,
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )
    }
}

// Services/MockPaymentService.swift (section 8)

@MainActor
final class MockPaymentService: PaymentService {

    var shouldFail = false
    private(set) var requests: [PaymentRequest] = []

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {

        requests.append(request)

        if shouldFail {
            throw PaymentServiceError.rejected
        }

        return PaymentReceipt(
            transactionID: UUID(),
            recipient: request.recipient,
            amountPaise: request.amountPaise
        )
    }
}

// Domain/PaymentAmount.swift, PaymentRecipient.swift, SendPaymentCommand.swift (Lesson 4.6, sections 3-5)

struct PaymentAmount: Equatable, Sendable {
    let paise: Int

    init(paise: Int) throws {
        guard paise > 0 else {
            throw PaymentDomainError.invalidAmount
        }

        self.paise = paise
    }
}

enum PaymentDomainError: Error {
    case invalidAmount
    case invalidRecipient
    case insufficientBalance
    case limitExceeded
}

struct PaymentRecipient: Equatable, Sendable {
    let identifier: String

    init(_ identifier: String) throws {
        let trimmed = identifier.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty else {
            throw PaymentDomainError.invalidRecipient
        }

        self.identifier = trimmed
    }
}

struct SendPaymentCommand: Sendable {
    let recipient: PaymentRecipient
    let amount: PaymentAmount
}

// Domain/AccountRepository.swift (Lesson 4.5, sections 4-5)

struct PaymentRecord: Identifiable, Sendable {
    let id: UUID
    let recipient: String
    let amountPaise: Int
    let createdAt: Date
}

struct AccountSnapshot: Sendable {
    let balancePaise: Int
    let transactions: [PaymentRecord]
}

enum AccountRepositoryError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
}

protocol AccountRepository: Sendable {
    func fetchSnapshot() async throws -> AccountSnapshot

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord
}

// Data/NPayStoreAccountRepository.swift (integration, ours): the repository contract over NPay's existing store, so
// Home and History keep one source of truth while payments go through the use case
@MainActor
final class NPayStoreAccountRepository: AccountRepository {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func fetchSnapshot() async throws -> AccountSnapshot {
        AccountSnapshot(
            balancePaise: store.balancePaise,
            transactions: store.transactions
                .filter { $0.amountPaise < 0 }
                .map { PaymentRecord(id: $0.id, recipient: $0.title, amountPaise: -$0.amountPaise, createdAt: $0.date) }
        )
    }

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord {
        let trimmed = recipient.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw AccountRepositoryError.invalidRecipient }
        guard amountPaise > 0 else { throw AccountRepositoryError.invalidAmount }

        // The store checks the balance and records the payment in one main-actor call (no suspension)
        guard let id = store.recordDemoPayment(recipient: trimmed, amountPaise: amountPaise) else {
            throw AccountRepositoryError.insufficientBalance
        }
        return PaymentRecord(id: id, recipient: trimmed, amountPaise: amountPaise, createdAt: .now)
    }
}

// Application/PaymentPolicy.swift and SendPaymentUseCase.swift (Lesson 4.6, section 18)

struct PaymentPolicy: Sendable {
    let maximumPerPaymentPaise: Int

    func validate(_ amount: PaymentAmount) throws {
        guard amount.paise <= maximumPerPaymentPaise else {
            throw PaymentDomainError.limitExceeded
        }
    }
}

struct SendPaymentUseCase {
    let repository: any AccountRepository
    let policy: PaymentPolicy

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        try policy.validate(command.amount)

        return try await repository.recordPayment(
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise
        )
    }
}

// App/NPayFactory.swift (Lesson 4.6, section 19; availableBalance is ours, for Lesson 4.2's form validation)

@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        repository: any AccountRepository,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) -> PaymentViewModel {

        let policy = PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )

        let useCase = SendPaymentUseCase(
            repository: repository,
            policy: policy
        )

        return PaymentViewModel(
            sendPayment: useCase,
            availableBalance: availableBalance
        )
    }
}

// Features/Payments/ValidatedPaymentRequest.swift (now wraps the immutable command the user reviews)

struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let command: SendPaymentCommand
}

// Features/Payments/PaymentViewModel.swift (Lesson 4.6: a SendPaymentUseCase replaces the PaymentService)

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?
    var isSubmitting = false

    private let sendPayment: SendPaymentUseCase
    private let availableBalance: @MainActor () -> Int   // integration (ours): read-only balance

    init(
        sendPayment: SendPaymentUseCase,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) {
        self.sendPayment = sendPayment
        self.availableBalance = availableBalance
    }

    var availableBalancePaise: Int {
        availableBalance()
    }

    var parsedAmountPaise: Int? {
        Money.parsePaise(amountText)
    }

    // Lesson 4.2, section 7
    func validate(
        availableBalancePaise: Int
    ) -> Bool {

        guard let amount = parsedAmountPaise else {
            return false
        }

        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amount,
                balancePaise: availableBalancePaise
            )

            return true
        } catch {
            return false
        }
    }

    // Integration (ours): parse the form into domain values, the snapshot the sheet shows and Confirm submits
    func prepareCommand() -> ValidatedPaymentRequest? {
        do {
            guard let paise = parsedAmountPaise,
                  validate(availableBalancePaise: availableBalancePaise) else {
                throw PaymentDomainError.invalidAmount
            }

            let command = SendPaymentCommand(
                recipient: try PaymentRecipient(recipient),
                amount: try PaymentAmount(paise: paise)
            )

            errorMessage = nil
            return ValidatedPaymentRequest(command: command)
        } catch {
            errorMessage = "Please check payment details"
            return nil
        }
    }

    // Lesson 4.6, section 20: submit exactly the command the user reviewed
    func submit(
        _ command: SendPaymentCommand
    ) async -> PaymentRecord? {

        guard !isSubmitting else {
            return nil
        }

        isSubmitting = true
        defer { isSubmitting = false }

        do {
            let result = try await sendPayment.execute(command)

            recipient = ""
            amountText = ""
            errorMessage = nil

            return result
        } catch {
            errorMessage = "Unable to complete demo payment"
            return nil
        }
    }

    // Lesson 3.4's Discard Draft
    func discardDraft() {
        recipient = ""
        amountText = ""
        errorMessage = nil
    }
}

// Features/Payments/PaymentsFeatureRoot.swift (Lesson 4.2; the ViewModel comes from NPayFactory)

struct PaymentsFeatureRoot: View {
    @State private var viewModel: PaymentViewModel
    let router: NPayRouter

    init(store: NPayStore, router: NPayRouter) {
        _viewModel = State(
            initialValue: NPayFactory.makePaymentViewModel(   // Lesson 4.6
                repository: NPayStoreAccountRepository(store: store),
                availableBalance: { store.balancePaise }
            )
        )
        self.router = router
    }

    var body: some View {
        PaymentsScreen(viewModel: viewModel, router: router)
    }
}

// Screens/PaymentsScreen.swift (presentation only: layout, focus, the review sheet, navigation on success)

struct PaymentsScreen: View {
    @Bindable var viewModel: PaymentViewModel
    let router: NPayRouter

    @State private var review: ValidatedPaymentRequest?
    @State private var pendingSuccessID: UUID?
    @State private var confirmDiscard = false

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text(
                    "Available: \(Money.display(viewModel.availableBalancePaise))"
                )
                .foregroundStyle(.secondary)

                TextField(
                    "Recipient ID",
                    text: $viewModel.recipient
                )
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .recipient
                )
                .accessibilityIdentifier(NPayAccessibilityID.recipientField)
                .accessibilityLabel("Recipient")
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .amount
                }

                TextField(
                    "Amount (₹)",
                    text: $viewModel.amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )
                .accessibilityIdentifier(NPayAccessibilityID.amountField)
                .accessibilityLabel("Amount in rupees")

                // Section 21: the ViewModel reports the error; the view decides how to show it
                if let errorMessage = viewModel.errorMessage {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundStyle(.red)
                } else if !viewModel.amountText.isEmpty
                            && !viewModel.validate(availableBalancePaise: viewModel.availableBalancePaise) {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                NPayButton("Review Payment", symbol: "doc.text.magnifyingglass") {
                    focusedField = nil
                    review = viewModel.prepareCommand()
                }
                .disabled(!viewModel.validate(availableBalancePaise: viewModel.availableBalancePaise))
                .accessibilityIdentifier(NPayAccessibilityID.sendButton)

                Button("Discard Draft", role: .destructive) {
                    confirmDiscard = true
                }
                .disabled(viewModel.recipient.isEmpty && viewModel.amountText.isEmpty)
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
        .sheet(
            item: $review,
            onDismiss: {
                // Section 22: the ViewModel returned an ID; the view asks the router to navigate
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    router.showPaymentSuccess(id)
                }
            }
        ) { request in

            PaymentReviewSheet(request: request) {
                // Lesson 4.6: confirmation submits the exact command the user reviewed
                Task {
                    pendingSuccessID = await viewModel.submit(request.command)?.id
                    self.review = nil
                }
            }
        }
        .alert("Discard payment draft?", isPresented: $confirmDiscard) {
            Button("Discard", role: .destructive) {
                viewModel.discardDraft()
            }

            Button("Cancel", role: .cancel) {}
        }
    }
}

// Screens/PaymentReviewSheet.swift (shows the validated request, not the live form)

struct PaymentReviewSheet: View {
    let request: ValidatedPaymentRequest
    let onConfirm: () -> Void

    @State private var isProcessing = false

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: request.command.recipient.identifier
            )

            LabeledContent(
                "Amount",
                value: Money.display(request.command.amount.paise)
            )

            NPayButton("Confirm Demo Payment") {
                guard !isProcessing else {
                    return
                }

                isProcessing = true
                onConfirm()
            }
            .disabled(isProcessing)

            Button("Edit Details") {
                dismiss()
            }
            .buttonStyle(.bordered)
        }
        .padding()
        .presentationDetents([.medium, .large])
        .interactiveDismissDisabled(isProcessing)
    }
}

// Screens/PaymentSuccessScreen.swift: unchanged from Lesson 3.2

struct PaymentSuccessScreen: View {
    let transactionID: UUID
    let onDone: () -> Void

    @Environment(\.accessibilityReduceMotion)
    private var reduceMotion

    @State private var showContent = false

    var body: some View {
        VStack(spacing: 24) {

            if showContent {
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 80))
                    .foregroundStyle(.green)
                    .transition(
                        .scale.combined(with: .opacity)
                    )
                    .accessibilityHidden(true)   // Lesson 3.12: was read as "Selected"; the text says it all
            }

            Text("Payment Recorded")
                .font(.title.bold())

            Text("Your demo payment was successful.")
                .foregroundStyle(.secondary)

            Text(transactionID.uuidString)
                .font(.caption2.monospaced())
                .multilineTextAlignment(.center)

            NPayButton("Back to Dashboard") {
                onDone()
            }
        }
        .padding()
        .navigationTitle("Payment Success")
        .navigationBarBackButtonHidden()
        .onAppear {
            if reduceMotion {
                showContent = true
            } else {
                withAnimation(
                    .spring(
                        response: 0.45,
                        dampingFraction: 0.7
                    )
                ) {
                    showContent = true
                }
            }
        }
    }
}

// Screens/HistoryScreen.swift (rows now push transaction details)

struct HistoryScreen: View {
    let transactions: [Transaction]

    @State private var searchText = ""

    // section 13: recomputed when the search text (or the transactions) change
    private var filteredTransactions: [Transaction] {
        guard !searchText.isEmpty else {
            return transactions
        }

        return transactions.filter {
            $0.title.localizedCaseInsensitiveContains(
                searchText
            )
        }
    }

    var body: some View {
        List(filteredTransactions) { transaction in
            NavigationLink(value: NPayRoute.transactionDetails(transaction.id)) {
                TransactionRow(transaction: transaction)
            }
        }
        .searchable(text: $searchText)
        .accessibilityIdentifier(NPayAccessibilityID.transactionList)
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

            NavigationLink(value: NPayRoute.appearance) {
                Label("Appearance", systemImage: "circle.lefthalf.filled")
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
