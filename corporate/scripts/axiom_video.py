"""Create an original, silent 24-second Axiom explainer from recorded computations.

No screenshot, external brand assets, voice recording, synthetic testimonials or
claimed live screen capture. All displayed numbers are source-locked executions.
"""
from __future__ import annotations
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from axiom_proof import examples

SLIDES = (
 ("MUSITU AXIOM", "QUANTITATIVE TOOLS IN ACTION", "Four recorded Axiom executions | 21 Nov 2026"),
 ("INVESTMENT NPV", "10% discount rate, four annual receipts", "+11,215.08 monetary units"),
 ("HISTORICAL RISK", "95% VaR | 20 synthetic period returns", "3.245% per period"),
 ("LINEAR REGRESSION", "Eight synthetic paired observations", "y = 0.975 + 2.0083 x"),
 ("LINEAR OPTIMISATION", "Maximise 3x + 2y within three limits", "x = 2, y = 2 | maximum 10"),
 ("TRY AXIOM IN CHATGPT", "74 capabilities across 18 disciplines", "mftintelligence.com/products/axiom/"),
)
CAPTIONS="""WEBVTT

00:00:00.000 --> 00:00:04.000
MUSITU Axiom. Quantitative tools in action. Four recorded Axiom executions on 21 November 2026.

00:00:04.000 --> 00:00:08.000
Investment net present value. Four annual receipts at a 10 percent discount rate. Result: plus 11,215.08 monetary units.

00:00:08.000 --> 00:00:12.000
Historical portfolio risk. 95 percent value at risk from 20 synthetic returns: 3.245 percent per period.

00:00:12.000 --> 00:00:16.000
Linear regression. Eight paired synthetic observations. Fitted line y equals 0.975 plus 2.0083 times x.

00:00:16.000 --> 00:00:20.000
Linear optimisation. Maximise 3x plus 2y under three capacity limits. Optimum x equals two, y equals two, objective value 10.

00:00:20.000 --> 00:00:24.000
Try MUSITU Axiom in ChatGPT. Explore 74 capabilities across 18 disciplines.
"""

def make_explainer(dest: Path) -> dict:
    cases = examples()
    assert len(cases) == 4 and cases[0]["verified"] and cases[3]["verified"]
    assert abs(cases[1]["result"]["var"] - .03245) < 1e-10
    assert "11,215.08" in SLIDES[1][2] and "3.245" in SLIDES[2][2]
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg required to render the original Axiom explainer")
    font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    if not font.is_file():
        raise RuntimeError("System font unavailable on build runner; no fallback video will be published")
    dest.parent.mkdir(parents=True, exist_ok=True)
    filters = ["drawbox=x=0:y=0:w=iw:h=9:color=0x76e8cb:t=fill"]
    with tempfile.TemporaryDirectory(prefix="axiom-video-") as work:
        base = Path(work)
        for i, (title, description, result) in enumerate(SLIDES):
            for line, y, font_size, color, name in (
                (title, 105, 47, "white", "title"),
                (description, 229, 25, "0xbed0de", "description"),
                (result, 316, 33, "0x76e8cb", "result"),
            ):
                label = base / f"{i}-{name}.txt"
                label.write_text(line, encoding="utf-8")
                filters.append(
                    f"drawtext=fontfile={font}:textfile={label}:fontsize={font_size}:"
                    f"fontcolor={color}:x=70:y={y}:enable='between(t,{i*4},{(i+1)*4-0.01})'"
                )
        args=[
            ffmpeg,"-hide_banner","-loglevel","error","-y","-f","lavfi",
            "-i","color=c=0x0b1725:s=960x540:r=10:d=24",
            "-vf",",".join(filters),"-c:v","libx264","-preset","ultrafast",
            "-crf","24","-threads","1","-pix_fmt","yuv420p",
            "-t","24","-movflags","+faststart",
            "-metadata","title=MUSITU Axiom - Recorded Quantitative Results",
            "-metadata","creation_time=2026-11-21T00:00:00Z",
            str(dest)
        ]
        subprocess.run(args,check=True,capture_output=True,timeout=150)
    captions=dest.with_suffix(".vtt")
    captions.write_text(CAPTIONS,encoding="utf-8")
    return {"sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
            "video_bytes":dest.stat().st_size,"captions":captions.name}

if __name__=="__main__":
    print(make_explainer(Path("axiom-explainer.mp4")))
