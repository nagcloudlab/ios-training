import Testing
@testable import NPayDomain

struct PaymentPolicyTests {

    let policy = PaymentPolicy(
        maximumPerPaymentPaise: 10_000_000
    )

    @Test
    func acceptsAmountAtLimit() throws {
        let amount = try PaymentAmount(
            paise: 10_000_000
        )

        try policy.validate(amount)
    }

    @Test
    func rejectsAmountAboveLimit() throws {
        let amount = try PaymentAmount(
            paise: 10_000_001
        )

        #expect(throws: PaymentDomainError.self) {
            try policy.validate(amount)
        }
    }
}

// Lab checklist: PaymentRecipient validation (ours)
struct PaymentRecipientTests {

    @Test
    func trimsWhitespace() throws {
        #expect(try PaymentRecipient("  ravi@npay ").identifier == "ravi@npay")
    }

    @Test(arguments: ["", "   ", "\n"])
    func rejectsBlank(identifier: String) {
        #expect(throws: PaymentDomainError.invalidRecipient) {
            try PaymentRecipient(identifier)
        }
    }
}
