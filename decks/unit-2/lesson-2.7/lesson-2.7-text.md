# Unit 2 · Lesson 2.7 — SwiftUI Button, Closures & Event Handling

> Lesson text as shared, in two parts: Part 1 (Sections 1–13, cut off mid-sentence in Section 13) and "Part 2:
> Complete Button Engineering Lab" (Sections 14–21). Between them the text noted that 2.7 was unfinished (breakpoint
> verification, knowledge check and checkpoint pending); Part 2 completes it. Interactive widgets are described in
> brackets. The deck (`index.html`, built by `tools/gen2_7.py`) follows Sections 1–21. Simulator evidence and
> authored additions are listed at the end under "Deck changes".

NPay Engineering Lab · Incremental Development · iOS Event Pipeline · Senior Engineer Edition

Until now, NPay has been a static interface. We have a balance card, a header, and three quick actions: Send, Request, and History.

Today, NPay becomes interactive. But we won't simply add a button and move on. We'll investigate how a finger tap travels through iOS, how SwiftUI recognizes it, why a closure executes, how hit testing works, and how to design reusable interactive components.

Our central question: **When a user touches "Send Money", how does iOS know which Swift closure to execute?**

## 1. Our next NPay milestone

[Mock-up: NPay, the balance card (Available Balance, ₹25,000, Demo Account), Send / Request / History — "Try tapping one of the quick actions."] Our goal is to reproduce this behavior in SwiftUI, using the existing NPay project.

## 2. First experiment — understand Button

```swift
Button("Send Money") {
    print("Send Money tapped")
}
```

We already studied trailing closures in Unit 1. A simplified form of this initializer is:

```swift
init(
    _ titleKey: LocalizedStringKey,
    action: @escaping () -> Void
)
```

SwiftUI provides several Button initializers, including versions that accept custom label views.

| Expression | Meaning |
|---|---|
| `Button` | Generic SwiftUI struct |
| `"Send Money"` | Button title |
| `{ ... }` | Trailing action closure |
| `@escaping` | Closure can be retained beyond initializer execution |
| `() -> Void` | Takes no arguments and returns no value |

**Connect to Unit 1.** `let action: () -> Void = { print("Payment requested") }; action()`. A SwiftUI button accepts a closure representing the action to perform when the control is activated.

## 3. Does the closure execute when body runs?

```swift
struct PaymentView: View {

    var body: some View {
        Button("Send Money") {
            print("Payment requested")
        }
    }
}
```

When SwiftUI evaluates body, it creates a button description containing an action closure. The action closure does not execute merely because body is evaluated. It executes when the button is activated.

[Button creation versus button activation — a 5-step stepper; only step 1 was included: "body evaluation — SwiftUI obtains a Button view description."]

**Trainer question.** If SwiftUI reevaluates body ten times, does the button action execute ten times? No. View evaluation and user activation are separate events.

## 4. Behind the scenes — from finger tap to Swift closure

Let's connect this to Unit 0, where we studied the main thread, RunLoop, and event handling. When the user touches the screen, the operating system handles the input and delivers relevant events to the application. SwiftUI participates in determining which interactive control should receive the action.

NPay — tap event pipeline:
1. Finger touches screen — hardware detects touch input.
2. iOS input infrastructure — system processes and routes input.
3. Application event delivery — input reaches the running application.
4. Hit testing and control handling — the relevant interactive control is identified.
5. SwiftUI Button activation — framework recognizes an activation.
6. Action closure executes — NPay handles the requested action.

Conceptual event flow. Exact system event routing and SwiftUI implementation details are not fully public.

**What thread runs the button action?** SwiftUI user-interface interactions are generally handled in the main-actor UI context. Button actions should remain responsive. Avoid performing long synchronous operations directly in an action closure. We'll explore asynchronous button actions in a later lesson.

## 5. What is hit testing?

Imagine the NPay screen has three quick actions. The user taps a point on the screen. How does SwiftUI determine which view should respond? This is where hit testing matters. Hit testing determines which interactive view corresponds to an input location, taking into account the relevant view hierarchy and interaction regions. [Interactive hit-testing experiment: Send / Request / History — "Hit target: History".]

**Important distinction.** A view's visual appearance and its interactive hit region are related, but they are not always identical. For example, a custom button label may have transparent areas that don't respond as expected. SwiftUI provides tools such as .contentShape() to define interaction shapes.

