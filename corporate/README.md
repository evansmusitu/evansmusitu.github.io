# MUSITU Corporate Website — review candidate (2 Nov 2026)

**ISOLATED WORK. DO NOT MERGE OR DEPLOY WITHOUT EXPLICIT OWNER RELEASE APPROVAL.**

This package implements the approved MUSITU corporate specification as a deterministic 22-route static site, with the six canonical product families, an Intelligence experience entry point, source links, truthful maturity states, responsive navigation, mobile product explorer, theme controls, working legal/support draft routes, SEO metadata and verification boundaries. The site is intentionally **noindex** and has no analytics, contact-form backend, customer account creation, payment gateway or live changes.

## Build

```bash
python3 scripts/build.py
python3 -m pytest -q tests/test_site.py
python3 tests/browser_smoke.py
python3 tests/browser_extended.py
python3 scripts/make_portable_preview.py
python3 -m http.server --directory dist 8000
```

Browser: `http://localhost:8000/` (the site uses root-relative routes). Static build requires only Python 3.12; static tests need pytest and BeautifulSoup; browser checks additionally require Playwright and Chromium. The standalone offline review file is generated at `review-artifacts/MUSITU_portable_interactive_preview.html` (portable review removes the production CSP for inline CSS/JS).

## Evidence and independent verification

`dist/claim-register.json` is a machine-readable register of the six product families, public source references, evidence review date, maturity and limitations. The generator includes a restrictive CSP meta policy, noindex, no remote scripts, no forms, and explicit external URL checks. See `RELEASE_REVIEW.md` for the limitations of CSP meta, unresolved real-browser/AT testing, hosting controls and release gates.

Static CI checks asset limits, metadata, internal links, product disclosures, contrast tokens, deterministic output, CSP, and approved schemes. The extended offline Chromium check covers 22 pages across nine viewport sizes and keyboard interaction. These checks **do not establish** hosted performance, security certification, legal validity or WCAG conformance.

## Important preservation rule

Do not replace the existing `index.html` or `/assets/musitu-*` files; leave the live Intelligence site and local encrypted workspaces intact. The corporate package is built and staged separately. New domain/origin migration needs explicit local workspace export/import acceptance.

## Release gates

- Owner approval of exact company copy, legal name, canonical domain, published contact and public product disclosures
- Privacy, terms and accessibility statements reviewed for actual deployment behavior
- Real-account Cloudflare/DNS and least-privilege deployment review
- Manual browser, mobile and WCAG 2.2 AA acceptance, security checks and real-form routing if contact form added
- Regression verification of existing live Intelligence site and no local-vault loss
- Remove noindex only on an explicitly approved production release

## Evidence sources

- Existing site: https://github.com/evansmusitu/evansmusitu.github.io
- Canonical products: https://github.com/evansmusitu/mft-axiom-build/blob/main/branding/MUSITU_BRAND_CANONICAL.json
- Axiom plugin release review: https://github.com/evansmusitu/mft-axiom-build/pull/47
- Customer identity NOT RELEASE: https://github.com/evansmusitu/mft-axiom-build/pull/66
- Education pilot: https://github.com/evansmusitu/chemforge-enterprise-android

Full release requires separate owner authorization even after tests pass.
