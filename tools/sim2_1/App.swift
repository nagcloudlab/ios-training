import SwiftUI

// Lesson 2.1 evidence app. Each launch argument runs one experiment from the lesson text.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("topleading") { TopLeadingView() }
            else if args.contains("measure") { MeasureView() }
            else if args.contains("types") { TypesView() }
            else if args.contains("order") { OrderView() }
            else if args.contains("unicode") { UnicodeView() }
            else if args.contains("l10n") { LocalizationView() }
            else if args.contains("final") { FinalView().logSize("final title") }
            else { ContentView() }
        }
    }
}

// Section 2: the first screen
struct ContentView: View {
    var body: some View {
        Text("NPay")
    }
}

// Section 8: move it with a frame
struct TopLeadingView: View {
    var body: some View {
        Text("NPay")
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .topLeading)
    }
}

extension View {
    func logSize(_ label: String) -> some View {
        onGeometryChange(for: CGSize.self) { $0.size } action: { s in
            print("\(label): \(Double(s.width).formatted(.number.precision(.fractionLength(1)))) × \(Double(s.height).formatted(.number.precision(.fractionLength(1)))) pt")
        }
    }
}

// Section 9: the same text, measured under different proposed widths
struct MeasureView: View {
    let line = "Welcome to NPay. Payments made simple."
    var body: some View {
        VStack(spacing: 40) {
            Text("NPay").logSize("\"NPay\", .body")
            Text("NPay").font(.largeTitle).logSize("\"NPay\", .largeTitle")
            Text(line).logSize("proposed width 260").frame(width: 260).border(.gray)
            Text(line).logSize("proposed width 140").frame(width: 140).border(.gray)
        }
    }
}

// Section 11: modifier return types; Section 6: the body's hidden concrete type
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let original = Text("NPay")
                let styled = original.font(.largeTitle)
                let padded = original.padding()
                print(type(of: original))
                print(type(of: styled))
                print(type(of: padded))
                print("ContentView.body:", type(of: ContentView().body))
                print("FinalView.body:", type(of: FinalView().body))
                print("TopLeadingView.body:", type(of: TopLeadingView().body))
            }
    }
}

// Sections 12 and 16: modifier order
struct OrderView: View {
    var body: some View {
        VStack(spacing: 48) {
            Text("NPay")
                .padding()
                .background(.yellow)
                .logSize("A: padding, then background")
            Text("NPay")
                .background(.yellow)
                .padding()
                .logSize("B: background, then padding")
        }
        .font(.largeTitle)
    }
}

// Section 13: Unicode
struct UnicodeView: View {
    var body: some View {
        VStack(spacing: 24) {
            Text("Welcome to NPay")
            Text("வணக்கம்")
            Text("नमस्ते")
        }
        .font(.largeTitle)
        .task {
            for s in ["NPay", "வணக்கம்", "नमस्ते"] {
                print("\(s): \(s.count) characters, \(s.unicodeScalars.count) scalars, \(s.utf8.count) UTF-8 bytes")
            }
        }
    }
}

// Section 13: localization lookup vs verbatim (run with -AppleLanguages "(ta)")
struct LocalizationView: View {
    var body: some View {
        VStack(spacing: 24) {
            Text("Welcome to NPay")
            Text(verbatim: "Welcome to NPay")
        }
        .font(.title)
    }
}

// Section 14: the lesson's final code
struct FinalView: View {
    var body: some View {
        Text("NPay")
            .font(.largeTitle)
            .bold()
            .foregroundStyle(.blue)
    }
}
