"""Generates decks/unit-4/lesson-4.7/index.html from the Lesson 4.7 text (UI State Modeling & Async Payment Lifecycle;
Part 1 Sections 1-7, Part 2 Sections 8-15, a continuation from Section 15 to 24). Evidence: the text's ViewModel on the
Mac (observed states, double confirm, the failure message, cancellation before and after recording, stale results,
the section 22 test) and tools/sim4_7 (NPay with PaymentUIState: success, a refused payment keeping the sheet open,
a slow payment showing the submitting state with dismissal blocked)."""
import html, os, re, sys
OUT47 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

MAC = 'Mac run, the text&rsquo;s ViewModel'
title_slide('4.7', 'UI State Modeling &amp;<br>Async Payment Lifecycle',
            'Loading, success, failure, <b>and &ldquo;we don&rsquo;t know&rdquo;</b>: one enum instead of four Booleans.',
            'Lesson 4.6 gave NPay a SendPaymentUseCase. Now: while a payment is in flight, what does the screen show? What if it fails, if the user taps Confirm twice, or leaves before it finishes? We replace loose Boolean flags with an explicit state machine, connect it to the review sheet, and then test the hard cases for real: cancellation after the money moved, and results that arrive after the user has started over.')
outcomes_slide('4.7', [("diff", "Replace Boolean flags with an enum state"),
                       ("decision", "Define legal transitions and block duplicates"),
                       ("clock", "Explain what await does, and doesn&rsquo;t"),
                       ("phone", "Render every state with a switch"),
                       ("shield", "Tell cancellation, failure and unknown apart"),
                       ("key", "Tie each result to its own submission")])
where_slide('4.7', 'Today: the payment&rsquo;s lifecycle as state', (),
            '4.6: SendPaymentUseCase; Confirm submits the reviewed command.',
            'PaymentUIState: idle, submitting, success, failure, unknown.',
            'Last time the business operation got its own use case. Today the screen gets an honest model of that operation&rsquo;s progress. The text came in three pieces; the third continues from Section 15.',
            'Four Booleans.')

