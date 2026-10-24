# Unit 2 · Lesson 2.11 — TextField, User Input, Validation & Keyboard Focus

> Lesson text as shared, in three pieces: Part 1 (Sections 1–13 and the heading of 14), "Part 2: Validation,
> Debugging & Engineering Assessment" (Sections 14–20), and "Complete Working Code" (the full ContentView.swift with a
> test table). Interactive widgets are described in brackets. The deck (`index.html`, built by `tools/gen2_11.py`)
> follows Sections 1–20. Simulator evidence and authored additions are listed at the end under "Deck changes".

NPay Engineering Lab · Incremental Development · SwiftUI Internals · State & Binding

In Lesson 2.10, we built NPay's transaction history using ForEach, Identifiable, and reusable transaction rows. Now we're going to make NPay accept input from the user.

Our engineering challenge: **When someone types 1500 into a payment amount field, how does that text travel from the iPhone keyboard into Swift state, and how does SwiftUI keep the screen synchronized?** We'll explore TextField, bindings, keyboard events, validation, focus management, and data flow—then add a payment-entry form to our existing NPay application.

## 1. Our next NPay milestone

[Interactive form illustration: the balance card (₹25,000) and "Send Money · Demo" with Recipient, Amount (₹) and "Continue demo". No actual payment is performed.] This is what we'll implement incrementally in Xcode.

## 2. What is TextField?

`Text("NPay")` displays content. `TextField("Enter amount", text: $amount)` is a SwiftUI control that allows the user to edit text. The important difference is that it requires a connection to mutable state.

| Text | TextField |
|---|---|
| Displays text | Accepts editable text |
| Can receive a String value | Commonly receives Binding<String> |
| No keyboard interaction | Integrates with text input and keyboard |
| Read-only presentation | Two-way data flow |

**Connect to Lesson 2.9.** `@State private var amount = ""` — the property amount is a String. The expression `$amount` produces a `Binding<String>`. That binding allows the text field to read and write the value.

## 3. First Xcode experiment — the smallest TextField

```swift
import SwiftUI

struct TextFieldExperiment: View {
    @State private var name = ""

    var body: some View {
        VStack(spacing: 20) {
            TextField("Enter your name", text: $name)
                .textFieldStyle(.roundedBorder)

            Text("Hello, \(name)")
        }
        .padding()
    }
}

#Preview {
    TextFieldExperiment()
}
```

Run the preview or Simulator. Type Ravi. You should see: Hello, Ravi.

**What just happened?** We did not manually update the Text. The text field changed the state through its binding. SwiftUI then updated the dependent display.

## 4. Behind the scenes — keyboard to SwiftUI state

This is the most important part of today's lesson. When the user types a character, several systems cooperate. [From keyboard input to visible SwiftUI update — a 6-stage stepper; only stage 5 was included: "@State changes — the view's owned state receives the new String value." Conceptual flow. The platform's text-input implementation includes additional handling for composition, selection, autocorrection, and input methods.]

**Important nuance.** Text input is not always one physical key press producing one Unicode character. Languages such as Tamil and Hindi can involve text composition and multiple input events. That's why we should use the platform's text-input APIs rather than attempting to process raw keyboard events for ordinary text entry.

## 5. Why does TextField require a Binding?

The text field needs to do two things: (1) read the current value to display it; (2) write the edited value when the user types. A plain String supplies only a value. A `Binding<String>` supplies a read/write connection. [@State amount → Binding<String> → TextField.]

**Trainer question.** If we write `text: amount` instead of `text: $amount`, will the common string-binding initializer compile? No. It expects a binding, not a plain string value.

## 6. Why should payment amounts initially be Strings?

Suppose the user is entering 1, 15, 150, 1500. During editing, the field contains text. If we immediately convert every intermediate value into a number, we can create awkward editing behavior. For example, users may temporarily enter an empty string or a decimal separator. A useful design is `@State private var amountText = ""`, then validate and parse the text when needed.

**Important production consideration.** For real financial calculations, don't use binary floating-point values such as Double as the authoritative representation of money. Prefer an appropriate decimal or integer minor-unit representation, combined with domain validation. For this Unit 2 lesson, we'll keep the payment form as a UI-only demo.

## 7. Keyboard types — .keyboardType()

`TextField("Amount", text: $amountText).keyboardType(.decimalPad)` influences the keyboard presented on supported devices.

