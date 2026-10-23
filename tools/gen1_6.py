"""Generates decks/unit-1/lesson-1.6/index.html from the Lesson 1.6 text (PocketBank -> NPay).
The text's 13 sections are grouped into 8 Parts (see the lesson's "Deck changes")."""
import html, os, re, sys
OUT16 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'

title_slide('1.6', 'Protocols, Extensions &amp;<br>Protocol-Oriented Programming',
            'How can different types offer the <b>same capability</b> without a <b>shared parent class</b>?',
            'In Lesson 1.5 we learned structs versus classes. Now a new architectural problem: how can different Swift types provide the same capability without inheriting from the same parent class? That is where protocol-oriented programming comes in. We stay with NPay and see how protocols make an app flexible and testable.')
outcomes_slide('1.6', [("link", "Define a <b>protocol</b> and make types <b>conform</b>"),
                       ("layers", "Use <b>polymorphism</b> through a protocol"),
                       ("diff", "Protocols versus <b>class inheritance</b>"),
                       ("code", "<b>Extensions</b>, defaults, and a dispatch surprise"),
                       ("decision", "<b>Composition</b> with <code>&amp;</code>, and <code>any</code> vs <code>some</code>"),
                       ("check", "Protocols in <b>SwiftUI</b> and <b>dependency injection</b>")])
where_slide('1.6', 'Today: shared capabilities', (),
            'Lesson 1.5: structs are values, classes share identity; start with a struct.',
            'Protocols let structs and classes share a capability without a class hierarchy.',
            'Last lesson ended with a rule: start with a struct. But structs cannot inherit. So how do several struct types share a capability, such as paying? Today&rsquo;s answer is protocols, and it is the idea underneath SwiftUI&rsquo;s View and NPay&rsquo;s testable services.',
            'Start with NPay&rsquo;s payment screen.')

# ================================================================== Part 1 (1-2)
divider(1, "Protocols", "A contract, not an implementation", 'NPay supports three payment methods. Each works differently, but all must be able to pay.', 'Define the contract.')
P = [box(0, 0, 250, 60, 'UPI', '', None, '', 'phone'), box(290, 0, 250, 60, 'Card', '', None, '', 'key'), box(580, 0, 250, 60, 'Bank transfer', '', None, '', 'bank'),
     wire('M125 64L400 116' + head(400, 116, 'd')), wire('M415 64V116' + head(415, 116, 'd')), wire('M705 64L430 116' + head(430, 116, 'd')),
     box(240, 122, 350, 60, 'Common capability: pay', 'different implementations, one contract', None, 'lit', 'link')]
PROTO = """protocol PaymentMethod {
    func pay(amountMinor: Int64)
}"""
S.append(slide("Part 1 &middot; The problem (sections 1&ndash;2)", "Three payment methods, one contract", f"""  <div class="body">
    {svg('0 0 830 182', 'UPI, card and bank transfer all provide one common capability: pay', 'pm', P, 'max-height:220px')}
    <div class="gap-lg"></div>
    <div class="cols step" style="{TWO};gap:24px;align-items:center">
      {code("PaymentMethod.swift", PROTO, "font-size:18px")}
      {card("A protocol", ul("States <b>what</b> a conforming type must provide", "Says nothing about <b>how</b>", "Each type supplies its own implementation"))}
    </div>
  </div>""", notes(('SAY', 'NPay supports UPI, card and bank transfer. Each behaves differently, but all must support one operation: making a payment. The challenge is a common contract without forcing every payment method into one class hierarchy.'),
                  ('SAY', 'Click: a protocol defines requirements that conforming types must satisfy, a contract. PaymentMethod says any conforming type must provide pay(amountMinor:). It says nothing about how payment works; that belongs to each type. Amounts are in paise, as in earlier lessons.'),
                  ('CONNECT', 'Now make two types conform.'))))

# ================================================================== Part 2 (3-4)
divider(2, "Conformance and polymorphism", "One call, many implementations", 'Two structs promise the same capability. One function uses both.', 'Here they are.')
CONF = """struct UPIPayment: PaymentMethod {
    func pay(amountMinor: Int64) {
        print("UPI payment: ₹\\(amountMinor / 100)")
    }
}

struct CardPayment: PaymentMethod {
    func pay(amountMinor: Int64) {
        print("Card payment: ₹\\(amountMinor / 100)")
    }
}"""
POLY = """func processPayment(using method: any PaymentMethod,
                    amountMinor: Int64) {
    method.pay(amountMinor: amountMinor)
}

processPayment(using: UPIPayment(),
               amountMinor: 100_000)
processPayment(using: CardPayment(),
               amountMinor: 200_000)"""