# ================================================================== Part 1 (1, 2, 3)
divider(1, "From flags to an enum", "Make contradictions unrepresentable", 'One value, one state.', 'The flags.')
FLAGS = """var isLoading = false
var isSuccess = false
var hasError = false
var isProcessing = false

// One of 16 combinations:
isLoading = true
isSuccess = true
hasError = true"""
ENUM = """enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
}"""
S.append(slide("Part 1 &middot; Booleans, then an enum (sections 1&ndash;3)", "2&#8308; = 16 combinations, most of them nonsense", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Four independent flags", FLAGS, "font-size:13px")}
        {card("Loading, successful or failed?", ul("Representable, contradictory"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("One enum, with associated values", ENUM, "font-size:13px")}</div>
        <div class="step">{card("Why better", ul("Exactly one case at a time", "Success carries the record; failure the message", "Enums from Unit 1"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Imagine a ViewModel with isLoading, isSuccess, hasError and isProcessing: four independent Booleans, two to the fourth, sixteen combinations, and most make no sense. Loading, successful and failed all at once: is NPay loading, successful or failed? The state is contradictory, yet perfectly representable. The text&rsquo;s interactive toggles showed this; the arithmetic is enough.'),
                  ('SAY', 'Click: instead, one enum: idle, validating, submitting, success, failure. NPay can be in exactly one of these at a time; you cannot set submitting and success simultaneously in one enum value. Section 3 adds associated values: success carries the PaymentRecord, failure carries the message.'),
                  ('SAY', 'Click: an enum with associated values represents a state machine far more precisely than loosely related flags. This is Unit 1&rsquo;s enums, put to work.'),
                  ('CONNECT', 'The machine itself.'))))

# ================================================================== Part 2 (4, 5, 6, 7)
divider(2, "The state machine", "States and the transitions between them", 'And no second submission while busy.', 'The lifecycle.')
P = []
P.append(box(0, 70, 190, 56, "Idle", "waiting", '1', '', ''))
P.append(wire('M191 98H228' + head(228, 98, 'r')))
P.append(box(230, 70, 210, 56, "Validating", "command, policy", '2', '', ''))
P.append(wire('M441 98H478' + head(478, 98, 'r')))
P.append(box(480, 70, 210, 56, "Submitting", "awaiting the operation", '3', '', ''))
P.append(wire('M691 90L760 35' + head(760, 35, 'r')))
P.append(wire('M691 106L760 161' + head(760, 161, 'r')))
P.append(box(762, 6, 240, 56, "Success", "PaymentRecord", '4+', '', 'check'))
P.append(box(762, 134, 240, 56, "Failure", "error information", '4+', '', 'cross'))
TR = [("Idle", "Confirm payment", "Validating"), ("Validating", "Passes / fails", "Submitting / Failure"), ("Submitting", "Succeeds / fails", "Success / Failure"),
      ("Failure", "Retry or edit", "Idle / Validating"), ("Success", "New payment", "Idle")]
S.append(slide("Part 2 &middot; The payment lifecycle and its transitions (sections 4&ndash;6)", "A state machine is states plus allowed moves", f"""  <div class="body">
    {cues(4)}
    {svg('0 0 1010 196', 'Idle, validating, submitting, then success or failure', 'sm', P, 'max-height:200px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:20px;align-items:start">
      <div class="step">{tbl(["Current", "Event", "Next"], TR, 'tbl compact')}</div>
      <div class="rule step" data-label="Scope">{ul("The submission flow only", "Form, sheet, navigation: separate state")}</div>
    </div>
  </div>""", notes(('SAY', 'The lifecycle. Click through: idle, waiting for the user; validating the command and policy; submitting, awaiting the operation; and then one of two outcomes: success with a PaymentRecord, or failure with error information. The text also had an interactive simulator stepping through these legal transitions; this diagram is the same machine.'),
                  ('SAY', 'Click: a state machine is not just an enum; it defines which transitions are allowed. Confirm moves idle to validating; validation passes to submitting or fails; the operation succeeds or fails; from failure the user retries or edits; after success a new payment returns to idle. Bugs come from unexpected transitions, like starting a second submission while one is processing.'),
                  ('SAY', 'Click: and the nuance: this models the submission flow. Form editing, the review sheet and payment execution are related but distinct concerns; don&rsquo;t force every UI detail into one enormous enum. Part 7 returns to this.'),
                  ('CONNECT', 'Block the unexpected transition.'))))

BUSY = """extension PaymentUIState {
    var isBusy: Bool {
        switch self {
        case .validating, .submitting:
            true
        default:
            false
        }
    }
}

guard !state.isBusy else { return }    // ViewModel

.disabled(viewModel.state.isBusy)      // SwiftUI"""
S.append(slide("Part 2 &middot; Prevent duplicate submission (section 7)", "isBusy: one rule, used twice", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 7", BUSY, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console(MAC + ": Confirm twice while busy", ["one call: success", "the other: failure(\"A payment is already processing\")", "payments recorded: <b>1</b>"], 12)}</div>
        <div class="step">{card("Two guards", ul("The ViewModel rejects the second call", "The view disables the button"))}</div>
        <div class="warn step" data-label="Not idempotency">{ul("Local UI workflow only", "The backend needs a request identifier")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A computed isBusy is true while validating or submitting. The ViewModel uses it to reject another submission; SwiftUI uses it to disable the button.'),
                  ('SAY', 'Click: we tested the ViewModel guard on the Mac: two submissions at once, with a repository that takes a moment. One succeeded; the other returned "A payment is already processing", Section 20&rsquo;s wording; one payment recorded. Click: two guards, one rule.'),
                  ('SAY', 'Click: but this protects the local UI workflow against overlapping submissions. It does not guarantee financial idempotency, which a real backend must enforce with an authoritative request identifier, Lesson 4.5&rsquo;s point.'),
                  ('CONNECT', 'Build the ViewModel around the state.'))))

# ================================================================== Part 3 (8, 9, 10)
divider(3, "State in the ViewModel", "One property for the lifecycle", 'And what await really does.', 'The ViewModel.')
VM = """private(set) var state: PaymentUIState = .idle

func submit(_ command: SendPaymentCommand) async {
    guard !state.isBusy else { return }

    state = .validating
    // Command value objects were validated at creation.
    state = .submitting

    do {
        let record = try await sendPayment.execute(command)
        recipient = ""; amountText = ""
        state = .success(record)
    } catch PaymentDomainError.insufficientBalance {
        state = .failure("Insufficient balance")
    } catch PaymentDomainError.limitExceeded {
        state = .failure("Demo payment limit exceeded")
    } catch {
        state = .failure("Unable to complete payment")
    }
}

func reset() {
    guard !state.isBusy else { return }
    state = .idle
}"""
S.append(slide("Part 3 &middot; PaymentViewModel with explicit UI state (section 8)", "isSubmitting + errorMessage + successRecord &rarr; state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("PaymentViewModel (condensed)", VM, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What changed", ul("One enum replaces three properties", "<code>private(set)</code>: only the ViewModel moves it"))}
        <div class="step">{console(MAC + ", 200 ms latency (ours)", ["50 ms in: submitting, isBusy true", "states a view observed:", "&ensp;[submitting, success(150050)]"], 11.5)}</div>
        <div class="rule step" data-label="Nuance">{ul("<code>.validating</code> is never seen: same turn", "Don&rsquo;t add delays to show it")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The core implementation: the ViewModel keeps recipient and amountText, and a private(set) state starting at idle. submit refuses if busy, sets validating, then submitting, awaits the use case, and moves to success with the record or to failure with a message for insufficient balance, the limit, or anything else. reset returns to idle unless busy. Previously we had isSubmitting, errorMessage and a success record; now one enum.'),
                  ('SAY', 'Click: we recorded what a view could actually observe, using Observation&rsquo;s change tracking, with a repository that takes 200 milliseconds. Fifty milliseconds in, the state is submitting and busy. The states observed: submitting, then success. Click: validating never appeared: it is set and replaced in the same synchronous turn, before any view update. The text predicts exactly this, and says not to insert artificial delays just to make every state visible.'),
                  ('CONNECT', 'Why can SwiftUI show submitting at all?'))))

