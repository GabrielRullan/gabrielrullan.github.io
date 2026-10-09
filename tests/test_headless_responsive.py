"""
tests/test_headless_responsive.py - Headless Chrome responsive rendering and runtime audit suite.

Verifies across vA, vB, and vC at 375px, 768px, and 1440px viewports:
1. No horizontal scrolling (scrollWidth <= window.innerWidth).
2. Zero console errors.
3. Zero network 404s / failed requests.
4. All images successfully loaded (complete && naturalWidth > 0).
5. Captures reference PNG screenshots for visual verification.
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

VERSIONS = ["vA", "vB", "vC"]
VIEWPORTS = [
    {"name": "mobile", "width": 375, "height": 812, "mobile": True},
    {"name": "tablet", "width": 768, "height": 1024, "mobile": False},
    {"name": "desktop", "width": 1440, "height": 900, "mobile": False},
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
    """Lightweight threaded HTTP server serving WEB_DIR."""

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
    """Manages a headless Chrome process and communicates via Chrome DevTools Protocol."""

    def __init__(self, browser_path: str):
        self.browser_path = browser_path
        self.port = find_free_port()
        self.user_data_dir = tempfile.mkdtemp(prefix="chrome_test_")
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
        time.sleep(1.5)  # Allow rendering, fonts, scripts to stabilize

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


class TestHeadlessResponsive(unittest.TestCase):
    """E2E Test verifying responsiveness, console logs, network integrity, and screenshots."""

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

    def _test_version_viewport(self, version: str, vp: dict):
        html_path = WEB_DIR / version / "index.html"
        self.assertTrue(html_path.exists(), f"Cannot test {version}: {html_path} does not exist.")

        url = f"http://127.0.0.1:{self.server.port}/{version}/"
        self.driver.set_viewport(vp["width"], vp["height"], vp["mobile"])
        self.driver.navigate(url)

        # 1. Screenshot capture
        screenshot_path = SCREENSHOTS_DIR / f"{version}_{vp['width']}.png"
        self.driver.capture_screenshot(screenshot_path)
        self.assertTrue(screenshot_path.exists(), f"Screenshot failed for {version} at {vp['width']}px")
        self.assertGreater(screenshot_path.stat().st_size, 5000, f"Screenshot empty for {version} at {vp['width']}px")

        # 2. Check no horizontal scrolling
        scroll_check = self.driver.evaluate("""
            (() => {
                const docScroll = document.documentElement.scrollWidth;
                const winWidth = window.innerWidth;
                const bodyScroll = document.body ? document.body.scrollWidth : 0;
                return {
                    docScroll: docScroll,
                    bodyScroll: bodyScroll,
                    winWidth: winWidth,
                    hasOverflow: (docScroll > winWidth + 1) || (bodyScroll > winWidth + 1)
                };
            })()
        """)
        self.assertIsNotNone(scroll_check, f"Failed to evaluate scroll metrics on {version} at {vp['width']}px")
        self.assertFalse(
            scroll_check.get("hasOverflow", False),
            f"Horizontal overflow detected on {version} at {vp['width']}px! "
            f"Doc scrollWidth={scroll_check.get('docScroll')}, Body scrollWidth={scroll_check.get('bodyScroll')}, "
            f"Window innerWidth={scroll_check.get('winWidth')}"
        )

        # 3. Check console errors (filter out favicon 404s if any)
        console_errors = [e for e in self.driver.console_errors if "favicon" not in e.lower()]
        self.assertEqual(
            len(console_errors), 0,
            f"Console errors detected on {version} at {vp['width']}px: {console_errors}"
        )

        # 4. Check network failures / 404s
        network_failures = [f for f in self.driver.network_failures if "favicon.ico" not in f]
        self.assertEqual(
            len(network_failures), 0,
            f"Network errors/404s detected on {version} at {vp['width']}px: {network_failures}"
        )

        # 5. Check all images loaded
        image_status = self.driver.evaluate("""
            (() => {
                const imgs = Array.from(document.images);
                return imgs.map(i => ({
                    src: i.src,
                    complete: i.complete,
                    naturalWidth: i.naturalWidth
                }));
            })()
        """) or []
        for img in image_status:
            if not img.get("src", "").startswith("data:"):
                self.assertTrue(
                    img.get("complete", False) and img.get("naturalWidth", 0) > 0,
                    f"Broken image detected on {version}: src='{img.get('src')}', naturalWidth={img.get('naturalWidth')}"
                )

    # Version A tests
    def test_vA_mobile_375(self):
        self._test_version_viewport("vA", VIEWPORTS[0])

    def test_vA_tablet_768(self):
        self._test_version_viewport("vA", VIEWPORTS[1])

    def test_vA_desktop_1440(self):
        self._test_version_viewport("vA", VIEWPORTS[2])

    # Version B tests
    def test_vB_mobile_375(self):
        self._test_version_viewport("vB", VIEWPORTS[0])

    def test_vB_tablet_768(self):
        self._test_version_viewport("vB", VIEWPORTS[1])

    def test_vB_desktop_1440(self):
        self._test_version_viewport("vB", VIEWPORTS[2])

    # Version C tests
    def test_vC_mobile_375(self):
        self._test_version_viewport("vC", VIEWPORTS[0])

    def test_vC_tablet_768(self):
        self._test_version_viewport("vC", VIEWPORTS[1])

    def test_vC_desktop_1440(self):
        self._test_version_viewport("vC", VIEWPORTS[2])


if __name__ == "__main__":
    unittest.main()
