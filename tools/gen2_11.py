"""Generates decks/unit-2/lesson-2.11/index.html from the Lesson 2.11 text (TextField, User Input, Validation & Keyboard Focus).
The text came in three pieces (Sections 1-13, 14-20, complete code), grouped into 8 Parts. Console output and
screenshots come from tools/sim2_11 (a scripted SwiftUI app run in the iOS Simulator: fields focused as a tap would,
text entered with UIKeyInput.insertText, buttons activated through accessibility); compiler error and validation
table run with swiftc."""
import html, os, re, sys
OUT211 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.11', 'TextField, User Input,<br>Validation &amp; Focus',
            'Someone types <b>1500</b>. How does it travel from the keyboard into Swift state, and keep the screen in sync?',
            'NPay can show and change things; today it accepts input. We follow text from the iPhone keyboard through a TextField and a binding into state, then validate it, manage focus, and add a payment form to NPay. In the simulator we focused fields as a tap would and entered text through UIKit&rsquo;s text-input protocol, the same one keyboards use; buttons were activated through accessibility as before.')
outcomes_slide('2.11', [("code", "<code>TextField</code> and why it needs a <b>Binding</b>"),
                        ("phone", "Keyboard &rarr; TextField &rarr; binding &rarr; <b>@State</b>"),
                        ("diff", "Why amounts start as <b>String</b>, never <code>Double</code>"),
                        ("shield", "Validation: keyboard hints are <b>not</b> validation"),
                        ("eye", "<code>@FocusState</code>, <code>onSubmit</code>, a Done button"),
                        ("check", "NPay&rsquo;s <b>payment form</b>, validated against the balance")])
where_slide('2.11', 'Today: NPay accepts input', (),
            '2.10: a transaction history from <code>ForEach</code> and stable IDs.',
            'A payment form: text input, validation, focus.',
            'Everything so far was shown or tapped. Today the user types. It is the binding from 2.9 again, now driven by the keyboard.',
            'The milestone.')

# ================================================================== Part 1 (1)
divider(1, "A payment form", "Recipient, amount, continue", 'NPay gets a Send Money form. A demo: nothing is paid.', 'The target.')
S.append(slide("Part 1 &middot; Our next NPay milestone (sections 1, 20)", "Milestone 2.11: a validated payment form", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Form", ul("<b>Recipient</b> and <b>Amount (₹)</b> fields", "<b>Continue Demo</b>, enabled only when valid"))}
        {card("A demo", ul("Prints the request", "No money moves; 2.12 simulates payments"))}
      </div>
      {PHONE("img/before.png", "Before: 2.10", 190)}
      <div class="step">{PHONE("img/typing.png", "ravi@npay, 1500: enabled", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'Where 2.10 ended. The milestone: a Send Money demo form with a recipient field, an amount field, and a Continue Demo button that is enabled only when the input is valid. Click: our run: ravi@npay and 1500 entered, Continue Demo enabled. It prints the request; it does not pay anyone. 2.12 adds a local payment simulation.'),
                  ('CONNECT', 'Start with what a TextField is.'))))

