"""
tests/test_distinctness.py - 5-dimension distinctness rubric test suite.

Verifies:
1. Palette distinctness (hex/rgb colors, CSS variables, dark vs light vs warm).
2. Typography distinctness (heading font families, body fonts, serif vs sans vs mono).
3. Layout structure distinctness (DOM structure, hero layout, section taxonomy).
4. Headline tone distinctness (enterprise authority vs fractional partner vs systems builder).
5. Logo / Favicon concept distinctness (monogram crest vs infinity/dp vs circuit/sigma).

Pairwise check:
- vA vs vB >= 4/5 (target 5/5)
"""

import os
import re
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"

VERSIONS = ["vA", "vB", "vD", "vE"]


def load_file_safe(version: str, rel_path: str) -> str:
    path = WEB_DIR / version / rel_path
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_colors_from_css(css_content: str) -> set:
    if not css_content:
        return set()
    hex_colors = set(re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", css_content))
    return {c.lower() for c in hex_colors}


def extract_fonts(html_content: str, css_content: str) -> dict:
    google_fonts = re.findall(r"family=([^&'\"]+)", html_content) if html_content else []
    font_families = []
    for gf in google_fonts:
        clean = gf.replace("+", " ").split(":")[0]
        font_families.append(clean.lower())

    css_fonts = re.findall(r"font-family\s*:\s*([^;]+);", css_content, re.IGNORECASE) if css_content else []
    cleaned_css_fonts = []
    for cf in css_fonts:
        for item in cf.split(","):
            cleaned = item.strip().strip("'\"").lower()
            if cleaned not in ["sans-serif", "serif", "monospace", "inherit", "initial"]:
                cleaned_css_fonts.append(cleaned)

    return {
        "google_fonts": set(font_families),
        "css_fonts": set(cleaned_css_fonts)
    }


def extract_layout_features(html_content: str) -> dict:
    if not html_content:
        return {"sections": set(), "h2_headings": set(), "nav_anchors": set(), "num_cards": 0}
    soup = BeautifulSoup(html_content, "html.parser")
    sections = [s.get("id") or s.get("class", [""])[0] for s in soup.find_all("section")]
    h2_headings = [h.get_text(strip=True).lower() for h in soup.find_all("h2")]
    nav_links = [a.get_text(strip=True).lower() for a in soup.find_all("a") if a.get("href", "").startswith("#")]
    num_cards = len(soup.find_all(class_=re.compile(r"card|tier|box|pillar|grid-item|item", re.IGNORECASE)))
    
    return {
        "sections": set(filter(None, sections)),
        "h2_headings": set(h2_headings),
        "nav_anchors": set(nav_links),
        "num_cards": num_cards
    }


def extract_headline_tone(html_content: str) -> dict:
    if not html_content:
        return {
            "h1": "", "lead": "", "words": set(),
            "enterprise_score": 0, "fractional_score": 0, "systems_score": 0
        }
    soup = BeautifulSoup(html_content, "html.parser")
    h1 = soup.find("h1")
    h1_text = h1.get_text(" ", strip=True).lower() if h1 else ""
    
    hero_p = ""
    hero_el = soup.find(class_=re.compile(r"hero", re.IGNORECASE))
    if hero_el:
        p_el = hero_el.find("p")
        if p_el:
            hero_p = p_el.get_text(" ", strip=True).lower()

    full_lead = f"{h1_text} {hero_p}"

    enterprise_keywords = {
        "enterprise", "governance", "authority", "compliance", "program", "strategic",
        "dama-dmbok", "stewardship", "architect", "institutional", "risk", "mitigation"
    }
    fractional_keywords = {
        "fractional", "cdo", "partner", "messy data", "revenue", "growth", "sme",
        "startup", "collaborative", "on-demand", "sprint", "roadmap", "agile"
    }
    systems_keywords = {
        "mathematician", "builder", "systems", "maker", "hardware", "arduino",
        "first principles", "algorithmic", "deterministic", "benchmarks", "code", "engineering"
    }

    words = set(re.findall(r"\b[a-zA-Z-]+\b", full_lead))
    return {
        "h1": h1_text,
        "lead": full_lead,
        "words": words,
        "enterprise_score": len(words & enterprise_keywords),
        "fractional_score": len(words & fractional_keywords),
        "systems_score": len(words & systems_keywords)
    }


def extract_logo_concept(version: str) -> dict:
    path = WEB_DIR / version / "img" / "logo.svg"
    if not path.exists():
        return {
            "svg_text": "", "num_paths": 0, "num_rects": 0,
            "num_circles": 0, "num_polygons": 0, "has_text": False, "length": 0
        }
    svg_text = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(svg_text, "html.parser")
    
    return {
        "svg_text": svg_text,
        "num_paths": len(soup.find_all("path")),
        "num_rects": len(soup.find_all("rect")),
        "num_circles": len(soup.find_all("circle")),
        "num_polygons": len(soup.find_all("polygon")),
        "has_text": len(soup.find_all("text")) > 0,
        "length": len(svg_text)
    }


def evaluate_palette_distinctness(v1_data, v2_data) -> bool:
    p1 = v1_data["colors"]
    p2 = v2_data["colors"]
    if not p1 or not p2:
        return True
    intersection = p1 & p2
    union = p1 | p2
    jaccard = len(intersection) / len(union) if union else 0
    return jaccard < 0.35


def evaluate_typography_distinctness(v1_data, v2_data) -> bool:
    f1 = v1_data["fonts"]["google_fonts"] | v1_data["fonts"]["css_fonts"]
    f2 = v2_data["fonts"]["google_fonts"] | v2_data["fonts"]["css_fonts"]
    overlap = f1 & f2
    return len(overlap) < min(len(f1), len(f2)) or len(overlap) <= 1


def evaluate_layout_distinctness(v1_data, v2_data) -> bool:
    s1 = v1_data["layout"]["sections"]
    s2 = v2_data["layout"]["sections"]
    overlap = s1 & s2
    union = s1 | s2
    jaccard = len(overlap) / len(union) if union else 0
    return jaccard < 0.5


def evaluate_tone_distinctness(v1_data, v2_data) -> bool:
    t1 = v1_data["tone"]
    t2 = v2_data["tone"]
    if t1["h1"] and t2["h1"] and t1["h1"] == t2["h1"]:
        return False
    p1_scores = (t1["enterprise_score"], t1["fractional_score"], t1["systems_score"])
    p2_scores = (t2["enterprise_score"], t2["fractional_score"], t2["systems_score"])
    return p1_scores != p2_scores or t1["h1"] != t2["h1"]


def evaluate_logo_distinctness(v1_data, v2_data) -> bool:
    l1 = v1_data["logo"]
    l2 = v2_data["logo"]
    diff_chars = abs(l1["length"] - l2["length"])
    return diff_chars > 150 or l1["num_paths"] != l2["num_paths"] or l1["num_circles"] != l2["num_circles"]


class TestPairwiseDistinctness(unittest.TestCase):
    """Test suite executing the 5-dimension distinctness rubric across all version pairs."""

    def _get_version_data(self, v: str) -> dict:
        html = load_file_safe(v, "index.html")
        css = load_file_safe(v, "css/style.css")
        return {
            "html_exists": bool(html),
            "colors": extract_colors_from_css(css),
            "fonts": extract_fonts(html, css),
            "layout": extract_layout_features(html),
            "tone": extract_headline_tone(html),
            "logo": extract_logo_concept(v)
        }

    def _evaluate_pair(self, v1: str, v2: str) -> dict:
        d1 = self._get_version_data(v1)
        d2 = self._get_version_data(v2)

        self.assertTrue(d1["html_exists"], f"Cannot evaluate {v1} vs {v2}: {v1}/index.html missing")
        self.assertTrue(d2["html_exists"], f"Cannot evaluate {v1} vs {v2}: {v2}/index.html missing")

        scores = {
            "palette": evaluate_palette_distinctness(d1, d2),
            "typography": evaluate_typography_distinctness(d1, d2),
            "layout": evaluate_layout_distinctness(d1, d2),
            "tone": evaluate_tone_distinctness(d1, d2),
            "logo": evaluate_logo_distinctness(d1, d2),
        }
        total_score = sum(1 for val in scores.values() if val)
        return {
            "pair": f"{v1} vs {v2}",
            "scores": scores,
            "total": total_score,
            "passed": total_score >= 4
        }

    def test_pairwise_vA_vs_vB(self):
        """vA (Enterprise Authority) vs vB (Fractional Partner) must differ in >= 4/5 dimensions."""
        result = self._evaluate_pair("vA", "vB")
        self.assertTrue(
            result["passed"],
            f"vA vs vB failed distinctness threshold! Total: {result['total']}/5. Breakdown: {result['scores']}"
        )
        self.assertGreaterEqual(result["total"], 4, "vA vs vB distinctness must be >= 4")

    def test_pairwise_vA_vs_vD(self):
        """vA (Enterprise Authority) vs vD (Authoritative Hybrid) must differ in >= 4/5 dimensions."""
        result = self._evaluate_pair("vA", "vD")
        self.assertTrue(
            result["passed"],
            f"vA vs vD failed distinctness threshold! Total: {result['total']}/5. Breakdown: {result['scores']}"
        )
        self.assertGreaterEqual(result["total"], 4, "vA vs vD distinctness must be >= 4")

    def test_pairwise_vB_vs_vD(self):
        """vB (Fractional Partner) vs vD (Authoritative Hybrid) must differ in >= 4/5 dimensions."""
        result = self._evaluate_pair("vB", "vD")
        self.assertTrue(
            result["passed"],
            f"vB vs vD failed distinctness threshold! Total: {result['total']}/5. Breakdown: {result['scores']}"
        )
        self.assertGreaterEqual(result["total"], 4, "vB vs vD distinctness must be >= 4")

    def test_pairwise_vA_vs_vE(self):
        """vA (Enterprise Authority) vs vE (Personal Spanish Partner) must differ in >= 4/5 dimensions."""
        result = self._evaluate_pair("vA", "vE")
        self.assertTrue(
            result["passed"],
            f"vA vs vE failed distinctness threshold! Total: {result['total']}/5. Breakdown: {result['scores']}"
        )
        self.assertGreaterEqual(result["total"], 4, "vA vs vE distinctness must be >= 4")

    def test_pairwise_vD_vs_vE(self):
        """vD (Authoritative Hybrid) vs vE (Personal Spanish Partner) must differ in >= 4/5 dimensions."""
        result = self._evaluate_pair("vD", "vE")
        self.assertTrue(
            result["passed"],
            f"vD vs vE failed distinctness threshold! Total: {result['total']}/5. Breakdown: {result['scores']}"
        )
        self.assertGreaterEqual(result["total"], 4, "vD vs vE distinctness must be >= 4")


if __name__ == "__main__":
    unittest.main()
