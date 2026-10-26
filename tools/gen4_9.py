"""Generates decks/unit-4/lesson-4.9/index.html from the Lesson 4.9 text (Architecture Testing: XCTest, Swift Testing &
Mock Dependencies; Part 1 Sections 1-9, Part 2 Sections 10-17, a continuation from Section 17 to 27). Evidence: real
test runs in tools/sim4_9 - NPayCore's test targets (3 XCTest + 12 Swift Testing tests, coverage), NPayAppTests (the
app's own payment sources compiled for tests: 4 ViewModel tests), and experiments.sh (a planted boundary bug with and
without the at-limit test, the duplicate test hanging without the busy guard)."""
import html, os, re, sys
OUT49 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.9', 'Architecture Testing:<br>XCTest &amp; Swift Testing',
            'Prove that payments work, fail safely and never double-submit, <b>without opening the simulator</b>.',
            'Lesson 4.8 gave NPay modules: NPayApp, NPayDomain, NPayData. Today: how do we prove that NPay processes payments correctly, rejects insufficient balances, prevents duplicate submissions and keeps account state consistent, without opening the simulator every time? We write the text&rsquo;s tests for all four layers, run them for real with XCTest and Swift Testing, measure coverage, then break the code on purpose to see what the tests catch, and what they don&rsquo;t.')
outcomes_slide('4.9', [("check", "Write arrange-act-assert unit tests"),
                       ("diff", "Use XCTest and Swift Testing side by side"),
                       ("layers", "Test domain, repository, use case and ViewModel"),
                       ("key", "Isolate a ViewModel with mock dependencies"),
                       ("clock", "Test async code deterministically, no sleeps"),
                       ("eye", "Read coverage critically; test boundaries")])
where_slide('4.9', 'Today: tests for every layer', (),
            '4.8: NPayDomain and NPayData as real modules.',
            'Unit, integration and async ViewModel tests.',
            'The modules from 4.8 make testing natural: each layer can be tested on its own. The text came in three pieces; the third continues from Section 17. Every test on these slides was run.',
            'The milestone.')

# ================================================================== Part 1 (1, 2, 3)
divider(1, "Unit testing", "Small, isolated, deterministic", 'Four layers; two frameworks.', 'The milestone.')
P = []
for i, (ic, t, sub) in enumerate([("check", "Domain", "PaymentAmount, PaymentRecipient, PaymentPolicy"), ("gear", "Use case", "SendPaymentUseCase: limits, failures"),
                                  ("db", "Repository", "balance consistency, records"), ("layers", "ViewModel", "states, errors, duplicates")]):
    x = i * 280
    P.append(tall(x, 0, 260, 120, ic, t, sub, f'{i + 1}' if i < 3 else '4+', ''))
AAA = """// Arrange
let input = 150_050

// Act
let amount = try PaymentAmount(paise: input)

// Assert
#expect(amount.paise == 150_050)"""
XS = [("XCTestCase classes", "@Test functions"), ("XCTAssertEqual", "#expect"), ("XCTAssertThrowsError", "#expect(throws:)"),
      ("Supports UI testing", "Unit and integration tests"), ("Existing codebases", "New Swift tests (Xcode 16+)")]
S.append(slide("Part 1 &middot; Milestone, unit tests, two frameworks (sections 1&ndash;3)", "Four layers to test", f"""  <div class="body">
    {cues(4)}
    {svg('0 0 1100 120', 'Domain, use case, repository and ViewModel tests', 'layers', P, 'max-height:124px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:20px;align-items:start">
      <div class="step">{code("Arrange, act, assert", AAA, "font-size:12px")}</div>
      <div class="step">{tbl(["XCTest", "Swift Testing"], XS, 'tbl compact')}</div>
    </div>
  </div>""", notes(('SAY', 'By the end of today we test four layers. Click through: domain tests for PaymentAmount, PaymentRecipient and PaymentPolicy; use-case tests for SendPaymentUseCase&rsquo;s limits and failures; repository tests for balance consistency and records; and ViewModel tests for submission states, errors and duplicate prevention. Small, deterministic tests first; asynchronous ViewModel tests at the end.'),
                  ('SAY', 'Click: a unit test verifies a small, isolated behaviour in three stages: arrange the inputs, act by executing the behaviour, assert the result. For NPay: arrange an amount, act by creating PaymentAmount, assert it holds the expected paise; and creating one with minus a hundred should throw.'),
                  ('SAY', 'Click: two frameworks. XCTest is mature, with XCTestCase classes, XCTAssertEqual, XCTAssertThrowsError, and UI testing; it fills existing codebases. Swift Testing is Swift-native: @Test functions, #expect, #expect(throws:), mostly unit and integration tests, available from Xcode 16. We use both.'),
                  ('CONNECT', 'The first test, both ways.'))))

