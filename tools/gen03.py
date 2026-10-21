"""Generates decks/lesson-0.3/index.html from the Lesson 0.3 text only (no code on slides)."""
import html, re, sys
OUT03 = sys.argv[1]
sys.argv = ['x', '/dev/null']
src = open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers: lit, tall, row, wire, head, svg, notes, slide, points, E

S = []


def divider(n, title, lead, say, con):
    S.append(f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(('SAY', say), ('CONNECT', con))}</section>

""")


def cues(n):
    return '<i class="step cue"></i>' * n


# ------------------------------------------------------------------ title
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.3</p>
    <h1 style="font-size:54px;line-height:1.05">iOS Application<br>Lifecycle Deep Dive</h1>
    <p class="lead" style="max-width:660px">When a user leaves an iPhone app, what actually happens to that app?</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'Today we answer a fundamental question: when a user leaves an iPhone app, what actually happens to that app? Does it stop? Does it keep running? Is it destroyed? And what happens when the user returns?'),
            ('CONNECT', 'These questions lead us into the iOS application lifecycle. Here is our route.')) + "</section>\n\n")

# ------------------------------------------------------------------ journey
journey = [("process", "Process versus scene"), ("layers", "Foreground, background and suspension"), ("play", "Cold launch versus warm activation"),
           ("memory", "Memory pressure and app termination"), ("frameworks", "SwiftUI versus UIKit lifecycle"), ("check", "Real-world architecture and challenges")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p><b>{t}</b></p></div>' for i, t in journey)
S.append(slide("Lesson 0.3 &middot; Our learning journey", "Six concepts, step by step", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'We will progressively cover six concepts: process versus scene; foreground, background and suspension; cold launch versus warm activation; memory pressure and termination; SwiftUI versus UIKit lifecycle; and what all of this means for real-world architecture.'),
                 ('CONNECT', 'We start with the most important distinction.'))))

# ================================================================== Part 1
divider(1, "Process versus scene", "The most important distinction",
        "Two words people use interchangeably, but iOS treats very differently.", "Start with a picture: a shopping mall.")

# mall analogy
P = ['<g class="nd ghost" data-lit="1"><rect class="sh" x="10" y="34" width="540" height="390" rx="18"/></g>',
     '<g class="nd" data-lit="1"><use href="#i-building" x="10" y="0" width="24" height="24"/><text class="mono" x="42" y="18">MALL MANAGEMENT: THE OPERATING SYSTEM</text></g>',
     '<g class="nd" data-lit="2"><rect class="sh" x="36" y="60" width="488" height="300" rx="14"/><text class="mono" x="56" y="88">MALL BUILDING: THE APP PROCESS</text></g>']
for i, (x, y, name) in enumerate([(60, 104, "Shop A"), (296, 104, "Shop B"), (60, 230, "Shop C"), (296, 230, "Shop D")]):
    P.append(f'<g class="nd" data-lit="3"><rect class="sh" x="{x}" y="{y}" width="204" height="106" rx="12"/><use href="#i-grid" x="{x + 89}" y="{y + 18}" width="26" height="26"/><text x="{x + 102}" y="{y + 72}" text-anchor="middle">{name}</text><text class="sm" x="{x + 102}" y="{y + 92}" text-anchor="middle">a scene</text></g>')
P.append('<g class="fade" data-lit="4"><use href="#i-user" x="246" y="380" width="30" height="30" style="color:var(--teal)"/><text class="sm" x="284" y="400">the user visits different shops</text></g>')
art = svg("0 0 560 430", "A shopping mall: mall management is the operating system, the building is the app process, each shop is a scene, and the user visits different shops.", "s3mall", P, "max-height:470px")
rows = [("building", "Mall management", "the operating system"), ("process", "The mall building", "an application process"),
        ("grid", "Each shop", "a scene"), ("user", "The visitor", "the user, moving between shops")]
lst = "\n".join(f'        <div class="step"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg><span><b>{t}</b><small>{d}</small></span></div>' for i, t, d in rows)
S.append(slide("Part 1 &middot; Analogy", "Think of a shopping mall", f"""  <div class="body cols middle" style="grid-template-columns:1.15fr 1fr">
    {art}
    <div>
      <div class="points v">
{lst}
      </div>
      <div class="gap"></div>
      <p class="step">One building can contain several shops. One app process can manage <b>multiple scenes</b>.</p>
    </div>
  </div>""", notes(('SAY', 'The mall building is the application process. Each shop is a scene. The operating system is the mall management, and the user visits different shops.'),
                 ('SAY', 'One building can contain several shops. Similarly, one iOS app process can manage multiple scenes.'),
                 ('CONNECT', "Now the same idea in iOS terms."))))

# process vs scene diagram
P = ['<g class="nd" data-lit="1"><rect class="sh" x="0" y="0" width="560" height="330" rx="18"/><use href="#i-process" x="22" y="20" width="26" height="26"/>'
     '<text x="58" y="34">App process</text><text class="sm" x="58" y="54">shared executable code, memory, threads and services</text></g>',
     '<g class="nd lit" data-lit="2+"><rect class="sh" x="24" y="90" width="244" height="210" rx="14"/><use href="#i-phone" x="132" y="112" width="28" height="28"/>'
     '<text x="146" y="176" text-anchor="middle">Scene A</text><text class="sm" x="146" y="198" text-anchor="middle">product catalog</text></g>',
     '<g class="fade" data-lit="2+"><text class="mono" x="146" y="262" text-anchor="middle">ACTIVE</text></g>',
     '<g class="nd"><rect class="sh" x="292" y="90" width="244" height="210" rx="14"/><use href="#i-phone" x="400" y="112" width="28" height="28"/>'
     '<text x="414" y="176" text-anchor="middle">Scene B</text><text class="sm" x="414" y="198" text-anchor="middle">order details</text></g>',
     '<g class="fade" data-lit="2+"><text class="mono" x="414" y="262" text-anchor="middle">BACKGROUND</text></g>']
art = svg("0 0 560 332", "One app process containing two scenes: scene A, product catalog, is active; scene B, order details, is in the background.", "s4ps", P, "max-height:360px")
S.append(slide("Part 1 &middot; Process vs scene &middot; conceptual", "One process, several scenes", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    <div>
      {art}
      {cues(2)}
      <p class="small muted" style="margin:10px 0 0">Conceptual multiwindow example. Most relevant on iPadOS; an ordinary iPhone app commonly has one main window scene.</p>
    </div>
    <div>
      {points([("process", "Process", "a running instance of your app: its execution environment"), ("phone", "Scene", "an instance of your app&rsquo;s UI that the system manages, with its own lifecycle states")], cls="v", box="card accent", step=False)}
      <div class="gap"></div>
      <div class="rule step" data-label="Critical point">One scene can be in the <b>background</b> while another scene of the same app is <b>active</b>. Scene lifecycle and process state are not the same.</div>
    </div>
  </div>""", notes(('SAY', 'A process is a running instance of your application; it contains the execution environment. A scene represents an instance of your app’s UI that the system manages, and scenes have their own lifecycle states.'),
                   ('SAY', 'Click two: scene A, the product catalog, is active while scene B, order details, is in the background. Same process, different scene states.'),
                   ('SAY', 'Multiple simultaneous windows matter most on iPadOS. An ordinary iPhone app commonly has one main window scene.'),
                   ('ASK', 'Can one scene be in the background while another scene of the same app is active?'),
                   ('EXPECT', 'Yes. Scene states are per scene; the process is shared.'),
                   ('CONNECT', 'So which states exist, and which belong to the scene versus the process?'))))
