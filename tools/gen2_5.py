"""Generates decks/unit-2/lesson-2.5/index.html from the Lesson 2.5 text (ZStack: Layering, Backgrounds & SwiftUI Rendering).
The 11 sections are grouped into 8 Parts. Console output and screenshots come from tools/sim2_5 (a scripted SwiftUI
app run in the iOS Simulator); interface lines from the iOS 26.5 SDK. The text has no knowledge check: the review is authored."""
import html, os, re, sys
OUT25 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.5', 'ZStack: Layering, Backgrounds<br>&amp; SwiftUI Rendering',
            'NPay&rsquo;s first balance card. How does SwiftUI put one view <b>on top of</b> another, size them, and decide which is <b>in front</b>?',
            'We have built NPay&rsquo;s welcome screen from Text, Image, VStack and HStack. Today it gets something that looks like a real payment app: a balance card. The deeper goal: how SwiftUI places views on top of other views, how it sizes them, and how it decides which one is in front. ZStack, Z-order, sizing, alignment, backgrounds, overlays and rendering, all checked in the iOS Simulator.')
outcomes_slide('2.5', [("layers", "What <code>ZStack</code> does on the <b>depth</b> axis"),
                       ("eye", "Which view is <b>in front</b>, and <code>.zIndex</code>"),
                       ("layout", "How a ZStack <b>sizes</b> itself"),
                       ("frame", "<code>Alignment</code> inside a ZStack"),
                       ("diff", "ZStack vs <code>.background</code> vs <code>.overlay</code>"),
                       ("check", "NPay&rsquo;s <b>balance card</b>, step by step")])
where_slide('2.5', 'Today: the balance card', (),
            '2.4: an <code>HStack</code> of quick actions under the title.',
            'A <code>ZStack</code>: text layered over a card.',
            'Last lesson NPay got a row of quick actions. Today we add the first card: text layered over a coloured shape. VStack and HStack arranged views next to each other; ZStack puts them on top of each other.',
            'The target.')

# ================================================================== Part 1 (1)
divider(1, "A balance card", "Layers, not rows", 'NPay needs a balance card between the title and the actions.', 'Before and after.')
S.append(slide("Part 1 &middot; NPay needs a balance card (section 1)", "Milestone 2.5: the balance card", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Add", ul("A <b>card</b>: label, balance, account name", "Text <b>on top of</b> a coloured shape"))}
        {card("For now", ul("A fixed demo balance: <b>₹25,000</b>", "Real balance and state: later"))}
      </div>
      {PHONE("img/before.png", "Before: Lesson 2.4", 190)}
      <div class="step">{PHONE("img/final.png", "After: Milestone 2.5", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'Our app has a payment icon, the NPay title, a subtitle and three quick actions. Now we want a balance card: "Available Balance", the amount, and the account name, on a blue card.'),
                  ('SAY', 'Click: the result we build today. The balance is a fixed demonstration value, ₹25,000; real balance updates and state management come later.'),
                  ('CONNECT', 'The new tool: ZStack.'))))

