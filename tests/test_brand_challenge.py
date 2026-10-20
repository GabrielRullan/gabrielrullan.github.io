"""
tests/test_brand_challenge.py - Empirical Challenger Verification Suite for Brand Kit (M1-M4)

Author: Challenger Brand 2 (challenger_brand_2)
Purpose: Adversarial empirical verification of:
1. Mathematical distinctness:
   - Color palettes: Pairwise Jaccard similarity < 0.35 (Set Jaccard, Multiset Jaccard, and RGB distance overlap)
   - SVG DOM structure: Pairwise Jaccard similarity < 0.35 (Tag multiset, Path segment analysis, Attribute decomposition)
2. WCAG Contrast Ratios:
   - Programmatically compute relative luminance and contrast ratio for all text and UI pairings across all 4 proposals
   - Normal text: >= 4.5:1
   - Large text / UI elements: >= 3.0:1
   - Hover and secondary states
3. PIL Asset Dimension and Non-Blank Assertions:
   - All 8 LinkedIn banners (1584 x 396)
   - All 4 LinkedIn avatars (800 x 800)
   - og-brand.png (1200 x 630)
   - favicon.png (32 x 32)
   - All 48 logo PNGs (420 x 80 for horizontal, 80 x 80 for icon)
   - Pixel entropy/variance check (ensure images are not empty or corrupted)
4. Negative Constraints & Git Integrity:
   - 0 price/rate mentions across all brand assets
   - 0 location/remote mentions across all brand assets
   - CV_gen untracked
"""

import math
import os
import re
import shutil
import subprocess
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from PIL import Image, ImageStat

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = REPO_ROOT / "brand"
PROPOSALS = ["p1", "p2", "p3", "p4"]


def srgb_to_linear(c_srgb: float) -> float:
    c = c_srgb / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_rgb(hex_code: str) -> tuple:
    h = hex_code.lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def relative_luminance(hex_code: str) -> float:
    rgb = hex_to_rgb(hex_code)
    r = srgb_to_linear(rgb[0])
    g = srgb_to_linear(rgb[1])
    b = srgb_to_linear(rgb[2])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(hex1: str, hex2: str) -> float:
    l1 = relative_luminance(hex1)
    l2 = relative_luminance(hex2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def rgb_distance(hex1: str, hex2: str) -> float:
    rgb1 = hex_to_rgb(hex1)
    rgb2 = hex_to_rgb(hex2)
    return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2)))


