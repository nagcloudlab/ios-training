"""Generates decks/lesson-0.5/index.html from the Lesson 0.5 text only."""
import html, re, sys
OUT05 = sys.argv[1]
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


def stepper(items, top, chip_w, gap, label, tid, title):
    """Row of chips lit one per click; below, the matching detail (title + description)."""
    P = []
    for i, (chip, *_r) in enumerate(items):
        P.append(row(i * (chip_w + gap), 0, chip_w, 52, '', chip, '', str(i)))
    for i, (_c, t, d) in enumerate(items):
        P.append(f'<g class="fade" data-lit="{i}"><text class="mono" x="0" y="{top}">{label} {i + 1} OF {len(items)}</text>'
                 f'<text x="0" y="{top + 36}" style="font-size:26px;font-weight:700">{t}</text>'
                 f'<text x="0" y="{top + 70}" style="font-size:19px;font-weight:400">{d}</text></g>')
    return svg(f"0 0 1136 {top + 84}", title, tid, P)


# ------------------------------------------------------------------ title + outcomes
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.5</p>
    <h1 style="font-size:54px;line-height:1.05">Main Thread, RunLoop<br>&amp; Event Handling</h1>
    <p class="lead" style="max-width:680px">When a user taps a button, how does that touch become Swift code, and how does the screen change?</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'Today: when a user taps a button on an iPhone, how does that touch become Swift code, and how does the screen change? This lesson connects operating systems, threads, event loops, SwiftUI, rendering and concurrency.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")
outs = [("thread", "The <b>main thread</b> handles critical UI work"), ("clock", "A <b>RunLoop</b> supports event-driven execution"),
        ("tap", "How a <b>touch</b> reaches your Swift code"), ("eye", "How SwiftUI <b>responds to state</b> with view updates"),
        ("cross", "Why <b>blocking</b> the main thread hurts responsiveness"), ("layers", "Why <b>tasks</b> and OS <b>threads</b> differ"),
        ("check", "Why performance is <b>measured</b>, not guessed")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.5 &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step" style="row-gap:16px">
{cells}
    </div>
  </div>""", notes(('SAY', 'Seven ideas you should be able to explain to other developers by the end of this lesson.'),
                 ('CONNECT', 'First, where this sits in NPay.'))))
# authored (Unit 00 audit): bridge from Lesson 0.4 on the shared NPay map
S.append(map_slide('0.5', 'Today: the main thread', ('thread',),
                   'Lesson 0.4: your code hears lifecycle events through AppDelegate, SceneDelegate or the SwiftUI <code>App</code> and <code>scenePhase</code>.',
                   'Inside the NPay process: how the main thread and its RunLoop turn a tap into Swift code and a new frame.',
                   'Lesson 0.4 was about how the system tells our code that a scene changed. Today we go inside the process, to the one thread that runs every tap handler and every screen update: the main thread.',
                   'Start with a kitchen.'))

# ================================================================== 1 · main thread
divider(1, "First understand the main thread", "One head chef plates every dish",
        "Before RunLoops and rendering: what is the main thread, and why does it matter so much?", "Start with a kitchen.")
P = [row(0, 0, 560, 62, "user", "User interface", "touch, scroll, text input, navigation", "1"),
     wire(f'M280 62V88{head(280, 88, "d")}'),
     '<g class="nd" data-lit="2"><rect class="sh" x="0" y="94" width="560" height="130" rx="14"/><use href="#i-thread" x="16" y="110" width="26" height="26"/>'
     '<text x="54" y="122">Main thread</text><text class="sm" x="54" y="141">processes UI events and main-thread work</text></g>']
for i, t in enumerate(["Tap", "Layout", "UI update"]):
    P.append(f'<g class="nd" data-lit="2"><rect class="sh" x="{20 + i * 178}" y="160" width="160" height="44" rx="10"/><text class="sm" x="{100 + i * 178}" y="187" text-anchor="middle">{t}</text></g>')
P += [wire(f'M280 224V262{head(280, 262, "d")}', None, "dash"),
      row(0, 268, 560, 62, "layers", "Background execution", "networking, file I/O, expensive computations", "3")]
S.append(slide("Part 1 &middot; Main thread &middot; conceptual", "The main thread is the head chef", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {svg("0 0 560 332", "User interface events go to the main thread, which handles taps, layout and UI updates; networking, file I/O and expensive computation belong to background execution.", "s3main", P, "max-height:380px")}
    <div>
      <div class="analogy">
        <div class="icon"><svg viewBox="0 0 24 24"><use href="#i-user"/></svg></div>
        <p>One <b>head chef</b> plates every dish the guests see. If the head chef stops to <b>bake bread from scratch</b>, every order on the rail waits.</p>
      </div>
      {cues(3)}
      <div class="gap"></div>
      <div class="rule step" data-label="Rule">Keep the main thread <b>responsive</b>. No expensive synchronous work inside button actions or UI callbacks.</div>
    </div>
  </div>""", notes(('SAY', 'Think of the restaurant kitchen inside the NPay process. One head chef plates every dish the guests see. Prep cooks can chop and simmer in the back, but only the head chef sends plates out. If the head chef stops to bake bread from scratch, every order on the rail waits. The head chef is the main thread.'),
                  ('SAY', 'Click through: UI events arrive; the main thread handles taps, layout and UI updates; networking, file I/O and heavy computation belong elsewhere. UIKit requires its UI APIs on the main thread, and SwiftUI has main-actor isolation requirements for UI state and updates.'),
                  ('ASK', 'What happens to other taps while a button action does three seconds of work on the main thread?'),
                  ('EXPECT', 'They wait. The head chef is busy baking bread.'),
                  ('CONNECT', 'Where does the main thread live? Inside the process.'))))

