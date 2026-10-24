"""Generates decks/unit-2/lesson-2.2/index.html from the Lesson 2.2 text (SwiftUI Image & SF Symbols).
The 12 sections are grouped into 7 Parts. Console output, system-log messages and screenshots come from
tools/sim2_2 (a scripted SwiftUI app with an asset catalog, run in the iOS Simulator); interface lines from the iOS 26.5 SDK."""
import html, os, re, sys
OUT22 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit2.py')).read())   # Unit 02 lesson list + shared helpers

title_slide('2.2', 'SwiftUI Image<br>&amp; SF Symbols',
            'How does the string <b>"creditcard.fill"</b> become a symbol on the iPhone screen?',
            'Lesson 2.1 took one Text from source code to the screen. Today we add exactly one new component, Image, and ask one question: how does the string "creditcard.fill" become a graphical symbol on the iPhone? We look at it at three levels: the Swift language, the SwiftUI framework, and iOS. As before, every screenshot and console line came from a small app we ran in the iOS Simulator.')
outcomes_slide('2.2', [("code", "What <code>Image(systemName:)</code> <b>creates</b>"),
                       ("globe", "Where <b>SF Symbols</b> come from, and when names are resolved"),
                       ("layout", "Why <code>.font()</code> <b>sizes</b> a symbol"),
                       ("eye", "How <code>.foregroundStyle(.blue)</code> is <b>inferred</b>"),
                       ("layers", "<b>Symbols</b> vs <b>asset images</b>"),
                       ("check", "Add the icon to NPay with a <code>VStack</code>")])
where_slide('2.2', 'Today: a payment icon', (),
            '2.1: <code>Text("NPay")</code>, from source code to pixels.',
            'One new component: <code>Image</code>, above the title.',
            'Last lesson we built NPay&rsquo;s title with Text and followed it all the way to the screen. Today NPay gets its first visual element, a payment icon, and we investigate Image the same way.',
            'Here is the requirement.')

