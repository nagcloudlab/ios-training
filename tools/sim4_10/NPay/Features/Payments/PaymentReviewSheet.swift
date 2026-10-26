import SwiftUI

struct PaymentReviewSheet: View {
    let request: ValidatedPaymentRequest
    let viewModel: PaymentViewModel
    let onConfirm: () -> Void

    @Environment(\.dismiss) private var dismiss

    // Lesson 4.7, sections 11 and 17: render the submission state
    @ViewBuilder
    private var statusContent: some View {
        switch viewModel.state {

        case .idle:
            EmptyView()

        case .validating:
            Text("Validating payment...")

        case .submitting:
            ProgressView("Processing demo payment...")

        case .success:
            Label(
                "Payment recorded",
                systemImage: "checkmark.circle.fill"
            )
            .foregroundStyle(.green)

        case .failure(let message):
            Text(message)
                .foregroundStyle(.red)

        case .statusUnknown:
            ContentUnavailableView {
                Label(
                    "Payment status unavailable",
                    systemImage: "questionmark.circle"
                )
            } description: {
                Text(
                    "Check transaction status before retrying."
                )
            }
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())

            LabeledContent(
                "Recipient",
                value: request.command.recipient.identifier
            )

            LabeledContent(
                "Amount",
                value: Money.display(request.command.amount.paise)
            )

            statusContent

            NPayButton("Confirm Demo Payment") {
                onConfirm()
            }
            .disabled(viewModel.state.isBusy)

            Button("Edit Details") {
                dismiss()
            }
            .buttonStyle(.bordered)
            .disabled(viewModel.state.isBusy)   // Lesson 4.7 (ours): the sheet stays while busy (section 12)
        }
        .padding()
        .presentationDetents([.medium, .large])
        .interactiveDismissDisabled(
            viewModel.state.isBusy
        )
    }
}
