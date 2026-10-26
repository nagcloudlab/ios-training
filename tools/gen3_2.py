"""Generates decks/unit-3/lesson-3.2/index.html from the Lesson 3.2 text (Typed Routes & Programmatic Navigation).
The text came in three pieces (Sections 1-14; a Q&A "don't we have a routing module?" 1-5; a note about a complete
project ZIP that was not shared), grouped into 8 Parts. The complete code through 3.2 is assembled from the text's
snippets onto the 3.1 complete code (flagged). Console output and screenshots come from tools/sim3_2 (iOS Simulator,
module named NPay) and two Mac runs (route printing and the empty-path trap; the non-Hashable compiler error)."""
import html, os, re, sys
OUT32 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

ID = 'DFE60279-893C-4480-8F7F-B5B92F57ED87'   # the transaction ID from the simulator run
R = lambda *xs: '[' + ', '.join(f'NPay.NPayRoute.{x}' for x in xs) + ']'

title_slide('3.2', 'Typed Routes &amp;<br>Programmatic Navigation',
            'After a payment, NPay moves to a <b>success screen by itself</b>. Nobody taps a link: the app changes its <b>navigation state</b>.',
            'Lesson 3.1 navigated when the user tapped a NavigationLink. Today a new requirement: after a successful demo payment, NPay must show a Payment Success screen on its own. There is no link to tap; application logic has to start the navigation. The answer is to model navigation as state: a typed route enum, a path array bound to the NavigationStack, and navigationDestination to turn routes into screens. We ran every step in the simulator.')
outcomes_slide('3.2', [("diff", "Why <b>destination links</b> can&rsquo;t start navigation from code"),
                       ("code", "Model destinations as a <b>typed route</b> enum, and why it is <code>Hashable</code>"),
                       ("layers", "Drive the stack with a <b>path</b>: append, removeLast, removeAll"),
                       ("link", "Map routes to screens with <code>navigationDestination</code>"),
                       ("check", "Navigate to Payment Success when the payment <b>returns an ID</b>"),
                       ("gear", "<code>[NPayRoute]</code> vs <code>NavigationPath</code>, and when to add a router")])
where_slide('3.2', 'Today: navigation driven by state', (),
            '3.1: NavigationStack and NavigationLink: three screens, one state owner.',
            'A route enum and a path: the app navigates after a payment.',
            'Lesson 3.1 gave NPay three screens with destination links. Today the navigation itself becomes state the app can change. Next lesson: TabView.',
            'The new requirement.')

# ================================================================== Part 1 (intro, 1)
divider(1, "The new requirement", "The app must navigate by itself", 'After a payment, show a success screen. No link to tap.', 'The journey.')
J = [("layout", "Dashboard", "user chooses Send Money"), ("file", "Payment screen", "₹1,500.50 to ravi@npay"), ("gear", "Processing", "local demo records it"),
     ("check", "Payment Success", "app navigates itself"), ("layout", "Dashboard", "updated balance")]
P = []
for i, (ic, t, sub) in enumerate(J):
    x = i * 228
    P.append(tall(x, 0, 208, 112, ic, t, sub, None, 'lit' if i == 3 else ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 56H{x + 226}' + head(x + 226, 56, 'r')))
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "A step no user taps", f"""  <div class="body">
    {svg('0 0 1120 112', 'Dashboard, payment screen, processing, payment success, back to the dashboard', 'jr', P, 'max-height:124px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The question", ul("No <code>NavigationLink</code> to activate", "How does SwiftUI navigate in response to <b>application logic</b>?"))}
        <div class="step">{card("What stays", ul("Balance, transactions, editor, form: unchanged", "Only the <b>navigation</b> changes"))}</div>
      </div>
      {PHONE("img/before.png", "3.1: an alert", 150)}
      <div class="step">{PHONE("img/success.png", "3.2: a success screen", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The new journey. From the dashboard the user chooses Send Money, enters ₹1,500.50 and a recipient, and the local demo validates and records the payment. Then the step in teal: NPay navigates to a Payment Success screen by itself. From there, back to the dashboard with the updated balance.'),
                  ('SAY', 'The question for today: there is no link for the user to tap. The application must initiate navigation. How does SwiftUI navigate in response to application logic? Click: we keep the balance, the transactions and every Unit 2 feature; only navigation changes.'),
                  ('SAY', 'On the right, where 3.1 ended: an alert on top of the payment screen. Click: where we end today: a real destination, reached from code.'),
                  ('CONNECT', 'Why can&rsquo;t a link do this?'))))

# ================================================================== Part 2 (2, 3)
divider(2, "Navigation as state", "A typed route", 'Name every destination with an enum.', 'Why links are not enough.')
DEST = """NavigationLink {
    PaymentScreen()
} label: {
    Text("Send Money")
}"""
S.append(slide("Part 2 &middot; Why NavigationLink alone isn&rsquo;t enough (section 2)", "Links react to taps; we need code to decide", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Destination-based navigation (3.1)", DEST, "font-size:15px")}
        {out("The link declares where the user goes <b>when they activate it</b>.", "")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("After a payment succeeds", ul("Nothing is tapped", "We must navigate <b>from code</b>"))}</div>
        <div class="step">{card("Not a pile of booleans", ul("One flag per screen doesn&rsquo;t scale", "Model navigation as <b>state</b>"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'What we had: a NavigationLink with its destination inside. That is destination-based navigation: the link declares where the user goes when they activate it. It is perfect for taps.'),
                  ('SAY', 'Click: after a payment succeeds, nothing is tapped. The decision to move comes from code, from the result of the payment.'),
                  ('SAY', 'Click: we could try a boolean per screen, showSuccess, showHistory and so on, but as the app grows those flags multiply and can contradict each other. Instead, we model navigation as state: one value that says which destinations are on the stack.'),
                  ('CONNECT', 'First, a type for destinations.'))))

ROUTE = """enum NPayRoute: Hashable {
    case payment
    case history
    case success(transactionID: UUID)
}"""
S.append(slide("Part 2 &middot; Introducing a typed route (section 3)", "Every destination, named by a type", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("Navigation/NPayRoute.swift", ROUTE, "font-size:16px")}
        {card("Plain Swift (Unit 1)", ul("An enum; <code>success</code> has an <b>associated value</b>", "<code>Hashable</code>: usable as a navigation path value"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{tbl(["Route", "Destination"], [("<code>.payment</code>", "Payment form"), ("<code>.history</code>", "Transactions"), ("<code>.success(id)</code>", "Receipt")])}</div>
        <div class="step">{console("print(path) (Mac run, module NPay)", [R('payment'), R('payment', 'success(transactionID: 6F1C2A9E-…)')], 12.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPayRoute: an ordinary Swift enum, the kind we built in Unit 1, listing the destinations NPay understands. payment and history are plain cases; success carries an associated value, the transaction&rsquo;s identifier. Hashable lets route values take part in SwiftUI&rsquo;s navigation path system.'),
                  ('SAY', 'Click: each route maps to a destination: the payment form, the transactions, a receipt.'),
                  ('SAY', 'Click: routes are just values. We put them in an array and printed it on a Mac, with the module named NPay as in your app: NPay.NPayRoute.payment, then payment and success with its UUID, shortened here.'),
                  ('CONNECT', 'Why does success carry only an ID?'))))

S.append(slide("Part 2 &middot; Why carry an ID? (section 3)", "Identify the destination; don&rsquo;t carry it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("A route says", ul("<b>Which</b> destination", "The data needed to <b>resolve</b> it"))}
        <div class="step">{card("A stable ID, not the Transaction", ul("No coupling to a whole mutable object", "The owner keeps the data; the route points at it"))}</div>
      </div>
      <div class="step">{console("Route equality (Mac run)", [".success(transactionID: id) == .success(transactionID: id)&ensp;&rarr; true", ".success(transactionID: id) == .success(transactionID: UUID())&ensp;&rarr; false"], 12.5)}
        <p class="small muted" style="margin:8px 0 0">Hashable routes compare by case <b>and</b> associated value.</p></div>
    </div>
  </div>""", notes(('SAY', 'Why does the success route carry a transaction ID instead of the whole Transaction? Because navigation should usually identify the destination and the data needed to resolve it, nothing more.'),
                  ('SAY', 'Click: passing a stable ID avoids coupling the route to an entire transaction object, which may change. The state owner, ContentView, keeps the data; the route just points at it.'),
                  ('SAY', 'Click: our Mac run: two success routes with the same ID are equal; with different IDs they are not. A synthesized Hashable route compares the case and its associated value: that is how SwiftUI can tell routes apart in a path.'),
                  ('CONNECT', 'And if we forget Hashable?'))))

