"""Generates decks/unit-4/lesson-4.3/index.html from the Lesson 4.3 text (Swift Observation Framework Internals; two
parts, Sections 1-24, Part 2 restarting at Section 16). Evidence: the compiler's real @Observable expansion (CounterModel,
@ObservationIgnored, NPay's PaymentViewModel), Swift 6 concurrency diagnostics, and tools/sim4_3 (plain vs observable
counter, _printChanges for the section 13 and 22 labs, an ObservableObject comparison, body counts for computed,
nested and ignored properties, a ViewModel created inside body)."""
import html, os, re, sys
OUT43 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.3', 'Swift Observation<br>Framework Internals',
            'How does SwiftUI know <b>which property changed</b>, which view read it, and what to update?',
            'In Lesson 4.2 we marked PaymentViewModel @Observable and SwiftUI simply responded when the user typed. Today we open that up: what the macro generates, how property reads become dependencies, how that differs from ObservableObject, and what Observation does not do: persistence, thread safety or performance tuning. Same approach as always: predict, write Swift, run it, inspect the internals, apply to NPay. Every claim today comes with a run.')
outcomes_slide('4.3', [("code", "Read what @Observable expands to"),
                       ("eye", "Explain dependency tracking by property reads"),
                       ("diff", "Contrast @Observable with ObservableObject"),
                       ("link", "Use @State, @Bindable and @Observable together"),
                       ("layers", "Predict updates for computed, nested and ignored properties"),
                       ("shield", "Keep Observation apart from threading and persistence")])
where_slide('4.3', 'Today: inside @Observable', (),
            '4.2: PaymentViewModel, owned by a feature root.',
            'Observation internals: tracking, scope, limits.',
            'Last time PaymentViewModel became @Observable and @State kept one instance alive. Today we look inside: what the macro generates and how SwiftUI learns, view by view, what to update. The text arrived in two parts; the second restarts at Section 16.',
            'The problem.')

# ================================================================== Part 1 (1, 2, 3)
divider(1, "Why Observation", "Update only what depends on the change", 'And what happens without it.', 'The problem.')
P = []
P.append(box(380, 0, 300, 56, "recipient changes", "one keystroke", None, 'solid', 'tap'))
for i, (t, sub, l) in enumerate([("BalanceCard", "₹25,000 &middot; unrelated", None), ("PaymentForm", "reads recipient", '1+'), ("History", "3 transactions &middot; unrelated", None)]):
    x = i * 380
    P.append(wire(f'M530 57L{x + 150} 118' + head(x + 150, 118, 'd'), '1+' if i == 1 else None, '' if i == 1 else 'faint'))
    P.append(box(x, 120, 300, 60, t, sub, l, '', ''))
S.append(slide("Part 1 &middot; Our engineering problem (section 1)", "One keystroke: what should update?", f"""  <div class="body">
    {cues(1)}
    {svg('0 0 1060 180', 'A recipient change should update PaymentForm, not BalanceCard or History', 'dep', P, 'max-height:190px')}
    <p class="small muted" style="margin:6px 0 0">Intended dependencies, not measured body counts.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Three areas, one store", ul("BalanceCard reads the balance", "PaymentForm reads the recipient", "History reads transactions"))}</div>
      <div class="rule step" data-label="Goal">{ul("Property-level dependency tracking")}</div>
    </div>
  </div>""", notes(('SAY', 'Imagine three independent areas of NPay reading the same NPayStore: BalanceCard shows ₹25,000, PaymentForm shows the recipient, TransactionHistory shows transactions. The user types one character into the recipient field. Should SwiftUI update the balance and every transaction row? Ideally, no. Click: only PaymentForm reads the recipient.'),
                  ('SAY', 'Click: three areas, one store. Click: what we want is property-level dependency tracking, and that is what modern Observation makes possible. Let&rsquo;s discover how, starting with no Observation at all.'),
                  ('CONNECT', 'An ordinary class.'))))

PLAIN = """final class CounterModel {
    var count = 0
}

struct CounterLab: View {
    @State private var model = CounterModel()

    var body: some View {
        VStack(spacing: 20) {
            Text("Count: \\(model.count)")

            Button("Increment") {
                model.count += 1
            }
        }
    }
}"""
S.append(slide("Part 1 &middot; Without Observation, then with it (sections 2&ndash;3)", "Same view; only the model changes", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 2: an ordinary class", PLAIN, "font-size:11.5px")}
        <div class="step">{code("Section 3: change only the model", "@Observable\nfinal class CounterModel {\n    var count = 0\n}", "font-size:12.5px")}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Plain class, three taps (simulator)", ["tap: model.count is now 1 &hellip; 2 &hellip; 3", "screen shows: <b>Count: 0</b>"], 12)}
          {crop("img/plain.png", "Plain class", 300)}</div>
        <div class="step">{console("@Observable, three taps", ["screen shows: <b>Count: 3</b>"], 12)}
          {crop("img/observable.png", "@Observable", 300)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 2: an ordinary class, CounterModel, with a count; a view that owns it in @State, shows the count and increments it. Predict: when you tap Increment, will the count reliably update?'),
                  ('SAY', 'Click: section 3 changes only the model: add @Observable. Click: first, the plain class, three taps in the simulator. The model counted to three; the screen still says Count: 0. @State stores the reference, but mutating a property of a plain class tells SwiftUI nothing. Other unrelated updates might make the value appear later, but that is not a reactive design.'),
                  ('SAY', 'Click: with @Observable and the same view: Count: 3. No refresh call, no notification of our own: the macro made the model take part in Observation.'),
                  ('CONNECT', 'So what is @Observable?'))))

