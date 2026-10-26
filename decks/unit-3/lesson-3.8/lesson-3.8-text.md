# Unit 3 · Lesson 3.8 — Adaptive Layouts & GeometryReader

> Lesson text as shared, in two pieces: Sections 1–14 (cut off at the knowledge check) and "Part 2: Layout Internals,
> Experiments & Architecture Review" (Sections 14–21). Interactive widgets are described in brackets. The deck
> (`index.html`, built by `tools/gen3_8.py`) follows both. The text ends by naming its remaining implementation task
> (responsive quick actions in the 3.7 app); that integration is **authored** and listed at the end. Evidence and
> authored additions are listed under "Deck changes".

NPay iOS Engineering Masterclass · Incremental Development · SwiftUI Layout Engine · Responsive UI

In Lesson 3.7, we created reusable NPay components and design tokens. Now we'll solve a challenge every professional iOS developer faces: how can the same SwiftUI screen work correctly on a small iPhone, a large iPhone, an iPad, and with larger accessibility text? We won't just learn GeometryReader. We'll investigate how SwiftUI's layout engine measures and positions views, how parent and child views negotiate space, and how to build adaptive layouts.

## 1. Our NPay milestone

Currently, NPay's quick actions use a fixed horizontal layout.

```swift
HStack(spacing: 12) {
    QuickAction(title: "Send")
    QuickAction(title: "Request")
    QuickAction(title: "History")
}
```

This may work well on a wide screen. But on a narrow screen or with large Dynamic Type, the content may become cramped. Our goal is to make NPay adapt to the available space.

[NPay layout simulator: width slider (440 pt), "Simulate larger accessibility text"; NPay, Available Balance ₹25,000.00, Send Money / Request / History. "Current layout: Horizontal actions. This illustrates a width-aware layout policy, not the actual SwiftUI layout engine." Try reducing the width and enabling larger text. Notice how the action layout changes.]

## 2. First concept — SwiftUI's layout system

In UIKit, developers often think about frames and constraints. SwiftUI uses a proposal-based layout system. The essential model is:

[SwiftUI layout negotiation: Parent proposes a size (how much space is available?) → Child chooses its size (how much space does the content need?) → Parent places the child (where should the child appear?).]

This is a conceptual description of SwiftUI's layout protocol. The parent proposes dimensions, the child responds with a size, and the parent positions the child.

**Important insight.** A child view doesn't always occupy all available space. For example, `Text("NPay")` typically chooses a size based on its content and the proposed constraints.

## 3. First experiment — how does .frame() work?

Consider:

```swift
Text("NPay")
    .frame(width: 200, height: 80)
    .background(.blue.opacity(0.2))
```

This produces a framed layout around the text. But .frame() is not simply assigning a mutable UIView.frame property. It creates a modified SwiftUI view description that participates in layout.

**Compare two modifier orders**

```swift
// Example A

Text("NPay")
    .background(.blue)
    .frame(width: 200, height: 80)
```

```swift
// Example B

Text("NPay")
    .frame(width: 200, height: 80)
    .background(.blue)
```

The visual result differs because modifier order affects which layout region receives the background.

[Background first: "Background wraps the text's size." Frame first: "Background covers the framed region."]

**Trainer question.** Does modifier order matter only for colors? No. It can affect layout, hit testing, animation, and rendering behavior.

## 4. What is GeometryReader?

GeometryReader is a SwiftUI container that provides geometry information about the space offered to it. Example:

```swift
import SwiftUI

struct GeometryExperiment: View {
    var body: some View {
        GeometryReader { geometry in
            VStack {
                Text("Width: \(geometry.size.width)")
                Text("Height: \(geometry.size.height)")
            }
        }
    }
}

#Preview {
    GeometryExperiment()
}
```

The closure receives a GeometryProxy. The proxy exposes information such as the container's size and coordinate-space frames.

**What is GeometryProxy?** It is a SwiftUI type that provides access to geometry information during layout. Common properties and methods include `geometry.size`, `geometry.safeAreaInsets`, `geometry.frame(in: .local)`, `geometry.frame(in: .global)`.

## 5. Behind the scenes — how GeometryReader participates in layout

[GeometryReader layout flow: Parent proposes space (for example, 390 × 700 points) → GeometryReader receives proposal (it generally expands to the offered space) → GeometryProxy exposes geometry (child content can inspect size and coordinate information) → Content builds layout (NPay chooses layout based on available width) → SwiftUI positions and renders (the resulting view hierarchy is presented).]

