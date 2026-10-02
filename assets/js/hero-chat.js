/**
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · hero-chat.js
 * Version: 1.0.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-10-02
 * Beschreibung: Hero „Der Chat" auf der Startseite. Im gezeichneten Handy
 *   laeuft ein Beispiel-Einsatz als Chat ab: Kundennachricht, Andreas tippt,
 *   Fernwartung, Ergebnis, Dank. Die Zeitstempel sind die echte Uhrzeit des
 *   Besuchers; abends, am Wochenende und nachts steht darueber eine Zeile.
 * Ablauf:
 *   1. Elemente suchen, ohne Hero sofort Abbruch.
 *   2. Tageszeit bestimmen (tag / abend / nacht), Uhrzeit-Zeile setzen und
 *      jede halbe Minute nachziehen.
 *   3. Bei prefers-reduced-motion: ersten Fall fertig hinstellen, nichts bewegt sich.
 *   4. Sonst: Faelle als Schrittliste abspielen (Zeitpunkt in ms je Schritt),
 *      danach den naechsten Fall, endlos.
 *   5. Anhalten: per Knopf (WCAG 2.2.2) und automatisch, wenn der Hero aus dem
 *      Bild gescrollt oder der Tab im Hintergrund ist.
 * Aenderungshistorie:
 *   1.0.0 (2026-10-02) Erste Fassung, ersetzt den Foto-Slider aus main.js.
 * ═══════════════════════════════════════════════════════════
 */
