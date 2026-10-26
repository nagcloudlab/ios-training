# Unit 3 · Lesson 3.9 — SwiftUI Environment & Shared Configuration

> Lesson text as shared, in two pieces: Sections 1–15 (cut off inside Section 15) and "Part 2: Environment Internals,
> Dependency Injection & NPay Integration" (Sections 15–25). Interactive widgets are described in brackets. The deck
> (`index.html`, built by `tools/gen3_9.py`) follows both. The text ends by naming its next checkpoint (integrating the
> changes into the 3.8 app); that integration is **authored** and listed at the end. Evidence and authored additions
> are listed under "Deck changes".

NPay iOS Engineering Masterclass · Incremental Development · Environment Propagation · Dependency Injection · Runtime Internals

In Lesson 3.8, we learned how SwiftUI adapts NPay's layout to different screen sizes. Now we'll solve a different architectural problem. Our application has four tabs, multiple navigation destinations, reusable components, and a growing design system. Suppose NPay introduces a user preference: Light, Dark, or System appearance. Should we pass the selected theme manually through every view initializer?

```swift
HomeScreen(theme: theme)
BalanceCard(theme: theme)
PaymentsScreen(theme: theme)
HistoryScreen(theme: theme)
```

That would become difficult to maintain as the application grows. SwiftUI provides a mechanism called the Environment to propagate contextual information through the view hierarchy. Today we'll investigate how it works, how it differs from @State and @Binding, and when to use it in NPay.

## 1. Our NPay milestone

We'll add an appearance preference to NPay.

[NPay appearance laboratory: System / Light / Dark; "Simulate system Dark Mode"; NPay, Available Balance ₹25,000.00, Send Money, History, Recent Transactions (Coffee Shop · Electricity Bill · Salary Credit). "The entire NPay interface responds to one appearance selection. This is a conceptual simulation of SwiftUI's color-scheme environment."]

Notice that the theme affects the whole interface, not just one button. That's the behavior we want to understand.

## 2. First experiment — what is @Environment?

Let's start with a built-in environment value. Create a new SwiftUI file named EnvironmentExperiment.swift.

```swift
import SwiftUI

struct EnvironmentExperiment: View {
    @Environment(\.colorScheme)
    private var colorScheme

    var body: some View {
        VStack(spacing: 20) {
            Text("NPay Environment Lab")
                .font(.title2.bold())

            Text(
                colorScheme == .dark
                    ? "Dark Mode"
                    : "Light Mode"
            )

            Image(
                systemName: colorScheme == .dark
                    ? "moon.fill"
                    : "sun.max.fill"
            )
            .font(.system(size: 48))
        }
        .padding()
    }
}

#Preview {
    EnvironmentExperiment()
}
```

**What did we introduce?**

| Part | Meaning |
|---|---|
| @Environment | SwiftUI property wrapper |
| \.colorScheme | Key path identifying an environment value |
| colorScheme | Local property used to read the value |
| .dark / .light | Values of the ColorScheme enum |

**Connect to Unit 1.** Remember key paths? A key path provides a typed way to refer to a property. Here, `\.colorScheme` identifies a property of SwiftUI's EnvironmentValues. SwiftUI uses that key path to retrieve the contextual value for this view.

## 3. Where does the environment value come from?

This is the most important question. Unlike an ordinary initializer parameter, an environment value is supplied through the SwiftUI view hierarchy. A parent or ancestor can override an environment value for its descendants.

[Environment propagation: NPayRootView (supplies shared environment configuration) → TabView / NavigationStack (descendant views receive contextual values) → HomeScreen, PaymentsScreen, HistoryScreen, ProfileScreen (each reads colorScheme).]

**Important nuance.** Environment values are not simply global variables. Their values depend on where a view appears in the hierarchy. Two instances of the same view can receive different environment values if they have different ancestors.

## 4. Experiment — override the environment

Let's force one part of the interface into Dark Mode.

```swift
VStack {
    Text("Normal appearance")

    EnvironmentExperiment()
        .environment(\.colorScheme, .dark)
}
```

