"""Generates decks/lesson-0.10/index.html from the Lesson 0.10 text only (PocketBank -> NPay)."""
import html, os, re, sys
OUT10 = sys.argv[1]
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


def stepper(items, chip_w, gap, label, tid, title, top=104):
    P = []
    n = len(items)
    lt = lambda i: str(i) if i < n - 1 else f"{i}+"   # last step stays shown after any closing callout
    for i, (chip, *_r) in enumerate(items):
        P.append(box(i * (chip_w + gap), 0, chip_w, 52, chip, '', lt(i)))
    for i, (_c, t, d) in enumerate(items):
        P.append(fade(lt(i), f'<text class="mono" x="0" y="{top}">{label} {i + 1} OF {n}</text><text x="0" y="{top + 36}" style="font-size:26px;font-weight:700">{t}</text><text x="0" y="{top + 70}" style="font-size:19px;font-weight:400">{d}</text>'))
    return svg(f"0 0 1136 {top + 84}", title, tid, P)


def vflow(items, w=560, h=50, gap=16, start=1):
    P = []
    for i, (ic, t, sub) in enumerate(items):
        y = i * (h + gap)
        P.append(box(0, y, w, h, t, sub, str(i + start), '', ic))
        if i < len(items) - 1:
            P.append(wire(f'M{w / 2:g} {y + h}V{y + h + gap - 4}{head(w / 2, y + h + gap - 4, "d")}'))
    return P, len(items) * (h + gap) - gap


def stages(items, step=True):
    st = ' class="step"' if step else ''
    return '<div class="points v stages">' + ''.join(
        f'<div{st}><span class="q-num">{i + 1}</span><span><b>{t}</b><small>{d}</small></span></div>' for i, (t, d) in enumerate(items)) + '</div>'


# ------------------------------------------------------------------ title
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.10 &middot; Foundation finale</p>
    <h1 style="font-size:52px;line-height:1.05">The Complete iOS<br>Architecture: End to End</h1>
    <p class="lead" style="max-width:680px">What happens, why it happens, who is responsible, and how it all fits together.</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'The final lesson of the iOS architecture foundation. In Lessons 0.1 to 0.9 we explored individual components; today we connect them into one system. The goal is not to memorize terms but to understand what happens, why, who is responsible, and how it fits together.'),
            ('CONNECT', "Here's what you'll be able to do by the end.")) + "</section>\n\n")

# ------------------------------------------------------------------ outcomes (authored)
outs = [("layers", "Separate <b>application</b> architecture from <b>platform</b> architecture"),
        ("tap", "Trace <b>Refresh balance</b> from the tap to the updated screen"),
        ("shield", "Name the <b>protections</b> around one request, client and server"),
        ("db", "Choose where each piece of data <b>belongs</b>"),
        ("clock", "Explain <b>leaving and returning</b>: warm activation or cold launch"),
        ("eye", "<b>Review</b> a design and spot architecture mistakes")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.10 &middot; Outcomes", "By the end, you will be able to", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six outcomes. Together they are the Unit 00 deliverable from the course plan: explain tap-to-first-frame and the end-to-end iOS architecture of NPay.'),
                  ('CONNECT', 'Every part of the NPay map lights up today.'))))

# ------------------------------------------------------------------ where we are: the whole map, one stage per click (authored)
ML = {'springboard': '1', 'kernel': '1', 'view': '2', 'thread': '3', 'vm': '3',
      'service': '4', 'frameworks': '4', 'https': '4', 'server': '4', 'sandbox': '5', 'keychain': '5',
      'model': '6', 'storage': '7', 'scene': '8', 'memory': '9+'}
S.append(map_slide('0.10', 'Today: the whole map', (),
                   'Lesson 0.9: each kind of data has a home, and a cached balance is a copy; the server is authoritative.',
                   'One day with NPay visits every part of the map, one stage per click.',
                   'Every lesson so far lit one region of this map. Today the teal moves through all of them, one stage per click: launch, the SwiftUI screen, the tap on the main thread and the ViewModel, the request to the bank, the sandbox and Keychain around it, the model that comes back, storage, the scene lifecycle and memory. Nine clicks, the whole unit.',
                   'Here is the day we will follow.', lits=ML, cues=9))

# ------------------------------------------------------------------ story
story = ["Taps the NPay icon", "iOS launches the app", "SwiftUI shows the dashboard", "Taps Refresh balance", "App contacts the bank securely",
         "Server returns &#8377;25,000", "Screen updates, data saved", "Switches to another app", "iOS suspends, may terminate", "Returns to NPay"]
