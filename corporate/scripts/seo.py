"""Non-executable, truth-constrained production SEO metadata for the 34-route corporate core.

All publicly generated organization attributes must already be visible on the website.
No business address, registered legal identifier, offer, aggregateRating, review, price,
social profile, author biography or external URL is inferred.
"""
from __future__ import annotations
import html
import json
import re
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

def approved_hreflang_links(
    route: str, equivalents: dict[str, str],
    published_routes_by_language: dict[str, set[str]],
    origin: str = ORIGIN
) -> str:
    """Emit reciprocal alternate links only for confirmed, published translations.

    Call this with each localized page's route using the same equivalence
    group. The current corporate build deliberately passes no such group.
    """
    if origin != ORIGIN:
        raise ValueError("Unapproved hreflang origin")
    if not isinstance(equivalents, dict) or len(equivalents) < 2 or "en" not in equivalents:
        raise ValueError("At least English and one approved translation are required")
    if not isinstance(published_routes_by_language, dict) or route not in equivalents.values():
        raise ValueError("Localized page must belong to its equivalence group")

    for language, path in equivalents.items():
        if language not in {"en", "fr", "pt"}:
            raise ValueError("Unsupported or unreviewed language")
        if not isinstance(path, str) or not re.fullmatch(r"/(?:[a-z0-9-]+/)*", path):
            raise ValueError("Malformed localized canonical route")
        if language == "en":
            if path.startswith(("/fr/", "/pt/")):
                raise ValueError("English route points to a translation")
        elif not path.startswith("/" + language + "/"):
            raise ValueError("Localized route lacks the corresponding language prefix")
        published = published_routes_by_language.get(language)
        if not isinstance(published, (set, frozenset)) or path not in published:
            raise ValueError("Unverified or unpublished localized route")

    lines = [
        '<link rel="alternate" hreflang="' + language
        + '" href="' + html.escape(origin + equivalents[language], quote=True) + '">'
        for language in sorted(equivalents)
    ]
    lines.append('<link rel="alternate" hreflang="x-default" href="'
                 + html.escape(origin + equivalents["en"], quote=True) + '">')
    return "\n".join(lines) + "\n"

def approved_article_schema(article: dict, origin: str = ORIGIN) -> dict:
    """Return Article JSON-LD only for separately authorized, actually published research.

    Existing editorial .md drafts intentionally do not meet this contract.
    """
    if origin != ORIGIN:
        raise ValueError("Unapproved article publication origin")
    if article.get("review_status") != "approved" or article.get("publication_status") != "published":
        raise ValueError("Unreviewed or unlaunched research must not receive public Article markup")
    route = article.get("path")
    if not isinstance(route, str) or not route.startswith("/research/articles/") or not route.endswith("/"):
        raise ValueError("Article requires canonical research URL")
    for key in ("headline", "description", "date_published"):
        if not isinstance(article.get(key), str) or not article[key].strip():
            raise ValueError("Article missing verified " + key)
    # Publisher and author are organizational until an actual named reviewer
    # explicitly approves a personal public author credit.
    return {"@context": "https://schema.org", "@type": "Article",
        "headline": article["headline"], "description": article["description"],
        "datePublished": article["date_published"], "inLanguage": "en",
        "mainEntityOfPage": {"@type": "WebPage", "@id": origin + route},
        "author": {"@type": "Organization", "name": "MUSITU"},
        "publisher": {"@id": origin + "/#organization"}}

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
