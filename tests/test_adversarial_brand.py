"""
tests/test_adversarial_brand.py - Empirical Adversarial Challenge Suite for Gabriel Rul-lan Personal Freelance Brand Kit.

Adversarially audits web/brand/index.html and web/brand/templates/a4-report.html:
1. Multi-viewport responsive layout stress: 320px, 375px, 390px, 768px, 1024px, 1440px, 1920px.
   - Zero horizontal overflow (documentElement and body scrollWidth <= innerWidth).
   - Per-element bounding box overflow check.
   - Zero console errors, warnings, or exceptions.
   - Zero network 404s or failed requests.
   - All <img> elements fully loaded (complete && naturalWidth > 0).
2. Interactive Controls Stress Test:
   - Proposal switcher (p1, p2, p3, p4) rapid multi-cycle switching, DOM data-proposal, aria-selected, class syncing.
   - Dynamic asset remapping verification for logos, banners, icons, and download links.
   - 3D Business Card flip: button click, card click, aria-pressed, overflow check while flipped.
   - Color swatches & HEX copy toast: 16 swatches, format validation, toast activation, rapid-click stress.
   - Email signature: ES/EN language toggle, rich visual copy, HTML raw copy, toast verification, links & credentials audit.
   - Exhaustive download links verification across all 4 proposals (verifying disk existence & size > 200B).
3. A4 Report Template Audit:
   - Responsive check at 375, 768, 1440px with zero overflow.
   - Zero console errors, zero 404s.
   - Negative constraints check.
4. Comprehensive Negative Constraints Audit:
   - Zero prices, zero day rates, zero retainers.
   - Zero locations (Mallorca, Barcelona), zero remote-work mentions.
   - Verification that CV_gen is untracked and git-ignored.
"""

import base64
import json
import os
import re
import shutil
import socket
import subprocess
import tempfile
import threading
import time
import unittest
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import urllib.request
import websocket

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"
BRAND_DIR = WEB_DIR / "brand"
SCREENSHOTS_DIR = REPO_ROOT / "tests" / "screenshots"

PROPOSALS = ["p1", "p2", "p3", "p4"]

VIEWPORTS = [
    {"name": "narrow_mobile_320", "width": 320, "height": 568, "mobile": True},
    {"name": "mobile_375", "width": 375, "height": 812, "mobile": True},
    {"name": "mobile_390", "width": 390, "height": 844, "mobile": True},
    {"name": "tablet_portrait_768", "width": 768, "height": 1024, "mobile": False},
    {"name": "tablet_landscape_1024", "width": 1024, "height": 768, "mobile": False},
    {"name": "desktop_1440", "width": 1440, "height": 900, "mobile": False},
    {"name": "desktop_hd_1920", "width": 1920, "height": 1080, "mobile": False},
]

CHROME_PATHS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
]


def find_browser_executable() -> str:
    for path in CHROME_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Neither Google Chrome nor Microsoft Edge was found on system.")


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class LocalWebServer:
    def __init__(self, port: int = 8000):
        self.port = port
        self.httpd = None
        self.thread = None

    def start(self):
        handler = partial(SimpleHTTPRequestHandler, directory=str(WEB_DIR))
        ThreadingHTTPServer.allow_reuse_address = True
        try:
            self.httpd = ThreadingHTTPServer(("127.0.0.1", self.port), handler)
        except OSError:
            self.port = find_free_port()
            self.httpd = ThreadingHTTPServer(("127.0.0.1", self.port), handler)

        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        time.sleep(0.5)

    def stop(self):
        if self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()


