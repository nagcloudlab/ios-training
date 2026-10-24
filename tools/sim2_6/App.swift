import SwiftUI

// Lesson 2.6 evidence app. Each launch argument runs one experiment from the lesson text.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("types") { TypesView() }
            else if args.contains("trace") { TraceView() }
            else if args.contains("order") { OrderView() }
            else if args.contains("frame") { FrameView() }
            else if args.contains("fgbg") { FgBgView() }
            else if args.contains("env") { EnvView() }
            else if args.contains("framepad") { FramePadView() }
            else if args.contains("custom") { CustomView() }
            else if args.contains("final") { ContentView() }
            else { BeforeView() }
        }
    }
}

extension View {
    func logSize(_ label: String) -> some View {
        onGeometryChange(for: CGSize.self) { $0.size } action: { s in
            print("\(label): \(Double(s.width).formatted(.number.precision(.fractionLength(1)))) × \(Double(s.height).formatted(.number.precision(.fractionLength(1)))) pt")
        }
    }
}

func label(_ s: String) -> some View {
    Text(s).font(.caption.monospaced()).foregroundStyle(.secondary)
}

// Section 1: where Lesson 2.5 ended
struct BeforeView: View {
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
            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(.blue)
                VStack(alignment: .leading, spacing: 12) {
                    Text("Available Balance").font(.subheadline)
                    Text("₹25,000").font(.largeTitle.bold())
                    Text("NPay Demo Account").font(.caption)
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(24)
            }
            .frame(height: 180)
            HStack(spacing: 30) {
                VStack(spacing: 8) { Image(systemName: "arrow.up.right"); Text("Send") }
                VStack(spacing: 8) { Image(systemName: "arrow.down.left"); Text("Request") }
                VStack(spacing: 8) { Image(systemName: "clock"); Text("History") }
            }
            .font(.subheadline)
            .foregroundStyle(.blue)
        }
        .padding()
    }
}

// Sections 3, 13, 16, 17, 19: types along a chain
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let card = Text("NPay")
                let padded = card.padding()
                let decorated = padded.background(.blue)
                print("card:", type(of: card))
                print("padded:", type(of: padded))
                print("decorated:", type(of: decorated))
                print("Text.font:", type(of: card.font(.largeTitle)))
                print("Text.foregroundStyle:", type(of: card.foregroundStyle(.blue)))
                print(".modifier(NPayCardStyle()):", type(of: Text("Recent Transactions").modifier(NPayCardStyle())))
                print(".npayCardStyle():", type(of: Text("Recent Transactions").npayCardStyle()))
                print("BalanceCard():", type(of: BalanceCard()))
            }
    }
}

// Section 12: constructing a view value vs evaluating its body
struct TraceView: View {
    var body: some View {
        let _ = print("1. TraceView.body evaluated")
        VStack {
            TracedCard()
        }
        .padding()
    }
}
struct TracedCard: View {
    init() { print("2. TracedCard value constructed") }
    var body: some View {
        let _ = print("3. TracedCard.body evaluated")
        BalanceCard()
    }
}

// Section 5: modifier order
struct OrderView: View {
    var body: some View {
        VStack(spacing: 40) {
            label("padding(24) → background")
            Text("NPay")
                .padding(24)
                .background(.yellow)
                .logSize("padding → background")

            label("background → padding(24)")
            Text("NPay")
                .background(.yellow)
                .padding(24)
                .logSize("background → padding")
        }
        .font(.title)
    }
}

// Sections 6 and 7: frames
struct FrameView: View {
    var body: some View {
        VStack(spacing: 24) {
            label(".frame(width: 200, height: 100)")
            Text("NPay")
                .logSize("the Text inside the 200 × 100 frame")
                .frame(width: 200, height: 100)
                .border(.blue)
                .logSize("the frame")

            label(".frame(maxWidth: .infinity)")
            Text("NPay")
                .frame(maxWidth: .infinity)
                .border(.blue)
                .logSize("maxWidth: .infinity")

            label(".frame(maxWidth: .infinity, alignment: .leading)")
            Text("NPay")
                .frame(maxWidth: .infinity, alignment: .leading)
                .border(.blue)
        }
        .font(.title)
        .padding()
    }
}