S[-1] = S[-1].replace('\n  ' + cues(2) + '\n', '\n  <div hidden>' + cues(2) + '</div>\n') if False else S[-1]

# ================================================================== Part 2
divider(2, "Understand the lifecycle states", "Foreground, background and suspension",
        "First, separate two categories of state: what the scene reports, and what the process is doing.", "Two lists, not one.")
S.append(slide("Part 2 &middot; Two categories", "Scene states vs process conditions", """  <div class="body">
    <div class="cols stretch">
      <div class="card accent step"><span class="label">Scene states (SwiftUI scenePhase)</span>
        <ul><li>Active</li><li>Inactive</li><li>Background</li></ul></div>
      <div class="card step"><span class="label">Process execution conditions</span>
        <ul><li>Running</li><li>Suspended</li><li>Terminated</li></ul></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Watch the words"><b>Suspended</b> is not a SwiftUI scenePhase value. It describes the process, not the scene.</div>
  </div>""", notes(('SAY', 'Scene states exposed through SwiftUI’s scenePhase are active, inactive and background. Process execution conditions are running, suspended and terminated.'),
                   ('SAY', 'Suspended is not a scenePhase value. Students often look for it there; it belongs to the process.'),
                   ('CONNECT', 'Now put them together for a typical single-scene iPhone app.'))))