# ================================================================== Part 2 (4, 5, 8)
divider(2, "Inside the macro", "What @Observable generates", 'The compiler&rsquo;s real expansion.', 'The idea.')
P = []
for i, (ic, t, sub) in enumerate([("code", "Your source", "@Observable class CounterModel"), ("gear", "Macro expansion", "adds tracking machinery"),
                                   ("layers", "Compiled model", "reads and writes are tracked"), ("eye", "SwiftUI", "records which properties a view read")]):
    x = i * 280
    P.append(tall(x, 0, 260, 120, ic, t, sub, f'{i + 1}' if i < 3 else '4+', ''))
    if i < 3:
        P.append(wire(f'M{x + 261} 60H{x + 278}' + head(x + 278, 60, 'r')))
S.append(slide("Part 2 &middot; What exactly is @Observable? (section 4)", "A macro, not a base class or protocol you implement", f"""  <div class="body">
    {cues(4)}
    {svg('0 0 1100 120', 'Source, macro expansion, compiled observable model, SwiftUI', 'macro', P, 'max-height:128px')}
    <div class="gap"></div>
    <div style="display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px">
      <div class="step">{card("Not a base class", ul("No superclass"))}</div>
      <div class="step">{card("Not hand-written", ul("No conformance you implement"))}</div>
      <div class="step">{card("Compile time", ul("The type is transformed"))}</div>
    </div>
  </div>""", notes(('SAY', '@Observable is a Swift macro. Click through: your source, an @Observable class; the macro expansion adds observation tracking machinery; the compiled model&rsquo;s property reads and writes take part in Observation; SwiftUI tracks which properties each view depends on.'),
                  ('SAY', 'Click: it is not a base class. Click: it is not a protocol conformance you implement by hand. Click: the macro transforms the annotated type at compile time. That is why we never write a notification for each property.'),
                  ('CONNECT', 'Let&rsquo;s see the real expansion.'))))

EXP = ["@ObservationIgnored private let _$observationRegistrar =", "&ensp;&ensp;&ensp;&ensp;Observation.ObservationRegistrar()", "",
       "@ObservationTracked var count = 0&ensp;&ensp;&rarr;&ensp;&ensp;private var _count = 0", "",
       "get {", "&ensp;&ensp;access(keyPath: \\.count)", "&ensp;&ensp;return _count", "}",
       "set {", "&ensp;&ensp;guard shouldNotifyObservers(_count, newValue) else {", "&ensp;&ensp;&ensp;&ensp;_count = newValue; return", "&ensp;&ensp;}",
       "&ensp;&ensp;withMutation(keyPath: \\.count) { _count = newValue }", "}", "",
       "extension CounterModel: nonisolated Observation.Observable {}"]
S.append(slide("Part 2 &middot; Inspect the macro expansion (section 5)", "Real compiler output, condensed", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:22px;align-items:start">
      {console("swiftc -Xfrontend -dump-macro-expansions (Swift 6.3)", EXP, 11.5)}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("What we see", ul("Backing storage: <code>_count</code>", "A registrar", "Access tracked in <code>get</code>", "Mutation tracked in <code>set</code>"))}</div>
        <div class="rule step" data-label="Equatable values">{ul("Old and new compared first", "Same value: no notification")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text shows a conceptual expansion. We asked the compiler for the real one, swiftc with dump-macro-expansions, Swift 6.3, and condensed it. A private registrar, _$observationRegistrar, itself ignored by Observation. The stored property count becomes tracked: its value moves to private backing storage, _count, and count becomes a computed property.'),
                  ('SAY', 'The getter calls access with the key path backslash count, then returns _count: that is the read being recorded. The setter asks shouldNotifyObservers, and, if so, wraps the write in withMutation for the same key path: that is the mutation being announced. And an extension makes the class conform to Observable. The real expansion also has a _modify accessor and an init accessor; details can change between Swift versions.'),
                  ('SAY', 'Click: so: backing storage, a registrar, access tracking, mutation tracking, exactly the text&rsquo;s list. Click: one detail the conceptual version hides: for Equatable values, shouldNotifyObservers is lhs not-equal rhs: assigning the same value notifies nobody, which is what Lesson 3.11 observed. In Xcode, right-click @Observable and choose Expand Macro; the menu location varies by version.'),
                  ('CONNECT', 'The registrar.'))))

