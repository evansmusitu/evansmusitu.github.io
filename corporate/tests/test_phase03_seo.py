"""Phase 03 safety and source regressions; no cloud credentials or network access."""
from pathlib import Path
import json
import re
import sys
import unittest

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "scripts"))
from seo import ORIGIN, read_catalog, validate_catalog, schemas, seo_head
from build import ROUTES, META_CSP, render

class Phase03SEOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads((BASE / "content" / "pages.json").read_text(encoding="utf-8"))
        cls.shared = {p.stem: p.read_text(encoding="utf-8") for p in (BASE / "templates").glob("*.html")}

    def test_exact_33_indexable_core_routes_reconciled(self):
        catalog = validate_catalog(ROUTES)
        self.assertEqual(len(catalog["routes"]), 33)
        self.assertEqual(set(catalog["routes"]), set(self.records) - {"/404/"})
        self.assertEqual(len(set(x["primary_query"] for x in catalog["routes"].values())), 33)

    def test_no_unapproved_language_is_published(self):
        catalog = read_catalog()
        self.assertEqual(catalog["published_languages"], ["en"])
        self.assertEqual(set(catalog["unpublished_language_pilots"]), {"fr", "pt"})

    def test_homepage_graph_is_correct_and_disclosure_minimal(self):
        graph = schemas("/", self.records)
        self.assertEqual([x["@type"] for x in graph], ["Organization", "WebSite"])
        self.assertEqual(graph[0]["url"], ORIGIN + "/")
        self.assertEqual(graph[0]["name"], "MUSITU")
        self.assertNotIn("address", json.dumps(graph).lower())
        self.assertNotIn("registration", json.dumps(graph).lower())

    def test_products_have_description_not_invented_offers(self):
        for route in ("/products/axiom/", "/products/foundry/studio/"):
            graph = schemas(route, self.records)
            self.assertIn("SoftwareApplication", [x["@type"] for x in graph])
            self.assertFalse(any(k in json.dumps(graph) for k in ('"offers"','"aggregateRating"','"price"')))
            self.assertEqual(graph[-1]["url"], ORIGIN + route)

    def test_breadcrumbs_are_hierarchical_and_reciprocal(self):
        route = "/products/education/chemistry-rescue/"
        crumb = schemas(route, self.records)[0]
        links = [e["item"] for e in crumb["itemListElement"]]
        self.assertEqual(links, [ORIGIN + "/", ORIGIN + "/products/", ORIGIN + "/products/education/", ORIGIN + route])

    def test_jsonld_is_valid_json_with_safe_html_boundaries(self):
        h = seo_head("/", self.records["/"], self.records)
        payload = re.search(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S)
        self.assertIsNotNone(payload)
        graph = json.loads(payload.group(1))
        self.assertEqual(graph["@context"], "https://schema.org")
        self.assertEqual(len(graph["@graph"]), 2)
        hostile = dict(self.records["/"])
        hostile["description"] = "</script><script>alert(1)</script>"
        rendered = seo_head("/", hostile, {**self.records, "/": hostile})
        self.assertNotIn("</script><script>", rendered)
        self.assertIn(r"\u003c/script>", rendered)

    def test_production_only_and_404_exclusion(self):
        self.assertFalse(seo_head("/404/", self.records["/404/"], self.records))
        raw = seo_head("/products/axiom/", self.records["/products/axiom/"], self.records)
        prod = render("/products/axiom/", self.records["/products/axiom/"], self.shared, mode="production", origin=ORIGIN, seo_html=raw)
        review = render("/products/axiom/", self.records["/products/axiom/"], self.shared, mode="review")
        self.assertIn('type="application/ld+json"', prod)
        self.assertNotIn('type="application/ld+json"', review)
        self.assertIn('content="index,follow"', prod)
        self.assertIn('content="noindex,nofollow"', review)
        self.assertEqual(review.count("<script "), 2)
        self.assertIn("script-src 'self'", META_CSP)

    def test_every_production_page_has_expected_index_and_schema_signals(self):
        from public_seo_observer import MetadataParser
        catalog = validate_catalog(ROUTES)
        for route in sorted(catalog["routes"]):
            with self.subTest(route=route):
                seo = seo_head(route, self.records[route], self.records)
                content = render(route, self.records[route], self.shared, mode="production", origin=ORIGIN, seo_html=seo)
                parser = MetadataParser()
                parser.feed(content)
                self.assertEqual(parser.canonical, [ORIGIN + route])
                self.assertEqual(parser.robots, ["index,follow"])
                self.assertEqual(len(parser.jsonld), 1)
                kinds = {x.get("@type") for x in parser.jsonld[0].get("@graph", [])}
                self.assertTrue(({"Organization","WebSite"} if route == "/" else {"BreadcrumbList"}).issubset(kinds))
                if route in ("/products/axiom/", "/products/foundry/studio/"):
                    self.assertIn("SoftwareApplication", kinds)
                self.assertNotIn("Mhundwa Village", seo)

    def test_article_schema_requires_actual_publication_approval(self):
        from seo import approved_article_schema
        fixture = {
            "path": "/research/articles/synthetic-check/",
            "headline": "Synthetic research example",
            "description": "A synthetic editorial test, not a public article.",
            "date_published": "2026-11-07",
            "review_status": "approved",
            "publication_status": "published",
        }
        graph = approved_article_schema(fixture)
        self.assertEqual(graph["@type"], "Article")
        self.assertEqual(graph["mainEntityOfPage"]["@id"], ORIGIN + fixture["path"])
        self.assertEqual(graph["publisher"]["@id"], ORIGIN + "/#organization")
        for field, invalid in (
            ("review_status", "draft"), ("publication_status", "draft"),
            ("path", "/private/"), ("date_published", "")
        ):
            rejected = dict(fixture)
            rejected[field] = invalid
            with self.assertRaises(ValueError):
                approved_article_schema(rejected)

    def test_unknown_origin_fails_closed(self):
        with self.assertRaises(ValueError):
            schemas("/", self.records, "https://fake.example")
        with self.assertRaises(ValueError):
            seo_head("/", self.records["/"], self.records, "https://fake.example")


    def test_twelve_editorial_drafts_are_complete_and_gated(self):
        folder = BASE / "editorial" / "research-drafts"
        drafts = sorted(folder.glob("*.md"))
        self.assertEqual(len(drafts), 12)
        required = ("## Research question", "## Method and reproducibility",
            "## Worked conceptual example", "## Failure modes and how to challenge the result",
            "## Reviewer checklist", "## Scope and limitations", "## Background reference")
        for path in drafts:
            with self.subTest(article=path.name):
                content = path.read_text(encoding="utf-8")
                self.assertIn("not approved for public release", content)
                self.assertGreaterEqual(len(content.split()), 350)
                for heading in required:
                    self.assertIn(heading, content)
                self.assertIn("https://", content)
                self.assertNotIn("http://", content)
                self.assertIn("## Related MUSITU page", content)

    def test_language_pilot_is_explicitly_unpublished(self):
        data = json.loads((BASE / "content" / "localization-pilot.json").read_text(encoding="utf-8"))
        self.assertEqual(data["routing"]["default_language"], "en")
        self.assertFalse(data["routing"]["auto_translate"])
        self.assertFalse(data["routing"]["location_redirects"])
        self.assertEqual([x["language"] for x in data["published"]], ["en"])
        self.assertEqual({p["language"] for p in data["pilots"]}, {"fr","pt"})
        for p in data["pilots"]:
            self.assertTrue("DRAFT" in p["status"] or "PLANNED" in p["status"])
        self.assertEqual(len(next(p for p in data["pilots"] if p["language"]=="fr")["sample"]), 3)

    def test_public_observer_parser_is_read_only_and_jsonld_aware(self):
        from public_seo_observer import MetadataParser
        observer = MetadataParser()
        observer.feed('<meta name="robots" content="index,follow">'
                      '<link rel="canonical" href="https://mftintelligence.com/">'
                      '<script type="application/ld+json">'
                      '{"@context":"https://schema.org","@graph":[]}</script>')
        self.assertEqual(observer.robots, ["index,follow"])
        self.assertEqual(observer.canonical, [ORIGIN + "/"])
        self.assertEqual(observer.jsonld[0]["@context"], "https://schema.org")


    def test_hreflang_requires_published_reciprocal_equivalents(self):
        import seo as seo_module
        fn = getattr(seo_module, "approved_hreflang_links", None)
        self.assertTrue(callable(fn), "Missing reviewed-localization publishing contract")
        approved = {
            "en": {"/products/axiom/"},
            "fr": {"/fr/products/axiom/"},
        }
        equivalents = {"en": "/products/axiom/", "fr": "/fr/products/axiom/"}
        en_links = fn("/products/axiom/", equivalents, approved)
        fr_links = fn("/fr/products/axiom/", equivalents, approved)
        self.assertEqual(en_links, fr_links)
        self.assertIn('hreflang="fr" href="https://mftintelligence.com/fr/products/axiom/"', en_links)
        self.assertIn('hreflang="x-default" href="https://mftintelligence.com/products/axiom/"', en_links)
        with self.assertRaises(ValueError):
            fn("/products/axiom/", equivalents, {"en": {"/products/axiom/"}})
        with self.assertRaises(ValueError):
            fn("/products/axiom/", {"en": "/products/axiom/", "fr": "https://evil.example/"}, approved)
        with self.assertRaises(ValueError):
            fn("/fr/products/axiom/", equivalents, {"en": {"/products/axiom/"}, "fr": set()})
        with self.assertRaises(ValueError):
            fn("/private/", equivalents, approved)
        with self.assertRaises(ValueError):
            fn("/products/axiom/", equivalents, approved, origin="https://fake.example")

if __name__ == "__main__":
    unittest.main()
