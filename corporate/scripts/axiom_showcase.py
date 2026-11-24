"""Static, source-locked Axiom demonstrations and onboarding.

Numbers are from actual Axiom calls with fictional inputs. No requests to the
plugin are made by the public website and no private source data is embedded.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "content/axiom-demonstrations.json"
SUPPORTED = (
    "finance.npv", "statistics.describe", "finance.black_scholes",
    "optimization.linear_program", "finance.var_historical",
    "statistics.regression", "statistics.correlation", "finance.compound",
    "statistics.quantile", "timeseries.moving_average",
    "timeseries.rolling_volatility", "finance.bond_price",
    "finance.bond_yield", "finance.var_parametric", "finance.portfolio_metrics",
    "probability.normal_cdf", "calculus.diff", "units.convert", "linear.det",
    "geometry.area_circle",
)
PLUGIN_URL = "https://chatgpt.com/plugins/plugin_asdk_app_6ae058ee6cec81919329ae43b76a4c86"


def load_axiom_demonstrations() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("executed_date") != "2026-11-21":
        raise ValueError("Unreviewed Axiom execution evidence")
    examples = data.get("examples")
    if not isinstance(examples, list) or len(examples) != len(SUPPORTED):
        raise ValueError("Expected twenty source-locked Axiom execution records")
    if tuple(item.get("operation") for item in examples) != SUPPORTED:
        raise ValueError("Unexpected operation order in Axiom demonstration source")
    ids = [item.get("id") for item in examples]
    if len(ids) != len(set(ids)) or any(not isinstance(i, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', i) for i in ids):
        raise ValueError("Axiom example IDs must be distinct and safe")
    for item in examples:
        for key in ("title", "discipline", "question", "inputs", "method", "result", "detail", "verification", "evidence_status"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError("Missing Axiom demonstration field: " + key)
        if not isinstance(item.get("arguments"), dict) or not item["arguments"]:
            raise ValueError("Missing exact Axiom execution inputs")
        if len(item["question"]) > 320 or len(item["inputs"]) > 350:
            raise ValueError("Example prompt too long for the public guide")
    return data


def render_axiom_showcase() -> str:
    data = load_axiom_demonstrations()
    esc = lambda value: html.escape(str(value), quote=True)
    starter_prompts = (
        "Use MUSITU Axiom to calculate NPV for cashflows [-10000,4000,4300,4700] at rate 0.10. Show the method, result and assumptions.",
        "Use MUSITU Axiom to estimate historical 95% VaR for synthetic returns [0.012,-0.018,0.009,-0.025,0.015,-0.041,0.022,-0.012,0.017,-0.032,0.006,-0.008,0.019,-0.022,0.010,-0.015,0.013,-0.028,0.004,-0.011]. Explain the sampling risk.",
        "Use MUSITU Axiom to fit regression for x=[1,2,3,4,5,6,7,8], y=[3.1,4.8,7.2,8.9,11.1,12.8,15,17.2]. Explain the slope.",
        "Use MUSITU Axiom to maximize 3x+5y with x<=4, 2y<=12, 3x+2y<=18 and nonnegative x,y. Show the optimal allocation.",
        "Use MUSITU Axiom to find the yield on a 5-year bond with price=1020, face=1000, annual coupon=5%, two coupon payments per year. State the model assumptions.",
    )
    starters = "".join(
        '<li class="axiom-starter-card"><p data-axiom-prompt>' + esc(prompt)
        + '</p><button class="button button-outline" type="button" data-axiom-copy>'
        + 'Copy prompt</button><span class="axiom-demo-feedback" role="status" aria-live="polite"></span></li>'
        for prompt in starter_prompts
    )
    cards = []
    for item in data["examples"]:
        cards.append(
            '<article class="axiom-demo-card">'
            '<div class="axiom-demo-top"><span class="eyebrow">' + esc(item["discipline"]) + '</span></div>'
            '<h3>' + esc(item["title"]) + '</h3>'
            '<p class="axiom-demo-prompt" data-axiom-prompt>' + esc(item["question"]) + '</p>'
            '<div class="axiom-demo-output"><span>Calculated result</span><strong>'
            + esc(item["result"]) + '</strong><p>' + esc(item["detail"]) + '</p></div>'
            '<details class="axiom-demo-method"><summary>View method, exact input and technical operation</summary>'
            '<p><strong>Method:</strong> ' + esc(item["method"]) + '</p>'
            '<pre><code>' + esc(json.dumps(item["arguments"], ensure_ascii=False, indent=2)) + '</code></pre>'
            '<p><strong>Operation:</strong> <code>' + esc(item["operation"]) + '</code></p></details>'
            '<div class="axiom-demo-actions"><button class="button button-outline" type="button" '
            'data-axiom-copy data-axiom-copy-payload="' + esc(item["question"] + " Exact inputs: " + json.dumps(item["arguments"], separators=(",", ":"), ensure_ascii=False)) + '" aria-label="Copy example question: ' + esc(item["title"]) + '">'
            'Copy example question</button>'
            '<span class="axiom-demo-feedback" role="status" aria-live="polite"></span></div>'
            '<p class="axiom-demo-evidence">' + esc(item["evidence_status"]) + ' · ' + esc(item["verification"]) + '</p>'
            '</article>'
        )
    return (
        '<section id="axiom-start" class="section axiom-onboarding-section">'
        '<div class="shell">'
        '<div class="section-heading"><span class="eyebrow">GET STARTED WITH MUSITU AXIOM</span>'
        '<h2>From a question to a mathematical answer.</h2>'
        '<p>Open Axiom in ChatGPT, choose a problem, and work through its inputs and calculated result.</p>'
        '</div>'
        '<ol class="axiom-start-steps">'
        '<li><span class="axiom-start-number">01</span><h3>Open Axiom</h3>'
        '<p>Start from the direct MUSITU Axiom listing in ChatGPT.</p></li>'
        '<li><span class="axiom-start-number">02</span><h3>Ask a specific question</h3>'
        '<p>Use an example below or describe your own mathematical task and known inputs.</p></li>'
        '<li><span class="axiom-start-number">03</span><h3>Review the calculation</h3>'
        '<p>Examine the result, method and assumptions before applying it to your work.</p></li>'
        '</ol>'
        '<h3 class="axiom-starter-heading">Five ready-to-use prompts</h3>'
        '<ol class="axiom-starter-grid">' + starters + '</ol>'
        '<div class="axiom-start-action"><a class="button button-primary" href="' + esc(PLUGIN_URL) + '" '
        'target="_blank" rel="noopener noreferrer" '
        'aria-label="Open Axiom in ChatGPT (opens in a new tab)">Open Axiom in ChatGPT ↗</a>'
        '<a class="text-link" href="#axiom-demonstrations">See calculated examples ↓</a></div>'
        '</div></section>'
        '<section id="axiom-demonstrations" class="section section-tinted axiom-demos-section">'
        '<div class="shell"><div class="section-heading">'
        '<span class="eyebrow">AXIOM IN ACTION</span>'
        '<h2>Explore 20 completed calculations.</h2>'
        '<p>These examples were calculated through MUSITU Axiom with fictional inputs on '
        + esc(data["executed_date"]) + '. Results are rounded for display; you can copy '
        'a question and explore it in Axiom.</p></div>'
        '<div class="axiom-demo-grid">' + "".join(cards) + '</div>'
        '</div></section>'
    )
