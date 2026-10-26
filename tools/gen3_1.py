"""Generates decks/unit-3/lesson-3.1/index.html from the Lesson 3.1 text (NavigationStack: How iOS Navigation Works).
The text came in three pieces (Sections 1-11; "Part 2" Sections 11-17; the complete code 1-12), grouped into 8 Parts.
Console output and screenshots come from tools/sim3_1 (the text's NavigationExperiment and complete code run unchanged
in the iOS Simulator; links and buttons activated through accessibility; the Section 9, 13, 14 and 16 experiments as
separate types)."""
import html, os, re, sys
OUT31 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

title_slide('3.1', 'NavigationStack:<br>How iOS Navigation Works',
            'NPay grows from one long scroll into <b>three screens</b>: Dashboard, Send Money and History, all sharing <b>one</b> balance.',
            'Unit 3 begins. At the end of Unit 2, NPay was one ScrollView: balance, editor, form and history stacked on one screen. Today the dashboard becomes the starting point and the other features move to their own screens, reached with NavigationStack and NavigationLink. We ran the lesson&rsquo;s first experiment and its complete code unchanged in the simulator, plus the experiments the text asks for.')
outcomes_slide('3.1', [("layers", "What <code>NavigationStack</code> manages, and why it is not a <code>VStack</code>"),
                       ("link", "<code>NavigationLink</code> declares a destination; <code>Button</code> performs an action"),
                       ("phone", "A push stays in the <b>same process</b> and window"),
                       ("db", "One state owner, shared by every screen"),
                       ("clock", "When a destination&rsquo;s state <b>resets</b>, and when its body runs"),
                       ("check", "Build and verify NPay&rsquo;s first multi-screen flow")])
where_slide('3.1', 'Today: from one screen to three', (),
            '2.12: the whole app in one ScrollView, with a working payment flow.',
            'Dashboard &rarr; Send Money and History, and Back again.',
            'Unit 2 ended with a complete payment flow on one long screen. Unit 3 is about larger SwiftUI apps: navigation first. Today: NavigationStack and NavigationLink. Next lesson: typed routes and programmatic navigation.',
            'The problem.')

# ================================================================== Part 1 (1)
divider(1, "The problem", "One scroll, or screens?", 'Unit 2 put every feature in one ScrollView.', 'Before and after.')
S.append(slide("Part 1 &middot; The problem we&rsquo;re solving (section 1)", "From one long scroll to three screens", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px 150px 150px;gap:18px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Before &middot; Unit 2", ul("Balance, editor, form, history", "One <b>ScrollView</b>; scroll to reach anything"))}
        <div class="step">{card("After &middot; Unit 3", ul("The <b>dashboard</b> is the start", "Send Money and History: <b>own screens</b>", "Back returns"))}</div>
      </div>
      {PHONE("img/before.png", "Before: 2.12", 150)}
      <div class="step">{PHONE("img/dash.png", "Dashboard", 150)}</div>
      <div class="step">{PHONE("img/pay.png", "Send Money", 150)}</div>
      <div class="step">{PHONE("img/history.png", "History", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'Where Unit 2 left us: one ScrollView with the balance editor, quick actions, the payment form and the transactions. To send money you scroll past everything else. It works, but it is not how people expect a payments app to feel.'),
                  ('SAY', 'Click: the plan. The dashboard becomes the starting point; Send Money and History live on their own screens; Back returns. Click, click, click: today&rsquo;s complete code, running: the dashboard, the Send Money screen, the History screen.'),
                  ('CONNECT', 'The smallest possible navigation first.'))))

# ================================================================== Part 2 (2, 5)
divider(2, "NavigationStack &amp; NavigationLink", "A container and a destination", 'Two APIs give us navigation.', 'The smallest example.')
EXP = """struct NavigationExperiment: View {
    var body: some View {
        NavigationStack {
            NavigationLink("Send Money") {
                Text("NPay Payment Screen")
            }
            .navigationTitle("NPay")
        }
    }
}"""
APIS = [("<code>NavigationStack</code>", "manages stack-based navigation"), ("<code>NavigationLink</code>", "declares a navigation action"),
        ("destination closure", "provides the destination&rsquo;s content"), ("<code>.navigationTitle()</code>", "configures the title")]
S.append(slide("Part 2 &middot; First concept: NavigationStack (section 2)", "Four lines of navigation", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("NavigationExperiment.swift", EXP, "font-size:13.5px")}
        <div class="step">{tbl(["API", "What it does"], APIS)}</div>
      </div>
      {PHONE("img/exp.png", "Launch", 150)}
      <div class="step">{PHONE("img/exppushed.png", "After Send Money", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s first experiment, a new file NavigationExperiment.swift. A NavigationStack wraps the root content. Inside it, a NavigationLink titled Send Money, whose closure provides the destination: here just a Text. navigationTitle sets "NPay" on the root.'),
                  ('SAY', 'Click: the four APIs. NavigationStack manages stack-based navigation. NavigationLink declares a navigation action. The destination closure provides the destination&rsquo;s content. navigationTitle configures the title.'),
                  ('SAY', 'On the right, the code running unchanged: "NPay" as a large title and a Send Money link. Click: after activating the link, the destination with a back button. Run the preview and try it.'),
                  ('CONNECT', 'It is called a stack. Is it like VStack?'))))

