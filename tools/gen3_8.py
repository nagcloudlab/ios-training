"""Generates decks/unit-3/lesson-3.8/index.html from the Lesson 3.8 text (Adaptive Layouts & GeometryReader).
The text came in two pieces (Sections 1-14, cut off; "Part 2" Sections 14-21), grouped into 8 Parts. Evidence comes
from tools/sim3_8, run on an iPhone 17, an iPhone SE (3rd generation) and an iPad Air 11-inch, at the default and the
largest accessibility text size and in landscape; a logging Layout prints the proposal negotiation. The integration of
the Section 19 quick actions into the 3.7 app is authored."""
import html, os, re, sys
OUT38 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers
TOP = lambda src_, cap, w, h: shot(src_, cap, w, h)

title_slide('3.8', 'Adaptive Layouts<br>&amp; GeometryReader',
            'One screen, many sizes: iPhone SE to iPad, portrait to landscape, default text to the largest. Adapt to the <b>content</b>, not a guessed breakpoint.',
            'Lesson 3.7 gave NPay a design system. Today the question every iOS developer meets: how does one SwiftUI screen work on a small iPhone, a large one, an iPad, and with much larger text? We look at how SwiftUI&rsquo;s layout negotiates sizes, at GeometryReader, ViewThatFits and AnyLayout. We ran everything on three simulated devices, at two text sizes and in landscape, and logged the layout negotiation itself.')
outcomes_slide('3.8', [("layers", "Explain the layout negotiation: <b>propose</b>, choose, place"),
                       ("frame", "Predict what <code>.frame</code> and modifier order do"),
                       ("grid", "Use <code>GeometryReader</code> when you need geometry, and know its traps"),
                       ("diff", "Adapt with <code>ViewThatFits</code> instead of a fixed breakpoint"),
                       ("key", "Switch layouts with <code>AnyLayout</code> and keep state"),
                       ("check", "Test sizes, orientation, Dynamic Type and safe areas")])
where_slide('3.8', 'Today: layouts that adapt', (),
            '3.7: tokens and reusable components.',
            'Quick actions that fit any width and text size.',
            'Lesson 3.7 built the components. Today they learn to adapt to space and text size. Next lesson: environment and preferences.',
            'The milestone.')

