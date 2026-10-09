# Version B: Approachable Fractional Data Partner

## 1. Positioning & Value Proposition
**Version B** positions Gabriel Rul-lan as an **Approachable Fractional Data Partner and On-Demand Chief Data Officer & Data Lead** targeted at high-growth SMEs, venture-backed startups (Seed to Series B), and mid-market scaleups (€1M–€30M ARR).

Unlike enterprise governance advisory firms that deliver heavy theoretical slide decks, or pure individual contractor engineers who lack commercial perspective, Version B positions Gabriel as an **embedded, collaborative partner**. He combines strategic C-suite data vision with hands-on pipeline engineering, delivering rapid commercial clarity without the €200k+ overhead and equity dilution of a full-time executive hire.

### Core Value Pillars:
- **Problem-Agitation-Solution Focus:** Directly addressing executive pain points—conflicting metrics in board meetings, fragile spreadsheet daisy-chains, and key-person risk.
- **Fast Time-to-Value:** Delivering an actionable architectural health scorecard and roadmap within 14 days; production pipelines and live dashboards within 3–4 weeks.
- **Pragmatic Modern Data Stack:** Deploying standard, modular cloud tools (dbt, BigQuery, Snowflake, Postgres, Python, SQL) directly into the client's infrastructure.
- **Complete Client Independence:** 100% code and infrastructure ownership handed over to the client's internal team with thorough documentation and zero vendor lock-in.

---

## 2. Target Audience
1. **Founders, CEOs & Managing Directors:** Leading high-growth companies who need reliable numbers for fundraising and operational scaling but cannot justify a full-time €200k+ CDO salary.
2. **CTOs & VP of Engineering:** Overburdened technical leaders seeking an experienced data partner to architect and deliver modern analytics without pulling backend engineers away from core product roadmaps.
3. **CFOs & Heads of Operations:** Leaders struggling with conflicting department reports, manual weekly reconciliation, and spreadsheet fragility who need automated, defensible financial and operational metrics.

---

## 3. Visual Identity & Design Rationale
- **Color Palette:**
  - **Warm Ivory (`#FAF8F5`):** Welcoming, human, approachable background that softens the sterile feel of corporate tech sites.
  - **Forest Emerald (`#0A5C36` primary, `#15803D`, `#ECFDF5` light):** Symbolizes sustainable growth, architectural stability, organic maturity, and financial health.
  - **Warm Coral (`#F97316` accent, `#EA580C`, `#FFF7ED` light):** Drives human warmth, collaborative energy, and high-converting, accessible calls-to-action.
  - **Text & Borders (`#1F2937` Dark Slate, `#374151` Body, `#E5E0D8` Warm Border):** Crisp contrast meeting WCAG AA/AAA standards.
- **Typography:**
  - **Headings:** *Plus Jakarta Sans* — Modern, friendly, geometric grotesk with humanist warmth that projects confidence without corporate stiffness.
  - **Body:** *DM Sans* — Clear, highly readable contemporary sans-serif engineered for effortless scanning across screens and data tables.
- **Brand Assets:**
  - **Vector Logo (`web/vB/img/logo.svg`):** An interconnected dual-loop infinity mark forming a subtle 'd' and 'p' (Data Partner), where the forest emerald data foundation seamlessly links with the warm coral human partnership node.
  - **Favicon (`web/vB/favicon.ico`, `web/vB/img/favicon.png`):** High-resolution circular icon encapsulating the emerald and coral partnership loop.
  - **Social Preview Card (`web/vB/img/og-image.png`):** High-fidelity 1200x630 Open Graph card with brand typography, value proposition, and key credentials.

---

## 4. Content Architecture & Verified Facts
All content is strictly factual and drawn from verified career records in `CV_gen` and `web/_data/en.yml`:
- **Engagement Model (3-Step Roadmap):**
  1. *Rapid Data Audit & Architecture Roadmap* (Days 1–14): Data source mapping, CDE taxonomy, health scorecard, and tool rationalization.
  2. *Scalable Modern Data Stack Deployment* (Weeks 2–4): Production ELT pipelines (dbt, SQL, Python), warehouse modeling, and automated quality testing.
  3. *Growth Dashboards & Self-Serve Analytics* (Steady-State): Executive KPI dashboards, self-serve semantic layers, and internal team upskilling.
- **Fractional Service Tiers (Strictly No Day Rate):**
  - *Data Strategy & Audit Sprint:* 2-week intensive diagnostic and roadmap.
  - *Fractional CDO & Data Lead:* Retained monthly embedded partnership (Featured tier).
  - *Data Governance & Quality Audit:* Targeted sprint for data cleaning, MDM, and compliance.
- **Interactive Cost Comparison Calculator:**
  - Dynamic selector for Seed, Growth, and Scaleup stages showing €110k–€200k+ annual savings versus full-time executive hires.
- **Real Client Case Studies:**
  - *Movinga:* Data platform turnaround, 99.8% pipeline reliability, and Master Data Management (MDM).
  - *Stealth AI SaaS:* 0-to-1 data roadmap, automated ingestion, and semantic models.
  - *Forensic Compliance & Analytics:* Cross-reconciling massive enterprise datasets and deploying 30+ executive dashboards.
- **Verified Testimonials (`web/_data/en.yml`):**
  - Arjun Katyal (Head of Internal Audits)
  - Ash (Founder)
  - Jacob Kratzsch (CEO & Founder)
  - Ayo Ayedefa (BI Head)
  - Xialu Zheng (Junior Data Scientist)
- **About Gabriel & Formal Credentials:**
  - BS in Mathematics – Universitat de les Illes Balears (UIB, 2013).
  - Executive MBA – ESERP Business School / UPC (2014).
  - Project Management Professional (PMP®) – PMI (#1974733).
  - DAMA-DMBOK Practitioner (Enterprise Data Governance & MDM).
  - Based in Mallorca, Spain (Remote-First worldwide).
- **Frictionless Booking & Contact:**
  - Direct Booking Link: `https://calendar.app.google/YbQTidmXT3Bg9wdY8`
  - Direct Email: `gabriel@data-partner.xyz`

---

## 5. Technical Implementation Details
- **Static Jekyll Isolation:** No YAML front matter (`---`) ensures Jekyll treats all files as verbatim static assets during GitHub Actions deployment (`actions/jekyll-build-pages@v1`).
- **Relative Asset Referencing:** All links, scripts, images, and fonts use strictly relative paths (`./css/style.css`, `./js/main.js`, `./img/...`), ensuring flawless local preview and `/vB/` subdirectory deployment.
- **Mobile Responsive Layout:** Verified at 375px (mobile), 768px (tablet), and 1440px (desktop) with zero horizontal overflow.
- **Interactive Client-Side Features (`web/vB/js/main.js`):**
  - Sticky glassmorphic navigation with scroll detection.
  - Accessible mobile hamburger navigation menu with ARIA state toggles.
  - Smooth-scrolling anchor links with keyboard focus management.
  - Interactive multi-item FAQ accordion with ARIA expansion tracking.
  - Dynamic stage-based savings and timeline calculator.
- **SEO & Social Metadata:** Exactly one `<h1>`, unique `<title>`, `<meta name="description">`, Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`), and semantic landmarks (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`).
