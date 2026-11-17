# Holiday 2026 campaigns: Lock-In and Black Friday

Source files for the [OCP Holiday Campaigns 2026 canvas](https://claude.ai/artifact/QYZCaFvUkVgqK8H85BK3RZ), plus the Black Friday and Lock-In landing page drafts. `index.html` is the live page at lp.oakcliffpilates.com/blackfriday and `media/` holds its photos. `.vercelignore` keeps everything else here (generator, canvas, drafts, this README) off the site.

| Path | What |
| --- | --- |
| `index.html` | The live /blackfriday landing page: five offers, Arketa links, countdown, FAQ. |
| `gen.py` | Writes every artboard and `canvas/project/canvas.json`. Offers, prices, dates, links and copy all live in this one file. |
| `canvas/project/` | The 75 artboards as `.dc.html` files plus `canvas.json` (layout, pages, row titles, the Arketa description notes). |
| `media/` | The resized photos and video loops uploaded to the canvas. The canvas loads them by upload id, so these are the originals to keep. |
| `landing-pages/holiday-offers-bundle.html` | The /black-friday and /lock-in pages (desktop and 390px) as one self-contained file. Open it in a browser. |
| `landing-pages/black-friday-source.html`, `lock-in-source.html` | The same two pages unpacked, readable source only. They don't render on their own. |

## Editing

1. Change the copy in `gen.py` (the `OFFERS` dictionary holds the five Black Friday offers and their Arketa links).
2. Run `python3 blackfriday/gen.py`. It rewrites the files in `canvas/project/` and keeps the published canvas's creation stamp.
3. Republish the changed `.dc.html` files (and `canvas.json` if artboards were added or removed) to the canvas.

Edits made directly on the canvas are not in these files. Pull them down before regenerating, or they get overwritten on the next publish.

## Still to fill in

- Bonus gift card valid-through date
- 10-class pack: one per person [confirm]
- Unlimited perks in its Arketa description (14-day booking, monthly guest pass) [confirm]
- Starter: does the week start at purchase or at the first class
- Gift bundle merch pickup [confirm], gift card delivery [confirm], refund policy
- Lock-In: late-cancel waiver terms, QR codes, photo for L3
- Landing pages here still show the old offers and Nov 27 to 30 dates