S.append(slide("Part 2 &middot; Conformance (sections 3&ndash;4)", "Same contract, different behavior", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Payments.swift", CONF, "font-size:13px")}
        <div class="gap"></div>
        {card("Conformance", ul("Two <b>structs</b>, one protocol", "No class inheritance involved"))}</div>
      <div class="step">{code("Process.swift", POLY, "font-size:13px")}
        <div style="margin-top:12px">{card("Prints", mono("UPI payment: ₹1000<br>Card payment: ₹2000") + ul("Polymorphism: the caller depends on the <b>contract</b>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'UPIPayment and CardPayment both conform to PaymentMethod: each provides pay(amountMinor:), in its own way. Both are structs. Protocol conformance does not imply class inheritance.'),
                  ('SAY', 'Click: processPayment takes any value that conforms to PaymentMethod and calls pay. Pass a UPI payment and a card payment and each prints its own message: UPI payment ₹1000, Card payment ₹2000. That is polymorphism: different implementations through one interface.'),
                  ('SAY', 'The caller depends on a contract, not a concrete payment type. Adding BankTransferPayment needs no change to processPayment, and in tests you can pass a fake. Less coupling, easier to extend and test.'),
                  ('CONNECT', 'Protocols can require properties too.'))))

# ================================================================== Part 3 (5)
divider(3, "Property requirements", "{ get } and { get set }", 'A protocol can require data as well as behavior.', 'Readable, or readable and writable.')
PROP = """protocol BankAccount {
    var accountNumber: String { get }
    var balanceMinor: Int64 { get set }
}

struct SavingsAccount: BankAccount {
    let accountNumber: String   // { get }
    var balanceMinor: Int64     // { get set }
}"""
S.append(slide("Part 3 &middot; Properties (section 5)", "Readable, or readable and writable", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("BankAccount.swift", PROP, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("{ get }", ul("Must be <b>readable</b>", "A <code>let</code> or a <code>var</code> satisfies it"))}
        {card("{ get set }", ul("Must be readable <b>and writable</b>", "A <code>let</code> does not satisfy it"))}
        <div class="step">{card("balanceMinor as a let", '<p style="margin:4px 0 0">' + err("type &lsquo;SavingsAccount&rsquo; does not conform to protocol &lsquo;BankAccount&rsquo;") + '</p>')}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'BankAccount requires two properties. { get } means the property must be readable; { get set } means readable and writable. SavingsAccount satisfies both: a let accountNumber is readable, a var balanceMinor is readable and writable.'),
                  ('SAY', 'A read-only requirement can be satisfied by something that is also writable, but not the other way round.'),
                  ('SAY', 'Click: make balanceMinor a let and SavingsAccount no longer conforms: type SavingsAccount does not conform to protocol BankAccount.'),
                  ('CONNECT', 'How does this compare with class inheritance?'))))

# ================================================================== Part 4 (6)
divider(4, "Protocols versus inheritance", "Capabilities or a family tree", 'Two ways to share: a class hierarchy, or a capability.', 'Compare them.')
P = ['<text class="mono" x="270" y="14" text-anchor="middle">CLASS INHERITANCE</text>',
     box(160, 30, 220, 56, 'BasePayment', 'superclass', None, '', 'layers'), wire('M270 90V122' + head(270, 122, 'd')),
     box(160, 128, 220, 56, 'UPIPayment', 'subclass: one parent', None, '', 'phone'),
     '<text class="mono" x="866" y="14" text-anchor="middle">PROTOCOL CONFORMANCE</text>',
     box(596, 30, 260, 56, 'PaymentMethod', 'protocol', None, 'lit', 'link'), box(876, 30, 260, 56, 'Receipts', 'protocol', None, 'lit', 'file'),
     wire('M726 90L846 122' + head(846, 122, 'd'), None, 'dash'), wire('M1006 90L886 122' + head(886, 122, 'd'), None, 'dash'),
     box(756, 128, 220, 56, 'UPIPayment', 'struct: many protocols', None, '', 'phone')]
CMP = [("Structs can take part", "Yes", "No"), ("Classes can take part", "Yes", "Yes"), ("How many", "Many protocols", "One superclass"),
       ("Shares implementation", "Protocol extensions", "Inherited members"), ("Main purpose", "Abstraction, capabilities", "Shared identity, specialization")]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in CMP)
