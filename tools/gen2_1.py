"""Generates decks/unit-2/lesson-2.1/index.html from the Lesson 2.1 text (SwiftUI Text: From Source Code to Screen).
Unit 02 restarts here. The 16 sections are grouped into 8 Parts. Console output and screenshots come from
tools/sim2_1 (a scripted SwiftUI app run in the iOS Simulator); interface lines come from the iOS 26.5 SDK."""
import html, os, re, sys
OUT21 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.1', 'SwiftUI Text:<br>From Source Code to Screen',
            'One word on an iPhone: <b>NPay</b>. What do Swift, SwiftUI and iOS do to put it there?',
            'Unit 02 starts here, on an iPhone. You know Swift, memory, processes and concurrency from Units 00 and 01; now we use that to understand how iOS apps are actually built. Today has one concept, SwiftUI Text, and we take it all the way: what Text is, how Swift finds it, what some View means, how SwiftUI measures it, and how it reaches the screen. Every screenshot and console line today came from a small SwiftUI app we ran in the iOS Simulator.')
outcomes_slide('2.1', [("code", "What <code>Text(\"NPay\")</code> <b>is</b>, and how Swift finds it"),
                       ("layers", "Why <code>ContentView</code> <b>conforms to View</b>"),
                       ("eye", "What <code>some View</code> <b>hides</b>"),
                       ("layout", "How SwiftUI <b>sizes and places</b> text"),
                       ("diff", "How <b>modifiers</b> wrap views, and why order matters"),
                       ("globe", "Unicode, <b>localization</b> and Dynamic Type")])
where_slide('2.1', 'Today: NPay&rsquo;s first screen', (),
            'Unit 01 (1.10): NPay&rsquo;s engine in plain Swift, tested on any computer.',
            'Unit 02 starts on an iPhone: one screen, one <code>Text</code>.',
            'Unit 01 gave us the Swift language and NPay&rsquo;s domain model. Unit 02 builds the interface with SwiftUI, in Xcode, on an iPhone simulator. We start as small as possible: one Text view. Lesson 2.2 adds an image above it.',
            'First, the requirement.')

# ================================================================== Part 1 (1-2)
divider(1, "The first screen", "One requirement, one word", 'NPay&rsquo;s first requirement is tiny on purpose: one word on the screen.', 'Here is the requirement.')
LOOP = [("code", "Build", "something small"), ("eye", "Predict", "before running"), ("play", "Run", "simulator or preview"),
        ("gear", "Investigate", "the internals"), ("diff", "Experiment", "change one thing"), ("check", "Improve NPay", "keep what works")]
P = [box(0, i * 52, 460, 44, t, sub, None, 'lit' if i == 0 else '', ic) for i, (ic, t, sub) in enumerate(LOOP)]
S.append(slide("Part 1 &middot; The engineering story (section 1)", "Milestone 2.1: NPay&rsquo;s name, centred", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:32px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Requirement", ul("When NPay launches, show its <b>name</b>", "In the <b>centre</b> of the screen"))}
        {card("Not yet", ul("No icons, buttons or layouts", "<b>One</b> component, investigated thoroughly"))}
      </div>
      <div>
        <p class="kicker" style="margin:0 0 8px;color:var(--muted)">How every lesson runs</p>
        {svg('0 0 460 304', 'Build, predict, run, investigate, experiment, improve NPay', 'loop', P, 'max-height:330px')}
      </div>
    </div>
  </div>""", notes(('SAY', 'We are building NPay, a payment app. The first requirement: when NPay launches, display the app&rsquo;s name in the centre of the screen. That is Milestone 2.1.'),
                  ('SAY', 'No icons, buttons or layouts yet. We investigate one SwiftUI component thoroughly, using the same loop every lesson: build something small, predict, run, investigate the internals, experiment, then improve NPay.'),
                  ('CONNECT', 'Build it.'))))

HELLO = """import SwiftUI

struct ContentView: View {

    var body: some View {
        Text("NPay")
    }
}

#Preview {
    ContentView()
}"""
S.append(slide("Part 1 &middot; Build (section 2)", "Our first SwiftUI view", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:32px;align-items:center">
      <div>{code("ContentView.swift", HELLO, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{card("Run it", ul("<b>⌘R</b>, or the Canvas preview", "NPay appears near the <b>centre</b>"))}</div></div>
      {PHONE("img/hello.png", SIM, 180)}
    </div>
  </div>""", notes(('SAY', 'Open your NPay Xcode project and put this in ContentView.swift: import SwiftUI, a ContentView struct whose body is Text("NPay"), and a #Preview so the canvas can show it.'),
                  ('SAY', 'Click: press Command-R to run, or use the canvas. On the right is the real result on an iPhone 17 simulator: the word NPay, small, in the middle of the screen.'),
                  ('CONNECT', 'We have a working feature. Now: what exactly did we write?'))))

