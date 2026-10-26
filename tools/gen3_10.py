"""Generates decks/unit-3/lesson-3.10/index.html from the Lesson 3.10 text (Accessibility & Localization). Only "Part 2:
Localization Internals, RTL Layout & Accessibility Testing" (Sections 15-25) was shared; Sections 1-14 (VoiceOver, Dynamic
Type, String Catalogs) were not, so the deck covers 15-25 and says so. Evidence comes from tools/sim3_10 (a compiled
String Catalog with en/ta/hi, the RTL pseudolanguage, printed accessibility elements) and a Mac currency run."""
import html, os, re, sys
OUT310 = sys.argv[1]
sys.argv = ['x', '/dev/null']
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
exec(open(os.path.join(HERE, 'unit3.py')).read())   # Unit 03 lesson list + shared helpers

title_slide('3.10', 'Accessibility &amp;<br>Localization',
            'The same NPay screen in English, Tamil and Hindi, mirrored for right-to-left, and <b>read aloud</b> meaningfully. The money never changes.',
            'This deck covers Part 2 of Lesson 3.10: localization internals, right-to-left layout and accessibility testing, Sections 15 to 25. Part 1, on VoiceOver, Dynamic Type and String Catalogs, was not shared. We compiled a real String Catalog into the app and ran it in English, Tamil and Hindi, used Xcode&rsquo;s right-to-left pseudolanguage, formatted rupees in several locales, and printed exactly what VoiceOver gets from each NPay screen.')
outcomes_slide('3.10', [("globe", "Explain how a localized string is resolved, and when it isn&rsquo;t"),
                        ("db", "Format money by locale without changing its value"),
                        ("diff", "Build layouts that survive right-to-left"),
                        ("eye", "Give VoiceOver meaning, not layout"),
                        ("key", "Add stable accessibility identifiers for UI tests"),
                        ("check", "Inspect an app&rsquo;s accessibility, element by element")])
where_slide('3.10', 'Today: every user, every language', (),
            '3.9: environment values and shared configuration.',
            'Localization, RTL and accessibility testing (Part 2).',
            'Lesson 3.9 used the environment for configuration; locale, layoutDirection and dynamicTypeSize are environment values too. Today they meet localization and accessibility. Part 1 of the text, on VoiceOver basics, Dynamic Type and String Catalogs, was not shared; this deck starts at Section 15. Unit 3 runs to twelve lessons: performance and an integration review follow.',
            'Languages.')

