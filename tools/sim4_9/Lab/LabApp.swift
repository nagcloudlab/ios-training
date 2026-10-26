import SwiftUI
import UIKit
import NPayDomain
import NPayData

// Lesson 4.9 evidence app (the 4.8 layout; PaymentViewModel now depends on SendPaymentExecuting): NPay sources split into the section 2 folders (still one app module, "NPay"), with the
// domain types imported from NPayCore's NPayDomain module and NPayData linked in. The driver prints which module each
// type lives in, makes a payment, visits all four tabs, and runs NPayData's InMemoryAccountRepository from the app.
// A DEBUG-only hook gives the driver the store; it is not NPay code.
@main
struct LabApp: App {
    init() { setvbuf(stdout, nil, _IONBF, 0) }

    var body: some Scene {
        WindowGroup {
            let a = ProcessInfo.processInfo.arguments
            NPayRootView().task {
                if a.contains("modules") { await modules() }
                else if a.contains("verify") { await verify() }
            }
        }
    }
}

@MainActor enum NPayDebug {
    static var router: NPayRouter?
    static var store: NPayStore?
    static var preferences: NPayPreferences?
    static var latency: Duration?
    static func attach(_ r: NPayRouter, _ s: NPayStore, _ p: NPayPreferences) { router = r; store = s; preferences = p }
    static func wrap(_ repository: any AccountRepository) -> any AccountRepository { repository }
}

@MainActor func modules() async {
    await wait(1)
    for (label, type) in [("PaymentsScreen (Features/Payments)", String(reflecting: PaymentsScreen.self)),
                          ("NPayStore (Data)", String(reflecting: NPayStore.self)),
                          ("Money (Domain/Models)", String(reflecting: Money.self)),
                          ("PaymentAmount", String(reflecting: PaymentAmount.self)),
                          ("SendPaymentUseCase", String(reflecting: SendPaymentUseCase.self)),
                          ("InMemoryAccountRepository", String(reflecting: InMemoryAccountRepository.self))] {
        print("\(label): \(type)")
    }
    let repository = InMemoryAccountRepository()
    let useCase = SendPaymentUseCase(repository: repository, policy: PaymentPolicy(maximumPerPaymentPaise: 10_000_000))
    do {
        let record = try await useCase.execute(SendPaymentCommand(recipient: try PaymentRecipient("ravi@npay"), amount: try PaymentAmount(paise: 150_050)))
        print("NPayDomain use case over NPayData repository, from the app: recorded \(record.amountPaise); balance \(try await repository.fetchSnapshot().balancePaise)")
    } catch { print("error \(error)") }
}

@MainActor func verify() async {
    await wait(1.5)
    guard let store = NPayDebug.store else { return }
    await selectTab("Payments")
    await fill()
    await press("Review Payment", quiet: true)
    await press("Confirm Demo Payment", quiet: true)
    await wait(1.2)
    print("payment: \(labels().contains("Payment Recorded") ? "Payment Recorded" : "?"); balancePaise \(store.balancePaise), transactions \(store.transactions.count)")
    await press("Back to Dashboard", quiet: true)
    for tab in ["Home", "Payments", "History", "Profile"] {
        await selectTab(tab)
        let title = tab == "Home" ? "NPay" : tab
        let shown = labels().contains(title) ? title : "?"
        let extra = tab == "Home" ? (labels().first { $0.contains("Available Balance") } ?? "") : tab == "History" ? (labels().first { $0.hasPrefix("Sent to") } ?? "") : ""
        print("tab \(tab): title \(shown)\(extra.isEmpty ? "" : "; \(extra)")")
    }
}
