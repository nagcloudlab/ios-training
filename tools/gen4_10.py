"""Generates decks/unit-4/lesson-4.10/index.html from the Lesson 4.10 text (Complete NPay MVVM Integration & Architecture
Review, the Unit 4 capstone; Part 1 Sections 1-6, Part 2 Sections 7-9, a final part from Section 9 to 12). Evidence:
tools/sim4_10 - the complete Unit 4 NPay (feature folders, NPayCore modules, one InMemoryAccountRepository behind
NPayDependencies, DashboardViewModel for Home and History): a 9-step trace, the capstone checklist, a slow payment,
screenshots, and test.sh (3 XCTest + 18 Swift Testing tests)."""
import html, os, re, sys
OUT410 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.10', 'Complete NPay MVVM<br>Integration',
            'The same app on the outside; <b>a maintainable, testable architecture</b> inside.',
            'This is the final lesson of Unit 4. Across nine lessons we learned MVVM, Observation, dependency injection, repositories, domain models and use cases, modularization and testing. Today we bring them together into one NPay, keeping everything from Unit 3, and we verify it: one payment traced through every layer, the text&rsquo;s acceptance checklist run on the real app, and the whole test suite green.')
outcomes_slide('4.10', [("layers", "Describe NPay&rsquo;s final layers and owners"),
                        ("db", "Derive balance and history from one repository"),
                        ("send", "Trace a payment from form to dashboard"),
                        ("check", "Verify an architecture against acceptance criteria"),
                        ("diff", "Compare Unit 3&rsquo;s design with Unit 4&rsquo;s"),
                        ("shield", "Name the risks that remain before networking")])
where_slide('4.10', 'Today: Unit 4, assembled and verified', (),
            '4.9: tests for every layer.',
            'The complete MVVM NPay, reviewed.',
            'Last time every layer got tests. Today the layers become one app, and the tests and the acceptance checklist prove it. The text came in three pieces; the third continues from Section 9.',
            'What we&rsquo;re building.')

# ================================================================== Part 1 (1, 2, 3)
divider(1, "The final architecture", "Same experience, new structure", 'Layers, owners and files.', 'The app.')
P = []
for i, (ic, t, sub) in enumerate([("phone", "Presentation", "SwiftUI views, PaymentViewModel, DashboardViewModel"), ("gear", "Application", "SendPaymentUseCase, PaymentPolicy"),
                                  ("key", "Domain", "PaymentAmount, PaymentRecipient, AccountRepository"), ("db", "Infrastructure", "InMemoryAccountRepository actor")]):
    y = i * 72
    P.append(box(0, y, 600, 58, t, sub, '1+' if i == 2 else None, '', ic))
for y in (59, 131):
    P.append(wire(f'M300 {y}V{y + 11}' + head(300, y + 11, 'd')))
P.append(wire('M300 274V218' + head(300, 218, 'u'), '2+'))
OWN = [("NPayRootView", "UI composition"), ("NPayRouter", "Tabs and navigation"), ("NPayDependencies", "One repository; builds ViewModels (ours)"),
       ("PaymentViewModel", "Payment form and submission state"), ("DashboardViewModel", "Balance and recent transactions"), ("SendPaymentUseCase", "Payment workflow"),
       ("PaymentPolicy", "Illustrative limits"), ("AccountRepository", "Data-access contract"), ("InMemoryAccountRepository", "Simulated account state"), ("NPayPreferences", "Appearance")]
