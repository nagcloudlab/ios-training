import SwiftUI
import UIKit

// Lesson 3.8 evidence app. The text's GeometryExperiment, LayoutIdentityExperiment, CounterView, AdaptiveActions and
// both NPayQuickActions versions run as written (the Section 6 GeometryReader version renamed NPayQuickActionsGeo so both
// compile); the complete code integrates the Section 19 version into the 3.7 app (authored: the text names this as its
// remaining task). A logging Layout prints each proposal and answer. Run on an iPhone 17, an iPhone SE (3rd
// generation) and an iPad Air 11-inch, at the default and the largest accessibility text size, and in landscape
// (requested with UIWindowScene.requestGeometryUpdate). Driver as in 3.7.
@main
struct LabApp: App {
    init() { setvbuf(stdout, nil, _IONBF, 0) }   // unbuffered, so every line reaches the console

    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("proposal") { ProposalLab() }
            else if args.contains("order") { OrderLab() }
            else if args.contains("geo") { GeometryExperiment().task { await geoReport() } }
            else if args.contains("geoland") { GeometryExperiment().task { await rotate(); await geoReport() } }
            else if args.contains("geoscroll") { GeoScrollLab() }
            else if args.contains("qa") { QuickActionsLab().task { await qaReport() } }
            else if args.contains("qageo") { QuickActionsLab().onAppear { QuickActionsLab.model.which = "geo" } }
            else if args.contains("qafit") { QuickActionsLab().onAppear { QuickActionsLab.model.which = "fit" } }
            else if args.contains("qaland") { QuickActionsLab().task { await rotate(); await qaReport() } }
            else if args.contains("identity") { IdentityLab().task { await identity() } }
            else if args.contains("safe") { SafeAreaLab() }
            else if args.contains("homeland") { NPayRootView().task { await rotate() } }
            else { NPayRootView() }
        }
    }
}

// MARK: - Runs

@MainActor func rotate() async {
    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene else { return }
    scene.requestGeometryUpdate(.iOS(interfaceOrientations: .landscapeRight)) { error in print("rotation error:", error) }
    await wait(1.5)
}
@MainActor func geoReport() async {
    await wait(1.5)
    print("screen labels: " + labels().filter { $0.hasPrefix("Width") || $0.hasPrefix("Height") }.prefix(2).joined(separator: ", "))
}
@MainActor func arrangement(_ name: String) -> String {
    let els = ["Send", "Request", "History"].compactMap { t in elements().last { ($0.accessibilityLabel ?? "").hasSuffix(t) && $0.accessibilityTraits.contains(.button) } }
    guard els.count == 3 else { return "\(name): not found" }
    let f = els.map(\.accessibilityFrame)
    let horizontal = f[0].maxX <= f[1].minX && f[1].maxX <= f[2].minX   // side by side, left to right
    return "\(name): \(horizontal ? "HStack" : "VStack"), buttons \(f.map { "\(Int($0.width))×\(Int($0.height))" }.joined(separator: ", "))"
}
@MainActor func qaReport() async {
    await wait(1.5)
    let w = allWindows().first.map { Int($0.bounds.width) } ?? 0
    let size = UIApplication.shared.preferredContentSizeCategory.rawValue
    print("window width \(w) pt, text size \(size)")
    for name in ["geo", "fit"] {
        QuickActionsLab.model.which = name
        await wait(0.8)
        print("   " + arrangement(name == "geo" ? "GeometryReader (section 6)" : "ViewThatFits (section 19)"))
    }
}
@MainActor func identity() async {
    await wait(1.5)
    for name in ["AnyLayout", "if/else"] {
        IdentityLab.model.mode = name
        await wait(0.8)
        for _ in 0..<3 { if let b = elements().last(where: { ($0.accessibilityLabel ?? "").hasPrefix("Count:") }) { _ = b.accessibilityActivate(); await wait(0.3) } }
        let before = labels().first { $0.hasPrefix("Count:") } ?? "?"
        await press("Switch Layout", quiet: true)
        await wait(0.5)
        let after = labels().first { $0.hasPrefix("Count:") } ?? "?"
        print("\(name): \(before) → after Switch Layout: \(after)")
    }
}

// MARK: - Labs

