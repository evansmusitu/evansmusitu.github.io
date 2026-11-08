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
| 4. Search Console and Bing site verification completed | **BLOCKED** | GSC Wizard `list_sites` and `list_bing_sites` returned `payment_required` on 2026-11-07. No provider property ownership/readback available. |
| 5. Approved XML sitemap submitted | **BLOCKED** | Production sitemap independently served; neither Google nor Bing account submission/acceptance is evidenced. |
| 6. Research centre and 12-article portfolio completed | **12 source drafts written; public release NOT DONE** | `editorial/research-drafts/` contains 12 English explainers, all explicitly unapproved. Need technical/editorial/rights review, article HTML routes, unique metadata, approved publication and sitemap changes. |
| 7. Multilingual infrastructure and approved pilot verified | **Gated rendering foundation prepared; publication NOT DONE** | `content/localization-pilot.json`: 3 French sample drafts; Portuguese planned. `approved_hreflang_links` now rejects missing approval/publication and unsafe URLs. No published French/Portuguese pages or hosted locale acceptance. |
| 8. International landing pages and AI-search foundations reviewed | **Core page mapping prepared; expansion review pending** | Six families and research intents mapped; existing product routes preserved. No new location-spam pages, fictitious endorsements, or claims of special AI-ranking inclusion. |
| 9. International analytics, dashboards and alerts operational | **Operational public watch PASS; search acquisition reporting blocked** | Existing hourly public-watch workflow successful on 2026-11-08. Search Analytics by country/query and qualified international conversion dashboard require verified search accounts and privacy review. No tracking scripts added. |
| 10. All CI, accessibility, security and performance acceptance passed | **Targeted source CI only; full release gate open** | Phase 03 source tests (14) and review-mode noindex build have passing Actions evidence. Complete production artifact, hosted WCAG 2.2 AA, cross-browser, penetration/security, real device and Core Web Vitals tests are not evidenced for Phase 03. |
| 11. Approved production deployment independently verified | **Existing site YES; new Phase 03 NO** | PR #33 release and existing live-watch evidence support earlier corporate deployment, not this PR #35. Await separate approval, retained rollback and Cloudflare Pages deployment evidence. |
| 12. Public crawlability, indexability and monitoring evidence recorded | **Current production PASS for crawlable intent; search indexing unknown** | Public watch confirms 33 reachable sitemap URLs and robots; search-engine indexing and Phase 03 post-deployment checks remain outstanding. |

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