# ================================================================== Part 1 (1)
divider(1, "The milestone", "Fixed layouts break", 'A row of quick actions on every screen size.', 'The problem.')
FX = """HStack(spacing: 12) {
    QuickAction(title: "Send")
    QuickAction(title: "Request")
    QuickAction(title: "History")
}"""
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "Fine on a wide screen; cramped with large text", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 230px 230px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Today&rsquo;s quick actions", FX, "font-size:14px")}
        <div class="step">{card("The goal", ul("Adapt to the <b>available space</b>", "Small screens, large screens, larger text"))}</div>
      </div>
      <div class="step">{crop("img/qa_fit.png", "iPhone 17, default text", 230)}</div>
      <div class="step">{TOP("img/qa_geo_ax.png", "Same row, largest text: &ldquo;Req…&rdquo;, &ldquo;Hist…&rdquo;", 230, 170)}</div>
    </div>
  </div>""", notes(('SAY', 'NPay&rsquo;s quick actions sit in a fixed HStack: Send, Request, History. On a wide screen that works.'),
                  ('SAY', 'Click: the goal: adapt to the available space. The text&rsquo;s simulator let you shrink the width and enlarge the text; we did it for real.'),
                  ('SAY', 'Click: an iPhone 17 at the default text size: three tidy buttons. Click: the same horizontal row at the largest accessibility text size: "Req…" and "Hist…". The labels no longer fit, and nothing in a fixed layout notices. That is today&rsquo;s problem.'),
                  ('CONNECT', 'First, how SwiftUI lays out at all.'))))

# ================================================================== Part 2 (2, 15)
divider(2, "The layout negotiation", "Propose, choose, place", 'Not frames and constraints: a conversation.', 'The model.')
P = []
for i, (ic, t, sub) in enumerate([("layers", "Parent proposes a size", "how much space is available?"), ("frame", "Child chooses its size", "how much does the content need?"), ("grid", "Parent places the child", "where should it appear?")]):
    x = i * 380
    P.append(tall(x, 0, 350, 112, ic, t, sub, f'{i + 1}', ''))
    if i < 2:
        P.append(wire(f'M{x + 352} 56H{x + 378}' + head(x + 378, 56, 'r')))
S.append(slide("Part 2 &middot; SwiftUI&rsquo;s layout system (section 2)", "A conversation between parent and child", f"""  <div class="body">
    {cues(3)}
    {svg('0 0 1110 112', 'Parent proposes a size, child chooses its size, parent places the child', 'neg', P, 'max-height:130px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("UIKit", ul("Frames and Auto Layout constraints"))}
      <div class="step">{card("SwiftUI", ul("Proposal-based: children decide their own size", "<code>Text(\"NPay\")</code> takes what its content needs"))}</div>
    </div>
  </div>""", notes(('SAY', 'In UIKit we think in frames and constraints. SwiftUI uses a proposal-based layout system, a conversation. Click: the parent proposes a size: here is how much space is available. Click: the child chooses its size: here is how much my content needs. Click: the parent places the child: where it should appear. This is a conceptual description of SwiftUI&rsquo;s layout protocol, and the next slide shows it really happening.'),
                  ('SAY', 'Click: the important insight: a child does not always take all the space it is offered. Text("NPay") picks a size from its content and the proposal.'),
                  ('CONNECT', 'Watch the conversation.'))))

PL = """struct ProposalLog: Layout {   // passes through, prints
    let name: String
    func sizeThatFits(proposal: ProposedViewSize,
                      subviews: Subviews, cache: inout ()) -> CGSize {
        let size = subviews[0].sizeThatFits(proposal)
        print("\\(name): proposed \\(proposal) → chose \\(size)")
        return size
    }
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize,
                       subviews: Subviews, cache: inout ()) {
        subviews[0].place(at: bounds.origin, proposal: proposal)
    }
}

VStack(spacing: 24) {
    ProposalLog(name: "Text") { Text("NPay") }
    ProposalLog(name: "maxWidth") {
        Text("NPay").frame(maxWidth: .infinity)
    }
    ProposalLog(name: "Color") { Color.blue }
}
.frame(width: 320, height: 300)"""
S.append(slide("Part 2 &middot; The negotiation, logged (sections 2, 15; authored experiment)", "A VStack of 320 points asks; each child answers", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      {code("A logging Layout (simplified: ours formats the sizes)", PL, "font-size:11px")}
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="step">{console("Probing: what's your smallest and largest?", ["Text: 320×0 &rarr; 39×24&ensp;&ensp;320×∞ &rarr; 39×24", "maxWidth: 320×0 &rarr; 320×24&ensp;320×∞ &rarr; 320×24", "Color: 320×0 &rarr; 320×0&ensp;&ensp;320×∞ &rarr; 320×∞"], 12)}</div>
        <div class="step">{console("Final proposals, then placement", ["Text: 320×84 &rarr; 39×24", "maxWidth: 320×113 &rarr; 320×24", "Color: 320×203 &rarr; 320×203"], 12)}</div>
        <div class="rule step" data-label="Read it">{ul("Text takes its content: 39×24", "<code>maxWidth: .infinity</code> = take the <b>proposed</b> width, not infinity", "Color takes whatever it is offered")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'To see the conversation, we wrote a tiny custom Layout, authored, that passes everything through to its single child and prints each proposal and the size the child chose. We wrapped three children in a VStack 320 points wide and 300 high: a plain Text, the same Text with frame maxWidth infinity, and a Color.'),
                  ('SAY', 'Click: first the VStack probes each child: what is your size if I offer zero height, and if I offer unlimited height? The Text answers 39 by 24 both times: it only needs its content. The maxWidth frame answers the full 320 wide. The Color is fully flexible: zero when offered zero, infinite when offered infinite.'),
                  ('SAY', 'Click: then the VStack shares out its 300 points, minus spacing, and makes final proposals: the Text still chooses 39 by 24; the frame 320 by 24; the Color takes the 203 left over. Click: Section 15&rsquo;s point, measured: maxWidth infinity does not make a view infinitely wide; it lets the frame expand to the proposed width.'),
                  ('CONNECT', 'Frames and modifier order.'))))

# ================================================================== Part 3 (3)
divider(3, "Frames and order", "Modifiers wrap layout", '.frame is not UIView.frame.', 'Two orders.')
OA = """// Example A
Text("NPay")
    .background(.blue)
    .frame(width: 200, height: 80)

// Example B
Text("NPay")
    .frame(width: 200, height: 80)
    .background(.blue)"""
S.append(slide("Part 3 &middot; How .frame() works; modifier order (section 3)", "Background first, or frame first?", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 300px;gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Two orders (red border: the 200×80 frame)", OA, "font-size:13.5px")}
        <div class="step">{card(".frame() is a view", ul("A new view description that takes part in layout", "Not a mutable <code>UIView.frame</code>"))}</div>
        <div class="rule step" data-label="Order matters for more than colour">{ul("Layout, hit testing, animation, rendering")}</div>
      </div>
      <div class="step">{crop("img/order.png", "A: background wraps the text &middot; B: background fills the frame", 300)}</div>
    </div>
  </div>""", notes(('SAY', 'Text("NPay").frame(width: 200, height: 80) is not assigning a UIView&rsquo;s frame property. It creates a modified view description, a frame view around the text, that takes part in the negotiation we just watched.'),
                  ('SAY', 'Click: so order matters. Example A puts the background on the text, then frames it: the background wraps the text&rsquo;s own size. Example B frames first, then adds the background: it covers the whole 200 by 80 region. Click: our screenshot: in A the blue hugs "NPay" inside the red frame; in B it fills the frame.'),
                  ('SAY', 'Click: the text&rsquo;s question: does order matter only for colours? No. It affects layout, hit testing, animation and rendering: a tap area or an animation attaches to whatever layer you put it on.'),
                  ('CONNECT', 'Sometimes a view needs to know its space: GeometryReader.'))))

