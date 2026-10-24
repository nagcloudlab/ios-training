"""Generates decks/unit-2/lesson-2.8/index.html from the Lesson 2.8 text (@State and Reactive UI).
The text came in two parts (Sections 1-11, 12-18), grouped into 8 Parts. Console output and screenshots come from
tools/sim2_8 (a scripted SwiftUI app run in the iOS Simulator; buttons activated through accessibility); the compiler
error and the property-wrapper example were run with swiftc."""
import html, os, re, sys
OUT28 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.8', '@State and<br>Reactive UI',
            'Tap <b>Add Demo ₹1,000</b> and the balance becomes ₹26,000. Nobody updated a label. <b>Who did?</b>',
            'Until now NPay&rsquo;s balance has been a hard-coded string. Today it becomes state: tap a button and the screen follows. We learn @State the usual way: build, predict, observe, investigate, experiment, integrate. How SwiftUI manages mutable state, why a view struct can be recreated without losing its state, and how a variable change becomes a visible update. Every console line and screenshot came from the iOS Simulator; buttons were activated through accessibility, as in 2.7.')
outcomes_slide('2.8', [("diff", "Why a plain <code>var</code> in a view <b>won&rsquo;t compile</b>"),
                       ("code", "What <code>@State</code> is: a <b>property wrapper</b>"),
                       ("layers", "Where state <b>lives</b>, and why it survives"),
                       ("eye", "How a change becomes a <b>screen update</b>"),
                       ("link", "Who <b>owns</b> state; what <code>$balance</code> is"),
                       ("frame", "When state <b>resets</b>: identity")])
where_slide('2.8', 'Today: the balance changes', (),
            '2.7: buttons that run closures, but only print.',
            '<code>@State</code>: a tap changes what is on screen.',
            'Last lesson the quick actions ran closures but nothing on screen changed. Today a button changes a value and SwiftUI updates the screen by itself. That is the heart of SwiftUI.',
            'The problem.')

# ================================================================== Part 1 (1)
divider(1, "A balance that changes", "Hard-coded no more", 'Text("₹25,000") can never change.', 'The requirement.')
S.append(slide("Part 1 &middot; Our balance cannot change (section 1)", "Tap, and the balance should follow", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Requirement", ul("Tap <b>Add Demo ₹1,000</b>", "The balance updates <b>immediately</b>"))}
        {card("Today", ul("No manual label updates", "The display is <b>derived from state</b>", "A demo: no money moves"))}
      </div>
      {PHONE("img/final.png", "Start: ₹25,000", 190)}
      <div class="step">{PHONE("img/taps.png", "After 3 taps: ₹28,000", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'Until 2.7 the balance card said Text("₹25,000"): a fixed string. A payment app shows changing information. The requirement: tap Add Demo ₹1,000 and the balance updates immediately. On the left, today&rsquo;s finished NPay at launch.'),
                  ('SAY', 'Click: the same app after three taps: ₹28,000. Nobody replaced a label; the display is derived from the current state. It is a demo, no money moves. How?'),
                  ('CONNECT', 'First, try the obvious thing.'))))

