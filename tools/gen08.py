"""Generates decks/unit-0/lesson-0.8/index.html from the Lesson 0.8 text only (PocketBank -> NPay)."""
import html, os, re, sys
OUT08 = sys.argv[1]
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


def vflow(items, w=560, h=58, gap=24):
    P = []
    for i, (ic, t, sub) in enumerate(items):
        y = i * (h + gap)
        P.append(box(0, y, w, h, t, sub, str(i + 1), '', ic))
        if i < len(items) - 1:
            P.append(wire(f'M{w / 2:g} {y + h}V{y + h + gap - 6}{head(w / 2, y + h + gap - 6, "d")}'))
    return P, len(items) * (h + gap) - gap


def chooser(items, top, chip_w, gap, label, tid, title):
    """Chips lit one per click; below, the matching result box."""
    P = []
    for i, (chip, *_r) in enumerate(items):
        P.append(box(i * (chip_w + gap), 0, chip_w, 52, chip, '', str(i) if i < len(items) - 1 else f"{i}+"))
    for i, (chip, t, d, cls) in enumerate(items):
        P.append(fade(str(i) if i < len(items) - 1 else f"{i}+",
                      f'<text class="mono" x="0" y="{top}">{label}</text>' + box(0, top + 14, 1136, 66, t, d, None, cls)))
    return svg(f"0 0 1136 {top + 82}", title, tid, P)


def stages(items):
    return '<div class="points v stages">' + ''.join(
        f'<div class="step"><span class="q-num">{i + 1}</span><span><b>{t}</b><small>{d}</small></span></div>' for i, (t, d) in enumerate(items)) + '</div>'


S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.8</p>
    <h1 style="font-size:52px;line-height:1.05">iOS Networking Architecture:<br>From App to Server</h1>
    <p class="lead" style="max-width:680px">When NPay shows your balance, where does it come from, and how does it reach the iPhone?</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'We have covered how iOS starts an app, manages its lifecycle, handles threads, manages memory and protects data. Now: when NPay shows your bank balance, where does it come from and how does it reach the iPhone? We follow one network request from a button tap to the server and back to the SwiftUI screen.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")
outs = [("bank", "Who owns the <b>authoritative</b> balance"), ("layers", "The layers from <b>SwiftUI</b> to the <b>server</b>"),
        ("globe", "What an <b>HTTP request</b> is, where <b>HTTPS</b> fits, and where the <b>token</b> comes from"), ("link", "How <b>URLSession</b> and <b>await</b> work together"),
        ("code", "How <b>Codable</b> turns JSON into a model"), ("cross", "Why <b>error handling</b> is part of the architecture")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.8 &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'The goal: explain the complete path, SwiftUI to ViewModel to networking service to URLSession to HTTPS to the server, and back as JSON to a model, the ViewModel and SwiftUI. Plus why networking is asynchronous, why security is layered and why error handling is architecture.'),
                 ('CONNECT', 'First, where this lesson sits on the NPay map.'))))
S.append(map_slide('0.8', 'Today: the network path', ('service', 'frameworks', 'https', 'server'),
                   'Lesson 0.7: the sandbox and signing protect NPay; its token belongs in the Keychain.',
                   'Follow one &ldquo;Refresh balance&rdquo; from the Service, through URLSession and HTTPS, to the bank and back.',
                   'Last time: the walls around NPay, and the Keychain for its token. Today we leave the device. The teal path is today: the Service in NPay, Apple&rsquo;s URLSession in the frameworks, HTTPS on the wire, and the bank&rsquo;s API server, which owns the real balance. The View and ViewModel at the top start and finish the trip.',
                   'Start with the problem.'))

# ================================================================== 1
divider(1, "First, understand the problem", "Where does the balance live?",
        "Open NPay and look at the balance. Where does that number actually live?", "Look at the screen.")
