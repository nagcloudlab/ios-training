"""Generates decks/unit-0/lesson-0.4/index.html from the Lesson 0.4 text only."""
import html, re, sys
OUT04 = sys.argv[1]
sys.argv = ['x', '/dev/null']
src = open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers: lit, tall, row, wire, head, svg, code, notes, slide, points, E

S = []
cues = lambda n: '<i class="step cue"></i>' * n


def divider(n, title, lead, say, con):
    S.append(f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(('SAY', say), ('CONNECT', con))}</section>

""")


def stages(items):
    return '<div class="points v stages">' + ''.join(
        f'<div class="step"><span class="q-num">{i + 1}</span><span><b>{t}</b><small>{d}</small></span></div>' for i, (t, d) in enumerate(items)) + '</div>'


# ------------------------------------------------------------------ title + outcomes
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.4</p>
    <h1 style="font-size:52px;line-height:1.05">SwiftUI App Lifecycle<br>vs UIKit AppDelegate</h1>
    <p class="lead" style="max-width:660px">iOS launches, suspends, resumes and terminates apps. <b>How does our Swift code know?</b></p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'We now understand how iOS launches, suspends, resumes and terminates applications. The next question: how does our Swift code know these events are happening? Historically developers used AppDelegate, then SceneDelegate. Modern SwiftUI apps usually use the App protocol and scene lifecycle APIs. We will understand all three, because professional iOS work means reading both modern and existing apps.'),
            ('CONNECT', "Here's what you'll be able to do by the end.")) + "</section>\n\n")
outs = [("clock", "Trace the <b>evolution</b>: AppDelegate, SceneDelegate, SwiftUI App"), ("bank", "Explain what an <b>AppDelegate</b> does"),
        ("phone", "Explain why each <b>scene</b> needs its own lifecycle"), ("code", "Read <b>scenePhase</b> in a <b>View</b> and in the <b>App</b>"),
        ("link", "Map UIKit <b>callbacks</b> to SwiftUI equivalents"), ("check", "Choose an approach for <b>new</b>, <b>existing</b> or <b>hybrid</b> apps")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.4 &middot; Outcomes", "By the end, you will be able to", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six outcomes, one question: how does our code hear about lifecycle events, in UIKit and in SwiftUI?'),
                 ('CONNECT', 'First, where this sits in NPay.'))))
# authored (Unit 00 audit): bridge from Lesson 0.3 on the shared NPay map
S.append(map_slide('0.4', 'Today: how your code hears lifecycle events', ('scene', 'view'),
                   'Lesson 0.3: one process can own several scenes; scene states are not process conditions.',
                   'The code that hears those changes: AppDelegate, SceneDelegate, and the SwiftUI <code>App</code> with <code>scenePhase</code>.',
                   'Lesson 0.3 showed what the system does to a process and its scenes. Today is the other side: how our Swift code is told. On the map, the Scene tile and the View: the SwiftUI view is where scenePhase is usually read.',
                   'Start with how we got here.'))

# ================================================================== Part 1
divider(1, "Evolution of iOS app architecture", "Three generations, still all in use",
        "Three approaches arrived over the years. You will meet all three in real code.", "Here they are in order.")
gens = [("bank", "UIKit + AppDelegate", "iOS 2+", "app-level lifecycle and application events"),
        ("phone", "UIKit + SceneDelegate", "iOS 13+", "scene-specific lifecycle, multiple windows"),
        ("code", "SwiftUI App lifecycle", "iOS 14+", "declarative app and scene definitions")]
P = []
for i, (ic, t, ver, sub) in enumerate(gens):
    x = i * 392
    P.append(f'<text class="mono" x="{x + 176}" y="16" text-anchor="middle">{ver}</text>')
    P.append(tall(x, 28, 352, 120, ic, t, sub, str(i + 1)))
    if i < 2:
        P.append(wire(f'M{x + 358} 88H{x + 386}{head(x + 386, 88, "r")}'))
S.append(slide("Part 1 &middot; Timeline", "From delegates to declarative", f"""  <div class="body">
    {svg("0 0 1136 150", "UIKit with AppDelegate from iOS 2, UIKit with SceneDelegate from iOS 13, SwiftUI App lifecycle from iOS 14", "s3gen", P)}
    {cues(3)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Not separate worlds">SwiftUI and UIKit can <b>interoperate</b>, and modern apps may combine them.</div>
  </div>""", notes(('SAY', 'Click by click. UIKit with AppDelegate, since iOS 2: app-level lifecycle and application events. UIKit with SceneDelegate, since iOS 13: scene-specific lifecycle, including multiple windows. The SwiftUI App lifecycle, since iOS 14: declarative app and scene definitions.'),
                  ('SAY', 'These are not completely separate. SwiftUI and UIKit interoperate, and modern apps may combine them.'),
                  ('CONNECT', 'Start with the oldest: the AppDelegate.'))))

# ================================================================== Part 2
divider(2, "Traditional UIKit: AppDelegate", "The system talks to a delegate",
        "In a traditional UIKit app, the operating system communicates application-level events through a delegate object.", "Here is the path a lifecycle event takes.")
P = []
flow = [("kernel", "iOS system", ""), ("bank", "AppDelegate", ""), ("code", "Application code", "")]
for i, (ic, t, _) in enumerate(flow):
    x = i * 420
    P.append(tall(x, 30, 296, 100, ic, t, '', str(i * 2 + 1) if i else "1"))
for i, (l1, l2) in enumerate([("lifecycle", "callback"), ("coordinate", "app services")]):
    x = 296 + i * 420
    P.append(f'<g>{wire(f"M{x + 6} 80H{x + 118}{head(x + 118, 80, chr(114))}", str(i * 2 + 2))}<text class="sm" x="{x + 62}" y="50" text-anchor="middle">{l1}</text><text class="sm" x="{x + 62}" y="66" text-anchor="middle">{l2}</text></g>')
AD = '''import UIKit

@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions:
            [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        print("Application launched")
        return true
    }
}'''
S.append(slide("Part 2 &middot; Delegate flow &middot; conceptual", "How the system reaches your code", f"""  <div class="body">
    {svg("0 0 1136 132", "The iOS system sends a lifecycle callback to the AppDelegate, which coordinates application services for the application code", "s5flow", P)}
    {cues(5)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="App-level events">The <b>AppDelegate</b> hears events about the <b>whole app process</b>: launch, push-notification registration, app-wide setup. Per-window events go to a scene (Part 3).</div>
  </div>""", notes(('SAY', 'Click through: the iOS system sends a lifecycle callback to the AppDelegate, and the AppDelegate coordinates application services for the rest of our code.'),
                  ('SAY', 'The AppDelegate hears events about the whole app process: launch, push-notification registration, app-wide setup. Events about one window go to a scene, which is Part 3.'),
                  ('CONNECT', 'Here is what that delegate looks like.'))))
S.append(slide("Part 2 &middot; AppDelegate", "A UIKit AppDelegate", f"""  <div class="body cols middle" style="grid-template-columns:1.25fr 1fr">
    {code("AppDelegate.swift", AD, "font-size:15px")}
    {stages([("<code>@main</code>", "identifies the application entry point"), ("<code>UIApplicationDelegate</code>", "AppDelegate conforms to it"),
             ("Callbacks", "UIKit invokes lifecycle-related delegate methods"), ("App-wide services", "the developer can initialize them here")])}
  </div>""", notes(('SAY', 'Four things. @main identifies the entry point. AppDelegate conforms to UIApplicationDelegate. UIKit invokes lifecycle-related delegate methods, here didFinishLaunching. And this is where developers initialize application-wide services.'),
                  ('SAY', 'But what happens when one app shows two windows at once?'),
                  ('CONNECT', 'That brings us to scenes.'))))

# ================================================================== Part 3
divider(3, "Why Apple introduced SceneDelegate", "One process, several windows",
        "Imagine an iPad app displaying two document windows.", "Look at the two windows.")
P = ['<g class="nd"><rect class="sh" x="0" y="0" width="560" height="300" rx="18"/><use href="#i-process" x="22" y="20" width="26" height="26"/><text x="58" y="40">One application process</text></g>',
     '<g class="nd" data-lit="1+"><rect class="sh" x="24" y="72" width="244" height="200" rx="14"/><use href="#i-file" x="132" y="96" width="28" height="28"/><text x="146" y="158" text-anchor="middle">Document A</text><text class="mono" x="146" y="230" text-anchor="middle">ACTIVE</text></g>',
     '<g class="nd"><rect class="sh" x="292" y="72" width="244" height="200" rx="14"/><use href="#i-file" x="400" y="96" width="28" height="28"/><text x="414" y="158" text-anchor="middle">Document B</text><text class="mono" x="414" y="230" text-anchor="middle">BACKGROUND</text></g>']
SD = '''import UIKit

class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?   // this scene's window

    func sceneDidBecomeActive(_ scene: UIScene)    { print("Active") }
    func sceneWillResignActive(_ scene: UIScene)   { print("Inactive") }
    func sceneDidEnterBackground(_ scene: UIScene) { print("Background") }
}'''
S.append(slide("Part 3 &middot; Multiple windows &middot; conceptual", "Two windows, two states", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {svg("0 0 560 302", "One iPad application process with two document windows: document A active, document B in the background", "s7ipad", P, "max-height:360px")}
    <div>
      <p style="font-size:24px;margin:0 0 18px">If one window becomes inactive, should the <b>whole app</b> become inactive?</p>
      <div class="rule step" data-label="No">Another scene may still be active. UIKit&rsquo;s scene architecture gives <b>each scene its own lifecycle</b>.</div>
    </div>
  </div>""", notes(('SAY', 'One application process, two document windows. Document A is active; document B is in the background.'),
                  ('ASK', 'If one window becomes inactive, should the entire application necessarily become inactive?'),
                  ('EXPECT', 'No. Another scene may still be active. That is why each scene needs its own lifecycle.'),
                  ('CONNECT', 'In UIKit, those per-scene events arrive at a SceneDelegate.'))))