S.append(slide("Part 2 &middot; What is ObservationRegistrar? (section 8)", "Records reads and writes; renders nothing", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Two questions", ul("Which property is being <b>accessed</b>? &rarr; <code>access(keyPath:)</code>", "When is it being <b>mutated</b>? &rarr; <code>withMutation(keyPath:)</code>"))}
        <div class="step">{card("One per object", ul("<code>_$observationRegistrar</code>, generated", "Itself <code>@ObservationIgnored</code>"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("SwiftUI", ul("Uses that information to invalidate views"))}</div>
        <div class="rule step" data-label="Distinction">{ul("Registrar: tracking", "SwiftUI: invalidation and updates", "Rendering: a separate responsibility")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'In the expansion we met ObservationRegistrar. An observable model must answer two questions: which property is being accessed, and when is it being mutated. The generated access method passes the key path to the registrar; withMutation tells it a mutation is happening. Click: each observable object gets its own registrar, generated by the macro and itself excluded from tracking.'),
                  ('SAY', 'Click: SwiftUI uses that information to coordinate view invalidation and updates. Click: the distinction: the registrar does not render the UI; SwiftUI decides what to invalidate; rendering remains a separate framework responsibility, as Lesson 3.12&rsquo;s pipeline showed.'),
                  ('CONNECT', 'How does SwiftUI learn which property a view read?'))))

# ================================================================== Part 3 (6, 7, 13, 22, 17)
divider(3, "Dependencies follow reads", "Each view depends on what its body read", 'Measured with _printChanges.', 'Two views.')
TWOV = """@Observable
final class DemoStore {
    var balance = 25000
    var recipient = ""
}

struct BalanceDisplay: View {
    let store: DemoStore
    var body: some View {
        let _ = Self._printChanges()
        return Text("Balance: \\(store.balance)")
    }
}

struct RecipientEditor: View {
    @Bindable var store: DemoStore
    var body: some View {
        let _ = Self._printChanges()
        return TextField("Recipient",
                         text: $store.recipient)
    }
}"""
L13 = ["BalanceDisplay: @self changed.", "RecipientEditor: @self changed.", "-- typing \"ravi\"",
       "RecipientEditor: \\DemoStore.recipient changed.&ensp;&times;4", "-- (no BalanceDisplay lines)"]
S.append(slide("Part 3 &middot; How does SwiftUI know which property was read? (sections 6, 13)", "Type four letters: one view updates", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 13 (excerpt; ObservationLab holds both)", TWOV, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator console", L13, 11.5)}</div>
        <div class="step">{card("Read it", ul("Each body ran once at first appearance (@self)", "Then only RecipientEditor, once per letter", "Named by key path"))}</div>
        <div class="warn step" data-label="Nuance">{ul("Tracking is precise, not a ban on re-evaluation", "Parents and identity still matter")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 6&rsquo;s idea, with Section 13&rsquo;s runnable lab: one observable DemoStore with a balance and a recipient; BalanceDisplay reads only the balance, RecipientEditor binds the recipient; both bodies call _printChanges. Observation records the accesses while SwiftUI evaluates each view.'),
                  ('SAY', 'Click: we ran it and typed "ravi". At first appearance each view printed "@self changed". Then four lines, all RecipientEditor: "backslash DemoStore dot recipient changed", once per letter. BalanceDisplay never printed: it does not depend on the recipient. Click: that answers the text&rsquo;s three investigation questions for this environment; extra updates from the parent or the input system did not appear here.'),
                  ('SAY', 'Click: the nuance: Observation provides more precise dependency tracking, not an absolute prohibition. Parent updates, identity changes and other dependencies can still re-evaluate BalanceDisplay. And _printChanges is a debugging aid, not a rendering measurement.'),
                  ('CONNECT', 'Now change the balance instead.'))))

L22 = ["-- typing \"ravi@npay\"", "RecipientDebugView: \\ObservationDemo.recipient changed.&ensp;&times;9", "-- Add ₹100, twice",
       "BalanceDebugView: \\ObservationDemo.balance changed.&ensp;&times;2"]
S.append(slide("Part 3 &middot; Debugging Observation (section 22)", "Different views, different dependencies", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Section 22&rsquo;s lab", ul("<code>@MainActor @Observable ObservationDemo</code>", "BalanceDebugView, RecipientDebugView", "Step 5: a button that changes the balance (ours: &ldquo;Add ₹100&rdquo;)"))}
        {code("Step 5", 'Button("Add ₹100") { model.balance += 100 }', "font-size:13px")}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator console", L22, 11.5)}</div>
        <div class="rule step" data-label="Learned">{ul("Each view tracks its own reads", "_printChanges: a debugging aid, not a performance metric")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 22 repeats the lab with a main-actor ViewModel, ObservationDemo, and adds steps: type ravi@npay, then add a button that modifies the balance and compare. Our button adds ₹100.'),
                  ('SAY', 'Click: nine letters, nine RecipientDebugView lines, each naming the recipient. Two taps on Add ₹100, two BalanceDebugView lines, each naming the balance. Neither view ever updated for the other&rsquo;s property.'),
                  ('SAY', 'Click: SwiftUI tracks different observable dependencies for different views. And _printChanges remains a debugging aid, not a guaranteed rendering or performance measurement.'),
                  ('CONNECT', 'What if a view reads several properties, or a computed one?'))))

