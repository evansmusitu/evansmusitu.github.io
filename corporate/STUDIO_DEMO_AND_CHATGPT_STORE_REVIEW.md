# Protected Studio demonstration and MUSITU Axiom ChatGPT destination

The direct ChatGPT destination shown on the Axiom page is:
https://chatgpt.com/plugins/plugin_asdk_app_6ae058ee6cec81919329ae43b76a4c86

MUSITU application materials identify this URL, but a logged-out public directory search did not establish universal discoverability or installability. Do not claim universal availability or OpenAI review/approval.

## Staging-only authentic 3D recording

The approved owner-review package contains an 82-second, silent H.264 Studio recording (1600 × 900, 24 FPS). It documents offline editor interaction, keyframe animation, animated GLB export and a separately labeled calculation. It is **not** live public AI-to-3D, integrated Axiom-to-Studio, or cloud GPU rendering.

Video source SHA-256:
`afd6dfd3c73668e544f3f8a857697fed0abaadccd4927202bb3a185612c2dea0`

Metadata-scrubbed poster SHA-256:
`0ea5e961d916375029010dbae01bf8a1783e5fd6b90f74c006dc852df1c285d0`

Media binaries are intentionally not committed in this public draft PR. To make the real video playable in an **Access-protected review build**, an authorized deployment operator must obtain the validated owner-provided files and place them at `corporate/assets/studio-demo-82s.mp4` and `corporate/assets/studio-poster.png` in the isolated build environment. Run `MUSITU_PROTECTED_STAGING_MEDIA=1 python3 scripts/build.py`. The build refuses absent or altered media and outputs an ordinary same-origin video player in Studio and Experience Lab. The transcript remains readable. Without this environment flag the review/build keeps its media clearance notice and embeds no video.

Do not expose restricted staging to anonymous visitors. No public media-rights clearance, public DNS, PR merge, or production deployment is implied. The video and poster are excluded from this GitHub source, and only a separate approved production release can make them publicly accessible.