The child reads .dark, even if its surrounding application is using Light Mode.

**What's happening?** The .environment() modifier supplies an overridden value to the modified subtree. SwiftUI resolves the appropriate environment value when descendants read it.

**Trainer question.** Does this change the entire iPhone's system appearance? No. It changes the SwiftUI environment for the relevant subtree.

## 5. Environment versus @State versus @Binding

| Mechanism | Purpose | NPay example |
|---|---|---|
| @State | Own local mutable state | Sheet visibility |
| @Binding | Read/write access to state owned elsewhere | Balance editor |
| @Environment | Read contextual values from the hierarchy | Color scheme |

**Important distinction.** @Environment does not automatically mean a view can modify the underlying value. For example, `@Environment(\.colorScheme) private var colorScheme` is used to read the effective color scheme. If we want users to change their appearance preference, we'll own that preference in state and apply it to the view hierarchy.

## 6. Build NPay appearance preferences

Let's introduce a model.

```swift
enum NPayAppearance: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String {
        rawValue
    }

    var title: String {
        rawValue.capitalized
    }

    var colorScheme: ColorScheme? {
        switch self {
        case .system:
            nil
        case .light:
            .light
        case .dark:
            .dark
        }
    }
}
```

**Why is ColorScheme? optional?** Because System appearance means we don't want to force a specific scheme. We can return nil, allowing the app to follow the surrounding appearance preference.

## 7. Store the preference in NPayStore

Our existing NPayStore already owns account data and payment drafts. For this lesson, we'll add `var appearance: NPayAppearance = .system`. Then our root view can apply:

```swift
TabView {
    // NPay tabs
}
.preferredColorScheme(store.appearance.colorScheme)
```

**Why .preferredColorScheme()?** This is the intended SwiftUI API for expressing an appearance preference for the presentation. It differs from simply overriding the colorScheme environment value inside a subtree. The exact presentation behavior depends on the enclosing scene and presentation hierarchy.

## 8. Build the appearance picker

Let's add the control to NPay's Profile screen.

```swift
import SwiftUI

struct AppearanceSettingsView: View {
    @Bindable var store: NPayStore

    var body: some View {
        Form {
            Section("Appearance") {
                Picker(
                    "Theme",
                    selection: $store.appearance
                ) {
                    ForEach(NPayAppearance.allCases) { option in
                        Text(option.title)
                            .tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }
        }
        .navigationTitle("Appearance")
    }
}
```

**What happens?** The picker receives a binding to store.appearance. When the user changes the selection, the store updates. The root view reads the new preference and applies the appropriate color scheme.

## 9. Behind the scenes — theme update pipeline

[NPay appearance update flow — a 6-stage stepper; only Stage 1 was shared: "1. User selects Dark. Picker receives the selection." Caption: "Conceptual update flow. SwiftUI manages environment propagation and rendering internally."]

## 10. Built-in environment values

SwiftUI provides many environment values. Some useful examples for NPay:

| Environment value | Purpose |
|---|---|
| colorScheme | Light or Dark appearance |
| locale | Language and regional formatting |
| dynamicTypeSize | Preferred text-size category |
| accessibilityReduceMotion | Reduced-motion preference |
| dismiss | Dismiss current presentation |
| horizontalSizeClass | Horizontal size-class context |
| scenePhase | Application scene lifecycle state |

**Example**

```swift
@Environment(\.locale)
private var locale

@Environment(\.dynamicTypeSize)
private var dynamicTypeSize

@Environment(\.accessibilityReduceMotion)
private var reduceMotion
```

These values allow views to adapt to their context.

## 11. Create our own environment value

Now let's go deeper. Suppose NPay has a custom configuration value controlling whether demo-mode indicators are visible. We can create a custom environment key.

```swift
import SwiftUI

private struct NPayDemoModeKey: EnvironmentKey {
    static let defaultValue = true
}

extension EnvironmentValues {
    var npayDemoMode: Bool {
        get {
            self[NPayDemoModeKey.self]
        }
        set {
            self[NPayDemoModeKey.self] = newValue
        }
    }
}
```

