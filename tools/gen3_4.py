"""Generates decks/unit-3/lesson-3.4/index.html from the Lesson 3.4 text (Sheets, Alerts & Modal Presentation).
The text came in three pieces (Sections 1-14, cut off; "Part 2" Sections 14-21; a note about a complete-code ZIP that
was not shared), grouped into 8 Parts. The complete code through 3.4 is assembled from the text's Sections 10-18 onto
the 3.3 code (flagged). Console output and screenshots come from tools/sim3_4 (iOS Simulator)."""
import html, os, re, sys
OUT34 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

title_slide('3.4', 'Sheets, Alerts &amp;<br>Modal Presentation',
            'Before NPay moves money, the user <b>reviews</b> it: a sheet over the form, one confirmation, then success, <b>after</b> the sheet has gone.',
            'In Lesson 3.3, tapping Send Demo Payment recorded the transaction at once. A payments app should let the user check the recipient and amount first. Today: modal presentation. Sheets, full-screen covers, alerts and confirmation dialogs, presentation state and dismissal, and how to coordinate a sheet with navigation. We built the complete flow and measured the parts that can go wrong: the order of dismissal and navigation, a double tap on Confirm, and a balance that changes while the review is open.')
outcomes_slide('3.4', [("layers", "Present a <b>sheet</b> from state, and dismiss it"),
                       ("diff", "Choose: navigation, sheet, cover, alert or dialog"),
                       ("file", "Review a payment with <code>sheet(item:)</code> and a draft"),
                       ("clock", "Navigate <b>after</b> dismissal with <code>onDismiss</code>"),
                       ("shield", "Stop double confirms; re-validate at confirm time"),
                       ("eye", "Know what sheet-local state and dismiss-locking really guarantee")])
where_slide('3.4', 'Today: review before paying', (),
            '3.3: four tabs, one router, one store; payments recorded on tap.',
            'Form &rarr; review sheet &rarr; confirm &rarr; success.',
            'Lesson 3.3 built NPay&rsquo;s tabs, router and store. Today the payment gets a review step presented modally. Next lesson: preserving state across navigation.',
            'The new flow.')

# ================================================================== Part 1 (intro, 1)
divider(1, "The milestone", "Review before you pay", 'What if the recipient or amount is wrong?', 'The new flow.')
FL = [("file", "Payment form", "recipient, amount"), ("eye", "Review sheet", "check the details"), ("check", "Confirm", "record once"), ("layout", "Payment Success", "the receipt")]
P = []
for i, (ic, t, sub) in enumerate(FL):
    x = i * 285
    P.append(tall(x, 0, 262, 104, ic, t, sub, None, 'lit' if i == 1 else ''))
    if i < 3:
        P.append(wire(f'M{x + 264} 52H{x + 283}' + head(x + 283, 52, 'r')))
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "Form &rarr; review &rarr; confirm &rarr; success", f"""  <div class="body">
    {svg('0 0 1117 104', 'Payment form, review sheet, confirm, payment success', 'fl', P, 'max-height:118px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The challenge", ul("Show a review <b>temporarily</b>", "Without pushing onto the Payments stack"))}
        <div class="step">{card("Today&rsquo;s APIs", ul("<code>sheet</code>, <code>fullScreenCover</code>, <code>alert</code>, <code>confirmationDialog</code>", "Presentation state and dismissal"))}</div>
      </div>
      {PHONE("img/before.png", "3.3: records on tap", 150)}
      <div class="step">{PHONE("img/review.png", "3.4: a review sheet", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'Today tapping Send Demo Payment records the transaction immediately and navigates to success. If the user typed the wrong recipient or amount, it is too late. A payments app should let them review first. The flow becomes: payment form, review sheet, confirm, payment success.'),
                  ('SAY', 'The engineering challenge: present a review screen temporarily, without pushing another destination onto the Payments navigation stack. Click: the tools: sheet, fullScreenCover, alert, confirmationDialog, presentation state, dismissal.'),
                  ('SAY', 'On the left, 3.3: the button that records at once. Click: today&rsquo;s app: Review Payment opens a native sheet over the form, showing the recipient and amount.'),
                  ('CONNECT', 'What is a sheet?'))))

# ================================================================== Part 2 (2-4)
divider(2, "Sheets", "Modal, temporary, state-driven", 'A focused task over the current interface.', 'The smallest sheet.')
SX = """struct SheetExperiment: View {
    @State private var showSheet = false

    var body: some View {
        Button("Review Payment") {
            showSheet = true
        }
        .sheet(isPresented: $showSheet) {
            Text("Payment Review")
                .font(.title)
                .presentationDetents([.medium, .large])
        }
    }
}"""
S.append(slide("Part 2 &middot; What is a sheet? (section 2)", "A Bool presents it; dismissal writes it back", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.7fr) 150px;gap:22px;align-items:start">
      {code("SheetExperiment.swift", SX, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("A sheet", ul("<b>Modal</b>: over the current interface", "A focused task, not a step deeper"))}
        <div class="step">{console("onChange(of: showSheet), simulator", ["tap Review Payment&ensp;&rarr; showSheet: true", "swipe down&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&rarr; showSheet: false"], 12.5)}</div>
      </div>
      <div class="step">{PHONE("img/sheetexp.png", "Medium detent", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'A sheet is a modal presentation: it appears over the current interface, typically for a focused task, without navigating permanently deeper into the stack. SwiftUI provides sheet(isPresented:content:). The text&rsquo;s minimal example: a Bool, a button that sets it to true, and a sheet modifier whose content is a Text with presentation detents.'),
                  ('SAY', 'Click: our run with onChange on the Bool. Tapping Review Payment set it to true and the sheet appeared. Swiping it down set it back to false: SwiftUI updated the binding when the sheet was dismissed. State-driven UI again: the Bool is the truth, in both directions.'),
                  ('SAY', 'Click: the sheet at its medium height, the first detent, over the button.'),
                  ('CONNECT', 'What happens between the tap and the sheet?'))))

PS = [("tap", "Tap Review", "the button action runs"), ("code", "State changes", "showSheet = true"), ("diff", "SwiftUI sees it", "the sheet modifier&rsquo;s binding"),
      ("frame", "Content built", "the sheet&rsquo;s view"), ("layers", "Presented", "over the current UI"), ("eye", "Dismissed later", "binding back to false")]
P = []
for i, (ic, t, sub) in enumerate(PS):
    x = i * 190
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}', ''))
    if i < 5:
        P.append(wire(f'M{x + 174} 60H{x + 188}' + head(x + 188, 60, 'r')))
S.append(slide("Part 2 &middot; How does .sheet() work? (section 3) &middot; conceptual", "Six stages, one presentation", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1132 120', 'Tap, state changes, SwiftUI sees the binding, content built, presented, dismissed', 'sp', P, 'max-height:140px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {card("Not a new app", ul("A presentation <b>inside</b> the running app", "Our run: still <b>1</b> window with the sheet up"))}
      <p class="small muted" style="margin:0">Conceptual presentation flow. SwiftUI&rsquo;s internal presentation-controller implementation is not part of its public contract.</p>
    </div>
  </div>""", notes(('SAY', 'Only stage 1 came with the text; stages 2 to 6 are our conceptual outline. Click: the user taps Review; the button action runs. Click: it changes state, showSheet becomes true. Click: SwiftUI notices the change through the sheet modifier&rsquo;s binding. Click: it builds the sheet&rsquo;s content. Click: it presents it over the current interface. Click: later, a dismissal sets the binding back to false.'),
                  ('SAY', 'Important distinction: a sheet is not a new iOS process; it is a presentation inside the running app. Our run counted the app&rsquo;s windows with the sheet up: still one. That is what we observed, not a promise; the text&rsquo;s caption applies: the internal presentation machinery is not part of the public contract.'),
                  ('CONNECT', 'We now have two ways to show another screen.'))))

