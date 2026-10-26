import SwiftUI

enum PaymentValidationError: Error {
    case emptyRecipient
    case invalidAmount
    case insufficientBalance
}

struct PaymentValidator {

    func validate(
        recipient: String,
        amountPaise: Int,
        balancePaise: Int
    ) throws {

        guard !recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        ).isEmpty else {
            throw PaymentValidationError.emptyRecipient
        }

        guard amountPaise > 0 else {
            throw PaymentValidationError.invalidAmount
        }

        guard amountPaise <= balancePaise else {
            throw PaymentValidationError.insufficientBalance
        }
    }
}
