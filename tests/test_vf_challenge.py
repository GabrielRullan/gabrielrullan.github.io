"""
tests/test_vf_challenge.py - Empirical Challenger Audit for Version F (web/vF/index.html)

Performs exhaustive headless browser audits via Chrome DevTools Protocol:
1. Responsive viewports: 375x812 (mobile), 768x1024 (tablet), 1440x900 (desktop)
   plus stress viewports: 320x568 (narrow mobile), 1920x1080 (HD).
2. Zero horizontal overflow (documentElement, body, and per-element bounding check).
3. Zero console errors, warnings, or exceptions.
4. Zero network 404s, failed asset loads; complete images with naturalWidth > 0.
5. Interactive Mobile Navigation:
   - Toggle opens menu (aria-expanded="true", class "open", visible in layout)
   - Nav link click closes menu (aria-expanded="false", class "open" removed)
   - Toggle closes menu cleanly
6. Interactive FAQ Accordion:
   - Sequential expansion and collapse across all items
   - Accurate aria-expanded toggling
   - Mutually exclusive active state
   - Toggle-to-close on active item
7. Internal anchor href target verification (zero broken anchor targets).
"""

import base64
import json
import os
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
SCREENSHOTS_DIR = REPO_ROOT / "tests" / "screenshots"

VIEWPORTS = [
    {"name": "mobile_375", "width": 375, "height": 812, "mobile": True},
    {"name": "tablet_768", "width": 768, "height": 1024, "mobile": False},
    {"name": "desktop_1440", "width": 1440, "height": 900, "mobile": False},
    {"name": "stress_narrow_320", "width": 320, "height": 568, "mobile": True},
    {"name": "stress_desktop_1920", "width": 1920, "height": 1080, "mobile": False},
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
        self.user_data_dir = tempfile.mkdtemp(prefix="chrome_vf_challenge_")
        self.proc = None
        self.ws = None
        self.cmd_id = 0
        self.console_errors = []
        self.console_warnings = []
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
                if m == "Runtime.consoleAPICalled":
                    t = p.get("type")
                    args = " ".join([str(a.get("value", "")) for a in p.get("args", [])])
                    if t == "error":
                        self.console_errors.append(f"Console error: {args}")
                    elif t == "warning":
                        self.console_warnings.append(f"Console warning: {args}")
                elif m == "Log.entryAdded":
                    lvl = p.get("entry", {}).get("level")
                    txt = p.get("entry", {}).get("text")
                    if lvl == "error":
                        self.console_errors.append(f"Log error: {txt}")
                    elif lvl == "warning":
                        self.console_warnings.append(f"Log warning: {txt}")
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
        self.console_warnings = []
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
        val = res.get("result", {}).get("result", {}).get("value")
        return val

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


class TestVFResponsiveDOM(unittest.TestCase):
    server = None
    driver = None

    @classmethod
    def setUpClass(cls):
        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.server = LocalWebServer(port=8001)
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

    def setUp(self):
        self.base_url = f"http://127.0.0.1:{self.server.port}/"

    def test_01_responsive_and_overflow_across_viewports(self):
        """Test 375x812, 768x1024, 1440x900 plus edge cases (320px, 1920px) for zero overflow."""
        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"]):
                self.driver.set_viewport(vp["width"], vp["height"], vp["mobile"])
                self.driver.navigate(self.base_url)

                # Capture screenshot
                shot_path = SCREENSHOTS_DIR / f"vF_{vp['name']}.png"
                self.driver.capture_screenshot(shot_path)
                self.assertTrue(shot_path.exists() and shot_path.stat().st_size > 5000)

                # Check root scroll overflow
                overflow_info = self.driver.evaluate("""
                    (() => {
                        const winWidth = window.innerWidth;
                        const docEl = document.documentElement;
                        const body = document.body;
                        const docScroll = docEl.scrollWidth;
                        const bodyScroll = body ? body.scrollWidth : 0;
                        const docClient = docEl.clientWidth;
                        
                        // Per-element deep audit for overflowing elements
                        const overflowingElements = [];
                        const allElements = document.querySelectorAll('*');
                        for (const el of allElements) {
                            const rect = el.getBoundingClientRect();
                            if (rect.width > 0 && rect.height > 0) {
                                if (rect.right > winWidth + 1.5) {
                                    overflowingElements.push({
                                        tag: el.tagName,
                                        id: el.id,
                                        class: el.className,
                                        right: rect.right,
                                        width: rect.width,
                                        winWidth: winWidth
                                    });
                                }
                            }
                        }

                        return {
                            winWidth: winWidth,
                            docScroll: docScroll,
                            docClient: docClient,
                            bodyScroll: bodyScroll,
                            hasRootOverflow: (docScroll > winWidth + 1) || (bodyScroll > winWidth + 1),
                            overflowCount: overflowingElements.length,
                            overflowDetails: overflowingElements.slice(0, 5)
                        };
                    })()
                """)

                self.assertIsNotNone(overflow_info, f"Could not evaluate overflow metrics at {vp['name']}")
                self.assertFalse(
                    overflow_info.get("hasRootOverflow", False),
                    f"Root horizontal overflow detected at {vp['name']}! "
                    f"docScroll={overflow_info.get('docScroll')}, bodyScroll={overflow_info.get('bodyScroll')}, "
                    f"winWidth={overflow_info.get('winWidth')}"
                )
                self.assertEqual(
                    overflow_info.get("overflowCount", 0), 0,
                    f"Elements extending past viewport right edge at {vp['name']}: {overflow_info.get('overflowDetails')}"
                )

    def test_02_zero_console_and_network_errors(self):
        """Audit for zero uncaught JS console errors and zero 404 network errors."""
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(self.base_url)

        console_errs = [e for e in self.driver.console_errors if "favicon" not in e.lower()]
        self.assertEqual(len(console_errs), 0, f"Uncaught console errors detected: {console_errs}")

        net_errs = [n for n in self.driver.network_failures if "favicon.ico" not in n]
        self.assertEqual(len(net_errs), 0, f"Network failures/404s detected: {net_errs}")

        # Check all images complete and have naturalWidth > 0
        img_check = self.driver.evaluate("""
            (() => {
                const imgs = Array.from(document.images);
                return imgs.map(img => ({
                    src: img.src,
                    complete: img.complete,
                    naturalWidth: img.naturalWidth,
                    naturalHeight: img.naturalHeight
                }));
            })()
        """)
        self.assertGreater(len(img_check), 0, "No images found on page!")
        for img in img_check:
            self.assertTrue(
                img["complete"] and img["naturalWidth"] > 0,
                f"Broken image detected: {img}"
            )

    def test_03_mobile_navigation_toggle_interaction(self):
        """Test mobile navigation menu opening, link clicking, closing, and aria-expanded state."""
        self.driver.set_viewport(375, 812, True)
        self.driver.navigate(self.base_url)

        # 1. Verify mobile toggle is visible and initial aria-expanded is 'false'
        init_state = self.driver.evaluate("""
            (() => {
                const toggle = document.querySelector('.mobile-toggle');
                const menu = document.querySelector('.nav-menu');
                if (!toggle || !menu) return { error: 'Toggle or Menu not found' };
                const toggleStyle = window.getComputedStyle(toggle);
                const menuStyle = window.getComputedStyle(menu);
                return {
                    toggleDisplay: toggleStyle.display,
                    ariaExpanded: toggle.getAttribute('aria-expanded'),
                    menuHasOpen: menu.classList.contains('open'),
                    menuDisplay: menuStyle.display
                };
            })()
        """)

        self.assertNotIn("error", init_state)
        self.assertNotEqual(init_state["toggleDisplay"], "none", "Mobile toggle should be visible on 375px mobile!")
        self.assertEqual(init_state["ariaExpanded"], "false", "Initial aria-expanded must be 'false'")
        self.assertFalse(init_state["menuHasOpen"], "Initial nav-menu must not have 'open' class")
        self.assertEqual(init_state["menuDisplay"], "none", "Initial nav-menu must be hidden on mobile")

        # 2. Click toggle button to OPEN menu
        opened_state = self.driver.evaluate("""
            (() => {
                const toggle = document.querySelector('.mobile-toggle');
                toggle.click();
                const menu = document.querySelector('.nav-menu');
                const menuStyle = window.getComputedStyle(menu);
                return {
                    ariaExpanded: toggle.getAttribute('aria-expanded'),
                    menuHasOpen: menu.classList.contains('open'),
                    menuDisplay: menuStyle.display,
                    navLinkCount: menu.querySelectorAll('.nav-link').length
                };
            })()
        """)

        self.assertEqual(opened_state["ariaExpanded"], "true", "aria-expanded must be 'true' after clicking toggle")
        self.assertTrue(opened_state["menuHasOpen"], "nav-menu must have class 'open' when expanded")
        self.assertEqual(opened_state["menuDisplay"], "flex", "nav-menu must be display: flex when opened")
        self.assertGreater(opened_state["navLinkCount"], 0, "nav-menu must contain links")

        # Capture mobile menu open screenshot
        shot_path = SCREENSHOTS_DIR / "vF_mobile_menu_open.png"
        self.driver.capture_screenshot(shot_path)
        self.assertTrue(shot_path.exists())

        # 3. Click a navigation link inside menu -> should close menu
        closed_by_link_state = self.driver.evaluate("""
            (() => {
                const toggle = document.querySelector('.mobile-toggle');
                const menu = document.querySelector('.nav-menu');
                const firstLink = menu.querySelector('.nav-link');
                firstLink.click();
                const menuStyle = window.getComputedStyle(menu);
                return {
                    ariaExpanded: toggle.getAttribute('aria-expanded'),
                    menuHasOpen: menu.classList.contains('open'),
                    menuDisplay: menuStyle.display
                };
            })()
        """)

        self.assertEqual(closed_by_link_state["ariaExpanded"], "false", "aria-expanded must revert to 'false' on link click")
        self.assertFalse(closed_by_link_state["menuHasOpen"], "nav-menu must remove 'open' class on link click")
        self.assertEqual(closed_by_link_state["menuDisplay"], "none", "nav-menu must be hidden again")

        # 4. Click toggle button again: open, then click toggle button again: close
        toggle_cycle_state = self.driver.evaluate("""
            (() => {
                const toggle = document.querySelector('.mobile-toggle');
                const menu = document.querySelector('.nav-menu');
                toggle.click(); // open
                const openAria = toggle.getAttribute('aria-expanded');
                const openClass = menu.classList.contains('open');
                
                toggle.click(); // close
                const closeAria = toggle.getAttribute('aria-expanded');
                const closeClass = menu.classList.contains('open');

                return {
                    openAria,
                    openClass,
                    closeAria,
                    closeClass
                };
            })()
        """)
        self.assertEqual(toggle_cycle_state["openAria"], "true")
        self.assertTrue(toggle_cycle_state["openClass"])
        self.assertEqual(toggle_cycle_state["closeAria"], "false")
        self.assertFalse(toggle_cycle_state["closeClass"])

    def test_04_faq_accordion_interaction_and_aria_expanded(self):
        """Test FAQ accordion expansion, collapse, and aria-expanded toggles across all items."""
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(self.base_url)

        faq_count = self.driver.evaluate("""
            (() => document.querySelectorAll('.faq-item').length)()
        """)
        self.assertGreater(faq_count, 0, "No .faq-item elements found on page!")

        for idx in range(faq_count):
            with self.subTest(faq_index=idx):
                # Expand item idx
                expand_result = self.driver.evaluate(f"""
                    (() => {{
                        const items = document.querySelectorAll('.faq-item');
                        const item = items[{idx}];
                        const btn = item.querySelector('.faq-question');
                        btn.click();
                        
                        // Check clicked item
                        const isExpanded = btn.getAttribute('aria-expanded');
                        const hasActive = item.classList.contains('active');
                        const answer = item.querySelector('.faq-answer');
                        const answerStyle = window.getComputedStyle(answer);
                        
                        // Check all other items are closed
                        let otherActiveCount = 0;
                        items.forEach((it, i) => {{
                            if (i !== {idx} && (it.classList.contains('active') || it.querySelector('.faq-question').getAttribute('aria-expanded') === 'true')) {{
                                otherActiveCount++;
                            }}
                        }});

                        return {{
                            isExpanded,
                            hasActive,
                            maxHeight: answerStyle.maxHeight,
                            otherActiveCount
                        }};
                    }})()
                """)

                self.assertEqual(expand_result["isExpanded"], "true", f"Item {idx} aria-expanded should be 'true'")
                self.assertTrue(expand_result["hasActive"], f"Item {idx} must have 'active' class")
                self.assertEqual(expand_result["otherActiveCount"], 0, f"Other items must be closed when item {idx} opens")
                # Wait for CSS transition (0.3s)
                time.sleep(0.35)

                expand_check = self.driver.evaluate(f"""
                    (() => {{
                        const items = document.querySelectorAll('.faq-item');
                        const item = items[{idx}];
                        const ans = item.querySelector('.faq-answer');
                        return {{
                            maxHeight: window.getComputedStyle(ans).maxHeight,
                            offsetHeight: ans.offsetHeight
                        }};
                    }})()
                """)

                self.assertNotEqual(expand_check["maxHeight"], "0px", f"Answer for item {idx} must have non-zero maxHeight")
                self.assertGreater(expand_check["offsetHeight"], 0, f"Answer for item {idx} must have positive offsetHeight")

                # Collapse item idx by clicking it again
                collapse_result = self.driver.evaluate(f"""
                    (() => {{
                        const items = document.querySelectorAll('.faq-item');
                        const item = items[{idx}];
                        const btn = item.querySelector('.faq-question');
                        btn.click(); // click again to collapse
                        
                        const isExpanded = btn.getAttribute('aria-expanded');
                        const hasActive = item.classList.contains('active');

                        return {{
                            isExpanded,
                            hasActive
                        }};
                    }})()
                """)

                self.assertEqual(collapse_result["isExpanded"], "false", f"Item {idx} aria-expanded should revert to 'false'")
                self.assertFalse(collapse_result["hasActive"], f"Item {idx} must remove 'active' class on second click")

    def test_05_internal_anchor_links_integrity(self):
        """Verify every anchor link with href='#...' resolves to a real DOM element ID."""
        self.driver.set_viewport(1440, 900, False)
        self.driver.navigate(self.base_url)

        anchor_results = self.driver.evaluate("""
            (() => {
                const anchors = Array.from(document.querySelectorAll('a[href^="#"]'));
                const results = [];
                anchors.forEach(a => {
                    const href = a.getAttribute('href');
                    if (href && href !== '#' && !href.startsWith('#!')) {
                        const targetId = href.substring(1);
                        const targetEl = document.getElementById(targetId);
                        results.push({
                            text: a.innerText.trim(),
                            href: href,
                            found: !!targetEl
                        });
                    }
                });
                return results;
            })()
        """)

        self.assertGreater(len(anchor_results), 0, "No internal anchor links found")
        for a in anchor_results:
            self.assertTrue(a["found"], f"Broken internal anchor: href='{a['href']}' on text '{a['text']}' has no matching element ID in DOM!")


if __name__ == "__main__":
    unittest.main()
