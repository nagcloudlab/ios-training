# Unit 2 · Lesson 2.3 — VStack & @ViewBuilder Internals

> Lesson text as shared (in two parts: Sections 1–15, then "Part 2" continuing at Section 15). Interactive widgets
> (spacing explorer, alignment buttons, layout calculator, quiz) are described in brackets. The deck (`index.html`,
> built by `tools/gen2_3.py`) follows Sections 1–20. Simulator evidence and authored additions are listed at the end
> under "Deck changes".

NPay Engineering Lab · Swift Generics → Closures → Result Builders → Layout Engine

In Lesson 2.1, we created `Text("NPay")`. In Lesson 2.2, we added `Image(systemName: "creditcard.fill")`.

Now we have two independent SwiftUI views. How do we arrange them vertically, control the space between them, and understand what SwiftUI does internally?

Today we'll investigate VStack, including its initializer, generic type, trailing closure, @ViewBuilder, and layout negotiation.

## 1. The problem — NPay needs a vertical layout

[Our components: the card symbol and NPay. Desired layout: the symbol above NPay.]

We need a container that arranges its children vertically. SwiftUI provides VStack.

```swift
VStack(spacing: 20) {
    Image(systemName: "creditcard.fill")
    Text("NPay")
}
```

But what exactly is this expression? Is VStack a function? Is the content a closure? How does a closure return two views? Let's investigate.

## 2. First important correction — VStack is not a function

`VStack(spacing: 20) { // Content }` looks like a function call. But VStack is a generic struct. We're calling its initializer. A simplified version of the actual initializer looks like:

```swift
// Simplified representation of SwiftUI's API

struct VStack<Content: View>: View {

    init(
        alignment: HorizontalAlignment = .center,
        spacing: CGFloat? = nil,
        @ViewBuilder content: () -> Content
    )
}
```

This reveals four important concepts:
- VStack is a struct.
- Content is a generic type parameter.
- spacing is an initializer argument.
- content is a closure annotated with @ViewBuilder.

**Connect to Unit 1.** Remember our own Swift struct:

```swift
struct Account {
    let balance: Int

    init(balance: Int) {
        self.balance = balance
    }
}

let account = Account(balance: 25000)
```

`Account(balance:)` calls an initializer. Likewise, `VStack(spacing:)` calls a generic struct initializer.

## 3. How does the trailing closure work?

```swift
VStack(spacing: 20) {
    Text("NPay")
}
```

Swift supports trailing closure syntax when a function or initializer accepts a closure argument. Conceptually, this is equivalent to:

```swift
VStack(
    spacing: 20,
    content: {
        Text("NPay")
    }
)
```

The closure supplies the child content.

**Important distinction.** The closure does not return a VStack. It returns the Content value that the VStack initializer uses. The initializer produces the `VStack<Content>` value. [Diagram: VStack initializer → content closure → Content → `VStack<Content>` value.]

## 4. The mystery — how can a closure return multiple views?

Normally, a Swift closure returns one result. For example:

```swift
let calculate = {
    10 + 20
}

print(calculate()) // 30
```

Now consider:

```swift
VStack {
    Text("NPay")
    Image(systemName: "creditcard.fill")
}
```

There are two expressions. How can one closure produce both? The answer is @ViewBuilder.

## 5. What is @ViewBuilder?

@ViewBuilder is a Swift result builder used by SwiftUI. It allows us to write multiple view expressions in a declarative block and have them combined into a single composite view value.

[What @ViewBuilder does conceptually: source expressions (Image · Text · Button) → @ViewBuilder transformation → one composite Content value → `VStack<Content>`.]

**Is it an array?** No. @ViewBuilder does not simply create `[View]`. It builds a strongly typed composite view representation. For simple multiple-child cases, you may encounter tuple-based view content internally. SwiftUI's exact representation and optimization details can vary by framework version.

**Trainer insight.** @ViewBuilder is a language-supported transformation applied at compile time. It isn't a runtime loop that discovers child views through reflection.

## 6. Let's create our own result builder

Before studying SwiftUI's builder further, let's understand the underlying Swift language feature.

