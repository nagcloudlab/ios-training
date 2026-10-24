"""Generates decks/unit-2/lesson-2.12/index.html from the Lesson 2.12 text (Build a Complete NPay Payment Flow, Unit 2 capstone).
The text came in two pieces (Sections 1-9 cut off; then "Final NPay Integration" 1-5 with the complete code), grouped
into 7 Parts. Console output and screenshots come from tools/sim2_12 (the complete code run unchanged in the iOS
Simulator, driven through text input and accessibility); parsePaise and Money.display were run with swiftc."""
import html, os, re, sys
OUT212 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.12', 'Build a Complete<br>NPay Payment Flow',
            'Send <b>₹1,500</b> to ravi@npay: the balance drops to ₹23,500 and the payment appears in the history. Unit 2&rsquo;s pieces, <b>connected</b>.',
            'The Unit 2 capstone. NPay has a balance card, an editor, a payment form, quick actions and a history, but they do not talk to each other: Continue Demo only prints. Today we connect them into one flow: the form asks, ContentView decides, the balance and the history change, and SwiftUI updates the screen. Money moves to integer paise. We ran the lesson&rsquo;s complete code unchanged in the simulator and drove it as a user would.')
outcomes_slide('2.12', [("link", "How a child <b>asks</b> its parent to act: an <code>onSend</code> closure"),
                        ("db", "Why money is <b>integer paise</b>, parsed safely"),
                        ("diff", "One action, two state changes, <b>one</b> consistent update"),
                        ("check", "Run and <b>verify</b> the whole flow"),
                        ("layers", "The Unit 2 <b>architecture</b>, end to end"),
                        ("shield", "What a prototype is <b>not</b>")])
where_slide('2.12', 'Today: the Unit 2 capstone', (),
            '2.11: a validated form that only printed.',
            'A working payment flow: form &rarr; parent &rarr; balance + history.',
            'Eleven lessons built the parts. This one connects them, and then we look back over the whole unit before Unit 3.',
            'The goal.')

# ================================================================== Part 1 (intro, 1)
divider(1, "The goal", "From form to history", 'Continue Demo only printed. Now a payment changes the app.', 'The flow.')
FLOW = [("tap", "Enter payment", "recipient, amount"), ("check", "Validate", "recipient, amount, balance"), ("gear", "Simulate", "local logic, no transfer"),
        ("db", "Balance updates", "@State changes"), ("file", "Transaction recorded", "a new identifiable row"), ("eye", "SwiftUI updates", "card and history")]
P = []
for i, (ic, t, sub) in enumerate(FLOW):
    x = i * 192
    P.append(tall(x, 0, 176, 112, ic, t, sub, None, 'lit' if i in (3, 4) else ''))
    if i < 5:
        P.append(wire(f'M{x + 178} 56H{x + 190}' + head(x + 190, 56, 'r')))
