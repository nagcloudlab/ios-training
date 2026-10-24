"""Generates decks/unit-2/lesson-2.6/index.html from the Lesson 2.6 text (SwiftUI View Modifiers: How They Really Work).
The text came in two parts (Sections 1-11, 12-21), grouped into 8 Parts. Console output and screenshots come from
tools/sim2_6 (a scripted SwiftUI app run in the iOS Simulator); interface lines from the iOS 26.5 SDK."""
import html, os, re, sys
OUT26 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.6', 'SwiftUI View Modifiers:<br>How They Really Work',
            'What actually happens when you write <code>.padding()</code>, <code>.frame()</code> or <code>.background()</code>, and why does <b>order</b> change the result?',
            'NPay is built from Text, Image and three kinds of stack, and the balance card works, but the interface still looks basic. Today: one of SwiftUI&rsquo;s most powerful ideas, view modifiers. What happens to a view when you write .padding, .frame, .background or .foregroundStyle, and why does their order change the result? Swift internals, experiments in the simulator, and a cleaner NPay.')
outcomes_slide('2.6', [("code", "A modifier <b>returns a new view</b>; the type changes"),
                       ("diff", "Why modifier <b>order</b> changes the result"),
                       ("frame", "What <code>.frame</code> really sizes"),
                       ("layers", "Which modifiers <b>flow down</b> the environment"),
                       ("gear", "Write your own <code>ViewModifier</code>"),
                       ("check", "Reusable views vs reusable <b>modifiers</b>")])
where_slide('2.6', 'Today: modifiers, deliberately', (),
            '2.5: a <code>ZStack</code> balance card.',
            'Modifiers: types, order, environment, custom ones.',
            'Last lesson NPay got its balance card from a ZStack. We have been using modifiers since 2.1 without looking closely; today we look closely, and use what we learn to restyle NPay with reusable components.',
            'The milestone.')

# ================================================================== Part 1 (1)
divider(1, "The milestone", "Composition, not a new screen", 'Same content, better styled, better structured.', 'Before and after.')
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "Milestone 2.6: a styled, reusable NPay", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Change", ul("A styled <b>BalanceCard</b>", "Quick actions as <b>tiles</b>", "Shared <b>card style</b>"))}
        {card("How", ul("<b>Composition</b> and <b>modifiers</b>", "Not a new screen architecture"))}
      </div>
      {PHONE("img/before.png", "Before: Lesson 2.5", 190)}
      <div class="step">{PHONE("img/final.png", "After: Milestone 2.6", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'On the left of the phones, NPay at the end of 2.5. Click: where we finish today: the same content, with the balance card as its own component and the quick actions as tiles. We get there through composition and modifiers, not a new screen architecture.'),
                  ('CONNECT', 'First: what is a modifier?'))))

# ================================================================== Part 2 (2-4, 13, 19)
divider(2, "What a modifier is", "A new value, a new type", 'Each call returns something new.', 'Follow a chain.')
CHAIN = """let title = Text("NPay")
let styled = title.font(.largeTitle)
let padded = styled.padding()"""
FOUR = """Text("NPay")
    .font(.largeTitle)
    .foregroundStyle(.blue)
    .padding()"""