**But does decimalPad guarantee valid input?** No. Keyboard type is a user-experience hint, not a security or validation boundary. Text can still arrive through paste, hardware keyboards, accessibility input, or other mechanisms.

**Senior engineer principle.** Always validate input independently of keyboard configuration.

## 8. Input validation — separate syntax from business rules

Our demo rules — a valid amount must: be a valid positive decimal number; contain no more than two fractional digits; not exceed the available demo balance. For learning, we can write a computed property:

```swift
private var parsedAmount: Decimal? {
    Decimal(
        string: amountText,
        locale: Locale(identifier: "en_US_POSIX")
    )
}
```

This converts a decimal string into a Decimal value when possible. However, parsing alone doesn't enforce our full requirements. For example, we also need to reject negative amounts and excessive decimal precision. We'll implement those rules in our payment form.

## 9. Focus management — what is @FocusState?

Imagine the user taps the amount field. The keyboard appears. Later, the user taps Done or continues to another field. SwiftUI provides @FocusState for managing focus: `@FocusState private var amountFocused: Bool`, then `TextField("Amount", text: $amountText).focused($amountFocused)`. We can dismiss focus programmatically: `amountFocused = false`.

**How is FocusState different from State?** @State manages local view state. @FocusState connects a property to the focus state of focusable controls. Both use property-wrapper syntax, but they represent different concerns.

## 10. Build our reusable NPay payment form

(Code: `struct PaymentForm: View` — `@State recipient`, `@State amountText`, `@FocusState private var focusedField: Field?` with `enum Field: Hashable { case recipient, amount }`; a VStack with "Send Money · Demo", the recipient TextField (no autocapitalization, autocorrection disabled, rounded border, `.focused($focusedField, equals: .recipient)`, `.submitLabel(.next)`, `.onSubmit { focusedField = .amount }`), the amount TextField (`.keyboardType(.decimalPad)`, rounded border, focused equals .amount), and a "Continue Demo" button (clears focus, prints the recipient and amount) `.disabled(!isValid)`; padded with a pale blue rounded background. `isValid`: trimmed recipient not empty; amount matches `^[0-9]+(\.[0-9]{1,2})?$`; parses as Decimal (en_US_POSIX); greater than zero.)

What did we introduce? @State for recipient and amount text; TextField for editable input; Binding<String> through $recipient and $amountText; @FocusState for keyboard focus; .keyboardType(.decimalPad) for amount entry; .disabled(!isValid) for form validation; .onSubmit for moving focus. This form validates positive amounts with up to two decimal places, but it doesn't yet enforce the available balance or perform any transfer.

## 11. Integrate PaymentForm into NPay

Our existing ContentView already contains `BalanceCard(balance: balance)` and `BalanceEditor(balance: $balance)`. Add `PaymentForm()` below the quick actions, inside the existing ScrollView. [Current architecture: ContentView (owns balance and transactions) → BalanceCard, BalanceEditor, QuickAction, PaymentForm (owns input and focus state), TransactionHistory.]

## 12. Behind the scenes — focus and keyboard behavior

When a TextField becomes focused, the platform's text-input infrastructure coordinates the editing session. The keyboard is part of the system input experience, not a SwiftUI view that we manually construct. SwiftUI integrates with platform text-input behavior and updates the binding as editing occurs.

**What about the main thread?** UI editing and SwiftUI state changes must respect their actor-isolation requirements. Avoid expensive synchronous validation or network requests on every keystroke. For complex validation, we may debounce input or move expensive work into an appropriate asynchronous service.

## 13. Xcode experiments

A — Binding: remove `$` from `text: $recipient`; observe the compiler error; restore it. B — Keyboard type: change `.decimalPad` to `.numberPad`; observe the keyboard difference in the Simulator. C — Validation: try entering 0, -100, 12.345, and 1500; observe when Continue is enabled. D — Focus: tap the recipient field, type a value, then press Next; observe how focus moves to the amount field. E — Input composition: try entering Tamil text into the recipient field using an appropriate keyboard; observe that TextField manages text composition rather than simply handling individual ASCII characters.

## Part 2: Validation, Debugging & Engineering Assessment

We've built NPay's first payment form using TextField, @State, @FocusState, bindings, and validation. Now let's complete the lesson by examining how SwiftUI handles input changes, why validation must be separated from keyboard configuration, and how to debug the form in Xcode.

## 14. Senior engineer knowledge check

