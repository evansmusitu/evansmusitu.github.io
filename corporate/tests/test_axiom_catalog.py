"""Evidence-locked tests for the full published Axiom capability directory."""
from pathlib import Path
import json
import sys

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from axiom_catalog import load_capability_catalog, load_operation_schemas, render_axiom_catalog

DIST = ROOT / "dist"
EXPECTED_OPERATIONS = {
    'algebra.expand',
    'algebra.factor',
    'algebra.polynomial_roots',
    'algebra.simplify',
    'algebra.solve',
    'arithmetic.evaluate',
    'calculus.diff',
    'calculus.integrate',
    'calculus.limit',
    'calculus.product',
    'calculus.series',
    'calculus.sum',
    'combinatorics.binomial',
    'combinatorics.factorial',
    'finance.beta',
    'finance.black_scholes',
    'finance.bond_price',
    'finance.bond_yield',
    'finance.compound',
    'finance.cvar_historical',
    'finance.drawdown',
    'finance.duration',
    'finance.greeks',
    'finance.implied_vol',
    'finance.monte_carlo_gbm',
    'finance.npv',
    'finance.portfolio_metrics',
    'finance.returns',
    'finance.var_historical',
    'finance.var_parametric',
    'geometry.area_circle',
    'geometry.distance',
    'geometry.volume_sphere',
    'knowledge.constant',
    'knowledge.element',
    'linear.det',
    'linear.eigen',
    'linear.inv',
    'linear.solve',
    'numbertheory.factorint',
    'numbertheory.gcd',
    'numbertheory.isprime',
    'numbertheory.lcm',
    'numeric.integrate',
    'numeric.interpolate',
    'numeric.least_squares',
    'numeric.ode',
    'numeric.optimize_scalar',
    'numeric.root',
    'optimization.linear_program',
    'optimization.quadratic',
    'probability.binomial_pmf',
    'probability.chi2_cdf',
    'probability.exponential_cdf',
    'probability.normal_cdf',
    'probability.normal_ppf',
    'probability.poisson_pmf',
    'statistics.correlation',
    'statistics.covariance',
    'statistics.describe',
    'statistics.normal_fit',
    'statistics.quantile',
    'statistics.regression',
    'statistics.ttest_ind',
    'statistics.zscore',
    'timeseries.ewma',
    'timeseries.moving_average',
    'timeseries.rolling_volatility',
    'transforms.fft',
    'transforms.ifft',
    'units.convert',
    'verified.interval_eval',
    'verify.crosscheck',
    'verify.evaluate',
}


def test_verified_operation_names_exactly_match_74_tool_registry():
    data = load_capability_catalog()
    groups = data["categories"]
    actual = [operation["id"] for group in groups for operation in group["operations"]]
    assert data["operation_count"] == len(actual) == len(EXPECTED_OPERATIONS) == 74
    assert set(actual) == EXPECTED_OPERATIONS
    assert len(actual) == len(set(actual))
    assert len(groups) == 18 and len({g["id"] for g in groups}) == 18
    assert data["business_tool_count"] == 30
    assert data["snapshot_date"] == "2026-11-20"


def test_directory_contains_every_plain_language_operation_and_valid_jump_target():
    data = load_capability_catalog()
    soup = BeautifulSoup(render_axiom_catalog(), "html.parser")
    section = soup.select_one("section#axiom-full-capabilities")
    assert section is not None
    assert len(section.select(".axiom-domain")) == 18
    assert len(section.select(".axiom-operation-list li")) == 74
    assert len(section.select(".axiom-operation-tech")) == 74
    assert len(section.select(".axiom-raw-schema")) == 74
    assert sum(len(x.select(".axiom-parameter-list > div")) for x in section.select(".axiom-operation-tech")) == 193
    assert {code.get_text(strip=True) for code in section.select(".axiom-operation-list code")} == EXPECTED_OPERATIONS
    actual_by_id = {entry.select_one("code").get_text(strip=True): entry.select_one(".axiom-operation-label").get_text(" ", strip=True)
                    for entry in section.select(".axiom-operation-list li")}
    for group in data["categories"]:
        for op in group["operations"]:
            assert actual_by_id[op["id"]] == op["label"]
    links = section.select('nav[aria-label="Jump to Axiom disciplines"] a[href^="#axiom-domain-"]')
    assert len(links) == 18
    for link in links:
        target = section.select_one(link["href"])
        assert target is not None and target.select_one("h3") is not None
    assert "Explore Axiom in ChatGPT" in section.get_text(" ", strip=True)
    assert "Availability and maturity" not in section.get_text(" ", strip=True)
    assert not section.select("script,iframe,form")
    assert len(section.select("button"))==1
    assert section.select_one("#axiom-capability-reset[type=button]")


