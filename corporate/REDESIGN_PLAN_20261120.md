# MUSITU corporate website — redesign and engineering plan
Date: 2026-11-20
Owner intent: eliminate repeated/poorly engineered experiences and establish a professional international presentation.
Scope: isolated corporate website source only; no edits to unrelated MUSITU Intelligence, Axiom services, credentials, customer data, DNS or production deployment.

## Evidence baseline
- Live website independently fetched on 20 Nov 2026; homepage repeats product cards, goal navigator, ecosystem atlas and evidence summaries available on dedicated pages.
- Main source has 34 HTML routes and 33 intended public sitemap URLs; root 404 handling was separately repaired in November.
- All 34 pages carry a repeated header embedded directly in content/pages.json (~207 KB aggregate); product-family pages also repeat headings and stock explanatory language.
- The 2026 Phase 03 international expansion remains a distinct draft PR (#35), with release gates; do not publish or silently merge it.

## Design decision
Preserve the static-first Python builder and canonical route URLs. Reject a framework rewrite that adds dependencies, client-side hydration, and deployment risk without improving product evidence. Replace the overgrown homepage with a concise editorial story: a clear promise, three documented proof points, buyer-focused paths, an Axiom example, a transparent engineering method, and a real contact action. Keep deep comparisons, interactive navigator, evidence lens and ecosystem visualization on dedicated routes. Retain honest published / prototype / research boundaries; do not invent customer logos, metrics, certifications, availability or legal identities.

## Deliverables
1. **Shared navigation source:** one header template, route-aware active state and aria-current, with per-page serialized header removed from content/pages.json. Builder rejects stale header fields. Test that every route gets exactly one navigation header and that active states are accurate, including nested product pages.
2. **Homepage and conversion:** replace current homepage sections with a focused editorial layout, avoid duplicate multi-family listings, put evidence next to claims, direct visitors to Axiom, Products, the Experience Lab, Trust, and Contact. Preserve all 34 routes and no-JavaScript navigation.
3. **Visual system:** improve typographic hierarchy, spacing, consistent card patterns, responsive grid, contrast and focus behavior. No remote fonts, trackers, mock telemetry or new user data collection. Maintain reduced-motion behavior and keyboard access.
4. **Regression and release:** run deterministic 34-route Python checks, production-mode sitemap/canonical/header checks, Node JavaScript syntax, cross-browser DOM/interactive and axe checks, mobile real-device/human accessibility, real public HTTP header & 404 verification, privacy and correspondence disclosure check, contact round-trip, and rollback rehearsal before merge/promotion.

## Acceptance contract
- Exact original 34 paths stay navigable and corporate production remains untouched until separately qualified.
- Navigation source is single-owned; current route uniquely identified in both desktop/mobile navigation when linked.
- Homepage contains one H1, a small number of differentiated sections, unique meaningful CTAs, no fake metrics/testimonials and no dependency on JavaScript for core content.
- Existing legal/privacy text is not silently rewritten, and no additional private registration or address information is disclosed.
- Test reports distinguish static source evidence from hosted and human verification. Fail closed on any material regression.

## Open release decisions
- Final legally sufficient public contact-identification wording and confidentiality review.
- Owner-approved design critique after a real-device preview.
- Integration and publication sequence with Phase 03; do not mix changes into its pending draft without conflict review.

## Release policy
Branch and PR are for review. Do not auto-merge, reconfigure production hosting, publish Phase 03, or refresh search engine submissions.