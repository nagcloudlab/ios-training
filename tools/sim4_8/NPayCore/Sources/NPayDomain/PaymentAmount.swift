import Foundation

public enum PaymentDomainError: Error {
    case invalidAmount
    case invalidRecipient
    case insufficientBalance
    case limitExceeded
}

public struct PaymentAmount: Equatable, Sendable {
    public let paise: Int

    public init(paise: Int) throws {
        guard paise > 0 else {
            throw PaymentDomainError.invalidAmount
        }

        self.paise = paise
    }
}
