# Gabriel Rul-lan — Website Redesign: Version Comparison & Promotion Guide

This repository hosts three fully developed, genuinely distinct directions for Gabriel Rul-lan's personal website. Each version presents Gabriel's authentic background (Mathematician from UIB, Executive MBA, PMP® certified, enterprise data governance and analytics leader) through a tailored visual identity, audience framing, and structural design.

All three versions are deployed side-by-side on GitHub Pages at:
- **Version A**: [https://www.data-partner.xyz/vA/](https://www.data-partner.xyz/vA/)
- **Version B**: [https://www.data-partner.xyz/vB/](https://www.data-partner.xyz/vB/)
- **Version C**: [https://www.data-partner.xyz/vC/](https://www.data-partner.xyz/vC/)
- **Current Root**: [https://www.data-partner.xyz/](https://www.data-partner.xyz/)

---

## 1. Executive Summary of the Three Versions

| Version | Positioning & Concept | Primary Target Audience | Core Value Proposition |
| :--- | :--- | :--- | :--- |
| **vA** | **Enterprise Authority & Governance Strategist** | Enterprise CDOs, CIOs, Heads of Data Governance, Pharma & Regulated Enterprises (AstraZeneca, Boehringer Ingelheim, Mapfre). | High-stakes data governance, master data management (MDM), DAMA-DMBOK alignment, and enterprise project governance. |
| **vB** | **Approachable Fractional Data Partner** | SME Founders, Seed to Series B CEOs, Scaleup Operators (e.g. Movinga, SaaS startups) needing CDO guidance without full-time overhead. | "Turn messy data into reliable revenue." Pragmatic 3-step modern data stack roadmaps, executive clarity, transparent fractional tiers. |
| **vC** | **Applied Mathematician & Systems Builder** | Technical CTOs, Engineering VPs, R&D Labs, Deep-Tech Founders, Hardware/IoT Teams. | First-principles engineering, mathematical optimization, hardware/embedded DIY builds (Arduino/ESP32), robust data architectures. |

---

## 2. Five-Dimension Pairwise Comparison Matrix

The three versions were developed to be unmistakably distinct across all 5 key design dimensions:

### 1. Color Palette
- **Version A (Institutional Enterprise)**:
  - Primary: Deep Navy (`#0F172A`)
  - Accent: Sovereign Gold (`#B45309`)
  - Supporting: Slate Gray (`#334155`), Pure White (`#FFFFFF`)
  - Mood: Prestigious, stable, boardroom-ready.
- **Version B (Warm Human Partner)**:
  - Primary: Forest Emerald (`#0A5C36`)
  - Accent: Warm Coral (`#F97316`)
  - Supporting: Warm Ivory (`#FAF8F5`), Charcoal (`#1E293B`)
  - Mood: Approachable, collaborative, vibrant, high-trust.
- **Version C (Terminal Cybernetic)**:
  - Primary: Void Obsidian (`#0B0F19`)
  - Accent: Neon Terminal Cyan (`#00F2FE`), Compiler Amber (`#F59E0B`)
  - Supporting: Terminal Slate (`#161B22`), Code Gray (`#30363D`)
  - Mood: Deep-tech, algorithmic, nighttime developer workstation.

### 2. Typography
- **Version A**:
  - Headings: *Playfair Display* / *Cormorant Garamond* (Editorial serif)
  - Body: *Inter* (Crisp executive sans-serif)
  - Character: Institutional governance advisory, management consulting report.
- **Version B**:
  - Headings: *Plus Jakarta Sans* / *Outfit* (Modern geometric sans-serif)
  - Body: *Plus Jakarta Sans* (High-legibility humanist sans)
  - Character: Friendly, modern tech product, transparent agency.
- **Version C**:
  - Headings: *Space Grotesk* (Clean technical sans)
  - Body & Accents: *JetBrains Mono* / *IBM Plex Mono* (Precision monospace)
  - Character: Compiler terminal, mathematical paper, hacker workbench.

### 3. Layout & Structure
- **Version A**:
  - Structure: Executive advisory flow.
  - Key Sections: Strategic Hero with trust metrics; DAMA-DMBOK Governance Pillars; Enterprise Case Studies (Pharma & Insurance); Career Credentials Grid; Formal Strategic Consultation Booking.
- **Version B**:
  - Structure: Problem-Agitation-Solution conversion funnel.
  - Key Sections: Pain Points ("Why Growing Companies Get Stuck With Data"); 3-Step Engagement Model (Audit, Stack, Handover); Fractional CDO Tiers; Interactive ROI & Cost Calculator; Verified Client Testimonials; FAQ Accordion; Discovery Call CTA.
- **Version C**:
  - Structure: First-principles engineering portfolio.
  - Key Sections: Mathematical Foundations Matrix (Graph Theory, Information Entropy, Stochastic Models); Hardware & Maker Lab (Rotary dial controller, ESP32 IoT); Interactive 4-Tab Performance Benchmarks Console; Architectural Deep Dives (dbt, SQL window partitioning, C++ ISR state machines); Production Tech Stack Matrix.

### 4. Tone of Voice
- **Version A**: Authoritative, strategic, compliance-focused, risk-mitigating.
- **Version B**: Empathetic, pragmatic, partner-oriented, business-ROI focused, jargon-free.
- **Version C**: Analytical, first-principles, builder-first, mathematically rigorous, code-level.

### 5. Logo & Visual Symbolism
- **Version A**: Geometric Monogram Crest ("GR") evoking an established advisory firm with classic serif typography.
- **Version B**: Continuous Infinity Loop / Interconnected Nodes ("dp") symbolizing ongoing partnership and clean data flow.
- **Version C**: Mathematical Sigma ($\Sigma$) / Circuit node glyph rendered in vector cyan with monospace brackets.

---

## 3. How to Promote Your Preferred Version to Root (`/`)

When you decide which version best fits your personal brand, follow these simple steps to make it the default root website (`https://www.data-partner.xyz/`):

### Option A: Complete Root Promotion (Recommended)

To promote version `vA`, `vB`, or `vC` as the permanent root homepage:

1. **Open PowerShell in the repository root**:
   ```powershell
   cd c:\Users\gabri\Documents\cv
   ```

2. **Select your preferred version** (e.g., set `$CHOICE = "vB"` for Version B, or `"vA"`, `"vC"`):
   ```powershell
   $CHOICE = "vB"  # Change to "vA", "vB", or "vC"
   ```

3. **Archive the legacy root files (Optional but safe)**:
   ```powershell
   New-Item -ItemType Directory -Force -Path "web/legacy_backup"
   Move-Item -Path "web/index.html" -Destination "web/legacy_backup/index.html" -Force
   ```

4. **Copy the selected version assets to the root `web/` directory**:
   ```powershell
   # Copy HTML, styles, scripts, images and favicons
   Copy-Item -Path "web/$CHOICE/index.html" -Destination "web/index.html" -Force
   Copy-Item -Path "web/$CHOICE/css" -Destination "web/css" -Recurse -Force
   Copy-Item -Path "web/$CHOICE/js" -Destination "web/js" -Recurse -Force
   Copy-Item -Path "web/$CHOICE/img" -Destination "web/img" -Recurse -Force
   Copy-Item -Path "web/$CHOICE/favicon.ico" -Destination "web/favicon.ico" -Force
   Copy-Item -Path "web/$CHOICE/favicon.png" -Destination "web/favicon.png" -Force
   ```

5. **Run the automated verification suite to verify link and file integrity**:
   ```powershell
   python tests/run_all_tests.py
   ```

6. **Commit and push to GitHub**:
   ```powershell
   git add web/
   git commit -m "feat: promote $CHOICE to root website"
   git push origin main
   ```
   GitHub Actions will automatically build and publish the changes to `https://www.data-partner.xyz/` in ~1-2 minutes.

---

### Option B: Quick Root Redirection

If you want to immediately redirect visitors from the root domain (`/`) to your preferred version without moving files:

1. Edit `web/index.html` and replace its `<head>` content with a standard HTML meta-refresh:
   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="utf-8">
     <meta http-equiv="refresh" content="0; url=/vB/">
     <link rel="canonical" href="https://www.data-partner.xyz/vB/">
     <title>Gabriel Rul-lan — Redirecting...</title>
     <script>window.location.replace('/vB/');</script>
   </head>
   <body>
     <p>Redirecting to <a href="/vB/">Gabriel Rul-lan</a>...</p>
   </body>
   </html>
   ```

2. Commit and push:
   ```powershell
   git add web/index.html
   git commit -m "feat: redirect root to /vB/"
   git push origin main
   ```

---

## 4. Verification & Testing

The website redesign includes a 27-test automated test suite covering:
- **Fact Integrity** (`tests/test_facts.py`): Validates contact info, education (UIB Math, MBA), PMP certification, verified clients (AstraZeneca, Boehringer Ingelheim, Movinga, Mapfre), and enforces zero disclosure of day rate.
- **5-Dimension Distinctness** (`tests/test_distinctness.py`): Programmatically evaluates pairwise distinctness across palette, typography, layout, tone, and branding.
- **HTML & Web Standards** (`tests/test_html_standards.py`): Single `<h1>` per page, valid meta descriptions, OG images, relative link isolation, and image alt text.
- **Headless Chrome Responsive Audit** (`tests/test_headless_responsive.py`): Audits rendering at 375px (mobile), 768px (tablet), and 1440px (desktop) with zero horizontal overflow, zero console errors, zero 404 network errors, and visual screenshot capture.

To run the complete test suite locally at any time:
```bash
python tests/run_all_tests.py
```
