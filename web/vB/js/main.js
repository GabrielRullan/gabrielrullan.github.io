/**
 * Version B: Approachable Fractional Data Partner
 * Interactive Scripts: Navigation, FAQ Accordion, ROI Calculator
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Sticky Header scroll effect
  const header = document.querySelector('.header');
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

  // 2. Mobile Menu Toggle
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');

  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      const isExpanded = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', !isExpanded);
      navMenu.classList.toggle('open');
    });

    // Close menu when clicking nav links
    const navLinks = navMenu.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        mobileToggle.setAttribute('aria-expanded', 'false');
        navMenu.classList.remove('open');
      });
    });
  }

  // 3. Interactive FAQ Accordion
  const faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (questionBtn) {
      questionBtn.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        
        // Close other items for a clean accordion effect
        faqItems.forEach(otherItem => {
          if (otherItem !== item) {
            otherItem.classList.remove('active');
            const otherBtn = otherItem.querySelector('.faq-question');
            if (otherBtn) otherBtn.setAttribute('aria-expanded', 'false');
          }
        });

        // Toggle current item
        if (isActive) {
          item.classList.remove('active');
          questionBtn.setAttribute('aria-expanded', 'false');
        } else {
          item.classList.add('active');
          questionBtn.setAttribute('aria-expanded', 'true');
        }
      });
    }
  });

  // 4. Interactive Fractional vs Full-Time Savings Calculator
  const stageSelect = document.getElementById('company-stage-select');
  const savingsDisplay = document.getElementById('calc-savings-display');
  const fulltimeDisplay = document.getElementById('calc-fulltime-cost');
  const fractionalDisplay = document.getElementById('calc-fractional-cost');
  const timelineDisplay = document.getElementById('calc-timeline-display');

  const stageData = {
    seed: {
      fullTime: '€180,000 / yr',
      fractional: 'Flexible Sprint / Part-time',
      savings: '€110,000+',
      timeline: 'First Single Source of Truth in 14 Days'
    },
    growth: {
      fullTime: '€240,000 / yr',
      fractional: 'On-Demand Fractional CDO',
      savings: '€150,000+',
      timeline: 'Audited Stack & Automated Dashboards in 4 Weeks'
    },
    scaleup: {
      fullTime: '€320,000+ / yr',
      fractional: 'Strategic Fractional Partnership',
      savings: '€200,000+',
      timeline: 'Cross-system MDM & Governance in 6 Weeks'
    }
  };

  if (stageSelect && savingsDisplay && fulltimeDisplay && fractionalDisplay && timelineDisplay) {
    const updateCalculator = () => {
      const selected = stageSelect.value;
      const data = stageData[selected] || stageData.growth;
      
      savingsDisplay.textContent = data.savings;
      fulltimeDisplay.textContent = data.fullTime;
      fractionalDisplay.textContent = data.fractional;
      timelineDisplay.textContent = data.timeline;
    };

    stageSelect.addEventListener('change', updateCalculator);
    updateCalculator();
  }

  // 5. Accessible Smooth Scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
        targetElement.setAttribute('tabindex', '-1');
        targetElement.focus({ preventScroll: true });
      }
    });
  });
});
