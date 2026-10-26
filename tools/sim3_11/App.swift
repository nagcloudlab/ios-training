import SwiftUI
import UIKit
import QuartzCore

// Lesson 3.11 evidence app. The text's HistoryPerformanceLab, PerformanceRow, makeDemoTransactions and the filtering
// code run as written; counting copies report how many rows SwiftUI builds, how often body-level sorts and filters run,
// and how many display frames arrive while the main actor is busy. Memory is the process's phys_footprint (task_info).
// All numbers come from the iPhone 17 simulator on a Mac: indicative, not device benchmarks. The complete code adds
// search to History (authored integration).
@main
struct LabApp: App {
    init() { setvbuf(stdout, nil, _IONBF, 0) }

    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("perf_eager") { NavigationStack { CountedPerformanceLab(selected: .eager) }.task { await perf("VStack") } }
            else if args.contains("perf_lazy") { NavigationStack { CountedPerformanceLab(selected: .lazy) }.task { await perf("LazyVStack") } }
            else if args.contains("perf_list") { NavigationStack { CountedPerformanceLab(selected: .list) }.task { await perf("List") } }
            else if args.contains("s_perf") { NavigationStack { HistoryPerformanceLab() } }
            else if args.contains("obs") { ObservationLab().task { await obs() } }
            else if args.contains("ids") { IdentityLab().task { await ids() } }
            else if args.contains("search") { SearchLab().task { await search() } }
            else if args.contains("block_big") { BlockLab().task { BlockLab.count = 500_000; await block() } }
            else if args.contains("block") { BlockLab().task { await block() } }
            else if args.contains("s_history") { NPayRootView().task { await wait(1.5); await selectTab("History"); await searchType("Coffee") } }
            else { NPayRootView() }
        }
    }
}

// MARK: - Measurement helpers

nonisolated(unsafe) var rowsBuilt = 0
nonisolated(unsafe) var sortsRun = 0
nonisolated(unsafe) var filtersRun = 0
nonisolated(unsafe) var appears = 0
nonisolated(unsafe) var tapped = 0
func footprintMB() -> Double {
    var info = task_vm_info_data_t()
    var count = mach_msg_type_number_t(MemoryLayout<task_vm_info_data_t>.size / MemoryLayout<natural_t>.size)
    let kr = withUnsafeMutablePointer(to: &info) {
        $0.withMemoryRebound(to: integer_t.self, capacity: Int(count)) { task_info(mach_task_self_, task_flavor_t(TASK_VM_INFO), $0, &count) }
    }
    return kr == KERN_SUCCESS ? Double(info.phys_footprint) / 1_048_576 : -1
}
@MainActor func scrollToEnd() async {
    func scrollViews(_ v: UIView) -> [UIScrollView] { ((v as? UIScrollView).map { [$0] } ?? []) + v.subviews.flatMap(scrollViews) }
    guard let sv = allWindows().flatMap({ scrollViews($0) }).max(by: { $0.contentSize.height < $1.contentSize.height }) else { return }
    for _ in 0..<3 {   // lazy content grows as it is revealed; jump to the end a few times
        sv.setContentOffset(CGPoint(x: 0, y: max(0, sv.contentSize.height - sv.bounds.height)), animated: false)
        try? await Task.sleep(for: .milliseconds(600))
    }
}
@MainActor func searchType(_ text: String) async {
    func fields(_ v: UIView) -> [UISearchTextField] { ((v as? UISearchTextField).map { [$0] } ?? []) + v.subviews.flatMap(fields) }
    guard let f = allWindows().flatMap({ fields($0) }).first else { print("no search field"); return }
    _ = f.becomeFirstResponder()
    try? await Task.sleep(for: .milliseconds(600))
    for ch in text {
        f.insertText(String(ch))
        try? await Task.sleep(for: .milliseconds(400))
    }
}

// MARK: - Runs

