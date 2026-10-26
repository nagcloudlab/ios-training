"""Generates decks/unit-4/lesson-4.4/index.html from the Lesson 4.4 text (Dependency Injection in iOS; two parts,
Sections 1-21, Part 2 restarting at Section 14). Evidence: the text's code run on the Mac with NPay's real store
(section 18 labs, one submit() against three services, existential identity, ARC, a double submit), and tools/sim4_4
(NPay with PaymentService injected by NPayFactory, the review flow kept, demo / mock / failing mock / stale review)."""
import html, os, re, sys
OUT44 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.4', 'Dependency Injection<br>in iOS',
            'Make the payment feature <b>independent of how payments happen</b>: demo today, a mock in tests, an API tomorrow.',
            'Lesson 4.3 showed how @Observable lets SwiftUI react to the ViewModel. Today a different problem: PaymentViewModel depends directly on NPayStore. When the demo payments become a backend API, would we rewrite the ViewModel? We introduce a PaymentService contract, a demo and a mock implementation, a factory that assembles them, and we run the same ViewModel against all of them, including inside NPay itself.')
outcomes_slide('4.4', [("key", "Define dependency injection, and dependency inversion"),
                       ("file", "Design a service contract for payments"),
                       ("diff", "Swap implementations without touching the ViewModel"),
                       ("check", "Test success and failure with a mock"),
                       ("gear", "Assemble objects in a composition root"),
                       ("clock", "Match each dependency&rsquo;s lifetime to its job")])
where_slide('4.4', 'Today: who supplies the dependencies', (),
            '4.3: how Observation tracks the ViewModel.',
            'Dependency injection: contracts, mocks, factories.',
            'Last time we looked inside @Observable. Today we change what the ViewModel depends on: an abstract PaymentService instead of the concrete store. The text arrived in two parts; the second restarts at Section 14.',
            'The problem.')

# ================================================================== Part 1 (1, 2)
divider(1, "The problem", "One ViewModel, many implementations", 'Demo, mock, API: the ViewModel shouldn&rsquo;t care.', 'Three environments.')
P = []
P.append(box(330, 0, 420, 58, "PaymentViewModel", "form state, submission", None, '', 'layers'))
P.append(wire('M540 59V84' + head(540, 84, 'd')))
P.append(box(330, 86, 420, 58, "PaymentService protocol", "the contract", '1+', '', 'key'))
for i, (t, sub) in enumerate([("Demo", "local simulation"), ("Mock", "controlled test"), ("API", "future backend")]):
    x = i * 380
    P.append(wire(f'M{x + 160} 196L540 146', None, 'dash'))
    P.append(box(x, 198, 320, 56, t, sub, None, 'ghost' if i == 2 else '', ''))
S.append(slide("Part 1 &middot; Understand the problem (section 1)", "The ViewModel shouldn&rsquo;t know which one it gets", f"""  <div class="body">
    {cues(1)}
    {svg('0 0 1080 254', 'PaymentViewModel depends on a PaymentService protocol; demo, mock and API implementations conform', 'three', P, 'max-height:270px')}
    <div class="gap"></div>
    <div class="step">{code("Today, from Lesson 4.2", "private let store: NPayStore\n\ninit(store: NPayStore) { self.store = store }", "font-size:13px")}</div>
  </div>""", notes(('SAY', 'Imagine three environments for NPay: a local demo simulation, a controlled mock for tests, and a future backend API. One PaymentViewModel should work with all three. Click: the trick is a contract in the middle, a PaymentService protocol, that each implementation conforms to; dashed lines are conformances. The API one is greyed out: it doesn&rsquo;t exist yet.'),
                  ('SAY', 'Click: today the ViewModel holds an NPayStore directly. That works, but swapping demo payments for an API would mean rewriting it. The ViewModel shouldn&rsquo;t need to know which implementation it receives: that&rsquo;s the central idea of dependency injection.'),
                  ('CONNECT', 'What exactly is it?'))))

