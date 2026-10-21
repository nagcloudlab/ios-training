"""After gen02.py: add the Lesson 0.2 text's slides and regroup the deck into its Parts.
Run:  python gen02.py decks/lesson-0.2/index.html && python post02.py"""
import re, sys
sys.argv = ['x', '/dev/null']
src = open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers: row, tall, wire, head, svg, code, notes, points

P_ = 'decks/lesson-0.2/index.html'
s = open(P_).read()
first = s.index('<section'); last = s.rindex('</section>') + len('</section>')
head_, tail_ = s[:first], s[last:]
secs = re.findall(r'<section\b.*?</section>', s[first:last], re.S)
assert len(secs) == 40, len(secs)
S = {i + 1: x for i, x in enumerate(secs)}
Q = [n for n in S if 'class="slide question"' in S[n][:40]]
assert len(Q) == 3


def kick(n, k):
    assert '<p class="kicker">' in S[n], n
    S[n] = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">{k}</p>', S[n], count=1)


def connect(n, new):
    S[n], c = re.subn(r'(<span class="notes-label">CONNECT</span><p>).*?(</p>)', lambda m: m.group(1) + new + m.group(2), S[n], count=1)
    assert c == 1, n


def divider(n, title, lead, say, con):
    return f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(('SAY', say), ('CONNECT', con))}</section>"""


# ---------------------------------------------------------------- NEW · five responsibilities
P = []
P.append(row(368, 0, 400, 62, "user", "User", "taps “Check Balance”", "1"))
P.append(wire(f'M568 62V90{head(568, 90, "d")}'))
for i, (ic, t, sub) in enumerate([("phone", "1. View (SwiftUI)", "displays the balance and receives interaction"),
                                  ("layout", "2. ViewModel", "manages screen state and coordinates actions"),
                                  ("link", "3. Service / Repository", "loads data and hides implementation details")]):
    y = 96 + i * 88
    P.append(row(0, y, 1136, 62, ic, t, sub, str(i + 2)))
    if i < 2:
        P.append(wire(f'M568 {y + 62}V{y + 82}{head(568, y + 82, "d")}'))
P.append(wire(f'M568 334V352H284V372{head(284, 372, "d")}M568 352H852V372{head(852, 372, "d")}'))
P.append(row(124, 378, 320, 62, "bank", "4. Network", "bank server", "5"))
P.append(row(692, 378, 320, 62, "db", "5. Storage", "local database", "5"))
FIVE = f"""<section class="slide">
  <p class="kicker">Part 1 &middot; Responsibilities &middot; conceptual</p>
  <h2>Five important responsibilities</h2>
  <div class="body">
    {svg("0 0 1136 442", "The user taps Check Balance; 1 the SwiftUI view, 2 the ViewModel, 3 the service or repository, which uses 4 the network (bank server) and 5 storage (local database).", "s2five", P, "max-height:450px")}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <p class="small muted" style="margin:10px 0 0">An example of a layered MVVM-style architecture, not a structure iOS forces every app to use.</p>
  </div>
{notes(('SAY', 'Click by click, top to bottom. The user taps Check Balance. The SwiftUI view displays the balance and receives the tap. The ViewModel manages the screen state and coordinates the action. The service or repository loads the data and hides how. Below it, the network reaches the bank server and storage keeps a local copy.'),
       ('SAY', 'This is one common, layered MVVM-style design. iOS does not force it on every app.'),
       ('CONNECT', 'How is this different from the architecture of iOS itself?'))}</section>"""

# ---------------------------------------------------------------- NEW · iOS vs app architecture table
TABLE = f"""<section class="slide">
  <p class="kicker">Part 2 &middot; Two architectures</p>
  <h2>iOS architecture vs your app&rsquo;s architecture</h2>
  <div class="body">
    <table class="tbl">
      <tr><th>iOS platform architecture</th><th>Application architecture</th></tr>
      <tr><td>Operating system</td><td>View</td></tr>
      <tr><td>Kernel and processes</td><td>ViewModel</td></tr>
      <tr><td>System frameworks</td><td>Model</td></tr>
      <tr><td>Hardware access</td><td>Services and repositories</td></tr>
      <tr><td>App lifecycle</td><td>Business logic and data flow</td></tr>
    </table>
    <div class="gap"></div>
    {points([("bank", "iOS architecture", "how Apple manages apps and system resources"), ("layers", "Application architecture", "how developers organize code inside their apps")], cls="p2", label="Related, but not the same thing")}
  </div>
{notes(('SAY', 'One of the most important distinctions in this course. The left column is Apple’s: the operating system, kernel and processes, system frameworks, hardware access and the app lifecycle. The right column is ours: how we organize views, ViewModels, models, services and data flow inside the app.'),
       ('ASK', 'Is MVVM part of iOS?'),
       ('EXPECT', 'No. MVVM is an application design choice; iOS does not know about it.'),
       ('CONNECT', 'Now follow one tap through these layers.'))}</section>"""

# ---------------------------------------------------------------- NEW · Check Balance walkthrough (8 steps, down then up)
lanes = ["USER", "VIEW", "VIEWMODEL", "SERVICE", "NETWORK"]
steps8 = [(0, "user", "User", "User taps button", "The user initiates an action on the balance screen."),
          (1, "phone", "View", "View forwards the action", "The SwiftUI view calls the ViewModel, for example loadBalance()."),
          (2, "layout", "ViewModel", "Loading state", "The ViewModel marks the screen as loading and asks the service for the balance."),
          (3, "link", "Service", "Service hides the details", "The service or repository decides where the data comes from and calls the network."),
          (4, "bank", "Bank server", "Bank server responds", "The bank server checks the request and returns the balance."),
          (3, "link", "Service", "Result comes back", "The service decodes the response, may save a copy to local storage, and returns a model."),
          (2, "layout", "ViewModel", "Screen state updates", "The ViewModel turns the model into what the screen needs, such as the balance text."),
          (1, "phone", "View", "SwiftUI re-renders", "The view shows the new balance. The user sees the result.")]
P = []
for d, lab in enumerate(lanes):
    P.append(f'<text class="mono" x="0" y="{d * 62 + 30}">{lab}</text>')
    P.append(wire(f'M104 {d * 62 + 25}H1136', cls="faint dash"))
pts = []
for i, (d, ic, t, _, _) in enumerate(steps8):
    x = 112 + i * 128; y = d * 62
    P.append(row(x, y + 2, 108, 46, '', t, '', str(i + 1)))
    pts.append((x, y))
for i in range(7):   # step connector: out of the right edge, along to the next lane, into the next box's left edge
    (x1, y1), (x2, y2) = pts[i], pts[i + 1]
    P.append(wire(f'M{x1 + 108} {y1 + 25}H{x1 + 118}V{y2 + 25}H{x2 - 2}{head(x2 - 2, y2 + 25, "r")}'))
P.append('<g class="fade" data-lit="6"><g class="nd lit"><rect class="sh" x="752" y="256" width="108" height="40" rx="10"/><use href="#i-db" x="762" y="265" width="22" height="22"/><text class="sm" x="790" y="281">Storage</text></g>'
         + wire(f'M806 236V250{head(806, 250, "d")}') + '</g>')
P.append('<text class="sm" x="430" y="320" text-anchor="middle">request goes down</text><text class="sm" x="940" y="320" text-anchor="middle">result comes back up</text>')
for i, (_, _, _, title, desc) in enumerate(steps8):
    P.append(f'<g class="fade" data-lit="{i + 1}"><text class="mono" x="0" y="364">STEP {i + 1} OF 8</text>'
             f'<text x="0" y="396" style="font-size:24px;font-weight:700">{title}</text>'
             f'<text x="0" y="426" style="font-size:19px;font-weight:400">{desc}</text></g>')
WALK = f"""<section class="slide">
  <p class="kicker">Part 3 &middot; Request walkthrough &middot; conceptual</p>
  <h2>Tapping &ldquo;Check Balance&rdquo;, step by step</h2>
  <div class="body">
    {svg("0 0 1136 432", "Eight steps: user, view, ViewModel, service, bank server going down; then service (saving to storage), ViewModel and view coming back up.", "s3walk", P, "max-height:470px")}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
  </div>
{notes(('SAY', 'Eight clicks. Notice the shape: the request moves down through the app, from the user to the view, the ViewModel, the service and the bank server. Then the result moves back up: the service decodes it and may store a copy, the ViewModel updates the screen state, and SwiftUI re-renders.'),
       ('ASK', 'At which step does the spinner appear, and which component decides it?'),
       ('EXPECT', 'Step 3. The ViewModel sets the loading state; the view only renders it.'),
       ('CONNECT', "Step 8 says the view simply re-rendered. That is SwiftUI's whole mental model."))}</section>"""

# ---------------------------------------------------------------- NEW · UIKit vs SwiftUI
UIKIT = f"""<section class="slide">
  <p class="kicker">Part 4 &middot; Imperative vs declarative</p>
  <h2>UIKit style vs SwiftUI style</h2>
  <div class="body">
    <p style="margin:0 0 22px">SwiftUI uses a <b>declarative</b> approach: the UI is a <b>function of its state</b>.</p>
    <div class="cols stretch">
      <div class="card step"><span class="label">UIKit style</span>
        <ol style="margin:6px 0 12px"><li>Create a <code>UILabel</code></li><li>Set its text</li><li>Update it manually when needed</li></ol>
        <p class="small muted" style="margin:0"><b>Imperative:</b> tell the interface what to change.</p></div>
      <div class="card accent step"><span class="label">SwiftUI style</span>
        <ol style="margin:6px 0 12px"><li>Declare a view</li><li>Connect it to state</li><li>Change state</li></ol>
        <p class="small muted" style="margin:0"><b>Declarative:</b> describe the desired result.</p></div>
    </div>
  </div>
{notes(('SAY', 'Traditional UIKit code often changes interface properties explicitly: create a label, set its text, and remember to update it whenever the data changes. SwiftUI flips this: declare the view, connect it to state, and just change the state.'),
       ('ASK', 'What goes wrong in the UIKit style if you forget one manual update?'),
       ('EXPECT', 'The screen shows stale data. In SwiftUI the view is derived from state, so it cannot drift out of sync the same way.'),
       ('CONNECT', "Let's see state driving the interface."))}</section>"""

# ---------------------------------------------------------------- NEW · state -> interface demo (interactive)
DEMO = f"""<section class="slide">
  <p class="kicker">Part 4 &middot; State drives the interface</p>
  <h2>State &rarr; interface</h2>
  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    <div class="demo-phone">
      <p class="small muted" style="margin:0">Available balance</p>
      <p class="demo-balance" id="npayDemoBalance">&#8377;12,500</p>
      <div class="demo-actions">
        <button type="button" class="demo-btn" onclick="npayDemo(1000);this.blur()">Simulate &#8377;1,000 deposit</button>
        <button type="button" class="demo-btn ghost" onclick="npayDemo(0);this.blur()">Reset balance</button>
      </div>
    </div>
    <div>
      <p class="small muted" style="margin:0 0 6px">Current state</p>
      <pre class="tree" style="font-size:22px">balance = <span class="dir" id="npayDemoState">12500</span></pre>
      <div class="gap"></div>
      <div class="rule">When the <b>balance state</b> changes, the displayed amount changes. That is the central mental model behind SwiftUI.</div>
      <p class="small muted" style="margin:12px 0 0">Local interactive simulation only; no real banking request or Swift runtime.</p>
    </div>
  </div>
  <script>
    function npayDemo(add) {{
      var el = document.getElementById('npayDemoState'), v = add ? (+el.textContent + add) : 12500;
      el.textContent = v;
      document.getElementById('npayDemoBalance').textContent = '\\u20B9' + v.toLocaleString('en-IN');
    }}
  </script>
{notes(('SAY', 'Click the deposit button a few times. We never touch the label; we only change the state, and the displayed amount follows. Reset puts the state back and the screen follows again.'),
       ('SAY', 'This is a browser simulation for teaching, not Swift. In SwiftUI, the same idea is a @State or observable property feeding a Text view.'),
       ('CONNECT', 'Where do the model and the ViewModel fit? That is MVVM.'))}</section>"""

# ---------------------------------------------------------------- NEW · where MVVM fits
ACC = '''struct Account {
    let id: String
    let balance: Decimal
}'''
AVM = '''@Observable
class AccountViewModel {
    var balanceText = "₹12,500"
}'''
BV = '''struct BalanceView: View {
    var model: AccountViewModel

    var body: some View {
        Text(model.balanceText)
    }
}'''
P = []
for i, (ic, t, sub) in enumerate([("db", "Model", "what the data means"), ("layout", "ViewModel", "what the screen needs"), ("phone", "View", "what the user sees")]):
    x = i * 392
    P.append(row(x, 0, 352, 62, ic, t, sub, str(i + 1)))
    if i < 2:
        P.append(wire(f'M{x + 356} 31H{x + 386}{head(x + 386, 31, "r")}'))
MVVM = f"""<section class="slide">
  <p class="kicker">Part 5 &middot; MVVM</p>
  <h2>Model&ndash;View&ndash;ViewModel, for a balance screen</h2>
  <div class="body top">
    {svg("0 0 1136 64", "Model, what the data means; ViewModel, what the screen needs; View, what the user sees", "s5mvvm", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="gap"></div>
    <p class="small muted" style="margin:0 0 12px">For a bank balance screen:</p>
    <div class="cols c3" style="gap:18px;align-items:start">
      {code("Account.swift", ACC, "font-size:15px")}
      {code("AccountViewModel.swift", AVM, "font-size:15px")}
      {code("BalanceView.swift", BV, "font-size:15px")}
    </div>
    <p class="small muted" style="margin:14px 0 0">Simplified teaching examples. A production app also needs dependency injection, currency formatting, error handling and secure data access.</p>
  </div>
{notes(('LIVE DEMO', 'Type these three pieces in Xcode, then change balanceText and show the preview updating.'),
       ('SAY', 'MVVM stands for Model, View, ViewModel. Click through: the model is what the data means, an account with an ID and a balance. The ViewModel is what the screen needs, here ready-to-show balance text. The view is what the user sees, a Text bound to the ViewModel.'),
       ('SAY', 'Account uses Decimal, a base-10 type, so amounts are exact; never binary floating point for money. These are simplified teaching examples: a production app would also address dependency injection, currency formatting, error handling and secure data access.'),
       ('CONNECT', "Let's check your understanding."))}</section>"""

# ---------------------------------------------------------------- keep only the lesson text's slides
D1 = divider(1, "Five important responsibilities", "Who does what inside a banking app",
             "In Lesson 0.1 iOS started the app. Now: who manages it after it starts? We split the work into five responsibilities.", "Start with the question on one screen.")
D2 = divider(2, "iOS vs your app&rsquo;s architecture", "Related, but not the same thing",
             "One of the most important distinctions: Apple's platform architecture versus how we organize our own code.", "Put the two side by side.")
D3 = divider(3, "What happens when the user taps &ldquo;Check Balance&rdquo;?", "The request goes down; the result comes back up",
             "Follow one tap through every layer and back.", "Eight steps, one per click.")
D4 = divider(4, "How SwiftUI differs from traditional UI", "The UI is a function of its state",
             "Traditional UIKit code changes interface properties explicitly. SwiftUI describes the result and lets the framework update it.", "Compare the two styles.")
D5 = divider(5, "Where does MVVM fit?", "Model, View, ViewModel",
             "MVVM gives each of the responsibilities we saw a clear home.", "Start with a balance screen in three small pieces.")
OUTCOMES = f"""<section class="slide">
  <p class="kicker">Lesson 0.2 &middot; Outcomes</p>
  <h2>By the end, you will be able to</h2>
  <div class="body">
    <div class="cols c3 stagger step">
      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-layers"/></svg></span><p>Name the <b>five responsibilities</b> inside an app</p></div>\n      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-bank"/></svg></span><p>Tell <b>iOS architecture</b> from <b>app architecture</b></p></div>\n      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-eye"/></svg></span><p>Follow a <b>Check Balance</b> tap down the layers and back up</p></div>\n      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-frameworks"/></svg></span><p>Explain how <b>declarative</b> SwiftUI differs from UIKit</p></div>\n      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-layout"/></svg></span><p>Place <b>Model</b>, <b>View</b> and <b>ViewModel</b> in a balance screen</p></div>\n      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-check"/></svg></span><p>Say who manages the <b>process</b>, the <b>UI updates</b> and the <b>loading state</b></p></div>
    </div>
  </div>
{notes(('SAY', 'Six outcomes, one question: who does what after the app starts? Every slide answers part of it.'), ('CONNECT', 'Start with five responsibilities.'))}</section>"""
order = [1, OUTCOMES,
         D1, 3, FIVE,
         D2, TABLE,
         D3, WALK,
         D4, UIKIT, DEMO,
         D5, MVVM,
         35, *Q, 40]
body = '\n\n'.join(S[x] if isinstance(x, int) else x for x in order)
out = head_ + body + '\n\n' + tail_.lstrip('\n')
out = out.replace('NPay dashboard with a balance, recent activity and a Send 500 rupees button. Labels appear: validation, loading indicator, network call, error message, confirmation.',
                  'NPay dashboard with a balance, recent activity and a Check Balance button. Labels appear: display the screen, handle the tap, talk to the bank, store information.')
open(P_, 'w').write(out)
print('slides', body.count('<section '))
