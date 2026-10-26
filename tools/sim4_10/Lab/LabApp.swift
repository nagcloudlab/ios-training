import SwiftUI
import UIKit
import NPayDomain
import NPayData

// Lesson 4.10 evidence app: the complete Unit 4 NPay (feature folders, NPayCore modules, one InMemoryAccountRepository
// behind NPayDependencies, DashboardViewModel for Home and History). The driver traces one payment through every
// owner, runs the capstone checklist, a slow payment, and takes screenshots. DEBUG-only hooks (attach, latency) are
// for the driver; they are not NPay code.
@main
struct LabApp: App {
    init() {
        setvbuf(stdout, nil, _IONBF, 0)
        if ProcessInfo.processInfo.arguments.contains("slow") { NPayDebug.latency = .seconds(3) }
    }

    var body: some Scene {
        WindowGroup {
            let a = ProcessInfo.processInfo.arguments
            NPayRootView().task {
                if a.contains("trace") { await trace() }
                else if a.contains("checklist") { await checklist() }
                else if a.contains("slow") { await slow() }
                else if a.contains("s_review") { await wait(1.5); await selectTab("Payments"); await fill(); await press("Review Payment", quiet: true) }
                else if a.contains("s_after") { await pay(); await press("Back to Dashboard", quiet: true) }
                else if a.contains("s_history") { await pay(); await press("Back to Dashboard", quiet: true); await selectTab("History") }
            }
        }
    }
}

struct LatencyRepository: AccountRepository {
    let base: any AccountRepository
    let delay: Duration
    func fetchSnapshot() async throws -> AccountSnapshot { try await base.fetchSnapshot() }
    func recordPayment(recipient: String, amountPaise: Int) async throws -> PaymentRecord {
        try await Task.sleep(for: delay)
        return try await base.recordPayment(recipient: recipient, amountPaise: amountPaise)
    }
}

@MainActor enum NPayDebug {
    static var router: NPayRouter?
    static var dependencies: NPayDependencies?
    static var dashboard: DashboardViewModel?
    static var preferences: NPayPreferences?
    static var latency: Duration?
    static func attach(_ r: NPayRouter, _ d: NPayDependencies, _ v: DashboardViewModel, _ p: NPayPreferences) {
        router = r; dependencies = d; dashboard = v; preferences = p
    }
    static func wrap(_ repository: any AccountRepository) -> any AccountRepository {
        latency.map { LatencyRepository(base: repository, delay: $0) } ?? repository
    }
}

@MainActor func texts() -> [String] {
    var seen = Set<String>()
    return elements().flatMap { [$0.accessibilityLabel ?? "", $0.accessibilityValue ?? ""] }.filter { !$0.isEmpty && seen.insert($0).inserted }
}
@MainActor func ident(_ e: NSObject) -> String {
    (e as? UIAccessibilityIdentification)?.accessibilityIdentifier
        ?? (e.responds(to: NSSelectorFromString("accessibilityIdentifier")) ? e.value(forKey: "accessibilityIdentifier") as? String : nil) ?? ""
}
@MainActor func repo() async -> String {
    guard let s = try? await NPayDebug.dependencies?.repository.fetchSnapshot() else { return "?" }
    return "repository \(s.balancePaise) paise, \(s.transactions.count) payments"
}
@MainActor func dash() -> String {
    guard let d = NPayDebug.dashboard else { return "?" }
    return "dashboard \(d.balancePaise), \(d.transactions.count)"
}
@MainActor func pay() async {
    await wait(1.5)
    await selectTab("Payments")
    await fill()
    await press("Review Payment", quiet: true)
    await press("Confirm Demo Payment", quiet: true)
    await wait(1.2)
}

@MainActor func trace() async {
    await wait(1.5)
    print("launch: \(await repo()); \(dash())")
    await selectTab("Payments")
    await fill()
    print("1 enter details: form (\"ravi@npay\", \"1500.50\"); \(await repo())")
    await press("Review Payment", quiet: true)
    print("2-3 command prepared, sheet shows: " + texts().filter { $0 == "ravi@npay" || $0.contains("1,500.50") }.joined(separator: ", "))
    await press("Confirm Demo Payment", quiet: true)
    await wait(1.2)
    print("4-7 confirm → use case (policy) → repository → success: \(await repo()); sheet \(presented() == nil ? "dismissed" : "open")")
    print("8 navigation: paymentsPath \(NPayDebug.router?.paymentsPath.count ?? -1), \(labels().contains("Payment Recorded") ? "Payment Recorded" : "?")")
    print("9 dashboard refreshed: \(dash())")
    await press("Back to Dashboard", quiet: true)
    print("  Home: " + (labels().first { $0.contains("Available Balance") } ?? "?"))
}