**What is happening?** EnvironmentKey defines the value's type and default. EnvironmentValues provides typed access to it. Now a parent can supply `.environment(\.npayDemoMode, true)` and a child can read `@Environment(\.npayDemoMode) private var demoMode`.

**Connect to Unit 1.** This uses protocols, static properties, extensions, generics, and key paths. The Swift language concepts we've learned are now supporting a framework-level configuration system.

## 12. Behind the scenes — custom environment lookup

[How a child receives NPay configuration: NPayRootView (supplies npayDemoMode = true) → Environment modifier (overrides the value for descendants) → View hierarchy (propagates contextual values) → BalanceCard (reads @Environment(\.npayDemoMode)) → Conditional UI (shows the Demo Account label).]

**Important nuance.** An environment value is scoped to a view hierarchy. It isn't a universal application-wide singleton. That makes it useful for contextual configuration.

## 13. @EnvironmentObject versus modern Observation

You may encounter older SwiftUI code like `@EnvironmentObject var store: NPayStore`. Historically, this pattern commonly used classes conforming to ObservableObject. With modern Observation, we can use observable model objects and inject them into the environment by type. For example, `.environment(store)`. Then a descendant can read `@Environment(NPayStore.self) private var store`.

**Which approach should we use?** For our iOS 17+ NPay project, modern Observation is a good choice. However, @EnvironmentObject remains relevant for existing applications and backward compatibility. We'll compare these architectures more deeply in Unit 4.

## 14. Environment injection — an important failure case

Suppose a child declares `@Environment(NPayStore.self) private var store` but no ancestor injects an NPayStore instance. A required environment lookup can fail at runtime. This is why dependency injection must be deliberate.

**Safer design practice.** At the application root: `NPayRootView().environment(store)`. And in previews, provide the required environment object as well. For critical dependencies, explicit initializer injection can also be appropriate.

**Senior engineer principle.** Environment injection reduces parameter passing, but it can make dependencies less obvious at the call site. Use it deliberately, not automatically for every service.

## 15. Should NPayStore contain theme preferences?

For this lesson, adding appearance to NPayStore keeps the example simple. But architecturally, account data and UI preferences are different concerns. A larger application might use NPayAccountStore, NPayPaymentStore, NPayPreferences, NPayRouter. This avoids turning one observable object into a container for … [the first piece ends here]

## Part 2: Environment Internals, Dependency Injection & NPay Integration

NPay iOS Engineering Masterclass · Continuing from Section 15. We've learned how @Environment works, how values propagate through SwiftUI's view hierarchy, and how NPay can introduce shared appearance preferences. Now we'll complete the lesson by investigating environment precedence, dependency injection, Observation, state ownership, and runtime debugging.

## 15. Should NPayStore contain every shared setting?

No. Our current NPayStore owns the demo balance, transactions, and payment draft. We temporarily added appearance preferences to it for learning. But imagine adding language, notification preferences, security settings, and accessibility preferences to the same object. It would become unnecessarily large. A better long-term architecture separates responsibilities.

[NPayRootView (application composition root) → NPayStore (balance and transactions), NPayRouter (tabs and navigation), NPayPreferences (appearance and language), PaymentDraft (editable payment data).]

We'll formally introduce application architecture and dependency injection in Unit 4. For now, the important principle is that sharing state does not mean putting all state into one object.

## 16. Deep experiment — environment precedence

What happens if two ancestors provide different values for the same environment key? Consider:

```swift
import SwiftUI

struct EnvironmentPrecedenceLab: View {
    var body: some View {
        VStack(spacing: 20) {
            SchemeReader(title: "Outer")

            SchemeReader(title: "Inner")
                .environment(\.colorScheme, .dark)
        }
        .environment(\.colorScheme, .light)
    }
}

struct SchemeReader: View {
    let title: String

    @Environment(\.colorScheme)
    private var colorScheme

    var body: some View {
        Text("\(title): \(colorScheme == .dark ? "Dark" : "Light")")
    }
}

#Preview {
    EnvironmentPrecedenceLab()
}
```

