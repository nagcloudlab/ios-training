"""Generates decks/unit-2/lesson-2.9/index.html from the Lesson 2.9 text (@Binding: How Two SwiftUI Views Share State).
The text came in two parts (Sections 1-11, 12-17), grouped into 8 Parts. Console output and screenshots come from
tools/sim2_9 (a scripted SwiftUI app run in the iOS Simulator; buttons activated through accessibility); compiler
errors and the SimpleBinding model were run with swiftc; interface lines from the iOS 26.5 SDK."""
import html, os, re, sys
OUT29 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.9', '@Binding: How Two<br>SwiftUI Views Share State',
            'A child view needs to <b>change</b> a value its <b>parent</b> owns. Without a second copy. How?',
            'In 2.8 NPay&rsquo;s balance became @State in ContentView. Now a separate view, a balance editor, needs to change that balance. Passing a value is not enough, and giving the child its own state creates a second copy. The answer is @Binding: what it is, how it writes through, how to build one by hand, and where it belongs in NPay. Console output and screenshots came from the iOS Simulator, with buttons activated through accessibility as before.')
outcomes_slide('2.9', [("diff", "Why passing an <code>Int</code> can&rsquo;t <b>change</b> the parent"),
                       ("link", "<code>@Binding</code> and <code>$balance</code>: read and <b>write</b>"),
                       ("gear", "How a binding writes through: <b>nonmutating set</b>"),
                       ("layers", "<b>One source of truth</b>, not two"),
                       ("code", "Custom bindings: <code>Binding(get:set:)</code>"),
                       ("eye", "Value or binding: give <b>only the access needed</b>")])
where_slide('2.9', 'Today: a child edits parent state', (),
            '2.8: <code>@State balance</code> in ContentView; BalanceCard reads it.',
            'A <code>BalanceEditor</code> that changes it, through a binding.',
            'Last lesson ContentView came to own the balance and BalanceCard displayed it. Today a second child, a balance editor, changes it: the first time a child writes state it does not own.',
            'The problem.')

# ================================================================== Part 1 (1)
divider(1, "A balance editor", "One balance, two views", 'A card shows the balance; an editor changes it.', 'The target.')
S.append(slide("Part 1 &middot; NPay needs a balance editor (section 1)", "Milestone 2.9: an editor sharing one balance", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Want", ul("A <b>Demo Balance Editor</b>: − ₹1,000 / + ₹1,000", "The card shows the <b>same</b> balance"))}
        {card("Don&rsquo;t want", ul("Two independent balance variables", "Instead: <b>one source of truth</b>"))}
      </div>
      {PHONE("img/before.png", "Before: Lesson 2.8", 190)}
      <div class="step">{PHONE("img/taps.png", "+, +, − : ₹26,000", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'ContentView owns the demo balance with @State and BalanceCard displays it; that works because the card only reads. Now we want a separate component, a Demo Balance Editor, that adds or subtracts ₹1,000.'),
                  ('SAY', 'Click: where we finish: the editor below the card. We activated plus, plus, minus, and the card shows ₹26,000. One balance, shown by one view and changed by another; not two balances that can drift apart.'),
                  ('CONNECT', 'First, try passing the balance as an Int.'))))

