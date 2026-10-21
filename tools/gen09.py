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
  </div>""", notes(('SAY', 'Six things you should be able to explain by the end of this lesson.'), ('CONNECT', 'First, where today sits on the NPay map.'))))
S.append(map_slide('0.9', 'Today: where NPay keeps its data', ('storage', 'keychain'),
                   'Lesson 0.8: a Refresh travels Service &rarr; URLSession &rarr; HTTPS &rarr; bank, and returns as JSON decoded into a model.',
                   'Where data lives so it survives termination: UserDefaults, SwiftData, files and the Keychain.',
                   'Last time the balance travelled from the bank into NPay&rsquo;s memory. Today we look down the map at Storage and the Keychain: what has to survive when that memory is gone, and where each kind of data belongs.',
                   'Start with a simple story.'))

# ================================================================== 1
divider(1, "Start with a simple story", "Showing data is not saving data",
        "NPay receives a balance from the server and displays it. Two different things are happening.", "Look at the response.")
JSON = '''{
  "accountId": "A1001",
  "balanceMinor": 2500000,
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
      <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div>
        <p>In the <b>kitchen</b>: RAM is the <b>counter</b> the chef works on, cleared when the kitchen closes. Storage is the <b>pantry</b>: what is still there tomorrow.</p></div>
    </div>
  </div>""", notes(('SAY', 'NPay receives this response and shows &#8377;25,000. Two different things happen: the app holds data in memory to display the screen, and it may persist selected data to storage for later. These are not the same operation.'),
                  ('SAY', 'The balance arrives as balanceMinor, 2,500,000 paise, and the ViewModel formats it as &#8377;25,000. Back in our restaurant kitchen: RAM is the counter the chef works on, convenient for the current order but cleared when the kitchen closes. Persistent storage is the pantry. An app should not rely on process memory for anything that must survive termination.'),
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
      <div class="card step"><span class="label">Avoid for</span><p class="small" style="margin:0">Large structured datasets, or as a <b>secure credential store</b>. Tokens go in the Keychain (Lesson 0.7).</p></div>
    </div>
  </div>""", notes(('SAY', 'Saving and reading a boolean preference is one line each. UserDefaults suits small settings: theme, onboarding completion, preferred language, simple app settings.'),
                  ('SAY', 'Avoid it as a database for large structured data, and never as a store for credentials: as we saw in Lesson 0.7, a token belongs in the Keychain.'),
                  ('CONNECT', 'What about many structured records?'))))

# ================================================================== 4
divider(4, "SwiftData", "Structured application data",
        "NPay wants to store locally saved transaction notes: create, read, update and delete records. That suits a persistence framework such as SwiftData.", "See how it fits.")
NOTE = '''import Foundation
import SwiftData

@Model
final class TransactionNote {
    var title: String
    var amountMinor: Int64   // paise

    init(title: String, amountMinor: Int64) {
        self.title = title
        self.amountMinor = amountMinor
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
    <div>
      {code("TransactionNote.swift", NOTE, "font-size:16px")}
      <p class="small muted" style="margin:8px 0 0">Money as whole <b>paise</b> in an <code>Int64</code>, like <code>balanceMinor</code>. <code>@Model</code> objects are <b>not Sendable</b>: use them on their context&rsquo;s actor. Unit 06 &middot; 6.2 builds this.</p>
    </div>
  </div>""", notes(('SAY', 'The SwiftUI screen works through a SwiftData ModelContext, which persists to model storage. @Model marks TransactionNote as a persistent model; SwiftData manages persistence through its model container and context. The amount is stored as whole paise in an Int64, the same convention as balanceMinor, so there are no rounding surprises.'),
                  ('SAY', 'One line for later: @Model objects are not Sendable. Use them on the actor that owns their context, which for UI work is the main actor. Unit 06, lesson 6.2, covers models, contexts and containers in depth.'),
                  ('SAY', 'SwiftData is not simply an in-memory array that automatically saves every variable. Developers still need to understand model containers, contexts, relationships, schema evolution and save behavior.'),
                  ('CONNECT', 'Some data is naturally a file, not a record.'))))

# ================================================================== 5
divider(5, "Files", "Documents, images and downloaded content",
        "NPay may download a PDF account statement. Some data is naturally a file rather than a database record.", "Where do files go?")
FM = '''import Foundation

// Re-downloadable: Caches
func saveStatement(_ pdf: Data) throws {
    let url = URL.cachesDirectory
        .appending(path: "statement.pdf")
    try pdf.write(to: url, options: .completeFileProtection)
}

// App-managed data: Application Support
let store = URL.applicationSupportDirectory
    .appending(path: "npay.store")'''
