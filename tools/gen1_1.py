"""Generates decks/unit-1/lesson-1.1/index.html from the Lesson 1.1 text (PocketBank -> NPay)."""
import html, os, re, sys
OUT11 = sys.argv[1]
sys.argv = ['x', '/dev/null']
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
cues = lambda n: '<i class="step cue"></i>' * n
box = lambda x, y, w, h, t, sub='', l=None, cls='', icon='': row(x, y, w, h, icon, t, sub, l, cls)


exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'unit1.py')).read())   # Unit 01 helpers


# ================================================================== title
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 01 &middot; Lesson 1.1</p>
    <h1 style="font-size:56px;line-height:1.05">Inside the Swift<br>Programming Language</h1>
    <p class="lead" style="max-width:720px">How does the Swift code we write become <b>instructions an Apple processor can execute?</b></p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'We have completed our iOS architecture foundation. Now we explore the language used to build iOS applications. Rather than starting with let, var and print, we begin with a more interesting question: how does the Swift code we write become instructions an Apple processor can execute? Today: Swift&rsquo;s design philosophy, its compiler and LLVM, the type system, the memory model, and how Swift differs from Java, Python and JavaScript.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")

outs = [("book", "Why Apple created Swift, and its four <b>design goals</b>"),
        ("layers", "How source becomes <b>machine code</b>: SIL and LLVM"),
        ("check", "<b>Static typing</b> and <b>type inference</b>"),
        ("decision", "<b>Optionals</b>: absence made explicit in the type"),
        ("diff", "<b>Value</b> versus <b>reference</b> semantics, and ARC"),
        ("link", "<b>Protocol-oriented</b> design, and where Swift fits in iOS")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 1.1 &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six things you should be able to explain by the end of this lesson.'), ('CONNECT', 'First, where the language sits.'))))

S.append(slide("Lesson 1.1 &middot; Where we are", "Today: the language itself", f"""  <div class="body">
    {stack(('lang', 'rt'), tid='where', style='max-height:330px')}
    <div class="bridge"><span><b>Last time</b>Lesson 0.10: one NPay journey across the whole iOS architecture map. Unit 00 is complete.</span><span><b>Today</b>The Swift language, and the compiler that turns it into native code.</span></div>
  </div>""", notes(('SAY', 'Unit 00 gave us the platform: the process, the main thread, memory, security, networking and storage. This picture is the same system seen from the language side. Today lives in the two teal layers: the Swift language we write, and the compiler and runtime that turn it into native code and manage memory with ARC.'),
                  ('CONNECT', 'Why did Apple need a new language at all?'))))

# ================================================================== 1
divider(1, "Why did Apple create Swift?", "Four design goals", 'Imagine you are building NPay, a financial application. What would you want from its language?', 'Here is what you would ask for.')
goals = [("play", "Performance", "native compiled code and optimization"),
         ("shield", "Safety", "optionals, type checking, memory safety mechanisms"),
         ("code", "Expressiveness", "concise syntax and powerful abstractions"),
         ("link", "Interoperability", "Apple frameworks and supported language interfaces")]
gcells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p><b>{t}</b><br><span class="muted" style="font-size:17px">{d}</span></p></div>' for i, t, d in goals)
S.append(slide("Part 1 &middot; Design goals", "A language for an app like NPay", f"""  <div class="body">
    <p class="lead" style="margin-top:0">Introduced by Apple in <b>2014</b>: a modern alternative to Objective-C that still works with existing Apple technologies.</p>
    <div class="cols c4 stagger step" style="align-items:stretch">
{gcells}
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Not Apple's Java">Swift has its own design: <b>value semantics</b>, <b>protocol-oriented</b> programming, <b>optionals</b>, <b>ARC</b> and <b>structured concurrency</b>.</div>
  </div>""", notes(('SAY', 'For NPay you want a language that is fast enough for demanding native apps, safe enough to prevent many common programming errors, expressive enough to write understandable code, able to work with existing Apple frameworks, and suited to modern concurrency. Apple introduced Swift in 2014 as a modern alternative to Objective-C that interoperates with existing Apple technologies.'),
                  ('SAY', 'Click: the four design goals. Performance from native compilation and optimization. Safety from optionals, type checking and memory-safety mechanisms. Expressiveness from concise syntax and powerful abstractions. Interoperability with Apple frameworks and supported language interfaces.'),
                  ('SAY', 'Click: do not file Swift away as Apple&rsquo;s version of Java. It has its own design: value semantics, protocol-oriented programming, optionals, ARC and structured concurrency. Each of those gets its own lesson in this unit.'),
                  ('CONNECT', 'Start with performance: is Swift compiled or interpreted?'))))

# ================================================================== 2
divider(2, "Is Swift compiled or interpreted?", "From source to machine code", 'Swift is primarily a compiled language. Follow six lines of Swift all the way to the processor.', 'Here are the six lines.')
MAIN = """let amount = 500
let quantity = 3

let total = amount * quantity

print(total)"""
W, G = 172, 20.8
stages = [("code", "Swift source", "main.swift"), ("decision", "Parse &amp; check", "syntax, types, diagnostics"),
          ("layers", "SIL", "Swift-specific IR"), ("frameworks", "LLVM IR", "lower-level IR"),
          ("chip", "Machine code", "target instructions"), ("app", "Executable", "linked binary")]
P = []
for i, (ic, t, sub) in enumerate(stages):
    x = i * (W + G)
    P.append(tall(x, 40, W, 150, ic, t, sub, str(i + 1) if i < 5 else '6+'))
    if i < 5:
        P.append(wire(f'M{x + W + 3:g} 115H{x + W + G - 3:g}' + head(x + W + G - 3, 115, 'r')))
for x0, x1, lab in ((0, 2 * (W + G) + W, 'SWIFT FRONTEND (swiftc)'), (3 * (W + G), 4 * (W + G) + W, 'LLVM'), (5 * (W + G), 5 * (W + G) + W, 'LINKER')):
    P.append(wire(f'M{x0:g} 22V14H{x1:g}V22', None, 'faint'))
    P.append(f'<text class="mono" x="{(x0 + x1) / 2:g}" y="8" text-anchor="middle">{lab}</text>')
S.append(slide("Part 2 &middot; Compilation pipeline &middot; conceptual", "Six lines, six stages", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:420px 1fr;gap:32px;align-items:center">
      {code("main.swift", MAIN, "font-size:16px")}
      <p class="lead" style="margin:0">Building NPay sends every <code>.swift</code> file through the same stages before anything runs on the iPhone.</p>
    </div>
    <div class="gap"></div>
    {svg('0 0 1136 190', 'Swift source, parse and check, SIL, LLVM IR, machine code, executable', 'pipe', P)}
    {cues(6)}
    <div class="gap"></div>
    <div class="takeaway step">Swift source &rarr; <b>Swift-specific compilation</b> &rarr; <b>LLVM-based</b> code generation &rarr; native executable.</div>
  </div>""", notes(('SAY', 'Six lines: amount times quantity, printed. Building a native Swift app sends this source through a compilation pipeline. Click through it.'),
                  ('SAY', 'One, the Swift source files. Two, parsing and semantic analysis: syntax, types, declarations, and the diagnostics you see as errors. Three, SIL, the Swift Intermediate Language. Four, LLVM IR, a lower-level intermediate representation. Five, machine code for the target architecture, arm64 on an iPhone. Six, the linker produces the executable with its dependencies.'),
                  ('SAY', 'The brackets show who does what: the Swift frontend, swiftc, handles stages one to three and produces the LLVM IR; LLVM optimizes it and generates machine code; the linker builds the binary. This is conceptual: real builds have more passes, modules and optimization stages.'),
                  ('SAY', 'Is Swift ever interpreted? Running swift main.swift in a terminal feels like a script, but it still compiles the code first and runs it straight away. There is no bytecode virtual machine.'),
                  ('CONNECT', 'What are SIL and LLVM, and can we see them?'))))

SIL_TBL = [("SIL", "<code>smul_with_overflow_Int64</code>", "Swift semantics kept: the multiply is <b>overflow-checked</b>"),
           ("LLVM IR", "<code>store i64 1500</code>", "LLVM worked out <b>500 &times; 3</b> at compile time"),
           ("Assembly", "<code>mov w20, #1500</code>", "one processor instruction loads the answer")]
trs = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in SIL_TBL)
S.append(slide("Part 2 &middot; SIL and LLVM", "What SIL and LLVM do", f"""  <div class="body">
    <div class="cols" style="gap:24px">
      <div class="card accent"><span class="label">SIL &middot; Swift Intermediate Language</span><p>A representation designed <b>for Swift</b>. It keeps Swift&rsquo;s semantics so the compiler can check and optimize them before lowering the code further.</p></div>
      <div class="card accent"><span class="label">LLVM</span><p>A <b>compiler infrastructure</b> project. Swift uses it to optimize and generate native machine code for each supported target.</p></div>
    </div>
    <div class="gap"></div>
    <div class="step">
      <p class="small muted" style="margin:0 0 6px">Our six lines, compiled with <code>swiftc -O</code> (Swift 6.3, arm64):</p>
      <table class="tbl"><thead><tr><th style="width:150px">Stage</th><th style="width:360px">What we see</th><th>Meaning</th></tr></thead><tbody>{trs}</tbody></table>
    </div>
  </div>""", notes(('SAY', 'SIL stands for Swift Intermediate Language: an intermediate representation designed specifically for Swift. It lets the compiler represent Swift semantics and optimize them before lowering the code further. LLVM is a compiler infrastructure project; Swift uses it to optimize and generate native machine code for each supported target.'),
                  ('SAY', 'Click: real output from our six lines. In SIL the multiply is still there, as an overflow-checked multiply: Swift traps on integer overflow instead of silently wrapping, and SIL carries that rule. In LLVM IR the optimizer has already computed 500 times 3, so it just stores 1500. The arm64 assembly loads 1500 with a single instruction. You will reproduce this in the lab.'),
                  ('LIVE DEMO', 'In a terminal: xcrun swiftc -emit-sil -O main.swift | grep smul; xcrun swiftc -emit-ir -O main.swift | grep 1500; xcrun swiftc -S -O main.swift | grep 1500. Exact text varies with compiler version.'),
                  ('CONNECT', 'Native compilation is one difference from other languages. Here are the rest.'))))

# ================================================================== 3
divider(3, "Swift, Java, Python, JavaScript", "One table, five differences", 'You already program in other languages. Comparison is one of the fastest ways to understand Swift.', 'Here is the table.')
CMP = [("Typical execution", "Native compilation", "JVM bytecode / JIT", "Interpreter / VM", "Engine / JIT"),
       ("Type system", "Static", "Static", "Dynamic", "Dynamic"),
       ("Null handling", "Explicit optionals", "Nullable references", "<code>None</code>", "<code>null</code>, <code>undefined</code>"),
       ("Memory management", "ARC + value semantics", "Garbage collection", "Reference counting + GC (CPython)", "Garbage collection"),
       ("Common app UI", "SwiftUI, UIKit", "Java UI ecosystems", "Various frameworks", "Web and other frameworks")]
trs = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>' for a, b, c, d, e in CMP)
S.append(slide("Part 3 &middot; Comparison", "Swift among familiar languages", f"""  <div class="body">
    <table class="tbl"><thead><tr><th>Feature</th><th>Swift</th><th>Java</th><th>Python</th><th>JavaScript</th></tr></thead><tbody>{trs}</tbody></table>
    <p class="small muted" style="margin:10px 0 0">Broad comparisons: language implementations and execution modes vary.</p>
  </div>""", notes(('SAY', 'Read across each row. Swift compiles to native code; Java runs JVM bytecode with a JIT; Python runs on an interpreter or VM; JavaScript runs in an engine with a JIT. Swift and Java are statically typed; Python and JavaScript are dynamic. Swift makes absence explicit with optionals, where Java has nullable references, Python None, and JavaScript null and undefined. Swift manages memory with ARC plus value semantics; Java and JavaScript use garbage collection; CPython uses reference counting plus a cycle-detecting GC. And Swift apps use SwiftUI or UIKit.'),
                  ('SAY', 'These are broad comparisons; implementations and execution modes vary.'),
                  ('CONNECT', 'Now the same idea written in three languages.'))))

SW = 'let balance = 25000\nvar customerName = "Ravi"'
JV = 'final int balance = 25000;\nString customerName = "Ravi";'
PYT = 'balance = 25000\ncustomer_name = "Ravi"'
S.append(slide("Part 3 &middot; Declaring a variable", "Same idea, three languages", f"""  <div class="body">
    <div class="cols c3" style="gap:20px">
      {code("Swift", SW, "font-size:17px")}
      {code("Java", JV, "font-size:17px")}
      {code("Python", PYT, "font-size:17px")}
    </div>
    <div class="gap"></div>
    <div class="cols step" style="gap:24px">
      <div class="card accent"><span class="label">let and var</span><p><code>let</code> is an immutable binding; <code>var</code> is a mutable variable.</p></div>
      <div class="card accent"><span class="label">Type inference</span><p>No type written, yet the compiler knows: <code>balance</code> is an <code>Int</code>, <code>customerName</code> is a <code>String</code>.</p></div>
    </div>
  </div>""", notes(('SAY', 'The same two declarations in Swift, Java and Python. Java writes the types and uses final for the constant. Python has no declarations or types at all.'),
                  ('SAY', 'Click: Swift uses let for an immutable binding and var for a mutable variable. And it infers the types: balance is an Int and customerName is a String, checked at compile time, even though we never wrote them. Static typing does not mean writing types everywhere.'),
                  ('CONNECT', 'So what happens when we break the type?'))))

# ================================================================== 4
divider(4, "Strongly and statically typed", "The compiler checks every assignment", 'Swift infers a type once and then holds you to it.', 'Try three assignments.')
TRY = [("<code>balance = 30000</code>", "Compiles", "an <code>Int</code> into an <code>Int</code>"),
       ("<code>balance = \"30000\"</code>", "error", "cannot assign value of type &lsquo;String&rsquo; to type &lsquo;Int&rsquo;"),
       ("<code>balance = 30000.5</code>", "error", "cannot assign value of type &lsquo;Double&rsquo; to type &lsquo;Int&rsquo;")]
rows_ = ''.join(f"""      <div class="card accent" style="display:grid;grid-template-columns:300px 1fr;gap:18px;align-items:center;padding:16px 22px">
        <code style="font-size:20px">{a.replace('<code>', '').replace('</code>', '')}</code>
        <p class="step" style="margin:0;font-size:19px"><b>{v}</b>{'' if v == 'Compiles' else ':'} <span class="{'muted' if v == 'Compiles' else ''}">{d}</span></p>
      </div>\n""" for a, v, d in TRY)
S.append(slide("Part 4 &middot; Type checking", "Three assignments to an Int", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:.8fr 1.2fr;gap:28px;align-items:start">
      <div>{code("Types.swift", 'var balance = 25000   // inferred: Int', "font-size:17px")}
        <p class="small muted" style="margin:12px 0 0">Real <code>swiftc</code> messages (Swift 6.3).</p></div>
      <div style="display:flex;flex-direction:column;gap:12px">
{rows_}      </div>
    </div>
    <div class="gap"></div>
    <div class="rule step">Swift does <b>not</b> silently convert between unrelated types. A type mismatch is a <b>compile-time</b> error, not a surprise at run time.</div>
  </div>""", notes(('SAY', '<code>var balance = 25000</code>: Swift infers Int. Now three assignments; reveal each result.'),
                  ('SAY', 'Click: 30000 is an Int, so it compiles. Click: the string "30000" does not: cannot assign value of type String to type Int. Click: 30000.5 is a Double, and Swift will not silently drop the .5, so that is an error too. These are the compiler&rsquo;s real messages.'),
                  ('SAY', 'Click: the rule. Swift does not silently convert between unrelated types, and the mistake is caught when you build, not when a customer runs the app.'),
                  ('CONNECT', 'So how do you convert when you mean to?'))))

CONV = """let count: Int = 10
let price: Double = 99.5

let total = Double(count) * price   // 995.0"""
S.append(slide("Part 4 &middot; Explicit conversion", "Convert on purpose", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1fr 1fr;gap:32px;align-items:center">
      {code("Conversion.swift", CONV, "font-size:18px")}
      <div>
        <div class="tip" data-label="Visible">We wrote <code>Double(count)</code>. The change of representation is <b>in the code</b>, where a reviewer can see it.</div>
        <div class="gap"></div>
        <div class="rule step" data-label="Money in NPay"><code>Double</code> is not ideal for exact money arithmetic. NPay keeps amounts as whole <b>paise</b> in an <code>Int64</code> (<code>balanceMinor</code>), and formats rupees only for display.</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'count is an Int and price is a Double. To multiply them we convert count explicitly with Double(count). The result is 995.0.'),
                  ('SAY', 'Why is that useful in financial software? The representation change is visible in the code and easy to review.'),
                  ('SAY', 'Click: but explicit conversion is not enough on its own. Double is binary floating point, so it cannot represent most decimal fractions exactly, and that matters for money. NPay stores amounts as whole paise in an Int64, balanceMinor, and turns them into rupees only for display. Lesson 1.2 goes into numeric types, and 1.10 builds a real Money type.'),
                  ('CONNECT', 'Swift&rsquo;s type system also answers one of the oldest bugs in programming: missing values.'))))

