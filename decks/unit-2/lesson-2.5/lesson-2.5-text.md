# Unit 2 · Lesson 2.5 — ZStack: Layering, Backgrounds & SwiftUI Rendering

> Lesson text as shared. It ends after Section 11 (experiments); there is no knowledge check or "next lesson" line.
> Interactive widgets (layer explorer, VStack/ZStack sizing toggle, alignment buttons) are described in brackets.
> The deck (`index.html`, built by `tools/gen2_5.py`) follows Sections 1–11. Simulator evidence and authored
> additions are listed at the end under "Deck changes".

NPay Engineering Lab · SwiftUI Layout Internals · Incremental App Development

We've already built NPay's welcome screen using Text, Image, VStack, and HStack.

Now we're going to build something that looks like a real payment application: our first account balance card.

But the real learning goal is deeper: **How does SwiftUI place views on top of other views, determine their sizes, and decide which one appears in front?**

Today we'll investigate ZStack, Z-order, layout proposals, alignment, backgrounds, overlays, and rendering.

## 1. The problem — NPay needs a balance card

Our current application has a payment icon, the NPay title, a subtitle, and three quick actions. Now we want to display a balance card. [Mock-up: NPay; a card with "Available balance", "₹25,000.00", "NPay Demo Account"; Send / Request / History.]

**Target milestone — NPay balance card.** We'll use a fixed demonstration balance of ₹25,000. Real balance updates and state management will come later.

## 2. What exactly is ZStack?

We already know: VStack arranges children vertically; HStack arranges children horizontally. ZStack overlays children along the depth axis.

```swift
ZStack {
    Color.blue

    Text("NPay")
        .foregroundStyle(.white)
}
.frame(width: 240, height: 140)
```

The blue color forms a background layer, and the text appears above it. [Two views occupying overlapping space.]

**Behind the scenes.** ZStack is a generic struct conforming to View. Its initializer is conceptually:

```swift
ZStack(
    alignment: .center,
    content: {
        // Child views
    }
)
```

Just like VStack, it uses a @ViewBuilder closure to construct its content. The difference is its layout behavior. Instead of placing children one after another, ZStack aligns them within overlapping layout space.

## 3. Z-order — which view appears in front?

```swift
ZStack {
    Color.blue
    Color.green
    Text("NPay")
}
.frame(width: 240, height: 140)
```

In normal ZStack source ordering, later children are drawn above earlier children. Here, green covers blue, while the text appears on top. [Interactive layer explorer: + Blue, + Green, + Text — the text appears above both color layers.]

**Trainer question.** Does changing the source order of children affect their visual layering? Yes. In a ZStack, later children normally appear above earlier children, unless stacking behavior is explicitly adjusted.

## 4. What is .zIndex()?

SwiftUI provides a modifier that controls relative drawing order.

```swift
ZStack {
    Text("Behind")
        .zIndex(0)

    Text("In Front")
        .zIndex(1)
}
```

A larger zIndex generally places a view above siblings with lower values in the relevant stacking context.

**Important nuance.** zIndex controls visual stacking order. It does not automatically change a view's size, position, or layout priority. It also doesn't create a new independent window or process.

## 5. How does ZStack calculate its size?

Suppose a ZStack contains two views: a blue rectangle requesting 300 × 180 points, and a text view requiring approximately 100 × 25 points. What should the ZStack's size be?

Under ordinary layout conditions, the stack considers the sizes of its children and their alignment. Unlike VStack, it doesn't add child heights together. [Compare layout sizing: VStack / ZStack toggle — ZStack overlaps the rectangle and text, so the resulting layout does not simply add their heights.]

**Important detail.** SwiftUI's exact ZStack sizing depends on proposed sizes, child flexibility, alignment, and layout behavior. Don't assume that every ZStack always takes the size of its largest child in all circumstances.

## 6. Alignment inside ZStack

By default, ZStack uses center alignment. But we can change it.

