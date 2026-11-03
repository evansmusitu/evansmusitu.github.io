# MUSITU Corporate Website — release review traceability

Status: **REVIEW ONLY — NOT PUBLISHED**. Evidence reviewed: 3 November 2026. This document describes the website review branch, not the preexisting MUSITU Intelligence backend.

| Requirement | Evidence in review branch | Disposition |
|---|---|---|
| 22 page/routes | `scripts/build.py`; `tests/test_site.py` | Built and statically verified |
| Six canonical MUSITU families | `claim-register.json` and product routes; brand policy | Built, final marketing copy owner-gated |
| Truthful maturity and limits | `PRODUCTS` source, evidence dialogs, negative tests | Built, future public claims owner-gated |
| No direct private research links | `test_private_repository_links_never_appear_in_public_html_or_claims` | Enforced |
| Existing Intelligence workspaces untouched | Corporate-only branch diff; no live data migration | Preserved by source isolation; deployment requires separate validation |
| Mobile and desktop responsive layout | `browser_extended.py` (198 view combinations) | Passed in Chromium |
| Zero-network site-wide discovery | Embedded public route index; `browser_search.py` (66 views); hosted interaction | Chromium validation; staged only |
| Text spacing, accessible names, focus | `browser_accessibility.py` (66 view combinations) | Automated checks pass; independent WCAG audit pending |
| Navigation with no JS or failed JS asset | `browser_nojs.py` (66 views); `browser_hosted.py` | Automated checks pass |
| Real HTTP routing/CSP/assets | `browser_hosted.py` on GitHub Actions localhost | CI tested; production hosting untested |
| Source and build integrity | SHA-256 build manifest; deterministic rebuild static test | Verified locally/CI |
| CSP and no third-party scripts | HTML meta CSP + static policy tests; hosted inline-script test | Tested in preview; response headers pending |
| No analytics, customer logins, payments or trading | Static build and tests | Confirmed absent from corporate shell |
| Theme persistence | Tab-only `sessionStorage`; hosted browser navigation/reload test | Functional; storage documented |
| Production domain and redirects | None provisioned | Owner/provider verification required |
| Company legal identity/privacy/terms | Draft gates in pages | Legal owner approval required |
| Corporate contact delivery | Existing published email only, no form backend | Owner verification required |
| Safari/Firefox and real assistive technology | Not independently tested | Independent acceptance required |
| Production speed | Static asset budgets enforced; no field data | LCP/INP/CLS require live measurement |
| Cloudflare authority and billing | Not changed or accessed during build | Authorized account audit required |
| Branch/merge/deploy | Draft PR, no merge to main | Separate explicit release authorization required |

## Scope of automated results

Automated checks are useful regression evidence, not third-party certification or blanket production claims. A passing source/CI test does not automatically authorize public release.