P = []
AS = [("phone", "Main actor", "state = .submitting"), ("clock", "await execute()", "may suspend here"), ("db", "Repository actor", "isolated account state"),
      ("check", "Result", "record or thrown error"), ("phone", "Main actor", "success or failure"), ("eye", "SwiftUI", "shows the new state")]
for i, (ic, t, sub) in enumerate(AS):
    x = i * 188
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}' if i < 5 else '6+', ''))
    if i < 5:
        P.append(wire(f'M{x + 173} 60H{x + 186}' + head(x + 186, 60, 'r')))
S.append(slide("Part 3 &middot; async/await and UI state (sections 9&ndash;10)", "await is a suspension point, not a thread", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1120 120', 'Main actor sets submitting, awaits, the repository actor works, the result returns, the main actor sets the outcome, SwiftUI shows it', 'async', P, 'max-height:126px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("While suspended", ul("The main actor runs other work", "SwiftUI can render <code>.submitting</code>"))}</div>
      <div class="warn step" data-label="Not a background thread">{ul("await doesn&rsquo;t pick a thread", "Actor isolation and the callee do")}</div>
    </div>
  </div>""", notes(('SAY', 'Click through the asynchronous lifecycle: on the main actor, state becomes submitting; await execute is a possible suspension point; the repository actor processes its isolated account state; the result, a record or a thrown error, comes back; on the main actor, state becomes success or failure; SwiftUI displays the new state.'),
                  ('SAY', 'Click: while the operation is suspended, the main actor can run other eligible work, including SwiftUI rendering the submitting state. That is why the ProgressView can appear at all.'),
                  ('SAY', 'Click: does await create a background thread? No. async/await is a concurrency abstraction, not a promise to run on a particular thread; where code runs depends on actor isolation and on the operation called. Lesson 3.11 showed the flip side: synchronous work on the main actor delivered no frames.'),
                  ('CONNECT', 'Render the state.'))))

# ================================================================== Part 4 (11, 12, 13, 14)
divider(4, "Rendering and the review sheet", "Switch over the state", 'Busy, failed, succeeded: in NPay.', 'The switch.')
SW = """@ViewBuilder
private var statusContent: some View {
    switch viewModel.state {
    case .idle:
        EmptyView()
    case .validating:
        Text("Validating payment...")
    case .submitting:
        ProgressView("Processing demo payment...")
    case .success:
        Label("Payment recorded",
              systemImage: "checkmark.circle.fill")
            .foregroundStyle(.green)
    case .failure(let message):
        Text(message)
            .foregroundStyle(.red)
    case .statusUnknown:
        ContentUnavailableView(/* section 17 */)
    }
}"""
S.append(slide("Part 4 &middot; Render UI from the state; keep the sheet while busy (sections 11&ndash;12)", "The compiler checks every case", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 180px minmax(0,.7fr);gap:18px;align-items:start">
      {code("Review sheet&rsquo;s statusContent (in NPay)", SW, "font-size:10.5px")}
      <div class="step">{PHONE("img/slow.png", "Submitting (3 s latency)", 180)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator, 0.8 s after Confirm", ["Processing demo payment...", "Confirm disabled", "swipe-to-dismiss blocked", "Edit Details disabled (ours)"], 11)}</div>
        <div class="warn step" data-label="Found">{ul("interactiveDismissDisabled stops the swipe only", "Edit Details still dismissed: we disabled it")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The view switches over the state: nothing when idle, text while validating, a ProgressView while submitting, a green label on success, the red message on failure; we added the statusUnknown case from Section 17. A switch makes the compiler check that every case is handled: add a state later, and Swift points at every switch that needs updating. In NPay this lives in the review sheet, flagged as ours.'),
                  ('SAY', 'Click: Section 12: keep the review sheet visible while busy, with interactiveDismissDisabled tied to isBusy. To see the submitting state, our test run added three seconds of latency through a debug-only hook; no delay exists in the app. Click: 0.8 seconds after Confirm: the spinner and "Processing demo payment...", Confirm disabled, and the sheet refused a swipe-down.'),
                  ('SAY', 'Click: what the run found: interactiveDismissDisabled only stops the swipe. The sheet&rsquo;s own Edit Details button could still dismiss it mid-payment, so we disabled it while busy too. As the text says, all this improves the experience; it is not a transaction guarantee.'),
                  ('CONNECT', 'Success, and navigation.'))))

NAVC = """Task {
    let result = await viewModel.submit(request.command)

    switch result {
    case .success(let record):
        pendingSuccessID = record.id
        review = nil              // then onDismiss navigates
    case .failure:
        break                     // sheet stays; it shows the error
    case .statusUnknown:
        break                     // status check, never a guess
    }
}"""
OUTC = [("₹1,500.50", "sheet closes; onDismiss &rarr; Payment Recorded; ₹23,499.50"),
        ("₹20,000; ₹10,000 left during review", "sheet <b>stays</b>: &ldquo;Insufficient balance&rdquo;; no route; Edit Details keeps the draft")]
S.append(slide("Part 4 &middot; Success navigates; failure stays (sections 13&ndash;14, 21)", "Only a successful result may navigate", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 170px;gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Confirm, in NPay (section 21)", NAVC, "font-size:11px")}
        <div class="step">{tbl(["Simulator", "Result"], OUTC, 'tbl compact')}</div>
      </div>
      <div class="step">{PHONE("img/stale.png", "Failure: the sheet stays", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'We want submitting, then success, then dismiss the review, then navigate. Section 13 read the shared state after the await; Section 21 improves the contract: submit returns this submission&rsquo;s own result. On success: remember the record&rsquo;s ID and dismiss; the sheet&rsquo;s onDismiss navigates, so the modal dismissal and the push are coordinated, as in Lesson 3.4. On failure: stay. On unknown: a status check, never a guess.'),
                  ('SAY', 'Click: run in NPay. ₹1,500.50: the sheet closed, onDismiss navigated, Payment Recorded, ₹23,499.50. A payment refused because the balance dropped during review: the sheet stayed open showing "Insufficient balance", no success route, and Edit Details returned to the form with the draft kept. Click: the screenshot. A button tap does not mean a payment succeeded; only a successful operation result does.'),
                  ('CONNECT', 'That message almost didn&rsquo;t appear.'))))

S.append(slide("Part 4 &middot; What happens if the payment fails? (section 14)", "The error must be mapped to reach the user", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console(MAC + " and 4.6&rsquo;s use case: ₹500 from ₹100", ["repository throws AccountRepositoryError.insufficientBalance", "use case passes it through", "ViewModel: <b>failure(\"Unable to complete demo payment\")</b>"], 11.5)}
        <div class="step">{console("Over the policy limit", ["failure(\"Demo payment limit exceeded\")"], 11.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why", ul("The ViewModel catches <code>PaymentDomainError</code>", "The repository throws its own error"))}</div>
        <div class="step">{code("Our fix, in SendPaymentUseCase", "} catch AccountRepositoryError.insufficientBalance {\n    throw PaymentDomainError.insufficientBalance\n}", "font-size:11.5px")}</div>
        <div class="rule step" data-label="Section 14">{ul("&ldquo;The use case or service maps the failure&rdquo;")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 14 says: the repository throws insufficientBalance, the use case or service maps it, and the ViewModel shows "Insufficient balance". We ran the text&rsquo;s ViewModel on Lesson 4.6&rsquo;s use case: ₹500 from ₹100. The result was "Unable to complete demo payment". Click: the policy limit, thrown by the use case itself as PaymentDomainError, did produce its specific message.'),
                  ('SAY', 'Click: why: the ViewModel catches PaymentDomainError.insufficientBalance, but the repository throws its own AccountRepositoryError, and 4.6&rsquo;s use case passes it through untranslated. Lesson 4.6&rsquo;s concurrency run showed the same gap.'),
                  ('SAY', 'Click: our fix, flagged: the use case translates the repository&rsquo;s three errors into domain errors. Click: that is what Section 14 assumes, and with it NPay&rsquo;s sheet shows "Insufficient balance", as on the last slide.'),
                  ('CONNECT', 'Now the hard cases: cancellation.'))))

# ================================================================== Part 5 (15, 16, 17)
divider(5, "Cancellation and unknown outcomes", "Cancelling a task isn&rsquo;t reversing a payment", 'And failure isn&rsquo;t the only bad news.', 'Cancellation.')
CANC = ["cancel before the payment is recorded:", "&ensp;result failure(\"Unable to complete demo payment\")", "&ensp;repository: 0 payments, 2500000", "",
        "cancel after it is recorded, before the reply:", "&ensp;result <b>failure</b>(\"Unable to complete demo payment\")", "&ensp;repository: <b>1 payment</b>, 2349950"]
S.append(slide("Part 5 &middot; Cancellation (section 15)", "The task was cancelled; the money had moved", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {console(MAC + ": Task.cancel() 50 ms in (ours)", CANC, 11.5)}
        <p class="small muted" style="margin:0">Latency before or after recording stands in for the network.</p>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Not interchangeable", ul("Cancelling local UI work", "Cancelling a network request", "Cancelling or reversing a payment", "An unknown status to reconcile"))}</div>
        <div class="warn step" data-label="Principle">{ul("Task cancellation is not transaction reversal")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The user starts a payment and switches to History before it finishes. Should the operation be cancelled? We tested cancellation on the Mac, ours: the task wrapping submit is cancelled fifty milliseconds in, with a repository whose delay comes either before recording, like a request still travelling, or after, like a reply on its way back.'),
                  ('SAY', 'Cancelled before recording: the ViewModel said failure, and indeed nothing was recorded. Cancelled after recording: the ViewModel said failure, yet the repository holds one payment and the balance fell to 2,349,950. The screen says failed; the money moved.'),
                  ('SAY', 'Click: the text&rsquo;s distinction: cancelling local UI work, cancelling a network request, actually cancelling or reversing a payment, and an unknown status needing reconciliation are not interchangeable. Click: task cancellation is not transaction reversal. The app may need to query the payment status before deciding to retry or show failure.'),
                  ('CONNECT', 'So the state needs another case.'))))

UNK = """enum PaymentUIState {
    case idle
    case validating
    case submitting
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown
    // isBusy as before
}

case .statusUnknown:
    ContentUnavailableView {
        Label("Payment status unavailable",
              systemImage: "questionmark.circle")
    } description: {
        Text("Check transaction status before retrying.")
    }"""
S.append(slide("Part 5 &middot; Model unknown outcomes (sections 16&ndash;17)", "statusUnknown: not success, not failure", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Section 17", UNK, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("When", ul("The server recorded it; the reply was lost", "The app can&rsquo;t know which"))}
        <div class="step">{card("Our cancelled-after-recording run", ul("Should have been statusUnknown", "It said failure: retrying could pay twice"))}</div>
        <div class="rule step" data-label="Real networking">{ul("Classify errors carefully (Unit 5)", "Ambiguous &ne; definitive failure")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'For a real payment app we need a state for an uncertain outcome: statusUnknown. It means the app cannot currently determine whether the operation completed; it does not mean the payment failed. The view renders it as "Payment status unavailable: check transaction status before retrying."'),
                  ('SAY', 'The scenario: NPay sends a payment, the server records it, the connection drops before the response arrives. The app cannot safely conclude the payment failed, and blindly retrying could duplicate it unless the backend enforces idempotency.'),
                  ('SAY', 'Click: our cancelled-after-recording run is exactly that case, and the ViewModel reported failure. Click: Section 20&rsquo;s local version never returns statusUnknown, because the in-memory repository gives definitive answers; with networking in Unit 5, transport failures must be classified carefully, and an ambiguous one must not become a definitive failure.'),
                  ('CONNECT', 'Results that arrive late.'))))

# ================================================================== Part 6 (18, 19, 20, 21)
divider(6, "Stale results", "Whose result is this?", 'Request identifiers and a result-returning submit.', 'The problem.')
STL = """private var activeSubmissionID: UUID?

let submissionID = UUID()
activeSubmissionID = submissionID

// ... after the await:
guard activeSubmissionID == submissionID else {
    return
}"""
SR = ["payment A starts; the user starts over 50 ms later; A finishes:", "&ensp;without the check: new flow shows <b>success(150050)</b>", "&ensp;with the check:&ensp;&ensp;&ensp;&ensp;new flow shows idle", "&ensp;repository: A recorded either way"]
S.append(slide("Part 6 &middot; Stale asynchronous results (sections 18&ndash;19)", "Associate each result with its submission", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 18", STL, "font-size:12.5px")}
        <div class="step">{console("Mac (ours; startOver() clears the active ID)", SR, 11)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("It protects", ul("The presentation from stale results"))}</div>
        <div class="warn step" data-label="It doesn&rsquo;t">{ul("Cancel or reverse payment A", "Replace a server idempotency key")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Payment A is in flight; the user navigates away and starts a different payment flow; then A finishes. Should A&rsquo;s result update the new screen? Not necessarily. Section 18 tracks an activeSubmissionID: each submission gets a fresh UUID, and after the await the result is applied only if its ID is still the active one.'),
                  ('SAY', 'Click: we ran it, ours: payment A starts, fifty milliseconds later the user starts over, which clears the active ID, then A completes. Without the check, the brand-new flow suddenly shows success for payment A. With the check, the new flow stays idle. And A was recorded either way.'),
                  ('SAY', 'Click: so it protects the presentation layer against stale results. Click: it does not cancel or reverse the payment, and a UI request ID is not a server-enforced idempotency key, though a production design may relate them. The text&rsquo;s six-step walkthrough was shared at step one; this run plays it out.'),
                  ('CONNECT', 'A safer submit contract.'))))

RES = """enum PaymentSubmissionResult {
    case success(PaymentRecord)
    case failure(String)
    case statusUnknown
}

func submit(_ command: SendPaymentCommand)
    async -> PaymentSubmissionResult {
    guard !state.isBusy else {
        return .failure("A payment is already processing")
    }
    state = .validating
    state = .submitting
    do {
        let record = try await sendPayment.execute(command)
        state = .success(record)
        recipient = ""; amountText = ""
        return .success(record)
    } catch PaymentDomainError.insufficientBalance {
        state = .failure("Insufficient balance")
        return .failure("Insufficient balance")
    } // ... limitExceeded, then a generic failure
}"""
S.append(slide("Part 6 &middot; A safer submission contract (sections 20&ndash;21)", "Return the result; still publish the state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("Section 20 (condensed)", RES, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Before", ul("submit() returned Void", "The caller read shared state after the await"))}
        <div class="step">{card("Now", ul("The caller gets this call&rsquo;s result", "Views still render <code>state</code>"))}</div>
        <div class="rule step" data-label="In NPay">{ul("Confirm switches on the result (Part 4)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 20 improves the contract. The earlier submit returned nothing, so the caller had to inspect mutable state after awaiting it, and that state might already belong to something else. Now submit returns a PaymentSubmissionResult: success with the record, failure with a message, or statusUnknown, and still sets state for rendering.'),
                  ('SAY', 'Click: the caller receives the result of exactly the command it submitted; the views keep rendering the published state. Two complementary responsibilities. Click: NPay&rsquo;s Confirm already switches on this result, as Part 4 showed. For the local demo the repository gives definitive answers, so no unknown outcome is invented for ordinary validation errors.'),
                  ('CONNECT', 'Test it.'))))

# ================================================================== Part 7 (22, 23)
divider(7, "Testing and scope", "Test the transitions; keep concerns apart", 'And not one enormous enum.', 'The test.')
TS = [("Initial ViewModel", "idle"), ("Submission starts", "submitting"), ("Repository succeeds", "success(record)"), ("Repository rejects", "failure(message)"), ("Unknown remote outcome", "statusUnknown")]
S.append(slide("Part 7 &middot; Testing the state machine (section 22)", "The test passed; read what it checks", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["Scenario", "Expected state"], TS, 'tbl compact')}
        <div class="step">{console("Section 22, Mac (₹500 from ₹100)", ["Correct failure result", "Correct UI state"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("It checks", ul("<code>case .failure</code>, any message", "No receipt, no navigation"))}</div>
        <div class="step">{card("It missed", ul("The message was the generic one (Part 4)", "Assert the message too"))}</div>
        <div class="rule step" data-label="Lesson 4.9">{ul("One test per transition, with exact values")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s table of transitions to verify: idle at first, submitting during, success with the record, failure with a message, statusUnknown for a genuinely unknown remote outcome. Click: Section 22&rsquo;s failure test: ₹500 from ₹100. It printed "Correct failure result" and "Correct UI state": the ViewModel reports failure and fabricates no receipt.'),
                  ('SAY', 'Click: but notice what it checks: case .failure, with any message. Click: on Lesson 4.6&rsquo;s use case the message was the generic "Unable to complete demo payment", the mapping gap from Part 4, and the test still passed. A test that asserts the exact message would have caught it. Click: Lesson 4.9 writes one test per transition, with exact values.'),
                  ('CONNECT', 'Should everything go in the enum?'))))

P = []
P.append(box(330, 0, 360, 54, "Payment feature", "", None, 'solid', 'layers'))
for i, (t, sub, ic) in enumerate([("Form state", "recipient, amount", "frame"), ("Submission state", "idle, busy, result", "clock"), ("Presentation state", "review sheet", "phone"), ("Navigation state", "success route", "decision")]):
    x = i * 260
    P.append(wire(f'M510 55L{x + 120} 98' + head(x + 120, 98, 'd')))
    P.append(box(x, 100, 240, 56, t, sub, '1+' if i == 1 else None, '', ic))
S.append(slide("Part 7 &middot; Why not one enormous enum? (section 23)", "Separate concerns; impossible combinations within each", f"""  <div class="body">
    {cues(1)}
    {svg('0 0 1020 160', 'Payment feature: form, submission, presentation and navigation state', 'split', P, 'max-height:170px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Elsewhere already", ul("Focus: @FocusState (2.11)", "Sheet: <code>review</code>; route: NPayRouter", "Draft: the ViewModel; appearance: preferences"))}</div>
      <div class="rule step" data-label="Goal">{ul("Make invalid combinations hard", "Not the fewest variables")}</div>
    </div>
  </div>""", notes(('SAY', 'PaymentUIState models submission status. NPay also has text-field focus, review-sheet visibility, navigation paths, appearance preferences and the payment draft. Combine them into one enum? No: that would produce an overly complex state machine. Click: the payment feature has form state, submission state, in teal, presentation state and navigation state, each with its own owner.'),
                  ('SAY', 'Click: and they already live in the right places: focus in @FocusState, the sheet in the screen&rsquo;s review property, the route in NPayRouter, the draft in the ViewModel, appearance in preferences, Lesson 3.12&rsquo;s ownership table. Click: the goal is not to minimize state variables at all costs; it is to make invalid combinations hard to represent while keeping independent concerns separate.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.7', (), [("diff", "One enum, one lifecycle", "idle, validating, submitting, success, failure, unknown"),
                     ("shield", "Results belong to submissions", "return the result; check the active ID"),
                     ("clock", "Cancelled &ne; reversed &ne; failed", "cancelled after recording: the money moved")],
          'Three things to remember. Model the submission lifecycle as one enum with associated values, guard it with isBusy, and render it with an exhaustive switch; four Booleans allow sixteen states, most of them nonsense. Tie every asynchronous result to the submission that produced it: return it from submit, and ignore results whose submission is no longer active. And keep cancellation, failure and unknown apart: our cancelled task reported failure after the money had already moved, which is exactly what statusUnknown and status checks exist for.')

review_divider(11)
review([("diff", "Choose one", "Why use an enum for payment lifecycle state?",
         "Why use an enum for payment lifecycle state?<br>A. To create more threads<br>B. To represent mutually exclusive states<br>C. To replace the repository", "B",
         "One case at a time; 16 Boolean combinations gone.",
         "Adding flags for every new situation.", "Most pick B.", None),
        ("clock", "Question", "Does await guarantee that code runs on a background thread?",
         "Does <code>await</code> guarantee that code runs on a background thread?", "No",
         "It marks a suspension point; isolation decides where code runs.",
         "Equating async with background.", "Some say yes.", None),
        ("shield", "Question", "Does cancelling a Swift task necessarily reverse a payment?",
         "Does canceling a Swift task necessarily reverse a payment?", "No",
         "Cancelled after recording: 1 payment, 2349950.",
         "Treating cancellation as undo.", "Some say yes.", None),
        ("eye", "Choose one", "What does statusUnknown represent?",
         "What does <code>statusUnknown</code> represent?<br>A. Definitive payment failure<br>B. The app can&rsquo;t determine the authoritative outcome<br>C. Guaranteed success", "B",
         "Check status before retrying.",
         "Reporting failure when unsure.", "Most pick B.", None),
        ("key", "Choose one", "Why return PaymentSubmissionResult from submit()?",
         "Why return <code>PaymentSubmissionResult</code> from <code>submit()</code>?<br>A. To persist data automatically<br>B. To replace SwiftUI rendering<br>C. To associate the result with that invocation", "C",
         "No reading shared state after the await.",
         "Reading mutable state that may have moved on.", "Most pick C.", None),
        ("decision", "Question", "Should a failed payment navigate to the success screen?",
         "Should a failed payment navigate to the success screen?", "No",
         "The sheet stayed: &ldquo;Insufficient balance&rdquo;, no route.",
         "Navigating on tap instead of on result.", "Most say no.", None),
        ("link", "Question", "Does a UI submission guard guarantee server-side idempotency?",
         "Does a UI submission guard guarantee server-side idempotency?", "No",
         "isBusy stops a double tap here, not a retry elsewhere.",
         "Confusing local guards with the server.", "Most say no.", None),
        ("layers", "Question", "Should form focus and navigation paths be forced into PaymentUIState?",
         "Should form focus and navigation paths be forced into <code>PaymentUIState</code>?", "No",
         "Separate concerns, separate owners.",
         "One enum for everything.", "Most say no.", None),
        ("phone", "Predict the result", "state = .validating; state = .submitting in one turn: which does a view see?",
         "<code>submit</code> sets <code>.validating</code> then <code>.submitting</code> with no await between. Which states can a view observe before the result?<br>A. Both<br>B. Only submitting<br>C. Neither", "B",
         "Observed: [submitting, success(150050)].",
         "Expecting every assignment to render.", "Many pick A.", None),
        ("check", "Predict the result", "₹500 from ₹100 on 4.6's use case: the message?",
         "The text&rsquo;s ViewModel on Lesson 4.6&rsquo;s use case submits ₹500 against ₹100. The failure message is&hellip;<br>A. Insufficient balance<br>B. Unable to complete demo payment<br>C. Demo payment limit exceeded", "B",
         "The repository&rsquo;s error wasn&rsquo;t mapped.",
         "Assuming errors translate themselves.", "Many pick A.", None),
        ("file", "Choose one", "From 4.6: what should Confirm submit?",
         "From Lesson 4.6: what should the review sheet&rsquo;s Confirm submit?<br>A. The current form fields<br>B. The immutable command the user reviewed<br>C. The last successful payment", "B",
         "The reviewed command paid 150050, not 200000.",
         "Re-reading the form.", "Most pick B.", "Spaced review from Lesson 4.6.")])

S.append(next_slide('4.7', [("4.8", "Modular project structure", "the payment feature&rsquo;s files, organized"),
                            ("4.9", "Architecture testing", "one test per transition, with exact messages"),
                            ("Unit 5", "Networking", "classifying errors; statusUnknown for real"),
                            ("Unit 8", "Concurrency", "task lifetime, cancellation, structured concurrency")],
                    'Lesson 4.8 organizes the growing payment feature into a modular structure. 4.9 tests every transition with exact values. Unit 5 brings networks, where statusUnknown stops being hypothetical, and Unit 8 covers task lifetime and structured cancellation.'))

S.append(lab_slide('4.7', "PaymentUIState", "An honest model of the payment&rsquo;s progress.",
                   ["Add PaymentUIState with isBusy and statusUnknown.",
                    "Replace isSubmitting and errorMessage with state.",
                    "Return PaymentSubmissionResult from submit.",
                    "Render statusContent in the review sheet.",
                    "Block dismissal while busy; stay open on failure.",
                    "Test a failure, asserting the message."],
                   "", 'Expected, as in our run: success navigates; a refused payment keeps the sheet with &ldquo;Insufficient balance&rdquo; once the use case maps the repository error; a double Confirm records one payment.',
                   side=f'<div>{card("You hand in", ul("Your state enum and ViewModel", "Screens: submitting and failure", "A test that checks the exact message"))}</div>'))

end_slide('4.7', 'UI State Modeling &amp;<br>Async Payment Lifecycle', 'Lesson 4.8 &mdash; Modular Project Structure',
          'You can now model a lifecycle with an enum, guard and render it, return results tied to their submission, and keep cancellation, failure and unknown outcomes apart.',
          'Next, Lesson 4.8: modular project structure for NPay&rsquo;s features.')

write_deck(OUT47, '4.7', 'UI State Modeling &amp; Async Payment Lifecycle', 'UI State Modeling &amp; Async Payment Lifecycle')
