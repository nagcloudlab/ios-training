import SwiftUI

struct PaymentsFeatureRoot: View {
    @State private var viewModel: PaymentViewModel
    let dashboard: DashboardViewModel
    let router: NPayRouter

    init(dependencies: NPayDependencies, dashboard: DashboardViewModel, router: NPayRouter) {
        _viewModel = State(
            initialValue: dependencies.makePaymentViewModel(   // Lesson 4.10: the shared repository
                availableBalance: { dashboard.balancePaise }
            )
        )
        self.dashboard = dashboard
        self.router = router
    }

    var body: some View {
        PaymentsScreen(
            viewModel: viewModel,
            router: router,
            onPaymentRecorded: { await dashboard.reload() }   // 4.5, section 18: refresh after success
        )
    }
}