```swift
@resultBuilder
struct StringBuilder {

    static func buildBlock(
        _ parts: String...
    ) -> String {
        parts.joined(separator: " ")
    }
}

func makeMessage(
    @StringBuilder content: () -> String
) -> String {
    content()
}

let message = makeMessage {
    "Welcome"
    "to"
    "NPay"
}

print(message)
// Welcome to NPay
```

This is a simplified result builder. It combines multiple expressions into one result. SwiftUI's @ViewBuilder uses the same general language mechanism, but supports a much richer set of view-composition rules.

## 7. How does Swift determine the generic Content type?

For `VStack { Text("NPay") }`, the compiler can infer that the content closure produces Text. So the resulting stack has a concrete generic type conceptually like `VStack<Text>`.

Now add another child (`Text("NPay")`, `Image(systemName: "creditcard.fill")`). The builder combines the children into a composite content type. The resulting VStack is still strongly typed.

**Why is this important?** SwiftUI uses compile-time type information extensively. This supports static checking and opportunities for efficient view composition. It also explains why complex SwiftUI expressions can sometimes produce long compiler diagnostics.

## 8. Behind the scenes — how does VStack arrange children?

Now let's move from Swift language internals to SwiftUI layout internals. VStack is a layout container. Its job is to arrange child views along a vertical axis. The simplified process:

1. Receive a size proposal from its parent.
2. Determine the space needed by its children.
3. Account for spacing and layout priorities.
4. Choose its own size.
5. Position children vertically.

[Interactive VStack spacing explorer: a 45 pt slider. Increasing spacing adds separation between the arranged children. It doesn't directly change the children's own content. Visual approximation.]

**Important nuance.** `spacing: 20` specifies the spacing between adjacent arranged child views. It doesn't automatically add 20 points of padding around the entire stack. Padding and spacing solve different layout problems.

## 9. spacing versus .padding()

```swift
VStack(spacing: 20) {
    Text("NPay")
    Text("Payments made simple")
}
.padding(30)
```

Here:
- `spacing: 20` controls separation between the two children.
- `.padding(30)` adds 30 points of space around the resulting stack's content region.

**Trainer question.** Does `.padding()` get called on the content closure? No. The closure produces the child content. VStack produces a view value. `.padding()` is then called on that resulting view. This connects directly to your earlier question about trailing closures and modifiers.

## 10. How does alignment work?

```swift
VStack(
    alignment: .leading,
    spacing: 20
) {
    Text("NPay")
    Text("Payments made simple")
}
```

`.leading` is a static member resolved through the expected HorizontalAlignment type. It controls how the children align along the horizontal axis of the vertical stack. [Leading / Center / Trailing buttons over "NPay", "Payments made simple", "Fast and secure".]

**Why is it called HorizontalAlignment?** Because VStack arranges children vertically. Its cross-axis alignment is horizontal. For HStack, the cross-axis alignment is vertical.

## 11. The subtle problem — why doesn't VStack always fill the screen?

`VStack { Text("NPay") }` doesn't necessarily occupy all available screen space. Its ideal size is influenced by its children and the parent's proposed size.

Now apply `.frame(maxWidth: .infinity, maxHeight: .infinity)`. This can make the modified view expand to fill available space under a suitable parent proposal. We'll explore frame modifiers in depth later.

**Trainer insight.** A common beginner mistake is assuming that every container automatically fills its parent. SwiftUI layout is proposal-driven, not simply equivalent to CSS block layout.

## 12. Our NPay implementation — Lesson 2.3

```swift
import SwiftUI

struct ContentView: View {

    var body: some View {
        VStack(
            alignment: .center,
            spacing: 20
        ) {
            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)

            Text("NPay")
                .font(.largeTitle)
                .bold()
                .foregroundStyle(.blue)

            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}

#Preview {
    ContentView()
}
```

What changed? We kept the existing NPay image and title. We explicitly configured VStack alignment and spacing. We added a subtitle. We also applied padding to the complete stack.

**Milestone 2.3 — Structured NPay welcome screen.**

## 13. Deep experiment — inspect the actual generic type

Inside a suitable SwiftUI-capable context, try:

```swift
let stack = VStack(spacing: 20) {
    Text("NPay")
    Text("Payments made simple")
}

print(type(of: stack))
```

You may see a generic type representation containing VStack and a composite content type. The exact printed name can vary by compiler and SwiftUI version.

**What does this prove?** VStack is not a dynamically assembled collection of arbitrary objects. It is a concrete generic Swift type whose content is constructed through @ViewBuilder.

## 14. Performance discussion — are nested stacks expensive?

```swift
VStack {
    VStack {
        Text("NPay")
    }
}
```

Is nesting stacks always bad? No. SwiftUI is designed for compositional layouts. The real performance cost depends on the view hierarchy, layout complexity, dependencies, and rendering behavior. Avoid premature optimization based only on the number of VStack declarations. For complex layouts, we should profile and investigate actual bottlenecks.

## 15. Senior engineer knowledge check (Part 2 begins here)

*Lesson 2.3 — Part 2: VStack Internals, Experiments & Assessment.* We've learned that VStack is a generic struct, its trailing closure builds child content through @ViewBuilder, and SwiftUI handles the vertical layout. Let's complete the knowledge check, then investigate two important behaviors: layout proposals and how SwiftUI handles changes to a stack's content.

1. What is VStack? — A Swift function / **A generic struct conforming to View** / A UIKit class
2. What does the trailing closure supply? — The VStack itself / **The child Content value** / The app's main function
3. What is @ViewBuilder? — A runtime reflection API / **A Swift result builder** / A memory allocator
4. Does @ViewBuilder simply return an array of View values? — Yes / **No**
5. What does VStack spacing control? — **Distance between arranged children** / Padding around the entire stack / Font size
6. What does `VStack(alignment: .leading)` configure? — Vertical alignment / **Horizontal alignment of children** / Text color
7. Does `.padding()` outside the VStack closure modify the closure? — Yes / **No**
8. Does VStack always fill its parent's entire height? — Yes / **No**

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 16. Behind the scenes — VStack's layout negotiation

```swift
VStack(spacing: 20) {
    Text("NPay")
        .font(.largeTitle)

    Text("Payments made simple")
        .font(.subheadline)
}
```

How does SwiftUI decide the stack's height? A simplified model is H_stack ≈ H₁ + H₂ + S, where H₁ and H₂ are the arranged children's heights, and S is the spacing between them.

For example, if the children choose heights of 41 and 20 points, with 20 points of spacing: H_stack = 41 + 20 + 20 = 81 points. This is an illustrative calculation. Real SwiftUI layout also considers proposals, flexibility, priorities, and other constraints.

[Interactive layout calculator: title 41 pt, subtitle 20 pt, spacing 20 pt → 81 pt.]

**Trainer insight.** This is why a VStack doesn't need explicit Y coordinates for each child. The layout container calculates positions based on child sizes, spacing, and alignment.

## 17. What happens if one child changes size?

Imagine NPay supports Dynamic Type. The user increases the system's preferred text size. The title and subtitle may become taller. SwiftUI's layout system can measure them again and update their positions.

Text size preference changes → environment information changes → text layout changes (text may require different dimensions) → VStack reevaluates layout (child sizes and spacing are considered) → children receive updated positions (layout responds to the new sizes).

**Important distinction.** A layout update doesn't necessarily require recreating the application process or rebuilding the app. This happens within the running SwiftUI interface.

## 18. Experiment — use .border() to see layout boundaries

```swift
VStack(spacing: 20) {
    Image(systemName: "creditcard.fill")
        .font(.system(size: 64))
        .border(.red)

    Text("NPay")
        .font(.largeTitle)
        .border(.green)

    Text("Payments made simple")
        .border(.orange)
}
.border(.blue)
.padding()
```

The borders reveal the approximate layout rectangles for the child views and their container. Try changing spacing from 20 to 50. You'll see the separation between children increase.

**Trainer question.** Does `.border(.blue)` draw a border around the entire iPhone screen? No. It draws a border around the view's layout region at that point in the modifier chain.

## 19. Experiment — understand modifier placement

Version A: Padding on the stack