**Important caution.** GeometryReader often takes all available space in its proposed dimensions. If used carelessly inside a ScrollView or VStack, it can produce unexpected layout behavior. We'll investigate that in an experiment.

## 6. Build adaptive NPay quick actions

Now let's replace our fixed quick-action layout.

```swift
import SwiftUI

struct NPayQuickActions: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        GeometryReader { geometry in
            let isCompact = geometry.size.width < 350

            Group {
                if isCompact {
                    VStack(spacing: 12) {
                        actions
                    }
                } else {
                    HStack(spacing: 12) {
                        actions
                    }
                }
            }
        }
        .frame(height: 180)
    }

    @ViewBuilder
    private var actions: some View {
        QuickAction(
            symbol: "arrow.up.right",
            title: "Send",
            action: onSend
        )

        QuickAction(
            symbol: "arrow.down.left",
            title: "Request",
            action: onRequest
        )

        QuickAction(
            symbol: "clock",
            title: "History",
            action: onHistory
        )
    }
}
```

**What did we introduce?** GeometryReader measures available width. A conditional layout chooses between HStack and VStack. @ViewBuilder composes reusable action views. The parent supplies behavior through closures.

**A limitation in this first experiment.** The fixed `.frame(height: 180)` is only a teaching shortcut. It may waste space in horizontal mode or clip content with larger text. We should improve it before using it in production.

## 7. Better solution — ViewThatFits

SwiftUI provides ViewThatFits, which can choose the first child view that fits the available space. For example:

```swift
ViewThatFits {
    HStack(spacing: 12) {
        Text("Send Money")
        Text("Request Money")
        Text("History")
    }

    VStack(spacing: 12) {
        Text("Send Money")
        Text("Request Money")
        Text("History")
    }
}
```

This avoids manually checking a fixed width threshold in some scenarios.

**Why is this better?** Because the decision can be based on whether the content fits, rather than assuming a particular device width. This is particularly useful with Dynamic Type.

**Important nuance.** ViewThatFits uses SwiftUI's layout fitting behavior. It doesn't simply compare screen width with a hardcoded breakpoint.

## 8. AnyLayout — switch layouts while preserving structure

SwiftUI also provides AnyLayout. We can choose between HStackLayout and VStackLayout dynamically.

```swift
struct AdaptiveActions: View {
    let compact: Bool

    var body: some View {
        let layout = compact
            ? AnyLayout(VStackLayout(spacing: 12))
            : AnyLayout(HStackLayout(spacing: 12))

        layout {
            Text("Send")
            Text("Request")
            Text("History")
        }
    }
}
```

**Why is this interesting?** Instead of having two separate branches that create different layout structures, we can switch the layout container while retaining the same child descriptions. This can help preserve view identity across layout changes. We'll explore this further in the next section.

## 9. AnyLayout versus conditional branches

Consider:

```swift
if compact {
    VStack {
        CounterView()
    }
} else {
    HStack {
        CounterView()
    }
}
```

These branches create different structural positions for CounterView. Depending on identity, its local state may reset when switching branches. Now compare:

```swift
let layout = compact
    ? AnyLayout(VStackLayout())
    : AnyLayout(HStackLayout())

layout {
    CounterView()
}
```

This keeps a more stable structural relationship for the child while changing the layout behavior.

**Connect to Lesson 3.5.** Remember that SwiftUI state lifetime is tied to view identity. Adaptive layout design should consider identity preservation, not only visual arrangement.

## 10. Safe areas — why doesn't content fill the entire screen?

iPhones have system-managed areas such as the status bar, home indicator region, and other interface boundaries. SwiftUI provides safe-area-aware layout behavior. Consider `VStack { Text("NPay") }`. By default, layout respects relevant safe-area constraints. But we can deliberately extend backgrounds: `Color.blue.ignoresSafeArea()`.

**Important distinction.** Extending a decorative background into the safe area is often appropriate. Placing interactive buttons underneath system gestures or camera cutouts is usually not.

## 11. Adaptive typography and Dynamic Type

Let's revisit Lesson 3.7. Using `.font(.headline)` allows the font to participate in Dynamic Type scaling. But using `.font(.system(size: 16))` does not automatically provide the same semantic scaling behavior.

**Better practice.** Prefer semantic styles where possible: `.font(.largeTitle)`, `.font(.title2)`, `.font(.headline)`, `.font(.body)`, `.font(.caption)`. Then test with larger accessibility text sizes.

**Why does this affect layout?** Text can occupy more width and height as the user increases font size. An HStack that fits at the default size may become cramped. That's why adaptive layouts should consider content requirements, not just device dimensions.

## 12. NPay integration — responsive dashboard