S.append(slide("Part 3 &middot; SceneDelegate", "A UIKit SceneDelegate", f"""  <div class="body cols middle" style="grid-template-columns:1.5fr 1fr">
    {code("SceneDelegate.swift", SD, "font-size:14px")}
    <div>
      {stages([("<code>sceneDidBecomeActive</code>", "the scene is ready for interaction"), ("<code>sceneWillResignActive</code>", "the scene is about to become inactive"), ("<code>sceneDidEnterBackground</code>", "the scene is no longer visible")])}
      <div class="gap"></div>
      <div class="rule step" data-label="Required going forward">Apple is making the <b>scene life cycle</b> mandatory for UIKit apps (TN3187). An AppDelegate-only app is legacy code to migrate.</div>
    </div>
  </div>""", notes(('SAY', 'Each callback is about one scene, not the whole app: it became active, it is about to resign active, it entered the background. The window property belongs to that scene.'),
                  ('SAY', 'This shows the callbacks, not the complete configuration a traditional UIKit scene-based project requires.'),
                  ('SAY', 'Scenes are not optional extras. Apple Technical Note TN3187 says that, in the release following iOS 26, UIKit apps built with the latest SDK must adopt the scene-based life cycle. If you inherit an AppDelegate-only app, plan its migration. (Authored addition from the Unit 00 audit.)'),
                  ('CONNECT', 'Now the modern SwiftUI approach.'))))

