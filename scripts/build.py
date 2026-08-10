"""Build index.html from src/zaras.orig.html by inlining every image.

The deployed index.html is ~3.7 MB of inline base64 and must never be edited by
hand. Edit src/zaras.orig.html instead, then run:

    python scripts/build.py

Requires Pillow (pip install pillow) and src/img/ populated by fetch_images.py.

Tunable via env vars: MAXPX (longest edge, default 560), MAXKB (per-image
ceiling, default 90).
"""
import os
import re
import io
import json
import base64
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "zaras.orig.html")
IMG = os.path.join(ROOT, "src", "img")
# Generated dish photography for items the restaurant has no photo of. Unlike
# src/img/ this is committed, since it cannot be re-fetched from their server.
IMG_AI = os.path.join(ROOT, "src", "img-ai")
OUT = os.path.join(ROOT, "index.html")
BASE = "https://www.zarasmediterraneankitchen.com/uploads/1/3/0/1/130157008/"

MAXPX = int(os.environ.get("MAXPX", "560"))
MAXKB = int(os.environ.get("MAXKB", "90"))

src = open(SRC, encoding="utf-8").read()

names = set(re.findall(r'\bi:"([^"]+)"', src))
names.update(
    re.findall(re.escape(BASE) + r"([A-Za-z0-9_\-./]+\.(?:png|jpg|jpeg))", src)
)
names = sorted(n for n in names if n)


def encode(path, name):
    im = Image.open(path)

    # The logo keeps its alpha channel; photos are flattened and go to JPEG.
    if "logo" in name.lower():
        im = im.convert("RGBA")
        im.thumbnail((420, 420), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        im = bg
    else:
        im = im.convert("RGB")

    im.thumbnail((MAXPX, MAXPX), Image.LANCZOS)
    for q in (72, 62, 52, 44, 36):
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=q, optimize=True, progressive=True)
        data = buf.getvalue()
        if len(data) <= MAXKB * 1000:
            break
    return "data:image/jpeg;base64," + base64.b64encode(data).decode()


mapping = {}
missing = []
for n in names:
    flat = n.replace("/", "__")
    p = os.path.join(IMG_AI if n.startswith("zara-ai-") else IMG, flat)
    if os.path.exists(p):
        mapping[n] = encode(p, n)
    else:
        missing.append(n)

if missing:
    print("WARNING: %d images missing from src/img — run scripts/fetch_images.py"
          % len(missing))
    for m in missing[:10]:
        print("  ", m)

print("encoded: %d   payload: %.2f MB"
      % (len(mapping), sum(len(v) for v in mapping.values()) / 1024 / 1024))

# 1) literal URLs in markup and CSS become data URIs
for n, uri in mapping.items():
    src = src.replace(BASE + n, uri)

# 2) template-literal lookups:  ${B}${it.i}  ->  ${IMGSRC(it.i)}
src, n_tpl = re.subn(r"\$\{B\}\$\{([^}]+)\}", r"${IMGSRC(\1)}", src)

# 3) swap the base-URL constant for the lookup table and resolver
decl = 'const B = "%s";' % BASE
assert decl in src, "base constant not found in source"
src = src.replace(
    decl,
    "const IMGMAP = " + json.dumps(mapping, separators=(",", ":")) + ";\n"
    'function IMGSRC(n){ return (n && IMGMAP[n]) || ""; }',
    1,
)

open(OUT, "w", encoding="utf-8").write(src)
print("template sites rewritten:", n_tpl)
print("remaining external refs:", src.count(BASE))
print("wrote %s (%.2f MB)" % (OUT, os.path.getsize(OUT) / 1024 / 1024))
