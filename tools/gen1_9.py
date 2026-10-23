"""Generates decks/unit-1/lesson-1.9/index.html from the Lesson 1.9 text (PocketBank -> NPay).
The text stops inside Section 11; actors, MainActor and Sendable (requested with the text) are authored.
Sections are grouped into 8 Parts (see the lesson's "Deck changes")."""
import html, os, re, sys
OUT19 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'
tbl = lambda head_, rows, cls='tbl compact': f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head_) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'


def bar(x, y, w, label, sub, l=None, cls=''):
    return box(x, y, w, 44, label, sub, l, cls, '')


title_slide('1.9', 'Swift Concurrency:<br>Tasks, Actors &amp; Sendable',
            'How can NPay do <b>several things at once</b> without <b>freezing the UI</b> or <b>corrupting shared data</b>?',
            'Today, one of the most important areas of modern iOS engineering: Swift concurrency. It connects what we learned about threads and the run loop in Unit 00, SwiftUI, ARC and networking. The question: how can NPay perform several operations at once without freezing the interface or corrupting shared data? We build up step by step: async/await, tasks, structured concurrency, cancellation, actors and Sendable.')
outcomes_slide('1.9', [("clock", "Concurrency vs parallelism; <b>tasks vs threads</b>"),
                       ("code", "What <code>async</code>/<code>await</code> really do"),
                       ("layers", "<code>async let</code>, task groups, <b>structured</b> concurrency"),
                       ("cross", "<b>Cooperative cancellation</b> and SwiftUI&rsquo;s <code>.task</code>"),
                       ("lock", "<b>Data races</b>, and how <b>actors</b> prevent them"),
                       ("shield", "<code>@MainActor</code> and <b>Sendable</b>")])
where_slide('1.9', 'Today: concurrency, safely', (),
            'Lesson 1.8: ownership, cycles, and a task that kept its view model alive.',
            'Tasks, structured concurrency, cancellation, actors and Sendable.',
            'Last lesson ended with a task that kept its view model alive, and we said the real fix was cancellation. Lesson 1.6 made our service Sendable without fully explaining why. Today answers both, and connects back to the main thread and run loop from Lesson 0.5.',
            'Start with NPay&rsquo;s slow dashboard.')

# ================================================================== Part 1 (1-2)
divider(1, "The slow dashboard", "Concurrency versus parallelism", 'The dashboard needs three things from the bank. Done one after another, the user waits.', 'Measure it.')
P = ['<text class="mono" x="0" y="14">SEQUENTIAL (MEASURED: 6.2 s)</text>',
     bar(0, 26, 2 * 150, 'Balance', '2 s'), bar(300, 26, 3 * 150, 'Transactions', '3 s'), bar(750, 26, 150, 'Profile', '1 s'),
     fade('1+', '<text class="mono" x="0" y="104">CONCURRENT (MEASURED: 3.2 s)</text>'
          + bar(0, 116, 300, 'Balance', '2 s', None, 'lit') + bar(0, 166, 450, 'Transactions', '3 s', None, 'lit') + bar(0, 216, 150, 'Profile', '1 s', None, 'lit')),
     wire('M0 270H900', None, 'faint')]
for sec in range(7):
    P += [wire(f'M{sec * 150} 266V274', None, 'faint'), f'<text class="sm" x="{sec * 150}" y="290" text-anchor="middle">{sec} s</text>']
S.append(slide("Part 1 &middot; The problem (section 1)", "Three requests: one after another, or together", f"""  <div class="body">
    {svg('-10 0 920 292', 'Sequential: balance 2 s, transactions 3 s, profile 1 s, about 6 seconds. Concurrent: all three overlap, about 3 seconds', 'dash', P, 'max-height:330px')}
    {cues(1)}
    <div class="gap"></div>
    <div class="takeaway step">Independent work can <b>overlap</b>: total &asymp; the <b>slowest</b> request, not the sum.</div>
  </div>""", notes(('SAY', 'NPay&rsquo;s dashboard needs the balance, about 2 seconds, recent transactions, about 3, and the profile, about 1. Illustrative durations. One after another, the user waits for all three: we measured 6.2 seconds with simulated delays.'),
                  ('SAY', 'Click: the three requests are independent, so they can run concurrently. Measured: 3.2 seconds, about the slowest one.'),
                  ('SAY', 'Click: when independent work overlaps, the total is roughly the slowest operation, not the sum. Real networks and servers vary, of course.'),
                  ('CONNECT', 'Two words to get right first: concurrency and parallelism.'))))

P = ['<text class="mono" x="0" y="14">CONCURRENCY &middot; ONE CHEF, TWO DISHES</text>']
for i, t in enumerate('ABABAB'):
    P.append(box(i * 92, 26, 84, 44, t, '', None, 'lit' if t == 'A' else '', ''))
