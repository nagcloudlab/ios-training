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

# ------------------------------------------------------------------ outcomes
outs = [("process", "Tell an app <b>process</b> from a <b>scene</b>"), ("layers", "Name the <b>scene states</b> and the <b>process conditions</b>"),
        ("play", "Explain <b>cold launch</b> versus <b>warm activation</b>"), ("clock", "Say why iOS <b>suspends</b> apps, and what may still run"),
        ("memory", "Explain <b>memory pressure</b> and jetsam termination"), ("check", "Design NPay so <b>termination</b> loses nothing important")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.3 &middot; Outcomes", "By the end, you will be able to", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six outcomes. Together they answer the opening question: what happens to NPay when the user leaves it, and when the user comes back.'),
                 ('CONNECT', 'First, where today sits on the NPay map.'))))

S.append(map_slide('0.3', 'Today: the process and its scenes', ('scene', 'springboard', 'sandbox'),
                   'Lesson 0.2: inside the process, the View, ViewModel, Service and Model each have one job.',
                   'What happens to NPay&rsquo;s process and its scene when the user leaves, and when the user comes back.',
                   'Same map as last time. In Lesson 0.2 we looked inside the process at who does what. Today we look at the process as a whole, the dashed box, and at its scene, and at how SpringBoard and iOS move them between states.',
                   'We start with the most important distinction.'))

# ================================================================== Part 1
divider(1, "Process versus scene", "The most important distinction",
        "Two words people use interchangeably, but iOS treats very differently.", "Start with a picture: back to the hotel from Lesson 0.1.")

# hotel analogy (the unit's platform analogy, from Lesson 0.1): NPay's suite = the process, its rooms = scenes
P = ['<g class="nd ghost" data-lit="1"><rect class="sh" x="10" y="34" width="540" height="390" rx="18"/></g>',
     '<g class="nd" data-lit="1"><use href="#i-building" x="10" y="0" width="24" height="24"/><text class="mono" x="42" y="18">HOTEL MANAGEMENT: THE OPERATING SYSTEM</text></g>',
     '<g class="nd" data-lit="2"><rect class="sh" x="36" y="60" width="488" height="300" rx="14"/><text class="mono" x="56" y="88">NPAY&#8217;S SUITE: THE APP PROCESS</text></g>']
for i, (x, y, name) in enumerate([(60, 104, "Room A"), (296, 104, "Room B"), (60, 230, "Room C"), (296, 230, "Room D")]):
    P.append(f'<g class="nd" data-lit="3"><rect class="sh" x="{x}" y="{y}" width="204" height="106" rx="12"/><use href="#i-frame" x="{x + 89}" y="{y + 18}" width="26" height="26"/><text x="{x + 102}" y="{y + 72}" text-anchor="middle">{name}</text><text class="sm" x="{x + 102}" y="{y + 92}" text-anchor="middle">a scene</text></g>')
P.append('<g class="fade" data-lit="4"><use href="#i-user" x="246" y="380" width="30" height="30" style="color:var(--teal)"/><text class="sm" x="284" y="400">the guest moves between rooms</text></g>')
art = svg("0 0 560 430", "A hotel: hotel management is the operating system, NPay's suite is the app process, each room of the suite is a scene, and the guest moves between rooms.", "s3hotel", P, "max-height:470px")
rows = [("building", "Hotel management", "the operating system"), ("process", "NPay&rsquo;s suite", "the app process: one per app"),
        ("frame", "Each room of the suite", "a scene, with its own lights on or off"), ("user", "The guest", "the user, moving between rooms")]
lst = "\n".join(f'        <div class="step"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg><span><b>{t}</b><small>{d}</small></span></div>' for i, t, d in rows)
S.append(slide("Part 1 &middot; Analogy", "NPay&rsquo;s suite in the hotel", f"""  <div class="body cols middle" style="grid-template-columns:1.15fr 1fr">
    {art}
    <div>
      <div class="points v">
{lst}
      </div>
      <div class="gap"></div>
      <p class="step">One suite can have several rooms. One app process can manage <b>multiple scenes</b>.</p>
    </div>
  </div>""", notes(('SAY', 'In Lesson 0.1 the iPhone was a hotel, iOS the hotel management and NPay one guest\u2019s space. Zoom in: NPay\u2019s space is a suite. The suite is the application process. Each room of the suite is a scene, and each room has its own lights: on, dimmed or off. The guest is the user, moving between rooms.'),
                 ('SAY', 'One suite can have several rooms. Similarly, one iOS app process can manage multiple scenes, and their lights change independently.'),
                 ('CONNECT', "Now the same idea in iOS terms."))))

