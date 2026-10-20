"""
tests/test_facts.py - Fact-checking & requirements verification suite for live localized pages (/, /es/, /en/, /ca/).

Verifies:
1. Site structure: Spanish default at /, localized /es/, /en/, /ca/, legacy version at /old/, and vA-vF + brand removed from web/.
2. Propuesta 2 branding & Opción B positioning across ES, EN, and CA on the vF framework.
3. Real photos of Gabriel used in web/img/ and brand/assets/.
4. Single checkmarks (zero redundant SVG checkmarks inside .tier-features li) in #servicios.
5. Contact information: booking URL, contact email, zero location/remote claims.
6. Core credentials (UIB Mathematics, Executive MBA ESERP, PMP® PMI) and clients (AstraZeneca, Boehringer Ingelheim, Movinga, Mapfre).
7. Strict prohibition of day rates or prices across all pages.
"""

import re
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"
ARCHIVE_DIR = REPO_ROOT / "archive"
BRAND_DIR = REPO_ROOT / "brand"

PAGES = ["", "es", "en", "ca"]

EXPECTED_BOOKING_URL = "https://calendar.app.google/YbQTidmXT3Bg9wdY8"
EXPECTED_EMAIL = "gabriel@data-partner.xyz"

DAY_RATE_PATTERNS = [
    re.compile(r"\b\d+\s*€\s*/\s*(day|día|dia|tag)\b", re.IGNORECASE),
    re.compile(r"\b(day|daily)\s*rate\b", re.IGNORECASE),
    re.compile(r"\btarifa\s*diaria\b", re.IGNORECASE),
    re.compile(r"€\s*\d+\s*/\s*d\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*€\s*per\s*day\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*eur\s*/\s*day\b", re.IGNORECASE),
    re.compile(r"\b(target_rate|rate)\s*[:=]\s*[\"']?\d+\s*€", re.IGNORECASE),
    re.compile(r"\b450\s*€\b", re.IGNORECASE),
    re.compile(r"€\s*\d+", re.IGNORECASE),
    re.compile(r"\b\d+\s*€", re.IGNORECASE),
]


def get_page_path(page: str) -> Path:
    return (WEB_DIR / "index.html") if page == "" else (WEB_DIR / page / "index.html")


def get_page_html(page: str) -> str:
    path = get_page_path(page)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def extract_visible_text(html: str) -> str:
    if not html:
        return ""
    soup = BeautifulSoup(html, "html.parser")
    for s in soup(["script", "style", "noscript"]):
        s.decompose()
    return soup.get_text(separator=" ", strip=True)


