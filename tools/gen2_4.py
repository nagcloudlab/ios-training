"""Generates decks/unit-2/lesson-2.4/index.html from the Lesson 2.4 text (HStack, Horizontal Layout & Spacer).
The 11 sections are grouped into 7 Parts. Console output and screenshots come from tools/sim2_4 (a scripted
SwiftUI app run in the iOS Simulator); interface lines from the iOS 26.5 SDK."""
import html, os, re, sys
OUT24 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.4', 'HStack, Horizontal Layout<br>&amp; Spacer',
            'Three payment actions side by side. Who decides <b>how wide</b> each one is, and where the <b>spare space</b> goes?',
            'In 2.3 we learned how VStack arranges views vertically, how @ViewBuilder builds the content, and how SwiftUI negotiates sizes. Now NPay needs its first horizontal interface: payment actions side by side, well spaced, and adapting to different iPhone widths. We investigate HStack, Spacer, proposals, alignment and flexible space, all measured in the iOS Simulator.')
outcomes_slide('2.4', [("code", "<code>HStack</code> as VStack&rsquo;s <b>horizontal twin</b>"),
                       ("layout", "How an HStack <b>shares out width</b>"),
                       ("diff", "Why children don&rsquo;t get <b>equal</b> widths by default"),
                       ("frame", "What <code>Spacer</code> does, and how it differs from padding"),
                       ("eye", "<code>VerticalAlignment</code>: top, center, bottom"),
                       ("gear", "<code>.layoutPriority</code> when space runs out")])
where_slide('2.4', 'Today: a row of actions', (),
            '2.3: a <code>VStack</code>: icon, title, subtitle.',
            'An <code>HStack</code> row: Send, Request, History.',
            'Last lesson the welcome screen became a VStack with an icon, a title and a subtitle. Today we add NPay&rsquo;s first horizontal layout, a row of three quick actions, and learn how horizontal layout differs.',
            'The milestone first.')

# ================================================================== Part 1 (1)
divider(1, "The next milestone", "Quick actions in a row", 'Three labels side by side below the subtitle.', 'Before and after.')
S.append(slide("Part 1 &middot; Our next NPay milestone (section 1)", "Milestone 2.4: a quick-action row", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Add", ul("Three quick actions: <b>Send</b>, <b>Request</b>, <b>History</b>", "Side by side, below the subtitle"))}
        {card("Not yet", ul("Visual only, not buttons", "Button behaviour: <b>Lesson 2.7</b>"))}
      </div>
      {PHONE("img/before.png", "Before: Lesson 2.3", 190)}
      <div class="step">{PHONE("img/final.png", "After: Milestone 2.4", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'We have a welcome screen with an icon, a title and a subtitle. Now we want three quick-action labels in a row: Send, Request and History.'),
                  ('SAY', 'Click: that is where we finish today. For now they are visual elements, not buttons; buttons come in Lesson 2.7.'),
                  ('CONNECT', 'The tool for a row: HStack.'))))

# ================================================================== Part 2 (2-3)
divider(2, "HStack", "VStack, turned sideways", 'Same pattern as VStack, on the other axis.', 'Read the declaration.')
IFACE = """@frozen public struct HStack<Content> : View
        where Content : View {
    public init(alignment: VerticalAlignment = .center,
                spacing: CGFloat? = nil,
                @ViewBuilder content: () -> Content)
}"""
CMP = [("Main axis", "vertical", "horizontal"), ("Cross-axis alignment", "<code>HorizontalAlignment</code>", "<code>VerticalAlignment</code>"),
       ("Spacing", "between vertical children", "between horizontal children"), ("Content", "<code>@ViewBuilder</code> closure", "<code>@ViewBuilder</code> closure")]
