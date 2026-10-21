"""Generates decks/lesson-0.7/index.html from the Lesson 0.7 text only (PocketBank -> NPay)."""
import html, re, sys
OUT07 = sys.argv[1]
sys.argv = ['x', '/dev/null']
src = open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)), 'gen02.py')).read()
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


def vflow(items, w=560, h=58, gap=26, lit_from=1):
    P = []
    for i, (ic, t, sub) in enumerate(items):
        y = i * (h + gap)
        P.append(box(0, y, w, h, t, sub, str(i + lit_from), '', ic))
        if i < len(items) - 1:
            P.append(wire(f'M{w / 2:g} {y + h}V{y + h + gap - 6}{head(w / 2, y + h + gap - 6, "d")}'))
    return P, len(items) * (h + gap) - gap


S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Lesson 0.7</p>
    <h1 style="font-size:54px;line-height:1.05">iOS Security<br>Architecture</h1>
    <p class="lead" style="max-width:680px">Thousands of apps run on an iPhone. How does iOS stop one app from stealing another app&rsquo;s data?</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'If thousands of applications run on an iPhone, how does iOS prevent one from stealing another’s data? We continue with NPay, our banking app, and explore the iOS security architecture.'),
            ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")
outs = [("shield", "Explain <b>least privilege</b> and why apps need isolation"), ("layers", "Describe iOS security as <b>layers</b> that work together"),
        ("lock", "Explain the <b>sandbox</b> and authorized data sharing"), ("key", "Tell <b>entitlements</b> from <b>privacy permissions</b>"),
        ("file", "Explain what <b>code signing</b> does, and does not, guarantee"), ("chip", "Choose <b>Keychain</b> for secrets; place the <b>Secure Enclave</b>")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.7 &middot; Outcomes", "By the end, you will be able to", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six outcomes, one question: how does iOS keep apps from reaching what they are not authorized to use?'),
                 ('CONNECT', 'Start with the problem itself.'))))

# ================================================================== 1
divider(1, "The security problem", "Many developers, one device",
        "An iPhone runs apps written by many different developers. Not every app can be trusted equally, so the operating system must provide isolation.", "Picture three apps on one phone.")
P = ['<g class="nd ghost"><rect class="sh" x="0" y="0" width="1136" height="190" rx="18"/></g>',
     '<text class="mono" x="20" y="28">iOS ENFORCES SECURITY BOUNDARIES</text>']
for i, (ic, t, sub) in enumerate([("bank", "NPay", "bank data"), ("frame", "PhotoGallery", "private photos"), ("app", "ShopEasy", "orders")]):
    x = 40 + i * 362
    P.append(tall(x, 50, 330, 116, ic, t, sub, '1' if i == 0 else None))
    P.append(fade("1+", f'<use href="#i-lock" x="{x + 296}" y="58" width="24" height="24" style="color:var(--teal)"/>'))
S.append(slide("Part 1 &middot; Isolation &middot; conceptual", "Three apps on one iPhone", f"""  <div class="body">
    {svg("0 0 1136 192", "NPay with bank data, PhotoGallery with private photos and ShopEasy with orders, each inside its own security boundary", "s4apps", P)}
    {cues(1)}
    <div class="gap"></div>
    <ul class="small" style="columns:3;column-gap:28px;margin:0">
      <li>Can ShopEasy directly read NPay&rsquo;s private files?</li>
      <li>Can NPay secretly activate the camera?</li>
      <li>Can a malicious app replace another app&rsquo;s executable?</li>
    </ul>
    <div class="gap"></div>
    <div class="rule step" data-label="Least privilege">Apps should only access the resources they are <b>authorized</b> to use.</div>
  </div>""", notes(('SAY', 'A user has three apps: NPay with banking information, PhotoGallery with personal photographs, and ShopEasy for shopping. Can ShopEasy read NPay’s private files? Can NPay secretly turn on the camera? Can a malicious app replace another app’s executable? The rest of the lesson answers these.'),
                  ('SAY', 'The first principle: applications should only access resources they are authorized to use. That is the principle of least privilege.'),
                  ('ASK', 'What would you guess for each of the three questions?'),
                  ('EXPECT', 'Collect guesses. The answers come part by part: no, no, and no, each for a different reason.'),
                  ('CONNECT', 'iOS answers them with several layers of protection.'))))

# ================================================================== 2
divider(2, "The big picture", "Security in layers",
        "Security is not one library or one permission dialog. iOS uses multiple layers of protection.", "Here are the layers.")
