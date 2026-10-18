/**
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · hero-wege.js
 * Version: 2.1.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-10-18
 * Beschreibung: Hero „Ein Weg" auf der Startseite. Die Buehne „So läuft das
 *   bei mir" zeigt vier Beispiele, je Fall drei Bilder nacheinander (Problem,
 *   Andreas ist dran, geloest), und bleibt danach im Endstand stehen. Alle
 *   Texte stehen im HTML, dieses Skript schaltet nur Klassen (is-on) und
 *   Attribute (data-fall, data-bild, data-zustand) um.
 * Ablauf:
 *   1. Buehne [data-zw] suchen, ohne Buehne sofort Abbruch.
 *   2. Bei prefers-reduced-motion: nichts tun – das HTML liefert den Endstand.
 *   3. Sonst nach dem Laden und zwei requestAnimationFrame starten (die H1
 *      bleibt das LCP-Element), Pause-Knopf einblenden.
 *   4. Schrittliste mit Zeitpunkten (ms) abarbeiten: ein Schritt je Takt,
 *      verspaetete Takte werden nicht nachgeholt. Fall 1 bis 4 je 7 s mit drei
 *      Bildern, danach Schluss und Endstand (data-zustand="ende"), Knopf
 *      „Nochmal abspielen". Gesamtdauer rund 28 s.
 *   5. Anhalten per Knopf (WCAG 2.2.2) und automatisch, solange weniger als
 *      20 % der Buehne sichtbar sind oder der Tab im Hintergrund liegt.
 *   6. Wird reduzierte Bewegung erst waehrend des Besuchs eingeschaltet:
 *      sofort zurueck in den Endstand aus dem HTML, Knopf ausblenden.
 *   7. Mitte: Die Textspalte reserviert Platz fuer alle drei Bilder und den
 *      Schluss. Damit die Buehne nie halb leer wirkt, wird sie per transform
 *      so verschoben, dass die sichtbaren Bilder neben der Figur mittig
 *      stehen (nur transform, die Hoehe bleibt fest, kein CLS).
 * Aenderungshistorie:
 *   1.0.0 (2026-10-18) Erste Fassung (Vorstufe, nicht veroeffentlicht).
 *   1.0.1 (2026-10-18) Umschalten auf reduzierte Bewegung waehrend des Besuchs
 *                      fuehrt sofort in den Endstand.
 *   2.0.0 (2026-10-18) Ein Weg: eine Spur, drei Bilder je Fall, eine Figur mit
 *                      Zustand je Bild (data-bild); der Spurwechsel entfaellt.
 *   2.1.0 (2026-10-18) Sichtbare Bilder vertikal mittig (transform), auch nach
 *                      Groessenaenderung des Fensters.
 * ═══════════════════════════════════════════════════════════
 */
