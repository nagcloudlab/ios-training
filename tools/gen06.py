"""Generates decks/lesson-0.6/index.html from the Lesson 0.6 text only."""
import html, re, sys
OUT06 = sys.argv[1]
sys.argv = ['x', '/dev/null']
src = open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers: lit, tall, row, wire, head, svg, code, notes, slide, points, E

S = []
cues = lambda n: '<i class="step cue"></i>' * n


def divider(n, title, lead, say, con):
    S.append(f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(('SAY', say), ('CONNECT', con))}</section>

""")


def box(x, y, w, h, title, sub='', l=None, cls='', icon=''):
    return row(x, y, w, h, icon, title, sub, l, cls)


def fade(l, inner):
    return f'<g class="fade" data-lit="{l}">{inner}</g>'


def stages(items):
    return '<div class="points v stages">' + ''.join(
        f'<div class="step"><span class="q-num">{i + 1}</span><span><b>{t}</b><small>{d}</small></span></div>' for i, (t, d) in enumerate(items)) + '</div>'


# ------------------------------------------------------------------ title + outcomes
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.6</p>
    <h1 style="font-size:54px;line-height:1.05">iOS Memory<br>Architecture &amp; ARC</h1>
    <p class="lead" style="max-width:660px">Who creates objects in memory, who owns them, and who destroys them?</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'One of the most important topics in Swift and iOS: who creates objects in memory, who owns them, and who destroys them? This prepares you to explain memory management to developers coming from Java, Python, C++ and other languages. We go slowly, from fundamentals to real iOS leaks.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")
outs = [("layers", "Why Swift distinguishes <b>value</b> and <b>reference</b> semantics"), ("memory", "How <b>ARC</b> manages class-instance lifetimes"),
        ("link", "Why <b>strong-reference cycles</b> occur"), ("shield", "How <b>weak</b> and <b>unowned</b> differ"),
        ("clock", "Why <b>closures</b> and <b>timers</b> can retain objects"), ("eye", "How to <b>investigate</b> unexpected retention in Xcode")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.6 &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six things you should be comfortable explaining by the end. The route: process memory, stack and heap, structs and classes, ARC, strong, weak and unowned, retain cycles, and diagnosing memory in Xcode.'),
                 ('CONNECT', 'First, where this sits in NPay.'))))
S.append(map_slide('0.6', 'Today: memory inside NPay', ('memory',),
                   'Lesson 0.5: the main thread runs NPay&rsquo;s UI through the RunLoop; slow work there freezes the screen.',
                   'Who creates, owns and destroys the objects inside NPay&rsquo;s process: stack, heap and ARC.',
                   'Last time we followed work through the main thread and its RunLoop. Today we stay inside the same NPay process and look at its memory: where values live, who owns class instances, and why some objects never go away.',
                   'Why does an app need memory at all?'))

# ================================================================== 1 · process memory
divider(1, "Why does an app need memory?", "How iOS organizes process memory",
        "NPay needs memory for the balance, the transaction list, merchant logos, network responses and screen state. Some data lives only while a function runs; other data must survive many calls.", "Here is how the process memory is organized.")
regions = [("code", "Code / text", "executable machine instructions"), ("file", "Global &amp; static data", "global and static storage"),
           ("memory", "Heap", "dynamic objects and allocations"), ("thread", "Thread stacks", "function call frames, execution state"),
           ("layers", "Other mapped memory", "libraries, files, graphics-related mappings")]
P = [box(0, i * 70, 560, 58, t, s, str(i + 1), '', ic) for i, (ic, t, s) in enumerate(regions)]
S.append(slide("Part 1 &middot; Process memory &middot; conceptual", "Simplified iOS process memory", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    <div>
      {svg("0 0 560 340", "Process memory: code, global and static data, heap, thread stacks, other mapped memory", "s3mem", P, "max-height:380px")}
      <p class="small muted" style="margin:8px 0 0">Conceptual regions, not their physical order. iOS uses virtual memory, not fixed partitions of RAM.</p>
    </div>
    <div>
      {cues(5)}
      <div class="analogy step">
        <div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div>
        <p>NPay&rsquo;s process is the <b>kitchen</b>. The chef&rsquo;s <b>cutting board</b> holds what the current dish needs; the <b>pantry</b> holds what many dishes need, for longer.</p>
      </div>
      <div class="gap"></div>
      <p class="small step">The OS provides the virtual memory environment; the language runtime and the app manage allocations inside it.</p>
    </div>
  </div>""", notes(('SAY', 'Click through the five regions: code, global and static data, the heap for dynamic objects, thread stacks for call frames, and other mapped memory such as libraries and graphics mappings. These are conceptual regions in virtual memory, not fixed slices of RAM.'),
                  ('SAY', 'Back to our kitchen: NPay’s process is the kitchen. The cutting board holds what the current dish needs and is cleared when the dish is done: that is the stack. The pantry holds ingredients many dishes need, for longer: that is the heap.'),
                  ('CONNECT', 'Two of those regions matter most for us: the stack and the heap.'))))

# ================================================================== 2 · stack vs heap
divider(2, "Stack versus heap", "The cutting board and the pantry",
        "Start with a simple function and ask where its values live.", "Here is the function.")
CALC = '''func transferTotal() {
    let amount = 2_500
    let fee = 10
    let total = amount + fee

    print(total)
}

transferTotal()'''
P = ['<text class="mono" x="0" y="16">STACK</text><text class="mono" x="300" y="16">HEAP</text>']
for i, t in enumerate(["Call frame", "Temporary values", "Return information"]):
    P.append(box(0, 28 + i * 66, 260, 54, t, '', '1'))
for i, t in enumerate(["Object A", "Object B", "Shared storage"]):
    P.append(box(300, 28 + i * 66, 260, 54, t, '', '2'))
