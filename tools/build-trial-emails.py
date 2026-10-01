#!/usr/bin/env python3
"""Build the 1-Week Unlimited trial conversion emails.

Source design: Claude Design project 575a0341…, "OCP Trial Email.dc.html".
Output: emails/trial/*.html, table-based with inline styles so Gmail, Outlook
and Apple Mail all render it. Images load from lp.oakcliffpilates.com/emails/img.

    python3 tools/build-trial-emails.py              # production URLs
    ASSET_BASE=../img python3 tools/build-trial-emails.py   # local preview
"""
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "emails" / "trial"
IMG = os.environ.get("ASSET_BASE", "https://lp.oakcliffpilates.com/emails/img").rstrip("/")

# ── Offer facts (Arketa catalog, 2026-10-01) ─────────────────────────────
DAYLIGHT = "$119"          # design default; drip copy said $139, ads settled on $119
SINGLE_STUDIO = "$159"
UNLIMITED = "$209"
PACKS = [("12 classes", "$189"), ("8 classes", "$159"), ("4 classes", "$99")]  # monthly memberships

# ── Links ────────────────────────────────────────────────────────────────
SITE = "https://oakcliffpilates.com"
SCHEDULE = f"{SITE}/schedule"
CLASSES = f"{SITE}/schedule/classes"
PRICING = f"{SITE}/pricing"
UNLIMITED_URL = f"{SITE}/pricing/unlimited"
UNSUBSCRIBE = "[UNSUBSCRIBE_URL]"   # swap for the sending platform's merge tag

# ── Tokens (rgba hairlines pre-blended over black: Outlook drops rgba) ───
BLACK, CREAM, GOLD, GOLD_WARM = "#0B0B0B", "#F4EFE6", "#C9A24A", "#E9C977"
TEXT, TEXT_LIGHT, DIM, MUTED = "#C9C2B6", "#E4DDD0", "#A39C90", "#8A837A"
RULE_GOLD, RULE_SOFT, RULE_GOLD_STRONG = "#40351D", "#272625", "#7D6631"
GOLD_TINT, CARD = "#1A1710", "#111110"
ACID = "#E8D44C"
PAPER, INK, BRONZE = "#FBF8F2", "#1A1918", "#6E5320"
FD = "Khand,'Arial Narrow',Arial,sans-serif"
FB = "Montserrat,'Helvetica Neue',Helvetica,Arial,sans-serif"

PX_D, PX_M = 42, 26        # side gutter: clamp(22px,7cqi,44px) at 600 / 375


def clamp(lo, cqi, hi, width):
    return round(max(lo, min(hi, cqi * width / 100)))


class Mobile:
    """Collects per-element mobile overrides into one @media block."""

    def __init__(self):
        self.rules = {}

    def cls(self, css):
        name = "m%d" % (len(self.rules) + 1)
        for k, v in self.rules.items():
            if v == css:
                return k
        self.rules[name] = css
        return name

    def css(self):
        return "\n".join(f"  .{k}{{{v}}}" for k, v in self.rules.items())


M = Mobile()


def fluid(lo, cqi, hi, lh=None):
    """Desktop size inline, mobile size as a class. Returns (style, class)."""
    d, m = clamp(lo, cqi, hi, 600), clamp(lo, cqi, hi, 375)
    style = f"font-size:{d}px;"
    cls = M.cls(f"font-size:{m}px!important") if m != d else ""
    return style, cls


def esc(s):
    return html.escape(s, quote=False)


# ── Building blocks ──────────────────────────────────────────────────────

def row(inner, pt=0, pb=0, pt_m=None, pb_m=None, extra="", bg=None):
    cls = ["px"]
    if pt_m is not None and pt_m != pt:
        cls.append(M.cls(f"padding-top:{pt_m}px!important"))
    if pb_m is not None and pb_m != pb:
        cls.append(M.cls(f"padding-bottom:{pb_m}px!important"))
    bgattr = f' bgcolor="{bg}"' if bg else ""
    bgcss = f"background:{bg};" if bg else ""
    return (f'<tr><td class="{" ".join(cls)}"{bgattr} style="{bgcss}padding:{pt}px {PX_D}px {pb}px;{extra}">'
            f"{inner}</td></tr>\n")


def vpad(lo, cqi, hi):
    return clamp(lo, cqi, hi, 600), clamp(lo, cqi, hi, 375)