S.append(slide("Part 5 &middot; Sandbox directories", "Where an app keeps its files", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.05fr">
    <div>
      <table class="tbl" style="font-size:19px">
        <tr><th>Directory</th><th>Typical purpose</th><th>Backed up</th></tr>
        <tr><td>Documents</td><td>Documents the <b>user</b> creates; can be shown in Files</td><td>Yes</td></tr>
        <tr><td>Application Support</td><td>App-managed data, hidden from the user</td><td>Yes</td></tr>
        <tr class="hl"><td>Caches</td><td>Re-downloadable content, e.g. the statement PDF</td><td>No</td></tr>
        <tr class="hl"><td>Temporary</td><td>Short-lived files</td><td>No</td></tr>
      </table>
      <div class="gap"></div>
      <div class="rule step">The system can remove cached and temporary content. Don&rsquo;t treat those directories as <b>permanent</b>.</div>
    </div>
    <div>
      {code("Statement.swift", FM, "font-size:15px")}
      <p class="small muted" style="margin:8px 0 0"><code>.completeFileProtection</code>: the file stays encrypted while the device is locked. Unit 06 &middot; 6.5 covers backups and data protection.</p>
    </div>
  </div>""", notes(('SAY', 'Apps have directories inside their sandbox. Documents is for documents the user creates; it is backed up and can be shown in the Files app, so it is not the place for app internals. Application Support holds app-managed data, backed up but hidden. Caches holds content that can be downloaded again, and Temporary holds short-lived files; the system can remove both.'),
                  ('SAY', 'NPay can download a statement again at any time, so it goes in Caches. The code uses the modern URL API, URL.cachesDirectory appending a path, and writes with complete file protection, which keeps the file encrypted while the device is locked. App data such as a store goes in Application Support.'),
                  ('SAY', 'Unit 06, lesson 6.5, goes deeper into files, backups and data protection classes.'),
                  ('CONNECT', 'And the most sensitive data: credentials.'))))

# ================================================================== 6
divider(6, "Keychain", "Sensitive data",
        "We met the Keychain in Lesson 0.7. Now connect it to storage choices.", "Choose the right home for four pieces of data.")
pick = [("Dark mode", "UserDefaults", "A lightweight, non-secret preference.", 'lit'),
        ("Auth token", "Keychain", "A sensitive credential that needs security controls.", 'lit'),
        ("PDF statement", "Files: Caches", "Re-downloadable, so Caches, written with file protection.", 'lit'),
        ("Transaction notes", "SwiftData", "Structured records to create, read, update and delete.", 'lit')]
S.append(slide("Part 6 &middot; Choose the storage", "Which storage for which data?", f"""  <div class="body">
    {chooser(pick, 104, 270, 18.7, "BEST FIT", "s16pick", "Dark mode goes in UserDefaults, the authentication token in the Keychain, the PDF statement in Caches, transaction notes in SwiftData")}
    {cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Directory is not security">Sensitive financial documents may also need <b>file protection</b>, encryption and retention policies.</div>
  </div>""", notes(('SAY', 'Dark mode: UserDefaults, a lightweight non-secret preference. Click: the authentication token is not a preference, it is a sensitive credential, so Keychain. Click: a downloaded PDF statement is a file; because NPay can download it again, it goes in Caches. Click: locally saved transaction notes are structured records, so SwiftData.'),
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
      <p class="small muted" style="margin:8px 0 0">Unit 06 &middot; 6.9 covers drafts and state restoration, including <code>@SceneStorage</code>.</p>
    </div>
  </div>""", notes(('SAY', 'The user types "Rent payment" as a transfer note. In the first version it exists only in memory: when iOS terminates the process and the user relaunches, it is gone. Click: in the second version the draft was saved, so it comes back.'),
                  ('SAY', 'Important data should be persisted before the app can lose its in-memory state. Do not rely on a termination callback; save periodically or when meaningful changes happen.'),
                  ('SAY', 'Unit 06, lesson 6.9, covers drafts and state restoration, including @SceneStorage for small per-scene UI state.'),
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
    <div class="rule step" data-label="Communicate freshness">Never present <b>stale</b> financial data as current. As in Lesson 0.8, the <b>server is authoritative</b>: local storage improves usability but does not replace server validation.</div>
    <p class="small muted" style="margin:10px 0 0">Unit 06 &middot; 6.6 covers caching, TTL and freshness states.</p>
  </div>""", notes(('SAY', 'The app can show the cached &#8377;25,000, but it must say it was last updated earlier. Click: the current verified balance is unavailable while offline.'),
                  ('SAY', 'Communicate data freshness clearly. Recall Lesson 0.8: the server is authoritative for balances and transactions, and NPay only holds a copy. Local storage helps usability but does not replace server-side validation. Unit 06, lesson 6.6, builds freshness states.'),
                  ('CONNECT', 'Finally, the persistence technologies you will hear about.'))))

# ================================================================== 9
divider(9, "SwiftData vs Core Data vs SQLite", "Different abstraction levels",
        "These technologies are related but work at different levels.", "Compare them.")
P = [box(0, 0, 172, 64, "SwiftData", "Swift-native", None, '', 'db'),
     box(186, 0, 172, 64, "Core Data", "object graph", None, '', 'layers'),
     box(388, 0, 172, 64, "FileManager", "file operations", None, '', 'folder'),
     wire(f'M86 64V112{head(86, 112, "d")}'), wire(f'M272 64V112{head(272, 112, "d")}'),
     box(0, 118, 358, 64, "SQLite store", "embedded relational database", None, '', 'code'),
     wire(f'M179 182V230{head(179, 230, "d")}'), wire(f'M474 64V230{head(474, 230, "d")}'),
     box(0, 236, 560, 64, "Files on disk", "inside NPay&rsquo;s sandbox", None, '', 'file'),
     '<text class="mono" x="0" y="328">HIGHER LEVEL ON TOP &middot; CLOSER TO THE DISK BELOW</text>']
S.append(slide("Part 9 &middot; Comparison &middot; conceptual", "Four persistence technologies", f"""  <div class="body cols middle" style="grid-template-columns:1.3fr 1fr">
    {svg("0 0 560 334", "SwiftData and Core Data both persist through an SQLite store, which is files on disk; FileManager works with files directly", "s20levels", P)}
    <div>
      <div class="card accent step"><span class="label">New SwiftUI app</span><p class="small" style="margin:0"><b>SwiftData</b> is often a good start, when its capabilities and deployment targets fit.</p></div>
      <div class="gap"></div>
      <div class="card accent step"><span class="label">Existing or advanced</span><p class="small" style="margin:0"><b>Core Data</b> remains important for existing apps and advanced requirements.</p></div>
      <div class="gap"></div>
      <p class="small muted" style="margin:0">Unit 06 &middot; 6.1 compares them in practice.</p>
    </div>
  </div>""", notes(('SAY', 'SwiftData is a Swift-native framework with model-oriented APIs. Core Data is a mature object-graph and persistence framework. SQLite is an embedded relational database engine. FileManager does filesystem operations, not database object management.'),
                  ('SAY', 'Read the drawing top to bottom: SwiftData and Core Data both persist through an SQLite-backed store, which in the end is files in the sandbox; FileManager works with files directly. Their programming models are not the same as writing SQL. For a new SwiftUI app, SwiftData is often a good start; Core Data remains important for existing apps and advanced needs.'),
                  ('CONNECT', "Pull the lesson together."))))

# ================================================================== recap
S.append(recap_slide('0.9', ('storage', 'keychain'),
                     [("db", "Match data to storage", "preferences, records, files, secrets"),
                      ("cross", "Persist before you lose it", "no final callback to rely on"),
                      ("clock", "A cache is a copy", "the server is authoritative")],
                     'Three things to remember. Choose storage by what the data is: preferences in UserDefaults, records in SwiftData, files in the right directory, secrets in the Keychain. Persist what matters before memory can disappear, because there is no final callback to rely on. And a cached balance is a copy: show its age, because the server is authoritative.'))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions, in different formats. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
# (icon, label, data-title, question html, verdict, why, trap, expect, extra notes)
QA = [("folder", "Choose one", "Where should NPay keep a statement PDF it can download again?",
       "NPay downloads a monthly statement PDF that it can download again at any time. Where should it go?"
       "<br><br>A&nbsp; Documents<br>B&nbsp; Caches<br>C&nbsp; UserDefaults<br>D&nbsp; Keychain", "B",
       "Re-downloadable content belongs in Caches; the system may purge it, and NPay fetches it again. Documents is backed up and can appear in Files; UserDefaults is for small preferences; the Keychain is for secrets.",
       "Putting every file in Documents.", "A is the common pick; ask what happens to the user&rsquo;s backup.", None),
      ("code", "Predict the output", "What does UserDefaults return for a key that was never set?",
       "On a fresh install, what does this print?<br><code>let d = UserDefaults.standard</code><br><code>print(d.bool(forKey: \"darkModeEnabled\"))</code>", "false",
       "A missing key is not an error: <code>bool(forKey:)</code> returns <code>false</code>. Design defaults on purpose.",
       "Expecting nil or a crash.", "Some say nil; others expect a crash.", None),
      ("memory", "Question", "Does @State keep a value after iOS terminates NPay?",
       "Does a value in <code>@State</code> survive after iOS terminates NPay?", "No",
       "@State lives with the view&rsquo;s identity inside the running process. When the process ends, it is gone; data that must survive needs persistent storage.",
       "Confusing view state with saved data.", "Some say yes.", None),
      ("bank", "Question", "Can NPay show a cached balance while offline?",
       "NPay is offline. Can it show the balance it cached this morning?", "Yes",
       "Yes, if it says how old the value is, for example &ldquo;Last updated 9:05&rdquo;. The server is authoritative; the cache is a labelled copy.",
       "Either hiding all data offline, or showing it as current.", "Split: some say never show stale data.", None),
      ("clock", "Question", "Does iOS give NPay a reliable last chance to save before termination?",
       "When iOS terminates a suspended NPay, does the app get a callback it can rely on to save the draft?", "No",
       "A suspended app is terminated without running code. Save drafts periodically or on meaningful changes.",
       "Waiting for a termination callback to save.", "Many say yes: they remember a termination method.", "Spaced review from Lesson 0.3.")]
N = len(QA)
for i, (ic, label, title, q, v, why, trap, exp, extra) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    S.append(f"""<section class="slide question" data-title="{E(title, quote=True)}">
  <div class="q-top">
    <p class="kicker">Check your understanding &middot; {i + 1} of {N}</p>
    <div class="q-dots" aria-hidden="true">{dots}</div>
  </div>
  <div class="body">
    <div class="q-row">
      <div class="q-card">
        <div class="q-icon"><svg viewBox="0 0 24 24"><use href="#i-{ic}"/></svg></div>
        <span class="label">{label}</span>
        {qhtml(q)}
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
""" + notes(*([('SAY', extra)] if extra else []), ('ASK', 'Give everyone a few seconds, then take a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next question.' if i < N - 1 else 'Where this goes next.')) + "</section>\n\n")

S.append(next_slide('0.9', [("6.1", "Choosing storage technologies", "today&rsquo;s storage chooser, with real trade-offs"),
                            ("6.2", "SwiftData models, contexts &amp; containers", "<code>@Model</code>, the context and its actor"),
                            ("6.5", "Files, backups &amp; data protection", "directories, backup and file protection"),
                            ("6.6", "Caching, TTL &amp; freshness", "cached balances that say how old they are"),
                            ("6.9", "Drafts &amp; state restoration", "the draft that survives termination, <code>@SceneStorage</code>")],
                    'Everything today is a foundation for Unit 06, Persistence and Offline-First. There you build each of these: the storage chooser with real trade-offs, SwiftData contexts, file protection, freshness states and drafts that survive termination.'))

ITEMS = ["Dark mode setting", "Auth token", "Refresh token", "Monthly statement PDF", "Transaction notes", "Onboarding completed flag",
         "Favourite payees", "Profile photo from the server", "CSV export the user asked to keep", "Last balance seen, with its time"]
items_html = ''.join(f'<li>{x}</li>' for x in ITEMS)
S.append(lab_slide('0.9', "Storage chooser", "Ten pieces of NPay data. Choose a home for each, and say why.",
                   ["For each item choose: <b>UserDefaults</b>, <b>Keychain</b>, <b>SwiftData</b>, a <b>file</b> (Documents or Application Support) or <b>Caches</b>.",
                    "Write the guarantee it needs: secret? must survive termination? re-creatable? user-visible?",
                    "Mark the items NPay may show offline, and how it shows their age.",
                    "Compare with a partner; settle every disagreement with a reason."],
                   "", 'Hand out the ten items. Work alone for five minutes, then in pairs. Expected answers: dark mode and onboarding flag, UserDefaults; auth and refresh tokens, Keychain; statement PDF and profile photo, Caches; transaction notes and favourite payees, SwiftData; the CSV export, Documents; the last balance seen, SwiftData or a file in Application Support, always shown with its time. Push on the reasons, not just the answers.',
                   side=f'<div class="card accent"><span class="label">The ten items</span><ol class="small" style="margin:6px 0 0;columns:1">{items_html}</ol></div>'))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.9 complete</p>
    <h2>iOS Data Storage<br>Architecture</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.10 &mdash; The Complete iOS Architecture: End to End</p>
  </div>
""" + notes(('SAY', 'You can now explain RAM versus persistent storage, why UserDefaults, SwiftData, files and Keychain serve different purposes, how sandboxing affects file access, why important data must survive termination, why cached financial data is not authoritative, and how storage choices shape security and architecture.'),
            ('SAY', 'Next, Lesson 0.10, our final foundation lesson: we follow NPay through a complete journey, from the tap and process launch through the SwiftUI screen, a button event, an API request, security, data storage, backgrounding, suspension and relaunch, on one architecture map.')) + "</section>\n\n")

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