# ================================================================== 2 · process vs thread
divider(2, "Process versus thread", "The environment and the paths through it",
        "Lesson 0.1 introduced processes and threads. Now we need the difference precisely.", "Look inside NPay's process.")
P = ['<g class="nd"><rect class="sh" x="0" y="0" width="560" height="330" rx="18"/><use href="#i-process" x="20" y="18" width="26" height="26"/><text x="56" y="37">NPay process</text></g>',
     f'<g class="nd" data-lit="1+"><rect class="sh" x="24" y="64" width="246" height="130" rx="14"/><use href="#i-thread" x="134" y="84" width="28" height="28"/><text x="147" y="140" text-anchor="middle">Main thread</text><text class="sm" x="147" y="162" text-anchor="middle">UI events, rendering coordination</text></g>',
     f'<g class="nd"><rect class="sh" x="290" y="64" width="246" height="130" rx="14"/><use href="#i-thread" x="400" y="84" width="28" height="28"/><text x="413" y="140" text-anchor="middle">Other threads</text><text class="sm" x="413" y="162" text-anchor="middle">system and application work</text></g>',
     '<g class="nd" data-lit="2+"><rect class="sh" x="24" y="214" width="512" height="92" rx="14"/><text class="mono" x="44" y="244">SHARED PROCESS RESOURCES</text><text x="44" y="276">Heap, loaded code, open files, network resources</text></g>']
S.append(slide("Part 2 &middot; Process vs thread &middot; conceptual", "One process, several threads", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {svg("0 0 560 332", "The NPay process contains the main thread and other threads, which share the process resources: heap, loaded code, open files and network resources.", "s5proc", P, "max-height:380px")}
    <div>
      {points([("process", "Process", "the app&rsquo;s execution environment"), ("thread", "Thread", "a path of execution within it")], cls="v", box="card accent", step=False)}
      {cues(2)}
      <div class="gap"></div>
      <p class="small">Threads <b>share</b> the process&rsquo;s address space; each has its <b>own stack</b> and scheduling state.</p>
      <div class="rule step" data-label="Modern Swift">An asynchronous Swift <b>task is not a thread</b>. Tasks can suspend without blocking an OS thread.</div>
    </div>
  </div>""", notes(('SAY', 'A process is the application’s execution environment; a thread is a path of execution within it. Threads share the process address space, but each has its own execution stack and scheduling state.'),
                  ('SAY', 'For modern Swift: an asynchronous task is not the same thing as a thread. Swift concurrency schedules tasks onto executors, and tasks may suspend without blocking an operating-system thread. We return to this shortly.'),
                  ('CONNECT', 'How does the main thread wait for work without spinning? A RunLoop.'))))

# ================================================================== 3 · RunLoop
divider(3, "What is a RunLoop?", "How a thread waits for work",
        "The main thread does not poll in a busy loop. It waits, handles one piece of work, and waits again.", "Here is the cycle.")
P = []
loop = [(10, 10, "clock", "Wait for work", ""), (290, 10, "tap", "Receive an event", ""), (290, 190, "code", "Dispatch the callback", ""), (10, 190, "thread", "Return to waiting", "")]
for i, (x, y, ic, t, sub) in enumerate(loop):
    P.append(tall(x, y, 220, 104, ic, t, sub, str(i + 1)))
P += [wire(f'M236 62H284{head(284, 62, "r")}'), wire(f'M400 120V184{head(400, 184, "d")}'),
      wire(f'M284 242H236{head(236, 242, "l")}'), wire(f'M120 184V120{head(120, 120, "u")}')]
S.append(slide("Part 3 &middot; RunLoop &middot; conceptual", "The RunLoop cycle", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {svg("0 0 520 300", "RunLoop cycle: wait for work, receive an event, dispatch the callback, return to waiting", "s7loop", P, "max-height:360px")}
    <div>
      <p>A <b>RunLoop</b> lets a thread wait for and process work: input events, timers and scheduled callbacks. The main thread&rsquo;s run loop takes part in app event processing.</p>
      {cues(4)}
      <div class="rule step" data-label="Why it matters">It can only handle the next event when execution <b>returns to it</b>. A callback that blocks for seconds stops everything else.</div>
      <p class="small muted" style="margin:14px 0 0">Conceptual. The real Core Foundation RunLoop has modes, input sources, observers, timers and dispatch-queue integration.</p>
    </div>
  </div>""", notes(('SAY', 'A RunLoop lets a thread wait for and process sources of work: input events, timers and scheduled callbacks. Click through the cycle: the head chef waits at the order rail, takes the next ticket, cooks that one order, and returns to the rail. The RunLoop is the order rail.'),
                  ('SAY', 'Why it matters: the loop only handles the next event when execution returns to it. If a main-thread callback blocks for several seconds, other main-thread work cannot proceed normally.'),
                  ('CONNECT', 'Now follow one tap all the way through.'))))

