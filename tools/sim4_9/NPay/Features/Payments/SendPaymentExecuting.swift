import NPayDomain

// Lesson 4.9, section 14
protocol SendPaymentExecuting: Sendable {
    func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord
}

extension SendPaymentUseCase: SendPaymentExecuting {}
