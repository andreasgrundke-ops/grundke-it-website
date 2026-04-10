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

/* ── FAQ Accordion ── */
function initFAQ() {
  document.querySelectorAll('.faq-q').forEach(q => {
    q.addEventListener('click', () => {
      const item   = q.parentElement;
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item').forEach(i => i.classList.remove('open'));
      if (!isOpen) item.classList.add('open');
    });
  });
}

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

/* ── Init ── */
document.addEventListener('DOMContentLoaded', () => {
  initHamburger();
  initSlider();
  initFAQ();
  initScrollNav();
  initVCard();
  var lenis = initLenis();
  initScrollTop(lenis);
});
