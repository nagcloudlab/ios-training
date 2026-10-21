"""Generates decks/lesson-0.2/index.html from the Lesson 0.2 manuscript (NPay app architecture)."""
import html, sys

OUT = sys.argv[1]
E = html.escape


# ------------------------------------------------------------------ svg helpers (same idiom as lesson 0.1)
def lit(v):
    return f' data-lit="{v}"' if v else ''


def tall(x, y, w, h, icon, title, sub='', l=None, cls='', style=''):
    cx = x + w / 2
    on = 'solid' in cls
    st = f' style="{style}"' if style else ''
    o = f'<g class="nd{(" " + cls) if cls else ""}"{lit(l)}{st}><rect class="sh" x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/>'
    if icon:
        o += f'<use{" class=\"on\"" if on else ""} href="#i-{icon}" x="{cx - 14:g}" y="{y + 14}" width="28" height="28"/>'
    o += f'<text{" class=\"on\"" if on else ""} x="{cx:g}" y="{y + h - (36 if sub else 22)}" text-anchor="middle">{title}</text>'
    if sub:
        o += f'<text class="sm{" on" if on else ""}" x="{cx:g}" y="{y + h - 16}" text-anchor="middle">{sub}</text>'
    return o + '</g>'


def row(x, y, w, h, icon, title, sub='', l=None, cls=''):
    on = 'solid' in cls
    oc = ' class="on"' if on else ''
    o = f'<g class="nd{(" " + cls) if cls else ""}"{lit(l)}><rect class="sh" x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>'
    tx = x + 16
    if icon:
        o += f'<use{oc} href="#i-{icon}" x="{x + 14}" y="{y + h / 2 - 13:g}" width="26" height="26"/>'
        tx = x + 52
    if sub:
        o += f'<text{oc} x="{tx}" y="{y + h / 2 - 3:g}">{title}</text><text class="sm{" on" if on else ""}" x="{tx}" y="{y + h / 2 + 15:g}">{sub}</text>'
    else:
        o += f'<text{oc} x="{tx}" y="{y + h / 2 + 6:g}">{title}</text>'
    return o + '</g>'


def wire(d, l=None, cls=''):
    return f'<path class="wire{(" " + cls) if cls else ""}"{lit(l)} d="{d}"/>'


def head(x, y, d):
    return {'r': f'M{x - 7} {y - 7}l7 7-7 7', 'd': f'M{x - 7} {y - 7}l7 7 7-7',
            'l': f'M{x + 7} {y - 7}l-7 7 7 7', 'u': f'M{x - 7} {y + 7}l7-7 7 7'}[d]


def svg(vb, title, tid, parts, style=''):
    st = f' style="{style}"' if style else ''
    return (f'<div class="diagram">\n      <svg class="art" viewBox="{vb}"{st} role="img" aria-labelledby="{tid}">\n'
            f'        <title id="{tid}">{title}</title>\n        ' + '\n        '.join(parts) + '\n      </svg>\n    </div>')


def code(name, src, style=''):
    st = f' style="{style}"' if style else ''
    return f'<div class="cw"><div class="ch"><span>{name}</span></div><pre class="cb"{st}>{E(src)}</pre></div>'


def notes(*pairs):
    return '  <aside class="notes-src">\n' + ''.join(
        f'    <span class="notes-label">{l}</span><p>{t}</p>\n' for l, t in pairs) + '  </aside>\n'


def slide(kicker, h2, body, nts, cls='', title_attr=''):
    c = f' {cls}' if cls else ''
    ta = f' data-title="{title_attr}"' if title_attr else ''
    k = f'  <p class="kicker">{kicker}</p>\n' if kicker else ''
    h = f'  <h2>{h2}</h2>\n' if h2 else ''
    return f'<section class="slide{c}"{ta}>\n{k}{h}{body}\n{nts}</section>\n\n'


def chapter(n, title, lead, say, connect=''):
    pairs = [('SAY', say)] + ([('CONNECT', connect)] if connect else [])
    return f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(*pairs)}</section>

