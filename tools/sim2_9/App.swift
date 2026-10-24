import SwiftUI
import UIKit

// Lesson 2.9 evidence app. Each launch argument runs one experiment from the lesson text.
// Buttons are activated through their accessibility elements (the path VoiceOver uses); run.sh turns simulator
// accessibility on so SwiftUI exposes them.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("types") { TypesDemo() }
            else if args.contains("flow") { ContentView().task { await activate(["+ ₹1,000", "+ ₹1,000", "− ₹1,000"]) } }
            else if args.contains("taps") { ContentView().task { await activate(["+ ₹1,000", "+ ₹1,000", "− ₹1,000"]) } }
            else if args.contains("twosources") { TwoSources().task { await activate(["Add ₹1,000"]) } }
            else if args.contains("clamp") { ClampDemo().task { await activate(["− ₹1,000", "− ₹1,000"]) } }
            else if args.contains("safe") { SafeDemo().task { await activate(["− ₹1,000 (no clamp)", "− ₹1,000 (no clamp)"]) } }
            else if args.contains("manual") { ManualDemo().task { await activate(["+ ₹1,000"]) } }
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

// Where Lesson 2.8 ended
struct BeforeView: View {
    @State private var balance = 25000
    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "creditcard.fill").font(.system(size: 48)).foregroundStyle(.blue)
            Text("NPay").font(.largeTitle.bold()).foregroundStyle(.blue)
            Text("Payments made simple").font(.subheadline).foregroundStyle(.secondary)
            BalanceCard(balance: balance)
            Button("Add Demo ₹1,000") { balance += 1000 }.buttonStyle(.borderedProminent)
            HStack(spacing: 12) {
                QuickAction(symbol: "arrow.up.right", title: "Send") { }
                QuickAction(symbol: "arrow.down.left", title: "Request") { }
                QuickAction(symbol: "clock", title: "History") { }
            }
        }
        .padding()
    }
}

// Sections 4, 11 and 13: types
struct TypesDemo: View {
    @State private var balance = 25000
    var body: some View {
        TypesChild(balance: $balance)
            .task {
                print("parent  balance:", type(of: balance))
                print("parent  $balance:", type(of: $balance))
                let manual = Binding(get: { balance }, set: { balance = $0 })
                print("Binding(get:set:):", type(of: manual))
            }
    }
}
struct TypesChild: View {
    @Binding var balance: Int
    var body: some View {
        Text("Types printed to the console")
            .task {
                print("child   balance:", type(of: balance))
                print("child   _balance:", type(of: _balance))
            }
    }
}

// Section 7: two sources of truth
struct TwoSources: View {
    @State private var balance = 25000
    var body: some View {
        VStack(spacing: 24) {
            Text("Parent: ₹\(balance)").font(.title2)
            WrongEditor()
        }
        .padding()
    }
}
struct WrongEditor: View {
    @State private var balance = 25000

    var body: some View {
        VStack(spacing: 12) {
            Text("Child: ₹\(balance)").font(.title2)
            Button("Add ₹1,000") {
                balance += 1000
                print("child balance now \(balance)")
            }
            .buttonStyle(.borderedProminent)
        }
    }
}

// Section 8: max(0, …) in the editor
struct ClampDemo: View {
    @State private var balance = 500
    var body: some View {
        VStack {
            Text("₹\(balance)")
            BalanceEditor(balance: $balance)
        }
        .onChange(of: balance) { _, new in print("balance now \(new)") }
    }
}

// Section 14: validation in a custom binding; the child does not clamp
struct SafeDemo: View {
    @State private var balance = 500

    private var safeBalance: Binding<Int> {
        Binding(
            get: {
                balance
            },
            set: { newValue in
                print("safeBalance set: asked \(newValue), storing \(max(0, newValue))")
                balance = max(0, newValue)
            }
        )
    }

    var body: some View {
        VStack {
            Text("₹\(balance)")
            NaiveEditor(balance: safeBalance)
        }
    }
}
struct NaiveEditor: View {
    @Binding var balance: Int
    var body: some View {
        Button("− ₹1,000 (no clamp)") { balance -= 1000 }
    }
}

// Section 11: a binding built by hand
struct ManualDemo: View {
    @State private var balance = 25000
    var body: some View {
        VStack {
            BalanceCard(balance: balance)
            BalanceEditor(
                balance: Binding(
                    get: {
                        balance
                    },
                    set: { newValue in
                        print("manual binding set \(newValue)")
                        balance = newValue
                    }
                )
            )
        }
        .padding()
    }
}

// Section 10: the complete code (prints added to BalanceCard and BalanceEditor bodies)
struct ContentView: View {
    @State private var balance = 25000

    var body: some View {
        ScrollView {
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

                BalanceEditor(balance: $balance)

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

struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        let _ = print("BalanceEditor body: \(balance)")
        VStack(spacing: 12) {
            Text("Demo Balance Editor")
                .font(.headline)

            HStack(spacing: 12) {
                Button("− ₹1,000") {
                    balance = max(0, balance - 1000)
                }
                .buttonStyle(.bordered)

                Button("+ ₹1,000") {
                    balance += 1000
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
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