WITHOUT = """final class PaymentViewModel {
    private let service = DemoPaymentService()
}"""
WITH = """final class PaymentViewModel {
    private let service: PaymentService

    init(service: PaymentService) {
        self.service = service
    }
}"""
S.append(slide("Part 1 &middot; What is dependency injection? (section 2)", "Supply the dependency from outside", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Without injection", WITHOUT, "font-size:13.5px")}
        {card("Coupled", ul("The ViewModel creates its dependency", "Always DemoPaymentService"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("With injection", WITH, "font-size:13.5px")}</div>
        <div class="step">{card("Decoupled", ul("The ViewModel receives it", "The caller chooses the implementation"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A dependency is an object or capability another component needs to do its work. Dependency injection means supplying it from outside rather than constructing it inside. Without injection, the ViewModel creates a DemoPaymentService itself: it is coupled to that one class.'),
                  ('SAY', 'Click: with injection, the ViewModel stores a PaymentService and receives it in its initializer. Click: the caller decides which implementation to supply.'),
                  ('SAY', 'Nothing new in Swift: protocols, initializer parameters and reference types from Unit 1. Dependency injection is an architectural pattern, not a SwiftUI feature; Lesson 4.2&rsquo;s init(store:) was already a small case of it.'),
                  ('CONNECT', 'Write the contract.'))))

# ================================================================== Part 2 (3, 4)
divider(2, "The contract and the demo", "PaymentService, then DemoPaymentService", 'What, not how; then one how.', 'The contract.')
CONTRACT = """struct PaymentRequest {
    let recipient: String
    let amountPaise: Int
}

struct PaymentReceipt {
    let transactionID: UUID
    let recipient: String
    let amountPaise: Int
}

@MainActor
protocol PaymentService {
    func send(_ request: PaymentRequest) async throws
        -> PaymentReceipt
}"""
S.append(slide("Part 2 &middot; Our first dependency contract (section 3)", "A request in, a receipt out", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("PaymentService.swift (import Foundation)", CONTRACT, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Three types", ul("PaymentRequest: validated input", "PaymentReceipt: the result", "PaymentService: behaviour, no implementation"))}
        <div class="step">{card("async throws", ul("A real payment waits and can fail"))}</div>
        <div class="warn step" data-label="Simplification">{ul("@MainActor on the protocol, for this local lesson", "Revisited with networking")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Create PaymentService.swift. PaymentRequest represents the validated input we intend to submit: recipient and amount in paise. PaymentReceipt is the result after the operation: the transaction ID, recipient and amount. PaymentService defines the behaviour, send a request and get a receipt, without saying how.'),
                  ('SAY', 'Click: send is async throws because a future implementation will involve asynchronous work and failures, a network call for instance, even though today&rsquo;s demo is immediate.'),
                  ('SAY', 'Click: the @MainActor on the protocol is a deliberate simplification for this local lesson; we revisit concurrency boundaries when networking is introduced in Unit 5.'),
                  ('CONNECT', 'The first implementation.'))))

DEMO = """enum PaymentServiceError: Error {
    case rejected
}

@MainActor
final class DemoPaymentService: PaymentService {
    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {
        guard let id = store.recordDemoPayment(
            recipient: request.recipient,
            amountPaise: request.amountPaise
        ) else {
            throw PaymentServiceError.rejected
        }
        return PaymentReceipt(
            transactionID: id,
            recipient: request.recipient,
            amountPaise: request.amountPaise)
    }
}"""
S.append(slide("Part 2 &middot; The demo implementation (section 4)", "It receives the shared store; it owns no balance", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("DemoPaymentService", DEMO, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What it does", ul("Calls <code>recordDemoPayment</code>", "nil &rarr; throws <code>.rejected</code>", "An ID &rarr; returns a receipt"))}
        <div class="step">{console("Mac, NPay&rsquo;s real NPayStore", ["send ₹1,500.50 &rarr; receipt", "store: 2,349,950 paise, 4 transactions"], 12)}</div>
        <div class="rule step" data-label="Single source of truth">{ul("The same store as Home and History")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The demo implementation. A small error enum with one case, rejected. DemoPaymentService receives an NPayStore in its initializer, and send asks the store to record the demo payment: if the store returns nil, it throws rejected; otherwise it returns a receipt with the store&rsquo;s transaction ID. It relies on recordDemoPayment returning an optional UUID, which ours does.'),
                  ('SAY', 'Click: we compiled the text&rsquo;s code on the Mac together with NPay&rsquo;s real NPayStore, Money and PaymentValidator: sending ₹1,500.50 produced a receipt and the store went to 2,349,950 paise with four transactions.'),
                  ('SAY', 'Click: what matters: DemoPaymentService does not own a new balance. It receives the same store Home and History use. A single source of truth, the lesson from 3.1 and 4.2 again.'),
                  ('CONNECT', 'Who creates whom?'))))

# ================================================================== Part 3 (5, 15)
divider(3, "Creation versus dependency", "Who builds it, who depends on it", 'And injection versus inversion.', 'Who creates whom.')
P = []
P.append('<text x="200" y="16" text-anchor="middle">Without injection</text><text x="760" y="16" text-anchor="middle">With injection</text>')
P.append(box(40, 30, 320, 56, "PaymentViewModel", "creates DemoPaymentService", '1', 'alert', 'layers'))
P.append(wire('M200 87V118' + head(200, 118, 'd')))
P.append(box(40, 120, 320, 56, "DemoPaymentService", "tightly coupled", None, '', 'db'))
P.append(box(560, 30, 400, 56, "Composition root", "creates and connects", '2', '', 'gear'))
P.append(wire('M660 87L620 118' + head(620, 118, 'd'), None, 'dash'))
P.append(wire('M860 87L900 118' + head(900, 118, 'd'), None, 'dash'))
P.append(box(500, 120, 240, 56, "PaymentViewModel", "", None, '', 'layers'))
P.append(box(780, 120, 240, 56, "DemoPaymentService", "", None, '', 'db'))
P.append(wire('M620 177L760 230' + head(760, 230, 'd'), '3+'))
P.append(wire('M900 177L760 230' + head(760, 230, 'd'), '3+'))
P.append(box(620, 232, 280, 56, "PaymentService", "the contract", '3+', '', 'key'))
S.append(slide("Part 3 &middot; Who creates whom? (section 5)", "Creation in one place; dependency on the contract", f"""  <div class="body">
    {cues(3)}
    {svg('0 0 1060 290', 'Without injection the ViewModel creates the service; with injection a composition root creates both and both depend on the contract', 'who', P, 'max-height:300px')}
    <p class="small muted" style="margin:6px 0 0">Dashed: creation. Solid: code dependency (the ViewModel uses it; the service conforms to it).</p>
  </div>""", notes(('SAY', 'Click: without injection, in orange: the ViewModel creates DemoPaymentService internally, tightly coupled to that implementation.'),
                  ('SAY', 'Click: with injection: a composition root creates and connects the objects, the dashed lines. Click: and in code, the ViewModel depends only on the PaymentService contract, while DemoPaymentService conforms to it, the solid lines. The diagram separates object creation from code dependencies: the root constructs the concrete service and hands it to the ViewModel.'),
                  ('CONNECT', 'Two terms that sound alike.'))))

DIP = [("Dependency Injection", "A technique", "Supply dependencies from outside"),
       ("Dependency Inversion Principle", "A design principle", "Policy and details both depend on abstractions")]
S.append(slide("Part 3 &middot; Injection versus inversion (section 15)", "A technique and a principle", f"""  <div class="body">
    {tbl(["", "What it is", "Says"], DIP, 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Injection without inversion", ul("Inject a concrete class: no protocol", "<code>init(store: NPayStore)</code> in 4.2"))}</div>
      <div class="step">{card("Inversion undermined", ul("A protocol exists&hellip;", "&hellip;but the consumer still constructs the concrete type"))}</div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Together">{ul("Often combined; neither guarantees the other")}</div>
  </div>""", notes(('SAY', 'Dependency injection is a technique: supplying dependencies to a component. The dependency inversion principle is a design principle: high-level policy, here the payment ViewModel, should not depend directly on low-level details like DemoPaymentService; both should depend on an abstraction, the PaymentService protocol. In the text&rsquo;s before-and-after diagram, the arrows are source-code dependencies and conformance, not the runtime call sequence.'),
                  ('SAY', 'Click: you can inject a concrete class without any protocol: Lesson 4.2&rsquo;s init(store: NPayStore) was injection without inversion. Click: and you can define an abstraction yet still construct the concrete implementation inside the consumer, undermining the separation.'),
                  ('SAY', 'Click: they often work together, but neither automatically guarantees the other.'),
                  ('CONNECT', 'Refactor the ViewModel.'))))

# ================================================================== Part 4 (6, 7, 16)
divider(4, "The refactored ViewModel", "It knows only PaymentService", 'Submission through the contract.', 'The code.')
VM = """private let service: any PaymentService   // init(service:)
func submit() async -> PaymentReceipt? {
    guard !isSubmitting else { return nil }
    let trimmed = recipient.trimmingCharacters(
        in: .whitespacesAndNewlines)
    guard let amount = Money.parsePaise(amountText),
          amount > 0, !trimmed.isEmpty else {
        errorMessage = "Check your payment details."
        return nil
    }
    let request = PaymentRequest(recipient: trimmed,
                                 amountPaise: amount)
    isSubmitting = true
    defer { isSubmitting = false }
    do {
        let receipt = try await service.send(request)
        recipient = ""; amountText = ""; errorMessage = nil
        return receipt
    } catch {
        errorMessage = "Payment could not be completed."
        return nil
    }
}"""
S.append(slide("Part 4 &middot; Refactor PaymentViewModel (section 6)", "No DemoPaymentService, no NPayStore", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:22px;align-items:start">
      {code("PaymentViewModel.submit() (condensed)", VM, "font-size:10px;line-height:1.45")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("submit()", ul("Guard, parse, check", "Send through the service", "Clear the form, or set an error"))}
        <div class="step">{card("The balance check?", ul("Not here: the service enforces it", "Demo, ₹30,000 &rarr; &ldquo;Payment could not be completed.&rdquo;"))}</div>
        <div class="warn step" data-label="Standalone">{ul("Review is reconnected in Part 7")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The ViewModel keeps the input properties and gains isSubmitting. Its only dependency is now any PaymentService, received in the initializer. submit() refuses a second submit while one is running; parses the amount and checks the recipient, setting "Check your payment details." if they fail; builds a PaymentRequest with the trimmed recipient; sets isSubmitting, with a defer to clear it; sends through the service; on success clears the form, on failure sets "Payment could not be completed."'),
                  ('SAY', 'The ViewModel no longer knows DemoPaymentService or NPayStore. Click: the service enforces the balance at execution time. On the Mac, ₹30,000 against a ₹25,000 balance came back as the generic "Payment could not be completed.": the store refused it and the demo service threw rejected. Lesson 4.7&rsquo;s structured UI state can say why.'),
                  ('SAY', 'Click: the text is explicit that this is a standalone submission experiment; the review sheet and confirmation are reconnected during integration, which we did, Part 7.'),
                  ('CONNECT', 'What does "any" mean here?'))))

S.append(slide("Part 4 &middot; Why any PaymentService? (sections 7, 16)", "An existential: one value, any conforming type", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 7", "private let service: any PaymentService", "font-size:14px")}
        {card("any", ul("Holds a value of some conforming type", "Demo or Mock, decided by the caller", "Makes existential use explicit"))}
        <div class="step">{card("Protocol required?", ul("No: concrete types can be injected", "Use one when it earns its keep"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Section 16, measured on the Mac", ["viewModel&rsquo;s stored service === the service passed in:&ensp;<b>true</b>", "MemoryLayout&lt;any PaymentService&gt;.size: 40 bytes", "MemoryLayout&lt;DemoPaymentService&gt;.size:&ensp;&ensp;8 bytes"], 11.5)}</div>
        <div class="rule step" data-label="No copy">{ul("Assigning to an existential creates no new service", "The layout is an implementation detail")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'PaymentService is a protocol. any PaymentService stores a value whose concrete type conforms to it: DemoPaymentService or MockPaymentService. The any keyword makes existential use explicit. Click: is a protocol required for dependency injection? No: you can inject concrete types. Protocols pay off when multiple implementations, testing or an abstraction boundary justify them; a protocol for every class adds complexity.'),
                  ('SAY', 'Click: Section 16 asks whether any PaymentService creates a new service instance. We checked on the Mac: reading the ViewModel&rsquo;s stored service back with Mirror gives the very same object, identity true. For interest: the existential box is 40 bytes on this Mac, room for a value plus type information, while a class reference is 8; but the precise representation and dispatch are compiler implementation details.'),
                  ('SAY', 'Click: assigning a class instance to an existential-typed property does not construct a new service object.'),
                  ('CONNECT', 'Now the payoff: a mock.'))))

# ================================================================== Part 5 (8, 9, 18)
divider(5, "Mocks and testing", "Control the dependency, test the ViewModel", 'Success and failure, deterministic.', 'The mock.')
MOCK = """@MainActor
final class MockPaymentService: PaymentService {

    var shouldFail = false
    private(set) var requests: [PaymentRequest] = []

    func send(
        _ request: PaymentRequest
    ) async throws -> PaymentReceipt {
        requests.append(request)
        if shouldFail {
            throw PaymentServiceError.rejected
        }
        return PaymentReceipt(
            transactionID: UUID(),
            recipient: request.recipient,
            amountPaise: request.amountPaise)
    }
}"""
SAME = [("Demo", "₹1,500.50", "nil (store 2,349,950)"), ("Mock, success", "₹1,500.50", "nil (store untouched)"),
        ("Mock, failure", "nil", "could not be completed"), ("Demo, ₹30,000", "nil", "could not be completed"),
        ("Mock, &ldquo;abc&rdquo;", "nil", "check your details (not sent)")]
S.append(slide("Part 5 &middot; A mock service, and one call three ways (sections 8&ndash;9)", "await viewModel.submit(), unchanged", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:22px;align-items:start">
      {code("MockPaymentService", MOCK, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Injected", "Receipt", "errorMessage"], SAME, 'tbl compact')}
          <p class="small muted" style="margin:6px 0 0">Mac run; the same submit() each time.</p></div>
        <div class="rule step" data-label="Only the implementation differs">{ul("No real store, no network for the mock")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The mock records every request it receives in requests, readable but not writable from outside, and can be told to fail with shouldFail. Otherwise it returns a receipt with a fresh UUID. It modifies no store and makes no network request.'),
                  ('SAY', 'Click: the text&rsquo;s interactive experiment, run for real on the Mac: the same ViewModel, the same await viewModel.submit(), different injected services. Demo: a receipt, and the real store dropped to 2,349,950. Mock succeeding: a receipt, store untouched. Mock failing: no receipt, "Payment could not be completed." Demo with thirty thousand rupees: the store refused, the same message. Mock with "abc": the ViewModel never sent anything, "Check your payment details."'),
                  ('SAY', 'Click: the ViewModel contract stayed the same; only the injected implementation differed.'),
                  ('CONNECT', 'Turn that into tests.'))))

LAB = """@MainActor
func runPaymentViewModelLab() async {
    let mock = MockPaymentService()
    let viewModel = PaymentViewModel(service: mock)

    viewModel.recipient = "ravi@npay"
    viewModel.amountText = "1500.50"

    let receipt = await viewModel.submit()

    assert(receipt != nil)
    assert(mock.requests.count == 1)
    assert(mock.requests[0].amountPaise == 150_050)

    print("PaymentViewModel test passed")
}"""
S.append(slide("Part 5 &middot; Testing without SwiftUI (section 18)", "Success and failure, in milliseconds", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:22px;align-items:start">
      {code("Section 18 (the failure lab sets mock.shouldFail = true)", LAB, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Mac, Debug build (asserts active)", ["PaymentViewModel test passed", "Failure-path test passed"], 13)}</div>
        <div class="step">{card("Proved", ul("Submission goes through the protocol", "₹1,500.50 became 150,050 paise", "On failure: errorMessage set, isSubmitting false"))}</div>
        <div class="step">{console("Ours: two submits at once, a slow mock", ["receipts 1, requests sent <b>1</b>"], 12)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 18 tests the ViewModel with the mock. Create a mock, inject it, set ravi@npay and 1500.50, await submit, and assert: a receipt came back, the mock received exactly one request, and its amount was 150,050 paise. The failure lab sets shouldFail and asserts no receipt, an error message, and isSubmitting back to false.'),
                  ('SAY', 'Click: we ran both on the Mac in a Debug build, where assert is active: "PaymentViewModel test passed", "Failure-path test passed". Click: that proves submission works through the protocol, the rupee text became paise correctly, and the failure path leaves the ViewModel consistent, without launching NPay, showing a sheet or making a network request. Lesson 4.9 turns these into a real test suite.'),
                  ('SAY', 'Click: one more, ours: a mock that waits 300 milliseconds, and two submits started together. One receipt, one request: the isSubmitting guard held because the first submit was suspended in the service when the second arrived.'),
                  ('CONNECT', 'Where are the objects assembled?'))))

# ================================================================== Part 6 (10, 11, 12, 17, 19)
divider(6, "Composition and lifetime", "Assemble in one place; own deliberately", 'Factories, injection styles, ARC, scopes.', 'The factory.')
FACT = """@MainActor
enum NPayFactory {

    static func makePaymentViewModel(
        store: NPayStore
    ) -> PaymentViewModel {

        let service = DemoPaymentService(store: store)

        return PaymentViewModel(service: service)
    }
}"""
CE = [("Passed in the initializer", "Supplied through the view hierarchy"), ("Explicit at the call site", "Convenient for descendants"),
      ("ViewModels, services, repositories", "Shared UI context"), ("Required dependencies are visible", "Needs deliberate setup")]
S.append(slide("Part 6 &middot; The composition root (sections 10&ndash;11, 19)", "One factory builds the feature", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("App/NPayFactory.swift", FACT, "font-size:12.5px")}
        <div class="step">{card("A framework?", ul("Not yet: a factory is enough", "Containers can hide ownership"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Constructor injection", "Environment injection"], CE, 'tbl compact')}</div>
        <div class="rule step" data-label="NPay">{ul("Constructor: services, repositories", "Environment: presentation preferences (3.9)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Where are dependencies assembled? In a composition root. NPayFactory centralizes construction: makePaymentViewModel takes the shared store, builds a DemoPaymentService with it, and returns a ViewModel with that service. NPay&rsquo;s root owns the store; a payment feature root owns the ViewModel in @State, so it is not recreated in body and the draft survives tab changes, Lessons 4.2 and 4.3.'),
                  ('SAY', 'Click: should NPay use a dependency injection framework? Not yet: a few shared dependencies, a simple factory. A container helps when construction rules, scopes and graphs grow complex, but introduced too early it hides the ownership and initialization we are trying to master.'),
                  ('SAY', 'Click: two injection styles. Constructor injection passes the dependency in the initializer, explicit at the call site, good for ViewModels and services, required dependencies visible. Environment injection supplies it through the view hierarchy, convenient for descendants, good for shared UI context, but it needs deliberate setup: Lesson 3.9 showed a missing environment object crashing. Click: NPay uses constructor injection for payment services and repositories, the environment for presentation preferences. Neither manages persistence or security for you.'),
                  ('CONNECT', 'Who keeps whom alive?'))))

P = []
for i, (t, ic) in enumerate([("PaymentViewModel", "layers"), ("DemoPaymentService", "db"), ("NPayStore", "db")]):
    x = i * 330
    P.append(box(x, 40, 280, 56, t, '', '1+' if i == 2 else None, '', ic))
    if i < 2:
        P.append(wire(f'M{x + 281} 68H{x + 328}' + head(x + 328, 68, 'r')))
P.append(box(660, 150, 280, 50, "App root", "also owns the store", None, '', 'gear'))
P.append(wire('M800 149V98' + head(800, 98, 'u')))
LIFE = [("Transient", "A short-lived validation helper"), ("Feature", "PaymentViewModel, for a payment workflow"), ("Application", "NPayStore, NPayRouter, owned by the root")]
S.append(slide("Part 6 &middot; Lifetime and ARC (sections 12, 17)", "Strong references point one way", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 940 200', 'PaymentViewModel holds DemoPaymentService, which holds NPayStore; the app root also owns the store', 'arc', P, 'max-height:210px')}
        <div class="step">{console("Mac: a factory-built ViewModel leaves scope", ["PaymentViewModel deinit", "DemoPaymentService deinit", "store still 2,349,950 (the root holds it)"], 12)}</div></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Lifetime", "NPay example"], LIFE, 'tbl compact')}</div>
        <div class="rule step" data-label="Match the job">{ul("A store per screen: inconsistent balances (4.2)", "Design choices, not SwiftUI scopes")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Both the service and the ViewModel are reference types. The ViewModel holds the service strongly; the service holds the store strongly; the application root also owns the store. Click: no cycle: the store never references the ViewModel.'),
                  ('SAY', 'Click: we checked on the Mac: a ViewModel built by the factory, left to go out of scope. PaymentViewModel deinit, then DemoPaymentService deinit, and the store, still owned elsewhere, kept its balance. Dependency injection doesn&rsquo;t remove ARC concerns, but explicit ownership makes them easy to reason about.'),
                  ('SAY', 'Click: lifetimes. Transient: a short-lived validation helper. Feature: the PaymentViewModel for an active workflow. Application: NPayStore and NPayRouter, owned by the root. These are design choices, not automatic SwiftUI scopes. Click: give each payment screen its own store and balances diverge, Lesson 4.2 measured that; make every helper application-wide and you extend lifetimes for nothing. The lifetime should match the responsibility.'),
                  ('CONNECT', 'Now, NPay itself.'))))

# ================================================================== Part 7 (13, 20, 21 + integration)
divider(7, "Dependency injection in NPay", "Same screen; three services", 'The review flow kept; the service swapped.', 'The integration.')
INTC = """// PaymentsFeatureRoot
_viewModel = State(initialValue:
    NPayFactory.makePaymentViewModel(store: store))

// PaymentsScreen: the review sheet's Confirm
PaymentReviewSheet(request: request) {
    Task {
        pendingSuccessID =
            await viewModel.submit()?.transactionID
        self.review = nil
    }
}"""
RES = [("Demo", "success", "₹23,499.50 + row", "cleared"),
       ("Mock, succeeding", "success", "₹25,000.00", "cleared"),
       ("Mock, failing", "error", "₹25,000.00", "kept"),
       ("Demo, stale review", "error", "unchanged", "kept")]
S.append(slide("Part 7 &middot; Xcode lab, integrated (section 13)", "Swap the service; nothing else changes", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Our integration (review flow kept)", INTC, "font-size:11.5px")}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Service", "Confirm", "Home", "Form"], RES, 'tbl compact')}
          <p class="small muted" style="margin:6px 0 0">Simulator; the mock is injected through a debug hook in the factory; mock.requests: [ravi@npay 150050].</p></div>
        <div class="rule step" data-label="Checklist">{ul("Concrete services in the ViewModel: 0")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The lab, done in NPay, flagged as ours. PaymentsFeatureRoot now gets its ViewModel from NPayFactory. The review flow stays: Review Payment still prepares Lesson 4.2&rsquo;s snapshot for the sheet, and the sheet&rsquo;s Confirm now starts a Task that awaits viewModel.submit() and passes the receipt&rsquo;s ID on for navigation. To keep 4.2&rsquo;s balance validation and the "Available" line, the factory also gives the ViewModel a read-only balance closure; the ViewModel still never sees the store type.'),
                  ('SAY', 'Click: then the same screens with three services. Demo: Payment Recorded, Home ₹23,499.50, History "Sent to ravi@npay", form cleared. A succeeding mock, injected through a debug hook in the factory: Payment Recorded again, but Home still ₹25,000.00 and no History row, because the mock touches no store; it recorded one request, ravi@npay, 150,050 paise. A failing mock: the inline "Payment could not be completed.", no navigation, the draft kept for another try. And the stale review from 4.2: the demo service refused, same message.'),
                  ('SAY', 'Click: the checklist&rsquo;s last item: the ViewModel contains no concrete service construction. We searched it: zero occurrences of DemoPaymentService or NPayStore.'),
                  ('CONNECT', 'What that looks like.'))))

S.append(slide("Part 7 &middot; The same screens, a mock behind them (section 13)", "Mock success, then mock failure", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:180px 180px minmax(0,1fr);gap:20px;align-items:start">
      {PHONE("img/mock.png", "Mock: success screen", 180)}
      <div class="step">{PHONE("img/mockfail.png", "Mock: failure, draft kept", 180)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Success with the mock", ul("The screen can&rsquo;t tell", "The balance didn&rsquo;t move"))}
        <div class="step">{card("Failure with the mock", ul("Deterministic: no real store or network needed", "The ViewModel&rsquo;s error, shown inline"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Left: the success screen after a payment through the succeeding mock: the screen cannot tell which service produced the receipt; the balance did not move.'),
                  ('SAY', 'Click: right: the failing mock. "Payment could not be completed." under the fields, the draft kept. That failure is deterministic: we didn&rsquo;t need a broken network or an empty account to see it, which is exactly what tests need.'),
                  ('CONNECT', 'Should everything get a protocol?'))))

P = []
AR = [("gear", "NPayRootView / composition root", "owns shared dependencies"), ("phone", "PaymentsScreen", "SwiftUI presentation"),
      ("layers", "PaymentViewModel", "form state, submission"), ("key", "PaymentService protocol", "abstract payment contract"), ("db", "DemoPaymentService", "uses the shared NPayStore")]
for i, (ic, t, sub) in enumerate(AR):
    y = i * 62
    P.append(box(0, y, 560, 52, t, sub, '1+' if i == 3 else None, '', ic))
    if i < 4:
        P.append(wire(f'M280 {y + 53}V{y + 60}' + head(280, y + 60, 'd')))
S.append(slide("Part 7 &middot; Useful boundaries; NPay after 4.4 (sections 20&ndash;21)", "Protocols where they earn their place", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 560 300', 'Composition root, PaymentsScreen, PaymentViewModel, PaymentService protocol, DemoPaymentService', 'arch', P, 'max-height:310px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Use a protocol for", ul("Swapping a payment implementation", "Isolating infrastructure", "Testing important behaviour"))}</div>
        <div class="step">{card("Prefer a concrete type for", ul("A simple, stable formatter", "Anything with one implementation"))}</div>
        <div class="rule step" data-label="Unit 5">{ul("A backend behind the same contract")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPay after this lesson: the root composes shared dependencies; PaymentsScreen presents; PaymentViewModel holds form state and coordinates submission; click: it depends on the PaymentService protocol; DemoPaymentService implements it with the shared store. The ViewModel is independent of the concrete demo implementation.'),
                  ('SAY', 'Click: but abstractions are not free: every protocol is a contract to maintain. Use one where it provides a meaningful boundary: replacing a payment implementation, isolating infrastructure, testing important behaviour. Click: for a simple, stable formatter with one implementation, a protocol, factory, mock and container add more complexity than value. Good architecture is about useful boundaries, not the number of protocols.'),
                  ('SAY', 'Click: in Unit 5 a backend arrives behind this same contract, without rewriting the SwiftUI payment screen.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.4', (), [("key", "Receive, don&rsquo;t create", "the ViewModel holds any PaymentService"),
                     ("check", "Mocks make tests deterministic", "success and failure, no store, no network"),
                     ("gear", "A factory assembles; lifetimes match jobs", "store app-wide, ViewModel per feature")],
          'Three things to remember. Dependency injection means a component receives what it needs instead of creating it: PaymentViewModel now holds any PaymentService and never mentions the store or the demo class, and dependency inversion is the principle that makes the abstraction worth having. Because of that, a mock can drive success and failure deterministically, on the Mac or inside NPay, without changing a line of the ViewModel. And one factory assembles the objects, with each lifetime matching its job: the store application-wide, the ViewModel per feature.')

review_divider(10)
review([("key", "Choose one", "What is dependency injection?",
         "What is dependency injection?<br>A. Creating every dependency inside the ViewModel<br>B. Storing dependencies in UserDefaults<br>C. Supplying dependencies from outside a component", "C",
         "<code>init(service:)</code>: the caller chooses.",
         "Thinking DI needs a framework.", "Most pick C.", None),
        ("file", "Question", "Does dependency injection always require a protocol?",
         "Does dependency injection always require a protocol?", "No",
         "4.2&rsquo;s <code>init(store: NPayStore)</code> injected a concrete type.",
         "A protocol for every class.", "Some say yes.", None),
        ("check", "Choose one", "Why use a MockPaymentService?",
         "Why use a MockPaymentService?<br>A. To control behaviour during testing<br>B. To replace the iOS runtime<br>C. To persist transactions automatically", "A",
         "shouldFail: a failure on demand.",
         "Waiting for real failures to test.", "Most pick A.", None),
        ("gear", "Choose one", "Who should create DemoPaymentService?",
         "Who should create DemoPaymentService?<br>A. BalanceCard<br>B. The composition root or factory<br>C. Every TextField", "B",
         "NPayFactory builds it with the shared store.",
         "Scattering construction across views.", "Most pick B.", None),
        ("db", "Question", "Should DemoPaymentService create an independent NPayStore?",
         "Should DemoPaymentService create an independent NPayStore?", "No",
         "A second store means a second balance (4.2).",
         "Losing the single source of truth.", "Most say no.", None),
        ("link", "Question", "Does dependency injection automatically prevent retain cycles?",
         "Does dependency injection automatically prevent retain cycles?", "No",
         "No cycle here only because the store doesn&rsquo;t point back.",
         "Assuming a pattern manages memory.", "Some say yes.", None),
        ("layers", "Choose one", "What does any PaymentService represent?",
         "What does <code>any PaymentService</code> represent?<br>A. A new background thread<br>B. An existential value conforming to PaymentService<br>C. A SwiftUI navigation destination", "B",
         "And it holds the same object: identity true.",
         "Thinking it copies or creates a service.", "Most pick B.", None),
        ("phone", "Predict the result", "MockPaymentService succeeds inside NPay. Home shows?",
         "NPay runs with a succeeding MockPaymentService injected. You pay ₹1,500.50 and return to Home. The balance shows&hellip;<br>A. ₹23,499.50<br>B. ₹25,000.00<br>C. An error", "B",
         "The mock returns a receipt; it touches no store.",
         "Assuming the success screen means money moved.", "Many pick A.", None),
        ("code", "Predict the result", "submit() with amountText \"abc\": how many requests reach the mock?",
         "With amountText \"abc\", <code>await viewModel.submit()</code> sends how many requests to the mock?<br>A. 0<br>B. 1<br>C. It crashes", "A",
         "The ViewModel stops at parsing: &ldquo;Check your payment details.&rdquo;",
         "Expecting the service to validate everything.", "Some pick B.", None),
        ("eye", "Question", "From 4.3: is a ViewModel's let dependency tracked by Observation?",
         "From Lesson 4.3: does <code>@Observable</code> track a ViewModel&rsquo;s <code>private let service</code>?", "No",
         "Only stored vars get @ObservationTracked; a let never changes.",
         "Expecting every property to be observed.", "Some say yes.", "Spaced review from Lesson 4.3.")])

S.append(next_slide('4.4', [("4.5", "Repository pattern", "data access behind a protocol, like PaymentService"),
                            ("4.6", "Use cases", "SendPaymentUseCase between ViewModel and service"),
                            ("4.9", "Architecture testing", "today&rsquo;s asserts become a test suite"),
                            ("Unit 5", "Networking", "an API implementation of the same contract")],
                    'Lesson 4.5 applies the same idea to data access: repository protocols with in-memory, cached and eventually API implementations behind the same ViewModel. 4.6 adds a use case between ViewModel and service, 4.9 turns today&rsquo;s asserts into a test suite, and Unit 5 writes the API implementation.'))

S.append(lab_slide('4.4', "Inject the payment service", "Contract, demo, mock, factory.",
                   ["Add PaymentRequest, PaymentReceipt, PaymentService.",
                    "Write DemoPaymentService with the shared store.",
                    "Write MockPaymentService.",
                    "Inject the service; build it in NPayFactory.",
                    "Keep the review flow; Confirm calls submit().",
                    "Run section 18&rsquo;s two labs; then NPay with the mock."],
                   "", 'Expected, as in our run: both labs print "passed"; the demo service moves the balance to ₹23,499.50, a succeeding mock shows success with the balance unchanged, a failing mock shows the error and keeps the draft.',
                   side=f'<div>{card("You hand in", ul("Your service files and factory", "Console output of both labs", "Screenshots: demo, mock success, mock failure"))}</div>'))

end_slide('4.4', 'Dependency Injection<br>in iOS', 'Lesson 4.5 &mdash; Repository Pattern',
          'You can now inject a service through a protocol, test a ViewModel with a mock, assemble objects in a composition root, tell injection from inversion, and match each dependency&rsquo;s lifetime to its job.',
          'Next, Lesson 4.5: the repository pattern, separating NPay&rsquo;s data access from payment behaviour.')

write_deck(OUT44, '4.4', 'Dependency Injection in iOS', 'Dependency Injection in iOS')
