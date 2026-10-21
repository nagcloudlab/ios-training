"""Generates decks/lesson-0.9/index.html from the Lesson 0.9 text only (PocketBank -> NPay)."""
import html, os, re, sys
OUT09 = sys.argv[1]
sys.argv = ['x', '/dev/null']
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
cues = lambda n: '<i class="step cue"></i>' * n
fade = lambda l, inner: f'<g class="fade" data-lit="{l}">{inner}</g>'
box = lambda x, y, w, h, t, sub='', l=None, cls='', icon='': row(x, y, w, h, icon, t, sub, l, cls)


def divider(n, title, lead, say, con):
    S.append(f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(('SAY', say), ('CONNECT', con))}</section>

""")


def chooser(items, top, chip_w, gap, label, tid, title):
    P = []
    last = len(items) - 1
    for i, (chip, *_r) in enumerate(items):
        P.append(box(i * (chip_w + gap), 0, chip_w, 52, chip, '', str(i) if i < last else f"{i}+"))
    for i, (chip, t, d, cls) in enumerate(items):
        P.append(fade(str(i) if i < last else f"{i}+", f'<text class="mono" x="0" y="{top}">{label}</text>' + box(0, top + 14, 1136, 66, t, d, None, cls)))
    return svg(f"0 0 1136 {top + 82}", title, tid, P)


S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.9</p>
    <h1 style="font-size:54px;line-height:1.05">iOS Data Storage<br>Architecture</h1>
    <p class="lead" style="max-width:680px">The user closes NPay, switches apps or restarts the iPhone. <b>What happens to the data?</b></p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'In Lesson 0.8, NPay fetched a balance from the server. Now the user closes the app, switches to another app or restarts the iPhone. Does the balance disappear? Does iOS save everything automatically? Where should we store login tokens, preferences, transaction records and downloaded images? Today: how iOS stores data and how to choose the right mechanism.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")
outs = [("memory", "<b>RAM</b> versus <b>persistent storage</b>"), ("layers", "Why UserDefaults, SwiftData, files and Keychain <b>differ</b>"),
        ("lock", "How the <b>sandbox</b> affects file access"), ("cross", "Why important data must survive <b>termination</b>"),
        ("clock", "Why cached financial data is <b>not authoritative</b>"), ("shield", "How storage choices shape <b>security</b> and architecture")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.9 &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six things you should be able to explain by the end of this lesson.'), ('CONNECT', 'Start with a simple story.'))))

# ================================================================== 1
divider(1, "Start with a simple story", "Showing data is not saving data",
        "NPay receives a balance from the server and displays it. Two different things are happening.", "Look at the response.")
JSON = '''{
  "accountId": "A1001",
  "balance": 25000,
  "currency": "INR"
}'''
P = [box(0, 0, 270, 100, "RAM", "runtime state and objects", '1', '', 'memory'), box(310, 0, 270, 100, "Persistent storage", "files, databases, preferences", '2', '', 'db'),
     fade("1+", '<text class="mono" x="20" y="130">TEMPORARY</text>'), fade("2+", '<text class="mono" x="330" y="130">DURABLE</text>')]
S.append(slide("Part 1 &middot; Memory vs storage", "Two different operations", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    <div>
      <div class="cw"><div class="ch"><span>response.json</span></div><pre class="tree" style="font-size:18px;border-radius:0 0 12px 12px">{E(JSON)}</pre></div>
      <div class="gap"></div>
      <p class="small">NPay displays <b>&#8377;25,000</b>. It holds the data <b>in memory</b> to draw the screen, and <b>may</b> persist selected data for later.</p>
    </div>
    <div>
      {svg("0 0 580 140", "RAM holds temporary runtime state; persistent storage holds durable files, databases and preferences", "s4mem", P)}
      {cues(2)}
      <div class="gap"></div>
      <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-book"/></svg></div>
        <p><b>RAM</b> is a classroom <b>whiteboard</b>; <b>storage</b> is a <b>notebook</b>. Don&rsquo;t assume the whiteboard survives the session.</p></div>
    </div>
  </div>""", notes(('SAY', 'NPay receives this response and shows &#8377;25,000. Two different things happen: the app holds data in memory to display the screen, and it may persist selected data to storage for later. These are not the same operation.'),
                  ('SAY', 'RAM is like a classroom whiteboard: convenient for current work, but you cannot assume it survives after the session ends. Persistent storage is a notebook. An app should not rely on process memory for anything that must survive termination.'),
                  ('CONNECT', 'iOS offers several kinds of notebook.'))))

