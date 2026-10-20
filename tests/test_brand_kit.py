"""
tests/test_brand_kit.py - Comprehensive verification suite for Personal Freelance Brand Kit.

Covers:
1. Complete brand kit file structure (index, css, js, template, 96 logos, 24 linkedin, 8 signatures, images).
2. Pairwise color palette Jaccard similarity < 0.35 across all 4 proposals.
3. Pairwise SVG DOM structure Jaccard similarity < 0.35 across all 4 proposals.
4. WCAG AA / AAA contrast compliance (>= 4.5:1 normal text, >= 3.0:1 large/UI).
5. PIL image validation: LinkedIn banners (1584x396), avatars (800x800), og-brand (1200x630), favicon (32x32).
6. HTML standards: single <h1>, SEO meta, Open Graph, <img> alt, relative links, transfer budget < 3 MB.
7. Negative constraints: zero prices/rates, zero location/remote mentions, portrait verification, untracked CV_gen.
8. Headless Chrome responsive audit (375px, 768px, 1440px) with 0 overflow, 0 console errors, 0 404s, all images loaded.
9. Headless Chrome interactive controls: proposal switcher, 3D card flip, copy hex toast, valid downloads.
"""

import hashlib
import os
import re
import shutil
import subprocess
import time
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup
import numpy as np
from PIL import Image

from test_headless_responsive import (
    LocalWebServer,
    ChromeHeadlessDriver,
    find_browser_executable,
)

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