S.append(slide("Part 2 &middot; Stack and heap &middot; conceptual", "Where do values live?", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    {code("Totals.swift", CALC, "font-size:17px")}
    <div>
      {svg("0 0 560 226", "Stack: call frame, temporary values, return information. Heap: object A, object B, shared storage.", "s5sh", P)}
      {cues(2)}
      <div class="gap"></div>
      <p class="small">The <b>stack</b> is efficient for call-related storage. The <b>heap</b> is more flexible, but involves allocation and lifetime management.</p>
    </div>
  </div>""", notes(('SAY', 'transferTotal needs temporary execution storage for amount, fee and total. Click: the stack, tied to function calls and thread execution, with the call frame, temporary values and return information. Click: the heap, for dynamically allocated storage and objects.'),
                  ('SAY', 'The stack is typically efficient for call-related storage; heap allocation is more flexible but needs allocation and lifetime management.'),
                  ('CONNECT', 'A warning before we go further.'))))
S.append(slide("Part 2 &middot; Swift nuance", "Not simply stack versus heap", """  <div class="body">
    <div class="cols stretch">
      <div class="card step"><span class="label">Common belief</span><p>&ldquo;Structs live on the stack; classes live on the heap.&rdquo;</p></div>
      <div class="card accent step"><span class="label">In Swift</span><p>A struct is <b>not guaranteed</b> to live on the stack: stored in a class, an array or an escaping closure, it lives on the heap. And a class <b>instance</b> that never escapes its function may be placed on the stack by the optimizer.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="The reliable distinction"><b>Value semantics</b> versus <b>reference semantics</b>, not simply stack versus heap.</div>
  </div>""", notes(('SAY', 'Developers from other languages often learn "structs on the stack, classes on the heap". In Swift that is not a guarantee. A struct stored inside a class instance, an array or an escaping closure lives on the heap. And the optimizer may place a class instance on the stack when it can prove the instance never escapes the function. Placement is an implementation detail.'),
                  ('SAY', 'The reliable language-level distinction is value semantics versus reference semantics.'),
                  ('CONNECT', 'So what do value and reference semantics mean in practice?'))))

# ================================================================== 3 · structs vs classes
divider(3, "Swift structs versus classes", "Value type versus reference type",
        "A struct is a value type; a class is a reference type. Let's see what that means with the same Account written both ways.", "First, the struct.")
SA = '''struct Account {
    var balanceMinor: Int64      // paise
}

var accountA = Account(balanceMinor: 500_000)   // ₹5,000
var accountB = accountA

accountB.balanceMinor = 900_000

print(accountA.balanceMinor)   // 500000
print(accountB.balanceMinor)   // 900000'''
P = [box(0, 0, 250, 80, "accountA", "&#8377;5,000"), box(300, 0, 250, 80, "accountB", "&#8377;5,000"),
     fade("1+", box(300, 0, 250, 80, "accountB", "&#8377;9,000", None, 'lit')),
     '<text class="sm" x="0" y="116">Each variable holds its own value.</text>']
S.append(slide("Part 3 &middot; Value type", "A struct: independent values", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Account.swift", SA, "font-size:15px")}
    <div>
      {svg("0 0 560 124", "accountA and accountB both hold 5,000 rupees; changing accountB to 9,000 leaves accountA at 5,000", "s8val", P)}
      {cues(1)}
      <div class="gap"></div>
      <div class="rule step">Assigning <code>accountA</code> to <code>accountB</code> gives <b>independent values</b>.</div>
    </div>
  </div>""", notes(('SAY', 'NPay stores money as whole paise in an Int64, balanceMinor, so 500,000 paise is &#8377;5,000. accountB starts as a copy of accountA. Click: we change accountB to &#8377;9,000; accountA still shows &#8377;5,000. Each variable changes separately.'),
                  ('CONNECT', 'Now the same code with a class.'))))
CA = '''final class Account {
    var balanceMinor: Int64      // paise
    init(balanceMinor: Int64) { self.balanceMinor = balanceMinor }
}

let accountA = Account(balanceMinor: 500_000)   // ₹5,000
let accountB = accountA

accountB.balanceMinor = 900_000

print(accountA.balanceMinor)   // 900000
print(accountB.balanceMinor)   // 900000'''
P = [box(0, 0, 200, 56, "accountA", "reference"), box(0, 110, 200, 56, "accountB", "reference"),
     wire(f'M200 28H270V70H316{head(316, 70, "r")}'), wire(f'M200 138H270V96H316{head(316, 96, "r")}'),
     box(322, 44, 230, 78, "Account instance", "&#8377;5,000"),
     fade("1+", box(322, 44, 230, 78, "Account instance", "&#8377;9,000", None, 'lit')),
     '<text class="sm" x="0" y="196">Both references observe the same balance.</text>']
S.append(slide("Part 3 &middot; Reference type", "A class: one shared instance", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Account.swift", CA, "font-size:14px")}
    <div>
      {svg("0 0 560 204", "accountA and accountB both reference one Account instance; changing it through accountB to 9,000 changes it for both", "s9ref", P)}
      {cues(1)}
      <div class="gap"></div>
      <div class="rule step">Both variables <b>reference the same instance</b>.</div>
    </div>
  </div>""", notes(('SAY', 'With a class, accountA and accountB are two references to one instance. Click: change the balance through accountB and accountA sees &#8377;9,000 too.'),
                  ('ASK', 'Why can accountA be a let constant and still change?'),
                  ('EXPECT', 'let fixes the reference, not the instance it points to. The instance itself is mutable.'),
                  ('CONNECT', 'Here is the full comparison.'))))
S.append(slide("Part 3 &middot; Comparison", "Struct vs class", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Struct</th><th>Class</th></tr>
      <tr><td>Value semantics</td><td>Reference semantics</td></tr>
      <tr><td>Assignment produces independent values</td><td>Assignment shares an instance</td></tr>
      <tr><td>No class inheritance</td><td>Supports inheritance</td></tr>
      <tr><td>No identity by default</td><td>Has object identity</td></tr>
      <tr><td>Can use <code>mutating</code> methods</td><td>Can mutate properties through shared references</td></tr>
      <tr class="hl"><td>Not managed as a class instance by ARC</td><td>Class instance lifetime managed by <b>ARC</b></td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Copy-on-write"><b>Array</b>, <b>Dictionary</b>, <b>Set</b> and <b>String</b> share storage until one copy is modified. Your own structs copy their stored properties; they get copy-on-write only if built that way (Lesson 1.5).</div>
  </div>""", notes(('SAY', 'Six differences. The last row leads into the rest of this lesson: class instance lifetimes are managed by ARC.'),
                  ('SAY', 'Copy-on-write is a property of the standard collections: Array, Dictionary, Set and String share their storage until one copy is modified, so assigning a large array does not copy every element immediately. It is not automatic for every struct: your own struct copies its stored properties, and gets copy-on-write only if you implement it, which Lesson 1.5 covers.'),
                  ('CONNECT', 'So how does ARC decide when a class instance can go away?'))))

