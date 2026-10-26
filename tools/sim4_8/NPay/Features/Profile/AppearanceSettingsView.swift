import SwiftUI

struct AppearanceSettingsView: View {

    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        @Bindable var preferences = preferences

        Form {
            Section("Appearance") {
                Picker(
                    "Theme",
                    selection: $preferences.appearance
                ) {
                    ForEach(NPayAppearance.allCases) { option in
                        Text(option.title)
                            .tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }

            Section("Display") {
                Toggle(
                    "Show Demo Badge",
                    isOn: $preferences.showDemoBadge
                )
            }
        }
        .navigationTitle("Appearance")
    }
}
