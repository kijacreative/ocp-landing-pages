#!/usr/bin/env python3
"""Builds the Shop Small 2026 business features from tools/shop-small-features.json.

  python3 tools/build-shop-small-features.py "<path to the Shop Small 2026 uploads folder>"

Writes:
  smallbusinesssaturday/features/img/      cropped photos and logo tiles for the posts
  smallbusinesssaturday/features/posts/    one 1080x1350 post per business, numbered in feature order
  smallbusinesssaturday/features/carousel/ cover slides for the two carousels and the closing slide
  smallbusinesssaturday/features/shop-small-slideshow.mp4   every slide as one 4:5 video
  emails/img/sbs/                          email-sized photos and logos
  emails/shop-small-features.html          the Friday, Nov 27 feature email
  tools/shop-small-features.html           the layout page the posts are rendered from

Pass --no-render to skip Chrome and ffmpeg (images and email only).
"""
import html
import json
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SITE = "https://lp.oakcliffpilates.com"
E = html.escape

FEAT = os.path.join(ROOT, "smallbusinesssaturday", "features")
DIRS = {k: os.path.join(FEAT, k) for k in ("img", "posts", "carousel")}
EMAIL_IMG = os.path.join(ROOT, "emails", "img", "sbs")


def load():
    with open(os.path.join(ROOT, "tools", "shop-small-features.json")) as f:
        data = json.load(f)
    n = 0
    for g in data["groups"]:
        for b in g["businesses"]:
            n += 1
            b["n"] = n
            b["group"] = g["title"]
    return data


def find(src, slug, kind):
    for f in os.listdir(src):
        if f.startswith(f"{slug}-{kind}."):
            return os.path.join(src, f)
    raise SystemExit(f"Missing {kind} for {slug} in {src}")


def flatten(im, bg=(255, 255, 255)):
    im = ImageOps.exif_transpose(im).convert("RGBA")
    base = Image.new("RGBA", im.size, bg + (255,))
    base.alpha_composite(im)
    return base.convert("RGB")