S.append(slide("Part 1 &middot; What we&rsquo;re building; the final architecture (sections 1&ndash;2)", "Four layers behind the same screens", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:170px minmax(0,1fr);gap:24px;align-items:start">
      {PHONE("img/home0.png", "NPay, Unit 4", 170)}
      <div>{cues(2)}{svg('0 0 600 274', 'Presentation, application, domain, infrastructure; infrastructure implements the domain contract', 'arch', P, 'max-height:300px')}
        <p class="small muted" style="margin:6px 0 0">Arrows: code dependencies. Infrastructure implements the domain contract.</p></div>
    </div>
  </div>""", notes(('SAY', 'What we are building: the same NPay, ₹25,000.00, Send Money, History, four tabs. The user experience stays the same; what changes is the architecture behind it. The text showed an interactive prototype; this is the real app, built and run.'),
                  ('SAY', 'The layers: presentation, the SwiftUI views and the two ViewModels; application, the use case and policy; click: domain, value objects and the repository contract; infrastructure, the in-memory actor. Click: the arrows are code dependencies, and infrastructure points up: it implements the domain&rsquo;s contract.'),
                  ('CONNECT', 'Who owns what.'))))

S.append(slide("Part 1 &middot; Who owns what? (section 2)", "Each component has one reason to change", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:18px;align-items:start">
      {tbl(["Component", "Responsibility"], OWN[:5], 'tbl compact')}
      {tbl(["Component", "Responsibility"], OWN[5:], 'tbl compact')}
    </div>
  </div>""", notes(('SAY', 'Who owns what. The root composes the UI; the router owns tabs and navigation; NPayDependencies, which we added from Lesson 4.5, owns the single repository and builds the ViewModels; PaymentViewModel owns the form and submission state; DashboardViewModel the balance and recent transactions; the use case the workflow; the policy the illustrative limits; the repository contract and its actor the account data; NPayPreferences the appearance. The rule: each component has one clear reason to change.'),
                  ('CONNECT', 'Where the files live.'))))

