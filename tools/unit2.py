"""Unit 02 settings, exec'd by each Unit 02 generator after gen02's helpers (S defined):
    exec(open(os.path.join(HERE, 'unit2.py')).read())
Unit 02 restarted from zero; lessons are named as their texts arrive (the restart runs past ten lessons; the progress strip sizes itself)."""
UNIT_NO, UNIT_TITLE = '02', 'SwiftUI Fundamentals'
UNIT_LESSONS = [('2.1', 'Text', ''), ('2.2', 'Image &amp;', 'SF Symbols'), ('2.3', 'VStack &amp;', '@ViewBuilder'),
                ('2.4', 'HStack &amp;', 'layout'), ('2.5', 'ZStack &amp;', 'layers'),
                ('2.6', 'View', 'modifiers'), ('2.7', 'Button &amp;', 'events'),
                ('2.8', '@State', ''), ('2.9', '@Binding', ''), ('2.10', 'ForEach', '&amp; List'), ('2.11', 'TextField', '&amp; focus'), ('2.12', 'Payment', 'flow')]
exec(open(os.path.join(HERE, 'unit1.py')).read())   # shared helpers (unit-aware)

# Unit 02 evidence helpers: console cards and simulator screenshots (tools/sim2_N/run.sh makes the images)
mono = lambda txt, size=15: f'<p style="font-family:var(--code-font);margin:4px 0 0;font-size:{size}px;line-height:1.55">{txt}</p>'
tbl = lambda head_, rows, cls='tbl compact': f'<table class="{cls}"><thead><tr>' + ''.join(f'<th>{h}</th>' for h in head_) + '</tr></thead><tbody>' + ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows) + '</tbody></table>'
console = lambda label, lines, size=14: card(label, mono('<br>'.join(lines), size))
shot = lambda src_, cap, w, h=None: f'<div style="width:{w}px;max-width:100%;margin:0 auto"><div class="shot"{f" style=\"height:{h}px\"" if h else ""}><img src="{src_}" alt="{cap}"></div><p class="shot-cap">{cap}</p></div>'
PHONE = lambda src_, cap, w=160: shot(src_, cap, w, round(w * 2622 / 1206))   # whole screen, 1206 x 2622
crop = lambda src_, cap, w, _=None: shot(src_, cap, w)   # cropped to content by crop.swift; natural height
SIM = 'iPhone 17 simulator, iOS 26.5'
