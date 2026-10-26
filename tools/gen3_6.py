"""Generates decks/unit-3/lesson-3.6/index.html from the Lesson 3.6 text (SwiftUI Animations & Transitions).
The text came in two pieces (Sections 1-15, cut off; "Part 2" Sections 15-23), grouped into 8 Parts. Evidence comes
from tools/sim3_6: frames the app captured during animations, and the per-frame values SwiftUI passed to Animatable
modifiers; two compiler runs (the Transaction name clash; AnimatedNumber in Swift 6 mode)."""
import html, os, re, sys
OUT36 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers


def strip(prefix, times, w=118, step=False, idx=None):
    """A row of frames the app captured, each labelled with its measured time (idx picks some of them)."""
    idx = idx if idx is not None else range(len(times))
    cells = ''.join(f'<figure style="margin:0"><img src="img/{prefix}{i}.png" alt="frame at {times[i]} ms" style="width:100%;display:block;border:1px solid var(--line-2);border-radius:8px">'
                    f'<figcaption class="shot-cap" style="margin-top:4px">{times[i]} ms</figcaption></figure>' for i in idx)
    return f'<div class="{"step" if step else ""}" style="display:grid;grid-template-columns:repeat({len(idx)},minmax(0,{w}px));gap:8px;justify-content:center">{cells}</div>'


CIRCLE_T = [17, 131, 236, 343, 450, 558, 666]
SUCCESS_T = [0, 123, 234, 347, 457, 567, 677]
NOANIM_T = [0, 131, 236, 346, 455, 564, 673]
REDUCED_T = [0, 129, 238, 347, 458, 568, 682]
LAB_T = [31, 138, 239, 338, 439, 540, 642]
# diameter samples (ms, value) from the curves run
LIN = [(38, 83.3), (55, 86.7), (105, 96.7), (155, 106.7), (205, 116.7), (255, 126.7), (305, 136.7), (355, 146.7), (405, 156.7), (455, 166.7), (505, 176.7), (521, 180.0), (800, 180.0)]
EIO = [(28, 80.2), (45, 80.9), (95, 85.6), (145, 94.7), (195, 108.0), (245, 124.3), (295, 141.4), (345, 156.8), (395, 168.8), (445, 176.4), (495, 179.8), (512, 180.0), (800, 180.0)]
SPR = [(36, 82.0), (52, 88.1), (102, 117.6), (152, 149.1), (202, 169.1), (252, 179.8), (302, 183.6), (352, 184.0), (402, 182.9), (452, 181.6), (502, 180.7), (602, 179.9), (802, 180.0)]

title_slide('3.6', 'SwiftUI Animations<br>&amp; Transitions',
            'The balance drops from ₹25,000 to ₹23,500 and the digits roll. Nobody wrote a frame: the state changed <b>once</b>, and SwiftUI animated the presentation.',
            'Lesson 3.5 made the draft survive. Today NPay gets motion: a balance that animates, a transaction that slides in, a success checkmark that springs in. Not as decoration: we measure how SwiftUI animates. Our app recorded the value SwiftUI used on every frame, and captured real frames mid-animation, so every claim on these slides comes with numbers or pictures.')
outcomes_slide('3.6', [("play", "Animate a state change with <code>withAnimation</code>"),
                       ("diff", "Read curves: linear, ease, spring, <b>measured</b>"),
                       ("layers", "Tell animations from <b>transitions</b>, and why identity matters"),
                       ("code", "Know what <code>Animatable</code> interpolates, and what never changes"),
                       ("db", "Animate the balance and new transactions without touching the money"),
                       ("eye", "Respect Reduce Motion; measure cost before optimising")])
where_slide('3.6', 'Today: motion with meaning', (),
            '3.5: a store-owned draft that survives navigation.',
            'Balance, insertion and success animations, measured.',
            'Lesson 3.5 finished the state story. Today the same state drives motion. Next lesson: reusable components and an NPay design system.',
            'The milestone.')