def eyebrow(text, color=GOLD, mb=0, ls=".3em"):
    return (f'<div style="font-family:{FB};font-size:11px;line-height:1.4;font-weight:600;letter-spacing:{ls};'
            f'text-transform:uppercase;color:{color};margin:0 0 {mb}px">{text}</div>')


def display(text, lo, cqi, hi, lh=".88", tag="h1", color=CREAM, mb=0, ls="-.015em", weight=700):
    s, c = fluid(lo, cqi, hi)
    cattr = f' class="{c}"' if c else ""
    return (f'<{tag}{cattr} style="margin:0 0 {mb}px;font-family:{FD};{s}line-height:{lh};font-weight:{weight};'
            f'letter-spacing:{ls};text-transform:uppercase;color:{color}">{text}</{tag}>')


def p(text, size=16, color=TEXT, mb=18, lh="1.62", weight=400, font=FB):
    return (f'<p style="margin:0 0 {mb}px;font-family:{font};font-size:{size}px;line-height:{lh};'
            f'font-weight:{weight};color:{color}">{text}</p>')


def strong(text, color=CREAM):
    return f'<strong style="color:{color};font-weight:700">{text}</strong>'


def gold(text):
    return f'<span style="color:{GOLD}">{text}</span>'


def button(text, href, variant="primary", mt=0):
    if variant == "primary":
        bg, fg, bd = GOLD, BLACK, GOLD
    else:  # outline
        bg, fg, bd = BLACK, CREAM, GOLD
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:{mt}px">'
            f'<tr><td bgcolor="{bg}" style="background:{bg};border:1px solid {bd};border-radius:2px">'
            f'<a href="{href}" style="display:inline-block;padding:19px 28px 18px;font-family:{FD};font-size:17px;'
            f'line-height:1;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:{fg};'
            f'text-decoration:none">{text}</a></td></tr></table>')


def header(tag):
    return (f'<tr><td class="px" style="padding:20px {PX_D}px;border-bottom:1px solid {RULE_GOLD}">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td style="vertical-align:middle"><a href="{SITE}" style="text-decoration:none">'
            f'<img src="{IMG}/logo-puck-80.png" width="40" height="40" alt="Oak Cliff Pilates" '
            f'style="display:inline-block;vertical-align:middle;border:0;width:40px;height:40px">'
            f'<span style="display:inline-block;vertical-align:middle;padding-left:12px;font-family:{FB};'
            f'font-size:11px;line-height:1;font-weight:600;letter-spacing:.3em;text-transform:uppercase;'
            f'color:{CREAM}">Oak Cliff Pilates</span></a></td>'
            f'<td align="right" style="vertical-align:middle;font-family:{FB};font-size:10px;line-height:1;'
            f'font-weight:600;letter-spacing:.18em;text-transform:uppercase;color:{GOLD}">{tag}</td>'
            f"</tr></table></td></tr>\n")


def locations():
    studios = [("Bishop Arts", "196 W Davis St"), ("Uptown", "2222 McKinney Ave"),
               ("Lower Greenville", "2000 Greenville Ave")]
    cells = "".join(
        f'<td class="stack loc" valign="top" style="padding:0 32px 0 0">'
        f'<div style="font-family:{FD};font-size:18px;line-height:1;font-weight:700;text-transform:uppercase;'
        f'color:{CREAM};white-space:nowrap">{n}</div>'
        f'<div style="font-family:{FB};font-size:13px;line-height:1.4;color:{DIM};padding-top:4px;'
        f'white-space:nowrap">{a}</div></td>' for n, a in studios)
    return (f'<tr><td class="px" style="padding:24px {PX_D}px;border-top:1px solid {RULE_GOLD}">'
            f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>{cells}</tr></table>'
            f"</td></tr>\n")


def spacer(d, m=None):
    cls = f' class="{M.cls(f"height:{m}px!important")}"' if m is not None and m != d else ""
    return f'<tr><td{cls} height="{d}" style="height:{d}px;font-size:0;line-height:0">&nbsp;</td></tr>\n'


def footer():
    return (f'<tr><td class="px" style="padding:0 {PX_D}px 28px;font-family:{FB};font-size:11px;line-height:1.5;'
            f'color:{MUTED}">Oak Cliff Pilates · Dallas, TX · '
            f'<a href="{UNSUBSCRIBE}" style="color:{DIM}">Unsubscribe</a></td></tr>\n')


def rule(color=RULE_GOLD):
    return f'<div style="border-top:1px solid {color};font-size:0;line-height:0">&nbsp;</div>'


