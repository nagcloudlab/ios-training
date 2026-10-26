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
    for a, b in subs:
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
    for a, b in subs:
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
take(5, 7, 5)

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
    ('CONNECT', 'Swift has a name for &ldquo;runs on the main thread&rdquo;: the MainActor. Are they the same thing?'))))
# simplified (Part 5 audit): three plain rows and one takeaway
S.append(slide('Part 5 &middot; Comparison', 'Main thread vs MainActor', f"""  <div class="body top">
    <table class="tbl" style="font-size:21px">
      <tr><th></th><th>Main thread</th><th>MainActor</th></tr>
      <tr><td><b>What it is</b></td><td>A thread that iOS runs</td><td>A Swift rule: &ldquo;this code runs on the main thread&rdquo;</td></tr>
      <tr><td><b>Who enforces it</b></td><td>iOS, at run time</td><td>The Swift compiler, at build time</td></tr>
      <tr><td><b>NPay example</b></td><td>Handles the Refresh tap, draws frames</td><td>DashboardViewModel&rsquo;s balance is only changed there</td></tr>
    </table>
    <div class="gap"></div>
    <div class="rule step" data-label="Mental model"><b>MainActor</b> is Swift&rsquo;s way of making sure UI code runs on the <b>main thread</b>, checked before the app even runs.</div>
  </div>""", notes(
    ('SAY', 'Two words that sound alike. The main thread is a real thread that iOS runs: it handles NPay&rsquo;s taps and draws its frames. MainActor is a Swift rule that says: this code runs on the main thread. iOS runs the thread; the Swift compiler checks the rule when we build.'),
    ('SAY', 'For NPay: the main thread handles the Refresh tap. DashboardViewModel is marked as main-actor code, so its balance can only be changed on the main thread, where the UI reads it.'),
    ('SAY', 'Click: the mental model. MainActor is Swift&rsquo;s way of making sure UI code runs on the main thread, and the check happens before the app even runs. Unit 01, lesson 1.9, shows the Swift.'),
    ('CONNECT', '&ldquo;Background&rdquo; is a word we use for three different things.'))))
take(5, 19, 5, subs=[   # shortened to NPay examples (Part 5 audit)
    ('<span class="label">Asynchronous I/O</span>', '<span class="label">1 &middot; Waiting</span>'),
    ('<span class="label">CPU-bound parallel work</span>', '<span class="label">2 &middot; Computing</span>'),
    ('<span class="label">iOS background execution</span>', '<span class="label">3 &middot; After the user leaves</span>'),
    ('<p>Network requests that <b>wait without occupying a thread</b>. Most file APIs are <b>synchronous</b>: keep large reads and writes off the main actor.</p>',
     '<p><b>Waiting</b>: fetching NPay&rsquo;s balance from the bank.</p><p class="small muted" style="margin:6px 0 0">No thread sits idle while it waits.</p>'),
    ('<p>Image processing, data transformation and expensive calculations that need <b>CPU time away from the main actor</b>.</p>',
     '<p><b>Computing</b>: sorting a year of NPay transactions.</p><p class="small muted" style="margin:6px 0 0">Needs CPU time away from the main thread.</p>'),
    ('<p>Work allowed while the app is <b>no longer foreground</b>, subject to system policies and capabilities.</p>',
     '<p><b>After the user leaves</b>: finishing an upload NPay started.</p><p class="small muted" style="margin:6px 0 0">Only with iOS&rsquo;s permission, as in Part 3.</p>')])
take(5, 21, 5)
take(5, 23, 5, subs=[('SwiftUI&rsquo;s <code>body</code> is a <b>description</b>, not a drawing function. Recomputing it does not mean every element is redrawn.',
                     'A SwiftUI view is a <b>description</b>, not a drawing. Recomputing it does <b>not</b> redraw every element: only what changed.'),
                    ('Recall from Lesson 0.2: body is a description of UI, not a drawing function. Recomputing a body does not mean every element is redrawn.',
                     'Recall from Part 1: a view is a description of the screen, not a drawing. Recomputing it does not mean every element is redrawn.')])
take(5, 25, 5, connect='Two kinds of slow work, and why the difference matters.')

