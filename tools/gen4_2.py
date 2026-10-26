"""Generates decks/unit-4/lesson-4.2/index.html from the Lesson 4.2 text (MVVM Internals: Building NPay's First ViewModel;
two parts, Sections 1-26; Part 2 restarts at Section 16). Evidence: tools/sim4_2 (the text's MVVM lab, isValid vs the
validator, the incorrect private store, the stale review, initializer and deinit logs with live-instance counts,
_printChanges, NPay refactored around PaymentViewModel and PaymentsFeatureRoot) and a Mac retain-cycle run."""
import html, os, re, sys
OUT42 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit4.py')).read())   # Unit 04 lesson list + shared helpers

title_slide('4.2', 'MVVM Internals:<br>PaymentViewModel',
            'Move the payment screen&rsquo;s <b>state and behaviour</b> into a ViewModel, and watch how SwiftUI keeps it alive.',
            'Lesson 4.1 extracted payment validation into PaymentValidator. Today we introduce one of the most important ideas in professional iOS development, the ViewModel. We build PaymentViewModel step by step, connect it to SwiftUI and to NPay&rsquo;s store, split payment into prepare and confirm, and then investigate what really happens to it in memory: when it is created, when it is kept, when it goes away.')
outcomes_slide('4.2', [("layers", "Say what belongs in a ViewModel, and what doesn&rsquo;t"),
                       ("eye", "Make a ViewModel observable and bind to it"),
                       ("key", "Inject the shared store; never create a second one"),
                       ("check", "Prepare, review and confirm in two stages"),
                       ("clock", "Explain ViewModel lifetime under @State"),
                       ("link", "Avoid reference cycles in ViewModels")])
where_slide('4.2', 'Today: NPay&rsquo;s first ViewModel', (),
            '4.1: PaymentValidator, extracted and tested.',
            'PaymentViewModel: state, ownership, lifetime.',
            'Last time we pulled the payment rules out of the view into PaymentValidator and proved NPay still behaved the same. Today the screen&rsquo;s state and behaviour move into a PaymentViewModel. The text arrived in two parts; the second restarts at Section 16.',
            'The problem.')

# ================================================================== Part 1 (1, 2)
divider(1, "Why a ViewModel", "The screen is doing too much", 'Presentation and behaviour, separated.', 'The problem.')
P = []
P.append('<text x="170" y="16" text-anchor="middle">Before</text><text x="580" y="16" text-anchor="middle">After</text>')
P.append(box(0, 30, 340, 60, "PaymentsScreen", "UI + validation + actions + state", '1', 'alert', 'phone'))
P.append(wire('M170 91V138' + head(170, 138, 'd')))
P.append(box(0, 140, 340, 54, "NPayStore", "", None, '', 'db'))
P.append(box(410, 30, 340, 54, "PaymentsScreen", "presentation", None, '', 'phone'))
P.append(wire('M580 85V108' + head(580, 108, 'd')))
P.append(box(410, 110, 340, 54, "PaymentViewModel", "screen state + behaviour", '2+', '', 'layers'))
P.append(wire('M580 165V188' + head(580, 188, 'd')))
P.append(box(410, 190, 340, 54, "PaymentValidator + NPayStore", "", None, '', 'check'))
BEF = [("Lines", "160", "120 (+ ViewModel 117)"), ("State properties", "6", "4 (focus, sheet, success, discard)"), ("Uses of the store", "14", "0")]
S.append(slide("Part 1 &middot; Our engineering problem (section 1)", "PaymentsScreen: UI, rules, actions and state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      <div>{cues(2)}{svg('0 0 750 250', 'Before: PaymentsScreen does everything over NPayStore. After: PaymentsScreen, PaymentViewModel, PaymentValidator and NPayStore', 'ba', P, 'max-height:270px')}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("PaymentsScreen today", ul("Reads the draft; validates", "Presents review; calls the store", "Handles results; navigates"))}
        <div class="step">{tbl(["PaymentsScreen", "3.12", "After this lesson"], BEF)}
          <p class="small muted" style="margin:6px 0 0">Counted in our code before and after the refactoring.</p></div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Our PaymentsScreen reads the payment draft, validates the form, presents the review sheet, calls NPayStore, handles payment results and coordinates navigation. Tomorrow add transaction limits, loading indicators, network errors and biometric verification, and the view keeps growing. Click: before, in orange: one view doing UI, validation, actions and state on top of the store.'),
                  ('SAY', 'Click: after: PaymentsScreen keeps presentation; a PaymentViewModel takes the screen&rsquo;s state and behaviour, and it talks to PaymentValidator and NPayStore. Click: measured in our own code: the screen goes from a hundred and sixty lines to a hundred and twenty, from six state properties to four, and from fourteen uses of the store to none. The ViewModel is a hundred and seventeen lines, but they are now in one place, testable without a view.'),
                  ('CONNECT', 'So what exactly is a ViewModel?'))))

VMR = [("TextField layout", "Editable payment data"), ("Buttons and colours", "Validation state"), ("Review sheet presentation", "Preparing payment requests"),
       ("Keyboard focus", "Submission coordination"), ("Navigation presentation", "Payment result"), ("Accessibility labels", "User-facing error state")]