SN = [("Pushes a navigation destination", "Presents modal content"), ("Hierarchical navigation", "Focused temporary tasks"), ("Back navigation", "Dismissal"),
      ("Managed by the navigation path", "Managed by presentation state"), ("History &rarr; Transaction Detail", "Payment &rarr; Review")]
S.append(slide("Part 2 &middot; Sheet versus NavigationStack (section 4)", "Deeper, or temporary?", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:24px;align-items:start">
      {tbl(["NavigationStack", "Sheet"], SN, 'tbl')}
      <div class="rule step" data-label="Every screen a sheet? No">{ul("Moving <b>deeper</b>: a navigation destination", "A <b>temporary</b>, focused task: a sheet")}</div>
    </div>
  </div>""", notes(('SAY', 'Two ways to show another screen. A NavigationStack pushes a destination; a sheet presents modal content. Navigation is for hierarchies, sheets for focused temporary tasks. You leave a pushed screen with Back, a sheet by dismissal. Navigation is managed by the path, a sheet by presentation state. History to Transaction Detail is navigation; Payment to Review is a sheet.'),
                  ('SAY', 'Click: so should every new screen be a sheet? No. Use a navigation destination when the user is moving deeper into a hierarchy; use a sheet when they are doing a temporary, focused interaction and will come back to where they were.'),
                  ('CONNECT', 'How does a sheet close itself?'))))

# ================================================================== Part 3 (5, 6)
divider(3, "Dismissal and detents", "Closing and sizing a sheet", 'An environment action, and the heights a sheet allows.', 'dismiss.')
DM = """struct ReviewSheet: View {
    @Environment(\\.dismiss) private var dismiss

    var body: some View {
        VStack(spacing: 20) {
            Text("Review Payment")

            Button("Cancel") {
                dismiss()
            }
        }
    }
}"""
S.append(slide("Part 3 &middot; How dismissal works (section 5)", "<code>dismiss()</code> asks; it changes no business state", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 140px;gap:22px;align-items:start">
      {code("Dismissing from inside", DM, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("What happens", ul("<code>dismiss</code> comes from the <b>environment</b> (as in 2.6)", "Calling it requests dismissal", "The parent&rsquo;s data is untouched"))}
        <div class="step">{console("NPay: Edit Details calls dismiss()", ["recipient \"ravi@npay\", amount \"1500.50\""], 12.5)}</div>
      </div>
      <div class="step">{PHONE("img/edit.png", "Back on the form", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'Inside a sheet, SwiftUI provides an environment action, dismiss. The sheet reads it with @Environment and calls it from Cancel. Calling dismiss requests dismissal of the current presentation; it does not directly modify the parent&rsquo;s business state. We used the same action in 3.1 to pop a pushed screen.'),
                  ('SAY', 'Connect to Unit 2: environment values propagate to descendants, like fonts in Lesson 2.6. Dismissal is one such contextual capability.'),
                  ('SAY', 'Click: in NPay, the review sheet&rsquo;s Edit Details calls dismiss. Our run: back on the form, both fields still hold ravi@npay and 1500.50: the draft lives in PaymentsScreen, not in the sheet. Click: the screenshot.'),
                  ('CONNECT', 'How tall is a sheet?'))))

DET = """.sheet(isPresented: $showSheet) {
    ReviewSheet()
        .presentationDetents([
            .medium,
            .large
        ])
}"""
S.append(slide("Part 3 &middot; presentationDetents: sheet height (section 6)", "Medium, large, or both", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 150px;gap:22px;align-items:start">
      {code("Detents on the sheet&rsquo;s content", DET, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Detents", ul("The heights the sheet can rest at", "First one listed: the starting height", "The user drags between them"))}
        <div class="step">{card("Approximate", ul("Real size depends on device, orientation and presentation"))}</div>
      </div>
      {PHONE("img/review.png", "NPay review: medium", 150)}
    </div>
  </div>""", notes(('SAY', 'presentationDetents configures the sizes a sheet supports. Note where it goes: on the sheet&rsquo;s content, not on the button that presents it. With medium and large, the sheet opens at medium, the first listed, and the user can drag it up to large.'),
                  ('SAY', 'Click: the text&rsquo;s widget showed approximate heights; real dimensions depend on the device, orientation and presentation environment. On the right, NPay&rsquo;s review sheet at medium on an iPhone 17, with the form still visible above it.'),
                  ('CONNECT', 'Three more presentations.'))))