S.append(slide("Part 2 &middot; What is a view modifier? (section 2)", "A chain of method calls", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", FOUR, "font-size:17px")}
        <div class="gap"></div>
        {card("One view, three calls", ul("Each returns a <b>new</b> view description", "The original is <b>not mutated</b>"))}</div>
      <div>{code("Method chaining (Unit 01)", CHAIN, "font-size:16px")}
        <div class="gap"></div>
        <div class="rule step" data-label="So">{ul("Each result is the next <b>receiver</b>", "Types can <b>change</b> along the chain: generics")}</div></div>
    </div>
  </div>""", notes(('SAY', 'One initial view value and three modifier calls. A modifier generally returns a new view description; it does not mutate the original value. Text, then font, then foregroundStyle, then padding: a final composed view.'),
                  ('SAY', 'This is ordinary Swift method-call syntax, from Unit 01. Written out with names: title, then styled from title, then padded from styled. Each call&rsquo;s result becomes the receiver of the next call.'),
                  ('SAY', 'Click: and the types can change along the chain. That is where generics come in.'),
                  ('CONNECT', 'Print the types.'))))

TYPES = """let card = Text("NPay")
let padded = card.padding()
let decorated = padded.background(.blue)

print(type(of: card))
print(type(of: padded))
print(type(of: decorated))"""
S.append(slide("Part 2 &middot; What .padding() returns (sections 3, 13, 19)", "Each wrapper is a new generic type", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Experiment.swift", TYPES, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{console("Also printed", ["Text(…).font(.largeTitle):  Text", "Text(…).foregroundStyle(.blue):  Text"], 13)}</div></div>
      <div>
        <div class="step">{console("Simulator console", ["Text", "ModifiedContent&lt;Text, _PaddingLayout&gt;", "ModifiedContent&lt;ModifiedContent&lt;Text,", "    _PaddingLayout&gt;, _BackgroundStyleModifier&lt;Color&gt;&gt;"], 13)}</div>
        <div class="gap"></div>
        {card("ModifiedContent", ul("A public generic struct: <b>content</b> + <b>modifier</b>", "Still a <code>View</code>", "<code>_PaddingLayout</code>: internal, may change"))}
        <div class="gap"></div>
        <div class="rule step" data-label="Not always">{ul("Text-specific modifiers can return <b>Text</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s experiment, from Sections 3, 13 and 19 together: a Text, the same Text padded, then that wrapped in a blue background, and print each type. Predict first.'),
                  ('SAY', 'Click: the simulator console. Text. Then ModifiedContent of Text and _PaddingLayout. Then ModifiedContent of that, with a background-style modifier for Color: a wrapper around a wrapper. The text&rsquo;s conceptual name PaddingModifier is really _PaddingLayout here; underscore types are SwiftUI internals and may change between versions.'),
                  ('SAY', 'ModifiedContent is a public generic struct that combines a content view and a modifier, and it is still a View, so you can keep chaining. Swift type-checks the whole chain at compile time; SwiftUI interprets the layout and styling at run time.'),
                  ('SAY', 'Click: not every modifier returns ModifiedContent. Click: the text-specific ones on Text, such as font and foregroundStyle, return Text, as we saw in 2.1. And no, a modifier does not create a new UIKit view; there is no one-to-one mapping.'),
                  ('CONNECT', 'Why can every kind of view use .padding?'))))

P = [box(400, 0, 336, 56, 'View protocol', 'Text, Image, stacks conform', None, 'lit', 'layers'),
     wire('M480 60V90H130V118' + head(130, 118, 'd')), wire('M568 60V118' + head(568, 118, 'd')), wire('M656 60V90H1006V118' + head(1006, 118, 'd')),
     box(0, 124, 260, 52, 'Text', '', None, '', 'file'), box(438, 124, 260, 52, 'Image', '', None, '', 'frame'), box(876, 124, 260, 52, 'VStack', '', None, '', 'layers'),
     wire('M130 180V206H568V230' + head(568, 230, 'd'), None, 'faint'), wire('M1006 180V206H568', None, 'faint'), wire('M568 180V206', None, 'faint'),
     box(338, 236, 460, 52, 'Shared modifiers', 'padding · frame · background · overlay', None, '', 'gear')]
S.append(slide("Part 2 &middot; Why almost every view has .padding() (section 4)", "Modifiers come from the View API", f"""  <div class="body">
    {svg('0 0 1136 288', 'Text, Image and VStack conform to View and so share padding, frame, background and overlay', 'shared', P, 'max-height:300px')}
    <div class="rule step" data-label="Composable" style="margin-top:14px">{ul("Conform to <code>View</code> &rarr; get every View modifier", "Including <code>ContentView</code> and your own views")}</div>
  </div>""", notes(('SAY', '.padding is part of SwiftUI&rsquo;s View API: it is declared in an extension on View. Text, Image, VStack, HStack and ZStack all conform to View, and so does every struct you write with ": View". Conforming gives them all the common modifiers: padding, frame, background, overlay.'),
                  ('SAY', 'Click: that is one of the reasons SwiftUI is so composable. Your own ContentView and BalanceCard get the same modifiers for free; Part 7 adds our own modifier to that list.'),
                  ('CONNECT', 'Now the most important experiment: order.'))))

# ================================================================== Part 3 (5, 14)
divider(3, "Modifier order", "Wrappers inside wrappers", 'Same modifiers, different order.', 'Run both.')
A = """Text("NPay")
    .padding(24)
    .background(.yellow)"""
B = """Text("NPay")
    .background(.yellow)
    .padding(24)"""
S.append(slide("Part 3 &middot; The most important experiment (section 5)", "Order decides what wraps what", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr) 280px;gap:22px;align-items:start">
      <div>{code("A: padding → background", A, "font-size:15px")}
        <div class="step" style="margin-top:10px">{code("A, conceptually", "Background(\n    Padding(\n        Text(\"NPay\")))", "font-size:14px")}</div></div>
      <div>{code("B: background → padding", B, "font-size:15px")}
        <div class="step" style="margin-top:10px">{code("B, conceptually", "Padding(\n    Background(\n        Text(\"NPay\")))", "font-size:14px")}</div></div>
      {crop("img/order.png", "A above, B below (.title)", 280)}
    </div>
    <div class="rule step" data-label="Measured" style="margin-top:10px">{ul("Both <b>112.0 × 89.7 pt</b>: same size, different composition")}</div>
  </div>""", notes(('SAY', 'The experiment we first met in 2.1, now with padding 24, run at title size: on the right, A on top, B below. Both compile; the result differs.'),
                  ('SAY', 'Click: why? Each modifier operates on the result of the previous expression. A is a background around padding around the text, so the yellow covers the padded region. Click: B is padding around a background around the text, so the yellow hugs the word and the padding is clear space outside. These nested names are conceptual, not real SwiftUI code.'),
                  ('SAY', 'Click: both measured 112 by 89.7 points: the layout size is the same, the composition is not.'),
                  ('CONNECT', 'Order also matters for layout modifiers. The balance card has three.'))))

