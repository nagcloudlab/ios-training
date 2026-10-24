# Unit 2 · Lesson 2.2 — SwiftUI Image & SF Symbols

> Lesson text as shared. Interactive widgets in the original (symbol pipeline stepper, font-size slider, colour
> buttons, quiz) are described in brackets. The deck (`index.html`, built by `tools/gen2_2.py`) follows Sections 1–12.
> Corrections, simulator evidence and authored additions are listed at the end under "Deck changes".

NPay Engineering Lab · Build → Observe → Investigate → Experiment

In Lesson 2.1, we learned how SwiftUI's Text works—from initializer resolution to layout and rendering.

Now we'll introduce exactly one new component: Image.

Our engineering question: **How does the string "creditcard.fill" become a graphical symbol on the iPhone screen?**

We'll investigate this at three levels: Swift language, SwiftUI framework, and iOS rendering infrastructure.

## 1. NPay's next requirement

Our current screen displays only the NPay title. We want a payment icon above it. [Before: NPay. After: a card icon above NPay.]

To keep the focus on Image, we'll first investigate the icon independently. Then we'll combine it with our existing Text using a simple VStack. We'll study VStack internals in the next lesson.

## 2. First experiment — create an Image

Open ContentView.swift and temporarily replace its body with:

```swift
var body: some View {
    Image(systemName: "creditcard.fill")
}
```

Run the preview. You should see a credit-card symbol.

| Part | Meaning |
|---|---|
| `Image` | Struct defined in SwiftUI |
| `systemName:` | Initializer argument label |
| `"creditcard.fill"` | SF Symbol identifier |
| Result | A SwiftUI Image value |

**Important distinction.** Image does not mean an image file is being loaded from your project. In this example, we're requesting a system symbol.

## 3. Where does creditcard.fill come from?

Apple provides a symbol library called SF Symbols. It contains thousands of symbols designed to integrate with Apple's system typography.

Examples of system symbols: `creditcard.fill`, `house.fill`, `person.fill`, `bell.fill`, `heart.fill`, `lock.fill`. [Illustrative symbols; the icons shown here are not exact SF Symbols renderings.] You can explore the actual symbol designs in Apple's SF Symbols application.

**Trainer question.** Does "creditcard.fill" represent a file path? No. It is a symbol name used to resolve a system-provided graphical symbol.

## 4. Behind the scenes — how is the symbol resolved?

Let's trace the journey. [From symbol name to visible icon — a 6-stage stepper; only stage 5 was included: "Stage 5 / 6 — Layout: SwiftUI determines the symbol's size and placement." Conceptual pipeline. Exact internal symbol lookup and rendering implementation is not publicly specified.]

**Senior engineer insight.** Swift's compiler doesn't convert "creditcard.fill" into image pixels. The symbol name is resolved by platform facilities at runtime. That is why using an unsupported symbol name can result in no visible symbol, even though the code compiles.

## 5. Why does .font() change an image's size?

```swift
Image(systemName: "creditcard.fill")
    .font(.system(size: 64))
```

You may wonder: why does an Image accept a font modifier? Fonts are for text!

SF Symbols are designed to work with typography. They can scale and align with text, and their appearance can respond to font size and weight.

[Interactive symbol-size experiment: font size slider at 64 pt. Illustrative credit-card symbol, not the exact SF Symbols glyph or point-size measurement.]

**Why is this better than scaling a small bitmap?** System symbols are designed for scalable rendering, so they can remain sharp at different sizes. A small raster image enlarged excessively may become blurry.

## 6. Where does .system(size: 64) come from?

`.font(.system(size: 64))` — the `.font()` modifier expects a font value. `.system(size: 64)` is shorthand for `.font(Font.system(size: 64))`. The compiler knows the expected type from the modifier's parameter. This is contextual type inference. It is the same Swift feature we studied with `.blue` in the previous lessons.

## 7. Apply a foreground style

```swift
Image(systemName: "creditcard.fill")
    .font(.system(size: 64))
    .foregroundStyle(.blue)
```

The foregroundStyle modifier applies a foreground style to the symbol. `.blue` is a shorthand static style member resolved using Swift's contextual type system. We could also write `.foregroundStyle(Color.blue)`.

[Experiment — change the color: Blue / Green / Red buttons.] The foreground style changes the symbol's presentation without requiring a different image resource.

## 8. Image versus Text — compare the types

We now have two SwiftUI types: `Text("NPay")` and `Image(systemName: "creditcard.fill")`. Both conform to View. [Diagram: View protocol; Text — textual content; Image — graphical content.]

This explains why both support common modifiers such as `.padding()` and `.foregroundStyle()`.

## 9. What is the difference between system images and asset images?

```swift
Image(systemName: "creditcard.fill")

Image("NPayLogo")
```

The first references an SF Symbol. The second looks for an image resource named NPayLogo, commonly stored in Assets.xcassets.

