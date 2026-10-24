import SwiftUI

// Lesson 2.3 evidence app. Each launch argument runs one experiment from the lesson text.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("types") { TypesView() }
            else if args.contains("borders20") { BordersView(spacing: 20) }
            else if args.contains("borders50") { BordersView(spacing: 50) }
            else if args.contains("padA") { PaddingA() }
            else if args.contains("padB") { PaddingB() }
            else if args.contains("align") { AlignView() }
            else if args.contains("hug") { HugView(fill: false) }
            else if args.contains("fill") { HugView(fill: true) }
            else if args.contains("calc") { CalcView() }
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

// Section 1: where Lesson 2.2 ended
struct BeforeView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)
            Text("NPay")
                .font(.largeTitle)
                .bold()
                .foregroundStyle(.blue)
        }
    }
}

// Sections 7 and 13: the generic types the builder produces
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let one = VStack {
                    Text("NPay")
                }
                let two = VStack {
                    Text("NPay")
                    Image(systemName: "creditcard.fill")
                }
                let stack = VStack(spacing: 20) {
                    Text("NPay")
                    Text("Payments made simple")
                }
                let nested = VStack {
                    VStack {
                        Text("NPay")
                    }
                }
                print("one child:", type(of: one))
                print("two children:", type(of: two))
                print("section 13:", type(of: stack))
                print("nested:", type(of: nested))
                print("ContentView.body:", type(of: ContentView().body))
            }
    }
}

// Sections 8 and 18: borders show the layout rectangles
struct BordersView: View {
    let spacing: CGFloat
    var body: some View {
        VStack(spacing: spacing) {
            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .border(.red)

            Text("NPay")
                .font(.largeTitle)
                .border(.green)

            Text("Payments made simple")
                .border(.orange)
        }
        .border(.blue)
        .padding()
        .logSize("spacing \(Int(spacing)), stack with padding")
    }
}

// Sections 9 and 19: padding on the stack vs on each child
struct PaddingA: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("NPay")
            Text("Payments made simple")
        }
        .padding(30)
        .background(.yellow)
        .logSize("A: padding on the stack")
    }
}
struct PaddingB: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("NPay")
                .padding(30)

            Text("Payments made simple")
                .padding(30)
        }
        .background(.yellow)
        .logSize("B: padding on each child")
    }
}

// Section 10: the three horizontal alignments
struct AlignView: View {
    var body: some View {
        VStack(spacing: 36) {
            stack(.leading, "leading")
            stack(.center, "center")
            stack(.trailing, "trailing")
        }
    }
    func stack(_ alignment: HorizontalAlignment, _ name: String) -> some View {
        VStack(spacing: 6) {
            Text(".\(name)").font(.caption.monospaced()).foregroundStyle(.secondary)
            VStack(alignment: alignment, spacing: 8) {
                Text("NPay").bold()
                Text("Payments made simple")
                Text("Fast and secure")
            }
            .border(.gray)
        }
    }
}

// Section 11: a stack hugs its content unless a frame lets it grow
struct HugView: View {
    let fill: Bool
    var body: some View {
        if fill {
            VStack {
                Text("NPay")
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .border(.blue)
            .logSize("with .frame(maxWidth: .infinity, maxHeight: .infinity)")
        } else {
            VStack {
                Text("NPay")
            }
            .border(.blue)
            .logSize("VStack { Text(\"NPay\") }")
        }
    }
}

// Sections 16 and 17: the stack's height from its children
struct CalcView: View {
    var body: some View {
        VStack(spacing: 20) {
            Text("NPay")
                .font(.largeTitle)
                .logSize("title")

            Text("Payments made simple")
                .font(.subheadline)
                .logSize("subtitle")
        }
        .logSize("stack")
        .border(.blue)
    }
}

// Sections 12 and 20: the lesson's final code
struct ContentView: View {

    var body: some View {
        VStack(
            alignment: .center,
            spacing: 20
        ) {
            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)

            Text("NPay")
                .font(.largeTitle)
                .bold()
                .foregroundStyle(.blue)

            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}
