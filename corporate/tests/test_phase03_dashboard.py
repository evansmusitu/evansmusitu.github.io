"""Private no-tracking international growth dashboard source constraints."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from render_growth_dashboard import render,write_dashboard

class DashboardTests(unittest.TestCase):
    def fixture(self):
        return {
          "document":"MUSITU-PHASE03-INTERNATIONAL-GROWTH-AGGREGATE-1",
          "query_text_exported":False,"visitor_or_contact_identifiers_exported":False,
          "cross_provider_positions_blended":False,
          "country_by_provider_daily":[
            {"provider":"google","date":"2026-11-06","dimension":"ZW","clicks":1,
             "impressions":5,"ctr":0.2,"average_search_position":1.2}],
          "query_theme_by_provider_daily":[],
          "qualified_enquiries_by_day_and_channel":[]}
    def test_single_sourced_country_is_not_inferred_as_global_growth(self):
        page=render(self.fixture())
        self.assertIn("MUSITU — International search growth",page)
        self.assertIn("No verified country-level records imported",page)
        self.assertIn("Numbers are unavailable, not zero.",page)
        self.assertIn("ZW",page)
        self.assertIn("noindex,nofollow",page)
        self.assertNotIn("<script",page.lower())
        self.assertNotIn("http://",page)
        self.assertNotIn("https://",page)
    def test_no_raw_query_email_or_unapproved_metric_export(self):
        row=self.fixture()
        row["country_by_provider_daily"][0]["email"]="private@example.com"
        with self.assertRaises(ValueError):render(row)
        row=self.fixture()
        row["query_theme_by_provider_daily"]=[{
          "provider":"google","date":"2026-11-06","dimension":"someone@example.com",
          "clicks":1,"impressions":5,"ctr":0.2,"average_search_position":1.2}]
        with self.assertRaises(ValueError):render(row)
        row=self.fixture()
        row["visitor_or_contact_identifiers_exported"]=True
        with self.assertRaises(ValueError):render(row)
    def test_private_output_is_no_overwrite_and_no_repo_write(self):
        report=self.fixture()
        with self.assertRaises(ValueError):
            write_dashboard(report,ROOT/"dist"/"improper-public.html")
        with tempfile.TemporaryDirectory() as work:
            target=Path(work)/"private-growth.html"
            write_dashboard(report,target)
            self.assertTrue(target.is_file())
            with self.assertRaises(FileExistsError):write_dashboard(report,target)

if __name__=="__main__":
  unittest.main()
