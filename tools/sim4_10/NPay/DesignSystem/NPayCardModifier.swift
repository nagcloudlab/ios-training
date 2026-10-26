import SwiftUI

struct NPayCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(
                NPayTheme.Colors.cardBackground,
                in: RoundedRectangle(cornerRadius: 18)
            )
    }
}

extension View {
    func npayCardStyle() -> some View {
        modifier(NPayCardModifier())
    }
}