def test_only_flagship_page_includes_complete_directory():
    axiom = BeautifulSoup((DIST / "products/axiom/index.html").read_text(encoding="utf-8"), "html.parser")
    assert len(axiom.select("section#axiom-full-capabilities")) == 1
    assert {x.get_text(strip=True) for x in axiom.select(".axiom-operation-list code")} == EXPECTED_OPERATIONS
    assert not axiom.find(string=lambda x: x and "AXIOM_CAPABILITY_DIRECTORY" in x)
    assert axiom.select_one('a[href^="https://chatgpt.com/plugins/"]')
    assert axiom.select_one("section#axiom-full-capabilities .axiom-explore-cta")
    assert axiom.select_one("section#axiom-full-capabilities .axiom-explore-cta a[href^='https://chatgpt.com/plugins/']")
    assert "Availability and maturity" not in axiom.get_text(" ", strip=True)
    assert "independently certified superiority" not in axiom.get_text(" ", strip=True)
    for route in ("company", "trust", "products/education", "products/foundry"):
        page = (DIST / route / "index.html").read_text(encoding="utf-8")
        assert "axiom-full-capabilities" not in page
        assert "AXIOM_CAPABILITY_DIRECTORY" not in page


def test_74_operation_directory_is_discoverable_from_home_and_products():
    home = BeautifulSoup((DIST / "index.html").read_text(encoding="utf-8"), "html.parser")
    products = BeautifulSoup((DIST / "products/index.html").read_text(encoding="utf-8"), "html.parser")
    anchor = "/products/axiom/#axiom-full-capabilities"
    assert home.select_one(f'a[href="{anchor}"]')
    assert products.select_one(f'a[href="{anchor}"]')
    assert "74 operations" in products.get_text(" ", strip=True)
    assert "18 technical disciplines" in products.get_text(" ", strip=True)


def test_no_overstated_access_or_backend_requests():
    data = load_capability_catalog()
    directory = render_axiom_catalog().lower()
    assert "capability library" in directory
    assert "bring your next question to axiom" in directory
    assert "availability and maturity" not in directory
    assert "unrestricted anonymous use" not in directory
    assert "independently certified superiority" not in directory
    assert "fetch(" not in directory
    assert "sk-proj-" not in directory
    assert data["snapshot_date"] == "2026-11-20"

def test_all_74_operation_input_schemas_match_exact_catalog():
    catalog = load_capability_catalog()
    schema = load_operation_schemas(catalog)
    expected = [op["id"] for group in catalog["categories"] for op in group["operations"]]
    assert len(schema) == len(expected) == 74
    assert list(schema) == expected
    assert sum(len(s["properties"]) for s in schema.values()) == 193
    for operation, fields in schema.items():
        assert fields["type"] == "object", operation
        assert fields["additionalProperties"] is False, operation
        assert all(x in fields["properties"] for x in fields["required"]), operation
        assert all(isinstance(p, dict) for p in fields["properties"].values()), operation
    browser = BeautifulSoup(render_axiom_catalog(), "html.parser")
    for operation in expected:
        row = browser.select_one("#axiom-operation-" + operation.replace(".", "-"))
        assert row is not None
        assert row.select_one(".axiom-operation-tech > summary")
        assert row.select_one(".axiom-raw-schema > pre > code")
        assert row.select_one(".axiom-parameter-list")
