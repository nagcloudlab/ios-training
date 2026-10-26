"""Generates decks/unit-4/lesson-4.6/index.html from the Lesson 4.6 text (Domain Models, Use Cases & Clean Architecture;
Part 1 Sections 1-9, Part 2 Sections 10-16, a continuation from Section 16 to 23). Evidence: the text's code on the Mac
(value objects, sections 14/15/22 labs, overlapping early checks, a daily limit checked early vs inside the actor, the
reviewed command vs mutable fields) and tools/sim4_6 (NPay's payment feature on SendPaymentUseCase through an adapter
repository over NPayStore; review shows and Confirm submits the immutable command)."""
import html, os, re, sys
OUT46 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

MAC = 'Mac run, the text&rsquo;s code'
title_slide('4.6', 'Domain Models, Use Cases<br>&amp; Clean Architecture',
            'Who owns the <b>business rules of sending money</b>? Not the screen, not the database: a use case.',
            'Lesson 4.5 gave NPay an account repository. Today&rsquo;s question: who owns the business rules of sending money? We introduce domain value objects that cannot hold invalid values, a SendPaymentUseCase that represents the operation itself, a payment policy, and the dependency rule. Then we test the rules without any UI, push concurrent payments against them, and connect the use case to NPay&rsquo;s real review flow.')
outcomes_slide('4.6', [("check", "Model money and recipients as value objects"),
                       ("file", "Turn form text into an immutable command"),
                       ("layers", "Write a use case for one business operation"),
                       ("diff", "Apply the dependency rule"),
                       ("shield", "Enforce concurrency-sensitive rules at the mutation"),
                       ("key", "Submit exactly what the user reviewed")])
where_slide('4.6', 'Today: the payment operation itself', (),
            '4.5: AccountRepository on an actor.',
            'Domain models, SendPaymentUseCase, the dependency rule.',
            'Last time data access got its own boundary. Today the business operation does. The text came in three pieces: Part 1, Part 2, and a continuation from Section 16 that finishes the lesson.',
            'The milestone.')

# ================================================================== Part 1 (1, 2)
divider(1, "Domain models", "Business concepts, not screens", 'Where the rules of sending money live.', 'The milestone.')
P = []
EV = [("phone", "PaymentsScreen", "collects input, shows results"), ("layers", "PaymentViewModel", "screen state"), ("check", "SendPaymentUseCase", "application payment rules"),
      ("key", "AccountRepository", "account operations"), ("db", "InMemoryAccountRepository", "demo account data")]
for i, (ic, t, sub) in enumerate(EV):
    y = i * 62
    P.append(box(0, y, 560, 52, t, sub, '1+' if i == 2 else None, '', ic))
    if i < 4:
        P.append(wire(f'M280 {y + 53}V{y + 60}' + head(280, y + 60, 'd')))
S.append(slide("Part 1 &middot; Our engineering milestone (sections 1&ndash;2)", "A component that is the operation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 560 300', 'Screen, ViewModel, SendPaymentUseCase, AccountRepository, InMemoryAccountRepository', 'evo', P, 'max-height:300px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Domain concepts in NPay", ul("Money, Account, Payment", "Recipient, Transaction, Payment status"))}</div>
        <div class="step">{code("UI editing state vs domain value", 'var amountText = "1500.50"   // form\nlet amountPaise = 150_050     // domain', "font-size:12px")}</div>
        <div class="rule step" data-label="Why separate">{ul("&ldquo;1500.&rdquo; is fine while typing", "It isn&rsquo;t a payment amount")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Who owns the rules of sending money? Should the ViewModel validate limits? Should the repository decide whether a payment is allowed? Click: today a new component appears: SendPaymentUseCase, representing the application operation "send money to a recipient", between the ViewModel and the repository.'),
                  ('SAY', 'Click: a domain model represents concepts belonging to the business: money, account, payment, recipient, transaction, payment status. They exist independently of SwiftUI, Xcode or any database.'),
                  ('SAY', 'Click: compare the form&rsquo;s amountText, "1500.50", UI editing state, with the domain&rsquo;s 150,050 paise, a validated monetary quantity. Click: "1500." is valid intermediate text while the user types, but it is not a completed payment amount; the domain should hold meaningful business values, not arbitrary input.'),
                  ('CONNECT', 'Build those values.'))))