cells = "\n".join(f'      <div style="display:flex;gap:12px;align-items:center"><span class="q-num" style="width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:var(--teal-soft);color:var(--teal);font-family:var(--mono);font-weight:700;flex:none">{i + 1}</span><span style="font-size:20px">{t}</span></div>' for i, t in enumerate(story))
S.append(slide("The story", "One day with NPay", f"""  <div class="body">
    <div style="display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(5,auto);gap:16px 48px">
{cells}
    </div>
    <div class="gap-lg"></div>
    <p class="lead step" style="margin:0">Can you explain every major component involved? <b>By the end of this lesson, you will.</b></p>
  </div>""", notes(('SAY', 'Ten moments: a user taps NPay; iOS launches it; SwiftUI shows the dashboard; the user taps Refresh balance; the app contacts the bank securely; the server returns &#8377;25,000; the app updates the screen and saves appropriate data; the user switches apps; iOS suspends NPay and may terminate it; the user returns.'),
                 ('ASK', 'Which of these ten steps could you explain in detail right now?'),
                 ('EXPECT', 'Usually only a few. By the end, all ten.'),
                 ('CONNECT', 'First, the whole architecture in one picture.'))))

# ================================================================== 1
divider(1, "The complete architecture", "Two perspectives in one picture",
        "One diagram that combines application design and platform architecture.", "Look at the two halves.")
P = ['<g class="nd ghost"><rect class="sh" x="0" y="0" width="760" height="300" rx="16"/></g><text class="mono" x="16" y="22">NPAY APP PROCESS</text>',
     box(20, 36, 720, 52, "SwiftUI View", "screens, navigation, user interaction", '1', '', 'phone'),
     box(20, 98, 720, 52, "ViewModel / presentation state", "loading, balance, errors, user actions", '1', '', 'layout'),
     box(20, 160, 720, 52, "Application services / repository", "business coordination, data access", '1', '', 'link'),
     box(20, 224, 350, 56, "Networking", "URLSession", '1', '', 'globe'), box(390, 224, 350, 56, "Storage", "SwiftData, files, Keychain", '1', '', 'db'),
     box(0, 316, 760, 50, "Apple frameworks &amp; iOS services", "SwiftUI, Foundation, Security, lifecycle, graphics", None, '', 'frameworks'),
     box(0, 376, 760, 50, "Darwin / XNU kernel", "processes, threads, virtual memory, scheduling", None, '', 'kernel'),
     box(0, 436, 760, 50, "Apple hardware", "", None, 'solid', 'chip'),
     wire('M760 251H858', None, 'dash'), '<text class="sm" x="809" y="240" text-anchor="middle">network</text>',
     tall(864, 196, 272, 112, 'bank', "Bank backend", "auth, accounts, transactions")]
S.append(slide("Part 1 &middot; Architecture &middot; conceptual", "NPay: the complete picture", f"""  <div class="body">
    {svg("0 0 1136 488", "The NPay app process holds the SwiftUI view, ViewModel, services, networking and storage, on top of Apple frameworks, the kernel and hardware; the bank backend is a separate system reached through system APIs", "s4arch", P, "max-height:390px")}
    <div class="gap"></div>
    <div class="rule step" data-label="Two perspectives"><b>Application architecture</b> (teal) organizes NPay&rsquo;s code; <b>platform architecture</b> (below) provides execution, security, frameworks and hardware.</div>
  </div>""", notes(('SAY', 'Inside the NPay process: the SwiftUI view, the ViewModel and presentation state, application services, then networking and storage. Below it: Apple frameworks and iOS services, the Darwin/XNU kernel and the hardware. On the right, the bank backend, a separate system reached through network APIs, not part of the iPhone process.'),
                  ('SAY', 'Click: this diagram mixes two perspectives. Application architecture, now teal, is how we organize NPay’s code. Platform architecture is how iOS provides execution, security, frameworks and hardware access. Do not confuse the two.'),
                  ('CONNECT', 'Now walk the day, stage by stage, starting with the launch.'))))

# ================================================================== 2 launch
divider(2, "Launching NPay", "Stage one: from the Home Screen to a running app",
        "Lesson 0.1 in seven steps.", "Click through the startup.")
launch = [("SpringBoard", "User taps the app icon", "The Home Screen handles the interaction and requests a launch or activation."),
          ("Launch request", "Launch or activate?", "The system checks whether an NPay process already exists."),
          ("Process", "Process created", "On a cold launch, the OS creates the process and its address space."),
          ("dyld", "Code loaded", "The dynamic loader prepares the executable and its libraries."),
          ("@main", "Swift entry point", "The runtime starts the NPay App type."),
          ("Scene", "Scene connected: inactive", "iOS connects a scene; WindowGroup supplies the root view."),
          ("First frame", "Dashboard on screen, then active", "SwiftUI lays out the views, the first frame appears, the scene becomes active.")]
S.append(slide("Part 2 &middot; Startup explorer &middot; conceptual", "Launch in seven steps", f"""  <div class="body">
    {stepper(launch, 147, 17.8, "STEP", "s6launch", "Seven launch steps from SpringBoard to the first frame")}
    {cues(6)}
    <div class="gap"></div>
    <div class="rule step" data-label="Checkpoint: who owns the process?">The <b>operating system</b> manages the process. SwiftUI provides app and scene abstractions <b>inside</b> it.</div>
  </div>""", notes(('SAY', 'Step one: SpringBoard, the system UI, handles the tap and requests a launch or activation. Click through the rest: the launch decision, process creation, dyld loading, the Swift entry point, the scene connecting in the inactive state, and the first frame, after which the scene becomes active. This is Lesson 0.1 compressed.'),
                  ('ASK', 'Who owns the process?'),
                  ('EXPECT', 'The operating system. SwiftUI provides application and scene abstractions within the running app.'),
                  ('CONNECT', 'Inside that process, SwiftUI builds the dashboard.'))))