Let's create a reusable dashboard layout.

```swift
import SwiftUI

struct NPayDashboardLayout<Content: View>: View {
    @ViewBuilder let content: Content

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 16) {
                content
            }

            VStack(spacing: 16) {
                content
            }
        }
    }
}
```

This demonstrates adaptive composition, although for complex content we'll often prefer more explicit layout components.

**Trainer question.** Is ViewThatFits always the best adaptive layout solution? No. For complex responsive designs, custom Layout implementations, AnyLayout, grid containers, and size-class-aware structures may be more appropriate.

## 13. Xcode experiments

Try these in your NPay project: (1) Use GeometryReader to display the available width. (2) Rotate the Simulator and observe the width change. (3) Compare HStack and VStack for quick actions. (4) Replace the conditional branches with AnyLayout. (5) Increase Dynamic Type and observe whether controls remain readable. (6) Test `.ignoresSafeArea()` on a background. (7) Place GeometryReader inside a ScrollView without a height constraint and investigate the resulting layout.

**Debugging tip.** You can add temporary borders, `.border(.red)`, to visualize the boundaries of layout containers. This is useful when diagnosing unexpected spacing and frame behavior.

## Part 2: Layout Internals, Experiments & Architecture Review

NPay Engineering Lab · Continuing from Section 14. We've explored GeometryReader, ViewThatFits, AnyLayout, safe areas, and Dynamic Type. Now we'll complete the senior-engineer assessment and investigate a particularly important concept: how SwiftUI negotiates layout without using fixed screen coordinates.

## 14. Senior engineer knowledge check

[Adaptive Layout Engineering Assessment, 0 / 6 answered.]
1. What is SwiftUI's core layout negotiation model? (Parent proposes, child chooses, parent places / Every view uses absolute coordinates / Only Auto Layout constraints)
2. What does GeometryReader provide? (Geometry information from its layout context / Network data / Persistent storage)
3. Why can GeometryReader be problematic inside ScrollView? (Its sizing behavior can interact unexpectedly with scroll-axis proposals / It always crashes / It disables SwiftUI)
4. What is ViewThatFits useful for? (Choosing content that fits available space / Persisting payment data / Routing between screens)
5. Why use AnyLayout? (To switch layout algorithms while retaining child structure / To erase application state / To create threads)
6. Does a fixed screen-width breakpoint always account for Dynamic Type? (Yes / No)

## 15. The deeper question — what does "proposed size" mean?

Imagine NPay's dashboard has 390 points of available width. A parent container proposes space to its children. The child decides how much of that space it needs, subject to its own layout behavior. For example, `Text("NPay")`: the text usually chooses a size based on its content and font. But `Text("NPay").frame(maxWidth: .infinity)` allows the modified view to expand within the proposed space.

[Interactive layout proposal explorer: available parent width 320 pt; "Apply frame(maxWidth: .infinity)"; "Blue region represents the modified text view's illustrative width."]

**Important insight.** `.frame(maxWidth: .infinity)` doesn't mean the view becomes infinitely wide. It means the frame can expand to the available proposed width.

## 16. Why GeometryReader sometimes behaves unexpectedly

Consider:

```swift
ScrollView {
    GeometryReader { geometry in
        Text("Width: \(geometry.size.width)")
    }
}
```

You might expect GeometryReader to fill the entire visible scroll area. But a vertical ScrollView can propose an unspecified height to its content along the scrolling axis. GeometryReader has its own ideal-size behavior when receiving unspecified dimensions. This can result in a surprisingly small height.

**Better approach for our NPay experiment.** Give it an explicit height:

```swift
ScrollView {
    GeometryReader { geometry in
        Text("Width: \(geometry.size.width)")
    }
    .frame(height: 100)
}
```

This gives the geometry reader a predictable vertical region.

**Senior engineer principle.** Use GeometryReader when you genuinely need geometry information. Don't use it as the default container for every responsive layout.

## 17. ViewThatFits — why it can be better than screen-width checks

Suppose our NPay quick actions contain labels of different lengths. At normal text size, an HStack may fit. At larger Dynamic Type sizes, it may not. If we use only `geometry.size.width < 350`, we're assuming that 350 points is the correct breakpoint for every text size and language. That assumption can fail.

**Alternative**

```swift
ViewThatFits(in: .horizontal) {
    HStack(spacing: 12) {
        Text("Send Money")
        Text("Request Money")
        Text("History")
    }

    VStack(spacing: 12) {
        Text("Send Money")
        Text("Request Money")
        Text("History")
    }
}
```

