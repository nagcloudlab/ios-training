"""Generates decks/unit-2/lesson-2.3/index.html from the Lesson 2.3 text (VStack & @ViewBuilder Internals).
The 20 sections are grouped into 8 Parts. Console output and screenshots come from tools/sim2_3 (a scripted
SwiftUI app run in the iOS Simulator); interface lines from the iOS 26.5 SDK; the result-builder example was run with swiftc."""
import html, os, re, sys
OUT23 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.3', 'VStack &amp;<br>@ViewBuilder Internals',
            'Two views, one column. How does <b>one closure</b> hand SwiftUI <b>two views</b>, and who decides where they go?',
            'In 2.1 we built Text("NPay"); in 2.2 we added Image(systemName: "creditcard.fill"). Now we have two independent views. Today: how to arrange them vertically, how to control the space between them, and what SwiftUI does inside: VStack&rsquo;s initializer, its generic type, the trailing closure, @ViewBuilder, and layout negotiation. Every screenshot, measurement and printed type came from the iOS Simulator.')
outcomes_slide('2.3', [("code", "Why <code>VStack</code> is a <b>generic struct</b>, not a function"),
                       ("link", "How the <b>trailing closure</b> supplies content"),
                       ("layers", "How <code>@ViewBuilder</code> turns many views into <b>one</b>"),
                       ("eye", "How the compiler infers <code>VStack&lt;Content&gt;</code>"),
                       ("layout", "Spacing, padding and alignment: <b>who does what</b>"),
                       ("frame", "How a stack <b>sizes itself</b>, and resizes")])
where_slide('2.3', 'Today: arrange the views', (),
            '2.2: <code>Image(systemName:)</code> above the title, in a <code>VStack</code> we didn&rsquo;t explain.',
            'Open up <code>VStack</code>: Swift first, then layout.',
            'Last lesson we put the symbol above the title with a VStack and promised to explain it. Today we keep that promise, first from the Swift language side, then from SwiftUI&rsquo;s layout side.',
            'Start with the problem.')

# ================================================================== Part 1 (1)
divider(1, "A vertical layout", "Two views, one column", 'Two independent views. We need them in a column.', 'The problem.')
FIRST = """VStack(spacing: 20) {
    Image(systemName: "creditcard.fill")
    Text("NPay")
}"""
S.append(slide("Part 1 &middot; The problem (section 1)", "NPay needs a vertical layout", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px;gap:36px;align-items:center">
      <div>{code("ContentView.swift", FIRST, "font-size:17px")}
        <div class="gap"></div>
        <div class="step">{card("Three questions", ul("Is <code>VStack</code> a <b>function</b>?", "Is the content a <b>closure</b>?", "How does a closure return <b>two</b> views?"))}</div></div>
      {PHONE("img/before.png", "Where 2.2 ended", 190)}
    </div>
  </div>""", notes(('SAY', 'We have two views, the symbol and the title, and we need a container that arranges its children vertically. SwiftUI provides VStack. On the right, the screen from the end of Lesson 2.2.'),
                  ('SAY', 'Click: but what exactly is this expression? Is VStack a function? Is the part in braces a closure? And if it is, how does one closure return two views? Those three questions are today&rsquo;s first half.'),
                  ('CONNECT', 'First question: function or not?'))))

# ================================================================== Part 2 (2)
divider(2, "A generic struct", "Not a function", 'VStack(spacing: 20) { } looks like a function call.', 'Read the declaration.')
IFACE = """@frozen public struct VStack<Content> : View
        where Content : View {
    public init(alignment: HorizontalAlignment = .center,
                spacing: CGFloat? = nil,
                @ViewBuilder content: () -> Content)
}"""
FOUR = [("<code>struct VStack</code>", "a <b>struct</b>"), ("<code>&lt;Content&gt;</code>", "a <b>generic</b> type parameter"),
        ("<code>spacing:</code>", "an initializer <b>argument</b>"), ("<code>@ViewBuilder content:</code>", "a <b>closure</b>, built by a result builder")]
S.append(slide("Part 2 &middot; VStack is not a function (section 2)", "<code>VStack(&hellip;)</code> calls an initializer", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:28px;align-items:start">
      <div>{code("Interface excerpt, iOS 26.5 SDK (body omitted)", IFACE, "font-size:14px")}
        <div class="gap"></div>
        <div class="step">{tbl(["In the declaration", "Means"], FOUR, 'tbl')}</div></div>
      <div class="step">{code("Unit 01", 'struct Account {\n    let balance: Int\n}\n\nlet account = Account(balance: 25000)', "font-size:14px")}
        <div class="gap"></div>
        {card("Same move", ul("<code>Account(balance:)</code> calls an initializer", "<code>VStack(spacing:)</code> calls a <b>generic</b> struct&rsquo;s initializer"))}</div>
    </div>
  </div>""", notes(('SAY', 'It looks like a function call, but VStack is a generic struct and we are calling its initializer. This is the real declaration from the iOS 26.5 SDK, with the body left out; the lesson text shows a simplified version of the same thing.'),
                  ('SAY', 'Click: four things to read off it. VStack is a struct. Content is a generic type parameter, constrained to View. spacing is an initializer argument, optional with a default of nil. And content is a closure marked @ViewBuilder.'),
                  ('SAY', 'Click: you have done this since Unit 01. Account(balance: 25000) calls Account&rsquo;s initializer. VStack(spacing: 20) calls a generic struct&rsquo;s initializer. Same syntax, same mechanism.'),
                  ('CONNECT', 'So what about the braces after it?'))))