# ================================================================== Part 4
divider(4, "Modern SwiftUI approach", "A declarative application structure",
        "SwiftUI provides a declarative application structure. Watch what disappears.", "Here is a whole SwiftUI app entry.")
APP = '''import SwiftUI

@main
struct NPayApp: App {

    var body: some Scene {
        WindowGroup {
            DashboardView()
        }
    }
}'''
S.append(slide("Part 4 &middot; SwiftUI App", "A SwiftUI app entry", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {code("NPayApp.swift", APP, "font-size:17px")}
    <div>
      <p class="small muted" style="margin:0 0 10px">Notice what is missing:</p>
      <div class="points v">
        <div class="step"><svg viewBox="0 0 24 24"><use href="#i-cross"/></svg><span><b>No AppDelegate</b><small>not explicitly defined</small></span></div>
        <div class="step"><svg viewBox="0 0 24 24"><use href="#i-cross"/></svg><span><b>No SceneDelegate</b><small>not explicitly defined</small></span></div>
        <div class="step"><svg viewBox="0 0 24 24"><use href="#i-cross"/></svg><span><b>No manual window creation</b><small>WindowGroup handles it</small></span></div>
      </div>
      <div class="gap"></div>
      <div class="rule step">SwiftUI and the system manage the normal <b>app and scene infrastructure</b>.</div>
    </div>
  </div>""", notes(('SAY', 'The whole entry point: an App with a body that returns a WindowGroup. Notice what is missing: no explicitly defined AppDelegate, no explicitly defined SceneDelegate, no manual window creation. SwiftUI and the underlying system manage the normal app and scene infrastructure.'),
                  ('CONNECT', 'So how does SwiftUI code hear about scene changes?'))))
CV = '''struct DashboardView: View {
    @Environment(\\.scenePhase) private var scenePhase

    var body: some View {
        Text("NPay Dashboard")
            .onChange(of: scenePhase) { _, phase in
                switch phase {
                case .active:     print("Active")
                case .inactive:   print("Inactive")
                case .background: print("Background")
                @unknown default: break
                }
            }
    }
}'''
S.append(slide("Part 4 &middot; scenePhase", "Observing scene changes", f"""  <div class="body cols middle" style="grid-template-columns:1.45fr 1fr">
    {code("DashboardView.swift", CV, "font-size:15px")}
    <div>
      {stages([("Read <code>scenePhase</code>", "from the environment"), ("<code>onChange</code>", "runs when the phase changes"), ("Switch on the phase", ".active, .inactive, .background")])}
      <div class="gap"></div>
      <div class="rule step">The <b>scenePhase</b> environment value lets SwiftUI code respond to scene lifecycle changes.</div>
    </div>
  </div>""", notes(('SAY', 'The view reads scenePhase from the environment and reacts with onChange. Each case maps to a scene state from Lesson 0.3. @unknown default keeps the switch safe if Apple adds a phase.'),
                  ('CONNECT', 'But which scene is this phase about? It depends where you read it.'))))
# authored (Unit 00 audit): 0.4 owns scenePhase, so explain App-level vs View-level reads
P = ['<g class="nd"><rect class="sh" x="0" y="0" width="560" height="318" rx="18"/><use href="#i-process" x="20" y="18" width="26" height="26"/><text x="56" y="37">NPay process (iPad)</text></g>',
     '<g class="nd" data-lit="1"><rect class="sh" x="24" y="64" width="244" height="150" rx="14"/><use href="#i-frame" x="132" y="82" width="28" height="28"/><text x="146" y="140" text-anchor="middle">Window A</text><text class="code" x="146" y="180" text-anchor="middle">View reads .active</text></g>',
     '<g class="nd" data-lit="2"><rect class="sh" x="292" y="64" width="244" height="150" rx="14"/><use href="#i-frame" x="400" y="82" width="28" height="28"/><text x="414" y="140" text-anchor="middle">Window B</text><text class="code" x="414" y="180" text-anchor="middle">View reads .background</text></g>',
     '<g class="nd" data-lit="3+"><rect class="sh" x="24" y="234" width="512" height="62" rx="14"/><use href="#i-code" x="40" y="252" width="26" height="26"/><text x="80" y="262">App reads .active</text><text class="sm" x="80" y="281">at least one scene is active</text></g>']
S.append(slide("Part 4 &middot; Where you read it", "scenePhase in a View vs in the App", f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    {svg("0 0 560 318", "One NPay process on iPad with two windows: a view in window A reads active, a view in window B reads background, and the App reads active because at least one scene is active", "s14where", P, "max-height:380px")}
    <div>
      {cues(3)}
      <table class="tbl" style="font-size:19px">
        <tr><th style="width:30%;white-space:nowrap">Read in</th><th>You get</th></tr>
        <tr><td style="white-space:nowrap">a <b>View</b></td><td>the phase of <b>that view&rsquo;s scene</b></td></tr>
        <tr><td style="white-space:nowrap">the <b>App</b></td><td><b>all scenes combined</b>: active if any scene is active; background only when every scene is in the background</td></tr>
      </table>
      <div class="gap"></div>
      <div class="rule step">Per-screen work (pause this screen&rsquo;s timer) belongs in the <b>View</b>; app-wide work (lock NPay when <b>every</b> window leaves) belongs in the <b>App</b>.</div>
    </div>
  </div>""", notes(('SAY', 'Click through. Window A is in front: a view inside it reads .active. Window B is in the background: a view inside it reads .background. The App reads the combined value: .active, because at least one scene is active. It only reports .background when every scene is in the background.'),
                  ('SAY', 'So per-screen reactions go in the view, and app-wide reactions, such as locking NPay when every window has left the screen, go in the App.'),
                  ('LIVE DEMO', 'App-level observer (typechecks, iOS 17+): <code>@main struct NPayApp: App { @Environment(\\.scenePhase) private var scenePhase; var body: some Scene { WindowGroup { DashboardView() }.onChange(of: scenePhase) { _, phase in if phase == .background { print("Every NPay scene is in the background") } } } }</code>. On an iPad simulator, open two NPay windows with Split View, send one to the background, and compare the App print with the per-view prints from the previous slide.'),
                  ('CONNECT', "Let's put UIKit and SwiftUI side by side."))))

