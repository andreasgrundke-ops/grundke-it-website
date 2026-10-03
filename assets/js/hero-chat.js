/**
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · hero-chat.js
 * Version: 1.4.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-10-03
 * Beschreibung: Hero „Der Chat" auf der Startseite. Im gezeichneten Handy
 *   laeuft ein Beispiel-Einsatz als Chat ab: Kundennachricht, Andreas tippt,
 *   Fernwartung, Ergebnis, Dank. Statusleiste und Zeitstempel tragen die echte
 *   Uhrzeit des Besuchers; abends, am Wochenende und nachts steht darueber die
 *   grosse Uhrzeit mit einem Satz.
 * Ablauf:
 *   1. Elemente suchen, ohne Hero sofort Abbruch.
 *   2. Tageszeit bestimmen (tag / abend / nacht), Statusleiste und Uhrzeit-Zeile
 *      setzen und jede halbe Minute nachziehen.
 *   3. Bei prefers-reduced-motion: ersten Fall fertig hinstellen, nichts bewegt sich.
 *   4. Sonst: jeden Fall EINMAL abspielen (Schrittliste mit Zeitpunkten in ms),
 *      nach dem letzten Fall stehen bleiben - der Knopf wird zu „Nochmal".
 *   5. Anhalten: per Knopf (WCAG 2.2.2) und automatisch, wenn der Hero aus dem
 *      Bild gescrollt oder der Tab im Hintergrund ist.
 * Aenderungshistorie:
 *   1.0.0 (2026-10-02) Erste Fassung, ersetzt den Foto-Slider aus main.js.
 *   1.1.0 (2026-10-02) Nach Finish-Review und Code-Review: einmal durchspielen
 *                      statt Endlosschleife; Statusleiste mit Uhrzeit in allen
 *                      Modi; Antwortabstaende je Fall verschieden (keine
 *                      scheinbare Reaktionszeit); Pause waehrend des Ueberblendens
 *                      laesst das Handy nicht mehr leer; ein Zeitpunkt je Fall;
 *                      Knopf ohne aria-pressed (Beschriftung nennt die Aktion).
 *   1.2.0 (2026-10-02) Neue Faelle nach Andreas: Kasse, E-Mail beim Anbieter,
 *                      Buchungsseite, langsamer PC durch defekten Netzwerkspeicher;
 *                      Uhrzeit nur noch in der Statusleiste (keine Doppelung);
 *                      Druckerfall raus, geloester Fall (Buchungsseite) bleibt am Ende stehen.
 *   1.3.0 (2026-10-02) Kundensicht nach Andreas: Handy gehoert dem Kunden (Kontakt
 *                      „Andreas IT"), Messenger-Optik, Tastatur faehrt beim Tippen
 *                      des Kunden ein, gedrueckte Tasten leuchten auf; Kopfzeile
 *                      zeigt „schreibt …", waehrend Andreas antwortet. Tipptempo
 *                      menschlich (ca. 115 ms je Taste, Pausen nach Wort und Satzzeichen).
 *   1.4.0 (2026-10-03) Handy-Ansicht repariert: unter 768 px sind Eingabezeile und
 *                      Tastatur ausgeblendet, das Tippen lief trotzdem unsichtbar
 *                      mit (bis zu 8 s leerer Chat, dann alles auf einmal). Dort
 *                      erscheint die Kundennachricht jetzt nach kurzer Pause.
 *                      Ausserdem holt der Takt nach gedrosselten Timern (Scrollen
 *                      am Handy, Energiesparen) nicht mehr mehrere Schritte auf einmal nach.
 * ═══════════════════════════════════════════════════════════
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-hero-chat]');
  if (!root) return;
  var thread = root.querySelector('[data-hc-thread]');
  var clockEl = root.querySelector('[data-hc-clock]');
  var statusEl = root.querySelector('[data-hc-status]');
  var knopf = root.querySelector('[data-hc-pause]');
  if (!thread) return;

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Beispielfaelle aus den „Acht Situationen" der Startseite.
     antwort/loesung = Minuten bis zur Antwort bzw. bis zum Ergebnis (bewusst verschieden).
     nacht:false = Fall passt nicht zu einer Nachricht mitten in der Nacht. */
  var CASES = [
    { me: 'Unsere Kasse geht nicht, die Gäste wollen zahlen.',
      ag: 'Ich prüfe Kassennetz, Internet und Kassenserver.',
      run: 'Prüfe Kassennetz, Server, EC-Terminal …', done: 'Netz und EC-Terminal ok, Kassenserver hing',
      fix: 'Kassenserver neu gestartet. Ihr könnt wieder kassieren.',
      thanks: 'Danke, läuft wieder!', antwort: 2, loesung: 6, nacht: false },
    { me: 'Seit heute früh kommen bei uns keine Mails an.',
      ag: 'Ich schau, ob es am Anbieter liegt oder bei euch.',
      run: 'Prüfe Postfach, DNS und Anbieter-Status …', done: 'Störung beim Anbieter, bei euch alles in Ordnung',
      fix: 'Liegt beim Anbieter. Ist gemeldet, ich behalte es im Blick.',
      thanks: 'Gut zu wissen, danke.', antwort: 4, loesung: 10, nacht: true },
    { me: 'Unser Kollege, der die IT nebenbei gemacht hat, hört Ende des Monats auf.',
      ag: 'Dann setzen wir uns nächste Woche zusammen. Ich nehme alles auf und übernehme.',
      run: 'IT-Schnellcheck wird geplant …', done: 'IT-Schnellcheck am Dienstag, 9 Uhr',
      fix: 'Danach weißt du genau, was läuft und was nicht.',
      thanks: 'Klingt gut, bis Dienstag.', antwort: 4, loesung: 11, nacht: true },
    { me: 'Mein PC ist heute extrem langsam, Ordner hängen ständig.',
      ag: 'Ich schau mir das aus der Ferne an.',
      run: 'Analysiere PC, Netzwerk, Netzwerkspeicher …', done: 'PC in Ordnung, Netzwerkspeicher meldet Plattenfehler',
      fix: 'Der Netzwerkspeicher ist defekt. Ersatz ist bestellt, eure Daten stelle ich noch heute wieder her.',
      thanks: 'Gut, dass du das gleich gesehen hast.', antwort: 3, loesung: 12, nacht: true },
    { me: 'Unsere Buchungsseite lädt nicht, Gäste rufen schon an.',
      ag: 'Ich prüfe, ob es an der Seite oder an eurem Netz liegt.',
      run: 'Prüfe Website, DNS und Internetzugang …', done: 'Netz in Ordnung, Zertifikat der Seite abgelaufen',
      fix: 'Das Zertifikat war abgelaufen. Ist erneuert, die Seite läuft.',
      thanks: 'Super, danke dir!', antwort: 3, loesung: 7, nacht: true }
  ];
  var NIGHT_REPLY = 'Guten Morgen, hab\'s gesehen. Ich kümmere mich.';

  /* ── Zeit ── */
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function hhmm(d) { return pad(d.getHours()) + ':' + pad(d.getMinutes()); }
  function plus(d, min) { return new Date(d.getTime() + min * 60000); }
  function morningOf(d) { var m = new Date(d.getTime()); m.setHours(7, 12, 0, 0); return m; }
  /* Werktags 7–18 Uhr = tag, abends und am Wochenende = abend, 0–7 Uhr = nacht */
  function dayMode(d) {
    var h = d.getHours(), wd = d.getDay();
    if (h < 7) return 'night';
    if (wd === 0 || wd === 6 || h >= 18) return 'evening';
    return 'day';
  }

  /* Zeitstempel eines Falls: die letzte Nachricht traegt die aktuelle Uhrzeit,
     die frueheren liegen je nach Fall unterschiedlich weit davor.
     Nachts antwortet Andreas um 07:12. */
  function timesFor(c, now) {
    if (dayMode(now) === 'night') {
      var m = morningOf(now);
      return { me: now, ag: m, fix: plus(m, c.loesung), thanks: plus(m, c.loesung + 1), night: true };
    }
    var fix = plus(now, -1), ag = plus(fix, -c.loesung);
    return { me: plus(ag, -c.antwort), ag: ag, fix: fix, thanks: now, night: false };
  }

  function updateClock() {
    var now = new Date(), mode = dayMode(now);
    if (statusEl) statusEl.textContent = hhmm(now);
    if (!clockEl) return;
    clockEl.textContent = '';
    clockEl.classList.toggle('is-empty', mode === 'day');
    if (mode === 'day') return;
    clockEl.appendChild(document.createTextNode(mode === 'night'
      ? 'Schreib einfach, ich melde mich, sobald ich wach bin.'
      : 'Bei mir gibt\'s keine Öffnungszeiten.'));
  }

  /* ── Bausteine (nur textContent, kein innerHTML) ── */
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }
  function msg(who, text, time) {
    var li = el('li', 'hc-msg ' + (who === 'me' ? 'is-me' : 'is-ag'));
    li.appendChild(document.createTextNode(text));
    li.appendChild(el('time', '', hhmm(time)));
    return li;
  }
  function typing() {
    var li = el('li', 'hc-msg is-ag hc-typing');
    for (var i = 0; i < 3; i++) li.appendChild(el('i'));
    return li;
  }
  function sys(text) {
    var li = el('li', 'hc-sys');
    li.appendChild(el('span', 'hc-sys-t', text));
    var bar = el('span', 'hc-bar');
    bar.appendChild(el('i'));
    li.appendChild(bar);
    return li;
  }
  function add(node) {
    node.classList.add('hc-in');
    thread.appendChild(node);
    return node;
  }
  function weg(node) {
    if (node && node.parentNode) node.parentNode.removeChild(node);
  }

  /* ── Eingabezeile und Tastatur (Kundensicht: der Kunde tippt) ── */
  var screen = root.querySelector('.hc-screen');
  var field = root.querySelector('[data-hc-field]');
  var sendBtn = root.querySelector('[data-hc-send]');
  var sub = root.querySelector('[data-hc-sub]');
  var kbIn = root.querySelector('[data-hc-kb] .hc-kb-in');
  var SUB_TEXT = sub ? sub.textContent : '';
  var KEYS = {};
  var KB_ROWS = [
    'q w e r t z u i o p ü',
    'a s d f g h j k l ö ä',
    '⇧ y x c v b n m ⌫'
  ];

  function buildKeyboard() {
    if (!kbIn) return;
    var rows = el('div', 'hc-kb-rows');
    KB_ROWS.forEach(function (r) {
      var row = el('div', 'hc-kb-row');
      r.split(' ').forEach(function (k) {
        var fn = k === '⇧' || k === '⌫';
        var key = row.appendChild(el('span', 'hc-key' + (fn ? ' is-fn' : ''), k));
        KEYS[fn ? (k === '⇧' ? 'shift' : 'back') : k] = key;
      });
      rows.appendChild(row);
    });
    var last = el('div', 'hc-kb-row');
    KEYS.num = last.appendChild(el('span', 'hc-key is-fn', '123'));
    KEYS[','] = last.appendChild(el('span', 'hc-key', ','));
    KEYS[' '] = last.appendChild(el('span', 'hc-key is-space', 'Leerzeichen'));
    KEYS['.'] = last.appendChild(el('span', 'hc-key', '.'));
    KEYS.ret = last.appendChild(el('span', 'hc-key is-ret', 'Senden'));
    rows.appendChild(last);
    kbIn.appendChild(rows);
  }

  /* Die gedrueckte Taste leuchtet kurz auf; Grossbuchstaben druecken Umschalt mit,
     Satzzeichen ohne eigene Taste die 123-Taste */
  function hit(ch) {
    var low = ch.toLowerCase(), keys = [];
    if (KEYS[low]) keys.push(KEYS[low]); else keys.push(KEYS.num);
    if (ch !== low) keys.push(KEYS.shift);
    keys.forEach(function (k) {
      if (!k) return;
      k.classList.add('is-hit');
      setTimeout(function () { k.classList.remove('is-hit'); }, 130);
    });
  }
  function setField(text) {
    if (!field) return;
    field.textContent = '';
    if (text) field.appendChild(document.createTextNode(text));
    else field.appendChild(el('span', 'hc-ph', 'Nachricht'));
    field.classList.toggle('is-typing', !!text);
    if (sendBtn) sendBtn.classList.toggle('has-text', !!text);
  }
  function tastatur(auf) { if (screen) screen.classList.toggle('is-kb', auf); }
  function schreibt(an) {
    if (!sub) return;
    sub.textContent = an ? 'schreibt …' : SUB_TEXT;
    sub.classList.toggle('is-typing', an);
  }

  /* ── Statisch (reduced-motion): erster Fall, fertig ── */
  function renderStatic() {
    var jetzt = new Date(), nachts = dayMode(jetzt) === 'night';
    var c = CASES.filter(function (k) { return !nachts || k.nacht; })[0], t = timesFor(c, jetzt);
    thread.textContent = '';
    thread.appendChild(el('li', 'hc-day', 'Heute'));
    thread.appendChild(msg('me', c.me, t.me));
    thread.appendChild(msg('ag', t.night ? NIGHT_REPLY : c.ag, t.ag));
    var s = sys(c.done);
    s.classList.add('is-done');
    thread.appendChild(s);
    thread.appendChild(msg('ag', c.fix, t.fix));
    thread.appendChild(msg('me', c.thanks, t.thanks));
  }

  buildKeyboard();
  updateClock();
  setInterval(updateClock, 30000);

  if (reduceMotion) { renderStatic(); return; }

  /* ── Abspielen ── */
  var steps = [], stepIdx = 0, elapsed = 0, lastTs = 0, timer = 0;
  var caseIdx = 0, pool = [];
  var zustand = 'laeuft';   // laeuft | pause | fertig
  var offscreen = false;

  /* Tipptempo wie ein Mensch am Handy: ruhig genug zum Mitlesen, nach Wortende
     und Satzzeichen eine kleine Denkpause, dazu leichte Unregelmaessigkeit */
  var TIPP_MS = 115;
  var kompakt = window.matchMedia('(max-width: 767px)');
  function tippPause(ch, n) {
    var p = TIPP_MS + (n * 37 % 5) * 14;
    if (ch === ' ') p += 90;
    if (',.!?'.indexOf(ch) >= 0) p += 260;
    return p;
  }

  /* Kunde tippt: Tastatur auf, Buchstabe fuer Buchstabe ins Feld, Senden, Tastatur zu.
     Haengt die Schritte an s an und gibt den Zeitpunkt nach dem Senden zurueck. */
  function tippen(s, at, text, time) {
    // Schmale Ansicht: Eingabezeile und Tastatur sind per CSS weg, ein unsichtbares
    // Tippen waere nur leere Wartezeit - die Nachricht kommt nach einer Lesepause
    if (kompakt.matches) {
      s.push({ at: at + 1400, run: function () { add(msg('me', text, time)); } });
      return at + 1400;
    }
    s.push({ at: at, run: function () { tastatur(true); } });
    var zeit = at + 450;
    for (var i = 0; i < text.length; i++) {
      (function (n) {
        s.push({ at: zeit, run: function () { hit(text.charAt(n)); setField(text.slice(0, n + 1)); } });
      })(i);
      zeit += tippPause(text.charAt(i), i);
    }
    var ende = zeit + 500;
    s.push({ at: ende, run: function () {
      if (KEYS.ret) { KEYS.ret.classList.add('is-hit'); setTimeout(function () { KEYS.ret.classList.remove('is-hit'); }, 130); }
      setField('');
      add(msg('me', text, time));
    } });
    s.push({ at: ende + 350, run: function () { tastatur(false); } });
    return ende + 350;
  }

  function stepsFor(c, now, letzter) {
    var t = timesFor(c, now), typingNode, sysNode;
    var s = [
      { at: 0, run: function () {
        thread.textContent = '';
        thread.classList.remove('is-out');
        setField('');
        schreibt(false);
        add(el('li', 'hc-day', 'Heute'));
      } }
    ];
    var a = tippen(s, 300, c.me, t.me) + 700;
    s.push({ at: a, run: function () { typingNode = add(typing()); schreibt(true); } });
    s.push({ at: a + 1500, run: function () {
      weg(typingNode);
      schreibt(false);
      add(msg('ag', t.night ? NIGHT_REPLY : c.ag, t.ag));
    } });
    s.push({ at: a + 2700, run: function () { sysNode = add(sys(c.run)); sysNode.classList.add('is-run'); } });
    s.push({ at: a + 4800, run: function () {
      sysNode.classList.remove('is-run');
      sysNode.classList.add('is-done');
      sysNode.firstChild.textContent = c.done;
    } });
    s.push({ at: a + 5600, run: function () { typingNode = add(typing()); schreibt(true); } });
    s.push({ at: a + 7000, run: function () {
      weg(typingNode);
      schreibt(false);
      add(msg('ag', c.fix, t.fix));
    } });
    var b = tippen(s, a + 7700, c.thanks, t.thanks);
    if (letzter) {
      s.push({ at: b + 400, run: fertig });
    } else {
      s.push({ at: b + 2600, run: function () { thread.classList.add('is-out'); } });
      s.push({ at: b + 3300, run: nextCase });
    }
    s.sort(function (x, y) { return x.at - y.at; });
    return s;
  }

  function nextCase() {
    var c = pool[caseIdx];
    caseIdx++;
    steps = stepsFor(c, new Date(), caseIdx >= pool.length);
    stepIdx = 0;
    elapsed = 0;
  }

  function start() {
    var night = dayMode(new Date()) === 'night';
    pool = CASES.filter(function (c) { return !night || c.nacht; });
    caseIdx = 0;
    zustand = 'laeuft';
    nextCase();
    setKnopf();
    setRunning();
  }

  function fertig() {
    zustand = 'fertig';
    setKnopf();
    setRunning();
  }

  /* Gedrosselte Timer (Handy beim Scrollen, Energiesparen) duerfen nicht
     mehrere Schritte auf einmal nachholen: hoechstens TICK_MAX je Takt zaehlen */
  var TICK_MAX = 250;
  function tick() {
    var ts = performance.now();
    elapsed += Math.min(ts - lastTs, TICK_MAX);
    lastTs = ts;
    while (zustand === 'laeuft' && stepIdx < steps.length && elapsed >= steps[stepIdx].at) {
      steps[stepIdx++].run();
    }
  }

  function setRunning() {
    var run = zustand === 'laeuft' && !offscreen && !document.hidden;
    root.classList.toggle('is-paused', !run);
    if (run && !timer) {
      // War beim Anhalten die Ueberblendung schon dran, sie wieder ansetzen
      if (stepIdx > 0 && stepIdx === steps.length - 1 && steps[stepIdx].run === nextCase) thread.classList.add('is-out');
      lastTs = performance.now();
      timer = setInterval(tick, 100);
    } else if (!run && timer) {
      clearInterval(timer);
      timer = 0;
      // Opacity-Uebergaenge halten bei animation-play-state nicht an: nie leer stehen lassen
      thread.classList.remove('is-out');
    }
  }

  var BESCHRIFTUNG = { laeuft: 'Beispiel-Chat anhalten', pause: 'Beispiel-Chat fortsetzen', fertig: 'Beispiel-Chat noch einmal abspielen' };
  function setKnopf() {
    if (!knopf) return;
    knopf.setAttribute('data-zustand', zustand);
    knopf.setAttribute('aria-label', BESCHRIFTUNG[zustand]);
  }

  if (knopf) {
    knopf.hidden = false;
    knopf.addEventListener('click', function () {
      if (zustand === 'fertig') { start(); return; }
      zustand = zustand === 'laeuft' ? 'pause' : 'laeuft';
      setKnopf();
      setRunning();
    });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      offscreen = !entries[entries.length - 1].isIntersecting;
      setRunning();
    }, { threshold: 0.15 }).observe(root);
  }
  document.addEventListener('visibilitychange', setRunning);

  start();
})();