# ================================================================== Part 2 (2)
divider(2, "A normal variable", "Predict: does it compile?", 'Give the view a var and change it in a button.', 'Predict first.')
EXP1 = """struct ContentView: View {
    var balance = 25000

    var body: some View {
        VStack(spacing: 20) {
            Text("Balance: ₹\\(balance)")
            Button("Add ₹1,000") {
                balance += 1000
            }
        }
    }
}"""
S.append(slide("Part 2 &middot; Experiment 1: a normal Swift variable (section 2)", "It doesn&rsquo;t compile", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", EXP1, "font-size:14.5px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{err("left side of mutating operator isn&rsquo;t mutable: &lsquo;self&rsquo; is immutable")}<p class="small muted" style="margin:4px 0 0">swiftc, iOS 26.5 SDK, at <code>balance += 1000</code></p></div>
        <div class="step">{card("Why", ul("<code>body</code> is a <b>nonmutating</b> getter", "The action can&rsquo;t change the view&rsquo;s stored property", "<code>var account = Account(…)</code> works: <code>account</code> is mutable"))}</div>
        <div class="rule step" data-label="Key insight">{ul("A view struct is a <b>description</b>, not a mutable controller")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Temporarily replace ContentView with this: an ordinary var balance, and a button that adds 1,000. Predict: does it compile? It is declared var, after all.'),
                  ('SAY', 'Click: the real compiler error: left side of mutating operator isn&rsquo;t mutable: self is immutable, at balance += 1000.'),
                  ('SAY', 'Click: why. Structs have value semantics, from Unit 01. var account = Account(balance: 25000); account.balance += 1000 works, because account is a mutable variable. But a view&rsquo;s body is a nonmutating computed property, and the escaping button action captured an immutable self. It cannot change a stored property of the view value.'),
                  ('SAY', 'Click: the key insight: a SwiftUI view struct is a description of UI, not a mutable controller object. Mutable state has to live somewhere else.'),
                  ('CONNECT', 'Change one word.'))))

# ================================================================== Part 3 (3-4)
divider(3, "@State", "One line changes everything", 'var balance → @State private var balance.', 'Run it.')
EXP2 = """struct ContentView: View {
    @State private var balance = 25000

    var body: some View {
        VStack(spacing: 20) {
            Text("Balance: ₹\\(balance)")
                .font(.title)
            Button("Add Demo ₹1,000") {
                balance += 1000
            }
            .buttonStyle(.borderedProminent)
        }
    }
}"""
S.append(slide("Part 3 &middot; Experiment 2: introduce @State (section 3)", "Change a property; the screen follows", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", EXP2, "font-size:14px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("A print in body; button activated 3 times", ["body: balance = 25000", "body: balance = 26000", "body: balance = 27000", "body: balance = 28000"], 13)}</div>
        <div class="rule step" data-label="What changed">{ul("No refresh call, no label replaced", "We updated a <b>property</b>; SwiftUI did the rest")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Change only one line: var balance becomes @State private var balance. It compiles. Run it and tap the button.'),
                  ('SAY', 'Click: with a print in body, activating the button three times: body ran with 25,000, then 26,000, 27,000, 28,000. Each change produced a new description with the new value.'),
                  ('SAY', 'Click: what changed? We did not call a refresh function. We did not replace a label. We updated a property, and SwiftUI handled the interface update.'),
                  ('CONNECT', 'So what is @State exactly?'))))

PARTS = [("<code>@State</code>", "a SwiftUI <b>property wrapper</b>"), ("<code>private</code>", "only this view can touch it"), ("<code>var</code>", "mutable"),
         ("<code>balance</code>", "the property name"), ("<code>25000</code>", "the <b>initial</b> value"), ("type", "inferred: <code>Int</code>")]
S.append(slide("Part 3 &middot; What exactly is @State? (section 4)", "<code>@State private var balance = 25000</code>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {tbl(["Part", "Meaning"], PARTS, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("@State", ul("Local mutable state <b>owned by a view</b>", "Takes part in SwiftUI&rsquo;s <b>update system</b>"))}
        <div class="step">{console("type(of:) inside the view", ["balance:   Int", "_balance:  State&lt;Int&gt;", "$balance:  Binding&lt;Int&gt;   (Part 8)"], 14)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', '@State is a SwiftUI property wrapper: a way for a view to own local mutable state that takes part in SwiftUI&rsquo;s update system. The declaration, part by part: the wrapper, private so only this view uses it, var because it changes, the name, the initial value, and the type, inferred as Int.'),
                  ('SAY', 'Click: we printed three types inside a view. balance is a plain Int. _balance, with an underscore, is the wrapper itself: State of Int, the text&rsquo;s "conceptually State of Int", confirmed. And $balance is a Binding of Int, which Part 8 explains.'),
                  ('CONNECT', 'Where do _balance and $balance come from? Property wrappers, in plain Swift.'))))