## 6. contentShape() — why does it matter?

```swift
Button {
    print("Send tapped")
} label: {
    HStack {
        Image(systemName: "arrow.up.right")
        Text("Send")
    }
    .frame(maxWidth: .infinity)
    .padding()
    .contentShape(Rectangle())
}
```

The `.contentShape(Rectangle())` modifier can help define the rectangular region used for interaction.

**Why is this useful?** Suppose the label has extra empty space. Without an appropriate hit-testing shape, some custom compositions may have unexpected interactive regions. A deliberate content shape helps align the interaction region with the intended button area.

## 7. Button with custom label — another initializer

```swift
Button {
    print("Send tapped")
} label: {
    VStack(spacing: 8) {
        Image(systemName: "arrow.up.right")
        Text("Send")
    }
}
```

This initializer accepts two closures: action — what happens when activated; label — what the button looks like. The label closure uses @ViewBuilder semantics to construct the view content.

**Generic type connection.** Button is generic over its label view type. Conceptually: `Button<Label>`. For a custom label, Swift infers the concrete label type from the closure. This is another example of Swift generics working behind the scenes.

## 8. Button styles

```swift
Button("Send Money") {
    print("Tapped")
}
.buttonStyle(.borderedProminent)
```

The style influences how the button is presented. Common built-in styles include .plain, .bordered, and .borderedProminent. [Button style comparison: Plain / Bordered / Prominent. Illustrative; exact native appearance varies by OS, environment and control state.]

**Trainer insight.** Button styles are not just color presets. They can influence interaction feedback, visual emphasis, shape, and environment-dependent presentation.

## 9. Disabled state and accessibility

Imagine the user hasn't entered a valid payment amount. The Send button should be disabled.

```swift
Button("Send Money") {
    print("Send requested")
}
.disabled(true)
```

.disabled() communicates that the control is unavailable for interaction. It is preferable to simply ignoring taps inside the action closure because the disabled state can also influence accessibility and presentation.

**Accessibility.** A button should have an understandable accessible label.

```swift
Button {
    print("Send requested")
} label: {
    Image(systemName: "arrow.up.right")
}
.accessibilityLabel("Send money")
```

This helps VoiceOver users understand the button's purpose.

## 10. Incremental NPay implementation — interactive quick actions

Previously QuickAction was a static VStack. We'll convert it into a reusable button that accepts an action closure.

```swift
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
```

**What's new?** QuickAction now has `let action: () -> Void`. This is a closure property. The parent decides what should happen when the button is tapped. The reusable component handles presentation and interaction.

**Important ownership detail.** Because the action is stored in the QuickAction value, it can capture other objects. When we later pass closures that capture ViewModels or services, we'll revisit ownership and ARC.

## 11. Use QuickAction in ContentView

```swift
HStack(spacing: 12) {

    QuickAction(
        symbol: "arrow.up.right",
        title: "Send"
    ) {
        print("Send tapped")
    }

    QuickAction(
        symbol: "arrow.down.left",
        title: "Request"
    ) {
        print("Request tapped")
    }

    QuickAction(
        symbol: "clock",
        title: "History"
    ) {
        print("History tapped")
    }
}
```

Notice the trailing closure syntax. Each QuickAction initializer receives the corresponding action closure. The same reusable view now supports three different behaviors.

## 12. Behind the scenes — how the parent passes behavior

QuickAction event architecture: ContentView (creates QuickAction and supplies closure) → QuickAction (stores title, symbol and action) → Button (uses the supplied action as its activation handler) → user tap (SwiftUI activates the relevant Button) → closure execution (the behavior defined by ContentView runs).

**Why is this good architecture?** The reusable view doesn't need to know about payment processing, transaction history, or navigation. It simply exposes an action. The parent decides what the action means. This separation will become important when we introduce MVVM and dependency injection.

## 13. Debug the event in Xcode

In ContentView.swift, set a breakpoint on `print("Send tapped")`. Run NPay with Command + R. Tap Send. Xcode should pause at the breakpoint. Inspect the call stack in the debug navigator. You'll see application code involved in the action, along with framework-related execution frames. The exact call stack depends on the SwiftUI and OS versions.

