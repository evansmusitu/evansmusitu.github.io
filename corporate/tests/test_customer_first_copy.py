"""Guard customer-facing product copy without weakening statutory disclosures.

These checks target public marketing pages, not the required legal documents.
The exact Axiom catalog and evidence record claims remain independently tested.
"""
from pathlib import Path
import json
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
PAGES=json.loads((ROOT/"content/pages.json").read_text(encoding="utf-8"))
RECORDS=json.loads((ROOT/"content/public-records.json").read_text(encoding="utf-8"))
PROHIBITED=(
    "availability and maturity",
    "what the evidence does not establish",
    "important boundaries",
    "publication gate",
    "staging-only review",
    "has not been independently confirmed",
    "not a promise of unrestricted anonymous use",
    "independently certified superiority",
    "no unrestricted enterprise",
    "not a general-availability",
    "a technical enquiry is not",
    "no live trading, promised financial outcome",
    "commercial general availability is not established",
    "no broker execution",
    "not a public production trading system",
    "no independent certification is implied",
    "a public live-status dashboard will be introduced only",
)

def page(route):
    return BeautifulSoup((DIST/route.lstrip("/")/"index.html").read_text(encoding="utf-8"),"html.parser")

def test_musitu_marketing_pages_have_no_internal_release_warning_banners():
    assert len(PAGES)==34
    for route in PAGES:
        if route.startswith("/legal/"):
            continue  # Preserve required policy and terms disclosures.
        text=page(route).get_text(" ",strip=True).lower()
        for phrase in PROHIBITED:
            assert phrase not in text,(route,phrase)
        assert not page(route).select(".gate-label"),route
        assert not page(route).find(string=lambda x: x and x.strip()=="NaN"),route
    assert "privacy" in page("/legal/privacy/").get_text(" ",strip=True).lower()
    assert "terms" in page("/legal/terms/").get_text(" ",strip=True).lower()

def test_axiom_directory_has_positive_action_instead_of_access_warning():
    main=page("/products/axiom/")
    directory=main.select_one("section#axiom-full-capabilities")
    assert directory is not None
    assert len(directory.select(".axiom-operation-list code"))==74
    assert len(directory.select(".axiom-domain"))==18
    assert not directory.select(".axiom-access-note,.notice")
    cta=directory.select_one(".axiom-explore-cta")
    assert cta and cta.select_one('a[href^="https://chatgpt.com/plugins/"]')
    assert cta.select_one("a")["aria-label"].startswith("Explore Axiom in ChatGPT")
    lead=main.select_one(".axiom-product-cta")
    assert lead and lead.select_one('a[href^="https://chatgpt.com/plugins/"]')
    assert "74 documented operations" in main.get_text(" ",strip=True)
    assert "Availability and maturity" not in main.get_text(" ",strip=True)

def test_live_news_developers_and_status_have_useful_content_not_internal_hold_notices():
    news=page("/news/");dev=page("/developers/");status=page("/status/")
    assert news.select_one('a[href="/products/axiom/#axiom-full-capabilities"]')
    assert "20 November 2026" in news.get_text(" ",strip=True)
    assert dev.select_one('a[href="/products/axiom/#axiom-full-capabilities"]')
    assert status.select_one('a[href="/support/"]')
    assert status.select_one('a[href="/news/"]')
    assert not any(".gate-label" in str(x) for x in [news,dev,status])

def test_evidence_dialog_and_compare_table_focus_on_facts():
    script=(DIST/"assets/site.js").read_text(encoding="utf-8")
    assert "['Scope of this record',rec.limits]" in script
    assert "['Technology focus','limits']" in script
    assert "['What was not established',rec.limits]" not in script
    assert "['Limits','limits']" not in script
    assert all(f["limits"].strip() and not f["limits"].startswith(("No ","Not ","Does not"))
               for f in RECORDS["families"])
    assert all(r["limits"].strip() and not r["limits"].startswith(("No ","Not ","Does not"))
               for r in RECORDS["evidence"])
    assert RECORDS["routes"] and len(RECORDS["routes"])==34

def test_marketing_remains_truthful_and_legal_disclosures_remain():
    ax=page("/products/axiom/").get_text(" ",strip=True)
    assert "74" in ax and "finance" in ax.lower()
    assert "research" in page("/products/fmi/").get_text(" ",strip=True).lower()
    assert "research" in page("/products/markets/").get_text(" ",strip=True).lower()
    assert "demonstration" in page("/products/foundry/studio/").get_text(" ",strip=True).lower()
    assert 'support@mftintelligence.com' in page("/legal/privacy/").get_text(" ",strip=True)
    assert 'support@mftintelligence.com' in page("/legal/terms/").get_text(" ",strip=True)
    for route in ("/","/products/axiom/","/products/fmi/","/products/markets/"):
        text=page(route).get_text(" ",strip=True).lower()
        assert "guaranteed financial returns" not in text
        assert "guaranteed academic results" not in text
        assert "fully licensed trading platform" not in text
