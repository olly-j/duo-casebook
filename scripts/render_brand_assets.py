#!/usr/bin/env python3
"""Render CASEBOOK's neutral icon and social preview from system fonts.

Authoring-only. Requires Pillow at build time. No font files are bundled and
the public website has no image-generation or font-loading dependency.
"""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "web" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)
PAPER = "#f5f5f7"
INK = "#1d1d1f"
MUTED = "#6e6e73"
LINE = "#d7d7dc"

def font(size, bold=False):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in paths:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    raise RuntimeError("A reviewed system sans font is required; no font is downloaded")

for size in (180, 192, 512):
    im = Image.new("RGB", (size, size), PAPER)
    draw = ImageDraw.Draw(im)
    f = font(round(size * .61), bold=True)
    bbox = draw.textbbox((0, 0), "C", font=f)
    x = (size - (bbox[2] - bbox[0])) / 2 - bbox[0]
    y = (size - (bbox[3] - bbox[1])) / 2 - bbox[1] - size * .012
    draw.text((round(x), round(y)), "C", font=f, fill=INK)
    im.save(ASSETS / f"icon-{size}.png", optimize=True)

count = len(json.loads((ROOT / "web" / "catalogue.json").read_text())["products"])
canvas = Image.new("RGB", (1200, 630), "#fbfbfc")
d = ImageDraw.Draw(canvas)
d.text((84, 64), "CASEBOOK", font=font(33, bold=True), fill=INK, stroke_width=0)
d.text((82, 170), "Compare iPhone", font=font(79, bold=True), fill=INK)
d.text((82, 270), "Duo cases.", font=font(79, bold=True), fill=INK)
d.text((85, 403), "Photos, specifications and source links.", font=font(27), fill=MUTED)
d.line([(84, 525), (1116, 525)], fill=LINE, width=2)
d.text((84, 551), f"{count} SOURCE-LINKED CASE DESIGNS", font=font(20, bold=True), fill=MUTED)
canvas.save(ASSETS / "share-card.png", optimize=True)
print(f"Rendered neutral CASEBOOK icon sizes and social preview for {count} catalogue records.")