states = [("cross", "Not running", "no app process exists"), ("play", "Active", "foreground, accepting user interaction"), ("clock", "Inactive", "foreground, temporarily not active"),
          ("layers", "Background", "no longer foreground; may run briefly"), ("memory", "Suspended", "kept in memory, not executing"), ("cross", "Terminated", "process no longer exists")]
P = []
for i, (ic, t, sub) in enumerate(states):
    r, c = divmod(i, 3)
    x, y = c * 398, r * 170
    P.append(tall(x, y, 340, 110, ic, t, sub, str(i + 1), 'alert' if t == 'Terminated' else ''))
    if c < 2:
        P.append(wire(f'M{x + 346} {y + 55}H{x + 392}{head(x + 392, y + 55, "r")}'))
P.append(wire(f'M966 110V140H170V164{head(170, 164, "d")}'))
S.append(slide("Part 2 &middot; Lifecycle &middot; conceptual", "A typical single-scene iPhone app", f"""  <div class="body">
    {svg("0 0 1136 282", "Not running, active, inactive, background, suspended, terminated", "s6states", P)}
    {cues(6)}
    <div class="gap"></div>
    <p class="small muted">One possible progression, not a mandatory sequence. An app may return to the foreground, be terminated directly, or follow other transitions.</p>
  </div>""", notes(('SAY', 'Click through: not running, no process exists. Active: in the foreground, accepting interaction. Inactive: still in the foreground but temporarily not active. Background: no longer in the foreground; execution may continue briefly. Suspended: the process is kept in memory but not executing. Terminated: the process no longer exists.'),
                   ('SAY', 'This is one possible path, not a required sequence. An app can come back to the foreground, be terminated directly, or take other transitions.'),
                   ('ASK', 'Is suspended one of the SwiftUI scenePhase values?'),
                   ('EXPECT', 'No. Suspended is a process condition, not a scene state.'),
                   ('CONNECT', "Let's walk through it with NPay."))))

# ================================================================== Part 3
divider(3, "Let&rsquo;s simulate the app lifecycle", "One banking app, five moments",
        "Imagine using NPay, our banking app. We will watch its scene and its process change.", "Five scenarios, one per click.")
sc = [("App not running", "No scene", "Not running", "Tap the NPay icon",
       "NPay is installed, but there is no running process. The system launches the app and activates its initial scene."),
      ("Using the app", "Active", "Running", "Swipe up to the Home Screen",
       "The user checks the balance. The scene is active and the process is running."),
      ("Just left the app", "Background", "Running briefly", "Wait while the user is in another app",
       "The scene moves to the background. Execution may continue briefly."),
      ("Suspended", "Background", "Suspended", "The user opens a memory-heavy game",
       "The process stays in memory but no code runs."),
      ("Terminated", "No scene", "Terminated", "Tap the NPay icon again",
       "iOS reclaimed the memory. Opening NPay now is a fresh launch.")]