# ================================================================== 3 SwiftUI
divider(3, "SwiftUI builds the dashboard", "Stage two: from @main to a view value",
        "Lessons 0.1 and 0.4: the app entry point.", "Here it is.")
APP = '''import SwiftUI

@main
struct NPayApp: App {
    var body: some Scene {
        WindowGroup {
            DashboardView()
        }
    }
}'''
S.append(slide("Part 3 &middot; App entry", "The NPay entry point", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("NPayApp.swift", APP, "font-size:17px")}
    <div>
      {stages([("<code>@main NPayApp</code>", "the entry-point type"), ("App protocol", "SwiftUI application"), ("WindowGroup", "system-managed windows"), ("DashboardView", "the root view")], step=False)}
      <div class="gap"></div>
      <div class="rule step"><code>DashboardView()</code> creates a <b>view value</b>; it does not draw pixels. SwiftUI evaluates, lays out and updates.</div>
    </div>
  </div>""", notes(('SAY', 'The structure: @main NPayApp, conforming to App, whose body is a WindowGroup containing DashboardView.'),
                  ('SAY', 'Calling DashboardView() creates a SwiftUI view value. It does not issue drawing commands; SwiftUI manages evaluating the hierarchy, layout and updates.'),
                  ('CONNECT', 'Now the user does something.'))))

# ================================================================== 4 Refresh balance (tap + the request, merged)
divider(4, "Refresh balance", "Stage three: one tap, the request behind it",
        "The user taps Refresh balance. Lessons 0.2, 0.5 and 0.8.", "Watch the screen and what happens behind it.")
P = ['<use href="#d-iphone" x="0" y="0" width="200" height="400"/>',
     '<text x="100" y="66" text-anchor="middle" style="font-size:20px;font-weight:800">NPay</text>',
     '<g class="nd"><rect class="sh" x="24" y="84" width="152" height="80" rx="12"/><text class="sm" x="100" y="110" text-anchor="middle">Available balance</text></g>',
     fade("0-4", '<text x="100" y="148" text-anchor="middle" style="font-size:24px;font-weight:700">&#8212;</text>'),
     fade("5", '<text x="100" y="148" text-anchor="middle" style="font-size:16px;font-weight:600">loading&#8230;</text>'),
     fade("6+", '<text x="100" y="148" text-anchor="middle" style="font-size:22px;font-weight:700;fill:var(--teal-ink)">&#8377;25,000</text>'),
     '<g class="nd lit"><rect class="sh" x="24" y="180" width="152" height="40" rx="12"/><text class="sm" x="100" y="205" text-anchor="middle">Refresh balance</text></g>']
inside = [("Touch event reaches the app", "main thread"), ("Button action executes", "SwiftUI"), ("DashboardViewModel starts async work", ""),
          ("BalanceService sends the request", "URLSession, HTTPS"), ("Response decoded", "into a Balance model"), ("Observable state changes", ""), ("SwiftUI updates the balance", "")]
S.append(slide("Part 4 &middot; Tap simulation &middot; conceptual", "What happens when Refresh balance is tapped", f"""  <div class="body cols middle" style="grid-template-columns:.55fr 1.45fr">
    {svg("0 0 200 400", "NPay screen: the balance changes from a dash to loading to 25,000 rupees", "s10tap", P, "max-height:430px")}
    <div>
      {stages(inside)}
      <p class="small muted" style="margin:10px 0 0">Illustrates state updates; no real network request.</p>
    </div>
  </div>""", notes(('SAY', 'Click through seven steps and watch the phone. The touch event reaches the app on the main thread; the SwiftUI Button action runs; DashboardViewModel starts an asynchronous operation; BalanceService sends the request through URLSession over HTTPS (the screen shows loading); the response is decoded into a Balance model; observable state changes; SwiftUI shows &#8377;25,000.'),
                  ('ASK', 'Does the main thread stay blocked while the bank server responds?'),
                  ('EXPECT', 'Not with properly asynchronous APIs like URLSession and await. The task suspends while the request is pending.'),
                  ('CONNECT', 'Step four, the request, is the service you met in Lesson 0.8.'))))
SVC = '''struct BalanceService {
    func fetchBalance() async throws -> Balance {
        let url = URL(string: "https://api.npay.example/balance")!
        let (data, response) = try await URLSession.shared.data(from: url)
        guard let http = response as? HTTPURLResponse,
              (200..<300).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(Balance.self, from: data)
    }
}'''
S.append(slide("Part 4 &middot; The request &middot; recall from 0.8", "The service behind step four", f"""  <div class="body cols middle" style="grid-template-columns:1.5fr 1fr">
    <div>
      {code("BalanceService.swift", SVC, "font-size:14.5px")}
      <p class="small muted" style="margin:8px 0 0">Fictional URL. Real banking code also needs authentication and secure token handling.</p>
    </div>
    {points([("clock", "await suspends", "the main thread stays free"), ("check", "Any 2xx is success", "<code>200..&lt;300</code>, not only 200"), ("code", "Decode", "JSON &rarr; <code>Balance</code>")], cls='v', label='Read it', step=False)}
  </div>""", notes(('SAY', 'This is step four from Lesson 0.8, not new material. The service builds the URL, awaits URLSession, which suspends the task without blocking the main thread, accepts any 2xx status, and decodes the JSON into a Balance. The URL is fictional; real code also needs authentication, authorization-aware error handling and secure token management.'),
                  ('CONNECT', 'Which security mechanisms protect this operation?'))))

# ================================================================== 5 security
divider(5, "Security protects the request", "Stage four: Lesson 0.7 in one view",
        "Several security mechanisms are involved when NPay talks to the bank.", "Six of them.")
sec = [("file", "Code signing", "code integrity, execution requirements"), ("lock", "Sandbox", "restricts the app&rsquo;s resource access"),
       ("key", "Keychain", "protects sensitive credentials"), ("globe", "HTTPS / TLS", "protects network communication"),
       ("bank", "Backend authorization", "decides which account data is accessible"), ("shield", "Data protection", "protects stored data under policy")]
P = []
for i, (ic, t, sub) in enumerate(sec):
    r, c = divmod(i, 3)
    P.append(tall(c * 392, r * 130, 352, 112, ic, t, sub, '1' if i == 4 else None))
S.append(slide("Part 5 &middot; Security &middot; conceptual", "Six protections around one request", f"""  <div class="body">
    {svg("0 0 1136 242", "Code signing, sandbox, Keychain, HTTPS and TLS, backend authorization, data protection", "s14sec", P)}
    <div class="gap"></div>
    <div class="rule step" data-label="Critical lesson">Client-side security does <b>not</b> replace <b>server-side authorization</b>. The bank must verify the user may access the requested account.</div>
  </div>""", notes(('SAY', 'Six protections: code signing for integrity, the sandbox restricting access, the Keychain protecting credentials, HTTPS protecting the network, backend authorization deciding what data is accessible, and data protection for stored data.'),
                  ('SAY', 'Click: even if NPay stores tokens securely and uses HTTPS, the bank server must independently verify that the authenticated user is authorized for the requested account.'),
                  ('CONNECT', 'Now the data comes back.'))))

# ================================================================== 6 data returns
divider(6, "Data returns, SwiftUI updates", "Stage five: from bytes to pixels",
        "The server responds with JSON. How does it reach the screen?", "Follow it.")
JSON = '''{
  "balanceMinor": 2500000,
  "currency": "INR"
}'''
MODEL = '''struct Balance: Decodable {
    let balanceMinor: Int64   // paise
    let currency: String
}'''
P, h = vflow([("file", "HTTP response data", ""), ("code", "JSONDecoder", ""), ("db", "Balance model", "balanceMinor: 2500000"),
              ("layout", "DashboardViewModel formats &#8377;25,000", ""), ("eye", "SwiftUI re-evaluates relevant views", ""), ("frame", "Updated balance on screen", "")], w=520, h=46, gap=14)
P = [p.replace(' data-lit="1"', '').replace(' data-lit="2"', '').replace(' data-lit="3"', '').replace(' data-lit="4"', '').replace(' data-lit="5"', '').replace(' data-lit="6"', '') for p in P]
S.append(slide("Part 6 &middot; Response to screen &middot; conceptual", "UI = f(state)", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    <div>
      <div class="cw"><div class="ch"><span>response.json</span></div><pre class="tree" style="font-size:17px;border-radius:0 0 12px 12px">{E(JSON)}</pre></div>
      <div class="gap"></div>
      {code("Balance.swift", MODEL, "font-size:16px")}
    </div>
    <div>
      {svg(f"0 0 520 {h}", "Response data, JSONDecoder, Balance model, ViewModel formatting, SwiftUI re-evaluation, updated balance", "s16ret", P, "max-height:300px")}
      <div class="gap"></div>
      <div class="rule step" data-label="UI = f(state)">The interface describes what to show for the current state. It does <b>not</b> mean every change redraws the whole screen.</div>
    </div>
  </div>""", notes(('SAY', 'The server returns balanceMinor 2,500,000 in INR: whole paise in an Int64, so no rounding. Read down: the data goes through JSONDecoder into a Balance; DashboardViewModel formats it as &#8377;25,000 and updates observable state; SwiftUI re-evaluates the relevant views; the updated balance appears.'),
                  ('SAY', 'Click: UI equals f of state, a conceptual way to describe declarative UI. It does not imply every state change redraws the whole screen.'),
                  ('CONNECT', 'What should NPay store, and where?'))))

