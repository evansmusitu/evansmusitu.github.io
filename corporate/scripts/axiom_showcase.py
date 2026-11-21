"""Static, source-locked Axiom demonstrations and onboarding.

Numbers are from actual Axiom calls with fictional inputs. No requests to the
plugin are made by the public website and no private source data is embedded.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "content/axiom-demonstrations.json"
SUPPORTED = (
    "finance.npv", "statistics.describe", "finance.black_scholes",
    "optimization.linear_program",
)
PLUGIN_URL = "https://chatgpt.com/plugins/plugin_asdk_app_6ae058ee6cec81919329ae43b76a4c86"


def load_axiom_demonstrations() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("executed_date") != "2026-11-21":
        raise ValueError("Unreviewed Axiom execution evidence")
    examples = data.get("examples")
    if not isinstance(examples, list) or len(examples) != len(SUPPORTED):
        raise ValueError("Expected four verified public example records")
    if tuple(item.get("operation") for item in examples) != SUPPORTED:
        raise ValueError("Unexpected operation order in Axiom demonstration source")
    ids = [item.get("id") for item in examples]
    if len(ids) != len(set(ids)) or any(not isinstance(i, str) or not i.isidentifier() for i in ids):
        raise ValueError("Axiom example IDs must be distinct and safe")
    for item in examples:
        for key in ("title", "discipline", "question", "inputs", "result", "detail", "verification"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise ValueError("Missing Axiom demonstration field: " + key)
        if len(item["question"]) > 320 or len(item["inputs"]) > 190:
            raise ValueError("Example prompt too long for the public guide")
    return data


def render_axiom_showcase() -> str:
    data = load_axiom_demonstrations()
    esc = lambda value: html.escape(str(value), quote=True)
    cards = []
    for item in data["examples"]:
        cards.append(
            '<article class="axiom-demo-card">'
            '<div class="axiom-demo-top"><span class="eyebrow">' + esc(item["discipline"]) + '</span>'
            '<code>' + esc(item["operation"]) + '</code></div>'
            '<h3>' + esc(item["title"]) + '</h3>'
            '<p class="axiom-demo-prompt" data-axiom-prompt>' + esc(item["question"]) + '</p>'
            '<div class="axiom-demo-output"><span>Calculated result</span><strong>'
            + esc(item["result"]) + '</strong><p>' + esc(item["detail"]) + '</p></div>'
            '<details class="axiom-demo-method"><summary>View sample inputs</summary><code>'
            + esc(item["inputs"]) + '</code></details>'
            '<div class="axiom-demo-actions"><button class="button button-outline" type="button" '
            'data-axiom-copy aria-label="Copy example question: ' + esc(item["title"]) + '">'
            'Copy example question</button>'
            '<span class="axiom-demo-feedback" role="status" aria-live="polite"></span></div>'
            '<p class="axiom-demo-evidence">' + esc(item["verification"]) + '</p>'
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
        '<div class="axiom-start-action"><a class="button button-primary" href="' + esc(PLUGIN_URL) + '" '
        'target="_blank" rel="noopener noreferrer" '
        'aria-label="Open Axiom in ChatGPT (opens in a new tab)">Open Axiom in ChatGPT ↗</a>'
        '<a class="text-link" href="#axiom-demonstrations">See calculated examples ↓</a></div>'
        '</div></section>'
        '<section id="axiom-demonstrations" class="section section-tinted axiom-demos-section">'
        '<div class="shell"><div class="section-heading">'
        '<span class="eyebrow">AXIOM IN ACTION</span>'
        '<h2>Explore four completed calculations.</h2>'
        '<p>These examples were calculated through MUSITU Axiom with fictional inputs on '
        + esc(data["executed_date"]) + '. Results are rounded for display; you can copy '
        'a question and explore it in Axiom.</p></div>'
        '<div class="axiom-demo-grid">' + "".join(cards) + '</div>'
        '</div></section>'
    )
