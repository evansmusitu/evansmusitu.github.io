"""Owner-approved, source-hash-locked research and French pilot publication renderer.

No external requests, private data, geolocation targeting, CMS writes or runtime JS.
A default build never includes these 15 additional pages; operator must explicitly
set MUSITU_PUBLISH_PHASE03=1, and production still needs the independent release gate.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
import re
from datetime import date
from pathlib import Path

from research_review import load_drafts, _body
from seo import ORIGIN, approved_article_schema, approved_hreflang_links

BASE = Path(__file__).resolve().parents[1]
APPROVAL_FILE = BASE / "content" / "phase03-publication-approvals.json"
LOCALES = BASE / "content" / "localization-pilot.json"
APPROVED_ON = "2026-11-08"
EN_FR = {
    "/": "/fr/",
    "/products/axiom/": "/fr/products/axiom/",
    "/research/": "/fr/research/",
}
FR_EN = {v: k for k, v in EN_FR.items()}
FR_BODY = {
    "/fr/": [
        ("Une organisation technologique à vocation internationale",
         "MUSITU est une organisation technologique. Elle développe des logiciels intelligents, des outils de calcul, des technologies éducatives, des expériences créatives et des systèmes numériques. Les différentes familles de produits sont présentées selon leur état réel de développement, sans assimiler une démonstration à une fonction disponible dans tous les produits."),
        ("Des méthodes que l’on peut examiner",
         "Nos pages publiques distinguent les faits documentés, les démonstrations, les travaux expérimentaux et les objectifs de recherche. Une analyse convaincante exige des données traçables, des hypothèses explicites, des résultats reproductibles et une description des limites. Les résultats présentés sur ce site ne constituent pas une garantie de performance."),
        ("Explorer les travaux publiés",
         "Découvrez les informations sur MUSITU Axiom et les explications consacrées aux méthodes de recherche. La version anglaise du site reste la référence pour les informations juridiques et les détails concernant les autres produits."),
    ],
    "/fr/products/axiom/": [
        ("À quoi sert une analyse quantitative structurée ?",
         "MUSITU Axiom est présenté dans le cadre du calcul mathématique et de l’analyse quantitative. Une question complexe doit être formulée précisément, avec des unités, des hypothèses et des méthodes de vérification. Le résultat d’un calcul ne remplace jamais l’examen de la qualité des données ni l’interprétation humaine."),
        ("Portée des informations publiées",
         "Les descriptions de méthodes ne signifient pas que chaque fonction décrite est disponible dans le produit ou qu’elle a fait l’objet d’une validation indépendante. Les exemples pédagogiques ne constituent ni des résultats financiers réels ni une recommandation d’investissement."),
        ("Poursuivre la lecture",
         "La rubrique Recherche présente des méthodes de validation, de reproductibilité, de contrôle des modèles et d’évaluation des risques. Pour connaître les capacités publiquement documentées et les modalités d’utilisation d’Axiom, consultez également la page anglaise du produit."),
    ],
    "/fr/research/": [
        ("Une recherche guidée par la méthode",
         "Les travaux de MUSITU abordent les méthodes quantitatives, les technologies éducatives, la création numérique et les systèmes d’information. Les publications méthodologiques décrivent un problème, une approche reproductible, un exemple conceptuel et les limites de l’analyse."),
        ("Vérification et interprétation",
         "Une étude rigoureuse précise la provenance des données, les périodes considérées, les hypothèses, les choix de modélisation et les risques de fuite d’information. Il est important de différencier une observation historique, une simulation et une prévision. Les résultats passés ne garantissent pas les résultats futurs."),
        ("Lire les explications",
         "La collection complète des douze articles techniques est disponible en anglais. Chaque article renvoie à des ressources de contexte et décrit la portée de ses affirmations. Ces textes sont pédagogiques : ils ne constituent pas des conseils financiers, juridiques ou professionnels."),
    ],
}


def _safe_jsonld(graph: list[dict]) -> str:
    payload = json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return '<script type="application/ld+json">' + payload + '</script>\n'


def actual_publication_date() -> str:
    """Require the operator's actual launch date, never the manuscript approval date."""
    raw = os.environ.get("MUSITU_PHASE03_PUBLICATION_DATE", "")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        raise ValueError("Phase 03 requires explicit publication date YYYY-MM-DD")
    try:
        published = date.fromisoformat(raw)
    except ValueError:
        raise ValueError("Phase 03 requires explicit publication date YYYY-MM-DD") from None
    if published < date.fromisoformat(APPROVED_ON):
        raise ValueError("Phase 03 publication date predates manuscript approval")
    return raw