@MainActor func perf(_ name: String) async {
    await wait(2)
    print("\(name): \(rowsBuilt) rows built on open; footprint \(String(format: "%.0f", footprintMB())) MB")
    await scrollToEnd()
    print("\(name): \(rowsBuilt) rows built after scrolling to the end; footprint \(String(format: "%.0f", footprintMB())) MB")
}
@MainActor func ids() async {
    await wait(3)
    for mode in ["stable", "computed"] {
        IdentityLab.model.mode = mode
        await wait(1)
        await press("Refresh", quiet: true)   // settle after the switch
        await wait(1)
        rowsBuilt = 0; appears = 0; tapped = 0
        await press("Refresh", quiet: true)
        await wait(1)
        print("\(mode) id: after one unrelated parent change: \(appears) rows appeared again, \(rowsBuilt) row bodies")
    }
}
@MainActor func search() async {
    await wait(2)
    sortsRun = 0; filtersRun = 0
    print("before typing: sorts \(sortsRun), filters \(filtersRun)")
    await searchType("4999")
    await wait(1)
    print("after typing 4 characters: sorts of 50,000 \(sortsRun), filters of 50,000 \(filtersRun)")
    print("results shown: " + labels().filter { $0.hasPrefix("Demo Transaction") }.prefix(3).joined(separator: ", "))
}
@MainActor func block() async {
    await wait(1.5)
    let before = footprintMB()
    BlockLab.frames = 0
    let link = FrameCounter()
    try? await Task.sleep(for: .milliseconds(500))
    let idle = BlockLab.frames
    print("display frames in 0.5 s while idle: \(idle)")
    link.maxGap = 0
    _ = element("Load Transactions")?.accessibilityActivate()   // runs makeDemoTransactions(count: 50_000) on the main actor
    try? await Task.sleep(for: .milliseconds(1500))
    link.stop()
    print(String(format: "Load Transactions (%d records): action ran %.2f s on the main thread; display frames delivered during it: %d", BlockLab.count, BlockLab.busy, BlockLab.framesDuring))
    print(String(format: "longest gap between display frames: %.2f s (normal gap %.3f s)", link.maxGap, 1.0 / 60))
    print(String(format: "footprint %.0f MB before, %.0f MB after %d records", before, footprintMB(), BlockLab.count))
}
@MainActor final class FrameCounter: NSObject {
    private var link: CADisplayLink?
    override init() {
        super.init()
        link = CADisplayLink(target: self, selector: #selector(tick))
        link?.add(to: .main, forMode: .common)
    }
    var last = 0.0, maxGap = 0.0
    @objc func tick() {
        BlockLab.frames += 1
        let now = CACurrentMediaTime()
        if last > 0 { maxGap = max(maxGap, now - last) }
        last = now
    }
    func stop() { link?.invalidate() }
}

// MARK: - Labs

// Section 9: one @Observable store, one view reading the balance and one reading the transactions
@MainActor @Observable final class ObsStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []
}
nonisolated(unsafe) var balanceBodies = 0
nonisolated(unsafe) var historyBodies = 0
struct ObservationLab: View {
    static let store = ObsStore()
    var body: some View {
        VStack {
            ObsBalance(store: ObservationLab.store)
            ObsHistory(store: ObservationLab.store)
            DebugTransactionRow(title: "Coffee Shop")
        }
    }
}
struct ObsBalance: View {
    let store: ObsStore
    var body: some View {
        let _ = balanceBodies += 1
        Text("Balance \(store.balancePaise)")
    }
}
struct ObsHistory: View {
    let store: ObsStore
    var body: some View {
        let _ = historyBodies += 1
        Text("\(store.transactions.count) transactions")
    }
}
// Section 10, verbatim
struct DebugTransactionRow: View {
    let title: String

    var body: some View {
        let _ = Self._printChanges()

        return Text(title)
            .padding()
    }
}
@MainActor func obs() async {
    await wait(1.5)
    func step(_ what: String, _ change: () -> Void) async {
        balanceBodies = 0; historyBodies = 0
        change()
        await wait(0.8)
        print("\(what): BalanceView body \(balanceBodies), HistoryView body \(historyBodies)")
    }
    await step("append a transaction") { ObservationLab.store.transactions.append(makeDemoTransactions(count: 1)[0]) }
    await step("change the balance") { ObservationLab.store.balancePaise -= 25_000 }
    await step("set the balance to the same value") { ObservationLab.store.balancePaise = ObservationLab.store.balancePaise }
}

// Section 19, verbatim
struct HistoryPerformanceLab: View {

    enum Container: String, CaseIterable {
        case eager = "VStack"
        case lazy = "LazyVStack"
        case list = "List"
    }

    @State private var selected: Container = .list

    @State private var records: [Int] =
        Array(0..<10_000)

    var body: some View {
        VStack(spacing: 12) {

            Picker("Container", selection: $selected) {
                ForEach(Container.allCases, id: \.self) { option in
                    Text(option.rawValue)
                        .tag(option)
                }
            }
            .pickerStyle(.segmented)
            .padding(.horizontal)

            Group {
                switch selected {

                case .eager:
                    ScrollView {
                        VStack(spacing: 0) {
                            rows
                        }
                    }

                case .lazy:
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            rows
                        }
                    }

                case .list:
                    List(records, id: \.self) { id in
                        PerformanceRow(id: id)
                    }
                }
            }
        }
        .navigationTitle("Performance Lab")
    }

    @ViewBuilder
    private var rows: some View {
        ForEach(records, id: \.self) { id in
            PerformanceRow(id: id)
        }
    }
}

