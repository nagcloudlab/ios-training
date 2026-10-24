"""Generates decks/unit-2/lesson-2.7/index.html from the Lesson 2.7 text (SwiftUI Button, Closures & Event Handling).
The text came in two parts (Sections 1-13, 14-21), grouped into 8 Parts. Console output and screenshots come from
tools/sim2_7 (a scripted SwiftUI app run in the iOS Simulator; buttons are activated through their accessibility
elements, which runs the real Button action); the capture demo was run with swiftc on the Mac."""
import html, os, re, sys
OUT27 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.7', 'SwiftUI Button, Closures<br>&amp; Event Handling',
            'A user touches <b>Send</b>. How does iOS know which <b>Swift closure</b> to run?',
            'Until now NPay has been static: a header, a balance card and three quick actions. Today it becomes interactive. We follow a tap from the screen to a Swift closure, see when a button&rsquo;s closure runs and when it does not, look at hit testing, styles and accessibility, and turn QuickAction into a reusable button. Everything printed today came from the iOS Simulator; we activated the buttons through accessibility, the same path VoiceOver uses.')
outcomes_slide('2.7', [("code", "<code>Button</code>&rsquo;s initializers and its <b>action closure</b>"),
                       ("diff", "Why evaluating <code>body</code> doesn&rsquo;t <b>run</b> the action"),
                       ("tap", "The path from a <b>tap</b> to your closure"),
                       ("frame", "Hit testing, <code>contentShape</code>, styles, <b>disabled</b>"),
                       ("link", "A reusable button that takes a <b>closure</b>"),
                       ("clock", "Captures, ARC and a <b>responsive</b> main thread")])
where_slide('2.7', 'Today: NPay responds', (),
            '2.6: reusable <code>BalanceCard</code> and <code>QuickAction</code>, still static.',
            'Buttons: the quick actions run closures.',
            'Last lesson NPay got reusable, styled components, but nothing responds to a tap. Today the quick actions become buttons. They only print for now; 2.8 makes them change what is on screen.',
            'The milestone.')

# ================================================================== Part 1 (1)
divider(1, "The milestone", "Quick actions that respond", 'Same screen; now the actions do something.', 'Before and after.')
S.append(slide("Part 1 &middot; Our next NPay milestone (sections 1, 21)", "Milestone 2.7: three working quick actions", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Today", ul("Send, Request, History become <b>buttons</b>", "Each runs a <b>closure</b> from ContentView"))}
        {card("Not yet", ul("Actions <b>print</b>; the balance stays ₹25,000", "Changing the screen: <b>2.8</b>, @State"))}
      </div>
      {PHONE("img/before.png", "Before: Lesson 2.6", 190)}
      <div class="step">{PHONE("img/final.png", "After: Milestone 2.7", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'NPay so far: header, balance card, three quick actions that do nothing when tapped. Click: today they become buttons. The difference on screen is small, tighter spacing and taller tiles, but each one now runs a closure supplied by ContentView.'),
                  ('SAY', 'For this lesson the actions only print to the console, and the balance stays a hard-coded ₹25,000 on purpose. Lesson 2.8 replaces it with state.'),
                  ('CONNECT', 'Start with the simplest button.'))))

# ================================================================== Part 2 (2, 7)
divider(2, "Button", "A struct with a closure", 'Button("Send Money") { … }: what is each part?', 'Read the API.')
BASIC = """Button("Send Money") {
    print("Send Money tapped")
}"""
INIT = """init(
    _ titleKey: LocalizedStringKey,
    action: @escaping () -> Void
)"""
PARTS = [("<code>Button</code>", "a generic SwiftUI struct"), ("<code>\"Send Money\"</code>", "the title"), ("<code>{ … }</code>", "trailing <b>action closure</b>"),
         ("<code>@escaping</code>", "<b>kept</b> after init returns"), ("<code>() -&gt; Void</code>", "no arguments, no result")]
