#!/usr/bin/env python3
"""Compare original KaScada 1.0.7 vs BLOODSKY main-menu button pixels.

Both screenshots MUST come from the same emulator/API/density/locale within one
session. Brand title and removed licensing status are intentionally excluded.
This proves only the six main-menu controls, not complete UI visual parity.
"""
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

if len(sys.argv) != 6:
    raise SystemExit("Usage: compare_visual.py original.png original.xml bloodsky.png bloodsky.xml report-directory")

original_png, original_xml, modified_png, modified_xml = map(Path, sys.argv[1:5])
out = Path(sys.argv[5])
out.mkdir(parents=True, exist_ok=True)
IDs = ("bGoToCanvas", "button3", "button4", "btnExport", "btnImport", "button2")
pattern = re.compile(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]")

def find_bounds(path):
    root = ET.parse(path).getroot()
    nodes = {}
    for n in root.iter("node"):
        rid = n.get("resource-id", "").rsplit("/", 1)[-1]
        if rid in IDs:
            m = pattern.fullmatch(n.get("bounds", ""))
            if not m:
                raise ValueError(f"Bad bounds for {rid} in {path}")
            bounds = tuple(map(int, m.groups()))
            if bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
                raise ValueError(f"Empty bounds for {rid}")
            nodes[rid] = (bounds, n.get("text", ""))
    if set(nodes) != set(IDs):
        raise ValueError(f"Missing menu items in {path}: {set(IDs)-set(nodes)}")
    return nodes

left = Image.open(original_png).convert("RGB")
right = Image.open(modified_png).convert("RGB")
if left.size != right.size:
    raise SystemExit(f"FAIL screenshot size mismatch: {left.size} != {right.size}")
orig_nodes, new_nodes = find_bounds(original_xml), find_bounds(modified_xml)
diff_image = Image.new("RGB", left.size)
reports = []
for rid in IDs:
    a, original_text = orig_nodes[rid]
    b, modified_text = new_nodes[rid]
    if a != b:
        reports.append(dict(button=rid, bounds_original=a, bounds_modified=b, error="bounds changed"))
        continue
    if original_text.casefold() != modified_text.casefold():
        reports.append(dict(button=rid, label_original=original_text, label_modified=modified_text, error="label changed"))
        continue
    before = left.crop(a)
    after = right.crop(b)
    diff = ImageChops.difference(before, after)
    avg = sum(ImageStat.Stat(diff).mean) / 3
    peak = diff.convert("L").point(lambda x: 255 if x > 30 else 0)
    percent = sum(peak.histogram()[1:]) / 255 / (diff.width * diff.height)
    diff_image.paste(diff, a)
    reports.append(dict(button=rid, average_channel_difference=round(avg, 3), fraction_pixels_large_diff=round(percent, 4), bounds=a))

diff_image.save(out / "menu-buttons-diff.png")
(out / "visual-report.json").write_text(json.dumps({"screensize":left.size, "buttons":reports}, indent=2), encoding="utf-8")
bad = [x for x in reports if "error" in x or x["average_channel_difference"] > 15 or x["fraction_pixels_large_diff"] > 0.16]
if bad:
    raise SystemExit(f"FAIL original-vs-BLOODSKY pixel mismatch on {len(bad)}/6 menu controls, see visual-report.json")
print("PASS all six main-menu controls have visually matching bounds/text/pixels (excluding branding and license footer)")