NOH = """enum NPayRoute {             // no Hashable
    case payment
    case history
    case success(transactionID: UUID)
}

@State private var path: [NPayRoute] = []
NavigationStack(path: $path) { … }"""
S.append(slide("Part 2 &middot; Hashable is required (section 3)", "Forget <code>Hashable</code>, and the compiler stops you", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Without Hashable", NOH, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("swiftc, iOS 26.5 SDK", err("no exact matches in call to initializer") + mono("note: candidate requires that 'NPayRoute' conform to 'Hashable' (requirement specified as 'Data.Element' : 'Hashable')", 12.5) + '<div class="gap"></div>' + err("instance method 'navigationDestination(for:destination:)' requires that 'NPayRoute' conform to 'Hashable'"))}</div>
        <div class="tip step" data-label="Detail">{ul("Without <code>success(UUID)</code> it compiles: an enum with no associated values is Hashable automatically", "Write <code>: Hashable</code> anyway")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'What if the route is not Hashable? We removed the conformance and compiled against the iOS SDK.'),
                  ('SAY', 'Click: two real errors. NavigationStack&rsquo;s path initializer needs a collection whose elements are Hashable: "candidate requires that NPayRoute conform to Hashable". And navigationDestination(for:) has the same requirement.'),
                  ('SAY', 'Click: a detail we found on the way: with only payment and history, no associated values, it compiled, because Swift makes simple enums Equatable and Hashable automatically. The associated UUID is what needs the declared conformance. Declare it anyway; it states the intent.'),
                  ('CONNECT', 'Now bind a path of routes to the stack.'))))

# ================================================================== Part 3 (4, 5, 7, 13.5)
divider(3, "The navigation path", "An array of routes", 'NavigationStack(path:) reads and writes it.', 'The binding.')
PATH = """@State private var path: [NPayRoute] = []

NavigationStack(path: $path) {
    // Dashboard
}"""
S.append(slide("Part 3 &middot; NavigationStack with a path (section 4)", "The array <b>is</b> the stack above the root", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("ContentView", PATH, "font-size:15px")}
        {card("<code>$path</code>", ul("A <b>binding</b> to the array", "The stack can read <b>and update</b> it"))}
      </div>
      <div class="step">{tbl(["Path", "Showing"], [("<code>[]</code>", "the root: Dashboard"), ("<code>[.payment]</code>", "Payment"), ("<code>[.payment, .success(transactionID: id)]</code>", "Success, above Payment")], 'tbl')}
        <div class="gap"></div>
        <div class="rule" data-label="So">{ul("The array models the destinations <b>above the root</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Two pieces. A @State array of routes, starting empty. And NavigationStack with path: $path. Notice the dollar sign: a binding, as in Lesson 2.9. The stack can read the array to know what to show, and update it when the user navigates, for example with the back button.'),
                  ('SAY', 'Click: what the array means. Empty: just the root, the dashboard. After navigating to Payment: [.payment]. After the success screen: [.payment, .success(transactionID: id)]. The array models the destinations above the root; the last element is the visible screen.'),
                  ('CONNECT', 'Let&rsquo;s watch the array change.'))))

XP = [("Open Payment", "<code>[.payment]</code>"), ("Show success", "<code>[.payment, .success(transactionID: 6F1C2A9E-…)]</code>"),
      ("Home (<code>removeAll</code>)", "<code>[]</code>"), ("Payment, then History (two appends)", "<code>[.payment, .history]</code>: Depth 2"),
      ("System Back", "<code>[.payment]</code>: Depth 1"), ("Pop (guarded)", "<code>[]</code>"), ("Pop at root (guarded)", "no change")]