# ================================================================== Part 1 (1)
divider(1, "The milestone", "Three animations", 'Balance, transaction insertion, success.', 'The demo, built natively.')
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "One tap: digits roll, a row slides in", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:20px;align-items:start">
      {card("Three animations", ul("A smooth <b>balance</b> update", "An animated <b>transaction</b> insertion", "A payment-<b>success</b> transition"))}
      <div class="rule step" data-label="The question">{ul("₹25,000 &rarr; ₹23,500: how, without drawing every frame?")}</div>
    </div>
    <div class="gap"></div>
    <div class="step">{strip("lab", LAB_T, 150)}
      <p class="small muted" style="margin:6px 0 0;text-align:center">Frames captured by the app after &ldquo;Simulate ₹1,500 payment&rdquo; (iPhone 17 simulator)</p></div>
  </div>""", notes(('SAY', 'Three animations for NPay: a smooth balance update, an animated transaction insertion and a payment-success transition. The text showed a web demo; we built the same Animation Lab natively: a balance card, a Simulate ₹1,500 payment button and recent transactions.'),
                  ('SAY', 'Click: the engineering question: when the balance changes from ₹25,000 to ₹23,500, how does SwiftUI animate it without us updating every frame?'),
                  ('SAY', 'Click: seven frames the app captured of its own screen after the tap, with their times. Look at the third and fourth: the digits are mid-roll, one digit replaced by the next, and the "Demo Payment" row is sliding in at the top while the others move down. By 338 ms it is settled. All of it from one state change.'),
                  ('CONNECT', 'Start from zero: what is an animation?'))))

# ================================================================== Part 2 (2-4)
divider(2, "withAnimation", "Change state; SwiftUI animates", 'One state change, many frames.', 'The first experiment.')
AX = """struct AnimationExperiment: View {
    @State private var expanded = false

    var body: some View {
        VStack(spacing: 30) {
            Circle()
                .fill(.blue)
                .frame(width: expanded ? 180 : 80,
                       height: expanded ? 180 : 80)

            Button("Toggle Size") {
                withAnimation(.easeInOut(duration: 0.5)) {
                    expanded.toggle()
                }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}"""
S.append(slide("Part 2 &middot; First experiment: withAnimation (sections 2&ndash;3)", "80 to 180 points, no frames written", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:20px;align-items:start">
      {code("AnimationExperiment.swift", AX, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Animation", ul("How a <b>visual value</b> changes over time", "SwiftUI interpolates animatable properties"))}
        <div class="step">{strip("circle", CIRCLE_T, 80)}
          <p class="small muted" style="margin:6px 0 0;text-align:center">Frames the app captured after Toggle Size</p></div>
        <div class="step">{card("What happened", ul("<code>expanded</code> changed inside <code>withAnimation</code>", "The update carried an animation; the frame size followed it"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A circle with a frame of 80 points. Change it to 180: without animation SwiftUI just shows the new size. With animation it interpolates supported animatable properties between the old and the new value. Animation describes how a visual value changes over time; we never render the intermediate frames ourselves.'),
                  ('SAY', 'The text&rsquo;s first experiment, AnimationExperiment: an @State Bool, a circle whose frame depends on it, and a button that toggles it inside withAnimation with an ease-in-out curve of half a second.'),
                  ('SAY', 'Click: our run: seven frames the app captured of itself after the tap. The circle grows through intermediate sizes, slow at first, fast in the middle, slow at the end. Click: what happened: expanded changed inside withAnimation, so SwiftUI associated an animation with that update, and the frame size, which is animatable, followed it smoothly.'),
                  ('CONNECT', 'Did expanded take intermediate values?'))))

PIPE = [("tap", "Tap", "the action closure runs"), ("code", "State changes", "once, to the target"), ("link", "Animation attached", "to this update"),
        ("diff", "Body re-evaluated", "new target values"), ("gear", "Interpolation", "old &rarr; new, per frame"), ("eye", "Frames drawn", "until settled")]
P = []
for i, (ic, t, sub) in enumerate(PIPE):
    x = i * 190
    P.append(tall(x, 0, 172, 120, ic, t, sub, f'{i + 1}', ''))
    if i < 5:
        P.append(wire(f'M{x + 174} 60H{x + 188}' + head(x + 188, 60, 'r')))
S.append(slide("Part 2 &middot; How withAnimation works (sections 4, 16) &middot; conceptual", "The state changes once; the presentation many times", f"""  <div class="body">
    {cues(6)}
    {svg('0 0 1132 120', 'Tap, state changes once, animation attached, body re-evaluated, interpolation, frames drawn', 'pipe', P, 'max-height:140px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div class="step">{console("Measured: Bool vs frame size (easeInOut 0.5 s)", ["state changes during the animation: 1", "frame diameter values: 30 (80.2 &hellip; 180.0)"], 13)}</div>
      <div class="rule step" data-label="So">{ul("<code>expanded</code>: <code>false &rarr; true</code>, once", "Intermediate sizes exist only in the <b>presentation</b>")}</div>
    </div>
  </div>""", notes(('SAY', 'Only stage 1 came with the text; the rest is our conceptual outline. Click: the user taps; the action closure runs. Click: the state changes once, to its target. Click: withAnimation attaches an animation to that update. Click: SwiftUI re-evaluates the body and gets the new target values. Click: for animatable properties, it interpolates from old to new on every frame. Click: frames are drawn until the animation settles. Exact scheduling and rendering are SwiftUI&rsquo;s business.'),
                  ('SAY', 'Click: we measured the text&rsquo;s key claim. The Bool changed exactly once during the animation; the frame modifier received 30 different diameters, from 80.2 to 180, one per frame at 60 frames a second.'),
                  ('SAY', 'Click: withAnimation does not repeatedly mutate the state through intermediate values. The state jumps to its target; intermediate sizes exist only in the presentation.'),
                  ('CONNECT', 'Those 30 values follow a curve. Which one?'))))

# ================================================================== Part 3 (5)
divider(3, "Animation curves", "Same distance, different motion", 'Measured, frame by frame.', 'Three curves.')


def curve_svg():
    X = lambda ms: 40 + ms * 0.78
    Y = lambda v: 210 - (v - 80) * 1.7
    P = [wire(f'M40 210H{X(820):g}', None, 'faint'), wire(f'M40 {Y(180):g}H{X(820):g}', None, 'faint'),
         f'<text class="sm" x="4" y="{Y(180) + 4:g}">180</text>', f'<text class="sm" x="12" y="214">80</text>',
         f'<text class="sm" x="{X(500) - 12:g}" y="232">500 ms</text>', f'<text class="sm" x="{X(800) - 12:g}" y="232">800 ms</text>']
    for k, (pts, cls, lab, l) in enumerate([(LIN, 'wire', 'linear', '1+'), (EIO, 'wire', 'easeInOut', '2+'), (SPR, 'wire lit', 'spring: peak 184.1', '3+')]):
        d = 'M' + ' L'.join(f'{X(t):g} {Y(v):g}' for t, v in [(0, 80)] + pts)
        P.append(f'<g class="fade"{lit(l)}><path class="{cls}" d="{d}" style="fill:none"/></g>')
    P.append(f'<text class="sm" x="{X(330):g}" y="{Y(186):g}">spring overshoots</text>')
    return svg('0 0 690 240', 'Measured frame diameters over time for linear, easeInOut and spring', 'crv', P, 'max-height:250px')


ROWS = [(f'{t} ms', f'{a:.1f}', f'{b:.1f}', f'{c:.1f}') for (t, a), (_, b), (_, c) in zip([(50, 86.7), (100, 96.7), (150, 106.7), (250, 126.7), (350, 146.7), (500, 176.7)],
                                                                                      [(50, 80.9), (100, 85.6), (150, 94.7), (250, 124.3), (350, 156.8), (500, 179.8)],
                                                                                      [(50, 88.1), (100, 117.6), (150, 149.1), (250, 179.8), (350, 184.0), (500, 180.7)])]
S.append(slide("Part 3 &middot; Animation curves, measured (section 5)", "80 &rarr; 180: three curves, same target", f"""  <div class="body">
    {cues(3)}
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:20px;align-items:start">
      {curve_svg()}
      <div style="display:flex;flex-direction:column;gap:10px">
        {tbl(["≈ time", "linear", "easeInOut", "spring"], ROWS)}
        <p class="small muted" style="margin:0">linear, easeInOut: 0.5 s, 30 values. spring(response 0.45, damping 0.7): 76 values, settled at 1,285 ms.</p>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s easing explorer was illustrative. Ours is measured: the same circle, 80 to 180 points, with each curve, and the diameter SwiftUI used on every frame. Times are from the withAnimation call; the table picks the nearest frame.'),
                  ('SAY', 'Click: linear: a constant 3.3 points per frame, 100 points over 30 frames. Click: ease-in-out: barely moving at 50 ms, 80.9, fastest in the middle, then easing in to 180 at half a second. Click: the spring, response 0.45 and damping 0.7: fast at first, past 180 by 300 ms, peaking at 184.1, then settling back. 76 frames, about 1.3 seconds: a spring&rsquo;s duration comes from its physics, not from a duration you pass.'),
                  ('CONNECT', 'Which suits a payments app?'))))

CV = """.linear(duration: 0.5)
.easeIn(duration: 0.5)
.easeOut(duration: 0.5)
.easeInOut(duration: 0.5)
.spring(response: 0.4, dampingFraction: 0.7)"""
S.append(slide("Part 3 &middot; Which should NPay use? (section 5)", "Restrained motion for money", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {code("Common animations", CV, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Use", "Curve"], [("Ordinary UI transitions", "<code>easeInOut</code>"), ("Playful feedback", "<code>spring</code>"), ("Financial confirmation", "<b>restrained</b>: success, not spectacle")], 'tbl')}</div>
        <div class="step">{card("Remember the spring", ul("It <b>overshoots</b> (184 for 180)", "Fine for a checkmark; odd for a balance"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI offers linear, ease-in, ease-out, ease-in-out and springs, among others; different curves, different motion characteristics.'),
                  ('SAY', 'Click: the text&rsquo;s guidance: ease-in-out is a reasonable start for ordinary transitions; a spring can feel natural for playful feedback; for financial confirmation, prefer restrained motion that communicates success without distracting.'),
                  ('SAY', 'Click: our measurement adds one practical point: the spring overshot its target, 184 for 180. That bounce suits a checkmark appearing; on a number or a balance it would look like the value went too far.'),
                  ('CONNECT', 'Two ways to attach an animation.'))))

# ================================================================== Part 4 (6, 12)
divider(4, "Explicit, implicit, transactions", "Where the animation comes from", 'withAnimation, .animation(value:), and the Transaction that carries it.', 'Two styles.')
EX = """withAnimation(.easeInOut(duration: 0.3)) {
    expanded.toggle()
}"""
IM = """Circle()
    .frame(width: expanded ? 180 : 80,
           height: expanded ? 180 : 80)
    .animation(.easeInOut(duration: 0.3),
               value: expanded)"""
S.append(slide("Part 4 &middot; Implicit versus explicit animations (section 6)", "On the change, or on the value", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div>{code("Explicit: withAnimation", EX, "font-size:14px")}{out("The animation is attached to the <b>state update</b>.", "")}</div>
      <div class="step">{code("Value-driven: .animation(_:value:)", IM, "font-size:14px")}{out("Animates when <b>expanded</b> changes.", "")}</div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Scope">{ul("<code>.animation(_:value:)</code> affects animatable changes in the modified <b>subtree</b>", "Not just one property, unless you scope it")}</div>
  </div>""", notes(('SAY', 'Explicit animation: withAnimation around the state change. The animation is associated with that update, wherever the change shows up.'),
                  ('SAY', 'Click: value-driven animation: the .animation modifier with a value. Whenever expanded changes, animatable changes in this part of the tree animate with that curve, no matter who changed the value.'),
                  ('SAY', 'Click: the important distinction: .animation(_:value:) affects animatable changes in the modified subtree when the value changes. It is not limited to one property unless you scope the modifier appropriately, by placing it close to what should animate.'),
                  ('CONNECT', 'How does an animation travel with an update?'))))

CL = """struct Transaction: Identifiable {   // NPay's domain model
    let id: UUID
    let title: String
    let amountPaise: Int
    let date: Date
}

withTransaction(Transaction(animation: .easeInOut)) {
    show = true
}"""
S.append(slide("Part 4 &middot; Animation transactions (section 12)", "SwiftUI&rsquo;s Transaction is not our Transaction", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("SwiftUI&rsquo;s <code>Transaction</code>", ul("Carries animation context through an update", "<code>withAnimation</code> sets its animation"))}
        <div class="step">{code("Both in one module (authored test)", CL, "font-size:12px")}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("swiftc, iOS 26.5 SDK", err("cannot convert value of type 'Transaction' to expected argument type 'SwiftUICore.Transaction'") + '<div class="gap"></div>' + err("extra argument 'animation' in call"))}</div>
        <div class="rule step" data-label="Fix">{ul("<code>SwiftUI.Transaction(animation:)</code> compiles", "Or rename ours <code>PaymentTransaction</code>, as the text suggests")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Behind withAnimation: SwiftUI has a Transaction type that carries animation-related context through view updates. withAnimation associates an animation with the update&rsquo;s transaction, so the framework can coordinate animation for the affected properties.'),
                  ('SAY', 'The text warns: SwiftUI&rsquo;s Transaction is not NPay&rsquo;s financial Transaction model. Same name, different concepts. Click: we tested what that costs: our domain struct next to a use of SwiftUI&rsquo;s withTransaction. Click: the compiler picks our Transaction, the nearer declaration, and fails: cannot convert our Transaction to SwiftUICore.Transaction, and extra argument animation.'),
                  ('SAY', 'Click: qualifying it, SwiftUI.Transaction, compiles. The cleaner long-term fix is the text&rsquo;s suggestion: rename the domain model, for example PaymentTransaction.'),
                  ('CONNECT', 'Now views that arrive and leave: transitions.'))))

# ================================================================== Part 5 (7, 8, 11, 14, 22)
divider(5, "Transitions", "How a view enters and leaves", 'Insertion and removal, not value changes.', 'The difference.')
TR = """if showSuccess {
    Text("Payment Successful")
        .transition(.opacity)
}

withAnimation {
    showSuccess.toggle()
}"""
S.append(slide("Part 5 &middot; Transitions: appearance and disappearance (sections 7&ndash;8)", "Animations change values; transitions move views in and out", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("A transition", TR, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["", "Describes"], [("Animation", "interpolating <b>animatable values</b>"), ("Transition", "how a view <b>enters or leaves</b> the hierarchy")], 'tbl')}</div>
        <div class="step">{card("Identity again (3.5)", ul("Same identity, new content: maybe no transition", "Insertion and removal are about identity"))}</div>
        <div class="step">{card("Built-in", ul("<code>.opacity</code>, <code>.slide</code>, <code>.scale</code>, <code>.move(edge:)</code>, combined"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Animations and transitions are related but different. The text&rsquo;s example: a Text inside if showSuccess, with an opacity transition; toggling showSuccess inside withAnimation fades it in and out.'),
                  ('SAY', 'Click: an animation interpolates changes in animatable values. A transition describes how a view enters or leaves the hierarchy. Click: so identity matters, as in Lesson 3.5: if SwiftUI considers the view the same, with only its content changed, there is no insertion or removal, and a transition may not occur.'),
                  ('SAY', 'Click: the text&rsquo;s explorer showed opacity, slide and scale; there are more, such as move(edge:), and they combine. In Xcode you apply .transition and animate the insertion or removal with withAnimation.'),
                  ('CONNECT', 'NPay&rsquo;s success screen.'))))

SUC = """@State private var showContent = false

var body: some View {
    VStack(spacing: 24) {
        if showContent {
            Image(systemName: "checkmark.circle.fill")
                .font(.system(size: 80))
                .foregroundStyle(.green)
                .transition(.scale.combined(with: .opacity))
        }
        Text("Payment Recorded")
            .font(.title.bold())
        // message, ID, Back to Dashboard as in 3.2
    }
    .onAppear {
        withAnimation(.spring(response: 0.45,
                              dampingFraction: 0.7)) {
            showContent = true
        }
    }
}"""
S.append(slide("Part 5 &middot; NPay&rsquo;s animated success screen (section 11)", "The checkmark springs in", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:20px;align-items:start">
      {code("PaymentSuccessScreen (excerpt)", SUC, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What happens", ul("On appear, <code>showContent</code>: false &rarr; true", "The checkmark is <b>inserted</b>: scale + opacity", "The spring paces the transition"))}
        <div class="step">{strip("success", SUCCESS_T, 125, idx=[1, 2, 3, 6])}
          <p class="small muted" style="margin:6px 0 0;text-align:center">The text&rsquo;s screen, frames captured after it appeared</p></div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s success screen. A showContent flag, false at first. The checkmark exists only when it is true, with a combined scale and opacity transition. On appear, showContent becomes true inside a spring animation.'),
                  ('SAY', 'When the screen appears, the checkmark enters the hierarchy; SwiftUI applies the combined transition; the spring controls how it progresses. Click: four of our frames: at 123 ms the text is there but no checkmark yet; at 234 ms a small, faded checkmark is growing while the text moves down to make room; at 347 ms and after, it is full size and opaque.'),
                  ('CONNECT', 'Experiment: remove withAnimation.'))))

S.append(slide("Part 5 &middot; Remove withAnimation; enable Reduce Motion (sections 14, 15, 22)", "Same transition modifier, no motion", f"""  <div class="body">
    <div style="display:flex;flex-direction:column;gap:10px">
      <div><p class="small" style="margin:0 0 6px"><b>Without <code>withAnimation</code></b> (<code>showContent = true</code> in onAppear)</p>{strip("noanim", NOANIM_T, 150)}</div>
      <div class="step"><p class="small" style="margin:0 0 6px"><b>Reduce Motion on</b> (Settings value read by the text&rsquo;s Section 22 code: <code>accessibilityReduceMotion: true</code>)</p>{strip("reduced", REDUCED_T, 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s experiment: remove withAnimation. The transition modifier is still on the checkmark, but nothing animates: by the first frame after the screen appears, the checkmark is there at full size. A transition needs an animated insertion; without one, the view simply appears.'),
                  ('SAY', 'Click: Reduce Motion, turned on in the simulator&rsquo;s accessibility settings. The app read accessibilityReduceMotion as true, so the text&rsquo;s Section 22 code set showContent without withAnimation: the same immediate result. That is the point: users who ask for less motion get the result without the movement.'),
                  ('CONNECT', 'How the code decides.'))))

RM = """@Environment(\\.accessibilityReduceMotion)
private var reduceMotion

.onAppear {
    if reduceMotion {
        showContent = true
    } else {
        withAnimation(.spring(response: 0.45,
                              dampingFraction: 0.7)) {
            showContent = true
        }
    }
}"""
S.append(slide("Part 5 &middot; Accessibility: make motion optional (sections 14, 22)", "Skip the motion, keep the result", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("PaymentSuccessScreen (section 22)", RM, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Section 14&rsquo;s first idea", ul("<code>.linear(duration: 0.01)</code> when reduced", "Still motion, just very fast"))}
        <div class="rule step" data-label="Better">{ul("For significant motion, <b>no</b> transition at all", "Never hide information behind an animation")}</div>
        <div class="step">{card("More", ul("Accessibility in depth: Lesson 3.10"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI provides the accessibilityReduceMotion environment value. Section 14 first suggested picking a near-instant linear animation when it is on. Section 22 improves it: if the user prefers reduced motion, set showContent directly; otherwise animate with the spring.'),
                  ('SAY', 'Click: why better: an extremely fast animation can still be uncomfortable; for significant motion, avoiding the transition entirely is the better reduced-motion experience. The information, the checkmark, still appears. Click: the text covers accessibility in depth in Lesson 3.10.'),
                  ('CONNECT', 'Back to the balance card.'))))

# ================================================================== Part 6 (9, 10, 19)
divider(6, "Balance and insertion", "Animate the money&rsquo;s presentation", 'numericText for digits; stable IDs for rows.', 'The balance card.')
NT = """Text(Money.display(balancePaise))
    .font(.largeTitle.bold())
    .contentTransition(.numericText())
    .animation(.easeInOut(duration: 0.4),
               value: balancePaise)"""
S.append(slide("Part 6 &middot; Animate NPay&rsquo;s balance card (section 9)", "Digits roll; paise stay integers", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("BalanceCard", NT, "font-size:13px")}
        <div class="warn step" data-label="Presentation only">{ul("<code>numericText()</code> changes how text <b>changes</b>", "Money is still an <code>Int</code> of paise")}</div>
      </div>
      <div class="step">{strip("lab", LAB_T, 165, idx=[0, 2, 3, 4])}
        <p class="small muted" style="margin:6px 0 0;text-align:center">The balance during the change</p></div>
    </div>
  </div>""", notes(('SAY', 'The balance card displays Money.display of balancePaise; when the balance changes, the text normally updates instantly. contentTransition(.numericText()) asks SwiftUI to animate numeric text changes; the value-driven animation supplies the curve whenever balancePaise changes.'),
                  ('SAY', 'Click: the nuance: numericText is a presentation effect for text. It does not change how money is calculated; the authoritative demo amount is still an integer number of paise.'),
                  ('SAY', 'Click: the frames from the Animation Lab, which uses this card: ₹25,000.00, then a digit rolling, then ₹23,500.00. Only the changing digits move.'),
                  ('CONNECT', 'And the new transaction row.'))))

INS = """withAnimation(.easeInOut(duration: 0.3)) {
    transactions.insert(newTransaction, at: 0)
}

// in a VStack (our Animation Lab)
ForEach(transactions) { transaction in
    TransactionRow(transaction: transaction)
        .transition(.move(edge: .top)
                        .combined(with: .opacity))
}"""
S.append(slide("Part 6 &middot; Animate transaction insertion (section 10)", "Insert inside withAnimation; the row transitions in", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Insertion", INS, "font-size:12px")}
        {card("List", ul("Insertion animation is more <b>platform-managed</b>", "May differ from a VStack"))}
      </div>
      <div class="step">{strip("lab", LAB_T, 165, idx=[1, 2, 3, 4])}
        <p class="small muted" style="margin:6px 0 0;text-align:center">&ldquo;Demo Payment&rdquo; slides in; rows below move down</p></div>
    </div>
  </div>""", notes(('SAY', 'Inserting a transaction inside withAnimation associates an animation with that change. In a custom VStack or LazyVStack you can give rows a transition; our Animation Lab uses move from the top combined with opacity, our choice. In a List, animation behaviour is more platform-managed and may differ.'),
                  ('SAY', 'Click: the frames: the new Demo Payment row fades and moves in at the top while Coffee Shop and Electricity Bill move down to make room. SwiftUI knows which rows are new and which only moved because each has a stable ID.'),
                  ('CONNECT', 'What if the IDs are not stable?'))))

S.append(slide("Part 6 &middot; Why animation and identity are connected (section 19)", "New IDs: every row leaves and arrives again", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Experiment (authored)", ul("Three rows with <code>onAppear</code> / <code>onDisappear</code>", "Refresh the same data, inside <code>withAnimation</code>:", "A: keep the IDs &middot; B: <code>Transaction(id: UUID(), …)</code>"))}
        <div class="step">{console("A: same IDs", ["(no row appeared or removed)"], 13)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("B: new IDs", ["row appeared: Salary Credit", "row appeared: Electricity Bill", "row appeared: Coffee Shop", "row removed: Coffee Shop", "row removed: Electricity Bill", "row removed: Salary Credit"], 13)}</div>
        <div class="rule step" data-label="Rule">{ul("Stable identity is a prerequisite for predictable collection transitions")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Lesson 2.10 gave transactions stable IDs; Lesson 3.5 showed identity owns state. Together: when a transaction is inserted, SwiftUI matches existing rows to their previous identities, so it knows which views are new. We tested a refresh: the same three transactions reassigned inside withAnimation, once keeping the IDs, once regenerating them.'),
                  ('SAY', 'Click: same IDs: nothing appeared or disappeared; SwiftUI saw the same three rows. Click: new IDs: SwiftUI saw three new rows and three removed ones: every row was inserted and removed, so every row would run its transition, and any row-local state would be lost. Same data on screen, completely different identity.'),
                  ('SAY', 'Click: the text&rsquo;s engineering rule: stable identity is a prerequisite for predictable collection transitions.'),
                  ('CONNECT', 'Under the hood: what can animate?'))))

# ================================================================== Part 7 (16-18, 20)
divider(7, "Interpolation", "Animatable data, step by step", 'What SwiftUI interpolates, and how to join in.', 'The formula.')
S.append(slide("Part 7 &middot; How SwiftUI knows what can animate (sections 16&ndash;17)", "<i>v</i>(<i>t</i>) = <i>v</i>&#8320; + (<i>v</i>&#8321; &minus; <i>v</i>&#8320;)<i>t</i>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Animatable", ul("Values SwiftUI can interpolate: size, offset, opacity, shape parameters", "Exposed through <code>animatableData</code>"))}
        <p style="font-size:24px;margin:6px 0;text-align:center"><i>v</i>(0.5) = 80 + (180 &minus; 80) &times; 0.5 = <b>130</b></p>
        <div class="step">{card("Not everything animates", ul("Some properties change <b>discretely</b>", "Others need an <code>Animatable</code> implementation"))}</div>
      </div>
      <div class="step">{console("linear(0.5), measured diameters", ["&hellip;", "205 ms&ensp;116.7", "255 ms&ensp;126.7", "305 ms&ensp;136.7", "&hellip;", "+3.3 per frame: 100 points over 30 frames"], 13)}
        <p class="small muted" style="margin:8px 0 0">Times from the <code>withAnimation</code> call; the first frame lands about 16 ms later, so 130 falls between the 255 and 305 ms frames.</p></div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI uses the Animatable protocol and related mechanisms: many modifiers expose animatable values such as size, offset, opacity and shape parameters. Animatable data is data that can be interpolated between two values. The linear case is this formula: v of t equals the start, plus the difference times t, with t the normalised progress from 0 to 1. At t = 0.5, 80 plus 100 times a half: 130 points.'),
                  ('SAY', 'Click: not every property animates: some change discretely, others need an Animatable implementation or a suitable modifier.'),
                  ('SAY', 'Click: our linear measurement matches the formula: a steady 3.3 points per frame, 116.7, 126.7, 136.7. Our clock starts at the withAnimation call and the first frame comes about 16 ms later, so the 130-point midpoint falls between our 255 and 305 ms samples. The text&rsquo;s note applies: the screen itself renders in physical pixels.'),
                  ('CONNECT', 'Join the mechanism with our own modifier.'))))

AN = """struct AnimatedNumber: AnimatableModifier {
    var value: Double

    var animatableData: Double {
        get { value }
        set { value = newValue }
    }

    func body(content: Content) -> some View {
        Text(value,
             format: .number.precision(.fractionLength(0)))
            .font(.largeTitle.bold())
    }
}

Text("")
    .modifier(AnimatedNumber(value: Double(balancePaise) / 100))
    .animation(.easeInOut(duration: 0.5), value: balancePaise)"""
S.append(slide("Part 7 &middot; Build our own Animatable modifier (section 18)", "SwiftUI feeds the in-between values", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.9fr);gap:20px;align-items:start">
      {code("AnimatedNumber (text)", AN, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="step">{console("₹25,000 &rarr; ₹23,500, values passed to body", ["30 values in 0.5 s:", "24997, 24947, 24832, 24652, 24420,", "24164, 23920, 23721, 23584, 23513 &hellip; 23500"], 12.5)}</div>
        <div class="tip step" data-label="Swift 6 mode">{ul("Add <code>nonisolated</code> to <code>animatableData</code>", "Fine as written in an Xcode 26 app")}</div>
        <div class="step">{card("For NPay&rsquo;s balance", ul("<code>numericText()</code> is simpler"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Connect animations to Swift protocols: a custom modifier that animates a number. animatableData exposes the value SwiftUI can interpolate; as the animation progresses, SwiftUI supplies intermediate values through it, and body draws the current one.'),
                  ('SAY', 'Click: we ran it with one extra line that records each value body receives: 30 values in half a second as the balance went from ₹25,000 to ₹23,500, following the ease-in-out curve: 24997, 24947, 24832, and so on to 23500. The state changed once; the modifier saw 30 values.'),
                  ('SAY', 'Click: a compiler finding. In plain Swift 6 language mode, as in a Swift package, this exact code fails: ViewModifier makes animatableData main-actor isolated, but Animatable requires it nonisolated. Marking it nonisolated fixes it. In a new Xcode 26 app project, whose template sets default MainActor isolation, and in Swift 5 mode, it compiles as written. Click: as the text says, for NPay&rsquo;s balance numericText is simpler; the SDK also marks AnimatableModifier as superseded: conform to Animatable directly.'),
                  ('CONNECT', 'What if the target changes mid-animation?'))))

S.append(slide("Part 7 &middot; What happens when animation is interrupted? (section 20)", "Retargeted from where it is, not where it was going", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Experiment (authored)", ul("80 &rarr; 180, linear 1 s", "At 427 ms: back to 80, linear 1 s"))}
        <div class="step">{console("Measured diameters", ["404 ms&ensp;118.3", "421 ms&ensp;120.0&ensp;&larr; retarget", "454 ms&ensp;121.0", "504 ms&ensp;123.6", "peak 129.0, then down to 80.0 at 1,437 ms"], 13)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("What we saw", ul("No jump: it kept its motion, slowed, reversed", "SwiftUI blended old and new animations"))}</div>
        <div class="rule step" data-label="For money">{ul("State is correct <b>immediately</b>", "Animation is feedback, never the business operation")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Imagine the user taps Add Money repeatedly: the balance changes again before the previous animation finishes. SwiftUI may retarget the animation from its current presentation toward the latest target; the exact behaviour depends on the animation type, the properties and the transaction. Our experiment: grow from 80 to 180 over a second, linearly, and at 427 ms send it back to 80.'),
                  ('SAY', 'Click: no jump. At the moment of the change it was at 120; it kept rising, more slowly, peaked at 129, then came back down to 80 by 1.4 seconds. SwiftUI blended the running animation with the new one instead of restarting. Click: that is the text&rsquo;s "retarget or otherwise coordinate".'),
                  ('SAY', 'Click: why it matters for finance: users must never wait for an animation before the state is correct. The state updates immediately, by the app&rsquo;s logic; the animation is presentation feedback, not the authoritative operation.'),
                  ('CONNECT', 'Animations also cost something.'))))

# ================================================================== Part 8 (13, 15, 21 + integration)
divider(8, "Cost and review", "Measure, don&rsquo;t assume", 'Performance, experiments, and NPay&rsquo;s animated code.', 'Cost.')
PF = [("Opacity", "often compositing"), ("Scale", "transform / compositing in many cases"), ("Offset", "position- or transform-related presentation"),
      ("Frame changes", "can involve <b>layout</b>"), ("Complex list changes", "reconciliation and layout"), ("Custom drawing", "repeated drawing work")]
S.append(slide("Part 8 &middot; Performance: animations are not free (sections 13, 21)", "Tendencies, not guarantees", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {tbl(["Animation", "Typical work"], PF, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Instruments (Product &rarr; Profile)", ul("Animation hitches, Core Animation, Time Profiler", "Look for hitches, layout, CPU, main-thread blocking, repeated bodies"))}</div>
        <div class="rule step" data-label="Principle">{ul("Measure on a device like your users&rsquo;", "We didn&rsquo;t profile here: the simulator isn&rsquo;t that device")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Animations can involve layout, rendering, compositing, or a mix. Opacity is often compositing-friendly. Scale is a transform, efficient in many cases. Offset is position- or transform-related. Frame changes, like our circle, can mean layout on every frame. Complex list changes need reconciliation and layout; custom drawing repeats drawing work. These are tendencies, not guarantees: the cost depends on the hierarchy and the rendering environment.'),
                  ('SAY', 'Click: measure with Instruments via Product, Profile: depending on the Xcode version, animation hitch analysis, Core Animation and the Time Profiler. Look for frame hitches, excessive layout, CPU use during the animation, main-thread blocking, repeated expensive view evaluation.'),
                  ('SAY', 'Click: the principle: do not optimise based on assumptions; measure on a device representative of your users. We deliberately did not profile on the simulator, which runs on a Mac and says little about a phone&rsquo;s rendering cost. Unit 8 covers performance.'),
                  ('CONNECT', 'The text&rsquo;s experiments, all run.'))))

XP = [("Numeric text animation", "digits roll during the change (Part 6)"), ("Linear versus spring", "linear 3.3/frame; spring peaks at 184.1 (Part 3)"),
      ("Insert a transaction", "stable IDs: only the new row transitions (Part 6)"), ("Success transition", "scale + opacity over ~350 ms (Part 5)"),
      ("Remove withAnimation", "no animation: checkmark appears at once (Part 5)"), ("Enable Reduce Motion", "read as true; no entrance animation (Part 5)")]
S.append(slide("Part 8 &middot; Xcode experiments (section 15)", "Six experiments, six answers", f"""  <div class="body">
    {tbl(["Experiment", "Simulator"], XP, 'tbl')}
    <p class="small muted" style="margin:6px 0 0">The text runs these on NPay&rsquo;s demo balance editor, which our 3.3 code dropped; the Animation Lab provides the balance change instead.</p>
  </div>""", notes(('SAY', 'The text&rsquo;s experiment table, with our answers. Numeric text: the digits roll. Linear versus spring: linear moves 3.3 points per frame; the spring overshoots to 184.1. Inserting a transaction: with stable IDs only the new row transitions. The success transition: scale plus opacity over about a third of a second. Removing withAnimation: no animation. Reduce Motion: read as true, and the entrance animation is skipped.'),
                  ('SAY', 'One practical note: the text changes the balance with the demo balance editor from Unit 2. Our 3.3 code follows the text&rsquo;s project structure, which no longer has the editor, so the Animation Lab&rsquo;s Simulate button provides the balance change.'),
                  ('CONNECT', 'What changed in NPay itself?'))))

S.append(slide("Part 8 &middot; NPay after Lesson 3.6 (integration, authored)", "Two files changed; the money logic didn&rsquo;t", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {tbl(["File", "Change"], [("BalanceCard", "numeric text transition + value animation"), ("PaymentSuccessScreen", "checkmark transition, spring, Reduce Motion"), ("Store, router, payment flow", "<b>unchanged</b>")], 'tbl')}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Why so small", ul("Animation is presentation", "State logic from 3.5 stays as it was"))}</div>
        <div class="step">{card("Not added", ul("Insertion animation on Home: the payment happens on another tab, so it would play unseen"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text names its next checkpoint: integrate the animated balance card, transaction updates and success feedback into the complete app. We did the parts that make sense, flagged as ours: BalanceCard gets numericText and a value-driven animation; PaymentSuccessScreen gets the checkmark transition, the spring and the Reduce Motion check from Section 22. The store, router and payment flow are unchanged.'),
                  ('SAY', 'Click: that is the lesson in one line: animation is presentation; the state logic stays as it was. Click: we did not add an insertion animation to Home&rsquo;s recent transactions: in NPay the payment is recorded while the Payments tab is showing, so it would animate where nobody sees it. The Animation Lab shows the technique.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.6', (), [("play", "State once, frames many", "withAnimation attaches a curve; SwiftUI interpolates"),
                     ("layers", "Transitions need identity", "insertion and removal; stable IDs; animated changes"),
                     ("eye", "Motion is optional", "Reduce Motion, measured cost, money never waits")],
         'Three things to remember. You change state once; withAnimation or .animation(value:) attaches a curve, and SwiftUI interpolates animatable values frame by frame: a linear 3.3 points per frame, a spring that overshoots and settles. Transitions are about views entering and leaving, so they depend on identity: stable IDs give predictable insertions, and without an animated change nothing moves. And motion is presentation: respect Reduce Motion, measure before optimising, and never make the money wait for an animation.')

review_divider(9)
review([("code", "Question", "Does withAnimation mutate a Bool through intermediate values?",
         "Does <code>withAnimation</code> repeatedly mutate a Boolean state through intermediate values?", "No",
         "Measured: 1 state change; the frame got 30 values.",
         "Thinking the state itself animates.", "Most say no.", None),
        ("gear", "Choose one", "What is the role of animatableData?",
         "What is the role of <code>Animatable.animatableData</code>?<br>A. Store network responses<br>B. Expose interpolatable data<br>C. Manage navigation", "B",
         "AnimatedNumber received 30 values through it.",
         "Treating it as ordinary storage.", "Most pick B.", None),
        ("key", "Choose one", "Why do stable transaction IDs matter for animation?",
         "Why do stable transaction IDs matter for animations?<br>A. They increase frame rate automatically<br>B. They create a new process<br>C. They help preserve logical view identity", "C",
         "New IDs made every row leave and arrive again.",
         "Regenerating IDs on refresh.", "Most pick C.", None),
        ("frame", "Question", "Can frame animation involve layout work?",
         "Can animating a view&rsquo;s frame involve layout work?", "Yes",
         "Size changes can mean layout each frame; measure with Instruments.",
         "Assuming all animation is free.", "Most say yes.", None),
        ("shield", "Question", "Should animation decide whether a payment succeeded?",
         "Should an animation determine whether a payment succeeded?", "No",
         "State is correct at once; animation is feedback.",
         "Waiting on animations for business state.", "Most say no.", None),
        ("eye", "Question", "Should NPay respect Reduce Motion?",
         "Should NPay respect Reduce Motion?", "Yes",
         "Our success screen skipped the spring when it was on.",
         "Making motion mandatory.", "Everyone says yes.", None),
        ("diff", "Predict the result", "spring(response 0.45, damping 0.7) from 80 to 180: the peak?",
         "A frame animates from 80 to 180 with <code>.spring(response: 0.45, dampingFraction: 0.7)</code>. The largest value it reaches is about&hellip;<br>A. 180 exactly<br>B. 184<br>C. 200", "B",
         "Measured peak 184.1, settling to 180 by about 1.3 s.",
         "Expecting springs to stop at the target.", "Some pick A.", None),
        ("layers", "Predict the result", "Remove withAnimation: does .transition still animate?",
         "The checkmark keeps <code>.transition(.scale.combined(with: .opacity))</code>, but <code>showContent = true</code> is no longer inside <code>withAnimation</code>. What happens?<br>A. It still scales in<br>B. It appears at once<br>C. It never appears", "B",
         "Our first frame after appear already showed it full size.",
         "Thinking .transition animates by itself.", "Some pick A.", None),
        ("clock", "Choose one", "From 3.5: what resets a view's local @State?",
         "From Lesson 3.5: which of these resets a view&rsquo;s local <code>@State</code>?<br>A. Its parent re-rendering<br>B. A new explicit <code>.id()</code><br>C. A tab switch in a stable TabView", "B",
         "A new identity, new state; new values alone keep it.",
         "Confusing values with identity.", "Most pick B.", "Spaced review from Lesson 3.5.")])

S.append(next_slide('3.6', [("3.7", "Reusable components &amp; NPay design system", "buttons, cards, typography, spacing; environment propagation"),
                            ("3.10", "Accessibility", "Reduce Motion and more, in depth"),
                            ("Unit 8", "Performance", "Instruments on a real device: hitches, layout, main thread")],
                    'Lesson 3.7 builds reusable buttons, cards, typography and spacing into an NPay design system. The text points to Lesson 3.10 for accessibility in depth, including motion. And Unit 8 profiles performance properly with Instruments on a real device.'))

S.append(lab_slide('3.6', "Motion with meaning", "Animate NPay&rsquo;s presentation; measure what you see.",
                   ["Run AnimationExperiment; try three curves.",
                    "Add numericText to BalanceCard.",
                    "Animate the success checkmark; then drop withAnimation.",
                    "Turn on Reduce Motion; check the success screen.",
                    "Insert rows with stable IDs, then with new IDs.",
                    "Profile one animation on a real device."],
                   "", 'Expected, as in our run: easeInOut starts and ends slowly, a spring overshoots slightly; the balance digits roll while the paise value changes once; without withAnimation the checkmark just appears, and with Reduce Motion the code skips the spring; regenerated IDs make every row disappear and reappear.',
                   side=f'<div>{card("You hand in", ul("A note on each curve&rsquo;s feel", "Your stable-vs-new ID observation", "One sentence: why animation never decides a payment"))}</div>'))

end_slide('3.6', 'SwiftUI Animations<br>&amp; Transitions', 'Lesson 3.7 &mdash; Reusable Components &amp; NPay Design System',
          'You can now animate state changes explicitly or by value, read and choose curves, tell transitions from animations and why identity matters, explain what Animatable interpolates while state changes once, animate the balance and new rows safely, respect Reduce Motion, and measure before optimising.',
          'Next, Lesson 3.7: reusable SwiftUI components and an NPay design system: buttons, cards, typography and spacing built on composition and the environment.')

write_deck(OUT36, '3.6', 'Animations', 'Animations')
