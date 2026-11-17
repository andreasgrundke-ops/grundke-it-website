/*
 * Grundke IT-Service · /tree/ · vCard-Download und Service-Worker-Anmeldung
 * Seit 08.11.2026 (Release 2.3.0) eigene Datei statt Inline-Skript (kommende CSP script-src 'self').
 * Bewusst nicht im Pre-Cache von sw.js (Seite ist unverlinkt).
 */
/* vCard generieren und als Download anbieten */
document.getElementById('vcardBtn').addEventListener('click', function(e) {
  e.preventDefault();

  var vcard = [
    'BEGIN:VCARD',
    'VERSION:3.0',
    'FN:Andreas Grundke',
    'N:Grundke;Andreas;;;',
    'ORG:Grundke IT-Service',
    'TITLE:IT-Service · Fachinformatiker Systemintegration',
    'TEL;TYPE=CELL,VOICE:+491782584438',
    'TEL;TYPE=WORK,VOICE:+491782584438',
    'EMAIL;TYPE=WORK:info@grundke-it.de',
    'URL:https://grundke-it.de',
    'ADR;TYPE=WORK:;;Beethovenring 16;Grasbrunn;;85630;Deutschland',
    'NOTE:IT-Betreuung für KMUs im Raum München Ost. Kein Ticketsystem – immer persönlich.',
    'END:VCARD'
  ].join('\r\n');

  var blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8' });
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = 'Andreas-Grundke-IT-Service.vcf';
  a.click();
  URL.revokeObjectURL(url);
});

/* Release-2 PWA: Service Worker auch von tree-Page registrieren,
   damit Add-to-Home-Screen ueberall greift. */
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .catch(err => console.warn('[SW] tree page registration failed:', err));
  });
}