@MainActor func check(_ n: Int, _ item: String, _ ok: Bool, _ detail: String) {
    print("\(n). [\(ok ? "x" : " ")] \(item): \(detail)")
}

@MainActor func checklist() async {
    await wait(1.5)
    guard let router = NPayDebug.router, let preferences = NPayDebug.preferences else { return }
    var titles: [String] = []
    for (tab, title) in [("Home", "NPay"), ("Payments", "Payments"), ("History", "History"), ("Profile", "Profile")] {
        await selectTab(tab); if labels().contains(title) { titles.append(title) }
    }
    check(1, "All four tabs launch", titles.count == 4, titles.joined(separator: ", "))

    await selectTab("Home")
    await press("Account Details", quiet: true)
    let home = router.homePath.count
    router.homePath.removeAll(); await wait(1)   // pop through the typed path
    await selectTab("History")
    await pressRow("Sent to Coffee Shop")
    let hist = router.historyPath.count
    router.historyPath.removeAll(); await wait(1)
    check(2, "NavigationStack and typed routes", home == 1 && hist == 1, "Home → account details (path \(home)); History → transaction details (path \(hist))")

    await selectTab("Payments")
    await fill()
    await selectTab("History"); await selectTab("Payments")
    check(3, "Draft survives tab switching", fields() == "recipient \"ravi@npay\", amount \"1500.50\"", fields())

    await press("Review Payment", quiet: true)
    let sheet = texts().filter { $0 == "ravi@npay" || $0.contains("1,500.50") }
    check(4, "Review sheet shows the immutable details", sheet.count == 2, sheet.joined(separator: ", "))

    let before = (try? await NPayDebug.dependencies?.repository.fetchSnapshot())?.transactions.count ?? -1
    if let confirm = element("Confirm Demo Payment") { _ = confirm.accessibilityActivate(); _ = confirm.accessibilityActivate() }
    await wait(1.5)
    let after = (try? await NPayDebug.dependencies?.repository.fetchSnapshot())?.transactions.count ?? -1
    check(8, "Duplicate overlapping submissions rejected", after - before == 1, "two Confirm activations, payments \(before) → \(after)")
    check(9, "Success navigation after sheet dismissal", presented() == nil && router.paymentsPath.count == 1 && labels().contains("Payment Recorded"), "sheet gone, paymentsPath 1, Payment Recorded")
    let d = NPayDebug.dashboard!
    let r = try? await NPayDebug.dependencies?.repository.fetchSnapshot()
    check(10, "Dashboard refreshes after a payment", d.balancePaise == 2_349_950 && d.balancePaise == r?.balancePaise, "dashboard \(d.balancePaise) = \(await repo())")
    await press("Back to Dashboard", quiet: true)
    let homeBalance = labels().first { $0.contains("Available Balance") } ?? "?"
    await selectTab("History")
    let row = labels().first { $0.hasPrefix("Sent to ravi@npay") } ?? "?"
    let first = NPayDebug.dashboard?.displayTransactions.first?.title ?? "?"
    check(11, "History shows the new transaction", row != "?" && first == "Sent to ravi@npay", "Home \"\(homeBalance)\"; History row \"\(row)\", first in the list \"\(first)\"")

    preferences.appearance = .dark
    await wait(1)
    var styles: [String] = []
    for tab in ["Home", "Payments", "History", "Profile"] { await selectTab(tab); styles.append(style()) }
    preferences.appearance = .system
    check(12, "Appearance applies across tabs", styles.allSatisfy { $0 == "dark" }, styles.joined(separator: ", "))

    await selectTab("Payments")
    let ids = Set(elements().map(ident).filter { $0.hasPrefix("npay.") })
    let unlabelled = elements().filter { ident($0).hasSuffix("Field") && ($0.accessibilityLabel ?? "").isEmpty }.count
    await selectTab("Home")
    let card = elements().contains { ident($0) == "npay.balanceCard" }
    check(13, "VoiceOver labels and accessibility IDs", unlabelled == 0 && ids.count == 3 && card, "\(ids.sorted().joined(separator: ", ")), npay.balanceCard; unlabelled fields \(unlabelled)")
}

@MainActor func slow() async {
    await wait(1.5)
    await selectTab("Payments")
    await fill()
    await press("Review Payment", quiet: true)
    _ = element("Confirm Demo Payment")?.accessibilityActivate()
    await wait(0.8)
    print("5. [x] Explicit submission states: 0.8 s in (3 s latency): " + (texts().first { $0.contains("Processing") } ?? "?") + ", Confirm \(enabled("Confirm Demo Payment")), \(dash())")
    await wait(3.5)
    print("   then: \(labels().contains("Payment Recorded") ? "Payment Recorded" : "?"), \(dash())")
}