// Section 8: foreground vs background
struct FgBgView: View {
    var body: some View {
        HStack(spacing: 40) {
            VStack(spacing: 8) {
                label(".foregroundStyle(.blue)")
                Text("NPay").foregroundStyle(.blue)
            }
            VStack(spacing: 8) {
                label(".background(.blue)")
                Text("NPay").background(.blue)
            }
        }
        .font(.largeTitle)
    }
}

// Sections 9 and 15: environment propagation, override, and a modifier that does not propagate
struct EnvView: View {
    var body: some View {
        VStack(spacing: 30) {
            label("VStack { … }.font(.title)")
            VStack {
                Text("NPay")
                Text("Payments made simple")
            }
            .font(.title)

            label("VStack { … }.padding(): around the stack only")
            VStack {
                Text("NPay").border(.gray)
                Text("Payments made simple").border(.gray)
            }
            .padding()
            .border(.blue)

            label("VStack { … }.foregroundStyle(.white), first Text .yellow")
            VStack {
                Text("Available Balance")
                    .foregroundStyle(.yellow)

                Text("₹25,000")
            }
            .foregroundStyle(.white)
            .padding()
            .background(.blue)
            .font(.title2)
        }
    }
}

// Section 14: frame → padding vs padding → frame
struct FramePadView: View {
    var body: some View {
        VStack(spacing: 20) {
            label("frame → padding(24) → background")
            VStack(alignment: .leading, spacing: 12) {
                Text("Available Balance")
                Text("₹25,000")
                Text("NPay Demo Account")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .padding(24)
            .background(.blue)
            .logSize("frame → padding → background")

            label("padding(24) → frame → background")
            VStack(alignment: .leading, spacing: 12) {
                Text("Available Balance")
                Text("₹25,000")
                Text("NPay Demo Account")
            }
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.blue)
            .logSize("padding → frame → background")

            label("frame → background → padding(24)")
            VStack(alignment: .leading, spacing: 12) {
                Text("Available Balance")
                Text("₹25,000")
                Text("NPay Demo Account")
            }
            .frame(maxWidth: .infinity, alignment: .leading)
            .background(.blue)
            .padding(24)
            .logSize("frame → background → padding")
        }
        .foregroundStyle(.white)
        .padding()
    }
}

// Sections 16 and 17: a custom ViewModifier
struct NPayCardStyle: ViewModifier {

    func body(content: Content) -> some View {
        content
            .padding(20)
            .background(
                Color.blue.opacity(0.08),
                in: RoundedRectangle(cornerRadius: 16)
            )
    }
}

extension View {

    func npayCardStyle() -> some View {
        modifier(NPayCardStyle())
    }
}

struct CustomView: View {
    var body: some View {
        VStack(spacing: 30) {
            label("plain")
            Text("Recent Transactions")
            label(".modifier(NPayCardStyle())")
            Text("Recent Transactions")
                .modifier(NPayCardStyle())
            label(".npayCardStyle()")
            Text("Recent Transactions")
                .npayCardStyle()
        }
        .font(.title3)
    }
}

// Sections 10 and 11: the lesson's final code
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

            HStack(spacing: 30) {
                QuickAction(
                    symbol: "arrow.up.right",
                    title: "Send"
                )

                QuickAction(
                    symbol: "arrow.down.left",
                    title: "Request"
                )

                QuickAction(
                    symbol: "clock",
                    title: "History"
                )
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

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: symbol)
                .font(.title2)

            Text(title)
                .font(.caption)
        }
        .foregroundStyle(.blue)
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(
            Color.blue.opacity(0.08),
            in: RoundedRectangle(cornerRadius: 12)
        )
    }
}