struct ProposalLog: Layout {   // authored: a pass-through layout that reports the negotiation
    let name: String
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let size = subviews[0].sizeThatFits(proposal)
        print("\(name): proposed \(fmt(proposal.width))×\(fmt(proposal.height)) → chose \(fmt(size.width))×\(fmt(size.height))")
        return size
    }
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        print("\(name): placed in \(fmt(bounds.width))×\(fmt(bounds.height))")
        subviews[0].place(at: bounds.origin, proposal: proposal)
    }
    private func fmt(_ v: CGFloat?) -> String {
        guard let v else { return "nil" }
        return v.isFinite ? "\(Int(v))" : "∞"
    }
}
struct ProposalLab: View {
    var body: some View {
        VStack(spacing: 24) {
            ProposalLog(name: "Text(\"NPay\")") { Text("NPay") }
            ProposalLog(name: "Text(\"NPay\").frame(maxWidth: .infinity)") { Text("NPay").frame(maxWidth: .infinity) }
            ProposalLog(name: "Color.blue") { Color.blue }
        }
        .frame(width: 320, height: 300)
    }
}

struct OrderLab: View {   // section 3, examples A and B
    var body: some View {
        VStack(spacing: 40) {
            Text("NPay")
                .background(.blue)
                .frame(width: 200, height: 80)
                .border(.red)

            Text("NPay")
                .frame(width: 200, height: 80)
                .background(.blue)
                .border(.red)
        }
    }
}

// Section 4, verbatim
struct GeometryExperiment: View {
    var body: some View {
        GeometryReader { geometry in
            VStack {
                Text("Width: \(geometry.size.width)")
                Text("Height: \(geometry.size.height)")
            }
        }
    }
}

struct GeoScrollLab: View {   // section 16
    var body: some View {
        ScrollView {
            GeometryReader { geometry in
                Text("Width: \(geometry.size.width)")
                    .onAppear { print("in ScrollView, no height: \(Int(geometry.size.width))×\(Int(geometry.size.height))") }
            }
            .border(.red)
            GeometryReader { geometry in
                Text("Width: \(geometry.size.width)")
                    .onAppear { print("in ScrollView, .frame(height: 100): \(Int(geometry.size.width))×\(Int(geometry.size.height))") }
            }
            .frame(height: 100)
            .border(.red)
        }
    }
}

// Section 6, renamed so it compiles next to the section 19 version
struct NPayQuickActionsGeo: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        GeometryReader { geometry in
            let isCompact = geometry.size.width < 350

            Group {
                if isCompact {
                    VStack(spacing: 12) {
                        actions
                    }
                } else {
                    HStack(spacing: 12) {
                        actions
                    }
                }
            }
        }
        .frame(height: 180)
    }

    @ViewBuilder
    private var actions: some View {
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

@MainActor @Observable final class QAModel { var which = "fit" }
struct QuickActionsLab: View {
    static let model = QAModel()
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(QuickActionsLab.model.which == "geo" ? "GeometryReader (section 6)" : "ViewThatFits (section 19)")
                .font(.headline)
            if QuickActionsLab.model.which == "geo" {
                NPayQuickActionsGeo(onSend: {}, onRequest: {}, onHistory: {})
                    .border(.red)
            } else {
                NPayQuickActions(onSend: {}, onRequest: {}, onHistory: {})
                    .border(.red)
            }
            Spacer()
        }
        .padding()
    }
}

// Section 18, verbatim
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        Button("Count: \(count)") {
            count += 1
        }
    }
}

struct LayoutIdentityExperiment: View {
    @State private var vertical = false

    var body: some View {
        let layout = vertical
            ? AnyLayout(VStackLayout())
            : AnyLayout(HStackLayout())

        VStack(spacing: 20) {
            layout {
                CounterView()
            }

            Button("Switch Layout") {
                vertical.toggle()
            }
        }
    }
}

struct BranchIdentityExperiment: View {   // section 9's conditional branches
    @State private var vertical = false

    var body: some View {
        VStack(spacing: 20) {
            if vertical {
                VStack {
                    CounterView()
                }
            } else {
                HStack {
                    CounterView()
                }
            }

            Button("Switch Layout") {
                vertical.toggle()
            }
        }
    }
}

@MainActor @Observable final class IDModel { var mode = "AnyLayout" }
struct IdentityLab: View {
    static let model = IDModel()
    var body: some View {
        if IdentityLab.model.mode == "AnyLayout" { LayoutIdentityExperiment() } else { BranchIdentityExperiment() }
    }
}

