/*
 * Grundke IT-Service · KI-Arbeitsplatz-Arbeitsbuch · Haken, Fortschritt, Hell/Dunkel (localStorage)
 * Seit 08.11.2026 (Release 2.3.0) eigene Datei statt Inline-Skript (kommende CSP script-src 'self').
 * Bewusst nicht im Pre-Cache von sw.js (Seite ist unverlinkt).
 */
(function(){
  var SP='onb_v1_';
  var kaesten=[].slice.call(document.querySelectorAll('.pkt input[type=checkbox]'));
  var phasen=[].slice.call(document.querySelectorAll('.phase'));
  var nurOffen=false;

  function lade(){
    kaesten.forEach(function(k){
      try{ k.checked = localStorage.getItem(SP+k.id)==='1'; }catch(e){}
    });
  }
  function sichere(k){ try{ localStorage.setItem(SP+k.id, k.checked?'1':'0'); }catch(e){} }

  function zeichne(){
    var g=0, ga=0;
    phasen.forEach(function(ph){
      var ks=[].slice.call(ph.querySelectorAll('input[type=checkbox]'));
      var n=ks.filter(function(k){return k.checked}).length;
      g+=n; ga+=ks.length;
      ph.querySelector('.pzahl').textContent = n+' / '+ks.length;
      ph.classList.toggle('fertig', n===ks.length && ks.length>0);
      ks.forEach(function(k){
        var zeile=k.closest('.pkt');
        zeile.classList.toggle('ab', k.checked);
        zeile.style.display = (nurOffen && k.checked) ? 'none' : '';
      });
      if(nurOffen){ ph.style.display = (n===ks.length) ? 'none' : ''; }
      else { ph.style.display=''; }
    });
    var pct = ga ? Math.round(g/ga*100) : 0;
    document.getElementById('gbalken').style.width = pct+'%';
    document.getElementById('gtext').textContent = g+' von '+ga+' erledigt ('+pct+'%)';
  }

  kaesten.forEach(function(k){
    k.addEventListener('change', function(){ sichere(k); zeichne(); });
  });

  phasen.forEach(function(ph){
    ph.querySelector('.pkopf').addEventListener('click', function(){ ph.classList.toggle('auf'); });
  });

  document.getElementById('btnAlle').addEventListener('click', function(){
    var zu = phasen.some(function(p){ return !p.classList.contains('auf'); });
    phasen.forEach(function(p){ p.classList.toggle('auf', zu); });
    this.textContent = zu ? 'Alle zuklappen' : 'Alle aufklappen';
  });

  document.getElementById('btnOffen').addEventListener('click', function(){
    nurOffen=!nurOffen;
    this.textContent = nurOffen ? 'Alle zeigen' : 'Nur offene';
    if(nurOffen) phasen.forEach(function(p){ p.classList.add('auf'); });
    zeichne();
  });

  document.getElementById('btnReset').addEventListener('click', function(){
    if(!confirm('Alle Haken zurücksetzen?')) return;
    kaesten.forEach(function(k){ k.checked=false; sichere(k); });
    zeichne();
  });

  var tb=document.getElementById('btnTheme');
  function thema(t){
    document.documentElement.setAttribute('data-theme',t);
    tb.textContent = (t==='dark') ? 'Hell' : 'Dunkel';
    try{ localStorage.setItem(SP+'theme',t); }catch(e){}
  }
  tb.addEventListener('click', function(){
    thema(document.documentElement.getAttribute('data-theme')==='dark'?'light':'dark');
  });
  var gespeichert='light';
  try{ gespeichert = localStorage.getItem(SP+'theme') || 'light'; }catch(e){}
  thema(gespeichert);

  lade();
  phasen[0].classList.add('auf');
  zeichne();
})();