class TestBrandKit(unittest.TestCase):
    """Personal Freelance Brand Kit verification suite."""

    server = None
    driver = None

    @classmethod
    def setUpClass(cls):
        from functools import partial
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        import threading
        from test_headless_responsive import find_free_port

        cls.server = LocalWebServer(port=find_free_port())
        handler = partial(SimpleHTTPRequestHandler, directory=str(REPO_ROOT))
        ThreadingHTTPServer.allow_reuse_address = True
        cls.server.httpd = ThreadingHTTPServer(("127.0.0.1", cls.server.port), handler)
        cls.server.thread = threading.Thread(target=cls.server.httpd.serve_forever, daemon=True)
        cls.server.thread.start()
        time.sleep(0.5)

        browser_path = find_browser_executable()
        cls.driver = ChromeHeadlessDriver(browser_path)
        cls.driver.start()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.close()
        if cls.server:
            cls.server.stop()

    def test_brand_kit_file_structure(self):
        """Verifies existence of core files in brand/ (not web/brand/), 96 logos, 24 linkedin assets, 8 signatures, images, templates."""
        self.assertFalse((REPO_ROOT / "web" / "brand").exists(), "web/brand must NOT exist (stored outside web/)")
        # 1. Core pages and stylesheets
        self.assertTrue((BRAND_DIR / "index.html").is_file(), "brand/index.html missing")
        self.assertTrue((BRAND_DIR / "css" / "brand.css").is_file(), "brand/css/brand.css missing")
        self.assertTrue((BRAND_DIR / "js" / "brand.js").is_file(), "brand/js/brand.js missing")
        self.assertTrue((BRAND_DIR / "templates" / "a4-report.html").is_file(), "a4-report.html missing")
        self.assertTrue((BRAND_DIR / "favicon.ico").is_file(), "brand/favicon.ico missing")

        # 2. Key images
        self.assertTrue((BRAND_DIR / "assets" / "img" / "gabriel.jpg").is_file(), "gabriel.jpg missing")
        self.assertTrue((BRAND_DIR / "assets" / "img" / "og-brand.png").is_file(), "og-brand.png missing")
        self.assertTrue((BRAND_DIR / "assets" / "img" / "favicon.png").is_file(), "favicon.png missing")

        # 3. Logo suite: 4 proposals x 4 lockups x 3 modes in SVG and PNG = 96 files
        lockups = ["es", "en", "domain", "icon"]
        modes = ["light", "dark", "mono"]
        logos_dir = BRAND_DIR / "assets" / "logos"
        svg_count = 0
        png_count = 0

        for p in PROPOSALS:
            for lk in lockups:
                for md in modes:
                    svg_file = logos_dir / f"{p}-logo-{lk}-{md}.svg"
                    png_file = logos_dir / f"{p}-logo-{lk}-{md}.png"
                    self.assertTrue(svg_file.is_file(), f"Missing logo SVG: {svg_file.name}")
                    self.assertTrue(png_file.is_file(), f"Missing logo PNG: {png_file.name}")
                    self.assertGreater(svg_file.stat().st_size, 200, f"SVG file too small: {svg_file.name}")
                    self.assertGreater(png_file.stat().st_size, 500, f"PNG file too small: {png_file.name}")
                    try:
                        tree = ET.parse(svg_file)
                        self.assertTrue(tree.getroot().tag.endswith("svg"), f"Root element of {svg_file.name} is not <svg>")
                    except Exception as e:
                        self.fail(f"Invalid XML syntax in logo SVG {svg_file.name}: {e}")
                    svg_count += 1
                    png_count += 1

        self.assertEqual(svg_count, 48, "Expected 48 SVG logos")
        self.assertEqual(png_count, 48, "Expected 48 PNG logos")

        # 4. LinkedIn kit: 8 banners (PNG+SVG) + 4 avatars (PNG+SVG) = 24 files
        li_dir = BRAND_DIR / "assets" / "linkedin"
        for p in PROPOSALS:
            for lang in ["es", "en"]:
                b_svg = li_dir / f"{p}-linkedin-banner-{lang}.svg"
                b_png = li_dir / f"{p}-linkedin-banner-{lang}.png"
                self.assertTrue(b_svg.is_file(), f"Missing LinkedIn banner SVG: {b_svg.name}")
                self.assertTrue(b_png.is_file(), f"Missing LinkedIn banner PNG: {b_png.name}")
                self.assertGreater(b_svg.stat().st_size, 1000, f"Banner SVG too small: {b_svg.name}")
                try:
                    tree = ET.parse(b_svg)
                    self.assertTrue(tree.getroot().tag.endswith("svg"), f"Root element of {b_svg.name} is not <svg>")
                except Exception as e:
                    self.fail(f"Invalid XML syntax in banner SVG {b_svg.name}: {e}")
            av_svg = li_dir / f"{p}-avatar.svg"
            av_png = li_dir / f"{p}-avatar.png"
            self.assertTrue(av_svg.is_file(), f"Missing LinkedIn avatar SVG: {av_svg.name}")
            self.assertTrue(av_png.is_file(), f"Missing LinkedIn avatar PNG: {av_png.name}")
            self.assertGreater(av_svg.stat().st_size, 1000, f"Avatar SVG too small: {av_svg.name}")
            try:
                tree = ET.parse(av_svg)
                self.assertTrue(tree.getroot().tag.endswith("svg"), f"Root element of {av_svg.name} is not <svg>")
            except Exception as e:
                self.fail(f"Invalid XML syntax in avatar SVG {av_svg.name}: {e}")

        # 5. Email signatures: 4 proposals x 2 languages = 8 signatures
        sig_dir = BRAND_DIR / "assets" / "signatures"
        for p in PROPOSALS:
            for lang in ["es", "en"]:
                sig_file = sig_dir / f"signature-{p}-{lang}.html"
                self.assertTrue(sig_file.is_file(), f"Missing email signature: {sig_file.name}")
                self.assertGreater(sig_file.stat().st_size, 500, f"Signature file too small: {sig_file.name}")

    def test_all_svg_xml_well_formedness(self):
        """Validates that EVERY .svg file under web/brand/ parses cleanly as valid XML without syntax errors."""
        svg_files = list(BRAND_DIR.rglob("*.svg"))
        self.assertGreaterEqual(len(svg_files), 60, f"Expected >= 60 SVGs in brand kit, found {len(svg_files)}")
        for svg_file in svg_files:
            try:
                tree = ET.parse(svg_file)
                root = tree.getroot()
                self.assertTrue(root.tag.endswith("svg"), f"Root element of {svg_file.name} is not <svg>: {root.tag}")
            except Exception as e:
                self.fail(f"XML parse failure in {svg_file.relative_to(REPO_ROOT)}: {e}")

    def test_color_palette_distinctness_jaccard(self):
        """Verifies pairwise color palette Jaccard similarity < 0.35 across all 4 proposals."""
        css_content = (BRAND_DIR / "css" / "brand.css").read_text(encoding="utf-8")

        palettes = {}
        for p in PROPOSALS:
            # Match :root[data-proposal="pX"] block
            pattern = rf':root\[data-proposal="{p}"\]\s*\{{([^}}]+)\}}'
            match = re.search(pattern, css_content)
            self.assertIsNotNone(match, f"Could not find CSS block for proposal {p}")
            block = match.group(1)
            hex_codes = set(re.findall(r"#[0-9a-fA-F]{6}", block))
            self.assertGreaterEqual(len(hex_codes), 5, f"Proposal {p} has too few color tokens: {hex_codes}")
            palettes[p] = {c.upper() for c in hex_codes}

        for i in range(len(PROPOSALS)):
            for j in range(i + 1, len(PROPOSALS)):
                p1, p2 = PROPOSALS[i], PROPOSALS[j]
                s1, s2 = palettes[p1], palettes[p2]
                intersection = s1 & s2
                union = s1 | s2
                jaccard = len(intersection) / len(union) if union else 0.0
                self.assertLess(
                    jaccard,
                    0.35,
                    f"Color palette Jaccard similarity {jaccard:.4f} between {p1} and {p2} is >= 0.35",
                )

    def test_svg_logo_structure_distinctness_jaccard(self):
        """Verifies pairwise SVG DOM structure multiset Jaccard similarity < 0.35 across all 4 proposals."""
        logos_dir = BRAND_DIR / "assets" / "logos"

        def extract_structural_tokens(p: str) -> Counter:
            svg_file = logos_dir / f"{p}-logo-icon-light.svg"
            self.assertTrue(svg_file.is_file(), f"Missing {svg_file.name}")
            tree = ET.parse(svg_file)
            root = tree.getroot()
            tokens = []
            for elem in root:
                tag = elem.tag.split("}")[-1]
                if tag == "title":
                    continue
                if tag == "path":
                    d = elem.get("d", "")
                    if "C" in d or "c" in d:
                        tokens.append("path:cubic")
                    else:
                        tokens.append("path:linear")
                else:
                    tokens.append(tag)
            return Counter(tokens)

        proposals_tokens = {p: extract_structural_tokens(p) for p in PROPOSALS}

        for i in range(len(PROPOSALS)):
            for j in range(i + 1, len(PROPOSALS)):
                p1, p2 = PROPOSALS[i], PROPOSALS[j]
                c1, c2 = proposals_tokens[p1], proposals_tokens[p2]
                all_keys = set(c1.keys()) | set(c2.keys())
                intersection = sum(min(c1[k], c2[k]) for k in all_keys)
                union = sum(max(c1[k], c2[k]) for k in all_keys)
                jaccard = intersection / union if union else 0.0
                self.assertLess(
                    jaccard,
                    0.35,
                    f"SVG DOM structure Jaccard similarity {jaccard:.4f} between {p1} and {p2} is >= 0.35",
                )

    def test_wcag_aa_contrast_compliance(self):
        """Verifies WCAG AA contrast compliance (>= 4.5:1 normal, >= 3.0:1 large/UI) across all 4 proposals."""
        css_content = (BRAND_DIR / "css" / "brand.css").read_text(encoding="utf-8")

        for p in PROPOSALS:
            pattern = rf':root\[data-proposal="{p}"\]\s*\{{([^}}]+)\}}'
            match = re.search(pattern, css_content)
            self.assertIsNotNone(match, f"Missing CSS block for {p}")
            block = match.group(1)

            def get_token(name: str) -> str:
                m = re.search(rf"{name}:\s*(#[0-9a-fA-F]{{6}})", block)
                self.assertIsNotNone(m, f"Token {name} not found in {p}")
                return m.group(1).upper()

            primary = get_token("--brand-primary")
            accent = get_token("--brand-accent")
            bg = get_token("--brand-bg")
            surface = get_token("--brand-surface")
            text_main = get_token("--brand-text-main")
            text_muted = get_token("--brand-text-muted")

            # 1. Main text on background surface (>= 4.5:1)
            cr_main_bg = contrast_ratio(text_main, bg)
            self.assertGreaterEqual(
                cr_main_bg,
                4.5,
                f"[{p}] Main text {text_main} on bg {bg} contrast {cr_main_bg:.2f}:1 is < 4.5:1",
            )

            # 2. Main text on card surface (>= 4.5:1)
            cr_main_surface = contrast_ratio(text_main, surface)
            self.assertGreaterEqual(
                cr_main_surface,
                4.5,
                f"[{p}] Main text {text_main} on surface {surface} contrast {cr_main_surface:.2f}:1 is < 4.5:1",
            )

            # 3. Muted text on background surface (>= 4.5:1)
            cr_muted_bg = contrast_ratio(text_muted, bg)
            self.assertGreaterEqual(
                cr_muted_bg,
                4.5,
                f"[{p}] Muted text {text_muted} on bg {bg} contrast {cr_muted_bg:.2f}:1 is < 4.5:1",
            )

            # 4. White text on primary button (>= 4.5:1)
            cr_white_prim = contrast_ratio("#FFFFFF", primary)
            self.assertGreaterEqual(
                cr_white_prim,
                4.5,
                f"[{p}] White on primary {primary} contrast {cr_white_prim:.2f}:1 is < 4.5:1",
            )

            # 5. White text on accent CTA button (>= 3.0:1 for large text/UI components)
            cr_white_accent = contrast_ratio("#FFFFFF", accent)
            self.assertGreaterEqual(
                cr_white_accent,
                3.0,
                f"[{p}] White on accent {accent} contrast {cr_white_accent:.2f}:1 is < 3.0:1",
            )

    def test_linkedin_collateral_dimensions_and_validity(self):
        """Verifies dimensions, pixel coverage, and hash distinctness for LinkedIn banners and avatars."""
        li_dir = BRAND_DIR / "assets" / "linkedin"

        # 8 LinkedIn banners: 1584 x 396, authentic size (> 40 KB), non-zero alpha coverage (> 25%), distinct hashes
        banner_hashes = {}
        for p in PROPOSALS:
            for lang in ["es", "en"]:
                bp = li_dir / f"{p}-linkedin-banner-{lang}.png"
                raw_bytes = bp.read_bytes()
                sha256_hash = hashlib.sha256(raw_bytes).hexdigest()
                banner_hashes[bp.name] = sha256_hash

                # Size assertion (> 40 KB)
                self.assertGreater(
                    bp.stat().st_size,
                    40000,
                    f"{bp.name} size ({bp.stat().st_size} bytes) is <= 40 KB (facade/blank screenshot detected)",
                )

                with Image.open(bp) as img:
                    self.assertEqual(img.size, (1584, 396), f"{bp.name} size is {img.size}, expected (1584, 396)")
                    self.assertEqual(img.format, "PNG", f"{bp.name} is {img.format}, expected PNG")

                    arr = np.array(img)
                    if arr.ndim == 3 and arr.shape[2] == 4:
                        non_zero_alpha = np.count_nonzero(arr[:, :, 3])
                        total_pixels = arr.shape[0] * arr.shape[1]
                        alpha_cov = non_zero_alpha / total_pixels
                        self.assertGreater(
                            alpha_cov,
                            0.25,
                            f"{bp.name} non-zero alpha coverage {alpha_cov:.2%} is <= 25% (blank/facade image)",
                        )
                    self.assertGreater(
                        float(arr.std()),
                        10.0,
                        f"{bp.name} pixel standard deviation {float(arr.std()):.2f} is too low (uniform/empty image)",
                    )

        # Assert 100% pairwise hash distinctness across all 8 banner PNGs
        unique_hashes = set(banner_hashes.values())
        self.assertEqual(
            len(unique_hashes),
            8,
            f"Expected 8 unique banner PNG hashes, but found only {len(unique_hashes)} unique. Hashes: {banner_hashes}",
        )

        # 4 Avatars: 800 x 800
        for p in PROPOSALS:
            ap = li_dir / f"{p}-avatar.png"
            with Image.open(ap) as img:
                self.assertEqual(img.size, (800, 800), f"{ap.name} size is {img.size}, expected (800, 800)")
                self.assertEqual(img.format, "PNG", f"{ap.name} is {img.format}, expected PNG")
                self.assertGreater(ap.stat().st_size, 1000, f"{ap.name} size suspiciously small")

        # og-brand.png: 1200 x 630
        og_path = BRAND_DIR / "assets" / "img" / "og-brand.png"
        with Image.open(og_path) as img:
            self.assertEqual(img.size, (1200, 630), f"og-brand.png size is {img.size}, expected (1200, 630)")
            self.assertEqual(img.format, "PNG")

        # favicon.png: 32 x 32
        fav_path = BRAND_DIR / "assets" / "img" / "favicon.png"
        with Image.open(fav_path) as img:
            self.assertEqual(img.size, (32, 32), f"favicon.png size is {img.size}, expected (32, 32)")
            self.assertEqual(img.format, "PNG")

    def test_html_standards_and_page_budget(self):
        """Verifies single <h1>, meta tags, alt attributes, relative URLs, and page budget < 3 MB."""
        index_file = BRAND_DIR / "index.html"
        content = index_file.read_text(encoding="utf-8")
        soup = BeautifulSoup(content, "html.parser")

        # Exactly one <h1>
        h1_tags = soup.find_all("h1")
        self.assertEqual(len(h1_tags), 1, f"Expected exactly 1 <h1>, found {len(h1_tags)}")
        self.assertGreater(len(h1_tags[0].text.strip()), 10, "<h1> content too short")

        # Title & Meta Description
        title = soup.find("title")
        self.assertIsNotNone(title, "Missing <title> tag")
        self.assertGreater(len(title.text.strip()), 10, "Title tag too short")

        meta_desc = soup.find("meta", attrs={"name": "description"})
        self.assertIsNotNone(meta_desc, "Missing <meta name='description'> tag")
        self.assertGreater(len(meta_desc.get("content", "").strip()), 20, "Meta description too short")

        # Open Graph
        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        og_image = soup.find("meta", attrs={"property": "og:image"})
        self.assertIsNotNone(og_title, "Missing og:title")
        self.assertIsNotNone(og_desc, "Missing og:description")
        self.assertIsNotNone(og_image, "Missing og:image")

        # Alt text on all <img> tags
        img_tags = soup.find_all("img")
        self.assertGreater(len(img_tags), 5, "Expected images on page")
        for img in img_tags:
            alt = img.get("alt", "").strip()
            self.assertTrue(alt, f"Image {img.get('src', 'unknown')} has empty alt text")

        # Relative URL isolation (zero root-leading URLs)
        for tag, attr in [("a", "href"), ("link", "href"), ("script", "src"), ("img", "src")]:
            for el in soup.find_all(tag):
                val = el.get(attr)
                if val and not val.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                    self.assertFalse(
                        val.startswith("/"),
                        f"Root-leading URL found in <{tag} {attr}='{val}'>; must be relative ('./')",
                    )

        # Page budget: index + css + js + loaded images < 3 MB
        total_weight = index_file.stat().st_size
        total_weight += (BRAND_DIR / "css" / "brand.css").stat().st_size
        total_weight += (BRAND_DIR / "js" / "brand.js").stat().st_size

        for img in img_tags:
            src = img.get("src", "")
            if src.startswith("./") or not src.startswith(("http", "/")):
                ipath = (BRAND_DIR / src).resolve()
                if ipath.exists():
                    total_weight += ipath.stat().st_size

        max_budget = 3 * 1024 * 1024  # 3 MB
        self.assertLess(
            total_weight,
            max_budget,
            f"Page budget {total_weight / (1024 * 1024):.2f} MB exceeds 3 MB limit",
        )

    def test_negative_constraints_in_brand_kit(self):
        """Verifies zero prices, zero location/remote mentions, verified portrait, and untracked CV_gen."""
        # 1. Price patterns
        price_patterns = [
            r"€",
            r"\$",
            r"\bEUR\b",
            r"day\s*rate",
            r"daily\s*rate",
            r"tarifa\s*diaria",
            r"\bretainer\b",
            r"cuota\s*mensual",
            r"\bprecio\b",
        ]

        # 2. Location & remote patterns
        location_patterns = [
            r"mallorca",
            r"remote[\s-]first",
            r"100%\s*remote",
            r"island\s*base",
            r"barcelona\s*on[\s-]site",
            r"barcelona",
            r"baleares",
        ]

        # Scan all text/svg files in brand/
        forbidden_role_patterns = [
            r"direcci[oó]n\s+de\s+datos",
            r"fractional",
            r"fraccional",
            r"head\s+of\s+data",
        ]
        for p in BRAND_DIR.rglob("*"):
            if p.is_file() and p.suffix in {".html", ".css", ".js", ".svg"}:
                content = p.read_text(encoding="utf-8")
                for pat in price_patterns:
                    matches = re.findall(pat, content, re.IGNORECASE)
                    self.assertFalse(
                        matches,
                        f"Price/rate violation '{pat}' in {p.relative_to(REPO_ROOT)}: {matches}",
                    )
                for pat in location_patterns:
                    matches = re.findall(pat, content, re.IGNORECASE)
                    self.assertFalse(
                        matches,
                        f"Location/remote violation '{pat}' in {p.relative_to(REPO_ROOT)}: {matches}",
                    )
                for pat in forbidden_role_patterns:
                    matches = re.findall(pat, content, re.IGNORECASE)
                    self.assertFalse(
                        matches,
                        f"Outdated non-Opción-B role violation '{pat}' in {p.relative_to(REPO_ROOT)}: {matches}",
                    )

        # 3. Portrait verification
        portrait_path = BRAND_DIR / "assets" / "img" / "gabriel.jpg"
        self.assertTrue(portrait_path.is_file(), "Verified portrait gabriel.jpg missing")

        # 4. CV_gen untracked in git
        git_bin = shutil.which("git") or (
            r"C:\Program Files\Git\cmd\git.exe"
            if os.path.exists(r"C:\Program Files\Git\cmd\git.exe")
            else None
        )
        if git_bin:
            res = subprocess.run(
                [git_bin, "status", "--porcelain", "CV_gen"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(
                res.stdout.strip(),
                "",
                f"CV_gen tracked or staged in git: {res.stdout}",
            )
            res_ignore = subprocess.run(
                [git_bin, "check-ignore", "CV_gen/"],
                cwd=str(REPO_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_ignore.returncode, 0, "CV_gen/ is not ignored by git")

    def test_headless_responsive_audit(self):
        """Verifies responsive rendering at 375, 768, 1440px with 0 overflow, 0 console errors, 0 404s."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        viewports = [
            {"name": "mobile", "width": 375, "height": 812, "mobile": True},
            {"name": "tablet", "width": 768, "height": 1024, "mobile": False},
            {"name": "desktop", "width": 1440, "height": 900, "mobile": False},
        ]

        for vp in viewports:
            self.driver.set_viewport(vp["width"], vp["height"], vp["mobile"])
            self.driver.navigate(url)
            time.sleep(1.2)

            scroll_w = self.driver.evaluate("document.documentElement.scrollWidth")
            inner_w = self.driver.evaluate("window.innerWidth")
            self.assertLessEqual(
                scroll_w,
                inner_w,
                f"Horizontal overflow detected at {vp['name']} ({vp['width']}px): scrollWidth {scroll_w} > innerWidth {inner_w}",
            )

            self.assertEqual(
                len(self.driver.console_errors),
                0,
                f"Console errors at {vp['name']} ({vp['width']}px): {self.driver.console_errors}",
            )

            self.assertEqual(
                len(self.driver.network_failures),
                0,
                f"Network failures at {vp['name']} ({vp['width']}px): {self.driver.network_failures}",
            )

            all_images_loaded = self.driver.evaluate(
                "Array.from(document.images).every(img => img.complete && img.naturalWidth > 0)"
            )
            self.assertTrue(
                all_images_loaded,
                f"Some images failed to load at {vp['name']} ({vp['width']}px)",
            )

    def test_headless_interactive_controls(self):
        """Verifies interactive proposal switching, 3D card flip, hex copy toast, and download paths."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(url)
        for _ in range(30):
            ready = self.driver.evaluate("typeof window.brandKit !== 'undefined'")
            if ready:
                break
            time.sleep(0.1)

        # 1. Proposal theme switching (p2, p3, p4)
        for p in ["p2", "p3", "p4"]:
            self.driver.evaluate(
                f"document.querySelector('[data-proposal-target=\"{p}\"]').click()"
            )
            time.sleep(0.3)
            current_p = self.driver.evaluate(
                "document.documentElement.getAttribute('data-proposal')"
            )
            self.assertEqual(
                current_p,
                p,
                f"Proposal switcher failed to set active proposal to {p}",
            )

        # 2. 3D Card flip toggle
        self.driver.evaluate("document.getElementById('btnFlipCard').click()")
        is_flipped = self.driver.evaluate(
            "document.querySelector('.bizcard-inner').classList.contains('is-flipped')"
        )
        self.assertTrue(is_flipped, "Business card failed to flip on #btnFlipCard click")
        aria_pressed = self.driver.evaluate(
            "document.getElementById('btnFlipCard').getAttribute('aria-pressed')"
        )
        self.assertEqual(aria_pressed, "true", "Aria-pressed not updated on flip button")

        # 3. Hex copy swatch toast notification (with strict DOM isolation and payload verification)
        # Step 3a: Explicitly dismiss and clear any leftover toast from previous steps
        self.driver.evaluate("""
            (() => {
                const toast = document.getElementById('brandToast');
                if (toast) {
                    toast.classList.remove('show');
                    toast.setAttribute('aria-hidden', 'true');
                    toast.textContent = '';
                }
            })()
        """)
        toast_isolated = self.driver.evaluate(
            "!document.getElementById('brandToast') || !document.getElementById('brandToast').classList.contains('show')"
        )
        self.assertTrue(toast_isolated, "Failed to isolate toast state prior to swatch test")

        # Step 3b: Retrieve target swatch HEX value
        swatch_hex = self.driver.evaluate(
            "document.querySelector('[data-copy-hex]').getAttribute('data-copy-hex')"
        )
        self.assertTrue(swatch_hex, "Swatch data-copy-hex attribute missing")

        # Step 3c: Click swatch and assert toast appearance with matching payload
        self.driver.evaluate("document.querySelector('[data-copy-hex]').click()")
        time.sleep(0.3)
        toast_state = self.driver.evaluate("""
            (() => {
                const toast = document.getElementById('brandToast');
                return {
                    hasShow: toast ? toast.classList.contains('show') : false,
                    text: toast ? toast.textContent.trim() : '',
                    ariaHidden: toast ? toast.getAttribute('aria-hidden') : 'true'
                };
            })()
        """)
        self.assertTrue(toast_state["hasShow"], "Toast #brandToast failed to activate on swatch click")
        self.assertEqual(toast_state["ariaHidden"], "false", "Toast aria-hidden is not false when visible")
        self.assertIn(
            swatch_hex.upper(),
            toast_state["text"].upper(),
            f"Toast text '{toast_state['text']}' did not contain clicked swatch HEX '{swatch_hex}'",
        )

        # 4. Email Signature interaction (Language toggle & Copy actions)
        self.driver.evaluate("document.querySelector('[data-signature-lang=\"en\"]').click()")
        time.sleep(0.2)
        en_preview = self.driver.evaluate("document.getElementById('signaturePreview').textContent")
        self.assertIn("Data Partner · Data Strategy, Analytics & Automation", en_preview)

        self.driver.evaluate("document.querySelector('[data-signature-lang=\"es\"]').click()")
        time.sleep(0.2)
        es_preview = self.driver.evaluate("document.getElementById('signaturePreview').textContent")
        self.assertIn("Data Partner · Estrategia, Analítica y Automatización", es_preview)

        # Clear toast and test visual copy
        self.driver.evaluate("""
            const t = document.getElementById('brandToast');
            if (t) { t.classList.remove('show'); t.textContent = ''; }
        """)
        self.driver.evaluate("document.getElementById('btnCopyVisualSig').click()")
        time.sleep(0.3)
        toast_vis = self.driver.evaluate("document.getElementById('brandToast').textContent")
        self.assertIn("copiad", toast_vis.lower())

        # Clear toast and test HTML raw copy
        self.driver.evaluate("""
            const t = document.getElementById('brandToast');
            if (t) { t.classList.remove('show'); t.textContent = ''; }
        """)
        self.driver.evaluate("document.getElementById('btnCopyHtmlSig').click()")
        time.sleep(0.3)
        toast_html = self.driver.evaluate("document.getElementById('brandToast').textContent")
        self.assertIn("copiad", toast_html.lower())
        self.assertNotIn("error", toast_html.lower())

        # 5. Multi-proposal download links integrity across all 4 proposals
        for p in PROPOSALS:
            self.driver.evaluate(f"window.brandKit.setProposal('{p}', false)")
            time.sleep(0.2)
            downloads = self.driver.evaluate(
                "Array.from(document.querySelectorAll('a[download]')).map(a => ({href: a.getAttribute('href'), download: a.getAttribute('download')}))"
            )
            self.assertGreaterEqual(len(downloads), 15, f"Expected >= 15 download links for proposal {p}")
            for link in downloads:
                rel_href = link["href"]
                dl_name = link["download"]
                self.assertFalse(rel_href.startswith("/"), f"Root-leading href in download: {rel_href}")
                self.assertFalse(rel_href.startswith("http"), f"External href in download: {rel_href}")
                target_path = (BRAND_DIR / rel_href).resolve()
                self.assertTrue(
                    target_path.is_file(),
                    f"[{p}] Download link targets missing file: {rel_href} (resolved {target_path})",
                )
                self.assertGreater(
                    target_path.stat().st_size,
                    200,
                    f"[{p}] Download file suspiciously small (< 200 bytes): {target_path.name}",
                )
                self.assertEqual(
                    target_path.name,
                    dl_name,
                    f"[{p}] Download attribute filename mismatch: target {target_path.name} vs download {dl_name}",
                )

    def test_a4_report_template_audit(self):
        """Audits A4 report template for responsive layout, zero console errors, zero 404s, and negative constraints."""
        a4_url = f"http://127.0.0.1:{self.server.port}/brand/templates/a4-report.html"
        viewports = [
            {"name": "mobile", "width": 375, "height": 812, "mobile": True},
            {"name": "tablet", "width": 768, "height": 1024, "mobile": False},
            {"name": "desktop", "width": 1440, "height": 900, "mobile": False},
        ]

        for vp in viewports:
            self.driver.set_viewport(vp["width"], vp["height"], vp["mobile"])
            self.driver.navigate(a4_url)
            time.sleep(0.8)

            scroll_w = self.driver.evaluate("document.documentElement.scrollWidth")
            inner_w = self.driver.evaluate("window.innerWidth")
            self.assertLessEqual(
                scroll_w,
                inner_w,
                f"Horizontal overflow on A4 report at {vp['name']} ({scroll_w} > {inner_w})",
            )

            self.assertEqual(
                len(self.driver.console_errors),
                0,
                f"Console errors on A4 template at {vp['name']}: {self.driver.console_errors}",
            )
            self.assertEqual(
                len(self.driver.network_failures),
                0,
                f"Network failures on A4 template at {vp['name']}: {self.driver.network_failures}",
            )

        # Check negative constraints in template content
        a4_content = (BRAND_DIR / "templates" / "a4-report.html").read_text(encoding="utf-8")
        for forbidden in ["€", r"\$", r"\bEUR\b", "mallorca", "barcelona", r"100%\s*remote", "island base"]:
            matches = re.findall(forbidden, a4_content, re.IGNORECASE)
            self.assertFalse(matches, f"Negative constraint violation '{forbidden}' in a4-report.html: {matches}")


if __name__ == "__main__":
    unittest.main()