S.append(slide("Part 3 &middot; Navigation-path explorer (sections 5, 13)", "Push appends; pop removes; home clears", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 160px;gap:24px;align-items:start">
      <div>{tbl(["Action", "New path (onChange, simulator)"], XP)}
        <p class="small muted" style="margin:6px 0 0">Printed by <code>.onChange(of: path)</code>; module prefix <code>NPay.NPayRoute</code> omitted.</p></div>
      <div class="step">{PHONE("img/two.png", "After two appends", 160)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s interactive explorer, replaced by a real one: a lab screen with buttons that change the path, and the onChange debugging tip from Section 13 printing the old and new path after each action.'),
                  ('SAY', 'Open Payment appends: [.payment]. Show success appends again. Home calls removeAll: back to an empty path, the root. Then experiment 5 from the text: append two routes in one action. One change, [.payment, .history], and the stack shows History at depth 2, directly. Click: the screenshot.'),
                  ('SAY', 'Then the system Back: the path lost its last element, [.payment]. We did not write that; the stack updated our array through the binding. A guarded pop emptied it; a guarded pop at the root did nothing. Pushing appends a route; popping removes the last route; returning home clears the path.'),
                  ('CONNECT', 'The operations, and the one that can crash.'))))

OPS = """path.append(.payment)                          // to Payment
path.append(.history)                          // to History
path.append(.success(transactionID: id))       // to Success
path.removeLast()                              // back one
path.removeAll()                               // to the dashboard

if !path.isEmpty {                             // safe back
    path.removeLast()
}"""
S.append(slide("Part 3 &middot; Programmatic navigation (section 7)", "Five operations on an array", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:24px;align-items:start">
      {code("Navigate from code", OPS, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Just array methods", ul("Navigation becomes ordinary <b>Swift</b>", "Testable without a screen"))}
        <div class="warn step" data-label="removeLast on []">{mono("Fatal error: Can&rsquo;t remove last element from an empty collection", 13.5)}<p class="small" style="margin:6px 0 0">Mac run: the guard skipped it; the unguarded call trapped.</p></div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Navigating from code is now array manipulation. append(.payment) pushes Payment. append(.history) pushes History. append(.success(transactionID: id)) pushes the receipt. removeLast goes back one destination. removeAll returns to the dashboard. Nothing here mentions a view controller.'),
                  ('SAY', 'Click: the safety detail. removeLast on an empty array is a runtime trap. We ran it on a Mac: the guarded version did nothing, the unguarded one crashed with "Can&rsquo;t remove last element from an empty collection". Guard it when the path might be empty.'),
                  ('CONNECT', 'The stack knows the routes. How does it know the screens?'))))

# ================================================================== Part 4 (6)
divider(4, "Register destinations", "Routes in, views out", 'navigationDestination maps each route to a view.', 'The mapping.')
ND = """.navigationDestination(for: NPayRoute.self) { route in
    switch route {
    case .payment:
        PaymentScreen()

    case .history:
        HistoryScreen()

    case .success(let transactionID):
        PaymentSuccessScreen(
            transactionID: transactionID
        )
    }
}"""
S.append(slide("Part 4 &middot; Register destinations with navigationDestination (section 6)", "One <code>switch</code>, every screen", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("The routing structure", ND, "font-size:13.5px")}
        <p class="small muted" style="margin:8px 0 0">Structure only: the real initializers still take 3.1&rsquo;s dependencies.</p></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("What happens", ul("SwiftUI associates the route <b>type</b> with a destination builder", "When a route becomes active, it builds the view", "The route: a typed description of <b>intent</b>"))}</div>
        <div class="step">{console("SDK (simplified)", ["func navigationDestination&lt;D, C&gt;(for data: D.Type,", "&ensp;&ensp;@ViewBuilder destination: @escaping (D) -&gt; C) -&gt; some View", "&ensp;&ensp;where D : Hashable, C : View"], 12.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI needs to know which view corresponds to each route, so we register a mapping: navigationDestination for NPayRoute.self, with a closure that receives a route and switches over it. The switch is exhaustive: add a route case and the compiler makes you handle it. This shows the routing structure; the real screens still need the balance, transactions and closures from 3.1, which we add in Part 6.'),
                  ('SAY', 'Click: conceptually, SwiftUI associates the route type with a destination builder; when a route becomes active, it builds the matching view. The route is a typed description of navigation intent.'),
                  ('SAY', 'Click: the SDK declaration: generic over the data type D, which must be Hashable, and the destination view C, built by an escaping closure. Escaping because SwiftUI calls it later, whenever a route needs a view.'),
                  ('CONNECT', 'What if a value has no registration?'))))