struct PerformanceRow: View {
    let id: Int

    var body: some View {
        HStack {
            Image(systemName: "creditcard")
                .foregroundStyle(.blue)

            Text("Transaction #\(id)")

            Spacer()

            Text("₹250")
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}

// The same lab with a row that counts its body evaluations, opened directly in one container
struct CountedPerformanceLab: View {
    let selected: HistoryPerformanceLab.Container
    @State private var records: [Int] = Array(0..<10_000)

    var body: some View {
        switch selected {
        case .eager:
            ScrollView { VStack(spacing: 0) { ForEach(records, id: \.self) { CountingRow(id: $0) } } }
        case .lazy:
            ScrollView { LazyVStack(spacing: 0) { ForEach(records, id: \.self) { CountingRow(id: $0) } } }
        case .list:
            List(records, id: \.self) { CountingRow(id: $0) }
        }
    }
}
struct CountingRow: View {
    let id: Int
    var body: some View {
        let _ = rowsBuilt += 1
        PerformanceRow(id: id)
    }
}

// Section 8: a stable id vs a computed id that returns a new UUID on every access
struct StableItem: Identifiable { let id = UUID(); let title: String }
struct ComputedItem: Identifiable {
    var id: UUID {
        UUID()
    }

    let title: String
}
@MainActor @Observable final class IDModel { var mode = "stable" }
struct IdentityLab: View {
    static let model = IDModel()
    @State private var stable = (0..<20).map { StableItem(title: "Transaction \($0)") }
    @State private var computed = (0..<20).map { ComputedItem(title: "Transaction \($0)") }
    @State private var refreshes = 0

    var body: some View {
        VStack {
            Text("Refreshes: \(refreshes)")
            Button("Refresh") { refreshes += 1 }
            if IdentityLab.model.mode == "stable" {
                List(stable) { item in CountingTitleRow(title: item.title, marker: refreshes) }
            } else {
                List(computed) { item in CountingTitleRow(title: item.title, marker: refreshes) }
            }
        }
    }
}
struct CountingTitleRow: View {
    let title: String
    let marker: Int   // unused by the row's look; the parent passes its counter, like many real rows receive context
    var body: some View {
        let _ = rowsBuilt += 1
        Text(title)
            .onAppear { appears += 1 }
    }
}

// Section 15, verbatim
func makeDemoTransactions(
    count: Int
) -> [Transaction] {
    (0..<count).map { index in
        Transaction(
            id: UUID(),
            title: "Demo Transaction \(index)",
            amountPaise: -(index + 1) * 100,
            date: Date().addingTimeInterval(
                -Double(index) * 60
            )
        )
    }
}

// Sections 11 and 13: a sort in body and a filtered computed property, counted
struct SearchLab: View {
    @State private var transactions = makeDemoTransactions(count: 50_000)
    @State private var searchText = ""

    private var filteredTransactions: [Transaction] {
        guard !searchText.isEmpty else {
            return transactions
        }
        filtersRun += 1
        return transactions.filter {
            $0.title.localizedCaseInsensitiveContains(
                searchText
            )
        }
    }

    var body: some View {
        let sorted = filteredTransactions.sorted { $0.date > $1.date }
        let _ = sortsRun += 1
        NavigationStack {
            List(sorted) { transaction in
                Text(transaction.title)
            }
            .searchable(text: $searchText)
            .navigationTitle("Search Lab")
        }
    }
}

// Section 20: generating 50,000 records synchronously in a button action
struct BlockLab: View {
    nonisolated(unsafe) static var frames = 0
    nonisolated(unsafe) static var count = 50_000
    nonisolated(unsafe) static var busy = 0.0
    nonisolated(unsafe) static var framesDuring = 0
    @State private var transactions: [Transaction] = []

    var body: some View {
        VStack(spacing: 20) {
            Button("Load Transactions") {
                let t0 = CACurrentMediaTime(), f0 = BlockLab.frames   // measurement only

                let records = makeDemoTransactions(
                    count: BlockLab.count   // 50_000 as in the text; 500_000 in the block_big run
                )

                transactions = records
                BlockLab.busy = CACurrentMediaTime() - t0; BlockLab.framesDuring = BlockLab.frames - f0
            }
            Text("Loaded: \(transactions.count)")
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


// ===================== Complete code through Lesson 3.11 =====================

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
        .environment(preferences)
        .preferredColorScheme(
            preferences.appearance.colorScheme
        )
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
                .accessibilityIdentifier(NPayAccessibilityID.recipientField)
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
                .accessibilityIdentifier(NPayAccessibilityID.amountField)

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
                .accessibilityIdentifier(NPayAccessibilityID.sendButton)

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