# ================================================================== Part 4 (4, 5, 16)
divider(4, "GeometryReader", "Geometry, when you need it", 'A container that reports the space it was offered.', 'The experiment.')
GE = """struct GeometryExperiment: View {
    var body: some View {
        GeometryReader { geometry in
            VStack {
                Text("Width: \\(geometry.size.width)")
                Text("Height: \\(geometry.size.height)")
            }
        }
    }
}

geometry.size
geometry.safeAreaInsets
geometry.frame(in: .local)
geometry.frame(in: .global)"""
S.append(slide("Part 4 &middot; What is GeometryReader? (section 4, experiments 1&ndash;2)", "The proxy reports the offered space", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      {code("GeometryExperiment.swift", GE, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("GeometryProxy", ul("Size, safe-area insets, frames in coordinate spaces", "Read during layout"))}
        <div class="step">{tbl(["Device", "Reported size (pt)"], [("iPhone 17, portrait", "402 × 778"), ("iPhone 17, landscape", "750 × 382"), ("iPhone SE (3rd gen.)", "375 × 647"), ("iPad Air 11-inch", "820 × 1128")])}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'GeometryReader is a container that gives its content geometry information about the space offered to it. Its closure receives a GeometryProxy: the container&rsquo;s size, its safe-area insets, and its frame in coordinate spaces such as local and global.'),
                  ('SAY', 'Click: the text&rsquo;s first two experiments, on three simulators. iPhone 17 portrait: 402 by 778. Rotated to landscape: 750 by 382. iPhone SE: 375 by 647. iPad Air 11-inch: 820 by 1128.'),
                  ('SAY', 'Two details. These are the safe-area sizes: the status bar and home indicator are already excluded. And in landscape the iPhone 17 window is 874 wide, but the reader gets 750: the sides belong to the camera housing and rounded corners.'),
                  ('CONNECT', 'How it fits into layout.'))))

GF = [("layers", "Parent proposes space", "e.g. 390 × 700"), ("grid", "GeometryReader receives it", "generally expands to fill it"), ("eye", "Proxy exposes geometry", "size, coordinates"),
      ("diff", "Content builds layout", "chooses based on width"), ("play", "SwiftUI positions, renders", "the result is presented")]