# ================================================================== 4 · event journey
divider(4, "Follow a button tap", "From finger to screen",
        "Let's trace the full journey of one tap.", "Eight steps, one per click.")
journey = [("Touch", "The finger touches the screen", "The touchscreen hardware detects the contact."),
           ("iOS events", "The system delivers an event", "iOS turns the touch into an event for the app in front."),
           ("Main RunLoop", "The main thread picks it up", "The main run loop receives the event and dispatches it."),
           ("Hit testing", "The framework finds the control", "SwiftUI or UIKit works out which control or gesture was tapped."),
           ("Action runs", "Your Button action runs", "Your Swift code executes on the main actor."),
           ("State changes", "State changes", "SwiftUI’s state-tracking machinery detects that UI-relevant information changed."),
           ("View update", "SwiftUI updates the views", "Relevant view bodies are evaluated, reconciled and laid out."),
           ("On screen", "The new frame is displayed", "The graphics system presents the updated pixels.")]
S.append(slide("Part 4 &middot; Event journey &middot; conceptual", "One tap, eight steps", f"""  <div class="body">
    {stepper(journey, 112, 130, 14.3, "STEP", "s9tap", "A tap travels from the touchscreen through iOS event delivery, the main run loop, hit testing, the button action, state change, view update and display")}
    {cues(7)}
    <p class="small muted" style="margin:16px 0 0">Deliberately simplified. A SwiftUI Button does not read raw touchscreen hardware events; the OS and frameworks handle that.</p>
  </div>""", notes(('SAY', 'Step six is the moment SwiftUI’s state tracking notices that something relevant to the interface changed. Click through all eight to see the whole path from hardware to pixels.'),
                  ('SAY', 'The hardware and system-event pathway is deliberately simplified. A Button is not responsible for reading raw touchscreen events; the OS and UI frameworks handle the low-level details so we can work with controls and gestures.'),
                  ('ASK', 'At which steps is the main thread busy?'),
                  ('EXPECT', 'From the run loop picking up the event, through your action and the view update. That is why your action must be quick.'),
                  ('LIVE DEMO', 'Set a breakpoint inside NPay&rsquo;s Refresh balance Button action and tap it. In the debug navigator, select Thread 1 (the main thread) and read the backtrace from the bottom: main, the run loop frames (CFRunLoopRun...), event dispatch, SwiftUI, then your closure at the top. That stack is steps 3 to 5 of this slide.'),
                  ('CONNECT', 'So what happens if step five, your action, is slow?'))))

# ================================================================== 5 · blocking
divider(5, "Why blocking the main thread freezes an app", "One line can stop everything",
        "Now the most common performance mistake in UI code.", "Look at this button.")
BLOCK = '''Button("Refresh balance") {
    Thread.sleep(forTimeInterval: 3)
    balanceLoaded = true
}'''
P = ['<text class="mono" x="0" y="16">BLOCKING</text><text class="mono" x="0" y="96">NON-BLOCKING</text>']
for i in range(5):
    x = 130 + i * 200
    P.append(f'<text class="sm" x="{x + 100}" y="160" text-anchor="middle">{i}s</text>')
P.append('<g class="nd alert"><rect class="sh" x="130" y="28" width="600" height="40" rx="8"/><text class="sm" x="430" y="53" text-anchor="middle">blocked: main thread cannot process other UI work</text></g>')
P.append('<g class="nd"><rect class="sh" x="730" y="28" width="400" height="40" rx="8"/><text class="sm" x="930" y="53" text-anchor="middle">free</text></g>')
P.append('<g class="fade" data-lit="1+"><g class="nd lit"><rect class="sh" x="130" y="108" width="1000" height="40" rx="8"/><text class="sm" x="630" y="133" text-anchor="middle">free: the task suspends while it waits; UI work keeps flowing</text></g></g>')
S.append(slide("Part 5 &middot; Blocking", "One line that freezes the app", f"""  <div class="body">
    <div class="cols middle" style="grid-template-columns:1fr 1.15fr">
      {code("DashboardView.swift", BLOCK, "font-size:17px")}
      <p>The action runs on the <b>main actor</b>, and <code>Thread.sleep</code> blocks the executing thread for three seconds. Other main-thread work cannot proceed.</p>
    </div>
    <div class="gap-lg"></div>
    {svg("0 0 1136 166", "Illustrative timeline: blocking keeps the main thread busy for three seconds; the non-blocking version leaves it free", "s11time", P)}
    {cues(1)}
    <p class="small muted" style="margin:8px 0 0">Illustrative timeline, not a measured trace. Real scheduling and event timing vary.</p>
  </div>""", notes(('SAY', 'The button action runs on the main actor, and Thread.sleep blocks the executing thread for three seconds. During that time other main-thread work cannot proceed normally: taps, scrolling and animations all wait.'),
                  ('SAY', 'Click: the non-blocking version. The task suspends while it waits, and the main thread stays free for UI work.'),
                  ('CONNECT', 'What does the non-blocking version look like?'))))