# ================================================================== 5
divider(5, "Optionals", "Absence, made explicit", 'One of Swift&rsquo;s most important features. NPay asks the server for a customer&rsquo;s nickname. Some customers have one; others do not. How should Swift represent that?', 'With a question mark.')
OPT = 'var nickname: String? = "Ravi"\n\nnickname = nil'
P = [f'<text class="mono" x="270" y="16" text-anchor="middle">String?</text>',
     wire('M0 28V22H540V28', None, 'faint'),
     tall(0, 40, 260, 130, 'check', 'Has a value', 'Some("Ravi")', '0'),
     tall(280, 40, 260, 130, 'cross', 'No value', 'nil', '1+')]
UNWRAP = """let nickname: String? = "Ravi"

if let name = nickname {
    print("Hello, \\(name)")
} else {
    print("No nickname available")
}"""
S.append(slide("Part 5 &middot; Optionals", "One type, two possible states", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1fr 1fr;gap:32px;align-items:center">
      <div>{code("Nickname.swift", OPT, "font-size:18px")}
        <div class="gap"></div>
        {svg('0 0 540 170', 'A String optional holds either Some Ravi or nil', 'opt', P, 'max-height:200px')}</div>
      <div>{code("Unwrap.swift", UNWRAP, "font-size:17px")}</div>
    </div>
    {cues(1)}
    <div class="gap"></div>
    <div class="takeaway step">The possibility of absence is part of the <b>type</b>. You unwrap before you use the value.</div>
  </div>""", notes(('SAY', 'var nickname: String? = "Ravi". The question mark means: either a String, or no value. It starts with a value.'),
                  ('SAY', 'Right now the optional holds Some("Ravi"). Click: nickname = nil, and now it holds no value.'),
                  ('SAY', 'In many languages, null-related errors happen because code assumes a value exists. Swift puts the possibility of absence into the type system, so the compiler knows. You generally must unwrap an optional before using the value as a non-optional one. if let does that: it binds name only when there is a value, and the else branch handles absence.'),
                  ('SAY', 'Click: the takeaway. Lesson 1.3 covers optionals in much greater depth.'),
                  ('CONNECT', 'Next, another major design choice: values and references.'))))

# ================================================================== 6
divider(6, "Values versus references", "Two kinds of data", 'Think of two kinds of NPay data: a transaction amount, and a shared account session manager. Are they the same kind of thing?', 'They are not.')
S.append(slide("Part 6 &middot; Semantics", "Value types and reference types", f"""  <div class="body">
    <div class="cols" style="gap:24px">
      <div class="card accent"><span class="label">Value types</span><ul style="margin:6px 0 0"><li><b>Structs, enums, tuples</b></li><li>Assignment makes an <b>independent</b> value</li><li>Example: a transaction amount</li></ul></div>
      <div class="card accent"><span class="label">Reference types</span><ul style="margin:6px 0 0"><li><b>Classes, actors</b></li><li>Many references, <b>one shared</b> instance</li><li>Example: a session manager</li></ul></div>
    </div>
    <div class="gap-lg"></div>
    <div class="misconception step">&ldquo;Structs live on the stack, classes on the heap.&rdquo; Not a guaranteed rule in Swift. The real distinction is <b>value semantics</b> versus <b>reference semantics</b>.</div>
  </div>""", notes(('SAY', 'A transaction amount is naturally a value. A session manager may need shared identity and controlled mutable state. Swift supports both. Value types are structs, enums and tuples: assignment produces an independent logical value. Reference types are classes and actors, and closures behave the same way: several references can point to the same instance.'),
                  ('SAY', 'Click: the misconception. Struct-on-stack, class-on-heap is not a guaranteed rule; a struct inside a class or an array lives on the heap, and the optimizer may place a class instance on the stack. Lesson 0.6 showed this. Think in semantics, not storage.'),
                  ('CONNECT', 'Now see the difference in code, and what each version leaves in memory.'))))

STRUCT = """struct Account {
    var balanceMinor: Int64      // paise
}

var accountA = Account(balanceMinor: 500_000)
var accountB = accountA
accountB.balanceMinor = 900_000
print(accountA.balanceMinor)
print(accountB.balanceMinor)"""
CLASS = """class Account {
    var balanceMinor: Int64
    init(balanceMinor: Int64) {
        self.balanceMinor = balanceMinor
    }
}
let accountA = Account(balanceMinor: 500_000)
let accountB = accountA
accountB.balanceMinor = 900_000
print(accountA.balanceMinor)"""
VAL = [box(0, 32, 236, 62, 'accountA', '500_000 &middot; &#8377;5,000', None, '', 'file'),
       wire('M244 63H308' + head(308, 63, 'r'), None, 'dash'),
       f'<text class="sm" x="276" y="52" text-anchor="middle">copy</text>',
       box(316, 32, 236, 62, 'accountB', '900_000 &middot; &#8377;9,000', None, 'lit', 'file')]
REF = [box(0, 0, 190, 54, 'accountA', 'reference', None, '', 'link'),
       box(0, 72, 190, 54, 'accountB', 'reference', None, '', 'link'),
       wire('M194 27L258 55' + head(258, 55, 'r')), wire('M194 99L258 71' + head(258, 71, 'r')),
       box(266, 28, 286, 70, 'One Account instance', '900_000 &middot; &#8377;9,000', None, 'lit', 'memory')]
S.append(slide("Part 6 &middot; In code", "Change the copy, check the original", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      <div>{code("StructAccount.swift", STRUCT, "font-size:15px;min-height:272px")}
        <div class="step" style="margin-top:12px">{svg('0 0 552 126', 'After the struct code: accountA holds 500,000 and accountB, an independent copy, holds 900,000', 'vv', VAL)}
          <p style="margin:8px 0 0;font-size:19px">Prints <code>500000</code>, <code>900000</code>: <b>two values</b>.</p></div></div>
      <div>{code("ClassAccount.swift", CLASS, "font-size:15px;min-height:272px")}
        <div class="step" style="margin-top:12px">{svg('0 0 552 126', 'After the class code: accountA and accountB both refer to one Account instance holding 900,000', 'rr', REF)}
          <p style="margin:8px 0 0;font-size:19px">Prints <code>900000</code>: <b>one shared instance</b>.</p></div></div>
    </div>
  </div>""", notes(('SAY', 'Two files, each with its own Account type. Amounts are whole paise in an Int64, as NPay stores money: 500,000 paise is ₹5,000. In both, accountB starts from accountA, and we change accountB to 900,000.'),
                  ('ASK', 'Before the click: what does each print?'),
                  ('SAY', 'Click: the struct. var accountB = accountA made a copy, so memory holds two Account values: changing accountB left accountA at ₹5,000. It prints 500000 then 900000. Click: the class. let accountB = accountA copied only the reference, so both names point to one instance, and the change through accountB is seen through accountA. It prints 900000.'),
                  ('CONNECT', 'Class instances are shared, so who decides when one goes away?'))))

