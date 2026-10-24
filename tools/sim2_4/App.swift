import SwiftUI

// Lesson 2.4 evidence app. Each launch argument runs one experiment from the lesson text.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("types") { TypesView() }
            else if args.contains("spacing") { SpacingView() }
            else if args.contains("widths") { WidthsView() }
            else if args.contains("spacer") { SpacerView() }
            else if args.contains("align") { AlignView() }
            else if args.contains("narrow") { NarrowView() }
            else if args.contains("final") { ContentView().logSize("whole screen content") }
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

// Section 1: where Lesson 2.3 ended
struct BeforeView: View {
    var body: some View {
        VStack(alignment: .center, spacing: 20) {
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

// Sections 2 and 10: types
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let row = HStack(spacing: 20) {
                    Text("Send")
                    Text("Request")
                    Text("History")
                }
                let header = HStack {
                    Text("NPay")
                    Spacer()
                    Image(systemName: "person.circle")
                }
                print("row:", type(of: row))
                print("header:", type(of: header))
                print("row.font(.subheadline):", type(of: row.font(.subheadline)))
            }
    }
}

// Section 3: spacing 0, 20, 40
struct SpacingView: View {
    var body: some View {
        VStack(spacing: 36) {
            ForEach([0, 20, 40], id: \.self) { s in
                VStack(spacing: 6) {
                    Text("spacing: \(s)").font(.caption.monospaced()).foregroundStyle(.secondary)
                    HStack(spacing: CGFloat(s)) {
                        Text("Send").border(.gray)
                        Text("Request").border(.gray)
                        Text("History").border(.gray)
                    }
                    .logSize("spacing \(s), row")
                }
            }
        }
    }
}

// Sections 4 and 5: a 350 pt proposal; plain Text vs equal flexible widths
struct WidthsView: View {
    var body: some View {
        VStack(spacing: 36) {
            VStack(spacing: 6) {
                Text("plain Text").font(.caption.monospaced()).foregroundStyle(.secondary)
                HStack(spacing: 20) {
                    Text("Send").logSize("plain Send").border(.gray)
                    Text("Request").logSize("plain Request").border(.gray)
                    Text("History").logSize("plain History").border(.gray)
                }
                .frame(width: 350)
                .border(.blue)
            }
            VStack(spacing: 6) {
                Text(".frame(maxWidth: .infinity)").font(.caption.monospaced()).foregroundStyle(.secondary)
                HStack(spacing: 20) {
                    Text("Send").frame(maxWidth: .infinity).logSize("flex Send").border(.gray)
                    Text("Request").frame(maxWidth: .infinity).logSize("flex Request").border(.gray)
                    Text("History").frame(maxWidth: .infinity).logSize("flex History").border(.gray)
                }
                .frame(width: 350)
                .border(.blue)
            }
        }
    }
}

// Sections 6 and 7: with and without Spacer
struct SpacerView: View {
    var body: some View {
        VStack(spacing: 36) {
            VStack(spacing: 6) {
                Text("without Spacer").font(.caption.monospaced()).foregroundStyle(.secondary)
                HStack {
                    Text("NPay")
                    Image(systemName: "person.circle")
                }
                .border(.blue)
                .logSize("without Spacer, row")
            }
            VStack(spacing: 6) {
                Text("with Spacer()").font(.caption.monospaced()).foregroundStyle(.secondary)
                HStack {
                    Text("NPay").logSize("with Spacer, title")

                    Spacer()

                    Image(systemName: "person.circle").logSize("with Spacer, icon")
                }
                .border(.blue)
                .logSize("with Spacer, row")
            }
        }
        .font(.title2)
        .padding()
    }
}

// Section 8: top, center, bottom
struct AlignView: View {
    var body: some View {
        VStack(spacing: 32) {
            row(.top, "top")
            row(.center, "center")
            row(.bottom, "bottom")
        }
    }
    func row(_ a: VerticalAlignment, _ name: String) -> some View {
        VStack(spacing: 6) {
            Text(".\(name)").font(.caption.monospaced()).foregroundStyle(.secondary)
            HStack(alignment: a, spacing: 20) {
                Text("Send")
                    .font(.largeTitle)
                    .border(.gray)
                Text("Request")
                    .font(.caption)
                    .border(.gray)
            }
            .border(.blue)
        }
    }
}

// Section 9: too narrow, with and without layoutPriority
struct NarrowView: View {
    var body: some View {
        VStack(spacing: 36) {
            VStack(spacing: 6) {
                Text("no priority").font(.caption.monospaced()).foregroundStyle(.secondary)
                HStack {
                    Text("Available Balance").logSize("no priority, label")
                    Text("₹25,000").logSize("no priority, amount")
                }
                .frame(width: 200)
                .border(.blue)
            }
            VStack(spacing: 6) {
                Text(".layoutPriority(1) on the label").font(.caption.monospaced()).foregroundStyle(.secondary)
                HStack {
                    Text("Available Balance")
                        .layoutPriority(1)
                        .logSize("priority, label")

                    Text("₹25,000").logSize("priority, amount")
                }
                .frame(width: 200)
                .border(.blue)
            }
        }
        .font(.title3)
    }
}

// Section 10: the lesson's final code
struct ContentView: View {

    var body: some View {
        VStack(spacing: 24) {

            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)

            Text("NPay")
                .font(.largeTitle.bold())
                .foregroundStyle(.blue)

            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            HStack(spacing: 24) {
                VStack(spacing: 8) {
                    Image(systemName: "arrow.up.right")
                    Text("Send")
                }

                VStack(spacing: 8) {
                    Image(systemName: "arrow.down.left")
                    Text("Request")
                }

                VStack(spacing: 8) {
                    Image(systemName: "clock")
                    Text("History")
                }
            }
            .font(.subheadline)
            .foregroundStyle(.blue)
        }
        .padding()
    }
}