P.append('<text class="mono" x="600" y="14">PARALLELISM &middot; TWO CHEFS</text>')
P += [box(600, 26, 536, 44, 'A A A', 'chef 1', None, 'lit', ''), box(600, 80, 536, 44, 'B B B', 'chef 2', None, '', '')]
S.append(slide("Part 1 &middot; Two words (section 2)", "Taking turns, or truly at once", f"""  <div class="body">
    {svg('0 0 1136 124', 'Concurrency: one chef alternates A and B. Parallelism: two chefs work on A and B at the same time', 'cp', P, 'max-height:150px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("Concurrency", ul("Tasks make progress in <b>overlapping</b> periods", "They may <b>take turns</b> on one resource"))}
      {card("Parallelism", ul("Computations run at the <b>same instant</b>", "Needs several cores"))}
    </div>
    <div class="gap"></div>
    <div class="tip step" data-label="Swift Concurrency">{ul("<b>Organizes</b> concurrent work; parallel or not depends on scheduling, isolation and cores")}</div>
  </div>""", notes(('SAY', 'Concurrency means several tasks make progress during overlapping periods; they may take turns. Parallelism means computations really run at the same instant, on different cores. Back to our restaurant kitchen: one chef alternating between two dishes while one simmers is concurrency; two chefs each cooking a dish is parallelism.'),
                  ('SAY', 'Click: Swift Concurrency is a way to organize concurrent work safely. Whether any of it actually runs in parallel depends on scheduling, isolation and the cores available.'),
                  ('CONNECT', 'The most important distinction of the day: tasks versus threads.'))))

# ================================================================== Part 2 (3-4)
divider(2, "Tasks, threads, async/await", "Suspend, don&rsquo;t block", 'A task is not a thread. That one fact explains most of Swift concurrency.', 'Prove it.')
P = [box(0, 0, 260, 50, 'Task A runs', 'on a thread', '1', '', 'play'), wire('M264 25H294' + head(294, 25, 'r')),
     box(300, 0, 260, 50, 'Task A reaches await', 'suspends', '2', '', 'clock'), wire('M564 25H594' + head(594, 25, 'r')),
     box(600, 0, 260, 50, 'Thread runs other work', 'not blocked', '3', '', 'thread'), wire('M864 25H894' + head(894, 25, 'r')),
     box(900, 0, 236, 50, 'Task A resumes', 'maybe another thread', '4+', '', 'play')]
S.append(slide("Part 2 &middot; Tasks vs threads (section 3)", "A task is work; a thread is a worker", f"""  <div class="body">
    {svg('0 0 1136 50', 'Task A runs, reaches await and suspends; the thread runs other work; task A later resumes, possibly on another thread', 'tvt', P, 'max-height:70px')}
    {cues(4)}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Thread", ul("An <b>OS</b> execution resource with its own stack", "Expensive; few of them"))}
        {card("Task", ul("A <b>language</b> unit of async work", "Suspends; resumes on an appropriate executor"))}
      </div>
      <div class="step">{card("Measured on this Mac (18 cores)", mono("10,000 tasks, each waiting 1 s<br>&rarr; all finished in 1.08 s", 17) + ul("Not 10,000 threads: waiting tasks <b>free</b> their thread"))}
        <div class="gap"></div>
        <div class="rule" data-label="Never teach">{ul("<code>Task {}</code> &ne; a new thread")}</div></div>
    </div>
  </div>""", notes(('SAY', 'A thread is an operating-system execution resource with its own stack, scheduled by the OS; threads are expensive and there are few. A Swift task is a language-level unit of asynchronous work that can suspend and resume on an appropriate executor. It is not tied to one thread.'),
                  ('SAY', 'Click through: task A runs; it reaches an await and suspends; the thread is free to run other work; later task A resumes, possibly on a different thread.'),
                  ('SAY', 'Click: we measured it. Ten thousand tasks, each waiting one second with Task.sleep, all finished in 1.08 seconds on this 18-core Mac. That is impossible with one thread per task: waiting tasks give their thread back. So never teach Task {} as creating a new thread.'),
                  ('CONNECT', 'That is what async and await are for.'))))

FB = """func fetchBalance() async throws -> Int64 {
    try await Task.sleep(for: .seconds(2))   // stands in for the network
    return 2_500_000
}"""
KW = [("<code>async</code>", "the function can <b>suspend</b>"), ("<code>await</code>", "a <b>possible</b> suspension point"),
      ("<code>throws</code>", "the function can fail"), ("<code>try</code>", "acknowledges a possible error")]