"""


def points(items, cls='', label=None, box='tip', step=True):
    lab = f' data-label="{label}"' if label else ''
    st = ' step' if step else ''
    inner = ''.join(f'<div><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg><span><b>{t}</b><small>{d}</small></span></div>'
                    for i, t, d in items)
    return f'<div class="{box}{st}"{lab}><div class="points{(" " + cls) if cls else ""}">{inner}</div></div>'


S = []

# ================================================================== 1 · title
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.2</p>
    <h1 style="font-size:54px;line-height:1.05">iOS App Architecture:<br>Who Does What?</h1>
    <p class="lead" style="max-width:660px">In Lesson 0.1, iOS started NPay. Now: <b>who manages the app after it starts?</b></p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'In Lesson 0.1 we learned how iOS starts an application. Now we look at who manages the application after it starts: who displays the screen, handles a tap, talks to the bank and stores information. No coding is required for this lesson; the code we show is there to read, not to write.'),
            ('CONNECT', "Here's what you'll be able to do by the end.")) + "</section>\n\n")

# ================================================================== 2 · outcomes
outs = [("layers", "Name the <b>five responsibilities</b>; tell <b>iOS</b> from <b>app</b> architecture"),
        ("send", "Trace a <b>request</b> and a <b>payment</b> through the app"),
        ("frameworks", "Compare <b>MVC</b>, <b>MVVM</b> and <b>layered</b> architecture"),
        ("layout", "Separate <b>view</b>, <b>state</b>, <b>domain</b>, <b>service</b> and <b>persistence</b>"),
        ("link", "Introduce <b>dependency injection</b>"),
        ("shield", "Place <b>security boundaries</b> and <b>tests</b>")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.2 &middot; Outcomes", "By the end, you will be able to", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six outcomes, one story: a single NPay payment. Every slide answers part of "who owns what" for that payment.'),
                 ('CONNECT', "Let's start on the NPay dashboard."))))

# ================================================================== 3 · hero: Send ₹500
P = []
P.append('<use href="#d-iphone" x="450" y="0" width="236" height="472"/>')
P.append('<text x="568" y="78" text-anchor="middle" style="font-size:22px;font-weight:800">NPay</text>')
P.append('<g class="nd"><rect class="sh" x="478" y="98" width="180" height="78" rx="12"/><text class="sm" x="568" y="126" text-anchor="middle">Available balance</text><text x="568" y="158" text-anchor="middle" style="font-size:24px;font-weight:700">&#8377;25,000</text></g>')
P.append('<text class="mono" x="478" y="206">RECENT ACTIVITY</text>')
P.append('<rect class="mute" x="478" y="216" width="180" height="34" rx="8"/><rect class="mute" x="478" y="258" width="180" height="34" rx="8"/><rect class="mute" x="478" y="300" width="180" height="34" rx="8"/>')
P.append('<g class="nd lit"><rect class="sh" x="478" y="380" width="180" height="48" rx="14"/><use href="#i-eye" x="496" y="393" width="22" height="22"/><text x="582" y="410" text-anchor="middle">Check Balance</text></g>')
P.append('<g class="fade" data-lit="0"><circle class="ring anim-ping" cx="568" cy="404" r="30"/></g>')
labels = [(1, 'DISPLAY THE SCREEN', 'l', 120), (2, 'HANDLE THE TAP', 'l', 404), (3, 'TALK TO THE BANK', 'r', 140),
          (4, 'STORE INFORMATION', 'r', 300)]
for n, t, side, y in labels:
    if side == 'l':
        P.append(f'<g class="fade" data-lit="{n}+"><text class="mono" x="400" y="{y + 4}" text-anchor="end">{t}</text>{wire(f"M410 {y}H440", n)}</g>')
    else:
        P.append(f'<g class="fade" data-lit="{n}+"><text class="mono" x="736" y="{y + 4}">{t}</text>{wire(f"M696 {y}H726", n)}</g>')
S.append(slide("", "", f"""  <div class="body center">
    {svg("0 0 1136 472", "NPay dashboard with a balance, recent activity and a Send 500 rupees button. Labels appear: validation, loading indicator, network call, error message, confirmation.", "h3t", P, "max-height:500px")}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <p class="lead" style="margin:10px 0 0">The user opens NPay, checks the balance, transfers money. Who is responsible?</p>
  </div>""", notes(('SAY', 'Imagine our banking app. The user opens NPay, checks the balance and transfers money. Click by click: something must display the screen, handle the button tap, communicate with the bank and store information.'),
                 ('ASK', 'Who should be responsible for each of these jobs?'),
                 ('EXPECT', "Collect answers without correcting them. Many will say \"the view does it all\". The next slides split the work into five responsibilities."),
                 ('CONNECT', "Let's name the five responsibilities.")), title_attr="Check Balance"))

# ================================================================== chapter 1
S.append(chapter(1, "Why architecture matters", "Boundaries for change, testing and ownership",
                 "Before choosing patterns, we need a reason. Architecture exists to make change, testing and ownership manageable."))

# ================================================================== 5 · giant view
GIANT = '''import SwiftUI
struct SendMoneyView: View {
    @State private var amountText = "500"
    @State private var status = ""
    var body: some View {
        VStack {
            TextField("Amount", text: $amountText)
            Button("Send") {
                // Temptation: validation, API, storage,
                // navigation and error handling all here.
                status = "Starting..."
            }
            Text(status)
        }
    }
}'''
S.append(slide("Part 1 &middot; The tempting design", "The giant view", f"""  <div class="body cols wide-left middle">
    {code("SendMoneyView.swift", GIANT, "font-size:16px")}
    <div>
      <p>Everything lands in the <code>Button</code> action:</p>
      <ul>
        <li class="step">Validation</li>
        <li class="step">The API call</li>
        <li class="step">Storage</li>
        <li class="step">Navigation and error handling</li>
      </ul>
      <div class="gap"></div>
      <div class="warn step" data-label="What goes wrong">Hard to <b>test</b> without a view, hard to <b>reuse</b>, and it grows into a <b>Massive View</b>.</div>
    </div>
  </div>""", notes(('SAY', 'This compiles and works for a demo. The temptation is to keep adding: validation, the API call, storage, navigation, error handling, all inside the Button closure.'),
                 ('ASK', 'How would you test transfer validation without launching a view? How would you reuse this logic on another screen?'),
                 ('EXPECT', "You can't easily do either. Logic trapped inside body needs a view to run, and it can't be shared. Over time it becomes a Massive View."),
                 ('CONNECT', 'So what is architecture actually for?'))))

# ================================================================== 6 · purpose + restaurant analogy
P = []
roles = [("phone", "UI", "Dining room"), ("layout", "Presentation", "Order coordinator"), ("gear", "Domain rules", "Kitchen"), ("link", "Data adapters", "Suppliers")]
for i, (ic, t, sub) in enumerate(roles):
    x = 10 + i * 284
    P.append(tall(x, 20, 240, 110, ic, t, sub, f"{i + 1}"))
    if i < 3:
        P.append(wire(f'M{x + 246} 75H{x + 278}{head(x + 278, 75, "r")}'))
P.append('<text class="mono" x="10" y="10">ANALOGY &#183; A RESTAURANT</text>'.replace('&#183;', '&amp;'))
S.append(slide("Part 1 &middot; Purpose", "What architecture is for", f"""  <div class="body">
    {points([("layers", "Change", "boundaries contain it"), ("check", "Testability", "logic runs without UI"), ("user", "Ownership", "clear who owns what"), ("eye", "Reasoning", "easy to follow")], cls="p4", label="Architecture gives you", step=False)}
    <div class="gap-lg"></div>
    {svg("0 0 1136 136", "Restaurant analogy: dining room is the UI, order coordinator is presentation, kitchen is domain rules, suppliers are data adapters", "s6t", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="gap"></div>
    <p class="muted small">More classes and folders do not automatically mean better design.</p>
  </div>""", notes(('SAY', 'Architecture gives you boundaries: for change, for testing, for ownership, and for reasoning about the code. It is not about having more folders.'),
                 ('SAY', 'A restaurant: guests sit in the dining room (UI). An order coordinator takes and tracks orders (presentation). The kitchen applies the recipes and rules (domain). Suppliers bring ingredients from outside (data adapters). Each can change without rebuilding the others.'),
                 ('CONNECT', 'Before NPay-specific layers, separate two kinds of architecture that people mix up.'))))
# fix label text (no middle dot)
S[-1] = S[-1].replace('ANALOGY &amp; A RESTAURANT', 'ANALOGY: A RESTAURANT')

# ================================================================== chapter 2
S.append(chapter(2, "Two different architectures", "The platform's, and ours",
                 "Lesson 0.1 was platform architecture. Today is application architecture. They are different things with different owners."))

# ================================================================== 8 · platform vs application
P = []
P.append('<g class="nd ghost" data-lit="1"><rect class="sh" x="4" y="26" width="1128" height="120" rx="18"/></g>')
P.append('<text class="mono" x="20" y="16">NPAY APPLICATION DESIGN</text>')
P.append('<text class="sm" x="1128" y="16" text-anchor="end">validation, state, business operations, networking, data</text>')
app = [("phone", "SwiftUI View", ""), ("layout", "ViewModel", ""), ("gear", "Transfer use case", ""), ("link", "Transfer service", "interface")]
for i, (ic, t, sub) in enumerate(app):
    x = 26 + i * 278
    P.append(row(x, 58, 250, 56, ic, t, sub, l="1"))
    if i < 3:
        P.append(wire(f'M{x + 254} 86H{x + 272}{head(x + 272, 86, "r")}', "1"))
P.append('<g class="nd ghost" data-lit="2"><rect class="sh" x="4" y="236" width="1128" height="190" rx="18"/></g>')
P.append('<text class="mono" x="20" y="226">iOS PLATFORM</text>')
P.append('<text class="sm" x="1128" y="226" text-anchor="end">process, threads, virtual memory, sandbox, display</text>')
P.append(row(26, 262, 1084, 56, "frameworks", "SwiftUI / Foundation", l="2"))
P.append(wire(f'M568 318V340{head(568, 340, "d")}', "2"))
P.append(row(26, 346, 1084, 56, "kernel", "System services / kernel", l="2"))
P.append(wire(f'M151 114V254{head(151, 254, "d")}', cls="dash"))
P.append('<text class="sm" x="162" y="190">uses</text>')
P.append(wire(f'M985 114V254{head(985, 254, "d")}', cls="dash"))
P.append('<text class="sm" x="996" y="190">uses</text>')
S.append(slide("Part 2 &middot; Two architectures &middot; conceptual", "Platform vs application architecture", f"""  <div class="body">
    {svg("0 0 1136 430", "Top region, NPay application design: SwiftUI View, ViewModel, transfer use case, transfer service interface. Bottom region, iOS platform: SwiftUI and Foundation on system services and the kernel. The view and the service use the platform.", "s8t", P, "max-height:430px")}
    <i class="step cue"></i><i class="step cue"></i>
    <div class="gap"></div>
    <p>The <b>NPay backend</b> is a separate system. It is not part of the app process.</p>
  </div>""", notes(('SAY', "First click: our application design. Views, a ViewModel, a use case and a service interface. We decide these. Second click: the platform. Processes, threads, memory, sandbox and display are Apple's, and our code only uses them."),
                 ('ASK', 'Is MVVM part of iOS?'),
                 ('EXPECT', "No. MVVM is an application design pattern we choose; the platform doesn't know about it."),
                 ('CONNECT', "Now let's follow one payment across our whole application, and past it to the bank."))))

# ================================================================== 9 · end to end
P = []
nodes = [("user", "User", ""), ("phone", "SwiftUI", "View"), ("layout", "ViewModel", ""), ("gear", "Use case", ""),
         ("link", "Service", "protocol"), ("globe", "URLSession", "adapter"), ("bank", "NPay", "backend"), ("db", "Ledger", "")]
xs = [0, 140, 280, 420, 560, 700, 876, 1016]
for i, (ic, t, sub) in enumerate(nodes):
    last = i == 7
    P.append(tall(xs[i], 46, 120, 100, ic, t, sub, "1+" if last else "1", '' if last else 'pass', '' if last else f'--d:{i * .16:.2f}s'))
    if i < 7:
        a, b = xs[i] + 124, xs[i + 1] - 4
        P.append(wire(f'M{a} 96H{b}{head(b, 96, "r")}', "2" if i == 5 else None))
P.append('<text class="mono" x="848" y="196" text-anchor="middle">HTTPS</text>')
P.append(wire('M848 26V176', "2", "dash"))
P.append('<text class="mono" x="420" y="16" text-anchor="middle">ON THE DEVICE (NPAY PROCESS)</text>')
P.append('<text class="mono" x="996" y="16" text-anchor="middle">BANK SERVERS</text>')
P.append(wire(f'M340 146V170H200V152{head(200, 152, "u")}'))
P.append('<text class="sm" x="270" y="188" text-anchor="middle">state updates the view</text>')
S.append(slide("Part 2 &middot; End to end &middot; conceptual", "One payment, end to end", f"""  <div class="body">
    {svg("0 0 1136 206", "User, SwiftUI view, ViewModel, use case, service protocol and URLSession adapter on the device; HTTPS to the NPay backend and its ledger on bank servers. The ViewModel updates the view.", "s9t", P)}
    <i class="step cue"></i><i class="step cue"></i>
    <div class="gap-lg"></div>
    <div class="cols step">
      <div class="card accent"><span class="label">Client checks</span><p>Improve <b>usability</b>: fast feedback on bad input.</p></div>
      <div class="card accent"><span class="label">Server is authoritative</span><p>Authentication, authorization, fraud policy, idempotency and <b>ledger consistency</b>.</p></div>
    </div>
  </div>""", notes(('SAY', "Click one: the payment flows from the user through our layers to the adapter. Click two: it crosses HTTPS to the NPay backend and the ledger. That dashed line is a trust boundary; the backend is not inside the iOS process."),
                 ('SAY', 'Client-side checks are for usability: tell the user quickly that an amount is invalid. The server decides whether the transfer is allowed and records it.'),
                 ('ASK', 'Does client validation authorize a transfer?'),
                 ('EXPECT', 'No. Only the backend can authorize. A client check can always be bypassed.'),
                 ('CONNECT', "Let's zoom into the left end: SwiftUI and state."))))

# ================================================================== chapter 3
S.append(chapter(3, "SwiftUI and state", "Views describe; state decides",
                 "SwiftUI views describe UI from state. Get the state right and the view follows."))

# ================================================================== 11 · BalanceCard
BAL = '''struct BalanceCard: View {
    let formattedBalance: String
    var body: some View {
        VStack(alignment: .leading) {
            Text("Available balance")
            Text(formattedBalance).font(.title)
        }
    }
}'''
P = ['<g class="nd"><rect class="sh" x="10" y="20" width="360" height="130" rx="18"/><text class="sm" x="40" y="66">Available balance</text><text x="40" y="112" style="font-size:34px;font-weight:700">&#8377;25,000</text></g>',
     '<text class="mono" x="10" y="180">RENDERED BY THE FRAMEWORK</text>']
S.append(slide("Part 3 &middot; Views", "A view is a description", f"""  <div class="body cols middle">
    {code("BalanceCard.swift", BAL, "font-size:17px")}
    <div>
      {svg("0 0 380 190", "The BalanceCard rendered: Available balance, 25,000 rupees", "s11t", P)}
      <div class="gap"></div>
      <div class="rule step">Constructing a view value does <b>not</b> draw pixels. SwiftUI renders it.</div>
    </div>
  </div>""", notes(('SAY', 'BalanceCard takes a ready-formatted string and describes two texts. No networking, no formatting logic, no state of its own. Small views like this are easy to reuse and preview.'),
                 ('CONNECT', 'Most screens are not that simple. A transfer screen has several states.'))))

# ================================================================== 12 · explicit states
ENUM = '''enum TransferScreenState: Equatable {
    case idle
    case submitting
    case success(reference: String)
    case failure(message: String)
    case pending(reference: String?)
}'''
P = []
P.append(row(170, 0, 200, 52, "", "idle", l="0"))
P.append(wire(f'M270 52V96{head(270, 96, "d")}'))
P.append(row(170, 102, 200, 52, "", "submitting", l="1"))
P.append(wire(f'M270 154V178H90V214{head(90, 214, "d")}'))
P.append(wire(f'M270 154V214{head(270, 214, "d")}'))
P.append(wire(f'M270 154V178H450V214{head(450, 214, "d")}'))
P.append(row(10, 220, 160, 52, "check", "success", l="2"))
P.append(row(190, 220, 160, 52, "cross", "failure", l="2"))
P.append(row(370, 220, 160, 52, "clock", "pending", cls="alert"))
P.append('<text class="sm" x="90" y="296" text-anchor="middle">reference</text>')
P.append('<text class="sm" x="270" y="296" text-anchor="middle">message</text>')
P.append('<g class="fade" data-lit="3"><text class="sm" x="450" y="296" text-anchor="middle">timed out:</text><text class="sm" x="450" y="314" text-anchor="middle">result unknown</text></g>')
S.append(slide("Part 3 &middot; State", "Explicit screen states", f"""  <div class="body cols middle">
    <div>
      {code("TransferScreenState.swift", ENUM)}
      <div class="gap"></div>
      <div class="rule">One enum, instead of contradictory booleans like <code>isLoading</code>, <code>hasError</code> and <code>isSuccessful</code>.</div>
    </div>
    {svg("0 0 540 320", "State machine: idle, then submitting, then success, failure or pending", "s12t", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
  </div>""", notes(('SAY', 'Three booleans allow impossible combinations: loading and error and success all true at once. One enum makes the screen be in exactly one state.'),
                 ('SAY', "Click three: pending. It exists because a payment request can time out even though the backend completed it. The app doesn't know the result yet, so it must not say \"failed\"."),
                 ('ASK', 'Why not just show failure when the request times out?'),
                 ('EXPECT', 'Because the money may already have moved. Pending says "we are checking", not "it failed".'),
                 ('CONNECT', 'Who moves the screen between these states?'))))

# ================================================================== 13 · state flow loop
P = []
loop = [(10, 10, "user", "User intent", "tap Send"), (290, 10, "layout", "Presentation logic", "the ViewModel"),
        (290, 190, "eye", "Observable state", ".submitting"), (10, 190, "phone", "SwiftUI", "renders the state")]
for i, (x, y, ic, t, sub) in enumerate(loop):
    P.append(tall(x, y, 220, 104, ic, t, sub, f"{i + 1}"))
P.append(wire(f'M236 62H284{head(284, 62, "r")}'))
P.append(wire(f'M400 120V184{head(400, 184, "d")}'))
P.append(wire(f'M284 242H236{head(236, 242, "l")}'))
P.append(wire(f'M120 184V120{head(120, 120, "u")}'))
S.append(slide("Part 3 &middot; Data flow &middot; conceptual", "State flows one way, in a loop", f"""  <div class="body cols middle">
    {svg("0 0 520 300", "Loop: user intent, presentation logic, observable state, SwiftUI, back to user intent", "s13t", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="cols" style="grid-template-columns:1fr">
      <div class="card accent step"><span class="label">The ViewModel decides</span><p>which state the screen is in, for example that a spinner should show.</p></div>
      <div class="card accent step"><span class="label">SwiftUI renders</span><p>whatever the state says. It never decides on its own.</p></div>
    </div>
  </div>""", notes(('SAY', 'Follow the teal around the loop: the user taps Send, presentation logic handles it, it changes observable state, SwiftUI renders the new state, and the user sees it and acts again.'),
                 ('ASK', 'Who decides that a spinner appears? Who renders it?'),
                 ('EXPECT', 'The ViewModel (state) decides; SwiftUI renders. If the view decides, logic leaks back into body.'),
                 ('CONNECT', "Let's look at that ViewModel properly."))))

# ================================================================== chapter 4
S.append(chapter(4, "ViewModel, domain and service", "Who owns what inside the app",
                 "Three roles: the ViewModel coordinates the screen, domain values describe the business, and a service talks to the outside world."))

# ================================================================== 15 · VM responsibilities
S.append(slide("Part 4 &middot; ViewModel", "What a ViewModel owns, and what it doesn't", """  <div class="body cols middle">
    <div class="card accent step"><span class="label">Owns</span>
      <ul>
        <li>Screen state</li>
        <li>Loading</li>
        <li>Presentation formatting</li>
        <li>Async coordination</li>
      </ul>
    </div>
    <div class="card step"><span class="label">Avoid</span>
      <ul>
        <li>Backend authorization rules</li>
        <li>Direct database implementation</li>
        <li>Unrelated features</li>
        <li>Unprotected credential storage</li>
      </ul>
    </div>
  </div>""", notes(('SAY', 'The ViewModel owns everything about presenting this screen: its state, loading, formatting for display, and coordinating async work.'),
                 ('SAY', 'It must not become the new Massive View. Authorization belongs to the backend, storage belongs behind a service, other features get their own ViewModels, and credentials never sit in plain properties or UserDefaults.'),
                 ('ASK', 'Must every SwiftUI view have a ViewModel?'),
                 ('EXPECT', 'No. BalanceCard needs none. Add a ViewModel when a screen has real state and coordination.'),
                 ('CONNECT', "Here's the transfer ViewModel in code."))))

# ================================================================== 16 · VM code A
VMA = '''import Observation

protocol TransferSubmitting: Sendable {
    func submit(destination: String, amountInPaise: Int64) async throws -> String
}

@MainActor
@Observable
final class TransferViewModel {
    private(set) var state: TransferScreenState = .idle
    var amountInPaiseText = "50000"
    private let service: any TransferSubmitting

    init(service: any TransferSubmitting) {
        self.service = service
    }
}'''
S.append(slide("Part 4 &middot; ViewModel", "The transfer ViewModel", f"""  <div class="body cols middle" style="grid-template-columns:2.1fr 1fr">
    {code("TransferViewModel.swift", VMA, "font-size:14px")}
    <ul>
      <li class="step"><code>TransferSubmitting</code>: the service, as a protocol</li>
      <li class="step"><code>@Observable</code>: SwiftUI watches its state</li>
      <li class="step"><code>@MainActor</code>: UI state stays on the main actor</li>
      <li class="step"><code>private(set) state</code>: only the ViewModel changes it</li>
      <li class="step">Service <b>injected</b> through <code>init</code></li>
    </ul>
  </div>""", notes(('SAY', 'A teaching skeleton for iOS 17+ Observation. The ViewModel does not create its service; it receives one. That single decision makes it testable.'),
                 ('SAY', 'Note the amount is in paise, as an integer, on purpose. Production UI needs deliberate rupee parsing and rounding.'),
                 ('CONNECT', 'Now the one method that does the work: send.'))))
S[-1] = S[-1].replace('class="cols wide-left middle">', 'class="cols wide-left middle">', 1)

# ================================================================== 17 · send()
SEND = '''func send(to destination: String) async {
    guard let amount = Int64(amountInPaiseText), amount > 0 else {
        state = .failure(message: "Invalid amount")
        return
    }
    state = .submitting
    do {
        let ref = try await service.submit(
            destination: destination, amountInPaise: amount
        )
        state = .success(reference: ref)
    } catch is CancellationError {
        state = .pending(reference: nil)
    } catch {
        state = .pending(reference: nil)
    }
}'''
P = []
steps = [("check", "Validate input", "else .failure"), ("clock", ".submitting", "spinner shows"), ("send", "await submit()", "service call"),
         ("check", ".success(ref)", "confirmed")]
for i, (ic, t, sub) in enumerate(steps):
    y = i * 82
    P.append(row(0, y, 300, 62, ic, t, sub, f"{i + 1}"))
    if i < 3:
        P.append(wire(f'M150 {y + 62}V{y + 76}{head(150, y + 76, "d")}'))
P.append(wire(f'M300 195H330V368H310{head(310, 368, "l")}', "5"))
P.append(row(0, 338, 300, 62, "clock", ".pending", "cancelled or error", cls="alert"))
S.append(slide("Part 4 &middot; ViewModel", "<code>send()</code>: one async flow", f"""  <div class="body cols middle" style="grid-template-columns:1.75fr 1fr">
    {code("TransferViewModel.swift", SEND, "font-size:14.5px")}
    {svg("0 0 340 404", "send flow: validate, submitting, await submit, success; cancellation or error goes to pending", "s17t", P, "max-height:430px")}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
  </div>""", notes(('SAY', 'Click through: validate the amount, or fail fast. Set submitting, so the spinner appears. Await the service. On a reference, success.'),
                 ('SAY', "Click five: cancellation or any error goes to pending, not failure. A timeout or cancellation after submission does not prove the payment failed. The app must reconcile with the backend."),
                 ('ASK', 'Why do both catch blocks lead to pending?'),
                 ('EXPECT', "Because after the request left the device, the app can't know whether the backend completed it. Only reconciliation can tell."),
                 ('CONNECT', 'The ViewModel passes raw Int64 and String. Domain values make that safer.'))))

# ================================================================== 18 · domain values
DOM = '''struct Money: Equatable, Sendable { let paise: Int64 }
struct TransferRequest: Sendable {
    let destinationAccountId: String
    let amount: Money
}
struct TransferReceipt: Sendable { let reference: String }'''
S.append(slide("Part 4 &middot; Domain", "Domain values", f"""  <div class="body">
    {code("Domain.swift", DOM)}
    <div class="gap-lg"></div>
    {points([("bank", "Money as values", "whole paise, never floating point"), ("file", "Requests and receipts", "plain, Sendable values"), ("shield", "Use cases coordinate", "the server still validates")], label="Domain rules")}
  </div>""", notes(('SAY', 'Money is a value type holding whole paise in an Int64. Never use binary floating point for money: it cannot represent many decimal amounts exactly.'),
                 ('SAY', 'Requests and receipts are small Sendable values that can cross concurrency boundaries safely. Use cases coordinate an operation, but they do not replace authoritative server validation.'),
                 ('CONNECT', 'How does the ViewModel talk to a service without depending on a specific one?'))))

# ================================================================== 19 · dependency inversion
P = []
P.append(row(418, 0, 300, 60, "layout", "TransferViewModel"))
P.append(wire(f'M568 60V110{head(568, 110, "d")}'))
P.append(row(418, 116, 300, 60, "link", "TransferSubmitting", "protocol", l="1"))
P.append(row(330, 270, 230, 60, "globe", "LiveTransferService", l="2"))
P.append(row(600, 270, 230, 60, "check", "MockTransferService", "used by tests", l="3"))
P.append(row(40, 270, 220, 60, "globe", "URLSession", l="2"))
P.append(wire(f'M445 270V200{head(445, 182, "u")}', "2", "dash"))
P.append(wire(f'M715 270V200{head(715, 182, "u")}', "3", "dash"))
P.append('<text class="sm" x="455" y="232">conforms</text><text class="sm" x="725" y="232">conforms</text>')
P.append(wire(f'M330 300H266{head(266, 300, "l")}', "2"))
S.append(slide("Part 4 &middot; Dependency inversion &middot; conceptual", "Depend on a protocol, not a service", f"""  <div class="body">
    {svg("0 0 1136 336", "TransferViewModel depends on the TransferSubmitting protocol. LiveTransferService, which uses URLSession, and MockTransferService both conform.", "s19t", P, "max-height:360px")}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="gap"></div>
    <div class="rule step">High-level code depends on an <b>abstraction</b>. Tests inject a mock, with no real network.</div>
  </div>""", notes(('SAY', 'Click one: the ViewModel only knows the TransferSubmitting protocol. Click two: the live service conforms and uses URLSession. Click three: a mock conforms too. The ViewModel cannot tell the difference.'),
                 ('ASK', 'Why inject a protocol instead of creating LiveTransferService inside the ViewModel?'),
                 ('EXPECT', 'Lower coupling and replaceable implementations: tests, previews and future backends plug in without changing the ViewModel.'),
                 ('CONNECT', 'Here is how small a mock can be.'))))

# ================================================================== 20 · mock
MOCK = '''struct MockTransferService: TransferSubmitting {
    func submit(destination: String, amountInPaise: Int64) async throws -> String {
        "NPAY-DEMO-001"
    }
}'''
S.append(slide("Part 4 &middot; Testing seam", "A mock in five lines", f"""  <div class="body">
    {code("MockTransferService.swift", MOCK)}
    <div class="gap-lg"></div>
    {points([("check", "Deterministic", "always the same reference"), ("globe", "No network", "nothing leaves the test"), ("clock", "Instant", "tests stay fast")], label="Why a mock")}
  </div>""", notes(('SAY', 'The mock conforms to the same protocol and returns a fixed reference. Tests and SwiftUI previews can use it with no backend at all.'),
                 ('CONNECT', 'Now the real one: the live service and the network.'))))

# ================================================================== chapter 5
S.append(chapter(5, "Networking and execution flow", "From await to the bank and back",
                 "We have the shape. Now follow the actual request: what the live service sends, and the order things happen in."))

# ================================================================== 22 · live service
LIVE = '''import Foundation
struct LiveTransferService: TransferSubmitting {
    let session: URLSession
    let endpoint: URL

    func submit(destination: String, amountInPaise: Int64) async throws -> String {
        struct Payload: Encodable {
            let destination: String
            let amountInPaise: Int64
        }
        struct Reply: Decodable { let reference: String }
        var request = URLRequest(url: endpoint)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(
            Payload(destination: destination, amountInPaise: amountInPaise)
        )
        // Demo only: real code needs secure auth, idempotency,
        // status reconciliation, error classification and safe logging.
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse,
              (200...299).contains(http.statusCode) else {
            throw URLError(.badServerResponse)
        }
        return try JSONDecoder().decode(Reply.self, from: data).reference
    }
}'''
S.append(slide("Part 5 &middot; Networking", "The live service: a sketch", f"""  <div class="body cols wide-left" style="grid-template-columns:1.9fr 1fr;align-items:center">
    {code("LiveTransferService.swift", LIVE, "font-size:12.5px;line-height:1.3;padding:12px 18px")}
    <div>
      <div class="warn step" data-label="Demo only">Do not send real payments with this skeleton. The endpoint is an injected <b>test</b> endpoint.</div>
      <div class="gap"></div>
      <p class="small"><b>Real code also needs:</b></p>
      <ul class="small">
        <li class="step">Secure authentication</li>
        <li class="step">Idempotency</li>
        <li class="step">Status reconciliation</li>
        <li class="step">Error classification</li>
        <li class="step">Safe logging</li>
      </ul>
    </div>
  </div>""", notes(('SAY', 'Encode a payload, POST it, check for a 2xx status, decode the reference. URLSession and session, endpoint are injected, so this too can be tested.'),
                 ('SAY', 'This is a sketch. Real payment code needs secure auth, an idempotency key so a retry cannot pay twice, reconciliation of unknown outcomes, classification of errors, and logging that never leaks secrets.'),
                 ('CONNECT', "Now watch the whole round trip, in order."))))

# ================================================================== 23 · sequence
P = []
parts = [("user", "User"), ("phone", "SwiftUI"), ("layout", "ViewModel"), ("link", "Service"), ("bank", "NPay backend")]
lx = [100, 330, 560, 790, 1020]
for (ic, t), x in zip(parts, lx):
    P.append(row(x - 95, 0, 190, 46, ic, t))
    P.append(wire(f'M{x} 46V478', cls="dash faint"))
msgs = [(1, 0, 1, "Tap Send"), (1, 1, 2, "send()"), (2, 2, 2, "state = .submitting"), (2, 2, 3, "await submit()"),
        (3, 3, 4, "HTTPS request"), (4, 4, 3, "receipt or error"), (4, 3, 2, "decode or throw"),
        (5, 2, 2, "state update"), (5, 2, 1, "observable change"), (5, 1, 0, "confirmation or pending")]
y = 82
for g, a, b, label in msgs:
    grp = f'<g class="fade" data-lit="{g}+">'
    if a == b:
        x = lx[a]
        grp += wire(f'M{x} {y - 6}H{x + 46}V{y + 14}H{x + 8}{head(x + 8, y + 14, "l")}', str(g))
        grp += f'<g class="nd" data-lit="{g}"><text class="sm" x="{x + 56}" y="{y + 8}">{label}</text></g>'
    else:
        x1, x2 = lx[a], lx[b]
        d = "r" if x2 > x1 else "l"
        end = x2 - 6 if d == "r" else x2 + 6
        dash = "dash" if b < a else ""
        grp += wire(f'M{x1 + (6 if d == "r" else -6)} {y}H{end}{head(end, y, d)}', str(g), dash)
        grp += f'<g class="nd" data-lit="{g}"><text class="sm" x="{(x1 + x2) / 2:g}" y="{y - 8}" text-anchor="middle">{label}</text></g>'
    grp += '</g>'
    P.append(grp)
    y += 40
S.append(slide("Part 5 &middot; Sequence &middot; conceptual", "The round trip, step by step", f"""  <div class="body">
    {svg("0 0 1136 480", "Sequence: user taps Send, SwiftUI calls send, ViewModel sets submitting and awaits the service, service sends an HTTPS request to the NPay backend, receipt or error returns, ViewModel updates state, SwiftUI shows confirmation or pending.", "s23t", P, "max-height:500px")}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
  </div>""", notes(('SAY', 'Five clicks. One: the tap reaches SwiftUI, which calls send(). Two: the ViewModel sets submitting and awaits the service. Three: the request crosses HTTPS to the backend. Four: a receipt or error comes back and is decoded or thrown. Five: state updates, SwiftUI observes it and shows confirmation or pending.'),
                 ('ASK', 'If the request times out at click four, can the UI safely say "Payment failed"?'),
                 ('EXPECT', 'No. The result may be unknown; the backend may have completed it. Use backend reconciliation and idempotency keys.'),
                 ('CONNECT', 'Payments touch more than the network: storage, security, threads and the app lifecycle.'))))

# ================================================================== chapter 6
S.append(chapter(6, "Storage, security, lifecycle and concurrency", "What surrounds the payment",
                 "Four concerns cut across every layer we've drawn. Each has one key rule."))

# ================================================================== 25 · storage table
S.append(slide("Part 6 &middot; Storage", "Choose storage by data type", """  <div class="body top">
    <table class="tbl">
      <tr><th>Data</th><th>Owner</th><th>Caution</th></tr>
      <tr class="step"><td>Loading state</td><td>ViewModel</td><td>Ephemeral</td></tr>
      <tr class="step"><td>Theme</td><td>UserDefaults</td><td>Nonsecret</td></tr>
      <tr class="step hl"><td>Auth token</td><td><b>Keychain</b></td><td>Access controls</td></tr>
      <tr class="step"><td>Cached activity</td><td>SwiftData / files</td><td>Freshness and data protection</td></tr>
      <tr class="step"><td>Balance</td><td>Backend</td><td>Client copy is not authoritative</td></tr>
    </table>
  </div>""", notes(('SAY', 'Each kind of data has a natural home. Screen state lives in the ViewModel and disappears. A theme preference is fine in UserDefaults because it is not secret. Tokens go in the Keychain with access controls.'),
                 ('SAY', 'Cached activity can live in SwiftData or files, but watch freshness and data protection. And the balance belongs to the backend: whatever the app shows is a copy.'),
                 ('ASK', 'Why not store the auth token in UserDefaults?'),
                 ('EXPECT', 'UserDefaults is not designed for secrets. The Keychain provides encrypted, access-controlled storage.'),
                 ('CONNECT', 'Security is not one class. It is several boundaries.'))))

# ================================================================== 26 · security boundaries
P = []
sec = [("lock", "Code signing", "the app is genuine"), ("shield", "Sandbox", "the process is contained"), ("key", "Keychain", "secrets at rest"),
       ("globe", "HTTPS", "data in transit"), ("bank", "Backend authorization", "who may pay whom")]
for i, (ic, t, sub) in enumerate(sec):
    x = i * 228
    P.append(tall(x, 10, 200, 120, ic, t, sub, str(i + 1)))
    if i < 4:
        P.append(wire(f'M{x + 204} 70H{x + 222}{head(x + 222, 70, "r")}'))
S.append(slide("Part 6 &middot; Security", "Security crosses layers", f"""  <div class="body">
    {svg("0 0 1136 140", "Five security boundaries: code signing, sandbox, Keychain, HTTPS, backend authorization", "s26t", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="gap-lg"></div>
    <div class="takeaway step">No single class or permission secures everything. Each boundary protects <b>something different</b>.</div>
  </div>""", notes(('SAY', 'Click through the five. Signing proves the app is genuine. The sandbox contains the process. The Keychain protects secrets on the device. HTTPS protects data in transit. Backend authorization decides who may move money.'),
                 ('CONNECT', 'Next: threads, and what await really does.'))))

# ================================================================== 27 · concurrency
P = []
P.append('<text class="mono" x="0" y="16">MAIN ACTOR</text>')
P.append('<g class="nd" data-lit="1"><rect class="sh" x="0" y="28" width="300" height="40" rx="8"/><text class="sm" x="150" y="53" text-anchor="middle">send() runs</text></g>')
P.append('<g class="nd" data-lit="2"><rect class="sh" x="300" y="28" width="520" height="40" rx="8"/><text class="sm" x="560" y="53" text-anchor="middle">await: task suspended, the main actor is free for UI</text></g>')
P.append('<g class="nd" data-lit="3"><rect class="sh" x="820" y="28" width="316" height="40" rx="8"/><text class="sm" x="978" y="53" text-anchor="middle">resumes: state = .success</text></g>')
S.append(slide("Part 6 &middot; Concurrency", "await suspends; it does not block", f"""  <div class="body">
    {svg("0 0 1136 72", "Main actor lane: send runs, then is suspended at await while the main actor stays free, then resumes and sets success", "s27t", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="gap-lg"></div>
    {points([("phone", "@MainActor", "for UI-related mutable state"), ("clock", "await suspends a task", "it does not automatically block a thread"), ("layers", "Actors are reentrant", "state can change across await")], label="Three rules")}
  </div>""", notes(('SAY', 'Click through the lane: send() starts on the main actor, suspends at await so the UI stays responsive, then resumes and updates state.'),
                 ('SAY', 'Actor isolation protects mutable state, but actors can be reentrant across await: another call can run while one is suspended. Do not treat actor methods as durable transactions.'),
                 ('ASK', 'Does await create a new thread?'),
                 ('EXPECT', 'No. It marks a suspension point. The task pauses; the thread can do other work.'),
                 ('CONNECT', 'Now the hardest case: the user leaves the app mid-payment.'))))

# ================================================================== 28 · lifecycle
P = []
P.append('<text class="mono" x="0" y="16">DEVICE</text><text class="mono" x="0" y="146">BACKEND</text>')
P.append(row(0, 28, 220, 56, "send", "Tap Send", l="1"))
P.append(wire(f'M226 56H254{head(254, 56, "r")}'))
P.append(row(260, 28, 250, 56, "clock", "Request in flight", l="1"))
P.append(wire(f'M516 56H544{head(544, 56, "r")}'))
P.append(row(550, 28, 270, 56, "cross", "User leaves: task cancelled", cls="alert"))
P.append(wire(f'M826 56H854{head(854, 56, "r")}'))
P.append(row(860, 28, 276, 56, "check", "Return: reconcile status", l="4"))
P.append(wire(f'M385 84V152{head(385, 152, "d")}', "2", "dash"))
P.append(row(260, 158, 560, 56, "bank", "Payment may still complete", "by reference / idempotency key", l="2 3"))
P.append(wire(f'M820 186H998V90{head(998, 90, "u")}', "4", "dash"))
S.append(slide("Part 6 &middot; Lifecycle &middot; conceptual", "Cancelled locally is not cancelled at the bank", f"""  <div class="body">
    {svg("0 0 1136 220", "Device lane: tap Send, request in flight, user leaves and the task is cancelled, user returns and reconciles. Backend lane: the payment may still complete.", "s28t", P)}
    <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
    <div class="gap-lg"></div>
    <div class="rule step">Keep a recoverable <b>transaction reference</b> or <b>idempotency identifier</b>, and reconcile status when the user returns.</div>
  </div>""", notes(('SAY', "Click one: the request leaves the device. Click two: the backend receives it. Click three: the user leaves NPay and the view's task may be cancelled, but the backend can still complete the payment. Click four: when the user returns, reconcile using the reference."),
                 ('ASK', 'If the local task is cancelled, was the payment cancelled?'),
                 ('EXPECT', 'Not necessarily. Cancelling local work does not reach back into the bank.'),
                 ('CONNECT', "That's an application lifecycle problem; we go deeper in Lesson 0.3. First, the patterns teams use to organize all this."))))

# ================================================================== chapter 7
S.append(chapter(7, "Architecture alternatives", "Patterns, not rules",
                 "MVVM is not the only answer. Four common patterns, what each is good at, and where each goes wrong."))

# ================================================================== 30 · alternatives
alts = [("MVC", "Model, View, Controller", "Common in UIKit", "A controller that owns every concern becomes hard to maintain."),
        ("MVVM", "View, ViewModel, Model", "Common with SwiftUI, not mandated by Apple", "View describes UI; ViewModel coordinates presentation state."),
        ("Unidirectional", "Action, state transition, render", "Multi-step payment flows", "Every state change is explicit and testable."),
        ("Layered / Clean", "Domain apart from adapters", "When complexity warrants it", "Don't create meaningless layers just for appearances.")]
cards = "\n".join(f'      <div class="card accent step"><span class="label">{a}</span><h3 style="font-size:22px;margin:2px 0 6px">{b}</h3><p class="small" style="margin:0 0 6px"><b>{c}</b></p><p class="small muted" style="margin:0">{d}</p></div>' for a, b, c, d in alts)
S.append(slide("Part 7 &middot; Patterns", "Four ways to organize an app", f"""  <div class="body">
    <div class="cols" style="row-gap:20px">
{cards}
    </div>
  </div>""", notes(('SAY', 'MVC: common in UIKit and fine until one controller owns everything. MVVM: common with SwiftUI, though Apple does not mandate it. Unidirectional data flow: action, state transition, render; strong for multi-step payments. Layered or Clean: domain policy separated from transport and persistence, worth it when complexity warrants.'),
                 ('ASK', 'Which one should NPay use?'),
                 ('EXPECT', 'MVVM per feature is a good default, with unidirectional flow for complex payment steps. The point is clear ownership, not the label.'),
                 ('CONNECT', 'Here is one way to lay NPay out on disk.'))))

# ================================================================== 31 · structure
TREE = '''<span class="dir">NPay/</span>
  <span class="dir">App/</span>
  <span class="dir">Features/</span>
    <span class="dir">Dashboard/</span>
      DashboardView.swift
      DashboardViewModel.swift
    <span class="dir">Transfer/</span>
      TransferView.swift
      TransferViewModel.swift
  <span class="dir">Domain/</span>
    Money.swift
    TransferRequest.swift
    TransferSubmitting.swift
  <span class="dir">Data/</span>
    LiveTransferService.swift
    MockTransferService.swift
  <span class="dir">Shared/DesignSystem/</span>
  <span class="dir">Tests/</span>'''
S.append(slide("Part 7 &middot; Structure", "A suggested NPay structure", f"""  <div class="body cols middle">
    <pre class="tree" style="font-size:17px">{TREE}</pre>
    <div>
      {points([("phone", "Features", "a View and ViewModel per screen"), ("bank", "Domain", "values and protocols"), ("globe", "Data", "live and mock services"), ("check", "Tests", "beside the code they cover")], cls="v", box="card accent", step=False)}
      <div class="gap"></div>
      <p class="small muted">One valid structure, not an Apple requirement.</p>
    </div>
  </div>""", notes(('SAY', 'Group by feature first: Dashboard and Transfer each hold their view and ViewModel. Domain holds values and protocols with no UIKit or networking. Data holds the services that talk to the outside world. Shared holds the design system.'),
                 ('CONNECT', "Structure is only worth it if we can test it. Let's write a test."))))

# ================================================================== chapter 8
S.append(chapter(8, "Test and review", "Prove it, then spot what's wrong",
                 "The payoff of all this separation: we can test the transfer logic without a screen or a network."))

# ================================================================== 33 · Swift Testing
TEST = '''import Testing

@Test @MainActor
func successfulTransferChangesState() async {
    let vm = TransferViewModel(service: MockTransferService())
    vm.amountInPaiseText = "50000"
    await vm.send(to: "NPAY-TEST-002")
    #expect(vm.state == .success(reference: "NPAY-DEMO-001"))
}'''
S.append(slide("Part 8 &middot; Testing", "Testing the ViewModel", f"""  <div class="body">
    {code("TransferViewModelTests.swift", TEST)}
    <div class="gap-lg"></div>
    <div class="card accent step"><span class="label">Also test</span>
      <p style="margin:6px 0 0"><span class="pill">Invalid input</span><span class="pill">Known failure</span><span class="pill">Unknown status</span><span class="pill">Cancellation</span><span class="pill">Recovery</span></p>
    </div>
  </div>""", notes(('SAY', 'Swift Testing: inject the mock, set the amount, await send, expect success with the mock reference. No view, no network, runs in milliseconds.'),
                 ('SAY', 'One happy path is not enough. Test invalid input, a known failure, an unknown status, cancellation and recovery.'),
                 ('CONNECT', "Now let's review some code that gets this wrong."))))

# ================================================================== 34 · anti-patterns
anti = [("All business logic lives in <code>View.body</code>", "Move it to a ViewModel or use case"),
        ("Every view calls <code>URLSession</code> directly", "One service, behind a protocol"),
        ("One ViewModel handles unrelated features", "One ViewModel per feature or screen"),
        ("Money uses binary floating point", "Integer minor units (paise) in a <code>Money</code> type"),
        ("Auth tokens saved in <code>UserDefaults</code>", "Keychain"),
        ("UI shows success before server confirmation", "Pending until the backend confirms"),
        ("Retry after timeout blindly resubmits", "Reconcile first; reuse the idempotency key"),
        ("Service hardcoded, impossible to mock", "Inject it through a protocol")]
rows = "\n".join(f'      <tr class="step"><td>{a}</td><td>{b}</td></tr>' for a, b in anti)
S.append(slide("Part 8 &middot; Review", "Spot the anti-pattern", f"""  <div class="body top">
    <table class="tbl" style="font-size:19px">
      <tr><th>Anti-pattern</th><th>Better</th></tr>
{rows}
    </table>
  </div>""", notes(('SAY', 'Eight smells you will meet in real code reviews. For each, name the risk before revealing the fix.'),
                 ('ASK', 'Which of these could cause a customer to be charged twice?'),
                 ('EXPECT', 'Blind retry after a timeout. Without reconciliation and an idempotency key, a retry can submit a second transfer.'),
                 ('CONNECT', "Let's check your understanding."))))

# ================================================================== review
S.append("""<!-- ============================================================
     REVIEW — CHECK YOUR UNDERSTANDING
     ============================================================ -->
<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Now we test what stuck. For each question, everyone commits to an answer before we reveal it.')) + "</section>\n\n")

QA = [("kernel", "Who creates and manages an iOS app&rsquo;s process?", "The operating system", "Process creation and management are OS responsibilities. SwiftUI operates within the app process.", "Thinking SwiftUI or the ViewModel starts the app.", "Some say SwiftUI. It runs inside a process the OS already created."),
      ("eye", "What should happen when observable SwiftUI state changes?", "Update the affected UI", "SwiftUI re-evaluates the relevant view descriptions and manages the necessary interface updates.", "Expecting to redraw every pixel manually, or restart the app.", "Imperative habits suggest manual redraws. SwiftUI handles the update."),
      ("phone", "Which component normally coordinates a balance-screen loading state in MVVM?", "The ViewModel", "It commonly owns presentation state and coordinates loading through a service. SwiftUI only renders that state.", "Letting the view decide, which pulls logic back into body.", "Many say the view. State decides; SwiftUI renders."),
      ("layers", "Is MVVM part of the operating system?", "No", "It is an application design pattern we choose.", "Mixing up platform architecture with application architecture.", "Some assume Apple requires it. It is our choice."),
      ("layout", "Must every SwiftUI view have a ViewModel?", "No", "Simple views like BalanceCard need none. Add one when a screen has real state and coordination.", "Creating a ViewModel for every view by reflex.", "Some think MVVM means one per view."),
      ("clock", "Does <code>await</code> mean a new thread?", "No", "It marks a suspension point. The task pauses and the thread can do other work.", "Treating await like starting a background thread.", "Many say yes."),
      ("shield", "Does client validation authorize a transfer?", "No", "Client checks improve usability. The backend must enforce authorization.", "Trusting checks that run on a device the user controls.", "Some say yes, because the app already checked the amount."),
      ("link", "Why inject a protocol?", "Loose coupling", "Implementations become replaceable: live, mock for tests, or a new backend, without changing the ViewModel.", "Hardcoding a service that tests cannot replace.", "Answers like \"it is cleaner\" are vague. Push for coupling and replaceability."),
      ("bank", "Is the backend inside the iOS process?", "No", "It is a separate system across a trust boundary, reached over HTTPS.", "Thinking of the backend as part of the app.", "Most get this; confirm the words \"trust boundary\"."),
      ("cross", "The request times out. Can the UI show \"Payment failed\"?", "No", "The result may be unknown. Show pending, then reconcile using the reference and idempotency key.", "Equating a timeout with a failed payment.", "Many say yes. The backend may already have completed it."),
      ("check", "How do you test transfer validation without launching a view?", "Move it out of the view", "Put it in the ViewModel, inject a mock service, and test it with Swift Testing.", "Leaving logic inside body, where only UI tests can reach it.", "Some suggest UI tests. They work but are slow; separation makes unit tests possible.")]
QA = QA[:3]   # lesson text's knowledge check only
N = len(QA)
for i, (ic, q, v, why, trap, exp) in enumerate(QA):
    dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
    import re
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
""" + notes(('ASK', 'Give everyone a few seconds to decide, then take a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
            ('CONNECT', 'Next question.' if i < N - 1 else 'One last look: what comes next.')) + "</section>\n\n")

# ================================================================== challenge
P = []
chain = ["View", "ViewModel", "Use case", "Service protocol", "Network adapter", "HTTPS (authenticated)", "Backend ledger", "Decoded result", "Observable state", "SwiftUI"]
for i, t in enumerate(chain):
    r, c = divmod(i, 5)
    x = c * 228
    y = r * 92
    P.append(f'<g class="nd pass" data-lit="1" style="--d:{i * .12:.2f}s"><rect class="sh" x="{x}" y="{y}" width="200" height="56" rx="12"/><text x="{x + 100}" y="{y + 34}" text-anchor="middle">{t}</text></g>')
    if c < 4:
        P.append(wire(f'M{x + 204} {y + 28}H{x + 222}{head(x + 222, y + 28, "r")}'))
P.append(wire(f'M1012 56V74H100V86{head(100, 86, "d")}'))
S.append(slide("Your challenge", "Narrate the payment", f"""  <div class="body">
    <p class="lead" style="font-size:22px;line-height:1.55;max-width:1000px">"Explain what happens after the NPay user taps Send, from UI intent to backend confirmation and UI state update. Identify the <b style="color:var(--teal)">ownership</b> and <b style="color:var(--teal)">trust</b> boundaries."</p>
    <div class="gap-lg"></div>
    <div class="step anim-up">
      {svg("0 0 1136 148", "Expected chain: view, ViewModel, use case, service protocol, network adapter, authenticated HTTPS, backend ledger, decoded result, observable state, SwiftUI", "s45t", P)}
    </div>
  </div>""", notes(('SAY', 'Final challenge. Narrate the payment end to end, and name every boundary you cross: which code owns each step, and where trust changes.'),
                 ('EXPECT', 'View, ViewModel, domain or use case, service protocol, network adapter, authenticated HTTPS, backend ledger, decoded result, observable state, SwiftUI. The trust boundary is the HTTPS hop to the backend.'),
                 ('CONNECT', 'One open question remains: what if the user leaves NPay while the request is still in flight?'))))

# ================================================================== end
S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.2 complete</p>
    <h2>iOS App Architecture:<br>Who Does What?</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: the iOS application lifecycle</p>
  </div>
""" + notes(('SAY', 'Recap: iOS manages the process; our app architecture organizes the code inside it. The view displays and receives interaction, the ViewModel owns screen state, the service hides where data comes from, and the network and storage sit behind it. A request goes down the layers and the result comes back up. And SwiftUI is declarative: change the state, and the interface follows.'),
            ('SAY', 'Next lesson goes one layer deeper into the application lifecycle: app process versus scene; foreground, background and suspension; what happens when the user presses Home; why iOS may terminate apps under memory pressure; cold launch versus warm activation; and the SwiftUI lifecycle versus UIKit AppDelegate and SceneDelegate.'),
            ('CONNECT', 'This matters for real-world app behavior and debugging.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.2 — iOS App Architecture: Who Does What?</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.2 — iOS App Architecture: Who Does What?">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT, 'w').write(doc)
print(len(S), 'slides')