CMP = """@Observable
final class NPayMetrics {
    var balance = 25000
    var transactionCount = 10

    var summary: String {
        "\\(balance) — \\(transactionCount)"
    }
}"""
DEPT = [("balance", "1", "0", "1"), ("transactionCount", "0", "1", "1"), ("balance = same value", "0", "0", "0")]
S.append(slide("Part 3 &middot; Observation follows property reads (sections 7, 17)", "A computed property depends on what it reads", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 17", CMP, "font-size:12.5px")}
        {card("Three views", ul("BalanceCard: <code>balance</code>", "TransactionCount: <code>transactionCount</code>", "DashboardSummary: <code>summary</code>"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Changed", "Balance", "Count", "Summary"], DEPT)}
          <p class="small muted" style="margin:6px 0 0">Body evaluations counted in the simulator (ours).</p></div>
        <div class="rule step" data-label="Computed">{ul("<code>summary</code>&rsquo;s getter reads both", "So the view depends on both")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s dependency explorer, measured. NPayMetrics has a balance, a transaction count and a computed summary that reads both. Three views read balance, transactionCount and summary respectively.'),
                  ('SAY', 'Click: we changed each property from code and counted body evaluations. Changing the balance ran BalanceCard and DashboardSummary, not TransactionCount. Changing the count ran TransactionCount and DashboardSummary. Assigning the balance its own value ran nothing, the equality check in the expansion.'),
                  ('SAY', 'Click: summary is computed: when DashboardSummary reads it, the getter accesses both stored properties, and those accesses become its dependencies. That is why computed properties work naturally with Observation.'),
                  ('CONNECT', 'Before Observation, SwiftUI used ObservableObject.'))))

# ================================================================== Part 4 (9)
divider(4, "ObservableObject", "Object-level vs property-level", 'The older model, measured side by side.', 'The comparison.')
OLD = """final class OldPaymentModel: ObservableObject {
    @Published var recipient = ""
    @Published var amountText = ""
}

@StateObject private var model = OldPaymentModel()"""
OBT = [("Protocol", "Macro-based observation"), ("@Published properties", "Stored properties, tracked by the macro"), ("Object-level change publisher", "Property-access tracking"),
       ("@StateObject for owned objects", "@State for owned objects"), ("Combine-oriented", "Observation framework")]
LOLD = ["-- typing \"ravi\" (ObservableObject + @Published)", "OldBalanceDisplay: _store changed.&ensp;&ensp;&times;5", "OldRecipientEditor: _store changed.&ensp;&times;5"]
S.append(slide("Part 4 &middot; How is this different from ObservableObject? (section 9)", "Every observer, on every change", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("The older pattern", OLD, "font-size:11.5px")}
        {tbl(["ObservableObject", "@Observable"], OBT, 'tbl compact')}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Section 13&rsquo;s lab rebuilt with ObservableObject (ours)", LOLD, 11.5)}</div>
        <div class="step">{card("Compare", ul("@Observable: 4 RecipientEditor, 0 BalanceDisplay", "ObservableObject: both, every time"))}</div>
        <div class="rule step" data-label="Not obsolete">{ul("Older iOS, existing code, APIs built on it", "NPay targets iOS 17+: Observation")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Before Observation: a class conforming to ObservableObject, @Published properties, owned with @StateObject. It publishes changes at the object level through Combine; Observation tracks individual property accesses. The table: protocol versus macro; @Published versus tracked stored properties; an object-level change publisher versus property-access tracking; @StateObject versus @State for owned objects; Combine versus the Observation framework.'),
                  ('SAY', 'Click: we rebuilt Section 13&rsquo;s lab with ObservableObject and @Published, both views using @ObservedObject, and typed "ravi". Both views printed "_store changed" on every change, five times each: the balance view updated for the recipient too, because it observes the whole object. Click: with @Observable, four RecipientEditor updates and no BalanceDisplay updates.'),
                  ('SAY', 'Click: is ObservableObject obsolete? No: existing codebases, older iOS versions and APIs designed around it still use it. NPay targets iOS 17 and later, so we continue with Observation.'),
                  ('CONNECT', 'Three attributes that are easy to mix up.'))))

# ================================================================== Part 5 (10, 20)
divider(5, "Owning and binding", "@Observable, @State, @Bindable", 'Who tracks, who owns, who binds.', 'The three.')
ROLES = """@Observable
final class PaymentViewModel {
    var recipient = ""
}

struct PaymentScreen: View {
    @State private var viewModel = PaymentViewModel()

    var body: some View {
        @Bindable var viewModel = viewModel

        TextField(
            "Recipient",
            text: $viewModel.recipient
        )
    }
}"""
RT = [("@Observable", "Makes model properties observable"), ("@State", "Owns the model reference in SwiftUI state"), ("@Bindable", "Creates bindings to its mutable properties")]
S.append(slide("Part 5 &middot; @State, @Bindable and @Observable together (section 10)", "Track, own, bind", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 10", ROLES, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Mechanism", "Responsibility"], RT)}
        <div class="step">{card("Why not @Binding?", ul("@Binding: one particular value", "@Bindable: bindings to <i>any</i> property", "<code>$viewModel.recipient</code> &rarr; a TextField binding"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Three attributes that are often confused, in one example. @Observable makes the model&rsquo;s properties observable. @State owns the model reference in SwiftUI&rsquo;s state storage, so it survives body evaluations, as 4.2 measured. @Bindable, here declared locally inside body, creates bindings to the model&rsquo;s mutable properties.'),
                  ('SAY', 'Click: why not @Binding? A @Binding represents a binding to one particular value. @Bindable provides dynamic binding projections to any property of an observable model: dollar viewModel dot recipient produces a binding suitable for TextField.'),
                  ('CONNECT', 'Ownership done wrong.'))))

BVM = """struct PaymentsScreen: View {
    var body: some View {
        let viewModel = PaymentViewModel()

        return TextField(
            "Recipient",
            text: Binding(
                get: { viewModel.recipient },
                set: { viewModel.recipient = $0 }
            )
        )
    }
}"""
LBV = ["at launch:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;1 ViewModel", "typed \"ravi\":&ensp;&ensp;&ensp;&ensp;field shows \"ravi\"", "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;4 more ViewModels created",
       "parent update:&ensp;&ensp;&ensp;field shows <b>\"\"</b>, 1 more ViewModel"]
S.append(slide("Part 5 &middot; Common mistake: a ViewModel inside body (section 20)", "Every evaluation can build a new one", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 20 (poor ownership)", BVM, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator (lab type renamed; parent button ours)", LBV, 11.5)}</div>
        <div class="step">{card("What happened", ul("Each keystroke re-ran body: a new ViewModel", "An unrelated parent update: the draft vanished"))}</div>
        <div class="rule step" data-label="Better">{ul("<code>@State private var viewModel</code>", "Or receive it from a stable parent (4.2)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A poor ownership design: body creates a PaymentViewModel and binds a TextField to it with a hand-made Binding. Every time body is evaluated, the expression can construct another ViewModel.'),
                  ('SAY', 'Click: we ran it, with a parent that can update for an unrelated reason, a button of ours. Typing "ravi" looked fine, the field showed ravi, but four more ViewModels were created along the way. Then one unrelated parent update: the field went blank, and one more ViewModel appeared. The draft was in an object nobody holds any more.'),
                  ('SAY', 'Click: the user&rsquo;s draft is lost and the model&rsquo;s lifetime is hard to reason about. Click: better: @State private var viewModel, or receive a ViewModel created by a stable parent, NPay&rsquo;s PaymentsFeatureRoot. ViewModel ownership is a lifecycle decision, not merely a syntax choice.'),
                  ('CONNECT', 'Computed, ignored and nested properties.'))))

