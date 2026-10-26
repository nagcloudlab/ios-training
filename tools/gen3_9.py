"""Generates decks/unit-3/lesson-3.9/index.html from the Lesson 3.9 text (SwiftUI Environment & Shared Configuration).
The text came in two pieces (Sections 1-15, cut off; "Part 2" Sections 15-25), grouped into 8 Parts. Evidence comes
from tools/sim3_9 (light and dark system appearance; the text's labs as written; NPayPreferences integrated into the 3.8
app, authored)."""
import html, os, re, sys
OUT39 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers
TOP = lambda src_, cap, w, h: shot(src_, cap, w, h)   # a phone screenshot cut to its top part

title_slide('3.9', 'SwiftUI Environment &amp;<br>Shared Configuration',
            'One appearance setting reaches every screen, and nobody passes it through an initializer. The <b>environment</b> carries it, contextually.',
            'Lesson 3.8 made NPay adapt to sizes. Today an architectural question: NPay gets a Light, Dark or System appearance preference. Do we pass a theme through every initializer? SwiftUI&rsquo;s environment propagates contextual values through the view hierarchy instead. We read built-in values, override them, define our own, inject an observable preferences model, and see exactly what happens when a required dependency is missing.')
outcomes_slide('3.9', [("eye", "Read environment values with <code>@Environment</code> and key paths"),
                       ("layers", "Explain how values propagate and how the <b>nearest</b> override wins"),
                       ("diff", "Choose between <code>@State</code>, <code>@Binding</code>, <code>@Environment</code>"),
                       ("gear", "Apply an appearance preference with <code>preferredColorScheme</code>"),
                       ("code", "Define a custom environment value"),
                       ("shield", "Inject observable models, and handle missing dependencies")])
where_slide('3.9', 'Today: configuration without plumbing', (),
            '3.8: adaptive layouts across devices and text sizes.',
            'NPayPreferences in the environment: appearance and a demo badge.',
            'Lesson 3.8 adapted layout to space. Today the environment carries shared configuration. Next lesson, the last of Unit 3: accessibility and localization.',
            'The milestone.')

# ================================================================== Part 1 (intro, 1)
divider(1, "The milestone", "A preference for the whole app", 'Light, Dark or System, chosen once.', 'The problem.')
PASS = """HomeScreen(theme: theme)
BalanceCard(theme: theme)
PaymentsScreen(theme: theme)
HistoryScreen(theme: theme)"""
S.append(slide("Part 1 &middot; Our NPay milestone (section 1)", "One choice, every screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px 150px;gap:18px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Passing the theme by hand", PASS, "font-size:14px")}
        <div class="warn step" data-label="Doesn&rsquo;t scale">{ul("Every initializer, every layer, forever")}</div>
        <div class="step">{card("The environment", ul("Propagates <b>contextual</b> information down the hierarchy", "No parameter at each step"))}</div>
      </div>
      {PHONE("img/home.png", "System: light", 150)}
      <div class="step">{PHONE("img/settings.png", "Profile &rarr; Appearance: Dark", 150)}</div>
      <div class="step">{PHONE("img/home_dark.png", "Home follows", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'NPay has four tabs, navigation destinations, reusable components and a design system. Now it introduces a user preference: Light, Dark or System appearance. Should we pass the selected theme manually through every initializer: HomeScreen, BalanceCard, PaymentsScreen, HistoryScreen?'),
                  ('SAY', 'Click: that becomes impossible to maintain as the app grows: every new layer must accept and forward a value it does not use. Click: SwiftUI provides the environment, a mechanism to propagate contextual information through the view hierarchy.'),
                  ('SAY', 'On the right, today&rsquo;s app, which follows the system light appearance. Click: in Profile, a new Appearance screen; we choose Dark. Click: Home, and every other tab, follows. One selection, the whole interface.'),
                  ('CONNECT', 'Start with a built-in value.'))))