# ================================================================== Part 1 (15, 16)
divider(1, "Localization at runtime", "One screen, three languages", 'Keys resolved against the app&rsquo;s language.', 'The explorer, for real.')
S.append(slide("Part 1 &middot; NPay in three languages (section 15)", "Same structure; different words, different lengths", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;align-items:start">
      {crop("img/loc_en.png", "-AppleLanguages (en)", 300)}
      <div class="step">{crop("img/loc_ta.png", "(ta): Tamil", 300)}</div>
      <div class="step">{crop("img/loc_hi.png", "(hi): Hindi", 300)}</div>
    </div>
    <div class="gap"></div>
    <div class="cols" style="{TWO};gap:20px">
      <div class="step">{card("Observe", ul("The screen&rsquo;s <b>structure</b> is unchanged", "Labels change length: layout must adapt (3.8)"))}</div>
      {card("How we ran it", ul("<code>Localizable.xcstrings</code> compiled into the app", "Launched with <code>-AppleLanguages</code>, <code>-AppleLocale</code>"))}
    </div>
  </div>""", notes(('SAY', 'The text&rsquo;s language explorer, done for real. We wrote a small String Catalog with three keys and their English, Tamil and Hindi values, compiled it into the app with Xcode&rsquo;s xcstringstool, and launched the same lab screen three times with the language and locale passed as launch arguments, the way Xcode&rsquo;s scheme options do. English first.'),
                  ('SAY', 'Click: Tamil: பணம் அனுப்பு for Send Money, and the balance title. Click: Hindi. The translations are ours and should be reviewed by native speakers before real use.'),
                  ('SAY', 'Click: what to observe: the SwiftUI structure did not change at all; only the strings did. But translations change label lengths: the Tamil balance title is noticeably longer. That is why localization and adaptive layout, Lesson 3.8, must work together. Notice the second line on each screen: it did not translate. Next slide.'),
                  ('CONNECT', 'How does a key become a translation?'))))

P = []
for i, (ic, t, sub) in enumerate([("code", "SwiftUI Text", "Text(\"payment.send\")"), ("key", "Localization key", "identifies the resource"), ("globe", "Locale + app language", "choose the localization"), ("file", "Localizable.xcstrings", "translations"), ("eye", "Rendered text", "the resolved string")]):
    x = i * 228
    P.append(tall(x, 0, 208, 112, ic, t, sub, None, ''))
    if i < 4:
        P.append(wire(f'M{x + 210} 56H{x + 226}' + head(x + 226, 56, 'r')))
KEYS = """Text("payment.send")                    // literal: a LocalizedStringKey

let title: String = "payment.send"
Text(title)                             // a String: shown as is

Text(LocalizedStringKey(title))         // explicitly a key"""
S.append(slide("Part 1 &middot; How localization is resolved (section 16)", "A literal is a key; a String is just text", f"""  <div class="body">
    {svg('0 0 1120 112', 'Text, localization key, locale and app language, Localizable.xcstrings, rendered text', 'res', P, 'max-height:118px')}
    <div class="gap"></div>
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px;align-items:start">
      {code("String versus LocalizedStringKey", KEYS, "font-size:11.5px")}
      <div class="step">{tbl(["Line", "en", "ta"], [("literal", "Send Money", "பணம் அனுப்பு"), ("<code>Text(title)</code>", "<b>payment.send</b>", "<b>payment.send</b>"), ("explicit key", "Send Money", "பணம் அனுப்பு")])}
        <p class="small muted" style="margin:6px 0 0">Accessibility labels read from the simulator.</p></div>
    </div>
  </div>""", notes(('SAY', 'The resolution pipeline: Text("payment.send") is interpreted as a LocalizedStringKey; the key identifies a translatable resource; the locale and the app&rsquo;s language decide which localization applies; the catalog supplies the value, with the development-language value as fallback; and the resolved string is rendered.'),
                  ('SAY', 'The important distinction. A string literal passed straight to Text uses SwiftUI&rsquo;s LocalizedStringKey initializer. A String variable uses the verbatim initializer: it is shown as is. To localize a key held in a variable, wrap it: Text(LocalizedStringKey(title)).'),
                  ('SAY', 'Click: our run: the literal and the explicit key resolved, Send Money and பணம் அனுப்பு; the String variable showed "payment.send" in every language. That raw key would also be what VoiceOver reads. It compiles without a warning, so it is easy to ship.'),
                  ('CONNECT', 'Money is the other half of localization.'))))

# ================================================================== Part 2 (17, 18)
divider(2, "Money and locale", "Same amount, local conventions", 'Value, currency and formatting locale are separate.', 'The example.')
CUR = """let amount = Decimal(150050) / Decimal(100)

let india = amount.formatted(
    .currency(code: "INR")
        .locale(Locale(identifier: "en_IN")))

let usa = amount.formatted(
    .currency(code: "INR")
        .locale(Locale(identifier: "en_US")))

print(india)
print(usa)"""
FM = [("en_IN", "₹1,500.50", "₹1,23,45,678.50"), ("en_US", "₹1,500.50", "₹12,345,678.50"), ("ta_IN, hi_IN", "₹1,500.50", ""),
      ("de_DE", "1.500,50 ₹", ""), ("fr_FR", "1 500,50 ₹", ""), ("ar_SA", "١٬٥٠٠٫٥٠ ₹", "")]
S.append(slide("Part 2 &middot; Locale-aware currency formatting (section 17)", "Always INR; the locale decides the look", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,.9fr) minmax(0,1.1fr);gap:22px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("The text&rsquo;s example", CUR, "font-size:12px")}
        <div class="step">{console("Output (Mac)", ["₹1,500.50", "₹1,500.50"], 13)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{tbl(["Locale", "₹1,500.50", "₹12,345,678.50"], FM)}
          <p class="small muted" style="margin:6px 0 0">Authored additions to the run: more locales and a larger amount.</p></div>
        <div class="rule step" data-label="Separate">{ul("Monetary <b>value</b>: paise in the domain", "<b>Currency</b>: INR", "<b>Formatting locale</b>: presentation")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A financial app must keep three things apart: the monetary value, the currency, and the formatting locale. The text&rsquo;s example formats ₹1,500.50 as INR in the en_IN and en_US locales. Click: our run printed ₹1,500.50 twice: at this amount the two look identical.'),
                  ('SAY', 'Click: so we added a larger amount and more locales. At twelve million, en_IN groups in lakhs and crores, ₹1,23,45,678.50, while en_US groups in thousands, ₹12,345,678.50, as Lesson 2.12 showed. German uses a dot for grouping, a comma for decimals and puts the symbol after; French uses a narrow space; Arabic in Saudi Arabia uses Arabic-Indic digits. Every one is the same INR value.'),
                  ('SAY', 'Click: the text&rsquo;s insight: changing the user&rsquo;s language must not change the currency or the monetary value. Localization is presentation; calculations follow the domain model, integer paise.'),
                  ('CONNECT', 'So why not build the string ourselves?'))))

MAN = """Text("₹\\(amount)")                       // avoid

Text(amount,
     format: .currency(code: "INR"))     // prefer"""
S.append(slide("Part 2 &middot; Why not build currency strings manually? (section 18)", "Interpolation drops what formatting knows", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Manual vs formatted", MAN, "font-size:14px")}
        <div class="step">{console("Mac run, same values", ["\"₹\\(amount)\":&ensp;₹1500.5&ensp;&ensp;₹12345678.5", "formatted (en_IN):&ensp;₹1,500.50&ensp;₹1,23,45,678.50"], 12.5)}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("What manual formatting loses", ul("Grouping: no separators at all", "Decimals: the trailing zero vanishes", "Symbol placement and separators by locale", "A clean spoken form for VoiceOver"))}</div>
        <div class="step">{card("NPay", ul("Amounts stay integer paise (2.12)", "Convert to a decimal only to format"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text says to avoid Text("₹\\(amount)") for production money, and to prefer Text with a currency format. Click: what the manual string gives: ₹1500.5 and ₹12345678.5: no grouping, and the trailing zero is gone, so one thousand five hundred rupees and fifty paise reads like fifty paise less. The formatted version: ₹1,500.50 and ₹1,23,45,678.50.'),
                  ('SAY', 'Click: manual formatting gets grouping, decimal separators, currency placement and the accessibility announcement wrong. Click: in NPay amounts remain integer paise, from Lesson 2.12; we convert to a decimal only for formatting, which is what Money.display has done all along.'),
                  ('CONNECT', 'Writing direction.'))))

# ================================================================== Part 3 (19, 20)
divider(3, "Right-to-left", "Leading isn&rsquo;t always left", 'Arabic and Hebrew mirror the layout.', 'The environment value.')
S.append(slide("Part 3 &middot; Right-to-left layout (sections 19&ndash;20)", "The same Home, mirrored", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:150px 150px 150px minmax(0,1fr);gap:16px;align-items:start">
      {PHONE("img/home.png", "Left to right", 150)}
      <div class="step">{PHONE("img/rtl_env.png", "Environment override", 150)}</div>
      <div class="step">{PHONE("img/rtl_pseudo.png", "RTL pseudolanguage", 150)}</div>
      <div style="display:flex;flex-direction:column;gap:10px">
        <div class="step">{console("@Environment(\\.layoutDirection)", ["default:&ensp;&ensp;&ensp;&ensp;leftToRight", "pseudolanguage: rightToLeft"], 12.5)}</div>
        <div class="step">{card("What mirrored", ul("Tabs, quick actions, row layout", "<code>.leading</code> text moved to the right"))}</div>
        <div class="step">{card("What didn&rsquo;t", ul("<code>arrow.up.right</code> still points right", "Directional symbols need checking"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Tamil and Hindi are left-to-right; Arabic and Hebrew are right-to-left. SwiftUI is layout-direction aware, and the direction is an environment value, layoutDirection, leftToRight or rightToLeft.'),
                  ('SAY', 'Left, Home normally. Click: the text&rsquo;s preview technique, applied to the whole app: .environment(\\.layoutDirection, .rightToLeft). Click: and the realistic test: Xcode&rsquo;s right-to-left pseudolanguage, the scheme option that forces RTL writing direction, passed as launch arguments. Both mirror the layout.'),
                  ('SAY', 'Click: under the pseudolanguage the app read layoutDirection as rightToLeft. Click: the tab bar, the quick actions and the transaction rows are mirrored, and everything aligned .leading moved to the right. Click: but the arrow symbols still point up and to the right: not every SF Symbol mirrors, so directional icons need a decision. And the text&rsquo;s point: neither technique replaces testing in a real RTL language.'),
                  ('CONNECT', 'Why leading and trailing.'))))

RT = """.frame(maxWidth: .infinity, alignment: .leading)   // adapts

#Preview("RTL") {
    ContentView()
        .environment(\\.layoutDirection, .rightToLeft)
}"""
S.append(slide("Part 3 &middot; Leading and trailing; test RTL (sections 19&ndash;20)", "Semantic alignment adapts; left and right don&rsquo;t", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("Semantic alignment and an RTL preview", RT, "font-size:13.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        {card("Leading / trailing", ul("Start and end of the reading direction", "Prefer them to hardcoded left/right"))}
        <div class="step">{card("RTL preview", ul("Finds layout assumptions fast"))}</div>
        <div class="warn step" data-label="Not a substitute">{ul("Test the app in a supported RTL language")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', '.frame(maxWidth: .infinity, alignment: .leading) uses semantic alignment: leading means the start of the reading direction, which is the right edge in Arabic. Avoid assuming leading means left; prefer leading and trailing over hardcoded left and right where appropriate. Every NPay alignment so far was semantic, which is why the mirror on the last slide just worked.'),
                  ('SAY', 'Click: the text&rsquo;s RTL preview: the content with the layoutDirection environment set to rightToLeft. Useful for finding layout assumptions. Click: but not a substitute for running the actual app in a supported RTL language, with real translations, fonts and symbol behaviour.'),
                  ('CONNECT', 'Now what VoiceOver hears.'))))

# ================================================================== Part 4 (21, 23)
divider(4, "Accessibility meets localization", "Meaning, not arrangement", 'What VoiceOver actually receives from NPay.', 'A transaction row.')
ROW = """TransactionRow(transaction: transaction)
    .accessibilityElement(children: .ignore)
    .accessibilityLabel(transaction.title)
    .accessibilityValue(
        Money.display(transaction.amountPaise)
    )"""
S.append(slide("Part 4 &middot; Accessibility and localization together (section 21)", "Four fragments, or one meaningful element", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      <div style="display:flex;flex-direction:column;gap:12px">
        {code("Section 21", ROW, "font-size:13.5px")}
        {card("Meaning", ul("Label: <b>what</b>; value: <b>how much</b>", "Both must be localized too"))}
      </div>
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Plain row: elements VoiceOver gets", ["\"arrow.up.right\" [image]", "\"Sent to ravi@npay\" [text]", "\"-₹1,500.50\" [text]", "\"24 Oct\" [text]"], 12.5)}</div>
        <div class="step">{console("With section 21", ["\"Sent to ravi@npay\" value \"-₹1,500.50\""], 12.5)}</div>
        <div class="rule step" data-label="Notice">{ul("Unlabelled SF Symbol: its <b>name</b> is spoken, &ldquo;arrow.up.right&rdquo;")}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'A row shows "Sent to ravi@npay" and ₹1,500.50. The layout may look right, but how will VoiceOver announce it? The text&rsquo;s answer: make the row one accessibility element, ignore its children, and give it a label, the title, and a value, the formatted amount. Label and value must be localized too in a localized app.'),
                  ('SAY', 'Click: we printed the accessibility elements of a plain row: four separate stops: the arrow image, labelled with its symbol name "arrow.up.right"; the title; the amount; and the date. Click: with the Section 21 modifiers: one element, "Sent to ravi@npay", value minus ₹1,500.50.'),
                  ('SAY', 'Click: the symbol name is worth a moment: an SF Symbol without its own label can be announced by its name, which means nothing to a listener, and is never translated. Accessibility text should communicate meaning, not reproduce the visual arrangement.'),
                  ('CONNECT', 'The text&rsquo;s inspection table, measured.'))))