P = []
for i, (t, *_rest) in enumerate(sc):
    x = i * 230
    P.append(row(x, 0, 212, 52, '', f"{i + 1}. {t}", '', str(i)))
for i, (t, scene, proc, nxt, desc) in enumerate(sc):
    P.append(f'<g class="fade" data-lit="{i}"><text class="mono" x="0" y="100">SCENARIO {i + 1} OF 5</text>'
             f'<text x="0" y="134" style="font-size:26px;font-weight:700">{t}</text>'
             f'<text x="0" y="168" style="font-size:19px;font-weight:400">{desc}</text>'
             f'<g class="nd"><rect class="sh" x="0" y="196" width="360" height="74" rx="12"/><text class="mono" x="20" y="224">SCENE</text><text x="20" y="254">{scene}</text></g>'
             f'<g class="nd{" alert" if proc == "Terminated" else ""}"><rect class="sh" x="388" y="196" width="360" height="74" rx="12"/><text class="mono" x="408" y="224">PROCESS STATUS</text><text x="408" y="254">{proc}</text></g>'
             f'<g class="nd" data-lit="{i}"><rect class="sh" x="776" y="196" width="360" height="74" rx="12"/><text class="mono" x="796" y="224">NEXT EVENT</text><text x="796" y="254">{nxt}</text></g></g>')
S.append(slide("Part 3 &middot; Lifecycle simulator &middot; conceptual", "NPay through five moments", f"""  <div class="body">
    {svg("0 0 1136 272", "Five scenarios: not running, using the app, just left, suspended, terminated; each shows scene state, process status and the next event.", "s8sim", P)}
    {cues(4)}
  </div>""", notes(('SAY', 'Scenario one: NPay is installed but not running; there is no process. The next event, tapping the icon, makes the system launch the app and activate its initial scene. Click through the other four: using the app, just leaving it, suspension, and termination.'),
                   ('SAY', 'Watch the two status boxes: the scene and the process change separately.'),
                   ('CONNECT', 'Two misconceptions come up at exactly this point.'))))
S.append(slide("Part 3 &middot; Misconceptions", "Two things that are not true", """  <div class="body top">
    <table class="tbl">
      <tr><th>Myth</th><th>Reality</th></tr>
      <tr><td>&ldquo;When the user switches apps, the old app is killed.&rdquo;</td><td>iOS usually moves its scene to the <b>background</b> and may eventually <b>suspend</b> the process. Termination is a separate possibility.</td></tr>
      <tr><td>&ldquo;Background means continuous execution.&rdquo;</td><td>Background does <b>not</b> mean unrestricted execution.</td></tr>
    </table>
  </div>""", notes(('SAY', 'A common misconception: when the user switches apps, the old app is killed. That is incorrect. iOS usually moves the old app’s scene to the background and may eventually suspend its process. Termination is a separate possibility.'),
                   ('SAY', 'Another misconception: background means continuous execution. Background does not mean unrestricted execution.'),
                   ('CONNECT', 'So what does the system do when the user comes back?'))))

# ================================================================== Part 4
divider(4, "Cold launch versus warm activation", "Same tap, different work",
        "The user performs the same action, tapping the app icon, but iOS may perform different internal work.", "Imagine opening a shopping app three times.")
kinds = [("Cold", "New process", "Application initialization must happen again."),
         ("Warm", "Existing process", "Application state may already be in memory."),
         ("Running", "Existing running process", "The app can become foreground without being resumed from suspension.")]
