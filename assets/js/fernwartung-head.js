/*
 * Grundke IT-Service · /fernwartung/ · Kopf-Skript
 * Seit 08.11.2026 (Release 2.3.0) eigene Datei statt Inline-Skript (kommende CSP script-src 'self').
 * Laeuft synchron im <head>, vor dem ersten Bild: mit JS nur die Windows-Anleitung zeigen, bis fernwartung.js
 * umschaltet. Meldet sich fernwartung.js bis 3 s nach DOMContentLoaded nicht (data-fw-ready, z. B. blockiert,
 * offline oder Fehler), nimmt der Rueckfall die Klasse js wieder weg: alle drei Anleitungen sichtbar, die
 * reservierte Reiterzeile verborgen.
 */
(function (d) { d.classList.add('js'); document.addEventListener('DOMContentLoaded', function () { setTimeout(function () { if (d.dataset.fwReady !== '1') d.classList.remove('js'); }, 3000); }); })(document.documentElement);
