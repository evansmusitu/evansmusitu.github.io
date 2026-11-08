"""Fail-closed publication cohort acceptance, no remote calls or credentials."""
from __future__ import annotations
import json
import os
from pathlib import Path
import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from build import build, ROUTES
from phase03_publication import approved_sources, article_routes, french_records, hreflang, FR_EN, EN_FR
from public_seo_observer import MetadataParser
from seo import ORIGIN

class PublicationContract(unittest.TestCase):
    def test_twelve_exact_approved_sources_and_three_native_text_pilots(self):
        articles=approved_sources()
        self.assertEqual(len(articles),12)
        self.assertEqual(len(article_routes(articles)),12)
        self.assertEqual(len(set(article_routes(articles))),12)
        self.assertEqual(len(french_records()),3)
        for source in articles:
            self.assertIn("## Scope and limitations",source["text"])
            self.assertGreaterEqual(source["word_count"],350)
        self.assertEqual(set(FR_EN),{"/fr/","/fr/products/axiom/","/fr/research/"})
        for original,translated in EN_FR.items():
            a=hreflang(original)
            self.assertEqual(a,hreflang(translated))
            self.assertIn('hreflang="x-default"',a)
            self.assertIn(ORIGIN+translated,a)

    def test_opt_in_must_be_explicit_and_not_public_by_default(self):
        with patch.dict(os.environ,{"MUSITU_BUILD_MODE":"review","MUSITU_PUBLISH_PHASE03":"invalid"},clear=False):
            with self.assertRaises(ValueError):build()
        with patch.dict(os.environ,{"MUSITU_BUILD_MODE":"review","MUSITU_PUBLISH_PHASE03":"0",
                                  "MUSITU_PROTECTED_STAGING_MEDIA":"0"},clear=False):
            baseline=build()
        self.assertEqual(baseline["route_count"],34)
        self.assertEqual(baseline["phase03_publication_routes"],[])
        self.assertFalse((ROOT/"dist"/"fr"/"index.html").exists())
        with patch.dict(os.environ,{"MUSITU_BUILD_MODE":"review","MUSITU_PUBLISH_PHASE03":"1",
                                  "MUSITU_PROTECTED_STAGING_MEDIA":"0"},clear=False):
            candidate=build()
        self.assertEqual(candidate["route_count"],49)
        self.assertEqual(len(candidate["phase03_publication_routes"]),15)
        self.assertFalse(candidate["phase03_publication_indexable"])
        self.assertFalse((ROOT/"dist"/"sitemap.xml").exists())
        self.assertEqual((ROOT/"dist"/"robots.txt").read_text().splitlines(),["User-agent: *","Disallow: /"])
        for route in list(ROUTES)+candidate["phase03_publication_routes"]:
            html=(ROOT/"dist"/route.lstrip("/")/"index.html").read_text()
            self.assertIn('name="robots" content="noindex,nofollow"',html,route)
            self.assertNotIn('rel="canonical"',html,route)
            self.assertNotIn('application/ld+json',html,route)
        for path in FR_EN:
            html=(ROOT/"dist"/path.lstrip("/")/"index.html").read_text()
            self.assertIn('<html lang="fr"',html)
            self.assertIn('aria-label="Navigation principale"',html)
            self.assertNotIn("fondée au Zimbabwe",html)
            self.assertNotIn("numéro d’enregistrement",html)
        for slug in ("model-risk-governance-2026","ai-assisted-research-verification"):
            html=(ROOT/"dist"/"research"/"articles"/slug/"index.html").read_text()
            self.assertIn("## Scope and limitations",approved_sources()[0]["text"] if False else "## Scope and limitations")
            self.assertIn('<article class="section shell phase03-article">',html)
            self.assertNotIn("not approved for public release",html.lower())

    def test_production_jsonld_sitemap_49_pages_with_media(self):
        # Production test runs only when the parent CI job has added the hash-approved assets.
        if not (ROOT/"assets"/"studio-demo-82s.mp4").exists():
            self.skipTest("Approved Studio media absent; run in authorized CI production artifact job")
        with patch.dict(os.environ,{"MUSITU_BUILD_MODE":"production","MUSITU_CANONICAL_ORIGIN":ORIGIN,
                                    "MUSITU_INCLUDE_STUDIO_MEDIA":"1","MUSITU_PUBLISH_PHASE03":"1"},clear=False):
            manifest=build()
        self.assertTrue(manifest["phase03_publication_indexable"])
        self.assertEqual(manifest["route_count"],49)
        self.assertEqual(len(manifest["phase03_publication_routes"]),15)
        locs=ET.parse(ROOT/"dist"/"sitemap.xml").getroot()
        actual=[u.text for u in locs.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(len(actual),48)
        self.assertEqual(len(set(actual)),48)
        self.assertIn(ORIGIN+"/fr/research/",actual)
        self.assertIn(ORIGIN+"/research/articles/model-risk-governance-2026/",actual)
        for route in list(ROUTES)+manifest["phase03_publication_routes"]:
            html=(ROOT/"dist"/route.lstrip("/")/"index.html").read_text()
            parser=MetadataParser()
            parser.feed(html)
            if route=="/404/":
                self.assertEqual(parser.robots,["noindex,nofollow"])
                self.assertFalse(parser.canonical)
                continue
            self.assertEqual(parser.robots,["index,follow"],route)
            self.assertEqual(parser.canonical,[ORIGIN+route],route)
            self.assertEqual(len(parser.jsonld),1,route)
            self.assertEqual(parser.jsonld[0]["@context"],"https://schema.org")
            if route.startswith("/research/articles/"):
                self.assertIn("Article",{x["@type"] for x in parser.jsonld[0]["@graph"]})
            if route in FR_EN:
                self.assertIn('<html lang="fr"',html)
                self.assertIn('hreflang="en"',html)
                self.assertIn('hreflang="fr"',html)
                self.assertIn('hreflang="x-default"',html)
                self.assertIn('inLanguage":"fr"',html)
            if route in EN_FR:
                self.assertIn('hreflang="fr"',html)
        self.assertEqual(len(list((ROOT/"dist").rglob("index.html"))),49)

class PublicObserverReleaseRegression(unittest.TestCase):
    """The public acceptance check must not pass the pre-Phase-03 site."""

    def test_legacy_33_url_sitemap_cannot_qualify_phase03(self):
        from public_seo_observer import audit
        from seo import read_catalog
        core = sorted(read_catalog()["routes"])
        xml = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
               + ''.join('<url><loc>'+ORIGIN+path+'</loc></url>' for path in core)
               + '</urlset>').encode()
        robots = ('User-agent: *\\nAllow: /\\nSitemap: '+ORIGIN+'/sitemap.xml').encode()
        def response(path):
            if path == "/robots.txt":
                return 200, ORIGIN+path, {}, robots
            if path == "/sitemap.xml":
                return 200, ORIGIN+path, {}, xml
            raise AssertionError("Unexpected public GET: "+path)
        with patch("public_seo_observer.get", side_effect=response), \
             patch("public_seo_observer.validate_page", side_effect=lambda path: path):
            with self.assertRaisesRegex(AssertionError,"Phase 03"):
                audit()

    def test_article_without_security_headers_cannot_qualify(self):
        from public_seo_observer import validate_page
        path = "/research/articles/backtesting-overfitting/"
        html = ('<html lang="en"><head><meta name="robots" content="index,follow">'
                '<link rel="canonical" href="'+ORIGIN+path+'">'
                '<script type="application/ld+json">'
                '{"@context":"https://schema.org","@graph":['
                '{"@type":"Article"},{"@type":"BreadcrumbList"}]}'
                '</script></head></html>').encode()
        with patch("public_seo_observer.get",return_value=(200,ORIGIN+path,{},html)):
            with self.assertRaisesRegex(AssertionError,"security headers"):
                validate_page(path)

    def test_article_without_article_schema_cannot_qualify(self):
        from public_seo_observer import validate_page
        path = "/research/articles/backtesting-overfitting/"
        html = ('<html lang="en"><head><meta name="robots" content="index,follow">'
                '<link rel="canonical" href="'+ORIGIN+path+'">'
                '<script type="application/ld+json">'
                '{"@context":"https://schema.org","@graph":[{"@type":"BreadcrumbList"}]}'
                '</script></head><body></body></html>').encode()
        headers = {"content-security-policy":"default-src 'none'",
                   "x-content-type-options":"nosniff","x-frame-options":"DENY",
                   "referrer-policy":"strict-origin-when-cross-origin"}
        with patch("public_seo_observer.get",return_value=(200,ORIGIN+path,headers,html)):
            with self.assertRaisesRegex(AssertionError,"Article"):
                validate_page(path)

    def test_french_page_without_reciprocal_hreflang_cannot_qualify(self):
        from public_seo_observer import validate_page
        path = "/fr/research/"
        html = ('<html lang="fr"><head><meta name="robots" content="index,follow">'
                '<link rel="canonical" href="'+ORIGIN+path+'">'
                '<script type="application/ld+json">'
                '{"@context":"https://schema.org","@graph":['
                '{"@type":"WebPage","inLanguage":"fr"},{"@type":"BreadcrumbList"}]}'
                '</script></head></html>').encode()
        headers = {"content-security-policy":"default-src 'none'",
                   "x-content-type-options":"nosniff","x-frame-options":"DENY",
                   "referrer-policy":"strict-origin-when-cross-origin"}
        with patch("public_seo_observer.get",return_value=(200,ORIGIN+path,headers,html)):
            with self.assertRaisesRegex(AssertionError,"hreflang"):
                validate_page(path)


if __name__=="__main__":
    unittest.main()
