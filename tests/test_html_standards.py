"""
tests/test_html_standards.py - HTML standards, SEO, accessibility, link crawling, and performance budget test suite.

Verifies:
1. Exactly one <h1> per version.
2. Presence and validity of <title>, <meta name="description">, and Open Graph tags (og:title, og:description, og:image).
3. All <img> tags have valid alt text.
4. Internal link crawl: zero broken local links or anchors.
5. Self-contained relative URLs: no root-leading slashes (/assets/, /css/, /img/, etc.).
6. Total transfer weight per page is under 3MB.
"""

import os
import re
import unittest
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"

VERSIONS = ["vA", "vB", "vD", "vE", "vF"]
MAX_TRANSFER_WEIGHT_BYTES = 3 * 1024 * 1024  # 3 MB


def get_version_html(v: str) -> str:
    path = WEB_DIR / v / "index.html"
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


class TestHtmlStandards(unittest.TestCase):
    """Test suite verifying technical HTML standards, accessibility, SEO, links, and weight budget."""

    def test_single_h1(self):
        """Each version must have exactly one <h1> element."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")
            h1_tags = soup.find_all("h1")
            self.assertEqual(
                len(h1_tags), 1,
                f"Version {v} must have exactly 1 <h1>, but has {len(h1_tags)}: {[h.get_text(strip=True) for h in h1_tags]}"
            )
            h1_text = h1_tags[0].get_text(strip=True)
            self.assertGreater(len(h1_text), 5, f"Version {v} <h1> text is too short: '{h1_text}'")

    def test_seo_title_and_meta_description(self):
        """Each version must have a descriptive <title> and <meta name="description">."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")
            
            # Title
            title_tag = soup.find("title")
            self.assertIsNotNone(title_tag, f"Version {v} is missing <title> tag")
            title_text = title_tag.get_text(strip=True)
            self.assertGreater(
                len(title_text), 10,
                f"Version {v} <title> must be descriptive (length >= 10): '{title_text}'"
            )

            # Meta description
            meta_desc = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
            self.assertIsNotNone(meta_desc, f"Version {v} is missing <meta name='description'>")
            desc_content = meta_desc.get("content", "").strip()
            self.assertGreater(
                len(desc_content), 20,
                f"Version {v} meta description must be substantial (length >= 20): '{desc_content}'"
            )

    def test_open_graph_tags(self):
        """Each version must have Open Graph tags (og:title, og:description, og:image)."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")

            og_title = soup.find("meta", property=re.compile(r"^og:title$", re.I))
            self.assertIsNotNone(og_title, f"Version {v} is missing og:title")
            self.assertTrue(bool(og_title.get("content", "").strip()), f"Version {v} og:title is empty")

            og_desc = soup.find("meta", property=re.compile(r"^og:description$", re.I))
            self.assertIsNotNone(og_desc, f"Version {v} is missing og:description")
            self.assertTrue(bool(og_desc.get("content", "").strip()), f"Version {v} og:description is empty")

            og_image = soup.find("meta", property=re.compile(r"^og:image$", re.I))
            self.assertIsNotNone(og_image, f"Version {v} is missing og:image")
            self.assertTrue(bool(og_image.get("content", "").strip()), f"Version {v} og:image is empty")

    def test_image_alt_text(self):
        """All <img> tags must have valid alt attributes."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")
            images = soup.find_all("img")
            self.assertGreater(len(images), 0, f"Version {v} has no <img> tags")
            for img in images:
                src = img.get("src", "")
                self.assertIn("alt", img.attrs, f"Version {v} image '{src}' is missing 'alt' attribute")
                is_decorative = img.get("role") == "presentation" or img.get("aria-hidden") == "true"
                if not is_decorative:
                    self.assertGreater(
                        len(img["alt"].strip()), 0,
                        f"Version {v} non-decorative image '{src}' has empty alt attribute"
                    )

    def test_self_contained_relative_urls(self):
        """No root-leading slashes (/assets/, /css/, /img/) allowed in version pages."""
        for v in VERSIONS:
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")

            url_attributes = [
                ("a", "href"),
                ("link", "href"),
                ("script", "src"),
                ("img", "src"),
                ("source", "srcset"),
            ]
            for tag_name, attr in url_attributes:
                for el in soup.find_all(tag_name):
                    val = el.get(attr)
                    if not val:
                        continue
                    if val.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                        continue
                    
                    self.assertFalse(
                        val.startswith("/"),
                        f"Version {v} has root-leading URL '{val}' in <{tag_name} {attr}>. Must be strictly relative!"
                    )

    def test_internal_links_and_anchors_crawl(self):
        """Crawl all local internal links and anchors to verify zero broken links."""
        for v in VERSIONS:
            v_dir = WEB_DIR / v
            html = get_version_html(v)
            self.assertTrue(bool(html), f"Version {v} index.html is missing or empty")
            soup = BeautifulSoup(html, "html.parser")

            all_ids = {el.get("id") for el in soup.find_all(id=True)}

            # 1. Check all local anchors (<a href="#...">)
            for a in soup.find_all("a"):
                href = a.get("href", "").strip()
                if not href:
                    continue
                if href.startswith("#") and href != "#":
                    anchor_id = href[1:]
                    self.assertIn(
                        anchor_id, all_ids,
                        f"Version {v} has broken anchor target '{href}'"
                    )
                elif not href.startswith(("http://", "https://", "mailto:", "tel:", "javascript:")):
                    target_file = (v_dir / href).resolve()
                    self.assertTrue(
                        target_file.exists(),
                        f"Version {v} link '{href}' points to non-existent file {target_file}"
                    )

            # 2. Check all CSS stylesheets
            for link in soup.find_all("link", rel=lambda r: r and "stylesheet" in r):
                href = link.get("href", "").strip()
                if href.startswith(("http://", "https://")):
                    continue
                target_file = (v_dir / href).resolve()
                self.assertTrue(
                    target_file.exists(),
                    f"Version {v} stylesheet '{href}' does not exist on disk: {target_file}"
                )

            # 3. Check all scripts
            for script in soup.find_all("script", src=True):
                src = script.get("src", "").strip()
                if src.startswith(("http://", "https://")):
                    continue
                target_file = (v_dir / src).resolve()
                self.assertTrue(
                    target_file.exists(),
                    f"Version {v} script '{src}' does not exist on disk: {target_file}"
                )

            # 4. Check all images
            for img in soup.find_all("img", src=True):
                src = img.get("src", "").strip()
                if src.startswith(("http://", "https://", "data:")):
                    continue
                target_file = (v_dir / src).resolve()
                self.assertTrue(
                    target_file.exists(),
                    f"Version {v} image '{src}' does not exist on disk: {target_file}"
                )

    def test_total_page_transfer_weight_budget(self):
        """Verify total transfer weight of index.html and all local assets is under 3MB."""
        for v in VERSIONS:
            v_dir = WEB_DIR / v
            html_path = v_dir / "index.html"
            self.assertTrue(html_path.exists(), f"Version {v} index.html does not exist")
            total_bytes = html_path.stat().st_size

            soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
            seen_files = {html_path.resolve()}

            for tag, attr in [("link", "href"), ("script", "src"), ("img", "src")]:
                for el in soup.find_all(tag):
                    val = el.get(attr, "").strip()
                    if not val or val.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                        continue
                    file_path = (v_dir / val).resolve()
                    if file_path.exists() and file_path not in seen_files:
                        seen_files.add(file_path)
                        total_bytes += file_path.stat().st_size

            self.assertLess(
                total_bytes, MAX_TRANSFER_WEIGHT_BYTES,
                f"Version {v} total asset weight ({total_bytes} bytes / {total_bytes / (1024*1024):.2f}MB) exceeds 3MB budget!"
            )


if __name__ == "__main__":
    unittest.main()