S.append(slide("Part 1 &middot; What we&rsquo;re building (section 1)", "Send ₹1,500; watch two things change", f"""  <div class="body">
    {svg('0 0 1136 112', 'Enter, validate, simulate, balance updates, transaction recorded, SwiftUI updates', 'flow', P, 'max-height:130px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 170px 170px 170px;gap:20px;align-items:start">
      {card("Try it", ul("ravi@npay, ₹1,500", "Balance: ₹25,000 &rarr; <b>₹23,500</b>", "History: <b>Sent to ravi@npay</b>", "Local simulation only"))}
      {PHONE("img/before.png", "Before: 2.11", 170)}
      <div class="step">{PHONE("img/paidtop.png", "After: ₹23,500.00", 170)}</div>
      <div class="step">{PHONE("img/paidbottom.png", "New row on top", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'The flow we are building: the user enters a payment; NPay validates the recipient, the amount and the balance; the payment is simulated locally, no real transfer; the balance state changes; a transaction is recorded with its own identity; SwiftUI updates the card and the history.'),
                  ('SAY', 'The text&rsquo;s demo: send ₹1,500 to ravi@npay. On the left, where 2.11 ended. Click: our run of today&rsquo;s complete code after the payment: ₹23,500.00. Click: and scrolled down: "Sent to ravi@npay", minus ₹1,500, at the top of the history, with "Demo payment recorded." above it.'),
                  ('CONNECT', 'The design problem: the form has the input, ContentView has the money.'))))

# ================================================================== Part 2 (2, 3, 7)
divider(2, "Who processes the payment?", "The form asks; the parent decides", 'PaymentForm owns the input. ContentView owns the balance.', 'Connect them with a closure.')
P = [box(0, 0, 420, 56, 'ContentView', 'owns balancePaise, transactions', None, 'lit', 'layers'),
     wire('M150 60V118' + head(150, 118, 'd')), wire('M270 118V60' + head(270, 64, 'u'), None, 'dash'),
     box(0, 124, 420, 56, 'PaymentForm', 'balance in · onSend(recipient, paise) out', None, '', 'file')]
CONTRACT = """struct PaymentForm: View {
    let availableBalancePaise: Int
    let onSend: (String, Int) -> Bool   // recipient, paise → accepted?

    @State private var recipient = ""
    @State private var amountText = ""
    // body: fields, validation, Send Demo Payment
}

PaymentForm(availableBalancePaise: balancePaise) { recipient, amountPaise in
    sendDemoPayment(to: recipient, amountPaise: amountPaise)
}"""
S.append(slide("Part 2 &middot; The action contract (sections 2&ndash;3, 7)", "Data down, a request up", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      <div>{code("PaymentForm and its caller", CONTRACT, "font-size:12.5px")}</div>
      <div>{svg('0 0 420 180', 'ContentView passes the balance down; PaymentForm calls onSend up', 'own', P, 'max-height:170px')}
        <div class="gap"></div>
        {card("Why not do it in the form?", ul("Form: <b>input</b> and <b>feedback</b>", "Parent: <b>application state</b>", "A step toward MVVM (Unit 4)"))}
        <div class="gap"></div>
        <div class="step">{console("type(of: onSend)", ["(String, Int) -&gt; Bool"], 13)}</div></div>
    </div>
  </div>""", notes(('SAY', 'PaymentForm owns recipient and amountText; ContentView owns the balance and the transactions. How does the form request a payment without owning or touching the money? With a closure, as QuickAction did in 2.7. The form receives the available balance as a value and an onSend closure that takes a recipient and an amount in paise and returns whether the request was accepted.'),
                  ('SAY', 'ContentView creates the form with a trailing closure that calls its own sendDemoPayment. The form never sees the transaction array; it sends a request, and the parent decides. Data flows down, requests flow up.'),
                  ('SAY', 'Why not put the logic in the form? Because the form&rsquo;s job is collecting input and showing validation feedback, while the parent coordinates application state. That split is a step toward MVVM and services in Unit 4. Click: the closure&rsquo;s type, printed: (String, Int) -> Bool.'),
                  ('CONNECT', 'Int for the amount: why?'))))

# ================================================================== Part 3 (3-5)
divider(3, "Money in paise", "Exact integers, parsed safely", 'No Double, no force unwrap.', 'Parse text into paise.')
PP = """static func parsePaise(_ text: String) -> Int? {
    let pattern = #"^[0-9]+(\\.[0-9]{1,2})?$"#
    guard text.range(of: pattern, options: .regularExpression)
          != nil else { return nil }
    let parts = text.split(separator: ".",
                           omittingEmptySubsequences: false)
    guard let rupees = Int(parts[0]) else { return nil }
    let fraction = parts.count > 1 ? String(parts[1]) : ""
    let padded = fraction.padding(toLength: 2, withPad: "0",
                                  startingAt: 0)
    guard let paise = Int(padded) else { return nil }
    let (rupeePaise, o1) = rupees.multipliedReportingOverflow(by: 100)
    guard !o1 else { return nil }
    let (total, o2) = rupeePaise.addingReportingOverflow(paise)
    guard !o2 else { return nil }
    return total
}"""
RUNS = [("\"1\"", "100"), ("\"10.50\"", "1050"), ("\"1500\"", "150000"), ("\"0.5\"", "50"), ("\"12.345\"", "nil"),
        ("\"-500\"", "nil"), ("\"92233720368547759\"", "nil (× 100 overflows)")]
