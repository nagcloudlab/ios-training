import SwiftUI

struct PaymentsFeatureRoot: View {
    @State private var viewModel: PaymentViewModel
    let router: NPayRouter

    init(store: NPayStore, router: NPayRouter) {
        _viewModel = State(
            initialValue: NPayFactory.makePaymentViewModel(   // Lesson 4.6
                repository: NPayStoreAccountRepository(store: store),
                availableBalance: { store.balancePaise }
            )
        )
        self.router = router
    }

    var body: some View {
        PaymentsScreen(viewModel: viewModel, router: router)
    }
}