# ================================================================== Part 1 (1)
divider(1, "The next requirement", "An icon above the title", 'NPay shows only its name. It needs a payment icon.', 'Before and after.')
S.append(slide("Part 1 &middot; NPay&rsquo;s next requirement (section 1)", "Add a payment icon above the title", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 190px 190px;gap:36px;align-items:center">
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("Requirement", ul("A payment <b>icon</b> above <b>NPay</b>", "Keep the Lesson 2.1 title"))}
        {card("Plan", ul("Investigate <code>Image</code> <b>alone</b> first", "Then combine with a simple <code>VStack</code>", "<code>VStack</code> internals: Lesson 2.3"))}
      </div>
      {PHONE("img/before.png", "Before: Lesson 2.1", 190)}
      <div class="step">{PHONE("img/final.png", "After: Milestone 2.2", 190)}</div>
    </div>
  </div>""", notes(('SAY', 'NPay&rsquo;s screen shows only its blue title from Lesson 2.1. The requirement: a payment icon above it, without throwing the title away.'),
                  ('SAY', 'Click: that is where we finish today. To keep the focus on Image, we first study the icon on its own, then combine it with the Text using a simple VStack. VStack&rsquo;s internals are Lesson 2.3.'),
                  ('CONNECT', 'First experiment: an Image on its own.'))))

# ================================================================== Part 2 (2-3)
divider(2, "A first Image", "A value that names a symbol", 'Replace the body with one Image.', 'Build it.')
FIRST = """var body: some View {
    Image(systemName: "creditcard.fill")
}"""
PARTS = [("<code>Image</code>", "struct defined in SwiftUI"), ("<code>systemName:</code>", "initializer argument label"),
         ("<code>\"creditcard.fill\"</code>", "SF Symbol <b>identifier</b>"), ("Result", "a SwiftUI <b>Image value</b>")]
S.append(slide("Part 2 &middot; First experiment (section 2)", "<code>Image(systemName:)</code> makes a value", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", FIRST, "font-size:17px")}
        <div class="gap"></div>
        {crop("img/symbol.png", SIM + " (default size)", 420)}</div>
      <div>{tbl(["Part", "Meaning"], PARTS, 'tbl')}
        <div class="gap"></div>
        <div class="rule step" data-label="Not a file">{ul("No image file is loaded from the project", "We are asking for a <b>system symbol</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Temporarily replace ContentView&rsquo;s body with one Image. Run the preview: a credit-card symbol appears. On the left, our simulator run. Notice how small it is: without any size, the symbol follows the default body text size, about 24 by 16 points. Hold that thought for Part 4.'),
                  ('SAY', 'Read the expression like Text in Lesson 2.1. Image is a struct defined in SwiftUI; systemName is the initializer&rsquo;s argument label; "creditcard.fill" is an SF Symbol identifier; the result is an Image value.'),
                  ('SAY', 'Click: Image here does not load an image file from your project. We are requesting a system symbol.'),
                  ('CONNECT', 'So where does creditcard.fill come from?'))))

S.append(slide("Part 2 &middot; SF Symbols (section 3)", "A system library of symbols", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{crop("img/library.png", "Real SF Symbols, " + SIM, 440)}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("SF Symbols", ul("Apple&rsquo;s library: <b>thousands</b> of symbols", "Designed to match system <b>typography</b>", "Browse them in Apple&rsquo;s <b>SF Symbols</b> app"))}
        <div class="rule step" data-label="A file path?">{ul("No: <code>\"creditcard.fill\"</code> is a symbol <b>name</b>", "The system resolves it to a symbol")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Apple provides a symbol library called SF Symbols: thousands of symbols designed to integrate with the system&rsquo;s typography. These six are the text&rsquo;s examples, rendered for real in the simulator, each at 44 points with its name underneath. You can browse every symbol in Apple&rsquo;s SF Symbols app.'),
                  ('SAY', 'Click: is "creditcard.fill" a file path? No. It is a symbol name, used to resolve a system-provided symbol.'),
                  ('CONNECT', 'When is that name resolved, and by whom?'))))

# ================================================================== Part 3 (4)
divider(3, "Resolved at run time", "From a name to an icon", 'The compiler does not turn "creditcard.fill" into pixels.', 'Trace the journey.')
PIPE = [("code", "Image value", "stores the name \"creditcard.fill\""),
        ("eye", "body evaluated", "SwiftUI receives the description"),
        ("globe", "Symbol lookup", "the name is resolved in the system symbol set"),
        ("gear", "Configuration", "font size and weight, foreground style"),
        ("layout", "Layout", "SwiftUI determines the symbol&rsquo;s size and placement"),
        ("frame", "Rendering", "the vector symbol is drawn at that size")]
P = [box(0, i * 58, 680, 48, t, sub, str(i + 1) if i < 5 else '6+', '', ic) for i, (ic, t, sub) in enumerate(PIPE)]
S.append(slide("Part 3 &middot; How the symbol is resolved (section 4) &middot; conceptual", "From symbol name to visible icon", f"""  <div class="body">
    {cues(6)}
    <div class="cols" style="grid-template-columns:minmax(0,1.4fr) minmax(0,.6fr);gap:28px;align-items:center">
      {svg('0 0 680 338', 'Image value, body evaluated, symbol lookup, configuration, layout, rendering', 'pipe', P, 'max-height:380px')}
      <div class="rule step" data-label="Compile time vs run time">{ul("The compiler sees only a <code>String</code>", "The <b>platform</b> resolves the name at run time")}</div>
    </div>
  </div>""", notes(('SAY', 'A conceptual pipeline; Apple does not publish exactly how symbol lookup and rendering work inside. Click: our code creates an Image value that stores the name. Click: SwiftUI evaluates body and receives that description. Click: at run time the name is looked up in the system symbol set.'),
                  ('SAY', 'Click: the symbol is configured from its environment: font size and weight, foreground style. Click: layout, the stage the text shows: SwiftUI determines the symbol&rsquo;s size and placement. Click: rendering draws the vector symbol at that size.'),
                  ('SAY', 'Click: the key point. Swift&rsquo;s compiler never turns "creditcard.fill" into pixels; it sees only a String. The platform resolves the name at run time. So what happens with a name that does not exist?'),
                  ('CONNECT', 'We tried it.'))))

BAD = """Image(systemName: "creditcard.fil")   // typo"""
S.append(slide("Part 3 &middot; An unsupported name (section 4)", "It compiles, and shows nothing", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:28px;align-items:start">
      <div>{code("ContentView.swift", BAD, "font-size:17px")}
        <div class="gap"></div>
        {console("Interface, iOS 26.5 SDK", ["public init(systemName: String)"], 14)}
        <div class="gap"></div>
        <div class="step">{console("Xcode console (system log)", ["No symbol named 'creditcard.fil' found in system symbol set"], 14)}</div>
        <div class="gap"></div>
        <div class="step">{console("Size SwiftUI gave it", ["creditcard.fil: 0.0 × 0.0 pt"], 14)}</div></div>
      {PHONE("img/invalid.png", "Built and ran: blank", 190)}
    </div>
  </div>""", notes(('SAY', 'One missing letter: creditcard.fil. The initializer takes a plain String, as the SDK interface shows, so the compiler accepts any string. It built without a warning and the app ran: a blank screen.'),
                  ('SAY', 'Click: the only signal is at run time. SwiftUI logged "No symbol named creditcard.fil found in system symbol set". It appears in Xcode&rsquo;s console, so keep an eye on it.'),
                  ('SAY', 'Click: we also measured the view: zero by zero points. The Image exists as a value, but there is nothing to draw. That is why a typo in a symbol name is not caught at compile time.'),
                  ('CONNECT', 'Next: making the symbol bigger, with a font.'))))

# ================================================================== Part 4 (5-6)
divider(4, "Sizing with .font", "Symbols follow typography", 'Why does an Image accept a font modifier? Fonts are for text.', 'Three sizes.')
SIZE = """Image(systemName: "creditcard.fill")
    .font(.system(size: 64))"""
S.append(slide("Part 4 &middot; Why .font() sizes an image (section 5)", "A symbol takes its size from the font", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", SIZE, "font-size:17px")}
        <div class="gap"></div>
        {card("SF Symbols are typographic", ul("They <b>scale</b> and <b>align</b> with text", "They follow font <b>size</b> and <b>weight</b>"))}</div>
      <div>{crop("img/sizes.png", "Font size 24, 64 and 100", 440)}
        <div class="step" style="margin-top:12px">{console("Measured in the simulator", ["size 24: 33.7 × 23.7 pt", "size 64: 89.7 × 62.3 pt", "size 100: 139.7 × 97.7 pt"], 14)}</div></div>
    </div>
  </div>""", notes(('SAY', 'Add .font(.system(size: 64)). Why does an Image accept a font? Because SF Symbols are designed to work with typography: they scale and align with text, and their appearance responds to font size and weight.'),
                  ('SAY', 'In place of the text&rsquo;s slider, the real thing: the same symbol at font sizes 24, 64 and 100. Click: measured, the symbol grows with the font: about 34 by 24 points at 24, 90 by 62 at 64, 140 by 98 at 100. The width is larger than the font size because a card is wider than it is tall.'),
                  ('CONNECT', 'Why not just use a small picture and stretch it?'))))

S.append(slide("Part 4 &middot; Symbols stay sharp (section 5)", "Scalable symbol vs enlarged bitmap", f"""  <div class="body">
    {crop("img/sharp.png", "Left: symbol at size 100. Right: a 23 × 16 pixel bitmap of it, enlarged to the same width", 760)}
    <div class="gap"></div>
    <div class="cols step" style="{TWO};gap:24px">
      {card("System symbol", ul("Designed for <b>scalable</b> rendering", "Sharp at every size"))}
      {card("Small raster image", ul("Fixed pixels", "Enlarged too far: <b>blurry</b>"))}
    </div>
  </div>""", notes(('SAY', 'On the left, the symbol drawn at font size 100. On the right, we rendered the same symbol into a small bitmap, 23 by 16 pixels, and stretched that bitmap to the same width.'),
                  ('SAY', 'Click: the symbol stays sharp because system symbols are designed for scalable rendering. The bitmap has only the pixels it was made with; enlarged that far, it goes blurry. That is the case for using symbols for interface icons.'),
                  ('CONNECT', 'Now look closely at .system(size: 64).'))))

INF = """.font(.system(size: 64))         // short form
.font(Font.system(size: 64))     // long form"""
S.append(slide("Part 4 &middot; Where .system(size: 64) comes from (section 6)", "<code>.system(size:)</code> is inferred from context", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("Inference.swift", INF, "font-size:16px")}
        <div class="gap"></div>
        {card("Contextual type inference", ul("<code>.font()</code> expects a <code>Font</code>", "so <code>.system(size: 64)</code> is <code>Font.system(size: 64)</code>", "Same feature as <code>.largeTitle</code> in 2.1"))}</div>
      <div>
        <div class="step">{console("type(of:) in the simulator", ["Image(…).font(…):", "ModifiedContent&lt;Image,", "  _EnvironmentKeyWritingModifier&lt;Optional&lt;Font&gt;&gt;&gt;", "", "Text(…).font(…):", "Text"], 13)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="So">{ul("On an Image, <code>.font</code> <b>writes the environment</b>", "The symbol reads that font")}</div></div>
    </div>
  </div>""", notes(('SAY', '.font expects a Font value, so the compiler looks .system(size: 64) up on Font: the long form is Font.system(size: 64). Contextual type inference again, the same feature as .largeTitle in Lesson 2.1.'),
                  ('SAY', 'Click: but the modifier itself is different. We printed the types. On Text, .font returned plain Text, as in 2.1. On Image it returned ModifiedContent of Image and an environment-writing modifier for an optional Font. The underscore name is SwiftUI internal, but the shape is clear.'),
                  ('SAY', 'Click: on an Image, .font puts a font into the environment, and the symbol reads it from there to choose its size. That is the mechanism behind "symbols follow typography".'),
                  ('CONNECT', 'Size done. Now colour.'))))

# ================================================================== Part 5 (7)
divider(5, "Foreground style", "Colour without a new image", 'Make the icon blue.', 'Add one modifier.')
FG = """Image(systemName: "creditcard.fill")
    .font(.system(size: 64))
    .foregroundStyle(.blue)    // or Color.blue"""
SHAPE = """extension ShapeStyle where Self == Color {
    static var blue: Color { get }
}"""
S.append(slide("Part 5 &middot; Apply a foreground style (section 7)", "One symbol, any colour", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{code("ContentView.swift", FG, "font-size:15px")}
        <div class="gap"></div>
        {crop("img/colors.png", ".blue, .green, .red", 440)}</div>
      <div style="display:flex;flex-direction:column;gap:14px">
        {card("No new resource", ul("The <b>same</b> symbol, three styles"))}
        <div class="step">{code("Interface excerpt, iOS 26.5 SDK", SHAPE, "font-size:14px")}</div>
        <div class="step">{card("How <code>.blue</code> is found", ul("<code>foregroundStyle</code> expects some <code>ShapeStyle</code>", "This extension supplies <code>.blue</code> as a <code>Color</code>"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'foregroundStyle applies a foreground style to the symbol. Instead of the text&rsquo;s colour buttons, the simulator: the same symbol with .blue, .green and .red. The foreground style changes how the symbol is presented without needing a different image resource.'),
                  ('SAY', 'Click: .blue is shorthand, resolved by Swift&rsquo;s type system; Color.blue is the long form. Here is how. foregroundStyle is generic: it expects some ShapeStyle. The SDK has an extension on ShapeStyle, only where Self is Color, that declares static var blue.'),
                  ('SAY', 'Click: so when the compiler needs a ShapeStyle and sees .blue, it finds this member and gets a Color. Protocol extensions with a where clause, from Unit 01.'),
                  ('CONNECT', 'Image now behaves a lot like Text. How alike are they?'))))

# ================================================================== Part 6 (8-9)
divider(6, "Image, Text and assets", "Two Views, two kinds of image", 'Text and Image share modifiers. And Image("NPayLogo") is a different thing again.', 'Compare the types.')
P = [box(140, 0, 300, 56, 'View protocol', 'shared modifiers', None, 'lit', 'layers'),
     wire('M140 150V100H290V62' + head(290, 62, 'u'), None, 'dash'), wire('M440 150V100H290', None, 'dash'),
     box(0, 150, 280, 56, 'Text', 'textual content', None, '', 'file'), box(300, 150, 280, 56, 'Image', 'graphical content', None, '', 'frame')]
S.append(slide("Part 6 &middot; Image versus Text (section 8)", "Both conform to View", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:28px;align-items:start">
      <div>{svg('0 0 580 206', 'Text and Image both conform to the View protocol', 'iv', P, 'max-height:220px')}
        <div class="gap"></div>
        {card("So both accept", ul("<code>.padding()</code>, <code>.foregroundStyle()</code>, &hellip;"))}</div>
      <div>{console("Interface, iOS 26.5 SDK", ["@frozen public struct Image : Equatable, Sendable", "extension Image : View"], 13)}
        <div class="gap"></div>
        <div class="step">{console("type(of:) in the simulator", ["Image(…).foregroundStyle(.blue):", "ModifiedContent&lt;Image, _ForegroundStyleModifier&lt;Color&gt;&gt;"], 13)}</div>
        <div class="gap"></div>
        <div class="rule step" data-label="Difference">{ul("Text has its own overloads that keep <b>Text</b>", "Image uses the general View modifiers: <b>wrapped</b>")}</div></div>
    </div>
  </div>""", notes(('SAY', 'Two SwiftUI types now: Text and Image. Both conform to View, Text for textual content and Image for graphical content. That is why both support common modifiers like padding and foregroundStyle: those are View modifiers.'),
                  ('SAY', 'The SDK declares Image exactly like Text: a frozen struct, Equatable and Sendable, with the View conformance in an extension.'),
                  ('SAY', 'Click: one difference shows in the types. Image&rsquo;s foregroundStyle returned ModifiedContent of Image and a foreground-style modifier. Click: Text has its own font, bold and foregroundStyle overloads that keep it Text, as we measured in 2.1; Image uses the general View modifiers, which wrap it.'),
                  ('CONNECT', 'Image has a second form: images from your own app.'))))

FEAT = [("Source", "system symbol library", "app-provided resource"), ("Typical use", "standard interface icons", "branding, custom artwork"),
        ("Scaling", "designed for scalable symbols", "depends on resource and configuration"), ("Styling", "symbol-specific modes", "template or original rendering"),
        ("Availability", "depends on OS and symbol version", "bundled with the app")]
S.append(slide("Part 6 &middot; System images and asset images (section 9)", "<code>systemName:</code> or an asset name", f"""  <div class="body">
    {code("Two forms", 'Image(systemName: "creditcard.fill")   // SF Symbol\nImage("NPayLogo")                      // Assets.xcassets', "font-size:16px")}
    <div class="gap"></div>
    {tbl(["Feature", "SF Symbol", "Asset image"], FEAT)}
    <div class="rule step" data-label="Asset images" style="margin-top:12px">{ul("Asset catalog <b>compiled</b> at build time", "Looked up in the <b>app&rsquo;s resources</b> at run time")}</div>
  </div>""", notes(('SAY', 'Two common forms. Image(systemName:) references an SF Symbol. Image("NPayLogo"), with no label, looks for an image resource named NPayLogo, usually in Assets.xcassets.'),
                  ('SAY', 'The table: symbols come from the system library, assets from your app. Symbols suit standard interface icons, assets suit branding and custom artwork. Symbols are designed to scale; an asset depends on its resource type and configuration. Symbols have symbol-specific styling modes; assets use template or original rendering. And symbol availability depends on the OS and symbol version, while assets ship inside your app.'),
                  ('SAY', 'Click: an asset named NPayLogo is processed by Xcode&rsquo;s asset catalog tools during the build, and at run time SwiftUI resolves it through the app&rsquo;s resources. A different path from resolving an SF Symbol.'),
                  ('CONNECT', 'We built an app with a real asset catalog to see the difference.'))))

ASSETS = """Image("NPayLogo")                    // asset
Image(systemName: "NPayLogo")        // symbol?
Image("creditcard.fill")             // asset?"""
S.append(slide("Part 6 &middot; Two lookups, observed (section 9)", "Same string, different place to look", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) minmax(0,.7fr);gap:28px;align-items:start">
      <div>{code("AssetsView.swift", ASSETS, "font-size:15px")}
        <div class="gap"></div>
        <div class="step">{console("Size SwiftUI gave each", ["Image(\"NPayLogo\"): 120.0 × 120.0 pt", "Image(systemName: \"NPayLogo\"): 0.0 × 0.0 pt", "Image(\"creditcard.fill\"): 0.0 × 0.0 pt"], 13)}</div>
        <div class="gap"></div>
        <div class="step">{console("Xcode console (system log)", ["No symbol named 'NPayLogo' found in system symbol set", "No image named 'creditcard.fill' found in asset catalog"], 13)}</div></div>
      {crop("img/assets.png", "Only the asset appears", 300)}
    </div>
  </div>""", notes(('SAY', 'Our test app has an asset catalog with one image, NPayLogo, a navy square with an N that we drew for this demo. Three Images: the asset by name, the same name as a system symbol, and a symbol name looked up as an asset.'),
                  ('SAY', 'Click: only the first one has a size, 120 by 120 points: a 360-pixel image marked as 3x. The other two are zero by zero. Click: and the log says why: no symbol named NPayLogo in the system symbol set, and no image named creditcard.fill in the app&rsquo;s asset catalog.'),
                  ('SAY', 'So Image("NPayLogo") and Image(systemName: "NPayLogo") are not the same: the label decides where SwiftUI looks.'),
                  ('CONNECT', 'Back to NPay: put the icon on the screen.'))))

# ================================================================== Part 7 (10)
divider(7, "NPay increment", "Icon and title together", 'Keep the Lesson 2.1 title; add the symbol above it.', 'The code.')
FINAL = """import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "creditcard.fill")
                .font(.system(size: 64))
                .foregroundStyle(.blue)
            Text("NPay")
                .font(.largeTitle)
                .bold()
                .foregroundStyle(.blue)
        }
    }
}

#Preview {
    ContentView()
}"""
S.append(slide("Part 7 &middot; Combine Image and Text (section 10)", "Milestone 2.2: title with payment symbol", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.25fr) minmax(0,.75fr);gap:28px;align-items:start">
      <div>{code("ContentView.swift", FINAL, "font-size:14px")}</div>
      <div>{PHONE("img/final.png", "Milestone 2.2", 150)}
        <div class="step" style="margin-top:10px">{card("VStack: a container today", ul("Its internals: <b>Lesson 2.3</b>"))}</div></div>
    </div>
  </div>""", notes(('SAY', 'The NPay increment. The Lesson 2.1 title stays exactly as it was; the symbol goes above it, 64 points and blue, and a VStack with 20 points of spacing holds the two. On the right, the real screen: Milestone 2.2.'),
                  ('SAY', 'Click: VStack is only a container for now. Its initializer, @ViewBuilder, the trailing closure, its generic content type and its layout are next lesson. As a teaser: we printed this body&rsquo;s type and got VStack of TupleView of the modified Image and Text. Lesson 2.3 explains every part of that.'),
                  ('CONNECT', 'Pull the lesson together.'))))

