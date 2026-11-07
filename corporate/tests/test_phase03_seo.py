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
        payload = re.search(r'<script type="application/ld\\+json">(.*?)</script>', h, flags=re.S)
        self.assertIsNotNone(payload)
        graph = json.loads(payload.group(1))
        self.assertEqual(graph["@context"], "https://schema.org")
        self.assertEqual(len(graph["@graph"]), 2)
        hostile = dict(self.records["/"])
        hostile["description"] = "</script><script>alert(1)</script>"
        rendered = seo_head("/", hostile, {**self.records, "/": hostile})
        self.assertNotIn("</script><script>", rendered)
        self.assertIn(r"\\u003c/script>", rendered)

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

    def test_unknown_origin_fails_closed(self):
        with self.assertRaises(ValueError):
            schemas("/", self.records, "https://fake.example")
        with self.assertRaises(ValueError):
            seo_head("/", self.records["/"], self.records, "https://fake.example")

if __name__ == "__main__":
    unittest.main()
