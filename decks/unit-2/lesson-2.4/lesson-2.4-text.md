# Unit 2 · Lesson 2.4 — HStack, Horizontal Layout & Spacer

> Lesson text as shared. Interactive widgets (layout explorer, Spacer checkbox, alignment buttons, quiz) are
> described in brackets. The deck (`index.html`, built by `tools/gen2_4.py`) follows Sections 1–11. Simulator
> evidence and authored additions are listed at the end under "Deck changes".

NPay Engineering Lab · SwiftUI Layout Internals · Incremental Development

In Lesson 2.3, we learned how VStack arranges views vertically, how @ViewBuilder constructs child content, and how SwiftUI negotiates layout sizes.

Now NPay needs its first horizontal interface.

Our engineering challenge: **How do we arrange payment actions side by side, give them appropriate spacing, and make them adapt to different iPhone screen sizes?**

We'll investigate HStack, Spacer, layout proposals, alignment, and flexible space—all while improving our existing NPay application.

## 1. Our next NPay milestone

We already have a welcome screen with an icon, title, and subtitle. Now we want three quick-action labels: Send, Request, History. [Mock-up: the welcome screen with a row of three actions below it.]

**Milestone 2.4 — Horizontal quick-action layout.** For now, these are visual elements, not interactive buttons. We'll add button behavior in Lesson 2.7.

## 2. What exactly is HStack?

```swift
HStack(spacing: 20) {
    Text("Send")
    Text("Request")
    Text("History")
}
```

Like VStack, HStack is a generic SwiftUI struct conforming to View. A simplified initializer looks like:

```swift
// Conceptual API signature

init(
    alignment: VerticalAlignment = .center,
    spacing: CGFloat? = nil,
    @ViewBuilder content: () -> Content
)
```

Notice the difference from VStack.

| Feature | VStack | HStack |
|---|---|---|
| Main axis | Vertical | Horizontal |
| Cross-axis alignment | HorizontalAlignment | VerticalAlignment |
| Spacing | Between vertical children | Between horizontal children |
| Content | @ViewBuilder closure | @ViewBuilder closure |

The trailing closure constructs the child content. The initializer produces an `HStack<Content>` value.

**Trainer question.** Does the closure return the HStack itself? No. The closure produces the child content, and the initializer constructs the stack.

## 3. First experiment — change VStack to HStack

```swift
import SwiftUI

struct ContentView: View {
    var body: some View {
        HStack(spacing: 20) {
            Text("Send")
            Text("Request")
            Text("History")
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
```

Observe how the three text views appear horizontally. Now change `spacing: 20` to `spacing: 0`, then `spacing: 40`.

**What changes?** The horizontal distance between adjacent children. spacing doesn't automatically add padding around the entire row.

## 4. Behind the scenes — HStack's layout negotiation

SwiftUI layout uses size proposals. For a horizontal stack, the container must decide how to distribute available width among its children. Conceptually:

1. Parent proposes available size — for example, a width of 350 points.
2. HStack considers spacing — two gaps of 20 points consume 40 points.
3. Children receive layout proposals — SwiftUI considers each child's sizing behavior and flexibility.
4. Children choose sizes — Text, images and other views report their sizes.
5. HStack positions children — views are arranged horizontally with alignment and spacing.

Simplified teaching model. SwiftUI's stack layout accounts for flexibility, ideal sizes, priorities, and other constraints.

**A simple numerical example.** Suppose the parent proposes 350 points of width. There are three child views and two 20-point gaps. The total spacing is 2 × 20 = 40. The remaining width available for child allocation is 350 − 40 = 310 points. That does not mean SwiftUI automatically assigns 103.3 points to every child. Each child has its own sizing behavior.

## 5. Interactive HStack layout explorer

[Proposed width 350 pt, spacing 20 pt; Send / Request / History; width remaining after gaps: 310 pt. Illustrative equal-flex layout, not the exact intrinsic sizing behavior of unmodified SwiftUI Text views.]

**Trainer insight.** In the simulator above, the children are deliberately given equal flexible widths. A plain SwiftUI HStack containing Text views does not necessarily distribute space equally. This distinction is important when designing reusable layouts.

## 6. What is Spacer?

Now suppose we want the NPay title on the left and an account icon on the right.

```swift
HStack {
    Text("NPay")

    Spacer()

    Image(systemName: "person.circle")
}
```

Spacer is a SwiftUI view that expands along the stack's main axis when space is available.

**How does Spacer work internally?** Spacer participates in layout as a flexible view. It doesn't create visible content by itself. The stack can allocate remaining space to it, subject to layout constraints.

**Trainer question.** Is `Spacer()` the same as `.padding(20)`? No. Padding adds a specified amount of space around a view. A Spacer is flexible and can expand to consume available space.

## 7. Interactive Spacer experiment

[Checkbox "Include Spacer()": NPay and the profile icon; Spacer expands between the title and profile icon.]

## 8. Alignment — why HStack uses VerticalAlignment

```swift
HStack(alignment: .top, spacing: 20) {
    Text("Send")
        .font(.largeTitle)

    Text("Request")
        .font(.caption)
}
```

