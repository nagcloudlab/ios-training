"""Generates decks/unit-1/lesson-1.8/index.html from the Lesson 1.8 text (PocketBank -> NPay).
The text's 13 sections are grouped into 7 Parts (see the lesson's "Deck changes")."""
import html, os, re, sys
OUT18 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'
tbl = lambda head_, rows, cls='tbl compact': f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head_) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'

title_slide('1.8', 'ARC, Ownership<br>&amp; Memory Management',
            'Why does an object sometimes <b>stay alive</b> after the screen that created it has gone?',
            'Lesson 0.6 introduced iOS memory. Today we go deeper into how Swift actually manages object lifetimes, with runnable examples and the ownership decisions you make every day. The question: why does an object sometimes stay alive after the screen that created it has disappeared? We investigate it in NPay.')
outcomes_slide('1.8', [("memory", "What <b>ARC</b> does, and what it doesn&rsquo;t"),
                       ("link", "<b>Strong</b> references and <b>cycles</b>"),
                       ("diff", "<b>weak</b> versus <b>unowned</b>"),
                       ("code", "Closures, <b>timers</b> and <b>tasks</b> that keep objects alive"),
                       ("layers", "ARC versus <b>garbage collection</b>"),
                       ("eye", "How to <b>investigate</b> a leak")])
where_slide('1.8', 'Today: who keeps an object alive', (),
            'Lesson 1.7: generics keep types; errors are typed values handled by the right layer.',
            'ARC and ownership in depth, with leaks you can reproduce and fix.',
            'Lesson 0.6 showed memory from the platform side, and 1.4 and 1.5 showed closures and classes. Today we put them together: who owns what, why an NPay screen can refuse to die, and how to prove a fix works.',
            'Start with a screen that refuses to die.')

# ================================================================== Part 1 (1-2)
divider(1, "A screen that refuses to die", "And what ARC really does", 'Every visit to NPay&rsquo;s transaction history creates a TransactionViewModel. What happens when you leave?', 'We counted.')
STORY = """@MainActor
final class TransactionViewModel {
    static var live = 0                    // instances alive now
    var onRefresh: (() -> Void)?

    init() {
        Self.live += 1
        onRefresh = { self.load() }        // strong capture
    }
    func load() {}
    deinit { MainActor.assumeIsolated { Self.live -= 1 } }
}"""
P = ['<text class="mono" x="0" y="14">ALIVE AFTER 3 VISITS (REAL COUNT)</text>']
for i in range(3):
    P.append(fade('1+', box(i * 186, 30, 172, 56, f'ViewModel {i + 1}', 'still alive', None, '', 'layout')))
P.append(fade('1+', '<text x="0" y="118" style="font-size:20px">Strong capture: <tspan style="font-weight:800">3</tspan></text>'))
P.append(fade('2+', '<text x="0" y="156" style="font-size:20px">[weak self]: <tspan style="font-weight:800">0</tspan></text>'))
S.append(slide("Part 1 &middot; The story (section 1)", "Open and close the screen three times", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.1fr .9fr;gap:24px;align-items:start">
      {code("TransactionViewModel.swift", STORY, "font-size:13px")}
      <div>{svg('0 0 544 160', 'After three visits with a strong capture, three ViewModels are still alive; with weak self, zero', 'leak', P, 'max-height:200px')}
        {cues(2)}
        <div class="gap"></div>
        <div class="tip step" data-label="Why">{ul("Each ViewModel owns a closure that owns the ViewModel", "Nothing outside holds it, yet it never goes away")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Every visit to the transaction-history screen creates a TransactionViewModel. When the user leaves, we expect it to be released. The code counts live instances: init adds one, deinit subtracts one. Notice the closure captures self.'),
                  ('SAY', 'Click: we simulated three visits in a real program and read the count. With the strong capture: 3. Every visit leaves a ViewModel behind. Click: change the capture to weak self and the count is 0.'),
                  ('SAY', 'Click: each ViewModel owns a closure, and the closure owns the ViewModel. Nothing outside holds them, yet ARC never frees them. To see why, revisit ARC.'),
                  ('CONNECT', 'What ARC actually does.'))))