# ================================================================== wrap-up
recap_u1('2.2', (), [("globe", "Names resolve at run time", "the compiler sees a String"),
                     ("layout", "Symbols follow the font", "size and weight from .font"),
                     ("layers", "Symbol or asset", "systemName: decides where to look")],
         'Three things to remember. A symbol name is just a String to the compiler; the platform resolves it at run time, so a typo builds and shows nothing. Symbols are typographic: .font writes the environment and the symbol takes its size and weight from it, staying sharp at any size. And Image(systemName:) looks in the system symbol set, while Image("name") looks in your app&rsquo;s assets.')

review_divider(7)
review([("code", "Choose one", "What is Image(systemName:) creating?",
         "What is <code>Image(systemName: \"creditcard.fill\")</code> creating?<br>A. A SwiftUI <code>Image</code> value<br>B. A <code>UIImageView</code> instance<br>C. A bitmap file", "A",
         "A value describing a symbol; SwiftUI resolves and draws it later.",
         "Thinking SwiftUI views are UIKit views or files.", "Some pick B.", None),
        ("chip", "Question", "Does the Swift compiler generate the symbol's pixels?",
         "Does the Swift compiler generate the symbol&rsquo;s pixels?", "No",
         "The compiler sees only a <code>String</code>; the platform resolves and renders the symbol at run time.",
         "Assuming the name is checked and drawn at build time.", "Some say yes.", None),
        ("layout", "Choose one", "Why does .font() influence SF Symbol size?",
         "Why does <code>.font()</code> change an SF Symbol&rsquo;s size?<br>A. Symbols integrate with typography<br>B. It modifies the source PNG", "A",
         "On an Image, <code>.font</code> writes the font into the environment; the symbol reads it.",
         "Thinking symbols are bitmap files.", "Some pick B.", None),
        ("globe", "Question", "Does every valid String name an available SF Symbol?",
         "Does every valid <code>String</code> name an available SF Symbol?", "No",
         "<code>\"creditcard.fil\"</code> compiled, ran, measured 0 &times; 0 pt and logged &ldquo;No symbol named&hellip;&rdquo;.",
         "Trusting that it compiled.", "Some say yes.", None),
        ("layers", "Question", "Is Image(\"NPayLogo\") the same as Image(systemName: \"NPayLogo\")?",
         "Does <code>Image(\"NPayLogo\")</code> mean the same as <code>Image(systemName: \"NPayLogo\")</code>?", "No",
         "The first looks in the app&rsquo;s asset catalog (120 &times; 120 pt logo); the second in the system symbol set (nothing found).",
         "Ignoring the argument label.", "Some say yes.", None),
        ("diff", "Predict the output", "What does type(of:) print for an Image with .font?",
         "What does <code>type(of:)</code> print for this value?<br><code>Image(systemName: \"creditcard.fill\")</code><br><code>    .font(.system(size: 64))</code><br>A. <code>Image</code><br>B. <code>Font</code><br>C. <code>ModifiedContent&lt;Image, &hellip;&gt;</code>", "C",
         "Image has no font overload of its own: the general View modifier wraps it (an environment-writing modifier).",
         "Expecting Image to stay Image, as Text does.", "Some pick A.", None),
        ("eye", "Predict the output", "What does type(of:) print for Text with .font?",
         "And this?<br><code>print(type(of: Text(\"NPay\").font(.largeTitle)))</code><br>A. <code>Text</code><br>B. <code>ModifiedContent&lt;Text, &hellip;&gt;</code><br>C. <code>Font</code>", "A",
         "Text has its own <code>.font</code> overload that returns <code>Text</code>; printed in both lessons&rsquo; runs.",
         "Assuming every modifier wraps.", "Some pick B.", "Spaced review from Lesson 2.1.")])