FP = """VStack(alignment: .leading, spacing: 12) {
    Text("Available Balance")
    Text("₹25,000")
    Text("NPay Demo Account")
}
.frame(maxWidth: .infinity, alignment: .leading)
.padding(24)
.background(.blue)"""
S.append(slide("Part 3 &middot; Order and the layout engine (section 14)", "Frame, padding, background: three orders", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.75fr) 290px;gap:22px;align-items:start">
      {code("The card&rsquo;s order (top)", FP, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("All three measured", ["370.0 × 145.0 pt"], 14)}</div>
        <div class="step">{card("What we saw", ul("frame &harr; padding: <b>no change</b> here", "bg before padding: blue <b>shrinks</b>"))}</div>
        <div class="rule step" data-label="Layout">{ul("<b>Transformations</b>, not properties")}</div></div>
      {crop("img/framepad.png", "frame→padding→bg · padding→frame→bg · frame→bg→padding", 290)}
    </div>
  </div>""", notes(('SAY', 'The card&rsquo;s content with three layout-related modifiers. Layout modifiers change how size proposals and chosen sizes flow through the composition. On the right, three orders in the simulator: frame then padding then background, which is our code; padding then frame then background; and frame then background then padding.'),
                  ('SAY', 'Click: all three take 370 by 145 points. Click: and the first two look identical: in this parent, the flexible frame takes the full width either way and the leading alignment plus padding put the text in the same place. The text&rsquo;s toggle hinted at a difference; with this parent there is none, which is exactly its caveat that differences depend on the parent proposal. The third one does differ: the background comes before the padding, so the blue no longer includes the padding.'),
                  ('SAY', 'Click: the lesson is the model, not the pixels: SwiftUI layout is a composition of transformations, not a list of style properties on one mutable object. Check order by running it, with a border or background.'),
                  ('CONNECT', 'Frames deserve a closer look.'))))

# ================================================================== Part 4 (6-7)
divider(4, "Frames", "A layout region, not the content", '.frame(width: 200): is the text now 200 points wide?', 'Measure it.')
FR = """Text("NPay")
    .frame(width: 200, height: 100)

Text("NPay")
    .frame(maxWidth: .infinity)

Text("NPay")
    .frame(maxWidth: .infinity, alignment: .leading)"""
S.append(slide("Part 4 &middot; Understanding .frame() (sections 6&ndash;7)", "The frame changes the region, not the text", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 300px;gap:22px;align-items:start">
      {code("Frames.swift (blue borders added)", FR, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{console("Measured (.title)", ["frame: 200.0 × 100.0 pt", "the Text inside: 64.0 × 41.7 pt", "maxWidth .infinity: 370.0 pt wide"], 13)}</div>
        <div class="rule step" data-label=".infinity">{ul("An <b>unbounded maximum</b>", "Grows to what the parent offers")}</div>
        <div class="step">{card(".leading", ul("Aligns content <b>within</b> the region"))}</div></div>
      {crop("img/frame.png", SIM, 300)}
    </div>
  </div>""", notes(('SAY', '.frame adds a layout container that proposes and reports dimensions by its own rules. It does not resize the glyphs. On the right, the text&rsquo;s three frames with blue borders, run at title size in place of the text&rsquo;s slider.'),
                  ('SAY', 'Click: measured. The frame is exactly 200 by 100; the Text inside it is still 64 by 41.7, its own size, centred. So .frame(width: 200) does not make the text 200 points wide; it makes the region 200 wide. With maxWidth .infinity the frame took the full 370 points the parent offered.'),
                  ('SAY', 'Click: .infinity is an unbounded maximum in the layout API, not physical infinite width; negotiation decides the real size. Click: and a view can occupy a wide frame while its visible content stays small, which is why alignment .leading is useful: it places the content within the larger region, as the third row shows.'),
                  ('CONNECT', 'Next: two modifiers that sound alike.'))))

