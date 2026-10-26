"""Generates decks/unit-3/lesson-3.5/index.html from the Lesson 3.5 text (State Preservation Across Navigation).
The text came in two pieces (Sections 1-13; "Part 2" Sections 13-19), grouped into 8 Parts. The shared-draft
integration into the 3.4 app is authored (the text names it as its next checkpoint). Console output and screenshots
come from tools/sim3_5 (iOS Simulator); the PaymentDraft name clash was compiled with swiftc."""
import html, os, re, sys
OUT35 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

title_slide('3.5', 'State Preservation<br>Across Navigation',
            'A half-typed payment should survive a trip to History and a dismissed review. Not by luck: by giving the draft an <b>owner that lives long enough</b>.',
            'Lesson 3.4 added a review sheet. Today a question that grows with every app: what happens to a partially completed payment when the user switches tabs, navigates away or dismisses a sheet? We will separate three ideas that are easy to confuse, view values, view identity and state storage, prove each one in the simulator, then move NPay&rsquo;s payment draft into the shared store on purpose.')
outcomes_slide('3.5', [("diff", "Separate a view&rsquo;s <b>value</b>, its <b>identity</b> and its <b>state</b>"),
                       ("clock", "Predict when local <code>@State</code> resets, and force it with <code>.id()</code>"),
                       ("file", "Model a <b>draft</b> separately from a payment request"),
                       ("db", "Move the draft into <code>NPayStore</code>; edit it with <code>@Bindable</code>"),
                       ("check", "Decide <b>when</b> a draft is cleared"),
                       ("shield", "Tell preservation from <b>persistence</b>; pick each state&rsquo;s owner")])
where_slide('3.5', 'Today: a draft that survives on purpose', (),
            '3.4: review sheet, confirm once, navigate after dismissal.',
            'A payment draft owned by the store, kept until paid or discarded.',
            'Lesson 3.4 completed the review flow. Today the draft gets a deliberate owner. Next lesson: animations and transitions.',
            'The journey.')