P = ['<use href="#d-iphone" x="0" y="0" width="210" height="420"/>',
     '<text x="105" y="70" text-anchor="middle" style="font-size:20px;font-weight:800">NPay</text>',
     '<g class="nd"><rect class="sh" x="26" y="88" width="158" height="78" rx="12"/><text class="sm" x="105" y="116" text-anchor="middle">Available balance</text><text x="105" y="148" text-anchor="middle" style="font-size:22px;font-weight:700">&#8377;25,000</text></g>',
     '<g class="nd lit"><rect class="sh" x="26" y="178" width="158" height="40" rx="12"/><text class="sm" x="105" y="203" text-anchor="middle">Refresh balance</text></g>',
     '<text class="mono" x="26" y="250">RECENT TRANSACTION</text>',
     '<g class="nd"><rect class="sh" x="26" y="260" width="158" height="44" rx="10"/><text class="sm" x="38" y="287">Coffee Shop</text><text class="sm" x="174" y="287" text-anchor="end">&#8722;&#8377;250</text></g>']
S.append(slide("Part 1 &middot; The problem", "Where does &#8377;25,000 come from?", f"""  <div class="body cols middle" style="grid-template-columns:.7fr 1.3fr">
    {svg("0 0 210 420", "Illustrative NPay screen: available balance 25,000 rupees, a Refresh balance button, a recent coffee shop transaction of 250 rupees", "s4scr", P, "max-height:440px")}
    <div>
      <p style="font-size:24px;margin:0 0 18px">Is the balance stored in the <b>SwiftUI screen</b>, in <b>iPhone memory</b>, or on the <b>bank&rsquo;s server</b>?</p>
      <div class="rule step" data-label="The answer">The <b>authoritative</b> balance belongs to the bank&rsquo;s backend. The app may hold a <b>copy</b> to display it.</div>
      <div class="gap"></div>
      {points([("bank", "Server", "maintains authoritative account information"), ("globe", "Networking layer", "communicates with the backend"), ("phone", "SwiftUI", "displays the result")], cls="v", label="Three responsibilities")}
    </div>
  </div>""", notes(('ASK', 'Is the bank balance stored inside the SwiftUI screen, in iPhone memory, or on the bank’s server?'),
                  ('EXPECT', 'The authoritative balance normally belongs to the bank’s backend. The app may temporarily hold a copy to display it.'),
                  ('SAY', 'That gives three responsibilities: the server maintains authoritative account information, the networking layer communicates with the backend, and SwiftUI displays the result.'),
                  ('CONNECT', 'Now follow a single tap all the way to the server and back.'))))

# ================================================================== 3
divider(2, "What happens when the user taps Refresh?", "One request, nine steps",
        "Follow the request out to the server and back.", "Nine steps, one per click.")
steps = [("SwiftUI", "User taps Refresh", "The button action starts an asynchronous operation."),
         ("ViewModel", "Loading starts", "DashboardViewModel sets the loading state and calls BalanceService."),
         ("Service", "Request is built", "The service builds the URL, method and headers."),
         ("URLSession", "Request is sent", "URLSession performs the request; the task suspends at await."),
         ("HTTPS", "Encrypted transport", "TLS protects the request on its way to the server."),
         ("Server", "Server responds", "The bank API checks authorization and returns JSON."),
         ("Service", "Response decoded", "The service validates the status and decodes the JSON into a model."),
         ("ViewModel", "State updates", "The ViewModel formats &#8377;25,000 and clears loading."),
         ("SwiftUI", "Screen updates", "SwiftUI re-renders with the new balance.")]
P = []
for i, (chip, *_r) in enumerate(steps):
    P.append(box(i * 126.5, 0, 114, 52, chip, '', str(i) if i < 8 else "8+"))
for i, (_c, t, d) in enumerate(steps):
    P.append(fade(str(i) if i < 8 else "8+", f'<text class="mono" x="0" y="104">STEP {i + 1} OF 9</text><text x="0" y="140" style="font-size:26px;font-weight:700">{t}</text><text x="0" y="174" style="font-size:19px;font-weight:400">{d}</text>'))
