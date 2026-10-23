"""Generates decks/unit-1/lesson-1.2/index.html from the Lesson 1.2 text (PocketBank -> NPay)."""
import html, os, re, sys
OUT12 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers

# ================================================================== title
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 01 &middot; Lesson 1.2</p>
    <h1 style="font-size:54px;line-height:1.05">Variables, Constants<br>&amp; Swift&rsquo;s Type System</h1>
    <p class="lead" style="max-width:760px">How does Swift know <b>what kind of data</b> we store, <b>whether it can change</b>, and <b>which operations are safe?</b></p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'In Lesson 1.1 we saw how Swift code is compiled into native machine instructions. Now we start writing Swift. Rather than memorizing syntax, we answer a deeper question: how does Swift know what kind of data we are storing, whether that data can change, and which operations are safe? We keep building NPay as we go.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")

outs = [("lock", "<b>let</b> versus <b>var</b>, and why to prefer <code>let</code>"),
        ("check", "<b>Static typing</b> with type <b>inference</b>"),
        ("bank", "The core types, and why money is <b>not a Double</b>"),
        ("diff", "<b>Explicit conversion</b>, and what <code>Int(3.9)</code> gives"),
        ("layers", "<b>Strings</b>, <b>tuples</b> and the three <b>collections</b>"),
        ("memory", "What <code>let</code> means for <b>structs</b> versus <b>classes</b>")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 1.2 &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six things you should be able to explain by the end of this lesson.'), ('CONNECT', 'First, where we are.'))))

where_slide('1.2', 'Today: writing Swift', ('lang',),
            'Lesson 1.1: Swift compiles to native code, and the compiler checks every type at build time.',
            'Declarations, types, conversions, strings and collections, written in Swift.',
            'Last time we followed Swift source through SIL and LLVM to machine code, and saw the compiler reject a String assigned to an Int. Today we stay in the language and write real declarations: what each one stores, whether it can change, and what the type checker allows.',
            'Start with a real NPay problem.')

# ================================================================== 1
divider(1, "Storing a bank account", "Our first NPay problem", 'NPay needs to represent one customer&rsquo;s account. How do we write that down in Swift?', 'Four facts, four lines.')
ACC = """let customerName = "Ravi"
let accountNumber = "NP1001"
var balance = 25000
var isActive = true

print(customerName)
print(balance)"""
P = ['<rect class="wire faint" x="0" y="0" width="420" height="300" rx="20"/>',
     '<text class="mono" x="24" y="34">NPAY ACCOUNT</text>',
     box(24, 52, 372, 50, 'Ravi', 'customer name', '1+', '', 'user'),
     box(24, 112, 372, 50, 'NP1001', 'account number', '1+', '', 'key'),
     box(24, 172, 372, 50, '&#8377;25,000', 'balance', '2+', '', 'bank'),
     box(24, 232, 372, 50, 'Active', 'account status', '2+', '', 'check')]
S.append(slide("Part 1 &middot; The problem", "Four facts about one account", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:420px 1fr;gap:40px;align-items:center">
      {svg('0 0 420 300', 'An NPay account: customer Ravi, account NP1001, balance 25,000 rupees, active', 'acct', P, 'max-height:330px')}
      <div>{code("Account.swift", ACC, "font-size:18px")}
        {cues(2)}
        <div class="gap"></div>
        <div class="cols step" style="gap:18px">{card("let", ul("Name and number", "Never change"))}{card("var", ul("Balance and status", "Can change"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPay needs the customer name Ravi, account number NP1001, a balance of ₹25,000, and whether the account is active. In Swift that is four declarations.'),
                  ('SAY', 'Click: the name and the account number are written with let. Click: the balance and the active flag with var.'),
                  ('SAY', 'Click: two keywords, fundamental to Swift. let for facts that never change after they are set; var for state that can.'),
                  ('CONNECT', 'What exactly is the difference?'))))

# ================================================================== 2
divider(2, "let versus var", "Can we change the balance?", 'let creates a binding that cannot be reassigned after initialization. var creates a mutable variable. Watch the compiler decide.', 'Same line, two keywords.')
LET = 'let balance = 25000\nbalance = 30000'
VAR = 'var balance = 25000\nbalance = 30000'
S.append(slide("Part 2 &middot; Reassignment", "Same assignment, two keywords", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start">
      <div>{code("Let.swift", LET, "font-size:18px")}
        <div class="card accent step" style="margin-top:14px;padding:16px 22px"><span class="label">Compiler</span><p style="margin:4px 0 0">{err("cannot assign to value: &lsquo;balance&rsquo; is a &lsquo;let&rsquo; constant")}</p></div></div>
      <div>{code("Var.swift", VAR, "font-size:18px")}
        <div class="card accent step" style="margin-top:14px;padding:16px 22px"><span class="label">Compiles</span><p style="margin:4px 0 0">balance is now <b>&#8377;30,000</b></p></div></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Prefer let">{ul("Use <code>let</code> unless the value must be <b>reassigned</b>", "It states <b>intent</b> and blocks <b>accidental</b> changes", "Careful: <code>let</code> does not always make an object immutable (Part 10)")}</div>
  </div>""", notes(('SAY', 'The same two lines, once with let and once with var.'),
                  ('SAY', 'Click: with let, the build fails. The real compiler message: cannot assign to value, balance is a let constant. Click: with var, it compiles and the balance becomes ₹30,000.'),
                  ('SAY', 'Click: prefer let whenever reassignment is unnecessary. It communicates intent and prevents accidental changes. The compiler even warns when a var is never changed. One subtlety we come back to in Part 10: let does not always mean the whole object is immutable.'),
                  ('CONNECT', 'Notice we never wrote a type. How did Swift know?'))))

# ================================================================== 3
divider(3, "Type inference", "Types without writing them", 'We have not declared a single type yet, and Swift still knows every one. Why?', 'The compiler reads the initial value.')
INF = """let name = "Ravi"
let age = 30
let balance = 25000.50
let isActive = true"""
INF_T = [('"Ravi"', 'String'), ('30', 'Int'), ('25000.50', 'Double'), ('true', 'Bool')]
trs = ''.join(f'<tr><td><code>{a}</code></td><td><b>{b}</b></td></tr>' for a, b in INF_T)
STAT = """var balance = 25000

balance = 30000       // valid
balance = "30000"     // error"""
S.append(slide("Part 3 &middot; Inference", "The initial value decides the type", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px;align-items:start">
      <div>{code("Inference.swift", INF, "font-size:18px")}
        <div class="gap"></div>
        <table class="tbl"><thead><tr><th>Initial value</th><th>Inferred type</th></tr></thead><tbody>{trs}</tbody></table></div>
      <div class="step">{code("Static.swift", STAT, "font-size:18px")}
        <p style="margin:10px 0 14px">{err("cannot assign value of type &lsquo;String&rsquo; to type &lsquo;Int&rsquo;")}</p>
        <div class="rule" data-label="Static typing + inference">{ul("Types are fixed at <b>compile time</b>", "Inference only saves <b>typing</b>", "A variable never <b>changes type</b> at run time")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Four declarations, no types written. The compiler examines the expression that initializes each one: "Ravi" is a String, 30 is an Int, 25000.50 is a Double, true is a Bool.'),
                  ('SAY', 'Click: inference is not dynamic typing. Once balance is an Int, 30000 is fine, but "30000" is the compile error we met in Lesson 1.1. Swift has static typing with type inference: the compiler decides the type during compilation, and a variable cannot change type at run time.'),
                  ('CONNECT', 'So which types are there to infer?'))))

# ================================================================== 4
divider(4, "Fundamental data types", "Six types you use every day", 'Here are the types the compiler inferred, and two more.', 'Six cards.')
TYPES = [("Int", "whole numbers", "let count = 3"), ("Double", "64-bit floating point", "let rate = 7.25"),
         ("Float", "32-bit floating point", "let ratio: Float = 0.5"), ("Bool", "true or false", "let isActive = true"),
         ("String", "text", 'let name = "Ravi"'), ("Character", "one extended grapheme cluster", 'let rupee: Character = "₹"')]
tcells = "\n".join(f'      <div class="card accent" style="padding:18px 22px"><span class="label">{t}</span><p style="margin:2px 0 10px;font-size:18px" class="muted">{d}</p><code style="font-size:16px">{E(c)}</code></div>' for t, d, c in TYPES)
S.append(slide("Part 4 &middot; Core types", "Six fundamental types", f"""  <div class="body">
    <div class="cols c3" style="gap:18px;align-items:stretch">
{tcells}
    </div>
    <div class="gap"></div>
    <div class="tip step" data-label="Sizes">{ul("Fixed-width integers: <code>Int8</code>, <code>UInt16</code>, <code>Int32</code>, <code>UInt64</code>&hellip;", "On iPhone and Mac, <code>Int</code> is <b>64-bit</b> (<code>Int.bitWidth == 64</code>)")}</div>
  </div>""", notes(('SAY', 'Int for whole numbers. Double for double-precision floating point. Float for single precision. Bool for true or false. String for text. And Character, a single extended grapheme cluster, which we come back to with strings.'),
                  ('SAY', 'Click: Swift also has fixed-width integers such as Int8, UInt16, Int32 and UInt64. On iPhone and Mac, Int is a 64-bit integer; you can check with Int.bitWidth. (On the Apple Watch arm64_32 architecture Int is 32-bit, which is one reason fixed widths exist.)'),
                  ('CONNECT', 'One of these types is dangerous for an app like NPay.'))))

# ================================================================== 5
divider(5, "Money: a very important warning", "Can we use Double for money?", 'NPay calculates a transfer. Can we store the amounts as Double?', 'Technically yes. Here is why we do not.')
FLT = """let a = 0.1
let b = 0.2

print(a + b == 0.3)
print(a + b)"""
PAISE = """let balanceMinor: Int64 = 2_500_000   // ₹25,000
let transferMinor: Int64 = 25_000     // ₹250

let remaining = balanceMinor - transferMinor
print(remaining)"""
S.append(slide("Part 5 &middot; Money", "Double cannot hold 0.1 exactly", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start">
      <div>{code("Double.swift", FLT, "font-size:18px")}
        {out("Prints <code>false</code>, then <code>0.30000000000000004</code>")}</div>
      <div class="step">{code("Paise.swift", PAISE, "font-size:16px")}
        {out("Prints <code>2475000</code>: exactly &#8377;24,750", '')}</div>
    </div>
    <div class="gap"></div>
    <div class="warn step" data-label="Money in NPay">{ul("Store <b>whole paise</b> in <code>Int64</code> (<code>balanceMinor</code>), or use a decimal type", "Still design <b>overflow</b>, <b>rounding</b> and <b>currency conversion</b>")}</div>
  </div>""", notes(('SAY', 'Binary floating point cannot represent many decimal fractions exactly; 0.1 and 0.2 are two of them.'),
                  ('ASK', 'Before the click: does 0.1 + 0.2 equal 0.3?'),
                  ('SAY', 'Click: false. The sum is 0.30000000000000004. Fine for a graphics coordinate, wrong for a bank balance.'),
                  ('SAY', 'Click: NPay uses integer minor units. ₹25,000 is 2,500,000 paise in an Int64; subtract a ₹250 transfer and you get exactly 2,475,000 paise, ₹24,750.'),
                  ('SAY', 'Click: for money, prefer integer minor units or an appropriate decimal type, depending on the domain. Integers remove binary rounding errors, but overflow, rounding rules and currency conversion still need careful design. Lesson 1.10 turns this into a real Money type.'),
                  ('CONNECT', 'Mixing number types has its own rules.'))))

# ================================================================== 6
divider(6, "Explicit type conversion", "Swift does not mix numeric types", 'Int and Double represent numbers differently, so Swift will not combine them silently.', 'Try it.')
CONV = """let count: Int = 3
let price: Double = 99.5

let total = count * price           // error
let total2 = Double(count) * price  // 298.5"""
TRUNC = """print(Int(3.9))            // 3
print(Int(-3.9))           // -3
print(Int(3.9.rounded()))  // 4"""
NL = [wire('M20 40H600', None, 'faint')]
for v in range(-4, 5):
    x = 310 + v * 70
    NL.append(wire(f'M{x} 34V46', None, 'faint'))
    NL.append(f'<text class="sm" x="{x}" y="68" text-anchor="middle">{v}</text>')
NL += [f'<text x="{310 + 3.9 * 70:g}" y="22" text-anchor="middle">3.9</text>',
       f'<text x="{310 - 3.9 * 70:g}" y="22" text-anchor="middle">&minus;3.9</text>',
       wire(f'M{310 + 3.9 * 70:g} 40H{310 + 3 * 70 + 4}' + head(310 + 3 * 70 + 4, 40, 'l'), None, 'lit'),
       wire(f'M{310 - 3.9 * 70:g} 40H{310 - 3 * 70 - 4}' + head(310 - 3 * 70 - 4, 40, 'r'), None, 'lit'),
       f'<circle class="fill-teal" cx="{310 + 3 * 70}" cy="40" r="6"/>', f'<circle class="fill-teal" cx="{310 - 3 * 70}" cy="40" r="6"/>',
       '<text class="mono" x="310" y="96" text-anchor="middle">TOWARD ZERO</text>']
S.append(slide("Part 6 &middot; Conversion", "Convert on purpose, know what you lose", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start">
      <div>{code("Convert.swift", CONV, "font-size:16px")}
        <p style="margin:10px 0 0">{err("binary operator &lsquo;*&rsquo; cannot be applied to operands of type &lsquo;Int&rsquo; and &lsquo;Double&rsquo;")}</p></div>
      <div class="step">{code("Truncate.swift", TRUNC, "font-size:16px")}
        <div class="gap"></div>
        {svg('0 0 620 100', 'Converting to Int truncates toward zero: 3.9 becomes 3, minus 3.9 becomes minus 3', 'trunc', NL, 'max-height:120px')}</div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Double to Int">{ul("<b>Truncates</b> toward zero; it does <b>not round</b>", "Round first with <code>.rounded()</code> when you mean rounding")}</div>
  </div>""", notes(('SAY', 'count is an Int, price a Double. count times price does not compile: binary operator star cannot be applied to Int and Double. Convert explicitly, Double(count) times price, and the result is 298.5.'),
                  ('SAY', 'Click: the other direction. Int(3.9) is 3, and Int(-3.9) is -3: for a finite, representable value, conversion to Int truncates the fractional part toward zero. It does not round. If you mean rounding, say so: Int(3.9.rounded()) is 4.'),
                  ('SAY', 'Click: the rule. Every conversion is visible in the code, and each one can lose information.'),
                  ('CONNECT', 'NPay also has to show these values to people.'))))

# ================================================================== 7
divider(7, "Strings and interpolation", "Text with values inside", 'NPay displays dynamic information: the customer&rsquo;s name and balance in one sentence.', 'Use interpolation.')
INTERP = """let customer = "Ravi"
let balance = 25000

let message =
    "Hello \\(customer), your balance is ₹\\(balance)"
print(message)"""
UNI = """let flag = "🇮🇳"

print(flag.count)                 // 1 Character
print(flag.unicodeScalars.count)  // 2 Unicode scalars"""
P = ['<g class="nd lit"><rect class="sh" x="0" y="0" width="240" height="90" rx="14"/><text x="70" y="58" text-anchor="middle" style="font-size:40px">🇮🇳</text><text x="160" y="52" text-anchor="middle">1 Character</text></g>',
     wire('M244 45H286' + head(286, 45, 'r')),
     box(292, 0, 260, 40, 'U+1F1EE', 'regional indicator I', None, '', ''),
     box(292, 50, 260, 40, 'U+1F1F3', 'regional indicator N', None, '', '')]
S.append(slide("Part 7 &middot; Strings", "Interpolation, and what a Character is", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start">
      <div>{code("Message.swift", INTERP, "font-size:15px")}
        {out("Prints <code>Hello Ravi, your balance is ₹25000</code>", '')}
        <div class="gap"></div>
        <div class="tip" data-label="Interpolation">{ul("<code>\\(&hellip;)</code> inserts a value&rsquo;s text into a string", "Formatting &ldquo;&#8377;25,000&rdquo; belongs in the ViewModel (0.2)")}</div></div>
      <div class="step">{code("Unicode.swift", UNI, "font-size:15px")}
        <div class="gap"></div>
        {svg('0 0 552 90', 'The India flag is one Character made of two Unicode scalars', 'uni', P, 'max-height:110px')}
        {out("A <b>Character</b> is an extended grapheme cluster: one or more Unicode scalars.", '')}</div>
    </div>
  </div>""", notes(('SAY', 'Swift uses backslash-parentheses for string interpolation. It inserts a textual representation of an expression into the string: Hello Ravi, your balance is ₹25000. Notice there is no thousands separator; display formatting such as ₹25,000 belongs in the ViewModel, as we said in Lesson 0.2.'),
                  ('SAY', 'Click: Swift strings are Unicode-aware. The India flag is one Character, but two Unicode scalars, the regional indicators I and N. A Swift Character is an extended grapheme cluster, which can be several scalars. That matters for emoji and for international names: count gives what a person sees as characters.'),
                  ('CONNECT', 'Sometimes we need to group a few values together.'))))

# ================================================================== 8
divider(8, "Tuples", "Grouping values without a custom type", 'A function needs to return both an account number and a balance. Do we need a new type?', 'Not always.')
TUP = """let account = (
    number: "NP1001",
    balance: 25000
)

print(account.number)    // NP1001
print(account.balance)   // 25000"""
S.append(slide("Part 8 &middot; Tuples", "Two values, one compound value", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:32px;align-items:center">
      {code("Tuple.swift", TUP, "font-size:18px")}
      <div>
        {card("Tuple", ul("Groups values into <b>one compound value</b>", "Good for <b>small, temporary</b> groupings", "Example: a function returning two results"))}
        <div class="gap"></div>
        {card("Struct instead", ul("Domain entities with <b>behavior</b>", "Validation and <b>long-term</b> structure", "Example: NPay&rsquo;s <code>BankAccount</code> (Part 11)"), 'step')}
      </div>
    </div>
  </div>""", notes(('SAY', 'A tuple groups several values into one compound value, here an account number and a balance, with labels so you can read account.number and account.balance.'),
                  ('SAY', 'Tuples are useful for small, temporary groupings, such as a function that returns two results.'),
                  ('SAY', 'Click: for domain entities with meaningful behavior, validation or long-term structure, a struct is usually the better choice. We build exactly that for NPay in Part 11.'),
                  ('CONNECT', 'For many values of the same kind, use a collection.'))))

# ================================================================== 9
divider(9, "Arrays, Sets and Dictionaries", "Three collections", 'NPay has a list of transactions, a set of payment methods and balances per customer. Each needs a different collection.', 'Here are all three.')
P = ['<text class="mono" x="0" y="14">ARRAY &middot; ORDERED</text>']
for i, v in enumerate(['500', '200', '900']):
    P.append(box(i * 120, 28, 110, 60, f'&#8377;{v}', f'[{i}]', None, '', ''))
P.append('<text class="mono" x="400" y="14">SET &middot; UNIQUE</text>')
for i, (v, x, y) in enumerate([('UPI', 400, 28), ('CARD', 520, 44), ('NEFT', 440, 100)]):
    P.append(f'<g class="nd"><rect class="sh" x="{x}" y="{y}" width="100" height="44" rx="22"/><text x="{x + 50}" y="{y + 28}" text-anchor="middle">{v}</text></g>')
P.append('<text class="mono" x="700" y="14">DICTIONARY &middot; KEY &rarr; VALUE</text>')
for i, (k, v) in enumerate([('"Ravi"', '25000'), ('"Meena"', '18000')]):
    y = 28 + i * 64
    P += [box(700, y, 180, 52, k, 'key', None, '', 'key'), wire(f'M884 {y + 26}H936' + head(936, y + 26, 'r')), box(942, y, 194, 52, v, 'value', None, '', '')]
COLL = """var transactions = [500, 200, 900]

let paymentMethods: Set<String> = ["UPI", "CARD", "NEFT"]

var balances: [String: Int] = ["Ravi": 25000, "Meena": 18000]"""
S.append(slide("Part 9 &middot; Collections", "Array, Set, Dictionary", f"""  <div class="body">
    {svg('0 0 1136 150', 'An array of three amounts with indexes, a set of three payment methods, a dictionary from names to balances', 'coll', P, 'max-height:170px')}
    <div class="gap"></div>
    {code("Collections.swift", COLL, "font-size:17px")}
    <div class="gap"></div>
    <div class="cols c3 step" style="gap:18px">
      {card("Array", ul("Keeps <b>order</b>", "Access by index"))}
      {card("Set", ul("<b>Unique</b> elements", "<b>No</b> guaranteed order"))}
      {card("Dictionary", ul("Unique <b>keys</b> &rarr; values", "Lookup returns an <b>optional</b>"))}
    </div>
  </div>""", notes(('SAY', 'An array of transaction amounts, a set of payment methods, and a dictionary from customer name to balance. The picture shows how each one organizes its elements.'),
                  ('SAY', 'Click: arrays preserve order and you access elements by index. Sets store unique elements and do not guarantee any iteration order. Dictionaries map unique keys to values, and a lookup returns an optional, because the key may not exist.'),
                  ('CONNECT', 'Those two last points surprise people. Here is the evidence.'))))

SETRUN = """let methods: Set<String> = ["UPI", "CARD", "NEFT"]
print(methods)"""
DICT = """var balances = ["Ravi": 25000, "Meena": 18000]

print(balances["Ravi"])   // Optional(25000)
print(balances["Asha"])   // nil"""
S.append(slide("Part 9 &middot; Evidence", "No order, and maybe no value", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start">
      <div>{code("SetOrder.swift", SETRUN, "font-size:16px")}
        <table class="tbl" style="margin-top:14px"><thead><tr><th>Run</th><th>Output</th></tr></thead><tbody><tr><td>1</td><td><code>["NEFT", "UPI", "CARD"]</code></td></tr><tr><td>2</td><td><code>["CARD", "NEFT", "UPI"]</code></td></tr></tbody></table>
        {out("Same program, different order on each run.", '')}</div>
      <div class="step">{code("Lookup.swift", DICT, "font-size:16px")}
        <div class="gap"></div>
        <div class="tip" data-label="Optional">{ul("A missing key gives <code>nil</code>, not a crash", "You unwrap the result: Lesson 1.3")}</div></div>
    </div>
  </div>""", notes(('SAY', 'We ran the same Set program twice. The first run printed NEFT, UPI, CARD; the second CARD, NEFT, UPI. Swift randomizes hashing per process, so never rely on a Set&rsquo;s order; sort it when order matters.'),
                  ('SAY', 'Click: a dictionary lookup returns an optional. balances["Ravi"] is Optional(25000); balances["Asha"] is nil, because there is no such key. The compiler also warns when you print an optional like this. Lesson 1.3 is all about unwrapping these safely.'),
                  ('CONNECT', 'Back to let: it hides a subtlety.'))))

# ================================================================== 10
divider(10, "let with classes", "The deeper meaning of let", 'Earlier we said let prevents reassignment. Now put let in front of a class and a struct.', 'One compiles, one does not.')
LCLS = """class BankAccount {
    var balance = 25000
}

let account = BankAccount()
account.balance = 30000"""
LSTR = """struct BankAccount {
    var balance = 25000
}

let account = BankAccount()
account.balance = 30000"""
RC = [box(0, 20, 200, 60, 'account', 'let &middot; constant reference', None, '', 'lock'),
      wire('M204 50H276' + head(276, 50, 'r')),
      box(282, 14, 270, 72, 'BankAccount instance', 'balance: 30000', None, 'lit', 'memory')]
RS = [box(0, 14, 552, 72, 'account', 'let &middot; the value itself: balance stays 25000', None, '', 'lock')]
S.append(slide("Part 10 &middot; let and mutation", "A constant reference versus a constant value", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      <div>{code("ClassAccount.swift", LCLS, "font-size:16px;min-height:200px")}
        <div class="step" style="margin-top:12px">{svg('0 0 552 100', 'let account is a constant reference to an instance whose balance changes to 30000', 'lc', RC)}
          {out("<b>Compiles.</b> The reference is constant; the instance is not.", '')}</div></div>
      <div>{code("StructAccount.swift", LSTR, "font-size:16px;min-height:200px")}
        <div class="step" style="margin-top:12px">{svg('0 0 552 100', 'let account is a constant value; its stored property cannot change', 'ls', RS)}
          <p style="margin:10px 0 0">{err("cannot assign to property: &lsquo;account&rsquo; is a &lsquo;let&rsquo; constant")}</p></div></div>
    </div>
  </div>""", notes(('SAY', 'The same five lines; only the first keyword differs, class or struct.'),
                  ('ASK', 'Before the clicks: which one compiles?'),
                  ('SAY', 'Click: the class compiles. account is a constant reference to a class instance: we cannot point account at a different instance, but the instance&rsquo;s mutable properties can still change.'),
                  ('SAY', 'Click: the struct does not. With a struct, account is the value itself, so a let binding prevents mutating its stored properties. The real message: cannot assign to property, account is a let constant.'),
                  ('CONNECT', 'Four combinations in one table.'))))

COMBO = [("<code>let</code> + struct", "No", "No"), ("<code>var</code> + struct", "Yes", "Yes"),
         ("<code>let</code> + class", "No", "<b>Yes</b>"), ("<code>var</code> + class", "Yes", "Yes")]
trs = ''.join(f'<tr{" class=\"hl\"" if "let</code> + class" in a else ""}><td>{a}</td><td>{b}</td><td>{c}</td></tr>' for a, b, c in COMBO)
S.append(slide("Part 10 &middot; Summary", "Reassign versus modify", f"""  <div class="body">
    <table class="tbl"><thead><tr><th>Declaration</th><th>Reassign the variable?</th><th>Modify a <code>var</code> property?</th></tr></thead><tbody>{trs}</tbody></table>
    <p class="small muted" style="margin:10px 0 0">Assumes the property is declared <code>var</code> and is accessible.</p>
    <div class="gap"></div>
    <div class="takeaway step"><code>let</code> fixes the <b>binding</b>. For a class, that binding is a <b>reference</b>, so the instance can still change.</div>
  </div>""", notes(('SAY', 'Read the table row by row. let with a struct: no reassigning, no modifying. var with a struct: both. let with a class: you cannot reassign the reference, but you can modify the instance&rsquo;s var properties; that is the highlighted row. var with a class: both. This assumes the property is declared var and is accessible.'),
                  ('SAY', 'Click: the takeaway. This is one of the most important ideas in Swift, and it comes straight from Lesson 1.1: values versus references.'),
                  ('CONNECT', 'Now combine everything into a real NPay model.'))))

# ================================================================== 11
divider(11, "A practical NPay model", "Putting it together", 'Constants, variables, Int64 paise, and a method that changes the balance safely.', 'Here is the model.')
MODEL = """struct BankAccount {
    let accountNumber: String
    var balanceMinor: Int64          // paise
    mutating func deposit(_ amountMinor: Int64) {
        guard amountMinor > 0 else { return }
        let (sum, overflow) = balanceMinor.addingReportingOverflow(amountMinor)
        guard !overflow else { return }
        balanceMinor = sum
    }
}
var account = BankAccount(accountNumber: "NP1001", balanceMinor: 2_500_000)
account.deposit(50_000)          // balanceMinor is now 2550000"""
S.append(slide("Part 11 &middot; Model", "NPay&rsquo;s first model", f"""  <div class="body">
    {code("BankAccount.swift", MODEL, "font-size:15px;line-height:1.45")}
    <div class="gap"></div>
    <div class="cols c3 tight" style="gap:18px;align-items:stretch">
      {card("mutating", ul("Needed to change a struct&rsquo;s <b>stored properties</b>"))}
      {card("Guards", ul("Only <b>positive</b> deposits", "Detect <b>overflow</b>, don&rsquo;t trap"), 'step')}
      {card("Production", ul("<b>Throw</b> errors (1.7)", "The <b>server</b> processes transactions"), 'step')}
    </div>
  </div>""", notes(('SAY', 'A struct with a constant account number and a variable balance in paise. deposit introduces a new keyword: mutating. A struct method that modifies stored properties must be marked mutating, because it changes the value itself.'),
                  ('SAY', 'Click: the model checks that the deposit is positive, and uses addingReportingOverflow so an overflow is detected instead of crashing the app. Depositing 50,000 paise, ₹500, gives 2,550,000.'),
                  ('SAY', 'Click: this is a teaching model. A production banking system would throw explicit errors instead of silently returning, and the server, not the app, processes transactions. Lesson 1.7 covers error handling.'),
                  ('LIVE DEMO', 'The full model from the lesson text, with customerName and isActive added back: struct BankAccount { let accountNumber: String; let customerName: String; var balanceMinor: Int64; var isActive: Bool; mutating func deposit(_:) as on the slide }. Create var account = BankAccount(accountNumber: "NP1001", customerName: "Ravi", balanceMinor: 2_500_000, isActive: true), call account.deposit(50_000), print(account.balanceMinor) → 2550000. Then change var account to let account and show the compile error on deposit.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.2', ('lang',), [("lock", "let by default", "var only when it must change"),
                            ("check", "Types fixed at build time", "inferred, converted explicitly"),
                            ("bank", "Money in paise", "Int64, never Double")],
         'Three things to remember. Use let by default and var only when the value must change; and remember let on a class fixes the reference, not the instance. Types are fixed at build time: inferred from the initial value, never mixed silently, converted explicitly, and Int(3.9) truncates. And money lives in whole paise in an Int64, never in a Double.')

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Eight questions, in different formats. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
review([("check", "Question", "Can a variable inferred as Int later hold a String?",
         "Can a Swift variable inferred as <code>Int</code> later hold a <code>String</code>?", "No",
         "Swift is statically typed. The inferred type stays <code>Int</code>; the assignment is a compile error.",
         "Confusing inference with dynamic typing.", "Python and JavaScript developers may say yes.", None),
        ("code", "Choose one", "What type does let balance = 25000.50 infer?",
         "What type does <code>let balance = 25000.50</code> infer?<br>A. Int<br>B. Float<br>C. Double<br>D. Decimal", "C",
         "A floating-point literal infers <code>Double</code> unless you write another type.",
         "Expecting Decimal because it looks like money.", "Some pick D, some B.", None),
        ("memory", "Question", "Can a let-bound class instance have a mutable property changed?",
         "Can a <code>let</code>-bound class instance have a <code>var</code> property changed?", "Yes",
         "The reference cannot be reassigned, but the instance&rsquo;s mutable properties can change.",
         "Thinking let freezes the whole object.", "Many say no.", None),
        ("diff", "Predict the output", "What does Int(-3.9) print?",
         "What does this print?<br><code>print(Int(-3.9))</code>", "-3",
         "Conversion to <code>Int</code> truncates toward zero. It does not round, and it does not floor to -4.",
         "Expecting rounding (-4) or flooring (-4).", "Most say -4.", None),
        ("layers", "Question", "Does a Set iterate in insertion order?",
         "Does a <code>Set</code> guarantee its elements are iterated in insertion order?", "No",
         "A Set has no guaranteed order; the same program can print a different order on each run.",
         "Relying on the order you wrote.", "Some say yes.", None),
        ("bank", "Question", "Is Double ideal for exact financial amounts?",
         "Is <code>Double</code> generally ideal for exact financial amounts?", "No",
         "Binary floating point cannot represent many decimal fractions exactly. NPay keeps whole paise in <code>Int64</code>.",
         "Trusting printed values that look exact.", "Most say no.", None),
        ("lock", "Question", "Must a struct method that modifies stored properties be marked mutating?",
         "Must a struct method that modifies its stored properties be marked <code>mutating</code>?", "Yes",
         "A <code>mutating</code> method is required to change a value type&rsquo;s stored state.",
         "Forgetting that a method on a value changes the value itself.", "Most say yes.", None),
        ("layers", "Choose one", "Which compiler stage rejects balance = \"30000\"?",
         "<code>var balance = 25000</code> then <code>balance = \"30000\"</code>. Which stage rejects it?<br>A. Parsing and semantic analysis<br>B. SIL optimization<br>C. LLVM code generation<br>D. At run time", "A",
         "Type checking is part of semantic analysis, before any SIL or machine code exists.",
         "Thinking type errors happen at run time.", "Some pick D.", "Spaced review from Lesson 1.1.")])

S.append(next_slide('1.2', [("1.3", "Optionals &amp; safe unwrapping", "the optional from a dictionary lookup"),
                            ("1.4", "Functions, parameters &amp; closures", "parameters such as <code>_ amountMinor</code>"),
                            ("1.5", "Structs, classes &amp; value semantics", "why <code>let</code> differs for classes"),
                            ("1.7", "Generics &amp; error handling", "a <code>deposit</code> that throws"),
                            ("1.10", "NPay domain model, actor ledger &amp; tests", "a real <code>Money</code> type")],
                    'Today&rsquo;s pieces each grow in this unit: the optional from a dictionary lookup in 1.3, function parameters in 1.4, value and reference semantics in 1.5, a deposit that throws real errors in 1.7, and in 1.10 the paise Int64 becomes a proper Money type with tests.'))

LAB = """struct BankAccount {
    let accountNumber: String
    var balanceMinor: Int64      // paise
    // deposit(_:) from the slide
    // TODO: mutating func withdraw(_ amountMinor: Int64) -> Bool
}"""
S.append(lab_slide('1.2', "Grow the NPay account", "Extend today&rsquo;s model and test your predictions on the command line.",
                   ["Start from <code>BankAccount</code> with <code>deposit</code>.",
                    "Add <code>withdraw</code>: reject amounts &le; 0 or above the balance; return <code>Bool</code>.",
                    "Predict, then print: <code>0.1 + 0.2 == 0.3</code>, <code>Int(3.9)</code>, <code>Int(-3.9)</code>.",
                    "Print a <code>Set</code> of payment methods; run twice and compare.",
                    "Make the account <code>let</code> and read the compiler error."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab (prefix xcrun on a Mac if needed). Reference withdraw: mutating func withdraw(_ amountMinor: Int64) -> Bool { guard amountMinor > 0, amountMinor <= balanceMinor else { return false }; balanceMinor -= amountMinor; return true }. Expected with balance 2,550,000: withdraw(10_000_000) is false, withdraw(25_000) is true and leaves 2,525,000. Predictions: false; 3; -3. The Set order can differ between runs. With let, the error is: cannot assign to property: the account is a let constant (or, calling withdraw: cannot use mutating member on immutable value).',
                   side=f'<div>{code("lab.swift", LAB, "font-size:15px")}<div class="gap"></div>{card("You hand in", ul("Your <code>withdraw</code>", "Predictions next to real outputs", "The compiler error, explained"))}</div>'))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 1.2 complete</p>
    <h2>Variables, Constants<br>&amp; Swift&rsquo;s Type System</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 1.3 &mdash; Optionals &amp; Safe Unwrapping</p>
  </div>
""" + notes(('SAY', 'You can now explain how Swift handles declarations, static typing and inference, numeric values, strings, tuples, collections and mutability, and, more importantly, why Swift&rsquo;s type system prevents certain mistakes before the app ever runs.'),
            ('SAY', 'Next, Lesson 1.3: optionals and safe unwrapping, starting with the optional we just got back from a dictionary lookup.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 1.2 — Variables, Constants &amp; Swift's Type System</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit 01 · Lesson 1.2 — Variables, Constants &amp; Type System">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT12, 'w').write(doc)
print(len(S), 'slides')
