# MUSITU Corporate Website — 6 November 2026 Release-Candidate Review Controls

**Decision: HOLD.** Draft PR #32 remains unmerged and must not be promoted on the strength of this document.

## Legal approval
- External review request sent; no formal sign-off evidenced at this review. Do not treat emailed outreach as legal clearance.
- Privacy/Terms remain conditional until a qualified reviewer approves exact published text and applicable obligations.

## Brand and Studio media
- Exact Axis Knot SVG, 82-second silent Studio demonstration and scrubbed poster are recorded as owner-approved for corporate website use.
- Raw video/poster were present in earlier public PR history and are excluded from this branch tip. This is **not a Git history purge** and gives no assurance that historical copies are inaccessible.
- Obtain separate confirmation of raw-source distribution scope; independently inspect any third-party appearance, poster metadata and descriptive transcript.
- Verified media is only included in a protected staging build via `MUSITU_PROTECTED_STAGING_MEDIA=1` with a checksum match; normal preview/build remains media-free.

## Accessibility acceptance — release gate remains open
- Source inspection confirms semantic `main`, skip link, native dialogs and details, reduced-motion rules, visible-focus styling and no dynamically inserted HTML via `innerHTML` in site.js.
- Required, not yet evidenced: manual keyboard and focus audit; NVDA/Firefox, VoiceOver/Safari and relevant mobile assistive technology; contrast/reflow/zoom; dynamic announcements; video text alternative; axe on 34 routes of the exact hosted revision; defect retesting and reviewer sign-off.
- Historic 115 local tests, 34-route DOM checks and earlier hosted preview scans **must not** be reported as a fresh CI pass for this candidate.

## Hosting/security/preservation — release gates remain open
- Test exact protected host's headers, TLS, CSP, 404, external navigation, response caching and access isolation, plus Chromium/Firefox/WebKit and mobile CLS.
- Preserve existing Intelligence origin and browser-local workspaces; test backup/export compatibility and rollback before any routing change.
- Confirm corporate inbound email and outbound reply workflow independently.
- Name monitoring owner, incident escalation and backup/rollback testers; collect completed rehearsal evidence.

**No public production authorization, domain/DNS change, PR merge, media publication, legal approval, or independent security/WCAG certification is granted here.**