# ================================================================== Part 2 (4, 5, 6)
divider(2, "First tests", "PaymentAmount in XCTest and Swift Testing", 'Written, run, passing.', 'XCTest.')
XT = """import XCTest
@testable import NPayDomain

final class PaymentAmountTests: XCTestCase {

    func testValidAmount() throws {
        let amount = try PaymentAmount(paise: 150_050)
        XCTAssertEqual(amount.paise, 150_050)
    }

    func testZeroAmountRejected() {
        XCTAssertThrowsError(try PaymentAmount(paise: 0))
    }

    func testNegativeAmountRejected() {
        XCTAssertThrowsError(try PaymentAmount(paise: -100))
    }
}"""
ST = """import Testing
@testable import NPayDomain

struct PaymentAmountSwiftTests {

    @Test
    func validAmount() throws {
        let amount = try PaymentAmount(paise: 150_050)
        #expect(amount.paise == 150_050)
    }

    @Test
    func zeroAmountRejected() {
        #expect(throws: PaymentDomainError.self) {
            try PaymentAmount(paise: 0)
        }
    }
}"""
S.append(slide("Part 2 &middot; PaymentAmount, twice (sections 4, 6)", "Same behaviour, two test styles", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("Section 4: XCTest", XT, "font-size:10.5px")}
        <div class="step">{console("swift test", ["Executed 3 tests, with 0 failures"], 11.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("Section 6: Swift Testing", ST, "font-size:10.5px")}
        <div class="step">{console("swift test", ["&#10004; validAmount()&ensp;&#10004; zeroAmountRejected()"], 11.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 4&rsquo;s XCTest: a class inheriting XCTestCase; testValidAmount asserts 150,050 paise; two tests assert that zero and minus a hundred throw. PaymentAmount now lives in NPayDomain, so, as the text&rsquo;s module note says, we import NPayDomain instead of NPay. Section 6 writes the same as Swift Testing: a plain struct, @Test functions, #expect for the value and #expect(throws:) for the error type.'),
                  ('SAY', 'Click: we added these to NPayCore&rsquo;s NPayDomainTests target and ran swift test: XCTest executed three tests with no failures. Click: Swift Testing reported validAmount and zeroAmountRejected passing. Both frameworks run side by side in one test target.'),
                  ('CONNECT', 'What happens behind ⌘U?'))))

P = []
for i, (ic, t, sub) in enumerate([("tap", "Test action", "the test plan"), ("gear", "Build system", "app + test modules"), ("play", "Test runner", "loads test code"),
                                  ("check", "Assertions", "actual vs expected"), ("file", "Report", "passed, failed, skipped")]):
    x = i * 228
    P.append(tall(x, 0, 208, 110, ic, t, sub, f'{i + 1}' if i < 4 else '5+', ''))
    if i < 4:
        P.append(wire(f'M{x + 209} 55H{x + 226}' + head(x + 226, 55, 'r')))
S.append(slide("Part 2 &middot; Running tests (section 5) &middot; conceptual", "Product &rarr; Test, or &#8984;U", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 110', 'Test action, build system, test runner, assertions, report', 'run', P, 'max-height:118px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("In Xcode", ul("&#8984;U runs the test plan", "Test Navigator: each result"))}</div>
      <div class="step">{card("Here (no Xcode project)", ul("<code>swift test</code> in each package", "Same frameworks, same runner output"))}</div>
    </div>
  </div>""", notes(('SAY', 'Product, Test, or Command-U. Click through: the test action starts the selected test plan; the build system compiles the app and test modules; the test runner loads and executes the test code; assertions compare actual and expected behaviour; the report shows passed, failed and skipped tests.'),
                  ('SAY', 'Click: in Xcode, the Test Navigator shows each result. Click: our course repository has no Xcode project, so we ran the same tests with swift test inside the packages; the frameworks and the runner&rsquo;s output are the same.'),
                  ('CONNECT', 'Many inputs, one test.'))))

# ================================================================== Part 3 (7, 8, 9)
divider(3, "Parameters and boundaries", "Test the edges", 'Where off-by-one bugs live.', 'Parameterized.')
PAR = """@Test(arguments: [0, -1, -100, -50_000])
func rejectsNonPositiveAmounts(paise: Int) {
    #expect(throws: PaymentDomainError.self) {
        try PaymentAmount(paise: paise)
    }
}"""
POL = """let policy = PaymentPolicy(
    maximumPerPaymentPaise: 10_000_000)

@Test func acceptsAmountAtLimit() throws {
    let amount = try PaymentAmount(paise: 10_000_000)
    try policy.validate(amount)
}

@Test func rejectsAmountAboveLimit() throws {
    let amount = try PaymentAmount(paise: 10_000_001)
    #expect(throws: PaymentDomainError.self) {
        try policy.validate(amount)
    }
}"""
S.append(slide("Part 3 &middot; Parameterized and boundary tests (sections 7&ndash;9)", "Just below, exactly at, just above", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("Section 7", PAR, "font-size:11.5px")}
        <div class="step">{console("swift test", ["&#10004; rejectsNonPositiveAmounts(paise:) with 4 test cases", "&#10004; rejectsBlank(identifier:) with 3 test cases (ours)"], 11)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("Section 9: PaymentPolicy at its boundary", POL, "font-size:11px")}
        <div class="step">{console("swift test", ["&#10004; acceptsAmountAtLimit()&ensp;&#10004; rejectsAmountAboveLimit()"], 11)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 7: instead of a test per invalid amount, one parameterized test with arguments zero, minus one, minus a hundred and minus fifty thousand. Click: Swift Testing ran it as four test cases. We added a PaymentRecipient test the lab checklist asks for: blank, spaces and a newline, three cases, plus one that checks trimming.'),
                  ('SAY', 'Section 8&rsquo;s boundary-value analysis: for the illustrative ₹1,00,000 limit, test just below, exactly at and just above the limit. Section 9 does the two that matter most: exactly 10,000,000 paise must be accepted, 10,000,001 must throw. Click: both pass, with no ViewModel, repository or screen in sight. Part 7 shows why the at-limit test earns its place.'),
                  ('CONNECT', 'Now the actor.'))))

# ================================================================== Part 4 (10, 11, 12, 13)
divider(4, "Repository and use case", "Async tests against real components", 'Including concurrency.', 'The repository.')
REP = """@Test
func insufficientBalanceDoesNotChangeState() async throws {
    let repository = InMemoryAccountRepository(
        initialBalancePaise: 10_000)
    do {
        _ = try await repository.recordPayment(
            recipient: "ravi@npay", amountPaise: 50_000)
        Issue.record("Expected insufficient balance")
    } catch AccountRepositoryError.insufficientBalance {
        // Expected rejection.
    }
    let snapshot = try await repository.fetchSnapshot()
    #expect(snapshot.balancePaise == 10_000)
    #expect(snapshot.transactions.isEmpty)
}"""
S.append(slide("Part 4 &middot; Test the actor-based repository (sections 10&ndash;11)", "Rejected means unchanged", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:20px;align-items:start">
      {code("Section 11", REP, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("swift test (NPayDataTests, ours target)", ["&#10004; paymentUpdatesBalanceAndHistory()", "&#10004; insufficientBalanceDoesNotChangeState()"], 11)}</div>
        <div class="step">{card("Section 10", ul("2,500,000 &minus; 150,050 = 2,349,950", "One transaction"))}</div>
        <div class="rule step" data-label="Principle">{ul("Assert no partial mutation too")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The repository is an actor, so these tests are async and use await. Section 10: pay ₹1,500.50 from ₹25,000 and expect the amount, a balance of 2,349,950 and one transaction. Section 11, on the slide: ₹500 from ₹100. Inside do, Issue.record fails the test if no error is thrown; catch the expected insufficientBalance; then, crucially, assert the balance is still 10,000 and there are no transactions.'),
                  ('SAY', 'Click: both pass. They live in a second test target we added to NPayCore, NPayDataTests, because they need NPayData as well as NPayDomain. Click: Section 10&rsquo;s numbers. Click: the principle: a test should verify not only that an error occurred, but that the rejected operation did not partially mutate account state.'),
                  ('CONNECT', 'Two payments at once.'))))

CONC = """async let first = attemptPayment(
    repository: repository, recipient: "a@npay",
    amountPaise: 150_000)