# ================================================================== 7
divider(7, "How does Swift manage memory?", "ARC, revisited", 'We studied this in Lesson 0.6. Here is the one idea to carry into the rest of the unit.', 'Three stages.')
P = [box(0, 0, 640, 60, 'Class instance created', '', '1+', '', 'memory'),
     wire('M320 64V86' + head(320, 86, 'd')),
     box(0, 92, 640, 60, 'Strong references keep it alive', '', '2+', '', 'link'),
     wire('M320 156V178' + head(320, 178, 'd')),
     box(0, 184, 640, 60, 'No strong references left', 'ARC deinitializes it', '3+', '', 'cross')]
S.append(slide("Part 7 &middot; ARC", "Automatic Reference Counting", f"""  <div class="body">
    {cues(3)}
    <div class="cols" style="grid-template-columns:1.1fr 1fr;gap:32px;align-items:center">
      {svg('0 0 640 244', 'Instance created, strong references keep it alive, no strong references left so ARC deinitializes it', 'arc', P, 'max-height:300px')}
      <div>
        <div class="tip" data-label="Not a tracing GC">ARC counts strong references and frees an instance when the count reaches zero. Nothing pauses to scan memory.</div>
        <div class="gap"></div>
        <div class="rule step" data-label="The cost">Ownership becomes your design job: <b>retain cycles</b> keep instances alive forever.</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Swift uses Automatic Reference Counting to manage the lifetime of class instances. Click through it: an instance is created; strong references keep it alive; when no strong ownership remains, ARC deinitializes it.'),
                  ('SAY', 'ARC is different from tracing garbage collection: it does not periodically scan memory to find unreachable objects. Click: the cost is that ownership becomes part of your design. Two objects that strongly own each other, a retain cycle, are never freed.'),
                  ('SAY', 'We return to ARC with classes and closures in Lessons 1.4, 1.5 and 1.8, and with concurrency in 1.9.'),
                  ('CONNECT', 'The last design idea: building abstractions with protocols.'))))

# ================================================================== 8
divider(8, "Protocol-oriented design", "Abstractions without a class hierarchy", 'NPay could get balances from several providers: the live bank API, a test double, a demo mode. Do they all need one base class?', 'No. They need a protocol.')
PROTO = """struct Balance { let balanceMinor: Int64 }   // paise

protocol BalanceProviding {
    func fetchBalance() async throws -> Balance
}

struct MockBalanceService: BalanceProviding {
    func fetchBalance() async throws -> Balance {
        Balance(balanceMinor: 2_500_000)        // ₹25,000
    }
}"""
P = [box(0, 0, 470, 62, 'DashboardViewModel', 'depends on the protocol only', None, '', 'layout'),
     wire('M235 66V96' + head(235, 96, 'd')),
     box(0, 102, 470, 62, 'BalanceProviding', 'protocol', None, 'lit', 'link'),
     wire('M112 230V170' + head(112, 170, 'u'), None, 'dash'), wire('M357 230V170' + head(357, 170, 'u'), None, 'dash'),
     box(0, 236, 225, 62, 'BalanceService', 'live bank API', None, '', 'bank'),
     box(245, 236, 225, 62, 'MockBalanceService', 'tests, previews', None, '', 'check')]
S.append(slide("Part 8 &middot; Protocols", "Depend on what, not on who", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.25fr .75fr;gap:32px;align-items:center">
      {code("BalanceProviding.swift", PROTO, "font-size:16px")}
      {svg('0 0 470 298', 'DashboardViewModel depends on BalanceProviding; BalanceService and MockBalanceService conform', 'proto', P, 'max-height:380px')}
    </div>
    <div class="gap"></div>
    <div class="points step"><div><svg viewBox="0 0 24 24"><use href="#i-link"/></svg><span><b>Dependency injection</b><small>pass in any provider</small></span></div><div><svg viewBox="0 0 24 24"><use href="#i-check"/></svg><span><b>Testing</b><small>a mock, no network</small></span></div><div><svg viewBox="0 0 24 24"><use href="#i-layers"/></svg><span><b>Modular architecture</b><small>swap implementations</small></span></div></div>
  </div>""", notes(('SAY', 'Instead of forcing every provider into one class inheritance hierarchy, we define a protocol: BalanceProviding promises a fetchBalance function that returns a Balance. Any suitable type can conform, including a struct. MockBalanceService always returns ₹25,000, held as 2,500,000 paise.'),
                  ('SAY', 'The diagram: DashboardViewModel depends only on the protocol. The live BalanceService and the mock both conform, so either can be passed in.'),
                  ('SAY', 'Click: that is what makes dependency injection, testing without a network, modular architecture and interchangeable implementations possible. Lesson 1.6 covers protocols in depth; Unit 04, Lesson 4.5, builds the injection.'),
                  ('CONNECT', 'Finally, put the language back into the platform.'))))