# ================================================================== Part 4 (5)
divider(4, "Property wrappers", "Plain Swift underneath", 'Build a wrapper ourselves.', 'NonNegative.')
NN = """@propertyWrapper
struct NonNegative {
    private var storage: Int
    var wrappedValue: Int {
        get { storage }
        set { storage = max(0, newValue) }
    }
    init(wrappedValue: Int) {
        storage = max(0, wrappedValue)
    }
}

struct Account {
    @NonNegative var balance = 25000
}

var account = Account()
account.balance = -500
print(account.balance)"""
TR = """struct Account {   // teaching approximation
    private var _balance =
        NonNegative(wrappedValue: 25000)
    var balance: Int {
        get { _balance.wrappedValue }
        set { _balance.wrappedValue = newValue }
    }
}"""
S.append(slide("Part 4 &middot; Property wrapper transformation (section 5)", "<code>@NonNegative</code>: a wrapper in plain Swift", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("NonNegative.swift (Mac, swiftc)", NN, "font-size:12.5px")}
        <div class="step" style="margin-top:10px">{console("Output", ["0"], 15)}</div></div>
      <div>
        <div class="step">{code("What the compiler generates, roughly", TR, "font-size:13px")}</div>
        <div class="rule step" data-label="@State adds" style="margin-top:12px">{ul("Same mechanism: <code>_balance</code> + accessors", "Plus <b>SwiftUI-managed storage</b> and updates")}</div></div>
    </div>
  </div>""", notes(('SAY', 'A custom wrapper in plain Swift: NonNegative stores an Int and clamps anything below zero. Account uses it on balance. We set -500 and print. Click: we compiled and ran it on a Mac: 0. The setter clamped it.'),
                  ('SAY', 'Click: what the compiler does, as a teaching approximation: it creates hidden backing storage, _balance, holding a NonNegative, and a computed balance property whose get and set go through wrappedValue. That is where the _balance name we printed for @State comes from.'),
                  ('SAY', 'Click: @State uses the same language mechanism, but its wrapper does something extra: it connects to storage that SwiftUI manages, and to SwiftUI&rsquo;s dependency updates. NonNegative is not how State is implemented; it shows the syntax.'),
                  ('CONNECT', 'Which raises the big question: where is that storage?'))))

# ================================================================== Part 5 (6, 13)
divider(5, "Where state lives", "Not in the struct", 'View values come and go. The balance stays.', 'We recreated the view.')
SV = """struct Survivor: View {
    let tick: Int
    @State private var balance = 25000
    init(tick: Int) {
        self.tick = tick
        print("Survivor value created (tick \\(tick))")
    }
    var body: some View {
        let _ = print("body: tick \\(tick), balance = \\(balance)")
        Button("Add") { balance += 1000 }
    }
}"""
S.append(slide("Part 5 &middot; Where is @State stored? (sections 6, 13)", "New view value, same state", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Survivor.swift (parent changes tick)", SV, "font-size:12.5px")}
        <div class="rule step" data-label="25000 is" style="margin-top:12px">{ul("The <b>initial</b> value for this identity", "Not re-assigned when <code>body</code> runs")}</div></div>
      <div class="step">{console("Add ×3, then the parent changed tick twice", ["Survivor value created (tick 0)", "body: tick 0, balance = 25000", "… Add ×3 …", "body: tick 0, balance = 28000", "Survivor value created (tick 1)", "body: tick 1, balance = 28000", "Survivor value created (tick 2)", "body: tick 2, balance = 28000"], 13)}
        <div class="gap"></div>
        {card("So", ul("The <b>struct</b> was created again, twice", "The <b>state</b> stayed at 28000: it lives with the view&rsquo;s <b>identity</b>"))}</div>
    </div>
  </div>""", notes(('SAY', 'The most important idea today. A view struct is a value that SwiftUI can recreate during normal updates, yet its @State does not reset. To see it, this Survivor view prints when its struct is created and when its body runs. Its parent passes a tick that changes, which forces a new Survivor value.'),
                  ('SAY', 'Click: the console. Created at tick 0 with 25,000. Three activations of Add: 28,000. Then the parent changed tick twice: two brand-new Survivor values were created, and both bodies saw balance 28,000. The struct is new; the state is not.'),
                  ('SAY', 'That is because SwiftUI keeps the state in storage associated with the view&rsquo;s identity, not inside the struct. Click: and it answers Section 13: = 25000 is the initial value SwiftUI uses when it first sets up state for that identity, not an assignment that runs every time body runs. The text&rsquo;s analogy is a hotel room: the sign on the door can be replaced, and the guest&rsquo;s belongings stay with the room.'),
                  ('CONNECT', 'A picture of that, and one warning.'))))

