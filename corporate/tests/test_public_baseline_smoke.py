"""Offline unit tests for the bounded public production baseline observer.

Only mock responses. Never touch the live host in unit tests or change it.
"""
from __future__ import annotations
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import public_baseline_smoke as site


SECURITY = {
    "content-security-policy": "default-src 'none'; object-src 'none'; frame-ancestors 'none'",
    "x-content-type-options": "nosniff",
}


def fake_get(path):
    origin = site.ORIGIN
    if path in site.PAGE_PATHS:
        body = (
            '<!doctype html><html lang="en"><head>'
            '<meta name="robots" content="index,follow">'
            '<link rel="canonical" href="' + origin + path + '">'
            '</head><body><main id="main"><h1>MUSITU</h1></main></body></html>'
        ).encode()
        return 200, origin + path, SECURITY, body
    if path == site.NEGATIVE_PATH:
        return 404, origin + path, SECURITY, (
            '<html lang="en"><head><meta name="robots" content="noindex,nofollow">'
            '</head><body><main id="main"><h1>Not found</h1></main></body></html>'
        ).encode()
    if path == "/manifest.json":
        return 404, origin + path, SECURITY, b""
    if path == "/robots.txt":
        return 200, origin + path, {}, (
            "User-agent: *\nAllow: /\nSitemap: " + origin + "/sitemap.xml\n"
        ).encode()
    if path == "/sitemap.xml":
        return 200, origin + path, {}, (
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            + "".join("<url><loc>" + origin + p + "</loc></url>" for p in site.PAGE_PATHS)
            + "</urlset>"
        ).encode()
    raise AssertionError("Unexpected route " + path)


class PublicBaselineSmokeUnitTests(unittest.TestCase):
    def test_full_pass_reports_live_baseline_not_candidate_acceptance(self):
        with patch.object(site, "get", side_effect=fake_get) as get:
            result = site.audit()
        self.assertEqual(get.call_count, len(site.PAGE_PATHS) + 4)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["candidate_hosted_acceptance"])
        self.assertFalse(result["human_visual_review"])
        self.assertFalse(result["core_web_vitals_test"])
        self.assertEqual(result["production_mutations"], 0)
        self.assertEqual(result["discovery"]["sitemap_entries"], 4)
        self.assertFalse(result["public_build_metadata"]["internal_release_fields_exposed"])

    def test_exposed_internal_build_flags_are_detected_without_copying_values(self):
        def exposed(path):
            if path == "/manifest.json":
                return 200, site.ORIGIN + path, {"content-type": "application/json"}, (
                    b'{"production_approved":false,"brand_master_sha256":"not-for-public-use"}'
                )
            return fake_get(path)
        with patch.object(site, "get", side_effect=exposed):
            result = site.audit()
        self.assertEqual(result["public_build_metadata"]["http_status"], 200)
        self.assertTrue(result["public_build_metadata"]["internal_release_fields_exposed"])
        self.assertNotIn("brand_master_sha256", str(result))
        self.assertNotIn("not-for-public-use", str(result))

    def test_security_header_regression_is_hard_failure(self):
        with self.assertRaisesRegex(AssertionError, "CSP protection"):
            site.assert_security_headers("/", {"x-content-type-options": "nosniff"})

    def test_unknown_page_as_soft_404_fails_closed(self):
        def soft404(path):
            data = fake_get(path)
            return (200, *data[1:]) if path == site.NEGATIVE_PATH else data
        with patch.object(site, "get", side_effect=soft404):
            with self.assertRaisesRegex(AssertionError, "not HTTP 404"):
                site.audit()

    def test_missing_live_index_page_fails_closed(self):
        def broken(path):
            status, url, headers, data = fake_get(path)
            if path == "/contact/":
                return 404, url, headers, data
            return status, url, headers, data
        with patch.object(site, "get", side_effect=broken):
            with self.assertRaisesRegex(AssertionError, "canonical transport"):
                site.audit()

    def test_off_origin_paths_are_rejected_before_network(self):
        for route in ("https://not-musitu.invalid/", "/users/private/", "//evil.com/"):
            with self.subTest(route=route), self.assertRaises(ValueError):
                site.get(route)

    def test_unexpected_off_origin_sitemap_fails_closed(self):
        def broken(path):
            if path == "/sitemap.xml":
                status, url, headers, data = fake_get(path)
                return status, url, headers, data.replace(
                    (site.ORIGIN + "/contact/").encode(), b"https://elsewhere.example/contact/"
                )
            return fake_get(path)
        with patch.object(site, "get", side_effect=broken):
            with self.assertRaisesRegex(AssertionError, "off-origin"):
                site.audit()

if __name__ == "__main__":
    unittest.main()
