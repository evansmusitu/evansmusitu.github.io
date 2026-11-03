# MUSITU Corporate — Security, accessibility and operational release contract

**State:** isolated implementation; not approved for production. **Review date:** 2026-11-03.

## Separation and trust boundaries
- The corporate build lives exclusively in `corporate/`. Its browser script does not call a network API, use cookies, store user content, run payments, or accept file uploads.
- The existing MUSITU Intelligence app stays deployed at its existing origin. Its encrypted local workspaces, local source-evidence workflows and Cloudflare Workers remain unchanged.
- External AXIOM links are navigation only. No customer login, remote workspace, keyless OAuth, billing, trading or Store payment is integrated or released.
- Company identity, contact destination, legal notices, custom domain ownership, product disclosure and Cloudflare account authority remain owner/provider sign-off items.

## Current technical controls
- Every generated HTML page has `noindex,nofollow`; `robots.txt` disallows all crawling.
- Every generated HTML page carries restrictive meta CSP: no default remote fetching, only same-origin script/style/media/fonts, `connect-src 'none'`, `form-action 'none'`, no objects or frames, and `base-uri 'none'`.
- All content is escaped, programmatically generated from audited static product records; external link schemes are allowlisted to HTTPS or mailto.
- Evidence records use safe textContent assignment and explicit source-review dates; recorded maturity must not be confused with a production certification.
- All outbound HTTPS links opening new tabs include noopener and noreferrer.
- No server-side tracking, client localStorage, sessionStorage, remote JavaScript, remote fonts, or contact form exists.

## CSP limitation and hosting requirements
- A CSP `<meta>` element supports only a subset of response-header security policy. In particular, `frame-ancestors` and reporting requirements must be set at the hosting response layer, where supported.
- GitHub Pages does not allow custom arbitrary HTTP response headers through an `_headers` file. If the final deployment stays there, verify equivalent controls through a trusted edge layer or document accepted remaining limits.
- HTTP `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, and a server-level CSP including `frame-ancestors 'none'` require deployment-specific verification; none are claimed by the static artifact alone.
- The offline single-file HTML preview deliberately omits the CSP because it embeds self-contained CSS and JavaScript. **Never serve the portable preview as production.**

## WCAG 2.2 AA acceptance
- Verified programmatically: language, one H1, main/header/footer landmark structure, labeled inputs, skip link, ARIA current state, accessible dialog labeling, focus restoration, theme toggle control state, keyboard Escape, 320 px reflow simulation, reduced-motion CSS, and 4.5:1 fixed color-token contrast across core surfaces.
- Not yet verified: VoiceOver/NVDA/TalkBack end-to-end, Safari/WebKit, Firefox, high contrast/forced colors, text-spacing overrides, 200–400% browser zoom using real assistive environments, cognitive comprehension and independent manual WCAG conformance.
- Large button targets are provided for key CTAs; evidence and navigation text-link spacing should be manually inspected under WCAG 2.2 Target Size exceptions.

## Performance and recovery
- Define a release-size budget, perform Lighthouse and WebPageTest lab runs, then validate real-user LCP <=2.5s, INP <=200ms and CLS <=0.1 at the 75th percentile, mobile and desktop separately. No real-user field scores are claimed yet.
- Production publishing is intentionally absent. Review an explicit build artifact, approve exact branch/commit and diff, test staging, then promote separately with real rollback and monitoring.
- Preserve the current site and local encrypted workspace origins until the owner approves a real user-controlled migration plan, including offline/export/import and passphrase recovery limitations.

## Mandatory external approvals
1. Founder signs off on exact public copy, product maturity, contact address, legal identity and public domain.
2. Legal/privacy specialist reviews actual data practices and country-specific terms.
3. Authorized Cloudflare administrator performs account inventory, least-privilege review, DNS, security header and environment check; **never extract credential values from GitHub Actions secrets**.
4. Independent security and accessibility reviewers provide observable results and can block a release.
5. Owner issues separate explicit merge and deployment authorization after receiving the acceptance packet. No automatic deployment on this branch.