// Section 8, verbatim
struct AdaptiveActions: View {
    let compact: Bool

    var body: some View {
        let layout = compact
            ? AnyLayout(VStackLayout(spacing: 12))
            : AnyLayout(HStackLayout(spacing: 12))

        layout {
            Text("Send")
            Text("Request")
            Text("History")
        }
    }
}

struct SafeAreaLab: View {   // section 10
    var body: some View {
        HStack(spacing: 0) {
            ZStack {
                Color.blue.opacity(0.3)
                Text("default").font(.headline)
            }
            ZStack {
                Color.blue.opacity(0.3)
                    .ignoresSafeArea()
                Text(".ignoresSafeArea()").font(.headline)
            }
        }
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



// ===================== Complete code through Lesson 3.8 =====================

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

    var paymentDraft = PaymentDraft()

    func clearPaymentDraft() {
        paymentDraft = PaymentDraft()
    }

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

            Text("NPay Demo Account")
                .font(.caption)
        }
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(24)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(cornerRadius: NPayTheme.Radius.card)
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

// Models/PaymentDraft.swift (Lesson 3.5: the editable input)

struct PaymentDraft {
    var recipient: String = ""
    var amountText: String = ""
}

// Models/PaymentReview.swift (Lesson 3.4's review snapshot, renamed: both lessons call it PaymentDraft)

struct PaymentReview: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}

// Screens/PaymentsScreen.swift (the draft now lives in NPayStore; the screen edits it through @Bindable)

struct PaymentsScreen: View {
    @Bindable var store: NPayStore
    let router: NPayRouter

    @State private var review: PaymentReview?
    @State private var pendingSuccessID: UUID?
    @State private var paymentFailed = false
    @State private var showFailure = false
    @State private var confirmDiscard = false

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    private var parsedAmount: Int? {
        Money.parsePaise(store.paymentDraft.amountText)
    }

    private var isValid: Bool {
        let trimmed = store.paymentDraft.recipient.trimmingCharacters(
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
                    text: $store.paymentDraft.recipient
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
                    text: $store.paymentDraft.amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )

                if !store.paymentDraft.amountText.isEmpty && !isValid {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                NPayButton("Review Payment", symbol: "doc.text.magnifyingglass") {
                    guard let amountPaise = parsedAmount else {
                        return
                    }

                    focusedField = nil
                    // An immutable snapshot of what the user is reviewing
                    review = PaymentReview(
                        recipient: store.paymentDraft.recipient,
                        amountPaise: amountPaise
                    )
                }
                .disabled(!isValid)

                Button("Discard Draft", role: .destructive) {
                    confirmDiscard = true
                }
                .disabled(store.paymentDraft.recipient.isEmpty && store.paymentDraft.amountText.isEmpty)
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
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    router.showPaymentSuccess(id)
                } else if paymentFailed {
                    paymentFailed = false
                    showFailure = true
                }
            }
        ) { review in

            PaymentReviewSheet(review: review) {
                // The store validates again against the current balance
                if let id = store.recordDemoPayment(
                    recipient: review.recipient,
                    amountPaise: review.amountPaise
                ) {
                    store.clearPaymentDraft()   // recorded: the draft is done
                    pendingSuccessID = id
                } else {
                    paymentFailed = true
                }
                self.review = nil
            }
        }
        .alert("Payment not recorded", isPresented: $showFailure) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("The amount is no longer within your available balance.")
        }
        .alert("Discard payment draft?", isPresented: $confirmDiscard) {
            Button("Discard", role: .destructive) {
                store.clearPaymentDraft()
            }

            Button("Cancel", role: .cancel) {}
        }
        // Diagnostic (Section 18): watch the shared draft change
        .onChange(of: store.paymentDraft.recipient) { oldValue, newValue in
            print("Draft changed:")
            print("Old:", oldValue)
            print("New:", newValue)
        }
    }
}

// Screens/PaymentReviewSheet.swift (shows the snapshot, not the live draft)

struct PaymentReviewSheet: View {
    let review: PaymentReview
    let onConfirm: () -> Void

    @State private var isProcessing = false

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: review.recipient
            )

            LabeledContent(
                "Amount",
                value: Money.display(review.amountPaise)
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
