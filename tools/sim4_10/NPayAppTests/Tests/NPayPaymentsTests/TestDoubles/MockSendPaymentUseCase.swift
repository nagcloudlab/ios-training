import Foundation
import NPayDomain
@testable import NPayPayments

struct MockSendPaymentUseCase: SendPaymentExecuting {

    let shouldFail: Bool

    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        if shouldFail {
            throw PaymentDomainError.insufficientBalance
        }

        return PaymentRecord(
            id: UUID(),
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise,
            createdAt: .now
        )
    }
}
