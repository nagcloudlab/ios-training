import SwiftUI
import UIKit

// Lesson 3.4 evidence app. The text's sheet, full-screen cover, alert and confirmation-dialog examples, and the complete
// code through 3.4 (assembled from the text's Sections 10-18 onto the 3.3 code; see "Deck changes") run below.
// PaymentsLab hosts the real PaymentsScreen with a store and router the driver can read; NaiveLab and UnguardedLab are
// the text's simpler versions (Section 12's same-update dismissal; a Confirm button without the isProcessing guard).
// Driver details as in 3.3 (accessibility activation, tabs selected as a tap does). Sheets are dismissed the way a
// swipe ends: the presented controller is dismissed; alert and dialog buttons run their action handler.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("sheetexp") { SheetExperiment().task { await sheetexp() } }
            else if args.contains("s_sheetexp") { SheetExperiment().task { await wait(1.5); await press("Review Payment") } }
            else if args.contains("s_cover") { CoverLab().task { await wait(1.5); await press("Start Full Screen Flow") } }
            else if args.contains("alert") { AlertLab().task { await alertRun() } }
            else if args.contains("s_alert") { AlertLab().task { await wait(1.5); await press("Delete Draft") } }
            else if args.contains("dialog") { DialogLab().task { await dialogRun() } }
            else if args.contains("s_dialog") { DialogLab().task { await wait(1.5); await press("Payment Options") } }
            else if args.contains("localstate") { LocalStateLab().task { await localState() } }
            else if args.contains("timeline") { PaymentsLab().task { await timeline() } }
            else if args.contains("naive") { NaiveLab().task { await naive() } }
            else if args.contains("revalidate") { PaymentsLab().task { await revalidate() } }
            else if args.contains("s_failure") { PaymentsLab().task { await revalidate(quiet: true) } }
            else if args.contains("doubleguard") { PaymentsLab().task { await doubleTap(guarded: true) } }
            else if args.contains("doubleraw") { UnguardedLab().task { await doubleTap(guarded: false) } }
            else if args.contains("verify") { NPayRootView().task { await verify() } }
            // screenshots of the unchanged NPayRootView
            else if args.contains("s_typed") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill() } }
            else if args.contains("s_review") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment") } }
            else if args.contains("s_edit") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment"); await press("Edit Details") } }
            else if args.contains("s_success") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment"); await press("Confirm Demo Payment") } }
            else if args.contains("s_home") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment"); await press("Confirm Demo Payment"); await wait(1); await press("Back to Dashboard") } }
            else if args.contains("s_history") { NPayRootView().task { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment"); await press("Confirm Demo Payment"); await wait(1); await press("Back to Dashboard"); await selectTab("History") } }
            else { NPayRootView() }
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
    let keep = ["₹", "Sent to", "Recorded", "Recipient", "Amount", "Review", "Count", "Details", "Coffee"]
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

// The store and router of PaymentsLab, readable by the driver
@MainActor var labStore: NPayStore?
@MainActor var labRouter: NPayRouter?

// MARK: - Runs

@MainActor func sheetexp() async {
    await wait(1.5)
    await press("Review Payment")
    print("sheet presented: \(presented() != nil); windows: \(allWindows().count)")
    await dismissSheet()
    print("sheet presented: \(presented() != nil)")
}
@MainActor func alertRun() async {
    await wait(1.5)
    await press("Delete Draft")
    print("presented: \(String(describing: Swift.type(of: presented() ?? UIViewController())))")
    await alertButton("Delete")
}
@MainActor func dialogRun() async {
    await wait(1.5)
    await press("Payment Options")
    if let a = presented() as? UIAlertController { print("actions: \(a.actions.map { $0.title ?? "" })") }
    await alertButton("Save Draft")
}
@MainActor func localState() async {
    await wait(1.5)
    await press("Present Review Sheet")
    await press("Show Details")
    visible("presented, after Show Details")
    await press("Close")
    await press("Present Review Sheet")
    visible("presented again")
}
@MainActor func timelineFrom(_ start: Date, until: Double = 1.6) async {
    var last = ""
    while Date.now.timeIntervalSince(start) < until {
        let state = "sheet \(presented() != nil ? "shown" : "gone"), paymentsPath \(labRouter?.paymentsPath.count ?? -1), transactions \(labStore?.transactions.count ?? -1)"
        if state != last { print(String(format: "  t=%4.0f ms  ", Date.now.timeIntervalSince(start) * 1000) + state); last = state }
        try? await Task.sleep(for: .milliseconds(10))
    }
}
@MainActor func timeline() async {
    await wait(1.5)
    await fill()
    await press("Review Payment")
    await press("Edit Details")
    print("after Edit Details: \(fields())")
    await press("Review Payment")
    let start = Date.now
    print("[activate \"Confirm Demo Payment\"]")
    _ = element("Confirm Demo Payment")?.accessibilityActivate()
    await timelineFrom(start)
    visible("end")
}
@MainActor func naive() async {
    await wait(1.5)
    await press("Review Payment")
    let start = Date.now
    print("[activate \"Confirm Demo Payment\"]")
    _ = element("Confirm Demo Payment")?.accessibilityActivate()
    await timelineFrom(start)
    visible("end")
}
@MainActor func revalidate(quiet: Bool = false) async {
    await wait(1.5)
    await fill()
    await press("Review Payment", quiet: quiet)
    labStore?.balancePaise = 100_000   // the balance changes while the review is open (₹1,000)
    if !quiet { print("balance changed to \(Money.display(labStore?.balancePaise ?? 0)) while the review is open") }
    await press("Confirm Demo Payment", quiet: quiet)
    await wait(1)
    if !quiet {
        print("transactions: \(labStore?.transactions.count ?? -1), paymentsPath: \(labRouter?.paymentsPath.count ?? -1)")
        if let a = presented() as? UIAlertController { print("alert: \(a.title ?? "") / \(a.message ?? "")") }
    }
}
@MainActor func doubleTap(guarded: Bool) async {
    await wait(1.5)
    if guarded { await fill() }
    await press("Review Payment")
    let before = labStore?.transactions.count ?? -1
    let confirm = element("Confirm Demo Payment")
    print("[activate \"Confirm Demo Payment\" twice, back to back]")
    _ = confirm?.accessibilityActivate()
    _ = confirm?.accessibilityActivate()
    await wait(1.5)
    let after = labStore?.transactions.count ?? -1
    print("\(guarded ? "with" : "without") isProcessing: transactions \(before) → \(after), balance \(Money.display(labStore?.balancePaise ?? 0))")
}
@MainActor func verify() async {
    await wait(1.5)
    await selectTab("Payments")
    await fill()
    print("1. typed: \(fields())")
    await press("Review Payment")
    visible("2. sheet")
    await dismissSheet()
    print("3. after swipe down: \(fields())")
    await press("Review Payment")
    await press("Confirm Demo Payment")
    await wait(1)
    visible("4-5. after Confirm")
    await press("Back to Dashboard")
    visible("6. Home")
    await selectTab("History")
    visible("7. History")
    await selectTab("Payments")
    for s in ["0", "12.345", "30000"] {
        await setAmount(s)
        print("8. amount \"\(s)\": Review Payment \(enabled("Review Payment"))")
    }
}

// MARK: - Experiments

struct SheetExperiment: View {   // Section 2
    @State private var showSheet = false

    var body: some View {
        Button("Review Payment") {
            showSheet = true
        }
        .sheet(isPresented: $showSheet) {
            Text("Payment Review")
                .font(.title)
                .presentationDetents([.medium, .large])
        }
        .onChange(of: showSheet) { _, new in print("showSheet:", new) }
    }
}

struct CoverLab: View {   // Section 7
    @State private var showFullScreen = false

    var body: some View {
        Button("Start Full Screen Flow") { showFullScreen = true }
            .fullScreenCover(isPresented: $showFullScreen) {
                Text("Full Screen Payment Flow")
            }
    }
}

struct AlertLab: View {   // Section 8
    @State private var showAlert = false

    var body: some View {
        Button("Delete Draft") {
            showAlert = true
        }
        .alert("Delete payment draft?", isPresented: $showAlert) {
            Button("Delete", role: .destructive) {
                print("Draft deleted")
            }

            Button("Cancel", role: .cancel) {}
        } message: {
            Text("This action cannot be undone.")
        }
    }
}

struct DialogLab: View {   // Section 9
    @State private var showOptions = false

    var body: some View {
        Button("Payment Options") {
            showOptions = true
        }
        .confirmationDialog(
            "Choose an action",
            isPresented: $showOptions
        ) {
            Button("Save Draft") {
                print("Draft saved")
            }

            Button("Discard", role: .destructive) {
                print("Draft discarded")
            }
        }
    }
}

struct LocalStateLab: View {   // Section 17: sheet-local @State
    @State private var showReview = false

    var body: some View {
        Button("Present Review Sheet") { showReview = true }
            .sheet(isPresented: $showReview) { LocalStateSheet() }
    }
}
struct LocalStateSheet: View {
    @State private var showDetails = false
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 20) {
            Text(showDetails ? "Details expanded" : "Details collapsed")
            Button("Show Details") { showDetails = true }
            Button("Close") { dismiss() }
        }
        .presentationDetents([.medium])
    }
}