# ================================================================== Part 1 (1)
divider(1, "The milestone", "Don&rsquo;t lose the user&rsquo;s input", 'Preserve the draft until it is paid or discarded.', 'The journey.')
J = [("file", "Open Payments", ""), ("tap", "Enter", "ravi@npay, ₹1,500"), ("clock", "Check History", "another tab"), ("file", "Back to Payments", ""), ("check", "Keep editing", "same payment")]
P = []
for i, (ic, t, sub) in enumerate(J):
    x = i * 228
    P.append(tall(x, 0, 208, 104, ic, t, sub, None, 'lit' if i == 4 else ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 52H{x + 226}' + head(x + 226, 52, 'r')))
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "Should the input disappear? No.", f"""  <div class="body">
    {svg('0 0 1120 104', 'Open Payments, enter a payment, check History, back to Payments, keep editing', 'jr', P, 'max-height:118px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("NPay&rsquo;s rule", ul("Keep the draft until a <b>successful</b> payment", "Or until the user <b>discards</b> it"))}
        <div class="rule step" data-label="Essential">{ul("Preservation depends on <b>ownership</b> and <b>identity</b>", "Not on whether a screen is visible")}</div>
      </div>
      {PHONE("img/typed.png", "Draft typed", 150)}
      <div class="step">{PHONE("img/back.png", "After History", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The journey: open Payments, enter ravi@npay and ₹1,500, switch to History to check an earlier transaction, come back, and keep editing the same payment. Should the input disappear? For NPay, no. We preserve it until the user completes the payment successfully or explicitly discards the draft.'),
                  ('SAY', 'Click: the sentence to keep in mind all lesson: state preservation depends on ownership and identity, not merely on whether a screen is visible. The text&rsquo;s simulation compared screen-local state with shared draft state; we will run both for real.'),
                  ('SAY', 'On the right, today&rsquo;s app: the draft typed. Click: after a trip to History and back, the same draft.'),
                  ('CONNECT', 'Start with the familiar approach: local @State.'))))

# ================================================================== Part 2 (2)
divider(2, "Local @State", "Works, until the screen is replaced", 'Two experiments, two results.', 'The familiar code.')
LOC = """struct PaymentsScreen: View {
    @State private var recipient = ""
    @State private var amountText = ""

    var body: some View {
        VStack {
            TextField("Recipient", text: $recipient)
            TextField("Amount", text: $amountText)
        }
        .padding()
    }
}"""
S.append(slide("Part 2 &middot; First experiment: local @State (section 2)", "Kept across tabs; lost when replaced", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Screen-local draft", LOC, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("A: inside a TabView, switch to History and back", ["typed: \"ravi@npay\"", "after History and back: \"ravi@npay\""], 12.5)}</div>
        <div class="step">{console("B: if/else replaces the screen, then shows it again", ["typed: \"ravi@npay\"", "after replacing the screen and back: \"\""], 12.5)}</div>
        <div class="rule step" data-label="So">{ul("A stable TabView kept the state (as in 3.3)", "Removed from the hierarchy, a new identity: reset", "A draft that must survive needs a <b>longer-lived owner</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The familiar approach: recipient and amountText as @State inside PaymentsScreen. It works; the user can type into both fields. But what happens when the screen is removed from the hierarchy? We ran the text&rsquo;s screen two ways.'),
                  ('SAY', 'Click: A, the screen as a tab, switching to History and back: the text survived, as Lesson 3.3 measured. Click: B, the screen inside an if-else that replaces it with another view and then brings it back: the field came back empty. Removing the screen from its structural position ended that identity; the new one started with fresh @State.'),
                  ('SAY', 'Click: so switching tabs does not automatically destroy local state, and a stable TabView preserved it here. But if a payment draft must survive deliberate screen replacement or other navigation changes, it needs a longer-lived owner.'),
                  ('CONNECT', 'Why exactly? Three concepts.'))))

# ================================================================== Part 3 (3, 4)
divider(3, "Value, identity, state", "Three concepts, never confused", 'Lesson 2.8, revisited with proof.', 'The three concepts.')
P = [box(0, 0, 340, 64, 'View value', 'a Swift struct describing UI', None, '', 'code'),
     box(380, 0, 340, 64, 'View identity', 'how SwiftUI links a logical view to state', None, 'lit', 'key'),
     box(760, 0, 340, 64, 'State storage', 'managed values tied to that identity', None, '', 'db'),
     wire('M342 32H376' + head(376, 32, 'r'), None, 'dash'), wire('M722 32H756' + head(756, 32, 'r'))]
S.append(slide("Part 3 &middot; View identity versus view value (section 3)", "A new struct is not a new identity", f"""  <div class="body">
    {svg('0 0 1100 64', 'View value, view identity, state storage', 'vis', P, 'max-height:80px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Lesson 2.8", ul("Views are value types, recreated freely", "<code>@State</code> survives while the <b>identity</b> does"))}
        <div class="step">{card("Experiment (authored)", ul("An editor whose <code>init</code> prints", "Type ravi@npay; re-render the parent twice"))}</div>
      </div>
      <div class="step">{console("Simulator", ["TracedEditor.init (a new view value)", "[Re-render Parent]", "TracedEditor.init (a new view value)", "[Re-render Parent]", "TracedEditor.init (a new view value)", "field: \"ravi@npay\""], 13)}</div>
    </div>
  </div>""", notes(('SAY', 'Three concepts that must not be confused. A view value: a Swift struct describing part of the UI, cheap and recreated all the time. A view identity: how SwiftUI associates a logical view with its state. State storage: the managed values associated with that identity. The value points at an identity; the identity owns the state.'),
                  ('SAY', 'Recall Lesson 2.8: a view struct can be recreated while its @State stays alive. Click: our experiment: an editor whose initializer prints, inside a parent we re-render on purpose. Click: three new view values, three init lines, and the field still says ravi@npay. Writing PaymentsScreen() again does not reset anything; only a new identity does.'),
                  ('CONNECT', 'So change the identity and watch.'))))

IDL = """struct IdentityLab: View {
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            DraftEditor()
                .id(identity)
            Button("Replace View Identity") {
                identity = UUID()
            }
        }
        .padding()
    }
}

struct DraftEditor: View {
    @State private var recipient = ""

    var body: some View {
        VStack {
            TextField("Recipient", text: $recipient)
                .textFieldStyle(.roundedBorder)
            Text("Current: \\(recipient)")
        }
    }
}"""
S.append(slide("Part 3 &middot; Force a state reset with .id() (section 4)", "New identity, new state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 260px;gap:24px;align-items:start">
      {code("IdentityLab.swift", IDL, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {crop("img/idbefore.png", "Typed: Current: ravi@npay", 260)}
        <div class="step">{crop("img/idafter.png", "After Replace View Identity", 260)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s proof. IdentityLab keeps a UUID in @State and gives DraftEditor an explicit identity with .id(identity). The button replaces the UUID. DraftEditor has its own @State recipient and shows it.'),
                  ('SAY', 'Type ravi@npay: "Current: ravi@npay". Click: tap Replace View Identity: the field is empty and "Current:" shows nothing. Changing the explicit identity made SwiftUI treat the editor as a new logical view, and its local state was initialized for that new identity.'),
                  ('CONNECT', 'The text&rsquo;s warning about random IDs, tested.'))))

UNST = """DraftEditor()
    .id(UUID())   // a new identity on every evaluation

Text("Taps: \\(taps)")
Button("Count Tap") { taps += 1 }"""
S.append(slide("Part 3 &middot; Unstable identity (section 4)", "<code>.id(UUID())</code> in body: state dies on every update", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Don&rsquo;t (authored experiment)", UNST, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator", ["typed: \"ravi@npay\"", "[Count Tap]: an unrelated state change", "field: \"\""], 13)}</div>
        <div class="warn step" data-label="Avoid">{ul("Random IDs generated during <code>body</code>", "Any re-evaluation becomes a new view: input lost")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text warns: avoid generating random .id(UUID()) values during normal body evaluation. We tested exactly that: the same DraftEditor, but with .id(UUID()) written inline, next to an unrelated counter.'),
                  ('SAY', 'Click: type ravi@npay, then tap Count Tap. The counter has nothing to do with the editor, but tapping it re-evaluated the parent&rsquo;s body, which generated a new UUID, which gave the editor a new identity: the field is empty. Click: unstable identity destroys useful state and causes unexpected UI behaviour. Use .id with a value that changes only when you mean it to.'),
                  ('CONNECT', 'The fix for NPay: a draft model with a deliberate owner.'))))

# ================================================================== Part 4 (5, 6, 11)
divider(4, "A draft model", "Input, kept as input", 'A struct for what the user is typing, owned by the store.', 'The model.')
PD = """struct PaymentDraft {
    var recipient: String = ""
    var amountText: String = ""
}"""
S.append(slide("Part 4 &middot; Create a payment draft model (section 5)", "A draft is not a payment request", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("Models/PaymentDraft.swift", PD, "font-size:15px")}
        {card("Why a String amount", ul("Mid-typing values like <code>\"1500.\"</code> must be allowed", "Parse only when reviewing (2.11, 2.12)"))}
      </div>
      <div class="step">{tbl(["Draft", "Payment request"], [("Incomplete user input", "Validated domain data"), ("<code>amountText: String</code>", "<code>amountPaise: Int</code>"), ("Can be invalid", "Valid by construction"), ("Edited freely", "Immutable once made")], 'tbl')}
        <div class="gap"></div>
        <div class="rule" data-label="Don&rsquo;t confuse them">{ul("Different types, different jobs")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Instead of two independent screen-local properties, one model for the draft: PaymentDraft, an ordinary struct holding the user&rsquo;s editable input. The amount stays a String on purpose: while typing, the user may pass through incomplete values such as "1500." that are not yet valid numbers. We parse when the user asks to review, as in Lessons 2.11 and 2.12.'),
                  ('SAY', 'Click: the design distinction. A draft is incomplete user input: a String amount, possibly invalid, edited freely. A payment request is validated domain data: an amount in paise, valid by construction, immutable once made. We should not confuse the two.'),
                  ('CONNECT', 'One practical problem with the name.'))))

S.append(slide("Part 4 &middot; Two lessons, one name (sections 5, 17)", "<code>PaymentDraft</code> twice does not compile", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("3.4&rsquo;s review model + 3.5&rsquo;s draft", "struct PaymentDraft: Identifiable {   // 3.4: the review\n    let id = UUID()\n    let recipient: String\n    let amountPaise: Int\n}\n\nstruct PaymentDraft {                 // 3.5: the input\n    var recipient: String = \"\"\n    var amountText: String = \"\"\n}", "font-size:12.5px")}
        <div class="step">{card("swiftc", err("invalid redeclaration of 'PaymentDraft'"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{tbl(["Type (our names)", "Is"], [("<code>PaymentDraft</code>", "editable input, in the store (3.5)"), ("<code>PaymentReview</code>", "immutable snapshot for the sheet (3.4&rsquo;s type, renamed)")], 'tbl')}</div>
        <div class="rule step" data-label="Section 17">{ul("The review shows a <b>snapshot</b>, not the live draft")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A practical problem: Lesson 3.4 already has a PaymentDraft, the Identifiable review model with an amount in paise. Lesson 3.5 introduces another PaymentDraft, the editable input. Click: put both in one project and the compiler stops: invalid redeclaration of PaymentDraft.'),
                  ('SAY', 'Click: our resolution, flagged as ours: keep the text&rsquo;s PaymentDraft for the editable input, and rename 3.4&rsquo;s review model to PaymentReview. Click: the names now match the jobs, and Section 17&rsquo;s design: when the review opens, it gets an immutable snapshot of what the user is reviewing, not the live draft.'),
                  ('CONNECT', 'Where should the draft live?'))))

ST = """@MainActor
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []

    var paymentDraft = PaymentDraft()

    func clearPaymentDraft() {
        paymentDraft = PaymentDraft()
    }

    // recordDemoPayment(recipient:amountPaise:) as in 3.3
}"""
P = [box(0, 0, 420, 54, 'NPayRootView', 'owns NPayStore', None, '', 'layers'), wire('M210 56V70' + head(210, 70, 'd')),
     box(0, 74, 420, 54, 'NPayStore.paymentDraft', 'recipient + amount text', None, 'lit', 'db'), wire('M210 130V144' + head(210, 144, 'd')),
     box(0, 148, 420, 54, 'PaymentsScreen', 'reads and edits the shared draft', None, '', 'file')]
S.append(slide("Part 4 &middot; Where should the draft live? (sections 6, 11)", "In the store the root owns", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Store/NPayStore.swift", ST, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {svg('0 0 420 202', 'NPayRootView owns NPayStore, which holds the draft that PaymentsScreen edits', 'own', P, 'max-height:200px')}
        <div class="step">{card("Lifetime", ul("As long as the root&rsquo;s store: tab switches, screen recreation"))}</div>
        <div class="step">{card("Acceptable for now (section 11)", ul("Draft = editing state; payment = behaviour", "Split into ViewModels and use cases in Unit 4"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The 3.3 store gets a new property, paymentDraft, and a clearPaymentDraft method that replaces it with an empty draft. Because NPayRootView owns the store with @State, the draft can survive ordinary tab switches and screen recreation for as long as the root lives.'),
                  ('SAY', 'Click: the ownership chain: the root owns the store; the store holds the draft; PaymentsScreen reads and edits it. Click: the text&rsquo;s honest note: the store now mixes editing state and application behaviour. Acceptable while learning; Unit 4 introduces dedicated ViewModels and use cases.'),
                  ('CONNECT', 'How does the screen edit a property of an object?'))))

# ================================================================== Part 5 (7, 8)
divider(5, "@Bindable", "Bindings into an observable object", 'TextFields need bindings; the draft lives in a class.', 'The code.')
BND = """struct PaymentsScreen: View {
    @Bindable var store: NPayStore

    var body: some View {
        VStack(spacing: 16) {
            TextField("Recipient",
                      text: $store.paymentDraft.recipient)
            TextField("Amount",
                      text: $store.paymentDraft.amountText)
        }
        .textFieldStyle(.roundedBorder)
        .padding()
    }
}"""
S.append(slide("Part 5 &middot; Connect the draft using @Bindable (section 7)", "<code>$store.paymentDraft.recipient</code>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("PaymentsScreen (text)", BND, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Wrapper", "Role"], [("<code>@Observable</code>", "the class takes part in Observation"), ("<code>@State</code>", "<b>owns</b> it (NPayRootView)"), ("<code>@Bindable</code>", "gives <b>bindings</b> to its properties")], 'tbl')}</div>
        <div class="step">{card("Owner unchanged", ul("The screen <b>receives</b> the store", "Internals: Unit 4"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Inside PaymentsScreen, the store property is marked @Bindable. That is what makes $store.paymentDraft.recipient legal: a binding that reads and writes a property of a property of an observable object. The TextFields bind to the shared draft instead of local state.'),
                  ('SAY', 'Click: three wrappers, three jobs. @Observable makes the class participate in Observation. @State owns an observable object in the view hierarchy: NPayRootView does that. @Bindable gives bindings to the mutable properties of an object someone else owns. The compiler and Observation internals come in Unit 4.'),
                  ('SAY', 'Click: focus on ownership: the screen receives the store; it does not own it. The 3.3 router used the same @Bindable, inside body, to bind the tab selection.'),
                  ('CONNECT', 'Trace one keystroke.'))))

PL = [("tap", "User types", "TextField edits the string"), ("link", "Binding writes", "$store.paymentDraft.recipient"), ("db", "Store mutates", "paymentDraft.recipient"),
      ("eye", "Observation notes", "readers of that property"), ("diff", "Body re-evaluated", "PaymentsScreen and others"), ("check", "Screen updates", "the draft everywhere")]
P = []
for i, (ic, t, sub) in enumerate(PL):
    x = i * 190
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}', ''))
    if i < 5:
        P.append(wire(f'M{x + 174} 60H{x + 188}' + head(x + 188, 60, 'r')))
S.append(slide("Part 5 &middot; What happens when the user types? (section 8) &middot; conceptual", "Six stages, one keystroke", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1132 120', 'User types, binding writes, store mutates, Observation notes readers, body re-evaluated, screen updates', 'pl', P, 'max-height:140px')}
    <div class="gap"></div>
    <div class="step">{console("onChange diagnostic (section 18), typing ravi@npay", ["Draft changed: Old: \"\" New: \"r\"", "Draft changed: Old: \"r\" New: \"ra\"", "…", "Draft changed: Old: \"ravi@npa\" New: \"ravi@npay\""], 12.5)}</div>
  </div>""", notes(('SAY', 'Only stage 1 came with the text; the rest is our conceptual outline. Click: the user types; the TextField receives the edited string. Click: its binding writes through $store.paymentDraft.recipient. Click: the store&rsquo;s draft mutates. Click: Observation notes that views reading that property depend on it. Click: SwiftUI re-evaluates those bodies. Click: the screen shows the new draft.'),
                  ('SAY', 'Click: the text&rsquo;s debugging tip, onChange of the draft&rsquo;s recipient, in our complete code: nine lines for nine characters, each with the old and new value. Every keystroke is a write into the shared store.'),
                  ('CONNECT', 'When does the draft go away?'))))

