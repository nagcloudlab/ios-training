import Testing
import NPayDomain
import NPayData
@testable import NPayPayments

@MainActor
struct PaymentViewModelTests {

    @Test
    func successfulPaymentUpdatesState() async throws {

        let mock = MockSendPaymentUseCase(
            shouldFail: false
        )

        let viewModel = PaymentViewModel(
            sendPayment: mock
        )

        let command = SendPaymentCommand(
            recipient: try PaymentRecipient("ravi@npay"),
            amount: try PaymentAmount(paise: 150_050)
        )

        let result = await viewModel.submit(command)

        if case .success(let record) = result {
            #expect(record.amountPaise == 150_050)
        } else {
            Issue.record("Expected success")
        }

        if case .success = viewModel.state {
            // Correct state.
        } else {
            Issue.record("Expected success UI state")
        }
    }
}

@MainActor
struct PaymentFailureTests {

    @Test
    func insufficientBalanceUpdatesFailureState() async throws {

        let mock = MockSendPaymentUseCase(
            shouldFail: true
        )

        let viewModel = PaymentViewModel(
            sendPayment: mock
        )

        let command = SendPaymentCommand(
            recipient: try PaymentRecipient("ravi@npay"),
            amount: try PaymentAmount(paise: 150_050)
        )

        let result = await viewModel.submit(command)

        if case .failure(let message) = result {
            #expect(message == "Insufficient balance")
        } else {
            Issue.record("Expected failure result")
        }

        if case .failure(let message) = viewModel.state {
            #expect(message == "Insufficient balance")
        } else {
            Issue.record("Expected failure UI state")
        }
    }
}

@MainActor
@Test
func duplicateSubmissionIsRejected() async throws {

    let mock = SuspendedPaymentUseCase()

    let viewModel = PaymentViewModel(
        sendPayment: mock
    )

    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 150_050)
    )

    let firstTask = Task {
        await viewModel.submit(command)
    }

    // Wait until the mock has received the first call.
    while await mock.calls() == 0 {
        await Task.yield()
    }

    let secondResult = await viewModel.submit(command)

    if case .failure = secondResult {
        // Expected local rejection.
    } else {
        Issue.record("Expected duplicate rejection")
    }

    #expect(await mock.calls() == 1)

    await mock.succeed()

    let firstResult = await firstTask.value

    if case .success = firstResult {
        // Expected.
    } else {
        Issue.record("Expected first payment to succeed")
    }
}

// Ours: the real chain, so the user-facing message is checked end to end (Lesson 4.7's mapping)
@MainActor
@Test
func realChainShowsInsufficientBalanceMessage() async throws {
    let repository = InMemoryAccountRepository(initialBalancePaise: 10_000)
    let viewModel = PaymentViewModel(
        sendPayment: SendPaymentUseCase(repository: repository, policy: PaymentPolicy(maximumPerPaymentPaise: 10_000_000))
    )
    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 50_000)
    )

    let result = await viewModel.submit(command)

    guard case .failure(let message) = result else {
        Issue.record("Expected failure"); return
    }
    #expect(message == "Insufficient balance")
    #expect(try await repository.fetchSnapshot().balancePaise == 10_000)
}