INS = [("BalanceCard", "announces the balance meaningfully", "3 separate texts &rarr; one combined element (ours)"),
       ("Send Money / quick actions", "announces its action", "&ldquo;Send&rdquo;, &ldquo;Request&rdquo;, &ldquo;History&rdquo; [button]"),
       ("Payment TextField", "has a meaningful label", "<b>empty label</b>; placeholder &ldquo;Recipient ID&rdquo; as value"),
       ("Transaction row", "announces transaction details", "&ldquo;Coffee Shop&rdquo; value &ldquo;-₹250.00&rdquo;"),
       ("Success screen", "not only animation", "checkmark read as <b>&ldquo;Selected&rdquo;</b>; the text carries it"),
       ("Tab bar", "meaningful tab labels", "Home, Payments, History, Profile [button, selected]")]
S.append(slide("Part 4 &middot; Accessibility inspection (section 23)", "Expected vs what NPay exposes", f"""  <div class="body">
    {tbl(["Component", "Expected", "Measured (elements printed in the simulator)"], INS, 'tbl compact')}
    <div class="gap"></div>
    <div class="step">{card("Two fixes to make", ul("TextFields: a real label &middot; the checkmark: a meaningful label, or hide it"))}</div>
  </div>""", notes(('SAY', 'The text&rsquo;s inspection table, with what NPay actually exposes. BalanceCard: three separate texts, until our integration combined them into one element. The quick actions announce their action as buttons. The payment TextFields: an empty label, with the placeholder as their value; when the user has typed, the placeholder is gone, so VoiceOver has only the typed text. Transaction rows: one element with label and value, after Section 21.'),
                  ('SAY', 'The success screen: the checkmark image is announced as "Selected", the symbol&rsquo;s built-in meaning, which is wrong here; success is carried by the "Payment Recorded" text, which is exactly why success must not rely only on a green animated checkmark. The tab bar exposes meaningful labels and the selected state.'),
                  ('SAY', 'Click: two fixes to make: real labels for the fields, and a proper label for the checkmark, or hide it since the text says it all. Tools: VoiceOver in the simulator to hear the order, and Apple&rsquo;s Accessibility Inspector for labels, values, traits and relationships. We printed the same information from inside the app.'),
                  ('CONNECT', 'A reusable accessible action.'))))