# ================================================================== Part 6 (9, 12, 18)
divider(6, "When to clear", "An explicit rule", 'Paid or discarded; nothing else.', 'The rule.')
RL = [("Switching tabs", "preserve"), ("Dismissing the review sheet", "preserve"), ("Navigating to History", "preserve"),
      ("Successful demo payment", "<b>clear</b>"), ("Discard Draft", "<b>clear</b>")]
S.append(slide("Part 6 &middot; When should we clear the draft? (section 9)", "Two events clear it; nothing else does", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      <div>{tbl(["Event", "Draft"], RL, 'tbl')}
        <div class="gap"></div>
        {code("NPayStore", "func clearPaymentDraft() {\n    paymentDraft = PaymentDraft()\n}", "font-size:13.5px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Call it", ul("After the payment is <b>recorded</b>", "When the user confirms Discard"))}</div>
        <div class="warn step" data-label="Not on dismissal">{ul("Dismissing may mean &ldquo;let me fix the amount&rdquo;", "Clearing then loses useful input")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'An explicit rule for NPay. Switching tabs, dismissing the review sheet and navigating to History all preserve the draft. A successful demo payment clears it, and so does tapping Discard Draft. clearPaymentDraft replaces the draft with an empty one.'),
                  ('SAY', 'Click: call it after the payment has been successfully recorded, and when the user confirms a discard. Click: why not clear it when the review sheet dismisses? Because dismissal might mean the user wants to correct the amount; clearing at that point would lose useful input.'),
                  ('CONNECT', 'The text&rsquo;s experiments, run on the complete app.'))))

