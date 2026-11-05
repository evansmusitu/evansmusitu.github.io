#!/usr/bin/env python3
"""Create a reproducible owner-readiness packet from the local Package A evidence."""
from pathlib import Path
import json,hashlib
from datetime import date
ROOT=Path(__file__).resolve().parents[1]
DIST=ROOT/'dist'
MANIFEST=json.loads((DIST/'manifest.json').read_text())
PUBLIC=json.loads((ROOT/'content/public-records.json').read_text())
ROUTE=MANIFEST['routes']
RUN=json.loads((ROOT/'review-artifacts/browser-dom-results.json').read_text())
assert RUN['routes_tested']==34 and RUN['passed']

(ROOT/'README.md').write_text('''# MUSITU corporate website — isolated Package A review candidate

**Authority:** MUSITU-WEB-MASTER-1.0; MUSITU-WEB-AUTH-001.  
**Mode:** Local-only Package A owner review. **NOT published. NOT merged. No public PR push authorized.**  
**Review:** 4 November 2026. Reconstructed from the owner-supplied 34-route portable preview (SHA-256 documented in `content/source-provenance.json`), not from a clone of GitHub PR #31.

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

This package makes **no remote source changes**. The live `evansmusitu/evansmusitu.github.io` root site, existing MUSITU Intelligence workspaces, product repositories, Cloudflare services, DNS, deployments, emails, payments and provider billing are not modified. The old remote PR #31 is a separate **22-route** baseline and must not be described as containing this new local 34-route implementation. See `RELEASE_REVIEW.md` and `RELEASE_GATES.json` before any remote sharing, merge or publication.
''',encoding='utf-8')

route_rows=[]
for idx,route in enumerate(ROUTE,1):
    state='Conditional / not approved for publication' if route in MANIFEST['gated_routes'] else 'Built & locally tested / editorial review pending'
    if route=='/404/':state='Built; true HTTP 404 verified on loopback server / production host conditional'
    page=json.loads((ROOT/'content/pages.json').read_text())[route]
    route_rows.append(f'| {idx} | `{route}` | {page["title"].replace("|","/")} | {state} |')
(ROOT/'ACCEPTANCE_MATRIX.md').write_text('''# MUSITU Corporate Website — Local Implementation Acceptance Matrix

Review date: 4 November 2026. **Local-only source; not an authorization to push, merge or deploy.**

## Master route inventory

All routes below exist as actual generated static HTML and were covered by the 115-test static/HTTP suite and the 34-route Chromium DOM review. "Locally tested" is *not* "publication cleared".

| # | Exact route | Page title | Local disposition |
|---:|---|---|---|
'''+ '\n'.join(route_rows)+'''\n
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
''',encoding='utf-8')

brand='''# MUSITU Brand and Media Register — owner review

As of 4 November 2026. **Candidate assets are not cleared for production.**

| Item | Source/provenance | Included in local `dist/`? | Publication disposition |
|---|---|---|---|
| Provisional geometric SVG favicon | From owner-supplied preview | Yes | Rights and exact approved emblem files required |
| Horizontal/compact/monochrome MUSITU lockups | Master specification | No | Final brand master files and rights required |
| Studio 82-second offline prototype recording | Embedded in prior owner preview; original provenance not independently reauthenticated | **No** | Rights, contextual claim, edit and captions required |
| Studio video poster / PNG render | Prior preview; metadata may include EXIF and file history | **No** | Provenance + metadata sanitization required |
| Studio 77-second vertical candidate | Master shortlist | No | Rights and claim review required |
| Chemistry Rescue imagery | Master shortlist | No | Current authentic safe captures required |
| Axiom quantitative screenshots | Master shortlist | No | Reproducible synthetic outputs and independent math review required |
| MUSITU Intelligence screenshots | Master shortlist | No | Current, safe synthetic captures and identity/privacy review required |

The Studio page displays an explicit rights-clearance notice instead of a dead video player. No third-party tracking images, embedded remote scripts or remote video sources were introduced. The provisional favicon remains review-only, not proof of brand source-rights clearance.
'''
(ROOT/'BRAND_MEDIA_REGISTER.md').write_text(brand,encoding='utf-8')