# ================================================================== 9
divider(9, "How Swift connects to iOS", "From language to hardware", 'Now connect the language to the platform we spent Unit 00 on.', 'Six layers.')
S.append(slide("Part 9 &middot; The full stack", "Where Swift fits", f"""  <div class="body">
    {stack(lits={k: str(i + 1) if i < 5 else '6+' for i, (k, *_r) in enumerate(STACK)}, tid='stack9', style='max-height:410px')}
    {cues(6)}
  </div>""", notes(('SAY', 'Click down the stack. The Swift language: types, functions, structs, classes, protocols. SwiftUI and UIKit: interfaces and interaction. Foundation and system APIs: networking, data, files and more. The Swift compiler and runtime: native code, runtime support and ARC. The iOS operating system: process execution, scheduling, memory and security. And Apple hardware: processor, memory, GPU and device capabilities.'),
                  ('SAY', 'This is why we studied iOS architecture before Swift syntax. You already know the bottom of this stack; now you know where Swift fits within the whole system.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
S.append(slide("Lesson 1.1 &middot; Recap", "What to remember", f"""  <div class="body">
    {stack(('lang', 'rt'), tid='recap', style='max-height:290px')}
    <div class="gap"></div>
    {points([("layers", "Compiled to native code", "source &rarr; SIL &rarr; LLVM IR &rarr; machine code"),
             ("check", "Types are checked at build time", "inferred, never silently converted"),
             ("diff", "Semantics, not storage", "values copy, references share, ARC frees")], label='Recap', box='tip', step=False)}
  </div>""", notes(('SAY', 'Three things to remember. Swift compiles to native code: source, SIL, LLVM IR, machine code. Types are checked when you build: inferred where you leave them out, never silently converted, and absence is explicit with optionals. And think in semantics, not storage: values copy, references share, and ARC frees class instances when the last strong reference goes. Protocols let NPay depend on what a service does, not which type provides it.'),
                  ('CONNECT', 'Now check your understanding.'))))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Eight questions, in different formats. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
# (icon, label, data-title, question html, verdict, why, trap, expect, extra notes)
QA = [("chip", "Question", "Does Swift always execute through a JVM-like virtual machine?",
       "Does Swift always execute through a JVM-like virtual machine?", "No",
       "Swift is commonly compiled ahead of time to native machine code for Apple platforms. There is no bytecode VM.",
       "Assuming every modern language runs on a VM.", "Java developers often say yes.", None),
      ("layers", "Choose one", "Which order is the Swift compilation pipeline?",
       "Which is the Swift compilation pipeline?<br>A. Source &rarr; LLVM IR &rarr; SIL &rarr; machine code<br>B. Source &rarr; SIL &rarr; LLVM IR &rarr; machine code<br>C. Source &rarr; bytecode &rarr; JIT<br>D. Source &rarr; machine code, in one step", "B",
       "The Swift frontend lowers source to SIL, a Swift-specific representation, then to LLVM IR; LLVM generates the machine code.",
       "Putting LLVM before SIL.", "A is the common slip.", None),
      ("diff", "Question", "Does assigning a struct always create a separate logical value?",
       "Does assigning a struct always create a separate logical value?", "Yes",
       "Structs have value semantics, even though the actual copying may be optimized. If the struct holds a class reference, the copy holds the same reference.",
       "Thinking an optimized copy means shared state.", "Some say no because copies are optimized away.", None),
      ("check", "Question", "Can Swift infer variable types?",
       "Can Swift infer variable types?", "Yes",
       "<code>let balance = 25000</code> is an <code>Int</code>, checked at compile time. Inference is static, not dynamic typing.",
       "Thinking inferred means dynamically typed.", "Python developers may hesitate.", None),
      ("bank", "Question", "Why is explicit numeric conversion useful in financial software?",
       "Why is an explicit conversion like <code>Double(count)</code> useful in financial software?", "It&rsquo;s visible",
       "Representation changes show up in the code, where they can be reviewed. The representation still matters: NPay keeps money in whole paise, not <code>Double</code>.",
       "Thinking conversion alone makes Double safe for money.", "Most say safety; push for the reason.", None),
      ("code", "Choose one", "Which best describes Swift's programming paradigm?",
       "Which best describes Swift?<br>A. Purely object-oriented<br>B. Purely functional<br>C. Multi-paradigm: object-oriented, functional, generic, protocol-oriented<br>D. Protocol-oriented only", "C",
       "Swift supports several paradigms. Protocols are central, but classes, closures and generics are first-class too.",
       "Picking one label for the whole language.", "Some pick D after Part 8.", None),
      ("link", "Question", "Are protocols useful for dependency injection?",
       "Are protocols useful for dependency injection?", "Yes",
       "A protocol defines what a dependency does, so NPay can pass in the live service or a mock.",
       "Thinking injection needs a class hierarchy.", "Most say yes.", None),
      ("thread", "Question", "Does async automatically create a background thread?",
       "Does <code>async</code> automatically create a background thread?", "No",
       "<code>async</code> means the function can suspend. Where it runs is decided by isolation, not by the keyword.",
       "Reading async as &ldquo;on another thread&rdquo;.", "Many say yes.", "Spaced review from Lesson 0.5.")]
review(QA)

S.append(next_slide('1.1', [("1.2", "Variables, constants &amp; type system", "<code>let</code>, <code>var</code>, numeric types, conversion"),
                            ("1.3", "Optionals &amp; safe unwrapping", "every way to unwrap, and when"),
                            ("1.5", "Structs, classes &amp; value semantics", "choosing value or reference"),
                            ("1.6", "Protocols, extensions &amp; protocol-oriented design", "<code>BalanceProviding</code> in depth"),
                            ("1.8", "ARC, ownership &amp; memory management", "ownership and retain cycles"),
                            ("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "what <code>async</code> really does")],
                    'Each part of today has its own lesson in this unit: types in 1.2, optionals in 1.3, value and reference semantics in 1.5, protocols in 1.6, ARC and ownership in 1.8, and concurrency in 1.9. Lesson 1.10 brings them together in an NPay Swift package with tests.'))

LAB = """let amount = 500
let quantity = 3
let total = amount * quantity
print(total)"""
TERM = """swiftc main.swift -o total && ./total
swiftc -emit-sil -O main.swift | grep smul
swiftc -emit-ir  -O main.swift | grep 1500
swiftc -S        -O main.swift | grep 1500"""
S.append(lab_slide('1.1', "See the pipeline yourself", "Compile the example and find each stage in the compiler&rsquo;s output. Swift only, no Xcode project.",
                   ["Save the code as <code>main.swift</code>; build and run it.",
                    "<b>SIL:</b> find the overflow-checked multiply.",
                    "<b>LLVM IR</b> and <b>assembly:</b> find where 1500 appears.",
                    "Change <code>quantity</code> to <code>\"3\"</code>, build again, and read the error.",
                    "Hand in the line you found at each stage, and one sentence on what that stage did."],
                   "", 'Students need a Swift toolchain only. On a Mac, prefix commands with xcrun if swiftc is not on the path. Expected: ./total prints 1500. SIL shows builtin "smul_with_overflow_Int64", the overflow-checked multiply. LLVM IR shows store i64 1500: the optimizer computed the product. arm64 assembly shows mov w20, #1500 (the register can differ; on Linux x86-64 it is a different instruction, but 1500 still appears). With quantity = "3", the build fails: cannot convert value of type String to expected argument type Int. Ask each student to write one sentence per stage: what did it do to the code?',
                   side=f'<div>{code("main.swift", LAB, "font-size:16px")}<div class="gap"></div>{code("Terminal", TERM, "font-size:14px")}<p class="small muted" style="margin:8px 0 0">On a Mac, prefix with <code>xcrun</code> if <code>swiftc</code> is not found.</p></div>'))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 1.1 complete</p>
    <h2>Inside the Swift<br>Programming Language</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 1.2 &mdash; Variables, Constants &amp; Swift&rsquo;s Type System</p>
  </div>
""" + notes(('SAY', 'You can now explain why Swift was created, how Swift source becomes native machine code, the role of SIL and LLVM, static typing and inference, optionals, value versus reference semantics, ARC, protocol-oriented design, and how Swift fits into iOS.'),
            ('SAY', 'Next, Lesson 1.2: let versus var, type inference, numeric types, strings, tuples, collections, type conversion, and the difference between mutability and value semantics, with NPay examples.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 1.1 — Inside the Swift Programming Language</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit 01 · Lesson 1.1 — Inside the Swift Programming Language">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT11, 'w').write(doc)
print(len(S), 'slides')
