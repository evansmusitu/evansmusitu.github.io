#!/usr/bin/env python3
"""Deterministic offline research editorial review packet. Never publishes to webroot.

No tokens, networking, runtime JS, CMS mutations, approvals or public Article schema.
All 12 editorial manuscripts remain unapproved even when previews are generated.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = BASE / "editorial" / "research-drafts"
DEFAULT_OUTPUT = BASE / "review-artifacts" / "research-preview"

REQUIRED_SECTIONS = (
    "## Research question",
    "## Method and reproducibility",
    "## Worked conceptual example",
    "## Failure modes and how to challenge the result",
    "## Reviewer checklist",
    "## Scope and limitations",
    "## Background reference",
    "## Related MUSITU page",
)
_LINK = re.compile(r"\[([^\]\n]+)\]\(([^\s)]+)\)")
_HEADING = re.compile(r"^(#{1,3})\s+(.+)$")
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")

def load_drafts(folder: Path = DEFAULT_SOURCE) -> list[dict]:
    """Read only fixed, content-hashed draft source with no public admission."""
    folder = Path(folder)
    paths = sorted(folder.glob("*.md"))
    if len(paths) != 12:
        raise ValueError("Expected exactly twelve research editorial drafts")
    records = []
    for source in paths:
        if not _SLUG.fullmatch(source.stem) or source.is_symlink():
            raise ValueError("Unacceptable draft source filename")
        raw = source.read_bytes()
        text = raw.decode("utf-8")
        first = text.splitlines()[0] if text.splitlines() else ""
        if not first.startswith("# ") or not first[2:].strip():
            raise ValueError("Missing article headline: " + source.name)
        if "not approved for public release" not in text:
            raise ValueError("Unreviewed source is mislabeled: " + source.name)
        if not all(heading in text for heading in REQUIRED_SECTIONS):
            raise ValueError("Missing review section: " + source.name)
        nwords = len(text.split())
        if nwords < 350:
            raise ValueError("Insufficient manuscript for technical review: " + source.name)
        if "https://" not in text:
            raise ValueError("Missing external reference: " + source.name)
        records.append({
            "slug": source.stem,
            "title": first[2:].strip(),
            "status": "draft",
            "publication_status": "unpublished",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "word_count": nwords,
            "text": text,
        })
    if len({x["slug"] for x in records}) != 12:
        raise ValueError("Duplicate article slug")
    return records

def _safe_link(raw: str) -> bool:
    parts = urlsplit(raw)
    if raw.startswith("/") and not raw.startswith("//"):
        return not (parts.scheme or parts.netloc or parts.query or parts.fragment) and bool(re.fullmatch(r"/(?:[a-z0-9-]+/)*", raw))
    return parts.scheme == "https" and bool(parts.netloc) and not (parts.username or parts.password or parts.port) and not any(c in raw for c in ('"', "'", "<", ">", "\\"))

def _inline(source: str) -> str:
    """Small safe Markdown subset for reviewer readability, not a public CMS."""
    source = source.replace("**", "").replace("  ", " ")
    pieces = []
    index = 0
    for match in _LINK.finditer(source):
        pieces.append(html.escape(source[index:match.start()], quote=True))
        label = html.escape(match.group(1), quote=True)
        url = match.group(2)
        if _safe_link(url):
            pieces.append('<a href="' + html.escape(url, quote=True) + '" rel="noopener noreferrer">' + label + '</a>')
        else:
            pieces.append(label + " (link withheld for review)")
        index = match.end()
    pieces.append(html.escape(source[index:], quote=True))
    return "".join(pieces)

def _body(text: str) -> str:
    rendered, paragraph = [], []
    def flush():
        if paragraph:
            rendered.append("<p>" + _inline(" ".join(paragraph)) + "</p>")
            paragraph.clear()
    for line in text.splitlines():
        line = line.strip()
        heading = _HEADING.fullmatch(line)
        if heading:
            flush()
            level = len(heading.group(1))
            rendered.append(f"<h{level}>" + _inline(heading.group(2)) + f"</h{level}>")
        elif not line:
            flush()
        else:
            paragraph.append(line)
    flush()
    return "\n".join(rendered)

def _shell(title: str, body: str) -> str:
    warning = ("<aside role=\"note\" aria-label=\"Publication status\">"
        "<strong>Editorial review preview — NOT PUBLISHED.</strong> "
        "Draft material. No public article route, search indexing or release authority.</aside>")
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
        '<meta name="robots" content="noindex,nofollow">\n'
        '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">\n'
        '<style>body{font:17px/1.65 system-ui,sans-serif;max-width:800px;margin:0 auto;padding:24px;color:#172033}'
        'h1,h2{line-height:1.25}aside{border:2px solid #ba7b14;padding:16px;border-radius:8px}'
        'a{color:#134b8b}main{margin-top:24px}p{max-width:76ch}</style>\n'
        "<title>" + html.escape(title, quote=True) + " | MUSITU editorial review</title>\n"
        "</head>\n<body>\n" + warning + '\n<main id="main">\n' + body + "\n</main>\n"
        "<footer><p>Review-only artifact; not a production website page.</p></footer>\n"
        "</body>\n</html>\n"
    )

def render_preview(article: dict) -> str:
    if article.get("status") != "draft" or article.get("publication_status") != "unpublished":
        raise ValueError("Only unpublished editorial drafts are eligible for review previews")
    return _shell(article["title"], _body(article["text"]))

def write_review_bundle(articles: list[dict], destination: Path) -> dict:
    destination = Path(destination).resolve()
    live = (BASE / "dist").resolve()
    if destination == live or live in destination.parents:
        raise ValueError("Never write editorial drafts into a public build artifact")
    if len(articles) != 12 or len({x["slug"] for x in articles}) != 12:
        raise ValueError("Exact twelve-item draft cohort required")
    destination.mkdir(parents=True, exist_ok=True)
    index = ['<h1>MUSITU research — editorial review inventory</h1>',
             '<p>All twelve articles below are draft, not published, not approved for indexing.</p>', "<ul>"]
    public_meta = []
    for article in sorted(articles, key=lambda x: x["slug"]):
        slug = article["slug"]
        if not _SLUG.fullmatch(slug):
            raise ValueError("Unsafe article slug")
        (destination / (slug + ".html")).write_text(render_preview(article), encoding="utf-8")
        index.append('<li><a href="' + slug + '.html">' + html.escape(article["title"]) + "</a></li>")
        public_meta.append({
            "slug": slug, "title": article["title"], "status": "draft",
            "source_sha256": article["sha256"], "word_count": article["word_count"],
        })
    index.append("</ul>")
    (destination / "index.html").write_text(_shell("Research review inventory", "\n".join(index)), encoding="utf-8")
    manifest = {
        "document": "MUSITU-PHASE03-RESEARCH-REVIEW-1",
        "publication_authorized": False,
        "indexing_authorized": False,
        "deployment_authorized": False,
        "article_count": len(public_meta),
        "articles": public_meta,
    }
    (destination / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create offline, noindex editorial preview packet only.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    records = load_drafts()
    bundle = write_review_bundle(records, args.output)
    print(json.dumps({
        "publication_authorized": bundle["publication_authorized"],
        "review_only_previews": bundle["article_count"],
        "destination": str(args.output),
    }, sort_keys=True))
