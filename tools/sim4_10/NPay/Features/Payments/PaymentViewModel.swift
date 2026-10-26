import SwiftUI
import NPayDomain

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    private(set) var state: PaymentUIState = .idle

    private let sendPayment: any SendPaymentExecuting   // Lesson 4.9, section 14: a protocol, so tests can inject a mock
    private let availableBalance: @MainActor () -> Int   // integration (ours): read-only balance

    init(
        sendPayment: any SendPaymentExecuting,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) {
        self.sendPayment = sendPayment
        self.availableBalance = availableBalance
    }

    var availableBalancePaise: Int {
        availableBalance()
    }

    var parsedAmountPaise: Int? {
        Money.parsePaise(amountText)
    }

    // Lesson 4.2, section 7
    func validate(
        availableBalancePaise: Int
    ) -> Bool {

        guard let amount = parsedAmountPaise else {
            return false
        }

        do {
            try PaymentValidator().validate(
                recipient: recipient,
                amountPaise: amount,
                balancePaise: availableBalancePaise
            )

            return true
        } catch {
            return false
        }
    }

    // Lesson 4.6 integration (ours): the immutable command the sheet shows and Confirm submits
    func prepareCommand() -> ValidatedPaymentRequest? {
        guard let paise = parsedAmountPaise,
              validate(availableBalancePaise: availableBalancePaise),
              let recipient = try? PaymentRecipient(recipient),
              let amount = try? PaymentAmount(paise: paise) else {
            return nil
        }

        return ValidatedPaymentRequest(
            command: SendPaymentCommand(recipient: recipient, amount: amount)
        )
    }

    // Section 20: returns the result of this submission; publishes state for rendering
    func submit(
        _ command: SendPaymentCommand
    ) async -> PaymentSubmissionResult {

        guard !state.isBusy else {
            return .failure("A payment is already processing")
        }

        state = .validating
        state = .submitting

        do {
            let record = try await sendPayment.execute(command)

            state = .success(record)
            recipient = ""
            amountText = ""

            return .success(record)

        } catch PaymentDomainError.insufficientBalance {
            let message = "Insufficient balance"
            state = .failure(message)
            return .failure(message)

        } catch PaymentDomainError.limitExceeded {
            let message = "Demo payment limit exceeded"
            state = .failure(message)
            return .failure(message)

        } catch {
            let message = "Unable to complete demo payment"
            state = .failure(message)
            return .failure(message)
        }
    }

    // Section 8
    func reset() {
        guard !state.isBusy else { return }
        state = .idle
    }

    // Lesson 3.4's Discard Draft
    func discardDraft() {
        recipient = ""
        amountText = ""
        reset()
    }
}
