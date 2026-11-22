"""Source and artifact acceptance for customer-facing Axiom onboarding.

Public examples reflect actual certified Axiom calls on fictional inputs.
The website performs no remote model execution and does not send contact mail.
"""
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/"dist"
sys.path.insert(0,str(ROOT/"scripts"))
from axiom_showcase import load_axiom_demonstrations, render_axiom_showcase

def page(route):
    return BeautifulSoup((DIST/route.lstrip("/")/"index.html").read_text(encoding="utf-8"),"html.parser")

def test_twenty_examples_match_executed_axiom_values():
    data=load_axiom_demonstrations()
    assert data["executed_date"]=="2026-11-21"
    examples=data["examples"]
    assert len(examples)==20
    assert [x["operation"] for x in examples[:4]]==[
        "finance.npv","statistics.describe","finance.black_scholes",
        "optimization.linear_program"
    ]
    assert examples[0]["result"]=="+721.26 units"
    assert examples[1]["result"]=="Mean 18.33 · median 18.5"
    assert examples[2]["result"]=="7.57 model units"
    assert examples[3]["result"]=="Maximum 36 · x=2, y=6"
    assert "Independent" in examples[0]["verification"]
    assert "Independent" in examples[3]["verification"]
    assert all("Independent" not in examples[i]["verification"] for i in [1,2])
    assert "fictional" in data["provenance"].lower()
    assert len({x["operation"] for x in examples}) == 20
    assert all(isinstance(x["arguments"], dict) and x["method"] for x in examples)
    assert all(x["evidence_status"] == "Recorded Axiom calculation" for x in examples[4:])
    assert examples[4]["operation"] == "finance.var_historical"
    assert examples[4]["result"] == "3.245% loss per period"
    assert examples[5]["operation"] == "statistics.regression"
    assert "2.0083" in examples[5]["result"]
    assert examples[12]["operation"] == "finance.bond_yield"
    assert examples[12]["result"] == "4.5483% annual yield"

def test_axiom_product_renders_onboarding_and_search_without_giving_up_directory():
    soup=page("/products/axiom/")
    assert soup.select_one("section#axiom-start")
    assert soup.select_one("section#axiom-demonstrations")
    assert len(soup.select(".axiom-demo-card"))==20
    assert len(soup.select(".axiom-demo-prompt"))==20
    assert len(soup.select("[data-axiom-copy]"))==25
    assert len(soup.select(".axiom-demo-output strong"))==20
    assert len(soup.select(".axiom-starter-card"))==5
    assert len(soup.select(".axiom-demo-method pre code"))==20
    assert len(soup.select(".axiom-operation-tech"))==74
    assert len(soup.select(".axiom-raw-schema"))==74
    assert len(soup.select(".axiom-parameter-list > div"))==193
    assert not soup.find(string=lambda x:x and "AXIOM_AUTHENTIC_EXAMPLES" in x)
    assert soup.select_one("#axiom-capability-search[type=search][maxlength='90']")
    assert soup.select_one("#axiom-capability-count[aria-live=polite]")
    assert soup.select_one("#axiom-capability-reset")
    assert len(soup.select("[data-axiom-category]"))==18
    assert len(soup.select("[data-axiom-operation]"))==74
    assert len(soup.select("[data-axiom-nav]"))==18
    assert len(soup.select(".axiom-operation-tech > p > code"))==74
    assert len({c.get_text(strip=True) for c in soup.select(".axiom-operation-tech > p > code")})==74
    assert not soup.select("section#axiom-demonstrations script, section#axiom-start iframe")

def test_starting_axiom_is_a_single_high_visibility_action_on_header_and_homepage():
    home=page("/")
    assert home.select_one('main .hero-actions a.button-primary[href="/products/axiom/#axiom-start"]')
    header=home.select_one("header.site-header")
    assert header
    assert len(header.select('a.header-axiom-cta[href="/products/axiom/#axiom-start"]'))==1
    assert len(header.select('a.mobile-primary-axiom[href="/products/axiom/#axiom-start"]'))==1
    assert header.select_one('a[href="/experiences/intelligence/"]')
    assert header.select_one('[data-open="ask-dialog"]')
    ax=page("/products/axiom/")
    assert ax.select_one('a[href^="https://chatgpt.com/plugins/"][target="_blank"][rel*="noopener"]')
    assert len(ax.select(".axiom-start-steps > li"))==3
    assert ax.select_one('section#axiom-start a[aria-label="Open Axiom in ChatGPT (opens in a new tab)"]')

