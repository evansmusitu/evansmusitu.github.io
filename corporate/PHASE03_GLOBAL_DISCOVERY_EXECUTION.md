# Phase 03 — Global Discovery implementation and release control

**Date:** 2026-11-07  
**Canonical domain:** https://mftintelligence.com  
**Source:** `evansmusitu/evansmusitu.github.io`, directory `corporate/`.  
**Isolation:** The GitHub Pages root remains MUSITU Intelligence. Corporate releases use the separately protected Cloudflare Pages project. This branch does not deploy or change Cloudflare, DNS, e-mail, legal text, billing, or private workspaces.

## Baseline reconciled

Core corpus: 34 routes, of which 33 may appear in the production sitemap; the 404 route stays `noindex`. The canonical origin and static production sitemap/robots contract already exist in `corporate/scripts/build.py`. The source now contains a route-to-search-intent register with exactly 33 unique primary queries at `corporate/content/seo-routes.json`. It is a content planning register, not a claim of search volume, ranking or market demand.

## Production-only structured metadata

`corporate/scripts/seo.py` emits JSON-LD only for approved public production pages. The graph includes bounded `Organization` and `WebSite` definitions on the homepage, hierarchical `BreadcrumbList` definitions for the other indexable core routes, and descriptive `SoftwareApplication` markup on the evidenced Axiom and Studio pages. The code does not create ratings, prices, product offers, private registration details, or unsupported endorsements. No `Article` metadata may appear until genuinely published article URLs exist.

## Research editorial packet

Twelve original technical draft files are stored under `corporate/editorial/research-drafts/`. Each includes methodology, conceptual example, limits, evidence reference and product-context boundary. **Drafts are not publicly published, indexable, or editorially approved.** An authorized reviewer must approve their facts, rights and technical quality before publication. Publishing must add actual HTML article routes, accessible internal links, page-specific metadata, Article JSON-LD, sitemap entries, deterministic tests and the real live-site monitor expectation. The existing exact 34-route contract must not be silently expanded.

## Languages and geographic targeting

`corporate/content/localization-pilot.json` describes an English primary site, a three-page French translation **draft**, and a Portuguese candidate. Neither French nor Portuguese pages are deployed, indexed or marked as live. After approval, each localized page needs its own canonical, translated visible copy, native-language validation, reciprocal `hreflang`, accessible language selection and verified sitemap entries. Avoid low-value automated translation and IP-based forced redirects.

Initial international search targeting: product-led navigation around Axiom and the six technology families; evidence-led discovery around quant research, model risk, verification, financial data quality and decision support. Market and language expansion is conditional on actual enquiry and search-demand evidence. No unsupported market-share or global ranking claims.

## Search Console and Bing operational controls

1. Validate live DNS, canonical HTTPS, public robots.txt and sitemap.xml at the exact production deployment.
2. Verify domain ownership in [Google Search Console](https://search.google.com/search-console/welcome) through an authorized domain DNS verification record.
3. Verify in [Bing Webmaster Tools](https://www.bing.com/webmasters/) and use its verified sitemap submission workflow. IndexNow is optional and only applicable to genuinely changed public URLs.
4. Submit `https://mftintelligence.com/sitemap.xml` and retain provider acceptance/readback and URL Inspection evidence.
5. Do not claim submission, property verification, indexing or ranking without provider evidence. The GSC Wizard connection returned `payment_required` on 2026-11-07, and the Browser Use connection returned `insufficient_credits`. These blocks do not justify bypassing verification.

## International analytics and privacy

Use aggregated query, country, page and search-impression data from verified webmaster tools. Track branded/non-branded discovery, indexed canonical URLs, qualified contact referrals and operational crawler errors. Begin with privacy-preserving server-side operational observations. **Do not install third-party analytics, cookies or trackers without disclosure review, consent/rights assessment where required and a documented data-retention policy.** Avoid collecting IP/user-agent logs in the open repository.

## Independent public observer

`corporate/scripts/public_seo_observer.py` provides bounded, read-only independent checks for all 33 existing public core routes, canonical and robots consistency, validated deployed JSON-LD, same-origin sitemap membership and security headers. A separate manually triggered workflow may be run after deploying the candidate. Its successful result is evidence of accessible indexed-intent signals, **not Google indexing or eligibility for rich results**. Preserve the existing hourly corporate monitor and avoid exposing its protected staging origin.

## Completion gates (fail closed)

- [x] Current authoritative source and 33 indexed-intent core routes identified.
- [x] Keyword register created with unique route intents (candidate mapping; approval pending).
- [x] Source-side structured-data implementation and regression checks prepared.
- [x] Twelve technical research article drafts created, publication gated.
- [x] Locale routing contract and French draft pilot prepared, not published.
- [ ] CI result for exact Phase 03 commit verified.
- [ ] Independent technical/editorial/native-language approval of expanded publications.
- [ ] Production staging and accessibility, cross-browser, security and performance acceptance for the new candidate.
- [ ] Controlled Cloudflare Pages deployment with verified rollback.
- [ ] Fresh public SEO observer and existing hourly corporate monitor pass on deployed candidate.
- [ ] Google Search Console verified property plus accepted sitemap submission.
- [ ] Bing verified property plus accepted sitemap submission.
- [ ] Public indexing evidence and international discovery baseline retained.

Do not merge to `main` or deploy the draft branch based on documentation alone. Never use the separate GitHub Pages root site as a corporate deployment target.
