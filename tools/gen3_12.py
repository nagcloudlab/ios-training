"""Generates decks/unit-3/lesson-3.12/index.html from the Lesson 3.12 text (NPay Final Integration & Architecture Mastery,
the Unit 3 capstone; two parts: Sections 1-6, then Part 2 restarting at Section 4 and running to Section 9). Part 2's
Sections 4-9 supersede Part 1's partial 4-6. Evidence comes from tools/sim3_12: the complete NPay through Unit 3 driven in
the simulator, with every owner's state printed along one ₹1,500.50 payment, the text's 12-item checklist, and History
with 50,000 extra transactions."""
import html, os, re, sys
OUT312 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

title_slide('3.12', 'NPay Final Integration<br>&amp; Architecture',
            'Eleven lessons, one running app. <b>Who owns what</b>, and what happens when a payment goes through.',
            'This is the final lesson of Unit 3. Over eleven lessons we learned SwiftUI concepts one at a time. Today we answer the bigger question: how do they all work together inside one running iOS application? We trace one payment through the whole app, review who owns each piece of state, run the full integration checklist on the real app, and name what should move into MVVM in Unit 4.')
outcomes_slide('3.12', [("layers", "Map every Unit 3 concept to an NPay feature"),
                        ("diff", "Draw NPay&rsquo;s architecture: three owners, four tabs"),
                        ("send", "Trace a payment from keystroke to dashboard"),
                        ("key", "Place each piece of state with the narrowest owner"),
                        ("check", "Verify the integrated app against a checklist"),
                        ("decision", "Name the limitations Unit 4 addresses")])
where_slide('3.12', 'Today: the whole of Unit 3, working together', (),
            '3.11: performance, lazy loading, measuring.',
            'Integration and architecture review.',
            'Lesson 3.11 made History efficient with large data. Today nothing new is added; everything is connected. The app we run is the complete NPay we have built through Unit 3, with two small accessibility fixes the checklist demanded.',
            'The milestone.')