# ================================================================== Part 2 (3-4)
divider(2, "What is Text?", "A struct, found by the compiler", 'Text("NPay"): is that a function, a class, a UIKit object?', 'Break it down.')
PARTS = [("<code>Text</code>", "SwiftUI struct"), ("<code>(...)</code>", "initializer call"), ("<code>\"NPay\"</code>", "string literal"), ("Result", "a <b>Text value</b> describing UI content")]
CUST = """struct Customer {
    let name: String
}

let customer = Customer(name: "Ravi")  // a Customer value
let title = Text("NPay")               // a Text value"""
S.append(slide("Part 2 &middot; What is Text? (section 3)", "<code>Text(\"NPay\")</code> makes a value", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{tbl(["Part", "Meaning"], PARTS, 'tbl')}
        <div class="gap"></div>
        <div class="rule step" data-label="Pixels yet?">{ul("No: a declarative <b>view value</b>", "SwiftUI lays out and renders it separately")}</div></div>
      <div>{code("Values.swift", CUST, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{card("Same mechanism, different purpose", ul("<code>Customer</code> models <b>domain data</b>", "<code>Text</code> describes <b>interface content</b>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'Text is not a function, not a class and not a UIKit object. It is a struct defined in SwiftUI, and it conforms to the View protocol. Text is the type, the parentheses call an initializer, "NPay" is a string literal, and the result is a Text value describing UI content.'),
                  ('SAY', 'Click: does Text("NPay") draw pixels immediately? No. It creates a declarative view value; SwiftUI does layout and rendering separately.'),
                  ('SAY', 'Click: you have seen this mechanism in Unit 01. Customer(name: "Ravi") creates a Customer value; Text("NPay") creates a Text value. The difference is purpose: Customer models domain data, Text describes interface content.'),
                  ('CONNECT', 'How does the compiler know what Text is?'))))

FIND = [("frameworks", "import SwiftUI", "declarations available"), ("code", "Text", "type resolved"), ("file", "\"NPay\"", "string literal"),
        ("decision", "Overloads", "picks an initializer"), ("check", "Text value", "statically typed")]
P = []
for i, (ic, t, sub) in enumerate(FIND):
    x = i * 232
    P.append(tall(x, 0, 208, 120, ic, t, sub, str(i + 1) if i < 4 else '5+'))
    if i < 4:
        P.append(wire(f'M{x + 210} 60H{x + 228}' + head(x + 228, 60, 'r')))
S.append(slide("Part 2 &middot; How Swift finds Text (section 4)", "From <code>import SwiftUI</code> to a Text value", f"""  <div class="body">
    {cues(5)}
    {svg('0 0 1136 120', 'import SwiftUI, resolve Text, process the string literal, choose an initializer, a Text value', 'find', P, 'max-height:150px')}
    <div class="gap-lg"></div>
    <div class="cols" style="{TWO};gap:24px">
      {card("At compile time", ul("Imported <b>module</b> information resolves <code>Text</code>", "No lookup by name at run time"))}
      {card("A module exposes", ul("<code>Text</code>, <code>Image</code>, <code>Button</code>, <code>VStack</code>, &hellip;"))}
    </div>
  </div>""", notes(('SAY', 'Five steps, all in the compiler. Click: import SwiftUI makes SwiftUI&rsquo;s declarations available. Click: the compiler resolves the name Text to SwiftUI&rsquo;s type. Click: it processes the string literal "NPay". Click: overload resolution picks a compatible Text initializer. Click: the result is a Text value, a statically typed view description.'),
                  ('SAY', 'All of that happens at compile time from the imported module&rsquo;s information; nothing looks Text up by name while the app runs. SwiftUI exposes Text, Image, Button, VStack and many more.'),
                  ('CONNECT', 'You can read that module information yourself.'))))

IFACE = """// SwiftUI.swiftinterface
@_exported import SwiftUICore

// SwiftUICore.swiftinterface
@frozen public struct Text : Equatable, Sendable
extension Text : View"""
S.append(slide("Part 2 &middot; Jump to Definition (section 4)", "Read the interface; don&rsquo;t memorise it", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.8fr) minmax(0,1.2fr);gap:28px;align-items:start">
      <div>{card("In Xcode", ul("Hold <b>⌘</b> and click <code>Text</code>", "Choose <b>Jump to Definition</b>"))}
        <div class="gap"></div>
        <div class="step">{card("What it tells us", ul("<code>Text</code> is a <b>struct</b>", "Its View conformance is an <b>extension</b>", "<code>import SwiftUI</code> brings SwiftUICore along"))}</div></div>
      <div>{code("Interface excerpt, iOS 26.5 SDK", IFACE, "font-size:15px")}
        <p class="small muted" style="margin:8px 0 0">The text expects roughly <code>public struct Text: View</code>; the exact interface differs by Xcode and SDK version.</p></div>
    </div>
  </div>""", notes(('SAY', 'Instead of memorising APIs, inspect them. Command-click Text and choose Jump to Definition; Xcode shows the generated interface.'),
                  ('SAY', 'These lines are from the iOS 26.5 SDK we built against. Text is declared as a frozen public struct, Equatable and Sendable, in a module called SwiftUICore; its View conformance is in an extension. SwiftUI re-exports SwiftUICore, so import SwiftUI is all you write. Older SDKs show it directly in SwiftUI; the exact interface varies by version.'),
                  ('SAY', 'Click: so Text is a struct, it conforms to View, and one import gives you both.'),
                  ('CONNECT', 'What does conforming to View mean?'))))

# ================================================================== Part 3 (5-6)
divider(3, "View and some View", "A protocol and a hidden type", 'struct ContentView: View. Inheritance, or something else?', 'The protocol first.')
PROTO = """// Teaching approximation, not Apple's exact API

protocol View {
    associatedtype Body: View

    @ViewBuilder
    var body: Body { get }
}"""
P = [box(130, 0, 300, 56, 'View protocol', 'requires a body', None, 'lit', 'layers'),
     wire('M130 150V100H280V62' + head(280, 62, 'u'), None, 'dash'), wire('M430 150V100H280', None, 'dash'),
     box(0, 150, 260, 56, 'ContentView', 'conforms', None, '', 'phone'), box(300, 150, 260, 56, 'Text', 'conforms', None, '', 'code')]
S.append(slide("Part 3 &middot; The View protocol (section 5)", "Conformance, not inheritance", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("View (mental model)", PROTO, "font-size:15px")}
        <div class="gap"></div>
        {card("The parts", ul("<code>Body</code>: each view&rsquo;s own body <b>type</b>", "<code>body</code>: the view&rsquo;s content", "<code>@ViewBuilder</code>: composing child views"))}</div>
      <div>{svg('0 0 560 206', 'ContentView and Text both conform to the View protocol', 'proto', P, 'max-height:220px')}
        <div class="gap"></div>
        <div class="step">{console("Real interface, iOS 26.5 SDK", ["associatedtype Body : View", "@ViewBuilder @MainActor var body: Self.Body { get }"], 13)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="Inheritance?">{ul("ContentView doesn&rsquo;t inherit from Text", "Its body returns something that <b>is a View</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'struct ContentView: View is protocol conformance, not class inheritance; we studied protocols in Unit 01. Here is a simplified model of View: an associated type Body that must itself be a View, a body property of that type, and @ViewBuilder, which lets you compose child views declaratively.'),
                  ('SAY', 'ContentView satisfies the protocol because its body produces a Text, and Text also conforms to View. Both sit under the same protocol.'),
                  ('SAY', 'Click: the real interface is close to our model; the two requirement lines say the same thing, and add that body runs on the main actor, as in Lesson 1.9.'),
                  ('SAY', 'Click: ContentView does not inherit from Text. It only needs to return a view description that satisfies View.'),
                  ('CONNECT', 'Now the strangest part of the signature: some View.'))))

OPQ = """var body: some View {
    Text("NPay")
}"""
S.append(slide("Part 3 &middot; some View (section 6)", "<code>some View</code>: one concrete type, hidden", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", OPQ, "font-size:17px")}
        <div class="gap"></div>
        {tbl(["Compiler&rsquo;s view", ""], [("Declared", "<code>some View</code>"), ("Underlying type", "<code>Text</code>"), ("Requirement", "<code>Text</code> conforms to <code>View</code>")])}</div>
      <div>
        <div class="step">{console("type(of: body), in the simulator", ["ContentView.body: Text", "with a .frame (Part 5):", "ModifiedContent&lt;Text, _FlexFrameLayout&gt;"], 13)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="Not &ldquo;any View&rdquo;">{ul("One underlying type <b>per declaration</b>", "Not a different type on each evaluation", "Matters for conditional views, later")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Why some View and not just View? some View is an opaque return type, from Lesson 1.6. The implementation returns one specific concrete type that conforms to View, and hides which one from callers. The compiler knows: declared some View, underlying type Text, and Text conforms to View.'),
                  ('SAY', 'Click: we printed type(of:) on the body in the simulator. ContentView&rsquo;s body is exactly Text. Add the .frame from Part 5 and the hidden type becomes ModifiedContent of Text and a frame layout: still one type, just a different one. The underscore name is SwiftUI&rsquo;s private implementation type.'),
                  ('SAY', 'Click: some View does not let body return a different concrete type each time it runs. The opaque type is fixed for that declaration. We will see why that matters when we write conditional views.'),
                  ('CONNECT', 'So we have a Text value. How does it become pixels?'))))

# ================================================================== Part 4 (7)
divider(4, "From value to pixels", "What happens at runtime", 'Creating a Text value is not drawing it.', 'Follow the journey.')
RUN = [("phone", "iOS launches NPay", "the process starts; the SwiftUI app lifecycle begins"),
       ("frame", "The scene shows ContentView", "it becomes the window&rsquo;s root view"),
       ("eye", "SwiftUI reads body", "and gets a Text value: a description"),
       ("layout", "Layout", "space is proposed; Text measures; it is placed"),
       ("code", "Rendering", "the glyphs are drawn for the next frame"),
       ("check", "On screen", "the frame is shown: NPay is visible")]
P = [box(0, i * 58, 680, 48, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(RUN)]
S.append(slide("Part 4 &middot; At runtime (section 7) &middot; conceptual", "From launch to visible text", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1.45fr) minmax(0,.55fr);gap:28px;align-items:center">
      <div>{svg('0 0 680 338', 'iOS launches NPay, the scene shows ContentView, SwiftUI reads body, layout, rendering, on screen', 'run', P, 'max-height:380px')}
        <div class="takeaway step" style="margin-top:12px">Making a <code>Text</code> value &ne; drawing text: the framework measures, places and renders it.</div></div>
      {PHONE("img/hello.png", "Step 6", 170)}
    </div>
  </div>""", notes(('SAY', 'A conceptual walk from launch to text; SwiftUI&rsquo;s private implementation is not fully public, so read this as the shape, not the exact internals. Click: iOS launches NPay; the process starts and the SwiftUI app lifecycle begins, as in Unit 00.'),
                  ('SAY', 'Click: the app&rsquo;s scene shows ContentView as the window&rsquo;s root view. Click: SwiftUI reads body and gets a Text value, a description. Click: layout: space is proposed, Text measures itself, and it is placed. Click: rendering draws the glyphs for the next frame. Click: the frame is shown, and NPay is visible.'),
                  ('SAY', 'Click: the key insight. Creating a Text value is not the same as drawing text; the framework decides how to measure, position and render the description.'),
                  ('CONNECT', 'Step 4, layout, explains something we skipped: why is NPay centred?'))))

# ================================================================== Part 5 (8-9)
divider(5, "Layout: place and size", "Parents propose, children choose", 'We never wrote positioning code, yet NPay is centred.', 'Move it.')
TL = """Text("NPay")
    .frame(maxWidth: .infinity, maxHeight: .infinity,
           alignment: .topLeading)"""
S.append(slide("Part 5 &middot; Why centred? (section 8)", "Centred by the layout, not by Text", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px;gap:16px;align-items:start">
        {code("Default", 'Text("NPay")', "font-size:15px")}
        {PHONE("img/hello.png", "Centred", 150)}
      </div>
      <div class="cols step" style="grid-template-columns:minmax(0,1fr) 150px;gap:16px;align-items:start">
        {code("Experiment", TL, "font-size:13px")}
        {PHONE("img/topleading.png", "Top leading", 150)}
      </div>
    </div>
    <div class="rule step" data-label="So" style="margin-top:10px">{ul("The <b>surrounding layout</b> decides position, not Text", "The safe area matters too; <code>.frame</code> comes in the layout lessons")}</div>
  </div>""", notes(('SAY', 'In this simple root layout, SwiftUI&rsquo;s hosting environment proposes the available space and places the text according to its layout behaviour, which here means centred. That does not mean every Text is centred in every parent; it depends on the surrounding layout.'),
                  ('SAY', 'Click: the experiment. Wrap the text in a frame as large as possible with top-leading alignment, and it moves to the top-left of the available area. Notice it sits below the status bar: that is the safe area.'),
                  ('SAY', 'Click: position comes from the layout around the view. We study .frame properly in the layout lessons.'),
                  ('CONNECT', 'Position is one half of layout. The other half is size.'))))

STEPS3 = [("frame", "Parent proposes", "a size"), ("code", "Text chooses", "its own size"), ("layout", "Parent places", "the child")]
P = []
for i, (ic, t, sub) in enumerate(STEPS3):
    x = i * 392
    P.append(tall(x, 0, 352, 112, ic, t, sub, str(i + 1)))
    if i < 2:
        P.append(wire(f'M{x + 356} 56H{x + 388}' + head(x + 388, 56, 'r')))
FACT = ["Font metrics", "Glyph advances", "Line breaks", "Language", "Proposed size"]
S.append(slide("Part 5 &middot; Measuring text (section 9)", "Parents propose, text chooses, parents place", f"""  <div class="body">
    {cues(3)}
    {svg('0 0 1136 112', 'The parent proposes a size, the text chooses its size, the parent places it', 'measure', P, 'max-height:140px')}
    <div class="gap-lg"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("Text measurement uses", ul(*FACT[:3]))}
      {card("&hellip; and", ul(*FACT[3:], "So text adapts to <b>device widths</b>"))}
    </div>
  </div>""", notes(('SAY', 'Text has an intrinsic content size under given constraints: "NPay" in a small font needs less space than "Welcome to NPay" in a large one. SwiftUI&rsquo;s layout runs in three moves. Click: the parent proposes a size. Click: the child, our Text, chooses its own size within that proposal. Click: the parent positions the child.'),
                  ('SAY', 'Click: behind the scenes, text measurement considers font metrics, glyph advances, line breaks, the language, and the proposed size. The text system finds a layout; SwiftUI positions the result. That is why text responds naturally to different device widths.'),
                  ('CONNECT', 'We measured it in the simulator.'))))

MEAS = """let line = "Welcome to NPay. Payments made simple."

Text("NPay")                          // .body
Text("NPay").font(.largeTitle)
Text(line).frame(width: 260).border(.gray)
Text(line).frame(width: 140).border(.gray)"""
S.append(slide("Part 5 &middot; Measured in the simulator (section 9)", "Same sentence, two proposals", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("MeasureView.swift (excerpt)", MEAS, "font-size:13px")}
        <div class="gap"></div>
        <div class="step">{console("Size each Text chose", ["\"NPay\", .body: 39.7 × 24.3 pt", "\"NPay\", .largeTitle: 77.3 × 48.7 pt", "proposed 260 wide: 221.0 × 50.3 pt", "proposed 140 wide: 140.0 × 76.3 pt"], 13)}</div></div>
      <div>{crop("img/measure.png", SIM, 360)}
        <div class="takeaway step" style="margin-top:12px">Narrower proposal &rarr; more lines &rarr; <b>taller</b> text.</div></div>
    </div>
  </div>""", notes(('SAY', 'In place of the text&rsquo;s browser slider, we ran the real thing. Four texts in a stack: NPay in the body font, NPay as largeTitle, and the sentence "Welcome to NPay. Payments made simple." offered 260 points and then 140 points of width. The grey borders show the frames.'),
                  ('SAY', 'Click: the sizes each Text chose, logged with onGeometryChange. A bigger font needs more room. Offered 260 points, the sentence took only 221: two lines, 50 points tall. Offered 140, it used all 140 and needed three lines, 76 points tall.'),
                  ('SAY', 'Click: a narrower proposal means more line breaks and more height. The parent proposes; the text chooses.'),
                  ('CONNECT', 'Now style it.'))))

# ================================================================== Part 6 (10-12)
divider(6, "Modifiers", "Styling returns new descriptions", 'Make NPay a large title, and look at what the modifier returns.', 'Start with .font.')
FONT = """Text("NPay")
    .font(.largeTitle)        // short form

Text("NPay")
    .font(Font.largeTitle)    // long form"""
S.append(slide("Part 6 &middot; Font styling (section 10)", "<code>.largeTitle</code> is inferred from context", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", FONT, "font-size:16px")}
        <div class="gap"></div>
        {card("Two words", ul("<code>.font()</code>: a SwiftUI <b>modifier</b>", "<code>.largeTitle</code>: a <b>semantic</b> font style"))}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        <div class="step">{card("Contextual type inference (Unit 01)", ul("<code>.font</code> expects a <code>Font</code>", "so <code>.largeTitle</code> means <code>Font.largeTitle</code>"))}</div>
        <div class="step">{card("Why semantic fonts", ul("<code>.body</code>, <code>.title</code>, <code>.largeTitle</code> follow platform typography", "and <b>Dynamic Type</b>: the user&rsquo;s chosen text size (Part 8)"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', '.font is a SwiftUI modifier. .largeTitle is a semantic font style. The long form is Font.largeTitle; both lines mean the same.'),
                  ('SAY', 'Click: why can we drop Font? Because the compiler knows .font expects a Font value, so .largeTitle is looked up on Font. That is contextual type inference from Unit 01, the same reason you can write .red where a Color is expected.'),
                  ('SAY', 'Click: why semantic styles instead of a point size? .body, .title and .largeTitle follow the platform&rsquo;s typography and Dynamic Type, which lets users choose their preferred text size for accessibility. We will see it working on the final code.'),
                  ('CONNECT', 'What does .font actually return?'))))

TYPES = """let original = Text("NPay")
let styled = original.font(.largeTitle)
let padded = original.padding()

print(type(of: original))
print(type(of: styled))
print(type(of: padded))"""
S.append(slide("Part 6 &middot; Modifier return types (section 11)", "Some modifiers keep Text; others wrap it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Experiment.swift", TYPES, "font-size:15px")}
        <p class="small muted" style="margin:8px 0 0">Run in a SwiftUI context: here, a view&rsquo;s <code>.task</code> in the simulator.</p></div>
      <div>
        <div class="step">{console("Simulator console", ["Text", "Text", "ModifiedContent&lt;Text, _PaddingLayout&gt;"], 15)}</div>
        <div class="gap"></div>
        <div class="step">{card("Why", ul("Text&rsquo;s own <code>.font</code> overload returns <b>Text</b>", "General View modifiers <b>wrap</b>: <code>ModifiedContent</code>", "Protocol extensions + generics + overloads"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'A temporary experiment. Take a Text, make a styled copy with .font and a padded copy with .padding, and print each type. It needs a SwiftUI context; we ran it in a view&rsquo;s task in the simulator. Predict first: what are the three types?'),
                  ('SAY', 'Click: the real console. original is Text. styled is also Text, because Text has its own .font overload that returns Text. padded is ModifiedContent of Text and a padding layout: a wrapper description around the original.'),
                  ('SAY', 'Click: not every modifier produces the same kind of type. Text-specific modifiers can keep Text; general View modifiers usually wrap. That is protocol extensions, generics and overload resolution working together, all from Unit 01. Names starting with an underscore are SwiftUI internals and can change.'),
                  ('CONNECT', 'If modifiers wrap, does the order of wrapping matter?'))))

A = """Text("NPay")
    .padding()
    .background(.yellow)"""
B = """Text("NPay")
    .background(.yellow)
    .padding()"""
S.append(slide("Part 6 &middot; Modifier order (section 12)", "Same modifiers, different order, different result", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr) 300px;gap:20px;align-items:start">
      <div>{code("A: padding, then background", A, "font-size:15px")}
        <div class="step" style="margin-top:12px">{card("A", ul("Background covers the <b>padded</b> area"))}</div></div>
      <div>{code("B: background, then padding", B, "font-size:15px")}
        <div class="step" style="margin-top:12px">{card("B", ul("Background covers the <b>text</b> only"))}</div></div>
      {crop("img/order.png", "A above, B below (.largeTitle)", 300, 700)}
    </div>
    <div class="rule step" data-label="Measured" style="margin-top:12px">{ul("Both take <b>109.3 × 80.7 pt</b>: same layout size, different structure", "Modifiers aren&rsquo;t decoration; each wraps the one before")}</div>
  </div>""", notes(('SAY', 'Two versions with the same two modifiers in a different order. We ran both, stacked, at largeTitle so they are easy to see: A on top, B below.'),
                  ('SAY', 'Click: in A, padding wraps the text first, then the background wraps the padded view, so yellow fills the padded area. Click: in B, the background wraps just the text, then padding adds space outside it, so the yellow is tight around the word.'),
                  ('SAY', 'Click: we measured both: each takes exactly the same space, 109.3 by 80.7 points. The layout size is the same; the structure, and so the result, differs. Modifiers are applied in sequence, and each one wraps the description before it. This is one of the most important ideas in SwiftUI.'),
                  ('CONNECT', 'NPay will also speak more than one language.'))))

# ================================================================== Part 7 (13)
divider(7, "Unicode and localization", "Text for every language", 'NPay may support many languages. What does Text do with them?', 'Three greetings.')
UNI = """Text("Welcome to NPay")
Text("வணக்கம்")
Text("नमस्ते")"""
S.append(slide("Part 7 &middot; Unicode (section 13)", "One visible letter is not one byte", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Greetings.swift", UNI, "font-size:17px")}
        <div class="gap"></div>
        {card("SwiftUI&rsquo;s text system handles", ul("Unicode text and <b>shaping</b>", "Line breaking and language rules"))}</div>
      <div>{crop("img/unicode.png", SIM, 400, 650)}
        <div class="step" style="margin-top:12px">{console("Counted in Swift", ["NPay: 4 characters, 4 scalars, 4 bytes", "வணக்கம்: 5 characters, 7 scalars, 21 bytes", "नमस्ते: 3 characters, 6 scalars, 18 bytes"], 13)}</div></div>
    </div>
  </div>""", notes(('SAY', 'English, Tamil and Hindi greetings. SwiftUI&rsquo;s text system supports Unicode, shaping, line breaking and language-specific layout, and the simulator draws all three correctly with no extra code.'),
                  ('SAY', 'Click: we counted each string in Swift. NPay is 4 characters, 4 Unicode scalars and 4 UTF-8 bytes. The Tamil greeting is 5 characters, 7 scalars and 21 bytes; the Hindi one 3 characters, 6 scalars and 18 bytes. A Swift Character is what a reader sees as one letter, and it can be several scalars and many bytes. So a visible glyph is not one byte, and not necessarily one scalar.'),
                  ('CONNECT', 'Showing another language is one thing. Translating is another.'))))

LOC = """Text("Welcome to NPay")            // a localization key
Text(verbatim: "Welcome to NPay")  // shown as written"""
S.append(slide("Part 7 &middot; Localization (section 13)", "<code>Text(\"…\")</code> looks it up; <code>verbatim</code> doesn&rsquo;t", f"""  <div class="body">
    {code("Localization.swift", LOC, "font-size:17px")}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {crop("img/l10n-en.png", "Device language: English", 440, 500)}
      <div class="step">{crop("img/l10n-ta.png", "Device language: Tamil (with a Tamil strings file)", 440, 500)}</div>
    </div>
    <div class="rule step" data-label="Later" style="margin-top:10px">{ul("Localization in depth when NPay becomes multilingual")}</div>
  </div>""", notes(('SAY', 'Text with a string literal treats it as a localization key, so it can participate in SwiftUI localization. Text(verbatim:) shows the string exactly as written.'),
                  ('SAY', 'With the device in English, both lines read "Welcome to NPay". Click: we added a Tamil strings file to the app, our own translation for this demo, and launched it in Tamil. The first line was looked up and translated; the verbatim line stayed in English.'),
                  ('SAY', 'Click: we study localization properly when we build NPay&rsquo;s multilingual interface.'),
                  ('CONNECT', 'Back to NPay&rsquo;s screen, for its final state today.'))))

# ================================================================== Part 8 (14)
divider(8, "Final NPay code", "Lesson 2.1&rsquo;s screen", 'Three modifiers on one Text.', 'The code.')
FINAL = """import SwiftUI

struct ContentView: View {

    var body: some View {
        Text("NPay")
            .font(.largeTitle)
            .bold()
            .foregroundStyle(.blue)
    }
}

#Preview {
    ContentView()
}"""
S.append(slide("Part 8 &middot; Final NPay code (section 14)", "NPay at the end of Lesson 2.1", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      {code("ContentView.swift", FINAL, "font-size:15px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {crop("img/final.png", "Default text size", 440, 400)}
        <div class="step">{crop("img/final-ax.png", "Settings: larger text (Accessibility XL)", 440, 400)}</div>
        <div class="step">{console("Measured in the simulator", ["Default: 82.7 × 48.7 pt", "Accessibility XL: 125.3 × 74.0 pt", "type(of: body): Text"], 13)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Keep the app in this state: largeTitle for semantic typography, bold, and a blue foreground style. Still one view, but now we understand its foundation. On the right, the real screen.'),
                  ('SAY', 'Click: we raised the simulator&rsquo;s text size to Accessibility Extra Large and relaunched. Same code, bigger title: that is Dynamic Type at work, because we used a semantic font.'),
                  ('SAY', 'Click: measured, the title grew from 82.7 by 48.7 points to 125.3 by 74. And type(of: body) is still plain Text: font, bold and foregroundStyle all have Text-specific overloads that return Text.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.1', (), [("code", "Text is a value", "a description, not pixels"),
                     ("layout", "Layout decides", "propose, choose, place"),
                     ("diff", "Modifiers wrap", "order changes the structure")],
         'Three things to remember. Text("NPay") is a value, a struct conforming to View, and body returns it as some View: a description, not pixels. Layout decides size and position: the parent proposes, the text chooses, the parent places. And modifiers return new descriptions, some keeping Text, most wrapping it, so their order changes the result.')

review_divider(11)
review([("code", "Choose one", "What does Text(\"NPay\") create?",
         "What does <code>Text(\"NPay\")</code> create?<br>A. A <code>UILabel</code> instance<br>B. A SwiftUI <code>Text</code> value<br>C. Pixels directly in a graphics buffer", "B",
         "A struct value describing UI content; SwiftUI lays out and renders it separately.",
         "Thinking SwiftUI views are UIKit objects or pixels.", "Some pick A.", None),
        ("layers", "Choose one", "Why can ContentView.body return Text?",
         "Why can <code>ContentView.body</code> return <code>Text</code>?<br>A. <code>Text</code> inherits from <code>ContentView</code><br>B. <code>Text</code> conforms to <code>View</code><br>C. <code>Text</code> is a special Swift keyword", "B",
         "<code>body</code> must return a View; <code>Text</code> conforms to View (an extension in the SDK interface).",
         "Thinking in class inheritance.", "Some pick A.", None),
        ("eye", "Choose one", "What does some View mean?",
         "What does <code>some View</code> mean?<br>A. Any different View type at run time<br>B. One underlying concrete type conforming to View<br>C. A dynamically typed object", "B",
         "An opaque type: one hidden concrete type per declaration. For ContentView it printed <code>Text</code>.",
         "Reading <code>some</code> as &ldquo;any&rdquo;.", "Some pick A.", None),
        ("frame", "Question", "Does evaluating body necessarily redraw the whole screen?",
         "Does evaluating <code>body</code> necessarily redraw the entire screen?", "No",
         "Evaluating body produces a description; layout and rendering are separate stages that the framework manages.",
         "Equating a new description with new pixels everywhere.", "Some say yes.", None),
        ("diff", "Choose one", "Why does .largeTitle work without Font.?",
         "Why does <code>.largeTitle</code> work without writing <code>Font.largeTitle</code>?<br>A. Run-time reflection<br>B. Contextual type inference<br>C. An implicit global variable", "B",
         "<code>.font</code> expects a <code>Font</code>, so the compiler looks <code>.largeTitle</code> up on <code>Font</code>.",
         "Thinking it is resolved while the app runs.", "Some pick A.", "Spaced review from Unit 01: type inference."),
        ("layout", "Choose one", "What does .padding() generally do?",
         "What does <code>.padding()</code> generally do?<br>A. Mutates the original <code>Text</code><br>B. Returns a padded view description<br>C. Adds spaces to the string", "B",
         "It returns a wrapper: the simulator printed <code>ModifiedContent&lt;Text, _PaddingLayout&gt;</code>.",
         "Thinking modifiers mutate the view.", "Some pick A.", None),
        ("diff", "Question", "Does modifier order affect layout?",
         "Does the order of modifiers affect the result?", "Yes",
         "Each modifier wraps the one before: padding then background colours the padded area; the reverse colours only the text.",
         "Treating modifiers as a set of style flags.", "Most say yes.", None),
        ("layout", "Choose one", "What influences Text measurement?",
         "What influences how <code>Text</code> is measured?<br>A. Only the number of characters<br>B. Font, content, proposed size and layout constraints<br>C. Only the screen resolution", "B",
         "The same sentence measured 221 &times; 50 pt when offered 260 pt, and 140 &times; 76 pt when offered 140 pt.",
         "Counting characters.", "Some pick A.", None),
        ("phone", "Question", "Does every Text value create a separate UILabel?",
         "Does every <code>Text</code> value create its own <code>UILabel</code>?", "Not guaranteed",
         "How SwiftUI renders text is its own implementation detail; a <code>Text</code> value is a description, not a UIKit view.",
         "Mapping SwiftUI views one-to-one onto UIKit views.", "Some say yes.", None),
        ("globe", "Choose one", "Which API displays text without localization lookup?",
         "Which API displays text without treating it as a localization key?<br>A. <code>Text(\"Welcome\")</code><br>B. <code>Text(verbatim: \"Welcome\")</code><br>C. <code>Text.localized()</code>", "B",
         "In Tamil, <code>Text(\"Welcome to NPay\")</code> was translated; the verbatim line stayed in English.",
         "Assuming every string literal is shown as written.", "Some pick A.", None),
        ("eye", "Predict the result", "padding(24) then background, or the reverse: which yellow is larger?",
         "Which version has the larger yellow background?<br><code>A: Text(\"NPay\").padding(24).background(.yellow)</code><br><code>B: Text(\"NPay\").background(.yellow).padding(24)</code>", "A",
         "In A the background wraps the padded view, so it is 24 pt bigger on every side; in B it wraps only the text, and the padding is clear space outside.",
         "Thinking both are the same because the modifiers are the same.", "Most say A; some say the same.", None)])

S.append(next_slide('2.1', [("2.2", "SwiftUI Image &amp; SF Symbols", "a payment icon above today&rsquo;s title"),
                            ("Later", "Layout lessons", "<code>.frame</code>, proposals and alignment in depth"),
                            ("Later", "Conditional views", "why <code>some View</code> needs one type"),
                            ("Later", "Localization", "NPay&rsquo;s multilingual interface")],
                    'Next lesson adds NPay&rsquo;s first image, a payment symbol, above today&rsquo;s title, without throwing this screen away. Three things we pointed at today come back later: .frame and layout, conditional views and some View, and localization.'))

LAB = """Button("Print types") {
    let original = Text("NPay")
    print(type(of: original))
    print(type(of: original.font(.largeTitle)))
    print(type(of: original.padding()))
}"""
S.append(lab_slide('2.1', "Investigate Text yourself", "Reproduce today&rsquo;s evidence in your own simulator.",
                   ["Build Section 2&rsquo;s <code>ContentView</code>; run with <b>⌘R</b> and in the canvas.",
                    "⌘-click <code>Text</code> &rarr; Jump to Definition: find the struct and its View conformance.",
                    "Add the top-leading <code>.frame</code>; predict, run, remove it.",
                    "Print the three <code>type(of:)</code> results from a button.",
                    "Swap <code>.padding()</code> and <code>.background(.yellow)</code>; predict first.",
                    "End in the Section 14 state; try a larger text size."],
                   "", 'Needs a Mac with Xcode and the NPay project. Expected, as in our simulator runs: NPay centred; the frame moves it top-leading below the status bar; the console prints Text, Text, ModifiedContent&lt;Text, _PaddingLayout&gt;; padding-then-background colours the padded area; with a larger text size (Settings > Accessibility > Display & Text Size > Larger Text, or the Canvas&rsquo;s Dynamic Type variants) the largeTitle grows. Ask for one sentence per result using the words value, layout and wrap.',
                   side=f'<div>{code("ContentView.swift", LAB, "font-size:14px")}<div class="gap"></div>{card("You hand in", ul("A screenshot per experiment", "Your three <code>type(of:)</code> lines, each explained"))}</div>'))

end_slide('2.1', 'SwiftUI Text:<br>From Source Code to Screen', 'Lesson 2.2 &mdash; SwiftUI Image &amp; SF Symbols',
          'You can now explain what Text("NPay") is, how the compiler finds it, why ContentView conforms to View, what some View hides, how SwiftUI sizes and places text, how modifiers wrap views and why their order matters, and how Text handles Unicode, localization and Dynamic Type.',
          'Next, Lesson 2.2: Image and SF Symbols. NPay gets a payment icon above its name, and we look at how symbols are resolved, why font modifiers affect them, and how image resources reach the screen.')

write_deck(OUT21, '2.1', 'SwiftUI Text', 'SwiftUI Text')