# ================================================================== Part 3 (3)
divider(3, "The trailing closure", "It supplies the content", 'The braces are the content argument.', 'Write it the long way.')
TR = """VStack(spacing: 20) {
    Text("NPay")
}"""
LONG = """VStack(
    spacing: 20,
    content: {
        Text("NPay")
    }
)"""
P = [box(0, 0, 300, 56, 'Content closure', 'returns Content', None, '', 'code'),
     wire('M304 28H346' + head(346, 28, 'r')),
     box(352, 0, 300, 56, 'VStack initializer', 'uses the Content', None, '', 'gear'),
     wire('M656 28H698' + head(698, 28, 'r')),
     box(704, 0, 300, 56, 'VStack&lt;Content&gt;', 'the value you get', None, 'lit', 'layers')]
S.append(slide("Part 3 &middot; The trailing closure (section 3)", "The closure supplies the content", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {code("Trailing closure", TR, "font-size:16px")}
      <div class="step">{code("Same call, written out", LONG, "font-size:16px")}</div>
    </div>
    <div class="gap"></div>
    <div class="step">{svg('0 0 1004 56', 'The content closure returns Content, the initializer uses it, the result is a VStack of Content', 'tc', P, 'max-height:70px')}</div>
    <div class="rule step" data-label="Not a VStack" style="margin-top:12px">{ul("The closure returns <b>Content</b>; the <b>initializer</b> returns the <code>VStack</code>")}</div>
  </div>""", notes(('SAY', 'Swift lets you write a closure argument after the parentheses when a function or initializer takes a closure: trailing closure syntax.'),
                  ('SAY', 'Click: so this is the same call written out: spacing 20, and a content argument whose value is a closure returning Text("NPay").'),
                  ('SAY', 'Click: the flow. The content closure returns a Content value; the VStack initializer uses it; the result is a value of type VStack of Content.'),
                  ('SAY', 'Click: a common confusion: the closure does not return a VStack. It returns the content. The initializer produces the VStack.'),
                  ('CONNECT', 'Now the real puzzle: two views in one closure.'))))

# ================================================================== Part 4 (4-6)
divider(4, "@ViewBuilder", "Many expressions, one value", 'A closure returns one value. This one has two expressions.', 'Compare.')
CALC = """let calculate = {
    10 + 20
}

print(calculate()) // 30"""
TWOV = """VStack {
    Text("NPay")
    Image(systemName: "creditcard.fill")
}"""
S.append(slide("Part 4 &middot; The mystery (section 4)", "How can one closure return two views?", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("A normal closure", CALC, "font-size:16px")}
        <div class="gap"></div>
        {console("swiftc, then run", ["30"], 15)}</div>
      <div>{code("A view closure", TWOV, "font-size:16px")}
        <div class="gap"></div>
        <div class="rule step" data-label="Two expressions">{ul("One closure, <b>two</b> results?", "The answer: <code>@ViewBuilder</code>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'A normal Swift closure returns one result. This one adds 10 and 20; we ran it, and it prints 30.'),
                  ('SAY', 'Click: the VStack closure has two expressions on two lines, a Text and an Image, and no return. How does one closure produce both? That is what @ViewBuilder is for.'),
                  ('CONNECT', 'What is @ViewBuilder?'))))

P = [box(0, 0, 330, 56, 'Source expressions', 'Image · Text · Button', None, '', 'code'),
     wire('M334 28H374' + head(374, 28, 'r')),
     box(380, 0, 330, 56, '@ViewBuilder', 'compile-time transformation', None, 'lit', 'gear'),
     wire('M714 28H754' + head(754, 28, 'r')),
     box(760, 0, 376, 56, 'One composite Content', 'then VStack&lt;Content&gt;', None, '', 'layers')]
BB = """// ViewBuilder (excerpt, iOS 26.5 SDK)
static func buildBlock<each Content>(
    _ content: repeat each Content
) -> TupleView<(repeat each Content)>
    where repeat each Content : View"""
S.append(slide("Part 4 &middot; What is @ViewBuilder? (section 5)", "A result builder: many views in, one value out", f"""  <div class="body">
    {svg('0 0 1136 56', 'Source expressions go through the ViewBuilder transformation into one composite Content value', 'vb', P, 'max-height:70px')}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("An array?", ul("No <code>[View]</code>", "A <b>strongly typed</b> composite value"))}</div>
        <div class="step">{card("When?", ul("At <b>compile time</b>: a language transformation", "Not a run-time loop or reflection"))}</div>
      </div>
      <div class="step">{code("Interface excerpt", BB, "font-size:13.5px")}
        <p class="small muted" style="margin:8px 0 0">Exact representation varies by SwiftUI version.</p></div>
    </div>
  </div>""", notes(('SAY', '@ViewBuilder is a Swift result builder used by SwiftUI. You write several view expressions in a block, and it combines them into a single composite view value; that value is the Content of the VStack.'),
                  ('SAY', 'Click: is it an array of views? No. It does not build [View]; it builds one strongly typed value. Click: and it happens at compile time: a language-supported transformation, not a run-time loop discovering child views by reflection.'),
                  ('SAY', 'Click: the SDK shows it. ViewBuilder&rsquo;s buildBlock takes a parameter pack, any number of views each with its own type, and returns a TupleView of exactly those types. That is the tuple-based content the text mentions. The exact representation can change between SwiftUI versions.'),
                  ('CONNECT', 'The mechanism is plain Swift. Let&rsquo;s build our own.'))))

SB = """@resultBuilder
struct StringBuilder {
    static func buildBlock(_ parts: String...) -> String {
        parts.joined(separator: " ")
    }
}

func makeMessage(@StringBuilder content: () -> String) -> String {
    content()
}

let message = makeMessage {
    "Welcome"
    "to"
    "NPay"
}
print(message)"""
S.append(slide("Part 4 &middot; Our own result builder (section 6)", "Build one: three strings, one message", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:28px;align-items:start">
      {code("StringBuilder.swift", SB, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("swiftc, then run", ["Welcome to NPay"], 16)}</div>
        <div class="step">{card("The same mechanism", ul("<code>buildBlock</code> gets <b>every</b> expression", "and returns <b>one</b> result", "<code>@ViewBuilder</code>: richer rules, for views"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Before going further into SwiftUI, the plain Swift feature. A struct marked @resultBuilder with a static buildBlock that joins strings with spaces. A function whose closure parameter is marked @StringBuilder. And a call with three string expressions on three lines.'),
                  ('SAY', 'Click: we compiled and ran it: "Welcome to NPay". The compiler passed all three expressions to buildBlock, which returned one String.'),
                  ('SAY', 'Click: @ViewBuilder is the same mechanism with a much richer set of rules for composing views; its buildBlock returns a TupleView instead of a String.'),
                  ('CONNECT', 'Which brings us to the type of the VStack itself.'))))

# ================================================================== Part 5 (7, 13)
divider(5, "The Content type", "Inferred, concrete, printed", 'What is the full type of a VStack?', 'Print it.')
TYPES = [("<code>VStack { Text }</code>", "<code>VStack&lt;Text&gt;</code>"),
         ("<code>VStack { Text; Image }</code>", "<code>VStack&lt;TupleView&lt;(Text, Image)&gt;&gt;</code>"),
         ("Section 13: two Texts", "<code>VStack&lt;TupleView&lt;(Text, Text)&gt;&gt;</code>"),
         ("Nested stacks (section 14)", "<code>VStack&lt;VStack&lt;Text&gt;&gt;</code>")]
S13 = """let stack = VStack(spacing: 20) {
    Text("NPay")
    Text("Payments made simple")
}
print(type(of: stack))"""
S.append(slide("Part 5 &middot; The generic Content type (sections 7, 13)", "The compiler infers <code>Content</code>", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.85fr) minmax(0,1.15fr);gap:28px;align-items:start">
      <div>{code("Experiment.swift", S13, "font-size:14px")}
        <div class="gap"></div>
        <div class="step">{card("Why it matters", ul("Static <b>checking</b> and efficient composition", "Also why SwiftUI errors can be <b>long</b>"))}</div></div>
      <div>{tbl(["Content", "type(of:) in the simulator"], TYPES, 'tbl')}
        <div class="gap"></div>
        <div class="rule step" data-label="So">{ul("Not a collection assembled at run time", "One <b>concrete generic</b> type, built by <code>@ViewBuilder</code>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'With one child, the compiler infers that the closure produces Text, so the stack is VStack of Text. With two children, the builder combines them, and the stack is still strongly typed. We printed the types in the simulator, as Section 13 suggests: one child gives VStack of Text; Text and Image give VStack of TupleView of Text and Image; Section 13&rsquo;s two Texts give a TupleView of Text and Text; and a stack in a stack is VStack of VStack of Text.'),
                  ('SAY', 'Click: SwiftUI uses this compile-time type information extensively, for static checking and efficient composition. It is also why a mistake inside a big SwiftUI expression can produce a long, confusing compiler message: the types are long.'),
                  ('SAY', 'Click: so a VStack is not a dynamically assembled collection of arbitrary objects. It is one concrete generic type whose content @ViewBuilder built. The printed names can vary between compiler and SwiftUI versions.'),
                  ('CONNECT', 'That was the Swift side. Now the layout side: how does a VStack arrange its children?'))))

# ================================================================== Part 6 (8-10, 18-19)
divider(6, "Spacing, padding, alignment", "How a VStack arranges children", 'From Swift internals to layout internals.', 'The process.')
STEPS = [("frame", "Receive a proposal", "from the parent"), ("code", "Measure the children", "the space they need"),
         ("diff", "Add spacing", "and layout priorities"), ("layout", "Choose its size", "its own size"), ("layers", "Position children", "top to bottom")]
P = []
for i, (ic, t, sub) in enumerate(STEPS):
    x = i * 232
    P.append(tall(x, 0, 208, 120, ic, t, sub, str(i + 1)))
    if i < 4:
        P.append(wire(f'M{x + 210} 60H{x + 228}' + head(x + 228, 60, 'r')))
BORD = """VStack(spacing: 20) {
    Image(systemName: "creditcard.fill")
        .font(.system(size: 64))
        .border(.red)
    Text("NPay")
        .font(.largeTitle)
        .border(.green)
    Text("Payments made simple")
        .border(.orange)
}
.border(.blue)
.padding()"""
S.append(slide("Part 6 &middot; How VStack arranges children (section 8)", "Five steps, no Y coordinates", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1136 120', 'Receive a proposal, measure the children, add spacing, choose its size, position the children', 'arr', P, 'max-height:150px')}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="spacing: 20">{ul("Space <b>between</b> adjacent children", "<b>Not</b> padding around the stack")}</div>
  </div>""", notes(('SAY', 'VStack is a layout container; its job is to arrange children along the vertical axis. A simplified process. Click: it receives a size proposal from its parent. Click: it works out the space its children need. Click: it accounts for spacing and layout priorities. Click: it chooses its own size. Click: it positions the children vertically. You never give a child a Y coordinate.'),
                  ('SAY', 'Click: spacing: 20 means 20 points between adjacent arranged children. It does not add 20 points around the whole stack. Spacing and padding solve different problems; the next slides show both.'),
                  ('CONNECT', 'See the rectangles with borders.'))))

S.append(slide("Part 6 &middot; Borders show the layout (sections 8, 18)", "Spacing 20, then 50", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 230px 230px;gap:24px;align-items:start">
      <div>{code("Borders.swift", BORD, "font-size:12.5px")}</div>
      <div>{crop("img/borders20.png", "spacing: 20", 230)}</div>
      <div class="step">{crop("img/borders50.png", "spacing: 50", 230)}</div>
    </div>
    <div class="cols step" style="{TWO};gap:24px;margin-top:12px">
      {console("Measured (stack + padding)", ["spacing 20: 207.7 × 207.3 pt", "spacing 50: 207.7 × 267.3 pt"], 13)}
      {card("Why +60", ul("Two gaps × 30 pt more", "The children didn&rsquo;t change"))}
    </div>
  </div>""", notes(('SAY', 'A debugging technique: give each view a border. Red around the symbol, green around the title, orange around the subtitle, blue around the stack, then padding. The borders show each view&rsquo;s layout rectangle at that point in the modifier chain; the blue border is around the stack, not the screen.'),
                  ('SAY', 'Click: the same code with spacing 50. The gaps grow; the children&rsquo;s own boxes do not change.'),
                  ('SAY', 'Click: measured: 207.3 points tall at spacing 20, 267.3 at spacing 50. Exactly 60 more: two gaps, 30 points each. Spacing separates children; it does not change their content.'),
                  ('CONNECT', 'Padding is a different tool. Where you put it matters.'))))

PA = """VStack(spacing: 20) {
    Text("NPay")
    Text("Payments made simple")
}
.padding(30)
.background(.yellow)"""
PB = """VStack(spacing: 20) {
    Text("NPay")
        .padding(30)
    Text("Payments made simple")
        .padding(30)
}
.background(.yellow)"""
S.append(slide("Part 6 &middot; spacing vs .padding() (sections 9, 19)", "Padding on the stack, or on each child", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px;gap:14px;align-items:start">{code("A: on the stack", PA, "font-size:13px")}
        {crop("img/padA.png", "A: 235.7 × 128.7 pt", 190)}</div>
      <div class="cols step" style="grid-template-columns:minmax(0,1fr) 190px;gap:14px;align-items:start">{code("B: on each child", PB, "font-size:13px")}
        {crop("img/padB.png", "B: 235.7 × 188.7 pt", 190)}</div>
    </div>
    <div class="rule step" data-label="The closure?" style="margin-top:10px">{ul("<code>.padding()</code> after <code>}</code> modifies the <b>VStack</b>, not the closure")}</div>
  </div>""", notes(('SAY', 'Version A: spacing 20 between the two texts, then padding 30 around the resulting stack, then a yellow background so we can see it. Measured 235.7 by 128.7 points.'),
                  ('SAY', 'Click: version B puts padding 30 on each child instead. Each child&rsquo;s own layout size grows, so the stack is 60 points taller: 188.7. Same width, because the widest child plus 60 is the same either way. Not equivalent: modifiers affect layout composition.'),
                  ('SAY', 'Click: and to answer the text&rsquo;s question: .padding written after the closing brace is not applied to the closure. The closure produces the content; the initializer produces the VStack; .padding is called on that VStack.'),
                  ('CONNECT', 'The other initializer argument: alignment.'))))

AL = """VStack(
    alignment: .leading,
    spacing: 20
) {
    Text("NPay")
    Text("Payments made simple")
}"""
S.append(slide("Part 6 &middot; Alignment (section 10)", "<code>.leading</code>, <code>.center</code>, <code>.trailing</code>", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr) 260px;gap:24px;align-items:start">
      {code("ContentView.swift", AL, "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Type inference again", ul("<code>alignment:</code> expects a <code>HorizontalAlignment</code>", "so <code>.leading</code> is <code>HorizontalAlignment.leading</code>"))}
        <div class="rule step" data-label="Why horizontal?">{ul("VStack stacks <b>vertically</b>; its cross axis is <b>horizontal</b>", "HStack: vertical alignment (2.4)")}</div></div>
      {crop("img/align.png", "Grey border = stack width", 260)}
    </div>
  </div>""", notes(('SAY', 'VStack also takes an alignment. .leading is a static member found through the expected type, HorizontalAlignment: contextual type inference once more.'),
                  ('SAY', 'Instead of the text&rsquo;s buttons, the simulator: three stacks with the text&rsquo;s three lines, aligned leading, center and trailing. The grey border is each stack&rsquo;s own width, set by its widest child, "Payments made simple"; the shorter lines move within it.'),
                  ('SAY', 'Click: why is it called HorizontalAlignment? Because a VStack arranges children vertically, so its cross-axis alignment is horizontal. HStack, next lesson, is the other way round.'),
                  ('CONNECT', 'Notice the stack was only as wide as its widest child. Does a stack ever fill the screen?'))))

# ================================================================== Part 7 (11, 14, 16-17)
divider(7, "How a stack sizes itself", "Proposals, children, changes", 'A stack is as big as its content, unless asked otherwise.', 'Hug or fill.')
S.append(slide("Part 7 &middot; Why VStack doesn&rsquo;t fill the screen (section 11)", "It hugs its children", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 170px 170px;gap:28px;align-items:start">
      <div>{code("Hug", 'VStack {\n    Text("NPay")\n}\n.border(.blue)', "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{code("Fill", 'VStack {\n    Text("NPay")\n}\n.frame(maxWidth: .infinity, maxHeight: .infinity)\n.border(.blue)', "font-size:13px")}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="Not CSS">{ul("Layout is <b>proposal-driven</b>", "Containers don&rsquo;t fill their parent by default")}</div></div>
      <div>{PHONE("img/hug.png", "39.7 × 24.3 pt", 170)}</div>
      <div class="step">{PHONE("img/fill.png", "402.0 × 778.0 pt", 170)}</div>
    </div>
  </div>""", notes(('SAY', 'A VStack with one Text and a blue border. The stack is only as big as its child: 39.7 by 24.3 points, the size of the word. Its ideal size comes from its children and the parent&rsquo;s proposal.'),
                  ('SAY', 'Click: add .frame with infinite max width and height, then the border. Now the framed view takes everything the parent offers: 402 by 778 points, the safe area of this iPhone. We study frames properly later.'),
                  ('SAY', 'Click: a common beginner mistake is to assume every container fills its parent, as a block does in CSS. SwiftUI layout is proposal-driven.'),
                  ('CONNECT', 'So how does a stack compute its height? With numbers.'))))

CALC2 = """VStack(spacing: 20) {
    Text("NPay")
        .font(.largeTitle)
    Text("Payments made simple")
        .font(.subheadline)
}"""
S.append(slide("Part 7 &middot; Layout negotiation (section 16)", "Stack height = children + spacing", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", CALC2, "font-size:15px")}
        <div class="gap"></div>
        <p style="font-size:24px;margin:0">H<sub>stack</sub> &asymp; H<sub>1</sub> + H<sub>2</sub> + S</p>
        <p class="small muted" style="margin:6px 0 0">The text&rsquo;s illustration: 41 + 20 + 20 = 81 pt.</p></div>
      <div>{crop("img/calc.png", SIM, 300)}
        <div class="step" style="margin-top:12px">{console("Measured", ["title: 77.3 × 48.7 pt", "subtitle: 158.0 × 21.0 pt", "stack: 158.0 × 89.7 pt", "48.7 + 21.0 + 20 = 89.7"], 14)}</div>
        <div class="takeaway step" style="margin-top:10px">Positions come from <b>sizes + spacing + alignment</b>.</div></div>
    </div>
  </div>""", notes(('SAY', 'How does SwiftUI decide this stack&rsquo;s height? A simplified model: the stack&rsquo;s height is about the first child&rsquo;s height, plus the second&rsquo;s, plus the spacing. The text illustrates it with 41, 20 and 20, giving 81 points.'),
                  ('SAY', 'Click: we measured the real thing. The title chose 48.7 points, the subtitle 21.0, the spacing is 20, and the stack is 89.7 points: exactly the sum. The stack&rsquo;s width, 158, is its widest child. Real layout also considers proposals, flexibility and priorities, which did not come into play here.'),
                  ('SAY', 'Click: that is why you never give a child a Y coordinate. The container computes positions from child sizes, spacing and alignment.'),
                  ('CONNECT', 'And if a child changes size while the app runs?'))))

DT = [("eye", "Text size preference changes", "Settings: larger text"), ("gear", "Environment changes", "the new size reaches the views"),
      ("code", "Text measures again", "taller lines"), ("layout", "VStack lays out again", "sizes + spacing"), ("check", "Children move", "new positions")]
P = [box(0, i * 54, 520, 46, t, sub, str(i + 1) if i < 4 else '5+', '', ic) for i, (ic, t, sub) in enumerate(DT)]
S.append(slide("Part 7 &middot; When a child changes size (section 17)", "Dynamic Type: measured again, placed again", f"""  <div class="body">
    {cues(5)}
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:28px;align-items:start">
      {svg('0 0 520 262', 'Text size changes, environment changes, text measures again, VStack lays out again, children move', 'dt', P, 'max-height:300px')}
      <div class="step">{crop("img/calc-ax.png", "Accessibility XL text size", 380)}
        <div style="margin-top:12px">{console("Measured again", ["title: 74.0 pt, subtitle: 49.7 pt", "stack: 74.0 + 49.7 + 20 = 143.7 pt"], 14)}</div></div>
    </div>
    <div class="rule step" data-label="No rebuild" style="margin-top:10px">{ul("Same running app: only <b>layout</b> runs again")}</div>
  </div>""", notes(('SAY', 'NPay supports Dynamic Type because it uses semantic fonts. Click: the user raises the text size. Click: that environment information reaches the views. Click: the text needs different dimensions. Click: the VStack lays out again with the new child sizes and the same spacing. Click: the children get new positions.'),
                  ('SAY', 'We set the simulator to Accessibility Extra Large: the title became 74 points tall, the subtitle 49.7, the spacing stayed 20, and the stack became 143.7, again exactly the sum.'),
                  ('SAY', 'Click: none of this needs a new process or a rebuild. It happens inside the running SwiftUI interface.'),
                  ('CONNECT', 'One more question people ask about stacks: are nested stacks expensive?'))))

S.append(slide("Part 7 &middot; Nested stacks (section 14)", "Is nesting stacks bad?", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Nested.swift", 'VStack {\n    VStack {\n        Text("NPay")\n    }\n}', "font-size:17px")}
        <div class="gap"></div>
        {console("type(of:)", ["VStack&lt;VStack&lt;Text&gt;&gt;"], 15)}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Not by itself", ul("SwiftUI is built for <b>composition</b>", "Cost depends on hierarchy, layout, dependencies, rendering"))}
        <div class="rule step" data-label="So">{ul("Don&rsquo;t optimise by counting <code>VStack</code>s", "<b>Profile</b> real bottlenecks")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A stack inside a stack: its type is simply VStack of VStack of Text. Is nesting always bad? No. SwiftUI is designed for compositional layouts, and the real cost depends on the view hierarchy, layout complexity, dependencies and rendering.'),
                  ('SAY', 'Click: avoid premature optimisation based only on how many VStacks you wrote. For complex layouts, profile and investigate actual bottlenecks; Instruments comes later in the course.'),
                  ('CONNECT', 'Back to NPay.'))))

# ================================================================== Part 8 (12, 20)
divider(8, "NPay welcome screen", "Milestone 2.3", 'Keep the symbol and title; add a subtitle; configure the stack.', 'The code.')
FINAL = """struct ContentView: View {
    var body: some View {
        VStack(alignment: .center, spacing: 20) {
            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)
            Text("NPay")
                .font(.largeTitle)
                .bold()
                .foregroundStyle(.blue)
            Text("Payments made simple")
                .font(.subheadline)
                .foregroundStyle(.secondary)
        }
        .padding()
    }
}"""
S.append(slide("Part 8 &middot; Final NPay code (sections 12, 20)", "Milestone 2.3: a structured welcome screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:28px;align-items:start">
      <div>{code("ContentView.swift", FINAL, "font-size:13px")}</div>
      <div>{PHONE("img/final.png", "Milestone 2.3", 130)}
        <div class="step" style="margin-top:8px">{card("What changed", ul("Explicit <b>alignment</b>, <b>spacing</b>", "A <b>subtitle</b>", "<b>Padding</b> on the stack"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'The NPay code after the experiments. We kept the symbol and the title from 2.2, configured the VStack&rsquo;s alignment and spacing explicitly, added a subtitle in the subheadline font with a secondary style, and padded the whole stack. On the right, the real screen. #Preview and import SwiftUI are unchanged and left off the slide.'),
                  ('SAY', 'Click: those are the four changes. And this body&rsquo;s printed type is now ModifiedContent of a VStack of a TupleView of the symbol and two Texts, with a padding layout around it: every part of it is something you can now explain.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.3', (), [("code", "VStack is a generic struct", "the closure supplies Content"),
                     ("layers", "@ViewBuilder builds one value", "a typed TupleView, at compile time"),
                     ("layout", "Layout from sizes", "children + spacing; padding is separate")],
         'Three things to remember. VStack is a generic struct: VStack(spacing:) calls its initializer, and the trailing closure supplies the Content. @ViewBuilder is a result builder that turns several view expressions into one strongly typed value at compile time, such as a TupleView. And the stack lays itself out from its children&rsquo;s sizes plus spacing; padding, alignment and frames are separate decisions.')

review_divider(10)
review([("code", "Choose one", "What is VStack?",
         "What is <code>VStack</code>?<br>A. A Swift function<br>B. A generic struct conforming to <code>View</code><br>C. A UIKit class", "B",
         "<code>@frozen public struct VStack&lt;Content&gt; : View</code>: <code>VStack(&hellip;)</code> calls its initializer.",
         "Reading the call syntax as a function call.", "Some pick A.", None),
        ("link", "Choose one", "What does the trailing closure supply?",
         "What does the trailing closure supply?<br>A. The <code>VStack</code> itself<br>B. The child <code>Content</code> value<br>C. The app&rsquo;s main function", "B",
         "The closure returns Content; the initializer produces the <code>VStack&lt;Content&gt;</code>.",
         "Thinking the closure returns the stack.", "Some pick A.", None),
        ("layers", "Choose one", "What is @ViewBuilder?",
         "What is <code>@ViewBuilder</code>?<br>A. A run-time reflection API<br>B. A Swift result builder<br>C. A memory allocator", "B",
         "A compile-time transformation, like our <code>StringBuilder</code>, with view-composition rules.",
         "Thinking SwiftUI discovers children at run time.", "Some pick A.", None),
        ("diff", "Question", "Does @ViewBuilder just return an array of View values?",
         "Does <code>@ViewBuilder</code> simply return an array of <code>View</code> values?", "No",
         "It returns one typed value: Text and Image printed as <code>TupleView&lt;(Text, Image)&gt;</code>.",
         "Picturing <code>[View]</code>.", "Some say yes.", None),
        ("layout", "Choose one", "What does VStack spacing control?",
         "What does <code>VStack</code>&rsquo;s <code>spacing</code> control?<br>A. Distance between arranged children<br>B. Padding around the entire stack<br>C. Font size", "A",
         "Spacing 20 &rarr; 50 added exactly 60 pt: two gaps, nothing around the stack.",
         "Confusing spacing with padding.", "Some pick B.", None),
        ("eye", "Choose one", "What does VStack(alignment: .leading) configure?",
         "What does <code>VStack(alignment: .leading)</code> configure?<br>A. Vertical alignment<br>B. Horizontal alignment of the children<br>C. Text colour", "B",
         "A VStack&rsquo;s cross axis is horizontal: <code>HorizontalAlignment</code>.",
         "Thinking &ldquo;VStack&rdquo; means vertical alignment.", "Some pick A.", None),
        ("gear", "Question", "Does .padding() after the closure modify the closure?",
         "Does <code>.padding()</code> written after the closing brace modify the closure?", "No",
         "It is called on the <code>VStack</code> value the initializer returned.",
         "Reading the modifier as part of the content.", "Some say yes.", None),
        ("frame", "Question", "Does VStack always fill its parent's height?",
         "Does a <code>VStack</code> always fill its parent&rsquo;s entire height?", "No",
         "<code>VStack { Text(\"NPay\") }</code> measured 39.7 &times; 24.3 pt; only a frame made it fill.",
         "Assuming CSS block behaviour.", "Some say yes.", None),
        ("layout", "Predict the result", "Title 48.7 pt, subtitle 21.0 pt, spacing 20: stack height?",
         "A title measures 48.7 pt tall and a subtitle 21.0 pt, in <code>VStack(spacing: 20)</code>. How tall is the stack?<br>A. 69.7 pt<br>B. 89.7 pt<br>C. 109.7 pt", "B",
         "48.7 + 21.0 + one gap of 20 = 89.7 pt, as measured.",
         "Counting spacing above and below as well.", "Some pick C.", None),
        ("phone", "Question", "From 2.2: does .font on an Image return an Image?",
         "From Lesson 2.2: does <code>Image(systemName: &hellip;).font(.system(size: 64))</code> still have the type <code>Image</code>?", "No",
         "It printed <code>ModifiedContent&lt;Image, _EnvironmentKeyWritingModifier&lt;&hellip;&gt;&gt;</code>; only Text keeps its type.",
         "Expecting Image to behave like Text.", "Some say yes.", "Spaced review from Lesson 2.2.")])

S.append(next_slide('2.3', [("2.4", "HStack &amp; horizontal layout", "a row of quick actions: alignment, flexible space, priorities, <code>Spacer</code>")],
                    'Next lesson turns the stack on its side: a row of NPay quick actions in an HStack, and how horizontal layout differs: vertical alignment, flexible space, layout priorities and Spacer.'))

S.append(lab_slide('2.3', "Make the layout visible", "Use borders and measurements to check each claim. Predict first.",
                   ["Section 18 borders; spacing 20 &rarr; 50.",
                    "Section 19 versions A and B.",
                    "Each <code>alignment</code>: leading, center, trailing.",
                    "A filling <code>.frame</code> with a border.",
                    "<code>type(of:)</code>: one child, two children.",
                    "Larger text size; then restore Section 20."],
                   "", 'Expected, as in our simulator runs: spacing 50 adds 60 pt to the stack (two gaps); B is 60 pt taller than A; alignment moves the shorter lines inside a stack as wide as its widest child; the frame makes the border fill the safe area; types VStack<Text> and VStack<TupleView<(Text, Image)>>; at a larger text size the stack height is still the children plus spacing.'.replace('<', '&lt;').replace('>', '&gt;'),
                   side=f'<div>{card("You hand in", ul("Screenshots with borders, before and after", "Your two printed types, each explained", "One stack height, checked by adding"))}</div>'))

end_slide('2.3', 'VStack &amp;<br>@ViewBuilder Internals', 'Lesson 2.4 &mdash; HStack &amp; Horizontal Layout',
          'You can now explain why VStack is a generic struct rather than a function, how the trailing closure supplies its content, how @ViewBuilder combines several views into one typed value, how the compiler infers VStack&lt;Content&gt;, how spacing, alignment and padding differ, and how a stack resizes when its children do. NPay now has a structured welcome screen.',
          'Next, Lesson 2.4: HStack and horizontal layout. A row of NPay quick actions, and how horizontal layout differs: alignment, flexible space, layout priorities, and HStack with Spacer.')

write_deck(OUT23, '2.3', 'VStack &amp; @ViewBuilder', 'VStack &amp; @ViewBuilder')
