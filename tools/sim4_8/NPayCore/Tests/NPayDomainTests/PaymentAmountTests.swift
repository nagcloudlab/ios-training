import Testing
import NPayDomain

@Test func positiveAmountIsAccepted() throws {
    #expect(try PaymentAmount(paise: 150_050).paise == 150_050)
}

@Test func zeroAmountIsRejected() {
    #expect(throws: PaymentDomainError.invalidAmount) {
        try PaymentAmount(paise: 0)
    }
}
