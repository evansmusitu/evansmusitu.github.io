"""Synthetic-only tests; must not use actual account queries or visitor data."""
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import international_growth_report as g


class GrowthSourceContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write_csv(self, name, fields, records):
        path = self.dir / name
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(fields)
            writer.writerows(records)
        return path

    def test_aggregate_country_query_themes_and_enquiries_without_identifiers(self):
        country = self.write_csv("country.csv", g.COUNTRY_FIELDS, [
            ["google", "2026-09-01", "ZW", 7, 70, "9.2"],
            ["google", "2026-09-02", "ZW", 1, 10, "12.0"],
            ["bing", "2026-09-01", "ZW", 2, 25, "7.5"],
            ["google", "2026-09-01", "ZA", 0, 0, ""],
        ])
        query = self.write_csv("queries.csv", g.QUERY_FIELDS, [
            ["google", "2026-09-01", "musitu axiom", 2, 20, 8],
            ["google", "2026-09-01", "model risk governance", 1, 30, "12.5"],
            ["google", "2026-09-01", "personal@example.com", 3, 10, 5],
            ["bing", "2026-09-01", "3d export", 1, 20, 7],
        ])
        contacts = self.write_csv("enquiries.csv", g.ENQUIRY_FIELDS, [
            ["2026-09-01", "google_organic", 2],
            ["2026-09-01", "unattributed", 4],
        ])
        result = g.make_report(country, query, contacts)
        countries = {(r["provider"], r["date"], r["dimension"]): r
                     for r in result["country_by_provider_daily"]}
        self.assertEqual(len(countries), 4)
        self.assertEqual(countries[("google", "2026-09-01", "ZW")]["ctr"], 0.1)
        self.assertIsNone(countries[("google", "2026-09-01", "ZA")]["ctr"])
        self.assertEqual(len(result["query_theme_by_provider_daily"]), 3)
        self.assertEqual(result["coverage"]["providers_present"], ["bing", "google"])
        self.assertEqual(result["coverage"]["countries_present"], ["ZA", "ZW"])
        self.assertEqual(sum(x["qualified_enquiries"] for x in result["qualified_enquiries_by_day_and_channel"]), 6)
        for claim in ("live_search_console_access_verified", "live_bing_webmaster_access_verified",
                      "sitemap_submission_claimed", "indexing_claimed", "query_text_exported",
                      "cross_provider_positions_blended", "visitor_or_contact_identifiers_exported"):
            self.assertIs(result[claim], False)
        serialized = json.dumps(result)
        for raw in ("personal@example.com", "musitu axiom", "model risk governance"):
            self.assertNotIn(raw, serialized)
        dest = self.dir / "private.json"
        g.write_private_report(result, dest)
        self.assertEqual(json.loads(dest.read_text()), result)
        self.assertEqual(dest.stat().st_mode & 0o777, 0o600)
        with self.assertRaises(FileExistsError):
            g.write_private_report(result, dest)

    def test_fail_closed_on_missing_bad_and_duplicate_source(self):
        invalid = [
            [["google", "2026-09-01", "ZW", 10, 9, 3]],
            [["google", "2026-09-01", "ZW", 1, 10, -3]],
            [["google", "2026-09-01", "Zimbabwe", 1, 10, 3]],
            [["unknown", "2026-09-01", "ZW", 1, 10, 3]],
            [["google", "2026-19-01", "ZW", 1, 10, 3]],
            [["google", "2026-09-01", "ZW", 1, 10, 3],
             ["google", "2026-09-01", "ZW", 1, 10, 3]],
            [],
        ]
        for i, rows in enumerate(invalid):
            path = self.write_csv("bad%d.csv" % i, g.COUNTRY_FIELDS, rows)
            with self.subTest(case=i), self.assertRaises(ValueError):
                g.make_report(path)
        bad_columns = self.write_csv("pii.csv", ["email", "clicks"],
                                     [["private@example.org", 3]])
        with self.assertRaises(ValueError):
            g.make_report(bad_columns)
        good = self.write_csv("good.csv", g.COUNTRY_FIELDS,
                              [["google", "2026-09-01", "ZW", 1, 10, 3]])
        report = g.make_report(good)
        for dest in (g.BASE / "dist" / "metrics.json",
                     g.BASE / "content" / "leaked.json"):
            with self.assertRaises(ValueError):
                g.write_private_report(report, dest)

    def test_sensitive_queries_and_invalid_enquiry_channels(self):
        good = self.write_csv("good.csv", g.COUNTRY_FIELDS,
                              [["google", "2026-09-01", "ZW", 1, 10, 3]])
        query = self.write_csv("private-queries.csv", g.QUERY_FIELDS,
                               [["google", "2026-09-01", "someone@example.com", 1, 2, 4]])
        output = g.make_report(good, query)
        self.assertEqual(output["query_theme_by_provider_daily"], [])
        self.assertTrue(output["coverage"]["query_export_supplied"])
        contacts = self.write_csv("unsafe-enquiries.csv", g.ENQUIRY_FIELDS,
                                  [["2026-09-01", "customer@example.com", 1]])
        with self.assertRaises(ValueError):
            g.make_report(good, enquiry_file=contacts)
