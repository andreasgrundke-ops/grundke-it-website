/**
 * ═══════════════════════════════════════════════════════════
 * Grundke IT-Service · main.js
 * Version: 1.0.0
 * Autor: Andreas Grundke / Grundke IT-Service
 * Datum: 2026-04-05
 * Beschreibung: Shared JS – Nav, Slider, FAQ, Scroll
 * ═══════════════════════════════════════════════════════════
 */

/* ── Hamburger Menu ── */
function initHamburger() {
  const ham = document.getElementById('ham');
  const mob = document.getElementById('mobileMenu');
  if (!ham || !mob) return;

  ham.addEventListener('click', () => {
    ham.classList.toggle('open');
    mob.classList.toggle('open');
  });

  mob.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
      ham.classList.remove('open');
      mob.classList.remove('open');
    });
  });

  document.addEventListener('click', e => {
    if (!ham.contains(e.target) && !mob.contains(e.target)) {
      ham.classList.remove('open');
      mob.classList.remove('open');
    }
  });
}

/* ── Hero Slider ── */
function initSlider() {
  const wrap   = document.getElementById('slidesWrap');
  if (!wrap) return;

  const slides = wrap.querySelectorAll('.slide');
  const dots   = document.querySelectorAll('.hero-dot');
  const counter= document.getElementById('heroCounter');
  const total  = slides.length;
  let cur = 0, timer;

  function goTo(n) {
    slides[cur].classList.remove('active');
    if (dots[cur]) dots[cur].classList.remove('on');
    cur = ((n % total) + total) % total;
    slides[cur].classList.add('active');
    if (dots[cur]) dots[cur].classList.add('on');
    wrap.style.transform = `translateX(-${cur * 100}%)`;
    if (counter) counter.innerHTML = `<em>${String(cur+1).padStart(2,'0')}</em> / ${String(total).padStart(2,'0')}`;
  }

  function resetTimer() {
    clearInterval(timer);
    timer = setInterval(() => goTo(cur + 1), 13000);
  }

  const btn_next = document.getElementById('sliderNext');
  const btn_prev = document.getElementById('sliderPrev');
  if (btn_next) btn_next.addEventListener('click', () => { goTo(cur+1); resetTimer(); });
  if (btn_prev) btn_prev.addEventListener('click', () => { goTo(cur-1); resetTimer(); });

  dots.forEach(d => d.addEventListener('click', () => { goTo(+d.dataset.i); resetTimer(); }));

  // Touch swipe
  let tx = 0;
  wrap.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive:true });
  wrap.addEventListener('touchend',   e => {
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 50) { goTo(dx < 0 ? cur+1 : cur-1); resetTimer(); }
  }, { passive:true });

  resetTimer();
}

/* ── FAQ Accordion (Release-2 Schritt 5):
   FAQ ist jetzt natives <details>/<summary> — kein JS noetig.
   Funktion bleibt als No-Op, falls sie irgendwo aufgerufen wird. */
function initFAQ() { /* native details/summary */ }

/* ── Active Nav on Scroll ── */
function initScrollNav() {
  const sections = document.querySelectorAll('section[id]');
  const navAs    = document.querySelectorAll('.nav-links a');
  if (!sections.length) return;

  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        navAs.forEach(a => {
          a.style.color = a.getAttribute('href') === '#' + e.target.id ? 'var(--cyan)' : '';
        });
      }
    });
  }, { threshold: 0.35 });

  sections.forEach(s => obs.observe(s));
}

/* ── vCard Generator ── */
function initVCard() {
  const btn = document.getElementById('vcardBtn');
  if (!btn) return;

  btn.addEventListener('click', e => {
    e.preventDefault();
    const vcard = [
      'BEGIN:VCARD', 'VERSION:3.0',
      'FN:Andreas Grundke', 'N:Grundke;Andreas;;;',
      'ORG:Grundke IT-Service',
      'TITLE:IT-Service · Fachinformatiker Systemintegration',
      'TEL;TYPE=CELL,VOICE:+491782584438',
      'EMAIL;TYPE=WORK:info@grundke-it.de',
      'URL:https://www.grundke-it.de',
      'ADR;TYPE=WORK:;;Beethovenring 16;Grasbrunn;;85630;Deutschland',
      'NOTE:IT-Betreuung für KMUs im Raum München Ost.',
      'END:VCARD'
    ].join('\r\n');
    const blob = new Blob([vcard], { type: 'text/vcard;charset=utf-8' });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement('a');
    a.href = url; a.download = 'Andreas-Grundke-IT-Service.vcf';
    a.click(); URL.revokeObjectURL(url);
  });
}

