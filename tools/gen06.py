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
                 ('CONNECT', 'Why does an app need memory at all?'))))

# ================================================================== 1 · process memory
divider(1, "Why does an app need memory?", "How iOS organizes process memory",
        "A shopping app needs memory for its product list, cart, user information, images, network responses and interface state. Some data lives only while a function runs; other data must survive many calls.", "Here is how the process memory is organized.")
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
        <p>A large <b>office building</b> is the address space. <b>Temporary desks</b> hold immediate work; <b>shared storage</b> holds what is needed longer.</p>
      </div>
      <div class="gap"></div>
      <p class="small step">The OS provides the virtual memory environment; the language runtime and the app manage allocations inside it.</p>
    </div>
  </div>""", notes(('SAY', 'Click through the five regions: code, global and static data, the heap for dynamic objects, thread stacks for call frames, and other mapped memory such as libraries and graphics mappings. These are conceptual regions in virtual memory, not fixed slices of RAM.'),
                  ('SAY', 'Think of an office building. The building is the address space; different rooms serve different purposes. Temporary desks are for immediate work; shared storage areas hold things needed longer.'),
                  ('CONNECT', 'Two of those regions matter most for us: the stack and the heap.'))))

# ================================================================== 2 · stack vs heap
divider(2, "Stack versus heap", "Temporary desks and shared storage",
        "Start with a simple function and ask where its values live.", "Here is the function.")
CALC = '''func calculateTotal() {
    let price = 100
    let quantity = 3
    let total = price * quantity

    print(total)
}

calculateTotal()'''
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
  </div>""", notes(('SAY', 'calculateTotal needs temporary execution storage for price, quantity and total. Click: the stack, tied to function calls and thread execution, with the call frame, temporary values and return information. Click: the heap, for dynamically allocated storage and objects.'),
                  ('SAY', 'The stack is typically efficient for call-related storage; heap allocation is more flexible but needs allocation and lifetime management.'),
                  ('CONNECT', 'A warning before we go further.'))))
S.append(slide("Part 2 &middot; Swift nuance", "Not simply stack versus heap", """  <div class="body">
    <div class="cols stretch">
      <div class="card step"><span class="label">Common belief</span><p>&ldquo;Structs live on the stack; classes live on the heap.&rdquo;</p></div>
      <div class="card accent step"><span class="label">In Swift</span><p>A struct is <b>not guaranteed</b> to live on the stack, and a class reference variable is <b>not necessarily</b> on the heap. Placement depends on implementation and optimization.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="The reliable distinction"><b>Value semantics</b> versus <b>reference semantics</b>, not simply stack versus heap.</div>
  </div>""", notes(('SAY', 'Developers from other languages often learn "structs on the stack, classes on the heap". In Swift that is not a guarantee: storage placement depends on the implementation and optimization.'),
                  ('SAY', 'The reliable language-level distinction is value semantics versus reference semantics.'),
                  ('CONNECT', 'So what do value and reference semantics mean in practice?'))))

# ================================================================== 3 · structs vs classes
divider(3, "Swift structs versus classes", "Value type versus reference type",
        "A struct is a value type; a class is a reference type. Let's see what that means with the same Account written both ways.", "First, the struct.")
SA = '''struct Account {
    var balance: Int
}

var accountA = Account(balance: 5000)
var accountB = accountA

accountB.balance = 9000

print(accountA.balance) // 5000
print(accountB.balance) // 9000'''
P = [box(0, 0, 250, 80, "accountA", "&#8377;5,000"), box(300, 0, 250, 80, "accountB", "&#8377;5,000"),
     fade("1+", box(300, 0, 250, 80, "accountB", "&#8377;9,000", None, 'lit')),
     '<text class="sm" x="0" y="116">Each variable holds its own value.</text>']
