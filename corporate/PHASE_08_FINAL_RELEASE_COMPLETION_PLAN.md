# MUSITU Corporate Website — Phase 08: Final Release Qualification & Production Launch

**Date:** 6 November 2026  
**Scope:** The remaining work for the 34-route MUSITU corporate website in draft [PR #32](https://github.com/evansmusitu/evansmusitu.github.io/pull/32), and the final separately authorized publication to the owner-selected `mftintelligence.com` origin.  
**Program structure:** **One final completion phase**, comprising seven coordinated acceptance workstreams. There are no additional phases and no reduced acceptance grades.  
**Decision today:** **HOLD / NOT PRODUCTION-READY.** Draft PR, no merge, no DNS mutation, no public website rollout.  
**Protected systems:** Existing MUSITU Intelligence origin and browser-local workspaces, product apps, payments, mail, and Cloudflare Workers are outside the default change boundary. No Package B paid AI inference or live-account capability is bundled into this release.

## Operating rules

1. Workstreams can run in parallel, but **all seven must be PASS** before the final production-release decision. Record PASS only with an actual reviewer/owner, date, exact tested revision, relevant artefacts, and defect closure.
2. Freeze the exact Git commit and asset hashes for protected-host acceptance. Any subsequent source, policy, asset or configuration change invalidates only the affected acceptance evidence and requires retesting before release.
3. Use an Access-protected, noindex, verified hosting environment for testing; perform independent readback of the actual response and routing. A prior Cloudflare preview or offline DOM test is **not** acceptance for this revision.
4. Do not claim legal compliance, WCAG conformance, security qualification, end-to-end email delivery, or recovery unless the relevant evidence exists.
5. Keep public copy confined to necessary corporate, product, privacy and support information. Verify all legally required notices and actual operational data flows before publication; do not commit confidential working records to the website or Git source.
6. Do not rewrite Git history, expose media or private workspaces, merge, change DNS, or promote production as a side effect of planning or test preparation. A separately approved, bounded action is required.

## The seven workstreams within this single phase

| ID | Workstream / accountable reviewer | Required completion and exact evidence | Current state |
|---|---|---|---|
| W1 | **Legal, Privacy and Terms** — accountable website publisher and compliance operator | Final accurate Privacy Policy and Terms for the deployed site; verify applicable controller/DPO obligations, mandatory electronic and business disclosures, hosting/security logs, support correspondence, international processing, consumer rights, retention and complaint handling. Record operational verification and approved publication version. | **PARTIAL:** draft policies expanded; mandatory operator and regulatory particulars, vendor/retention facts and final publication checks remain unverified. |
| W2 | **Brand, Studio and Media** — rights holder + publisher + media/accessibility reviewer | Confirm exact approved Axis Knot SVG, scrubbed poster and silent 82-second Studio video hashes; third-party appearances and accurate capability/no-endorsement statements; independently validate video text alternative and metadata. Record separate decision on historical Git media exposure and future raw-source distribution. Test checksum-gated staging playback. | **PARTIAL:** owner approval recorded; raw media removed from current PR branch tip, but historical objects remain; other reviews open. |
| W3 | **Accessibility** — independent accessibility reviewer | Manual keyboard/tab/focus/escape/modal/menu audits; contrast, text zoom/reflow at 320px and 400% where applicable; semantic landmarks and error/status announcements; reduced-motion; NVDA + Firefox, VoiceOver + Safari and appropriate mobile assistive technology. Run axe and route-by-route checks on the *hosted exact artifact*; resolve and retest violations against **WCAG 2.2 AA**. Include transcript/player and all 34 routes, including gated pages and real 404 behavior. | **OPEN:** source-level safeguards exist, but full independent hosted audit/sign-off absent. |
| W4 | **Security, Browsers and Performance** — independent security reviewer + release engineer | Build and test PR #32 exact SHA; verify authenticated Cloudflare Access protection and no anonymous staging; response CSP, TLS, HSTS policy, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, frame protection, redirects and caching from the actual host. Test all 34 routes and internal/external links, mobile/desktop, Chromium/Firefox/WebKit/Safari, keyboard without JS, forms/dialogs, no unintended third-party calls and 404. Validate Core Web Vitals including prior mobile CLS regression. Publish reproducible reports, defects and corrections. Field CWV: LCP <=2.5s, INP <=200ms, CLS <=0.1 at p75 when enough traffic exists; otherwise state lab-only qualification without falsely claiming field acceptance. | **OPEN:** historical local results and different-artifact protected preview cannot transfer to new SHA; no current CI pass. |
| W5 | **Domain, Contact and Destinations** — authorized DNS/mail operator | Inventory apex/www, mail, API, payment, application, Worker and other existing routes before any DNS change; select conflict-free canonical origin; prove TLS/DNS and effective Access boundaries. Conduct genuine independent-sender mail delivery and **reply** acceptance for support, privacy and accessibility contact; check SPF/DKIM/DMARC as relevant. Verify real external links, including Axiom's specific ChatGPT destination, without implying universal discoverability or endorsement. | **OPEN:** domain selected, but complete origin/email/link acceptance not evidenced. |
| W6 | **Preservation, Monitoring, Backup and Rollback** — current Intelligence operator + infrastructure owner | Establish baseline and compare original/live root application versus new corporate origin; confirm no shadowing, domain redirects, customer-storage or Worker regressions. Exercise permitted smoke and workspace/export compatibility without reading private user data. Establish monitoring, named incident contact, alarms, immutable backup/snapshot or provider recovery equivalent, tested restore and documented rollback with measured timings. Preserve evidence and set acceptance RPO/RTO explicitly. | **OPEN:** preservation evidence and historical monitoring are not an independently tested recovery rehearsal. |
| W7 | **Controlled Production Release** — MUSITU website owner/release approver | Obtain one final consolidated GO sign-off after W1–W6 PASS, referencing exact revision and asset hashes. Confirm release checklist, canonical sitemap/robots/indexability after legal clearance, production headers and incident readiness. Only then separately authorize merge, route/domain changes and production deploy. Perform post-deploy 34-route smoke, security-header/canonical/contact checks, error and Web Vitals monitoring, and rollback on failure. Archive release evidence and close the phase. | **NOT AUTHORIZED:** no production merge/deploy permission and prerequisites unmet. |

## Execution order inside Phase 08 (not separate phases)

**A. Establish immutable candidate + safe staging.** Freeze the review commit and media hashes; verify branch integrity and no root-application changes; construct protected hosting with a complete, deterministic build. Keep legal pages conditional and indexability off. Do not publish media until allowed for the specific venue.

**B. Run parallel acceptance.** The accountable operator completes W1's factual and mandatory-disclosure checks; owner/reviewers finish W2; QA/security complete W3–W4 against the exact hosted candidate; operators demonstrate W5–W6. Log issues, fix in draft PR, rebuild and rerun impacted gates. No test pass is inferred from preparation.

**C. One GO / NO-GO checkpoint.** Verify that W1–W6 each have direct evidence and reviewer acceptance, and W7 has an owner-issued, bounded written release authorization. Absent any item, mark **NO-GO**, keep protected staging and do not merge.

**D. Execute approved production publication within W7.** Apply only approved release operations, test production immediately, preserve rollback, monitor and close the same phase after stable acceptance.

## Required handover/evidence bundle

- Exact Git SHA, complete source diff, 34-route matrix, reproducible build manifest, approved asset hashes.
- Final accurate public Privacy Policy/Terms; verified obligations and operational compliance evidence register.
- Brand/media rights statement, transcript/accessibility validation and historical Git media-distribution decision.
- Hosted screenshot/report set, full automated and manual WCAG accessibility evidence, browser/device coverage, documented remediation.
- Actual HTTP header/TLS/CSP/Access/404 evidence, CWV numbers with explicit lab/field provenance, security findings disposition.
- DNS/domain dependency inventory, independent inbound and outgoing reply evidence, tested external links.
- Intelligence regression/baseline, backup/restore rehearsal, alerts/incident ownership, rollback steps and observed outcome.
- Final owner GO record for exact artefact, production deploy receipt, post-launch acceptance and monitoring observation.

## Release invariant

`PRODUCTION_GO = W1_PASS && W2_PASS && W3_PASS && W4_PASS && W5_PASS && W6_PASS && W7_OWNER_AUTHORIZED`

If any term is false, the disposition remains **HOLD**. One phase does **not** mean waiving mandatory obligations or any of the other acceptance gates. This plan is a draft-branch governance update only, **not** consent to perform production-impacting actions.

## Phase 08 W1/W2 execution started — 6 November 2026

- **W1 privacy/terms:** Draft copy now covers technical requests, browser storage/security cookies, contact, purposes, vendors, rights, cross-border processing, children and separate transactions. The statutory operator/processing facts and data-controller obligations still require actual evidence. No release-ready publication check has been recorded; this workstream remains open.
- **W2 media:** Exact GitHub favicon was matched to owner Visual Operating System master and SHA-256 checked. Historical PNG poster SHA-256 and PNG metadata chunks verified; raw video binary/frame review, rights/public Git history decision and accessibility equivalent remain pending. See `BRAND_MEDIA_VERIFICATION_20261106.md`.
- The Studio/Lab placeholder language was adjusted in the draft source to recognize owner site-use approval while making unresolved independent release gates explicit. This requires a new build and affected-route regression before sign-off.
