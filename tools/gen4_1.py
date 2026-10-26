"""Generates decks/unit-4/lesson-4.1/index.html from the Lesson 4.1 text (Why iOS Applications Need Architecture;
Sections 1-11). Evidence: PaymentValidator run on the Mac and as a Swift package with Swift Testing (5 tests), the
repository contract run, sizes of NPayStore and PaymentsScreen in the 3.12 code, and tools/sim4_1 (NPay with the
validator integrated: the same behaviour checks give identical results before and after the refactoring)."""
import html, os, re, sys
OUT41 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.1', 'Why iOS Applications<br>Need Architecture',
            'NPay works at 500 lines. What happens at <b>50,000</b>? MVC, MVVM and Clean Architecture, through NPay&rsquo;s own problems.',
            'Unit 3 left NPay with a working architecture for navigation, payment forms, review sheets, history and shared state. Before we add networking and databases, we improve how the code is organised. The question for today: why does an app that works perfectly at 500 lines become hard to maintain at 50,000? We answer it with NPay&rsquo;s own code, make our first small refactoring, and prove the app still behaves exactly the same.')
outcomes_slide('4.1', [("layers", "Name the responsibilities an app must separate"),
                       ("diff", "Compare MVC, MVVM and Clean Architecture"),
                       ("decision", "Describe NPay&rsquo;s target architecture"),
                       ("check", "Extract business rules into plain Swift"),
                       ("key", "Explain why repository protocols matter"),
                       ("gear", "Refactor while preserving observable behaviour")])
where_slide('4.1', 'Today: organising NPay&rsquo;s code', (),
            '3.12: the complete Unit 3 app, verified.',
            'Architecture: why and where we&rsquo;re heading.',
            'Lesson 3.12 ended Unit 3 with a verified app and a list of limitations: the store holds payment rules, screens reach the shared store directly, and nothing is tested automatically. Unit 4 addresses exactly those. Today is the why and the first small step.',
            'The problem.')

# ================================================================== Part 1 (1)
divider(1, "The problem", "One store, too many jobs", 'What works at 500 lines breaks at 50,000.', 'NPayStore today.')
STORE = """@MainActor
@Observable
final class NPayStore {
    var balancePaise = 2_500_000
    var transactions: [Transaction] = []
    var paymentDraft = PaymentDraft()

    func recordDemoPayment(
        recipient: String,
        amountPaise: Int
    ) -> UUID? {
        // Validate recipient
        // Validate amount
        // Check balance
        // Deduct money
        // Create transaction
        // Update history
    }
}"""
P = []
P.append(box(330, 150, 300, 64, "NPayStore", "application state + payment logic", None, 'solid', 'db'))
RS = [("Balance", 0, 0), ("Transactions", 330, 0), ("Payment validation", 660, 0), ("Payment execution", 0, 300), ("Draft state", 330, 300), ("Future networking", 660, 300)]
for i, (t, x, y) in enumerate(RS):
    P.append(box(x, y, 300, 52, t, '', f'{i + 1}' if i < 5 else None, 'alert' if i == 5 else '', ''))
    cx = x + 150
    P.append(wire(f'M{cx} {y + 53 if y == 0 else y - 1}L480 {149 if y == 0 else 215}', None, 'faint' if i == 5 else ''))
