import SwiftUI

enum NPayAppearance: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var title: String {
        rawValue.capitalized
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system:
            return nil
        case .light:
            return .light
        case .dark:
            return .dark
        }
    }
}

@MainActor
@Observable
final class NPayPreferences {
    var appearance: NPayAppearance = .system
    var showDemoBadge = true
}