The layout can choose the first candidate that fits according to the specified axes.

**Important nuance.** ViewThatFits evaluates candidate layouts according to their ideal sizing behavior. It isn't a universal overflow detector. Some flexible content may report that it fits while compressing or truncating. We still need to test the actual UI.

## 18. AnyLayout and state identity

Let's connect adaptive layout to Lesson 3.5. Consider a counter with local state.

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        Button("Count: \(count)") {
            count += 1
        }
    }
}
```

Now imagine switching between HStack and VStack. If we conditionally create entirely different structural branches, the counter's identity may change. Using AnyLayout can preserve the child structure while changing layout behavior.

```swift
struct LayoutIdentityExperiment: View {
    @State private var vertical = false

    var body: some View {
        let layout = vertical
            ? AnyLayout(VStackLayout())
            : AnyLayout(HStackLayout())

        VStack(spacing: 20) {
            layout {
                CounterView()
            }

            Button("Switch Layout") {
                vertical.toggle()
            }
        }
    }
}
```

**Practice.** Increment the counter. Switch the layout. Observe whether the count remains. This experiment demonstrates how layout changes and identity preservation interact.

## 19. Build a better NPay quick-action layout

Our earlier version used a fixed-height GeometryReader. Let's improve it using ViewThatFits.

```swift
import SwiftUI

struct NPayQuickActions: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) {
                actionViews
            }

            VStack(spacing: 12) {
                actionViews
            }
        }
    }

    @ViewBuilder
    private var actionViews: some View {
        QuickAction(
            symbol: "arrow.up.right",
            title: "Send",
            action: onSend
        )

        QuickAction(
            symbol: "arrow.down.left",
            title: "Request",
            action: onRequest
        )

        QuickAction(
            symbol: "clock",
            title: "History",
            action: onHistory
        )
    }
}
```

This is a better starting point because we no longer require a fixed-height geometry reader. However, we should still test it at large Dynamic Type sizes and in localized languages.

## 20. Responsive design isn't only about width

| Factor | Example |
|---|---|
| Available width | Small versus large iPhone |
| Orientation | Portrait versus landscape |
| Dynamic Type | Larger accessibility text |
| Safe areas | Status bar and home indicator |
| Localization | Longer translated labels |
| Keyboard | Reduced visible content area |
| Multitasking | Variable window size on iPad |

**Important distinction.** A responsive layout isn't simply a collection of hardcoded device breakpoints. It should adapt to the actual content and available space.

## 21. Xcode verification lab

Use the Simulator and SwiftUI previews.

[Lesson 3.8 practical checklist, 0 / 8]
- [ ] Test NPay on a smaller iPhone simulator
- [ ] Test on a larger iPhone simulator
- [ ] Rotate the simulator to landscape
- [ ] Increase Dynamic Type in accessibility settings
- [ ] Compare GeometryReader and ViewThatFits
- [ ] Switch between HStackLayout and VStackLayout using AnyLayout
- [ ] Verify CounterView state survives the layout switch
- [ ] Check that buttons remain usable and text is readable

**Lesson 3.8 checkpoint.** We've completed the conceptual lesson on SwiftUI's layout proposal system, GeometryReader, ViewThatFits, AnyLayout, safe areas, Dynamic Type, and adaptive design. The remaining implementation task is to integrate the responsive quick actions and layout improvements into the complete NPay application from Lesson 3.7.

Next — Lesson 3.9: SwiftUI Environment & Preferences. We'll explore environment propagation, custom environment values, theme management, @Environment, @EnvironmentObject, and how NPay can share configuration across its screens without manually passing every value through multiple view layers.

## Integration through Lesson 3.8 (authored)

The remaining task, done on the Lesson 3.7 code and run in the simulator (`tools/sim3_8/App.swift`):
- **Components/QuickAction.swift**: Lesson 2.7's QuickAction (symbol, title, action), which the text uses; it had been
  dropped with the 3.3 project structure.
- **Components/NPayQuickActions.swift**: the Section 19 (ViewThatFits) version.
- **HomeScreen**: NPayQuickActions replaces the single Send Money button. Send selects the Payments tab, History the
  History tab; Request, which the demo doesn't have, shows an alert saying so.
- Not fixed: at the largest accessibility text size BalanceCard wraps the amount ("₹25,000.0" / "0"). Shown on a slide
  and left as the lab's last step.

### Components

```swift
import SwiftUI

// Components/QuickAction.swift (Lesson 2.7's component, back for the quick actions)