cards = "\n".join(f'      <div class="card{" accent" if i == 2 else ""} step"><span class="label">{k}</span><h3 style="font-size:22px;margin:4px 0 8px">{t}</h3><p class="small" style="margin:0">{d}</p></div>' for i, (k, t, d) in enumerate(kinds))
S.append(slide("Part 4 &middot; Three cases", "One tap, three possible situations", f"""  <div class="body">
    <div class="cols c3 stretch">
{cards}
    </div>
    <div class="gap"></div>
    <p class="small muted step">Cold, warm and hot launch are often used informally; their precise meanings vary by performance tool or discussion.</p>
  </div>""", notes(('SAY', 'For teaching, the clearest distinction: a new process means initialization must happen again. An existing process means application state may already be in memory. An existing running process can become foreground without being resumed from suspension.'),
                   ('SAY', 'The running case: the app is still executing eligible background work. The user brings it forward, the scene transitions through lifecycle states, and foreground interaction resumes, with no process creation or suspension recovery.'),
                   ('SAY', 'Developers use cold, warm and hot launch informally, and the exact meanings vary by tool. Teach the process distinction rather than the labels.'),
                   ('CONNECT', 'Why does this matter to us? A banking example.'))))
P = [row(388, 0, 360, 62, "user", "Balance shows &#8377;50,000", "the user switches apps, then returns"),
     wire(f'M568 62V86H190V112{head(190, 112, "d")}M568 86H946V112{head(946, 112, "d")}'),
     row(0, 118, 380, 78, "check", "Process survived", "in-memory balance may still be &#8377;50,000", "1+"),
     row(756, 118, 380, 78, "cross", "Process terminated", "rebuild the interface, retrieve or restore data", "2", "alert")]
S.append(slide("Part 4 &middot; Example &middot; conceptual", "Coming back to NPay", f"""  <div class="body">
    {svg("0 0 1136 200", "The user switches away from NPay showing 50,000 rupees and returns; if the process survived the balance may still be in memory, if it was terminated the app must rebuild and restore.", "s11ex", P)}
    {cues(2)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Architectural rule">Never design an iOS application assuming that its <b>process will remain alive</b>.</div>
  </div>""", notes(('SAY', 'NPay shows a balance of &#8377;50,000. The user switches to another app and returns. If the process survived, the in-memory balance may still be &#8377;50,000. If iOS terminated it, NPay must reconstruct its interface and retrieve or restore the right data.'),
                   ('ASK', 'If NPay was terminated while in the background, is its in-memory balance still there when the user returns?'),
                   ('EXPECT', 'No. A new process starts; the app must rebuild and fetch or restore its data.'),
                   ('CONNECT', 'Why would iOS keep a process around but stop it from running?'))))

# ================================================================== Part 5
divider(5, "Why does iOS suspend applications?", "Balancing responsiveness, battery and memory",
        "The operating system must balance responsiveness, battery consumption, memory and permitted background activity.", "Look at a device with several apps.")
apps = [("send", "Messaging", "Suspended", ''), ("eye", "Camera", "Running", 'lit'), ("app", "Shopping", "Suspended", ''), ("play", "Music", "Background audio", '')]
P = []
for i, (ic, t, st, cls) in enumerate(apps):
    P.append(tall(i * 290, 0, 266, 120, ic, t, st, None, cls))
S.append(slide("Part 5 &middot; Device workload &middot; illustrative", "Many apps, one device", f"""  <div class="body">
    {svg("0 0 1136 122", "Messaging suspended, camera running, shopping suspended, music playing background audio", "s13dev", P)}
    <div class="gap-lg"></div>
    <p>A <b>suspended</b> app stays resident in memory but <b>does not execute instructions</b>.</p>
    {points([("clock", "Saves energy", "CPU time and battery"), ("memory", "Keeps useful state", "still in memory"), ("play", "Faster return", "no rebuild needed"), ("phone", "Foreground first", "the system prioritizes it")], cls="p4", label="Why suspend")}
  </div>""", notes(('SAY', 'An illustrative device: messaging and shopping are suspended, the camera is running in front, and music continues as background audio.'),
                   ('SAY', 'When an app is suspended, its process can remain in memory but it does not execute instructions. That saves CPU time and energy, preserves useful state in memory, can make returning faster, and lets the system prioritize foreground work.'),
                   ('CONNECT', 'But music kept playing. How?'))))