S.append(slide("Part 2 &middot; What exactly is HStack? (section 2)", "A generic struct, like VStack", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Interface excerpt, iOS 26.5 SDK (body omitted)", IFACE, "font-size:13.5px")}
        <div class="gap"></div>
        <div class="step">{console("type(of:) in the simulator", ["HStack { Send; Request; History }:", "HStack&lt;TupleView&lt;(Text, Text, Text)&gt;&gt;"], 13)}</div></div>
      <div>{tbl(["", "VStack", "HStack"], CMP)}
        <div class="gap"></div>
        <div class="rule step" data-label="The closure?">{ul("Returns the <b>content</b>; the initializer builds the <code>HStack</code>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Like VStack, HStack is a generic SwiftUI struct conforming to View. Here is its real declaration from the SDK: the same shape as VStack&rsquo;s, except alignment is a VerticalAlignment.'),
                  ('SAY', 'The table: the main axis is horizontal instead of vertical; cross-axis alignment is VerticalAlignment instead of HorizontalAlignment; spacing goes between horizontal children; and the content is the same @ViewBuilder closure.'),
                  ('SAY', 'Click: we printed the type of our three-label row: HStack of a TupleView of three Texts. Exactly the pattern from 2.3.'),
                  ('SAY', 'Click: does the closure return the HStack? No. The closure produces the child content; the initializer constructs the stack.'),
                  ('CONNECT', 'First experiment: spacing.'))))

ROW = """HStack(spacing: 20) {
    Text("Send")
    Text("Request")
    Text("History")
}
.padding()"""
S.append(slide("Part 2 &middot; First experiment (section 3)", "Change the spacing: 0, 20, 40", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift (body)", ROW, "font-size:16px")}
        <div class="gap"></div>
        <div class="step">{console("Row width, measured", ["spacing 0: 156.7 pt", "spacing 20: 196.7 pt", "spacing 40: 236.7 pt"], 14)}</div></div>
      <div>{crop("img/spacing.png", "Grey border = each Text", 440)}
        <div class="rule step" data-label="What changes" style="margin-top:12px">{ul("+40 pt per step: <b>two gaps</b> × 20", "The labels and the outside: unchanged")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Replace the body with an HStack of three Texts, spacing 20, padded. Then try spacing 0 and 40. On the right, all three runs, with a grey border on each Text.'),
                  ('SAY', 'Click: the row measured 156.7 points at spacing 0, 196.7 at 20, and 236.7 at 40.'),
                  ('SAY', 'Click: each step adds 40 points: two gaps, 20 points more each. Only the distance between adjacent children changes; the labels stay the same size, and spacing adds nothing around the row.'),
                  ('CONNECT', 'So how does an HStack decide widths when space is limited?'))))

# ================================================================== Part 3 (4-5)
divider(3, "Sharing out width", "Proposals, not equal shares", 'A parent offers 350 points. Who gets what?', 'The negotiation.')
NEG = [("frame", "Parent proposes", "e.g. 350 pt wide"), ("diff", "Spacing first", "2 gaps × 20 = 40 pt"),
       ("link", "Children get proposals", "by sizing and flexibility"), ("code", "Children choose", "and report sizes"), ("layout", "HStack positions", "with alignment, spacing")]
P = []
for i, (ic, t, sub) in enumerate(NEG):
    x = i * 232
    P.append(tall(x, 0, 208, 120, ic, t, sub, str(i + 1)))
    if i < 4:
        P.append(wire(f'M{x + 210} 60H{x + 228}' + head(x + 228, 60, 'r')))
S.append(slide("Part 3 &middot; HStack&rsquo;s layout negotiation (section 4)", "How an HStack shares out width", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1136 120', 'The parent proposes a width, spacing is subtracted, children get proposals, children choose sizes, the stack positions them', 'neg', P, 'max-height:150px')}
    <div class="gap-lg"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("The arithmetic", ul("Spacing: 2 × 20 = <b>40 pt</b>", "Left for children: 350 &minus; 40 = <b>310 pt</b>"))}
      <div class="rule" data-label="But">{ul("Not 310 &divide; 3 = 103.3 pt each", "Each child has its <b>own sizing</b>")}</div>
    </div>
  </div>""", notes(('SAY', 'Layout uses size proposals. For a horizontal stack, the container decides how to distribute width. Click: the parent proposes a size, say 350 points wide. Click: the stack accounts for spacing: two gaps of 20 take 40 points. Click: the children receive proposals, depending on each child&rsquo;s sizing behaviour and flexibility. Click: they choose sizes and report them. Click: the stack positions them with alignment and spacing.'),
                  ('SAY', 'Click: the numbers. 350 minus 40 leaves 310 points for the children. But that does not mean each child gets 103.3 points. Each child has its own sizing behaviour. A simplified model; real stacks also weigh ideal sizes and priorities.'),
                  ('CONNECT', 'We measured both cases.'))))

FLEX = """HStack(spacing: 20) {
    Text("Send")
        .frame(maxWidth: .infinity)
    Text("Request")
        .frame(maxWidth: .infinity)
    Text("History")
        .frame(maxWidth: .infinity)
}
.frame(width: 350)"""
S.append(slide("Part 3 &middot; Equal widths? (sections 4&ndash;5)", "Plain Text vs equal flexible widths, in 350 pt", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Equal flexible widths", FLEX, "font-size:13.5px")}
        <div class="gap"></div>
        <div class="rule step" data-label="Design rule">{ul("Plain Text does <b>not</b> share equally", "Equal widths: ask for them, with a flexible frame")}</div></div>
      <div>{crop("img/widths.png", "Blue = the 350 pt stack; grey = each child", 460)}
        <div class="cols step" style="{TWO};gap:12px;margin-top:12px">
          {console("plain Text", ["Send: 39.3 pt", "Request: 62.7 pt", "History: 54.7 pt"], 13)}
          {console("maxWidth: .infinity", ["Send: 103.3 pt", "Request: 103.3 pt", "History: 103.3 pt"], 13)}
        </div></div>
    </div>
  </div>""", notes(('SAY', 'Both rows sit in a stack 350 points wide with spacing 20, so 310 points are left for children. The top row has plain Texts; the bottom row gives every Text a flexible frame with infinite max width. This replaces the text&rsquo;s browser explorer, which deliberately gave equal flexible widths.'),
                  ('SAY', 'Click: measured. Plain Texts take what they need: 39.3, 62.7 and 54.7 points, and the stack centres them in the leftover space. With flexible frames, each child gets exactly 103.3 points: 310 divided by 3.'),
                  ('SAY', 'Click: a plain HStack of Texts does not distribute space equally. When a reusable layout needs equal columns, ask for flexibility explicitly.'),
                  ('CONNECT', 'Flexible space has its own view: Spacer.'))))

