/**
 * Gabriel Rul-lan | Version C: Applied Mathematician & Systems Builder
 * Client-side script: Mobile nav, Benchmark Tabs, Clipboard helper, Telemetry
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileNav();
  initBenchmarkTabs();
  initTelemetryClock();
  initCopyButtons();
});

/**
 * Mobile Navigation Toggle & Accessibility
 */
function initMobileNav() {
  const toggleBtn = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (!toggleBtn || !navLinks) return;

  toggleBtn.addEventListener('click', () => {
    const isExpanded = toggleBtn.getAttribute('aria-expanded') === 'true';
    toggleBtn.setAttribute('aria-expanded', String(!isExpanded));
    navLinks.classList.toggle('active');
  });

  // Close menu on link click
  navLinks.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      toggleBtn.setAttribute('aria-expanded', 'false');
      navLinks.classList.remove('active');
    });
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && navLinks.classList.contains('active')) {
      toggleBtn.setAttribute('aria-expanded', 'false');
      navLinks.classList.remove('active');
      toggleBtn.focus();
    }
  });
}

/**
 * Benchmark Console Tabs Switcher
 */
function initBenchmarkTabs() {
  const tabs = document.querySelectorAll('.console-tab');
  const panes = document.querySelectorAll('.benchmark-tab-pane');

  if (!tabs.length || !panes.length) return;

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      activateTab(tab, tabs, panes);
    });

    // Keyboard arrow navigation
    tab.addEventListener('keydown', (e) => {
      let targetIndex = -1;
      if (e.key === 'ArrowRight') {
        targetIndex = (index + 1) % tabs.length;
      } else if (e.key === 'ArrowLeft') {
        targetIndex = (index - 1 + tabs.length) % tabs.length;
      }

      if (targetIndex !== -1) {
        e.preventDefault();
        tabs[targetIndex].focus();
        activateTab(tabs[targetIndex], tabs, panes);
      }
    });
  });
}

function activateTab(activeTab, allTabs, allPanes) {
  const targetId = activeTab.getAttribute('data-target');

  allTabs.forEach(t => {
    t.classList.remove('active');
    t.setAttribute('aria-selected', 'false');
    t.setAttribute('tabindex', '-1');
  });

  allPanes.forEach(p => {
    p.classList.remove('active');
  });

  activeTab.classList.add('active');
  activeTab.setAttribute('aria-selected', 'true');
  activeTab.removeAttribute('tabindex');

  const targetPane = document.getElementById(targetId);
  if (targetPane) {
    targetPane.classList.add('active');
  }
}

/**
 * Live Telemetry Clock (UTC + 1 / Mallorca Local)
 */
function initTelemetryClock() {
  const clockEl = document.getElementById('telemetry-clock');
  if (!clockEl) return;

  function updateClock() {
    const now = new Date();
    // Format UTC ISO timestamp
    const hours = String(now.getUTCHours()).padStart(2, '0');
    const minutes = String(now.getUTCMinutes()).padStart(2, '0');
    const seconds = String(now.getUTCSeconds()).padStart(2, '0');
    clockEl.textContent = `${hours}:${minutes}:${seconds} UTC`;
  }

  updateClock();
  setInterval(updateClock, 1000);
}

/**
 * Copy to Clipboard Helper for Terminal Snippets
 */
function initCopyButtons() {
  const copyBtns = document.querySelectorAll('.terminal-copy-cmd');

  copyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const textToCopy = btn.getAttribute('data-copy') || btn.textContent.trim();
      navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = btn.innerHTML;
        btn.innerHTML = `<span style="color: #10B981;">✓ COPIED TO CLIPBOARD</span> <span>[OK]</span>`;
        setTimeout(() => {
          btn.innerHTML = originalText;
        }, 2500);
      }).catch(err => {
        console.error('Clipboard copy failed:', err);
      });
    });
  });
}
