#!/usr/bin/env python3
"""Automated axe-core WCAG 2.2 A/AA and best-practice scan of local production HTML.

This uses real local HTTP/JS/CSS on the immutable production-mode build.
CSP is bypassed in a separate audit-only Playwright context to inject axe-core;
normal-CSP browser contract is tested separately in phase03_production_http_browser.py.
It is NOT hosted, manual screen-reader, keyboard/focus, real-device, or field audit.
"""
from __future__ import annotations
import argparse
import json
import threading
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright
from phase03_production_http_browser import Handler, parse_headers, ROOT, DIST, OUTPUT

TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa",
        "wcag22a", "wcag22aa", "best-practice"]


def audit(engine: str, axe_path: Path, publication_only: bool = False) -> dict:
    if engine not in ("chromium", "firefox", "webkit"):
        raise ValueError("Unsupported engine")
    script = axe_path.resolve(strict=True)
    if not script.is_file() or script.stat().st_size < 100_000:
        raise ValueError("A genuine locally installed axe-core asset is required")
    manifest = json.loads((DIST / "manifest.json").read_text(encoding="utf-8"))
    expected_routes = 49 if publication_only else 34
    if manifest.get("build_mode") != "production" or manifest.get("route_count") != expected_routes:
        raise AssertionError("Unexpected production candidate route count")
    routes = manifest.get("phase03_publication_routes", []) if publication_only else manifest["routes"]
    if len(routes) != (15 if publication_only else 34):
        raise AssertionError("Accessibility audit route cohort mismatch")
    header_type = type("LocalAxeHandler", (Handler,), {"response_headers": parse_headers()})
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(header_type, directory=str(DIST)))
    worker = threading.Thread(target=httpd.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{httpd.server_port}"
    result = {
        "classification": "LOCAL_HTTP_AXE_AUTOMATED_AUDIT_ONLY",
        "engine": engine, "axe_version": None, "routes": 0,
        "scans": 0, "tags": TAGS, "violations": [], "incomplete_checks": 0,
        "passed": False, "hosted_cloudflare_verified": False,
        "manual_wcag_22_aa_certified": False, "deployed": False,
        "privacy": "rule ids, selectors and counts only; no page text or visitor data",
    }
    try:
        with sync_playwright() as pw:
            browser = getattr(pw, engine).launch(headless=True, **(
                {"args": ["--no-sandbox"]} if engine == "chromium" else {}))
            # Only this additional audit context bypasses CSP to load the
            # accessibility testing library; the real-CSP context does not.
            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                reduced_motion="reduce", bypass_csp=True)
            page = context.new_page()
            page.set_default_timeout(10000)
            for route in routes:
                response = page.goto(base + route, wait_until="load", timeout=20000)
                if not response or response.status != 200:
                    raise AssertionError("Local audit route was not served: " + route)
                page.add_script_tag(path=str(script))
                result["axe_version"] = page.evaluate("() => window.axe.version")
                for theme in ("dark", "light"):
                    page.locator("html").evaluate("(el, theme) => el.dataset.theme = theme", theme)
                    # Return only rule/impact/count/limited selector evidence,
                    # never HTML snippets or PII-bearing page content.
                    details = page.evaluate("""async (tags) => {
                        const res = await window.axe.run(document, {
                          runOnly: {type: 'tag', values: tags},
                          resultTypes: ['violations', 'incomplete']
                        });
                        return {
                          violations: res.violations.map(v => ({
                            id: v.id, impact: v.impact, count: v.nodes.length,
                            selectors: v.nodes.slice(0, 3).map(n => n.target)
                          })),
                          incomplete: res.incomplete.length
                        };
                    }""", TAGS)
                    result["scans"] += 1
                    result["incomplete_checks"] += details["incomplete"]
                    for violation in details["violations"]:
                        result["violations"].append({"route": route, "theme": theme, **violation})
                result["routes"] += 1
            context.close()
            browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()
    if result["axe_version"] != "4.14.0":
        raise AssertionError("Unapproved/unpinned axe-core version")
    result["passed"] = (
        result["routes"] == len(routes) and result["scans"] == len(routes)*2
        and not result["violations"])
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", choices=["chromium", "firefox", "webkit"], required=True)
    parser.add_argument("--axe-path", type=Path, required=True)
    parser.add_argument("--publication-only", action="store_true")
    args = parser.parse_args()
    result = audit(args.engine, args.axe_path, publication_only=args.publication_only)
    OUTPUT.mkdir(exist_ok=True)
    artifact = OUTPUT / (f"phase03-axe-publication-{args.engine}.json" if args.publication_only else f"phase03-axe-{args.engine}.json")
    artifact.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "classification": result["classification"], "engine": result["engine"],
        "axe_version": result["axe_version"], "routes": result["routes"],
        "scans": result["scans"], "violations": len(result["violations"]),
        "incomplete_checks": result["incomplete_checks"], "passed": result["passed"],
        "hosted_cloudflare_verified": False, "manual_wcag_22_aa_certified": False
    }, sort_keys=True))
    if result["violations"]:
        print(json.dumps(result["violations"][:45], ensure_ascii=True)[:9000])
    if not result["passed"]:
        raise SystemExit(1)
