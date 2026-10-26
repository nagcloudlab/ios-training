import SwiftUI
import NPayDomain

enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown

    var isBusy: Bool {
        switch self {
        case .validating, .submitting:
            true
        default:
            false
        }
    }
}

enum PaymentSubmissionResult {
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown
}
