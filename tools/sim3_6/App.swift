import SwiftUI
import UIKit

// Lesson 3.6 evidence app. The text's AnimationExperiment, PaymentSuccessScreen (Sections 11 + 22) and AnimatedNumber
// run as written; the complete code integrates the animated balance card and success screen into the 3.5 app (authored:
// the text names this as its next checkpoint). Two kinds of evidence: (1) frames captured by the app itself during an
// animation (UIView.drawHierarchy, afterScreenUpdates: false), labelled with their measured time; (2) the values SwiftUI
// passes to an Animatable modifier on each frame, printed with their time. Driver as in 3.5.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("circle") { AnimationExperiment().task { await circleFilm() } }
            else if args.contains("curves") { CurveLab().task { await curves() } }
            else if args.contains("interrupt") { CurveLab().task { await interrupt() } }
            else if args.contains("number") { NumberLab().task { await numberRun() } }
            else if args.contains("success") { SuccessLab(animated: true).task { await successFilm("success") } }
            else if args.contains("noanim") { SuccessLab(animated: false).task { await successFilm("noanim") } }
            else if args.contains("reduced") { SuccessLab(animated: true).task { await successFilm("reduced") } }
            else if args.contains("lab") { AnimationLab().task { await labFilm() } }
            else if args.contains("ids") { IdentityRowsLab().task { await ids() } }
            else if args.contains("s_home") { NPayRootView() }
            else { NPayRootView() }
        }
    }
}

// MARK: - Frame capture and sampling

@MainActor var t0 = Date.now
@MainActor func ms() -> Int { Int(Date.now.timeIntervalSince(t0) * 1000) }
@MainActor func capture(_ name: String, y: CGFloat, height: CGFloat) -> Int {
    guard let w = allWindows().first else { return -1 }
    let t = ms()
    let full = UIGraphicsImageRenderer(bounds: w.bounds).image { _ in _ = w.drawHierarchy(in: w.bounds, afterScreenUpdates: false) }
    let s = full.scale
    if let cg = full.cgImage?.cropping(to: CGRect(x: 0, y: y * s, width: w.bounds.width * s, height: height * s)) {
        try? UIImage(cgImage: cg).pngData()?.write(to: FileManager.default.temporaryDirectory.appendingPathComponent(name + ".png"))
    }
    return t
}
@MainActor func film(_ prefix: String, frames: Int, every: Int, y: CGFloat, height: CGFloat) async {
    var times: [String] = []
    for i in 0..<frames {
        times.append("\(capture("\(prefix)\(i)", y: y, height: height))")
        try? await Task.sleep(for: .milliseconds(every))
    }
    print("\(prefix) frames at ms: " + times.joined(separator: ", "))
}
@MainActor final class Sampler {
    static let shared = Sampler()
    var on = false
    var samples: [(Int, Double)] = []
    func record(_ v: Double) { if on { samples.append((ms(), v)) } }
    func start() { samples = []; t0 = .now; on = true }
    func stop() -> [(Int, Double)] { on = false; return samples }
}
struct SampledDiameter: ViewModifier, Animatable {   // a frame modifier that reports each interpolated value
    var diameter: Double
    nonisolated var animatableData: Double {
        get { diameter }
        set { diameter = newValue }
    }
    func body(content: Content) -> some View {
        let _ = Sampler.shared.record(diameter)
        content.frame(width: diameter, height: diameter)
    }
}
@MainActor func report(_ name: String, _ s: [(Int, Double)]) {
    let pick = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 600, 800].map { target in
        s.min(by: { abs($0.0 - target) < abs($1.0 - target) }).map { "\($0.0)ms \(String(format: "%.1f", $0.1))" } ?? "-"
    }
    let peak = s.map(\.1).max() ?? 0
    let last = s.last.map { "\($0.0)ms \(String(format: "%.1f", $0.1))" } ?? "-"
    print("\(name): \(s.count) values; peak \(String(format: "%.1f", peak)); last \(last)")
    print("   " + pick.joined(separator: " | "))
}

// MARK: - Runs