rec_lines=[]
for e in PUBLIC['evidence']:
    rec_lines.append(f'''### {e["title"]}

- **Record ID:** `{e["id"]}`; **associated family:** {e["family"]}
- **Evidence type:** {e["kind"]}; **source review date:** {e["date"]}
- **Supported claim:** {e["claim"]}
- **What is established:** {e["establishes"]}
- **What is not established:** {e["limits"]}
- **Public link or staged explanation:** `{e["link"]}`
''')
(ROOT/'CONTENT_EVIDENCE_REGISTER.md').write_text('''# MUSITU Content and Evidence Register — local public-safe candidate

Content source: `content/public-records.json`, imported from the supplied owner preview. The entries are *editorial evidence claims* reviewed on the recorded dates; their presence in this package does not independently revalidate current live availability or certify the underlying systems. Never substitute controlled research records for publicly inspectable sources.

## Six canonical families

'''+ '\n'.join(f'- **{x["name"]}** — {x["category"]}; page `{x["path"]}`; limit: {x["limits"]}' for x in PUBLIC['families'])+'''\n
## Public-safe claim records

'''+ '\n'.join(rec_lines)+'''
## Mandatory current-availability checks

Before release, independently verify the actual Axiom ChatGPT listing, the Chemistry Rescue and Chemistry Mastery product destinations and version state, contact delivery, existing Intelligence entry origin, and any approved external CTA. Research claims remain bounded and may not imply live trading, deployed enterprise identity, public marketplace checkout or production GPU rendering.
''',encoding='utf-8')

(ROOT/'DEPLOYMENT_SECURITY_HEADERS.md').write_text('''# Proposed HTTP Security Header Contract — NOT applied to any live system

The `dist/` HTML contains a restrictive staging meta CSP and `noindex`; `scripts/preview_server.py` adds headers **only on the local loopback development server**. Production requires read-back from the owner-approved actual host and may need an edge proxy. The following is a *review template*, not a Cloudflare or GitHub Pages configuration change:

```text
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; media-src 'self'; connect-src 'none'; object-src 'none'; frame-src 'none'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
X-Frame-Options: DENY
X-Robots-Tag: noindex, nofollow  [staging only]
```

For production, choose and test the HSTS policy against the complete domain/subdomain inventory; do not enable `includeSubDomains` or preload without owner/provider assessment. A production indexing change needs explicit release approval, verified canonical origin, legally cleared conditional pages and a real `sitemap.xml` on the final host. `robots.txt` is not access control and cannot enforce staging confidentiality. `_headers` is platform-dependent, especially for a runtime/Worker path; verify effective HTTP headers rather than file presence.

Avoid placing credentials or private document content in source, generated JSON, CI logs or static assets. No secrets are required for Package A.
''',encoding='utf-8')

(ROOT/'SECURITY_REVIEW.md').write_text('''# Local Static Security Review — bounded results

**Observed:** 34 routes generated with staging noindex; no backend, cookies, third-party analytics, uploads, customer logins, payments, remote inference or order processing. All executable website scripts are same-origin static assets; the public record corpus contains seven bounded evidence entries and no private Drive source material. Source import excludes the embedded Studio video and PNG poster. The isolated review server adds noindex and defense-in-depth response headers for local HTTP tests.

**Executable checks:** 115 static/HTTP/sitemap tests and 34-route Chromium in-memory DOM suite; 12 local interactive use-cases. The comparison buttons were initially inert and were corrected to generate a structured comparison panel; Escape in search dialogs was corrected to dismiss consistently; mobile theme was made available through the mobile menu. The successful regression evidence is recorded in `review-artifacts/`.

**Not tested or not established:** authenticated production Cloudflare account security, real DNS/hosting settings, response headers on real origins, deployment pipeline permissions, HSTS, HTTP-to-HTTPS behavior, actual form delivery, independent penetration testing, real Safari/Firefox/WebKit browser conformance, independent WCAG audit, real-user traffic/performance, source rights, privacy/terms legal compliance and live Intelligence workspace preservation. These are release blockers, not exceptions to acceptance criteria.

**Security boundaries:** the portable preview removes the meta CSP solely to embed local CSS/JS, and must never be deployed. The production package is not authorized. Do not attempt secrets extraction from GitHub workflows or use public PRs as a substitute for source-disclosure review.
''',encoding='utf-8')