# ================================================================== Part 5 (22, 24)
divider(5, "Built for every user", "Localized titles, stable identifiers", 'A design-system action and a test contract.', 'NPayActionButton.')
AB = """struct NPayActionButton: View {
    let title: LocalizedStringKey
    let symbol: String
    let accessibilityID: String
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(title, systemImage: symbol)
                .font(.headline)
                .frame(maxWidth: .infinity)
                .padding()
        }
        .buttonStyle(.borderedProminent)
        .accessibilityIdentifier(accessibilityID)
    }
}

NPayActionButton(title: "payment.send",
                 symbol: "arrow.up.right",
                 accessibilityID: "npay.sendPayment") {
    print("Send Money tapped")
}"""
S.append(slide("Part 5 &middot; A reusable accessible NPay action (section 22)", "Translated title; identifier never spoken", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1fr) minmax(0,.85fr);gap:22px;align-items:start">
      {code("NPayActionButton", AB, "font-size:11.5px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Simulator, Tamil", ["\"பணம் அனுப்பு\" [button] id npay.sendPayment"], 12.5)}</div>
        {card("<code>LocalizedStringKey</code>", ul("&ldquo;payment.send&rdquo; is looked up, not shown", "A <code>String</code> parameter would show the key (Part 1)"))}
        <div class="step">{card("<code>accessibilityIdentifier</code>", ul("Stable, for UI automation", "<b>Not</b> spoken by VoiceOver"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text adds an accessible action to the design system: NPayActionButton takes its title as a LocalizedStringKey, a symbol, an accessibility identifier and an action, and renders a bordered-prominent Button with a Label.'),
                  ('SAY', 'Click: run in Tamil, the element is "பணம் அனுப்பு", a button, with the identifier npay.sendPayment. Why LocalizedStringKey? So the literal "payment.send" at the call site is looked up; had the parameter been a String, we would see the key, as Part 1 showed.'),
                  ('SAY', 'Click: why accessibilityIdentifier? It gives UI automation a stable identifier that does not change with the language. It is not a spoken label: VoiceOver reads the localized title; tests find the identifier. Two audiences, two properties.'),
                  ('CONNECT', 'Identifiers across NPay.'))))

ID = """enum NPayAccessibilityID {
    static let balanceCard = "npay.balanceCard"
    static let recipientField = "npay.recipientField"
    static let amountField = "npay.amountField"
    static let sendButton = "npay.sendButton"
    static let transactionList = "npay.transactionList"
}

TextField("Recipient", text: $recipient)
    .accessibilityIdentifier(NPayAccessibilityID.recipientField)"""
S.append(slide("Part 5 &middot; Identifiers for future UI tests (section 24)", "One enum, used everywhere", f"""  <div class="body">
    <div class="cols" style="{TWO};gap:24px;align-items:start">
      {code("App/NPayAccessibilityID.swift", ID, "font-size:12px")}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{console("Integrated NPay (simulator)", ["Home:&ensp;&ensp;&ensp;\"Available Balance, ₹25,000.00, …\" id npay.balanceCard", "Payments: \"\" value \"Recipient ID\" id npay.recipientField", "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;\"\" value \"Amount (₹)\" id npay.amountField", "&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;\"Review Payment\" [button] id npay.sendButton", "History:&ensp;&ensp;id npay.transactionList"], 11.5)}</div>
        <div class="step">{card("Why an enum", ul("One spelling, shared by the app and its tests", "Unit 9 writes the UI tests that use them"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'The text defines stable identifiers in one enum, NPayAccessibilityID: the balance card, the recipient and amount fields, the send button and the transaction list, and applies them consistently, for example on the recipient TextField.'),
                  ('SAY', 'Click: our integration applies all five, flagged as ours; printed from the running app: the combined balance card, both fields, the Review Payment button as the send button, and the History list. Note again the fields&rsquo; empty labels: identifiers help tests, not VoiceOver users.'),
                  ('SAY', 'Click: why an enum: tests and app share one spelling, so a typo is a compile error, not a flaky test. Unit 9 writes the UI automation tests that use these identifiers.'),
                  ('CONNECT', 'What changed in NPay.'))))

# ================================================================== Part 6 (integration, status)
divider(6, "NPay after Lesson 3.10", "Accessible by default", 'Identifiers, grouping, row descriptions.', 'The changes.')
CH = [("App/NPayAccessibilityID.swift", "the section 24 enum"), ("BalanceCard", "<code>.accessibilityElement(children: .combine)</code> + identifier"),
      ("TransactionRow", "section 21: one element, label and value"), ("PaymentsScreen", "identifiers on both fields and Review Payment"),
      ("HistoryScreen", "identifier on the List")]
S.append(slide("Part 6 &middot; NPay after Lesson 3.10 (integration, authored)", "Five small changes", f"""  <div class="body">
    <div class="cols" style="grid-template-columns:minmax(0,1.2fr) minmax(0,.8fr);gap:22px;align-items:start">
      {tbl(["File", "Change"], CH, 'tbl')}
      <div style="display:flex;flex-direction:column;gap:12px">
        <div class="step">{card("Not yet", ul("Field labels; the checkmark label", "Localizing the whole app: our catalog has three keys"))}</div>
        <div class="step">{card("Unit 3 status (from the text)", ul("Twelve lessons: next 3.11 Performance, then 3.12 Integration &amp; review"))}</div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Our integration, flagged as ours: the NPayAccessibilityID enum; BalanceCard combined into one element with an identifier; TransactionRow described with the Section 21 label and value, applied inside the component so Home and History both benefit; identifiers on the payment fields, the Review Payment button and the History list.'),
                  ('SAY', 'Click: not done yet: real labels for the text fields and the checkmark, the two problems we measured; and localizing the whole app, since our catalog only holds the three keys of the lab. Click: the text&rsquo;s status: Unit 3 runs to twelve lessons; 3.11 on performance and 3.12, a complete integration and architecture review, are next.'),
                  ('CONNECT', 'The recap.'))))