struct PaymentsLab: View {   // the real PaymentsScreen, with a store and router the driver can read
    @State private var store = NPayStore()
    @State private var router = NPayRouter()

    var body: some View {
        @Bindable var router = router
        NavigationStack(path: $router.paymentsPath) {
            PaymentsScreen(store: store, router: router)
                .navigationDestination(for: NPayRoute.self) { route in
                    if case .paymentSuccess(let id) = route {
                        PaymentSuccessScreen(transactionID: id, onDone: { router.returnHome() })
                    }
                }
        }
        .onAppear { labStore = store; labRouter = router }
    }
}

struct NaiveLab: View {   // Section 12: dismiss and navigate in the same update
    @State private var store = NPayStore()
    @State private var router = NPayRouter()
    @State private var reviewDraft: PaymentDraft?

    var body: some View {
        @Bindable var router = router
        NavigationStack(path: $router.paymentsPath) {
            Button("Review Payment") {
                reviewDraft = PaymentDraft(recipient: "ravi@npay", amountPaise: 150_050)
            }
            .navigationTitle("Payments")
            .navigationDestination(for: NPayRoute.self) { route in
                if case .paymentSuccess(let id) = route {
                    PaymentSuccessScreen(transactionID: id, onDone: { router.returnHome() })
                }
            }
            .sheet(item: $reviewDraft) { draft in
                PaymentReviewSheet(draft: draft) {
                    if let transactionID = store.recordDemoPayment(
                        recipient: draft.recipient,
                        amountPaise: draft.amountPaise
                    ) {
                        reviewDraft = nil
                        router.showPaymentSuccess(transactionID)
                    }
                }
            }
        }
        .onAppear { labStore = store; labRouter = router }
    }
}

