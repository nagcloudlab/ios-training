import XCTest
@testable import NPayDomain

final class PaymentAmountTests: XCTestCase {

    func testValidAmount() throws {
        let amount = try PaymentAmount(paise: 150_050)

        XCTAssertEqual(amount.paise, 150_050)
    }

    func testZeroAmountRejected() {
        XCTAssertThrowsError(
            try PaymentAmount(paise: 0)
        )
    }

    func testNegativeAmountRejected() {
        XCTAssertThrowsError(
            try PaymentAmount(paise: -100)
        )
    }
}