S.append(slide("Part 6 &middot; Xcode experiments (sections 12, 18)", "The diagnostic fires only on the events that matter", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) 140px 140px;gap:18px;align-items:start">
      {console("Complete app, onChange(of: store.paymentDraft.recipient)", ["1. type ravi@npay, 1500&ensp;&rarr; 9 &times; Draft changed", "2-3. History and back&ensp;&ensp;&ensp;&ensp;&ensp;&rarr; (nothing)", "&ensp;&ensp;&ensp;recipient \"ravi@npay\", amount \"1500\"", "4-5. review, swipe down&ensp;&ensp;&rarr; (nothing)", "&ensp;&ensp;&ensp;recipient \"ravi@npay\", amount \"1500\"", "6. confirm&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&rarr; Old: ravi@npay New: \"\"", "7. back on Payments&ensp;&ensp;&ensp;&ensp;&rarr; recipient \"\", amount \"\"", "Discard Draft &rarr; Discard &rarr; Old: ravi@npay New: \"\""], 12.5)}
      <div class="step">{PHONE("img/cleared.png", "After paying", 140)}</div>
      <div class="step">{PHONE("img/discard.png", "Discard Draft", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s experiments 1 to 7, with the Section 18 diagnostic in place. Typing produced one "Draft changed" per character. Switching to History and back produced nothing, and the fields still held ravi@npay and 1500. Opening the review and swiping it down produced nothing; the draft was intact. Confirming produced exactly one change: ravi@npay to empty, the clear after recording. Back on Payments, both fields were empty.'),
                  ('SAY', 'Click: the Payments tab after paying: empty fields, and the available balance already reduced. Click: Discard Draft, our addition, asks first, with the alert pattern from 3.4; Discard cleared the draft, one more change in the log.'),
                  ('SAY', 'You can also set breakpoints in clearPaymentDraft and recordDemoPayment, as the text suggests, to see exactly when state changes.'),
                  ('CONNECT', 'Experiment 8: restart the app.'))))

