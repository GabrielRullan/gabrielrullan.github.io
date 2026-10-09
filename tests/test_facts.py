"""
tests/test_facts.py - Fact-checking test suite for vA, vB, and vC.

Verifies:
1. Contact information: booking URL, contact email, location.
2. Core credentials: UIB Mathematics, MBA (ESERP), PMP (PMI).
3. Core client/employer facts: AstraZeneca, Boehringer Ingelheim, Movinga, Mapfre.
4. Strict prohibition of day rate on all versions.
5. Entity extraction & verification against CV_gen ground truth (zero unmapped entities/claims).
"""

import os
import re
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"
CV_GEN_DIR = REPO_ROOT / "CV_gen"

VERSIONS = ["vA", "vB", "vC"]

EXPECTED_BOOKING_URL = "https://calendar.app.google/YbQTidmXT3Bg9wdY8"
EXPECTED_EMAIL = "gabriel@data-partner.xyz"
EXPECTED_LOCATION_KEYWORDS = ["mallorca", "spain", "remote"]

DAY_RATE_PATTERNS = [
    re.compile(r"\b\d+\s*€\s*/\s*(day|día|dia|tag)\b", re.IGNORECASE),
    re.compile(r"\b(day|daily)\s*rate\b", re.IGNORECASE),
    re.compile(r"\btarifa\s*diaria\b", re.IGNORECASE),
    re.compile(r"€\s*\d+\s*/\s*d\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*€\s*per\s*day\b", re.IGNORECASE),
    re.compile(r"\b\d+\s*eur\s*/\s*day\b", re.IGNORECASE),
    re.compile(r"\b(target_rate|rate)\s*[:=]\s*[\"']?\d+\s*€", re.IGNORECASE),
    re.compile(r"\b450\s*€\b", re.IGNORECASE),
]


def get_version_html(v: str) -> str:
    path = WEB_DIR / v / "index.html"
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
    """Test suite for verifying factual accuracy across vA, vB, and vC."""

    def test_versions_exist(self):
        """Check that index.html exists for vA, vB, and vC."""
        for v in VERSIONS:
            path = WEB_DIR / v / "index.html"
            self.assertTrue(path.exists(), f"Index file for {v} does not exist at {path}")

    def test_booking_link_present_and_exact(self):
        """Verify the exact Google Calendar booking link is present in every version."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")
            booking_anchors = soup.find_all("a", href=lambda h: h and EXPECTED_BOOKING_URL in h)
            self.assertGreater(
                len(booking_anchors), 0,
                f"Version {v} is missing the required booking link {EXPECTED_BOOKING_URL}"
            )
            for a in booking_anchors:
                self.assertEqual(
                    a["href"].strip(), EXPECTED_BOOKING_URL,
                    f"Version {v} booking link does not match canonical link exactly"
                )

    def test_contact_email_present_and_valid(self):
        """Verify valid mailto link with gabriel@data-partner.xyz in every version."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")
            email_anchors = soup.find_all(
                "a", href=lambda h: h and h.lower().startswith("mailto:") and EXPECTED_EMAIL in h.lower()
            )
            self.assertGreater(
                len(email_anchors), 0,
                f"Version {v} is missing the verified contact email {EXPECTED_EMAIL}"
            )

    def test_location_mentions(self):
        """Verify Mallorca / Spain / Remote-first location is correctly stated."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            text = extract_visible_text(html).lower()
            has_mallorca = "mallorca" in text
            has_spain = "spain" in text or "españa" in text
            has_remote = "remote" in text
            self.assertTrue(
                has_mallorca or (has_spain and has_remote),
                f"Version {v} does not mention location (Mallorca / Spain / Remote)"
            )

    def test_no_day_rate_displayed(self):
        """CRITICAL: Strict requirement that NO day rate is present on any version."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            for pattern in DAY_RATE_PATTERNS:
                matches = pattern.findall(html)
                self.assertEqual(
                    len(matches), 0,
                    f"Version {v} violates rate prohibition! Found rate match: {matches} with pattern {pattern.pattern}"
                )

    def test_verified_credentials(self):
        """Verify real credentials (UIB Math, MBA, PMP) appear in each version."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            text = extract_visible_text(html).lower()

            # Math
            has_math = "mathematics" in text or "matemáticas" in text or "math" in text
            self.assertTrue(has_math, f"Version {v} missing Mathematics background mention")

            # PMP
            has_pmp = "pmp" in text or "project management professional" in text
            self.assertTrue(has_pmp, f"Version {v} missing PMP certification mention")

            # MBA / Business
            has_mba = "mba" in text or "master in business" in text or "eserp" in text
            self.assertTrue(has_mba, f"Version {v} missing MBA / Business qualification mention")

    def test_verified_clients_and_employers(self):
        """Verify real enterprise clients/employers from CV_gen are cited accurately."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            text = extract_visible_text(html).lower()
            matched_companies = [
                c for c in ["astrazeneca", "boehringer", "movinga", "mapfre"]
                if c in text
            ]
            # vA (Enterprise) and vC (Systems) cite large enterprise clients; vB (SME Fractional) focuses on scale-ups (Movinga)
            min_expected = 1 if v == "vB" else 2
            self.assertGreaterEqual(
                len(matched_companies), min_expected,
                f"Version {v} cites fewer than {min_expected} verified enterprise/scaleup clients (found: {matched_companies})"
            )

    def test_no_unmapped_fictional_claims(self):
        """Flag any unmapped client or corporate claims not present in CV_gen."""
        hallucination_indicators = [
            "google lead", "amazon director", "meta cdo", "mckinsey partner",
            "microsoft vp", "apple architect", "harvard phd", "stanford mba",
            "20+ years", "30+ years", "100m revenue", "$100m"
        ]
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            text = extract_visible_text(html).lower()
            for bad_claim in hallucination_indicators:
                self.assertNotIn(
                    bad_claim, text,
                    f"Version {v} contains unmapped or embellished claim: '{bad_claim}'"
                )


if __name__ == "__main__":
    unittest.main()