# ================================================================== Part 6 (11, 12, 18)
divider(6, "Computed, ignored, nested", "What is tracked, exactly", 'Three cases, measured.', 'Computed.')
VALID = """@Observable
final class PaymentViewModel {
    var recipient = ""
    var amountText = ""

    var isValid: Bool {
        !recipient.isEmpty && !amountText.isEmpty
    }
}

.disabled(!viewModel.isValid)"""
VT = [("amountText (recipient still empty)", "<b>0</b>"), ("recipient", "1")]
S.append(slide("Part 6 &middot; Tracking and computed properties (section 11)", "Dependencies are the reads that actually happened", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 11", VALID, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("The getter reads", ul("<code>recipient</code> and <code>amountText</code>", "Both can become dependencies"))}
        <div class="step">{tbl(["Changed (starting empty)", "Continue button body"], VT)}
          <p class="small muted" style="margin:6px 0 0">Simulator count (ours).</p></div>
        <div class="step">{card("Why 0?", ul("<code>&amp;&amp;</code> stopped at the empty recipient", "<code>amountText</code> was never read, so not tracked"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The ViewModel&rsquo;s isValid reads recipient and amountText. When SwiftUI evaluates .disabled(!viewModel.isValid), the getter&rsquo;s reads become tracked dependencies, so we do not need a stored isValid flag.'),
                  ('SAY', 'Click: we measured it, starting from an empty form. Setting amountText did not re-run the Continue button at all. Setting recipient did. Click: why? The && short-circuited: with an empty recipient, the getter returned false without ever reading amountText, so that evaluation had no dependency on it. Once the recipient changes and the body runs again, both are read and both are tracked.'),
                  ('SAY', 'This is the precise meaning of "can become dependencies": Observation tracks the reads that actually happened during the last evaluation, and that is always enough to stay correct, because the result could not have changed.'),
                  ('CONNECT', 'Properties that should not be tracked.'))))

IGN = """@Observable
final class PaymentViewModel {
    var recipient = ""

    @ObservationIgnored
    private let logger = Logger(
        subsystem: "com.example.npay",
        category: "Payments"
    )
}"""
S.append(slide("Part 6 &middot; Properties that should not be observed (section 12)", "@ObservationIgnored", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 12 (import OSLog)", IGN, "font-size:12.5px")}
        <div class="step">{console("Expansion", ["recipient:&ensp;@ObservationTracked, _recipient", "logger:&ensp;&ensp;&ensp;nothing generated"], 12)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("An ignored <code>var note</code> in a view (simulator)", ["note changed:&ensp;&ensp;&ensp;&ensp;&ensp;view body 0; screen \"/ first\"", "recipient changed: view body 1; screen \"ravi@npay / second\""], 11.5)}</div>
        <div class="warn step" data-label="Only observation">{ul("Not thread safety, not ownership", "An ignored value shown in UI goes stale")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Not every property belongs in Observation. A logger is an implementation detail, not something that should drive UI updates, so the text marks it @ObservationIgnored. You need import OSLog for Logger. Click: the expansion confirms it: recipient gets @ObservationTracked and backing storage; the ignored logger gets nothing.'),
                  ('SAY', 'Click: we also ignored a var, note, that a view displays. Changing note ran no body: the screen still said "first". Changing the tracked recipient ran the body once, and only then did the new note appear. Click: so ignoring affects observation participation only: it does not make the property thread safe or change its ownership, and if the UI shows an ignored value, the UI goes stale.'),
                  ('CONNECT', 'Models inside models.'))))

NEST = """@Observable
final class AccountModel {
    var balancePaise = 2_500_000
}

@Observable
final class PaymentModel {
    var recipient = ""
    var amountText = ""
}

@Observable
final class NPayAppState {
    var account = AccountModel()
    var payment = PaymentModel()
}"""
NT = [("payment.recipient", "0", "1"), ("payment.amountText", "0", "0"), ("account.balancePaise", "1", "0"),
      ("new AccountModel", "1", "0"), ("new PaymentModel", "0", "1")]
S.append(slide("Part 6 &middot; Nested observable models (section 18)", "Each link in the chain is a dependency", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 18", NEST, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Changed", "Account view", "Payment view"], NT, 'tbl compact')}
          <p class="small muted" style="margin:6px 0 0">Body evaluations, simulator (ours).</p></div>
        <div class="rule step" data-label="Not recursive">{ul("No parent-wide publishing", "Only properties actually read")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A more realistic shape: separate observable models for the account and the payment, composed into NPayAppState. A view can read appState.account.balancePaise or appState.payment.recipient.'),
                  ('SAY', 'Click: we measured two views, one reading each chain. A recipient change ran only the payment view; amountText, read by nobody, ran nothing; a balance change ran only the account view. Replacing the whole account with a new AccountModel ran the account view; replacing the payment model ran the payment view.'),
                  ('SAY', 'The access chain involves two observations: reading appState.account is a read of the parent&rsquo;s account property, and reading balancePaise is a read of the child. Either changing invalidates the view. Click: and it is not recursive publishing: changing any property of the child does not notify everyone who reads the parent; dependencies are the properties actually accessed.'),
                  ('CONNECT', 'What Observation does not do.'))))

