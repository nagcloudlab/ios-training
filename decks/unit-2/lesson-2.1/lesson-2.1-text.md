# Unit 2 · Lesson 2.1 — SwiftUI Text: From Source Code to Screen

> Lesson text as shared (Unit 2 restarted from zero; this replaces the earlier "Inside SwiftUI" Lesson 2.1, which
> is kept in git history at commit d9883ef). Interactive widgets in the original (runtime walkthrough, width slider,
> quiz) are described in brackets. The deck (`index.html`, built by `tools/gen2_1.py`) follows Sections 1–16.
> Corrections, simulator evidence and authored additions are listed at the end under "Deck changes".

NPay iOS Engineering Masterclass · Beginner in iOS → Senior-Level Understanding

We're restarting Unit 2 from zero.

You already know programming and have studied Swift, memory, processes, and concurrency in Units 0 and 1. Now we'll use that knowledge to understand how iOS applications are actually built.

Our learning rule is simple: **Build something small → Predict → Run → Investigate internals → Experiment → Improve NPay.**

Today we'll learn one main concept: SwiftUI Text.

By the end, you'll understand not only how to display text but also how Swift resolves Text, why it conforms to View, what `some View` means, how SwiftUI measures text, and how it becomes visible on an iPhone.

## 1. The engineering story

Imagine we're developing NPay, a new payment application.

Our first requirement: When NPay launches, display the application name in the center of the screen.

> **Milestone 2.1 — Our first NPay screen.** We won't add icons, buttons, or layouts yet. We'll investigate one SwiftUI component thoroughly.

## 2. Build — our first SwiftUI view

Open your existing NPay Xcode project. In `ContentView.swift`, use:

```swift
import SwiftUI

struct ContentView: View {

    var body: some View {
        Text("NPay")
    }
}

#Preview {
    ContentView()
}
```

Press Command + R to launch the application, or use Xcode's SwiftUI Canvas preview.

Expected result: the word NPay appears near the center of the screen.

Now we have a working feature. Let's investigate how it works.

## 3. First mystery — what exactly is Text?

When Swift encounters `Text("NPay")`, what is Text? A function? A class? A UIKit object?

Text is a struct defined in the SwiftUI framework. Conceptually:

```swift
// Simplified illustration — not Apple's source
struct Text: View {
    // Text content and styling information
}
```

Text conforms to the View protocol.

| Part | Meaning |
|---|---|
| `Text` | SwiftUI struct |
| `(...)` | Initializer invocation |
| `"NPay"` | String literal |
| Result | A Text value describing UI content |

**Connect to Unit 1.** Remember:

```swift
struct Customer {
    let name: String
}

let customer = Customer(name: "Ravi")
```

`Customer(...)` creates a Customer value. Similarly, `let title = Text("NPay")` creates a Text value. But there's a difference in purpose: Customer models domain data, while Text describes interface content.

**Trainer question.** Does `Text("NPay")` immediately draw pixels? No. It creates a declarative view value. SwiftUI manages layout and rendering separately.

## 4. How does Swift find Text?

Look at the first line: `import SwiftUI`. SwiftUI is an Apple framework that exposes a module containing types such as Text, Image, Button, and VStack. The compiler uses imported module information to resolve those declarations.

1. `import SwiftUI` — makes SwiftUI declarations available
2. `Text` — compiler resolves the SwiftUI type
3. `"NPay"` — compiler processes the string literal
4. Initializer overload resolution — selects a compatible Text initializer
5. Text value — a statically typed view description

**Investigate in Xcode.** Hold Command (⌘) and click Text, then select Jump to Definition. You should see an interface declaration resembling `public struct Text: View`. The exact interface may differ by Xcode and SDK version. This is how you can inspect APIs instead of memorizing them.

## 5. Why does ContentView conform to View?

`struct ContentView: View` is protocol conformance, not class inheritance. We studied protocols in Unit 1. A simplified mental model of the View protocol is:

```swift
// Teaching approximation, not Apple's exact API

protocol View {
    associatedtype Body: View

    @ViewBuilder
    var body: Body { get }
}
```

The important parts are:
- `associatedtype Body` — each view has a specific body type.
- `body` — describes the view's content.
- `@ViewBuilder` — supports declarative composition of child views.

Our ContentView satisfies the protocol because its body produces a Text, which itself conforms to View. (Diagram: View protocol; ContentView and Text both conform to View.)

**Trainer insight.** ContentView doesn't need to inherit from Text. It only needs to return a view description satisfying the View protocol.

## 6. What exactly does some View mean?

```swift
var body: some View {
    Text("NPay")
}
```

Why `some View` instead of just `View`? Because `some View` is an opaque return type. It means the implementation returns one specific concrete type conforming to View, while hiding that concrete type from callers. In our example, that underlying type is Text.

Compiler's understanding: declared return type `some View`; underlying concrete type `Text`; requirement: Text conforms to View.

