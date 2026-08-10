"""Download every image referenced by src/zaras.orig.html into src/img/.

Safe to re-run: files already present are skipped. Run this only if src/img/
is missing or you have added new image references to the source file.

    python scripts/fetch_images.py
"""
import os
import re
import json
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "zaras.orig.html")
OUT = os.path.join(ROOT, "src", "img")
BASE = "https://www.zarasmediterraneankitchen.com/uploads/1/3/0/1/130157008/"

os.makedirs(OUT, exist_ok=True)
src = open(SRC, encoding="utf-8").read()

names = set(re.findall(r'\bi:"([^"]+)"', src))
names.update(
    re.findall(re.escape(BASE) + r"([A-Za-z0-9_\-./]+\.(?:png|jpg|jpeg))", src)
)
names = sorted(n for n in names if n)
print("referenced:", len(names))

results = {}
for n in names:
    dest = os.path.join(OUT, n.replace("/", "__"))
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        results[n] = os.path.getsize(dest)
        continue
    r = subprocess.run(
        ["curl", "-sfL", "--max-time", "25", "-o", dest, BASE + n],
        capture_output=True,
    )
    if r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0:
        results[n] = os.path.getsize(dest)
    else:
        results[n] = 0
        if os.path.exists(dest):
            os.remove(dest)

ok = {k: v for k, v in results.items() if v}
bad = [k for k, v in results.items() if not v]
print("downloaded: %d   failed: %d   total: %.1f MB"
      % (len(ok), len(bad), sum(ok.values()) / 1024 / 1024))
for b in bad:
    print("  FAILED:", b)

json.dump(results, open(os.path.join(OUT, "_manifest.json"), "w"), indent=1)
