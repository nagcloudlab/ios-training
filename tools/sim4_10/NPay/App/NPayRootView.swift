import SwiftUI

struct NPayRootView: View {

    @State private var router = NPayRouter()
    @State private var preferences = NPayPreferences()
    @State private var dependencies: NPayDependencies   // Lesson 4.10: the composition root
    @State private var dashboard: DashboardViewModel

    init() {
        let dependencies = NPayDependencies()
        _dependencies = State(initialValue: dependencies)
        _dashboard = State(initialValue: dependencies.makeDashboardViewModel())
    }

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {

            NavigationStack(path: $router.homePath) {
                HomeScreen(dashboard: dashboard, router: router)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsFeatureRoot(
                    dependencies: dependencies,
                    dashboard: dashboard,
                    router: router
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Payments", systemImage: "arrow.up.right")
            }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen(
                    transactions: dashboard.displayTransactions
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
        .environment(preferences)
        .preferredColorScheme(
            preferences.appearance.colorScheme
        )
        .task {
            await dashboard.reload()   // the first snapshot
        }
        #if DEBUG
        .onAppear { NPayDebug.attach(router, dependencies, dashboard, preferences) }   // evidence hook; not part of NPay
        #endif
    }

    // One mapping from route to screen, registered in every tab's stack
    @ViewBuilder
    private func destination(_ route: NPayRoute) -> some View {
        switch route {
        case .accountDetails:
            AccountDetailsScreen(balancePaise: dashboard.balancePaise)

        case .paymentSuccess(let id):
            PaymentSuccessScreen(
                transactionID: id,
                onDone: { router.returnHome() }
            )

        case .transactionDetails(let id):
            if let transaction = dashboard.displayTransactions.first(where: { $0.id == id }) {
                TransactionDetailScreen(transaction: transaction)
            } else {
                ContentUnavailableView(
                    "Transaction not found",
                    systemImage: "questionmark.circle"
                )
            }

        case .settings:
            SettingsScreen()

        case .appearance:
            AppearanceSettingsView()
        }
    }
}
