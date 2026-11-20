"""Render the public, verified MUSITU Axiom operation directory.

This is static HTML only. No credentials, network requests, trading or paid
services are invoked from the website, and publication is not an entitlement.
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "content/axiom-capabilities.json"
TECHNICAL_ID = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")
CATEGORY_ID = re.compile(r"^[a-z][a-z0-9_]*$")


def load_capability_catalog() -> dict:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("snapshot_date") != "2026-11-20":
        raise ValueError("Unreviewed Axiom capability catalog version/date")
    categories = data.get("categories")
    if not isinstance(categories, list) or len(categories) != 18:
        raise ValueError("Axiom catalog must have the verified 18 categories")
    unique, domain_names = set(), set()
    for group in categories:
        domain = group.get("id")
        if not isinstance(domain, str) or not CATEGORY_ID.fullmatch(domain) or domain in domain_names:
            raise ValueError("Invalid or duplicate Axiom category")
        domain_names.add(domain)
        if not all(isinstance(group.get(k), str) and group[k].strip() for k in ("title", "description")):
            raise ValueError("Missing Axiom category editorial description")
        items = group.get("operations")
        if not isinstance(items, list) or not items:
            raise ValueError("Missing Axiom category operations")
        for operation in items:
            code, label = operation.get("id"), operation.get("label")
            if not isinstance(code, str) or not TECHNICAL_ID.fullmatch(code):
                raise ValueError("Unrecognized technical Axiom operation")
            if not code.startswith(domain + ".") or code in unique:
                raise ValueError("Axiom operation category mismatch or duplicate")
            if not isinstance(label, str) or not label.strip():
                raise ValueError("Axiom operation missing human-readable label")
            unique.add(code)
    if len(unique) != 74 or data.get("operation_count") != 74 or data.get("business_tool_count") != 30:
        raise ValueError("Unreviewed Axiom operation or business-entrypoint count")
    return data


def render_axiom_catalog() -> str:
    data = load_capability_catalog()
    esc = lambda value: html.escape(str(value), quote=True)
    categories = data["categories"]
    navigation = "".join(
        '<a href="#axiom-domain-' + esc(group["id"]) + '">' + esc(group["title"])
        + '<span aria-hidden="true">' + str(len(group["operations"])) + '</span></a>'
        for group in categories
    )
    panels = []
    for group in categories:
        entries = "".join(
            '<li><span class="axiom-operation-label">' + esc(item["label"])
            + '</span><code>' + esc(item["id"]) + '</code></li>'
            for item in group["operations"]
        )
        panels.append(
            '<article class="axiom-domain" id="axiom-domain-' + esc(group["id"]) + '">'
            '<div class="axiom-domain-header"><div><h3>' + esc(group["title"]) + '</h3>'
            '<p>' + esc(group["description"]) + '</p></div>'
            '<span class="axiom-domain-count">' + str(len(group["operations"])) + ' operations</span></div>'
            '<ul class="axiom-operation-list">' + entries + '</ul></article>'
        )
    return (
        '<section class="section axiom-directory-section" id="axiom-full-capabilities">'
        '<div class="shell"><div class="section-heading">'
        '<span class="eyebrow">THE AXIOM CAPABILITY LIBRARY</span>'
        '<h2>Explore all 74 Axiom operations.</h2>'
        '<p>Discover tools for financial analysis, statistics, mathematics, optimisation and more. '
        'Browse by discipline and explore the exact capabilities behind each tool.</p>'
        '</div><div class="axiom-metrics" aria-label="Axiom registry snapshot">'
        '<div><strong>74</strong><span>Registered operations</span></div>'
        '<div><strong>18</strong><span>Capability disciplines</span></div>'
        '<div><strong>30</strong><span>Focused analytical tools</span></div>'
        '</div><p class="axiom-snapshot">Capability library updated ' + esc(data["snapshot_date"]) + '.</p>'
        '<nav class="axiom-directory-nav" aria-label="Jump to Axiom disciplines">'
        + navigation + '</nav>'
        '<div class="axiom-directory-grid">' + "".join(panels) + '</div>'
        '<div class="axiom-explore-cta"><div><h3>Bring your next question to Axiom.</h3>'
        '<p>Explore the mathematical tools behind sharper analysis, stronger models and more informed decisions.</p>'
        '</div><a class="button button-primary" '
        'href="https://chatgpt.com/plugins/plugin_asdk_app_6ae058ee6cec81919329ae43b76a4c86" '
        'target="_blank" rel="noopener noreferrer" '
        'aria-label="Open MUSITU Axiom in ChatGPT (opens in a new tab)">Explore Axiom in ChatGPT ↗</a>'
        '</div>'
        '</div></section>'
    )