S.append(slide("Part 5 &middot; Background capabilities", "What about music or navigation apps?", f"""  <div class="body">
    <div class="cols stretch">
      <div class="card accent step"><span class="label">Audio playback</span><p>Can continue in the background when the app is <b>properly configured</b> and follows the relevant audio rules.</p></div>
      <div class="card accent step"><span class="label">Navigation</span><p>May receive <b>background location updates</b> under appropriate permissions and conditions.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Not an exemption">These are specific <b>permitted capabilities</b>, not a general exemption to execute indefinitely.</div>
  </div>""", notes(('SAY', 'Some apps can do specific background work through supported iOS capabilities. Audio playback can continue when the app is properly configured and operating under the relevant audio rules. Navigation apps may receive background location updates under appropriate permissions and conditions.'),
                   ('SAY', 'These are permitted capabilities, not a general exemption that lets any app run forever.'),
                   ('CONNECT', 'Suspended apps also have a risk: the system may need their memory.'))))

# ================================================================== Part 6
divider(6, "Memory pressure", "Why iOS terminates apps",
        "Now the user opens a memory-intensive game. The system needs memory for the game, graphics resources and other active services.", "Watch what happens to the suspended apps.")
levels = [(35, "Low pressure", "The system has relatively little need to reclaim memory."),
          (65, "Rising pressure", "The game needs more memory; the system looks for resources to reclaim."),
          (90, "High pressure", "Suspended apps become candidates for termination so the system can reclaim memory.")]
P = ['<text class="mono" x="0" y="16">ILLUSTRATIVE MEMORY PRESSURE</text>',
     '<g class="nd"><rect class="sh" x="0" y="28" width="1136" height="40" rx="10"/></g>']
for i, (pct, t, d) in enumerate(levels):
    l = str(i) if i < 2 else '2+'
    cls = 'nd lit'
    P.append(f'<g class="fade" data-lit="{i}"><g class="{cls}"><rect class="sh" x="0" y="28" width="{1136 * pct // 100}" height="40" rx="10"/></g>'
             f'<text x="0" y="112" style="font-size:40px;font-weight:800">{pct}%</text><text x="110" y="100" style="font-size:22px;font-weight:700">{t}</text>'
             f'<text x="110" y="126" style="font-size:18px;font-weight:400">{d}</text></g>')
for i, (ic, t) in enumerate([("send", "Messaging"), ("app", "Shopping"), ("chip", "Game")]):
    x = i * 390
    if t == "Game":
        P.append(row(x, 160, 356, 64, ic, t, "in front, needs memory", "1+"))
    else:
        P.append(f'<g class="nd"><rect class="sh" x="{x}" y="160" width="356" height="64" rx="12"/><use href="#i-{ic}" x="{x + 14}" y="179" width="26" height="26"/><text x="{x + 52}" y="189">{t}</text>'
                 f'<text class="sm" x="{x + 52}" y="208">suspended</text></g>')
P.append('<g class="fade" data-lit="2"><g class="nd alert"><rect class="sh" x="0" y="160" width="746" height="64" rx="12"/><use href="#i-cross" x="14" y="179" width="26" height="26"/>'
         '<text x="52" y="189">Messaging and Shopping terminated</text><text class="sm" x="52" y="208">suspended apps ended to reclaim memory</text></g></g>')
S.append(slide("Part 6 &middot; Memory pressure &middot; illustrative", "When the system needs memory back", f"""  <div class="body">
    {svg("0 0 1136 226", "Memory pressure rises from 35 percent to 65 and 90 percent as a game runs; at high pressure the suspended messaging and shopping apps are terminated.", "s16mem", P)}
    {cues(2)}
    <div class="gap"></div>
    <p class="small muted">Teaching simulation, not an actual iPhone memory measurement or Apple&rsquo;s process-termination algorithm. The percentages are illustrative.</p>
  </div>""", notes(('SAY', 'At 35% the system has relatively little need to reclaim memory. Click: the game needs more. Click: under high pressure, suspended apps become candidates for termination so the system can reclaim resources.'),
                   ('SAY', 'This is a teaching simulation. The numbers are illustrative, not real measurements or Apple’s algorithm.'),
                   ('ASK', 'Which apps does the system reclaim memory from first in this picture?'),
                   ('EXPECT', 'The suspended ones, messaging and shopping, while the game in front keeps running.'),
                   ('CONNECT', 'The mechanism behind this has a name: jetsam.'))))