struct QuickAction: View {
    let symbol: String
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: symbol)
                    .font(.title2)

                Text(title)
                    .font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(.blue)
        .background(
            Color.blue.opacity(0.08),
            in: RoundedRectangle(cornerRadius: 12)
        )
    }
}

// Components/NPayQuickActions.swift (section 19)

struct NPayQuickActions: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) {
                actionViews
            }

            VStack(spacing: 12) {
                actionViews
            }
        }
    }

    @ViewBuilder
    private var actionViews: some View {
        QuickAction(
            symbol: "arrow.up.right",
            title: "Send",
            action: onSend
        )

        QuickAction(
            symbol: "arrow.down.left",
            title: "Request",
            action: onRequest
        )

        QuickAction(
            symbol: "clock",
            title: "History",
            action: onHistory
        )
    }
}
```

### Screens/HomeScreen.swift

```swift
import SwiftUI

struct HomeScreen: View {
    let store: NPayStore
    let router: NPayRouter

    @State private var showRequestInfo = false

    var body: some View {
        ScrollView {
            VStack(spacing: NPayTheme.Spacing.large) {
                BalanceCard(balancePaise: store.balancePaise)

                NPayQuickActions(
                    onSend: { router.select(.payments) },
                    onRequest: { showRequestInfo = true },
                    onHistory: { router.select(.history) }
                )

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
        .alert("Request money", isPresented: $showRequestInfo) {
            Button("OK", role: .cancel) {}
        } message: {
            Text("Requests aren't part of the demo yet.")
        }
    }
}
```

## Deck changes

The deck (`index.html`, built by `tools/gen3_8.py`, 45 slides) follows both pieces, grouped into 8 Parts: the milestone
(1), the layout negotiation (2, 15), frames and order (3), GeometryReader (4, 5, 13, 16), adaptive quick actions (6, 7,
17, 19), AnyLayout and identity (8, 9, 18), beyond width (10, 11, 20), NPay responsive (12, 13, 21 and the
integration); then recap, review, next, lab, end.

**Evidence** (iOS 26.5 simulators: iPhone 17, iPhone SE (3rd generation) and iPad Air 11-inch, the last two created by
`tools/sim3_8/run.sh`; text size via `simctl ui content_size` (default and accessibility-extra-extra-extra-large);
landscape via `UIWindowScene.requestGeometryUpdate`; the app declares iPhone and iPad (`UIDeviceFamily`), otherwise the
iPad runs it in a 320 × 435 iPhone-compatibility window)
- A logging `Layout` (authored) around three children in a 320 × 300 VStack: the VStack probes each child with heights
  0 and ∞, then makes final proposals. `Text("NPay")` 39 × 24; `.frame(maxWidth: .infinity)` 320 × 24; `Color.blue`
  takes what it is offered (0, ∞, then 203).
- Modifier order (Section 3): screenshot of examples A and B with a red border on the frame.
- GeometryExperiment: 402 × 778 (iPhone 17), 750 × 382 (landscape), 375 × 647 (SE), 820 × 1128 (iPad Air).
- GeometryReader in a ScrollView with no height: 402 × 10; with `.frame(height: 100)`: 402 × 100.
- NPayQuickActions, both versions, arrangement read from the buttons' accessibility frames: the 350-pt GeometryReader
  version kept a row at 370 pt with the largest text (labels truncated to "Req…", "Hist…") and stacked on the SE at 343
  pt, where the 180-pt frame clipped the third button; the ViewThatFits version kept a row on the SE and switched to a
  column at the largest size; both rows on iPad and in landscape.
- CounterView: AnyLayout kept Count: 3 across the switch; the if/else branches reset it to 0.
- iPad Air: `requestGeometryUpdate` to landscape failed with "The current windowing mode does not allow for
  programmatic changes to interface orientation."
- Safe-area screenshot (default vs `.ignoresSafeArea()`); Home on the SE, at the largest text size (balance wraps), in
  landscape, and on iPad.

**Authored (flagged)**
- The integration (above), the logging Layout, the safe-area lab layout, `BranchIdentityExperiment` (Section 9's
  branches made runnable), `NPayQuickActionsGeo` (Section 6's version renamed so both versions compile).
- Section 5's flow shown as a stepped diagram.
- Review: the text's 6 questions (options reordered) plus three predict items (the SE breakpoint; GeometryReader in a
  ScrollView; branches and the counter) and a spaced item from 3.7; 1 of 10 verdicts is "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.9 as the text names it; 3.10 accessibility as Lesson 3.6
  names it), lab, end slide.

**Wording**
- "Trainer question", "Senior engineer principle / knowledge check" became neutral callouts and "Check your
  understanding".
