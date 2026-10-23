"""Generates decks/unit-1/lesson-1.4/index.html from the Lesson 1.4 text (PocketBank -> NPay).
The text's 16 short sections are grouped into 8 Parts (see the lesson's "Deck changes")."""
import html, os, re, sys
OUT14 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'

title_slide('1.4', 'Functions, Parameters<br>&amp; Closures',
            'How does Swift <b>name</b>, <b>pass</b> and <b>run later</b> a piece of logic?',
            'We have learned variables, types and optionals. Now: how Swift organizes executable logic. This lesson matters because functions and closures are everywhere in iOS: SwiftUI buttons, networking, event handling, asynchronous work and dependency injection. We keep using NPay.')
outcomes_slide('1.4', [("code", "Write <b>functions</b> with parameters and return types"),
                       ("link", "Use <b>argument labels</b>, <code>_</code> and <b>default</b> values"),
                       ("layers", "Read <b>closure</b> syntax and trailing closures"),
                       ("phone", "Explain how a SwiftUI <b>Button</b> runs a closure"),
                       ("memory", "<b>Capture</b>, <code>@escaping</code> and retain cycles"),
                       ("diff", "Transform data with <code>map</code>, <code>filter</code>, <code>reduce</code>")])
where_slide('1.4', 'Today: logic you can name and pass', ('lang',),
            'Lesson 1.3: optionals make absence part of the type; unwrap with if let, guard let, ?? and ?.',
            'Functions name logic; closures turn logic into a value you can store, pass and run later.',
            'So far we have described data: types, optionals, collections. Today we organize the logic that works on that data. Functions give logic a name. Closures go one step further: logic becomes a value, and that is exactly how SwiftUI, networking and callbacks hand work back to your code.',
            'Start with a problem NPay already has.')

# ================================================================== Part 1 (text 1-2)
divider(1, "Functions", "Give reusable logic a name", 'NPay charges a 2% fee on transfers. Where does that rule live?', 'Right now, everywhere.')
REP = """let fee1 = 100_000 * 2 / 100   // ₹1,000
let fee2 = 250_000 * 2 / 100   // ₹2,500
let fee3 = 500_000 * 2 / 100   // ₹5,000"""
P = [box(0, 0, 240, 60, 'Transfer amount', 'input', None, '', 'send'), wire('M244 30H284' + head(284, 30, 'r')),
     box(290, 0, 240, 60, 'calculateFee', 'function', None, 'lit', 'code'), wire('M534 30H574' + head(574, 30, 'r')),
     box(580, 0, 240, 60, 'Fee amount', 'output', None, '', 'bank')]
S.append(slide("Part 1 &middot; The problem (section 1)", "The same rule, copied three times", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("Fees.swift", REP, "font-size:17px")}
      <div>{card("If the fee becomes 3%", ul("Find and change <b>every copy</b>", "Miss one: customers are charged <b>differently</b>"))}</div>
    </div>
    <div class="gap-lg"></div>
    <div class="step">{svg('0 0 820 60', 'Transfer amount goes into calculateFee, which returns the fee amount', 'io', P, 'max-height:80px')}</div>
  </div>""", notes(('SAY', 'NPay charges a 2% fee on transfers. Amounts are in paise, as in Lesson 1.2: 100,000 paise is ₹1,000, and 2% of it is 2,000 paise, ₹20. Without functions we repeat the calculation wherever a fee is needed.'),
                  ('SAY', 'If the fee changes from 2% to 3%, every copy must change, and missing one charges customers differently.'),
                  ('SAY', 'Click: a function gives the rule a name. An amount goes in, calculateFee runs, a fee comes out. One place to change.'),
                  ('CONNECT', 'Here is that function in Swift.'))))

FN = """func calculateFee(amountMinor: Int64) -> Int64 {
    return amountMinor * 2 / 100
}

let fee = calculateFee(amountMinor: 100_000)
print(fee)   // 2000 paise = ₹20"""
PARTS = [("<code>func</code>", "declares a function"), ("<code>calculateFee</code>", "the function name"),
         ("<code>amountMinor: Int64</code>", "parameter and its type"), ("<code>-&gt; Int64</code>", "return type"), ("<code>return</code>", "returns a result")]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in PARTS)