def numbered(items):
    """Gold-numbered prep list, hairline between rows."""
    out = []
    for i, body in enumerate(items, 1):
        last = i == len(items)
        bb = f"border-bottom:1px solid {RULE_GOLD};" if last else ""
        out.append(
            f'<tr><td valign="top" width="44" style="padding:16px 0;border-top:1px solid {RULE_GOLD};{bb}'
            f'font-family:{FD};font-size:22px;line-height:1;font-weight:700;color:{GOLD}">{i:02d}</td>'
            f'<td valign="top" style="padding:16px 0;border-top:1px solid {RULE_GOLD};{bb}">{body}</td></tr>')
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
            + "".join(out) + "</table>")


def ladder(big=38, price_big=52, row_name=24, sub=True):
    """Unlimited on top with weight, then the 12/8/4 memberships."""
    top = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
           f'<td bgcolor="{GOLD_TINT}" style="background:{GOLD_TINT};border:1px solid {GOLD};border-radius:2px;padding:22px 20px">'
           f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
           f'<td valign="bottom"><div style="font-family:{FD};font-size:{big}px;line-height:.85;font-weight:700;'
           f'text-transform:uppercase;color:{CREAM}">Unlimited</div>'
           f'<div style="font-family:{FB};font-size:14px;line-height:1.4;color:{TEXT};padding-top:6px">All three studios, all hours</div></td>'
           f'<td valign="bottom" align="right" style="white-space:nowrap"><span style="font-family:{FD};font-size:{price_big}px;'
           f'line-height:.85;font-weight:700;color:{GOLD}">{UNLIMITED}</span><span style="font-family:{FB};font-size:13px;'
           f'font-weight:600;color:{TEXT}">/mo</span></td></tr></table></td></tr></table>')
    rows = []
    for i, (name, price) in enumerate(PACKS):
        bb = f"border-bottom:1px solid {RULE_SOFT};" if i < len(PACKS) - 1 else ""
        subline = (f'<div style="font-family:{FB};font-size:13px;line-height:1.4;color:{DIM};padding-top:4px">'
                   f"Every month, any studio</div>") if sub else ""
        rows.append(
            f'<tr><td valign="middle" style="padding:16px 20px;{bb}"><div style="font-family:{FD};font-size:{row_name}px;'
            f'line-height:.9;font-weight:700;text-transform:uppercase;color:{CREAM}">{name}</div>{subline}</td>'
            f'<td valign="middle" align="right" style="padding:16px 20px;{bb}white-space:nowrap">'
            f'<span style="font-family:{FD};font-size:26px;line-height:1;font-weight:700;color:{GOLD}">{price}</span>'
            f'<span style="font-family:{FB};font-size:12px;font-weight:600;color:{TEXT}">/mo</span></td></tr>')
    return top + ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
                  + "".join(rows) + "</table>")


def page(meta, body, bg=BLACK):
    pre = esc(meta["preheader"]) if meta["preheader"] else ""
    pad = "&#847;&zwnj;&nbsp;" * 60
    return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<meta name="robots" content="noindex">
