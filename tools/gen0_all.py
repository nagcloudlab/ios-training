"""Generates decks/unit-0/unit-00-complete/index.html: Unit 00 as ONE code-free, full-day deck.

Built from the ten generated Unit 00 decks (run after them in build.sh); those decks are not changed.
Slides are taken verbatim (kickers renumbered into ten Parts, LIVE DEMO notes dropped) except the
code slides, which are removed or redrawn without code (marked "# code-free" below). Each Part:
divider -> NPay map -> content -> recap -> two review questions. Swift code is Unit 01's job."""
import html, os, re, sys

OUT_ALL = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.argv = ['x', '/dev/null']
src = open(os.path.join(HERE, 'gen02.py')).read()
exec(src[:src.index('S = []')])   # helpers

S = []
SRC = {}
for n in range(1, 11):
    doc = open(os.path.join(ROOT, f'decks/unit-0/lesson-0.{n}/index.html')).read()
    SRC[n] = re.findall(r'<section class="slide[^"]*"[^>]*>.*?</section>', doc, re.S)

cues = lambda k: '<i class="step cue"></i>' * k
ul = lambda *items: '<ul style="margin:6px 0 0">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
card = lambda label, body, cls='': f'<div class="card accent{(" " + cls) if cls else ""}"><span class="label">{label}</span>{body}</div>'


def label(P):
    return f'Part {P}' if isinstance(P, int) else P


def set_connect(s, text):
    """Replace the slide's last CONNECT note (or add one)."""
    m = list(re.finditer(r'<span class="notes-label">CONNECT</span><p>.*?</p>', s, re.S))
    new = f'<span class="notes-label">CONNECT</span><p>{text}</p>'
    if m:
        return s[:m[-1].start()] + new + s[m[-1].end():]
    return s.replace('  </aside>', f'    {new}\n  </aside>', 1)


def get(n, i):
    s = SRC[n][i - 1]
    return re.sub(r'\s*<span class="notes-label">LIVE DEMO</span><p>.*?</p>', '', s, flags=re.S)


def rekick(s, P, kicker=None):
    def fix(m):
        k = m.group(2)
        if kicker is not None:
            k = kicker
        else:
            k = re.sub(r' &middot; recall from 0\.\d+', '', k)
            if re.match(r'(Part \d+|Wrap-up|Lesson 0\.\d+)( &middot; |$)', k):
                k = re.sub(r'^(Part \d+|Wrap-up|Lesson 0\.\d+)', label(P), k)
            else:
                k = f'{label(P)} &middot; {k}'
        return m.group(1) + k + m.group(3)
    return re.sub(r'(<p class="kicker">)(.*?)(</p>)', fix, s, count=1, flags=re.S)


def simple_recap(s):
    """User: recaps without the 14-box NPay map; the three takeaways become large cards."""
    if '<h2>What to remember</h2>' not in s:
        return s
    items = re.findall(r'<div><svg viewBox="0 0 24 24"><use href="#i-([\w-]+)"/></svg><span><b>(.*?)</b><small>(.*?)</small></span></div>', s)
    assert len(items) == 3, items
    cells = ''.join(f'<div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{ic}"/></svg></span>'
                    f'<p style="font-size:24px"><b>{t}</b><br><span class="muted" style="font-size:20px">{d}</span></p></div>' for ic, t, d in items)
    body = f'<div class="body">\n    <div class="cols c3" style="gap:20px;align-items:stretch">{cells}</div>\n  </div>'
    s = re.sub(r'<div class="body">.*?</div>\s*(?=<aside)', body + '\n', s, count=1, flags=re.S)
    return s.replace('The teal boundary is NPay&rsquo;s own code; everything around it is the platform and the bank. ', '')


def take(n, i, P, kicker=None, connect=None, subs=()):
    s = simple_recap(rekick(get(n, i), P, kicker))
    for sub in subs:
        a, b = sub[0], sub[1]
        assert a in s, (n, i, a)
        s = s.replace(a, b)
    if connect:
        s = set_connect(s, connect)
    S.append(s + '\n\n')


def diagrams(n, i):
    """The slide's svg.art blocks, verbatim."""
    return re.findall(r'<div class="diagram">\s*<svg class="art".*?</svg>\s*</div>', SRC[n][i - 1], re.S)


def question(n, i, P, k, connect, subs=()):
    s = get(n, i)
    dots = ''.join('<i class="done"></i>' if j < k else '<i class="now"></i>' if j == k else '<i></i>' for j in range(2))
    s = re.sub(r'<p class="kicker">.*?</p>', f'<p class="kicker">{label(P)} &middot; Check your understanding &middot; {k + 1} of 2</p>', s, count=1, flags=re.S)
    s = re.sub(r'<div class="q-dots" aria-hidden="true">.*?</div>', f'<div class="q-dots" aria-hidden="true">{dots}</div>', s, count=1, flags=re.S)
    for sub in subs:
        a, b = sub[0], sub[1]
        assert a in s, (n, i, a)
        s = s.replace(a, b)
    S.append(set_connect(s, connect) + '\n\n')


def part(P, title, lead, say, focus, so_far, now, map_say):
    """Part divider only (user: no "Where we are" map slides); focus/so_far/now/map_say kept for the call sites."""
    S.append(chapter(P, title, lead, say, 'Let&rsquo;s start.'))


