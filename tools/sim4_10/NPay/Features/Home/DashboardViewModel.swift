import SwiftUI
import NPayDomain

// Lesson 4.5, section 11 (moved into the app in 4.10): presentation state derived from the repository
@MainActor
@Observable
final class DashboardViewModel {

    private let repository: any AccountRepository

    var balancePaise = 0
    var transactions: [PaymentRecord] = []
    var refreshFailed = false   // Lesson 4.10 (ours): reported separately from any payment result

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func refresh() async throws {
        let snapshot = try await repository.fetchSnapshot()

        balancePaise = snapshot.balancePaise
        transactions = snapshot.transactions
    }

    // Lesson 4.10 (ours): a failed refresh never turns a confirmed payment into a failure
    func reload() async {
        do {
            try await refresh()
            refreshFailed = false
        } catch {
            refreshFailed = true
        }
    }

    // The existing rows and screens display Transaction values
    var displayTransactions: [Transaction] {
        transactions.map {
            Transaction(id: $0.id, title: "Sent to \($0.recipient)", amountPaise: -$0.amountPaise, date: $0.createdAt)
        }
    }
}