```swift
ZStack(alignment: .topLeading) {
    Color.blue

    Text("NPay")
        .foregroundStyle(.white)
        .padding()
}
.frame(width: 300, height: 180)
```

The text appears toward the top-leading corner.

**Why .topLeading?** It is an Alignment value representing vertical top and horizontal leading alignment. Swift uses contextual type inference to resolve the shorthand. [Top Leading / Center / Bottom Trailing buttons. Conceptual alignment visualization.]

## 7. ZStack versus .background() versus .overlay()

This is a very important SwiftUI design decision. All three can create layered visuals, but their layout relationships differ.

ZStack:

```swift
ZStack {
    Color.blue
    Text("NPay")
}
.frame(width: 240, height: 120)
```

Children participate together in the ZStack layout.

Background:

```swift
Text("NPay")
    .padding(30)
    .background(.blue)
```

The background is attached to the modified text view. Its size follows the primary view's layout region.

Overlay:

```swift
RoundedRectangle(cornerRadius: 16)
    .fill(.blue)
    .frame(width: 240, height: 120)
    .overlay {
        Text("NPay")
            .foregroundStyle(.white)
    }
```

The overlay is laid out relative to the primary view and generally does not determine the primary view's required size.

| Feature | ZStack | Background | Overlay |
|---|---|---|---|
| Purpose | General overlapping layout | Place content behind a view | Place content over a view |
| Size relationship | Considers participating children | Follows primary view | Follows primary view |
| Typical use | Complex layered composition | Card backgrounds | Badges, labels, decoration |

**Trainer insight.** Use ZStack when multiple layers should participate in one layered layout. Use .background() and .overlay() when the visual is naturally attached to a primary view.

## 8. Let's build NPay's balance card incrementally

**Step A — Blue card shape**

```swift
RoundedRectangle(cornerRadius: 20)
    .fill(.blue)
    .frame(height: 180)
```

RoundedRectangle is a SwiftUI shape. `.fill(.blue)` describes its fill style. `.frame(height: 180)` constrains its layout height.

**Step B — Add the balance**

```swift
ZStack {
    RoundedRectangle(cornerRadius: 20)
        .fill(.blue)

    Text("₹25,000")
        .font(.largeTitle.bold())
        .foregroundStyle(.white)
}
.frame(height: 180)
```

Now the text appears over the blue card.

**Step C — Add structured content.** We want a label, balance, and account name.

```swift
ZStack {
    RoundedRectangle(cornerRadius: 20)
        .fill(.blue)

    VStack(alignment: .leading, spacing: 12) {
        Text("Available Balance")
            .font(.subheadline)

        Text("₹25,000")
            .font(.largeTitle.bold())

        Text("NPay Demo Account")
            .font(.caption)
    }
    .foregroundStyle(.white)
    .frame(maxWidth: .infinity, alignment: .leading)
    .padding(24)
}
.frame(height: 180)
```

**What is happening?** The ZStack creates overlapping layers. The RoundedRectangle forms the background. The VStack organizes the text vertically. The padding keeps the content away from the card edges.

## 9. Behind the scenes — how SwiftUI composes the card

[NPay balance card composition: ZStack → RoundedRectangle (background layer) + VStack (text content layer) → layout + rendering.]

**Does SwiftUI create separate CALayers for each child?** Not necessarily. SwiftUI manages rendering representations internally. The public API guarantees the declarative layout and drawing behavior, not a fixed one-to-one mapping to CALayer objects.

## 10. Complete NPay code — Lesson 2.5

Now integrate the balance card into the existing NPay application.

