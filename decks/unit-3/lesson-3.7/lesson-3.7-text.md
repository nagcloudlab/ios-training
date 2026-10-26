# Unit 3 · Lesson 3.7 — Reusable SwiftUI Components & NPay Design System

> Lesson text as shared, in two pieces: Sections 1–14 (cut off at the knowledge check) and "Part 2: Design System
> Internals & Engineering Review" (Sections 14–22). Interactive widgets are described in brackets. The deck
> (`index.html`, built by `tools/gen3_7.py`) follows both. The text ends by naming its next checkpoint (integrating the
> components into the 3.6 app); that integration is **authored** and listed at the end. Evidence and authored additions
> are listed under "Deck changes".

NPay iOS Engineering Masterclass · Incremental Development · View Composition · Protocols · Generics · Environment Internals

In Lesson 3.6, we added animations to NPay's balance, transactions, and payment-success screen. Now we're going to solve a different engineering problem. Our NPay application has grown to multiple screens, but we are repeating styling code everywhere. For example:

```swift
.padding(16)
.background(
    Color.blue.opacity(0.08),
    in: RoundedRectangle(cornerRadius: 16)
)
```

And `.buttonStyle(.borderedProminent)`. These work, but as NPay grows, repeated styling becomes difficult to maintain.

Our engineering question: How do professional iOS applications create consistent, reusable UI components without sacrificing SwiftUI's declarative architecture? Today we'll build the foundation of an NPay Design System.

## 1. Our NPay milestone — before and after

[BEFORE · UNIT 3.6: NPay, Available Balance ₹25,000, Send Money, Recent Transactions. AFTER · UNIT 3.7: NPay, Available Balance ₹25,000, NPay Demo Account, Send Money, Recent Transactions — styled consistently.]

We're not changing NPay's business logic. We're creating a reusable visual language.

## 2. What exactly is a design system?

A design system is a collection of shared design decisions and reusable UI components. For NPay, we'll organize it into three layers.

[Design Tokens (Colors · Spacing · Typography · Corner radii) → Reusable Components (NPayButton · NPayCard · NPaySectionHeader) → Feature Screens (Home · Payments · History · Profile).]

**Why separate these layers?** Because the design tokens define the shared visual rules, components apply those rules, and screens assemble the components. This prevents every screen from independently inventing its own appearance.

## 3. First concept — design tokens

Let's define NPay's colors and spacing. Create NPayTheme.swift.

```swift
import SwiftUI

enum NPayTheme {

    enum Colors {
        static let primary = Color(
            red: 0.10,
            green: 0.34,
            blue: 0.65
        )

        static let success = Color.green

        static let cardBackground =
            Color.blue.opacity(0.06)
    }

    enum Spacing {
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
    }

    enum Radius {
        static let small: CGFloat = 10
        static let card: CGFloat = 18
    }
}
```

**What is this Swift code?** An enum with static properties. We're using Swift's type system to organize constants. We don't need to instantiate NPayTheme. Instead, we access `NPayTheme.Colors.primary`, `NPayTheme.Spacing.medium`, `NPayTheme.Radius.card`.

**Connect to Unit 1.** This is ordinary Swift namespace organization using enums and static members. No special SwiftUI mechanism is required to define the tokens.

## 4. Why not hardcode colors everywhere?

Consider `.foregroundStyle(.blue)`. That works. But suppose NPay's brand color changes. If we have hundreds of hardcoded colors, updating the application becomes difficult. Instead: `.foregroundStyle(NPayTheme.Colors.primary)`. Now the styling references one shared token.

**Senior engineer insight.** Design tokens are not just about convenience. They create a consistent interface contract across teams and features. For production applications, color assets and semantic colors are often preferable to hardcoded RGB values because they can support light mode, dark mode, accessibility contrast, and branding variations.

## 5. Build our first reusable component — NPayButton

Currently, we use SwiftUI's built-in button styles. Let's create a branded button.

```swift
import SwiftUI

struct NPayButton: View {
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(
                cornerRadius: NPayTheme.Radius.small
            )
        )
    }
}
```

Use it:

```swift
NPayButton(title: "Send Money") {
    print("Send tapped")
}
```

**What's reusable?** The visual styling stays inside NPayButton. The caller supplies the action. This is the same closure-based component architecture we learned in Lesson 2.7.

## 6. Behind the scenes — how a reusable View works

Remember that SwiftUI views are structs conforming to View. When we write `NPayButton(title: "Send Money") { print("Tapped") }` we create a value describing a reusable component. SwiftUI evaluates its body as needed.