ASYNC = '''Button("Refresh balance") {
    Task {
        isLoading = true
        do {
            balance = try await balanceService.fetchBalance()
        } catch {
            errorMessage = error.localizedDescription
        }
        isLoading = false
    }
}'''
S.append(slide("Part 5 &middot; Non-blocking", "Suspend instead of block", f"""  <div class="body cols middle" style="grid-template-columns:1.2fr 1fr">
    {code("DashboardView.swift", ASYNC, "font-size:16px")}
    <div>
      {points([("send", "await suspends", "the task pauses while the operation is pending"), ("thread", "The main thread stays free", "no blocking is required")], cls="v", label="How it works", step=False)}
      <div class="gap"></div>
      <div class="rule step" data-label="Nuance"><code>async</code> does <b>not</b> move CPU-heavy work off the main actor. Heavy synchronous computation still needs to run elsewhere.</div>
    </div>
  </div>""", notes(('SAY', 'Use asynchronous APIs for operations that can suspend, such as networking. await lets the task suspend while the operation is pending, without blocking the main thread.'),
                  ('SAY', 'Important nuance: async does not automatically move CPU-intensive work off the main actor. Heavy synchronous computation still needs appropriate isolation or execution elsewhere.'),
                  ('CONNECT', 'We keep saying main actor. How is that different from the main thread?'))))

# ================================================================== 6 · main thread vs MainActor
divider(6, "Main thread versus MainActor", "Related, but not identical",
        "Two terms people use interchangeably. They are closely related, but they are different concepts.", "Compare them side by side.")
S.append(slide("Part 6 &middot; Comparison", "Main thread vs MainActor", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Main thread</th><th>MainActor</th></tr>
      <tr><td>Operating-system thread</td><td>Swift concurrency global actor</td></tr>
      <tr><td>Executes UI event processing</td><td>Serializes access to main-actor-isolated code</td></tr>
      <tr><td>Exists at runtime</td><td>Enforced through Swift&rsquo;s actor isolation model</td></tr>
      <tr><td>Can be blocked by synchronous work</td><td>Code waiting at <code>await</code> lets other main-actor work run first</td></tr>
      <tr><td>Used by UIKit</td><td>Commonly used for SwiftUI UI-related state</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Mental model"><b>MainActor</b> is a concurrency isolation mechanism that coordinates main-thread-bound application work.</div>
    <p class="small muted step" style="margin:12px 0 0"><b>Reentrancy:</b> after an <code>await</code>, main-actor state may have changed, so check it again. Unit 08 &middot; 8.4 goes deeper.</p>
  </div>""", notes(('SAY', 'The main thread is an operating-system thread that executes UI event processing; it exists at runtime and can be blocked by synchronous work. MainActor is a Swift concurrency global actor that serializes access to main-actor-isolated code, enforced by Swift’s actor isolation model, and it can suspend at await points.'),
                  ('SAY', 'Mental model: MainActor is an isolation mechanism that coordinates main-thread-bound work.'),
                  ('SAY', 'Click: one consequence. While a main-actor function waits at await, the main actor is free to run other main-actor work, such as a second tap on Refresh balance. So when the function resumes, state it read before the await may have changed. That is actor reentrancy: re-check state after every await. Unit 08 covers it properly.'),
                  ('CONNECT', "Here it is on a ViewModel."))))
VM = '''@MainActor @Observable
final class DashboardViewModel {
    private(set) var balanceText = "—"

    func show(_ balance: Balance) {
        balanceText = (Decimal(balance.balanceMinor) / 100)
            .formatted(.currency(code: "INR"))
    }
}'''
S.append(slide("Part 6 &middot; @MainActor", "A main-actor ViewModel", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("DashboardViewModel.swift", VM, "font-size:16px")}
    <div>
      <p>The annotation helps ensure the ViewModel&rsquo;s mutable state is accessed <b>consistently through the main actor</b>.</p>
      <div class="gap"></div>
      <div class="rule step" data-label="Isolation, not speed"><code>@MainActor</code> does not make a slow calculation faster. A long synchronous calculation on the main actor can still freeze the UI.</div>
    </div>
  </div>""", notes(('SAY', 'Marking the ViewModel @MainActor means its mutable state, like balanceText, is always accessed through the main actor, which is where SwiftUI reads it. The balance arrives in paise as balanceMinor; the ViewModel formats it as rupees for the screen.'),
                  ('ASK', 'Does @MainActor make a slow calculation faster?'),
                  ('EXPECT', 'No. It provides isolation, not acceleration. A long synchronous calculation on the main actor can still freeze the interface.'),
                  ('CONNECT', '"Background work" means several different things. Separate them.'))))

# ================================================================== 7 · background work
divider(7, "Background work", "Not all work is the same",
        "Three different concepts developers often confuse.", "Here they are.")