SIM = [("&#8377;1,000", "100_000", "2000", "&#8377;20"), ("&#8377;2,500", "250_000", "5000", "&#8377;50"), ("&#8377;5,000", "500_000", "10000", "&#8377;100")]
trs2 = ''.join(f'<tr><td>{a}</td><td><code>{b}</code></td><td><code>{c}</code></td><td><b>{d}</b></td></tr>' for a, b, c, d in SIM)
S.append(slide("Part 1 &middot; First function (section 2)", "Anatomy of a function", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Fee.swift", FN, "font-size:16px")}
        <div class="step"><table class="tbl" style="margin-top:14px"><thead><tr><th>Transfer</th><th>amountMinor</th><th>Returns</th><th>Fee</th></tr></thead><tbody>{trs2}</tbody></table></div></div>
      <table class="tbl"><thead><tr><th>Part</th><th>Meaning</th></tr></thead><tbody>{trs}</tbody></table>
    </div>
  </div>""", notes(('SAY', 'Read it left to right: func declares a function; calculateFee is its name; amountMinor colon Int64 is the parameter and its type; arrow Int64 is the return type; return hands back the result. Calling it with 100,000 paise returns 2,000, ₹20.'),
                  ('SAY', 'Click: run it for three transfers: ₹1,000 gives ₹20, ₹2,500 gives ₹50, ₹5,000 gives ₹100. These are the real outputs.'),
                  ('SAY', 'The lesson text used Double for the amount. In NPay money is whole paise in Int64, as in Lesson 1.2. Integer division also truncates, so a real fee needs an explicit rounding rule; that design comes in Lesson 1.10.'),
                  ('CONNECT', 'Two words people mix up: parameter and argument.'))))

# ================================================================== Part 2 (text 3-5)
divider(2, "Parameters and labels", "Readable calls by design", 'Parameters, arguments, and Swift&rsquo;s two-name parameters.', 'Start with the vocabulary.')
GREET = """func greet(name: String) {
    print("Hello, \\(name)")
}

greet(name: "Ravi")"""
S.append(slide("Part 2 &middot; Vocabulary (section 3)", "Parameter versus argument", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("Greet.swift", GREET, "font-size:18px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Parameter", ul("In the <b>declaration</b>: <code>name: String</code>", "What kind of input is accepted"))}
        {card("Argument", ul("In the <b>call</b>: <code>\"Ravi\"</code>", "The actual value supplied"), 'step')}
      </div>
    </div>
  </div>""", notes(('SAY', 'name in the function declaration is a parameter: it describes what kind of input the function accepts.'),
                  ('SAY', 'Click: "Ravi", passed when we call the function, is an argument: the actual value supplied. Think of a machine: the parameter is the slot&rsquo;s shape, the argument is the item you put in.'),
                  ('CONNECT', 'Swift gives each parameter up to two names.'))))

TRANSFER = """func transfer(from source: String,
              to destination: String,
              amountMinor: Int64) {
    print("\\(source) → \\(destination): \\(amountMinor)")
}

transfer(from: "NP1001", to: "NP2002", amountMinor: 50_000)"""
LBL = [("<code>from</code>", "<code>source</code>"), ("<code>to</code>", "<code>destination</code>"), ("<code>amountMinor</code>", "<code>amountMinor</code>")]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in LBL)
S.append(slide("Part 2 &middot; Argument labels (section 4)", "Outside name, inside name", f"""  <div class="body">
    {code("Transfer.swift", TRANSFER, "font-size:16px")}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div><table class="tbl"><thead><tr><th>External label (caller)</th><th>Internal name (body)</th></tr></thead><tbody>{trs}</tbody></table></div>
      <div class="step">{card("Without labels", f'<p style="margin:4px 0 8px"><code>transfer("NP1001", "NP2002", 50_000)</code></p>{err("missing argument labels &lsquo;from:to:amountMinor:&rsquo; in call")}')}</div>
    </div>
  </div>""", notes(('SAY', 'A distinctive Swift feature: a parameter can have an external argument label, used by the caller, and an internal name, used in the body. from and to are labels; source and destination are names. amountMinor uses one name for both.'),
                  ('SAY', 'The call reads like a sentence: transfer from NP1001 to NP2002, amount 50,000 paise. Labels make calls readable; internal names make the implementation understandable.'),
                  ('SAY', 'Click: leave the labels out and Swift refuses: missing argument labels from, to, amountMinor in call. The labels are part of the function&rsquo;s name, so intent stays visible at every call site.'),
                  ('CONNECT', 'Sometimes a label adds nothing.'))))