@MainActor func circleFilm() async {
    await wait(1.5)
    t0 = .now
    _ = element("Toggle Size")?.accessibilityActivate()
    await film("circle", frames: 7, every: 60, y: 300, height: 260)
}
@MainActor func curves() async {
    await wait(1.5)
    let lab = CurveLab.model
    for (name, anim) in [("linear(0.5)", Animation.linear(duration: 0.5)), ("easeInOut(0.5)", .easeInOut(duration: 0.5)),
                         ("spring(response 0.45, damping 0.7)", .spring(response: 0.45, dampingFraction: 0.7))] {
        lab.expanded = false
        await wait(0.8)
        lab.stateChanges = 0
        Sampler.shared.start()
        withAnimation(anim) { lab.expanded = true }
        await wait(1.3)
        report(name, Sampler.shared.stop())
        print("   state changes during the animation: \(lab.stateChanges)")
    }
}
@MainActor func interrupt() async {
    await wait(1.5)
    let lab = CurveLab.model
    Sampler.shared.start()
    withAnimation(.linear(duration: 1.0)) { lab.expanded = true }
    await wait(0.4)
    let at = ms()
    withAnimation(.linear(duration: 1.0)) { lab.expanded = false }
    await wait(1.4)
    let s = Sampler.shared.stop()
    print("retarget at \(at)ms")
    let around = s.filter { $0.0 > at - 70 && $0.0 < at + 110 }.map { "\($0.0)ms \(String(format: "%.1f", $0.1))" }
    print("   around it: " + around.joined(separator: " | "))
    print("   peak \(String(format: "%.1f", s.map(\.1).max() ?? 0)); last \(s.last.map { "\($0.0)ms \(String(format: "%.1f", $0.1))" } ?? "-")")
}
@MainActor func numberRun() async {
    await wait(1.5)
    Sampler.shared.start()
    NumberLab.model.balancePaise = 2_350_000
    await wait(0.9)
    let s = Sampler.shared.stop()
    let vals = stride(from: 0, to: s.count, by: max(1, s.count / 8)).map { "\(s[$0].0)ms \(String(format: "%.0f", s[$0].1))" }
    print("AnimatedNumber body: \(s.count) values; " + vals.joined(separator: " | ") + "; last \(String(format: "%.0f", s.last?.1 ?? 0))")
}
@MainActor func successFilm(_ prefix: String) async {
    await wait(1.0)
    print("accessibilityReduceMotion: \(UIAccessibility.isReduceMotionEnabled)")
    t0 = .now
    SuccessLab.model.shown = true
    await film(prefix, frames: 7, every: 50, y: 200, height: 380)
}
@MainActor func labFilm() async {
    await wait(1.5)
    t0 = .now
    _ = element("Simulate ₹1,500 payment")?.accessibilityActivate()
    await film("lab", frames: 7, every: 40, y: 110, height: 420)
}
@MainActor func ids() async {
    await wait(1.5)
    print("-- Refresh, same IDs"); await press("Refresh (same IDs)", quiet: true)
    print("-- Refresh, new IDs"); await press("Refresh (new IDs)", quiet: true)
    print("-- done")
}

// MARK: - Experiments

struct AnimationExperiment: View {   // Section 3, verbatim
    @State private var expanded = false

