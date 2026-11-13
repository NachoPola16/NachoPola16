"""Re-render the static text of assets/banner.svg into the animated assets/banner.png.

The animation (the basketball play on the right) exists only as the 60 frames of banner.png;
banner.svg is the static source of everything else. This script renders banner.svg with
headless Edge/Chrome and pastes its text area (left side) over every frame, so you can
change the terminal text without redrawing the play.

Usage (from the repo root):
    python -m venv .venv && .venv/Scripts/pip install pillow
    .venv/Scripts/python tools/update_banner_text.py

Edit the text in assets/banner.svg first. Keep text left of x=845 (the court starts at x=850).
If you change which area holds text, adjust BOX below. Frame timing is 83 ms, looping forever.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "assets" / "banner.svg"
PNG = ROOT / "assets" / "banner.png"
BOX = (60, 100, 845, 382)  # left/top/right/bottom of the text area, in pixels of the 1200x420 banner
BROWSERS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
]


def find_browser():
    for path in BROWSERS:
        if Path(path).exists():
            return path
    sys.exit("No Edge/Chrome/Chromium found; edit BROWSERS in this script.")


def render_svg(out_png):
    with tempfile.TemporaryDirectory() as tmp:
        html = Path(tmp) / "r.html"
        html.write_text(
            '<html><body style="margin:0"><img src="%s" width="1200" height="420" style="display:block"></body></html>'
            % SVG.as_uri(),
            encoding="utf-8",
        )
        subprocess.run(
            [find_browser(), "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=1200,420",
             "--allow-file-access-from-files", "--screenshot=" + str(out_png), html.as_uri()],
            check=True, capture_output=True,
        )


def main():
    with tempfile.TemporaryDirectory() as tmp:
        static = Path(tmp) / "static.png"
        render_svg(static)
        region = Image.open(static).convert("RGBA").crop(BOX)
        src = Image.open(PNG)
        frames = []
        for i in range(src.n_frames):
            src.seek(i)
            frame = src.convert("RGBA").copy()
            frame.paste(region, BOX[:2])
            frames.append(frame)
        frames[0].save(PNG, save_all=True, append_images=frames[1:], duration=83, loop=0)
    print("Updated", PNG, "with", len(frames), "frames")


if __name__ == "__main__":
    main()
