import Foundation
import NPayDomain
@testable import NPayPayments

actor SuspendedPaymentUseCase: SendPaymentExecuting {

    private var continuation:
        CheckedContinuation<PaymentRecord, Error>?

    private var invocationCount = 0

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        invocationCount += 1

        return try await withCheckedThrowingContinuation {
            continuation = $0
        }
    }

    func calls() -> Int {
        invocationCount
    }

    func succeed() {
        continuation?.resume(
            returning: PaymentRecord(
                id: UUID(),
                recipient: "ravi@npay",
                amountPaise: 150_050,
                createdAt: .now
            )
        )

        continuation = nil
    }
}
