# Version D: "Authoritative Hybrid" — Executive Rationale & Documentation

## 1. Overview & Vision
Version D (`web/vD/`) delivers an **"Authoritative Hybrid"** strategic landing page for Gabriel Rul-lan, purpose-built for medium-sized, high-revenue Spanish enterprises (€15M–€650M turnover) and family offices.

It bridges the strategic divide between Version A (Enterprise Authority) and Version B (Fractional Partner):
- **Institutional Gravitas (Inherited from vA):** Rigorous governance frameworks (DAMA-DMBOK, PMP®), deep biopharma/life sciences credentials (AstraZeneca, Boehringer Ingelheim, Mapfre), and academic pedigree (Licenciatura en Matemáticas UIB, Executive MBA ESERP).
- **Commercial & Actionable Clarity (Inherited from vB):** Problem agitation targeting real executive friction (ERP vs Excel, steering committee "guerra de cifras", month-end latency), clear 3-tier service packaging, and low-friction consultative booking.
- **Native Executive Spanish:** Formatted in natural, authoritative Spanish (*Español Corporativo Sobrio y Riguroso*) suited for the Comité de Dirección, Dirección General, CFO and CIO, with multilingual navigation toggles for Catalan and English.

---

## 2. Target Market & Buyer Persona
- **Market Segment:** Spanish middle-market corporations and family-owned enterprises (industrial, consumer goods, food & beverage, logistics, pharma).
- **Economic Scale:** Annual turnover between €15M and €650M; organizations that have invested heavily in ERPs (SAP, Microsoft Business Central, Navision) but still rely on fragmented spreadsheets for executive reporting.
- **Decision Makers (Buyers):**
  - **Director General / CEO:** Needs objective visibility across departments without vendor lock-in.
  - **CFO / Director Financiero:** Frustrated by reconciliation delays and discrepant revenue figures between Sales and Accounting.
  - **Consejo de Administración / Family Office:** Requires independent data governance oversight and accountability from external software vendors.
  - **CIO / Director de Sistemas:** Welcomes a senior PMP® ally to manage business stakeholder alignment and analytical delivery without expanding fixed internal payroll.

---

## 3. Visual Identity & Design System
- **Palette (Authoritative Hybrid Tokens):**
  - **Deep Midnight Navy (`#0e1726`):** Institutional foundation, stability, corporate authority.
  - **Forest Emerald (`#056a3e`, `#10b981`):** Actionable clarity, growth, trustworthy CTAs.
  - **Sovereign Amber (`#d97706`, `#b45309`, `#fbbf24`):** Academic rigor, PMP® credential accents, executive highlights.
  - **Warm Parchment / Ivory (`#fcfbf9`, `#f7f4ee`):** Human, warm executive canvas avoiding sterile corporate white.
- **Typography:**
  - **Headings:** *Plus Jakarta Sans* (geometric clarity with executive presence).
  - **Body:** *DM Sans* (humanist, highly legible for dense analytical and business reading).
- **Vector Logo (`web/vD/img/logo.svg`):**
  - Hexagonal Strategic Diamond Crest combining a faceted shield contour in Midnight Navy and Amber with an internal isometric emerald prism and convergence nodes, paired with tracked executive typography.

---

## 4. Service Architecture & Packaging
1. **Sprint de Diagnóstico y Auditoría de Datos (14 Días):** Forensic radiograph of data pipelines, identification of Critical Data Elements (CDEs), risk matrix, and prioritized quick-win roadmap.
2. **Director de Datos Fraccional (1–2 días/semana) [Destacado]:** Ongoing analytical leadership, single source of truth, steering committee representation, vendor accountability, and team enablement.
3. **Dirección de Programas de IT y Gobernanza (PMP®):** Formal project management for complex migrations (ERP, Cloud Data Warehouse) under PMI methodology and DAMA-DMBOK standards.

---

## 5. Strict Governance & Policy Compliance
1. **Confidential Pricing Policy:** Strictly zero prices, retainers, day rates, or fee figures on public pages. All CTAs drive to consultative dialogue via Google Calendar (`https://calendar.app.google/YbQTidmXT3Bg9wdY8`) and corporate email (`mailto:gabriel@data-partner.xyz`).
2. **Strict Location/Remote Removal (User Guidance 2026-10-11):** Strictly zero mentions of "100% remote", "remote-first", "Mallorca", "Barcelona on-site travel", "island base", or any travel/modality constraints. Focus remains entirely on capability, partnership, and results.
3. **Strict Factual Rigor:** 100% verified against `CV_gen/`. Zero ungrounded metrics (no "99.8%", no "5 EU countries", no fake PMI ID numbers, no "multi-million P&L").
4. **Strictly Relative URLs:** Zero root-leading slashes (`/`). All asset links relative (`css/style.css`, `img/logo.svg`, `favicon.ico`). Nav toggles link relatively (`../vA/` for English) to satisfy `test_html_standards.py`.
5. **Technical Quality:** Exactly 1 `<h1>`, complete SEO metadata, Open Graph preview, alt text on all images, zero horizontal overflow at 375px / 768px / 1440px, and zero console errors.