**Predict the result.** What will each SchemeReader report? (Both Light / Outer Light, Inner Dark / Both Dark)

**Why?** Environment lookup is contextual. The effective value depends on the modifiers and ancestors surrounding the reading view. This is why two instances of BalanceCard can receive different appearance settings even though they use the same SwiftUI struct.

## 17. Build a dedicated NPayPreferences model

Let's improve our architecture. Create NPayPreferences.swift.

```swift
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
```

**What did we introduce?** NPayPreferences is an observable reference-type model. It owns presentation preferences rather than payment data. We'll create one instance at the application root.

## 18. Inject preferences into the SwiftUI hierarchy

In NPayRootView, introduce `@State private var preferences = NPayPreferences()`. Then apply the environment:

```swift
TabView {
    // Existing NPay tabs
}
.environment(preferences)
.preferredColorScheme(
    preferences.appearance.colorScheme
)
```

**What happens?** The root owns the preferences object. The environment makes it available to descendants. The appearance preference influences the app's presentation.

[NPayRootView (owns NPayPreferences) → .environment(preferences) (makes the instance available to descendants) → ProfileScreen (reads and edits preferences) → Observation (tracks relevant property changes) → Root appearance modifier (applies the selected color scheme).]

## 19. Read the preferences in ProfileScreen

Now we'll use environment-based dependency injection.

```swift
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
```

**Why use @Bindable inside body?** @Environment retrieves the observable model instance. @Bindable provides binding projections for its mutable properties. The picker and toggle need bindings because they modify values.

**Important distinction.** @Environment and @Bindable solve different problems. One retrieves a contextual dependency. The other exposes bindings to mutable properties.

## 20. Read the Demo Badge preference in BalanceCard

Let's extend our reusable balance component.

```swift
struct BalanceCard: View {

    let balancePaise: Int

    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {

            Text("Available Balance")
                .font(.subheadline)

            Text(Money.display(balancePaise))
                .font(.largeTitle.bold())

            if preferences.showDemoBadge {
                Text("DEMO ACCOUNT")
                    .font(.caption.bold())
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(
                        .white.opacity(0.18),
                        in: Capsule()
                    )
            }
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
```

Now changing the toggle in Profile affects the balance card on Home. No manual showDemoBadge parameter is needed between the root and BalanceCard.

**Important safety note.** The Demo badge is only a visual preference in this lesson. NPay remains a simulation regardless of whether the badge is displayed. A production application must never use a UI preference to determine whether payment operations are real or simulated.

## 21. Behind the scenes — how Observation works with Environment

[NPay preference-update pipeline — a 6-stage stepper; only Stage 1 was shared: "1. User toggles setting. The Toggle control receives the interaction." Caption: "Conceptual update model; exact dependency tracking and rendering scheduling are framework-managed."]

## 22. An important failure — missing environment dependency

Consider `@Environment(NPayPreferences.self) private var preferences`. This declares a required dependency. If a view attempts to read it without an ancestor supplying the model, SwiftUI can fail at runtime. For example, a standalone BalanceCard preview must provide the preferences.

```swift
#Preview {
    BalanceCard(balancePaise: 2_500_000)
        .environment(NPayPreferences())
}
```

**Senior engineer lesson.** Environment injection is convenient, but dependencies become less visible at the initializer call site. A good architecture documents required environment dependencies and provides them in previews and tests.

## 23. Does the environment replace dependency injection?

No. It is one mechanism for supplying dependencies. We can compare three approaches.

| Approach | Example | Best use |
|---|---|---|
| Initializer injection | BalanceCard(balancePaise: balance) | Explicit required data |
| Environment values | @Environment(\.colorScheme) | Contextual configuration |
| Observable environment model | @Environment(NPayPreferences.self) | Shared observable preferences |

For NPay, we'll continue using explicit parameters for domain data and environment injection for suitable shared UI configuration. This avoids hiding every dependency inside the environment.