# ================================================================== 4 · ARC
divider(4, "Automatic Reference Counting", "ARC: the central concept",
        "Swift uses Automatic Reference Counting to manage the lifetime of class instances.", "Think of a rented conference room.")
P = []
counts = ["3", "2", "1", "0"]
P.append('<g class="nd lit" data-lit="0-2"><rect class="sh" x="353" y="0" width="430" height="104" rx="14"/></g>')
P.append(fade("3+", '<g class="nd alert"><rect class="sh" x="353" y="0" width="430" height="104" rx="14"/></g>'))
P.append('<text x="377" y="32">Customer object</text>')
for i, c in enumerate(counts):
    lbl = 'strong reference' if c == '1' else 'strong references'
    state = 'ALIVE' if c != '0' else 'DEINIT CAN RUN'
    P.append(fade(str(i) if i < 3 else "3+", f'<text x="377" y="84" style="font-size:40px;font-weight:800">{c}</text>'
                  f'<text class="sm" x="412" y="80">{lbl}</text><text class="mono" x="760" y="84" text-anchor="end">{state}</text>'))
for i, (name, gone) in enumerate([("Reference A", 3), ("Reference B", 2), ("Reference C", 1)]):
    x = 120 + i * 320
    P.append(fade(f"0-{gone - 1}", wire(f'M{x + 120} 168V110{head(x + 120, 110, "u")}', None, 'lit') + box(x, 168, 240, 56, name, "strong")))
    P.append(fade(f"{gone}+", box(x, 168, 240, 56, name, "released", None, 'ghost')))
S.append(slide("Part 4 &middot; ARC &middot; conceptual", "Counting strong references", f"""  <div class="body">
    {svg("0 0 1136 226", "A Customer object with three strong references; releasing them one by one brings the count from 3 to 0, and then the object can be deinitialized", "s12arc", P)}
    {cues(3)}
    <div class="gap-lg"></div>
    <div class="cols">
      <div class="analogy"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div><p>Each strong reference is a cook still <b>using</b> an ingredient from the pantry. When nobody is using it, it can be <b>cleared away</b>.</p></div>
      <p class="small muted">Conceptual. The compiler and runtime may optimize reference-count operations; they are not necessarily visible one-for-one.</p>
    </div>
  </div>""", notes(('SAY', 'ARC tracks strong references to a class instance. When no strong references keep it alive, it can be deinitialized. Click through: three references, then two, then one, then none, and the object can be destroyed.'),
                  ('SAY', 'In the kitchen: each strong reference is a cook still using an ingredient from the pantry. When nobody is using it, it can be cleared away.'),
                  ('CONNECT', "Now the same thing in Swift code."))))
CUST = '''final class Customer {
    let name: String
    init(name: String) { self.name = name }
    deinit { print("Customer destroyed") }
}

var customer1: Customer? = Customer(name: "Ravi")
var customer2 = customer1

customer1 = nil   // still alive through customer2
customer2 = nil   // no strong references: deinit runs'''
S.append(slide("Part 4 &middot; ARC in code", "Setting one reference to nil", f"""  <div class="body cols middle" style="grid-template-columns:1.3fr 1fr">
    {code("Customer.swift", CUST, "font-size:15px")}
    <div>
      {stages([("Two strong references", "customer1 and customer2 point to Ravi"), ("<code>customer1 = nil</code>", "the instance is still alive through customer2"), ("<code>customer2 = nil</code>", "no strong references remain; deinit can run")])}
      <div class="gap"></div>
      <div class="rule step">Setting one variable to <code>nil</code> does not necessarily destroy the instance.</div>
    </div>
  </div>""", notes(('SAY', 'Two variables reference the same Customer. Setting customer1 to nil releases one reference, but the object survives through customer2. Only when customer2 is also nil do no strong references remain, and deinit can execute.'),
                  ('ASK', 'After customer1 = nil, has "Customer destroyed" printed?'),
                  ('EXPECT', 'No. customer2 still holds a strong reference.'),
                  ('CONNECT', 'Strong is only one kind of reference.'))))

# ================================================================== 5 · strong / weak / unowned
divider(5, "Strong, weak and unowned", "Three ownership relationships",
        "Swift provides different ownership relationships for different lifetime situations.", "Here are the three.")
P = ['<text class="mono" x="0" y="14">REFERENCE</text><text class="mono" x="446" y="14">OBJECT</text><text class="mono" x="760" y="14">WHEN THE OBJECT IS DEALLOCATED</text>']
kinds = [("strong", "the default", "Keeps it alive", "it cannot be deallocated while held", ''),
         ("weak", "optional", "Becomes nil", "automatically, safely", ''),
         ("unowned", "assumes it is alive", "Access traps (crash)", "if the object is already gone", 'alert')]
