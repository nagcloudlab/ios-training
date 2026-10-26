# Unit 3 · Lesson 3.6 — SwiftUI Animations & Transitions

> Lesson text as shared, in two pieces: Sections 1–15 (cut off inside Section 15's experiment list) and "Part 2:
> Animation Internals, Experiments & Engineering Review" (Sections 15–23). Interactive widgets are described in
> brackets. The deck (`index.html`, built by `tools/gen3_6.py`) follows both. The text ends by naming its next
> implementation checkpoint; the small integration we made is **authored** and listed at the end. Evidence and authored
> additions are listed under "Deck changes".

NPay iOS Engineering Masterclass · Incremental Development · Animation Transactions · Rendering Internals

In Lesson 3.5, we made NPay preserve payment drafts across tab switches and sheet dismissal. Now we'll make NPay feel more polished by introducing animations. But we're not going to learn animations as visual decoration alone. We'll investigate how SwiftUI animates state changes, how interpolation works, how transitions differ from animations, and how to avoid performance problems.

Our engineering question: when NPay's balance changes from ₹25,000 to ₹23,500, how does SwiftUI animate the change without manually updating every frame?

## 1. Our NPay milestone

We'll introduce three animations: a smooth balance update; an animated transaction insertion; a payment-success transition. Let's begin with a conceptual demonstration.

[NPay Animation Lab: Available Balance ₹19,000, Demo Account; "Simulate ₹1,500 payment", Reset; "Demo Payment Recorded"; Recent Transactions: Demo Payment −₹1,500 (×4), Coffee Shop −₹250, Electricity Bill −₹1,200. Caption: "Interactive state-change preview. We'll implement native SwiftUI animations in Xcode."]

## 2. First concept — what is animation in SwiftUI?

Consider a view:

```swift
Circle()
    .frame(width: 100, height: 100)
```

Now imagine changing its width from 100 to 200. Without animation, SwiftUI updates the presentation to the new size. With animation, SwiftUI can interpolate supported animatable properties between the old and new values.

**Key idea.** Animation describes how a visual value changes over time. It does not require us to manually render each intermediate frame.

## 3. First Xcode experiment — withAnimation

Create AnimationExperiment.swift:

```swift
import SwiftUI

struct AnimationExperiment: View {
    @State private var expanded = false

    var body: some View {
        VStack(spacing: 30) {
            Circle()
                .fill(.blue)
                .frame(
                    width: expanded ? 180 : 80,
                    height: expanded ? 180 : 80
                )

            Button("Toggle Size") {
                withAnimation(.easeInOut(duration: 0.5)) {
                    expanded.toggle()
                }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}

#Preview {
    AnimationExperiment()
}
```

Run the preview. Tap Toggle Size. The circle grows and shrinks smoothly.

**What's happening?** expanded is an @State property. When it changes inside withAnimation, SwiftUI associates an animation with the resulting update. Eligible animatable properties can transition smoothly.

## 4. Behind the scenes — how withAnimation works

[SwiftUI animation pipeline — a 6-stage stepper; only Stage 1 was shared: "1. User taps button. SwiftUI executes the action closure." Caption: "Conceptual animation flow. Exact scheduling and rendering internals are managed by SwiftUI."]

Trainer insight: withAnimation does not repeatedly mutate the state value to intermediate values. The state changes to its target value. SwiftUI handles interpolation for supported animatable properties during presentation.

## 5. Animation curves — how does motion change?

SwiftUI provides several animation styles. Common examples:

```swift
.linear(duration: 0.5)
.easeIn(duration: 0.5)
.easeOut(duration: 0.5)
.easeInOut(duration: 0.5)
.spring(response: 0.4, dampingFraction: 0.7)
```

Different curves produce different motion characteristics.

[Interactive easing explorer: Linear / Ease In / Ease Out / Ease In Out; animation time 50%, interpolated position 25%. Caption: "Illustrative easing functions, not exact reproductions of SwiftUI's animation curves."]

**Which should NPay use?** For ordinary UI transitions, ease-in-out is a reasonable starting point. For playful feedback, a spring animation can feel natural. For financial confirmation, prefer restrained motion that communicates success without distracting the user.

## 6. Implicit versus explicit animations

SwiftUI supports different ways to associate animations with changes.

**Explicit animation**

```swift
withAnimation(.easeInOut(duration: 0.3)) {
    expanded.toggle()
}
```

The animation is associated with the state update.

**Value-driven animation**

```swift
Circle()
    .frame(
        width: expanded ? 180 : 80,
        height: expanded ? 180 : 80
    )
    .animation(
        .easeInOut(duration: 0.3),
        value: expanded
    )
```

This associates animation with changes to a specific observed value.

**Important distinction.** Value-driven animation can affect animatable changes in the modified subtree when the specified value changes. It is not limited to a single property unless the modifier is scoped appropriately.

## 7. Transitions — appearance and disappearance

Animations and transitions are related but different. An animation interpolates changes in animatable values. A transition describes how a view enters or leaves the hierarchy. Example:

```swift
if showSuccess {
    Text("Payment Successful")
        .transition(.opacity)
}
```

Now toggle it with animation:

```swift
withAnimation {
    showSuccess.toggle()
}
```

The text fades in and out.

**Why does identity matter?** Transitions are associated with insertion and removal of views. If SwiftUI considers a view to have the same identity and only its content changes, a transition may not occur. This connects directly to Lesson 3.5.

## 8. Interactive transition explorer

[Opacity / Slide / Scale; "Success view removed"; Insert success view. "In Xcode, apply .transition(.{transition}) and animate the insertion/removal with withAnimation." Caption: "This illustrates view insertion and removal; actual native transition animation is implemented in SwiftUI."]

## 9. Animate NPay's balance card

Our current balance card displays `Text(Money.display(balancePaise))`. When the balance changes, the text updates immediately. SwiftUI provides contentTransition for certain content changes. For numeric values:

```swift
Text(Money.display(balancePaise))
    .font(.largeTitle.bold())
    .contentTransition(.numericText())
    .animation(
        .easeInOut(duration: 0.4),
        value: balancePaise
    )
```

This can animate numeric text changes.

**Important nuance.** numericText() is a presentation effect for text changes. It doesn't change how money is calculated. Our authoritative demo amount remains an integer number of paise.

## 10. Animate transaction insertion

Our transaction history uses:

```swift
ForEach(transactions) { transaction in
    TransactionRow(transaction: transaction)
}
```

When a new transaction is inserted, we can associate an animation with the state change:

```swift
withAnimation(.easeInOut(duration: 0.3)) {
    transactions.insert(
        newTransaction,
        at: 0
    )
}
```

For a custom VStack or LazyVStack, row transitions can be applied to inserted views. For List, animation behavior is more platform-managed and may differ.

**Senior engineer insight.** Stable transaction identity is essential for predictable insertion and removal animations. This is why we studied Identifiable and stable IDs in Lesson 2.10.

## 11. Build NPay's animated success screen

Now let's improve PaymentSuccessScreen.

```swift
import SwiftUI

struct PaymentSuccessScreen: View {
    let transactionID: UUID
    let onDone: () -> Void

    @State private var showContent = false

    var body: some View {
        VStack(spacing: 24) {

            if showContent {
                Image(systemName: "checkmark.circle.fill")
                    .font(.system(size: 80))
                    .foregroundStyle(.green)
                    .transition(
                        .scale.combined(with: .opacity)
                    )
            }

            Text("Payment Recorded")
                .font(.title.bold())

            Text("Your demo payment was successful.")
                .foregroundStyle(.secondary)

            Text(transactionID.uuidString)
                .font(.caption2.monospaced())
                .multilineTextAlignment(.center)

            Button("Back to Dashboard") {
                onDone()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
        .navigationTitle("Payment Success")
        .navigationBarBackButtonHidden()
        .onAppear {
            withAnimation(
                .spring(
                    response: 0.45,
                    dampingFraction: 0.7
                )
            ) {
                showContent = true
            }
        }
    }
}
```

**What happens?** When the success screen appears, showContent changes from false to true. The checkmark enters the hierarchy. SwiftUI applies the combined scale and opacity transition. The spring animation controls how the transition progresses.

## 12. Behind the scenes — animation transactions

SwiftUI has a Transaction type that carries animation-related context through view updates. When you call:

```swift
withAnimation(.easeInOut) {
    showContent = true
}
```

SwiftUI associates an animation with the relevant update transaction. This allows the framework to coordinate animation behavior for affected animatable properties.

**Important distinction.** A SwiftUI Transaction is not the same as our NPay financial Transaction model. They share a name but represent completely different concepts. To avoid confusion in a larger application, we might eventually rename our domain model to PaymentTransaction.

## 13. Performance — animations are not free

Animations can involve layout, rendering, compositing, or combinations of these operations. Some effects are relatively inexpensive. Others can trigger more work. For example: animating opacity can often be compositing-friendly; animating transforms can be efficient in many cases; animating complex layout changes can require repeated layout work; animating large, complex collections can be expensive. The actual cost depends on the view hierarchy and rendering environment.

**Senior engineer principle.** Measure performance using Instruments rather than assuming a particular animation is always cheap.

## 14. Accessibility — Reduce Motion

Some users prefer reduced motion. SwiftUI provides an environment value:

```swift
@Environment(\.accessibilityReduceMotion)
private var reduceMotion
```

We can adapt animations:

```swift
let animation: Animation = reduceMotion
    ? .linear(duration: 0.01)
    : .spring(
        response: 0.45,
        dampingFraction: 0.7
    )

withAnimation(animation) {
    showContent = true
}
```

For significant motion, a better reduced-motion experience may avoid the transition entirely rather than merely making it extremely fast. We'll study accessibility in greater depth in Lesson 3.10.

## 15. Xcode experiments

Run these experiments using the NPay application from Lesson 3.5: (1) Add `.contentTransition(.numericText())` to BalanceCard. (2) Change the balance using the demo editor. (3) Compare .linear, .easeInOut, and .spring. (4) Animate the … [the first piece ends here]

## Part 2: Animation Internals, Experiments & Engineering Review

NPay iOS Engineering Masterclass · Continuing from Section 15. We've learned withAnimation, animation curves, transitions, contentTransition, and the SwiftUI animation transaction model. Now we'll finish the lesson by investigating how animations interact with view identity, how SwiftUI renders intermediate frames, and how to debug animation behavior in Xcode.

## 15. Xcode experiments — continued

Complete these experiments using NPay Lesson 3.5.

| Experiment | What to investigate |
|---|---|
| Numeric text animation | Does the balance change smoothly? |
| Linear versus spring | How does motion behavior differ? |
| Insert a transaction | Does stable identity support insertion animation? |
| Success transition | How does scale + opacity affect presentation? |
| Remove withAnimation | Does the transition still animate? |
| Enable Reduce Motion | Does NPay respect accessibility preferences? |

**Experiment A — Numeric balance transition.** Modify BalanceCard (the Section 9 code) and change the balance using our demo editor. Observe how the text changes.

**Experiment B — Compare animation curves.** Try `.animation(.linear(duration: 0.5), value: balancePaise)`, then `.animation(.easeInOut(duration: 0.5), value: balancePaise)`, then `.animation(.spring(response: 0.45, dampingFraction: 0.7), value: balancePaise)`. Compare the motion.

## 16. The deeper question — does SwiftUI update state every animation frame?

Consider:

```swift
withAnimation(.easeInOut(duration: 1.0)) {
    expanded = true
}
```

Does SwiftUI change expanded through intermediate values? No. expanded is a Boolean. It changes to true. SwiftUI then coordinates animation of eligible presentation properties.

[Model state versus animated presentation: State — target value true, changes once; Presentation — intermediate sizes 80 → 110 → 145 → 180 (illustrative animation frames).]

**Senior engineer insight.** SwiftUI separates the logical target state from its animated presentation. This is why we can write declarative animation code instead of manually calculating every frame.

## 17. How does SwiftUI know what can animate?

SwiftUI uses the Animatable protocol and related mechanisms to support interpolation. For example, many view modifiers expose animatable values such as size, offset, opacity, and shape parameters. The central idea is that animatable data can be interpolated between two values.

**Simplified example.** Suppose a width changes from 80 to 180. We can describe linear interpolation mathematically: v(t) = v₀ + (v₁ − v₀)t, where v₀ is the starting value, v₁ is the target value, and t is normalized progress between 0 and 1. For example, at t = 0.5: v(0.5) = 80 + (180 − 80)(0.5) = 130. The midpoint width is 130 points under linear interpolation.

[Interactive interpolation explorer: animation progress 50%, interpolated diameter 130 points. Caption: "Linear interpolation illustration; screen rendering may use different physical pixel scaling."]

**Important distinction.** Not every property is directly animatable. Some properties change discretely. Others require an explicit Animatable implementation or an appropriate animatable modifier.

## 18. Build our own Animatable modifier

Now let's connect SwiftUI animations to Swift protocols. We'll create a custom modifier that animates a number.

```swift
import SwiftUI

struct AnimatedNumber: AnimatableModifier {
    var value: Double

    var animatableData: Double {
        get { value }
        set { value = newValue }
    }

    func body(content: Content) -> some View {
        Text(
            value,
            format: .number.precision(.fractionLength(0))
        )
        .font(.largeTitle.bold())
    }
}
```

**How does it work?** animatableData exposes the value SwiftUI can interpolate. As the animation progresses, SwiftUI can supply intermediate values through this property. The modifier uses the current interpolated value to construct its display.

**Apply it**

```swift
Text("")
    .modifier(
        AnimatedNumber(value: Double(balancePaise) / 100)
    )
    .animation(
        .easeInOut(duration: 0.5),
        value: balancePaise
    )
```

This is an educational example. For NPay's normal balance display, `.contentTransition(.numericText())` is simpler and generally preferable.

## 19. Why animation and identity are connected

Remember Lesson 2.10 — Identifiable. And Lesson 3.5 — view identity. Suppose a transaction row has a stable ID: `Transaction(id: id, ...)`. When a new transaction is inserted, SwiftUI can associate existing rows with their previous identities. This helps the framework understand which views are new and which remain. But if we generate a new ID every time data is refreshed, SwiftUI may treat existing transactions as new elements. That can produce unexpected insertion/removal animations and lost row-local state.

**Engineering rule.** Stable identity is a prerequisite for predictable collection transitions.

## 20. What happens when animation is interrupted?

Imagine the user taps Add Money repeatedly. The balance changes again before the previous animation finishes. SwiftUI may retarget or otherwise coordinate the animation from its current presentation state toward the latest target. The exact behavior depends on the animation type, properties, and transaction context.

**Why does this matter?** Financial interfaces should not make users wait for an animation before the underlying state becomes correct. The state should update immediately according to the application's logic. The animation is presentation feedback, not the authoritative business operation.

## 21. Performance — when animation becomes expensive

| Animation | Typical work involved |
|---|---|
| Opacity | Often compositing |
| Scale | Transform/compositing in many cases |
| Offset | Position or transform-related presentation |
| Frame changes | Can involve layout |
| Complex list changes | Collection reconciliation and layout |
| Custom drawing | May involve repeated drawing work |

These are tendencies, not guarantees.

**Debug with Instruments.** In Xcode, use Product → Profile to open Instruments. Depending on the Xcode version, relevant tools may include animation hitch analysis, Core Animation, and Time Profiler. Investigate: frame hitches; excessive layout work; CPU usage during animation; main-thread blocking; repeated expensive view evaluation.

**Senior engineer principle.** Don't optimize based on assumptions. Measure the actual behavior on a device representative of your users.

## 22. Accessibility — make motion optional

Let's improve the animated success screen.

```swift
@Environment(\.accessibilityReduceMotion)
private var reduceMotion

@State private var showContent = false
```

Then:

```swift
.onAppear {
    if reduceMotion {
        showContent = true
    } else {
        withAnimation(
            .spring(
                response: 0.45,
                dampingFraction: 0.7
            )
        ) {
            showContent = true
        }
    }
}
```

This avoids the entrance animation when the user prefers reduced motion. It is generally better than forcing a very fast animation that could still be uncomfortable.

## 23. Senior engineer knowledge check

1. Does withAnimation repeatedly mutate a Boolean state through intermediate values? (Yes / No)
2. What is the role of Animatable.animatableData? (Expose interpolatable data / Store network responses / Manage navigation)
3. Why do stable transaction IDs matter for animations? (They help preserve logical view identity / They increase frame rate automatically / They create a new process)
4. Can frame animation involve layout work? (Yes / No)
5. Should animation determine whether a payment succeeded? (Yes / No)
6. Should NPay respect Reduce Motion? (Yes / No)

**Lesson 3.6 — Final checkpoint.** We've completed the conceptual coverage of SwiftUI animations and transitions, including animation transactions, interpolation, custom animatable modifiers, identity, performance, and accessibility. Our next implementation checkpoint is to integrate the animated balance card, transaction updates, and success feedback into the complete NPay application from Lesson 3.5.

Next — Lesson 3.7: Reusable SwiftUI Components & NPay Design System. We'll build reusable buttons, cards, typography, spacing, and styling primitives, while investigating how SwiftUI composition and environment propagation support a scalable design system.

## Integration through Lesson 3.6 (authored)

Applied to the Lesson 3.5 code and run in the simulator (`tools/sim3_6/App.swift`); everything else is unchanged.

- **Components/BalanceCard.swift**: the balance Text gets the Section 9 modifiers,
  `.contentTransition(.numericText())` and `.animation(.easeInOut(duration: 0.4), value: balancePaise)`.
- **Screens/PaymentSuccessScreen.swift**: the Section 11 screen with Section 22's Reduce Motion check
  (`@Environment(\.accessibilityReduceMotion)`; set `showContent` directly when it is on, otherwise inside the spring).
- Not added: an insertion animation on Home's recent transactions. In NPay the payment is recorded while the Payments
  tab is showing, so it would play unseen; the Animation Lab (`tools/sim3_6`) demonstrates the technique.

## Deck changes

The deck (`index.html`, built by `tools/gen3_6.py`, 45 slides) follows both pieces, grouped into 8 Parts: the milestone
(1), withAnimation (2–4, 16), animation curves (5), explicit, implicit, transactions (6, 12), transitions (7, 8, 11, 14,
22), balance and insertion (9, 10, 19), interpolation (16–18, 20), cost and review (13, 15, 21 and the integration); then
recap, review, next, lab, end.

**Evidence** (iPhone 17 simulator, iOS 26.5; app in `tools/sim3_6/`, rerun with `sh tools/sim3_6/run.sh`, one launch per
experiment via `runone.sh`). Two kinds: frames the app captured of its own window during an animation
(`drawHierarchy(afterScreenUpdates: false)`), labelled with measured times; and the value SwiftUI passed to an
`Animatable` modifier on each frame, printed with its time.
- AnimationExperiment (verbatim): seven frames after Toggle Size showing intermediate sizes.
- Curves, 80 → 180 on the same circle: linear(0.5) and easeInOut(0.5) 30 values each (60 fps), linear +3.3 per frame;
  spring(response 0.45, damping 0.7) 76 values, peak 184.1, settled at 1,285 ms. The Bool changed once in each run.
- Interruption (authored): linear 1 s 80 → 180, retargeted to 80 at 427 ms (value 120): no jump; it kept rising to
  129.0, then reached 80.0 at 1,437 ms.
- AnimatedNumber (text's code plus one line recording each value): 30 values from 24997 to 23500 for ₹25,000 → ₹23,500.
- Success screen (text's code): frames show the checkmark scaling and fading in (~123–347 ms); without `withAnimation`
  and with Reduce Motion on (`accessibilityReduceMotion: true`, set via the simulator's accessibility defaults) it is
  fully present in the first frame.
- Animation Lab (Section 1's demo, built natively with BalanceCard and a VStack of rows): frames show the digits rolling
  and the new row moving in from the top.
- Stable vs regenerated IDs (authored): refreshing the same data with the same IDs produced no appear/disappear; with new
  IDs, all three rows appeared and all three were removed.
- swiftc: our domain `Transaction` next to `withTransaction(Transaction(animation:))` → "cannot convert value of type
  'Transaction' to expected argument type 'SwiftUICore.Transaction'" and "extra argument 'animation' in call";
  `SwiftUI.Transaction(...)` compiles.
- swiftc: the text's AnimatedNumber fails in plain Swift 6 mode ("conformance of 'AnimatedNumber' to protocol
  'Animatable' crosses into main actor-isolated code"); it compiles in Swift 5 mode and with default MainActor isolation
  (the Xcode 26 app template's setting); `nonisolated var animatableData` fixes it everywhere. The SDK marks
  `AnimatableModifier` deprecated ("use Animatable directly").
- Not done: Instruments profiling (the simulator is not a representative device; stated on the slide).

**Authored (flagged)**
- The integration above; the Animation Lab, interruption, ID-refresh and Transaction-clash experiments; row transition
  `.move(edge: .top).combined(with: .opacity)` in the lab.
- Section 4's stages 2–6 (only stage 1 shared), marked conceptual; the curve chart drawn from measured values (the text's
  explorer was illustrative).
- The experiments table answers Section 15 with the Animation Lab instead of the demo balance editor (dropped in the 3.3
  code, which follows that text's project structure).
- Review: the text's 6 questions (options reordered) plus two predict items (spring peak; transition without
  withAnimation) and a spaced item from 3.5; 2 of 9 verdicts are "No".
- Outcomes, "Where we are", recap, "Where this goes next" (3.7 and 3.10 as the text names them; Unit 8 for performance),
  lab, end slide.

**Wording**
- "Trainer insight" and "Senior engineer insight / principle / knowledge check" became neutral callouts and "Check your
  understanding".