**Important distinction.** `some View` does not mean Swift can arbitrarily return a different concrete type on each evaluation. The opaque return type has a consistent underlying concrete type for that declaration. We'll see why this matters when we introduce conditional views.

## 7. What happens at runtime?

Let's follow the complete journey from launching NPay to seeing text.

[Interactive execution walkthrough. Step 1 — Operating system: iOS launches NPay. The app process starts and the SwiftUI application lifecycle is established. (The remaining steps were not included in the shared text.) Conceptual runtime flow; SwiftUI's private implementation details are not fully public.]

**Key insight.** Creating a Text value is not the same as drawing text. The framework decides how to measure, position, and render the description.

## 8. Why is NPay centered without a VStack?

We haven't written any positioning code. Yet the text appears centered in the root screen. Why?

In this simple root layout, the SwiftUI hosting environment proposes available space and places the text according to its layout behavior. This does not mean every Text is automatically centered in every parent. The result depends on the surrounding layout.

**Experiment.** Replace `Text("NPay")` with:

```swift
Text("NPay")
    .frame(maxWidth: .infinity, maxHeight: .infinity,
           alignment: .topLeading)
```

Now the text should move toward the top-leading position of the available layout area. The visible position may also be influenced by safe-area behavior. We'll study `.frame` deeply in the layout lessons.

## 9. How does SwiftUI measure text?

This is where the layout engine becomes interesting.

Text has an intrinsic content size under given constraints. For example, "NPay" at a small font requires less space than "Welcome to NPay" at a large font.

SwiftUI uses a layout process in which parents propose sizes, children choose sizes, and parents position children.

[Text layout experiment: an "Available width" slider (260px) over the text "Welcome to NPay. Payments made simple." Narrower space may cause additional line wrapping, increasing the height needed for text. Browser-based illustration, not SwiftUI's exact text measurement.]

**Behind the scenes.** Text measurement considers font metrics, glyph advances, line breaks, language, and the proposed available size. The text system determines a suitable layout, and SwiftUI positions that result. This is why text can respond naturally to different device widths.

## 10. Experiment — introduce font styling

```swift
Text("NPay")
    .font(.largeTitle)
```

What is `.font()`? It's a SwiftUI modifier. What is `.largeTitle`? A semantic font style resolved through the expected Font type. The longer form is `Text("NPay").font(Font.largeTitle)`.

Why does Swift understand `.largeTitle`? Because the compiler knows the modifier expects a font value. This is contextual type inference, which we learned in Unit 1.

**Why use semantic fonts?** Styles such as `.body`, `.title`, and `.largeTitle` integrate with platform typography conventions and Dynamic Type. Dynamic Type allows users to choose preferred text sizes for accessibility.

## 11. Experiment — inspect modifier return types

Add this temporary experiment inside an appropriate SwiftUI-capable execution context, such as a Playground or a button action:

```swift
let original = Text("NPay")
let styled = original.font(.largeTitle)
let padded = original.padding()

print(type(of: original))
print(type(of: styled))
print(type(of: padded))
```

What do you expect? `original` is Text. For the text-specific `.font()` overload, `styled` is also Text. `padding()` returns a modified view type rather than plain Text.

**Why is this interesting?** Not every modifier produces the same concrete type. Some text-specific modifiers preserve Text, while general View modifiers commonly create wrapper descriptions. This is an example of how SwiftUI combines protocol extensions, generics, and overload resolution.

## 12. Experiment — modifier order matters

```swift
Text("NPay")
    .padding()
    .background(.yellow)
```

compared with:

```swift
Text("NPay")
    .background(.yellow)
    .padding()
```

The output differs because modifiers are applied in sequence. (Illustration: padding then background — the background covers the padded region; background then padding — the background covers only the text.)

This is a crucial SwiftUI concept. Modifiers aren't just visual decorations. Their order changes the structure and layout behavior of the resulting view description.

## 13. What about Unicode and localization?

NPay may eventually support multiple languages. Consider:

```swift
Text("Welcome to NPay")
Text("வணக்கம்")
Text("नमस्ते")
```

SwiftUI's text infrastructure supports Unicode text, shaping, line breaking, and language-specific layout behavior. A visible glyph isn't necessarily equivalent to one byte or one Unicode scalar.

**Localization distinction.** `Text("Welcome to NPay")` can participate in SwiftUI localization. But `Text(verbatim: "Welcome to NPay")` explicitly treats the string as verbatim content. We'll study localization deeply when building NPay's multilingual interface.

## 14. Final NPay code — Lesson 2.1

Now keep the application in this state:

```swift
import SwiftUI

struct ContentView: View {

    var body: some View {
        Text("NPay")
            .font(.largeTitle)
            .bold()
            .foregroundStyle(.blue)
    }
}

#Preview {
    ContentView()
}
```

We've added semantic typography, bold styling, and foreground color. Our application still has only one view, but we now understand its foundation.

## 15. Senior engineer knowledge check

SwiftUI Text · Protocols · Type System · Layout · Rendering · Modifiers. Answer these 10 questions.

1. What does `Text("NPay")` create? — A UILabel instance / **A SwiftUI Text value** / Pixels directly in a graphics buffer
2. Why can `ContentView.body` return Text? — Text inherits from ContentView / **Text conforms to View** / Text is a special Swift keyword
3. What does `some View` mean? — Any different View type at runtime / **One underlying concrete type conforming to View** / A dynamically typed object
4. Does evaluating body necessarily redraw the entire screen? — Yes / **No**
5. Why does `.largeTitle` work without writing `Font.largeTitle`? — Runtime reflection / **Contextual type inference** / Implicit global variable
6. What does `.padding()` generally do? — Mutates the original Text object / **Returns a padded view description** / Adds spaces to the string
7. Does modifier order affect layout? — **Yes** / No
8. What influences Text measurement? — Only the number of characters / **Font, content, proposed size and layout constraints** / Only the screen resolution
9. Does every Text value create a separate UILabel? — Yes / **Not guaranteed**
10. Which API explicitly displays text without localization-key interpretation? — `Text("Welcome")` / **`Text(verbatim: "Welcome")`** / `Text.localized()`

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 16. Final practical challenge — Predict the result

Version A:

```swift
Text("NPay")
    .padding(24)
    .background(.yellow)
```

Version B:

```swift
Text("NPay")
    .background(.yellow)
    .padding(24)
```

Which version has the larger yellow background? [Reveal explanation — not included in the shared text.]

**Lesson 2.1 complete.** We've now covered Text as a Swift struct, the View protocol, `some View`, initializer resolution, localization, text measurement, rendering, modifiers, and modifier order.

Next, we'll continue Lesson 2.2 — Image and SF Symbols, building on this screen without discarding what we've already developed.

## Deck changes

The deck (`index.html`, built by `tools/gen2_1.py`, 44 slides) follows Sections 1–16, grouped into 8 Parts:
the first screen (1–2), what is Text (3–4), View and some View (5–6), from value to pixels (7), layout (8–9),
modifiers (10–12), Unicode and localization (13), final code (14); then recap, the review (15–16), next, lab, end.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5; app in `tools/sim2_1/`, rerun with `sh tools/sim2_1/run.sh`)
- Section 2: screenshot of the first `ContentView` (NPay centred). Section 8: screenshot with the top-leading frame.
- Section 4: the real iOS 26.5 SDK interface: `@frozen public struct Text : Equatable, Sendable` lives in SwiftUICore, the View conformance is an extension, and SwiftUI re-exports SwiftUICore (`@_exported import SwiftUICore`). The text's expectation `public struct Text: View` is shown as a note.
- Section 5: the real requirement lines (`associatedtype Body : View`, `@ViewBuilder @MainActor var body: Self.Body { get }`) next to the teaching approximation.
- Section 6: `type(of: body)` printed `Text` for ContentView, and `ModifiedContent<Text, _FlexFrameLayout>` with the frame.
- Section 9: the browser width slider is replaced by measured sizes: "NPay" .body 39.7 × 24.3 pt, .largeTitle 77.3 × 48.7 pt; the sentence offered 260 pt chose 221.0 × 50.3 pt (2 lines), offered 140 pt chose 140.0 × 76.3 pt (3 lines). Grey borders added to show the frames.
- Section 11: real console `Text`, `Text`, `ModifiedContent<Text, _PaddingLayout>` (run in a view's `.task`).
- Section 12: screenshot of both orders (shown at `.largeTitle`); both measured 109.3 × 80.7 pt.
- Section 13: screenshot of the three greetings; counts: NPay 4/4/4, வணக்கம் 5 characters / 7 scalars / 21 UTF-8 bytes, नमस्ते 3 / 6 / 18. Localization shown with a Tamil `Localizable.strings` (**authored translation** "NPay-க்கு வரவேற்கிறோம்") and the device language set to Tamil: `Text("…")` translated, `Text(verbatim:)` did not.
- Section 14: screenshots at the default text size and at Accessibility XL (Dynamic Type); 82.7 × 48.7 pt → 125.3 × 74.0 pt; `type(of: body)` is `Text`.

**Authored (flagged)**
- Section 7's walkthrough: only step 1 was shared; steps 2–6 (scene shows ContentView, body read, layout, rendering, on screen) are authored and the slide is marked conceptual.
- Section 15/16 answers (not marked in the shared text) and every "why" / "common trap"; Q5 noted as spaced review from Unit 01.
- Outcomes, "Where we are" (Unit 02 progress strip: only 2.1 and 2.2 are named, since the unit restarted), recap, "Where this goes next" (2.2 plus the text's own forward pointers), lab "Investigate Text yourself".
- The learning loop on the Part 1 slide comes from the text's introduction.

**Wording**
- "Trainer question" / "Trainer insight" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding". `ContentView` kept (the Xcode template name the text uses).