P = [box(0, 0, 340, 56, 'Instance created', '', '1+', '', 'memory'), wire('M170 60V80' + head(170, 80, 'd')),
     box(0, 86, 340, 56, 'Strong references keep it alive', '', '2+', '', 'link'), wire('M170 146V166' + head(170, 166, 'd')),
     box(0, 172, 340, 56, 'Last strong reference released', 'then deinit', '3+', '', 'cross')]
S.append(slide("Part 1 &middot; ARC (section 2)", "Automatic Reference Counting", f"""  <div class="body">
    {cues(3)}
    <div class="cols" style="grid-template-columns:.8fr 1.2fr;gap:28px;align-items:center">
      {svg('0 0 340 228', 'Instance created; strong references keep it alive; last strong reference released, then deinit', 'arc', P, 'max-height:300px')}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Automatic", ul("The <b>compiler</b> inserts and optimizes retain/release", "For <b>class</b> instances (and closures, actors)"))}
        <div class="rule step" data-label="Not effortless">{ul("<b>You</b> design ownership: which references keep things alive")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'ARC, Automatic Reference Counting, manages the lifetimes of class instances, and also closures and actors. Click through: an instance is created; strong references keep it alive; when the last strong reference is released, it is deinitialized.'),
                  ('SAY', 'The compiler inserts and optimizes the reference-management operations for you. Do not picture a fixed sequence of literal increments: the optimizer removes many of them.'),
                  ('SAY', 'Click: automatic does not mean you can ignore ownership. The language decides when to retain and release; you decide which references own something. That is the rest of this lesson.'),
                  ('CONNECT', 'Watch lifetimes happen.'))))

# ================================================================== Part 2 (3-4)
divider(2, "Lifetimes and strong references", "Watch objects come and go", 'deinit tells us exactly when an instance dies.', 'Two experiments.')
LIFE = """final class Customer {
    let name: String
    init(name: String) {
        self.name = name; print("\\(name) created")
    }
    deinit { print("\\(name) destroyed") }
}
func testCustomer() {
    let customer = Customer(name: "Ravi")
    print(customer.name)
}
testCustomer()"""
STRONG = """var customerA: Customer? = Customer(name: "Meena")
var customerB = customerA

customerA = nil;  print("a = nil")
customerB = nil;  print("b = nil")"""
P = [box(0, 0, 200, 50, 'customerA', '', None, '', 'link'), box(0, 74, 200, 50, 'customerB', '', None, '', 'link'),
     fade('0', wire('M204 25L276 55' + head(276, 55, 'r'))), fade('0-1', wire('M204 99L276 75' + head(276, 75, 'r'))),
     fade('0-1', box(282, 37, 270, 50, 'Customer "Meena"', 'alive', None, 'lit', 'memory')),
     fade('2+', box(282, 37, 270, 50, 'destroyed', 'no strong references left', None, 'ghost', 'cross'))]
S.append(slide("Part 2 &middot; Lifetimes (sections 3&ndash;4)", "deinit runs when the last owner lets go", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Lifetime.swift", LIFE, "font-size:13px")}
        <div style="margin-top:12px">{card("Prints", mono("Ravi created<br>Ravi<br>Ravi destroyed"))}</div></div>
      <div>{code("Strong.swift", STRONG, "font-size:13px")}
        <div class="gap"></div>
        {svg('0 0 552 124', 'Two variables reference one Customer; setting the first to nil keeps it alive; setting the second to nil destroys it', 'strong', P, 'max-height:140px')}
        {cues(2)}
        <div style="margin-top:10px">{card("Prints", mono("Meena created<br>a = nil<br>Meena destroyed<br>b = nil"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Left: Customer prints when it is created and destroyed. Inside testCustomer it lives only while the function needs it; real output: created, Ravi, destroyed. Nothing escaped, so it is freed at the end of its use. The optimizer may even end lifetimes earlier than the closing brace.'),
                  ('SAY', 'Right: two variables refer to one Customer. Click: customerA = nil releases one reference, and nothing is destroyed; customerB still owns it. Click: customerB = nil releases the last one, and only now does it print Meena destroyed.'),
                  ('SAY', 'The takeaway: setting a variable to nil releases that reference; it does not necessarily destroy the object.'),
                  ('CONNECT', 'So what if two objects own each other?'))))

# ================================================================== Part 3 (5-6)
divider(3, "Cycles and weak references", "Two owners that never let go", 'A customer owns an account. The account points back to the customer.', 'Strongly, at first.')
CYC = """final class Customer {
    var account: Account?
    deinit { print("Customer destroyed") }
}
final class Account {
    var owner: Customer?            // strong: cycle
    deinit { print("Account destroyed") }
}

var customer: Customer? = Customer()
var account: Account? = Account()
customer?.account = account
account?.owner = customer
customer = nil;  account = nil      // prints nothing"""
WEAK = """final class Account {
    weak var owner: Customer?       // does not own
}
// customer = nil  →  "Customer destroyed"
// account.owner   →  nil"""
P = [box(0, 0, 230, 56, 'Customer', '', None, '', 'user'), box(322, 0, 230, 56, 'Account', '', None, '', 'bank'),
     wire('M234 18H318' + head(318, 18, 'r')), '<text class="sm" x="276" y="12" text-anchor="middle">owns</text>',
     fade('0', wire('M318 40H234' + head(234, 40, 'l'), None, 'lit') + '<text class="sm" x="276" y="70" text-anchor="middle">owns back: cycle</text>'),
     fade('1+', wire('M318 40H234' + head(234, 40, 'l'), None, 'dash') + '<text class="sm" x="276" y="70" text-anchor="middle">weak: not owned</text>')]
S.append(slide("Part 3 &middot; Cycles and weak (sections 5&ndash;6)", "A cycle, and the one-word fix", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Cycle.swift", CYC, "font-size:13px")}
      <div>{svg('0 0 552 76', 'Customer owns Account; Account owns Customer back, a cycle; with weak, the back reference does not own', 'cyc', P, 'max-height:90px')}
        {cues(1)}
        <div class="gap"></div>
        <div class="step">{code("WeakOwner.swift", WEAK, "font-size:13px")}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="ARC won't find it">{ul("ARC does <b>not</b> detect cycles", "You decide who owns whom")}</div></div>
    </div>
  </div>""", notes(('SAY', 'A customer owns an account; the account also strongly references its owner. Set both variables to nil and nothing prints: neither deinit runs. Each instance still holds the other. That is a strong-reference cycle.'),
                  ('SAY', 'Click: the customer owns the account, but the account only needs to know who owns it. Make the back-reference weak.'),
                  ('SAY', 'Click: we ran it. Now setting customer to nil prints Customer destroyed, and the account&rsquo;s owner is automatically nil. A weak reference never keeps its target alive.'),
                  ('SAY', 'Click: ARC does not detect and break arbitrary cycles. Designing the ownership is your job.'),
                  ('CONNECT', 'weak has a sibling: unowned.'))))

# ================================================================== Part 4 (7) + ownership extras
divider(4, "weak versus unowned", "Two ways not to own", 'Both avoid keeping the target alive. They fail very differently.', 'Compare them.')
WU = [("Keeps target alive", "No", "No"), ("Type", "Optional (<code>var</code>)", "Usually non-optional"),
      ("Target destroyed", "Becomes <code>nil</code>", "Stays; access <b>traps</b>"),
      ("Use when", "Target <b>may</b> go first", "Target <b>always</b> outlives the reference")]
UN = """final class CreditCard {
    unowned let customer: Customer
    init(customer: Customer) { self.customer = customer }
}"""
S.append(slide("Part 4 &middot; weak vs unowned (section 7)", "nil, or a crash", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{tbl(["", "weak", "unowned"], WU, 'tbl')}</div>
      <div>{code("CreditCard.swift", UN, "font-size:14px")}
        <div class="step" style="margin-top:12px">{card("Read it after the customer is gone", mono("Fatal error: Attempted to read an unowned<br>reference but object 0x&hellip; was already destroyed", 14))}</div>
        <div class="gap"></div>
        <div class="tip step" data-label="unowned(unsafe)">{ul("No check at all: <b>undefined behaviour</b>. Avoid in app code.")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Neither weak nor unowned keeps its target alive. weak is an optional var that automatically becomes nil when the target goes. unowned is usually non-optional and does not become nil.'),
                  ('SAY', 'A CreditCard cannot exist without its customer, so it holds the customer unowned. Click: if the customer is destroyed first and the card reads it anyway, the app traps. Real message: attempted to read an unowned reference but the object was already destroyed.'),
                  ('SAY', 'So use unowned only when the lifetime relationship guarantees the target outlives every access; otherwise use weak. Click: and unowned(unsafe) removes even that check: reading it after deallocation is undefined behaviour. Avoid it in app code. This answers the question left open in Lesson 0.6.'),
                  ('CONNECT', 'Swift&rsquo;s ownership story is not only about classes.'))))

NC = """struct ExportToken: ~Copyable {
    let id: Int
    deinit { print("token \\(id) released") }
}
func upload(_ token: consuming ExportToken) {
    print("uploading with token \\(token.id)")
}

let token = ExportToken(id: 1)
upload(token)          // ownership moves in
// upload(token)       // error: consumed more than once"""
S.append(slide("Part 4 &middot; Ownership for values (authored)", "Non-copyable types: one owner, by law", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.15fr .85fr;gap:24px;align-items:start">
      {code("ExportToken.swift", NC, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Prints", mono("uploading with token 1<br>token 1 released"))}
        {card("~Copyable", ul("A struct that <b>cannot be copied</b>", "Can have a <code>deinit</code> (Lesson 1.5)", "<code>consuming</code>: ownership <b>moves</b>"), 'step')}
        <div class="step">{card("Use it twice", '<p style="margin:4px 0 0">' + err("&lsquo;token&rsquo; consumed more than once") + '</p>')}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'This slide is beyond the lesson text; Lesson 1.5 promised it. Swift 5.9 added non-copyable types. ExportToken is a struct marked tilde Copyable: it cannot be copied, so it always has exactly one owner, and it can have a deinit.'),
                  ('SAY', 'upload takes the token as consuming: ownership moves into the function. Real output: uploading with token 1, then token 1 released, when upload finishes with it.'),
                  ('SAY', 'Click: that is the point: a value with exactly one owner, enforced by the compiler. Click: use it a second time and the build fails: token consumed more than once. Good for one-time resources like an export token or a file handle. You will see it rarely in app code, but it shows where Swift ownership is heading.'),
                  ('CONNECT', 'Back to classes: the most common cycles involve closures.'))))

# ================================================================== Part 5 (8-9)
divider(5, "Closures and timers", "Who owns the closure?", 'Lesson 1.4 met this cycle. Now ask the deeper question.', 'And add a timer.')
CL = """@MainActor
final class DashboardViewModel {
    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = { [weak self] in   // the fix
            self?.refresh()
        }
    }
    func refresh() { print("Refreshing dashboard") }
}"""
S.append(slide("Part 5 &middot; Closures (section 8)", "Ask three questions", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DashboardViewModel.swift", CL, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The cycle (Lesson 1.4)", ul("The ViewModel owns <code>onRefresh</code>", "<code>onRefresh</code> captured <code>self</code> strongly"))}
        <div class="rule step" data-label="Before you add [weak self]">{ul("<b>Who owns</b> the closure?", "<b>How long</b> does it live?", "<b>What</b> does it capture?")}</div>
        <div class="step">{card("No cycle", ul("Non-escaping closures run now: <code>map</code>, <code>filter</code>", "Owned by something that ends soon"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The cycle from Lesson 1.4: the ViewModel owns onRefresh, and the closure captured self strongly. The fix: capture self weakly, so the closure no longer retains the ViewModel.'),
                  ('SAY', 'Click: but weak capture is not required for every closure. Before adding it, ask three questions: who owns the closure, how long does it live, and what does it capture?'),
                  ('SAY', 'Click: a non-escaping closure that runs immediately, like map or filter, cannot form this cycle, and neither can a closure owned by something short-lived. Reflexive [weak self] everywhere adds noise and can hide real design problems.'),
                  ('CONNECT', 'Timers are a classic long-lived owner.'))))

TIMER = """@MainActor
final class DashboardController {
    var timer: Timer?

    func start() {
        timer = Timer.scheduledTimer(
            withTimeInterval: 1, repeats: true
        ) { [weak self] _ in
            self?.refresh()
        }
    }
    func refresh() { print("Refresh") }
    func stop() { timer?.invalidate(); timer = nil }
}"""
P = [box(0, 0, 250, 56, 'Run loop', 'keeps scheduled timers', None, '', 'clock'), wire('M254 28H296' + head(296, 28, 'r')),
     box(302, 0, 250, 56, 'Timer', 'owns the closure', None, '', 'clock'), wire('M427 60V86' + head(427, 86, 'd')),
     box(302, 92, 250, 56, 'Callback closure', 'weak self', None, '', 'code'),
     wire('M298 120H260' + head(260, 120, 'l'), None, 'dash'),
     box(0, 92, 250, 56, 'DashboardController', 'not kept alive', None, 'lit', 'layout')]
S.append(slide("Part 5 &middot; Timers (section 9)", "Weak capture and invalidate: two different jobs", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DashboardController.swift", TIMER, "font-size:13px")}
      <div>{svg('0 0 552 148', 'The run loop keeps the timer; the timer owns its closure; the closure captures the controller weakly', 'timer', P, 'max-height:170px')}
        <div class="gap"></div>
        <div class="cols step" style="gap:14px">{card("[weak self]", ul("Callback doesn&rsquo;t keep the <b>controller</b> alive"))}{card("invalidate()", ul("<b>Stops the timer</b>; the run loop lets go"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'A repeating timer owns its callback closure, and the run loop keeps a scheduled timer alive, as Lesson 0.6 showed. If the callback captured the controller strongly, the controller would live as long as the timer.'),
                  ('SAY', 'This version does two things. Click: weak self, so the callback does not keep the controller alive. And invalidate in stop, so the timer actually stops and the run loop releases it.'),
                  ('SAY', 'They address different concerns. Weak capture alone leaves a timer firing every second into a nil self; invalidate alone, with a strong capture, depends on stop being called. Do both.'),
                  ('CONNECT', 'How does this compare with garbage collection?'))))

# ================================================================== Part 6 (10-11)
divider(6, "ARC versus GC, and finding leaks", "What Java developers expect, and how to check", 'Java&rsquo;s collector would have freed our cycle. Swift&rsquo;s ARC does not.', 'Compare, then investigate.')
GC = [("How", "Counts ownership; frees when it ends", "Traces what is reachable"),
      ("When", "<b>Promptly</b>, when ownership ends", "When the collector runs"),
      ("Strong cycles", "<b>Stay alive</b>", "Usually reclaimed if unreachable"),
      ("Used by", "Swift class instances", "Java and many runtimes")]
S.append(slide("Part 6 &middot; ARC vs GC (section 10)", "Prompt and predictable, but cycles stay", f"""  <div class="body">
    {tbl(["", "ARC", "Tracing garbage collection"], GC, 'tbl')}
    <p class="small muted" style="margin:8px 0 0">Simplified; real systems add many optimizations.</p>
    <div class="gap"></div>
    <div class="warn step" data-label="Can Swift apps leak?">{ul("<b>Yes</b>: strong cycles and unintended long-lived references")}</div>
  </div>""", notes(('SAY', 'ARC manages lifetimes through ownership and can free an object promptly, the moment ownership ends. A tracing collector, as in Java, periodically finds what is still reachable, and its timing depends on the collector. The big practical difference: a strong cycle stays alive under ARC, while many tracing collectors reclaim unreachable cycles. ARC is used for Swift class instances.'),
                  ('SAY', 'This is simplified; both kinds of system use many optimizations.'),
                  ('SAY', 'Click: so, can a Swift app leak memory? Yes: strong-reference cycles and unintended long-lived references, like our screen that refused to die.'),
                  ('CONNECT', 'How do you find one?'))))

STEPS = ["Reproduce the suspected leak", "Navigate away from the screen", "Check whether expected objects deinitialize",
         "Inspect the <b>Memory Graph</b> (Xcode)", "Find unexpected strong-reference chains", "Correct the ownership", "Repeat and <b>verify</b>"]
lis = ''.join(f'<li>{x}</li>' for x in STEPS)
S.append(slide("Part 6 &middot; Investigating (section 11)", "Seven steps from suspicion to proof", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.1fr .9fr;gap:28px;align-items:start">
      <ol class="lab">{lis}</ol>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Tools", ul("<b>Memory Graph Debugger</b>: who holds this object?", "<b>Instruments</b>: Allocations, Leaks over time"))}
        <div class="rule step" data-label="Careful">{ul("A missing <code>deinit</code> is <b>not</b> proof of a leak", "Something may legitimately still own it")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A reliable process. Reproduce the suspected leak. Navigate away from the screen. Check whether the objects you expect to disappear actually deinitialize, our deinit prints and live counter. Inspect Xcode&rsquo;s Memory Graph to see who still holds them. Find the unexpected strong-reference chain. Correct the ownership. Then repeat the experiment and verify.'),
                  ('SAY', 'The Memory Graph Debugger answers who holds this object; Instruments shows allocations and leaks over time. Lesson 8.9 goes deep on Instruments.'),
                  ('SAY', 'Click: a missing deinit message alone does not prove a leak. The object may still be legitimately retained, by a cache, a navigation stack, or a task that has not finished, which is our last part.'),
                  ('CONNECT', 'The senior-engineer challenge.'))))

# ================================================================== Part 7 (12)
divider(7, "Async tasks and lifetimes", "When [weak self] is not enough", 'A ViewModel starts a long-running task. Does [weak self] solve the lifetime problem?', 'Not necessarily.')
TASK = """@MainActor
final class StatementViewModel {
    func startExport() {
        Task { [weak self] in
            guard let self else { return }           // strong from here on
            try? await Task.sleep(for: .seconds(2))  // long work
            self.finish()
        }
    }
    func finish() { print("export finished") }
    deinit { print("StatementViewModel deinit") }
}"""
P = [box(0, 0, 552, 46, 'Screen closes: vm = nil', 'the screen is gone', '1', '', 'phone'),
     box(0, 58, 552, 46, 'Task still holds self (guard let)', 'two more seconds of work', '2', '', 'clock'),
     box(0, 116, 552, 46, 'export finished, then deinit', 'only now is it freed', '3+', '', 'cross')]
S.append(slide("Part 7 &middot; Tasks (section 12)", "guard let self keeps it alive until the work ends", f"""  <div class="body">
    {cues(3)}
    <div class="cols" style="grid-template-columns:1.15fr .85fr;gap:24px;align-items:start">
      {code("StatementViewModel.swift", TASK, "font-size:13px")}
      <div>{svg('0 0 552 162', 'The screen closes; the task still holds self strongly for two more seconds; then export finishes and deinit runs', 'task', P, 'max-height:200px')}
        <div style="margin-top:12px">{card("Real output", mono("screen closed, vm = nil<br>export finished<br>StatementViewModel deinit", 14))}</div></div>
    </div>
    <div class="gap"></div>
    <div class="takeaway step">The real fix is <b>cancellation</b> and lifecycle design: Lesson 1.9.</div>
  </div>""", notes(('SAY', 'A statement export runs as a long task. It captures self weakly, which looks safe, then immediately promotes it: guard let self. From that line on, the task holds a strong reference for the whole long operation.'),
                  ('SAY', 'Click: the user closes the screen and the view model variable is set to nil. Click: but the task still holds self, so nothing is freed. Click: we ran it: export finished prints after the screen closed, and only then does deinit run.'),
                  ('SAY', 'So weak self alone does not always solve the lifetime problem. Click: the real fix is cancelling the task when the screen goes away, and designing the lifecycle; Lesson 1.9 covers tasks and cancellation, and Lesson 8.3 goes deeper.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.8', (), [("link", "Owners keep things alive", "nil releases a reference, not the object"),
                     ("diff", "weak or unowned", "nil safely, or trap"),
                     ("eye", "Prove it", "deinit, Memory Graph, verify the fix")],
         'Three things to remember. Strong references own: setting one to nil releases that reference, not necessarily the object, and ARC never breaks a cycle for you. weak becomes nil safely; unowned traps if its target is gone; ask who owns a closure before adding weak self, and remember a promoted self in a task lives until the task ends. And prove it: reproduce, check deinit, inspect the Memory Graph, fix ownership, verify.')

review_divider(8)
review([("link", "Question", "Does ARC automatically collect every strong-reference cycle?",
         "Does ARC automatically collect every strong-reference cycle?", "No",
         "ARC does not detect cycles. Customer and Account held each other: neither <code>deinit</code> ran.",
         "Assuming ARC behaves like a tracing GC.", "Java developers often say yes.", None),
        ("diff", "Question", "Does weak ownership keep an object alive?",
         "Does a <code>weak</code> reference keep its target alive?", "No",
         "It never owns; when the target is destroyed, the weak reference becomes <code>nil</code>.",
         "Thinking weak delays deallocation.", "Most say no.", None),
        ("code", "Question", "Should every closure capture self weakly?",
         "Should every closure capture <code>self</code> weakly?", "No",
         "Only when a cycle or unwanted long life is possible. Ask: who owns it, how long does it live, what does it capture?",
         "Reflexive [weak self] everywhere.", "Many say yes.", None),
        ("clock", "Question", "Can a timer retain its callback closure?",
         "Can a repeating timer retain its callback closure?", "Yes",
         "The timer owns its closure, and the run loop keeps the scheduled timer. Capture weakly and invalidate.",
         "Thinking timers are fire-and-forget.", "Most say yes.", None),
        ("eye", "Question", "Does a missing deinit always prove a leak?",
         "Does a missing <code>deinit</code> message always prove a leak?", "No",
         "Something may legitimately still own it: a cache, a navigation stack, an unfinished task.",
         "Treating every missing deinit as a bug.", "Some say yes.", None),
        ("memory", "Predict the output", "What prints when customerA is set to nil?",
         "<code>var customerA: Customer? = Customer(name: \"Meena\")</code><br><code>var customerB = customerA</code><br><code>customerA = nil</code><br>Does <code>deinit</code> print?", "No",
         "<code>customerB</code> still owns it. Only <code>customerB = nil</code> prints &ldquo;Meena destroyed&rdquo;.",
         "Thinking nil destroys the object.", "Many say yes.", None),
        ("cross", "Choose one", "What happens reading an unowned reference after its target is destroyed?",
         "An <code>unowned</code> reference is read after its target is destroyed. What happens?<br>A. It returns nil<br>B. It returns an empty object<br>C. The app traps<br>D. The compiler prevents it", "C",
         "&ldquo;Attempted to read an unowned reference but object &hellip; was already destroyed.&rdquo; Use <code>weak</code> if the target may go first.",
         "Expecting unowned to behave like weak.", "Some pick A.", None),
        ("layers", "Choose one", "Is a struct value managed by ARC like a class instance?",
         "Which of these is managed by ARC as an instance?<br>A. A struct value<br>B. A class instance<br>C. An Int<br>D. A tuple", "B",
         "ARC manages class instances (and closures, actors). Structs are values; class references inside them are still counted.",
         "Thinking everything is reference counted.", "Some pick A.", "Spaced review from Lesson 1.5.")])

S.append(next_slide('1.8', [("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "tasks, cancellation and lifetimes"),
                            ("8.3", "Task lifetimes &amp; cancellation", "the export task, done right"),
                            ("8.8", "Memory, ARC &amp; energy optimization", "reducing NPay&rsquo;s footprint"),
                            ("8.9", "Instruments &amp; measurement", "Allocations and Leaks in practice"),
                            ("9.7", "Xcode debugger, LLDB &amp; crash analysis", "the Memory Graph and crash logs")],
                    'Ownership runs into the next lessons. 1.9 introduces tasks and cancellation, which is the real fix for the export task; 8.3 goes deep on task lifetimes; 8.8 and 8.9 optimize and measure memory with Instruments; and 9.7 covers the debugger, the Memory Graph and crash analysis.'))

LAB = """@MainActor
final class TransactionViewModel {
    static var live = 0
    var onRefresh: (() -> Void)?
    init() { Self.live += 1; onRefresh = { self.load() } }
    func load() {}
    deinit { MainActor.assumeIsolated { Self.live -= 1 } }
}
// TODO: visit the screen 3 times; print TransactionViewModel.live"""
S.append(lab_slide('1.8', "Make it leak, then prove the fix", "Reproduce each problem from today, then fix it and verify with output.",
                   ["Run three visits; print the live count. Fix the capture; run again.",
                    "Build the Customer/Account cycle; make <code>owner</code> weak; confirm both <code>deinit</code>s.",
                    "Read an <code>unowned</code> reference after its target dies; read the trap.",
                    "Run the export task; add cancellation so <code>deinit</code> comes first."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab. Call MainActor-isolated code from top level with MainActor.assumeIsolated { … }. Expected: strong capture → live = 3 after three visits; [weak self] → 0. Cycle: nothing prints; with weak var owner → "Customer destroyed" and the account&rsquo;s owner is nil. unowned → "Fatal error: Attempted to read an unowned reference but object … was already destroyed". Export task: keep a reference to the Task (var exportTask: Task&lt;Void, Never&gt;?), cancel it in a close() method, and check Task.isCancelled (or use try await Task.sleep, which throws on cancellation) so the view model is freed immediately. Full cancellation patterns come in Lesson 1.9.',
                   side=f'<div>{code("lab.swift", LAB, "font-size:12px")}<div class="gap"></div>{card("You hand in", ul("Before and after output for each step"))}</div>'))

end_slide('1.8', 'ARC, Ownership<br>&amp; Memory Management', 'Lesson 1.9 &mdash; Swift Concurrency: Tasks, Actors &amp; Sendable',
          'You can now explain what ARC does and does not do, how strong references and cycles keep objects alive, when to use weak or unowned, how closures, timers and tasks extend lifetimes, how ARC differs from garbage collection, and how to investigate a suspected leak.',
          'Next, Lesson 1.9: Swift concurrency, with tasks, actors and Sendable, including the cancellation that properly fixes our export task.')

write_deck(OUT18, '1.8', 'ARC, Ownership &amp; Memory', 'ARC, Ownership &amp; Memory')
