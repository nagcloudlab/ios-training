"""Generates decks/unit-1/lesson-1.10/index.html from the Lesson 1.10 text (PocketBank -> NPay).
Unit 01 finale. The text's 19 sections are grouped into 8 Parts; its code was verified as the NPayCore Swift package."""
import html, os, re, sys
OUT110 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit1.py')).read())   # Unit 01 helpers
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'
tbl = lambda head_, rows, cls='tbl compact': f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head_) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'

title_slide('1.10', 'Build NPay&rsquo;s<br>Domain Model',
            'Everything from Unit 01, in one small banking engine, <b>with tests</b>.',
            'This is the final lesson of Unit 01. We have covered types, optionals, functions and closures, structs and classes, protocols, generics and errors, ARC and concurrency. Today we connect them by designing the core engine of NPay: a small, well-structured Swift banking simulation with tests, not disconnected examples. Everything on these slides was built and tested as a real Swift package.')
outcomes_slide('1.10', [("layers", "Split a design into <b>responsibilities</b>"),
                        ("bank", "Model <b>Money</b>, accounts and transactions as values"),
                        ("cross", "Describe failures with a <b>domain error</b> type"),
                        ("lock", "Protect shared state with an <b>actor ledger</b>"),
                        ("check", "Test it with <b>Swift Testing</b>"),
                        ("eye", "Spot <b>reentrancy</b> races; review the architecture")])
where_slide('1.10', 'Today: putting Unit 01 together', (),
            'Lesson 1.9: tasks, structured concurrency, cancellation, actors and Sendable.',
            'Money, accounts, a protocol, an actor ledger and tests, as one Swift package.',
            'Lesson 1.9 gave us actors and Sendable. Today they hold up a real design, together with everything else from the unit. By the end you will have the deliverable your training plan names for Unit 01: a cross-platform Swift package with Money, accounts, a ledger actor and tests.',
            'Start with what the engine must do.')

# ================================================================== Part 1 (1-2)
divider(1, "The challenge and the architecture", "Decide responsibilities before code", 'Eight capabilities. Which Swift feature carries each one?', 'Architecture first.')
CAPS = ["Create accounts", "Represent money accurately", "Deposit and withdraw", "Validate transfers",
        "Store transaction records", "Load data asynchronously", "Prevent unsafe concurrent changes", "Handle failures explicitly"]
P = [box(0, 0, 560, 50, 'ViewModel', 'coordinates user actions', '1', '', 'layout'), wire('M280 54V70' + head(280, 70, 'd')),
     box(0, 76, 560, 50, 'BankingService protocol', 'what the engine can do', '2', '', 'link'), wire('M280 130V146' + head(280, 146, 'd')),
     box(0, 152, 560, 50, 'BankLedger actor', 'protects shared account state', '3', '', 'lock'), wire('M140 206V222' + head(140, 222, 'd')), wire('M420 206V222' + head(420, 222, 'd')),
     box(0, 228, 270, 50, 'BankAccount', 'value', '4+', '', 'user'), box(290, 228, 270, 50, 'Transaction', 'value', '4+', '', 'file')]
