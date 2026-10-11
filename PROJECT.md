# Project: Gabriel Rul-lan Personal Website Redesign (vA, vB, vD)

## Architecture
The repository hosts a public static website via GitHub Pages from the `web/` directory using GitHub Actions (`.github/workflows/pages.yml`).
The site maintains the existing root website untouched while delivering three genuinely distinct alternative website versions in dedicated subdirectories:
- `web/vA/`: Enterprise Authority & Governance Strategist (English)
- `web/vB/`: Approachable Fractional Data Partner (English)
- `web/vD/`: Native Spanish "Authoritative Hybrid" for Mid-Size Enterprises (Spanish default with Catalan/English toggles)

### Core Architectural Invariants:
1. **Jekyll Static Isolation**: Files in `web/vA/`, `web/vB/`, and `web/vD/` omit YAML front matter (`---`), causing Jekyll's `actions/jekyll-build-pages@v1` to treat them as `Jekyll::StaticFile` and copy them verbatim without Liquid processing or template injection.
2. **Asset Encapsulation & Relative Paths**: All styling, scripts, fonts, logos, and images are strictly relative (`./` or `css/...`) and self-contained within each version's folder (`web/vA/css/`, `web/vB/css/`, `web/vD/css/`, etc.). No collisions with root `web/assets/`.
3. **Root Site Safety**: Root files (`web/index.html`, `en/`, `es/`, `ca/`, `_data/`, `_layouts/`, `assets/`, `CNAME`) remain functional and unmodified.
4. **Data Privacy**: Private career source files in `CV_gen/` and agent metadata in `.agents/` are strictly git-ignored and never committed or copied into `web/`.
5. **Strict No-Price Policy Across All Versions**: Strictly no price quotes, day rates, fees, retainers, salary benchmarks, or euro amounts on public pages across vA, vB, or vD. All CTAs drive to consultative dialogue via Google Calendar (`https://calendar.app.google/YbQTidmXT3Bg9wdY8`) and corporate email (`mailto:gabriel@data-partner.xyz`).
6. **Strict Location/Remote Removal Across All Versions (User Directive)**: Strictly remove all references to "100% remote", "remote-first", "Mallorca", "Barcelona on-site travel", "island base", or any travel/location constraints from copy in vA, vB, and vD. Focus strictly on capability, partnership, and business results.
7. **Cross-Industry with Life Sciences Highlight**: Positioned as cross-industry data strategist with dedicated life sciences and enterprise proof points (AstraZeneca, Boehringer Ingelheim, Mapfre).

