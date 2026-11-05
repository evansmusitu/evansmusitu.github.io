# Isolated Package A local source inventory

All source objects below were created/modified within the isolated `corporate/` workspace from the approved 34-route preview. **A source-only commit was pushed to a dedicated branch and draft PR #32 opened on 5 November 2026.** The first remote commit is `85e94ad46eadbd863023d069be6cc8faba4f452a`; this inventory is not the changed-file list of PR #31. No merge, deployment, DNS or Cloudflare modification occurred.

- `corporate/ACCEPTANCE_MATRIX.md`
- `corporate/BRAND_MEDIA_REGISTER.md`
- `corporate/CONTENT_EVIDENCE_REGISTER.md`
- `corporate/DEPLOYMENT_SECURITY_HEADERS.md`
- `corporate/PRESERVATION_CONFIRMATION.md`
- `corporate/QA_REPORT.md`
- `corporate/README.md`
- `corporate/RELEASE_GATES.json`
- `corporate/RELEASE_REVIEW.md`
- `corporate/SECURITY_REVIEW.md`
- `corporate/assets/favicon.svg`
- `corporate/assets/site.css`
- `corporate/assets/site.js`
- `corporate/content/pages.json`
- `corporate/content/public-records.json`
- `corporate/content/source-provenance.json`
- `corporate/scripts/build.py`
- `corporate/scripts/import_preview.py`
- `corporate/scripts/make_portable_preview.py`
- `corporate/scripts/preview_server.py`
- `corporate/scripts/sitemap.py`
- `corporate/templates/dialogs.html`
- `corporate/templates/footer.html`
- `corporate/templates/review-ribbon.html`
- `corporate/templates/skip.html`
- `corporate/tests/browser_portable.py`
- `corporate/tests/browser_review.py`
- `corporate/tests/test_http.py`
- `corporate/tests/test_site.py`
- `corporate/tests/test_sitemap.py`
- `corporate/SOURCE_CHANGE_INVENTORY.md` (this file)

Generated, reproducible build outputs are under `corporate/dist/` (34 page files plus static assets, robots and manifests). Nondeployed visual and QA evidence is under `corporate/review-artifacts/`. The portable owner review HTML is nondeployable because it embeds script/style content without production CSP.

Final review-draft source excludes generated outputs, the portable HTML, screenshots and the one-time report-authoring script. All draft PR paths remain inside `corporate/`.