S.append(slide("Part 1 &middot; Architecture (sections 1&ndash;2)", "Four layers, one job each", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:.8fr 1.2fr;gap:28px;align-items:start">
      {card("The engine must", '<ul style="margin:6px 0 0;font-size:18px">' + ''.join(f'<li>{c}</li>' for c in CAPS) + '</ul>')}
      <div>{svg('0 0 560 278', 'ViewModel, BankingService protocol, BankLedger actor, and BankAccount and Transaction values', 'arch', P, 'max-height:330px')}
        {cues(4)}
        <p class="small muted" style="margin:8px 0 0">In-memory learning design. A real bank: server-side ledger, authentication, durable transactions, audit.</p></div>
    </div>
  </div>""", notes(('SAY', 'NPay&rsquo;s engine must create accounts, represent money accurately, deposit and withdraw, validate transfers, store transaction records, load data asynchronously, prevent unsafe concurrent changes, and handle failures explicitly. Before writing code, decide which Swift feature carries each job.'),
                  ('SAY', 'Click through the layers: a ViewModel coordinates user actions; a BankingService protocol defines what the engine can do; a BankLedger actor protects the shared account state; and BankAccount and Transaction are plain values.'),
                  ('ASK', 'Why not put everything in one BankAccount class? EXPECT: data, validation, transaction processing and synchronization are different responsibilities; separating them makes the design easier to reason about, test and extend.'),
                  ('SAY', 'This is an in-memory learning design. A real bank needs a server-side authoritative ledger, authentication, durable transactions and audit controls: the server is authoritative, as in Lesson 0.8.'),
                  ('CONNECT', 'Start at the bottom: money.'))))

# ================================================================== Part 2 (3-5)
divider(2, "Values: Money, Account, Transaction", "The data is all structs and enums", 'Lesson 1.2 said money is whole paise in Int64. Now it gets its own type.', 'Money first.')
MONEY = """struct Money: Equatable, Sendable {
    let paise: Int64

    init(paise: Int64) { self.paise = paise }

    var rupees: Decimal {
        Decimal(paise) / Decimal(100)
    }
}"""
ACC = """struct BankAccount: Identifiable, Sendable {
    let id: String
    let customerName: String
    var balance: Money
    var isActive: Bool
}"""
WHY = [("struct", "an amount is a <b>value</b> (1.5)"), ("Int64 paise", "<b>exact</b>; no binary fractions (1.2)"),
       ("Equatable", "compare amounts with <code>==</code>"), ("Sendable", "safe to cross into the actor (1.9)"),
       ("Identifiable", "a standard <code>id</code> contract")]
S.append(slide("Part 2 &middot; Money and account (sections 3&ndash;4)", "A Money type, and an account made of values", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Money.swift", MONEY, "font-size:14px")}
        <div class="gap"></div>
        {code("BankAccount.swift", ACC, "font-size:14px")}</div>
      <div>{tbl(["Choice", "Why"], WHY, 'tbl')}
        <div class="gap"></div>
        <div class="step">{card("2,500,000 paise", mono("Money(paise: 2_500_000).rupees  →  25000", 15) + ul("Formatting &#8377;25,000 stays in the ViewModel (0.2)"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Money is a struct, because an amount is a value; it stores whole paise in an Int64, exact, with no binary fractions, as Lesson 1.2 argued. It is Equatable so amounts compare with ==, and Sendable because this immutable value will cross into the ledger actor. rupees converts to Decimal for display.'),
                  ('SAY', 'BankAccount is also a value: an id, the customer name, a Money balance and an active flag. Identifiable gives it the standard id contract; Sendable lets it cross isolation boundaries. The shared, changing collection of accounts will live inside an actor, not in these structs.'),
                  ('SAY', 'Click: Money(paise: 2_500_000).rupees is 25000. Turning that into ₹25,000 with grouping is still the ViewModel&rsquo;s job.'),
                  ('CONNECT', 'Every change should leave a record.'))))

TX = """enum TransactionType: String, Sendable {
    case deposit, withdrawal, transfer
}

struct Transaction: Identifiable, Sendable {
    let id: UUID
    let accountId: String
    let type: TransactionType
    let amount: Money
    let timestamp: Date
}"""
ERR = """enum BankingError: Error {
    case accountNotFound
    case accountInactive
    case invalidAmount
    case insufficientFunds
    case sameAccountTransfer
    case arithmeticOverflow
}"""
S.append(slide("Part 2 &middot; Transactions and errors (sections 5&ndash;6)", "Enums for known cases: types and failures", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Transaction.swift", TX, "font-size:14px")}
        <div style="margin-top:12px">{card("enum TransactionType", ul("A <b>known set</b> of cases", "Not &ldquo;Deposit&rdquo;, &ldquo;deposit&rdquo;, &ldquo;DEPOSIT&rdquo;"))}</div></div>
      <div>{code("BankingError.swift", ERR, "font-size:14px")}
        <div style="margin-top:12px">{card("enum BankingError", ul("Says <b>why</b> it failed (1.7)", "Better than returning <code>false</code>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Every deposit, withdrawal or transfer should produce a record. The type is an enum because valid types form a known set; that is safer than strings like Deposit, deposit and DEPOSIT, which a typo silently breaks.'),
                  ('SAY', 'Failures get their own enum, as in Lesson 1.7: account not found, inactive, invalid amount, insufficient funds, a transfer to the same account, arithmetic overflow. A good error model says why an operation failed; a Boolean false loses that information.'),
                  ('CONNECT', 'Now the contract for the whole engine.'))))

# ================================================================== Part 3 (7)
divider(3, "The service contract", "A protocol for the engine", 'The ViewModel should not care how banking is implemented.', 'Define what, not how.')
SVC = """protocol BankingService: Sendable {
    func balance(for accountId: String) async throws -> Money
    func deposit(_ amount: Money, into accountId: String) async throws
    func withdraw(_ amount: Money, from accountId: String) async throws
    func transfer(_ amount: Money,
                  from sourceId: String,
                  to destinationId: String) async throws
}"""
P = [box(160, 0, 300, 52, 'BankingService', 'protocol', None, 'lit', 'link'),
     wire('M210 56L90 92' + head(90, 92, 'd'), None, 'dash'), wire('M310 56V92' + head(310, 92, 'd'), None, 'dash'), wire('M410 56L530 92' + head(530, 92, 'd'), None, 'dash'),
     box(0, 98, 190, 52, 'BankLedger', 'in-memory actor', None, '', 'lock'), box(215, 98, 190, 52, 'Mock', 'tests, previews', None, '', 'check'),
     box(430, 98, 190, 52, 'Network', 'real backend later', None, '', 'globe')]
S.append(slide("Part 3 &middot; Contract (section 7)", "One protocol, several implementations", f"""  <div class="body">
    {code("BankingService.swift", SVC, "font-size:15px")}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:1.1fr .9fr;gap:24px;align-items:center">
      {svg('0 0 620 150', 'BankingService is implemented by the BankLedger actor, a mock, and later a network service', 'svc', P, 'max-height:170px')}
      <div class="step">{card("Why", ul("<code>async throws</code>: any implementation may wait or fail", "<code>Sendable</code>: safe to share (1.6, 1.9)", "The ViewModel depends on <b>this</b> (4.5)"))}</div>
    </div>
  </div>""", notes(('SAY', 'BankingService says what the engine can do: read a balance, deposit, withdraw, transfer. Every requirement is async throws, because some implementation may need to wait, for the network for example, and any of them can fail. It is Sendable, as Lesson 1.9 explained, because it will be shared across isolation boundaries.'),
                  ('SAY', 'It says nothing about how. Today&rsquo;s in-memory BankLedger actor implements it; a mock can implement it for tests and previews; later a network-backed service can implement it.'),
                  ('SAY', 'Click: the ViewModel depends on this protocol, not on a concrete type: dependency injection from Lesson 1.6, built properly in Lesson 4.5.'),
                  ('CONNECT', 'The interesting implementation is the actor.'))))

# ================================================================== Part 4 (8-10)
divider(4, "The BankLedger actor", "Shared state behind one door", 'Two tasks withdraw from the same account at once. Who protects the balance?', 'An actor.')
LEDGER = """actor BankLedger: BankingService {
    private var accounts: [String: BankAccount]

    init(accounts: [BankAccount]) {
        self.accounts = Dictionary(uniqueKeysWithValues: accounts.map { ($0.id, $0) })
    }

    func balance(for accountId: String) throws -> Money {
        guard let account = accounts[accountId] else { throw BankingError.accountNotFound }
        return account.balance
    }
}"""
S.append(slide("Part 4 &middot; The actor (sections 8&ndash;9)", "The ledger owns the accounts", f"""  <div class="body">
    {code("BankLedger.swift", LEDGER, "font-size:14px")}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:repeat(3,1fr);gap:18px">
      {card("private var accounts", ul("Only the actor touches it"))}
      {card("No async needed", ul("Methods without <code>await</code> inside stay <b>sync</b>", "Callers outside still <code>await</code>"), 'step')}
      {card("Not a database", ul("One door, in memory", "No durability, no ACID"), 'step')}
    </div>
  </div>""", notes(('SAY', 'Without synchronization, two tasks could both read the same balance and both approve a withdrawal, the lost update from Lesson 1.9. So the account dictionary lives inside an actor, private, and only the actor touches it.'),
                  ('SAY', 'Click: balance(for:) is not marked async: it contains no suspension point. Yet it satisfies the protocol&rsquo;s async throws requirement, and code outside the actor still awaits it, because it may have to wait its turn. We compiled this under Swift 6.'),
                  ('SAY', 'Click: an actor serializes access to its own state; it is not a database transaction system. And actor methods are reentrant at suspension points, so for our transfer we deliberately keep validation and mutation free of await. Remember that for Part 7.'),
                  ('CONNECT', 'Deposits and withdrawals: validate, then change.'))))

WD = """func withdraw(_ amount: Money, from accountId: String) throws {
    guard amount.paise > 0 else { throw BankingError.invalidAmount }
    guard var account = accounts[accountId] else { throw BankingError.accountNotFound }
    guard account.isActive else { throw BankingError.accountInactive }
    guard account.balance.paise >= amount.paise else {
        throw BankingError.insufficientFunds
    }
    account.balance = Money(paise: account.balance.paise - amount.paise)
    accounts[accountId] = account
}"""
S.append(slide("Part 4 &middot; Deposit and withdraw (sections 9&ndash;10)", "Every guard before any change", f"""  <div class="body">
    {code("BankLedger+Withdraw.swift", WD, "font-size:14px")}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {card("Validation order", ul("Amount, account exists, active, enough funds", "Only <b>then</b> change the balance"))}
      <div class="step">{card("deposit", ul("Same guards, plus <code>addingReportingOverflow</code> (1.2)", "Overflow throws <code>.arithmeticOverflow</code>"))}</div>
    </div>
  </div>""", notes(('SAY', 'withdraw checks, in order: a positive amount, the account exists, it is active, and it has enough money. Only after every guard passes does it change the balance and write the account back into the dictionary. A failed withdrawal changes nothing.'),
                  ('SAY', 'With a non-negative balance and a positive amount no larger than it, the subtraction cannot overflow Int64.'),
                  ('SAY', 'Click: deposit uses the same guards, and addingReportingOverflow from Lesson 1.2, throwing arithmeticOverflow instead of crashing.'),
                  ('CONNECT', 'The most important operation touches two accounts.'))))

# ================================================================== Part 5 (11-13)
divider(5, "Transfers", "Two accounts, one logical change", 'Ravi sends Meena ₹5,000. Both balances must change, or neither.', 'Watch it.')
TR = """func transfer(_ amount: Money, from sourceId: String, to destinationId: String) throws {
    guard sourceId != destinationId else { throw BankingError.sameAccountTransfer }
    guard amount.paise > 0 else { throw BankingError.invalidAmount }
    guard var source = accounts[sourceId],
          var destination = accounts[destinationId] else { throw BankingError.accountNotFound }
    guard source.isActive, destination.isActive else { throw BankingError.accountInactive }
    guard source.balance.paise >= amount.paise else { throw BankingError.insufficientFunds }
    let (newDest, overflow) = destination.balance.paise.addingReportingOverflow(amount.paise)
    guard !overflow else { throw BankingError.arithmeticOverflow }
    source.balance = Money(paise: source.balance.paise - amount.paise)
    destination.balance = Money(paise: newDest)
    accounts[sourceId] = source
    accounts[destinationId] = destination          // no await anywhere above
}"""
P = [box(0, 0, 260, 56, 'Ravi', '&#8377;25,000', '0', '', 'user'), fade('1+', box(0, 0, 260, 56, 'Ravi', '&#8377;20,000', None, 'lit', 'user')),
     wire('M264 28H316' + head(316, 28, 'r'), '1+'), '<text class="sm" x="290" y="18" text-anchor="middle">&#8377;5,000</text>',
     box(322, 0, 260, 56, 'Meena', '&#8377;10,000', '0', '', 'user'), fade('1+', box(322, 0, 260, 56, 'Meena', '&#8377;15,000', None, 'lit', 'user')),
     '<text class="sm" x="291" y="84" text-anchor="middle">total stays &#8377;35,000</text>']
S.append(slide("Part 5 &middot; Transfer (section 11)", "All the checks, then both writes, no await", f"""  <div class="body">
    {cues(1)}
    {code("BankLedger+Transfer.swift", TR, "font-size:12.5px")}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:1fr 1fr;gap:24px;align-items:center">
      {svg('0 0 582 90', 'Ravi 25,000 sends 5,000 to Meena 10,000; afterwards Ravi 20,000 and Meena 15,000; total 35,000', 'tr', P, 'max-height:110px')}
      <div class="step">{card("Safe here because", ul("The actor owns both accounts", "<b>No <code>await</code></b> between check and change"))}</div>
    </div>
  </div>""", notes(('SAY', 'A transfer changes two accounts: the source goes down, the destination goes up, as one logical operation. The method checks everything first: not the same account, a positive amount, both accounts exist and are active, enough funds, and no overflow at the destination. Only then does it write both accounts.'),
                  ('SAY', 'Click: Ravi ₹25,000 sends ₹5,000 to Meena ₹10,000. Afterwards ₹20,000 and ₹15,000; the total stays ₹35,000 in this zero-fee example.'),
                  ('SAY', 'Click: why is this safe? The actor owns both accounts, and there is no await between validation and mutation, so no other call on the ledger can interleave with this critical section. It is still an in-memory simulation: no durable transactions, no distributed consistency, nothing survives the process ending.'),
                  ('CONNECT', 'Call it from app code.'))))

APP = """let ledger = BankLedger(accounts: [
    BankAccount(id: "NP1001", customerName: "Ravi",
                balance: Money(paise: 2_500_000), isActive: true),
    BankAccount(id: "NP2002", customerName: "Meena",
                balance: Money(paise: 1_000_000), isActive: true)
])
try await ledger.transfer(Money(paise: 500_000), from: "NP1001", to: "NP2002")
print("Ravi:", try await ledger.balance(for: "NP1001").rupees)
print("Meena:", try await ledger.balance(for: "NP2002").rupees)"""
ENTRY = """struct LedgerEntry: Sendable {
    let id: UUID
    let accountId: String
    let amountPaise: Int64       // − debit, + credit
    let timestamp: Date
}"""
S.append(slide("Part 5 &middot; Using it, and history (sections 12&ndash;13)", "Run a transfer; then record it properly", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1.15fr .85fr;gap:24px;align-items:start">
      <div>{code("App.swift", APP, "font-size:13px")}
        <div style="margin-top:12px">{card("Real output", mono("Ravi: 20000<br>Meena: 15000", 16) + '<p class="small muted" style="margin:6px 0 0">A further &#8377;90,000 transfer: <code>Transfer failed: insufficientFunds</code></p>')}</div></div>
      <div class="step">{code("LedgerEntry.swift", ENTRY, "font-size:13px")}
        <div style="margin-top:12px">{card("A transfer = two entries", ul("A <b>debit</b> and a <b>credit</b>", "Durable, consistent storage is the <b>backend&rsquo;s</b> job", "Double entry, idempotency, audit"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'App code creates the ledger with Ravi and Meena, transfers ₹5,000 with try await, and reads both balances. Real output: Ravi 20000, Meena 15000; rupees is a Decimal, so formatting with ₹ and grouping is still the ViewModel&rsquo;s job. A second transfer of ₹90,000 fails with insufficientFunds.'),
                  ('SAY', 'Click: our ledger changes balances but keeps no history. A stronger design stores ledger entries: for a transfer, a debit on one account and a credit on the other.'),
                  ('SAY', 'In a real bank, entries and balances must be committed durably and consistently, which leads to double-entry bookkeeping, idempotency, auditability and transactional databases. Those are backend guarantees, not something Swift actors provide.'),
                  ('CONNECT', 'Does it actually work? Prove it with tests.'))))

# ================================================================== Part 6 (14-15)
divider(6, "Testing the domain", "No iPhone needed", 'Domain logic separate from SwiftUI can be tested on any machine.', 'Swift Testing.')
T1 = """import Testing
@testable import NPayCore

@Test func transferMovesMoney() async throws {
    let ledger = makeLedger(2_500_000, 1_000_000)  // Ravi, Meena
    try await ledger.transfer(Money(paise: 500_000),
                              from: "A", to: "B")
    #expect(try await ledger.balance(for: "A").paise == 2_000_000)
    #expect(try await ledger.balance(for: "B").paise == 1_500_000)
}"""
T2 = """@Test func insufficientFundsChangesNothing() async throws {
    let ledger = makeLedger(100_000, 50_000)
    await #expect(throws: BankingError.insufficientFunds) {
        try await ledger.transfer(Money(paise: 200_000),
                                  from: "A", to: "B")
    }
    #expect(try await ledger.balance(for: "A").paise == 100_000)
    #expect(try await ledger.balance(for: "B").paise == 50_000)
}"""
S.append(slide("Part 6 &middot; Tests (sections 14&ndash;15)", "@Test and #expect", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("TransferTests.swift", T1, "font-size:12.5px")}
        <div style="margin-top:12px">{card("@Test, #expect", ul("<code>@Test</code> marks a test", "<code>#expect</code> fails the test if false"))}</div></div>
      <div class="step">{code("FailureTests.swift", T2, "font-size:12.5px")}
        <div style="margin-top:12px">{card("Precise failure test", ul("The <b>exact</b> error, not just &ldquo;some error&rdquo;", "And <b>nothing changed</b>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Because the domain is separate from SwiftUI, we test it without launching an iPhone interface. transferMovesMoney builds a ledger, transfers ₹5,000, reads both balances with await, and checks them with #expect. @Test marks a test; #expect reports a failure if its condition is false. makeLedger is a small helper that creates Ravi and Meena.'),
                  ('SAY', 'Click: good engineers test failures too. The lesson text&rsquo;s version checks that some BankingError is thrown. We tightened it, as the text suggests: the exact error, insufficientFunds, and that neither balance changed.'),
                  ('SAY', 'A passing test shows correctness for that scenario; it does not prove the whole system correct. That is why we write many.'),
                  ('CONNECT', 'Here is the full list we ran.'))))

CASES = [("Valid transfer", "both balances updated", "&#10003;"), ("Insufficient funds (2 tests)", "rejected; exact error, nothing changes", "&#10003;"),
         ("Same-account transfer", "rejected", "&#10003;"), ("Inactive account", "rejected", "&#10003;"),
         ("Destination overflow", "rejected", "&#10003;"), ("Negative deposit", "rejected", "&#10003;"),
         ("₹7,000 + ₹6,000 at once from ₹10,000", "exactly one succeeds", "&#10003;")]
S.append(slide("Part 6 &middot; Test plan (section 15)", "Eight tests, all passing", f"""  <div class="body">
    {tbl(["Scenario", "Expected", "Result"], CASES, 'tbl compact')}
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px;align-items:start">
      {card("swift test", mono("✔ Test run with 8 tests passed", 16))}
      {card("Still to add", ul("Valid deposit and withdrawal", "Transaction history entries"))}
    </div>
  </div>""", notes(('SAY', 'The lesson lists the scenarios every banking model should consider. We wrote them as Swift Testing tests in the NPayCore package: valid transfer, insufficient funds with nothing changed, same-account transfer, inactive account, destination overflow, negative deposit, plus a concurrency test: transfers of ₹7,000 and ₹6,000 at the same time from ₹10,000 must leave exactly one succeeding.'),
                  ('SAY', 'Click: swift test: all eight passed. Still to add from the list: valid deposit and withdrawal, and once history exists, its entries. That is part of the lab.'),
                  ('CONNECT', 'That concurrency test passed because of one detail. Change it and watch it break.'))))

# ================================================================== Part 7 (16-17)
divider(7, "Reentrancy", "When an actor is not enough", 'Ravi has ₹10,000. Two withdrawals arrive together: ₹7,000 and ₹6,000. Both cannot succeed.', 'Unless we put an await in the wrong place.')
RE = """actor AccountStore {
    var balancePaise: Int64 = 1_000_000            // ₹10,000

    func withdraw(_ amountPaise: Int64) async throws {
        guard balancePaise >= amountPaise else {
            throw BankingError.insufficientFunds
        }
        await performExternalCheck()     // others may run
        balancePaise -= amountPaise
    }
}"""
P = [box(0, 0, 552, 44, 'A checks ₹10,000 ≥ ₹7,000: ok', '', '1', '', 'check'),
     box(0, 54, 552, 44, 'A awaits the external check', 'the actor is free again', '2', '', 'clock'),
     box(0, 108, 552, 44, 'B checks ₹10,000 ≥ ₹6,000: ok', 'stale: A hasn&rsquo;t paid yet', '3', '', 'check'),
     box(0, 162, 552, 44, 'A pays ₹7,000, then B pays ₹6,000', '', '4', '', 'send'),
     fade('5+', box(0, 216, 552, 44, 'Balance: −₹3,000', 'measured', None, 'alert', 'cross'))]
S.append(slide("Part 7 &middot; Reentrancy (sections 16&ndash;17)", "Check, await, change: the check goes stale", f"""  <div class="body">
    {cues(5)}
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("AccountStore.swift", RE, "font-size:13px")}
      {svg('0 0 552 260', 'A checks, awaits; B checks the old balance; both pay; balance minus 3,000', 're', P, 'max-height:300px')}
    </div>
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("Real runs", mono("check, await, change → both ok, &#8377;&minus;3,000<br>await, then check + change → one rejected, &#8377;4,000", 14))}
      <div class="rule" data-label="Rule">{ul("Actor isolation does <b>not</b> make a multi-step async operation atomic")}</div>
    </div>
  </div>""", notes(('SAY', 'An actor lets one task in at a time, but it is reentrant: at an await, the actor is free to run other calls. This AccountStore checks the balance, then awaits an external check, then subtracts.'),
                  ('SAY', 'Click through: A checks ₹10,000 against ₹7,000: fine. A awaits the external check, and the actor is free. B checks ₹10,000 against ₹6,000: fine, but stale, because A has not paid yet. A pays, then B pays. Click: −₹3,000.'),
                  ('SAY', 'Click: we ran both versions. Check, await, change: both withdrawals succeeded and the balance went to minus ₹3,000. Await first, then check and change together with no suspension in between: one was rejected and ₹4,000 remained. That is why our BankLedger&rsquo;s transfer has no await inside it, and why its concurrency test passed.'),
                  ('SAY', 'The rule: never assume actor isolation makes a multi-step asynchronous business operation atomic. Keep validation and mutation together without suspension, or re-validate after the await. In a real bank this is a database and business-consistency problem; Lesson 8.4 goes deeper.'),
                  ('CONNECT', 'Step back and look at the whole design.'))))

# ================================================================== Part 8 (18-19 + unit wrap)
divider(8, "The whole architecture", "Every Unit 01 idea has a job", 'From the SwiftUI view down to the Money struct.', 'One map, one table.')
CONCEPTS = [("Struct", "<code>Money</code>, <code>BankAccount</code>, <code>Transaction</code>", "1.5"), ("Enum", "<code>TransactionType</code>, <code>BankingError</code>", "1.2, 1.7"),
            ("Protocol", "<code>BankingService</code>", "1.6"), ("Generics", "repositories, API responses", "1.7"),
            ("Optionals", "a missing account in the dictionary", "1.3"), ("throws", "every failed operation", "1.7"),
            ("async/await", "calls into the ledger", "1.9"), ("Actor", "<code>BankLedger</code>", "1.9"),
            ("Sendable", "values crossing into the actor", "1.9"), ("ARC", "ViewModel and service lifetimes", "1.8")]
P = [box(0, 0, 400, 44, 'SwiftUI View', 'presentation', None, '', 'phone'), box(0, 54, 400, 44, 'ViewModel', 'state, async coordination', None, '', 'layout'),
     box(0, 108, 400, 44, 'BankingService', 'injection', None, '', 'link'), box(0, 162, 400, 44, 'BankLedger actor', 'shared state', None, 'lit', 'lock'),
     box(0, 216, 400, 44, 'Money · BankAccount · Transaction', 'structs', None, '', 'bank')]
S.append(slide("Part 8 &middot; Architecture (section 18)", "Ten concepts, one engine", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:.75fr 1.25fr;gap:24px;align-items:start">
      {svg('0 0 400 260', 'SwiftUI View, ViewModel, BankingService, BankLedger actor, and value types', 'all', P, 'max-height:340px')}
      {tbl(["Concept", "NPay usage", "Lesson"], CONCEPTS, 'tbl compact')}
    </div>
  </div>""", notes(('SAY', 'The whole design: a SwiftUI view presents; a ViewModel holds observable state and coordinates async work; it depends on the BankingService protocol; the BankLedger actor protects shared state; and the data is plain value types.'),
                  ('SAY', 'And every Unit 01 concept has a job. Structs for Money, accounts and transactions; enums for transaction types and errors; a protocol for the service; generics for reusable repositories and API responses; optionals for a missing account; throws for failures; async and await for ledger calls; an actor for shared state; Sendable for values crossing into it; and ARC for the lifetimes of the ViewModel and services.'),
                  ('CONNECT', 'Now review it like a senior engineer.'))))