def approved_sources() -> list[dict]:
    approval = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
    if approval.get("approval_date") != APPROVED_ON or len(approval.get("articles", [])) != 12:
        raise ValueError("Publication approval record not complete")
    expected = {item["slug"]: item for item in approval["articles"]}
    if len(expected) != 12:
        raise ValueError("Duplicate approved editorial slug")
    drafts = load_drafts()
    if set(expected) != {a["slug"] for a in drafts}:
        raise ValueError("Approved manuscripts differ from candidate corpus")
    for article in drafts:
        src = (BASE / "editorial" / "research-drafts" / (article["slug"] + ".md")).read_bytes()
        git_sha = hashlib.sha1(b"blob " + str(len(src)).encode("ascii") + b"\0" + src).hexdigest()
        match = expected[article["slug"]]
        if match.get("source_git_blob_sha") != git_sha or match.get("title") != article["title"]:
            raise ValueError("Research source changed after owner approval: " + article["slug"])
        if not article["text"].count("## Scope and limitations") == 1:
            raise ValueError("Missing or duplicate limitation statement")
        if "not approved for public release" not in article["text"]:
            raise ValueError("Unsafe editorial source changed")
    return drafts


def article_routes(articles: list[dict]) -> list[str]:
    return ["/research/articles/" + a["slug"] + "/" for a in articles]


def _article_content(article: dict) -> str:
    start = article["text"].index("## Research question")
    text = "# " + article["title"] + "\n\n" + article["text"][start:]
    return _body(text)


def article_info(article: dict, header: str, published_on: str | None = None) -> dict:
    path = "/research/articles/" + article["slug"] + "/"
    heading = html.escape(article["title"])
    first = article["text"].split("## Research question", 1)[1].split("## Method", 1)[0].strip()
    description = " ".join(first.split())[:155].rstrip(" ,.;") + "."
    day = date.fromisoformat(published_on) if published_on else None
    date_label = (str(day.day) + " " + day.strftime("%B %Y")) if day else "Publication date pending"
    main = ('<main id="main" tabindex="-1">'
        '<nav aria-label="Breadcrumb" class="breadcrumbs shell"><ol>'
        '<li><a href="/">Home</a></li><li><a href="/research/">Research</a></li>'
        '<li aria-current="page">Article</li></ol></nav>'
        '<section class="page-hero shell"><span class="eyebrow">RESEARCH / METHODS</span>'
        '<p class="lead">Technical explainer · MUSITU Research · ' + date_label + '</p></section>'
        '<article class="section shell phase03-article">'
        + _article_content(article)
        + '</article>'
        '<section class="section section-tinted"><div class="shell reading-section">'
        '<h2>Context and limits</h2>'
        '<p>This educational article describes methods, assumptions and limitations. '
        'It is not personal investment advice or independent product certification.</p>'
        '<p><a class="text-link" href="/research/">Explore more MUSITU research</a></p>'
        '</div></section></main>')
    return {"header": header, "main": main, "title": article["title"] + " — MUSITU Research", "description": description}


def article_head(article: dict) -> str:
    path = "/research/articles/" + article["slug"] + "/"
    info = article_info(article, "", actual_publication_date())
    record = {"path": path, "headline": article["title"], "description": info["description"],
              "date_published": actual_publication_date(), "review_status": "approved", "publication_status": "published"}
    data = approved_article_schema(record)
    data.pop("@context")
    crumbs = {"@type":"BreadcrumbList", "itemListElement":[
        {"@type":"ListItem","position":1,"name":"MUSITU","item":ORIGIN+"/"},
        {"@type":"ListItem","position":2,"name":"Research","item":ORIGIN+"/research/"},
        {"@type":"ListItem","position":3,"name":article["title"],"item":ORIGIN+path},
    ]}
    return '<meta property="og:site_name" content="MUSITU">\n' + _safe_jsonld([crumbs, data])


def index_links(articles: list[dict]) -> str:
    out = ['<section class="section phase03-publications" aria-labelledby="research-articles-title">',
           '<div class="shell"><div class="section-heading">',
           '<span class="eyebrow">PUBLISHED RESEARCH / TECHNICAL EXPLAINERS</span>',
           '<h2 id="research-articles-title">Explore twelve evidence-led research articles</h2>',
           '<p>Conceptual examples and methodology, with sources, limitations and no investment recommendations.</p>',
           '</div><div class="proof-grid">']
    for a in articles:
        url="/research/articles/"+a["slug"]+"/"
        out.append('<article class="proof-card"><span class="card-eyebrow">Methodology · 2026</span>'
                   '<h3><a href="'+url+'">'+html.escape(a["title"])+'</a></h3>'
                   '<p>Technical methodology, worked example, source context and limitations.</p></article>')
    out.extend(['</div></div></section>'])
    return "\n".join(out)