# ================================================================== Part 4 (7-9)
divider(4, "Covers, alerts, dialogs", "Three more modal tools", 'Each fits a different kind of interruption.', 'Full-screen cover.')
COV = """@State private var showFullScreen = false

.fullScreenCover(isPresented: $showFullScreen) {
    Text("Full Screen Payment Flow")
}"""
ALR = """Button("Delete Draft") {
    showAlert = true
}
.alert("Delete payment draft?", isPresented: $showAlert) {
    Button("Delete", role: .destructive) {
        print("Draft deleted")
    }
    Button("Cancel", role: .cancel) {}
} message: {
    Text("This action cannot be undone.")
}"""
S.append(slide("Part 4 &middot; fullScreenCover and alert (sections 7&ndash;8)", "The whole screen, or one decision", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 125px minmax(0,1.1fr) 125px;gap:16px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("fullScreenCover", COV, "font-size:11.5px")}
        {card("Use for", ul("Immersive flows: onboarding, sign-in", "Not our review: a sheet fits"))}
      </div>
      {PHONE("img/cover.png", "Full screen", 125)}
      <div class="step" style="display:flex;flex-direction:column;gap:12px">
        {code("alert", ALR, "font-size:11px")}
        {console("Simulator", ["tap Delete &rarr; Draft deleted"], 12)}
      </div>
      <div class="step">{PHONE("img/alert.png", "Alert", 125)}</div>
    </div>
  </div>""", notes(('SAY', 'fullScreenCover presents content over the entire interface, with the same isPresented binding as a sheet. Useful when the presented experience should take the whole screen: onboarding, or a focused authentication flow. Our payment review is better as a sheet, which keeps the context visible. The screenshot: the cover fills the screen; no tab bar, no form.'),
                  ('SAY', 'Click: alert presents important information or asks for a simple decision. The text&rsquo;s example: Delete payment draft?, a destructive Delete, a Cancel, and a message. Roles matter: the system styles Delete in red and treats Cancel as the cancel action. Our run: tapping Delete printed "Draft deleted". Alerts are for concise, important messages, never complex forms.'),
                  ('CONNECT', 'A set of related actions: a confirmation dialog.'))))

DLG = """Button("Payment Options") {
    showOptions = true
}
.confirmationDialog(
    "Choose an action",
    isPresented: $showOptions
) {
    Button("Save Draft") {
        print("Draft saved")
    }
    Button("Discard", role: .destructive) {
        print("Draft discarded")
    }
}"""
CMP = [("<code>.sheet()</code>", "Custom temporary workflows"), ("<code>.fullScreenCover()</code>", "Immersive modal experiences"),
       ("<code>.alert()</code>", "Important messages or simple confirmations"), ("<code>.confirmationDialog()</code>", "Choosing among related actions")]
S.append(slide("Part 4 &middot; confirmationDialog, and which to use (section 9)", "Related actions; then the whole menu", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 130px minmax(0,1fr);gap:18px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("confirmationDialog", DLG, "font-size:11.5px")}
        <div class="step">{console("Simulator", ["actions: Save Draft, Discard, Cancel", "tap Save Draft &rarr; Draft saved"], 12)}</div>
      </div>
      {PHONE("img/dialog.png", "Dialog", 130)}
      <div class="step">{tbl(["API", "Best suited for"], CMP, 'tbl')}</div>
    </div>
  </div>""", notes(('SAY', 'confirmationDialog presents a set of related actions. Same shape: a title, a binding, and buttons. Click: our run listed three actions, Save Draft, Discard and Cancel: we wrote only two; the system added Cancel. Tapping Save Draft printed "Draft saved". On iPhone it appears anchored near the button, as in the screenshot.'),
                  ('SAY', 'Click: the summary. sheet: custom temporary workflows. fullScreenCover: immersive modal experiences. alert: important messages or simple confirmations. confirmationDialog: choosing among related actions.'),
                  ('CONNECT', 'Now NPay&rsquo;s review sheet.'))))

# ================================================================== Part 5 (10-12)
divider(5, "NPay&rsquo;s review sheet", "Validate, review, confirm", 'Two steps instead of one.', 'A draft model.')
DR = """struct PaymentDraft: Identifiable {
    let id = UUID()
    let recipient: String
    let amountPaise: Int
}

@State private var reviewDraft: PaymentDraft?

.sheet(item: $reviewDraft) { draft in
    PaymentReviewSheet(draft: draft)
}"""
S.append(slide("Part 5 &middot; A review model and sheet(item:) (section 10)", "The optional item <b>is</b> the presentation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("PaymentDraft + sheet(item:)", DR, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Two steps", ul("1. Validate, then <b>present</b> a review", "2. Confirm, then <b>execute</b> the demo payment"))}
        <div class="step">{tbl(["<code>reviewDraft</code>", "Screen"], [("<code>nil</code>", "no sheet"), ("a draft", "sheet presented, showing <b>that</b> draft")])}</div>
        <div class="step">{card("Why item, not a Bool", ul("One value: whether to show <b>and</b> what to show", "No Bool and optional to keep in sync"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'In PaymentsScreen, submitting used to call store.recordDemoPayment directly. Now two steps: validate and present a review; then confirm and execute. The review needs a model: PaymentDraft, a recipient and an amount in paise, Identifiable with its own UUID.'),
                  ('SAY', 'Identifiable because SwiftUI has an item-based sheet API. Click: the optional draft is the presentation state: nil means no sheet; a draft means the sheet is presented, showing that draft, which the content closure receives.'),
                  ('SAY', 'Click: why not a Bool plus a separate optional draft? Two pieces of state can disagree: a sheet with no draft, or a draft with no sheet. One optional cannot.'),
                  ('CONNECT', 'The sheet itself.'))))