S.append(slide("Part 4 &middot; Comparison (section 6)", "One parent, or many capabilities", f"""  <div class="body">
    {svg('0 0 1136 184', 'Class inheritance: UPIPayment has one superclass. Protocols: UPIPayment conforms to several protocols', 'inh', P, 'max-height:200px')}
    <div class="gap"></div>
    <table class="tbl compact"><thead><tr><th>Feature</th><th>Protocol</th><th>Class inheritance</th></tr></thead><tbody>{trs}</tbody></table>
  </div>""", notes(('SAY', 'Two design approaches. Class inheritance shares behavior and implementation through a hierarchy, and a class has exactly one superclass. Protocol conformance defines a shared capability, and a type, struct or class, can conform to many protocols.'),
                  ('SAY', 'The table: structs can take part in protocols but not inheritance; classes can do both; many protocols versus one superclass; protocols share implementation through extensions, which is the next part; and the main purpose differs: abstraction and capabilities versus shared identity and specialization.'),
                  ('CONNECT', 'So how do protocols share code without a base class?'))))

# ================================================================== Part 5 (7-8)
divider(5, "Protocol extensions", "Shared behavior and defaults", 'An extension on a protocol gives every conforming type code for free.', 'Two uses, one surprise.')
EXT = """protocol PaymentMethod {
    func pay(amountMinor: Int64)
    func validate(amountMinor: Int64) -> Bool    // requirement
}

extension PaymentMethod {
    func validate(amountMinor: Int64) -> Bool {   // default
        amountMinor > 0
    }
    func logPayment(amountMinor: Int64) {        // shared helper
        print("Payment initiated: ₹\\(amountMinor / 100)")
    }
}"""
S.append(slide("Part 5 &middot; Extensions and defaults (sections 7&ndash;8)", "Write it once, every type gets it", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:start">
      {code("PaymentMethod.swift", EXT, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Shared behavior", ul("<code>logPayment</code>: every payment method can call it"))}
        {card("Default implementation", ul("<code>validate</code> is a <b>requirement</b>", "Types may use the default, or <b>provide their own</b>"), 'step')}
        <div class="step">{card("Result", ul("Composition without a deep class hierarchy"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A protocol extension adds code to every conforming type. logPayment is a shared helper: any payment method can call it instead of re-implementing logging.'),
                  ('SAY', 'Click: an extension can also provide a default implementation of a requirement. validate is declared in the protocol, and the extension gives it a default: amount greater than zero. A type with no validate of its own satisfies the requirement through the default; a type that needs stricter rules provides its own.'),
                  ('SAY', 'Click: protocols define capabilities; extensions provide shared behavior. That is composition without a deep class hierarchy.'),
                  ('CONNECT', 'Now the surprise the lesson text warned about. Watch closely.'))))

DISP = """protocol PaymentMethod {
    func validate(amountMinor: Int64) -> Bool   // requirement
}
extension PaymentMethod {
    func validate(amountMinor: Int64) -> Bool { amountMinor > 0 }
    func label() -> String { "payment" }        // extension only
}
struct CardPayment: PaymentMethod {
    func validate(amountMinor: Int64) -> Bool { amountMinor >= 10_000 }
    func label() -> String { "card" }
}
let card = CardPayment()
let method: any PaymentMethod = card"""
RES = [("<code>validate(amountMinor: 5_000)</code>", "<code>false</code>", "<code>false</code>", "requirement: the <b>card&rsquo;s</b> version both times"),
       ("<code>label()</code>", "<code>\"card\"</code>", "<b><code>\"payment\"</code></b>", "extension only: chosen by the <b>static</b> type")]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in RES)
S.append(slide("Part 5 &middot; Dispatch (section 8)", "Same object, two different answers", f"""  <div class="body">
    {code("Dispatch.swift", DISP, "font-size:13px")}
    <div class="gap"></div>
    <div class="step"><table class="tbl compact"><thead><tr><th>Call</th><th>on <code>card</code></th><th>on <code>method</code></th><th>Why</th></tr></thead><tbody>{trs}</tbody></table></div>
  </div>""", notes(('SAY', 'One CardPayment value, seen two ways: as card, its concrete type, and as method, typed any PaymentMethod. validate is a requirement; label exists only in the extension. CardPayment provides its own version of both.'),
                  ('ASK', 'Before the click: what does each call return?'),
                  ('SAY', 'Click: we ran it. validate is a requirement, so the call goes through the protocol&rsquo;s witness table to the card&rsquo;s own version both times: false, because the card needs at least ₹100. But label is only in the extension: through method, Swift calls the extension&rsquo;s version and returns "payment", even though the object is a card. Methods only in an extension are chosen by the static type.'),
                  ('SAY', 'This surprises developers from Java, where every method is virtual. The rule: if conforming types should be able to customize a method, declare it in the protocol.'),
                  ('CONNECT', 'Extensions are not just for protocols.'))))

# ================================================================== Part 6 (9)
divider(6, "Extensions", "Add to types you don&rsquo;t own", 'An extension adds functionality to an existing type, even one from the standard library.', 'Add a helper to Int64.')
XT = """extension Int64 {
    var rupeesText: String {   // computed
        "₹\\(self / 100)"
    }
}

let amountMinor: Int64 = 50_000
print(amountMinor.rupeesText)       // ₹500"""
S.append(slide("Part 6 &middot; Extensions (section 9)", "Extend Int64 with a rupee helper", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Int64+Rupees.swift", XT, "font-size:16px")}
        <div class="gap"></div>
        {card("Can add", ul("Computed properties, methods", "Initializers, protocol conformances, more"))}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Even for types you don&rsquo;t own", ul("<code>Int64</code>, <code>String</code>, Apple&rsquo;s types", "Subject to access rules"))}
        <div class="step">{card("Cannot add stored properties", '<p style="margin:4px 0 0">' + err("extensions must not contain stored properties") + '</p>')}</div>
        <div class="tip step" data-label="Display text">{ul("Real formatting (&#8377;25,000) belongs in the <b>ViewModel</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'An extension adds functionality to an existing type. Here we add a rupeesText computed property to Int64, turning paise into a simple rupee string: 50,000 paise is ₹500. We do not own Int64; it is in the standard library. Extensions work on accessible types you did not write, subject to access rules.'),
                  ('SAY', 'Extensions can add computed properties, methods, initializers in supported contexts, protocol conformances and more.'),
                  ('SAY', 'Click: they cannot add stored properties: extensions must not contain stored properties. The type&rsquo;s memory layout is already fixed.'),
                  ('SAY', 'Click: this helper is a teaching example. Real display formatting, with grouping like ₹25,000 and the user&rsquo;s locale, belongs in the ViewModel, as in Lesson 0.2.'),
                  ('CONNECT', 'Sometimes you need two capabilities at once.'))))

# ================================================================== Part 7 (10-11)
divider(7, "Composition, any and some", "Combine capabilities; hide or fix the type", 'Require several protocols at once, and choose between any and some.', 'First, composition.')
COMP = """protocol PaymentProcessing {
    func process(amountMinor: Int64)
}
protocol ReceiptGenerating {
    func generateReceipt() -> String
}
func completePayment(
    using service: any PaymentProcessing & ReceiptGenerating,
    amountMinor: Int64
) {
    service.process(amountMinor: amountMinor)
    print(service.generateReceipt())
}"""
TYPES = """completePayment(using: UPIService(), amountMinor: 50_000)
completePayment(using: CashCounter(), amountMinor: 50_000)"""
badge = lambda x, y, t, ok: (f'<g class="nd{"" if ok else " ghost"}"><rect class="sh" x="{x}" y="{y}" width="150" height="34" rx="17"/>'
                             f'<text class="sm" x="{x + 75}" y="{y + 22}" text-anchor="middle">{t} {"&#10003;" if ok else "&#10007;"}</text></g>')
P = [box(0, 0, 552, 60, 'UPIService', 'conforms to both', None, '', 'phone'),
     badge(236, 13, 'process', True), badge(394, 13, 'receipt', True),
     f'<g class="fade" data-lit="1+">{box(0, 70, 552, 56, "Accepted", "UPI: ₹500 paid · Receipt NP-R1", None, "lit", "check")}</g>',
     box(0, 150, 552, 60, 'CashCounter', 'pays only', None, '', 'bank'),
     badge(236, 163, 'process', True), badge(394, 163, 'receipt', False),
     f'<g class="fade" data-lit="2+">{box(0, 220, 552, 56, "Rejected by the compiler", "does not conform to ReceiptGenerating", None, "alert", "cross")}</g>']
S.append(slide("Part 7 &middot; Composition (section 10)", "Require two capabilities with &amp;", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("CompletePayment.swift", COMP, "font-size:13.5px")}
        <div class="gap"></div>
        {code("Callers.swift", TYPES, "font-size:13px")}</div>
      {svg('0 0 552 276', 'completePayment needs both process and receipt. UPIService has both and is accepted; CashCounter has only process and is rejected', 'comp', P, 'max-height:400px')}
    </div>
    {cues(2)}
  </div>""", notes(('SAY', 'Two small protocols: PaymentProcessing can take a payment, ReceiptGenerating can produce a receipt. completePayment needs a service that can do both, so its parameter type is any PaymentProcessing & ReceiptGenerating. The ampersand means: must conform to both.'),
                  ('SAY', 'Two NPay services. UPIService conforms to both protocols. CashCounter only takes payments; it cannot issue receipts.'),
                  ('SAY', 'Click: pass the UPI service and it is accepted. Real output: UPI: ₹500 paid, then Receipt NP-R1.'),
                  ('SAY', 'Click: pass the cash counter and the build fails before the app ever runs. The real message: argument type CashCounter does not conform to expected type ReceiptGenerating.'),
                  ('SAY', 'Notice we did not need a combined superclass, such as a PaymentAndReceiptBase, just to say both. Keep protocols small and combine them with the ampersand where a function needs more.'),
                  ('CONNECT', 'You have now seen any several times. Swift also has some.'))))

MIX = """let methods: [any PaymentMethod] = [
    UPIPayment(), CardPayment()
]

for m in methods {
    m.pay(amountMinor: 50_000)
}"""
MIXBAD = """let methods: [some PaymentMethod] = [UPIPayment(), CardPayment()]"""
P = ['<text class="mono" x="0" y="14">[any PaymentMethod]: ONE ARRAY, MIXED TYPES</text>',
     '<rect class="wire dash" x="0" y="28" width="552" height="96" rx="16"/>',
     box(16, 44, 252, 64, 'UPIPayment', '[0]', None, '', 'phone'), box(284, 44, 252, 64, 'CardPayment', '[1]', None, '', 'key'),
     wire('M142 128V156' + head(142, 156, 'd'), '1+'), wire('M410 128V156' + head(410, 156, 'd'), '1+'),
     fade('1+', box(16, 162, 252, 56, 'UPI ₹500', 'its own pay()', None, 'lit', 'check') + box(284, 162, 252, 56, 'Card ₹500', 'its own pay()', None, 'lit', 'check'))]
S.append(slide("Part 7 &middot; any (section 11)", "any: different types in one place", f"""  <div class="body">
    {cues(1)}
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Mixed.swift", MIX, "font-size:14px")}
        <div class="step" style="margin-top:14px">{card("Same array with some", f'<p style="margin:4px 0 8px"><code>[some PaymentMethod]</code></p>' + err("conflicting arguments to generic parameter (&lsquo;UPIPayment&rsquo; vs. &lsquo;CardPayment&rsquo;)"))}</div></div>
      {svg('0 0 552 218', 'An array of any PaymentMethod holds a UPIPayment and a CardPayment; each calls its own pay and prints UPI 500 rupees and Card 500 rupees', 'anymix', P, 'max-height:280px')}
    </div>
    <div class="gap"></div>
    <div class="takeaway step"><code>any</code>: the type <b>can be different</b> for each value. Use it for mixed arrays and swappable values.</div>
  </div>""", notes(('SAY', 'any PaymentMethod and some PaymentMethod both mean: a value of a type that conforms to PaymentMethod. The difference is whether that type can vary. Start with any.'),
                  ('SAY', 'This array holds two different types: a UPIPayment and a CardPayment. That is only possible because the element type is any PaymentMethod.'),
                  ('SAY', 'Click: loop over it and each one calls its own pay. Real output: UPI ₹500, then Card ₹500. Swift works out which pay to call while the app runs.'),
                  ('SAY', 'Click: write the same array with some instead, and the compiler refuses: conflicting arguments, UPIPayment versus CardPayment. some allows only one type.'),
                  ('SAY', 'Click: so any means the type can be different for each value. Use it for mixed arrays and for stored values you may swap, like the service in a ViewModel in Part 8.'),
                  ('CONNECT', 'So what is some for?'))))

BODY = """import SwiftUI

struct DashboardView: View {
    var body: some View {
        VStack {
            Text("₹25,000")
            Button("Refresh balance") { }
        }
    }
}"""
SOME = """func defaultPayment() -> some PaymentMethod {
    UPIPayment()   // always UPIPayment; a CardPayment
}                  // on another path won't compile"""
S.append(slide("Part 7 &middot; some (section 11)", "some: one exact type you don&rsquo;t have to name", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DashboardView.swift", BODY, "font-size:14px")}
      <div>
        <div class="step">{card("The real type of body (printed)", '<p style="font-family:var(--code-font);font-size:20px;margin:8px 0 4px;color:var(--teal-ink);font-weight:600">VStack&lt;TupleView&lt;(Text, Button&lt;Text&gt;)&gt;&gt;</p>' + ul("<code>some View</code> hides this", "It changes every time you edit the view"))}</div>
        <div class="gap"></div>
        <div class="step">{code("DefaultPayment.swift", SOME, "font-size:14px")}</div>
      </div>
    </div>
    <div class="gap"></div>
    <div class="takeaway step"><code>some</code>: <b>one</b> exact type the compiler knows, so you don&rsquo;t have to name it. <code>any</code> can vary; <code>some</code> cannot.</div>
  </div>""", notes(('SAY', 'Now some. Here is a small NPay view: a VStack with a Text and a Button. Its body is declared as some View.'),
                  ('SAY', 'Click: we printed the real type of body. It is VStack of TupleView of Text and Button of Text. Nobody wants to write that, and it changes every time you edit the view. some View means: one exact type, the compiler knows it, you do not have to spell it.'),
                  ('SAY', 'Click: the same works for our protocol. defaultPayment returns some PaymentMethod, and it is always a UPIPayment; the caller just does not see the name. Because it must be one type, returning a card payment on another path is a compile error: the return statements do not have matching underlying types.'),
                  ('SAY', 'Click: so some means one fixed type, known to the compiler and hidden from the caller, used mostly for return types. any can vary; some cannot. Lesson 1.7 explains the generics underneath.'),
                  ('CONNECT', 'Which brings us to SwiftUI.'))))

# ================================================================== Part 8 (12-13)
divider(8, "Protocols in SwiftUI and DI", "The framework and the architecture", 'SwiftUI is built on protocols, and so is a testable NPay.', 'SwiftUI first.')
VIEW = """import SwiftUI

struct DashboardView: View {
    var body: some View {
        Text("NPay")
    }
}"""
S.append(slide("Part 8 &middot; SwiftUI (section 12)", "View is a protocol", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:center">
      {code("DashboardView.swift", VIEW, "font-size:16px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("struct DashboardView: View", ul("A <b>struct</b> conforming to the <b>View</b> protocol (1.5, today)"))}
        {card("var body: some View", ul("An <b>opaque</b> type: one specific view, hidden"))}
        {card("Modifiers, composition", ul("Built on protocols and <b>generics</b> (1.7, Unit 02)"))}
      </div>
    </div>
  </div>""", notes(('SAY', 'View is a protocol. DashboardView is a struct that conforms to it, a value type from Lesson 1.5 conforming to a protocol from today. body returns some View, an opaque type: one specific view type, hidden from you. Modifiers and view composition build on protocols and generics.'),
                  ('SAY', 'These are not arbitrary framework conventions. They are Swift&rsquo;s protocol and generic type system, which is why we learn the language first. Unit 02 builds real screens with them.'),
                  ('CONNECT', 'Last, protocols in NPay&rsquo;s architecture.'))))

DI = """struct Balance: Sendable { let balanceMinor: Int64 }

protocol BalanceProviding: Sendable {
    func fetchBalance() async throws -> Balance
}

struct MockBalanceService: BalanceProviding {
    func fetchBalance() async throws -> Balance {
        Balance(balanceMinor: 2_500_000)        // ₹25,000
    }
}"""
VM = """@MainActor
final class DashboardViewModel {
    private let service: any BalanceProviding

    init(service: any BalanceProviding) {
        self.service = service
    }

    func loadBalance() async throws -> Balance {
        try await service.fetchBalance()
    }
}"""
P = [box(0, 0, 260, 56, 'DashboardViewModel', 'depends on', None, '', 'layout'), wire('M264 28H306' + head(306, 28, 'r')),
     box(312, 0, 250, 56, 'BalanceProviding', 'protocol', None, 'lit', 'link'),
     wire('M614 28H568' + head(568, 28, 'l'), None, 'dash'),
     box(620, 0, 240, 56, 'BalanceService', 'real API', None, '', 'bank'), box(876, 0, 260, 56, 'MockBalanceService', 'tests, previews', None, '', 'check')]
S.append(slide("Part 8 &middot; Dependency injection (section 13)", "Depend on the protocol, inject the service", f"""  <div class="body">
    {svg('0 0 1136 56', 'DashboardViewModel depends on BalanceProviding; BalanceService and MockBalanceService conform to it', 'di', P, 'max-height:64px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("BalanceProviding.swift", DI, "font-size:13px")}
      <div>{code("DashboardViewModel.swift", VM, "font-size:13px")}</div>
    </div>
    <div class="gap"></div>
    <div class="warn step" data-label="Swift 6">{ul("Without <code>: Sendable</code>: <b>sending &lsquo;self.service&rsquo; risks causing data races</b> (why: Lesson 1.9)")}</div>
  </div>""", notes(('SAY', 'NPay&rsquo;s ViewModel fetches the balance. It should not be tied to one network service. So it depends on the BalanceProviding protocol and receives a service through its initializer: dependency injection. The real BalanceService talks to the bank&rsquo;s API; MockBalanceService returns ₹25,000 for tests and previews. Same names as Lessons 0.8 and 1.1.'),
                  ('SAY', 'The ViewModel depends on the protocol, not the concrete implementation, so swapping the real service for a mock in a test is one line.'),
                  ('SAY', 'Click: one correction to the lesson text. Its version of this code does not compile in Swift 6: sending self.service risks causing data races. The ViewModel is on the main actor and the service&rsquo;s async method runs elsewhere, so the service must be safe to share. Marking the protocol Sendable fixes it, and both our services are simple structs, so they qualify. Lesson 1.9 explains Sendable; Unit 04 builds full dependency injection.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.6', (), [("link", "Protocols are contracts", "structs and classes conform"),
                     ("code", "Extensions share code", "declare it to make it overridable"),
                     ("check", "Depend on protocols", "inject real or mock services")],
         'Three things to remember. A protocol is a contract that any struct, class or enum can conform to, and a type can conform to many. Protocol extensions share code and defaults; declare a method in the protocol if conforming types should be able to customize it. And depend on protocols, not concrete types: that is what makes SwiftUI work and NPay testable.')

review_divider(8)
review([("link", "Choose one", "What does a protocol define?",
         "What does a protocol define?<br>A. A base class with shared stored properties<br>B. Requirements that conforming types must satisfy<br>C. A concrete implementation every type inherits<br>D. A struct&rsquo;s memory layout", "B",
         "A protocol is a contract: what must be provided, not how. Implementations live in the conforming types (or in defaults).",
         "Treating a protocol like an abstract base class.", "Some pick A.", None),
        ("layers", "Question", "Can a struct conform to a protocol?",
         "Can a <code>struct</code> conform to a protocol?", "Yes",
         "Structs, classes and enums can all conform, and a type can conform to many protocols.",
         "Assuming protocols need classes, like inheritance.", "Most say yes.", None),
        ("diff", "Question", "Can a Swift class have two superclasses?",
         "Can a Swift class inherit from two superclasses?", "No",
         "Single class inheritance only. A class can conform to many protocols.",
         "Confusing protocols with superclasses.", "Most say no.", None),
        ("code", "Predict the output", "What does method.label() return for a CardPayment?",
         "<code>label()</code> is defined only in a protocol extension, and <code>CardPayment</code> defines its own.<br><code>let method: any PaymentMethod = CardPayment()</code><br><code>print(method.label())</code>", "\"payment\"",
         "A method only in an extension is chosen by the static type, <code>any PaymentMethod</code>. Declare it in the protocol to get the card&rsquo;s version.",
         "Expecting dynamic dispatch, as in Java.", "Most say card.", None),
        ("cross", "Question", "Can an extension add a stored property?",
         "Can an extension add a stored property to an existing type?", "No",
         "&ldquo;Extensions must not contain stored properties.&rdquo; Computed properties are fine.",
         "Expecting extensions to add any member.", "Some say yes.", None),
        ("decision", "Choose one", "Which lets one variable hold a UPIPayment, then a CardPayment?",
         "Which declaration lets one variable hold a <code>UPIPayment</code>, then a <code>CardPayment</code>?<br>A. <code>var m: some PaymentMethod</code><br>B. <code>var m: any PaymentMethod</code><br>C. <code>var m: UPIPayment</code><br>D. <code>var m: PaymentMethod.Type</code>", "B",
         "<code>any</code> is a box for any conforming type. <code>some</code> fixes one hidden type.",
         "Thinking some and any are interchangeable.", "Some pick A.", None),
        ("lock", "Question", "Does a let property satisfy a { get set } requirement?",
         "A protocol requires <code>var balanceMinor: Int64 { get set }</code>. Does <code>let balanceMinor: Int64</code> satisfy it?", "No",
         "A read-write requirement needs a writable property. The compiler reports the type does not conform.",
         "Assuming any property with the right name works.", "Some say yes.", None),
        ("eye", "Choose one", "For two Equatable structs, what does == compare?",
         "Two values of an <code>Equatable</code> struct are compared with <code>==</code>. What is compared?<br>A. Their memory addresses<br>B. Their values<br>C. Their type names<br>D. Nothing; structs cannot use ==", "B",
         "<code>Equatable</code> is itself a protocol: <code>==</code> compares values. Identity (<code>===</code>) is for classes.",
         "Mixing up == and ===.", "Some pick A.", "Spaced review from Lesson 1.5.")])

S.append(next_slide('1.6', [("1.7", "Generics &amp; error handling", "<code>some</code>, constraints, generic functions"),
                            ("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "why <code>BalanceProviding: Sendable</code>"),
                            ("3.5", "Reusable views &amp; environment", "View protocol in practice"),
                            ("4.5", "Dependency injection &amp; composition root", "injecting NPay&rsquo;s services"),
                            ("9.4", "Mocks, fakes &amp; URLProtocol", "MockBalanceService in tests")],
                    'Protocols run through the course. Lesson 1.7 builds generics on top of them and explains some properly; 1.9 explains why our protocol had to be Sendable; Unit 03 builds reusable views; Unit 04 builds dependency injection with a composition root; and Unit 09 uses mocks like MockBalanceService in tests.'))

LAB = """protocol PaymentMethod {
    var name: String { get }
    func pay(amountMinor: Int64)
    func validate(amountMinor: Int64) -> Bool
}
// TODO: extension with a default validate (> 0) and log(amountMinor:)
// TODO: UPIPayment, CardPayment (minimum ₹100), BankTransferPayment
let methods: [any PaymentMethod] = [/* all three */]
for m in methods where m.validate(amountMinor: 5_000) {
    m.pay(amountMinor: 5_000)
}"""
S.append(lab_slide('1.6', "NPay payment methods", "Build three payment methods on one protocol, then test the dispatch rule.",
                   ["Write the default <code>validate</code> and a shared <code>log</code> in an extension.",
                    "Add three conforming structs; the card needs at least &#8377;100.",
                    "Run the loop: which methods pay &#8377;50?",
                    "Move <code>validate</code> out of the protocol: what changes, and why?",
                    "Make a mock <code>BalanceProviding</code> and inject it."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab. Reference: extension PaymentMethod { func validate(amountMinor: Int64) -> Bool { amountMinor > 0 }; func log(amountMinor: Int64) { print("\\(name): ₹\\(amountMinor / 100)") } }. CardPayment overrides validate with amountMinor >= 10_000. Expected output: "UPI: ₹50" and "Bank transfer: ₹50"; the card is skipped because ₹50 is below its ₹100 minimum. Step 4: remove validate from the protocol (keep it in the extension and in CardPayment): now the loop over [any PaymentMethod] calls the extension version, the card passes validation and "Card: ₹50" also prints. That is the dispatch rule from Part 5. Step 5: protocol BalanceProviding: Sendable plus a struct mock returning Balance(balanceMinor: 2_500_000).',
                   side=f'<div>{code("lab.swift", LAB, "font-size:13px")}<div class="gap"></div>{card("You hand in", ul("Output before and after step 4, with the reason"))}</div>'))

end_slide('1.6', 'Protocols, Extensions &amp;<br>Protocol-Oriented Programming', 'Lesson 1.7 &mdash; Generics &amp; Error Handling',
          'You can now define protocols and make structs and classes conform, use polymorphism through a protocol, compare protocols with class inheritance, share code with extensions and defaults, explain the dispatch rule, compose protocols, tell any from some, and inject protocol-typed dependencies.',
          'Next, Lesson 1.7: generics and error handling, the type-system machinery behind some View and the proper alternative to try?.')

write_deck(OUT16, '1.6', 'Protocols &amp; Extensions', 'Protocols, Extensions &amp; POP')