S.append(slide("Part 4 &middot; A value with no destination (section 6, authored experiment)", "Unregistered type: a warning, not a screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 160px;gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Experiment", ul("A path holding <code>NPayRoute</code>, <code>42</code> and <code>\"ravi@npay\"</code>", "Destinations registered for <code>NPayRoute</code> and <code>Int</code> only"))}
        <div class="step">{console("Simulator", ["count: 3", "top: String, no destination &rarr; yellow warning symbol", "Back &rarr; count 2: \"Int destination #42\""], 13.5)}</div>
        <div class="rule step" data-label="So">{ul("Every value type you push needs a <code>navigationDestination</code>", "Register it inside the stack, on the root content")}</div>
      </div>
      <div class="step">{PHONE("img/mixed.png", "No String destination", 160)}</div>
    </div>
  </div>""", notes(('SAY', 'Our own experiment, to see what registration really does. A path that holds a route, an Int and a String, with destinations registered for the route type and for Int, but not for String. That mixed path needs NavigationPath, the topic of Part 5.'),
                  ('SAY', 'Click: count 3, and the top value is the String, which has no registered destination. Click: SwiftUI pushes a screen with only a yellow warning symbol. After Back, the Int is on top and its destination appears: "Int destination #42".'),
                  ('SAY', 'Click: so every type you put on the path needs a navigationDestination, placed inside the NavigationStack, typically on the root content, as our dashboard does.'),
                  ('CONNECT', 'NavigationPath, properly.'))))

# ================================================================== Part 5 (8)
divider(5, "NavigationPath", "A type-erased path", 'When the path must hold different Hashable types.', 'The comparison.')
CMP = [("<code>[NPayRoute]</code>", "Type-erased path"), ("One route type", "Can hold multiple Hashable types"),
       ("Strong compile-time route modeling", "More flexible heterogeneous routing"), ("Simple <code>switch</code>-based destinations", "Type-specific destination registrations"),
       ("Good for our NPay example", "Useful for more heterogeneous navigation")]
S.append(slide("Part 5 &middot; What is NavigationPath? (section 8)", "Typed array or type-erased path?", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:24px;align-items:start">
      <div>{code("Two ways to declare the path", "@State private var path: [NPayRoute] = []\n@State private var path = NavigationPath()", "font-size:14px")}
        <div class="gap"></div>
        {tbl(["Typed array", "NavigationPath"], CMP, 'tbl')}</div>
      <div class="rule step" data-label="For NPay">{ul("Use <code>[NPayRoute]</code> for now", "Easier to reason about; the route model stays <b>explicit</b>")}</div>
    </div>
  </div>""", notes(('SAY', 'So far: an array of NPayRoute. SwiftUI also provides NavigationPath, a type-erased path that can hold Hashable values of different types: for example, routes from several features, or plain identifiers.'),
                  ('SAY', 'The trade-off. The typed array has one route type, strong compile-time modelling, and one exhaustive switch. NavigationPath is more flexible: any Hashable values, each type with its own destination registration. Good for heterogeneous navigation.'),
                  ('SAY', 'Click: the recommendation for NPay: use the typed array for now. It is easier to reason about and keeps the route model explicit.'),
                  ('CONNECT', 'What NavigationPath gives up.'))))

NP = """public struct NavigationPath {
    public var count: Int { get }
    public var isEmpty: Bool { get }
    public var codable: CodableRepresentation? { get }
    public init()
    public mutating func append&lt;V&gt;(_ value: V) where V : Hashable
    public mutating func removeLast(_ k: Int = 1)
}"""
S.append(slide("Part 5 &middot; Inside NavigationPath (section 8, SDK)", "What you can do with an erased path", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {console("iOS 26.5 SDK, SwiftUI interface (simplified)", [NP.replace(chr(10), '<br>').replace('    ', '&ensp;&ensp;')], 12.5)}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{tbl(["Need", "<code>[NPayRoute]</code>", "<code>NavigationPath</code>"], [("Read the routes", "yes", "no: only <code>count</code>"), ("Back to root", "<code>removeAll()</code>", "<code>removeLast(path.count)</code>"), ("Mixed types", "no", "yes")])}</div>
        <div class="tip step" data-label="codable">{ul("Non-nil when every value is <code>Codable</code>: a way to save and restore navigation")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The NavigationPath declaration from the SDK, simplified: count, isEmpty, an optional codable representation, append for any Hashable value, and removeLast with a count. Notice what is missing.'),
                  ('SAY', 'Click: you cannot read the elements back: no subscript, no iteration, only the count. There is no removeAll; to go home you remove count elements, or assign a new empty NavigationPath. And it can hold mixed types, which the array cannot. Another reason the typed array suits NPay: we can print it, inspect it and test it.'),
                  ('SAY', 'Click: the codable property is non-nil when every value in the path is Codable, which is the hook for saving and restoring navigation. We note it here; we do not need it yet.'),
                  ('CONNECT', 'Back to NPay: the success screen.'))))