P = [box(0, 0, 250, 40, 'Balance', '', None, ''), box(0, 52, 250, 40, 'Form', '', None, ''), box(0, 104, 250, 40, 'History', '', None, ''),
     '<text class="sm" x="125" y="176" text-anchor="middle">VStack: all children laid out, all visible</text>',
     box(340, 0, 250, 64, 'Dashboard', 'previous destination', None, 'ghost'),
     box(360, 40, 250, 104, 'PaymentScreen', 'the visible destination', None, 'lit'),
     '<text class="sm" x="475" y="176" text-anchor="middle">NavigationStack: a hierarchy, one visible</text>']
IFACE = """public struct NavigationStack&lt;Data, Root&gt; : View where Root : View {
    public init(@ViewBuilder root: () -> Root) where Data == NavigationPath
    public init(path: Binding&lt;NavigationPath&gt;, @ViewBuilder root: () -> Root)
    …
}"""
S.append(slide("Part 2 &middot; Not a layout stack (section 2)", "<code>NavigationStack</code> is not a <code>VStack</code>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {svg('0 0 620 184', 'A VStack shows all its children; a NavigationStack shows one destination of a hierarchy', 'nvs', P, 'max-height:200px')}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Two different jobs", ul("<code>VStack</code>: arranges children <b>vertically</b>", "<code>NavigationStack</code>: manages a hierarchy of <b>destinations</b>"))}
        <div class="step">{console("iOS 26.5 SDK, SwiftUI interface (simplified)", [IFACE.replace(chr(10), '<br>').replace('    ', '&ensp;&ensp;')], 12)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The name says stack, but this is not a layout stack. A VStack arranges several children vertically, and all of them are on screen together. A NavigationStack manages a hierarchy of navigation destinations: the root, then whatever has been pushed on top. One destination is visible at a time; the earlier ones sit behind it in the hierarchy.'),
                  ('SAY', 'Click: the declaration from the SDK, what Command-click shows, simplified. It is generic over Data and Root. The plain init takes only the root content; then Data is NavigationPath, a list of destinations SwiftUI keeps for you. The second init takes a path binding: navigation driven by your own state. That is Lesson 3.2.'),
                  ('CONNECT', 'NavigationLink looks like a button. Is it one?'))))

BTN = """Button("Send Money") {
    print("Send tapped")
}"""
LNK = """NavigationLink("Send Money") {
    PaymentScreen()
}"""
S.append(slide("Part 2 &middot; NavigationLink versus Button (section 5)", "An action, or a destination?", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("An action", BTN, "font-size:15px")}{out("A <b>button</b> runs code when tapped.", "")}</div>
      <div class="step">{code("A destination", LNK, "font-size:15px")}{out("A <b>navigation link</b> declares where to go.", "")}</div>
    </div>
    <div class="gap"></div>
    <div class="step">{tbl(["You want to…", "Use"], [("Confirm a payment", "<code>Button</code>"), ("Move from Dashboard to PaymentScreen", "<code>NavigationLink</code>")])}</div>
  </div>""", notes(('SAY', 'Both are interactive, and both can show the words Send Money, but they express different intentions. A Button represents an action: run this closure. A NavigationLink declares a destination: this is where tapping takes you.'),
                  ('SAY', 'Click. Why it matters: with the navigation API, SwiftUI can provide the navigation behaviour for you: the push, the back button, the swipe back, the transition, and the navigation semantics. A Button that tried to fake that would have to rebuild it.'),
                  ('SAY', 'Click: the rule of thumb. Confirming a payment is an operation: a Button. Moving from the dashboard to the payment screen is navigation: a NavigationLink.'),
                  ('CONNECT', 'What happens between the tap and the new screen?'))))

# ================================================================== Part 3 (3, 12)
divider(3, "Behind the tap", "From touch to transition", 'The Unit 0 event pipeline, ending in a navigation change.', 'Six stages.')
STAGES = [("tap", "Touch event", "iOS processes the touch"), ("frame", "Hit test", "the NavigationLink is found"),
          ("link", "Link activates", "its destination is chosen"), ("layers", "Navigation state", "a destination is added"),
          ("eye", "Destination built", "PaymentScreen&rsquo;s body runs"), ("play", "Transition", "slides in; Back appears")]
P = []
for i, (ic, t, sub) in enumerate(STAGES):
    x = i * 190
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}', ''))
    if i < 5:
        P.append(wire(f'M{x + 174} 60H{x + 188}' + head(x + 188, 60, 'r')))
S.append(slide("Part 3 &middot; From tap to navigation transition (section 3) &middot; conceptual", "Six stages, one tap", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1132 120', 'Touch event, hit test, link activates, navigation state changes, destination built, transition', 'tap', P, 'max-height:140px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {card("Connect to Unit 0", ul("The same event pipeline as any tap", "The result is a <b>navigation change</b>, not a print"))}
      <p class="small muted" style="margin:0">Conceptual flow; SwiftUI&rsquo;s private navigation implementation is not guaranteed.</p>
    </div>
  </div>""", notes(('SAY', 'Unit 0 traced a touch through the event pipeline. Navigation is the same pipeline, ending somewhere new. Only stage 1 came with the text; stages 2 to 6 are our conceptual outline, not a description of SwiftUI&rsquo;s private implementation.'),
                  ('SAY', 'Click: a touch event: iOS processes the interaction. Click: hit testing finds the NavigationLink under the finger. Click: the link activates; it declared PaymentScreen as its destination. Click: the stack&rsquo;s navigation state gains that destination. Click: SwiftUI evaluates the destination&rsquo;s body. Click: the transition runs, the destination slides in and a back button appears.'),
                  ('CONNECT', 'What exactly was pushed?'))))