# ================================================================== recap
recap_u1('1.10', (), [("bank", "Values for data", "Money in paise, structs, enums"),
                      ("lock", "One owner for shared state", "an actor; no await mid-change"),
                      ("check", "Prove it with tests", "including failures and concurrency")],
         'Three things to remember. Data is values: Money in exact paise, accounts and transactions as structs, closed sets as enums. Shared state has one owner, the actor, and its critical sections contain no await, because actors are reentrant. And prove the design with tests, including failure cases and a concurrent one, on any machine.')

# ================================================================== architecture review (text 19)
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Architecture review</h2>
  </div>
""" + notes(('SAY', 'Review the design as a senior engineer would before a team builds it. Eight questions: the lesson&rsquo;s five, then three more. Commit to an answer before each reveal.')) + "</section>\n\n")
review([("bank", "Question", "Can an in-memory actor replace a bank's production database?",
         "Can this in-memory <code>BankLedger</code> actor replace a bank&rsquo;s production database?", "No",
         "No durability, no ACID transactions, nothing survives the process. The server&rsquo;s ledger is authoritative (0.8).",
         "Thinking actor safety equals transactional safety.", "Most say no; ask why.", None),
        ("eye", "Question", "Can an actor method still have a logical race?",
         "Can an actor method still have a logical race?", "Yes",
         "At an <code>await</code> the actor runs other calls; a check before it can go stale (we measured &minus;&#8377;3,000).",
         "Believing actors make every method atomic.", "Many say no.", None),
        ("diff", "Question", "Why is Money a struct rather than a class?",
         "Why is <code>Money</code> a struct rather than a class?", "It&rsquo;s a value",
         "Two equal amounts are interchangeable, there is no identity, and copies can&rsquo;t race; it is Sendable for free.",
         "Defaulting to classes for &ldquo;important&rdquo; types.", "Most get it.", None),
        ("link", "Question", "Why should the ViewModel depend on BankingService?",
         "Why should the ViewModel depend on <code>BankingService</code> instead of <code>BankLedger</code>?", "To swap it",
         "Inject a mock in tests and previews, the in-memory ledger today, a network service later, with no ViewModel change.",
         "Coupling the UI to one implementation.", "Most get it.", None),
        ("shield", "Question", "Why validate on the server if the app already validates transfers?",
         "The app already validates transfers. Why must the server validate them too?", "Server decides",
         "The client can be modified, outdated or bypassed; the server owns the authoritative balance and rules (Unit 07).",
         "Trusting client-side checks.", "Some say it is redundant.", None),
        ("layers", "Predict the output", "Ravi has ₹10,000; transfers of ₹7,000 and ₹6,000 run concurrently on BankLedger. How many succeed?",
         "Ravi has &#8377;10,000. Transfers of &#8377;7,000 and &#8377;6,000 run concurrently on <code>BankLedger</code>. How many succeed?", "Exactly one",
         "The transfer checks and changes with no <code>await</code>, so the actor runs them one at a time. Our test confirms it.",
         "Expecting both, or neither.", "Some say both.", None),
        ("check", "Choose one", "Which test is most precise for a failed transfer?",
         "Which test is most precise for a transfer with insufficient funds?<br>A. <code>#expect(throws: BankingError.self)</code><br>B. <code>#expect(throws: BankingError.insufficientFunds)</code>, then check both balances<br>C. Expect the call to return false<br>D. Just check it doesn&rsquo;t crash", "B",
         "The exact error, plus proof nothing changed.",
         "Settling for &ldquo;some error happened&rdquo;.", "Some pick A.", None),
        ("clock", "Choose one", "Three independent requests of 2 s, 3 s and 1 s with async let take about?",
         "Three independent requests of 2 s, 3 s and 1 s, started with <code>async let</code>, take about:<br>A. 6 s<br>B. 1 s<br>C. 3 s<br>D. 2 s", "C",
         "They overlap; the total is roughly the slowest (measured 3.2 s).",
         "Adding the durations.", "Some pick A.", "Spaced review from Lesson 1.9.")])

# ================================================================== Unit complete + practice anywhere
UNIT = [("1.1", "Swift, compiler, SIL, LLVM"), ("1.2", "Variables, constants, types"), ("1.3", "Optionals"), ("1.4", "Functions, closures"),
        ("1.5", "Structs, classes, semantics"), ("1.6", "Protocols, extensions"), ("1.7", "Generics, errors"), ("1.8", "ARC, ownership"),
        ("1.9", "Concurrency, actors"), ("1.10", "NPay domain model")]
cells = ''.join(f'<div class="card accent" style="padding:12px 16px"><span class="label">{n}</span><p style="margin:2px 0 0;font-size:17px">{t}</p></div>' for n, t in UNIT)
S.append(slide("Unit 01 &middot; Complete", "Swift Language Mastery: done", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:repeat(5,1fr);gap:14px">{cells}</div>
    <div class="gap"></div>
    <div class="takeaway">Your plan&rsquo;s Unit 01 deliverable: a <b>cross-platform Swift package</b> with Money, accounts, a ledger actor and <b>tests</b>. That is the lab.</div>
  </div>""", notes(('SAY', 'That completes Unit 01: the compiler, types, optionals, functions and closures, structs and classes, protocols, generics and errors, ARC, concurrency, and today&rsquo;s domain model.'),
                  ('SAY', 'The training plan&rsquo;s Unit 01 deliverable is a cross-platform Swift package with Money, accounts, a ledger actor and tests. The final lab builds exactly that, and it runs on any computer, which is the next slide.'),
                  ('CONNECT', 'Can everyone practise this, even without a Mac?'))))

