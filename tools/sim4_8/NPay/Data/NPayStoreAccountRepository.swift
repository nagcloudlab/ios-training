import SwiftUI
import NPayDomain

@MainActor
final class NPayStoreAccountRepository: AccountRepository {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func fetchSnapshot() async throws -> AccountSnapshot {
        AccountSnapshot(
            balancePaise: store.balancePaise,
            transactions: store.transactions
                .filter { $0.amountPaise < 0 }
                .map { PaymentRecord(id: $0.id, recipient: $0.title, amountPaise: -$0.amountPaise, createdAt: $0.date) }
        )
    }

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord {
        let trimmed = recipient.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw AccountRepositoryError.invalidRecipient }
        guard amountPaise > 0 else { throw AccountRepositoryError.invalidAmount }

        // The store checks the balance and records the payment in one main-actor call (no suspension)
        guard let id = store.recordDemoPayment(recipient: trimmed, amountPaise: amountPaise) else {
            throw AccountRepositoryError.insufficientBalance
        }
        return PaymentRecord(id: id, recipient: trimmed, amountPaise: amountPaise, createdAt: .now)
    }
}