S.append(next_slide('2.2', [("2.3", "VStack &amp; @ViewBuilder", "the container we used today: trailing closure, <code>VStack&lt;Content&gt;</code>, vertical layout")],
                    'Next lesson opens up the VStack we used today: how SwiftUI accepts several child views through a trailing closure, builds a generic VStack value with @ViewBuilder, and arranges the children vertically.'))

S.append(lab_slide('2.2', "Your Xcode investigation", "Try each change in your NPay project. Predict first.",
                   ["Change <code>\"creditcard.fill\"</code> to <code>\"house.fill\"</code>.",
                    "Change the size from 64 to 24, then 100.",
                    "Change <code>.blue</code> to <code>.green</code>.",
                    "Try an invalid symbol name; read Xcode&rsquo;s console.",
                    "⌘-click <code>Image</code> to read its public API."],
                   "", 'Expected, as in our simulator runs: house.fill swaps the symbol; 24 and 100 give roughly 34 x 24 and 140 x 98 points; .green recolours without a new resource; an invalid name builds, shows nothing and logs "No symbol named ... found in system symbol set"; Jump to Definition shows the struct, init(systemName: String) and init(_ name: String, bundle:). Ask for one sentence per result.',
                   side=f'<div>{card("You hand in", ul("A screenshot per change", "The console line for the invalid name", "Two <code>Image</code> initializers from the interface"))}</div>'))

end_slide('2.2', 'SwiftUI Image<br>&amp; SF Symbols', 'Lesson 2.3 &mdash; VStack &amp; @ViewBuilder',
          'You can now explain what Image(systemName:) creates, why a symbol name is resolved at run time and fails silently, why .font sizes a symbol and keeps it sharp, how .blue is found, how symbols differ from asset images, and you have NPay&rsquo;s title with its payment symbol.',
          'Next, Lesson 2.3: VStack and @ViewBuilder. How SwiftUI accepts several child views through a trailing closure, builds a generic VStack&lt;Content&gt; value, and arranges the children vertically.')

write_deck(OUT22, '2.2', 'SwiftUI Image &amp; SF Symbols', 'SwiftUI Image &amp; SF Symbols')