# ================================================================== wrap-up
recap_u1('3.10', (), [("globe", "Keys resolve; Strings don&rsquo;t", "literals and LocalizedStringKey are looked up"),
                      ("db", "Locale formats, never changes, money", "INR stays INR; paise stay paise"),
                      ("eye", "Meaning for every user", "leading/trailing; one element per idea; stable identifiers")],
          'Three things to remember. A string literal in Text is a localization key resolved against the app&rsquo;s language, but a String variable is shown as is unless you wrap it in LocalizedStringKey. Locale-aware formatting changes how money looks, lakhs or thousands, symbol first or last, never its value or currency. And build for every user: semantic leading and trailing so layouts mirror, accessibility elements that carry meaning rather than layout, labels for every field and symbol, and stable identifiers for tests that VoiceOver never speaks.')

review_divider(10)
review([("layers", "Question", "Is every SwiftUI container a separate VoiceOver element?",
         "Does VoiceOver necessarily expose every SwiftUI layout container as a separate element?", "No",
         "Our Home exposed texts, buttons and combined elements, no stacks.",
         "Picturing the view tree as the accessibility tree.", "Some say yes.", None),
        ("key", "Choose one", "What is accessibilityIdentifier for?",
         "What is the purpose of <code>accessibilityIdentifier</code>?<br>A. Spoken VoiceOver label<br>B. Stable programmatic identification<br>C. Currency formatting", "B",
         "npay.sendPayment stayed the same in Tamil; the label changed.",
         "Using identifiers as labels.", "Most pick B.", None),
        ("db", "Question", "Should changing NPay's language change its monetary values?",
         "Should changing NPay&rsquo;s language change its underlying monetary values?", "No",
         "₹1,500.50 in every locale we tried; only the format differs.",
         "Converting currency with the language.", "Most say no.", None),
        ("diff", "Choose one", "Why prefer leading and trailing alignment?",
         "Why prefer <code>.leading</code> and <code>.trailing</code> alignment?<br>A. They are always faster<br>B. They disable localization<br>C. They adapt to semantic layout direction", "C",
         "Our Home mirrored correctly under the RTL pseudolanguage.",
         "Hardcoding left and right.", "Most pick C.", None),
        ("code", "Question", "Is a LocalizedStringKey equivalent to every String?",
         "Is a <code>LocalizedStringKey</code> equivalent to every ordinary <code>String</code>?", "No",
         "<code>Text(title)</code> with a String showed &ldquo;payment.send&rdquo;.",
         "Assuming every string is looked up.", "Some say yes.", None),
        ("check", "Question", "Should payment success rely only on a green animated checkmark?",
         "Should payment success rely only on a green animated checkmark?", "No",
         "VoiceOver read the checkmark as &ldquo;Selected&rdquo;; the text carried the meaning.",
         "Communicating with colour and motion alone.", "Most say no.", None),
        ("globe", "Predict the result", "let title = \"payment.send\"; Text(title) in Tamil?",
         "<code>let title: String = \"payment.send\"</code>, then <code>Text(title)</code>, with the app in Tamil and a Tamil translation in the catalog. What appears?<br>A. பணம் அனுப்பு<br>B. payment.send<br>C. Send Money", "B",
         "A String uses the verbatim initializer; wrap it in LocalizedStringKey.",
         "Expecting variables to be localized.", "Many pick A.", None),
        ("eye", "Predict the result", "How is Image(systemName: \"checkmark.circle.fill\") announced?",
         "With no label of your own, how did VoiceOver get NPay&rsquo;s success checkmark?<br>A. &ldquo;Payment successful&rdquo;<br>B. &ldquo;Selected&rdquo;<br>C. Nothing", "B",
         "The symbol&rsquo;s built-in meaning, not ours: label it or hide it.",
         "Trusting icons to speak for themselves.", "Some pick A.", None),
        ("frame", "Predict the result", "₹12,345,678.50 in en_IN?",
         "<code>.currency(code: \"INR\")</code> in the <code>en_IN</code> locale formats 12,345,678.50 as&hellip;<br>A. ₹12,345,678.50<br>B. ₹1,23,45,678.50<br>C. 12.345.678,50 ₹", "B",
         "Lakhs and crores; en_US gives A, de_DE gives C.",
         "Assuming one grouping style.", "Some pick A.", None),
        ("layers", "Choose one", "From 3.9: who supplies layoutDirection to a view?",
         "From Lesson 3.9: where does <code>@Environment(\\.layoutDirection)</code> get its value?<br>A. A global variable<br>B. The view&rsquo;s position in the hierarchy (its ancestors)<br>C. The view&rsquo;s initializer", "B",
         "Like colorScheme: the nearest ancestor&rsquo;s value; the pseudolanguage set it at the root.",
         "Treating environment values as globals.", "Most pick B.", "Spaced review from Lesson 3.9.")])