# ================================================================== Part 5 (8, 9, 15)
divider(5, "Style and the environment", "Some modifiers flow down", 'Foreground or background? And which modifiers reach the children?', 'Compare.')
S.append(slide("Part 5 &middot; Foreground style vs background (section 8)", "Two different roles", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Two modifiers", 'Text("NPay")\n    .foregroundStyle(.blue)\n\nText("NPay")\n    .background(.blue)', "font-size:17px")}
        <div class="gap"></div>
        {card(".blue", ul("Inferred from the <b>expected</b> style type", "No full type name needed"))}</div>
      <div>{crop("img/fgbg.png", "Left: foregroundStyle. Right: background (.largeTitle)", 440)}
        <div class="gap"></div>
        <div class="step">{card("Different roles", ul("<code>foregroundStyle</code>: the <b>foreground</b> (the glyphs)", "<code>background</code>: a view <b>behind</b>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'foregroundStyle(.blue) colours the foreground, the glyphs; background(.blue) puts a blue view behind the text. On the right, both at largeTitle size. In both, .blue is inferred from the type the API expects, so you do not repeat the full type name; 2.2 showed the ShapeStyle extension behind it.'),
                  ('SAY', 'Click: different roles, even though both just say blue.'),
                  ('CONNECT', 'Some modifiers do more than style one view: they reach its children.'))))

ENV = """VStack {
    Text("NPay")
    Text("Payments made simple")
}
.font(.title)

VStack {
    Text("Available Balance")
        .foregroundStyle(.yellow)
    Text("₹25,000")
}
.foregroundStyle(.white)"""
S.append(slide("Part 5 &middot; Environment-driven modifiers (sections 9, 15)", "Set it on the parent; children inherit", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr) 290px;gap:22px;align-items:start">
      {code("Environment.swift", ENV, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Flows down", ul("<code>.font</code>, <code>.foregroundStyle</code>", "Through the <b>environment</b>", "A child can <b>override</b>"))}
        <div class="rule step" data-label="Stays put">{ul("<code>.padding()</code>: only around the view it is on")}</div></div>
      {crop("img/env.png", "Middle: .padding() on the stack only. Bottom: on blue to show white", 290)}
    </div>
  </div>""", notes(('SAY', 'Top on the right: .font(.title) on the VStack reaches both texts. The parent does not mutate each child; SwiftUI propagates environment values down the hierarchy, and each Text reads the font.'),
                  ('SAY', 'Bottom: .foregroundStyle(.white) on the stack, with the first Text overriding it with yellow. The first is yellow, the second inherits white. We added a blue background so white is visible. That is how a reusable component sets default styles high up while specific children override them.'),
                  ('SAY', 'Click: not every modifier propagates. The middle example puts .padding() on the stack: the blue border shows space around the stack only; the grey-bordered children got no padding of their own. Knowing which modifiers flow down matters when you build reusable components.'),
                  ('CONNECT', 'Which brings us to building them.'))))

# ================================================================== Part 6 (10-12, 21)
divider(6, "Reusable views", "BalanceCard and QuickAction", 'Extract the card and the actions into their own views.', 'The card first.')
BC = """struct BalanceCard: View {
    var body: some View {
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
        .background(.blue, in: RoundedRectangle(cornerRadius: 20))
    }
}"""
ORDER = [("1", "content", "three texts"), ("2", "<code>foregroundStyle</code>", "flows to all"),
         ("3", "<code>frame(maxWidth:)</code>", "full width"), ("4", "<code>padding(24)</code>", "inner space"),
         ("5", "<code>background(_:in:)</code>", "behind it all")]
S.append(slide("Part 6 &middot; A reusable balance card (section 10)", "BalanceCard: order on purpose", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:24px;align-items:start">
      {code("BalanceCard.swift", BC, "font-size:12.5px")}
      <div>{tbl(["", "Step", "Why"], ORDER)}
        <div class="rule step" data-label="Deliberate" style="margin-top:12px">{ul("Content &rarr; style &rarr; size &rarr; space &rarr; backdrop")}</div></div>
    </div>
  </div>""", notes(('SAY', 'We extract the card into its own view, BalanceCard. Instead of a ZStack it uses .background with a rounded rectangle, as in 2.5&rsquo;s Experiment C.'),
                  ('SAY', 'Read the modifier order as a recipe. First build the content. Then the foreground style, which flows to all three texts. Then let the region expand horizontally, leading-aligned. Then pad it. Finally draw the blue rounded background behind the padded region. Click: deliberate composition: each step wraps the one before.'),
                  ('CONNECT', 'The quick actions get the same treatment.'))))

QA = """struct QuickAction: View {
    let symbol: String
    let title: String

    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: symbol)
                .font(.title2)
            Text(title)
                .font(.caption)
        }
        .foregroundStyle(.blue)
        .frame(maxWidth: .infinity)
        .padding(.vertical, 12)
        .background(Color.blue.opacity(0.08),
                    in: RoundedRectangle(cornerRadius: 12))
    }
}"""
S.append(slide("Part 6 &middot; Complete NPay code (sections 11, 21)", "ContentView assembles; components draw", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.1fr) minmax(0,.6fr) 170px;gap:22px;align-items:start">
      {code("QuickAction.swift", QA, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("ContentView", ul("Header: icon, title, subtitle", "<code>BalanceCard()</code>", "<code>HStack(spacing: 30)</code> of 3 <code>QuickAction</code>s"))}
        <div class="step">{card("Checkpoint 2.6", ul("Reusable components", "Consistent spacing and style"))}</div></div>
      {PHONE("img/final.png", "Milestone 2.6", 170)}
    </div>
  </div>""", notes(('SAY', 'QuickAction takes a symbol name and a title, and stacks the symbol over the label. Then the same recipe: blue foreground, flexible width so the three tiles share the row equally, vertical padding, and a pale blue rounded background. Note .frame(maxWidth: .infinity): that is the equal-widths technique from 2.4.'),
                  ('SAY', 'ContentView now only assembles: the header, BalanceCard(), and an HStack of three QuickActions for Send, Request and History. The full code is in the lesson text. On the right, the real screen.'),
                  ('SAY', 'Click: the Section 21 checkpoint: a branded header, a styled balance card, reusable quick actions, consistent spacing, and next, a custom modifier for shared styling.'),
                  ('CONNECT', 'What does SwiftUI do when it meets BalanceCard() inside ContentView.body?'))))

TR = """struct TracedCard: View {
    init() { print("2. TracedCard value constructed") }
    var body: some View {
        let _ = print("3. TracedCard.body evaluated")
        BalanceCard()
    }
}
// parent body: let _ = print("1. … body evaluated")"""
STG = [("code", "Parent body evaluated", "ContentView.body runs"), ("diff", "BalanceCard() constructed", "a Swift value"),
       ("eye", "BalanceCard.body evaluated", "when SwiftUI needs it"), ("layers", "Modifiers wrap the VStack", "a nested description"),
       ("layout", "Layout", "sizes proposed and chosen"), ("frame", "Rendering", "text and the rounded blue card")]
P = [box(0, i * 52, 560, 44, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(STG)]
S.append(slide("Part 6 &middot; Evaluating BalanceCard (section 12) &middot; conceptual", "Constructing a view &ne; evaluating its body", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      {svg('0 0 560 304', 'Parent body evaluated, BalanceCard constructed, its body evaluated, modifiers wrap, layout, rendering', 'eval', P, 'max-height:330px')}
      <div>{code("Trace.swift (excerpt)", TR, "font-size:12px")}
        <div class="step" style="margin-top:10px">{console("Simulator console, at launch", ["1. TraceView.body evaluated", "2. TracedCard value constructed", "3. TracedCard.body evaluated"], 13)}</div></div>
    </div>
  </div>""", notes(('SAY', 'A conceptual walk; only the final stage, rendering, was in the text&rsquo;s widget. Click: the parent&rsquo;s body is evaluated. Click: inside it, BalanceCard() constructs a Swift value, nothing more. Click: SwiftUI evaluates BalanceCard&rsquo;s body when it needs it. Click: the modifiers wrap the VStack into a nested description. Click: layout. Click: rendering produces the text and the rounded blue card.'),
                  ('SAY', 'We made steps 1 to 3 visible: a print in the parent&rsquo;s body, in the card&rsquo;s init and in the card&rsquo;s body. At launch the console shows exactly that order: parent body, card constructed, card body.'),
                  ('SAY', 'The point: constructing a view value and evaluating its body are separate operations. SwiftUI can evaluate bodies selectively; it does not necessarily run every body on every update. Prints like these are for learning, never for app logic.'),
                  ('CONNECT', 'Reusable views are one tool. Reusable modifiers are the other.'))))

# ================================================================== Part 7 (16-18)
divider(7, "Custom modifiers", "Reusable styling", 'NPay wants one consistent card style everywhere.', 'Write a ViewModifier.')
CM = """struct NPayCardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(20)
            .background(
                Color.blue.opacity(0.08),
                in: RoundedRectangle(cornerRadius: 16)
            )
    }
}

extension View {
    func npayCardStyle() -> some View {
        modifier(NPayCardStyle())
    }
}"""
S.append(slide("Part 7 &middot; A custom ViewModifier (sections 16&ndash;17)", "NPayCardStyle, and a View extension", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 250px minmax(0,.7fr);gap:22px;align-items:start">
      {code("NPayCardStyle.swift", CM, "font-size:12.5px")}
      {crop("img/custom.png", "plain · .modifier · .npayCardStyle()", 250)}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("type(of:), both forms", ["ModifiedContent&lt;Text,", "  NPayCardStyle&gt;"], 13)}</div>
        <div class="step">{card("Unit 01, again", ul("A <b>protocol</b>, no UIKit subclass", "Extension on <code>View</code>: every view gets it"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI defines a ViewModifier protocol. NPayCardStyle conforms to it: its body receives the content being modified and returns a composed view, here padded with a pale blue rounded background. Apply it with .modifier(NPayCardStyle()).'),
                  ('SAY', 'Then a View extension adds npayCardStyle(), so you can write it like any built-in modifier. On the right: plain, with .modifier, and with .npayCardStyle(). Click: both forms print the same type, ModifiedContent of Text and NPayCardStyle: our own type sits exactly where _PaddingLayout sat earlier.'),
                  ('SAY', 'Click: no UIKit subclass: a struct conforming to a protocol. And because the extension is on View, every conforming view can call it: protocol extensions from Unit 01, and one consistent NPay design language without repeated styling code.'),
                  ('CONNECT', 'So when do you write a view, and when a modifier?'))))

VM = [("Encapsulates", "content and structure", "a transformation or styling"), ("Example", "<code>BalanceCard</code>", "<code>NPayCardStyle</code>"),
      ("Can", "own state or receive models", "decorate or modify content"), ("Represents", "a meaningful UI component", "reusable presentation behaviour")]
S.append(slide("Part 7 &middot; Custom modifier or reusable view? (section 18)", "Component or styling rule?", f"""  <div class="body">
    {tbl(["", "Reusable view", "Custom ViewModifier"], VM, 'tbl')}
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("A view when", ul("It is a <b>recognisable UI element</b>", "with its own content and behaviour"))}
      {card("A modifier when", ul("It is a <b>styling rule</b>", "for many unrelated views"))}
    </div>
  </div>""", notes(('SAY', 'An architecture decision. A reusable view encapsulates content and structure, like BalanceCard; it can own state or receive models, and it represents a meaningful UI component. A custom ViewModifier encapsulates a transformation or styling behaviour, like NPayCardStyle; it decorates content and represents reusable presentation behaviour.'),
                  ('SAY', 'Click: the rule of thumb. If it is a recognisable UI element with its own content and behaviour, make a view. If it is a styling rule you would apply to many unrelated views, make a modifier.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.6', (), [("code", "Modifiers wrap", "a new value and often a new type"),
                     ("diff", "Order is structure", "what wraps what decides the result"),
                     ("layers", "Some flow down", "font and style via the environment")],
         'Three things to remember. A modifier returns a new view, usually a ModifiedContent wrapping the old one, sometimes the same type, as Text&rsquo;s own modifiers do. Order is structure: each modifier wraps the result of the one before, so changing the order changes the composition. And some modifiers, like font and foregroundStyle, flow down the environment to children, while others, like padding, stay on the view they are applied to.')

review_divider(8)
review([("code", "Question", "Does every modifier mutate the original view?",
         "Does a SwiftUI modifier mutate the original view?", "No",
         "It returns a new value: <code>card</code> stayed <code>Text</code> while <code>padded</code> became a <code>ModifiedContent</code>.",
         "Picturing a mutable UI object.", "Some say yes.", None),
        ("diff", "Question", "Does every modifier return ModifiedContent?",
         "Does every modifier return a <code>ModifiedContent</code>?", "No",
         "<code>Text(…).font(…)</code> and <code>.foregroundStyle(…)</code> printed <code>Text</code>.",
         "Generalising from <code>.padding()</code>.", "Some say yes.", None),
        ("layers", "Choose one", "Why can Text, Image and VStack use padding?",
         "Why can <code>Text</code>, <code>Image</code> and <code>VStack</code> all use <code>.padding()</code>?<br>A. They inherit from <code>UIView</code><br>B. They conform to <code>View</code><br>C. They are all classes", "B",
         "<code>.padding</code> is declared on the <code>View</code> protocol&rsquo;s API; conforming types get it.",
         "Thinking in class inheritance.", "Some pick A.", None),
        ("layout", "Question", "Does modifier order affect the result?",
         "Does modifier order affect the result?", "Yes",
         "padding&rarr;background colours the padded area; background&rarr;padding only the text.",
         "Treating modifiers as a set of properties.", "Most say yes.", None),
        ("eye", "Question", "Can parent styling influence descendant views?",
         "Can styling on a parent influence its descendant views?", "Yes",
         "<code>.font(.title)</code> on a VStack reached both texts; a child can still override.",
         "Assuming every modifier stays on its view.", "Most say yes.", None),
        ("gear", "Choose one", "What does a ViewModifier represent?",
         "What does a <code>ViewModifier</code> represent?<br>A. A reusable view transformation<br>B. A UIKit subclass<br>C. A new Swift thread", "A",
         "<code>NPayCardStyle</code> takes content and returns it padded with a background.",
         "Expecting UIKit underneath.", "Some pick B.", None),
        ("diff", "Predict the output", "Type of Text(\"NPay\").padding().background(.blue)?",
         "What does <code>type(of:)</code> print for <code>Text(\"NPay\").padding().background(.blue)</code>?<br>A. <code>Text</code><br>B. <code>ModifiedContent&lt;Text, &hellip;&gt;</code> with one wrapper<br>C. <code>ModifiedContent&lt;ModifiedContent&lt;Text, &hellip;&gt;, &hellip;&gt;</code>", "C",
         "Each modifier wraps the result of the previous one: two wrappers.",
         "Expecting one flat wrapper.", "Some pick B.", None),
        ("frame", "Question", "From 2.5: does an overlay grow its primary view?",
         "From Lesson 2.5: does an oversized <code>.overlay</code> make its primary view bigger?", "No",
         "The shape stayed 240 &times; 120 pt while the overlay text spilled over.",
         "Expecting overlays to take part in sizing.", "Some say yes.", "Spaced review from Lesson 2.5.")])

S.append(next_slide('2.6', [("2.7", "Button, closures &amp; event handling", "NPay becomes interactive: tap &rarr; Button &rarr; action closure"),
                            ("Later", "State-driven NPay", "the balance card fed by real state")],
                    'Next lesson makes NPay interactive for the first time: the full event path from a finger tap through iOS input handling to a SwiftUI Button and its action closure, plus button styles, hit testing, accessibility, and keeping business logic out of the view. It is the first step toward state-driven NPay.'))

S.append(lab_slide('2.6', "Modifiers under the microscope", "Predict, run, explain.",
                   ["Print the three types of Section 19.",
                    "Swap <code>.padding(24)</code> and <code>.background(.yellow)</code>.",
                    "Border a <code>.frame(width: 200, height: 100)</code>; measure the Text.",
                    "<code>.font</code> on a VStack; override one child.",
                    "Write <code>NPayCardStyle</code> and <code>.npayCardStyle()</code>.",
                    "Refactor to <code>BalanceCard</code> and <code>QuickAction</code>."],
                   "", 'Expected, as in our simulator runs: Text, ModifiedContent<Text, _PaddingLayout>, then a ModifiedContent of that with _BackgroundStyleModifier<Color>; both orders take the same size but colour different regions; the frame is 200 x 100 while the Text keeps its own size; the font reaches every child unless one overrides; the custom modifier prints ModifiedContent<Text, NPayCardStyle>.'.replace('<', '&lt;').replace('>', '&gt;'),
                   side=f'<div>{card("You hand in", ul("Your printed types, each explained", "One screenshot per experiment", "A one-line reason: view or modifier?"))}</div>'))

end_slide('2.6', 'SwiftUI View Modifiers:<br>How They Really Work', 'Lesson 2.7 &mdash; Button, Closures &amp; Event Handling',
          'You can now explain that a modifier returns a new, often differently typed view, why order changes the composition, what .frame really sizes, which modifiers flow down the environment, how to write your own ViewModifier with a View extension, and when to choose a reusable view instead. NPay has reusable, consistently styled components.',
          'Next, Lesson 2.7: Button, closures and event handling. NPay becomes interactive: the event path from a finger tap to an action closure, button styles, hit testing, accessibility, and business logic out of the view.')

write_deck(OUT26, '2.6', 'View Modifiers', 'View Modifiers')