P = [box(0, 0, 340, 56, 'ContentView value', 'may be recreated', None, '', 'file'),
     wire('M344 28H396' + head(396, 28, 'r'), None, 'dash'),
     box(400, 0, 340, 56, 'SwiftUI state storage', 'keyed by view identity', None, 'lit', 'layers'),
     wire('M744 28H796' + head(796, 28, 'r')),
     box(800, 0, 336, 56, 'balance = 28000', 'survives re-evaluation', None, '', 'db')]
S.append(slide("Part 5 &middot; View value vs persistent UI state (section 6) &middot; conceptual", "The struct describes; SwiftUI keeps", f"""  <div class="body">
    {svg('0 0 1136 56', 'The ContentView value may be recreated; SwiftUI state storage, keyed by identity, keeps balance', 'store', P, 'max-height:70px')}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("Like a form", ul("SwiftUI may recreate the <b>form template</b>", "The <b>values entered</b> are kept separately"))}
      <div class="rule step" data-label="Not persistence">{ul("Not saved to disk", "App terminated: the value is <b>not guaranteed</b> to survive", "Persistence: a later unit")}</div>
    </div>
  </div>""", notes(('SAY', 'The model. The ContentView value may be recreated. SwiftUI&rsquo;s state machinery keeps storage associated with the view&rsquo;s identity, and that is where balance lives. The private memory layout is not public; this is a conceptual model. The text&rsquo;s other analogy: a form template can be reprinted, while the values entered into the form are kept separately.'),
                  ('SAY', 'Click: one important distinction. @State is not durable persistence. It does not save to disk; if NPay is terminated, the value is not guaranteed to survive. Persistence, SwiftData and the Keychain come later.'),
                  ('CONNECT', 'Now follow a change from tap to screen.'))))

# ================================================================== Part 6 (7-9, 16)
divider(6, "From change to screen", "UI = f(State)", 'balance changes. What does SwiftUI do?', 'The pipeline.')
PIPE = [("tap", "User taps Add Demo ₹1,000", "the event reaches SwiftUI (2.7)"), ("code", "The action runs", "balance += 1000"),
        ("layers", "State storage updated", "SwiftUI notes the change"), ("eye", "Dependent bodies re-evaluated", "new descriptions with ₹26,000"),
        ("layout", "Layout as needed", "only what changed"), ("frame", "Rendered", "the new balance on screen")]