S.append(slide("Part 2 &middot; Request journey &middot; conceptual", "A Refresh tap, step by step", f"""  <div class="body">
    {svg("0 0 1136 186", "Nine steps: SwiftUI, ViewModel, service, URLSession, HTTPS, server, service, ViewModel, SwiftUI", "s8journey", P)}
    {cues(8)}
    <div class="gap"></div>
    <div class="rule step">SwiftUI does <b>not</b> implement HTTP: <b>URLSession</b> is a Foundation API. MVVM is a way to organize code, not an iOS requirement.</div>
  </div>""", notes(('SAY', 'Step one: the user taps Refresh and the button action starts an asynchronous operation. Click through: the ViewModel starts loading, the service builds the request, URLSession sends it while the task suspends, TLS protects it in transit, the server checks authorization and returns JSON, the service validates and decodes it, the ViewModel updates state, and SwiftUI re-renders.'),
                  ('ASK', 'At which step is the main thread free to handle other taps?'),
                  ('EXPECT', 'From step 4 until the response returns: the task is suspended, not blocking a thread.'),
                  ('SAY', 'Notice who does what. SwiftUI does not implement HTTP networking; URLSession, a Foundation API, does. And MVVM is a code organization pattern, not something iOS requires.'),
                  ('CONNECT', 'Look closer at what is actually sent in step 3.'))))

# ================================================================== 4
divider(3, "What is an HTTP request?", "A structured message from client to server",
        "An HTTP request is a structured message sent by a client to a server.", "Here is one.")
REQ = '''GET /api/accounts/123/balance HTTP/1.1
Host: api.npay.example
Accept: application/json
Authorization: Bearer <token>'''
S.append(slide("Part 3 &middot; HTTP request", "Anatomy of a request", f"""  <div class="body cols middle" style="grid-template-columns:1.2fr 1fr">
    <div class="cw"><div class="ch"><span>HTTP request</span></div><pre class="tree" style="font-size:18px;border-radius:0 0 12px 12px">{E(REQ)}</pre></div>
    <div>
      {stages([("Method", "GET: what to do"), ("Resource path", "/api/accounts/123/balance"), ("Headers", "host, accepted format, authorization")])}
      <div class="gap"></div>
      <div class="rule step" data-label="Sensitive">The bearer <b>token</b> is a credential. Never log or expose it.</div>
    </div>
  </div>""", notes(('SAY', 'The request contains a method, a resource path and headers: here GET for the balance resource, the host, the accepted response format, and an Authorization header carrying a bearer token.'),
                  ('SAY', 'In real applications the bearer token is a sensitive credential and must never be logged or exposed.'),
                  ('CONNECT', 'GET is one of several methods.'))))
S.append(slide("Part 3 &middot; Methods", "Common HTTP methods", """  <div class="body top">
    <table class="tbl">
      <tr><th>Method</th><th>Typical purpose</th><th>Idempotent?</th></tr>
      <tr><td><code>GET</code></td><td>Retrieve a resource</td><td>Yes</td></tr>
      <tr><td><code>POST</code></td><td>Submit data or initiate an operation</td><td>No</td></tr>
      <tr><td><code>PUT</code></td><td>Replace a resource</td><td>Yes</td></tr>
      <tr><td><code>PATCH</code></td><td>Partially update a resource</td><td>Not guaranteed</td></tr>
      <tr><td><code>DELETE</code></td><td>Request deletion</td><td>Yes</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Idempotent">Sending the request <b>twice</b> has the same effect as sending it <b>once</b>. Methods describe intent; the server still decides and enforces <b>authorization</b>.</div>
  </div>""", notes(('SAY', 'GET retrieves, POST submits or starts an operation, PUT replaces, PATCH partially updates, DELETE requests deletion.'),
                  ('SAY', 'The last column matters for retries. A request is idempotent when sending it twice has the same effect as sending it once. GET, PUT and DELETE are defined that way; POST is not; PATCH is not guaranteed. These describe intent; the server decides how to process each request and enforces authorization. Unit 05, lesson 5.1, goes deeper.'),
                  ('CONNECT', 'How is the request protected on its way?'))))

# ================================================================== 5
divider(4, "Where does HTTPS fit?", "Protecting data in transit",
        "NPay must protect data while it travels over the network. HTTPS uses TLS for authenticated, encrypted communication.", "See where it sits.")