layers = [("code", "Application security", "secure coding, authentication, data handling"), ("eye", "Privacy &amp; permissions", "camera, microphone, photos, location"),
          ("lock", "Sandbox &amp; entitlements", "filesystem boundaries, approved capabilities"), ("file", "Code signing &amp; runtime protections", "code integrity, platform enforcement"),
          ("chip", "Kernel &amp; hardware security", "process isolation, memory protection, Secure Enclave")]
P = [box(0, i * 70, 600, 58, t, sub, str(i + 1), 'solid' if i == 4 else '', ic) for i, (ic, t, sub) in enumerate(layers)]
S.append(slide("Part 2 &middot; Layers &middot; conceptual", "iOS security architecture", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    <div>
      {svg("0 0 600 340", "Application security, privacy and permissions, sandbox and entitlements, code signing and runtime protections, kernel and hardware security", "s6lay", P, "max-height:380px")}
      <p class="small muted" style="margin:8px 0 0">Conceptual. The layers overlap and work together, not in a strict top-to-bottom sequence.</p>
    </div>
    <div>
      {cues(5)}
      <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div>
        <p>An international <b>airport</b> has identity checks, boarding passes, restricted areas and screening. Passing <b>one checkpoint</b> does not open everything.</p></div>
      <div class="gap"></div>
      <div class="rule step">A <b>signed</b> app cannot automatically use <b>every device capability</b>.</div>
    </div>
  </div>""", notes(('SAY', 'Click through the layers: application security, privacy and permissions, sandbox and entitlements, code signing and runtime protections, and kernel and hardware security. These are conceptual; the mechanisms overlap and work together.'),
                  ('SAY', 'Think of an airport: identity checks, boarding passes, restricted areas, security screening, protected infrastructure. Passing one checkpoint does not grant access to everything. Likewise, a signed app does not get every device capability.'),
                  ('CONNECT', 'Start with the boundary every app lives inside: the sandbox.'))))

# ================================================================== 3
divider(3, "The App Sandbox", "Each app in its own container",
        "The sandbox restricts what an application process can access.", "Watch ShopEasy try three things.")
att = [("Its own private files", "Normally allowed", "ShopEasy can access its own container, subject to filesystem and data-protection rules.", ''),
       ("NPay’s private files directly", "Blocked", "The sandbox stops one app browsing another app’s private container.", 'alert'),
       ("A document shared with it", "Allowed, through the system", "The user shares a document through an approved system interface, so access is authorized.", 'lit')]
P = [box(0, 0, 330, 70, "NPay", "private app container", None, '', 'bank'), box(806, 0, 330, 70, "ShopEasy", "private app container", None, '', 'app')]
for i, (t, *_r) in enumerate(att):
    P.append(box(i * 380, 100, 356, 52, t, '', str(i)))
for i, (t, res, d, cls) in enumerate(att):
    arrow = {0: wire(f'M970 70V88{head(970, 88, "d")}'), 1: wire(f'M806 35H336{head(336, 35, "l")}', None, 'dash'), 2: ''}[i]
    P.append(fade(str(i) if i < 2 else "2+", arrow + f'<text class="mono" x="0" y="196">SHOPEASY ATTEMPTS: {t.upper()}</text>'
                  + box(0, 210, 1136, 62, res, d, None, cls or 'lit')))
S.append(slide("Part 3 &middot; Sandbox &middot; conceptual", "Explore application isolation", f"""  <div class="body">
    {svg("0 0 1136 274", "ShopEasy can read its own container, is blocked from reading NPay's private files directly, and can open a document shared through an approved system interface", "s8sand", P)}
    {cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="Authorized, not never">Apps can still exchange data through <b>App Groups</b>, extensions, document pickers and system-mediated services.</div>
  </div>""", notes(('SAY', 'Each app normally has its own private data container. Click through what ShopEasy tries: its own files, allowed; NPay’s private files directly, blocked; a document the user shares through an approved system interface, allowed because the system mediates it.'),
                  ('SAY', 'The sandbox does not mean apps can never exchange data. App Groups, extensions, document pickers and system-mediated services allow controlled communication. The important word is authorized.'),
                  ('CONNECT', 'How does an app get approved capabilities like an App Group? Entitlements.'))))

# ================================================================== 4
divider(4, "Entitlements", "Signed declarations of capability",
        "An entitlement is a signed declaration of a capability granted to an app, for example access to an App Group or certain Apple services.", "Here is how it flows.")
P = []
for i, (ic, t, sub) in enumerate([("bank", "NPay application", ""), ("key", "Signed entitlements", ""), ("shield", "System-enforced capabilities", "")]):
    x = i * 392
    P.append(tall(x, 0, 352, 96, ic, t, '', str(i + 1)))
    if i < 2:
        P.append(wire(f'M{x + 358} 48H{x + 386}{head(x + 386, 48, "r")}'))
S.append(slide("Part 4 &middot; Entitlements &middot; conceptual", "From declaration to enforcement", f"""  <div class="body">
    {svg("0 0 1136 98", "NPay application, signed entitlements, system-enforced capabilities", "s10ent", P)}
    {cues(3)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Not a runtime switch">An entitlement is not a boolean an app sets at runtime. It must be <b>configured</b>, <b>signed</b> and <b>accepted</b> by the platform.</div>
  </div>""", notes(('SAY', 'NPay declares a capability, such as an App Group. It is part of the signed entitlements, and the system enforces it.'),
                  ('SAY', 'An entitlement is not something an app can switch on at runtime to grab any privilege. The capability must be configured, signed and accepted by the platform.'),
                  ('CONNECT', 'Entitlements are often confused with permissions. Compare them.'))))
S.append(slide("Part 4 &middot; Comparison", "Entitlements vs privacy permissions", """  <div class="body top">
    <table class="tbl" style="font-size:20px">
      <tr><th>Entitlement</th><th>Privacy permission</th></tr>
      <tr><td>Declares an app capability</td><td>Authorizes access to privacy-sensitive resources</td></tr>
      <tr><td>Usually configured at build or signing time</td><td>Often involves user choice at runtime</td></tr>
      <tr><td>Example: App Groups</td><td>Example: camera access</td></tr>
      <tr><td>Enforced by platform services</td><td>Enforced by privacy and system APIs</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step">Some capabilities also require runtime authorization. These mechanisms can <b>work together</b>.</div>
  </div>""", notes(('SAY', 'An entitlement declares a capability, is usually configured at build or signing time, and is enforced by platform services; App Groups is an example. A privacy permission authorizes access to privacy-sensitive resources, often involves a user choice at runtime, and is enforced by privacy and system APIs; camera access is an example.'),
                  ('CONNECT', 'Let’s follow a privacy permission: NPay and the camera.'))))

# ================================================================== 5
divider(5, "NPay requests the camera", "Privacy permission in action",
        "NPay supports scanning a cheque, so it needs camera access.", "Follow the authorization flow.")
flow = [("tap", "User taps Scan Cheque", ""), ("eye", "NPay requests camera authorization", ""), ("phone", "System permission prompt", "")]
P = []
for i, (ic, t, _s) in enumerate(flow):
    x = i * 392
    P.append(box(x, 0, 352, 62, t, '', None, '', ic))
    if i < 2:
        P.append(wire(f'M{x + 358} 31H{x + 386}{head(x + 386, 31, "r")}'))
states = [("Not determined", "No decision has been made yet.", ''), ("Allow", "Camera authorized: NPay can scan the cheque.", 'lit'),
          ("Don&rsquo;t Allow", "Camera denied: NPay must offer another way to continue.", 'alert')]
for i, (t, *_r) in enumerate(states):
    P.append(box(i * 380, 100, 356, 52, t, '', str(i)))
for i, (t, d, cls) in enumerate(states):
    P.append(fade(str(i) if i < 2 else "2+", f'<text class="mono" x="0" y="196">CAMERA PERMISSION</text>' + box(0, 210, 1136, 62, t, d, None, cls)))
S.append(slide("Part 5 &middot; Camera authorization &middot; conceptual", "Scanning a cheque", f"""  <div class="body">
    {svg("0 0 1136 274", "The user taps Scan Cheque, NPay requests camera authorization, the system prompts; the state is not determined, allowed or denied", "s13cam", P)}
    {cues(2)}
    <div class="gap"></div>
    <p class="small">Add a privacy usage description such as <code>NSCameraUsageDescription</code>, and explain <b>why</b> before the system prompt appears.</p>
  </div>""", notes(('SAY', 'The user taps Scan Cheque; NPay requests camera authorization; the system shows its prompt. Until the user decides, the state is not determined. Click: Allow, and NPay can use the camera. Click: Don’t Allow, and NPay must offer another way to continue.'),
                  ('SAY', 'A real app also needs the privacy usage description, such as NSCameraUsageDescription, in its configuration. The user should understand why access is requested before the system prompt appears.'),
                  ('ASK', 'Can NPay secretly activate the camera, as we asked at the start?'),
                  ('EXPECT', 'No. Camera access goes through the system’s privacy authorization, with the user’s choice.'),
                  ('CONNECT', 'Now the third question: can a malicious app replace another app’s executable?'))))

# ================================================================== 6
divider(6, "Code signing", "Why iOS trusts the executable",
        "Imagine a malicious app tries to modify NPay’s executable. How does iOS protect code integrity? One major mechanism is code signing.", "Follow it from build to execution.")
items = [("code", "Developer builds the app", "compiler and linker produce executable code"), ("file", "The app is signed", "signature and metadata protect code integrity"),
         ("shield", "iOS validates execution requirements", "platform policies and code-signing checks apply"), ("lock", "The app runs under restrictions", "signing does not bypass sandbox or privacy controls")]
P, h = vflow(items, w=600, h=58, gap=24)
S.append(slide("Part 6 &middot; Code signing &middot; conceptual", "From build to trusted execution", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {svg(f"0 0 600 {h}", "The developer builds the app, it is signed, iOS validates execution requirements, and the app runs under restrictions", "s16sig", P, "max-height:380px")}
    <div>
      {cues(4)}
      <div class="rule step" data-label="Identity, not safety">A valid signature establishes code <b>identity</b> and <b>integrity</b>. It is not proof that the app&rsquo;s logic is <b>secure</b>.</div>
    </div>
  </div>""", notes(('SAY', 'Click through: the developer builds the app; the app is signed, with a signature and metadata protecting its integrity; iOS validates execution requirements through platform policies and signing checks; and the app runs under restrictions. Signing does not bypass the sandbox or privacy controls.'),
                  ('ASK', 'Does a valid code signature guarantee the app has no security vulnerabilities?'),
                  ('EXPECT', 'No. Signing establishes identity and integrity under platform policy. It says nothing about whether the app’s logic is secure.'),
                  ('CONNECT', 'Inside a secure app: where should secrets live?'))))

# ================================================================== 7
divider(7, "Keychain", "Where sensitive secrets live",
        "After login, NPay receives an authentication token. Where should it store it?", "Compare the two common options.")
S.append(slide("Part 7 &middot; Storage choice", "UserDefaults vs Keychain", """  <div class="body">
    <div class="cols stretch">
      <div class="card step"><span class="label">UserDefaults</span><p>Application <b>preferences</b> and lightweight settings.</p><p class="small muted" style="margin:0">Examples: selected theme, onboarding completed.</p></div>
      <div class="card accent step"><span class="label">Keychain</span><p>Sensitive <b>credentials</b> and small secret values.</p><p class="small muted" style="margin:0">Examples: authentication tokens, cryptographic key references.</p></div>
    </div>
    <div class="gap"></div>
    <div class="rule step" data-label="Accessibility policies">Keychain items control <b>when</b> data can be accessed. A <b>WhenUnlocked</b> class is intended for use while the device is unlocked. Choose by security and background-access needs.</div>
  </div>""", notes(('SAY', 'UserDefaults is for preferences and lightweight settings like the selected theme or whether onboarding is done. Storing sensitive credentials there is generally inappropriate. The Keychain is for credentials and small secrets: authentication tokens and cryptographic key references.'),
                  ('SAY', 'Keychain items support accessibility policies. An item with a WhenUnlocked class is intended to be accessible while the device is unlocked. The right policy depends on the app’s security and background-access requirements.'),
                  ('CONNECT', 'Some keys get even stronger, hardware-backed protection.'))))

# ================================================================== 8
divider(8, "The Secure Enclave", "Hardware-backed security",
        "The Secure Enclave is a hardware-based security subsystem on supported Apple devices.", "See where it sits.")
items = [("app", "Application process", ""), ("frameworks", "Security frameworks and services", "Keychain, LocalAuthentication, CryptoKit and Security APIs"),
         ("chip", "Secure Enclave", "protected key operations and security functions")]
P, h = vflow(items, w=600, h=64, gap=30)
P[-1] = box(0, 2 * 94, 600, 64, "Secure Enclave", "protected key operations and security functions", '3', 'solid', 'chip')
S.append(slide("Part 8 &middot; Secure Enclave &middot; conceptual", "Isolated security operations", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {svg(f"0 0 600 {h}", "The application process uses security frameworks such as Keychain, LocalAuthentication and CryptoKit, which use the Secure Enclave for protected key operations", "s19se", P, "max-height:360px")}
    <div>
      {cues(3)}
      <p>It provides <b>isolated</b> security operations and helps protect certain cryptographic keys.</p>
      <div class="rule step" data-label="Critical distinction">Not every Keychain item is stored inside the Secure Enclave. It supports particular operations and key types; it is not a general-purpose database.</div>
    </div>
  </div>""", notes(('SAY', 'Click down the stack: the app process calls security frameworks and services such as Keychain, LocalAuthentication, CryptoKit and the Security APIs; those use the Secure Enclave for protected key operations.'),
                  ('SAY', 'A critical distinction: not every Keychain item lives in the Secure Enclave. It supports particular operations and key types and is not a general-purpose database for app data.'),
                  ('CONNECT', 'Let’s put it all together in one NPay login.'))))

# ================================================================== 9
divider(9, "Putting it together", "An NPay login, end to end",
        "Follow a secure login at a conceptual level.", "Five steps.")
steps = [("bank", "User opens NPay", "the signed app runs inside its sandbox"), ("user", "User authenticates", "authenticated HTTPS to the backend"),
         ("globe", "Backend returns a token", "the app validates the response"), ("key", "Token is stored securely", "Keychain accessibility and access controls"),
         ("clock", "User returns later", "the app retrieves credentials when appropriate")]
P, h = vflow(steps, w=640, h=54, gap=18)
S.append(slide("Part 9 &middot; Secure login &middot; conceptual", "A secure NPay login", f"""  <div class="body cols middle" style="grid-template-columns:1.15fr 1fr">
    {svg(f"0 0 640 {h}", "Open the signed sandboxed app, authenticate over HTTPS, receive and validate a token, store it in the Keychain, retrieve it later", "s22log", P, "max-height:400px")}
    <div>
      {cues(5)}
      <p class="small step">Only one part of secure banking. Production systems also need <b>backend authorization</b>, token lifecycle management, secure sessions, fraud controls, logging policies and <b>threat modeling</b>.</p>
    </div>
  </div>""", notes(('SAY', 'Click through: the user opens NPay, a signed app running in its sandbox; the user authenticates over authenticated HTTPS; the backend returns a token, which the app validates; the token is stored with appropriate Keychain accessibility and access controls; later, the app retrieves the credentials when appropriate.'),
                  ('SAY', 'This is only one part of a secure banking architecture. Backend authorization, token lifecycle, session handling, fraud controls, logging policy and threat modeling all matter too.'),
                  ('CONNECT', "Let's check your understanding."))))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Four questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("lock", "Can one iOS app directly read another app&rsquo;s private container?", "Normally no",
       "The sandbox keeps each app in its own container. Sharing goes through authorized mechanisms.", "Assuming files on the same device are visible to every app.", "Most say no; ask how authorized sharing works."),
      ("file", "Does code signing mean an app is free of vulnerabilities?", "No",
       "Signing establishes code identity and integrity. It is not proof the app&rsquo;s logic is secure.", "Treating a signature as a security audit.", "Some say yes."),
      ("key", "Where should an authentication token generally be stored: UserDefaults, the Keychain, or a hardcoded constant?", "Keychain",
       "It is designed for credentials and small secrets, with accessibility policies. UserDefaults and constants are not.", "Storing tokens in UserDefaults for convenience.", "Most get this; ask why not UserDefaults."),
      ("chip", "Is every Keychain item stored inside the Secure Enclave?", "No",
       "The Secure Enclave supports particular operations and key types. It is not a general-purpose store.", "Assuming Keychain and Secure Enclave are the same thing.", "Many say yes.")]
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
    <p class="kicker">Lesson 0.7 complete</p>
    <h2>iOS Security<br>Architecture</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Least privilege, enforced at every layer.</p>
  </div>
""" + notes(('SAY', 'Recap: apps get only what they are authorized to use. Security comes in layers: app security, privacy permissions, sandbox and entitlements, code signing, and kernel and hardware protection. The sandbox isolates containers; entitlements and permissions grant specific capabilities; signing proves identity and integrity, not safety; secrets go in the Keychain; and the Secure Enclave protects particular keys.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.7 — iOS Security Architecture</title>
<link rel="stylesheet" href="../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.7 — iOS Security Architecture">
<div class="deck">

{''.join(S)}</div>
<script src="../../shared/art.js"></script>
<script src="../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT07, 'w').write(doc)
print(len(S), 'slides')
