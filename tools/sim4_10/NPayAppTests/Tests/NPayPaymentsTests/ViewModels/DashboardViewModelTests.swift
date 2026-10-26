import Testing
import Foundation
import NPayDomain
import NPayData
@testable import NPayPayments

// Lesson 4.10 (ours): the dashboard and the payment feature share one repository
@MainActor
struct DashboardViewModelTests {

    @Test
    func dashboardShowsThePaymentAfterRefresh() async throws {
        let repository = InMemoryAccountRepository()
        let dashboard = DashboardViewModel(repository: repository)
        let payments = PaymentViewModel(
            sendPayment: SendPaymentUseCase(repository: repository, policy: PaymentPolicy(maximumPerPaymentPaise: 10_000_000))
        )
        await dashboard.reload()
        #expect(dashboard.balancePaise == 2_500_000)

        let command = SendPaymentCommand(
            recipient: try PaymentRecipient("ravi@npay"),
            amount: try PaymentAmount(paise: 150_050)
        )
        _ = await payments.submit(command)
        #expect(dashboard.balancePaise == 2_500_000)   // a snapshot: unchanged until refreshed

        await dashboard.reload()
        #expect(dashboard.balancePaise == 2_349_950)
        #expect(dashboard.displayTransactions.first?.title == "Sent to ravi@npay")
    }

    @Test
    func failedRefreshKeepsTheLastSnapshot() async throws {
        let dashboard = DashboardViewModel(repository: FailingSnapshotRepository())
        await dashboard.reload()
        #expect(dashboard.refreshFailed)
        #expect(dashboard.balancePaise == 0)
    }
}

struct FailingSnapshotRepository: AccountRepository {
    struct Unavailable: Error {}
    func fetchSnapshot() async throws -> AccountSnapshot { throw Unavailable() }
    func recordPayment(recipient: String, amountPaise: Int) async throws -> PaymentRecord { throw Unavailable() }
}
