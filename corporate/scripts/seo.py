"""Non-executable, truth-constrained production SEO metadata for the 34-route corporate core.

All publicly generated organization attributes must already be visible on the website.
No business address, registered legal identifier, offer, aggregateRating, review, price,
social profile, author biography or external URL is inferred.
"""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEO_CATALOG = ROOT / "content" / "seo-routes.json"
ORIGIN = "https://mftintelligence.com"

def read_catalog() -> dict:
    data = json.loads(SEO_CATALOG.read_text(encoding="utf-8"))
    if data.get("origin") != ORIGIN or data.get("language") != "en":
        raise ValueError("Unexpected SEO origin or language")
    return data

def validate_catalog(routes: list[str]) -> dict:
    data = read_catalog()
    expected = set(routes) - {"/404/"}
    actual = set(data.get("routes", {}))
    if actual != expected:
        raise ValueError("SEO route mismatch: missing %s extras %s" % (sorted(expected-actual), sorted(actual-expected)))
    for route, entry in data["routes"].items():
        if not (isinstance(entry.get("primary_query"), str) and entry["primary_query"].strip()):
            raise ValueError("Missing SEO search intent: " + route)
        if not entry.get("page_kind") or not entry.get("search_intent"):
            raise ValueError("Missing SEO page classification: " + route)
    if data.get("published_languages") != ["en"]:
        raise ValueError("Unverified translations cannot be marked published")
    return data

def _trail(route: str, records: dict, origin: str) -> dict | None:
    if route == "/":
        return None
    parts = [p for p in route.strip("/").split("/") if p]
    paths = ["/"]
    for i in range(1, len(parts) + 1):
        item = "/" + "/".join(parts[:i]) + "/"
        if item in records and item not in paths:
            paths.append(item)
    items = []
    for position, path in enumerate(paths, 1):
        label = "MUSITU" if path == "/" else records[path]["title"].split(" — ")[0].strip()
        items.append({"@type": "ListItem", "position": position, "name": label, "item": origin + path})
    return {"@type": "BreadcrumbList", "@id": origin + route + "#breadcrumb", "itemListElement": items}

def schemas(route: str, records: dict, origin: str = ORIGIN) -> list[dict]:
    if origin != ORIGIN:
        raise ValueError("Unapproved structured-data origin")
    if route not in records or route == "/404/":
        return []
    info = records[route]
    result = []
    if route == "/":
        result.extend([
            {"@type": "Organization", "@id": origin + "/#organization", "name": "MUSITU", "url": origin + "/", "description": info["description"]},
            {"@type": "WebSite", "@id": origin + "/#website", "name": "MUSITU", "url": origin + "/", "inLanguage": "en", "publisher": {"@id": origin + "/#organization"}}
        ])
    trail = _trail(route, records, origin)
    if trail:
        result.append(trail)
    # Limited descriptive schema only: no unverified prices, ratings, installs, offers, or reviews.
    if route in ("/products/axiom/", "/products/foundry/studio/"):
        result.append({"@type": "SoftwareApplication", "name": "MUSITU Axiom" if route.endswith("/axiom/") else "MUSITU Studio", "url": origin + route, "description": info["description"], "publisher": {"@id": origin + "/#organization"}})
    return result

def seo_head(route: str, info: dict, records: dict, origin: str = ORIGIN) -> str:
    if route == "/404/":
        return ""
    if origin != ORIGIN:
        raise ValueError("Unapproved SEO origin")
    graph = {"@context": "https://schema.org", "@graph": schemas(route, records, origin)}
    # U+003C protects the JSON data block against HTML tag boundaries.
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return (
        '<meta property="og:site_name" content="MUSITU">\n'
        '<meta property="og:locale" content="en_US">\n'
        '<meta name="twitter:card" content="summary">\n'
        '<script type="application/ld+json">' + payload + '</script>\n'
    )