# ================================================================== Part 2 (2-3, 5)
divider(2, "TextField", "Editable text needs a binding", 'Text displays. TextField edits.', 'The smallest one.')
TT = [("Shows text", "edits text"), ("a <code>String</code> value", "a <code>Binding&lt;String&gt;</code>"), ("no keyboard", "keyboard and text input"), ("read only", "two-way data flow")]
HELLO = """struct TextFieldExperiment: View {
    @State private var name = ""

    var body: some View {
        VStack(spacing: 20) {
            TextField("Enter your name", text: $name)
                .textFieldStyle(.roundedBorder)
            Text("Hello, \\(name)")
        }
        .padding()
    }
}"""
S.append(slide("Part 2 &middot; The smallest TextField (sections 2&ndash;3)", "Type Ravi; the Text follows", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.75fr) 250px;gap:22px;align-items:start">
      <div>{code("TextFieldExperiment.swift", HELLO, "font-size:13px")}
        <div class="gap"></div>
        {tbl(["Text", "TextField"], TT)}</div>
      <div class="step">{console("onChange(of: name), typing R-a-v-i", ["name = \"R\"", "name = \"Ra\"", "name = \"Rav\"", "name = \"Ravi\""], 13)}
        <div class="rule" data-label="What happened" style="margin-top:12px">{ul("The field wrote <code>name</code> via the binding", "The <code>Text</code> re-rendered by itself")}</div></div>
      {crop("img/hello.png", "Hello, Ravi (with the keyboard)", 250)}
    </div>
  </div>""", notes(('SAY', 'Text displays content; TextField lets the user edit it, so it needs a connection to mutable state: a binding. The table: Text shows text from a value, with no keyboard; TextField edits text through a Binding of String and brings up the keyboard: two-way data flow.'),
                  ('SAY', 'The smallest experiment: @State name, a TextField bound to $name, and Text("Hello, \\(name)"). On the right, our run after typing Ravi: the field, Hello, Ravi, and the system keyboard. Click: we logged each change of name: R, Ra, Rav, Ravi.'),
                  ('SAY', 'We never updated the Text. The field changed the state through its binding, and SwiftUI updated what depends on it. That is 2.9&rsquo;s binding, driven by a keyboard.'),
                  ('CONNECT', 'Why a binding, and not just the string?'))))

S.append(slide("Part 2 &middot; Why TextField requires a Binding (section 5)", "Read the value, write the edits", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Without the $", 'TextField("Recipient ID", text: recipient)', "font-size:15px")}
        <div class="step" style="margin-top:10px">{err("cannot convert value &lsquo;recipient&rsquo; of type &lsquo;String&rsquo; to expected type &lsquo;Binding&lt;String&gt;&rsquo;, use wrapper instead")}<p class="small muted" style="margin:4px 0 0">swiftc, iOS 26.5 SDK</p></div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The field must", ul("<b>Read</b> the value to display it", "<b>Write</b> the value as the user types"))}
        <div class="step">{console("type(of:) in the simulator", ["$amountText:  Binding&lt;String&gt;"], 14)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A text field has two jobs: read the current value to display it, and write the edited value as the user types. A plain String only gives it a value; a Binding of String gives it a read and write connection.'),
                  ('SAY', 'Click: so writing text: recipient without the dollar sign does not compile. The real error: cannot convert value recipient of type String to expected type Binding of String, use wrapper instead: the compiler even suggests the $ projected value. Click: $amountText printed as Binding of String.'),
                  ('CONNECT', 'What happens between a key press and that binding?'))))

# ================================================================== Part 3 (4, 12)
divider(3, "Keyboard to state", "The system owns the keyboard", 'Several systems cooperate on every character.', 'The pipeline.')
KS = [("tap", "User types", "on the system keyboard"), ("kernel", "Platform text input", "composition, selection, autocorrect"),
      ("frame", "The text field", "the edited text changes"), ("link", "Binding setter", "writes the new String"),
      ("layers", "@State changes", "the owner&rsquo;s state gets the value"), ("eye", "Dependent views update", "e.g. Hello, Ravi")]
P = [box(0, i * 52, 600, 44, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(KS)]
S.append(slide("Part 3 &middot; Keyboard to SwiftUI state (sections 4, 12) &middot; conceptual", "From a key to a visible update", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      {svg('0 0 600 304', 'User types, platform text input, text field, binding setter, state changes, dependent views update', 'kb', P, 'max-height:330px')}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Not one key = one character", ul("Tamil, Hindi: <b>composition</b>, several events", "Use platform text input, not raw key events"))}</div>
        <div class="rule step" data-label="The keyboard">{ul("A <b>system</b> experience, not a SwiftUI view", "Keep per-keystroke work cheap; debounce later")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Conceptually; the text&rsquo;s widget showed only stage 5. Click: the user types on the system keyboard. Click: the platform&rsquo;s text-input system handles it, including composition, selection and autocorrection. Click: the text field&rsquo;s edited text changes. Click: SwiftUI writes the new string through the binding. Click: the @State owner receives it. Click: views that depend on it update.'),
                  ('SAY', 'Click: one key press is not always one character. Tamil and Hindi, among others, compose characters from several input events. That is why ordinary text entry should use the platform&rsquo;s text-input APIs, not raw key events. Our test entered text through UIKit&rsquo;s text-input protocol, the same entry point keyboards use.'),
                  ('SAY', 'Click: the keyboard itself is part of the system input experience; we never build it in SwiftUI. And because every accepted edit can update state, keep per-keystroke work cheap: no network call per keystroke. Debouncing and async validation come later.'),
                  ('CONNECT', 'The amount field holds text. Why not a number?'))))

# ================================================================== Part 4 (6, 8)
divider(4, "Amounts as text", "And never as Double", 'While typing, the amount is not a number yet.', 'Watch it change.')
S.append(slide("Part 4 &middot; Why amounts start as Strings (sections 6, 8)", "Keep the text; parse it carefully", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;align-items:start">
      <div>{console("Typing 1500: onChange", ["\"\" → \"1\"", "\"1\" → \"15\"", "\"15\" → \"150\"", "\"150\" → \"1500\""], 13)}
        <div class="gap"></div>
        {card("String while editing", ul("Holds <b>intermediate</b> text", "Empty, a lone \".\", partial input"))}</div>
      <div class="step">{console("Decimal(string:) alone (Mac)", ["\"12abc\"  → 12", "\"1,500\"  → 1", "\"-500\"   → -500", "\"\"       → nil"], 13)}
        <div class="gap"></div>
        {card("Parsing isn&rsquo;t validation", ul("Stops at the first bad character", "Also check <b>syntax</b> and <b>rules</b>"))}</div>
      <div class="step">{console("Money as Double vs Decimal (Mac)", ["Double 0.1 + 0.2 == 0.3: false", "  (0.30000000000000004)", "Decimal 0.1 + 0.2 == 0.3: true"], 13)}
        <div class="gap"></div>
        <div class="rule" data-label="Real money">{ul("Never <code>Double</code> as the source of truth", "Decimal, or integer minor units (Unit 01)")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Typing 1500 goes through empty, 1, 15, 150, 1500: our onChange log. A user might also briefly have an empty field or just a decimal point. Keeping amountText as a String while editing preserves those intermediate states; converting every keystroke to a number would fight the user.'),
                  ('SAY', 'Click: then parse it carefully. Decimal(string:) on its own is lenient: "12abc" became 12, and "1,500" became 1, because it stops at the first character it cannot use. So parsing is not validation: we also check the syntax and the business rules, which is what the form does.'),
                  ('SAY', 'Click: and never use Double as the authoritative representation of money. In binary floating point, 0.1 plus 0.2 is 0.30000000000000004, not 0.3; Decimal gets it right. Real money uses Decimal or integer minor units, paise, as in Unit 01. Today&rsquo;s form is a UI-only demo.'),
                  ('CONNECT', 'The amount field also asks for a numeric keyboard.'))))

# ================================================================== Part 5 (7)
divider(5, "Keyboard types", "A hint, not a boundary", '.keyboardType(.decimalPad): does that make input valid?', 'Look, then paste.')
S.append(slide("Part 5 &middot; .keyboardType() (section 7)", "<code>.decimalPad</code> shapes the keyboard, not the input", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 230px;gap:22px;align-items:start">
      <div>{code("Amount field", 'TextField("Amount (₹)", text: $amountText)\n    .keyboardType(.decimalPad)', "font-size:14px")}
        <div class="gap"></div>
        {card("A UX hint", ul("Asks for a digits-and-point keyboard", "Text can still arrive by <b>paste</b>, hardware keyboard, accessibility"))}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Pasting \"1500\": onChange", ["Old amount: \"\"", "New amount: 1500", "(one change, no key presses)"], 13)}</div>
        <div class="rule step" data-label="Principle">{ul("Validate <b>independently</b> of the keyboard")}</div>
      </div>
      {PHONE("img/keyboard.png", "Decimal pad + Done", 230)}
    </div>
  </div>""", notes(('SAY', '.keyboardType(.decimalPad) asks iOS for a keyboard with digits and a decimal point. On the right, the real decimal pad in the simulator, with our Done toolbar above it.'),
                  ('SAY', 'Does it guarantee valid input? No. It is a user-experience hint, not a validation boundary. Text can still arrive by paste, a hardware keyboard, accessibility input or other means. Click: we pasted "1500" into the amount field: onChange saw one change, from empty to 1500, with no key presses at all. Paste "abc" and it would arrive just as easily.'),
                  ('SAY', 'Click: so always validate independently of the keyboard configuration.'),
                  ('CONNECT', 'Before validation: focus. Which field is the keyboard typing into?'))))

