import sys
src, D = sys.argv[1], sys.argv[2]
s=open(src).read()
err='<script>window.__e=[];addEventListener("error",function(e){__e.push(e.message)});</script>'
audit=r'''<script>document.fonts.ready.then(function(){setTimeout(function(){
var out=[], slides=[].slice.call(document.querySelectorAll('.slide')), tot=0;
document.querySelectorAll('aside.notes-src').forEach(function(a,i){if(!a.closest('.slide'))out.push('notes '+i+' outside slide');});
slides.forEach(function(sl,i){ if(!sl.closest('.deck'))out.push('slide '+(i+1)+' outside deck');
  var steps=sl.querySelectorAll('.step').length, prev=null; tot+=steps+1;
  var lits=[].slice.call(sl.querySelectorAll('[data-lit]')), ever=lits.map(function(){return false});
  for(var n=0;n<=steps;n++){
    Deck.go(i); for(var k=0;k<n;k++) Deck.next();
    var r=sl.getBoundingClientRect(), lim=r.top+(720-46)*r.height/720, rl=r.right-60*r.width/1280;
    sl.querySelectorAll('.body *').forEach(function(e){var b=e.getBoundingClientRect(); if(!b.height||getComputedStyle(e).display==='none')return;
      if(b.bottom>lim+1) out.push((i+1)+'@'+n+' overflow-bottom '+e.tagName+'.'+(e.className.baseVal!==undefined?e.className.baseVal:e.className));
      if(b.right>r.right-2) out.push((i+1)+'@'+n+' overflow-right '+e.tagName);});
    var lv=lits.map(function(e,j){var l=e.classList.contains('lit'); if(l)ever[j]=true; return l});
    var teal=sl.querySelectorAll('.nd.lit:not(.pass)').length; if(teal>5) out.push((i+1)+'@'+n+' teal '+teal);
    var sig=JSON.stringify([lv,sl.querySelectorAll('.step.shown:not(.cue)').length]);
    if(prev!==null&&sig===prev) out.push((i+1)+'@'+n+' click changes nothing'); prev=sig;
  }
  lits.forEach(function(e,j){if(!ever[j])out.push((i+1)+' data-lit="'+e.dataset.lit+'" never fires');});
});
out=out.filter(function(v,k,a){return a.indexOf(v)===k});
document.body.setAttribute('data-audit',(out.join(' ;; ')||'clean')+' | errors='+(__e.join('|')||'none')+' | slides='+slides.length+' states='+tot);},400)});</script></body>'''
open(D+'/audit.html','w').write(s.replace('<div class="deck">',err+'<div class="deck">',1).replace('</body>',audit))
open(D+'/all.html','w').write(s.replace('</body>','<script>Deck.go((parseInt(location.hash.slice(1))||1)-1,true);</script></body>'))
open(D+'/index.html','w').write(s.replace('</body>','<script>var n=+(new URLSearchParams(location.search).get("n")||0);for(var i=0;i<n;i++)Deck.next();</script></body>'))