def test_contact_enquiry_is_explicitly_user_sent_from_local_email_app():
    soup=page("/contact/")
    builder=soup.select_one("[data-enquiry-builder]")
    assert soup.select_one('main.contact-page a.button[href="#contact-enquiry"]')
    assert soup.select_one('#contact-enquiry .section-heading h2').get_text(strip=True)=="Tell us what you need."
    stylesheet=(DIST/"assets/site.css").read_text(encoding="utf-8")
    assert ".contact-page .page-hero" in stylesheet
    assert ".contact-page #contact-enquiry" in stylesheet
    assert builder
    for element in ("enquiry-topic","enquiry-subject","enquiry-email","enquiry-message","enquiry-compose"):
        assert builder.select_one("#"+element)
    assert builder.select_one('a[href^="mailto:support@mftintelligence.com"]')
    assert not builder.select_one("form")
    assert "your own email app" in soup.get_text(" ",strip=True).lower()
    assert "press send to contact musitu" in builder.get_text(" ",strip=True).lower()
    assert "what happens after you prepare an enquiry?" in soup.get_text(" ",strip=True).lower()
    assert "01 / the approach" not in soup.get_text(" ",strip=True).lower()
    assert builder.select_one('a[href="/legal/privacy/"]')
    assert builder.select_one('#enquiry-feedback[role="status"][aria-live="polite"]')
    for element in ("enquiry-topic","enquiry-subject","enquiry-email","enquiry-message"):
        field=builder.select_one("#"+element)
        assert field.has_attr("required") and field.get("aria-required")=="true"
    assert builder.select_one('#enquiry-email[type="email"]')
    assert builder.select_one('#enquiry-subject[minlength="3"]')
    assert builder.select_one('#enquiry-message[minlength="10"]')
    script=(DIST/"assets/site.js").read_text(encoding="utf-8")
    assert "event.preventDefault()" in script and "checkValidity()" in script
    assert "href.length>1900" in script
    assert "Review it and press Send to contact MUSITU" in script
    assert "mailto:support@mftintelligence.com?subject=" in script
    assert "navigator.clipboard.writeText" in script
    assert "const axiomQuery=" in script
    assert "Array.from(document.querySelectorAll('[data-axiom-operation]'))" in script

def test_marketing_seo_uses_customer_facing_descriptions_not_internal_release_controls():
    pages=json.loads((ROOT/"content/pages.json").read_text(encoding="utf-8"))
    for route in ("/developers/","/news/","/status/","/contact/"):
        text=pages[route]["description"].lower()
        assert len(text)>=65
        assert not any(bad in text for bad in (
            "not a public api","publication gate","must report only",
            "subject to an explicit acceptance test","staging","unverified"
        )),route
        generated=page(route)
        assert generated.select_one('meta[name=description]')["content"]==pages[route]["description"]
    for route in ("/legal/privacy/","/legal/terms/"):
        legal=page(route).get_text(" ",strip=True)
        assert "support@mftintelligence.com" in legal
    assert page("/products/axiom/").select_one('meta[name=description]')

def test_four_on_page_guides_link_to_specific_capabilities():
    resources=page("/resources/")
    guide=resources.select_one("#axiom-practical-guides")
    assert guide is not None
    assert len(guide.select(".axiom-guide"))==4
    expected=("finance-npv","finance-var_historical","statistics-regression","optimization-linear_program")
    for item in expected:
        assert guide.select_one('a[href="/products/axiom/#axiom-operation-'+item+'"]')
    directory=page("/products/axiom/")
    for item in expected:
        assert directory.select_one("#axiom-operation-"+item)


def test_four_canonical_tutorials_are_source_accurate_and_connect_to_operations():
    pages=json.loads((ROOT/"content/pages.json").read_text(encoding="utf-8"))
    evidence=load_axiom_demonstrations()
    operations={
        "/resources/axiom-investment-npv/":("npv","finance.npv"),
        "/resources/axiom-historical-var/":("portfolio-var","finance.var_historical"),
        "/resources/axiom-linear-regression/":("regression","statistics.regression"),
        "/resources/axiom-linear-optimisation/":("optimization","optimization.linear_program"),
    }
    cases={x["id"]:x for x in evidence["examples"]}
    for route,(example_id,operation) in operations.items():
        assert route in pages
        source=pages[route]
        article=page(route)
        assert article.select_one("article.axiom-longform")
        assert article.select_one('time[datetime="2026-11-21"]')
        assert article.select_one('link[rel="stylesheet"][href="/assets/site.css"]')
        assert article.select_one('a[href="/products/axiom/#axiom-operation-'+operation.replace(".", "-")+'"]')
        assert article.select_one('a[href="/resources/#axiom-practical-guides"]')
        assert len(article.select("main#main"))==1 and len(article.select("h1"))==1
        assert len(article.select("h2"))>=6
        assert not article.select("article.axiom-longform form, article.axiom-longform iframe")
        assert cases[example_id]["result"] in article.get_text(" ",strip=True)
        exact=article.select_one(".axiom-tutorial-inputs pre code")
        assert exact is not None
        assert json.loads(exact.get_text())==cases[example_id]["arguments"]
    resources=page("/resources/")
    assert len(resources.select('#axiom-practical-guides a[href^="/resources/axiom-"]'))==4
    demos=page("/products/axiom/")
    assert len(demos.select('.axiom-demo-card a[href^="/resources/axiom-"]'))==4

def test_four_tutorials_have_distinct_indexable_intents_in_seo_source():
    pages=json.loads((ROOT/"content/pages.json").read_text(encoding="utf-8"))
    seo=json.loads((ROOT/"content/seo-routes.json").read_text(encoding="utf-8"))
    tutorial_urls=[route for route in pages if route.startswith("/resources/axiom-")]
    assert len(tutorial_urls)==4
    assert len(seo["routes"])==37
    keywords={seo["routes"][route]["primary_query"] for route in tutorial_urls}
    assert len(keywords)==4
    for route in tutorial_urls:
        assert seo["routes"][route]["page_kind"]=="tutorial"
        assert pages[route]["title"] in page(route).title.get_text()