# code-free: 0.5's "Waiting vs computing" + "async does not mean background", without code
c27 = re.search(r'<div class="cols stretch">.*?</div>\s*</div>(?=\s*<div class="gap">)', SRC[5][26], re.S).group(0)
S.append(slide('Part 5 &middot; Two kinds of slow', 'Waiting vs computing', f"""  <div class="body">
    {c27}
    <div class="gap"></div>
    <div class="cols stretch">
      <p class="small step" style="margin:0">While the balance request <b>waits</b>, the task <b>suspends</b>: no thread sits idle waiting.</p>
      <p class="small step" style="margin:0">A long <b>calculation</b> occupies a thread until it ends. On the main thread, the UI waits.</p>
    </div>
    <div class="gap"></div>
    <div class="rule step"><b>async</b> enables suspension. It does <b>not</b> guarantee parallel execution or a different thread.</div>
  </div>""", notes(('SAY', 'Operation A downloads the NPay balance: mostly waiting for the bank&rsquo;s server. Operation B processes a million transaction records: mostly executing calculations. Both take time, for different reasons.'),
                  ('SAY', 'Click: while the network request waits, the calling task suspends and the thread is free. Click: a calculation is different: it keeps a thread busy until it ends, and if that thread is the main thread, the UI waits.'),
                  ('SAY', 'Click: marking work async enables suspension; it does not by itself move work to another thread. CPU-heavy work must be moved off the main actor deliberately; Unit 01 lesson 1.9 shows how.'),
                  ('CONNECT', 'So what should run where?'))))
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
take(5, 33, 5, connect='Two quick questions on Part 5.')
question(5, 35, 5, 0, 'Next question.', subs=[
    ('<li>awaiting URLSession data in a Task</li><li>a 3-second <code>Thread.sleep</code> in a Button action</li><li>updating a small <code>@State</code> value</li><li>reading a <code>@MainActor</code> ViewModel property</li>',
     '<li>waiting for the balance download</li><li>the Refresh action waiting 3 seconds on the main thread</li><li>changing one small value on screen</li><li>reading the ViewModel&rsquo;s balance</li>'),
    ('<p class="q-why">Thread.sleep blocks the main thread. Awaiting suspends the task, and the other two are cheap main-thread work.</p>',
     '<p class="q-why">Waiting on the main thread blocks it. A download suspends while it waits, and the other two are cheap main-thread work.</p>'),
    ('<span class="notes-label">SAY</span><p>B. Thread.sleep blocks the main thread. Awaiting suspends the task, and the other two are cheap main-thread work.</p>',
     '<span class="notes-label">SAY</span><p>B. Waiting on the main thread blocks it. A download suspends while it waits, and the other two are cheap main-thread work.</p>'),
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
take(6, 5, 6, connect='Where do individual values live?')

# code-free: stack vs heap with an example in words
sh = diagrams(6, 7)[0]
S.append(slide('Part 6 &middot; Stack and heap &middot; conceptual', 'Where do values live?', f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    {card('Example: one transfer', ul('Adding a fee needs three temporary numbers: <b>amount</b>, <b>fee</b>, <b>total</b>', 'They live in the call&rsquo;s frame on the <b>stack</b>', 'Gone as soon as the calculation returns', 'An account object shared by several screens lives on the <b>heap</b>'))}
    <div>
      {sh}
      <i class="step cue"></i><i class="step cue"></i>
      <div class="gap"></div>
      <p class="small">The <b>stack</b> is efficient for call-related storage. The <b>heap</b> is more flexible, but involves allocation and lifetime management.</p>
    </div>
  </div>""", notes(('SAY', 'A calculation that adds a fee to a transfer needs temporary storage for the amount, the fee and the total. Click: the stack, tied to function calls and thread execution, with the call frame, temporary values and return information. Click: the heap, for dynamically allocated storage and objects that outlive one call, such as an account shared by several screens.'),
                  ('SAY', 'The stack is typically efficient for call-related storage; heap allocation is more flexible but needs allocation and lifetime management.'),
                  ('CONNECT', 'A warning before we go further.'))))
take(6, 8, 6)
take(6, 12, 6, connect='Class instances are shared. So how does Swift know when one can be freed?')
take(6, 14, 6, connect='Not every reference keeps an object alive.')
take(6, 17, 6, connect='What happens when two objects keep each other alive?')

# code-free: retain cycle in words, the diagram unchanged
cy = diagrams(6, 19)[0]
S.append(slide('Part 6 &middot; Retain cycle &middot; conceptual', 'Two objects that never let go', f"""  <div class="body cols middle" style="grid-template-columns:1fr 1fr">
    <div>
      {card('Two objects', ul('A <b>person</b> strongly references their apartment', 'The <b>apartment</b> strongly references its tenant', 'Both outside variables are cleared', 'Each still holds the other: <b>neither is freed</b>'))}
      <div class="gap"></div>
      <div class="rule step" data-label="The fix">Make the apartment&rsquo;s reference to its tenant <b>weak</b>. It no longer owns the tenant, so both are freed.</div>
    </div>
    <div>
      {cy}
      <i class="step cue"></i>
    </div>
  </div>""", notes(('SAY', 'A person strongly references their apartment, and the apartment strongly references its tenant. Both are also reachable from outside variables. Click: set the outside variables to nil. The two instances still retain one another, so neither is released: a leak.'),
                  ('SAY', 'Click: make the apartment&rsquo;s reference to its tenant weak. Now nothing keeps the person alive once the outside reference goes, and the cycle no longer prevents deallocation.'),
                  ('CONNECT', 'Cycles between two objects are easy to spot. Cycles through closures are not.'))))
take(6, 24, 6)
take(6, 26, 6)
take(6, 28, 6)
take(6, 30, 6)
take(6, 31, 6, connect='Let&rsquo;s recap Part 6.')
take(6, 35, 6, connect='Two quick questions on Part 6.')
question(6, 37, 6, 0, 'Next question.')
question(6, 39, 6, 1, 'Part 7: the walls iOS builds around NPay.')


# ================================================================== Part 7 · security (0.7)
part(7, 'Security', 'Sandbox, entitlements, signing, Keychain, Secure Enclave',
     'NPay handles money. How does iOS keep it apart from other apps, and keep its secrets safe?',
     ('sandbox', 'keychain', 'kernel', 'hardware'),
     'Memory inside NPay&rsquo;s process.', 'The walls around that process: sandbox, signing, Keychain and the Secure Enclave.',
     'The teal is on the walls: NPay&rsquo;s sandbox, the Keychain, the kernel that enforces the rules, and the hardware with the Secure Enclave.')
for i in (5, 7, 9, 11, 12, 14, 16, 18):
    take(7, i, 7)
take(7, 20, 7, connect='Let&rsquo;s recap Part 7.')
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
take(8, 7, 8)
take(8, 9, 8)
take(8, 10, 8)
take(8, 12, 8)
take(8, 13, 8, connect='Inside the app, who coordinates the request?')

# code-free: ViewModel in the request path, ViewModel duties in words
vp = diagrams(8, 19)[0]
S.append(slide('Part 8 &middot; MVVM &middot; conceptual', 'A ViewModel in the request path', f"""  <div class="body cols middle" style="grid-template-columns:1fr 1.1fr">
    <div>
      {vp}
      <i class="step cue"></i><i class="step cue"></i><i class="step cue"></i><i class="step cue"></i>
      <p class="small muted" style="margin:10px 0 0">The View owns its ViewModel.</p>
    </div>
    {card('DashboardViewModel', ul('Runs on the <b>main actor</b>: its state feeds the UI', 'Asks BalanceService for the balance and <b>waits without blocking</b>', 'Formats paise as <b>&#8377;25,000</b> for display', 'Stores an <b>error message</b> when the request fails'))}
  </div>""", notes(('SAY', 'Click down: the view displays the balance and loading state; the ViewModel coordinates the call and updates observable state; the service talks to the network and decodes the response; the server returns authorized account information.'),
                  ('SAY', 'The ViewModel runs on the main actor, so its state changes happen where the UI reads them. It waits for the service without blocking, formats the minor units as rupees for display, and on failure stores a message the view can show. Formatting is the ViewModel&rsquo;s job, not the view&rsquo;s.'),
                  ('CONNECT', 'And when the response arrives, how does it reach the screen?'))))

# code-free: 0.10's response-to-screen slide, keeping the JSON (data) and dropping the Swift type
s = rekick(get(10, 17), 8)
s = re.sub(r'\s*<div class="gap"></div>\s*<div class="cw"><div class="ch"><span>Balance\.swift.*?</pre></div>', '', s, count=1, flags=re.S)
s = s.replace('through JSONDecoder into a Balance', 'through a decoder into a Balance model')
S.append(set_connect(s, 'Not every request succeeds. What then?') + '\n\n')
take(8, 21, 8)
take(8, 23, 8)
take(8, 24, 8, connect='Let&rsquo;s recap Part 8.')
take(8, 25, 8, connect='Two quick questions on Part 8.')
question(8, 27, 8, 0, 'Next question.')
question(8, 30, 8, 1, 'Part 9: what NPay keeps on the device, and where.',
         subs=[('Spaced review from 0.5. While <code>fetchBalance()</code> awaits the server', 'Spaced review from Part 5. While NPay awaits the balance from the server'),
               ('While fetchBalance() awaits the server', 'While NPay awaits the balance from the server')])


# ================================================================== Part 9 · storage (0.9)
part(9, 'Data storage', 'What survives termination, and where it belongs',
     'Memory is gone when the process ends. What should NPay keep, and where?',
     ('storage', 'keychain'),
     'The network path to the bank&rsquo;s server.', 'Storage on the device: UserDefaults, files, SwiftData and the Keychain.',
     'The teal is on storage and the Keychain, the two places NPay&rsquo;s data can outlive its process.')
take(9, 5, 9)
take(9, 7, 9, connect='Files have their own places inside the sandbox.')

# code-free: sandbox directories, the table and rule without the code column
s = get(9, 13)
tbl = re.search(r'<table class="tbl".*?</table>', s, re.S).group(0)
S.append(slide('Part 9 &middot; Sandbox directories', 'Where an app keeps its files', f"""  <div class="body">
    {tbl}
    <div class="gap"></div>
    <div class="rule step">The system can remove cached and temporary content. Don&rsquo;t treat those directories as <b>permanent</b>.</div>
    <p class="small muted" style="margin:10px 0 0">Files can also be protected so they stay encrypted while the device is locked. Unit 06 &middot; 6.5 covers backups and data protection.</p>
  </div>""", notes(('SAY', 'Apps have directories inside their sandbox. Documents is for documents the user creates; it is backed up and can be shown in the Files app, so it is not the place for app internals. Application Support holds app-managed data, backed up but hidden. Caches holds content that can be downloaded again, and Temporary holds short-lived files; the system can remove both.'),
                  ('SAY', 'NPay can download a statement again at any time, so it goes in Caches, written with file protection so it stays encrypted while the device is locked. App data such as a store goes in Application Support. Unit 06, lesson 6.5, goes deeper.'),
                  ('CONNECT', 'So which storage for which data?'))))
take(9, 15, 9)
take(9, 17, 9)
take(9, 19, 9)
take(9, 21, 9, connect='Let&rsquo;s recap Part 9.')
take(9, 22, 9, connect='Two quick questions on Part 9.')
question(9, 24, 9, 0, 'Next question.')
question(9, 28, 9, 1, 'Part 10: one day with NPay, every layer at once.')


# ================================================================== Part 10 · end to end (0.10)
part(10, 'End to end', 'One day with NPay, every layer at once',
     'Everything from Parts 1 to 9, in one story: the day from this morning&rsquo;s opening slide.',
     (),
     'Nine Parts, one layer at a time.', 'The whole map at once: one day with NPay, from launch to return.',
     'No single teal box this time: every box on the map is involved in one ordinary day with NPay.')
take(10, 6, 10, connect='Follow one Refresh balance request: six protections surround it.')
take(10, 15, 10, connect='The data comes back. What does NPay keep, and where?')
take(10, 19, 10, subs=[('(Lesson 0.7)', '(Part 7)')], connect='Then the user leaves NPay, and later comes back.')
take(10, 25, 10, subs=[('as in Stage one', 'as in Part 2')])
take(10, 27, 10, connect='Let&rsquo;s recap the whole day.')
take(10, 29, 10, connect='Two last questions.')
question(10, 32, 10, 0, 'Next question.')
question(10, 35, 10, 1, 'Let&rsquo;s wrap up.')


# ================================================================== wrap-up
S.append(chapter('Wrap-up', 'Putting it together', 'What comes next, and your checkpoint',
                 'Two last things: where each of today&rsquo;s ideas goes next in the course, and your checkpoint.', 'Where does each of today&rsquo;s ideas go next?').replace('<p class="kicker">Part Wrap-up</p>', '<p class="kicker">Wrap-up</p>'))
take(10, 36, 'Wrap-up', subs=[('<th>Builds on today</th>', '<th>Builds on</th>')],
     connect='Your checkpoint.')
take(10, 37, 'Wrap-up')
take(10, 38, 'Wrap-up')
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
for k, s in enumerate(S):
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