S.append(slide("Part 1 &middot; The problem with our current NPay architecture (section 1)", "Every new feature lands in NPayStore", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:22px;align-items:start">
      {code("NPayStore (outline from the text)", STORE, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:10px">
        <div>{cues(5)}{svg('0 0 960 352', 'NPayStore with balance, transactions, payment validation, payment execution, draft state and future networking', 'grow', P, 'max-height:250px')}</div>
        <div class="step">{card("Next: backend API, biometrics, persistence, limits, retries", ul("Where would each one go?"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Our NPayStore holds the balance, the transactions and the payment draft, and its recordDemoPayment validates the recipient and amount, checks the balance, deducts money, creates the transaction and updates history. For a learning prototype, that works.'),
                  ('SAY', 'Click through what it is responsible for: the balance; the transactions; payment validation; payment execution; the draft state. And in orange, the one we have not added yet: networking.'),
                  ('SAY', 'Click: NPay now needs a backend API, biometric authentication, persistence, payment limits and retry handling. If every one of them lands in NPayStore, it becomes one large object with too many responsibilities.'),
                  ('CONNECT', 'What goes wrong, concretely?'))))

SZ = [("<code>NPayStore</code>", "63", "balance, transactions, draft, payment rules"), ("<code>PaymentsScreen</code>", "160", "6 state properties; 14 uses of the store"),
      ("<code>NPayRootView</code>", "92", "owners, tabs, every route&rsquo;s screen")]
S.append(slide("Part 1 &middot; What could go wrong? (section 1)", "Change, test, replace: all harder", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Change", ul("Edit validation, break unrelated state"))}
        <div class="step">{card("Test", ul("Testing payment logic needs the whole store"))}</div>
        <div class="step">{card("Replace", ul("Swap demo payments for an API: the UI is coupled to networking"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Our 3.12 code", "Lines", "Holds"], SZ)}
          <p class="small muted" style="margin:6px 0 0">Counted in the Unit 3 app (authored measurement).</p></div>
        <div class="rule step" data-label="Architecture">{ul("Manages these dependencies")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s three risks. Change: if we change payment validation, we might accidentally affect unrelated state. Click: test: to test payment logic, we may need to construct the entire store. Click: replace: when local demo payments become an API, the UI could become tightly coupled to networking.'),
                  ('SAY', 'Click: a measurement from our own Unit 3 app: NPayStore is sixty-three lines; PaymentsScreen is a hundred and sixty, with six state properties and fourteen uses of the store; NPayRootView, ninety-two. Small today, but every one of those numbers grows with each feature.'),
                  ('SAY', 'Click: architecture helps us manage these dependencies.'),
                  ('CONNECT', 'So what is architecture?'))))

# ================================================================== Part 2 (2, 3)
divider(2, "What architecture is", "Clear responsibilities, clear boundaries", 'And three well-known shapes.', 'The responsibilities.')
RESP = [("phone", "Presentation", "what the user sees"), ("layers", "Presentation state", "what the screen needs to display"), ("check", "Business rules", "what makes a payment valid"),
        ("db", "Data access", "where account data comes from"), ("decision", "Navigation", "where the user goes next")]
P = []
for i, (ic, t, sub) in enumerate(RESP):
    x = i * 228
    P.append(tall(x, 0, 208, 120, ic, t, sub, f'{i + 1}' if i < 4 else '5+', ''))
S.append(slide("Part 2 &middot; What is application architecture? (section 2)", "Divide responsibilities; define how they talk", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 120', 'Presentation, presentation state, business rules, data access, navigation', 'resp', P, 'max-height:128px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("In NPay today", ul("PaymentsScreen: presentation <i>and</i> rules", "NPayStore: data <i>and</i> rules", "NPayRouter: navigation only"))}</div>
      <div class="rule step" data-label="Goal">{ul("Clear boundaries between these five")}</div>
    </div>
  </div>""", notes(('SAY', 'Application architecture defines how responsibilities are divided and how components communicate. For NPay we want to separate five things. Click: presentation, what the user sees. Click: presentation state, what the screen needs to display. Click: business rules, what makes a payment valid. Click: data access, where account and transaction information comes from. Click: navigation, where the user goes next.'),
                  ('SAY', 'Click: in NPay today, the Payments screen holds presentation and validation rules; the store holds data and rules too; only the router is already clean, a single responsibility since Lesson 3.2. Click: the goal is clear boundaries between all five.'),
                  ('CONNECT', 'Three common shapes for those boundaries.'))))

P = []
for c, (name, items, l) in enumerate([("MVC", ["View", "Controller", "Model"], '1'), ("MVVM", ["View", "ViewModel", "Model"], '2+'), ("Clean", ["UI", "Use Cases", "Domain"], '3')]):
    x = c * 380
    P.append(f'<text x="{x + 170}" y="18" text-anchor="middle">{name}</text>')
    for r, t in enumerate(items):
        y = 34 + r * 82
        P.append(box(x + 20, y, 300, 56, t, '', l if r == 1 else None, '', ''))
        if r < 2:
            P.append(wire(f'M{x + 170} {y + 57}V{y + 80}' + head(x + 170, y + 80, 'd')))
COMP = [("MVC", "Controller coordinates views and models", "Historically common in UIKit"),
        ("MVVM", "ViewModel holds the screen&rsquo;s state and behaviour", "Fits SwiftUI&rsquo;s state-driven model"),
        ("Clean", "Dependency direction; rules apart from technology", "Complements MVVM")]
S.append(slide("Part 2 &middot; MVC, MVVM and Clean Architecture (section 3)", "Three shapes; NPay uses MVVM plus Clean ideas", f"""  <div class="body">
    {cues(3)}{svg('0 0 1100 260', 'MVC: view, controller, model; MVVM: view, ViewModel, model; Clean: UI, use cases, domain', 'mvx', P, 'max-height:200px')}
    <p class="small muted" style="margin:4px 0 10px">Simplified teaching diagrams: real architectures have more relationships.</p>
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:18px">
      {"".join(card(n, ul(i, nt)) for n, i, nt in COMP)}
    </div>
  </div>""", notes(('SAY', 'Three shapes, as simplified teaching diagrams. Click: MVC, Model-View-Controller, historically common in UIKit: the controller coordinates user interaction and updates between views and models.'),
                  ('SAY', 'Click: MVVM, Model-View-ViewModel: the ViewModel holds the state and behaviour a screen needs, separate from how the screen looks. It fits SwiftUI&rsquo;s state-driven approach naturally. Click: Clean Architecture emphasises dependency direction and keeping business rules apart from external technologies such as networking and storage. It complements MVVM rather than replacing it.'),
                  ('SAY', 'NPay&rsquo;s choice, in the title: MVVM for presentation, with domain use cases and repository abstractions introduced incrementally across Unit 4.'),
                  ('CONNECT', 'What that looks like for one feature.'))))

# ================================================================== Part 3 (4, 7)
divider(3, "Where we&rsquo;re heading", "View, ViewModel, use case, repository", 'The direction for all of Unit 4.', 'The target.')
TGT = [("phone", "SwiftUI View", "PaymentsScreen: renders the form"), ("layers", "ViewModel", "PaymentViewModel: form state, submission"),
       ("check", "Use Case", "SendPaymentUseCase: payment rules"), ("key", "Repository Protocol", "PaymentRepository: abstracts payments"),
       ("db", "Implementation", "DemoPaymentRepository now; an API later")]
P = []
for i, (ic, t, sub) in enumerate(TGT):
    y = i * 68
    P.append(box(0, y, 620, 56, t, sub, f'{i + 1}' if i < 4 else '5+', '', ic))
    if i < 4:
        P.append(wire(f'M310 {y + 57}V{y + 66}' + head(310, y + 66, 'd')))
S.append(slide("Part 3 &middot; Our target NPay architecture (section 4)", "Five layers for the payment feature", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:22px;align-items:start">
      <div>{cues(5)}{svg('0 0 620 328', 'SwiftUI view, ViewModel, use case, repository protocol, implementation', 'tgt', P, 'max-height:340px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Each layer knows less", ul("The view: nothing about rules", "The ViewModel: nothing about layout", "The use case: nothing about storage"))}</div>
        <div class="rule step" data-label="Unit 4">{ul("Built toward lesson by lesson")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The direction for Unit 4. Click: the SwiftUI view, PaymentsScreen, renders the form. Click: the ViewModel, PaymentViewModel, manages form state and submission. Click: the use case, SendPaymentUseCase, applies the payment rules. Click: the repository protocol, PaymentRepository, abstracts payment operations. Click: the implementation: DemoPaymentRepository now, an API implementation later.'),
                  ('SAY', 'Click: each layer knows less than the one before it needs to: the view nothing about rules, the ViewModel nothing about layout, the use case nothing about where data is stored. Click: we build toward this across Unit 4, one lesson at a time.'),
                  ('CONNECT', 'How state flows through it.'))))

FL = [("tap", "User taps Confirm", "SwiftUI Button action"), ("layers", "PaymentViewModel", "coordinates, exposes UI state"), ("check", "SendPaymentUseCase", "applies payment rules"),
      ("db", "PaymentRepository", "performs the operation"), ("layers", "ViewModel receives result", "success or error state"), ("phone", "SwiftUI updates", "shows the result")]
P = []
for i, (ic, t, sub) in enumerate(FL):
    y = i * 58
    P.append(box(0, y, 520, 48, t, sub, f'{i + 1}' if i < 5 else '6+', '', ic))
    if i < 5:
        P.append(wire(f'M260 {y + 49}V{y + 56}' + head(260, y + 56, 'd')))
S.append(slide("Part 3 &middot; How MVVM changes state flow (section 7) &middot; conceptual", "The view delegates; the ViewModel coordinates", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      <div>{cues(6)}{svg('0 0 520 338', 'Confirm tap, ViewModel, use case, repository, result, SwiftUI update', 'flow', P, 'max-height:350px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Unit 3", ul("The view called the shared store directly"))}
        <div class="step">{card("The ViewModel doesn&rsquo;t know", ul("The physical layout of the screen"))}</div>
        <div class="step">{card("The view doesn&rsquo;t know", ul("Whether payments are in memory or an API"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'In Unit 3 our view called the shared store directly. With MVVM, the view delegates. Click through: the user taps Confirm, a SwiftUI Button action; the PaymentViewModel coordinates submission and exposes UI state; the SendPaymentUseCase executes the payment rules; the PaymentRepository performs the operation; the ViewModel receives the result and updates success or error state; SwiftUI updates the screen.'),
                  ('SAY', 'This is the target, conceptually; none of the use case or repository exists in NPay yet. Click: the ViewModel does not need to know the physical layout of the payment screen. Click: and the view does not need to know whether the repository uses in-memory data or an API.'),
                  ('CONNECT', 'Let&rsquo;s take the first small step.'))))

# ================================================================== Part 4 (5, 6)
divider(4, "First refactoring", "Move validation out of the View", 'A pure Swift validator, testable alone.', 'The code.')
VAL = """enum PaymentValidationError: Error {
    case emptyRecipient
    case invalidAmount
    case insufficientBalance
}

struct PaymentValidator {

    func validate(
        recipient: String,
        amountPaise: Int,
        balancePaise: Int
    ) throws {

        guard !recipient.trimmingCharacters(
            in: .whitespacesAndNewlines
        ).isEmpty else {
            throw PaymentValidationError.emptyRecipient
        }

        guard amountPaise > 0 else {
            throw PaymentValidationError.invalidAmount
        }

        guard amountPaise <= balancePaise else {
            throw PaymentValidationError.insufficientBalance
        }
    }
}"""
S.append(slide("Part 4 &middot; Move validation out of the View (section 5)", "PaymentValidator: rules without SwiftUI", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("PaymentValidator.swift (import Foundation)", VAL, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Three rules, three errors", ul("Recipient not blank", "Amount above zero", "Amount within the balance"))}
        <div class="step">{card("What changed", ul("No dependency on SwiftUI", "Callable from a ViewModel, a use case, a test"))}</div>
        <div class="rule step" data-label="First step">{ul("Toward testable architecture")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Start small. Our payment form validates the amount inside the SwiftUI view. We extract a pure Swift validation component: an error enum with three cases, empty recipient, invalid amount, insufficient balance; and a PaymentValidator struct whose validate method takes the recipient, the amount in paise and the balance in paise, and throws.'),
                  ('SAY', 'The rules: the recipient, trimmed of whitespace, must not be empty; the amount must be above zero; the amount must not exceed the balance. Only Foundation is imported. Click: the rules no longer depend on SwiftUI: we can call them from a ViewModel, a use case or a unit test. Click: this is our first step toward a testable architecture.'),
                  ('CONNECT', 'Test it without launching NPay.'))))

TST = """let validator = PaymentValidator()

do {
    try validator.validate(
        recipient: "ravi@npay",
        amountPaise: 150_000,
        balancePaise: 2_500_000
    )

    print("Valid payment")
} catch {
    print("Validation failed:", error)
}"""
CASES = [("\"ravi@npay\", 150,050", "valid"), ("\"&ensp;&ensp;&ensp;\", 150,000", "emptyRecipient"), ("\"ravi@npay\", 0", "invalidAmount"),
         ("\"ravi@npay\", &minus;100", "invalidAmount"), ("\"ravi@npay\", 3,000,000", "insufficientBalance"), ("\"ravi@npay\", 2,500,000", "valid (the whole balance)")]
S.append(slide("Part 4 &middot; Test the validator without launching NPay (section 6)", "No screen, no simulator", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 6", TST, "font-size:12px")}
        <div class="step">{console("Output (Mac, swiftc)", ["Valid payment"], 14)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Input (balance 2,500,000)", "Result"], CASES)}
          <p class="small muted" style="margin:6px 0 0">More cases, run the same way (ours).</p></div>
        <div class="step">{console("swift test (Swift Testing, ours)", ["&#10004; Test run with 5 tests in 1 suite passed"], 12.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s test: create a validator, validate ravi@npay, ₹1,500 against ₹25,000, print "Valid payment" or the error. Click: we compiled it on the Mac with swiftc, no app, no simulator: "Valid payment".'),
                  ('SAY', 'Click: more cases, run the same way: a blank recipient throws emptyRecipient; zero and negative amounts throw invalidAmount; thirty thousand rupees against twenty-five thousand throws insufficientBalance; the whole balance exactly is valid, because the rule is less than or equal.'),
                  ('SAY', 'Click: and as real unit tests: we put the validator in a small Swift package with five Swift Testing tests, valid, blank, zero, over the balance and the whole balance, and swift test passed all five. Testing business rules without rendering a screen is one of the major benefits of separating domain logic from presentation; Lesson 4.9 does this for ViewModels and use cases.'),
                  ('CONNECT', 'The next abstraction: where payments go.'))))

# ================================================================== Part 5 (8)
divider(5, "Protocols", "Depend on a contract, not an implementation", 'Swap demo for API without touching ViewModels.', 'The protocol.')
REPO = """protocol PaymentRepository {
    func sendPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> UUID
}

struct DemoPaymentRepository: PaymentRepository {
    func sendPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> UUID {
        UUID()
    }
}"""
S.append(slide("Part 5 &middot; Why protocols matter (section 8)", "One contract, many implementations", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("PaymentRepository and a demo conformance", REPO, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Called through any PaymentRepository (Mac)", ["id: 455AE80B-DDD4-48D2-AD5C-125C804069CF", "balancePaise afterwards: 2500000"], 12)}</div>
        <div class="warn step" data-label="Contract only">{ul("Returns an ID; changes no balance, no history", "A real demo repository comes later (4.5)")}</div>
        <div class="step">{card("From Unit 1", ul("Protocols, async, throws", "Dependency abstraction"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Suppose NPay first uses an in-memory payment repository and later a network-backed one. We do not want to rewrite every ViewModel. So we define an abstraction: PaymentRepository, with one async throwing method, sendPayment, returning the new payment&rsquo;s UUID. Different implementations conform to the same contract; DemoPaymentRepository is the simplest.'),
                  ('SAY', 'Click: we called it through the protocol type on the Mac: it returned an ID, and the balance was unchanged. Click: that is the text&rsquo;s point: this implementation is only a contract demonstration; it does not update NPay&rsquo;s balance or history. A real in-memory demo repository connected to account state comes in Lesson 4.5.'),
                  ('SAY', 'Click: these are Unit 1 fundamentals at work: protocol-oriented programming, async and throwing functions, and dependency abstraction.'),
                  ('CONNECT', 'Now the lab: refactor without changing behaviour.'))))

# ================================================================== Part 6 (10)
divider(6, "Refactor safely", "Same app, better structure", 'The validator inside NPay; behaviour checked before and after.', 'The change.')
INT = """// PaymentsScreen
private var isValid: Bool {
    guard let amount = parsedAmount else {
        return false
    }
    do {
        try PaymentValidator().validate(
            recipient: store.paymentDraft.recipient,
            amountPaise: amount,
            balancePaise: store.balancePaise)
        return true
    } catch {
        return false
    }
}"""
BH = [("empty recipient, ₹1", "disabled", "disabled"), ("blank recipient, ₹1", "disabled", "disabled"), ("zero amount", "disabled", "disabled"),
      ("₹30,000 (over the balance)", "disabled", "disabled"), ("₹25,000 (the whole balance)", "enabled", "enabled"),
      ("₹1,500.50 &rarr; confirm", "₹23,499.50", "₹23,499.50"), ("store: &ldquo;&rdquo;, ₹30,000, ₹0", "rejected", "rejected")]
S.append(slide("Part 6 &middot; Xcode lab: first architecture refactoring (section 10)", "Move the rules; prove nothing else moved", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Calling the validator (ours)", INT, "font-size:11px")}
        {card("Also", ul("<code>NPayStore.recordDemoPayment</code> calls it"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Same script, simulator", "3.12 code", "4.1 code"], BH)}</div>
        <div class="rule step" data-label="Practice">{ul("Refactor the structure; keep observable behaviour")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The lab: create PaymentValidator.swift, move the validation logic into it, and call it from the existing payment code. We did exactly that in NPay, flagged as ours: the Payments screen&rsquo;s isValid now asks the validator, and the store&rsquo;s recordDemoPayment calls the same validator instead of repeating the rules.'),
                  ('SAY', 'Click: then the important part: verify. One script drove the real app, once on the Unit 3 code and once on the refactored code. Empty, blank, zero and over-the-balance inputs kept Review Payment disabled in both; the whole balance enabled it in both; a ₹1,500.50 payment ended at ₹23,499.50 in both; and the store refused an empty recipient, thirty thousand rupees and zero in both. Identical.'),
                  ('SAY', 'Click: that is the practice: refactor the architecture while preserving observable behaviour, and check it, rather than assume it.'),
                  ('CONNECT', 'What the user sees for an invalid amount.'))))

S.append(slide("Part 6 &middot; Invalid payments are still rejected (section 10)", "Same message, same disabled button", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:180px minmax(0,1fr);gap:24px;align-items:start">
      {PHONE("img/invalid.png", "₹30,000 against ₹25,000", 180)}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("On screen", ul("&ldquo;Enter a valid amount within your balance.&rdquo;", "Review Payment disabled"))}
        <div class="step">{card("Noticed", ul("The same message shows for an empty recipient", "It names the amount even when the recipient is wrong"))}</div>
        <div class="rule step" data-label="Next">{ul("The validator&rsquo;s error cases can drive specific messages: 4.2 and 4.7")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The refactored app with thirty thousand rupees against a balance of twenty-five thousand: the same message as before, and Review Payment disabled.'),
                  ('SAY', 'Click: something the before-and-after run surfaced: the message also appears when the recipient is empty, and it talks about the amount. That was true before the refactoring too; we preserved behaviour, including this. Click: now that validation throws specific errors, the ViewModel in Lesson 4.2 and the UI-state modelling in Lesson 4.7 can turn them into specific messages.'),
                  ('CONNECT', 'Where Unit 4 goes from here.'))))

# ================================================================== Part 7 (9)
divider(7, "Unit 4 roadmap", "Ten lessons to a complete MVVM NPay", 'One step per lesson.', 'The sequence.')
SEQ = [("4.1", "Architecture fundamentals", "Extract payment validation"), ("4.2", "MVVM internals", "PaymentViewModel"),
       ("4.3", "Observation framework", "Observable ViewModels"), ("4.4", "Dependency injection", "Inject repositories and services"),
       ("4.5", "Repository pattern", "Demo payment repository"), ("4.6", "Domain models and use cases", "SendPaymentUseCase"),
       ("4.7", "UI state modeling", "Loading, success, error"), ("4.8", "Modular project structure", "Feature organization"),
       ("4.9", "Architecture testing", "ViewModel and use-case tests"), ("4.10", "Integration lab", "Complete MVVM NPay")]
S.append(slide("Part 7 &middot; Unit 4 learning sequence (section 9)", "From a validator to a complete MVVM app", f"""  <div class="body">
    {tbl(["Lesson", "Topic", "NPay implementation"], SEQ, 'tbl compact')}
  </div>""", notes(('SAY', 'The Unit 4 sequence. Today, architecture fundamentals and the extracted validator. 4.2, MVVM internals and the PaymentViewModel. 4.3, the Observation framework behind observable ViewModels. 4.4, dependency injection of repositories and services. 4.5, the repository pattern with a real demo payment repository. 4.6, domain models and the SendPaymentUseCase. 4.7, UI state: loading, success, error. 4.8, modular project structure. 4.9, testing ViewModels and use cases. 4.10, the integration lab: a complete MVVM NPay.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.1', (), [("layers", "Separate responsibilities", "presentation, state, rules, data, navigation"),
                     ("diff", "MVVM plus Clean ideas", "ViewModel per screen; use cases and repositories behind it"),
                     ("check", "Refactor, then verify", "PaymentValidator: 5 tests pass; NPay behaves the same")],
          'Three things to remember. An app stays maintainable when responsibilities are separated: presentation, presentation state, business rules, data access and navigation, each with clear boundaries; NPayStore and PaymentsScreen are where ours blur. NPay&rsquo;s direction is MVVM for presentation, with use cases and repository protocols behind it, Clean Architecture ideas complementing MVVM. And our first step was small and verified: the payment rules now live in a plain Swift PaymentValidator that five unit tests exercise without an app, and the same behaviour script gives identical results before and after.')

review_divider(9)
review([("layers", "Choose one", "What is the main responsibility of a ViewModel?",
         "What is the main responsibility of a ViewModel?<br>A. Store Xcode build settings<br>B. Manage screen state and presentation behaviour<br>C. Draw pixels manually", "B",
         "State and behaviour for one screen; SwiftUI draws.",
         "Turning the ViewModel into a second view.", "Most pick B.", None),
        ("diff", "Question", "Can MVVM and Clean Architecture be used together?",
         "Can MVVM and Clean Architecture be used together?", "Yes",
         "MVVM for presentation; use cases and repositories behind it.",
         "Treating architectures as either/or.", "Most say yes.", None),
        ("check", "Choose one", "Why extract PaymentValidator from SwiftUI?",
         "Why extract PaymentValidator from SwiftUI?<br>A. To improve SF Symbols<br>B. To create a new process<br>C. To make rules independently testable", "C",
         "Five tests ran with no app and no simulator.",
         "Thinking extraction is about speed.", "Most pick C.", None),
        ("key", "Choose one", "What does a repository protocol provide?",
         "What does a repository protocol provide?<br>A. An abstraction for data operations<br>B. A tab bar<br>C. A new application window", "A",
         "Demo now, API later, same contract.",
         "Coupling ViewModels to one data source.", "Most pick A.", None),
        ("phone", "Question", "Should a ViewModel directly control pixel rendering?",
         "Should a ViewModel directly control pixel rendering?", "No",
         "It exposes state; the view and SwiftUI render it.",
         "Mixing layout into the ViewModel.", "Most say no.", None),
        ("code", "Predict the result", "validate(\"ravi@npay\", 2,500,000, balance 2,500,000)?",
         "<code>validate(recipient: \"ravi@npay\", amountPaise: 2_500_000, balancePaise: 2_500_000)</code>. What happens?<br>A. Returns normally<br>B. Throws insufficientBalance<br>C. Throws invalidAmount", "A",
         "The rule is <code>&lt;=</code>: the whole balance is allowed.",
         "Off-by-one on a boundary.", "Some pick B.", None),
        ("code", "Predict the result", "validate(\"   \", 150,000, 2,500,000)?",
         "<code>validate(recipient: \"   \", amountPaise: 150_000, balancePaise: 2_500_000)</code> throws&hellip;<br>A. Nothing<br>B. emptyRecipient<br>C. invalidAmount", "B",
         "Whitespace is trimmed before the empty check.",
         "Forgetting the trim.", "Some pick A.", None),
        ("db", "Choose one", "DemoPaymentRepository.sendPayment: what happens to the balance?",
         "After <code>try await DemoPaymentRepository().sendPayment(recipient: \"ravi@npay\", amountPaise: 150_050)</code>, NPay&rsquo;s balance is&hellip;<br>A. ₹23,499.50<br>B. ₹25,000.00<br>C. Undefined", "B",
         "A contract demo: it returns an ID and touches no state.",
         "Assuming a conformance does real work.", "Some pick A.", None),
        ("decision", "Choose one", "From 3.12: who owns paymentsPath?",
         "From Lesson 3.12: who owns <code>paymentsPath</code>?<br>A. NPayStore<br>B. PaymentsScreen<br>C. NPayRouter", "C",
         "Navigation state belongs to the router.",
         "Mixing navigation into the data owner.", "Most pick C.", "Spaced review from Lesson 3.12.")])

S.append(next_slide('4.1', [("4.2", "MVVM internals", "PaymentViewModel calls PaymentValidator"),
                            ("4.5", "Repository pattern", "a real demo repository behind PaymentRepository"),
                            ("4.6", "Use cases", "SendPaymentUseCase owns the rules"),
                            ("4.9", "Architecture testing", "tests like today&rsquo;s five, for ViewModels too")],
                    'Lesson 4.2 builds PaymentViewModel on top of today&rsquo;s validator. Lesson 4.5 gives PaymentRepository a real in-memory implementation; 4.6 moves the rules into SendPaymentUseCase; 4.9 extends today&rsquo;s five tests to ViewModels and use cases.'))

S.append(lab_slide('4.1', "First architecture refactoring", "Extract the rules; keep the behaviour.",
                   ["Create <code>PaymentValidator.swift</code>.",
                    "Move the payment rules into it.",
                    "Call it from the payment form and the store.",
                    "Run five cases before and after; compare.",
                    "Optional: add Swift Testing tests.",
                    "Note which messages could be more specific."],
                   "", 'Expected, as in our run: identical results before and after; valid payments still reach ₹23,499.50 and invalid ones stay disabled or refused.',
                   side=f'<div>{card("You hand in", ul("Your validator and its call sites", "Your before/after table", "Optional: a passing swift test run"))}</div>'))

end_slide('4.1', 'Why iOS Applications<br>Need Architecture', 'Lesson 4.2 &mdash; MVVM Internals &amp; PaymentViewModel',
          'You can now explain why NPay needs architecture, compare MVC, MVVM and Clean Architecture, describe the target layers, extract business rules into testable Swift, and refactor without changing behaviour.',
          'Next, Lesson 4.2: MVVM internals, building NPay&rsquo;s first observable ViewModel.')

write_deck(OUT41, '4.1', 'Why iOS Applications Need Architecture', 'Why iOS Applications Need Architecture')
