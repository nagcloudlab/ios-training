import Testing
@testable import NPayDomain
@testable import NPayData

struct AccountRepositoryTests {

    @Test
    func paymentUpdatesBalanceAndHistory() async throws {

        let repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000
        )

        let payment = try await repository.recordPayment(
            recipient: "ravi@npay",
            amountPaise: 150_050
        )

        let snapshot = try await repository.fetchSnapshot()

        #expect(payment.amountPaise == 150_050)
        #expect(snapshot.balancePaise == 2_349_950)
        #expect(snapshot.transactions.count == 1)
    }

    @Test
    func insufficientBalanceDoesNotChangeState() async throws {

        let repository = InMemoryAccountRepository(
            initialBalancePaise: 10_000
        )

        do {
            _ = try await repository.recordPayment(
                recipient: "ravi@npay",
                amountPaise: 50_000
            )

            Issue.record("Expected insufficient balance")
        } catch AccountRepositoryError.insufficientBalance {
            // Expected rejection.
        }

        let snapshot = try await repository.fetchSnapshot()

        #expect(snapshot.balancePaise == 10_000)
        #expect(snapshot.transactions.isEmpty)
    }

    @Test
    func concurrentPaymentsDoNotOverdraw() async throws {

        let repository = InMemoryAccountRepository(
            initialBalancePaise: 200_000
        )

        async let first = attemptPayment(
            repository: repository,
            recipient: "a@npay",
            amountPaise: 150_000
        )

        async let second = attemptPayment(
            repository: repository,
            recipient: "b@npay",
            amountPaise: 150_000
        )

        let results = await [first, second]

        let successCount = results.filter {
            if case .success = $0 { return true }
            return false
        }.count

        let snapshot = try await repository.fetchSnapshot()

        #expect(successCount == 1)
        #expect(snapshot.balancePaise == 50_000)
        #expect(snapshot.transactions.count == 1)
    }
}

func attemptPayment(
    repository: InMemoryAccountRepository,
    recipient: String,
    amountPaise: Int
) async -> Result<PaymentRecord, Error> {
    do {
        let record = try await repository.recordPayment(
            recipient: recipient,
            amountPaise: amountPaise
        )
        return .success(record)
    } catch {
        return .failure(error)
    }
}
