# MUSITU Phase 03 — exact-source acceptance ledger

**Captured:** 2026-11-08 (UTC)  
**Disposition:** **HOLD FOR REVIEW — NOT DEPLOYED**.  
**Corporate production origin:** https://mftintelligence.com  
**Website source:** `evansmusitu/evansmusitu.github.io`, `corporate/`; draft PR #35.  
**Preserve:** current corporate Pages deployment, standalone MUSITU Intelligence/GitHub Pages, protected Cloudflare preview, emails, legal content and customer workspaces.

Source-side checks for the Phase 03 candidate and read-only checks of the **existing** production site are distinct evidence classes. Do not conflate them.

## Evidence register

| User-requested acceptance item | Phase 03 result | Grounded evidence / missing proof |
| --- | --- | --- |
| 1. Existing production routes and keyword map reconciled | **Source prepared; editorial approval pending** | `content/seo-routes.json`: 33 core canonical routes; 404 excluded. 34-route master contract preserved. Search volume and ranking not asserted. |
| 2. Technical SEO, robots, sitemap, redirects and canonicals validated | **Existing production PASS; new candidate only source tested** | Production watch run [42434788640](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42434788640) checked apex/www, public sitemap (33 routes), headers and important routes. Phase 03 live schema/canonicals require deployment then public observer. |
| 3. Organization, product, article and breadcrumb schema validated | **Organization/product/breadcrumb source PASS; article publication gated** | `scripts/seo.py`, `tests/test_phase03_seo.py`. Article contract rejects drafts; no public Article pages currently authored. Independent Google rich-result eligibility not asserted. |
| 4. Search Console and Bing site verification completed | **Historical owner notifications found; direct current provider readback blocked** | Historical provider verification notifications are available in the private owner mailbox; latest ownership state still requires authenticated dashboard readback. GSC Wizard currently refuses account reads with `payment_required`. Do not expose private account details or mistake connector billing for expired search-engine verification. |
| 5. Approved XML sitemap submitted | **BLOCKED** | Production sitemap independently served; neither Google nor Bing account submission/acceptance is evidenced. |
| 6. Research centre and 12-article portfolio completed | **12 source drafts written; public release NOT DONE** | `editorial/research-drafts/` contains 12 English explainers, all explicitly unapproved. Need technical/editorial/rights review, article HTML routes, unique metadata, approved publication and sitemap changes. |
| 7. Multilingual infrastructure and approved pilot verified | **Gated rendering foundation prepared; publication NOT DONE** | `content/localization-pilot.json`: 3 French sample drafts; Portuguese planned. `approved_hreflang_links` now rejects missing approval/publication and unsafe URLs. No published French/Portuguese pages or hosted locale acceptance. |
| 8. International landing pages and AI-search foundations reviewed | **Core page mapping prepared; expansion review pending** | Six families and research intents mapped; existing product routes preserved. No new location-spam pages, fictitious endorsements, or claims of special AI-ranking inclusion. |
| 9. International analytics, dashboards and alerts operational | **Operational site watch + new email index alerts; private reporting source prepared, live dashboard NOT ACTIVE** | Existing public monitor operating, plus owner-enabled daily search index notice watch. `scripts/international_growth_report.py` prepares privacy-limited country/keyword-theme/enquiry aggregates from approved normalized exports, without raw search queries or visitor identifiers. Live country data, authorized CRM counts and account/API access remain missing. No tracking scripts added. |
| 10. All CI, accessibility, security and performance acceptance passed | **15 Phase 03 + 118 inherited review + 5 production tests and 3-engine offline browser QA passed; hosted gates remain open** | Run [42449477762](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42449477762): 15 source tests, 118 inherited review tests, 5 production tests, 33 JSON-LD core routes, reproducible build, and 34 routes across Chromium, Firefox and WebKit (each 102 responsive, 204 theme, 34 no-JS and 12 interaction checks). Hosted WCAG 2.2 AA, cross-browser, penetration/security, real device and field Core Web Vitals acceptance remain unevidenced for Phase 03. |
| 11. Approved production deployment independently verified | **Existing site YES; new Phase 03 NO** | PR #33 release and existing live-watch evidence support earlier corporate deployment, not this PR #35. Await separate approval, retained rollback and Cloudflare Pages deployment evidence. |
| 12. Public crawlability, indexability and monitoring evidence recorded | **Existing production public watch PASS; historical Google Search visibility evidenced; Phase 03 indexing unknown** | Current live public watch confirms 33 reachable sitemap URLs and robots. Historical private provider notices support earlier search visibility but not current route-level indexing. Phase 03 post-release public observer and provider index coverage remain outstanding. |

## Exact-source development history

- Source CI [42408730048](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42408730048) ran 13/13 initial tests against `fac85a97d2ba8626333f7ea8d0937931f16c34ec`.
- Hreflang red/green cycle: expected missing-function failure in [42447333464](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42447333464), then pass in [42447376114](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42447376114).
- HTML newline emission regression: expected failure in [42447409700](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42447409700), followed by 14/14 source tests green in [42447447386](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42447447386).
- Existing independent public watch [42434788640](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42434788640) reports `status=PASS`, `indexable_sitemap_routes=33`, apex/www, headers, email MX, private preview and Intelligence isolation, `writes=0`.

These tests establish **source contracts only**. Independent live Phase 03 observer must run **after deployment**, not against the earlier release.

## Release admissions — strict order