| Feature | SF Symbol | Asset image |
|---|---|---|
| Source | System symbol library | App-provided resource |
| Typical use | Standard interface icons | Branding and custom artwork |
| Scaling | Designed for scalable symbol rendering | Depends on resource type and configuration |
| Styling | Supports symbol-specific modes | Depends on template/original rendering |
| Availability | Depends on OS and symbol version | Bundled with application |

**Important detail.** If you create an asset named NPayLogo, Xcode's asset catalog tools process that resource during the build. At runtime, SwiftUI resolves the named resource through the application's resource system. This is different from resolving an SF Symbol.

## 10. Our NPay increment — combine Image and Text

Now let's retain our Lesson 2.1 title and add the payment symbol above it.

```swift
import SwiftUI

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

#Preview {
    ContentView()
}
```

We've introduced VStack only as a container for our two views. We will study its initializer, @ViewBuilder, trailing closure, generic content type, and layout behavior in Lesson 2.3.

**Milestone 2.2 — NPay title with payment symbol.**

## 11. Senior engineer knowledge check

1. What is `Image(systemName:)` creating? — **A SwiftUI Image value** / A UIImageView instance / A bitmap file
2. Does the Swift compiler generate the symbol's pixels? — Yes / **No**
3. Why does `.font()` influence SF Symbol size? — **Symbols integrate with typography** / It modifies the source PNG
4. Does every valid String represent an available SF Symbol? — Yes / **No**
5. Does `Image("NPayLogo")` mean the same thing as `Image(systemName: "NPayLogo")`? — Yes / **No**

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 12. Your Xcode investigation

Before moving forward, try these experiments in your actual NPay project:
1. Change "creditcard.fill" to "house.fill".
2. Change the symbol font size from 64 to 24, then 100.
3. Change .blue to .green.
4. Try an invalid system symbol name and observe the result.
5. Command-click Image in Xcode to inspect its public API.

Our next lesson is 2.3 — VStack and @ViewBuilder, where we'll deeply investigate how SwiftUI accepts multiple child views through a trailing closure, constructs a generic `VStack<Content>` value, and arranges those children vertically.

## Deck changes

The deck (`index.html`, built by `tools/gen2_2.py`, 35 slides) follows Sections 1–12, grouped into 7 Parts:
the requirement (1), a first Image (2–3), resolved at run time (4), sizing with .font (5–6), foreground style (7),
Image, Text and assets (8–9), the NPay increment (10); then recap, the review (11), next, lab (12), end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_2/`, rerun with `sh tools/sim2_2/run.sh`)
- Section 1: before/after screenshots (the Lesson 2.1 title; Milestone 2.2).
- Section 2: screenshot of the bare symbol; at default size it measured 23.7 × 16.3 pt.
- Section 3: the six example names rendered as real SF Symbols (replacing the illustrative icons).
- Section 4: `Image(systemName: "creditcard.fil")` built and ran blank, measured 0 × 0 pt, and SwiftUI logged "No symbol named 'creditcard.fil' found in system symbol set". The SDK interface shows `init(systemName: String)`.
- Section 5: the slider is replaced by sizes 24 / 64 / 100 (33.7 × 23.7, 89.7 × 62.3, 139.7 × 97.7 pt) and a sharpness comparison: the symbol at size 100 next to a 23 × 16 pixel bitmap of it enlarged to the same width.
- Section 6: `type(of:)` shows that `.font` on an Image returns `ModifiedContent<Image, _EnvironmentKeyWritingModifier<Optional<Font>>>` (it writes the environment), while on Text it returns `Text`. This explanation of "why .font sizes a symbol" is added.
- Section 7: the colour buttons are replaced by a screenshot of .blue / .green / .red; the SDK's `extension ShapeStyle where Self == Color { static var blue: Color }` shows how `.blue` is found.
- Section 8: SDK lines `@frozen public struct Image : Equatable, Sendable` and `extension Image : View`; `.foregroundStyle(.blue)` on Image returns `ModifiedContent<Image, _ForegroundStyleModifier<Color>>`.
- Section 9: an app with a real asset catalog (compiled with `actool`). `Image("NPayLogo")` measured 120 × 120 pt; `Image(systemName: "NPayLogo")` and `Image("creditcard.fill")` measured 0 × 0 and logged "No symbol named 'NPayLogo' …" and "No image named 'creditcard.fill' found in asset catalog …". The **NPayLogo artwork is authored** (`makelogo.swift`: a navy square with a teal N).
- Section 10: screenshot of Milestone 2.2. Blank lines inside the code were removed to fit the slide. The body's printed type, `VStack<TupleView<(…, Text)>>`, is mentioned in the notes as a teaser for 2.3.

**Authored (flagged)**
- Section 4's pipeline: only stage 5 (Layout) was shared; stages 1–4 and 6 are authored and the slide is marked conceptual.
- Review: the text's 5 questions (answers authored), plus two predict-the-output items on `type(of:)` (Image with .font; Text with .font as spaced review from 2.1).
- Outcomes, "Where we are", recap, "Where this goes next" (2.3 from the text), lab from Section 12 with expected results.

**Wording**
- "Trainer question" / "Senior engineer insight" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding".
