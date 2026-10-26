import SwiftUI
import NPayDomain

struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let command: SendPaymentCommand
}