---

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F01 | vA Visual Identity & Branding | Deep Navy (#0F172A), Slate Gray (#334155), Sovereign Gold (#B45309), Cormorant/Playfair serif + Inter typography, Monogram Crest logo & favicon | M1: Version A | ORIGINAL_REQUEST R1 |
| F02 | vA Enterprise Governance Wireframe | Strategic Hero, Governance Frameworks (DAMA-DMBOK), Proven Enterprise Impact metrics, Case Studies (AstraZeneca, Boehringer, Mapfre), Bio, Consultation CTA | M1: Version A | ORIGINAL_REQUEST R1, R2 |
| F03 | vA Self-Containment & Rationale | Fully relative asset linking, dedicated `web/vA/README.md` explaining enterprise audience, positioning, and design rationale | M1: Version A | ORIGINAL_REQUEST R1, R3 |
| F04 | vB Visual Identity & Branding | Warm Ivory (#FAF8F5), Forest Emerald (#0A5C36), Warm Coral (#F97316), Plus Jakarta Sans/Outfit typography, Collaborative Infinity / 'dp' logo & favicon | M2: Version B | ORIGINAL_REQUEST R1 |
| F05 | vB Fractional Partner Wireframe | Problem-Agitation-Solution Hero, How We Work, Fractional CDO Packages, Client Wins & Testimonials (Movinga/SMEs), Frictionless Booking CTA | M2: Version B | ORIGINAL_REQUEST R1, R2 |
| F06 | vB Self-Containment & Rationale | Fully relative asset linking, dedicated `web/vB/README.md` explaining SME audience, positioning, and design rationale | M2: Version B | ORIGINAL_REQUEST R1, R3 |
| F07 | vC Retirement | Version C removed from site, docs, and test suite per user directive (not a maker) | Phase 2 | ORIGINAL_REQUEST R1 |
| F14 | vD Visual Identity & Branding | Deep Navy (#0F172A), Forest Emerald (#0A5C36), Sovereign Amber (#D97706), Warm Ivory (#FAF8F5), Plus Jakarta Sans typography, Hexagonal Diamond logo & favicons | M1 (vD) | Strategic Directive |
| F15 | vD Information Architecture | Native executive Spanish copy, 4 problem agitation cards, 3-tier consultative service packaging, enterprise cases (AstraZeneca, Boehringer, Mapfre, Movinga), FAQ, CTA | M1 (vD) | Strategic Directive |
| F16 | vD Language Navigation Toggles | Spanish default with Català (`#contacto`) and English (`../vA/`) toggles using strict relative linking | M1 (vD) | Strategic Directive |
| F24 | vA & vB Alignment | Removed all location/remote mentions across vA and vB; removed pricing quotes, salary benchmarks, and #calculator from vB HTML and JS | M2 (Alignment) | User Directive 2026-10-11 |
| F22 | Test Suite Extension & Verification | Extended test harness across vA, vB, and vD: 8 fact tests, 3 pairwise distinctness tests, 7 HTML standards tests, 9 headless responsive tests (27/27 passing) | M2 (Alignment) | User Directive 2026-10-11 |
| F23 | Deployment & Live Validation | Commit and push to `origin main`, GitHub Pages build, live verification of HTTP 200 on `/`, `/vA/`, `/vB/`, `/vD/` | M3 (Deployment) | Strategic Directive |

---

## Interface Contracts & Shared Standards
### Common Requirements Across All Versions:
- **Language**: English for vA and vB; Spanish primary with Catalan and English navigation options for vD.
- **Booking Link**: `https://calendar.app.google/YbQTidmXT3Bg9wdY8`
- **Email**: Valid mailto: link to `gabriel@data-partner.xyz`.
- **Location & Modality**: Strictly neutral across all versions (all Mallorca, remote-first, and travel constraint claims removed per user directive).
- **Credentials**:
  - Degree in Mathematics (Universitat de les Illes Balears - UIB).
  - Executive MBA (ESERP / Universitat Politècnica de Catalunya).
  - Project Management Professional (PMP® - PMI).
  - Data Governance practitioner (DAMA-DMBOK).
- **No Day Rate / No Prices**: Day rates, fees, retainers, and price benchmarks strictly prohibited across all versions.
- **Single `<h1>`**: Every page has exactly one `<h1>`.
- **SEO & Social**: Unique `<title>`, `<meta name="description">`, Open Graph tags (`og:title`, `og:description`, `og:image`, `og:url`).
- **Assets**: All asset references must be relative (`href="./css/..."` or `href="css/..."`, `src="img/..."`). No root-leading slashes (`/assets/...`).
- **Transfer Budget**: Under 3 MB total uncompressed weight per page.

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
├── vA/                        # Enterprise Authority (English)
│   ├── index.html
│   ├── README.md
│   ├── favicon.ico / .png
│   ├── css/
│   │   └── style.css
│   └── img/
│       ├── logo.svg
│       └── ...
│
├── vB/                        # Fractional Data Partner (English)
│   ├── index.html
│   ├── README.md
│   ├── favicon.ico / .png
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
│       ├── logo.svg
│       └── ...
│
├── vD/                        # Authoritative Hybrid (Spanish, Catalan/English toggles)
│   ├── index.html
│   ├── README.md
│   ├── favicon.ico / .png
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── img/
│       ├── logo.svg
│       └── ...
│
└── VERSIONS.md                # Summary guide explaining versions & promotion to root
```