**Trainer question.** Does tapping Send recreate the entire application process? No. The existing application process handles the [text cut off here]

## Part 2: Complete Button Engineering Lab

We'll finish Lesson 2.7 before moving to @State. Three deeper questions: (1) How does a reusable QuickAction pass a tap back to ContentView? (2) What exactly happens when we pause a button action in Xcode? (3) What are the memory, performance, and accessibility implications?

## 14. Build the complete interactive NPay screen

We will preserve our existing NPay title, balance card, and quick actions. For this lesson, the actions will print messages to Xcode's console. They will not yet change the UI.

(Code: the complete `ContentView.swift` — `ContentView` with the header, `BalanceCard()` and the Section 11 `HStack(spacing: 12)` of three `QuickAction`s with print actions; `BalanceCard` as in Lesson 2.6; `QuickAction` as in Section 10; `#Preview`. It runs in `tools/sim2_7/App.swift`.)

## 15. Behind the scenes — who actually owns the action?

```swift
QuickAction(
    symbol: "arrow.up.right",
    title: "Send"
) {
    print("Send tapped")
}
```

The closure is created in ContentView. The QuickAction struct stores it in its action property. Inside QuickAction.body, that closure is supplied to Button.

Follow the closure: ContentView (defines the Send action closure) → QuickAction initializer (receives the closure as an argument) → QuickAction.action (stores the closure value) → `Button(action: action)` (uses it as the activation handler) → user taps Send (SwiftUI activates the button) → closure executes (`print("Send tapped")`).

**Important insight.** The reusable QuickAction does not need to know what sending money means. It knows only how to display an action and invoke its closure. That is a useful separation between presentation and application behavior.

## 16. Investigate closure capture and ARC

In Unit 1, we learned that closures can capture values and references.

```swift
final class PaymentService {
    func send() {
        print("Sending payment")
    }
}

let service = PaymentService()

let action = {
    service.send()
}
```

The closure captures the service reference. If the closure is stored by a long-lived object, it can extend the lifetime of captured references.

**Does every Button closure cause a retain cycle?** No. A retain cycle requires a strong-reference cycle. For example, a service retaining a closure that strongly captures that same service can create a cycle. Our current NPay actions simply call print, so they do not introduce such a cycle.

**Senior engineer question.** Should we always write [weak self] inside every SwiftUI button action? No. Capture strategies depend on ownership relationships. Adding weak references indiscriminately is not a substitute for understanding object lifetimes.

## 17. Debug a real tap using Xcode

Step 1 — set a breakpoint on `print("Send tapped")` (click the gutter). Step 2 — run NPay (Command + R); tap Send in the Simulator; Xcode should pause at the breakpoint. Step 3 — open the Debug navigator (Command + 7) to see the current execution context and call stack; the exact framework frames can differ by iOS and Xcode version. Step 4 — in the debug console, try `bt` (a backtrace for the current thread) and `thread list` (the threads in the process).

**What should you observe?** The action is executing inside the existing NPay process. The app was not rebuilt when you tapped the button. SwiftUI and the underlying platform handled the interaction and invoked your closure.

## 18. Why must button actions remain responsive?

```swift
Button("Send") {
    Thread.sleep(forTimeInterval: 3)
    print("Finished")
}
```

If executed on the main thread, this blocks it for three seconds. During that time, normal UI event handling and rendering responsiveness can suffer.

**Better architectural direction.** Later, when NPay sends a payment request, we'll use an asynchronous service:

```swift
Button("Send") {
    Task {
        // Call an asynchronous payment service.
    }
}
```

This is only the structure of the future implementation. Creating a Task does not automatically make synchronous CPU-intensive work safe for the main actor. We'll revisit this in the networking and concurrency units.

## 19. Accessibility and interaction design

Our quick-action buttons contain both an image and a text label. This is good because the label communicates the action's meaning. We can explicitly configure accessibility:

```swift
Button(action: action) {
    VStack(spacing: 8) {
        Image(systemName: symbol)
        Text(title)
    }
}
.accessibilityLabel(title)
```

**Why not use only an icon?** Icons can be ambiguous. A payment arrow may mean Send, Transfer, Upload, or Share depending on context. A text label improves clarity.

**What about touch targets?** Apple's interface guidance commonly recommends touch targets of approximately 44 × 44 points or larger. Our quick actions should provide comfortable interactive regions.

