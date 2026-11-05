# MUSITU Corporate Website — Local Implementation Acceptance Matrix

Review date: 4 November 2026. **Local-only source; not an authorization to push, merge or deploy.**

## Master route inventory

All routes below exist as actual generated static HTML and were covered by the 115-test static/HTTP suite and the 34-route Chromium DOM review. "Locally tested" is *not* "publication cleared".

| # | Exact route | Page title | Local disposition |
|---:|---|---|---|
| 1 | `/` | MUSITU — Intelligence with evidence. Technology with purpose. | Built & locally tested / editorial review pending |
| 2 | `/company/` | About MUSITU — MUSITU | Built & locally tested / editorial review pending |
| 3 | `/trust/` | Trust & Responsible Technology — MUSITU | Built & locally tested / editorial review pending |
| 4 | `/accessibility/` | Accessibility — MUSITU | Built & locally tested / editorial review pending |
| 5 | `/products/` | Products & Technologies — MUSITU | Built & locally tested / editorial review pending |
| 6 | `/products/axiom/` | MUSITU Axiom — MUSITU | Built & locally tested / editorial review pending |
| 7 | `/products/education/` | MUSITU Education — MUSITU | Built & locally tested / editorial review pending |
| 8 | `/products/foundry/` | MUSITU Foundry — MUSITU | Built & locally tested / editorial review pending |
| 9 | `/products/markets/` | MUSITU Markets — MUSITU | Built & locally tested / editorial review pending |
| 10 | `/products/fmi/` | MUSITU Frontier Market Intelligence — MUSITU | Built & locally tested / editorial review pending |
| 11 | `/products/worldfabric/` | MUSITU WorldFabric — MUSITU | Built & locally tested / editorial review pending |
| 12 | `/products/education/chemistry-rescue/` | Chemistry Rescue — MUSITU | Built & locally tested / editorial review pending |
| 13 | `/products/foundry/studio/` | MUSITU Studio — MUSITU | Built & locally tested / editorial review pending |
| 14 | `/solutions/` | Solutions — MUSITU | Built & locally tested / editorial review pending |
| 15 | `/solutions/finance-research/` | Finance & Research — MUSITU | Built & locally tested / editorial review pending |
| 16 | `/solutions/learning/` | Learning & Education — MUSITU | Built & locally tested / editorial review pending |
| 17 | `/solutions/creative-production/` | Creative Production — MUSITU | Built & locally tested / editorial review pending |
| 18 | `/solutions/enterprise-systems/` | Enterprise Systems — MUSITU | Built & locally tested / editorial review pending |
| 19 | `/experiences/` | Experiences — MUSITU | Built & locally tested / editorial review pending |
| 20 | `/experiences/intelligence/` | MUSITU Intelligence — MUSITU | Built & locally tested / editorial review pending |
| 21 | `/experiences/lab/` | Experience Lab — MUSITU | Built & locally tested / editorial review pending |
| 22 | `/ecosystem/` | Living Ecosystem Atlas — MUSITU | Built & locally tested / editorial review pending |
| 23 | `/research/` | Research — MUSITU | Built & locally tested / editorial review pending |
| 24 | `/evidence/` | Evidence — MUSITU | Built & locally tested / editorial review pending |
| 25 | `/resources/` | Resources — MUSITU | Built & locally tested / editorial review pending |
| 26 | `/developers/` | Developers — MUSITU | Conditional / not approved for publication |
| 27 | `/news/` | News & Updates — MUSITU | Conditional / not approved for publication |
| 28 | `/contact/` | Contact — MUSITU | Built & locally tested / editorial review pending |
| 29 | `/support/` | Support — MUSITU | Built & locally tested / editorial review pending |
| 30 | `/status/` | Service Status — MUSITU | Conditional / not approved for publication |
| 31 | `/legal/privacy/` | Privacy Policy — MUSITU | Conditional / not approved for publication |
| 32 | `/legal/terms/` | Terms of Use — MUSITU | Conditional / not approved for publication |
| 33 | `/sitemap/` | Sitemap — MUSITU | Built & locally tested / editorial review pending |
| 34 | `/404/` | Page Not Found — MUSITU | Built; true HTTP 404 verified on loopback server / production host conditional |

## Required interface behaviors

| Behavior | Local disposition | Evidence/remaining qualification |
|---|---|---|
| Six canonical product families; separate Intelligence experience | Built, static checks passed | `public-records.json`; live product current access not reverified |
| Navigator goal-based local discovery | Chromium DOM pass | Does not invoke AI or profiling |
| Evidence Lens | Chromium DOM pass | Source claims dated; external source validity owner-gated |
| Living Ecosystem Atlas + text equivalent | Chromium DOM pass; static text alternative present | Needs real assistive technology review |
| Experience Lab deterministic NPV and chemistry example | Chromium DOM pass | Not remote Axiom computation or a live education-app test |
| Studio recorded demonstration | Explicitly gated | Real video/poster withheld until rights/provenance/captions approved |
| Global local search, keyboard and Escape | Chromium DOM pass | In-memory DOM runner, not HTTP-loaded browser test |
| Six-family search/filter and comparison | Chromium DOM pass | Comparison panel added after defect detected |
| Mobile navigation and theme control | Chromium DOM pass | 320px/390px checks; no device certification |
| No-JavaScript navigation | 34-route Chromium DOM pass | Native nested disclosure confirmed |
| Responsive layout, dark/light | 102 viewport checks / 204 theme checks | No horizontal overflow reported in this runner; real devices pending |
| Staging `noindex`, robots, local CSP | 115-test suite pass | Server CSP/HSTS on selected production host pending |
| Real HTTP routing and 404 | Local Python HTTP pass | Production provider routing not tested |
| Production sitemap | Template implemented, not published | Canonical domain and conditional-route clearance required |
| Ask MUSITU | Browser-local informational guide only | AI backend remains Package B, not approved |

## Interpretation

All observed local results have test logs and reproducible source. **Production-ready is NO.** A passing in-memory browser test or isolated static preview cannot close legal, brand-rights, operational or live-infrastructure gates. Current PR #31 covers 22 routes, not this local 34-route candidate.
