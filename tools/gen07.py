"""Generates decks/unit-0/lesson-0.7/index.html from the Lesson 0.7 text only (PocketBank -> NPay)."""
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
        ("file", "Explain what <b>code signing</b> does, and does not, guarantee"), ("chip", "Choose the <b>Keychain</b> for secrets; explain what the <b>Secure Enclave</b> protects")]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide("Lesson 0.7 &middot; Outcomes", "By the end, you will be able to", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six outcomes, one question: how does iOS keep apps from reaching what they are not authorized to use?'),
                 ('CONNECT', 'First, where this lesson sits on the NPay map.'))))
S.append(map_slide('0.7', 'Today: the walls around NPay', ('sandbox', 'keychain', 'kernel', 'hardware'),
                   'Lesson 0.6: ARC frees an object when its last strong reference goes; a retain cycle keeps it alive.',
                   'The boundaries iOS puts around NPay: the sandbox, code signing, the Keychain and the Secure Enclave.',
                   'Last time we looked inside NPay&rsquo;s memory. Today we step outside the process and look at the walls around it: the sandbox around the whole process, the kernel that enforces it and checks code signatures, the Keychain that holds secrets, and the hardware Secure Enclave underneath.',
                   'Start with the problem itself.'))

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
        <p>Back to the <b>hotel</b> from Lesson 0.1: the front desk checks who you are, your <b>room key</b> opens only your room, and valuables go in the <b>in-room safe</b>. Passing <b>one check</b> does not open every door.</p></div>
      <div class="gap"></div>
      <div class="rule step">A <b>signed</b> app cannot automatically use <b>every device capability</b>.</div>
    </div>
  </div>""", notes(('SAY', 'Click through the layers: application security, privacy and permissions, sandbox and entitlements, code signing and runtime protections, and kernel and hardware security. These are conceptual; the mechanisms overlap and work together.'),
                  ('SAY', 'Back to the hotel from Lesson 0.1. The front desk checks who you are, your room key opens only your room, and valuables go in the in-room safe. Passing one check does not open every door. In iOS terms: the sandbox is the room, signing and entitlements are the key, and the Keychain is the safe. Likewise, a signed app does not get every device capability.'),
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
    <p class="small muted" style="margin:10px 0 0">Widgets and other extensions run as <b>separate sandboxed processes</b>; they share data with the app through an App Group (Unit 10 &middot; 10.9).</p>
  </div>""", notes(('SAY', 'Each app normally has its own private data container. Click through what ShopEasy tries: its own files, allowed; NPay’s private files directly, blocked; a document the user shares through an approved system interface, allowed because the system mediates it.'),
                  ('SAY', 'The sandbox does not mean apps can never exchange data. App Groups, extensions, document pickers and system-mediated services allow controlled communication. The important word is authorized.'),
                  ('SAY', 'One more boundary to know about: a widget or other extension is not part of the app process. It runs as its own sandboxed process and shares data with the app through an App Group. Unit 10, lesson 10.9, builds one.'),
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
lanes = [("ENTITLEMENT &middot; SET AT BUILD AND SIGNING TIME", "1", [("gear", "Configure the capability", "in the project"), ("file", "Signed into NPay", "part of the signature"), ("shield", "Platform services enforce", "e.g. App Groups")]),
         ("PRIVACY PERMISSION &middot; DECIDED AT RUN TIME", "2+", [("eye", "NPay asks", "with a usage description"), ("user", "The user chooses", "Allow or Don&rsquo;t Allow"), ("lock", "Privacy APIs enforce", "e.g. the camera")])]
P = []
for r, (lab, l, items) in enumerate(lanes):
    y = r * 130
    P.append(f'<text class="mono" x="0" y="{y + 14}">{lab}</text>')
    for i, (ic, t, sub) in enumerate(items):
        x = i * 392
        P.append(box(x, y + 28, 352, 70, t, sub, l, '', ic))
        if i < 2:
            P.append(wire(f'M{x + 358} {y + 63}H{x + 386}{head(x + 386, y + 63, "r")}'))
S.append(slide("Part 4 &middot; Comparison", "Entitlements vs privacy permissions", f"""  <div class="body">
    {svg("0 0 1136 228", "An entitlement is configured, signed into the app and enforced by platform services, for example App Groups. A privacy permission is requested by the app, chosen by the user at run time and enforced by privacy APIs, for example the camera", "s11cmp", P)}
    {cues(2)}
    <div class="gap"></div>
    <div class="rule step">Some capabilities need <b>both</b>: an entitlement in the signature and the user&rsquo;s permission at run time.</div>
  </div>""", notes(('SAY', 'Top lane, an entitlement: it declares an app capability, is configured at build or signing time, becomes part of the signature, and is enforced by platform services. App Groups is an example.'),
                  ('SAY', 'Bottom lane, a privacy permission: it authorizes access to a privacy-sensitive resource. The app asks, the user chooses at run time, and privacy and system APIs enforce the choice. The camera is an example.'),
                  ('SAY', 'Some capabilities need both mechanisms working together.'),
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
          ("Don&rsquo;t Allow", "Camera denied: NPay cannot ask again. Offer another way to continue and a link to Settings.", 'alert')]
for i, (t, *_r) in enumerate(states):
    P.append(box(i * 380, 100, 356, 52, t, '', str(i)))
for i, (t, d, cls) in enumerate(states):
    P.append(fade(str(i) if i < 2 else "2+", f'<text class="mono" x="0" y="196">CAMERA PERMISSION</text>' + box(0, 210, 1136, 62, t, d, None, cls)))
S.append(slide("Part 5 &middot; Camera authorization &middot; conceptual", "Scanning a cheque", f"""  <div class="body">
    {svg("0 0 1136 274", "The user taps Scan Cheque, NPay requests camera authorization, the system prompts; the state is not determined, allowed or denied", "s13cam", P)}
    {cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="Usage description">Without <code>NSCameraUsageDescription</code> in Info.plist, the app is <b>terminated</b> when it asks for the camera. Explain <b>why</b> before the prompt appears.</div>
  </div>""", notes(('SAY', 'The user taps Scan Cheque; NPay requests camera authorization; the system shows its prompt. Until the user decides, the state is not determined. Click: Allow, and NPay can use the camera. Click: Don’t Allow. The system shows its prompt only once, so NPay cannot ask again: it must offer another way to continue, such as uploading a photo, and can only direct the user to Settings to change the decision.'),
                  ('SAY', 'The app must also declare a privacy usage description, NSCameraUsageDescription, in Info.plist. If it is missing, iOS terminates the app the moment it asks for the camera. The user should understand why access is requested before the system prompt appears. Later, the privacy manifest declares what data the app collects; Unit 11, lesson 11.8, covers it.'),
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
P = ['<rect class="wire dash" x="0" y="0" width="540" height="176" rx="16"/>',
     '<text class="mono" x="20" y="30">NPAY&rsquo;S CONTAINER &middot; SANDBOX</text>',
     tall(30, 50, 480, 100, "file", "UserDefaults", "a preferences file: theme, onboarding done", "1"),
     '<text class="mono" x="620" y="30">MANAGED BY IOS</text>',
     tall(620, 50, 516, 100, "key", "Keychain", "an encrypted database: tokens, key references", "2+")]
S.append(slide("Part 7 &middot; Storage choice &middot; conceptual", "UserDefaults vs Keychain", f"""  <div class="body">
    {svg("0 0 1136 178", "UserDefaults is a preferences file inside NPay's sandbox container; the Keychain is an encrypted database managed by iOS", "s17kc", P)}
    {cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="The token goes in the Keychain">UserDefaults is a plain <b>preferences file</b>: never put a token there. Keychain items also choose <b>when</b> they can be read, e.g. only while the device is <b>unlocked</b>.</div>
  </div>""", notes(('ASK', 'After sign-in, NPay has a token. Where should it go: UserDefaults or the Keychain?'),
                  ('EXPECT', 'Most say the Keychain; ask why not UserDefaults.'),
                  ('SAY', 'Click: UserDefaults is for preferences and lightweight settings, such as the selected theme or whether onboarding is done. It is stored as a preferences file inside NPay’s container, so it is not a place for credentials.'),
                  ('SAY', 'Click: the Keychain is a database managed by iOS, outside the app’s container, that encrypts each item. It is designed for credentials and small secrets: authentication tokens and cryptographic key references.'),
                  ('SAY', 'Keychain items also carry an accessibility policy, for example an item intended to be readable only while the device is unlocked. The right policy depends on the app’s security and background-access needs; Unit 07, lesson 7.3, goes deeper.'),
                  ('CONNECT', 'Who protects the keys that encrypt the Keychain? Hardware.'))))

# ================================================================== 8
divider(8, "The Secure Enclave", "Hardware-backed security",
        "The Secure Enclave is a hardware-based security subsystem on supported Apple devices.", "See where it sits.")
P = [box(0, 0, 600, 56, "Application process", "NPay", "1", '', "app"),
     wire(f'M300 56V78{head(300, 78, "d")}'),
     box(0, 84, 600, 64, "Security frameworks", "Keychain services, CryptoKit, LocalAuthentication", "2", '', "frameworks"),
     wire(f'M150 148V178{head(150, 178, "d")}'), wire(f'M450 148V178{head(450, 178, "d")}'),
     tall(0, 184, 290, 100, "db", "Keychain database", "encrypted items", "3"),
     tall(310, 184, 290, 100, "chip", "Secure Enclave", "protects keys; holds P-256 keys", "4+", "solid"),
     wire('M292 260H308', None, 'dash')]
S.append(slide("Part 8 &middot; Secure Enclave &middot; conceptual", "Isolated security operations", f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {svg("0 0 600 286", "NPay calls security frameworks; Keychain items live in an encrypted database; the Secure Enclave protects the keys that encrypt them and can hold P-256 private keys", "s19se", P, "max-height:380px")}
    <div>
      {cues(4)}
      <div class="rule step" data-label="Critical distinction">Keychain items are <b>not</b> stored in the Secure Enclave. It protects the <b>keys</b> that encrypt them, and can create <b>P-256 private keys</b> that never leave it.</div>
    </div>
  </div>""", notes(('SAY', 'Click down: NPay calls the security frameworks, such as Keychain services, CryptoKit and LocalAuthentication.'),
                  ('SAY', 'Click: the Keychain items themselves live in an encrypted database. Click: the Secure Enclave is a separate hardware subsystem. It protects the keys used to encrypt Keychain items, and it can create P-256 private keys that never leave it; the app asks the Enclave to sign or decrypt with them.'),
                  ('SAY', 'The critical distinction: Keychain items are not stored inside the Secure Enclave. It is not a general-purpose database. Unit 07, lesson 7.5, uses it from CryptoKit.'),
                  ('CONNECT', 'How the token gets there in the first place, signing in over the network, is the start of Lesson 0.8. First, a recap.'))))

# ================================================================== wrap-up
S.append(recap_slide('0.7', ('sandbox', 'keychain', 'kernel', 'hardware'),
                     [("lock", "Sandbox", "each app in its own container; sharing must be authorized"),
                      ("file", "Signing", "identity and integrity, not proof of safety"),
                      ("key", "Keychain", "secrets, encrypted with keys the Secure Enclave protects")],
                     'Least privilege at every layer. The sandbox keeps NPay in its own container, enforced by the kernel. Entitlements and permissions grant specific capabilities. Signing proves identity and integrity, not safety. Secrets go in the Keychain, whose keys the Secure Enclave protects.'))

# ================================================================== review
S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', 'Five questions. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")
QA = [("lock", "ShopEasy needs a statement PDF that NPay created. Which route works?<br>A) Read NPay&rsquo;s container path directly<br>B) Request the camera permission<br>C) The user shares it with the share sheet or a document picker<br>D) Re-sign ShopEasy with NPay&rsquo;s certificate", "C",
       "The sandbox blocks direct access. Sharing goes through system-mediated routes the user controls.", "Assuming files on the same device are visible to every app.", "Some pick A or D; ask what the sandbox and signing each protect."),
      ("file", "Does code signing mean an app is free of vulnerabilities?", "No",
       "Signing establishes code identity and integrity. It is not proof the app&rsquo;s logic is secure.", "Treating a signature as a security audit.", "Some say yes."),
      ("key", "After sign-in, where should NPay keep its authentication token?<br>A) The Keychain<br>B) UserDefaults<br>C) A hardcoded constant<br>D) A file in Documents", "A",
       "The Keychain is designed for credentials, encrypts each item and supports accessibility policies. The others are plain files or code.", "Storing tokens in UserDefaults for convenience.", "Most get this; ask why not UserDefaults."),
      ("chip", "Are Keychain items stored inside the Secure Enclave?", "No",
       "They live in an encrypted database. The Secure Enclave protects the keys that encrypt them and can hold P-256 private keys.", "Assuming Keychain and Secure Enclave are the same thing.", "Many say yes."),
      ("memory", "Spaced review from 0.6. <code>DashboardViewModel</code> stores a closure that calls <code>self.refresh()</code>. Which capture avoids a retain cycle?<br>A) <code>[self]</code><br>B) <code>[weak self]</code><br>C) None: Swift breaks cycles automatically<br>D) Marking the class <code>final</code>", "B",
       "A weak capture does not keep the ViewModel alive, so the cycle is broken.", "Believing ARC detects cycles for you.", "Spaced review from 0.6. A few pick C.")]
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

S.append(next_slide('0.7', [("7.1", "Threat modeling &amp; trust boundaries", "the boundaries drawn today"),
                            ("7.2", "Sandbox, signing &amp; entitlements", "configuring them in a real project"),
                            ("7.3", "Keychain access controls", "accessibility policies, biometrics"),
                            ("7.5", "Secure Enclave &amp; cryptographic APIs", "keys that never leave the chip"),
                            ("7.6", "TLS, ATS &amp; certificate trust", "ATS: iOS expects HTTPS by default"),
                            ("7.8", "Privacy permissions &amp; minimization", "the camera prompt, and asking for less")],
                    'Everything today was conceptual. Unit 07 implements it: threat modeling, real entitlements and signing, Keychain access controls, the Secure Enclave from CryptoKit, TLS with App Transport Security, which makes iOS expect HTTPS connections by default, and privacy permissions: asking only for what NPay needs.'))

LAB = """<table class="tbl" style="font-size:17px">
      <tr><th style="width:40%">NPay item</th><th style="width:30%">Lives in</th><th>Protected by</th></tr>
      <tr><td>Auth token</td><td></td><td></td></tr>
      <tr><td>Theme setting</td><td></td><td></td></tr>
      <tr><td>Statement PDF</td><td></td><td></td></tr>
      <tr><td>Cheque photo</td><td></td><td></td></tr>
      <tr><td>NPay executable</td><td></td><td></td></tr>
      <tr><td>Balance shown in a widget</td><td></td><td></td></tr>
    </table>"""
S.append(lab_slide('0.7', 'Map NPay&rsquo;s threats',
                   'Fill in the table for six NPay items. Work alone, then compare with a partner.',
                   ['For each item, write <b>where it lives</b>.', 'Write <b>what protects it</b>: sandbox, signing, Keychain, permission or entitlement.',
                    'Mark the one item you think is <b>most at risk</b>, and say why.'],
                   '', 'Answers. Auth token: Keychain, encrypted with keys the Secure Enclave protects, plus its accessibility policy. Theme setting: UserDefaults in NPay’s container, protected by the sandbox. Statement PDF: NPay’s container, Caches, protected by the sandbox and file data protection. Cheque photo: taken through the camera, protected by the camera permission and the usage description, then stored in the container. NPay executable: the app bundle, protected by code signing. Balance in a widget: an App Group container shared by the app and its widget extension, granted by the App Group entitlement. Most at risk: the token, because it lets someone act as the user.', side=LAB))

S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson 0.7 complete</p>
    <h2>iOS Security<br>Architecture</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Lesson 0.8 &mdash; iOS Networking Architecture</p>
  </div>
""" + notes(('SAY', 'Least privilege, enforced at every layer. Next lesson we leave the device: NPay signs in and fetches the balance over the network.')) + "</section>\n\n")

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson 0.7 — iOS Security Architecture</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit 00 · Lesson 0.7 — iOS Security Architecture">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT07, 'w').write(doc)
print(len(S), 'slides')