# ================================================================== 7 storage (challenge slide folded in: token is a one-line recall)
divider(7, "What should we store?", "Stage six: Lesson 0.9 applied",
        "Not all NPay data belongs in the same storage system.", "Six pieces of data.")
S.append(slide("Part 7 &middot; Storage map", "Where each piece of data belongs", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Data</th><th>Appropriate storage</th></tr>
      <tr><td>Dark mode preference</td><td>UserDefaults</td></tr>
      <tr><td>Authentication token</td><td>Keychain, never UserDefaults (Lesson 0.7)</td></tr>
      <tr><td>Downloaded statement PDF</td><td>Caches, with file protection (re-downloadable)</td></tr>
      <tr><td>Locally saved transaction notes</td><td>SwiftData or another persistence store</td></tr>
      <tr><td>Current screen loading flag</td><td>In-memory ViewModel state</td></tr>
      <tr class="hl"><td>Authoritative account balance</td><td>Bank backend; a cached copy shows when it was last verified</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Principle">Choose storage by <b>sensitivity</b>, <b>size</b>, <b>lifecycle</b> and <b>consistency</b> needs, not because an API is easy.</div>
  </div>""", notes(('SAY', 'Six pieces of data, six homes. The preference in UserDefaults; the token in the Keychain, as Lesson 0.7 established; the statement PDF in Caches with file protection, because NPay can download it again; notes in SwiftData or similar; the loading flag only in ViewModel memory; and the authoritative balance on the bank backend, with any cached copy showing when it was last verified.'),
                  ('SAY', 'Click: choose storage by sensitivity, size, lifecycle and consistency, not convenience.'),
                  ('CONNECT', 'Now the user leaves NPay.'))))

# ================================================================== 8 lifecycle (recall, shown whole)
divider(8, "The user leaves", "Stage seven: Lesson 0.3 in one table",
        "The user presses Home or switches apps. What happens to NPay?", "One possible progression.")
S.append(slide("Part 8 &middot; Lifecycle &middot; recall from 0.3", "From active to terminated", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Moment</th><th>Scene phase</th><th>Process</th><th>What it means</th></tr>
      <tr><td><b>Active</b></td><td><code>.active</code></td><td>Running</td><td>Visible and responding to the user</td></tr>
      <tr><td><b>Inactive</b></td><td><code>.inactive</code></td><td>Running</td><td>In the foreground, not receiving events</td></tr>
      <tr><td><b>Background</b></td><td><code>.background</code></td><td>Running briefly</td><td>No longer visible; execution may continue briefly</td></tr>
      <tr><td><b>Suspended</b></td><td><code>.background</code></td><td>Suspended</td><td>Kept in memory, no code runs</td></tr>
      <tr><td><b>Terminated</b></td><td>none</td><td>Gone</td><td>iOS reclaimed the memory</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Watch the words">Scene phases are <code>.active</code>, <code>.inactive</code>, <code>.background</code>. <b>Suspended</b> is a process condition, not a scene phase.</div>
  </div>""", notes(('SAY', 'A recall from Lesson 0.3, so the whole table at once. Active: visible and responding. Inactive: still in the foreground but not receiving events. Background: no longer visible, execution may continue briefly. Suspended: kept in memory, no code runs. Terminated: the process is gone. One possible progression; iOS does not guarantee every app passes through each state in order.'),
                  ('SAY', 'Click: the three scene phases are active, inactive and background. Suspended describes the process. This matters when someone asks whether their background code keeps running.'),
                  ('CONNECT', 'While navigating, objects come and go too.'))))

