"""Generates decks/unit-1/lesson-1.5/index.html from the Lesson 1.5 text (PocketBank -> NPay).
The text's 12 sections are grouped into 8 Parts (see the lesson's "Deck changes")."""
import html, os, re, sys
OUT15 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'

title_slide('1.5', 'Structs vs Classes:<br>Value &amp; Reference Semantics',
            'When should a type be a <b>struct</b>, and when a <b>class</b>?',
            'Last lesson: functions and closures. Today, one of Swift&rsquo;s most important design decisions: when to create a struct and when to create a class. It comes up in almost every serious iOS app: models, SwiftUI state, ViewModels and shared services. We learn it through one NPay story.')
outcomes_slide('1.5', [("diff", "<b>Value</b> versus <b>reference</b> semantics"),
                       ("layers", "The full <b>struct vs class</b> comparison"),
                       ("lock", "<code>mutating</code> and <b>initializers</b>"),
                       ("eye", "<b>Identity</b> (<code>===</code>) versus <b>equality</b> (<code>==</code>)"),
                       ("memory", "<b>Copy-on-write</b>, ARC and SwiftUI views"),
                       ("check", "Choose struct or class for NPay&rsquo;s <b>model</b>")])
where_slide('1.5', 'Today: values or shared objects', (),
            'Lesson 1.4: closures are values that capture what they use; a strong capture can keep an object alive.',
            'Struct or class: what assignment means, and how to choose for each NPay type.',
            'Last lesson we saw closures capture their surroundings, and that capturing a class instance strongly can keep it alive. That only happens with reference types. Today we look at that difference head on: value types and reference types, and how to choose between them.',
            'Start with two NPay screens.')

# ================================================================== Part 1 (text 1)
divider(1, "Two screens, one account", "Should a change show up everywhere?", 'NPay shows the same account on the dashboard and on the transfer screen. The transfer screen changes its balance. What happens on the dashboard?', 'It depends on the type.')
V = lambda x, y, name, l=None, cls='': box(x, y, 250, 70, name, '&#8377;25,000', l, cls, 'phone')
P = ['<text class="mono" x="255" y="14" text-anchor="middle">STRUCT &middot; EACH SCREEN HOLDS A VALUE</text>',
     V(0, 30, 'Dashboard'), V(280, 30, 'Transfer screen'),
     fade('1+', box(280, 30, 250, 70, 'Transfer screen', '&#8377;20,000', None, 'lit', 'phone')),
     '<text class="mono" x="866" y="14" text-anchor="middle">CLASS &middot; BOTH SCREENS SHARE ONE OBJECT</text>',
     V(606, 30, 'Dashboard'), V(886, 30, 'Transfer screen'),
     box(686, 170, 360, 64, 'One Account instance', '&#8377;25,000', None, '', 'memory'),
     wire('M731 104L800 164' + head(800, 164, 'd')), wire('M1011 104L942 164' + head(942, 164, 'd')),
     fade('1+', box(606, 30, 250, 70, 'Dashboard', '&#8377;20,000', None, 'lit', 'phone') + box(886, 30, 250, 70, 'Transfer screen', '&#8377;20,000', None, 'lit', 'phone')
          + box(686, 170, 360, 64, 'One Account instance', '&#8377;20,000', None, 'lit', 'memory'))]
S.append(slide("Part 1 &middot; The problem (section 1)", "Change the transfer screen. What does the dashboard show?", f"""  <div class="body">
    {svg('0 0 1136 234', 'With a struct each screen has its own balance; with a class both screens show the shared instance', 'screens', P, 'max-height:270px')}
    {cues(1)}
    <div class="gap-lg"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("Value semantics", ul("Independent <b>logical values</b>", "Change one, the other stays"))}
      {card("Reference semantics", ul("Shared <b>object identity</b>", "Change it once, everyone sees it"))}
    </div>
  </div>""", notes(('SAY', 'NPay shows the account in two places: the dashboard and the transfer screen. Both start at ₹25,000. The transfer screen changes its balance to ₹20,000. Should the dashboard change too?'),
                  ('SAY', 'Click: with a struct, each screen holds its own value, so only the transfer screen shows ₹20,000. With a class, both screens refer to one Account instance, so both now show ₹20,000. This is a conceptual picture, not real SwiftUI synchronization or a banking transaction.'),
                  ('SAY', 'Click: two fundamental ideas. Value semantics: independent logical values. Reference semantics: shared object identity.'),
                  ('CONNECT', 'Now in code.'))))

