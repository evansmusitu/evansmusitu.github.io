# MUSITU — Brand and Studio Media Verification and Decision Record (6 Nov 2026)

**Status: PARTIALLY VERIFIED — owner approval recorded; third-party, actual MP4 and release acceptance open.** The site remains a draft under protected-release controls.

## Independently checked artefacts

| Asset | Actual bytes and provenance checked | SHA-256 | Result |
|---|---|---|---|
| Axis Knot master SVG at `corporate/assets/favicon.svg` | 924-byte current GitHub draft artifact compared byte-for-byte to the master SVG embedded in the owner's MUSITU Visual Operating System Drive source | `f0e73478176b335bf3cfb5afd8bd7249d5aa39f2627798af7c71d9f13972c2fd` | **PASS:** exact match to owner master and brand register. SVG namespace valid; no script/remote reference detected in inspected text. |
| Studio poster, former public PR object | 30,375 raw decoded bytes from GitHub historical revision `df87c9b`; PNG 320 × 200; parsed chunk sequence `IHDR/IDAT/IEND`; no `eXIf`, `tEXt`, `iTXt` or `zTXt` chunks | `0ea5e961d916375029010dbae01bf8a1783e5fd6b90f74c006dc852df1c285d0` | **PASS:** byte checksum and inspected metadata-chunk criterion. Poster render independently inspected at native resolution: stylized 3D geometric scene on a dark background, no visible text, brand logo, person or obvious third-party symbol. This bounded visual scan does not establish copyright ownership or comprehensive third-party clearance. |
| Studio 82-second H.264 MP4 | Historical public Git blob `79a43a75ed7ac50deb0ca45a6eee49736737d86e` (previous recorded size 1,540,312 bytes); owner demo notes reviewed. Full binary could not be streamed through this repository connection (>1 MB textual contents limit). | **Expected only:** `afd6dfd3c73668e544f3f8a857697fed0abaadccd4927202bb3a185612c2dea0` | **PENDING actual-byte hash, codec/duration/frame check, frame-by-frame third-party and personal-information inspection.** Do not claim independently verified video SHA. |

The owner-authorized register approves website use of the exact logo, video and scrubbed poster. This record is not a trademark clearance opinion, statutory legal approval, independent media license review, or publication GO.

## Provenance and factual accuracy

The original Drive `MUSITU_Demo_Reviewer_Notes.md` (25 Oct 2026) describes an **offline** 3D editor, camera orbit, sphere placement, coordinate changes, rotation-keyframe animation playback and exported animated GLB (13 meshes, 13 nodes, 13 materials, one animation clip). A separate Axiom `geometry.volume_sphere` example at radius 2 returned a numeric result with `verified: null`; it is not an independent certificate. Gemini-based scene generation, Studio–Axiom integration and public cloud/GPU rendering are **not demonstrated**.

Publication language must consistently describe an authentic **recorded offline prototype** and the separate Axiom calculation; do not imply integrated systems, vendor endorsement or general availability.

## Accessibility equivalent — candidate sequence for reviewer to cross-check

The recording is silent with on-screen text. An equivalent text description must cover all substantive visual steps, any informative visual annotations, and the separation between demonstrated and proposed functions. Candidate sequence, **not independently timed or certified**:

1. The offline Studio editor and interactive 3D viewport appear.
2. The user moves the camera around the scene to inspect geometry.
3. A sphere is added and the object's position is adjusted.
4. Rotation keyframes are created and an animation is played in the editor.
5. An animated GLB file is exported; the source reviewer separately validated its structure.
6. The video displays a separate Axiom numerical computation and its result, **not** a connected Studio–Axiom workflow.
7. Proposed Gemini-related workflow appears as roadmap material, not an implemented feature.

The media reviewer must compare this text against the complete 82 seconds, verify all essential on-screen text and visuals, and decide whether on-page text alternatives or synchronized descriptive media are required. The website's existing transcript must be expanded if necessary. Silence does not waive accessible alternatives for prerecorded video-only content.

## Public Git-history scope and recommended interim decision

**Evidence:** Earlier public PR #32 commits tracked both video and poster; current review branch tip does **not** include either. The normal Git deletion did not purge earlier objects or downstream copies.

**Interim recommended choice: retain history unmodified and maintain current-tip exclusion, while requesting an explicit owner/legal decision on whether raw-source redistribution is authorized.** Do not force-push or rewrite Git history merely to improve appearances; doing so cannot guarantee erasure from caches/forks and may disrupt provenance or collaborators.

**Required decision, signed by rights holder/operator:**
- A. Authorize raw files to remain historically publicly retrievable, subject to any third-party permissions, or
- B. Request a separately planned, risk-assessed Git-history remediation and understand that remote copies may persist.
- Confirm whether checksum-verified files may be distributed via the final **website media host** (distinct from Git repository) after independent review and production approval.

## Remaining sign-off record

- Master logo exact-byte check: **PASS**
- Poster checksum and structural metadata scan: **PASS**
- MP4 SHA/duration/codecs and full-frame privacy/IP inspection: **PENDING**
- Poster visual scan for visible text/people/logos: **PASS (bounded inspection only)**
- Full accessibility equivalent, video/player/manual assistive technology: **PENDING**
- Trademark similarity/third-party marks rights assessment: **PENDING**
- Raw Git history/remediation owner decision: **PENDING**
- Production media publication authorization and CDN/cache checks: **PENDING**

**Brand-media gate: PARTIALLY EVIDENCED; corporate website production: HOLD.**
