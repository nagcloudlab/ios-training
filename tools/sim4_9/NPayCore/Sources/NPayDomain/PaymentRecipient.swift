import Foundation

public struct PaymentRecipient: Equatable, Sendable {
    public let identifier: String

    public init(_ identifier: String) throws {
        let trimmed = identifier.trimmingCharacters(
            in: .whitespacesAndNewlines
        )

        guard !trimmed.isEmpty else {
            throw PaymentDomainError.invalidRecipient
        }

        self.identifier = trimmed
    }
}