async let second = attemptPayment(
    repository: repository, recipient: "b@npay",
    amountPaise: 150_000)

let results = await [first, second]
// … count successes, read the snapshot
#expect(successCount == 1)
#expect(snapshot.balancePaise == 50_000)
#expect(snapshot.transactions.count == 1)"""
S.append(slide("Part 4 &middot; Test concurrent payments (section 12)", "The text&rsquo;s own correction, confirmed", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:10px">
        {console("First version: async let first = Result { try await &hellip; }", ["error: cannot pass function of type", "'() async throws -> PaymentRecord' to parameter", "expecting synchronous function type"], 11)}
        <div class="step">{card("Why", ul("<code>Result.init(catching:)</code> takes a synchronous closure", "Hence the text&rsquo;s <code>attemptPayment</code> helper"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="step">{code("Corrected version (condensed)", CONC, "font-size:11px")}</div>
        <div class="step">{console("swift test", ["&#10004; concurrentPaymentsDoNotOverdraw()"], 11.5)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 12 first writes the concurrent test with Result wrapping a try await, then corrects itself. We compiled the first version: "cannot pass function of type async throws to parameter expecting synchronous function type". Click: Result&rsquo;s catching initializer takes a synchronous closure, which is why the text introduces an async attemptPayment helper that returns a Result.'),
                  ('SAY', 'Click: the corrected test: two async let payments of ₹1,500 from ₹2,000 through the helper; await both; count the successes; expect exactly one, a balance of ₹500 and one transaction. Click: it passes, the test version of what Lesson 4.5 showed with print statements.'),
                  ('CONNECT', 'The use case, and a real integration.'))))

UC = """@Test
func paymentIntegrationTest() async throws {
    let repository = InMemoryAccountRepository(
        initialBalancePaise: 2_500_000)
    let useCase = SendPaymentUseCase(
        repository: repository,
        policy: PaymentPolicy(maximumPerPaymentPaise: 10_000_000))
    let command = SendPaymentCommand(
        recipient: try PaymentRecipient("ravi@npay"),
        amount: try PaymentAmount(paise: 150_050))

    let payment = try await useCase.execute(command)
    let snapshot = try await repository.fetchSnapshot()

    #expect(payment.amountPaise == 150_050)
    #expect(snapshot.balancePaise == 2_349_950)
    #expect(snapshot.transactions.count == 1)
    #expect(snapshot.transactions.first?.id == payment.id)
}"""
S.append(slide("Part 4 &middot; Use case and integration tests (sections 13, 23)", "Rule tested twice, at two boundaries", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:20px;align-items:start">
      {code("Section 23: real components together", UC, "font-size:10px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("swift test", ["&#10004; useCaseEnforcesPaymentLimit()", "&#10004; paymentIntegrationTest()", "&#10004; Test run with 12 tests in 5 suites", "Executed 3 tests (XCTest), 0 failures"], 11)}</div>
        <div class="step">{card("Two boundaries", ul("Policy test: the rule itself", "Use-case test: the operation applies it"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 13 tests the use case: ₹1,50,000 against a ₹1,00,000 limit with plenty of balance; expect limitExceeded and no transactions. Why test the policy and the use case? The policy test proves the rule; the use-case test proves the operation actually applies it. Different boundaries.'),
                  ('SAY', 'Section 23, on the slide, is an integration test: the real use case and the real in-memory repository together; pay ₹1,500.50 and check the amount, the balance, one transaction, and that the stored record&rsquo;s ID is the payment&rsquo;s. Integration tests catch problems isolated mocks can miss.'),
                  ('SAY', 'Click: the whole NPayCore suite: twelve Swift Testing tests in five suites, and three XCTest tests, all passing. Click: the two boundaries again.'),
                  ('CONNECT', 'Now the ViewModel, which lives in the app.'))))

# ================================================================== Part 5 (14, 15, 16, 17)
divider(5, "ViewModel tests with mocks", "Inject a controllable use case", 'A protocol where it earns its place.', 'The seam.')
SEAM = """protocol SendPaymentExecuting: Sendable {
    func execute(_ command: SendPaymentCommand)
        async throws -> PaymentRecord
}

extension SendPaymentUseCase: SendPaymentExecuting {}

// PaymentViewModel
private let sendPayment: any SendPaymentExecuting

struct MockSendPaymentUseCase: SendPaymentExecuting {
    let shouldFail: Bool

    func execute(_ command: SendPaymentCommand)
        async throws -> PaymentRecord {
        if shouldFail {
            throw PaymentDomainError.insufficientBalance
        }
        return PaymentRecord(id: UUID(),
            recipient: command.recipient.identifier,
            amountPaise: command.amount.paise, createdAt: .now)
    }
}"""
S.append(slide("Part 5 &middot; A protocol and a mock use case (sections 14&ndash;15)", "The ViewModel accepts any SendPaymentExecuting", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:20px;align-items:start">
      {code("Sections 14&ndash;15 (condensed)", SEAM, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("In NPay (ours)", ul("New file in Features/Payments", "The app still pays: ₹23,499.50"))}</div>
        <div class="step">{card("Testing the app&rsquo;s code (ours)", ul("NPayAppTests: the app&rsquo;s files, symlinked", "Imports NPayPayments, not NPay"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The ViewModel depends on the concrete SendPaymentUseCase struct: fine for production, inflexible for isolated tests. Two choices, as the text says: test with a real use case on an in-memory repository, or introduce a small protocol and inject a mock. The text introduces SendPaymentExecuting, makes the use case conform with an empty extension, and changes the ViewModel to hold any SendPaymentExecuting. The mock conforms too: it throws insufficientBalance or returns a record built from the command. No repository, no database.'),
                  ('SAY', 'Click: we made that change in NPay, a new file in Features/Payments, and rebuilt and re-ran the app: the payment still ends at ₹23,499.50 and all four tabs work.'),
                  ('SAY', 'Click: the text uses @testable import NPay from an Xcode test target. Without an Xcode project, we built a small test package, NPayAppTests, that compiles the app&rsquo;s own payment files, symlinked, not copied, as a module; so the tests import NPayPayments where the text imports NPay, and test the very code the app ships.'),
                  ('CONNECT', 'The tests.'))))

VMT = """let viewModel = PaymentViewModel(
    sendPayment: MockSendPaymentUseCase(shouldFail: true))

let result = await viewModel.submit(command)

if case .failure(let message) = result {
    #expect(message == "Insufficient balance")
} else {
    Issue.record("Expected failure result")
}

if case .failure(let message) = viewModel.state {
    #expect(message == "Insufficient balance")
} else {
    Issue.record("Expected failure UI state")
}"""
S.append(slide("Part 5 &middot; ViewModel success and failure (sections 16&ndash;17)", "Presentation behaviour, without a screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:20px;align-items:start">
      {code("Section 17 (condensed; section 16 mirrors it for success)", VMT, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("swift test (NPayAppTests)", ["&#10004; successfulPaymentUpdatesState()", "&#10004; insufficientBalanceUpdatesFailureState()", "&#10004; realChainShowsInsufficientBalanceMessage() (ours)"], 11)}</div>
        <div class="step">{card("Ours: the real chain", ul("Real use case + repository, ₹500 from ₹100", "Exact message &ldquo;Insufficient balance&rdquo;", "Would have failed before 4.7&rsquo;s mapping fix"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 16 injects a succeeding mock and checks that submit returns success with 150,050 paise and that the observable state is success. Section 17, on the slide, injects a failing mock and checks that both the returned result and the state carry exactly "Insufficient balance". The ViewModel calls the use case, catches the error and exposes the failure, with no SwiftUI. These are unit tests of presentation behaviour, not UI automation.'),
                  ('SAY', 'Click: both pass. Click: we added one integration-style test of our own: the real use case and repository, ₹500 from ₹100, asserting the exact message. The mock-based test passes even if the real use case leaks the repository&rsquo;s own error; this one would have failed before Lesson 4.7&rsquo;s mapping fix, exactly the gap 4.7&rsquo;s generic message revealed. Mocks test the ViewModel; the real chain tests the contract between layers.'),
                  ('CONNECT', 'Duplicate submissions: an async test.'))))

# ================================================================== Part 6 (18, 19, 20, 21)
divider(6, "Async tests, deterministically", "Hold the dependency open", 'Continuations, not sleeps.', 'The controllable mock.')
SUS = """actor SuspendedPaymentUseCase: SendPaymentExecuting {
    private var continuation:
        CheckedContinuation<PaymentRecord, Error>?
    private var invocationCount = 0

    func execute(_ command: SendPaymentCommand)
        async throws -> PaymentRecord {
        invocationCount += 1
        return try await withCheckedThrowingContinuation {
            continuation = $0
        }
    }

    func calls() -> Int { invocationCount }

    func succeed() {
        continuation?.resume(returning: PaymentRecord(
            id: UUID(), recipient: "ravi@npay",
            amountPaise: 150_050, createdAt: .now))
        continuation = nil
    }
}"""
S.append(slide("Part 6 &middot; A controllable mock; the duplicate test (sections 18&ndash;19)", "The test decides when the payment completes", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:20px;align-items:start">
      {code("Section 18", SUS, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Section 19&rsquo;s test", ul("Start submit #1; wait until the mock is called", "Submit #2: expect a failure", "Expect calls() == 1; then succeed()", "#1 ends in success"))}
        <div class="step">{console("swift test", ["&#10004; duplicateSubmissionIsRejected()&ensp;(&lt; 1 s)"], 11.5)}</div>
        <div class="warn step" data-label="Caution">{ul("Resume every continuation exactly once", "Bound every wait")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'To test duplicate submission we need the first payment to stay in flight. SuspendedPaymentUseCase, an actor, counts calls and, inside withCheckedThrowingContinuation, stores the continuation instead of finishing: the ViewModel stays submitting until the test calls succeed, which resumes it with a record.'),
                  ('SAY', 'Section 19&rsquo;s test: start the first submit in a Task; yield until the mock has been called once; submit again and expect a failure; expect calls to still be one; then succeed and expect the first submission to end in success. Click: it passes in well under a second, with no sleeps.'),
                  ('SAY', 'Click: the text&rsquo;s cautions: every checked continuation must be resumed exactly once, and the polling loop is a teaching shortcut; a robust suite bounds its waits so a regression cannot hang the run. Let&rsquo;s see what that regression looks like.'),
                  ('CONNECT', 'Remove the guard.'))))

ASY = [("Arbitrary sleep", "Timing-dependent"), ("Controlled mock completion", "Deterministic when synchronized"), ("Test expectations", "Explicitly await an event"), ("Injected clock", "Retry and debounce tests")]
S.append(slide("Part 6 &middot; Why tests need bounded, controlled waits (sections 19&ndash;21)", "A regression shouldn&rsquo;t hang the suite", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("experiments.sh (ours): PaymentViewModel without its isBusy guard", ["duplicateSubmissionIsRejected:", "&ensp;no result; stopped after <b>40 s</b>", "&ensp;(with the guard: passes in &lt; 1 s)"], 11.5)}
        <div class="step">{card("Why it hung", ul("Submit #2 also reached the mock", "Its continuation replaced #1&rsquo;s", "#1 never resumed: firstTask.value waits forever"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Approach", "Reliability"], ASY, 'tbl compact')}</div>
        <div class="rule step" data-label="So">{ul("Control completion; bound the wait (a time limit)", "Never Task.sleep and hope")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'We removed the isBusy guard from a copy of the ViewModel and ran Section 19&rsquo;s test. It produced no result at all; we stopped it after forty seconds. With the guard it passes in under a second.'),
                  ('SAY', 'Click: why it hung: without the guard, the second submit also reached the mock; its continuation replaced the first one&rsquo;s, so the first was never resumed, and the test&rsquo;s await on the first task waits forever. A regression became a hang, not a failure: exactly why the text asks for bounded waits, for example a Swift Testing time-limit trait, and for resuming every continuation exactly once.'),
                  ('SAY', 'Click: Section 20&rsquo;s table: an arbitrary sleep is timing-dependent, wasteful on fast machines and too short on slow ones; controlled mock completion is deterministic; expectations explicitly await an event; an injected clock suits retry and debounce tests later. Click: control completion, bound the wait, never sleep and hope. The text&rsquo;s eight-stage lifecycle stepper was shared at stage one; this run is its sharpest lesson.'),
                  ('CONNECT', 'How do unit tests fit with the rest?'))))

# ================================================================== Part 7 (22, 24)
divider(7, "Layers and coverage", "What each test proves", 'And what 92% doesn&rsquo;t.', 'The pyramid.')
P = []
for i, (t, sub, w) in enumerate([("UI tests", "complete user journeys", 360), ("Integration tests", "ViewModel + use case + repository", 600), ("Unit tests", "value objects, policies, isolated ViewModels", 840)]):
    y = i * 70
    x = (840 - w) // 2
    P.append(box(x, y, w, 58, t, sub, None, 'ghost' if i == 0 else '', ''))
LAY = [("Unit", "PaymentAmount rejects zero"), ("Integration", "₹1,500.50 updates the repository; one transaction"), ("UI (Unit 9)", "enter, review, confirm, see success")]
S.append(slide("Part 7 &middot; Unit, integration and UI tests (section 22)", "Different purposes, different costs", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      {svg('0 0 840 198', 'UI tests at the top, integration tests, unit tests at the base', 'pyr', P, 'max-height:210px')}
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Layer", "NPay example"], LAY, 'tbl compact')}
        <div class="step">{card("Today&rsquo;s count", ul("Unit and integration: 3 XCTest + 16 Swift Testing", "UI tests: Unit 9"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Three layers. Unit tests at the base: value objects, policies, isolated ViewModels, like PaymentAmount rejecting zero. Integration tests in the middle: ViewModel, use case and repository together, like ₹1,500.50 updating the shared repository with one transaction. UI tests at the top, greyed out here: complete journeys, entering a recipient, reviewing, confirming and seeing success; Unit 9 covers UI automation.'),
                  ('SAY', 'Click: today we have three XCTest tests and sixteen Swift Testing tests, twelve in NPayCore and four on the app&rsquo;s payment code, all unit or integration.'),
                  ('CONNECT', 'Coverage: what does it tell us?'))))

COV = [("InMemoryAccountRepository.swift", "95.00%"), ("AccountRepository.swift", "100.00%"), ("PaymentAmount.swift", "100.00%"),
       ("PaymentRecipient.swift", "100.00%"), ("SendPaymentUseCase.swift", "82.35%"), ("<b>Total</b>", "<b>92.16%</b>")]
BUG = ["'&lt;=' changed to '&lt;' in PaymentPolicy:", "&ensp;&#10008; acceptsAmountAtLimit(): Caught error .limitExceeded", "", "same bug, at-limit test removed:",
       "&ensp;&#10004; 11 tests passed", "&ensp;coverage: SendPaymentUseCase 82.35%, total 92.16%"]
S.append(slide("Part 7 &middot; What does coverage mean? (section 24)", "Same coverage, bug or no bug", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:10px">
        {tbl(["NPayCore file (swift test --enable-code-coverage)", "Lines"], COV, 'tbl compact')}
      </div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="step">{console("experiments.sh (ours): a planted boundary bug", BUG, 11)}</div>
        <div class="rule step" data-label="So">{ul("Coverage shows what ran, not what was checked", "Test behaviours and boundaries")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Coverage measures which code ran during tests. NPayCore&rsquo;s report: the repository 95%, the contract, amount and recipient files 100%, SendPaymentUseCase 82%, its unmapped error branches never hit, and 92% overall.'),
                  ('SAY', 'Click: then a planted bug, ours: in PaymentPolicy, less-than-or-equal became less-than, so a payment exactly at the limit is wrongly refused. The full suite caught it: acceptsAmountAtLimit failed with "caught error limitExceeded". Then we removed that one test and kept the bug: eleven tests passed, and the coverage was identical, 82.35% for the file, 92.16% overall. The bug was invisible to coverage; only the boundary assertion saw it.'),
                  ('SAY', 'Click: so coverage is a useful signal of what ran, but not a substitute for meaningful assertions. The text&rsquo;s list of NPay scenarios to test: valid payments, zero and negative amounts, an empty recipient, insufficient balance, exactly at and above the limit, concurrent requests, duplicates, repository failure, and, once networking exists, unknown remote outcomes.'),
                  ('CONNECT', 'Where do tests live?'))))

# ================================================================== Part 8 (25, 26)
divider(8, "Organizing tests", "A test tree and a checklist", 'Ours, run.', 'The tree.')
TREE = """NPayCore/Tests/
├── NPayDomainTests/
│   ├── PaymentAmountTests.swift          (XCTest)
│   ├── PaymentAmountSwiftTests.swift     (+ parameterized)
│   └── PaymentPolicyTests.swift          (+ recipient)
└── NPayDataTests/
    ├── AccountRepositoryTests.swift
    └── SendPaymentUseCaseTests.swift     (+ integration)

NPayAppTests/Tests/NPayPaymentsTests/
├── TestDoubles/
│   ├── MockSendPaymentUseCase.swift
│   └── SuspendedPaymentUseCase.swift
└── ViewModels/
    └── PaymentViewModelTests.swift"""
CK = [("Swift Testing target", "&#10003;"), ("PaymentAmount valid / invalid", "&#10003;"), ("PaymentPolicy boundaries", "&#10003;"), ("PaymentRecipient validation", "&#10003; (ours)"),
      ("Repository payment; insufficient balance", "&#10003;"), ("Concurrent payments", "&#10003;"), ("Use-case policy", "&#10003;"),
      ("ViewModel success, failure, overlap", "&#10003;"), ("Whole suite; coverage", "&#10003; test.sh")]
S.append(slide("Part 8 &middot; Test organization and the lab checklist (sections 25&ndash;26)", "Tests next to the module they test", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:20px;align-items:start">
      {code("Our test tree", TREE, "font-size:10.5px")}
      <div class="step">{tbl(["Lab checklist", "Done"], CK, 'tbl compact')}</div>
    </div>
  </div>""", notes(('SAY', 'Section 25 suggests an NPayTests folder split into Domain, UseCases, Repositories, ViewModels and TestDoubles, and notes that once domain and data are package targets, tests can live in their package&rsquo;s test targets. That is what we did: domain tests in NPayDomainTests, repository, use-case and integration tests in NPayDataTests, and the ViewModel tests with their two test doubles in NPayAppTests. In Xcode: Command-U, the Test Navigator, coverage reports and breakpoints in tests.'),
                  ('SAY', 'Click: the lab checklist, run: every item done. One script, test.sh, runs both packages and prints coverage; experiments.sh repeats the planted bug and the missing guard.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.9', (), [("check", "Every layer, its own tests", "3 XCTest + 16 Swift Testing, all passing"),
                     ("key", "Mocks for isolation, real chains for contracts", "the real chain checks the exact message"),
                     ("clock", "Deterministic async; meaningful assertions", "no guard: a hang; no boundary test: a hidden bug at 92%")],
          'Three things to remember. Each layer gets tests at its own boundary: domain values and policies, the actor repository including concurrency, the use case, and the ViewModel, which we tested on the app&rsquo;s own source. Mocks isolate the ViewModel, while a real-chain test checks the contract between layers, which mocks cannot. And async tests must control completion and bound their waits, and assertions must target boundaries: removing a guard turned a test into a hang, and a planted off-by-one bug survived at 92% coverage until the at-limit assertion caught it.')

review_divider(10)
review([("check", "Choose one", "What is the main purpose of a unit test?",
         "What is the main purpose of a unit test?<br>A. Test only UI animations<br>B. Verify a small behaviour in isolation<br>C. Replace the compiler", "B",
         "PaymentAmount(paise: 0) throws: one behaviour.",
         "Testing everything at once.", "Most pick B.", None),
        ("key", "Choose one", "Why use mocks in ViewModel tests?",
         "Why use mocks in ViewModel tests?<br>A. To control dependency behaviour<br>B. To generate real payments<br>C. To replace SwiftUI rendering", "A",
         "shouldFail, or held open with a continuation.",
         "Waiting for real failures.", "Most pick A.", None),
        ("eye", "Question", "Does 100% line coverage guarantee correctness?",
         "Does 100% line coverage guarantee correctness?", "No",
         "The planted bug kept coverage at 92.16%.",
         "Treating coverage as a quality score.", "Some say yes.", None),
        ("clock", "Choose one", "Why avoid arbitrary sleeps in async tests?",
         "Why avoid arbitrary sleeps in async tests?<br>A. They disable actors<br>B. They prevent compilation<br>C. They create timing-dependent tests", "C",
         "Too slow on fast machines, too short on slow ones.",
         "Sleeping until it passes.", "Most pick C.", None),
        ("layers", "Choose one", "What does an integration test verify?",
         "What does an integration test verify?<br>A. Multiple components working together<br>B. Only one pure function<br>C. Only app-icon rendering", "A",
         "Use case + repository: 2,349,950 and one record.",
         "Mocking everything.", "Most pick A.", None),
        ("db", "Question", "Should rejected payments leave the repository state unchanged?",
         "Should rejected payments leave the repository state unchanged?", "Yes",
         "Asserted: balance 10,000, no transactions.",
         "Checking only that an error was thrown.", "Most say yes.", None),
        ("shield", "Question", "Does local duplicate-submission protection guarantee backend idempotency?",
         "Does local duplicate-submission protection guarantee backend idempotency?", "No",
         "It stops a second call in this process only.",
         "Confusing UI guards with the server.", "Most say no.", None),
        ("diff", "Predict the result", "'<=' becomes '<' in PaymentPolicy, at-limit test removed: what changes?",
         "PaymentPolicy&rsquo;s <code>&lt;=</code> becomes <code>&lt;</code>, and the at-limit test is deleted. What happens?<br>A. Tests fail; coverage drops<br>B. Tests pass; coverage unchanged<br>C. It doesn&rsquo;t compile", "B",
         "11 passed; 82.35% and 92.16%, as before.",
         "Trusting coverage to reveal bugs.", "Many pick A.", None),
        ("clock", "Predict the result", "Remove isBusy's guard; run the duplicate test. Result?",
         "PaymentViewModel loses its <code>isBusy</code> guard. Section 19&rsquo;s duplicate test then&hellip;<br>A. Fails quickly<br>B. Passes<br>C. Never finishes", "C",
         "The first continuation is never resumed.",
         "Assuming a regression always fails cleanly.", "Many pick A.", None),
        ("folder", "Choose one", "From 4.8: which tests can reach an internal type in NPayDomain?",
         "From Lesson 4.8: an internal type in NPayDomain is reachable from tests that&hellip;<br>A. Import NPay<br>B. Use <code>@testable import NPayDomain</code><br>C. Live in any folder", "B",
         "@testable opens internal declarations to the test module.",
         "Making everything public for tests.", "Some pick A.", "Spaced review from Lesson 4.8.")])

S.append(next_slide('4.9', [("4.10", "Integration lab", "the complete MVVM NPay, with these tests running"),
                            ("Unit 5", "Networking", "tests with a mocked transport; unknown outcomes"),
                            ("Unit 8", "Concurrency", "injected clocks; bounded waits"),
                            ("Unit 9", "Testing &amp; quality", "UI automation, test plans, CI")],
                    'Lesson 4.10 consolidates Unit 4 into a complete MVVM NPay with this suite running. Unit 5 tests networking with mocked transports, Unit 8 brings injected clocks and bounded waits, and Unit 9 adds UI automation and continuous integration.'))

S.append(lab_slide('4.9', "NPay architecture tests", "One suite for every layer.",
                   ["Add Swift Testing and XCTest tests for PaymentAmount.",
                    "Test PaymentPolicy at, below and above the limit.",
                    "Test the repository: success, rejection, concurrency.",
                    "Add SendPaymentExecuting and a mock.",
                    "Test ViewModel success, failure, duplicates.",
                    "Plant a bug; check the tests and the coverage."],
                   "", 'Expected, as in our run: all green; a planted boundary bug fails exactly the at-limit test; without it, coverage stays the same and the bug survives.',
                   side=f'<div>{card("You hand in", ul("Your test files", "Test run and coverage output", "Your planted bug and which test caught it"))}</div>'))

end_slide('4.9', 'Architecture Testing:<br>XCTest &amp; Swift Testing', 'Lesson 4.10 &mdash; Unit 4 Integration Lab',
          'You can now test every layer of NPay with XCTest and Swift Testing, isolate a ViewModel with mocks, test async code deterministically, and read coverage critically.',
          'Next, Lesson 4.10: the Unit 4 integration lab, a complete MVVM NPay.')

write_deck(OUT49, '4.9', 'Architecture Testing: XCTest &amp; Swift Testing', 'Architecture Testing: XCTest &amp; Swift Testing')
