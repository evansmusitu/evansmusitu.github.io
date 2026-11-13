#!/usr/bin/env python3
"""Actual local HTTP transport/browser test for the generated production artifact.

This bounded loopback test replays the generated Cloudflare Pages _headers file
against real static responses, with local CSS and JS fetched by the browser.
It is NOT a hosted Cloudflare/CSP acceptance, real mobile device test, manual
WCAG certification, production deployment or external network probe.
"""
from __future__ import annotations
import argparse
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ORIGIN = "https://mftintelligence.com"
OUTPUT = ROOT / "review-artifacts"


def parse_headers() -> dict[str, str]:
    data = (DIST / "_headers").read_text(encoding="utf-8").splitlines()
    if not data or data[0] != "/*":
        raise ValueError("Missing expected generated Pages header scope")
    result = {}
    for line in data[1:]:
        if not line.startswith("  ") or ":" not in line:
            raise ValueError("Malformed Pages header declaration")
        key, value = line.strip().split(":", 1)
        key = key.strip().lower()
        if not key or key in result:
            raise ValueError("Duplicate/empty Pages header")
        result[key] = value.strip()
    required = {"content-security-policy", "x-content-type-options",
                "permissions-policy", "referrer-policy", "x-frame-options"}
    if not required.issubset(result):
        raise ValueError("Incomplete security header contract")
    if "frame-ancestors 'none'" not in result["content-security-policy"]:
        raise ValueError("Frame restrictions missing")
    if result["x-content-type-options"] != "nosniff":
        raise ValueError("Missing nosniff")
    return result


class Handler(SimpleHTTPRequestHandler):
    response_headers: dict[str, str] = {}

    def end_headers(self):
        for key, value in self.response_headers.items():
            self.send_header(key, value)
        super().end_headers()

    def log_message(self, format, *args):
        return