P = ['<rect class="sh" x="0" y="0" width="460" height="230" rx="16" style="fill:none;stroke-dasharray:6 5"/>',
     '<text class="sm" x="16" y="24">NavigationStack</text>',
     box(30, 40, 400, 64, 'PaymentScreen', 'currently visible destination', None, 'lit', 'phone'),
     box(30, 136, 400, 64, 'Dashboard', 'previous destination in the hierarchy', None, 'ghost', 'layout')]
S.append(slide("Part 3 &middot; What is actually pushed? (sections 3, 12)", "A destination, inside the same app", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{svg('0 0 460 230', 'NavigationStack holding the visible PaymentScreen above the previous Dashboard', 'push', P, 'max-height:250px')}
        <div class="gap"></div>
        <div class="step">{console("Printed in onAppear (simulator)", ["Dashboard: pid 49206, windows 1", "PaymentScreen: pid 49206, windows 1"], 14)}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("What a push is", ul("A navigation <b>destination</b>, managed by SwiftUI", "Same <b>process</b>, same window"))}
        <div class="step">{card("What it does not mean", ul("Off-screen &ne; state discarded", "No promised UIKit view controller per destination"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'At the public API level, SwiftUI manages a navigation destination. The text is careful here, and so are we: do not assume a push creates a new process, a new window, or a particular UIKit view controller for every destination. Navigation happens inside the existing NPay app.'),
                  ('SAY', 'Click: our evidence. Both screens printed their process ID and the window count when they appeared: the same pid, one window. The tap changed what the one window shows.'),
                  ('SAY', 'Click: and the dashboard? It stops being the visible destination, but that does not mean its view state is destroyed. The stack keeps the relationship between the active destination and the earlier ones. Whether state survives depends on identity and navigation lifetime, which Part 6 measures.'),
                  ('CONNECT', 'Now NPay&rsquo;s real destinations.'))))

# ================================================================== Part 4 (6-8)
divider(4, "Build the destinations", "Separate screens, separate structs", 'PaymentScreen and HistoryScreen, then the links.', 'Two placeholder screens.')
PAY0 = """struct PaymentScreen: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "arrow.up.right.circle.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)
            Text("Send Money")
                .font(.title.bold())
            Text("NPay payment form will appear here.")
                .foregroundStyle(.secondary)
        }
        .padding()
        .navigationTitle("Send Money")
        .navigationBarTitleDisplayMode(.inline)
    }
}"""
HIS0 = """struct HistoryScreen: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "clock.arrow.circlepath")
                .font(.system(size: 64))
                .foregroundStyle(.blue)
            Text("Transaction History")
                .font(.title.bold())
            Text("NPay transaction history will appear here.")
                .foregroundStyle(.secondary)
        }
        .padding()
        .navigationTitle("History")
    }
}

#Preview { NavigationStack { HistoryScreen() } }"""
S.append(slide("Part 4 &middot; Our first real destinations (sections 6&ndash;7)", "One struct per destination", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("PaymentScreen.swift", PAY0, "font-size:11.5px")}
      <div class="step">{code("HistoryScreen.swift", HIS0, "font-size:11.5px")}</div>
    </div>
    <div class="gap"></div>
    <div class="step">{card("Why a separate struct?", ul("A distinct <b>destination</b> deserves its own type", "Room for its own state and behaviour later"))}</div>
  </div>""", notes(('SAY', 'PaymentScreen.swift: an icon, a title and a placeholder line in a VStack. It sets its own navigation title, Send Money, and asks for the inline title display mode: a small title in the bar instead of the large one.'),
                  ('SAY', 'Click: HistoryScreen.swift, the same shape, with the default large title. Notice the preview wraps the screen in a NavigationStack; without a stack around it, a destination&rsquo;s navigation title has nowhere to appear.'),
                  ('SAY', 'Click: why separate structs? PaymentScreen represents a distinct application destination. Its own type improves composition and prepares NPay for navigation-specific state and behaviour.'),
                  ('CONNECT', 'Wire them into the dashboard.'))))

WRAP = """NavigationStack {
    ScrollView {
        VStack(spacing: 24) {
            // Existing dashboard content

            NavigationLink {
                PaymentScreen()
            } label: {
                Label("Open Send Money",
                      systemImage: "arrow.up.right")
            }

            NavigationLink {
                HistoryScreen()
            } label: {
                Label("Open History",
                      systemImage: "clock")
            }
        }
        .padding()
    }
    .navigationTitle("NPay")
}"""
S.append(slide("Part 4 &middot; Integrate with the NPay dashboard (section 8)", "Wrap the dashboard, add two links", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 160px;gap:24px;align-items:start">
      {code("ContentView.swift (body)", WRAP, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Steps", ul("<b>NavigationStack</b> outside the ScrollView", "Title on the root content", "Links inside the dashboard&rsquo;s VStack"))}
        <div class="step">{card("Run and check", ul("Tap each link", "Back returns to the dashboard"))}</div>
      </div>
      {PHONE("img/dash.png", "Dashboard (final code)", 160)}
    </div>
  </div>""", notes(('SAY', 'For this first lab we do not move all the functionality at once. We add the navigation container and the links. The NavigationStack goes outside the existing ScrollView; navigationTitle "NPay" goes on the root content inside it.'),
                  ('SAY', 'Then two NavigationLinks using the closure form with a separate label: a Label with text and an SF Symbol. Place them inside the dashboard&rsquo;s VStack. On the right, the final version of the dashboard, where the links are styled as wide tinted buttons.'),
                  ('SAY', 'Click: run NPay, tap each link, and verify that Back works.'),
                  ('CONNECT', 'Two screens now need the same balance. Who owns it?'))))