S.append(slide("Part 7 &middot; Three kinds of work", "Three things called &ldquo;background&rdquo;", """  <div class="body">
    <div class="cols c3 stretch">
      <div class="card accent step"><span class="label">Asynchronous I/O</span><p>Network requests that <b>wait without occupying a thread</b>. Most file APIs are <b>synchronous</b>: keep large reads and writes off the main actor.</p></div>
      <div class="card accent step"><span class="label">CPU-bound parallel work</span><p>Image processing, data transformation and expensive calculations that need <b>CPU time away from the main actor</b>.</p></div>
      <div class="card accent step"><span class="label">iOS background execution</span><p>Work allowed while the app is <b>no longer foreground</b>, subject to system policies and capabilities.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step">An async task does <b>not</b> mean iOS will let it continue after the app is suspended.</div>
  </div>""", notes(('SAY', 'Asynchronous I/O: network requests that can wait without occupying a thread. Careful with files: most file APIs, such as Data(contentsOf:) and write(to:), are synchronous and block the calling thread, so large reads and writes belong off the main actor. CPU-bound parallel work: image processing, data transformation, expensive calculations that need CPU execution away from the main actor. iOS background execution: work allowed after the app leaves the foreground, subject to system policies and specific capabilities, as in Lesson 0.3.'),
                  ('SAY', 'These are different concerns. An async task does not automatically mean iOS will let it continue after the app is suspended.'),
                  ('CONNECT', 'Now the deadline the main thread is racing against: the frame.'))))

# ================================================================== 8 · frame budget
divider(8, "The rendering pipeline and frame budget", "The screen refreshes many times a second",
        "The display refreshes many times a second: 60 Hz, or up to 120 Hz on ProMotion displays, which adapt their rate. Each refresh is a deadline.", "Compare 60 Hz and 120 Hz.")
P = []
for i, (hz, ms, w) in enumerate([(60, "16.67", 900), (120, "8.33", 450)]):
    y = i * 86
    P.append(f'<g class="fade" data-lit="{i}+"><text class="mono" x="0" y="{y + 16}">{hz} HZ</text>'
             f'<g class="nd lit"><rect class="sh" x="0" y="{y + 26}" width="{w}" height="44" rx="10"/></g>'
             f'<text x="{w + 18}" y="{y + 58}" style="font-size:26px;font-weight:800">{ms} ms</text></g>')
S.append(slide("Part 8 &middot; Frame budget &middot; illustrative", "One refresh, one deadline", f"""  <div class="body">
    {svg("0 0 1136 160", "Refresh interval per display refresh: 16.67 milliseconds at 60 Hz, 8.33 milliseconds at 120 Hz", "s19frame", P)}
    {cues(1)}
    <div class="gap"></div>
    <p>Your app does <b>not</b> get the whole interval: the system also needs time for layout, rendering and compositing. ProMotion displays <b>adapt</b> their rate, up to 120 Hz.</p>
    <div class="rule step" data-label="Miss the deadline">If main-thread work or rendering misses it, no new frame arrives in time: visible <b>stutter</b> or <b>dropped frames</b>.</div>
  </div>""", notes(('SAY', 'An iPhone display updates at a rate the device and conditions support. At 60 Hz one refresh interval is about 16.67 milliseconds; click, and at 120 Hz it is about 8.33.'),
                  ('SAY', 'Back in the kitchen: a frame is a dish sent out on every tick. ProMotion displays adapt their rate, low when nothing moves and up to 120 Hz while scrolling, so the deadline changes with them.'),
                  ('SAY', 'That does not mean the app gets the whole interval for arbitrary computation; the system also needs time for layout, rendering, compositing and other work. Miss the deadline and the interface may not deliver a new frame in time, which shows as stutter or dropped frames.'),
                  ('CONNECT', 'So what actually happens between a state change and new pixels?'))))

# ================================================================== 9 · rendering pipeline
divider(9, "How does an iPhone draw a screen?", "From a state change to pixels",
        "Why an app can be slow even when its code is logically correct.", "The NPay balance changes from &#8377;25,000 to &#8377;24,750.")
P = []
stages = [("eye", "State changes", "new balance"), ("code", "Evaluate views", "the desired interface"), ("diff", "Reconcile", "what changed"),
          ("layout", "Layout", "sizes and positions"), ("layers", "Graphics", "prepare content"), ("frame", "Display", "pixels visible")]
for i, (ic, t, sub) in enumerate(stages):
    x = i * 192
    last = i == 5
    P.append(tall(x, 0, 168, 104, ic, t, sub, "1+" if last else "1", '' if last else 'pass', '' if last else f'--d:{i * .2:.1f}s'))
    if i < 5:
        P.append(wire(f'M{x + 172} 52H{x + 188}{head(x + 188, 52, "r")}'))
S.append(slide("Part 9 &middot; Rendering &middot; conceptual", "From &#8377;25,000 to &#8377;24,750", f"""  <div class="body">
    {svg("0 0 1136 106", "State change, evaluate views, reconcile, layout, graphics rendering, display", "s21render", P)}
    {cues(1)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Recall from Lesson 0.2">SwiftUI&rsquo;s <code>body</code> is a <b>description</b>, not a drawing function. Recomputing it does not mean every element is redrawn.</div>
  </div>""", notes(('SAY', 'A &#8377;250 coffee payment lands and the balance changes from &#8377;25,000 to &#8377;24,750. SwiftUI does not repaint the whole screen: it tracks the change, re-evaluates view descriptions, reconciles what changed, lays out as needed and works with the graphics pipeline until updated pixels appear. Click to watch it sweep through.'),
                  ('SAY', 'Recall from Lesson 0.2: body is a description of UI, not a drawing function. Recomputing a body does not mean every element is redrawn. That distinction is essential for SwiftUI performance.'),
                  ('CONNECT', 'So why do frames drop?'))))

