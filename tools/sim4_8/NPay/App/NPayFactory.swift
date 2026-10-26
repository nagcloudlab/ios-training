import SwiftUI
import NPayDomain

@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        repository: any AccountRepository,
        availableBalance: @escaping @MainActor () -> Int = { .max }
    ) -> PaymentViewModel {

        let policy = PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000
        )

        var repository = repository
        #if DEBUG
        repository = NPayDebug.wrap(repository)   // evidence hook: the lab driver can add latency
        #endif

        let useCase = SendPaymentUseCase(
            repository: repository,
            policy: policy
        )

        return PaymentViewModel(
            sendPayment: useCase,
            availableBalance: availableBalance
        )
    }
}