# ================================================================== Part 5 (9)
divider(5, "State across screens", "One owner, many screens", 'The dashboard keeps the balance and the transactions.', 'Pass data in, actions up.')
OWN = """// ContentView: the owner
@State private var balancePaise = 2_500_000
@State private var transactions: [Transaction] = []

// the destinations receive, they don't own
PaymentScreen(
    availableBalancePaise: balancePaise,
    onSend: sendDemoPayment
)
HistoryScreen(transactions: transactions)"""
P = [box(150, 0, 360, 56, 'ContentView', 'owns balance and transactions', None, 'lit', 'db'),
     wire('M250 60V100' + head(250, 100, 'd')), wire('M410 60V100' + head(410, 100, 'd')),
     box(0, 106, 320, 56, 'PaymentScreen', 'balance + payment action', None, '', 'send'),
     box(340, 106, 320, 56, 'HistoryScreen', 'transaction data', None, '', 'clock')]
S.append(slide("Part 5 &middot; State ownership across screens (section 9)", "The dashboard stays the owner", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.62fr) 150px;gap:22px;align-items:start">
      <div>{code("Owner and destinations", OWN, "font-size:12.5px")}
        <div class="gap"></div>
        {svg('0 0 660 162', 'ContentView owns the state and passes it to PaymentScreen and HistoryScreen', 'own', P, 'max-height:160px')}</div>
      <div class="step">{card("Measured", ul("After paying, the still-open screen read <b>Available: ₹23,500.00</b>", "It shows the owner&rsquo;s <b>current</b> value"))}</div>
      <div class="step">{PHONE("img/alert.png", "Right after paying", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'NPay already owns its state in ContentView: the balance in paise and the transactions. For this stage of learning, the dashboard stays the state owner. When the payment form moves to PaymentScreen, the dashboard passes it the available balance and the payment action, sendDemoPayment, as the onSend closure from Lesson 2.12. HistoryScreen receives the transaction collection. No screen creates its own balance.'),
                  ('SAY', 'Click: the evidence. In our run of the complete code, the payment screen was still on screen when the payment succeeded, under the alert. Its "Available" line already read ₹23,500.00: the owner changed, SwiftUI re-evaluated the dashboard, and the destination received the new value. Click: the screenshot.'),
                  ('CONNECT', 'And if PaymentScreen kept its own copy?'))))