# ================================================================== Part 7 (14, 15, 19, 21, 23)
divider(7, "What Observation isn&rsquo;t", "Not persistence, thread safety or performance", 'Separate concerns, separate tools.', 'Persistence.')
PERS = [("@Observable", "Tracks observable changes"), ("@State", "Owns state in the SwiftUI hierarchy"), ("@Bindable", "Exposes mutable bindings"),
        ("SwiftData", "Persists structured local data"), ("UserDefaults", "Persists simple preferences"), ("Keychain", "Stores secrets securely")]
S.append(slide("Part 7 &middot; Observation isn&rsquo;t persistence or performance (sections 14, 19, 23)", "It coordinates updates; nothing more", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Mechanism", "Responsibility"], PERS, 'tbl compact')}
        <p class="small muted" style="margin:0">Section 19. Persistent repositories: Unit 6. Relaunch empties the draft (3.5).</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("Section 14", "var filteredTransactions: [Transaction] {\n    transactions.filter {\n        $0.title.contains(searchText)\n    }\n}", "font-size:12px")}</div>
        <div class="step">{card("Still your job", ul("A computed property isn&rsquo;t cached", "50,000 records: 4 keystrokes, 4 filters (3.11)", "Layout, identity, main-thread work"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Setting viewModel.recipient updates the interface. Does the value get saved to disk? No. Observation tracks changes; persistence stores data durably. @Observable tracks, @State owns, @Bindable binds; SwiftData, UserDefaults and the Keychain persist, each for its own kind of data. Lesson 3.5 showed a relaunch emptying the draft; persistent repositories come in Unit 6.'),
                  ('SAY', 'Click: and performance. A filtered list as a computed property is still recomputed whenever it is read after a change. Click: Observation tracks dependencies; it does not cache arbitrary computed properties or improve their algorithms. Lesson 3.11 measured it: four keystrokes, four filters of fifty thousand records. Property-level tracking avoids invalidating unrelated views, but layout complexity, expensive calculations, collection identity and main-thread work remain yours. Observation improves update coordination; it does not replace profiling.'),
                  ('CONNECT', 'And it is not thread safety.'))))

RACE = """@Observable
final class PaymentViewModel {
    var amountText = ""
}

func edit(_ viewModel: PaymentViewModel) async {
    await withTaskGroup(of: Void.self) { group in
        for i in 0..<2 {
            group.addTask {
                viewModel.amountText = "\\(i)"
            }
        }
    }
}"""
TS = [("Observation", "Actor isolation"), ("Tracks property access and changes", "Controls concurrent access"), ("Supports reactive UI updates", "Helps prevent data races"),
      ("Doesn&rsquo;t guarantee thread safety", "Doesn&rsquo;t render UI")]
S.append(slide("Part 7 &middot; Observation isn&rsquo;t thread safety (sections 15, 21)", "Two concurrent writers: the compiler objects", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Two tasks write one model (ours)", RACE, "font-size:11px")}
        <div class="step">{console("swiftc -swift-version 6", ["error: passing closure as a 'sending' parameter risks", "causing data races between code in the current task", "and concurrent execution of the closure"], 11)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Add @MainActor", ["error: main actor-isolated property 'amountText'", "can not be mutated from a nonisolated context"], 11)}</div>
        <div class="step">{card("With <code>await MainActor.run { &hellip; }</code>", ul("Compiles: each write waits its turn on the main actor"))}</div>
        <div class="step">{tbl(["Observation", "Actor isolation"], TS[1:], 'tbl compact')}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Does @Observable make an object thread safe? No. We wrote two concurrent tasks writing the same observable model. Click: Swift 6 rejected it: passing the closure risks a data race. The macro made the model observable; it did nothing to serialize mutations. Note: this check runs after type checking, so a plain typecheck does not show it; a full compile does.'),
                  ('SAY', 'Click: add @MainActor, NPay&rsquo;s choice for UI-facing state: now the error is about isolation: a main-actor property cannot be mutated from a nonisolated context. Click: the mutation rules are explicit, and with await MainActor.run, each write waits its turn on the main actor, and it compiles.'),
                  ('SAY', 'Click: the text&rsquo;s table: Observation tracks access and changes and supports reactive UI, but does not guarantee thread safety; actor isolation controls concurrent access and helps prevent data races, but does not render UI. Observation answers what changed; actor isolation answers who may access or mutate this state, and when. Unit 8 goes deep on actors.'),
                  ('CONNECT', 'The whole flow, end to end.'))))

# ================================================================== Part 8 (16, NPay)
divider(8, "The full flow, in NPay", "From keystroke to updated screen", 'And what NPay&rsquo;s ViewModel actually tracks.', 'The flow.')
P = []
FS = [("tap", "User edits amount", "TextField gets new text"), ("link", "Binding writes", "$viewModel.amountText"), ("gear", "withMutation", "the registrar records it"),
      ("eye", "Invalidation", "views that read amountText"), ("code", "Body re-evaluated", "reads, and tracks, again"), ("phone", "Screen updates", "message, Review button")]
for i, (ic, t, sub) in enumerate(FS):
    x = i * 188
    P.append(tall(x, 0, 172, 124, ic, t, sub, f'{i + 1}' if i < 5 else '6+', ''))
    if i < 5:
        P.append(wire(f'M{x + 173} 62H{x + 186}' + head(x + 186, 62, 'r')))
NPV = ["recipient&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;@ObservationTracked", "amountText&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;@ObservationTracked",
       "errorMessage&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;@ObservationTracked", "let store&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;nothing (a let)",
       "parsedAmountPaise, &hellip;&ensp;nothing (computed)"]
S.append(slide("Part 8 &middot; The complete NPay Observation flow (section 16) &middot; conceptual", "Views declare dependencies by reading", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1120 124', 'Edit, binding write, withMutation, invalidation, body re-evaluated, screen updates', 'flow', P, 'max-height:130px')}
    <p class="small muted" style="margin:6px 0 0">Stage 1 is the text&rsquo;s; stages 2&ndash;6 are ours, from the expansion and today&rsquo;s runs.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div class="step">{console("NPay&rsquo;s PaymentViewModel, expanded", NPV, 11.5)}</div>
      <div class="rule step" data-label="No refreshPaymentScreen()">{ul("Reading an observable property declares the dependency", "SwiftUI coordinates the rest")}</div>
    </div>
  </div>""", notes(('SAY', 'The full flow. Only the first stage of the text&rsquo;s stepper was shared, so stages two to six are ours, built from today&rsquo;s expansion and runs. Click through: the user edits the amount and the TextField receives text through the input system; the binding writes viewModel.amountText; the generated setter calls withMutation and the registrar records it; SwiftUI invalidates the views whose last evaluation read amountText; their bodies run again, reading, and so re-tracking, what they need; the screen shows the validation message and the Review button&rsquo;s new state.'),
                  ('SAY', 'Click: applied to NPay: we expanded NPay&rsquo;s real PaymentViewModel. recipient, amountText and errorMessage get @ObservationTracked. The injected store, a let, gets nothing: it never changes, so there is nothing to observe. Computed properties like parsedAmountPaise get nothing either: their dependencies are the stored properties they read.'),
                  ('SAY', 'Click: the principle: SwiftUI never needs a refreshPaymentScreen() call; the screen declares its dependencies by reading observable properties during evaluation, and SwiftUI coordinates the updates. User input, binding, observable ViewModel, dependency tracking, SwiftUI update.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.3', (), [("code", "A macro that rewrites properties", "get &rarr; access, set &rarr; withMutation, via a registrar"),
                     ("eye", "Dependencies = reads that happened", "only RecipientEditor updated; ObservableObject updated both"),
                     ("shield", "Tracking only", "not persistence, not thread safety, not caching")],
          'Three things to remember. @Observable is a macro: each stored property becomes a computed one whose getter reports an access and whose setter wraps the write in withMutation, through a per-object registrar; equal values notify nobody. A view depends exactly on the observable properties its last evaluation read, including through computed properties and nested models, which is why typing updated only RecipientEditor while ObservableObject updated both views. And Observation only tracks: it does not save, it does not make a class thread safe, and it does not cache expensive computations.')

review_divider(10)
review([("code", "Choose one", "What does @Observable primarily provide?",
         "What does <code>@Observable</code> primarily provide?<br>A. Database persistence<br>B. Property observation support<br>C. Automatic thread safety", "B",
         "Tracked getters and setters, via a registrar.",
         "Reading more into the macro than tracking.", "Most pick B.", None),
        ("db", "Question", "Does @Observable automatically save values to disk?",
         "Does <code>@Observable</code> automatically save values to disk?", "No",
         "Persistence is SwiftData, UserDefaults, Keychain: Unit 6.",
         "Confusing observed with stored.", "Most say no.", None),
        ("layers", "Question", "Can a computed property participate in Observation dependencies?",
         "Can a computed property participate in Observation dependencies?", "Yes",
         "summary depended on both properties it read.",
         "Thinking only stored properties count.", "Most say yes.", None),
        ("clock", "Choose one", "Why avoid constructing ViewModels inside body?",
         "Why avoid constructing ViewModels inside <code>body</code>?<br>A. Classes can&rsquo;t be initialized there<br>B. Unstable ownership and possible state loss<br>C. SwiftUI prohibits local variables", "B",
         "Our run: 5 ViewModels, then a blank field.",
         "Treating ownership as syntax.", "Most pick B.", None),
        ("shield", "Question", "Does @MainActor serve the same purpose as @Observable?",
         "Does <code>@MainActor</code> serve the same purpose as <code>@Observable</code>?", "No",
         "One answers who may mutate; the other, what changed.",
         "Merging isolation and observation.", "Some say yes.", None),
        ("phone", "Question", "Does every observed mutation cause a full-screen redraw?",
         "Does every observed mutation necessarily cause a full-screen redraw?", "No",
         "Only dependent views re-evaluated; rendering is separate.",
         "Picturing whole-screen refreshes.", "Some say yes.", None),
        ("eye", "Question", "Can different views track different properties of the same model?",
         "Can different views track different properties of the same observable model?", "Yes",
         "RecipientDebugView &times;9, BalanceDebugView &times;2.",
         "Expecting object-level updates.", "Most say yes.", None),
        ("tap", "Predict the result", "Plain class, @State, three Increment taps: the screen shows?",
         "<code>final class CounterModel { var count = 0 }</code> (no @Observable), owned with <code>@State</code>. After three taps on Increment, the screen shows&hellip;<br>A. Count: 3<br>B. Count: 0<br>C. A runtime error", "B",
         "The model reached 3; SwiftUI was never told.",
         "Expecting @State to observe a class&rsquo;s properties.", "Many pick A.", None),
        ("check", "Predict the result", "isValid = !recipient.isEmpty && !amountText.isEmpty; recipient empty; set amountText. Does the button's body re-run?",
         "A button reads <code>isValid</code> (<code>!recipient.isEmpty &amp;&amp; !amountText.isEmpty</code>). The recipient is empty. You set <code>amountText</code>. Does the button&rsquo;s body re-run?<br>A. Yes, it reads isValid<br>B. No: amountText was never read<br>C. Only if amountText is valid", "B",
         "The && short-circuited; measured: 0 evaluations.",
         "Assuming every property in a getter is tracked.", "Many pick A.", None),
        ("key", "Choose one", "From 4.2: where should NPay's PaymentViewModel be created?",
         "From Lesson 4.2: where is NPay&rsquo;s PaymentViewModel created?<br>A. Inside PaymentsScreen.body<br>B. In NPayStore<br>C. In PaymentsFeatureRoot&rsquo;s @State, with the shared store", "C",
         "A stable owner; the store injected.",
         "Creating models where views are described.", "Most pick C.", "Spaced review from Lesson 4.2.")])

S.append(next_slide('4.3', [("4.4", "Dependency injection", "constructor injection, composition roots, a mock payment service"),
                            ("4.7", "UI state modeling", "loading, success, error as observable state"),
                            ("Unit 6", "Persistence", "what Observation deliberately doesn&rsquo;t do"),
                            ("Unit 8", "Concurrency", "actor isolation, beyond @MainActor")],
                    'Lesson 4.4 is dependency injection: constructor injection, protocol-based dependencies, composition roots, environment injection, and swapping NPay&rsquo;s demo payment service for a mock without changing the screen. Unit 6 adds the persistence Observation leaves out, and Unit 8 the concurrency it does not provide.'))

S.append(lab_slide('4.3', "Observe Observation", "Predict, run, read the console.",
                   ["Run CounterLab without, then with, @Observable.",
                    "Expand @Observable in Xcode; find access and withMutation.",
                    "Run the section 22 lab; type, then change the balance.",
                    "Rebuild it with ObservableObject; compare the console.",
                    "Read a computed and a nested property; predict updates.",
                    "Mark one property @ObservationIgnored; watch the UI."],
                   "", 'Expected, as in our run: Count: 0 then Count: 3; only the view that read a property reports it; ObservableObject updates both views; an ignored property shown in the UI goes stale.',
                   side=f'<div>{card("You hand in", ul("Your expansion, annotated", "Console output for both labs", "Your predictions vs results"))}</div>'))

end_slide('4.3', 'Swift Observation<br>Framework Internals', 'Lesson 4.4 &mdash; Dependency Injection in iOS',
          'You can now read what @Observable generates, explain how property reads become view dependencies, contrast Observation with ObservableObject, and keep it apart from persistence, thread safety and performance work.',
          'Next, Lesson 4.4: dependency injection, and replacing NPay&rsquo;s demo payment service with a mock without changing the screen.')

write_deck(OUT43, '4.3', 'Swift Observation Framework Internals', 'Swift Observation Framework Internals')