# ================================================================== Part 5
divider(5, "Compare the approaches", "Same responsibilities, different tools",
        "The same responsibilities exist in both worlds; they are expressed differently.", "Six responsibilities side by side.")
S.append(slide("Part 5 &middot; Comparison", "UIKit delegates vs SwiftUI lifecycle", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Responsibility</th><th>UIKit delegates</th><th>SwiftUI lifecycle</th></tr>
      <tr><td>App entry</td><td>AppDelegate-based entry</td><td><code>@main</code> App</td></tr>
      <tr><td>UI creation</td><td>UIKit window and view controllers</td><td>WindowGroup and Views</td></tr>
      <tr class="hl"><td>Scene events</td><td>SceneDelegate callbacks</td><td><code>scenePhase</code></td></tr>
      <tr><td>UI layout</td><td>Auto Layout, frames, constraints</td><td>Declarative layout</td></tr>
      <tr><td>Navigation</td><td>UINavigationController</td><td>NavigationStack</td></tr>
      <tr><td>State updates</td><td>Explicit updates, observation</td><td>State-driven view updates</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Key distinction">AppDelegate and SceneDelegate are <b>lifecycle integration</b> mechanisms; SwiftUI is also a complete <b>UI framework</b>. Useful to compare, but not direct replacements for every UIKit feature.</div>
  </div>""", notes(('SAY', 'Six responsibilities. App entry: AppDelegate-based entry versus an @main App. UI creation: windows and view controllers versus WindowGroup and Views. Scene events: SceneDelegate callbacks versus scenePhase. Layout: Auto Layout, frames and constraints versus declarative layout. Navigation: UINavigationController versus NavigationStack. State: explicit updates versus state-driven view updates.'),
                  ('SAY', 'Key distinction: the delegates are lifecycle integration mechanisms, while SwiftUI is also a whole UI framework. The comparison helps teaching, but they are not one-to-one replacements.'),
                  ('CONNECT', 'Now event by event: what code actually runs?'))))

# ================================================================== Part 6
divider(6, "What code runs?", "One lifecycle event, two worlds",
        "Pick a lifecycle event and ask: what runs in UIKit, and what in SwiftUI?", "Five events, one per click.")
ev = [("App process launches", "application(_:didFinishLaunchingWithOptions:)", "the App is created; its body builds the scenes", "The process starts and the app sets itself up."),
      ("Scene becomes active", "sceneDidBecomeActive(_:)", "scenePhase becomes .active", "At launch the scene connects inactive, shows its first frame, then becomes active."),
      ("Scene becomes inactive", "sceneWillResignActive(_:)", "scenePhase becomes .inactive", "Still visible, temporarily not receiving events."),
      ("Scene enters background", "sceneDidEnterBackground(_:)", "scenePhase becomes .background", "No longer visible: save data and pause work."),
      ("Process terminated under pressure", "no callback is guaranteed", "no callback is guaranteed", "Persist important data earlier; the app may not get a last chance.")]
P = []
for i, (t, *_r) in enumerate(ev):
    P.append(row(i * 230, 0, 212, 56, '', ["Process launches", "Scene active", "Scene inactive", "Enters background", "Terminated"][i], '', str(i)))
for i, (t, uk, su, desc) in enumerate(ev):
    alert = i == 4
    P.append(f'<g class="fade" data-lit="{i}"><text class="mono" x="0" y="104">EVENT {i + 1} OF 5</text>'
             f'<text x="0" y="138" style="font-size:26px;font-weight:700">{t}</text>'
             f'<g class="nd"><rect class="sh" x="0" y="166" width="556" height="80" rx="12"/><text class="mono" x="20" y="194">UIKIT CALLBACK OR MECHANISM</text><text class="code" x="20" y="226" style="font-size:16px">{uk}</text></g>'
             f'<g class="nd{"" if alert else " lit"}"><rect class="sh" x="580" y="166" width="556" height="80" rx="12"/><text class="mono" x="600" y="194">SWIFTUI APPROACH</text><text class="code" x="600" y="226" style="font-size:16px">{su}</text></g>'
             f'<text x="0" y="284" style="font-size:19px;font-weight:400">{desc}</text></g>')
S.append(slide("Part 6 &middot; Event map &middot; conceptual", "Lifecycle event, UIKit vs SwiftUI", f"""  <div class="body">
    {svg("0 0 1136 292", "Five lifecycle events and what runs for each in UIKit and in SwiftUI", "s15ev", P)}
    {cues(4)}
  </div>""", notes(('SAY', 'Event two is the one from the text: when a scene becomes active, UIKit calls sceneDidBecomeActive and SwiftUI sets scenePhase to .active; the scene is ready for foreground interaction. Click through the others: launch, becoming inactive, entering the background, and termination under memory pressure.'),
                  ('SAY', 'The last one matters most: when iOS ends a suspended app under memory pressure, neither world gets a guaranteed callback. Persist data earlier.'),
                  ('CONNECT', 'Can a SwiftUI app still have an AppDelegate?'))))

# ================================================================== Part 7
divider(7, "Can SwiftUI still use AppDelegate?", "Yes, through an adaptor",
        "Yes. This matters for existing applications and certain system integrations.", "SwiftUI provides UIApplicationDelegateAdaptor.")
ADP = '''import SwiftUI

// AppDelegate: an ordinary class conforming to
// UIApplicationDelegate (no @main of its own)

@main
struct NPayApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self)
    var appDelegate

    var body: some Scene {
        WindowGroup { DashboardView() }
    }
}'''
S.append(slide("Part 7 &middot; Delegate adaptor", "UIApplicationDelegateAdaptor", f"""  <div class="body cols middle" style="grid-template-columns:1.45fr 1fr">
    {code("NPayApp.swift", ADP, "font-size:16px")}
    <div>
      {stages([("A plain AppDelegate", "conforms to UIApplicationDelegate"), ("<code>@UIApplicationDelegateAdaptor</code>", "SwiftUI creates it and forwards delegate calls"), ("The App stays SwiftUI", "WindowGroup and views as usual")])}
      <div class="gap"></div>
      <div class="rule step">A modern SwiftUI structure, plus <b>UIKit application delegate</b> functionality where it is needed.</div>
    </div>
  </div>""", notes(('SAY', 'The AppDelegate is an ordinary class conforming to UIApplicationDelegate. The App declares @UIApplicationDelegateAdaptor, and SwiftUI creates that delegate and forwards application delegate calls to it. Everything else stays SwiftUI.'),
                  ('SAY', 'This is how you keep a modern SwiftUI structure while integrating UIKit application delegate functionality that some system integrations require.'),
                  ('LIVE DEMO', 'Full file: <code>import SwiftUI</code> / <code>import UIKit</code>; <code>class AppDelegate: NSObject, UIApplicationDelegate { func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -&gt; Bool { print("Application initialized"); return true } }</code>; then the NPayApp on the slide. Run it and show "Application initialized" printing before the first scenePhase change.'),
                  ('CONNECT', 'So which approach should you choose?'))))

# ================================================================== Part 8
divider(8, "When should we use which?", "New, existing or hybrid",
        "The right choice depends on what you are working on.", "Three situations.")
P = ['<g class="nd solid"><rect class="sh" x="368" y="0" width="400" height="56" rx="12"/><text class="on" x="568" y="34" text-anchor="middle">What are you working on?</text></g>']
choices = [("app", "New application", "SwiftUI App lifecycle", ["Start here unless you have", "a specific reason not to.", "Add the delegate adaptor only", "when an integration needs it."]),
           ("bank", "Existing UIKit app", "AppDelegate + SceneDelegate", ["Maintain both delegates and", "view-controller lifecycles.", "Still AppDelegate-only?", "Migrate to scenes (TN3187)."]),
           ("layers", "Hybrid application", "Interoperability", ["SwiftUI and UIKit together,", "adapting the delegate", "where required.", "Unit 10 &middot; 10.3"])]
for i, (ic, t, sub, lines) in enumerate(choices):
    x = i * 392
    P.append(wire(f'M568 56V80H{x + 176}V104{head(x + 176, 104, "d")}'))
    P.append(tall(x, 110, 352, 110, ic, t, sub, f"{i + 1}+"))
    P.append(f'<g class="fade" data-lit="{i + 1}+">' + ''.join(f'<text class="sm" x="{x + 176}" y="{252 + k * 22}" text-anchor="middle" style="font-size:15px">{ln}</text>' for k, ln in enumerate(lines)) + '</g>')
S.append(slide("Part 8 &middot; Choosing", "Which approach, when?", f"""  <div class="body">
    {svg("0 0 1136 330", "Decision: a new application starts with the SwiftUI App lifecycle; an existing UIKit app maintains AppDelegate and SceneDelegate and migrates to scenes; a hybrid app uses interoperability", "s21choose", P)}
    {cues(3)}
  </div>""", notes(('SAY', 'New application: start with the SwiftUI App lifecycle unless there is a specific reason not to; add the delegate adaptor only where an integration needs it. Existing UIKit application: understand and maintain AppDelegate, SceneDelegate and view-controller lifecycle behavior, and if it is still AppDelegate-only, plan the move to scenes. Hybrid: use interoperability, adapting the delegate where required; Unit 10 covers interoperability in depth.'),
                  ('CONNECT', 'Before the review, one picture to remember.'))))

# authored (Unit 00 audit): recap on the shared map
S.append(recap_slide('0.4', ('scene', 'view'), [
    ("frame", "Each scene has its own lifecycle", "UIKit: SceneDelegate &middot; SwiftUI: scenePhase"),
    ("code", "Where you read scenePhase matters", "a View sees its scene; the App sees all"),
    ("cross", "No guaranteed last callback", "save as you go, not at termination")],
    'Three things to keep. Scenes have their own lifecycle, delivered by SceneDelegate in UIKit and scenePhase in SwiftUI. Where you read scenePhase decides which scene it describes. And termination gives no guaranteed final callback, so save as you go.'))

# ================================================================== review: the text's four questions (answers authored)
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions to check what stuck. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("bank", "Can a SwiftUI app still have an AppDelegate?", "Yes",
       "Through <code>@UIApplicationDelegateAdaptor</code>. SwiftUI creates the delegate and forwards application events to it.", "Assuming SwiftUI removed every reason for a delegate.",
       "Some say no. Some system integrations still need application delegate functionality."),
      ("frame", "NPay has two iPad windows: A is active, B is in the background. What does <code>scenePhase</code> read in the <code>App</code>?<br>A. <code>.background</code><br>B. <code>.inactive</code><br>C. <code>.active</code><br>D. whichever window opened first", "C",
       "In the App, scenePhase combines all scenes: active if any scene is active. A view in window B would read .background.", "Thinking the App-level value describes one particular window.",
       "Some pick A or D. Go back to the two-window picture from Part 4."),
      ("tap", "NPay is open with the Part 4 <code>DashboardView</code>. The user swipes up to the Home Screen. What prints?", "Inactive, then Background",
       "The scene resigns active first, then enters the background. scenePhase changes twice, so onChange runs twice.", "Expecting only &ldquo;Background&rdquo;, or a &ldquo;Suspended&rdquo; phase.",
       "Many say only Background."),
      ("layers", "Does <code>scenePhase</code> <code>.background</code> mean the app has been suspended?", "No",
       "Background is a scene state. Suspension is a process condition that may follow later, or not at all.", "Mixing scene states with process conditions.",
       "Spaced review from 0.3. Many say yes. Suspended is not a scenePhase value."),
      ("cross", "Will <code>applicationWillTerminate</code> always run before iOS kills an app?", "No",
       "A suspended app terminated under memory pressure gets no final callback. Persist important data earlier.", "Saving data only in a termination callback.",
       "Many say yes. Jetsam termination gives no warning.")]
N = len(QA)
# multiple choice: question, then the options on smaller lines
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
            ('CONNECT', 'Next question.' if i < N - 1 else 'Where these ideas go next in the course.')) + "</section>\n\n")

# authored (Unit 00 audit): where this goes next + lab
S.append(next_slide('0.4', [
    ("3.1", "View identity, lifetime &amp; state reset", "a view&rsquo;s lifetime is not its scene&rsquo;s"),
    ("6.9", "Drafts &amp; state restoration", "save before background; restore per scene"),
    ("10.1", "UIKit lifecycle &amp; responder chain", "AppDelegate, SceneDelegate, view controllers"),
    ("10.3", "SwiftUI&ndash;UIKit interoperability", "hybrid apps and the delegate adaptor"),
    ("10.7", "BackgroundTasks &amp; execution limits", "what may run after the scene leaves")],
    'Today was the foundation. In Unit 03 you meet view identity, which is a different lifetime from the scene. Unit 06 saves drafts and restores state per scene. Unit 10 goes deep on UIKit lifecycles, interoperability, and the background work iOS allows after a scene leaves the screen.'))
S.append(lab_slide('0.4', 'Map the lifecycle events', 'For five NPay moments, write what each world calls. Work on paper or in a table.', [
    'Draw four columns: <b>Event</b> &middot; <b>AppDelegate</b> &middot; <b>SceneDelegate</b> &middot; <b>SwiftUI</b>.',
    'Rows: NPay launches &middot; a second NPay window opens on iPad &middot; the user pulls down Notification Center &middot; the user goes to the Home Screen &middot; iOS terminates the suspended app.',
    'Fill each cell with the callback or <code>scenePhase</code> change. Write <b>none</b> where nothing is called.',
    'For each row, add what NPay should do, for example save a half-typed transfer.'],
    'The completed table, with one NPay action per row.',
    'Five moments, four columns. Fill in what each world calls, and write none where nothing is called. Then add what NPay should do at each moment. Compare with a neighbour before we check. Answer key: (1) Launch: AppDelegate application(_:didFinishLaunchingWithOptions:); SceneDelegate scene(_:willConnectTo:options:), then sceneDidBecomeActive; SwiftUI: the App is created, WindowGroup builds the scene, scenePhase becomes .active. (2) Second window: AppDelegate application(_:configurationForConnecting:options:); SceneDelegate scene(_:willConnectTo:options:) for the new scene; SwiftUI: WindowGroup creates another window whose views have their own scenePhase. (3) Notification Center: sceneWillResignActive; scenePhase .inactive; nothing at app level. (4) Home Screen: sceneWillResignActive then sceneDidEnterBackground; scenePhase .inactive then .background. (5) Terminated while suspended: none, in every column. NPay actions: e.g. save a draft transfer on background, hide the balance when inactive.'))

# ================================================================== end
S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.4 complete</p>
    <h2>SwiftUI App Lifecycle<br>vs UIKit AppDelegate</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.5 &mdash; Main Thread, RunLoop &amp; Event Handling</p>
  </div>
""" + notes(('SAY', 'You can now explain why modern iOS apps use SwiftUI’s declarative lifecycle, why UIKit delegate APIs still matter, and how scene-level events differ from application-process events.'),
            ('SAY', 'Next, Lesson 0.5: we trace a single button tap from the touchscreen through iOS event delivery, the main thread, SwiftUI state changes and screen rendering. That prepares us for Swift concurrency and performance engineering.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.4 — SwiftUI App Lifecycle vs UIKit AppDelegate</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.4 — SwiftUI App Lifecycle vs UIKit AppDelegate">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT04, 'w').write(doc)
print(len(S), 'slides')