P = [tall(0, 0, 300, 110, "phone", "iPhone", "NPay"), tall(836, 0, 300, 110, "bank", "Bank server", "backend API"),
     wire(f'M306 55H830{head(830, 55, "r")}', "1+"), wire(f'M830 75H306{head(306, 75, "l")}', "1+"),
     fade("1+", '<g class="nd lit"><rect class="sh" x="418" y="16" width="300" height="34" rx="10"/><use href="#i-lock" x="432" y="22" width="22" height="22"/><text class="sm" x="464" y="38">HTTPS / TLS</text></g>')]
S.append(slide("Part 4 &middot; HTTPS &middot; conceptual", "An encrypted, authenticated channel", f"""  <div class="body">
    {svg("0 0 1136 112", "NPay on the iPhone talks to the bank server over HTTPS with TLS", "s13tls", P)}
    {cues(1)}
    <div class="gap-lg"></div>
    <p>TLS protects data <b>in transit</b> and <b>authenticates the server</b> under the TLS trust model.</p>
    <div class="rule step" data-label="Important distinction">HTTPS protects the <b>transport</b>. The app still needs secure authentication, authorization, token handling and backend security.</div>
  </div>""", notes(('SAY', 'Click: HTTPS uses TLS to protect data in transit and to authenticate the server under the TLS trust model.'),
                  ('ASK', 'Is HTTPS enough to make a banking app secure?'),
                  ('EXPECT', 'No. It protects the connection. Authentication, authorization, token handling and backend security are still needed, as in Lesson 0.7.'),
                  ('SAY', 'iOS also pushes apps toward HTTPS: App Transport Security expects secure connections by default. Unit 07, lesson 7.6, covers TLS, ATS and certificate trust.'),
                  ('CONNECT', 'HTTPS carries the sign-in too. Where does the bearer token come from?'))))
steps = [("bank", "User opens NPay", "the signed app runs inside its sandbox"), ("user", "User signs in", "credentials go to the backend over HTTPS"),
         ("globe", "Backend returns a token", "the app checks the response"), ("key", "Token goes in the Keychain", "never UserDefaults (Lesson 0.7)"),
         ("send", "Later requests carry it", "Authorization: Bearer &lt;token&gt;")]
P, h = vflow(steps, w=640, h=54, gap=18)
P[-1] = P[-1].replace('data-lit="5"', 'data-lit="5+"')
S.append(slide("Part 4 &middot; Signing in &middot; conceptual", "Where the token comes from", f"""  <div class="body cols middle" style="grid-template-columns:1.15fr 1fr">
    {svg(f"0 0 640 {h}", "Open the signed sandboxed app, sign in over HTTPS, receive a token, store it in the Keychain, send it with later requests", "s14log", P, "max-height:400px")}
    <div>
      {cues(5)}
      <div class="rule step" data-label="401 means">The token is missing, invalid or <b>expired</b>: ask the user to sign in again. Production apps also need backend authorization, token refresh and session handling.</div>
    </div>
  </div>""", notes(('SAY', 'Click through a sign-in at a conceptual level. The user opens NPay, a signed app running in its sandbox. The user signs in, and the credentials go to the backend over HTTPS. The backend returns a token, which the app checks. The token goes into the Keychain, never UserDefaults, as in Lesson 0.7. Every later request carries it in the Authorization header we just saw.'),
                  ('SAY', 'When the server answers 401, the token is missing, invalid or expired, so the app asks the user to sign in again. This is only one part of secure banking: backend authorization, token lifecycle and refresh, session handling, fraud controls and threat modeling all matter. Unit 05, lesson 5.5, builds token refresh; Unit 07, lesson 7.10, builds the secure login.'),
                  ('CONNECT', 'Now the code that sends the request: URLSession.'))))

# ================================================================== 6
divider(5, "What is URLSession?", "Apple&rsquo;s API for network transfers",
        "URLSession is Apple’s API for performing network data transfers.", "Here is a request in code.")