# ================================================================== Part 2 (2)
divider(2, "ZStack", "The depth axis", 'VStack: vertical. HStack: horizontal. ZStack: depth.', 'The smallest ZStack.')
BASIC = """ZStack {
    Color.blue

    Text("NPay")
        .foregroundStyle(.white)
}
.frame(width: 240, height: 140)"""
IFACE = """@frozen public struct ZStack<Content> : View
        where Content : View {
    public init(alignment: Alignment = .center,
                @ViewBuilder content: () -> Content)
}"""
S.append(slide("Part 2 &middot; What exactly is ZStack? (section 2)", "Children share the same space", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", BASIC, "font-size:15px")}
        <div class="gap"></div>
        {crop("img/basic.png", "240 × 140 pt, measured", 380)}</div>
      <div>
        <div class="step">{code("Interface excerpt, iOS 26.5 SDK (body omitted)", IFACE, "font-size:13.5px")}</div>
        <div class="gap"></div>
        <div class="step">{console("type(of:) in the simulator", ["ZStack&lt;TupleView&lt;(Color, Text)&gt;&gt;"], 14)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="The difference">{ul("Same <code>@ViewBuilder</code> closure as VStack", "Children are <b>aligned in overlapping</b> space")}</div></div>
    </div>
  </div>""", notes(('SAY', 'VStack arranges children vertically, HStack horizontally; ZStack overlays them along the depth axis. Here Color.blue fills the frame as a background layer, and the white text sits above it. On the left, the simulator: 240 by 140 points.'),
                  ('SAY', 'Click: like the other stacks, ZStack is a generic struct conforming to View. Its initializer takes an Alignment, a full two-dimensional alignment, defaulting to .center, and the same @ViewBuilder content closure. Click: the printed type is ZStack of a TupleView of Color and Text: Color is a View too.'),
                  ('SAY', 'Click: the difference is layout. Instead of placing children one after another, ZStack aligns them within overlapping space.'),
                  ('CONNECT', 'If they overlap, which one is in front?'))))

# ================================================================== Part 3 (3-4)
divider(3, "Z-order", "Who is in front", 'Three children in one ZStack.', 'Change the order.')
ORD = """ZStack {
    Color.blue
    Color.green
    Text("NPay")
}
.frame(width: 240, height: 140)"""
S.append(slide("Part 3 &middot; Which view appears in front? (section 3)", "Later children are drawn on top", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 300px;gap:28px;align-items:start">
      <div>{code("ContentView.swift", ORD, "font-size:16px")}
        <div class="gap"></div>
        {card("Source order = drawing order", ul("Green covers blue", "The text, last, is on top"))}
        <div class="gap"></div>
        <div class="rule step" data-label="Reverse it">{ul("<code>Text</code> first: <b>hidden</b> under both colours", "Source order changes the layering")}</div></div>
      {crop("img/order.png", "Middle: Text, Blue, Green", 300)}
    </div>
  </div>""", notes(('SAY', 'Blue, then green, then the text. In a ZStack, later children are normally drawn above earlier ones: green covers blue completely, and the text is on top. That is the top card on the right; it replaces the text&rsquo;s layer explorer.'),
                  ('SAY', 'Click: the middle card has the same three children with the text first. It is drawn first, so both colours cover it: the text is still there, but you cannot see it. Changing the source order changes the layering, unless you adjust it explicitly. The bottom card shows how.'),
                  ('CONNECT', 'The explicit adjustment: zIndex.'))))

ZI = """ZStack {
    Text("Behind")
        .zIndex(0)

    Text("In Front")
        .zIndex(1)
}"""
S.append(slide("Part 3 &middot; What is .zIndex()? (section 4)", "<code>.zIndex</code> changes drawing order only", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", ZI, "font-size:16px")}
        <div class="gap"></div>
        {card("Higher zIndex", ul("Drawn <b>above</b> siblings with lower values"))}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Rescue the hidden text", ul("<code>Text(\"NPay\").zIndex(1)</code>, still written <b>first</b>", "Visible again: bottom card, previous slide"))}</div>
        <div class="rule step" data-label="It does not">{ul("Change size, position or layout priority", "Create a window or process")}</div>
        <div class="step">{card("Observed", ul("Works on the stack&rsquo;s <b>direct</b> child", "Wrapped in another modifier, it had no effect"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', '.zIndex controls relative drawing order: a larger value generally places a view above siblings with lower values in the same stacking context.'),
                  ('SAY', 'Click: our bottom card on the previous slide: the text still comes first in the source, but with zIndex(1) it is drawn above both colours.'),
                  ('SAY', 'Click: zIndex only changes visual stacking. It does not change a view&rsquo;s size, position or layout priority, and it does not create a separate window or process.'),
                  ('SAY', 'Click: something we hit while measuring: when we put another modifier after .zIndex, so that zIndex was no longer on the outermost layer of the ZStack&rsquo;s child, it had no effect. Put .zIndex last on the child.'),
                  ('CONNECT', 'Drawing order is settled. Now size: how big is a ZStack?'))))

# ================================================================== Part 4 (5)
divider(4, "ZStack sizing", "Overlap, don&rsquo;t add", 'A 300 × 180 rectangle and a small text.', 'ZStack vs VStack.')
SZ = """ZStack {
    Rectangle().fill(.blue)
        .frame(width: 300, height: 180)
    Text("NPay")
}

VStack {   // same children
    Rectangle().fill(.blue)
        .frame(width: 300, height: 180)
    Text("NPay")
}"""
S.append(slide("Part 4 &middot; How does ZStack calculate its size? (section 5)", "Same children, different sizes", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 280px;gap:24px;align-items:start">
      {code("Sizes.swift", SZ, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Measured (red border)", ["ZStack: 300.0 × 180.0 pt", "VStack: 300.0 × 212.9 pt"], 14)}</div>
        <div class="rule step" data-label="Careful">{ul("Here, the size of the <b>largest</b> child", "Not a rule: proposals and flexibility decide")}</div></div>
      {crop("img/size.png", "Top: ZStack. Bottom: VStack", 280)}
    </div>
  </div>""", notes(('SAY', 'A blue rectangle requesting 300 by 180 points and a small text, once in a ZStack and once in a VStack, each with a red border. Under ordinary conditions a ZStack considers its children&rsquo;s sizes and alignment, but it does not add their heights.'),
                  ('SAY', 'Click: measured. The ZStack is 300 by 180, the rectangle&rsquo;s size; the text sits inside it. The VStack is 212.9 tall: the rectangle, the default spacing and the text, one after another. That replaces the text&rsquo;s toggle.'),
                  ('SAY', 'Click: in this case the ZStack took the size of its largest child, but do not turn that into a rule. ZStack sizing depends on proposals, child flexibility and alignment; a flexible child like Color takes whatever it is offered.'),
                  ('CONNECT', 'Inside that space, where does each child go? Alignment.'))))

# ================================================================== Part 5 (6)
divider(5, "ZStack alignment", "Two axes at once", 'ZStack centres its children by default.', 'Move the text.')
ALG = """ZStack(alignment: .topLeading) {
    Color.blue

    Text("NPay")
        .foregroundStyle(.white)
        .padding()
}
.frame(width: 300, height: 180)"""
S.append(slide("Part 5 &middot; Alignment inside ZStack (section 6)", "<code>.topLeading</code>: top <b>and</b> leading", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 300px;gap:28px;align-items:start">
      <div>{code("ContentView.swift", ALG, "font-size:15px")}
        <div class="gap"></div>
        {card("An Alignment value", ul("Vertical <b>and</b> horizontal: <code>.topLeading</code>, <code>.center</code>, <code>.bottomTrailing</code>, &hellip;", "<code>alignment:</code> expects <code>Alignment</code>, so the shorthand is inferred"))}</div>
      {crop("img/align.png", "Run at 300 × 150 to fit all three", 300)}
    </div>
  </div>""", notes(('SAY', 'ZStack centres by default. With alignment .topLeading the text goes to the top-leading corner; its padding keeps it off the edge. Unlike VStack&rsquo;s HorizontalAlignment or HStack&rsquo;s VerticalAlignment, a ZStack has both axes free, so it takes an Alignment: a vertical and a horizontal part together.'),
                  ('SAY', 'The shorthand works because alignment: expects an Alignment value, contextual type inference again. On the right, .topLeading, .center and .bottomTrailing in the simulator, run at 150 points tall so all three fit; the text&rsquo;s buttons showed the same idea conceptually.'),
                  ('CONNECT', 'ZStack is not the only way to layer. Two modifiers do it too.'))))

# ================================================================== Part 6 (7)
divider(6, "ZStack, background, overlay", "Three ways to layer", 'All three layer views. Their size rules differ.', 'Compare.')
CMP = [("Purpose", "general overlapping layout", "content <b>behind</b> a view", "content <b>over</b> a view"),
       ("Size", "considers participating children", "follows the primary view", "follows the primary view"),
       ("Typical use", "complex layered composition", "card backgrounds", "badges, labels, decoration")]
S.append(slide("Part 6 &middot; ZStack vs .background() vs .overlay() (section 7)", "Who decides the size?", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 250px;gap:28px;align-items:start">
      <div>{tbl(["", "ZStack", ".background", ".overlay"], CMP)}
        <div class="gap"></div>
        <div class="step">{console("Measured (pt)", ["ZStack 240 × 120 · background 110.3 × 92.3", "overlay 240 × 120 · oversized overlay 240 × 120"], 13)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="Choose">{ul("Layers that <b>share</b> a layout: ZStack", "Visual <b>attached</b> to one view: background / overlay")}</div></div>
      {crop("img/layering.png", "Bottom: the overlay spills", 250)}
    </div>
  </div>""", notes(('SAY', 'Three ways to get layered visuals. A ZStack: its children take part in one layout together. .background: the background is attached to the modified view, behind it, and its size follows that view&rsquo;s layout region. .overlay: content laid out relative to the primary view, over it, and it generally does not decide the primary view&rsquo;s size.'),
                  ('SAY', 'On the right, top to bottom: the ZStack, the padded text with a blue background, the rounded rectangle with a text overlay, and the same rectangle with an overlay that is far too big. Click: the measurements. The background version is exactly the padded text, 110 by 92: the background followed the text. Both overlay versions are 240 by 120: the oversized text spills over the edges, drawn in black so you can see it, and the shape does not grow.'),
                  ('SAY', 'Click: the decision. Use ZStack when several layers should participate in one layered layout; use background and overlay when the visual naturally belongs to one primary view.'),
                  ('CONNECT', 'Now build NPay&rsquo;s card, one step at a time.'))))

# ================================================================== Part 7 (8-9)
divider(7, "Build the balance card", "Shape, text, structure", 'Three steps from a blue shape to a balance card.', 'Step A.')
STEPC = """ZStack {
    RoundedRectangle(cornerRadius: 20)
        .fill(.blue)

    VStack(alignment: .leading, spacing: 12) {
        Text("Available Balance")
            .font(.subheadline)
        Text("₹25,000")
            .font(.largeTitle.bold())
        Text("NPay Demo Account")
            .font(.caption)
    }
    .foregroundStyle(.white)
    .frame(maxWidth: .infinity, alignment: .leading)
    .padding(24)
}
.frame(height: 180)"""
S.append(slide("Part 7 &middot; Build the card incrementally (section 8)", "Step A, B, C", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.7fr) 250px;gap:24px;align-items:start">
      {code("Step C", STEPC, "font-size:12.5px")}
      <div class="step">{card("Step C", ul("<b>Shape</b>: the background layer", "<b>VStack</b>: the text, top to bottom", "<b>Padding</b>: away from the edges"))}</div>
      {crop("img/steps.png", "Steps A, B (150 pt) and C", 250)}
    </div>
  </div>""", notes(('SAY', 'Step A: a RoundedRectangle, a SwiftUI shape, filled blue; .fill(.blue) describes its fill style and the frame constrains its height. Step B: put it in a ZStack with the balance on top: the text appears over the card. On the right, the top two cards; in the simulator we ran them 150 points tall so all three steps fit on one screen.'),
                  ('SAY', 'Step C, the code on the left: a label, the balance and the account name in a VStack aligned leading, white, stretched to the full width with leading alignment, and padded by 24. Click: the ZStack creates the overlapping layers, the RoundedRectangle is the background, the VStack organises the text, and the padding keeps it away from the card edges.'),
                  ('CONNECT', 'What does SwiftUI actually create for this?'))))

P = [box(380, 0, 300, 56, 'ZStack', 'the card', None, 'lit', 'layers'),
     wire('M450 60V92H170V120' + head(170, 120, 'd')), wire('M610 60V92H890V120' + head(890, 120, 'd')),
     box(20, 126, 300, 56, 'RoundedRectangle', 'background layer', None, '', 'frame'),
     box(740, 126, 300, 56, 'VStack', 'text content layer', None, '', 'file'),
     wire('M170 186V216H530V240' + head(530, 240, 'd'), None, 'faint'), wire('M890 186V216H530', None, 'faint'),
     box(380, 246, 300, 56, 'Layout + rendering', 'SwiftUI, internally', None, '', 'gear')]
S.append(slide("Part 7 &middot; How SwiftUI composes the card (section 9) &middot; conceptual", "One description, rendered by SwiftUI", f"""  <div class="body">
    {svg('0 0 1060 302', 'The ZStack has a RoundedRectangle background layer and a VStack text layer; SwiftUI does layout and rendering', 'comp', P, 'max-height:300px')}
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("One CALayer per child?", ul("<b>Not necessarily</b>", "SwiftUI manages rendering internally"))}
      {card("What the API promises", ul("The declarative <b>layout</b> and <b>drawing</b>", "Not a one-to-one map to layers"))}
    </div>
  </div>""", notes(('SAY', 'Conceptually the card is a ZStack with two children: the RoundedRectangle as the background layer and the VStack as the text layer, then layout and rendering. The word layer here is about drawing order, not a specific object.'),
                  ('SAY', 'Click: does SwiftUI create a separate CALayer for each child? Not necessarily. SwiftUI manages its rendering representations internally. The public API guarantees the declarative layout and drawing behaviour, not a fixed one-to-one mapping to Core Animation layers. That is the same caution as Lesson 2.1&rsquo;s "does every Text create a UILabel?".'),
                  ('CONNECT', 'Put the card into NPay.'))))

# ================================================================== Part 8 (10-11)
divider(8, "NPay with its card", "Milestone 2.5", 'The card goes between the subtitle and the quick actions.', 'The final screen.')
S.append(slide("Part 8 &middot; Complete NPay code (section 10)", "Milestone 2.5: the welcome screen with a card", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 200px;gap:32px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("The screen, top to bottom", ul("<code>VStack(spacing: 28)</code>", "Icon (now 48 pt), title, subtitle", "<b>New</b>: the Step C card, 180 pt tall", "Quick actions, <code>HStack(spacing: 30)</code>", "<code>.padding()</code>"))}
        <div class="rule step" data-label="One new component">{ul("Everything from 2.1&ndash;2.4 kept", "The card: a ZStack inside the VStack")}</div>
      </div>
      {PHONE("img/final.png", "Milestone 2.5", 200)}
    </div>
  </div>""", notes(('SAY', 'The complete code is in the lesson text and is long, so here is its structure. The outer VStack now has spacing 28. The symbol is 48 points instead of 64, then the title and subtitle. Then the new part: Step C&rsquo;s ZStack card, 180 points tall. Then the quick actions, now with spacing 30. The whole stack is padded. On the right, the real screen.'),
                  ('SAY', 'Click: we preserved every feature from the earlier lessons and added exactly one component: the balance card, a ZStack nested in the screen&rsquo;s VStack.'),
                  ('CONNECT', 'Three experiments from the text, run for real.'))))

BG = """VStack(alignment: .leading, spacing: 12) {
    Text("Available Balance")
    Text("₹25,000")
    Text("NPay Demo Account")
}
.foregroundStyle(.white)
.padding(24)
.frame(maxWidth: .infinity, alignment: .leading)
.frame(height: 180)
.background(.blue, in: RoundedRectangle(cornerRadius: 20))"""
S.append(slide("Part 8 &middot; Experiments to run (section 11)", "The same card with <code>.background(_:in:)</code>", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr) 260px;gap:22px;align-items:start">
      <div>{code("Experiment C", BG, "font-size:12.5px")}
        <div class="step" style="margin-top:10px">{console("Measured", ["ZStack card: 370.0 × 180.0 pt", "background card: 370.0 × 180.0 pt"], 13)}</div></div>
      {card("Experiments A and B", ul("<b>A</b>: shape after the text: it <b>covers</b> it (Part 3)", "<b>B</b>: <code>.topLeading</code>: <b>no visible change</b>; the VStack already fills the card"))}
      {crop("img/compare.png", "Top: ZStack. Bottom: background", 260)}
    </div>
  </div>""", notes(('SAY', 'The text suggests three experiments. A: reverse the layers; the shape drawn after the text covers it, exactly what we saw in Part 3. B: give the card&rsquo;s ZStack .topLeading alignment; because the inner VStack already stretches to the full width and is padded, the difference is subtle to invisible.'),
                  ('SAY', 'C: build the card without a ZStack, using .background with a shape: background(.blue, in: RoundedRectangle). On the right, both versions, run with plain text so the comparison is fair. Click: same size, 370 by 180, and the same look.'),
                  ('SAY', 'For a card, whose shape is just the backdrop of its content, .background is the natural tool; a ZStack earns its place when several layers each take part in the layout.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.5', (), [("layers", "Later is in front", "source order; .zIndex when needed"),
                     ("layout", "ZStack overlaps", "sizes don&rsquo;t add; proposals decide"),
                     ("frame", "Attach or compose", "background/overlay vs ZStack")],
         'Three things to remember. In a ZStack later children are drawn in front; .zIndex changes only that drawing order. A ZStack overlaps its children instead of adding their sizes, and its exact size depends on proposals and flexibility. And background and overlay attach a visual to one primary view, whose size wins, while a ZStack composes layers that take part in one layout.')

review_divider(7)
review([("layers", "Question", "In a ZStack, is a later child drawn above an earlier one?",
         "In a <code>ZStack</code>, is a later child normally drawn above an earlier one?", "Yes",
         "Blue, then green, then the text: green covered blue and the text was on top.",
         "Thinking the first child is the front.", "Most say yes.", None),
        ("eye", "Predict the result", "ZStack { Text; Color.blue; Color.green }: what do you see?",
         "What do you see?<br><code>ZStack { Text(\"NPay\"); Color.blue; Color.green }</code><br>A. Green, with NPay on top<br>B. Only green<br>C. Blue and green side by side", "B",
         "The text is drawn first, so both colours cover it.",
         "Expecting text to float above colours automatically.", "Some pick A.", None),
        ("gear", "Question", "Does .zIndex(1) make a view larger?",
         "Does <code>.zIndex(1)</code> change a view&rsquo;s size or position?", "No",
         "It only changes drawing order among siblings; layout is untouched.",
         "Confusing zIndex with layoutPriority.", "Some say yes.", None),
        ("layout", "Choose one", "ZStack { 300 × 180 rectangle; Text }: how tall?",
         "<code>ZStack</code> with a 300 &times; 180 pt rectangle and a small Text. How tall is it?<br>A. 180 pt<br>B. 180 pt + the text&rsquo;s height<br>C. The whole screen", "A",
         "Measured 300 &times; 180 pt; the same children in a VStack measured 212.9 pt tall.",
         "Adding heights as a VStack does.", "Some pick B.", None),
        ("frame", "Choose one", "Which follows the primary view's size?",
         "Which layering tool lets the <b>primary view</b> decide the size?<br>A. <code>ZStack</code><br>B. <code>.background</code> and <code>.overlay</code><br>C. <code>.zIndex</code>", "B",
         "An oversized overlay spilled over the edges; the shape stayed 240 &times; 120 pt.",
         "Expecting an overlay to grow its view.", "Some pick A.", None),
        ("diff", "Question", "Does every ZStack child get its own CALayer?",
         "Does SwiftUI create a separate <code>CALayer</code> for every child of a ZStack?", "Not necessarily",
         "Rendering is internal; the API promises layout and drawing, not a layer per view.",
         "Mapping SwiftUI views one-to-one onto Core Animation objects.", "Some say yes.", None),
        ("phone", "Question", "From 2.4: does HStack give children equal widths?",
         "From Lesson 2.4: does a plain <code>HStack</code> give its children equal widths?", "No",
         "Plain Texts kept their own widths (39.3, 62.7, 54.7 pt); only flexible frames shared equally.",
         "Imagining equal columns.", "Some say yes.", "Spaced review from Lesson 2.4.")])

S.append(next_slide('2.5', [("Later", "State management", "a real, changing balance instead of ₹25,000"),
                            ("2.6", "SwiftUI view modifiers", "background, overlay and the environment in depth")],
                    'The lesson text points ahead to real balance updates and state management, which replace today&rsquo;s fixed ₹25,000. Next lesson, 2.6, looks at modifiers in depth: background, overlay, order and the environment.'))

S.append(lab_slide('2.5', "Layer the card yourself", "Run the text&rsquo;s three experiments. Predict first.",
                   ["<b>A</b>: move the shape before, then after, the VStack.",
                    "<b>B</b>: <code>ZStack(alignment: .topLeading)</code>.",
                    "<b>C</b>: rebuild the card with <code>.background(_:in:)</code>.",
                    "Hide a Text behind a colour; bring it back with <code>.zIndex</code>."],
                   "", 'Expected, as in our simulator runs: with the shape last it covers the text; .topLeading makes no visible difference because the VStack already fills the card; the background version measures the same 370 x 180 pt; zIndex(1) brings the hidden text forward, as long as it is the last modifier on that child.',
                   side=f'<div>{card("You hand in", ul("A screenshot per experiment", "One sentence: when you&rsquo;d choose ZStack over background"))}</div>'))

end_slide('2.5', 'ZStack: Layering, Backgrounds<br>&amp; SwiftUI Rendering', 'Lesson 2.6 &mdash; SwiftUI View Modifiers',
          'You can now explain what ZStack does on the depth axis, which child is in front and what zIndex changes, how a ZStack sizes itself, how its two-axis alignment works, when to use background or overlay instead, and how NPay&rsquo;s balance card is composed.',
          'Next, Lesson 2.6: SwiftUI view modifiers, how they really work: what .padding, .frame and .background return, why order matters, and the environment.')

write_deck(OUT25, '2.5', 'ZStack &amp; Layering', 'ZStack &amp; Layering')