# process vs scene diagram
P = ['<g class="nd" data-lit="1"><rect class="sh" x="0" y="0" width="560" height="330" rx="18"/><use href="#i-process" x="22" y="20" width="26" height="26"/>'
     '<text x="58" y="34">App process</text><text class="sm" x="58" y="54">shared executable code, memory, threads and services</text></g>',
     '<g class="nd lit" data-lit="2+"><rect class="sh" x="24" y="90" width="244" height="210" rx="14"/><use href="#i-phone" x="132" y="112" width="28" height="28"/>'
     '<text x="146" y="176" text-anchor="middle">Scene A</text><text class="sm" x="146" y="198" text-anchor="middle">NPay accounts</text></g>',
     '<g class="fade" data-lit="2+"><text class="mono" x="146" y="262" text-anchor="middle">ACTIVE</text></g>',
     '<g class="nd"><rect class="sh" x="292" y="90" width="244" height="210" rx="14"/><use href="#i-phone" x="400" y="112" width="28" height="28"/>'
     '<text x="414" y="176" text-anchor="middle">Scene B</text><text class="sm" x="414" y="198" text-anchor="middle">NPay statement</text></g>',
     '<g class="fade" data-lit="2+"><text class="mono" x="414" y="262" text-anchor="middle">BACKGROUND</text></g>']