# ================================================================== 10 · frame experiment
divider(10, "Why do frames drop?", "Work against the deadline",
        "Compare a smooth frame with one delayed by too much main-thread work.", "Three cases.")
cases = [("10 ms of work at 60 Hz", 10, 16.67, False, "Fits within one refresh interval, but real rendering still needs time for other system work."),
         ("20 ms of work at 60 Hz", 20, 16.67, True, "Longer than one refresh interval: the frame misses its deadline."),
         ("10 ms of work at 120 Hz", 10, 8.33, True, "The same work misses at 120 Hz: the deadline is twice as tight.")]
scale = 1136 / 22
P = []
for i, (t, work, iv, miss, d) in enumerate(cases):
    P.append(row(i * 388, 0, 360, 52, '', t, '', str(i)))
    g = (f'<g class="fade" data-lit="{i}"><text class="mono" x="0" y="100">REFRESH INTERVAL {iv} MS</text>'
         f'<g class="nd"><rect class="sh" x="0" y="112" width="{iv * scale:.0f}" height="40" rx="8"/></g>'
         f'<text class="mono" x="0" y="190">SIMULATED WORK {work} MS</text>'
         f'<g class="nd {"alert" if miss else "lit"}"><rect class="sh" x="0" y="202" width="{work * scale:.0f}" height="40" rx="8"/></g>'
         f'<path class="wire dash" d="M{iv * scale:.0f} 104V250"/>'
         f'<text x="0" y="290" style="font-size:20px;font-weight:400">{d}</text></g>')
    P.append(g)
S.append(slide("Part 10 &middot; Frame timing &middot; illustrative", "Does the work fit the frame?", f"""  <div class="body">
    {svg("0 0 1136 300", "Three cases: 10 ms at 60 Hz fits; 20 ms at 60 Hz misses; 10 ms at 120 Hz misses", "s23exp", P)}
    {cues(2)}
    <p class="small muted" style="margin:10px 0 0">Conceptual budget comparison, not a measured iPhone frame trace.</p>
  </div>""", notes(('SAY', 'Case one: 10 ms of work at 60 Hz fits within the 16.67 ms interval, though real rendering still needs time for other system work. Click: 20 ms misses the deadline. Click: the same 10 ms misses at 120 Hz, where the interval is 8.33 ms.'),
                  ('SAY', 'The lesson: avoid expensive synchronous work on the main thread, minimize unnecessary UI computation, and measure before optimizing.'),
                  ('CONNECT', 'Which brings us to async versus parallel work.'))))

# ================================================================== 11 · async vs parallel
divider(11, "Async versus parallel execution", "Waiting is not computing",
        "Two operations can both take time for completely different reasons.", "Compare a download with a calculation.")
FETCH = '''func fetchBalance() async throws -> Data {
    let url = URL(string: "https://api.npay.example/balance")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return data
}'''
S.append(slide("Part 11 &middot; Two kinds of slow", "Waiting vs computing", f"""  <div class="body">
    <div class="cols stretch">
      <div class="card accent step"><span class="label">Asynchronous I/O</span><h3 style="font-size:22px;margin:4px 0 6px">Download the NPay balance</h3><p class="small" style="margin:0">Mostly <b>waiting</b> for an external response.</p></div>
      <div class="card step"><span class="label">CPU-bound work</span><h3 style="font-size:22px;margin:4px 0 6px">Process a million transactions</h3><p class="small" style="margin:0">Mostly <b>executing calculations</b> on a CPU.</p></div>
    </div>
    <div class="gap"></div>
    <div class="cols middle" style="grid-template-columns:1.3fr 1fr">
      {code("BalanceService.swift", FETCH, "font-size:14px")}
      <p class="small">While <code>URLSession</code> waits for the response, the task <b>suspends</b>. No thread sits idle waiting.</p>
    </div>
  </div>""", notes(('SAY', 'Operation A downloads the NPay balance: mostly waiting for the bank&rsquo;s server. Operation B processes a million transaction records: mostly executing calculations. Both take time, for different reasons.'),
                  ('SAY', 'For networking: when URLSession waits for the response, the calling task can suspend. The executing thread does not need to sit idle.'),
                  ('CONNECT', 'But what about the calculation?'))))