<title>{esc(meta["subjects"][0])}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<link href="https://fonts.googleapis.com/css2?family=Khand:wght@600;700&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  body{{margin:0;padding:0;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}}
  table{{border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0}}
  img{{border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}}
  a[x-apple-data-detectors]{{color:inherit!important;text-decoration:none!important}}
  .code{{-webkit-user-select:all;user-select:all}}
  @media only screen and (max-width:620px){{
  .container{{width:100%!important}}
  .px{{padding-left:{PX_M}px!important;padding-right:{PX_M}px!important}}
  .stack{{display:block!important;width:100%!important;box-sizing:border-box}}
  .loc{{padding:0 0 14px!important}}
  .fluid{{width:100%!important;height:auto!important}}
  .gap-m{{padding:0 0 4px!important}}
  .card-m{{padding:0 0 12px!important}}
{M.css()}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:{bg}" bgcolor="{bg}">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:{bg}">{pre}{pad}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{bg}" style="background:{bg}">
<tr><td align="center" style="padding:0">
<!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="{bg}" style="width:600px;max-width:600px;background:{bg}">
{body}</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr>
</table>
</body>
</html>
"""


# ── Emails ───────────────────────────────────────────────────────────────

def e1():
    t1, t1m = vpad(32, 9, 56)
    gap, gapm = vpad(32, 9, 48)
    prep = numbered([
        p(f"{strong('Arrive 10 minutes early. Not five.')} Tell the front desk it's your first time and someone will "
          "set your springs and footbar and walk you through the machine before class starts.", 15, mb=0, lh="1.6"),
        p(f"{strong('Grip socks are required')} and we sell them for 25 dollars if you don't have a pair. Bring your "
          "own if you do. Worth knowing now rather than at the desk.", 15, mb=12, lh="1.6")
        + f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td bgcolor="{GOLD_TINT}" '
          f'style="background:{GOLD_TINT};border:1px solid {GOLD};border-radius:2px;padding:14px 16px">'
          f'<span style="font-family:{FD};font-size:40px;line-height:.9;font-weight:700;color:{GOLD};vertical-align:baseline">$25</span>'
          f'<span style="font-family:{FB};font-size:11px;line-height:1.4;font-weight:600;letter-spacing:.18em;'
          f'text-transform:uppercase;color:{CREAM};padding-left:12px;vertical-align:baseline">Grip socks · at the desk</span>'
          f"</td></tr></table>",
        p(f"{strong('Wear something fitted.')} Loose shorts and baggy tees don't work on a reformer. You'll spend the "
          "hour fighting your clothes.", 15, mb=0, lh="1.6"),
        p(strong("Don't eat in the hour before.") + f" Trust us.", 15, mb=0, lh="1.6"),
    ])
    return (
        header("1-Week Unlimited")
        + row(eyebrow("Good news first:", mb=20)
              + display(f"Your week doesn't start until your {gold('first class.')}", 44, 11.5, 74, mb=20)
              + p("Buy today, come Thursday, and your seven days begin Thursday. Nothing is ticking.", 17, TEXT_LIGHT, 20)
              + p("The catch is the obvious one. Book it now, or this quietly becomes a thing you meant to do.", 16, mb=24)
              + button("Book your first class", SCHEDULE), t1, 0, t1m)
        + spacer(gap, gapm)
        + f'<tr><td style="padding:0"><img src="{IMG}/trial-first-class-setup.jpg" width="600" height="375" class="fluid" '
          f'alt="Trainer setting up a member on the reformer" style="display:block;width:600px;height:auto;max-width:100%"></td></tr>\n'
        + row(display("Before you come in", 34, 0, 34, ".9", "h2", mb=18, ls="-.01em") + prep, gap, 0, gapm)
        + row(eyebrow("Which class first?", mb=14)
              + p(f'<strong style="font-family:{FD};font-size:24px;line-height:1;font-weight:700;text-transform:uppercase;'
                  f'color:{CREAM}">OG Reformer Pilates.</strong> Every trainer teaches it, it\'s the foundation, and it\'s where '
                  "everyone starts. Take this one first even if something else looks more interesting.", mb=14)
              + p("One last thing. There are no mirrors in any of our studios. Nobody is watching you, nobody is checking "
                  "their own form, and the lights are low. Whatever you're nervous about, that room is the easiest "
                  "possible place to be new.", mb=0), gap, 0, gapm)
        + spacer(gap, gapm) + locations() + footer()
    )


def e2():
    t, tm = vpad(36, 10, 64)
    return (
        header("1-Week Unlimited")
        + row(display("Three days since you bought your week and you haven't been in.", 40, 10, 64, ".9", mb=20)
              + p(strong("Nothing's lost.", GOLD) + f" The clock doesn't start until your first class, so none of your "
                  "seven days have burned.", 17, TEXT_LIGHT, 20)
              + p("But this is where most people stall, waiting for a week that feels less busy. That week doesn't arrive.", mb=20)
              + p("So pick the class that's easiest to get to, not the one that's ideal.", mb=24)
              + button("See this week's schedule", SCHEDULE)
              + p(f"{gold('250+')} classes a week. Three studios. One of them fits.", 24, CREAM, 20, "1", 700, FD)
                .replace("margin:0 0 20px", "margin:32px 0 20px;text-transform:uppercase")
              + rule(RULE_SOFT)
              + p("If something's actually in the way, reply and tell us what it is. Someone reads these.", 15, DIM, 0, "1.6")
                .replace("margin:0 0 0px", "margin:20px 0 0"), t, t, tm, tm)
        + footer()
    )


def plain(paras, link_text, link_href, closing):
    t, tm = vpad(28, 8, 48)
    body = "".join(p(x, 15, INK, 16, "1.65") for x in paras)
    body += p(f'<a href="{link_href}" style="color:{BRONZE};text-decoration:underline">{link_text}</a>', 15, INK, 16, "1.65", 600)
    body += "".join(p(x, 15, INK, 16, "1.65") for x in closing)
    body += p(f'Oak Cliff Pilates<br><span style="font-size:13px;color:#5E5A53">Bishop Arts · Uptown · Lower Greenville</span>',
              15, INK, 0, "1.5").replace("margin:0 0 0px", "margin:24px 0 0")
    body += p(f'<a href="{UNSUBSCRIBE}" style="color:#6E6A63">Unsubscribe</a>', 11, "#6E6A63", 0, "1.5") \
        .replace("margin:0 0 0px", "margin:32px 0 0")
    return row(body, t, t, tm, tm)


def e3():
    return plain(
        ["Ten days. Still no rush, your week starts whenever you walk in.",
         "But at this point it's worth asking what the actual blocker is, because it's rarely the Pilates.",
         "<strong>Timing?</strong> Most of the schedule is early morning and evening, but there are 53 classes a week "
         "between 10am and 4pm if your free hours are the middle of the day.",
         "<strong>Distance?</strong> Three studios. Bishop Arts, Uptown, Lower Greenville. One is likely closer than "
         "the one you had in mind.",
         "<strong>Nerves?</strong> Genuinely the most common one. No mirrors, low lights, and the front desk will set "
         "your machine up for you. Nobody in that room is looking at you."],
        "Book one class", SCHEDULE, ["Or reply and tell us what's in the way."])


def e4():
    t, tm = vpad(32, 9, 56)
    m4, m4m = vpad(28, 8, 44)
    s4, c4 = fluid(170, 46, 250)
    sa, ca = fluid(32, 8, 44)
    bar = "".join(f'<td width="28" height="6" bgcolor="{GOLD if i == 0 else RULE_GOLD}" style="font-size:0;line-height:0">&nbsp;</td>'
                  + ('<td width="6" style="font-size:0">&nbsp;</td>' if i < 3 else "") for i in range(4))
    four = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="border-top:1px solid {RULE_GOLD};border-bottom:1px solid {RULE_GOLD}"><tr>'
            f'<td class="stack" valign="middle" width="170" style="padding:20px 28px 20px 0">'
            f'<div class="{c4}" style="font-family:{FD};{s4}line-height:.78;font-weight:700;letter-spacing:-.04em;color:{GOLD}">4</div></td>'
            f'<td class="stack" valign="middle" style="padding:20px 0">'
            + eyebrow("Your seven days start now.", mb=12)
            + f'<div class="{ca}" style="font-family:{FD};{sa}line-height:.9;font-weight:700;text-transform:uppercase;color:{CREAM};margin-bottom:12px">Aim for four classes.</div>'
            + f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>{bar}</tr></table>'
            + "</td></tr></table>")
    sore = (p(strong("You'll probably be sore somewhere unexpected.") + f" That's normal and it's the point. It usually "
              "shows up 24 to 36 hours out.", 15, mb=10, lh="1.6")
            + p("Don't wait for it to pass before going again. A second class inside 48 hours is what turns this from a "
                "thing you tried into a thing you do.", 15, mb=0, lh="1.6"))
    trainer = p(f"{strong('Take a different trainer.')} There are 50+ of them and they teach the same format completely "
                "differently. The one you click with is the reason people stay for years, and you won't find them by "
                "repeating the same class.", 15, mb=0, lh="1.6")
    g, gm = vpad(32, 9, 48)
    return (
        header("Day 1 of 7")
        + row(display("You did the hardest one.", 40, 10, 62, ".9", mb=18)
              + p("Everything after this is easier, because the difficult part was never the Pilates. It was walking in.", mb=0), t, 0, tm)
        + row(four, m4, 0, m4m)
        + row(p(strong("That's the number.") + f" People who take four in their trial week stay. Book the rest now, while "
                "you still feel like it, and move them later if you need to.", mb=18)
              + button("Book the rest of your week", SCHEDULE), *vpad(24, 7, 36)[:1], 0, vpad(24, 7, 36)[1])
        + row(eyebrow("Two things about tomorrow", mb=16)
              + f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">'
                f'<tr><td style="padding:16px 0;border-top:1px solid {RULE_SOFT}">{sore}</td></tr>'
                f'<tr><td style="padding:16px 0;border-top:1px solid {RULE_SOFT}">{trainer}</td></tr></table>', g, 0, gm)
        + spacer(24) + locations() + footer()
    )


def e5():
    t, tm = vpad(28, 8, 48)
    g, gm = vpad(32, 9, 48)
    s, sm = vpad(24, 7, 36)

    def photo(src, alt, cap, pad):
        return (f'<td class="stack {pad}" valign="top" width="298" style="padding:0">'
                f'<img src="{IMG}/{src}" width="298" height="373" class="fluid" alt="{alt}" '
                f'style="display:block;width:298px;height:auto;max-width:100%">'
                f'<div style="padding:10px 14px;font-family:{FB};font-size:10px;line-height:1;font-weight:600;'
                f'letter-spacing:.18em;text-transform:uppercase;color:{DIM}">{cap}</div></td>')

    photos = (f'<tr><td style="padding:0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
              + photo("trial-park-2016.jpg", "Pilates in the Park at Kidd Springs, 2016", "2016 · Kidd Springs Park", "gap-m")
              + '<td class="stack" width="4" style="font-size:0;line-height:0">&nbsp;</td>'
              + photo("trial-lower-greenville.jpg", "A class on the reformers at Lower Greenville", "Now · Lower Greenville", "")
              + "</tr></table></td></tr>\n")
    stats = "".join(
        f'<td valign="top" width="33%" style="padding:18px 0"><div class="{M.cls("font-size:34px!important")}" '
        f'style="font-family:{FD};font-size:44px;line-height:.85;font-weight:700;color:{GOLD}">{n}</div>'
        f'<div style="font-family:{FB};font-size:10px;line-height:1.3;font-weight:600;letter-spacing:.18em;'
        f'text-transform:uppercase;color:{TEXT};padding-top:6px">{l}</div></td>'
        for n, l in [("1,000", "members now"), ("50+", "trainers"), ("2025", "Best of Dallas")])
    chips = "".join(
        f'<a href="{CLASSES}" style="display:inline-block;margin:0 4px 8px 0;padding:9px 14px;border:1px solid {RULE_GOLD_STRONG};'
        f'border-radius:999px;font-family:{FB};font-size:12px;line-height:1;font-weight:600;letter-spacing:.06em;'
        f'color:{CREAM};text-decoration:none">{esc(c).replace("&amp;", "&amp;")}</a>'
        for c in ["Classical AF", "Arms, Ass & Abs", "Jumpboard", "Tabata Pilates", "Restorative Pilates",
                  "OG Reformer Amped", "Strength & Flexibility"])
    return (
        header("Day 3 of 7") + photos
        + row(display(f"In {gold('2016')} this was free mat classes at Kidd Springs Park.", 40, 10.5, 66, mb=18)
              + p("A speaker in the grass and whoever showed up.", 17, TEXT_LIGHT)
              + p("Bishop Arts came in 2021. Uptown in 2024. Lower Greenville last year, built from scratch with 14 "
                  "reformers, a private training room and a podcast studio in the back.")
              + p("What didn't change is the room. Lights down, music up, and no mirrors anywhere in any of the three "
                  "buildings. That last one is deliberate. Mirrors turn a class into a performance, and we'd rather you "
                  "paid attention to how something feels than how it looks.", mb=0), t, 0, tm)
        + row(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
              f'style="border-top:1px solid {RULE_GOLD};border-bottom:1px solid {RULE_GOLD}"><tr>{stats}</tr></table>'
              + p("Same energy as the park.", 22, CREAM, 0, "1", 700, FD).replace("margin:0 0 0px", "margin:16px 0 0;text-transform:uppercase"),
              s, 0, sm)
        + row(display(f"Four days left. {gold('Spend them on something new.')}", 30, 8, 40, ".9", "h2", mb=16, ls="0")
              + p(f"{strong('Take a second studio.')} Your week works at all three and they each feel different.", mb=16)
              + p(strong("Take a format you haven't:"), mb=12)
              + f"<div>{chips}</div>"
              + button("Book something different", SCHEDULE, mt=16), g, 0, gm)
        + spacer(g, gm) + locations() + footer()
    )


def e6():
    t, tm = vpad(32, 9, 56)
    b, bm = vpad(24, 7, 36)
    sc, cc = fluid(64, 18, 112)
    band = (f'<tr><td class="px {M.cls(f"padding-top:{bm}px!important;padding-bottom:{bm}px!important")}" bgcolor="{ACID}" '
            f'style="background:{ACID};padding:{b}px {PX_D}px">'
            + eyebrow("Use code UPGRADE25 for 25 dollars off.", BLACK, 10).replace("font-weight:600", "font-weight:700")
            + f'<div class="code {cc}" style="font-family:{FD};{sc}line-height:.82;font-weight:700;letter-spacing:-.02em;color:{BLACK}">UPGRADE25</div>'
            + "</td></tr>\n")

    def card(name, price, copy, cls):
        return (f'<td class="stack {cls}" valign="top" width="50%" style="padding:0 6px 0 0">'
                f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE_GOLD};border-radius:8px;padding:18px">'
                f'<div style="font-family:{FD};font-size:22px;line-height:.9;font-weight:700;text-transform:uppercase;color:{CREAM}">{name}</div>'
                f'<div style="padding:8px 0 10px"><span style="font-family:{FD};font-size:26px;line-height:.9;font-weight:700;color:{GOLD}">{price}</span>'
                f'<span style="font-family:{FB};font-size:12px;font-weight:600;color:{TEXT}"> a month</span></div>'
                + p(copy, 14, mb=0, lh="1.55") + "</td></tr></table></td>")

    cards = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
             + card("Daylight Unlimited", DAYLIGHT, "Unlimited weekday classes between 10am and 4pm, all three studios. "
                    "If your week was mostly midday, this is the one.", "card-m")
             + card("Single Studio Unlimited", SINGLE_STUDIO, "Unlimited at one location. If you went to the same studio "
                    "every time, this is cheaper for exactly what you already did.", "")
             + "</tr></table>").replace('style="padding:0 6px 0 0"', 'style="padding:0 6px 0 0"', 1)
    # second card gets the gap on its left instead of its right
    cards = cards[::-1].replace('"0 0 6px 0:gniddap"', '"0 0 0 6px:gniddap"', 1)[::-1]
    m2, m2m = vpad(36, 10, 56)
    t2, t2m = vpad(28, 8, 40)
    g, gm = vpad(32, 9, 48)
    return (
        header("Day 5 of 7")
        + row(display("Two days left on your week.", 44, 11.5, 74, mb=16)
              + p("If you want to keep going, here's the part where we make it easy.", mb=0), t, b, tm, bm)
        + band
        + row(ladder() + button("Claim 25 off", UNLIMITED_URL, mt=20), b, 0, bm)
        + spacer(m2, m2m)
        + row(display("Not going to be here four times a week?", 28, 7.5, 38, ".9", "h2", mb=18, ls="0")
              + cards
              + p("No contract. Cancel whenever. [CONFIRM CANCEL POLICY]", 14, mb=10, lh="1.6").replace("margin:0 0 10px", "margin:18px 0 10px")
              + p("Code's good through [DATE].", 14, CREAM, 0, "1.6", 600), t2, 0, t2m, extra=f"border-top:1px solid {RULE_GOLD};")
        + spacer(g, gm) + locations() + footer()
    )


def e7():
    t, tm = vpad(36, 10, 64)
    g, gm = vpad(32, 9, 48)
    tt, ttm = vpad(24, 7, 32)
    return (
        header("Day 7 of 7")
        + row(display(f"Last day of {gold('your week.')}", 52, 14, 92, ".86", mb=18)
              + p("Get one more class in if you can. Finish it properly.", 17, TEXT_LIGHT, 18)
              + button("Today's schedule", SCHEDULE), t, 0, tm)
        + spacer(g, gm)
        + row(rule()
              + p(f"Then, whenever you're ready: {strong('UPGRADE25')} takes 25 dollars off Unlimited at {UNLIMITED} a month, "
                  "or a 4, 8 or 12-class membership. Good through [DATE], so tonight isn't actually the deadline for deciding.", mb=16)
                .replace("margin:0 0 16px", f"margin:{tt}px 0 16px")
              + button("Join with 25 off", UNLIMITED_URL, "outline")
              + p(f"Daylight Unlimited at {DAYLIGHT} and Single Studio at {SINGLE_STUDIO} are both there too if the full "
                  "unlimited is more than you need.", 14, DIM, 0, "1.6").replace("margin:0 0 0px", "margin:16px 0 0"), 0, 0)
        + spacer(g, gm) + footer()
    )


def e8a():
    t, tm = vpad(36, 10, 64)
    l, lm = vpad(24, 7, 32)
    g, gm = vpad(32, 9, 48)
    return (
        header("UPGRADE25")
        + row(display("Your week ended two days ago.", 44, 11.5, 74, mb=18)
              + p(f"You got into a rhythm, and {strong('rhythms are the whole thing.')} People who let one lapse here usually "
                  "come back three months later and start from nothing.")
              + p(f"{strong('UPGRADE25 is good until [DATE].')} 25 dollars off Unlimited at {UNLIMITED} a month, or a 4, 8 or "
                  "12-class membership.", mb=0), t, 0, tm)
        + row(ladder(34, 46, 22, sub=False)
              + button("Pick up where you left off", PRICING, mt=20)
              + p(f"Daylight Unlimited at {DAYLIGHT} and Single Studio at {SINGLE_STUDIO} are both options if you want "
                  "something narrower.", 14, DIM, 0, "1.6").replace("margin:0 0 0px", "margin:20px 0 0"), l, 0, lm)
        + spacer(g, gm) + locations() + footer()
    )


def e8b():
    return plain(
        ["Your week's over and you didn't get much out of it. We'd rather ask why than pretend otherwise.",
         "Usually it's one of three things.",
         f"<strong>The times didn't work.</strong> Most of the schedule is early morning and evening. If your free hours "
         f"are the middle of the day, Daylight Unlimited is {DAYLIGHT} a month for 53 weekday classes between 10 and 4.",
         f"<strong>It's across town.</strong> Three studios. Bishop Arts, Uptown, Lower Greenville. One is likely closer "
         f"than the one you tried. Single Studio Unlimited is {SINGLE_STUDIO} a month for one location.",
         "<strong>It wasn't for you.</strong> Completely fair, and you won't hear from us about it again.",
         "If it's one of the first two, UPGRADE25 is good until [DATE] and works on class memberships as well as "
         "unlimited, so a 4-class month is a low-commitment way back in."],
        "See the options", PRICING, ["If it's the third, reply and say so. We'll leave you alone."])


EMAILS = [
    dict(id="e1", file="01-on-purchase", phase=1, trigger="On purchase", build=e1, bg=BLACK,
         subjects=["Your week hasn't started yet", "You're in. Here's how it works.", "Book your first class"],
         preheader="The clock doesn't start until you walk in. Here's what to know first."),
    dict(id="e2", file="02-purchase-plus-3", phase=1, trigger="Purchase +3 days, no visit", build=e2, bg=BLACK,
         subjects=["Still not booked", "Your week is waiting on you", "Pick a day"],
         preheader="Nothing has started. Nothing is wasted. Just pick one."),
    dict(id="e3", file="03-purchase-plus-10", phase=1, trigger="Purchase +10 days, no visit", build=e3, bg=PAPER,
         subjects=["Still here whenever you are", "Ten days", "No expiry, just a reminder"], preheader=""),
    dict(id="e4", file="04-first-class-evening", phase=2, trigger="Evening of first class", build=e4, bg=BLACK,
         subjects=["One down", "You survived. Book the next one.", "That was the hard part"],
         preheader="Your week is running now. Aim for four."),
    dict(id="e5", file="05-trial-day-3", phase=2, trigger="Trial day 3", build=e5, bg=BLACK,
         subjects=["It started in a park", "Why there aren't any mirrors", "The part that isn't the Pilates"],
         preheader="Ten years, three studios, and a reason for all of it."),
    dict(id="e6", file="06-trial-day-5", phase=2, trigger="Trial day 5 · UPGRADE25", build=e6, bg=BLACK,
         subjects=["Two days left, and 25 dollars off", "UPGRADE25", "Don't let this end on [DAY]"],
         preheader="Your week ends [DAY]. Here's what happens next if you want it to."),
    dict(id="e7", file="07-trial-day-7", phase=2, trigger="Trial day 7, final day · UPGRADE25", build=e7, bg=BLACK,
         subjects=["Last day", "Your week ends tonight", "One more class, then decide"],
         preheader="25 dollars off with UPGRADE25, good for five more days."),
    dict(id="e8a", file="08a-trial-day-9-engaged", phase=2, trigger="Trial day 9 · 3+ classes · UPGRADE25", build=e8a, bg=BLACK,
         subjects=["Two days without it", "UPGRADE25 expires [DATE]", "You had a good week"], preheader=""),
    dict(id="e8b", file="08b-trial-day-9-light", phase=2, trigger="Trial day 9 · 2 or fewer · UPGRADE25", build=e8b, bg=PAPER,
         subjects=["That didn't really work, did it", "Honest question"], preheader=""),
]


def main():
    global M
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for e in EMAILS:
        M = Mobile()
        body = e["build"]()
        (OUT / f"{e['file']}.html").write_text(page(e, body, e["bg"]))
        manifest.append({k: e[k] for k in ("id", "file", "phase", "trigger", "subjects", "preheader")})
    (OUT / "emails.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(EMAILS)} emails to {OUT.relative_to(ROOT)} (images from {IMG})")


if __name__ == "__main__":
    main()