PKG = """swift package init --type library --name NPayCore
swift build
swift test          # runs the @Test functions"""
SUP = [("Swift language, Unit 01 labs", "&#10003;", "&#10003;", "&#10003;"), ("Swift Testing (<code>swift test</code>)", "&#10003;", "&#10003;", "&#10003;"),
       ("SwiftUI, UIKit, iOS Simulator", "&mdash;", "&#10003;", "&mdash;")]
S.append(slide("Unit 01 &middot; Practice anywhere", "Unit 01 runs on Windows, macOS and Linux", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:1fr 1fr;gap:24px;align-items:start">
      <div>{code("Terminal", PKG, "font-size:15px")}
        <div style="margin-top:12px">{card("Setup", ul("Install the Swift toolchain (swift.org)", "Windows: VS Code + the Swift extension", "macOS: Xcode or VS Code"))}</div></div>
      <div>{tbl(["", "Windows", "macOS", "Linux"], SUP, 'tbl')}
        <div class="gap"></div>
        <div class="tip" data-label="Unit 02">{ul("SwiftUI needs <b>macOS and Xcode</b>: everyone moves to a Mac for Unit 02")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Almost everything in Unit 01 is pure Swift, so it runs on Windows, macOS and Linux with the Swift toolchain from swift.org. On Windows, use VS Code with the Swift extension; on a Mac, Xcode or VS Code.'),
                  ('SAY', 'Swift Package Manager does the rest: swift package init creates the package, swift build builds it, and swift test runs the @Test functions. All the lesson code here was built and tested that way, on macOS.'),
                  ('SAY', 'What needs a Mac: SwiftUI, UIKit, the iOS Simulator and iOS app builds. So Unit 01 can be practised anywhere, and for Unit 02 everyone moves to macOS with Xcode, as the training plan says.'),
                  ('CONNECT', 'Where this goes next.'))))