struct UnguardedLab: View {   // Section 16: a Confirm button without the isProcessing guard
    @State private var store = NPayStore()
    @State private var reviewDraft: PaymentDraft?

    var body: some View {
        Button("Review Payment") {
            reviewDraft = PaymentDraft(recipient: "ravi@npay", amountPaise: 150_050)
        }
        .sheet(item: $reviewDraft) { draft in
            VStack(spacing: 24) {
                Text("Review Payment")
                Button("Confirm Demo Payment") {
                    _ = store.recordDemoPayment(recipient: draft.recipient, amountPaise: draft.amountPaise)
                    reviewDraft = nil
                }
            }
        }
        .onAppear { labStore = store }
    }
}
// ===================== Complete code through Lesson 3.4 =====================

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

// Models/PaymentDraft.swift

struct PaymentDraft: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}

// Screens/PaymentsScreen.swift (3.3's form, now: validate → review sheet → confirm → success after dismissal)

struct PaymentsScreen: View {
    let store: NPayStore
    let router: NPayRouter

    @State private var recipient = ""
    @State private var amountText = ""

    @State private var reviewDraft: PaymentDraft?
    @State private var pendingSuccessID: UUID?
    @State private var paymentFailed = false
    @State private var showFailure = false

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

                Button("Review Payment") {
                    guard let amountPaise = parsedAmount else {
                        return
                    }

                    focusedField = nil
                    reviewDraft = PaymentDraft(
                        recipient: recipient,
                        amountPaise: amountPaise
                    )
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
        .sheet(
            item: $reviewDraft,
            onDismiss: {
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    recipient = ""
                    amountText = ""
                    router.showPaymentSuccess(id)
                } else if paymentFailed {
                    paymentFailed = false
                    showFailure = true
                }
            }
        ) { draft in

            PaymentReviewSheet(draft: draft) {
                // The store validates again: the balance may have changed while the review was open
                if let id = store.recordDemoPayment(
                    recipient: draft.recipient,
                    amountPaise: draft.amountPaise
                ) {
                    pendingSuccessID = id
                } else {
                    paymentFailed = true
                }
                reviewDraft = nil
            }
        }
        .alert("Payment not recorded", isPresented: $showFailure) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("The amount is no longer within your available balance.")
        }
    }
}

// Screens/PaymentReviewSheet.swift

struct PaymentReviewSheet: View {
    let draft: PaymentDraft
    let onConfirm: () -> Void

    @State private var isProcessing = false

    @Environment(\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: draft.recipient
            )

            LabeledContent(
                "Amount",
                value: Money.display(draft.amountPaise)
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