(function () {
  'use strict';

  var root = document.querySelector('[data-hero-chat]');
  if (!root) return;
  var thread = root.querySelector('[data-hc-thread]');
  var clockEl = root.querySelector('[data-hc-clock]');
  var pauseBtn = root.querySelector('[data-hc-pause]');
  if (!thread) return;

  var reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Beispielfaelle aus den „Acht Situationen" der Startseite.
     night:false = Fall passt nicht zu einer Nachricht mitten in der Nacht. */
  var CASES = [
    { me: 'Hi Andreas, unser Drucker druckt nichts mehr. Morgen ist Abgabe.',
      ag: 'Bin dran. Ich schalte mich kurz auf euren Rechner.',
      run: 'Fernwartung verbunden …', done: 'Druckwarteschlange geleert',
      fix: 'Die Warteschlange hing. Läuft wieder.',
      thanks: 'Super, danke dir!', night: true },
    { me: 'Lisa kommt nicht mehr in ihr Postfach. Gleich ist ein Kundentermin.',
      ag: 'Ich kümmere mich. Sie soll kurz am Rechner bleiben.',
      run: 'Konto wird entsperrt …', done: 'Konto entsperrt, Zwei-Faktor neu eingerichtet',
      fix: 'Erledigt, sie kommt wieder rein.',
      thanks: 'Perfekt, das war knapp.', night: false },
    { me: 'Im Besprechungsraum ist schon wieder kein WLAN.',
      ag: 'Ich schau mir euer Netz aus der Ferne an.',
      run: 'Access Point wird geprüft …', done: 'Access Point neu gestartet, Kanal gewechselt',
      fix: 'Der Access Point hing. Ich behalte ihn im Blick.',
      thanks: 'Danke, die Präsentation ist gerettet.', night: true },
    { me: 'Unser Kollege, der die IT nebenbei gemacht hat, hört Ende des Monats auf.',
      ag: 'Dann setzen wir uns nächste Woche zusammen. Ich nehme alles auf und übernehme.',
      run: 'IT-Schnellcheck wird geplant …', done: 'IT-Schnellcheck am Dienstag, 9 Uhr',
      fix: 'Danach weißt du genau, was läuft und was nicht.',
      thanks: 'Klingt gut, bis Dienstag.', night: true }
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
     die frueheren liegen davor. Nachts antwortet Andreas um 07:12. */
  function timesFor(now) {
    if (dayMode(now) === 'night') {
      var m = morningOf(now);
      return { me: now, ag: m, fix: plus(m, 8), thanks: plus(m, 9), night: true };
    }
    return { me: plus(now, -10), ag: plus(now, -9), fix: plus(now, -1), thanks: now, night: false };
  }

  function updateClock() {
    if (!clockEl) return;
    var now = new Date(), mode = dayMode(now);
    clockEl.textContent = '';
    clockEl.classList.toggle('is-empty', mode === 'day');
    if (mode === 'day') return;
    var t = document.createElement('time');
    t.textContent = hhmm(now) + ' Uhr';
    clockEl.appendChild(document.createTextNode('Es ist '));
    clockEl.appendChild(t);
    clockEl.appendChild(document.createTextNode(mode === 'night'
      ? '. Schreib einfach, ich melde mich, sobald ich wach bin.'
      : '. Bei mir gibt\'s keine Öffnungszeiten.'));
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
    while (thread.children.length > 7) thread.removeChild(thread.firstChild);
    return node;
  }

  /* ── Statisch (reduced-motion): erster Fall, fertig ── */
  function renderStatic() {
    var c = CASES[0], t = timesFor(new Date());
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

  updateClock();
  setInterval(updateClock, 30000);

  if (reduceMotion) { renderStatic(); return; }

  /* ── Abspielen ── */
  var steps = [], stepIdx = 0, elapsed = 0, lastTs = 0, timer = 0, caseIdx = 0;
  var userPaused = false, offscreen = false;

  function stepsFor(c, now) {
    var t = timesFor(now), typingNode, sysNode;
    return [
      { at: 0, run: function () {
        thread.textContent = '';
        thread.classList.remove('is-out');
        add(el('li', 'hc-day', 'Heute'));
      } },
      { at: 450, run: function () { add(msg('me', c.me, t.me)); } },
      { at: 1700, run: function () { typingNode = add(typing()); } },
      { at: 3200, run: function () {
        thread.removeChild(typingNode);
        add(msg('ag', t.night ? NIGHT_REPLY : c.ag, t.ag));
      } },
      { at: 4600, run: function () { sysNode = add(sys(c.run)); sysNode.classList.add('is-run'); } },
      { at: 6700, run: function () {
        sysNode.classList.remove('is-run');
        sysNode.classList.add('is-done');
        sysNode.firstChild.textContent = c.done;
      } },
      { at: 7700, run: function () { typingNode = add(typing()); } },
      { at: 9100, run: function () {
        thread.removeChild(typingNode);
        add(msg('ag', c.fix, t.fix));
      } },
      { at: 10500, run: function () { add(msg('me', c.thanks, t.thanks)); } },
      { at: 14000, run: function () { thread.classList.add('is-out'); } },
      { at: 14700, run: nextCase }
    ];
  }

  function nextCase() {
    var night = dayMode(new Date()) === 'night';
    var pool = CASES.filter(function (c) { return !night || c.night; });
    var c = pool[caseIdx % pool.length];
    caseIdx++;
    steps = stepsFor(c, new Date());
    stepIdx = 0;
    elapsed = 0;
  }

  function tick() {
    var ts = performance.now();
    elapsed += ts - lastTs;
    lastTs = ts;
    while (stepIdx < steps.length && elapsed >= steps[stepIdx].at) {
      steps[stepIdx++].run();
    }
  }

  function setRunning() {
    var run = !userPaused && !offscreen && !document.hidden;
    root.classList.toggle('is-paused', !run);
    if (run && !timer) {
      lastTs = performance.now();
      timer = setInterval(tick, 100);
    } else if (!run && timer) {
      clearInterval(timer);
      timer = 0;
    }
  }

  if (pauseBtn) {
    pauseBtn.hidden = false;
    pauseBtn.addEventListener('click', function () {
      userPaused = !userPaused;
      pauseBtn.setAttribute('aria-pressed', String(userPaused));
      pauseBtn.setAttribute('aria-label', userPaused ? 'Beispiel-Chat fortsetzen' : 'Beispiel-Chat anhalten');
      setRunning();
    });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) {
      offscreen = !entries[0].isIntersecting;
      setRunning();
    }, { threshold: 0.15 }).observe(root);
  }
  document.addEventListener('visibilitychange', setRunning);

  nextCase();
  setRunning();
})();