S.append(slide("Part 2 &middot; Understand Button (section 2)", "A title and an escaping action", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", BASIC, "font-size:17px")}
        <div class="gap"></div>
        {code("Simplified initializer", INIT, "font-size:15px")}</div>
      <div>{tbl(["Part", "Meaning"], PARTS, 'tbl')}
        <div class="rule step" data-label="Unit 01" style="margin-top:12px">{ul("A closure is a value: store it, call it later", "Button stores one; calls it <b>when activated</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'The simplest button: a title and a trailing closure. A simplified form of the initializer it calls: a localized title key, and an action of type escaping closure taking nothing and returning Void. SwiftUI has several Button initializers; we meet the custom-label one next.'),
                  ('SAY', 'The parts: Button, a generic struct; the title; the trailing action closure; @escaping, because the button keeps the closure after the initializer has returned; and () -> Void, no arguments and no result.'),
                  ('SAY', 'Click: closures as values, from Unit 01. You can store a closure in a constant and call it later. A Button does exactly that: it stores the closure and calls it when the button is activated.'),
                  ('CONNECT', 'The second initializer lets you design the label.'))))

CL = """Button {
    print("Send tapped")
} label: {
    VStack(spacing: 8) {
        Image(systemName: "arrow.up.right")
        Text("Send")
    }
}"""
S.append(slide("Part 2 &middot; A custom label (section 7)", "Two closures: action and label", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", CL, "font-size:16px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Two closures", ul("<code>action</code>: what happens", "<code>label</code>: what it looks like, a <code>@ViewBuilder</code>"))}
        <div class="step">{console("type(of:) in the simulator", ["Button(\"Send Money\") { … }:", "  Button&lt;Text&gt;", "Button { … } label: { VStack … }:", "  Button&lt;VStack&lt;TupleView&lt;(Image, Text)&gt;&gt;&gt;"], 13)}</div>
        <div class="rule step" data-label="Generics">{ul("<code>Button&lt;Label&gt;</code>: Swift infers <code>Label</code> from the closure")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The second initializer takes two closures: the action, what happens when it is activated, and the label, what the button looks like. The label closure is a @ViewBuilder, like a stack&rsquo;s content in 2.3, so it can hold an icon over a text.'),
                  ('SAY', 'Click: the printed types. With a string title, Button of Text. With our label, Button of VStack of TupleView of Image and Text. Click: Button is generic over its label type, and Swift infers that type from the label closure: generics again.'),
                  ('CONNECT', 'So when does the action closure actually run?'))))

# ================================================================== Part 3 (3)
divider(3, "Creation vs activation", "body runs; the action waits", 'If body is evaluated ten times, does the action run ten times?', 'We counted.')
PV = """struct PaymentView: View {
    let tick: Int
    var body: some View {
        let _ = print("PaymentView.body evaluated (tick \\(tick))")
        Button("Send Money") {
            print("Payment requested")
        }
    }
}"""
CA = [("code", "body evaluated", "SwiftUI gets a Button description"), ("link", "Closure stored", "inside that description, not called"),
      ("diff", "body evaluated again", "a new description, a new closure"), ("tap", "User activates the button", "a separate event"), ("check", "The action runs", "once per activation")]
P = [box(0, i * 52, 520, 44, t, sub, str(i + 1) if i < 4 else '5+', '', ic) for i, (ic, t, sub) in enumerate(CA)]
S.append(slide("Part 3 &middot; Does the closure run when body runs? (section 3)", "Evaluation is not activation", f"""  <div class="body">
    {cues(5)}
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      <div>{code("PaymentView.swift", PV, "font-size:13px")}
        <div class="step" style="margin-top:10px">{console("Parent changed 3 times, no tap", ["PaymentView.body evaluated (tick 0)", "… (tick 1) … (tick 2) … (tick 3)", "\"Payment requested\": never printed"], 13)}</div></div>
      {svg('0 0 520 252', 'Body evaluated, closure stored, body evaluated again, user activates, action runs', 'ca', P, 'max-height:280px')}
    </div>
  </div>""", notes(('SAY', 'A PaymentView with a print in its body and a button. We made its parent change three times, which makes SwiftUI evaluate the body again, and never activated the button. Click: body evaluated. Click: the description contains the action closure, stored, not called. Click: body evaluated again: a new description with a new closure.'),
                  ('SAY', 'The console: body evaluated four times, tick 0 to 3, and "Payment requested" never printed. Click: the action runs only when the user activates the button, a separate event. Click: and then once per activation.'),
                  ('SAY', 'So if SwiftUI re-evaluates body ten times, the action runs zero times. View evaluation and user activation are separate events. That is also why it is safe to create closures in body.'),
                  ('CONNECT', 'Now the activation itself: from a finger to your closure.'))))

# ================================================================== Part 4 (4, 13, 17)
divider(4, "From tap to closure", "The event path", 'A finger touches glass. Your closure runs. What happens in between?', 'The pipeline.')
PIPE = [("phone", "Finger touches the screen", "hardware detects touch"), ("kernel", "iOS input handling", "the system processes and routes it"),
        ("process", "Delivered to the app", "the running NPay process"), ("frame", "Hit testing", "the interactive control is identified"),
        ("tap", "SwiftUI Button activation", "the framework recognises it"), ("check", "Your action closure runs", "on the main actor")]
P = [box(0, i * 52, 600, 44, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(PIPE)]
S.append(slide("Part 4 &middot; From finger tap to Swift closure (section 4) &middot; conceptual", "Six steps from glass to code", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:28px;align-items:center">
      {svg('0 0 600 304', 'Finger touches the screen, iOS input handling, delivery to the app, hit testing, Button activation, the action closure runs', 'tap', P, 'max-height:330px')}
      <div class="rule step" data-label="Main thread (0.5)">{ul("UI interactions run on the <b>main actor</b>", "Keep actions <b>short</b>")}</div>
    </div>
  </div>""", notes(('SAY', 'Connect to Unit 00&rsquo;s main thread and RunLoop. Click: a finger touches the screen and the hardware detects it. Click: iOS&rsquo;s input infrastructure processes and routes the input. Click: the event reaches the running NPay process. Click: hit testing identifies the interactive control under the finger. Click: SwiftUI recognises a button activation. Click: your action closure runs.'),
                  ('SAY', 'This is conceptual: Apple does not publish the exact routing or SwiftUI&rsquo;s internals. Click: one thing we can rely on: SwiftUI handles UI interactions on the main actor, so actions must stay short. Part 8 shows what happens when they are not.'),
                  ('CONNECT', 'We can see the last steps for real, in a call stack.'))))

STK = ["Send tapped", "main thread: true", "", "0  closure #1 in StackView.body.getter", "2  static MainActor.assumeIsolated(…)", "3  ButtonAction.callAsFunction()",
       "4  … AccessibilityButtonModifier.init(_:)", "…", "12 AccessibilityNode.accessibilityActivate()", "13 activate(_:)   ← our test code"]
S.append(slide("Part 4 &middot; Inspect the call stack (sections 13, 17)", "Inside the existing process, on the main thread", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:28px;align-items:start">
      <div>{console("Inside the Send action: Thread.callStackSymbols (selected)", STK, 13)}
        <p class="small muted" style="margin:8px 0 0">Activated through accessibility, as VoiceOver does; a finger tap shows touch and gesture frames lower down. Frames vary by iOS version.</p></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("In Xcode", ul("Breakpoint on <code>print(\"Send tapped\")</code>", "<b>⌘R</b>, tap Send, <b>⌘7</b> for the stack", "LLDB: <code>bt</code>, <code>thread list</code>"))}
        <div class="rule step" data-label="Observe">{ul("Your closure, called by SwiftUI&rsquo;s <code>ButtonAction</code>", "Same process: nothing rebuilt, nothing relaunched")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s debugging lab: set a breakpoint on print("Send tapped"), run, tap Send, open the Debug navigator with Command-7, and type bt and thread list in the console. We did the equivalent inside the action: printed whether we are on the main thread and the call stack.'),
                  ('SAY', 'Main thread: true. At the top of the stack, frame 0, our closure. Just below it, SwiftUI&rsquo;s ButtonAction.callAsFunction, run with MainActor.assumeIsolated. Lower down, the activation entered through the accessibility node, because our script activated the button the way VoiceOver does; a real finger tap would show touch and gesture-recognition frames there instead. The exact frames depend on the iOS version.'),
                  ('SAY', 'Click: what to observe: your closure, called by SwiftUI&rsquo;s button machinery, inside the same running process. Tapping Send does not rebuild or relaunch NPay.'),
                  ('CONNECT', 'Step 4 of the pipeline was hit testing. What is that?'))))

# ================================================================== Part 5 (5, 6)
divider(5, "Hit testing", "Which view gets the tap?", 'A point on the screen. Which control responds?', 'Interaction regions.')
CS = """Button {
    print("Send tapped")
} label: {
    HStack {
        Image(systemName: "arrow.up.right")
        Text("Send")
    }
    .frame(maxWidth: .infinity)
    .padding()
    .contentShape(Rectangle())
}"""
S.append(slide("Part 5 &middot; Hit testing and contentShape (sections 5&ndash;6)", "Make the whole tile tappable", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", CS, "font-size:14px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Hit testing", ul("Finds the <b>interactive view</b> at the touch point", "Uses the hierarchy and <b>interaction regions</b>"))}
        <div class="step">{card("Looks ≠ responds", ul("Empty or transparent parts of a label may <b>not</b> respond", "<code>.contentShape(Rectangle())</code>: the whole rectangle"))}</div>
        <div class="step">{console("NPay&rsquo;s tiles, accessibility frames", ["Send 115 × 72 · Request 115 × 72 · History 115 × 78 pt"], 13)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'When the user taps a point, hit testing determines which interactive view corresponds to that location, using the view hierarchy and each view&rsquo;s interaction region. The text&rsquo;s widget showed a tap landing on History.'),
                  ('SAY', 'Click: a view&rsquo;s appearance and its hit region are related but not identical. A custom label with empty space, like this HStack stretched to full width, may not respond in its empty parts. .contentShape(Rectangle()) declares the whole rectangle as the interaction shape, so the region matches the tile you drew.'),
                  ('SAY', 'Click: NPay&rsquo;s quick actions use it. The accessibility frames of the three tiles: about 115 by 72 points each, comfortably above the 44 by 44 guideline from Section 19. We could not script real finger taps in this setup, so hit testing itself is shown, not measured; try tapping the tile edges in your own simulator.'),
                  ('CONNECT', 'Next: how a button looks and whether it can be used at all.'))))

# ================================================================== Part 6 (8, 9, 19)
divider(6, "Styles, disabled, accessibility", "Presentation and access", 'Same button, different presentation, and sometimes unavailable.', 'Styles first.')
S.append(slide("Part 6 &middot; Button styles (section 8)", "<code>.plain</code>, <code>.bordered</code>, <code>.borderedProminent</code>", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 320px;gap:28px;align-items:start">
      <div>{code("ContentView.swift", 'Button("Send Money") {\n    print("Tapped")\n}\n.buttonStyle(.borderedProminent)', "font-size:16px")}
        <div class="gap"></div>
        <div class="rule step" data-label="Not just colour">{ul("Feedback, emphasis, shape", "Adapts to environment and state")}</div></div>
      {crop("img/styles.png", SIM, 320)}
    </div>
  </div>""", notes(('SAY', '.buttonStyle changes how a button is presented. On the right, the three common built-in styles in the iOS 26.5 simulator, plain, bordered and borderedProminent, plus a disabled prominent button; the exact look varies by OS version, environment and state.'),
                  ('SAY', 'Click: styles are not colour presets. They also define interaction feedback, visual emphasis and shape, and they adapt to the environment, such as dark mode or the disabled state you see at the bottom.'),
                  ('CONNECT', 'That disabled state deserves its own slide.'))))

DIS = """Button("Send Money") {
    print("Send requested")
}
.disabled(true)

Button {
    print("Send requested")
} label: {
    Image(systemName: "arrow.up.right")
}
.accessibilityLabel("Send money")"""
S.append(slide("Part 6 &middot; Disabled state and accessibility (sections 9, 19)", "Say it&rsquo;s unavailable; say what it does", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", DIS, "font-size:14px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Activated both, in the simulator", ["Send Money: button, enabled: false", "  → nothing printed", "Request Money: button, enabled: true", "  → Request requested"], 13)}</div>
        {card("Why .disabled", ul("Better than ignoring taps in the action", "Changes <b>look</b> and <b>accessibility</b>"))}
        <div class="step">{card("Labels", ul("Icon only? Add <code>.accessibilityLabel</code>", "Text labels are clearer: an arrow could mean Send, Upload, Share", "Touch targets: about <b>44 × 44 pt</b> or larger"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Until the user enters a valid amount, Send should be disabled. .disabled(true) says the control is unavailable. Click: we activated a disabled Send Money button and an enabled Request Money button: accessibility reported Send as a button that is not enabled, and nothing ran; Request ran its action.'),
                  ('SAY', 'That is why .disabled beats silently ignoring taps inside the action: the button looks unavailable, and VoiceOver announces it as dimmed.'),
                  ('SAY', 'Click: accessibility labels. An icon-only button needs .accessibilityLabel so VoiceOver can say what it does. Our quick actions have text labels, which helps everyone: an arrow alone could mean Send, Transfer, Upload or Share. Apple&rsquo;s guidance suggests touch targets of about 44 by 44 points or larger; our tiles measured about 115 by 72.'),
                  ('CONNECT', 'Now make QuickAction a real, reusable button.'))))

# ================================================================== Part 7 (10-12, 14-15)
divider(7, "QuickAction as a button", "The parent supplies behaviour", 'One reusable view, three behaviours.', 'The new QuickAction.')
QA = """struct QuickAction: View {
    let symbol: String
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                Image(systemName: symbol)
                    .font(.title2)
                Text(title)
                    .font(.caption)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
            .contentShape(Rectangle())
        }
        .buttonStyle(.plain)
        .foregroundStyle(.blue)
        .background(Color.blue.opacity(0.08),
                    in: RoundedRectangle(cornerRadius: 12))
    }
}"""
S.append(slide("Part 7 &middot; Interactive quick actions (section 10)", "QuickAction stores a closure", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:28px;align-items:start">
      {code("QuickAction.swift", QA, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("New", ul("<code>let action: () -&gt; Void</code>, a <b>closure property</b>", "<code>Button(action: action)</code> uses it"))}
        <div class="step">{console("type(of: quickAction.action)", ["() -&gt; ()"], 14)}</div>
        <div class="rule step" data-label="Ownership">{ul("A stored closure can <b>capture</b> objects", "ARC matters when it captures models (Part 8)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'QuickAction gets a third property: let action: () -> Void, a closure property. Its body wraps the old icon-over-label VStack in Button(action: action): the label is the tile, and contentShape makes the whole tile tappable. .buttonStyle(.plain) keeps our own look instead of the system style.'),
                  ('SAY', 'Click: we printed the stored property&rsquo;s type: () -> (), Swift&rsquo;s spelling of () -> Void. A closure value, not a function name and not an event object.'),
                  ('SAY', 'Click: because QuickAction stores the closure, the closure can capture other objects and keep them alive. Today the actions only print, so nothing is captured; when they start capturing ViewModels and services, ARC matters. Part 8.'),
                  ('CONNECT', 'ContentView supplies the three closures.'))))

ROW = """HStack(spacing: 12) {
    QuickAction(symbol: "arrow.up.right",
                title: "Send") {
        print("Send tapped")
    }
    QuickAction(symbol: "arrow.down.left",
                title: "Request") {
        print("Request tapped")
    }
    QuickAction(symbol: "clock",
                title: "History") {
        print("History tapped")
    }
}"""
FLOW = [("phone", "ContentView", "defines the Send closure"), ("code", "QuickAction init", "receives it as an argument"), ("link", "QuickAction.action", "stores the closure value"),
        ("tap", "Button(action: action)", "its activation handler"), ("check", "Activated", "print(\"Send tapped\") runs")]
P = [box(0, i * 52, 480, 44, t, sub, str(i + 1) if i < 4 else '5+', '', ic) for i, (ic, t, sub) in enumerate(FLOW)]
S.append(slide("Part 7 &middot; Who owns the action? (sections 11&ndash;12, 14&ndash;15)", "Follow the Send closure", f"""  <div class="body">
    {cues(5)}
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:24px;align-items:start">
      <div>{code("ContentView.swift (the row)", ROW, "font-size:12.5px")}
        <div class="step" style="margin-top:10px">{console("All three activated", ["Send tapped", "Request tapped", "History tapped"], 13)}</div></div>
      <div>{svg('0 0 480 252', 'ContentView defines the closure, the initializer receives it, QuickAction stores it, Button uses it, activation runs it', 'own', P, 'max-height:280px')}
        <div class="rule step" data-label="Separation" style="margin-top:10px">{ul("QuickAction: <b>how</b> it looks and is triggered", "ContentView: <b>what</b> it means")}</div></div>
    </div>
  </div>""", notes(('SAY', 'ContentView&rsquo;s new row: three QuickActions, each with a trailing closure. Follow Send&rsquo;s closure. Click: ContentView defines it. Click: QuickAction&rsquo;s initializer receives it as an argument. Click: QuickAction stores it in action. Click: inside body, Button(action: action) makes it the activation handler. Click: when the button is activated, print("Send tapped") runs.'),
                  ('SAY', 'We activated all three tiles in the simulator: Send tapped, Request tapped, History tapped. One reusable view, three behaviours; that is the lab&rsquo;s verification step.'),
                  ('SAY', 'Click: why this is good architecture. QuickAction does not know about payments, history or navigation; it knows how to look and how to call its closure. The parent decides what the action means. That separation is the seed of MVVM and dependency injection later.'),
                  ('CONNECT', 'Two risks come with closures in buttons: lifetimes and blocking.'))))

# ================================================================== Part 8 (16, 18)
divider(8, "Captures and responsiveness", "Lifetimes and the main thread", 'What can a stored closure keep alive, and what can a slow one freeze?', 'Captures first.')
CAP = """final class PaymentService {
    func send() { print("Sending payment") }
    deinit { print("PaymentService deinit") }
}

var service: PaymentService? = PaymentService()
var action: (() -> Void)? = { [service] in service?.send() }

service = nil
print("service variable set to nil")
action?()
action = nil
print("closure released")"""
S.append(slide("Part 8 &middot; Closure capture and ARC (section 16)", "A closure can keep an object alive", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:28px;align-items:start">
      <div>{code("Capture.swift (Mac, swiftc)", CAP, "font-size:13px")}
        <div class="step" style="margin-top:10px">{console("Output", ["service variable set to nil", "Sending payment", "PaymentService deinit", "closure released"], 13)}</div></div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Every capture a cycle?", ul("<b>No</b>: a cycle needs a strong <b>loop</b>", "e.g. a service storing a closure that captures that service"))}</div>
        <div class="rule step" data-label="[weak self] everywhere?">{ul("No: decide from <b>ownership</b> (1.8)", "Today&rsquo;s actions only print")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s PaymentService example, made observable: a deinit that prints, a closure that captures the service, then we drop our own variable. Click: we compiled and ran it on a Mac. Setting the variable to nil did not free the service: the closure still held it and could still send a payment. The service was freed only when the closure was released. A stored closure can extend the lifetime of what it captures.'),
                  ('SAY', 'Click: does every button closure cause a retain cycle? No. A cycle needs a strong loop, for example a service that stores a closure which strongly captures that same service, as in Lesson 1.8.'),
                  ('SAY', 'Click: so should every SwiftUI action say [weak self]? No. Decide from the ownership relationships; weak references everywhere are not a substitute for understanding lifetimes. Our current actions only call print, so there is nothing to worry about yet.'),
                  ('CONNECT', 'The other risk: a slow action.'))))

BL = """Button("Send") {
    Thread.sleep(forTimeInterval: 3)
    print("Finished")
}"""
S.append(slide("Part 8 &middot; Keep actions responsive (section 18)", "A 3-second action freezes the main thread", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Deliberately bad", BL, "font-size:16px")}
        <div class="gap"></div>
        {code("Later: the structure for async work", 'Button("Send") {\n    Task {\n        // call an async payment service\n    }\n}', "font-size:14px")}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("A main-thread timer, every 0.5 s", ["fired at 0.5 · 1.0 · 1.5 secs", "→ Send activated", "Finished", "fired at 4.6 · 5.0 · 5.5 secs"], 13)}</div>
        <div class="rule step" data-label="Silent for 3 s">{ul("No timer, no events, no frames (0.5)", "<code>Task</code> alone doesn&rsquo;t make CPU work safe (1.9)")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A deliberately bad action: sleep three seconds on the main thread, then print. We ran a repeating timer on the main thread, firing every half second, and activated the button at 1.5 seconds.'),
                  ('SAY', 'Click: the timer fired at 0.5, 1.0 and 1.5 seconds, then nothing until 4.6. Three seconds of silence: while the action blocked the main thread, no timer, no touch handling and no new frames, the RunLoop story from Lesson 0.5.'),
                  ('SAY', 'Click: the direction for later: when Send calls a real payment service, the action will start a Task and await an asynchronous service. Only the structure for now. Creating a Task does not by itself make synchronous CPU-heavy work safe on the main actor, as 1.9 measured. Networking and concurrency units come back to this.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.7', (), [("link", "A button stores a closure", "body creates it; activation runs it"),
                     ("tap", "Tap → hit test → action", "on the main actor, in the same process"),
                     ("layers", "Views show, parents decide", "QuickAction takes its action as a closure")],
         'Three things to remember. A Button stores an escaping closure: evaluating body creates it, only activation runs it. A tap travels through iOS, hit testing and SwiftUI&rsquo;s button handling to your closure, on the main actor, inside the running app, so keep actions short. And a reusable view like QuickAction shows and triggers; its parent supplies what the action means.')

review_divider(8)
review([("tap", "Choose one", "When does a Button's action closure execute?",
         "When does a <code>Button</code>&rsquo;s action closure execute?<br>A. Every time <code>body</code> is evaluated<br>B. When the button is activated<br>C. During compilation", "B",
         "body ran four times and &ldquo;Payment requested&rdquo; never printed; activation ran it.",
         "Thinking body &ldquo;runs&rdquo; the button.", "Some pick A.", None),
        ("link", "Choose one", "What does QuickAction store?",
         "What does <code>QuickAction</code> store in <code>action</code>?<br>A. A function name as a <code>String</code><br>B. A closure value<br>C. A UIKit event object", "B",
         "<code>type(of: quickAction.action)</code> printed <code>() -&gt; ()</code>.",
         "Expecting a selector or event, as in older APIs.", "Some pick A.", None),
        ("diff", "Question", "Does every captured reference create a retain cycle?",
         "Does every captured reference automatically create a retain cycle?", "No",
         "A cycle needs a strong loop; our capture only delayed the service&rsquo;s deinit until the closure was released.",
         "Adding [weak self] everywhere.", "Some say yes.", None),
        ("clock", "Question", "Should long synchronous work run in a button action on the main thread?",
         "Should long synchronous work run directly in a button action on the main thread?", "No",
         "A 3-second sleep stopped a main-thread timer from 1.5 s to 4.6 s.",
         "Assuming actions run in the background.", "Some say it is fine.", None),
        ("frame", "Choose one", "What is hit testing?",
         "What is hit testing?<br>A. Finding the tapped interactive view<br>B. Compiling the button<br>C. Measuring network latency", "A",
         "It maps a touch location to the view that should respond, using interaction regions.",
         "Confusing the name with testing.", "Most pick A.", None),
        ("layers", "Choose one", "Why use a reusable QuickAction?",
         "Why make <code>QuickAction</code> a reusable component with an action closure?<br>A. To separate presentation from behaviour<br>B. To create a separate process<br>C. To avoid Swift closures", "A",
         "QuickAction shows and triggers; ContentView decides what Send means.",
         "Putting behaviour inside the component.", "Most pick A.", None),
        ("eye", "Predict the result", "body evaluated 4 times, no tap: how many \"Payment requested\"?",
         "<code>PaymentView.body</code> is evaluated 4 times and nobody taps. How many times does <code>print(\"Payment requested\")</code> run?<br>A. 0<br>B. 1<br>C. 4", "A",
         "Measured: zero. Evaluation and activation are separate events.",
         "Counting body evaluations as taps.", "Some pick C.", None),
        ("code", "Question", "From 2.6: does a modifier mutate the original view?",
         "From Lesson 2.6: does <code>.buttonStyle(.plain)</code> mutate the <code>Button</code> it is applied to?", "No",
         "Like every modifier, it returns a new view description.",
         "Picturing a mutable button object.", "Some say yes.", "Spaced review from Lesson 2.6.")])

S.append(next_slide('2.7', [("2.8", "@State and reactive UI", "the Add Money button changes the balance from ₹25,000 to ₹26,000"),
                            ("Later", "Async actions", "Task and an asynchronous payment service")],
                    'Next lesson replaces the hard-coded balance with SwiftUI-managed state, so a button visibly changes NPay: property wrappers, value semantics, identity, state storage and updates. Asynchronous actions come with the networking and concurrency units.'))

S.append(lab_slide('2.7', "Trace a real tap", "Verify the three actions and catch Send in the debugger.",
                   ["Build the Section 14 code; tap each action.",
                    "Breakpoint on <code>print(\"Send tapped\")</code>; tap Send.",
                    "<b>⌘7</b>: find your closure and SwiftUI frames.",
                    "LLDB: <code>bt</code>, then <code>thread list</code>.",
                    "Add <code>Thread.sleep(forTimeInterval: 3)</code>; tap; feel it.",
                    "Remove it. Try <code>.disabled(true)</code> on Send."],
                   "", 'Expected: the console prints Send tapped, Request tapped, History tapped; the breakpoint stops on the main thread (thread 1) with the closure at the top and SwiftUI button frames below it, then touch and gesture frames (our scripted activation showed accessibility frames there instead); the sleep freezes the UI for three seconds; a disabled Send does nothing and looks dimmed.',
                   side=f'<div>{card("You hand in", ul("Your console output for all three", "A screenshot of the stopped stack", "One line: which thread ran the action?"))}</div>'))

end_slide('2.7', 'SwiftUI Button, Closures<br>&amp; Event Handling', 'Lesson 2.8 &mdash; @State and Reactive UI',
          'You can now explain Button&rsquo;s initializers and its escaping action closure, why evaluating body never runs the action, the path from a tap to your closure on the main actor, hit testing and contentShape, styles, the disabled state and accessibility labels, and how a reusable QuickAction takes its behaviour as a closure without keeping things alive by accident.',
          'Next, Lesson 2.8: @State and reactive UI. The hard-coded balance becomes SwiftUI-managed state, and NPay responds visibly to a tap.')

write_deck(OUT27, '2.7', 'Button &amp; Events', 'Button &amp; Events')