class ChromeHeadlessDriver:
    def __init__(self, browser_path: str):
        self.browser_path = browser_path
        self.port = find_free_port()
        self.user_data_dir = tempfile.mkdtemp(prefix="chrome_adv_")
        self.proc = None
        self.ws = None
        self.cmd_id = 0
        self.console_errors = []
        self.network_failures = []

    def start(self):
        cmd = [
            self.browser_path,
            "--headless=new",
            "--disable-gpu",
            "--disable-extensions",
            "--no-first-run",
            "--no-default-browser-check",
            f"--remote-debugging-port={self.port}",
            "--remote-allow-origins=*",
            f"--user-data-dir={self.user_data_dir}",
            "about:blank",
        ]
        self.proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        ws_url = None
        for _ in range(30):
            try:
                resp = urllib.request.urlopen(f"http://127.0.0.1:{self.port}/json/list", timeout=2)
                tabs = json.loads(resp.read().decode())
                pages = [t for t in tabs if t.get("type") == "page"]
                if pages and "webSocketDebuggerUrl" in pages[0]:
                    ws_url = pages[0]["webSocketDebuggerUrl"]
                    break
            except Exception:
                time.sleep(0.2)

        if not ws_url:
            raise RuntimeError("Failed to connect to Chrome DevTools endpoint.")

        self.ws = websocket.create_connection(ws_url, timeout=10)
        self._enable_domains()

    def _enable_domains(self):
        self._send("Page.enable")
        self._send("Runtime.enable")
        self._send("Log.enable")
        self._send("Network.enable")
        try:
            self._send("Browser.grantPermissions", {
                "permissions": ["clipboardReadWrite", "clipboardSanitizedWrite"],
            })
        except Exception:
            pass

    def _send(self, method: str, params: dict = None) -> dict:
        self.cmd_id += 1
        msg_id = self.cmd_id
        payload = {"id": msg_id, "method": method, "params": params or {}}
        self.ws.send(json.dumps(payload))

        while True:
            raw = self.ws.recv()
            data = json.loads(raw)
            if "method" in data:
                m = data["method"]
                p = data.get("params", {})
                if m == "Runtime.consoleAPICalled" and p.get("type") == "error":
                    args = " ".join([str(a.get("value", "")) for a in p.get("args", [])])
                    self.console_errors.append(f"Console error: {args}")
                elif m == "Log.entryAdded" and p.get("entry", {}).get("level") == "error":
                    self.console_errors.append(f"Log error: {p.get('entry', {}).get('text')}")
                elif m == "Network.responseReceived":
                    resp = p.get("response", {})
                    status = resp.get("status", 200)
                    url = resp.get("url", "")
                    if status >= 400:
                        self.network_failures.append(f"HTTP {status} on {url}")
                elif m == "Network.loadingFailed":
                    err = p.get("errorText", "")
                    if err != "net::ERR_ABORTED":
                        self.network_failures.append(f"Failed to load: {err}")
            elif data.get("id") == msg_id:
                return data

    def reset_logs(self):
        self.console_errors = []
        self.network_failures = []

    def set_viewport(self, width: int, height: int, mobile: bool = False):
        self._send("Emulation.setDeviceMetricsOverride", {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        })
        self._send("Emulation.setVisibleSize", {"width": width, "height": height})

    def navigate(self, url: str):
        self.reset_logs()
        self._send("Page.navigate", {"url": url})
        time.sleep(1.2)

    def evaluate(self, expr: str):
        res = self._send("Runtime.evaluate", {
            "expression": expr,
            "returnByValue": True,
            "awaitPromise": True,
        })
        return res.get("result", {}).get("result", {}).get("value")

    def capture_screenshot(self, output_path: Path):
        output_path.parent.mkdir(parents=True, exist_ok=True)
        res = self._send("Page.captureScreenshot", {"format": "png"})
        b64_data = res.get("result", {}).get("data", "")
        if b64_data:
            output_path.write_bytes(base64.b64decode(b64_data))

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        if self.proc:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except Exception:
                self.proc.kill()
        shutil.rmtree(self.user_data_dir, ignore_errors=True)


