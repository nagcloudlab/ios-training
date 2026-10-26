import Testing
@testable import NPayDomain

struct PaymentAmountSwiftTests {

    @Test
    func validAmount() throws {
        let amount = try PaymentAmount(paise: 150_050)

        #expect(amount.paise == 150_050)
    }

    @Test
    func zeroAmountRejected() {
        #expect(throws: PaymentDomainError.self) {
            try PaymentAmount(paise: 0)
        }
    }
}

struct PaymentAmountParameterizedTests {

    @Test(arguments: [0, -1, -100, -50_000])
    func rejectsNonPositiveAmounts(paise: Int) {
        #expect(throws: PaymentDomainError.self) {
            try PaymentAmount(paise: paise)
        }
    }
}