# ================================================================== Part 2 (3, 4, 5)
divider(2, "Value objects", "Invalid states hard to represent", 'PaymentAmount, PaymentRecipient, the command.', 'Amount.')
VO = """struct PaymentAmount: Equatable, Sendable {
    let paise: Int

    init(paise: Int) throws {
        guard paise > 0 else {
            throw PaymentDomainError.invalidAmount
        }
        self.paise = paise
    }
}

struct PaymentRecipient: Equatable, Sendable {
    let identifier: String

    init(_ identifier: String) throws {
        let trimmed = identifier.trimmingCharacters(
            in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else {
            throw PaymentDomainError.invalidRecipient
        }
        self.identifier = trimmed
    }
}"""
VOR = ["PaymentAmount(paise: 150050)&ensp;&rarr; 150050", "PaymentAmount(paise: 0)&ensp;&ensp;&ensp;&ensp;&rarr; throws invalidAmount", "PaymentAmount(paise: -100)&ensp;&rarr; throws invalidAmount",
       "PaymentRecipient(\"&ensp;ravi@npay \") &rarr; \"ravi@npay\"", "PaymentRecipient(\"&ensp;&ensp;&ensp;\")&ensp;&ensp;&ensp;&ensp;&rarr; throws invalidRecipient"]
S.append(slide("Part 2 &middot; PaymentAmount and PaymentRecipient (sections 3&ndash;4)", "Throwing initializers guard the invariants", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:22px;align-items:start">
      {code("Domain value objects (PaymentDomainError: invalidAmount, invalidRecipient, insufficientBalance, limitExceeded)", VO, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(MAC, VOR, 11)}</div>
        <div class="step">{card("Invariant", ul("A PaymentAmount is always positive", "A PaymentRecipient is never blank"))}</div>
        <div class="warn step" data-label="Only one rule">{ul("Positive can still exceed the balance or a limit")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Until now Money was a formatting utility. PaymentAmount, named so it does not clash with Money, wraps paise, and its throwing initializer refuses anything not positive. PaymentRecipient trims the identifier and refuses an empty one. Both throw PaymentDomainError, whose four cases are invalid amount, invalid recipient, insufficient balance and limit exceeded.'),
                  ('SAY', 'Click: run on the Mac: 150,050 is accepted; zero and minus a hundred throw invalidAmount; "ravi@npay" with spaces is trimmed; blanks throw invalidRecipient. Click: these are domain invariants: if you hold a PaymentAmount, it is positive; if you hold a PaymentRecipient, it is not blank. A value object makes invalid states hard to represent.'),
                  ('SAY', 'Click: but one invariant is not every rule: a positive amount can still exceed the balance or a limit. And real UPI recipient validation needs far more, with authoritative verification; NPay stays a simulation.'),
                  ('CONNECT', 'Combine them into a request.'))))

P = []
CV = [("frame", "TextField", "\"1500.50\""), ("code", "Money.parsePaise", "150050"), ("check", "PaymentAmount", "validated, positive"), ("file", "SendPaymentCommand", "recipient + amount"), ("gear", "SendPaymentUseCase", "executes")]
for i, (ic, t, sub) in enumerate(CV):
    x = i * 228
    P.append(tall(x, 0, 208, 110, ic, t, sub, f'{i + 1}' if i < 4 else '5+', ''))
    if i < 4:
        P.append(wire(f'M{x + 209} 55H{x + 226}' + head(x + 226, 55, 'r')))
S.append(slide("Part 2 &middot; A domain payment request (section 5)", "From text to command", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 110', 'TextField text, parsed paise, PaymentAmount, SendPaymentCommand, SendPaymentUseCase', 'conv', P, 'max-height:118px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("SendPaymentCommand", "struct SendPaymentCommand: Sendable {\n    let recipient: PaymentRecipient\n    let amount: PaymentAmount\n}", "font-size:13px")}
      <div class="step">{card("No UI types inside", ul("No Binding, TextField or View", "A meaningful application request"))}</div>
    </div>
  </div>""", notes(('SAY', 'The conversion from UI to domain, step by step. Click: the TextField holds "1500.50". Click: Money.parsePaise turns it into 150,050. Click: PaymentAmount validates it as a positive amount. Click: SendPaymentCommand pairs it with a validated recipient. Click: SendPaymentUseCase executes the operation.'),
                  ('SAY', 'SendPaymentCommand is just a recipient and an amount, both value objects, and Sendable. Click: it contains no Binding, TextField or View: it is a meaningful application request that would make sense with any user interface.'),
                  ('CONNECT', 'What executes it?'))))

# ================================================================== Part 3 (6, 7, 8)
divider(3, "Use cases", "One operation the application supports", 'SendPaymentUseCase, first version.', 'Definition.')
UC1 = """struct SendPaymentUseCase {
    let repository: any AccountRepository

    func execute(_ command: SendPaymentCommand)
        async throws -> PaymentRecord {
        let snapshot = try await repository.fetchSnapshot()

        guard command.amount.paise <= snapshot.balancePaise else {
            throw PaymentDomainError.insufficientBalance
        }

        let perPaymentLimitPaise = 100_000_00
        guard command.amount.paise <= perPaymentLimitPaise else {
            throw PaymentDomainError.limitExceeded
        }

        return try await repository.recordPayment(
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise)
    }
}"""
S.append(slide("Part 3 &middot; What is a use case? Build one (sections 6&ndash;7)", "SendPaymentUseCase, version 1", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:22px;align-items:start">
      {code("Section 7", UC1, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("A use case is", ul("An operation the app supports", "Not a screen, a table or a request"))}
        <div class="step">{card("Steps", ul("Snapshot; check balance", "Check a ₹1,00,000 limit (illustrative)", "Record; return the record"))}</div>
        <div class="warn step" data-label="Not final">{ul("The balance can change before recordPayment", "The repository must check again")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A use case represents an operation the application supports: SendPayment, FetchBalance, FetchTransactionHistory. It coordinates the rules and dependencies the operation needs. It is not a screen, not a database table, not necessarily a network request; sending money stays meaningful even if SwiftUI is replaced.'),
                  ('SAY', 'Click: version one uses Lesson 4.5&rsquo;s repository. It fetches a snapshot, rejects the payment if the amount exceeds the balance, applies an illustrative per-payment limit of ₹1,00,000, which is not a statement of actual UPI limits, then asks the repository to record the payment and returns the record.'),
                  ('SAY', 'Click: the text&rsquo;s concurrency detail: the early balance check expresses the rule but is not the final guarantee; another operation can change the balance between fetchSnapshot and recordPayment. That is why the repository revalidates atomically. Part 6 measures exactly this.'),
                  ('CONNECT', 'So which rules go where?'))))

RULES = [("Amount positive", "Domain value object", "Defensive validation"), ("Recipient non-empty", "Domain value object", "Defensive validation"),
         ("Per-payment limit", "Use-case policy", "May also need enforcement"), ("Sufficient balance", "Preliminary check", "Atomic final check"),
         ("Record transaction", "Requests the operation", "Performs it")]
S.append(slide("Part 3 &middot; Why not every rule in the repository? (section 8)", "Policy in the use case; integrity at the data", f"""  <div class="body">
    {tbl(["Rule", "Use case", "Repository"], RULES, 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Different jobs", ul("Use case: application policy", "Repository: data integrity, data operations"))}</div>
      <div class="warn step" data-label="Real payments">{ul("Authoritative limits and balance checks: the trusted backend")}</div>
    </div>
  </div>""", notes(('SAY', 'Repositories and use cases have different responsibilities: the use case represents application policy; the repository protects data integrity and performs data operations. Some rules are enforced at both boundaries for different reasons.'),
                  ('SAY', 'The text&rsquo;s table: positive amount and non-empty recipient are guaranteed by the value objects, and validated defensively again by the repository. The per-payment limit is use-case policy, though authoritative enforcement may also be required. Sufficient balance: a preliminary check in the use case, the atomic final check in the repository. Recording: the use case requests it, the repository performs it.'),
                  ('SAY', 'Click: different jobs. Click: and for a real payment system, authoritative limits and balance checks belong on the trusted backend; the exact division depends on the domain and the backend contract.'),
                  ('CONNECT', 'Test the use case, no UI.'))))

# ================================================================== Part 4 (9, 14, 15, 22)
divider(4, "Testing the domain", "Rules, without a simulator", 'Labs from sections 14, 15 and 22.', 'The runs.')
S.append(slide("Part 4 &middot; Test the use case and policy (sections 14, 15, 22)", "Three labs, no SwiftUI", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Section 14: runUseCaseLab()", ["Payment: B54D1D0A-6633-4F8C-8628-54153C2E2188", "Balance: 2349950&ensp;&ensp;(₹25,000.00 &minus; ₹1,500.50)"], 11.5)}
        <div class="step">{console("Section 15: ₹1,50,000 from ₹2,00,000", ["Payment limit enforced"], 12.5)}</div>
        <div class="step">{console("Section 22: PaymentPolicy alone", ["Limit correctly enforced"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("What each tests", ul("The operation end to end, in memory", "An application policy", "The policy alone: no repository at all"))}</div>
        <div class="rule step" data-label="Benefit">{ul("No simulator, form or navigation stack", "Lesson 4.9: a real test suite")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 14 runs the use case against an in-memory repository: ravi@npay, ₹1,500.50, and the balance comes back 2,349,950 paise, ₹23,499.50, as expected. Click: Section 15 tests the illustrative limit: ₹2,00,000 in the account, ₹1,50,000 requested: "Payment limit enforced". Click: Section 22 tests PaymentPolicy, which arrives in Part 6, on its own: a valid amount passes, an excessive one throws limitExceeded.'),
                  ('SAY', 'Click: the first exercises the whole operation in memory; the second an application policy; the third the policy without even a repository. Click: we needed no simulator, payment form or navigation stack. That separation is the benefit; Lesson 4.9 builds the real test suite. The text&rsquo;s seven-stage execution stepper was shared only at stage one, so the deck shows these runs instead.'),
                  ('CONNECT', 'Which way do the dependencies point?'))))

# ================================================================== Part 5 (10, 11)
divider(5, "The dependency rule", "Source code points toward policy", 'Clean Architecture in NPay.', 'The layers.')
P = []
LY = [("phone", "Presentation", "SwiftUI + PaymentViewModel"), ("gear", "Application", "SendPaymentUseCase"), ("key", "Domain", "PaymentAmount, PaymentRecipient, repository contract"), ("db", "Infrastructure", "InMemoryAccountRepository")]
for i, (ic, t, sub) in enumerate(LY):
    y = i * 72
    P.append(box(0, y, 600, 58, t, sub, '1+' if i == 2 else None, '', ic))
for y in (59, 131):
    P.append(wire(f'M300 {y}V{y + 11}' + head(300, y + 11, 'd')))
P.append(wire('M300 274V218' + head(300, 218, 'u'), '2+'))
S.append(slide("Part 5 &middot; What is the Dependency Rule? (sections 10&ndash;11)", "Infrastructure depends on the domain, not the reverse", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      <div>{cues(2)}{svg('0 0 600 274', 'Presentation, application, domain, infrastructure; infrastructure points up to the domain', 'rule', P, 'max-height:290px')}
        <p class="small muted" style="margin:6px 0 0">Arrows: source-code dependencies. Calls still flow out to infrastructure, through domain-owned abstractions.</p></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Dependency inversion, in practice", ul("The use case depends on the protocol", "The actor implements it"))}</div>
        <div class="step">{card("A protocol for the use case?", ul("Not now: a struct is fine", "Add one for ViewModel tests if needed"))}</div>
        <div class="rule step" data-label="NPay rule">{ul("Abstractions where they earn it", "Not layers to imitate a diagram")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Clean Architecture says source-code dependencies should point toward the application&rsquo;s core policies. Presentation, SwiftUI and the ViewModel, depends on the application layer, SendPaymentUseCase, which depends on the domain: click: the value objects and the repository contract. The domain does not depend on SwiftUI, URLSession or a database framework.'),
                  ('SAY', 'Click: and infrastructure, InMemoryAccountRepository, points up: it implements the domain&rsquo;s protocol. At runtime the use case still calls outward into the actor, but through an abstraction the domain owns. Click: that is dependency inversion in practice, Lesson 4.4&rsquo;s principle.'),
                  ('SAY', 'Click: do we need a protocol for the use case too? Not yet: a concrete struct is fine; if ViewModel tests need to mock it, introduce one then. Click: use abstractions where they give meaningful testability or replaceability, not to imitate a diagram.'),
                  ('CONNECT', 'Now the hard part: concurrency.'))))

# ================================================================== Part 6 (16, 17, 18)
divider(6, "Rules under concurrency", "Check early; enforce at the mutation", 'Two payments, a daily limit, a better use case.', 'Overlapping checks.')
OVL = ["early checks don&rsquo;t overlap (as run):", "&ensp;A recorded; B &ldquo;Insufficient balance&rdquo; (early check)", "",
       "20 ms latency in fetchSnapshot (ours):", "&ensp;both early checks see ₹2,000", "&ensp;A &ldquo;Unable to complete payment&rdquo;; B recorded", "&ensp;balance ₹500: the repository caught it"]
S.append(slide("Part 6 &middot; Payment limits and concurrency (section 16)", "Two ₹1,500 payments at once from ₹2,000", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console(MAC + ": version 1 + section 12&rsquo;s ViewModel", OVL, 11.5)}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Learned", ul("The early check is useful, not final", "The atomic repository check is final"))}</div>
        <div class="step">{card("Noticed", ul("The repository&rsquo;s own error isn&rsquo;t mapped", "So the user saw the generic message"))}</div>
        <div class="rule step" data-label="Principle">{ul("Final check and mutation together, at the authoritative boundary")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s simulator, run for real: ₹2,000, two ₹1,500 payments started together through version one and Section 12&rsquo;s ViewModel. In our first run the two early checks did not overlap: A was recorded, and B&rsquo;s snapshot already showed ₹500, so the early check said "Insufficient balance".'),
                  ('SAY', 'Then we gave fetchSnapshot twenty milliseconds of latency, as a network read would have: both early checks saw ₹2,000 and passed. The repository&rsquo;s atomic check stopped the second payment, balance ₹500, no overdraft. Click: so the early check is useful for fast feedback; the final check and mutation must be atomic at the authoritative boundary.'),
                  ('SAY', 'Click: and something the run surfaced: the repository threw its own AccountRepositoryError.insufficientBalance, which the use case does not translate, so that user saw "Unable to complete payment" instead of "Insufficient balance". Error mapping across layers is Lesson 4.5&rsquo;s point again, and Lesson 4.7&rsquo;s job. Click: the principle.'),
                  ('CONNECT', 'A rule that depends on history: a daily limit.'))))

DL = [("First", "₹20,000", "₹20,000"), ("Second", "₹15,000", "₹35,000"), ("Third", "₹20,000", "₹55,000: rejected")]
S.append(slide("Part 7 &middot; A daily limit (section 17)".replace("Part 7", "Part 6"), "Cumulative rules need the authoritative state", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Payment", "Amount", "Daily total (limit ₹50,000)"], DL)}
        <p class="small muted" style="margin:0">A hypothetical limit, for teaching.</p>
        <div class="step">{console("Ours, Mac: three ₹20,000 payments at once, limit ₹50,000", ["checked from a snapshot, then recorded: <b>3 accepted</b>, ₹60,000", "rule inside one actor call:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;2 accepted, ₹40,000"], 11)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Where it lives", ul("Defined: domain / application", "Enforced: where today&rsquo;s total is checked and updated together"))}</div>
        <div class="rule step" data-label="Principle">{ul("Express rules in the domain", "Enforce concurrency-sensitive invariants at the mutation", "Production: the trusted backend")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A hypothetical daily outgoing limit of ₹50,000. A single-payment limit is not enough: ₹20,000, then ₹15,000 makes ₹35,000, and a third ₹20,000 would make ₹55,000: rejected.'),
                  ('SAY', 'Click: we tested both placements on the Mac, ours. Three ₹20,000 payments at once. Checking today&rsquo;s total from a snapshot and then recording: all three accepted, ₹60,000, over the limit. Passing the rule into one actor call that sums and records with no suspension: two accepted, ₹40,000.'),
                  ('SAY', 'Click: so the policy is defined in the domain or application layer, but enforced where the authoritative transaction state is checked and updated consistently: for our simulation, a repository operation that takes the policy; in production, the trusted backend. Click: business rules expressed in the domain; concurrency-sensitive invariants enforced at the authoritative mutation boundary.'),
                  ('CONNECT', 'Improve the use case accordingly.'))))

UC2 = """struct PaymentPolicy: Sendable {
    let maximumPerPaymentPaise: Int

    func validate(_ amount: PaymentAmount) throws {
        guard amount.paise <= maximumPerPaymentPaise else {
            throw PaymentDomainError.limitExceeded
        }
    }
}

struct SendPaymentUseCase {
    let repository: any AccountRepository
    let policy: PaymentPolicy

    func execute(_ command: SendPaymentCommand)
        async throws -> PaymentRecord {
        try policy.validate(command.amount)

        return try await repository.recordPayment(
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise)
    }
}"""
S.append(slide("Part 6 &middot; Improve our use-case design (section 18)", "Static policy here; the balance at the repository", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("PaymentPolicy and SendPaymentUseCase (replaces version 1)", UC2, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What changed", ul("No snapshot, no early balance check", "Policy first, then the atomic mutation"))}
        <div class="step">{card("Why better", ul("No stale-balance decision", "The policy is testable alone (section 22)"))}</div>
        <div class="step">{code("Demo configuration", "PaymentPolicy(maximumPerPaymentPaise: 10_000_000)\n// ₹1,00,000, illustrative", "font-size:11.5px")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Version one did an early balance check from a snapshot and then recorded, duplicating validation and assuming fresh data. Version two separates static policy from the authoritative balance check. PaymentPolicy holds a maximum per payment and validates an amount against it. SendPaymentUseCase now takes the repository and a policy: it validates the policy, then delegates the atomic account mutation.'),
                  ('SAY', 'Click: why better: the use case no longer makes a balance decision from a possibly stale snapshot, and the policy can be tested independently, as Section 22 did. Click: the demo policy is 10,000,000 paise, ₹1,00,000, purely illustrative. This replaces version one under the same name.'),
                  ('CONNECT', 'Plug it into NPay.'))))

# ================================================================== Part 7 (12, 13, 19, 20, 21)
divider(7, "Into NPay", "Use case, factory, reviewed command", 'The review flow, preserved.', 'The ViewModel.')
VMC = """private let sendPayment: SendPaymentUseCase

init(sendPayment: SendPaymentUseCase) {
    self.sendPayment = sendPayment
}

func submit(_ command: SendPaymentCommand) async -> PaymentRecord? {
    guard !isSubmitting else { return nil }
    isSubmitting = true
    defer { isSubmitting = false }
    do {
        let result = try await sendPayment.execute(command)
        recipient = ""; amountText = ""; errorMessage = nil
        return result
    } catch {
        errorMessage = "Unable to complete demo payment"
        return nil
    }
}"""
FACT = """@MainActor
enum NPayFactory {
    static func makePaymentViewModel(
        repository: any AccountRepository
    ) -> PaymentViewModel {
        let policy = PaymentPolicy(
            maximumPerPaymentPaise: 10_000_000)
        let useCase = SendPaymentUseCase(
            repository: repository, policy: policy)
        return PaymentViewModel(sendPayment: useCase)
    }
}"""
S.append(slide("Part 7 &middot; ViewModel and composition root (sections 12&ndash;13, 19&ndash;20)", "The ViewModel delegates the operation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      {code("PaymentViewModel (section 20&rsquo;s submission)", VMC, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("NPayFactory (section 19)", FACT, "font-size:10.5px")}</div>
        <div class="step">{card("Section 12&rsquo;s version", ul("Parsed the fields itself; specific messages", "Section 20&rsquo;s: one generic message"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 12 replaces the PaymentService dependency with the use case: the ViewModel no longer calls the repository, it delegates the operation. Its first submit parsed the form fields into a command itself and mapped insufficientBalance and limitExceeded to specific messages. Section 20 replaces that with submit taking a command, on the slide: guard against a double submit, execute the use case, clear the form, or set "Unable to complete demo payment".'),
                  ('SAY', 'Click: the composition root, Section 19: the factory creates the policy and the use case from a repository and hands the use case to the ViewModel, which constructs neither.'),
                  ('SAY', 'Click: one trade-off to notice: Section 12 gave specific messages; Section 20&rsquo;s version shows one message for every failure: we measured insufficient balance and over-limit both giving "Unable to complete demo payment". Lesson 4.7 models those states properly.'),
                  ('CONNECT', 'Why submit a command at all?'))))

REV = ["the user reviews ₹1,500.50, then the form changes to 2000:", "&ensp;submit() reading the fields (section 12):&ensp;paid <b>200000</b>", "&ensp;submit(reviewedCommand) (section 20):&ensp;&ensp;paid 150050"]
S.append(slide("Part 7 &middot; Submit exactly what was reviewed (section 20)", "The command is the contract with the user", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("The flow, preserved (3.4)", ul("Form &rarr; review sheet &rarr; Confirm &rarr; success", "Opening review never pays; only Confirm does"))}
        <div class="step">{console(MAC, REV, 11.5)}</div>
        <div class="step">{card("In NPay (ours)", ul("Review: <code>prepareCommand()</code> builds the command", "The sheet shows it; Confirm submits that same value"))}</div>
      </div>
      <div class="step">{PHONE("img/review.png", "The sheet shows the command", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'Lesson 3.4&rsquo;s flow must survive: form, review sheet, Confirm, success. Opening the review never executes a payment; only confirmation does. The integration correction: the earlier submit read the mutable form fields; in a review flow we should submit the exact immutable request the user reviewed.'),
                  ('SAY', 'Click: we showed the difference on the Mac: the user reviews ₹1,500.50, then the form text changes to 2000 before Confirm. Section 12&rsquo;s submit, reading the fields, paid 200,000 paise: not what was reviewed. Section 20&rsquo;s submit with the reviewed command paid 150,050.'),
                  ('SAY', 'Click: in NPay, flagged as ours: Review Payment calls prepareCommand, which parses the form into a SendPaymentCommand; click: the sheet shows that command, and Confirm submits the very same value. The repository still revalidates its authoritative state.'),
                  ('CONNECT', 'And after Confirm?'))))

P = []
NF = [("tap", "Confirm", "the reviewed command"), ("gear", "await execute(command)", "policy, then repository"), ("check", "Success", "pendingSuccessID = record.id"),
      ("layers", "Sheet dismissed", "review = nil"), ("decision", "onDismiss", "router.showPaymentSuccess(id)")]
for i, (ic, t, sub) in enumerate(NF):
    x = i * 228
    P.append(tall(x, 0, 208, 110, ic, t, sub, f'{i + 1}' if i < 4 else '5+', ''))
    if i < 4:
        P.append(wire(f'M{x + 209} 55H{x + 226}' + head(x + 226, 55, 'r')))
RUN = [("₹1,500.50", "Payment Recorded; ₹23,499.50; History top &ldquo;Sent to ravi@npay&rdquo;; form cleared"),
       ("₹20,000, ₹10,000 left during review", "&ldquo;Unable to complete demo payment&rdquo;; no navigation; balance unchanged; draft kept")]
S.append(slide("Part 7 &middot; Navigation after asynchronous submission (section 21)", "Success navigates; failure never does", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 110', 'Confirm, execute, success, dismiss, navigate', 'nav', P, 'max-height:118px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) 150px;gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["NPay, simulator", "Result"], RUN, 'tbl compact')}</div>
        <div class="warn step" data-label="Lifetime">{ul("A task can finish after the user has left: Lesson 4.7")}</div>
      </div>
      <div class="step">{PHONE("img/stale.png", "Failure: no success", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'Lesson 3.4&rsquo;s coordination of dismissal and navigation, with an asynchronous step. Click through: the user confirms the reviewed command; the ViewModel awaits the use case; on success the record&rsquo;s ID is stored as the pending navigation result; the sheet is dismissed; its onDismiss asks the router to show payment success.'),
                  ('SAY', 'Click: run in NPay through our adapter repository over NPayStore, so Home and History keep one source of truth. ₹1,500.50: Payment Recorded, ₹23,499.50, "Sent to ravi@npay" at the top of History, the form cleared. A stale review, ₹20,000 with ₹10,000 removed during review: the store refused, the ViewModel showed "Unable to complete demo payment", there was no navigation, the balance was unchanged and the draft was kept. Click: the screenshot. On failure the text allows keeping the sheet open or showing an error; ours closes it and shows the error inline.'),
                  ('SAY', 'Click: the senior insight: an asynchronous operation can complete after the user has navigated away; cancellation, task lifetime and presentation state must be managed deliberately. Lesson 4.7 models those states.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.6', (), [("check", "Values that can&rsquo;t be invalid", "PaymentAmount &gt; 0; PaymentRecipient non-blank"),
                     ("gear", "A use case is the operation", "policy first; the repository mutates atomically"),
                     ("key", "Submit what was reviewed", "the command, not the fields: 150050, not 200000")],
          'Three things to remember. Domain value objects hold business values with invariants: a PaymentAmount is positive, a PaymentRecipient is not blank, and a SendPaymentCommand carries both with no UI types. SendPaymentUseCase is the operation itself: it applies the policy, then lets the repository check the balance and record atomically, because early checks and snapshot-based limits failed under concurrency in our runs. And in NPay the review sheet shows a command and Confirm submits that same command, so the user pays exactly what they reviewed.')

review_divider(11)
review([("check", "Choose one", "What is a domain value object?",
         "What is a domain value object?<br>A. A SwiftUI screen<br>B. A type representing a domain concept and its invariants<br>C. A database connection", "B",
         "PaymentAmount can&rsquo;t be zero or negative.",
         "Treating every struct as a value object.", "Most pick B.", None),
        ("phone", "Question", "Should SendPaymentUseCase import SwiftUI?",
         "Should SendPaymentUseCase import SwiftUI?", "No",
         "Foundation only: it ran on the Mac with no UI.",
         "Letting the operation depend on presentation.", "Most say no.", None),
        ("clock", "Choose one", "Why is an early balance check insufficient for final authorization?",
         "Why is an early balance check insufficient for final payment authorization?<br>A. SwiftUI doesn&rsquo;t support integers<br>B. The balance may change before mutation<br>C. Repositories can&rsquo;t throw", "B",
         "With latency both early checks saw ₹2,000.",
         "Trusting a snapshot.", "Most pick B.", None),
        ("shield", "Choose one", "Where should the authoritative balance check occur?",
         "Where should the authoritative balance check occur?<br>A. Inside BalanceCard<br>B. Only in TextField validation<br>C. At the atomic mutation boundary", "C",
         "The repository caught the overdraft.",
         "Checking far from the write.", "Most pick C.", None),
        ("file", "Choose one", "Why submit the immutable reviewed command?",
         "Why submit the immutable reviewed command?<br>A. To ensure submitted data matches what was reviewed<br>B. To improve animation speed<br>C. To eliminate all concurrency issues", "A",
         "Fields changed to 2000; the command still paid 150050.",
         "Re-reading mutable fields on Confirm.", "Most pick A.", None),
        ("link", "Question", "Does actor isolation automatically enforce payment idempotency?",
         "Does actor isolation automatically enforce payment idempotency?", "No",
         "The same request twice was recorded twice (4.5).",
         "Confusing safety with idempotency.", "Some say yes.", None),
        ("decision", "Choose one", "What should happen if payment submission fails?",
         "What should happen if payment submission fails?<br>A. Clear the account balance<br>B. Navigate to success anyway<br>C. Show an error and avoid success navigation", "C",
         "Stale review: error shown, paymentsPath empty.",
         "Navigating before the result.", "Most pick C.", None),
        ("gear", "Question", "Can PaymentPolicy be tested without launching SwiftUI?",
         "Can PaymentPolicy be tested without launching SwiftUI?", "Yes",
         "&ldquo;Limit correctly enforced&rdquo;, on the Mac.",
         "Assuming rules need the app to test.", "Most say yes.", None),
        ("diff", "Predict the result", "Daily limit ₹50,000 checked from a snapshot; three ₹20,000 at once?",
         "A daily limit of ₹50,000 is checked in the use case from a snapshot, then the payment is recorded. Three ₹20,000 payments start at once. How many are accepted?<br>A. 2<br>B. 3<br>C. 0", "B",
         "All saw ₹0 spent today; inside the actor call: 2.",
         "Assuming a check before an await still holds.", "Many pick A.", None),
        ("key", "Predict the result", "Reviewed ₹1,500.50; fields then changed to 2000; section 12's submit() pays?",
         "The user reviews ₹1,500.50; before Confirm the amount field changes to 2000. Section 12&rsquo;s parameterless <code>submit()</code> pays&hellip;<br>A. ₹1,500.50<br>B. ₹2,000<br>C. Nothing", "B",
         "It reads the fields: 200000 paise.",
         "Assuming the sheet&rsquo;s values are submitted.", "Some pick A.", None),
        ("db", "Question", "From 4.5: does a dashboard snapshot update itself after a payment?",
         "From Lesson 4.5: after a payment, does a DashboardViewModel snapshot update itself?", "No",
         "It showed ₹25,000.00 until refresh().",
         "Expecting snapshots to observe the repository.", "Most say no.", "Spaced review from Lesson 4.5.")])

S.append(next_slide('4.6', [("4.7", "UI state modeling", "idle, submitting, success, failure; specific error messages"),
                            ("4.9", "Architecture testing", "the policy and use-case labs as a test suite"),
                            ("Unit 5", "Networking", "a remote repository behind the same use case"),
                            ("Unit 8", "Concurrency", "task lifetime and cancellation after navigation")],
                    'Lesson 4.7 models the payment lifecycle as explicit UI states, and finally maps each domain error to its own message. 4.9 turns today&rsquo;s labs into tests, Unit 5 puts a remote repository behind the same use case, and Unit 8 deals with tasks that outlive the screen.'))

S.append(lab_slide('4.6', "SendPaymentUseCase", "Values, command, policy, use case.",
                   ["Add PaymentAmount and PaymentRecipient.",
                    "Add SendPaymentCommand.",
                    "Write PaymentPolicy and SendPaymentUseCase.",
                    "Run sections 14, 15 and 22&rsquo;s labs.",
                    "Inject the use case through NPayFactory.",
                    "Review a command; Confirm submits it."],
                   "", 'Expected, as in our run: 2349950, "Payment limit enforced", "Limit correctly enforced"; in the app ₹23,499.50 after a payment, and an error with no navigation when the balance falls during review.',
                   side=f'<div>{card("You hand in", ul("Your domain and use-case files", "Lab output", "The review flow submitting the command"))}</div>'))

end_slide('4.6', 'Domain Models, Use Cases<br>&amp; Clean Architecture', 'Lesson 4.7 &mdash; UI State Modeling',
          'You can now model domain values with invariants, build an immutable command, write a use case for a business operation, apply the dependency rule, enforce concurrency-sensitive rules at the mutation, and submit exactly what the user reviewed.',
          'Next, Lesson 4.7: UI state modeling for NPay&rsquo;s payment lifecycle.')

write_deck(OUT46, '4.6', 'Domain Models, Use Cases &amp; Clean Architecture', 'Domain Models, Use Cases &amp; Clean Architecture')
