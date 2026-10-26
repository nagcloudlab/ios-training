import SwiftUI

struct PaymentsScreen: View {
    @Bindable var viewModel: PaymentViewModel
    let router: NPayRouter
    let onPaymentRecorded: @MainActor () async -> Void

    @State private var review: ValidatedPaymentRequest?
    @State private var pendingSuccessID: UUID?
    @State private var confirmDiscard = false

    @FocusState private var focusedField: Field?

    enum Field: Hashable {
        case recipient
        case amount
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {

                Text(
                    "Available: \(Money.display(viewModel.availableBalancePaise))"
                )
                .foregroundStyle(.secondary)

                TextField(
                    "Recipient ID",
                    text: $viewModel.recipient
                )
                .textInputAutocapitalization(.never)
                .autocorrectionDisabled()
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .recipient
                )
                .accessibilityIdentifier(NPayAccessibilityID.recipientField)
                .accessibilityLabel("Recipient")
                .submitLabel(.next)
                .onSubmit {
                    focusedField = .amount
                }

                TextField(
                    "Amount (₹)",
                    text: $viewModel.amountText
                )
                .keyboardType(.decimalPad)
                .textFieldStyle(.roundedBorder)
                .focused(
                    $focusedField,
                    equals: .amount
                )
                .accessibilityIdentifier(NPayAccessibilityID.amountField)
                .accessibilityLabel("Amount in rupees")

                if !viewModel.amountText.isEmpty
                            && !viewModel.validate(availableBalancePaise: viewModel.availableBalancePaise) {
                    Text("Enter a valid amount within your balance.")
                        .font(.caption)
                        .foregroundStyle(.red)
                }

                NPayButton("Review Payment", symbol: "doc.text.magnifyingglass") {
                    focusedField = nil
                    viewModel.reset()   // a new review starts from idle
                    review = viewModel.prepareCommand()
                }
                .disabled(!viewModel.validate(availableBalancePaise: viewModel.availableBalancePaise))
                .accessibilityIdentifier(NPayAccessibilityID.sendButton)

                Button("Discard Draft", role: .destructive) {
                    confirmDiscard = true
                }
                .disabled(viewModel.recipient.isEmpty && viewModel.amountText.isEmpty)
            }
            .padding()
        }
        .navigationTitle("Payments")
        .toolbar {
            ToolbarItemGroup(placement: .keyboard) {
                Spacer()

                Button("Done") {
                    focusedField = nil
                }
            }
        }
        .sheet(
            item: $review,
            onDismiss: {
                // Section 22: the ViewModel returned an ID; the view asks the router to navigate
                if let id = pendingSuccessID {
                    pendingSuccessID = nil
                    router.showPaymentSuccess(id)
                }
            }
        ) { request in

            PaymentReviewSheet(request: request, viewModel: viewModel) {
                // Lesson 4.7, section 21: act on this submission's own result
                Task {
                    let result = await viewModel.submit(request.command)

                    switch result {
                    case .success(let record):
                        pendingSuccessID = record.id
                        self.review = nil
                        await onPaymentRecorded()

                    case .failure:
                        // Keep the review sheet visible; it shows the ViewModel's failure state.
                        break

                    case .statusUnknown:
                        // A status-check workflow would go here; never claim success or failure.
                        break
                    }
                }
            }
        }
        .alert("Discard payment draft?", isPresented: $confirmDiscard) {
            Button("Discard", role: .destructive) {
                viewModel.discardDraft()
            }

            Button("Cancel", role: .cancel) {}
        }
    }
}