1. Why does TextField commonly accept Binding<String>? — **To read and write editable text** / To create a new thread / To store data in a database
2. Does .decimalPad guarantee valid decimal input? — Yes / **No**
3. What does @FocusState manage? — **Control focus** / Network state / Application signing
4. Why is String useful while editing an amount? — **It preserves intermediate text such as empty input and decimal separators** / It automatically encrypts money / It eliminates validation
5. Should Double be used as the authoritative representation of money? — Yes / **No**
6. Does a disabled Continue button replace backend validation? — Yes / **No**
7. What happens when TextField writes through $amountText? — **The state owner receives the updated String** / A new independent TextField state is created / The application recompiles

(Answers in bold were not marked in the shared text; they follow from the lesson.)

## 15. Behind the scenes — why every keystroke can affect SwiftUI

Each accepted edit can update the bound string. If another view depends on amountText, SwiftUI can reevaluate its description.

```swift
VStack {
    TextField("Amount", text: $amountText)
        .textFieldStyle(.roundedBorder)

    Text("You entered: \(amountText)")
}
```

[Interactive text-state simulation: an amount input, "Current state amountText = ''", "You entered: —".]

**Senior engineer insight.** Don't perform expensive synchronous work inside body or on every text edit. For example, calling a remote API after every keystroke without control could create excessive network traffic. We'll study debouncing and asynchronous validation later.

## 16. Input validation — three separate responsibilities

Input experience (keyboard type, placeholder, focus and formatting) → client-side validation (required fields, syntax, amount limits and user feedback) → trusted business validation (authoritative balance, permissions, transaction rules and security). For NPay, our current form only performs local validation and prints a demo request. It does not perform a financial transaction.

## 17. Improve NPay — validate against the demo balance

Make the form accept a read-only balance (`let availableBalance: Int`), pass `PaymentForm(availableBalance: balance)` from ContentView, and end `isValid` with `return amount > 0 && amount <= Decimal(availableBalance)`.

If the available demo balance is ₹25,000:

| Entered amount | Valid? | Reason |
|---|---|---|
| 1500 | Yes | Positive and within balance |
| 25000 | Yes | Exactly equal to balance |
| 25001 | No | Exceeds balance |
| 0 | No | Must be positive |
| 12.345 | No | More than two decimal places |
| abc | No | Invalid numeric syntax |
| -500 | No | Negative amount |

The form now responds to changes in both amountText and availableBalance. **Behind the scenes.** PaymentForm receives the latest balance as an input value. Its computed isValid property uses that value alongside local input state. When either relevant input changes, SwiftUI can update the button's disabled state.

## 18. Debugging TextField in Xcode

```swift
TextField("Amount (₹)", text: $amountText)
    .keyboardType(.decimalPad)
    .textFieldStyle(.roundedBorder)
    .onChange(of: amountText) { oldValue, newValue in
        print("Old amount:", oldValue)
        print("New amount:", newValue)
    }
```

This uses the two-parameter onChange API available on modern iOS versions. Run NPay and type 1500. Observe the debug console. You'll see accepted changes to the text value.

**What should you learn?** onChange observes value changes. It is not a raw keyboard-event listener. For example, pasting text can change the value without a corresponding sequence of individual physical key presses.

## 19. Focus debugging

`@FocusState private var focusedField: Field?` with `enum Field: Hashable { case recipient; case amount }` — the enum identifies which input should have focus. Experiment — add a toolbar action to dismiss the keyboard, attached to the form's outer view:

```swift
.toolbar {
    ToolbarItemGroup(placement: .keyboard) {
        Spacer()

        Button("Done") {
            focusedField = nil
        }
    }
}
```

When the keyboard appears, the toolbar can provide a Done action to clear focus. The exact presentation depends on the platform and keyboard environment.

## 20. Final NPay checkpoint — Lesson 2.11

[ContentView (balance and transaction state) → BalanceCard, BalanceEditor, QuickAction, PaymentForm (TextField, validation, focus), TransactionHistory.] You should now be able to explain the complete flow: **Keyboard input → TextField → Binding → @State → Validation → Button enabled/disabled → SwiftUI update.**

**Lesson 2.11 complete.** We've covered TextField, editable state, binding, keyboard configuration, @FocusState, validation, onChange, and input debugging. Our NPay form now validates input against the current demo balance, but still does not initiate a real payment.

**Next — Lesson 2.12: Unit 2 Integration & Architecture Review.** We'll assemble the complete NPay dashboard, clean up the file structure, connect the demo payment form to local transaction simulation, and review every SwiftUI concept we've learned before advancing to Unit 3.