for i, (k, sub, out, osub, oc) in enumerate(kinds):
    y = 28 + i * 84
    P.append(box(0, y, 300, 62, f'<tspan class="code">{k}</tspan> reference', sub, str(i + 1)))
    P.append(wire(f'M300 {y + 31}H440{head(440, y + 31, "r")}', None, '' if i == 0 else 'dash'))
    P.append(box(446, y, 240, 62, "Class instance", "", None, '', 'memory'))
    P.append(fade(f"{i + 1}+", box(760, y, 376, 62, out, osub, None, oc)))
S.append(slide("Part 5 &middot; Reference kinds", "Strong, weak and unowned", f"""  <div class="body">
    {svg("0 0 1136 278", "Strong keeps the instance alive; weak becomes nil when it is deallocated; unowned traps if accessed after deallocation", "s16kinds", P, "max-height:300px")}
    {cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Do not overcorrect">Strong ownership is <b>normal and necessary</b>. A parent strongly owns its child; a child may hold a <b>weak</b> reference back.</div>
  </div>""", notes(('SAY', 'Click through the three. Strong keeps the instance alive and is the default. Weak does not keep it alive; it is optional and becomes nil automatically when the instance is deallocated. Unowned does not keep it alive either, and assumes the instance is still alive whenever accessed: accessing it after deallocation traps, a deliberate crash.'),
                  ('SAY', 'There is also unowned(unsafe), which skips even that check: accessing a deallocated instance is then undefined behaviour. Lesson 1.8 goes deeper into unowned and ownership.'),
                  ('SAY', 'Do not replace every strong reference with weak. A parent usually strongly owns a child; the child may hold a weak back-reference to a parent that can disappear independently.'),
                  ('CONNECT', 'What goes wrong when two objects own each other?'))))

# ================================================================== 6 · retain cycles
divider(6, "Retain cycles", "The classic ARC problem",
        "Imagine two people holding each other's hands and refusing to let go.", "In Swift, two class instances can do the same.")
CYC = '''class Person { var apartment: Apartment? }
class Apartment { var tenant: Person? }

var person: Person? = Person()
var apartment: Apartment? = Apartment()
person?.apartment = apartment
apartment?.tenant = person

person = nil
apartment = nil   // neither instance is freed'''
P = [box(30, 0, 200, 50, "person", "outside variable"), box(330, 0, 200, 50, "apartment", "outside variable"),
     fade("0", wire(f'M130 50V96{head(130, 96, "d")}') + wire(f'M430 50V96{head(430, 96, "d")}')),
     fade("1+", '<text class="sm" x="280" y="80" text-anchor="middle">set to nil</text>'),
     box(30, 102, 200, 64, "Person", "instance", None, '', 'user'), box(330, 102, 200, 64, "Apartment", "instance", None, '', 'building'),
     wire(f'M230 124H324{head(324, 124, "r")}'), '<text class="sm" x="277" y="116" text-anchor="middle">strong</text>',
     fade("0-1", wire(f'M330 146H236{head(236, 146, "l")}') + '<text class="sm" x="283" y="164" text-anchor="middle">strong</text>'),
     fade("2+", wire(f'M330 146H236{head(236, 146, "l")}', None, 'dash') + '<text class="sm" x="283" y="164" text-anchor="middle">weak</text>'),
     fade("0", '<text class="mono" x="280" y="206" text-anchor="middle">BOTH REACHABLE FROM OUTSIDE</text>'),
     fade("1", box(30, 186, 500, 50, "Leak: both stay alive", "they retain each other", None, 'alert')),
     fade("2+", box(30, 186, 500, 50, "Weak tenant: both can be released", "the cycle is broken", None, 'lit'))]
S.append(slide("Part 6 &middot; Retain cycle &middot; conceptual", "Two objects that never let go", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    <div>
      {code("Ownership.swift", CYC, "font-size:14.5px")}
      <div class="gap"></div>
      <div class="rule step" data-label="The fix"><code>weak var tenant: Person?</code> The apartment no longer owns its tenant, so both instances are freed.</div>
    </div>
    <div>
      {svg("0 0 560 240", "Person and Apartment strongly reference each other; removing the outside variables leaks both; making tenant weak breaks the cycle", "s16cyc", P)}
      {cues(1)}
    </div>
  </div>""", notes(('SAY', 'Person strongly references its apartment and Apartment strongly references its tenant. Both are also reachable from outside variables. Click: set the outside variables to nil. The two instances still retain one another, so neither is released: a leak.'),
                  ('SAY', 'Click: make Apartment’s reference to its tenant weak, one word: weak var tenant. Now nothing keeps Person alive once the outside reference goes, and the cycle no longer prevents deallocation. With deinit messages in both classes, both would print.'),
                  ('CONNECT', 'Cycles between two classes are easy to spot. Cycles through closures are not.'))))

# ================================================================== 7 · closures
divider(7, "Retain cycles in closures", "One of the most common memory bugs",
        "A closure is a block of code that can capture values from its surrounding context, including self.", "Look at NPay&rsquo;s dashboard ViewModel.")
CL = '''@MainActor @Observable
final class DashboardViewModel {
    var onUpdate: (() -> Void)?

    func configure() {
        onUpdate = {
            print(self)       // captures self strongly
        }
    }

    deinit { print("DashboardViewModel destroyed") }
}'''
P = [box(0, 0, 250, 56, "External owner", ''), fade("0", wire(f'M125 56V92{head(125, 92, "d")}')),
     fade("1+", '<text class="sm" x="140" y="82">released</text>'),
     box(0, 98, 250, 70, "DashboardViewModel", "self", None, '', 'layout'), box(320, 98, 240, 70, "onUpdate closure", "", None, '', 'code'),
     wire(f'M250 120H314{head(314, 120, "r")}'), '<text class="sm" x="282" y="112" text-anchor="middle">owns</text>',
     wire(f'M320 150H256{head(256, 150, "l")}'), '<text class="sm" x="288" y="168" text-anchor="middle">captures self</text>',
     fade("1+", box(0, 196, 560, 50, "Still alive: the closure keeps the ViewModel", "a cycle without an outside owner", None, 'alert'))]
S.append(slide("Part 7 &middot; Closure cycle", "A closure that captures self", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {code("DashboardViewModel.swift", CL, "font-size:15px")}
    <div>
      {svg("0 0 560 248", "DashboardViewModel owns its onUpdate closure, which captures self strongly; after the external owner is released, the two keep each other alive", "s19clo", P)}
      {cues(1)}
    </div>
  </div>""", notes(('SAY', 'The ViewModel owns its onUpdate closure. The closure captures self strongly, and self is the ViewModel. Both keep each other alive.'),
                  ('SAY', 'Click: the external owner releases the ViewModel. The cycle remains, so deinit never runs.'),
                  ('CONNECT', 'The fix is a capture list.'))))
