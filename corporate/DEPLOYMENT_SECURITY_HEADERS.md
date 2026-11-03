# MUSITU corporate: response-header and origin policy (owner review)

**Not a deploy instruction; no production change authorized.** This is a proposed verification contract for a future dedicated corporate domain or edge hostname.

## Same-origin corporate shell

The corporate site has no analytics, login, forms, network AI calls or remote JavaScript. Its currently generated CSP is a **meta** policy for staging and cannot enforce all security response directives. Prefer a stricter **HTTP header** set only after testing the exact deployed corporate hostname:

```http
Content-Security-Policy: default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; form-action 'none'; base-uri 'none'; object-src 'none'; frame-src 'none'; frame-ancestors 'none'
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
```

A `Report-To` or `Content-Security-Policy-Report-Only` endpoint is not activated by this review: it needs a privacy/retention owner and an approved destination. HSTS should be considered **only after** the exact custom domain, subdomain hosting, HTTPS coverage and rollback strategy have been verified. Do not set `includeSubDomains` blindly. Do not copy these restrictions onto the existing Intelligence application: its tools and API connections require a different policy.

## Deployment separation

- Current live MUSITU Intelligence host and the existing browser-origin encrypted workspaces remain untouched.
- The corporate generated `dist` files are **not** wired into the existing root Pages workflow. Do not merge or deploy them without exact-release authorization.
- Draft legal, contact, developer and status pages remain noindex staging content. A release must not silently remove any critical owner gate.
- Avoid GitHub global Cloudflare API keys. Prefer a narrowly scoped token in a dedicated environment, independently verified by an authorized operator; never inspect secret values.
- Verify `Cache-Control` on immutable assets, HTML freshness, redirect/404 behavior, strict TLS and appropriate CDN logs/retention only after the target host is chosen.

## Required acceptance evidence

1. Exact domain owner and approved DNS configuration.
2. Header readback from the **actual** TLS endpoint (not just the build artifact).
3. XSS/CSP negative probe, unauthorized form/network block, absent third-party scripts.
4. Verified cache invalidation, health checks, 404 behavior, safe rollback and monitoring.
5. Mobile desktop accessibility review and no loss of existing local encrypted workspaces.
6. Independent security review and separate founder release authorization.

Automated localhost tests in GitHub Actions establish **staging application behavior only**. They cannot certify any of the above provider-configured production controls.