[NPayButton composition: Feature Screen (creates NPayButton with title and action) → NPayButton (reusable SwiftUI View struct) → Button (native interactive control) → Text + Modifiers (defines label, padding, colors and shape) → SwiftUI runtime (coordinates layout, rendering and interaction).]

**Important distinction.** Creating a reusable view does not necessarily create a separate UIKit view object. SwiftUI composes view descriptions and manages the platform presentation internally.

## 7. Build NPayCard — generic reusable content

Now we'll build a more advanced component. We want a card that can contain any SwiftUI view content. For example `NPayCard { Text("Recent Transactions") }`, or `NPayCard { VStack { Text("Account"); Text("Demo User") } }`. How can one component accept different view types? Using generics and @ViewBuilder.

```swift
import SwiftUI

struct NPayCard<Content: View>: View {

    @ViewBuilder let content: Content

    var body: some View {
        content
            .padding(NPayTheme.Spacing.medium)
            .frame(maxWidth: .infinity)
            .background(
                NPayTheme.Colors.cardBackground,
                in: RoundedRectangle(
                    cornerRadius: NPayTheme.Radius.card
                )
            )
    }
}
```

**Connect to Unit 1.** Content is a generic type parameter. The constraint `Content: View` means the content must conform to SwiftUI's View protocol. @ViewBuilder lets the caller use declarative view-building syntax inside the trailing closure.

## 8. What does @ViewBuilder actually do?

Consider `NPayCard { Text("Account"); Text("Balance") }`. There are two view expressions. How can Swift return both? SwiftUI's result builder transforms the closure into a composed view value. Conceptually, multiple children can be represented by a tuple-like view composition. The exact generated types are compiler and framework details.

[@ViewBuilder closure: Text A, Text B → Composed Content: View.]

**Trainer question.** Does @ViewBuilder mean the closure returns an array of UIView objects? No. It builds SwiftUI view descriptions using the result-builder mechanism.

## 9. Custom ViewModifier versus reusable View

We already studied ViewModifier in Lesson 2.6. Now let's compare the two approaches.

| Reusable View | ViewModifier |
|---|---|
| Encapsulates content structure | Encapsulates a transformation |
| Can receive custom child content | Modifies an existing view |
| Example: NPayCard | Example: NPayCardStyle |
| Useful for semantic components | Useful for shared styling rules |

**Example custom modifier**

```swift
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
```

Usage: `Text("Recent Transactions").npayCardStyle()`.

**Which approach should we choose?** For a meaningful component with its own structure, use a reusable view. For a styling rule applicable to many different views, use a modifier.

## 10. Build NPaySectionHeader

Our dashboard and history screens both need section headers. Let's create a reusable component.

```swift
struct NPaySectionHeader: View {
    let title: String
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        HStack {
            Text(title)
                .font(.headline)

            Spacer()

            if let actionTitle,
               let action {
                Button(actionTitle, action: action)
                    .font(.subheadline)
            }
        }
    }
}
```

Use it:

```swift
NPaySectionHeader(
    title: "Recent Transactions",
    actionTitle: "View All"
) {
    router.select(.history)
}
```

**Why is this useful?** The same header component can appear in Home, History, or Profile without duplicating its layout.

## 11. Environment propagation and design systems

SwiftUI allows certain styling values to propagate through the view hierarchy. For example:

```swift
VStack {
    Text("Account")
    Text("Balance")
}
.font(.headline)
```

The font environment influences descendant text. But not every modifier propagates. For example, `.padding()` changes layout around a specific view rather than setting a globally inherited padding value.

**Important distinction.** Design tokens are ordinary Swift constants. Environment values are part of SwiftUI's contextual data propagation system. We'll study custom environment keys and shared themes in Lesson 3.9.

## 12. Integrate the design system into NPay

We'll update three parts of the existing application.

**A. Replace primary buttons.** Before: `Button("Send Money") { submitPayment() }.buttonStyle(.borderedProminent)`. After: `NPayButton(title: "Send Money") { submitPayment() }`.

**B. Wrap transaction sections.** Before: a VStack with `Text("Recent Transactions")` and rows, `.padding()`, `.background(Color.blue.opacity(0.06))`. After:

```swift
NPayCard {
    VStack(alignment: .leading, spacing: 12) {
        Text("Recent Transactions")
        // Rows
    }
}
```

**C. Reuse section headers.** `NPaySectionHeader(title: "Recent Transactions", actionTitle: "View All") { router.select(.history) }`.

The application's business logic remains unchanged. We're improving composition and consistency.

## 13. Xcode experiments

