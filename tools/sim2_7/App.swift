import SwiftUI
import UIKit

// Lesson 2.7 evidence app. Each launch argument runs one experiment from the lesson text.
// Buttons are activated through their accessibility elements (the path VoiceOver uses), which runs the real
// Button action; run.sh turns simulator accessibility on so SwiftUI exposes those elements.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("types") { TypesView() }
            else if args.contains("body") { BodyParent() }
            else if args.contains("activate") { ContentView().task { await activate(["Send", "Request", "History"]) } }
            else if args.contains("stack") { StackView().task { await activate(["Send"]) } }
            else if args.contains("disabled") { DisabledView().task { await activate(["Send Money", "Request Money"]) } }
            else if args.contains("blocking") { BlockingView() }
            else if args.contains("styles") { StylesView() }
            else if args.contains("final") { ContentView() }
            else { BeforeView() }
        }
    }
}

// Find SwiftUI's accessibility elements and activate the ones with these labels, in order.
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
    var seen = Set<String>()
    return found.filter { seen.insert($0.accessibilityLabel ?? "").inserted }
}

@MainActor func activate(_ labels: [String]) async {
    try? await Task.sleep(for: .seconds(1.5))
    for label in labels {
        guard let e = elements().first(where: { $0.accessibilityLabel == label }) else { print("no element \(label)"); continue }
        let enabled = !e.accessibilityTraits.contains(.notEnabled)
        let f = e.accessibilityFrame
        print("activating \"\(label)\" (button: \(e.accessibilityTraits.contains(.button)), enabled: \(enabled), frame \(Int(f.width)) × \(Int(f.height)) pt)")
        _ = e.accessibilityActivate()
        try? await Task.sleep(for: .milliseconds(300))
    }
}

// Where Lesson 2.6 ended
struct BeforeView: View {
    var body: some View {
        VStack(spacing: 28) {
            Image(systemName: "creditcard.fill").font(.system(size: 48)).foregroundStyle(.blue)
            Text("NPay").font(.largeTitle.bold()).foregroundStyle(.blue)
            Text("Payments made simple").font(.subheadline).foregroundStyle(.secondary)
            BalanceCard()
            HStack(spacing: 30) {
                StaticAction(symbol: "arrow.up.right", title: "Send")
                StaticAction(symbol: "arrow.down.left", title: "Request")
                StaticAction(symbol: "clock", title: "History")
            }
        }
        .padding()
    }
}
struct StaticAction: View {
    let symbol: String
    let title: String
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: symbol).font(.title2)
            Text(title).font(.caption)
        }
        .foregroundStyle(.blue)
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color.blue.opacity(0.08), in: RoundedRectangle(cornerRadius: 12))
    }
}

// Sections 2 and 7: types
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let simple = Button("Send Money") {
                    print("Send Money tapped")
                }
                let custom = Button {
                    print("Send tapped")
                } label: {
                    VStack(spacing: 8) {
                        Image(systemName: "arrow.up.right")
                        Text("Send")
                    }
                }
                let action = QuickAction(symbol: "arrow.up.right", title: "Send") { print("Send tapped") }
                print("Button(\"Send Money\") { … }:", type(of: simple))
                print("Button { … } label: { VStack … }:", type(of: custom))
                print("QuickAction.action:", type(of: action.action))
            }
    }
}

// Section 3: body evaluation does not run the action
struct BodyParent: View {
    @State private var tick = 0
    var body: some View {
        PaymentView(tick: tick)
            .task {
                for _ in 0..<3 {
                    try? await Task.sleep(for: .milliseconds(400))
                    tick += 1
                }
                print("done: parent changed 3 times, no tap")
            }
    }
}
struct PaymentView: View {
    let tick: Int
    var body: some View {
        let _ = print("PaymentView.body evaluated (tick \(tick))")
        Button("Send Money") {
            print("Payment requested")
        }
    }
}

// Sections 4 and 17: where the action runs
struct StackView: View {
    var body: some View {
        QuickAction(symbol: "arrow.up.right", title: "Send") {
            print("Send tapped")
            print("main thread: \(Thread.isMainThread)")
            for s in Thread.callStackSymbols.prefix(14) { print("FRAME " + s) }
        }
        .padding()
    }
}

// Section 9: disabled
struct DisabledView: View {
    var body: some View {
        VStack(spacing: 24) {
            Button("Send Money") {
                print("Send requested")
            }
            .disabled(true)

            Button("Request Money") {
                print("Request requested")
            }
        }
        .buttonStyle(.borderedProminent)
    }
}

// Section 18: a blocking action stops the main thread
struct BlockingView: View {
    var body: some View {
        Button("Send") {
            Thread.sleep(forTimeInterval: 3)
            print("Finished")
        }
        .task {
            let clock = ContinuousClock()
            let start = clock.now
            Timer.scheduledTimer(withTimeInterval: 0.5, repeats: true) { _ in
                let t = start.duration(to: clock.now)
                print("main-thread timer fired at \(t.formatted(.units(allowed: [.seconds], fractionalPart: .show(length: 1))))")
            }
            await activate(["Send"])
            try? await Task.sleep(for: .seconds(2))
        }
    }
}

// Section 8: styles
struct StylesView: View {
    var body: some View {
        VStack(spacing: 28) {
            ForEach(["plain", "bordered", "borderedProminent"], id: \.self) { name in
                VStack(spacing: 8) {
                    Text(".\(name)").font(.caption.monospaced()).foregroundStyle(.secondary)
                    styled(name)
                }
            }
            VStack(spacing: 8) {
                Text(".borderedProminent + .disabled(true)").font(.caption.monospaced()).foregroundStyle(.secondary)
                Button("Send Money") { }.buttonStyle(.borderedProminent).disabled(true)
            }
        }
    }
    @ViewBuilder func styled(_ name: String) -> some View {
        let b = Button("Send Money") { print("Tapped") }
        switch name {
        case "plain": b.buttonStyle(.plain)
        case "bordered": b.buttonStyle(.bordered)
        default: b.buttonStyle(.borderedProminent)
        }
    }
}

// Section 14: the lesson's complete code
struct ContentView: View {

    var body: some View {
        VStack(spacing: 28) {

            Image(systemName: "creditcard.fill")
                .font(.system(size: 48))
                .foregroundStyle(.blue)

            Text("NPay")
                .font(.largeTitle.bold())
                .foregroundStyle(.blue)

            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            BalanceCard()

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

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Available Balance")
                .font(.subheadline)

            Text("₹25,000")
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
