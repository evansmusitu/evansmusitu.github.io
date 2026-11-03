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
- No server-side tracking, localStorage, remote JavaScript, remote fonts, or contact form exists. The only sessionStorage key is the optional tab-scoped visual theme preference (`musitu_corporate_theme_v1`), which contains no user content and is not transmitted.

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

## November 3 implementation review addendum
- A published-source visibility audit found two private GitHub repositories previously linked from the FMI and Foundry product pages. Public references now resolve to the internal public evidence overview and state that underlying primary research is not public; generated HTML/claim JSON test forbids the private repository slugs.
- The AXIOM main action no longer points to an unverified ChatGPT app URL. It points to the published GitHub release/correction record until an owner-approved public product entry link is verified.
- Corporate theme choice is optional, tab-scoped only (`sessionStorage`) and does not use cookies, localStorage, accounts, analytics, or customer information. Public privacy copy reflects this precisely.
- A mobile JS-loading failure previously could leave only a nonfunctional menu button. The primary navigation now remains usable when the script is unavailable, even when JavaScript is technically enabled. Dead controls disappear without the script.
- An automated control-name/ARIA/duplicate-ID/text-spacing audit was added. Text-spacing enlargement previously overflowed seven pages; fixes now pass all 66 layout checks.
- New HTTP/Chromium CI acceptance exercises actual HTML, CSS, JS, routes, CSP, theme navigation and no-JavaScript navigation on GitHub Actions localhost. The ChatGPT managed browser prohibits navigation to localhost, so local real-URL browser results are not claimed.
- **Not yet qualified:** independently verified accessibility conformance, production-domain HTTP response security headers, privacy/legal identity, contact delivery, real-user Core Web Vitals, Safari/WebKit/Firefox behavior, final domain routing and Cloudflare account authority.

## November 3 search enhancement (Build 6 review)
- Public company-page discovery uses a locally embedded route index, without analytics, remote requests, hidden documents or personal data. Gated pages are omitted from indexed results.
- Search dialog has a labeled search input, status announcements, semantic list of results, keyboard shortcuts, ArrowDown/ArrowUp focus management, Escape dismissal, and trigger focus restoration.
- With JavaScript disabled or missing, the search button is hidden and ordinary navigation remains functional.
- This capability is a staged corporate-site interface, not a general MUSITU AI or research search service.

## Reviewer functionality and browser-engine gates (Build 6)
- Added four explicit audience navigation paths, using linked product maturity and evidence rather than invented customer segments or case studies.
- Portable reviewer closes open search dialogs when internal navigation occurs and places focus on the replacement page's `main` landmark.
- Chromium, Firefox and WebKit coverage is configured as a required CI test; each engine tests 22 routes at three viewport sizes, mobile navigation and search. A local Chromium-only success cannot be described as a three-engine success.
- Search is documented in the preview privacy section, does not transmit queries, and is excluded when JavaScript is unavailable.

## Lab performance versus field performance
- A staging localhost browser report is generated under `review-artifacts/performance-lab.json` with Chromium first-contentful-paint observations, LCP candidates, observed layout shifts and asset bytes. This is not a production page-speed score or a substitute for the real-user 75th-percentile Core Web Vitals targets.
- The proposed response CSP, Permissions-Policy, Referrer-Policy, and nosniff rules are documented in `DEPLOYMENT_SECURITY_HEADERS.md`, but no live headers can be claimed without origin/account readback.

## Build 7 — structured independent quality boundaries

- Rejection tests cover authority-confusion URLs (`github.com@evil.example`, misleading subdomains, custom ports), percent-encoded CR/LF, malformed internal paths and unauthorized `mailto` headers. The source validator is build-time only, protecting *staged corporate outbound links*; it is not an external-site content audit.
- The navigation state and breadcrumb hierarchy are now static HTML. This works with normal page loads and no-JavaScript access, including mobile fallback.
- Evidence modal external links disclose new-tab behavior and internal source summaries remain in-page navigation. This was found while expanding automated accessibility tests.
- The computed browser contrast audit checks **solid-background text only**, currently 88 route/size/theme views. It intentionally skips complex painted backgrounds; the figures must not be presented as certified WCAG compliance or accessibility conformance.
- The review workflow uses fixed GitHub action commit IDs validated against official GitHub release tags, with `persist-credentials: false`; a passing CI build does not establish full dependency-chain integrity or production hosting security.
- Production release remains blocked pending independent accessibility, security and legal review, confirmed contact, verified domain/response headers, real-user field performance and separate explicit owner merge/deploy authorization.

## Build 7 navigation stability and layout-shift incident

- Previous read-only CI run 41587211958 measured mobile `/products/` staging CLS 0.2815, which violates the 0.1 lab gate. The evidence is retained; it has not been rewritten as passing.
- Root-cause candidate: a pre-script mobile navigation expanded the header until `has-js` was assigned by deferred JavaScript. The staged correction uses a closed native `<details>` menu with stable header geometry and a no-JavaScript navigation overlay.
- This is subject to fresh real-HTTP CI verification. A successful static or injected-DOM test alone does not close the browser CLS gate.
- The performance script now writes `performance-lab.json` before failing when a layout-shift observation exceeds the budget. A failed release gate must not be suppressed or relabeled as success.