The two text views have different heights. `alignment: .top` aligns their top edges. `alignment: .center` aligns their vertical centers. `alignment: .bottom` aligns their bottom edges. [Top / Center / Bottom buttons.]

**Why does alignment matter?** When child views have different sizes, their vertical placement can significantly affect the appearance of the row. SwiftUI also supports text-baseline alignment, which is especially useful when aligning text with different font sizes. We'll explore baseline alignment in a later layout experiment.

## 9. What happens when the screen is too narrow?

Now imagine NPay runs on a smaller iPhone. Our three actions may no longer fit comfortably. SwiftUI must resolve the layout under the available width constraints. Possible outcomes include text compression, truncation, wrapping, or other adjustments depending on the child views and their modifiers.

**Introducing layout priority.** SwiftUI provides `.layoutPriority(1)`. This can influence how space is allocated among competing views. For example:

```swift
HStack {
    Text("Available Balance")
        .layoutPriority(1)

    Text("₹25,000")
}
```

The higher-priority view receives preference during layout negotiation.

**Trainer insight.** layoutPriority is not a universal instruction to make a view larger. It influences layout decisions when space is constrained.

## 10. Build our NPay quick-action row

We'll keep the existing welcome screen and add three visual quick actions.

```swift
import SwiftUI

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

#Preview {
    ContentView()
}
```

What did we introduce?
- HStack arranges the three actions horizontally.
- Each action uses a nested VStack for icon-over-label layout.
- The parent stack controls the vertical arrangement of the entire screen.
- Shared modifiers on the HStack can influence its descendants through SwiftUI's styling environment.

**Why does .font(.subheadline) affect the child views?** Font is an environment-driven style in SwiftUI. A font modifier applied to a container can influence descendants that don't override it. This is an important concept that we'll explore deeply in the modifiers lesson.

## 11. Senior engineer knowledge check

1. What is HStack? — A Swift function / **A generic struct conforming to View** / A UIKit controller
2. Does HStack distribute equal widths to every child by default? — Yes / **No**
3. What does Spacer do? — Adds a fixed 20-point gap / **Expands flexibly when space is available**
4. Which alignment type does HStack use? — HorizontalAlignment / **VerticalAlignment**
5. Does layoutPriority guarantee a fixed width? — Yes / **No**

(Answers in bold were not marked in the shared text; they follow from the lesson.)

**Lesson 2.4 complete.** We've added a horizontal quick-action row to NPay and learned how HStack, Spacer, alignment, layout priorities, and flexible space work.

Next — Lesson 2.5: ZStack and Layered Layouts. We'll build NPay's first balance card by placing text and icons over a colored background, then investigate Z-axis ordering, layout sizing, overlays, backgrounds, and how SwiftUI composes layered content.

## Deck changes

The deck (`index.html`, built by `tools/gen2_4.py`, 33 slides) follows Sections 1–11, grouped into 7 Parts:
the milestone (1), HStack (2–3), sharing out width (4–5), Spacer (6–7), vertical alignment (8), when space runs out (9),
NPay quick actions (10); then recap, review (11), next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_4/`, rerun with `sh tools/sim2_4/run.sh`)
- Section 2: the text's conceptual `init` is replaced by the real SDK declaration `@frozen public struct HStack<Content> : View` with `init(alignment: VerticalAlignment = .center, spacing:content:)`; printed type `HStack<TupleView<(Text, Text, Text)>>`.
- Section 3: rows measured at spacing 0 / 20 / 40: 156.7 / 196.7 / 236.7 pt (two gaps), with a screenshot.
- Sections 4–5: the browser explorer (equal flexible widths) is replaced by both cases in a 350 pt stack: plain Texts took 39.3, 62.7 and 54.7 pt; with `.frame(maxWidth: .infinity)` each took 103.3 pt (310 ÷ 3).
- Sections 6–7: the checkbox experiment is replaced by screenshots with and without Spacer (shown at `.title2`): the row grew from 84.3 to 370.0 pt; printed type `HStack<TupleView<(Text, Spacer, Image)>>`.
- Section 8: the alignment buttons are replaced by a screenshot of `.top`, `.center`, `.bottom`.
- Section 9: the balance row squeezed into 200 pt (at `.title3`): without priority the label wrapped (82.3 pt) and the amount kept one line; with `.layoutPriority(1)` on the label it kept one line (152 pt) and the amount wrapped ("₹25," / "000"). This shows that priority is not "bigger".
- Section 10: before/after screenshots; only the new HStack is shown on the slide (the full code is in the text and the lab). `type(of: row.font(.subheadline))` printed `ModifiedContent<HStack<…>, _EnvironmentKeyWritingModifier<Optional<Font>>>`, linking the environment explanation to Lesson 2.2.

**Authored (flagged)**
- Section 4's five steps are drawn as a stepper (the text lists them as a flow).
- A "Spacer vs padding" comparison slide built from the text's answer.
- Review: the text's 5 questions (answers authored), plus a predict-the-width item and a spaced item from 2.3.
- Outcomes, "Where we are", recap, "Where this goes next" (2.5 and 2.7, both named in the text), lab with expected results.

**Wording**
- "Trainer question" / "Trainer insight" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding".
