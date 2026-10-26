"""Generates decks/unit-3/lesson-3.7/index.html from the Lesson 3.7 text (Reusable SwiftUI Components & NPay Design
System). The text came in two pieces (Sections 1-14, cut off; "Part 2" Sections 14-22), grouped into 8 Parts.
Evidence comes from tools/sim3_7 (component catalog and integrated app in light, dark, a large text size and with
changed tokens; inferred generic types; Dynamic Type heights; _printChanges); the integration is authored."""
import html, os, re, sys
OUT37 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers
TOP = lambda src_, cap, w, h: shot(src_, cap, w, h)   # a phone screenshot cut to its top part

title_slide('3.7', 'Reusable Components &amp;<br>NPay Design System',
            'Tokens, components, screens. Change <b>one</b> colour token and every NPay button and card follows.',
            'Lesson 3.6 added motion. NPay now has several screens, and the same styling is repeated on all of them. Today we build the foundation of an NPay design system: design tokens, reusable components built on generics and @ViewBuilder, a custom modifier, and the rules for what a component must not do. We ran the components in light and dark mode, at a large text size and with changed tokens, and printed the types Swift infers for them.')
outcomes_slide('3.7', [("layers", "Organise a design system: <b>tokens</b>, components, screens"),
                       ("code", "Build components that take an <b>action</b> and keep their styling"),
                       ("diff", "Use generics and <code>@ViewBuilder</code> for any content"),
                       ("gear", "Choose: reusable <b>view</b> or <b>modifier</b>"),
                       ("eye", "Make the system adapt: Dynamic Type, dark mode, disabled"),
                       ("shield", "Keep business logic <b>out</b> of components")])
where_slide('3.7', 'Today: one visual language', (),
            '3.6: animations for the balance, insertions and success.',
            'NPayTheme, NPayButton, NPayCard, NPaySectionHeader, integrated.',
            'Lesson 3.6 finished motion. Today NPay gets a design system. Next lesson: adaptive layouts and GeometryReader.',
            'The problem.')

# ================================================================== Part 1 (intro, 1)
divider(1, "The milestone", "Stop repeating styling", 'Same padding, same background, on every screen.', 'The problem.')
REP = """.padding(16)
.background(
    Color.blue.opacity(0.08),
    in: RoundedRectangle(cornerRadius: 16)
)

.buttonStyle(.borderedProminent)"""
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "Same app, one visual language", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Repeated on every screen", REP, "font-size:13.5px")}
        <div class="step">{card("The question", ul("Consistent, reusable UI", "Without losing SwiftUI&rsquo;s declarative style"))}</div>
        <div class="rule step" data-label="Not changing">{ul("Business logic: the same", "Only the <b>visual language</b> becomes shared")}</div>
      </div>
      {PHONE("../lesson-3.3/img/home.png", "Before: Home since 3.3", 150)}
      <div class="step">{PHONE("img/home.png", "After: 3.7", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'NPay has grown to several screens, and styling is repeated everywhere: the same padding and tinted rounded background, the same bordered-prominent buttons. It works, but as NPay grows, repeated styling becomes hard to maintain: change the brand colour and you hunt through every file.'),
                  ('SAY', 'Click: the engineering question: how do professional iOS apps create consistent, reusable UI without giving up SwiftUI&rsquo;s declarative architecture? Click: and what does not change: business logic. We are creating a reusable visual language.'),
                  ('SAY', 'On the right, Home before, as it has looked since 3.3. Click: after today: a token-coloured balance card, one branded Send Money button, and the recent transactions in a card with a View All header.'),
                  ('CONNECT', 'What is a design system?'))))

# ================================================================== Part 2 (2-4)
divider(2, "Tokens", "Shared design decisions", 'Colours, spacing and radii as plain Swift constants.', 'The three layers.')
P = [box(0, 0, 700, 60, 'Design tokens', 'colours · spacing · typography · corner radii', None, '', 'grid'), wire('M350 62V78' + head(350, 78, 'd')),
     box(0, 82, 700, 60, 'Reusable components', 'NPayButton · NPayCard · NPaySectionHeader', None, 'lit', 'layers'), wire('M350 144V160' + head(350, 160, 'd')),
     box(0, 164, 700, 60, 'Feature screens', 'Home · Payments · History · Profile', None, '', 'phone')]