/* ── Smooth Scroll (Lenis) ── */
function initLenis() {
  if (typeof Lenis === 'undefined') return;

  const lenis = new Lenis({
    duration: 1.1,
    easing: function(t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
    smoothWheel: true,
    touchMultiplier: 1.5
  });

  function raf(time) {
    lenis.raf(time);
    requestAnimationFrame(raf);
  }
  requestAnimationFrame(raf);

  // Anchor-Klicks mit Lenis smooth scrollen
  document.querySelectorAll('a[href^="#"]').forEach(function(a) {
    a.addEventListener('click', function(e) {
      var target = document.querySelector(a.getAttribute('href'));
      if (target) {
        e.preventDefault();
        lenis.scrollTo(target, { offset: -80 });
      }
    });
  });

  return lenis;
}

/* ── IT-Schnellcheck: Info-Modals + Report-Vorschau ── */
function initSchnellcheck() {
  // Texte fuer die 9 Info-Popups (wartbar an einem Ort)
  const INFO_TEXTS = {
    netzwerk: {
      title: 'Netzwerk & WLAN',
      body:  'Ich schau mir die Ausleuchtung an, die Auslastung, wie viele Geräte drin sind, wo es klemmt. Bei Bedarf mit Mess-App. Wenn das WLAN instabil ist, weißt du danach warum.'
    },
    clients: {
      title: 'Arbeitsplätze & Server',
      body:  'Welche Rechner laufen, wie alt sind sie, wie voll sind sie, welcher Windows-Stand, welche Software ist drauf. Kurzcheck auf offensichtliche Bremsen und Risiken.'
    },
    m365: {
      title: 'Microsoft 365 / E-Mail',
      body:  'Welche Lizenzen hast du, wofür zahlst du zu viel oder zu wenig, wie ist die E-Mail konfiguriert, sind Spam und Phishing abgedeckt. Falls du noch bei POP3 oder einem alten Provider bist: ehrlicher Blick drauf.'
    },
    security: {
      title: 'Virenschutz & Firewall',
      body:  'Läuft ein aktiver Virenschutz oder nur die Windows-Basisausstattung? Ist die Firewall richtig konfiguriert oder hängt alles offen im Netz? Gefahrenpunkte werden benannt, nicht dramatisiert.'
    },
    backup: {
      title: 'Datensicherung (Backup)',
      body:  'Hast du überhaupt ein Backup? Wo liegt es? Wann wurde es zuletzt getestet? Die 3-2-1-Regel ist der Maßstab — ich bewerte, wie weit du davon weg bist und was der einfachste Weg dahin wäre.'
    },
    router: {
      title: 'Router & Internet-Anschluss',
      body:  'FritzBox? Speedport? Alter? Firmware aktuell? Wird der Router noch mit Sicherheits-Updates versorgt oder ist er End-of-Life? Welche Anschlussgeschwindigkeit kommt bei dir wirklich an.'
    },
    peripherie: {
      title: 'Drucker, Kameras, Peripherie',
      body:  'Was hängt alles mit drin, wo gibt\u2019s kleine Stolperfallen. Netzwerk-Drucker ohne Passwort? Unbekannte IP-Kameras? Ich prüfe, ob da was sichtbar wird, das später zum Problem werden kann.'
    },
    eol: {
      title: 'Software-Aktualität (EOL, BSI)',
      body:  'Welche Software hast du im Einsatz, läuft davon etwas auf End-of-Life? Gibt es aktuelle BSI-Warnungen, die dich betreffen? Beispiel: TP-Link-Router, bestimmte Exchange-Stände, alte FritzBox-Firmwares.'
    },
    doku: {
      title: 'Benutzer, Passwörter, Dokumentation',
      body:  'Gibt es eine saubere Benutzerstruktur, nutzen alle eigene Konten, gibt es einen Passwortmanager, existiert überhaupt eine Dokumentation für deine Vertretung oder den Notfall? Das ist oft der meistvergessene Punkt.'
    }
  };

  const FOCUSABLE = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"]), input, select, textarea';

  // Modal-Helfer ── generisch fuer beide Modals (Info + Report)
  let lastTrigger = null;

  function openModal(modalEl) {
    if (!modalEl) return;
    lastTrigger = document.activeElement;
    modalEl.hidden = false;
    modalEl.classList.add('open');
    document.body.classList.add('modal-open');
    // Initial-Fokus auf den Dialog (nicht auf den Close-Button — angenehmer)
    const dialog = modalEl.querySelector('.modal-dialog');
    if (dialog) {
      // microtask, damit Animation startet bevor Fokus wandert
      requestAnimationFrame(() => dialog.focus());
    }
  }

  function closeModal(modalEl) {
    if (!modalEl || !modalEl.classList.contains('open')) return;
    modalEl.classList.remove('open');
    modalEl.hidden = true;
    // Body-Scroll-Lock nur entfernen, wenn kein anderes Modal mehr offen ist
    if (!document.querySelector('.modal.open')) {
      document.body.classList.remove('modal-open');
    }
    if (lastTrigger && typeof lastTrigger.focus === 'function') {
      lastTrigger.focus();
      lastTrigger = null;
    }
  }

  function trapFocus(e, modalEl) {
    if (e.key !== 'Tab') return;
    const dialog = modalEl.querySelector('.modal-dialog');
    if (!dialog) return;
    const focusables = Array.from(dialog.querySelectorAll(FOCUSABLE))
      .filter(el => !el.hasAttribute('disabled') && el.offsetParent !== null);
    if (focusables.length === 0) { e.preventDefault(); dialog.focus(); return; }
    const first = focusables[0];
    const last  = focusables[focusables.length - 1];
    const active = document.activeElement;
    if (e.shiftKey) {
      if (active === first || active === dialog) {
        e.preventDefault(); last.focus();
      }
    } else {
      if (active === last) {
        e.preventDefault(); first.focus();
      }
    }
  }

  // Info-Popups verdrahten
  const infoModal      = document.getElementById('info-modal');
  const infoModalTitle = document.getElementById('info-modal-title');
  const infoModalBody  = document.getElementById('info-modal-body');
  const infoBtns       = document.querySelectorAll('.info-btn[data-info]');

  if (infoModal && infoModalTitle && infoModalBody) {
    infoBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const key = btn.dataset.info;
        const data = INFO_TEXTS[key];
        if (!data) return;
        infoModalTitle.textContent = data.title;
        infoModalBody.innerHTML = '<p>' + data.body + '</p>';
        openModal(infoModal);
      });
    });
  }

  // Report-Vorschau verdrahten
  const previewModal = document.getElementById('preview-modal');
  const previewBtn   = document.getElementById('sc-preview-btn');
  if (previewModal && previewBtn) {
    previewBtn.addEventListener('click', () => openModal(previewModal));
  }

  // Globale Schliess-Logik fuer alle Modals (Click-Outside via [data-modal-close])
  document.querySelectorAll('.modal').forEach(modalEl => {
    modalEl.addEventListener('click', e => {
      if (e.target.closest('[data-modal-close]')) {
        closeModal(modalEl);
      }
    });
  });

  // ESC schliesst das oberste offene Modal, Tab bleibt im Modal gefangen
  document.addEventListener('keydown', e => {
    const openModalEl = document.querySelector('.modal.open');
    if (!openModalEl) return;
    if (e.key === 'Escape') {
      e.preventDefault();
      closeModal(openModalEl);
    } else if (e.key === 'Tab') {
      trapFocus(e, openModalEl);
    }
  });
}