# ================================================================== 2
divider(2, "The major storage choices", "Different needs, different mechanisms",
        "iOS provides several storage mechanisms, each designed for different needs.", "Here are the four main ones.")
P = [box(368, 0, 400, 56, "NPay application", "", None, '', 'bank'), wire('M568 56V78M143 78H993M143 78V96M425 78V96M711 78V96M993 78V96')]
for i, (ic, t, sub) in enumerate([("gear", "UserDefaults", "preferences"), ("db", "SwiftData", "structured app data"), ("folder", "FileManager", "documents and files"), ("key", "Keychain", "credentials and secrets")]):
    P.append(tall(i * 286, 102, 266, 104, ic, t, sub, str(i + 1)))
S.append(slide("Part 2 &middot; Storage architecture &middot; conceptual", "iOS storage choices", f"""  <div class="body">
    {svg("0 0 1136 208", "NPay uses UserDefaults for preferences, SwiftData for structured data, FileManager for files and Keychain for secrets", "s6choices", P)}
    {cues(4)}
    <div class="gap"></div>
    <p class="small muted">Also: Core Data, SQLite, caches, cloud synchronization and other specialized mechanisms.</p>
    <div class="rule step" data-label="The real question">Not &ldquo;which storage API is best?&rdquo; but <b>&ldquo;what kind of data is this, and what guarantees does it need?&rdquo;</b></div>
  </div>""", notes(('SAY', 'Click through: UserDefaults for preferences, SwiftData for structured app data, FileManager for documents and files, Keychain for credentials and secrets. There are more, including Core Data, SQLite, caches and cloud sync.'),
                  ('SAY', 'The important question is not which storage API is best. It is: what kind of data am I storing, and what guarantees does it need?'),
                  ('CONNECT', 'Start with the simplest: UserDefaults.'))))

# ================================================================== 3
divider(3, "UserDefaults", "Lightweight preferences",
        "NPay lets the user choose dark mode. The selected appearance is a small preference.", "Here is how to store it.")
UD = '''import Foundation

// Save a preference
UserDefaults.standard.set(
    true,
    forKey: "darkModeEnabled"
)

// Read a preference
let darkMode = UserDefaults.standard.bool(
    forKey: "darkModeEnabled"
)

print(darkMode)'''
S.append(slide("Part 3 &middot; UserDefaults", "Saving a preference", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("Settings.swift", UD, "font-size:16px")}
    <div>
      <div class="card accent step"><span class="label">Good for</span><p class="small" style="margin:0">Selected theme, onboarding completion, preferred language, simple app settings.</p></div>
      <div class="gap"></div>
      <div class="card step"><span class="label">Avoid for</span><p class="small" style="margin:0">Large structured datasets, or as a <b>secure credential store</b>.</p></div>
    </div>
  </div>""", notes(('SAY', 'Saving and reading a boolean preference is one line each. UserDefaults suits small settings: theme, onboarding completion, preferred language, simple app settings.'),
                  ('SAY', 'Avoid it as a database for large structured data, and never as a store for credentials.'),
                  ('CONNECT', 'What about many structured records?'))))

# ================================================================== 4
divider(4, "SwiftData", "Structured application data",
        "NPay wants to store locally saved transaction notes: create, read, update and delete records. That suits a persistence framework such as SwiftData.", "See how it fits.")
NOTE = '''import Foundation
import SwiftData

@Model
final class TransactionNote {
    var title: String
    var amount: Decimal

    init(title: String, amount: Decimal) {
        self.title = title
        self.amount = amount
    }
}'''
P = []
for i, (ic, t) in enumerate([("phone", "SwiftUI screen"), ("layers", "SwiftData ModelContext"), ("db", "Persistent model storage")]):
    P.append(box(0, i * 76, 400, 56, t, '', str(i + 1), '', ic))
    if i < 2:
        P.append(wire(f'M200 {i * 76 + 56}V{i * 76 + 70}{head(200, i * 76 + 70, "d")}'))
S.append(slide("Part 4 &middot; SwiftData", "A persistent model", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    <div>
      {svg("0 0 400 208", "SwiftUI screen, SwiftData ModelContext, persistent model storage", "s10sd", P)}
      {cues(3)}
      <div class="gap"></div>
      <div class="rule step" data-label="Not magic">SwiftData is not an in-memory array that saves itself. Learn <b>containers</b>, <b>contexts</b>, relationships, schema evolution and save behavior.</div>
    </div>
    {code("TransactionNote.swift", NOTE, "font-size:16px")}
  </div>""", notes(('SAY', 'The SwiftUI screen works through a SwiftData ModelContext, which persists to model storage. @Model marks TransactionNote as a persistent model; SwiftData manages persistence through its model container and context.'),
                  ('SAY', 'SwiftData is not simply an in-memory array that automatically saves every variable. Developers still need to understand model containers, contexts, relationships, schema evolution and save behavior.'),
                  ('CONNECT', 'Some data is naturally a file, not a record.'))))