def crop(im, w, h, fx, fy):
    """Cover-crop to w x h, keeping the point (fx, fy) as central as the edges allow."""
    sw, sh = im.size
    scale = max(w / sw, h / sh)
    nw, nh = round(sw * scale), round(sh * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = min(max(round(nw * fx - w / 2), 0), nw - w)
    top = min(max(round(nh * fy - h / 2), 0), nh - h)
    return im.crop((left, top, left + w, top + h))


def logo_tile(path, size):
    """Square logo tile. Full-bleed square artwork fills it; anything else sits on white with room around it."""
    raw = ImageOps.exif_transpose(Image.open(path))
    w, h = raw.size
    rgba = raw.convert("RGBA")
    corners = [rgba.getpixel(p) for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))]
    opaque = all(c[3] > 250 for c in corners)
    whiteish = all(min(c[:3]) > 235 for c in corners)
    if 0.9 <= w / h <= 1.1 and opaque and not whiteish:
        return crop(flatten(raw), size, size, 0.5, 0.5)
    im = flatten(raw)
    # Trim plain white margins so small marks don't float in a sea of white.
    if whiteish or not opaque:
        bbox = ImageOps.invert(im.convert("L")).point(lambda v: 255 if v > 12 else 0).getbbox()
        if bbox:
            im = im.crop(bbox)
    pad = round(size * 0.14)
    im.thumbnail((size - 2 * pad, size - 2 * pad), Image.LANCZOS)
    tile = Image.new("RGB", (size, size), "white")
    tile.paste(im, ((size - im.width) // 2, (size - im.height) // 2))
    return tile


def build_images(data, src):
    for d in list(DIRS.values()) + [EMAIL_IMG]:
        os.makedirs(d, exist_ok=True)
    for g in data["groups"]:
        for b in g["businesses"]:
            s = b["slug"]
            photo = flatten(Image.open(find(src, s, "photo")))
            if b.get("contain"):
                # Whole image on a solid band, for ads and illustrations a wide crop would cut apart.
                wide = Image.new("RGB", (1080, 640), b["contain"])
                fit = photo.copy()
                fit.thumbnail((1080, 640), Image.LANCZOS)
                wide.paste(fit, ((1080 - fit.width) // 2, (640 - fit.height) // 2))
            else:
                wide = crop(photo, 1080, 640, b["fx"], b["fy"])
            wide.save(os.path.join(DIRS["img"], f"{s}-wide.jpg"), quality=86, optimize=True, progressive=True)
            crop(photo, 480, 600, b["fx"], b["fy"]).save(os.path.join(EMAIL_IMG, f"{s}-photo.jpg"), quality=80, optimize=True, progressive=True)
            lp = find(src, s, "logo")
            logo_tile(lp, 400).save(os.path.join(DIRS["img"], f"{s}-logo.png"), optimize=True)
            logo_tile(lp, 112).save(os.path.join(EMAIL_IMG, f"{s}-logo.jpg"), quality=88, optimize=True)
            print("images:", s)


# ---------- Social posts ----------

POST_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{--black:#0B0B0B;--gold:#C9A24A;--cream:#F4EFE6;--muted:#3A3733}
html,body{background:#333;font-family:Montserrat,Arial,sans-serif}
.board{display:none;position:relative;width:1080px;height:1350px;overflow:hidden;background:var(--cream);color:var(--black)}
.board.on{display:block}
.bar{position:absolute;left:0;right:0;top:0;height:96px;background:var(--black);display:flex;align-items:center;justify-content:space-between;padding:0 48px;color:var(--gold);font:700 22px/1 Montserrat;letter-spacing:.22em;text-transform:uppercase}
.bar .l{display:flex;align-items:center;gap:16px}
.bar img{width:56px;height:56px}
.photo{position:absolute;left:0;top:96px;width:1080px;height:640px;object-fit:cover;display:block}
.logo{position:absolute;left:56px;top:636px;width:208px;height:208px;background:#fff;border:4px solid var(--black)}
.logo img{width:100%;height:100%;display:block}
.who{position:absolute;left:296px;right:56px;top:756px;display:flex;flex-direction:column;gap:10px}
.name{font:700 52px/.9 Khand;text-transform:uppercase}
.where{font:700 22px/1.3 Montserrat;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.copy{position:absolute;left:56px;right:56px;top:880px;bottom:150px;display:flex;flex-direction:column;justify-content:center;gap:18px}
.headline{font:700 104px/.86 Khand;text-transform:uppercase;letter-spacing:-.01em}
.details{font:500 30px/1.45 Montserrat;color:#1F1D1A}
.chips{position:absolute;left:56px;right:56px;bottom:52px;display:flex;flex-wrap:wrap;gap:14px;align-items:center}
.chip{font:700 22px/1 Montserrat;letter-spacing:.12em;text-transform:uppercase;padding:20px 22px;border:3px solid var(--black);border-radius:2px;white-space:nowrap}
.chip.code{background:var(--black);color:var(--gold)}
.chip.code b{color:var(--cream);letter-spacing:.06em;text-transform:none;font-size:26px}
.num{position:absolute;right:48px;top:756px;font:700 28px/1 Khand;color:var(--muted)}

.dark{background:var(--black);color:var(--cream)}
.dark .eyebrow{font:700 26px/1.2 Montserrat;letter-spacing:.24em;text-transform:uppercase;color:var(--gold)}
.cover .in{position:absolute;inset:96px 72px 96px;display:flex;flex-direction:column;gap:34px}
.cover h1{font:700 150px/.85 Khand;text-transform:uppercase;letter-spacing:-.01em}
.cover h1 span{color:var(--gold)}
.cover .part{font:700 30px/1.3 Montserrat;color:var(--cream)}
.cover ul{list-style:none;display:flex;flex-wrap:wrap;gap:12px 14px;margin-top:6px}
.cover li{font:700 24px/1 Montserrat;padding:14px 16px;border:2px solid rgba(201,162,74,.55);border-radius:2px;color:var(--cream)}
.cover .foot{position:absolute;left:72px;right:72px;bottom:72px;display:flex;justify-content:space-between;align-items:center;font:700 24px/1 Montserrat;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
.cover .foot .l{display:flex;align-items:center;gap:16px;color:var(--cream)}
.cover .foot img{width:64px;height:64px}
.outro .in{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px;text-align:center;padding:0 90px}
.outro img{width:200px;height:200px}
.outro h1{font:700 140px/.85 Khand;text-transform:uppercase}
.outro h1 span{color:var(--gold)}
.outro p{font:500 34px/1.5 Montserrat;color:#E4DDD0}
.outro p b{color:var(--cream)}
"""

FIT_JS = """
document.querySelectorAll('.board.biz').forEach(function (b) {});
function fit(board) {
  var box = board.querySelector('.copy'); if (!box) return;
  var chips = board.querySelector('.chips');
  box.style.bottom = (1350 - chips.offsetTop + 28) + 'px';
  var h = box.querySelector('.headline'), d = box.querySelector('.details');
  var hs = 104, ds = 30;
  function over() { return box.scrollHeight > box.clientHeight + 1; }
  while (over() && hs > 60) { hs -= 4; h.style.fontSize = hs + 'px'; }
  while (over() && ds > 22) { ds -= 1; d.style.fontSize = ds + 'px'; }
  var n = board.querySelector('.name'), ns = 52;
  var who = board.querySelector('.who');
  while (who && who.getBoundingClientRect().bottom > 870 && ns > 34) { ns -= 2; n.style.fontSize = ns + 'px'; }
}
var id = (location.hash || '#cover-all').slice(1);
var el = document.getElementById(id);
el.classList.add('on');
document.fonts.ready.then(function () { fit(el); document.title = 'ready'; });
"""


def nowrap_hyphens(text):
    """Escape, and keep hyphenated words like T-shirts from splitting at the hyphen."""
    return " ".join(f'<span style="white-space:nowrap">{E(w)}</span>' if "-" in w else E(w) for w in text.split(" "))


def post_board(b, total):
    chips = []
    if b["code"]:
        chips.append(f'<span class="chip code">Code <b>{E(b["code"])}</b></span>')
    chips.append(f'<span class="chip">{E(b["valid"])}</span>')
    chips.append(f'<span class="chip">{E(b["redeem"])}</span>')
    return f"""
<section class="board biz" id="{b['slug']}">
  <div class="bar"><span class="l"><img src="../img/OCP-Logo-128.png" alt="">Shop small with OCP</span><span>Sat, Nov 28</span></div>
  <img class="photo" src="../smallbusinesssaturday/features/img/{b['slug']}-wide.jpg" alt="">
  <div class="logo"><img src="../smallbusinesssaturday/features/img/{b['slug']}-logo.png" alt=""></div>
  <div class="who"><p class="name">{E(b['name'])}</p><p class="where">{E(b['area'])} · @{E(b['handle'])}</p></div>
  <div class="copy"><p class="headline">{nowrap_hyphens(b['headline'])}</p><p class="details">{E(b['details'])}</p></div>
  <div class="chips">{''.join(chips)}</div>
</section>"""


def cover_board(cid, part, names, total):
    lis = "".join(f"<li>{E(n)}</li>" for n in names)
    return f"""
<section class="board dark cover" id="{cid}">
  <div class="in">
    <p class="eyebrow">Small Business Saturday · Nov 28</p>
    <h1>Shop small<br><span>this weekend.</span></h1>
    <p class="part">{E(part)}</p>
    <ul>{lis}</ul>
  </div>
  <div class="foot"><span class="l"><img src="../img/OCP-Logo-128.png" alt="">@oakcliffpilates</span><span>Swipe for every deal</span></div>
</section>"""


def outro_board():
    return """
<section class="board dark outro" id="outro">
  <div class="in">
    <img src="../img/OCP-Logo-128.png" alt="">
    <h1>Shop small.<br><span>Show up big.</span></h1>
    <p>Hit these spots Friday through Monday.<br><b>Tag @oakcliffpilates</b> when you go.</p>
  </div>
</section>"""


def build_posts_page(data):
    bs = [b for g in data["groups"] for b in g["businesses"]]
    total = len(bs)
    g1 = data["groups"][:2]
    g2 = data["groups"][2:]
    p1 = [b["name"] for g in g1 for b in g["businesses"]]
    p2 = [b["name"] for g in g2 for b in g["businesses"]]
    boards = [
        cover_board("cover-all", f"{total} Dallas small businesses. Real deals, Friday through Cyber Monday.", [b["name"] for b in bs], total),
        cover_board("cover-1", "Part 1 of 2: " + ", ".join(g["title"] for g in g1), p1, total),
        cover_board("cover-2", "Part 2 of 2: " + ", ".join(g["title"] for g in g2), p2, total),
        outro_board(),
    ] + [post_board(b, total) for b in bs]
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>render</title>
<!-- Generated by tools/build-shop-small-features.py. Edit tools/shop-small-features.json, not this file. Open with #slug. -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Khand:wght@700&family=Montserrat:wght@500;700&display=block">
<style>{POST_CSS}</style></head><body>
{''.join(boards)}
<script>{FIT_JS}</script>
</body></html>
"""
    path = os.path.join(ROOT, "tools", "shop-small-features.html")
    with open(path, "w") as f:
        f.write(page)
    return path, bs


def render(page, bs, data):
    tmp = tempfile.mkdtemp()
    jobs = [("cover-all", DIRS["carousel"], "00-cover-all"), ("cover-1", DIRS["carousel"], "part-1-cover"),
            ("cover-2", DIRS["carousel"], "part-2-cover"), ("outro", DIRS["carousel"], "zz-closing")]
    jobs += [(b["slug"], DIRS["posts"], f"{b['n']:02d}-{b['slug']}") for b in bs]
    for anchor, outdir, name in jobs:
        png = os.path.join(tmp, name + ".png")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                        "--window-size=1080,1350", "--virtual-time-budget=8000", f"--screenshot={png}",
                        f"file://{page}#{anchor}"], check=True, capture_output=True)
        Image.open(png).convert("RGB").save(os.path.join(outdir, name + ".jpg"), quality=90, optimize=True, progressive=True)
        print("rendered:", name)

    # Slideshow: cover, every business, closing slide. 3 seconds each, quick crossfades.
    frames = [os.path.join(DIRS["carousel"], "00-cover-all.jpg")]
    frames += [os.path.join(DIRS["posts"], f"{b['n']:02d}-{b['slug']}.jpg") for b in bs]
    frames += [os.path.join(DIRS["carousel"], "zz-closing.jpg")]
    hold, fade = 3.0, 0.4
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    for f in frames:
        cmd += ["-loop", "1", "-t", str(hold + fade), "-i", f]
    chain, prev = [], "0:v"
    for i in range(1, len(frames)):
        out = f"v{i}"
        chain.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={fade}:offset={i * hold:.2f}[{out}]")
        prev = out
    chain.append(f"[{prev}]format=yuv420p,fps=30[out]")
    cmd += ["-filter_complex", ";".join(chain), "-map", "[out]", "-c:v", "libx264", "-crf", "22", "-preset", "medium",
            "-movflags", "+faststart", os.path.join(FEAT, "shop-small-slideshow.mp4")]
    subprocess.run(cmd, check=True)
    print("rendered: shop-small-slideshow.mp4")


# ---------- Email ----------

F_BODY = "font-family:'Montserrat',Arial,Helvetica,sans-serif"
F_DISP = "font-family:'Khand','Arial Narrow',Impact,Arial,sans-serif;font-weight:700;text-transform:uppercase"


def email_card(b):
    img = f"{SITE}/emails/img/sbs/{b['slug']}"
    code = (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:12px"><tr><td bgcolor="#0B0B0B" style="background:#0B0B0B;padding:8px 12px;{F_BODY};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#C9A24A">Code <span style="color:#F4EFE6;letter-spacing:.04em;text-transform:none;font-size:14px">{E(b["code"])}</span></td></tr></table>'
            if b["code"] else "")
    addr = f" · {E(b['address'])}" if b["address"] else ""
    return f"""
<tr><td class="px" style="padding:0 40px 28px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFFFFF" style="background:#FFFFFF;border:2px solid #0B0B0B"><tr>
<td class="stack" width="220" valign="top" style="width:220px;padding:0"><a href="{E(b['url'])}"><img class="ph" src="{img}-photo.jpg" width="220" height="275" alt="{E(b['name'])}" style="display:block;width:220px;height:275px;border:0"></a></td>
<td class="stack cardtxt" valign="top" style="padding:20px 22px">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td valign="middle" style="padding-right:12px"><img src="{img}-logo.jpg" width="48" height="48" alt="" style="display:block;width:48px;height:48px;border:1px solid #D9D2C5"></td><td valign="middle" style="{F_BODY};font-size:15px;line-height:19px;font-weight:700;color:#0B0B0B">{E(b['name'])}<br><span style="font-size:12px;font-weight:500;color:#55514B">{E(b['area'])}{addr}</span></td></tr></table>
<p style="margin:14px 0 0;{F_DISP};font-size:30px;line-height:28px;color:#0B0B0B">{E(b['headline'])}</p>
<p style="margin:8px 0 0;{F_BODY};font-size:14px;line-height:21px;color:#2A2825">{E(b['details'])}</p>{code}
<p style="margin:12px 0 0;{F_BODY};font-size:12px;line-height:18px;font-weight:700;color:#55514B">{E(b['valid'])} · {E(b['redeem'])}</p>
<p style="margin:12px 0 0;{F_BODY};font-size:14px;line-height:20px;font-weight:700"><a href="{E(b['url'])}" style="color:#0B0B0B">Visit {E(b['name'])}</a> &nbsp;·&nbsp; <a href="https://instagram.com/{E(b['handle'])}" style="color:#0B0B0B">@{E(b['handle'])}</a></p>
</td></tr></table></td></tr>"""


def build_email(data, ghl=False):
    """ghl=True writes the HighLevel version: {{contact.first_name}} greeting and {{unsubscribe_link}}."""
    greet = (f'<p style="margin:20px 0 0;{F_BODY};font-size:17px;line-height:27px;color:#F4EFE6">Hi {{{{contact.first_name}}}},</p>' if ghl else "")
    unsub = "{{unsubscribe_link}}" if ghl else "{{unsubscribe}}"
    total = sum(len(g["businesses"]) for g in data["groups"])
    sections = []
    for g in data["groups"]:
        sections.append(f'<tr><td class="px" style="padding:12px 40px 18px"><p style="margin:0;{F_DISP};font-size:40px;line-height:38px;color:#0B0B0B">{E(g["title"])}</p><div style="width:64px;height:4px;background:#C9A24A;margin-top:10px;font-size:0;line-height:0">&nbsp;</div></td></tr>')
        sections += [email_card(b) for b in g["businesses"]]
    page = f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light only">
<meta name="supported-color-schemes" content="light only">
<title>Shop small this weekend: {total} Dallas deals from our neighbors</title>
<!-- Generated by tools/build-shop-small-features.py from tools/shop-small-features.json. Edit those, then rebuild. -->
<link href="https://fonts.googleapis.com/css2?family=Khand:wght@700&family=Montserrat:wght@500;700&display=swap" rel="stylesheet">
<style>
body{{margin:0;padding:0;background:#E9E3D8;-webkit-text-size-adjust:100%}}
table{{border-collapse:collapse}}
img{{border:0;display:block;outline:none;text-decoration:none}}
@media only screen and (max-width:620px){{
.container{{width:100%!important}}
.px{{padding-left:16px!important;padding-right:16px!important}}
.h1{{font-size:54px!important;line-height:50px!important}}
.stack{{display:block!important;width:100%!important;box-sizing:border-box}}
.ph{{width:100%!important;height:auto!important}}
.cardtxt{{padding:18px!important}}
.loc{{padding:0 0 14px!important}}
}}
</style>
</head>
<body style="margin:0;padding:0;background:#E9E3D8">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:#E9E3D8">{total} Dallas small businesses, {total} deals for Small Business Saturday. Codes inside.&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#E9E3D8"><tr><td align="center" style="padding:24px 12px">
<!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;background:#F4EFE6">

<tr><td class="px" bgcolor="#0B0B0B" style="background:#0B0B0B;padding:18px 40px;border-bottom:1px solid #40351D"><a href="https://oakcliffpilates.com" style="text-decoration:none"><img src="{SITE}/emails/img/logo-puck-80.png" width="44" height="44" alt="Oak Cliff Pilates logo" style="display:inline-block;vertical-align:middle;width:44px;height:44px"><span style="display:inline-block;vertical-align:middle;padding-left:12px;{F_BODY};font-size:10px;line-height:14px;font-weight:700;letter-spacing:.3em;text-transform:uppercase;color:#C9A24A">Oak Cliff Pilates</span></a></td></tr>

<tr><td class="px" bgcolor="#0B0B0B" style="background:#0B0B0B;padding:32px 40px 44px">
<p style="margin:0 0 16px;{F_BODY};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:#C9A24A">Small Business Saturday · Nov 28</p>
<h1 class="h1" style="margin:0;{F_DISP};font-size:72px;line-height:64px;letter-spacing:-0.5px;color:#F4EFE6">Shop small.<br><span style="color:#C9A24A">We brought the crowd.</span></h1>
{greet}<p style="margin:{"12px" if ghl else "20px"} 0 0;{F_BODY};font-size:17px;line-height:27px;color:#F4EFE6">Tomorrow is Small Business Saturday. These are our neighbors, partners and members, and every one of them has a deal for you this weekend. Show this email or use the code, and tell them OCP sent you.</p>
</td></tr>

<tr><td height="36" style="height:36px;font-size:0;line-height:0">&nbsp;</td></tr>
{''.join(sections)}

<tr><td class="px" style="padding:8px 40px 40px;{F_BODY};font-size:12px;line-height:18px;color:#55514B">Offers are run by each business, and their terms apply. Questions about an offer go to the business. Questions about this feature: <a href="mailto:isabel@oakcliffpilates.com" style="color:#0B0B0B">isabel@oakcliffpilates.com</a>.</td></tr>

<tr><td class="px" bgcolor="#0B0B0B" style="background:#0B0B0B;padding:36px 40px">
<p style="margin:0;{F_DISP};font-size:40px;line-height:38px;color:#F4EFE6">Shop small. <span style="color:#C9A24A">Show up big.</span></p>
<p style="margin:14px 0 0;{F_BODY};font-size:16px;line-height:26px;color:#F4EFE6">Tag <a href="https://instagram.com/oakcliffpilates" style="color:#C9A24A;font-weight:700">@oakcliffpilates</a> and the shop when you go. We'll repost our favorites.</p>
</td></tr>

<tr><td class="px" bgcolor="#0B0B0B" style="background:#0B0B0B;padding:0 40px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td height="1" bgcolor="#272625" style="height:1px;font-size:0;line-height:0;background:#272625">&nbsp;</td></tr></table></td></tr>
<tr><td class="px" bgcolor="#0B0B0B" style="background:#0B0B0B;padding:26px 40px 0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td class="stack loc" valign="top" width="33%" style="padding:0 16px 0 0"><a href="https://www.google.com/maps/search/?api=1&amp;query=Oak+Cliff+Pilates+196+W+Davis+St%2C+Suite+140%2C+Dallas%2C+TX+75208" style="display:block;text-decoration:none"><div style="{F_DISP};font-size:19px;line-height:19px;color:#F4EFE6">Bishop Arts</div><div style="{F_BODY};font-size:12px;line-height:18px;color:#BDB6AA;padding-top:6px">196 W Davis St, Suite 140<br>Dallas, TX 75208</div></a></td>
<td class="stack loc" valign="top" width="33%" style="padding:0 16px 0 0"><a href="https://www.google.com/maps/search/?api=1&amp;query=Oak+Cliff+Pilates+2222+McKinney+Ave+%23160%2C+Dallas%2C+TX+75201" style="display:block;text-decoration:none"><div style="{F_DISP};font-size:19px;line-height:19px;color:#F4EFE6">Uptown</div><div style="{F_BODY};font-size:12px;line-height:18px;color:#BDB6AA;padding-top:6px">2222 McKinney Ave, #160<br>Dallas, TX 75201</div></a></td>
<td class="stack loc" valign="top" width="34%" style="padding:0"><a href="https://www.google.com/maps/search/?api=1&amp;query=Oak+Cliff+Pilates+2000+Greenville+Ave%2C+Dallas%2C+TX+75206" style="display:block;text-decoration:none"><div style="{F_DISP};font-size:19px;line-height:19px;color:#F4EFE6">Lower Greenville</div><div style="{F_BODY};font-size:12px;line-height:18px;color:#BDB6AA;padding-top:6px">2000 Greenville Ave<br>Dallas, TX 75206</div></a></td>
</tr></table></td></tr>
<tr><td class="px" bgcolor="#0B0B0B" style="background:#0B0B0B;padding:26px 40px 36px;{F_BODY};font-size:12px;line-height:20px;color:#BDB6AA"><a href="https://instagram.com/oakcliffpilates" style="color:#C9A24A;font-weight:700">@oakcliffpilates</a><br>You're getting this because you're on the Oak Cliff Pilates list.<br><a href="{unsub}" style="color:#BDB6AA">Unsubscribe</a> &middot; <a href="https://oakcliffpilates.com" style="color:#BDB6AA">oakcliffpilates.com</a></td></tr>

</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr></table>
</body>
</html>
"""
    path = os.path.join(ROOT, "emails", "shop-small-features-ghl.html" if ghl else "shop-small-features.html")
    with open(path, "w") as f:
        f.write(page)
    print(f"email: {path} ({len(page.encode()) // 1024} KB)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    data = load()
    build_images(data, args[0])
    page, bs = build_posts_page(data)
    build_email(data)
    build_email(data, ghl=True)
    if "--no-render" not in sys.argv:
        render(page, bs, data)


if __name__ == "__main__":
    main()