## 24. Xcode investigation lab

Try these experiments in sequence: (1) Change the appearance picker from System to Dark. (2) Switch between Home, Payments, History, and Profile. (3) Verify that the selected appearance applies consistently. (4) Turn off Show Demo Badge and return to Home. (5) Verify the badge disappears without changing the balance. (6) Add `.environment(\.colorScheme, .light)` to one isolated test subtree and inspect its effect. (7) Create a preview without the required NPayPreferences injection, observe the failure, and restore the dependency. (8) Add `Self._printChanges()` to BalanceCard and observe when preference changes cause its body to be evaluated.

## 25. Senior engineer knowledge check

[Environment Engineering Assessment, 0 / 6 answered.]
1. Is an environment value a global variable? (Yes / No, it is contextual to the view hierarchy)
2. What happens when a nearer ancestor overrides an environment value? (The nearer value applies to its descendants / The application restarts / The outer value always wins)
3. Why use @Bindable with an observable preferences object? (To obtain bindings to mutable properties / To start a background task / To persist preferences automatically)
4. Does `.environment(preferences)` automatically persist preferences to disk? (Yes / No)
5. What is the risk of missing a required observable environment model? (A runtime failure when accessed / Automatic fallback to UserDefaults / A compiler-generated default model)
6. Should every NPay dependency be hidden in the environment? (Yes / No)

**Lesson 3.9 — Final checkpoint.** We've now covered environment values, key paths, inheritance and precedence, custom environment keys, modern Observation-based injection, @Bindable, appearance preferences, and missing-dependency behavior. Our NPay application has a new architecture concept: NPayRootView → NPayPreferences → Environment → Feature Screens → Reusable Components. The next practical checkpoint is to integrate these changes into the complete NPay project from Lesson 3.8 and verify them in Xcode.

Next — Lesson 3.10: Accessibility & Localization. We'll investigate VoiceOver, Dynamic Type, accessibility identifiers, localization resources, right-to-left layouts, and how NPay can support multiple languages without duplicating screens.

## Integration through Lesson 3.9 (authored)

The text's checkpoint, done on the Lesson 3.8 code and run in the simulator (`tools/sim3_9/App.swift`). Sections 17–20
are used (Sections 7–8's store-based version is the text's first step, superseded by NPayPreferences):
- **App/NPayPreferences.swift** and **Screens/AppearanceSettingsView.swift**: the text's code.
- **NPayRootView**: owns `@State private var preferences = NPayPreferences()`; `.environment(preferences)` and
  `.preferredColorScheme(preferences.appearance.colorScheme)` on the TabView; a new `NPayRoute.appearance` case maps to
  AppearanceSettingsView.
- **ProfileScreen**: an "Appearance" row above Settings.
- **BalanceCard**: the Section 20 structure (the DEMO ACCOUNT badge replaces the "NPay Demo Account" caption), keeping
  3.6's numeric transition and 3.7's tokens.

### App/NPayPreferences.swift and Screens/AppearanceSettingsView.swift

```swift
import SwiftUI

// App/NPayPreferences.swift (section 17)

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

// Screens/AppearanceSettingsView.swift (section 19)

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
```

### Components/BalanceCard.swift

```swift
import SwiftUI

struct BalanceCard: View {

    let balancePaise: Int

    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {

            Text("Available Balance")
                .font(.subheadline)

            Text(Money.display(balancePaise))
                .font(.largeTitle.bold())
                .contentTransition(.numericText())
                .animation(
                    .easeInOut(duration: 0.4),
                    value: balancePaise
                )

            if preferences.showDemoBadge {
                Text("DEMO ACCOUNT")
                    .font(.caption.bold())
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(
                        .white.opacity(0.18),
                        in: Capsule()
                    )
            }
        }
        .foregroundStyle(.white)
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(24)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(cornerRadius: NPayTheme.Radius.card)
        )
    }
}
```

### App/NPayRootView.swift (excerpt)