    var body: some View {
        VStack(spacing: 30) {
            Circle()
                .fill(.blue)
                .frame(
                    width: expanded ? 180 : 80,
                    height: expanded ? 180 : 80
                )

            Button("Toggle Size") {
                withAnimation(.easeInOut(duration: 0.5)) {
                    expanded.toggle()
                }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

@MainActor @Observable final class CurveModel {
    var expanded = false { didSet { stateChanges += 1 } }
    var stateChanges = 0
}
struct CurveLab: View {   // Sections 5, 16, 17, 20: the same circle, its diameter sampled every frame
    static let model = CurveModel()
    var body: some View {
        Circle()
            .fill(.blue)
            .modifier(SampledDiameter(diameter: CurveLab.model.expanded ? 180 : 80))
    }
}

// Section 18, verbatim except nonisolated on animatableData (needed in Swift 6 mode without default MainActor isolation)
struct AnimatedNumber: AnimatableModifier {
    var value: Double

    nonisolated var animatableData: Double {
        get { value }
        set { value = newValue }
    }

    func body(content: Content) -> some View {
        Text(
            value,
            format: .number.precision(.fractionLength(0))
        )
        .font(.largeTitle.bold())
    }
}
struct TracedAnimatedNumber: AnimatableModifier {   // AnimatedNumber plus one line that reports each value
    var value: Double

    nonisolated var animatableData: Double {
        get { value }
        set { value = newValue }
    }

    func body(content: Content) -> some View {
        let _ = Sampler.shared.record(value)
        Text(
            value,
            format: .number.precision(.fractionLength(0))
        )
        .font(.largeTitle.bold())
    }
}
@MainActor @Observable final class NumberModel { var balancePaise = 2_500_000 }
struct NumberLab: View {
    static let model = NumberModel()
    var body: some View {
        Text("")
            .modifier(
                TracedAnimatedNumber(value: Double(NumberLab.model.balancePaise) / 100)
            )
            .animation(
                .easeInOut(duration: 0.5),
                value: NumberLab.model.balancePaise
            )
    }
}

@MainActor @Observable final class SuccessModel { var shown = false }
struct SuccessLab: View {   // the text's success screen, shown on demand; animated: false drops withAnimation
    static let model = SuccessModel()
    let animated: Bool
    var body: some View {
        NavigationStack {
            if SuccessLab.model.shown {
                if animated {
                    PaymentSuccessScreen(transactionID: UUID(uuidString: "6F1C2A9E-3B7D-4E21-9C55-0A8B7F3D2E10")!, onDone: {})
                } else {
                    UnanimatedSuccess()
                }
            } else {
                Color.clear
            }
        }
    }
}
struct UnanimatedSuccess: View {   // Experiment: remove withAnimation
    @State private var showContent = false
    var body: some View {
        VStack(spacing: 24) {
            if showContent {
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 80))
                    .foregroundStyle(.green)
                    .transition(.scale.combined(with: .opacity))
            }
            Text("Payment Recorded")
                .font(.title.bold())
        }
        .onAppear { showContent = true }
    }
}

@MainActor @Observable final class LabStore {   // Section 1's demo, built natively
    var balancePaise = 2_500_000
    var transactions: [Transaction] = [
        Transaction(id: UUID(), title: "Coffee Shop", amountPaise: -25_000, date: .now),
        Transaction(id: UUID(), title: "Electricity Bill", amountPaise: -120_000, date: .now)
    ]
}
struct AnimationLab: View {
    @State private var store = LabStore()
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            BalanceCard(balancePaise: store.balancePaise)
            Button("Simulate ₹1,500 payment") {
                withAnimation(.easeInOut(duration: 0.3)) {
                    store.balancePaise -= 150_000
                    store.transactions.insert(
                        Transaction(id: UUID(), title: "Demo Payment", amountPaise: -150_000, date: .now),
                        at: 0)
                }
            }
            .buttonStyle(.borderedProminent)
            Text("Recent Transactions").font(.headline)
            VStack(spacing: 0) {
                ForEach(store.transactions) { transaction in
                    TransactionRow(transaction: transaction)
                        .transition(.move(edge: .top).combined(with: .opacity))
                }
            }
            Spacer()
        }
        .padding()
    }
}

struct IdentityRowsLab: View {   // Section 19: refresh with stable IDs vs regenerated IDs
    @State private var transactions: [Transaction] = [
        Transaction(id: UUID(), title: "Coffee Shop", amountPaise: -25_000, date: .now),
        Transaction(id: UUID(), title: "Electricity Bill", amountPaise: -120_000, date: .now),
        Transaction(id: UUID(), title: "Salary Credit", amountPaise: 4_500_000, date: .now)
    ]
    var body: some View {
        VStack(spacing: 12) {
            ForEach(transactions) { transaction in
                TransactionRow(transaction: transaction)
                    .onAppear { print("   row appeared: \(transaction.title)") }
                    .onDisappear { print("   row removed: \(transaction.title)") }
            }
            Button("Refresh (same IDs)") {
                withAnimation { transactions = transactions.map { $0 } }
            }
            Button("Refresh (new IDs)") {
                withAnimation {
                    transactions = transactions.map {
                        Transaction(id: UUID(), title: $0.title, amountPaise: $0.amountPaise, date: $0.date)
                    }
                }
            }
        }
        .padding()
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


// ===================== Complete code through Lesson 3.6 =====================

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

                Button("Review Payment") {
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
                .buttonStyle(.borderedProminent)
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

            Button("Confirm Demo Payment") {
                guard !isProcessing else {
                    return
                }

                isProcessing = true
                onConfirm()
            }
            .buttonStyle(.borderedProminent)
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

            Button("Back to Dashboard") {
                onDone()
            }
            .buttonStyle(.borderedProminent)
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
