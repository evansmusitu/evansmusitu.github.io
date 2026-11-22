#!/usr/bin/env python3
"""GET-only external baseline observation for the *currently live* corporate site.

This is NOT candidate hosted acceptance, a security penetration test, a load test,
a performance/Core-Web-Vitals audit, search-indexing proof, or deployment authority.
No tokens, cookies, personal information, emails, or requests with side effects.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, HTTPRedirectHandler, build_opener
from xml.etree import ElementTree as ET
import json

ORIGIN = "https://mftintelligence.com"
PAGE_PATHS = ("/", "/products/axiom/", "/contact/", "/experiences/intelligence/")
NEGATIVE_PATH = "/__musitu-read-only-baseline-not-a-real-page-20261122/"
MAX_BYTES = 1_000_000
OUTPUT = Path(__file__).resolve().parents[1] / "review-artifacts" / "public-baseline-smoke.json"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class HeadParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.robots = []
        self.lang = []
        self.mains = 0
        self.headings = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang.append(a.get("lang"))
        if tag == "main" and a.get("id") == "main":
            self.mains += 1
        if tag == "h1":
            self.headings += 1
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical.append(a.get("href"))
        if tag == "meta" and a.get("name") == "robots":
            self.robots.append(a.get("content"))


def get(route: str):
    """Fetch only one of a fixed set of public same-origin paths, never follow redirects."""
    if route not in {*PAGE_PATHS, NEGATIVE_PATH, "/robots.txt", "/sitemap.xml", "/manifest.json"}:
        raise ValueError("Route not in fixed, public, read-only observation set")
    request = Request(
        ORIGIN + route,
        headers={"User-Agent": "MUSITU-read-only-public-baseline/1.0",
                 "Accept": "text/html,application/xml,text/plain"},
        method="GET",
    )
    opener = build_opener(NoRedirect())
    try:
        response = opener.open(request, timeout=16)
    except HTTPError as exc:
        response = exc
    with response:
        raw = response.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise AssertionError("Live response exceeds bounded read budget")
        return int(response.code), response.url, {
            k.lower(): v for k, v in response.headers.items()
        }, raw


def assert_security_headers(route: str, headers: dict):
    csp = headers.get("content-security-policy", "").lower()
    if "frame-ancestors 'none'" not in csp or "object-src 'none'" not in csp:
        raise AssertionError("Missing production CSP protection on " + route)
    if headers.get("x-content-type-options", "").lower() != "nosniff":
        raise AssertionError("Missing production X-Content-Type-Options on " + route)


def inspect_page(route: str):
    status, url, headers, raw = get(route)
    if status != 200 or url != ORIGIN + route:
        raise AssertionError("Live canonical transport failed for " + route)
    assert_security_headers(route, headers)
    p = HeadParser()
    p.feed(raw.decode("utf-8"))
    if p.lang != ["en"] or p.mains != 1 or p.headings != 1:
        raise AssertionError("Missing accessible page structure on " + route)
    if p.canonical != [ORIGIN + route] or p.robots != ["index,follow"]:
        raise AssertionError("Missing public canonical/indexability contract on " + route)
    return {"path": route, "http_status": status, "canonical": True,
            "security_headers": True, "html_document": True}


def inspect_negative_control():
    status, url, headers, raw = get(NEGATIVE_PATH)
    if status != 404 or url != ORIGIN + NEGATIVE_PATH:
        raise AssertionError("Unknown page is not HTTP 404")
    assert_security_headers(NEGATIVE_PATH, headers)
    p = HeadParser()
    p.feed(raw.decode("utf-8"))
    if p.robots != ["noindex,nofollow"] or p.canonical:
        raise AssertionError("404 page is not safely noindex")
    return {"path": NEGATIVE_PATH, "http_status": status, "noindex": True}


def inspect_discovery():
    status, url, _, robots = get("/robots.txt")
    if status != 200 or url != ORIGIN + "/robots.txt":
        raise AssertionError("Missing live robots.txt")
    rules = robots.decode("utf-8")
    if "Disallow: /" in rules or "Sitemap: " + ORIGIN + "/sitemap.xml" not in rules:
        raise AssertionError("Public crawling or sitemap directive is incorrect")
    status, url, _, xml = get("/sitemap.xml")
    if status != 200 or url != ORIGIN + "/sitemap.xml":
        raise AssertionError("Missing live sitemap")
    root = ET.fromstring(xml)
    ns = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
    locs = [e.text for e in root.findall(ns + "url/" + ns + "loc")]
    if len(locs) != len(set(locs)) or not locs:
        raise AssertionError("Empty or duplicate public sitemap URLs")
    if any(not x.startswith(ORIGIN + "/") for x in locs):
        raise AssertionError("Unexpected off-origin sitemap URL")
    for p in PAGE_PATHS:
        if ORIGIN + p not in locs:
            raise AssertionError("Missing preserved core public route " + p)
    return {"robots": "crawl_allowed", "sitemap_entries": len(locs),
            "preserved_core_routes": list(PAGE_PATHS)}


def inspect_public_build_metadata():
    """Detect accidental exposure of internal build flags without logging any values."""
    route = "/manifest.json"
    status, url, _, raw = get(route)
    if status == 404:
        return {"path": route, "http_status": 404, "internal_release_fields_exposed": False}
    if status != 200 or url != ORIGIN + route:
        raise AssertionError("Unexpected public manifest response")
    try:
        value = json.loads(raw)
    except (UnicodeError, ValueError, TypeError):
        return {"path": route, "http_status": 200,
                "internal_release_fields_exposed": False,
                "non_json_response": True}
    flagged = bool(isinstance(value, dict) and (
        {"production_approved", "gated_routes", "brand_master_sha256",
         "media_publication_approved", "phase03_publication_source_approved"} & set(value)
    ))
    return {"path": route, "http_status": 200,
            "internal_release_fields_exposed": flagged}


def audit():
    details = [inspect_page(path) for path in PAGE_PATHS]
    not_found = inspect_negative_control()
    discovery = inspect_discovery()
    metadata = inspect_public_build_metadata()
    return {
        "schema": "musitu.public_baseline_observation.v1",
        "origin": ORIGIN,
        "scope": "currently_live_production_only",
        "candidate_hosted_acceptance": False,
        "human_visual_review": False,
        "core_web_vitals_test": False,
        "production_mutations": 0,
        "status": "PASS",
        "pages": details,
        "negative_control": not_found,
        "discovery": discovery,
        "public_build_metadata": metadata,
    }


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    try:
        record = audit()
    except Exception as exc:
        record = {"schema": "musitu.public_baseline_observation.v1",
                  "origin": ORIGIN, "scope": "currently_live_production_only",
                  "candidate_hosted_acceptance": False,
                  "production_mutations": 0, "status": "FAIL",
                  "reason": str(exc)[:240]}
        OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        raise
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, sort_keys=True))
