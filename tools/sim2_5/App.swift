import SwiftUI

// Lesson 2.5 evidence app. Each launch argument runs one experiment from the lesson text.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("types") { TypesView() }
            else if args.contains("basic") { BasicView() }
            else if args.contains("order") { OrderView() }
            else if args.contains("size") { SizeView() }
            else if args.contains("align") { AlignView() }
            else if args.contains("layering") { LayeringView() }
            else if args.contains("steps") { StepsView() }
            else if args.contains("compare") { CompareView() }
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

// Section 1: where Lesson 2.4 ended
struct BeforeView: View {
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

// Sections 2 and 3: printed types
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let two = ZStack {
                    Color.blue
                    Text("NPay")
                        .foregroundStyle(.white)
                }
                let three = ZStack {
                    Color.blue
                    Color.green
                    Text("NPay")
                }
                print("section 2:", type(of: two))
                print("section 3:", type(of: three))
            }
    }
}

// Section 2: a colour layer under a text layer
struct BasicView: View {
    var body: some View {
        ZStack {
            Color.blue

            Text("NPay")
                .foregroundStyle(.white)
        }
        .frame(width: 240, height: 140)
        .logSize("ZStack")
    }
}

// Sections 3, 4 and 11A: source order and zIndex
struct OrderView: View {
    var body: some View {
        VStack(spacing: 14) {
            label("Blue, Green, Text")
            ZStack {
                Color.blue
                Color.green
                Text("NPay")
            }
            .frame(width: 240, height: 140)

            label("Text, Blue, Green")
            ZStack {
                Text("NPay")
                Color.blue
                Color.green
            }
            .frame(width: 240, height: 140)

            label("Text.zIndex(1), Blue, Green")
            ZStack {
                Text("NPay")
                    .logSize("Text with zIndex(1)")
                    .zIndex(1)
                Color.blue
                Color.green
            }
            .frame(width: 240, height: 140)
        }
        .font(.title)
    }
}

// Section 5: ZStack overlaps; VStack adds
struct SizeView: View {
    var body: some View {
        VStack(spacing: 28) {
            label("ZStack")
            ZStack {
                Rectangle().fill(.blue).frame(width: 300, height: 180)
                Text("NPay").foregroundStyle(.white)
            }
            .border(.red)
            .logSize("ZStack { 300 × 180 rectangle; Text }")

            label("VStack")
            VStack {
                Rectangle().fill(.blue).frame(width: 300, height: 180)
                Text("NPay")
            }
            .border(.red)
            .logSize("VStack { 300 × 180 rectangle; Text }")
        }
    }
}

// Section 6: alignment
struct AlignView: View {
    var body: some View {
        VStack(spacing: 10) {
            ForEach([("topLeading", Alignment.topLeading), ("center", .center), ("bottomTrailing", .bottomTrailing)], id: \.0) { name, a in
                label(".\(name)")
                ZStack(alignment: a) {
                    Color.blue

                    Text("NPay")
                        .foregroundStyle(.white)
                        .padding()
                }
                .frame(width: 300, height: 150)
            }
        }
    }
}

// Section 7: ZStack, background, overlay
struct LayeringView: View {
    var body: some View {
        VStack(spacing: 14) {
            label("ZStack")
            ZStack {
                Color.blue
                Text("NPay")
                    .foregroundStyle(.white)
            }
            .frame(width: 240, height: 120)
            .logSize("ZStack")

            label(".background")
            Text("NPay")
                .foregroundStyle(.white)
                .padding(30)
                .background(.blue)
                .logSize("Text + padding(30) + background")

            label(".overlay")
            RoundedRectangle(cornerRadius: 16)
                .fill(.blue)
                .frame(width: 240, height: 120)
                .overlay {
                    Text("NPay")
                        .foregroundStyle(.white)
                }
                .logSize("overlay")

            label(".overlay with oversized content")
            RoundedRectangle(cornerRadius: 16)
                .fill(.blue)
                .frame(width: 240, height: 120)
                .overlay {
                    Text("NPay Demo Account")
                        .font(.system(size: 40))
                        .fixedSize()
                        .foregroundStyle(.black)
                }
                .logSize("overlay with oversized text")
        }
        .font(.title2)
    }
}

// Section 8: steps A, B, C
struct StepsView: View {
    var body: some View {
        VStack(spacing: 10) {
            label("Step A")
            RoundedRectangle(cornerRadius: 20)
                .fill(.blue)
                .frame(height: 150)

            label("Step B")
            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(.blue)

                Text("₹25,000")
                    .font(.largeTitle.bold())
                    .foregroundStyle(.white)
            }
            .frame(height: 150)

            label("Step C")
            card.frame(height: 180)
        }
        .padding()
    }
    var card: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 20)
                .fill(.blue)

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
        }
    }
}

// Section 11, experiment C: ZStack card vs background card
struct CompareView: View {
    var body: some View {
        VStack(spacing: 14) {
            label("ZStack card")
            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(.blue)

                VStack(alignment: .leading, spacing: 12) {
                    Text("Available Balance")
                    Text("₹25,000")
                    Text("NPay Demo Account")
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(24)
            }
            .frame(height: 180)
            .logSize("ZStack card")

            label(".background(_:in:) card")
            VStack(alignment: .leading, spacing: 12) {
                Text("Available Balance")
                Text("₹25,000")
                Text("NPay Demo Account")
            }
            .foregroundStyle(.white)
            .padding(24)
            .frame(maxWidth: .infinity, alignment: .leading)
            .frame(height: 180)
            .background(.blue, in: RoundedRectangle(cornerRadius: 20))
            .logSize("background card")
        }
        .padding()
    }
}

// Section 10: the lesson's final code
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

            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(.blue)

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
            }
            .frame(height: 180)

            HStack(spacing: 30) {
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