S.append(slide("Part 6 &middot; Jetsam", "What is a jetsam termination?", f"""  <div class="body">
    <p style="margin:0 0 20px">iOS uses memory-management mechanisms commonly called <b>jetsam</b> to terminate processes when it must manage memory pressure.</p>
    <div class="points v">
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-memory"/></svg><span><b>No resume first</b><small>A suspended app can be terminated without being resumed.</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-cross"/></svg><span><b>No final callback</b><small>The app cannot rely on a last cleanup call.</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-play"/></svg><span><b>Next launch rebuilds</b><small>State may need to be reconstructed.</small></span></div>
      <div class="step"><svg viewBox="0 0 24 24"><use href="#i-phone"/></svg><span><b>Foreground apps too</b><small>If their memory use becomes problematic.</small></span></div>
    </div>
    <div class="gap"></div>
    <div class="rule step">Persist important user data at <b>appropriate moments</b>, not when you expect termination.</div>
  </div>""", notes(('SAY', 'Four facts. A suspended app can be terminated without first being resumed. It cannot rely on a final cleanup callback. The next launch may need to reconstruct its state. And foreground apps can also be terminated if their memory use becomes problematic.'),
                   ('SAY', 'That is why we save important data as we go, not when we think the app is about to end.'),
                   ('CONNECT', 'So how do we design for this?'))))

# ================================================================== Part 7
divider(7, "How to design for termination", "Process memory is temporary",
        "A user fills out a long registration form, switches to another app, and later iOS terminates the app under memory pressure.", "What happens to the form?")
S.append(slide("Part 7 &middot; Design", "The registration form", """  <div class="body">
    <div class="cols stretch">
      <div class="card step"><span class="label">Poor design</span><p>Keep all form data <b>only in memory</b>.</p><p class="small muted" style="margin:0">Process termination makes unsaved progress disappear.</p></div>
      <div class="card accent step"><span class="label">Better design</span><p><b>Persist a draft</b> as the user makes progress.</p><p class="small muted" style="margin:0">A new process can recover the saved draft.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Principle"><b>Process memory is temporary.</b> Durable user data belongs in persistent storage.</div>
    <p class="small muted step" style="margin:14px 0 0">SwiftData, files and Keychain serve different purposes. Sensitive information needs protection; not every field belongs in plain preferences.</p>
  </div>""", notes(('SAY', 'The user has entered their name, address and more, then switched apps. Later iOS terminates the app under memory pressure. With the poor design, everything lived only in memory, so the progress is gone. With the better design, a draft was saved as they went, and the new process recovers it.'),
                   ('SAY', 'SwiftData, files, Keychain and other storage mechanisms serve different purposes. Sensitive information needs appropriate protection; not every field should go in plain preferences.'),
                   ('ASK', 'Where should the registration draft be saved: in memory, or in persistent storage?'),
                   ('EXPECT', 'Persistent storage, saved as the user goes. Process memory disappears with the process.'),
                   ('CONNECT', 'Finally, how do UIKit and SwiftUI let us observe all of this?'))))

# ================================================================== Part 8
divider(8, "SwiftUI versus UIKit lifecycle", "Two ways to define an app",
        "Historically UIKit apps used an app delegate; modern UIKit apps may also use a scene delegate. SwiftUI introduced a more declarative approach.", "Compare the two.")
