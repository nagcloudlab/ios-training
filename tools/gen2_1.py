"""Generates decks/unit-2/lesson-2.1/index.html from the Lesson 2.1 text (Sections 11-30; Part 1 was not shared).
Sections are grouped into 8 Parts. Console logs and screenshots come from a scripted SwiftUI app run in the iOS Simulator."""
import html, os, re, sys
OUT21 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
UNIT_NO, UNIT_TITLE = '02', 'SwiftUI Fundamentals'
UNIT_LESSONS = [('2.1', 'Declarative', 'UI, body'), ('2.2', 'Xcode &amp;', 'previews'), ('2.3', 'Text &amp;', 'modifiers'),
                ('2.4', 'Stacks &amp;', 'layout'), ('2.5', '@State &amp;', '@Binding'), ('2.6', 'Controls', '&amp; forms'),
                ('2.7', 'List &amp;', 'identity'), ('2.8', 'Design', 'system'), ('2.9', 'Access-', 'ibility'), ('2.10', 'Lab:', 'dashboard')]
exec(open(os.path.join(HERE, 'unit1.py')).read())   # shared helpers (unit-aware)
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'
tbl = lambda head_, rows, cls='tbl compact': f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head_) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'
console = lambda label, lines, size=14: card(label, mono('<br>'.join(lines), size))
shot = lambda src_, cap, h=330: f'<div><div class="shot" style="height:{h}px"><img src="{src_}" alt="{cap}"></div><p class="shot-cap">{cap}</p></div>'

title_slide('2.1', 'Inside SwiftUI:<br>State, Identity &amp; Rendering',
            'When NPay&rsquo;s balance changes, how does SwiftUI update the screen <b>without rebuilding everything</b>?',
            'Unit 02 begins: SwiftUI. Today we look inside it. Views are descriptions, not pixels; so when NPay&rsquo;s balance changes from ₹25,000 to ₹30,000, how does SwiftUI update the interface without rebuilding everything? Everything you will see logged or on a phone screen today came from a small SwiftUI app we ran in the iOS Simulator.')
outcomes_slide('2.1', [("diff", "What happens when a <b>description changes</b>"),
                       ("eye", "Why and when <code>body</code> <b>runs again</b>"),
                       ("link", "How <b>identity</b> keeps or resets state"),
                       ("layers", "<code>@State</code>, <code>@Binding</code> and <code>@Observable</code>: who owns state"),
                       ("frame", "From description to <b>pixels</b>, and what costs time"),
                       ("check", "Debug it: <code>_printChanges()</code>, identity, Instruments")])
where_slide('2.1', 'Today: how SwiftUI thinks', (),
            'Unit 01 (1.10): NPay&rsquo;s engine in plain Swift, tested on any computer.',
            'The SwiftUI layer on top: descriptions, state, identity and rendering.',
            'Unit 01 gave us the language and NPay&rsquo;s domain engine. Unit 02 builds the interface on a Mac with Xcode. We start with how SwiftUI works inside, because every later lesson relies on it.',
            'One reminder from Unit 01 first.')