```swift
import SwiftUI

struct ContentView: View {

    var body: some View {
        VStack(spacing: 28) {

            Image(systemName: "creditcard.fill")
                .font(.system(size: 48))
                .foregroundStyle(.blue)

            Text("NPay")
                .font(.largeTitle.bold())
                .foregroundStyle(.blue)

            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)

            ZStack {
                RoundedRectangle(cornerRadius: 20)
                    .fill(.blue)

                VStack(alignment: .leading, spacing: 12) {
                    Text("Available Balance")
                        .font(.subheadline)

                    Text("₹25,000")
                        .font(.largeTitle.bold())

                    Text("NPay Demo Account")
                        .font(.caption)
                }
                .foregroundStyle(.white)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(24)
            }
            .frame(height: 180)

            HStack(spacing: 30) {
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

We've preserved the existing NPay features and added one new component: the balance card.

## 11. Experiments to run in Xcode

Try these changes one at a time.

**Experiment A — Reverse the layers.** Move the RoundedRectangle below the text in source order, then move it above the text. Observe which layer covers the other.

**Experiment B — Change alignment.** Change `ZStack {` to `ZStack(alignment: .topLeading) {`. Observe the result. Note that our inner VStack has its own frame and padding, so the visual difference may be subtle.

**Experiment C — Replace ZStack with background.** Try building the same card using:

```swift
VStack(alignment: .leading, spacing: 12) {
    Text("Available Balance")
    Text("₹25,000")
    Text("NPay Demo Account")
}
.foregroundStyle(.white)
.padding(24)
.frame(maxWidth: .infinity, alignment: .leading)
.frame(height: 180)
.background(.blue, in: RoundedRectangle(cornerRadius: 20))
```

Compare the resulting layout with the ZStack version.

## Deck changes

The deck (`index.html`, built by `tools/gen2_5.py`, 34 slides) follows Sections 1–11, grouped into 8 Parts:
a balance card (1), ZStack (2), Z-order and zIndex (3–4), sizing (5), alignment (6), ZStack vs background vs overlay (7),
building the card (8–9), NPay with its card (10–11); then recap, review, next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_5/`, rerun with `sh tools/sim2_5/run.sh`)
- Section 2: the text's conceptual `ZStack(alignment:content:)` is replaced by the SDK declaration (`init(alignment: Alignment = .center, @ViewBuilder content:)`); printed type `ZStack<TupleView<(Color, Text)>>`; the basic stack measured 240 × 140 pt.
- Sections 3–4 and experiment A: the layer explorer is replaced by three real cards: Blue, Green, Text (text on top); Text, Blue, Green (text hidden); `Text.zIndex(1)`, Blue, Green (text visible again).
- **Observed while measuring:** with another modifier placed after `.zIndex(1)` (so zIndex was not the child's outermost modifier), the text stayed hidden; with `.zIndex` last it worked. This is stated on the zIndex slide as an observation.
- Section 5: the VStack/ZStack toggle is replaced by measurements of the text's example: ZStack 300 × 180 pt, the same children in a VStack 300 × 212.9 pt.
- Section 6: the alignment buttons are replaced by a screenshot of `.topLeading`, `.center`, `.bottomTrailing` (run at 300 × 150 to fit three).
- Section 7: screenshot and sizes of ZStack (240 × 120), padded Text with background (110.3 × 92.3), overlay (240 × 120), plus an **authored** oversized overlay (black text so it shows) that spills while the shape stays 240 × 120.
- Section 8: screenshot of steps A–C (A and B run at 150 pt tall to fit).
- Sections 10–11: before/after screenshots; experiment C: the ZStack card and the `.background(_:in:)` card both measured 370 × 180 pt (both run with plain text). Experiment B's subtle result is stated (no visible change).
- The text's mock-up shows "₹25,000.00"; the deck follows the code: "₹25,000".

**Authored (flagged)**
- The text has **no knowledge check**: all 7 review questions are authored (including a predict item and a spaced item from 2.4).
- The text names no next lesson: "Where this goes next" lists state management ("Later") and the modifiers lesson, which turned out to be 2.6 (SwiftUI View Modifiers); the end slide names it.
- Section 9's composition drawn as a diagram (conceptual).
- The final-code slide shows the screen's structure rather than all 70 lines (the full code is in the text).
- Outcomes, "Where we are", recap, lab (the text's experiments A–C plus zIndex).

**Wording**
- "Trainer question" / "Trainer insight" became neutral callouts.