## 20. Senior engineer knowledge check

1. When does a Button action closure execute? — Every time body is evaluated / **When the button is activated** / During compilation
2. What does QuickAction store? — A function name as a String / **A closure value** / A UIKit event object
3. Does every captured reference automatically create a retain cycle? — Yes / **No**
4. Should long synchronous work run directly in a button action on the main thread? — Yes / **No**
5. What is hit testing? — **Finding the tapped interactive view** / Compiling the button / Measuring network latency
6. Why use a reusable QuickAction component? — **To separate presentation from behavior** / To create a separate process / To avoid Swift closures

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 21. Final Lesson 2.7 checkpoint

At this point, NPay has three interactive quick actions. Each action invokes a closure supplied by ContentView. The balance remains hardcoded, which is intentional.

We've now completed the conceptual material and provided the practical debugging procedure. You'll have verified the lab once all three buttons print the expected messages and the Send breakpoint is hit in Xcode.

**Next — Lesson 2.8: @State and Reactive UI.** We'll replace the hardcoded demo balance with SwiftUI-managed state and make NPay respond visibly to user interactions. That lesson will connect property wrappers, value semantics, view identity, state storage, dependency tracking, and rendering updates.

## Deck changes

The deck (`index.html`, built by `tools/gen2_7.py`, 37 slides) follows Sections 1–21 (both parts), grouped into 8 Parts:
the milestone (1, 21), Button (2, 7), creation vs activation (3), from tap to closure (4, 13, 17), hit testing (5–6),
styles, disabled and accessibility (8, 9, 19), QuickAction as a button (10–12, 14–15), captures and responsiveness (16, 18);
then recap, review (20), next, lab, end.

**How the evidence was gathered.** Finger taps cannot be scripted in this setup (no UI-test project, no assistive access
to the Simulator). The evidence app (`tools/sim2_7/`, `sh tools/sim2_7/run.sh`) turns simulator accessibility on and
activates buttons through their accessibility elements, the path VoiceOver uses; this runs the real Button action.
Every slide that shows this says so.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5)
- Sections 2, 7: printed types `Button<Text>` and `Button<VStack<TupleView<(Image, Text)>>>`.
- Section 3: the 5-step stepper (only step 1 shared) is drawn with **authored** steps 2–5; a parent changed three times: `PaymentView.body` evaluated 4 times, "Payment requested" never printed.
- Sections 4, 13, 17: inside the Send action, `Thread.isMainThread` was true and `Thread.callStackSymbols` showed the closure, `MainActor.assumeIsolated`, `ButtonAction.callAsFunction()`, then the accessibility activation frames (a finger tap would show touch frames there). The breakpoint / `bt` / `thread list` procedure is on the slide and in the lab.
- Sections 5–6: hit testing itself is **not measured** (no scripted taps); the tiles' accessibility frames (115 × 72, 115 × 72, 115 × 78 pt) are shown against the 44 × 44 pt guideline.
- Section 8: the style comparison is replaced by a screenshot of `.plain`, `.bordered`, `.borderedProminent` and a disabled prominent button.
- Section 9: activating a disabled "Send Money" ran nothing (accessibility reported it not enabled); "Request Money" ran.
- Sections 10–15: `type(of: quickAction.action)` printed `() -> ()`; all three quick actions activated: "Send tapped", "Request tapped", "History tapped"; before/after screenshots.
- Section 16: the `PaymentService` example was run on the Mac with a `deinit` and a capture list (**adapted**: the text's version uses `let`): the service outlived its variable until the closure was released.
- Section 18: with a main-thread timer every 0.5 s, the 3-second sleep in an action silenced it from 1.5 s to 4.6 s.
- The text's Section 13 is cut off mid-sentence ("The existing application process handles the …"); the deck states the point (same process, nothing rebuilt).

**Authored (flagged)**
- Review: the text's 6 questions (answers authored), plus a predict item (body evaluated 4 times → 0 actions) and a spaced item from 2.6.
- Outcomes, "Where we are", recap, "Where this goes next" (2.8 from the text), lab with expected results.

**Wording**
- "Trainer question" / "Trainer insight" / "Senior engineer question" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding". The note between the two parts ("before 2.8, 2.7 completed?") is not part of the deck.