S.append(slide("Part 2 &middot; async/await (section 4)", "Wait without holding the thread", f"""  <div class="body">
    {code("FetchBalance.swift", FB, "font-size:16px")}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {tbl(["Keyword", "Means"], KW, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Why it exists", ul("A network call is mostly <b>waiting</b>", "Blocking wastes a thread; suspending frees it"))}
        <div class="rule step" data-label="await">{ul("Marks where code <b>may</b> suspend, not that it will")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A network request is mostly waiting for the server; the CPU has nothing to do for it. Synchronous code would block a thread for that whole time. An async function lets the calling task suspend instead. Task.sleep stands in for the network here; the balance is paise, as always.'),
                  ('SAY', 'async: the function can suspend. await: a possible suspension point. throws and try: it can fail, as in Lesson 1.7.'),
                  ('SAY', 'Click: await does not mean a delay or a network call is happening. It marks a call that may suspend; it might complete immediately.'),
                  ('CONNECT', 'So how does that keep NPay&rsquo;s screen responsive?'))))

# ================================================================== Part 3 (5)
divider(3, "Keeping the UI responsive", "Suspension versus blocking", 'A button starts the work. What happens to the main thread while it waits?', 'Compare suspending and blocking.')
BTN = """Button("Refresh balance") {
    Task {
        do {
            let balanceMinor = try await fetchBalance()
            print(balanceMinor)
        } catch {
            print(error)
        }
    }
}"""
S.append(slide("Part 3 &middot; Responsive UI (section 5)", "Suspending frees the thread; blocking holds it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("RefreshButton.swift", BTN, "font-size:14px")}
        <div style="margin-top:12px">{card("While it waits", ul("The task <b>suspends</b> at <code>await</code>", "The main thread keeps handling taps and frames (0.5)"))}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Measured: 40 tasks, each BLOCKING 1 s", mono("&rarr; 3.0 s on 18 cores", 17) + ul("Blocked tasks <b>hold</b> pool threads: about 40 &divide; 18 rounds"))}</div>
        <div class="step">{card("Swift 6 even refuses it", '<p style="margin:4px 0 0">' + err("class method &lsquo;sleep&rsquo; is unavailable from asynchronous contexts") + '</p>')}</div>
        <div class="warn step" data-label="async is not magic">{ul("Heavy synchronous work inside an async function still <b>blocks</b> its thread")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The Refresh balance button creates a task, and the task awaits fetchBalance. While it waits, the task is suspended, and the main thread is free to handle taps and draw frames, exactly the run loop behaviour from Lesson 0.5.'),
                  ('SAY', 'Click: compare blocking. We ran 40 tasks that each block their thread for one second with Thread.sleep: 3.0 seconds on 18 cores, because blocked tasks hold the pool&rsquo;s threads. Ten thousand suspending tasks took one second.'),
                  ('SAY', 'Click: Swift 6 actually refuses Thread.sleep directly inside async code: class method sleep is unavailable from asynchronous contexts. We had to hide it inside a synchronous helper to measure it.'),
                  ('SAY', 'Click: async does not make CPU-heavy work safe. A long synchronous loop inside an async function still blocks whatever thread it runs on; if that is the main actor, the UI freezes. Lesson 8.7 covers hangs.'),
                  ('CONNECT', 'Back to the dashboard: how do we start three requests at once?'))))

# ================================================================== Part 4 (6-7)
divider(4, "async let and structure", "Start together, finish together", 'Sequential awaits wait for each other. async let does not.', 'Two versions.')
SEQ = """let balance      = try await fetchBalance()
let transactions = try await fetchTransactions()
let profile      = try await fetchProfile()
// measured: 6.2 s"""
CON = """async let balance      = fetchBalance()
async let transactions = fetchTransactions()
async let profile      = fetchProfile()

let dashboard = try await (balance, transactions, profile)
// measured: 3.2 s"""
S.append(slide("Part 4 &middot; async let (section 6)", "Three awaits, or three child tasks", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Sequential.swift", SEQ, "font-size:14px;min-height:190px")}
        <div style="margin-top:12px">{card("Sequential", ul("Each call starts after the previous one <b>finishes</b>", "Total &asymp; <b>sum</b>: 2 + 3 + 1"))}</div></div>
      <div class="step">{code("Concurrent.swift", CON, "font-size:14px;min-height:190px")}
        <div style="margin-top:12px">{card("async let", ul("Each starts a <b>child task</b> immediately", "Total &asymp; the <b>slowest</b>: 3 s"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Sequential awaits: the transactions call starts only after the balance arrives, and the profile only after that. Measured 6.2 seconds.'),
                  ('SAY', 'Click: async let starts each call as a child task immediately and keeps going. The single try await on the tuple waits for all three. Measured 3.2 seconds: the slowest request, because they overlap. Only do this when the requests are independent.'),
                  ('CONNECT', 'Those child tasks have a parent. That is structured concurrency.'))))

P = [box(318, 0, 500, 56, 'Parent task: load dashboard', 'owns its children', None, 'lit', 'layers'),
     wire('M450 60L190 96' + head(190, 96, 'd')), wire('M568 60V96' + head(568, 96, 'd')), wire('M686 60L946 96' + head(946, 96, 'd')),
     box(60, 102, 260, 50, 'Balance', 'child', None, '', 'bank'), box(438, 102, 260, 50, 'Transactions', 'child', None, '', 'file'),
     box(816, 102, 260, 50, 'Profile', 'child', None, '', 'user'),
     wire('M190 156L450 196' + head(450, 196, 'd'), None, 'dash'), wire('M568 156V196' + head(568, 196, 'd'), None, 'dash'), wire('M946 156L686 196' + head(686, 196, 'd'), None, 'dash'),
     box(318, 202, 500, 50, 'Scope ends only after all children finish', '', None, '', 'check')]
S.append(slide("Part 4 &middot; Structured concurrency (section 7)", "Children belong to a parent scope", f"""  <div class="body">
    {svg('0 0 1136 252', 'A parent task owns three child tasks; its scope ends only after all children finish', 'tree', P, 'max-height:270px')}
    <div class="gap"></div>
    <div class="cols step" style="grid-template-columns:repeat(3,1fr);gap:18px">
      {card("Lifetime", ul("No child is <b>abandoned</b>"))}
      {card("Errors", ul("A child&rsquo;s error reaches the parent"))}
      {card("Cancellation", ul("Cancel the parent: children are cancelled"))}
    </div>
  </div>""", notes(('SAY', 'Structured concurrency: child tasks belong to a defined parent scope. The dashboard task owns the balance, transactions and profile children, and its scope cannot end until all three have finished.'),
                  ('SAY', 'Click: that structure gives three guarantees. Lifetime: a parent cannot abandon unfinished children when it leaves the scope. Errors: a child&rsquo;s thrown error propagates to the parent. Cancellation: cancelling the parent cancels its children.'),
                  ('SAY', 'Compare a loose Task {} with no owner, like the export task in Lesson 1.8: nobody waits for it, nobody cancels it. Prefer structure; Lesson 8.2 goes deeper.'),
                  ('CONNECT', 'What if the number of requests is not known in advance?'))))

# ================================================================== Part 5 (8)
divider(5, "Task groups", "Dynamic concurrency", 'Fetch balances for however many accounts the customer has.', 'withThrowingTaskGroup.')
GRP = """func fetchAllBalances(accountIds: [String]) async throws -> [(String, Int64)] {
    try await withThrowingTaskGroup(of: (String, Int64).self) { group in
        for id in accountIds {
            group.addTask { (id, try await fetchBalance(for: id)) }
        }
        var results: [(String, Int64)] = []
        for try await result in group { results.append(result) }
        return results
    }
}"""
ORD = [("Added", "<code>NP1001</code>, <code>NP1002</code>, <code>NP1003</code>"), ("Took", "3 s, 1 s, 2 s"),
       ("Returned", "<b><code>NP1002</code>, <code>NP1003</code>, <code>NP1001</code></b>")]
S.append(slide("Part 5 &middot; Task groups (section 8)", "One child per account, results as they finish", f"""  <div class="body">
    {code("FetchAllBalances.swift", GRP, "font-size:13px")}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div class="step"><p class="small muted" style="margin:0 0 6px">Real run:</p>{tbl(["", ""], ORD)}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Completion order", ul("Results come back as tasks <b>finish</b>", "Need order? Return the <b>id</b> with each result"))}</div>
        <div class="warn step" data-label="Thousands at once?">{ul("No: limits, rate limits, back-pressure (8.6)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'async let suits a fixed number of operations. For a dynamic list, like every account a customer holds, use a task group: one child task per account id, then collect results with for try await. Each result carries its account id.'),
                  ('SAY', 'Click: we ran it with three accounts that take 3, 1 and 2 seconds. Added in order NP1001, NP1002, NP1003; returned NP1002, NP1003, NP1001.'),
                  ('SAY', 'Click: task-group results arrive in completion order, not the order you added them. If order matters, return an identifier with each result, as we did, and rebuild the order.'),
                  ('SAY', 'Click: should we launch thousands of requests at once? No: real systems need concurrency limits, server rate limits, resource management and back-pressure. Lesson 8.6 covers that.'),
                  ('CONNECT', 'What if the user leaves before the work is done?'))))

# ================================================================== Part 6 (9-10)
divider(6, "Cancellation and .task", "Stop work nobody needs", 'The user leaves the transaction history before it loads. Keep going?', 'Not necessarily.')
CAN = """func loadTransactions() async throws {
    try Task.checkCancellation()
    let transactions = try await fetchTransactions()
    try Task.checkCancellation()
    print(transactions)
}

let task = Task { try await loadTransactions() }
task.cancel()       // 0.2 s later, in the real run"""
S.append(slide("Part 6 &middot; Cancellation (section 9)", "Cancellation is cooperative", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("LoadTransactions.swift", CAN, "font-size:14px")}
        <div style="margin-top:12px" class="step">{card("Real run", mono("stopped: CancellationError"))}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("cancel()", ul("Sets a <b>flag</b> on the task", "Does <b>not</b> stop it by force"))}
        <div class="step">{card("Who responds", ul("<code>Task.checkCancellation()</code> throws", "<code>Task.sleep</code>, <code>URLSession</code> throw on cancel", "Your loops check <code>Task.isCancelled</code>"))}</div>
        <div class="rule step" data-label="Key principle">{ul("Synchronous code keeps running until it <b>checks</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Swift tasks support cooperative cancellation. loadTransactions checks before and after the network call; Task.checkCancellation throws CancellationError if the task has been cancelled.'),
                  ('SAY', 'Click: real run: we cancelled the task 0.2 seconds in, while it was waiting; it stopped with CancellationError.'),
                  ('SAY', 'Click: cancel only sets a flag. Things that respond: checkCancellation, and asynchronous APIs like Task.sleep and URLSession, which throw when cancelled. Your own long loops must check Task.isCancelled.'),
                  ('SAY', 'Click: requesting cancellation never forcibly stops arbitrary synchronous code. This is the fix for Lesson 1.8&rsquo;s export task: keep the task, cancel it when the screen closes.'),
                  ('CONNECT', 'SwiftUI can cancel for you.'))))

TV = """struct TransactionHistoryView: View {
    var body: some View {
        Text("Transactions")
            .task {
                await loadTransactions()
            }
    }

    func loadTransactions() async {
        // load, checking for cancellation
    }
}"""
P = [box(0, 0, 250, 52, 'View appears', '', '1', '', 'phone'), wire('M254 26H286' + head(286, 26, 'r')),
     box(292, 0, 250, 52, '.task starts', 'tied to the view', '2', '', 'play'), wire('M546 26H578' + head(578, 26, 'r')),
     box(584, 0, 250, 52, 'View disappears', '.task is cancelled', '3+', '', 'cross')]
S.append(slide("Part 6 &middot; SwiftUI .task (section 10)", "Work that lives and dies with the view", f"""  <div class="body">
    {svg('0 0 834 52', 'The view appears, .task starts, the view disappears and the task is cancelled', 'task', P, 'max-height:66px')}
    {cues(3)}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("TransactionHistoryView.swift", TV, "font-size:14px")}
      <div class="step" style="display:flex;flex-direction:column;gap:14px">
        {card("Why prefer it", ul("SwiftUI <b>owns</b> the task&rsquo;s lifetime", "No loose, long-lived <code>Task {}</code>"))}
        <div class="rule" data-label="Still cooperative">{ul("Your code and its APIs must respond to cancellation")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI&rsquo;s .task modifier starts async work tied to the view. Click: the view appears. Click: the task starts. Click: when the view disappears, SwiftUI cancels the task.'),
                  ('SAY', 'Click: that is usually better than creating a long-lived unstructured task with no clear owner. But cancellation is still cooperative: your code and the APIs it calls must respond. Unit 03 uses .task throughout.'),
                  ('CONNECT', 'Now the danger concurrency brings: two tasks, one balance.'))))

# ================================================================== Part 7 (11 + authored actors)
divider(7, "Data races and actors", "Two tasks, one balance", 'Concurrency lets tasks overlap. What if they touch the same data?', 'Lose an update.')
P = [box(380, 0, 376, 50, 'Stored balance: ₹25,000', '', None, '', 'bank'),
     box(0, 80, 360, 50, 'Task A reads ₹25,000', 'adds ₹5,000 → ₹30,000', '1+', '', 'play'),
     box(776, 80, 360, 50, 'Task B reads ₹25,000', 'subtracts ₹3,000 → ₹22,000', '1+', '', 'play'),
     wire('M380 25H180V76' + head(180, 76, 'd'), '1+'), wire('M756 25H956V76' + head(956, 76, 'd'), '1+'),
     fade('2+', wire('M180 134V160H560' + head(560, 160, 'r'), None, 'dash') + '<text class="sm" x="370" y="152" text-anchor="middle">writes ₹30,000</text>'),
     fade('3+', wire('M956 134V160H576' + head(576, 160, 'l'), None, 'dash') + '<text class="sm" x="766" y="152" text-anchor="middle">then writes ₹22,000</text>'),
     fade('3+', box(380, 172, 376, 50, 'Stored: ₹22,000', 'should be ₹27,000: A&rsquo;s deposit is lost', None, 'alert', 'cross'))]
S.append(slide("Part 7 &middot; Data race (section 11)", "The lost update", f"""  <div class="body">
    {svg('0 0 1136 222', 'Both tasks read 25,000; task A writes 30,000, then task B writes 22,000; the deposit is lost', 'race', P, 'max-height:250px')}
    {cues(3)}
    <div class="gap"></div>
    <div class="step">{card("Measured: 1,000 concurrent ₹1 deposits, no protection", mono("expected &#8377;26,000 &middot; got &#8377;25,598, then &#8377;25,578 (one run was right)", 16))}</div>
  </div>""", notes(('SAY', 'Two tasks update the same balance at the same time. Click: both read ₹25,000. Task A will add ₹5,000; task B will subtract ₹3,000.'),
                  ('SAY', 'Click: task A writes ₹30,000. Click: then task B writes ₹22,000, computed from the old value. The stored balance should be ₹27,000; task A&rsquo;s deposit is simply lost. That is a lost update, one kind of data race.'),
                  ('SAY', 'Click: it really happens. We ran 1,000 concurrent one-rupee deposits on unprotected state. Expected ₹26,000; we got ₹25,598 and ₹25,578 on two runs, and the right answer once. Correct sometimes is the worst kind of bug.'),
                  ('CONNECT', 'Swift 6 has two answers: the compiler, and actors.'))))

ACT = """actor Account {
    private(set) var balanceMinor: Int64 = 2_500_000

    func deposit(_ amountMinor: Int64) {
        balanceMinor += amountMinor          // one caller at a time
    }
}

let account = Account()
await withTaskGroup(of: Void.self) { group in
    for _ in 0..<1000 { group.addTask { await account.deposit(100) } }
}
print(await account.balanceMinor)            // 2600000, every run"""
S.append(slide("Part 7 &middot; Actors (authored)", "An actor lets one task in at a time", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.2fr .8fr;gap:24px;align-items:start">
      {code("Account.swift", ACT, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Swift 6 catches the unsafe version", '<p style="margin:4px 0 0">' + err("passing closure as a &lsquo;sending&rsquo; parameter risks causing data races&hellip;") + '</p>')}
        <div class="step">{card("actor", ul("Protects its own state: <b>one task at a time</b>", "Outside callers must <code>await</code>", "Same 1,000 deposits: <b>&#8377;26,000 every run</b>"))}</div>
        <div class="tip step" data-label="Reentrancy">{ul("At an <code>await</code> inside an actor, other calls may run (8.4)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Beyond the lesson text, which stopped here, as you asked for actors. First, Swift 6 refuses to compile the unsafe version: share a plain class balance between two child tasks and you get passing closure as a sending parameter risks causing data races. A global var gets a similar error. We had to opt out deliberately to measure the race.'),
                  ('SAY', 'Click: the fix is an actor. An actor protects its own mutable state by letting one task in at a time. Code outside must await to call it, because it may have to wait its turn. The same thousand deposits: ₹26,000 on every run.'),
                  ('SAY', 'Click: one subtlety, from Lesson 0.5: actors are reentrant. If an actor method awaits, other calls can run in between, so state may change across the await. Lesson 8.4 covers reentrancy; Lesson 1.10 builds NPay&rsquo;s ledger as an actor.'),
                  ('CONNECT', 'One special actor runs the UI.'))))

# ================================================================== Part 8 (authored)
divider(8, "MainActor and Sendable", "The UI&rsquo;s actor, and safe-to-share types", 'Two more pieces complete the picture: where UI code runs, and what may cross between tasks.', 'MainActor first.')
VM = """@MainActor @Observable
final class DashboardViewModel {
    var balanceText = "—"

    func refresh() async {
        do {
            let minor = try await fetchBalance()  // elsewhere
            balanceText = "₹\\(minor / 100)"        // main actor
        } catch {
            balanceText = "Balance unavailable"
        }
    }
}"""
S.append(slide("Part 8 &middot; MainActor (authored)", "The main actor owns the UI", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.15fr .85fr;gap:24px;align-items:start">
      {code("DashboardViewModel.swift", VM, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("@MainActor", ul("A global actor: the <b>main thread</b> (0.5)", "All of the ViewModel runs there", "Safe to update what SwiftUI shows"))}
        <div class="step">{card("From outside, without await", '<p style="margin:4px 0 0">' + err("main actor-isolated property &lsquo;balanceText&rsquo; can not be mutated from a nonisolated context") + '</p>')}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The main actor is a global actor for the main thread from Lesson 0.5. Marking the ViewModel @MainActor, the course canon since Unit 00, puts all of it there, so updating what SwiftUI shows is always safe.'),
                  ('SAY', 'refresh awaits fetchBalance, which may run elsewhere; when it returns, the code is back on the main actor and sets balanceText. The compiler handles the hop.'),
                  ('SAY', 'Click: try to set balanceText from a nonisolated function without awaiting and the compiler refuses: main actor-isolated property balanceText can not be mutated from a nonisolated context. UI updates from the wrong thread become a build error, not a crash.'),
                  ('CONNECT', 'Last: what is allowed to cross between actors and tasks.'))))

SEND = [("Value types of Sendable parts", "<code>struct Balance { let balanceMinor: Int64 }</code>", "copies can&rsquo;t race"),
        ("Actors", "<code>actor Account</code>", "protect their own state"),
        ("Immutable final classes", "<code>final class</code> with only <code>let</code> Sendable properties", "nothing to race on"),
        ("Not Sendable", "a class with <code>var</code> state", "the compiler stops it crossing")]
S.append(slide("Part 8 &middot; Sendable (authored)", "Sendable: safe to share across tasks", f"""  <div class="body">
    {tbl(["Kind", "Example", "Why"], SEND, 'tbl')}
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px;align-items:start">
      {card("Lesson 1.6, explained", ul("The ViewModel is on the <b>main actor</b>", "<code>fetchBalance()</code> ran <b>off</b> it", "So the service had to be <code>Sendable</code>"))}
      {card("The rule", ul("Values that cross an isolation boundary must be <b>Sendable</b>", "Swift 6 checks it at compile time (8.5)"))}
    </div>
  </div>""", notes(('SAY', 'Sendable marks types that are safe to share between concurrency domains, between tasks and actors. Value types made of Sendable parts, like our Balance struct, are Sendable: every task gets its own copy. Actors are Sendable because they protect their own state. Immutable final classes can be. A class with mutable var state is not, and the compiler will not let it cross.'),
                  ('SAY', 'Click: this explains Lesson 1.6. The DashboardViewModel lives on the main actor; its service&rsquo;s async method ran off the main actor; so the service crossed a boundary and had to be Sendable. The rule: anything that crosses an isolation boundary must be Sendable, and Swift 6 checks it when you build. Lesson 8.5 goes deeper into strict concurrency checking.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== recap
recap_u1('1.9', (), [("clock", "Tasks suspend; threads don&rsquo;t", "await frees the thread"),
                     ("layers", "Structure your work", "async let, groups, cancellation"),
                     ("lock", "Isolate shared state", "actors, @MainActor, Sendable")],
         'Three things to remember. A task is not a thread: at an await it suspends and frees its thread, which is how ten thousand waits finished in a second, while blocking work holds threads hostage. Structure your work: async let and task groups make child tasks with a parent, errors and cancellation flow through that structure, and cancellation is cooperative. And isolate shared state: actors prevent lost updates, the main actor owns the UI, and Sendable decides what may cross between them, all checked by the Swift 6 compiler.')

review_divider(8)
review([("thread", "Question", "Does Task {} create a new thread?",
         "Does <code>Task { &hellip; }</code> create a new operating-system thread?", "No",
         "It creates a unit of work that runs on a shared pool and frees its thread whenever it suspends: 10,000 waiting tasks finished in about a second.",
         "Equating tasks with threads.", "Many say yes.", None),
        ("clock", "Choose one", "How long do three independent requests of 2 s, 3 s and 1 s take with async let?",
         "Three independent requests take 2 s, 3 s and 1 s. With <code>async let</code>, the total is about:<br>A. 6 s<br>B. 3 s<br>C. 1 s<br>D. 2 s", "B",
         "They overlap, so the total is roughly the slowest: measured 3.2 s (sequential: 6.2 s).",
         "Adding the durations.", "Some pick A.", None),
        ("layers", "Predict the output", "In what order does the task group return NP1001 (3 s), NP1002 (1 s), NP1003 (2 s)?",
         "A task group adds <code>NP1001</code> (3 s), <code>NP1002</code> (1 s), <code>NP1003</code> (2 s). In what order do results arrive?", "1002, 1003, 1001",
         "Completion order, not the order added. Return an id with each result if order matters.",
         "Expecting insertion order.", "Most say 1001, 1002, 1003.", None),
        ("cross", "Choose one", "What does task.cancel() do?",
         "What does <code>task.cancel()</code> do?<br>A. Kills the thread immediately<br>B. Sets a flag; code and APIs must respond<br>C. Throws inside any running code<br>D. Nothing for async tasks", "B",
         "Cancellation is cooperative: <code>checkCancellation</code>, <code>Task.sleep</code> and <code>URLSession</code> respond; plain synchronous loops keep running.",
         "Expecting forced termination.", "Some pick A.", None),
        ("code", "Question", "Does async make CPU-heavy work safe for the UI?",
         "Does marking a function <code>async</code> make CPU-heavy work inside it safe for the UI?", "No",
         "Synchronous work still blocks the thread it runs on; on the main actor, the UI freezes.",
         "Treating async as &ldquo;runs in the background&rdquo;.", "Many say yes.", None),
        ("lock", "Choose one", "Which prevents the lost update on NPay's balance?",
         "Which prevents the lost update when many tasks deposit into one balance?<br>A. Using <code>Int64</code> instead of <code>Int</code><br>B. An <code>actor</code> that owns the balance<br>C. <code>async let</code><br>D. <code>[weak self]</code>", "B",
         "The actor lets one task in at a time: 1,000 deposits gave exactly &#8377;26,000 every run.",
         "Thinking types or syntax fix races.", "Some pick C.", None),
        ("shield", "Question", "Can a nonisolated function set a @MainActor property directly?",
         "Can a nonisolated function set <code>DashboardViewModel.balanceText</code> (a <code>@MainActor</code> class) without <code>await</code>?", "No",
         "&ldquo;Main actor-isolated property &lsquo;balanceText&rsquo; can not be mutated from a nonisolated context.&rdquo;",
         "Expecting a runtime warning instead.", "Some say yes.", None),
        ("memory", "Question", "Does guard let self keep a view model alive during a long task?",
         "A task captures <code>[weak self]</code>, then does <code>guard let self</code> before a long <code>await</code>. Does that keep the view model alive until the task ends?", "Yes",
         "The strong <code>self</code> lives for the rest of the task. Cancellation is the real fix.",
         "Thinking weak capture alone guarantees release.", "Most say no.", "Spaced review from Lesson 1.8.")])

S.append(next_slide('1.9', [("1.10", "NPay domain model, actor ledger &amp; tests", "the ledger as an <code>actor</code>"),
                            ("8.1", "Executors &amp; actor isolation", "where code runs, <code>@concurrent</code>"),
                            ("8.2", "Structured concurrency deep dive", "groups, priorities, errors"),
                            ("8.3", "Task lifetimes &amp; cancellation", "owning and cancelling tasks"),
                            ("8.4", "Actor reentrancy &amp; logical races", "state across <code>await</code>"),
                            ("8.5", "Sendable &amp; strict concurrency checking", "every compiler error from today")],
                    'Concurrency continues straight into 1.10, where NPay&rsquo;s ledger becomes an actor with tests, and then Unit 08: executors and isolation, structured concurrency in depth, task lifetimes and cancellation, actor reentrancy, and strict Sendable checking.'))

LAB = """func fetchBalance() async throws -> Int64 {
    try await Task.sleep(for: .seconds(2)); return 2_500_000
}
// TODO fetchTransactions (3 s), fetchProfile (1 s)
let clock = ContinuousClock(); let start = clock.now
// 1. sequential, then async let: print clock.now - start
// 2. task group over 3 account ids: print the order
// 3. cancel a task after 0.2 s: print the error
// 4. actor Account: 1,000 deposits of 100 paise"""
S.append(lab_slide('1.9', "Measure NPay&rsquo;s dashboard", "Turn each claim from today into a number you measured yourself.",
                   ["Time sequential awaits, then <code>async let</code>.",
                    "Run a task group; record the completion order.",
                    "Cancel a task mid-wait; print the error type.",
                    "Make 1,000 concurrent deposits into an <code>actor</code>; check the total."],
                   "", 'Swift only: swiftc lab.swift -o lab && ./lab (top-level await is allowed in main.swift). Expected: sequential ≈ 6 s, async let ≈ 3 s; group order by duration (1 s, 2 s, 3 s first); cancellation prints CancellationError; actor total 2600000 paise (₹26,000) every run. Stretch: write the unprotected version and read Swift 6&rsquo;s error; only with nonisolated(unsafe) does it compile, and then totals vary (lost updates). Do not ship nonisolated(unsafe).',
                   side=f'<div>{code("lab.swift", LAB, "font-size:12px")}<div class="gap"></div>{card("You hand in", ul("Four measured results, with your explanation"))}</div>'))

end_slide('1.9', 'Swift Concurrency:<br>Tasks, Actors &amp; Sendable', 'Lesson 1.10 &mdash; NPay Domain Model, Actor Ledger &amp; Tests',
          'You can now explain concurrency versus parallelism and tasks versus threads, use async/await, async let and task groups within structured concurrency, cancel work cooperatively, recognise a data race, and prevent it with actors, @MainActor and Sendable.',
          'Next, Lesson 1.10, the end of Unit 01: NPay&rsquo;s domain model as a Swift package, with a Money type, an actor-based ledger, and tests.')

write_deck(OUT19, '1.9', 'Swift Concurrency', 'Swift Concurrency')