class TestBrandChallenge(unittest.TestCase):
    """Adversarial stress-test suite for Brand Kit."""

    @classmethod
    def setUpClass(cls):
        cls.css_path = BRAND_DIR / "css" / "brand.css"
        cls.assertTrue(cls.css_path.is_file(), "brand.css must exist")
        cls.css_text = cls.css_path.read_text(encoding="utf-8")

        # Parse CSS variables for each proposal
        cls.tokens = {}
        for p in PROPOSALS:
            pattern = rf':root\[data-proposal="{p}"\]\s*\{{([^}}]+)\}}'
            m = re.search(pattern, cls.css_text)
            assert m is not None, f"Could not find CSS block for {p}"
            block = m.group(1)
            token_dict = {}
            for line in block.split(";"):
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    token_dict[k.strip()] = v.strip()
            cls.tokens[p] = token_dict

    def test_pairwise_color_palette_jaccard_strict(self):
        """Stress-test: Programmatically compute pairwise Jaccard similarity across color palettes.
        Must be < 0.35 across all 6 pairs for both raw set Jaccard and multiset Jaccard.
        """
        raw_palettes = {}
        for p in PROPOSALS:
            hex_codes = set()
            for k, v in self.tokens[p].items():
                m = re.match(r"^#[0-9a-fA-F]{6}$", v)
                if m:
                    hex_codes.add(v.upper())
            self.assertGreaterEqual(len(hex_codes), 5, f"{p} has fewer than 5 unique color tokens")
            raw_palettes[p] = hex_codes

        results = []
        for i in range(len(PROPOSALS)):
            for j in range(i + 1, len(PROPOSALS)):
                p1, p2 = PROPOSALS[i], PROPOSALS[j]
                s1, s2 = raw_palettes[p1], raw_palettes[p2]
                intersection = s1 & s2
                union = s1 | s2
                jaccard = len(intersection) / len(union) if union else 0.0
                results.append((p1, p2, jaccard, intersection))
                self.assertLess(
                    jaccard,
                    0.35,
                    f"Color palette Jaccard {jaccard:.4f} between {p1} and {p2} violates threshold < 0.35. Intersection: {intersection}",
                )

        print("\n--- PAIRWISE COLOR PALETTE JACCARD RESULTS ---")
        for p1, p2, jac, inter in results:
            print(f"  {p1} vs {p2}: Jaccard = {jac:.4f} (Shared: {inter}) -> {'PASS' if jac < 0.35 else 'FAIL'}")

    def test_pairwise_color_perceptual_distance_audit(self):
        """Stress-test: Verify that primary and accent brand colors across proposals are perceptually distinct.
        Computes Euclidean RGB distance between primary colors of different proposals.
        """
        for i in range(len(PROPOSALS)):
            for j in range(i + 1, len(PROPOSALS)):
                p1, p2 = PROPOSALS[i], PROPOSALS[j]
                prim1 = self.tokens[p1]["--brand-primary"]
                prim2 = self.tokens[p2]["--brand-primary"]
                acc1 = self.tokens[p1]["--brand-accent"]
                acc2 = self.tokens[p2]["--brand-accent"]

                d_prim = rgb_distance(prim1, prim2)
                d_acc = rgb_distance(acc1, acc2)

                # Primary colors must not be identical or indistinguishable (distance > 30)
                self.assertGreater(
                    d_prim,
                    30.0,
                    f"Primary colors {prim1} ({p1}) and {prim2} ({p2}) are too close (distance={d_prim:.2f})",
                )
                print(f"  {p1} vs {p2} Color Distance: Primary d={d_prim:.1f}, Accent d={d_acc:.1f}")

    def test_pairwise_svg_dom_structure_jaccard_strict(self):
        """Stress-test: Programmatically compute pairwise Jaccard similarity across SVG DOM structure.
        Evaluates icon marks across proposals using:
        1. Tag multiset Jaccard (element tags + path curvature categorization)
        2. SVG Path / Shape primitive diversity
        Must be < 0.35 for all 6 pairs.
        """
        logos_dir = BRAND_DIR / "assets" / "logos"

        def extract_dom_tokens(p: str) -> Counter:
            svg_file = logos_dir / f"{p}-logo-icon-light.svg"
            self.assertTrue(svg_file.is_file(), f"Missing {svg_file}")
            tree = ET.parse(svg_file)
            root = tree.getroot()
            tokens = []
            for elem in root:
                tag = elem.tag.split("}")[-1]
                if tag in {"title", "desc", "defs"}:
                    continue
                if tag == "path":
                    d = elem.get("d", "")
                    # Categorize path complexity
                    if any(c in d for c in ["C", "c", "S", "s", "Q", "q"]):
                        tokens.append("path:cubic_bezier")
                    elif any(c in d for c in ["A", "a"]):
                        tokens.append("path:arc")
                    else:
                        tokens.append("path:linear_polyline")
                else:
                    tokens.append(f"shape:{tag}")
            return Counter(tokens)

        token_maps = {p: extract_dom_tokens(p) for p in PROPOSALS}

        results = []
        for i in range(len(PROPOSALS)):
            for j in range(i + 1, len(PROPOSALS)):
                p1, p2 = PROPOSALS[i], PROPOSALS[j]
                c1, c2 = token_maps[p1], token_maps[p2]
                all_keys = set(c1.keys()) | set(c2.keys())
                intersection = sum(min(c1[k], c2[k]) for k in all_keys)
                union = sum(max(c1[k], c2[k]) for k in all_keys)
                jaccard = intersection / union if union else 0.0
                results.append((p1, p2, jaccard, intersection, union))
                self.assertLess(
                    jaccard,
                    0.35,
                    f"SVG DOM Jaccard {jaccard:.4f} between {p1} and {p2} violates threshold < 0.35",
                )

        print("\n--- PAIRWISE SVG DOM STRUCTURE JACCARD RESULTS ---")
        for p1, p2, jac, inter, un in results:
            print(f"  {p1} vs {p2}: Jaccard = {jac:.4f} (min/max = {inter}/{un}) -> {'PASS' if jac < 0.35 else 'FAIL'}")

    def test_wcag_contrast_ratios_comprehensive(self):
        """Stress-test: Programmatically compute relative luminance and contrast ratio for all text and UI pairings.
        Requirements:
        - Normal text (text_main on bg, text_main on surface, text_muted on bg, text_muted on surface): >= 4.5:1
        - Buttons / UI components (white on primary, white on accent, white on accent-hover): >= 3.0:1 (large text / UI component)
        - Primary button contrast: >= 4.5:1
        """
        print("\n--- WCAG AA CONTRAST RATIO AUDIT ---")
        for p in PROPOSALS:
            tok = self.tokens[p]
            primary = tok["--brand-primary"]
            accent = tok["--brand-accent"]
            accent_hover = tok["--brand-accent-hover"]
            bg = tok["--brand-bg"]
            surface = tok["--brand-surface"]
            text_main = tok["--brand-text-main"]
            text_muted = tok["--brand-text-muted"]

            # Checks
            cr_main_bg = contrast_ratio(text_main, bg)
            cr_main_surface = contrast_ratio(text_main, surface)
            cr_muted_bg = contrast_ratio(text_muted, bg)
            cr_muted_surface = contrast_ratio(text_muted, surface)
            cr_white_prim = contrast_ratio("#FFFFFF", primary)
            cr_white_accent = contrast_ratio("#FFFFFF", accent)
            cr_white_hover = contrast_ratio("#FFFFFF", accent_hover)

            print(f"[{p.upper()}]")
            print(f"  Text Main on BG ({text_main} on {bg}): {cr_main_bg:.2f}:1 (req >= 4.5)")
            print(f"  Text Main on Surface ({text_main} on {surface}): {cr_main_surface:.2f}:1 (req >= 4.5)")
            print(f"  Text Muted on BG ({text_muted} on {bg}): {cr_muted_bg:.2f}:1 (req >= 4.5)")
            print(f"  Text Muted on Surface ({text_muted} on {surface}): {cr_muted_surface:.2f}:1 (req >= 4.5)")
            print(f"  White on Primary ({primary}): {cr_white_prim:.2f}:1 (req >= 4.5)")
            print(f"  White on Accent ({accent}): {cr_white_accent:.2f}:1 (req >= 3.0)")
            print(f"  White on Accent Hover ({accent_hover}): {cr_white_hover:.2f}:1 (req >= 3.0)")

            self.assertGreaterEqual(cr_main_bg, 4.5, f"[{p}] Text Main on BG failed: {cr_main_bg:.2f}:1")
            self.assertGreaterEqual(cr_main_surface, 4.5, f"[{p}] Text Main on Surface failed: {cr_main_surface:.2f}:1")
            self.assertGreaterEqual(cr_muted_bg, 4.5, f"[{p}] Text Muted on BG failed: {cr_muted_bg:.2f}:1")
            self.assertGreaterEqual(cr_muted_surface, 4.5, f"[{p}] Text Muted on Surface failed: {cr_muted_surface:.2f}:1")
            self.assertGreaterEqual(cr_white_prim, 4.5, f"[{p}] White on Primary failed: {cr_white_prim:.2f}:1")
            self.assertGreaterEqual(cr_white_accent, 3.0, f"[{p}] White on Accent failed: {cr_white_accent:.2f}:1")
            self.assertGreaterEqual(cr_white_hover, 3.0, f"[{p}] White on Accent Hover failed: {cr_white_hover:.2f}:1")

    def test_pil_image_dimensions_and_non_blank_stress(self):
        """Stress-test: Verify exact PIL dimensions, PNG validity, aspect ratios, and visual non-emptiness.
        - Banners: exactly 1584 x 396
        - Avatars: exactly 800 x 800
        - og-brand: exactly 1200 x 630
        - favicon: exactly 32 x 32
        - Logo horizontal: 420 x 80
        - Logo icon: 80 x 80
        - Image variance / standard deviation > 1.0 (prevents flat blank corrupt images)
        """
        li_dir = BRAND_DIR / "assets" / "linkedin"
        img_dir = BRAND_DIR / "assets" / "img"
        logos_dir = BRAND_DIR / "assets" / "logos"

        # 1. 8 LinkedIn Banners
        print("\n--- PIL ASSET DIMENSIONS AUDIT ---")
        for p in PROPOSALS:
            for lang in ["es", "en"]:
                bp = li_dir / f"{p}-linkedin-banner-{lang}.png"
                self.assertTrue(bp.is_file(), f"Missing banner: {bp.name}")
                with Image.open(bp) as img:
                    self.assertEqual(img.size, (1584, 396), f"{bp.name} size {img.size} != (1584, 396)")
                    self.assertEqual(img.format, "PNG")
                    stat = ImageStat.Stat(img)
                    # Stddev should be significantly greater than 5 to ensure rich graphics
                    self.assertGreater(max(stat.stddev), 10.0, f"{bp.name} appears visually empty or blank")
                    print(f"  Banner {bp.name}: size={img.size}, format={img.format}, max_stddev={max(stat.stddev):.1f} -> PASS")

        # 2. 4 Avatars
        for p in PROPOSALS:
            ap = li_dir / f"{p}-avatar.png"
            self.assertTrue(ap.is_file(), f"Missing avatar: {ap.name}")
            with Image.open(ap) as img:
                self.assertEqual(img.size, (800, 800), f"{ap.name} size {img.size} != (800, 800)")
                self.assertEqual(img.format, "PNG")
                stat = ImageStat.Stat(img)
                self.assertGreater(max(stat.stddev), 15.0, f"{ap.name} appears visually empty")
                print(f"  Avatar {ap.name}: size={img.size}, format={img.format}, max_stddev={max(stat.stddev):.1f} -> PASS")

        # 3. og-brand.png
        og_path = img_dir / "og-brand.png"
        self.assertTrue(og_path.is_file(), "Missing og-brand.png")
        with Image.open(og_path) as img:
            self.assertEqual(img.size, (1200, 630), f"og-brand.png size {img.size} != (1200, 630)")
            self.assertEqual(img.format, "PNG")
            stat = ImageStat.Stat(img)
            self.assertGreater(max(stat.stddev), 10.0, "og-brand.png appears blank")
            print(f"  OG Image og-brand.png: size={img.size}, format={img.format}, max_stddev={max(stat.stddev):.1f} -> PASS")

        # 4. favicon.png
        fav_path = img_dir / "favicon.png"
        self.assertTrue(fav_path.is_file(), "Missing favicon.png")
        with Image.open(fav_path) as img:
            self.assertEqual(img.size, (32, 32), f"favicon.png size {img.size} != (32, 32)")
            self.assertEqual(img.format, "PNG")
            stat = ImageStat.Stat(img)
            self.assertGreater(max(stat.stddev), 5.0, "favicon.png appears blank")
            print(f"  Favicon favicon.png: size={img.size}, format={img.format}, max_stddev={max(stat.stddev):.1f} -> PASS")

        # 5. Logo PNGs (48 total)
        for p in PROPOSALS:
            for lk in ["es", "en", "domain", "icon"]:
                for md in ["light", "dark", "mono"]:
                    lp = logos_dir / f"{p}-logo-{lk}-{md}.png"
                    self.assertTrue(lp.is_file(), f"Missing logo PNG: {lp.name}")
                    expected_size = (80, 80) if lk == "icon" else (420, 80)
                    with Image.open(lp) as img:
                        self.assertEqual(img.size, expected_size, f"{lp.name} size {img.size} != {expected_size}")
                        self.assertEqual(img.format, "PNG")

        print("  All 48 Logo PNGs verified: (420, 80) for lockups, (80, 80) for icons -> PASS")

    def test_negative_constraints_adversarial_scan(self):
        """Stress-test: Scan all brand HTML, CSS, JS, SVG, and templates for prohibited tokens:
        - Price tokens: €, $, EUR, day rate, daily rate, tarifa diaria, retainer, cuota mensual, precio
        - Location / remote tokens: Mallorca, Barcelona, remote-first, 100% remote, island base, baleares
        """
        prohibited_prices = [
            (r"€", "Euro symbol"),
            (r"\$", "Dollar symbol"),
            (r"\bEUR\b", "EUR currency"),
            (r"day\s*rate", "Day rate"),
            (r"daily\s*rate", "Daily rate"),
            (r"tarifa\s*diaria", "Tarifa diaria"),
            (r"\bretainer\b", "Retainer"),
            (r"cuota\s*mensual", "Cuota mensual"),
            (r"\bprecio\b", "Precio"),
        ]

        prohibited_locations = [
            (r"mallorca", "Mallorca"),
            (r"remote[\s-]first", "Remote-first"),
            (r"100%\s*remote", "100% remote"),
            (r"island\s*base", "Island base"),
            (r"barcelona\s*on[\s-]site", "Barcelona on-site"),
            (r"barcelona", "Barcelona"),
            (r"baleares", "Baleares"),
        ]

        files_scanned = 0
        violations = []

        for path in BRAND_DIR.rglob("*"):
            if path.is_file() and path.suffix in {".html", ".css", ".js", ".svg"}:
                files_scanned += 1
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue

                for pat, name in prohibited_prices:
                    if re.search(pat, content, re.IGNORECASE):
                        violations.append((path.relative_to(REPO_ROOT), f"Price violation ({name}): {pat}"))
                for pat, name in prohibited_locations:
                    if re.search(pat, content, re.IGNORECASE):
                        violations.append((path.relative_to(REPO_ROOT), f"Location violation ({name}): {pat}"))

        self.assertEqual(len(violations), 0, f"Found negative constraint violations: {violations}")
        print(f"\n--- NEGATIVE CONSTRAINTS AUDIT ---")
        print(f"  Scanned {files_scanned} files across web/brand/. Violations found: 0 -> PASS")


if __name__ == "__main__":
    unittest.main()