def check(engine: str) -> dict:
    if engine not in {"chromium", "firefox", "webkit"}:
        raise ValueError("Unsupported browser")
    manifest = json.loads((DIST / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("build_mode") != "production" or manifest.get("studio_media_included") is not True:
        raise AssertionError("A full media-qualified production artifact is required")
    routes = manifest["routes"]
    if len(routes) != 34 or len(set(routes)) != 34:
        raise AssertionError("Unexpected production route count")
    response_headers = parse_headers()
    handler_type = type("LocalProductionHandler", (Handler,), {"response_headers": response_headers})
    handler = partial(handler_type, directory=str(DIST))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    results = {
        "classification": "LOCAL_HTTP_PRODUCTION_ARTIFACT_SIMULATION_ONLY",
        "browser": engine, "source_mode": "production",
        "checked_routes": 0, "headers_checked": 0, "jsonld_checked": 0,
        "local_assets_real_network_loaded": False, "interactions_checked": 0,
        "hosted_cloudflare_verified": False, "wcag_certified": False,
        "field_web_vitals_measured": False, "deployed": False,
        "remote_writes": 0, "console_errors": [], "page_errors": [],
        "request_failures": [], "off_origin_requests": [],
        "interrupted_local_media_preloads": 0,
    }
    browser = None
    try:
        with sync_playwright() as playwright:
            launch = {"headless": True}
            if engine == "chromium":
                if os.environ.get("MUSITU_CHROMIUM_EXECUTABLE"):
                    launch["executable_path"] = os.environ["MUSITU_CHROMIUM_EXECUTABLE"]
                launch["args"] = ["--no-sandbox"]
            browser = getattr(playwright, engine).launch(**launch)
            context = browser.new_context(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
            page = context.new_page()
            page.set_default_timeout(7000)
            page.on("console", lambda msg: results["console_errors"].append(msg.text) if msg.type == "error" else None)
            page.on("pageerror", lambda exc: results["page_errors"].append(str(exc)))
            def failed(request):
                reason = request.failure or "unknown"
                # Browsers may abort a streaming metadata prefetch when navigating
                # off the Studio page. The media is separately fetched and checked
                # to distinguish aborted preload from an actually missing file.
                if (urlsplit(request.url).path == "/assets/studio-demo-82s.mp4"
                        and "ERR_ABORTED" in reason):
                    results["interrupted_local_media_preloads"] += 1
                else:
                    results["request_failures"].append(request.url + ": " + reason)

            def track_request(request):
                parsed = urlsplit(request.url)
                if parsed.scheme in ("http", "https") and parsed.netloc == urlsplit(base).netloc:
                    return
                if parsed.scheme == "blob" and request.url.startswith("blob:" + base + "/"):
                    return  # media-generated same-origin blob object, not a remote request
                results["off_origin_requests"].append(request.url)

            page.on("requestfailed", failed)
            page.on("request", track_request)
            for route in routes:
                response = page.goto(base + route, wait_until="load", timeout=16000)
                if response is None or response.status != 200:
                    raise AssertionError(f"Generated route failed on local HTTP: {route}")
                received = {k.lower(): v for k, v in response.headers.items()}
                for key, value in response_headers.items():
                    if received.get(key) != value:
                        raise AssertionError(f"Local response header mismatch: {route}, {key}")
                results["headers_checked"] += 1
                if page.locator("main#main").count() != 1 or page.locator("h1").count() != 1:
                    raise AssertionError(f"Missing accessible document structure: {route}")
                if page.locator("html.has-js").count() != 1:
                    raise AssertionError(f"Real JS did not initialize: {route}")
                if page.evaluate("() => document.styleSheets.length") < 1:
                    raise AssertionError(f"CSS failed to load: {route}")
                expected = "noindex,nofollow" if route == "/404/" else "index,follow"
                if page.locator('meta[name="robots"]').get_attribute("content") != expected:
                    raise AssertionError(f"Wrong crawler directive: {route}")
                if route == "/404/":
                    if page.locator('link[rel="canonical"], script[type="application/ld+json"]').count():
                        raise AssertionError("404 should not have canonical or Article/Product schema")
                else:
                    if page.locator('link[rel="canonical"]').get_attribute("href") != ORIGIN + route:
                        raise AssertionError(f"Canonical mismatch: {route}")
                    if page.locator('meta[property="og:url"]').get_attribute("content") != ORIGIN + route:
                        raise AssertionError(f"Open Graph canonical mismatch: {route}")
                    if page.locator('script[type="application/ld+json"]').count() != 1:
                        raise AssertionError(f"Wrong JSON-LD count: {route}")
                    payload = json.loads(page.locator('script[type="application/ld+json"]').inner_text())
                    if payload.get("@context") != "https://schema.org" or not payload.get("@graph"):
                        raise AssertionError(f"Invalid JSON-LD document: {route}")
                    results["jsonld_checked"] += 1
                results["checked_routes"] += 1
            # Verify navigation, CSS and scripts were actually served over local HTTP,
            # rather than replaced with inline test fixtures.
            for resource in ("/assets/site.css", "/assets/site.js", "/assets/site-data.js"):
                response = page.request.get(base + resource)
                if response.status != 200 or not response.body():
                    raise AssertionError("Local browser asset failed: " + resource)
            media_response = page.request.get(base + "/assets/studio-demo-82s.mp4")
            if media_response.status != 200 or len(media_response.body()) != 1540312:
                raise AssertionError("Media source did not respond with expected exact bytes")
            results["local_assets_real_network_loaded"] = True
            page.set_viewport_size({"width": 1280, "height": 800})
            page.goto(base + "/", wait_until="load", timeout=16000)
            page.get_by_role("button", name="Search the website").click()
            if not page.locator("#search-dialog").evaluate("(e)=>e.open"):
                raise AssertionError("Search modal failed with real CSP + scripts")
            results["interactions_checked"] += 1
            page.keyboard.press("Escape")
            if page.locator("#search-dialog").evaluate("(e)=>e.open"):
                raise AssertionError("Search modal cannot be dismissed")
            results["interactions_checked"] += 1
            page.locator('main a[href="/products/axiom/"]').first.click()
            page.wait_for_url(base + "/products/axiom/")
            if page.locator("h1").count() != 1:
                raise AssertionError("Same-origin product navigation failed")
            results["interactions_checked"] += 1
            context.close()
            browser.close()
            browser = None
    finally:
        if browser is not None:
            browser.close()
        httpd.shutdown()
        httpd.server_close()
    if results["console_errors"] or results["page_errors"] or results["request_failures"] or results["off_origin_requests"]:
        raise AssertionError(json.dumps(results, ensure_ascii=False)[:5000])
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=("chromium", "firefox", "webkit"), required=True)
    args = parser.parse_args()
    result = check(args.engine)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / f"phase03-production-local-http-{args.engine}.json").write_text(
        json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))
