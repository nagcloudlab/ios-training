import SwiftUI
import UIKit

// Lesson 2.8 evidence app. Each launch argument runs one experiment from the lesson text.
// Buttons are activated through their accessibility elements (the path VoiceOver uses); run.sh turns simulator
// accessibility on so SwiftUI exposes them.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("counter") { CounterDemo().task { await activate(["Add Demo ₹1,000", "Add Demo ₹1,000", "Add Demo ₹1,000"]) } }
            else if args.contains("changes") { ChangesDemo().task { await activate(["Add Money", "Add Money"]) } }
            else if args.contains("survive") { SurviveParent() }
            else if args.contains("identity") { IdentityExperiment().task { await activate(["Increment", "Increment", "Increment", "Replace Identity"]) } }
            else if args.contains("identity3") { IdentityExperiment().task { await activate(["Increment", "Increment", "Increment"]) } }
            else if args.contains("types") { TypesDemo() }
            else if args.contains("taps") { ContentView().task { await activate(["Add Demo ₹1,000", "Add Demo ₹1,000", "Add Demo ₹1,000", "Send"]) } }
            else if args.contains("final") { ContentView() }
            else { BeforeView() }
        }
    }
}

@MainActor func elements() -> [NSObject] {
    guard let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
          let window = scene.windows.first else { return [] }
    var found: [NSObject] = []
    func walk(_ o: NSObject, _ depth: Int) {
        guard depth < 30 else { return }
        if let els = o.accessibilityElements as? [NSObject] { for e in els { found.append(e); walk(e, depth + 1) } }
        if let v = o as? UIView { for s in v.subviews { walk(s, depth + 1) } }
    }
    walk(window, 0)
    return found
}

@MainActor func activate(_ labels: [String]) async {
    try? await Task.sleep(for: .seconds(1.5))
    for label in labels {
        guard let e = elements().first(where: { $0.accessibilityLabel == label }) else { print("no element \(label)"); continue }
        print("[activate \"\(label)\"]")
        _ = e.accessibilityActivate()
        try? await Task.sleep(for: .milliseconds(400))
    }
}

// Where Lesson 2.7 ended
struct BeforeView: View {
    var body: some View {
        VStack(spacing: 28) {
            Image(systemName: "creditcard.fill").font(.system(size: 48)).foregroundStyle(.blue)
            Text("NPay").font(.largeTitle.bold()).foregroundStyle(.blue)
            Text("Payments made simple").font(.subheadline).foregroundStyle(.secondary)
            VStack(alignment: .leading, spacing: 12) {
                Text("Available Balance").font(.subheadline)
                Text("₹25,000").font(.largeTitle.bold())
                Text("NPay Demo Account").font(.caption)
            }
            .foregroundStyle(.white)
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(24)
            .background(.blue, in: RoundedRectangle(cornerRadius: 20))
            HStack(spacing: 12) {
                QuickAction(symbol: "arrow.up.right", title: "Send") { }
                QuickAction(symbol: "arrow.down.left", title: "Request") { }
                QuickAction(symbol: "clock", title: "History") { }
            }
        }
        .padding()
    }
}

// Section 3: the first @State counter
struct CounterDemo: View {
    @State private var balance = 25000

    var body: some View {
        let _ = print("body: balance = \(balance)")
        VStack(spacing: 20) {
            Text("Balance: ₹\(balance)")
                .font(.title)

            Button("Add Demo ₹1,000") {
                balance += 1000
            }
            .buttonStyle(.borderedProminent)
        }
    }
}

// Section 9: _printChanges
struct ChangesDemo: View {
    @State private var balance = 25000

    var body: some View {
        let _ = Self._printChanges()

        return VStack(spacing: 20) {
            Text("₹\(balance)")

            Button("Add Money") {
                balance += 1000
            }
        }
    }
}

// Sections 6 and 13: the view value is recreated, the state survives
struct SurviveParent: View {
    @State private var tick = 0
    var body: some View {
        Survivor(tick: tick)
            .task {
                await activate(["Add", "Add", "Add"])
                for _ in 0..<2 {
                    tick += 1
                    try? await Task.sleep(for: .milliseconds(300))
                }
            }
    }
}
struct Survivor: View {
    let tick: Int
    @State private var balance = 25000
    init(tick: Int) {
        self.tick = tick
        print("Survivor value created (tick \(tick))")
    }
    var body: some View {
        let _ = print("body: tick \(tick), balance = \(balance)")
        Button("Add") { balance += 1000 }
    }
}

// Section 14: identity resets state
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        let _ = print("CounterView body: count = \(count)")
        VStack(spacing: 16) {
            Text("Count: \(count)")

            Button("Increment") {
                count += 1
            }
        }
    }
}

struct IdentityExperiment: View {
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            CounterView()
                .id(identity)

            Button("Replace Identity") {
                identity = UUID()
            }
        }
        .font(.title2)
    }
}

// Sections 4 and 15: the wrapper and the projected value
struct TypesDemo: View {
    @State private var balance = 25000
    var body: some View {
        Text("Types printed to the console")
            .task {
                print("balance:", type(of: balance))
                print("_balance:", type(of: _balance))
                print("$balance:", type(of: $balance))
                print("formatted:", balance.formatted(.currency(code: "INR").precision(.fractionLength(0))))
            }
    }
}

// Section 12: the complete code
struct ContentView: View {
    @State private var balance = 25000

    var body: some View {
        VStack(spacing: 24) {

            Image(systemName: "creditcard.fill")
                .font(.system(size: 48))
                .foregroundStyle(.blue)

            Text("NPay")
                .font(.largeTitle.bold())
                .foregroundStyle(.blue)

            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            BalanceCard(balance: balance)

            Button("Add Demo ₹1,000") {
                balance += 1000
            }
            .buttonStyle(.borderedProminent)

            HStack(spacing: 12) {
                QuickAction(
                    symbol: "arrow.up.right",
                    title: "Send"
                ) {
                    print("Send tapped")
                }

                QuickAction(
                    symbol: "arrow.down.left",
                    title: "Request"
                ) {
                    print("Request tapped")
                }

                QuickAction(
                    symbol: "clock",
                    title: "History"
                ) {
                    print("History tapped")
                }
            }
        }
        .padding()
    }
}

struct BalanceCard: View {
    let balance: Int

    var body: some View {
        let _ = print("BalanceCard body: \(balance)")
        VStack(alignment: .leading, spacing: 12) {
            Text("Available Balance")
                .font(.subheadline)

            Text(
                balance,
                format: .currency(code: "INR")
                    .precision(.fractionLength(0))
            )
            .font(.largeTitle.bold())

            Text("NPay Demo Account")
                .font(.caption)
        }
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(24)
        .background(
            .blue,
            in: RoundedRectangle(cornerRadius: 20)
        )
    }
}

struct QuickAction: View {
    let symbol: String
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: symbol)
                    .font(.title2)

                Text(title)
                    .font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(.blue)
        .background(
            Color.blue.opacity(0.08),
            in: RoundedRectangle(cornerRadius: 12)
        )
    }
}