FETCH = '''import Foundation

struct BalanceService {
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
S.append(slide("Part 5 &middot; URLSession", "Fetching the balance", f"""  <div class="body cols middle" style="grid-template-columns:1.25fr 1fr">
    <div>
      {code("BalanceService.swift", FETCH, "font-size:13px")}
      <p class="small muted" style="margin:8px 0 0">The URL is fictional; no authentication header yet. <code>Balance</code> is defined in Part 6.</p>
    </div>
    {stages([("Create the URL", ""), ("Ask URLSession", "to perform the request"), ("Suspend at await", "while the operation is pending"),
             ("Receive", "the response or an error"), ("Validate", "any 2xx status"), ("Decode", "into a Balance (Part 6)")])}
  </div>""", notes(('SAY', 'Six steps: create the URL, ask URLSession to perform the request, suspend at await while it is pending, receive the response or an error, validate the response, and decode it. Validation accepts any status from 200 up to 299, not only 200: a 2xx code means success. Anything else becomes an error the ViewModel can show.'),
                  ('ASK', 'Does await mean a thread is blocked until the response arrives?'),
                  ('EXPECT', 'No. The asynchronous task suspends while the networking operation proceeds, as in Lesson 0.5.'),
                  ('SAY', 'Unit 05, lesson 5.2, builds the full service with URLRequest, headers and timeouts.'),
                  ('CONNECT', 'The server answered with JSON bytes. How do they become a Swift value?'))))

# ================================================================== 7
divider(6, "What is Codable?", "From JSON to a Swift model",
        "Servers commonly return JSON. Swift can decode it into a model.", "Here is the response.")
JSON = '''{
  "accountId": "123",
  "currency": "INR",
  "balanceMinor": 2500000
}'''
DEC = '''struct Balance: Decodable {
    let accountId: String
    let currency: String
    let balanceMinor: Int64
}

// BalanceService ends with exactly this step:
func decode(_ data: Data) throws -> Balance {
    try JSONDecoder().decode(Balance.self, from: data)
}'''
S.append(slide("Part 6 &middot; Codable", "Decoding the balance", f"""  <div class="body">
    <div class="cols" style="align-items:start">
      <div class="cw"><div class="ch"><span>response.json</span></div><pre class="tree" style="font-size:17px;border-radius:0 0 12px 12px">{E(JSON)}</pre></div>
      {code("Balance.swift", DEC, "font-size:15px")}
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Minor units"><code>balanceMinor</code> is in the smallest currency unit: 2,500,000 paise is <b>&#8377;25,000</b>. Integer minor units avoid floating-point errors in money.</div>
  </div>""", notes(('SAY', 'The JSON has an account ID, a currency and balanceMinor, the amount in the smallest unit. For INR, 2,500,000 paise is &#8377;25,000. A Decodable struct, Balance, has matching properties, and JSONDecoder in BalanceService turns the bytes into a Balance. If a key is missing or has the wrong type, decoding throws.'),
                  ('SAY', 'Integer minor units, or an appropriate decimal type, avoid the floating-point issues that are dangerous in financial calculations.'),
                  ('CONNECT', 'How does that model reach the screen? MVVM.'))))

# ================================================================== 8
divider(7, "Connecting networking to SwiftUI", "MVVM in the request path",
        "Four layers, each with one job.", "Here they are.")
items = [("phone", "View", "displays balance and loading state"), ("layout", "ViewModel", "coordinates the call and updates observable state"),
         ("link", "Service", "uses URLSession and decodes responses"), ("bank", "Server", "returns authorized account information")]
P, h = vflow(items, w=520, h=56, gap=20)
VM = '''@MainActor @Observable
final class DashboardViewModel {
    var balanceText = "—"
    var errorMessage: String?
    private let service = BalanceService()