Try these one by one: (1) Change NPayTheme.Colors.primary and observe all components using it. (2) Change NPayTheme.Radius.card and compare card shapes. (3) Create an NPayCard containing a VStack. (4) Create another NPayCard containing an HStack. (5) Inspect the inferred generic type of NPayCard. (6) Compare a reusable view with a custom modifier. (7) Test the design in light and dark appearance.

**Debugging experiment.** Use `let _ = Self._printChanges()` inside a reusable component's body. Observe when SwiftUI reevaluates it. Remember: reevaluation doesn't necessarily mean a full redraw.

## Part 2: Design System Internals & Engineering Review

NPay iOS Engineering Masterclass · Continuing from Section 14. We've created our first NPay design system using reusable components, generic views, @ViewBuilder, and design tokens. Now we'll complete the lesson by exploring component architecture, SwiftUI's type system, styling consistency, and the senior-engineer assessment.

## 14. Senior engineer knowledge check

[Design System Engineering Assessment, 0 / 7 answered.]
1. What is a design token? (A shared visual constant / A network authentication token / A SwiftUI thread)
2. Why use `NPayCard<Content: View>`? (To accept different SwiftUI content types / To create a database / To disable type checking)
3. What does @ViewBuilder do? (Builds composed SwiftUI view descriptions / Creates arrays of UIView objects / Starts background tasks)
4. When is ViewModifier appropriate? (For reusable view transformations / For storing payment data / For managing navigation paths)
5. Do hardcoded design tokens automatically support dark mode? (Yes / No)
6. Does creating a custom SwiftUI View necessarily create a separate UIKit view object? (Yes / No)
7. Should business logic live inside NPayButton? (Yes / No)

## 15. Deeper concept — why generic views matter

Let's revisit `struct NPayCard<Content: View>: View`. Content is a generic parameter. When we create `NPayCard { Text("Available Balance") }`, Swift can infer the content type as Text. But when we create `NPayCard { VStack { Text("Account"); Text("Balance") } }`, the content type is a VStack with its own generic content type.

**Why is this powerful?** SwiftUI can represent complex view hierarchies using strongly typed compositions. This enables compile-time checking and optimization opportunities.

[NPayCard<Content>: Content = Text (simple content); Content = VStack<...> (composed content).]

**Senior engineer insight.** Generics are a foundational part of SwiftUI's declarative architecture. They allow reusable components without forcing every child view into a type-erased AnyView.

## 16. Why not use AnyView everywhere?

SwiftUI provides AnyView, which erases the concrete view type. For example: `let content: AnyView = AnyView(Text("NPay"))`. This can be useful when different view types must be stored behind one common type. But unnecessary type erasure can obscure structural information and introduce additional complexity.

**Compare.** Generic approach: `struct NPayCard<Content: View>: View { let content: Content }`. Type-erased approach: `struct NPayCard: View { let content: AnyView }`. For our reusable NPay components, the generic approach is usually preferable.

## 17. A more flexible NPayButton

Our first button accepted only a string title. Now let's support a label with an icon.

```swift
import SwiftUI

struct NPayButton: View {
    let title: String
    let symbol: String?
    let action: () -> Void

    init(
        _ title: String,
        symbol: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.symbol = symbol
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                if let symbol {
                    Image(systemName: symbol)
                }

                Text(title)
            }
            .font(.headline)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(
                cornerRadius: NPayTheme.Radius.small
            )
        )
    }
}
```

Use it:

```swift
NPayButton(
    "Send Money",
    symbol: "arrow.up.right"
) {
    print("Send tapped")
}
```

**Connect to Unit 1.** This combines several Swift concepts: optional properties; custom initializers; default arguments; escaping closures; conditional binding with if let; protocol conformance through View. All of them are now working together in a reusable UI component.

## 18. Component responsibility — what belongs inside NPayButton?

Suppose the Send Money button must validate a payment. Should the reusable button contain `store.recordDemoPayment(...)`? No. The button should not know about financial operations. Instead: `NPayButton("Send Money") { submitPayment() }`. The component handles presentation and user activation. The caller handles application behavior.

[NPayButton (appearance + interaction) → PaymentsScreen (coordinates payment form) → NPayStore (validates and records demo payment).]

This separation will become even more important when we introduce MVVM and clean architecture.

## 19. Dynamic Type — why fixed fonts can be problematic

Consider `.font(.system(size: 16))`. This uses a fixed font size unless additional scaling behavior is applied. Users can configure larger text sizes for accessibility. SwiftUI's semantic font styles are generally a better default: `.font(.headline)`, `.font(.body)`, `.font(.caption)`. These adapt to the system's Dynamic Type settings.

**Senior engineer principle.** A design system should not simply make every screen look identical. It should help the interface adapt consistently to user accessibility settings.

