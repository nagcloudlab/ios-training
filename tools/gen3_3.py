"""Generates decks/unit-3/lesson-3.3/index.html from the Lesson 3.3 text (TabView: Building NPay's Main Navigation).
The text came in three pieces (Sections 1-11; "Part 2" Sections 11-19; a note about a complete-code ZIP that was not
shared), grouped into 7 Parts. The complete code through 3.3 is assembled from the text's Sections 9-18 onto the 3.2
code (flagged). Console output and screenshots come from tools/sim3_3 (iOS Simulator)."""
import html, os, re, sys
OUT33 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

title_slide('3.3', 'TabView: Building<br>NPay&rsquo;s Main Navigation',
            'Four sections, <b>Home, Payments, History, Profile</b>, each with its own navigation stack, all sharing <b>one</b> store.',
            'Lesson 3.2 drove one NavigationStack from a typed path. Real payment apps have several top-level sections the user switches between all day. Today NPay gets a TabView with four tabs, a router that keeps one path per tab, and a shared store for the balance and transactions. We built the complete app from the text&rsquo;s pieces and measured how tabs live, keep their state and update.')
outcomes_slide('3.3', [("grid", "What <code>TabView</code> does, and how it differs from <code>NavigationStack</code>"),
                       ("code", "Drive the selected tab with <code>@State</code> and <code>.tag()</code>"),
                       ("layers", "Give each tab its <b>own</b> navigation path"),
                       ("clock", "What switching tabs does to view state, measured"),
                       ("db", "Share one <code>NPayStore</code> across tabs; Observation updates readers"),
                       ("shield", "Keep <b>where</b> (router) apart from <b>what</b> (store)")])
where_slide('3.3', 'Today: four sections, one app', (),
            '3.2: typed routes and a path; the app navigates after a payment.',
            'A TabView of four stacks, one router, one store.',
            'Lesson 3.2 gave us state-driven navigation inside one stack. Today NPay gets its main navigation: tabs, each with a stack, coordinated by a router and sharing a store. Next lesson: sheets, alerts and modal presentation.',
            'The requirement.')