    func refreshBalance() async {
        do {
            let balance = try await service.fetchBalance()
            balanceText = (Decimal(balance.balanceMinor) / 100)
                .formatted(.currency(code: "INR"))
        } catch { errorMessage = error.localizedDescription }
    }
}'''
S.append(slide("Part 7 &middot; MVVM &middot; conceptual", "A ViewModel in the request path", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.2fr">
    <div>
      {svg(f"0 0 520 {h}", "View, ViewModel, service, server", "s20mvvm", P, "max-height:300px")}
      {cues(4)}
      <p class="small muted" style="margin:10px 0 0">The view owns it: <code>@State private var model = DashboardViewModel()</code></p>
    </div>
    {code("DashboardViewModel.swift", VM, "font-size:14px")}
  </div>""", notes(('SAY', 'Click down: the view displays the balance and loading state; the ViewModel coordinates the API call and updates observable state; the service uses URLSession and decodes; the server returns authorized account information.'),
                  ('SAY', 'DashboardViewModel is @MainActor, so its state changes happen on the main actor, and @Observable, so SwiftUI redraws when balanceText changes. It awaits BalanceService, formats the minor units as rupees for display, and on error stores a message. Formatting is the ViewModel’s job, not the view’s.'),
                  ('LIVE DEMO', 'Extend the ViewModel in Xcode: add var isLoading = false; at the top of refreshBalance set isLoading = true and add defer { isLoading = false }, so loading clears however the function exits. Inject the service through init(service: BalanceService = BalanceService()). In DashboardView, own it with @State private var model = DashboardViewModel(), show ProgressView() while model.isLoading, Text(model.balanceText) otherwise, and a Button("Refresh balance") { Task { await model.refreshBalance() } }. Unit 04, lesson 4.5, covers injection properly.'),
                  ('CONNECT', 'Not every request succeeds. What then?'))))

# ================================================================== 9
divider(8, "When the network fails", "Errors are part of the architecture",
        "A production app must handle more than successful responses.", "Five outcomes, one per click.")
fails = [("Success", "&#8377;25,000", "The server responds with valid account data.", 'lit'),
         ("No network", "You&rsquo;re offline", "No connection: show the last known balance as possibly out of date, and offer retry.", ''),
         ("HTTP 401", "Please sign in again", "Unauthorized: the token is missing, invalid or expired.", ''),
         ("Timeout", "Taking longer than expected", "No response in time: the request&rsquo;s outcome may be unknown.", ''),
         ("HTTP 500", "Something went wrong", "A server error: not the user&rsquo;s fault; try again later.", 'alert')]
S.append(slide("Part 8 &middot; Failure explorer &middot; illustrative", "Five possible outcomes", f"""  <div class="body">
    {chooser(fails, 104, 211, 20, "WHAT THE USER SEES", "s23fail", "Success, no network, 401 unauthorized, timeout and 500 server error, each with what the user sees")}
    {cues(4)}
    <div class="gap"></div>
    <div class="rule step" data-label="Retries">Do not retry every failure automatically. Consider whether the request is <b>idempotent</b> (Part 3), authentication and rate limits. Retrying a <b>money transfer</b> without idempotency protection can cause serious problems.</div>
  </div>""", notes(('SAY', 'Success: the server returns valid data. Click through: no network connection, 401 unauthorized, a timeout, and a 500 server error. Each needs a different message and a different next step.'),
                  ('SAY', 'Do not retry every failed request automatically. Retries must consider HTTP semantics, whether the request is idempotent, authentication, rate limits and the business operation. A timed-out POST may already have moved the money. Unit 05, lesson 5.6, covers timeouts, retries and backoff.'),
                  ('ASK', 'Should every failed money-transfer POST be retried automatically?'),
                  ('EXPECT', 'No. Without idempotency protection a retry can transfer the money twice.'),
                  ('CONNECT', 'One more case: the user leaves the app mid-request.'))))

# ================================================================== 10
divider(9, "Networking and background execution", "Connecting to Lesson 0.3",
        "If the user starts a download and backgrounds the app, what happens?", "Two kinds of session.")
S.append(slide("Part 9 &middot; Background transfers", "What happens when the app is backgrounded?", """  <div class="body">
    <div class="cols stretch">
      <div class="card step"><span class="label">Normal foreground request</span><p>Not automatically guaranteed to <b>continue indefinitely</b> once the app is suspended.</p></div>
      <div class="card accent step"><span class="label">Background URLSession</span><p><b>Uploads and downloads</b> only, handed to the system so they can finish while NPay is suspended or terminated, on the system&rsquo;s schedule.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Important">It is <b>not</b> a way to keep your own code running, and if the user <b>force-quits</b> NPay from the app switcher, its background transfers are <b>cancelled</b>.</div>
  </div>""", notes(('SAY', 'A normal foreground URLSession request is not guaranteed to continue indefinitely after the app is backgrounded and suspended. For transfers that must survive suspension or even termination by the system, iOS provides background URLSession configurations. They support upload and download tasks only, not ordinary data tasks, and the system schedules them.'),
                  ('SAY', 'Background URLSession is not a way to run arbitrary code after suspension. And if the user force-quits the app from the app switcher, the system cancels its background transfers. Unit 05, lesson 5.8, builds one; Unit 10, lesson 10.7, covers BackgroundTasks.'),
                  ('CONNECT', 'One last look at the whole path.'))))

# ================================================================== final understanding
chain = ["SwiftUI", "ViewModel", "Service", "URLSession", "HTTPS", "Server", "JSON", "Model", "ViewModel", "SwiftUI"]
P = []
for i, t in enumerate(chain):
    r, c = divmod(i, 5)
    x = c * 228 if r == 0 else (4 - c) * 228
    y = r * 100
    P.append(f'<g class="nd pass" data-lit="1" style="--d:{i * .12:.2f}s"><rect class="sh" x="{x}" y="{y}" width="196" height="56" rx="12"/><text x="{x + 98}" y="{y + 34}" text-anchor="middle">{t}</text></g>')
    if c < 4:
        P.append(wire(f'M{x + 200} {y + 28}H{x + 222}{head(x + 222, y + 28, "r")}') if r == 0 else wire(f'M{x - 4} {y + 28}H{x - 26}{head(x - 26, y + 28, "l")}'))
P.append(wire(f'M1010 56V94{head(1010, 94, "d")}'))
S.append(slide("Final understanding", "The complete path", f"""  <div class="body">
    {svg("0 0 1136 158", "SwiftUI, ViewModel, service, URLSession, HTTPS, server, then JSON, model, ViewModel and back to SwiftUI", "s33path", P)}
    {cues(1)}
    <div class="gap-lg"></div>
    {points([("clock", "Asynchronous", "never block the UI"), ("shield", "Layered security", "HTTPS is one layer of several"), ("cross", "Errors are architecture", "every failure needs a designed response")], label="And why")}
  </div>""", notes(('SAY', 'Click and watch the whole path: SwiftUI to the ViewModel, the service, URLSession, HTTPS, the server; then back as JSON, decoded into a model, through the ViewModel to SwiftUI.'),
                  ('SAY', 'And why: networking must be asynchronous, security is layered, and error handling is part of the application architecture.'),
                  ('CONNECT', 'Now the recap on the map.'))))

S.append(recap_slide('0.8', ('service', 'frameworks', 'https', 'server'),
                     [("bank", "The server owns the balance", "NPay shows a copy"),
                      ("check", "Validate, then decode", "any 2xx status, then Codable into a Balance"),
                      ("send", "Retry with care", "only when repeating is safe: idempotent requests")],
                     'Three things to remember. The bank’s server owns the authoritative balance; NPay holds a copy to display. BalanceService validates the status, any 2xx, before decoding JSON into a Balance. And retries are a design decision: repeat a request only when doing so twice is safe.'))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("bank", "Who owns the authoritative &#8377;25,000?<br>A) The SwiftUI view<br>B) DashboardViewModel<br>C) The bank&rsquo;s server<br>D) UserDefaults on the iPhone", "C",
       "The backend owns the real balance. The ViewModel holds a copy for display.", "Treating the number on screen as the source of truth.", "Some pick B because the ViewModel holds balanceText."),
      ("code", "<code>fetchBalance()</code> gets HTTP 401 with a JSON error body. What happens?<br>A) It decodes the error body as a Balance<br>B) It throws <code>URLError(.badServerResponse)</code><br>C) It returns a balance of &#8377;0<br>D) URLSession retries automatically", "B",
       "401 is outside 200..&lt;300, so the guard fails and the function throws before decoding. The ViewModel shows the error.", "Assuming URLSession throws for HTTP error codes on its own.", "Some pick A or D. URLSession only throws for transport failures; status codes are the app&rsquo;s job."),
      ("lock", "Is HTTPS sufficient to secure a banking application?", "No",
       "It protects data in transit. Authentication, authorization, token handling and backend security are still required.", "Equating an encrypted connection with a secure app.", "Some say yes."),
      ("thread", "Spaced review from 0.5. While <code>fetchBalance()</code> awaits the server, can the main thread handle another tap?", "Yes",
       "The task is suspended at await, not blocking the thread, so the main thread keeps running its RunLoop.", "Treating await like a blocking call.", "Spaced review from 0.5. Some say no."),
      ("send", "A money-transfer POST timed out. What is the safe next step?<br>A) Retry it immediately, unchanged<br>B) Retry it three times quickly<br>C) Send it again as a GET<br>D) Retry with the same idempotency key, so the server can spot a duplicate", "D",
       "POST is not idempotent and the first attempt may have succeeded. An idempotency key lets the server apply it only once.", "Retrying everything by reflex.", "Many pick A; ask what happens if the first attempt actually succeeded.")]
N = len(QA)



for i, (ic, q, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    title = html.unescape(re.sub('<[^>]+>', '', q.split('<br>')[0]))
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
""" + notes(('ASK', 'Give everyone a few seconds, then take a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next question.' if i < N - 1 else 'Where these ideas go next.')) + "</section>\n\n")

S.append(next_slide('0.8', [("5.1", "HTTP, REST &amp; idempotency", "methods and safe retries"),
                            ("5.2", "URLSession &amp; URLRequest", "the full BalanceService"),
                            ("5.3", "Codable, dates &amp; custom decoding", "decoding real bank responses"),
                            ("5.5", "Auth headers &amp; token refresh", "the bearer token and 401"),
                            ("5.8", "Uploads, downloads &amp; background sessions", "transfers that outlive suspension"),
                            ("7.6", "TLS, ATS &amp; certificate trust", "what HTTPS protects, and how")],
                    'Today was the architecture. Unit 05 builds it: HTTP semantics and idempotency, a full URLSession service, Codable with dates and custom decoding, auth headers and token refresh, and background transfers. Unit 07, lesson 7.6, goes inside TLS and App Transport Security.'))

LABSRC = '''struct Balance: Decodable {
    let accountId: String
    let currency: String
    let balanceMinor: Int64
}
let json = Data("""
    {"accountId": "123", "currency": "INR",
     "balanceMinor": 2500000}
    """.utf8)