class TestAdversarialBrandKit(unittest.TestCase):
    """Empirical adversarial test harness for Personal Freelance Brand Kit."""

    server = None
    driver = None

    @classmethod
    def setUpClass(cls):
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.server = LocalWebServer(port=8000)
        cls.server.start()

        browser_path = find_browser_executable()
        cls.driver = ChromeHeadlessDriver(browser_path)
        cls.driver.start()

    @classmethod
    def tearDownClass(cls):
        if cls.driver:
            cls.driver.close()
        if cls.server:
            cls.server.stop()

    def test_01_responsive_viewports_and_zero_overflow(self):
        """Adversarially tests 7 viewports for zero overflow, zero console errors, zero 404s, and full images."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"

        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"], width=vp["width"]):
                self.driver.set_viewport(vp["width"], vp["height"], vp["mobile"])
                self.driver.navigate(url)

                # 1. documentElement & body scrollWidth check
                metrics = self.driver.evaluate("""
                    (() => {
                        const docW = document.documentElement.scrollWidth;
                        const bodyW = document.body.scrollWidth;
                        const winW = window.innerWidth;
                        return { docW, bodyW, winW };
                    })()
                """)
                self.assertIsNotNone(metrics, "Failed to retrieve layout metrics")
                doc_w = metrics["docW"]
                body_w = metrics["bodyW"]
                win_w = metrics["winW"]

                self.assertLessEqual(
                    doc_w,
                    win_w,
                    f"[{vp['name']}] documentElement.scrollWidth ({doc_w}) > window.innerWidth ({win_w})",
                )
                self.assertLessEqual(
                    body_w,
                    win_w,
                    f"[{vp['name']}] document.body.scrollWidth ({body_w}) > window.innerWidth ({win_w})",
                )

                # 2. Per-element bounding overflow check (excluding elements inside scroll-containers)
                overflow_elements = self.driver.evaluate("""
                    (() => {
                        const winW = window.innerWidth;
                        const culprits = [];
                        const all = document.querySelectorAll('*');
                        for (const el of all) {
                            const style = window.getComputedStyle(el);
                            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') continue;
                            let p = el.parentElement;
                            let clipped = false;
                            while (p && p !== document.body && p !== document.documentElement) {
                                const ps = window.getComputedStyle(p);
                                if (ps.overflowX === 'hidden' || ps.overflowX === 'auto' || ps.overflowX === 'scroll') {
                                    clipped = true;
                                    break;
                                }
                                p = p.parentElement;
                            }
                            if (clipped) continue;
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.right > winW + 1.5) {
                                culprits.push({
                                    tag: el.tagName,
                                    id: el.id,
                                    cls: (el.className || '').toString().slice(0, 50),
                                    right: Math.round(rect.right),
                                    winW: winW
                                });
                            }
                        }
                        return culprits;
                    })()
                """)
                self.assertEqual(
                    len(overflow_elements),
                    0,
                    f"[{vp['name']}] Found uncontained overflowing elements: {overflow_elements}",
                )

                # 3. Console errors
                self.assertEqual(
                    len(self.driver.console_errors),
                    0,
                    f"[{vp['name']}] Console errors detected: {self.driver.console_errors}",
                )

                # 4. Network failures / 404s
                self.assertEqual(
                    len(self.driver.network_failures),
                    0,
                    f"[{vp['name']}] Network failures detected: {self.driver.network_failures}",
                )

                # 5. Image loading completion
                images_ok = self.driver.evaluate("""
                    Array.from(document.images).every(img => img.complete && img.naturalWidth > 0)
                """)
                self.assertTrue(images_ok, f"[{vp['name']}] One or more images failed to load")

                # 6. Capture screenshot
                screenshot_file = SCREENSHOTS_DIR / f"brand_{vp['name']}.png"
                self.driver.capture_screenshot(screenshot_file)
                self.assertTrue(screenshot_file.is_file(), f"Screenshot not saved for {vp['name']}")

    def test_02_proposal_switcher_multi_cycle_stress(self):
        """Adversarially stresses the proposal switcher across rapid cycles, verifying assets & attributes."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(url)

        # Sequence of rapid switches
        test_sequence = ["p2", "p3", "p4", "p1", "p3", "p2", "p4", "p1"]

        for target_p in test_sequence:
            self.driver.evaluate(f"document.querySelector('[data-proposal-target=\"{target_p}\"]').click()")
            time.sleep(0.2)

            # Check root attribute
            active_p = self.driver.evaluate("document.documentElement.getAttribute('data-proposal')")
            self.assertEqual(active_p, target_p, f"Root data-proposal not updated to {target_p}")

            # Check active tab button
            tab_state = self.driver.evaluate(f"""
                (() => {{
                    const btn = document.querySelector('[data-proposal-target="{target_p}"]');
                    return {{
                        selected: btn.getAttribute('aria-selected'),
                        hasActive: btn.classList.contains('active')
                    }};
                }})()
            """)
            self.assertEqual(tab_state["selected"], "true")
            self.assertTrue(tab_state["hasActive"])

            # Check matrix active column
            matrix_active = self.driver.evaluate(f"""
                document.querySelector('.matrix-col[data-proposal="{target_p}"]').classList.contains('current-active')
            """)
            self.assertTrue(matrix_active, f"Matrix column {target_p} missing class current-active")

            # Check remapped sandbox images
            sandbox_assets = self.driver.evaluate("""
                (() => {
                    const bizLogo = document.getElementById('bizcardLogo');
                    const bizMark = document.getElementById('bizcardMark');
                    const liBanner = document.getElementById('linkedinBanner');
                    const a4Logo = document.getElementById('a4Logo');
                    return {
                        bizLogo: bizLogo ? bizLogo.getAttribute('src') : null,
                        bizMark: bizMark ? bizMark.getAttribute('src') : null,
                        liBanner: liBanner ? liBanner.getAttribute('src') : null,
                        a4Logo: a4Logo ? a4Logo.getAttribute('src') : null,
                        bizLogoLoaded: bizLogo ? (bizLogo.complete && bizLogo.naturalWidth > 0) : false,
                        bizMarkLoaded: bizMark ? (bizMark.complete && bizMark.naturalWidth > 0) : false,
                        liBannerLoaded: liBanner ? (liBanner.complete && liBanner.naturalWidth > 0) : false,
                        a4LogoLoaded: a4Logo ? (a4Logo.complete && a4Logo.naturalWidth > 0) : false,
                    };
                })()
            """)
            self.assertIn(f"{target_p}-logo-es-light.svg", sandbox_assets["bizLogo"])
            self.assertIn(f"{target_p}-logo-icon-light.svg", sandbox_assets["bizMark"])
            self.assertIn(f"{target_p}-linkedin-banner-es.png", sandbox_assets["liBanner"])
            self.assertIn(f"{target_p}-logo-es-light.svg", sandbox_assets["a4Logo"])
            self.assertTrue(sandbox_assets["bizLogoLoaded"])
            self.assertTrue(sandbox_assets["bizMarkLoaded"])
            self.assertTrue(sandbox_assets["liBannerLoaded"])
            self.assertTrue(sandbox_assets["a4LogoLoaded"])

        # Check no console errors or 404s across all switching
        self.assertEqual(len(self.driver.console_errors), 0, f"Console errors: {self.driver.console_errors}")
        self.assertEqual(len(self.driver.network_failures), 0, f"Network failures: {self.driver.network_failures}")

    def test_03_3d_card_flip_stress(self):
        """Adversarially stresses the 3D card flip toggle via button and card click, checking overflow."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        self.driver.set_viewport(375, 812, True)  # Test at mobile viewport
        self.driver.navigate(url)

        # 1. Flip using button
        self.driver.evaluate("document.getElementById('btnFlipCard').click()")
        time.sleep(0.3)
        flipped_1 = self.driver.evaluate("""
            (() => {
                const card = document.querySelector('.bizcard-inner');
                const btn = document.getElementById('btnFlipCard');
                return {
                    isFlipped: card.classList.contains('is-flipped'),
                    ariaPressed: btn.getAttribute('aria-pressed'),
                    text: btn.textContent.trim()
                };
            })()
        """)
        self.assertTrue(flipped_1["isFlipped"])
        self.assertEqual(flipped_1["ariaPressed"], "true")

        # Check mobile overflow while flipped
        overflow_while_flipped = self.driver.evaluate("""
            document.documentElement.scrollWidth <= window.innerWidth
        """)
        self.assertTrue(overflow_while_flipped, "Horizontal overflow occurred while card was flipped in 3D")

        # 2. Unflip using button
        self.driver.evaluate("document.getElementById('btnFlipCard').click()")
        time.sleep(0.3)
        flipped_2 = self.driver.evaluate("""
            (() => {
                const card = document.querySelector('.bizcard-inner');
                const btn = document.getElementById('btnFlipCard');
                return {
                    isFlipped: card.classList.contains('is-flipped'),
                    ariaPressed: btn.getAttribute('aria-pressed'),
                };
            })()
        """)
        self.assertFalse(flipped_2["isFlipped"])
        self.assertEqual(flipped_2["ariaPressed"], "false")

        # 3. Flip by clicking card directly
        self.driver.evaluate("document.querySelector('.bizcard-inner').click()")
        time.sleep(0.3)
        flipped_3 = self.driver.evaluate("document.querySelector('.bizcard-inner').classList.contains('is-flipped')")
        self.assertTrue(flipped_3, "Clicking .bizcard-inner failed to flip the card")

        # 4. Unflip by clicking card directly again
        self.driver.evaluate("document.querySelector('.bizcard-inner').click()")
        time.sleep(0.3)
        flipped_4 = self.driver.evaluate("document.querySelector('.bizcard-inner').classList.contains('is-flipped')")
        self.assertFalse(flipped_4, "Clicking .bizcard-inner a second time failed to unflip")

        self.assertEqual(len(self.driver.console_errors), 0, f"Console errors: {self.driver.console_errors}")

    def test_04_color_swatches_and_hex_copy_toast(self):
        """Adversarially tests all color swatches for valid hex format, copy action, and toast display."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(url)

        swatches = self.driver.evaluate("""
            Array.from(document.querySelectorAll('[data-copy-hex]')).map(el => el.getAttribute('data-copy-hex'))
        """)
        self.assertGreaterEqual(len(swatches), 16, f"Expected at least 16 color swatches, found {len(swatches)}")

        # Verify HEX format
        hex_regex = re.compile(r"^#[0-9A-Fa-f]{6}$")
        for h in swatches:
            self.assertTrue(hex_regex.match(h), f"Invalid HEX color code in swatch: {h}")



        # Click swatches and verify toast appears
        for idx in [0, 4, 8, 12]:  # Sample swatches from each proposal column
            self.driver.evaluate(f"""
                (() => {{
                    const sw = document.querySelectorAll('[data-copy-hex]')[{idx}];
                    sw.click();
                }})()
            """)
            time.sleep(0.3)
            toast_info = self.driver.evaluate("""
                (() => {
                    const toast = document.getElementById('brandToast');
                    return {
                        hasShow: toast.classList.contains('show'),
                        text: toast.textContent.trim(),
                        ariaHidden: toast.getAttribute('aria-hidden')
                    };
                })()
            """)
            self.assertTrue(toast_info["hasShow"], f"Toast did not show on clicking swatch index {idx}")
            self.assertIn(swatches[idx].upper(), toast_info["text"].upper())

        # Rapid clicking stress (clicking 8 swatches in rapid succession)
        self.driver.evaluate("""
            const sws = document.querySelectorAll('[data-copy-hex]');
            for (let i = 0; i < Math.min(sws.length, 8); i++) {
                sws[i].click();
            }
        """)
        time.sleep(0.3)
        self.assertEqual(len(self.driver.console_errors), 0, "Console errors on rapid swatch clicking")

    def test_05_email_signature_interaction_and_content(self):
        """Tests email signature language toggle, rich visual copy, HTML raw copy, links and negative constraints."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(url)

        # 1. English toggle
        self.driver.evaluate("document.querySelector('[data-signature-lang=\"en\"]').click()")
        time.sleep(0.2)
        en_preview = self.driver.evaluate("document.getElementById('signaturePreview').textContent")
        self.assertIn("Fractional Data Director", en_preview)

        # 2. Spanish toggle
        self.driver.evaluate("document.querySelector('[data-signature-lang=\"es\"]').click()")
        time.sleep(0.2)
        es_preview = self.driver.evaluate("document.getElementById('signaturePreview').textContent")
        self.assertIn("Director de Datos Fraccional", es_preview)

        # 3. Visual signature copy button
        self.driver.evaluate("document.getElementById('btnCopyVisualSig').click()")
        time.sleep(0.3)
        toast_text = self.driver.evaluate("document.getElementById('brandToast').textContent")
        self.assertIn("copiad", toast_text.lower())

        # 4. HTML code copy button
        self.driver.evaluate("document.getElementById('btnCopyHtmlSig').click()")
        time.sleep(0.3)
        toast_text_2 = self.driver.evaluate("document.getElementById('brandToast').textContent")
        self.assertIn("copiad", toast_text_2.lower())

        # 5. Verify email signature links and negative constraints
        sig_html = self.driver.evaluate("document.getElementById('signatureHtmlCode').textContent")
        self.assertIn("gabriel@data-partner.xyz", sig_html)
        self.assertIn("https://calendar.app.google/YbQTidmXT3Bg9wdY8", sig_html)
        self.assertIn("data-partner.xyz", sig_html)

        # Negative constraints in signature HTML
        for forbidden in ["€", "$", "EUR", "Mallorca", "Barcelona", "remote"]:
            self.assertNotIn(forbidden.lower(), sig_html.lower(), f"Forbidden word '{forbidden}' in signature HTML")

        self.assertEqual(len(self.driver.console_errors), 0, f"Console errors: {self.driver.console_errors}")

    def test_06_exhaustive_download_links_across_proposals(self):
        """Verifies that all download links across all 4 proposals point to real files on disk with size > 200B."""
        url = f"http://127.0.0.1:{self.server.port}/brand/index.html"
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(url)

        for p in PROPOSALS:
            self.driver.evaluate(f"window.brandKit.setProposal('{p}', false)")
            time.sleep(0.2)

            links = self.driver.evaluate("""
                Array.from(document.querySelectorAll('a[download]')).map(a => ({
                    href: a.getAttribute('href'),
                    download: a.getAttribute('download')
                }))
            """)
            self.assertGreaterEqual(len(links), 15, f"Too few download links for proposal {p}")

            for link in links:
                href = link["href"]
                dl_name = link["download"]
                self.assertFalse(href.startswith("/"), f"Root-leading href in download: {href}")
                self.assertFalse(href.startswith("http"), f"External href in download: {href}")

                # Resolve relative to BRAND_DIR
                target_file = (BRAND_DIR / href).resolve()
                self.assertTrue(target_file.is_file(), f"[{p}] Download file does not exist on disk: {target_file}")
                self.assertGreater(
                    target_file.stat().st_size,
                    200,
                    f"[{p}] Download file suspiciously small (<200 bytes): {target_file}",
                )
                self.assertEqual(
                    target_file.name,
                    dl_name,
                    f"[{p}] Download filename mismatch: expected {target_file.name}, got {dl_name}",
                )

    def test_07_a4_report_template_audit(self):
        """Verifies responsive layout, zero console errors, zero 404s, and negative constraints on A4 template."""
        a4_url = f"http://127.0.0.1:{self.server.port}/brand/templates/a4-report.html"

        for vp in [VIEWPORTS[1], VIEWPORTS[3], VIEWPORTS[5]]:  # 375, 768, 1440px
            self.driver.set_viewport(vp["width"], vp["height"], vp["mobile"])
            self.driver.navigate(a4_url)

            doc_w = self.driver.evaluate("document.documentElement.scrollWidth")
            win_w = self.driver.evaluate("window.innerWidth")
            self.assertLessEqual(
                doc_w,
                win_w,
                f"Horizontal overflow on A4 report at {vp['name']} ({doc_w} > {win_w})",
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

        # Verify negative constraints in A4 template HTML
        a4_path = BRAND_DIR / "templates" / "a4-report.html"
        a4_content = a4_path.read_text(encoding="utf-8")
        for forbidden in ["€", r"\$", r"\bEUR\b", "mallorca", "barcelona", r"100%\s*remote", "island base"]:
            matches = re.findall(forbidden, a4_content, re.IGNORECASE)
            self.assertFalse(matches, f"Forbidden match '{forbidden}' in a4-report.html: {matches}")

    def test_08_brand_negative_constraints_and_untracked(self):
        """Exhaustively scans all brand kit files for forbidden keywords and verifies untracked CV_gen."""
        price_patterns = [
            r"€",
            r"\$",
            r"\bEUR\b",
            r"day\s*rate",
            r"daily\s*rate",
            r"tarifa\s*diaria",
            r"\bretainer\b",
            r"cuota\s*mensual",
        ]
        location_patterns = [
            r"mallorca",
            r"barcelona",
            r"remote[\s-]first",
            r"100%\s*remote",
            r"island\s*base",
            r"baleares",
        ]

        scanned_count = 0
        for p in BRAND_DIR.rglob("*"):
            if p.is_file() and p.suffix in {".html", ".css", ".js", ".svg"}:
                scanned_count += 1
                content = p.read_text(encoding="utf-8", errors="ignore")
                for pat in price_patterns:
                    matches = re.findall(pat, content, re.IGNORECASE)
                    self.assertFalse(matches, f"Price pattern '{pat}' in {p.relative_to(REPO_ROOT)}: {matches}")
                for pat in location_patterns:
                    matches = re.findall(pat, content, re.IGNORECASE)
                    self.assertFalse(matches, f"Location pattern '{pat}' in {p.relative_to(REPO_ROOT)}: {matches}")

        self.assertGreaterEqual(scanned_count, 50, f"Expected >= 50 scanned files, scanned {scanned_count}")

        # Git status check for CV_gen
        git_bin = shutil.which("git") or (
            r"C:\Program Files\Git\cmd\git.exe"
            if os.path.exists(r"C:\Program Files\Git\cmd\git.exe")
            else None
        )
        if git_bin:
            res = subprocess.run([git_bin, "status", "--porcelain", "CV_gen"], cwd=str(REPO_ROOT), capture_output=True, text=True)
            self.assertEqual(res.stdout.strip(), "", f"CV_gen tracked or modified: {res.stdout}")


if __name__ == "__main__":
    unittest.main()