API = """viewModel.recipient
viewModel.amountText
viewModel.isValid
viewModel.errorMessage
viewModel.submitPayment()"""
S.append(slide("Part 1 &middot; What exactly is a ViewModel? (section 2)", "State and behaviour for one screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.7fr) minmax(0,1.3fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("What it might expose", API, "font-size:14px")}
        <div class="step">{card("The view", ul("Reads its state", "Calls its methods"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["PaymentsScreen", "PaymentViewModel"], VMR)}</div>
        <div class="rule step" data-label="Not its job">{ul("Where buttons go, what colours they use")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A ViewModel is an object that prepares and manages the state and behaviour a particular screen or feature needs. For NPay it might expose the recipient, the amount text, whether the form is valid, an error message, and a submitPayment method. Click: the view does not need to know every validation rule; it reads the ViewModel&rsquo;s state and calls its methods.'),
                  ('SAY', 'Click: the text&rsquo;s split. The screen keeps TextField layout, buttons and colours, review sheet presentation, keyboard focus, navigation presentation and accessibility labels. The ViewModel takes editable payment data, validation state, preparing payment requests, submission coordination, the payment result and user-facing error state.'),
                  ('SAY', 'Click: the ViewModel does not decide where buttons are positioned or what colours they use; those remain presentation responsibilities.'),
                  ('CONNECT', 'Build one, starting with plain Swift.'))))

# ================================================================== Part 2 (3, 4)
divider(2, "A first ViewModel", "Plain Swift, then observable", 'A class, on the main actor, with @Observable.', 'Plain Swift.')
VM0 = """import Foundation

@MainActor
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""

    var isValid: Bool {
        !recipient.isEmpty && !amountText.isEmpty
    }
}"""
S.append(slide("Part 2 &middot; A ViewModel without SwiftUI (section 3)", "Ordinary Swift: properties and a computed property", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("PaymentViewModel.swift", VM0, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why a class?", ul("Stable reference identity while state changes"))}</div>
        <div class="step">{card("Why @MainActor?", ul("Its state feeds the UI", "Mutations coordinated with UI work"))}</div>
        <div class="warn step" data-label="Nuance">{ul("@MainActor doesn&rsquo;t make work fast", "Heavy synchronous work still blocks (3.11)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Create PaymentViewModel.swift. It is ordinary Swift: a recipient, an amount text, and a computed isValid that is true when both are non-empty.'),
                  ('SAY', 'Click: why a class? A ViewModel often needs a stable reference identity while its state changes: the screen keeps talking to the same object. Click: why @MainActor? Its state is consumed by the user interface; main-actor isolation coordinates those mutations safely with UI work.'),
                  ('SAY', 'Click: the nuance: @MainActor does not mean every operation is fast. Lesson 3.11 measured it: synchronous work on the main actor delivered zero frames while it ran.'),
                  ('CONNECT', 'What&rsquo;s missing for SwiftUI?'))))

VM1 = """import SwiftUI

@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""

    var isValid: Bool {
        !recipient.isEmpty && !amountText.isEmpty
    }
}"""
S.append(slide("Part 2 &middot; How will SwiftUI observe changes? (section 4)", "@Observable: one macro, generated machinery", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Add @Observable", VM1, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("@Observable", ul("A macro from the Observation framework", "Tracks property access and change"))}
        <div class="step">{card("Behind the scenes", ul("The compiler expands the type", "Not a runtime flag"))}</div>
        <div class="rule step" data-label="Lesson 4.3">{ul("The expansion, in detail")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Our class has no Observation support yet: SwiftUI would never know the recipient changed. Add @Observable, a macro from Apple&rsquo;s Observation framework. It enables observation of property accesses and changes, and SwiftUI uses that to update the views that depend on the properties they read.'),
                  ('SAY', 'Click: conceptually, the macro expands the type at compile time: the compiler generates additional machinery that participates in the Observation system. It is not simply a runtime flag. Click: Lesson 4.3 looks at that expansion in detail.'),
                  ('CONNECT', 'Connect it to a view.'))))

# ================================================================== Part 3 (5, 6)
divider(3, "Binding a view to it", "@State owns it; @Bindable binds to it", 'The text&rsquo;s MVVM lab, run.', 'The lab.')
LAB = """struct PaymentMVVMLab: View {

    @State private var viewModel = PaymentViewModel()

    var body: some View {
        @Bindable var viewModel = viewModel

        VStack(spacing: 20) {
            TextField("Recipient",
                      text: $viewModel.recipient)
                .textFieldStyle(.roundedBorder)

            TextField("Amount",
                      text: $viewModel.amountText)
                .textFieldStyle(.roundedBorder)

            Button("Continue") {
                print("Payment requested")
            }
            .disabled(!viewModel.isValid)
        }
        .padding()
    }
}"""
LABRUN = ["start:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;Continue disabled", "recipient only:&ensp;&ensp;&ensp;disabled",
          "+ amount \"1\":&ensp;&ensp;&ensp;&ensp;<b>enabled</b>", "amount cleared:&ensp;&ensp;&ensp;disabled", "amount \"abc\":&ensp;&ensp;&ensp;&ensp;<b>enabled</b>", "tap:&ensp;Payment requested"]
S.append(slide("Part 3 &middot; Connect PaymentViewModel to SwiftUI (section 5)", "Continue follows isValid", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) 140px 140px minmax(0,.7fr);gap:16px;align-items:start">
      {code("PaymentMVVMLab", LAB, "font-size:10.5px")}
      {PHONE("img/lab1.png", "Recipient only", 140)}
      <div class="step">{PHONE("img/lab2.png", "Amount &ldquo;abc&rdquo;", 140)}</div>
      <div class="step">{console("Simulator", LABRUN, 11)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s lab view: @State owns a PaymentViewModel; inside body, @Bindable var viewModel gives us bindings; two TextFields write the recipient and amount through those bindings; Continue is disabled unless isValid. We ran it in the simulator, typing through the keyboard input API. Left: recipient only, Continue still disabled.'),
                  ('SAY', 'Click: with any amount, Continue enables, even "abc". Click: the log: enabled with "1", disabled when the amount is cleared, enabled again with "abc", and the tap printed "Payment requested". isValid checks only that the fields are non-empty; Section 7 fixes that.'),
                  ('CONNECT', 'What did we introduce?'))))

P = []
PS = [("tap", "Keystroke", "the user types"), ("frame", "TextField", "writes through the binding"), ("link", "@Bindable binding", "sets viewModel.recipient"),
      ("layers", "ViewModel property", "changes; Observation records it"), ("code", "Body re-evaluated", "the view read that property"), ("check", "Continue updates", "disabled reflects isValid")]
for i, (ic, t, sub) in enumerate(PS):
    x = i * 188
    P.append(tall(x, 0, 172, 124, ic, t, sub, f'{i + 1}' if i < 5 else '6+', ''))
    if i < 5:
        P.append(wire(f'M{x + 173} 62H{x + 186}' + head(x + 186, 62, 'r')))
S.append(slide("Part 3 &middot; TextField to ViewModel (sections 5&ndash;6) &middot; conceptual", "The input pipeline", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1120 124', 'Keystroke, TextField, binding, ViewModel property, body re-evaluated, Continue updates', 'pipe', P, 'max-height:130px')}
    <p class="small muted" style="margin:6px 0 0">Stage 6 is the text&rsquo;s; stages 1&ndash;5 are ours, from section 5&rsquo;s list (only the last stage of the text&rsquo;s stepper was shared).</p>
    <div class="gap"></div>
    <div style="display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:18px">
      <div class="step">{card("@State", ul("Owns the instance"))}</div>
      <div class="step">{card("@Bindable", ul("Bindings to its properties"))}</div>
      <div class="step">{card("TextField", ul("Writes through them"))}</div>
      <div class="step">{card("SwiftUI", ul("Tracks what body read"))}</div>
    </div>
  </div>""", notes(('SAY', 'The input pipeline, conceptually. Only the last stage of the text&rsquo;s stepper was shared, so stages one to five are ours, built from Section 5&rsquo;s list. Click through: a keystroke; the TextField writes through its binding; the @Bindable binding sets viewModel.recipient; the property changes and Observation records the change; the body that read it is re-evaluated; Continue&rsquo;s disabled state reflects isValid.'),
                  ('SAY', 'Click through the four pieces from Section 5: @State owns the observable ViewModel instance; @Bindable provides bindings to its editable properties; TextField writes through those bindings; SwiftUI tracks the ViewModel properties the view reads.'),
                  ('CONNECT', 'Now, real validation.'))))

# ================================================================== Part 4 (7, 8)
divider(4, "Rules and dependencies", "Validator rules; the shared store", 'The ViewModel coordinates; others own.', 'Validation.')
VAL = """var parsedAmountPaise: Int? {
    Money.parsePaise(amountText)
}

func validate(
    availableBalancePaise: Int
) -> Bool {
    guard let amount = parsedAmountPaise else {
        return false
    }
    do {
        try PaymentValidator().validate(
            recipient: recipient,
            amountPaise: amount,
            balancePaise: availableBalancePaise
        )
        return true
    } catch {
        return false
    }
}"""
RL = [("ravi@npay", "1500.50", "true", "true"), ("ravi@npay", "abc", "true", "<b>false</b>"), ("&ensp;&ensp;&ensp;", "100", "true", "<b>false</b>"),
      ("ravi@npay", "30000", "true", "<b>false</b>"), ("ravi@npay", "0", "true", "<b>false</b>"), ("", "", "false", "false")]
S.append(slide("Part 4 &middot; Introduce proper payment validation (section 7)", "The ViewModel asks; the validator decides", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("PaymentViewModel", VAL, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["recipient", "amount", "isValid", "validate(₹25,000)"], RL)}
          <p class="small muted" style="margin:6px 0 0">Both run in the simulator, same inputs.</p></div>
        <div class="rule step" data-label="Separation">{ul("Validator owns the rules", "ViewModel coordinates", "View asks for the result")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Non-empty is not enough. We parse the amount with Money.parsePaise from Lesson 2.12 into parsedAmountPaise, then validate against the balance: no parsable amount is invalid; otherwise ask Lesson 4.1&rsquo;s PaymentValidator, and turn its throw into false.'),
                  ('SAY', 'Click: we ran both checks on the same inputs. The non-empty isValid accepted "abc", a blank recipient, thirty thousand rupees and zero. validate rejected all four, and agreed on the valid payment and the empty form.'),
                  ('SAY', 'Click: the separation: the validator owns the rules; the ViewModel coordinates validation; the SwiftUI view only asks for the result.'),
                  ('CONNECT', 'Validation needs the balance. Where does it come from?'))))

DEP = """@MainActor
@Observable
final class PaymentViewModel {

    var recipient = ""
    var amountText = ""
    var errorMessage: String?

    private let store: NPayStore

    init(store: NPayStore) {
        self.store = store
    }
}"""
S.append(slide("Part 4 &middot; How does the ViewModel reach NPayStore? (section 8)", "Inject the store; never create one", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Initializer injection", DEP, "font-size:12px")}
        {code("Incorrect", "private let store = NPayStore()", "font-size:13px")}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("A ViewModel with its own NPayStore, paying ₹1,500.50", ["its own store:&ensp;2,349,950 paise", "NPay&rsquo;s store:&ensp;2,500,000, 3 transactions", "Home:&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;₹25,000.00"], 12)}</div>
        <div class="step">{console("PaymentViewModel(store: NPay&rsquo;s store)", ["Home:&ensp;₹23,499.50"], 12)}</div>
        <div class="rule step" data-label="Why injection">{ul("The dependency is declared", "The same store as the rest of NPay")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPayStore still owns the demo balance and transactions, and stays the source of truth for now. The ViewModel receives it through its initializer and keeps it in a private let. It also gains an errorMessage.'),
                  ('SAY', 'The incorrect version creates its own store with private let store = NPayStore(). Click: we ran exactly that: a ViewModel with its own store paid ₹1,500.50. Its private store dropped to 2,349,950 paise, while NPay&rsquo;s real store stayed at 2,500,000 with three transactions, and Home kept showing ₹25,000.00. A second, invisible balance.'),
                  ('SAY', 'Click: the same payment through a ViewModel given NPay&rsquo;s store: Home showed ₹23,499.50. Click: initializer injection declares the dependency explicitly, and the ViewModel uses the same store instance as the rest of NPay, the lesson of 3.1&rsquo;s second @State owner, again.'),
                  ('CONNECT', 'Now the submission.'))))

# ================================================================== Part 5 (9, 11, 12)
divider(5, "Submitting in two stages", "Prepare for review; confirm to pay", 'Two user actions, two methods.', 'One method first.')
SUB = """func submitPayment() -> UUID? {
    guard let amount = Money.parsePaise(amountText) else {
        errorMessage = "Invalid amount"
        return nil
    }
    do {
        try PaymentValidator().validate(
            recipient: recipient, amountPaise: amount,
            balancePaise: store.balancePaise)
    } catch {
        errorMessage = "Payment validation failed"
        return nil
    }
    guard let transactionID = store.recordDemoPayment(
        recipient: recipient, amountPaise: amount) else {
        errorMessage = "Unable to record payment"
        return nil
    }
    recipient = ""; amountText = ""; errorMessage = nil
    return transactionID
}"""
S.append(slide("Part 5 &middot; Build the payment submission method (section 9)", "Coordinate: validator, store, presentation state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:22px;align-items:start">
      {code("submitPayment() (condensed)", SUB, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What it does", ul("Validator checks the rules", "Store records the transaction", "ViewModel updates its state", "Returns the ID"))}
        <div class="step">{card("Navigation stays out", ul("The router decides where the user goes"))}</div>
        <div class="rule step" data-label="But">{ul("Review and confirm are separate user actions (3.4)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s first submission method, condensed on the slide. Parse the amount, or set "Invalid amount". Validate with PaymentValidator against the store&rsquo;s balance, or set "Payment validation failed". Ask the store to record the demo payment, or set "Unable to record payment". On success clear the form and the error, and return the transaction ID.'),
                  ('SAY', 'It coordinates the workflow: the validator checks the rules, the store records the transaction, the ViewModel updates its presentation state, and it returns the ID so the caller can coordinate navigation. Click: navigation deliberately stays outside the ViewModel; the router remains responsible for where the user goes.'),
                  ('SAY', 'Click: but remember Lesson 3.4: Review and Confirm are two different user actions. One method that validates and executes at once doesn&rsquo;t match the flow.'),
                  ('CONNECT', 'Split it.'))))

TWOS = """struct ValidatedPaymentRequest: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}

func preparePayment() -> ValidatedPaymentRequest?
// parse + validate; set errorMessage or
// return an immutable request for review

func confirmPayment(
    _ request: ValidatedPaymentRequest
) -> UUID?
// validate again against the current balance,
// record, clear the form, return the ID"""
P = []
for i, (t, sub, l) in enumerate([("Payment form", "edit", None), ("preparePayment()", "validate, snapshot", '1'), ("Review sheet", "shows the request", None), ("confirmPayment(_:)", "revalidate, record", '2+'), ("Success", "router navigates", None)]):
    x = i * 224
    P.append(box(x, 0, 206, 60, t, sub, l, '', ''))
    if i < 4:
        P.append(wire(f'M{x + 207} 30H{x + 222}' + head(x + 222, 30, 'r')))
S.append(slide("Part 5 &middot; Two stages: prepare, then confirm (sections 11&ndash;12)", "The architecture mirrors the user&rsquo;s two actions", f"""  <div class="body">
    {cues(2)}
    {svg('0 0 1100 60', 'Payment form, preparePayment, review sheet, confirmPayment, success', 'two', P, 'max-height:66px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("PaymentViewModel (outline; full code in the text)", TWOS, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Validate twice", ul("First: better feedback before review", "Second: the balance may have changed"))}</div>
        <div class="rule step" data-label="Final authority">{ul("The store still enforces its own rules")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The flow from Lesson 3.4: form, review sheet, confirm, success. Tapping Review must not process the payment. Click: stage one, preparePayment, parses and validates, then returns an immutable ValidatedPaymentRequest, or sets "Invalid amount" or "Please check payment details". The review sheet shows that request. Click: stage two, confirmPayment, validates again against the current balance, setting "Payment details are no longer valid" if that fails, records the payment, clears the form and returns the ID.'),
                  ('SAY', 'ValidatedPaymentRequest replaces Lesson 3.4&rsquo;s review snapshot in our code. Click: why validate twice? The first validation improves the user experience; the second protects the operation against stale input, because the balance can change between opening the review and confirming. Click: and the store, as the final authority for this local simulation, still checks its own rules.'),
                  ('CONNECT', 'Does the second validation matter? We made the balance change.'))))

S.append(slide("Part 5 &middot; Why validate twice? Measured (section 12)", "The balance changed during review", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:180px minmax(0,1fr);gap:24px;align-items:start">
      <div class="step">{PHONE("img/stalee.png", "After Confirm", 180)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {console("Simulator, integrated NPay", ["prepare ₹20,000 &rarr; review sheet: ravi@npay", "meanwhile ₹10,000 leaves &rarr; balance 1,500,000 paise", "Confirm &rarr; balance <b>still 1,500,000</b>, sheet closed", "screen: &ldquo;Payment details are no longer valid&rdquo;"], 12.5)}
        <div class="step">{card("Without the second check", ul("The store would still refuse (its own rule)", "But the ViewModel couldn&rsquo;t say why"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'We tested the second validation in the integrated app. Prepare ₹20,000 to ravi@npay: the review sheet opens. While it is open, our script records a ₹10,000 payment elsewhere through the store, standing in for anything that changes the balance: the balance falls to fifteen thousand rupees. Then Confirm.'),
                  ('SAY', 'confirmPayment&rsquo;s revalidation failed: the balance stayed at 1,500,000 paise, the sheet closed, and, click, the Payments screen shows the ViewModel&rsquo;s message "Payment details are no longer valid" with Review disabled, because twenty thousand is now more than the balance.'),
                  ('SAY', 'Click: without the second check, the store would still have refused, its own rule, but the ViewModel would only see a nil and could not tell the user why.'),
                  ('CONNECT', 'Who owns the ViewModel in the real app?'))))

# ================================================================== Part 6 (10, 13, 14, 15, 17, 18)
divider(6, "Ownership and lifetime", "Who creates it, who keeps it", 'Body runs often; the ViewModel lives long.', 'The owner.')
ROOT = """struct PaymentsFeatureRoot: View {
    @State private var viewModel: PaymentViewModel

    init(store: NPayStore) {
        _viewModel = State(
            initialValue: PaymentViewModel(store: store)
        )
    }

    var body: some View {
        PaymentsScreen(viewModel: viewModel)
    }
}"""
S.append(slide("Part 6 &middot; Who owns the ViewModel? (section 10)", "A feature root creates it with the shared store", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("PaymentsFeatureRoot", ROOT, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("_viewModel", ul("Initializes the wrapper&rsquo;s storage"))}
        <div class="step">{card("In NPay (ours)", ul("<code>PaymentsFeatureRoot(store:router:)</code>", "Passes the router on"))}</div>
        <div class="warn step" data-label="Lifecycle">{ul("@State keeps the first instance", "A later store change may not reach it")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'In the small lab, @State private var viewModel = PaymentViewModel() was fine: the view owned it. In NPay the ViewModel needs the shared store, so a parent composition view, PaymentsFeatureRoot, creates it in its initializer with the store, and passes it to PaymentsScreen. We write underscore viewModel because we are initializing the property wrapper&rsquo;s storage, which is different from assigning to the wrapped property after initialization.'),
                  ('SAY', 'Click: in our NPay, flagged as ours, the Payments tab now shows PaymentsFeatureRoot with the store and the router; the router is passed through so the screen can navigate on success, as Section 22 describes.'),
                  ('SAY', 'Click: the lifecycle nuance: @State preserves its value while the view&rsquo;s identity is stable. If the parent later passed a different store to the same identity, the original ViewModel could remain. Dependencies should be stable for the owner&rsquo;s lifetime, or the design must handle replacement explicitly.'),
                  ('CONNECT', 'ViewModel versus store.'))))

VS = [("Owns payment form state", "Owns demo account state"), ("Exposes validation feedback", "Owns the transaction collection"),
      ("Prepares review requests", "Records demo payments"), ("Coordinates submission", "Updates the balance"), ("Screen / feature lifetime", "Application-root lifetime")]
S.append(slide("Part 6 &middot; ViewModel versus store (section 13)", "Feature state versus application state", f"""  <div class="body">
    {tbl(["PaymentViewModel", "NPayStore"], VS, 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:22px">
      <div class="step">{card("Moved in our code", ul("<code>paymentDraft</code> left NPayStore", "Recipient and amount live in the ViewModel"))}</div>
      <div class="rule step" data-label="Distinction">{ul("A ViewModel isn&rsquo;t a repository or domain service", "It coordinates a feature&rsquo;s presentation")}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s comparison. PaymentViewModel owns payment form state, exposes validation feedback, prepares review requests and coordinates submission, with a screen or feature lifetime. NPayStore owns the demo account state and the transaction collection, records demo payments and updates the balance, with an application-root lifetime.'),
                  ('SAY', 'Click: in our code that meant moving the payment draft out of NPayStore, where Lesson 3.5 put it: recipient and amount now live in the ViewModel. Click: and the important distinction: a ViewModel is not automatically a repository or a domain service; its primary job is to coordinate the state and behaviour a feature&rsquo;s presentation needs.'),
                  ('CONNECT', 'Is the ViewModel recreated? Experiment.'))))

LIFE = ["six tab switches:&ensp;&ensp;initializer ran <b>7</b> times", "typed &ldquo;ra&rdquo;, left, came back: <b>9</b> times", "draft after all of it:&ensp;recipient &ldquo;ra&rdquo;",
        "live instances:&ensp;&ensp;&ensp;&ensp;&ensp;1 kept (+1 briefly)", "each extra one:&ensp;&ensp;&ensp;&ensp;&ldquo;PaymentViewModel deinitialized&rdquo;"]
S.append(slide("Part 6 &middot; ViewModel identity, measured (sections 14, 17)", "The initializer runs often; one instance is kept", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 14: log the initializer", 'init(store: NPayStore) {\n    self.store = store\n    print("PaymentViewModel initialized")\n}', "font-size:13px")}
        <div class="step">{console("Integrated NPay, simulator", LIFE, 11.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why", ul("<code>PaymentViewModel(store:)</code> is evaluated whenever the parent view value is built", "@State keeps its original storage and drops the new one"))}</div>
        <div class="warn step" data-label="Section 17">{ul("Init logs don&rsquo;t prove lifetime", "Watch identity and deinit too")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Section 14&rsquo;s experiment: log the initializer, then navigate between tabs. We also tracked which instances were alive, through a debug-only hook. Click: six tab switches, and the initializer ran seven times. Typing "ra", leaving and coming back: nine. Yet the draft was still "ra": the ViewModel holding it was never replaced. One instance was kept, sometimes one extra existed for a moment, and every extra one printed "PaymentViewModel deinitialized" right away.'),
                  ('SAY', 'Click: why? Every time NPayRootView&rsquo;s body runs, it builds a new PaymentsFeatureRoot value, and its initializer evaluates PaymentViewModel(store:). SwiftUI keeps the @State storage it already has for that identity and discards the new object. Click: that is exactly Section 17&rsquo;s caveat: do not rely on the number of initializer log messages to prove object lifetime. View structs are recreated freely; the state-owned ViewModel is not.'),
                  ('CONNECT', 'And body evaluations?'))))

S.append(slide("Part 6 &middot; Debugging Observation (section 15)", "Body runs; the ViewModel stays", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Inside PaymentsScreen.body, temporarily", "let _ = Self._printChanges()", "font-size:14px")}
        <div class="step">{console("Typing &ldquo;ra&rdquo; into the recipient field", ["PaymentsScreen: \\PaymentViewModel.recipient changed.", "PaymentsScreen: \\PaymentViewModel.recipient changed."], 12)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Read it", ul("Two keystrokes, two body evaluations", "Named: the ViewModel&rsquo;s <code>recipient</code>"))}</div>
        <div class="rule step" data-label="Nuance">{ul("Body evaluation &ne; a new ViewModel", "Different lifetimes")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Temporarily add let underscore equals Self._printChanges() inside PaymentsScreen&rsquo;s body, then type into the recipient field. Click: our console for two keystrokes: twice, "PaymentsScreen: backslash PaymentViewModel dot recipient changed." With Observation, SwiftUI names the exact property of the observable object that the body depended on: a key path.'),
                  ('SAY', 'Click: two keystrokes, two body evaluations, each caused by the recipient property. Click: and the nuance: a body evaluation does not mean SwiftUI recreated the ViewModel. The view description and the ViewModel object have different lifetimes, as the last slide measured.'),
                  ('CONNECT', 'The lifetime picture.'))))

P = []
for i, (t, sub, ic) in enumerate([("PaymentsFeatureRoot", "owns @State storage", "layers"), ("PaymentViewModel instance", "stable while the owner&rsquo;s identity survives", "db"), ("PaymentsScreen", "reads state, creates bindings", "phone")]):
    y = i * 82
    P.append(box(0, y, 560, 60, t, sub, '1+' if i == 1 else None, '', ic))
    if i < 2:
        P.append(wire(f'M280 {y + 61}V{y + 80}' + head(280, y + 80, 'd')))
OLD = [("ObservableObject", "@Observable"), ("@Published", "Observable stored properties"), ("@StateObject", "@State for owned models"),
       ("@ObservedObject", "Plain references; @Bindable for bindings"), ("@EnvironmentObject", "@Environment(Model.self)")]
S.append(slide("Part 6 &middot; Who creates it, who retains it (sections 17&ndash;18)", "@State owns an @Observable ViewModel", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 560 224', 'PaymentsFeatureRoot owns the state storage; the PaymentViewModel instance; PaymentsScreen reads it', 'own', P, 'max-height:240px')}
        <p class="small muted" style="margin:6px 0 0">Lifetime follows the owning storage, not the number of body runs.</p></div>
      <div class="step">{tbl(["Older observation", "Modern Observation (iOS 17+)"], OLD, 'tbl compact')}
        <p class="small muted" style="margin:6px 0 0">Common correspondences, not exact one-to-one replacements.</p></div>
    </div>
  </div>""", notes(('SAY', 'The ownership picture. PaymentsFeatureRoot owns the @State storage. Click: the PaymentViewModel instance in it, in teal, is a stable reference while the owner&rsquo;s identity survives. PaymentsScreen reads its state and creates bindings. SwiftUI can re-evaluate PaymentsScreen&rsquo;s body many times without creating a new ViewModel: its lifetime is tied to the owning state storage, not to how many times body runs.'),
                  ('SAY', 'Click: why @State? Older SwiftUI code uses ObservableObject with @Published properties, owned with @StateObject. With iOS 17&rsquo;s Observation: @Observable, plain stored properties, and @State for a model the view owns. @ObservedObject becomes an ordinary reference, with @Bindable when bindings are needed; @EnvironmentObject becomes @Environment with the model type, as NPayPreferences did in Lesson 3.9. These are common correspondences, not exact replacements in every situation; Lesson 4.3 examines their runtime behaviour.'),
                  ('CONNECT', 'What should the ViewModel store, and what should it compute?'))))

# ================================================================== Part 7 (19, 20, 21, 22)
divider(7, "State, errors, navigation", "Derive, report, return", 'What the ViewModel exposes, and what it leaves to others.', 'Derived state.')
DUP = """// Stored: must be kept in sync
var recipient = ""
var amountText = ""
var isValid = false

// Derived: always current
var isValid: Bool {
    !recipient.isEmpty && !amountText.isEmpty
}"""
S.append(slide("Part 7 &middot; Derived state (sections 19&ndash;20)", "Compute it; don&rsquo;t store a copy", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Stored flag vs computed property", DUP, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("viewModel.recipient = \"ravi@npay\"", ul("Observation records the change", "Views that read it are re-evaluated"))}
        <div class="step">{card("A stored isValid", ul("Must be updated on every input change", "One missed update: wrong button state"))}</div>
        <div class="rule step" data-label="Default">{ul("Simple derived state: computed", "Cache only expensive results")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'When the user enters ravi@npay, the assignment to viewModel.recipient is a tracked mutation: views that depend on the recipient can be invalidated and re-evaluated. The text&rsquo;s interactive simulation showed derived values, recipient valid, amount syntax valid, following the inputs.'),
                  ('SAY', 'Click: a computed isValid does not need its own stored observable value; it derives from the underlying properties. Store it instead, and the ViewModel must keep it synchronized whenever either input changes: more chances for inconsistency. Click: simple derived state is best as a computed property; for expensive derivations, like Lesson 3.11&rsquo;s sort of fifty thousand records, caching may be appropriate.'),
                  ('CONNECT', 'What about errors?'))))

ERR = """// PaymentViewModel
var errorMessage: String?

// PaymentsScreen
if let errorMessage = viewModel.errorMessage {
    Text(errorMessage)
        .font(.caption)
        .foregroundStyle(.red)
}"""
NAV = """if let transactionID =
    viewModel.confirmPayment(request) {
    router.showPaymentSuccess(transactionID)
}"""
S.append(slide("Part 7 &middot; Errors and navigation (sections 21&ndash;22)", "The ViewModel reports; the view presents and navigates", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Expose errors, not alerts", ERR, "font-size:12.5px")}
        <div class="step">{card("Who decides what", ul("ViewModel: an error occurred", "View: inline text, alert, or another presentation"))}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("Navigation stays with the router", NAV, "font-size:12.5px")}</div>
        <div class="step">{card("Why return a result", ul("The ViewModel stays about payments", "Tests need no navigation system"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Should a ViewModel call SwiftUI&rsquo;s .alert()? No: .alert is a view modifier. The ViewModel exposes an error state, an optional errorMessage, and the view decides how to present it, here as red caption text. Our integrated screen does exactly this, which is how the stale-review message appeared; it replaced Lesson 3.4&rsquo;s failure alert. Later lessons use a structured error type instead of a string.'),
                  ('SAY', 'Click: the ViewModel determines that an error occurred; the view decides between inline text, an alert, or another accessible presentation.'),
                  ('SAY', 'Click: does the ViewModel need NPayRouter? One approach injects a router; another lets the ViewModel return a result and the view or a coordinator navigates. NPay uses the second: if confirmPayment returns an ID, the router shows payment success. In our code that happens in the sheet&rsquo;s onDismiss, as in Lesson 3.4. Click: it keeps the ViewModel focused on payments, and its tests need no navigation system.'),
                  ('CONNECT', 'Last: memory.'))))

# ================================================================== Part 8 (23, 24, 16, 25)
divider(8, "Memory and integration", "ARC still applies; the app still works", 'Deinit, cycles, and the full payment.', 'Deinit.')
S.append(slide("Part 8 &middot; What happens when the screen disappears? (section 23)", "Tab switches keep it; removing the owner frees it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 23", 'deinit {\n    print("PaymentViewModel deinitialized")\n}', "font-size:14px")}
        <div class="step">{console("Integrated NPay: switching tabs", ["the draft-holding ViewModel: never deinitialized", "(only the discarded extra instances were)"], 12)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Lab: an <code>if</code> removes PaymentsFeatureRoot", ["open:&ensp;&ensp;&ensp;&ensp;live 1", "close:&ensp;&ensp;&ensp;PaymentViewModel deinitialized &rarr; live 0", "reopen:&ensp;&ensp;a new instance (initializer #2)"], 12)}</div>
        <div class="rule step" data-label="Nuance">{ul("Disappearing &ne; released", "Lifetime follows real references")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'PaymentViewModel is a class, so ARC manages its lifetime: when the owning state storage releases it and no other strong references remain, it is deinitialized. Add a deinit that prints. Click: switching tabs in NPay never deinitialized the ViewModel that held the draft: the Payments tab&rsquo;s identity survives tab switches, Lesson 3.3. Only the discarded extra instances from two slides ago printed deinit.'),
                  ('SAY', 'Click: a small lab of ours removes the owner instead: a button toggles an if around PaymentsFeatureRoot. Open: one live ViewModel. Close: "PaymentViewModel deinitialized", zero live. Reopen: a brand-new instance, initializer number two, with an empty form.'),
                  ('SAY', 'Click: so do not assume a screen disappearing means its ViewModel is released, or kept: it depends on the actual references, which depend on view identity.'),
                  ('CONNECT', 'One way to keep it alive by accident.'))))

CYC = """viewModel.callback = {
    viewModel.performAction()
}

viewModel.callback = { [weak viewModel] in
    viewModel?.performAction()
}"""
S.append(slide("Part 8 &middot; Avoiding reference cycles (section 24)", "A closure the ViewModel owns, capturing the ViewModel", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:22px;align-items:start">
      {code("Strong capture, then weak capture", CYC, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Mac run, @MainActor @Observable class", ["strong: initialized", "strong: performAction", "after strongCapture()&ensp;&ensp;&larr; <b>no deinit</b>", "weak: initialized", "weak: performAction", "weak: deinitialized", "after weakCapture()"], 12)}</div>
        <div class="rule step" data-label="Unit 1">{ul("SwiftUI doesn&rsquo;t remove cycle risks", "ARC, weak, escaping closures (1.8)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'If the ViewModel stores a closure that captures the ViewModel strongly, the ViewModel owns the closure and the closure owns the ViewModel: neither can be released. A weak capture breaks the cycle: the closure holds viewModel weakly and calls it optionally.'),
                  ('SAY', 'Click: we ran both on the Mac with an @MainActor @Observable class that prints its lifecycle. The strong version initialized, ran its action, and when the function ended, no deinit: leaked. The weak version initialized, ran, and deinitialized as soon as the function ended.'),
                  ('SAY', 'Click: this is why Unit 1 studied ARC, strong and weak references and escaping closures, Lesson 1.8. SwiftUI does not eliminate reference-cycle risks in reference-type models.'),
                  ('CONNECT', 'The whole feature, working.'))))

P = []
AR = [("phone", "PaymentsScreen", "text fields, buttons, focus, review sheet"), ("layers", "PaymentViewModel", "form state, validation, error feedback"),
      ("check", "PaymentValidator", "pure Swift payment rules"), ("db", "NPayStore", "shared demo balance and transactions")]
for i, (ic, t, sub) in enumerate(AR):
    y = i * 70
    P.append(box(0, y, 560, 58, t, sub, '1+' if i == 1 else None, '', ic))
    if i < 3:
        P.append(wire(f'M280 {y + 59}V{y + 68}' + head(280, y + 68, 'd')))
P.append(box(620, 0, 300, 58, "NPayRouter", "navigates to success", None, '', 'decision'))
P.append(wire('M561 29H618' + head(618, 29, 'r'), None, 'dash'))
PAY = ["draft kept across tabs: ravi@npay, 1500.50", "Confirm: 2,349,950 paise, 4 transactions", "router: paymentsPath 1 route, Payment Recorded",
       "Home ₹23,499.50 &middot; History top: Sent to ravi@npay", "form after success: empty"]
S.append(slide("Part 8 &middot; Complete payment architecture (sections 16, 25)", "MVVM payment flow, verified", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:22px;align-items:start">
      <div>{cues(1)}{svg('0 0 920 270', 'PaymentsScreen, PaymentViewModel, PaymentValidator, NPayStore; NPayRouter navigates to success', 'arch', P, 'max-height:270px')}
        <p class="small muted" style="margin:6px 0 0">Conceptual. The view calls the router after the ViewModel reports success; the router isn&rsquo;t a store dependency.</p></div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Section 25 checks, integrated NPay", PAY, 11.5)}</div>
        <div class="step">{PHONE("img/payments.png", "Payments, with a ViewModel", 130)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The complete architecture after this lesson. PaymentsScreen: text fields, buttons, focus and the review sheet. Click: PaymentViewModel: form state, validation coordination and error feedback. PaymentValidator: pure Swift rules. NPayStore: shared demo balance and transactions. NPayRouter, to the side: the view invokes it after the ViewModel reports success; it is not a data dependency of the store. The ViewModel coordinates the feature but does not render views or own navigation.'),
                  ('SAY', 'Click: the text&rsquo;s lab checklist, verified on our integrated NPay. The draft survived switching tabs, now inside the ViewModel. Confirm left 2,349,950 paise and four transactions; the router pushed one route and "Payment Recorded" appeared; Home showed ₹23,499.50 and History "Sent to ravi@npay" on top; and the form was empty afterwards. Balance and history stay consistent.'),
                  ('SAY', 'Click: the Payments screen, unchanged to the eye: the refactoring moved code, not pixels.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('4.2', (), [("layers", "ViewModel = a screen&rsquo;s state and behaviour", "the view keeps layout, focus, presentation"),
                     ("key", "Inject the shared store; return results", "no second store; the router navigates"),
                     ("clock", "Lifetime follows the owner", "initializer ran 9 times; one instance kept the draft")],
          'Three things to remember. A ViewModel holds a screen&rsquo;s state and behaviour, @MainActor and @Observable, while the view keeps layout, focus and presentation, and asks it for results. It receives the shared store through its initializer, never creating its own, splits payment into prepare and confirm with validation at both, and returns an ID so the view can ask the router to navigate. And its lifetime follows the @State storage that owns it: the initializer ran nine times in our run, yet one instance kept the draft until its owner went away, and a strong self-capture would have kept it forever.')

review_divider(9)
review([("clock", "Question", "Does SwiftUI recreate the ViewModel every time body executes?",
         "Does SwiftUI recreate the ViewModel every time <code>body</code> executes?", "No",
         "Body ran on every keystroke; the same instance kept the draft.",
         "Equating body runs with object lifetime.", "Some say yes.", None),
        ("link", "Choose one", "What is the purpose of @Bindable?",
         "What is the purpose of <code>@Bindable</code>?<br>A. Start a network request<br>B. Create bindings to observable properties<br>C. Create a database", "B",
         "<code>$viewModel.recipient</code> for a TextField.",
         "Expecting @State to provide bindings to an object passed in.", "Most pick B.", None),
        ("check", "Choose one", "Why prefer computed validation over duplicated stored flags?",
         "Why prefer computed validation over duplicated stored flags?<br>A. To increase memory usage<br>B. To disable Observation<br>C. To avoid synchronization errors", "C",
         "A computed isValid is always current.",
         "Storing derived state by habit.", "Most pick C.", None),
        ("eye", "Question", "Should the ViewModel directly construct SwiftUI alert views?",
         "Should the ViewModel directly construct SwiftUI alert views?", "No",
         "It exposes errorMessage; the view chooses how to show it.",
         "Putting view modifiers in the ViewModel.", "Most say no.", None),
        ("clock", "Question", "Does @MainActor guarantee expensive synchronous code won't block the UI?",
         "Does <code>@MainActor</code> guarantee that expensive synchronous code won&rsquo;t block the UI?", "No",
         "It runs on the main actor: 0 frames during heavy work (3.11).",
         "Reading isolation as speed.", "Some say yes.", None),
        ("link", "Question", "Can a ViewModel class participate in ARC reference cycles?",
         "Can a ViewModel class participate in ARC reference cycles?", "Yes",
         "Strong self-capture: no deinit in our run.",
         "Thinking SwiftUI manages object memory.", "Most say yes.", None),
        ("key", "Predict the result", "private let store = NPayStore() inside the ViewModel; pay ₹1,500.50. Home shows?",
         "A ViewModel declares <code>private let store = NPayStore()</code> and records a ₹1,500.50 payment. What does Home show?<br>A. ₹23,499.50<br>B. ₹25,000.00<br>C. A crash", "B",
         "The payment went to a second store nobody else reads.",
         "Creating dependencies instead of injecting them.", "Some pick A.", None),
        ("layers", "Predict the result", "Switch tabs six times: how many PaymentViewModel inits?",
         "NPay&rsquo;s Payments tab owns its ViewModel with <code>_viewModel = State(initialValue: PaymentViewModel(store:))</code>. After six tab switches, the draft is&hellip;<br>A. Lost: a new ViewModel<br>B. Kept, though the initializer ran several times<br>C. Kept, and the initializer ran once", "B",
         "7 initializer runs; @State kept the original instance.",
         "Using init logs as proof of lifetime.", "Many pick C.", None),
        ("check", "Choose one", "From 4.1: what does PaymentValidator depend on?",
         "From Lesson 4.1: what does PaymentValidator depend on?<br>A. SwiftUI<br>B. Foundation only<br>C. NPayStore", "B",
         "That&rsquo;s why five tests ran without an app.",
         "Letting rules import the UI.", "Most pick B.", "Spaced review from Lesson 4.1.")])

S.append(next_slide('4.2', [("4.3", "Observation framework internals", "how @Observable tracks the reads we saw today"),
                            ("4.4", "Dependency injection", "the store passed in today, generalized"),
                            ("4.6", "Use cases", "SendPaymentUseCase takes over from the store"),
                            ("4.7", "UI state modeling", "structured errors instead of a String")],
                    'Lesson 4.3 opens up @Observable: how property access is tracked, how it differs from ObservableObject, and how SwiftUI decides what to invalidate. 4.4 generalizes today&rsquo;s initializer injection. 4.6 moves payment execution into a use case, and 4.7 replaces errorMessage with structured UI state.'))

S.append(lab_slide('4.2', "PaymentViewModel", "Move the screen&rsquo;s state into a ViewModel.",
                   ["Create PaymentViewModel: @MainActor, @Observable.",
                    "Move recipient and amount into it; bind with @Bindable.",
                    "Validate with PaymentValidator; inject the store.",
                    "Add preparePayment and confirmPayment.",
                    "Keep navigation in NPayRouter.",
                    "Log init and deinit; switch tabs; compare."],
                   "", 'Expected, as in our run: the draft survives tab switches; init logs appear more than once but one instance keeps the state; ₹23,499.50 and the new History row after a payment; a stale review is refused with a message.',
                   side=f'<div>{card("You hand in", ul("Your ViewModel and feature root", "Your init/deinit log with tab switches", "The 12-item checklist, ticked"))}</div>'))

end_slide('4.2', 'MVVM Internals:<br>PaymentViewModel', 'Lesson 4.3 &mdash; Observation Framework Internals',
          'You can now build an observable ViewModel, bind a view to it, inject the shared store, prepare and confirm payments in two stages, and explain how long the ViewModel lives and why.',
          'Next, Lesson 4.3: Observation framework internals, how @Observable works behind the scenes.')

write_deck(OUT42, '4.2', 'MVVM Internals: PaymentViewModel', 'MVVM Internals: PaymentViewModel')