# ================================================================== 9 memory (recall)
divider(9, "Memory during navigation", "Stage eight: Lesson 0.6, who owns the ViewModel?",
        "The user opens transaction history; NPay creates a ViewModel holding transactions. When they navigate away, is it destroyed?", "Look at the ownership.")
P = [box(0, 0, 420, 54, "TransactionHistoryView", "", None, '', 'phone'), wire(f'M210 54V74{head(210, 74, "d")}'),
     box(0, 80, 420, 54, "TransactionViewModel", "", None, '', 'layout'), wire(f'M210 134V154{head(210, 154, "d")}'),
     box(0, 160, 420, 54, "TransactionService", "", None, '', 'link')]
TVM = '''@MainActor
final class TransactionViewModel {
    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = { [weak self] in self?.refresh() }
    }

    func refresh() { print("Refreshing transactions") }

    deinit { print("ViewModel deinitialized") }
}'''
S.append(slide("Part 9 &middot; Ownership &middot; recall from 0.6", "A ViewModel and its closure", f"""  <div class="body cols middle" style="grid-template-columns:.9fr 1.2fr">
    <div>
      {svg("0 0 420 216", "TransactionHistoryView owns TransactionViewModel, which uses TransactionService", "s24own", P)}
      <div class="gap"></div>
      <p class="small">A stored closure that strongly captures the ViewModel creates a <b>retain cycle</b>. <code>[weak self]</code> avoids it.</p>
    </div>
    {code("TransactionViewModel.swift", TVM, "font-size:15px")}
  </div>""", notes(('SAY', 'A recall from Lesson 0.6. The view owns the ViewModel, which uses the service. If the ViewModel stores a closure that strongly captures the ViewModel, a retain cycle can form; this code uses weak capture to avoid it.'),
                  ('ASK', 'Does navigating away from a screen guarantee its ViewModel’s deinit runs immediately?'),
                  ('EXPECT', 'No. It may still be legitimately retained elsewhere. Navigation and object lifetime are related but not identical.'),
                  ('CONNECT', 'Finally, the user comes back.'))))

