# Proposed HTTP Security Header Contract — NOT applied to any live system

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