UK = '''class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(_ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions:
            [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        true
    }
}'''
SU = '''@main
struct NPayApp: App {
    @Environment(\\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup { Text("NPay") }
            .onChange(of: scenePhase) { _, phase in
                print(phase)
            }
    }
}'''
S.append(slide("Part 8 &middot; App entry approaches", "UIKit vs SwiftUI", f"""  <div class="body top">
    <div class="cols stretch">
      <div class="card step"><span class="label">UIKit</span><h3 style="font-size:24px;margin:4px 0 10px">Delegate-driven approach</h3>
        <p class="small" style="margin:0">Historically <b>UIApplicationDelegate</b>; modern UIKit apps may also use <b>UISceneDelegate</b>.</p>
        <div class="gap"></div>
        {code("AppDelegate.swift", UK, "font-size:13.5px")}</div>
      <div class="card accent step"><span class="label">SwiftUI</span><h3 style="font-size:24px;margin:4px 0 10px">Declarative approach</h3>
        <p class="small" style="margin:0">Defines the application structure declaratively and <b>observes scene lifecycle changes</b>.</p>
        <div class="gap"></div>
        {code("NPayApp.swift", SU, "font-size:13.5px")}</div>
    </div>
  </div>""", notes(('SAY', 'On the left, the system calls the app delegate when launch finishes. On the right, the SwiftUI App declares a WindowGroup and reacts to scenePhase changes; there is no delegate to implement.'),
                   ('SAY', 'Historically, UIKit apps commonly used UIApplicationDelegate, and modern UIKit apps may also use UISceneDelegate: the system calls delegate methods as the app and its scenes change state. SwiftUI introduced a more declarative way to define application structure and observe scene lifecycle changes.'),
                   ('CONNECT', "Let's check your understanding."))))

# ================================================================== review (the text's trainer question)
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Commit to an answer before it is revealed.')) + "</section>\n\n")
q = "Can an app start a normal timer and assume it will fire every second after the app is suspended?"
S.append(f"""<section class="slide question" data-title="{E(q, quote=True)}">
  <div class="q-top">
    <p class="kicker">Check your understanding &middot; 1 of 1</p>
    <div class="q-dots" aria-hidden="true"><i class="now"></i></div>
  </div>
  <div class="body">
    <div class="q-row">
      <div class="q-card">
        <div class="q-icon"><svg viewBox="0 0 24 24"><use href="#i-clock"/></svg></div>
        <span class="label">Question</span>
        <p class="q-text">{q}</p>
      </div>
      <div class="q-panel">
        <div class="q-ans step anim-up">
          <span class="q-verdict">No</span>
          <p class="q-why">Once suspended, the app&rsquo;s ordinary code is not executing. Time-sensitive or background work needs a system-supported mechanism, subject to iOS policies.</p>
          <p class="q-trap"><b>Common trap:</b> Treating suspended like paused-but-ticking.</p>
        </div>
      </div>
    </div>
  </div>
""" + notes(('ASK', 'Give everyone a few seconds, then take a quick vote.'), ('EXPECT', 'Many say yes. A suspended app runs no code, so its timer does not fire.'),
            ('SAY', 'No. Once suspended, the app\u2019s ordinary code is not executing. Time-sensitive or background work needs an appropriate system-supported mechanism, and execution is subject to iOS policies.'),
            ('CONNECT', 'That wraps up the lifecycle.')) + "</section>\n\n")

# ================================================================== end
S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.3 complete</p>
    <h2>iOS Application<br>Lifecycle Deep Dive</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: SwiftUI app lifecycle vs UIKit AppDelegate</p>
  </div>
""" + notes(('SAY', 'Recap: a process is not a scene; scenes move between active, inactive and background, while the process runs, suspends or is terminated. Same tap, different work. Suspension saves resources; memory pressure can end suspended apps without warning. So persist important data as the user goes: process memory is temporary; never assume your process stays alive.'),
            ('SAY', 'Next, Lesson 0.4: how our Swift code finds out about these events, through SwiftUI\u2019s App lifecycle and UIKit\u2019s AppDelegate and SceneDelegate.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.3 — iOS Application Lifecycle Deep Dive</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.3 — iOS Application Lifecycle Deep Dive">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT03, "w").write(doc)
print(len(S), 'slides')