OWN2 = """struct OwnBalancePaymentScreen: View {
    @State private var balancePaise: Int   // a second owner

    init(startPaise: Int) {
        _balancePaise = State(initialValue: startPaise)
    }

    var body: some View {
        VStack(spacing: 20) {
            Text("Available: \\(Money.display(balancePaise))")
            Button("Pay ₹1,500") { balancePaise -= 150_000 }
        }
    }
}"""
S.append(slide("Part 5 &middot; What if PaymentScreen owns a balance? (section 9)", "Two owners, two balances", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("The experiment (authored)", OWN2, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{tbl(["Where", "Shows (simulator)"], [("Dashboard", "₹25,000.00"), ("PaymentScreen, after Pay ₹1,500", "₹23,500.00"), ("Back on the dashboard", "<b>₹25,000.00</b>")])}</div>
        <div class="warn step" data-label="Inconsistent">{ul("A second <code>@State</code> is a separate <b>owner</b>", "The screens disagree about the balance")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s question: what happens if PaymentScreen creates its own @State balancePaise? We wrote it as an experiment: the screen starts its own state from the value it is given and subtracts from that.'),
                  ('SAY', 'Click: our run. The dashboard shows ₹25,000.00. On the payment screen, after Pay ₹1,500, it shows ₹23,500.00. Back on the dashboard: still ₹25,000.00. The initial value was copied once; after that there are two independent sources of truth.'),
                  ('SAY', 'Click: that is the bug. A second @State makes the payment screen a separate state owner, and the dashboard and payment screen can show inconsistent balances. Pass the value down and the action up instead.'),
                  ('CONNECT', 'Destinations do own some state, though: their own input. How long does it live?'))))

# ================================================================== Part 6 (10, 13, 14)
divider(6, "Destination lifetime", "Popped means reset", 'Local state lives as long as the destination does.', 'The counter experiment.')
CNT = """struct PaymentScreen: View {
    @State private var count = 0

    var body: some View {
        VStack(spacing: 20) {
            Text("Payment Screen")
                .font(.title)
            Text("Count: \\(count)")
                .font(.headline)
            Button("Increment") {
                count += 1
            }
            .buttonStyle(.borderedProminent)
        }
        .navigationTitle("Payment")
    }
}"""
S.append(slide("Part 6 &middot; Observe destination state lifetime (sections 10, 13)", "Back, then in again: the count is gone", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("PaymentScreen.swift (temporary)", CNT, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Run it", ul("Push; Increment &times; 3; Back; push again", "What is <code>count</code>?"))}
        <div class="step">{console("Simulator", ["after 3 taps: Count: 3", "[Back]", "pushed again: Count: 0"], 14)}</div>
        <div class="rule step" data-label="Why">{ul("Popping ended its <b>state lifetime</b>", "Keeping drafts: Lesson 3.5")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Replace PaymentScreen temporarily with a counter: @State count, a Text and an Increment button. Push the screen, tap Increment three times, go Back, push it again. What is count?'),
                  ('SAY', 'Click: our run. Count: 3 after three taps; after Back and a new push, Count: 0.'),
                  ('SAY', 'Click: why. When the destination was popped, it was removed from the navigation hierarchy and its state lifetime ended. The next push establishes a new destination identity, and its @State starts again at its initial value. Lesson 3.5 shows how to keep a draft across navigation.'),
                  ('CONNECT', 'So when does SwiftUI actually build and evaluate a destination?'))))

TRC = """struct TracePaymentScreen: View {
    init() { print("PaymentScreen.init") }

    var body: some View {
        let _ = Self._printChanges()
        let _ = print("PaymentScreen.body")
        return VStack {
            Text("Payment Screen")
        }
        .onDisappear { print("PaymentScreen.onDisappear") }
    }
}"""
S.append(slide("Part 6 &middot; Debugging navigation in Xcode (section 14)", "When do <code>init</code> and <code>body</code> run?", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("Instrumented destination", TRC, "font-size:12.5px")}
        <div class="step">{console("SDK: NavigationLink.init (simplified)", ["init(@ViewBuilder destination: () -&gt; Destination, …) {", "&ensp;&ensp;self.init(destination: destination(), label: label)", "}"], 12.5)}</div>
      </div>
      <div class="step">{console("Simulator console", ["Dashboard.body", "PaymentScreen.init", "-- tap Send Money", "TracePaymentScreen: @self changed.", "PaymentScreen.body", "-- tap Back", "PaymentScreen.onDisappear", "-- tap Send Money again", "TracePaymentScreen: @self changed.", "PaymentScreen.body"], 13.5)}
        <div class="gap"></div>
        {card("What we learn", ul("The struct is made with the link; <b>body</b> waits for the push", "Body runs again on every push: not a new process or window"))}</div>
    </div>
  </div>""", notes(('SAY', 'The text suggests a breakpoint in the destination&rsquo;s body or Self._printChanges(). We did both kinds of tracing: a print in init, _printChanges and a print in body.'),
                  ('SAY', 'Click: why init runs early. The SDK&rsquo;s NavigationLink initializer calls your destination closure right away and stores the resulting view value. Click: our console. Dashboard.body, then PaymentScreen.init, before any tap. The struct value exists; its body has not run. Tap Send Money: _printChanges reports @self changed and body runs. Back: onDisappear. Push again: body runs again, with no new init, because the dashboard did not re-evaluate.'),
                  ('SAY', 'The lesson: body evaluation is cheap and repeated. A body running, even several times, does not mean a new process, a new window, or a new rendering surface.'),
                  ('CONNECT', 'The text&rsquo;s Xcode experiments, all run.'))))

XP = [("1. Open PaymentScreen, Back", "Dashboard returns"), ("2. Open HistoryScreen, Back", "Dashboard returns"),
      ("3. <code>@State counter</code> in PaymentScreen", "Resets to 0 after Back and a new push"),
      ("4. Command-click <code>NavigationStack</code>", "<code>NavigationStack&lt;Data, Root&gt;</code>, <code>init(root:)</code>, <code>init(path:root:)</code>"),
      ("5. Breakpoint in the destination&rsquo;s body", "Hit on each push; never before the first")]
S.append(slide("Part 6 &middot; Xcode experiments (section 10)", "Five experiments, five results", f"""  <div class="body">
    {tbl(["Experiment", "What we saw (simulator)"], XP, 'tbl')}
    <div class="gap"></div>
    <div class="rule step" data-label="Remember">{ul("A body may be evaluated many times; that is not a new iOS process")}</div>
  </div>""", notes(('SAY', 'The text asks you to complete five experiments before moving on; here is what each gave us. Opening PaymentScreen and HistoryScreen and going Back returned to the dashboard both times. The counter reset to zero after Back and a new push. Command-click on NavigationStack shows the generic struct and its two initializers. A breakpoint, or our print, in the destination body fires on each push and never before the first.'),
                  ('SAY', 'Click: the reminder from the text. A destination&rsquo;s body may be evaluated multiple times; that does not mean a new iOS process is created.'),
                  ('CONNECT', 'How does this compare with UIKit, and what happens to memory?'))))

# ================================================================== Part 7 (15, 16)
divider(7, "UIKit and memory", "Declarative navigation, ARC underneath", 'How NavigationStack relates to UINavigationController, and what Back frees.', 'The comparison.')
UK = [("<code>UINavigationController</code>", "<code>NavigationStack</code>"), ("<code>pushViewController</code>", "<code>NavigationLink</code> or a path update"),
      ("<code>popViewController</code>", "Back navigation or a path update"), ("<code>UIViewController</code> objects", "View descriptions and navigation state"),
      ("Imperative navigation API", "Declarative navigation API")]
S.append(slide("Part 7 &middot; NavigationStack versus UINavigationController (section 15)", "Same idea, declarative API", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:24px;align-items:start">
      {tbl(["UIKit", "SwiftUI"], UK, 'tbl')}
      <div class="rule step" data-label="Insight">{ul("SwiftUI may use UIKit internally on iOS", "No fixed one-to-one mapping to view controllers", "Use the public navigation APIs")}</div>
    </div>
  </div>""", notes(('SAY', 'In UIKit, navigation is commonly built with UINavigationController: you create view controller objects and call pushViewController and popViewController, an imperative API. SwiftUI&rsquo;s NavigationStack is a declarative abstraction: you describe destinations with links, or with a path, which is Lesson 3.2, and SwiftUI performs the pushes and pops. View controllers become view descriptions plus navigation state.'),
                  ('SAY', 'Click: the insight. On iOS, SwiftUI may integrate with UIKit internally, but do not assume a fixed one-to-one mapping between SwiftUI destinations and UIKit view controllers. Use the public navigation APIs unless you have a specific interoperability need; Unit 10 covers UIKit integration.'),
                  ('CONNECT', 'And memory: what happens to a destination&rsquo;s objects after Back?'))))

SVC = """final class DemoPaymentService {
    init() { print("DemoPaymentService init") }
    deinit { print("DemoPaymentService deinit") }
}

struct ServicePaymentScreen: View {
    @State private var service: DemoPaymentService?

    var body: some View {
        Text("Payment Screen")
            .onAppear {
                if service == nil { service = DemoPaymentService() }
            }
    }
}"""
S.append(slide("Part 7 &middot; What happens to memory when navigating? (section 16)", "Back can free memory; it doesn&rsquo;t promise to", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("A destination that owns a service (authored)", SVC, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Simulator", ["-- tap Send Money", "DemoPaymentService init", "-- tap Back", "DemoPaymentService deinit"], 13.5)}</div>
        {card("Two systems", ul("<b>SwiftUI</b>: view lifetime and state, by hierarchy", "<b>ARC</b>: class instances, by ownership (1.8)"))}
        <div class="step">{card("So", ul("Here: freed right after Back", "Off screen &ne; guaranteed immediate deallocation", "A capturing closure can keep it alive"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Connect Unit 0 and Unit 1. When a destination appears it may create state, load resources or reference services; when it disappears, some of that may become eligible for release. Two systems are involved: SwiftUI manages view lifetime and state according to the hierarchy, and ARC manages the lifetime of class instances, as in Lesson 1.8.'),
                  ('SAY', 'Our experiment, authored: the destination creates a reference-type service in onAppear and keeps it in @State. Click: the run: the service is created on the push; after Back, onDisappear, then deinit: the destination&rsquo;s state was discarded and the last strong reference went with it.'),
                  ('SAY', 'Click: but read that as "here", not "always". Disappearing from the screen is not a guarantee of immediate deallocation. If a closure retained that service, for example a stored callback or a task, its lifetime would follow those ownership relationships. That is why closure capture and reference cycles matter; we look at them again with ViewModels.'),
                  ('CONNECT', 'Now the complete code for Lesson 3.1.'))))

# ================================================================== Part 8 (17 + complete code)
divider(8, "NPay after Lesson 3.1", "Three screens, one state owner", 'The complete code: files, screens, and a verified run.', 'The architecture.')
ARCH = [("app", "NPayApp", "application entry point"), ("layers", "NavigationStack", "navigation container"), ("db", "ContentView / Dashboard", "owns NPay demo state")]
P = []
for i, (ic, t, sub) in enumerate(ARCH):
    P.append(box(0, i * 70, 460, 56, t, sub, None, 'lit' if i == 2 else '', ic))
    P.append(wire(f'M230 {i * 70 + 58}V{i * 70 + 68}' + head(230, i * 70 + 68, 'd')))
P += [box(0, 210, 220, 56, 'PaymentScreen', 'destination', None, '', 'send'), box(240, 210, 220, 56, 'HistoryScreen', 'destination', None, '', 'clock')]
P[-3] = wire('M115 198V208' + head(115, 208, 'd') + 'M345 198V208' + head(345, 208, 'd'))
TREE = """NPay/
├── NPayApp.swift
├── ContentView.swift
├── Models/
│   ├── Money.swift
│   └── Transaction.swift
├── Components/
│   ├── BalanceCard.swift
│   ├── BalanceEditor.swift
│   └── TransactionRow.swift
└── Screens/
    ├── PaymentScreen.swift
    └── HistoryScreen.swift"""
S.append(slide("Part 8 &middot; Final NPay architecture (section 17; code 1)", "From one file to a project", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {svg('0 0 460 266', 'NPayApp, NavigationStack, ContentView owning state, then PaymentScreen and HistoryScreen', 'arch', P, 'max-height:300px')}
      <div class="step">{code("Xcode project structure", TREE, "font-size:13px")}
        <p class="small muted" style="margin:8px 0 0">Folders organize; every file must belong to the NPay target.</p></div>
    </div>
  </div>""", notes(('SAY', 'The architecture after Lesson 3.1: NPayApp is the entry point; its WindowGroup shows ContentView, which wraps its content in a NavigationStack; ContentView, the dashboard, owns the demo state; PaymentScreen and HistoryScreen are destinations.'),
                  ('SAY', 'Click: the complete code splits the old single file into a project: the app and ContentView at the top, Money and Transaction in Models, BalanceCard, BalanceEditor and TransactionRow in Components, the two screens in Screens. The folders are organisational: make sure each file belongs to the NPay target, and remove the duplicate type definitions from the old ContentView.swift.'),
                  ('CONNECT', 'The payment screen is now real.'))))

PAYF = """struct PaymentScreen: View {
    let availableBalancePaise: Int
    let onSend: (String, Int) -> Bool

    @State private var recipient = ""
    @State private var amountText = ""
    @State private var showSuccess = false
    @FocusState private var focusedField: Field?
    @Environment(\\.dismiss) private var dismiss

    enum Field: Hashable { case recipient, amount }

    var body: some View {
        // fields, validation, Send Demo Payment (as in 2.12);
        // when onSend returns true: focusedField = nil; showSuccess = true
        Text("…")
            .alert("Demo Payment Successful", isPresented: $showSuccess) {
                Button("Done") { dismiss() }
            } message: {
                Text("Your simulated payment was recorded.")
            }
    }
}"""
S.append(slide("Part 8 &middot; PaymentScreen, complete (code 8)", "Pay, confirm, and go back", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.78fr);gap:22px;align-items:start">
      {code("Screens/PaymentScreen.swift (condensed)", PAYF, "font-size:11px")}
      <div>
        <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;align-items:start">
          {PHONE("img/pay.png", "Pushed", 130)}
          <div class="step">{PHONE("img/alert.png", "Sent ₹1,500", 130)}</div>
          <div class="step">{PHONE("img/paid.png", "Done: ₹23,500", 130)}</div>
        </div>
        <div class="gap"></div>
        <div class="tip" data-label="New: dismiss">{ul("<code>@Environment(\\.dismiss)</code>: a destination asks to be <b>dismissed</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Our first real destination. PaymentScreen receives the available balance and the onSend action from the dashboard, and owns only its input: recipient, amount text, the success flag and focus. The fields, the validation and the button are the ones from Lesson 2.12, with a decimal pad and a keyboard Done toolbar.'),
                  ('SAY', 'New: @Environment dismiss. It lets a destination request its own dismissal; here, popping back to the dashboard. When onSend returns true, the screen clears focus and shows an alert; its Done button calls dismiss. Alerts and sheets in depth are Lesson 3.4.'),
                  ('SAY', 'On the right, our run. The pushed screen with the balance. Click: after entering ravi@npay and 1500 and sending, the alert; the balance line already reads ₹23,500.00. Click: after Done, dismiss popped back to the dashboard: ₹23,500.00.'),
                  ('CONNECT', 'And the history screen receives the same data.'))))

HISF = """struct HistoryScreen: View {
    let transactions: [Transaction]

    var body: some View {
        List(transactions) { transaction in
            TransactionRow(transaction: transaction)
        }
        .navigationTitle("History")
    }
}

// in ContentView
NavigationLink {
    HistoryScreen(transactions: transactions)
} label: {
    Label("Transaction History", systemImage: "clock")
}"""
S.append(slide("Part 8 &middot; HistoryScreen, complete (codes 9&ndash;10)", "The same transactions, on their own screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 170px 170px;gap:22px;align-items:start">
      <div>{code("HistoryScreen.swift + the link", HISF, "font-size:12.5px")}
        <div class="gap"></div>
        {card("List", ul("<code>List(transactions)</code>: rows by stable <code>id</code> (2.10)"))}</div>
      {PHONE("img/history.png", "Before paying", 170)}
      <div class="step">{PHONE("img/paidhistory.png", "After paying", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'HistoryScreen receives the transaction array owned by ContentView and shows it with a List instead of a ScrollView and ForEach: List builds the rows by the transactions&rsquo; stable identifiers, as in Lesson 2.10. The dashboard&rsquo;s link passes transactions in.'),
                  ('SAY', 'Left screenshot: the three mock transactions. Click: after the payment, the same screen shows "Sent to ravi@npay", minus ₹1,500, on top: one array, owned once, shown by two screens.'),
                  ('CONNECT', 'The text&rsquo;s verification checklist.'))))

VER = [("NPay launches to the dashboard", "₹25,000.00 and the links"), ("Send Money opens PaymentScreen", "Available: ₹25,000.00"),
       ("Back returns to the dashboard", "yes"), ("A valid demo payment reduces the balance", "₹25,000.00 &rarr; ₹23,500.00"),
       ("It appears in recent transactions", "Sent to ravi@npay, -₹1,500.00"), ("HistoryScreen shows the same collection", "yes, on top"),
       ("Invalid amounts can&rsquo;t be submitted", "0, 12.345, 25000.01: disabled"), ("Balance editor updates the shared balance", "+ ₹1,000: ₹24,500.00 on both screens")]
S.append(slide("Part 8 &middot; Xcode verification checklist (code 12)", "Eight checks, all run", f"""  <div class="body">
    {tbl(["Check", "Simulator"], VER)}
    <div class="gap"></div>
    <div class="step">{card("Still intentional", ul("ContentView owns payment and transaction state: application architecture in Unit 4"))}</div>
  </div>""", notes(('SAY', 'The text&rsquo;s eight checks, run against the complete code. NPay launches to the dashboard with ₹25,000.00. Send Money opens PaymentScreen showing ₹25,000.00 available. Back returns. ravi@npay and 1500: the balance becomes ₹23,500.00 and "Sent to ravi@npay", minus ₹1,500.00, appears in the recent transactions, and on top in HistoryScreen. 0, 12.345 and 25000.01 keep the button disabled. Plus ₹1,000 on the dashboard gives ₹24,500.00, and the payment screen then shows the same ₹24,500.00 available.'),
                  ('SAY', 'Click: what we achieved: three real screens sharing one logical state. One limitation remains on purpose: ContentView still owns the payment and transaction state. Unit 4 moves that into a proper application architecture.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.1', (), [("layers", "A hierarchy, not a layout", "NavigationStack manages destinations; one is visible"),
                     ("link", "Links declare, buttons act", "NavigationLink for screens; Button for operations"),
                     ("db", "One owner; local state is temporary", "pass data down; a popped screen&rsquo;s @State resets")],
         'Three things to remember. NavigationStack manages a hierarchy of destinations inside the same process and window; it is not a layout container. NavigationLink declares where to go; Button performs an action. And state has one owner, the dashboard, which passes values and actions to its destinations, while a destination&rsquo;s own @State lives only as long as that destination: pop it and push again, and it starts over.')

review_divider(9)
review([("layers", "Choose one", "What does NavigationStack manage?",
         "What does <code>NavigationStack</code> manage?<br>A. Vertical layout<br>B. Navigation hierarchy<br>C. Thread scheduling", "B",
         "It manages destinations; one is visible at a time.",
         "Reading &ldquo;stack&rdquo; as a layout stack.", "Most pick B; some A.", None),
        ("phone", "Question", "Does navigation create a new application process?",
         "Does navigation create a new application process?", "No",
         "Both screens printed the same pid and one window.",
         "Picturing each screen as a separate app.", "Most say no.", None),
        ("link", "Choose one", "Which API best expresses moving to another screen?",
         "Which API best expresses moving to another screen?<br>A. <code>NavigationLink</code><br>B. <code>Spacer</code><br>C. <code>Text</code>", "A",
         "A link declares a destination; SwiftUI provides the push and Back.",
         "Faking navigation with a Button.", "Almost everyone picks A.", None),
        ("db", "Question", "Should every destination create its own balance?",
         "Should every destination create its own independent account balance?", "No",
         "A second <code>@State</code> is a second owner: our screens showed ₹23,500 and ₹25,000.",
         "Copying shared data into local state.", "Most say no.", None),
        ("clock", "Question", "Can a destination's @State reset after it is popped?",
         "Can destination-local <code>@State</code> reset after the destination is popped and recreated?", "Yes",
         "Popping ends its state lifetime; the next push starts from the initial value.",
         "Expecting off-screen state to persist.", "Some say no.", None),
        ("diff", "Predict the result", "Count after Increment ×3, Back, push again?",
         "PaymentScreen has <code>@State private var count = 0</code>. Push it, tap Increment three times, go Back, push it again. What does it show?<br>A. Count: 3<br>B. Count: 0<br>C. Count: 4", "B",
         "Our run: Count: 3, then Count: 0 after the new push.",
         "Thinking the struct keeps the value.", "Some pick A.", None),
        ("frame", "Question", "Is NavigationStack the same kind of container as VStack?",
         "Is <code>NavigationStack</code> the same kind of layout container as <code>VStack</code>?", "No",
         "A VStack lays out children; a NavigationStack manages destinations.",
         "Going by the name.", "Most say no.", None),
        ("eye", "Question", "Does NavigationLink create its destination's body immediately?",
         "Does <code>NavigationLink</code> necessarily create its destination&rsquo;s body immediately?", "No",
         "The destination struct is made with the link; its body ran only on the push.",
         "Confusing a view value with its body.", "Some say yes.", None),
        ("code", "Choose one", "From 2.9: who owns balancePaise?",
         "From Lesson 2.9: in <code>BalanceEditor(balancePaise: $balancePaise)</code>, who owns the value?<br>A. <code>BalanceEditor</code><br>B. <code>ContentView</code><br>C. The environment", "B",
         "A binding reads and writes the owner&rsquo;s state; it owns nothing.",
         "Thinking @Binding stores a copy.", "Most pick B.", "Spaced review from Lesson 2.9.")])

S.append(next_slide('3.1', [("3.2", "Typed routes &amp; programmatic navigation", "<code>NavigationPath</code>, <code>navigationDestination</code>, a confirmation screen"),
                            ("3.4", "Sheets &amp; alerts", "the success alert, studied properly"),
                            ("3.5", "Drafts across navigation", "keeping input when a screen is popped"),
                            ("Unit 4", "Application architecture", "payment state out of ContentView")],
                    'Lesson 3.2 replaces destination closures with a typed route model: NavigationPath, navigationDestination, and navigating to a payment confirmation screen after a simulated payment. Lesson 3.4 studies sheets and alerts; Lesson 3.5 keeps drafts across navigation; Unit 4 moves the payment state out of ContentView.'))

S.append(lab_slide('3.1', "NPay goes multi-screen", "Split NPay into files and screens; verify the checklist.",
                   ["Create the files from the project structure.",
                    "Run NavigationExperiment; tap Send Money.",
                    "Open each screen; check Back.",
                    "Pay ₹1,500 to ravi@npay; check both screens.",
                    "Add a counter to PaymentScreen; pop and push.",
                    "Command-click NavigationStack; break in a body."],
                   "", 'Expected, as in our run: ₹25,000.00 → ₹23,500.00 after paying ravi@npay ₹1,500, the alert, then back on the dashboard with "Sent to ravi@npay" in recent transactions and on top of History; invalid amounts keep Send disabled; the counter returns to 0 after Back and a new push; the body breakpoint fires on each push and not before.',
                   side=f'<div>{card("You hand in", ul("Your completed 8-item checklist", "Counter values before and after Back", "One sentence: who owns the balance, and why"))}</div>'))

end_slide('3.1', 'NavigationStack:<br>How iOS Navigation Works', 'Lesson 3.2 &mdash; Typed Routes &amp; Programmatic Navigation',
          'You can now explain what NavigationStack manages and why it is not a layout stack, choose NavigationLink for destinations and Button for actions, show that a push stays in the same process, keep one owner of state across screens, and predict when a destination&rsquo;s state resets and its body runs.',
          'Next, Lesson 3.2: typed routes and programmatic navigation. We control navigation through state, with NavigationPath and navigationDestination, and navigate to a confirmation screen after a payment.')

write_deck(OUT31, '3.1', 'NavigationStack', 'NavigationStack')
