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


def stages(items):
    return '<div class="points v stages">' + ''.join(
        f'<div class="step"><span class="q-num">{i + 1}</span><span><b>{t}</b><small>{d}</small></span></div>' for i, (t, d) in enumerate(items)) + '</div>'


# ------------------------------------------------------------------ title
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.10 &middot; Foundation finale</p>
    <h1 style="font-size:52px;line-height:1.05">The Complete iOS<br>Architecture: End to End</h1>
    <p class="lead" style="max-width:680px">What happens, why it happens, who is responsible, and how it all fits together.</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'The final lesson of the iOS architecture foundation. In Lessons 0.1 to 0.9 we explored individual components; today we connect them into one system. The goal is not to memorize terms but to understand what happens, why, who is responsible, and how it fits together.'),
            ('CONNECT', 'We follow one day with NPay.')) + "</section>\n\n")

# ------------------------------------------------------------------ story
story = ["Taps the NPay icon", "iOS launches the app", "SwiftUI shows the dashboard", "Taps Check Balance", "App contacts the bank securely",
         "Server returns &#8377;25,000", "Screen updates, data saved", "Switches to another app", "iOS suspends, may terminate", "Returns to NPay"]
cells = "\n".join(f'      <div class="step" style="display:flex;gap:12px;align-items:center"><span class="q-num" style="width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:var(--teal-soft);color:var(--teal);font-family:var(--mono);font-weight:700;flex:none">{i + 1}</span><span style="font-size:20px">{t}</span></div>' for i, t in enumerate(story))
S.append(slide("The story", "One day with NPay", f"""  <div class="body">
    <div style="display:grid;grid-template-columns:1fr 1fr;grid-auto-flow:column;grid-template-rows:repeat(5,auto);gap:16px 48px">
{cells}
    </div>
    <div class="gap-lg"></div>
    <p class="lead step" style="margin:0">Can you explain every major component involved? <b>By the end of this lesson, you will.</b></p>
  </div>""", notes(('SAY', 'Ten moments, one per click: a user taps NPay; iOS launches it; SwiftUI shows the dashboard; the user taps Check Balance; the app contacts the bank securely; the server returns &#8377;25,000; the app updates the screen and saves appropriate data; the user switches apps; iOS suspends NPay and may terminate it; the user returns.'),
                 ('ASK', 'Which of these ten steps could you explain in detail right now?'),
                 ('EXPECT', 'Usually only a few. By the end, all ten.'),
                 ('CONNECT', 'First, the whole architecture in one picture.'))))

# ================================================================== 1
divider(1, "The complete architecture", "Two perspectives in one picture",
        "One diagram that combines application design and platform architecture.", "Build it up layer by layer.")
P = ['<g class="nd ghost"><rect class="sh" x="0" y="0" width="760" height="300" rx="16"/></g><text class="mono" x="16" y="22">NPAY APP PROCESS</text>',
     box(20, 36, 720, 52, "SwiftUI View", "screens, navigation, user interaction", '1', '', 'phone'),
     box(20, 98, 720, 52, "ViewModel / presentation state", "loading, balance, errors, user actions", '2', '', 'layout'),
     box(20, 160, 720, 52, "Application services / repository", "business coordination, data access", '3', '', 'link'),
     box(20, 224, 350, 56, "Networking", "URLSession", '4', '', 'globe'), box(390, 224, 350, 56, "Storage", "SwiftData, files, Keychain", '4', '', 'db'),
     box(0, 316, 760, 50, "Apple frameworks &amp; iOS services", "SwiftUI, Foundation, Security, lifecycle, graphics", '5', '', 'frameworks'),
     box(0, 376, 760, 50, "Darwin / XNU kernel", "processes, threads, virtual memory, scheduling", '5', '', 'kernel'),
     box(0, 436, 760, 50, "Apple hardware", "", '5', 'solid', 'chip'),
     wire('M760 251H858', '6', 'dash'), '<text class="sm" x="809" y="240" text-anchor="middle">network</text>',
     tall(864, 196, 272, 112, 'bank', "Bank backend", "auth, accounts, transactions", '6')]