S.append(next_slide('1.10', [("2.1", "Declarative UI, View &amp; body", "the first SwiftUI screen"),
                             ("2.2", "Xcode projects, simulator &amp; previews", "NPayCore inside an iOS app"),
                             ("4.3", "Domain entities &amp; use cases", "today&rsquo;s model, at app scale"),
                             ("4.5", "Dependency injection &amp; composition root", "injecting <code>BankingService</code>"),
                             ("8.4", "Actor reentrancy &amp; logical races", "the &minus;&#8377;3,000 bug, in depth"),
                             ("9.2", "Swift Testing framework", "more <code>@Test</code> and <code>#expect</code>")],
                    'Today&rsquo;s engine stays with us. Unit 02 builds the first SwiftUI screens and puts NPayCore into an Xcode project; Unit 04 turns it into domain entities and use cases with proper dependency injection; Lesson 8.4 returns to reentrancy; and Unit 09 extends the tests with Swift Testing.'))

LAB = """NPayCore/
├── Package.swift
├── Sources/NPayCore/
│   ├── Money.swift  BankAccount.swift  Transaction.swift
│   ├── BankingError.swift  BankingService.swift
│   └── BankLedger.swift
└── Tests/NPayCoreTests/
    └── LedgerTests.swift      // 8+ @Test functions"""