# ================================================================== 10 return
divider(10, "The user returns", "Stage nine: two possible situations",
        "The user returns to NPay after several minutes.", "Survived, or terminated?")
S.append(slide("Part 10 &middot; Return scenarios", "Warm activation or cold launch", """  <div class="body">
    <div class="cols stretch">
      <div class="card accent step"><span class="label">Process survived: warm activation</span>
        <ol class="small" style="margin:6px 0 0"><li>iOS resumes execution if the process was suspended.</li><li>The scene returns toward the foreground.</li><li>In-memory state may still exist.</li><li>The app refreshes data when appropriate.</li></ol></div>
      <div class="card step"><span class="label">Process terminated: cold launch</span>
        <ol class="small" style="margin:6px 0 0"><li>iOS starts a new process.</li><li>The launch runs again, as in Stage one.</li><li>In-memory state is gone.</li><li>The app restores persisted data and fetches fresh data.</li></ol></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Key lesson">Work correctly in <b>both</b>. Never assume the process stays alive, and never assume cached financial data is <b>current</b>.</div>
  </div>""", notes(('SAY', 'Warm activation: iOS resumes the suspended process, the scene comes back to the foreground, in-memory state may still exist, and the app refreshes data when appropriate. Click: cold launch: a new process, the full launch again, in-memory state is gone, so the app restores what it persisted and fetches fresh data.'),
                  ('SAY', 'A robust app must work in both cases. Never assume the process stays alive, and never assume cached financial data is current.'),
                  ('CONNECT', 'Now put the whole day on one page.'))))

# ================================================================== 11 complete flow (one sweep)
divider(11, "The complete flow", "One user action, many systems",
        "Reconstruct the entire NPay journey.", "Twelve steps, one sweep.")
flow = [("User taps NPay", "SpringBoard, launch coordination"), ("iOS starts or activates the app", "process, dyld, Swift entry point"),
        ("SwiftUI shows DashboardView", "scene, state, evaluation, rendering"), ("User taps Refresh balance", "touch event, main thread, action"),
        ("ViewModel requests data", "asynchronous app logic"), ("Service contacts the backend", "URLSession, HTTPS, authentication"),
        ("Server returns authorized data", "business rules, account data"), ("ViewModel updates state", "decoding, formatting, errors"),
        ("SwiftUI updates the screen", "reconciliation, layout, presentation"), ("App persists selected data", "SwiftData, files, Keychain, preferences"),
        ("User leaves the app", "scene lifecycle, background, suspension"), ("User returns", "warm activation or cold launch, restoration")]
P = []
for i, (t, sub) in enumerate(flow):
    r, c = divmod(i, 3)
    o = box(c * 386, r * 104, 362, 76, f"{i + 1}. {t}", sub, '1', 'pass')
    P.append(o.replace('<g class="nd pass"', f'<g class="nd pass" style="--d:{i * 0.12:.2f}s"', 1))
S.append(slide("Part 11 &middot; End to end &middot; conceptual", "The whole day in twelve steps", f"""  <div class="body">
    {svg("0 0 1136 388", "Twelve steps from tapping NPay through launch, the dashboard, the balance request, the server, state update, rendering, storage, leaving and returning", "s29flow", P, "max-height:470px")}
    {cues(1)}
  </div>""", notes(('SAY', 'All twelve on one page. Click and watch one sweep run through them in order. Each step names the lesson behind it: launch coordination and process startup from 0.1; SwiftUI from 0.4 and 0.5; the request from 0.2 and 0.8; security from 0.7; persistence from 0.9; leaving and returning from 0.3; and object lifetimes from 0.6.'),
                  ('CONNECT', 'Step back and see the whole module.'))))