/* ── Scroll-to-Top ── */
function initScrollTop(lenis) {
  const btn = document.getElementById('scrollTop');
  if (!btn) return;

  window.addEventListener('scroll', () => {
    btn.classList.toggle('visible', window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener('click', () => {
    if (lenis) lenis.scrollTo(0);
    else window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/* ── Flip-Cards (Release-2 Schritt 4.5)
   Tap-Toggle fuer .flip-wrap <button>-Elemente. Synchronisiert
   aria-expanded und .flipped-Klasse fuer A11y + CSS-Trigger.
   Hover-Effekt auf Pointer-Devices laeuft rein per CSS. */
function initFlipCards() {
  document.querySelectorAll('.flip-wrap').forEach(card => {
    card.addEventListener('click', () => {
      const isOpen = card.getAttribute('aria-expanded') === 'true';
      card.setAttribute('aria-expanded', String(!isOpen));
      card.classList.toggle('flipped', !isOpen);
    });
  });
}

/* ── Service Worker Registration (Release-2 PWA-Setup)
   Registriert den SW unter Scope "/", sodass die ganze Site
   als PWA installierbar wird (Add-to-Home, Offline-Cache).
   Nur in produktiven HTTPS-/localhost-Kontexten registriert. */
function initServiceWorker() {
  if (!('serviceWorker' in navigator)) return;
  if (location.protocol !== 'https:' && location.hostname !== 'localhost') return;
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js', { scope: '/' })
      .then(reg => {
        // Bei Update sofort skipWaiting triggern, damit neue Version greift
        if (reg.waiting) reg.waiting.postMessage({ type: 'SKIP_WAITING' });
        reg.addEventListener('updatefound', () => {
          const sw = reg.installing;
          if (!sw) return;
          sw.addEventListener('statechange', () => {
            if (sw.state === 'installed' && navigator.serviceWorker.controller) {
              sw.postMessage({ type: 'SKIP_WAITING' });
            }
          });
        });
      })
      .catch(err => console.warn('[SW] Registration failed:', err));
  });
}

/* ── Install-Prompt UI (PWA): zeigt nichts proaktiv, sammelt nur das
   beforeinstallprompt-Event und macht es ueber window.gIT.installPWA()
   manuell triggerbar. So kann spaeter ein Button ergaenzt werden. */
function initInstallPrompt() {
  let deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredPrompt = e;
    document.documentElement.classList.add('pwa-installable');
  });
  window.addEventListener('appinstalled', () => {
    deferredPrompt = null;
    document.documentElement.classList.remove('pwa-installable');
    document.documentElement.classList.add('pwa-installed');
  });
  window.gIT = window.gIT || {};
  window.gIT.installPWA = async () => {
    if (!deferredPrompt) return false;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    deferredPrompt = null;
    return outcome === 'accepted';
  };
}

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
  initHamburger();
  initSlider();
  initFAQ();
  initScrollNav();
  initVCard();
  initSchnellcheck();
  initFlipCards();
  initInstallPrompt();
  var lenis = initLenis();
  initScrollTop(lenis);
});

/* SW-Registrierung laeuft eigenstaendig ueber window.load */
initServiceWorker();
