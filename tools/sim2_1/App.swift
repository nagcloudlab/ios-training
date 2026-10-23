import SwiftUI

@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("body") { BodyScenario() }
            else if args.contains("changes") { ChangesScenario() }
            else if args.contains("identity") { IdentityScenario() }
            else if args.contains("uuid") { UUIDScenario(stable: false) }
            else if args.contains("stableid") { UUIDScenario(stable: true) }
            else if args.contains("tapped") { DashboardView(autoTap: true) }
            else { DashboardView(autoTap: false) }
        }
    }
}

// 12: body evaluation; a child that depends on nothing
struct BodyScenario: View {
    @State private var balanceMinor: Int64 = 2_500_000
    var body: some View {
        let _ = print("DashboardView body evaluated, balance \(balanceMinor / 100)")
        VStack {
            HeaderView()
            Text("₹\(balanceMinor / 100)")
        }
        .task {
            for _ in 0..<2 {
                try? await Task.sleep(for: .milliseconds(400))
                balanceMinor += 100_000
            }
        }
    }
}
struct HeaderView: View {
    var body: some View {
        let _ = print("HeaderView body evaluated")
        Text("NPay").font(.largeTitle)
    }
}

// 24: _printChanges
struct ChangesScenario: View {
    @State private var count = 0
    var body: some View {
        let _ = Self._printChanges()
        Text("Count: \(count)")
            .task { for _ in 0..<2 { try? await Task.sleep(for: .milliseconds(400)); count += 1 } }
    }
}

// 14: structural identity
struct IdentityScenario: View {
    @State private var showPremium = false
    var body: some View {
        VStack {
            if showPremium { CounterView(name: "Premium") } else { CounterView(name: "Standard") }
        }
        .task {
            try? await Task.sleep(for: .milliseconds(1500)); showPremium = true
            try? await Task.sleep(for: .milliseconds(1500)); showPremium = false
        }
    }
}
struct CounterView: View {
    let name: String
    @State private var count = 0
    var body: some View {
        Text("\(name): \(count)")
            .onAppear { print("\(name)CounterView appeared, count = \(count)") }
            .task { for _ in 0..<3 { try? await Task.sleep(for: .milliseconds(200)); count += 1 }; print("\(name) counted to \(count)") }
    }
}

// 25: .id(UUID()) vs stable id
@MainActor enum Made { static var cards = 0 }
struct UUIDScenario: View {
    let stable: Bool
    @State private var tick = 0
    var body: some View {
        VStack {
            if stable { BalanceCard().id("NP1001") } else { BalanceCard().id(UUID()) }
            Text("tick \(tick)")
        }
        .task { for _ in 0..<3 { try? await Task.sleep(for: .milliseconds(400)); tick += 1 } }
    }
}
struct BalanceCard: View {
    @State private var instance = 0
    var body: some View {
        Text("card")
            .onAppear { Made.cards += 1; instance = Made.cards; print("BalanceCard appeared: fresh state #\(instance)") }
    }
}

// 22: the dashboard
struct DashboardView: View {
    let autoTap: Bool
    @State private var balanceMinor: Int64 = 2_500_000     // paise
    @State private var showMessage = false

    var body: some View {
        VStack(spacing: 24) {
            Text("NPay").font(.largeTitle.bold())
            Text("Available Balance").foregroundStyle(.secondary)
            Text(Decimal(balanceMinor) / 100,
                 format: .currency(code: "INR").precision(.fractionLength(0)))
                .font(.system(size: 38, weight: .bold))
            Button("Add Demo ₹1,000") {
                balanceMinor += 100_000
                showMessage = true
            }
            .buttonStyle(.borderedProminent)
            if showMessage {
                Text("Demo balance updated").foregroundStyle(.green)
            }
            Spacer()
        }
        .padding()
        .task { if autoTap { balanceMinor += 100_000; showMessage = true } }
    }
}