# ================================================================== opening
S.append("""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit 00 &middot; Foundations</p>
    <h1 style="font-size:58px;line-height:1.05">iOS Architecture<br>Foundations</h1>
    <p class="lead" style="max-width:760px">One app, one day, every layer: how iOS <b>starts, runs, protects, connects and stores</b> NPay.</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', 'Welcome. Today is about architecture, not code: what iOS does for an app, and what the app is responsible for itself. One running example all day: NPay, a payments app with a balance of &#8377;25,000 and a Refresh balance button. From Unit 01 on we write the Swift behind every box you see today.'),
            ('CONNECT', "Here's what you'll be able to explain by the end of the day.")) + "</section>\n\n")

outs = [('grid', 'What iOS does between a <b>tap</b> and NPay&rsquo;s <b>first frame</b>'),
        ('frame', 'Process vs scene, the <b>lifecycle</b> states, and why apps are suspended and terminated'),
        ('thread', 'How a tap travels through the <b>main thread</b>, the RunLoop and rendering'),
        ('memory', 'How <b>ARC</b> keeps objects alive, and how a <b>retain cycle</b> leaks them'),
        ('shield', 'The <b>security</b> layers around NPay: sandbox, signing, Keychain, Secure Enclave'),
        ('link', 'A <b>Refresh balance</b> request end to end, and where each piece of data is <b>stored</b>')]
cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
S.append(slide('Unit 00 &middot; Outcomes', 'By the end of today, you will be able to explain', f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', 'Six things you should be able to explain by the end of today. None of them needs code: each is about who does what, and why.'),
                  ('CONNECT', 'We start with a story.'))))

take(10, 4, 'Unit 00', kicker='Unit 00 &middot; The story',
     subs=[('By the end of this lesson, you will.', 'By the end of today, you will.')],
     connect='Here is how the day is organised.')

rows = [(1, 'The big picture', 'How do iOS and NPay&rsquo;s own code divide the work?'),
        (2, 'From tap to first frame', 'How does an app start?'),
        (3, 'The app lifecycle', 'What happens when the user leaves?'),
        (4, 'Hearing lifecycle events', 'How does app code receive system events?'),
        (5, 'Main thread &amp; rendering', 'How does a tap become UI work?'),
        (6, 'Memory &amp; ARC', 'Who owns objects?'),
        (7, 'Security', 'How does iOS protect data?'),
        (8, 'Networking', 'How does data reach the server and come back?'),
        (9, 'Data storage', 'How does data survive termination?'),
        (10, 'End to end', 'How does everything fit together?')]
trs = ''.join(f'<tr{" class=\"hl\"" if p == 10 else ""}><td class="mono">Part {p}</td><td><b>{t}</b></td><td>{q}</td></tr>' for p, t, q in rows)
S.append(slide('Unit 00 &middot; Today', 'Ten Parts, one app', f"""  <div class="body">
    <table class="tbl"><thead><tr><th>Part</th><th>Topic</th><th>Central question</th></tr></thead><tbody>{trs}</tbody></table>
  </div>""", notes(('SAY', 'Ten Parts, each answering one question about NPay. Every Part opens on the same NPay map, ends with a short recap and two questions. Part 10 puts everything together: one day in NPay&rsquo;s life, every layer at once.'),
                  ('CONNECT', 'Part 1: the big picture.'))))


# ================================================================== Part 1 · the big picture (0.1 Part 1 + 0.2)
part(1, 'The big picture', 'Layers, entities, and who does what inside NPay',
     'Before any detail: the platform layers, the three things we call "the app", and the jobs inside NPay&rsquo;s own code.',
     ('view', 'vm', 'service', 'model'),
     'Nothing yet: we start with the whole map.', 'The layers of iOS, and NPay&rsquo;s own four boxes at the top.',
     'This is the NPay map. It comes back at the start of every Part, with the teal moving to that Part&rsquo;s topic. The dashed box is NPay&rsquo;s process and sandbox; below it is iOS; on the right, the bank&rsquo;s server. Today the teal is on NPay&rsquo;s own code: View, ViewModel, Service, Model.')
take(1, 5, 1)
take(1, 6, 1, connect='Why keep the scene separate from the process? Because one process can have several.')

# authored (user request): why a scene is separate from the process, iPhone vs iPad
P = [f'<rect class="wire dash" x="0" y="20" width="420" height="250" rx="16"/>',
     '<text class="mono" x="18" y="46">IPHONE &#183; ONE NPAY PROCESS</text>',
     tall(60, 72, 300, 170, 'phone', 'Scene: Balance', 'one window &#183; active', l='1'),
     f'<rect class="wire dash" x="470" y="20" width="666" height="250" rx="16"/>',
     '<text class="mono" x="488" y="46">IPAD &#183; ONE NPAY PROCESS</text>',
     tall(500, 72, 300, 170, 'frame', 'Scene A: Balance', 'window A &#183; active', l='2+'),
     tall(818, 72, 300, 170, 'frame', 'Scene B: Transfer', 'window B &#183; background')]
S.append(slide('Part 1 &middot; Process vs scene', 'Why a scene is separate from the process', f"""  <div class="body">
    {svg('0 0 1136 270', 'iPhone: one NPay process with one scene. iPad: one NPay process with two scenes, one active and one in the background', 'scenesep', P, 'max-height:300px')}{cues(2)}
    <div class="gap"></div>
    {points([('phone', 'On iPhone', 'usually one process, one scene: they feel like the same thing'),
             ('frame', 'On iPad', 'two NPay windows side by side: one process, two scenes'),
             ('layers', 'Each scene, its own state', 'one can be active while the other is in the background')],
            label='One process can host several scenes')}
  </div>""", notes(('SAY', 'Why do we separate the scene from the process? Click: on iPhone there is usually one process with one scene, so the two feel like the same thing.'),
                  ('SAY', 'Click: on iPad a user can open NPay in two windows side by side, the balance in one and a transfer in the other. That is still one process, but two scenes. Each scene has its own state: window A is active while window B is in the background.'),
                  ('SAY', 'Click: so "the app is in the background" is ambiguous. Ask which scene, and what the process is doing. Part 3 comes back to this.'),
                  ('ASK', 'NPay has two windows on an iPad. How many processes are running?'),
                  ('EXPECT', 'One. One NPay process hosting two scenes.'),
                  ('CONNECT', 'So what does NPay actually run on? Let&rsquo;s look at the platform beneath it.'))))
take(1, 7, 1)
# improved (user request): the layer stack from 0.1, plus what each layer does for NPay
NPAY_LAYER = {'1': ('Dashboard, Refresh balance', 'formats 2,500,000 paise as &#8377;25,000'),
              '2': ('SwiftUI draws the dashboard', 'URLSession calls the bank'),
              '3': ('Launches NPay, manages its scenes', 'camera permission, notifications'),
              '4': ('Creates NPay&#8217;s process', 'schedules threads, enforces the sandbox'),
              '5': ('CPU runs NPay, GPU draws frames', 'Secure Enclave protects keys')}
layers = re.findall(r'<g data-lit="(\d)" class="nd[^"]*"\s*>.*?</g>', SRC[1][7], re.S)
groups = re.findall(r'(<g data-lit="\d" class="nd[^"]*"\s*>.*?)</g>', SRC[1][7], re.S)
assert len(groups) == 5
P = ['<text class="mono" x="412" y="14">LAYER</text>', '<text class="mono" x="770" y="14">WHAT IT DOES FOR NPAY</text>',
     '<path class="wire faint" d="M748 30V440"/>']
for g in groups:
    n = re.match(r'<g data-lit="(\d)"', g).group(1)
    y = int(re.search(r'<text x="412" y="(\d+)"', g).group(1))
    t, sub = NPAY_LAYER[n]
    g = g.replace(f'data-lit="{n}"', f'data-lit="{n}+"' if n == '5' else f'data-lit="{n}"', 1)
    P.append(g + f'<text x="770" y="{y}">{t}</text><text class="sm" x="770" y="{y + 19}">{sub}</text></g>')
S.append(slide('Part 1 &middot; Architecture &middot; conceptual', 'iOS platform layers, and what each does for NPay', f"""  <div class="body">
    {svg('0 0 1136 450', 'Five stacked layers and what each does for NPay: your app, Apple frameworks, iOS system services, the Darwin/XNU kernel, and hardware', 'layersnpay', P, 'max-height:390px')}{cues(5)}
    <div class="rule step" data-label="Who is in charge">NPay <b>asks</b> through Apple&rsquo;s APIs; iOS <b>decides</b>. Your app does not own the iPhone.</div>
  </div>""", notes(('SAY', 'Five clicks, top to bottom, and for each layer what it does for NPay. Our app: the dashboard, the Refresh balance button, and turning 2,500,000 paise into &#8377;25,000. Apple frameworks: SwiftUI draws the dashboard, URLSession calls the bank. iOS system services: they launch NPay, manage its scenes, ask the user for camera permission, deliver notifications. The Darwin/XNU kernel: it creates NPay&rsquo;s process, schedules its threads and enforces the sandbox. And the hardware: the CPU runs NPay&rsquo;s code, the GPU draws its frames, and the Secure Enclave protects keys.'),
                  ('SAY', 'Click: the important idea. NPay asks through APIs and iOS decides. The app doesn&rsquo;t create its own process or control the display; the platform mediates every request.'),
                  ('SAY', 'This is a responsibility map, not a strict call chain: real frameworks and services talk through several layers rather than one straight path.'),
                  ('ASK', 'Can NPay directly read another app&rsquo;s files, or switch on the camera without asking?'),
                  ('EXPECT', 'No. Apps run inside security restrictions and must use approved APIs and permissions. The operating system mediates access.'),
                  ('CONNECT', 'That is the platform. Now the app on top of it: who is responsible for what inside NPay?'))))
take(2, 5, 1)
take(2, 6, 1)
# fixed (user review): 0.2's table paired unrelated items row by row (Operating system / View ...); now each row compares one aspect
cmp_rows = [('Who designs it', 'Apple', 'Your team'),
            ('What it organises', 'The device: processes, memory, security, hardware', 'Your app&rsquo;s code: screens, state, data'),
            ('Main parts', 'Kernel, system services, frameworks, app lifecycle', 'View, ViewModel, Model, Service'),
            ('Can you change it?', 'No: you use it through Apple&rsquo;s APIs', 'Yes: MVVM is one choice among several'),
            ('NPay example', 'Creates NPay&rsquo;s process, draws its frames', 'DashboardViewModel formats &#8377;25,000')]
trs = ''.join(f'<tr><td><b>{a}</b></td><td>{b}</td><td>{c}</td></tr>' for a, b, c in cmp_rows)
cmp_pts = re.search(r'<div class="tip step"[^>]*>.*?</div></div></div>', SRC[2][7], re.S).group(0)
S.append(slide('Part 1 &middot; Two architectures', 'iOS architecture vs your app&rsquo;s architecture', f"""  <div class="body">
    <table class="tbl"><thead><tr><th></th><th>iOS platform architecture</th><th>Application architecture</th></tr></thead><tbody>{trs}</tbody></table>
    <div class="gap"></div>
    {cmp_pts}
  </div>""", notes(('SAY', 'One of the most important distinctions in this course. Read it row by row. Apple designs the platform architecture; your team designs the application architecture. The platform organises the device: processes, memory, security and hardware. Your architecture organises your own code: screens, state and data.'),
                  ('SAY', 'Its parts are the kernel, system services, frameworks and the app lifecycle; yours are View, ViewModel, Model and Service. You cannot change the platform, you use it through Apple&rsquo;s APIs; your own structure is a choice, and MVVM is only one option. For NPay: iOS creates the process and draws the frames; DashboardViewModel formats &#8377;25,000.'),
                  ('SAY', 'Click: related, but not the same thing.'),
                  ('ASK', 'Is MVVM part of iOS?'),
                  ('EXPECT', 'No. MVVM is an application design choice; iOS does not know about it.'),
                  ('CONNECT', 'Now follow one tap through these layers.'))))
take(2, 10, 1)
take(2, 12, 1)
take(2, 13, 1, connect='So who holds that state, and who turns it into what the screen shows? That is MVVM.')

# code-free: 0.2's MVVM slide, code windows replaced by the three roles (the cards are the diagram's steps)
mv = diagrams(2, 15)[0]
roles = [('Model', 'what the data means', ['A balance: account and amount in paise', 'No formatting, no UI']),
         ('ViewModel', 'what the screen needs', ['Turns 2,500,000 paise into &ldquo;&#8377;25,000&rdquo;', 'Holds loading and error state', 'Asks the Service for data']),
         ('View', 'what the user sees', ['Shows the balance text', 'Sends taps to the ViewModel', 'Owns its ViewModel'])]
cards3 = ''.join(f'<div class="card accent step"><span class="label">{t} &middot; {d}</span>{ul(*b)}</div>' for t, d, b in roles)
S.append(slide('Part 1 &middot; MVVM', 'Model&ndash;View&ndash;ViewModel, for a balance screen', f"""  <div class="body top">
    {mv}
    <div class="gap"></div>
    <div class="cols c3" style="gap:18px;align-items:stretch">{cards3}</div>
    <p class="small muted" style="margin:14px 0 0">MVVM is a way to organise app code, not an iOS requirement. Unit 04 builds it in Swift.</p>
  </div>""", notes(('SAY', 'MVVM stands for Model, View, ViewModel. Click through. The Model is what the data means: a balance for an account, stored as whole paise so money stays exact. The ViewModel is what the screen needs: ready-to-show text such as &#8377;25,000, plus loading and error state; it asks the Service for data. The View is what the user sees: it shows the text and passes taps to the ViewModel.'),
                  ('SAY', 'Formatting paise as rupees is presentation, so it belongs in the ViewModel: not on the server, not in the view. Unit 04 builds this pattern properly, with dependency injection and tests.'),
                  ('CONNECT', 'Before the questions, a recap.'))))
take(2, 16, 1, connect='Two quick questions on Part 1.')
question(1, 35, 1, 0, 'Next question.')
question(2, 20, 1, 1, 'Part 2: what happens between a tap on the NPay icon and its first screen.')


# ================================================================== Part 2 · from tap to first frame (0.1)
part(2, 'From tap to first frame', 'What iOS does before NPay&rsquo;s first screen appears',
     'One tap on the NPay icon, followed all the way to the first frame on screen.',
     ('springboard', 'kernel', 'scene'),
     'The layers, and who does what inside NPay.', 'The launch: SpringBoard, the kernel and the first scene.',
     'The teal moves down into iOS: SpringBoard, which handles the tap, the kernel, which creates the process, and the scene NPay shows its first frame in.')
take(1, 10, 2)
take(1, 11, 2)
# rebuilt (user review): one point per click, each lighting its part of the drawing
sb = re.search(r'<div class="diagram">\s*<svg class="art".*?</svg>\s*</div>', SRC[1][11], re.S).group(0)
for a_, b_ in [('<path class="wire" data-lit="2" d="M440', '<path class="wire" data-lit="3+" d="M440'),
               ('<path class="wire" data-lit="2" d="M720', '<path class="wire" data-lit="3+" d="M720'),
               ('<g class="nd" data-lit="2">\n          <rect class="sh" x="530"', '<g class="nd" data-lit="3+">\n          <rect class="sh" x="530"'),
               ('<g class="nd" data-lit="2">\n          <path class="sh" d="M855', '<g class="nd" data-lit="3+">\n          <path class="sh" d="M855'),
               ('<g class="nd ghost">', '<g class="nd ghost" data-lit="2">'),
               ('<text class="mono fade" data-lit="2"', '<text class="mono fade" data-lit="2+"'),
               ('<circle class="fill-teal travel fade" data-lit="2" r="5"><animateMotion dur="1.2s" repeatCount="indefinite" path="M440', '<circle class="fill-teal travel fade" data-lit="3+" r="5"><animateMotion dur="1.2s" repeatCount="indefinite" path="M440'),
               ('<circle class="fill-teal travel fade" data-lit="2" r="5"><animateMotion dur="1.2s" repeatCount="indefinite" path="M720', '<circle class="fill-teal travel fade" data-lit="3+" r="5"><animateMotion dur="1.2s" repeatCount="indefinite" path="M720')]:
    assert a_ in sb, a_
    sb = sb.replace(a_, b_)
sb_cards = ''.join(f'<div class="card accent step anim-up"><span class="label">{k}</span><h3 style="font-size:24px;margin:4px 0 4px">{t}</h3><p class="small muted" style="margin:0">{d}</p></div>'
                   for k, t, d in [('1 &middot; SpringBoard', 'Part of iOS', 'it draws the Home Screen'),
                                   ('2 &middot; NPay', 'Isn&rsquo;t running yet', 'its icon is only a picture'),
                                   ('3 &middot; The request', 'iOS is asked to open NPay', 'new process, or reuse one')])
S.append(slide('Part 2 &middot; System UI &middot; conceptual', 'SpringBoard handles the tap', f"""  <div class="body">
    {sb}
    <div class="gap-lg"></div>
    <div class="cols c3" style="gap:18px;align-items:stretch">{sb_cards}</div>
  </div>""", notes(
    ('SAY', 'Click one: the tap goes to SpringBoard. It is part of iOS, a system process that starts when the iPhone boots, and the Home Screen is SpringBoard&rsquo;s screen, not NPay&rsquo;s. In the hotel picture, SpringBoard is the front desk.'),
    ('SAY', 'Click two: NPay is not running yet. The icon is just an image from NPay&rsquo;s bundle that SpringBoard draws, so nothing in our code can react to the tap itself. Badges and the app switcher are SpringBoard&rsquo;s too; a switcher card is a snapshot, not proof the app is running.'),
    ('SAY', 'Click three: SpringBoard does not start NPay itself. It asks iOS to open the app: if NPay&rsquo;s process is still alive, iOS brings it forward; if not, it creates a new process. The exact private steps are undocumented and change between iOS versions, so we keep this conceptual.'),
    ('CONNECT', 'That question, is the process alive, is a critical fork: cold launch vs warm activation.'))))
take(1, 13, 2)
take(1, 15, 2)
take(1, 16, 2)
# rebuilt (user review): the teal moves through the pipeline, one caption per step; plain points instead of Mach-O internals
PIPE = [('file', '.swift source', 'what you write', 'Xcode reads NPay&#8217;s Swift files'),
        ('code', 'Frontend', 'parse + type check', 'Checks NPay&#8217;s code: syntax and types'),
        ('layers', 'SIL', 'Swift IR', 'Swift-specific analysis and optimisation'),
        ('chip', 'LLVM', 'machine code', 'Produces ARM64 machine code for the iPhone CPU'),
        ('lock', 'Link + sign', 'one binary', 'Joins the pieces into one binary, then signs it'),
        ('file', 'Mach-O', 'executable', 'NPay&#8217;s executable, inside NPay.app')]
P = []
for k, (ic, t, sub, cap) in enumerate(PIPE):
    x = 2 + k * 190
    w = 180 if k == 5 else 160
    cls = 'nd solid' if k == 5 else 'nd'
    on = ' class="on"' if k == 5 else ''
    lit_ = '6+' if k == 5 else str(k + 1)
    P.append(f'<g class="{cls}" data-lit="{lit_}"><rect class="sh" x="{x}" y="10" width="{w}" height="104" rx="14"/>'
             f'<use{on} href="#i-{ic}" x="{x + w / 2 - 14:g}" y="24" width="28" height="28"/>'
             f'<text{on} x="{x + w / 2:g}" y="78" text-anchor="middle">{t}</text>'
             f'<text class="sm{" on" if k == 5 else ""}" x="{x + w / 2:g}" y="98" text-anchor="middle">{sub}</text></g>')
    if k < 5:
        P.append(f'<path class="wire" d="M{x + 166} 62H{x + 184}M{x + 177} 55l7 7-7 7"/>')
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 5 else ""}" x="568" y="214" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
P += ['<path class="wire" data-lit="1-5" d="M2 136V144H912V136"/>', '<text class="mono" x="457" y="166" text-anchor="middle">BUILD TIME, ON YOUR MAC</text>',
      '<path class="wire" data-lit="6+" d="M952 136V144H1132V136"/>', '<text class="mono" x="1042" y="166" text-anchor="middle">SHIPS IN THE BUNDLE</text>']
S.append(slide('Part 2 &middot; Build time', 'The compilation pipeline', f"""  <div class="body top">
    {svg('0 0 1136 226', 'NPay&#8217;s Swift source goes through the frontend, SIL, LLVM, then link and sign, producing a Mach-O executable that ships in the app bundle', 'pipe6', P)}{cues(6)}
    <div class="gap-lg"></div>
    {points([('chip', 'Compiled ahead of time', 'the iPhone never sees Swift source'),
             ('lock', 'Signed', 'iOS checks who built it, and that it is unchanged'),
             ('app', 'Ships in NPay.app', 'dyld loads it at launch')], label='What this means')}
  </div>""", notes(
    ('SAY', 'Six clicks along the pipeline, all on your Mac, before NPay ever reaches a phone. One: Xcode reads NPay&rsquo;s Swift files. Two: the frontend parses them and type-checks them; most compiler errors you will ever see come from here. Three: SIL, Swift&rsquo;s own intermediate language, where Swift-specific analysis and optimisation happen. Four: LLVM produces ARM64 machine code for the iPhone&rsquo;s CPU. Five: the linker joins everything into one binary, and it is signed.'),
    ('SAY', 'Six: the result is a Mach-O executable, the executable format for Apple platforms, and it ships inside NPay.app.'),
    ('SAY', 'Click: what this means. Swift is compiled ahead of time, so the iPhone never sees or interprets our source. The binary is signed, so iOS can check who built it and that nobody changed it; Part 7 comes back to code signing. And at launch, dyld loads this file into the new process.'),
    ('ASK', 'Does the iPhone compile NPay&rsquo;s Swift code when you tap the icon?'),
    ('EXPECT', 'No. It was compiled on the Mac at build time; the phone loads machine code.'),
    ('CONNECT', 'When the user taps, the system loads this binary. That&rsquo;s dyld&rsquo;s job.'))))
# rebuilt (user review): the teal walks down dyld's four steps, one numbered card per click
dy = re.search(r'<div class="diagram">\s*<svg class="art".*?</svg>\s*</div>', SRC[1][18], re.S).group(0)
for a_, b_ in [('<g class="nd solid" data-lit="2">', '<g class="nd solid" data-lit="1">'),
               ('<g class="fade" data-lit="2">', '<g class="fade" data-lit="1">'),
               ('<g class="nd" data-lit="0-1">', '<g class="nd" data-lit="1">'),
               ('<g class="nd"><rect class="sh" x="15" y="204"', '<g class="nd" data-lit="2"><rect class="sh" x="15" y="204"'),
               ('<g class="nd"><rect class="sh" x="185" y="204"', '<g class="nd" data-lit="2"><rect class="sh" x="185" y="204"'),
               ('<g class="nd"><rect class="sh" x="355" y="204"', '<g class="nd" data-lit="2"><rect class="sh" x="355" y="204"'),
               ('<g class="nd"><rect class="sh" x="150" y="292"', '<g class="nd" data-lit="3"><rect class="sh" x="150" y="292"'),
               ('<g class="nd"><rect class="sh" x="150" y="386"', '<g class="nd" data-lit="4+"><rect class="sh" x="150" y="386"')]:
    assert a_ in dy, a_
    dy = dy.replace(a_, b_)
dy_cards = ''.join(f'<div class="card accent step anim-up" style="padding:12px 18px;margin:0 0 10px"><span class="label">{k}</span><p style="margin:2px 0 0;font-size:20px"><b>{t}</b> <span class="muted">&middot; {d}</span></p></div>'
                   for k, t, d in [('1', 'Open NPay&rsquo;s executable', 'built on your Mac'),
                                   ('2', 'Load what it needs', 'SwiftUI, Foundation, Swift runtime'),
                                   ('3', 'Connect the pieces', 'every call finds its target'),
                                   ('4', 'Start NPay&rsquo;s code', 'initializers, then the entry point')])
S.append(slide('Part 2 &middot; Runtime loading &middot; conceptual', 'dyld: the dynamic loader', f"""  <div class="body cols middle">
    {dy}
    <div>
      {dy_cards}
      <div class="rule step" style="margin-top:6px">dyld <b>loads and links</b> code compiled earlier, on your Mac. It <b>never compiles</b> anything.</div>
    </div>
  </div>""", notes(
    ('SAY', 'The process exists; now its code must be loaded. That is dyld&rsquo;s job, the dynamic loader. Click one: dyld opens NPay&rsquo;s executable, the Mach-O file we built on the Mac.'),
    ('SAY', 'Click two: NPay uses SwiftUI, Foundation and the Swift runtime, so dyld loads those too. System frameworks come from the dyld shared cache, prepared ahead of time by Apple, which is why they load quickly.'),
    ('SAY', 'Click three: dyld connects the pieces. When NPay calls into SwiftUI, that call has to find its target in memory; dyld maps the code and binds those symbols. Click four: initializers run, and then NPay&rsquo;s own entry point.'),
    ('SAY', 'Click: dyld loads and links. It never compiles; the compiling happened on the Mac.'),
    ('CONNECT', 'The loader has done its work. Where does NPay&rsquo;s own code begin?'))))

# code-free: 0.1's @main slide redrawn as the chain from entry point to root view; one plain caption per click (user review)
steps4 = [('code', '@main', 'the entry point', 'Swift marks where NPay&#8217;s code starts: dyld jumps here'),
          ('frameworks', 'NPayApp', 'the App', 'The App describes NPay as a whole: created once per launch'),
          ('frame', 'WindowGroup', 'a Scene', 'Declares NPay&#8217;s windows: iOS creates a scene for each'),
          ('phone', 'DashboardView', 'the root view', 'The first screen each window shows')]
P = []
for k, (ic, t, sub, cap) in enumerate(steps4):
    x = k * 292
    P.append(tall(x, 0, 260, 120, ic, t, sub, l=f'{k + 1}+' if k == 3 else str(k + 1)))
    if k < 3:
        P.append(wire(f'M{x + 262} 60H{x + 290}') + wire(head(x + 290, 60, 'r')))
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="568" y="172" text-anchor="middle" style="font-size:21px">{k + 1}. {cap}</text>')
S.append(slide('Part 2 &middot; App entry point', 'Where NPay&rsquo;s own code begins', f"""  <div class="body">
    {svg('0 0 1136 184', 'Entry point, App, Scene, root view', 'entry4', P)}{cues(4)}
    <div class="gap-lg"></div>
    {points([('process', 'Once per launch', 'the App is created when the process starts'),
             ('frame', 'One window, one scene', 'on iPad, two windows: two DashboardViews'),
             ('eye', 'Still a description', 'the next slide turns it into pixels')], label='What this means')}
  </div>""", notes(('SAY', 'When dyld has loaded the executable and its libraries, execution reaches NPay&rsquo;s own code. Click one: the entry point, marked @main; this is where dyld jumps.'),
                  ('SAY', 'Click two: in a SwiftUI app the entry point is the App type, NPayApp. It describes NPay as a whole and is created once per launch. Click three: the App declares its windows with a WindowGroup, and iOS creates a scene for each window. Click four: inside each window, the first screen, DashboardView.'),
                  ('SAY', 'Click: what this means. The App is created once, when the process starts. Each window is its own scene, so on an iPad with two NPay windows there are two DashboardViews, as on slide 8. And DashboardView is still only a description of the screen. We read these names today; Unit 01 writes the Swift behind each box.'),
                  ('ASK', 'NPay is open in two iPad windows. How many NPayApp instances are there?'),
                  ('EXPECT', 'One: one process, one App. Two scenes, each with its own DashboardView.'),
                  ('CONNECT', 'DashboardView is only a description. How does it become pixels?'))))
# code-free labels on 0.1's view tree (user review)
take(1, 24, 2, subs=[('<text class="code" x="16" y="26">WindowGroup</text>', '<text x="16" y="26">Window</text>'),
                     ('<text class="code" x="56" y="88">DashboardView</text>', '<text x="56" y="88">Dashboard screen</text>'),
                     ('<text class="code" x="96" y="150">VStack</text>', '<text x="96" y="150">Vertical stack</text>'),
                     ('<text class="code" x="136" y="212">Text("NPay")</text>', '<text x="136" y="212">Title &#8220;NPay&#8221;</text>'),
                     ('<text class="code" x="136" y="262">Text("Available balance")</text>', '<text x="136" y="262">Label &#8220;Available balance&#8221;</text>'),
                     ('<text class="code" x="136" y="312">Text(balanceText)</text>', '<text x="136" y="312">Balance &#8220;&#8377;25,000&#8221;</text>'),
                     ('<text class="code" x="136" y="362">Button("Refresh balance")</text>', '<text x="136" y="362">Button &#8220;Refresh balance&#8221;</text>'),
                     ('The view values form a tree: WindowGroup, DashboardView, VStack, three Texts and a Button.', 'The view values form a tree: a window, the dashboard screen, a vertical stack, a title, a label, the balance and a button.'),
                     ("Views compose into a tree. WindowGroup holds the root view, DashboardView's body returns a VStack, and the VStack holds three Texts and a Button. Nothing here is a drawing command.",
                      'Click: views compose into a tree. The window holds the dashboard screen; the screen is a vertical stack holding a title, a label, the balance and a Refresh button. Each box is a description, not a drawing command. Click: the frameworks render that tree onto the screen.')])

# rebuilt (user review): one stage per click with an NPay caption, then the main-thread lane, then the takeaway
FF = [('play', 'Scene connects', 'still inactive', 'iOS gives NPay a window, still inactive: no touches yet'),
      ('eye', 'Evaluate', 'view descriptions', 'SwiftUI reads DashboardView&#8217;s description'),
      ('diff', 'Reconcile', 'what changed', 'Works out what is new: on launch, everything'),
      ('layout', 'Layout', 'size &amp; place', 'Decides each element&#8217;s size and position'),
      ('layers', 'Graphics', 'composite', 'Draws and combines the layers into one image'),
      ('frame', 'First frame', 'then: active', '&#8377;25,000 is on screen, then the scene becomes active')]
P = []
for k, (ic, t, sub, cap) in enumerate(FF):
    x = 12 + k * 192
    P.append(f'<g class="nd" data-lit="{k + 1}{"+" if k == 5 else ""}"><rect class="sh" x="{x}" y="10" width="152" height="104" rx="14"/>'
             f'<use href="#i-{ic}" x="{x + 62}" y="24" width="28" height="28"/><text x="{x + 76}" y="78" text-anchor="middle">{t}</text>'
             f'<text class="sm" x="{x + 76}" y="98" text-anchor="middle">{sub}</text></g>')
    if k < 5:
        P.append(f'<path class="wire" d="M{x + 160} 62H{x + 184}M{x + 178} 56l6 6-6 6"/>')
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 5 else ""}" x="450" y="164" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
# the phone builds up beside the caption, one stage per click
cx = 1050
P.append('<use href="#d-iphone" x="990" y="128" width="120" height="240"/>')
P.append(f'<g class="fade" data-lit="1"><text class="sm" x="{cx}" y="252" text-anchor="middle">inactive</text></g>')
P.append(f'<g class="fade" data-lit="2-3">' + ''.join(f'<text class="sm" x="{x0}" y="{y0}">{t}</text>' for x0, y0, t in
         [(1012, 190, 'Window'), (1018, 208, 'Dashboard'), (1024, 226, 'Stack'), (1030, 244, 'Title'), (1030, 262, 'Label'), (1030, 280, 'Balance'), (1030, 298, 'Button')]) + '</g>')
P.append(f'<text class="mono fade fill-teal" data-lit="3" x="{cx}" y="326" text-anchor="middle">ALL NEW</text>')
P.append('<g class="fade" data-lit="4">' + ''.join(f'<rect class="mute" x="{cx - w / 2:g}" y="{y0}" width="{w}" height="{h}" rx="4"/>' for y0, w, h in
         [(184, 46, 14), (214, 70, 10), (234, 74, 20), (268, 72, 20)]) + '</g>')
P.append(f'<g class="fade" data-lit="5+"><text x="{cx}" y="196" text-anchor="middle" style="font-size:15px;font-weight:800">NPay</text>'
         f'<text class="sm" x="{cx}" y="222" text-anchor="middle" style="font-size:10px">Available balance</text>'
         f'<text x="{cx}" y="250" text-anchor="middle" style="font-size:16px;font-weight:700">&#8377;25,000</text></g>')
P.append(f'<g class="fade" data-lit="5"><rect class="wire" style="fill:none" x="{cx - 38}" y="266" width="76" height="22" rx="6"/><text class="sm" x="{cx}" y="281" text-anchor="middle" style="font-size:9px">Refresh balance</text></g>')
P.append(f'<g class="nd fade" data-lit="6+"><rect class="sh" x="{cx - 38}" y="266" width="76" height="22" rx="6"/><text class="sm" x="{cx}" y="281" text-anchor="middle" style="font-size:9px">Refresh balance</text></g>')
P.append(f'<text class="mono fade fill-teal" data-lit="6+" x="{cx}" y="326" text-anchor="middle">ACTIVE</text>')
P.append("""<g class="fade" data-lit="7+">
          <text class="mono" x="12" y="226">MAIN THREAD</text>
          <g class="nd"><rect class="sh" x="12" y="238" width="420" height="30" rx="8"/><text class="sm" x="222" y="258" text-anchor="middle">launch work</text></g>
          <g class="nd alert"><rect class="sh" x="432" y="238" width="270" height="30" rx="8"/><text class="sm" x="567" y="258" text-anchor="middle">blocked: heavy synchronous work</text></g>
          <g class="nd"><rect class="sh" x="702" y="238" width="196" height="30" rx="8"/><text class="sm" x="800" y="258" text-anchor="middle">responds to taps</text></g>
          <path class="wire" d="M432 230V276"/><text class="sm" x="432" y="296" text-anchor="middle">first frame visible</text>
          <path class="wire" d="M702 230V276"/><text class="sm" x="702" y="296" text-anchor="middle">fully interactive</text>
        </g>""")
S.append(slide('Part 2 &middot; Rendering &middot; conceptual', 'The first-frame journey', f"""  <div class="body top">
    {svg('0 0 1136 370', 'Six stages from scene connected (still inactive) to first frame, after which the scene becomes active, then a main-thread timeline where the frame is visible but input waits behind blocking work', 'ffj', P)}{cues(7)}
    <div class="gap"></div>
    <div class="takeaway step">First visible frame and <b>fully interactive</b> are not the same milestone.</div>
  </div>""", notes(
    ('SAY', 'Watch the phone on the right: it builds up with each click. Six clicks, one stage each. One: the scene connects; iOS gives NPay a window, but it is still inactive, so no touches yet. Two: SwiftUI evaluates DashboardView&rsquo;s description. Three: it reconciles, working out what changed; on launch, everything is new. Four: layout decides each element&rsquo;s size and position. Five: graphics draws and composites the layers into one image. Six: the first frame, &#8377;25,000 on screen, and only then does the scene become active.'),
    ('SAY', 'Click: the main-thread lane. The first frame can be on screen while the main thread is still busy with heavy synchronous work. Until that work finishes, taps wait in line.'),
    ('SAY', 'Click: so first visible frame and fully interactive are two different milestones. Part 5 comes back to why.'),
    ('ASK', 'The dashboard is visible but a tap does nothing for two seconds. What is the main thread doing?'),
    ('EXPECT', 'Still busy with synchronous work; the tap waits in line until it finishes.'),
    ('CONNECT', 'A frame on screen doesn&rsquo;t mean the app runs forever. The system manages its life from here.'))))
# rebuilt (user: "not clear"): one plain card per click beside the state diagram; the demo table and the code in the notes removed
lc = re.search(r'<div class="diagram">\s*<svg class="art".*?</svg>\s*</div>', SRC[1][26], re.S).group(0)
lc_cards = ''.join(f'<div class="card accent step anim-up" style="padding:10px 18px;margin:0 0 8px"><p style="margin:0;font-size:20px"><span class="mono" style="color:var(--teal)">{k}</span>&ensp;<b>{t}</b> <span class="muted">&middot; {d}</span></p></div>'
                   for k, t, d in [('1', 'Inactive', 'on screen, no touches yet'),
                                   ('2', 'Active', 'the user is using NPay'),
                                   ('3', 'Background', 'the user left: not visible'),
                                   ('4', 'Suspended', 'kept in memory, no code runs'),
                                   ('5', 'Terminated', 'iOS needs the memory: no warning')])
S.append(slide('Part 2 &middot; Preview &middot; conceptual', 'After the first frame, iOS decides', f"""  <div class="body cols middle" style="grid-template-columns:1.05fr 1fr">
    {lc}
    <div>
      {lc_cards}
      <div class="rule step" style="margin-top:6px">From the first frame on, <b>iOS</b> decides when NPay runs. Part 3 goes deeper.</div>
    </div>
  </div>""", notes(
    ('SAY', 'The first frame is on screen. From here, iOS manages NPay&rsquo;s life. Click one: launch ends in inactive; the scene is on screen but not yet receiving touches. Click two: active; the user is using NPay.'),
    ('SAY', 'Click three: the user goes to the Home Screen; the scene passes through inactive to background, no longer visible. Click four: soon after, iOS suspends NPay; the process stays in memory but none of its code runs. Click five: if the system needs memory, it may end a suspended NPay with no warning, which is why coming back is not always a warm activation.'),
    ('SAY', 'Click: the point of this slide. After the first frame, iOS decides when NPay runs. Part 3 is all about this.'),
    ('ASK', 'NPay is suspended. Can it update the balance in the background on its own?'),
    ('EXPECT', 'No. A suspended app runs no code; it continues only when iOS resumes it.'),
    ('CONNECT', 'We have every piece. Let&rsquo;s put it together.'))))
# rebuilt (user review): two lanes show what a cold launch does that a warm activation skips; no timing numbers
COLD = [('process', 'Create process'), ('link', 'dyld loads'), ('code', 'App starts'), ('play', 'Scene connects'), ('frame', 'First frame')]
P = ['<text class="mono" x="0" y="18">COLD LAUNCH &#183; NO PROCESS</text>',
     '<text class="mono" x="0" y="130">WARM ACTIVATION &#183; PROCESS SURVIVED</text>']
for k, (ic, t) in enumerate(COLD):
    x = k * 224
    P.append(f'<g class="nd pass" data-lit="1" style="--d:{k * 0.18:.2f}s"><rect class="sh" x="{x}" y="28" width="200" height="60" rx="12"/>'
             f'<use href="#i-{ic}" x="{x + 14}" y="45" width="26" height="26"/><text x="{x + 50}" y="64">{t}</text></g>')
    if k < 4:
        P.append(f'<path class="wire" d="M{x + 202} 58H{x + 222}M{x + 215} 51l7 7-7 7"/>')
P.append('<g class="nd ghost"><rect class="sh" x="0" y="140" width="648" height="60" rx="12"/><text x="324" y="166" text-anchor="middle">already done</text>'
         '<text class="sm" x="324" y="186" text-anchor="middle">process, loading and App are still in memory</text></g>')
P.append('<path class="wire" d="M650 170H670M663 163l7 7-7 7"/>')
for k, (ic, t) in enumerate([('play', 'Scene activates'), ('frame', 'Frame')]):
    x = 672 + k * 224
    P.append(f'<g class="nd" data-lit="2"><rect class="sh" x="{x}" y="140" width="200" height="60" rx="12"/>'
             f'<use href="#i-{ic}" x="{x + 14}" y="157" width="26" height="26"/><text x="{x + 50}" y="176">{t}</text></g>')
    if k == 0:
        P.append(f'<path class="wire" d="M{x + 202} 170H{x + 222}M{x + 215} 163l7 7-7 7"/>')
S.append(slide('Part 2 &middot; Comparison &middot; illustrative', 'What a cold launch costs', f"""  <div class="body top">
    {svg('0 0 1120 204', 'A cold launch creates the process, loads with dyld, starts the App, connects the scene and draws the first frame. A warm activation skips the first three: they are still in memory.', 'coldwarm', P)}{cues(2)}
    <div class="gap"></div>
    <div class="cols" style="gap:18px;align-items:stretch">
      {card('A cold launch rebuilds memory', ul('NPay&rsquo;s balance and screen state are gone', 'Restore saved data, then refresh from the server'), 'step')}
      {card('What slows the first frame', ul('Too much setup before it', 'A blocked main thread', 'A heavy first screen'), 'step')}
    </div>
  </div>""", notes(
    ('SAY', 'Click one: a cold launch. There is no process, so iOS creates one, dyld loads the code, the App starts, the scene connects, and only then the first frame.'),
    ('SAY', 'Click two: a warm activation. The process survived, so the first three steps are already done; the scene activates and a frame is drawn. That is why warm is cheaper. But survival is never guaranteed: iOS can end any background app, so never design around &ldquo;it will still be in memory&rdquo;.'),
    ('SAY', 'Click: after a cold launch everything that lived in memory is gone, NPay&rsquo;s balance and screen state included, so the app restores what it saved and refreshes from the server. Click: what makes the first frame slow is almost always our own work: too much setup, a blocked main thread, or a heavy first screen.'),
    ('ASK', 'What happens to in-memory state when the OS ends the process?'),
    ('EXPECT', 'It is lost. Anything that matters must be saved, and restored on the next launch.'),
    ('ASK', 'Should we speed up dyld first when startup is slow?'),
    ('EXPECT', 'Not without measuring. Find the actual bottleneck first.'),
    ('CONNECT', 'Now let&rsquo;s put the whole journey together.'))))
take(1, 31, 2, connect='Before the recap: five things people often believe about launch.')
take(1, 32, 2, connect='Let&rsquo;s recap Part 2.')   # launch myths (moved from the wrap-up: all five are about launch)
take(1, 33, 2, subs=[('Three things to keep from today.', 'Three things to keep from Part 2.')], connect='Two quick questions on Part 2.')
question(1, 37, 2, 0, 'Next question.')
question(1, 42, 2, 1, 'Part 3: the app is running. What happens when the user leaves it?')


# ================================================================== Part 3 · lifecycle (0.3)
part(3, 'The app lifecycle', 'Scenes, states, suspension and memory pressure',
     'NPay is running. Now the user switches apps, and iOS starts making decisions.',
     ('scene', 'springboard', 'sandbox'),
     'From a tap to NPay&rsquo;s first frame.', 'What happens after: scenes, states, suspension and termination.',
     'The teal is on the scene and on NPay&rsquo;s process boundary: iOS decides when NPay runs, waits or ends.')
# rebuilt (user review): the hotel analogy carries the states: room lights = scene phases, suite locked/cleared = process conditions
P = ['<g class="nd ghost" data-lit="1"><rect class="sh" x="10" y="34" width="540" height="392" rx="18"/></g>',
     '<g class="nd" data-lit="1"><use href="#i-building" x="10" y="0" width="24" height="24"/><text class="mono" x="42" y="18">HOTEL MANAGEMENT &#183; iOS</text></g>',
     '<g class="nd" data-lit="2"><rect class="sh" x="36" y="60" width="488" height="232" rx="14"/><text class="mono" x="56" y="88">NPAY&#8217;S SUITE &#183; THE APP PROCESS</text></g>',
     '<g class="nd" data-lit="3+"><rect class="sh" x="60" y="104" width="204" height="168" rx="12"/><use href="#i-frame" x="149" y="122" width="26" height="26"/>'
     '<text x="162" y="176" text-anchor="middle">Room A &#183; Balance</text><text class="sm" x="162" y="198" text-anchor="middle">lights on: active</text></g>',
     '<g class="nd"><rect class="sh" x="296" y="104" width="204" height="168" rx="12"/><use href="#i-frame" x="385" y="122" width="26" height="26"/>'
     '<text x="398" y="176" text-anchor="middle">Room B &#183; Transfer</text><text class="sm" x="398" y="198" text-anchor="middle">lights off: background</text></g>',
     '<g class="fade" data-lit="4+"><use href="#i-user" x="147" y="218" width="30" height="30" style="color:var(--teal)"/><text class="sm" x="162" y="262" text-anchor="middle">the guest</text></g>',
     '<g class="fade" data-lit="5+"><text class="mono" x="36" y="324">WHAT MANAGEMENT CAN DO TO THE WHOLE SUITE</text>'
     '<g class="nd"><rect class="sh" x="36" y="336" width="232" height="68" rx="12"/><use href="#i-lock" x="50" y="357" width="26" height="26"/><text x="88" y="364">Suite locked</text><text class="sm" x="88" y="384">suspended: no one works</text></g>'
     '<g class="nd"><rect class="sh" x="292" y="336" width="232" height="68" rx="12"/><use href="#i-cross" x="306" y="357" width="26" height="26"/><text x="344" y="364">Suite cleared</text><text class="sm" x="344" y="384">terminated: memory freed</text></g></g>']
hotel_rows = [('building', 'Hotel management', 'iOS'),
              ('process', 'NPay&rsquo;s suite', 'the app process: one per app'),
              ('frame', 'A room&rsquo;s lights', 'a scene: on active &middot; dimmed inactive &middot; off background'),
              ('user', 'The guest', 'the user, in one room at a time'),
              ('lock', 'Suite locked or cleared', 'the process: suspended or terminated')]
rows_html = ''.join(f'<div class="step"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg><span><b>{t}</b><small>{d}</small></span></div>' for i, t, d in hotel_rows)
S.append(slide('Part 3 &middot; Analogy', 'NPay&rsquo;s suite in the hotel', f"""  <div class="body cols middle" style="grid-template-columns:1.1fr 1fr">
    {svg('0 0 560 430', 'A hotel: management is iOS, NPay&rsquo;s suite is the app process, each room is a scene whose lights show its phase, and management can lock or clear the whole suite.', 's3hotel2', P, 'max-height:470px')}
    <div>
      <div class="points v">{rows_html}</div>
      <div class="gap"></div>
      <div class="rule step"><b>Rooms</b> have lights: scene phases. The <b>suite</b> can be locked or cleared: process conditions.</div>
    </div>
  </div>""", notes(
    ('SAY', 'In Part 1 the iPhone was a hotel. Click one: hotel management is iOS. Click two: NPay has a suite, the app process, one per app.'),
    ('SAY', 'Click three: the suite has rooms, the scenes. Each room has its own lights: on means active, dimmed means inactive, off means background. Here Room A, the balance, has its lights on; Room B, a transfer, is dark. Click four: the guest, the user, is in one room at a time.'),
    ('SAY', 'Click five: management can also act on the whole suite. It can lock it, and nobody inside works: the process is suspended. Or it can clear it out to free the space: the process is terminated.'),
    ('SAY', 'Click: so there are two kinds of state. Rooms have lights, the scene phases. The suite can be locked or cleared, the process conditions.'),
    ('ASK', 'Room A&rsquo;s lights are off and so are Room B&rsquo;s. Is the suite locked?'),
    ('EXPECT', 'Not necessarily: all scenes in the background, the process may still run briefly. Locking, suspension, is management&rsquo;s separate decision.'),
    ('CONNECT', 'Now the same two kinds of state with their real names.'))))
# rebuilt (user review): scene phase and process condition as two tracks over the same NPay moments
MOMENTS = [('Launch', ''), ('Using', 'NPay'), ('Notification', 'Center'), ('Home', 'Screen'), ('Minutes', 'later'), ('Memory', 'needed')]
SCENE = ['inactive', 'active', 'inactive', 'background', 'background', 'none']
PROC = ['running', 'running', 'running', 'running briefly', 'suspended', 'terminated']
P = ['<use href="#i-frame" x="0" y="96" width="24" height="24"/><text x="34" y="106">Scene phase</text><text class="sm" x="34" y="126">room lights</text>',
     '<use href="#i-process" x="0" y="186" width="24" height="24"/><text x="34" y="196">Process</text><text class="sm" x="34" y="216">the suite</text>']
for k, (m1, m2) in enumerate(MOMENTS):
    x = 196 + k * 157
    P.append(f'<g class="nd fade" data-lit="{k + 1}"><rect class="sh" x="{x - 6}" y="4" width="157" height="236" rx="14"/></g>')   # band only on the current moment
    P.append(f'<text x="{x + 72}" y="30" text-anchor="middle" style="font-size:17px">{m1}</text><text x="{x + 72}" y="52" text-anchor="middle" style="font-size:17px">{m2}</text>')
    sc, pr = SCENE[k], PROC[k]
    P.append(f'<g class="fade" data-lit="{k + 1}+">'
             f'<g class="nd{" lit" if sc == "active" else " ghost" if sc == "none" else ""}"><rect class="sh" x="{x}" y="84" width="145" height="56" rx="10"/><text x="{x + 72}" y="118" text-anchor="middle">{sc}</text></g>'
             f'<g class="nd{" alert" if pr == "terminated" else ""}"><rect class="sh" x="{x}" y="172" width="145" height="56" rx="10"/><text x="{x + 72}" y="206" text-anchor="middle">{pr}</text></g></g>')
P.append('<g class="fade" data-lit="7+"><path class="wire lit" d="M667 252V262H965V252"/>'
         '<text class="fill-teal" x="816" y="286" text-anchor="middle" style="font-size:18px">same scene phase, different process condition</text></g>')
S.append(slide('Part 3 &middot; Two categories', 'Scene states vs process conditions', f"""  <div class="body">
    {svg('0 0 1136 296', 'Six moments in NPay&rsquo;s day. Scene phase: inactive, active, inactive, background, background, none. Process: running, running, running, running briefly, suspended, terminated.', 'twotracks', P)}{cues(7)}
    <div class="gap"></div>
    <div class="rule step" data-label="Watch the words"><b>Suspended</b> is a process condition. SwiftUI&rsquo;s scenePhase never says &ldquo;suspended&rdquo;.</div>
  </div>""", notes(
    ('SAY', 'Two kinds of state over the same day: the scene phase, the room&rsquo;s lights, and the process, the suite. Click through the moments. Launch: the scene is inactive, the process running. Using NPay: active and running. Pulling down Notification Center: the scene goes inactive, the process keeps running.'),
    ('SAY', 'Home Screen: the scene is in the background; the process may run briefly. Minutes later: the scene still says background, but the process is now suspended, kept in memory with no code running. Memory needed: the process is terminated and there is no scene at all.'),
    ('SAY', 'Click: look at these two moments. Same scene phase, different process condition. That is why we keep the two apart.'),
    ('SAY', 'Click: watch the words. Suspended describes the process, not the scene. People often look for it in SwiftUI&rsquo;s scenePhase, which only has active, inactive and background. Part 4 shows how SwiftUI code reads scenePhase.'),
    ('ASK', 'NPay&rsquo;s scene is in the background. Is NPay&rsquo;s code still running?'),
    ('EXPECT', 'Maybe, briefly. Then the process is usually suspended; scenePhase still says background.'),
    ('CONNECT', 'Now put them together for a typical single-scene iPhone app.'))))
# replaces 0.3's "A typical single-scene iPhone app" (same path as Part 2's preview and the two tracks): what NPay should do at each transition (user review)
TRANS = [('Launch', 'inactive &rarr; active', 'Restore saved data, then refresh the balance'),
         ('A call or Notification Center', 'active &rarr; inactive', 'Pause time-sensitive work'),
         ('Home Screen', 'scene &rarr; background', 'Save the draft; hide the balance from the app-switcher snapshot'),
         ('Minutes later', 'process suspended', 'Nothing: no NPay code runs'),
         ('Memory needed', 'process terminated', 'No warning: anything unsaved is lost'),
         ('User returns', 'scene &rarr; active', 'Refresh: the cached balance may be stale')]
tr_cards = ''.join(f'<div class="card accent step anim-up" style="padding:14px 18px"><span class="label">{k + 1} &middot; {w}</span>'
                   f'<p class="small muted" style="margin:2px 0 6px">{st}</p><p style="margin:0;font-size:20px"><b>{d}</b></p></div>' for k, (w, st, d) in enumerate(TRANS))
S.append(slide('Part 3 &middot; Design', 'Each transition, and what NPay should do', f"""  <div class="body">
    <div class="cols c3" style="gap:16px;align-items:stretch">{tr_cards}</div>
    <div class="gap"></div>
    <div class="rule step" data-label="Design rule">Save as you go. <b>Never wait for a goodbye</b>: termination gives none.</div>
  </div>""", notes(
    ('SAY', 'We know the states. Now the architect&rsquo;s question: what should NPay do at each transition? One per click.'),
    ('SAY', 'One, launch: restore what was saved, then refresh the balance from the server. Two, a phone call or Notification Center makes the scene inactive: pause anything time-sensitive. Three, the Home Screen: the scene goes to the background. Save the draft now, and hide the balance, because iOS takes a snapshot for the app switcher.'),
    ('SAY', 'Four, minutes later the process is suspended: NPay can do nothing, its code does not run. Five, if memory is needed the process is terminated without warning: anything not saved is gone. Six, when the user returns, refresh: a cached balance may be stale.'),
    ('SAY', 'Click: the design rule. Save as you go; never wait for a goodbye, because termination gives none.'),
    ('ASK', 'Where should NPay save the half-filled transfer form?'),
    ('EXPECT', 'As the user types, or at the latest when the scene goes to the background; not in a termination callback.'),
    ('CONNECT', 'Two misconceptions come up at exactly this point.'))))
take(3, 12, 3)   # 0.3's "NPay through five moments" dropped (user): the two-track slide covers it
take(3, 14, 3)

# rebuilt (user review): two phones show what the user finds on return, survived vs terminated
def phone_npay(cx, extra):
    return (f'<text x="{cx}" y="182" text-anchor="middle" style="font-size:15px;font-weight:800">NPay</text>'
            f'<text x="{cx}" y="214" text-anchor="middle" style="font-size:17px;font-weight:700">&#8377;25,000</text>'
            f'<rect class="wire" style="fill:none" x="{cx - 44}" y="230" width="88" height="24" rx="6"/><text class="sm" x="{cx}" y="246" text-anchor="middle">Send &#8377;1,500</text>{extra}')
P = ['<g class="nd"><rect class="sh" x="388" y="0" width="360" height="56" rx="12"/><use href="#i-user" x="402" y="15" width="26" height="26"/>'
     '<text x="440" y="25">The user returns to NPay</text><text class="sm" x="440" y="43">a &#8377;1,500 transfer was half typed</text></g>',
     '<path class="wire" d="M568 56V84H284V112M277 105l7 7 7-7M568 84H852V112M845 105l7 7 7-7"/>',
     '<use href="#d-iphone" x="224" y="118" width="120" height="240"/>', '<use href="#d-iphone" x="792" y="118" width="120" height="240"/>',
     '<g class="fade" data-lit="1+">' + phone_npay(284, '') + '</g>',
     '<g class="nd fade" data-lit="1+"><rect class="sh" x="0" y="190" width="200" height="74" rx="12"/><use href="#i-check" x="12" y="212" width="24" height="24"/>'
     '<text x="44" y="220">Process survived</text><text class="sm" x="44" y="242">all still in memory</text></g>',
     '<g class="fade" data-lit="2+">' + phone_npay(852, '<text class="sm fill-teal" x="852" y="278" text-anchor="middle">updated now</text>') + '</g>',
     '<g class="nd alert fade" data-lit="2+"><rect class="sh" x="936" y="190" width="200" height="74" rx="12"/><use href="#i-cross" x="948" y="212" width="24" height="24"/>'
     '<text x="980" y="220">Process ended</text><text class="sm" x="980" y="242">rebuilt: saved draft</text><text class="sm" x="980" y="258">+ fresh balance</text></g>']
S.append(slide('Part 3 &middot; Example &middot; conceptual', 'Coming back to NPay', f"""  <div class="body">
    {svg('0 0 1136 362', 'The user returns to NPay with a half-typed transfer. If the process survived, the screen is as they left it. If it ended, NPay rebuilds the same screen from the saved draft and a fresh balance.', 'comeback', P, 'max-height:390px')}{cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="Design goal">A well-built NPay looks the <b>same either way</b>: the user should not be able to tell.</div>
  </div>""", notes(
    ('SAY', 'The user was typing a &#8377;1,500 transfer, switched to another app, and now returns. Two things may have happened. Click: the process survived. Everything is still in memory: the balance and the half-typed amount, exactly as they left it.'),
    ('SAY', 'Click: the process was ended while NPay was in the background. A new process starts, and NPay rebuilds the screen: it restores the draft it saved when the scene went to the background, and fetches a fresh balance.'),
    ('SAY', 'Click: the design goal. A well-built NPay looks the same either way; the user should never be able to tell which one happened. That only works if NPay saved the draft in time, the rule from the transitions slide.'),
    ('ASK', 'NPay did not save the draft. The process was ended. What does the user see?'),
    ('EXPECT', 'An empty transfer form: the typed amount is gone. The balance is still fine, because it comes from the server.'),
    ('CONNECT', 'Why would iOS keep a process around but stop it from running?'))))
# NPay put into Part 3's device examples (user review): NPay is the teal app on the device and the one reclaimed under pressure
s17 = rekick(get(3, 17), 3)
for a_, b_ in [('<g class="nd lit"><rect class="sh" x="290"', '<g class="nd"><rect class="sh" x="290"'),
               ('<text class="sm" x="423" y="104" text-anchor="middle">Running</text>', '<text class="sm" x="423" y="104" text-anchor="middle">Running, in front</text>'),
               ('<g class="nd"><rect class="sh" x="580"', '<g class="nd lit"><rect class="sh" x="580"'),
               ('text-anchor="middle">Shopping</text>', 'text-anchor="middle">NPay</text>'),
               ('camera running, shopping suspended', 'camera running in front, NPay suspended')]:
    assert a_ in s17, a_
    s17 = s17.replace(a_, b_)
s17 = re.sub(r'[Ss]hopping', 'NPay', s17)
S.append(s17 + '\n\n')
take(3, 18, 3, subs=[('<div class="cols stretch">', '<div class="cols c3 stretch">'),
                     ('<p>May receive <b>background location updates</b> under appropriate permissions and conditions.</p></div>',
                      '<p>May receive <b>background location updates</b> under appropriate permissions and conditions.</p></div>\n'
                      '      <div class="card accent step"><span class="label">NPay</span><p>Needs <b>neither</b>: it saves on the way out and refreshes when the user returns.</p></div>'),
                     ('<span class="notes-label">SAY</span><p>These are permitted capabilities',
                      '<span class="notes-label">SAY</span><p>Click: and NPay? It needs neither. It does not have to run in the background at all: it saves the draft when the scene goes to the background and refreshes the balance on return, as on the transitions slide.</p>\n    <span class="notes-label">SAY</span><p>Click: these are permitted capabilities')])
s20 = rekick(get(3, 20), 3)
s20 = re.sub(r'Shopping', 'NPay', s20)
s20 = re.sub(r'shopping', 'NPay', s20)
assert 'Messaging and NPay terminated' in s20
S.append(s20 + '\n\n')
take(3, 21, 3, subs=[('<p style="margin:0 0 20px">iOS uses memory-management mechanisms commonly called <b>jetsam</b> to terminate processes when it must manage memory pressure.</p>',
                      '<p style="margin:0 0 20px"><b>Jetsam</b>: how iOS ends processes to get memory back.</p>'),
                     ('<small>A suspended app can be terminated without being resumed.</small>', '<small>NPay gets no chance to run first</small>'),
                     ('<small>The app cannot rely on a last cleanup call.</small>', '<small>no last moment to save</small>'),
                     ('<small>State may need to be reconstructed.</small>', '<small>NPay rebuilds from what it saved</small>'),
                     ('<small>If their memory use becomes problematic.</small>', '<small>if they use too much memory</small>')])
take(3, 23, 3, connect='Let&rsquo;s recap Part 3.')
take(3, 24, 3, connect='Two quick questions on Part 3.')
question(3, 27, 3, 0, 'Next question.')
question(3, 29, 3, 1, 'Part 4: how does NPay&rsquo;s code hear about all these changes?')


# ================================================================== Part 4 · hearing lifecycle events (0.4)
part(4, 'Hearing lifecycle events', 'How a SwiftUI app hears what iOS decides',
     'iOS changes NPay&rsquo;s state. How does our SwiftUI app find out, and react?',
     ('scene', 'view'),
     'Scenes, states, suspension and termination.', 'How a SwiftUI app hears those changes: scenePhase.',
     'The teal is on the scene and on the view: lifecycle events arrive at the scene, and SwiftUI views can read them.')
# rebuilt (user: focus on SwiftUI; the flow diagram was confusing): three phones show what the user does, the scenePhase value, and NPay's reaction
def npay_screen(c, dy=0):
    return (f'<text x="{c}" y="{66 + dy}" text-anchor="middle" style="font-size:14px;font-weight:800">NPay</text>'
            f'<text x="{c}" y="{96 + dy}" text-anchor="middle" style="font-size:16px;font-weight:700">&#8377;25,000</text>'
            f'<rect class="wire" style="fill:none" x="{c - 36}" y="{110 + dy}" width="72" height="20" rx="6"/><text class="sm" x="{c}" y="{124 + dy}" text-anchor="middle" style="font-size:9px">Refresh balance</text>')
PH = [(190, 'active', 'refresh the balance', npay_screen(190)),
      (568, 'inactive', 'pause time-sensitive work', npay_screen(568, 64) + '<rect class="mute" x="522" y="18" width="92" height="86" rx="10"/>'
            + ''.join(f'<rect class="wire faint" style="fill:none" x="532" y="{y0}" width="72" height="14" rx="4"/>' for y0 in (32, 52, 72))),
      (946, 'background', 'save the draft, hide the balance', ''.join(f'<rect class="mute" x="{902 + cx_ * 30}" y="{30 + ry * 32}" width="22" height="22" rx="5"/>' for ry in range(4) for cx_ in range(3)))]
P = []
for k, (c, v, r, screen) in enumerate(PH):
    P.append(f'<use href="#d-iphone" x="{c - 55}" y="0" width="110" height="220"/>')
    P.append(f'<g class="fade" data-lit="{k + 1}+">{screen}'
             f'<text class="mono" x="{c}" y="246" text-anchor="middle">SCENEPHASE</text></g>')
    P.append(f'<g class="fade" data-lit="{k + 1}+"><rect class="wire" style="fill:none" x="{c - 90}" y="256" width="180" height="40" rx="10"/><text x="{c}" y="282" text-anchor="middle" style="font-size:19px;font-weight:700">{v}</text></g>')
    P.append(f'<g class="nd fade" data-lit="{k + 1}"><rect class="sh" x="{c - 90}" y="256" width="180" height="40" rx="10"/><text x="{c}" y="282" text-anchor="middle" style="font-size:19px;font-weight:700">{v}</text></g>')   # teal only while current
    P.append(f'<text class="fade" data-lit="{k + 1}+" x="{c}" y="326" text-anchor="middle" style="font-size:17px">NPay: <tspan style="font-weight:700">{r}</tspan></text>')
for k, (x1, x2, l1, l2) in enumerate([(262, 494, 'pulls down', 'Notification Center'), (640, 872, 'goes to the', 'Home Screen')]):
    P.append(f'<g class="fade" data-lit="{k + 2}+"><path class="wire" d="M{x1} 110H{x2}M{x2 - 7} 103l7 7-7 7"/>'
             f'<text class="sm" x="{(x1 + x2) // 2}" y="84" text-anchor="middle">the user {l1}</text><text class="sm" x="{(x1 + x2) // 2}" y="100" text-anchor="middle">{l2}</text></g>')
S.append(slide('Part 4 &middot; SwiftUI lifecycle', 'How a SwiftUI app hears lifecycle events', f"""  <div class="body">
    {svg('0 0 1136 336', 'NPay on screen: scenePhase active, NPay refreshes. Notification Center pulled down: inactive, NPay pauses time-sensitive work. Home Screen: background, NPay saves the draft and hides the balance.', 'hear3', P, 'max-height:390px')}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="One value">SwiftUI tells NPay what happened through one value, <b>scenePhase</b>. There is no &ldquo;suspended&rdquo;: a suspended app runs no code.</div>
  </div>""", notes(
    ('SAY', 'How does our SwiftUI app hear what iOS decides? Through one value, scenePhase. Watch three moments. Click one: NPay is on screen and the user can touch it; scenePhase is active. NPay refreshes the balance.'),
    ('SAY', 'Click two: the user pulls down Notification Center over NPay. NPay is still visible but gets no touches; scenePhase is inactive. NPay pauses anything time-sensitive.'),
    ('SAY', 'Click three: the user goes to the Home Screen. NPay is not visible; scenePhase is background. NPay saves the draft and hides the balance, because iOS takes a snapshot for the app switcher.'),
    ('SAY', 'Click: so SwiftUI reports every change through this one value, with exactly three possibilities. There is no suspended: that is the process, and a suspended app runs no code to hear anything.'),
    ('ASK', 'Can NPay use scenePhase to find out that it is about to be suspended?'),
    ('EXPECT', 'No. It hears background; suspension follows without any value or callback.'),
    ('CONNECT', 'Where should NPay read scenePhase: in a view, or in the App?'))))
# SwiftUI only (user): 0.4's UIKit slides dropped (delegate flow, two windows, comparison, event map, choosing)
# rebuilt (user review, concrete style): an iPad with two NPay windows shows what a View and the App each read
P = ['<rect class="wire" style="fill:none;stroke-width:4" x="2" y="2" width="636" height="376" rx="30"/>',
     '<text class="mono" x="24" y="34">IPAD &#183; ONE NPAY PROCESS</text>',
     '<g class="nd"><rect class="sh" x="24" y="50" width="420" height="306" rx="16"/><text class="mono" x="44" y="80">WINDOW A &#183; ON SCREEN</text>'
     '<text x="234" y="140" text-anchor="middle" style="font-size:18px;font-weight:800">NPay</text>'
     '<text class="sm" x="234" y="172" text-anchor="middle">Available balance</text>'
     '<text x="234" y="210" text-anchor="middle" style="font-size:26px;font-weight:700">&#8377;25,000</text></g>',
     '<g class="nd ghost"><rect class="sh" x="466" y="110" width="150" height="190" rx="14"/><text class="mono" x="541" y="140" text-anchor="middle">WINDOW B</text>'
     '<text x="541" y="196" text-anchor="middle">Transfer</text><text class="sm" x="541" y="218" text-anchor="middle">in the background</text></g>',
     '<g class="nd fade" data-lit="1"><rect class="sh" x="84" y="282" width="300" height="48" rx="12"/><text x="234" y="312" text-anchor="middle">its View reads: active</text></g>',
     '<g class="fade" data-lit="2+"><rect class="wire" style="fill:none" x="84" y="282" width="300" height="48" rx="12"/><text x="234" y="312" text-anchor="middle">its View reads: active</text></g>',
     '<g class="nd fade" data-lit="2"><rect class="sh" x="476" y="236" width="130" height="52" rx="10"/><text class="sm" x="541" y="258" text-anchor="middle">its View reads:</text><text x="541" y="278" text-anchor="middle">background</text></g>',
     '<g class="fade" data-lit="3+"><rect class="wire" style="fill:none" x="476" y="236" width="130" height="52" rx="10"/><text class="sm" x="541" y="258" text-anchor="middle">its View reads:</text><text x="541" y="278" text-anchor="middle">background</text></g>',
     '<g class="nd fade" data-lit="3+"><rect class="sh" x="2" y="396" width="636" height="52" rx="12"/><use href="#i-process" x="18" y="409" width="26" height="26"/>'
     '<text x="56" y="420">The App reads: active</text><text class="sm" x="56" y="438">at least one window is active</text></g>']
where_cards = ''.join(f'<div class="card accent step anim-up" style="margin:0 0 14px"><span class="label">{t}</span><p style="margin:2px 0 6px;font-size:21px"><b>{a}</b></p><p class="small muted" style="margin:0">{e}</p></div>'
                      for t, a, e in [('Read in a View', 'this window only', 'e.g. pause this screen&rsquo;s timer'),
                                      ('Read in the App', 'all windows combined', 'e.g. lock NPay when every window has left')])
S.append(slide('Part 4 &middot; Where you read it', 'scenePhase in a View vs in the App', f"""  <div class="body cols middle" style="grid-template-columns:1.25fr 1fr">
    {svg('0 0 640 450', 'An iPad with one NPay process: window A on screen, its view reads active; window B in the background, its view reads background; the App reads active because at least one window is active.', 'ipad2', P, 'max-height:440px')}{cues(3)}
    <div>{where_cards}</div>
  </div>""", notes(
    ('SAY', 'On iPad, NPay can have two windows: the balance on screen, and a transfer the user moved to the background. One process, two scenes. Click one: a view inside window A reads active.'),
    ('SAY', 'Click two: a view inside window B reads background. Click three: the App reads the combined value, active, because at least one window is active. The App only reports background when every window has left the screen.'),
    ('SAY', 'Click: so read it in a view for work that belongs to that window, such as pausing that screen&rsquo;s timer. Click: read it in the App for work that concerns all of NPay, such as locking it when every window has gone.'),
    ('ASK', 'Where should NPay hide the balance before the app-switcher snapshot?'),
    ('EXPECT', 'In the view that shows the balance: that window&rsquo;s own scene goes to the background.'),
    ('CONNECT', 'Let&rsquo;s recap Part 4.'))))
take(4, 24, 4, connect='Two quick questions on Part 4.',
     subs=[('UIKit: SceneDelegate &middot; SwiftUI: scenePhase', 'SwiftUI reports it through scenePhase'),
           ('delivered by SceneDelegate in UIKit and scenePhase in SwiftUI', 'which SwiftUI reports through scenePhase')])
question(4, 27, 4, 0, 'Next question.')
question(4, 29, 4, 1, 'Part 5: inside the running app, the thread that does all the UI work.')


# ================================================================== Part 5 · main thread & rendering (0.5)
part(5, 'Main thread &amp; rendering', 'RunLoop, events, frames, and where work belongs',
     'Every tap, every frame and every UI update goes through one thread. This Part is about keeping it free.',
     ('thread',),
     'How the app hears lifecycle events.', 'The main thread: RunLoop, events, frames and where work belongs.',
     'The teal is on the main thread, inside NPay&rsquo;s process.')
# rebuilt (user review, concrete style): the head chef as two lanes over time, one Refresh balance tap handed to the back and returned
P = ['<text x="0" y="62">Main thread</text><text class="sm" x="0" y="82">the head chef</text>',
     '<text x="0" y="222">Background</text><text class="sm" x="0" y="242">the prep cooks</text>',
     '<path class="wire faint" d="M190 72H1136M190 232H1136"/>']
MAIN = [(200, 210, 'Tap: Refresh balance', '1'), (430, 130, 'Scroll', None), (580, 150, 'Draw frame', None), (750, 130, 'Scroll', None)]
for x, w, t, l in MAIN:
    cls = 'nd fade' if l else 'fade'
    inner = (f'<rect class="sh" x="{x}" y="46" width="{w}" height="52" rx="12"/>' if l else f'<rect class="wire" style="fill:none" x="{x}" y="46" width="{w}" height="52" rx="12"/>')
    P.append(f'<g class="{cls}" data-lit="{"1" if l else "1+"}">{inner}<text x="{x + w / 2:g}" y="78" text-anchor="middle">{t}</text></g>')
P.append('<g class="fade" data-lit="2+"><rect class="wire" style="fill:none" x="200" y="46" width="210" height="52" rx="12"/><text x="305" y="78" text-anchor="middle">Tap: Refresh balance</text></g>')
P.append('<g class="fade" data-lit="2+"><path class="wire" d="M305 98V198M298 191l7 7 7-7"/><text class="sm" x="314" y="150">hand off</text></g>')
P.append('<g class="nd fade" data-lit="2"><rect class="sh" x="290" y="204" width="610" height="56" rx="12"/><use href="#i-globe" x="306" y="219" width="26" height="26"/><text x="344" y="238">Fetch the balance from the bank: mostly waiting</text></g>')
P.append('<g class="fade" data-lit="3+"><rect class="wire" style="fill:none" x="290" y="204" width="610" height="56" rx="12"/><use href="#i-globe" x="306" y="219" width="26" height="26"/><text x="344" y="238">Fetch the balance from the bank: mostly waiting</text></g>')
P.append('<g class="fade" data-lit="3+"><path class="wire" d="M900 232H1015V104M1008 111l7-7 7 7"/><text class="sm" x="1024" y="170">result</text></g>')
P.append('<g class="nd fade" data-lit="3+"><rect class="sh" x="910" y="46" width="220" height="52" rx="12"/><text x="1020" y="78" text-anchor="middle">Show &#8377;24,750</text></g>')
for k, cap in enumerate(['The main thread works one order at a time: taps, scrolling, drawing frames',
                         'Fetching is slow waiting, so it goes to the back; the main thread keeps scrolling and drawing',
                         'When the answer arrives, the main thread updates the screen']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="306" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 5 &middot; Main thread &middot; conceptual', 'The main thread is the head chef', f"""  <div class="body">
    {svg('0 0 1136 320', 'The main thread handles a Refresh balance tap, scrolling and drawing frames; fetching the balance is handed to the background; when it returns, the main thread shows the new balance.', 'chef2', P)}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Rule">Keep the main thread <b>free</b>. Slow work goes to the back; only screen updates come back to it.</div>
  </div>""", notes(
    ('SAY', 'Inside the NPay process is a kitchen. One head chef, the main thread, plates every dish the guests see. Prep cooks in the back, background work, do the slow jobs. Click one: the main thread works through orders one at a time: the user taps Refresh balance, scrolls, and frames are drawn.'),
    ('SAY', 'Click two: fetching the balance from the bank is slow, mostly waiting, so it is handed to the back. Meanwhile the main thread keeps scrolling and drawing: the app stays smooth.'),
    ('SAY', 'Click three: when the answer arrives, it comes back to the main thread, which shows the new balance. Screen updates always happen on the main thread.'),
    ('SAY', 'Click: the rule. Keep the main thread free. If the head chef stopped to bake bread from scratch, every order on the rail would wait: that is a frozen app.'),
    ('ASK', 'What happens to other taps while a button action does three seconds of work on the main thread?'),
    ('EXPECT', 'They wait. The head chef is busy baking bread.'),
    ('CONNECT', 'Where does the main thread live? Inside the process.'))))
take(5, 7, 5, subs=[   # Part 5 re-check: no Swift tasks yet (Unit 01 · 1.9); NPay's own threads instead
    ('<p class="small">Threads <b>share</b> the process&rsquo;s address space; each has its <b>own stack</b> and scheduling state.</p>',
     '<p class="small">Threads <b>share</b> NPay&rsquo;s memory; each follows <b>its own steps</b>, and iOS decides when each one runs.</p>'),
    ('<div class="rule step" data-label="Modern Swift">An asynchronous Swift <b>task is not a thread</b>. Tasks can suspend without blocking an OS thread.</div>',
     '<div class="rule step" data-label="In NPay">The <b>main thread</b> handles taps and frames; <b>other threads</b> do networking and decoding. All share NPay&rsquo;s memory.</div>'),
    ('<span class="notes-label">SAY</span><p>For modern Swift: an asynchronous task is not the same thing as a thread. Swift concurrency schedules tasks onto executors, and tasks may suspend without blocking an operating-system thread. We return to this shortly.</p>',
     '<span class="notes-label">SAY</span><p>Click: in NPay, the main thread handles taps and draws frames, while other threads do work such as networking and decoding the response. They all share NPay&rsquo;s memory, which is why Part 6 matters. How Swift moves work between threads is Unit 01, lesson 1.9.</p>')])

# rebuilt (user: "no clarity of what a RunLoop is"): the main thread as a timeline: sleep, wake on an event, run, sleep again; then the slow case
def seg(x, w, y, t, kind, lit_):
    """kind: sleep (dashed), run (tile), alert (orange tile)"""
    if kind == 'sleep':
        return (f'<g class="fade" data-lit="{lit_}"><rect class="wire dash" style="fill:none" x="{x}" y="{y}" width="{w}" height="52" rx="10"/>'
                f'<text class="sm" x="{x + w / 2:g}" y="{y + 32}" text-anchor="middle">{t}</text></g>')
    cls = 'nd alert fade' if kind == 'alert' else 'nd fade'
    return (f'<g class="{cls}" data-lit="{lit_}"><rect class="sh" x="{x}" y="{y}" width="{w}" height="52" rx="10"/>'
            f'<text x="{x + w / 2:g}" y="{y + 32}" text-anchor="middle">{t}</text></g>')
def plain(x, w, y, t, lit_):
    return (f'<g class="fade" data-lit="{lit_}"><rect class="wire" style="fill:none" x="{x}" y="{y}" width="{w}" height="52" rx="10"/>'
            f'<text x="{x + w / 2:g}" y="{y + 32}" text-anchor="middle">{t}</text></g>')
def event(x, icon, label, y_to, lit_):
    return (f'<g class="fade" data-lit="{lit_}"><use href="#i-{icon}" x="{x - 13}" y="22" width="26" height="26"/>'
            f'<text class="sm" x="{x}" y="66" text-anchor="middle">{label}</text><path class="wire" d="M{x} 74V{y_to - 4}M{x - 6} {y_to - 11}l6 7 6-7"/></g>')
P = ['<text class="mono" x="0" y="20">THE LOOP</text>',
     row(0, 40, 176, 52, 'clock', 'Sleep', '', '1 3'), wire('M88 94V116') + wire(head(88, 116, 'd')),
     row(0, 120, 176, 52, 'tap', 'Event', '', '2'), wire('M88 174V196') + wire(head(88, 196, 'd')),
     row(0, 200, 176, 52, 'code', 'Run code', '', '2'),
     wire('M178 226H198V66H184') + wire(head(184, 66, 'l')),
     '<text class="sm" x="88" y="282" text-anchor="middle">again, forever</text>',
     '<path class="wire faint" d="M214 10V300"/>',
     '<text class="mono" x="1136" y="20" text-anchor="end">THE MAIN THREAD OVER TIME</text>',
     '<text class="sm" x="1136" y="200" text-anchor="end">time &#8594;</text>',
     seg(236, 135, 126, 'sleeping', 'sleep', '1+'),
     event(371, 'tap', 'tap: Refresh balance', 126, '2+'),
     seg(371, 206, 126, 'NPay&#8217;s Refresh runs', 'run', '2'), plain(371, 206, 126, 'Refresh runs', '3+'),
     seg(577, 94, 126, 'sleeping', 'sleep', '3+'),
     event(686, 'grid', 'scroll', 126, '3+'), plain(681, 141, 126, 'move the list', '3+'),
     event(850, 'clock', 'timer', 126, '3+'), plain(830, 141, 126, 'update clock', '3+'),
     seg(979, 157, 126, 'sleeping', 'sleep', '3+'),
     '<text class="mono fade" data-lit="4+" x="236" y="208">IF NPAY&#8217;S CODE IS SLOW</text>',
     seg(236, 135, 216, 'sleeping', 'sleep', '4+'),
     seg(371, 450, 216, 'Refresh blocks for 3 seconds', 'alert', '4+'),
     '<g class="fade" data-lit="4+"><use href="#i-tap" x="440" y="274" width="22" height="22"/><text class="sm" x="468" y="291">a new tap arrives &#8230; and waits</text></g>',
     plain(821, 188, 216, 'the tap runs, late', '4+')]
for k, cap in enumerate(['Nothing to do: the main thread sleeps, using no CPU or battery',
                         'A tap wakes it, and NPay&#8217;s Refresh action runs',
                         'Then it sleeps again, until the next event: a scroll, a timer',
                         'But while NPay&#8217;s code runs, new events can only wait']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="686" y="326" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 5 &middot; RunLoop &middot; conceptual', 'What is a RunLoop?', f"""  <div class="body">
    <p class="lead" style="margin:0 0 8px;font-size:22px">It keeps the main thread alive: <b>sleep</b> until something happens, <b>handle</b> it, sleep again.</p>
    {svg('0 0 1136 336', 'Left: the loop, sleep, event, run code, again. Right: the main thread over time: sleeping, woken by a tap to run NPay&rsquo;s Refresh action, sleeping, a scroll and a timer, sleeping. Below, a slow Refresh blocks for three seconds while a new tap waits.', 'runloop3', P)}{cues(4)}
    <div class="rule step" data-label="RunLoop: wait &rarr; handle &rarr; wait">The next event runs only when <b>your code returns</b>.</div>
  </div>""", notes(
    ('SAY', 'What is a RunLoop? Without one, a thread runs its code once and ends. The main thread must stay alive for as long as NPay is open, waiting for the user. The RunLoop is the loop that keeps it alive: it sleeps until something happens, handles it, then sleeps again.'),
    ('SAY', 'Watch the main thread over time. Click one: nothing to do, so it sleeps; no CPU, no battery. Click two: the user taps Refresh balance; the event wakes the thread and NPay&rsquo;s Refresh action runs. Click three: when the action returns, the thread sleeps again, until the next event: a scroll moves the list, a timer updates the clock, and back to sleep. That cycle, wait, handle, wait, is the RunLoop.'),
    ('SAY', 'Click four: the slow case. If NPay&rsquo;s Refresh action blocks for three seconds, the RunLoop cannot take the next event. A new tap arrives and simply waits; it runs late. To the user, the app is frozen.'),
    ('SAY', 'Click: so the RunLoop takes the next event only when our code returns. Keep main-thread code short. In the head-chef picture, the RunLoop is the order rail: one ticket at a time.'),
    ('ASK', 'NPay is open and the user is not touching it. Is the main thread busy?'),
    ('EXPECT', 'No. It sleeps in its RunLoop until the next event wakes it.'),
    ('CONNECT', 'Now follow one tap all the way through.'))))
# rebuilt (Part 5 audit): one tap through three owner lanes, the teal moving step by step, one NPay caption per click
TAP8 = [(0, 'tap', 'Touch', 'Your finger touches the glass: the hardware detects it'),
        (0, 'kernel', 'Event', 'iOS turns it into a touch event for NPay'),
        (1, 'clock', 'Wake up', 'NPay&#8217;s main thread wakes in its RunLoop and takes the event'),
        (1, 'eye', 'Find button', 'Which button is under the finger? Refresh balance'),
        (1, 'code', 'Run action', 'NPay&#8217;s Refresh action runs'),
        (1, 'diff', 'New state', 'NPay&#8217;s balance state changes'),
        (2, 'layout', 'Diff views', 'SwiftUI works out what changed on screen'),
        (2, 'frame', 'New frame', 'The next frame shows the new balance')]
LANES = [('iOS', 'hardware &#183; system'), ('NPay&#8217;s main thread', 'your code runs here'), ('SwiftUI', 'updates the screen')]
P = []
for r, (t, sub) in enumerate(LANES):
    y = 10 + r * 92
    P.append(f'<text x="0" y="{y + 30}">{t}</text><text class="sm" x="0" y="{y + 50}">{sub}</text><path class="wire faint" d="M164 {y + 28}H1136"/>')
prev = None
for k, (r, ic, t, cap) in enumerate(TAP8):
    x, y = 164 + k * 121, 10 + r * 92
    if prev:
        px, py = prev
        P.append(wire(f'M{px + 116} {py + 28}H{x}' if py == y else f'M{px + 58} {py + 56}V{y + 28}H{x}'))
    P.append(f'<g class="nd" data-lit="{k + 1}{"+" if k == 7 else ""}"><rect class="sh" x="{x}" y="{y}" width="116" height="56" rx="10"/>'
             f'<use href="#i-{ic}" x="{x + 8}" y="{y + 16}" width="22" height="22"/><text class="sm" x="{x + 36}" y="{y + 33}">{t}</text></g>')
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 7 else ""}" x="568" y="300" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
    prev = (x, y)
S.append(slide('Part 5 &middot; Event journey &middot; conceptual', 'One tap, eight steps', f"""  <div class="body">
    {svg('0 0 1136 312', 'One tap: the hardware and iOS deliver a touch event; NPay&rsquo;s main thread wakes, finds the button, runs the action and changes state; SwiftUI updates the view and the next frame shows it.', 'tap8', P)}{cues(8)}
    <p class="small muted" style="margin:10px 0 0">Simplified: NPay never reads raw touchscreen hardware; iOS and the frameworks handle that.</p>
  </div>""", notes(
    ('SAY', 'One tap on Refresh balance, followed through three owners: iOS, NPay&rsquo;s main thread, and SwiftUI. One step per click.'),
    ('SAY', 'One: the finger touches the glass and the hardware detects it. Two: iOS turns that into a touch event for NPay. Three: NPay&rsquo;s main thread wakes in its RunLoop and takes the event. Four: which button is under the finger? Refresh balance.'),
    ('SAY', 'Five: NPay&rsquo;s Refresh action runs: our code. Six: the balance state changes. Seven: SwiftUI works out what changed on screen. Eight: the next frame shows the new balance.'),
    ('SAY', 'Steps three to six all happen on the main thread. That is why the action in step five must be quick.'),
    ('CONNECT', 'What happens if the action in step five takes too long?'))))

# rebuilt (user review, concrete style): the user's view of a 3-second Refresh, blocking vs not blocking
def freeze_phone(c, mode):
    o = [f'<use href="#d-iphone" x="{c - 65}" y="34" width="130" height="260"/>',
         f'<text x="{c}" y="86" text-anchor="middle" style="font-size:15px;font-weight:800">NPay</text>',
         (f'<text x="{c}" y="116" text-anchor="middle" style="font-size:17px;font-weight:700">&#8377;25,000</text>' if mode == 'block' else
          f'<g class="fade" data-lit="2"><text x="{c}" y="116" text-anchor="middle" style="font-size:17px;font-weight:700">&#8377;25,000</text></g>'
          f'<g class="fade" data-lit="3+"><text class="fill-teal" x="{c}" y="116" text-anchor="middle" style="font-size:17px;font-weight:700">&#8377;24,750</text></g>')]
    if mode == 'block':
        o.append(f'<rect class="wire" style="fill:none" x="{c - 44}" y="128" width="88" height="22" rx="6"/><text class="sm" x="{c}" y="143" text-anchor="middle" style="font-size:10px">Refresh balance</text>')
        o += [f'<rect class="mute" x="{c - 46}" y="{y0}" width="92" height="20" rx="4"/>' for y0 in (164, 190, 216)]
        o.append(f'<use href="#i-tap" x="{c + 14}" y="180" width="24" height="24"/><text class="sm" x="{c}" y="262" text-anchor="middle">no response</text>')
    else:
        o.append(f'<g class="fade" data-lit="2"><text class="sm fill-teal" x="{c}" y="143" text-anchor="middle">Updating&#8230;</text></g>'
                 f'<g class="fade" data-lit="3+"><text class="sm fill-teal" x="{c}" y="143" text-anchor="middle">updated</text></g>')
        o += [f'<rect class="mute" x="{c - 46}" y="{y0}" width="92" height="20" rx="4"/>' for y0 in (158, 184, 210)]
        o.append(f'<path class="wire" d="M{c + 54} 214V166M{c + 48} 172l6-6 6 6"/><text class="sm fill-teal" x="{c}" y="262" text-anchor="middle">still scrolls</text>')
    return ''.join(o)
P = []
for k, (c, mode, title, bar, cap) in enumerate([(284, 'block', 'BLOCKING WAIT &#183; HOLDS THE MAIN THREAD', 'main thread blocked: 3 s', 'Taps and scrolls wait: the app looks frozen'),
                                               (852, 'free', 'NON-BLOCKING WAIT &#183; HANDED OFF', 'main thread free', 'Taps and scrolls still work')]):
    barc = 'nd alert' if mode == 'block' else 'nd lit'
    P.append(f'<g class="fade" data-lit="{k + 1}+"><text class="mono" x="{c}" y="18" text-anchor="middle">{title}</text>{freeze_phone(c, mode)}'
             f'<g class="{barc}"><rect class="sh" x="{c - 200}" y="310" width="400" height="32" rx="8"/><text class="sm" x="{c}" y="331" text-anchor="middle">{bar}</text></g>'
             f'<text x="{c}" y="370" text-anchor="middle" style="font-size:18px">{cap}</text></g>')
S.append(slide('Part 5 &middot; Blocking vs non-blocking', 'Blocking vs non-blocking waits', f"""  <div class="body">
    {svg('0 0 1136 380', 'Blocking vs non-blocking. Two phones press Refresh balance. Left: the 3-second wait blocks the main thread, taps get no response. Right: the wait is handed off, the phone shows Updating and still scrolls.', 'freeze2', P, 'max-height:410px')}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Same wait">Same 3-second wait. Only <b>where it happens</b> decides whether the app freezes.</div>
  </div>""", notes(
    ('SAY', 'Blocking versus non-blocking, seen by the user. Blocking: the code waits while holding the main thread, so nothing else can run there. Non-blocking: it starts the wait, lets go of the main thread, and comes back when the answer arrives. Both phones press Refresh balance, and both have to wait about three seconds for the bank. Click: on the left, the Refresh action waits on the main thread. The user taps a transaction, tries to scroll: no response. The app looks frozen.'),
    ('SAY', 'Click: on the right, the wait is handed off, as on the head-chef slide. The screen shows Updating, and the list still scrolls and responds to taps. The main thread is free.'),
    ('SAY', 'Click: three seconds later the answer arrives. The main thread, free all along, shows the new balance, &#8377;24,750. Non-blocking does not mean the wait is skipped: the result still comes back.'),
    ('SAY', 'Click: same three-second wait in both. Only where it happens decides whether the app freezes. Unit 01 shows the Swift for both.'),
    ('ASK', 'Which version would you ship in a banking app?'),
    ('EXPECT', 'The right one: the user sees progress and the app stays responsive.'),
    ('CONNECT', '&ldquo;Background&rdquo; is a word we use for three different things.'))))
# 0.5's "Main thread vs MainActor" dropped (user: actors appeared without introduction; Unit 01 · 1.9 teaches them)
take(5, 19, 5, subs=[   # shortened to NPay examples (Part 5 audit)
    ('<span class="label">Asynchronous I/O</span>', '<span class="label">1 &middot; Waiting</span>'),
    ('<span class="label">CPU-bound parallel work</span>', '<span class="label">2 &middot; Computing</span>'),
    ('<span class="label">iOS background execution</span>', '<span class="label">3 &middot; After the user leaves</span>'),
    ('<p>Network requests that <b>wait without occupying a thread</b>. Most file APIs are <b>synchronous</b>: keep large reads and writes off the main actor.</p>',
     '<p>Fetching NPay&rsquo;s balance from the bank.</p><p class="small muted" style="margin:6px 0 0">No thread sits idle while it waits.</p>'),
    ('<p>Image processing, data transformation and expensive calculations that need <b>CPU time away from the main actor</b>.</p>',
     '<p>Sorting a year of NPay transactions.</p><p class="small muted" style="margin:6px 0 0">Needs CPU time away from the main thread.</p>'),
    ('<p>Work allowed while the app is <b>no longer foreground</b>, subject to system policies and capabilities.</p>',
     '<p>Finishing an upload NPay started.</p><p class="small muted" style="margin:6px 0 0">Only with iOS&rsquo;s permission, as in Part 3.</p>'),
    ('An async task does <b>not</b> mean iOS will let it continue after the app is suspended.', 'Handing work off does <b>not</b> keep it running after iOS suspends NPay.')])
S[-1] = re.sub(r'<aside class="notes-src">.*?</aside>', notes(
    ('SAY', 'People say &ldquo;background&rdquo; for three different things. Click: one, waiting, such as fetching the balance from the bank; while it waits, no thread sits idle. Click: two, computing, such as sorting a year of transactions; that needs real CPU time, away from the main thread.'),
    ('SAY', 'Click: three, after the user leaves: finishing an upload NPay started. That is iOS background execution, allowed only with iOS&rsquo;s permission, as in Part 3.'),
    ('SAY', 'Click: so handing work off the main thread does not keep it running after iOS suspends NPay. Different problems, different solutions.'),
    ('CONNECT', 'Now the deadline the main thread is racing against: the frame.')).strip(), S[-1], count=1, flags=re.S)
# rebuilt (user review, concrete style): NPay's list scrolling against the display's ticks; 60 Hz, 120 Hz, then a missed tick
X0, X1 = 196, 1136
def mini(x, off, cls=''):
    """one frame of NPay's scrolling list: three rows moved up by `off`"""
    rows_ = ''.join(f'<rect class="mute" x="{x + 10}" y="{76 + 12 * r - off}" width="96" height="8" rx="3"/>' for r in range(5) if 64 < 76 + 12 * r - off < 118)
    box = (f'<rect class="sh" x="{x}" y="62" width="116" height="66" rx="8"/>' if 'alert' in cls else
           f'<rect class="wire" style="fill:none" x="{x}" y="62" width="116" height="66" rx="8"/>')
    return f'<g class="{cls}">{box}{rows_}</g>'
P = ['<text x="0" y="40">60 Hz</text><text class="sm" x="0" y="60">a frame every</text><text class="sm" x="0" y="78">16.67 ms</text>',
     f'<g class="fade" data-lit="1+"><path class="wire" d="M{X0} 40H{X1}"/>' +
     ''.join(f'<path class="wire" d="M{X0 + k * 156:g} 30V50"/>' for k in range(7)) +
     '<text class="sm" x="1136" y="22" text-anchor="end">one tenth of a second &#8594;</text></g>']
frames = ''.join(mini(X0 + 20 + k * 156, k * 6) for k in range(6))
P.append(f'<g class="fade" data-lit="2-3">{frames}</g>')
late = ''.join(mini(X0 + 20 + k * 156, (k if k < 3 else k - 1) * 6, 'nd alert' if k == 3 else '') for k in range(6))
P.append(f'<g class="fade" data-lit="4+">{late}<text class="sm" x="{X0 + 20 + 3 * 156 + 58}" y="146" text-anchor="middle">late: the old frame stays</text></g>')
P.append('<g class="fade" data-lit="3+"><text x="0" y="200">120 Hz</text><text class="sm" x="0" y="220">a frame every</text><text class="sm" x="0" y="238">8.33 ms</text>'
         f'<path class="wire" d="M{X0} 200H{X1}"/>' + ''.join(f'<path class="wire" d="M{X0 + k * 78:g} 190V210"/>' for k in range(13)) +
         f'<text class="sm" x="{(X0 + X1) // 2}" y="236" text-anchor="middle">twice the deadlines, each half as long</text></g>')
for k, cap in enumerate(['The display wants a new picture at every tick: 60 times a second',
                         'Scrolling NPay&#8217;s list: a new frame is ready at every tick, so it looks smooth',
                         'ProMotion iPhones go up to 120 Hz: twice the ticks, half the time for each',
                         'One frame is not ready in time: the old picture stays one tick longer, a stutter']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="666" y="290" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 5 &middot; Frame budget &middot; illustrative', 'One refresh, one deadline', f"""  <div class="body">
    {svg('0 0 1136 300', 'NPay&rsquo;s list scrolling, one frame per display tick: 60 Hz ticks every 16.67 ms, 120 Hz ticks every 8.33 ms; one late frame repeats the old picture.', 'ticks', P)}{cues(4)}
    <div class="gap"></div>
    <div class="rule step" data-label="Deadline">Every tick is a deadline, and NPay only gets <b>part</b> of it: the system needs time to draw too.</div>
  </div>""", notes(
    ('SAY', 'Why does the main thread have to be quick? Because the screen keeps asking for new pictures. Click: at 60 Hz the display refreshes 60 times a second, a tick every 16.67 milliseconds. Here is one tenth of a second.'),
    ('SAY', 'Click: the user scrolls NPay&rsquo;s transaction list. At every tick a new frame is ready, the rows a little higher each time: that is what smooth looks like. Click: ProMotion iPhones go up to 120 Hz while scrolling, twice as many ticks, each deadline half as long, 8.33 milliseconds.'),
    ('SAY', 'Click: one frame is not ready in time, because the main thread was busy. The display shows the old picture for one more tick: the user sees a stutter.'),
    ('SAY', 'Click: every tick is a deadline, and NPay does not even get the whole interval: the system also needs time for layout, rendering and compositing.'),
    ('ASK', 'Is the same work more likely to stutter at 60 Hz or at 120 Hz?'),
    ('EXPECT', 'At 120 Hz: each deadline is half as long.'),
    ('CONNECT', 'So what actually happens between a state change and new pixels?'))))
# rebuilt (user review, concrete style): an update redraws only what changed; one stage per click, NPay's phone beside it
UPD = [('diff', 'State changes', 'new balance', 'A &#8377;250 coffee payment: the balance becomes &#8377;24,750 in memory'),
       ('eye', 'Evaluate', 'read description', 'SwiftUI reads the dashboard&#8217;s description again'),
       ('diff', 'Reconcile', 'what changed', 'Compared with last time, only two things changed'),
       ('layout', 'Layout', 'size &amp; place', 'Makes room for the new row'),
       ('layers', 'Graphics', 'redraw changes', 'Redraws only the changed parts'),
       ('frame', 'Display', 'next frame', 'The next frame shows &#8377;24,750')]
P = []
for k, (ic, t, sub, cap) in enumerate(UPD):
    x = 12 + k * 192
    P.append(f'<g class="nd" data-lit="{k + 1}{"+" if k == 5 else ""}"><rect class="sh" x="{x}" y="10" width="152" height="104" rx="14"/>'
             f'<use href="#i-{ic}" x="{x + 62}" y="24" width="28" height="28"/><text x="{x + 76}" y="78" text-anchor="middle">{t}</text>'
             f'<text class="sm" x="{x + 76}" y="98" text-anchor="middle">{sub}</text></g>')
    if k < 5:
        P.append(f'<path class="wire" d="M{x + 160} 62H{x + 184}M{x + 178} 56l6 6-6 6"/>')
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 5 else ""}" x="460" y="168" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
cx = 1050
P.append('<use href="#d-iphone" x="990" y="128" width="120" height="240"/>')
P.append(f'<text x="{cx}" y="176" text-anchor="middle" style="font-size:14px;font-weight:800">NPay</text>')
P.append(f'<g class="fade" data-lit="0-5"><text x="{cx}" y="206" text-anchor="middle" style="font-size:16px;font-weight:700">&#8377;25,000</text></g>')
P.append(f'<g class="fade" data-lit="6+"><text class="fill-teal" x="{cx}" y="206" text-anchor="middle" style="font-size:16px;font-weight:700">&#8377;24,750</text></g>')
P.append('<g class="fade" data-lit="0-3">' + ''.join(f'<rect class="mute" x="{cx - 44}" y="{y0}" width="88" height="14" rx="4"/>' for y0 in (222, 242, 262)) + '</g>')
P.append(f'<g class="fade" data-lit="4+"><rect class="wire" style="fill:none" x="{cx - 44}" y="220" width="88" height="16" rx="4"/>'
         f'<text class="sm" x="{cx}" y="232" text-anchor="middle" style="font-size:9px">Coffee &#8722;&#8377;250</text>'
         + ''.join(f'<rect class="mute" x="{cx - 44}" y="{y0}" width="88" height="14" rx="4"/>' for y0 in (242, 262, 282)) + '</g>')
P.append(f'<g class="nd fade" data-lit="3-5"><rect class="sh" style="fill:none" x="{cx - 50}" y="188" width="100" height="26" rx="6"/></g>')
P.append(f'<g class="nd fade" data-lit="3-5"><rect class="sh" style="fill:none" x="{cx - 50}" y="216" width="100" height="24" rx="6"/></g>')
P.append('<g class="fade" data-lit="3-5"><text class="sm fill-teal" x="972" y="208" text-anchor="end">only these</text><text class="sm fill-teal" x="972" y="226" text-anchor="end">change &#8594;</text></g>')
S.append(slide('Part 5 &middot; Rendering &middot; conceptual', 'From &#8377;25,000 to &#8377;24,750', f"""  <div class="body top">
    {svg('0 0 1136 372', 'An update: state changes, SwiftUI evaluates the description, reconciles what changed (the balance and one new row), lays out, redraws only those parts, and the next frame shows the new balance.', 'upd6', P)}{cues(6)}
    <div class="gap"></div>
    <div class="takeaway step">Only <b>what changed</b> is redrawn: not the whole screen.</div>
  </div>""", notes(
    ('SAY', 'NPay is already on screen showing &#8377;25,000. A &#8377;250 coffee payment lands. Watch the phone on the right. Click one: the state changes; in memory the balance is now &#8377;24,750, but the screen still shows the old value.'),
    ('SAY', 'Click two: SwiftUI reads the dashboard&rsquo;s description again. Click three: it compares the new description with the last one: only two things changed, the balance and one new transaction row. Click four: layout makes room for the new row. Click five: graphics redraws only those changed parts. Click six: the next frame shows &#8377;24,750.'),
    ('SAY', 'Click: so after the first frame, an update redraws only what changed, not the whole screen. Recall from Part 1: a view is a description, not a drawing.'),
    ('ASK', 'How is this different from the first frame in Part 2?'),
    ('EXPECT', 'On the first frame everything was new and drawn; on an update only what changed is redrawn.'),
    ('CONNECT', 'So why do frames drop?'))))
# rebuilt (user review, concrete style): does NPay's work fit the frame? scrolling fits, a main-thread sort misses three frames, the sort moved off fits again
F0, FW = 196, 156
def chip(k, t='draw', cls=''):
    x = F0 + k * FW + 10
    if cls:
        return f'<g class="{cls}"><rect class="sh" x="{x}" y="56" width="70" height="34" rx="8"/><text class="sm" x="{x + 35}" y="78" text-anchor="middle">{t}</text></g>'
    return f'<rect class="wire" style="fill:none" x="{x}" y="56" width="70" height="34" rx="8"/><text class="sm" x="{x + 35}" y="78" text-anchor="middle">{t}</text>'
P = ['<text x="0" y="78">Main thread</text><text class="sm" x="0" y="96">60 Hz frames</text>',
     f'<path class="wire" d="M{F0} 34H1136"/>' + ''.join(f'<path class="wire" d="M{F0 + k * FW} 24V44"/>' for k in range(7)),
     '<text class="sm" x="1136" y="16" text-anchor="end">a tick every 16.67 ms &#8594;</text>',
     '<g class="fade" data-lit="1">' + ''.join(chip(k) for k in range(6)) + '</g>',
     '<g class="fade" data-lit="2">' + chip(0) + chip(1) +
     f'<g class="nd alert"><rect class="sh" x="{F0 + 2 * FW + 10}" y="56" width="{3 * FW - 20}" height="34" rx="8"/><text x="{F0 + 3.5 * FW:g}" y="78" text-anchor="middle">Sort 50,000 transactions</text></g>'
     + chip(5) + ''.join(f'<text class="sm" x="{F0 + k * FW}" y="112" text-anchor="middle">missed</text>' for k in (3, 4, 5)) + '</g>',
     '<g class="fade" data-lit="3+">' + ''.join(chip(k) for k in range(5)) + chip(5, 'sorted', 'nd lit') +
     '<text x="0" y="166">Other thread</text><text class="sm" x="0" y="184">off the main thread</text>'
     f'<rect class="wire" style="fill:none" x="{F0 + FW + 40}" y="146" width="{3 * FW + 60}" height="34" rx="8"/><text x="{F0 + FW + 40 + (3 * FW + 60) / 2:g}" y="168" text-anchor="middle">Sort 50,000 transactions</text>'
     f'<path class="wire" d="M{F0 + 4 * FW + 100} 163H{F0 + 5 * FW + 45}V94M{F0 + 5 * FW + 39} 100l6-6 6 6"/></g>']
for k, cap in enumerate(['Scrolling: each frame&#8217;s work fits before its tick',
                         'The user taps Sort: sorting on the main thread takes three frames, and the list freezes',
                         'Sort on another thread: every frame still fits, and the sorted list appears when ready']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="666" y="236" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 5 &middot; Frame timing &middot; illustrative', 'Does the work fit the frame?', f"""  <div class="body">
    {svg('0 0 1136 250', 'Main-thread frames at 60 Hz: scrolling work fits each frame; sorting 50,000 transactions on the main thread misses three frames; sorting on another thread lets every frame fit and shows the sorted list when ready.', 'fit3', P)}{cues(3)}
    <div class="gap-lg"></div>
    <div class="rule step" data-label="Rule">Too big for one frame? Move it <b>off the main thread</b>.</div>
  </div>""", notes(
    ('SAY', 'The main thread has one frame, one tick, to do its work. Click one: while the user scrolls NPay&rsquo;s list, each frame only has a little drawing to do, and it fits before the tick.'),
    ('SAY', 'Click two: the user taps Sort by amount. Sorting fifty thousand transactions on the main thread takes about three frames. Those frames are missed, and the list freezes mid-scroll.'),
    ('SAY', 'Click three: move the sort to another thread. The main thread keeps drawing every frame, and when the sort is ready, one frame shows the sorted list.'),
    ('SAY', 'Click: the rule. If the work is too big for one frame, it does not belong on the main thread. Durations are illustrative, not measured.'),
    ('ASK', 'Would sorting fifty transactions need to move off the main thread?'),
    ('EXPECT', 'Probably not: it fits in a frame. Measure before moving work.'),
    ('CONNECT', 'So where should each kind of work run?'))))

# 0.5's "Waiting vs computing" dropped (Part 5 re-check): "Three things called background" already contrasts waiting and computing
# rebuilt (Part 5 audit): NPay tasks instead of jargon; the Swift 6.2 code footnote removed
WHERE = [('A tap on Refresh balance', 'Main thread'), ('Showing the new balance', 'Main thread'),
         ('Fetching the balance', 'Off the main thread, waiting'), ('Sorting a year of transactions', 'Off the main thread, computing'),
         ('Saving the draft', 'Off the main thread'), ('Finishing an upload after the user leaves', 'iOS background task, with permission')]
trs = ''.join(f'<tr><td>{a}</td><td><b>{b}</b></td></tr>' for a, b in WHERE)
S.append(slide('Part 5 &middot; Reference', 'Where each kind of work belongs', f"""  <div class="body top">
    <table class="tbl" style="font-size:20px"><thead><tr><th>NPay work</th><th>Where it runs</th></tr></thead><tbody>{trs}</tbody></table>
    <div class="gap"></div>
    <div class="rule step">Only <b>touching the screen</b> belongs on the main thread. Everything slow goes elsewhere.</div>
  </div>""", notes(
    ('SAY', 'The whole Part on one page, with NPay&rsquo;s own work. Taps and showing the new balance: the main thread. Fetching the balance: off the main thread, mostly waiting. Sorting a year of transactions: off the main thread, computing. Saving the draft: off the main thread. And finishing an upload after the user leaves: only through an iOS background task, with permission.'),
    ('SAY', 'Click: the rule. Only work that touches the screen belongs on the main thread; everything slow goes elsewhere. Unit 01, lesson 1.9, shows how Swift says where code runs.'),
    ('CONNECT', 'Finally: how do we know where time actually goes?'))))
take(5, 32, 5, connect='Let&rsquo;s recap Part 5.')
take(5, 33, 5, connect='Two quick questions on Part 5.',
     subs=[('<b>await suspends, it does not block</b>', '<b>Waiting need not block</b>'), ('but async is not background', 'but heavy computing must move off the main thread'),
           ('await suspends without blocking, but async alone does not move work off the main actor.', 'a wait can be handed off without blocking, but heavy computing must be moved off the main thread.')])
question(5, 35, 5, 0, 'Next question.', subs=[
    ('<li>awaiting URLSession data in a Task</li><li>a 3-second <code>Thread.sleep</code> in a Button action</li><li>updating a small <code>@State</code> value</li><li>reading a <code>@MainActor</code> ViewModel property</li>',
     '<li>waiting for the balance download</li><li>the Refresh action waiting 3 seconds on the main thread</li><li>changing one small value on screen</li><li>reading the ViewModel&rsquo;s balance</li>'),
    ('<p class="q-why">Thread.sleep blocks the main thread. Awaiting suspends the task, and the other two are cheap main-thread work.</p>',
     '<p class="q-why">Waiting on the main thread blocks it. A download waits without holding the main thread, and the other two are cheap main-thread work.</p>'),
    ('<span class="notes-label">SAY</span><p>B. Thread.sleep blocks the main thread. Awaiting suspends the task, and the other two are cheap main-thread work.</p>',
     '<span class="notes-label">SAY</span><p>B. Waiting on the main thread blocks it. A download waits without holding the main thread, and the other two are cheap main-thread work.</p>'),
    ('Ask why awaiting does not freeze.', 'Ask why waiting for the download does not freeze.')])
question(5, 39, 5, 1, 'Part 6: memory, and who keeps objects alive.', subs=[
    ('data-title="Does every SwiftUI body evaluation redraw the entire screen?"', 'data-title="When SwiftUI recomputes a view, does it redraw the entire screen?"'),
    ('<p class="q-text">Does every SwiftUI <code>body</code> evaluation redraw the entire screen?</p>', '<p class="q-text">When SwiftUI recomputes a view&rsquo;s description, does it redraw the entire screen?</p>'),
    ('<p class="q-why">body is a description. SwiftUI reconciles changes and updates only what is needed.</p>', '<p class="q-why">A view is a description. SwiftUI works out what changed and updates only that.</p>'),
    ('<b>Common trap:</b> Treating body like a paint method.', '<b>Common trap:</b> Treating a view like a painting that is redone every time.'),
    ('<span class="notes-label">SAY</span><p>No. body is a description. SwiftUI reconciles changes and updates only what is needed.</p>', '<span class="notes-label">SAY</span><p>No. A view is a description. SwiftUI works out what changed and updates only that.</p>')])


# ================================================================== Part 6 · memory & ARC (0.6)
part(6, 'Memory &amp; ARC', 'Stack, heap, ownership and retain cycles',
     'NPay&rsquo;s objects live in memory. Who keeps them alive, and what happens when nobody lets go?',
     ('memory',),
     'The main thread and where work belongs.', 'Memory inside NPay: stack, heap, ARC and retain cycles.',
     'The teal is on memory, inside NPay&rsquo;s process.')
# rebuilt (Part 6 audit, concrete style): each memory region with what NPay keeps there, one per click
REG = [('code', 'Code', 'the machine code the app ships', 'NPay&#8217;s compiled app, built on your Mac (Part 2)'),
       ('file', 'Fixed data', 'values that exist for the whole run', 'settings and constants'),
       ('memory', 'Heap', 'objects that live a while', 'DashboardViewModel, the account, the transaction list'),
       ('thread', 'Stacks', 'one per thread', 'each thread&#8217;s current calculation, gone when it ends'),
       ('layers', 'Shared libraries', 'mapped in from the system', 'SwiftUI, Foundation, images')]
P = ['<text class="mono" x="0" y="14">REGION</text><text class="mono" x="560" y="14">WHAT NPAY KEEPS THERE</text>']
for k, (ic, t, sub, ex) in enumerate(REG):
    y = 26 + k * 64
    P.append(f'<g class="nd" data-lit="{k + 1}"><rect class="sh" x="0" y="{y}" width="1136" height="54" rx="12"/><use href="#i-{ic}" x="14" y="{y + 14}" width="26" height="26"/>'
             f'<text x="52" y="{y + 24}">{t}</text><text class="sm" x="52" y="{y + 42}">{sub}</text></g>')
    P.append(f'<text class="fade" data-lit="{k + 1}+" x="560" y="{y + 33}" style="font-size:18px">{ex}</text>')
S.append(slide('Part 6 &middot; Process memory &middot; conceptual', 'What lives where in NPay&rsquo;s memory', f"""  <div class="body">
    {svg('0 0 1136 346', 'NPay&rsquo;s process memory: code, fixed data, heap, thread stacks and shared libraries, each with what NPay keeps there', 'npaymem', P)}{cues(5)}
    <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div><p>In the kitchen: a <b>stack</b> is a cook&rsquo;s cutting board, cleared after each dish; the <b>heap</b> is the pantry, holding what many dishes need, for longer.</p></div>
  </div>""", notes(
    ('SAY', 'Every process gets its own memory from iOS, and inside it different things live in different places. One region per click. Code: NPay&rsquo;s compiled app, the machine code we built on the Mac in Part 2. Fixed data: settings and constants that exist for the whole run.'),
    ('SAY', 'The heap: objects that live for a while, such as DashboardViewModel, the account and the transaction list. Stacks: one per thread, holding each thread&rsquo;s current calculation, gone when it ends. Shared libraries: SwiftUI, Foundation and images, mapped in from the system.'),
    ('SAY', 'Click: in the kitchen, a stack is a cook&rsquo;s cutting board, cleared after each dish; the heap is the pantry. These are conceptual regions, not their physical order: iOS uses virtual memory.'),
    ('CONNECT', 'Where do individual values live?'))))

# code-free: stack vs heap with an example in words
sh = diagrams(6, 7)[0]
for a_, b_ in [('>Call frame<', '>amount: &#8377;1,500<'), ('>Temporary values<', '>fee: &#8377;10<'), ('>Return information<', '>total: &#8377;1,510<'),
               ('>Object A<', '>Account<'), ('>Object B<', '>Transaction list<'), ('>Shared storage<', '>DashboardViewModel<')]:   # NPay values (Part 6 re-audit)
    assert a_ in sh, a_
    sh = sh.replace(a_, b_)
S.append(slide('Part 6 &middot; Stack and heap &middot; conceptual', 'Where do values live?', f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    {card('Example: one transfer', ul('Adding a fee needs three temporary numbers: <b>amount</b>, <b>fee</b>, <b>total</b>', 'They live in the call&rsquo;s frame on the <b>stack</b>', 'Gone as soon as the calculation returns', 'An account object shared by several screens lives on the <b>heap</b>'))}
    <div>
      {sh}
      <i class="step cue"></i><i class="step cue"></i>
      <div class="gap"></div>
      <p class="small">The <b>stack</b> is fast and clears itself. The <b>heap</b> keeps things as long as someone needs them: ARC decides when they go.</p>
    </div>
  </div>""", notes(('SAY', 'A calculation that adds a fee to a transfer needs temporary storage for the amount, the fee and the total. Click: the stack, tied to function calls and thread execution, with the call frame, temporary values and return information. Click: the heap, for dynamically allocated storage and objects that outlive one call, such as an account shared by several screens.'),
                  ('SAY', 'The stack is typically efficient for call-related storage; heap allocation is more flexible but needs allocation and lifetime management.'),
                  ('CONNECT', 'Some values are copied; some objects are shared. What is the difference?'))))
# 0.6's "Not simply stack versus heap" dropped (Part 6 audit): a Swift-compiler nuance shown before values and objects are introduced
# rebuilt (Part 6 audit; user review: phones): copied vs shared, with NPay's screens; replaces the Swift struct-vs-class table
def ph(c):
    return f'<use href="#d-iphone" x="{c - 55}" y="26" width="110" height="220"/>'
big = lambda c, y, t, cls='': f'<text{(" class=\"" + cls + "\"") if cls else ""} x="{c}" y="{y}" text-anchor="middle" style="font-size:17px;font-weight:700">{t}</text>'
sm_ = lambda c, y, t, cls='sm': f'<text class="{cls}" x="{c}" y="{y}" text-anchor="middle">{t}</text>'
P = ['<text class="mono" x="0" y="14">A VALUE IS COPIED</text>', '<path class="wire faint" d="M566 4V330"/>', '<text class="mono" x="600" y="14">AN OBJECT IS SHARED</text>',
     ph(130), sm_(130, 76, 'Payment', 'mono'), sm_(130, 100, 'to ravi@npay'), '<rect class="wire" style="fill:none" x="88" y="112" width="84" height="32" rx="6"/>',
     f'<g class="fade" data-lit="1">{big(130, 134, "&#8377;1,500")}</g>',
     f'<g class="fade" data-lit="2+">{big(130, 134, "&#8377;2,000", "fill-teal")}{sm_(130, 166, "edited", "sm fill-teal")}</g>',
     f'<g class="fade" data-lit="1+"><path class="wire" d="M196 128H350M343 121l7 7-7 7"/>{sm_(272, 116, "copy")}'
     f'{ph(420)}{sm_(420, 76, "Review", "mono")}{sm_(420, 104, "Pay")}{big(420, 128, "&#8377;1,500")}{sm_(420, 152, "to ravi@npay")}'
     '<rect class="wire" style="fill:none" x="384" y="168" width="72" height="22" rx="6"/><text class="sm" x="420" y="183" text-anchor="middle">Confirm</text></g>',
     f'<g class="fade" data-lit="2+">{sm_(420, 270, "the copy is not affected")}</g>',
     f'<g class="fade" data-lit="3+">{ph(700)}{sm_(700, 76, "Home", "mono")}{ph(1000)}{sm_(1000, 76, "History", "mono")}'
     '<path class="wire" d="M700 248V290H748M741 283l7 7-7 7M1000 248V290H952M959 283l7 7-7 7"/>'
     '<g class="nd"><rect class="sh" x="752" y="266" width="196" height="50" rx="12"/><use href="#i-bank" x="764" y="278" width="24" height="24"/><text class="sm" x="796" y="295">one Account object</text></g></g>',
     f'<g class="fade" data-lit="3">{big(700, 124, "&#8377;25,000")}{big(1000, 124, "&#8377;25,000")}</g>',
     f'<g class="fade" data-lit="4+">{big(700, 124, "&#8377;24,750", "fill-teal")}{big(1000, 124, "&#8377;24,750", "fill-teal")}{sm_(850, 230, "both screens see it", "sm fill-teal")}</g>']
for k, cap in enumerate(['NPay copies the &#8377;1,500 draft to the review screen',
                         'Edit the draft to &#8377;2,000: the review screen&#8217;s copy still says &#8377;1,500',
                         'Home and History hold the same Account object',
                         'A payment changes it once: both screens show &#8377;24,750']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="568" y="352" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 6 &middot; Values and objects', 'Copied vs shared', f"""  <div class="body">
    {svg('0 0 1136 364', 'Left: the draft amount is copied to the review screen; editing the draft leaves the copy unchanged. Right: Home and History share one Account object; a payment changes it once and both see the new balance.', 'copyshare', P)}{cues(4)}
    <div class="gap"></div>
    <div class="rule step" data-label="Values and objects">Values are <b>copied</b>; objects are <b>shared</b>. A shared object needs someone to decide when it can be freed: that is <b>ARC</b>.</div>
    <p class="small muted" style="margin:8px 0 0">In Swift, values are structs and shared objects are classes; Unit 01 &middot; 1.5 shows both.</p>
  </div>""", notes(
    ('SAY', 'Two ways data lives in NPay. Click: a value is copied. NPay copies the &#8377;1,500 draft to the review screen. Click: the user edits the draft to &#8377;2,000, and the review screen&rsquo;s copy still says &#8377;1,500: copies are independent.'),
    ('SAY', 'Click: an object is shared. Home and History both hold the same Account object. Click: a payment changes it once, and both screens show &#8377;24,750.'),
    ('SAY', 'Click: values are copied, objects are shared. And because a shared object can be held by many screens, something must decide when nobody needs it any more and it can be freed. In Swift that is ARC, automatic reference counting.'),
    ('ASK', 'Should NPay&rsquo;s account balance, shown on several screens, be a copied value or a shared object?'),
    ('EXPECT', 'Shared, so every screen sees the same balance.'),
    ('CONNECT', 'So how does ARC know when nobody needs an object?'))))
# rebuilt (user review): the count goes up and down as NPay's screens open and close; freed when the last holder lets go
def holder(y, t, active, gone):
    return (f'<g class="fade" data-lit="{active}"><g class="nd"><rect class="sh" x="0" y="{y}" width="300" height="62" rx="12"/><use href="#i-phone" x="14" y="{y + 18}" width="26" height="26"/>'
            f'<text x="52" y="{y + 28}">{t}</text><text class="sm" x="52" y="{y + 46}">holds the account</text></g>'
            f'<path class="wire" d="M302 {y + 31}H{514}M507 {y + 24}l7 7-7 7"/></g>'
            f'<g class="fade" data-lit="{gone}"><g class="nd ghost"><rect class="sh" x="0" y="{y}" width="300" height="62" rx="12"/>'
            f'<text x="52" y="{y + 28}">{t}</text><text class="sm" x="52" y="{y + 46}">let go</text></g></g>')
P = [holder(40, 'Home screen', '1-3', '4+'), holder(150, 'Payment sheet', '2', '3+'),
     '<g class="fade" data-lit="1-3"><g class="nd lit"><rect class="sh" x="520" y="30" width="420" height="190" rx="18"/></g></g>',
     '<g class="fade" data-lit="0"><g class="nd ghost"><rect class="sh" x="520" y="30" width="420" height="190" rx="18"/></g></g>',   # ghost inside a fade: .nd.ghost opacity outranks .fade
     '<g class="fade" data-lit="4+"><g class="nd ghost"><rect class="sh" x="520" y="30" width="420" height="190" rx="18"/></g></g>',
     '<use href="#i-bank" x="544" y="52" width="28" height="28"/><text x="584" y="72">Account object</text>',
     '<text class="sm" x="544" y="196">strong references holding it</text>']
for lit_, n, st in [('1', '1', 'ALIVE'), ('2', '2', 'ALIVE'), ('3', '1', 'STILL ALIVE'), ('4+', '0', 'FREED BY ARC')]:
    P.append(f'<g class="fade" data-lit="{lit_}"><text x="544" y="168" style="font-size:72px;font-weight:800">{n}</text>'
             f'<text class="mono" x="916" y="168" text-anchor="end">{st}</text></g>')
for k, cap in enumerate(['Home opens and holds the account: 1 strong reference',
                         'The payment sheet also holds it: 2',
                         'The sheet closes and lets go: 1. Home still holds it, so it stays alive',
                         'The user signs out and Home lets go: 0. Nobody holds it, so ARC frees it']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="568" y="270" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 6 &middot; ARC &middot; conceptual', 'Counting strong references', f"""  <div class="body">
    {svg('0 0 1136 284', 'NPay&rsquo;s Account object: Home holds it (1), the payment sheet holds it too (2), the sheet lets go (1), Home lets go (0) and ARC frees it.', 'arccount', P)}{cues(4)}
    <div class="gap"></div>
    <div class="rule step" data-label="ARC">ARC frees an object when its <b>last strong holder</b> lets go.</div>
  </div>""", notes(
    ('SAY', 'ARC, automatic reference counting, counts who is holding an object. Follow NPay&rsquo;s Account object. Click: Home opens and holds the account: one strong reference. Click: the payment sheet opens and holds it too: two.'),
    ('SAY', 'Click: the sheet closes and lets go: back to one. Home still holds it, so it stays alive. Click: the user signs out and Home lets go: zero. Nobody holds it any more, so ARC frees it straight away.'),
    ('SAY', 'Click: the rule. ARC frees an object when its last strong holder lets go. In the kitchen: each holder is a cook still using an ingredient; when nobody is using it, it is cleared away. Conceptual: the compiler may optimise the counting, so it is not always visible one-for-one.'),
    ('ASK', 'The payment sheet closes. Is the Account object freed?'),
    ('EXPECT', 'No: Home still holds it. Only when the last holder lets go.'),
    ('CONNECT', 'Not every reference keeps an object alive.'))))
# rebuilt (user review): strong vs weak as an NPay story; unowned is Unit 01 · 1.8
def box2(x, y, w, ic, t, sub, cls=''):
    return (f'<g class="nd{(" " + cls) if cls else ""}"><rect class="sh" x="{x}" y="{y}" width="{w}" height="70" rx="12"/><use href="#i-{ic}" x="{x + 14}" y="{y + 22}" width="26" height="26"/>'
            f'<text x="{x + 52}" y="{y + 31}">{t}</text><text class="sm" x="{x + 52}" y="{y + 51}">{sub}</text></g>')
P = ['<g class="fade" data-lit="1-2">' + box2(80, 30, 300, 'phone', 'Home screen', 'holds the account') + '</g>',
     '<g class="fade" data-lit="3+">' + box2(80, 30, 300, 'phone', 'Home screen', 'let go (signed out)', 'ghost') + '</g>',
     '<g class="fade" data-lit="1-2"><path class="wire lit" d="M382 65H560V112M553 105l7 7 7-7"/><text class="sm" x="470" y="54" text-anchor="middle">strong: keeps it alive</text></g>',
     '<g class="fade" data-lit="1-2"><g class="nd lit"><rect class="sh" x="430" y="118" width="300" height="70" rx="14"/></g></g>',
     '<g class="fade" data-lit="3+"><g class="nd ghost"><rect class="sh" x="430" y="118" width="300" height="70" rx="14"/></g></g>',
     '<use href="#i-bank" x="444" y="140" width="26" height="26"/><text x="482" y="149">Account object</text>',
     '<g class="fade" data-lit="1-2"><text class="sm" x="482" y="169">alive</text></g>',
     '<g class="fade" data-lit="3+"><text class="sm" x="482" y="169">freed by ARC</text></g>',
     '<g class="fade" data-lit="2+">' + box2(780, 220, 300, 'eye', 'Balance banner', 'shows it if it still exists') + '</g>',
     '<g class="fade" data-lit="2"><path class="wire dash lit" d="M778 255H600V194M593 201l7-7 7 7"/><text class="sm" x="690" y="276" text-anchor="middle">weak: only points to it</text></g>',
     '<g class="fade" data-lit="3+"><path class="wire dash" d="M778 255H700"/><text class="sm fill-teal" x="690" y="276" text-anchor="middle">link is now empty: no crash</text></g>']
for k, cap in enumerate(['Home holds the account strongly: while Home holds it, it stays alive',
                         'A balance banner points to it weakly: it can show it, but does not keep it alive',
                         'The user signs out: only a weak link is left, so ARC frees it, and the link becomes empty']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="324" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 6 &middot; Reference kinds', 'Strong and weak references', f"""  <div class="body">
    {svg('0 0 1136 336', 'Home holds NPay&rsquo;s Account object strongly; a balance banner points to it weakly; when Home lets go, the account is freed and the banner&rsquo;s weak link becomes empty.', 'strongweak', P)}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Strong and weak"><b>Strong</b> = owns it, keeps it alive. <b>Weak</b> = only points to it, and becomes empty when it is freed.</div>
  </div>""", notes(
    ('SAY', 'Not every reference keeps an object alive. Click: Home holds NPay&rsquo;s Account object strongly; while Home holds it, ARC keeps it alive. That is the normal kind.'),
    ('SAY', 'Click: a small balance banner points to the same account weakly. It can show the balance while the account exists, but it does not keep the account alive.'),
    ('SAY', 'Click: the user signs out and Home lets go. Only a weak link is left, and weak links do not count, so ARC frees the account. The banner&rsquo;s link simply becomes empty: no crash, nothing leaked.'),
    ('SAY', 'Click: strong owns it; weak only points to it. Do not overcorrect: owners should hold strongly, and weak is for back-links and observers. Swift has a third kind, unowned, for special cases; Unit 01, lesson 1.8, covers it.'),
    ('ASK', 'If the banner held the account strongly instead, what would happen after sign-out?'),
    ('EXPECT', 'The account would stay alive because the banner still holds it.'),
    ('CONNECT', 'What happens when two objects keep each other alive?'))))

# rebuilt (Part 6 re-audit): the retain cycle with NPay's own objects; Home lets go, the cycle leaks, a weak back-link fixes it
def ob(x, y, ic, t, sub, lit_, cls=''):
    return (f'<g class="fade" data-lit="{lit_}"><g class="nd{(" " + cls) if cls else ""}"><rect class="sh" x="{x}" y="{y}" width="260" height="70" rx="12"/>'
            f'<use href="#i-{ic}" x="{x + 14}" y="{y + 22}" width="26" height="26"/><text x="{x + 52}" y="{y + 31}">{t}</text><text class="sm" x="{x + 52}" y="{y + 51}">{sub}</text></g></g>')
P = [ob(438, 0, 'phone', 'Home screen', 'holds the account', '1'), ob(438, 0, 'phone', 'Home screen', 'let go (signed out)', '2+', 'ghost'),
     '<g class="fade" data-lit="1"><path class="wire" d="M568 72V128M561 121l7 7 7-7"/></g>',
     ob(140, 134, 'bank', 'Account', 'holds its card', '1'), ob(140, 134, 'bank', 'Account', 'still held by the card', '2'),
     ob(140, 134, 'bank', 'Account', 'freed', '3+', 'ghost'),
     ob(736, 134, 'key', 'Card', 'points back to its account', '1'), ob(736, 134, 'key', 'Card', 'still held by the account', '2'),
     '<g class="fade" data-lit="2"><g class="nd alert"><rect class="sh" x="418" y="226" width="300" height="34" rx="10"/><text x="568" y="248" text-anchor="middle">neither is freed: a leak</text></g></g>',
     ob(736, 134, 'key', 'Card', 'freed', '3+', 'ghost'),
     '<g class="fade" data-lit="1-2"><path class="wire" d="M402 156H730M723 149l7 7-7 7"/><text class="sm" x="566" y="148" text-anchor="middle">strong</text>'
     '<path class="wire" d="M734 190H406M413 183l-7 7 7 7"/><text class="sm" x="566" y="214" text-anchor="middle">strong</text></g>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M402 156H730M723 149l7 7-7 7"/><text class="sm" x="566" y="148" text-anchor="middle">strong</text>'
     '<path class="wire dash lit" d="M734 190H406M413 183l-7 7 7 7"/><text class="sm fill-teal" x="566" y="214" text-anchor="middle">weak back-link</text></g>']
for k, cap in enumerate(['The account holds its card; the card points back to its account. Both strongly',
                         'The user signs out: Home lets go, but each still holds the other, so neither is freed: a leak',
                         'Fix: the card points back weakly. Home lets go, and both are freed']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="296" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 6 &middot; Retain cycle &middot; conceptual', 'Two objects that never let go', f"""  <div class="body">
    {svg('0 0 1136 308', 'NPay&rsquo;s account holds its card and the card holds the account back. When Home lets go, both stay alive: a retain cycle. With a weak back-link, both are freed.', 'cycle2', P)}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Retain cycle">Two objects holding each other <b>strongly</b> are never freed. Make the <b>back-link weak</b>.</div>
  </div>""", notes(
    ('SAY', 'Click: NPay&rsquo;s account holds its card, and the card points back to its account. Both links are strong, and Home holds the account.'),
    ('SAY', 'Click: the user signs out and Home lets go. Nothing else needs them, but each still holds the other, so their counts never reach zero: neither is freed. That is a retain cycle, a leak.'),
    ('SAY', 'Click: the fix. The account owns its card, so that link stays strong; the card only points back, so make that link weak. Now when Home lets go, the account is freed, and then the card.'),
    ('SAY', 'Click: two objects holding each other strongly are never freed; make the back-link weak.'),
    ('ASK', 'Which link should be weak: account to card, or card back to account?'),
    ('EXPECT', 'Card back to account: the owner holds strongly, the back-link is weak.'),
    ('CONNECT', 'Cycles between two objects are easy to spot. Cycles through closures are not.'))))
take(6, 24, 6, kicker='Part 6 &middot; Closures &middot; conceptual', connect='Is every high-memory app leaking? No.', subs=[   # plain words (Part 6 audit)
    ('<h2>Strong vs weak capture</h2>', '<h2>A closure that holds on</h2>'),
    ('<div class="rule step" data-label="Not for every closure"><code>[weak self]</code> matters for <b>escaping closures</b> that are retained and create a cycle. A short-lived, non-escaping closure does not need it.</div>',
     '<div><p class="lead" style="margin:0 0 12px;font-size:21px">A <b>closure</b> is code NPay keeps to run later, such as &ldquo;refresh when the timer fires&rdquo;. It holds on to what it uses.</p>'
     '<div class="rule step" data-label="The fix">If the closure holds the ViewModel that keeps it, let it hold the ViewModel <b>weakly</b>. A closure that runs once and is gone needs nothing.</div></div>'),
    ('<span class="notes-label">SAY</span><p>Strong capture: release the external owner and the ViewModel stays alive in an ownership cycle. Click: with weak capture, the same release lets the ViewModel be deallocated.</p>',
     '<span class="notes-label">SAY</span><p>A closure is a piece of code NPay keeps to run later, for example: when the timer fires, refresh the balance. It holds on to whatever it uses. If DashboardViewModel keeps that closure, and the closure holds the ViewModel strongly, they keep each other alive: release the screen and the ViewModel stays. Click: if the closure holds the ViewModel weakly, the same release lets the ViewModel be freed.</p>'),
    ('<span class="notes-label">SAY</span><p>Do not teach [weak self] as mandatory for every closure. It matters for escaping closures retained in a way that creates an unwanted cycle or extends a lifetime beyond what is intended. A short-lived non-escaping closure does not automatically need it.</p>',
     '<span class="notes-label">SAY</span><p>Not every closure needs this: one that runs once and is gone cannot create a cycle. Unit 01, lesson 1.8, shows the Swift.</p>'),
    ('With strong capture the ViewModel stays alive after its external owner is released; with weak capture it is deallocated',
     'If the closure holds the ViewModel strongly, the ViewModel stays alive after its screen lets go; if it holds it weakly, it is freed')])
# 0.6's "strong vs weak vs unowned" table dropped (Part 6 audit): repeats strong and weak, adds unowned (Unit 01 · 1.8)
take(6, 28, 6, subs=[   # plain words (Part 6 re-audit)
    ('<p>Memory stays allocated though <b>no longer needed</b>, and cannot be reclaimed through the intended ownership path.</p>',
     '<p>Memory NPay <b>no longer needs</b> but can never get back, like the account and card in a cycle.</p>'),
    ('<p>The app uses a lot of memory. That may be <b>legitimate</b>, or a sign of excessive caching or allocation.</p>',
     '<p>NPay uses a lot of memory <b>on purpose</b>, like a big photo. Fine, unless it keeps growing.</p>'),
    ('A leak is memory that stays allocated though no longer needed and cannot be reclaimed through the intended ownership path. High memory usage may be legitimate, or may indicate excessive caching or allocation.',
     'Two different problems. A leak is memory NPay no longer needs but can never get back, like the account and card in a cycle. High usage is memory NPay uses on purpose; that is fine unless it keeps growing.')])
# simplified (user review): three tools, one question and one NPay example each
TOOLS = [('eye', 'Memory Graph', 'Who is still holding this object?', 'The closed payment sheet is still in memory: who holds it?'),
         ('layers', 'Allocations', 'Does memory grow each time I repeat something?', 'Open and close History ten times: memory keeps growing'),
         ('cross', 'Leaks', 'Is there memory nobody can reach any more?', 'Two objects holding each other, with nobody else pointing at them')]
tool_cards = ''.join(f'<div class="card accent step anim-up" style="padding:16px 20px"><span class="label">{t}</span>'
                     f'<p style="margin:4px 0 8px;font-size:21px"><b>{q}</b></p><p class="small muted" style="margin:0">e.g. {e}</p></div>' for ic, t, q, e in TOOLS)
S.append(slide('Part 6 &middot; Tools', 'Three memory tools', f"""  <div class="body">
    <div class="cols c3" style="gap:18px;align-items:stretch">{tool_cards}</div>
    <div class="gap"></div>
    <div class="rule step" data-label="Watch out"><b>Leaks</b> only finds memory nobody can reach. Something still held, like a cache that keeps growing, looks fine to it: use the <b>Memory Graph</b>.</div>
  </div>""", notes(
    ('SAY', 'Xcode gives us three tools, each answering one question. Click: the Memory Graph answers &ldquo;who is still holding this object?&rdquo;; for example, the payment sheet is closed but still in memory, and the graph shows the chain of strong references holding it.'),
    ('SAY', 'Click: Allocations answers &ldquo;does memory grow each time I repeat something?&rdquo;; open and close History ten times and see whether memory keeps climbing. Click: Leaks answers &ldquo;is there memory nobody can reach any more?&rdquo;, such as two objects holding each other with nobody else pointing at them.'),
    ('SAY', 'Click: watch out. Leaks only finds memory nobody can reach. Something still held, like a cache that keeps growing or a timer that keeps running, looks fine to Leaks; the Memory Graph and Allocations find those.'),
    ('CONNECT', 'Here is a repeatable sequence for any suspected leak.'))))
take(6, 31, 6, connect='Let&rsquo;s recap Part 6.', subs=[
    ('A missing deinit message alone does not prove a leak: the object may still be intentionally owned.', 'An object that is never freed is not always a leak: something may still own it on purpose.'),
    ('observe memory growth or a missing deinit;', 'observe memory growing, or an object that is never freed;'),
    ('missing deinit', 'object never freed')])
take(6, 35, 6, connect='Two quick questions on Part 6.', subs=[
    ('structs give independent values; classes share one instance', 'values are copied; objects are shared'), ('<b>Value vs reference</b>', '<b>Copied vs shared</b>'),
    ('strong references keep a class instance alive', 'strong references keep a shared object alive'),
    ('break them with weak; stop timers explicitly', 'break them with a weak reference'),
    ('Value versus reference semantics is the reliable distinction, not stack versus heap. ARC keeps a class instance alive while strong references exist. And cycles, through properties, closures or timers, are broken with weak references and explicit cancellation.',
     'Values are copied and objects are shared. ARC keeps a shared object alive while someone holds it strongly. And cycles, between two objects or through a closure, are broken with a weak reference.')])
question(6, 37, 6, 0, 'Next question.', subs=[
    ('data-title="What keeps a class instance alive under ARC?"', 'data-title="What keeps a shared object alive?"'),
    ('<p class="q-text">What keeps a class instance alive under ARC?</p>', '<p class="q-text">What keeps a shared object alive?</p>'),
    ('<li>Being declared with <code>let</code></li>', '<li>Being stored in a constant</li>'),
    ('Only strong references keep an instance alive. Weak and unowned references do not, and where it is allocated or how the variable is declared has nothing to do with it.',
     'Only strong references keep an object alive. Weak references do not, and where or how it is stored has nothing to do with it.', 2)])
question(6, 39, 6, 1, 'Part 7: the walls iOS builds around NPay.', subs=[
    ('Can two class instances that strongly retain each other stay alive after external references disappear?', 'Can two objects that strongly hold each other stay alive after everyone else lets go?'),
    ('data-title="Can two instances that retain each other outlive their external references?"', 'data-title="Can two objects that hold each other stay alive?"')])


# ================================================================== Part 7 · security (0.7)
part(7, 'Security', 'Sandbox, entitlements, signing, Keychain, Secure Enclave',
     'NPay handles money. How does iOS keep it apart from other apps, and keep its secrets safe?',
     ('sandbox', 'keychain', 'kernel', 'hardware'),
     'Memory inside NPay&rsquo;s process.', 'The walls around that process: sandbox, signing, Keychain and the Secure Enclave.',
     'The teal is on the walls: NPay&rsquo;s sandbox, the Keychain, the kernel that enforces the rules, and the hardware with the Secure Enclave.')
take(7, 5, 7)
# rebuilt (user review, concrete style): each security layer with what it does for NPay, one per click
SEC = [('code', 'Application security', 'NPay&#8217;s own code', 'Signs the user in; keeps the token in the Keychain'),
       ('eye', 'Privacy &amp; permissions', 'the user decides', 'Asks before using the camera to scan a cheque'),
       ('lock', 'Sandbox &amp; entitlements', 'boundaries', 'Other apps cannot read NPay&#8217;s files'),
       ('file', 'Code signing', 'integrity', 'iOS checks NPay is from its team and unchanged'),
       ('chip', 'Kernel &amp; hardware', 'the foundation', 'Keeps apps apart; the Secure Enclave guards keys')]
P = ['<text class="mono" x="0" y="14">LAYER</text><text class="mono" x="560" y="14">WHAT IT DOES FOR NPAY</text>']
for k, (ic, t, sub, ex) in enumerate(SEC):
    y = 26 + k * 66
    P.append(f'<g class="nd" data-lit="{k + 1}"><rect class="sh" x="0" y="{y}" width="1136" height="56" rx="12"/><use href="#i-{ic}" x="14" y="{y + 15}" width="26" height="26"/>'
             f'<text x="52" y="{y + 25}">{t}</text><text class="sm" x="52" y="{y + 43}">{sub}</text></g>')
    P.append(f'<text class="fade" data-lit="{k + 1}+" x="560" y="{y + 34}" style="font-size:18px">{ex}</text>')
S.append(slide('Part 7 &middot; Layers &middot; conceptual', 'iOS security architecture', f"""  <div class="body">
    {svg('0 0 1136 352', 'Five security layers, each with what it does for NPay: application security, privacy and permissions, sandbox and entitlements, code signing, kernel and hardware', 'seclayers', P)}{cues(5)}
    <div class="analogy step"><div class="icon"><svg viewBox="0 0 24 24"><use href="#i-building"/></svg></div><p>Like the <b>hotel</b>: the front desk checks who you are, your <b>key</b> opens only your room, valuables go in the <b>safe</b>. Passing one check does <b>not</b> open every door.</p></div>
  </div>""", notes(
    ('SAY', 'iOS protects NPay with several layers, each guarding something different. One per click. Application security is NPay&rsquo;s own job: signing the user in and keeping the token safe in the Keychain. Privacy and permissions put the user in charge: NPay must ask before using the camera to scan a cheque.'),
    ('SAY', 'The sandbox keeps other apps out of NPay&rsquo;s files. Code signing lets iOS check that NPay really comes from its team and has not been changed. And the kernel and hardware are the foundation: they keep apps apart, and the Secure Enclave guards the most sensitive keys.'),
    ('SAY', 'Click: like the hotel from Part 1. The front desk checks who you are, your key opens only your room, and valuables go in the safe. Passing one check does not open every door: a signed app still cannot use every device capability. The layers overlap and work together.'),
    ('CONNECT', 'Start with the boundary every app lives inside: the sandbox.'))))
# rebuilt (user review, concrete style): two app containers; what ShopEasy can and cannot reach, one attempt per click
def fileb(x, y, t, cls=''):
    return (f'<g class="nd{(" " + cls) if cls else ""}"><rect class="sh" x="{x}" y="{y}" width="330" height="40" rx="8"/>'
            f'<use href="#i-file" x="{x + 10}" y="{y + 9}" width="22" height="22"/><text class="sm" x="{x + 40}" y="{y + 25}">{t}</text></g>')
P = ['<rect class="wire dash" style="fill:none" x="0" y="0" width="390" height="210" rx="16"/>',
     '<use href="#i-bank" x="16" y="14" width="24" height="24"/><text x="48" y="32">NPay&#8217;s container</text>',
     fileb(30, 54, 'account data'), fileb(30, 104, 'statement.pdf'),
     '<rect class="wire dash" style="fill:none" x="746" y="0" width="390" height="210" rx="16"/>',
     '<use href="#i-app" x="762" y="14" width="24" height="24"/><text x="794" y="32">ShopEasy&#8217;s container</text>',
     fileb(776, 54, 'cart, orders', ''),
     '<g class="fade" data-lit="1"><g class="nd lit"><rect class="sh" x="776" y="54" width="330" height="40" rx="8"/><use href="#i-file" x="786" y="63" width="22" height="22"/><text class="sm" x="816" y="79">cart, orders</text></g>'
     '<text class="sm fill-teal" x="941" y="124" text-anchor="middle">reads its own files: allowed</text></g>',
     '<g class="fade" data-lit="2"><path class="wire" d="M742 74H436"/><g class="nd alert"><rect class="sh" x="396" y="50" width="70" height="48" rx="10"/><use href="#i-lock" x="418" y="61" width="26" height="26"/></g>'
     '<text class="sm" x="568" y="128" text-anchor="middle">reaching into NPay&#8217;s files: blocked by the sandbox</text></g>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M362 124H470V256H508M501 249l7 7-7 7"/>'
     '<g class="nd lit"><rect class="sh" x="512" y="230" width="112" height="52" rx="12"/><text x="568" y="261" text-anchor="middle">Share</text></g>'
     '<path class="wire" d="M628 256H700V172H770M763 165l7 7-7 7"/>'
     + fileb(776, 152, 'statement.pdf (a copy)', 'lit') +
     '<text class="sm" x="568" y="304" text-anchor="middle">the user shares it through iOS: allowed</text></g>']
for k, cap in enumerate(['ShopEasy reads its own files: allowed',
                         'ShopEasy tries to read NPay&#8217;s files directly: the sandbox blocks it',
                         'The user shares NPay&#8217;s statement through iOS: ShopEasy gets a copy']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="346" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Sandbox &middot; conceptual', 'The sandbox: each app in its own container', f"""  <div class="body">
    {svg('0 0 1136 358', 'NPay and ShopEasy each have a private container. ShopEasy can read its own files, is blocked from NPay&rsquo;s, and gets a copy of NPay&rsquo;s statement only when the user shares it through iOS.', 'sandbox2', P, 'max-height:400px')}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Sandbox">Apps never reach into each other. Data crosses only when the <b>user and iOS</b> hand it over.</div>
  </div>""", notes(
    ('SAY', 'Every app lives in its own container, its own room in the hotel. NPay keeps its account data and statements there; ShopEasy keeps its cart. Click: ShopEasy reads its own files: allowed.'),
    ('SAY', 'Click: ShopEasy tries to reach into NPay&rsquo;s container and read its files directly. The sandbox blocks it: no app can browse another app&rsquo;s private files.'),
    ('SAY', 'Click: the user opens NPay&rsquo;s statement and taps Share. iOS hands a copy to ShopEasy, because the user chose to. Data can cross, but only through iOS and with the user&rsquo;s choice.'),
    ('SAY', 'Click: apps never reach into each other. There are other approved routes too, such as an App Group that lets NPay share data with its own widget; that needs an approved capability, which brings us to entitlements.'),
    ('ASK', 'Could a malicious app on the same phone read NPay&rsquo;s saved token file?'),
    ('EXPECT', 'No: the sandbox blocks access to NPay&rsquo;s container. Sensitive data also goes in the Keychain.'),
    ('CONNECT', 'How does an app get approved capabilities like an App Group? Entitlements.'))))
# rebuilt (user review, concrete style): the entitlement drawn as a signed slip inside the app; iOS checks it; NPay's widget shows the balance, ShopEasy is refused
def bundle(y, name, ic, slip, slip_lit, seal_lit, cls=''):
    o = (f'<rect class="wire dash" style="fill:none" x="0" y="{y}" width="360" height="132" rx="16"/>'
         f'<use href="#i-{ic}" x="16" y="{y + 14}" width="24" height="24"/><text x="48" y="{y + 32}">{name}</text>'
         f'<g class="fade" data-lit="{slip_lit}"><g class="nd{(" " + cls) if cls else ""}"><rect class="sh" x="22" y="{y + 50}" width="316" height="66" rx="10"/>'
         f'<use href="#i-file" x="34" y="{y + 70}" width="24" height="24"/><text class="sm" x="66" y="{y + 76}">Entitlements</text><text x="66" y="{y + 98}">{slip}</text></g></g>')
    if seal_lit:
        o += (f'<g class="fade" data-lit="{seal_lit}"><circle class="wire lit" style="fill:var(--paper)" cx="322" cy="{y + 28}" r="24"/>'
              f'<text class="mono fill-teal" x="322" y="{y + 32}" text-anchor="middle" style="font-size:10px">SIGNED</text></g>')
    return o
P = [bundle(0, 'NPay.app', 'bank', 'App Group: shared with the widget', '1+', '2+'),
     '<g class="fade" data-lit="3+"><path class="wire" d="M364 66H452M445 59l7 7-7 7"/></g>',
     '<g class="nd" data-lit="3-4"><rect class="sh" x="458" y="22" width="200" height="88" rx="14"/><use href="#i-shield" x="544" y="34" width="28" height="28"/>'
     '<text x="558" y="82" text-anchor="middle">iOS checks</text><text class="sm" x="558" y="100" text-anchor="middle">reads the signed slip</text></g>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M662 66H770M763 59l7 7-7 7"/>'
     '<use href="#d-iphone" x="830" y="0" width="120" height="240"/>'
     + ''.join(f'<rect class="mute" x="{850 + c * 28}" y="{150 + r * 28}" width="20" height="20" rx="5"/>' for r in range(2) for c in range(3)) +
     '<g class="nd lit"><rect class="sh" x="848" y="40" width="84" height="96" rx="12"/></g>'
     '<text class="sm" x="890" y="64" text-anchor="middle">NPay</text><text x="890" y="96" text-anchor="middle" style="font-size:14px;font-weight:700">&#8377;25,000</text>'
     '<text class="sm" x="890" y="118" text-anchor="middle" style="font-size:9px">widget</text>'
     '<text class="fill-teal" x="972" y="96">allowed:</text><text class="sm fill-teal" x="972" y="116">the widget shows</text><text class="sm fill-teal" x="972" y="134">the balance</text></g>',
     '<g class="fade" data-lit="4+">' + bundle(186, 'ShopEasy.app', 'app', 'no App Group', '4+', '') +
     '<path class="wire" d="M364 252H558V114M551 121l7-7 7 7"/>'
     '<g class="nd alert"><rect class="sh" x="440" y="270" width="236" height="48" rx="12"/><use href="#i-cross" x="454" y="281" width="26" height="26"/>'
     '<text x="490" y="300">refused</text></g>'
     '<text class="sm" x="690" y="300">asks for NPay&#8217;s shared folder</text></g>']
for k, cap in enumerate(['NPay&#8217;s team writes the request: an App Group shared with the widget',
                         'At build time it is signed into the app: nobody can change it later',
                         'iOS reads the signed slip: the widget may use the shared folder and show the balance',
                         'ShopEasy&#8217;s slip has no App Group: iOS refuses']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}" x="568" y="356" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Entitlements &middot; conceptual', 'Entitlements: a signed permission slip', f"""  <div class="body">
    {svg('0 0 1136 368', 'NPay.app carries a signed entitlement slip for an App Group; iOS checks it and the NPay widget shows the balance; ShopEasy&rsquo;s slip has no App Group, so iOS refuses.', 'ent3', P, 'max-height:390px')}{cues(4)}
    <div class="rule step" data-label="Not a switch">An app cannot switch an entitlement on at run time. If it is <b>not on the signed slip</b>, iOS refuses.</div>
  </div>""", notes(
    ('SAY', 'NPay wants a home-screen widget that shows the balance. The app and the widget need a folder they share, and that needs a special capability: an entitlement. Think of it as a permission slip inside the app. Click: NPay&rsquo;s team writes the request in Xcode: an App Group shared with the widget.'),
    ('SAY', 'Click: at build time the slip is signed into NPay.app, sealed with the signature, so nobody can change it later. Click: at run time iOS reads the signed slip, and the widget may use the shared folder: there is the balance on the home screen.'),
    ('SAY', 'Click: ShopEasy asks for NPay&rsquo;s shared folder, but its slip has no App Group, so iOS refuses. Click: an entitlement is not a switch an app turns on at run time; what is not on the signed slip, iOS refuses.'),
    ('ASK', 'Can NPay add an entitlement to itself after the user installs it?'),
    ('EXPECT', 'No. The slip is sealed into the signature at build time; changing it breaks the signature.'),
    ('CONNECT', 'Entitlements are often confused with permissions. Compare them.'))))
# rebuilt (user review, same style as entitlements): who decides: the signed slip (team, build time) vs the user's choice on the phone (run time)
P = ['<text class="mono" x="0" y="14">ENTITLEMENT &#183; NPAY&#8217;S TEAM DECIDES, AT BUILD TIME</text>', '<path class="wire faint" d="M566 4V300"/>',
     '<text class="mono" x="600" y="14">PRIVACY PERMISSION &#183; THE USER DECIDES, AT RUN TIME</text>',
     '<g class="fade" data-lit="1+"><rect class="wire dash" style="fill:none" x="20" y="40" width="440" height="140" rx="16"/>'
     '<use href="#i-bank" x="36" y="54" width="24" height="24"/><text x="68" y="72">NPay.app</text>'
     '<g class="nd lit"><rect class="sh" x="42" y="92" width="396" height="66" rx="10"/><use href="#i-file" x="54" y="112" width="24" height="24"/>'
     '<text class="sm" x="86" y="118">Entitlements</text><text x="86" y="140">App Group: shared with the widget</text></g>'
     '<circle class="wire lit" style="fill:var(--paper)" cx="430" cy="68" r="24"/><text class="mono fill-teal" x="430" y="72" text-anchor="middle" style="font-size:10px">SIGNED</text>'
     '<text class="sm" x="240" y="214" text-anchor="middle">fixed in the app; the user never sees it</text></g>',
     '<g class="fade" data-lit="2+"><use href="#d-iphone" x="790" y="26" width="140" height="280"/>'
     '<g class="nd"><rect class="sh" x="800" y="110" width="120" height="112" rx="12"/></g>'
     '<text x="860" y="134" text-anchor="middle" style="font-size:11px;font-weight:700">&#8220;NPay&#8221; would</text>'
     '<text x="860" y="148" text-anchor="middle" style="font-size:11px;font-weight:700">like to use</text>'
     '<text x="860" y="162" text-anchor="middle" style="font-size:11px;font-weight:700">the camera</text>'
     '<text class="sm" x="860" y="180" text-anchor="middle" style="font-size:9px">To scan cheques</text>'
     '<path class="wire faint" d="M800 190H920M860 190V222"/>'
     '<text class="sm" x="830" y="210" text-anchor="middle" style="font-size:9px">Don&#8217;t Allow</text></g>',
     '<g class="fade" data-lit="2"><text class="sm" x="890" y="210" text-anchor="middle" style="font-size:9px">Allow</text></g>',
     '<g class="fade" data-lit="3+"><g class="nd lit"><rect class="sh" x="862" y="194" width="56" height="26" rx="6"/></g>'
     '<text class="sm fill-teal" x="890" y="211" text-anchor="middle" style="font-size:9px;font-weight:700">Allow</text>'
     '<use href="#i-tap" x="906" y="208" width="24" height="24"/>'
     '<text class="sm" x="960" y="160">the user chose;</text><text class="sm" x="960" y="178">can change it later</text><text class="sm" x="960" y="196">in Settings</text></g>']
for k, cap in enumerate(['An entitlement: NPay&#8217;s team writes it, and it is signed into the app',
                         'A permission: when NPay first needs the camera, iOS asks the user',
                         'The user taps Allow; they can take it back any time in Settings']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="340" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Comparison', 'Entitlements vs privacy permissions', f"""  <div class="body">
    {svg('0 0 1136 352', 'Left: an entitlement is a signed slip inside NPay.app, decided by the team at build time. Right: a privacy permission is the user&rsquo;s choice on an iOS prompt at run time, for example the camera.', 'entperm', P, 'max-height:400px')}{cues(3)}
    <div class="rule step" data-label="Who decides?">Entitlement: <b>the team</b>, at build time. Permission: <b>the user</b>, at run time. Some features need <b>both</b>.</div>
  </div>""", notes(
    ('SAY', 'Two things that sound alike but differ in one question: who decides? Click: an entitlement, like the App Group from the last slide. NPay&rsquo;s team writes it and it is signed into the app; it is fixed, and the user never sees it.'),
    ('SAY', 'Click: a privacy permission. The first time NPay needs the camera, to scan a cheque, iOS shows the user a prompt with NPay&rsquo;s reason. Click: the user taps Allow, and can take it back at any time in Settings.'),
    ('SAY', 'Click: so an entitlement is decided by the team at build time, a permission by the user at run time. Some features need both: a signed capability and the user&rsquo;s yes.'),
    ('ASK', 'Can NPay turn the camera on without asking, because it is a signed, trusted app?'),
    ('EXPECT', 'No. Signing does not replace the user&rsquo;s permission.'),
    ('CONNECT', 'Let&rsquo;s follow that camera permission more closely: scanning a cheque.'))))
# rebuilt (user review): 0.7's "Scanning a cheque" refocused on the "no" path; three phones, one per click
def prompt(c, choose):
    o = (f'<g class="nd"><rect class="sh" x="{c - 60}" y="104" width="120" height="112" rx="12"/></g>'
         f'<text x="{c}" y="128" text-anchor="middle" style="font-size:11px;font-weight:700">&#8220;NPay&#8221; would</text>'
         f'<text x="{c}" y="142" text-anchor="middle" style="font-size:11px;font-weight:700">like to use</text>'
         f'<text x="{c}" y="156" text-anchor="middle" style="font-size:11px;font-weight:700">the camera</text>'
         f'<text class="sm" x="{c}" y="174" text-anchor="middle" style="font-size:9px">To scan cheques</text>'
         f'<path class="wire faint" d="M{c - 60} 184H{c + 60}M{c} 184V216"/>'
         f'<text class="sm" x="{c + 30}" y="204" text-anchor="middle" style="font-size:9px">Allow</text>')
    o += (f'<g class="nd lit"><rect class="sh" x="{c - 58}" y="188" width="56" height="26" rx="6"/></g>'
          f'<text class="sm fill-teal" x="{c - 30}" y="205" text-anchor="middle" style="font-size:9px;font-weight:700">Don&#8217;t Allow</text>'
          f'<use href="#i-tap" x="{c - 30}" y="214" width="22" height="22"/>' if choose else
          f'<text class="sm" x="{c - 30}" y="204" text-anchor="middle" style="font-size:9px">Don&#8217;t Allow</text>')
    return o
phone = lambda c: f'<use href="#d-iphone" x="{c - 70}" y="20" width="140" height="280"/>'
P = [f'<g class="fade" data-lit="1+">{phone(190)}{prompt(190, True)}<text class="mono" x="190" y="12" text-anchor="middle">FIRST TIME</text></g>',
     '<g class="fade" data-lit="2+"><path class="wire" d="M270 160H488M481 153l7 7-7 7"/><text class="sm" x="379" y="148" text-anchor="middle">a week later</text>'
     f'{phone(568)}<text class="mono" x="568" y="12" text-anchor="middle">TAPS SCAN AGAIN</text>'
     '<text x="568" y="84" text-anchor="middle" style="font-size:14px;font-weight:800">NPay</text>'
     '<rect class="wire" style="fill:none" x="512" y="100" width="112" height="26" rx="6"/><text class="sm" x="568" y="117" text-anchor="middle">Scan cheque</text>'
     '<use href="#i-tap" x="590" y="124" width="22" height="22"/>'
     '<text class="sm" x="568" y="176" text-anchor="middle">no prompt:</text><text class="sm" x="568" y="194" text-anchor="middle">iOS asks only once</text></g>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M648 160H866M859 153l7 7-7 7"/>'
     f'{phone(946)}<text class="mono" x="946" y="12" text-anchor="middle">NPAY STILL WORKS</text>'
     '<use href="#i-eye" x="932" y="70" width="28" height="28"/><text x="946" y="122" text-anchor="middle" style="font-size:12px;font-weight:700">Camera is off</text>'
     '<g class="nd lit"><rect class="sh" x="888" y="140" width="116" height="30" rx="8"/><text class="sm" x="946" y="160" text-anchor="middle">Enter details</text></g>'
     '<rect class="wire" style="fill:none" x="888" y="180" width="116" height="30" rx="8"/><text class="sm" x="946" y="200" text-anchor="middle">Open Settings</text></g>']
for k, cap in enumerate(['The first time, the user taps Don&#8217;t Allow',
                         'A week later they tap Scan again: iOS shows no prompt. It asks only once',
                         'So NPay offers another way: type the cheque details, or turn the camera on in Settings']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="340" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Camera permission', 'When the user says no', f"""  <div class="body">
    {svg('0 0 1136 352', 'The user taps Don&rsquo;t Allow on the camera prompt; a week later tapping Scan shows no prompt because iOS asks only once; NPay offers to enter the cheque details or open Settings.', 'sayno', P, 'max-height:400px')}{cues(3)}
    <div class="rule step" data-label="Design for no">The user can refuse, and NPay must <b>still work</b>. Explain the reason <b>before</b> iOS asks: you only get one prompt.</div>
  </div>""", notes(
    ('SAY', 'The last slide showed the user saying yes. What if they say no? Click: the first time NPay needs the camera, the user taps Don&rsquo;t Allow.'),
    ('SAY', 'Click: a week later they tap Scan cheque again. No prompt appears: iOS asks only once. NPay cannot nag the user with the prompt again.'),
    ('SAY', 'Click: so NPay must still work: it offers to type the cheque details by hand, and a button that opens Settings, where only the user can switch the camera on.'),
    ('SAY', 'Click: design for no. And because you only get one prompt, explain the reason in your own screen before iOS asks. The reason text on the prompt itself is required too: an app that asks for the camera without one is stopped by iOS. Unit 11, lesson 11.8, covers privacy declarations.'),
    ('ASK', 'Can NPay secretly switch the camera on, as we asked at the start of this Part?'),
    ('EXPECT', 'No. Camera access goes through iOS and the user&rsquo;s choice.'),
    ('CONNECT', 'Now the third question: can a malicious app replace another app&rsquo;s executable?'))))
# rebuilt (user review, same style as entitlements): the app sealed on the Mac; iOS checks the seal before it runs; a changed app is refused
def appbox(y, name, sub, seal, seal_cls, lit_):
    return (f'<g class="fade" data-lit="{lit_}"><rect class="wire dash" style="fill:none" x="0" y="{y}" width="360" height="110" rx="16"/>'
            f'<use href="#i-bank" x="16" y="{y + 16}" width="24" height="24"/><text x="48" y="{y + 34}">{name}</text>'
            f'<text class="sm" x="48" y="{y + 54}">{sub}</text>'
            f'<circle class="wire {seal_cls}" style="fill:var(--paper)" cx="310" cy="{y + 56}" r="30"/>'
            f'<text class="mono{" fill-teal" if seal_cls == "lit" else ""}" x="310" y="{y + 60}" text-anchor="middle" style="font-size:10px">{seal}</text></g>')
P = ['<text class="mono" x="0" y="14">ON THE MAC &#183; BUILD TIME</text><text class="mono" x="458" y="14">ON THE IPHONE &#183; EVERY LAUNCH</text>',
     appbox(30, 'NPay.app', 'built by NPay&#8217;s team', 'SIGNED', 'lit', '1+'),
     '<g class="fade" data-lit="2+"><path class="wire" d="M364 85H452M445 78l7 7-7 7"/></g>',
     '<g class="nd" data-lit="2"><rect class="sh" x="458" y="40" width="210" height="90" rx="14"/><use href="#i-shield" x="549" y="52" width="28" height="28"/>'
     '<text x="563" y="100" text-anchor="middle">iOS checks the seal</text><text class="sm" x="563" y="118" text-anchor="middle">who built it? unchanged?</text></g>',
     '<g class="fade" data-lit="3+"><g class="nd"><rect class="sh" x="458" y="40" width="210" height="90" rx="14"/><use href="#i-shield" x="549" y="52" width="28" height="28"/>'
     '<text x="563" y="100" text-anchor="middle">iOS checks the seal</text><text class="sm" x="563" y="118" text-anchor="middle">who built it? unchanged?</text></g></g>',
     '<g class="fade" data-lit="2+"><path class="wire" d="M672 85H760M753 78l7 7-7 7"/>'
     '<g class="nd lit"><rect class="sh" x="766" y="50" width="370" height="70" rx="12"/><use href="#i-check" x="780" y="72" width="26" height="26"/>'
     '<text x="818" y="81">Seal intact: NPay runs</text><text class="sm" x="818" y="100">still inside its sandbox and permissions</text></g></g>',
     appbox(176, 'NPay.app, changed', 'someone altered one file', 'BROKEN', 'dash', '3+'),
     '<g class="fade" data-lit="3+"><path class="wire" d="M364 231H563V136M556 143l7-7 7 7"/>'
     '<g class="nd alert"><rect class="sh" x="766" y="196" width="370" height="70" rx="12"/><use href="#i-cross" x="780" y="218" width="26" height="26"/>'
     '<text x="818" y="227">Seal broken: it will not launch</text><text class="sm" x="818" y="246">iOS refuses the changed code</text></g>'
     '<path class="wire" d="M672 120V231H760M753 224l7 7-7 7"/></g>']
for k, cap in enumerate(['On the Mac, NPay&#8217;s team seals the app with its signature',
                         'Every launch, iOS checks the seal: built by NPay&#8217;s team and unchanged, so it runs',
                         'If anyone changes the app, the seal breaks and iOS will not launch it']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="314" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Code signing &middot; conceptual', 'Code signing: a seal iOS checks', f"""  <div class="body">
    {svg('0 0 1136 326', 'NPay.app is sealed with its signature on the Mac; at every launch iOS checks the seal: intact, it runs; changed, the seal is broken and iOS refuses to launch it.', 'sign2', P)}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="Identity, not safety">The seal proves <b>who built it</b> and that it is <b>unchanged</b>. It does not prove the code is <b>secure</b>.</div>
  </div>""", notes(
    ('SAY', 'The third question from the start of this Part: can a malicious app replace another app&rsquo;s code? Click: on the Mac, NPay&rsquo;s team seals the finished app with its signature, like the wax seal on a letter.'),
    ('SAY', 'Click: every time NPay launches, iOS checks the seal. It was built by NPay&rsquo;s team and nothing has changed, so NPay runs, still inside its sandbox and permissions: signing does not bypass those.'),
    ('SAY', 'Click: if anyone changes even one file in the app, the seal breaks, and iOS will not launch it. So a malicious app cannot swap in its own code.'),
    ('SAY', 'Click: but be careful. The seal proves who built the app and that it is unchanged. It does not prove NPay&rsquo;s own code has no security bugs.'),
    ('ASK', 'Does a valid signature mean NPay has no security vulnerabilities?'),
    ('EXPECT', 'No. It proves identity and integrity, not that the logic is secure.'),
    ('CONNECT', 'Inside a secure app: where should secrets live?'))))
# rebuilt (user review, concrete style): what each store actually holds after sign-in; a token in the plain file vs locked in the Keychain
P = ['<rect class="wire dash" style="fill:none" x="0" y="0" width="540" height="250" rx="16"/>',
     '<text class="mono" x="20" y="30">NPAY&#8217;S CONTAINER &#183; SANDBOX</text>',
     '<g class="nd" data-lit="1"><rect class="sh" x="30" y="48" width="480" height="180" rx="14"/></g>',
     '<use href="#i-file" x="48" y="64" width="26" height="26"/><text x="86" y="83">UserDefaults</text><text class="sm" x="210" y="83">a plain preferences file</text>',
     '<g class="fade" data-lit="1+"><text class="mono" x="52" y="122" style="font-size:15px">theme: dark</text><text class="mono" x="52" y="148" style="font-size:15px">onboardingDone: true</text></g>',
     '<g class="fade" data-lit="2"><g class="nd alert"><rect class="sh" x="44" y="164" width="452" height="50" rx="10"/>'
     '<text class="mono" x="60" y="186" style="font-size:15px">token: 7f3a9c&#8230;e21b</text><text class="sm" x="60" y="205">readable as plain text, e.g. from a backup</text></g></g>',
     '<text class="mono" x="620" y="30">MANAGED BY IOS &#183; OUTSIDE THE CONTAINER</text>',
     '<g class="nd" data-lit="3+"><rect class="sh" x="620" y="48" width="516" height="180" rx="14"/></g>',
     '<use href="#i-key" x="638" y="64" width="26" height="26"/><text x="676" y="83">Keychain</text><text class="sm" x="772" y="83">an encrypted store</text>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M500 189H612M605 182l7 7-7 7"/><text class="sm" x="580" y="210" text-anchor="middle">move it</text>'
     '<text class="mono" x="644" y="130" style="font-size:15px">token: &#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;</text>'
     '<text class="sm" x="644" y="152">encrypted; only NPay can read it</text>'
     '<use href="#i-lock" x="644" y="172" width="22" height="22"/><text class="sm" x="674" y="188">readable only while the phone is unlocked</text></g>']
for k, cap in enumerate(['UserDefaults: a plain file for small settings, like the theme',
                         'Put the sign-in token there, and anyone with a copy of the file can read it',
                         'The Keychain keeps it encrypted, outside the app, and locked with the phone']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="288" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Storage choice &middot; conceptual', 'UserDefaults vs Keychain', f"""  <div class="body">
    {svg('0 0 1136 300', 'UserDefaults is a plain preferences file in NPay&rsquo;s container holding the theme; a token stored there is readable; the Keychain, managed by iOS outside the container, keeps the token encrypted and readable only while the phone is unlocked.', 'kc2', P)}{cues(3)}
    <div class="gap"></div>
    <div class="rule step" data-label="The token goes in the Keychain">Settings in <b>UserDefaults</b>; secrets in the <b>Keychain</b>. Never put a token in a plain file.</div>
  </div>""", notes(
    ('ASK', 'After sign-in, NPay has a token that proves who the user is. Where should it go?'),
    ('SAY', 'Click: UserDefaults is a plain preferences file inside NPay&rsquo;s container, perfect for small settings such as the theme or whether onboarding is done.'),
    ('SAY', 'Click: put the token there and it sits in that file as plain text. Anyone who gets a copy of the file, for example from an unencrypted backup or a debugging tool, can read it and act as the user.'),
    ('SAY', 'Click: the Keychain is managed by iOS, outside the app&rsquo;s container, and encrypts every item. Only NPay can read its own items, and an item can be set to be readable only while the phone is unlocked. Unit 07, lesson 7.3, goes deeper.'),
    ('SAY', 'Click: settings in UserDefaults, secrets in the Keychain.'),
    ('CONNECT', 'Who protects the keys that encrypt the Keychain? Hardware.'))))
# rebuilt (user review, concrete style): Face ID approving a payment; secrets stay inside the Secure Enclave, only answers come out
P = ['<use href="#d-iphone" x="40" y="10" width="140" height="280"/>',
     '<text x="110" y="74" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text>',
     '<text class="sm" x="110" y="98" text-anchor="middle">Pay ravi@npay</text><text x="110" y="122" text-anchor="middle" style="font-size:16px;font-weight:700">&#8377;1,500</text>',
     '<g class="fade" data-lit="1-2"><g class="nd lit"><rect class="sh" x="62" y="148" width="96" height="64" rx="12"/></g><use href="#i-user" x="98" y="156" width="24" height="24"/>'
     '<text class="sm fill-teal" x="110" y="200" text-anchor="middle">Face ID</text></g>',
     '<g class="fade" data-lit="3+"><text class="sm fill-teal" x="110" y="188" text-anchor="middle">Approved</text></g>',
     '<text class="mono" x="440" y="22" text-anchor="middle">INSIDE THE IPHONE&#8217;S CHIP</text>',
     '<g class="nd" data-lit="2-3"><rect class="sh" x="300" y="34" width="280" height="160" rx="16"/></g>',
     '<use href="#i-chip" x="316" y="50" width="26" height="26"/><text x="354" y="69">Secure Enclave</text><text class="sm" x="354" y="88">a sealed vault</text>',
     '<g class="fade" data-lit="2+"><path class="wire" d="M184 180H294M287 173l7 7-7 7"/><text class="sm" x="240" y="168" text-anchor="middle">your face</text>'
     '<text class="sm" x="320" y="124">&#10003; face matched inside</text><text class="sm" x="320" y="144">face data never leaves</text></g>',
     '<g class="fade" data-lit="3+"><use href="#i-key" x="320" y="154" width="22" height="22"/><text class="sm" x="348" y="170">NPay&#8217;s private key signs it</text>'
     '<path class="wire" d="M584 114H700M693 107l7 7-7 7"/><text class="sm" x="642" y="102" text-anchor="middle">only the</text><text class="sm" x="642" y="134" text-anchor="middle">signature</text>'
     '<g class="nd lit"><rect class="sh" x="706" y="80" width="300" height="70" rx="12"/><use href="#i-bank" x="720" y="102" width="26" height="26"/>'
     '<text x="758" y="110">Bank API server</text><text class="sm" x="758" y="130">checks the signature: approved</text></g></g>',
     '<g class="fade" data-lit="4+"><path class="wire dash" d="M440 198V236"/><g class="nd"><rect class="sh" x="300" y="240" width="360" height="62" rx="12"/>'
     '<use href="#i-key" x="316" y="258" width="26" height="26"/><text x="354" y="266">Keychain: token &#8226;&#8226;&#8226;&#8226;</text>'
     '<text class="sm" x="354" y="286">stored outside; the Enclave guards its key</text></g></g>']
for k, cap in enumerate(['The user confirms a &#8377;1,500 payment with Face ID',
                         'The face is matched inside the Secure Enclave: face data never leaves it',
                         'NPay&#8217;s private key, kept inside, signs the payment: only the signature goes out',
                         'The Keychain token is stored outside: the Enclave guards the key that encrypts it']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="568" y="336" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 7 &middot; Secure Enclave &middot; conceptual', 'The Secure Enclave: a vault for keys', f"""  <div class="body">
    {svg('0 0 1136 348', 'The user confirms a payment with Face ID; the face is matched inside the Secure Enclave; NPay&rsquo;s private key inside it signs the payment and only the signature goes to the bank; the Keychain token is stored outside, its key guarded by the Enclave.', 'enclave2', P, 'max-height:400px')}{cues(4)}
    <div class="rule step" data-label="Vault, not database">Secrets stay <b>inside</b>; only answers come out. Keychain items are <b>not</b> stored there.</div>
  </div>""", notes(
    ('SAY', 'Who protects the most sensitive secrets? A separate part of the iPhone&rsquo;s chip, the Secure Enclave: a sealed vault. Click: the user confirms a &#8377;1,500 payment with Face ID.'),
    ('SAY', 'Click: the face is matched inside the Secure Enclave. The face data never leaves it, not even to NPay or iOS. Click: NPay keeps a private key inside the Enclave; the key signs the payment, and only the signature goes out to the bank, which checks it. The key itself never leaves.'),
    ('SAY', 'Click: and the Keychain token from the last slide? It is stored outside the Enclave, in the encrypted Keychain; the Enclave guards the key that encrypts it.'),
    ('SAY', 'Click: so the Secure Enclave is a vault for keys, not a database: secrets stay inside, only answers come out. Unit 07, lesson 7.5, uses it from Swift.'),
    ('ASK', 'Are Keychain items stored inside the Secure Enclave?'),
    ('EXPECT', 'No. They are in the encrypted Keychain; the Enclave protects the keys.'),
    ('CONNECT', 'Let&rsquo;s recap Part 7.'))))
take(7, 21, 7, connect='Two quick questions on Part 7.')
question(7, 23, 7, 0, 'Next question.')
question(7, 26, 7, 1, 'Part 8: leaving the device. How does ₹25,000 reach NPay?')


# ================================================================== Part 8 · networking (0.8)
part(8, 'Networking', 'From a Refresh tap to the bank&rsquo;s server and back',
     'The balance does not live on the phone. Follow one Refresh tap to the bank&rsquo;s server and back.',
     ('service', 'frameworks', 'https', 'server'),
     'The security walls around NPay.', 'The network path: Service, URLSession, HTTPS and the bank&rsquo;s server.',
     'The teal is on the path out of the device: the Service, the frameworks that do the networking, the HTTPS connection and the bank&rsquo;s server.')
take(8, 5, 8)
# rebuilt (Part 8 audit, concrete style): one Refresh tap from the phone to the bank and back, six plain steps
P = ['<use href="#d-iphone" x="20" y="16" width="130" height="260"/>',
     '<text x="85" y="78" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text>',
     '<g class="fade" data-lit="0-5"><text x="85" y="112" text-anchor="middle" style="font-size:15px;font-weight:700">&#8377;25,000</text></g>',
     '<g class="fade" data-lit="0"><text class="sm" x="85" y="136" text-anchor="middle">2 hours ago</text></g>',
     '<g class="fade" data-lit="1-5"><text class="sm fill-teal" x="85" y="136" text-anchor="middle">Updating&#8230;</text></g>',
     '<g class="fade" data-lit="6+"><text class="fill-teal" x="85" y="112" text-anchor="middle" style="font-size:15px;font-weight:700">&#8377;25,000</text><text class="sm fill-teal" x="85" y="136" text-anchor="middle">updated now</text></g>',
     '<g class="nd" data-lit="1"><rect class="sh" x="40" y="150" width="90" height="28" rx="7"/><text class="sm" x="85" y="169" text-anchor="middle">Refresh</text></g>',
     '<text class="mono" x="560" y="14" text-anchor="middle">GOING OUT</text><text class="mono" x="560" y="290" text-anchor="middle">COMING BACK</text>',
     '<g class="nd" data-lit="2"><rect class="sh" x="210" y="34" width="250" height="70" rx="12"/><use href="#i-send" x="224" y="56" width="26" height="26"/><text x="262" y="64">NPay builds a request</text><text class="sm" x="262" y="84">balance of account 123 + token</text></g>',
     '<path class="wire" d="M154 69H204M197 62l7 7-7 7M464 69H560M553 62l7 7-7 7"/>',
     '<g class="nd" data-lit="3"><rect class="sh" x="566" y="34" width="210" height="70" rx="12"/><use href="#i-lock" x="580" y="56" width="26" height="26"/><text x="618" y="64">Over the internet</text><text class="sm" x="618" y="84">encrypted (HTTPS)</text></g>',
     '<path class="wire" d="M780 69H866M859 62l7 7-7 7"/>',
     '<g class="nd" data-lit="4"><rect class="sh" x="872" y="34" width="264" height="206" rx="14"/><use href="#i-bank" x="890" y="54" width="28" height="28"/><text x="928" y="74">Bank API server</text>'
     '<text class="sm" x="890" y="110">checks the token</text><text class="sm" x="890" y="130">reads the real balance</text><text class="sm" x="890" y="150">replies with JSON</text></g>',
     '<path class="wire" d="M866 206H780M787 199l-7 7 7 7"/>',
     '<g class="nd" data-lit="4"><rect class="sh" x="566" y="172" width="210" height="70" rx="12"/><use href="#i-file" x="580" y="194" width="26" height="26"/><text x="618" y="202">The answer</text><text class="sm" x="618" y="222">the balance, in paise</text></g>',
     '<path class="wire" d="M560 206H464M471 199l-7 7 7 7"/>',
     '<g class="nd" data-lit="5"><rect class="sh" x="210" y="172" width="250" height="70" rx="12"/><use href="#i-check" x="224" y="194" width="26" height="26"/><text x="262" y="202">NPay decodes it</text><text class="sm" x="262" y="222">then formats &#8377;25,000</text></g>',
     '<path class="wire" d="M204 206H158M165 199l-7 7 7 7"/>']
for k, cap in enumerate(['The user taps Refresh: NPay shows Updating&#8230; and the main thread stays free',
                         'NPay builds a request: the balance of account 123, with the sign-in token',
                         'It travels over the internet, encrypted by HTTPS',
                         'The bank checks the token and replies with the real balance, as JSON',
                         'NPay checks the answer, decodes it and formats &#8377;25,000',
                         'The screen shows the new balance']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 5 else ""}" x="568" y="326" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; Request journey &middot; conceptual', 'A Refresh tap, step by step', f"""  <div class="body">
    {svg('0 0 1136 338', 'A Refresh tap: NPay builds a request with the token, it travels encrypted over the internet, the bank checks the token and replies with JSON, NPay decodes it and the screen shows the new balance.', 'journey6', P, 'max-height:420px')}{cues(6)}
  </div>""", notes(
    ('SAY', 'Six steps, one Refresh tap, out to the bank and back. Click: the user taps Refresh. NPay shows Updating, and from here the waiting happens off the main thread, so the app stays responsive.'),
    ('SAY', 'Click: NPay builds a request: the balance of account 123, with the sign-in token attached. Click: it travels over the internet, encrypted by HTTPS. Click: the bank checks the token, reads the real balance, and replies with JSON: 2,500,000 paise.'),
    ('SAY', 'Click: NPay checks the answer was a success, decodes it, and formats &#8377;25,000. Click: the screen shows the new balance. Notice who does what: the request itself is sent by Apple&rsquo;s networking framework, URLSession, not by SwiftUI.'),
    ('ASK', 'During which steps can the user still scroll NPay?'),
    ('EXPECT', 'All of them: the waiting happens off the main thread.'),
    ('CONNECT', 'Look closer at the request NPay sends in step 2.'))))
take(8, 9, 8)
# rebuilt (Part 8 audit): read vs change, and why it matters for repeating a request
P = ['<text class="mono" x="0" y="14">READ &#183; GET</text>', '<path class="wire faint" d="M566 4V250"/>', '<text class="mono" x="600" y="14">CHANGE &#183; POST</text>',
     '<g class="fade" data-lit="1+"><g class="nd"><rect class="sh" x="0" y="32" width="250" height="60" rx="12"/><use href="#i-send" x="14" y="49" width="26" height="26"/><text x="52" y="58">Get the balance</text><text class="sm" x="52" y="78">sent twice</text></g>'
     '<path class="wire" d="M254 62H300M293 55l7 7-7 7"/>'
     '<g class="nd"><rect class="sh" x="306" y="32" width="230" height="60" rx="12"/><text x="322" y="58">&#8377;25,000</text><text class="sm" x="322" y="78">first answer</text></g>'
     '<g class="nd"><rect class="sh" x="306" y="104" width="230" height="60" rx="12"/><text x="322" y="130">&#8377;25,000</text><text class="sm" x="322" y="150">same again</text></g>'
     '<text class="fill-teal" x="0" y="206">Safe to repeat</text><text class="sm" x="0" y="228">nothing changes on the server</text></g>',
     '<g class="fade" data-lit="2+"><g class="nd"><rect class="sh" x="600" y="32" width="250" height="60" rx="12"/><use href="#i-send" x="614" y="49" width="26" height="26"/><text x="652" y="58">Send &#8377;1,500</text><text class="sm" x="652" y="78">sent twice</text></g>'
     '<path class="wire" d="M854 62H900M893 55l7 7-7 7"/>'
     '<g class="nd"><rect class="sh" x="906" y="32" width="230" height="60" rx="12"/><text x="922" y="58">&#8722;&#8377;1,500</text><text class="sm" x="922" y="78">first payment</text></g>'
     '<g class="nd alert"><rect class="sh" x="906" y="104" width="230" height="60" rx="12"/><text x="922" y="130">&#8722;&#8377;1,500 again</text><text class="sm" x="922" y="150">a second payment</text></g>'
     '<text x="600" y="206">Not safe to repeat</text><text class="sm" x="600" y="228">each one moves money</text></g>']
for k, cap in enumerate(['Reading the balance twice gives the same answer', 'Sending &#8377;1,500 twice sends two payments']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 1 else ""}" x="568" y="276" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; Methods', 'Read vs change: GET and POST', f"""  <div class="body">
    {svg('0 0 1136 288', 'Getting the balance twice gives the same answer: safe to repeat. Sending 1,500 rupees twice makes two payments: not safe to repeat.', 'getpost', P)}{cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="Safe to repeat?">Safe to repeat is called <b>idempotent</b>. Never blindly repeat a request that <b>moves money</b>.</div>
  </div>""", notes(
    ('SAY', 'Every request says what it wants to do. The two you will see most: GET reads, POST changes. Click: GET the balance twice and you get the same answer twice; nothing changed on the server, so it is safe to repeat.'),
    ('SAY', 'Click: POST a &#8377;1,500 payment twice and the bank makes two payments. Each one moves money, so it is not safe to repeat.'),
    ('SAY', 'Click: a request that is safe to repeat is called idempotent. This matters when the network fails and the app wonders whether to try again; we come back to it on the failure slide. There are other methods, PUT, PATCH and DELETE; Unit 05, lesson 5.1, covers them. The server always decides and checks authorization.'),
    ('CONNECT', 'How is the request protected on its way?'))))
# rebuilt (Part 8 audit, concrete style): what someone on the same café Wi-Fi can see, without and with HTTPS
P = ['<use href="#d-iphone" x="0" y="20" width="110" height="220"/><text x="55" y="80" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text>'
     '<text x="55" y="108" text-anchor="middle" style="font-size:14px;font-weight:700">&#8377;25,000</text><text class="sm" x="55" y="132" text-anchor="middle">Updating&#8230;</text>',
     '<g class="nd"><rect class="sh" x="936" y="80" width="200" height="90" rx="14"/><use href="#i-bank" x="1022" y="94" width="28" height="28"/><text x="1036" y="148" text-anchor="middle">Bank server</text></g>',
     '<path class="wire" d="M118 125H930M923 118l7 7-7 7"/>',
     '<g class="nd"><rect class="sh" x="400" y="20" width="300" height="56" rx="12"/><use href="#i-globe" x="414" y="35" width="26" height="26"/><text x="452" y="54">Caf&#233; Wi-Fi</text></g>',
     '<use href="#i-user" x="530" y="170" width="28" height="28"/><text class="sm" x="544" y="214" text-anchor="middle">someone else on the Wi-Fi</text>',
     '<g class="fade" data-lit="1"><g class="nd alert"><rect class="sh" x="300" y="226" width="500" height="54" rx="10"/><text class="mono" x="316" y="250" style="font-size:14px">token: 7f3a9c&#8230;  balance: 2500000</text><text class="sm" x="316" y="270">without HTTPS: readable</text></g></g>',
     '<g class="fade" data-lit="2+"><g class="nd lit"><rect class="sh" x="300" y="226" width="500" height="54" rx="10"/><text class="mono" x="316" y="250" style="font-size:14px">x8#q!7&#8230;k2%Zp&#8230;</text><text class="sm" x="316" y="270">with HTTPS: scrambled</text></g>'
     '<use href="#i-lock" x="500" y="112" width="26" height="26"/></g>',
     '<g class="fade" data-lit="3+"><text class="sm fill-teal" x="1036" y="196" text-anchor="middle">&#10003; really the bank</text></g>']
for k, cap in enumerate(['Without HTTPS, anyone on the same Wi-Fi could read the token and the balance',
                         'With HTTPS the trip is encrypted: they see only scrambled data',
                         'HTTPS also proves NPay is talking to the real bank, not an impostor']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="320" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; HTTPS &middot; conceptual', 'HTTPS: an encrypted, checked connection', f"""  <div class="body">
    {svg('0 0 1136 332', 'NPay talks to the bank over caf&eacute; Wi-Fi. Without HTTPS someone else on the Wi-Fi can read the token and balance; with HTTPS they see scrambled data, and NPay knows it reached the real bank.', 'https2', P, 'max-height:400px')}{cues(3)}
    <div class="rule step" data-label="One layer">HTTPS protects the <b>trip</b>. Sign-in, the token in the Keychain and the bank&rsquo;s own checks are still needed.</div>
  </div>""", notes(
    ('SAY', 'NPay is on caf&eacute; Wi-Fi, and someone else is on the same network. Click: without HTTPS, that person could read the token and the balance as they pass by. With the token, they could act as the user.'),
    ('SAY', 'Click: with HTTPS, the trip is encrypted; they see only scrambled data. Click: and HTTPS checks the server&rsquo;s certificate, so NPay knows it is talking to the real bank, not an impostor.'),
    ('SAY', 'Click: but HTTPS protects only the trip. Signing in, keeping the token in the Keychain and the bank&rsquo;s own checks are still needed: security is layered. iOS expects HTTPS by default; Unit 07, lesson 7.6, covers certificates.'),
    ('ASK', 'Is HTTPS enough to make a banking app secure?'),
    ('EXPECT', 'No. It protects the connection; the other layers are still needed.'),
    ('CONNECT', 'HTTPS carries the sign-in too. Where does the token come from?'))))
# rebuilt (user review, concrete style): sign in once, then the token is the pass for every request; an expired token means sign in again
pc = 80
scr = lambda lit_, body: f'<g class="fade" data-lit="{lit_}">{body}</g>'
P = ['<use href="#d-iphone" x="10" y="10" width="140" height="280"/>',
     scr('0-1', f'<text x="{pc}" y="70" text-anchor="middle" style="font-size:13px;font-weight:800">Sign in</text>'
         f'<rect class="wire" style="fill:none" x="34" y="86" width="92" height="20" rx="5"/><text class="sm" x="40" y="100" style="font-size:9px">priya@npay</text>'
         f'<rect class="wire" style="fill:none" x="34" y="114" width="92" height="20" rx="5"/><text class="sm" x="40" y="128" style="font-size:9px">&#8226;&#8226;&#8226;&#8226;&#8226;&#8226;</text>'
         f'<rect class="wire" style="fill:none" x="46" y="144" width="68" height="20" rx="6"/><text class="sm" x="{pc}" y="158" text-anchor="middle" style="font-size:9px">Sign in</text>'),
     scr('2-4', f'<text x="{pc}" y="74" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text>'
         f'<text x="{pc}" y="104" text-anchor="middle" style="font-size:15px;font-weight:700">&#8377;25,000</text>'),
     scr('5+', f'<text x="{pc}" y="96" text-anchor="middle" style="font-size:11px;font-weight:700">Please sign</text>'
         f'<text x="{pc}" y="112" text-anchor="middle" style="font-size:11px;font-weight:700">in again</text>'),
     '<g class="nd"><rect class="sh" x="900" y="10" width="236" height="280" rx="16"/><use href="#i-bank" x="1004" y="26" width="28" height="28"/><text x="1018" y="76" text-anchor="middle">Bank server</text></g>',
     '<g class="fade" data-lit="1+"><path class="wire" d="M156 60H894M887 53l7 7-7 7"/><text class="sm" x="525" y="50" text-anchor="middle">email + password, over HTTPS (once)</text></g>',
     '<g class="fade" data-lit="2+"><path class="wire" d="M894 104H156M163 97l7 7-7 7"/><text class="sm" x="525" y="94" text-anchor="middle">password is right: here is a token</text>'
     '<g class="nd lit"><rect class="sh" x="930" y="92" width="176" height="44" rx="10"/><use href="#i-key" x="942" y="102" width="22" height="22"/><text class="sm" x="972" y="112">token: Priya,</text><text class="sm" x="972" y="128">valid for a while</text></g></g>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M80 294V318H262"/><g class="nd lit"><rect class="sh" x="266" y="296" width="260" height="46" rx="10"/>'
     '<use href="#i-key" x="278" y="308" width="22" height="22"/><text x="308" y="324">Keychain: the token</text></g>'
     '<text class="sm" x="540" y="324">not the password</text></g>',
     '<g class="fade" data-lit="4+"><path class="wire" d="M156 160H894M887 153l7 7-7 7"/><text class="sm" x="525" y="150" text-anchor="middle">&#8220;my balance?&#8221; + token</text>'
     '<path class="wire" d="M894 196H156M163 189l7 7-7 7"/><text class="sm" x="525" y="186" text-anchor="middle">&#8377;25,000 (no password needed)</text></g>',
     '<g class="fade" data-lit="5+"><path class="wire" d="M894 246H156M163 239l7 7-7 7"/>'
     '<g class="nd alert"><rect class="sh" x="380" y="222" width="290" height="48" rx="10"/><text x="396" y="244">401: token expired</text><text class="sm" x="396" y="262">the user signs in again</text></g></g>']
for k, cap in enumerate(['The user signs in once: email and password go to the bank over HTTPS',
                         'The bank checks them and hands back a token: a pass that says &#8220;this is Priya&#8221;',
                         'NPay keeps the token in the Keychain, never the password',
                         'Every later request carries the token: no password needed',
                         'When the token expires, the bank answers 401, and the user signs in again']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 4 else ""}" x="568" y="380" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; Signing in &middot; conceptual', 'Where the token comes from', f"""  <div class="body">
    {svg('0 0 1136 392', 'The user signs in once; the bank returns a token; NPay stores it in the Keychain; later requests carry the token; when it expires the bank answers 401 and the user signs in again.', 'token2', P, 'max-height:440px')}{cues(5)}
    <div class="rule step" data-label="Token">The password is used <b>once</b>; the token is the <b>pass</b> for every request after.</div>
  </div>""", notes(
    ('SAY', 'How does the bank know a request really comes from Priya? Click: she signs in once. Her email and password go to the bank, encrypted by HTTPS.'),
    ('SAY', 'Click: the bank checks them and hands back a token: a pass that says &ldquo;this is Priya&rdquo;, valid for a while. Like a wristband at an event: you show your ticket once, then the wristband gets you in. Click: NPay keeps the token in the Keychain, as in Part 7, and never stores the password.'),
    ('SAY', 'Click: every later request carries the token, so no password is needed. Click: tokens expire. When it does, the bank answers 401, unauthorized, and NPay asks the user to sign in again.'),
    ('SAY', 'Click: the password is used once; the token is the pass for every request after. Real apps also refresh tokens and check authorization on the server; Unit 05, lesson 5.5, and Unit 07, lesson 7.10, build that.'),
    ('ASK', 'Why does NPay keep the token and not the password?'),
    ('EXPECT', 'A token can expire and be revoked; a leaked token is less damaging than a leaked password.'),
    ('CONNECT', 'Inside the app, who coordinates the request?'))))

# ---- slides 110-113 rebuilt (user review, concrete style): who does what, UI = f(state), five outcomes on the phone, leaving mid-download
def npay_phone(x, w=140, h=280):
    return f'<use href="#d-iphone" x="{x}" y="10" width="{w}" height="{h}"/>'

# 110: each layer with what it does during one Refresh tap
LAY = [('phone', 'View', 'what the user sees', 'Shows the balance, a spinner, or a message'),
       ('layout', 'ViewModel', 'the screen&#8217;s state', 'Sets &#8220;loading&#8221;, asks the Service, formats &#8377;25,000'),
       ('link', 'Service', 'talks to the bank', 'Sends the request with the token, decodes the answer'),
       ('bank', 'Bank server', 'owns the real data', 'Checks the token, replies with the balance')]
P = ['<text class="mono" x="0" y="14">LAYER</text><text class="mono" x="460" y="14">ITS JOB IN ONE REFRESH TAP</text>']
for k, (ic, t, sub, job) in enumerate(LAY):
    y = 26 + k * 72
    P.append(f'<g class="nd" data-lit="{k + 1}"><rect class="sh" x="0" y="{y}" width="1136" height="60" rx="12"/><use href="#i-{ic}" x="14" y="{y + 17}" width="26" height="26"/>'
             f'<text x="52" y="{y + 27}">{t}</text><text class="sm" x="52" y="{y + 46}">{sub}</text></g>')
    P.append(f'<text class="fade" data-lit="{k + 1}+" x="460" y="{y + 36}" style="font-size:18px">{job}</text>')
    if k < 3:
        P.append(f'<path class="wire" d="M300 {y + 60}V{y + 72}"/>')
S.append(slide('Part 8 &middot; MVVM &middot; conceptual', 'Who does what in one Refresh', f"""  <div class="body">
    {svg('0 0 1136 314', 'View, ViewModel, Service and bank server, each with its job in one Refresh tap', 'whodoes', P)}{cues(4)}
    <div class="gap"></div>
    <div class="rule step" data-label="Each layer, one job">The View never talks to the bank; the Service never draws. The <b>ViewModel</b> sits between them.</div>
  </div>""", notes(
    ('SAY', 'Inside NPay, who does what during one Refresh tap? One layer per click. The View is what the user sees: the balance, a spinner, or a message.'),
    ('SAY', 'The ViewModel holds the screen&rsquo;s state: it sets loading, asks the Service for the balance, and formats paise as &#8377;25,000. It runs on the main thread, because its state feeds the screen, and waits for the Service without blocking.'),
    ('SAY', 'The Service talks to the bank: it sends the request with the token and decodes the answer. And the bank server owns the real data: it checks the token and replies.'),
    ('SAY', 'Click: each layer has one job. The View never talks to the bank, the Service never draws; the ViewModel sits between them. This is MVVM, from Part 1; Unit 04 builds it.'),
    ('CONNECT', 'And when the answer arrives, how does it reach the screen?'))))

# 111: the screen as a function of the ViewModel's state
STATES = [('loading: yes', 'balance: &#8377;25,000', 'error: none', [('sm fill-teal', 'Updating&#8230;')]),
          ('loading: no', 'balance: &#8377;24,750', 'error: none', [('big', '&#8377;24,750')]),
          ('loading: no', 'balance: &#8377;24,750', 'error: offline', [('sm', 'You&#8217;re offline'), ('big', '&#8377;24,750'), ('sm', 'last updated 9:05')])]
P = ['<text class="mono" x="0" y="14">THE VIEWMODEL&#8217;S STATE</text><text class="mono" x="560" y="14">WHAT THE SCREEN SHOWS</text>',
     '<path class="wire" d="M450 150H640M633 143l7 7-7 7"/><text class="sm" x="545" y="138" text-anchor="middle">SwiftUI draws it</text>',
     npay_phone(780), '<text x="850" y="72" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text>']
for k, (l1, l2, l3, scr) in enumerate(STATES):
    lit_ = f'{k + 1}{"+" if k == 2 else ""}'
    P.append(f'<g class="fade" data-lit="{lit_}"><g class="nd lit"><rect class="sh" x="0" y="44" width="420" height="200" rx="14"/></g>'
             f'<text class="mono" x="24" y="96" style="font-size:17px">{l1}</text><text class="mono" x="24" y="140" style="font-size:17px">{l2}</text>'
             f'<text class="mono" x="24" y="184" style="font-size:17px">{l3}</text>')
    y = 104
    for cls, t in scr:
        if cls == 'big':
            P.append(f'<text x="850" y="{y + 4}" text-anchor="middle" style="font-size:16px;font-weight:700">{t}</text>')
        else:
            P.append(f'<text class="{cls}" x="850" y="{y}" text-anchor="middle">{t}</text>')
        y += 26
    P.append('</g>')
for k, cap in enumerate(['While loading, the screen shows Updating&#8230;',
                         'The answer arrives: the state changes, and the screen follows',
                         'Offline: the state says so, and the screen shows the last known balance']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="326" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; Response to screen &middot; conceptual', 'UI = f(state)', f"""  <div class="body">
    {svg('0 0 1136 338', 'Three states of the ViewModel and the screen SwiftUI draws for each: loading shows Updating, a new balance shows 24,750 rupees, offline shows the last known balance.', 'uifstate', P, 'max-height:400px')}{cues(3)}
    <div class="rule step" data-label="UI = f(state)">Change the <b>state</b>; SwiftUI redraws the screen to match, only the parts that changed.</div>
  </div>""", notes(
    ('SAY', 'The screen is a function of the state: UI equals f of state. On the left, three values the ViewModel holds; on the right, what SwiftUI draws for them. Click: while loading is yes, the screen shows Updating.'),
    ('SAY', 'Click: the answer arrives, the balance becomes &#8377;24,750 and loading becomes no; nobody tells the screen what to do, it simply follows the state. Click: if the request fails offline, the state records the error, and the screen shows &ldquo;You&rsquo;re offline&rdquo; with the last known balance and its time.'),
    ('SAY', 'Click: change the state, and SwiftUI redraws to match, only the parts that changed, as we saw in Part 5.'),
    ('CONNECT', 'Not every request succeeds. What then?'))))

# 112: five outcomes, each as what the phone shows
OUT = [('Success', [('big', '&#8377;25,000'), ('sm', 'updated now')], 'nd lit'),
       ('No network', [('sm', 'You&#8217;re offline'), ('big', '&#8377;25,000'), ('sm', 'as of 9:05'), ('btn', 'Retry')], 'nd'),
       ('401', [('sm', 'Session expired'), ('btn', 'Sign in again')], 'nd'),
       ('Timeout', [('sm', 'Taking longer'), ('sm', 'than expected'), ('btn', 'Try again')], 'nd'),
       ('500', [('sm', 'Bank problem'), ('sm', 'not your fault'), ('sm', 'Try later')], 'nd')]
P = []
for k, (t, scr, cls) in enumerate(OUT):
    x = k * 230
    cx = x + 100
    P.append(f'<g class="nd" data-lit="{k + 1}"><rect class="sh" x="{x + 10}" y="0" width="180" height="40" rx="10"/><text x="{cx}" y="26" text-anchor="middle">{t}</text></g>')
    body = npay_phone(x + 40, 120, 240).replace('y="10"', 'y="52"') + f'<text x="{cx}" y="104" text-anchor="middle" style="font-size:12px;font-weight:800">NPay</text>'
    y = 132
    for c2, tx in scr:
        if c2 == 'big':
            body += f'<text x="{cx}" y="{y + 4}" text-anchor="middle" style="font-size:15px;font-weight:700">{tx}</text>'
        elif c2 == 'btn':
            body += f'<rect class="wire" style="fill:none" x="{cx - 42}" y="{y - 12}" width="84" height="22" rx="6"/><text class="sm" x="{cx}" y="{y + 3}" text-anchor="middle" style="font-size:10px">{tx}</text>'
        else:
            body += f'<text class="sm" x="{cx}" y="{y}" text-anchor="middle" style="font-size:10px">{tx}</text>'
        y += 24
    P.append(f'<g class="fade" data-lit="{k + 1}+">{body}</g>')
for k, cap in enumerate(['Success: the new balance', 'No network: the last known balance, clearly dated, and Retry',
                         '401: the token expired, so sign in again', 'Timeout: the outcome is unknown; check before trying again',
                         '500: the bank had a problem, not the user; try later']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 4 else ""}" x="568" y="330" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; Failure explorer &middot; illustrative', 'Five possible outcomes', f"""  <div class="body">
    {svg('0 0 1136 342', 'Five outcomes of a request and what NPay shows for each: success, no network, 401, timeout, server error.', 'five2', P, 'max-height:400px')}{cues(5)}
    <div class="warn step" data-label="Payments">A payment that timed out <b>may already have gone through</b>. Never retry it automatically.</div>
  </div>""", notes(
    ('SAY', 'A request can end five ways, and each needs its own screen. Click: success, the new balance. Click: no network: show the last known balance, clearly dated, and a Retry button. Click: 401: the token expired, so ask the user to sign in again.'),
    ('SAY', 'Click: timeout: no answer in time, so the outcome is unknown. For a balance, trying again is fine. Click: 500: the bank had a problem; not the user&rsquo;s fault, try later.'),
    ('SAY', 'Click: the dangerous one. A payment that timed out may already have gone through. Retrying it automatically could send the money twice: remember GET versus POST. Real apps protect payments so a repeat can be detected; Unit 05, lesson 5.6, covers retries.'),
    ('ASK', 'Should NPay automatically retry a payment that timed out?'),
    ('EXPECT', 'No. It may have succeeded; check its status first.'),
    ('CONNECT', 'One more case: the user leaves the app mid-request.'))))

# 113: leaving the app mid-download, three phones
P = [f'<g class="fade" data-lit="1+">{npay_phone(40)}<text class="mono" x="110" y="0" text-anchor="middle">STARTS DOWNLOAD</text>'
     '<text x="110" y="72" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text><text class="sm" x="110" y="100" text-anchor="middle">Statement.pdf</text>'
     '<rect class="mute" x="60" y="114" width="100" height="10" rx="5"/><g class="nd lit"><rect class="sh" x="60" y="114" width="40" height="10" rx="5"/></g>'
     '<text class="sm" x="110" y="144" text-anchor="middle">40%</text></g>',
     '<g class="fade" data-lit="2"><path class="wire" d="M184 150H370M363 143l7 7-7 7"/><text class="sm" x="277" y="138" text-anchor="middle">user leaves</text>'
     f'{npay_phone(430)}<text class="mono" x="500" y="0" text-anchor="middle">ORDINARY REQUEST</text>'
     '<text class="sm" x="500" y="100" text-anchor="middle">NPay suspended</text><g class="nd alert"><rect class="sh" x="440" y="120" width="120" height="48" rx="10"/>'
     '<text x="500" y="141" text-anchor="middle" style="font-size:13px">download</text><text x="500" y="158" text-anchor="middle" style="font-size:13px">stops</text></g></g>',
     '<g class="fade" data-lit="3+"><path class="wire" d="M184 150H370M363 143l7 7-7 7"/><text class="sm" x="277" y="138" text-anchor="middle">user leaves</text>'
     f'{npay_phone(430)}<text class="mono" x="500" y="0" text-anchor="middle">BACKGROUND DOWNLOAD</text>'
     '<text class="sm" x="500" y="100" text-anchor="middle">NPay suspended,</text><text class="sm" x="500" y="118" text-anchor="middle">iOS keeps going</text>'
     '<rect class="mute" x="450" y="132" width="100" height="10" rx="5"/><g class="nd lit"><rect class="sh" x="450" y="132" width="100" height="10" rx="5"/></g>'
     '<path class="wire" d="M574 150H760M753 143l7 7-7 7"/><text class="sm" x="667" y="138" text-anchor="middle">user returns</text>'
     f'{npay_phone(820)}<text class="mono" x="890" y="0" text-anchor="middle">READY</text>'
     '<text x="890" y="72" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text><g class="nd lit"><rect class="sh" x="836" y="96" width="108" height="40" rx="8"/>'
     '<use href="#i-file" x="846" y="104" width="22" height="22"/><text class="sm" x="874" y="120">Statement</text></g></g>']
for k, cap in enumerate(['The user starts downloading a statement in NPay',
                         'They leave: an ordinary request stops when iOS suspends NPay',
                         'A background download is handed to iOS, which finishes it: ready when they return']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="330" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 8 &middot; Background transfers', 'What happens when the app is backgrounded?', f"""  <div class="body">
    {svg('0 0 1136 342', 'The user starts downloading a statement and leaves NPay: an ordinary request stops when NPay is suspended; a background download is finished by iOS and ready when the user returns.', 'bgdl', P, 'max-height:400px')}{cues(3)}
    <div class="rule step" data-label="Downloads and uploads only">iOS finishes <b>transfers</b> for NPay; it does not keep NPay&rsquo;s own code running. A <b>force-quit</b> cancels them.</div>
  </div>""", notes(
    ('SAY', 'Click: the user starts downloading a monthly statement in NPay, then switches to another app halfway.'),
    ('SAY', 'Click: with an ordinary request, iOS suspends NPay soon after, and the download stops. Click: with a background download, NPay hands the transfer to iOS, which keeps downloading while NPay is suspended, even if iOS ends NPay. When the user comes back, the statement is ready.'),
    ('SAY', 'Click: but iOS only finishes uploads and downloads; it does not keep NPay&rsquo;s own code running. And if the user force-quits NPay from the app switcher, iOS cancels its transfers. Unit 05, lesson 5.8, builds one.'),
    ('CONNECT', 'Let&rsquo;s recap Part 8.'))))
# 0.8's "The complete path" dropped (Part 8 audit): the request-journey slide now shows the whole round trip
take(8, 25, 8, connect='Two quick questions on Part 8.', subs=[
     ('Validate, then decode', 'Encrypted, never blocking'), ('any 2xx status, then Codable into a Balance', 'HTTPS on the way; the main thread stays free'),
     ('only when repeating is safe: idempotent requests', 'repeat only what is safe: never a payment'),
     ('BalanceService validates the status, any 2xx, before decoding JSON into a Balance.', 'The request travels encrypted, and the waiting never blocks the main thread.')])
question(8, 27, 8, 0, 'Next question.')
question(8, 30, 8, 1, 'Part 9: what NPay keeps on the device, and where.',
         subs=[('Spaced review from 0.5. While <code>fetchBalance()</code> awaits the server', 'Spaced review from Part 5. While NPay awaits the balance from the server'),
               ('While fetchBalance() awaits the server', 'While NPay awaits the balance from the server'),
               ('The task is suspended at await, not blocking the thread, so the main thread keeps running its RunLoop.', 'The wait happens off the main thread, so its RunLoop keeps taking taps.', 2),
               ('Treating await like a blocking call.', 'Thinking that waiting for the network freezes the app.')])


# ================================================================== Part 9 · storage (0.9)
part(9, 'Data storage', 'What survives termination, and where it belongs',
     'Memory is gone when the process ends. What should NPay keep, and where?',
     ('storage', 'keychain'),
     'The network path to the bank&rsquo;s server.', 'Storage on the device: UserDefaults, files, SwiftData and the Keychain.',
     'The teal is on storage and the Keychain, the two places NPay&rsquo;s data can outlive its process.')
# ---- Part 9 rebuilt (user: same as Parts 7-8): memory vs storage, NPay's folders, which store for which data, cached vs current, the database stack
def item(x, y, w, ic, t, sub, lit_, cls=''):
    return (f'<g class="fade" data-lit="{lit_}"><g class="nd{(" " + cls) if cls else ""}"><rect class="sh" x="{x}" y="{y}" width="{w}" height="56" rx="12"/>'
            f'<use href="#i-{ic}" x="{x + 14}" y="{y + 15}" width="26" height="26"/><text x="{x + 52}" y="{y + 25}">{t}</text><text class="sm" x="{x + 52}" y="{y + 43}">{sub}</text></g></g>')

# 118: what survives a restart
MEM = [('eye', '&#8377;25,000 on the screen', 'drawn from memory'), ('file', 'A half-typed note', '&#8220;Rent for Ma&#8230;&#8221;'), ('layers', 'Where the list was scrolled', 'screen position')]
STO = [('gear', 'Dark mode: on', 'a setting'), ('db', 'Saved transactions', 'NPay&#8217;s database'), ('key', 'The sign-in token', 'in the Keychain')]
P = ['<text class="mono" x="0" y="14">MEMORY (RAM) &#183; THE COUNTER</text>', '<path class="wire faint" d="M566 4V250"/>', '<text class="mono" x="600" y="14">STORAGE &#183; THE PANTRY</text>']
for k, (ic, t, sub) in enumerate(MEM):
    y = 30 + k * 70
    P.append(item(0, y, 520, ic, t, sub, '1'))
    P.append(item(0, y, 520, ic, t, 'gone', '2+', 'ghost'))
for k, (ic, t, sub) in enumerate(STO):
    y = 30 + k * 70
    P.append(item(600, y, 536, ic, t, sub, '1'))
    P.append(item(600, y, 536, ic, t, 'still there', '2+', 'lit'))
for k, cap in enumerate(['NPay is open: some things live only in memory, some are saved in storage',
                         'The phone restarts: memory is wiped, storage is still there']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 1 else ""}" x="568" y="270" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 9 &middot; Memory vs storage', 'What survives a restart?', f"""  <div class="body">
    {svg('0 0 1136 282', 'While NPay runs, the balance on screen, a half-typed note and the scroll position live in memory; dark mode, saved transactions and the token are in storage. After a restart, memory is gone and storage is still there.', 'survive', P)}{cues(2)}
    <div class="gap"></div>
    <div class="rule step" data-label="Memory vs storage">Memory is the chef&rsquo;s <b>counter</b>, cleared every night. Storage is the <b>pantry</b>: still there tomorrow.</div>
  </div>""", notes(
    ('SAY', 'Two very different places for NPay&rsquo;s data. Click: while NPay is open, some things live only in memory: the balance drawn on screen, a half-typed note, where the list was scrolled. Others are saved in storage: the dark-mode setting, saved transactions, the sign-in token in the Keychain.'),
    ('SAY', 'Click: the phone restarts, or iOS ends NPay as in Part 3. Memory is wiped; storage is still there. That is why anything that matters must be saved.'),
    ('SAY', 'Click: in the kitchen, memory is the counter the chef works on, cleared every night; storage is the pantry, still there tomorrow.'),
    ('CONNECT', 'Inside storage, NPay&rsquo;s files have their own places.'))))

# 120: NPay's folders
FOLD = [('Documents', 'files the user made', 'Receipt-June.pdf', 'backed up &#183; visible in Files'),
        ('Application Support', 'NPay&#8217;s own data', 'npay.store', 'backed up &#183; hidden'),
        ('Caches', 'can be downloaded again', 'Statement-May.pdf', 'not backed up &#183; iOS may delete'),
        ('tmp', 'short-lived', 'upload-part.tmp', 'deleted soon')]
P = ['<rect class="wire dash" style="fill:none" x="0" y="0" width="1136" height="276" rx="16"/>',
     '<use href="#i-bank" x="16" y="14" width="24" height="24"/><text x="48" y="32">NPay&#8217;s container</text>']
for k, (f, sub, fn, note) in enumerate(FOLD):
    x = 20 + k * 278
    gone = k >= 2
    P.append(f'<g class="nd" data-lit="{k + 1}"><rect class="sh" x="{x}" y="50" width="262" height="76" rx="12"/><use href="#i-folder" x="{x + 14}" y="66" width="26" height="26"/>'
             f'<text x="{x + 52}" y="78">{f}</text><text class="sm" x="{x + 52}" y="98">{sub}</text></g>')
    P.append(f'<g class="fade" data-lit="{k + 1}{"-4" if gone else "+"}"><path class="wire" d="M{x + 131} 128V146"/>{item(x, 150, 262, "file", fn, note, "0+")}</g>'.replace('<g class="fade" data-lit="0+">', '<g>'))
    if gone:
        P.append(f'<g class="fade" data-lit="5+"><path class="wire" d="M{x + 131} 128V146"/>{item(x, 150, 262, "file", fn, "deleted: space was low", "0+", "ghost")}</g>'.replace('<g class="fade" data-lit="0+">', '<g>'))
P.append('<g class="fade" data-lit="5+"><g class="nd alert"><rect class="sh" x="576" y="222" width="540" height="40" rx="10"/><text x="592" y="248">iPhone low on space: iOS clears Caches and tmp</text></g></g>')
for k, cap in enumerate(['Documents: what the user made, like an exported receipt', 'Application Support: NPay&#8217;s own data, like its database',
                         'Caches: things NPay can download again, like a statement', 'tmp: short-lived files', 'Space runs low: iOS may delete Caches and tmp, and NPay downloads again']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 4 else ""}" x="568" y="310" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 9 &middot; Sandbox directories', 'Where an app keeps its files', f"""  <div class="body">
    {svg('0 0 1136 322', 'NPay&rsquo;s container has four folders: Documents with a receipt, Application Support with its database, Caches with a statement and tmp with a temporary file; when space is low, iOS clears Caches and tmp.', 'folders', P)}{cues(5)}
    <div class="gap"></div>
    <div class="rule step" data-label="Folders">Keep what matters in <b>Documents</b> or <b>Application Support</b>. <b>Caches</b> and <b>tmp</b> can disappear.</div>
  </div>""", notes(
    ('SAY', 'Inside NPay&rsquo;s container are four folders, each with its own rules. Click: Documents holds what the user made, like an exported receipt; it is backed up and can be shown in the Files app. Click: Application Support holds NPay&rsquo;s own data, like its database: backed up, hidden from the user.'),
    ('SAY', 'Click: Caches holds things NPay can download again, like a monthly statement: not backed up. Click: tmp holds short-lived files, such as part of an upload.'),
    ('SAY', 'Click: when the iPhone runs low on space, iOS may delete Caches and tmp. NPay simply downloads the statement again. Files can also be protected so they stay encrypted while the phone is locked; Unit 06, lesson 6.5.'),
    ('CONNECT', 'So which storage for which data?'))))

# 121: which store for which data
MAP = [('gear', 'Dark mode', 'a small setting', 'UserDefaults', 'a plain settings file'),
       ('key', 'Sign-in token', 'a secret', 'Keychain', 'encrypted, managed by iOS'),
       ('file', 'Monthly statement', 'can be downloaded again', 'Caches folder', 'iOS may delete it'),
       ('db', 'Transaction notes', 'records to search and edit', 'SwiftData', 'NPay&#8217;s database')]
P = ['<text class="mono" x="0" y="14">NPAY&#8217;S DATA</text><text class="mono" x="660" y="14">WHERE IT GOES</text>']
for k, (ic, t, sub, st, ssub) in enumerate(MAP):
    y = 28 + k * 72
    P.append(f'<g class="nd"><rect class="sh" x="0" y="{y}" width="420" height="58" rx="12"/><use href="#i-{ic}" x="14" y="{y + 16}" width="26" height="26"/>'
             f'<text x="52" y="{y + 26}">{t}</text><text class="sm" x="52" y="{y + 45}">{sub}</text></g>')
    P.append(f'<g class="fade" data-lit="{k + 1}+"><path class="wire" d="M424 {y + 29}H654M647 {y + 22}l7 7-7 7"/></g>')
    P.append(item(660, y, 476, ic, st, ssub, f'{k + 1}+', 'lit' if k == 1 else ''))
for k, cap in enumerate(['Dark mode is a small setting: UserDefaults', 'The sign-in token is a secret: the Keychain',
                         'A statement can be downloaded again: the Caches folder', 'Transaction notes are records to search and edit: SwiftData']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 3 else ""}" x="568" y="330" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 9 &middot; Choose the storage', 'Which storage for which data?', f"""  <div class="body">
    {svg('0 0 1136 342', 'Dark mode goes in UserDefaults, the sign-in token in the Keychain, the statement in the Caches folder, transaction notes in SwiftData.', 'which4', P)}{cues(4)}
    <div class="rule step" data-label="Ask first">Not &ldquo;which storage is best?&rdquo; but &ldquo;<b>what kind of data is this?</b>&rdquo; Small setting, secret, file or records.</div>
  </div>""", notes(
    ('SAY', 'Four kinds of NPay data, four homes. Click: dark mode is a small, non-secret setting: UserDefaults. Click: the sign-in token is a secret: the Keychain, as in Part 7.'),
    ('SAY', 'Click: the monthly statement can be downloaded again: a file in the Caches folder. Click: transaction notes are records the user can search and edit: a database, SwiftData.'),
    ('SAY', 'Click: so start with the question &ldquo;what kind of data is this?&rdquo;, not &ldquo;which API is best?&rdquo;. And save as you go, the rule from Part 3: iOS gives no last chance before it ends NPay.'),
    ('CONNECT', 'Saved data raises a different question for a bank: is it still true?'))))
# 0.9's "iOS storage choices" and "A draft that may not survive" dropped (Part 9 rebuild): the first repeated the store-by-data slide, the second Part 3's transitions and coming-back slides

# 123: cached is not current
def cphone(c, top, bal, sub, lit_):
    return (f'<g class="fade" data-lit="{lit_}"><use href="#d-iphone" x="{c - 70}" y="30" width="140" height="280"/>'
            f'<text x="{c}" y="92" text-anchor="middle" style="font-size:13px;font-weight:800">NPay</text>{top}'
            f'<text x="{c}" y="150" text-anchor="middle" style="font-size:17px;font-weight:700">{bal}</text>{sub}</g>')
P = ['<g class="nd"><rect class="sh" x="476" y="40" width="184" height="96" rx="14"/><use href="#i-bank" x="554" y="54" width="28" height="28"/>'
     '<text x="568" y="104" text-anchor="middle">Bank: &#8377;23,500</text><text class="sm" x="568" y="124" text-anchor="middle">rent was paid at 11:00</text></g>',
     '<g class="nd"><rect class="sh" x="476" y="170" width="184" height="56" rx="12"/><use href="#i-globe" x="490" y="185" width="26" height="26"/><text x="528" y="204">offline</text></g>',
     cphone(200, '<text class="mono" x="200" y="20" text-anchor="middle">STALE AS CURRENT</text>', '&#8377;25,000', '', '1+'),
     '<g class="fade" data-lit="1+"><g class="nd alert"><rect class="sh" x="110" y="176" width="180" height="40" rx="10"/><text class="sm" x="200" y="200" text-anchor="middle">looks current: it is not</text></g></g>',
     cphone(936, '<text class="mono" x="936" y="20" text-anchor="middle">HONEST</text><text class="sm fill-teal" x="936" y="118" text-anchor="middle">You&#8217;re offline</text>',
            '&#8377;25,000', '<text class="sm" x="936" y="172" text-anchor="middle">as of 9:05 AM</text>'
            '<rect class="wire" style="fill:none" x="896" y="190" width="80" height="24" rx="6"/><text class="sm" x="936" y="206" text-anchor="middle">Retry</text>', '2+')]
for k, cap in enumerate(['Offline, NPay shows this morning&#8217;s cached &#8377;25,000 as if it were current: the user overspends',
                         'Honest: say it is offline, and show when the balance was last updated']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 1 else ""}" x="568" y="346" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 9 &middot; Freshness &middot; conceptual', 'Cached is not current', f"""  <div class="body">
    {svg('0 0 1136 358', 'The bank now says 23,500 rupees, but NPay is offline with a cached 25,000. Left: shown as if current. Right: shown as offline with the time it was last updated.', 'cached2', P, 'max-height:420px')}{cues(2)}
    <div class="rule step" data-label="The server decides">A cache is a <b>copy</b> with an age. Show the age; the bank&rsquo;s balance is the real one.</div>
  </div>""", notes(
    ('SAY', 'At 9:05 NPay saved the balance, &#8377;25,000. At 11:00 rent was paid from another device, so the bank now says &#8377;23,500. NPay is offline. Click: if NPay shows its cached &#8377;25,000 as if it were current, the user may spend money they do not have.'),
    ('SAY', 'Click: the honest version says &ldquo;You&rsquo;re offline&rdquo;, shows the balance as of 9:05, and offers Retry.'),
    ('SAY', 'Click: a cache is a copy with an age. Show the age, and remember the bank&rsquo;s balance is the real one, as in Part 8. Unit 06, lesson 6.6, builds freshness states.'),
    ('ASK', 'Should NPay hide the cached balance completely while offline?'),
    ('EXPECT', 'No: showing it, clearly dated, is more useful than nothing.'),
    ('CONNECT', 'Finally, the database technologies you will hear about.'))))

# 124: the database stack, with NPay
STK = [('db', 'SwiftData', 'the modern choice for new SwiftUI apps', 'NPay saves its transaction notes here', '1+', 'lit'),
       ('layers', 'Core Data', 'the older choice, still in many apps', 'does the same job in existing apps', '2+', ''),
       ('file', 'SQLite database', 'what both write to underneath', 'one database file&#8230;', '3+', ''),
       ('folder', 'npay.store', 'a file in Application Support', '&#8230;inside NPay&#8217;s container', '3+', '')]
P = ['<text class="mono" x="0" y="14">EASIER TO USE &#8593;</text><text class="mono" x="0" y="330">&#8595; CLOSER TO THE DISK</text>']
for k, (ic, t, sub, ex, lit_, cls) in enumerate(STK):
    y = 26 + k * 72
    P.append(f'<g class="fade" data-lit="{lit_}">' + f'<g class="nd{(" " + cls) if cls else ""}"><rect class="sh" x="0" y="{y}" width="560" height="60" rx="12"/><use href="#i-{ic}" x="14" y="{y + 17}" width="26" height="26"/>'
             f'<text x="52" y="{y + 27}">{t}</text><text class="sm" x="52" y="{y + 46}">{sub}</text></g>'
             f'<text x="620" y="{y + 36}" style="font-size:18px">{ex}</text></g>')
    if k < 3:
        P.append(f'<g class="fade" data-lit="{STK[k + 1][4]}"><path class="wire" d="M280 {y + 60}V{y + 72}"/></g>')
for k, cap in enumerate(['SwiftData: what a new SwiftUI app like NPay starts with', 'Core Data: the same job, in many existing apps',
                         'Underneath, both save to an SQLite database: a file in NPay&#8217;s container']):
    P.append(f'<text class="fade fill-teal" data-lit="{k + 1}{"+" if k == 2 else ""}" x="568" y="370" text-anchor="middle" style="font-size:20px">{k + 1}. {cap}</text>')
S.append(slide('Part 9 &middot; Comparison &middot; conceptual', 'Where NPay&rsquo;s database lives', f"""  <div class="body">
    {svg('0 0 1136 382', 'SwiftData and Core Data both save to an SQLite database, which is a file in Application Support inside NPay&rsquo;s container.', 'dbstack', P, 'max-height:420px')}{cues(3)}
    <div class="rule step" data-label="In the end, a file">Every database is <b>a file in the sandbox</b>. Unit 06 &middot; 6.1 compares them in practice.</div>
  </div>""", notes(
    ('SAY', 'You will hear several database names. Click: SwiftData is the modern choice for a new SwiftUI app; NPay saves its transaction notes there. Click: Core Data does the same job and is still in many existing apps.'),
    ('SAY', 'Click: underneath, both save to an SQLite database, and that database is simply a file, npay.store, in the Application Support folder inside NPay&rsquo;s container.'),
    ('SAY', 'Click: in the end, every database is a file in the sandbox, protected by everything in Part 7. Unit 06, lesson 6.1, compares them in practice.'),
    ('CONNECT', 'Let&rsquo;s recap Part 9.'))))
take(9, 22, 9, connect='Two quick questions on Part 9.')
question(9, 24, 9, 0, 'Next question.')
question(9, 28, 9, 1, 'Part 10: one day with NPay, every layer at once.')


# ================================================================== Part 10 · end to end (0.10)
part(10, 'End to end', 'One day with NPay, every layer at once',
     'Everything from Parts 1 to 9, in one story: the day from this morning&rsquo;s opening slide.',
     (),
     'Nine Parts, one layer at a time.', 'The whole map at once: one day with NPay, from launch to return.',
     'No single teal box this time: every box on the map is involved in one ordinary day with NPay.')
# ---- Part 10 rebuilt (user: same style): the stack with the Part that taught each layer, six protections on one request, the day as three scenes
tag = lambda x, y, t: f'<rect class="wire" style="fill:none" x="{x}" y="{y}" width="{18 + 9 * len(t)}" height="24" rx="12"/><text class="mono" x="{x + 9 + 4.5 * len(t):g}" y="{y + 16}" text-anchor="middle" style="font-size:11px">{t}</text>'

# 127: every layer, and the Part that taught it
STACK = [('phone', 'Screens', 'what the user sees and taps', 'Parts 1, 4'),
         ('layout', 'ViewModel', 'the screen&#8217;s state', 'Parts 1, 8'),
         ('link', 'Service and storage', 'talks to the bank, saves data', 'Parts 8, 9'),
         ('frameworks', 'Apple frameworks', 'SwiftUI, networking, security', 'Parts 2, 5'),
         ('kernel', 'iOS and the kernel', 'process, threads, memory, sandbox', 'Parts 3, 6, 7'),
         ('chip', 'Hardware', 'CPU, GPU, Secure Enclave', 'Part 7')]
P = ['<rect class="wire dash" style="fill:none" x="0" y="0" width="820" height="200" rx="16"/><text class="mono" x="16" y="22">NPAY&#8217;S OWN CODE</text>',
     '<text class="mono" x="16" y="232">THE PLATFORM</text>']
for k, (ic, t, sub, parts) in enumerate(STACK):
    y = 30 + k * 56 + (40 if k >= 3 else 0)
    P.append(f'<g class="nd" data-lit="{k + 1}"><rect class="sh" x="16" y="{y}" width="788" height="46" rx="10"/><use href="#i-{ic}" x="30" y="{y + 11}" width="24" height="24"/>'
             f'<text x="66" y="{y + 29}">{t}</text><text class="sm" x="300" y="{y + 29}">{sub}</text></g>')
    P.append(f'<g class="fade" data-lit="{k + 1}+">{tag(650, y + 11, parts)}</g>')
P.append('<g class="fade" data-lit="7+"><path class="wire" d="M824 140H900M893 133l7 7-7 7"/><text class="sm" x="862" y="128" text-anchor="middle">HTTPS</text>'
         '<g class="nd lit"><rect class="sh" x="906" y="100" width="230" height="80" rx="14"/><use href="#i-bank" x="920" y="124" width="28" height="28"/>'
         '<text x="958" y="136">Bank server</text><text class="sm" x="958" y="156">Part 8</text></g></g>')
S.append(slide('Part 10 &middot; Architecture &middot; conceptual', 'NPay: the complete picture', f"""  <div class="body">
    {svg('0 0 1136 400', 'NPay&rsquo;s own code (screens, ViewModel, service and storage) on top of the platform (Apple frameworks, iOS and the kernel, hardware), connected to the bank server; each layer tagged with the Part that taught it.', 'whole', P, 'max-height:420px')}{cues(7)}
    <div class="rule step" data-label="Two architectures">NPay&rsquo;s <b>own code</b> on top of the <b>platform</b>. Every Part today was one layer of this picture.</div>
  </div>""", notes(
    ('SAY', 'The whole day on one picture, top to bottom, with the Part that taught each layer. Click: the screens the user sees and taps, Parts 1 and 4. Click: the ViewModel, the screen&rsquo;s state, Parts 1 and 8. Click: the service and storage, Parts 8 and 9. That is NPay&rsquo;s own code.'),
    ('SAY', 'Below it, the platform. Click: Apple&rsquo;s frameworks, Parts 2 and 5. Click: iOS and the kernel, with the process, threads, memory and sandbox, Parts 3, 6 and 7. Click: the hardware, with the Secure Enclave, Part 7. Click: and over HTTPS, the bank server, Part 8.'),
    ('SAY', 'Click: two architectures: NPay&rsquo;s own code on top of the platform. If any layer is unclear, the tag tells you which Part to revisit.'),
    ('CONNECT', 'Follow one Refresh balance request: six protections surround it.'))))

# 128: six protections placed on one request
PROT = [('phone', 'Code signing', 'only NPay&#8217;s own, unchanged code runs', 'Part 7', 40, 40),
        ('lock', 'Sandbox', 'other apps cannot reach NPay&#8217;s data', 'Part 7', 40, 112),
        ('key', 'Keychain', 'the token is stored encrypted', 'Part 7', 40, 184),
        ('file', 'File protection', 'saved files locked with the phone', 'Part 9', 40, 256),
        ('globe', 'HTTPS', 'the trip is encrypted and checked', 'Part 8', 470, 112),
        ('bank', 'Bank authorization', 'the bank decides what Priya may see', 'Part 8', 800, 112)]
P = ['<rect class="wire dash" style="fill:none" x="20" y="10" width="410" height="320" rx="16"/><text class="mono" x="36" y="32">ON THE IPHONE</text>',
     '<path class="wire" d="M434 140H464M457 133l7 7-7 7M766 140H794M787 133l7 7-7 7"/>']
for k, (ic, t, sub, part_, x, y) in enumerate(PROT):
    w = 370 if x == 40 else 290 if x == 470 else 336
    cls = 'nd lit' if k == 5 else 'nd'
    P.append(f'<g class="fade" data-lit="{k + 1}+"><g class="{cls}"><rect class="sh" x="{x}" y="{y}" width="{w}" height="60" rx="12"/><use href="#i-{ic}" x="{x + 14}" y="{y + 17}" width="26" height="26"/>'
             f'<text x="{x + 52}" y="{y + 26}">{t}</text><text class="sm" x="{x + 52}" y="{y + 45}">{sub}</text></g>'
             f'<text class="mono" x="{x + w - 10}" y="{y + 26}" text-anchor="end" style="font-size:11px">{part_.upper()}</text></g>')
S.append(slide('Part 10 &middot; Security &middot; conceptual', 'Six protections around one request', f"""  <div class="body">
    {svg('0 0 1136 340', 'One Refresh request: on the iPhone, code signing, the sandbox, the Keychain and file protection; on the way, HTTPS; at the bank, authorization.', 'six2', P, 'max-height:400px')}{cues(6)}
    <div class="rule step" data-label="Layers">Four on the phone, one on the way, one at the bank. <b>None</b> replaces the bank&rsquo;s own check.</div>
  </div>""", notes(
    ('SAY', 'One Refresh request, and every protection around it, in order. On the iPhone: click, code signing, so only NPay&rsquo;s own unchanged code runs. Click: the sandbox, so other apps cannot reach NPay&rsquo;s data. Click: the Keychain, holding the token encrypted. Click: file protection, keeping saved files locked with the phone.'),
    ('SAY', 'Click: on the way, HTTPS encrypts the trip and checks it is the real bank. Click: at the bank, authorization: the bank decides what Priya may see. It must check every request, because the phone can never be fully trusted.'),
    ('SAY', 'Click: four protections on the phone, one on the way, one at the bank, and none of them replaces the bank&rsquo;s own check.'),
    ('CONNECT', 'Now the whole day, from the first tap to coming back.'))))
# 0.10's "Where each piece of data belongs" and "Warm activation or cold launch" dropped (Part 10 rebuild): Part 9 and Part 3 teach them with pictures

# 131: one day with NPay, three scenes
DAY = [('MORNING &#183; OPEN NPAY', [('1', 'Tap the icon', 'SpringBoard asks iOS', '2'), ('2', 'Process starts', 'loaded, then NPay&#8217;s code', '2'), ('3', 'First frame', 'the dashboard appears', '2, 5'), ('4', 'Saved data', 'token and settings read back', '7, 9')]),
       ('REFRESH THE BALANCE', [('5', 'Tap Refresh', 'on the main thread', '5'), ('6', 'Request goes out', 'with the token, over HTTPS', '8'), ('7', 'Bank answers', 'checks, then replies', '8'), ('8', 'Screen updates', 'only what changed', '5, 8')]),
       ('LEAVE AND COME BACK', [('9', 'Save as you go', 'drafts and data', '3, 9'), ('10', 'Home Screen', 'scene to background', '3, 4'), ('11', 'Suspended or ended', 'iOS decides', '3'), ('12', 'Return', 'warm, or a cold launch', '2, 3')])]
P = []
for r, (title_, steps_) in enumerate(DAY):
    y = r * 112
    P.append(f'<g class="fade" data-lit="{r + 1}+"><text class="mono" x="0" y="{y + 14}">{title_}</text>'
             + ''.join(f'<path class="wire" d="M{c * 286 + 272} {y + 61}H{c * 286 + 284}"/>' for c in range(3)) + '</g>')
    def boxes(cls):
        o = ''
        for c, (n, t, sub, pt) in enumerate(steps_):
            x = c * 286
            o += (f'<g class="{cls}"><rect class="sh" x="{x}" y="{y + 24}" width="270" height="74" rx="12"/>'
                  f'<text class="mono" x="{x + 14}" y="{y + 50}">{n}</text><text x="{x + 46}" y="{y + 50}">{t}</text><text class="sm" x="{x + 46}" y="{y + 72}">{sub}</text>'
                  f'<text class="mono" x="{x + 256}" y="{y + 90}" text-anchor="end" style="font-size:10px">PART {pt}</text></g>')
        return o
    P.append(boxes('nd fade" data-lit="' + f'{r + 1}{"+" if r == 2 else ""}'))   # current row: teal (lit and visible on the same element)
    if r < 2:
        P.append(f'<g class="fade" data-lit="{r + 2}+">{boxes("nd")}</g>')                       # earlier rows: grey
S.append(slide('Part 10 &middot; End to end &middot; conceptual', 'One day with NPay, in twelve steps', f"""  <div class="body">
    {svg('0 0 1136 334', 'One day with NPay in three scenes: opening the app, refreshing the balance, leaving and coming back; twelve steps, each tagged with the Part that taught it.', 'day12', P, 'max-height:420px')}{cues(3)}
    <div class="rule step" data-label="The whole day">Every step is something <b>iOS</b> does, something <b>NPay</b> does, or both. You can now explain all twelve.</div>
  </div>""", notes(
    ('SAY', 'The story from this morning&rsquo;s opening slide, now with every layer named. Three scenes. Click: morning. The user taps the icon and SpringBoard asks iOS to open NPay; the process starts and NPay&rsquo;s code is loaded; the first frame shows the dashboard; and the saved token and settings are read back.'),
    ('SAY', 'Click: refreshing the balance. The tap arrives on the main thread; the request goes out with the token over HTTPS; the bank checks and answers; the screen updates only what changed.'),
    ('SAY', 'Click: leaving and coming back. NPay saves as it goes; the Home Screen sends the scene to the background; iOS suspends NPay or ends it; and the return is either warm or a cold launch.'),
    ('SAY', 'Click: every step is something iOS does, something NPay does, or both, and each is tagged with the Part that taught it.'),
    ('ASK', 'Pick one step. Which layer owns it: iOS or NPay&rsquo;s own code?'),
    ('EXPECT', 'For example: step 2 is iOS; step 6 is NPay&rsquo;s service; step 10 is iOS, and NPay reacts.'),
    ('CONNECT', 'Let&rsquo;s recap the whole day.'))))
take(10, 29, 10, connect='Two last questions.')
question(10, 32, 10, 0, 'Next question.')
question(10, 35, 10, 1, 'Let&rsquo;s wrap up.')


# ================================================================== wrap-up
S.append(chapter('Wrap-up', 'Putting it together', 'What comes next, and your checkpoint',
                 'Two last things: where each of today&rsquo;s ideas goes next in the course, and your checkpoint.', 'Where does each of today&rsquo;s ideas go next?').replace('<p class="kicker">Part Wrap-up</p>', '<p class="kicker">Wrap-up</p>'))
take(10, 36, 'Wrap-up', subs=[('<th>Builds on today</th>', '<th>Builds on</th>'),
     ('the ViewModel closure and <code>[weak self]</code>', 'strong and weak references, closures that hold on'),
     ('<code>await</code>, <code>@MainActor</code> and the main thread', 'waiting without blocking the main thread'),
     ('<code>balanceMinor</code> becomes a real Money type', 'the balance in paise becomes a real Money type')],
     connect='Your checkpoint.')
take(10, 37, 'Wrap-up')
take(10, 38, 'Wrap-up', subs=[('<code>await</code> suspends without blocking it', 'waiting never blocks it')])
S.append("""<section class="slide end">
  <div class="body">
    <p class="kicker">Unit 00 complete</p>
    <h2>iOS Architecture Foundations</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: Unit 01 &middot; Swift Language Mastery, the code behind every box on today&rsquo;s map</p>
  </div>
""" + notes(('SAY', 'That completes the architecture foundation: how iOS starts NPay, runs it, protects it, connects it to the bank and stores its data.'),
            ('SAY', 'From Unit 01 on, we write the Swift: types, optionals, functions, structs and classes, ARC and concurrency, ending with NPay&rsquo;s domain model.')) + "</section>\n\n")


# ------------------------------------------------------------------ references to the old lessons -> Parts
LMAP = {'1': '2', '2': '1', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9', '10': '10'}   # lesson 0.N -> Part
part_of = lambda m: f'Part {LMAP[m.group(1)]}'
FIX = [  # (text that identifies the slide, old, new)
    ('Per-window events go to a scene (Part 3)', 'Per-window events go to a scene (Part 3)', 'Per-window events go to a scene (next slide)'),
    ('Per-window events go to a scene', 'Events about one window go to a scene, which is Part 3.', 'Events about one window go to a scene: the next slide.'),
    ('Five possible outcomes', '</b> (Part 3)', '</b> (see HTTP methods)'),
    ('today we only need to know', 'today we only need to know', 'for now we only need to know'),
    ('leads into the rest of this lesson', 'the rest of this lesson', 'the rest of this Part'),
    ('The rest of the lesson answers these', 'The rest of the lesson answers these', 'The rest of this Part answers these'),
    ('Each step names the lesson behind it', 'Each step names the lesson behind it', 'Each step names the Part behind it'),
    ('Checkpoint rubric', 'names the lesson to revisit', 'names the Part to revisit'),
    ('Checkpoint rubric', 'which lesson to revisit', 'which Part to revisit'),
    ('Checkpoint rubric', '<th>Revisit</th>', '<th>Revisit Part</th>'),
]
ACTOR = [('off the main actor', 'off the main thread'), ('away from the main actor', 'away from the main thread'),
         ('on the main actor', 'on the main thread'), ('main actor', 'main thread')]   # no actors in Unit 00 (user); Unit 01 teaches them
PLAIN6 = [('deallocated', 'freed'), ('deallocation', 'freeing'), ('set to nil', 'cleared'), ('becomes nil', 'becomes empty'),
          ('instances', 'objects'), ('Person instance', 'Person object'), ('Apartment instance', 'Apartment object'),
          ('>instance<', '>object<'), ('An instance that', 'An object that'), ('class instance', 'object'), (' instance ', ' object '),
          ('DEALLOCATED', 'FREED'), ('variables to nil', 'variables to nothing'), (' to nil', ' to nothing'),
          ('Strong capture', 'Holds it strongly'), ('Weak capture', 'Holds it weakly'), ('strong capture', 'holds strongly'), ('weak capture', 'holds weakly')]   # Part 6 in plain words (audit)
for k, s in enumerate(S):
    if '<p class="kicker">Part 6' in s or 'data-title="Can two objects that hold each other' in s:
        for a, b in PLAIN6:
            s = s.replace(a, b)
        S[k] = s
for k, s in enumerate(S):
    if 'actor ledger' not in s:
        for a, b in ACTOR:
            s = s.replace(a, b)
    for key, a, b in FIX:
        if key in s:
            s = s.replace(a, b)
    if 'hotel' in s:
        s = s.replace('Lesson 0.1', 'Part 1')
    s = re.sub(r'Lesson 0\.(\d+)', part_of, s)
    s = re.sub(r'Spaced review from 0\.(\d+)', lambda m: 'Spaced review from ' + part_of(m), s)
    if 'Each step names the Part behind it' in s:
        s = re.sub(r'(from|and) 0\.(\d+)', lambda m: f'{m.group(1)} Part {LMAP[m.group(2)]}', s)
    if 'Checkpoint rubric' in s:
        s = re.sub(r'<td>(0\.\d+(?:, 0\.\d+)*)</td>', lambda m: '<td>' + ', '.join(LMAP[x.split('.')[1]] for x in m.group(1).split(', ')) + '</td>', s)
    S[k] = s


# ------------------------------------------------------------------ unique ids across the merged slides
seen = set()
for k, s in enumerate(S):
    for i in re.findall(r' id="([^"]+)"', s):
        if i in seen:
            j = f'{i}_{k}'
            s = re.sub(rf'(id="|aria-labelledby="|href="#){re.escape(i)}"', rf'\g<1>{j}"', s)
            S[k] = s
            i = j
        seen.add(i)

doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Unit 00 — iOS Architecture Foundations</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit 00 — iOS Architecture Foundations">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
open(OUT_ALL, "w").write(doc)
print(len(S), 'slides')