let balance = try JSONDecoder().decode(Balance.self, from: json)
let rupees = Decimal(balance.balanceMinor) / 100
print(rupees.formatted(.currency(code: "INR")))'''
LAB = code("lab.swift (excerpt)", LABSRC, "font-size:13px")
S.append(lab_slide('0.8', 'Decode a balance, classify a status',
                   'Swift on the command line only; no Xcode project needed.',
                   ['Save <code>lab.swift</code> and <b>predict</b> its output.', 'Run <code>swiftc lab.swift -o lab &amp;&amp; ./lab</code>.',
                    'Rename the JSON key to <code>"balance"</code>. What error do you get?',
                    'Write <code>classify(_ status:)</code> for 200, 204, 401, 404, 500, 503.'],
                   '', 'LIVE DEMO / lab script. Full lab.swift: import Foundation, then the excerpt on the slide. It prints ₹25,000.00 (the exact format depends on the locale). Renaming the key to "balance" throws DecodingError.keyNotFound for balanceMinor. Model answer for classify: switch status { case 200..&lt;300: "success: decode the body"; case 401: "sign in again"; case 400..&lt;500: "request problem: don’t retry as-is"; case 500..&lt;600: "server problem: try again later"; default: "unexpected" }, then loop over [200, 204, 401, 404, 500, 503] and print each. Discussion: 204 is a success with no body, so decoding it as a Balance would fail.', side=LAB))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.8 complete</p>
    <h2>iOS Networking Architecture:<br>From App to Server</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.9 &mdash; iOS Data Storage Architecture</p>
  </div>
""" + notes(('SAY', 'You can now explain the complete path of a network request in an iOS app, why it is asynchronous, why its security is layered, and why error handling belongs in the architecture. Next lesson: once the balance arrives, what should NPay keep on the device, and where?')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.8 — iOS Networking Architecture</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.8 — iOS Networking Architecture">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT08, 'w').write(doc)
print(len(S), 'slides')
