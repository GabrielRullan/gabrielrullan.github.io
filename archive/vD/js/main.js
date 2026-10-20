/**
 * Version D: Authoritative Hybrid JavaScript
 * Vanilla ES2020+ interactions: Sticky Header, Mobile Drawer,
 * Accessible FAQ Accordion, and Smooth Navigation.
 * Zero external libraries, zero console errors.
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Sticky Header elevation on scroll
  const header = document.querySelector('.site-header');
  if (header) {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        header.classList.add('scrolled');
      } else {
        header.classList.remove('scrolled');
      }
    };
    window.addEventListener('scroll', handleScroll, { passive: true });
    handleScroll();
  }

  // 2. Mobile Nav Drawer Toggle
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const drawer = document.querySelector('.mobile-nav-drawer');

  if (toggleBtn && drawer) {
    toggleBtn.addEventListener('click', () => {
      const isOpen = drawer.classList.contains('open');
      if (isOpen) {
        drawer.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      } else {
        drawer.classList.add('open');
        toggleBtn.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden';
      }
    });

    // Close on link click inside drawer
    const drawerLinks = drawer.querySelectorAll('a');
    drawerLinks.forEach((link) => {
      link.addEventListener('click', () => {
        drawer.classList.remove('open');
        toggleBtn.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
      });
    });
  }

  // 3. Accessible FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach((item) => {
    const btn = item.querySelector('.faq-question-btn');
    const panel = item.querySelector('.faq-answer-panel');

    if (btn && panel) {
      btn.addEventListener('click', () => {
        const isActive = item.classList.contains('active');

        // Close other items
        faqItems.forEach((other) => {
          if (other !== item) {
            other.classList.remove('active');
            const otherBtn = other.querySelector('.faq-question-btn');
            const otherPanel = other.querySelector('.faq-answer-panel');
            if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
            if (otherPanel) otherPanel.style.maxHeight = null;
          }
        });

        // Toggle current item
        if (isActive) {
          item.classList.remove('active');
          btn.setAttribute('aria-expanded', 'false');
          panel.style.maxHeight = null;
        } else {
          item.classList.add('active');
          btn.setAttribute('aria-expanded', 'true');
          panel.style.maxHeight = panel.scrollHeight + 'px';
        }
      });
    }
  });

  // 4. Smooth Anchor Scrolling & Focus Management
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#' || targetId === '') return;

      const targetEl = document.querySelector(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: 'smooth' });
        // Update URL hash safely without jumping
        if (history.pushState) {
          history.pushState(null, null, targetId);
        }
      }
    });
  });

  // 5. Catalan Notification Modal/Toast
  const catalaBtn = document.querySelector('#btn-lang-ca');
  if (catalaBtn) {
    catalaBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const existingToast = document.querySelector('.ca-toast-notification');
      if (existingToast) existingToast.remove();

      const toast = document.createElement('div');
      toast.className = 'ca-toast-notification';
      toast.style.cssText = `
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: #0e1726;
        color: #ffffff;
        border: 1px solid #10b981;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        z-index: 2000;
        max-width: 360px;
        font-family: 'DM Sans', sans-serif;
        font-size: 0.95rem;
        line-height: 1.45;
      `;
      toast.innerHTML = `
        <div style="font-weight:700; color:#fbbf24; margin-bottom:4px; font-family:'Plus Jakarta Sans', sans-serif;">
          Parlem en Català
        </div>
        <div>
          Fluïdesa nativa en català per a reunions directives, comitès de direcció i documentació executiva.
        </div>
        <button type="button" style="margin-top:10px; background:#056a3e; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-weight:600; font-size:0.8rem;">
          Tancar
        </button>
      `;
      document.body.appendChild(toast);
      toast.querySelector('button').addEventListener('click', () => toast.remove());
      setTimeout(() => { if (toast.parentNode) toast.remove(); }, 6000);
    });
  }
});