# ================================================================== Part 2 (2)
divider(2, "Passing an Int", "A copy can&rsquo;t write back", 'Give the editor the balance as a value.', 'Predict.')
LET = """struct BalanceEditor: View {
    let balance: Int

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}"""
S.append(slide("Part 2 &middot; Why passing an Int is not enough (section 2)", "A value is a copy", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("BalanceEditor.swift", LET, "font-size:15px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{err("left side of mutating operator isn&rsquo;t mutable: &lsquo;balance&rsquo; is a &lsquo;let&rsquo; constant")}</div>
        <div class="step"><p style="margin:0;font-size:16px"><b>With <code>var</code> instead:</b></p>{err("left side of mutating operator isn&rsquo;t mutable: &lsquo;self&rsquo; is immutable")}<p class="small muted" style="margin:4px 0 0">Both from swiftc, iOS 26.5 SDK</p></div>
        <div class="rule step" data-label="Unit 01">{ul("An <code>Int</code> parameter is a <b>copy</b>", "Changing a copy can&rsquo;t update the parent", "The child needs access to the parent&rsquo;s <b>storage</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The editor receives the balance as a let and tries to add 1,000. Predict: does it compile?'),
                  ('SAY', 'Click: no: balance is a let constant. Click: change it to var and it still fails, with 2.8&rsquo;s error: self is immutable. And even if it compiled, it would be the wrong pattern.'),
                  ('SAY', 'Click: value semantics from Unit 01. Passing an Int passes a copy. Changing an independent copy can never update the parent&rsquo;s state. The child needs access to the parent&rsquo;s state storage itself.'),
                  ('CONNECT', 'That access is a binding.'))))

# ================================================================== Part 3 (3-4)
divider(3, "@Binding", "Access to someone else&rsquo;s state", 'The child declares @Binding; the parent passes $balance.', 'Two small changes.')
CH = """struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}"""
PA = """struct ContentView: View {
    @State private var balance = 25000

    var body: some View {
        BalanceEditor(balance: $balance)
    }
}"""
S.append(slide("Part 3 &middot; Introducing @Binding (section 3)", "Child: <code>@Binding</code>. Parent: <code>$balance</code>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("The child", CH, "font-size:15px")}</div>
      <div>{code("The parent", PA, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{card("What is happening", ul("ContentView <b>owns</b> the state", "BalanceEditor gets a <b>binding</b> to it", "It reads and writes <b>through</b> the binding"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Change the child&rsquo;s let to @Binding var balance: Int. Now it compiles: the child can modify a value owned elsewhere. The parent provides access by passing $balance, with a dollar sign.'),
                  ('SAY', 'Click: ContentView still owns the state. BalanceEditor receives a binding to it, and reads and writes through that binding.'),
                  ('CONNECT', 'balance and $balance: the most important distinction today.'))))

P = [box(384, 0, 368, 56, '@State balance', 'owned by ContentView', None, 'lit', 'layers'),
     wire('M480 60V96H184V124' + head(184, 124, 'd')), wire('M656 60V96H952V124' + head(952, 124, 'd')),
     box(0, 130, 368, 56, 'balance', 'the Int value', None, '', 'code'),
     box(768, 130, 368, 56, '$balance', 'Binding&lt;Int&gt;: the projected value', None, '', 'link')]
SDK = """// iOS 26.5 SDK (excerpts)
@propertyWrapper public struct State<Value> {
    public var projectedValue: Binding<Value> { get }
}
@propertyWrapper public struct Binding<Value> {
    public var wrappedValue: Value { get nonmutating set }
}"""
S.append(slide("Part 3 &middot; balance versus $balance (section 4)", "The value, or a binding to it", f"""  <div class="body">
    {svg('0 0 1136 186', 'balance is the Int value; $balance is the projected value, a Binding of Int', 'proj', P, 'max-height:170px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div class="step">{console("type(of:) in the simulator", ["parent  $balance:  Binding&lt;Int&gt;", "child   balance:   Int", "child   _balance:  Binding&lt;Int&gt;"], 13)}</div>
      <div class="step">{code("Why the $", SDK, "font-size:12.5px")}</div>
    </div>
  </div>""", notes(('SAY', 'balance gives the wrapped value, an Int. $balance gives the projected value of @State, a Binding of Int.'),
                  ('SAY', 'Click: printed in the simulator. In the parent, $balance is Binding of Int. In the child, balance reads as a plain Int, and its hidden storage, _balance, is a Binding of Int: the child stores the binding the parent passed.'),
                  ('SAY', 'Click: why the dollar sign? A Swift property wrapper can expose a projectedValue, and $name is how you reach it. The SDK shows State&rsquo;s projectedValue is a Binding. So $ is a Swift language feature, not special SwiftUI syntax. Notice Binding&rsquo;s wrappedValue: get, nonmutating set. That is the next slide.'),
                  ('CONNECT', 'How can a binding change something it does not own?'))))

# ================================================================== Part 4 (5, 13)
divider(4, "How a binding works", "It forwards the write", 'A binding holds no balance of its own.', 'A teaching model.')
SB = """// Teaching approximation, not Apple's implementation
struct SimpleBinding<Value> {
    let get: () -> Value
    let set: (Value) -> Void

    var wrappedValue: Value {
        get { get() }
        nonmutating set { set(newValue) }
    }
}

final class Storage { var balance = 25000 }
let storage = Storage()
let binding = SimpleBinding(get: { storage.balance },
                            set: { storage.balance = $0 })
binding.wrappedValue += 1000     // binding is a let!
print(binding.wrappedValue, storage.balance)"""
S.append(slide("Part 4 &middot; How does Binding work? (sections 5, 13)", "A getter, a setter, and <code>nonmutating set</code>", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      <div>{code("SimpleBinding.swift (Mac, swiftc)", SB, "font-size:12.5px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Output", ["through the binding: 26000", "the storage itself:  26000"], 14)}</div>
        <div class="step">{card("nonmutating set", ul("<b>Forwards</b> the write elsewhere", "Works on a <code>let</code>, inside a view"))}</div>
        <div class="rule step" data-label="Ownership">{ul("A binding <b>owns nothing</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A teaching model of a binding, not Apple&rsquo;s implementation: two closures, one that gets a value and one that sets it, and a wrappedValue whose setter is nonmutating. We added a tiny class to stand in for SwiftUI&rsquo;s state storage, made a SimpleBinding to it, stored the binding in a let, and added 1,000 through it.'),
                  ('SAY', 'Click: we compiled and ran it on a Mac: 26,000 through the binding, and 26,000 in the storage itself. Click: that worked on a let because the setter is nonmutating: writing does not change the binding&rsquo;s own fields, it forwards the write to storage elsewhere. That is exactly why a child view, whose self is immutable, can still write through @Binding. The real Binding&rsquo;s wrappedValue is declared get nonmutating set, as we saw in the SDK.'),
                  ('SAY', 'Click: so a binding does not own the value. It is a read and write connection to state owned elsewhere. Value is generic; for NPay it is Binding of Int.'),
                  ('CONNECT', 'Follow one write from the editor to the screen.'))))

WF = [("tap", "Editor: balance += 1000", "the child writes its bound property"), ("link", "Binding.wrappedValue setter", "the write is forwarded"),
      ("layers", "ContentView&rsquo;s @State storage", "the parent&rsquo;s state gets the new value"), ("eye", "Dependency update", "views that read balance are re-evaluated")]
P = [box(0, i * 56, 620, 48, t, sub, str(i + 1) if i < 3 else '4+', '', ic) for i, (ic, t, sub) in enumerate(WF)]
S.append(slide("Part 4 &middot; One write, start to finish (sections 6, 13) &middot; conceptual", "From the editor&rsquo;s button to the card", f"""  <div class="body">
    {cues(4)}
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      {svg('0 0 620 216', 'The editor writes, the binding forwards, the parent state updates, dependent views re-evaluate', 'wf', P, 'max-height:240px')}
      <div class="step">{console("Simulator: +, +, − in NPay", ["BalanceCard body: 25000", "BalanceEditor body: 25000", "BalanceCard body: 26000", "BalanceEditor body: 26000", "… 27000 … 27000", "… 26000 … 26000"], 13)}</div>
    </div>
    <div class="rule step" data-label="Parent @State &harr; child @Binding" style="margin-top:10px">{ul("Read and write both ways; <b>ownership</b> stays with the parent")}</div>
  </div>""", notes(('SAY', 'A conceptual walk; only step 1 of the text&rsquo;s widget was shared, and SwiftUI&rsquo;s binding storage is private. Click: in the editor, balance += 1000 writes the bound property. Click: the binding&rsquo;s setter forwards the write. Click: ContentView&rsquo;s @State storage receives the new value. Click: SwiftUI re-evaluates the views that read balance.'),
                  ('SAY', 'Click: our run in NPay with prints in both bodies: after each activation, both the card and the editor were evaluated with the same new number: 26,000, 27,000, then 26,000 again. One value, two consumers.'),
                  ('SAY', 'Click: the relationship: parent @State, child @Binding, with reads and writes in both directions, but ownership stays with the parent.'),
                  ('CONNECT', 'Why not just give the editor its own @State?'))))

# ================================================================== Part 5 (7)
divider(5, "One source of truth", "Not two copies", 'What if the child owns its own balance?', 'We tried it.')
WR = """struct BalanceEditor: View {   // incorrect design
    @State private var balance = 25000

    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}"""
S.append(slide("Part 5 &middot; Why the child needs no @State of its own (section 7)", "Two sources of truth drift apart", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 320px;gap:28px;align-items:start">
      <div>{code("BalanceEditor.swift", WR, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{console("One activation", ["child balance now 26000", "parent still shows ₹25,000"], 13)}</div></div>
      <div>{crop("img/twosources.png", "Parent and child disagree", 320)}
        <div class="rule step" data-label="Principle" style="margin-top:12px">{ul("Make ownership <b>explicit</b>", "Shared state lives at a <b>shared level</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'The incorrect design: the editor declares its own @State balance, starting at 25,000, next to the parent&rsquo;s. We activated Add once.'),
                  ('SAY', 'Click: the child&rsquo;s balance became 26,000; the parent still shows ₹25,000. Two sources of truth, and they have already diverged.'),
                  ('SAY', 'Click: the principle: make state ownership explicit. When several views read or change the same local state, put it at a shared level, here ContentView, and pass values or bindings down.'),
                  ('CONNECT', 'Build the real editor.'))))

# ================================================================== Part 6 (8-10)
divider(6, "NPay&rsquo;s BalanceEditor", "Milestone 2.9", 'An editor with − and +, wired to ContentView&rsquo;s state.', 'The code.')
ED = """struct BalanceEditor: View {
    @Binding var balance: Int

    var body: some View {
        VStack(spacing: 12) {
            Text("Demo Balance Editor")
                .font(.headline)
            HStack(spacing: 12) {
                Button("− ₹1,000") {
                    balance = max(0, balance - 1000)
                }
                .buttonStyle(.bordered)
                Button("+ ₹1,000") {
                    balance += 1000
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}"""
S.append(slide("Part 6 &middot; Create BalanceEditor (section 8)", "Two buttons, one binding", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:28px;align-items:start">
      {code("BalanceEditor.swift", ED, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("max(0, balance - 1000)", ul("The demo balance never goes <b>negative</b>"))}
        <div class="step">{console("Started at ₹500: − , −", ["BalanceEditor body: 0", "balance now 0", "(second −: still 0, no new update)"], 13)}</div>
        <div class="rule step" data-label="Real payments">{ul("Validation belongs in trusted <b>domain and backend</b> logic", "Not only in UI controls")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The real editor: a headline, then an HStack with a bordered minus button and a prominent plus button, both writing through the binding. Minus uses max(0, balance - 1000) so the demo balance never goes below zero.'),
                  ('SAY', 'Click: we started an editor at ₹500 and activated minus twice. The first press clamped to 0. The second asked for max(0, -1000), which is 0 again: the value did not change, and no further update was printed.'),
                  ('SAY', 'Click: a production note. A UI clamp is a convenience. In a real payment system, validation belongs in trusted domain and backend logic, never only in a button.'),
                  ('CONNECT', 'Wire it into ContentView.'))))

P = [box(190, 0, 300, 52, 'ContentView', '@State balance', None, 'lit', 'layers'),
     wire('M270 56V84H160V110' + head(160, 110, 'd')), wire('M410 56V84H520V110' + head(520, 110, 'd')),
     box(0, 116, 320, 56, 'BalanceCard', 'balance · Int, read only', None, '', 'file'),
     box(360, 116, 320, 56, 'BalanceEditor', '$balance · Binding, read + write', None, '', 'link')]
S.append(slide("Part 6 &middot; Integrate and run (sections 9&ndash;10, 17)", "A value to the card, a binding to the editor", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 180px 180px;gap:24px;align-items:start">
      <div>{svg('0 0 680 172', 'ContentView passes a value to BalanceCard and a binding to BalanceEditor', 'int', P, 'max-height:200px')}
        <div class="gap"></div>
        {card("ContentView now", ul("<code>ScrollView</code> around the <code>VStack</code>", "Header, card, <b>editor</b>, quick actions"))}
        <div class="gap"></div>
        <div class="rule step" data-label="Verify">{ul("+ updates the card; − decreases it, never below 0")}</div></div>
      {PHONE("img/final.png", "Launch: ₹25,000", 180)}
      <div class="step">{PHONE("img/taps.png", "+, +, −: ₹26,000", 180)}</div>
    </div>
  </div>""", notes(('SAY', 'ContentView already owns @State balance and passes balance, the value, to BalanceCard. Now it also passes $balance, a binding, to BalanceEditor. One source of truth, two consumers: the card reads, the editor reads and writes.'),
                  ('SAY', 'The complete code wraps the screen&rsquo;s VStack in a ScrollView so the growing interface stays usable on smaller iPhones; the next lesson looks at scrolling containers. The full code is in the lesson text. On the right, the real app at launch, and click, after plus, plus, minus: ₹26,000.'),
                  ('SAY', 'That is the text&rsquo;s final checkpoint: plus updates the card, minus decreases it without going below zero.'),
                  ('CONNECT', 'Bindings can also be built by hand.'))))

# ================================================================== Part 7 (11, 14)
divider(7, "Custom bindings", "Binding(get:set:)", 'A binding is just a read and a write. Write them yourself.', 'By hand.')
MB = """BalanceEditor(
    balance: Binding(
        get: {
            balance
        },
        set: { newValue in
            balance = newValue
        }
    )
)"""
SAFE = """private var safeBalance: Binding<Int> {
    Binding(
        get: {
            balance
        },
        set: { newValue in
            balance = max(0, newValue)
        }
    )
}
// BalanceEditor(balance: safeBalance)"""
S.append(slide("Part 7 &middot; Build a binding manually (sections 11, 14)", "Explicit get and set, with validation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Like $balance", MB, "font-size:13.5px")}
        <div class="step" style="margin-top:10px">{console("+ through it", ["manual binding set 26000", "BalanceCard body: 26000"], 13)}</div></div>
      <div>{code("Validating binding", SAFE, "font-size:13px")}
        <div class="step" style="margin-top:10px">{console("A child that doesn&rsquo;t clamp, from ₹500: − , −", ["safeBalance set: asked -500, storing 0", "safeBalance set: asked -1000, storing 0"], 13)}</div></div>
    </div>
    <div class="rule step" data-label="Use sparingly" style="margin-top:10px">{ul("Prefer plain <code>$balance</code>; UI validation &ne; financial validation")}</div>
  </div>""", notes(('SAY', 'A binding is a read and a write, so you can build one with Binding(get:set:): get returns the parent&rsquo;s balance, set stores the new value. That is conceptually the same as passing $balance. Click: we activated plus through it: our set closure ran with 26,000 and the card showed 26,000. It printed Binding of Int, the same type as $balance.'),
                  ('SAY', 'Custom bindings can also transform or validate. safeBalance clamps every write to zero or above. We gave it to a deliberately naive child that subtracts 1,000 with no check, starting from ₹500. Click: the child asked for -500, the binding stored 0; asked for -1,000, stored 0. The child never knew about the rule; the binding intercepted the write.'),
                  ('SAY', 'Click: two cautions. Do not add custom bindings where $balance is enough. And this is UI behaviour, not financial security: real payment rules are enforced by trusted domain and backend systems.'),
                  ('CONNECT', 'Last: how much access should each child get?'))))

# ================================================================== Part 8 (15-17)
divider(8, "Access and debugging", "Only the access needed", 'Value for readers; binding for writers.', 'Compare.')
RO = """struct BalanceCard: View {      // reads
    let balance: Int
    var body: some View {
        Text("₹\\(balance)")
    }
}

struct BalanceEditor: View {    // reads and writes
    @Binding var balance: Int
    var body: some View {
        Button("Add ₹1,000") {
            balance += 1000
        }
    }
}"""
S.append(slide("Part 8 &middot; Read-only value vs binding (sections 15&ndash;16)", "Give a child only the access it needs", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Two children", RO, "font-size:13.5px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Rule", ul("Only <b>displays</b> it: pass a <b>value</b>", "Must <b>modify</b> parent state: pass a <b>binding</b>", "Data flow stays understandable"))}
        <div class="step">{card("In Xcode", ul("Breakpoint on <code>balance += 1000</code> in the editor", "Tap + ₹1,000; inspect; continue", "The card shows the new amount"))}</div>
        <div class="rule step" data-label="Observe">{ul("The <b>parent&rsquo;s</b> state changed", "No copy in the child")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Two children, intentionally different. BalanceCard only displays, so it gets a let value. BalanceEditor modifies parent-owned state, so it gets a @Binding.'),
                  ('SAY', 'The rule: give a child only the access it needs. If it only displays information, pass a value; if it must change parent-owned local state, pass a binding. That keeps ownership and data flow easy to follow.'),
                  ('SAY', 'Click: the debugging check from Section 15: a breakpoint on balance += 1000 in the editor, tap plus, inspect, continue, and the card updates. Click: what you are confirming is what our console showed: the child wrote through the binding, the parent&rsquo;s state changed, and no separate copy exists in the child.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.9', (), [("link", "$balance is a Binding", "the projected value of @State"),
                     ("gear", "Bindings forward writes", "nonmutating set; no ownership"),
                     ("layers", "One owner, right access", "value to readers, binding to writers")],
         'Three things to remember. $balance is @State&rsquo;s projected value, a Binding of Int, and a child declares @Binding to receive it. A binding owns nothing: its nonmutating setter forwards each write to the parent&rsquo;s storage, which is why it works inside a view struct. And keep one owner for each piece of state, passing a value to children that only read and a binding to children that write.')

review_divider(10)
review([("layers", "Choose one", "Who owns the balance in our NPay design?",
         "Who owns the balance in our NPay design?<br>A. <code>ContentView</code><br>B. <code>BalanceEditor</code><br>C. Both, independently", "A",
         "ContentView&rsquo;s @State; the editor only has a binding to it.",
         "Thinking whoever writes, owns.", "Some pick B.", None),
        ("link", "Choose one", "What is the type of $balance?",
         "What is the type of <code>$balance</code>?<br>A. <code>Int</code><br>B. <code>Binding&lt;Int&gt;</code><br>C. <code>State&lt;Int&gt;</code>", "B",
         "Printed in the simulator; it is State&rsquo;s projectedValue.",
         "Confusing it with the wrapper, State.", "Some pick C.", None),
        ("gear", "Question", "Does @Binding own the underlying value?",
         "Does <code>@Binding</code> own the underlying value?", "No",
         "It forwards reads and writes to storage owned elsewhere.",
         "Picturing a copy inside the child.", "Some say yes.", None),
        ("diff", "Choose one", "What happens when BalanceEditor changes balance?",
         "What happens when <code>BalanceEditor</code> changes <code>balance</code>?<br>A. Only the child updates<br>B. The parent-owned state changes<br>C. A new independent balance is created", "B",
         "Both BalanceCard and BalanceEditor re-evaluated with the same new value.",
         "Expecting a local change.", "Some pick A.", None),
        ("code", "Choose one", "Why can @Binding work inside a view struct?",
         "Why can <code>@Binding</code> work inside a SwiftUI struct?<br>A. Its setter is nonmutating and writes through<br>B. It turns the struct into a class<br>C. It disables type checking", "A",
         "SDK: <code>wrappedValue { get nonmutating set }</code>; our SimpleBinding wrote through a <code>let</code>.",
         "Thinking the struct must become mutable.", "Some pick B.", None),
        ("frame", "Choose one", "Main risk of @State in both parent and child?",
         "What is the main risk of duplicating <code>@State</code> in parent and child?<br>A. Two inconsistent sources of truth<br>B. A compiler crash<br>C. Automatic database writes", "A",
         "Child ₹26,000, parent ₹25,000 after one tap.",
         "Thinking SwiftUI keeps them in sync.", "Most pick A.", None),
        ("eye", "Choose one", "What does Binding(get:set:) provide?",
         "What does <code>Binding(get:set:)</code> provide?<br>A. Explicit read and write closures<br>B. A new process<br>C. Automatic persistence", "A",
         "safeBalance&rsquo;s setter clamped −500 to 0 before storing.",
         "Thinking bindings are magic.", "Most pick A.", None),
        ("file", "Choose one", "Should a display-only child get a @Binding?",
         "Should a child receive <code>@Binding</code> if it only displays a value?<br>A. Always<br>B. Usually no", "B",
         "Pass a value: give only the access needed.",
         "Handing out write access by default.", "Some pick A.", None),
        ("diff", "Predict the result", "Balance ₹500, tap − ₹1,000 twice: result?",
         "The balance is ₹500. You tap <b>− ₹1,000</b> twice (it uses <code>max(0, balance - 1000)</code>). What does it show?<br>A. −₹1,500<br>B. ₹0<br>C. −₹500", "B",
         "First press clamps to 0; the second stays 0.",
         "Forgetting the clamp.", "Some pick A.", None),
        ("db", "Question", "From 2.8: does @State survive app termination?",
         "From Lesson 2.8: does the <code>@State</code> balance survive if NPay is terminated?", "No",
         "@State is in-memory UI state; persistence comes later.",
         "Confusing &ldquo;survives updates&rdquo; with &ldquo;saved&rdquo;.", "Some say yes.", "Spaced review from Lesson 2.8.")])

S.append(next_slide('2.9', [("2.10", "ForEach, List &amp; collection identity", "a transaction model and NPay&rsquo;s first history: Identifiable, stable IDs")],
                    'Next lesson introduces a real transaction model and NPay&rsquo;s first transaction history: ForEach, List, Identifiable, stable IDs, view reuse, collection updates, and why unstable identity causes SwiftUI bugs, which connects straight back to 2.8&rsquo;s identity experiment.'))

S.append(lab_slide('2.9', "Share one balance", "Predict, run, verify.",
                   ["Try <code>let balance</code>, then <code>var</code>, in the child; read both errors.",
                    "Switch to <code>@Binding</code>; pass <code>$balance</code>.",
                    "Give the child its own <code>@State</code>; watch them diverge.",
                    "Build NPay&rsquo;s <code>BalanceEditor</code>; tap +, +, −.",
                    "Pass <code>safeBalance</code> to a child that doesn&rsquo;t clamp.",
                    "Breakpoint on <code>balance += 1000</code>; inspect."],
                   "", 'Expected, as in our runs: "&lsquo;balance&rsquo; is a &lsquo;let&rsquo; constant", then "&lsquo;self&rsquo; is immutable"; with its own @State the child shows 26,000 while the parent shows 25,000; +, +, − leaves ₹26,000 on the card; safeBalance turns −500 into 0; at the breakpoint the editor is about to write through the binding and the card updates after you continue.',
                   side=f'<div>{card("You hand in", ul("Both compiler errors, explained", "A screenshot of the diverged copies", "Console output for safeBalance"))}</div>'))

end_slide('2.9', '@Binding: How Two<br>SwiftUI Views Share State', 'Lesson 2.10 &mdash; ForEach, List &amp; Collection Identity',
          'You can now explain why a passed value cannot change its parent, what @Binding and $balance are, how a binding forwards writes through a nonmutating setter without owning anything, why duplicated @State breaks the single source of truth, how to build and validate a binding by hand, and how to give each child only the access it needs.',
          'Next, Lesson 2.10: ForEach, List and collection identity. A transaction model and NPay&rsquo;s first transaction history, and why stable identity matters.')

write_deck(OUT29, '2.9', '@Binding', '@Binding')
