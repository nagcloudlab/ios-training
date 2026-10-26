"""Shared helpers for Unit 01+ generators. Exec'd after gen02's helpers, with S defined.
A generator for another unit sets UNIT_NO, UNIT_TITLE and UNIT_LESSONS before exec'ing this file:
    exec(open(os.path.join(HERE, 'unit1.py')).read())"""


def divider(n, title, lead, say, con):
    S.append(f"""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Part {n}</p>
    <h2>{title}</h2>
    <p class="lead">{lead}</p>
  </div>
{notes(('SAY', say), ('CONNECT', con))}</section>

""")


# Section 9's stack: where the Swift language sits in an iOS app. Reused as this unit's "where we are" picture.
STACK = [('lang', 'code', 'Swift language', 'types, functions, structs, classes, protocols'),
         ('ui', 'phone', 'SwiftUI / UIKit', 'application interfaces and interaction'),
         ('found', 'frameworks', 'Foundation and system APIs', 'networking, data, files and other capabilities'),
         ('rt', 'gear', 'Swift compiler and runtime', 'native code, runtime support and ARC'),
         ('os', 'kernel', 'iOS operating system', 'process execution, scheduling, memory and security'),
         ('hw', 'chip', 'Apple hardware', 'processor, memory, GPU and device capabilities')]


def stack(focus=(), lits=None, tid='stack', style='max-height:420px', h=56, gap=12):
    lits = lits or {}
    P = []
    for i, (k, icon, t, sub) in enumerate(STACK):
        y = i * (h + gap)
        cls = 'solid' if k == 'hw' else ''
        cls = (cls + ' lit').strip() if k in focus else cls
        P.append(row(0, y, 1136, h, icon, t, sub, lits.get(k), cls))
    return svg(f'0 0 1136 {len(STACK) * (h + gap) - gap}', 'Swift language, SwiftUI and UIKit, Foundation, the Swift compiler and runtime, iOS, Apple hardware', tid, P, style)


def review(QA):
    """Check-your-understanding slides. QA rows: (icon, label, data-title, question html, verdict, why, trap, expect, extra notes)."""
    N = len(QA)
    for i, (ic, label, title, q, v, why, trap, exp, extra) in enumerate(QA):
        dots = ''.join('<i class="done"></i>' if k < i else '<i class="now"></i>' if k == i else '<i></i>' for k in range(N))
        S.append(f"""<section class="slide question" data-title="{E(title, quote=True)}">
  <div class="q-top">
    <p class="kicker">Check your understanding &middot; {i + 1} of {N}</p>
    <div class="q-dots" aria-hidden="true">{dots}</div>
  </div>
  <div class="body">
    <div class="q-row">
      <div class="q-card">
        <div class="q-icon"><svg viewBox="0 0 24 24"><use href="#i-{ic}"/></svg></div>
        <span class="label">{label}</span>
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
""" + notes(*([('SAY', extra)] if extra else []), ('ASK', 'Give everyone a few seconds, then take a quick vote.'), ('EXPECT', exp), ('SAY', f'{v}. {why}'),
                    ('CONNECT', 'Next question.' if i < N - 1 else 'Where this goes next.')) + "</section>\n\n")


cues = lambda n: '<i class="step cue"></i>' * n
box = lambda x, y, w, h, t, sub='', l=None, cls='', icon='': row(x, y, w, h, icon, t, sub, l, cls)
ul = lambda *items: '<ul style="margin:6px 0 0">' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>'
card = lambda label, body, cls='': f'<div class="card accent{(" " + cls) if cls else ""}"><span class="label">{label}</span>{body}</div>'
out = lambda txt, cls='step': f'<p class="{cls}" style="margin:10px 0 0;font-size:19px">{txt}</p>'
err = lambda msg: f'<span style="font-size:19px;line-height:1.4"><b class="mono" style="font-size:15px;letter-spacing:.06em">ERROR</b>&ensp;{msg}</span>'
TWO = 'grid-template-columns:minmax(0,1fr) minmax(0,1fr)'   # equal columns, so side-by-side pictures line up


def title_slide(lesson, h1, lead, say):
    S.append(f"""<section class="slide title" style="background:linear-gradient(135deg,#0f172a 0%,#1e3a5f 40%,#134e4a 100%)">
  <div class="body" style="z-index:1;position:relative">
    <p class="kicker" style="letter-spacing:.2em">Unit {UNIT_NO} &middot; Lesson {lesson}</p>
    <h1 style="font-size:54px;line-height:1.05">{h1}</h1>
    <p class="lead" style="max-width:760px">{lead}</p>
  </div>
  <svg style="position:absolute;right:-30px;top:-30px;width:460px;opacity:.06;pointer-events:none" viewBox="0 0 460 460"><circle cx="230" cy="230" r="200" stroke="#5eead4" stroke-width="1" fill="none"/><circle cx="230" cy="230" r="140" stroke="#5eead4" stroke-width=".5" fill="none"/><circle cx="230" cy="230" r="80" stroke="#5eead4" stroke-width=".5" fill="none"/></svg>
""" + notes(('SAY', say), ('CONNECT', "Here's what you'll be able to explain by the end.")) + "</section>\n\n")