(ROOT/'PRESERVATION_CONFIRMATION.md').write_text('''# Existing MUSITU Intelligence Preservation — source boundary

Owner authority: `MUSITU-WEB-AUTH-001`, Package A, local-only. All new work was placed under `/mnt/data/corporate/`; no remote source writes were made, and no local clone of `evansmusitu/evansmusitu.github.io` was modified. Root-level production `index.html`, root `assets/`, Workers, AI provider configuration, local encrypted workspaces, DNS, Cloudflare, hosting, payment systems, mailboxes and product repositories were outside the operations performed.

Read-only GitHub evidence earlier in the review established that [PR #31](https://github.com/evansmusitu/evansmusitu.github.io/pull/31) remains a draft 22-route candidate, with head `d48a3752b3de2df7dbdf5d073bccc1ee5a158144`; its changed files were corporate/* plus a read-only review workflow. This new local build is **not that pull request** and has not been pushed there.

**Remaining mandatory preservation acceptance:** owner-authorized original-vs-new source diff; actual live application smoke and storage/export compatibility checks; confirmation that any approved corporate domain does not shadow the Intelligence origin; and rollback rehearsal. No live application behavior or private stored user workspaces were accessed or modified.
''',encoding='utf-8')

status={
 "review_date":"2026-11-04","package":"A","implementation_local_only":True,
 "source_origin":"owner uploaded 34-route offline preview","owner_approved_remote_push":False,"owner_approved_deployment":False,"owner_approved_package_b":False,
 "local_static_tests":{"passed":115,"report":"review-artifacts/pytest-results.txt"},
 "local_chromium_dom":{"routes":RUN['routes_tested'],"responsive_viewports":RUN['responsive_checks'],"theme_views":RUN['theme_checks'],"no_javascript_routes":RUN['nojs_checks'],"interactions_passed":sum(x=='PASS' for x in RUN['interactions'].values()),"errors":len(RUN['errors'])+len(RUN['overflow'])+len(RUN['runtime_exceptions']),"report":"review-artifacts/browser-dom-results.json"},
 "gates":[
  {"id":1,"name":"Production domain and hosting","status":"blocked","required":"owner-approved canonical domain, authorized Cloudflare/DNS inventory, hosted routing and security header read-back"},
  {"id":2,"name":"Privacy, Terms and legal","status":"blocked","required":"qualified legal sign-off on actual operator, data practices and policies"},
  {"id":3,"name":"Contact and support","status":"blocked","required":"confirmed corporate delivery, verified support route and escalation tests"},
  {"id":4,"name":"Final brand and media rights","status":"blocked","required":"approved master visual identity, asset rights, media safety/captions/metadata review"},
  {"id":5,"name":"Independent security, accessibility, hosted performance","status":"partially_evidenced","required":"third-party security and WCAG reviews, real Chrome/Firefox/Safari tests, hosted LCP/INP/CLS data; prior mobile CLS issue revalidated on exact release source"},
  {"id":6,"name":"Existing Intelligence preservation","status":"partially_evidenced","required":"owner-approved diff/real live app regression/origin/workspace preservation"},
  {"id":7,"name":"Production monitoring, backup and rollback","status":"blocked","required":"service/account owner, alerts, backups, tested restore/rollback rehearsal"}
 ],
 "production_release_decision":"HOLD",
 "missing_owner_decisions":["Remote source visibility and PR update scope","Canonical corporate domain/hosting","Public legal content approval","Verified corporate contact","Final brand/media rights","Package B optional backend provider/model/budget if desired","Explicit separate merge and production release authorization"]
}
(ROOT/'RELEASE_GATES.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

(ROOT/'QA_REPORT.md').write_text('''# MUSITU Package A — Actual Local QA Report

Date: **4 November 2026**. Source SHA-256: `c30e0ae55938ea9324aec8ac0998041a7c0a804ef28110c70b38408fa6cf8909`. This report covers the local 34-route candidate, **not GitHub PR #31**.

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
| Source manifest repeat build | SHA-256 matches between two local builds | No public git commit or deployed artifact tested |
| Portable single-file review navigation | 34 options, selector and internal link smoke PASS | Nondeployable `srcdoc` artifact; CSP intentionally removed |
| Release media | Studio original video and EXIF-bearing PNG **excluded** | Publishing requires independent rights/provenance/caption review |

**Recorded functional fixes during the local review:** inserted a real product comparison panel for previously inert Compare buttons; corrected Escape handling in search dialogs; added a working mobile theme control. All were verified by browser-local regressions.

**Not claimed:** Firefox/WebKit/Safari passes on this 34-route candidate, WCAG 2.2 AA certification, penetration test, live CSP/HSTS, real-user LCP/INP/CLS, cross-device storage preservation, actual availability of external Axiom/Chemistry/Intelligence destinations, legal/brand rights, production monitoring or rollback. Historical 22-route CI and an earlier mobile CLS 0.2815 failure are separate records that must be reconciled before any release.
''',encoding='utf-8')

(ROOT/'RELEASE_REVIEW.md').write_text('''# MUSITU Corporate Website — Release Review and Change Control

**Current disposition: HOLD / REVIEW ONLY**. Package A local implementation is produced; separate remote source-sharing, merge and production publishing authorizations remain absent.

## What Package A local implementation establishes

A generated 34-route, static-first review site with the approved six-family portfolio, four interactive UI systems, browser-local discovery, accessible navigational foundations, no live financial/account/commerce functionality, and optional *local-only* Ask MUSITU. The site is noindex, has conditional legal/status/news/developer content, and excludes uncleared media.

## What it cannot establish

1. The operator's legal identity, published privacy/terms validity and local jurisdiction requirements.
2. The chosen canonical production domain, DNS/Cloudflare/hosting account authority and response headers.
3. Actual delivery/replies from contact and support channels.
4. Rights to the final emblem, photographs, Studio videos, screenshots and audio/captions.
5. Independent WCAG/security review, real-device and Safari/Firefox acceptance, hosted Web Vitals (including CLS requalification).
6. Live MUSITU Intelligence application preservation and user workspace recovery under any domain migration.
7. Production monitoring, backup, incident ownership and successful rollback rehearsal.
8. Consent to public remote source disclosure, PR update, branch merge or deployment.

## Source reconciliation

Connected GitHub PR #31 (`feature/musitu-corporate-v1-20261102` at reviewed SHA `d48a3752b3de2df7dbdf5d073bccc1ee5a158144`) is a 22-route review branch. This 34-route candidate was reconstructed from the owner-supplied 34-route file locally and is **not represented as an update of PR #31**. The next source integration must start with a fresh approved SHA/diff review and separate public source disclosure permission. No workflow changes were performed.

## Product and editorial controls

Axiom direct listing needs independently verified access; historical release/correction record alone does not certify current listing availability. Education currently cited 1.3.0 Android release must be revalidated on release date. Foundry Studio prototype is not GPU cloud render or public AI-to-3D. Markets/FMI/WorldFabric remain research/controlled work. Exact source records with dates and limits appear in `CONTENT_EVIDENCE_REGISTER.md`; they cannot replace external verification or operator approval.

## Release-only actions intentionally withheld

No publication-approved canonical `sitemap.xml`, no noindex removal, no production CSP/HSTS/DNS change, no live status feed, no contact backend, no user accounts, no payments, no AI provider configuration, no rollout or redirect and no disclosure of private source material. The rights-gated Studio media remain excluded. Package B for live Ask MUSITU has not been authorized.

**Decision rule:** no promotion or publishing until all seven external release gates are passed with independent evidence and the owner issues separate explicit merge/deploy instructions. The completed local review packet is available, but a production-release decision is not implied.
''',encoding='utf-8')

sourcefiles=sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and not any(k in p.relative_to(ROOT).parts for k in ('dist','review-artifacts','__pycache__','.pytest_cache')) and not p.name.endswith('.pyc'))
(ROOT/'SOURCE_CHANGE_INVENTORY.md').write_text('''# Isolated Package A local source inventory

All source objects below were created/modified within the isolated `corporate/` workspace from the approved 34-route preview. **No Git remote diff, commit, PR update, merge or deployment occurred.** Do not interpret this as the changed-file list of PR #31.

'''+ '\n'.join(f'- `corporate/{p}`' for p in sourcefiles if p!='SOURCE_CHANGE_INVENTORY.md') + '''\n- `corporate/SOURCE_CHANGE_INVENTORY.md` (this file)

Generated, reproducible build outputs are under `corporate/dist/` (34 page files plus static assets, robots and manifests). Nondeployed visual and QA evidence is under `corporate/review-artifacts/`. The portable owner review HTML is nondeployable because it embeds script/style content without production CSP.
''',encoding='utf-8')

print('Wrote owner packet: README, acceptance, QA, gates, release, source inventory, brand, evidence, preservation, headers, security. No remote changes.')