S.append(slide("Part 1 &middot; Architecture &middot; conceptual", "NPay: the complete picture", f"""  <div class="body">
    {svg("0 0 1136 488", "The NPay app process holds the SwiftUI view, ViewModel, services, networking and storage, on top of Apple frameworks, the kernel and hardware; the bank backend is a separate system reached through system APIs", "s4arch", P, "max-height:480px")}
    {cues(6)}
  </div>""", notes(('SAY', 'Click by click. Inside the NPay process: the SwiftUI view, the ViewModel and presentation state, application services, then networking and storage. Below it: Apple frameworks and iOS services, the Darwin/XNU kernel and the hardware. Last, the bank backend, a separate system reached through network APIs, not part of the iPhone process.'),
                  ('SAY', 'This diagram mixes two perspectives. Application architecture is how we organize NPay’s code: view, ViewModel, services, networking, storage. Platform architecture is how iOS provides execution, security, frameworks and hardware access. Do not confuse the two.'),
                  ('CONNECT', 'Now walk the day, stage by stage, starting with the launch.'))))

# ================================================================== 2 launch
divider(2, "Stage one: launching NPay", "From the Home Screen to a running app",
        "Lesson 0.1 in seven steps.", "Click through the startup.")
launch = [("SpringBoard", "User taps the app icon", "The Home Screen handles the interaction and requests a launch or activation."),
          ("Launch request", "Launch or activate?", "The system checks whether an NPay process already exists."),
          ("Process", "Process created", "On a cold launch, the OS creates the process and its address space."),
          ("dyld", "Code loaded", "The dynamic loader prepares the executable and its libraries."),
          ("@main", "Swift entry point", "The runtime starts the NPay App type."),
          ("Scene", "Scene created", "iOS creates a scene; WindowGroup supplies the root view."),
          ("First frame", "Dashboard on screen", "SwiftUI evaluates and lays out the views; the first frame appears.")]
S.append(slide("Part 2 &middot; Startup explorer &middot; conceptual", "Launch in seven steps", f"""  <div class="body">
    {stepper(launch, 147, 17.8, "STEP", "s6launch", "Seven launch steps from SpringBoard to the first frame")}
    {cues(6)}
    <div class="gap"></div>
    <div class="rule step" data-label="Checkpoint: who owns the process?">The <b>operating system</b> manages the process. SwiftUI provides app and scene abstractions <b>inside</b> it.</div>
  </div>""", notes(('SAY', 'Step one: SpringBoard, the system UI, handles the tap and requests a launch or activation. Click through the rest: the launch decision, process creation, dyld loading, the Swift entry point, the scene, and the first frame. This is Lesson 0.1 compressed.'),
                  ('ASK', 'Who owns the process?'),
                  ('EXPECT', 'The operating system. SwiftUI provides application and scene abstractions within the running app.'),
                  ('CONNECT', 'Inside that process, SwiftUI builds the dashboard.'))))