def outcomes_slide(lesson, outs):
    cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p>{t}</p></div>' for i, t in outs)
    S.append(slide(f"Lesson {lesson} &middot; Outcomes", "By the end, you will be able to explain", f"""  <div class="body">
    <div class="cols c3 stagger step">
{cells}
    </div>
  </div>""", notes(('SAY', f'{len(outs)} things you should be able to explain by the end of this lesson.'), ('CONNECT', 'First, where we are.'))))


# Unit 01 lessons (curriculum plan), for the progress strip on each lesson's "Where we are" slide.
UNIT1 = [('1.1', 'Swift &amp;', 'compiler'), ('1.2', 'Variables', '&amp; types'), ('1.3', 'Optionals', ''), ('1.4', 'Functions', '&amp; closures'),
         ('1.5', 'Structs', '&amp; classes'), ('1.6', 'Protocols', ''), ('1.7', 'Generics', '&amp; errors'), ('1.8', 'ARC &amp;', 'ownership'),
         ('1.9', 'Concurrency', ''), ('1.10', 'NPay', 'model')]
UNIT_NO = globals().get('UNIT_NO', '01')
UNIT_TITLE = globals().get('UNIT_TITLE', 'Swift Language Mastery')
UNIT_LESSONS = globals().get('UNIT_LESSONS', UNIT1)


def progress(lesson, tid='prog'):
    """Unit progress strip: earlier lessons done, this one teal, later ones ahead (dashed)."""
    n = [k for k, *_ in UNIT_LESSONS].index(lesson)
    count = len(UNIT_LESSONS)
    w = 104 if count <= 10 else (1136 - (count - 1) * 8) // count   # boxes shrink to fit more than ten lessons
    g = (1136 - count * w) / (count - 1)
    P = []
    for i, (k, t1, t2) in enumerate(UNIT_LESSONS):
        x = i * (w + g)
        cls = 'nd lit' if i == n else 'nd ghost' if i > n else 'nd'
        fs = 14 if w >= 100 or max(len(html.unescape(t1)), len(html.unescape(t2))) <= 9 else 12   # long labels in narrow boxes
        P.append(f'<g class="{cls}"><rect class="sh" x="{x:g}" y="0" width="{w}" height="84" rx="12"/>'
                 f'<text class="sm" x="{x + 12:g}" y="24">{k}</text><text x="{x + 12:g}" y="50" style="font-size:{fs}px">{t1}</text>'
                 f'<text x="{x + 12:g}" y="68" style="font-size:{fs}px">{t2}</text></g>')
    return svg('0 0 1136 84', f'Unit {UNIT_NO} progress: lesson {lesson} of {count}', tid, P, 'max-height:96px')


def where_slide(lesson, h2, focus, last, today, say, con):
    """Opening bridge: where this lesson sits in its unit, and what came last time. (`focus` kept for call compatibility.)"""
    S.append(slide(f"Lesson {lesson} &middot; Where we are", h2, f"""  <div class="body">
    <p class="kicker" style="margin:0 0 10px;color:var(--muted)">Unit {UNIT_NO} &middot; {UNIT_TITLE}</p>
    {progress(lesson)}
    <div class="gap-lg"></div>
    <div class="bridge lg" style="margin-top:0"><span><b>Last time</b>{last}</span><span><b>Today</b>{today}</span></div>
  </div>""", notes(('SAY', say), ('CONNECT', con))))


def recap_u1(lesson, focus, items, say):
    """Closing recap: three takeaways as cards. (`focus` kept for call compatibility.)"""
    cells = "\n".join(f'      <div class="card accent outcome"><span class="icon-badge"><svg viewBox="0 0 24 24"><use href="#i-{i}"/></svg></span><p style="font-size:23px"><b>{t}</b><br><span class="muted" style="font-size:19px">{d}</span></p></div>' for i, t, d in items)
    S.append(slide(f"Lesson {lesson} &middot; Recap", "What to remember", f"""  <div class="body">
    <div class="cols c3" style="gap:20px;align-items:stretch">
{cells}
    </div>
  </div>""", notes(('SAY', say), ('CONNECT', 'Now check your understanding.'))))


def review_divider(n):
    S.append("""<section class="slide chapter">
  <div class="body">
    <p class="kicker">Review</p>
    <h2>Check your understanding</h2>
  </div>
""" + notes(('SAY', f'{n} questions, in different formats. Everyone commits to an answer before it is revealed.')) + "</section>\n\n")


def end_slide(lesson, h2, nxt, say1, say2):
    S.append(f"""<section class="slide end">
  <div class="body">
    <p class="kicker">Lesson {lesson} complete</p>
    <h2>{h2}</h2>
    <p class="lead" style="max-width:820px;margin:0 auto">Next: {nxt}</p>
  </div>
""" + notes(('SAY', say1), ('SAY', say2)) + "</section>\n\n")


def write_deck(out_path, lesson, title, deck_name):
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lesson {lesson} — {title}</title>
<link rel="stylesheet" href="../../../shared/deck.css">
</head>
<body data-deck="Unit {UNIT_NO} · Lesson {lesson} — {deck_name}">
<div class="deck">

{''.join(S)}</div>
<script src="../../../shared/art.js"></script>
<script src="../../../shared/deck.js"></script>
</body>
</html>
"""
    open(out_path, 'w').write(doc)
    print(len(S), 'slides')