# ================================================================== Part 7 (10, 14, 15)
divider(7, "Preservation vs persistence", "Alive is not saved", 'In memory survives navigation, not termination.', 'Restart.')
LT = [("<code>@State</code>", "while the view&rsquo;s identity survives"), ("Shared <code>NPayStore</code>", "while the store instance survives"),
      ("<code>@SceneStorage</code>", "simple scene state, through supported restoration"), ("<code>@AppStorage</code>", "simple values, via UserDefaults"), ("SwiftData", "structured records, local storage")]
S.append(slide("Part 7 &middot; State preservation versus persistence (sections 10, 14)", "Different mechanisms, different lifetimes", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {tbl(["Mechanism", "Survives"], LT, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Experiment 8: relaunch (simulator)", ["typed: \"ravi@npay\", \"1500.50\"", "app terminated, launched again", "after relaunch: \"\", \"\""], 12.5)}</div>
        <div class="rule step" data-label="Definitions">{ul("<b>Preservation</b>: kept while the owner lives", "<b>Persistence</b>: recovered after owner or process is gone")}</div>
        <div class="warn step" data-label="Before persisting">{ul("Recipient and amounts are financial data: privacy first (Unit 6, Unit 7)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Two ideas that are frequently confused. The lifetimes: @State lives while its view identity survives. The shared store lives while its instance survives. @SceneStorage can restore simple scene state through supported restoration. @AppStorage persists simple values through UserDefaults. SwiftData persists structured records to local storage.'),
                  ('SAY', 'Click: experiment 8, run: type a draft, terminate NPay, launch it again: both fields empty. The store is an in-memory object; when the process ended, so did the draft. Click: preservation means keeping a value while its owner is alive; persistence means storing it so it can be recovered after the owner or the process is gone.'),
                  ('SAY', 'Click: for Unit 3 we deliberately preserve the draft in memory. Persistence comes in Unit 6, and a payment draft holds a recipient and an amount: privacy and security must be considered before storing it, which is Unit 7&rsquo;s territory.'),
                  ('CONNECT', 'One more experiment: reset the child, keep the draft.'))))