S.append(slide("Part 2 &middot; What exactly is a design system? (section 2)", "Tokens define, components apply, screens assemble", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {svg('0 0 700 224', 'Design tokens, reusable components, feature screens', 'ds', P, 'max-height:260px')}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("A design system", ul("Shared design decisions", "Reusable UI components"))}
        <div class="step">{card("Why layers", ul("Tokens: the shared visual rules", "Components apply them; screens assemble components", "No screen invents its own look"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A design system is a collection of shared design decisions and reusable UI components. For NPay, three layers: design tokens, the colours, spacing, typography and corner radii; reusable components, NPayButton, NPayCard, NPaySectionHeader; and the feature screens, Home, Payments, History, Profile.'),
                  ('SAY', 'Click: why separate them? The tokens define the shared visual rules; components apply those rules; screens assemble the components. That prevents every screen from independently inventing its own appearance.'),
                  ('CONNECT', 'The first layer: tokens.'))))

TH = """enum NPayTheme {
    enum Colors {
        static let primary = Color(red: 0.10, green: 0.34,
                                   blue: 0.65)
        static let success = Color.green
        static let cardBackground = Color.blue.opacity(0.06)
    }
    enum Spacing {
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
    }
    enum Radius {
        static let small: CGFloat = 10
        static let card: CGFloat = 18
    }
}

NPayTheme.Colors.primary
NPayTheme.Spacing.medium
NPayTheme.Radius.card"""
S.append(slide("Part 2 &middot; Design tokens (section 3)", "Enums as namespaces: no instance, just constants", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("DesignSystem/NPayTheme.swift", TH, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What this Swift is", ul("An <code>enum</code> with <code>static</code> properties", "Nested enums group colours, spacing, radii", "Never instantiated"))}
        <div class="step">{card("Unit 1", ul("Ordinary namespacing with enums and static members", "No SwiftUI mechanism needed to define tokens"))}</div>
        <div class="step">{card("Why an enum", ul("No cases: it <b>cannot</b> be instantiated by mistake"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPayTheme.swift: an enum with nested enums, Colors, Spacing and Radius, each with static properties: a primary colour, success and card-background colours; small, medium and large spacing; a small and a card radius. We never create an NPayTheme; we write NPayTheme.Colors.primary, NPayTheme.Spacing.medium, NPayTheme.Radius.card.'),
                  ('SAY', 'Click: connect to Unit 1: this is ordinary Swift namespace organisation with enums and static members. No special SwiftUI mechanism is involved in defining the tokens. Click: why an enum rather than a struct? An enum with no cases has no values, so nobody can create one by mistake: it can only be a namespace.'),
                  ('CONNECT', 'Why not just write .blue?'))))

S.append(slide("Part 2 &middot; Why not hardcode colours everywhere? (section 4, experiments 1&ndash;2)", "Change two tokens, rebuild: everything follows", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px 150px 150px;gap:14px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Before / after", ".foregroundStyle(.blue)\\n.foregroundStyle(NPayTheme.Colors.primary)".replace(chr(92) + "n", chr(10)), "font-size:12.5px")}
        <div class="step">{card("Experiment build", ul("<code>primary</code> &rarr; a teal", "<code>Radius.card</code> 18 &rarr; 4", "No component or screen edited"))}</div>
      </div>
      {TOP("img/catalog.png", "Catalog", 150, 200)}
      <div class="step">{TOP("img/catalog_alt.png", "Changed tokens", 150, 200)}</div>
      {PHONE("img/home.png", "Home", 150)}
      <div class="step">{PHONE("img/home_alt.png", "Changed tokens", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'Hardcoding .blue works, until NPay&rsquo;s brand colour changes and there are hundreds of them. With a token, styling references one shared value.'),
                  ('SAY', 'Click: the text&rsquo;s experiments 1 and 2, done as one rebuild: the primary colour changed to a teal and the card radius from 18 to 4, and nothing else. Click: the component catalog: both buttons and the "Fixed token" text changed colour. Click: Home: the balance card, Send Money and the transactions card all follow; the cards are now nearly square.'),
                  ('SAY', 'The text&rsquo;s point: tokens are not just convenience; they are an interface contract across teams and features. And for production, colour assets and semantic colours are often better than fixed RGB values; we test that in Part 6.'),
                  ('CONNECT', 'The second layer: components.'))))

# ================================================================== Part 3 (5, 6, 17, 18)
divider(3, "NPayButton", "Styling inside, action outside", 'The first reusable component.', 'Version 1.')
B1 = """struct NPayButton: View {
    let title: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.headline)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 14)
        }
        .buttonStyle(.plain)
        .foregroundStyle(.white)
        .background(NPayTheme.Colors.primary,
                    in: RoundedRectangle(
                        cornerRadius: NPayTheme.Radius.small))
    }
}

NPayButton(title: "Send Money") {
    print("Send tapped")
}"""
P = [box(0, i * 50, 430, 42, t, sub, None, 'lit' if i == 1 else '', ic) for i, (ic, t, sub) in enumerate([
    ("phone", "Feature screen", "creates NPayButton(title, action)"), ("layers", "NPayButton", "a reusable View struct"), ("tap", "Button", "the native interactive control"),
    ("frame", "Text + modifiers", "label, padding, colours, shape"), ("gear", "SwiftUI runtime", "layout, rendering, interaction")])]
S.append(slide("Part 3 &middot; Our first reusable component (sections 5&ndash;6)", "A value describing a branded button", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.95fr);gap:24px;align-items:start">
      {code("DesignSystem/NPayButton.swift (v1)", B1, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Reusable", ul("Styling stays <b>inside</b>", "The caller supplies the <b>action</b>: 2.7&rsquo;s closures"))}
        <div class="step">{svg('0 0 430 242', 'Feature screen, NPayButton, Button, Text and modifiers, SwiftUI runtime', 'cmp', P, 'max-height:220px')}
          <p class="small muted" style="margin:6px 0 0">A view description, not necessarily a UIKit object.</p></div>
      </div>
    </div>
  </div>""", notes(('SAY', 'NPayButton: a title and an action. Its body is a native Button whose label is the title, full width, with vertical padding; plain button style, white text, and the primary token as a rounded background with the small radius. The caller writes NPayButton(title:) with a trailing closure. The visual styling stays inside the component; the caller supplies the action, the closure-based architecture of Lesson 2.7.'),
                  ('SAY', 'Click: behind the scenes: the feature screen creates an NPayButton value; NPayButton is a struct conforming to View; inside, a native Button, the interactive control; then Text and modifiers for label, padding, colours and shape; and the SwiftUI runtime coordinates layout, rendering and interaction, evaluating body as needed.'),
                  ('SAY', 'Click: creating a reusable view does not necessarily create a separate UIKit view object. SwiftUI composes view descriptions and manages the platform presentation internally.'),
                  ('CONNECT', 'Version 2: an icon.'))))

B2 = """struct NPayButton: View {
    let title: String
    let symbol: String?
    let action: () -> Void

    init(_ title: String,
         symbol: String? = nil,
         action: @escaping () -> Void) {
        self.title = title
        self.symbol = symbol
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 10) {
                if let symbol { Image(systemName: symbol) }
                Text(title)
            }
            .font(.headline)
            .frame(maxWidth: .infinity)
            .padding(.vertical, 14)
        }
        // .buttonStyle, .foregroundStyle, .background as v1
    }
}"""
S.append(slide("Part 3 &middot; A more flexible NPayButton (section 17)", "Six Unit 1 ideas in one component", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.8fr);gap:24px;align-items:start">
      {code("NPayButton (v2, condensed)", B2, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Use", 'NPayButton("Send Money",\\n           symbol: "arrow.up.right") {\\n    print("Send tapped")\\n}'.replace(chr(92) + "n", chr(10)), "font-size:12.5px")}
        <div class="step">{tbl(["Swift", "Here"], [("Optional property", "<code>symbol: String?</code>"), ("Custom initializer", "<code>init(_:symbol:action:)</code>"), ("Default argument", "<code>symbol = nil</code>"), ("Escaping closure", "<code>@escaping</code> action"), ("<code>if let</code>", "show the icon only if set"), ("Protocol conformance", "<code>View</code>")])}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Version 2 adds an optional SF Symbol. A custom initializer takes an unlabelled title, an optional symbol defaulting to nil, and an escaping action. In body, if let shows the image only when a symbol was given, beside the title in an HStack. Calls read NPayButton("Send Money", symbol: "arrow.up.right") with a trailing closure.'),
                  ('SAY', 'Click: the Unit 1 connection: an optional property, a custom initializer, a default argument, an escaping closure, conditional binding with if let, and protocol conformance through View. All of them work together in one reusable component. The action must be @escaping because the button stores it and calls it later, after init returns.'),
                  ('CONNECT', 'What must a button not do?'))))

P = [box(0, 0, 460, 54, 'NPayButton', 'appearance + interaction', None, '', 'tap'), wire('M230 56V70' + head(230, 70, 'd')),
     box(0, 74, 460, 54, 'PaymentsScreen', 'coordinates the payment form', None, 'lit', 'file'), wire('M230 130V144' + head(230, 144, 'd')),
     box(0, 148, 460, 54, 'NPayStore', 'validates and records the demo payment', None, '', 'db')]
S.append(slide("Part 3 &middot; What belongs inside NPayButton? (section 18)", "Presentation and activation; never the payment", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("The caller decides", 'NPayButton("Send Money") {\\n    submitPayment()\\n}'.replace(chr(92) + "n", chr(10)), "font-size:14px")}
        <div class="warn step" data-label="Not inside the button">{ul("<code>store.recordDemoPayment(...)</code>", "A button that knows about money can&rsquo;t be reused")}</div>
      </div>
      <div class="step">{svg('0 0 460 202', 'NPayButton handles appearance, PaymentsScreen coordinates, NPayStore records', 'resp', P, 'max-height:220px')}
        <div class="gap"></div>
        {card("Later", ul("Even more important with MVVM and clean architecture (Unit 4)"))}</div>
    </div>
  </div>""", notes(('SAY', 'Suppose the Send Money button must validate a payment. Should the reusable button contain store.recordDemoPayment? Click: no. The button should not know about financial operations; a button that calls the store is no longer a reusable design component, it is a payment feature.'),
                  ('SAY', 'Click: the split: NPayButton handles appearance and user activation; PaymentsScreen coordinates the payment form; NPayStore validates and records the demo payment. The caller passes submitPayment in the closure. This separation matters even more with MVVM and clean architecture in Unit 4.'),
                  ('CONNECT', 'One more thing a button must do: look disabled.'))))

EN = """struct NPayButton: View {
    // title, symbol, action, init as before
    @Environment(\\.isEnabled) private var isEnabled

    var body: some View {
        Button(action: action) { /* label as before */ }
            .buttonStyle(.plain)
            .foregroundStyle(.white)
            .background(NPayTheme.Colors.primary
                            .opacity(isEnabled ? 1 : 0.4),
                        in: RoundedRectangle(
                            cornerRadius: NPayTheme.Radius.small))
    }
}"""
S.append(slide("Part 3 &middot; A finding: .disabled barely shows (integration)", "The background is ours, so dimming it is our job", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px 150px minmax(0,1fr);gap:20px;align-items:start">
      {TOP("img/payments.png", "Disabled (empty form)", 150, 210)}
      {TOP("img/valid.png", "Enabled (valid form)", 150, 210)}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What we saw", ul("<code>.disabled(!isValid)</code> on NPayButton", "Only the text dimmed; the blue stayed full strength"))}
        <div class="step">{code("A fix (authored, not in our integration)", EN, "font-size:11.5px")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Integrating the button into the Payments form showed something the text does not cover. Review Payment is disabled until the form is valid. On the left, disabled; in the middle, enabled. Look closely: only the text dims; the blue background stays at full strength, so a disabled payment button looks almost tappable. With .plain style, the system dims the content it styles; our background is our own drawing.'),
                  ('SAY', 'Click: a design-system fix, which we wrote and typechecked but did not put into the integration, to keep the text&rsquo;s component as written: read isEnabled from the environment, which .disabled sets, and dim the background. Another reason a design system is more than looking identical: states matter.'),
                  ('CONNECT', 'The second component: a card that holds anything.'))))

# ================================================================== Part 4 (7, 8, 15, 16)
divider(4, "NPayCard", "Generic over its content", 'One card, any SwiftUI view inside.', 'The code.')
CD = """struct NPayCard<Content: View>: View {

    @ViewBuilder let content: Content

    var body: some View {
        content
            .padding(NPayTheme.Spacing.medium)
            .frame(maxWidth: .infinity)
            .background(NPayTheme.Colors.cardBackground,
                        in: RoundedRectangle(
                            cornerRadius: NPayTheme.Radius.card))
    }
}

NPayCard {
    VStack {
        Text("Account")
        Text("Demo User")
    }
}"""
S.append(slide("Part 4 &middot; NPayCard: generic reusable content (section 7)", "<code>Content: View</code>, filled by the caller", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.9fr);gap:24px;align-items:start">
      {code("DesignSystem/NPayCard.swift", CD, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Unit 1: generics", ul("<code>Content</code>: a generic type parameter", "<code>Content: View</code>: must conform to <code>View</code>"))}
        <div class="step">{card("<code>@ViewBuilder</code> on the property", ul("The memberwise init takes a builder closure", "Callers write declarative view syntax"))}</div>
        <div class="step">{TOP("img/catalog.png", "Two NPayCards: a VStack, an HStack", 260, 160)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'We want a card that can contain any SwiftUI content: a Text, or a VStack of several texts. One component, different view types: generics and @ViewBuilder. NPayCard is generic over Content, constrained to View. It stores content, and its body pads it with the medium spacing, makes it full width, and puts the card background behind it with the card radius.'),
                  ('SAY', 'Click: from Unit 1: Content is a generic type parameter; the constraint means whatever the caller provides must conform to View. Click: @ViewBuilder on the stored property makes Swift&rsquo;s memberwise initializer take a view-builder closure, so callers write the trailing-closure syntax you see. Click: two cards in our catalog: one holding a VStack, one an HStack with an icon.'),
                  ('CONNECT', 'What types does Swift actually infer?'))))

TY = [("<code>NPayCard {{ Text }}</code>", "<code>NPayCard&lt;Text&gt;</code>"),
      ("<code>NPayCard {{ VStack {{ Text; Text }} }}</code>", "<code>NPayCard&lt;VStack&lt;TupleView&lt;(Text, Text)&gt;&gt;&gt;</code>"),
      ("<code>NPayCard {{ HStack {{ Image; Text }} }}</code>", "<code>NPayCard&lt;HStack&lt;TupleView&lt;(Image, Text)&gt;&gt;&gt;</code>"),
      ("<code>NPayCard {{ Text; Text }}</code>", "<code>NPayCard&lt;TupleView&lt;(Text, Text)&gt;&gt;</code>")]
S.append(slide("Part 4 &middot; What @ViewBuilder builds; why generics matter (sections 8, 15)", "Real types, printed with <code>type(of:)</code>", f"""  <div class="body">
    {tbl(["Code", "type(of:) in the simulator"], [(a.replace('{{', '{').replace('}}', '}'), b) for a, b in TY], 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:20px">
      <div class="step">{card("@ViewBuilder", ul("Two children &rarr; one <code>TupleView&lt;(Text, Text)&gt;</code>", "Not an array of <code>UIView</code>s"))}</div>
      <div class="step">{card("Generics", ul("The full structure is in the <b>type</b>", "Checked at compile time; no <code>AnyView</code>"))}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s experiment 5: inspect the inferred generic types. We printed type(of:) for four cards. A single Text: NPayCard of Text. A VStack of two Texts: NPayCard of VStack of TupleView of a pair of Texts. An HStack with an Image and a Text: the same shape with HStack. And two Texts directly in the card: NPayCard of TupleView of Text and Text.'),
                  ('SAY', 'Click: that last line answers Section 8: how can the closure return two views? The result builder combines them into one composed value, a TupleView here. The text calls it tuple-like and a compiler detail, and that is right: it is what the iOS 26.5 SDK produces today. It is never an array of UIView objects.'),
                  ('SAY', 'Click: why generics matter: the complete structure of the content is in the type, so it is checked at compile time and SwiftUI has the structural information; nothing is forced into a type-erased AnyView.'),
                  ('CONNECT', 'So why not AnyView?'))))

AV = """// generic: the structure stays in the type
struct NPayCard<Content: View>: View {
    let content: Content
    var body: some View { content }
}

// type-erased: one type for any content
struct ErasedCard: View {
    let content: AnyView
    var body: some View { content }
}

ErasedCard(content: AnyView(Text("NPay")))"""
S.append(slide("Part 4 &middot; Why not AnyView everywhere? (section 16)", "Erasure hides the structure", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Generic vs type-erased", AV, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("type(of:), simulator", ["AnyView(Text(\"NPay\")): AnyView", "NPayCard { Text }:&ensp;&ensp;&ensp;NPayCard&lt;Text&gt;"], 13)}</div>
        <div class="step">{card("AnyView is for", ul("Storing <b>different</b> view types behind one type"))}</div>
        <div class="rule step" data-label="For NPay components">{ul("Prefer generics: unnecessary erasure obscures structure")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI provides AnyView, which erases the concrete view type. Compare a generic card, whose content type is part of the card&rsquo;s type, with a type-erased one that stores AnyView. We renamed the erased one ErasedCard so both compile together.'),
                  ('SAY', 'Click: printed: an AnyView is just AnyView; what was inside is no longer in the type. The generic card keeps it: NPayCard of Text. Click: AnyView is useful when different view types must be stored behind one common type. Click: but unnecessary type erasure obscures structural information and adds complexity, so for NPay&rsquo;s reusable components the generic approach is preferable.'),
                  ('CONNECT', 'Components can also be modifiers.'))))

# ================================================================== Part 5 (9, 10)
divider(5, "Views and modifiers", "Structure, or transformation?", 'NPayCard vs NPayCardModifier; a section header.', 'The comparison.')
MD = """struct NPayCardModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding(16)
            .background(NPayTheme.Colors.cardBackground,
                        in: RoundedRectangle(cornerRadius: 18))
    }
}

extension View {
    func npayCardStyle() -> some View {
        modifier(NPayCardModifier())
    }
}

Text("Recent Transactions")
    .npayCardStyle()"""
VM = [("Encapsulates content structure", "Encapsulates a transformation"), ("Can receive custom child content", "Modifies an existing view"),
      ("NPayCard", "NPayCardStyle"), ("Semantic components", "Shared styling rules")]
S.append(slide("Part 5 &middot; Custom ViewModifier versus reusable View (section 9)", "Two tools, two jobs", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("Lesson 2.6&rsquo;s pattern", MD, "font-size:11.5px")}
        <div class="step">{console("type(of: Text(…).npayCardStyle())", ["ModifiedContent&lt;Text, NPayCardModifier&gt;"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Reusable View", "ViewModifier"], VM, 'tbl')}</div>
        <div class="step">{card("Notice", ul("The modifier uses 16 and 18, not the tokens", "Experiment 2 changed the card radius; this one stayed"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Lesson 2.6 built a ViewModifier for NPay&rsquo;s card style. The text&rsquo;s version: NPayCardModifier pads its content and adds the card background, and an extension adds npayCardStyle(). Click: printed type: ModifiedContent of Text and NPayCardModifier: a wrapper, as 2.6 showed.'),
                  ('SAY', 'Click: the comparison. A reusable view encapsulates content structure and can receive custom child content: NPayCard. A modifier encapsulates a transformation of an existing view: the card style. Choose a view for a meaningful component with its own structure; a modifier for a styling rule that applies to many different views.'),
                  ('SAY', 'Click: one thing to spot: the text&rsquo;s modifier hardcodes 16 and 18 instead of using the tokens. In our changed-token build, the NPayCards became square; the "Recent Transactions" text styled by the modifier kept its round corners. A token only helps where it is used.'),
                  ('CONNECT', 'A component for section headers.'))))

SH = """struct NPaySectionHeader: View {
    let title: String
    let actionTitle: String?
    let action: (() -> Void)?

    var body: some View {
        HStack {
            Text(title)
                .font(.headline)
            Spacer()
            if let actionTitle, let action {
                Button(actionTitle, action: action)
                    .font(.subheadline)
            }
        }
    }
}

NPaySectionHeader(title: "Recent Transactions",
                  actionTitle: "View All") {
    router.select(.history)
}"""
S.append(slide("Part 5 &middot; Build NPaySectionHeader (section 10)", "One header for Home, History and Profile", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.85fr);gap:24px;align-items:start">
      {code("DesignSystem/NPaySectionHeader.swift", SH, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("How it&rsquo;s built", ul("Title left, optional action right", "Both <code>actionTitle</code> and <code>action</code> needed: <code>if let</code> both"))}
        <div class="step">{TOP("img/home.png", "In Home: View All switches to History", 220, 260)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Home and History both need section headers. NPaySectionHeader: a title, an optional action title and an optional action. The body is an HStack: the title in headline, a Spacer, and a button only when both the action title and the action are present: if let on both.'),
                  ('SAY', 'Using it: the memberwise initializer lets the optional action be a trailing closure. In Home, View All asks the router to select the History tab, the 3.3 pattern. Click: in our integrated Home, the header inside the transactions card. The same component can appear in Home, History or Profile without duplicating its layout.'),
                  ('CONNECT', 'Which styles flow down by themselves?'))))

# ================================================================== Part 6 (11, 19, 20)
divider(6, "Adapting", "Environment, Dynamic Type, dark mode", 'A design system must adapt, not just match.', 'Environment.')
S.append(slide("Part 6 &middot; Environment propagation and design systems (section 11)", "Some values flow down; padding doesn&rsquo;t", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("The font flows down", 'VStack {\\n    Text("Account")\\n    Text("Balance")\\n}\\n.font(.headline)'.replace(chr(92) + "n", chr(10)), "font-size:14px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Propagates", ul("<code>.font</code>: an <b>environment</b> value for descendants (2.6)"))}
        <div class="step">{card("Doesn&rsquo;t", ul("<code>.padding()</code>: layout around <b>this</b> view only"))}</div>
        <div class="rule step" data-label="Two different things">{ul("Tokens: ordinary Swift constants", "Environment values: SwiftUI&rsquo;s contextual data", "Custom keys and shared themes: Lesson 3.9")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'SwiftUI lets certain styling values propagate through the hierarchy. A font set on the VStack influences every Text inside it: the font is an environment value, as Lesson 2.6 showed with type(of:).'),
                  ('SAY', 'Click: not every modifier propagates. .padding changes layout around one specific view; it is not an inherited value. Click: so keep two ideas apart: design tokens are ordinary Swift constants you reference; environment values are SwiftUI&rsquo;s contextual data propagation. Custom environment keys and shared themes are Lesson 3.9.'),
                  ('CONNECT', 'Users can change the text size. Does the system follow?'))))

S.append(slide("Part 6 &middot; Dynamic Type: fixed fonts don&rsquo;t scale (section 19)", "At the largest size: 19.3 points vs 74.7", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 160px;gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {tbl(["&ldquo;Send Money&rdquo;", "Default size", "Accessibility XXXL"], [("<code>.font(.system(size: 16))</code>", "19.3 pt high", "<b>19.3</b> pt"), ("<code>.font(.headline)</code>", "24.3 pt", "<b>74.7</b> pt")], 'tbl')}
        <div class="step">{card("Semantic styles", ul("<code>.headline</code>, <code>.body</code>, <code>.caption</code> follow the user&rsquo;s setting", "Our components use <code>.headline</code>, so they scaled"))}</div>
        <div class="rule step" data-label="Principle">{ul("A design system shouldn&rsquo;t make screens identical", "It should make them <b>adapt</b> consistently")}</div>
      </div>
      <div class="step">{TOP("img/catalog_ax.png", "Catalog, largest text", 160, 300)}</div>
    </div>
  </div>""", notes(('SAY', 'A fixed size, .system(size: 16), stays that size unless you add scaling. Users can choose larger text for accessibility. We measured the height of the same words, "Send Money", in a fixed 16-point font and in the semantic headline style, at the default size and at the largest accessibility size.'),
                  ('SAY', 'The fixed font was 19.3 points high at both sizes: it ignored the setting. Headline went from 24.3 to 74.7. Click: semantic styles adapt to Dynamic Type; NPayButton and NPaySectionHeader use .headline, and click: our catalog at that size: the buttons and cards grew with the text.'),
                  ('SAY', 'Click: the text&rsquo;s principle: a design system should not simply make every screen look identical; it should help the interface adapt consistently to accessibility settings. Lesson 3.8 deals with layouts that must make room for that.'),
                  ('CONNECT', 'And dark mode?'))))

AS = """// Assets.xcassets/NPayPrimary.colorset (our values)
// Any:  sRGB 0.10, 0.34, 0.65   (the token)
// Dark: sRGB 0.45, 0.65, 1.00

Text("Asset NPayPrimary")
    .foregroundStyle(Color("NPayPrimary"))"""
S.append(slide("Part 6 &middot; Design tokens versus semantic colours (sections 4, 20)", "A fixed colour can&rsquo;t follow the appearance", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px 150px minmax(0,1fr);gap:18px;align-items:start">
      {TOP("img/catalog.png", "Light", 150, 270)}
      {TOP("img/catalog_dark.png", "Dark", 150, 270)}
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("A colour asset", AS, "font-size:11.5px")}
        <div class="step">{tbl(["Colour", "on white", "on black"], [("Fixed <code>primary</code>", "7.1 : 1", "<b>2.9 : 1</b>"), ("Asset, dark variant", "", "8.6 : 1")])}
          <p class="small muted" style="margin:6px 0 0">WCAG contrast ratio, computed from the sRGB values; 4.5 : 1 is the usual minimum for body text.</p></div>
        <div class="step">{card("Also in dark", ul("<code>Color.blue.opacity(0.06)</code> cards almost vanish (Home, next slide)"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The theme&rsquo;s primary is a fixed RGB colour. Fine on white; but test the design in dark mode, experiment 7. Our catalog, light and dark: the "Fixed token" text in the bottom row is dark blue on black, hard to read; next to it, a colour asset, NPayPrimary, with a lighter dark-mode variant we chose.'),
                  ('SAY', 'For production the text recommends semantic colour assets: create NPayPrimary in Assets.xcassets with light and dark appearances and use Color("NPayPrimary"). Click: in numbers, using the standard WCAG contrast formula on the sRGB values: the fixed primary is 7.1 to 1 on white, but only 2.9 to 1 on black, below the usual 4.5 minimum for text. The asset&rsquo;s dark variant is 8.6 to 1.'),
                  ('SAY', 'Click: the card background is a fixed 6% blue too; on black it nearly disappears. Semantic assets let the design system adapt without rewriting every component.'),
                  ('CONNECT', 'Now integrate the system into NPay.'))))

# ================================================================== Part 7 (12, 21)
divider(7, "Integration", "Same behaviour, new components", 'Buttons, cards and headers in the real app.', 'Three changes.')
BA = """// A. Primary buttons
Button("Send Money") { submitPayment() }
    .buttonStyle(.borderedProminent)
NPayButton("Send Money") { submitPayment() }

// B. Transaction sections
NPayCard {
    VStack(alignment: .leading, spacing: 12) {
        // C. Section headers
        NPaySectionHeader(title: "Recent Transactions",
                          actionTitle: "View All") {
            router.select(.history)
        }
        // rows
    }
}"""
S.append(slide("Part 7 &middot; Integrate the design system (section 12)", "Replace buttons, wrap sections, reuse headers", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 140px 140px;gap:18px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:10px">
        {code("Before &rarr; after", BA, "font-size:11.5px")}
        <div class="step">{card("Our integration (authored)", ul("Home: NPayButton, NPayCard + header; BalanceCard uses tokens", "Review, Confirm, Back to Dashboard: NPayButton"))}</div>
      </div>
      {PHONE("img/home.png", "Home", 140)}
      <div class="step">{PHONE("img/home_dark.png", "Home, dark", 140)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s three changes. A: primary buttons: Button with the bordered-prominent style becomes NPayButton with the same closure. B: transaction sections wrapped in NPayCard instead of hand-written padding and background. C: the NPaySectionHeader with View All. The business logic is unchanged; we improve composition and consistency.'),
                  ('SAY', 'Click: what we did in the complete app, flagged as ours since the text names this as its next checkpoint: on Home, Send Money is an NPayButton that selects the Payments tab, and the recent transactions sit in an NPayCard with the header; BalanceCard uses the primary and card-radius tokens; Review Payment, Confirm Demo Payment and Back to Dashboard are NPayButtons.'),
                  ('SAY', 'On the right, Home. Click: Home in dark mode: the balance card and buttons hold up; the transactions card background has all but disappeared, the fixed-colour issue from the last slide.'),
                  ('CONNECT', 'The rest of the flow.'))))

S.append(slide("Part 7 &middot; The payment flow, with components (integration)", "Same flow as 3.5; new buttons", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;align-items:start">
      {PHONE("img/valid.png", "Review Payment: NPayButton", 165)}
      <div class="step">{PHONE("img/review.png", "Confirm: NPayButton", 165)}</div>
      <div class="step">{PHONE("img/success.png", "Back to Dashboard: NPayButton", 165)}</div>
    </div>
  </div>""", notes(('SAY', 'The payment flow from 3.5 with the new components: Review Payment with an icon. Click: the review sheet&rsquo;s Confirm Demo Payment. Click: the success screen&rsquo;s Back to Dashboard. The draft, review snapshot, re-validation and onDismiss navigation are exactly as before; only the buttons changed, and every one now follows the tokens.'),
                  ('CONNECT', 'The component catalog.'))))

CAT = [("NPayTheme", "shared design tokens", "design system"), ("NPayButton", "branded primary actions", "design system"), ("NPayCard", "reusable card container", "design system"),
       ("NPaySectionHeader", "consistent section headings", "design system"), ("NPayCardModifier", "reusable card styling", "design system"),
       ("BalanceCard", "domain-specific balance display", "feature"), ("TransactionRow", "domain-specific transaction display", "feature")]
S.append(slide("Part 7 &middot; NPay component catalog (section 21)", "General-purpose vs domain-specific", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) 170px;gap:22px;align-items:start">
      <div>{tbl(["Component", "Responsibility", "Level"], CAT)}
        <div class="gap"></div>
        <div class="rule step" data-label="Two levels">{ul("Both reusable; different architectural levels", "BalanceCard knows money; NPayCard knows only layout")}</div></div>
      <div class="step">{TOP("img/catalog.png", "The catalog screen", 170, 280)}</div>
    </div>
  </div>""", notes(('SAY', 'By the end of the lesson the design system has NPayTheme for tokens, NPayButton for primary actions, NPayCard as a container, NPaySectionHeader for headings and NPayCardModifier for card styling. BalanceCard and TransactionRow are reusable too, but domain-specific feature components.'),
                  ('SAY', 'Click: both are reusable, at different architectural levels: BalanceCard knows about money and formatting; NPayCard knows only layout. Click: our catalog screen shows every design-system component in one place: worth keeping in a real project, as a preview, to review changes.'),
                  ('CONNECT', 'Debugging components.'))))

# ================================================================== Part 8 (13, 22)
divider(8, "Debugging and experiments", "When does a component re-evaluate?", '_printChanges and the text&rsquo;s experiment list.', 'The probe.')
PC = """var body: some View {
    let _ = Self._printChanges()
    Button(action: action) { /* … */ }
}

// parent: three buttons, an unrelated counter
TracedNPayButton(title: "Send Money") { print("Send tapped") }
TracedNPayButton(title: "Static") {}
TracedNPayButton(title: "Captures count") {
    print("count is", count)
}"""
S.append(slide("Part 8 &middot; _printChanges in a component (sections 13, 22)", "The parent changed; most buttons didn&rsquo;t re-run", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("NPayButton with the debugging line (authored lab)", PC, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator", ["launch: 3 &times; TracedNPayButton: @self changed.", "Count tapped twice (screen: Count: 2)", "&ensp;2 &times; TracedNPayButton: @self changed.", "&ensp;(only the button whose closure captures count)"], 12.5)}</div>
        <div class="rule step" data-label="Read it">{ul("New closure values that capture nothing: no re-evaluation here", "A closure that captures changing state: re-evaluated", "And a body run is not a full redraw")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s debugging experiment: put let _ = Self._printChanges() in a reusable component&rsquo;s body and watch when SwiftUI re-evaluates it. We used three copies of the first NPayButton in a parent with an unrelated counter: one whose action prints, one empty, one whose closure captures the counter.'),
                  ('SAY', 'Click: at launch, three lines, one per button. Then we tapped Count twice; the screen said Count: 2, so the parent re-evaluated twice and built new button values each time. Only two more lines appeared, both from the button whose closure captures count. The other two were not re-evaluated, even though they received brand-new closure values.'),
                  ('SAY', 'Click: so, on this release, SwiftUI skipped buttons whose inputs had not meaningfully changed, and re-ran the one whose closure captured changing state. That is an observation, not a contract; and as the text says, even when body runs it does not necessarily mean a full redraw.'),
                  ('CONNECT', 'The text&rsquo;s experiment list.'))))

XP = [("1. Change <code>primary</code>", "every NPayButton, the balance card, token-coloured text (Part 2)"), ("2. Change <code>Radius.card</code>", "NPayCards and BalanceCard; not the modifier (Parts 2, 5)"),
      ("3&ndash;4. NPayCard with a VStack / an HStack", "both render; same card (Part 4)"), ("5. Inspect inferred types", "<code>NPayCard&lt;VStack&lt;TupleView&lt;(Text, Text)&gt;&gt;&gt;</code> … (Part 4)"),
      ("6. View vs modifier", "<code>ModifiedContent&lt;Text, NPayCardModifier&gt;</code> (Part 5)"), ("7. Light and dark", "fixed primary 2.9 : 1 on black; cards fade (Part 6)"),
      ("Larger text size", "<code>.headline</code> 24.3 &rarr; 74.7 pt; fixed 16 pt stays 19.3 (Part 6)")]
S.append(slide("Part 8 &middot; Xcode experiments (sections 13, 22)", "Every experiment, run", f"""  <div class="body">
    {tbl(["Experiment", "What we saw"], XP, 'tbl')}
  </div>""", notes(('SAY', 'The text&rsquo;s experiments, appearing in both pieces, with our results. Changing the primary colour changed every NPayButton, the balance card and token-coloured text. Changing the card radius changed the NPayCards and the balance card, but not the modifier with its hardcoded 18. Cards with a VStack and an HStack both work. The inferred types are the TupleView-based types we printed. The modifier version is a ModifiedContent wrapper. Dark mode exposed the fixed colours. And a larger text size scaled the semantic fonts, not the fixed one.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.7', (), [("layers", "Tokens &rarr; components &rarr; screens", "one change in a token reaches everything that uses it"),
                     ("diff", "Generic, not erased", "Content: View + @ViewBuilder; real types like TupleView"),
                     ("eye", "Adapt, don&rsquo;t just match", "semantic fonts and colours; disabled states; no business logic")],
         'Three things to remember. A design system is layers: tokens are plain Swift constants, components apply them, screens assemble components, so one token change reaches everything that uses it, and nothing that hardcodes around it. Components that take arbitrary content are generic over Content: View with @ViewBuilder, keeping the full structure in the type instead of AnyView. And a good system adapts: semantic fonts scale with Dynamic Type, semantic colours follow dark mode, components show their states, and none of them contains business logic.')

review_divider(10)
review([("grid", "Choose one", "What is a design token?",
         "What is a design token?<br>A. A network authentication token<br>B. A shared visual constant<br>C. A SwiftUI thread", "B",
         "<code>NPayTheme.Colors.primary</code>: one value many components use.",
         "Confusing it with auth tokens.", "Most pick B.", None),
        ("diff", "Choose one", "Why NPayCard&lt;Content: View&gt;?",
         "Why declare <code>NPayCard&lt;Content: View&gt;</code>?<br>A. To create a database<br>B. To disable type checking<br>C. To accept different SwiftUI content types", "C",
         "<code>NPayCard&lt;Text&gt;</code>, <code>NPayCard&lt;VStack&lt;…&gt;&gt;</code>: one component.",
         "Reaching for AnyView.", "Most pick C.", None),
        ("code", "Choose one", "What does @ViewBuilder do?",
         "What does <code>@ViewBuilder</code> do?<br>A. Builds composed SwiftUI view descriptions<br>B. Creates arrays of UIView objects<br>C. Starts background tasks", "A",
         "Two Texts became one <code>TupleView&lt;(Text, Text)&gt;</code>.",
         "Picturing UIKit views.", "Most pick A.", None),
        ("gear", "Choose one", "When is a ViewModifier appropriate?",
         "When is a <code>ViewModifier</code> appropriate?<br>A. For storing payment data<br>B. For reusable view transformations<br>C. For managing navigation paths", "B",
         "A styling rule for many views: <code>npayCardStyle()</code>.",
         "Using modifiers for structure.", "Most pick B.", None),
        ("eye", "Question", "Do hardcoded tokens support dark mode automatically?",
         "Do hardcoded design tokens automatically support dark mode?", "No",
         "Fixed primary: 7.1 : 1 on white, 2.9 : 1 on black.",
         "Assuming a token is semantic.", "Some say yes.", None),
        ("layers", "Question", "Does a custom View create a separate UIKit object?",
         "Does creating a custom SwiftUI <code>View</code> necessarily create a separate UIKit view object?", "No",
         "It is a view description; SwiftUI manages the platform side.",
         "One struct = one UIView.", "Some say yes.", None),
        ("shield", "Question", "Should business logic live inside NPayButton?",
         "Should business logic live inside <code>NPayButton</code>?", "No",
         "The caller passes the action; the store records payments.",
         "Making components &ldquo;smart&rdquo;.", "Most say no.", None),
        ("tap", "Predict the result", "NPayButton(…).disabled(true): what changes?",
         "<code>NPayButton</code> (plain style, its own blue background) gets <code>.disabled(true)</code>. What do you see?<br>A. The whole button greys out<br>B. Only the text dims; the blue stays<br>C. It disappears", "B",
         "Our Payments screen: only the label dimmed. Dim the background via <code>isEnabled</code>.",
         "Assuming the system restyles custom backgrounds.", "Many pick A.", None),
        ("frame", "Predict the result", ".font(.system(size: 16)) at the largest text size?",
         "&ldquo;Send Money&rdquo; in <code>.font(.system(size: 16))</code> is 19.3 pt high. The user picks the largest accessibility size. Its height?<br>A. 19.3 pt<br>B. about 75 pt<br>C. 16 pt", "A",
         "Fixed sizes ignore Dynamic Type; <code>.headline</code> went to 74.7.",
         "Expecting every font to scale.", "Some pick B.", None),
        ("play", "Choose one", "From 3.6: does numericText() change the money?",
         "From Lesson 3.6: what does <code>.contentTransition(.numericText())</code> change?<br>A. How the balance is calculated<br>B. How the text changes on screen<br>C. The paise value stored", "B",
         "Presentation only; the paise integer is untouched.",
         "Mixing presentation with state.", "Most pick B.", "Spaced review from Lesson 3.6.")])

S.append(next_slide('3.7', [("3.8", "Adaptive layouts &amp; GeometryReader", "iPhone sizes, orientation, Dynamic Type, the layout proposal system"),
                            ("3.9", "Custom environment keys &amp; shared themes", "a theme passed through the environment"),
                            ("Unit 4", "MVVM &amp; clean architecture", "components stay dumb; behaviour moves to view models")],
                    'Lesson 3.8 makes NPay adapt to different iPhone sizes, orientations and Dynamic Type, and explains SwiftUI&rsquo;s layout proposals and measurement. Lesson 3.9 adds custom environment keys and shared themes. Unit 4 keeps components free of behaviour as MVVM arrives.'))

S.append(lab_slide('3.7', "An NPay design system", "Add the components; integrate; test the edges.",
                   ["Add NPayTheme, NPayButton, NPayCard, NPaySectionHeader.",
                    "Replace Home&rsquo;s button and transactions section.",
                    "Print <code>type(of:)</code> for three NPayCards.",
                    "Change <code>primary</code> and <code>Radius.card</code>; rebuild.",
                    "Test dark mode and the largest text size.",
                    "Make a disabled NPayButton look disabled."],
                   "", 'Expected, as in our run: NPayCard types such as NPayCard of VStack of TupleView of (Text, Text); a token change restyles every component that uses it (not the modifier with hardcoded values); dark mode exposes fixed colours; semantic fonts scale and the fixed one does not; .disabled alone only dims the label.',
                   side=f'<div>{card("You hand in", ul("Your printed NPayCard types", "Light and dark screenshots of Home", "Your disabled-state fix"))}</div>'))

end_slide('3.7', 'Reusable Components &amp;<br>NPay Design System', 'Lesson 3.8 &mdash; Adaptive Layouts, GeometryReader &amp; Responsive SwiftUI',
          'You can now organise tokens, components and screens; build components that keep styling and take actions; use generics and @ViewBuilder instead of AnyView; choose between a view and a modifier; make the system adapt to Dynamic Type, dark mode and disabled states; and keep business logic out of components.',
          'Next, Lesson 3.8: adaptive layouts, GeometryReader and responsive SwiftUI, and the layout proposal system underneath.')

write_deck(OUT37, '3.7', 'Design System', 'Design System')
