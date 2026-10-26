"""Generates decks/unit-4/lesson-4.5/index.html from the Lesson 4.5 text (Repository Pattern & Data Access Architecture;
Part 1 Sections 1-8, Part 2 Sections 9-21, Section 13 split across a continuation). Evidence: the text's code on the Mac
(section 8 lab, section 19 tests, concurrent payments on the actor, section 14's split workflow overdrawing, error mapping,
one repository with two ViewModels, duplicate requests) and tools/sim4_5 (a dashboard snapshot before and after the explicit
refresh). NPay's own code is unchanged in this lesson."""
import html, os, re, sys
OUT45 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

MAC = 'Mac run, the text&rsquo;s code'
title_slide('4.5', 'Repository Pattern &amp;<br>Data Access',
            'In memory today, a database and an API tomorrow: <b>one contract</b> for NPay&rsquo;s account data.',
            'Lesson 4.4 put PaymentService between the ViewModel and the store. Today we separate data access itself: how can NPay switch between in-memory data, local storage and a backend API without rewriting business logic or screens? We define an account repository, implement it as a Swift actor, connect it to a payment service and a dashboard, and then test the claims: concurrent payments, a non-atomic workflow, stale snapshots, duplicate requests.')
outcomes_slide('4.5', [("db", "Explain what a repository abstracts, and what it doesn&rsquo;t"),
                       ("file", "Design an atomic repository operation"),
                       ("shield", "Use an actor to protect in-memory account state"),
                       ("diff", "Map storage errors to payment errors"),
                       ("layers", "Share one repository across ViewModels and refresh deliberately"),
                       ("clock", "Tell concurrency safety from atomicity and idempotency")])
where_slide('4.5', 'Today: a boundary for data access', (),
            '4.4: PaymentService, injected; a mock behind the same screen.',
            'Repositories: contract, actor, caching, consistency.',
            'Last time the ViewModel stopped knowing how payments happen. Today the payment service stops knowing where account data lives. The text came as Part 1 and Part 2; Section 13 continues across the break.',
            'The problem.')

# ================================================================== Part 1 (1, 2)
divider(1, "The problem", "Who should know where data lives?", 'Not the ViewModel, not the payment workflow.', 'Today&rsquo;s chain.')
P = []
CH = [("phone", "PaymentsScreen", "displays payment UI"), ("layers", "PaymentViewModel", "coordinates submission"), ("check", "DemoPaymentService", "simulated payment"), ("db", "NPayStore", "balance and transactions")]
for i, (ic, t, sub) in enumerate(CH):
    y = i * 66
    P.append(box(0, y, 520, 54, t, sub, None, '', ic))
    if i < 3:
        P.append(wire(f'M260 {y + 55}V{y + 64}' + head(260, y + 64, 'd')))
S.append(slide("Part 1 &middot; The problem with our current design (section 1)", "Data access has no boundary of its own", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:22px;align-items:start">
      {svg('0 0 520 252', 'PaymentsScreen, PaymentViewModel, DemoPaymentService, NPayStore', 'chain', P, 'max-height:270px')}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Coming", ul("A REST API for transactions", "A SwiftData cache", "Cached records when offline"))}
        <div class="step">{card("Should the ViewModel know SwiftData vs server?", ul("No"))}</div>
        <div class="step">{card("Should the payment service build SQL or URLSession requests?", ul("Ideally, no"))}</div>
        <div class="rule step" data-label="Need">{ul("A boundary that abstracts data access")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPay today: the screen displays the UI, the ViewModel coordinates submission, DemoPaymentService handles the simulated payment, and NPayStore holds the balance and transactions. For a local simulation that works. Now imagine NPay must fetch transactions from a REST API, cache recent ones in SwiftData, and show cached records when offline.'),
                  ('SAY', 'Click: should PaymentViewModel know whether data came from SwiftData or a server? No. Click: should PaymentService contain SQL queries or URLSession request-building code? Ideally, no. Click: we need a boundary that abstracts data access: a repository.'),
                  ('CONNECT', 'What exactly is one?'))))

RV = [("Retrieves and stores domain data", "Coordinates application behaviour"), ("Abstracts data sources", "Enforces business workflows"),
      ("<code>fetchBalance()</code>", "<code>sendPayment()</code>"), ("<code>fetchTransactions()</code>", "Validate and execute a transfer"),
      ("<code>saveTransaction()</code>", "Decide when to save, what to return")]