DIE = """@MainActor @Observable
final class DraftStore { var recipient = "" }

struct DraftIdentityExperiment: View {
    @State private var store = DraftStore()
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            DraftChild(store: store)
                .id(identity)
            Button("Recreate Child Identity") { identity = UUID() }
            Text("Store value: \\(store.recipient)")
        }
        .padding()
    }
}

struct DraftChild: View {
    @Bindable var store: DraftStore
    var body: some View {
        TextField("Recipient", text: $store.recipient)
            .textFieldStyle(.roundedBorder)
    }
}"""
S.append(slide("Part 7 &middot; Reset the child, preserve the draft (section 15)", "Same <code>.id()</code> trick; this time nothing is lost", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 320px;gap:24px;align-items:start">
      {code("DraftIdentityExperiment.swift (condensed)", DIE, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{crop("img/draftexp.png", "After Recreate Child Identity", 320)}</div>
        <div class="step">{console("Simulator", ["before: Store value: ravi@npay", "[Recreate Child Identity]", "after:&ensp;Store value: ravi@npay", "field: \"ravi@npay\""], 12.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s deeper experiment. The same .id() reset as IdentityLab, but the recipient lives in an observable DraftStore owned by the parent, and the child edits it through @Bindable.'),
                  ('SAY', 'Click: type ravi@npay and tap Recreate Child Identity: the field still says ravi@npay. Click: our run: "Store value: ravi@npay" before and after, and the new child&rsquo;s field shows it. Why: the child received a new identity, so any child-local state would reset, but the recipient was never in the child. It belongs to the DraftStore, still alive in the parent. That is the whole lesson in one experiment: move ownership upward to the lifetime you need.'),
                  ('CONNECT', 'Then should everything move up?'))))

# ================================================================== Part 8 (16, 17, 19)
divider(8, "Choosing owners", "As local as possible, as shared as necessary", 'Every piece of state gets the owner its lifetime needs.', 'The table.')
OW = [("Current balance", "Shared NPayStore"), ("Transaction collection", "Shared NPayStore"), ("Payment draft", "Shared feature-level store"),
      ("Review sheet visibility", "PaymentsScreen"), ("Focused text field", "PaymentsScreen"), ("Temporary animation state", "The relevant component"),
      ("Selected tab", "NPayRouter"), ("Navigation paths", "NPayRouter")]
S.append(slide("Part 8 &middot; Should every property go into NPayStore? (section 16)", "No: decide by lifetime and sharing", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {tbl(["State", "Recommended owner"], OW)}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="rule step" data-label="Principle">{ul("Keep state as <b>local</b> as possible", "but as <b>shared</b> as necessary")}</div>
        <div class="step">{card("Why not one global object", ul("Unnecessary coupling", "Every change touches everything"))}</div>
        <div class="step">{card("Later", ul("A dedicated payment-flow model for the draft"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Should every state property go into NPayStore? No. Moving everything into one global object creates unnecessary coupling. Decide ownership by intended lifetime and sharing. The balance and the transactions: the shared store. The payment draft: a shared, feature-level store. The review sheet&rsquo;s visibility and the focused field: PaymentsScreen, they matter only there. Temporary animation state: the component that animates. The selected tab and the paths: the router.'),
                  ('SAY', 'Click: the principle: keep state as local as possible, but as shared as necessary. Click: a single global object couples everything to everything. Click: keeping the draft in NPayStore is a practical learning step; later a dedicated payment-flow model can own it.'),
                  ('CONNECT', 'Shared state raises one more question: two editors.'))))

SNAP = """Button("Review Payment") {
    guard let amountPaise = parsedAmount else { return }
    focusedField = nil
    // an immutable snapshot of what the user is reviewing
    review = PaymentReview(
        recipient: store.paymentDraft.recipient,
        amountPaise: amountPaise)
}

PaymentReviewSheet(review: review) {
    // validate again against the current balance
    if let id = store.recordDemoPayment(
        recipient: review.recipient,
        amountPaise: review.amountPaise) {
        store.clearPaymentDraft()   // recorded: the draft is done
        pendingSuccessID = id
    } else {
        paymentFailed = true
    }
    self.review = nil
}"""
S.append(slide("Part 8 &middot; Two screens, one draft (section 17)", "Edit the draft; review a snapshot", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("PaymentsScreen (complete code, authored)", SNAP, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Shared bindings raise questions", ul("Who owns the editing workflow?", "Should edits appear in both at once?", "What if the draft is discarded?", "Can a review show <b>stale</b> values?"))}
        <div class="step">{card("NPay&rsquo;s answer", ul("Review = immutable <b>snapshot</b> at open", "Confirm re-validates against the current balance", "Editable draft &ne; confirmed input"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Suppose PaymentsScreen and another payment editor both get bindings to the same draft. They can both read and write it. That may be intentional, but it raises coordination questions: which screen owns the editing workflow, should edits in one appear in the other immediately, what happens when the user discards, and can a review sheet show stale values after the draft changes?'),
                  ('SAY', 'Click: NPay&rsquo;s answer, as the text designs it, in our complete code. Review Payment creates an immutable PaymentReview snapshot of what the user is reviewing. Confirm validates again against the store&rsquo;s current balance, as 3.4 measured. On success the store clears the draft, while the sheet still shows the snapshot, so nothing on screen changes under the user. Editable draft state and confirmed payment input stay separate.'),
                  ('CONNECT', 'The final architecture.'))))

P = [box(250, 0, 420, 54, 'NPayRootView', 'owns shared application objects', None, '', 'layers'),
     wire('M460 56V70H210V86' + head(210, 86, 'd')), wire('M460 56V70H710V86' + head(710, 86, 'd')),
     box(0, 90, 420, 54, 'NPayRouter', 'tabs and navigation paths', None, '', 'grid'),
     box(500, 90, 420, 54, 'NPayStore', 'balance, transactions, draft', None, 'lit', 'db'),
     wire('M710 146V162' + head(710, 162, 'd')),
     box(500, 166, 420, 54, 'PaymentsScreen', 'edits the shared draft through @Bindable', None, '', 'file')]
S.append(slide("Part 8 &middot; Final NPay architecture (section 19)", "Two owned objects; one draft, edited in place", f"""  <div class="body">
    {svg('0 0 920 220', 'NPayRootView owns NPayRouter and NPayStore; PaymentsScreen edits the store draft', 'fin', P, 'max-height:250px')}
    <div class="gap"></div>
    <div class="step">{tbl(["Checkpoint", "In the simulator"], [("Draft across tab switches", "kept"), ("Draft across review dismissal", "kept"), ("Draft after a recorded payment", "cleared"), ("Draft after relaunch", "gone: in memory only")])}</div>
  </div>""", notes(('SAY', 'The final architecture for Lesson 3.5. NPayRootView owns the shared application objects: NPayRouter for tabs and navigation paths, NPayStore for the balance, the transactions and now the draft. PaymentsScreen edits the shared draft through @Bindable.'),
                  ('SAY', 'Click: the integration checkpoint the text set, measured: the draft survived tab switches and the review&rsquo;s dismissal, was cleared after a recorded payment, and was gone after a relaunch, because it is preserved in memory, not persisted. The integration code is ours, written out in the lesson text file.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.5', (), [("diff", "Identity owns state", "new values keep it; a new identity resets it"),
                     ("db", "Give drafts an owner", "store + @Bindable; clear when paid or discarded"),
                     ("shield", "Preserved is not persisted", "in memory dies with the process")],
         'Three things to remember. A view value is just a struct; state belongs to the view&rsquo;s identity, so recreating structs keeps it and a new identity, from replacement or .id, resets it. When input must survive navigation, move it to an owner whose lifetime spans the journey, like NPayStore, edit it through @Bindable, and clear it only on a recorded payment or an explicit discard. And preservation is not persistence: anything held in memory is gone when the process ends.')

review_divider(9)
review([("code", "Question", "Does recreating a view struct reset @State?",
         "Does recreating a SwiftUI view struct necessarily reset its <code>@State</code>?", "No",
         "Three new <code>TracedEditor</code> values; the field still said ravi@npay.",
         "Confusing a view value with its identity.", "Some say yes.", None),
        ("key", "Choose one", "What can changing a view's .id() cause?",
         "What can changing a view&rsquo;s explicit <code>.id()</code> cause?<br>A. Automatic persistence<br>B. A state identity reset<br>C. A new iOS process", "B",
         "IdentityLab: Replace View Identity emptied the field.",
         "Thinking .id is only for lists.", "Most pick B.", None),
        ("db", "Choose one", "Why put the NPay draft in a shared store?",
         "Why place the NPay payment draft in a shared store?<br>A. To encrypt it automatically<br>B. To create a new thread<br>C. To give it a lifetime beyond one screen", "C",
         "The root owns the store; the draft outlives screen changes.",
         "Expecting the store to add security.", "Most pick C.", None),
        ("link", "Choose one", "What does @Bindable provide?",
         "What does <code>@Bindable</code> provide?<br>A. Bindings to mutable observable properties<br>B. Database persistence<br>C. Background execution", "A",
         "<code>$store.paymentDraft.recipient</code> for a TextField.",
         "Thinking @Bindable owns the object.", "Most pick A.", None),
        ("eye", "Question", "Should dismissing the review erase the draft?",
         "Should dismissing the review sheet automatically erase the payment draft?", "No",
         "Dismissal may mean &ldquo;let me fix it&rdquo;; our swipe-down left the draft intact.",
         "Clearing on every exit.", "Most say no.", None),
        ("shield", "Question", "Does the in-memory NPayStore survive termination?",
         "Does an in-memory <code>NPayStore</code> automatically survive app termination?", "No",
         "After a relaunch the fields were empty.",
         "Treating preservation as persistence.", "Most say no.", None),
        ("diff", "Predict the result", "DraftEditor().id(UUID()) and an unrelated tap?",
         "A parent shows <code>DraftEditor().id(UUID())</code> and a counter. The user types ravi@npay, then taps the counter. What does the field show?<br>A. ravi@npay<br>B. Nothing: it reset<br>C. The counter value", "B",
         "The re-evaluated body made a new UUID, so a new identity.",
         "Thinking .id(UUID()) is harmless.", "Some pick A.", None),
        ("layers", "Predict the result", "Child identity recreated; where's the recipient?",
         "<code>DraftChild</code> edits a parent-owned <code>DraftStore</code> through <code>@Bindable</code>. Its <code>.id</code> is replaced. What does the field show?<br>A. ravi@npay<br>B. Empty<br>C. A compile error", "A",
         "The value lives in the store, not the child: &ldquo;Store value: ravi@npay&rdquo;.",
         "Assuming any .id change loses data.", "Some pick B.", None),
        ("clock", "Choose one", "From 3.4: what decides whether sheet(item:) shows?",
         "From Lesson 3.4: what makes <code>sheet(item: $review)</code> present?<br>A. <code>review</code> becoming non-nil<br>B. A navigation path change<br>C. A Bool named isPresented", "A",
         "An optional Identifiable item: nil means no sheet.",
         "Mixing presentation with navigation.", "Most pick A.", "Spaced review from Lesson 3.4.")])

S.append(next_slide('3.5', [("3.6", "SwiftUI animations &amp; transitions", "balance updates, confirmation, success feedback; identity in animation"),
                            ("Unit 4", "ViewModels, use cases, Observation internals", "a payment-flow model owns the draft"),
                            ("Unit 6", "Persistence", "drafts that survive a relaunch, with privacy in mind")],
                    'Lesson 3.6 animates the balance, the confirmation and the success feedback, and identity matters there too. Unit 4 gives the draft a dedicated payment-flow model and explains Observation and @Bindable from the compiler&rsquo;s side. Unit 6 adds persistence, so a draft could survive a relaunch, after deciding whether it should.'))

S.append(lab_slide('3.5', "A draft that survives on purpose", "Move the draft into the store; prove each lifetime.",
                   ["Run IdentityLab and DraftIdentityExperiment.",
                    "Add <code>PaymentDraft</code>; rename 3.4&rsquo;s to <code>PaymentReview</code>.",
                    "Store + <code>@Bindable</code>; add <code>clearPaymentDraft()</code>.",
                    "Add the onChange diagnostic; run experiments 1&ndash;7.",
                    "Add Discard Draft with a confirmation.",
                    "Relaunch: what survives?"],
                   "", 'Expected, as in our run: IdentityLab resets, DraftIdentityExperiment keeps ravi@npay; the diagnostic fires on typing, on the recorded payment and on Discard, never on tab switches or sheet dismissal; after a relaunch the draft is gone.',
                   side=f'<div>{card("You hand in", ul("Your diagnostic log for experiments 1&ndash;7", "Your owner table for NPay&rsquo;s state", "One sentence: preservation vs persistence"))}</div>'))

end_slide('3.5', 'State Preservation<br>Across Navigation', 'Lesson 3.6 &mdash; SwiftUI Animations &amp; Transitions',
          'You can now separate view values, identity and state storage, predict and force state resets, model a draft separately from a payment request, give it a store-owned lifetime edited through @Bindable, clear it on purpose, and tell preservation from persistence.',
          'Next, Lesson 3.6: SwiftUI animations and transitions. We animate NPay&rsquo;s balance updates, payment confirmation and success feedback.')

write_deck(OUT35, '3.5', 'State Preservation', 'State Preservation')
