#!/usr/bin/env python3
"""Independent bounded public SEO observer. GET-only, no cookies, auth, or production mutation.

Run only AFTER an approved Phase 03 corporate Pages deployment. It checks HTTP
indexability signals but cannot establish search-engine indexing or ranking.
"""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET
import json

from seo import ORIGIN, read_catalog
from phase03_publication import approved_sources, article_routes, EN_FR, FR_EN

class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonical = []
        self.robots = []
        self.jsonld = []
        self.alternates = []
        self.document_lang = []
        self._capture = False
        self._chunks = []

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        if tag == "html":
            self.document_lang.append(data.get("lang"))
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical.append(data.get("href"))
        elif tag == "link" and data.get("rel") == "alternate" and data.get("hreflang"):
            self.alternates.append((data.get("hreflang"), data.get("href")))
        elif tag == "meta" and data.get("name") == "robots":
            self.robots.append(data.get("content"))
        elif tag == "script" and data.get("type") == "application/ld+json":
            self._capture = True
            self._chunks = []

    def handle_data(self, data):
        if self._capture:
            self._chunks.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self._capture:
            self._capture = False
            self.jsonld.append(json.loads("".join(self._chunks)))
            self._chunks = []

def get(path: str, max_bytes: int = 1_000_000):
    if not path.startswith("/"):
        raise ValueError("Only root-relative public GETs are allowed")
    request = Request(ORIGIN + path, headers={"User-Agent": "MUSITU-SEO-Observer/1.0 (read-only)", "Accept": "text/html,application/xml,text/plain"})
    with urlopen(request, timeout=18) as response:
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError("Response exceeded read budget")
        return response.status, response.url, {k.lower(): v for k,v in response.headers.items()}, data

def validate_page(route: str):
    status, url, headers, body = get(route)
    expected = ORIGIN + route
    if status != 200 or url.rstrip("/") != expected.rstrip("/"):
        raise AssertionError(f"Noncanonical HTTP response: {route}")
    parser = MetadataParser()
    parser.feed(body.decode("utf-8"))
    if parser.canonical != [expected]:
        raise AssertionError(f"Canonical mismatch: {route}")
    if parser.robots != ["index,follow"]:
        raise AssertionError(f"Indexability mismatch: {route}")
    if len(parser.jsonld) != 1:
        raise AssertionError(f"Missing JSON-LD: {route}")
    graph = parser.jsonld[0]
    if graph.get("@context") != "https://schema.org":
        raise AssertionError(f"Invalid JSON-LD context: {route}")
    types = {x.get("@type") for x in graph.get("@graph", [])}
    required = {"Organization","WebSite"} if route == "/" else {"BreadcrumbList"}
    if route in ("/products/axiom/", "/products/foundry/studio/"):
        required.add("SoftwareApplication")
    if route.startswith("/research/articles/"):
        required.update(("Article", "BreadcrumbList"))
    if route in FR_EN:
        required.update(("WebPage", "BreadcrumbList"))
        if parser.document_lang != ["fr"] or not any(
            x.get("@type") == "WebPage" and x.get("inLanguage") == "fr"
            for x in graph.get("@graph", [])
        ):
            raise AssertionError(f"French document language mismatch: {route}")
    if route in EN_FR or route in FR_EN:
        en = route if route in EN_FR else FR_EN[route]
        fr = EN_FR[en]
        expected_alternates = [("en", ORIGIN + en), ("fr", ORIGIN + fr),
                               ("x-default", ORIGIN + en)]
        if sorted(parser.alternates) != sorted(expected_alternates):
            raise AssertionError(f"Missing or non-reciprocal hreflang: {route}")
    if not required.issubset(types):
        raise AssertionError(f"Incomplete structured metadata: {route}; expected {sorted(required)}")
    if route == "/" and (not headers.get("content-security-policy") or headers.get("x-content-type-options", "").lower() != "nosniff"):
        raise AssertionError("Missing public security headers")
    return route

def audit():
    core_routes = set(read_catalog()["routes"])
    article_pages = set(article_routes(approved_sources()))
    french_pages = set(FR_EN)
    routes = core_routes | article_pages | french_pages
    if (len(core_routes) != 33 or len(article_pages) != 12
            or len(french_pages) != 3 or len(routes) != 48 or "/404/" in routes):
        raise AssertionError("Unexpected Phase 03 release cohort")
    status, url, _, robots = get("/robots.txt")
    if status != 200 or url != ORIGIN + "/robots.txt" or b"Sitemap: https://mftintelligence.com/sitemap.xml" not in robots:
        raise AssertionError("Unacceptable robots/sitemap contract")
    if b"Disallow: /" in robots:
        raise AssertionError("Root crawling unexpectedly disabled")
    status, url, _, data = get("/sitemap.xml")
    if status != 200 or url != ORIGIN + "/sitemap.xml":
        raise AssertionError("Missing production sitemap")
    root = ET.fromstring(data)
    locs = [x.text for x in root.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    if len(locs) != len(set(locs)):
        raise AssertionError("Duplicate sitemap URL")
    for u in locs:
        s = urlsplit(u)
        if s.scheme != "https" or s.netloc != "mftintelligence.com" or s.username or s.password or s.fragment:
            raise AssertionError("Off-origin or malformed sitemap entry")
    if set(locs) != {ORIGIN + p for p in routes}:
        raise AssertionError("Phase 03 live sitemap must contain exactly 48 approved URLs")
    passed = []
    with ThreadPoolExecutor(max_workers=5) as pool:
        jobs = {pool.submit(validate_page, route): route for route in sorted(routes)}
        for job in as_completed(jobs):
            passed.append(job.result())
    result = {"phase":"MUSITU corporate Phase 03","result":"PASS","production_origin":ORIGIN,
      "indexed_intent_core_routes_checked":len(core_routes),
      "research_articles_checked":len(article_pages),"french_pages_checked":len(french_pages),
      "total_phase03_routes_checked":len(passed),"sitemap_entries":len(locs),
      "jsonld_documents_checked":len(passed),"account_verification_claimed":False,
      "google_indexing_claimed":False,"writes":0}
    print(json.dumps(result, sort_keys=True))
    return result

if __name__ == "__main__":
    audit()
