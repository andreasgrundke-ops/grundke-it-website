/**
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · fernwartung.js
 * Version: 1.0.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-10-09
 * Beschreibung: Betriebssystem-Umschalter auf /fernwartung/ (Windows, Linux,
 *   macOS) und Kopierknopf fuer die Linux-Befehlszeile. Ohne JS stehen alle
 *   drei Anleitungen untereinander.
 * Ablauf:
 *   1. Umschalter und Bereiche suchen, ohne sie sofort Abbruch.
 *   2. Startsystem bestimmen: Sprungmarke in der Adresse (#windows, #linux,
 *      #mac) vor erkanntem Geraet vor Windows.
 *   3. Umschalter einblenden, nur den gewaehlten Bereich zeigen.
 *   4. Klick und Pfeiltasten (WAI-ARIA Tabs) wechseln das System und schreiben
 *      die Sprungmarke in die Adresse, damit sich der Link weitergeben laesst.
 *      Die Bereiche heissen fw-windows usw., damit der Browser bei #linux nicht
 *      selbst dorthin springt und die Reiter verdeckt.
 *   5. Kopierknopf: Befehl in die Zwischenablage, kurz „Kopiert" anzeigen.
 * Aenderungshistorie:
 *   1.0.0 (2026-10-09) Erste Fassung. Nach Code-Review: Tab-Rollen erst per JS,
 *                      Rueckfall auf alle drei Anleitungen, wenn etwas fehlt,
 *                      Kopier-Rueckmeldung auch fuer Screenreader.
 * ═══════════════════════════════════════════════════════════
 */
(function () {
  'use strict';

  /* Fehlt etwas, alle drei Anleitungen zeigen (die Klasse js im Kopf blendet sie sonst aus) */
  function rueckfall() { document.documentElement.classList.remove('js'); }

  var box = document.querySelector('[data-fw-os]');
  if (!box) { rueckfall(); return; }
  var tabs = Array.prototype.slice.call(box.querySelectorAll('[role="tab"]')).filter(function (t) {
    return !!document.getElementById(t.getAttribute('aria-controls'));
  });
  if (tabs.length < 2) { rueckfall(); return; }
  var autoHint = box.querySelector('[data-fw-os-auto]');
  var OS_LIST = tabs.map(function (t) { return t.getAttribute('data-os'); });

  function panelOf(tab) { return document.getElementById(tab.getAttribute('aria-controls')); }

  /* Geraet erkennen. iPad meldet sich als Mac, hat aber Touch - dort nichts vorwaehlen,
     ebenso bei Android und anderen Handys */
  function detectOs() {
    var ua = navigator.userAgent || '';
    var plat = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || '';
    var probe = plat + ' ' + ua;
    if (/Android|iPhone|iPad|iPod|CrOS/i.test(ua)) return null;
    if (/Win/i.test(probe)) return 'windows';
    if (/Mac/i.test(probe)) return navigator.maxTouchPoints > 1 ? null : 'mac';
    if (/Linux|X11/i.test(probe)) return 'linux';
    return null;
  }

  function fromHash() {
    var h = (location.hash || '').replace('#', '').toLowerCase();
    return OS_LIST.indexOf(h) >= 0 ? h : null;
  }

  function select(os, opts) {
    opts = opts || {};
    tabs.forEach(function (t) {
      var on = t.getAttribute('data-os') === os;
      t.setAttribute('aria-selected', on ? 'true' : 'false');
      t.tabIndex = on ? 0 : -1;
      panelOf(t).hidden = !on;
      if (on && opts.focus) t.focus();
    });
    if (opts.writeHash && history.replaceState) {
      history.replaceState(null, '', '#' + os);
    }
  }

  /* Bereiche in Tab-Darstellung schalten (ohne JS stehen sie als einfache Abschnitte untereinander) */
  tabs.forEach(function (t) {
    var p = panelOf(t);
    p.classList.add('is-tab');
    p.setAttribute('role', 'tabpanel');
    p.setAttribute('aria-labelledby', t.id);
    p.tabIndex = 0;
  });

  var start = fromHash();
  var detected = detectOs();
  if (!start && detected) {
    start = detected;
    if (autoHint) autoHint.hidden = false;
  }
  box.hidden = false;
  select(start || 'windows');

  function hideAutoHint() { if (autoHint) autoHint.hidden = true; }

  tabs.forEach(function (t, i) {
    t.addEventListener('click', function () {
      select(t.getAttribute('data-os'), { writeHash: true });
      hideAutoHint();
    });
    t.addEventListener('keydown', function (e) {
      var next = null;
      if (e.key === 'ArrowRight') next = (i + 1) % tabs.length;
      else if (e.key === 'ArrowLeft') next = (i - 1 + tabs.length) % tabs.length;
      else if (e.key === 'Home') next = 0;
      else if (e.key === 'End') next = tabs.length - 1;
      if (next === null) return;
      e.preventDefault();
      select(tabs[next].getAttribute('data-os'), { focus: true, writeHash: true });
      hideAutoHint();
    });
  });

  window.addEventListener('hashchange', function () {
    var os = fromHash();
    if (os) { select(os); hideAutoHint(); }
  });

  /* ── Kopierknopf ── */
  var copyBtns = document.querySelectorAll('[data-fw-copy]');
  Array.prototype.forEach.call(copyBtns, function (btn) {
    var src = document.getElementById(btn.getAttribute('data-fw-copy'));
    var label = btn.querySelector('span');
    var status = btn.parentNode.querySelector('[data-fw-copy-status]');
    if (!src || !label || !navigator.clipboard) return;
    function melden(text) { if (status) status.textContent = text; }
    btn.hidden = false;
    var timer = null;
    btn.addEventListener('click', function () {
      navigator.clipboard.writeText(src.textContent).then(function () {
        btn.classList.add('is-done');
        label.textContent = 'Kopiert';
        melden('Befehl in die Zwischenablage kopiert');
      }, function () {
        label.textContent = 'Bitte markieren';
        melden('Kopieren nicht möglich, bitte den Befehl markieren und kopieren');
      }).then(function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          btn.classList.remove('is-done');
          label.textContent = 'Kopieren';
          melden('');
        }, 2200);
      });
    });
  });
})();