# ================================================================== Part 2 (text 2-3)
divider(2, "Value and reference in code", "Same lines, one keyword different", 'struct versus class, with the same assignment and the same change.', 'Side by side.')
STRUCT = """struct Account {
    var balanceMinor: Int64       // paise
}

var accountA = Account(balanceMinor: 2_500_000)
var accountB = accountA
accountB.balanceMinor = 2_000_000
print(accountA.balanceMinor)      // 2500000
print(accountB.balanceMinor)      // 2000000"""
CLASS = """final class Account {
    var balanceMinor: Int64
    init(balanceMinor: Int64) {
        self.balanceMinor = balanceMinor
    }
}
let accountA = Account(balanceMinor: 2_500_000)
let accountB = accountA
accountB.balanceMinor = 2_000_000
print(accountA.balanceMinor)      // 2000000"""
VAL = [box(0, 32, 236, 62, 'accountA', '&#8377;25,000', None, '', 'file'),
       wire('M244 63H308' + head(308, 63, 'r'), None, 'dash'), '<text class="sm" x="276" y="52" text-anchor="middle">copy</text>',
       box(316, 32, 236, 62, 'accountB', '&#8377;20,000', None, 'lit', 'file')]
REF = [box(0, 0, 190, 54, 'accountA', 'reference', None, '', 'link'), box(0, 72, 190, 54, 'accountB', 'reference', None, '', 'link'),
       wire('M194 27L258 55' + head(258, 55, 'r')), wire('M194 99L258 71' + head(258, 71, 'r')),
       box(266, 28, 286, 70, 'One Account instance', '&#8377;20,000', None, 'lit', 'memory')]