# ================================================================== module map
S.append(slide("Foundation module", "Ten connected lessons", """  <div class="body top">
    <table class="tbl" style="font-size:17.5px">
      <tr><th>Lesson</th><th>Central question</th><th>Prepares you for</th></tr>
      <tr><td>0.1 App startup</td><td>How does an app start?</td><td>Swift entry point and Xcode</td></tr>
      <tr><td>0.2 Architecture</td><td>How do app components communicate?</td><td>MVVM and code organization</td></tr>
      <tr><td>0.3 Lifecycle</td><td>What happens when users leave?</td><td>State restoration</td></tr>
      <tr><td>0.4 SwiftUI vs UIKit</td><td>How does app code receive system events?</td><td>UI frameworks</td></tr>
      <tr><td>0.5 Threads &amp; RunLoop</td><td>How does a tap become UI work?</td><td>Swift concurrency</td></tr>
      <tr><td>0.6 Memory &amp; ARC</td><td>Who owns objects?</td><td>Structs, classes, closures</td></tr>
      <tr><td>0.7 Security</td><td>How does iOS protect data?</td><td>Keychain and permissions</td></tr>
      <tr><td>0.8 Networking</td><td>How does data reach the server?</td><td>URLSession and Codable</td></tr>
      <tr><td>0.9 Storage</td><td>How does data survive termination?</td><td>SwiftData and persistence</td></tr>
      <tr class="hl"><td>0.10 Integration</td><td>How does everything fit together?</td><td>Production app development</td></tr>
    </table>
  </div>""", notes(('SAY', 'The whole foundation module on one page: each lesson’s central question and what it prepares you for.'),
                  ('CONNECT', 'Pull it together on the map.'))))

# ================================================================== recap (authored)
S.append(recap_slide('0.10', ('sandbox',),
                     [("layers", "Two architectures", "your code on top of the platform"),
                      ("shield", "Layered protection", "client security plus server authorization"),
                      ("clock", "Never assume", "that the process lives or the cache is current")],
                     'The teal boundary is NPay&rsquo;s own code; everything around it is the platform and the bank. Three things to carry into Unit 01: NPay is application architecture sitting on platform architecture; protection is layered, and the server always authorizes; and a robust app never assumes its process is still alive or its cached data still current.',
                     'Now review some designs.'))

# ================================================================== review (architecture review, mixed formats; authored rework)
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Architecture review</h2>
    <p class="lead">Good design, problem, or the right answer?</p>
  </div>