P = []
for i, (ic, t, sub) in enumerate(GF):
    x = i * 228
    P.append(tall(x, 0, 208, 112, ic, t, sub, f'{i + 1}', ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 56H{x + 226}' + head(x + 226, 56, 'r')))
S.append(slide("Part 4 &middot; How GeometryReader participates in layout (section 5)", "It takes what it&rsquo;s offered", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1120 112', 'Parent proposes, GeometryReader receives, proxy exposes, content builds, SwiftUI renders', 'gf', P, 'max-height:130px')}
    <div class="gap"></div>
    <div class="warn step" data-label="Caution">{ul("It often takes <b>all</b> the space proposed", "Inside a ScrollView or VStack: surprises (next slide)")}</div>
  </div>""", notes(('SAY', 'The text&rsquo;s flow. Click: the parent proposes space, say 390 by 700. Click: GeometryReader receives the proposal and generally expands to fill it, like the Color in our log. Click: the proxy exposes that geometry. Click: the content builds its layout from it, for example NPay choosing an arrangement by width. Click: SwiftUI positions and renders the result.'),
                  ('SAY', 'Click: the caution: because it takes all the space it is offered, a GeometryReader used carelessly inside a ScrollView or a VStack can produce unexpected layout. Experiment 7.'),
                  ('CONNECT', 'Inside a ScrollView.'))))

GS = """ScrollView {
    GeometryReader { geometry in
        Text("Width: \\(geometry.size.width)")
    }

    GeometryReader { geometry in
        Text("Width: \\(geometry.size.width)")
    }
    .frame(height: 100)
}"""
S.append(slide("Part 4 &middot; Why GeometryReader sometimes behaves unexpectedly (sections 13, 16)", "In a ScrollView: 10 points tall", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 150px;gap:20px;align-items:start">
      {code("Experiment 7, then the fix", GS, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Measured GeometryReader sizes", ["no height:&ensp;&ensp;&ensp;&ensp;&ensp;402 × <b>10</b>", ".frame(height: 100): 402 × 100"], 13)}</div>
        <div class="step">{card("Why", ul("A vertical ScrollView proposes an <b>unspecified</b> height", "GeometryReader&rsquo;s ideal size is small: 10"))}</div>
      </div>
      <div class="step">{TOP("img/geoscroll.png", "Red borders: 10 pt, then 100 pt", 150, 160)}</div>
    </div>
  </div>""", notes(('SAY', 'Experiment 7: a GeometryReader inside a ScrollView with no height. You might expect it to fill the visible scroll area. Click: measured: 402 wide, 10 high.'),
                  ('SAY', 'Click: why: a vertical ScrollView proposes an unspecified height along the scrolling axis, it has no fixed height to give, and GeometryReader&rsquo;s ideal size for an unspecified dimension is small: here 10 points. The text overflows its 10-point box. The text&rsquo;s fix: give it an explicit height, 100, and the reader is 402 by 100, predictable.'),
                  ('SAY', 'Click: the screenshot: the first red box is a thin strip with the text spilling out; the second is 100 tall. The principle: use GeometryReader when you genuinely need geometry information, not as the default container for every responsive layout.'),
                  ('CONNECT', 'Now the adaptive quick actions.'))))

# ================================================================== Part 5 (6, 7, 17, 19)
divider(5, "Adaptive quick actions", "A breakpoint, or a fit?", 'Two versions of NPayQuickActions, measured.', 'The GeometryReader version.')
QG = """struct NPayQuickActions: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        GeometryReader { geometry in
            let isCompact = geometry.size.width < 350
            Group {
                if isCompact {
                    VStack(spacing: 12) { actions }
                } else {
                    HStack(spacing: 12) { actions }
                }
            }
        }
        .frame(height: 180)
    }

    @ViewBuilder
    private var actions: some View {
        QuickAction(symbol: "arrow.up.right", title: "Send",
                    action: onSend)
        // Request and History the same way
    }
}"""
S.append(slide("Part 5 &middot; Build adaptive quick actions with GeometryReader (section 6)", "Measure the width; switch below 350", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.9fr);gap:22px;align-items:start">
      {code("NPayQuickActions (section 6, condensed)", QG, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What it introduces", ul("GeometryReader measures the width", "A conditional picks HStack or VStack", "<code>@ViewBuilder</code> shares the actions; closures supply behaviour"))}
        <div class="warn step" data-label="The text&rsquo;s own warning">{ul("<code>.frame(height: 180)</code>: a teaching shortcut", "May waste space, or clip with larger text")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s first version: a GeometryReader measures the available width; below 350 points the three actions stack vertically, otherwise they sit in a row. @ViewBuilder lets one property supply the three QuickAction views to either stack, and the parent supplies behaviour through closures. QuickAction is Lesson 2.7&rsquo;s component, back in our code.'),
                  ('SAY', 'Click: the text itself flags the limitation: the fixed 180-point height is a teaching shortcut; it may waste space in the row and clip content with larger text. The next slide shows both happening.'),
                  ('CONNECT', 'What it did on three devices.'))))

S.append(slide("Part 5 &middot; The 350-point breakpoint, measured (sections 6, 17)", "Wrong in both directions", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 210px 210px;gap:18px;align-items:start">
      <div>{tbl(["Device, text size", "Width", "Chose", "Result"], [("iPhone 17, default", "370", "HStack", "fine; 180 pt mostly empty"), ("iPhone 17, largest", "370", "HStack", "<b>&ldquo;Req…&rdquo;, &ldquo;Hist…&rdquo;</b>"), ("iPhone SE, default", "343", "VStack", "<b>third button clipped</b> by 180 pt"), ("iPad Air 11, default", "788", "HStack", "fine")])}
        <div class="gap"></div>
        <div class="rule step" data-label="Section 17">{ul("350 assumes one breakpoint for every text size and language", "It failed at both a narrow width and a large text size")}</div></div>
      <div class="step">{crop("img/qa_geo_ax.png", "iPhone 17, largest text", 210)}</div>
      <div class="step">{crop("img/qa_geo_se.png", "iPhone SE: History below the 180-pt frame", 210)}</div>
    </div>
  </div>""", notes(('SAY', 'We put the GeometryReader version in a padded container on three simulators. The width column is what the reader measured. On the iPhone 17 at the default size, 370 points: a row, fine, but the fixed 180-point height leaves most of the box empty.'),
                  ('SAY', 'At the largest accessibility text size, still 370 points, so still a row; but the labels no longer fit: "Req…" and "Hist…". Click: the screenshot. On the iPhone SE at the default text size, 343 points, under 350, so it stacks vertically; but three stacked buttons need about 246 points and the frame is 180. Click: the History button sits below the red 180-point frame, outside the space the layout reserved, where the next view would overlap it.'),
                  ('SAY', 'Click: Section 17&rsquo;s point exactly: a check like width under 350 assumes 350 is the right breakpoint for every text size and language. Here it failed both ways: it stacked when a row would have fitted, and kept a row when the text did not fit.'),
                  ('CONNECT', 'The alternative: ask whether it fits.'))))

QF = """struct NPayQuickActions: View {
    let onSend: () -> Void
    let onRequest: () -> Void
    let onHistory: () -> Void

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 12) { actionViews }
            VStack(spacing: 12) { actionViews }
        }
    }

    @ViewBuilder
    private var actionViews: some View {
        // the same three QuickActions
    }
}"""
S.append(slide("Part 5 &middot; Better: ViewThatFits (sections 7, 19)", "The first candidate that fits wins", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("NPayQuickActions (section 19, condensed)", QF, "font-size:11px")}
        <div class="step">{card("Why better", ul("Decides by whether the content <b>fits</b>", "No fixed height; no device breakpoint"))}</div>
      </div>
      <div class="step">{tbl(["Device, text size", "ViewThatFits chose"], [("iPhone 17, default", "HStack"), ("iPhone 17, largest", "<b>VStack</b>, full width"), ("iPhone SE, default", "<b>HStack</b>: it fits"), ("iPhone SE, largest", "VStack"), ("iPad Air 11, default", "HStack")])}
        <div class="gap"></div>
        {TOP("img/qa_fit_se.png", "iPhone SE, default text: a row", 300, 90)}</div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI&rsquo;s ViewThatFits takes candidate views in order and uses the first one that fits the available space along the given axes, horizontal here. The text&rsquo;s improved NPayQuickActions offers an HStack first, then a VStack, with the same three actions. No GeometryReader, no fixed height.'),
                  ('SAY', 'Click: why better: the decision is whether the content fits, not an assumption about device width, which matters most with Dynamic Type. Click: measured: on the iPhone 17 a row at the default size and a full-width column at the largest size; on the SE a row, because it does fit, and a column at the largest size; on the iPad a row. Both of the breakpoint&rsquo;s mistakes are gone.'),
                  ('CONNECT', 'It is not magic, though.'))))

S.append(slide("Part 5 &middot; ViewThatFits: an important nuance (sections 7, 17)", "It judges ideal sizes, not truncation", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("How it decides", ul("Each candidate&rsquo;s <b>ideal</b> size along the axis", "Not a comparison with a hardcoded screen width"))}
        <div class="warn step" data-label="Not an overflow detector">{ul("Flexible content can &ldquo;fit&rdquo; while compressing or truncating", "QuickAction uses <code>maxWidth: .infinity</code>: its ideal width is its label")}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("So", ul("It worked here because the labels&rsquo; ideal widths grew with the text", "Still <b>test</b>: large text, other languages"))}</div>
        <div class="step">{card("Other tools (section 12)", ul("<code>AnyLayout</code>, grids, custom <code>Layout</code>, size classes"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s nuance. ViewThatFits evaluates candidates by their ideal sizing behaviour along the axes you give it. It is not a universal overflow detector: some flexible content reports that it fits while it compresses or truncates.'),
                  ('SAY', 'Click: our QuickAction is flexible, it uses frame maxWidth infinity, but its ideal width still comes from its icon and label, which grow with Dynamic Type, so the row stopped fitting at the largest size and ViewThatFits chose the column. Click: with different content that might not happen, so test the actual UI: large text sizes and localised labels.'),
                  ('SAY', 'Click: the text&rsquo;s trainer question: is ViewThatFits always the best adaptive solution? No: for complex responsive designs, custom Layout implementations, AnyLayout, grid containers and size-class-aware structures may be more appropriate.'),
                  ('CONNECT', 'AnyLayout.'))))

# ================================================================== Part 6 (8, 9, 18)
divider(6, "AnyLayout and identity", "Switch the layout, keep the children", 'Layout changes can reset state, or not.', 'AnyLayout.')
AL = """struct AdaptiveActions: View {
    let compact: Bool

    var body: some View {
        let layout = compact
            ? AnyLayout(VStackLayout(spacing: 12))
            : AnyLayout(HStackLayout(spacing: 12))

        layout {
            Text("Send")
            Text("Request")
            Text("History")
        }
    }
}"""
S.append(slide("Part 6 &middot; AnyLayout: switch the algorithm, keep the structure (section 8)", "One child list, two layouts", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("AdaptiveActions.swift", AL, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("AnyLayout", ul("Type-erases a <code>Layout</code>: <code>HStackLayout</code>, <code>VStackLayout</code>…", "Callable like a container: <code>layout { … }</code>"))}
        <div class="step">{card("Why it matters", ul("Not two branches with two structures", "The <b>same</b> children; only the algorithm changes"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'AnyLayout lets us choose between HStackLayout and VStackLayout at run time: both are Layout types, and AnyLayout erases which one, so a single variable can hold either. You call it like a container with the children in a closure.'),
                  ('SAY', 'Click: why it is interesting: instead of two separate branches that create two different layout structures, we switch the layout container while keeping the same child descriptions. That can preserve view identity across layout changes. Let&rsquo;s measure that.'),
                  ('CONNECT', 'The identity experiment.'))))

ID = """struct CounterView: View {
    @State private var count = 0
    var body: some View {
        Button("Count: \\(count)") { count += 1 }
    }
}

// AnyLayout (section 18)
let layout = vertical ? AnyLayout(VStackLayout())
                      : AnyLayout(HStackLayout())
layout { CounterView() }

// Branches (section 9)
if vertical {
    VStack { CounterView() }
} else {
    HStack { CounterView() }
}"""
S.append(slide("Part 6 &middot; AnyLayout and state identity (sections 9, 18)", "Count to 3, switch the layout", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Two ways to switch (condensed)", ID, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator: tap Count three times, then Switch Layout", ["AnyLayout:&ensp;Count: 3 &rarr; Count: <b>3</b>", "if / else:&ensp;Count: 3 &rarr; Count: <b>0</b>"], 13.5)}</div>
        <div class="rule step" data-label="Lesson 3.5 again">{ul("Branches: different structural positions, new identity", "AnyLayout: same position, same identity, state kept")}</div>
        <div class="step">{card("Adaptive design", ul("Consider identity, not only the arrangement"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s experiment. CounterView keeps a count in @State. In LayoutIdentityExperiment, from Section 18, a Switch Layout button toggles between a VStackLayout and an HStackLayout through AnyLayout. Section 9&rsquo;s alternative uses if and else with a VStack in one branch and an HStack in the other.'),
                  ('SAY', 'Click: we tapped Count three times and switched. With AnyLayout: still Count: 3. With the branches: Count: 0.'),
                  ('SAY', 'Click: Lesson 3.5 explains it: the two branches give CounterView different structural positions, so SwiftUI treats the switch as removing one counter and inserting another, and its state resets. AnyLayout keeps the child in the same position and only changes the algorithm, so the identity and the state survive. Click: adaptive layout design must consider identity, not only visual arrangement: a user&rsquo;s half-filled form should not reset because they rotated the phone.'),
                  ('CONNECT', 'Space the system reserves: safe areas.'))))

# ================================================================== Part 7 (10, 11, 20)
divider(7, "Beyond width", "Safe areas, text size, orientation", 'Responsive means more than a screen width.', 'Safe areas.')
SA = """ZStack {
    Color.blue.opacity(0.3)
    Text("default")
}

ZStack {
    Color.blue.opacity(0.3)
        .ignoresSafeArea()
    Text(".ignoresSafeArea()")
}"""
S.append(slide("Part 7 &middot; Safe areas (sections 10, 13)", "Extend backgrounds, not buttons", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 170px;gap:20px;align-items:start">
      {code("Experiment 6 (authored layout)", SA, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Safe areas", ul("Status bar, home indicator, other system boundaries", "Layout respects them by default"))}
        <div class="step">{card("<code>.ignoresSafeArea()</code>", ul("Good: a decorative <b>background</b>", "Bad: <b>interactive</b> controls under system gestures or cutouts"))}</div>
      </div>
      <div class="step">{PHONE("img/safe.png", "Left: default &middot; right: ignores", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'iPhones have system-managed areas: the status bar, the home indicator region, other interface boundaries. SwiftUI layout respects the safe area by default: content stays inside it, as our GeometryReader sizes showed.'),
                  ('SAY', 'Click: a background can be extended on purpose with ignoresSafeArea. Click: our experiment 6, two halves side by side: the left background stops at the safe area, leaving white at the top and bottom; the right one runs to the edges. Extending a decorative background is often right; placing interactive buttons under system gestures or the camera cutout usually is not.'),
                  ('CONNECT', 'Text size, again.'))))

S.append(slide("Part 7 &middot; Adaptive typography and Dynamic Type (section 11)", "Text grows; layouts must make room", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 170px 170px;gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("From 3.7", ul("<code>.headline</code>: 24.3 &rarr; 74.7 pt at the largest size", "<code>.system(size: 16)</code>: stays 19.3 pt"))}
        <div class="step">{card("Layout consequence", ul("An HStack that fits at the default size may not", "Adapt to <b>content</b>, not just device dimensions"))}</div>
        <div class="warn step" data-label="Found in our Home">{ul("At the largest size the balance wraps: &ldquo;₹25,000.0 / 0&rdquo;", "A money value must never split: fix in BalanceCard")}</div>
      </div>
      {PHONE("img/home.png", "Default text", 170)}
      <div class="step">{PHONE("img/home_ax.png", "Largest text", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'Lesson 3.7 measured it: semantic styles like headline scale with Dynamic Type, from 24 to almost 75 points; a fixed 16-point font does not. Prefer semantic styles, then test with larger accessibility sizes.'),
                  ('SAY', 'Click: why this is a layout topic: text takes more width and height as the size grows, so an HStack that fits at the default size can become cramped, as the quick actions showed. Adaptive layouts must consider content, not only device dimensions.'),
                  ('SAY', 'Click: and a finding in our own Home at the largest size: the balance card wraps the amount, "₹25,000.0" with the final zero on the next line. A money value must never split. A fix belongs in BalanceCard, for example keeping the amount on one line with a minimum scale factor, or switching layout with ViewThatFits; we leave it as the lab&rsquo;s last step.'),
                  ('CONNECT', 'Width is only one factor.'))))

FA = [("Available width", "iPhone SE 375 pt, iPhone 17 402 pt, iPad 820 pt"), ("Orientation", "landscape: 750 × 382 usable on iPhone 17"),
      ("Dynamic Type", "labels truncate; a row stops fitting"), ("Safe areas", "status bar, home indicator, side insets"),
      ("Localization", "longer translated labels"), ("Keyboard", "less visible content"),
      ("Multitasking", "iPad: variable window size; rotation can&rsquo;t be forced")]
S.append(slide("Part 7 &middot; Responsive design isn&rsquo;t only about width (section 20)", "Seven factors; we measured five", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:22px;align-items:start">
      <div>{tbl(["Factor", "Example (ours where measured)"], FA)}</div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("iPad Air 11, requestGeometryUpdate(landscape)", ["UISceneErrorDomain 101: &ldquo;The current windowing", "mode does not allow for programmatic", "changes to interface orientation.&rdquo;"], 11.5)}</div>
        <div class="rule step" data-label="Not a list of breakpoints">{ul("Adapt to the actual <b>content</b> and <b>space</b>")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A professional NPay interface considers several factors. Available width: our three simulators gave 375, 402 and 820 points. Orientation: 750 by 382 usable in landscape on the iPhone 17. Dynamic Type: truncation and rows that stop fitting. Safe areas. Localization: German or Tamil labels can be much longer. The keyboard: it takes away visible content. And multitasking: on iPad the window size varies.'),
                  ('SAY', 'Click: a multitasking detail we hit: on the iPad, asking the scene to rotate to landscape failed with "the current windowing mode does not allow for programmatic changes to interface orientation". On iPadOS the user and the windowing system are in charge of the window&rsquo;s shape, so layouts must handle whatever size they get.'),
                  ('SAY', 'Click: the text&rsquo;s distinction: a responsive layout is not a collection of hardcoded device breakpoints; it adapts to the actual content and the available space.'),
                  ('CONNECT', 'NPay, integrated.'))))

# ================================================================== Part 8 (12, 13, 21 + integration)
divider(8, "NPay, responsive", "Integrate and verify", 'The quick actions in Home, on every device.', 'A dashboard layout.')
DL = """struct NPayDashboardLayout<Content: View>: View {
    @ViewBuilder let content: Content

    var body: some View {
        ViewThatFits(in: .horizontal) {
            HStack(spacing: 16) { content }
            VStack(spacing: 16) { content }
        }
    }
}"""
S.append(slide("Part 8 &middot; A responsive dashboard layout (section 12)", "ViewThatFits, made generic", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("NPayDashboardLayout.swift", DL, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Adaptive composition", ul("3.7&rsquo;s generic <code>Content: View</code> + <code>@ViewBuilder</code>", "Any content: row if it fits, else column"))}
        <div class="step">{card("Note", ul("<code>content</code> appears in both candidates", "For complex content, prefer explicit layout components"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text generalises the idea: NPayDashboardLayout, generic over its content with @ViewBuilder, as in 3.7, wraps whatever it is given in a ViewThatFits with a row and a column.'),
                  ('SAY', 'Click: a note: the same content value is used in both candidates, which is fine for simple views; the text says that for complex content we often prefer more explicit layout components, and that AnyLayout, grids, custom layouts and size classes are other options.'),
                  ('CONNECT', 'Our integration.'))))

S.append(slide("Part 8 &middot; NPay Home with responsive quick actions (integration, authored)", "Same code, four environments", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:130px 130px minmax(0,1fr);gap:16px;align-items:start">
      {PHONE("img/home_se.png", "iPhone SE", 130)}
      <div class="step">{PHONE("img/home_ax.png", "iPhone 17, largest text", 130)}</div>
      <div class="step"><img src="img/homeland.png" alt="iPhone 17 landscape" style="width:100%;border:1px solid var(--line-2);border-radius:14px"><p class="shot-cap">iPhone 17, landscape</p>
        <p class="small muted" style="margin:8px 0 0">Home now uses NPayQuickActions (section 19): Send &rarr; Payments, History &rarr; History, Request &rarr; an alert (not in the demo).</p></div>
    </div>
  </div>""", notes(('SAY', 'The text names the integration as its remaining task; we did it, flagged as ours. Home now uses the Section 19 NPayQuickActions instead of the single Send Money button: Send selects the Payments tab, History the History tab, and Request, which NPay does not have, shows a short alert saying so. QuickAction comes back from Unit 2 for this.'),
                  ('SAY', 'On the iPhone SE, the actions fit in a row. Click: on the iPhone 17 at the largest text size, ViewThatFits switched them to a column; the balance wraps, the finding from Part 7. Click: in landscape, a wide row; the content keeps clear of the camera side.'),
                  ('CONNECT', 'The text&rsquo;s checklist.'))))