```swift
import SwiftUI

struct NPayRootView: View {

    @State private var router = NPayRouter()
    @State private var store = NPayStore()
    @State private var preferences = NPayPreferences()

    var body: some View {
        @Bindable var router = router

        TabView(selection: $router.selectedTab) {

            NavigationStack(path: $router.homePath) {
                HomeScreen(store: store, router: router)
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Home", systemImage: "house")
            }
            .tag(NPayTab.home)

            NavigationStack(path: $router.paymentsPath) {
                PaymentsScreen(
                    store: store,
                    router: router
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Payments", systemImage: "arrow.up.right")
            }
            .tag(NPayTab.payments)

            NavigationStack(path: $router.historyPath) {
                HistoryScreen(
                    transactions: store.transactions
                )
                .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("History", systemImage: "clock")
            }
            .tag(NPayTab.history)

            NavigationStack(path: $router.profilePath) {
                ProfileScreen()
                    .navigationDestination(for: NPayRoute.self, destination: destination)
            }
            .tabItem {
                Label("Profile", systemImage: "person")
            }
            .tag(NPayTab.profile)
        }
        .environment(preferences)
        .preferredColorScheme(
            preferences.appearance.colorScheme
        )
    }

    // destination(_:) as in 3.3, plus case .appearance: AppearanceSettingsView()
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_9.py`, 46 slides) follows both pieces, grouped into 8 Parts: the milestone
(1), @Environment (2, 3), overrides and precedence (4, 16), which mechanism? (5, 10), appearance preference (6–9),
custom environment values (11, 12), observable models in the environment (13, 14, 15, 17–22), dependency injection (15,
23, 24); then recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_9/`, rerun with `sh tools/sim3_9/run.sh`; system
appearance switched with `simctl ui appearance`; segmented-picker segments and switches driven as a tap does)
- EnvironmentExperiment: "Light Mode" with a light system, "Dark Mode" with a dark one (screenshots).
- Section 4's override in a light app: the screen's labels include "Dark Mode", but the child's text resolved to white
  on the white background and is not visible (screenshot).
- EnvironmentPrecedenceLab: "Outer: Light", "Inner: Dark".
- NPayDemoModeKey: "true" with no ancestor setting it (the default), "false" under `.environment(\.npayDemoMode, false)`.
- `.environment(\.colorScheme, .dark)` vs `.preferredColorScheme(.dark)` with a presented sheet (authored): the
  override left the sheet light; the preference darkened it (screenshots).
- Integrated app: Appearance → Dark made Home, Payments, History and Profile dark (window trait read each time);
  turning off Show Demo Badge removed the badge on Home with the balance unchanged (₹25,000.00).
- `_printChanges` in the text's BalanceCard (traced copy): launch "@self, @identity, _preferences changed"; badge
  toggle "\NPayPreferences.showDemoBadge changed"; appearance change "@self changed"; unrelated counter: nothing.
- Missing dependency: BalanceCard without NPayPreferences → "Fatal error: No Observable object of type
  NPayPreferences found. A View.environmentObject(_:) for NPayPreferences may be missing as an ancestor of this view."
- Relaunch after choosing Dark: back to System (preferences are in memory).
- swiftc: `extension EnvironmentValues { @Entry var npayDemoMode: Bool = true }` typechecks for the iOS 17 target.

**Authored (flagged)**
- The integration (above), the sheet experiment, the traced BalanceCard lab, the relaunch check, the @Entry note.
- Sections 9 and 12 as diagrams (Section 9's stages 2–6 authored, marked conceptual; Section 12's chain was shared).
- Review: the text's 6 questions (options reordered) plus three predict items (the override on a white screen; a sheet
  under an override; @Entry) and a spaced item from 3.8; 2 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.10 as the text names it; Units 4 and 6 as it says), lab, end.
- The Unit 3 progress strip now names every lesson (3.4–3.10 from their texts); all Unit 3 decks were rebuilt.

**Wording**
- "Trainer question", "Senior engineer principle / lesson / knowledge check" became neutral callouts and "Check your
  understanding".
