import SwiftUI

// Lesson 2.2 evidence app. Each launch argument runs one experiment from the lesson text.
@main
struct LabApp: App {
    var body: some Scene {
        WindowGroup {
            let args = ProcessInfo.processInfo.arguments
            if args.contains("library") { LibraryView() }
            else if args.contains("invalid") { InvalidView() }
            else if args.contains("sizes") { SizesView() }
            else if args.contains("sharp") { SharpView() }
            else if args.contains("colors") { ColorsView() }
            else if args.contains("types") { TypesView() }
            else if args.contains("assets") { AssetsView() }
            else if args.contains("final") { ContentView() }
            else if args.contains("before") { BeforeView() }
            else { SymbolView() }
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

// Section 2: the first experiment
struct SymbolView: View {
    var body: some View {
        Image(systemName: "creditcard.fill")
            .logSize("creditcard.fill, default")
    }
}

// Section 3: real SF Symbols for the text's six names
struct LibraryView: View {
    let names = ["creditcard.fill", "house.fill", "person.fill", "bell.fill", "heart.fill", "lock.fill"]
    var body: some View {
        LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 3), spacing: 36) {
            ForEach(names, id: \.self) { name in
                VStack(spacing: 10) {
                    Image(systemName: name).font(.system(size: 44))
                    Text(name).font(.caption.monospaced())
                }
            }
        }
        .padding()
    }
}

// Section 4: an unsupported name still compiles
struct InvalidView: View {
    var body: some View {
        Image(systemName: "creditcard.fil")
            .logSize("creditcard.fil")
    }
}

// Section 5: .font sizes the symbol
struct SizesView: View {
    var body: some View {
        HStack(alignment: .bottom, spacing: 32) {
            Image(systemName: "creditcard.fill").font(.system(size: 24)).logSize("size 24")
            Image(systemName: "creditcard.fill").font(.system(size: 64)).logSize("size 64")
            Image(systemName: "creditcard.fill").font(.system(size: 100)).logSize("size 100")
        }
    }
}

// Section 5: symbol at 100 pt vs a 16 pt bitmap enlarged to the same width
struct SharpView: View {
    @State private var bitmap: UIImage?
    var body: some View {
        HStack(spacing: 40) {
            Image(systemName: "creditcard.fill").font(.system(size: 100))
            if let bitmap {
                Image(uiImage: bitmap).resizable().scaledToFit().frame(width: 134)
            }
        }
        .task {
            let renderer = ImageRenderer(content: Image(systemName: "creditcard.fill").font(.system(size: 16)))
            renderer.scale = 1
            bitmap = renderer.uiImage
            if let b = bitmap { print("bitmap: \(Int(b.size.width)) × \(Int(b.size.height)) pixels") }
        }
    }
}

// Section 7: same symbol, three foreground styles
struct ColorsView: View {
    var body: some View {
        HStack(spacing: 32) {
            Image(systemName: "creditcard.fill").foregroundStyle(.blue)
            Image(systemName: "creditcard.fill").foregroundStyle(.green)
            Image(systemName: "creditcard.fill").foregroundStyle(.red)
        }
        .font(.system(size: 64))
    }
}

// Sections 5, 7, 8 and 10: concrete types
struct TypesView: View {
    var body: some View {
        Text("Types printed to the console")
            .task {
                let icon = Image(systemName: "creditcard.fill")
                print(type(of: icon))
                print(type(of: icon.font(.system(size: 64))))
                print(type(of: icon.foregroundStyle(.blue)))
                print(type(of: Text("NPay").font(.largeTitle)))
                print("ContentView.body:", type(of: ContentView().body))
            }
    }
}

// Section 9: asset image vs system symbol
struct AssetsView: View {
    var body: some View {
        VStack(spacing: 40) {
            Image("NPayLogo").logSize("Image(\"NPayLogo\")")
            Image(systemName: "NPayLogo").logSize("Image(systemName: \"NPayLogo\")")
            Image("creditcard.fill").logSize("Image(\"creditcard.fill\")")
        }
    }
}

// Section 1: the screen at the end of Lesson 2.1
struct BeforeView: View {
    var body: some View {
        Text("NPay")
            .font(.largeTitle)
            .bold()
            .foregroundStyle(.blue)
    }
}

// Section 10: the lesson's final code
struct ContentView: View {

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
