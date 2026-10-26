import Foundation

public struct PaymentRecord: Identifiable, Sendable {
    public let id: UUID
    public let recipient: String
    public let amountPaise: Int
    public let createdAt: Date

    public init(
        id: UUID,
        recipient: String,
        amountPaise: Int,
        createdAt: Date
    ) {
        self.id = id
        self.recipient = recipient
        self.amountPaise = amountPaise
        self.createdAt = createdAt
    }
}

public struct AccountSnapshot: Sendable {
    public let balancePaise: Int
    public let transactions: [PaymentRecord]

    public init(
        balancePaise: Int,
        transactions: [PaymentRecord]
    ) {
        self.balancePaise = balancePaise
        self.transactions = transactions
    }
}

public enum AccountRepositoryError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
}

public protocol AccountRepository: Sendable {
    func fetchSnapshot() async throws -> AccountSnapshot

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord
}
