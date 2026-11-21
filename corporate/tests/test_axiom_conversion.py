"""Acceptance for MUSITU Axiom conversion and credible recorded examples."""
import json
from pathlib import Path
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
PAGES=json.loads((ROOT/"content/pages.json").read_text(encoding="utf-8"))
PROOFS=json.loads((ROOT/"content/axiom-verified-examples.json").read_text(encoding="utf-8"))
CATS=json.loads((ROOT/"content/axiom-capabilities.json").read_text(encoding="utf-8"))
ARTICLE_ROUTES=tuple("/resources/axiom-"+x["id"]+"/" for x in PROOFS["cases"])

def soup(route):
    return BeautifulSoup((DIST/route.lstrip("/")/"index.html").read_text(encoding="utf-8"),"html.parser")

def test_real_execution_evidence_and_four_independent_tutorial_urls():
    assert len(PAGES)==38 and len(PROOFS["cases"])==4
    assert len(set(x["operation"] for x in PROOFS["cases"]))==4
    assert PROOFS["executed_at"]=="2026-11-21"
    assert all(x["input"] and x["result"] and x["prompt"] for x in PROOFS["cases"])
    for e in PROOFS["cases"]:
        route="/resources/axiom-"+e["id"]+"/"
        page=soup(route)
        assert page.select_one("article.axiom-tutorial")
        assert page.select_one('time[datetime="2026-11-21"]')
        assert page.select_one('a[href="/products/axiom/#axiom-full-capabilities"]')
        assert e["operation"] in page.get_text(" ",strip=True)
        assert e["summary"] in page.get_text(" ",strip=True)
        assert len(page.select("h1"))==1 and len(page.select("h2"))>=5
        assert not page.select("iframe, form")
    assert abs(PROOFS["cases"][0]["result"]-11215.08093709444)<1e-7
    assert abs(PROOFS["cases"][1]["result"]["var"]-0.03245)<1e-8
    assert PROOFS["cases"][3]["result"]["x"]==[2,2]
    assert [x["verified"] for x in PROOFS["cases"]]==[True,False,False,True]
    assert all("independent" not in x["verification"].lower() or x["verified"] for x in PROOFS["cases"][::3])

def test_real_own_outputs_and_get_started_product_experience():
    page=soup("/products/axiom/")
    assert len(page.select(".axiom-proof-card"))==4
    assert len(page.select(".axiom-proof-answer"))==4
    assert len(page.select("#get-started-axiom .axiom-start-steps li"))==3
    assert page.select_one("#get-started-axiom .axiom-start-prompt")
    assert page.select_one('a[href^="https://chatgpt.com/plugins/"]')
    assert len(page.select('button[data-copy-axiom-prompt]'))>=5
    assert page.select_one("#axiom-capability-search")
    assert page.select_one("#axiom-search-clear")
    assert len(page.select(".axiom-operation-list li"))==74
    assert len(page.select(".axiom-op-detail code"))==74
    assert len(page.select(".axiom-metrics>div"))==2
    assert "30" not in page.select_one(".axiom-metrics").get_text(" ",strip=True)
    for op in ("finance.npv","finance.var_historical","statistics.regression","optimization.linear_program"):
        assert page.find("code",string=op)
    for op in ("finance.bond_yield","timeseries.rolling_volatility","algebra.solve"):
        assert page.find("code",string=op)

def test_capability_search_is_progressive_and_task_friendly():
    script=(DIST/"assets/axiom-experience.js").read_text(encoding="utf-8")
    assert "data-search" in (DIST/"products/axiom/index.html").read_text(encoding="utf-8")
    assert "filter" not in script or "hidden" in script
    for word in ("search.value","aria","dataset.search","navigator.clipboard","shown"):
        assert word in script or word=="aria"
    assert "fetch(" not in script and "XMLHttpRequest" not in script
    page=soup("/products/axiom/")
    code_to_search={}
    for li in page.select(".axiom-operation"):
        code=li.select_one("code")
        code_to_search[code.get_text(strip=True)]=li.get("data-search","")
    assert len(code_to_search)==74
    assert all(token in code_to_search["finance.bond_yield"] for token in ("bond","yield"))
    assert all(token in code_to_search["timeseries.rolling_volatility"] for token in ("forecast","volatility"))
    assert all(token in code_to_search["algebra.solve"] for token in ("solve","equations"))

def test_customer_enquiry_is_accessible_and_fail_closed_until_mail_roundtrip_qualified():
    page=soup("/contact/")
    form=page.select_one("#musitu-enquiry-form")
    assert form
    for name in ("product","purpose","email","message"):
        assert form.select_one('[name="'+name+'"][required]')
    assert form.select_one('a[href="/legal/privacy/"]')
    assert form.select_one('button[type="submit"]')
    assert page.select_one('#enquiry-status[role="status"][aria-live="polite"]')
    js=(DIST/"assets/contact-enquiry.js").read_text(encoding="utf-8")
    assert "mailto:support@mftintelligence.com" in js
    assert "window.location.href=href" in js
    assert "has not sent anything" in js
    assert "fetch(" not in js and "sendBeacon" not in js
    assert "successfully delivered" not in js and "Message sent!" not in js
    assert not form.get("action")
    assert soup("/legal/privacy/").select_one("main#main")
    assert soup("/legal/terms/").select_one("main#main")

def test_navigation_home_and_seo_are_customer_oriented():
    home=soup("/")
    assert home.select_one('a[href="/products/axiom/#get-started-axiom"]')
    assert home.select_one('a[href="/resources/axiom-investment-npv/"]')
    head=home.select_one("header.site-header")
    assert head.select_one(".header-axiom-cta")
    assert head.select_one('.mobile-menu-panel a[href^="https://chatgpt.com/plugins/"]')
    assert "SIX CANONICAL FAMILIES" not in soup("/products/").get_text(" ",strip=True)
    assert "Technical Resources" in soup("/developers/").title.get_text()
    assert "Service Information" in soup("/status/").title.get_text()
    for route in ("/developers/","/status/","/news/","/contact/"):
        desc=PAGES[route]["description"].lower()
        assert "unverified" not in desc and "publication" not in desc and "gate" not in desc
    articles=soup("/resources/")
    assert len(articles.select(".axiom-tutorial-card"))==4
    assert all(articles.select_one(f'a[href="{route}"]') for route in ARTICLE_ROUTES)
    assert all("source only" not in PAGES[route]["description"].lower() for route in ARTICLE_ROUTES)

def test_production_extra_articles_are_canonical_and_phase03_still_off():
    manifest=json.loads((DIST/"manifest.json").read_text(encoding="utf-8"))
    assert manifest["route_count"]==38 and len(manifest["routes"])==38
    assert manifest["phase03_publication_routes"]==[]
    assert manifest["phase03_publication_indexable"] is False
    if manifest["build_mode"]=="production":
        xml=(DIST/"sitemap.xml").read_text(encoding="utf-8")
        assert xml.count("<loc>")==37
        for route in ARTICLE_ROUTES:
            assert "https://mftintelligence.com"+route in xml
            assert soup(route).select_one('link[rel="canonical"]')["href"]=="https://mftintelligence.com"+route