RV = """struct PaymentReviewSheet: View {
    let draft: PaymentDraft
    let onConfirm: () -> Void

    @Environment(\\.dismiss) private var dismiss

    var body: some View {
        VStack(alignment: .leading, spacing: 24) {
            Text("Review Payment")
                .font(.title.bold())
            LabeledContent("Recipient", value: draft.recipient)
            LabeledContent("Amount",
                           value: Money.display(draft.amountPaise))
            Button("Confirm Demo Payment") { onConfirm() }
                .buttonStyle(.borderedProminent)
            Button("Edit Details") { dismiss() }
                .buttonStyle(.bordered)
        }
        .padding()
        .presentationDetents([.medium, .large])
    }
}"""
S.append(slide("Part 5 &middot; Build the PaymentReviewSheet (section 11)", "Shows a draft; exposes one action", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.55fr) 150px;gap:20px;align-items:start">
      {code("Screens/PaymentReviewSheet.swift (text)", RV, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Owns", ul("Nothing but presentation"))}
        <div class="step">{card("Doesn&rsquo;t own", ul("The balance or history", "The payment operation"))}</div>
        <div class="step">{card("The parent", ul("Performs the demo payment"))}</div>
      </div>
      {PHONE("img/review.png", "In the simulator", 150)}
    </div>
  </div>""", notes(('SAY', 'PaymentReviewSheet.swift: a title, the recipient and the amount as LabeledContent rows, a prominent Confirm Demo Payment button that calls onConfirm, and Edit Details that dismisses. Detents medium and large on the content.'),
                  ('SAY', 'The important architectural detail. Click: it owns nothing but presentation. Click: it does not own the balance, the history, or the payment operation; it displays a draft and exposes a confirmation action. Click: the parent remains responsible for the demo operation, the pattern of onSend in 2.12 and onDone in 3.2.'),
                  ('CONNECT', 'Wire it into PaymentsScreen.'))))

NV = """// PaymentsScreen
@State private var reviewDraft: PaymentDraft?

// Review Payment, when the form is valid
reviewDraft = PaymentDraft(recipient: recipient,
                           amountPaise: amountPaise)

.sheet(item: $reviewDraft) { draft in
    PaymentReviewSheet(draft: draft) {
        if let transactionID = store.recordDemoPayment(
            recipient: draft.recipient,
            amountPaise: draft.amountPaise) {
            reviewDraft = nil
            router.showPaymentSuccess(transactionID)
        }
    }
}"""
S.append(slide("Part 5 &middot; Connect the sheet to PaymentsScreen (section 12)", "First version: dismiss and navigate together", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("PaymentsScreen (section 12)", NV, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The flow", ul("Valid form &rarr; <code>reviewDraft</code> set &rarr; sheet", "Confirm &rarr; store records &rarr; ID", "<code>reviewDraft = nil</code> and <b>push success</b>"))}
        <div class="warn step" data-label="One nuance">{ul("Dismissing a sheet and pushing in the <b>same</b> update", "Not guaranteed to transition as you want")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'PaymentsScreen gets the reviewDraft state. When the form is valid and the user taps Review Payment, it creates a draft from the recipient and the parsed amount. The sheet modifier passes that draft to PaymentReviewSheet, with a trailing closure for onConfirm: record the payment in the store; with the returned ID, set reviewDraft to nil to dismiss, and ask the router to show success.'),
                  ('SAY', 'Click: the nuance the text raises. That closure dismisses a sheet and pushes a navigation destination in the same synchronous update. We should not assume that always produces the transition we want. The fix uses the sheet&rsquo;s onDismiss callback, which is Part 6, where we also measure what this version does.'),
                  ('CONNECT', 'Two kinds of UI state are now in play.'))))

# ================================================================== Part 6 (13, 15)
divider(6, "Dismiss, then navigate", "Two state machines, coordinated", 'Navigation in the router; presentation in the screen.', 'Two machines.')
P = ['<rect class="sh" x="0" y="0" width="420" height="200" rx="16" style="fill:none;stroke-dasharray:6 5"/>', '<text class="sm" x="16" y="24">Navigation &middot; NPayRouter.paymentsPath</text>',
     box(20, 44, 170, 52, 'Payment', '[]', None, ''), wire('M192 70H226' + head(226, 70, 'r')), box(230, 44, 170, 52, 'Success', '[.paymentSuccess]', None, 'lit'),
     '<rect class="sh" x="460" y="0" width="420" height="200" rx="16" style="fill:none;stroke-dasharray:6 5"/>', '<text class="sm" x="476" y="24">Presentation &middot; PaymentsScreen.reviewDraft</text>',
     box(480, 44, 170, 52, 'No sheet', 'nil', None, ''), wire('M652 70H686' + head(686, 70, 'r')), box(690, 44, 170, 52, 'Review sheet', 'a draft', None, 'lit'),
     '<text class="sm" x="440" y="160" text-anchor="middle">NPayStore: the demo transaction data</text>']
S.append(slide("Part 6 &middot; Two independent state machines (section 13)", "Where the user is; what is presented", f"""  <div class="body">
    {svg('0 0 880 200', 'Navigation state in the router and presentation state in the payment screen', 'two', P, 'max-height:220px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:18px">
      {card("Router", ul("Navigation destinations"))}
      <div class="step">{card("PaymentsScreen", ul("Temporary presentation state"))}</div>
      <div class="step">{card("Store", ul("The demo transaction data"))}</div>
    </div>
  </div>""", notes(('SAY', 'NPay now has two related but distinct UI mechanisms. Navigation: the router&rsquo;s payments path, empty on the form, one success route after a payment. Presentation: PaymentsScreen&rsquo;s reviewDraft, nil for no sheet, a draft for the review sheet.'),
                  ('SAY', 'The router manages navigation destinations. Click: the payment screen manages temporary presentation state. Click: the store manages the demo transaction data. Three owners, three jobs; keeping them separate makes the app easier to reason about, and it is why "dismiss, then navigate" is a coordination problem between two machines.'),
                  ('CONNECT', 'Measure the two orders.'))))

OD = """@State private var reviewDraft: PaymentDraft?
@State private var pendingSuccessID: UUID?

.sheet(item: $reviewDraft, onDismiss: {
    guard let id = pendingSuccessID else { return }
    pendingSuccessID = nil
    router.showPaymentSuccess(id)
}) { draft in
    PaymentReviewSheet(draft: draft) {
        if let id = store.recordDemoPayment(
            recipient: draft.recipient,
            amountPaise: draft.amountPaise) {
            pendingSuccessID = id
            reviewDraft = nil
        }
    }
}"""
S.append(slide("Part 6 &middot; Better: navigate in onDismiss (section 15)", "Remember the ID; push when the sheet is gone", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      {code("PaymentsScreen (section 15)", OD, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Section 12: dismiss + push together", ["t=&ensp;&ensp;9 ms&ensp;sheet shown, paymentsPath 1", "t=567 ms&ensp;sheet gone,&ensp;paymentsPath 1"], 12)}</div>
        <div class="step">{console("Section 15: onDismiss", ["t=&ensp;&ensp;8 ms&ensp;sheet shown, paymentsPath 0", "t=588 ms&ensp;sheet gone,&ensp;paymentsPath 1"], 12)}</div>
        <div class="rule step" data-label="Read it">{ul("Same update: the push happened <b>behind</b> the sheet", "onDismiss: the path changed only once the sheet was gone", "Both reached Success here; only one is ordered by design")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The better approach: a pending transaction ID. Confirm records the payment, stores the ID in pendingSuccessID, and sets reviewDraft to nil. The navigation happens in the sheet&rsquo;s onDismiss callback: if there is a pending ID, clear it and ask the router to show success. We no longer request navigation in the same update as the dismissal.'),
                  ('SAY', 'We measured both, polling every 10 milliseconds after Confirm. Click: the Section 12 version: at 9 ms the sheet is still on screen and the payments path already holds the success route: the push happened behind the sheet. At 567 ms the sheet is gone. Click: the onDismiss version: at 8 ms the sheet is up and the path is still empty; when the sheet is gone, the path holds the success route.'),
                  ('SAY', 'Click: honestly read: on iOS 26.5 both versions ended on the success screen. The difference is that onDismiss orders the two transitions by design, instead of depending on how this release happens to handle a push behind a sheet.'),
                  ('CONNECT', 'The coordinated transition, stage by stage.'))))

CT = [("tap", "Confirm tapped", "the sheet calls onConfirm"), ("db", "Store records", "returns an ID"), ("key", "ID pending", "pendingSuccessID = id"),
      ("diff", "Draft cleared", "reviewDraft = nil"), ("eye", "Sheet dismissed", "onDismiss runs"), ("layers", "Router pushes", "Payment Success")]
P = []
for i, (ic, t, sub) in enumerate(CT):
    x = i * 190
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}', ''))
    if i < 5:
        P.append(wire(f'M{x + 174} 60H{x + 188}' + head(x + 188, 60, 'r')))
S.append(slide("Part 6 &middot; Coordinated payment transition (section 15) &middot; conceptual", "Six stages, in order", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1132 120', 'Confirm tapped, store records, ID pending, draft cleared, sheet dismissed, router pushes success', 'ct', P, 'max-height:140px')}
    <div class="gap"></div>
    <div class="warn step" data-label="Not a delay">{ul("<code>DispatchQueue.main.asyncAfter</code> to wait for an animation: <b>fragile</b>", "Coordinate with the presentation lifecycle")}</div>
  </div>""", notes(('SAY', 'Only stage 1 came with the text; the rest is our conceptual outline of the code we just ran. Click: Confirm is tapped; the sheet calls its confirmation closure. Click: the store validates and records, returning an ID. Click: the screen keeps it as pending. Click: it clears reviewDraft, which requests dismissal. Click: when the sheet has gone, onDismiss runs. Click: and only then does the router push Payment Success.'),
                  ('SAY', 'Click: the senior-engineer insight from the text: coordinate a UI transition with the relevant presentation lifecycle, not with arbitrary delays like asyncAfter. A fixed delay guesses how long an animation takes; it breaks with a different device, accessibility settings, or the next release.'),
                  ('CONNECT', 'Now the money: what if Confirm runs twice?'))))

# ================================================================== Part 7 (14, 16-18)
divider(7, "Safety in the sheet", "Once, valid, and honest", 'Double taps, stale validation, local state, dismiss-locking.', 'Double taps.')
GD = """@State private var isProcessing = false

Button("Confirm Demo Payment") {
    guard !isProcessing else { return }
    isProcessing = true
    onConfirm()
}
.disabled(isProcessing)"""
S.append(slide("Part 7 &middot; Why confirmation must be idempotent (section 16)", "Two taps, two payments", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {console("Confirm activated twice, back to back (simulator)", ["without isProcessing: transactions 3 &rarr; 5, balance ₹21,999.00", "with isProcessing:&ensp;&ensp;&ensp;transactions 3 &rarr; 4, balance ₹23,499.50"], 13)}
        <div class="step">{code("UI protection (section 16)", GD, "font-size:13px")}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{tbl(["Idea", "Means"], [("UI protection", "stop repeated taps while processing"), ("Business idempotency", "one logical request applied <b>once</b>")], 'tbl')}</div>
        <div class="warn step" data-label="Not enough">{ul("A disabled button protects <b>this</b> view instance", "It is not durable idempotency")}</div>
        <div class="rule step" data-label="Production">{ul("Server-enforced: a stable request ID, authoritative handling")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'What if the user taps Confirm twice? We tested it: two activations back to back, before SwiftUI could dismiss the sheet. Without a guard, a confirm button that records the payment ran twice: two transactions, and the balance dropped by ₹3,001, to ₹21,999.00. With the guard, one transaction, ₹23,499.50.'),
                  ('SAY', 'Click: the guard from the text: an isProcessing state; the action returns early if it is set, sets it, then confirms; and the button is disabled while processing. Our complete code uses it.'),
                  ('SAY', 'Click: two different ideas. UI protection prevents repeated taps while processing. Business idempotency ensures the same logical payment request cannot be applied more than once, anywhere. Click: a disabled button helps within this view instance, but it is not durable idempotency: a new sheet, a retry after a crash, or a second device are not covered. Click: a real payment API enforces idempotency on the server, with a stable request identifier and authoritative transaction handling. Our demo only models the idea locally.'),
                  ('CONNECT', 'And if the balance changes while the review is open?'))))

S.append(slide("Part 7 &middot; Validate again at confirm time (section 14)", "The review was valid; the payment isn&rsquo;t", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.9fr) 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Experiment", ul("Review ₹1,500.50 (balance ₹25,000)", "While the sheet is open: balance &rarr; <b>₹1,000</b>", "Tap Confirm"))}
        <div class="step">{console("Simulator", ["transactions: 3 (unchanged), paymentsPath: 0", "alert: Payment not recorded", "&ensp;The amount is no longer within your available balance."], 12.5)}</div>
      </div>
      <div class="step">{card("Why it held", ul("<code>recordDemoPayment</code> checks again: <code>amountPaise &lt;= balancePaise</code>", "<code>nil</code> &rarr; no payment, no navigation", "Our onDismiss shows an alert (authored)"))}</div>
      <div class="step">{PHONE("img/failure.png", "Rejected at confirm", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The experiment the text calls particularly important: change the balance while a review is pending. We opened the review for ₹1,500.50 against ₹25,000, then, with the sheet still up, set the balance to ₹1,000 and tapped Confirm.'),
                  ('SAY', 'Click: nothing was recorded and nothing was pushed. Click: the reason: the store validates again inside recordDemoPayment; the earlier validation result, from when the form was filled, is not trusted. It returned nil. Our complete code then remembers the failure and, in onDismiss, shows an alert, the same coordination as success. That alert is ours; the text only requires the re-validation.'),
                  ('SAY', 'Click: the screenshot: the form behind it now says the amount is invalid, because the balance dropped.'),
                  ('CONNECT', 'What happens to state inside the sheet itself?'))))

S.append(slide("Part 7 &middot; Sheet-local @State, and where the draft lives (section 17)", "The sheet&rsquo;s state resets; the draft must not", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("Inside the sheet", "@State private var showDetails = false", "font-size:14px")}
        <div class="step">{console("Simulator: present, Show Details, close, present", ["presented:&ensp;&ensp;&ensp;&ensp;&ensp;Details expanded", "presented again: Details collapsed"], 13)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Why", ul("State belongs to the sheet&rsquo;s view <b>identity</b>", "A new presentation, a new identity: it resets (as 3.1&rsquo;s counter)"))}</div>
        <div class="rule step" data-label="The draft">{ul("Belongs to the payment <b>flow</b>, not the sheet", "Keep it in PaymentsScreen or another owner (3.5)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Suppose the review sheet had its own @State, showDetails. SwiftUI associates that state with the sheet&rsquo;s view identity. Click: our run: present, expand the details, close, present again: collapsed. The state reset with the new presentation, exactly like the counter on a re-pushed screen in 3.1.'),
                  ('SAY', 'Click: that is fine for showDetails. Click: it is not fine for the payment draft. The draft belongs to the payment flow: when the user dismisses the review to edit, the recipient and amount must still be there. That is why they live in PaymentsScreen, as the Edit Details run showed, or in another owner whose lifetime covers the editing workflow. Lesson 3.5 goes deeper.'),
                  ('CONNECT', 'Can we stop the user from swiping the sheet away?'))))

S.append(slide("Part 7 &middot; Prevent accidental dismissal (section 18)", "Lock the swipe while processing; promise nothing more", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {code("PaymentReviewSheet (our placement)", ".presentationDetents([.medium, .large])\n.interactiveDismissDisabled(isProcessing)", "font-size:13.5px")}
        {card("What it does", ul("No swipe-to-dismiss while <code>isProcessing</code>", "Where supported"))}
      </div>
      <div class="warn step" data-label="Not a guarantee">{ul("The sheet can still go away: app lifecycle, system behaviour", "Never a security or transaction guarantee")}</div>
    </div>
  </div>""", notes(('SAY', 'For some workflows we want to prevent swipe-to-dismiss. SwiftUI provides interactiveDismissDisabled. The text applies it from the parent with an isProcessing flag; our complete code keeps isProcessing inside the sheet, from Section 16, so it applies the modifier there, on the sheet&rsquo;s content. While processing, the swipe-down does nothing, where supported.'),
                  ('SAY', 'Click: the nuance: it does not guarantee the presentation can never be dismissed. App lifecycle changes and other system behaviour still exist. Do not use modal presentation state as a security or transaction guarantee; that belongs to the store, and in production to the server.'),
                  ('CONNECT', 'The complete 3.4 app.'))))

# ================================================================== Part 8 (19, 21 + complete code)
divider(8, "NPay after Lesson 3.4", "The complete review flow", 'One sheet, one confirmation, one transaction.', 'Architecture.')
P = [box(0, 0, 520, 54, 'PaymentsScreen', 'owns input and presentation state', None, '', 'file'), wire('M260 56V70' + head(260, 70, 'd')),
     box(0, 74, 520, 54, 'reviewDraft: PaymentDraft?', 'nil &rarr; no sheet &middot; non-nil &rarr; sheet presented', None, 'lit', 'code'), wire('M260 130V144' + head(260, 144, 'd')),
     box(0, 148, 520, 54, 'PaymentReviewSheet', 'temporary modal presentation', None, '', 'eye')]
S.append(slide("Part 8 &middot; How presentation relates to the view hierarchy (section 19)", "A modifier describes a conditional presentation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {svg('0 0 520 202', 'PaymentsScreen owns reviewDraft; nil means no sheet; a draft presents PaymentReviewSheet', 'mod', P, 'max-height:230px')}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The modifier", ul("Declared on a view: <code>.sheet(item: $reviewDraft)</code>", "Non-nil &rarr; SwiftUI presents; nil &rarr; it dismisses"))}
        <div class="step">{card("A new UIWindow per sheet?", ul("No such guarantee in the public API", "Implementation is private and may change"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A sheet is declared as a modifier on a view. The modifier describes a conditional presentation relationship: when the bound item becomes non-nil, SwiftUI coordinates presentation; when it becomes nil, SwiftUI coordinates dismissal. In NPay, PaymentsScreen owns its input and the reviewDraft; the review sheet is a temporary presentation of it.'),
                  ('SAY', 'Click: does sheet always create a new UIWindow? No such guarantee exists in the public SwiftUI API. SwiftUI coordinates presentation through platform infrastructure, and its private implementation may change. Our window count of one is an observation, not a contract.'),
                  ('CONNECT', 'The complete PaymentsScreen.'))))

FULL = """.sheet(item: $reviewDraft, onDismiss: {
    if let id = pendingSuccessID {
        pendingSuccessID = nil
        recipient = ""
        amountText = ""
        router.showPaymentSuccess(id)
    } else if paymentFailed {
        paymentFailed = false
        showFailure = true
    }
}) { draft in
    PaymentReviewSheet(draft: draft) {
        // the store validates again
        if let id = store.recordDemoPayment(
            recipient: draft.recipient,
            amountPaise: draft.amountPaise) {
            pendingSuccessID = id
        } else {
            paymentFailed = true
        }
        reviewDraft = nil
    }
}
.alert("Payment not recorded", isPresented: $showFailure) {
    Button("OK", role: .cancel) {}
} message: {
    Text("The amount is no longer within your available balance.")
}"""
S.append(slide("Part 8 &middot; PaymentsScreen, complete (complete code, authored)", "Success and failure both wait for dismissal", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {code("Screens/PaymentsScreen.swift (presentation)", FULL, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("From the text", ul("<code>reviewDraft</code>, <code>pendingSuccessID</code>, <code>onDismiss</code>", "<code>isProcessing</code> and <code>interactiveDismissDisabled</code> in the sheet"))}
        <div class="step">{card("Ours (authored)", ul("Clear the form on success", "Failure: a flag, then an alert after dismissal", "<code>focusedField = nil</code> before review"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text described a ZIP of the complete code that we did not receive, so we assembled it from the text&rsquo;s sections on top of 3.3; it is in the lesson text file and ran unchanged in the simulator. The presentation part of PaymentsScreen: the sheet with onDismiss, and the confirmation closure.'),
                  ('SAY', 'From the text: reviewDraft, the pending success ID and navigation in onDismiss; in the sheet, the isProcessing guard and interactiveDismissDisabled. Click: our additions: on success the form is cleared, since the tab stays alive; on failure, a flag set during confirm and an alert shown in onDismiss, so even the error waits for the sheet to go; and the keyboard is dismissed before the review opens.'),
                  ('CONNECT', 'Run it.'))))

S.append(slide("Part 8 &middot; The flow, run (complete code)", "₹1,500.50 to ravi@npay, reviewed", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;align-items:start">
      {PHONE("img/typed.png", "1. Form", 150)}
      <div class="step">{PHONE("img/review.png", "2. Review", 150)}</div>
      <div class="step">{PHONE("img/success.png", "3. Confirm &rarr; Success", 150)}</div>
      <div class="step">{PHONE("img/home.png", "4. Home: ₹23,499.50", 150)}</div>
      <div class="step">{PHONE("img/history.png", "5. History", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The flow in the simulator. The Payments form with ravi@npay and 1500.50; the button now says Review Payment.'),
                  ('SAY', 'Click: the review sheet at medium height. Click: Confirm Demo Payment: the sheet dismisses, and then the router pushes Payment Success, inside the Payments tab. Click: Back to Dashboard: Home shows ₹23,499.50. Click: History has "Sent to ravi@npay", minus ₹1,500.50, on top. One transaction.'),
                  ('CONNECT', 'The text&rsquo;s checklist.'))))

CK = [("Open Payments; ravi@npay, ₹1,500.50", "typed"), ("Review Payment: the native sheet", "Recipient ravi@npay, Amount ₹1,500.50"),
      ("Dismiss: the form keeps its input", "after swipe down: \"ravi@npay\", \"1500.50\""), ("Reopen; confirm", "recorded once"),
      ("Automatic navigation to Payment Success", "after the sheet is gone"), ("Home: balance ₹23,499.50", "₹23,499.50"),
      ("History: the new transaction", "Sent to ravi@npay, -₹1,500.50"), ("Invalid amounts, insufficient balance", "0, 12.345, 30000: Review disabled")]
S.append(slide("Part 8 &middot; Lab verification checklist (complete code)", "Eight checks, all run", f"""  <div class="body">
    {tbl(["Check", "Simulator"], CK)}
    <p class="small muted" style="margin:6px 0 0">Plus the Section 14 experiments: swipe down, Edit Details, re-review, confirm, balance changed while reviewing (Part 7).</p>
  </div>""", notes(('SAY', 'The text&rsquo;s eight-item lab checklist, all run. Typed ravi@npay and 1500.50. Review Payment showed the native sheet with both values. A swipe down dismissed it and the form kept its input. Reopened and confirmed: recorded once. Navigation to Payment Success happened after the sheet was gone. Home shows ₹23,499.50; History shows the new transaction. And 0, 12.345 and ₹30,000, above the balance, all keep Review Payment disabled.'),
                  ('SAY', 'The Section 14 experiment table is covered too: swipe down, Edit Details, changing the amount and reopening, confirming, and the balance changing while the review was pending.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.4', (), [("layers", "Presentation is state", "a Bool or an optional item; dismissal writes it back"),
                     ("clock", "Dismiss, then navigate", "pending ID + onDismiss; never a fixed delay"),
                     ("shield", "Confirm once, validate again", "guard the button; the store re-checks; servers enforce")],
         'Three things to remember. A sheet, cover, alert or dialog is driven by state: a Bool or an optional item, which SwiftUI writes back when the presentation is dismissed; choose sheets for temporary tasks and navigation for going deeper. Coordinate transitions with the presentation lifecycle: keep the result pending and navigate in onDismiss, never after a guessed delay. And protect the money: guard Confirm against double taps, validate again in the store at confirm time, and remember that real idempotency is enforced by the server.')

review_divider(9)
review([("clock", "Choose one", "Why use onDismiss before navigating to success?",
         "Why use the sheet&rsquo;s <code>onDismiss</code> before navigating to success?<br>A. To persist the payment<br>B. To coordinate presentation and navigation transitions<br>C. To create a new process", "B",
         "The path changed only once the sheet was gone.",
         "Navigating in the same update as the dismissal.", "Most pick B.", None),
        ("shield", "Question", "Does disabling Confirm guarantee idempotency?",
         "Does disabling the Confirm button guarantee financial idempotency?", "No",
         "It protects one view instance; idempotency is enforced by the server.",
         "Treating a UI guard as a business rule.", "Some say yes.", None),
        ("file", "Choose one", "Where should a draft live to survive dismissal?",
         "Where should an editable payment draft live if it must survive sheet dismissal?<br>A. Only inside the sheet<br>B. In a state owner outside the temporary sheet", "B",
         "After Edit Details, PaymentsScreen still held ravi@npay and 1500.50.",
         "Putting the draft in the sheet&rsquo;s @State.", "Most pick B.", None),
        ("code", "Choose one", "What does sheet(item:) use to decide to present?",
         "What does <code>sheet(item:)</code> use to decide whether to present?<br>A. A navigation path<br>B. A network response only<br>C. An optional Identifiable item", "C",
         "nil: no sheet; a value: the sheet, showing that value.",
         "Keeping a Bool and an optional in sync.", "Most pick C.", None),
        ("eye", "Question", "Does interactiveDismissDisabled guarantee the sheet stays?",
         "Does <code>interactiveDismissDisabled</code> guarantee that the app can never dismiss the sheet?", "No",
         "It blocks the swipe; lifecycle and system behaviour still apply.",
         "Using presentation as a guarantee.", "Most say no.", None),
        ("db", "Question", "Should payment processing live in PaymentReviewSheet?",
         "Should payment processing live inside <code>PaymentReviewSheet</code>?", "No",
         "The sheet shows a draft and calls <code>onConfirm</code>; the store records.",
         "Letting a temporary view own the money.", "Most say no.", None),
        ("diff", "Predict the result", "Confirm fires twice with no guard?",
         "A Confirm button without <code>isProcessing</code> records ₹1,500.50 and sets <code>reviewDraft = nil</code>. It is activated twice before the sheet closes. How many transactions?<br>A. One: the sheet closed<br>B. Two<br>C. None", "B",
         "Our run: 3 &rarr; 5 transactions, ₹21,999.00.",
         "Assuming dismissal is instant.", "Some pick A.", None),
        ("key", "Predict the result", "Balance drops while the review is open?",
         "The review shows ₹1,500.50; while it is open the balance drops to ₹1,000. The user confirms. What happens?<br>A. ₹1,500.50 is recorded<br>B. Nothing is recorded; the user is told<br>C. The app crashes", "B",
         "The store re-validated: nil, no navigation, an alert.",
         "Trusting the earlier validation.", "Some pick A.", None),
        ("grid", "Choose one", "From 3.3: who navigates after a payment?",
         "From Lesson 3.3: after a payment is recorded, which object pushes Payment Success?<br>A. <code>NPayStore</code><br>B. <code>NPayRouter</code><br>C. <code>PaymentReviewSheet</code>", "B",
         "The store records; the router decides where the user goes.",
         "Letting the store navigate.", "Most pick B.", "Spaced review from Lesson 3.3.")])

S.append(next_slide('3.4', [("3.5", "State preservation across navigation", "payment drafts across tabs, sheets and pushes"),
                            ("Unit 5", "HTTP, REST &amp; idempotency", "server-enforced idempotency with request IDs"),
                            ("Unit 4", "Application architecture", "presentation state in view models; testable flows")],
                    'Lesson 3.5 preserves payment drafts when switching tabs, dismissing sheets or navigating, and shows how to avoid accidental resets. Unit 5 returns to idempotency where it really lives, in HTTP APIs with stable request identifiers. Unit 4 moves presentation and flow state into view models you can test.'))

S.append(lab_slide('3.4', "Review before paying", "Add the review sheet to the 3.3 project; verify, then break it.",
                   ["Add PaymentDraft and PaymentReviewSheet.",
                    "Present with <code>sheet(item:)</code>; navigate in <code>onDismiss</code>.",
                    "Run the 8-item checklist with ₹1,500.50.",
                    "Remove the <code>isProcessing</code> guard; tap Confirm fast.",
                    "Lower the balance while reviewing; confirm.",
                    "Try an alert and a confirmationDialog."],
                   "", 'Expected, as in our run: the sheet shows ravi@npay and ₹1,500.50; swipe down keeps the form; Confirm leads to Payment Success after the sheet closes; Home ₹23,499.50; History has the transaction; without the guard a fast double confirm can record twice; a lowered balance makes the store reject the payment.',
                   side=f'<div>{card("You hand in", ul("Your completed checklist", "Your double-tap result, with and without the guard", "One sentence: UI protection vs idempotency"))}</div>'))

end_slide('3.4', 'Sheets, Alerts &amp;<br>Modal Presentation', 'Lesson 3.5 &mdash; State Preservation Across Navigation',
          'You can now drive sheets, covers, alerts and dialogs from state, choose between presentation and navigation, review a payment with sheet(item:), navigate after dismissal with onDismiss, guard Confirm against double taps, re-validate at confirm time, and explain what sheet-local state and dismiss-locking really guarantee.',
          'Next, Lesson 3.5: state preservation across navigation. We keep payment drafts alive across tab switches, sheet dismissals and navigation changes.')

write_deck(OUT34, '3.4', 'Sheets &amp; Alerts', 'Sheets &amp; Alerts')