TREE = """NPay/                             (one app module)
├── App/        NPayRootView, NPayRouter, NPayDependencies,
│               NPayFactory, NPayPreferences, NPayAccessibilityID
├── Features/
│   ├── Home/      HomeScreen, DashboardViewModel
│   ├── Payments/  PaymentsScreen, PaymentViewModel,
│   │              PaymentReviewSheet, PaymentSuccessScreen, …
│   ├── History/   HistoryScreen, TransactionDetailScreen
│   └── Profile/   ProfileScreen, AppearanceSettingsView
├── Domain/     Money, Transaction, PaymentValidator
└── DesignSystem/  NPayTheme, NPayButton, NPayCard, …
NPayCore/  NPayDomain · NPayData · NPayDomainTests · NPayDataTests
NPayAppTests/  ViewModel tests on the app&rsquo;s own sources"""
S.append(slide("Part 1 &middot; Final project structure (section 3)", "Folders for people; modules for the compiler", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:20px;align-items:start">
      {code("tools/sim4_10 (ours)", TREE, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Matches the text", ul("App, Features, Domain, DesignSystem", "Tests by layer"))}
        <div class="step">{card("Differs", ul("Domain and Data types live in NPayCore (4.8)", "Tests sit with their package"))}</div>
        <div class="rule step" data-label="Reminder">{ul("Folders alone don&rsquo;t create modules")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s target structure: App with the root, router and dependencies; Features with Home, Payments, History and Profile, each with its screens and ViewModels; Domain with models, use cases and repositories; Data with the in-memory repository; DesignSystem; and Tests by layer. Ours, on the slide, follows it.'),
                  ('SAY', 'Click: where it differs, from Lesson 4.8: the domain types and the in-memory repository live in the NPayCore package as NPayDomain and NPayData, so the app&rsquo;s Domain folder keeps only Money, Transaction and the form validator; and tests sit with their package, NPayCore&rsquo;s test targets and NPayAppTests. Click: the reminder from 4.8: folders alone do not create Swift modules.'),
                  ('CONNECT', 'The one big change today: one source of truth.'))))

# ================================================================== Part 2 (integration: one repository)
divider(2, "One source of truth", "Home, History and Payments on one repository", 'NPayStore retires.', 'The change.')
DEPS = """@MainActor
final class NPayDependencies {
    let repository: any AccountRepository

    init() {
        repository = InMemoryAccountRepository(
            initialBalancePaise: 2_500_000,
            transactions: NPayDependencies.demoHistory)
    }

    func makeDashboardViewModel() -> DashboardViewModel {
        DashboardViewModel(repository: repository)
    }

    func makePaymentViewModel(availableBalance:
        @escaping @MainActor () -> Int) -> PaymentViewModel {
        NPayFactory.makePaymentViewModel(
            repository: repository,
            availableBalance: availableBalance)
    }
}"""
CHG = [("Home", "NPayStore", "DashboardViewModel"), ("History", "NPayStore.transactions", "DashboardViewModel"),
       ("Payments", "adapter over NPayStore (4.6)", "the same repository"), ("After a payment", "Observation on the store", "<code>await dashboard.reload()</code>")]
S.append(slide("Part 2 &middot; Balance and history from the same repository (sections 2, 11; integration ours)", "NPayDependencies owns the repository", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      {code("App/NPayDependencies.swift", DEPS, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["", "Before (4.9)", "Now"], CHG, 'tbl compact')}</div>
        <div class="step">{card("Also", ul("NPayStore and its adapter deleted", "NPayData&rsquo;s init gains an optional demo history", "Salary Credit dropped: the repository models payments"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 11&rsquo;s requirement: the balance and transaction history must be derived from the same repository state. Until now, Home and History read NPayStore, and payments reached it through our adapter. Today, flagged as ours, NPayDependencies, the shape Lesson 4.5 used, owns one InMemoryAccountRepository and builds both ViewModels from it.'),
                  ('SAY', 'Click: Home and History now read DashboardViewModel; Payments writes through the use case to the same repository; and after a successful payment the screen awaits dashboard.reload, Lesson 4.5&rsquo;s explicit refresh.'),
                  ('SAY', 'Click: NPayStore and the adapter are gone. To keep Unit 3&rsquo;s demo history, NPayData&rsquo;s initializer gained an optional transactions parameter with a default, so every earlier call still compiles. One visible difference: the Salary Credit row is gone, because the repository records outgoing payments only; history rows now read "Sent to Coffee Shop".'),
                  ('CONNECT', 'Refresh, and when it fails.'))))

RELOAD = """// DashboardViewModel (ours)
var refreshFailed = false

func reload() async {
    do {
        try await refresh()
        refreshFailed = false
    } catch {
        refreshFailed = true      // the payment stays a success
    }
}

// PaymentsScreen, after Confirm succeeds
pendingSuccessID = record.id
self.review = nil
await onPaymentRecorded()     // { await dashboard.reload() }"""
S.append(slide("Part 2 &middot; Refresh after a payment (section 9, question 6)", "A failed refresh is not a failed payment", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      {code("Ours", RELOAD, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("NPayAppTests (ours)", ["&#10004; dashboardShowsThePaymentAfterRefresh()", "&ensp;before reload: 2500000; after: 2349950", "&#10004; failedRefreshKeepsTheLastSnapshot()", "&ensp;refreshFailed true; snapshot untouched"], 11)}</div>
        <div class="rule step" data-label="Rule">{ul("Preserve the success; report the refresh separately")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s assessment asks what should happen after a confirmed payment when the dashboard refresh fails: preserve the success and report the refresh failure separately. Our DashboardViewModel gets a reload that does exactly that: it refreshes, and on error sets refreshFailed instead of throwing at the payment. The Payments screen, on success, stores the ID, dismisses the sheet and awaits the dashboard reload.'),
                  ('SAY', 'Click: two tests of ours. One pays through the real use case and shows the dashboard is a snapshot: still 2,500,000 until reload, then 2,349,950 with "Sent to ravi@npay" first. The other uses a repository whose snapshot always fails: reload sets refreshFailed and leaves the last snapshot untouched.'),
                  ('SAY', 'Click: the rule from Lesson 4.5, now in the app: never interpret a failed UI refresh as proof the payment failed.'),
                  ('CONNECT', 'Trace one payment end to end.'))))

# ================================================================== Part 3 (4, 5)
divider(3, "One payment, end to end", "₹1,500.50, through every layer", 'Nine steps, printed.', 'The steps.')
P = []
STEPS = [("Enter details", "bindings &rarr; PaymentViewModel"), ("Prepare command", "domain values"), ("Review sheet", "immutable command"),
         ("Confirm", "submit(command): .submitting"), ("Use case", "PaymentPolicy"), ("Repository actor", "atomic check and update"),
         ("Success", "state .success(record)"), ("Navigate", "onDismiss &rarr; router"), ("Refresh", "dashboard.reload()")]
for i, (t, sub) in enumerate(STEPS):
    col, r = divmod(i, 5)
    x, y = col * 560, r * 62
    P.append(box(x, y, 540, 52, f'{i + 1}. {t}', sub, f'{i + 1}' if i < 8 else '9+', ''))
TRC = ["launch:&ensp;repository 2,500,000, 2 payments; dashboard the same", "1&ensp;form (\"ravi@npay\", \"1500.50\"); repository unchanged", "2&ndash;3 sheet: ravi@npay, ₹1,500.50",
       "4&ndash;7 repository <b>2,349,950</b>, 3 payments; sheet dismissed", "8&ensp;paymentsPath 1, Payment Recorded", "9&ensp;dashboard 2,349,950, 3; Home ₹23,499.50"]
S.append(slide("Part 3 &middot; End-to-end payment flow (section 4)", "From binding to refreshed dashboard", f"""  <div class="body">
    {cues(9)}
    {svg('0 0 1100 310', 'Nine steps from entering details to refreshing the dashboard', 'flow', P, 'max-height:250px')}
    <div class="gap"></div>
    <div class="step">{console("Simulator, printed after each stage", TRC, 11)}</div>
  </div>""", notes(('SAY', 'Trace ₹1,500.50 to ravi@npay. Only step one of the text&rsquo;s nine-step stepper was shared, PaymentsScreen binding recipient and amount to PaymentViewModel; the other steps are ours, from the code. Click through: enter details; prepare the command in domain values; the review sheet shows that immutable command; Confirm calls submit and the state becomes submitting; the use case applies the policy; the repository actor checks and updates atomically; the state becomes success with the record; the sheet&rsquo;s onDismiss asks the router to navigate; the dashboard reloads.'),
                  ('SAY', 'Click: printed from the running app. At launch the repository and dashboard both hold 2,500,000 and two payments. Typing changes only the form. The sheet shows ravi@npay and ₹1,500.50. After Confirm the repository holds 2,349,950 paise and three payments, and the sheet is gone; the Payments path holds the success route; the dashboard shows 2,349,950 and three payments, and Home ₹23,499.50.'),
                  ('CONNECT', 'What happened at the await?'))))

S.append(slide("Part 3 &middot; What happens at await? (section 5)", "Three isolation domains, one call", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px 150px minmax(0,1fr);gap:18px;align-items:start">
      {PHONE("img/review.png", "Review: the command", 150)}
      {PHONE("img/home1.png", "Home after the payment", 150)}
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("PaymentViewModel", "let record = try await sendPayment.execute(command)", "font-size:12px")}
        <div class="step">{card("Crossing boundaries", ul("ViewModel: main actor", "Use case: async call into the repository", "Repository actor: protects its state", "Back on the main actor: update state"))}</div>
        <div class="step">{console("With 3 s latency (debug hook)", ["0.8 s in: Processing demo payment..., Confirm disabled", "&ensp;dashboard still 2500000", "then: Payment Recorded, dashboard 2349950"], 11)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Left, the review sheet showing the command; right, Home after the payment, ₹23,499.50 and the new row on top. The call that did the work: let record equals try await sendPayment.execute(command).'),
                  ('SAY', 'Click: it crosses several boundaries: the ViewModel is main-actor isolated; the use case makes an asynchronous call into the repository; the repository actor protects its mutable account state; when it completes, the ViewModel resumes on the main actor and updates its state. await marks a possible suspension; it does not guarantee a new thread. Actor isolation controls access; the concurrency runtime schedules tasks.'),
                  ('SAY', 'Click: we slowed the repository by three seconds through a debug-only hook to watch it: 0.8 seconds in, "Processing demo payment...", Confirm disabled, the dashboard still on the old snapshot; then Payment Recorded and the dashboard at 2,349,950. This is the foundation for networking and concurrency in later units.'),
                  ('CONNECT', 'The capstone checklist.'))))

# ================================================================== Part 4 (6, 11)
divider(4, "Verification", "The acceptance checklist, run", 'Fourteen items; app and tests.', 'The results.')
CK = [("1", "All four tabs launch", "&#10003; NPay, Payments, History, Profile"), ("2", "NavigationStack, typed routes", "&#10003; account details; transaction details"),
      ("3", "Draft survives tab switching", "&#10003; ravi@npay, 1500.50"), ("4", "Review shows immutable details", "&#10003; ravi@npay, ₹1,500.50"),
      ("5", "Explicit submission states", "&#10003; submitting, then success"), ("6", "Use case applies policy", "&#10003; tests"),
      ("7", "Repository updates atomically", "&#10003; tests (concurrent)"), ("8", "Duplicate submissions rejected", "&#10003; 2 Confirms &rarr; 1 payment"),
      ("9", "Success after sheet dismissal", "&#10003; sheet gone, path 1"), ("10", "Dashboard refreshes", "&#10003; 2,349,950 = repository"),
      ("11", "History shows the new row", "&#10003; first: Sent to ravi@npay"), ("12", "Appearance across tabs", "&#10003; dark in all four"),
      ("13", "VoiceOver labels and IDs", "&#10003; 4 IDs; no unlabelled field"), ("14", "Tests pass", "&#10003; 3 XCTest + 18 Swift Testing")]
S.append(slide("Part 4 &middot; Unit 4 capstone verification (sections 6, 11)", "Every item, checked on the real app", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start">
      {tbl(["#", "Check", "Result (ours)"], CK[:7], 'tbl compact')}
      {tbl(["#", "Check", "Result (ours)"], CK[7:], 'tbl compact')}
    </div>
  </div>""", notes(('SAY', 'Section 6&rsquo;s fourteen-item checklist, run by script on the real app and the test suites. The four tabs launch. Typed routes push account details from Home and transaction details from History. The draft survives a tab switch. The review sheet shows ravi@npay and ₹1,500.50. With latency, the state is visibly submitting, then success. The policy and atomic repository updates are covered by the tests, including the concurrent-payment test.'),
                  ('SAY', 'Confirm activated twice records one payment. Success navigation happens after the sheet is gone. The dashboard&rsquo;s balance equals the repository&rsquo;s, 2,349,950. History lists "Sent to ravi@npay" first. Dark appearance applies to all four tabs. All four accessibility identifiers are present and no field is unlabelled. And the tests pass: three XCTest and eighteen Swift Testing tests. Section 11&rsquo;s ten-item list is a subset of these.'),
                  ('CONNECT', 'The arithmetic, and the history.'))))

S.append(slide("Part 4 &middot; The final NPay demonstration (section 11)", "₹25,000.00 &minus; ₹1,500.50 = ₹23,499.50", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px 150px minmax(0,1fr);gap:18px;align-items:start">
      {PHONE("img/home1.png", "Home", 150)}
      {PHONE("img/history1.png", "History", 150)}
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Integer paise", ["&ensp;2,500,000", "&minus;&ensp;&ensp;150,050", "= 2,349,950"], 15)}
        <div class="step">{card("Same state, two screens", ul("Home: balance and recent rows", "History: the full list", "Both from one repository snapshot"))}</div>
        <div class="step">{console("test.sh", ["NPayCore: 3 XCTest + 12 Swift Testing, coverage 92.23%", "NPayAppTests: 6 Swift Testing tests"], 11)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The expected scenario: ₹25,000.00, minus ₹1,500.50 to ravi@npay, equals ₹23,499.50: in integer paise, 2,500,000 minus 150,050 is 2,349,950. Home shows the balance and the recent rows; History the full list with the new payment first.'),
                  ('SAY', 'Click: the requirement that matters most: both come from the same repository snapshot, not two copies that could drift apart. Click: and the tests: NPayCore&rsquo;s three XCTest and twelve Swift Testing tests with 92% line coverage, and six tests on the app&rsquo;s ViewModels, including the two dashboard tests from Part 2.'),
                  ('CONNECT', 'How far have we come since Unit 3?'))))

# ================================================================== Part 5 (7, 8)
divider(5, "Architecture review", "What improved; what remains", 'Honest about both.', 'Unit 3 vs Unit 4.')
CMP = [("Shared NPayStore handles payment behaviour", "PaymentViewModel coordinates the feature"), ("Store validates and records payments", "Use case defines the workflow"),
       ("In-memory store holds transactions", "Repository abstracts account operations"), ("Direct concrete dependencies", "Constructor injection and protocols"),
       ("UI-driven error handling", "An explicit state machine"), ("Mostly manual verification", "Unit and integration tests"), ("Large app target", "Feature folders and modules")]
S.append(slide("Part 5 &middot; What have we improved since Unit 3? (section 7)", "Nearly identical screens; a different inside", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:20px;align-items:start">
      {tbl(["Unit 3", "Unit 4"], CMP, 'tbl compact')}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Measured along the way", ["PaymentsScreen: 160 &rarr; 120 lines (4.2)", "Store uses in the screen: 14 &rarr; 0", "One 1,543-line file &rarr; 32 files (4.8)", "Tests: 0 &rarr; 21"], 11)}</div>
        <div class="rule step" data-label="Result">{ul("Easier to test and extend", "Not a different-looking app")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Unit 3 versus Unit 4, from the text. A shared NPayStore handled payment behaviour; now PaymentViewModel coordinates the feature. The store validated and recorded payments; now a use case defines the workflow. The store held transactions in memory; now a repository abstracts account operations. Concrete dependencies became constructor injection and protocols; UI-driven error handling became an explicit state machine; mostly manual verification became unit and integration tests; a large app target became feature folders and modules.'),
                  ('SAY', 'Click: some of that, measured during the unit: the Payments screen went from a hundred and sixty lines to a hundred and twenty and from fourteen uses of the store to none in 4.2; one 1,543-line file became organized files in 4.8; and the test count went from zero to twenty-one.'),
                  ('SAY', 'Click: the visible interface looks almost identical. The internal design is significantly easier to test and to extend.'),
                  ('CONNECT', 'What is still missing.'))))

RISK = [("cloud", "No real backend", "simulated in memory"), ("db", "No persistence", "lost on relaunch"),
        ("lock", "No authentication", "no verified identity"), ("key", "No idempotency", "duplicates possible"),
        ("decision", "No reconciliation", "unknown outcomes")]
P = []
for i, (ic, t, sub) in enumerate(RISK):
    x = i * 224
    P.append(tall(x, 0, 208, 130, ic, t, sub, f'{i + 1}' if i < 4 else '5+', ''))
S.append(slide("Part 5 &middot; Architecture risks still remaining (section 8)", "Exactly what later units address", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1110 130', 'No backend, no persistence, no authentication, no server idempotency, no status reconciliation', 'risk', P, 'max-height:136px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Seen in this unit", ul("Relaunch: ₹25,000.00 again (in memory)", "The same request twice: two payments (4.5)", "Cancelled after recording: failure shown (4.7)"))}</div>
      <div class="rule step" data-label="Next">{ul("Units 5&ndash;8: networking, persistence, security, concurrency")}</div>
    </div>
  </div>""", notes(('SAY', 'Even with MVVM and Clean Architecture, the demo has limits. Click through: no real backend, payments are simulated in memory; no durable persistence, account state is lost when the repository instance goes away; no authentication; no server-enforced idempotency, the local guard does not prevent distributed duplicates; no authoritative status reconciliation, unknown remote outcomes are not implemented.'),
                  ('SAY', 'Click: we met most of these with real runs: every relaunch starts at ₹25,000.00 again; the same request submitted twice became two payments in 4.5; a task cancelled after recording reported failure in 4.7.'),
                  ('SAY', 'Click: these are exactly the concerns of the coming units: networking in Unit 5, persistence in Unit 6, authentication and security in Unit 7, concurrency in Unit 8.'),
                  ('CONNECT', 'Unit 4 in one table.'))))

# ================================================================== Part 6 (10, 12)
divider(6, "Unit 4 complete", "Ten lessons, one architecture", 'And where NPay goes next.', 'The summary.')
SUM = [("4.1", "Architecture fundamentals", "Separation of concerns"), ("4.2", "MVVM", "PaymentViewModel"), ("4.3", "Observation", "@Observable, @Bindable"),
       ("4.4", "Dependency injection", "Protocol-based services"), ("4.5", "Repository pattern", "Actor-isolated account data"), ("4.6", "Domain models &amp; use cases", "SendPaymentUseCase"),
       ("4.7", "UI state modeling", "Explicit payment lifecycle"), ("4.8", "Modular architecture", "Feature folders, Swift packages"), ("4.9", "Architecture testing", "Unit, async, integration tests"),
       ("4.10", "Final integration", "End-to-end MVVM architecture")]
S.append(slide("Part 6 &middot; Unit 4 learning summary (section 10)", "Every lesson is in the running app", f"""  <div class="body">
    {tbl(["Lesson", "Topic", "Main NPay concept"], SUM, 'tbl compact')}
    <p class="small muted" style="margin:6px 0 0">The text notes the consolidated Xcode project as still outstanding; here every lesson&rsquo;s code was built, run and tested.</p>
  </div>""", notes(('SAY', 'All ten lessons: architecture fundamentals and separation of concerns; MVVM and PaymentViewModel; Observation, @Observable and @Bindable; dependency injection with protocol-based services; the repository pattern with actor-isolated data; domain models and SendPaymentUseCase; UI state modelling and the explicit payment lifecycle; modular architecture with feature folders and Swift packages; architecture testing; and today&rsquo;s end-to-end integration.'),
                  ('SAY', 'The text ends by saying the consolidated Xcode project and its tests remain outstanding. In this course, every lesson&rsquo;s code was built and run in the simulator and its tests executed, and today&rsquo;s app is the consolidated result.'),
                  ('CONNECT', 'The road ahead.'))))

# ================================================================== wrap-up
recap_u1('4.10', (), [("layers", "Layers with one reason to change", "views, ViewModels, use case, repository"),
                      ("db", "One repository, one truth", "Home, History and Payments: 2,349,950"),
                      ("check", "Verified, not assumed", "14 checks on the app; 21 tests green")],
          'Three things to remember from Unit 4. NPay is now layered, presentation, application, domain and infrastructure, with every component owning one reason to change and dependencies pointing at the domain. Home, History and Payments all derive from one repository, created once by NPayDependencies and refreshed deliberately after each payment, without letting a failed refresh undo a success. And the architecture is verified rather than assumed: the acceptance checklist on the running app, and twenty-one tests across every layer.')

review_divider(11)
review([("phone", "Choose one", "Which component should own SwiftUI layout?",
         "Which component should own SwiftUI layout?<br>A. SendPaymentUseCase<br>B. PaymentsScreen<br>C. AccountRepository", "B",
         "Views lay out; ViewModels and use cases don&rsquo;t.",
         "Leaking layout into logic.", "Most pick B.", None),
        ("gear", "Choose one", "Which component enforces application-level payment policy?",
         "Which component should enforce application-level payment policy?<br>A. PaymentViewModel<br>B. SendPaymentUseCase / PaymentPolicy<br>C. NPayRouter", "B",
         "The policy runs before the repository call.",
         "Putting rules in the ViewModel.", "Most pick B.", None),
        ("key", "Choose one", "Why should AccountRepository be an abstraction?",
         "Why should AccountRepository be an abstraction?<br>A. To separate application logic from storage details<br>B. To generate animations<br>C. To replace all tests", "A",
         "In-memory today, API in Unit 5.",
         "Coupling the use case to storage.", "Most pick A.", None),
        ("shield", "Choose one", "What protects the in-memory balance update from interleaving?",
         "What protects the in-memory balance update from interleaving?<br>A. TextField validation<br>B. TabView<br>C. An actor-isolated, non-suspending operation", "C",
         "Concurrent test: one of two payments recorded.",
         "Trusting UI checks.", "Most pick C.", None),
        ("link", "Question", "Does actor isolation automatically provide backend idempotency?",
         "Does actor isolation automatically provide backend idempotency?", "No",
         "The same request twice became two payments.",
         "Confusing safety with idempotency.", "Most say no.", None),
        ("db", "Choose one", "After a confirmed payment, the dashboard refresh fails. Then&hellip;",
         "What should happen after a confirmed payment but a failed dashboard refresh?<br>A. Treat the payment as failed<br>B. Preserve success; report the refresh failure separately<br>C. Submit the payment again", "B",
         "Our reload() sets refreshFailed; the payment stays recorded.",
         "Retrying a payment that succeeded.", "Most pick B.", None),
        ("decision", "Choose one", "Which component should manage navigation paths?",
         "Which component should manage navigation paths?<br>A. NPayRouter<br>B. AccountRepository<br>C. PaymentPolicy", "A",
         "paymentsPath held the success route.",
         "Navigating from data layers.", "Most pick A.", None),
        ("file", "Choose one", "Why use an immutable payment command for confirmation?",
         "Why use an immutable payment command for confirmation?<br>A. To improve rendering speed<br>B. To eliminate all concurrency issues<br>C. To submit exactly what the user reviewed", "C",
         "4.6: the command paid 150050, the fields would have paid 200000.",
         "Re-reading the form on Confirm.", "Most pick C.", None),
        ("layers", "Choose one", "What does dependency injection improve?",
         "What does dependency injection improve?<br>A. Replaceability and testability<br>B. Automatic database persistence<br>C. Automatic payment security", "A",
         "Mocks in tests; one repository in the app.",
         "Expecting DI to add features.", "Most pick A.", None),
        ("code", "Choose one", "Can a domain module depend on SwiftUI?",
         "Can a domain module depend on SwiftUI?<br>A. It must always import SwiftUI<br>B. It should generally remain independent<br>C. Only when using NavigationStack", "B",
         "NPayDomain imports Foundation only; it built and tested on the Mac.",
         "Letting the core depend on the UI.", "Most pick B.", None),
        ("eye", "Choose one", "From 4.9: a planted bug with 92% coverage unchanged. What caught it?",
         "From Lesson 4.9: a planted off-by-one bug left coverage at 92%. What caught it?<br>A. The coverage report<br>B. The at-limit boundary assertion<br>C. Nothing could", "B",
         "Without that test, 11 tests passed.",
         "Trusting coverage numbers.", "Most pick B.", "Spaced review from Lesson 4.9.")])

S.append(next_slide('4.10', [("5.1", "How iOS networking works", "URLSession, HTTP, DNS, TLS, back into the ViewModel"),
                             ("Unit 5", "Networking &amp; REST APIs", "an API-backed AccountRepository"),
                             ("Unit 6", "Persistence &amp; offline", "SwiftData, caching, sync"),
                             ("Units 7&ndash;12", "Production engineering", "auth, security, concurrency, testing, UIKit, CI/CD, capstone")],
                    'Unit 5 starts with Lesson 5.1, following a request from URLSession through HTTP, DNS, TLS and the network stack and back into NPay&rsquo;s ViewModel, then builds an API-backed repository behind today&rsquo;s contract. Unit 6 adds SwiftData persistence and offline data, and Units 7 to 12 the rest of production engineering.'))

S.append(lab_slide('4.10', "Unit 4 checkpoint", "The complete MVVM NPay, verified.",
                   ["Create NPayDependencies with one repository.",
                    "Move Home and History onto DashboardViewModel.",
                    "Refresh the dashboard after a successful payment.",
                    "Pay ₹1,500.50; expect ₹23,499.50 everywhere.",
                    "Run the 14-item checklist.",
                    "Run every test; all green."],
                   "", 'Expected, as in our run: the repository, dashboard, Home and History all agree on 2,349,950 paise; all 14 checks pass; 3 XCTest and 18 Swift Testing tests pass.',
                   side=f'<div>{card("You hand in", ul("Your NPayDependencies and DashboardViewModel", "Your checklist results", "Your test run"))}</div>'))

end_slide('4.10', 'Complete NPay MVVM<br>Integration', 'Unit 5 &middot; Lesson 5.1 &mdash; How iOS Networking Works Behind the Scenes',
          'You can now describe and verify a layered MVVM architecture with one source of truth, trace a payment through every layer, and name the risks that remain. Unit 4, Application Architecture and MVVM, is complete.',
          'Next, Unit 5, Lesson 5.1: how iOS networking works behind the scenes.')

write_deck(OUT410, '4.10', 'Complete NPay MVVM Integration', 'Complete NPay MVVM Integration')