CALC = '''@MainActor
func totalSpent(_ amountsMinor: [Int64]) async -> Int64 {
    var total: Int64 = 0
    for amount in amountsMinor {   // a million transactions
        total += amount
    }
    return total
}'''
S.append(slide("Part 11 &middot; async is not parallel", "async does not mean background", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Spending.swift", CALC, "font-size:16px")}
    <div>
      <p>Declared <code>async</code>, but it does <b>synchronous CPU work on the main actor</b> with no suspension point. It can block the UI.</p>
      <div class="gap"></div>
      <div class="rule step" data-label="Remember"><code>async</code> enables <b>suspension</b>. It does not guarantee parallel execution or a different thread.</div>
    </div>
  </div>""", notes(('SAY', 'Despite being declared async, this function loops over a million NPay transactions as synchronous CPU work on the main actor. It contains no suspension point, so it can block UI responsiveness.'),
                  ('ASK', 'Does adding async automatically create a background thread?'),
                  ('EXPECT', 'No. async enables suspension; it does not guarantee parallel execution or a different thread.'),
                  ('CONNECT', 'So where should each kind of work run?'))))

# ================================================================== 12 · what runs where
divider(12, "What should run where?", "Match the work to the place",
        "A quick reference for deciding where work belongs.", "Seven common kinds of work.")
S.append(slide("Part 12 &middot; Reference", "Where each kind of work belongs", """  <div class="body top">
    <table class="tbl" style="font-size:18px">
      <tr><th>Work</th><th>Preferred approach</th></tr>
      <tr><td>Button handling</td><td>Main actor</td></tr>
      <tr><td>UI state changes</td><td>Main actor or appropriate SwiftUI isolation</td></tr>
      <tr><td>HTTP request</td><td>URLSession async API</td></tr>
      <tr><td>Expensive image processing</td><td>Non-main-actor execution</td></tr>
      <tr><td>Large data transformations</td><td>Appropriate background executor or parallel processing</td></tr>
      <tr><td>Saving persistent data</td><td>Storage API with suitable concurrency</td></tr>
      <tr><td>Scheduled work after app backgrounding</td><td>Approved iOS background APIs</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step">A <b>background thread</b> and iOS <b>background-mode</b> execution are different concepts.</div>
    <p class="small muted" style="margin:10px 0 0">Coming up: Swift 6.2&rsquo;s <code>@concurrent</code> and <code>nonisolated(nonsending)</code> say where async code runs (Units 01 &middot; 1.9, 08 &middot; 8.1).</p>
  </div>""", notes(('SAY', 'Button handling and UI state on the main actor. HTTP through URLSession’s async API. Expensive image processing off the main actor. Large transformations on an appropriate background executor or in parallel. Persistent saves through a storage API with suitable concurrency. Work after backgrounding only through approved iOS background APIs.'),
                  ('SAY', 'Background thread execution and iOS background-mode execution are different things.'),
                  ('SAY', 'A pointer, not a topic for today: Swift 6.2 makes where async code runs more explicit. @concurrent marks an async function that should run off the caller&rsquo;s actor, and nonisolated(nonsending) describes async functions that stay on the caller&rsquo;s actor; with the newer build settings that becomes the default for nonisolated async functions. Units 01 and 08 cover this.'),
                  ('CONNECT', 'Finally: how do we know where time actually goes?'))))

# ================================================================== 13 · Instruments
divider(13, "Measure with Xcode Instruments", "Evidence before optimization",
        "Performance must be measured, not guessed. Xcode Instruments is how.", "Five tools to know.")
S.append(slide("Part 13 &middot; Instruments", "Tools for measuring performance", """  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    <div class="points v">
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-clock"/></svg><span><b>Time Profiler</b><small>where CPU time is spent</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-cross"/></svg><span><b>Hangs</b><small>periods when the app is unresponsive</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-memory"/></svg><span><b>Allocations</b><small>memory allocations</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-db"/></svg><span><b>Leaks</b><small>certain memory leaks</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-eye"/></svg><span><b>SwiftUI profiling</b><small>view updates and rendering, where your Xcode supports it</small></span></div>
    </div>
    <div class="rule step" data-label="Method">Reproduce the <b>slow path</b>, <b>measure</b> it, make one <b>targeted change</b>, then <b>measure again</b>.</div>
  </div>""", notes(('SAY', 'Time Profiler finds where CPU time is spent. Hangs identifies periods when the app becomes unresponsive. Allocations examines memory allocations; Leaks investigates certain memory leaks. SwiftUI profiling tools examine view updates and rendering where the installed Xcode supports them.'),
                  ('LIVE DEMO', 'Run a deliberately slow screen (for example the Thread.sleep button), record it with Time Profiler and Hangs, fix it with async, and record again to show the difference.'),
                  ('CONNECT', 'Before the review, one picture to remember.'))))

# authored (Unit 00 audit): recap on the shared map
S.append(recap_slide('0.5', ('thread',), [
    ("thread", "Keep the main thread free", "no blocking work in actions or callbacks"),
    ("clock", "await suspends, it does not block", "but async is not background"),
    ("eye", "Measure, don&rsquo;t guess", "Time Profiler and Hangs first")],
    'Three things to keep. The main thread, our head chef, must stay free: no blocking work in actions or callbacks. await suspends without blocking, but async alone does not move work off the main actor. And measure with Instruments before you optimize.'))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("cross", "Which is most likely to freeze NPay&rsquo;s UI?<br>A. awaiting URLSession data in a Task<br>B. a 3-second <code>Thread.sleep</code> in a Button action<br>C. updating a small <code>@State</code> value<br>D. reading a <code>@MainActor</code> ViewModel property", "B",
       "Thread.sleep blocks the main thread. Awaiting suspends the task, and the other two are cheap main-thread work.", "Thinking anything that takes time, or anything on the main actor, freezes the UI.",
       "Most pick B; some pick A. Ask why awaiting does not freeze."),
      ("code", "On the main actor: <code>print(\"1\")</code>, then <code>Task { print(\"3\") }</code>, then <code>print(\"2\")</code>. What order prints?", "1, 2, 3",
       "The new Task joins the main actor&rsquo;s queue. It runs only after the current code finishes or suspends.", "Expecting a new Task to start immediately, or on another thread.",
       "Some say 1, 3, 2. The lab lets you run exactly this."),
      ("layers", "Does <code>async</code> automatically mean background-thread execution?", "No",
       "async enables suspension; it does not guarantee parallel execution or a different thread.", "Assuming async moves work off the main actor.", "Many say yes."),
      ("thread", "Can a <code>@MainActor</code> ViewModel&rsquo;s state change while one of its methods is waiting at <code>await</code>?", "Yes",
       "While the method is suspended, other main-actor work can run, such as a second tap on Refresh balance. Re-check state after await.", "Assuming main-actor code runs start to finish without interruption.",
       "Many say no. Actor reentrancy: Unit 08 goes deeper."),
      ("eye", "Does every SwiftUI <code>body</code> evaluation redraw the entire screen?", "No",
       "body is a description. SwiftUI reconciles changes and updates only what is needed.", "Treating body like a paint method.", "Spaced review from 0.2. Some say yes. Recomputing a description is not redrawing pixels.")]
N = len(QA)
# multiple choice: question, then the options on smaller lines
for i, (ic, q, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    title = html.unescape(re.sub('<[^>]+>', '', q.split('<br>')[0]))
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
            ('CONNECT', 'Next question.' if i < N - 1 else 'Where these ideas go next in the course.')) + "</section>\n\n")

# authored (Unit 00 audit): where this goes next + Swift command-line lab
LAB = '''// + fetchBalance(): waits 0.2 s, returns 25_000
@MainActor
func refreshBalance() async {
    print("A: Refresh balance tapped")
    Task { print("B: a new main-actor task runs") }
    print("C: the action continues")
    let balance = await fetchBalance()
    print("D: balance \\(balance) arrived")
}

await refreshBalance()
print("E: done")'''
S.append(next_slide('0.5', [
    ("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "tasks are not threads; the main actor"),
    ("3.9", "SwiftUI rendering performance", "body is a description; view updates"),
    ("8.1", "Executors &amp; actor isolation", "where async code runs; <code>@concurrent</code>"),
    ("8.4", "Actor reentrancy &amp; logical races", "state can change across <code>await</code>"),
    ("8.7", "UI hangs &amp; frame performance", "blocking, frame deadlines, Instruments")],
    'Today was the foundation. Unit 01 makes tasks and actors precise. Unit 03 covers SwiftUI rendering performance. Unit 08 goes deep on executors, reentrancy, hangs and frame performance.'))
S.append(lab_slide('0.5', 'Predict the print order', 'A Swift command-line lab: no Xcode project needed.', [
    'Save the starter file as <code>lab05.swift</code>: this code plus a <code>fetchBalance()</code> that waits 0.2 s.',
    'Before running, write down the order in which <b>A&ndash;E</b> print.',
    'Run <code>swiftc -swift-version 6 lab05.swift -o lab05 &amp;&amp; ./lab05</code>. Were you right?',
    'Replace <code>await fetchBalance()</code> with a blocking call (<code>Thread.sleep</code> inside a plain function). Predict again, run, and explain why <b>B</b> moves.'],
    '', 'A command-line lab: predict first, then run. Expected output: A, C, B, D, E. B runs while refreshBalance waits at await. With a blocking call instead, the order becomes A, C, D, B, E: the new task cannot run until the main actor is free. LAB SCRIPT, full starter file lab05.swift: func fetchBalance() async -&gt; Int { try? await Task.sleep(for: .milliseconds(200)); return 25_000 } followed by the code on the slide. Step 4 version: import Foundation; func blockingFetch() -&gt; Int { Thread.sleep(forTimeInterval: 0.2); return 25_000 }; call let balance = blockingFetch(); and add try? await Task.sleep(for: .milliseconds(100)) before print("E: done") so B has time to print before the program exits. Note: Swift 6 refuses Thread.sleep directly inside an async function, which is why it sits in a plain function.',
    side=code("lab05.swift", LAB, "font-size:15px")))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.5 complete</p>
    <h2>Main Thread, RunLoop<br>&amp; Event Handling</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.6 &mdash; iOS Memory Architecture &amp; ARC</p>
  </div>
""" + notes(('SAY', 'Recap: the main thread handles critical UI work; a RunLoop supports event-driven execution; touches travel through iOS and the frameworks before reaching our code; SwiftUI responds to state with declarative updates; blocking the main thread damages responsiveness; tasks and OS threads differ; and performance must be measured, not guessed.'),
            ('SAY', 'Next, Lesson 0.6: stack versus heap, structs versus classes, reference counting, strong and weak references, retain cycles and why leaks happen, especially for developers coming from Java, Python or C++.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.5 — Main Thread, RunLoop &amp; Event Handling</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.5 — Main Thread, RunLoop &amp; Event Handling">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT05, 'w').write(doc)
print(len(S), 'slides')