# ================================================================== Part 2 (2, 3)
divider(2, "@Environment", "Reading contextual values", 'A key path into EnvironmentValues.', 'The first experiment.')
EE = """struct EnvironmentExperiment: View {
    @Environment(\\.colorScheme)
    private var colorScheme

    var body: some View {
        VStack(spacing: 20) {
            Text("NPay Environment Lab")
                .font(.title2.bold())
            Text(colorScheme == .dark ? "Dark Mode"
                                      : "Light Mode")
            Image(systemName: colorScheme == .dark
                  ? "moon.fill" : "sun.max.fill")
                .font(.system(size: 48))
        }
        .padding()
    }
}"""
S.append(slide("Part 2 &middot; What is @Environment? (section 2)", "The same view reads a different value", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;align-items:start">
      {code("EnvironmentExperiment.swift", EE, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="cols" style="{TWO};gap:12px">{TOP("img/envexp_light.png", "System light", 150, 190)}<div class="step">{TOP("img/envexp_dark.png", "System dark", 150, 190)}</div></div>
        <div class="step">{tbl(["Part", "Meaning"], [("<code>@Environment</code>", "SwiftUI property wrapper"), ("<code>\\.colorScheme</code>", "key path to an environment value"), ("<code>colorScheme</code>", "local property to read it"), ("<code>.dark</code> / <code>.light</code>", "cases of <code>ColorScheme</code>")])}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s first experiment, EnvironmentExperiment.swift: a property declared with @Environment(\\.colorScheme), and a body that shows "Dark Mode" or "Light Mode" and a moon or a sun accordingly.'),
                  ('SAY', 'Click, click: the parts: @Environment, the property wrapper; \\.colorScheme, a key path identifying an environment value; colorScheme, the local property we read; .dark and .light, cases of the ColorScheme enum. Unit 1 connection: a key path is a typed reference to a property, here a property of SwiftUI&rsquo;s EnvironmentValues, which SwiftUI uses to look the value up for this view.'),
                  ('SAY', 'Our runs, top right: with the simulator in light appearance, "Light Mode" and a sun; switched to dark, the same code reads dark: "Dark Mode" and a moon. Nobody passed anything in.'),
                  ('CONNECT', 'So where does the value come from?'))))

P = [box(240, 0, 460, 50, 'NPayRootView', 'supplies shared environment configuration', None, 'lit', 'layers'), wire('M470 52V66' + head(470, 66, 'd')),
     box(240, 70, 460, 50, 'TabView / NavigationStack', 'descendants receive contextual values', None, '', 'grid')]
for i, t in enumerate(['HomeScreen', 'PaymentsScreen', 'HistoryScreen', 'ProfileScreen']):
    x = i * 240
    P.append(wire(f'M470 122V136H{x + 110}V150' + head(x + 110, 150, 'd')))
    P.append(box(x, 154, 220, 50, t, 'reads colorScheme', None, '', 'eye'))
S.append(slide("Part 2 &middot; Where does the value come from? (section 3)", "From the hierarchy, not the initializer", f"""  <div class="body">
    {svg('0 0 940 204', 'NPayRootView supplies configuration; TabView and NavigationStack pass it; each screen reads colorScheme', 'prop', P, 'max-height:230px')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:20px">
      {card("Propagation", ul("A parent or ancestor can <b>override</b> a value", "Descendants read the effective value"))}
      <div class="rule step" data-label="Not a global variable">{ul("The value depends on <b>where</b> a view sits", "Two instances of one view can read different values")}</div>
    </div>
  </div>""", notes(('SAY', 'The most important question. Unlike an initializer parameter, an environment value is supplied through the view hierarchy. The root supplies configuration; containers like the TabView and NavigationStack pass it on; each screen reads what it needs, such as colorScheme. A parent or ancestor can override a value for its descendants.'),
                  ('SAY', 'Click: the nuance: environment values are not simply global variables. Their value depends on where a view appears in the hierarchy, so two instances of the same view can receive different values if they have different ancestors. The next part proves it.'),
                  ('CONNECT', 'Override a value.'))))

# ================================================================== Part 3 (4, 16)
divider(3, "Overrides and precedence", "The nearest value wins", 'Overriding a subtree, and what that really changes.', 'An override.')
OV = """VStack {
    Text("Normal appearance")

    EnvironmentExperiment()
        .environment(\\.colorScheme, .dark)
}"""
S.append(slide("Part 3 &middot; Override the environment (section 4)", "The child reads dark; its text turns white", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.85fr) 160px;gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Force one subtree into Dark", OV, "font-size:14px")}
        <div class="step">{console("Accessibility labels on screen", ["\"Normal appearance\", \"Dark Mode\""], 13)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("What happens", ul("<code>.environment(…)</code> overrides the value for that <b>subtree</b>", "The child reads <code>.dark</code>"))}
        <div class="warn step" data-label="Look at the screen">{ul("&ldquo;Dark Mode&rdquo; is there, but invisible", "Dark-scheme text is white; nothing darkened the background")}</div>
      </div>
      <div class="step">{PHONE("img/override.png", "Only the outer text shows", 160)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s override experiment: a VStack with a normal Text, and the EnvironmentExperiment with .environment(\\.colorScheme, .dark) applied. The modifier supplies an overridden value to that subtree, and SwiftUI resolves it when descendants read it.'),
                  ('SAY', 'Click: our run, in a light simulator: the screen&rsquo;s accessibility labels include "Dark Mode": the child read dark. Click: but look at the screenshot: only "Normal appearance" is visible. The child resolved its adaptive colours for the dark scheme, so its text and symbol are white, and nothing in that subtree drew a dark background. White on white.'),
                  ('SAY', 'The text&rsquo;s trainer question: does this change the iPhone&rsquo;s system appearance? No, only the SwiftUI environment for that subtree. Overriding colorScheme changes how views resolve colours, not the surface beneath them.'),
                  ('CONNECT', 'Two overrides at once: which wins?'))))

