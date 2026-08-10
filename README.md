# Zara's Mediterranean Kitchen — design concept

A single-page website concept for [Zara's Mediterranean Kitchen](https://www.zarasmediterraneankitchen.com/)
(415 Rayford Rd, Spring, TX), built as a demonstration of what a modern site with online
ordering could look like for a local restaurant.

**This is an unaffiliated design concept.** It is not operated by, endorsed by, or connected
to the restaurant. Orders placed through the cart are not received by anyone — checkout
summarizes the order and shows the restaurant's real phone number for a pickup call.

## What's here

`index.html` — the entire site. One self-contained file, no build step, no dependencies.

- 212 menu items across 11 categories, tab-filtered — 164 with photography
- Every food category and Sides & Extras are fully illustrated. The 48 items without a
  photo are all Beverages, which render a branded tile rather than an empty slot
- Working cart: add, adjust quantity, remove, subtotal + 8.25% tax, persists across reloads
- All imagery embedded as data URIs, so the page renders offline
- Light / dark / system theming, responsive to phone width, reduced-motion respected

## Running it

Open `index.html` in any browser. That's it.

## Editing it

**Never edit `index.html` directly.** It is ~5 MB of inline base64 and is a build
artifact. Edit the source instead:

```
src/zaras.orig.html     the real source — small, references images by URL
src/img/                downloaded photography (gitignored, ~43 MB)
src/img-ai/             generated dish photography (committed, ~3 MB)
scripts/fetch_images.py downloads src/img/ from the restaurant's site
scripts/build.py        inlines every image and writes index.html
```

`src/img-ai/` is committed rather than gitignored because, unlike `src/img/`, it
cannot be re-fetched from anywhere — losing it would lose the images. Its files are
referenced by the `zara-ai-` filename prefix, which `build.py` resolves against this
directory and `fetch_images.py` skips.

Workflow:

```bash
python scripts/fetch_images.py   # only if src/img/ is missing
python scripts/build.py          # regenerates index.html
git add -A && git commit -m "..." && git push
```

GitHub Pages redeploys about a minute after the push.

Requires Python with Pillow (`pip install pillow`) and `curl` on PATH.

## Credit

Menu content, photography, and branding belong to Zara's Mediterranean Kitchen.