S.append(next_slide('3.10', [("3.11", "SwiftUI performance, lazy loading &amp; profiling", "LazyVStack, body evaluations, Instruments, NPay&rsquo;s history"),
                             ("3.12", "Unit 3 integration &amp; architecture review", "the complete app, reviewed"),
                             ("Unit 9", "Testing", "UI tests that use NPayAccessibilityID")],
                    'Lesson 3.11 investigates rendering performance with NPay&rsquo;s transaction history: LazyVStack, unnecessary body evaluations and Instruments. Lesson 3.12 integrates and reviews the whole of Unit 3. Unit 9 writes the UI automation tests that rely on today&rsquo;s identifiers.'))

S.append(lab_slide('3.10', "Every user, every language", "Localize a screen; mirror it; listen to it.",
                   ["Add a String Catalog with English and one more language.",
                    "Compare <code>Text(\"key\")</code>, <code>Text(title)</code>, <code>LocalizedStringKey</code>.",
                    "Format ₹12,345,678.50 in three locales.",
                    "Run with the RTL pseudolanguage; find what didn&rsquo;t mirror.",
                    "Turn on VoiceOver; walk Home and Payments.",
                    "Fix the field labels and the checkmark."],
                   "", 'Expected, as in our run: the literal and LocalizedStringKey translate, the String variable shows its key; lakh grouping in en_IN; layout mirrors but directional arrows don&rsquo;t; VoiceOver hears empty labels on the fields and &ldquo;Selected&rdquo; for the checkmark until you fix them.',
                   side=f'<div>{card("You hand in", ul("Screenshots in two languages and RTL", "Your accessibility element list for Payments", "The two fixes, with before and after"))}</div>'))

end_slide('3.10', 'Accessibility &amp;<br>Localization', 'Lesson 3.11 &mdash; SwiftUI Performance, Lazy Loading &amp; Profiling',
          'You can now explain how localized strings resolve and when they don&rsquo;t, format money by locale without changing it, build layouts that mirror for right-to-left, give VoiceOver meaningful elements, add stable identifiers for tests, and inspect what an app really exposes.',
          'Next, Lesson 3.11: SwiftUI performance, lazy loading and profiling, using NPay&rsquo;s transaction history.')

write_deck(OUT310, '3.10', 'Accessibility &amp; Localization', 'Accessibility &amp; Localization')
