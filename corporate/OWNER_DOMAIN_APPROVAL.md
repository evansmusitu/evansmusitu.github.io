# MUSITU corporate domain selection — 5 November 2026

**Owner-selected domain:** `mftintelligence.com`. This authorizes website planning and a draft source PR using that domain as a candidate corporate origin. It does **not** authorize DNS changes, Cloudflare configuration changes, migration of the existing MUSITU Intelligence origin, or public production deployment.

## Safeguards

- Validate registrant/zone control and effective DNS and Cloudflare Access policies using authorized read-only account access.
- Inventory any existing apex, `www`, application, API, payments and email dependencies before selecting origin routing.
- Ensure an isolated preview remains noindex and Access protected. Do not attach a custom domain until separately approved.
- Generate only an unpublished sitemap candidate for `https://mftintelligence.com/` pending exact canonical selection, legal readiness, final security headers and owner release authorization.
- Preserve the current Intelligence origin, local browser workspaces and Cloudflare Workers unless a distinct migration is authorized.

## Existing historical evidence

Read-only GitHub Actions review identified successful 3 November 2026 protected corporate preview workflows in `evansmusitu/mft-axiom-build` (runs `41712809858` and `41716545176`). These runs establish historical staging use, **not** ongoing credential validity, a completed corporate production deployment, or final readiness.