1. Obtain final acceptance of keywords, copy and claims; verify every source and external right in the 12 research drafts; obtain competent native-language review of selected translations.
2. Build an immutable exact-SHA production artifact with Studio media hash checks, and run full production security, WCAG, real device, cross-browser, Core Web Vitals and content regression acceptance.
3. Execute an explicit owner-approved **corporate Cloudflare Pages** release with previous deployment reserved as rollback; leave GitHub Pages MUSITU Intelligence and all protected infrastructure intact.
4. Run existing public corporate monitor plus `scripts/public_seo_observer.py` against the new deployed artifact, record timestamp, responses and exact artifact identity.
5. Verify site ownership through authorized Google Search Console and Bing Webmaster Tools access; submit `https://mftintelligence.com/sitemap.xml`, retain provider readback, and establish index/performance baseline.
6. Activate privacy-reviewed country/language performance reporting and operational alerts only after working data-source permissions and retention controls are proven.

**No silent release, fabricated provider verification, unapproved translation, duplicate page expansion or downgrade of acceptance grades.**

## 8 November 2026 — deeper code/research verification

- Added a content-addressed, offline editorial review renderer: `corporate/scripts/research_review.py`. It generates an index, 12 standalone HTML draft previews, and a JSON review manifest carrying the SHA-256 of each manuscript. Every generated HTML declares `noindex,nofollow`; no public canonical, article JSON-LD, sitemap, or webroot output is produced.
- TDD trace for missing review renderer: [expected RED 42447958187](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42447958187), then [15/15 GREEN 42448025825](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42448025825).
- Expanded [review/source qualification 42448117036](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42448117036) passed **15 Phase 03 unit tests + 42 inherited local HTTP/sitemap/Studio/Store tests**, generated all twelve review previews and uploaded review-only artifact `musitu-phase03-research-review-only`, retention 14 days.
- Added a **non-deploying production-candidate test** using immutable previously qualified source artifact `MUSITU-CORPORATE-PR33-PRODUCTION-87cc21fc` (run 42287099983, artifact 13537253738), from which **only the previously approved media files** were extracted. The video SHA-256 is `afd6dfd3c73668e544f3f8a857697fed0abaadccd4927202bb3a185612c2dea0`; poster SHA-256 `0ea5e961d916375029010dbae01bf8a1783e5fd6b90f74c006dc852df1c285d0`.
- [Production-mode source verification 42448284667](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42448284667) passed **5/5 production tests**, generated **34 routes**, checked actual generated metadata/JSON-LD on **all 33 indexable-intent core routes**, and ran two matching production builds; deterministic manifest SHA-256 `8f0b3867567f7357f0d8b686786d4a8d1251842ccae6b620fa6bce4791fdf5df`. **No public deployment occurred**.
- Google Search Central documents recommended [Article properties](https://developers.google.com/search/docs/appearance/structured-data/article) and requires `offers.price` for [SoftwareApplication rich-result eligibility](https://developers.google.com/search/docs/appearance/structured-data/software-app). We intentionally do not invent any offering/price and do **not** claim Google rich-result eligibility merely because valid Schema.org descriptions were generated.
- Production-mode acceptance with approved media is **source/artifact qualification**, not hosted browser, true search-engine validation, independent accessibility, international analytics or production cutover.

**Release remains HOLD.** Preserve the live Cloudflare deployment and corporate monitoring while the remaining review, account verification and hosted acceptance gates are completed.

## 8 November 2026 — expanded three-browser source qualification

[Exact-head CI run 42449477762](https://github.com/evansmusitu/evansmusitu.github.io/actions/runs/42449477762) on source `09ff9fe5960667b84093aeaa9e43d1517eefcb64` completed successfully. Verified logs showed 118/118 inherited review tests, 15/15 Phase 03 source tests, 5/5 production build contract tests, deterministic production manifest and 33 rendered canonical JSON-LD core pages. Production builds were **not deployed**.

Browser matrix verified Chromium, Firefox and WebKit independently. For **each** engine: 34 routes, 102 viewport checks, 204 theme checks, 34 no-JavaScript checks and 12 interactions; no observed JS exceptions, unexpected network requests or layout overflow in the offline DOM runner. Runner intentionally inlines local assets and removes CSP for this offline DOM test. It is **not** hosted HTTP/CSP, independent WCAG 2.2 AA certification, physical device testing, penetration testing, or field Core Web Vitals evidence.

Security hardening: the phase workflow's previous-release media download and its downstream browser matrix are now restricted to same-repository PR heads or explicitly authorized manual workflow_dispatch. Untrusted fork pull requests may execute credential-free source checks only; they must not be able to access the previous approved media artifact.

No external provider account verification, search-engine submission, localization or article publication, corporate DNS change, deployment or full release gate has occurred.

## 8 November — search-account evidence and privacy-limited reporting

Private historical Google and Bing provider messages support **prior** verified property ownership, but cannot replace currently authenticated provider readback. The connected Search Console app returns `payment_required` and an alternative browser account lacks a funded browser session; do not claim the live property still belongs to the current connection or that its sitemap has been processed. The existing domain sitemap is publicly monitorable, not proof of submission. Provider messages about indexing are monitored through an owner-enabled daily condition watch, without uploading account data or disclosing private message content publicly.

Added a private normalized-export processing contract at `scripts/international_growth_report.py`, with synthetic-data-only tests at `tests/test_phase03_growth.py` and the source guide `PHASE03_INTERNATIONAL_GROWTH_MONITORING.md`. It separates Google/Bing, country, query-theme and qualified-enquiry aggregates; rejects unsupported inputs, hides raw search queries, saves outputs with mode 0600, forbids public build output and never claims live APIs, verified sitemap submissions or real index coverage. The report cannot become an active growth dashboard until legitimate owner exports and privacy-approved qualification data are available.