def localize_english_core(route: str, info: dict, articles: list[dict]) -> dict:
    body=info["main"]
    if route=="/research/":
        body=body.replace("</main>",index_links(articles)+"</main>",1)
    if route in EN_FR:
        fr=EN_FR[route]
        widget='<nav class="phase03-language" aria-label="Language"><a href="'+fr+'" lang="fr" hreflang="fr">Lire cette page en français</a></nav>'
        body=body.replace("</main>",widget+"</main>",1)
    return {**info, "main": body}


def locale_equivalents(route: str) -> dict[str, str] | None:
    source = route if route in EN_FR else FR_EN.get(route)
    if source is None:
        return None
    return {"en": source, "fr": EN_FR[source]}


def hreflang(route: str) -> str:
    group=locale_equivalents(route)
    if group is None:
        return ""
    return approved_hreflang_links(route,group,{"en":set(EN_FR),"fr":set(FR_EN)})


def french_info(route: str, english: dict, pilot: dict) -> dict:
    if route not in FR_BODY:
        raise ValueError("Unknown French translation")
    sections = FR_BODY[route]
    breadcrumb = '<nav class="breadcrumbs shell" aria-label="Fil d’Ariane"><ol><li><a href="/fr/">Accueil</a></li>'
    if route!="/fr/":
        breadcrumb += '<li aria-current="page">'+html.escape(pilot["h1"])+'</li>'
    breadcrumb+='</ol></nav>'
    body = ('<main id="main" tabindex="-1">'+breadcrumb+
            '<section class="page-hero shell"><span class="eyebrow">MUSITU · FRANÇAIS</span>'
            '<h1>'+html.escape(pilot["h1"])+'</h1>'
            '<p class="lead">'+html.escape(pilot["description"])+'</p></section>')
    for i,(heading,paragraph) in enumerate(sections):
        body+=('<section class="section'+(' section-tinted' if i%2 else '')+'">'
               '<div class="shell reading-section"><h2>'+html.escape(heading)+'</h2>'
               '<p>'+html.escape(paragraph)+'</p></div></section>')
    body+=('<nav class="phase03-language" aria-label="Changer de langue"><a href="'+FR_EN[route]+'" lang="en" hreflang="en">Read this page in English</a> · '
           '<a href="/fr/research/">Recherche</a> · <a href="/fr/products/axiom/">Axiom</a></nav></main>')
    header = ('<header class="site-header"><div class="shell phase03-fr-header">'
              '<a class="brand" aria-label="MUSITU accueil" href="/fr/"><img class="brand-mark" alt="" src="/assets/favicon.svg"><span>MUSITU</span></a>'
              '<nav aria-label="Navigation principale" class="phase03-fr-nav">'
              '<a href="/fr/">Accueil</a><a href="/fr/products/axiom/">Axiom</a>'
              '<a href="/fr/research/">Recherche</a><a href="'+FR_EN[route]+'" lang="en" hreflang="en">English</a>'
              '</nav></div></header>')
    return {"title":pilot["title"],"description":pilot["description"],"header":header,"main":body}


def french_head(route: str, info: dict) -> str:
    crumbs = [{"@type":"ListItem","position":1,"name":"MUSITU","item":ORIGIN+"/fr/"}]
    if route!="/fr/":
        crumbs.append({"@type":"ListItem","position":2,"name":info["title"],"item":ORIGIN+route})
    graph = [
        {"@type":"WebPage","url":ORIGIN+route,"name":info["title"],"description":info["description"],"inLanguage":"fr"},
        {"@type":"BreadcrumbList","itemListElement":crumbs}
    ]
    return hreflang(route) + '<meta property="og:locale" content="fr_FR">\n' + _safe_jsonld(graph)


def french_records() -> dict[str, dict]:
    approval = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
    if approval.get("french_pilot",{}).get("approved_by_owner") is not True:
        raise ValueError("French release requires owner approval")
    data = json.loads(LOCALES.read_text(encoding="utf-8"))
    fr = next(p for p in data["pilots"] if p.get("language") == "fr")
    samples={s["localized_path"]:s for s in fr["sample"]}
    if set(samples)!=set(FR_BODY) or set(samples)!=set(approval["french_pilot"]["paths"]):
        raise ValueError("French sample and approved three-path pilot differ")
    return samples
