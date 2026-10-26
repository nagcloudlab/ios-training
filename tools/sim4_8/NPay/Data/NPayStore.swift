import SwiftUI

@MainActor
@Observable
final class NPayStore {

    var balancePaise = 2_500_000

    var transactions: [Transaction] = [
        Transaction(
            id: UUID(),
            title: "Coffee Shop",
            amountPaise: -25_000,
            date: .now
        ),
        Transaction(
            id: UUID(),
            title: "Electricity Bill",
            amountPaise: -120_000,
            date: .now
        ),
        Transaction(
            id: UUID(),
            title: "Salary Credit",
            amountPaise: 4_500_000,
            date: .now
        )
    ]

    // Lesson 4.2: the payment form state moved to PaymentViewModel

    func recordDemoPayment(
        recipient: String,
        amountPaise: Int
    ) -> UUID? {

        // Lesson 4.1: the rules live in PaymentValidator
        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amountPaise,
                balancePaise: balancePaise
            )
        } catch {
            return nil
        }

        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        let id = UUID()

        balancePaise -= amountPaise

        transactions.insert(
            Transaction(
                id: id,
                title: "Sent to \(trimmed)",
                amountPaise: -amountPaise,
                date: .now
            ),
            at: 0
        )

        return id
    }
}