S.append(slide("Part 3 &middot; Value type", "A struct: independent values", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Account.swift", SA, "font-size:16px")}
    <div>
      {svg("0 0 560 124", "accountA and accountB both hold 5,000 rupees; changing accountB to 9,000 leaves accountA at 5,000", "s8val", P)}
      {cues(1)}
      <div class="gap"></div>
      <div class="rule step">Assigning <code>accountA</code> to <code>accountB</code> gives <b>independent values</b>.</div>
    </div>
  </div>""", notes(('SAY', 'accountB starts as a copy of accountA. Click: we change accountB to &#8377;9,000; accountA still shows &#8377;5,000. Each variable changes separately.'),
                  ('CONNECT', 'Now the same code with a class.'))))
CA = '''class Account {
    var balance: Int

    init(balance: Int) {
        self.balance = balance
    }
}

let accountA = Account(balance: 5000)
let accountB = accountA

accountB.balance = 9000

print(accountA.balance) // 9000
print(accountB.balance) // 9000'''
P = [box(0, 0, 200, 56, "accountA", "reference"), box(0, 110, 200, 56, "accountB", "reference"),
     wire(f'M200 28H270V70H316{head(316, 70, "r")}'), wire(f'M200 138H270V96H316{head(316, 96, "r")}'),
     box(322, 44, 230, 78, "Account instance", "&#8377;5,000"),
     fade("1+", box(322, 44, 230, 78, "Account instance", "&#8377;9,000", None, 'lit')),
     '<text class="sm" x="0" y="196">Both references observe the same balance.</text>']
S.append(slide("Part 3 &middot; Reference type", "A class: one shared instance", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Account.swift", CA, "font-size:14.5px")}
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
    <div class="rule step" data-label="Copy-on-write">Value types can share storage internally. Value semantics does not always mean <b>copying every byte</b> immediately.</div>
  </div>""", notes(('SAY', 'Six differences. The last row leads into the rest of this lesson: class instance lifetimes are managed by ARC.'),
                  ('SAY', 'Copy-on-write: value types can internally share storage until one copy is modified, so value semantics does not always mean immediately copying all the underlying bytes.'),
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
      <div class="analogy"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div><p>Each strong reference is someone holding a <b>booking</b> for a conference room. When nobody holds it, the room is <b>released</b>.</p></div>
      <p class="small muted">Conceptual. The compiler and runtime may optimize reference-count operations; they are not necessarily visible one-for-one.</p>
    </div>
  </div>""", notes(('SAY', 'ARC tracks strong references to a class instance. When no strong references keep it alive, it can be deinitialized. Click through: three references, then two, then one, then none, and the object can be destroyed.'),
                  ('SAY', 'An object is like a rented conference room; each strong reference is someone holding a valid booking. When nobody holds the room, it can be released.'),
                  ('CONNECT', "Now the same thing in Swift code."))))
CUST = '''class Customer {
    let name: String

    init(name: String) {
        self.name = name
        print("Customer created")
    }

    deinit {
        print("Customer destroyed")
    }
}

var customer1: Customer? = Customer(name: "Ravi")
var customer2 = customer1

customer1 = nil
// Object is still alive through customer2

customer2 = nil
// No strong references remain
// deinit can execute'''
S.append(slide("Part 4 &middot; ARC in code", "Setting one reference to nil", f"""  <div class="body cols middle" style="grid-template-columns:1.3fr 1fr">
    {code("Customer.swift", CUST, "font-size:13px;line-height:1.36;padding:12px 20px")}
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
S.append(slide("Part 5 &middot; Reference kinds", "Strong, weak and unowned", """  <div class="body">
    <div class="cols c3 stretch">
      <div class="card accent step"><span class="label">Strong</span><p>Keeps the instance <b>alive</b>. Strong ownership is the <b>default</b>.</p></div>
      <div class="card accent step"><span class="label">Weak</span><p>Does <b>not</b> keep it alive. Optional, and automatically becomes <b>nil</b> when the instance is deallocated.</p></div>
      <div class="card accent step"><span class="label">Unowned</span><p>Does <b>not</b> retain it. Assumes the instance is <b>still alive</b> whenever accessed; violating that can crash.</p></div>
    </div>
    <div class="gap"></div>
    <p class="small step">A parent usually <b>strongly owns</b> a child. A child may hold a <b>weak</b> reference back to a parent that can disappear independently. Use <b>unowned</b> only when the lifetime relationship guarantees safe access.</p>
    <div class="rule step" data-label="Do not overcorrect">Do not replace every strong reference with weak. Strong ownership is <b>normal and necessary</b>.</div>
  </div>""", notes(('SAY', 'Strong keeps the instance alive and is the default. Weak does not keep it alive; it is optional and becomes nil automatically when the instance is deallocated. Unowned does not retain it either, but assumes the instance is still alive whenever accessed; violating that assumption can cause a runtime failure.'),
                  ('SAY', 'A parent usually strongly owns a child; the child may hold a weak back-reference. And do not teach students to replace every strong reference with weak: weak and unowned solve particular lifetime relationships.'),
                  ('CONNECT', 'What goes wrong when two objects own each other?'))))

# ================================================================== 6 · retain cycles
divider(6, "Retain cycles", "The classic ARC problem",
        "Imagine two people holding each other's hands and refusing to let go.", "In Swift, two class instances can do the same.")
CYC = '''class Person {
    var apartment: Apartment?
}

class Apartment {
    var tenant: Person?
}

var person: Person? = Person()
var apartment: Apartment? = Apartment()

person?.apartment = apartment
apartment?.tenant = person

person = nil
apartment = nil'''
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
    {code("Ownership.swift", CYC, "font-size:13.5px;line-height:1.38")}
    <div>
      {svg("0 0 560 240", "Person and Apartment strongly reference each other; removing the outside variables leaks both; making tenant weak breaks the cycle", "s16cyc", P)}
      {cues(2)}
    </div>
  </div>""", notes(('SAY', 'Person strongly references its apartment and Apartment strongly references its tenant. Both are also reachable from outside variables. Click: set the outside variables to nil. The two instances still retain one another, so neither is released: a leak.'),
                  ('SAY', 'Click: make Apartment’s reference to its tenant weak. Now nothing keeps Person alive once the outside reference goes, and the cycle no longer prevents deallocation.'),
                  ('CONNECT', 'Here is the fix in code.'))))
FIX = '''class Person {
    var apartment: Apartment?

    deinit {
        print("Person deinitialized")
    }
}

class Apartment {
    weak var tenant: Person?

    deinit {
        print("Apartment deinitialized")
    }
}'''
S.append(slide("Part 6 &middot; Fix", "Break the cycle with weak", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Ownership.swift", FIX, "font-size:15px")}
    <div>
      <p>The apartment no longer <b>strongly owns</b> its tenant.</p>
      <div class="gap"></div>
      <div class="rule step">When the external strong references are released, the cycle <b>no longer prevents deallocation</b>. Both deinit messages print.</div>
    </div>
  </div>""", notes(('SAY', 'One word changes: weak var tenant. The apartment no longer strongly owns its tenant, so once the outside references are released, both objects can be deinitialized and both messages print.'),
                  ('CONNECT', 'Cycles between two classes are easy to spot. Cycles through closures are not.'))))

# ================================================================== 7 · closures
divider(7, "Retain cycles in closures", "One of the most common memory bugs",
        "A closure is a block of code that can capture values from its surrounding context, including self.", "Look at this ViewModel.")
CL = '''class ProfileViewModel {

    var onUpdate: (() -> Void)?

    func configure() {
        onUpdate = {
            print(self)
        }
    }

    deinit {
        print("ProfileViewModel destroyed")
    }
}'''
P = [box(0, 0, 250, 56, "External owner", ''), fade("0", wire(f'M125 56V92{head(125, 92, "d")}')),
     fade("1+", '<text class="sm" x="140" y="82">released</text>'),
     box(0, 98, 250, 70, "ProfileViewModel", "self", None, '', 'layout'), box(320, 98, 240, 70, "onUpdate closure", "", None, '', 'code'),
     wire(f'M250 120H314{head(314, 120, "r")}'), '<text class="sm" x="282" y="112" text-anchor="middle">owns</text>',
     wire(f'M320 150H256{head(256, 150, "l")}'), '<text class="sm" x="288" y="168" text-anchor="middle">captures self</text>',
     fade("1+", box(0, 196, 560, 50, "Still alive: the closure keeps the ViewModel", "a cycle without an outside owner", None, 'alert'))]
S.append(slide("Part 7 &middot; Closure cycle", "A closure that captures self", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {code("ProfileViewModel.swift", CL, "font-size:15px")}
    <div>
      {svg("0 0 560 248", "ProfileViewModel owns its onUpdate closure, which captures self strongly; after the external owner is released, the two keep each other alive", "s19clo", P)}
      {cues(1)}
    </div>
  </div>""", notes(('SAY', 'The ViewModel owns its onUpdate closure. The closure captures self strongly, and self is the ViewModel. Both keep each other alive.'),
                  ('SAY', 'Click: the external owner releases the ViewModel. The cycle remains, so deinit never runs.'),
                  ('CONNECT', 'The fix is a capture list.'))))
CLF = '''class ProfileViewModel {

    var onUpdate: (() -> Void)?

    func configure() {
        onUpdate = { [weak self] in
            guard let self else { return }
            print(self)
        }
    }

    deinit {
        print("ProfileViewModel destroyed")
    }
}'''
S.append(slide("Part 7 &middot; Fix", "<code>[weak self]</code>", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("ProfileViewModel.swift", CLF, "font-size:15px")}
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
      <tr><td>Risk</td><td>Retain cycle</td><td>Reference may be nil</td><td>Invalid access may crash</td></tr>
    </table>
    <div class="gap"></div>
    <div class="cols">
      <div class="card accent step"><span class="label">Weak: apartment and tenant</span><p class="small" style="margin:0">The tenant can move out, so the apartment&rsquo;s reference to its tenant is <b>weak</b>.</p></div>
      <div class="card accent step"><span class="label">Unowned: card and customer</span><p class="small" style="margin:0">A card cannot exist without its customer: an <b>unowned</b> candidate, if that guarantee is enforced.</p></div>
    </div>
  </div>""", notes(('SAY', 'Strong keeps the object alive; the risk is a retain cycle. Weak does not, and becomes nil on deallocation; the risk is that it may be nil. Unowned does not keep it alive and does not become nil; invalid access may crash.'),
                  ('SAY', 'The tenant can move out, so the apartment’s reference is weak. A credit card that cannot exist without its customer can be unowned, provided that lifetime guarantee is enforced.'),
                  ('CONNECT', 'Here is the card in code.'))))
CARD = '''class Customer {
    let name: String
    var card: CreditCard?

    init(name: String) {
        self.name = name
    }
}

class CreditCard {
    let number: String
    unowned let customer: Customer

    init(number: String, customer: Customer) {
        self.number = number
        self.customer = customer
    }
}'''
S.append(slide("Part 9 &middot; unowned", "A card that cannot outlive its customer", f"""  <div class="body cols middle" style="grid-template-columns:1.2fr 1fr">
    {code("CreditCard.swift", CARD, "font-size:14.5px")}
    <div>
      <div class="rule step" data-label="Only if">Safe only if the card is <b>never accessed</b> after its customer has been deallocated.</div>
      <div class="gap"></div>
      <p class="small step">Teach <b>weak first</b>. Introduce unowned only once students understand lifetime guarantees.</p>
    </div>
  </div>""", notes(('SAY', 'The customer strongly owns the card; the card holds an unowned reference back. This design is safe only if the card is never accessed after its customer has been deallocated.'),
                  ('SAY', 'Introduce weak first, and teach unowned only after students understand lifetime guarantees.'),
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
    <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-frame"/></svg></div><p>A photo app keeps recent images in a <b>cache</b>: not a leak. But a cache that grows <b>without bounds</b> can still cause memory problems, even when everything stays reachable.</p></div>
  </div>""", notes(('SAY', 'A leak is memory that stays allocated though no longer needed and cannot be reclaimed through the intended ownership path. High memory usage may be legitimate, or may indicate excessive caching or allocation.'),
                  ('SAY', 'An app can use a lot of memory without leaking; and a small leak repeated thousands of times can eventually cause serious memory pressure. An image cache is fine until it grows without bounds.'),
                  ('CONNECT', 'How do we find out which one we have?'))))

# ================================================================== 11 · Instruments
divider(11, "Detecting leaks with Xcode", "Memory Graph, Allocations and Leaks",
        "Xcode provides several tools for investigating memory.", "Start with the Memory Graph Debugger.")
S.append(slide("Part 11 &middot; Tools", "Three memory tools", """  <div class="body cols stretch">
    <div class="card accent step"><span class="label">Memory Graph Debugger</span><p class="small">Inspect object relationships and find instances that <b>remain alive unexpectedly</b>.</p></div>
    <div class="card accent step"><span class="label">Instruments: Allocations</span><p class="small">Allocation patterns, object <b>lifetimes</b> and memory <b>growth</b>.</p></div>
    <div class="card accent step"><span class="label">Instruments: Leaks</span><p class="small">Detects certain leaked allocations. Objects still reachable through a <b>cycle</b> may not be reported.</p></div>
  </div>""".replace('<div class="body cols stretch">', '<div class="body cols c3 stretch">'), notes(('SAY', 'The Memory Graph Debugger shows object relationships, so you can find instances that stay alive unexpectedly. Allocations shows allocation patterns, lifetimes and growth. Leaks detects certain leaked allocations, but not every unwanted retained object is reported, especially one still reachable through a reference cycle.'),
                  ('LIVE DEMO', 'Open a screen that creates a ViewModel, navigate away, check whether deinit runs; if it does not, open the Memory Graph and find the strong-reference chain keeping it alive. A missing deinit alone does not prove a leak: the object may be intentionally owned.'),
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
TM = '''class DashboardController {

    var timer: Timer?

    func startTimer() {
        timer = Timer.scheduledTimer(
            withTimeInterval: 1,
            repeats: true
        ) { _ in
            self.refreshDashboard()
        }
    }

    func refreshDashboard() {
        print("Refreshing...")
    }

    deinit {
        timer?.invalidate()
        print("Dashboard destroyed")
    }
}'''
P = [box(0, 0, 240, 60, "Timer infrastructure", ""), box(300, 0, 200, 60, "Timer", "", None, '', 'clock'),
     box(560, 0, 200, 60, "Closure", "", None, '', 'code'), box(820, 0, 316, 60, "DashboardController", "self", None, '', 'layout'),
     wire(f'M240 30H294{head(294, 30, "r")}'), wire(f'M500 30H554{head(554, 30, "r")}'), wire(f'M760 30H814{head(814, 30, "r")}'),
     wire(f'M978 60V92H400V66{head(400, 66, "u")}'), '<text class="sm" x="689" y="110" text-anchor="middle">the controller also holds the timer</text>']
S.append(slide("Part 12 &middot; Timer cycle", "A repeating timer that never lets go", f"""  <div class="body">
    {svg("0 0 1136 116", "Timer infrastructure retains the timer, the timer retains its closure, the closure retains the controller, and the controller holds the timer", "s33tim", P)}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:1.2fr 1fr;align-items:center">
      {code("DashboardController.swift", TM, "font-size:11.5px;line-height:1.3;padding:10px 18px")}
      <div class="rule step" data-label="The trap"><code>deinit</code> cleanup cannot help if the cycle stops <code>deinit</code> from <b>ever running</b>.</div>
    </div>
  </div>""", notes(('SAY', 'The timer infrastructure retains the timer, the timer retains its closure, and the closure retains self. The controller also holds a reference to the timer. This can prevent the controller from ever being released.'),
                  ('SAY', 'The invalidate call in deinit looks like cleanup, but it cannot solve the problem if the cycle prevents deinit from running in the first place.'),
                  ('CONNECT', 'So what is the safer design?'))))
TMF = '''func startTimer() {
    timer = Timer.scheduledTimer(
        withTimeInterval: 1,
        repeats: true
    ) { [weak self] _ in
        self?.refreshDashboard()
    }
}

func stopTimer() {
    timer?.invalidate()
    timer = nil
}'''
S.append(slide("Part 12 &middot; Fix", "Weak capture and explicit cancellation", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("DashboardController.swift", TMF, "font-size:16px")}
    <div>
      {points([("code", "Weak capture", "addresses the closure owning self"), ("clock", "Explicit invalidation", "stops the timer when the feature no longer needs it")], cls="v", label="Two related fixes", step=False)}
      <div class="gap"></div>
      <div class="rule step">They solve <b>related but distinct</b> problems: ownership versus ongoing activity.</div>
    </div>
  </div>""", notes(('SAY', 'Weak capture addresses the closure’s ownership of self. Explicit invalidation, in stopTimer, addresses the timer’s continuing activity when the feature no longer needs it. Related, but distinct problems; you usually need both.'),
                  ('CONNECT', "Let's check your understanding."))))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Four questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("layers", "Does assigning a Swift struct to another variable always create an immediate deep copy of all storage?", "No",
       "Value semantics are guaranteed, but storage may be shared until a copy is modified (copy-on-write).", "Equating value semantics with copying every byte.", "Many say yes."),
      ("memory", "What keeps a class instance alive under ARC?", "Strong references",
       "Weak references do not keep it alive, and its class name has nothing to do with lifetime.", "Thinking any reference keeps an object alive.", "Most get this; ask why a weak reference does not count."),
      ("link", "Can two class instances that strongly retain each other stay alive after external references disappear?", "Yes",
       "That is a retain cycle: each keeps the other alive, so neither is deallocated.", "Assuming ARC detects and breaks cycles.", "Some expect ARC to clean it up, as a garbage collector might."),
      ("code", "Should every closure capture <code>self</code> weakly?", "No",
       "Weak capture matters for escaping closures that create an unwanted cycle. Short-lived non-escaping closures do not need it.", "Adding [weak self] everywhere by reflex.", "Many say yes after this lesson; push back.")]
N = len(QA)
for i, (ic, q, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    title = html.unescape(re.sub('<[^>]+>', '', q))
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
        <p class="q-text">{q}</p>
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
            ('CONNECT', 'Next question.' if i < N - 1 else 'That completes the lesson.')) + "</section>\n\n")

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.6 complete</p>
    <h2>iOS Memory<br>Architecture &amp; ARC</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: how iOS protects apps from one another</p>
  </div>
""" + notes(('SAY', 'We have now connected iOS process architecture, lifecycle, the main thread, concurrency and memory management. You can explain value and reference semantics, how ARC manages lifetimes, why strong-reference cycles occur, how weak and unowned differ, why closures and timers can retain objects, and how to investigate retention in Xcode.'),
            ('SAY', 'The next natural foundation is how iOS protects applications from one another.')) + "</section>\n\n")

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