art = svg("0 0 560 332", "One NPay process containing two scenes: scene A, accounts, is active; scene B, the statement, is in the background.", "s4ps", P, "max-height:360px")
S.append(slide("Part 1 &middot; Process vs scene &middot; conceptual", "One process, several scenes", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    <div>
      {art}
      {cues(2)}
      <p class="small muted" style="margin:10px 0 0">Conceptual multiwindow example, most relevant on iPadOS; an iPhone app commonly has one main window scene. Apple is making the scene-based lifecycle required for apps built with SDKs after iOS 26 (TN3187).</p>
    </div>
    <div>
      {points([("process", "Process", "a running instance of your app: its execution environment"), ("phone", "Scene", "an instance of your app&rsquo;s UI that the system manages, with its own lifecycle states")], cls="v", box="card accent", step=False)}
      <div class="gap"></div>
      <div class="rule step" data-label="Critical point">One scene can be in the <b>background</b> while another scene of the same app is <b>active</b>. Scene lifecycle and process state are not the same.</div>
    </div>
  </div>""", notes(('SAY', 'A process is a running instance of your application; it contains the execution environment. A scene represents an instance of your app’s UI that the system manages, and scenes have their own lifecycle states.'),
                   ('SAY', 'Click two: on an iPad, scene A, NPay\u2019s accounts window, is active while scene B, a statement window, is in the background. Same process, different scene states.'),
                   ('SAY', 'Multiple simultaneous windows matter most on iPadOS; an ordinary iPhone app commonly has one main window scene. Either way, the scene is the unit iOS manages for UI. Apple\u2019s technote TN3187 says apps built with SDKs released after iOS 26 must adopt the scene-based lifecycle, so treat scenes as standard, not optional.'),
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
                   ('SAY', 'Suspended is not a scenePhase value. Students often look for it there; it belongs to the process. Lesson 0.4 shows how SwiftUI code reads scenePhase.'),
                   ('CONNECT', 'Now put them together for a typical single-scene iPhone app.'))))

top = [("cross", "Not running", "no app process exists"), ("clock", "Inactive", "launching: first frame drawn"), ("play", "Active", "foreground, accepting interaction")]
bot = [("clock", "Inactive", "leaving: not accepting events"), ("layers", "Background", "no longer foreground"),
       ("memory", "Suspended", "kept in memory, not executing"), ("cross", "Terminated", "process no longer exists")]
P = []
for i, (ic, t, sub) in enumerate(top):
    x = i * 398
    P.append(tall(x, 0, 340, 104, ic, t, sub, str(i + 1)))
    if i < 2:
        P.append(wire(f'M{x + 346} 52H{x + 392}{head(x + 392, 52, "r")}'))
for i, (ic, t, sub) in enumerate(bot):
    x = i * 292
    P.append(tall(x, 164, 260, 104, ic, t, sub, str(i + 4), 'alert' if t == 'Terminated' else ''))
    if i < 3:
        P.append(wire(f'M{x + 264} 216H{x + 286}{head(x + 286, 216, "r")}'))
P.append(wire(f'M966 104V134H130V158{head(130, 158, "d")}'))
S.append(slide("Part 2 &middot; Lifecycle &middot; conceptual", "A typical single-scene iPhone app", f"""  <div class="body">
    {svg("0 0 1136 270", "Launch: not running, inactive while the first frame is drawn, then active. Leaving: inactive, background, suspended, and possibly terminated.", "s6states", P)}
    {cues(7)}
    <div class="gap"></div>
    <p class="small muted">One possible progression, not a mandatory sequence. An app may return to the foreground, be terminated directly, or follow other transitions.</p>
  </div>""", notes(('SAY', 'Click through the top row, the launch: not running, no process exists. Then inactive: the process has started and its scene is connected and draws its first frame, but is not yet accepting events. Then active: in the foreground, accepting interaction.'),
                   ('SAY', 'Bottom row, leaving: inactive again, still visible but not accepting events, for example while the user swipes up. Background: no longer in the foreground; execution may continue briefly. Suspended: the process is kept in memory but not executing. Terminated: the process no longer exists.'),
                   ('SAY', 'This is one possible path, not a required sequence. An app can come back to the foreground, be terminated directly, or take other transitions.'),
                   ('ASK', 'On launch, is NPay already active when its first frame appears?'),
                   ('EXPECT', 'No. The scene is inactive while the first frame is drawn; it becomes active after that.'),
                   ('CONNECT', "Let's walk through it with NPay."))))

# ================================================================== Part 3
divider(3, "Let&rsquo;s simulate the app lifecycle", "One banking app, five moments",
        "Imagine using NPay, our banking app. We will watch its scene and its process change.", "Five scenarios, one per click.")
sc = [("App not running", "No scene", "Not running", "Tap the NPay icon",
       "NPay is installed, but there is no running process. The system launches it; its scene connects, draws its first frame, then becomes active."),
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
        "The user performs the same action, tapping the app icon, but iOS may perform different internal work.", "Imagine opening NPay in three different situations.")
kinds = [("Cold", "New process", "Application initialization must happen again."),
         ("Warm", "Existing process", "Application state may already be in memory."),
         ("Running", "Existing running process", "The app can become foreground without being resumed from suspension.")]
cards = "\n".join(f'      <div class="card{" accent" if i == 2 else ""} step"><span class="label">{k}</span><h3 style="font-size:22px;margin:4px 0 8px">{t}</h3><p class="small" style="margin:0">{d}</p></div>' for i, (k, t, d) in enumerate(kinds))
S.append(slide("Part 4 &middot; Three cases", "One tap, three possible situations", f"""  <div class="body">
    <div class="cols c3 stretch">
{cards}
    </div>
    <div class="gap"></div>
    <p class="small muted step">Cold, warm and hot launch are often used informally; their precise meanings vary by tool. Not every launch starts with a tap: a notification or a link can also launch NPay (Unit 10: 10.6, 10.8).</p>
  </div>""", notes(('SAY', 'For teaching, the clearest distinction: a new process means initialization must happen again. An existing process means application state may already be in memory. An existing running process can become foreground without being resumed from suspension.'),
                   ('SAY', 'The running case: the app is still executing eligible background work. The user brings it forward, the scene transitions through lifecycle states, and foreground interaction resumes, with no process creation or suspension recovery.'),
                   ('SAY', 'Developers use cold, warm and hot launch informally, and the exact meanings vary by tool. Focus on the process distinction rather than the labels.'),
                   ('SAY', 'And a launch does not always start with a tap on the icon. Tapping a notification or a link can launch NPay too; Unit 10 covers notifications (10.6) and deep links (10.8).'),
                   ('CONNECT', 'Why does this matter to us? A banking example.'))))
P = [row(388, 0, 360, 62, "user", "Balance shows &#8377;25,000", "the user switches apps, then returns"),
     wire(f'M568 62V86H190V112{head(190, 112, "d")}M568 86H946V112{head(946, 112, "d")}'),
     row(0, 118, 380, 78, "check", "Process survived", "in-memory balance may still be &#8377;25,000", "1+"),
     row(756, 118, 380, 78, "cross", "Process terminated", "rebuild the interface, retrieve or restore data", "2", "alert")]
S.append(slide("Part 4 &middot; Example &middot; conceptual", "Coming back to NPay", f"""  <div class="body">
    {svg("0 0 1136 200", "The user switches away from NPay showing 25,000 rupees and returns; if the process survived the balance may still be in memory, if it was terminated the app must rebuild and restore.", "s11ex", P)}
    {cues(2)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Architectural rule">Never design an iOS application assuming that its <b>process will remain alive</b>.</div>
  </div>""", notes(('SAY', 'NPay shows a balance of &#8377;25,000. The user switches to another app and returns. If the process survived, the in-memory balance may still be &#8377;25,000. If iOS terminated it, NPay must reconstruct its interface and retrieve or restore the right data.'),
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
    <div class="rule step" data-label="Not an exemption">These are specific <b>permitted capabilities</b>, not a general exemption to execute indefinitely. Scheduled work uses <b>BackgroundTasks</b>: Unit 10 (10.7).</div>
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
        "A user fills out NPay&rsquo;s long account-opening form, switches to another app, and later iOS terminates NPay under memory pressure.", "What happens to the form?")
S.append(slide("Part 7 &middot; Design", "The account-opening form", """  <div class="body">
    <div class="cols stretch">
      <div class="card step"><span class="label">Poor design</span><p>Keep all form data <b>only in memory</b>.</p><p class="small muted" style="margin:0">Process termination makes unsaved progress disappear.</p></div>
      <div class="card accent step"><span class="label">Better design</span><p><b>Persist a draft</b> as the user makes progress.</p><p class="small muted" style="margin:0">A new process can recover the saved draft.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Principle"><b>Process memory is temporary.</b> Durable user data belongs in persistent storage.</div>
    <p class="small muted step" style="margin:14px 0 0">SwiftData, files and Keychain serve different purposes, and sensitive fields need protection (Lesson 0.9). Drafts and state restoration in depth: Unit 06 (6.9).</p>
  </div>""", notes(('SAY', 'The user has entered their name, address and more in NPay\u2019s account-opening form, then switched apps. Later iOS terminates the app under memory pressure. With the poor design, everything lived only in memory, so the progress is gone. With the better design, a draft was saved as they went, and the new process recovers it.'),
                   ('SAY', 'SwiftData, files, Keychain and other storage mechanisms serve different purposes; Lesson 0.9 compares them. Sensitive information needs appropriate protection; not every field should go in plain preferences. Unit 06 (6.9) builds drafts and state restoration properly.'),
                   ('ASK', 'Where should the registration draft be saved: in memory, or in persistent storage?'),
                   ('EXPECT', 'Persistent storage, saved as the user goes. Process memory disappears with the process.'),
                   ('CONNECT', 'Before the review, a recap.'))))

# ================================================================== wrap-up (authored per the Unit 00 audit)
# The text's Part 8 (SwiftUI vs UIKit lifecycle) is not repeated here: Lesson 0.4 owns it (and the text was truncated there).
S.append(recap_slide('0.3', ('scene', 'springboard', 'sandbox'),
                     [("process", "Process is not scene", "scenes change state; the process runs, suspends or ends"),
                      ("memory", "Suspended can become terminated", "with no warning and no final callback"),
                      ("check", "Process memory is temporary", "save what matters as the user goes")],
                     'Three things to keep. A scene and a process are different things with different states. A suspended app can be terminated without warning or a final callback. So process memory is temporary: persist what matters as the user goes.'))

S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions. Commit to an answer before it is revealed.')) + "</section>\n\n")

OPT = lambda *o: '<span style="display:block;font-size:22px;line-height:1.5;margin-top:14px">' + '<br>'.join(f'{chr(65 + k)}. {x}' for k, x in enumerate(o)) + '</span>'
QA = [("clock", "Can an app start a normal timer and assume it will fire every second after the app is suspended?", "",
       "No", "Once suspended, the app&rsquo;s ordinary code is not executing. Time-sensitive or background work needs a system-supported mechanism, subject to iOS policies.",
       "Treating suspended like paused-but-ticking.", "Many say yes. A suspended app runs no code, so its timer does not fire."),
      ("phone", "Can one NPay scene be in the background while another NPay scene is active?", "",
       "Yes", "Scene states are per scene; the process is shared. On an iPad, two NPay windows can be in different states.",
       "Treating the whole app as one on/off switch.", "Some say no, thinking of the app as a single state."),
      ("layers", "Which of these is a SwiftUI <code>scenePhase</code> value?", OPT("suspended", "terminated", "inactive", "not running"),
       "C", "scenePhase reports active, inactive and background. Suspended, terminated and not running describe the process, not the scene.",
       "Looking for suspended in scenePhase.", "A and B are common picks. They are process conditions."),
      ("memory", "NPay is suspended and the system needs memory. What can happen?", OPT("iOS resumes NPay so it can save, then ends it", "iOS ends NPay&rsquo;s process without running more of its code", "iOS moves NPay&rsquo;s scene to inactive", "iOS waits for NPay to finish its work"),
       "B", "A suspended app can be terminated without being resumed and without a final callback. That is why NPay saves as it goes.",
       "Counting on a last chance to save.", "A is the popular wrong answer: there is no final callback to rely on."),
      ("layout", "NPay was terminated, and the user taps its icon again. Which component reloads the balance for the screen?", OPT("The View, inside <code>body</code>", "The ViewModel, through the Service", "iOS, from the old process", "The Model, by itself"),
       "B", "A new process starts empty. The ViewModel asks the Service for the balance again; the view only shows the result.",
       "Expecting the old process memory to come back.", "Spaced review from 0.2. Some pick C; the old process and its memory are gone.")]
N = len(QA)
for i, (ic, q, opts, v, why, trap, exp) in enumerate(QA):
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
        {qhtml(q + opts)}
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
            ('CONNECT', 'Next question.' if i < N - 1 else 'Where does this go next in the course?')) + "</section>\n\n")

S.append(next_slide('0.3', [("0.4", "SwiftUI App lifecycle vs UIKit delegates", "how your code observes these states"),
                            ("6.9", "Drafts &amp; state restoration", "saving progress before termination"),
                            ("8.8", "Memory, ARC &amp; energy optimization", "staying small under memory pressure"),
                            ("10.7", "BackgroundTasks &amp; execution limits", "permitted background work"),
                            ("10.8", "Deep links &amp; universal links", "launches that do not start with a tap")],
                    'Next lesson shows how SwiftUI and UIKit code find out about these state changes. Later units build on today: drafts and state restoration in Unit 06, memory and energy in Unit 08, and background tasks and deep links in Unit 10.'))

EVENTS = ["NPay is not running; the user taps its icon", "The balance screen is showing", "The user pulls down Control Center",
          "The user swipes up to the Home Screen", "A little later, NPay is doing no work", "The user opens a large game", "The user taps NPay again"]
S.append(lab_slide('0.3', 'Predict NPay&rsquo;s state', 'For each event, predict NPay&rsquo;s <b>scene state</b> and its <b>process condition</b>.',
                   ['Write two columns: scene state, process condition.', 'Fill in one row per event card.', 'Mark any row where the answer is &ldquo;it depends&rdquo;, and say on what.', 'Compare with a partner.'],
                   '', 'Answers. 1: the process starts; the scene is inactive while the first frame is drawn, then active. 2: active, running. 3: inactive, running. 4: background, running briefly. 5: background, suspended. 6: it depends: under memory pressure NPay may be terminated (no scene, no process). 7: if it was terminated, a cold launch with a fresh process; if not, a warm return from suspension, the scene inactive then active.',
                   side='<div class="card accent"><span class="label">Event cards</span><ol style="margin:6px 0 0;padding-left:24px">' + ''.join(f'<li style="font-size:18px;margin-bottom:6px">{e}</li>' for e in EVENTS) + '</ol></div>'))

# ================================================================== end
S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.3 complete</p>
    <h2>iOS Application<br>Lifecycle Deep Dive</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.4 &mdash; SwiftUI App Lifecycle vs UIKit AppDelegate</p>
  </div>
""" + notes(('SAY', 'Recap: a process is not a scene; scenes move between active, inactive and background, while the process runs, suspends or is terminated. Same tap, different work. Suspension saves resources; memory pressure can end suspended apps without warning. So persist important data as the user goes: process memory is temporary; never assume your process stays alive.'),
            ('SAY', 'Next, Lesson 0.4: how our Swift code finds out about these events, through SwiftUI’s App lifecycle and UIKit’s AppDelegate and SceneDelegate.')) + "</section>\n\n")

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