# ================================================================== Part 6 (9-11 + complete code)
divider(6, "The payment success flow", "Result in, navigation out", 'Payment returns an ID; the parent appends a route.', 'The success screen.')
SUC = """struct PaymentSuccessScreen: View {
    let transactionID: UUID
    let onDone: () -> Void

    var body: some View {
        VStack(spacing: 24) {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 72))
                .foregroundStyle(.green)
            Text("Payment Recorded")
                .font(.title.bold())
            Text("Your demo payment was successful.")
                .foregroundStyle(.secondary)
            Text(transactionID.uuidString)
                .font(.caption2.monospaced())
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)
            Button("Back to Dashboard") { onDone() }
                .buttonStyle(.borderedProminent)
        }
        .padding()
        .navigationTitle("Payment Success")
        .navigationBarBackButtonHidden()
    }
}"""
S.append(slide("Part 6 &middot; Build the Payment Success screen (section 9)", "It receives an ID and a way home", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.62fr) 150px;gap:20px;align-items:start">
      {code("Screens/PaymentSuccessScreen.swift", SUC, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Receives", ul("<code>transactionID</code>", "<code>onDone</code>: a closure"))}
        <div class="step">{card("Doesn&rsquo;t own", ul("The navigation <b>path</b>", "The parent navigates"))}</div>
        <div class="step">{card("No back button", ul("Hidden by a modifier", "Leave with <b>Back to Dashboard</b>"))}</div>
      </div>
      {PHONE("img/success.png", "In the simulator", 150)}
    </div>
  </div>""", notes(('SAY', 'PaymentSuccessScreen.swift: a green checkmark, "Payment Recorded", a line of text, the transaction ID in a small monospaced font, and a Back to Dashboard button. It receives two things: the transaction ID and an onDone closure.'),
                  ('SAY', 'Click: what it does not own: the application&rsquo;s navigation path. Its button calls onDone; the parent decides what that means. The same pattern as onSend in 2.12: data in, requests up.'),
                  ('SAY', 'Click: navigationBarBackButtonHidden removes the back button. Back would land on the payment form again, which makes little sense after paying; the only way out is Back to Dashboard. The screenshot: no back button in the bar.'),
                  ('CONNECT', 'Where does the transaction ID come from?'))))

SEND = """private func sendDemoPayment(
    to recipient: String,
    amountPaise: Int
) -> UUID? {
    let trimmed = recipient.trimmingCharacters(
        in: .whitespacesAndNewlines)
    guard !trimmed.isEmpty,
          amountPaise > 0,
          amountPaise <= balancePaise else {
        return nil
    }
    let transactionID = UUID()
    balancePaise -= amountPaise
    transactions.insert(
        Transaction(id: transactionID,
                    title: "Sent to \\(trimmed)",
                    amountPaise: -amountPaise, date: .now),
        at: 0)
    return transactionID
}"""
S.append(slide("Part 6 &middot; Connect payment success to navigation (section 10)", "From <code>Bool</code> to <code>UUID?</code>", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("ContentView.sendDemoPayment", SEND, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The new contract", ul("<code>nil</code>: rejected", "A <code>UUID</code>: recorded, and <b>which</b> transaction"))}
        <div class="step">{code("Navigation responds to the result", "if let id = sendDemoPayment(\n    to: recipient, amountPaise: amountPaise) {\n    path.append(.success(transactionID: id))\n}", "font-size:12.5px")}</div>
        <div class="rule step" data-label="Why better">{ul("Payment returns a <b>meaningful</b> result", "Navigation responds to it", "Payment logic knows no screens")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'In 3.1 sendDemoPayment returned a Bool. Now we need the transaction ID, so the contract improves: it returns an optional UUID. nil means rejected. On success it creates the ID first, uses it for the inserted transaction, and returns it.'),
                  ('SAY', 'Click: the navigation flow uses it: if let id = sendDemoPayment, append the success route with that ID.'),
                  ('SAY', 'Click: why this is better. Payment processing returns a meaningful result. Navigation responds to that result. And the payment logic does not need to know about SwiftUI screens; it could move into a service in Unit 4 unchanged.'),
                  ('CONNECT', 'The payment form sits between the two. How does it report success?'))))

BTN = """let onSend: (String, Int) -> UUID?
let onPaymentSuccess: (UUID) -> Void

Button("Send Demo Payment") {
    guard let amount = parsedAmount else { return }
    if let transactionID = onSend(recipient, amount) {
        focusedField = nil
        onPaymentSuccess(transactionID)
    }
}"""
FL = [("file", "PaymentScreen", "collects user input"), ("send", "onSend", "requests the demo payment"), ("db", "ContentView", "validates, records"),
      ("key", "Transaction ID", "returned on success"), ("link", "onPaymentSuccess", "requests navigation"), ("layers", "NavigationStack", "shows Success")]
P = [box(0, i * 50, 520, 42, t, sub, str(i + 1), '', ic) for i, (ic, t, sub) in enumerate(FL)]
S.append(slide("Part 6 &middot; How PaymentScreen communicates success (section 11) &middot; conceptual", "Two closures: a request, then a report", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Screens/PaymentScreen.swift (changes)", BTN, "font-size:13px")}
      {svg('0 0 520 292', 'PaymentScreen, onSend, ContentView, transaction ID, onPaymentSuccess, NavigationStack', 'cl', P, 'max-height:310px')}
    </div>
  </div>""", notes(('SAY', 'PaymentScreen&rsquo;s contract changes in two places. onSend now returns an optional UUID. And a second closure, onPaymentSuccess, takes the ID. In the button: if onSend returns an ID, clear focus and call onPaymentSuccess with it. The 3.1 alert and dismiss are gone; the success screen replaces them.'),
                  ('SAY', 'The text&rsquo;s chain, step by step. Click: PaymentScreen collects input. Click: onSend requests the demo payment. Click: ContentView validates and records the transaction. Click: the transaction ID comes back. Click: onPaymentSuccess requests navigation. Click: the NavigationStack displays the success destination. The parent supplies the navigation behaviour; the form never touches the path.'),
                  ('CONNECT', 'Where those closures are created: the registration.'))))

WIRE = """.navigationDestination(for: NPayRoute.self) { route in
    switch route {
    case .payment:
        PaymentScreen(
            availableBalancePaise: balancePaise,
            onSend: sendDemoPayment,
            onPaymentSuccess: { transactionID in
                path.append(.success(transactionID: transactionID))
            })
    case .history:
        HistoryScreen(transactions: transactions)
    case .success(let transactionID):
        PaymentSuccessScreen(
            transactionID: transactionID,
            onDone: { path.removeAll() })
    }
}"""
DASH = """Button {
    path.append(.payment)
} label: {
    Label("Send Money", systemImage: "arrow.up.right")
    // same styling as 3.1
}"""
S.append(slide("Part 6 &middot; Wire it up in ContentView (complete code, authored)", "The registration holds every dependency", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:24px;align-items:start">
      {code("ContentView: destinations", WIRE, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("Dashboard buttons", DASH, "font-size:12px")}
        <div class="step">{card("ContentView owns", ul("Balance, transactions, <b>and the path</b>", "Screens get values and closures"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text gave the pieces; we assembled them into the complete ContentView, flagged as ours. The registration now passes each screen its dependencies. Payment gets the balance, sendDemoPayment as onSend, and an onPaymentSuccess closure that appends the success route. History gets the transactions. Success gets its ID and an onDone that clears the path.'),
                  ('SAY', 'On the right: the dashboard&rsquo;s links became buttons that append routes, styled as in 3.1, as in the text&rsquo;s path.append examples. A value-based NavigationLink, NavigationLink(value:), would also append to the path; we stay with the text&rsquo;s buttons.'),
                  ('SAY', 'Click: ContentView now owns three things: the balance, the transactions and the navigation path. Every screen receives values and closures.'),
                  ('CONNECT', 'Run it: the text&rsquo;s practical test.'))))

S.append(slide("Part 6 &middot; Run the route-based flow (practical test)", "₹1,500.50 to ravi@npay, step by step", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 130px 130px 130px 130px;gap:14px;align-items:start">
      {console("onChange(of: path), simulator", ["tap Send Money", "&ensp;" + R('payment'), "tap Send Demo Payment", "&ensp;[….payment, ….success(transactionID:", "&ensp;&ensp;DFE60279-…)]", "tap Back to Dashboard", "&ensp;[]", "tap Transaction History", "&ensp;" + R('history')], 12)}
      {PHONE("img/typed.png", "1500.50 typed", 130)}
      <div class="step">{PHONE("img/success.png", "Success, by code", 130)}</div>
      <div class="step">{PHONE("img/home.png", "₹23,499.50", 130)}</div>
      <div class="step">{PHONE("img/history.png", "History", 130)}</div>
    </div>
  </div>""", notes(('SAY', 'The practical test: send ₹1,500.50 to ravi@npay. Our run, with the path printed after each change. Send Money appended .payment. The left screenshot: the form filled in, Send enabled.'),
                  ('SAY', 'Click: Send Demo Payment: the payment returned an ID and the app appended .success with it; no link was tapped. Click: Back to Dashboard cleared the path: the dashboard shows ₹25,000.00 minus ₹1,500.50, ₹23,499.50. Click: Transaction History appended .history; "Sent to ravi@npay", minus ₹1,500.50, is on top.'),
                  ('CONNECT', 'The whole project, file by file.'))))

TREE = """NPay/
├── NPayApp.swift
├── ContentView.swift          path, destinations, payment
├── Navigation/
│   └── NPayRoute.swift         new
├── Models/            Money, Transaction
├── Components/        BalanceCard, BalanceEditor, TransactionRow
└── Screens/
    ├── PaymentScreen.swift          onSend → UUID?, onPaymentSuccess
    ├── PaymentSuccessScreen.swift   new
    └── HistoryScreen.swift"""
CHK = [("Starting balance", "₹25,000.00"), ("Send ₹1,500.50 to ravi@npay", "Success screen, by code"), ("Back to Dashboard", "₹23,499.50; path []"),
       ("History", "Sent to ravi@npay, -₹1,500.50"), ("Success screen&rsquo;s back button", "hidden")]
S.append(slide("Part 6 &middot; NPay through Lesson 3.2 (complete code, authored)", "Two new files, three changed", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Project", TREE, "font-size:12.5px")}
      <div class="step">{tbl(["Check", "Simulator"], CHK)}
        <p class="small muted" style="margin:8px 0 0">The text described a project ZIP; the code is in this lesson&rsquo;s text file, run in the simulator.</p></div>
    </div>
  </div>""", notes(('SAY', 'The project through Lesson 3.2. New: NPayRoute.swift in a Navigation folder and PaymentSuccessScreen.swift. Changed: ContentView owns the path and registers destinations; PaymentScreen&rsquo;s onSend returns an optional UUID and it reports success through onPaymentSuccess; sendDemoPayment returns the ID. Models and Components are unchanged from 3.1.'),
                  ('SAY', 'Click: our checks. ₹25,000.00 at launch; the payment lands on the success screen by code; Back to Dashboard shows ₹23,499.50 with an empty path; History has the new transaction; the success screen has no back button. The text mentioned a ZIP of the project; we did not receive it, so the complete code is written out in the lesson text file and is exactly what ran.'),
                  ('CONNECT', 'Behind the scenes: why this is just state.'))))

# ================================================================== Part 7 (12, 13)
divider(7, "Navigation is state", "Visible destination = f(path)", 'The same idea as UI = f(State) in Lesson 2.8.', 'The principle.')
S.append(slide("Part 7 &middot; Behind the scenes: navigation is state (section 12)", "UI = f(State), and now navigation too", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 160px;gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        <p style="font-size:30px;margin:0;text-align:center"><b>UI</b> = <i>f</i>(State)&emsp;&rarr;&emsp;<b>Visible destination</b> = <i>f</i>(<span class="mono">path</span>)</p>
        {card("When the path changes", ul("SwiftUI updates the navigation presentation", "The app pushes <b>no</b> view controller; it changes declarative state", "SwiftUI runs the transition"))}
        <div class="step">{console("Authored experiment: launch with a path", ["@State private var path: [NPayRoute] = [.payment, .history]", "launch &rarr; History on screen, Payment below it", "Back &rarr; New path: " + R('payment')], 12.5)}</div>
      </div>
      <div class="step">{PHONE("img/deep.png", "Launched deep", 160)}</div>
    </div>
  </div>""", notes(('SAY', 'Lesson 2.8: UI is a function of state. Navigation follows the same principle: the visible destination is a function of the navigation path. When the path changes, SwiftUI updates the navigation presentation. The app is not directly pushing a UIKit view controller; it changes declarative state, and SwiftUI handles the transition.'),
                  ('SAY', 'Click: our experiment to prove the function. Start the path with two routes, payment and history, instead of empty. Click: the app launches straight into History, with a back button; Back goes to Payment, and the path prints [.payment]. Nobody navigated: the screen was computed from the state. That is also how deep links and restored navigation work.'),
                  ('CONNECT', 'The text&rsquo;s six experiments.'))))

EX = [("1. Empty path, navigate to Payment", "<code>[]</code> &rarr; <code>[.payment]</code>"), ("2. After a payment, append success", "<code>[.payment, .success(…)]</code>, by code"),
      ("3. Print the path after each action", "<code>onChange(of: path)</code>: old and new"), ("4. <code>removeAll()</code> to the dashboard", "<code>[]</code>; the dashboard"),
      ("5. Append two routes in one action", "one change; lands on History, depth 2"), ("6. <code>[NPayRoute]</code> vs <code>NavigationPath</code>", "mixed types, <code>count</code> only (Part 5)")]
ONCH = """.onChange(of: path) { oldPath, newPath in
    print("Old path:", oldPath)
    print("New path:", newPath)
}"""
S.append(slide("Part 7 &middot; Xcode experiments (section 13)", "Six experiments, six results", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:24px;align-items:start">
      {tbl(["Experiment", "Simulator"], EX)}
      <div class="step">{code("Debugging tip", ONCH, "font-size:12.5px")}
        <p class="small muted" style="margin:8px 0 0">Our complete ContentView keeps this, so you can watch navigation state evolve.</p></div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s six experiments and what each gave us. Navigating from an empty path appended .payment. After a payment, the success route was appended by code. Printing the path after each action showed every step. removeAll returned to the dashboard. Two appends in one action produced a single change and went straight to History at depth 2. And NavigationPath took mixed types but only exposes a count.'),
                  ('SAY', 'Click: the debugging tip: onChange of path with the old and new values. We kept it in the complete ContentView; remove it before shipping.'),
                  ('CONNECT', 'A question that comes up here: where is the router?'))))

# ================================================================== Part 8 (Q&A 1-5)
divider(8, "Do we need a router?", "Primitives first, a router on top", 'SwiftUI has navigation, but no Router class.', 'The comparison.')
RC = [("Angular", "Angular Router"), ("React", "React Router (external library)"), ("Flutter", "Navigator / Router"),
      ("SwiftUI", "<code>NavigationStack</code> + <code>navigationDestination</code>"), ("UIKit", "<code>UINavigationController</code>")]
S.append(slide("Part 8 &middot; Don&rsquo;t we have a routing module? (Q&amp;A 1&ndash;2)", "Navigation built in; no Router class", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {tbl(["Framework", "Routing mechanism"], RC, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("In SwiftUI", ul("<code>import SwiftUI</code>: no router package", "Primitives: stack, path, destinations"))}
        <div class="step">{card("A Router class?", ul("Not built in at app level", "You can <b>build your own</b> on the primitives"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A question from the lesson discussion: don&rsquo;t we have a routing module, like Angular Router or React Router? Angular ships its router; React uses an external library; Flutter has Navigator and Router. In SwiftUI, navigation is part of the framework: NavigationStack and navigationDestination. In UIKit, UINavigationController.'),
                  ('SAY', 'Click: so there is no separate router package and no built-in application-level Router class. SwiftUI provides the navigation primitives, and we can build our own router on top to centralise navigation.'),
                  ('CONNECT', 'What that looks like.'))))

ROUTER = """@MainActor
@Observable
final class NPayRouter {
    var path: [NPayRoute] = []

    func push(_ route: NPayRoute) {
        path.append(route)
    }

    func pop() {
        guard !path.isEmpty else { return }
        path.removeLast()
    }

    func popToRoot() {
        path.removeAll()
    }
}"""
USE = """@State private var router = NPayRouter()

var body: some View {
    @Bindable var router = router

    NavigationStack(path: $router.path) {
        VStack(spacing: 20) {
            Button("Send Money") { router.push(.payment) }
            Button("History") { router.push(.history) }
        }
        .navigationDestination(for: NPayRoute.self) { route in
            switch route {
            case .payment: Text("Payment Screen")
            case .history: Text("History Screen")
            case .success(let id):
                Text("Payment Success: \\(id.uuidString)")
            }
        }
    }
}"""
S.append(slide("Part 8 &middot; A router of our own (Q&amp;A 2&ndash;3)", "The path, moved into an object", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.8fr) minmax(0,1fr) 140px;gap:18px;align-items:start">
      <div>{code("NPayRouter.swift", ROUTER, "font-size:12px")}
        <p class="small muted" style="margin:8px 0 0">Observation framework: iOS 17+.</p></div>
      <div class="step">{code("ContentView", USE, "font-size:11.5px")}</div>
      <div class="step">{PHONE("img/router.png", "After Send Money", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'NPayRouter: a main-actor, @Observable class from Apple&rsquo;s Observation framework, iOS 17 and later. It owns the path array and offers push, a guarded pop, and popToRoot. The same array operations as Part 3, behind names.'),
                  ('SAY', 'Click: connecting it. ContentView owns the router with @State, as the canon does for observable objects. Inside body, @Bindable var router gives us bindings into the object, so $router.path can drive NavigationStack. The buttons call router.push; the destinations are registered as before, here as placeholder Texts.'),
                  ('SAY', 'Click: we ran the Q&amp;A&rsquo;s code unchanged: Send Money pushed "Payment Screen". Today it is enough that the router&rsquo;s path behaves exactly like our @State array.'),
                  ('CONNECT', 'Should NPay have one now?'))))

AR = [("layout", "NPay view", "user taps Send Money"), ("gear", "NPayRouter", "push(.payment)"), ("db", "Navigation path", "stores [.payment]"),
      ("layers", "NavigationStack", "observes the bound path"), ("link", "navigationDestination", ".payment &rarr; PaymentScreen")]
P = []
for i, (ic, t, sub) in enumerate(AR):
    P.append(box(0, i * 56, 470, 46, t, sub, None, 'lit' if i == 1 else '', ic))
    if i < 4:
        P.append(wire(f'M235 {i * 56 + 47}V{i * 56 + 55}' + head(235, i * 56 + 55, 'd')))
FUT = """NPayApp
  +-- NPayRouter
  |     +-- NavigationStack
  |     +-- NavigationPath
  |     +-- Route resolution
  +-- Features
        +-- Dashboard
        +-- Payments
        +-- History
        +-- Profile"""
S.append(slide("Part 8 &middot; Should NPay have a router? (Q&amp;A 4&ndash;5)", "Later: when navigation spans screens and tabs", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {svg('0 0 470 270', 'View, NPayRouter, navigation path, NavigationStack, navigationDestination', 'rt', P, 'max-height:290px')}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{code("Eventually", FUT, "font-size:12px")}</div>
        <div class="rule step" data-label="Boundary">{ul("A router manages <b>where</b> the user goes", "Not payments, not business logic")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The flow with a router: a view asks the router to push .payment; the router stores it in the path; NavigationStack observes the bound path; navigationDestination resolves .payment to PaymentScreen. The router sits where ContentView&rsquo;s @State path sits today.'),
                  ('SAY', 'Click: should NPay have one? Yes, as the app grows, but understand the native primitives first. The suggestion is to introduce NPayRouter when navigation is coordinated across several screens and tabs: then the app owns a router, which owns the stack, the path and route resolution, next to the features: dashboard, payments, history, profile.'),
                  ('SAY', 'Click: one boundary to keep: the router manages where the user goes. Payment processing and business logic stay out of it. Native NavigationStack underneath, our own small abstraction on top, no extra dependencies.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.2', (), [("code", "Routes are values", "a Hashable enum names every destination"),
                     ("layers", "The path is the stack", "append, removeLast, removeAll; the stack writes back"),
                     ("link", "Results drive navigation", "payment returns an ID; the parent appends .success")],
         'Three things to remember. A typed route is a Hashable enum that names each destination, carrying only the data needed to resolve it, like a transaction ID. The path array is the stack above the root: append pushes, removeLast pops, removeAll goes home, and the stack updates the array when the user goes back; navigationDestination maps each route to a view. And application logic drives navigation: the payment returns an ID, the parent appends the success route, and the payment code never knows about screens.')

review_divider(9)
review([("code", "Choose one", "What is a typed navigation route?",
         "What is a typed navigation route?<br>A. A network URL<br>B. A Swift type representing a destination<br>C. A UIKit thread", "B",
         "<code>NPayRoute</code> names each destination as an enum case.",
         "Thinking of routes as URLs.", "Most pick B.", None),
        ("key", "Choose one", "Why does NPayRoute conform to Hashable?",
         "Why does <code>NPayRoute</code> conform to <code>Hashable</code>?<br>A. To enable HTTP requests<br>B. To create animations<br>C. To support navigation path values", "C",
         "Both <code>NavigationStack(path:)</code> and <code>navigationDestination(for:)</code> require it: real compiler errors.",
         "Thinking Hashable is optional.", "Most pick C.", None),
        ("layers", "Choose one", "What does path.append(.payment) do?",
         "What does <code>path.append(.payment)</code> do?<br>A. Adds a navigation destination<br>B. Starts a new process<br>C. Creates a database record", "A",
         "The path is the stack: appending pushes Payment.",
         "Expecting a push call.", "Almost everyone picks A.", None),
        ("layout", "Choose one", "What does path.removeAll() represent?",
         "What does <code>path.removeAll()</code> represent?<br>A. Delete all transactions<br>B. Return to root<br>C. Terminate the app", "B",
         "An empty path shows only the dashboard.",
         "Confusing the path with app data.", "Most pick B.", None),
        ("check", "Choose one", "Why return a transaction ID from payment logic?",
         "Why does <code>sendDemoPayment</code> return a transaction ID?<br>A. To increase the balance<br>B. To create a thread<br>C. To identify the successful transaction", "C",
         "The success route carries it; <code>nil</code> means rejected.",
         "Returning only a Bool.", "Most pick C.", None),
        ("gear", "Question", "Must every NavigationPath element have the same type?",
         "Does <code>NavigationPath</code> require every element to have the same concrete type?", "No",
         "Ours held a route, an <code>Int</code> and a <code>String</code>; count 3.",
         "Mixing it up with <code>[NPayRoute]</code>.", "Some say yes.", None),
        ("diff", "Predict the result", "path after system Back from [.payment, .history]?",
         "The path is <code>[.payment, .history]</code>. The user taps the system back button. What is <code>path</code> now?<br>A. <code>[.payment, .history]</code>: we never changed it<br>B. <code>[.payment]</code><br>C. <code>[]</code>", "B",
         "The stack writes back through <code>$path</code>: onChange printed <code>[.payment]</code>.",
         "Thinking only our code changes the path.", "Some pick A.", None),
        ("shield", "Predict the result", "path.removeLast() on an empty path?",
         "<code>path</code> is <code>[]</code> and code calls <code>path.removeLast()</code>. What happens?<br>A. Nothing<br>B. The app crashes<br>C. It returns <code>nil</code>", "B",
         "&ldquo;Can&rsquo;t remove last element from an empty collection&rdquo;: guard with <code>isEmpty</code>.",
         "Assuming a safe no-op.", "Many pick A.", None),
        ("clock", "Question", "From 3.1: is a popped destination's @State kept?",
         "From Lesson 3.1: after a destination is popped and pushed again, is its <code>@State</code> kept?", "No",
         "The counter went 3 &rarr; 0: popping ends the state lifetime.",
         "Expecting off-screen state to persist.", "Most say no.", "Spaced review from Lesson 3.1.")])

S.append(next_slide('3.2', [("3.3", "TabView &amp; multi-tab navigation", "Home, Payments, History, Profile; consistent shared data"),
                            ("Later", "A router across tabs", "<code>NPayRouter</code> when navigation spans tabs"),
                            ("Unit 4", "Application architecture", "payment logic out of ContentView; the router beside it")],
                    'Lesson 3.3 adds a TabView with Home, Payments, History and Profile tabs while keeping navigation state and shared account data consistent. A router like NPayRouter becomes worthwhile once navigation is coordinated across tabs. Unit 4 moves payment logic out of ContentView; the payment function that returns an ID is already ready for that.'))

S.append(lab_slide('3.2', "Route-based NPay", "Replace links with routes; navigate after a payment.",
                   ["Add <code>NPayRoute</code> and a <code>path</code> to ContentView.",
                    "Register destinations; buttons append routes.",
                    "Return <code>UUID?</code>; add <code>PaymentSuccessScreen</code>.",
                    "Pay ₹1,500.50 to ravi@npay; check the screens.",
                    "Print the path; try two appends, then Back.",
                    "Try <code>NavigationPath</code> with mixed types."],
                   "", 'Expected, as in our run: [.payment], then [.payment, .success(…)] with no tap, then [] after Back to Dashboard with ₹23,499.50 and "Sent to ravi@npay" in History; two appends land on History at depth 2 and the system Back leaves [.payment]; a mixed NavigationPath reports its count, and a type with no destination shows a warning symbol.',
                   side=f'<div>{card("You hand in", ul("Your printed path log for the practical test", "A success-screen screenshot", "One sentence: why the payment returns an ID"))}</div>'))

end_slide('3.2', 'Typed Routes &amp;<br>Programmatic Navigation', 'Lesson 3.3 &mdash; TabView &amp; Multi-Tab Navigation',
          'You can now model destinations as a Hashable route enum, drive a NavigationStack with a path array, register destinations with navigationDestination, navigate from code after a payment returns an ID, choose between an array and NavigationPath, and explain when a router of your own is worth it.',
          'Next, Lesson 3.3: TabView and multi-tab navigation. NPay gets Home, Payments, History and Profile tabs, with navigation state and account data kept consistent.')

write_deck(OUT32, '3.2', 'Typed Routes', 'Typed Routes')
