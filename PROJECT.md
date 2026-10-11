# Project: Gabriel Rul-lan Personal Website Redesign (vA, vB)

## Architecture
The repository hosts a public static website via GitHub Pages from the `web/` directory using GitHub Actions (`.github/workflows/pages.yml`).
The site maintains the existing root website untouched while delivering two genuinely distinct alternative website versions in dedicated subdirectories:
- `web/vA/`: Enterprise Authority & Governance Strategist
- `web/vB/`: Approachable Fractional Data Partner

### Core Architectural Invariants:
1. **Jekyll Static Isolation**: Files in `web/vA/`, `web/vB/` omit YAML front matter (`---`), causing Jekyll's `actions/jekyll-build-pages@v1` to treat them as `Jekyll::StaticFile` and copy them verbatim without Liquid processing or template injection.
2. **Asset Encapsulation**: All styling, scripts, fonts, logos, and images are strictly relative (`./` or `css/...`) and self-contained within each version's folder (`web/vA/css/`, `web/vB/css/`, etc.). No collisions with root `web/assets/`.
3. **Root Site Safety**: Root files (`web/index.html`, `en/`, `es/`, `ca/`, `_data/`, `_layouts/`, `assets/`, `CNAME`) remain functional and unmodified.
4. **Data Privacy**: Private career source files in `CV_gen/` and agent metadata in `.agents/` are strictly git-ignored and never committed or copied into `web/`.
5. **Deployment Target**: Remote GitHub Pages build type toggled to `workflow` via GitHub CLI, deploying to `https://www.data-partner.xyz/` with `/vA/`, `/vB/`.

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F01 | vA Visual Identity & Branding | Deep Navy (#0F172A), Slate Gray (#334155), Sovereign Gold (#B45309), Cormorant/Playfair serif + Inter typography, Monogram Crest logo & favicon | M1: Version A | ORIGINAL_REQUEST R1 |
| F02 | vA Enterprise Governance Wireframe | Strategic Hero, Governance Frameworks (DAMA-DMBOK), Proven Enterprise Impact metrics, Case Studies (AstraZeneca, Boehringer, Mapfre), Bio, Consultation CTA | M1: Version A | ORIGINAL_REQUEST R1, R2 |
| F03 | vA Self-Containment & Rationale | Fully relative asset linking, dedicated `web/vA/README.md` explaining enterprise audience, positioning, and design rationale | M1: Version A | ORIGINAL_REQUEST R1, R3 |
| F04 | vB Visual Identity & Branding | Warm Ivory (#FAF8F5), Forest Emerald (#0A5C36), Warm Coral (#F97316), Plus Jakarta Sans/Outfit typography, Collaborative Infinity / 'dp' logo & favicon | M2: Version B | ORIGINAL_REQUEST R1 |
| F05 | vB Fractional Partner Wireframe | Problem-Agitation-Solution Hero, How We Work, Fractional CDO Packages/Tiers, Client Wins & Testimonials (Movinga/SMEs), Frictionless Booking CTA | M2: Version B | ORIGINAL_REQUEST R1, R2 |
| F06 | vB Self-Containment & Rationale | Fully relative asset linking, dedicated `web/vB/README.md` explaining SME audience, positioning, and design rationale | M2: Version B | ORIGINAL_REQUEST R1, R3 |
| F07 | vC Retirement | Version C removed from site, docs, and test suite per user directive (not a maker) | M1 (Phase 2) | ORIGINAL_REQUEST R1 |
| F10 | Career Facts & Content Integrity | Strictly authentic facts from `CV_gen` (UIB Math, MBA, PMP, real roles/metrics), valid email, active booking calendar link, NO day rate displayed | M4: Testing Track | ORIGINAL_REQUEST R2 |
| F11 | 5-Dimension Pairwise Distinctness | Independent verification that vA vs vB differs across >= 4/5 dimensions (palette, typography, layout, tone, logo) | M4: Testing Track | ORIGINAL_REQUEST AC |
| F12 | Headless Responsive & Quality Audit | Local headless Chrome/Edge test suite at 375, 768, 1440 px: zero horizontal scroll, zero console errors, zero 404s, link crawl, SEO/meta tags, Lighthouse thresholds | M4: Testing Track | ORIGINAL_REQUEST R3, AC |
| F13 | Git Integration & Live Deployment | Add `.agents/` to `.gitignore`, switch Pages API to `workflow`, push to `origin main`, verify HTTP 200 on `https://www.data-partner.xyz/vA/`, `/vB/`, root site index guide | M5: Deployment | ORIGINAL_REQUEST R4, AC |

---

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Version A: Enterprise Authority | Create `web/vA/` complete static implementation, CSS, logo, favicon, images, README | none | DONE |
| M2 | Version B: Fractional Data Partner | Create `web/vB/` complete static implementation, CSS, logo, favicon, images, README | none | DONE |
| M3 | Version C: Systems Builder & Maker | Retired per user directive 2026-10-11 (not a maker) | none | RETIRED |
| M4 | E2E Testing & Quality Verification | Fact-check pass against `CV_gen/`, 5-dimension distinctness evaluation, headless responsive & link crawl suite, Lighthouse audit | M1, M2 | DONE |
| M5 | Final Deployment & Online Verification | GitHub Pages API workflow switch, git commit & push to `main`, live HTTP 200 verification, version promotion guide | M4 | DONE |

---

## Interface Contracts & Shared Standards
### Common Requirements Across All Versions:
- **Language**: English only.
- **Booking Link**: `https://calendar.app.google/YbQTidmXT3Bg9wdY8`
- **Email**: Valid mailto: link to Gabriel Rul-lan's professional contact (`gabriel@data-partner.xyz` or verified email from CV).
- **Location**: Mallorca, Spain (Remote-first).
- **Credentials**:
  - Degree in Mathematics (Universitat de les Illes Balears - UIB).
  - Executive MBA (ESERP / Universitat Politècnica de Catalunya).
  - Project Management Professional (PMP® - PMI).
  - Data Governance practitioner (DAMA-DMBOK).
- **No Day Rate**: Day rate is strictly prohibited on all versions.
- **Single `<h1>`**: Every page has exactly one `<h1>`.
- **SEO & Social**: Unique `<title>`, `<meta name="description">`, Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`).
- **Assets**: All asset references must be relative (`href="./css/..."` or `href="css/..."`, `src="img/..."`). No root-leading slashes (`/assets/...`).

---

## Code Layout
```
web/
├── index.html                 # Existing root index (UNTOUCHED)
├── en/                        # Existing English root (UNTOUCHED)
├── es/                        # Existing Spanish root (UNTOUCHED)
├── ca/                        # Existing Catalan root (UNTOUCHED)
├── assets/                    # Existing root assets (UNTOUCHED)
├── _data/                     # Existing root data (UNTOUCHED)
├── _layouts/                  # Existing root layouts (UNTOUCHED)
├── CNAME                      # Existing custom domain (UNTOUCHED)
│
├── vA/                        # Milestone 1 (Enterprise Authority)
│   ├── index.html
│   ├── README.md              # Audience, positioning, and design rationale
│   ├── favicon.ico / .png
│   ├── css/
│   │   └── style.css
│   └── img/
│       ├── logo.svg
│       ├── hero-bg.jpg / svg
│       └── ...
│
├── vB/                        # Milestone 2 (Fractional Data Partner)
│   ├── index.html
│   ├── README.md              # Audience, positioning, and design rationale
│   ├── favicon.ico / .png
│   ├── css/
│   │   └── style.css
│   └── img/
│       ├── logo.svg
│       └── ...
│
└── VERSIONS.md                # Summary guide explaining versions & promotion to root
```