S.append(lab_slide('1.10', "Unit 01 checkpoint: NPayCore", "Build the package from today&rsquo;s slides and make every test pass. Any OS.",
                   ["Create the package; add the model, errors, protocol and <code>BankLedger</code>.",
                    "Write the eight tests from Part 6; run <code>swift test</code>.",
                    "Add valid deposit and withdrawal tests.",
                    "Stretch: record <code>LedgerEntry</code> debits and credits; test them.",
                    "Peer review against the eight architecture questions."],
                   "", 'Works on Windows, macOS and Linux with the Swift toolchain. Package.swift: swift-tools-version 6.0, a library target NPayCore and a test target NPayCoreTests depending on it. Make the types public, or use @testable import NPayCore in tests. Expected: all tests pass, including the concurrent ₹7,000 + ₹6,000 test (exactly one succeeds). Reference implementation verified with swift test (8 tests passed). Checkpoint rubric (plan: "build or explain a feature, review correctness, answer architecture questions"): correct values and errors; all guards before mutation; no await inside the transfer; failure tests check the exact error and unchanged balances; can explain the reentrancy race and why the server stays authoritative.',
                   side=f'<div>{code("Layout", LAB, "font-size:13px")}<div class="gap"></div>{card("You hand in", ul("<code>swift test</code> output", "Your answers to the architecture review"))}</div>'))

end_slide('1.10', 'Unit 01 complete:<br>Swift Language Mastery', 'Unit 02 &mdash; SwiftUI Fundamentals, Lesson 2.1: Declarative UI, View &amp; body',
          'You can now design a small Swift domain: values for money, accounts and transactions, enums for types and errors, a protocol for the service, an actor that owns shared state with no await mid-change, and tests that prove success, failure and concurrency. That completes Unit 01.',
          'Next, Unit 02: SwiftUI Fundamentals, starting with Lesson 2.1, declarative UI, View and body, on a Mac with Xcode, building NPay&rsquo;s first real screen on top of this engine.')

write_deck(OUT110, '1.10', 'NPay Domain Model', 'NPay Domain Model')