CK = [("Smaller iPhone simulator", "iPhone SE (3rd gen.): 375 pt; actions in a row"), ("Larger iPhone simulator", "iPhone 17: 402 pt; iPad Air 11: 820 pt"),
      ("Rotate to landscape", "750 × 382 usable; row of actions"), ("Increase Dynamic Type", "actions become a column; balance wraps (to fix)"),
      ("GeometryReader vs ViewThatFits", "breakpoint truncated and clipped; ViewThatFits didn&rsquo;t"), ("AnyLayout HStack ↔ VStack", "switches; same children"),
      ("CounterView survives the switch", "AnyLayout 3 &rarr; 3; branches 3 &rarr; 0"), ("Buttons usable, text readable", "yes, except the wrapped balance")]
S.append(slide("Part 8 &middot; Xcode verification lab (sections 13, 21)", "Eight checks, all run", f"""  <div class="body">
    {tbl(["Check", "Result (simulator)"], CK, 'tbl')}
    <p class="small muted" style="margin:6px 0 0">Debugging tip from section 13: <code>.border(.red)</code> shows container bounds; our screenshots use it.</p>
  </div>""", notes(('SAY', 'The text&rsquo;s practical checklist, run. A smaller iPhone, the SE: 375 points wide, actions in a row. Larger devices: the iPhone 17 at 402 and an iPad Air at 820. Landscape: 750 by 382 usable, a row of actions. Increased Dynamic Type: the actions become a column; the balance wraps, which we flagged. GeometryReader versus ViewThatFits: the breakpoint version truncated and clipped; ViewThatFits did not. AnyLayout switches between row and column with the same children, and the counter survives; branches reset it. And the buttons stay usable and readable, apart from the balance.'),
                  ('SAY', 'The text&rsquo;s debugging tip, borders, is in our screenshots: every red line on the quick-action and ScrollView pictures is a .border(.red).'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.8', (), [("layers", "Propose, choose, place", "children size themselves; maxWidth means the proposed width"),
                     ("diff", "Fit, don&rsquo;t guess", "ViewThatFits over a 350-pt breakpoint; test anyway"),
                     ("key", "Adapt without resetting", "AnyLayout keeps identity; respect safe areas and text size")],
         'Three things to remember. SwiftUI layout is a negotiation: the parent proposes, the child chooses, the parent places; that is why Text takes 39 points and maxWidth infinity means the proposed width. Adapt to content rather than guessed breakpoints: GeometryReader is for real geometry needs and misbehaves in a ScrollView, while ViewThatFits picks what fits, though you still test large text and other languages. And adapt without breaking things: AnyLayout switches arrangement while keeping identity and state, backgrounds may extend into the safe area but controls should not, and text must stay whole at every size.')

review_divider(10)
review([("layers", "Choose one", "What is SwiftUI's core layout negotiation?",
         "What is SwiftUI&rsquo;s core layout negotiation model?<br>A. Every view uses absolute coordinates<br>B. Parent proposes, child chooses, parent places<br>C. Only Auto Layout constraints", "B",
         "Our log: proposed 320×0 &rarr; chose 39×24 for Text.",
         "Thinking in UIKit frames.", "Most pick B.", None),
        ("grid", "Choose one", "What does GeometryReader provide?",
         "What does <code>GeometryReader</code> provide?<br>A. Network data<br>B. Persistent storage<br>C. Geometry information from its layout context", "C",
         "402 × 778 on iPhone 17; 820 × 1128 on iPad Air.",
         "Using it for everything responsive.", "Most pick C.", None),
        ("frame", "Choose one", "Why can GeometryReader misbehave in a ScrollView?",
         "Why can <code>GeometryReader</code> be problematic inside a <code>ScrollView</code>?<br>A. It always crashes<br>B. Its sizing interacts unexpectedly with scroll-axis proposals<br>C. It disables SwiftUI", "B",
         "Unspecified height &rarr; 10 points tall.",
         "Expecting it to fill the scroll area.", "Most pick B.", None),
        ("diff", "Choose one", "What is ViewThatFits useful for?",
         "What is <code>ViewThatFits</code> useful for?<br>A. Choosing content that fits available space<br>B. Persisting payment data<br>C. Routing between screens", "A",
         "Row on the SE, column at the largest text size.",
         "Expecting it to detect truncation.", "Most pick A.", None),
        ("key", "Choose one", "Why use AnyLayout?",
         "Why use <code>AnyLayout</code>?<br>A. To erase application state<br>B. To create threads<br>C. To switch layout algorithms while retaining child structure", "C",
         "Same children, HStackLayout or VStackLayout; the counter kept 3.",
         "Writing two branches.", "Most pick C.", None),
        ("eye", "Question", "Does a fixed width breakpoint account for Dynamic Type?",
         "Does a fixed screen-width breakpoint always account for Dynamic Type?", "No",
         "At 370 points and the largest text: &ldquo;Req…&rdquo;, &ldquo;Hist…&rdquo;.",
         "Designing for one text size.", "Most say no.", None),
        ("phone", "Predict the result", "iPhone SE, default text: which stack?",
         "On an iPhone SE the quick actions get 343 points; at the default text size a row of three fits. With the <code>width &lt; 350</code> version, what do you get?<br>A. A row<br>B. A column, clipped by the 180-point frame<br>C. Nothing", "B",
         "343 &lt; 350: VStack; three buttons need about 246 points.",
         "Trusting the breakpoint.", "Some pick A.", None),
        ("grid", "Predict the result", "GeometryReader in a ScrollView, no height?",
         "<code>ScrollView {{ GeometryReader {{ … }} }}</code> on an iPhone 17, no height given. Its size?<br>A. 402 × 778<br>B. 402 × 10<br>C. 0 × 0".replace('{{', '{').replace('}}', '}'), "B",
         "The unspecified scroll-axis height leaves its ideal size: 10.",
         "Expecting it to fill the screen.", "Many pick A.", None),
        ("clock", "Predict the result", "if/else between HStack and VStack: the counter?",
         "CounterView shows Count: 3. A Switch Layout button toggles between <code>if vertical {{ VStack {{ CounterView() }} }} else {{ HStack {{ … }} }}</code>. After switching?<br>A. Count: 3<br>B. Count: 0".replace('{{', '{').replace('}}', '}'), "B",
         "Different branches, new identity; AnyLayout kept 3.",
         "Thinking a layout change is cosmetic.", "Some pick A.", None),
        ("code", "Choose one", "From 3.7: which font scales with Dynamic Type?",
         "From Lesson 3.7: which of these scales with the user&rsquo;s text size?<br>A. <code>.font(.system(size: 16))</code><br>B. <code>.font(.headline)</code>", "B",
         "Headline 24.3 &rarr; 74.7 pt; the fixed 16 pt stayed 19.3.",
         "Using fixed sizes for UI text.", "Most pick B.", "Spaced review from Lesson 3.7.")])

S.append(next_slide('3.8', [("3.9", "SwiftUI environment &amp; preferences", "custom environment values, themes, @Environment, @EnvironmentObject"),
                            ("3.10", "Accessibility", "Dynamic Type, motion and more, in depth")],
                    'Lesson 3.9 explores environment propagation and preferences: custom environment values, theme management, @Environment and @EnvironmentObject, so NPay can share configuration without passing every value through each layer. Lesson 3.10 is accessibility in depth, including the Dynamic Type issues we found today.'))

S.append(lab_slide('3.8', "A responsive NPay", "Make Home adapt; prove it on three devices.",
                   ["Show the available width with GeometryReader.",
                    "Run both NPayQuickActions on an SE and an iPhone 17.",
                    "Switch to the largest text size; compare.",
                    "Count to 3; switch layouts with AnyLayout, then branches.",
                    "Rotate; check safe areas with <code>.border(.red)</code>.",
                    "Stop the balance wrapping at the largest size."],
                   "", 'Expected, as in our run: 375 pt on the SE and 402 pt on the iPhone 17; the 350-pt version stacks and clips on the SE and truncates at the largest size, while ViewThatFits keeps a row on the SE and switches to a column at the largest size; AnyLayout keeps Count: 3 and branches reset it; the balance must stay on one line.',
                   side=f'<div>{card("You hand in", ul("Screenshots: SE, iPhone 17 large text, landscape", "Your counter results", "Your BalanceCard fix"))}</div>'))

end_slide('3.8', 'Adaptive Layouts<br>&amp; GeometryReader', 'Lesson 3.9 &mdash; SwiftUI Environment &amp; Preferences',
          'You can now explain the propose-choose-place negotiation, predict what frames and modifier order do, use GeometryReader for real geometry and avoid its ScrollView trap, prefer ViewThatFits to fixed breakpoints, switch layouts with AnyLayout without losing state, and test width, orientation, Dynamic Type, safe areas and multitasking.',
          'Next, Lesson 3.9: SwiftUI environment and preferences: sharing configuration such as themes across NPay without passing it through every layer.')

write_deck(OUT38, '3.8', 'Adaptive Layouts', 'Adaptive Layouts')
