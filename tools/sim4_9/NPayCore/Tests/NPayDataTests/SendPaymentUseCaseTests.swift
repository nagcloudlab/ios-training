import Testing
@testable import NPayDomain
@testable import NPayData

@Test
func useCaseEnforcesPaymentLimit() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 20_000_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository,
        policy: PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 15_000_000)
    )

    do {
        _ = try await useCase.execute(command)
        Issue.record("Expected limitExceeded")
    } catch PaymentDomainError.limitExceeded {
        // Expected.
    }

    let snapshot = try await repository.fetchSnapshot()

    #expect(snapshot.transactions.isEmpty)
}

@Test
func paymentIntegrationTest() async throws {

    let repository = InMemoryAccountRepository(
        initialBalancePaise: 2_500_000
    )

    let useCase = SendPaymentUseCase(
        repository: repository,
        policy: PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 150_050)
    )

    let payment = try await useCase.execute(command)

    let snapshot = try await repository.fetchSnapshot()

    #expect(payment.amountPaise == 150_050)
    #expect(snapshot.balancePaise == 2_349_950)
    #expect(snapshot.transactions.count == 1)
    #expect(snapshot.transactions.first?.id == payment.id)
}