class TestFactIntegrity(unittest.TestCase):
    """Test suite verifying factual accuracy, localization, branding, and structural requirements."""

    def test_site_structure_and_stopped_serving_other_options(self):
        """Verify /, /es/, /en/, /ca/, and /old/ exist in web/, while vA-vF and brand are stored outside web/."""
        for p in PAGES:
            path = get_page_path(p)
            self.assertTrue(path.is_file(), f"Missing localized page at {path}")

        self.assertTrue((WEB_DIR / "old" / "index.html").is_file(), "Previous version must be stored in web/old/index.html")

        for removed in ["vA", "vB", "vC", "vD", "vE", "vF", "brand"]:
            self.assertFalse(
                (WEB_DIR / removed).exists(),
                f"Directory web/{removed} must NOT be served in web/ (must be stored outside web/)",
            )

        for archived in ["vA", "vB", "vD", "vE", "vF"]:
            self.assertTrue((ARCHIVE_DIR / archived / "index.html").is_file(), f"Archived {archived} missing in archive/")
        self.assertTrue((BRAND_DIR / "index.html").is_file(), "Brand kit missing in brand/index.html")

    def test_default_spanish_and_localized_languages_and_opcion_b(self):
        """Verify Spanish is served by default at / and /es/, English at /en/, Catalan at /ca/, with Opción B."""
        expected_langs = {
            "": (
                "es",
                "Data Partner · Estrategia, Analítica y Automatización",
                "Data Partner Continuo (Estrategia, Analítica y Automatización)",
            ),
            "es": (
                "es",
                "Data Partner · Estrategia, Analítica y Automatización",
                "Data Partner Continuo (Estrategia, Analítica y Automatización)",
            ),
            "en": (
                "en",
                "Data Partner · Data Strategy, Analytics & Automation",
                "Ongoing Data Partner (Strategy, Analytics & Automation)",
            ),
            "ca": (
                "ca",
                "Data Partner · Estratègia, Analítica i Automatització",
                "Data Partner Continu (Estratègia, Analítica i Automatització)",
            ),
        }
        for page, (exp_lang, exp_pill, exp_card) in expected_langs.items():
            html = get_page_html(page)
            soup = BeautifulSoup(html, "html.parser")
            html_tag = soup.find("html")
            self.assertIsNotNone(html_tag)
            self.assertEqual(html_tag.get("lang"), exp_lang, f"Page '{page or '/'}' must have lang='{exp_lang}'")
            text = extract_visible_text(html)
            self.assertIn(exp_pill, text, f"Page '{page or '/'}' missing Opción B pill '{exp_pill}'")
            self.assertIn(exp_card, text, f"Page '{page or '/'}' missing Opción B service card '{exp_card}'")
            self.assertNotIn("fraccional", text.lower(), f"Page '{page or '/'}' still contains 'fraccional'")
            self.assertNotIn("fractional", text.lower(), f"Page '{page or '/'}' still contains 'fractional'")

    def test_propuesta_2_branding_applied(self):
        """Verify Propuesta 2 palette and typography are applied in web/css/style.css."""
        css = (WEB_DIR / "css" / "style.css").read_text(encoding="utf-8")
        for color in ["#0A5C36", "#15803D", "#EA580C", "#FAF8F5", "#1F2937"]:
            self.assertIn(color, css, f"Propuesta 2 color {color} missing from web/css/style.css")
        for font in ["Plus Jakarta Sans", "DM Sans", "Fira Code"]:
            self.assertIn(font, css, f"Propuesta 2 font {font} missing from web/css/style.css")

    def test_real_photos_used_and_single_checkmarks_in_services(self):
        """Verify real photos of Gabriel are used and #servicios has zero duplicate SVG checkmarks in .tier-features li."""
        real_1 = (WEB_DIR / "old" / "assets" / "img" / "profile-img.jpg").read_bytes()
        real_2 = (WEB_DIR / "old" / "assets" / "img" / "profile-img_2.jpg").read_bytes()
        self.assertEqual((WEB_DIR / "img" / "gabriel.jpg").read_bytes(), real_1, "web/img/gabriel.jpg must match real photo")
        self.assertEqual(
            (WEB_DIR / "img" / "gabriel-partner.jpg").read_bytes(),
            real_2,
            "web/img/gabriel-partner.jpg must match real second photo",
        )
        self.assertEqual(
            (BRAND_DIR / "assets" / "img" / "gabriel.jpg").read_bytes(),
            real_1,
            "brand/assets/img/gabriel.jpg must match real photo",
        )

        for p in PAGES:
            soup = BeautifulSoup(get_page_html(p), "html.parser")
            imgs = [img.get("src", "") for img in soup.find_all("img")]
            self.assertTrue(any("gabriel.jpg" in s for s in imgs), f"Page '{p or '/'}' missing gabriel.jpg")
            self.assertTrue(any("gabriel-partner.jpg" in s for s in imgs), f"Page '{p or '/'}' missing gabriel-partner.jpg")

            # Verify single checkmarks in #servicios (.tier-features li must NOT contain inline <svg>)
            tier_lis = soup.select("#servicios .tier-features li")
            self.assertEqual(len(tier_lis), 15, f"Page '{p or '/'}' should have 15 tier feature items")
            for li in tier_lis:
                self.assertIsNone(
                    li.find("svg"),
                    f"Page '{p or '/'}' has redundant <svg> checkmark inside .tier-features li!",
                )

    def test_booking_link_present_and_exact(self):
        """Verify the exact Google Calendar booking link is present in every page."""
        for p in PAGES:
            soup = BeautifulSoup(get_page_html(p), "html.parser")
            booking_anchors = soup.find_all("a", href=lambda h: h and EXPECTED_BOOKING_URL in h)
            self.assertGreater(len(booking_anchors), 0, f"Page '{p or '/'}' missing booking link")
            for a in booking_anchors:
                self.assertEqual(a["href"].strip(), EXPECTED_BOOKING_URL)

    def test_contact_email_present_and_valid(self):
        """Verify valid mailto link with gabriel@data-partner.xyz in every page."""
        for p in PAGES:
            soup = BeautifulSoup(get_page_html(p), "html.parser")
            email_anchors = soup.find_all(
                "a", href=lambda h: h and h.lower().startswith("mailto:") and EXPECTED_EMAIL in h.lower()
            )
            self.assertGreater(len(email_anchors), 0, f"Page '{p or '/'}' missing contact email")

    def test_location_mentions(self):
        """Verify location/remote mentions are absent across all pages."""
        prohibited_terms = ["mallorca", "remote-first", "100% remote", "island base", "barcelona on-site"]
        for p in PAGES:
            text = extract_visible_text(get_page_html(p)).lower()
            for term in prohibited_terms:
                self.assertNotIn(term, text, f"Page '{p or '/'}' must not mention '{term}'")

    def test_no_day_rate_displayed(self):
        """CRITICAL: Strict requirement that NO day rate is present on any page."""
        for p in PAGES:
            html = get_page_html(p)
            for pattern in DAY_RATE_PATTERNS:
                matches = pattern.findall(html)
                self.assertEqual(len(matches), 0, f"Page '{p or '/'}' violates rate prohibition: {matches}")

    def test_verified_credentials_and_clients(self):
        """Verify real credentials (UIB Math, MBA, PMP) and clients appear in each localized page."""
        for p in PAGES:
            text = extract_visible_text(get_page_html(p)).lower()
            has_math = any(m in text for m in ["mathematics", "matemáticas", "matemàtiques"])
            self.assertTrue(has_math, f"Page '{p or '/'}' missing Mathematics mention")
            self.assertIn("pmp", text, f"Page '{p or '/'}' missing PMP mention")
            self.assertIn("mba", text, f"Page '{p or '/'}' missing MBA mention")
            for client in ["astrazeneca", "boehringer", "movinga", "mapfre"]:
                self.assertIn(client, text, f"Page '{p or '/'}' missing client '{client}'")

    def test_no_unmapped_fictional_claims(self):
        """Flag any unmapped client or corporate claims not present in CV_gen."""
        hallucination_indicators = [
            "google lead", "amazon director", "meta cdo", "mckinsey partner",
            "microsoft vp", "apple architect", "harvard phd", "stanford mba",
            "20+ years", "30+ years", "100m revenue", "$100m",
            "99.8%", "5 eu countries", "5 países de la ue", "multi-million", "multimillonari",
            "pmi-id", "pmi id", "pmi #"
        ]
        for p in PAGES:
            text = extract_visible_text(get_page_html(p)).lower()
            for bad_claim in hallucination_indicators:
                self.assertNotIn(bad_claim, text, f"Page '{p or '/'}' contains unmapped claim: '{bad_claim}'")

    def test_old_site_hero_grammar_and_link_integrity(self):
        """Verify /old/ hero typed sentence is grammatically ordered and zero broken local links exist across web/, brand/, and archive/."""
        for old_es in [WEB_DIR / "old" / "index.html", WEB_DIR / "old" / "es" / "index.html"]:
            content = old_es.read_text(encoding="utf-8")
            self.assertNotIn("Soy un  de Datos", content, f"{old_es} has garbled hero sentence")
            self.assertIn('Soy un <span class="typed"', content)
            self.assertIn('></span> de Datos</p>', content)

        old_ca = (WEB_DIR / "old" / "ca" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("Sóc  de Dades", old_ca, "web/old/ca/index.html has garbled hero sentence")
        self.assertIn('Sóc <span class="typed"', old_ca)
        self.assertIn('></span> de Dades</p>', old_ca)

        for folder in [WEB_DIR, BRAND_DIR, ARCHIVE_DIR]:
            for html_file in folder.rglob("*.html"):
                if "legacy_jekyll" in str(html_file):
                    continue
                soup = BeautifulSoup(html_file.read_text(encoding="utf-8", errors="ignore"), "html.parser")
                for tag, attr in [("a", "href"), ("link", "href"), ("script", "src"), ("img", "src")]:
                    for el in soup.find_all(tag):
                        val = el.get(attr, "").strip()
                        if not val or val.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:", "javascript:")):
                            continue
                        clean = val.split("#")[0].split("?")[0]
                        if not clean:
                            continue
                        target = (html_file.parent / clean).resolve()
                        self.assertTrue(
                            target.exists(),
                            f"Broken local link in {html_file.relative_to(REPO_ROOT)}: <{tag} {attr}='{val}'> -> {target}",
                        )


if __name__ == "__main__":
    unittest.main()
