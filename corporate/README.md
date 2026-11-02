# MUSITU Corporate Website — isolated review candidate

**2 November 2026 · Not approved for public release**

The implementation lives in this branch under `corporate/`, separate from the existing published MUSITU Intelligence homepage and assets.

## What is implemented

- 22 deterministic static routes covering the agreed company pages, six canonical product families, research, evidence, trust, support, legal review, developer and status gates.
- Source-linked maturity and limitation statements on each product page; no false claim that draft customer portals, marketplace payments or trading are public services.
- Responsive MUSITU navy/violet/mint design, mobile navigation, theme switching, searchable/filterable product directory and accessible native evidence dialogs.
- Static, dependency-free page generation; SEO title/description foundations; staging `noindex,nofollow` and `robots.txt` denial.
- Review-only CI workflow: build + automated checks + artifact upload; **no deployment step**.

## Local build and review

Requires Python 3.12+ for building, Node.js for JS syntax checks, and optional `pytest` and `beautifulsoup4` for tests.

```bash
python3 corporate/scripts/build.py
python3 -m pip install pytest==8.4.2 beautifulsoup4==4.14.2
python3 -m pytest -q corporate/tests/test_site.py
node --check corporate/assets/site.js
python3 -m http.server 8000 --directory corporate/dist
```

Open `http://localhost:8000/`. Files use root-relative URLs so they must be served from the domain root in staging.

## Preservation and release rules

- **Do not replace** existing repository-root `index.html`, `assets/musitu-*`, or published GitHub Pages workflows as part of review.
- Existing Intelligence's encrypted local workspaces remain on their original origin. A move requires verified user export/import and regression testing.
- Do not infer a verified legal entity, business contact, pricing, domain ownership, customer account system or live commerce.
- Privacy and terms are clearly marked as working drafts; developer/status surfaces are gated.
- Public launch requires owner acceptance of content and legal details, verified Cloudflare/DNS authority, real-device and accessibility review, security checks, tested contact delivery, deployment change review and **separate explicit release approval**.
- Only remove `noindex` after production release authorization.

## Primary evidence

- Canonical family naming: https://github.com/evansmusitu/mft-axiom-build/blob/main/branding/MUSITU_BRAND_CANONICAL.json
- AXIOM integration and correction-draft distinction: https://github.com/evansmusitu/mft-axiom-build/pull/47
- Customer identity B27 rollback failure and no-release: https://github.com/evansmusitu/mft-axiom-build/pull/66
- Current Intelligence source: https://github.com/evansmusitu/evansmusitu.github.io
- Education development record: https://github.com/evansmusitu/chemforge-enterprise-android

## Remaining independent quality verification

The 6 local static test groups passed. Browser-level and screen-reader accessibility tests, Core Web Vitals, contact delivery, verified company legal identity, real Cloudflare account readback and production deployment were **not** performed or certified.