## 20. Design tokens versus semantic colors

Our initial theme uses a fixed color, `Color(red: 0.10, green: 0.34, blue: 0.65)`. For production NPay, we'd prefer semantic color assets when appropriate. For example, create a color asset named NPayPrimary in Assets.xcassets. Then use `Color("NPayPrimary")`. The asset can define different appearances for light and dark mode.

**Why does this matter?** A fixed dark-blue color might work well on a white background but become difficult to read in another appearance. Semantic assets let the design system adapt without rewriting every component.

## 21. NPay component catalog

| Component | Responsibility |
|---|---|
| NPayTheme | Shared design tokens |
| NPayButton | Branded primary actions |
| NPayCard | Reusable card container |
| NPaySectionHeader | Consistent section headings |
| NPayCardModifier | Reusable card styling |
| BalanceCard | Domain-specific balance display |
| TransactionRow | Domain-specific transaction display |

Notice the distinction between general-purpose design components and domain-specific feature components. Both are reusable, but at different architectural levels.

## 22. Xcode debugging experiments

Before closing the lesson, try: (1) Change NPay's primary color in NPayTheme and inspect the affected components. (2) Change the corner radius token and observe all cards. (3) Create an NPayCard containing an HStack. (4) Create another containing a VStack. (5) Inspect the generic types inferred by Swift. (6) Test the design in dark mode. (7) Increase the system text size and check whether labels remain readable.

**Advanced experiment.** Temporarily use `let _ = Self._printChanges()` inside NPayButton.body. Observe when SwiftUI reevaluates the component. Do not assume that every body evaluation causes a complete redraw.

**Lesson 3.7 checkpoint.** We've completed the conceptual coverage of reusable SwiftUI components, generics, @ViewBuilder, custom modifiers, design tokens, semantic colors, and component responsibilities. Our NPay design system now has a clear structure: Design Tokens → Reusable Components → Feature Screens → Application Behavior. The next practical checkpoint is to integrate these components into the full NPay application from Lesson 3.6 and verify the resulting screens in Xcode.

Next — Lesson 3.8: Adaptive Layouts, GeometryReader & Responsive SwiftUI. We'll make NPay adapt to different iPhone sizes, orientations, Dynamic Type settings, and available layout space while investigating SwiftUI's layout proposal and measurement system.

## Integration through Lesson 3.7 (authored)

The text's checkpoint, done on the Lesson 3.6 code and run in the simulator (`tools/sim3_7/App.swift`). New
`DesignSystem/` files hold the text's code (NPayButton is the Section 17 version). Changes elsewhere:
- **HomeScreen**: Send Money is an `NPayButton` that selects the Payments tab (replacing the two tinted buttons); the
  recent transactions sit in an `NPayCard` with `NPaySectionHeader` ("View All" → History tab).
- **BalanceCard**: background `NPayTheme.Colors.primary`, corner radius `NPayTheme.Radius.card`.
- **PaymentsScreen / PaymentReviewSheet / PaymentSuccessScreen**: Review Payment (with an icon), Confirm Demo Payment
  and Back to Dashboard are `NPayButton`s; their `.disabled(...)` modifiers stay.
- Not changed: `NPayButton` itself. The deck shows (and typechecks) an `@Environment(\.isEnabled)` fix for its disabled
  look but the integration keeps the text's component as written.

### DesignSystem (the text's code)

```swift
import SwiftUI

// DesignSystem/NPayTheme.swift (section 3)

enum NPayTheme {

    enum Colors {
        static let primary = Color(
            red: 0.10,
            green: 0.34,
            blue: 0.65
        )

        static let success = Color.green

        static let cardBackground =
            Color.blue.opacity(0.06)
    }

    enum Spacing {
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
    }

    enum Radius {
        static let small: CGFloat = 10
        static let card: CGFloat = 18
    }
}

// DesignSystem/NPayButton.swift (section 17)

struct NPayButton: View {
    let title: String
    let symbol: String?
    let action: () -> Void

    init(
        _ title: String,
        symbol: String? = nil,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.symbol = symbol
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                if let symbol {
                    Image(systemName: symbol)
                }

                Text(title)
            }
            .font(.headline)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(
            NPayTheme.Colors.primary,
            in: RoundedRectangle(
                cornerRadius: NPayTheme.Radius.small
            )
        )
    }
}

// DesignSystem/NPayCard.swift (section 7)

struct NPayCard<Content: View>: View {

    @ViewBuilder let content: Content

    var body: some View {
        content
            .padding(NPayTheme.Spacing.medium)
            .frame(maxWidth: .infinity)
            .background(
                NPayTheme.Colors.cardBackground,
                in: RoundedRectangle(
                    cornerRadius: NPayTheme.Radius.card
                )
            )
    }
}

// DesignSystem/NPayCardModifier.swift (section 9)

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

// DesignSystem/NPaySectionHeader.swift (section 10)

struct NPaySectionHeader: View {
    let title: String
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        HStack {
            Text(title)
                .font(.headline)

            Spacer()

            if let actionTitle,
               let action {
                Button(actionTitle, action: action)
                    .font(.subheadline)
            }
        }
    }
}
```

