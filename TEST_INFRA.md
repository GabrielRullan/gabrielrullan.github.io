# Test Infrastructure & Verification Architecture

## Overview
This document specifies the automated E2E test harness, quality assurance standards, and verification methodologies for the Gabriel Rul-lan Personal Website Redesign project (`web/vA`, `web/vB`).

The test suite is written in Python (Python 3.10+ / standard library `unittest` + BeautifulSoup4 + WebSocket CDP) and resides entirely under `tests/`. It provides 100% automated, non-interactive verification across all project requirements.

---

## Directory Layout
```
tests/
├── __init__.py
├── test_facts.py                 # Ground-truth fact verification & rate prohibition
├── test_distinctness.py          # 5-dimension pairwise distinctness rubric
├── test_html_standards.py        # Single H1, SEO/OG, accessibility, links, budget
├── test_headless_responsive.py   # Headless Chrome/Edge rendering, scroll & runtime audit
├── run_all_tests.py              # Master test runner and JSON summary reporter
├── screenshots/                  # Viewport captures (375px, 768px, 1440px per version)
└── test_results.json             # Structured machine-readable test execution report
```

---

## Test Suites & Methodologies

### 1. `tests/test_facts.py` (Fact Integrity & Rate Prohibition)
- **Objective**: Ensure absolute truthfulness and fidelity to Gabriel Rul-lan's career dossier (`CV_gen/`) and enforce the strict prohibition of day rates.
- **Verification Criteria**:
  1. **Canonical Booking Link**: Verifies exact link `https://calendar.app.google/YbQTidmXT3Bg9wdY8` is present in all versions.
  2. **Verified Contact Email**: Verifies `mailto:gabriel@data-partner.xyz` exists and is properly formatted in all versions.
  3. **Location & Work Mode**: Verifies Mallorca, Spain, and remote-first engagement are accurately stated.
  4. **Strict Rate Prohibition**: Scans text and source code using regex patterns (`\b\d+\s*€\s*/\s*day\b`, `\bday\s*rate\b`, `\btarifa\s*diaria\b`, `target_rate`, etc.) to guarantee no day rate is displayed on any page.
  5. **Verified Credentials**: Confirms BS in Mathematics (UIB), Executive MBA (ESERP / UPC), and PMP® certification from PMI are present.
  6. **Enterprise Client Verification**: Checks citations of real clients from `CV_gen` (AstraZeneca, Boehringer Ingelheim, Movinga, Mapfre).
  7. **Zero Unmapped Claims**: Scans for hallucinated employers or exaggerated metrics not substantiated in `CV_gen/`.

### 2. `tests/test_distinctness.py` (5-Dimension Pairwise Rubric)
- **Objective**: Guarantee that vA vs vB constitutes fundamentally distinct positioning and user experience (requiring at least 4 out of 5 distinct dimensions, targeting 5/5).
- **The 5 Dimensions**:
  1. **Palette**: Computes color set overlap (Jaccard dissimilarity) and background tone differentiation (Warm Ivory vs Deep Navy).
  2. **Typography**: Verifies heading and body font family independence (Serif / Inter vs Plus Jakarta Sans).
  3. **Layout Structure**: Inspects DOM section taxonomy, hero hierarchy, card grids, and navigation paradigms.
  4. **Headline Tone**: Analyzes H1, H2, and hero copy using semantic term profiles (Enterprise Authority vs Fractional Partner).
  5. **Logo & Favicon Concept**: Inspects vector SVG geometry, primitive paths, and conceptual branding (Monogram Crest vs Collaborative Infinity/DP).

### 3. `tests/test_html_standards.py` (HTML Standards & Performance Budget)
- **Objective**: Validate semantic HTML5, SEO compliance, accessibility, link integrity, and transfer budget.
- **Verification Criteria**:
  1. **Single H1**: Exactly one `<h1>` per version home page.
  2. **SEO Metadata**: Descriptive `<title>` (>=10 chars) and `<meta name="description">` (>=20 chars).
  3. **Open Graph Protocol**: Valid `og:title`, `og:description`, and `og:image` tags.
  4. **Accessibility (Alt Text)**: Every `<img>` tag contains an `alt` attribute; non-decorative images contain descriptive text.
  5. **Strict Relative Linking**: Prohibits root-leading slashes (`/assets/...`, `/css/...`); ensures pages are fully portable and isolated under `/vA/`, `/vB/`.
  6. **Internal Link Crawling**: Crawls all `<a href>`, `<link href>`, `<script src>`, and `<img src>` to ensure zero 404s, missing files, or broken anchor `#ids`.
  7. **Page Weight Budget**: Asserts total transfer size of HTML and all local assets is strictly under 3 MB.

### 4. `tests/test_headless_responsive.py` (Headless Browser & Runtime Audit)
- **Objective**: Render both versions in a real headless browser engine (Google Chrome or Edge) across mobile (375px), tablet (768px), and desktop (1440px) viewports.
- **Verification Criteria**:
  1. **Local Server Integration**: Automatically spawns and tears down a local HTTP server (`http://127.0.0.1:8000/`) serving `web/`.
  2. **Chrome DevTools Protocol (CDP)**: Connects directly via WebSocket to monitor browser events in real-time.
  3. **Zero Horizontal Overflow**: Evaluates `document.documentElement.scrollWidth <= window.innerWidth` (with 1px rounding tolerance).
  4. **Zero Console Errors**: Listens to `Runtime.consoleAPICalled` and `Log.entryAdded` for runtime errors.
  5. **Zero Network 404s**: Listens to `Network.responseReceived` and `Network.loadingFailed` for broken assets.
  6. **Image Load Verification**: Verifies `complete === true && naturalWidth > 0` for all rendered images.
  7. **Reference Screenshots**: Captures PNG screenshots of each viewport into `tests/screenshots/` for visual review.

---

## Running the Tests

### Master Runner (All Suites)
To execute all test suites sequentially with formatted console output and JSON export:
```bash
python tests/run_all_tests.py
```

### Running Individual Test Suites
```bash
# Fact Integrity & Rate Prohibition
python tests/test_facts.py

# 5-Dimension Pairwise Distinctness
python tests/test_distinctness.py

# HTML Standards, SEO, Links & Performance Budget
python tests/test_html_standards.py

# Headless Responsive Rendering & Runtime Audit
python tests/test_headless_responsive.py
```

### Standard Python Unittest Discovery
```bash
python -m unittest discover tests
```

---

## Output & Attestation
- **Screenshots**: Saved to `tests/screenshots/{vA|vB}_{375|768|1440}.png`.
- **JSON Report**: Saved to `tests/test_results.json` containing complete metrics and failure traces (if any).