# ================================================================== 3 SwiftUI
divider(3, "Stage two: SwiftUI builds the dashboard", "From @main to a view value",
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
      {stages([("<code>@main NPayApp</code>", "the entry-point type"), ("App protocol", "SwiftUI application"), ("WindowGroup", "system-managed windows"), ("DashboardView", "the root view")])}
      <div class="gap"></div>
      <div class="rule step"><code>DashboardView()</code> creates a <b>view value</b>; it does not draw pixels. SwiftUI evaluates, lays out and updates.</div>
    </div>
  </div>""", notes(('SAY', 'The structure: @main NPayApp, conforming to App, whose body is a WindowGroup containing DashboardView.'),
                  ('SAY', 'Calling DashboardView() creates a SwiftUI view value. It does not issue drawing commands; SwiftUI manages evaluating the hierarchy, layout and updates.'),
                  ('CONNECT', 'Now the user does something.'))))

# ================================================================== 4 Check Balance
divider(4, "Stage three: Check Balance", "One tap, seven internal steps",
        "The user taps Check Balance. Lessons 0.2 and 0.5.", "Watch the screen and what happens behind it.")
P = ['<use href="#d-iphone" x="0" y="0" width="200" height="400"/>',
     '<text x="100" y="66" text-anchor="middle" style="font-size:20px;font-weight:800">NPay</text>',
     '<g class="nd"><rect class="sh" x="24" y="84" width="152" height="80" rx="12"/><text class="sm" x="100" y="110" text-anchor="middle">Available balance</text></g>',
     fade("0-4", '<text x="100" y="148" text-anchor="middle" style="font-size:24px;font-weight:700">&#8212;</text>'),
     fade("5", '<text x="100" y="148" text-anchor="middle" style="font-size:16px;font-weight:600">loading&#8230;</text>'),
     fade("6+", '<text x="100" y="148" text-anchor="middle" style="font-size:22px;font-weight:700;fill:var(--teal-ink)">&#8377;25,000</text>'),
     '<g class="nd lit"><rect class="sh" x="24" y="180" width="152" height="40" rx="12"/><text class="sm" x="100" y="205" text-anchor="middle">Check Balance</text></g>']
inside = [("Touch event reaches the app", ""), ("Button action executes", "SwiftUI"), ("ViewModel starts async work", ""), ("Service sends the request", "networking"),
          ("Response decoded", "into a Swift model"), ("Observable state changes", ""), ("SwiftUI updates the balance", "")]
S.append(slide("Part 4 &middot; Tap simulation &middot; conceptual", "What happens when Check Balance is tapped", f"""  <div class="body cols middle" style="grid-template-columns:.55fr 1.45fr">
    {svg("0 0 200 400", "NPay screen: the balance changes from a dash to loading to 25,000 rupees", "s10tap", P, "max-height:430px")}
    <div>
      {stages(inside)}
      <p class="small muted" style="margin:10px 0 0">Illustrates state updates; no real network request.</p>
    </div>
  </div>""", notes(('SAY', 'Click through seven steps and watch the phone. The touch event reaches the app; the SwiftUI Button action runs; the ViewModel starts an asynchronous operation; the networking service sends the request (the screen shows loading); the response is decoded into a model; observable state changes; SwiftUI shows &#8377;25,000.'),
                  ('ASK', 'Does the main thread stay blocked while the bank server responds?'),
                  ('EXPECT', 'Not with properly asynchronous APIs like URLSession and await. The task suspends while the request is pending.'),
                  ('CONNECT', 'Zoom into the request itself.'))))

# ================================================================== 5 API request
divider(5, "Stage four: the API request", "From the view to the bank API",
        "Lesson 0.8: the networking architecture.", "Six layers, then the code.")
P, h = vflow([("phone", "DashboardView", "user interaction"), ("layout", "BalanceViewModel", "loading and presentation state"),
              ("link", "BalanceService", "constructs and performs the request"), ("frameworks", "URLSession", "networking API"),
              ("lock", "HTTPS / TLS", "protected transport"), ("bank", "Bank API", "authorization and account retrieval")], w=470, h=50, gap=14)
SVC = '''import Foundation

struct BalanceResponse: Decodable {
    let balanceMinor: Int64
    let currency: String
}

struct BalanceService {
    func fetchBalance() async throws -> BalanceResponse {
        let url = URL(
            string: "https://api.npay.example/balance"
        )!

        let (data, response) =
            try await URLSession.shared.data(from: url)

        guard let http = response as? HTTPURLResponse,
              http.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }

        return try JSONDecoder().decode(
            BalanceResponse.self,
            from: data
        )
    }
}'''
S.append(slide("Part 5 &middot; Networking &middot; conceptual", "The request path and the service", f"""  <div class="body cols middle" style="grid-template-columns:.95fr 1.25fr">
    <div>
      {svg(f"0 0 470 {h}", "DashboardView, BalanceViewModel, BalanceService, URLSession, HTTPS and the bank API", "s12api", P, "max-height:430px")}
      {cues(6)}
    </div>
    <div>
      {code("BalanceService.swift", SVC, "font-size:11.5px;line-height:1.3;padding:10px 18px")}
      <p class="small muted" style="margin:6px 0 0">Fictional URL. Real banking code also needs authentication, authorization-aware error handling and secure token management.</p>
    </div>
  </div>""", notes(('SAY', 'Click down the path: DashboardView, BalanceViewModel, BalanceService, URLSession, HTTPS and the bank API.'),
                  ('SAY', 'The service builds the URL, awaits URLSession, checks for a 200 status and decodes BalanceResponse. The URL is fictional, and real code needs authentication, authorization-aware error handling and secure token management.'),
                  ('CONNECT', 'Which security mechanisms protect this operation?'))))

# ================================================================== 6 security
divider(6, "Stage five: security protects the operation", "Lesson 0.7 in one view",
        "Several security mechanisms are involved when NPay talks to the bank.", "Six of them.")
sec = [("file", "Code signing", "code integrity, execution requirements"), ("lock", "Sandbox", "restricts the app&rsquo;s resource access"),
       ("key", "Keychain", "protects sensitive credentials"), ("globe", "HTTPS / TLS", "protects network communication"),
       ("bank", "Backend authorization", "decides which account data is accessible"), ("shield", "Data protection", "protects stored data under policy")]
P = []
for i, (ic, t, sub) in enumerate(sec):
    r, c = divmod(i, 3)
    P.append(tall(c * 392, r * 130, 352, 112, ic, t, sub, str(i + 1)))
S.append(slide("Part 6 &middot; Security &middot; conceptual", "Six protections around one request", f"""  <div class="body">
    {svg("0 0 1136 242", "Code signing, sandbox, Keychain, HTTPS and TLS, backend authorization, data protection", "s14sec", P)}
    {cues(6)}
    <div class="gap"></div>
    <div class="rule step" data-label="Critical lesson">Client-side security does <b>not</b> replace <b>server-side authorization</b>. The bank must verify the user may access the requested account.</div>
  </div>""", notes(('SAY', 'Click through: code signing for integrity, the sandbox restricting access, the Keychain protecting credentials, HTTPS protecting the network, backend authorization deciding what data is accessible, and data protection for stored data.'),
                  ('SAY', 'Even if NPay stores tokens securely and uses HTTPS, the bank server must independently verify that the authenticated user is authorized for the requested account.'),
                  ('CONNECT', 'Now the data comes back.'))))

# ================================================================== 7 data returns
divider(7, "Stage six: data returns, SwiftUI updates", "From bytes to pixels",
        "The server responds with JSON. How does it reach the screen?", "Follow it.")
JSON = '''{
  "balanceMinor": 2500000,
  "currency": "INR"
}'''
P, h = vflow([("file", "HTTP response data", ""), ("code", "JSONDecoder", ""), ("db", "BalanceResponse model", ""),
              ("layout", "ViewModel updates balance state", ""), ("eye", "SwiftUI re-evaluates relevant views", ""), ("frame", "Updated balance on screen", "")], w=520, h=46, gap=14)
S.append(slide("Part 7 &middot; Response to screen &middot; conceptual", "UI = f(state)", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    <div>
      <div class="cw"><div class="ch"><span>response.json</span></div><pre class="tree" style="font-size:18px;border-radius:0 0 12px 12px">{E(JSON)}</pre></div>
      <div class="gap"></div>
      <div class="rule step" data-label="UI = f(state)">The interface describes what to show for the current state. It does <b>not</b> mean every change redraws the whole screen.</div>
    </div>
    <div>
      {svg(f"0 0 520 {h}", "Response data, JSONDecoder, BalanceResponse, ViewModel state, SwiftUI re-evaluation, updated balance", "s16ret", P, "max-height:400px")}
      {cues(6)}
    </div>
  </div>""", notes(('SAY', 'The server returns balanceMinor 2,500,000 in INR. Click down: the data goes through JSONDecoder into a BalanceResponse; the ViewModel converts it into a display value and updates observable state; SwiftUI re-evaluates the relevant views; the updated balance appears.'),
                  ('SAY', 'UI equals f of state: a conceptual way to describe declarative UI. It does not imply every state change redraws the whole screen.'),
                  ('CONNECT', 'What should NPay store, and where?'))))

