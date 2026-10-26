import Foundation
import NPayDomain

public actor InMemoryAccountRepository: AccountRepository {

    private var balancePaise: Int
    private var transactions: [PaymentRecord] = []

    public init(initialBalancePaise: Int = 2_500_000) {
        self.balancePaise = initialBalancePaise
    }

    public func fetchSnapshot() async throws -> AccountSnapshot {
        AccountSnapshot(
            balancePaise: balancePaise,
            transactions: transactions
        )
    }

    public func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord {

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty else {
            throw AccountRepositoryError.invalidRecipient
        }

        guard amountPaise > 0 else {
            throw AccountRepositoryError.invalidAmount
        }

        guard amountPaise <= balancePaise else {
            throw AccountRepositoryError.insufficientBalance
        }

        let record = PaymentRecord(
            id: UUID(),
            recipient: trimmed,
            amountPaise: amountPaise,
            createdAt: .now
        )

        balancePaise -= amountPaise
        transactions.insert(record, at: 0)

        return record
    }
}