# ================================================================== 5
divider(5, "Files", "Documents, images and downloaded content",
        "NPay may download a PDF account statement. Some data is naturally a file rather than a database record.", "Where do files go?")
FM = '''import Foundation

let documents = FileManager.default.urls(
    for: .documentDirectory,
    in: .userDomainMask
).first!

let statementURL = documents.appendingPathComponent(
    "statement.pdf"
)'''
S.append(slide("Part 5 &middot; Sandbox directories", "Where an app keeps its files", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.05fr">
    <div>
      <table class="tbl" style="font-size:19px">
        <tr><th>Directory</th><th>Typical purpose</th></tr>
        <tr><td>Documents</td><td>User documents, persistent app files</td></tr>
        <tr><td>Application Support</td><td>App-managed support files</td></tr>
        <tr class="hl"><td>Caches</td><td>Re-creatable cached content</td></tr>
        <tr class="hl"><td>Temporary</td><td>Short-lived temporary files</td></tr>
      </table>
      <div class="gap"></div>
      <div class="rule step">The system can remove cached and temporary content. Don&rsquo;t treat those directories as <b>permanent</b>.</div>
    </div>
    <div>
      {code("Statement.swift", FM, "font-size:15px")}
      <p class="small muted" style="margin:8px 0 0">This builds a destination URL; it does not download or write the PDF.</p>
    </div>
  </div>""", notes(('SAY', 'Apps have directories inside their sandbox. Documents for user documents and persistent files; Application Support for app-managed support files; Caches for content that can be re-created; Temporary for short-lived files. The system can remove cached and temporary content.'),
                  ('SAY', 'The code asks FileManager for the Documents directory and builds a URL for statement.pdf. It only builds the location; it does not download or write the file.'),
                  ('CONNECT', 'And the most sensitive data: credentials.'))))

# ================================================================== 6
divider(6, "Keychain", "Sensitive data",
        "We met the Keychain in Lesson 0.7. Now connect it to storage choices.", "Choose the right home for four pieces of data.")
pick = [("Dark mode", "UserDefaults", "A lightweight, non-secret preference.", 'lit'),
        ("Auth token", "Keychain", "A sensitive credential that needs security controls.", 'lit'),
        ("PDF statement", "Files (FileManager)", "A document; may also need file protection and retention policies.", 'lit'),
        ("Transaction notes", "SwiftData", "Structured records to create, read, update and delete.", 'lit')]
S.append(slide("Part 6 &middot; Choose the storage", "Which storage for which data?", f"""  <div class="body">
    {chooser(pick, 104, 270, 18.7, "BEST FIT", "s16pick", "Dark mode goes in UserDefaults, the authentication token in the Keychain, the PDF statement in files, transaction notes in SwiftData")}
    {cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Directory is not security">Sensitive financial documents may also need <b>file protection</b>, encryption and retention policies.</div>
  </div>""", notes(('SAY', 'Dark mode: UserDefaults, a lightweight non-secret preference. Click: the authentication token is not a preference, it is a sensitive credential, so Keychain. Click: a downloaded PDF statement is a file. Click: locally saved transaction notes are structured records, so SwiftData.'),
                  ('ASK', 'Before each click: where would you put it?'),
                  ('EXPECT', 'Most get dark mode and the token. The PDF and notes show why "file" and "record" are different shapes of data.'),
                  ('SAY', 'Choosing a directory alone is not sufficient security for sensitive documents: file protection, encryption and retention policies matter too.'),
                  ('CONNECT', 'What happens to unsaved data when iOS ends the app?'))))

# ================================================================== 7
divider(7, "When the app is terminated", "Revisiting Lesson 0.3",
        "The user has typed a transaction note but not pressed Save. Then iOS terminates the process.", "Two versions of the same story.")
P = []
scen = [("No save", "Draft only in memory", "Terminate, relaunch: the note is gone.", 'alert'),
        ("Saved draft", "Draft persisted", "Terminate, relaunch: the note comes back.", 'lit')]
for i, (chip, *_r) in enumerate(scen):
    P.append(box(i * 300, 0, 280, 52, chip, '', str(i) if i == 0 else "1+"))
P.append('<g class="nd"><rect class="sh" x="0" y="80" width="580" height="60" rx="12"/><text class="mono" x="20" y="104">TRANSFER NOTE</text><text x="20" y="128">Rent payment</text></g>')
for i, (_c, t, d, cls) in enumerate(scen):
    P.append(fade(str(i) if i == 0 else "1+", box(0, 160, 580, 66, t, d, None, cls)))
S.append(slide("Part 7 &middot; Termination &middot; conceptual", "A draft that may not survive", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {svg("0 0 580 228", "A transfer note draft: with no save it is lost on termination; with a saved draft it survives relaunch", "s19draft", P)}
    {cues(1)}
    <div>
      <div class="rule" data-label="Principle">Persist important data <b>before</b> the app can lose its memory. Do not depend on a final termination callback.</div>
      <div class="gap"></div>
      <p class="small step">For drafts, save <b>periodically</b> or on meaningful changes, minding performance, security and consistency.</p>
    </div>
  </div>""", notes(('SAY', 'The user types "Rent payment" as a transfer note. In the first version it exists only in memory: when iOS terminates the process and the user relaunches, it is gone. Click: in the second version the draft was saved, so it comes back.'),
                  ('SAY', 'Important data should be persisted before the app can lose its in-memory state. Do not rely on a termination callback; save periodically or when meaningful changes happen.'),
                  ('CONNECT', 'Saved data raises a different question for a bank: is it still true?'))))

# ================================================================== 8
divider(8, "Cache versus source of truth", "Especially important for banking",
        "NPay previously showed &#8377;25,000. The user reopens it while offline. Can it show the old balance?", "Possibly, but carefully.")
P = [box(0, 0, 540, 110, "Cached balance: &#8377;25,000", "last updated earlier", None, '', 'clock'),
     fade("1+", box(596, 0, 540, 110, "Current verified balance: unavailable", "offline", None, 'alert', 'cross'))]
S.append(slide("Part 8 &middot; Freshness &middot; conceptual", "Cached is not current", f"""  <div class="body">
    {svg("0 0 1136 112", "A cached balance of 25,000 rupees last updated earlier, next to a current verified balance that is unavailable offline", "s22cache", P)}
    {cues(1)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Communicate freshness">Never present <b>stale</b> financial data as current. The <b>backend</b> stays authoritative; local storage improves usability but does not replace server validation.</div>
  </div>""", notes(('SAY', 'The app can show the cached &#8377;25,000, but it must say it was last updated earlier. Click: the current verified balance is unavailable while offline.'),
                  ('SAY', 'Communicate data freshness clearly. The backend remains authoritative for balances and transactions; local storage helps usability but does not replace server-side validation.'),
                  ('CONNECT', 'Finally, the persistence technologies you will hear about.'))))

# ================================================================== 9
divider(9, "SwiftData vs Core Data vs SQLite", "Different abstraction levels",
        "These technologies are related but work at different levels.", "Compare them.")
S.append(slide("Part 9 &middot; Comparison", "Four persistence technologies", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Technology</th><th>What it provides</th></tr>
      <tr><td><b>SwiftData</b></td><td>Swift-native persistence framework with model-oriented APIs</td></tr>
      <tr><td><b>Core Data</b></td><td>Mature object graph management and persistence framework</td></tr>
      <tr><td><b>SQLite</b></td><td>Embedded relational database engine</td></tr>
      <tr><td><b>FileManager</b></td><td>Filesystem operations, not database object management</td></tr>
    </table>
    <div class="gap"></div>
    <div class="cols">
      <div class="card accent step"><span class="label">New SwiftUI app</span><p class="small" style="margin:0"><b>SwiftData</b> is often a good start, when its capabilities and deployment targets fit.</p></div>
      <div class="card accent step"><span class="label">Existing or advanced</span><p class="small" style="margin:0"><b>Core Data</b> remains important for existing apps and advanced requirements.</p></div>
    </div>
  </div>""", notes(('SAY', 'SwiftData is a Swift-native framework with model-oriented APIs. Core Data is a mature object-graph and persistence framework. SQLite is an embedded relational database engine. FileManager does filesystem operations, not database object management.'),
                  ('SAY', 'SwiftData and Core Data can use SQLite-backed stores, but their programming models are not the same as writing SQL. For a new SwiftUI app, SwiftData is often a good start; Core Data remains important for existing apps and advanced needs.'),
                  ('CONNECT', "Let's check your understanding."))))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Four questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("memory", "Does <code>@State</code> automatically guarantee data survives app termination?", "No",
       "@State lives with the running app. Data that must survive termination needs persistent storage.", "Confusing view state with saved data.", "Some say yes."),
      ("key", "Should authentication tokens normally be stored in UserDefaults?", "No",
       "Tokens are credentials: they belong in the Keychain, with its security controls.", "Storing secrets where preferences go.", "Most say no; ask why."),
      ("folder", "Can iOS remove files stored in a cache directory?", "Yes",
       "Cached and temporary content can be removed by the system. Keep only re-creatable data there.", "Treating Caches as permanent storage.", "Many say no."),
      ("bank", "Should a banking app present stale cached balances as verified live balances?", "No",
       "Show freshness clearly. The backend is authoritative; a cache only improves usability.", "Showing old numbers as if current.", "Most say no; discuss how to show freshness.")]
N = len(QA)
for i, (ic, q, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    title = html.unescape(re.sub('<[^>]+>', '', q))
    S.append(f"""<section class="slide question" data-title="{E(title, quote=True)}">
  <div class="q-top">
    <p class="kicker">Check your understanding &middot; {i + 1} of {N}</p>
    <div class="q-dots" aria-hidden="true">{dots}</div>
  </div>
  <div class="body">
    <div class="q-row">
      <div class="q-card">
        <div class="q-icon"><svg viewBox="0 0 24 24"><use href="#i-{ic}"/></svg></div>
        <span class="label">Question</span>
        <p class="q-text">{q}</p>
      </div>
      <div class="q-panel">
        <div class="q-ans step anim-up">
          <span class="q-verdict">{v}</span>
          <p class="q-why">{why}</p>
          <p class="q-trap"><b>Common trap:</b> {trap}</p>
        </div>
      </div>
    </div>
  </div>
""" + notes(('ASK', 'Give everyone a few seconds, then take a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next question.' if i < N - 1 else 'That completes the lesson.')) + "</section>\n\n")

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.9 complete</p>
    <h2>iOS Data Storage<br>Architecture</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: complete iOS architecture, end to end</p>
  </div>
""" + notes(('SAY', 'You can now explain RAM versus persistent storage, why UserDefaults, SwiftData, files and Keychain serve different purposes, how sandboxing affects file access, why important data must survive termination, why cached financial data is not authoritative, and how storage choices shape security and architecture.'),
            ('SAY', 'Next, Lesson 0.10, our final foundation lesson: we follow NPay through a complete journey, from the tap and process launch through the SwiftUI screen, a button event, an API request, secure authentication, data storage, backgrounding, suspension and relaunch, and build one complete architecture diagram.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.9 — iOS Data Storage Architecture</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.9 — iOS Data Storage Architecture">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT09, 'w').write(doc)
print(len(S), 'slides')