PR = """struct EnvironmentPrecedenceLab: View {
    var body: some View {
        VStack(spacing: 20) {
            SchemeReader(title: "Outer")

            SchemeReader(title: "Inner")
                .environment(\\.colorScheme, .dark)
        }
        .environment(\\.colorScheme, .light)
    }
}

struct SchemeReader: View {
    let title: String
    @Environment(\\.colorScheme) private var colorScheme

    var body: some View {
        Text("\\(title): \\(colorScheme == .dark ? "Dark" : "Light")")
    }
}"""
S.append(slide("Part 3 &middot; Environment precedence (section 16)", "Predict: Outer and Inner?", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("EnvironmentPrecedenceLab.swift", PR, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Predict", ul("A. Both Light", "B. Outer Light, Inner Dark", "C. Both Dark"))}
        <div class="step">{console("Simulator", ["Outer: Light", "Inner: Dark"], 14)}</div>
        <div class="rule step" data-label="Why">{ul("Lookup is contextual: the <b>nearest</b> modifier above the reader wins", "Same struct, different values")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s precedence experiment: a VStack sets colorScheme to light for everything inside it; one of its two SchemeReaders also sets dark on itself. Predict what each reports: both light, outer light and inner dark, or both dark?'),
                  ('SAY', 'Click: our run: Outer: Light, Inner: Dark. B.'),
                  ('SAY', 'Click: environment lookup is contextual: the effective value comes from the modifiers and ancestors around the reading view, and the nearer override wins for its own subtree. That is how two BalanceCards can receive different appearance settings while being the same struct.'),
                  ('CONNECT', 'Three mechanisms side by side.'))))

# ================================================================== Part 4 (5, 10)
divider(4, "Which mechanism?", "State, Binding, Environment", 'Own it, borrow it, or read it from context.', 'The comparison.')
MC = [("<code>@State</code>", "own local mutable state", "sheet visibility"), ("<code>@Binding</code>", "read/write state owned elsewhere", "balance editor"),
      ("<code>@Environment</code>", "read contextual values from the hierarchy", "color scheme")]
S.append(slide("Part 4 &middot; Environment versus @State versus @Binding (section 5)", "Reading context is not owning it", f"""  <div class="body">
    {tbl(["Mechanism", "Purpose", "NPay example"], MC, 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:20px">
      <div class="step">{card("Read, not write", ul("<code>@Environment(\\.colorScheme)</code> gives the <b>effective</b> scheme", "It doesn&rsquo;t let you change it"))}</div>
      <div class="step">{card("To let users choose", ul("<b>Own</b> the preference in state", "<b>Apply</b> it to the hierarchy (Part 5)"))}</div>
    </div>
  </div>""", notes(('SAY', 'Three mechanisms. @State owns local mutable state: whether a sheet is shown. @Binding reads and writes state owned elsewhere: the balance editor of Unit 2. @Environment reads contextual values from the hierarchy: the colour scheme.'),
                  ('SAY', 'Click: @Environment does not automatically mean a view can modify the underlying value: @Environment(\\.colorScheme) tells you the effective scheme; it is not a setter. Click: if users should choose their appearance, we own that preference in state and apply it to the hierarchy. That is Part 5.'),
                  ('CONNECT', 'Built-in values worth knowing.'))))

BV = [("<code>colorScheme</code>", "light or dark appearance"), ("<code>locale</code>", "language and regional formatting"), ("<code>dynamicTypeSize</code>", "preferred text size (3.7, 3.8)"),
      ("<code>accessibilityReduceMotion</code>", "reduced-motion preference (3.6)"), ("<code>dismiss</code>", "dismiss the presentation (3.1, 3.4)"),
      ("<code>horizontalSizeClass</code>", "horizontal size-class context"), ("<code>scenePhase</code>", "scene lifecycle state (0.4)")]
S.append(slide("Part 4 &middot; Built-in environment values (section 10)", "You&rsquo;ve been using the environment all unit", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:22px;align-items:start">
      {tbl(["Value", "Purpose (where we met it)"], BV, 'tbl')}
      {code("Reading several", "@Environment(\\\\.locale)\\nprivate var locale\\n\\n@Environment(\\\\.dynamicTypeSize)\\nprivate var dynamicTypeSize\\n\\n@Environment(\\\\.accessibilityReduceMotion)\\nprivate var reduceMotion".replace(chr(92) + chr(92), chr(92)).replace(chr(92) + "n", chr(10)), "font-size:12.5px")}
    </div>
  </div>""", notes(('SAY', 'SwiftUI provides many environment values, and we have already used several. colorScheme for appearance. locale for language and regional formatting: Lesson 2.12&rsquo;s en_IN rupee formatting is closely related. dynamicTypeSize, the text size of 3.7 and 3.8. accessibilityReduceMotion from 3.6. dismiss, from 3.1 and 3.4. horizontalSizeClass for size-class context. scenePhase for the scene lifecycle, back in Lesson 0.4.'),
                  ('SAY', 'Each is read the same way, with @Environment and a key path. These values let views adapt to their context.'),
                  ('CONNECT', 'Now let users choose an appearance.'))))

# ================================================================== Part 5 (6-9, 7)
divider(5, "Appearance preference", "Own it, apply it", 'NPayAppearance, a picker and preferredColorScheme.', 'The model.')
AP = """enum NPayAppearance: String, CaseIterable, Identifiable {
    case system
    case light
    case dark

    var id: String { rawValue }

    var title: String { rawValue.capitalized }

    var colorScheme: ColorScheme? {
        switch self {
        case .system: return nil
        case .light:  return .light
        case .dark:   return .dark
        }
    }
}"""
S.append(slide("Part 5 &middot; Build NPay appearance preferences (sections 6, 17)", "System means &ldquo;don&rsquo;t force it&rdquo;: nil", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("NPayAppearance", AP, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Swift features", ul("<code>String</code> raw values; <code>CaseIterable</code> for the picker", "<code>Identifiable</code> via <code>id</code>; <code>title</code> from the raw value"))}
        <div class="step">{card("Why <code>ColorScheme?</code>", ul("<code>.system</code> &rarr; <code>nil</code>", "<code>nil</code> = follow the surrounding appearance"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A model for the preference: NPayAppearance, an enum with System, Light and Dark. String raw values give a title through capitalized; CaseIterable lets a picker list all cases; Identifiable lets ForEach use them, with the raw value as the id.'),
                  ('SAY', 'Click: why is colorScheme optional? Because System means we do not want to force a specific scheme. Returning nil lets the app follow the surrounding appearance. Sections 6 and 17 show the same enum; 17 uses explicit returns.'),
                  ('CONNECT', 'Applying it: preferredColorScheme.'))))

PCS = """TabView {
    // NPay tabs
}
.preferredColorScheme(store.appearance.colorScheme)"""
S.append(slide("Part 5 &middot; Why .preferredColorScheme()? (section 7)", "A preference for the presentation, not a subtree override", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) 150px 150px;gap:20px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 7 (store version)", PCS, "font-size:13.5px")}
        <div class="step">{card("Experiment (authored)", ul("Same screen, two ways to say dark", "Then open a sheet"))}</div>
        <div class="rule step" data-label="Result">{ul("Overriding <code>colorScheme</code>: the sheet stays <b>light</b>", "<code>.preferredColorScheme(.dark)</code>: the sheet is dark too")}</div>
      </div>
      <div class="step">{PHONE("img/sheetenv.png", "environment override", 150)}</div>
      <div class="step">{PHONE("img/sheetpref.png", "preferredColorScheme", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'Section 7 first put the appearance in NPayStore and applied it on the root with .preferredColorScheme. Why that API? The text says it is the intended way to express an appearance preference for the presentation, and that it differs from overriding the colorScheme environment value inside a subtree. Click: we tested the difference.'),
                  ('SAY', 'Click: one screen made dark two ways, each with a button that opens a sheet. Click: with the environment override, the screen is dark, but the presented sheet is light: the override stops at that subtree, and a presentation is not inside it. Click: with preferredColorScheme the sheet is dark too: the preference applies to the presentation that contains the view, and what it presents.'),
                  ('SAY', 'The exact behaviour depends on the enclosing scene and presentation hierarchy, as the text says; for an app-wide appearance setting, preferredColorScheme at the root is the right tool.'),
                  ('CONNECT', 'The picker.'))))

PK = """struct AppearanceSettingsView: View {
    @Bindable var store: NPayStore

    var body: some View {
        Form {
            Section("Appearance") {
                Picker("Theme", selection: $store.appearance) {
                    ForEach(NPayAppearance.allCases) { option in
                        Text(option.title)
                            .tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }
        }
        .navigationTitle("Appearance")
    }
}"""
UP = [("tap", "User selects Dark", "the picker gets it"), ("link", "Binding writes", "appearance = .dark"), ("db", "Model changes", "observable property"),
      ("eye", "Root re-evaluates", "it read appearance"), ("layers", "Preference applied", "preferredColorScheme(.dark)"), ("play", "Interface updates", "every tab, dark")]
P = []
for i, (ic, t, sub) in enumerate(UP):
    x = i * 190
    P.append(tall(x, 0, 172, 116, ic, t, sub, f'{i + 1}', ''))
    if i < 5:
        P.append(wire(f'M{x + 174} 58H{x + 188}' + head(x + 188, 58, 'r')))
S.append(slide("Part 5 &middot; The appearance picker and its pipeline (sections 8&ndash;9) &middot; conceptual", "Selection &rarr; binding &rarr; model &rarr; root &rarr; screen", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;align-items:start">
      {code("Section 8 (store version)", PK, "font-size:11.5px")}
      <div>{cues(6)}{svg('0 0 1132 116', 'Select Dark, binding writes, model changes, root re-evaluates, preference applied, interface updates', 'up', P, 'max-height:110px')}
        <div class="gap"></div>
        {card("Segmented picker", ul("<code>selection:</code> a binding; each option&rsquo;s <code>.tag</code> is its value (3.3)"))}</div>
    </div>
  </div>""", notes(('SAY', 'The picker in Section 8: a Form with a segmented Picker bound to $store.appearance, one Text per case, each tagged with its value, like TabView tags in 3.3. When the user changes the selection, the store updates; the root reads the new preference and applies it.'),
                  ('SAY', 'Only stage 1 of the text&rsquo;s pipeline came with it; the rest is our outline. Click: the user selects Dark. Click: the binding writes .dark. Click: the observable model changes. Click: the root re-evaluates, because it read appearance. Click: it applies preferredColorScheme(.dark). Click: the whole interface updates. SwiftUI manages the propagation and rendering.'),
                  ('CONNECT', 'Our own environment values.'))))

# ================================================================== Part 6 (11, 12)
divider(6, "Custom environment values", "NPay&rsquo;s own configuration", 'A key, a typed accessor, a default.', 'The key.')
CK = """private struct NPayDemoModeKey: EnvironmentKey {
    static let defaultValue = true
}

extension EnvironmentValues {
    var npayDemoMode: Bool {
        get { self[NPayDemoModeKey.self] }
        set { self[NPayDemoModeKey.self] = newValue }
    }
}

// a parent supplies
.environment(\\.npayDemoMode, true)

// a child reads
@Environment(\\.npayDemoMode) private var demoMode"""
S.append(slide("Part 6 &middot; Create our own environment value (section 11)", "A key and an accessor", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("NPayDemoModeKey", CK, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("The parts", ul("<code>EnvironmentKey</code>: the type and the <b>default</b>", "<code>EnvironmentValues</code> extension: typed key-path access"))}
        <div class="step">{console("Two readers (simulator)", ["no ancestor sets it:&ensp;true&ensp;(the default)", "ancestor sets false:&ensp;false"], 13)}</div>
        <div class="tip step" data-label="Shorter (SDK)">{ul("<code>extension EnvironmentValues { @Entry var npayDemoMode = true }</code>", "Typechecks for our iOS 17 target")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Suppose NPay wants a configuration value controlling whether demo-mode indicators appear. A custom environment value needs two things: an EnvironmentKey, which defines the value&rsquo;s type through its default, true here; and an extension on EnvironmentValues with a computed property that reads and writes through the key. Then any parent can supply .environment(\\.npayDemoMode, …) and any child can read it with @Environment.'),
                  ('SAY', 'Click: our run: a reader with no ancestor setting the value gets the default, true; a reader under .environment(\\.npayDemoMode, false) gets false. Unit 1 at work: protocols, static properties, extensions, generics and key paths supporting a framework-level configuration system.'),
                  ('SAY', 'Click: a note from the SDK: SwiftUI also has the @Entry macro, which writes the key and accessor for you in one line. We typechecked it for NPay&rsquo;s iOS 17 target. The long form shows what @Entry generates.'),
                  ('CONNECT', 'How a child receives it.'))))

LK = [("layers", "NPayRootView", "supplies npayDemoMode = true"), ("gear", "Environment modifier", "overrides for descendants"), ("grid", "View hierarchy", "propagates contextual values"),
      ("db", "BalanceCard", "reads @Environment(\\.npayDemoMode)"), ("eye", "Conditional UI", "shows the Demo Account label")]
P = [box(0, i * 50, 600, 42, t, sub, None, '', ic) for i, (ic, t, sub) in enumerate(LK)]
S.append(slide("Part 6 &middot; Custom environment lookup (section 12) &middot; conceptual", "Scoped to a hierarchy, not a singleton", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:24px;align-items:start">
      {svg('0 0 600 242', 'Root supplies, modifier overrides, hierarchy propagates, BalanceCard reads, conditional UI', 'lk', P, 'max-height:260px')}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="rule" data-label="Scoped">{ul("Not a universal app-wide singleton", "Useful for <b>contextual</b> configuration")}</div>
        <div class="step">{card("Next", ul("A whole observable model in the environment"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The lookup path: the root supplies npayDemoMode true; an environment modifier can override it for a subtree; the hierarchy propagates it; BalanceCard reads it with @Environment; conditional UI shows a Demo Account label. An environment value is scoped to a view hierarchy; it is not a universal singleton, which is what makes it good for contextual configuration.'),
                  ('SAY', 'Click: the text then moves from single values to a whole observable model in the environment.'),
                  ('CONNECT', 'EnvironmentObject, and the modern way.'))))

# ================================================================== Part 7 (13, 14, 17-22)
divider(7, "Observable models in the environment", "Inject by type", 'NPayPreferences: appearance and a demo badge.', 'Old and new.')
EO = """// older code: ObservableObject + @EnvironmentObject
@EnvironmentObject var store: NPayStore

// Observation (iOS 17+): inject the instance, read by type
NPayRootView()
    .environment(store)

@Environment(NPayStore.self)
private var store"""
S.append(slide("Part 7 &middot; @EnvironmentObject versus modern Observation (section 13)", "Inject an instance; read it by its type", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Two generations", EO, "font-size:13px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("@EnvironmentObject", ul("Classes conforming to <code>ObservableObject</code>", "Still in many existing apps"))}
        <div class="step">{card("Observation", ul("An <code>@Observable</code> object via <code>.environment(object)</code>", "Read with <code>@Environment(Type.self)</code>", "Good for NPay&rsquo;s iOS 17+ target"))}</div>
        <div class="step">{card("Deeper", ul("Comparing the architectures: Unit 4"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'You will meet older SwiftUI code using @EnvironmentObject, historically with classes conforming to ObservableObject. Click: with modern Observation, we inject an observable model object into the environment by passing the instance to .environment, and a descendant reads it by type, @Environment(NPayStore.self). For our iOS 17+ project, modern Observation is a good choice; @EnvironmentObject remains relevant for existing apps and backward compatibility. Click: Unit 4 compares the architectures.'),
                  ('CONNECT', 'A dedicated preferences model.'))))

PF = """@MainActor
@Observable
final class NPayPreferences {
    var appearance: NPayAppearance = .system
    var showDemoBadge = true
}

// NPayRootView
@State private var preferences = NPayPreferences()

TabView(selection: $router.selectedTab) {
    // the four tabs
}
.environment(preferences)
.preferredColorScheme(preferences.appearance.colorScheme)"""
S.append(slide("Part 7 &middot; NPayPreferences, injected at the root (sections 15, 17&ndash;18)", "The root owns it; the environment shares it", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("NPayPreferences.swift + NPayRootView", PF, "font-size:12.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Why a separate model", ul("Account data and UI preferences: different concerns", "NPayStore shouldn&rsquo;t collect every setting"))}
        <div class="step">{card("At the root", ul("<code>@State</code> owns the instance", "<code>.environment(preferences)</code> shares it", "<code>.preferredColorScheme</code> applies it"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Should NPayStore contain every shared setting? No: it owns the balance, transactions and draft; add language, notifications, security and accessibility settings and it becomes a container for everything. The text&rsquo;s improvement: NPayPreferences, a main-actor observable class with the appearance and a showDemoBadge flag. It owns presentation preferences, not payment data.'),
                  ('SAY', 'Click: the root view owns one instance with @State, injects it with .environment(preferences), and applies the appearance with preferredColorScheme, read from the same object. Our complete code does exactly this, flagged as our integration.'),
                  ('CONNECT', 'Reading and editing it.'))))

AS = """struct AppearanceSettingsView: View {
    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        @Bindable var preferences = preferences

        Form {
            Section("Appearance") {
                Picker("Theme",
                       selection: $preferences.appearance) {
                    ForEach(NPayAppearance.allCases) { option in
                        Text(option.title).tag(option)
                    }
                }
                .pickerStyle(.segmented)
            }
            Section("Display") {
                Toggle("Show Demo Badge",
                       isOn: $preferences.showDemoBadge)
            }
        }
        .navigationTitle("Appearance")
    }
}"""
S.append(slide("Part 7 &middot; Read and edit the preferences (section 19)", "@Environment retrieves; @Bindable binds", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.6fr) 150px;gap:20px;align-items:start">
      {code("Screens/AppearanceSettingsView.swift", AS, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Two jobs", ul("<code>@Environment</code>: get the dependency", "<code>@Bindable</code>: bindings for the picker and toggle"))}
        <div class="step">{card("Our wiring (authored)", ul("Profile &rarr; Appearance row", "A new <code>.appearance</code> route"))}</div>
      </div>
      <div class="step">{PHONE("img/settings.png", "Dark selected", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The settings screen now gets the preferences from the environment, by type. Inside body, @Bindable var preferences turns that instance into something we can take bindings from: $preferences.appearance for the segmented picker, $preferences.showDemoBadge for a toggle. The same @Bindable-inside-body pattern as the router in 3.3.'),
                  ('SAY', 'Click: two different problems: @Environment retrieves a contextual dependency; @Bindable exposes bindings to its mutable properties. Click: our wiring: Profile gets an Appearance row and NPayRoute an .appearance case. Click: the screen in the simulator after choosing Dark.'),
                  ('CONNECT', 'Use the badge in BalanceCard.'))))

BC = """struct BalanceCard: View {
    let balancePaise: Int

    @Environment(NPayPreferences.self)
    private var preferences

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Available Balance")
                .font(.subheadline)
            Text(Money.display(balancePaise))
                .font(.largeTitle.bold())
            if preferences.showDemoBadge {
                Text("DEMO ACCOUNT")
                    .font(.caption.bold())
                    .padding(.horizontal, 10)
                    .padding(.vertical, 5)
                    .background(.white.opacity(0.18), in: Capsule())
            }
        }
        // white text, padding, rounded background as before
    }
}"""
S.append(slide("Part 7 &middot; Read the badge preference in BalanceCard (section 20)", "Toggle in Profile, change on Home", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.85fr);gap:20px;align-items:start">
      {code("Components/BalanceCard.swift (condensed)", BC, "font-size:10.5px")}
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="cols" style="{TWO};gap:12px">{TOP("img/home.png", "Badge on", 150, 230)}<div class="step">{TOP("img/nobadge.png", "Badge off", 150, 230)}</div></div>
        <div class="step">{console("Simulator", ["Home shows badge: true, ₹25,000.00", "[toggle \"Show Demo Badge\"]", "Home shows badge: false, ₹25,000.00"], 12)}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'BalanceCard reads the preferences from the environment and shows a DEMO ACCOUNT capsule only when showDemoBadge is on. No showDemoBadge parameter travels from the root to the card. In our integration the card keeps 3.6&rsquo;s numeric transition and 3.7&rsquo;s tokens; the badge replaces the old caption.'),
                  ('SAY', 'Click: our run: Home showed the badge and ₹25,000.00; we turned Show Demo Badge off in Profile; back on Home, no badge and the same balance. Click: the screenshot.'),
                  ('SAY', 'The text&rsquo;s safety note: the badge is only a visual preference. NPay stays a simulation either way; a production app must never let a UI preference decide whether payments are real or simulated.'),
                  ('CONNECT', 'What re-evaluates when a preference changes?'))))

S.append(slide("Part 7 &middot; Observation with the environment (sections 21, 24)", "_printChanges names the property", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Experiment 8", ul("The text&rsquo;s BalanceCard + <code>Self._printChanges()</code>", "Toggle the badge; change the appearance; change an unrelated counter"))}
        <div class="step">{console("Simulator", ["launch:&ensp;@self, @identity, _preferences changed.", "toggle badge:&ensp;\\NPayPreferences.showDemoBadge changed.", "change appearance:&ensp;@self changed.", "unrelated counter:&ensp;(nothing)"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Read it", ul("Observation tracked the exact property the body read", "The appearance change reached it another way: a new view value", "A change it didn&rsquo;t depend on: no body run"))}</div>
        <div class="rule step" data-label="Remember">{ul("Exact tracking and scheduling are framework-managed")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s pipeline for the badge toggle: the toggle receives the interaction, writes through the binding, the observable property changes, Observation knows BalanceCard read it, the card re-evaluates, the badge disappears. Experiment 8 lets us watch: the card with Self._printChanges(), in a small lab with three buttons.'),
                  ('SAY', 'Click: at launch: @self, @identity and _preferences changed: the first evaluation. Toggling the badge: "\\NPayPreferences.showDemoBadge changed": _printChanges names the exact observable property, the key path, that triggered the body. Changing the appearance: "@self changed": the card does not read appearance, but the root applied a new colour scheme and SwiftUI handed the card a new view value. Changing an unrelated counter: nothing.'),
                  ('SAY', 'Click: Observation tracked exactly what the body read. Click: the text&rsquo;s caution: the exact dependency tracking and rendering scheduling are framework-managed; use this to understand, not to build logic on.'),
                  ('CONNECT', 'And if the dependency is missing?'))))

S.append(slide("Part 7 &middot; Missing environment dependency (sections 14, 22)", "A required dependency, discovered at run time", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("No ancestor injects NPayPreferences", "// BalanceCard declares:\\n@Environment(NPayPreferences.self) private var preferences\\n\\n// shown without .environment(NPayPreferences())\\nBalanceCard(balancePaise: 2_500_000)".replace(chr(92) + "n", chr(10)), "font-size:12.5px")}
        <div class="step">{console("Simulator console", ["SwiftUICore/Environment+Objects.swift:34:", "Fatal error: No Observable object of type", "NPayPreferences found. A View.environmentObject(_:)", "for NPayPreferences may be missing as an", "ancestor of this view."], 12)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{code("Previews and tests supply it too", "#Preview {\\n    BalanceCard(balancePaise: 2_500_000)\\n        .environment(NPayPreferences())\\n}".replace(chr(92) + "n", chr(10)), "font-size:13px")}</div>
        <div class="rule step" data-label="Lesson">{ul("It compiles; it crashes when read", "Document required environment dependencies", "Critical ones: consider initializer injection")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'BalanceCard now declares a required dependency: @Environment(NPayPreferences.self). What if no ancestor supplies it? We launched a BalanceCard on its own, experiment 7.'),
                  ('SAY', 'Click: it compiled fine, and crashed when the card read the value: "Fatal error: No Observable object of type NPayPreferences found. A View.environmentObject for NPayPreferences may be missing as an ancestor of this view." Note the message still mentions environmentObject, the older API.'),
                  ('SAY', 'Click: the fix for previews and tests is to supply the dependency, as the text shows: .environment(NPayPreferences()). Click: the text&rsquo;s lesson: environment injection is convenient, but dependencies become invisible at the initializer call site and the compiler cannot check them. Document required environment dependencies, provide them in previews and tests, and consider explicit initializer injection for critical ones.'),
                  ('CONNECT', 'So when should we use the environment?'))))

# ================================================================== Part 8 (15, 23, 24)
divider(8, "Dependency injection", "Explicit where it matters", 'Three ways to supply what a view needs.', 'The comparison.')
DI = [("Initializer injection", "<code>BalanceCard(balancePaise: balance)</code>", "explicit required data"), ("Environment values", "<code>@Environment(\\.colorScheme)</code>", "contextual configuration"),
      ("Observable environment model", "<code>@Environment(NPayPreferences.self)</code>", "shared observable preferences")]
P = [box(250, 0, 440, 50, 'NPayRootView', 'application composition root', None, 'lit', 'layers')]
for i, (t, d) in enumerate([('NPayStore', 'balance, transactions'), ('NPayRouter', 'tabs, navigation'), ('NPayPreferences', 'appearance, language'), ('PaymentDraft', 'editable payment data')]):
    x = i * 240
    P.append(wire(f'M470 52V66H{x + 110}V80' + head(x + 110, 80, 'd')))
    P.append(box(x, 84, 220, 50, t, d, None, '', ''))
S.append(slide("Part 8 &middot; Does the environment replace dependency injection? (sections 15, 23)", "No: it is one way to supply dependencies", f"""  <div class="body">
    {tbl(["Approach", "Example", "Best use"], DI, 'tbl')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:20px;align-items:start">
      <div class="step">{svg('0 0 940 134', 'NPayRootView composes NPayStore, NPayRouter, NPayPreferences and the payment draft', 'cr', P, 'max-height:140px')}</div>
      <div class="rule step" data-label="NPay&rsquo;s rule">{ul("Domain data: explicit parameters", "Shared UI configuration: the environment", "Sharing state &ne; one big object")}</div>
    </div>
  </div>""", notes(('SAY', 'Three approaches. Initializer injection, like BalanceCard(balancePaise:), for explicit required data. Environment values like colorScheme for contextual configuration. An observable environment model like NPayPreferences for shared observable preferences.'),
                  ('SAY', 'Click: the longer-term architecture from Section 15: the root view as the composition root, owning separate objects with separate responsibilities: NPayStore for balance and transactions, NPayRouter for navigation, NPayPreferences for appearance and language, and the payment draft. Unit 4 formalises this. Click: NPay&rsquo;s rule: explicit parameters for domain data, the environment for suitable shared UI configuration, so we do not hide every dependency in the environment. And sharing state does not mean putting all state into one object.'),
                  ('CONNECT', 'The text&rsquo;s investigation lab.'))))

LAB = [("1&ndash;3. Picker: System &rarr; Dark; visit all tabs", "dark on Home, Payments, History, Profile"), ("4&ndash;5. Show Demo Badge off; Home", "badge gone; balance unchanged"),
       ("6. <code>.environment(\\.colorScheme, .light/.dark)</code> on a subtree", "only that subtree; colours, not background (Part 3)"),
       ("7. Preview without NPayPreferences", "fatal error: no Observable object found"), ("8. <code>_printChanges</code> in BalanceCard", "names <code>showDemoBadge</code>; ignores unrelated state"),
       ("Relaunch after choosing Dark (authored)", "back to System: preferences are in memory")]
S.append(slide("Part 8 &middot; Xcode investigation lab (section 24)", "Every experiment, run", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.3fr) 150px;gap:20px;align-items:start">
      {tbl(["Experiment", "Simulator"], LAB)}
      <div class="step">{PHONE("img/history_dark.png", "History, dark", 150)}</div>
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s eight experiments, all run. System to Dark, and every tab followed. The badge toggle removed the badge without touching the balance. An override on an isolated subtree affected only that subtree, and only how it resolves colours. A view without the required preferences crashed with the fatal error. _printChanges in BalanceCard named showDemoBadge and ignored unrelated state.'),
                  ('SAY', 'One more of ours: choose Dark, terminate the app, relaunch: back to System. The text&rsquo;s question 4: .environment(preferences) does not persist anything; preferences live in memory like the 3.5 draft. Persistence is Unit 6. Click: History in dark.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.9', (), [("layers", "Contextual, not global", "the nearest override wins; values depend on position"),
                     ("gear", "Own it, apply it", "preferences in an observable model; preferredColorScheme at the root"),
                     ("shield", "Inject deliberately", "required environment models crash if missing; data stays explicit")],
         'Three things to remember. The environment carries contextual values down the hierarchy: what a view reads depends on where it sits, and the nearest override wins; overriding colorScheme changes how a subtree resolves colours, not the surface or the sheets it presents. User preferences are owned in a model, NPayPreferences, injected with .environment and applied with preferredColorScheme; @Environment retrieves it and @Bindable binds it. And inject deliberately: a missing required model is a run-time crash, nothing is persisted automatically, and domain data stays in explicit parameters.')

review_divider(10)
review([("layers", "Choose one", "Is an environment value a global variable?",
         "Is an environment value a global variable?<br>A. Yes<br>B. No, it is contextual to the view hierarchy", "B",
         "Outer read Light while Inner read Dark in the same view tree.",
         "Thinking of it as app-wide state.", "Most pick B.", None),
        ("diff", "Choose one", "A nearer ancestor overrides a value: what happens?",
         "What happens when a nearer ancestor overrides an environment value?<br>A. The application restarts<br>B. The outer value always wins<br>C. The nearer value applies to its descendants", "C",
         "Inner: Dark under an outer Light.",
         "Expecting the outermost to win.", "Most pick C.", None),
        ("link", "Choose one", "Why @Bindable with an observable preferences object?",
         "Why use <code>@Bindable</code> with an observable preferences object?<br>A. To obtain bindings to mutable properties<br>B. To start a background task<br>C. To persist preferences automatically", "A",
         "The picker and toggle need <code>$preferences.appearance</code>, <code>$preferences.showDemoBadge</code>.",
         "Thinking @Environment gives bindings.", "Most pick A.", None),
        ("db", "Question", "Does .environment(preferences) persist them?",
         "Does <code>.environment(preferences)</code> automatically persist preferences to disk?", "No",
         "After a relaunch the app was back to System.",
         "Confusing sharing with saving.", "Most say no.", None),
        ("shield", "Choose one", "Risk of a missing required environment model?",
         "What is the risk of a missing required observable environment model?<br>A. Automatic fallback to UserDefaults<br>B. A runtime failure when accessed<br>C. A compiler-generated default model", "B",
         "&ldquo;Fatal error: No Observable object of type NPayPreferences found.&rdquo;",
         "Expecting the compiler to catch it.", "Most pick B.", None),
        ("gear", "Question", "Should every NPay dependency go in the environment?",
         "Should every NPay dependency be hidden in the environment?", "No",
         "Domain data stays in explicit parameters; the environment carries shared UI configuration.",
         "Using the environment for everything.", "Most say no.", None),
        ("eye", "Predict the result", "EnvironmentExperiment with .environment(\\.colorScheme, .dark), light app?",
         "In a light app, <code>EnvironmentExperiment().environment(\\.colorScheme, .dark)</code> sits on a white screen. What do you see?<br>A. A dark panel with white text<br>B. Its text, white on white: effectively invisible<br>C. The whole phone switches to dark", "B",
         "It read dark and resolved white text; nothing drew a dark background.",
         "Expecting the override to paint a background.", "Many pick A.", None),
        ("frame", "Predict the result", "Override colorScheme, then present a sheet?",
         "A screen uses <code>.environment(\\.colorScheme, .dark)</code> and opens a sheet. The sheet is&hellip;<br>A. Dark<br>B. Light", "B",
         "The override stops at the subtree; <code>.preferredColorScheme(.dark)</code> darkened the sheet.",
         "Using an environment override for app appearance.", "Some pick A.", None),
        ("code", "Choose one", "What does @Entry do?",
         "What does <code>@Entry var npayDemoMode = true</code> in an <code>EnvironmentValues</code> extension do?<br>A. Persists the value<br>B. Generates the key and accessor for a custom environment value<br>C. Makes it a global variable", "B",
         "The same as NPayDemoModeKey plus the get/set accessor, in one line.",
         "Thinking it changes the semantics.", "Some pick A.", None),
        ("key", "Choose one", "From 3.8: what keeps state when switching layouts?",
         "From Lesson 3.8: which kept CounterView&rsquo;s count when switching between a row and a column?<br>A. <code>if</code>/<code>else</code> branches<br>B. <code>AnyLayout</code>", "B",
         "AnyLayout 3 &rarr; 3; branches 3 &rarr; 0.",
         "Treating layout changes as cosmetic.", "Most pick B.", "Spaced review from Lesson 3.8.")])

S.append(next_slide('3.9', [("3.10", "Accessibility &amp; localization", "VoiceOver, Dynamic Type, identifiers, localization, right-to-left"),
                            ("Unit 4", "Architecture &amp; dependency injection", "composition root; Observation vs @EnvironmentObject in depth"),
                            ("Unit 6", "Persistence", "preferences that survive a relaunch")],
                    'Lesson 3.10, the last of Unit 3, covers accessibility and localization: VoiceOver, Dynamic Type, accessibility identifiers, localization resources and right-to-left layouts, using the locale and dynamicTypeSize values we listed today. Unit 4 formalises the composition root and dependency injection. Unit 6 makes preferences survive a relaunch.'))

S.append(lab_slide('3.9', "Shared configuration", "Add NPayPreferences; prove each behaviour.",
                   ["Run EnvironmentExperiment in light and dark.",
                    "Run the precedence lab; predict first.",
                    "Add NPayPreferences; inject it at the root.",
                    "Build AppearanceSettingsView; switch to Dark.",
                    "Add the demo badge; toggle it off.",
                    "Remove the injection from a preview; read the error."],
                   "", 'Expected, as in our run: Outer Light / Inner Dark; Dark applies to every tab and to sheets; the badge disappears without changing the balance; a view without NPayPreferences fails with "No Observable object of type NPayPreferences found"; nothing survives a relaunch.',
                   side=f'<div>{card("You hand in", ul("Your precedence prediction and result", "Screenshots: light, dark, badge off", "One sentence: environment vs initializer injection"))}</div>'))

end_slide('3.9', 'SwiftUI Environment &amp;<br>Shared Configuration', 'Lesson 3.10 &mdash; Accessibility &amp; Localization',
          'You can now read and override environment values, explain contextual precedence, choose between @State, @Binding and @Environment, apply an appearance with preferredColorScheme, define custom values, inject observable models and handle missing dependencies deliberately.',
          'Next, Lesson 3.10: accessibility and localization: VoiceOver, Dynamic Type, identifiers, localization resources and right-to-left layouts.')

write_deck(OUT39, '3.9', 'Environment', 'Environment')
