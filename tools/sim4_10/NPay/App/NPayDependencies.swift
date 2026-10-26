import SwiftUI
import NPayDomain
import NPayData

// Lesson 4.10 (section 3; 4.5's NPayDependencies): one repository for the whole app; Home, History and Payments all
// read and write the same account state through it.
@MainActor
final class NPayDependencies {

    let repository: any AccountRepository

    init() {
        repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000,
            transactions: NPayDependencies.demoHistory
        )
    }

    // Unit 3's two demo payments (ours: the repository models outgoing payments only)
    static let demoHistory = [
        PaymentRecord(id: UUID(), recipient: "Coffee Shop", amountPaise: 25_000, createdAt: .now),
        PaymentRecord(id: UUID(), recipient: "Electricity Bill", amountPaise: 120_000, createdAt: .now)
    ]

    func makeDashboardViewModel() -> DashboardViewModel {
        DashboardViewModel(repository: repository)
    }

    func makePaymentViewModel(
        availableBalance: @escaping @MainActor () -> Int
    ) -> PaymentViewModel {
        NPayFactory.makePaymentViewModel(
            repository: repository,
            availableBalance: availableBalance
        )
    }
}