# ================================================================== 8 storage
divider(8, "Stage seven: what should we store?", "Lesson 0.9 applied",
        "Not all NPay data belongs in the same storage system.", "Six pieces of data.")
S.append(slide("Part 8 &middot; Storage map", "Where each piece of data belongs", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Data</th><th>Appropriate storage</th></tr>
      <tr><td>Dark mode preference</td><td>UserDefaults</td></tr>
      <tr><td>Authentication token</td><td>Keychain</td></tr>
      <tr><td>Downloaded statement PDF</td><td>Protected file storage</td></tr>
      <tr><td>Locally saved transaction notes</td><td>SwiftData or another persistence store</td></tr>
      <tr><td>Current screen loading flag</td><td>In-memory ViewModel state</td></tr>
      <tr class="hl"><td>Authoritative account balance</td><td>Bank backend</td></tr>
    </table>
    <div class="gap"></div>
    <p class="small step">For cached balances, show clearly <b>when</b> the data was last verified.</p>
  </div>""", notes(('SAY', 'Six pieces of data, six homes. The preference in UserDefaults, the token in the Keychain, the PDF in protected file storage, notes in SwiftData or similar, the loading flag only in ViewModel memory, and the authoritative balance on the bank backend.'),
                  ('CONNECT', 'A developer proposes a shortcut. Spot the problem.'))))
S.append(slide("Part 8 &middot; Design challenge", "&ldquo;Just put it all in UserDefaults&rdquo;", """  <div class="body">
    <p style="margin:0 0 18px">A developer proposes saving the <b>token</b>, the <b>balance</b> and <b>all transactions</b> in UserDefaults. What is wrong?</p>
    <div class="cols" style="row-gap:16px">
      <div class="card accent step"><span class="label">Authentication token</span><p class="small" style="margin:0">Use appropriate <b>Keychain</b> protections, not ordinary preferences.</p></div>
      <div class="card accent step"><span class="label">Account balance</span><p class="small" style="margin:0">The <b>backend</b> is authoritative; a local copy may be stale.</p></div>
      <div class="card accent step"><span class="label">Transactions</span><p class="small" style="margin:0">A <b>structured persistence</b> mechanism, with data protection and retention.</p></div>
      <div class="card accent step"><span class="label">Preferences</span><p class="small" style="margin:0"><b>UserDefaults</b> is right for small, non-secret settings.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Principle">Choose storage by <b>sensitivity</b>, <b>size</b>, <b>lifecycle</b> and <b>consistency</b> needs, not because an API is easy.</div>
  </div>""", notes(('ASK', 'A developer proposes saving the authentication token, account balance and all transactions into UserDefaults. What is wrong?'),
                  ('EXPECT', 'Different data has different security, persistence and performance requirements.'),
                  ('SAY', 'Click through: the token needs Keychain protection; the balance belongs to the backend and a local copy may be stale; transactions need structured persistence with data protection and retention; only preferences belong in UserDefaults. Choose storage by sensitivity, size, lifecycle and consistency, not convenience.'),
                  ('CONNECT', 'Now the user leaves NPay.'))))

# ================================================================== 9 lifecycle
divider(9, "Stage eight: the user leaves", "Lesson 0.3 in motion",
        "The user presses Home or switches apps. What happens to NPay?", "Follow the transitions.")
lc = [("Active", "Active", "Running", "NPay is visible and responding to the user."),
      ("Inactive", "Inactive", "Running", "Still in the foreground, but temporarily not receiving events."),
      ("Background", "Background", "Running briefly", "No longer visible; execution may continue briefly."),
      ("Suspended", "Background", "Suspended", "Kept in memory, but no code runs."),
      ("Terminated", "None", "Terminated", "iOS reclaimed the memory; the process is gone.")]
P = []
lt = lambda i: str(i) if i < len(lc) - 1 else f"{i}+"
for i, (chip, *_r) in enumerate(lc):
    P.append(box(i * 230, 0, 212, 52, chip, '', lt(i)))
for i, (chip, sp, pr, d) in enumerate(lc):
    P.append(fade(lt(i), f'<text x="0" y="110" style="font-size:26px;font-weight:700">{chip}</text><text x="0" y="142" style="font-size:19px;font-weight:400">{d}</text>'
                  + box(0, 168, 556, 66, "Scene phase", sp, None, '') + box(580, 168, 556, 66, "Process execution", pr, None, 'alert' if pr == 'Terminated' else '')))
S.append(slide("Part 9 &middot; Lifecycle journey &middot; conceptual", "From active to terminated", f"""  <div class="body">
    {svg("0 0 1136 236", "Active, inactive, background, suspended, terminated, each with its scene phase and process execution state", "s21lc", P)}
    {cues(4)}
    <div class="gap"></div>
    <div class="rule step" data-label="Watch the words">SwiftUI scene phases are <code>.active</code>, <code>.inactive</code>, <code>.background</code>. <b>Suspended</b> is a process condition, not a scene phase.</div>
  </div>""", notes(('SAY', 'Active: NPay is visible and responding; the scene phase is active, the process running. Click through: inactive, background with brief execution, suspended with no code running, and terminated. One possible progression; iOS does not guarantee every app passes through each state in order.'),
                  ('SAY', 'The three scene phases are active, inactive and background. Suspended describes the process. This matters when someone asks whether their background code keeps running.'),
                  ('CONNECT', 'While navigating, objects come and go too.'))))

# ================================================================== 10 memory
divider(10, "Stage nine: memory during navigation", "Lesson 0.6: who owns the ViewModel?",
        "The user opens transaction history; NPay creates a ViewModel holding transactions. When they navigate away, is it destroyed?", "Look at the ownership.")
P = [box(0, 0, 420, 54, "TransactionHistoryView", "", '1', '', 'phone'), wire(f'M210 54V74{head(210, 74, "d")}'),
     box(0, 80, 420, 54, "TransactionViewModel", "", '2', '', 'layout'), wire(f'M210 134V154{head(210, 154, "d")}'),
     box(0, 160, 420, 54, "TransactionService", "", '3', '', 'link')]
TVM = '''class TransactionViewModel {
    var onRefresh: (() -> Void)?

    func configure() {
        onRefresh = { [weak self] in
            self?.refresh()
        }
    }

    func refresh() {
        print("Refreshing transactions")
    }

    deinit {
        print("ViewModel deinitialized")
    }
}'''
S.append(slide("Part 10 &middot; Ownership &middot; conceptual", "A ViewModel and its closure", f"""  <div class="body cols middle" style="grid-template-columns:.9fr 1.2fr">
    <div>
      {svg("0 0 420 216", "TransactionHistoryView owns TransactionViewModel, which uses TransactionService", "s24own", P)}
      {cues(3)}
      <div class="gap"></div>
      <p class="small">A stored closure that strongly captures the ViewModel creates a <b>retain cycle</b>. <code>[weak self]</code> avoids it.</p>
    </div>
    {code("TransactionViewModel.swift", TVM, "font-size:14px")}
  </div>""", notes(('SAY', 'Click down: the view owns the ViewModel, which uses the service. If the ViewModel stores a closure that strongly captures the ViewModel, a retain cycle can form; this code uses weak capture to avoid it.'),
                  ('ASK', 'Does navigating away from a screen guarantee its ViewModel’s deinit runs immediately?'),
                  ('EXPECT', 'No. It may still be legitimately retained elsewhere. Navigation and object lifetime are related but not identical.'),
                  ('CONNECT', 'Finally, the user comes back.'))))

# ================================================================== 11 return
divider(11, "Stage ten: the user returns", "Two possible situations",
        "The user returns to NPay after several minutes.", "Survived, or terminated?")
S.append(slide("Part 11 &middot; Return scenarios", "Warm activation or cold launch", """  <div class="body">
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

# ================================================================== 12 complete flow
divider(12, "The complete flow", "One user action, many systems",
        "Reconstruct the entire NPay journey.", "Twelve steps.")
flow = [("User taps NPay", "SpringBoard, launch coordination"), ("iOS starts or activates the app", "process, dyld, Swift entry point"),
        ("SwiftUI shows DashboardView", "scene, state, evaluation, rendering"), ("User taps Check Balance", "touch event, main thread, action"),
        ("ViewModel requests data", "asynchronous app logic"), ("Service contacts the backend", "URLSession, HTTPS, authentication"),
        ("Server returns authorized data", "business rules, account data"), ("ViewModel updates state", "decoding, formatting, errors"),
        ("SwiftUI updates the screen", "reconciliation, layout, presentation"), ("App persists selected data", "SwiftData, files, Keychain, preferences"),
        ("User leaves the app", "scene lifecycle, background, suspension"), ("User returns", "warm activation or cold launch, restoration")]
P = []
for i, (t, sub) in enumerate(flow):
    r, c = divmod(i, 3)
    P.append(box(c * 386, r * 104, 362, 76, f"{i + 1}. {t}", sub, str(i + 1)))
S.append(slide("Part 12 &middot; End to end &middot; conceptual", "The whole day in twelve steps", f"""  <div class="body">
    {svg("0 0 1136 388", "Twelve steps from tapping NPay through launch, the dashboard, the balance request, the server, state update, rendering, storage, leaving and returning", "s29flow", P, "max-height:470px")}
    {cues(12)}
  </div>""", notes(('SAY', 'Click through all twelve. Each step names the lesson behind it: launch coordination and process startup from 0.1; SwiftUI from 0.4 and 0.5; the request from 0.2 and 0.8; security from 0.7; persistence from 0.9; leaving and returning from 0.3; and object lifetimes from 0.6.'),
                  ('CONNECT', 'Now think like a senior engineer reviewing someone else’s design.'))))

# ================================================================== review (architecture review, 5)
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Architecture review: find the mistakes</h2>
  </div>
""" + notes(('SAY', 'Five design decisions. For each, decide: good design, or a problem? Commit before it is revealed.')) + "</section>\n\n")
QA = [("clock", "A developer performs a synchronous five-second calculation directly inside a SwiftUI Button action.", "Problem",
       "It blocks the main actor: the UI cannot respond for five seconds. Move heavy work off the main actor.", "Assuming async UI frameworks protect you from blocking code.", "Most spot it; ask where the work should run."),
      ("key", "The authentication token is saved in UserDefaults for convenience.", "Problem",
       "Tokens are credentials. Store them with Keychain protections.", "Choosing storage by convenience.", "Most spot it."),
      ("bank", "Offline, the app shows yesterday&rsquo;s cached balance as the current balance.", "Problem",
       "The backend is authoritative. Show cached data with its last-verified time.", "Presenting stale financial data as current.", "Some think showing something is always better."),
      ("send", "A failed money-transfer POST is retried automatically, with no idempotency protection.", "Problem",
       "If the first attempt actually succeeded, the retry can transfer the money twice.", "Retrying every failure by reflex.", "Many accept automatic retries."),
      ("layers", "The app relies on its in-memory state to still be there when the user returns.", "Problem",
       "iOS may have terminated the process. Persist what matters and handle a cold launch.", "Assuming the process stays alive.", "Some assume backgrounded apps keep running.")]
N = len(QA)
for i, (ic, q, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    title = html.unescape(re.sub('<[^>]+>', '', q))
    S.append(f"""<section class="slide question" data-title="{E(title, quote=True)}">
  <div class="q-top">
    <p class="kicker">Architecture review &middot; {i + 1} of {N}</p>
    <div class="q-dots" aria-hidden="true">{dots}</div>
  </div>
  <div class="body">
    <div class="q-row">
      <div class="q-card">
        <div class="q-icon"><svg viewBox="0 0 24 24"><use href="#i-{ic}"/></svg></div>
        <span class="label">Good design or problem?</span>
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
""" + notes(('ASK', 'Good design, or a problem? Quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next design.' if i < N - 1 else 'Step back and see the whole module.')) + "</section>\n\n")

# ================================================================== module map + challenge
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
                  ('CONNECT', 'Now prove you can connect them.'))))
S.append(slide("Your challenge", "Explain the whole journey", """  <div class="body center">
    <div style="max-width:900px;margin:0 auto">
      <p class="lead" style="font-size:24px;line-height:1.6">&ldquo;I tap NPay, open my account balance, switch to another app, and return ten minutes later. Explain the entire journey, from the <b style="color:var(--teal)">operating system</b> to SwiftUI, networking, storage, security and lifecycle.&rdquo;</p>
    </div>
    <div class="gap-lg"></div>
    <div class="step anim-up">
      <div class="cols c3" style="text-align:left;grid-template-columns:repeat(4,1fr)">
        <div class="card accent"><span class="label">Operating system</span><p class="small" style="margin:0">Process, lifecycle, sandbox, scheduling</p></div>
        <div class="card accent"><span class="label">Frameworks</span><p class="small" style="margin:0">SwiftUI, URLSession, Security, SwiftData</p></div>
        <div class="card accent"><span class="label">Application code</span><p class="small" style="margin:0">Views, ViewModels, services</p></div>
        <div class="card accent"><span class="label">Backend</span><p class="small" style="margin:0">Authorization, accounts, truth</p></div>
      </div>
    </div>
  </div>""", notes(('SAY', 'Answer without looking at the architecture diagram. A strong answer separates the responsibility of the operating system, the frameworks, the application code and the backend.'),
                  ('CONNECT', 'That completes the foundation.'))))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Foundation module complete</p>
    <h2>iOS Architecture<br>Foundation</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Unit 1, Swift Language Mastery</p>
  </div>
""" + notes(('SAY', 'Ten connected lessons: app startup, system architecture, lifecycle, UIKit and SwiftUI, threads, concurrency fundamentals, ARC, security, networking, persistence and complete application flow. This is the conceptual foundation; practical mastery comes from implementing, debugging and measuring these mechanisms in Xcode.'),
            ('SAY', 'Next, Unit 1: Swift Language Mastery, in the same deep style but with executable code, progressively building the NPay domain model. Swift design and compilation; variables and the type system; optionals; functions and closures; structs, classes and value semantics; enums, protocols and extensions; generics and errors; ARC in practice; async/await, actors and structured concurrency; and the NPay domain model.')) + "</section>\n\n")

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
