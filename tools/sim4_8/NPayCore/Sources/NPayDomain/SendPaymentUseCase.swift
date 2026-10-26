import Foundation

public struct SendPaymentCommand: Sendable {
    public let recipient: PaymentRecipient
    public let amount: PaymentAmount

    public init(recipient: PaymentRecipient, amount: PaymentAmount) {
        self.recipient = recipient
        self.amount = amount
    }
}

public struct PaymentPolicy: Sendable {
    public let maximumPerPaymentPaise: Int

    public init(maximumPerPaymentPaise: Int) {
        self.maximumPerPaymentPaise = maximumPerPaymentPaise
    }

    public func validate(_ amount: PaymentAmount) throws {
        guard amount.paise <= maximumPerPaymentPaise else {
            throw PaymentDomainError.limitExceeded
        }
    }
}

public struct SendPaymentUseCase: Sendable {
    public let repository: any AccountRepository
    public let policy: PaymentPolicy

    public init(repository: any AccountRepository, policy: PaymentPolicy) {
        self.repository = repository
        self.policy = policy
    }

    public func execute(
        _ command: SendPaymentCommand
    ) async throws -> PaymentRecord {

        try policy.validate(command.amount)

        // Lesson 4.7: translate the repository's errors into domain errors
        do {
            return try await repository.recordPayment(
                recipient: command.recipient.identifier,
                amountPaise: command.amount.paise
            )
        } catch AccountRepositoryError.insufficientBalance {
            throw PaymentDomainError.insufficientBalance
        } catch AccountRepositoryError.invalidRecipient {
            throw PaymentDomainError.invalidRecipient
        } catch AccountRepositoryError.invalidAmount {
            throw PaymentDomainError.invalidAmount
        }
    }
}