# ================================================================== Part 4 (6-7)
divider(4, "Spacer", "Flexible space", 'NPay on the left, an account icon on the right.', 'Add a Spacer.')
SP = """HStack {
    Text("NPay")

    Spacer()

    Image(systemName: "person.circle")
}"""
S.append(slide("Part 4 &middot; What is Spacer? (sections 6&ndash;7)", "Spacer takes the leftover space", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Header.swift", SP, "font-size:16px")}
        <div class="gap"></div>
        {card("Spacer", ul("A <b>flexible</b> view along the stack&rsquo;s main axis", "No visible content of its own"))}
        <div class="gap"></div>
        <div class="step">{console("type(of:)", ["HStack&lt;TupleView&lt;(Text, Spacer, Image)&gt;&gt;"], 13)}</div></div>
      <div>{crop("img/spacer.png", "Blue = the HStack (.title2, padded screen)", 460)}
        <div class="step" style="margin-top:12px">{console("Row width, measured", ["without Spacer: 84.3 pt", "with Spacer: 370.0 pt (+285.7)"], 14)}</div></div>
    </div>
  </div>""", notes(('SAY', 'The NPay title on the left and an account icon on the right: put a Spacer between them. Spacer is a SwiftUI view that expands along the stack&rsquo;s main axis when space is available. It draws nothing itself; the stack can give it the remaining space, subject to layout constraints.'),
                  ('SAY', 'On the right, the text&rsquo;s checkbox experiment for real: the top row has no Spacer, the bottom row has one. The blue border is the HStack. Click: without the Spacer, the row is just its content, 84.3 points. With it, 370 points: the Spacer absorbed 285.7 points and pushed the icon to the far edge.'),
                  ('SAY', 'Click: and the Spacer is a real child in the content type: a TupleView of Text, Spacer and Image.'),
                  ('CONNECT', 'Is a Spacer just padding?'))))

S.append(slide("Part 4 &middot; Spacer vs padding (section 6)", "<code>Spacer()</code> is not <code>.padding(20)</code>", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px">
      {card(".padding(20)", ul("A <b>fixed</b> amount", "<b>Around</b> one view", "Same on every screen"))}
      {card("Spacer()", ul("<b>Flexible</b>: grows into leftover space", "<b>Between</b> siblings in a stack", "Wider screen, wider Spacer"))}
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Measured">{ul("Spacer took <b>285.7 pt</b> here; on another iPhone width, a different amount")}</div>
  </div>""", notes(('SAY', 'Is Spacer() the same as .padding(20)? No. Padding adds a specified amount of space around a view, the same on every screen. A Spacer is flexible: it sits between siblings in a stack and expands to consume the available space.'),
                  ('SAY', 'Click: in our run the Spacer took 285.7 points; on a narrower or wider iPhone it would take a different amount, which is exactly why NPay&rsquo;s header adapts to the device.'),
                  ('CONNECT', 'Next: children of different heights.'))))