CLF = '''@MainActor @Observable
final class DashboardViewModel {
    var onUpdate: (() -> Void)?

    func configure() {
        onUpdate = { [weak self] in
            guard let self else { return }
            print(self)
        }
    }
}'''
S.append(slide("Part 7 &middot; Fix", "<code>[weak self]</code>", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("DashboardViewModel.swift", CLF, "font-size:15px")}
    <div>
      {stages([("<code>[weak self]</code>", "the closure no longer retains the ViewModel"), ("<code>guard let self</code>", "a temporary strong reference while the closure runs, if the object still exists")])}
    </div>
  </div>""", notes(('SAY', '[weak self] prevents the closure from retaining the ViewModel through its capture. guard let self temporarily obtains a strong reference while the closure executes, if the object still exists; otherwise it returns.'),
                  ('CONNECT', 'Compare the two captures side by side.'))))

# ================================================================== 8 · capture experiment
divider(8, "Strong versus weak capture", "Same code, one keyword different",
        "Let's compare what happens when the external owner goes away.", "Two captures, one per click.")
P = []
for i, (label, strong) in enumerate([("Strong capture", True), ("Weak capture", False)]):
    P.append(box(i * 290, 0, 270, 52, label, '', "0" if i == 0 else "1+"))
P += [box(0, 90, 260, 70, "ViewModel", "", None, '', 'layout'), box(420, 90, 260, 70, "Closure", "", None, '', 'code'),
      wire(f'M260 110H414{head(414, 110, "r")}'), '<text class="sm" x="337" y="102" text-anchor="middle">owns</text>',
      fade("0", wire(f'M420 142H266{head(266, 142, "l")}') + '<text class="sm" x="343" y="160" text-anchor="middle">strong capture</text>'),
      fade("1+", wire(f'M420 142H266{head(266, 142, "l")}', None, 'dash') + '<text class="sm" x="343" y="160" text-anchor="middle">weak capture</text>'),
      fade("0", box(0, 190, 680, 50, "External owner released: ViewModel stays alive", "strong ownership cycle", None, 'alert')),
      fade("1+", box(0, 190, 680, 50, "External owner released: ViewModel deallocated", "no cycle", None, 'lit'))]
S.append(slide("Part 8 &middot; Capture experiment &middot; conceptual", "Strong vs weak capture", f"""  <div class="body cols middle" style="grid-template-columns:1.25fr 1fr">
    {svg("0 0 690 242", "With strong capture the ViewModel stays alive after its external owner is released; with weak capture it is deallocated", "s22cap", P)}
    {cues(1)}
    <div class="rule step" data-label="Not for every closure"><code>[weak self]</code> matters for <b>escaping closures</b> that are retained and create a cycle. A short-lived, non-escaping closure does not need it.</div>
  </div>""", notes(('SAY', 'Strong capture: release the external owner and the ViewModel stays alive in an ownership cycle. Click: with weak capture, the same release lets the ViewModel be deallocated.'),
                  ('SAY', 'Do not teach [weak self] as mandatory for every closure. It matters for escaping closures retained in a way that creates an unwanted cycle or extends a lifetime beyond what is intended. A short-lived non-escaping closure does not automatically need it.'),
                  ('CONNECT', 'Weak is one way to break a cycle. When is unowned the right choice?'))))

# ================================================================== 9 · weak vs unowned
divider(9, "Weak versus unowned", "When should we use each?",
        "Both avoid retaining. They differ in what happens when the other object goes away.", "Two relationships to compare.")
S.append(slide("Part 9 &middot; Comparison", "strong vs weak vs unowned", """  <div class="body top">
    <table class="tbl" style="font-size:19px">
      <tr><th>Property</th><th>strong</th><th>weak</th><th>unowned</th></tr>
      <tr><td>Keeps object alive</td><td>Yes</td><td>No</td><td>No</td></tr>
      <tr><td>Becomes nil on deallocation</td><td>No</td><td>Yes</td><td>No (ordinary unowned)</td></tr>
      <tr><td>Common usage</td><td>Ownership</td><td>Optional back-reference</td><td>Guaranteed lifetime relationship</td></tr>
      <tr><td>Risk</td><td>Retain cycle</td><td>Reference may be nil</td><td>Access after deallocation traps</td></tr>
    </table>
    <div class="gap"></div>
    <div class="cols">
      <div class="card accent step"><span class="label">Weak: apartment and tenant</span><p class="small" style="margin:0">The tenant can move out, so the apartment&rsquo;s reference to its tenant is <b>weak</b>.</p></div>
      <div class="card accent step"><span class="label">Unowned: card and customer</span><p class="small" style="margin:0">A card cannot exist without its customer: an <b>unowned</b> candidate, only if that guarantee is truly enforced.</p></div>
    </div>
    <div class="gap"></div>
    <p class="small muted step">Reach for <b>weak</b> first. Lesson 1.8 covers <code>unowned</code> in depth, including <code>unowned(unsafe)</code>.</p>
  </div>""", notes(('SAY', 'Strong keeps the object alive; the risk is a retain cycle. Weak does not, and becomes nil on deallocation; the risk is that it may be nil. Unowned does not keep it alive and does not become nil; invalid access may crash.'),
                  ('SAY', 'The tenant can move out, so the apartment’s reference is weak. A credit card that cannot exist without its customer can hold an unowned reference back to it, provided that lifetime guarantee is enforced: the customer strongly owns the card, and the card is never used after the customer is gone.'),
                  ('SAY', 'Reach for weak first; use unowned only when the lifetime guarantee is real. Lesson 1.8 goes deeper, including unowned(unsafe), which removes the safety check and makes a bad access undefined behaviour.'),
                  ('CONNECT', 'Is every high-memory app leaking? No.'))))

# ================================================================== 10 · leak vs high usage
divider(10, "Memory leak versus high memory usage", "Not the same thing",
        "Two problems that are often confused.", "Compare them.")
S.append(slide("Part 10 &middot; Two problems", "Leak vs high usage", """  <div class="body">
    <div class="cols stretch">
      <div class="card accent step"><span class="label">Memory leak</span><p>Memory stays allocated though <b>no longer needed</b>, and cannot be reclaimed through the intended ownership path.</p></div>
      <div class="card step"><span class="label">High memory usage</span><p>The app uses a lot of memory. That may be <b>legitimate</b>, or a sign of excessive caching or allocation.</p></div>
    </div>
    <div class="gap"></div>
    <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-frame"/></svg></div><p>NPay keeps recent merchant logos in a <b>cache</b>: not a leak. But a cache that grows <b>without bounds</b> can still cause memory problems, even when everything stays reachable.</p></div>
  </div>""", notes(('SAY', 'A leak is memory that stays allocated though no longer needed and cannot be reclaimed through the intended ownership path. High memory usage may be legitimate, or may indicate excessive caching or allocation.'),
                  ('SAY', 'An app can use a lot of memory without leaking; and a small leak repeated thousands of times can eventually cause serious memory pressure. A merchant-logo cache is fine until it grows without bounds.'),
                  ('CONNECT', 'How do we find out which one we have?'))))

# ================================================================== 11 · Instruments
divider(11, "Detecting leaks with Xcode", "Memory Graph, Allocations and Leaks",
        "Xcode provides several tools for investigating memory.", "Start with the Memory Graph Debugger.")
S.append(slide("Part 11 &middot; Tools", "Three memory tools", """  <div class="body top">
    <table class="tbl" style="font-size:18px">
      <tr><th>Tool</th><th>Shows</th><th>Good at finding</th><th>Can miss</th></tr>
      <tr><td><b>Memory Graph Debugger</b></td><td>Live objects and who references them, at one moment</td><td>An instance that should be gone, and the <b>strong chain</b> holding it</td><td>Growth over time</td></tr>
      <tr><td><b>Instruments: Allocations</b></td><td>Allocations and growth over time; mark <b>generations</b> between repeated actions</td><td>Memory that keeps growing each time you repeat an action</td><td>Which reference holds an object</td></tr>
      <tr class="hl"><td><b>Instruments: Leaks</b></td><td>Memory nothing can reach any more</td><td>Unreachable memory, including <b>unreachable cycles</b></td><td>Memory still <b>reachable</b> but no longer needed: a running timer, an unbounded cache</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step">An object kept alive by something still reachable is <b>not</b> a leak to the Leaks instrument. Find it with the Memory Graph and Allocations generations.</div>
  </div>""", notes(('SAY', 'Three tools. The Memory Graph Debugger shows live objects and who references them at one moment, so you can find an instance that should be gone and the strong chain holding it. Allocations shows allocation patterns and growth over time; mark a generation, repeat an action, and see what stayed. Leaks reports memory that nothing can reach any more, including cycles that are no longer reachable from your code.'),
                  ('SAY', 'What Leaks cannot see is abandoned memory that is still reachable: an object kept alive by a running timer or an unbounded cache. That is where the Memory Graph and generations come in.'),
                  ('LIVE DEMO', 'Open a screen that creates a ViewModel, navigate away, check whether deinit runs; if it does not, open the Memory Graph and find the strong-reference chain keeping it alive. Then in Instruments, Allocations: mark a generation, open and close the screen five times, and show the growth. A missing deinit alone does not prove a leak: the object may be intentionally owned.'),
                  ('CONNECT', 'Here is a repeatable sequence for any suspected leak.'))))
seq = [("Reproduce", "the suspected leak"), ("Observe", "memory growth or missing deinit"), ("Inspect", "Memory Graph and ownership"),
       ("Identify", "the unexpected strong reference"), ("Correct", "ownership or lifecycle handling"), ("Verify", "repeat the test")]
P = []
for i, (t, sub) in enumerate(seq):
    r, c = divmod(i, 3)
    x, y = c * 392, r * 110
    P.append(row(x, y, 352, 66, '', f"{i + 1}. {t}", sub, str(i + 1)))
    if c < 2:
        P.append(wire(f'M{x + 358} {y + 33}H{x + 386}{head(x + 386, y + 33, "r")}'))
P.append(wire(f'M960 66V88H176V104{head(176, 104, "d")}'))
S.append(slide("Part 11 &middot; Debugging sequence", "Six steps for a suspected leak", f"""  <div class="body">
    {svg("0 0 1136 178", "Reproduce, observe, inspect the memory graph, identify the strong reference, correct ownership, verify", "s30seq", P)}
    {cues(6)}
    <div class="gap"></div>
    <p class="small muted">A missing deinit message alone does not prove a leak: the object may still be intentionally owned.</p>
  </div>""", notes(('SAY', 'Click through: reproduce the suspected leak; observe memory growth or a missing deinit; inspect the Memory Graph and ownership; identify the unexpected strong reference; correct the ownership or lifecycle handling; then repeat the test and verify.'),
                  ('CONNECT', 'A real-world case: the repeating timer.'))))

# ================================================================== 12 · timer
divider(12, "Real-world example: a timer", "A retain cycle hiding in plain sight",
        "A repeating timer can keep an object alive if its closure strongly captures that object.", "Here is the code.")
TM = '''@MainActor @Observable
final class DashboardViewModel {
    var timer: Timer?
    func startAutoRefresh() {
        timer = Timer.scheduledTimer(withTimeInterval: 30,
                                     repeats: true) { _ in
            MainActor.assumeIsolated { self.refreshBalance() }
        }
    }
    func refreshBalance() { print("Refreshing balance") }
    deinit { print("destroyed") }   // never prints
}'''
P = [box(0, 0, 230, 60, "Run loop", "keeps scheduled timers", None, '', 'thread'), box(290, 0, 190, 60, "Timer", "repeating", None, '', 'clock'),
     box(540, 0, 200, 60, "Closure", "captures self", None, '', 'code'), box(800, 0, 336, 60, "DashboardViewModel", "self", None, 'lit', 'layout'),
     wire(f'M230 30H284{head(284, 30, "r")}'), wire(f'M480 30H534{head(534, 30, "r")}'), wire(f'M740 30H794{head(794, 30, "r")}'),
     wire(f'M968 60V92H385V66{head(385, 66, "u")}', None, 'dash'), '<text class="sm" x="676" y="110" text-anchor="middle">the ViewModel holds the timer only so it can invalidate it</text>']
S.append(slide("Part 12 &middot; Timer cycle", "A repeating timer that never lets go", f"""  <div class="body">
    {svg("0 0 1136 116", "The run loop retains the scheduled timer, the timer retains its closure, and the closure retains the DashboardViewModel; the ViewModel's own timer property only lets it invalidate the timer", "s33tim", P)}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:1.25fr 1fr;align-items:center">
      {code("DashboardViewModel.swift", TM, "font-size:12.5px;line-height:1.35;padding:12px 18px")}
      <div class="rule step" data-label="The trap">The <b>run loop</b> keeps a repeating timer alive until <code>invalidate()</code>. Through the closure, it keeps the ViewModel alive too, so <code>deinit</code> never runs and cleanup there never happens.</div>
    </div>
  </div>""", notes(('SAY', 'NPay refreshes the balance every 30 seconds. Follow the chain: the run loop keeps a scheduled repeating timer alive until it is invalidated; the timer retains its closure; the closure captures self strongly. So the ViewModel stays alive even after the dashboard is gone, and the timer keeps firing.'),
                  ('SAY', 'The ViewModel’s own timer property is not what keeps the timer alive; the run loop is. The property only lets the ViewModel invalidate it. That is why putting invalidate() in deinit cannot work: deinit never runs while the chain exists.'),
                  ('SAY', 'Two Swift 6 details: the timer block is a Sendable closure, so the ViewModel is @MainActor, and because the timer was scheduled on the main run loop, its block runs on the main thread, so MainActor.assumeIsolated is safe there.'),
                  ('CONNECT', 'So what is the safer design?'))))
TMF = '''func startAutoRefresh() {
    timer = Timer.scheduledTimer(withTimeInterval: 30,
                                 repeats: true) { [weak self] _ in
        MainActor.assumeIsolated { self?.refreshBalance() }
    }
}

func stopAutoRefresh() {   // call when the dashboard goes away
    timer?.invalidate()
    timer = nil
}'''
S.append(slide("Part 12 &middot; Fix", "Weak capture and explicit cancellation", f"""  <div class="body cols middle" style="grid-template-columns:1.25fr 1fr">
    {code("DashboardViewModel.swift", TMF, "font-size:13.5px")}
    <div>
      {points([("code", "Weak capture", "the closure no longer keeps the ViewModel alive"), ("clock", "Explicit invalidation", "the run loop lets go of the timer, and it stops firing")], cls="v", label="Two related fixes", step=False)}
      <div class="gap"></div>
      <div class="rule step">They solve <b>related but distinct</b> problems: ownership versus ongoing activity.</div>
    </div>
  </div>""", notes(('SAY', 'Weak capture stops the closure owning the ViewModel, so it can be deallocated. But the run loop still holds the timer, and it would keep firing with a nil self. Explicit invalidation in stopAutoRefresh, called when the dashboard goes away, for example from onDisappear, stops that activity. Related but distinct problems; you usually need both.'),
                  ('SAY', 'A modern alternative is a Task loop that sleeps between refreshes and is cancelled when the screen goes away. Lesson 8.3 covers task lifetimes and cancellation.'),
                  ('CONNECT', 'Before the review, what to remember.'))))

S.append(recap_slide('0.6', ('memory',), [("layers", "Value vs reference", "structs give independent values; classes share one instance"),
                                           ("memory", "ARC", "strong references keep a class instance alive"),
                                           ("link", "Cycles", "break them with weak; stop timers explicitly")],
                     'Three things to keep. Value versus reference semantics is the reliable distinction, not stack versus heap. ARC keeps a class instance alive while strong references exist. And cycles, through properties, closures or timers, are broken with weak references and explicit cancellation.'))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("memory", "What keeps a class instance alive under ARC?<br>A. Any reference to it<br>B. At least one strong reference<br>C. Being allocated on the heap<br>D. Being declared with <code>let</code>",
       "What keeps a class instance alive under ARC?", "B",
       "Only strong references keep an instance alive. Weak and unowned references do not, and where it is allocated or how the variable is declared has nothing to do with it.",
       "Thinking any reference keeps an object alive.", "Most choose B; some pick A. Ask why a weak reference does not count."),
      ("code", "What prints, in order?<br><code style=\"font-size:18px\">var a: Customer? = Customer(name: \"Ravi\")</code><br><code style=\"font-size:18px\">var b = a</code><br><code style=\"font-size:18px\">a = nil; print(\"after a\")</code><br><code style=\"font-size:18px\">b = nil; print(\"after b\")</code>",
       "What prints, in order, when two variables share one Customer?", "after a &rarr; Customer destroyed &rarr; after b",
       "Setting <code>a</code> to nil leaves <code>b</code> holding the instance. Only <code>b = nil</code> removes the last strong reference, so deinit prints between the two lines.",
       "Expecting deinit to print as soon as the first variable is set to nil.", "Some put Customer destroyed first."),
      ("link", "Can two class instances that strongly retain each other stay alive after external references disappear?",
       "Can two instances that retain each other outlive their external references?", "Yes",
       "That is a retain cycle: each keeps the other alive, so neither is deallocated.", "Assuming ARC detects and breaks cycles.", "Some expect ARC to clean it up, as a garbage collector might."),
      ("code", "Should every closure capture <code>self</code> weakly?", "Should every closure capture self weakly?", "No",
       "Weak capture matters for escaping closures that create an unwanted cycle. Short-lived non-escaping closures do not need it.", "Adding [weak self] everywhere by reflex.", "Many say yes after this lesson; push back."),
      ("thread", "A repeating <code>Timer</code> is scheduled from the main thread. On which thread does its block run?",
       "On which thread does a timer scheduled from the main thread fire?", "The main thread",
       "A scheduled timer is added to the current thread&rsquo;s run loop. Scheduled from the main thread, it fires on the main run loop, which is why <code>MainActor.assumeIsolated</code> is safe in NPay&rsquo;s refresh timer.",
       "Assuming timers fire on a background thread.", "Spaced review from 0.5 (main thread and RunLoop). Some guess a background thread.")]
N = len(QA)
for i, (ic, q, title, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    S.append(f"""<section class="slide question" data-title="{E(title, quote=True)}">
  <div class="q-top">
    <p class="kicker">Check your understanding &middot; {i + 1} of {N}</p>
    <div class="q-dots" aria-hidden="true">{dots}</div>
  </div>
  <div class="body">
    <div class="q-row">
      <div class="q-card">
        <div class="q-icon"><svg viewBox="0 0 24 24"><use href="#i-{ic}"/></svg></div>
        <span class="label">Question</span>
        {qhtml(q)}
      </div>
      <div class="q-panel">
        <div class="q-ans step anim-up">
          <span class="q-verdict">{v}</span>
          <p class="q-why">{why}</p>
          <p class="q-trap"><b>Common trap:</b> {trap}</p>
        </div>
      </div>
    </div>
  </div>
""" + notes(('ASK', 'Give everyone a few seconds, then take a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next question.' if i < N - 1 else 'Where this goes next.')) + "</section>\n\n")

S.append(next_slide('0.6', [('1.4', 'Functions, parameters &amp; closures', 'closures, captures and capture lists'),
                           ('1.5', 'Structs, classes &amp; value semantics', 'copy-on-write; choosing struct or class'),
                           ('1.8', 'ARC, ownership &amp; memory management', 'unowned and ownership in depth'),
                           ('8.3', 'Task lifetimes &amp; cancellation', 'a Task loop instead of a Timer'),
                           ('8.8', 'Memory, ARC &amp; energy optimization', 'reducing NPay&rsquo;s footprint'),
                           ('8.9', 'Instruments &amp; measurement', 'Allocations and Leaks in practice')],
                    'Today was the foundation. Unit 01 returns to closures, value semantics and ownership in the language itself, and Unit 08 measures and optimizes memory in a real NPay build.'))
LAB = '''final class ScreenModel {
    let name: String
    var onRefresh: (() -> Void)?
    init(name: String) { self.name = name }
    func start() { onRefresh = { print("refresh \\(self.name)") } }
    deinit { print("\\(name) deinit") }
}

func open(_ name: String, start: Bool) {
    let model = ScreenModel(name: name)
    if start { model.start() }
}
open("Dashboard", start: false); open("Statements", start: true)'''
lab = lab_slide('0.6', 'Find the missing deinit', 'A Swift command-line program, no Xcode project needed.',
                ['Save the code as <code>cycle.swift</code>.', '<b>Predict</b> which <code>deinit</code> lines print.',
                 'Run <code>swiftc cycle.swift -o cycle &amp;&amp; ./cycle</code>', 'Fix it with <code>[weak self]</code>, run again, and explain the difference.'],
                '', 'Two screens open and close. Only one of them starts a refresh closure. Predict first, then run it, then fix it.',
                side=code("cycle.swift", LAB, "font-size:13px") + '<div class="gap"></div><div class="card accent"><span class="label">You hand in</span><p class="small" style="margin:0">Your prediction, both outputs, and one sentence on why one <code>deinit</code> was missing.</p></div>')
S.append(lab.replace('    <span class="notes-label">CONNECT</span>', '    <span class="notes-label">EXPECT</span><p>First run prints only "Dashboard deinit": the Statements model owns its onRefresh closure, which captures self strongly, so it is never freed. After changing the closure to { [weak self] in guard let self else { return }; print("refresh \\(self.name)") } both "Dashboard deinit" and "Statements deinit" print. Runs with any Swift toolchain (macOS, Linux or Windows).</p>\n    <span class="notes-label">CONNECT</span>'))
S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.6 complete</p>
    <h2>iOS Memory<br>Architecture &amp; ARC</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.7 &mdash; iOS Security Architecture</p>
  </div>
""" + notes(('SAY', 'We have now connected iOS process architecture, lifecycle, the main thread, concurrency and memory management. You can explain value and reference semantics, how ARC manages lifetimes, why strong-reference cycles occur, how weak and unowned differ, why closures and timers can retain objects, and how to investigate retention in Xcode.'),
            ('SAY', 'Next, Lesson 0.7: how iOS protects applications, and NPay’s secrets, from one another.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.6 — iOS Memory Architecture &amp; ARC</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.6 — iOS Memory Architecture &amp; ARC">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT06, 'w').write(doc)
print(len(S), 'slides')