P = [box(0, i * 52, 600, 44, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(PIPE)]
S.append(slide("Part 6 &middot; What happens when balance changes? (section 7) &middot; conceptual", "From a tap to a new balance on screen", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:28px;align-items:center">
      {svg('0 0 600 304', 'Tap, action runs, state updated, dependent bodies re-evaluated, layout, rendered', 'pipe', P, 'max-height:330px')}
      <div class="step"><p style="font-size:34px;font-weight:700;margin:0;text-align:center">UI = f(State)</p>
        <p class="small muted" style="text-align:center;margin:8px 0 0">The description is a function of the current state.</p></div>
    </div>
  </div>""", notes(('SAY', 'A conceptual pipeline; only stage 1 was in the text&rsquo;s widget, and SwiftUI&rsquo;s scheduling is private. Click: the user taps, and as in 2.7 the event reaches SwiftUI. Click: the action runs: balance += 1000. Click: the write goes to SwiftUI&rsquo;s state storage, and SwiftUI notes the change. Click: views whose body read balance are evaluated again, producing descriptions with ₹26,000. Click: layout runs where needed. Click: the new balance is rendered.'),
                  ('SAY', 'Click: the mental model: UI equals f of State. The interface description depends on the current state; change the state and SwiftUI updates the presentation.'),
                  ('CONNECT', 'Does that mean the whole screen is rebuilt? We asked SwiftUI.'))))

PC = """var body: some View {
    let _ = Self._printChanges()

    return VStack(spacing: 20) {
        Text("₹\\(balance)")
        Button("Add Money") {
            balance += 1000
        }
    }
}"""
S.append(slide("Part 6 &middot; Observe body evaluation (sections 8&ndash;9, 16)", "Ask SwiftUI why body ran", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift (temporary)", PC, "font-size:14px")}
        <div class="gap"></div>
        {card("In Xcode, too", ul("Breakpoint on <code>balance += 1000</code>", "LLDB: <code>po balance</code> (when it can evaluate)"))}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Simulator console: launch, then Add Money ×2", ["ChangesDemo: @self, @identity, _balance changed.", "ChangesDemo: _balance changed.", "ChangesDemo: _balance changed."], 13)}</div>
        <div class="rule step" data-label="Not a redraw count">{ul("Init &ne; body &ne; layout &ne; rendering", "Body evaluations aren&rsquo;t frames drawn")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Self._printChanges() is a SwiftUI debugging helper: called inside body, it prints why the body is being evaluated. Note the return before VStack: once body contains a let statement, the view expression needs an explicit return here.'),
                  ('SAY', 'Click: our run. At launch: @self, @identity and _balance changed, everything is new. After each Add Money: only "_balance changed". SwiftUI knows exactly which state triggered the update. In 2.1 we saw the same pattern with a counter.'),
                  ('SAY', 'Click: several evaluations do not mean the screen was redrawn several times. View initialization, body evaluation, layout and rendering are separate stages. The text&rsquo;s widget made the point visually: only the balance changes; the header and actions stay as they are.'),
                  ('SAY', 'The text also suggests a breakpoint on balance += 1000 and po balance in LLDB; whether LLDB can evaluate it depends on the debug context and optimisation.'),
                  ('CONNECT', 'Now put the state into NPay itself.'))))

# ================================================================== Part 7 (10-12, 17)
divider(7, "State in NPay", "One owner, one-way flow", 'Change only what is needed.', 'BalanceCard first.')
BC = """struct BalanceCard: View {
    let balance: Int

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Available Balance")
                .font(.subheadline)
            Text(balance,
                 format: .currency(code: "INR")
                     .precision(.fractionLength(0)))
                .font(.largeTitle.bold())
            Text("NPay Demo Account")
                .font(.caption)
        }
        // same modifiers as 2.6
    }
}"""
CV = """@State private var balance = 25000   // ContentView

BalanceCard(balance: balance)

Button("Add Demo ₹1,000") {
    balance += 1000
}
.buttonStyle(.borderedProminent)"""
S.append(slide("Part 7 &middot; Integrate @State into NPay (sections 10, 12)", "Steps A, B, C", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("A: BalanceCard receives a value", BC, "font-size:12.5px")}</div>
      <div>{code("B, C: ContentView owns it", CV, "font-size:13.5px")}
        <div class="gap"></div>
        <div class="step">{console("formatted, in the simulator", ["25000 → ₹25,000"], 14)}</div>
        <div class="gap"></div>
        <div class="step">{console("BalanceCard body, Add ×3 then Send", ["BalanceCard body: 25000 … 26000 … 27000 … 28000", "Send tapped"], 13)}</div></div>
    </div>
  </div>""", notes(('SAY', 'Step A: BalanceCard gets a let balance: Int instead of a fixed string, and shows it with a currency format: INR, no decimal places, which printed ₹25,000 in the simulator. The modifiers are the same as in 2.6. BalanceCard does not own mutable state; it receives a value.'),
                  ('SAY', 'Steps B and C: ContentView gets @State private var balance = 25000, passes it with BalanceCard(balance: balance), and adds an Add Demo ₹1,000 button below the card.'),
                  ('SAY', 'Click: the format check. Click: with a print in BalanceCard&rsquo;s body, three activations: the card was evaluated with 26,000, 27,000, 28,000; then Send still printed "Send tapped": the quick actions keep working. The screenshots on the first slide are this exact code.'),
                  ('CONNECT', 'Why does ContentView own the balance, and not the card?'))))