S.append(slide("Part 2 &middot; Struct and class (sections 2&ndash;3)", "A copy, or a second name", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("StructAccount.swift", STRUCT, "font-size:14px;min-height:268px")}
        <div class="step" style="margin-top:12px">{svg('0 0 552 126', 'Struct: accountA keeps 25,000; accountB, an independent copy, holds 20,000', 'vv', VAL)}
          {out("<b>Two values.</b> Changing B left A alone.", '')}</div></div>
      <div>{code("ClassAccount.swift", CLASS, "font-size:14px;min-height:268px")}
        <div class="step" style="margin-top:12px">{svg('0 0 552 126', 'Class: accountA and accountB refer to one instance holding 20,000', 'rr', REF)}
          {out("<b>One instance.</b> Both names see &#8377;20,000.", '')}</div></div>
    </div>
  </div>""", notes(('SAY', 'Both start at ₹25,000, 2,500,000 paise. accountB is assigned from accountA and changed to ₹20,000.'),
                  ('ASK', 'Before the clicks: what does accountA print in each version?'),
                  ('SAY', 'Click: the struct. Assignment produced an independent logical value: accountA still prints 2,500,000. Value semantics does not mean Swift duplicates every byte immediately; it can share storage and copy only when needed, as we will see in Part 6. The guarantee is that changing one value never changes another.'),
                  ('SAY', 'Click: the class. accountA and accountB are two references to the same object, so accountA prints 2,000,000. And notice accountB is a let: let stops you pointing it at a different object, not changing the object, exactly as in Lesson 1.2.'),
                  ('CONNECT', 'The full comparison in one table.'))))

# ================================================================== Part 3 (text 4)
divider(3, "Struct versus class", "The complete comparison", 'Eight differences you will meet in practice.', 'One table.')
CMP = [("Semantics", "Value", "Reference"), ("Identity", "No object identity", "Object identity (<code>===</code>)"),
       ("Inheritance", "No class inheritance", "Supports inheritance"), ("ARC", "Not ARC-managed as an instance", "Instances managed by ARC"),
       ("Deinitializer", "No <code>deinit</code>*", "Supports <code>deinit</code>"), ("Mutating methods", "Need <code>mutating</code>", "No <code>mutating</code> keyword"),
       ("Memberwise init", "Synthesized", "Write <code>init</code> yourself"), ("Typical use", "Data models and values", "Shared identity, services")]
trs = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in CMP)
S.append(slide("Part 3 &middot; Comparison (section 4)", "Eight differences", f"""  <div class="body">
    <table class="tbl compact" style="font-size:18px"><thead><tr><th>Feature</th><th>Struct</th><th>Class</th></tr></thead><tbody>{trs}</tbody></table>
    <p class="small muted" style="margin:8px 0 0">* Non-copyable structs (<code>~Copyable</code>) can have a <code>deinit</code>; Lesson 1.8.</p>
    <div class="gap"></div>
    <div class="misconception step">&ldquo;Struct = stack, class = heap&rdquo; is not the rule. The distinction is <b>semantics</b>.</div>
  </div>""", notes(('SAY', 'Row by row. Structs have value semantics, classes reference semantics. Classes have object identity, checked with three equals signs. Only classes support inheritance. ARC manages class instances; a struct is not ARC-managed as an instance, though any class references inside it are. Classes support deinit. A struct method that changes stored properties needs mutating; classes have no such keyword. Structs get a synthesized memberwise initializer; classes need you to write init. And typically: structs for data models and values, classes for shared identity and reference-based services.'),
                  ('SAY', 'One refinement: since Swift 5.9, non-copyable structs, marked tilde Copyable, can have a deinit. Ordinary structs cannot. Lesson 1.8 covers ownership.'),
                  ('SAY', 'Click: do not teach struct equals stack and class equals heap as a rule. Where values are stored is an implementation detail; the language guarantee is about semantics.'),
                  ('CONNECT', 'Two rows deserve a closer look: mutating and initializers.'))))

# ================================================================== Part 4 (text 5-6)
divider(4, "Mutation and initializers", "mutating, and who writes init", 'A struct method that changes the value must say so; a class must set up its own state.', 'Both, with real compiler errors.')
MUT = """struct Account {
    var balanceMinor: Int64

    mutating func deposit(_ amountMinor: Int64) {
        balanceMinor += amountMinor
    }
}

var account = Account(balanceMinor: 2_500_000)
account.deposit(500_000)
print(account.balanceMinor)       // 3000000"""
INIT = """struct Customer {                 // memberwise init: free
    let id: String
    var name: String
}
let customer = Customer(id: "C1001", name: "Ravi")

class CustomerRecord {            // no init written
    let id: String
    var name: String
}"""
S.append(slide("Part 4 &middot; mutating and init (sections 5&ndash;6)", "Say when you change it; say how it starts", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Deposit.swift", MUT, "font-size:14px;min-height:262px")}
        <div class="step" style="margin-top:12px">{card("Without mutating", '<p style="margin:4px 0 0">' + err("left side of mutating operator isn&rsquo;t mutable: &lsquo;self&rsquo; is immutable") + '</p>')}</div></div>
      <div>{code("Init.swift", INIT, "font-size:14px;min-height:262px")}
        <div class="step" style="margin-top:12px">{card("Class without init", '<p style="margin:4px 0 0">' + err("class &lsquo;CustomerRecord&rsquo; has no initializers") + '</p>')}</div></div>
    </div>
  </div>""", notes(('SAY', 'deposit changes the struct&rsquo;s stored balance, so it is marked mutating. Depositing ₹5,000 to ₹25,000 gives 3,000,000 paise. The method is changing the value represented by the instance, and mutating makes that intent explicit.'),
                  ('SAY', 'Click: remove mutating and the compiler says: left side of mutating operator isn&rsquo;t mutable, self is immutable.'),
                  ('SAY', 'Right side: a struct gets a synthesized memberwise initializer for free, so Customer(id:name:) just works. A class with stored properties that have no default values must write its own init. Click: without it, class CustomerRecord has no initializers. Designated and convenience initializers and two-phase class initialization come in a later lesson.'),
                  ('CONNECT', 'Classes have identity. What does that mean?'))))

# ================================================================== Part 5 (text 7)
divider(5, "Identity versus equality", "The same object, or the same data?", 'Two customers both named Ravi. Are they the same?', 'It depends what you ask.')
IDN = """final class Customer {
    let name: String
    init(name: String) { self.name = name }
}

let a = Customer(name: "Ravi")
let b = Customer(name: "Ravi")
let c = a

print(a === b)   // false
print(a === c)   // true"""
EQ = """struct CustomerValue: Equatable {
    let name: String
}

print(CustomerValue(name: "Ravi") ==
      CustomerValue(name: "Ravi"))   // true"""
P = [box(0, 0, 140, 50, 'a', '', None, '', 'link'), box(0, 70, 140, 50, 'c', '', None, '', 'link'), box(0, 150, 140, 50, 'b', '', None, '', 'link'),
     wire('M144 25L226 50' + head(226, 50, 'r')), wire('M144 95L226 70' + head(226, 70, 'r')), wire('M144 175H226' + head(226, 175, 'r')),
     box(232, 26, 320, 66, 'Instance 1', 'name: Ravi', None, 'lit', 'memory'), box(232, 142, 320, 66, 'Instance 2', 'name: Ravi', None, '', 'memory')]
S.append(slide("Part 5 &middot; === and == (section 7)", "Same object versus same value", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Identity.swift", IDN, "font-size:14px")}
        <div class="gap"></div>
        {svg('0 0 552 208', 'a and c refer to instance 1; b refers to instance 2; both hold Ravi', 'idn', P, 'max-height:200px')}</div>
      <div class="step">{code("Equality.swift", EQ, "font-size:14px")}
        <div class="gap"></div>
        {card("===", ul("Same <b>instance</b>? Classes only", "Ignores the data"))}
        <div class="gap"></div>
        {card("==", ul("Same <b>value</b>? Needs <code>Equatable</code>", "Compares the data"))}</div>
    </div>
  </div>""", notes(('SAY', 'a and b are two Customer objects that both hold Ravi. c is just another name for a. Three equals signs asks: do these two references identify the same instance? a === b is false: same data, different objects. a === c is true. The picture shows it: a and c point to instance 1, b to instance 2.'),
                  ('SAY', 'Click: for equality of values, types conform to Equatable. Two CustomerValue structs with the same name are equal, ==, true. Structs have no identity to compare; they are their data.'),
                  ('CONNECT', 'If structs are copied on assignment, isn&rsquo;t that expensive?'))))

# ================================================================== Part 6 (text 8)
divider(6, "Copy-on-write", "Copy only when you change it", 'Arrays have value semantics. Does that mean every assignment copies every element?', 'Measure it.')
COW = """var a = [10, 20, 30]
var b = a          // shares a's buffer

b.append(40)       // b gets its own buffer

print(a)   // [10, 20, 30]
print(b)   // [10, 20, 30, 40]"""
BUF = lambda x, y, t, sub, l=None, cls='': box(x, y, 300, 56, t, sub, l, cls, 'memory')
P = [box(0, 0, 150, 50, 'a', '', None, '', 'link'), box(0, 120, 150, 50, 'b', '', None, '', 'link'),
     BUF(250, 0, '[10, 20, 30]', 'buffer 1'),
     wire('M154 25H246' + head(246, 25, 'r')),
     fade('0', wire('M154 145L246 40' + head(246, 40, 'r'), None, 'lit') + '<text class="sm" x="210" y="80" text-anchor="middle">shared</text>'),
     fade('1+', wire('M154 145H246' + head(246, 145, 'r'), None, 'lit') + BUF(250, 120, '[10, 20, 30, 40]', 'buffer 2: copied on append', None, 'lit'))]
EV = [("Before <code>b.append(40)</code>", "<b>true</b>: one shared buffer"), ("After", "<b>false</b>: separate buffers")]
trs = ''.join(f'<tr><td>{x}</td><td>{y}</td></tr>' for x, y in EV)
S.append(slide("Part 6 &middot; Copy-on-write (section 8)", "Share until someone writes", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:center">
      {code("CopyOnWrite.swift", COW, "font-size:16px")}
      {svg('0 0 552 176', 'a and b share one buffer until b appends; then b gets its own copy', 'cow', P, 'max-height:200px')}
    </div>
    {cues(1)}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div class="step"><p class="small muted" style="margin:0 0 4px">Measured: do <code>a</code> and <code>b</code> use the same buffer address?</p>
        <table class="tbl"><tbody>{trs}</tbody></table></div>
      <div class="step">{card("Why it matters", ul("Value semantics, <b>without</b> copying on every assignment", "One reason Swift favours structs for models", "Built into <code>Array</code>, <code>Dictionary</code>, <code>Set</code>, <code>String</code>"))}</div>
    </div>
  </div>""", notes(('SAY', 'a and b are arrays, so they have value semantics: after b.append(40), a is still [10, 20, 30]. But Swift does not copy the elements on var b = a. Both arrays start out sharing one underlying buffer.'),
                  ('SAY', 'Click: when b is mutated and the buffer is shared, b first gets its own copy. That is copy-on-write: copy only when someone writes.'),
                  ('SAY', 'Click: we measured it, using withUnsafeBufferPointer to read each array&rsquo;s buffer address. Before the append: the same address, true. After: different, false. Exact storage behaviour is an implementation detail; the semantics are the guarantee.'),
                  ('SAY', 'Click: copy-on-write gives you the simplicity of value semantics with efficient storage reuse. It is built into the standard collections, Array, Dictionary, Set and String; your own structs get it only if you implement it. That is one reason Swift encourages value types for data models.'),
                  ('CONNECT', 'Reference types bring something structs never need: lifetime management.'))))

# ================================================================== Part 7 (text 9-10)
divider(7, "ARC and SwiftUI", "Lifetimes for classes, descriptions for views", 'Classes need ARC. SwiftUI views are structs. How do these fit?', 'One at a time.')
ARC = """final class Customer {
    let name: String
    init(name: String) {
        self.name = name; print("Created")
    }
    deinit { print("Destroyed") }
}
var customer: Customer? = Customer(name: "Ravi")
customer = nil"""
VIEW = """import SwiftUI

struct BalanceView: View {
    let balanceText: String   // from the ViewModel

    var body: some View {
        Text(balanceText)
    }
}"""
S.append(slide("Part 7 &middot; ARC and SwiftUI (sections 9&ndash;10)", "Classes live and die; views describe", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Lifetime.swift", ARC, "font-size:14px;min-height:232px")}
        <div style="margin-top:12px">{card("Prints", mono("Created<br>Destroyed") + ul("Last strong reference gone: <b>deinit</b>", "A cycle prevents it (0.6, 1.4)"))}</div></div>
      <div class="step">{code("BalanceView.swift", VIEW, "font-size:14px;min-height:232px")}
        <div class="gap"></div>
        {card("SwiftUI views are structs", ul("A <b>description</b> of the UI, recreated often", "Lasting state is kept by SwiftUI (Unit 03)"))}</div>
    </div>
  </div>""", notes(('SAY', 'Classes introduce reference ownership. Create a Customer and it prints Created; set the only reference to nil and ARC deinitializes it: Destroyed. Strong reference cycles would prevent that, as in Lesson 0.6 and the closure cycle in Lesson 1.4. Now you can see why cycles are a reference-type problem.'),
                  ('SAY', 'Click: SwiftUI views are usually structs. BalanceView takes ready-formatted text from the ViewModel, as in Lesson 0.2, and describes a Text. That does not mean SwiftUI redraws the whole screen whenever a struct changes: view values are descriptions of the desired interface, and SwiftUI manages identity, state and rendering itself.'),
                  ('SAY', 'A view struct can be recreated very often, so lasting view state is kept separately by SwiftUI. That is why view identity and property wrappers matter so much in Unit 03.'),
                  ('CONNECT', 'So how do you choose?'))))

# ================================================================== Part 8 (text 11-12)
divider(8, "Choosing for NPay", "Struct by default; class when identity matters", 'Five NPay types. Struct or class?', 'Decide, then check.')
DEC = [("Transaction record", "struct", "a value representing data"), ("Currency amount", "struct", "a value; equal amounts are interchangeable"),
       ("SwiftUI screen description", "struct", "a cheap description SwiftUI recreates"),
       ("Observable ViewModel", "class", "one shared, observed instance (<code>@Observable</code> is for classes)"),
       ("Shared session manager", "class", "identity and shared mutable session state")]
trs = ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td><td>{c}</td></tr>' for a, b, c in DEC)
S.append(slide("Part 8 &middot; Decision (section 11)", "Struct or class?", f"""  <div class="body">
    <table class="tbl"><thead><tr><th>NPay type</th><th>Choose</th><th>Because</th></tr></thead><tbody>{trs}</tbody></table>
    <div class="gap"></div>
    <div class="rule step" data-label="Practical rule">{ul("Start with a <b>struct</b> for independent values", "Choose a <b>class</b> when identity or shared ownership is <b>part of the design</b>", "A guideline, not a law")}</div>
  </div>""", notes(('ASK', 'Before the table: struct or class for each of the five?'),
                  ('SAY', 'A transaction record is naturally a value representing data: struct. A currency amount: struct; two equal amounts are interchangeable. A SwiftUI screen description: struct, recreated cheaply. An observable ViewModel: class; the screen observes one shared instance, and the @Observable macro works on classes. A shared session manager: class, because identity and shared mutable session state are the point.'),
                  ('SAY', 'Click: start with a struct when you need independent values; choose a class when reference identity or shared ownership is genuinely part of the design. A guideline, not an absolute law.'),
                  ('CONNECT', 'Here is that decision in NPay&rsquo;s model.'))))

MODEL = """struct Money: Equatable {
    let amountMinor: Int64       // paise
    let currency: String         // "INR"
}

struct Transaction: Equatable {
    let id: String
    let amount: Money
    let description: String
}

final class SessionManager {
    private(set) var isLoggedIn = false
    func login() { isLoggedIn = true }
    func logout() { isLoggedIn = false }
}"""
S.append(slide("Part 8 &middot; NPay model (section 12)", "Values for data, a class for the session", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:start">
      {code("Model.swift", MODEL, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Money, Transaction", ul("<b>Domain values</b>: structs", "Equatable: compare by value"))}
        {card("SessionManager", ul("A <b>service</b> with identity", "Shared, mutable session state", "<code>final</code>: no subclassing"), 'step')}
        <div class="tip step" data-label="Real banking">{ul("Stronger validation, secure sessions (Unit 07)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Money and Transaction are domain values, so they are structs, and Equatable so they compare by value. Money stores whole paise in Int64 plus a currency code, as in Lesson 1.2; Lesson 1.10 makes it a richer type.'),
                  ('SAY', 'Click: SessionManager is a service with identity and shared mutable state, so it is a class, final because nothing should subclass it. private(set) lets everyone read isLoggedIn but only the manager change it.'),
                  ('SAY', 'Click: a real banking implementation needs stronger domain validation and secure session handling; Unit 07 covers that.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.5', (), [("diff", "Values copy, references share", "semantics, not stack or heap"),
                     ("eye", "=== is identity, == is value", "only classes have identity"),
                     ("check", "Struct first", "class when identity is the point")],
         'Three things to remember. Values copy and references share: that is the real difference, not stack versus heap, and copy-on-write keeps values cheap. Identity versus equality: three equals signs asks whether two references are the same object, double equals asks whether two values are equal. And start with a struct; choose a class when identity or shared ownership is genuinely part of the design.')

review_divider(8)
review([("link", "Question", "Does assigning a class instance to another variable create a new instance?",
         "Does <code>let b = a</code> create a new instance when <code>a</code> is a class instance?", "No",
         "It copies the <b>reference</b>. <code>a</code> and <code>b</code> now identify the same object.",
         "Expecting a copy, as with structs.", "Some say yes.", None),
        ("diff", "Question", "Do structs guarantee independent logical values after assignment?",
         "After <code>var b = a</code> with a struct, are <code>a</code> and <code>b</code> independent logical values?", "Yes",
         "Changing one never changes the other, even if storage is shared until a write (copy-on-write).",
         "Thinking shared storage means shared values.", "Most say yes.", None),
        ("lock", "Question", "Does a let-bound class reference make every property immutable?",
         "Does <code>let account = Account(&hellip;)</code> make every property of a class instance immutable?", "No",
         "<code>let</code> fixes the reference. The instance&rsquo;s <code>var</code> properties can still change.",
         "Reading let as &ldquo;frozen object&rdquo;.", "Many say yes.", None),
        ("memory", "Question", "Does Swift Array use copy-on-write?",
         "Does Swift&rsquo;s <code>Array</code> use copy-on-write?", "Yes",
         "Copies share a buffer until one is mutated; we measured the same address before <code>append</code> and different after.",
         "Thinking every assignment copies all elements.", "Most say yes.", None),
        ("layers", "Question", "Should every iOS model be a class?",
         "Should every model type in an iOS app be a class?", "No",
         "Start with structs for values. Use classes where identity or shared ownership is part of the design.",
         "Bringing class-everything habits from other languages.", "Java developers may say yes.", None),
        ("check", "Choose one", "Which NPay type should be a class?",
         "Which of these should be a class?<br>A. <code>Money</code><br>B. A transaction record<br>C. An observable ViewModel<br>D. A SwiftUI screen description", "C",
         "The screen observes one shared ViewModel instance, and <code>@Observable</code> works on classes. The others are values.",
         "Picking the type that &ldquo;feels important&rdquo;.", "Some pick A.", None),
        ("eye", "Predict the output", "What does print(a === b, a === c) print?",
         "<code>let a = Customer(name: \"Ravi\")</code><br><code>let b = Customer(name: \"Ravi\")</code><br><code>let c = a</code><br><code>print(a === b, a === c)</code>", "false true",
         "Same data does not make the same object. <code>c</code> is another name for <code>a</code>.",
         "Expecting === to compare names.", "Some say true true.", None),
        ("code", "Predict the output", "What does the closure print after n changes?",
         "<code>var n = 1</code><br><code>let f = { print(n) }</code><br><code>n = 2</code><br><code>f()</code>", "2",
         "A closure captures the <b>variable</b>, not a snapshot of its value, so it sees the change.",
         "Expecting the value at creation time (1).", "Many say 1.", "Spaced review from Lesson 1.4.")])

S.append(next_slide('1.5', [("1.6", "Protocols, extensions &amp; protocol-oriented design", "<code>Equatable</code> and protocols for structs"),
                            ("1.8", "ARC, ownership &amp; memory management", "references, cycles, <code>~Copyable</code>"),
                            ("1.10", "NPay domain model, actor ledger &amp; tests", "a full <code>Money</code> value type"),
                            ("3.1", "View identity, lifetime &amp; state reset", "why view structs are cheap"),
                            ("3.2", "Observation: @Observable &amp; @Bindable", "the ViewModel as a class")],
                    'Values and references run through the rest of the course. 1.6 shows how protocols like Equatable work with structs; 1.8 goes deep on references, cycles and non-copyable types; 1.10 builds the full Money value type; and Unit 03 explains view identity and why the ViewModel is an observable class.'))

LAB = """struct Money: Equatable { let amountMinor: Int64; let currency: String }
struct Transaction: Equatable {
    let id: String
    var amount: Money
    let description: String
}
final class SessionManager {
    private(set) var isLoggedIn = false
    func login() { isLoggedIn = true }
    deinit { print("SessionManager destroyed") }
}"""
S.append(lab_slide('1.5', "Model NPay&rsquo;s types", "Build the model, then prove each claim from today with output.",
                   ["Copy a <code>Transaction</code>, change the copy: is the original unchanged? Is <code>==</code> false?",
                    "Give two &ldquo;screens&rdquo; one <code>SessionManager</code>; log in from one; check the other and <code>===</code>.",
                    "Hold the manager in an optional; set it to <code>nil</code>: does <code>deinit</code> print?",
                    "Copy an array of transaction ids; compare buffer addresses before and after an <code>append</code>."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab. Expected: t1 = Transaction(id: "T1", amount: Money(amountMinor: 50_000, currency: "INR"), description: "Rent"); var t2 = t1; t2.amount = Money(amountMinor: 60_000, currency: "INR") → t1 keeps 50000, t2 has 60000, t1 == t2 is false. let session = SessionManager(); let screenA = session; let screenB = session; screenB.login() → screenA.isLoggedIn is true and screenA === screenB is true. var maybe: SessionManager? = SessionManager(); maybe = nil prints "SessionManager destroyed". Buffer check: ids.withUnsafeBufferPointer { $0.baseAddress } == copy.withUnsafeBufferPointer { $0.baseAddress } is true before copy.append("T3") and false after. No force unwraps (Lesson 1.3).',
                   side=f'<div>{code("lab.swift", LAB, "font-size:13px")}<div class="gap"></div>{card("You hand in", ul("Four outputs, each next to the claim it proves"))}</div>'))

end_slide('1.5', 'Structs vs Classes:<br>Value &amp; Reference Semantics', 'Lesson 1.6 &mdash; Protocols, Extensions &amp; Protocol-Oriented Design',
          'You can now explain value versus reference semantics, compare structs and classes feature by feature, use mutating and initializers, tell identity from equality, describe copy-on-write, connect ARC to reference types and SwiftUI views to structs, and choose the right kind of type for NPay&rsquo;s model.',
          'Next, Lesson 1.6: protocols, extensions and protocol-oriented design, including how Equatable gave our structs ==.')

write_deck(OUT15, '1.5', 'Structs vs Classes', 'Structs vs Classes')
