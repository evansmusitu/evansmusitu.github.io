# MUSITU Corporate Website — review candidate (2 Nov 2026)

**ISOLATED WORK. DO NOT MERGE OR DEPLOY WITHOUT EXPLICIT OWNER RELEASE APPROVAL.**

This package implements the approved MUSITU corporate specification as a deterministic 22-route static site, with the six canonical product families, an Intelligence experience entry point, source links, truthful maturity states, responsive navigation, mobile product explorer, zero-network site-wide page search, theme controls, working legal/support draft routes, SEO metadata and verification boundaries. The site is intentionally **noindex** and has no analytics, contact-form backend, customer account creation, payment gateway or live changes.

## Build

```bash
python3 scripts/build.py
python3 -m pytest -q tests/test_site.py
python3 tests/browser_smoke.py
python3 tests/browser_extended.py
python3 tests/browser_search.py
python3 tests/browser_crossengine.py --engines chromium # use all engines in CI
python3 tests/browser_accessibility.py
python3 tests/browser_nojs.py
python3 tests/browser_hosted.py # GitHub CI with permitted localhost navigation
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

## Real HTTP acceptance (CI)

`python3 tests/browser_hosted.py` launches an ephemeral Python HTTP server bound to `127.0.0.1`, then exercises the built website in real Chromium. Unlike the existing offline-DOM tests, this checks HTTP routing, stylesheet/JS loading, CSP enforcement, keyboard navigation, product filtering, and JavaScript-disabled navigation. It never calls production APIs or third-party sites.

Note: the ChatGPT container's managed browser policy blocks Chromium URL navigation, so this suite is evaluated on the GitHub Actions runner where loopback navigation is permitted. The local offline-DOM test continues to run independently.

## Accessibility regression checks (not certification)

`python3 tests/browser_accessibility.py` runs DOM-name, duplicate-ID, ARIA-reference, skip-focus, 320px reflow, and WCAG 1.4.12 text-spacing-style regression checks at 320, 390, and 1440 CSS pixels. All pages are checked without calling live services. The output `review-artifacts/accessibility-regressions.json` is uploaded as a review-only artifact. This does not claim complete WCAG 2.2 AA conformance or replace a screen-reader/manual audit.

## Design continuity and privacy

All 22 routes use the same tiny local SVG favicon and the canonical MUSITU navy, violet, and mint palette. Choosing light or dark mode saves only the visual preference in the browser tab's `sessionStorage` under `musitu_corporate_theme_v1`; no preference is sent to a server. If storage is disabled, theme switching still works for the current page. No cookies, analytics, browser localStorage, or customer data are used by the corporate shell. Existing Intelligence local encrypted workspaces are unrelated and never touched.

Private research repositories are never presented as public evidence links. The FMI and Foundry cards direct visitors to a public research/evidence summary until their primary materials receive explicit publication approval. Unverified direct ChatGPT app URLs are not included in this preview; AXIOM's action goes to its published release evidence.

## Missing-script resilience

`python3 tests/browser_nojs.py` checks every route at 320, 390, and 1440 CSS pixels with the corporate script absent. On mobile, a stable native disclosure menu exposes the same navigation without shifting the header; on desktop, the primary navigation remains visible. Interaction-only theme/filter/evidence controls do not become dead buttons. In real HTTP CI, `browser_hosted.py` additionally checks navigation with JavaScript explicitly disabled at mobile and desktop sizes. These two checks cover separate failure mechanisms.

## Corporate site-wide search (review only)

The search control uses a compact public-route index embedded at build time. No remote requests, private Drive content, prompt text, or client analytics are involved. It shows ranked results across approved public corporate and product pages, excluding gated legal/status and error routes. Keyboard shortcuts: Ctrl+K / Cmd+K and `/` outside inputs. Escape closes and returns focus to the trigger. Without JavaScript, the search control disappears while ordinary navigation remains available.

## Portable reviewer and cross-engine acceptance

`python3 scripts/make_portable_preview.py` followed by `python3 tests/browser_portable.py` verifies search-result navigation, dialog closure and focus transfer into the new route, and catalog filtering after client-side route swapping. The portable preview is self-contained but **never a production deploy artifact**.

`python3 tests/browser_crossengine.py` is a required staging CI gate for current Chromium, Firefox and WebKit; it tests all 22 routes at three sizes, verifies search and mobile navigation, and records engine-specific failures. The container-only single-engine invocation does not certify the other engines. Local real HTTP behavior remains verified in Chromium CI; production HTTP headers and independent manual accessibility assessments remain owner/reviewer gates.

## Staging laboratory performance and deployment boundary

`python3 tests/browser_perf.py` on the GitHub Actions runner serves the generated site over local HTTP and records FCP/LCP candidates, observed layout shifts, resource counts, and bytes for four representative routes at mobile/desktop sizes. Metrics are explicitly staging lab observations, **not** real-user Core Web Vitals. It rejects unexpected third-party requests and large layout shifts. The production response-header and origin requirements live in `DEPLOYMENT_SECURITY_HEADERS.md` and must be reviewed against real provider configuration before launch.

## Build 7 hardening: navigation, source integrity and readable evidence links

- All external evidence origins are explicitly allowlisted by `checked_link_url` (`github.com` and the existing public `evansmusitu.github.io` origin). It rejects user-info URLs, alternate ports, misleading subdomains, control characters, protocol-relative links and malformed internal routes. Only the existing publicly documented `support@mftintelligence.com` mail draft is allowed; **corporate email delivery remains unverified**.
- New-window source links include a visually hidden accessible announcement. The evidence dialog uses a same-tab link for internal summaries and new tabs only for reviewed external sources, with a matching announcement.
- Navigation `aria-current=page` and breadcrumbs render server-side and stay available when JavaScript is disabled or fails.
- Site search announces capped result counts correctly and supports ArrowUp/ArrowDown navigation through the result links. The query field is bounded to 120 characters; queries stay in the local browser.
- `tests/browser_color_contrast.py` adds a computed text-contrast regression across all 22 routes at two widths in light and dark modes. It evaluates solid, resolved backgrounds; **gradient/image/translucent areas and real assistive technology still require review**.
- Review GitHub Actions are pinned to exact upstream-verified commit SHAs, checkout credentials are not persisted, and the workflow remains read-only. No production or live app changes.

## Build 7 mobile layout-shift correction

A real GitHub Actions performance observation once recorded staging mobile `/products/` CLS **0.2815**. The first implementation exposed the entire horizontal primary navigation on narrow screens until a deferred script added `has-js`; that header then collapsed after the script loaded. This is a concrete layout-stability risk, not a generic test flake.

The staged correction replaces the expanding pre-script header with a closed native `<details>` fallback menu. It uses a stable 42px slot equivalent to the JS menu button, and the details panel opens as an overlay only upon user interaction. With the script disabled or missing, the native menu still provides all product and company links. Browser/CI performance checks remain hard-gated at measured staging CLS ≤0.1 per route; do not infer production field CLS from these lab checks. Failed checks write the full performance report before exiting to aid diagnosis.