```swift
VStack(spacing: 20) {
    Text("NPay")
    Text("Payments made simple")
}
.padding(30)
.background(.yellow)
```

Version B: Padding on each child

```swift
VStack(spacing: 20) {
    Text("NPay")
        .padding(30)

    Text("Payments made simple")
        .padding(30)
}
.background(.yellow)
```

These are not equivalent. Version A adds padding around the entire stack. Version B adds padding around each child, which affects their individual layout sizes and the overall stack size.

**What to observe.** In Version B, the stack becomes significantly taller because each child includes its own padding. This demonstrates that modifiers affect layout composition.

## 20. Final NPay code for Lesson 2.3

After completing the experiments, restore the clean version (the same code as Section 12).

**Lesson 2.3 complete.** You should now be able to explain:
- Why VStack is a generic struct rather than a function.
- How trailing closure syntax supplies its child content.
- How @ViewBuilder combines multiple view expressions.
- How the compiler infers `VStack<Content>`.
- How vertical layout, spacing, alignment, and padding work.
- How changes to child sizes influence layout.

Our NPay application now has a structured welcome screen.

Next: Lesson 2.4 — HStack and Horizontal Layout. We'll add a row of NPay quick actions and investigate how horizontal layout differs from vertical layout, including alignment, flexible space, layout priorities, and the relationship between HStack and Spacer.

## Deck changes

The deck (`index.html`, built by `tools/gen2_3.py`, 42 slides) follows Sections 1–20, grouped into 8 Parts:
the problem (1), a generic struct (2), the trailing closure (3), @ViewBuilder (4–6), the Content type (7, 13),
spacing, padding and alignment (8–10, 18–19), how a stack sizes itself (11, 14, 16–17), the NPay screen (12, 20);
then recap, review (15), next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_3/`, rerun with `sh tools/sim2_3/run.sh`)
- Section 2: the text's simplified initializer (an `init` without a body does not compile) is replaced by the real iOS 26.5 SDK declaration `@frozen public struct VStack<Content> : View where Content : View` with `init(alignment:spacing:content:)`, body omitted.
- Sections 4 and 6: the closure and `StringBuilder` examples compiled and ran: `30`, `Welcome to NPay`. The builder is shown with one-line signatures to fit.
- Section 5: the SDK's `ViewBuilder.buildBlock<each Content>(…) -> TupleView<(repeat each Content)>` shows the tuple-based content.
- Sections 7, 13, 14: printed types `VStack<Text>`, `VStack<TupleView<(Text, Image)>>`, `VStack<TupleView<(Text, Text)>>`, `VStack<VStack<Text>>`.
- Sections 8 and 18: the spacing slider is replaced by the border experiment at spacing 20 and 50 (207.3 → 267.3 pt: +60 for two gaps).
- Sections 9 and 19: versions A and B measured 235.7 × 128.7 and 235.7 × 188.7 pt.
- Section 10: the alignment buttons are replaced by a screenshot of the three alignments (grey border = stack width).
- Section 11: `VStack { Text("NPay") }` measured 39.7 × 24.3 pt; with the filling frame, 402 × 778 pt (the safe area).
- Section 16: the calculator's illustrative 41 + 20 + 20 = 81 pt is kept as the text's illustration; measured: 48.7 + 21.0 + 20 = 89.7 pt.
- Section 17: at Accessibility XL, 74.0 + 49.7 + 20 = 143.7 pt, with a screenshot.
- Sections 1 and 12/20: screenshots of the Lesson 2.2 screen and Milestone 2.3. The final code on the slide writes `VStack(alignment: .center, spacing: 20) {` on one line, drops blank lines and leaves out `import SwiftUI` / `#Preview` to fit.

**Authored (flagged)**
- Section 17's five steps drawn as a stepper (the text lists them as a flow).
- Review: the text's 8 questions (answers authored), plus a predict-the-height item and a spaced item from 2.2.
- Outcomes, "Where we are", recap, "Where this goes next" (2.4 from the text), lab with expected results.

**Wording**
- "Trainer question" / "Trainer insight" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding"; "your earlier question about trailing closures" is dropped.