S.append(slide("Part 3 &middot; Convert input to paise safely (sections 3&ndash;4)", "<code>parsePaise</code>: syntax, then exact integers", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:24px;align-items:start">
      {code("Money.parsePaise", PP, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Input", "Paise (Mac run)"], RUNS)}</div>
        <div class="rule step" data-label="Instead of">{ul("<code>Double(amountText)!</code>: crashes on bad input, inexact")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The amount travels as an Int of paise, the smallest INR unit: ₹1 is 100, ₹10.50 is 1,050, ₹1,500 is 150,000. Integers are exact, so no floating-point rounding, as 2.11 showed, and it matches the paise model from Unit 01.'),
                  ('SAY', 'parsePaise checks the syntax with the regex first, splits rupees and fraction, pads the fraction to two digits, and combines them with overflow-reporting arithmetic, returning nil instead of crashing. Click: we ran it on a Mac: "1" is 100, "10.50" is 1050, "1500" is 150000, "0.5" is 50; "12.345" and "-500" fail the regex; and "92233720368547759" passes the regex and fits an Int, but times 100 overflows, so the overflow check returns nil.'),
                  ('SAY', 'Click: compare Double(amountText)!: a crash on bad input, and an inexact number on good input. Still a teaching implementation; production money needs a full domain model.'),
                  ('CONNECT', 'Paise in, but people read rupees.'))))

MODEL = """struct Transaction: Identifiable {
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date          // a value; "24 Oct" is presentation
}

@State private var balancePaise = 2_500_000   // ₹25,000

enum Money {
    static func display(_ paise: Int) -> String {
        (Decimal(paise) / Decimal(100)).formatted(
            .currency(code: "INR").locale(Locale(identifier: "en_IN")))
    }
}"""
DISP = [("2_500_000", "₹25,000.00"), ("2_350_000", "₹23,500.00"), ("-25_000", "-₹250.00"), ("1_050", "₹10.50"), ("12_345_678_900", "₹12,34,56,789.00")]
S.append(slide("Part 3 &middot; Paise everywhere (section 5)", "Store paise and dates; format at the edge", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {code("Model and formatting", MODEL, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Paise", "Money.display (Mac run)"], DISP)}</div>
        <div class="rule step" data-label="en_IN">{ul("Indian grouping: <b>12,34,56,789</b>", "Domain values in, text only at display")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The balance becomes balancePaise, 2,500,000 for ₹25,000, and Transaction stores amountPaise and a real Date. "Today" or "24 Oct" is a presentation decision, not domain data: domain values in the model, formatting at the edge.'),
                  ('SAY', 'Money.display divides by 100 as a Decimal, exact, and formats it as INR in the en_IN locale. Click: our Mac run: ₹25,000.00, ₹23,500.00, minus ₹250.00, ₹10.50, and for 12,345,678,900 paise, ₹12,34,56,789.00: the en_IN locale uses Indian digit grouping, lakhs and crores.'),
                  ('CONNECT', 'Now the operation itself.'))))

# ================================================================== Part 4 (6, 8)
divider(4, "The payment operation", "Validate, then change both", 'One function changes the balance and the history.', 'sendDemoPayment.')
OP = """private func sendDemoPayment(to recipient: String,
                             amountPaise: Int) -> Bool {
    let trimmed = recipient.trimmingCharacters(
        in: .whitespacesAndNewlines)

    guard !trimmed.isEmpty,
          amountPaise > 0,
          amountPaise <= balancePaise else {
        statusMessage = "Invalid payment request."
        return false
    }

    balancePaise -= amountPaise
    transactions.insert(
        Transaction(id: UUID(), title: "Sent to \\(trimmed)",
                    amountPaise: -amountPaise, date: .now),
        at: 0)
    statusMessage = "Demo payment recorded."
    return true
}"""
S.append(slide("Part 4 &middot; Implement the demo payment (section 6)", "The parent validates again, then updates", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {code("ContentView.sendDemoPayment", OP, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Two mutations, one action", ul("<code>balancePaise</code> and <code>transactions</code>", "In one synchronous call: <b>consistent</b> on screen"))}
        <div class="rule step" data-label="Not a database">{ul("No durability across crashes or devices", "SwiftUI coordinates UI, it isn&rsquo;t a transaction engine")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'sendDemoPayment is the only place money changes. It validates again on the parent&rsquo;s side: a trimmed, non-empty recipient, an amount above zero and not above the balance. The form checked too, but the owner of the state does not trust the caller blindly, a habit we keep all the way to the backend. If valid, it subtracts from the balance, inserts a "Sent to" transaction with a negative amount and the current date, sets a status message, and returns true; otherwise it sets an error status and returns false.'),
                  ('SAY', 'Both the balance and the transaction list change in one synchronous call, so the screen never shows one without the other. Click: but this is not a database transaction: nothing is durable across a crash or another device. SwiftUI coordinates UI updates; it is not a financial transaction engine. Authoritative transactions belong on the backend, later in the course.'),
                  ('CONNECT', 'Follow one ₹1,500 payment end to end.'))))

TR = [("tap", "TextFields receive input", "recipient and amount via bindings"), ("check", "PaymentForm validates", "parsePaise, isValid: button enabled"),
      ("link", "Button calls onSend", "(\"ravi@npay\", 150000)"), ("gear", "ContentView validates", "and decides to accept"),
      ("db", "State mutates", "balancePaise, transactions"), ("file", "Form clears on true", "recipient, amount, focus"), ("eye", "SwiftUI updates", "BalanceCard, TransactionHistory")]
P = [box(0, i * 46, 620, 40, t, sub, str(i + 1) if i < 6 else '7+', '', ic) for i, (ic, t, sub) in enumerate(TR)]
S.append(slide("Part 4 &middot; Trace a ₹1,500 payment (section 8) &middot; conceptual", "Seven steps, one tap", f"""  <div class="body">
    {cues(7)}
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {svg('0 0 620 316', 'Input, form validation, onSend, parent validation, state mutation, form clears, SwiftUI updates', 'tr', P, 'max-height:340px')}
      <div class="step">{console("Driven in the simulator", ["before: ₹25,000.00", "Send Demo Payment enabled: false", "… ravi@npay, 1500 …", "Send Demo Payment enabled: true", "[activate]", "after: ₹23,500.00", "Demo payment recorded.", "fields now: \"\", \"\""], 12.5)}</div>
    </div>
  </div>""", notes(('SAY', 'Only stage 1 was in the text&rsquo;s widget; the rest is our trace, conceptual. Click: the text fields receive input through their bindings. Click: the form parses and validates; the button becomes enabled. Click: the button calls onSend with "ravi@npay" and 150,000 paise. Click: ContentView validates and accepts. Click: the balance and the transactions mutate. Click: onSend returned true, so the form clears its fields and focus. Click: SwiftUI updates the card and the history.'),
                  ('SAY', 'Click: our run: the balance read ₹25,000.00 and the button was disabled; after entering ravi@npay and 1500 it was enabled; after the activation the balance read ₹23,500.00, the status said "Demo payment recorded.", and both fields were empty again.'),
                  ('CONNECT', 'Now the text&rsquo;s whole verification table.'))))

# ================================================================== Part 5 (Final 2-3)
divider(5, "Run and verify", "The text&rsquo;s test table, run", 'Every row of the verification table, in the simulator.', 'Results.')
VER = [("Starting balance", "₹25,000.00", "₹25,000.00"), ("ravi@npay, 1500", "Send enabled", "enabled"), ("Send Demo Payment", "₹23,500.00", "₹23,500.00"),
       ("History", "Sent to ravi@npay", "on top, -₹1,500.00"), ("0", "disabled", "disabled"), ("Above balance (25000.01)", "disabled", "disabled"),
       ("12.345", "disabled", "disabled"), ("+ ₹1,000", "+₹1,000", "₹26,000.00; 25000.01 now enabled"), ("Request", "status message", "Request feature coming soon.")]
S.append(slide("Part 5 &middot; Verify the complete flow (final section 3)", "Every test, run", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) 190px;gap:24px;align-items:start">
      <div>{tbl(["Test", "Expected", "Simulator"], VER)}
        <p class="small muted" style="margin:6px 0 0">The complete code ran unchanged; local simulation only.</p></div>
      {PHONE("img/paidbottom.png", "After the payment", 190)}
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s verification table, every row run against the complete code. Starting balance ₹25,000.00. ravi@npay and 1500: Send enabled. After sending: ₹23,500.00, and "Sent to ravi@npay", minus ₹1,500.00, on top of the history, as the screenshot shows. 0, an amount just above the balance, 25,000.01, and 12.345: disabled. Plus ₹1,000: ₹26,000.00, and the same 25,000.01 became valid, because the form re-validates against the new balance. Request: the status message "Request feature coming soon."'),
                  ('SAY', 'All of it local: no bank, no network, no real money.'),
                  ('CONNECT', 'Step back: what did Unit 2 build?'))))

# ================================================================== Part 6 (Final 4-5)
divider(6, "Architecture review", "What we built, what it isn&rsquo;t", 'One file, six components, one owner of state.', 'The tree.')
TREE = """ContentView        @State balancePaise, transactions, statusMessage
├── BalanceCard        let balancePaise           read only
├── BalanceEditor      @Binding balancePaise      teaching control
├── QuickAction × 3    action: () -> Void
├── PaymentForm        input, validation, focus · onSend ↑
└── TransactionHistory ForEach + stable identity
    └── TransactionRow
sendDemoPayment        validates, updates balance, inserts row"""
S.append(slide("Part 6 &middot; Architecture review (final sections 4&ndash;5)", "Nearly every Unit 2 idea, in one flow", f"""  <div class="body">
    {code("NPay after Unit 2", TREE, "font-size:13.5px")}
    <div class="gap"></div>
    <div class="rule" data-label="The flow">{ul("TextField &rarr; Binding &rarr; @State &rarr; Button &rarr; onSend &rarr; validation &rarr; state mutation &rarr; SwiftUI update")}</div>
    <div class="gap"></div>
    <div class="step">{card("Not production-ready, on purpose", ul("Payment rules in <b>ContentView</b>; nothing <b>persisted</b>; mock records", "No auth, networking, server authority or tests", "A real app never lets the user <b>edit</b> the balance"))}</div>
  </div>""", notes(('SAY', 'The whole app: ContentView owns the balance, the transactions and the status. BalanceCard reads a value; BalanceEditor has a binding; QuickActions take closures; PaymentForm owns input, validation and focus and sends requests up; TransactionHistory uses ForEach with stable identity; sendDemoPayment is the single place money changes.'),
                  ('SAY', 'The flow connects nearly every idea in the unit: TextField, binding, @State, a button action, the onSend closure, validation in the owner, state mutation, and SwiftUI updating the card and the history.'),
                  ('SAY', 'Click: the honest review. It is a learning prototype. Payment rules live in a view; nothing is persisted; the records are mock data; there is no authentication, networking, server authority or test suite. And the balance editor is a teaching control: a real banking app must never let the user change an authoritative balance. Each of these limits is addressed by a later unit.'),
                  ('CONNECT', 'One last look back over the unit.'))))

# ================================================================== Part 7 (authored): Unit 2 in one picture
divider(7, "Unit 2 in one picture", "Twelve lessons, one app", 'Where each lesson lives in today&rsquo;s NPay.', 'The map.')
MAP = [("2.1", "Text", "a view is a description; <code>some View</code>"), ("2.2", "Image", "SF Symbols resolved at run time"),
       ("2.3", "VStack", "<code>@ViewBuilder</code>, generic content"), ("2.4", "HStack", "width negotiation, Spacer"),
       ("2.5", "ZStack", "layers; background vs overlay"), ("2.6", "Modifiers", "wrappers; order; environment"),
       ("2.7", "Button", "action closures: QuickAction"), ("2.8", "@State", "state lives with identity"),
       ("2.9", "@Binding", "BalanceEditor writes through"), ("2.10", "ForEach", "stable IDs: TransactionHistory"),
       ("2.11", "TextField", "input, validation, focus: PaymentForm"), ("2.12", "Payment flow", "onSend up, paise, one owner")]
S.append(slide("Part 7 &middot; Unit 2 review (authored)", "Every lesson is somewhere on this screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;align-items:start">
      {tbl(["", "Lesson", "In NPay today"], MAP[:6])}
      {tbl(["", "Lesson", "In NPay today"], MAP[6:])}
    </div>
  </div>""", notes(('SAY', 'Twelve lessons, one screen. 2.1: the NPay title is a Text, a description, returned as some View. 2.2: the card symbol, resolved at run time. 2.3 and 2.4: the stacks and their layout negotiation. 2.5: layering, and why the card uses a background. 2.6: modifiers as wrappers, order, and the environment that carries fonts and colours down.'),
                  ('SAY', '2.7: QuickAction&rsquo;s closures. 2.8: @State, kept with the view&rsquo;s identity. 2.9: BalanceEditor&rsquo;s binding. 2.10: the history&rsquo;s stable IDs. 2.11: the form&rsquo;s input, validation and focus. 2.12: the onSend request, paise, and one owner of state. If you can point at each and explain it, you are ready for Unit 3.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('2.12', (), [("link", "Requests go up", "onSend closure; the parent decides"),
                      ("db", "Paise, exactly", "parse safely; format at display"),
                      ("layers", "One owner of state", "consistent updates; not a database")],
         'Three things to remember. A child asks, its parent decides: PaymentForm collects input and calls onSend; ContentView validates and changes its own state. Money is integer paise, parsed with syntax and overflow checks, and formatted only for display. And keeping state in one owner lets one action update the balance and the history together, though that is UI consistency, not a durable financial transaction.')

review_divider(9)
review([("layers", "Choose one", "Who owns the balance and the transactions?",
         "In the final NPay, who owns <code>balancePaise</code> and <code>transactions</code>?<br>A. <code>PaymentForm</code><br>B. <code>ContentView</code><br>C. <code>TransactionHistory</code>", "B",
         "The form only receives the balance and calls <code>onSend</code>.",
         "Giving state to whoever edits it.", "Some pick A.", None),
        ("link", "Question", "Does PaymentForm change balancePaise directly?",
         "Does <code>PaymentForm</code> change <code>balancePaise</code> directly?", "No",
         "It calls <code>onSend(recipient, paise)</code>; ContentView decides and mutates its own state.",
         "Passing a binding to everything.", "Some say yes.", None),
        ("code", "Choose one", "What does onSend's Bool mean?",
         "What does the <code>Bool</code> returned by <code>onSend</code> tell the form?<br>A. Whether the request was accepted<br>B. Whether the keyboard is visible<br>C. Whether the app is online", "A",
         "On true the form clears its fields and focus; on false it keeps them.",
         "Ignoring the result.", "Most pick A.", None),
        ("db", "Predict the result", "parsePaise(\"10.50\") returns…?",
         "What does <code>Money.parsePaise(\"10.50\")</code> return?<br>A. <code>10</code><br>B. <code>1050</code><br>C. <code>10.5</code>", "B",
         "Rupees × 100 plus the padded fraction: exactly 1,050 paise.",
         "Thinking in rupees or Double.", "Some pick C.", None),
        ("diff", "Predict the result", "parsePaise(\"92233720368547759\")?",
         "<code>\"92233720368547759\"</code> passes the regex and fits in an <code>Int</code>. What does <code>parsePaise</code> return?<br>A. A huge number<br>B. <code>nil</code><br>C. A crash", "B",
         "× 100 overflows; <code>multipliedReportingOverflow</code> catches it.",
         "Forgetting arithmetic can overflow.", "Some pick C.", None),
        ("eye", "Choose one", "Money.display(12_345_678_900) in en_IN shows…?",
         "<code>Money.display(12_345_678_900)</code> with the en_IN locale shows:<br>A. ₹123,456,789.00<br>B. ₹12,34,56,789.00<br>C. ₹12345678900", "B",
         "en_IN groups in lakhs and crores; the value is paise ÷ 100.",
         "Assuming Western grouping.", "Many pick A.", None),
        ("gear", "Question", "Are two @State changes a durable, atomic transaction?",
         "Is changing <code>balancePaise</code> and <code>transactions</code> in one action a durable, atomic transaction?", "No",
         "It is consistent on screen; nothing survives a crash or syncs devices.",
         "Treating UI state as a database.", "Some say yes.", None),
        ("shield", "Question", "Should a production app let users edit the balance?",
         "Should a production banking app keep a balance editor like ours?", "No",
         "The balance is authoritative on the backend; the editor is a teaching control.",
         "Shipping demo controls.", "Most say no.", None),
        ("phone", "Choose one", "From 2.11: what does .decimalPad guarantee?",
         "From Lesson 2.11: what does <code>.keyboardType(.decimalPad)</code> guarantee?<br>A. Only digits and a point can be entered<br>B. Nothing: it is a keyboard hint<br>C. The value is a valid amount", "B",
         "A paste delivered any text; validation must check the value.",
         "Trusting the keyboard.", "Some pick A.", "Spaced review from Lesson 2.11.")])

S.append(next_slide('2.12', [("Unit 3", "Advanced SwiftUI &amp; navigation", "separate files and screens instead of one ContentView"),
                             ("Unit 4", "Application architecture &amp; MVVM", "payment rules out of the view, into models and services"),
                             ("Later units", "Networking, persistence, security, tests", "server authority, saved data, authentication, a test suite")],
                    'Unit 3 splits NPay into files and screens with navigation. Unit 4 moves the payment rules out of ContentView into a ViewModel and services. Later units add the backend that owns the balance, persistence, authentication and tests: every limitation from the review has a place in the course.'))

S.append(lab_slide('2.12', "Ship the Unit 2 NPay", "Build the complete code and run the verification table.",
                   ["Replace ContentView.swift; keep NPayApp.swift.",
                    "Send ₹1,500 to ravi@npay; check card and history.",
                    "Try 0, 12.345 and above the balance.",
                    "+ ₹1,000, then re-try an amount just above the old balance.",
                    "Tap Request, Send, History: read the status.",
                    "Explain each Unit 2 lesson&rsquo;s place on screen."],
                   "", 'Expected, as in our run: ₹25,000.00 → ₹23,500.00 with "Sent to ravi@npay" on top and the form cleared; 0, 12.345 and 25000.01 keep Send disabled; after + ₹1,000 the balance is ₹26,000.00 and 25000.01 is accepted; the quick actions show their status messages. For the last step, use the Unit 2 map slide.',
                   side=f'<div>{card("You hand in", ul("Your completed verification table", "A screenshot after one payment", "One sentence per Unit 2 lesson"))}</div>'))

end_slide('2.12', 'Build a Complete<br>NPay Payment Flow', 'Unit 03 &mdash; Advanced SwiftUI &amp; Navigation',
          'Unit 2 is complete. You can explain how a child requests an action through a closure while its parent owns the state, why money is integer paise parsed with overflow checks and formatted only for display, how one action keeps the balance and history consistent, and how every lesson from Text to TextField fits into one working NPay.',
          'Next, Unit 03: advanced SwiftUI and navigation. NPay is split into files and screens, with navigation between them.')

write_deck(OUT212, '2.12', 'NPay Payment Flow', 'NPay Payment Flow')
