# MUSITU Package A — Actual Local QA Report

Date: **4 November 2026**. Source SHA-256: `c30e0ae55938ea9324aec8ac0998041a7c0a804ef28110c70b38408fa6cf8909`. This report covers the local 34-route candidate subsequently shared as draft PR #32; it is **not a fresh GitHub CI result for PR #32** and does not describe PR #31.

| Test category | Actual observed evidence | Limits |
|---|---|---|
| Static/source/HTTP/sitemap | **115 passed, 0 failed** | Reproducible pytest result; localhost Python client only |
| Route inventory | **34 exact routes** | All noindex; conditional copy not public-approved |
| Chromium layout | **34 pages, 102 viewport checks** at 320/390/1280 CSS px | Browser loads DOM from self-contained source, not localhost URLs |
| Light/dark themes | **204 checks** | No horizontal overflow reported in DOM runner; painted gradients and assistive tech not independently certified |
| JavaScript-disabled | **34 routes** | Native mobile disclosure navigation verified |
| Functional interactions | **12 / 12 passed** | Search, Navigator, Atlas, Evidence Lens, local Ask, theme desktop/mobile, filters, comparison, NPV, chemistry, no-JS menu |
| Runtime errors and network | **0 JS exceptions, 0 external requests** in DOM runner | Only instrumented during runner; no hosted scan |
| HTTP responses | 34 routes: 33 × HTTP 200 and 1 × HTTP 404; unknown route × HTTP 404; local header checks pass | Real local Python HTTP server only, **not production host** |
| Source manifest repeat build | SHA-256 matches between two local builds | Local checks are not a hosted run for the public draft PR commit |
| Portable single-file review navigation | 34 options, selector and internal link smoke PASS | Nondeployable `srcdoc` artifact; CSP intentionally removed |
| Release media | Studio original video and EXIF-bearing PNG **excluded** | Publishing requires independent rights/provenance/caption review |

**Recorded functional fixes during the local review:** inserted a real product comparison panel for previously inert Compare buttons; corrected Escape handling in search dialogs; added a working mobile theme control. All were verified by browser-local regressions.

**Not claimed:** Firefox/WebKit/Safari passes on this 34-route candidate, WCAG 2.2 AA certification, penetration test, live CSP/HSTS, real-user LCP/INP/CLS, cross-device storage preservation, actual availability of external Axiom/Chemistry/Intelligence destinations, legal/brand rights, production monitoring or rollback. Historical 22-route CI and an earlier mobile CLS 0.2815 failure are separate records that must be reconciled before any release.