SQ = """func square(_ number: Int) -> Int {
    number * number
}

print(square(5))           // 25
print(square(number: 5))   // error"""
S.append(slide("Part 2 &middot; Omitting labels (section 5)", "The underscore removes the label", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Square.swift", SQ, "font-size:17px")}
        <p class="step" style="margin:12px 0 0">{err("extraneous argument label &lsquo;number:&rsquo; in call")}</p></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("_ number", ul("Callers write <b>no label</b>: <code>square(5)</code>", "Inside, the name is still <code>number</code>"))}
        {card("Use it when", ul("The function name already says it", "Like <code>print(x)</code>, <code>square(5)</code>"))}
      </div>
    </div>
  </div>""", notes(('SAY', 'The underscore means callers do not write an external label for that parameter: square(5) reads naturally. Inside the function the parameter is still called number.'),
                  ('SAY', 'Click: and now the label is not allowed: square(number: 5) fails with extraneous argument label number. Without the underscore, it is the other way round: the label is required.'),
                  ('CONNECT', 'Functions can also return more than one value, and supply defaults.'))))

# ================================================================== Part 3 (text 6-7)
divider(3, "Returns and defaults", "Tuples out, defaults in", 'Two conveniences: several results at once, and arguments you rarely need to pass.', 'Side by side.')
TUP = """func accountSummary() -> (balanceMinor: Int64,
                          isActive: Bool) {
    (balanceMinor: 2_500_000, isActive: true)
}

let result = accountSummary()
print(result.balanceMinor)   // 2500000
print(result.isActive)       // true"""
DEF = """func calculateFee(amountMinor: Int64,
                  percent: Int64 = 2) -> Int64 {
    amountMinor * percent / 100
}

print(calculateFee(amountMinor: 100_000))
// 2000
print(calculateFee(amountMinor: 100_000, percent: 3))
// 3000"""
S.append(slide("Part 3 &middot; Tuples and defaults (sections 6&ndash;7)", "Several results, optional arguments", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Summary.swift", TUP, "font-size:15px;min-height:268px")}
        <div class="gap"></div>
        {card("Tuple return", ul("Good for <b>small</b> grouped results", "Stable model with behavior: a <b>struct</b>"))}</div>
      <div class="step">{code("DefaultRate.swift", DEF, "font-size:15px;min-height:268px")}
        <div class="gap"></div>
        {card("Default value", ul("Callers <b>may omit</b> <code>percent</code>", "Override when needed: <code>percent: 3</code>"))}</div>
    </div>
  </div>""", notes(('SAY', 'A function can return a tuple: here a balance and an active flag together, read back as result.balanceMinor and result.isActive. Useful for small grouped results; for a stable domain model with behavior, a struct is better, as in Lesson 1.2.'),
                  ('SAY', 'Click: default parameter values. percent defaults to 2, so most callers write calculateFee(amountMinor:) and get 2,000; a caller that needs 3% passes percent: 3 and gets 3,000. Fewer repeated arguments, still customizable.'),
                  ('CONNECT', 'Now one of Swift&rsquo;s most important ideas: closures.'))))

# ================================================================== Part 4 (text 8-9)
divider(4, "Closures", "Logic as a value", 'A closure is a self-contained block of functionality that can be passed around and executed later.', 'An executable instruction package.')
FIRST = """let greet = {
    print("Hello from a closure")
}

greet()   // Hello from a closure"""
P = [box(0, 0, 300, 60, 'Create', 'a block of logic', '1+', '', 'code'), wire('M304 30H344' + head(344, 30, 'r')),
     box(350, 0, 300, 60, 'Store or pass it', 'a constant, a parameter', '2+', '', 'link'), wire('M654 30H694' + head(694, 30, 'r')),
     box(700, 0, 300, 60, 'Execute it', 'when needed', '3+', '', 'play')]
S.append(slide("Part 4 &middot; What is a closure? (section 8)", "Create it now, run it later", f"""  <div class="body">
    {svg('0 0 1000 60', 'Create a block of logic, store or pass it, execute it when needed', 'life', P, 'max-height:80px')}
    {cues(3)}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("FirstClosure.swift", FIRST, "font-size:17px")}
      {card("Functions are closures too", ul("A function is a <b>named</b> closure", "A closure <b>expression</b> is written inline"))}
    </div>
  </div>""", notes(('SAY', 'A closure is a self-contained block of functionality that can be passed around and executed later. Click through its life: create a block of logic; store it in a constant or pass it as an argument; execute it when needed.'),
                  ('SAY', 'The first closure: we assign a block to greet, and later call greet() like a function. It prints Hello from a closure.'),
                  ('SAY', 'Functions are also closures in Swift&rsquo;s broad sense; closure expressions are the inline form, and that is what we write most often.'),
                  ('CONNECT', 'Closures that take parameters need a little more syntax.'))))

ADD = """let add: (Int, Int) -> Int = { a, b in
    return a + b
}

print(add(10, 20))   // 30"""
READ = [("<code>(Int, Int) -&gt; Int</code>", "the closure&rsquo;s <b>type</b>"), ("<code>{ &hellip; }</code>", "the closure <b>expression</b>"),
        ("<code>a, b</code>", "its <b>parameters</b>"), ("<code>in</code>", "separates parameters from the <b>body</b>"), ("<code>return a + b</code>", "the <b>result</b>")]
trs = ''.join(f'<tr><td>{a}</td><td>{b}</td></tr>' for a, b in READ)
S.append(slide("Part 4 &middot; Syntax (section 9)", "Reading a closure", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Add.swift", ADD, "font-size:17px")}
        <div class="gap"></div>
        <div class="cols step" style="gap:14px">{card("Function", ul("Named, reusable", "<code>func add(&hellip;)</code>"))}{card("Closure", ul("Inline value", "<code>{ a, b in &hellip; }</code>"))}</div></div>
      <table class="tbl"><thead><tr><th style="width:230px">Piece</th><th>Meaning</th></tr></thead><tbody>{trs}</tbody></table>
    </div>
  </div>""", notes(('SAY', 'A closure that adds two numbers. Read it piece by piece: (Int, Int) -> Int is the closure&rsquo;s type; the braces contain the closure expression; a and b are its parameters; the keyword in separates the parameters from the body; return a + b produces the result. add(10, 20) is 30.'),
                  ('SAY', 'Click: a function is named reusable behavior; a closure expression is an inline executable value. Same idea, two forms.'),
                  ('CONNECT', 'Why does this matter so much in iOS?'))))

# ================================================================== Part 5 (text 10-12)
divider(5, "Closures in iOS", "Buttons, operations and trailing closures", 'Every SwiftUI button you write hands a closure to SwiftUI.', 'Follow a tap.')
BTN = """import SwiftUI

struct DashboardView: View {
    var body: some View {
        Button("Refresh balance") {
            print("Button tapped")
        }
    }
}"""
P = [box(0, 0, 520, 52, 'User taps the button', '', '1+', '', 'tap'), wire('M260 54V70' + head(260, 70, 'd')),
     box(0, 76, 520, 52, 'SwiftUI recognizes the activation', '', '2+', '', 'phone'), wire('M260 130V146' + head(260, 146, 'd')),
     box(0, 152, 520, 52, 'The action closure executes', '', '3+', '', 'code'), wire('M260 206V222' + head(260, 222, 'd')),
     box(0, 228, 520, 52, 'Application logic runs', '', '4+', '', 'gear')]
S.append(slide("Part 5 &middot; Buttons (section 10)", "A button stores your closure", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("DashboardView.swift", BTN, "font-size:16px")}
      {svg('0 0 520 280', 'User taps, SwiftUI recognizes the activation, the action closure executes, application logic runs', 'tap', P, 'max-height:320px')}
    </div>
    {cues(4)}
  </div>""", notes(('SAY', 'NPay&rsquo;s Refresh balance button. The code in the braces after Button is a closure. SwiftUI receives it, keeps it, and calls it when the button is activated.'),
                  ('SAY', 'Click through: the user taps; SwiftUI recognizes the activation; the action closure executes; application logic runs. This is the bridge between language fundamentals and event-driven UI, and it connects to Lesson 0.5: the closure runs on the main thread.'),
                  ('CONNECT', 'You can write functions that accept closures too.'))))

OP = """func performOperation(a: Int, b: Int,
                      operation: (Int, Int) -> Int) -> Int {
    operation(a, b)
}

performOperation(a: 10, b: 5,
                 operation: { x, y in x + y })   // 15"""
TRAIL = """performOperation(a: 10, b: 5) { x, y in
    x + y
}                                    // 15

Button("Transfer") {                 // SwiftUI
    print("Transfer tapped")
}"""
S.append(slide("Part 5 &middot; Passing closures (sections 11&ndash;12)", "Pass behavior in; trail it outside", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.3fr .7fr;gap:24px;align-items:start">
      <div>{code("Operation.swift", OP, "font-size:14px")}
        <div class="gap"></div>
        <div class="step">{code("Trailing.swift", TRAIL, "font-size:14px")}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Why it is powerful", ul("Same function, <b>any</b> operation", "<code>operation: *</code> gives 50"))}
        <div class="step">{card("Trailing closure", ul("Last argument a closure? Write it <b>after</b> <code>( )</code>", "Everywhere in SwiftUI"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'performOperation takes two numbers and an operation, itself a function-like value of type (Int, Int) -> Int. Pass an addition closure and you get 15. Pass the multiplication operator and you get 50, without changing performOperation at all. Behavior is supplied by the caller.'),
                  ('SAY', 'Click: when the last argument is a closure, Swift lets you write it after the parentheses. That is trailing closure syntax, and it is exactly what Button("Transfer") { &hellip; } uses.'),
                  ('CONNECT', 'Closures can also remember things.'))))

# ================================================================== Part 6 (text 13)
divider(6, "Capturing values", "A closure remembers", 'A closure can use values from the place where it was created, even after that place is gone.', 'Watch a counter.')
CNT = """func makeCounter() -> () -> Int {
    var count = 0
    return {
        count += 1
        return count
    }
}

let counter = makeCounter()
print(counter(), counter(), counter())   // 1 2 3
let other = makeCounter()
print(other())                           // 1"""
P = ['<rect class="wire faint" x="0" y="0" width="520" height="200" rx="16"/>',
     '<text class="mono" x="20" y="28">counter: CLOSURE + CAPTURED STATE</text>',
     box(20, 44, 230, 56, '{ count += 1 }', 'the code', None, '', 'code')]
for i in range(1, 4):
    P.append(f'<g class="fade" data-lit="{i}{"+" if i == 3 else ""}">{box(270, 44, 230, 56, f"count = {i}", f"counter() returned {i}", None, "lit", "memory")}</g>')
P.append(f'<g class="fade" data-lit="0">{box(270, 44, 230, 56, "count = 0", "not called yet", None, "", "memory")}</g>')
P.append(f'<g class="fade" data-lit="4+">{box(20, 124, 480, 56, "other: a new counter", "its own count, starting at 0", None, "", "memory")}</g>')
S.append(slide("Part 6 &middot; Capture (section 13)", "The closure outlives the function", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:center">
      {code("Counter.swift", CNT, "font-size:15px")}
      {svg('0 0 520 200', 'The counter closure keeps its own captured count, which grows 1, 2, 3; a new counter has its own count', 'cap', P, 'max-height:260px')}
    </div>
    {cues(4)}
    <div class="gap"></div>
    <div class="warn step" data-label="The other side">{ul("Captured state <b>outlives</b> the call that created it", "Capturing a class instance <b>strongly</b> can keep it alive (Part 7)")}</div>
  </div>""", notes(('SAY', 'makeCounter creates a local var count, then returns a closure that adds one and returns it. When makeCounter returns, its local variables would normally be gone.'),
                  ('SAY', 'Click: call counter(): 1. Click: 2. Click: 3. The closure still remembers count, because it captured it. That is capturing values.'),
                  ('SAY', 'Click: a second makeCounter() call creates a new closure with its own count, so other() starts again at 1.'),
                  ('SAY', 'Click: captured state can outlive the function call that created it. That is also why closures can create memory ownership problems when they strongly capture class instances.'),
                  ('CONNECT', 'Which brings us to escaping closures and ARC.'))))

# ================================================================== Part 7 (text 14-15)
divider(7, "Escaping closures and ARC", "When a closure is kept for later", 'Some closures run during the call; others are stored and run later. Swift makes you say which.', 'Compare two functions.')
NOW = """func executeNow(action: () -> Void) {
    action()                // runs during the call
}"""
LATER = """final class TaskManager {
    var savedAction: (() -> Void)?

    func register(action: @escaping () -> Void) {
        savedAction = action    // kept for later
    }
}"""
S.append(slide("Part 7 &middot; @escaping (section 14)", "Runs now, or escapes for later", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Now.swift", NOW, "font-size:15px")}
        <div class="gap"></div>
        {card("Non-escaping (default)", ul("Cannot <b>outlive</b> the call", "Safe to capture anything"))}</div>
      <div>{code("Later.swift", LATER, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{card("@escaping", ul("May run <b>after</b> the function returns", "Without it:") + '<p style="margin:2px 0 0 26px">' + err("assigning non-escaping parameter &lsquo;action&rsquo; to an &lsquo;@escaping&rsquo; closure") + '</p>')}</div></div>
    </div>
  </div>""", notes(('SAY', 'A non-escaping closure is guaranteed not to outlive the call it is passed to. executeNow runs its action during the call, and that is Swift&rsquo;s default for closure parameters.'),
                  ('SAY', 'An escaping closure may be stored or executed after the function returns. TaskManager stores the action in a property for later, so the parameter must be marked @escaping.'),
                  ('SAY', 'Click: leave @escaping out and the compiler refuses: assigning non-escaping parameter action to an @escaping closure. The marker is a warning sign to readers: this closure lives on, and so does everything it captures. That is where strong reference cycles can occur.'),
                  ('CONNECT', 'Here is that cycle in NPay.'))))

CYC = """@MainActor
final class DashboardViewModel {
    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = { self.refresh() }        // cycle
        // fix: { [weak self] in self?.refresh() }
    }

    func refresh() { print("Refreshing") }
    deinit { print("DashboardViewModel deinit") }
}"""
P = [box(0, 0, 250, 60, 'DashboardViewModel', '', None, '', 'layout'),
     box(330, 0, 220, 60, 'onRefresh closure', '', None, '', 'code'),
     wire('M254 22H326' + head(326, 22, 'r')), f'<text class="sm" x="290" y="14" text-anchor="middle">owns</text>',
     f'<g class="fade" data-lit="0">{wire("M326 44H254" + head(254, 44, "l"), None, "lit")}<text class="sm" x="290" y="62" text-anchor="middle">strong self</text></g>',
     f'<g class="fade" data-lit="1+">{wire("M326 44H254" + head(254, 44, "l"), None, "dash lit")}<text class="sm" x="290" y="62" text-anchor="middle">weak self</text></g>']
RUNS = [("strong <code>self</code>", "nothing prints: <b>leaked</b>"), ("<code>[weak self]</code>", "&ldquo;deinit&rdquo; prints: <b>freed</b>")]
trs = ''.join(f'<tr><td style="white-space:nowrap">{a}</td><td>{b}</td></tr>' for a, b in RUNS)
S.append(slide("Part 7 &middot; Closures and ARC (section 15)", "A closure that owns its owner", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DashboardViewModel.swift", CYC, "font-size:13px")}
      <div>{svg('0 0 550 70', 'The ViewModel owns the closure; the closure captures self strongly, or weakly after the fix', 'cyc', P, 'max-height:90px')}
        <div class="gap"></div>
        <div class="step"><p class="small muted" style="margin:0 0 4px">Set the ViewModel to <code>nil</code> and run:</p>
        <table class="tbl"><thead><tr><th>Capture</th><th>Result</th></tr></thead><tbody>{trs}</tbody></table></div>
        <div class="gap"></div>
        <div class="rule step" data-label="Not every closure">{ul("<code>[weak self]</code> only for <b>escaping</b> closures that self <b>keeps</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'This connects to Lesson 0.6. The ViewModel strongly owns its onRefresh closure, and the closure strongly captures self, the ViewModel. Each keeps the other alive: a retain cycle.'),
                  ('SAY', 'Click: the evidence. We created the ViewModel, configured it and set it to nil. With the strong capture, nothing prints: deinit never runs, the ViewModel leaked. With [weak self], DashboardViewModel deinit prints: it was freed.'),
                  ('SAY', 'Click: weak capture is right when you need to break an unwanted ownership relationship, typically an escaping closure stored by the object it captures. Not every closure needs [weak self]: a non-escaping closure, or a map or filter, cannot create this cycle. Lesson 1.8 goes deeper.'),
                  ('CONNECT', 'Last, the closures you will use most every day.'))))

# ================================================================== Part 8 (text 16)
divider(8, "map, filter, reduce", "Higher-order functions", 'Swift collections have functions that take closures. NPay has a list of transaction amounts.', 'Transform, select, combine.')
HOF = """let transactions = [500, 1200, 300, 2500]

let doubled = transactions.map { $0 * 2 }        // [1000, 2400, 600, 5000]
let large = transactions.filter { $0 > 1000 }    // [1200, 2500]
let total = transactions.reduce(0) { result, value in
    result + value
}                                                // 4500"""
P = ['<text class="mono" x="0" y="14">ORIGINAL</text>']
VALS = [500, 1200, 300, 2500]
for i, v in enumerate(VALS):
    P.append(box(220 + i * 140, 0, 120, 44, str(v), '', None, '', ''))
P.append('<text class="mono" x="0" y="80">map { $0 * 2 }</text>')
for i, v in enumerate(VALS):
    P.append(box(220 + i * 140, 62, 120, 44, str(v * 2), '', '1', '', ''))
P.append('<text class="mono" x="0" y="142">filter { $0 &gt; 1000 }</text>')
for i, v in enumerate(VALS):
    P.append(box(220 + i * 140, 124, 120, 44, str(v), 'kept' if v > 1000 else 'dropped', '2' if v > 1000 else None, '' if v > 1000 else 'ghost', ''))
P.append('<text class="mono" x="0" y="204">reduce(0, +)</text>')
P.append(box(220, 186, 540, 44, '500 + 1200 + 300 + 2500 = 4500', '', '3+', '', ''))
S.append(slide("Part 8 &middot; Higher-order functions (section 16)", "Transform, select, combine", f"""  <div class="body">
    {svg('0 0 780 230', 'map doubles every value; filter keeps 1200 and 2500; reduce adds them all to 4500', 'hof', P, 'max-height:250px')}
    {cues(3)}
    <div class="gap"></div>
    {code("Transactions.swift", HOF, "font-size:15px")}
  </div>""", notes(('SAY', 'Four transaction amounts. Each of these functions takes a closure; $0 is the shorthand name for the closure&rsquo;s first argument.'),
                  ('SAY', 'Click: map transforms each element: doubling gives 1000, 2400, 600, 5000. Click: filter selects the elements that match: above 1000 keeps 1200 and 2500. Click: reduce combines everything into one value, starting from 0 and adding each element: 4500.'),
                  ('SAY', 'They chain: transactions.filter { $0 > 1000 }.reduce(0, +) is 3700. And these closures are non-escaping: they run during the call, so no [weak self] needed. Collections and performance come back in later lessons.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.4', ('lang',), [("code", "Functions name logic", "labels make calls read well"),
                            ("layers", "Closures are values", "stored, passed, run later"),
                            ("memory", "Captures keep things alive", "@escaping + self: think weak")],
         'Three things to remember. Functions give logic a name, and argument labels, underscores and defaults make the call site read clearly. Closures are logic as a value: SwiftUI stores your button&rsquo;s closure and runs it on a tap, and trailing closure syntax keeps that readable. And closures capture what they use: an escaping closure kept by the object it captures strongly is a retain cycle, which [weak self] breaks.')

review_divider(8)
review([("code", "Choose one", "In greet(name: \"Ravi\"), which is the argument?",
         "In <code>greet(name: \"Ravi\")</code>, what is the argument?<br>A. <code>greet</code><br>B. <code>name</code><br>C. <code>\"Ravi\"</code><br>D. <code>String</code>", "C",
         "The argument is the value supplied at the call. <code>name</code> is the parameter (and here also the label).",
         "Calling the label the argument.", "Some pick B.", None),
        ("link", "Choose one", "Which call compiles for func square(_ number: Int)?",
         "Given <code>func square(_ number: Int) -&gt; Int</code>, which call compiles?<br>A. <code>square(number: 5)</code><br>B. <code>square(5)</code><br>C. <code>square(_: 5)</code><br>D. <code>square(n: 5)</code>", "B",
         "The underscore removes the external label, so callers pass the value alone. A label is now an error.",
         "Thinking the internal name is still the label.", "Some pick A.", None),
        ("bank", "Predict the output", "What does calculateFee(amountMinor: 250_000) return with the default 2%?",
         "<code>func calculateFee(amountMinor: Int64, percent: Int64 = 2) -&gt; Int64</code><br>What does <code>calculateFee(amountMinor: 250_000)</code> return?", "5000",
         "The default <code>percent</code> of 2 is used: 250,000 &times; 2 / 100 = 5,000 paise, &#8377;50.",
         "Thinking a defaulted argument must still be passed.", "Most get it.", None),
        ("memory", "Predict the output", "What prints for two counters?",
         "<code>let a = makeCounter()</code><br><code>let b = makeCounter()</code><br><code>print(a(), a(), b())</code>", "1 2 1",
         "Each call to <code>makeCounter()</code> creates a new closure with its own captured <code>count</code>.",
         "Thinking all counters share one count.", "Some say 1 2 3.", None),
        ("clock", "Question", "Must a closure parameter that is stored for later be marked @escaping?",
         "A function stores its closure parameter in a property. Must the parameter be marked <code>@escaping</code>?", "Yes",
         "A closure that may run after the function returns escapes; the compiler rejects storing it otherwise.",
         "Thinking @escaping is an optimization hint.", "Most say yes.", None),
        ("cross", "Question", "Does every closure need [weak self]?",
         "Does every closure that uses <code>self</code> need <code>[weak self]</code>?", "No",
         "Only when a cycle is possible, typically an escaping closure stored by the object it captures. <code>map</code>, <code>filter</code> and other non-escaping closures cannot create it.",
         "Adding [weak self] everywhere out of habit.", "Many say yes.", None),
        ("diff", "Predict the output", "What is transactions.filter { $0 > 1000 }.reduce(0, +)?",
         "<code>let transactions = [500, 1200, 300, 2500]</code><br><code>print(transactions.filter { $0 &gt; 1000 }.reduce(0, +))</code>", "3700",
         "<code>filter</code> keeps 1200 and 2500; <code>reduce(0, +)</code> adds them.",
         "Adding everything (4500).", "Some say 4500.", None),
        ("decision", "Choose one", "What does onRefresh?() do when onRefresh is nil?",
         "<code>var onRefresh: (() -&gt; Void)? = nil</code><br>What does <code>onRefresh?()</code> do?<br>A. Traps at run time<br>B. Nothing; the expression is nil<br>C. Compile error<br>D. Calls an empty closure", "B",
         "Optional chaining works on optional closures too: with no closure, nothing is called and the result is <code>nil</code>.",
         "Expecting a crash, like force unwrapping.", "Some pick A.", "Spaced review from Lesson 1.3.")])

S.append(next_slide('1.4', [("1.5", "Structs, classes &amp; value semantics", "what a closure captures: a copy or a reference"),
                            ("1.7", "Generics &amp; error handling", "why <code>map</code> works for any element type"),
                            ("1.8", "ARC, ownership &amp; memory management", "capture lists and cycles in depth"),
                            ("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "<code>async</code> instead of callbacks, <code>@Sendable</code> closures"),
                            ("2.3", "Text, images, buttons &amp; modifiers", "SwiftUI actions as closures")],
                    'Closures run through the rest of the course. 1.5 explains what a closure captures for values and references; 1.7 shows why map works for any element type; 1.8 goes deep on capture lists and cycles; 1.9 replaces many callbacks with async and introduces Sendable closures; and in Unit 02 every SwiftUI action is a closure.'))

LAB = """let transfers: [Int64] = [50_000, 120_000, 30_000, 250_000]  // paise

// 1. calculateFee(amountMinor:percent:) with percent = 2 by default
// 2. fees for transfers above ₹1,000:  filter, then map
// 3. total of those fees:              reduce
// 4. makeReceiptCounter() -> () -> String   // "NP-R1", "NP-R2"…"""
S.append(lab_slide('1.4', "NPay fee toolkit", "Functions, closures and higher-order functions on real NPay amounts.",
                   ["Write <code>calculateFee</code> with a 2% default.",
                    "Fees above &#8377;1,000: <code>filter</code>, then <code>map</code>.",
                    "Total them with <code>reduce</code>.",
                    "A receipt counter: &ldquo;NP-R1&rdquo;, &ldquo;NP-R2&rdquo;&hellip;",
                    "Run the cycle demo: predict <code>deinit</code>, then fix it."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab. Expected: transfers above 100,000 paise are [120000, 250000]; fees [2400, 5000]; total 7400 paise (₹74). makeReceiptCounter: var n = 0; return { n += 1; return "NP-R\\(n)" } prints NP-R1 then NP-R2. Cycle: with the strong capture, setting the ViewModel to nil prints nothing; with [weak self], DashboardViewModel deinit prints. The class is @MainActor, so wrap the test in a @MainActor function and call it with MainActor.assumeIsolated { run() } at top level.',
                   side=f'<div>{code("lab.swift", LAB, "font-size:14px")}<div class="gap"></div>{card("You hand in", ul("Large transfers, their fees and the total", "Your receipt numbers", "deinit: before and after the fix"))}</div>'))

end_slide('1.4', 'Functions, Parameters<br>&amp; Closures', 'Lesson 1.5 &mdash; Structs, Classes &amp; Value Semantics',
          'You can now write functions with labels and defaults, read closure syntax and trailing closures, explain how a SwiftUI button runs your closure, describe capture and @escaping, spot a closure retain cycle, and use map, filter and reduce.',
          'Next, Lesson 1.5: structs, classes and value semantics, including what a closure actually captures when it uses a value or a reference.')

write_deck(OUT14, '1.4', 'Functions, Parameters &amp; Closures', 'Functions, Parameters &amp; Closures')