P = [box(368, 0, 400, 56, 'ContentView', 'owns @State balance', None, 'lit', 'layers'),
     wire('M468 60V96H184V124' + head(184, 124, 'd')), wire('M952 124V96H668V60' + head(668, 64, 'u'), None, 'dash'),
     box(0, 130, 368, 56, 'BalanceCard', 'reads balance', None, '', 'file'),
     box(768, 130, 368, 56, 'Add Demo button', 'changes balance', None, '', 'tap')]
PROD = [("bank", "Trusted backend", "authoritative balance"), ("link", "Networking service", "authenticated fetch"),
        ("layers", "ViewModel / app state", "loading, errors, display"), ("file", "BalanceCard", "displays it")]
P2 = [box(i * 290, 0, 266, 56, t, sub, None, '', ic) for i, (ic, t, sub) in enumerate(PROD)] + \
     [wire(f'M{i * 290 + 268} 28H{i * 290 + 286}' + head(i * 290 + 286, 28, 'r')) for i in range(3)]
S.append(slide("Part 7 &middot; State ownership (sections 11, 17)", "The parent owns; children read; actions change", f"""  <div class="body">
    {svg('0 0 1136 186', 'ContentView owns the balance; BalanceCard reads it; the Add button changes it', 'own', P, 'max-height:190px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("One-way data flow", ul("State &rarr; descriptions &rarr; screen", "Actions change state, never the card"))}
      <div class="step">{card("A real payment app (17)", ul("The <b>backend</b> owns the real balance", "A local <code>+= 1000</code> is <b>not</b> a transaction"))}</div>
    </div>
    <div class="step" style="margin-top:12px">{svg('0 0 1136 56', 'Trusted backend, networking service, ViewModel, BalanceCard', 'prod', P2, 'max-height:60px')}</div>
  </div>""", notes(('SAY', 'Why does ContentView own the state? Because it coordinates both the button that changes the balance and the card that shows it. The parent owns the state and passes values down; the card only reads; the button&rsquo;s action changes the state, which produces new descriptions. That is one-way data flow. Two-way bindings come next lesson.'),
                  ('SAY', 'Click: Section 17&rsquo;s architecture decision. @State is right for this demo of local UI state. In a real payment app the authoritative balance comes from a trusted backend. Click: a production shape: backend, an authenticated networking service, a ViewModel that manages loading, errors and the displayed data, and BalanceCard showing it. The client must never treat a locally incremented number as a real transaction. Later units also store money as paise in Int64, as Unit 01 did; today&rsquo;s whole-rupee Int is for the demo.'),
                  ('CONNECT', 'Last question: when does @State reset?'))))