S.append(slide("Part 1 &middot; What exactly is a repository? (section 2)", "An application-facing interface to domain data", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("The caller&rsquo;s view", "let balance = try await\n    repository.fetchBalance()", "font-size:14px")}
        {card("Hidden from the caller", ul("A dictionary in memory", "A local database", "A remote API"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Repository", "Service / use case"], RV, 'tbl compact')}</div>
        <div class="rule step" data-label="Convention">{ul("Architectural, not enforced by Swift", "Some repository calls are atomic domain operations")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A repository provides an application-facing interface for accessing and modifying domain data, and hides how the data is stored or retrieved. The caller writes try await repository.fetchBalance() and does not know whether that is an in-memory dictionary, a local database or a remote API.'),
                  ('SAY', 'Click: repository versus service. The repository retrieves and stores domain data and abstracts data sources: fetchBalance, fetchTransactions, saveTransaction. A service or use case coordinates behaviour and enforces workflows: sendPayment, validate and execute a transfer, decide when to save and what to return.'),
                  ('SAY', 'Click: the distinction is architectural, not enforced by Swift, and in some apps a repository operation is itself a meaningful atomic domain operation, as ours will be.'),
                  ('CONNECT', 'Where it fits in NPay.'))))

# ================================================================== Part 2 (3, 4, 5)
divider(2, "The contract", "Models and one atomic operation", 'AccountRepository.', 'The target.')
P = []
TG = [("phone", "PaymentsScreen", "interaction, presentation"), ("layers", "PaymentViewModel", "screen state, actions"), ("check", "PaymentService", "payment workflow"),
      ("key", "AccountRepository", "account data contract"), ("db", "Repository implementation", "in memory today; persistent or remote later")]
for i, (ic, t, sub) in enumerate(TG):
    y = i * 62
    P.append(box(0, y, 560, 52, t, sub, '1+' if i == 3 else None, '', ic))
    if i < 4:
        P.append(wire(f'M280 {y + 53}V{y + 60}' + head(280, y + 60, 'd')))
MODELS = """struct PaymentRecord: Identifiable, Sendable {
    let id: UUID
    let recipient: String
    let amountPaise: Int
    let createdAt: Date
}

struct AccountSnapshot: Sendable {
    let balancePaise: Int
    let transactions: [PaymentRecord]
}"""
S.append(slide("Part 2 &middot; Target architecture and domain models (sections 3&ndash;4)", "One repository owns the demo account", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 560 300', 'PaymentsScreen, PaymentViewModel, PaymentService, AccountRepository, implementation', 'tgt', P, 'max-height:300px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("PaymentRecord.swift", MODELS, "font-size:12px")}</div>
        <div class="step">{card("Why these", ul("<code>PaymentRecord</code>: avoids Unit 3&rsquo;s <code>Transaction</code>", "<code>Sendable</code>: safe across isolation (Unit 8)"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The target: the screen, the ViewModel, the PaymentService workflow, then, click, the AccountRepository contract, and an implementation that is in memory today and persistent or remote later. One repository will own the demo balance and history, taking over NPayStore&rsquo;s storage job incrementally; we do not delete the existing app code today.'),
                  ('SAY', 'Click: two domain models. PaymentRecord: an ID, recipient, amount in paise and a creation date; named so it does not clash with Unit 3&rsquo;s Transaction. AccountSnapshot: the balance and the transactions at one moment.'),
                  ('SAY', 'Click: both are Sendable: their value-type properties can safely cross concurrency isolation boundaries, which matters because the repository will be an actor. Unit 8 goes deeper.'),
                  ('CONNECT', 'The contract.'))))

CON = """enum AccountRepositoryError: Error {
    case invalidRecipient
    case invalidAmount
    case insufficientBalance
}

protocol AccountRepository: Sendable {
    func fetchSnapshot() async throws -> AccountSnapshot

    func recordPayment(
        recipient: String,
        amountPaise: Int
    ) async throws -> PaymentRecord
}"""
S.append(slide("Part 2 &middot; The repository contract (section 5)", "Two methods; the payment is one call", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("AccountRepository.swift", CON, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("fetchSnapshot()", ul("The current account state"))}
        <div class="step">{card("recordPayment(recipient:amountPaise:)", ul("Records the payment <i>and</i> updates the balance"))}</div>
        <div class="rule step" data-label="Intentional">{ul("No separate saveTransaction() and updateBalance()", "Payment and balance stay consistent")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The contract: an error enum with three cases, invalid recipient, invalid amount, insufficient balance; and AccountRepository, a Sendable protocol with two async throwing methods.'),
                  ('SAY', 'fetchSnapshot returns the current account state. Click: recordPayment records a local demo transaction and updates the balance in the same call.'),
                  ('SAY', 'Click: notice what is missing: no separate saveTransaction and updateBalance. That is intentional: a payment and its balance update must stay consistent, so the repository offers one atomic operation over its in-memory state. Part 6 shows what goes wrong otherwise.'),
                  ('CONNECT', 'Implement it.'))))

# ================================================================== Part 3 (6, 7, 8, 19)
divider(3, "An actor-backed repository", "In memory, isolated, testable", 'InMemoryAccountRepository.', 'The actor.')
ACT = """actor InMemoryAccountRepository: AccountRepository {
    private var balancePaise: Int
    private var transactions: [PaymentRecord] = []

    init(initialBalancePaise: Int = 2_500_000) {
        self.balancePaise = initialBalancePaise
    }

    func fetchSnapshot() async throws -> AccountSnapshot {
        AccountSnapshot(balancePaise: balancePaise, transactions: transactions)
    }

    func recordPayment(recipient: String, amountPaise: Int)
        async throws -> PaymentRecord {
        let trimmed = recipient.trimmingCharacters(
            in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw AccountRepositoryError.invalidRecipient }
        guard amountPaise > 0 else { throw AccountRepositoryError.invalidAmount }
        guard amountPaise <= balancePaise else {
            throw AccountRepositoryError.insufficientBalance }

        let payment = PaymentRecord(id: UUID(), recipient: trimmed,
            amountPaise: amountPaise, createdAt: .now)
        balancePaise -= amountPaise
        transactions.insert(payment, at: 0)
        return payment
    }
}"""
S.append(slide("Part 3 &middot; An in-memory repository (section 6)", "An actor: one operation at a time on its state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:22px;align-items:start">
      {code("InMemoryAccountRepository.swift (condensed)", ACT, "font-size:10px;line-height:1.4")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("recordPayment", ul("Check recipient, amount, balance", "Create the record", "Deduct, insert, return"))}
        <div class="step">{card("Why an actor?", ul("Protects mutable state from unsynchronized access", "Called with await from outside"))}</div>
        <div class="rule step" data-label="Key detail">{ul("No await inside check-and-update")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Our first repository is a Swift actor. It holds the balance, default ₹25,000, and the transactions, both private. fetchSnapshot returns them together. recordPayment trims the recipient and throws invalidRecipient if it is empty, invalidAmount if the amount is not positive, insufficientBalance if it exceeds the balance; otherwise it creates the record, deducts, inserts it first, and returns it.'),
                  ('SAY', 'Click: why an actor? It protects its mutable state from unsynchronized concurrent access; outside callers reach its methods asynchronously, with await.'),
                  ('SAY', 'Click: the detail that makes it work: there is no await inside the check-and-update sequence. Actor isolation then lets that sequence run without another actor-isolated operation interleaving. Imagine two payments arriving almost together: let&rsquo;s test that.'),
                  ('CONNECT', 'Two payments at once.'))))

CONC = ["two ₹1,500 payments at once, ₹2,000 balance:", "&ensp;a@npay: recorded", "&ensp;rejected: insufficientBalance", "&ensp;balance 50000, transactions 1", "",
        "1,000 concurrent ₹1 payments, ₹500 balance (ours):", "&ensp;recorded 500, rejected 500; balance 0"]
S.append(slide("Part 3 &middot; Actor isolation, measured (section 7)", "Concurrent payments can&rsquo;t overdraw", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console(MAC + " (Swift 6)", CONC, 12)}
        <p class="small muted" style="margin:0">Which request wins isn&rsquo;t guaranteed; that one wins is.</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why", ul("Each recordPayment runs to completion", "The second sees ₹500, and is rejected"))}</div>
        <div class="warn step" data-label="Limit">{ul("Data-race safety, not workflow atomicity", "An await between read and write breaks it (Part 6)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s scenario: ₹2,000, two ₹1,500 payments at the same moment. We ran it: one recorded, the other rejected with insufficientBalance; balance ₹500, one transaction. Which request wins depends on scheduling, as the text notes; that exactly one wins does not.'),
                  ('SAY', 'Then a heavier version of ours: a thousand concurrent ₹1 payments against ₹500. Exactly five hundred recorded, five hundred rejected, balance zero. No lost updates.'),
                  ('SAY', 'Click: why: each recordPayment runs its non-suspending check-and-update to completion before the next one touches the balance. Click: but the text&rsquo;s insight: actors prevent data races on isolated state; they do not make a multi-step workflow atomic if it suspends between reading and writing. Part 6 measures that, and Unit 8 studies reentrancy.'),
                  ('CONNECT', 'Test it without SwiftUI.'))))

S.append(slide("Part 3 &middot; Test the repository without SwiftUI (sections 8, 19)", "Deterministic, no app", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Section 8: runRepositoryLab()", ["Before: 2500000", "Payment ID: 870B57C9-0ECC-4DE2-95EF-964FFA8A7050", "After: 2349950", "Transactions: 1"], 12)}
        <div class="step">{console("Section 19 (Debug: asserts active)", ["Repository test passed", "Correctly rejected"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("testRepositoryPayment", ul("₹2,000 &minus; ₹500 = ₹1,500", "One transaction"))}</div>
        <div class="step">{card("testInsufficientBalance", ul("₹500 from ₹100: rejected", "Balance still ₹100; no transactions"))}</div>
        <div class="rule step" data-label="Lesson 4.9">{ul("These become a real test suite")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 8&rsquo;s experiment, run: before 2,500,000 paise; a generated payment ID; after 2,349,950; one transaction. Exactly the text&rsquo;s expected output. A working domain-data repository, independent of SwiftUI.'),
                  ('SAY', 'Click: Section 19&rsquo;s two tests, in a Debug build where assert is active: "Repository test passed" and "Correctly rejected". Click: the first starts at ₹2,000, pays ₹500 and checks ₹1,500 and one transaction. Click: the second starts at ₹100, tries ₹500, expects insufficientBalance, and confirms nothing changed: a rejected payment must not modify account state.'),
                  ('SAY', 'Click: Lesson 4.9 turns these into proper automated tests.'),
                  ('CONNECT', 'Connect it to the payment service.'))))

# ================================================================== Part 4 (9, 10, 15, 16)
divider(4, "Service on a repository", "RepositoryPaymentService and typed errors", 'Errors gain meaning on the way up.', 'The service.')
SVC = """@MainActor
final class RepositoryPaymentService: PaymentService {
    private let repository: any AccountRepository

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func send(_ request: PaymentRequest) async throws
        -> PaymentReceipt {
        do {
            let payment = try await repository.recordPayment(
                recipient: request.recipient,
                amountPaise: request.amountPaise)
            return PaymentReceipt(transactionID: payment.id,
                recipient: payment.recipient,
                amountPaise: payment.amountPaise)
        } catch AccountRepositoryError.invalidRecipient {
            throw PaymentError.invalidRecipient
        } catch AccountRepositoryError.invalidAmount {
            throw PaymentError.invalidAmount
        } catch AccountRepositoryError.insufficientBalance {
            throw PaymentError.insufficientBalance
        } catch {
            throw PaymentError.unknown
        }
    }
}"""
S.append(slide("Part 4 &middot; Connect the repository to a payment service (sections 9, 15)", "Depend on the contract; translate its errors", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:22px;align-items:start">
      {code("RepositoryPaymentService (section 15&rsquo;s version)", SVC, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What changed", ul("Before: DemoPaymentService &rarr; NPayStore", "Now: RepositoryPaymentService &rarr; AccountRepository"))}
        <div class="step">{card("Error mapping", ul("Storage errors &rarr; <code>PaymentError</code>", "Better than nil for every failure"))}</div>
        <div class="warn step" data-label="One declaration">{ul("Section 15&rsquo;s version replaces section 9&rsquo;s")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 9 adds a PaymentService implementation built on the repository: it records the payment and turns the PaymentRecord into a PaymentReceipt. Section 15 improves it, and that is the version on the slide: each AccountRepositoryError is caught and rethrown as a PaymentError, with anything else becoming unknown.'),
                  ('SAY', 'Before, DemoPaymentService depended on the concrete NPayStore; now RepositoryPaymentService depends on the AccountRepository abstraction. Click: why map errors? The payment feature should not expose internal storage or networking errors directly to the UI; the service translates repository failures into payment-domain failures. Three distinct cases are better than a nil that could mean anything.'),
                  ('SAY', 'Click: the text&rsquo;s warning: section 15&rsquo;s version replaces section 9&rsquo;s; keep only one declaration in a target, or it will not compile.'),
                  ('CONNECT', 'The whole chain, and an error travelling up it.'))))

P = []
SQ = [("phone", "PaymentsScreen", "user confirms"), ("layers", "PaymentViewModel", "service.send(request)"), ("check", "RepositoryPaymentService", "coordinates the operation"),
      ("key", "AccountRepository", "abstract contract"), ("db", "InMemoryAccountRepository", "validates, updates atomically")]
for i, (ic, t, sub) in enumerate(SQ):
    y = i * 60
    P.append(box(0, y, 500, 50, t, sub, None, '', ic))
    if i < 4:
        P.append(wire(f'M250 {y + 51}V{y + 58}' + head(250, y + 58, 'd')))
ERR = ["repository:&ensp;AccountRepositoryError.insufficientBalance", "service:&ensp;&ensp;&ensp;&ensp;PaymentError.<b>insufficientBalance</b>",
       "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;(blank recipient &rarr; PaymentError.invalidRecipient)", "ViewModel (4.4): &ldquo;Payment could not be completed.&rdquo;"]
S.append(slide("Part 4 &middot; The call chain and error propagation (sections 10, 16)", "Errors should mean more as they rise", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:22px;align-items:start">
      <div>{svg('0 0 500 290', 'Screen, ViewModel, RepositoryPaymentService, AccountRepository, InMemoryAccountRepository', 'seq', P, 'max-height:300px')}
        <p class="small muted" style="margin:6px 0 0">A receipt goes back up; the router navigates afterwards, not the repository.</p></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(MAC + ": ₹30,000 against ₹25,000", ERR, 11)}</div>
        <div class="step">{card("Noticed", ul("The ViewModel still collapses every error into one message", "Specific messages: Lesson 4.7"))}</div>
        <div class="rule step" data-label="But">{ul("Keep debugging detail: log it, don&rsquo;t show it")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The full chain for one payment: the screen&rsquo;s confirm, the ViewModel calling service.send, RepositoryPaymentService coordinating, the AccountRepository contract, and the in-memory actor that validates and updates atomically. A PaymentReceipt comes back to the ViewModel; the router navigates after a successful result, never the repository itself.'),
                  ('SAY', 'Click: an insufficient-balance error travelling up, measured: thirty thousand rupees against twenty-five. The repository threw AccountRepositoryError.insufficientBalance; the service rethrew PaymentError.insufficientBalance; a blank recipient became PaymentError.invalidRecipient. Then Lesson 4.4&rsquo;s ViewModel turned it into "Payment could not be completed."'),
                  ('SAY', 'Click: so the information reached the ViewModel and stopped there: it still collapses every failure into one message. The text says the ViewModel can convert each failure into an appropriate message; Lesson 4.7&rsquo;s UI state modelling does exactly that. Click: and do not throw away what debugging needs: log infrastructure details separately, without showing sensitive implementation details to users.'),
                  ('CONNECT', 'How does the dashboard see the new balance?'))))

# ================================================================== Part 5 (11, 17, 18)
divider(5, "One repository, two ViewModels", "Snapshots and explicit refresh", 'The dashboard reads; payments write.', 'The dashboard.')
DASH = """@MainActor
@Observable
final class DashboardViewModel {
    private let repository: any AccountRepository

    var balancePaise = 0
    var transactions: [PaymentRecord] = []

    init(repository: any AccountRepository) {
        self.repository = repository
    }

    func refresh() async throws {
        let snapshot = try await repository.fetchSnapshot()
        balancePaise = snapshot.balancePaise
        transactions = snapshot.transactions
    }
}"""
DEPS = """@MainActor
final class NPayDependencies {
    let repository: any AccountRepository
    let paymentService: any PaymentService

    init() {
        let repository = InMemoryAccountRepository()
        self.repository = repository
        self.paymentService = RepositoryPaymentService(
            repository: repository)
    }

    func makeDashboardViewModel() -> DashboardViewModel {
        DashboardViewModel(repository: repository)
    }

    func makePaymentViewModel() -> PaymentViewModel {
        PaymentViewModel(service: paymentService)
    }
}"""
S.append(slide("Part 5 &middot; Dashboard and dependencies (sections 11, 17)", "A presentation snapshot of authoritative data", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      {code("DashboardViewModel", DASH, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("NPayDependencies: one repository", DEPS, "font-size:10.5px")}</div>
        <div class="step">{console(MAC, ["a new DashboardViewModel, before refresh: <b>0</b>", "on its own InMemoryAccountRepository(): 2500000, never our payments"], 11)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The repository owns the balance; the dashboard has to display it. We must not create a second, competing balance. DashboardViewModel holds presentation state derived from repository data, balancePaise and transactions, and refresh copies them from a fresh snapshot. The repository stays authoritative.'),
                  ('SAY', 'Click: NPayDependencies, a small container, creates one repository and connects both features to it: the dashboard ViewModel reads it directly; the payment ViewModel submits through a RepositoryPaymentService on the same repository.'),
                  ('SAY', 'Click: two things we measured. A new DashboardViewModel shows zero until its first refresh: its stored default. And a dashboard given its own InMemoryAccountRepository shows ₹25,000 forever, never seeing our payments: one repository instance is the whole point.'),
                  ('CONNECT', 'But one repository doesn&rsquo;t refresh anything by itself.'))))

S.append(slide("Part 5 &middot; Refresh the dashboard (section 18)", "A snapshot doesn&rsquo;t update itself", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr) minmax(0,.9fr);gap:18px;align-items:start">
      {crop("img/norefresh.png", "Paid, no refresh", 300)}
      <div class="step">{crop("img/refresh.png", "Paid, then refresh()", 300)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Simulator lab (ours)", ["no refresh: shows ₹25,000.00, 0", "repository: 2,349,950, 1", "refresh: ₹23,499.50, 1"], 11.5)}
        <div class="step">{code("Section 18", "let receipt = await paymentViewModel.submit()\n\nif receipt != nil {\n    try? await dashboardViewModel.refresh()\n}", "font-size:10.5px")}</div>
        <div class="warn step" data-label="Separate outcomes">{ul("A failed refresh &ne; a failed payment")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A small simulator lab of ours: a dashboard snapshot and a pay button, both from one NPayDependencies. Left: we paid ₹1,500.50 without refreshing. The dashboard still says ₹25,000.00 and zero payments, while the repository holds 2,349,950 paise and one payment. Same repository, stale snapshot.'),
                  ('SAY', 'Click: with Section 18&rsquo;s explicit refresh after a successful payment: ₹23,499.50 and one payment. Click: the code: if submit returned a receipt, try await refresh. Explicit refresh demonstrates the coordination; observable streams or a shared coordinator come later.'),
                  ('SAY', 'Click: but the try? silently ignores a refresh failure. A payment can succeed while the refresh that follows fails: keep the successful payment result and handle the refresh failure separately. Never read a failed UI refresh as proof the payment failed; with networking that becomes critical.'),
                  ('CONNECT', 'Where real data will come from.'))))

# ================================================================== Part 6 (12, 13)
divider(6, "Data sources and caching", "Behind the repository", 'Local and remote; which first.', 'Data sources.')
P = []
P.append(box(130, 0, 440, 54, "AccountRepository", "application-facing contract", None, '', 'key'))
P.append(wire('M350 55V78' + head(350, 78, 'd')))
P.append(box(130, 80, 440, 54, "DefaultAccountRepository", "data access and caching policy", '1+', '', 'gear'))
P.append(wire('M280 135L170 168' + head(170, 168, 'd')))
P.append(wire('M420 135L530 168' + head(530, 168, 'd')))
P.append(box(0, 170, 340, 54, "LocalDataSource", "SwiftData / cache &middot; Unit 6", None, 'ghost', 'folder'))
P.append(box(360, 170, 340, 54, "RemoteDataSource", "REST API &middot; Unit 5", None, 'ghost', 'cloud'))
STRAT = [("Transaction history", "Cached display, background refresh"), ("Profile preferences", "Local persistence, synchronized"),
         ("Available balance", "Server-authoritative; label any cached value"), ("Payment execution", "Server-authoritative, never an offline cache write"),
         ("Payment status", "Reconcile with the authoritative status")]
S.append(slide("Part 6 &middot; Repository vs data source; caching (sections 12&ndash;13)", "The repository chooses where data comes from", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.95fr) minmax(0,1.05fr);gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 700 226', 'AccountRepository, DefaultAccountRepository, local and remote data sources', 'ds', P, 'max-height:230px')}
        <div class="step">{card("Cache-first", ul("Show cached history fast", "Fetch updates; reconcile; show again"))}</div></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Data or operation", "Approach"], STRAT, 'tbl compact')}</div>
        <div class="warn step" data-label="Critical">{ul("A cached balance never authorizes a transfer")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A repository is an application-facing abstraction; a data source is a concrete mechanism. Click: in NPay&rsquo;s future, a DefaultAccountRepository coordinates data access and caching policy over a local data source, SwiftData or a cache, Unit 6, and a remote one, a REST API, Unit 5. Greyed out: not built today; the abstraction prepares for them.'),
                  ('SAY', 'Click: cache-first versus network-first. With ten thousand transactions, should History always wait for the backend? Cache-first reads the local copy and shows it quickly, then fetches authoritative updates, reconciles the cache and shows the refreshed history. It improves perceived responsiveness, but cached financial data must be clearly distinguished from current data.'),
                  ('SAY', 'Click: so it depends on the operation: history, cached with background refresh; preferences, local with sync; the available balance, server-authoritative, with any cached value clearly labelled; payment execution, server-authoritative, never an offline cache mutation; payment status, reconciled against the authoritative record. Click: the critical principle: a real payment app must not treat a locally cached balance as authorization to transfer money. Our in-memory repository is only a simulation.'),
                  ('CONNECT', 'Consistency.'))))

# ================================================================== Part 7 (14, 20)
divider(7, "Consistency and idempotency", "Atomic, and only once", 'Two problems actors don&rsquo;t solve alone.', 'The unsafe design.')
UNSAFE = """let balance = try await repository.fetchBalance()

guard balance >= amount else {
    throw PaymentError.insufficientBalance
}

try await repository.saveTransaction(payment)
try await repository.updateBalance(balance - amount)"""
SPLIT = ["two ₹1,500 payments at once, ₹2,000 balance", "split read / save / update, on an actor (ours):", "&ensp;both <b>accepted</b>: 2 transactions, ₹3,000", "&ensp;balance ₹500 (each wrote 2,000 &minus; 1,500)", "",
         "recordPayment (one call): 1 accepted, 1 rejected"]
S.append(slide("Part 7 &middot; Repository consistency (section 14)", "Read, then later write: the balance can move", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 14: an unsafe design", UNSAFE, "font-size:12.5px")}
        {card("Two problems", ul("The balance can change between read and update", "Save can succeed while update fails"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(MAC + " (a 20 ms await stands in for I/O)", SPLIT, 11.5)}</div>
        <div class="rule step" data-label="Ours">{ul("Validate and mutate in one actor call", "No suspension inside")}</div>
        <div class="warn step" data-label="Not production">{ul("No durable transactions, no cross-device consistency")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The unsafe design: fetch the balance, check it, then save the transaction and update the balance in two more calls. Two problems: the balance can change between reading and updating; and saving might succeed while the balance update fails, leaving inconsistent records.'),
                  ('SAY', 'Click: we built exactly that shape, on an actor, so every individual call is data-race safe, with a short await between reading and writing standing in for any I/O. Two ₹1,500 payments at once from ₹2,000: both accepted. Two transactions totalling ₹3,000, and the balance ₹500, because both computed 2,000 minus 1,500 from the same stale read. The single recordPayment call: one accepted, one rejected. Actor isolation was never the problem; the suspension in the middle of the workflow was.'),
                  ('SAY', 'Click: so our repository validates and mutates in one actor call with no suspension inside: check the request, check the balance, create, deduct, insert, return. Click: production-ready? No: that protects one actor instance&rsquo;s memory. Durable database transactions, cross-device consistency and server-enforced authorization must come from the backend and persistence architecture.'),
                  ('CONNECT', 'One more trap: the same request twice.'))))

S.append(slide("Part 7 &middot; Duplicate payment requests (section 20)", "Concurrency safety &ne; idempotency", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console(MAC + ": the same request, twice, one after the other", ["transactions 2, balance 2,199,900", "(₹1,500.50 taken twice)"], 12)}
        <div class="step">{tbl(["Concurrency safety", "Idempotency"], [("Safe concurrent access to state", "The same logical request applied once"), ("The actor provides it", "Needs a request identifier")], 'tbl compact')}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Where it&rsquo;s enforced", ul("The backend, with request IDs and authoritative records", "Later: use cases (4.6) and networking (Unit 5)"))}</div>
        <div class="rule step" data-label="Remember">{ul("The UI guards (isProcessing, isSubmitting) don&rsquo;t reach the server")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Suppose the same logical payment is submitted twice, one after the other. The actor executes both safely, and we measured it: two transactions, balance 2,199,900: ₹1,500.50 taken twice. Safely, and wrongly.'),
                  ('SAY', 'Click: concurrency safety and idempotency are different. Actor isolation prevents unsafe concurrent access to its state. Idempotency prevents the same logical request from being applied more than once, and it needs an identifier for the request.'),
                  ('SAY', 'Click: in a real payment system the backend enforces idempotency with request identifiers and authoritative transaction records; we revisit it with use cases and networking. Click: and the guards we already have, the sheet&rsquo;s isProcessing and the ViewModel&rsquo;s isSubmitting, only stop a double tap in this process; they never reach the server.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.5', (), [("db", "A repository hides where data lives", "one contract: fetchSnapshot, recordPayment"),
                     ("shield", "One atomic actor call", "1 of 2 accepted; the split workflow took ₹3,000 from ₹2,000"),
                     ("layers", "Share it; refresh deliberately", "one repository, two ViewModels, explicit refresh")],
          'Three things to remember. A repository is the application&rsquo;s contract for domain data; it hides whether data comes from memory, a database or an API, and the service above it translates its errors into payment errors. Payment and balance must change together: our actor does it in one non-suspending call, so concurrent payments cannot overdraw, while the split read-save-update workflow accepted ₹3,000 from ₹2,000. And share one repository across ViewModels, but refresh their snapshots deliberately: a snapshot never updates itself, and a failed refresh is not a failed payment.')

review_divider(10)
review([("db", "Choose one", "What does a repository primarily abstract?",
         "What does a repository primarily abstract?<br>A. SwiftUI colours<br>B. Data access and persistence details<br>C. Navigation animations", "B",
         "Memory, database or API: the caller can&rsquo;t tell.",
         "Putting business workflows in the repository.", "Most pick B.", None),
        ("frame", "Question", "Does LazyVStack automatically provide database pagination?",
         "Does <code>LazyVStack</code> automatically provide database pagination?", "No",
         "Lazy views, not lazy data (3.11).",
         "Confusing layout with data loading.", "Most say no.", "Spaced review from Lesson 3.11."),
        ("file", "Choose one", "Why expose recordPayment as one operation?",
         "Why expose <code>recordPayment</code> as one operation?<br>A. To create more ViewModels<br>B. To avoid using protocols<br>C. To keep balance and transaction consistent", "C",
         "Split calls took ₹3,000 from ₹2,000.",
         "Exposing save and update separately.", "Most pick C.", None),
        ("shield", "Question", "Does actor isolation automatically provide durable database transactions?",
         "Does actor isolation automatically provide durable database transactions?", "No",
         "It protects one instance&rsquo;s memory, nothing on disk.",
         "Treating an actor like a database.", "Some say yes.", None),
        ("layers", "Question", "Should DashboardViewModel and PaymentViewModel use independent repositories?",
         "Should DashboardViewModel and PaymentViewModel use independent account repositories?", "No",
         "A separate one showed ₹25,000 forever.",
         "Two sources of truth.", "Most say no.", None),
        ("clock", "Question", "Does a successful payment guarantee the dashboard refresh will succeed?",
         "Does a successful payment guarantee that a subsequent dashboard refresh will succeed?", "No",
         "Separate operations; handle each outcome.",
         "Reading a failed refresh as a failed payment.", "Some say yes.", None),
        ("check", "Question", "Does actor isolation automatically prevent duplicate logical payments?",
         "Does actor isolation automatically prevent duplicate logical payment requests?", "No",
         "The same request twice: two transactions.",
         "Confusing safety with idempotency.", "Some say yes.", None),
        ("diff", "Predict the result", "Split read/save/update, two ₹1,500 at once from ₹2,000?",
         "The section 14 workflow (read balance, await, save, update) runs twice at once: ₹1,500 each from ₹2,000, on an actor. Result?<br>A. One accepted, one rejected<br>B. Both accepted; balance ₹500<br>C. A compile error", "B",
         "Both read 2,000 before either wrote.",
         "Assuming actor methods make workflows atomic.", "Many pick A.", None),
        ("phone", "Predict the result", "Pay ₹1,500.50 without refresh: the dashboard shows?",
         "One repository; the payment ViewModel pays ₹1,500.50; the dashboard ViewModel isn&rsquo;t refreshed. It shows&hellip;<br>A. ₹23,499.50<br>B. ₹25,000.00<br>C. ₹0", "B",
         "A snapshot; the repository holds 2,349,950.",
         "Expecting snapshots to update themselves.", "Many pick A.", None),
        ("key", "Choose one", "From 4.4: which keyword marks an existential?",
         "From Lesson 4.4: in <code>private let repository: ___ AccountRepository</code>, which keyword makes existential use explicit?<br>A. some<br>B. any<br>C. actor", "B",
         "<code>any AccountRepository</code>: any conforming value.",
         "Mixing up some and any.", "Most pick B.", "Spaced review from Lesson 4.4.")])

S.append(next_slide('4.5', [("4.6", "Domain models &amp; use cases", "SendPaymentUseCase over the repository"),
                            ("4.7", "UI state modeling", "PaymentError becomes specific messages"),
                            ("Units 5&ndash;6", "Networking; persistence", "remote and local data sources behind the repository"),
                            ("Unit 8", "Concurrency", "actor reentrancy, beyond today&rsquo;s split workflow")],
                    'Lesson 4.6 adds a SendPaymentUseCase between the ViewModel and the repository, the natural home for rules like idempotency. 4.7 turns PaymentError into specific, accessible messages. Units 5 and 6 add the remote and local data sources, and Unit 8 studies actor reentrancy.'))

S.append(lab_slide('4.5', "An account repository", "Contract, actor, service, dashboard.",
                   ["Add PaymentRecord, AccountSnapshot, AccountRepository.",
                    "Write InMemoryAccountRepository as an actor.",
                    "Run section 8&rsquo;s lab and section 19&rsquo;s tests.",
                    "Add RepositoryPaymentService with error mapping.",
                    "Share one repository via NPayDependencies.",
                    "Pay, then refresh the dashboard; compare."],
                   "", 'Expected, as in our run: 2,500,000 → 2,349,950; both tests pass; concurrent payments never overdraw; the dashboard is stale until refresh(); the same request twice is recorded twice.',
                   side=f'<div>{card("You hand in", ul("Your repository files", "Console output of the labs", "One sentence: why one recordPayment call"))}</div>'))

end_slide('4.5', 'Repository Pattern &amp;<br>Data Access', 'Lesson 4.6 &mdash; Domain Models &amp; Use Cases',
          'You can now hide data access behind a repository contract, keep payment and balance consistent in one actor call, translate storage errors into payment errors, share a repository across ViewModels, and tell concurrency safety from atomicity and idempotency.',
          'Next, Lesson 4.6: domain models and use cases, starting with SendPaymentUseCase.')

write_deck(OUT45, '4.5', 'Repository Pattern &amp; Data Access', 'Repository Pattern &amp; Data Access')
