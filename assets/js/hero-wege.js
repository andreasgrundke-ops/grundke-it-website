/**
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · hero-wege.js
 * Version: 1.0.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-10-18
 * Beschreibung: Hero „Zwei Wege" auf der Startseite. Die Buehne zeigt vier
 *   Beispiele aus dem Alltag in zwei Spuren (ohne feste Betreuung / mit
 *   Grundke-Betreuung) und bleibt danach im Endstand stehen. Alle Texte stehen
 *   im HTML, dieses Skript schaltet nur Klassen (is-on) und Attribute um.
 * Ablauf:
 *   1. Buehne [data-zw] suchen, ohne Buehne sofort Abbruch.
 *   2. Bei prefers-reduced-motion: nichts tun – das HTML liefert den Endstand.
 *   3. Sonst nach dem Laden und zwei requestAnimationFrame starten (die H1
 *      bleibt das LCP-Element), Pause-Knopf einblenden.
 *   4. Schrittliste mit Zeitpunkten (ms) abarbeiten: ein Schritt je Takt,
 *      verspaetete Takte werden nicht nachgeholt. Fall 1 bis 4 je 7 s, dann
 *      Schluss und Endstand (data-zustand="ende"), Knopf „Nochmal abspielen".
 *   5. Anhalten per Knopf (WCAG 2.2.2) und automatisch, solange weniger als
 *      20 % der Buehne sichtbar sind oder der Tab im Hintergrund liegt.
 * Aenderungshistorie:
 *   1.0.0 (2026-10-18) Erste Fassung.
 * ═══════════════════════════════════════════════════════════
 */
(function () {
  'use strict';

  var stage = document.querySelector('[data-zw]');
  if (!stage) return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  var knopf = stage.parentNode.querySelector('[data-zw-pause]');
  var links = stage.querySelector('.zw-lane--links');
  var rechts = stage.querySelector('.zw-lane--rechts');
  var schluss = stage.querySelector('.zw-schluss');
  var punkte = stage.querySelectorAll('.zw-dots i');
  if (!links || !rechts) return;

  var FAELLE = 4, FALL_MS = 7000, AUS_MS = 250;

  function an(el, ja) { if (el) el.classList.toggle('is-on', ja); }
  function alle(list, ja) { for (var i = 0; i < list.length; i++) an(list[i], ja); }
  function faelle(n) { return stage.querySelectorAll('.zw-case[data-fall="' + n + '"]'); }
  function texte(spur, n) { return spur.querySelectorAll('.zw-case[data-fall="' + n + '"] .zw-t'); }

  /* ── Schrittliste: [Zeitpunkt in ms, Funktion] ── */
  var schritte = [[0, function () {          // Start aus dem Endstand: Texte ausblenden
    alle(stage.querySelectorAll('.zw-case'), false);
    an(schluss, false);
  }]];

  function fall(n) {
    var t0 = AUS_MS + (n - 1) * FALL_MS, l = texte(links, n), r = texte(rechts, n);
    schritte.push(
      [t0, function () {
        stage.setAttribute('data-fall', String(n));
        for (var i = 0; i < punkte.length; i++) {
          punkte[i].className = i < n - 1 ? 'is-done' : (i === n - 1 ? 'is-on' : '');
        }
        alle(l, false); alle(r, false);
        an(links, true); an(rechts, false);
        alle(faelle(n), true);
      }],
      [t0 + 300, function () { an(l[0], true); }],
      [t0 + 1300, function () { an(l[1], true); }],
      [t0 + 3000, function () { an(links, false); }],         // unter 1024 px: erst links aus ...
      [t0 + 3300, function () { an(rechts, true); an(r[0], true); }],   // ... dann rechts ein
      [t0 + 4500, function () { an(r[1], true); }]
    );
    if (n < FAELLE) {
      schritte.push([t0 + 6750, function () { alle(faelle(n), false); an(rechts, false); }]);
    } else {
      schritte.push(
        [t0 + 7000, function () { an(schluss, true); }],
        [t0 + 7300, function () { setzeZustand('ende'); }]
      );
    }
  }
  for (var n = 1; n <= FAELLE; n++) fall(n);

  /* ── Takt ── */
  var idx = 0, timer = 0, faellig = 0, rest = 0;
  var zustand = 'ende', ausserSicht = false, imHintergrund = !!document.hidden;

  function setzeZustand(z) {
    zustand = z;
    stage.setAttribute('data-zustand', z);
    if (knopf) {
      knopf.setAttribute('data-zustand', z);
      knopf.setAttribute('aria-label', knopf.getAttribute('data-label-' + z) || '');
    }
  }

  function darfLaufen() { return zustand === 'laeuft' && !ausserSicht && !imHintergrund; }

  function plane(ms) {
    faellig = Date.now() + ms;
    timer = setTimeout(takt, ms);
  }

  function takt() {
    timer = 0;
    var s = schritte[idx++];
    s[1]();
    if (idx < schritte.length && darfLaufen()) plane(schritte[idx][0] - s[0]);
    else rest = idx < schritte.length ? schritte[idx][0] - s[0] : 0;
  }

  function anhalten() {
    if (!timer) return;
    clearTimeout(timer);
    timer = 0;
    rest = Math.max(0, faellig - Date.now());
  }

  function weiter() {
    if (timer || !darfLaufen() || idx >= schritte.length) return;
    plane(rest);
  }

  function abgleichen() { if (darfLaufen()) weiter(); else anhalten(); }

  function starten() {
    anhalten();
    idx = 0; rest = 0;
    setzeZustand('laeuft');
    weiter();
  }

  if (knopf) {
    knopf.addEventListener('click', function () {
      if (zustand === 'laeuft') { anhalten(); setzeZustand('pause'); }
      else if (zustand === 'pause') { setzeZustand('laeuft'); weiter(); }
      else starten();
    });
  }

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (eintraege) {
      var e = eintraege[eintraege.length - 1];
      ausserSicht = !e.isIntersecting || e.intersectionRatio < 0.2;
      abgleichen();
    }, { threshold: [0, 0.2] }).observe(stage);
  }
  document.addEventListener('visibilitychange', function () {
    imHintergrund = !!document.hidden;
    abgleichen();
  });

  function los() {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        if (knopf) knopf.hidden = false;
        starten();
      });
    });
  }
  if (document.readyState === 'complete') los();
  else window.addEventListener('load', los, { once: true });
})();