# ================================================================== Part 8 (14-15)
divider(8, "Identity and $balance", "When state resets; what $ gives you", 'State is tied to identity. Change the identity...', 'Run the experiment.')
ID = """struct IdentityExperiment: View {
    @State private var identity = UUID()

    var body: some View {
        VStack(spacing: 20) {
            CounterView()          // @State count = 0
                .id(identity)
            Button("Replace Identity") {
                identity = UUID()
            }
        }
    }
}"""
S.append(slide("Part 8 &middot; When does @State reset? (section 14)", "New identity, fresh state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:28px;align-items:start">
      <div>{code("IdentityExperiment.swift", ID, "font-size:13px")}
        <div class="step" style="margin-top:10px">{console("Increment ×3, then Replace Identity", ["CounterView body: count = 0 … 1 … 2 … 3", "CounterView body: count = 0"], 13)}</div></div>
      <div>
        <div class="cols" style="{TWO};gap:12px">{crop("img/identity-before.png", "After 3 increments", 200)}<div class="step">{crop("img/identity-after.png", "After Replace Identity", 200)}</div></div>
        <div class="rule step" data-label="Avoid" style="margin-top:12px">{ul("<code>.id(UUID())</code> created <b>in body</b>", "Every evaluation would reset state")}</div></div>
    </div>
  </div>""", notes(('SAY', 'CounterView has its own @State count. The parent gives it an explicit identity with .id, stored as a UUID in the parent&rsquo;s state, and a button that replaces that UUID.'),
                  ('SAY', 'We activated Increment three times: count 1, 2, 3, on the left. Click: then Replace Identity: count 0, on the right. Changing .id gave SwiftUI a different identity for CounterView, so the old state was no longer associated with it and a new state started from 0. Same result as 2.1&rsquo;s identity experiment.'),
                  ('SAY', 'Click: so never create .id(UUID()) inside body: every evaluation would produce a new identity and reset the state, and SwiftUI would replace the view each time. Here the UUID lives in @State and changes only on purpose.'),
                  ('CONNECT', 'One last piece of syntax: the dollar sign.'))))

P = [box(384, 0, 368, 56, '@State balance', 'SwiftUI-managed state', None, 'lit', 'layers'),
     wire('M480 60V96H184V124' + head(184, 124, 'd')), wire('M656 60V96H952V124' + head(952, 124, 'd')),
     box(0, 130, 368, 56, 'balance', 'the Int value', None, '', 'code'),
     box(768, 130, 368, 56, '$balance', 'Binding&lt;Int&gt;: read and write', None, '', 'link')]
S.append(slide("Part 8 &middot; What does $balance mean? (section 15)", "The value, and a binding to it", f"""  <div class="body">
    {svg('0 0 1136 186', 'From @State balance: balance is the Int value; $balance is a Binding of Int', 'proj', P, 'max-height:190px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      {console("type(of:) inside the view", ["balance:  Int", "$balance: Binding&lt;Int&gt;"], 14)}
      <div class="step">{card("Next lesson", ul("Pass <code>$balance</code> to a child", "The child <b>edits the parent&rsquo;s</b> state, no copy"))}</div>
    </div>
  </div>""", notes(('SAY', 'balance gives the wrapped value, an Int. $balance gives the projected value, which for @State is a Binding of Int, as we printed. A binding is a reference to state stored elsewhere that you can read and write.'),
                  ('SAY', 'Click: that is Lesson 2.9: pass $balance to a child view, a balance editor, and the child can change state owned by its parent without creating a second, independent copy.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.8', (), [("code", "@State is a wrapper", "view-owned state in SwiftUI storage"),
                     ("layers", "Identity keeps it", "new struct, same state; new id, fresh state"),
                     ("diff", "UI = f(State)", "change state; SwiftUI updates the screen")],
         'Three things to remember. A view struct cannot change its own stored properties, so @State, a property wrapper, gives it state that SwiftUI stores for it. That state belongs to the view&rsquo;s identity: the struct can be recreated and the state survives, but a new identity starts fresh. And the screen is a function of state: change the state in an action and SwiftUI re-evaluates what depends on it.')

review_divider(8)
review([("code", "Choose one", "What is @State?",
         "What is <code>@State</code>?<br>A. A SwiftUI property wrapper<br>B. A database<br>C. A background thread", "A",
         "<code>_balance</code> printed <code>State&lt;Int&gt;</code>: the wrapper behind the property.",
         "Thinking it stores data permanently.", "Most pick A.", None),
        ("db", "Question", "Does @State persist across app termination?",
         "Does <code>@State</code> automatically persist across app termination?", "No",
         "It lives in SwiftUI&rsquo;s in-memory storage for the view&rsquo;s identity; persistence is a later unit.",
         "Confusing &ldquo;survives updates&rdquo; with &ldquo;saved&rdquo;.", "Some say yes.", None),
        ("layers", "Question", "Can a view struct be recreated while its @State survives?",
         "Can a view struct be recreated while its <code>@State</code> survives?", "Yes",
         "Two new Survivor values were created; both saw balance 28000.",
         "Thinking the state lives inside the struct.", "Some say no.", None),
        ("frame", "Choose one", "What can happen when a view's identity changes?",
         "What can happen when a view&rsquo;s identity changes?<br>A. Its local state may reset<br>B. The entire iOS process must restart", "A",
         "Replace Identity took the counter from 3 back to 0.",
         "Expecting state to follow the struct&rsquo;s type.", "Most pick A.", None),
        ("link", "Choose one", "What does $balance provide for @State?",
         "What does <code>$balance</code> provide for an <code>@State</code> property?<br>A. A <code>Binding&lt;Int&gt;</code><br>B. A second, independent <code>Int</code><br>C. A database connection", "A",
         "Printed <code>Binding&lt;Int&gt;</code>: read and write access to the same state.",
         "Thinking $ makes a copy.", "Some pick B.", None),
        ("bank", "Question", "Should a production balance change by incrementing local @State?",
         "Should a production payment balance be changed only by incrementing local <code>@State</code>?", "No",
         "The backend owns the real balance; a local <code>+= 1000</code> is not a transaction.",
         "Treating demo state as the source of truth.", "Some say yes.", None),
        ("eye", "Predict the result", "Increment ×3, then Replace Identity: what does the counter show?",
         "The counter shows 3. You tap <b>Replace Identity</b>. What does it show?<br>A. 3<br>B. 0<br>C. 4", "B",
         "A new identity gets new state, starting from its initial value 0.",
         "Expecting the count to carry over.", "Some pick A.", None),
        ("tap", "Question", "From 2.7: does evaluating body run a button's action?",
         "From Lesson 2.7: when the balance change makes <code>body</code> run again, does the button&rsquo;s action run again?", "No",
         "body creates a new closure; only activation runs it.",
         "Mixing up evaluation and activation.", "Some say yes.", "Spaced review from Lesson 2.7.")])

S.append(next_slide('2.8', [("2.9", "@Binding: two-way state communication", "a balance editor that changes the parent&rsquo;s state via <code>$balance</code>"),
                            ("Later", "Networking, ViewModels, persistence", "the real, authoritative balance")],
                    'Next lesson builds a separate NPay balance editor and passes $balance to it, so a child view can modify state owned by its parent without a second copy. The real balance, from a backend through a ViewModel, comes in later units.'))

S.append(lab_slide('2.8', "Make NPay reactive", "Predict each result before you run it.",
                   ["Experiment 1: a plain <code>var</code>; read the error.",
                    "Experiment 2: <code>@State</code>; tap three times.",
                    "Add <code>Self._printChanges()</code>; tap; read the console.",
                    "Integrate: <code>BalanceCard(balance:)</code> and the button.",
                    "Run <code>IdentityExperiment</code>: increment, then replace.",
                    "Breakpoint on <code>balance += 1000</code>; try <code>po balance</code>."],
                   "", 'Expected, as in our runs: "left side of mutating operator isn&rsquo;t mutable: &lsquo;self&rsquo; is immutable"; the balance goes 25,000 → 28,000; _printChanges prints "@self, @identity, _balance changed." then "_balance changed." per tap; the counter goes 3 → 0 on Replace Identity; po balance may or may not evaluate depending on optimisation.',
                   side=f'<div>{card("You hand in", ul("The compiler error and your one-line explanation", "Console output for three taps", "Before/after screenshots of Replace Identity"))}</div>'))

end_slide('2.8', '@State and<br>Reactive UI', 'Lesson 2.9 &mdash; @Binding and Two-Way State Communication',
          'You can now explain why a plain var in a view cannot change, what the @State property wrapper adds, why state survives when the view struct is recreated and resets when identity changes, how a change flows from a tap to the screen, who should own state, what $balance is, and why a real balance does not live in local @State.',
          'Next, Lesson 2.9: @Binding. A separate NPay balance editor changes state owned by its parent, through a binding, without making a copy.')

write_deck(OUT28, '2.8', '@State', '@State')