# ================================================================== Part 1 (1, 2)
divider(1, "The finished NPay", "Eleven lessons in one app", 'The milestone and the feature inventory.', 'The app.')
S.append(slide("Part 1 &middot; Our final NPay milestone (section 1)", "One app, four tabs, real navigation", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:170px 170px minmax(0,1fr);gap:20px;align-items:start">
      {PHONE("img/home0.png", "Home: ₹25,000.00", 170)}
      <div class="step">{PHONE("img/review.png", "Payments: review sheet", 170)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What&rsquo;s on screen", ul("Balance card and quick actions", "Recent transactions", "Home, Payments, History, Profile"))}
        <div class="step">{card("Under the surface", ul("Native navigation and sheets", "Money as integer paise", "Shared state with separate owners"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The final Unit 3 milestone. The text shows an interactive prototype; this is the real app: the NPay we have built lesson by lesson, running in the simulator. Available balance ₹25,000.00, the demo account badge, Send, Request and History quick actions, recent transactions, and four tabs.'),
                  ('SAY', 'Click: the Payments tab with its review sheet. Click: under the surface: native SwiftUI navigation and sheets, money held as integer paise, and shared state with separate owners, which is today&rsquo;s main subject.'),
                  ('CONNECT', 'Which lesson built which part?'))))

INV = [("3.1", "NavigationStack", "Screen navigation"), ("3.2", "Typed routes", "Programmatic payment-success navigation"),
       ("3.3", "TabView", "Four top-level tabs"), ("3.4", "Sheets and alerts", "Payment review"),
       ("3.5", "State preservation", "Payment drafts survive tab changes"), ("3.6", "Animations", "Balance and success feedback"),
       ("3.7", "Reusable components", "NPay design system"), ("3.8", "Adaptive layout", "Responsive quick actions"),
       ("3.9", "Environment", "Appearance preferences"), ("3.10", "Accessibility &amp; localization", "Accessible controls, translated resources"),
       ("3.11", "Performance", "Lazy transaction history and search"), ("3.12", "Integration", "Complete multi-screen NPay")]
S.append(slide("Part 1 &middot; Complete Unit 3 feature inventory (section 2)", "Every lesson left something in the app", f"""  <div class="body">
    {tbl(["Lesson", "Concept", "Integrated NPay feature"], INV, 'tbl compact')}
  </div>""", notes(('SAY', 'The inventory: 3.1 NavigationStack gave screen navigation; 3.2 typed routes gave programmatic navigation to payment success; 3.3 TabView the four tabs; 3.4 sheets and alerts the payment review; 3.5 state preservation kept drafts across tab changes; 3.6 animations the balance and success feedback; 3.7 the design system; 3.8 responsive quick actions; 3.9 appearance preferences through the environment; 3.10 accessible controls and translated resources; 3.11 lazy history and search; and today, 3.12, the complete multi-screen app.'),
                  ('CONNECT', 'How is it all wired together?'))))

# ================================================================== Part 2 (3)
divider(2, "The final architecture", "Three owners, four tabs", 'Navigation, data and preferences live apart.', 'The diagram.')
P = []
P.append(box(260, 0, 240, 50, "NPayApp", "@main &middot; WindowGroup", '1', '', 'app'))
P.append(wire('M380 51V70' + head(380, 70, 'd')))
P.append(box(220, 72, 320, 50, "NPayRootView", "composition root", '1', '', 'layers'))
for i, (t, sub, ic) in enumerate([("NPayRouter", "tabs + paths", "decision"), ("NPayStore", "balance, transactions, draft", "db"), ("NPayPreferences", "appearance", "gear")]):
    x = i * 260
    P.append(wire(f'M380 123L{x + 120} 142' + head(x + 120, 142, 'd')))
    P.append(box(x, 144, 240, 54, t, sub, '2+', '', ic))
    P.append(wire(f'M{x + 120} 199L380 216' + head(380, 216, 'd')))
P.append(box(220, 218, 320, 50, "TabView", "four navigation hierarchies", '3', '', 'grid'))   # the tabs stay grey
for i, (t, sub) in enumerate([("Home", "dashboard"), ("Payments", "form, review, success"), ("History", "search, details"), ("Profile", "settings, appearance")]):
    x = i * 195
    P.append(wire(f'M380 269L{x + 90} 288' + head(x + 90, 288, 'd')))
    P.append(box(x, 290, 180, 50, t, sub, None, ''))
ROOT = """@State private var router = NPayRouter()
@State private var store = NPayStore()
@State private var preferences = NPayPreferences()"""
S.append(slide("Part 2 &middot; The final architecture (section 3)", "Navigation, data and preferences: separate owners", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:22px;align-items:start">
      <div>{cues(3)}{svg('0 0 760 340', 'NPayApp, NPayRootView, NPayRouter, NPayStore, NPayPreferences, TabView, Home, Payments, History, Profile', 'arch', P, 'max-height:350px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("NPayRootView", ROOT, "font-size:11px")}</div>
        <div class="rule step" data-label="Key decision">{ul("Each kind of state has its own owner", "Prepares the Unit 4 MVVM refactor")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The final architecture. Click: NPayApp, the @main entry with its WindowGroup, creates NPayRootView, the application&rsquo;s composition root. Click: the root owns three observable objects: NPayRouter, the selected tab and every tab&rsquo;s path; NPayStore, the balance, transactions and payment draft; NPayPreferences, appearance and configuration.'),
                  ('SAY', 'Click: they feed a TabView with four independent navigation hierarchies: Home with the dashboard and balance; Payments with the form, review and success; History with search and details; Profile with settings and appearance.'),
                  ('SAY', 'Click: in code it is three @State properties in NPayRootView. Click: the text&rsquo;s most important point: navigation, application data and appearance preferences have separate owners. That separation is what Unit 4&rsquo;s MVVM refactoring builds on.'),
                  ('CONNECT', 'Each part has a responsibility, and limits.'))))

RESP = [("NPayRouter", "where the user is", "never deducts money"), ("PaymentReviewSheet", "shows a snapshot, asks to confirm", "never owns the balance"),
        ("BalanceCard", "displays a balance", "never processes a payment"), ("NPayStore", "applies the demo payment", "never decides navigation")]
S.append(slide("Part 2 &middot; One responsibility each (section 4, part 1)", "What each component must never do", f"""  <div class="body">
    {tbl(["Component", "Does", "Never"], RESP, 'tbl')}
    <p class="small muted" style="margin:6px 0 0">First three rows from the text; the NPayStore row is ours, from the same code.</p>
    <div class="gap"></div>
    <div class="step">{card("Why it matters", ul("A bug has one place to live", "Each piece can change, and later be tested, alone"))}</div>
  </div>""", notes(('SAY', 'The text&rsquo;s engineering insight from the first part of Section 4: the router should never deduct money; the review sheet should never own the account balance; the balance card should never process a payment. We add the mirror image from the code: the store applies the payment but never decides where the user goes; the Payments screen asks the router for that.'),
                  ('SAY', 'Click: why it matters: when a bug appears, there is one place it can live, and each piece can change, and in Unit 9 be tested, on its own.'),
                  ('CONNECT', 'Let&rsquo;s watch them cooperate on one payment.'))))

# ================================================================== Part 3 (4)
divider(3, "One payment, end to end", "₹1,500.50 to ravi@npay", 'From keystroke to dashboard.', 'The ten steps.')
TR = [("Text input", "TextField writes the draft (@Bindable)", "NPayStore"), ("Validation", "isValid enables Review Payment", "PaymentsScreen"),
      ("Review", "PaymentReview snapshot; sheet shown", "PaymentsScreen"), ("Confirm", "sheet calls onConfirm", "PaymentReviewSheet"),
      ("Re-validate", "amount still within balance?", "NPayStore"), ("Record", "balance &minus;150,050; transaction inserted", "NPayStore"),
      ("Clean up", "draft cleared; sheet dismissed", "NPayStore + screen"), ("Navigate", "onDismiss &rarr; showPaymentSuccess", "NPayRouter"),
      ("Success", "success screen on paymentsPath", "NPayRouter"), ("Update", "Observation re-runs Home and History", "SwiftUI")]
P = []
for i, (t, sub, own) in enumerate(TR):
    col, r = divmod(i, 5)
    x, y = col * 560, r * 64
    P.append(box(x, y, 540, 54, f'{i + 1}. {t} &middot; {own}', sub, f'{i + 1}' if i < 9 else '10+', ''))
S.append(slide("Part 3 &middot; Trace a complete payment (section 4)", "Ten steps through the owners", f"""  <div class="body">
    {cues(10)}
    {svg('0 0 1100 310', 'Ten steps from text input to the updated dashboard', 'trace', P, 'max-height:330px')}
    <p class="small muted" style="margin:6px 0 0">Step 1 is the text&rsquo;s; steps 2&ndash;10 are ours, read from NPay&rsquo;s code (only the first step of the text&rsquo;s stepper was shared).</p>
  </div>""", notes(('SAY', 'The user sends ₹1,500.50 to ravi@npay. Click: step 1, from the text: the TextField updates the shared PaymentDraft through @Bindable: the draft lives in the store.'),
                  ('SAY', 'The text&rsquo;s stepper had ten steps but only the first was shared; the rest are read from our code. Click: validation: the Payments screen&rsquo;s isValid enables Review Payment. Click: Review takes an immutable PaymentReview snapshot and presents the sheet: presentation state, owned by the screen. Click: Confirm calls the sheet&rsquo;s onConfirm closure.'),
                  ('SAY', 'Click: the store validates again, against the balance as it is now. Click: it deducts 150,050 paise and inserts the transaction. Click: the draft is cleared and the sheet dismissed. Click: the sheet&rsquo;s onDismiss asks the router to show payment success. Click: the router appends the success route to the Payments path. Click: Observation re-runs the views that read the balance and transactions: Home and History.'),
                  ('CONNECT', 'Here is that payment, printed from the running app.'))))

TRC = ["typed:&ensp;&ensp;&ensp;draft (\"ravi@npay\", \"1500.50\") &middot; balance 2,500,000",
       "review:&ensp;&ensp;sheet presented &middot; store unchanged",
       "confirm: balance <b>2,349,950</b> &middot; transactions 3 &rarr; 4",
       "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;draft (\"\", \"\") &middot; sheet gone",
       "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;paymentsPath [.paymentSuccess]",
       "done:&ensp;&ensp;&ensp;&ensp;tab .home &middot; paymentsPath []"]
S.append(slide("Part 3 &middot; The trace, printed (section 4)", "What each owner held, step by step", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:18px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Owners after each step (simulator)", TRC, 12)}
        <div class="step">{card("Notice", ul("Only the store&rsquo;s numbers changed money", "Only the router&rsquo;s path changed the screen"))}</div>
      </div>
      <div class="step">{PHONE("img/success.png", "Payment success", 150)}</div>
      <div class="step">{PHONE("img/home1.png", "Home: ₹23,499.50", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'We drove the real app through accessibility and printed what each owner held after each step, through a debug-only hook that hands the three owners to the test driver; the hook is not part of NPay. Typing wrote the draft in the store; the balance was still 2,500,000 paise. Review presented the sheet and changed nothing in the store.'),
                  ('SAY', 'Confirm: balance 2,349,950 paise, transactions from three to four, the draft emptied, the sheet gone, and the Payments path holding the success route. Done: Home selected and the path empty.'),
                  ('SAY', 'Click: notice the division of labour: only the store changed money; only the router changed which screen is showing. Click: the success screen. Click: Home, showing ₹23,499.50 with the new transaction on top.'),
                  ('CONNECT', 'The flow touched three different kinds of state.'))))

KS = [("Business / demo state", "NPayStore", "Balance, transactions"), ("Navigation state", "NPayRouter", "Selected tab, route paths"),
      ("Presentation state", "PaymentsScreen", "Review sheet visibility")]
S.append(slide("Part 3 &middot; Three kinds of state (section 4)", "Different state, different owners", f"""  <div class="body">
    {tbl(["State", "Owner", "Example"], KS, 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("In the trace", ul("Money moved in the store", "Screens moved in the router", "The sheet came and went in the screen"))}</div>
      <div class="rule step" data-label="Separate">{ul("Less coupling", "Easier debugging")}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s distinction: three kinds of state in one flow. Business, here demo, state, the balance and transactions, owned by NPayStore. Navigation state, the selected tab and route paths, owned by NPayRouter. Presentation state, whether the review sheet is visible, owned by the Payments screen.'),
                  ('SAY', 'Click: that is exactly what the trace showed. Click: keeping them separate reduces coupling and makes debugging easier: a wrong balance is a store question, a wrong screen a router question.'),
                  ('CONNECT', 'What does SwiftUI do between a change and the pixels?'))))

# ================================================================== Part 4 (5)
divider(4, "The SwiftUI runtime", "From state to pixels", 'Change the state; SwiftUI does the rest.', 'The pipeline.')
P = []
PL = [("tap", "Event", "tap, input, data"), ("db", "State mutation", "@State, Binding, model"), ("link", "Invalidation", "which descriptions?"),
      ("code", "View evaluation", "relevant bodies"), ("frame", "Reconcile + layout", "identity, geometry"), ("phone", "Render + present", "the platform")]
for i, (ic, t, sub) in enumerate(PL):
    x = i * 188
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}' if i < 5 else '6+', ''))
    if i < 5:
        P.append(wire(f'M{x + 173} 60H{x + 186}' + head(x + 186, 60, 'r')))
S.append(slide("Part 4 &middot; What the SwiftUI runtime does (section 5) &middot; conceptual", "We change state; SwiftUI updates the interface", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1120 120', 'Application event, state mutation, dependency invalidation, view evaluation, reconciliation and layout, rendering and presentation', 'rt', P, 'max-height:126px')}
    <p class="small muted" style="margin:6px 0 0">SwiftUI&rsquo;s exact reconciliation and rendering are not publicly specified.</p>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("No refreshBalanceCard()", ul("<code>balancePaise -= amountPaise</code>", "Home showed ₹23,499.50 on its own"))}</div>
      <div class="rule step" data-label="Principle">{ul("Change the state", "Views describe the UI for that state", "SwiftUI coordinates the update")}</div>
    </div>
  </div>""", notes(('SAY', 'Connecting Unit 0 to everything since. Click through: an application event, a tap, text input, navigation or a data change; a state mutation, in @State, a Binding or an observable model; dependency invalidation, SwiftUI working out which descriptions may need updating; view evaluation of the relevant bodies; reconciliation and layout, identity, structure and geometry; rendering and presentation by the platform. This is conceptual: the exact implementation is not publicly specified.'),
                  ('SAY', 'Click: the key principle in our trace: the store subtracted the amount, one line, and Home showed ₹23,499.50. Nobody called a method like refreshBalanceCard. Click: we change the state; the view descriptions say how the interface looks for that state; SwiftUI coordinates the updates.'),
                  ('CONNECT', 'So where should each piece of state live?'))))

# ================================================================== Part 5 (6)
divider(5, "State ownership", "The narrowest owner that works", 'The most important Unit 3 concept.', 'The table.')
OWN = [("<code>balancePaise</code>", "NPayStore", "Shared application data"), ("<code>transactions</code>", "NPayStore", "Shared transaction collection"),
       ("<code>paymentDraft</code>", "NPayStore", "Must survive tab switches"), ("<code>selectedTab</code>", "NPayRouter", "Top-level navigation"),
       ("<code>paymentsPath</code>", "NPayRouter", "Payment navigation hierarchy"), ("<code>reviewDraft</code>*", "PaymentsScreen", "Temporary modal presentation"),
       ("<code>focusedField</code>", "PaymentsScreen", "Local keyboard focus"), ("<code>showSuccessAnimation</code>*", "PaymentSuccessScreen", "Temporary visual state"),
       ("<code>appearance</code>", "NPayPreferences", "Shared UI preference")]
S.append(slide("Part 5 &middot; State ownership (section 6)", "Where each value belongs", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.5fr) minmax(0,.5fr);gap:18px;align-items:start">
      <div>{tbl(["Property", "Owner", "Reason"], OWN, 'tbl compact')}
        <p class="small muted" style="margin:4px 0 0">* In our code: <code>review</code> and <code>showContent</code>.</p></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why not all in NPayStore?", ul("Focus needn&rsquo;t be global", "A balance mustn&rsquo;t be copied into four tabs"))}</div>
        <div class="rule step" data-label="Rule">{ul("Narrowest owner that supports the value&rsquo;s lifetime and sharing")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s ownership table. The balance, the transactions and the payment draft belong to NPayStore: shared data, and the draft must survive tab switches, Lesson 3.5. The selected tab and Payments path belong to NPayRouter. The review value and the focused field belong to the Payments screen: temporary presentation and local focus. The success animation flag belongs to the success screen. Appearance belongs to NPayPreferences. Two names differ in our code: the text&rsquo;s reviewDraft is our review, and showSuccessAnimation is our showContent.'),
                  ('SAY', 'Click: why not put everything in NPayStore? A focus indicator does not need to be global; and a balance should not be duplicated independently in four tabs, which Lesson 3.1 showed going wrong with a second @State owner. Click: the rule: state is owned at the narrowest level that supports its intended lifetime and sharing. This is a foundational architectural skill.'),
                  ('CONNECT', 'Now verify the whole app.'))))

# ================================================================== Part 6 (7)
divider(6, "Final integration test", "Twelve checks on the real app", '₹25,000.00 &minus; ₹1,500.50.', 'The arithmetic.')
CK = [("1", "Dashboard initially shows ₹25,000.00", "&#10003;"), ("2", "Payments accepts a valid recipient and amount", "&#10003; Review enabled"),
      ("3", "Review sheet shows the exact payment", "&#10003; ravi@npay, ₹1,500.50"), ("4", "Cancelling review preserves the draft", "&#10003; both fields kept"),
      ("5", "Confirming records exactly one transaction", "&#10003; 2 activations &rarr; 1"), ("6", "Success screen after sheet dismissal", "&#10003; sheet gone first"),
      ("7", "Dashboard shows ₹23,499.50", "&#10003;"), ("8", "History contains the new transaction", "&#10003; at the top"),
      ("9", "Draft cleared after success", "&#10003; both fields empty"), ("10", "Appearance applies across tabs", "&#10003; dark in all four"),
      ("11", "VoiceOver identifies important controls", "&#10003; after our fix"), ("12", "History responsive with a larger dataset", "&#10003; 50,003 records")]
S.append(slide("Part 6 &middot; Simulate a complete transaction (section 7)", "₹25,000.00 &minus; ₹1,500.50 = ₹23,499.50", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.62fr) minmax(0,1.38fr);gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Integer paise", ["&ensp;2,500,000", "&minus;&ensp;&ensp;150,050", "= 2,349,950"], 15)}
        <div class="step">{card("Measured", ul("Store: 2,349,950", "Screen: ₹23,499.50"))}</div>
      </div>
      <div class="step">{tbl(["#", "Unit 3 integration check", "Run in the simulator"], CK, 'tbl compact')}</div>
    </div>
  </div>""", notes(('SAY', 'Starting balance ₹25,000.00; the payment, ₹1,500.50; expected, ₹23,499.50. In integer paise: 2,500,000 minus 150,050 is 2,349,950. Click: the store held exactly that, and the balance card showed ₹23,499.50.'),
                  ('SAY', 'Click: the text&rsquo;s twelve-item checklist, run on the real app by a script. Every item passes. Some details: item 4, Edit Details closed the sheet and both fields still held ravi@npay and 1500.50. Item 5, we activated Confirm twice in a row, like a double tap, and exactly one transaction was recorded, three to four, the guard from Lesson 3.4. Item 6, when "Payment Recorded" appeared, the sheet was already gone. Item 10, Dark chosen in Profile, and all four tabs reported a dark interface.'),
                  ('SAY', 'Item 11 passes only after a fix; item 12 has its own evidence. Next two slides.'),
                  ('CONNECT', 'Item 11.'))))

FIX = """TextField("Recipient ID",
          text: $store.paymentDraft.recipient)
    .accessibilityIdentifier(
        NPayAccessibilityID.recipientField)
    .accessibilityLabel("Recipient")

Image(systemName: "checkmark.circle.fill")
    .accessibilityHidden(true)"""
S.append(slide("Part 6 &middot; Item 11: VoiceOver can identify important controls (section 7)", "The check failed until we fixed it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("NPay as of 3.11", ["identifiers: npay.recipientField, npay.amountField, npay.sendButton", "fields with an <b>empty label</b>: both"], 12)}
        <div class="step">{code("Lesson 3.12 fixes (ours)", FIX, "font-size:12px")}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("After the fix", ["fields with an empty label: none", "success: &ldquo;Payment Recorded&rdquo; | &ldquo;Your demo payment was successful.&rdquo;", "(no &ldquo;Selected&rdquo; checkmark)"], 12)}</div>
        <div class="rule step" data-label="Lesson">{ul("A checklist is only useful if it can fail", "Identifiers serve tests; labels serve people")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Item 11 is the interesting one. Run on NPay as it stood after Lesson 3.11, it failed: all the identifiers were present, but both payment text fields had an empty accessibility label, the problem Lesson 3.10 measured and left open.'),
                  ('SAY', 'Click: our fix, flagged as ours: a label on each field, "Recipient" and "Amount in rupees", and the success checkmark hidden from accessibility, because VoiceOver read it as "Selected" and the text beside it already says the payment was recorded.'),
                  ('SAY', 'Click: after the fix: no unlabelled fields, and the success screen reads its text without the misleading checkmark. Click: a checklist is only useful if it can fail; this one did. And identifiers serve UI tests, labels serve people.'),
                  ('CONNECT', 'Item 12 and appearance.'))))

S.append(slide("Part 6 &middot; Items 10 and 12: appearance and a large History (section 7)", "Dark everywhere; 50,003 records", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px 150px minmax(0,1fr);gap:18px;align-items:start">
      {PHONE("img/dark.png", "Dark, set in Profile", 150)}
      {PHONE("img/history1.png", "History after the payment", 150)}
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Item 10", ["Home dark, Payments dark, History dark, Profile dark"], 12)}
        <div class="step">{console("Item 12: 50,000 more records (simulator)", ["store: 50,003 transactions (+5 MB)", "History: 8 rows exposed (lazy List)", "search &ldquo;49999&rdquo;: Demo Transaction 49999", "display frames, 1 s after typing: 60"], 12)}</div>
        <div class="step">{card("Responsive, not benchmarked", ul("Counts, not timings: see 3.11", "Instruments on a device for real numbers"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Item 10: Dark chosen once on the Profile tab&rsquo;s Appearance screen; every tab reported a dark interface, because NPayPreferences is applied at the root with preferredColorScheme, Lesson 3.9. Beside it, History after the payment, with "Sent to ravi@npay" on top.'),
                  ('SAY', 'Click: item 12: we added fifty thousand demo transactions to the store from Lesson 3.11. History, a List, exposed eight rows: the visible region. Searching 49999 found the one match, and the display delivered sixty frames in the second after typing.'),
                  ('SAY', 'Click: that is a responsiveness check by counts, in the simulator, not a benchmark; Lesson 3.11 covers measuring properly with Instruments on a device.'),
                  ('CONNECT', 'It works. What would we still improve?'))))

# ================================================================== Part 7 (5, 8)
divider(7, "Limitations and Unit 4", "A working prototype, not the final design", 'What remains, and why that&rsquo;s fine.', 'The list.')
LIM = [("NPayStore contains payment rules", "Use cases and domain services", "4"), ("Screens access the shared store", "Feature ViewModels", "4"),
       ("UI coordinates some operations", "MVVM and dependency injection", "4"), ("Demo transactions in memory", "Repositories and persistence", "5&ndash;6"),
       ("Local payment simulation", "Backend API; real authentication", "5, 7"), ("Simple error handling", "Typed errors, loading states", "4&ndash;5"),
       ("Manual testing", "Automated unit, integration and UI tests", "9"), ("One application module", "Feature modularization", "12")]
S.append(slide("Part 7 &middot; Architecture limitations (sections 5 and 8)", "What still needs improvement", f"""  <div class="body">
    {tbl(["Current implementation", "Future improvement", "Unit"], LIM, 'tbl compact')}
    <p class="small muted" style="margin:6px 0 0">Merged from the text&rsquo;s two limitation tables; the Unit column is ours, from the curriculum.</p>
    <div class="gap"></div>
    <div class="rule step" data-label="Not a rewrite">{ul("Intentional: Unit 3 taught composition; these motivate Unit 4")}</div>
  </div>""", notes(('SAY', 'The text lists the limitations twice, in Part 1 and Part 2; this is the merged list. NPayStore combines responsibilities and holds the payment rules: Unit 4 brings use cases and feature ViewModels. Screens reach the shared store directly and the UI coordinates some operations: MVVM and dependency injection. Transactions live in memory: repositories and persistence, Units 5 and 6. The payment is a local simulation with no real authentication: the backend API and security units. Error handling is simple: typed errors and loading states. Testing is manual: Unit 9. And it is one module: modularization comes in the final unit. The Unit column is our mapping to the curriculum.'),
                  ('SAY', 'Click: the text is clear that this is intentional. Unit 3 taught SwiftUI application composition; these are not reasons to rewrite everything immediately, they are the motivation for Unit 4, architecture and testability.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.12', (), [("layers", "Three owners, four tabs", "router, store, preferences; navigation apart from data"),
                      ("key", "Narrowest owner that works", "store for shared data, screen for presentation, view for visuals"),
                      ("check", "Verified, end to end", "₹23,499.50, one transaction, all 12 checks")],
          'Three things to remember from Unit 3. NPay&rsquo;s architecture is three owners at the root, router, store and preferences, feeding four independent navigation hierarchies. Each value lives with the narrowest owner that supports its lifetime and sharing: shared data in the store, navigation in the router, presentation in the screen, a visual flag in its view. And the whole app is verified: one payment of ₹1,500.50 took the balance to ₹23,499.50, recorded exactly one transaction, and passed all twelve integration checks once we fixed the field labels.')

review_divider(10)
review([("db", "Choose one", "Who should own NPay's shared account balance?",
         "Who should own NPay&rsquo;s shared account balance?<br>A. Each tab independently<br>B. The review sheet<br>C. One shared application state owner", "C",
         "NPayStore: every tab reads the same balance.",
         "Copying shared data into each screen.", "Most pick C.", None),
        ("decision", "Choose one", "What is the purpose of NPayRouter?",
         "What is the purpose of NPayRouter?<br>A. Payment calculations<br>B. Navigation state<br>C. Currency formatting", "B",
         "Selected tab and paths; it never touches money.",
         "Letting navigation code do business work.", "Most pick B.", None),
        ("file", "Choose one", "Why preserve PaymentDraft outside the review sheet?",
         "Why preserve PaymentDraft outside the review sheet?<br>A. To survive review dismissal<br>B. To create a new process<br>C. To avoid using Swift", "A",
         "Edit Details closed the sheet; both fields were kept.",
         "Storing input inside a modal.", "Most pick A.", None),
        ("frame", "Question", "Does LazyVStack automatically fetch transactions from an API?",
         "Does <code>LazyVStack</code> automatically fetch transactions from an API?", "No",
         "It creates views lazily; fetching is Units 5&ndash;6.",
         "Confusing lazy views with lazy data.", "Most say no.", None),
        ("key", "Choose one", "Why use stable transaction IDs?",
         "Why use stable transaction IDs?<br>A. To increase frame rate automatically<br>B. To preserve logical identity<br>C. To create a new navigation stack", "B",
         "Identity is the transaction, not the render pass.",
         "Thinking any unique value will do.", "Most pick B.", None),
        ("layers", "Choose one", "What is the role of @Environment?",
         "What is the role of <code>@Environment</code>?<br>A. Read contextual values from the view hierarchy<br>B. Persist data to disk<br>C. Create threads", "A",
         "NPayPreferences reached all four tabs that way.",
         "Treating it as storage.", "Most pick A.", None),
        ("check", "Question", "Should the success animation determine whether the transaction succeeded?",
         "Should the payment success animation determine whether the transaction succeeded?", "No",
         "The store decides; the screen only shows the result.",
         "Letting presentation decide business outcomes.", "Most say no.", None),
        ("send", "Predict the result", "Confirm activated twice: how many transactions?",
         "The review sheet&rsquo;s Confirm button is activated twice in a row. How many transactions does NPay record?<br>A. 0<br>B. 1<br>C. 2", "B",
         "The isProcessing guard (3.4) and the store&rsquo;s check: 3 &rarr; 4.",
         "Assuming a button runs once per tap only.", "Some pick C.", None),
        ("diff", "Choose one", "What is the main purpose of Unit 4?",
         "What is the main purpose of Unit 4?<br>A. Replace SwiftUI with UIKit<br>B. Remove all protocols<br>C. Introduce maintainable application architecture", "C",
         "MVVM, use cases, DI: the limitations list.",
         "Expecting a rewrite.", "Most pick C.", None),
        ("code", "Question", "From 3.11: does a sort inside body run on every evaluation?",
         "From Lesson 3.11: if <code>body</code> sorts the transactions, does the sort run every time the body is evaluated?", "Yes",
         "4 keystrokes, 4 sorts of 50,000 records.",
         "Assuming SwiftUI caches body work.", "Most say yes.", "Spaced review from Lesson 3.11.")])

S.append(next_slide('3.12', [("Unit 4", "MVVM &amp; application architecture", "feature ViewModels, payment use case, DI"),
                             ("Units 5&ndash;6", "Networking; persistence", "repositories replace in-memory transactions"),
                             ("Unit 7", "Security &amp; authentication", "a real, authenticated payment flow"),
                             ("Unit 9", "Testing", "today&rsquo;s checklist as automated tests")],
                    'Unit 4 refactors this exact app into MVVM: feature ViewModels, a dedicated payment use case, dependency injection. Units 5 and 6 replace in-memory transactions with API and persistence repositories. Unit 7 makes payments authenticated. Unit 9 turns today&rsquo;s twelve manual checks into automated tests, using the identifiers from 3.10.'))

S.append(lab_slide('3.12', "Unit 3 checkpoint", "Run, trace and review your own NPay.",
                   ["Build your complete NPay through Lesson 3.12.",
                    "Send ₹1,500.50 to ravi@npay; expect ₹23,499.50.",
                    "Run all 12 integration checks.",
                    "Fill in the state ownership table from your code.",
                    "Fix anything that fails, like the field labels.",
                    "List three things to move into ViewModels."],
                   "", 'Expected, as in our run: 2,349,950 paise, one transaction even on a double activation, the draft kept on Edit Details and cleared on success, dark in every tab, and labels on both payment fields once fixed.',
                   side=f'<div>{card("You hand in", ul("Your 12-check results", "Your ownership table with reasons", "Three Unit 4 refactoring candidates"))}</div>'))

end_slide('3.12', 'NPay Final Integration<br>&amp; Architecture', 'Unit 4 &mdash; MVVM &amp; Application Architecture',
          'You can now explain how NPay&rsquo;s owners, tabs and screens fit together, trace a payment end to end, place state with the narrowest owner, and verify an app against an integration checklist. Unit 3, Advanced SwiftUI and Navigation, is complete.',
          'Next, Unit 4: MVVM and application architecture, starting from this exact app.')

write_deck(OUT312, '3.12', 'NPay Final Integration &amp; Architecture', 'NPay Final Integration &amp; Architecture')