""" + notes(('SAY', 'Five items in different formats: some designs are good, some are problems, one is a choice and one asks you to predict output. Commit before each answer is revealed.')) + "</section>\n\n")
QA = [("clock", "Good design or problem?", "A synchronous five-second calculation inside a SwiftUI Button action",
       "A developer performs a synchronous five-second calculation directly inside a SwiftUI Button action.", "Problem",
       "It blocks the main thread: the UI cannot respond for five seconds. Move heavy work off the main actor.", "Assuming async UI frameworks protect you from blocking code.", "Most spot it; ask where the work should run.", None),
      ("bank", "Choose one", "What should the dashboard show offline?",
       "NPay is offline and has this morning&rsquo;s cached balance. What should the dashboard show?"
       "<br><br>A&nbsp; &#8377;25,000 as the current balance<br>B&nbsp; &#8377;25,000, &ldquo;Last updated 9:05&rdquo;<br>C&nbsp; Nothing until it is online<br>D&nbsp; Only an error alert", "B",
       "Show the copy with its age. The backend is authoritative; hiding everything (C, D) is unhelpful, and A presents stale data as current.", "Presenting stale financial data as current.", "Some pick C to be safe.", None),
      ("layout", "Good design or problem?", "The ViewModel awaits the request and shows a loading state",
       "<code>DashboardViewModel</code> awaits <code>BalanceService</code> and shows a loading state while the request is pending.", "Good design",
       "<code>await</code> suspends the task without blocking the main thread, and loading is explicit screen state the view can show.", "Thinking every async call needs a background thread.", "Some look for a hidden flaw.", None),
      ("code", "Predict the output", "What prints when the ViewModel variable is set to nil?",
       "Using the <code>TransactionViewModel</code> from Stage eight:<br><code>var vm: TransactionViewModel? = TransactionViewModel()</code><br><code>vm?.configure()</code><br><code>vm = nil</code><br>What prints?", "&ldquo;ViewModel deinitialized&rdquo;",
       "<code>[weak self]</code> means the stored closure does not own the ViewModel, so the last strong reference is gone and <code>deinit</code> runs.", "Expecting nothing to print because the closure still exists.", "Some expect a leak.", "Spaced review from Lesson 0.6."),
      ("send", "Good design or problem?", "A failed money-transfer POST is retried automatically",
       "A failed money-transfer POST is retried automatically, with no idempotency protection.", "Problem",
       "If the first attempt actually succeeded, the retry can transfer the money twice.", "Retrying every failure by reflex.", "Many accept automatic retries.", None)]
N = len(QA)
for i, (ic, label, title, q, v, why, trap, exp, extra) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    S.append(f"""<section class="slide question" data-title="{E(title, quote=True)}">
  <div class="q-top">
    <p class="kicker">Architecture review &middot; {i + 1} of {N}</p>
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
""" + notes(*([('SAY', extra)] if extra else []), ('ASK', 'Commit to an answer, then a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next item.' if i < N - 1 else 'Where this goes next.')) + "</section>\n\n")

# ================================================================== where next (authored, from the course plan)
S.append(next_slide('0.10', [("1.5", "Structs, classes &amp; value semantics", "views are values, ViewModels are classes"),
                             ("1.8", "ARC, ownership &amp; memory management", "the ViewModel closure and <code>[weak self]</code>"),
                             ("1.9", "Swift concurrency: tasks, actors &amp; Sendable", "<code>await</code>, <code>@MainActor</code> and the main thread"),
                             ("1.10", "NPay domain model, actor ledger &amp; tests", "<code>balanceMinor</code> becomes a real Money type"),
                             ("12.9", "Capstone integration &amp; final test plan", "this end-to-end map, built for real")],
                    'Unit 01 turns these concepts into executable Swift: value and reference types, ownership, concurrency, and the NPay domain model with a Money type. The same end-to-end map comes back in the capstone, Unit 12, where you build and defend it.'))

# ================================================================== Unit 00 checkpoint (authored; replaces "Your challenge")
S.append(slide("Lesson 0.10 &middot; Unit 00 checkpoint", "Explain Refresh balance end to end", f"""  <div class="body">
    <p style="margin:0 0 10px;font-size:20px">&ldquo;I tap NPay, refresh my balance, switch to another app, and return ten minutes later. Explain the entire journey.&rdquo;</p>
    {archmap((), title='Blank NPay architecture map for the checkpoint', tid='ckmap', style='max-height:330px')}
    <ol class="lab" style="display:grid;grid-template-columns:repeat(3,1fr);gap:0 28px;font-size:18px;margin-top:12px">
      <li>Number the map in the order things happen.</li><li>Explain each step aloud to a partner, in 3 minutes.</li><li>Swap; your partner scores you on the rubric.</li>
    </ol>
  </div>""", notes(('SAY', 'This is the Unit 00 checkpoint from the course plan: explain a feature end to end. Use the blank map: number every region in the order Refresh balance touches it, then explain it aloud without looking at the earlier slides. A strong answer separates the operating system, the frameworks, your application code and the backend.'),
                  ('LIVE DEMO', 'Print the blank map, one per pair. Allow five minutes to annotate and three minutes per person to explain. Partners score each other on the rubric on the next slide; anything scored "Not yet" is the lesson to revisit.'),
                  ('CONNECT', 'Here is how your partner scores you.'))))
S.append(slide("Lesson 0.10 &middot; Unit 00 checkpoint", "Checkpoint rubric", """  <div class="body top">
    <table class="tbl" style="font-size:18px">
      <tr><th>Area</th><th>A strong answer says</th><th>Revisit</th></tr>
      <tr><td><b>Launch</b></td><td>The OS owns the process; scene connects inactive, first frame, then active</td><td>0.1, 0.3</td></tr>
      <tr><td><b>The tap</b></td><td>Touch on the main thread; <code>await</code> suspends without blocking it</td><td>0.5</td></tr>
      <tr><td><b>Layers</b></td><td>View &rarr; ViewModel &rarr; Service &rarr; URLSession &rarr; HTTPS &rarr; server, each with one job</td><td>0.2, 0.8</td></tr>
      <tr><td><b>Security</b></td><td>Sandbox, token in the Keychain, HTTPS, and the server authorizes</td><td>0.7</td></tr>
      <tr><td><b>Data</b></td><td>The right home for each item; a cache is a copy with its age shown</td><td>0.9</td></tr>
      <tr><td><b>Leave &amp; return</b></td><td>Suspended or terminated; warm activation or cold launch; who owns the ViewModel</td><td>0.3, 0.4, 0.6</td></tr>
    </table>
    <p class="small muted" style="margin:12px 0 0">Score each row: <b>Clear</b> &middot; <b>Partly</b> &middot; <b>Not yet</b>. Every &ldquo;Not yet&rdquo; names the lesson to revisit.</p>
  </div>""", notes(('SAY', 'Six areas, one per region of the map. For each, your partner marks clear, partly or not yet. The last column tells you which lesson to revisit before Unit 01.'),
                  ('CONNECT', 'That completes the foundation.'))))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Foundation module complete</p>
    <h2>iOS Architecture<br>Foundation</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Unit 01 &mdash; Swift Language Mastery</p>
  </div>
""" + notes(('SAY', 'Ten connected lessons: app startup, system architecture, lifecycle, UIKit and SwiftUI, threads, concurrency fundamentals, ARC, security, networking, persistence and complete application flow. This is the conceptual foundation; practical mastery comes from implementing, debugging and measuring these mechanisms in Xcode.'),
            ('SAY', 'Next, Unit 01: Swift Language Mastery, in the same deep style but with executable code, progressively building the NPay domain model. Swift design and compilation; variables and the type system; optionals; functions and closures; structs, classes and value semantics; protocols and extensions; generics and errors; ARC in practice; tasks, actors and Sendable; and the NPay domain model.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.10 — The Complete iOS Architecture: End to End</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.10 — The Complete iOS Architecture">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT10, 'w').write(doc)
print(len(S), 'slides')