# ================================================================== Part 6 (9, 19)
divider(6, "Focus", "@FocusState", 'Next moves to Amount; Done hides the keyboard.', 'FocusState.')
FS = """@FocusState private var focusedField: Field?
enum Field: Hashable { case recipient, amount }

TextField("Recipient ID (e.g. ravi@npay)", text: $recipient)
    .focused($focusedField, equals: .recipient)
    .submitLabel(.next)
    .onSubmit { focusedField = .amount }

.toolbar {                         // on the form
    ToolbarItemGroup(placement: .keyboard) {
        Spacer()
        Button("Done") { focusedField = nil }
    }
}"""
S.append(slide("Part 6 &middot; Focus management (sections 9, 19)", "Which field has the keyboard?", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      {code("PaymentForm (focus parts)", FS, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Return in the recipient field", ["focused after return:", "  UITextField, placeholder Amount (₹)"], 13)}</div>
        <div class="step">{console("type(of:)", ["_amountFocused: FocusState&lt;Bool&gt;", "$amountFocused: Binding"], 13)}</div>
        <div class="rule step" data-label="@State vs @FocusState">{ul("<b>@State</b>: the view&rsquo;s own data", "<b>@FocusState</b>: which control is focused")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', '@FocusState connects a property to the focus of focusable controls. With an optional enum, Field, one property says which of several fields has focus, or nil for none. .focused($focusedField, equals: .recipient) ties the recipient field to that case. .submitLabel(.next) labels the return key, and .onSubmit moves focus to the amount field. Setting focusedField = nil clears focus and hides the keyboard; the Done button in a keyboard toolbar does exactly that, and it is visible above the decimal pad on the previous slide.'),
                  ('SAY', 'Click: we entered ravi@npay and sent a return: the first responder became the Amount field. onSubmit moved the focus.'),
                  ('SAY', 'Click: like @State, it is a property wrapper: _amountFocused is a FocusState of Bool, and $amountFocused a binding. Click: but a different concern: @State is the view&rsquo;s own data; @FocusState is which control is focused.'),
                  ('CONNECT', 'Now assemble the form and validate it.'))))

# ================================================================== Part 7 (10-11, 16-17)
divider(7, "PaymentForm", "Validated against the balance", 'Recipient required; amount positive, two decimals, within the balance.', 'The rules.')
VAL = """private var isValidAmount: Bool {
    let pattern = #"^[0-9]+(\\.[0-9]{1,2})?$"#
    guard amountText.range(of: pattern,
                           options: .regularExpression) != nil
    else { return false }
    guard let amount = Decimal(string: amountText,
              locale: Locale(identifier: "en_US_POSIX"))
    else { return false }
    return amount > 0
        && amount <= Decimal(availableBalance)
}
// isValid: recipient not blank && isValidAmount
// Button("Continue Demo") { … }.disabled(!isValid)"""
TB = [("1500", "valid"), ("25000", "valid"), ("25001", "invalid"), ("0", "invalid"), ("12.345", "invalid"), ("abc", "invalid"), ("-500", "invalid")]
S.append(slide("Part 7 &middot; Validate against the demo balance (sections 10, 17)", "Syntax, then rules, then the balance", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.5fr) 210px;gap:22px;align-items:start">
      <div>{code("PaymentForm validation", VAL, "font-size:12.5px")}
        <div class="rule step" data-label="Reacts to both" style="margin-top:10px">{ul("25500 invalid at ₹25,000; <b>+ ₹1,000</b> &rarr; enabled")}</div></div>
      <div class="step">{tbl(["Amount", "Ran"], TB)}<p class="small muted" style="margin:6px 0 0">Balance ₹25,000; Mac, swiftc</p></div>
      {PHONE("img/over.png", "25001: message, disabled", 210)}
    </div>
  </div>""", notes(('SAY', 'PaymentForm&rsquo;s validation in three steps. A regular expression checks the syntax: digits, optionally a point and one or two digits. Then Decimal parses it, which after the regex is safe. Then the rules: greater than zero, and not more than the available balance, which the form now receives from ContentView as a let. Continue Demo is disabled unless the recipient is not blank and the amount is valid.'),
                  ('SAY', 'Click: we ran the text&rsquo;s whole table: 1500 and 25,000 valid; 25,001, 0, 12.345, abc and -500 invalid, exactly as the text predicts. On the right, the real form with 25001: the red message and a disabled button, with the decimal pad and Done still up.'),
                  ('SAY', 'Click: and it reacts to the balance too. We typed 25500: invalid at ₹25,000. Then we activated + ₹1,000 in the balance editor: the balance became 26,000, the form received the new value, and Continue Demo enabled itself. isValid is computed from both local input and the input value.'),
                  ('CONNECT', 'Where does this validation sit among all the checks a payment needs?'))))

LAY = [("phone", "Input experience", "keyboard type, placeholder, focus, formatting"), ("check", "Client-side validation", "required fields, syntax, limits, feedback"),
       ("shield", "Trusted business validation", "authoritative balance, permissions, rules, security")]
P = [box(0, i * 62, 900, 52, t, sub, None, 'lit' if i == 1 else '', ic) for i, (ic, t, sub) in enumerate(LAY)]
S.append(slide("Part 7 &middot; Three responsibilities (sections 11, 16)", "Where today&rsquo;s validation sits", f"""  <div class="body">
    {svg('0 0 900 176', 'Input experience, client-side validation, trusted business validation', 'lay', P, 'max-height:200px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("NPay today", ul("PaymentForm owns its input and focus state", "Local validation, then prints a request"))}
      <div class="rule step" data-label="A disabled button">{ul("Does <b>not</b> replace backend validation", "No financial transaction happens")}</div>
    </div>
  </div>""", notes(('SAY', 'Three separate responsibilities. The input experience: keyboard type, placeholder, focus, formatting. Client-side validation, highlighted, which is what we built: required fields, syntax, limits and feedback. And trusted business validation: the authoritative balance, permissions, transaction rules and security, which belongs to the backend.'),
                  ('SAY', 'In NPay, PaymentForm is added below the quick actions; it owns its own input and focus state and only prints a demo request. Click: a disabled button is a convenience, not security: it never replaces backend validation, and no transaction happens.'),
                  ('CONNECT', 'Last: debugging the form.'))))

# ================================================================== Part 8 (13, 15, 18, 20)
divider(8, "Debugging and checkpoint", "Watch the values change", 'onChange shows values, not key presses.', 'The log.')
OC = """TextField("Amount (₹)", text: $amountText)
    .keyboardType(.decimalPad)
    .textFieldStyle(.roundedBorder)
    .onChange(of: amountText) { oldValue, newValue in
        print("Old amount:", oldValue)
        print("New amount:", newValue)
    }"""
S.append(slide("Part 8 &middot; Debugging TextField (sections 15, 18, 20)", "Values, not key presses", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("PaymentForm amount field", OC, "font-size:13.5px")}
        <div class="gap"></div>
        <div class="rule step" data-label="The whole flow">{ul("Keyboard &rarr; TextField &rarr; Binding &rarr; @State", "&rarr; Validation &rarr; button state &rarr; update")}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Typed 1500 vs pasted 1500", ["typed:  4 changes (1, 15, 150, 1500)", "pasted: 1 change  (1500)"], 13)}</div>
        <div class="step">{console("Continue Demo, activated", ["Demo payment request", "Recipient: ravi@npay", "Amount: 1500"], 13)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s debugging tool: onChange(of: amountText) with the two-parameter closure, printing old and new values. Click: typed character by character, 1500 produced four changes; pasted, one. onChange observes value changes; it is not a raw keyboard listener, and that difference is exactly why we validate the value, not the keys.'),
                  ('SAY', 'Click: with a valid form, Continue Demo printed the demo request: recipient ravi@npay, amount 1500.'),
                  ('SAY', 'Click: the complete flow to be able to explain: keyboard input, TextField, Binding, @State, validation, the button enabled or disabled, SwiftUI update. The text&rsquo;s Xcode experiments, removing the $, numberPad, the validation inputs, Next focus and Tamil composition, are in the lab.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.11', (), [("link", "TextField writes a binding", "keyboard → binding → @State"),
                      ("shield", "Validate the value", "keyboard type is only a hint"),
                      ("eye", "Focus is state too", "@FocusState, onSubmit, Done")],
         'Three things to remember. A TextField reads and writes text through a Binding of String, so the keyboard ends up changing your @State and SwiftUI updates the rest. Validate the value itself, syntax then rules then the balance, because a decimal pad is only a hint and paste bypasses it; and the backend has the final word. And focus is state: @FocusState says which field has the keyboard, onSubmit moves it, and Done clears it.')

review_divider(9)
review([("link", "Choose one", "Why does TextField take a Binding<String>?",
         "Why does <code>TextField</code> commonly take a <code>Binding&lt;String&gt;</code>?<br>A. To read and write the editable text<br>B. To create a new thread<br>C. To store data in a database", "A",
         "It displays the value and writes each edit back; a plain String did not compile.",
         "Thinking the field keeps its own copy.", "Most pick A.", None),
        ("shield", "Question", "Does .decimalPad guarantee valid decimal input?",
         "Does <code>.keyboardType(.decimalPad)</code> guarantee valid decimal input?", "No",
         "A paste delivered \"1500\" in one change without a key press; anything can be pasted.",
         "Treating the keyboard as validation.", "Some say yes.", None),
        ("eye", "Choose one", "What does @FocusState manage?",
         "What does <code>@FocusState</code> manage?<br>A. Which control has focus<br>B. Network state<br>C. Application signing", "A",
         "onSubmit set it to .amount and the Amount field became first responder.",
         "Confusing it with @State.", "Most pick A.", None),
        ("diff", "Choose one", "Why keep the amount as a String while editing?",
         "Why is a <code>String</code> useful while the amount is being edited?<br>A. It keeps intermediate text such as empty input and a lone decimal point<br>B. It encrypts money<br>C. It removes the need for validation", "A",
         "Typing 1500 passes through \"\", \"1\", \"15\", \"150\".",
         "Converting every keystroke to a number.", "Most pick A.", None),
        ("db", "Question", "Should Double be the authoritative representation of money?",
         "Should <code>Double</code> be the authoritative representation of money?", "No",
         "0.1 + 0.2 printed 0.30000000000000004; use Decimal or integer minor units.",
         "Assuming floating point is exact.", "Some say yes.", None),
        ("bank", "Question", "Does a disabled Continue button replace backend validation?",
         "Does a disabled Continue button replace backend validation?", "No",
         "It is client-side convenience; trusted rules live on the backend.",
         "Trusting the client.", "Some say yes.", None),
        ("layers", "Choose one", "What happens when TextField writes through $amountText?",
         "What happens when the TextField writes through <code>$amountText</code>?<br>A. The state owner receives the updated String<br>B. A new independent TextField state is created<br>C. The app recompiles", "A",
         "onChange on the owner logged every new value.",
         "Expecting a separate copy in the field.", "Most pick A.", None),
        ("code", "Predict the result", "Decimal(string: \"12abc\") on its own returns…?",
         "Without the regex check, what does <code>Decimal(string: \"12abc\", locale: en_US_POSIX)</code> return?<br>A. <code>nil</code><br>B. <code>12</code><br>C. A crash", "B",
         "It stops at the first character it cannot use, which is why the form checks syntax first.",
         "Expecting strict parsing.", "Most pick A.", None),
        ("frame", "Choose one", "From 2.10: what decides lazy row creation?",
         "From Lesson 2.10: what decides whether 1,000 rows are built eagerly or lazily?<br>A. <code>ForEach</code><br>B. The surrounding container<br>C. <code>Identifiable</code>", "B",
         "VStack built 1,000 row bodies, LazyVStack 12, List 9.",
         "Assuming ForEach is lazy.", "Some pick A.", "Spaced review from Lesson 2.10.")])

S.append(next_slide('2.11', [("2.12", "Unit 2 integration &amp; architecture review", "connect the form to a local payment simulation; clean up the files; review Unit 2"),
                             ("Later", "Debouncing, async validation", "expensive checks off the keystroke path")],
                    'Next lesson closes Unit 2: the full NPay dashboard assembled and cleaned up, the payment form connected to a local transaction simulation, and a review of every SwiftUI idea before Unit 3. Debouncing and asynchronous validation come later in the course.'))

S.append(lab_slide('2.11', "Type, paste, validate", "Run the text&rsquo;s experiments A to E.",
                   ["<b>A</b>: remove <code>$</code> from <code>text: $recipient</code>.",
                    "<b>B</b>: <code>.decimalPad</code> &rarr; <code>.numberPad</code>.",
                    "<b>C</b>: amounts 0, -100, 12.345, 1500.",
                    "<b>D</b>: recipient, then Next: where&rsquo;s the focus?",
                    "<b>E</b>: a Tamil recipient name.",
                    "Paste an amount; compare the onChange log."],
                   "", 'Expected, as in our runs: "cannot convert value &lsquo;recipient&rsquo; of type &lsquo;String&rsquo; to expected type &lsquo;Binding&lt;String&gt;&rsquo;"; numberPad drops the decimal point key; only 1500 enables Continue (-100 cannot even be typed on the pad, but can be pasted and is rejected); Next moves focus to Amount; Tamil input is composed by the system keyboard before it reaches the binding; a paste logs one change.',
                   side=f'<div>{card("You hand in", ul("The compiler error, explained", "Which amounts enabled Continue", "Your onChange log: typed vs pasted"))}</div>'))

end_slide('2.11', 'TextField, User Input,<br>Validation &amp; Focus', 'Lesson 2.12 &mdash; Unit 2 Integration &amp; Architecture Review',
          'You can now explain how typed text reaches @State through a TextField&rsquo;s binding, why amounts stay text while editing and never become Double, why keyboard types are hints and validation must check the value, how @FocusState, onSubmit and a Done button manage focus, and how NPay&rsquo;s payment form validates against the balance without moving money.',
          'Next, Lesson 2.12: Unit 2 integration and architecture review. The full NPay dashboard, a local payment simulation, and a review before Unit 3.')

write_deck(OUT211, '2.11', 'TextField &amp; Focus', 'TextField &amp; Focus')
