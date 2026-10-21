# Validates deck HTML structure: balanced tags per <section>, notes inside slides, all sections inside .deck
import sys
from html.parser import HTMLParser
VOID={'meta','link','br','img','input','hr','use','path','rect','circle','ellipse','line','polyline','polygon','stop'}
class P(HTMLParser):
    def __init__(s): super().__init__(); s.stack=[]; s.err=[]; s.sec=0
    def handle_starttag(s,t,a):
        if t in VOID: return
        if t=='section':
            s.sec+=1
            if [x for x,_ in s.stack if x=='div' ][:1]==[] : s.err.append(f'section {s.sec} not inside .deck')
        if t=='aside' and 'section' not in [x for x,_ in s.stack]: s.err.append(f'aside outside a section near line {s.getpos()[0]}')
        s.stack.append((t,s.getpos()[0]))
    def handle_startendtag(s,t,a): pass
    def handle_endtag(s,t):
        if t in VOID: return
        if not s.stack or s.stack[-1][0]!=t:
            s.err.append(f'mismatched </{t}> at line {s.getpos()[0]} (open: {s.stack[-1] if s.stack else None})'); 
            # recover
            for i in range(len(s.stack)-1,-1,-1):
                if s.stack[i][0]==t: del s.stack[i:]; break
            return
        s.stack.pop()
for f in sys.argv[1:]:
    p=P(); p.feed(open(f).read())
    print(f, 'sections',p.sec, 'OK' if not p.err else '\n  '+'\n  '.join(p.err[:10]))