# ================================================================== Part 1 (1)
divider(1, "The requirement", "Sections, not just screens", 'Users switch between major sections all the time.', 'Before and after.')
S.append(slide("Part 1 &middot; The engineering requirement (section 1)", "From one stack to four sections", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 130px 130px 130px 130px 130px;gap:14px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Today", ul("Dashboard &rarr; Send Money, History", "One <b>navigation stack</b>"))}
        <div class="step">{card("Wanted", ul("<b>Home, Payments, History, Profile</b>", "Always one tap away", "Top-level <b>sections</b>, not pushed screens"))}</div>
      </div>
      {PHONE("img/before.png", "3.2: one stack", 130)}
      <div class="step">{PHONE("img/home.png", "Home", 130)}</div>
      <div class="step">{PHONE("img/payments.png", "Payments", 130)}</div>
      <div class="step">{PHONE("img/history.png", "History", 130)}</div>
      <div class="step">{PHONE("img/profile.png", "Profile", 130)}</div>
    </div>
  </div>""", notes(('SAY', 'Today NPay navigates from the dashboard to Send Money and History with one navigation stack. That was 3.2, on the left.'),
                  ('SAY', 'Click: in a real payments app, users switch between major sections constantly: check the balance, pay, look at history, change a setting. We want persistent navigation between Home, Payments, History and Profile. These are top-level sections of the app, not screens pushed onto one stack.'),
                  ('SAY', 'Click by click: the four tabs of today&rsquo;s complete app, running in the simulator: Home, Payments, History, Profile. The tab bar stays at the bottom of every one.'),
                  ('CONNECT', 'What is a TabView?'))))

# ================================================================== Part 2 (2, 3)
divider(2, "TabView", "Selectable sections", 'A container that shows one of several children.', 'The smallest example.')
TEX = """struct TabExperiment: View {
    var body: some View {
        TabView {
            Text("Home Screen")
                .tabItem { Label("Home", systemImage: "house") }

            Text("History Screen")
                .tabItem { Label("History", systemImage: "clock") }
        }
    }
}"""
APIS = [("<code>TabView</code>", "hosts selectable tab content"), ("<code>.tabItem</code>", "provides the tab&rsquo;s label and icon"),
        ("<code>Label</code>", "combines text and a symbol"), ("Selected tab", "decides which content is active")]
S.append(slide("Part 2 &middot; What exactly is TabView? (section 2)", "Two children, one tab bar", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("TabExperiment.swift", TEX, "font-size:12.5px")}
        <div class="step">{tbl(["API", "Responsibility"], APIS)}</div>
      </div>
      {PHONE("img/tabexp.png", "Launch: Home", 150)}
      <div class="step">{PHONE("img/tabexphistory.png", "History selected", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'TabView is a generic SwiftUI container that presents several selectable child views. The text&rsquo;s first experiment: two Texts, each with a tabItem that supplies a Label, a title and an SF Symbol. Run it and you get a tab bar with Home and History.'),
                  ('SAY', 'Click: the APIs. TabView hosts the selectable content. tabItem provides each tab&rsquo;s label and icon. Label combines text and a symbol, as in 3.1. And the selected tab decides which content is active.'),
                  ('SAY', 'On the right, the experiment running on iOS 26.5: the tab bar floats at the bottom in the current system style. Click: History selected. TabView supports several presentation styles; on iPhone the conventional one is this tab bar.'),
                  ('CONNECT', 'How is that different from NavigationStack?'))))

P = [box(0, 0, 250, 46, 'Dashboard', '', None, ''), wire('M125 48V60' + head(125, 60, 'd')),
     box(0, 64, 250, 46, 'Payment', '', None, ''), wire('M125 112V124' + head(125, 124, 'd')),
     box(0, 128, 250, 46, 'Confirmation', '', None, 'lit'),
     '<text class="sm" x="125" y="200" text-anchor="middle">NavigationStack: deeper in one hierarchy</text>']
for i, t in enumerate(['Home', 'Payments', 'History', 'Profile']):
    P.append(box(330 + i * 130, 64, 118, 46, t, '', None, 'lit' if i == 2 else ''))
P += [wire('M330 140H838', None, 'faint'), '<text class="sm" x="584" y="200" text-anchor="middle">TabView: across major sections</text>']
S.append(slide("Part 2 &middot; TabView versus NavigationStack (section 3)", "Across, or deeper?", f"""  <div class="body">
    {svg('0 0 840 206', 'NavigationStack moves deeper; TabView switches between sections', 'tvn', P, 'max-height:230px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      <div class="rule step" data-label="TabView answers">{ul("<b>Which</b> major section is active?")}</div>
      <div class="rule step" data-label="NavigationStack answers">{ul("<b>How deep</b> have we gone in a section?")}</div>
    </div>
  </div>""", notes(('SAY', 'The most important architectural distinction of the lesson. On the left, a NavigationStack: Dashboard, then Payment, then Confirmation. It moves deeper within one navigation hierarchy. On the right, a TabView: Home, Payments, History, Profile, side by side. It switches between major application sections.'),
                  ('SAY', 'Click: TabView answers which major section is active. Click: NavigationStack answers how deep we have navigated within a section. They solve different problems, and real apps usually use them together: a stack inside each tab, as we build today.'),
                  ('CONNECT', 'Let&rsquo;s make the selected tab explicit state.'))))

# ================================================================== Part 3 (4-6)
divider(3, "Selection is state", "An enum, a binding, a tag", 'Same model as the path: change the value, the UI follows.', 'NPayTab.')
SEL = """enum NPayTab: Hashable {
    case home, payments, history, profile
}

@State private var selectedTab: NPayTab = .home

TabView(selection: $selectedTab) {
    Text("Home")
        .tabItem { Label("Home", systemImage: "house") }
        .tag(NPayTab.home)

    Text("History")
        .tabItem { Label("History", systemImage: "clock") }
        .tag(NPayTab.history)
    // Payments and Profile the same way
}"""
S.append(slide("Part 3 &middot; Control the selected tab with @State (section 4)", "The tag is the tab&rsquo;s selection value", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("Tab selection", SEL, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("<code>.tag()</code>", ul("Identifies a tab&rsquo;s <b>selection value</b>", "User selects a tab &rarr; SwiftUI writes <code>selectedTab</code>", "Code writes <code>selectedTab</code> &rarr; the tab switches"))}
        <div class="step">{console("onChange(of: selectedTab), simulator", ["select History&ensp;&rarr; selectedTab: home &rarr; history", "select Home&ensp;&ensp;&ensp;&rarr; selectedTab: history &rarr; home"], 13)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Make selection explicit. An enum, NPayTab, with a case per section, Hashable like our routes. A @State selectedTab starting at .home. And TabView with selection: $selectedTab, a binding again. Each child gets a tag with its NPayTab value.'),
                  ('SAY', 'The tag identifies a tab&rsquo;s selection value. When the user selects a tab, SwiftUI updates the bound selectedTab; when code changes selectedTab, SwiftUI switches the active tab. The state-driven model again, as with the path in 3.2.'),
                  ('SAY', 'Click: our run of the text&rsquo;s four-tab example with onChange printing the selection: selecting History wrote home to history; selecting Home wrote it back. The binding works in both directions.'),
                  ('CONNECT', 'What happens between the tap and the switch?'))))

ST = [("tap", "User taps History", "iOS delivers the touch"), ("grid", "Tab control", "reports the chosen tab"), ("code", "Binding written", "selectedTab = .history"),
      ("diff", "SwiftUI updates", "views that read selection"), ("eye", "History shown", "its content becomes active")]
P = []
for i, (ic, t, sub) in enumerate(ST):
    x = i * 228
    P.append(tall(x, 0, 208, 120, ic, t, sub, f'{i + 1}', ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 60H{x + 226}' + head(x + 226, 60, 'r')))
S.append(slide("Part 3 &middot; Tab selection pipeline (section 5) &middot; conceptual", "Five stages, one tap", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 120', 'User taps History, tab control, binding written, SwiftUI updates, History shown', 'pipe', P, 'max-height:140px')}
    <div class="gap"></div>
    <p class="small muted" style="margin:0">Conceptual SwiftUI selection flow; the internal tab-controller implementation is not guaranteed.</p>
  </div>""", notes(('SAY', 'Only stage 1 came with the text; stages 2 to 5 are our conceptual outline. Click: the user taps History; iOS delivers the interaction to the tab control. Click: the tab control reports which tab was chosen. Click: SwiftUI writes the new value into the bound selectedTab. Click: views that read the selection update. Click: the History tab&rsquo;s content becomes the active one.'),
                  ('SAY', 'As the text says, this is a conceptual flow; the internal tab-controller implementation is not guaranteed.'),
                  ('CONNECT', 'If the binding can be written by a tap, it can be written by code.'))))

PROG = """Button("View All Transactions") {
    selectedTab = .history
}"""
S.append(slide("Part 3 &middot; Programmatically switch tabs (section 6)", "Switch a section, or push a screen?", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("On the Home tab", PROG, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{console("Simulator", ["[activate \"View All Transactions\"]", "selectedTab: home &rarr; history"], 14)}</div></div>
      <div class="step">{tbl(["Code", "Means"], [("<code>selectedTab = .history</code>", "switch to the History <b>section</b>"), ("<code>path.append(.history)</code>", "push a History <b>screen</b> on this stack")], 'tbl')}
        <div class="gap"></div>
        <div class="rule" data-label="Choose one">{ul("One consistent navigation meaning per action")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Suppose the dashboard has a View All Transactions button. Its action sets selectedTab to .history. Click: our run: activating the button changed the selection from home to history. It switched the active tab without pushing any navigation destination.'),
                  ('SAY', 'Click: the distinction. Setting selectedTab switches major sections. path.append(.history), from 3.2, pushes a History screen onto the current stack: a different place, a different Back behaviour. For each action, NPay should pick one meaning and use it consistently.'),
                  ('CONNECT', 'If tabs are sections, where do their stacks go?'))))

# ================================================================== Part 4 (7, 12, 13)
divider(4, "A stack per tab", "Independent navigation paths", 'Each section remembers how deep it is.', 'The recommended structure.')
P = [box(250, 0, 360, 52, 'TabView', 'selected tab state', None, 'lit', 'grid')]
for i, (t, d) in enumerate([('Home', 'Account Details'), ('Payments', 'Payment Success'), ('History', 'Transaction Details'), ('Profile', 'Settings')]):
    x = i * 215
    P.append(wire(f'M430 54V70H{x + 100}V96' + head(x + 100, 96, 'd')))
    P.append(box(x, 100, 200, 56, t, 'NavigationStack', None, ''))
    P.append(wire(f'M{x + 100} 158V174' + head(x + 100, 174, 'd'), None, 'dash'))
    P.append(box(x, 178, 200, 44, d, '', None, 'ghost'))
S.append(slide("Part 4 &middot; Should each tab have its own NavigationStack? (section 7)", "Often yes: one hierarchy per section", f"""  <div class="body">
    {svg('0 0 845 222', 'TabView with four tabs, each holding a NavigationStack with its own deeper screen', 'arch4', P, 'max-height:250px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("Why", ul("Each section manages its <b>own</b> hierarchy", "Deeper flows stay in their tab"))}
      <div class="step">{card("Every app? No", ul("Structure follows the intended experience", "Useful when tabs have deeper flows"))}</div>
    </div>
  </div>""", notes(('SAY', 'For a larger app, each tab often gets its own NavigationStack. The TabView holds the selected-tab state; each section manages its own navigation hierarchy: Home to Account Details, Payments to Payment Confirmation, History to Transaction Details, Profile to Settings.'),
                  ('SAY', 'Click: does every app need four stacks? No. The right structure depends on the navigation experience you intend. But independent stacks are a useful design when each tab has its own deeper flow, which NPay will.'),
                  ('CONNECT', 'Our 3.2 router had one path. Now?'))))

RT = """enum NPayRoute: Hashable {
    case accountDetails, settings
    case paymentSuccess(UUID), transactionDetails(UUID)
}

@MainActor @Observable
final class NPayRouter {
    var selectedTab: NPayTab = .home
    var homePath: [NPayRoute] = []
    var paymentsPath: [NPayRoute] = []
    var historyPath: [NPayRoute] = []
    var profilePath: [NPayRoute] = []

    func select(_ tab: NPayTab) { selectedTab = tab }

    func showPaymentSuccess(_ id: UUID) {
        selectedTab = .payments
        paymentsPath.append(.paymentSuccess(id))
    }

    func returnHome() {
        paymentsPath.removeAll()
        selectedTab = .home
    }
}"""
S.append(slide("Part 4 &middot; TabView and NPayRouter together (section 12)", "One router: a selection and four paths", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("App/NPayRouter.swift (condensed)", RT, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Why separate paths", ul("Home &rarr; Account Details; History &rarr; a transaction", "Back on Home: still on Account Details", "One shared path makes that hard"))}
        <div class="step">{card("<code>@MainActor</code>", ul("Navigation state drives UI: mutate it on the main actor"))}</div>
        <div class="step">{card("<code>@Observable</code>", ul("SwiftUI tracks the properties it reads", "In depth: Unit 4"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The 3.2 router had one path. Now NPay has four tabs. Picture the journey: Home to Account Details; switch to History and open a transaction; switch back to Home. Ideally Home is still on Account Details, independently of History. One shared path for every tab makes that hard to manage.'),
                  ('SAY', 'The better design: the router holds the selected tab and one path per tab. The route enum changes too: account details, payment success and transaction details carrying a UUID, and settings. Two coordinating methods: showPaymentSuccess selects the Payments tab and pushes the success route; returnHome clears the payments path and selects Home.'),
                  ('SAY', 'Click: why @MainActor? Navigation state affects the user interface, so main-actor isolation keeps its mutations in the UI execution context, as in Lesson 1.9. Click: why @Observable? The Observation framework lets SwiftUI track which properties a view reads and respond when they change. The text studies it in depth in Unit 4; for now, this router is a reference-type object that owns navigation state.'),
                  ('CONNECT', 'Bind it to the TabView, and measure the journey.'))))

ROOT = """@State private var router = NPayRouter()

var body: some View {
    @Bindable var router = router

    TabView(selection: $router.selectedTab) {
        NavigationStack(path: $router.homePath) {
            HomeScreen(store: store, router: router)
        }
        .tabItem { Label("Home", systemImage: "house") }
        .tag(NPayTab.home)

        NavigationStack(path: $router.historyPath) {
            HistoryScreen(transactions: store.transactions)
        }
        .tabItem { Label("History", systemImage: "clock") }
        .tag(NPayTab.history)
        // Payments, Profile: the same shape
    }
}"""
S.append(slide("Part 4 &middot; Connect the router to TabView (section 13)", "Four bindings into one object", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 140px;gap:20px;align-items:start">
      {code("App/NPayRootView.swift (excerpt)", ROOT, "font-size:11.5px")}
      <div class="step">{console("The journey, router state printed", ["Home: Account Details", "&ensp;homePath: [accountDetails]", "History tab, open Coffee Shop", "&ensp;selectedTab: history", "&ensp;historyPath: [transactionDetails(3341DC68…)]", "Home tab again", "&ensp;selectedTab: home", "&ensp;on screen: Account Details"], 12)}</div>
      <div class="step">{PHONE("img/keep.png", "Home kept its place", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'The root view owns the router with @State and uses @Bindable inside body to get bindings: $router.selectedTab for the TabView, and $router.homePath, paymentsPath, historyPath, profilePath for the four stacks. In the text&rsquo;s scaffold the screens are placeholders; our complete code passes the store and router, as we will see.'),
                  ('SAY', 'Click: the text&rsquo;s journey, run on the complete app with the router&rsquo;s state printed. Home to Account Details: homePath is [accountDetails]. Switch to History, open Coffee Shop: selectedTab history, historyPath holds transactionDetails with that row&rsquo;s ID. Switch back to Home.'),
                  ('SAY', 'Click: Home is still on Account Details. Each tab kept its own position, because each stack is bound to its own path.'),
                  ('CONNECT', 'And state that is not navigation: does a tab switch destroy it?'))))

# ================================================================== Part 5 (8)
divider(5, "Does switching destroy state?", "Measure it, then design it", 'What happens to a tab&rsquo;s views and @State?', 'The experiment.')
S.append(slide("Part 5 &middot; Does tab switching destroy state? (section 8)", "Built on first visit, kept after", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Experiment (authored)", ul("Four tabs; each prints <code>body</code>, <code>onAppear</code>, <code>onDisappear</code>", "Each keeps a <code>@State</code> timestamp from when it was made"))}
        <div class="step">{console("Simulator", ["launch:&ensp;Home.body, Home.onAppear (state from 01:35)", "History:&ensp;History.body, History.onAppear (01:35)", "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Home.onDisappear", "Home:&ensp;&ensp;&ensp;Home.onAppear (01:35), History.onDisappear", "History:&ensp;History.onAppear (01:35), Home.onDisappear"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("What we saw (iOS 26.5)", ul("Payments, Profile never built: never selected", "A tab&rsquo;s view is built on <b>first</b> selection", "Switching: appear / disappear; <code>@State</code> <b>kept</b>"))}</div>
        <div class="step">{console("Payments draft, complete app", ["typed: ravi@npay, 1500.50", "History tab, then Payments again", "amount field: \"1500.50\", recipient: \"ravi@npay\""], 12.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s subtle question: the user starts a payment, switches to History, returns to Payments. Should the amount still be there? It depends on state ownership and view identity. So we measured. Our own experiment: four tabs, each printing when its body runs and when it appears or disappears, each holding a @State timestamp from when it was created.'),
                  ('SAY', 'Click: at launch only Home was built. Selecting History built it then. Switching back and forth only fired onAppear and onDisappear, and both kept their original state, minute 01:35. Click: so on this iOS version, a tab is built on first selection and kept afterwards; Payments and Profile were never built because nobody selected them.'),
                  ('SAY', 'Click: the real form. In the complete app we typed ravi@npay and 1500.50 on Payments, switched to History and back: both fields still held their text.'),
                  ('CONNECT', 'So can we rely on it?'))))

S.append(slide("Part 5 &middot; Design the draft&rsquo;s lifetime (section 8)", "Kept here; promised nowhere", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div class="warn" data-label="Don&rsquo;t rely on it">{ul("SwiftUI <b>can</b> preserve tab state", "Our run is behaviour, not a documented guarantee", "Not for <b>critical</b> drafts")}</div>
      <div class="rule step" data-label="Instead">{ul("Put the draft in a <b>deliberate owner</b>", "Its lifetime must span the tab changes", "How: Lesson 3.5")}</div>
    </div>
  </div>""", notes(('SAY', 'Our run kept the draft, and SwiftUI can preserve tab-associated state. But that is how this version behaved in this structure, not a documented promise, and it depends on view identity: restructure the root, and it may change. Do not rely on undocumented view-construction details for a critical payment draft.'),
                  ('SAY', 'Click: if a payment draft must survive tab changes, place its state in a deliberate owner whose lifetime spans those changes. Lesson 3.5 does exactly that.'),
                  ('CONNECT', 'The balance and transactions are shared across tabs. Who owns them now?'))))

# ================================================================== Part 6 (14-17)
divider(6, "Shared state: NPayStore", "One owner for every tab", 'Balance and transactions move out of ContentView.', 'The store.')
STORE = """@MainActor
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []

    func recordDemoPayment(recipient: String,
                           amountPaise: Int) -> UUID? {
        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty, amountPaise > 0,
              amountPaise <= balancePaise else { return nil }
        let id = UUID()
        balancePaise -= amountPaise
        transactions.insert(
            Transaction(id: id, title: "Sent to \\(trimmed)",
                        amountPaise: -amountPaise, date: .now),
            at: 0)
        return id
    }
}"""
S.append(slide("Part 6 &middot; Where should balance and transactions live? (section 14)", "Not in a tab: in a shared store", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("Store/NPayStore.swift", STORE, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("What changed", ul("Before: <code>ContentView</code> owned the data", "Now: <b>NPayStore</b> owns it; the root owns one store", "3.2&rsquo;s <code>sendDemoPayment</code>, moved in"))}
        <div class="step">{card("Never", ul("A separate balance per tab (3.1&rsquo;s two owners)"))}</div>
        <div class="warn step" data-label="Still a demo">{ul("In memory: not persisted, authenticated or server-backed")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The crucial design question. ContentView owned the balance and the transactions; now Home, Payments and History all need them. We must not create a separate balance per tab: Lesson 3.1 showed what two owners do. So Unit 3 introduces a shared application state object, NPayStore: main-actor, observable, holding the balance and transactions, with recordDemoPayment, which is 3.2&rsquo;s sendDemoPayment moved into the store: validate, subtract, insert, return the ID.'),
                  ('SAY', 'The root view owns one instance and passes it to the tabs. This prepares us for MVVM and dependency injection in Unit 4. Click: never one balance per tab. Click: and an honest note: this is still local, in-memory demo state. Not persisted, not authenticated, not backed by a payment server.'),
                  ('CONNECT', 'Connect the store to the tabs.'))))

WIRE = """@State private var router = NPayRouter()
@State private var store = NPayStore()

// inside the TabView
NavigationStack(path: $router.homePath) {
    HomeScreen(store: store, router: router)
}
NavigationStack(path: $router.paymentsPath) {
    PaymentsScreen(store: store, router: router)
}
NavigationStack(path: $router.historyPath) {
    HistoryScreen(transactions: store.transactions)
}
NavigationStack(path: $router.profilePath) {
    ProfileScreen()
}"""
S.append(slide("Part 6 &middot; Connect shared state to the root view (section 15)", "One store instance, passed to three tabs", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("NPayRootView (excerpt)", WIRE, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Passed down", ul("Home, Payments: the <b>store</b> itself", "History: <code>store.transactions</code>, a value", "Profile: nothing yet"))}
        <div class="step">{card("Our change (authored)", ul("Home also gets the <b>router</b>: its buttons switch tabs", "<code>.tabItem</code> and <code>.tag</code> as before"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The root view now owns two objects: the router and the store, both with @State. The same store instance goes to Home and Payments; History receives the transactions array as a value, as in 3.1; Profile needs nothing yet. When the balance changes, every view that reads it can update.'),
                  ('SAY', 'Click: one change of ours: the text passes only the store to Home, but Home&rsquo;s Send Money and History buttons switch tabs, so our complete code passes the router too. Each stack keeps its tabItem and tag as in Section 13.'),
                  ('CONNECT', 'How does SwiftUI know which tabs to update?'))))

S.append(slide("Part 6 &middot; How SwiftUI tracks changes across tabs (section 16)", "Only the readers re-evaluate", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Experiment (authored)", ul("One observable store, three tabs", "BalanceTab reads <code>balancePaise</code>; ListTab reads <code>transactions</code>; NameTab reads <code>profileName</code>", "A payment changes balance and transactions"))}
        <div class="step">{console("Simulator: bodies after the payment", ["ListTab.body (reads transactions)", "BalanceTab.body (reads balancePaise)", "<i>NameTab: not re-evaluated</i>"], 13)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("So", ul("Observation tracks which properties each body <b>read</b>", "ListTab updated though it was off screen", "Not &ldquo;redraw every tab on any change&rdquo;"))}</div>
        <div class="rule step" data-label="Remember">{ul("Exact evaluation and rendering stay framework-managed")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s flow: PaymentsScreen submits a payment; NPayStore validates and updates the balance and transactions; Observation tracks relevant reads and changes; HomeScreen shows the new balance and HistoryScreen the new transactions. We tested the "relevant" part: three tabs on one observable store, each reading a different property, and a payment that changes two of them.'),
                  ('SAY', 'Click: after the payment, ListTab and BalanceTab re-evaluated their bodies; NameTab did not, because it read only profileName. ListTab updated even though it was not the visible tab: it had been built, and it read transactions.'),
                  ('SAY', 'Click: so Observation does not redraw every tab whenever any property changes; it tracks dependencies. Click: but, as the text says, the precise evaluation and rendering behaviour remains framework-managed. Do not build logic on body counts.'),
                  ('CONNECT', 'Two objects now: what goes where?'))))

RS = [("Selected tab", "Available balance"), ("Home navigation path", "Transactions"), ("Payments navigation path", "Demo payment validation"),
      ("History navigation path", "Payment recording"), ("Profile navigation path", "Application data")]
S.append(slide("Part 6 &middot; Navigation state versus business state (section 17)", "Where the user goes; what the app knows", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {tbl(["NPayRouter", "NPayStore"], RS, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="rule step" data-label="Router">{ul("Decides <b>where</b> the user goes")}</div>
        <div class="rule step" data-label="Store">{ul("Manages <b>what</b> the application knows")}</div>
        <div class="step">{card("Neither", ul("takes over the other&rsquo;s job"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Two separate objects. NPayRouter: the selected tab and the four navigation paths. NPayStore: the balance, the transactions, payment validation and recording: the application&rsquo;s data.'),
                  ('SAY', 'Click: the router decides where the user goes. Click: the store manages what the application knows. Click: neither should take over the other&rsquo;s responsibilities. The payment screen asks the store to record a payment and the router to show success; the store never navigates, and the router never touches money. The routing Q&amp;A in 3.2 drew the same boundary.'),
                  ('CONNECT', 'Now the complete app.'))))

# ================================================================== Part 7 (9, 10, 18, 19 + complete code)
divider(7, "NPay after Lesson 3.3", "The complete four-tab app", 'Files, screens and a verified run.', 'The architecture.')
AR = [("app", "NPayApp", "WindowGroup { NPayRootView() }"), ("layers", "NPayRootView", "owns NPayRouter + NPayStore")]
P = []
for i, (ic, t, sub) in enumerate(AR):
    P.append(box(160, i * 70, 520, 54, t, sub, None, 'lit' if i == 1 else '', ic))
P.append(wire('M420 56V66' + head(420, 66, 'd')))
for i, (t, d) in enumerate([('Home', 'balance, dashboard'), ('Payments', 'form, confirmation'), ('History', 'transactions'), ('Profile', 'user settings')]):
    x = i * 215
    P.append(wire(f'M420 126V140H{x + 100}V158' + head(x + 100, 158, 'd')))
    P.append(box(x, 162, 200, 56, t, d, None, ''))
TREE = """NPay/
├── NPayApp.swift
├── App/
│   ├── NPayRootView.swift
│   └── NPayRouter.swift       NPayTab, NPayRoute, router
├── Models/        Money, Transaction
├── Store/
│   └── NPayStore.swift
├── Components/    BalanceCard, TransactionRow
└── Screens/
    ├── HomeScreen.swift            + AccountDetailsScreen
    ├── PaymentsScreen.swift
    ├── PaymentSuccessScreen.swift
    ├── HistoryScreen.swift
    ├── TransactionDetailScreen.swift
    └── ProfileScreen.swift         + SettingsScreen"""
S.append(slide("Part 7 &middot; Architecture checkpoint (sections 10, 18; complete code)", "From ContentView to a root, a router and a store", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:24px;align-items:start">
      {svg('0 0 845 218', 'NPayApp, NPayRootView owning router and store, four tabs', 'ar3', P, 'max-height:230px')}
      <div class="step">{code("Project (authored from the text&rsquo;s structure)", TREE, "font-size:11.5px")}</div>
    </div>
  </div>""", notes(('SAY', 'The architecture after 3.3. NPayApp&rsquo;s WindowGroup now launches NPayRootView instead of ContentView, the text&rsquo;s Section 10. The root view owns the router and the store. Under it, four tabs: Home with the balance and dashboard, Payments with the form and confirmation, History with the transactions, Profile with user settings.'),
                  ('SAY', 'Click: the project. The text listed this structure with a complete-code ZIP that we did not receive, so we wrote the files from the text&rsquo;s sections and the 3.2 code; it is all in the lesson text file and ran unchanged in the simulator. Two small extra screens live beside their tabs: AccountDetailsScreen in HomeScreen.swift, SettingsScreen in ProfileScreen.swift. The balance editor from Unit 2 is not in the structure, so it is gone.'),
                  ('CONNECT', 'One mapping from route to screen.'))))

DEST = """// NPayRootView: each tab's root registers the same mapping
HomeScreen(store: store, router: router)
    .navigationDestination(for: NPayRoute.self,
                           destination: destination)

@ViewBuilder
private func destination(_ route: NPayRoute) -> some View {
    switch route {
    case .accountDetails:
        AccountDetailsScreen(balancePaise: store.balancePaise)
    case .paymentSuccess(let id):
        PaymentSuccessScreen(transactionID: id,
                             onDone: { router.returnHome() })
    case .transactionDetails(let id):
        if let transaction = store.transactions.first(where: { $0.id == id }) {
            TransactionDetailScreen(transaction: transaction)
        } else {
            ContentUnavailableView("Transaction not found",
                                   systemImage: "questionmark.circle")
        }
    case .settings:
        SettingsScreen()
    }
}"""
S.append(slide("Part 7 &middot; Resolving routes (complete code, authored)", "Every stack, one <code>destination</code> function", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:24px;align-items:start">
      {code("App/NPayRootView.swift", DEST, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Why one function", ul("Any tab can show any route", "Registered on each stack&rsquo;s root"))}
        <div class="step">{card("IDs resolved by the owner", ul("<code>.transactionDetails(id)</code> &rarr; the store finds it", "Missing ID: a <code>ContentUnavailableView</code>"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'With four stacks, each one needs navigationDestination for NPayRoute. Rather than four copies of the switch, our complete code has one destination function in the root view, passed to each stack&rsquo;s root. Account details shows the balance; payment success gets its ID and an onDone that calls router.returnHome(); settings shows SettingsScreen.'),
                  ('SAY', 'Click: transaction details is 3.2&rsquo;s "carry an ID" idea paying off: the route holds only the UUID, and the store, the owner of the data, looks the transaction up. If the ID is not found, ContentUnavailableView shows a standard empty state instead of crashing.'),
                  ('CONNECT', 'Run the payment across tabs.'))))

PAYC = """Button("Send Demo Payment") {
    guard let amount = parsedAmount else { return }
    if let id = store.recordDemoPayment(
        recipient: recipient, amountPaise: amount) {
        focusedField = nil
        recipient = ""
        amountText = ""
        router.showPaymentSuccess(id)
    }
}"""
S.append(slide("Part 7 &middot; Payments tab: record, then route (complete code)", "The store records; the router navigates", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 125px 125px 125px;gap:14px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Screens/PaymentsScreen.swift (button)", PAYC, "font-size:12px")}
        <div class="step">{console("Router state, simulator", ["paymentsPath: [paymentSuccess(CB81C78F…)]", "Back to Dashboard &rarr; selectedTab: home, paymentsPath: []"], 12)}</div>
      </div>
      {PHONE("img/typed.png", "Payments tab", 125)}
      <div class="step">{PHONE("img/success.png", "Success, same tab", 125)}</div>
      <div class="step">{PHONE("img/homeafter.png", "Home: ₹23,499.50", 125)}</div>
    </div>
  </div>""", notes(('SAY', 'PaymentsScreen is 3.2&rsquo;s PaymentScreen turned into a tab: it reads the balance from the store and has two collaborators. The button asks the store to record the payment and, with the returned ID, clears the form, a choice of ours because the tab stays alive, and asks the router to show success.'),
                  ('SAY', 'On the right, ₹1,500.50 to ravi@npay on the Payments tab. Click: the router printed paymentsPath with the success route; the success screen appears inside the Payments tab, tab bar still visible. Click: Back to Dashboard calls returnHome: the payments path empties and Home is selected, showing ₹23,499.50 with "Sent to ravi@npay" on top.'),
                  ('SAY', 'One detail from our trace: returnHome clears only the payments path. When Home was left on Account Details, Back to Dashboard landed on Account Details, now showing ₹23,499.50. If "dashboard" must mean Home&rsquo;s root, returnHome should clear homePath too. A design decision for you.'),
                  ('CONNECT', 'History and the transaction details.'))))

HIS = """struct HistoryScreen: View {
    let transactions: [Transaction]

    var body: some View {
        List(transactions) { transaction in
            NavigationLink(value: NPayRoute.transactionDetails(transaction.id)) {
                TransactionRow(transaction: transaction)
            }
        }
        .navigationTitle("History")
    }
}"""
S.append(slide("Part 7 &middot; History &rarr; transaction details (complete code)", "A value link appends to the History path", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 140px 140px;gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("Screens/HistoryScreen.swift", HIS, "font-size:12px")}
        <div class="step">{card("<code>NavigationLink(value:)</code>", ul("A link that carries a <b>route</b>, not a view", "Tapping appends it to the enclosing stack&rsquo;s path"))}</div>
      </div>
      {PHONE("img/history.png", "History tab", 140)}
      <div class="step">{PHONE("img/detail.png", "Transaction", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'History needs to push transaction details, but HistoryScreen gets only the transactions, not the router. A value-based NavigationLink fits: NavigationLink(value:) carries a route instead of a destination view. When tapped, it appends that value to the path of the stack it is in: here historyPath. The 3.1 destination closure is replaced by the route, resolved by our destination function. This form of link is ours, not the text&rsquo;s.'),
                  ('SAY', 'On the right, History after the payment: "Sent to ravi@npay" on top, each row with a disclosure chevron. Click: the detail for that row: title, amount, date and ID, looked up in the store by ID.'),
                  ('CONNECT', 'The text&rsquo;s five checks.'))))

VER = [("1. Switch Home, Payments, History, Profile", "all four, tab bar always visible"), ("2. Send a demo payment of ₹1,500.50", "Payment Recorded, in the Payments tab"),
       ("3. Updated balance", "₹23,499.50 on Home"), ("4. History &rarr; select the transaction", "Sent to ravi@npay, -₹1,500.50"),
       ("5. Back to Home: shared state kept", "₹23,499.50, Sent to ravi@npay on top")]
S.append(slide("Part 7 &middot; Verify these five behaviors (complete code)", "Five checks, all run", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 140px 140px;gap:20px;align-items:start">
      <div>{tbl(["Check", "Simulator"], VER, 'tbl')}
        <p class="small muted" style="margin:6px 0 0">The text&rsquo;s ZIP was not shared; this is the authored complete code in the lesson text file.</p></div>
      {PHONE("img/profile.png", "Profile", 140)}
      <div class="step">{PHONE("img/settings.png", "Profile &rarr; Settings", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'The five behaviours the text asks you to verify, all run against the complete code. All four tabs switch with the tab bar always visible. A payment of ₹1,500.50 records and shows Payment Recorded inside the Payments tab. Home shows ₹23,499.50. In History, selecting the new transaction shows its details. And back on Home the shared state is intact.'),
                  ('SAY', 'On the right, the Profile tab: the demo user and a Settings row. Click: Settings, pushed on the Profile stack. Its toggle is local view state; nothing is saved.'),
                  ('CONNECT', 'The text&rsquo;s completion checklist.'))))

CK = [("TabView versus NavigationStack", "Part 2"), ("selectedTab and <code>.tag()</code>", "Part 3"), ("The NPayTab enum", "Part 3"),
      ("Independent navigation paths", "Part 4"), ("NPayRouter&rsquo;s responsibility", "Parts 4, 6"), ("Shared NPayStore ownership", "Part 6"),
      ("Business state stays out of the router", "Part 6"), ("The root architecture", "Part 7")]
S.append(slide("Part 7 &middot; Lesson 3.3 completion checklist (section 19)", "Eight items, and where we covered them", f"""  <div class="body">
    {tbl(["Checklist item", "Covered in"], CK, 'tbl')}
  </div>""", notes(('SAY', 'The text&rsquo;s checklist: TabView versus NavigationStack; selectedTab and tag; the NPayTab enum; independent navigation paths; the router&rsquo;s responsibility; shared store ownership; why business state does not belong in the router; and the root architecture. If any item feels shaky, the right column says where to look again.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.3', (), [("grid", "Tabs switch, stacks deepen", "TabView: which section; NavigationStack: how deep"),
                     ("layers", "One path per tab", "a router: selection + four paths"),
                     ("db", "One store, observed", "readers update; router and store stay separate")],
         'Three things to remember. TabView answers which major section is active and NavigationStack answers how deep we are within it; selection is state, written by taps or by code. Each tab gets its own navigation path in one router, so every section keeps its place. And shared data lives in one observable store that the root owns: Observation updates the views that read what changed, and the router decides where while the store decides what.')

review_divider(9)
review([("grid", "Choose one", "What is TabView primarily responsible for?",
         "What is <code>TabView</code> primarily responsible for?<br>A. Pushing a route onto a navigation stack<br>B. Switching major application sections<br>C. Performing network requests", "B",
         "Tabs switch sections; stacks push screens.",
         "Mixing up tabs and stacks.", "Most pick B.", None),
        ("code", "Choose one", "What does .tag(NPayTab.history) provide?",
         "What does <code>.tag(NPayTab.history)</code> provide?<br>A. A database ID<br>B. A thread identifier<br>C. A tab selection value", "C",
         "SwiftUI writes it into <code>selectedTab</code> when the tab is chosen.",
         "Thinking tags are data IDs.", "Most pick C.", None),
        ("diff", "Question", "Does selectedTab = .history push a route?",
         "Does changing <code>selectedTab</code> to <code>.history</code> necessarily push a NavigationStack route?", "No",
         "It switched sections; no path changed.",
         "Treating every move as a push.", "Some say yes.", None),
        ("layers", "Question", "Can each tab contain its own NavigationStack?",
         "Can each tab contain its own <code>NavigationStack</code>?", "Yes",
         "NPay has four, bound to four paths.",
         "Expecting one stack for the app.", "Most say yes.", None),
        ("clock", "Question", "Should a payment draft's lifetime be designed?",
         "Should payment draft state lifetime be designed explicitly?", "Yes",
         "Our run kept it, but that isn&rsquo;t a guarantee; give it an owner (3.5).",
         "Relying on observed behaviour.", "Most say yes.", None),
        ("eye", "Predict the result", "Home → Account Details, History, back to Home?",
         "On Home you open Account Details, switch to History, open a transaction, then select Home again. What does Home show?<br>A. Its root dashboard<br>B. Account Details<br>C. The transaction", "B",
         "Home&rsquo;s own path still held <code>[accountDetails]</code>.",
         "Thinking a tab switch resets the stack.", "Some pick A.", None),
        ("db", "Predict the result", "After a payment, which tab body did not re-run?",
         "Three tabs read <code>balancePaise</code>, <code>transactions</code> and <code>profileName</code>. A payment changes the first two. Which body was <b>not</b> re-evaluated?<br>A. The balance tab<br>B. The transactions tab<br>C. The profile-name tab", "C",
         "Observation re-ran only the readers of changed properties.",
         "Assuming every tab redraws.", "Some pick B (off screen).", None),
        ("shield", "Choose one", "Where does payment validation belong?",
         "Where does demo payment validation belong?<br>A. <code>NPayRouter</code><br>B. <code>NPayStore</code><br>C. <code>TabView</code>", "B",
         "The store manages what the app knows; the router only where the user goes.",
         "Letting the router do business logic.", "Most pick B.", None),
        ("key", "Choose one", "From 3.2: why does a route carry an ID?",
         "From Lesson 3.2: why does <code>.transactionDetails(UUID)</code> carry an ID instead of the Transaction?<br>A. IDs are faster to draw<br>B. The owner resolves the data; the route only identifies it<br>C. Transactions can&rsquo;t be Hashable", "B",
         "Our destination looks the ID up in the store.",
         "Copying whole objects into routes.", "Most pick B.", "Spaced review from Lesson 3.2.")])

S.append(next_slide('3.3', [("3.4", "Sheets, alerts &amp; modal presentation", "a payment review flow over the current hierarchy"),
                            ("3.5", "Draft state across navigation", "a deliberate owner for the payment draft"),
                            ("Unit 4", "Observation in depth, MVVM, DI", "the store and router as injected dependencies")],
                    'Lesson 3.4 builds a payment review flow with sheets and alerts, temporary screens presented over the current navigation hierarchy. Lesson 3.5 gives the payment draft a deliberate owner. Unit 4 studies Observation in depth and turns the store and router into properly injected dependencies.'))

S.append(lab_slide('3.3', "NPay goes four-tab", "Build the complete 3.3 project; verify, then measure.",
                   ["Add NPayTab, NPayRoute, NPayRouter, NPayStore.",
                    "Create NPayRootView; launch it from NPayApp.",
                    "Run the five checks with ₹1,500.50.",
                    "Home → Account Details, History, back: where?",
                    "Print body/onAppear per tab; switch tabs.",
                    "Decide: should returnHome clear homePath?"],
                   "", 'Expected, as in our run: four tabs; ₹1,500.50 records on Payments and Back to Dashboard shows ₹23,499.50 on Home; History shows the transaction details; Home keeps Account Details across tab switches; each tab is built on first selection and keeps its state; returnHome clears only the payments path, so Home can stay on Account Details.',
                   side=f'<div>{card("You hand in", ul("Your five-check results", "Your tab lifetime log", "Your returnHome decision, with a reason"))}</div>'))

end_slide('3.3', 'TabView: Building<br>NPay&rsquo;s Main Navigation', 'Lesson 3.4 &mdash; Sheets, Alerts &amp; Modal Presentation',
          'You can now explain how TabView differs from NavigationStack, drive the selected tab with state and tags, give each tab its own path in a router, describe what tab switching did to view state and why drafts need a deliberate owner, share one observable store across tabs, and keep navigation state apart from business state.',
          'Next, Lesson 3.4: sheets, alerts and modal presentation. We build NPay&rsquo;s payment review flow over the current navigation hierarchy.')

write_deck(OUT33, '3.3', 'TabView', 'TabView')