# ================================================================== Part 5 (8)
divider(5, "Vertical alignment", "Top, center, bottom", 'Two texts with very different heights in one row.', 'Align them.')
AL = """HStack(alignment: .top, spacing: 20) {
    Text("Send")
        .font(.largeTitle)

    Text("Request")
        .font(.caption)
}"""
S.append(slide("Part 5 &middot; Why HStack uses VerticalAlignment (section 8)", "Different heights, three alignments", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 300px;gap:24px;align-items:start">
      {code("ContentView.swift", AL, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Each aligns", ul("<code>.top</code>: top edges", "<code>.center</code>: vertical centres", "<code>.bottom</code>: bottom edges"))}
        <div class="rule step" data-label="Later">{ul("Text <b>baseline</b> alignment: a later experiment")}</div></div>
      {crop("img/align.png", "Grey = each Text; blue = the row", 300)}
    </div>
  </div>""", notes(('SAY', 'Send in largeTitle and Request in caption: very different heights. HStack&rsquo;s cross axis is vertical, so its alignment is a VerticalAlignment. .top lines up the top edges, .center the vertical centres, .bottom the bottom edges. On the right, all three in the simulator; the row is as tall as its tallest child.'),
                  ('SAY', 'When children differ in size, this choice changes how the row looks. Click: for text in different font sizes you often want the text baseline instead; SwiftUI supports that, and we come back to it in a later layout experiment.'),
                  ('CONNECT', 'What if the row does not fit at all?'))))

# ================================================================== Part 6 (9)
divider(6, "When space runs out", "Compression and priority", 'A smaller iPhone, or longer labels.', 'Squeeze a row.')
NR = """HStack {
    Text("Available Balance")
        .layoutPriority(1)

    Text("₹25,000")
}"""
S.append(slide("Part 6 &middot; Too narrow: layoutPriority (section 9)", "Who gets the space when there isn&rsquo;t enough", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("BalanceRow.swift", NR, "font-size:15px")}
        <div class="cols step" style="{TWO};gap:12px;margin-top:12px">
          {console("no priority", ["label: 82.3 pt, 2 lines", "amount: 75.3 pt, 1 line"], 13)}
          {console("label priority 1", ["label: 152.0 pt, 1 line", "amount: 39.3 pt, 2 lines"], 13)}
        </div>
        <div class="rule step" data-label="Not &ldquo;bigger&rdquo;" style="margin-top:12px">{ul("Priority decides who is <b>served first</b> when space is short", "Here it squeezed the <b>amount</b>")}</div></div>
      <div>{crop("img/narrow.png", "Both rows squeezed into 200 pt (.title3)", 420)}</div>
    </div>
  </div>""", notes(('SAY', 'On a smaller iPhone, a row may not fit. SwiftUI has to resolve the layout within the width it has: text may compress, wrap or truncate, depending on the views and their modifiers. We squeezed the text&rsquo;s balance row into 200 points, at title3 so it clearly does not fit.'),
                  ('SAY', 'Top row, no priority: the label wrapped onto two lines and the amount kept one line. Bottom row, the label has layoutPriority(1): it is served first and keeps one line, 152 points, and the amount is left with 39 points and wraps: "₹25," above "000".'),
                  ('SAY', 'Click: so layoutPriority is not an instruction to make a view larger. It decides who gets space first when space is short, and here it produced a worse result for the balance. Use it deliberately, and check the result.'),
                  ('CONNECT', 'Now build NPay&rsquo;s row.'))))

# ================================================================== Part 7 (10)
divider(7, "NPay quick actions", "Milestone 2.4", 'Keep the welcome screen; add a row of three actions.', 'The code.')
ACT = """HStack(spacing: 24) {
    VStack(spacing: 8) {
        Image(systemName: "arrow.up.right")
        Text("Send")
    }
    VStack(spacing: 8) {
        Image(systemName: "arrow.down.left")
        Text("Request")
    }
    VStack(spacing: 8) {
        Image(systemName: "clock")
        Text("History")
    }
}
.font(.subheadline)
.foregroundStyle(.blue)"""
S.append(slide("Part 7 &middot; The quick-action row (section 10)", "An HStack of three small VStacks", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);gap:28px;align-items:start">
      <div>{code("Added below the subtitle, in VStack(spacing: 24)", ACT, "font-size:13px")}</div>
      <div class="cols" style="grid-template-columns:150px minmax(0,1fr);gap:16px;align-items:start">
        {PHONE("img/final.png", "Milestone 2.4", 150)}
        <div class="step">{card("Structure", ul("<b>HStack</b>: the row", "<b>VStack</b> per action: icon over label", "Outer <b>VStack</b>: the screen"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The welcome screen stays: symbol, title, subtitle, now in a VStack with spacing 24 and the title as largeTitle.bold(). Below the subtitle we add this HStack. Each action is a small VStack with an SF Symbol over a label: arrow up-right for Send, arrow down-left for Request, a clock for History. On the left, just the new part; the full code is in the lesson text and the lab.'),
                  ('SAY', 'Click: three levels. The HStack arranges the actions horizontally; each nested VStack puts an icon over a label; the outer VStack arranges the whole screen vertically. The real screen: Milestone 2.4.'),
                  ('CONNECT', 'One thing is new: .font and .foregroundStyle on the HStack reached every child. How?'))))

S.append(slide("Part 7 &middot; Why .font(.subheadline) reaches the children (section 10)", "Modifiers on a container flow down", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{console("type(of:) in the simulator", ["row.font(.subheadline):", "ModifiedContent&lt;HStack&lt;&hellip;&gt;,", "  _EnvironmentKeyWritingModifier&lt;Optional&lt;Font&gt;&gt;&gt;"], 14)}
        <div class="gap"></div>
        {card("Same as on an Image (2.2)", ul("<code>.font</code> on a non-Text view <b>writes the environment</b>"))}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("The environment", ul("Font is an <b>environment</b>-driven style", "Every descendant reads it", "unless it sets its own"))}</div>
        <div class="rule step" data-label="Later">{ul("The modifiers lesson goes deep on this")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Why does .font(.subheadline) on the HStack change the labels inside it, and size the symbols too? We printed the type: the HStack wrapped in an environment-writing modifier for an optional Font, the same thing we saw on an Image in 2.2.'),
                  ('SAY', 'Click: font is an environment-driven style. A font modifier on a container puts the font into the environment, and every descendant that does not set its own font reads it. The same happens with foregroundStyle, which is why all three actions are blue.'),
                  ('SAY', 'Click: this is an important concept; the modifiers lesson explores it properly.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.4', (), [("code", "HStack = sideways VStack", "VerticalAlignment, horizontal spacing"),
                     ("layout", "Width is negotiated", "children size themselves; not equal shares"),
                     ("frame", "Spacer and priority", "flexible space; who is served first")],
         'Three things to remember. HStack is VStack&rsquo;s horizontal twin: a generic struct, a @ViewBuilder closure, spacing between horizontal children and a VerticalAlignment. Width is negotiated: after spacing, children size themselves, so plain Texts do not get equal shares unless you ask for flexibility. And Spacer is flexible space that takes what is left, while layoutPriority decides who is served first when space runs out.')

review_divider(7)
review([("code", "Choose one", "What is HStack?",
         "What is <code>HStack</code>?<br>A. A Swift function<br>B. A generic struct conforming to <code>View</code><br>C. A UIKit controller", "B",
         "<code>@frozen public struct HStack&lt;Content&gt; : View</code>, built like VStack.",
         "Reading the call as a function call.", "Some pick A.", None),
        ("diff", "Question", "Does HStack give every child an equal width by default?",
         "Does <code>HStack</code> give every child an equal width by default?", "No",
         "In 350 pt, plain Texts took 39.3, 62.7 and 54.7 pt; only flexible frames gave 103.3 pt each.",
         "Imagining equal columns.", "Some say yes.", None),
        ("frame", "Choose one", "What does Spacer do?",
         "What does <code>Spacer()</code> do?<br>A. Adds a fixed 20-point gap<br>B. Expands flexibly when space is available", "B",
         "It took 285.7 pt in our header row; a different width on another iPhone.",
         "Treating it as fixed padding.", "Some pick A.", None),
        ("eye", "Choose one", "Which alignment type does HStack use?",
         "Which alignment type does <code>HStack</code> use?<br>A. <code>HorizontalAlignment</code><br>B. <code>VerticalAlignment</code>", "B",
         "Its main axis is horizontal, so its cross axis is vertical.",
         "Matching the name &ldquo;H&rdquo; to horizontal alignment.", "Some pick A.", None),
        ("gear", "Question", "Does layoutPriority guarantee a fixed width?",
         "Does <code>.layoutPriority(1)</code> guarantee a view a fixed width?", "No",
         "It only decides who is served first when space is short; the label kept one line, the amount wrapped.",
         "Treating priority as a size.", "Some say yes.", None),
        ("layout", "Predict the result", "Spacing 0 to 40 in a three-Text row: how much wider?",
         "A row of three Texts goes from <code>spacing: 0</code> to <code>spacing: 40</code>. How much wider is it?<br>A. 40 pt<br>B. 80 pt<br>C. 120 pt", "B",
         "Two gaps &times; 40 pt: measured 156.7 &rarr; 236.7 pt.",
         "Counting a gap per child, or around the row.", "Some pick C.", None),
        ("layers", "Question", "From 2.3: does VStack spacing add space around the stack?",
         "From Lesson 2.3: does a <code>VStack</code>&rsquo;s <code>spacing</code> add space around the whole stack?", "No",
         "Only between adjacent children; padding is separate. The same holds for HStack.",
         "Confusing spacing with padding.", "Some say yes.", "Spaced review from Lesson 2.3.")])

S.append(next_slide('2.4', [("2.5", "ZStack &amp; layered layouts", "NPay&rsquo;s balance card: Z-order, overlays, backgrounds"),
                            ("2.7", "Buttons", "making Send, Request and History tappable")],
                    'Next lesson builds NPay&rsquo;s first balance card with a ZStack: text and icons over a coloured background, Z-axis ordering, overlays and backgrounds. And in 2.7 today&rsquo;s labels become real buttons.'))

S.append(lab_slide('2.4', "Measure the row", "Predict each result, then check it with borders.",
                   ["Section 3: spacing 0, 20, 40.",
                    "Equal widths: add <code>.frame(maxWidth: .infinity)</code>.",
                    "Header with and without <code>Spacer()</code>.",
                    "Alignment: <code>.top</code>, <code>.center</code>, <code>.bottom</code>.",
                    "Squeeze the balance row; try <code>.layoutPriority(1)</code>.",
                    "Build the Section 10 quick-action row."],
                   "", 'Expected, as in our simulator runs: each spacing step of 20 adds 40 pt (two gaps); plain Texts keep their own widths, flexible frames share equally; the Spacer pushes the icon to the edge; the row is as tall as its tallest child; in a narrow row priority keeps the label on one line and the amount wraps; the quick actions inherit .subheadline and blue from the HStack.',
                   side=f'<div>{card("You hand in", ul("Screenshots with borders", "One measured width you predicted", "One sentence on what layoutPriority did"))}</div>'))

end_slide('2.4', 'HStack, Horizontal Layout<br>&amp; Spacer', 'Lesson 2.5 &mdash; ZStack &amp; Layered Layouts',
          'You can now explain HStack as VStack&rsquo;s horizontal twin, how an HStack shares out width, why plain children do not get equal widths, what Spacer does and how it differs from padding, how vertical alignment works, and what layoutPriority does when space runs out. NPay has its quick-action row.',
          'Next, Lesson 2.5: ZStack and layered layouts. NPay&rsquo;s first balance card: text and icons over a coloured background, Z-axis ordering, layout sizing, overlays and backgrounds.')

write_deck(OUT24, '2.4', 'HStack &amp; Spacer', 'HStack &amp; Spacer')