### Screens/HomeScreen.swift

```swift
import SwiftUI

struct HomeScreen: View {
    let store: NPayStore
    let router: NPayRouter

    var body: some View {
        ScrollView {
            VStack(spacing: NPayTheme.Spacing.large) {
                BalanceCard(balancePaise: store.balancePaise)

                NPayButton("Send Money", symbol: "arrow.up.right") {
                    router.select(.payments)
                }

                NavigationLink(value: NPayRoute.accountDetails) {
                    Label("Account Details", systemImage: "person.text.rectangle")
                        .frame(maxWidth: .infinity, alignment: .leading)
                }

                NPayCard {
                    VStack(alignment: .leading, spacing: 12) {
                        NPaySectionHeader(
                            title: "Recent Transactions",
                            actionTitle: "View All"
                        ) {
                            router.select(.history)
                        }

                        ForEach(store.transactions.prefix(3)) { transaction in
                            TransactionRow(transaction: transaction)
                        }
                    }
                }
            }
            .padding()
        }
        .navigationTitle("NPay")
    }
}
```

### Components/BalanceCard.swift

```swift
import SwiftUI

struct BalanceCard: View {
    let balancePaise: Int

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

            Text("NPay Demo Account")
                .font(.caption)
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

## Deck changes

The deck (`index.html`, built by `tools/gen3_7.py`, 47 slides) follows both pieces, grouped into 8 Parts: the milestone
(1), tokens (2–4), NPayButton (5, 6, 17, 18), NPayCard (7, 8, 15, 16), views and modifiers (9, 10), adapting (11, 19,
20), integration (12, 21), debugging and experiments (13, 22); then recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_7/`, rerun with `sh tools/sim3_7/run.sh`; built twice,
normally and with `-D ALTTOKENS`; light/dark via `simctl ui appearance`, text size via `simctl ui content_size`)
- Inferred types (`type(of:)`): `NPayCard<Text>`, `NPayCard<VStack<TupleView<(Text, Text)>>>`,
  `NPayCard<HStack<TupleView<(Image, Text)>>>`, `NPayCard<TupleView<(Text, Text)>>`, `AnyView`,
  `ModifiedContent<Text, NPayCardModifier>`.
- Experiments 1–2 as one rebuild (primary → teal, card radius 18 → 4): every token user changed; the text's
  `NPayCardModifier` (hardcoded 16/18) kept its radius. Catalog and Home screenshots.
- Dynamic Type: "Send Money" in `.system(size: 16)` 19.3 pt high at both the default and the largest accessibility
  size; `.headline` 24.3 → 74.7 pt. Catalog screenshot at the largest size.
- Dark mode: catalog and Home screenshots; the fixed primary is hard to read on black and the 6% card background nearly
  vanishes. WCAG contrast computed from sRGB: fixed primary 7.1:1 on white, 2.9:1 on black; our asset's dark variant
  8.6:1 on black.
- `_printChanges` in a traced copy of the first NPayButton: three lines at launch; after two unrelated parent updates
  (screen showed "Count: 2") only the button whose closure captures the counter re-ran (two more lines).
- Finding: `.disabled(!isValid)` on NPayButton dims only the label; the background stays full strength (Payments
  screenshots, empty vs valid form).
- The integrated payment flow (Review, Confirm, Back to Dashboard as NPayButtons) and Home light/dark/changed-token
  screenshots.

**Authored (flagged)**
- The integration (above); the `NPayPrimary` colour asset and its dark value (sRGB 0.45, 0.65, 1.00); the component
  catalog screen; the `-D ALTTOKENS` experiment values; `ErasedCard` (Section 16's type-erased card renamed so both
  compile together); the traced button with three closures; the `isEnabled` fix.
- Review: the text's 7 questions (options reordered) plus two predict items (disabled NPayButton; fixed font at the
  largest size) and a spaced item from 3.6; 3 of 10 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.8 and 3.9 as the text names them; Unit 4), lab, end slide.

**Wording**
- "Senior engineer insight / principle / knowledge check" and "Trainer question" became neutral callouts and "Check
  your understanding".