(function () {
  'use strict';

  var stage = document.querySelector('[data-zw]');
  if (!stage) return;
  var ruhig = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
  if (ruhig && ruhig.matches) return;

  var knopf = stage.parentNode.querySelector('[data-zw-pause]');
  var schluss = stage.querySelector('.zw-schluss');
  var spalte = stage.querySelector('.zw-txt');
  var aktuell = null;                      // gerade sichtbarer Fall
  var punkte = stage.querySelectorAll('.zw-dots i');

  var FAELLE = 4, FALL_MS = 7000, AUS_MS = 250;
  var BILD_MS = [300, 2300, 4300];        // Bild 1, 2, 3 je Fall, ab Fallbeginn

  /* Endstand = HTML-Grundzustand: Klassen und Attribute vor der ersten Aenderung merken */
  var grund = Array.prototype.map.call(stage.querySelectorAll('[class]'), function (e) {
    return [e, e.getAttribute('class')];
  });
  var grundAttr = ['data-fall', 'data-bild'].map(function (a) { return [a, stage.getAttribute(a)]; });

  function an(el, ja) { if (el) el.classList.toggle('is-on', ja); }
  function alle(list, ja) { for (var i = 0; i < list.length; i++) an(list[i], ja); }

  /* Sichtbaren Teil der Textspalte mittig setzen: halber freier Platz unter dem letzten sichtbaren Bild.
     .zw-txt ist position:relative und damit offsetParent der Bilder; offsetTop/-Height ignorieren transforms, die
     Messung bleibt also stabil. sofort = ohne Uebergang (Fallwechsel) */
  function mitte(sofort) {
    if (!spalte) return;
    var y = 0;
    if (aktuell && !(schluss && schluss.classList.contains('is-on'))) {
      var sichtbar = aktuell.querySelectorAll('.zw-t.is-on');
      var letztes = sichtbar.length ? sichtbar[sichtbar.length - 1] : aktuell.querySelector('.zw-zeit');
      if (letztes) {
        var unten = letztes.offsetTop + letztes.offsetHeight;
        y = Math.max(0, Math.round((spalte.offsetHeight - unten) / 2));
      }
    }
    if (sofort) spalte.style.transition = 'none';
    spalte.style.transform = y ? 'translateY(' + y + 'px)' : '';
    if (sofort) { void spalte.offsetHeight; spalte.style.transition = ''; }
  }

  /* ── Schrittliste: [Zeitpunkt in ms, Funktion] ── */
  var schritte = [[0, function () {          // Start aus dem Endstand: Texte ausblenden
    alle(stage.querySelectorAll('.zw-case'), false);
    an(schluss, false);
  }]];

  function fall(n) {
    var t0 = AUS_MS + (n - 1) * FALL_MS;
    var el = stage.querySelector('.zw-case[data-fall="' + n + '"]');
    var bilder = el ? el.querySelectorAll('.zw-t') : [];
    schritte.push([t0, function () {
      stage.setAttribute('data-fall', String(n));
      stage.setAttribute('data-bild', '1');
      for (var i = 0; i < punkte.length; i++) {
        punkte[i].className = i < n - 1 ? 'is-done' : (i === n - 1 ? 'is-on' : '');
      }
      alle(bilder, false);
      aktuell = el;
      mitte(true);
      an(el, true);
    }]);
    BILD_MS.forEach(function (ms, k) {
      schritte.push([t0 + ms, function () {
        stage.setAttribute('data-bild', String(k + 1));
        an(bilder[k], true);
        mitte(false);
      }]);
    });
    if (n < FAELLE) {
      schritte.push([t0 + 6750, function () { an(el, false); }]);
    } else {
      schritte.push(
        [t0 + 5600, function () { an(schluss, true); mitte(false); }],
        [t0 + 6200, function () { setzeZustand('ende'); }]
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

  function endstand() {
    anhalten();
    idx = schritte.length; rest = 0;
    grund.forEach(function (g) { g[0].setAttribute('class', g[1]); });
    grundAttr.forEach(function (a) { if (a[1] !== null) stage.setAttribute(a[0], a[1]); });
    aktuell = null;
    mitte(true);
    setzeZustand('ende');
    if (knopf) knopf.hidden = true;
  }

  if (knopf) {
    knopf.addEventListener('click', function () {
      if (ruhig && ruhig.matches) return;
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
  window.addEventListener('resize', function () { mitte(true); });
  document.addEventListener('visibilitychange', function () {
    imHintergrund = !!document.hidden;
    abgleichen();
  });

  if (ruhig) {
    var umschalten = function () { if (ruhig.matches) endstand(); };
    if (ruhig.addEventListener) ruhig.addEventListener('change', umschalten);
    else if (ruhig.addListener) ruhig.addListener(umschalten);
  }

  function los() {
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        if (ruhig && ruhig.matches) { endstand(); return; }
        if (knopf) knopf.hidden = false;
        starten();
      });
    });
  }
  if (document.readyState === 'complete') los();
  else window.addEventListener('load', los, { once: true });
})();