# authored bridge: views are descriptions
DESC = """struct DashboardView: View {       // 1.5
    var body: some View {          // 1.6
        VStack {
            Text("NPay")
            Text("₹25,000")
            Button("Send Money") { }
        }
    }
}"""
S.append(slide("Lesson 2.1 &middot; Starting point (authored)", "A view is a description, not pixels", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:center">
      {code("DashboardView.swift", DESC, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("What you write", ul("A <b>value</b> saying what should appear", "Cheap to create, often recreated"))}
        {card("What SwiftUI does", ul("Keeps <b>state</b> and <b>identity</b>", "Works out the <b>smallest</b> update", "Lays out and renders"))}
      </div>
    </div>
  </div>""", notes(('SAY', 'The lesson text picks up from a part we did not receive, so here is the starting point, from Unit 01. A SwiftUI view is a struct, a value, as in Lesson 1.5, and body returns some View, one hidden concrete type, as in Lesson 1.6. It describes what should appear; it is not the pixels.'),
                  ('SAY', 'You write the description. SwiftUI keeps the state and identity, works out what actually changed, and does layout and rendering. Today is about that second column.'),
                  ('CONNECT', 'So what happens when the description changes?'))))

# ================================================================== Part 1 (11)
divider(1, "Reconciliation", "Only what changed", 'The balance goes from ₹25,000 to ₹30,000. Everything else stays the same.', 'Compare the descriptions.')
P = ['<text class="mono" x="0" y="14">PREVIOUS DESCRIPTION</text>', '<text class="mono" x="596" y="14">NEW DESCRIPTION</text>']
for i, (a, b) in enumerate([('NPay', 'NPay'), ('₹25,000', '₹30,000'), ('Send Money', 'Send Money')]):
    y = 28 + i * 64
    P.append(box(0, y, 540, 52, a, '', None, '', ''))
    P.append(box(596, y, 540, 52, b, 'changed' if i == 1 else 'same', '1+' if i == 1 else None, '', ''))
STEPS = ["The balance <b>state</b> changes", "SwiftUI finds the <b>dependencies</b> on it", "Relevant descriptions may be <b>re-evaluated</b>",
         "It decides what managed UI needs <b>updating</b>", "<b>Layout</b>, graphics and presentation run as needed"]
S.append(slide("Part 1 &middot; Reconciliation (section 11) &middot; conceptual", "Same screen, one value different", f"""  <div class="body">
    {svg('0 0 1136 220', 'Previous and new descriptions: NPay and Send Money are the same; the balance changed from 25,000 to 30,000 rupees', 'recon', P, 'max-height:230px')}
    {cues(1)}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:start">
      <ol class="lab step" style="font-size:18px">{''.join(f'<li>{x}</li>' for x in STEPS)}</ol>
      <div class="warn step" data-label="Not a virtual DOM">{ul("No public, fixed tree-diff algorithm", "Dependency tracking and identity, largely private")}</div>
    </div>
  </div>""", notes(('SAY', 'NPay&rsquo;s dashboard: a heading, the balance and a Send Money button. A transaction completes and the balance becomes ₹30,000. Click: in the new description only the balance differs.'),
                  ('SAY', 'Click: conceptually, the balance state changes; SwiftUI identifies what depends on it; those descriptions may be re-evaluated; it works out which managed UI needs updating; then layout, graphics and presentation happen as required. Like a restaurant&rsquo;s order display: when one order goes from Preparing to Ready, nobody rebuilds the kitchen; the display updates that line.'),
                  ('SAY', 'Click: do not teach this as React&rsquo;s virtual DOM diff. SwiftUI does not publish a fixed tree-comparison algorithm; its dependency tracking, identity and update mechanisms are more sophisticated and mostly private. Our evidence next comes from logging, not from reading its internals.'),
                  ('CONNECT', 'So when exactly does body run again? We measured it.'))))

# ================================================================== Part 2 (12-13)
divider(2, "When body runs again", "Evaluation is not rendering", 'Put a print in body and watch.', 'A real run.')
BODY = """struct DashboardView: View {
    @State private var balanceMinor: Int64 = 2_500_000
    var body: some View {
        let _ = print("DashboardView body evaluated, balance \\(balanceMinor / 100)")
        VStack {
            HeaderView()          // reads nothing
            Text("₹\\(balanceMinor / 100)")
        }
    }
}
struct HeaderView: View {
    var body: some View {
        let _ = print("HeaderView body evaluated")
        Text("NPay").font(.largeTitle)
    }
}"""
OPS = [("View initialization", "a Swift value is built"), ("<code>body</code> evaluation", "a new description is computed"), ("Rendering", "pixels are prepared and shown")]
S.append(slide("Part 2 &middot; body evaluation (section 12)", "The balance changed twice; the header didn&rsquo;t care", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {code("DashboardView.swift", BODY, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("iOS Simulator console (balance +₹1,000 twice)", ["DashboardView body evaluated, balance 25000", "HeaderView body evaluated", "DashboardView body evaluated, balance 26000", "DashboardView body evaluated, balance 27000"], 13)}</div>
        <div class="step">{tbl(["Operation", "Means"], OPS)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A dashboard with a print in body, and a HeaderView that depends on nothing. We ran it in the iOS Simulator and changed the balance twice, the way a button would.'),
                  ('SAY', 'Click: the real console. The dashboard&rsquo;s body ran three times: once at first, then after each change. The header&rsquo;s body ran once. SwiftUI only re-evaluated what depended on the balance. The prints are for teaching and debugging; never build app logic on how often body runs.'),
                  ('SAY', 'Click: keep three operations apart. Initializing a view struct builds a value. Evaluating body computes a new description. Rendering prepares and presents pixels. If body runs ten times, the GPU does not necessarily draw the whole screen ten times.'),
                  ('CONNECT', 'That is also why views are structs.'))))

CARD = """struct BalanceCard: View {
    let title: String
    let balanceText: String     // from the ViewModel

    var body: some View {
        VStack(alignment: .leading) {
            Text(title)
            Text(balanceText).font(.largeTitle)
        }
    }
}"""
S.append(slide("Part 2 &middot; Views are structs (section 13)", "Cheap values, recreated freely", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:center">
      {code("BalanceCard.swift", CARD, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("A struct (1.5)", ul("Value semantics: a <b>configuration</b>", "Not a permanent on-screen object"))}
        {card("SwiftUI owns the rest", ul("State, identity, rendering"))}
        <div class="rule step" data-label="So">{ul("No expensive work or <b>side effects</b> in <code>body</code>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Structs have value semantics, which suits describing a UI configuration. BalanceCard says: a title and a balance, in a vertical stack. It takes balanceText already formatted, as the ViewModel does in NPay.'),
                  ('SAY', 'A view struct is not a permanent object that represents one element on screen. SwiftUI may recreate view values constantly as part of normal updates; the state, identity and rendering infrastructure live in SwiftUI.'),
                  ('SAY', 'Click: so keep body pure: no expensive work, no side effects like network calls. Part 6 comes back to this.'),
                  ('CONNECT', 'If structs come and go, how does state survive? Identity.'))))

# ================================================================== Part 3 (14-15)
divider(3, "View identity", "How state finds its view", 'One of the deepest SwiftUI ideas: state belongs to a view&rsquo;s identity.', 'Swap two branches.')
ID = """struct NPayScreen: View {
    @State private var showPremium = false

    var body: some View {
        VStack {
            Toggle("Premium Mode", isOn: $showPremium)
            if showPremium {
                CounterView(name: "Premium")  // own @State
            } else {
                CounterView(name: "Standard")
            }
        }
    }
}"""
P = [box(0, 0, 250, 52, 'Standard branch', 'counts to 3', '1', '', 'layers'), wire('M254 26H286' + head(286, 26, 'r'), '2'),
     box(292, 0, 250, 52, 'Premium branch', 'new identity: 0', '2', '', 'layers'), wire('M546 26H578' + head(578, 26, 'r'), '3+'),
     box(584, 0, 260, 52, 'Standard again', 'fresh state: 0', '3+', '', 'layers')]
S.append(slide("Part 3 &middot; Structural identity (section 14)", "Switch branches, lose the state", f"""  <div class="body">
    {cues(3)}
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:24px;align-items:start">
      {code("NPayScreen.swift", ID, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {svg('0 0 844 52', 'Standard counts to 3; switch to Premium, which starts at 0; switch back, Standard starts at 0 again', 'idsw', P, 'max-height:60px')}
        <div class="step">{console("iOS Simulator console", ["StandardCounterView appeared, count = 0", "Standard counted to 3", "PremiumCounterView appeared, count = 0", "Premium counted to 3", "StandardCounterView appeared, count = 0"], 13)}</div>
        <div class="tip step" data-label="View identity">{ul("Not object identity: <b>position and structure</b> in the hierarchy")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A Premium Mode toggle chooses between two branches, each a counter with its own @State count. SwiftUI uses view identity to attach state to the right part of the hierarchy, and a branch is a different position in the structure.'),
                  ('SAY', 'Click through: the standard counter counts to 3. Click: switch to premium; it is a different identity, so it starts at 0. Click: switch back; the standard counter is new again, at 0. Its count of 3 was discarded when its branch was removed.'),
                  ('SAY', 'Click: the real console from the simulator confirms it: Standard appeared at 0 and counted to 3; Premium appeared at 0; Standard appeared again at 0.'),
                  ('SAY', 'Click: view identity is not object identity from Lesson 1.5. It is how SwiftUI associates state and updates with a view&rsquo;s position and structure. Lists and navigation, later in this unit, depend on stable identity.'),
                  ('CONNECT', 'You can also set identity explicitly.'))))

EXP = """BalanceCard(title: "Savings", balanceText: text)
    .id(accountId)      // a new account → a new identity"""
S.append(slide("Part 3 &middot; Explicit identity (section 15)", ".id() resets state, on purpose", f"""  <div class="body">
    {code("ExplicitIdentity.swift", EXP, "font-size:17px")}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:repeat(3,1fr);gap:18px;align-items:stretch">
      {card("What it does", ul("A changed <code>id</code> = a different view", "Its <code>@State</code> starts fresh"))}
      {card("Good use", ul("Switch account A &rarr; B", "Reset account-specific temporary state"), 'step')}
      <div class="warn step" data-label="Use deliberately">{ul("Not a fix for update bugs", "Destroys state, adds work (Part 8)")}</div>
    </div>
  </div>""", notes(('SAY', 'Besides structural identity, SwiftUI supports explicit identity with .id(). If accountId changes, SwiftUI treats this as a different view, and its state resets.'),
                  ('SAY', 'Click: that is useful when switching from account A to account B should reset temporary, account-specific state, such as a half-typed note.'),
                  ('SAY', 'Click: but .id() is not a universal fix for UI update problems. Used carelessly it destroys useful state and adds work. Part 8 shows the classic mistake, measured.'),
                  ('CONNECT', 'Next question: where should state live?'))))

# ================================================================== Part 4 (16-17)
divider(4, "Who owns state", "Lift it; bind to it", 'The dashboard and the transaction history both need the selected account.', 'One owner.')
OWN = """struct AccountScreen: View {
    @State private var balanceMinor: Int64 = 2_500_000   // the owner

    var body: some View {
        BalanceEditor(balanceMinor: $balanceMinor)         // pass a binding
    }
}

struct BalanceEditor: View {
    @Binding var balanceMinor: Int64                       // reads and writes it

    var body: some View {
        Button("Add Demo ₹1,000") { balanceMinor += 100_000 }
    }
}"""
P = [box(70, 0, 320, 56, 'Shared owner', 'selected account', None, 'lit', 'user'),
     wire('M170 60L110 96' + head(110, 96, 'd')), wire('M290 60L350 96' + head(350, 96, 'd')),
     box(0, 102, 220, 52, 'DashboardView', 'reads it', None, '', 'phone'), box(240, 102, 220, 52, 'TransactionsView', 'reads it', None, '', 'file')]
S.append(slide("Part 4 &middot; Ownership (sections 16&ndash;17)", "One owner; children get a binding", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:24px;align-items:start">
      <div>{svg('0 0 460 154', 'A shared owner holds the selected account; DashboardView and TransactionsView both read it', 'own', P, 'max-height:170px')}
        <div class="gap"></div>
        {card("Lift shared state", ul("Owned at the <b>lowest common</b> level", "No inconsistent copies"))}</div>
      <div class="step">{code("Binding.swift", OWN, "font-size:12.5px")}
        <div style="margin-top:12px">{card("@Binding", ul("Not a copy: access to state <b>owned elsewhere</b>", "<code>$balanceMinor</code> creates it"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'The dashboard and the transaction history both need the selected account. If each kept its own copy, they could disagree. So shared state is lifted to an appropriate common owner, and both screens read it from there.'),
                  ('SAY', 'Click: @State marks the owner. AccountScreen owns the balance, in paise as always. BalanceEditor needs to change it, so it receives a binding: dollar balanceMinor. Inside, @Binding reads and writes the parent&rsquo;s state.'),
                  ('SAY', 'A binding is not a second, independent copy; it is access to state owned elsewhere. When the editor adds ₹1,000, the parent&rsquo;s value changes. Lesson 2.5 goes deeper into sources of truth.'),
                  ('CONNECT', 'For app-level state, use a model object.'))))

# ================================================================== Part 5 (18-19)
divider(5, "@Observable and the main actor", "Reference state for real screens", 'Bigger state lives in a model. Unit 01 gave it its shape.', 'DashboardViewModel.')
VM = """import Observation

@MainActor @Observable
final class DashboardViewModel {
    var balanceMinor: Int64 = 2_500_000
    var isLoading = false

    var balanceText: String {
        let rupees = Decimal(balanceMinor) / 100
        return rupees.formatted(.currency(code: "INR"))
    }
    func refresh() async {
        isLoading = true
        defer { isLoading = false }
        // await the BalanceService (1.9)
    }
}"""
VIEW = """struct DashboardView: View {
    @State private var model = DashboardViewModel()

    var body: some View {
        VStack {
            Text(model.balanceText)
            Button("Refresh balance") {
                Task { await model.refresh() }
            }
        }
    }
}"""
S.append(slide("Part 5 &middot; Observation (sections 18&ndash;19)", "An observable model, isolated to the main actor", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DashboardViewModel.swift", VM, "font-size:12px")}
      <div>{code("DashboardView.swift", VIEW, "font-size:12px")}
        <div class="gap"></div>
        <div class="cols tight step" style="gap:12px">{card("@Observable", ul("Updates views that <b>read</b> it", "<b>Not</b> thread-safe"))}{card("@MainActor", ul("UI state, main actor", "<code>await</code> frees it"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'For more complex state, NPay uses an observable model: the DashboardViewModel from Unit 00 and 1.9. @Observable lets SwiftUI track which properties a view reads, and update that view when they change. The view owns the model with @State, so the model lives as long as the view&rsquo;s identity.'),
                  ('SAY', 'The model holds paise and formats balanceText, the canon from Lesson 0.2. The button calls refresh in a task.'),
                  ('SAY', 'Click: two distinctions. @Observable makes a type observable; it does not make its mutable state thread-safe. That is why it is also @MainActor, which isolates UI-facing state to the main actor. And @MainActor does not mean blocking the main thread: at an await the main actor processes other work, though CPU-heavy synchronous work on it still freezes the UI, as Lesson 1.9 measured.'),
                  ('CONNECT', 'Finally: how do descriptions become pixels?'))))

# ================================================================== Part 6 (20-21)
divider(6, "Rendering and performance", "From description to frame", 'SwiftUI describes and lays out; Apple&rsquo;s graphics stack draws.', 'The pipeline, and what slows it.')
PIPE = [("SwiftUI view descriptions", "what should be displayed", "code"), ("Dependencies and identity", "what may need updating", "link"),
        ("Layout", "where content belongs", "layout"), ("Graphics and compositing", "prepare and combine content", "layers"), ("Display", "a visible frame", "phone")]
P = []
for i, (t, sub, ic) in enumerate(PIPE):
    P.append(box(i * 228, 0, 212, 64, t, sub, str(i + 1) if i < 4 else '5+', '', ic))
    if i < 4:
        P.append(wire(f'M{i * 228 + 214} 32H{i * 228 + 226}' + head(i * 228 + 226, 32, 'r')))
S.append(slide("Part 6 &middot; Rendering (section 20) &middot; conceptual", "Five stages to a visible frame", f"""  <div class="body">
    {svg('0 0 1124 64', 'View descriptions, dependencies and identity, layout, graphics and compositing, display', 'pipe', P, 'max-height:80px')}
    {cues(5)}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {card("Three different costs", ul("Computing <b>descriptions</b>", "<b>Layout</b>", "<b>Rendering</b> and presenting frames"))}
      <div class="rule step" data-label="Avoid teaching">{ul("&ldquo;Every SwiftUI view is a <code>CALayer</code>&rdquo;", "The rendering representation is an implementation detail")}</div>
    </div>
  </div>""", notes(('SAY', 'Click through a conceptual pipeline: SwiftUI view descriptions say what should appear; dependency and identity management decide what may need updating; layout decides where things go; Apple&rsquo;s graphics and compositing infrastructure prepares and combines the content; and a visible frame reaches the display, the frame from Lesson 0.5.'),
                  ('SAY', 'It is conceptual: SwiftUI&rsquo;s private rendering implementation, and the exact role of technologies like Core Animation, can change between OS releases. Each stage can be a separate bottleneck: computing descriptions, layout, and rendering.'),
                  ('SAY', 'Click: so avoid teaching that every SwiftUI view is a CALayer. SwiftUI manages its own abstractions.'),
                  ('CONNECT', 'The cost you control most directly is body.'))))

BAD = """var body: some View {
    let result = expensiveCalculation()  // each time
    return Text("\\(result)")
}"""
GOOD = """@State private var result = 0

var body: some View {
    Text("\\(result)")
        .task {                        // once, owned
            result = await calculator.run()
        }
}"""
S.append(slide("Part 6 &middot; Performance (section 21)", "Keep body cheap; do work elsewhere", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Risky.swift", BAD, "font-size:15px")}
        <div style="margin-top:12px">{card("Risky", ul("<code>body</code> may run many times (Part 2)", "Synchronous work here costs every time"))}</div></div>
      <div class="step">{code("Better.swift", GOOD, "font-size:15px")}
        <div style="margin-top:12px">{card("Better", ul("Work in a service or <code>.task</code>", "The result becomes <b>state</b>", "Networking: <b>never</b> as a side effect of <code>body</code>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Because SwiftUI may re-evaluate body many times, as Part 2 showed, a substantial synchronous calculation inside body is paid on every evaluation, and it harms responsiveness.'),
                  ('SAY', 'Click: move the work into a service or an asynchronous operation and expose the result as state. Here .task runs it with the view&rsquo;s lifetime, as in Lesson 1.9. calculator stands for whatever service does the work.'),
                  ('SAY', 'Should a network request start as a side effect of evaluating body? No. body describes the interface; use .task, actions and properly owned models for side effects.'),
                  ('CONNECT', 'Put the pieces together: NPay&rsquo;s first real dashboard.'))))

# ================================================================== Part 7 (22)
divider(7, "NPay&rsquo;s first dashboard", "A real screen in the simulator", 'Composition, formatting, state, a conditional view, modifiers and layout, in one screen.', 'Run it.')
DASH = """struct DashboardView: View {
    @State private var balanceMinor: Int64 = 2_500_000
    @State private var showMessage = false

    var body: some View {
        VStack(spacing: 24) {
            Text("NPay").font(.largeTitle.bold())
            Text("Available Balance").foregroundStyle(.secondary)
            Text(Decimal(balanceMinor) / 100,
                 format: .currency(code: "INR")
                     .precision(.fractionLength(0)))
                .font(.system(size: 38, weight: .bold))
            Button("Add Demo ₹1,000") {
                balanceMinor += 100_000
                showMessage = true
            }
            .buttonStyle(.borderedProminent)
            if showMessage {
                Text("Demo balance updated").foregroundStyle(.green)
            }
            Spacer()
        }
        .padding()
    }
}"""
S.append(slide("Part 7 &middot; Dashboard (section 22)", "Before and after one tap", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.375fr) minmax(0,.375fr);gap:20px;align-items:start">
      {code("DashboardView.swift", DASH, "font-size:11.5px")}
      {shot("img/dash.png", "Launch")}
      <div class="step">{shot("img/tapped.png", "After one tap")}</div>
    </div>
  </div>""", notes(('SAY', 'NPay&rsquo;s first dashboard, a demonstration screen, not a real wallet. A vertical stack with the title, a label, the balance formatted as Indian rupees from paise, a button, a message that appears only after a tap, and a spacer pushing everything up.'),
                  ('SAY', 'These are real iOS Simulator screenshots. At launch: ₹25,000, with grouping and the rupee sign from the currency format. Click: after one tap the balance is ₹26,000 and the conditional message appears.'),
                  ('SAY', 'It previews almost every topic of this unit: composition, text formatting, state changes, conditional views, modifiers, layout, and Xcode previews, which is Lesson 2.2.'),
                  ('LIVE DEMO', 'In Xcode: File, New, Project, iOS App. Paste DashboardView into ContentView.swift, rename, add #Preview { DashboardView() }, and run on an iPhone simulator. Tap the button; then add let _ = Self._printChanges() to body and watch the console.'),
                  ('CONNECT', 'When this misbehaves, how do you debug it?'))))

# ================================================================== Part 8 (24-28)
divider(8, "Debugging SwiftUI", "Measure before you optimize", '&ldquo;My dashboard&rsquo;s body runs repeatedly. SwiftUI must be inefficient!&rdquo; Is it?', 'Ask SwiftUI.')
PC = """struct DashboardView: View {
    @State private var count = 0

    var body: some View {
        let _ = Self._printChanges()
        Text("Count: \\(count)")
    }
}"""
INV = ["Which state or observable property <b>changed</b>?", "Which views <b>depend</b> on it?", "Is the view&rsquo;s <b>identity stable</b>?",
       "Is expensive work happening <b>in body</b>?", "Is a side effect <b>repeatedly changing</b> state?"]
S.append(slide("Part 8 &middot; _printChanges (section 24)", "Ask SwiftUI why body ran", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Debug.swift", PC, "font-size:14px")}
        <div class="step" style="margin-top:12px">{console("iOS Simulator console (count +1 twice)", ["DashboardView: @self, @identity, _count changed.", "DashboardView: _count changed.", "DashboardView: _count changed."], 13)}</div></div>
      <div>{card("Investigate", '<ol class="lab" style="font-size:17px;margin-top:6px">' + ''.join(f'<li>{x}</li>' for x in INV) + '</ol>')}
        <div class="gap"></div>
        <div class="tip step" data-label="Debugging only">{ul("<code>_printChanges()</code> is a diagnostic, not app logic")}</div></div>
    </div>
  </div>""", notes(('SAY', 'body running repeatedly is not proof that SwiftUI is inefficient: re-evaluation is how dependency updates work. The useful question is whether unnecessary expensive work is happening.'),
                  ('SAY', 'Self._printChanges() is a SwiftUI debugging facility that prints why body was evaluated. Click: the real console. First evaluation: @self, @identity and _count, because everything is new. Then, after each increment: _count changed. Exactly the state we expected.'),
                  ('SAY', 'Investigate in order: which state changed, which views depend on it, whether identity is stable, whether body does expensive work, and whether a side effect keeps changing state. Measure and find the cause before optimizing.'),
                  ('SAY', 'Click: _printChanges is a diagnostic. Never build app logic on it.'),
                  ('CONNECT', 'The most common identity bug, measured.'))))

UU = """BalanceCard()
    .id(UUID())     // new every time"""
ST = """BalanceCard()
    .id(accountId)  // stable"""
S.append(slide("Part 8 &middot; Identity bugs (section 25)", "A random id throws state away every time", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Unstable.swift", UU, "font-size:15px")}
        <div class="step" style="margin-top:12px">{console("Parent updates 3 times", ["BalanceCard appeared: fresh state #1", "BalanceCard appeared: fresh state #2", "BalanceCard appeared: fresh state #3", "BalanceCard appeared: fresh state #4"], 13)}</div></div>
      <div>{code("Stable.swift", ST, "font-size:15px")}
        <div class="step" style="margin-top:12px">{console("Parent updates 3 times", ["BalanceCard appeared: fresh state #1"], 13)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label=".id() everywhere?">{ul("No: structural identity is the default", "Explicit identity only for a reason")}</div></div>
    </div>
  </div>""", notes(('SAY', 'A common mistake: giving a view .id(UUID()). Every evaluation of the parent creates a new UUID, so SwiftUI sees a brand-new view each time.'),
                  ('SAY', 'Click: we measured it. The parent updated three times; the card appeared four times, each with fresh state, numbers one to four. Any state inside it would reset on every update, and SwiftUI did extra work each time.'),
                  ('SAY', 'Click: with a stable id, accountId, the same three updates: one appearance, state kept. Use that only when changing accounts should deliberately reset the card.'),
                  ('SAY', 'Click: should you add .id() to every view? No. SwiftUI already uses structural identity; explicit identity is for specific cases.'),
                  ('CONNECT', 'Two more debugging angles: the main thread and Instruments.'))))

CALC = """Button("Calculate") {
    result = expensiveCalculation()  // main actor
}"""
TOOLS = [("Time Profiler", "CPU-heavy call paths"), ("Animation / hitches", "frame timing and rendering"), ("Allocations, Memory Graph", "growth and retention (1.8)")]
S.append(slide("Part 8 &middot; Main thread and Instruments (sections 26&ndash;27)", "Find what blocks the main thread", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Calculate.swift", CALC, "font-size:15px")}
        <div style="margin-top:12px">{card("Several seconds on the main actor", ul("No event handling, no new frames: the UI <b>freezes</b> (0.5)", "<code>async</code> alone doesn&rsquo;t move CPU work off it (1.9)"))}</div></div>
      <div class="step">{tbl(["Instrument", "Finds"], TOOLS, 'tbl')}
        <p class="small muted" style="margin:8px 0 0">Available instruments vary with the Xcode version.</p>
        <div class="gap"></div>
        {card("Separate the three costs", ul("Descriptions, layout, rendering (Part 6)"))}</div>
    </div>
  </div>""", notes(('SAY', 'A Calculate button that runs a several-second calculation directly in its action. Actions run on the main actor, so for those seconds the main thread cannot handle events or produce frames, and the UI freezes, exactly the run loop story from Lesson 0.5. And as Lesson 1.9 measured, adding async to a function does not by itself move CPU work off the main actor; you must know where the work runs.'),
                  ('SAY', 'Click: Xcode&rsquo;s Instruments helps: Time Profiler for CPU-heavy call paths; animation and hitch tools for frame timing; Allocations and the Memory Graph for growth and retention from Lesson 1.8. The exact set depends on the Xcode version.'),
                  ('SAY', 'Always separate the three costs from Part 6: computing descriptions, layout, and rendering. They have different bottlenecks. Lessons 3.9 and 8.7 go deep.'),
                  ('CONNECT', 'Finally, trace one tap all the way to the screen.'))))

TR = [("tap", "User taps the button", "the system delivers the event; SwiftUI runs the action"),
      ("diff", "State changes", "balanceMinor += 100_000"),
      ("link", "Dependencies invalidated", "views that read it are marked"),
      ("code", "body re-evaluated", "a new description"),
      ("layout", "UI updates", "only what changed; layout as needed"),
      ("phone", "Visible frame", "₹26,000 on screen")]
P = []
for i, (ic, t, sub) in enumerate(TR):
    P.append(box(0, i * 52, 640, 44, t, sub, str(i + 1) if i < 5 else '6+', '', ic))
S.append(slide("Part 8 &middot; Trace a tap (sections 28, 30) &middot; conceptual", "From a tap to a pixel", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:center">
      {svg('0 0 640 304', 'Tap, state change, dependencies invalidated, body re-evaluated, UI updates, visible frame', 'trace', P, 'max-height:420px')}
      {shot("img/tapped.png", "Step 6: the new frame", 320)}
    </div>
  </div>""", notes(('SAY', 'Trace one tap on the dashboard. Click: the system delivers the touch and SwiftUI runs the button action. Click: the action mutates state. Click: SwiftUI invalidates the views that read that state. Click: their body is re-evaluated into a new description. Click: only the necessary UI is updated, with layout as needed. Click: a visible frame reaches the screen: ₹26,000.'),
                  ('SAY', 'Event, state mutation, dependency invalidation, view re-evaluation, required UI updates, visible frame. That is a conceptual pipeline, not a claim about the private order of every internal step, and it answers today&rsquo;s question: how a change in Swift state becomes an updated pixel on the iPhone.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('2.1', (), [("code", "Views describe", "body is cheap and may run often"),
                     ("link", "Identity keeps state", "change it and state resets"),
                     ("layers", "One owner per state", "@State, @Binding, @Observable")],
         'Three things to remember. Views are cheap descriptions: body may run often, only for views whose dependencies changed, and evaluation is not rendering. Identity keeps state attached: switch a branch or change an id and the state starts fresh. And every piece of state has one owner: @State for view state, @Binding to share it, an @Observable, @MainActor model for app state.')

review_divider(8)
review([("phone", "Question", "Is a SwiftUI View struct the same as a UIKit UIView?",
         "Is a SwiftUI <code>View</code> struct the same thing as a UIKit <code>UIView</code> object?", "No",
         "A View is a cheap description value, recreated often; SwiftUI keeps the state, identity and rendering.",
         "Treating view structs as long-lived objects.", "UIKit developers may say yes.", None),
        ("eye", "Choose one", "When the balance changes, which body runs again?",
         "The balance changes. Which bodies re-run?<br>A. Every view on the screen<br>B. Views that depend on the balance<br>C. Only <code>HeaderView</code><br>D. None; only rendering runs", "B",
         "Measured: <code>DashboardView</code> re-ran after each change; <code>HeaderView</code>, which reads nothing, ran once.",
         "Assuming the whole tree is rebuilt.", "Some pick A.", None),
        ("link", "Choose one", "Why doesn't @State disappear when the View struct is recreated?",
         "Why doesn&rsquo;t <code>@State</code> disappear when the view struct is recreated?<br>A. Structs are reference types<br>B. SwiftUI stores it, tied to the view&rsquo;s identity<br>C. It is saved to disk<br>D. It does disappear", "B",
         "The struct is a description; the state lives in SwiftUI&rsquo;s storage for that identity, until the identity changes.",
         "Thinking the state lives in the struct.", "Some pick D.", None),
        ("globe", "Choose one", "Where should a balance fetch start?",
         "Where should a network fetch of the balance start?<br>A. Inside <code>body</code><br>B. In <code>.task</code> or a button action, via the model<br>C. In the view&rsquo;s <code>init</code><br>D. In a computed property", "B",
         "<code>body</code> must stay a pure description; side effects belong to lifecycle-aware places and owned models.",
         "Starting work wherever the data is needed.", "Some pick A.", None),
        ("shield", "Question", "Does @Observable make a ViewModel thread-safe?",
         "Does <code>@Observable</code> make a ViewModel thread-safe?", "No",
         "It makes it observable. Isolation, often <code>@MainActor</code>, protects its state.",
         "Confusing observation with synchronization.", "Some say yes.", None),
        ("layers", "Predict the output", "Standard counts to 3; toggle to Premium and back. What is Standard's count?",
         "The Standard counter counts to 3. Toggle to Premium, then back. What does Standard show?", "0",
         "Removing the branch discarded its state; coming back is a new identity. The simulator log showed count = 0.",
         "Expecting the count to be remembered.", "Many say 3.", None),
        ("diff", "Predict the output", "With .id(UUID()), how many fresh states after 3 parent updates?",
         "A <code>BalanceCard</code> has <code>.id(UUID())</code>. The parent updates 3 times. How many times does it start with fresh state?", "4",
         "Once at first, then once per update: each evaluation is a new identity. With a stable id: once.",
         "Thinking a UUID is a stable identity.", "Most say 1.", None),
        ("clock", "Choose one", "In a @MainActor ViewModel, what does await fetchBalance() do to the main thread?",
         "In a <code>@MainActor</code> ViewModel, <code>await service.fetchBalance()</code>:<br>A. Blocks the main thread until it returns<br>B. Suspends; the main thread keeps handling events<br>C. Moves the ViewModel to a background thread<br>D. Crashes", "B",
         "At an <code>await</code> the main actor is free (1.9). Only synchronous heavy work blocks it.",
         "Equating MainActor with blocking.", "Some pick A.", "Spaced review from Lesson 1.9.")])

S.append(next_slide('2.1', [("2.2", "Xcode projects, simulator &amp; previews", "running today&rsquo;s dashboard yourself"),
                            ("2.4", "Stacks, layout &amp; geometry", "the layout stage, in depth"),
                            ("2.5", "@State, @Binding &amp; source of truth", "ownership, in depth"),
                            ("3.1", "View identity, lifetime &amp; state reset", "identity, in depth"),
                            ("3.2", "Observation: @Observable &amp; @Bindable", "observable models"),
                            ("3.9", "SwiftUI rendering performance", "measuring body, layout and rendering")],
                    'Today was the mental model. 2.2 sets up Xcode, the simulator and previews so you can run all of this; 2.4 and 2.5 go deep into layout and state ownership; and Unit 03 returns to identity, observation and rendering performance with real measurements.'))

LAB = """struct HeaderView: View {
    var body: some View {
        let _ = print("HeaderView body evaluated")
        Text("NPay").font(.largeTitle)
    }
}
// 1. DashboardView from Part 7 + Self._printChanges()
// 2. Toggle between two CounterViews: watch the count
// 3. .id(UUID()) vs .id("NP1001"): count appearances"""
S.append(lab_slide('2.1', "Make SwiftUI explain itself", "Reproduce today&rsquo;s evidence in your own simulator.",
                   ["Build the Part 7 dashboard; tap; compare with the screenshots.",
                    "Add prints and <code>_printChanges()</code>; tap twice; read the console.",
                    "Add <code>HeaderView</code>: how often does its body run?",
                    "Toggle two counters; then try <code>.id(UUID())</code> vs a stable id."],
                   "", 'Needs a Mac with Xcode: File > New > Project > iOS App (Lesson 2.2 covers Xcode properly). Expected, as in our simulator runs: the dashboard body runs on every balance change, HeaderView once; _printChanges prints "@self, @identity, _count changed." then "_count changed."; switching branches resets the counter to 0; .id(UUID()) gives a fresh state on every parent update, a stable id only once. Ask students to explain each result with the words description, dependency and identity.',
                   side=f'<div>{code("Lab.swift", LAB, "font-size:13px")}<div class="gap"></div>{card("You hand in", ul("Your console logs, each with a one-line explanation"))}</div>'))

end_slide('2.1', 'Inside SwiftUI:<br>State, Identity &amp; Rendering', 'Lesson 2.2 &mdash; Xcode Projects, Simulator &amp; Previews',
          'You can now explain why SwiftUI is declarative, why body can be re-evaluated and how that differs from rendering, how identity keeps or resets state, who owns state with @State, @Binding and @Observable, how a tap becomes a pixel, and how to debug it.',
          'Next, Lesson 2.2: Xcode projects, the simulator and previews: creating the NPay project and exploring targets, schemes, @main, WindowGroup, previews and the build.')

write_deck(OUT21, '2.1', 'Inside SwiftUI', 'Inside SwiftUI')
