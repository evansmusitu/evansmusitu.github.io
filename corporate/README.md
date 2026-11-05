# MUSITU corporate website — isolated Package A review candidate

**Authority:** MUSITU-WEB-MASTER-1.0; MUSITU-WEB-AUTH-001.  
**Mode:** Package A published-source draft review (PR #32). **No production merge or deployment authorized.**  
**Review:** 5 November 2026. Reconstructed from the owner-supplied 34-route portable preview (SHA-256 documented in `content/source-provenance.json`), not from a clone of GitHub PR #31.

## What is included

- All **34 planned routes** from the master route inventory; generated under `dist/` with shared local styles, scripts and routing-independent HTML.
- Six canonical technology families and separate featured MUSITU Intelligence experience.
- Browser-local search, Navigator, Evidence Lens, Ecosystem Atlas, Experience Lab, catalog filters, comparisons, accessible modal interaction and mobile theme control.
- Local-only Ask MUSITU guide, **not live AI**; no analytics, remote fonts, customer accounts, payments or form posting.
- Deterministic manifest, source-controlled public evidence records, 404 local-server handling, staging CSP and noindex controls.
- Rights-gated Studio media and legally/operationally gated review pages.

## Reproduce without external services

Run from `corporate/` (Python 3.12+, Python 3.13 verified):

```bash
python3 scripts/build.py
python3 -m pytest -q tests/test_site.py tests/test_http.py tests/test_sitemap.py
node --check assets/site.js
node --check dist/assets/site-data.js
python3 tests/browser_review.py   # requires Playwright and installed Chromium
python3 scripts/make_portable_preview.py
python3 tests/browser_portable.py  # standalone selector and internal-link smoke test
python3 scripts/preview_server.py --port 8000
```

The browser test uses in-memory page content (with local styles and scripts embedded) because the managed browser in this environment blocks loopback navigation. It is **not a test of hosted CSP, response headers, network routing, Safari/Firefox, real assistive technology or real-world performance**. The Python HTTP test runs on a loopback-only server and checks 34 route responses, headers, assets and true HTTP 404 behavior. It does not touch production.

Open `review-artifacts/MUSITU_34_ROUTE_PORTABLE_OWNER_REVIEW_LOCAL_ONLY.html` directly in a browser for a stand-alone owner review with a 34-route selector. Its embedded CSP is removed solely for offline portable review; **NEVER DEPLOY THIS PORTABLE FILE**. Production delivery must originate from a separately authorized, complete and independently verified source revision.

## Source structure

- `content/pages.json` — per-route reviewed copy, semantic body and page-specific navigation states.
- `content/public-records.json` — six families, seven bounded evidence entries, 34-route local knowledge corpus.
- `templates/` — shared footer, dialogs, skip control and review ribbon.
- `assets/` — visual system, browser-local features and **provisional** favicon.
- `scripts/build.py` — deterministic local `dist/` compilation and claim-register generation.
- `scripts/import_preview.py` — one-time original importer, guarded against accidentally overwriting curated source; **not** part of normal builds.
- `scripts/preview_server.py` — loopback-only manual test server with staging headers and true 404.
- `scripts/sitemap.py` — conditional XML sitemap template: does not generate a production sitemap without a supplied canonical domain, nor publish one.
- `scripts/make_portable_preview.py` — creates the nondeployable 34-route owner review.
- `tests/` — static, local HTTP, sitemap and Chromium offline-DOM regression checks.
- `review-artifacts/` — actual test evidence and owner review material.

## Authority boundaries

The 34-route candidate is published for source review in [draft PR #32](https://github.com/evansmusitu/evansmusitu.github.io/pull/32) at commit `85e94ad46eadbd863023d069be6cc8faba4f452a`, with no merge or production deployment authorization. The live `evansmusitu/evansmusitu.github.io` root site, existing MUSITU Intelligence workspaces, product repositories, Cloudflare services, DNS, deployments, emails, payments and provider billing are not modified. The old remote PR #31 is a separate **22-route** baseline and must not be described as containing this new local 34-route implementation. See `RELEASE_REVIEW.md` and `RELEASE_GATES.json` before any merge or publication.