## Complete working code (Lessons 2.1–2.11)

(Code: the complete `ContentView.swift` — the 2.10 code plus `PaymentForm(availableBalance: balance)` between the quick actions and "Add Demo Transaction". `PaymentForm` now has the recipient placeholder "Recipient ID (e.g. ravi@npay)", the amount field's `onChange` logging, a red caption "Enter a valid amount within your balance." when the amount is non-empty and invalid, the keyboard toolbar with Done, and validation split into `isValid` (recipient non-empty and `isValidAmount`) and `isValidAmount` (regex, Decimal parse, `> 0`, `<= Decimal(availableBalance)`). Keep NPayApp.swift unchanged. It runs unchanged in `tools/sim2_11/App.swift`.)

Verify these experiments in Xcode:

| Test | Expected result |
|---|---|
| Enter recipient ravi@npay | Accepted |
| Enter amount 1500 | Continue enabled |
| Enter amount 0 | Continue disabled |
| Enter amount 12.345 | Continue disabled |
| Enter amount above balance | Continue disabled |
| Change demo balance | Amount validation updates |
| Tap Done on keyboard | Focus clears |
| Tap Continue Demo | Values printed in debug console |
| Add Demo Transaction | New row appears at the top |

**Important.** This is still a local learning application. Continue Demo logs the request; it does not deduct money, initiate a payment, or add a payment transaction. We'll implement a consistent local payment simulation in Lesson 2.12.

## Deck changes

The deck (`index.html`, built by `tools/gen2_11.py`, 35 slides) follows Sections 1–20 and the complete code, grouped into
8 Parts: a payment form (1, 20), TextField (2–3, 5), keyboard to state (4, 12), amounts as text (6, 8), keyboard types (7),
focus (9, 19), PaymentForm and validation (10–11, 16–17), debugging and checkpoint (13, 15, 18, 20); then recap,
review (14), next, lab, end.

**How the evidence was gathered.** In `tools/sim2_11/` (`sh tools/sim2_11/run.sh`), the complete code runs unchanged.
Fields are focused by making their `UITextField` first responder (what a tap does) and text is entered with
`UIKeyInput.insertText`, the protocol keyboards use; a paste uses `UITextField.paste`; buttons are activated through
accessibility as in 2.7–2.10. The real system keyboards appear in the screenshots.

**Evidence instead of illustrations** (iPhone 17 simulator, iOS 26.5)
- Section 3: typing Ravi logged name = "R", "Ra", "Rav", "Ravi"; screenshot with "Hello, Ravi" and the keyboard.
- Section 5: the real swiftc error without `$`: "cannot convert value 'recipient' of type 'String' to expected type 'Binding<String>', use wrapper instead"; printed `$amountText: Binding<String>`.
- Section 4: the 6-stage stepper (only stage 5 shared) is drawn with **authored** stages 1–4 and 6, marked conceptual.
- Sections 6, 8: typing 1500 logged "" → 1 → 15 → 150 → 1500; on the Mac, `Decimal(string:)` alone gave "12abc" → 12 and "1,500" → 1 (**added**: why parsing isn't validation); `0.1 + 0.2 == 0.3` is false for Double (0.30000000000000004) and true for Decimal (**added**).
- Section 7: screenshot of the decimal pad with the Done toolbar; a paste of "1500" produced a single onChange.
- Sections 9, 19: after return in the recipient field, the Amount field was first responder (onSubmit); printed `_amountFocused: FocusState<Bool>`, `$amountFocused: Binding`.
- Section 17: the text's validation table was run (Mac, swiftc) and matched exactly; in the simulator 25001 showed the red message with Continue disabled (screenshot); 25500 was invalid at ₹25,000 and became valid after "+ ₹1,000".
- Section 18 / complete code: Continue Demo printed "Demo payment request / Recipient: ravi@npay / Amount: 1500".
- Experiments B (numberPad) and E (Tamil composition) are in the lab, not run.

**Authored (flagged)**
- Review: the text's 7 questions (answers authored), plus a predict item (`Decimal(string: "12abc")`) and a spaced item from 2.10.
- Outcomes, "Where we are", recap, "Where this goes next" (2.12 from the text), lab with expected results.
- Section 16's three layers drawn as a diagram.

**Wording**
- "Trainer question" / "Senior engineer principle/insight" became neutral callouts; "Senior engineer knowledge check" became "Check your understanding".
