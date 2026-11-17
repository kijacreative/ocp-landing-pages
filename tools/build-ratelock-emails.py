#!/usr/bin/env python3
"""Build the 2027 rate lock emails sent to all members.

Visual source: the /ratelock landing page (Anton + Archivo, orange accent).
Output: emails/ratelock/*.html, table-based with inline styles so Gmail,
Outlook and Apple Mail all render it, plus emails.json for the preview page.

    python3 tools/build-ratelock-emails.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "emails" / "ratelock"
IMG = "https://lp.oakcliffpilates.com/emails/img"

# ── Offer facts (match /ratelock) ────────────────────────────────────────
NEW_RATE = "$229"           # All-Studio Unlimited from January 1, 2027
ALL_STUDIO = "$209"
HOME_STUDIO = "$189"
COUPLES, COUPLES_NEW = "$359", "$399"
PREPAY = [("3 months", "$599", "About $200 a month", "$649"),     # last item: price from January 1
          ("6 months", "$1,159", "About $193 a month", "$1,249"),
          ("12 months", "$2,199", "About $183 a month", "$2,459")]
DEADLINE = "December 31"
# Monthly class memberships: today's price, then January 1 (+$10).
CLASS_PLANS = [("4 classes", "OCP Lite", "$99", "$109"), ("8 classes", "Perfect Balance", "$159", "$169"),
               ("12 classes", "The Regular", "$189", "$199")]

# ── Links ────────────────────────────────────────────────────────────────
PAGE = "https://lp.oakcliffpilates.com/ratelock"
PLANS, PREPAY_URL = f"{PAGE}#plans", f"{PAGE}#prepay"
CHECKOUT = "https://app.arketa.co/oakcliffpilates/pricing/checkout/"
ALL_STUDIO_URL = CHECKOUT + "NYH9dctoUSiY9llrTpDz"
PREPAY_12_URL = CHECKOUT + "BrarwgDVt2JrdSuJ5MJG"
PREPAY_URLS = [CHECKOUT + "S1dYzKADWZfO5g3WCSja", CHECKOUT + "P1oBISrBIaTZXf0eO0Jb", PREPAY_12_URL]  # 3, 6, 12 months
PACK_10_EACH = 29                # 10-class pack: $290, so $29 a class (drop-in is $30)
INTRO_CODE = "UPGRADE25"        # intro offer clients: $25 off their first month
UPGRADE_PAGE = "https://lp.oakcliffpilates.com/upgrade25"   # landing page for intro offer clients
HOME_STUDIO_URLS = [("Bishop Arts", CHECKOUT + "FPy3uCkkxQ2H1sRaTITB"), ("Uptown", CHECKOUT + "MrXrNPz1NlRuBympPyyG"),
                    ("Lower Greenville", CHECKOUT + "KuXjLTvAX8g7G1weK6Hb")]
COUPLES_URL = CHECKOUT + "mRf1xuUpq5Y8Cc46uWHA"
CONTACT = "kiel@oakcliffpilates.com"
NAME = "{{clientFirstName}}"      # Arketa handlebar
UNSUBSCRIBE = "{{unsubscribe}}"   # unconfirmed in Arketa: check a test send

# ── Tokens ───────────────────────────────────────────────────────────────
INK, CREAM, SUB, ACCENT = "#121110", "#F4EFE6", "#D9D2C5", "#FF6A2B"
RULE, MUTED, CARD_RULE = "#2E2B28", "#4A4640", "#D9D2C5"
FD = "Anton,Impact,'Arial Narrow',sans-serif"
FB = "Archivo,'Helvetica Neue',Helvetica,Arial,sans-serif"
PX = 40


# ── Building blocks ──────────────────────────────────────────────────────

def row(inner, pt=0, pb=0, bg=None, extra=""):
    bga = f' bgcolor="{bg}"' if bg else ""
    bgc = f"background:{bg};" if bg else ""
    return f'<tr><td class="px"{bga} style="{bgc}padding:{pt}px {PX}px {pb}px;{extra}">{inner}</td></tr>\n'


def spacer(h):
    return f'<tr><td height="{h}" style="height:{h}px;font-size:0;line-height:0">&nbsp;</td></tr>\n'


def eyebrow(text, color=ACCENT, mb=16):
    return (f'<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:700;letter-spacing:.14em;'
            f'text-transform:uppercase;color:{color};margin:0 0 {mb}px">{text}</div>')


def display(text, size, msize, color=CREAM, mb=20, tag="h1", lh=".92"):
    return (f'<{tag} class="d{msize}" style="margin:0 0 {mb}px;font-family:{FD};font-size:{size}px;line-height:{lh};'
            f'font-weight:400;letter-spacing:.01em;text-transform:uppercase;color:{color};word-break:break-word">{text}</{tag}>')


def p(text, size=17, color=SUB, mb=18, weight=400):
    return (f'<p style="margin:0 0 {mb}px;font-family:{FB};font-size:{size}px;line-height:1.55;font-weight:{weight};'
            f'color:{color}">{text}</p>')


def strong(text, color=CREAM):
    return f'<strong style="color:{color};font-weight:700">{text}</strong>'


def button(label, href, kind="solid", mt=8):
    if kind == "solid":
        bg, fg, border = ACCENT, INK, ACCENT
    elif kind == "dark":
        bg, fg, border = INK, CREAM, INK
    else:
        bg, fg, border = "transparent", CREAM, CREAM
    bga = f' bgcolor="{bg}"' if bg != "transparent" else ""
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:{mt}px;border-collapse:separate"><tr>'
            f'<td align="center"{bga} style="background:{bg};border:1px solid {border};border-radius:999px">'
            f'<a class="btn" href="{href}" style="display:inline-block;padding:18px 32px;min-width:220px;font-family:{FB};'
            f'font-size:17px;line-height:20px;font-weight:700;letter-spacing:.02em;color:{fg};text-decoration:none;'
            f'text-align:center">{label}</a></td></tr></table>')


def photo(src, w, h, alt, href):
    """Full-bleed photo row. Width and height attributes keep Outlook from stretching it."""
    return (f'<tr><td style="padding:0;font-size:0;line-height:0"><a href="{href}">'
            f'<img src="{IMG}/{src}" width="{w}" height="{h}" alt="{alt}" '
            f'style="display:block;width:100%;max-width:{w}px;height:auto;border:0"></a></td></tr>\n')


def photo_pair(a, b, href):
    """Two portrait photos side by side, edge to edge, with a thin gap."""
    cell = lambda src, alt, pad: (f'<td width="50%" valign="top" style="padding:{pad};font-size:0;line-height:0">'
                                  f'<a href="{href}"><img src="{IMG}/{src}" width="298" height="372" alt="{alt}" '
                                  'style="display:block;width:100%;max-width:298px;height:auto;border:0"></a></td>')
    return ('<tr><td style="padding:0"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            + cell(*a, "0 2px 0 0") + cell(*b, "0 0 0 2px") + "</tr></table></td></tr>\n")


def header(pill="Members only", href=PAGE):
    return row(
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="vertical-align:middle"><a href="{href}" style="text-decoration:none">'
        f'<img src="{IMG}/ocp-logo-emails.png" width="40" height="40" alt="Oak Cliff Pilates logo" '
        'style="display:inline-block;vertical-align:middle;border:0;width:40px;height:40px">'
        f'<span style="display:inline-block;vertical-align:middle;padding-left:12px;font-family:{FD};font-size:22px;'
        f'line-height:1;letter-spacing:.04em;text-transform:uppercase;color:{CREAM}">Oak Cliff Pilates</span></a></td>'
        f'<td align="right" style="vertical-align:middle"><span class="pill" style="display:inline-block;border:1px solid {CREAM};'
        f'border-radius:999px;padding:7px 14px;font-family:{FB};font-size:11px;line-height:1;font-weight:600;'
        f'letter-spacing:.12em;text-transform:uppercase;color:{CREAM};white-space:nowrap">{pill}</span></td>'
        '</tr></table>', 22, 22, extra=f"border-bottom:1px solid {RULE};")


def footer(reason="you're an Oak Cliff Pilates member"):
    locs = "Bishop Arts &middot; Uptown &middot; Lower Greenville"
    return (row(display("Questions? Ask a real person.", 36, 30, INK, 10, "div", "1")
                + f'<a href="mailto:{CONTACT}" style="font-family:{FB};font-size:18px;line-height:1.4;font-weight:700;'
                  f'color:{INK};text-decoration:underline">{CONTACT}</a>'
                + f'<div style="padding-top:22px;font-family:{FB};font-size:12px;line-height:18px;font-weight:700;'
                  f'letter-spacing:.12em;text-transform:uppercase;color:{INK}">{locs}</div>', 44, 0, ACCENT)
            + row(f'<div style="font-family:{FB};font-size:12px;line-height:20px;color:{INK}">You\'re getting this because '
                  f'{reason}. <a href="{UNSUBSCRIBE}" style="color:{INK};text-decoration:underline">'
                  'Unsubscribe</a></div>', 18, 40, ACCENT))


def price_shift(now=ALL_STUDIO, then=NEW_RATE, label="All-Studio Unlimited"):
    """Today's rate beside the January rate."""
    cell = lambda k, v, c, strike="": (
        f'<td class="stack" valign="top" width="50%" style="padding:22px 24px;border:1px solid {RULE}">'
        f'<div style="font-family:{FB};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.12em;'
        f'text-transform:uppercase;color:{SUB};margin:0 0 8px">{k}</div>'
        f'<div style="font-family:{FD};font-size:56px;line-height:1;color:{c};{strike}">{v}</div>'
        f'<div style="font-family:{FB};font-size:14px;line-height:20px;color:{SUB};padding-top:6px">a month</div></td>')
    return (eyebrow(label, SUB, 12)
            + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            + cell("Lock it now", now, ACCENT)
            + cell("From January 1", then, CREAM)
            + "</tr></table>")


def plan_rows(light=True):
    """The two monthly plans as stacked rows (cards don't survive Outlook)."""
    bg, fg, sub, rule = ("#FFFFFF", INK, MUTED, CARD_RULE) if light else (INK, CREAM, SUB, RULE)
    plans = [
        ("All-Studio Unlimited", ALL_STUDIO, "Unlimited classes at all 3 studios. 20% off retail.", "Lock in " + ALL_STUDIO, ALL_STUDIO_URL),
        ("Home Studio Unlimited", HOME_STUDIO, "Unlimited at the studio you call home. 10% off retail.",
         "Pick your studio", PLANS),
    ]
    out = ""
    for i, (name, price, desc, cta, href) in enumerate(plans):
        hl = i == 0
        cbg, cfg, csub = (INK, CREAM, SUB) if hl and light else (bg, fg, sub)
        out += (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{cbg}" '
                f'style="background:{cbg};border:1px solid {INK if hl and light else rule};border-collapse:separate;border-radius:16px;margin:0 0 14px">'
                f'<tr><td class="card" style="padding:26px 28px">'
                f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                f'<td style="vertical-align:baseline;font-family:{FB};font-size:13px;line-height:18px;font-weight:700;'
                f'letter-spacing:.12em;text-transform:uppercase;color:{cfg}">{name}</td>'
                f'<td align="right" style="vertical-align:baseline;white-space:nowrap"><span style="font-family:{FD};'
                f'font-size:44px;line-height:1;color:{ACCENT if hl else cfg}">{price}</span>'
                f'<span style="font-family:{FB};font-size:14px;color:{csub}">/mo</span></td></tr></table>'
                f'<div style="font-family:{FB};font-size:15px;line-height:1.5;color:{csub};padding:10px 0 14px">{desc}</div>'
                f'<a href="{href}" style="font-family:{FB};font-size:15px;line-height:20px;font-weight:700;'
                f'color:{ACCENT if hl else cfg};text-decoration:underline">{cta} &rarr;</a>'
                "</td></tr></table>")
    return out


def perks(color=SUB):
    items = ["Book 14 days ahead", "A free guest pass every month",
             "Teacher, nurse and other discounts still take $10 off monthly plans"]
    return "".join(
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td width="22" valign="top" style="padding:3px 0 10px;font-family:{FB};font-size:15px;line-height:22px;'
        f'font-weight:700;color:{ACCENT}">&mdash;</td>'
        f'<td valign="top" style="padding:3px 0 10px 8px;font-family:{FB};font-size:15px;line-height:22px;color:{color}">{t}</td>'
        "</tr></table>" for t in items)


def faq(items):
    return "".join(
        f'<div style="padding:18px 0;border-top:1px solid {RULE}">'
        f'<div style="font-family:{FB};font-size:17px;line-height:1.4;font-weight:700;color:{CREAM};margin:0 0 6px">{q}</div>'
        f'<div style="font-family:{FB};font-size:15px;line-height:1.55;color:{SUB}">{a}</div></div>' for q, a in items)


def countdown(n, unit):
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td valign="bottom" class="count" style="font-family:{FD};font-size:200px;line-height:.8;color:{ACCENT};'
            f'padding-right:20px">{n}</td>'
            f'<td valign="bottom" style="padding-bottom:8px;font-family:{FD};font-size:40px;line-height:.95;'
            f'text-transform:uppercase;color:{CREAM}">{unit}</td></tr></table>')


# ── Emails ───────────────────────────────────────────────────────────────

def e1():
    return (header()
            + row(eyebrow(f"Ends {DEADLINE}, 2026")
                  + display("Prices change January 1.<br>Yours doesn't have to.", 64, 46)
                  + p(f"Hi {NAME}. On January 1, All-Studio Unlimited goes to {NEW_RATE} a month. You were here first, so you "
                      f"get first move: choose a membership before {DEADLINE} and your rate is locked through December 31, 2027.")
                  + button("Choose my membership", PLANS), 52, 0)
            + spacer(44)
            + row(price_shift()
                  + p(f"That's {strong('$240 back in your pocket')} over 2027 if you lock in All-Studio today.", 15, SUB, 0)
                  .replace("margin:0 0 0px", "margin:16px 0 0"), 0, 0)
            + spacer(48)
            + row(display("Two ways to stay unlimited", 40, 34, INK, 10, "h2", ".95")
                  + p("Every plan comes with:", 16, MUTED, 10)
                  + perks(MUTED).replace(f"color:{ACCENT}\">&mdash;", f"color:{INK}\">&mdash;")
                  + '<div style="height:18px;line-height:18px;font-size:0">&nbsp;</div>'
                  + plan_rows(), 48, 34, CREAM)
            + row(p(f"Unlimited Couples is {COUPLES} for two, and goes to {COUPLES_NEW} on January 1. "
                    f"<a href=\"{PLANS}\" style=\"color:{INK};font-weight:700\">See it on the page</a>.", 15, MUTED, 0), 0, 48, CREAM)
            + footer())


def bullets(items, color=SUB):
    return "".join(
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td width="22" valign="top" style="padding:3px 0 10px;font-family:{FB};font-size:15px;line-height:22px;'
        f'font-weight:700;color:{ACCENT}">&mdash;</td>'
        f'<td valign="top" style="padding:3px 0 10px 8px;font-family:{FB};font-size:15px;line-height:22px;color:{color}">{t}</td>'
        "</tr></table>" for t in items)


def e1_unlimited():
    return (header()
            + row(eyebrow("For All-Studio Unlimited members")
                  + display(f"Keep {ALL_STUDIO}.<br>All of 2027.", 72, 52)
                  + p(f"Hi {NAME}. You're on All-Studio Unlimited, and on January 1 it goes to {NEW_RATE} a month. Lock in "
                      f"before {DEADLINE} and you keep {ALL_STUDIO} through December 31, 2027.")
                  + button(f"Lock in {ALL_STUDIO}", ALL_STUDIO_URL), 52, 0)
            + spacer(44)
            + row(price_shift()
                  + p(f"That's {strong('$240 back in your pocket')} over 2027.", 15, SUB, 0)
                  .replace("margin:0 0 0px", "margin:16px 0 0"), 0, 0)
            + spacer(48)
            + row(eyebrow("Or skip the monthly bill", INK, 12)
                  + display("A year of unlimited for $2,199", 40, 34, INK, 14, "h2", ".95")
                  + p(f"About $183 a month, and it goes to {strong('$2,459', INK)} on January 1. That's {strong('$549 less', INK)} than "
                      f"twelve months at {NEW_RATE}. Same studios, same "
                      "perks. Teacher and nurse discounts don't apply to prepay.", 16, MUTED, 0)
                  + button("Prepay 12 months", PREPAY_12_URL, "dark", 22)
                  + p(f"<a href=\"{PREPAY_URL}\" style=\"color:{INK};font-weight:700\">3 and 6 months</a> are on the page too.",
                      14, MUTED, 0).replace("margin:0 0 0px", "margin:16px 0 0"), 44, 44, CREAM)
            + row(p(f"Mostly at one studio? Home Studio Unlimited is {HOME_STUDIO} a month at any studio. "
                    f"<a href=\"{PLANS}\" style=\"color:{CREAM};font-weight:700\">Compare plans</a>.", 15, SUB, 0), 36, 48)
            + footer())


def e1_classes():
    match = [
        ("12 classes", CLASS_PLANS[2], "Home Studio Unlimited", HOME_STUDIO, "$10 less than your January price. Unlimited at your home studio."),
        ("8 classes", CLASS_PLANS[1], "Home Studio Unlimited", HOME_STUDIO, "$20 more than your January price. Unlimited at your home studio."),
        ("4 classes", CLASS_PLANS[0], "Home Studio Unlimited", HOME_STUDIO, "$80 more than your January price. Unlimited at your home studio."),
    ]
    rows = "".join(
        f'<tr><td class="stack" valign="top" width="38%" style="padding:18px 16px 18px 0;border-top:1px solid {CARD_RULE}">'
        f'<div style="font-family:{FB};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.12em;'
        f'text-transform:uppercase;color:{MUTED};margin:0 0 4px">You have</div>'
        f'<div style="font-family:{FD};font-size:28px;line-height:1;text-transform:uppercase;color:{INK}">{have}</div>'
        f'<div style="font-family:{FB};font-size:14px;line-height:20px;color:{MUTED}">{was[2]}/mo now, {was[3]} from January 1</div></td>'
        f'<td class="stack" valign="top" style="padding:18px 0;border-top:1px solid {CARD_RULE}">'
        f'<div style="font-family:{FB};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.12em;'
        f'text-transform:uppercase;color:{ACCENT};margin:0 0 4px">Go unlimited</div>'
        f'<div style="font-family:{FD};font-size:28px;line-height:1;text-transform:uppercase;color:{INK}">{plan} &middot; {price}</div>'
        f'<div style="font-family:{FB};font-size:14px;line-height:20px;color:{MUTED};padding-top:4px">{why}</div></td></tr>'
        for have, was, plan, price, why in match)
    return (header()
            + row(eyebrow("Thinking about unlimited?")
                  + display("Ready to stop<br>counting classes?", 64, 46)
                  + p(f"Hi {NAME}. Your class membership is yours to keep, no action needed. But if you've wondered about "
                      "going unlimited, this is a good moment to try it.")
                  + p(f"Choose an unlimited plan before {DEADLINE} and its price is locked through all of 2027. All-Studio "
                      f"Unlimited goes to {NEW_RATE} on January 1.", mb=0)
                  + button("See unlimited plans", PLANS, mt=24), 52, 0)
            + spacer(48)
            + row(display("What unlimited costs you", 40, 34, INK, 8, "h2", ".95")
                  + p("Your class plan next to Home Studio Unlimited. Class memberships go up $10 a month on January 1.", 16, MUTED, 16)
                  + '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">' + rows + "</table>"
                  + button("See both plans", PLANS, "dark", 20), 44, 44, CREAM)
            + row(eyebrow("On every plan", SUB, 12) + perks(), 40, 0)
            + spacer(48)
            + footer())


def e1_couples():
    return (header()
            + row(eyebrow("For Unlimited Couples members")
                  + display("Two of you.<br>One locked rate.", 72, 52)
                  + p(f"Hi {NAME}. Unlimited Couples goes to {COUPLES_NEW} a month on January 1. Lock in before {DEADLINE} "
                      f"and the two of you keep {COUPLES} through December 31, 2027. That's about $180 each.")
                  + button(f"Lock in {COUPLES}", COUPLES_URL), 52, 0)
            + spacer(44)
            + row(price_shift(COUPLES, COUPLES_NEW, "Unlimited Couples")
                  + p(f"That's {strong('$480 back')} over 2027, split however you like.", 15, SUB, 0)
                  .replace("margin:0 0 0px", "margin:16px 0 0"), 0, 0)
            + spacer(44)
            + row(eyebrow("What you both keep", SUB, 12)
                  + bullets(["Unlimited Pilates for two at all 3 studios", "Book 14 days ahead"]), 0, 0)
            + spacer(40)
            + row(display("Train with your person", 32, 28, INK, 12, "h2", ".95")
                  + p("Same studios, same trainers, one bill. Keep it that way for 2027.", 16, MUTED, 0)
                  + button(f"Lock in {COUPLES}", COUPLES_URL, "dark", 20), 40, 44, CREAM)
            + footer())


def e2():
    return (header()
            + row(eyebrow("Which one is yours?")
                  + display(f"Pick the plan<br>that fits your week, {NAME}.", 56, 42)
                  + p(f"Same studios, same trainers. The only difference is where you train. Choose before "
                      f"{DEADLINE} and whichever you pick keeps today's price all of 2027.", mb=0), 52, 0)
            + spacer(36)
            + row(_who("You move around.", "All-Studio Unlimited", ALL_STUDIO,
                       "Bishop Arts on Monday, Uptown after work, Lower Greenville on the weekend. Unlimited at all three, "
                       "plus 20% off retail.", "Lock in " + ALL_STUDIO, ALL_STUDIO_URL, True)
                  + _who("You have a home studio.", "Home Studio Unlimited", HOME_STUDIO,
                         "Unlimited at the one you always go to. 10% off retail.",
                         "Pick your studio", PLANS), 0, 0)
            + spacer(24)
            + row(eyebrow("On every plan", SUB, 12) + perks(), 0, 0)
            + spacer(24)
            + row(button("Compare all plans", PLANS), 0, 56)
            + footer())


def _who(lead, name, price, desc, cta, href, hl=False):
    border = ACCENT if hl else RULE
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="border:1px solid {border};border-collapse:separate;border-radius:16px;margin:0 0 14px"><tr><td class="card" style="padding:26px 28px">'
            + display(lead, 34, 30, CREAM, 14, "div", ".95")
            + f'<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:700;letter-spacing:.12em;'
              f'text-transform:uppercase;color:{ACCENT if hl else SUB};margin:0 0 10px">{name} &middot; {price}/mo</div>'
            + p(desc, 15, SUB, 14)
            + f'<a href="{href}" style="font-family:{FB};font-size:15px;line-height:20px;font-weight:700;color:{CREAM};'
              f'text-decoration:underline">{cta} &rarr;</a>'
            + "</td></tr></table>")


def e3():
    cells = ""
    for i, (term, price, per, then) in enumerate(PREPAY):
        best = i == 2
        bg, fg, sub = (ACCENT, INK, INK) if best else (INK, CREAM, SUB)
        pad = "0 8px 0 0" if i == 0 else ("0 0 0 8px" if best else "0 4px")
        cells += (f'<td class="stack card-m" valign="top" width="33%" style="padding:{pad}">'
                  f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{bg}" '
                  f'style="background:{bg};border:1px solid {ACCENT if best else MUTED};border-collapse:separate;border-radius:16px"><tr>'
                  f'<td style="padding:22px 18px">'
                  f'<div style="font-family:{FB};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.12em;'
                  f'text-transform:uppercase;color:{fg};margin:0 0 8px">{term}{" &middot; Best value" if best else ""}</div>'
                  f'<div style="font-family:{FD};font-size:40px;line-height:1;color:{fg}">{price}</div>'
                  f'<div style="font-family:{FB};font-size:13px;line-height:18px;color:{sub};padding-top:6px">{per}</div>'
                  f'<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:700;color:{fg};padding-top:8px">{then} from Jan 1</div>'
                  "</td></tr></table></td>")
    return (header()
            + row(eyebrow("Pay ahead, pay less")
                  + display("Full unlimited for under $200 a month.", 60, 44)
                  + p(f"Prepay All-Studio Unlimited and every perk comes with it: all 3 studios, 20% off retail, and a guest pass "
                      f"every month. Twelve months is {strong('$549 less')} than a year at {NEW_RATE}. "
                      f"Prepay goes up on January 1 too, so today's prices end {DEADLINE}.", mb=0), 52, 0)
            + spacer(36)
            + row('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                  + cells + "</tr></table>"
                  + button("Prepay 12 months", PREPAY_12_URL, mt=24)
                  + p(f"Or <a href=\"{PREPAY_URL}\" style=\"color:{CREAM};font-weight:700\">see 3 and 6 months</a>. Prepay is "
                      "All-Studio only, and teacher and nurse discounts don't apply to it.", 14, SUB, 0)
                  .replace("margin:0 0 0px", "margin:18px 0 0"), 0, 56)
            + footer())


def e4():
    return (header()
            + row(eyebrow("The fine print, made short")
                  + display("What happens<br>if you do nothing?", 60, 44)
                  + p(f"On January 1, an unlimited membership that hasn't chosen moves to {strong(f'All-Studio Unlimited at {NEW_RATE} a month')} "
                      f"automatically. Nothing breaks, you just pay the new rate. 4, 8 and 12-class memberships stay as they are "
                      f"and go up $10 a month.")
                  + p(f"If you'd rather keep what you pay now, or switch to a plan that suits you better, choose before {DEADLINE}.", mb=0), 52, 0)
            + spacer(36)
            + row(faq([
                ("How long is my rate locked?",
                 f"Choose before December 31, 2026 and your rate holds through December 31, 2027. If rates rise again after "
                 "that, this rate isn't guaranteed."),
                ("Can I pause?", "Yes, on every plan, up to twice a year and no more than 30 days in total."),
                ("Do my teacher or nurse discounts still apply?",
                 "Yes, on monthly plans. They take $10 off per month. They don't apply to prepay."),
                ("How does the guest pass work?", "Every plan includes a free guest pass each month to bring a friend to class."),
                ("Can I switch plans later?", f"Write to {CONTACT} and a real person will sort it out."),
              ]) + button("Lock my rate", PLANS, mt=16), 0, 56)
            + footer())


def e5():
    return (header()
            + row(eyebrow(f"Ends {DEADLINE}")
                  + countdown(5, "days left<br>to lock<br>your rate")
                  + '<div style="height:28px;line-height:28px;font-size:0">&nbsp;</div>'
                  + p(f"{NAME}, after {DEADLINE} the price you pay today is gone. On January 1, All-Studio Unlimited is "
                      f"{NEW_RATE} a month, and that's where every unlimited membership that hasn't chosen lands.")
                  + p("It takes about a minute. Pick a plan, check out, done for 2027.", mb=0)
                  + button("Choose my membership", PLANS, mt=24), 52, 0)
            + spacer(48)
            + row(price_shift(), 0, 56)
            + footer())


def e6():
    return (header()
            + row(eyebrow("Last day", ACCENT)
                  + display("Tonight's<br>the night.", 84, 58, mb=22)
                  + p(f"Choose a membership before midnight and you keep today's price through all of 2027. Tomorrow, "
                      f"All-Studio Unlimited is {NEW_RATE} a month.")
                  + button("Lock my rate now", PLANS, mt=16), 52, 0)
            + spacer(44)
            + row(display("Quickest way in", 32, 28, INK, 14, "h2", ".95")
                  + p(f"Lock in All-Studio Unlimited at {ALL_STUDIO} in one tap. Prefer another plan? "
                      f"<a href=\"{PLANS}\" style=\"color:{INK};font-weight:700\">Compare them here</a>.", 16, MUTED, 0)
                  + button(f"Lock in {ALL_STUDIO}", ALL_STUDIO_URL, "dark", 20), 40, 44, CREAM)
            + row(p("Happy New Year from all of us at OCP. See you on the reformer in 2027.", 15, SUB, 0), 36, 48)
            + footer())


def e7_intro():
    """Intro offer clients who never bought a membership: UPGRADE25 plus the 2027 rate lock. Links go to
    /upgrade25 (the /ratelock page is labeled members only) or straight to an Arketa checkout."""
    studio = lambda name, url: (f'<a href="{url}" style="font-family:{FB};font-size:15px;line-height:24px;font-weight:700;'
                                f'color:{INK};text-decoration:underline;white-space:nowrap">{name} &rarr;</a>')
    home_links = " &nbsp;&middot;&nbsp; ".join(studio(n, u) for n, u in HOME_STUDIO_URLS)
    card = lambda inner, bg, border: (
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{bg}" '
        f'style="background:{bg};border:1px solid {border};border-collapse:separate;border-radius:16px;margin:0 0 14px">'
        f'<tr><td class="card" style="padding:26px 28px">{inner}</td></tr></table>')
    head = lambda name, price, fg, pc: (
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="vertical-align:baseline;font-family:{FB};font-size:13px;line-height:18px;font-weight:700;'
        f'letter-spacing:.12em;text-transform:uppercase;color:{fg}">{name}</td>'
        f'<td align="right" style="vertical-align:baseline;white-space:nowrap"><span style="font-family:{FD};'
        f'font-size:44px;line-height:1;color:{pc}">{price}</span>'
        f'<span style="font-family:{FB};font-size:14px;color:{fg}">/mo</span></td></tr></table>')
    plans = (card(head("All-Studio Unlimited", ALL_STUDIO, CREAM, ACCENT)
                  + p("Unlimited classes at all 3 studios. 20% off retail. Goes to " + NEW_RATE + " on January 1.", 15, SUB, 14)
                  .replace("margin:0 0 14px", "margin:10px 0 14px")
                  + f'<a href="{ALL_STUDIO_URL}" style="font-family:{FB};font-size:15px;line-height:20px;font-weight:700;'
                    f'color:{ACCENT};text-decoration:underline">Join at {ALL_STUDIO} &rarr;</a>', INK, INK)
             + card(head("Home Studio Unlimited", HOME_STUDIO, INK, INK)
                    + p("Unlimited at the studio you call home. 10% off retail. Pick yours:", 15, MUTED, 10)
                    .replace("margin:0 0 10px", "margin:10px 0 10px")
                    + f'<div style="line-height:28px">{home_links}</div>', "#FFFFFF", CARD_RULE))
    th = lambda v, align="left": (f'<td align="{align}" style="padding:0 0 10px;font-family:{FB};font-size:11px;line-height:14px;'
                                  f'font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:{MUTED}">{v}</td>')
    td = lambda v, style, align="right": (f'<td align="{align}" valign="baseline" style="padding:14px 0;border-top:1px solid {CARD_RULE};'
                                          f'{style}">{v}</td>')
    class_rows = "".join(
        "<tr>"
        + td(f'{n}<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:400;text-transform:none;'
             f'letter-spacing:0;color:{MUTED};padding-top:4px">${int(now[1:]) - 25} first month with {INTRO_CODE}</div>',
             f"font-family:{FD};font-size:22px;line-height:1;text-transform:uppercase;color:{INK}", "left")
        + td(now, f"font-family:{FD};font-size:34px;line-height:1;color:{INK};padding-left:12px")
        + td(then, f"font-family:{FD};font-size:22px;line-height:1;color:{MUTED};text-decoration:line-through;padding-left:16px")
        + "</tr>" for n, _, now, then in reversed(CLASS_PLANS))
    class_table = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#FFFFFF" '
                   f'style="background:#FFFFFF;border:1px solid {CARD_RULE};border-collapse:separate;border-radius:16px">'
                   f'<tr><td class="card" style="padding:26px 28px">'
                   '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                   + th("A month") + th("Now", "right") + th("Jan 1", "right") + "</tr>" + class_rows + "</table></td></tr></table>")
    return (header("Intro offer", UPGRADE_PAGE)
            + photo("trial-first-class-setup.jpg", 600, 375, "A trainer laughing with a client on the reformer", UPGRADE_PAGE)
            + row(eyebrow(f"Ends {DEADLINE}")
                  + display("$25 off.<br>Locked for 2027.", 64, 46)
                  + p(f"Hi {NAME}. You've had a taste of OCP. Here's a good reason to stay: use code {strong(INTRO_CODE)} "
                      "and your first month of membership is $25 less.")
                  + p(f"And prices go up on January 1: All-Studio Unlimited to {NEW_RATE} a month, and 4, 8 and 12-class "
                      f"memberships by {strong('$10 a month')}. Join before {DEADLINE} and you keep today's price through "
                      "December 31, 2027.", mb=0)
                  + button("Claim $25 off", UPGRADE_PAGE, mt=24), 52, 0)
            + spacer(36)
            + row('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
                  f'style="border:2px dashed {ACCENT};border-collapse:separate;border-radius:16px"><tr><td class="card" style="padding:24px 26px">'
                  + eyebrow("Your code", ACCENT, 10)
                  + f'<div style="font-family:{FD};font-size:48px;line-height:1;letter-spacing:.04em;color:{CREAM}">{INTRO_CODE}</div>'
                  + p(f"Enter it at checkout for $25 off your first month of Unlimited or a 4, 8 or 12-class membership. "
                      f"Good through {DEADLINE}.", 15, SUB, 0).replace("margin:0 0 0px", "margin:12px 0 0")
                  + "</td></tr></table>", 0, 0)
            + spacer(44)
            + row(price_shift(label="All-Studio Unlimited")
                  + p(f"That's {strong('$240')} you keep over 2027 by joining now, on top of the $25 off.", 15, SUB, 0)
                  .replace("margin:0 0 0px", "margin:16px 0 0"), 0, 0)
            + spacer(48)
            + photo_pair(("trial-lower-greenville.jpg", "A client on the reformer with her legs in the straps"),
                         ("upgrade25-window.jpg", "A client on the reformer in front of the Oak Cliff Pilates window"), UPGRADE_PAGE)
            + row(display("Two ways to go unlimited", 40, 34, INK, 10, "h2", ".95")
                  + p("Both come with:", 16, MUTED, 10)
                  + perks(MUTED).replace(f"color:{ACCENT}\">&mdash;", f"color:{INK}\">&mdash;")
                  + '<div style="height:18px;line-height:18px;font-size:0">&nbsp;</div>'
                  + plans, 48, 34, CREAM)
            + row(eyebrow("Not ready for unlimited?", INK, 10)
                  + display("4, 8 or 12 classes.<br>Up $10 in January.", 36, 30, INK, 12, "h2", ".95")
                  + p(f"Every class membership goes up $10 a month on January 1. Join before {DEADLINE} and today's price "
                      f"holds through 2027. {INTRO_CODE} takes $25 off your first month here too.", 15, MUTED, 18)
                  + class_table
                  + p(f"<a href=\"{UPGRADE_PAGE}#plans\" style=\"color:{INK};font-weight:700\">See every plan &rarr;</a>", 15, MUTED, 0)
                  .replace("margin:0 0 0px", "margin:18px 0 0"), 20, 48, CREAM)
            + footer("you tried an Oak Cliff Pilates intro offer"))

def e8_prepay_renew():
    """Current 3, 6 and 12-month prepay members: buy the next prepay at today's price, starting when theirs ends."""
    money = lambda v: int(v.replace("$", "").replace(",", ""))
    cells = ""
    for i, ((term, price, per, then), url) in enumerate(zip(PREPAY, PREPAY_URLS)):
        best = i == 2
        bg, fg, sub = (ACCENT, INK, INK) if best else (INK, CREAM, SUB)
        pad = "0 8px 0 0" if i == 0 else ("0 0 0 8px" if best else "0 4px")
        save = f"${money(then) - money(price):,}"
        cells += (f'<td class="stack card-m" valign="top" width="33%" style="padding:{pad}">'
                  f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{bg}" '
                  f'style="background:{bg};border:1px solid {ACCENT if best else MUTED};border-collapse:separate;border-radius:16px"><tr>'
                  f'<td style="padding:22px 18px">'
                  f'<div style="font-family:{FB};font-size:12px;line-height:16px;font-weight:700;letter-spacing:.12em;'
                  f'text-transform:uppercase;color:{fg};margin:0 0 8px">{term}{" &middot; Best value" if best else ""}</div>'
                  f'<div style="font-family:{FD};font-size:40px;line-height:1;color:{fg}">{price}</div>'
                  f'<div style="font-family:{FB};font-size:13px;line-height:18px;color:{sub};padding-top:6px">{per}</div>'
                  f'<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:700;color:{fg};padding-top:8px">'
                  f'{then} from Jan 1. Save {save}.</div>'
                  f'<a href="{url}" style="display:inline-block;padding-top:12px;font-family:{FB};font-size:14px;line-height:18px;'
                  f'font-weight:700;color:{fg};text-decoration:underline">Lock in {term} &rarr;</a>'
                  "</td></tr></table></td>")
    steps = [("Pick your term", f"3, 6 or 12 months, at today's price. Buy it before {DEADLINE}."),
             ("Keep training", "Nothing changes now. Your current prepay runs to its end date as usual."),
             ("It starts when yours renews", "Your new prepay picks up the day your current one ends. No gap, no overlap, no January price.")]
    step_rows = "".join(
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td width="56" valign="top" style="padding:0 0 22px;font-family:{FD};font-size:40px;line-height:1;color:{INK}">{n}</td>'
        f'<td valign="top" style="padding:2px 0 22px">'
        f'<div style="font-family:{FB};font-size:17px;line-height:24px;font-weight:700;color:{INK}">{t}</div>'
        f'<div style="font-family:{FB};font-size:15px;line-height:22px;color:{MUTED};padding-top:4px">{d}</div></td></tr></table>'
        for n, (t, d) in enumerate(steps, 1))
    return (header("Prepay members")
            + row(eyebrow(f"Ends {DEADLINE}")
                  + display("Your next prepay,<br>at this year's price.", 60, 44)
                  + p(f"Hi {NAME}. Prepay goes up on January 1. You don't have to wait for yours to run out to beat it: "
                      f"buy your next prepay before {DEADLINE} and we'll start it when your current one renews.")
                  + p("Today's price, locked in, whenever your renewal lands.", mb=0), 52, 0)
            + spacer(36)
            + row('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
                  + cells + "</tr></table>"
                  + button("Prepay 12 months", PREPAY_12_URL, mt=24)
                  + p("Same All-Studio Unlimited you have now: all 3 studios, 20% off retail and a guest pass every month. "
                      "Teacher and nurse discounts don't apply to prepay.", 14, SUB, 0)
                  .replace("margin:0 0 0px", "margin:18px 0 0"), 0, 56)
            + row(display("How it works", 40, 34, INK, 22, "h2", ".95") + step_rows
                  + p(f"Want a different term than you have now? Pick whichever fits. Questions about your end date? "
                      f"<a href=\"mailto:{CONTACT}\" style=\"color:{INK};font-weight:700\">Ask us</a>.", 15, MUTED, 0), 48, 44, CREAM)
            + footer())

def e9_packs():
    """Clients who buy class packs: around two classes a week, unlimited costs less than a pack."""
    home = int(HOME_STUDIO[1:])
    cell = lambda v, c=INK, w=400, align="left": (
        f'<td align="{align}" style="padding:14px 0;border-top:1px solid {CARD_RULE};font-family:{FB};font-size:15px;'
        f'line-height:20px;font-weight:{w};color:{c}">{v}</td>')
    th = lambda v, align="left": (
        f'<td align="{align}" style="padding:0 0 10px;font-family:{FB};font-size:11px;line-height:14px;font-weight:700;'
        f'letter-spacing:.12em;text-transform:uppercase;color:{MUTED}">{v}</td>')
    rows = "".join(
        f"<tr>{cell(f'{n} classes ({n // 4} a week)', INK, 700)}{cell(f'${n * PACK_10_EACH}', INK, 400, 'right')}"
        f"{cell(f'You save ${n * PACK_10_EACH - home}', ACCENT, 700, 'right')}</tr>"
        for n in (8, 12, 16))
    table = ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
             + th("A month") + th("On 10-packs", "right") + th(f"Unlimited at {HOME_STUDIO}", "right") + "</tr>"
             + rows + "</table>")
    studio = lambda name, url: (f'<a href="{url}" style="font-family:{FB};font-size:15px;line-height:24px;font-weight:700;'
                                f'color:{INK};text-decoration:underline;white-space:nowrap">{name} &rarr;</a>')
    home_links = " &nbsp;&middot;&nbsp; ".join(studio(n, u) for n, u in HOME_STUDIO_URLS)
    return (header("Class packs", "https://oakcliffpilates.com")
            + row(eyebrow(f"Ends {DEADLINE}")
                  + display("Done buying<br>class packs?", 64, 46)
                  + p(f"Hi {NAME}. At ${PACK_10_EACH} a class on a 10-pack, twice a week costs you about "
                      f"${8 * PACK_10_EACH} a month. Unlimited at your home studio is {strong(HOME_STUDIO)}, and you can come every day.")
                  + p(f"On January 1, All-Studio Unlimited goes to {NEW_RATE}. Join before {DEADLINE} and today's price is "
                      "yours through December 31, 2027.", mb=0)
                  + button(f"Join at {ALL_STUDIO}", ALL_STUDIO_URL, mt=24), 52, 0)
            + spacer(48)
            + row(display("The math", 40, 34, INK, 8, "h2", ".95")
                  + p(f"Your pack price next to Home Studio Unlimited. It pays off from {-(-home // PACK_10_EACH)} classes a month.",
                      16, MUTED, 16)
                  + table, 44, 40, CREAM)
            + row(display("Two ways to go unlimited", 32, 28, INK, 14, "h2", ".95")
                  + f'<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:700;letter-spacing:.12em;'
                    f'text-transform:uppercase;color:{INK};margin:0 0 6px">Home Studio Unlimited &middot; {HOME_STUDIO}/mo</div>'
                  + p("Unlimited at the studio you call home. 10% off retail.", 15, MUTED, 8)
                  + f'<div style="line-height:28px;margin:0 0 22px">{home_links}</div>'
                  + f'<div style="font-family:{FB};font-size:13px;line-height:18px;font-weight:700;letter-spacing:.12em;'
                    f'text-transform:uppercase;color:{INK};margin:0 0 6px">All-Studio Unlimited &middot; {ALL_STUDIO}/mo</div>'
                  + p(f"Unlimited at all 3 studios. 20% off retail. {NEW_RATE} from January 1.", 15, MUTED, 8)
                  + f'<a href="{ALL_STUDIO_URL}" style="font-family:{FB};font-size:15px;line-height:24px;font-weight:700;'
                    f'color:{INK};text-decoration:underline">Join at {ALL_STUDIO} &rarr;</a>'
                  + '<div style="height:40px;line-height:40px;font-size:0">&nbsp;</div>'
                  + eyebrow("Both come with", INK, 12) + perks(MUTED).replace(f"color:{ACCENT}\">&mdash;", f"color:{INK}\">&mdash;")
                  + p(f"Still have classes on a pack? Write to {CONTACT} and we'll help you figure out the best time to switch.",
                      15, MUTED, 0).replace("margin:0 0 0px", "margin:8px 0 0"), 0, 48, CREAM)
            + footer("you've bought a class pack at Oak Cliff Pilates"))


# ── Main brand restyle (black, gold, Khand + Montserrat) ─────────────────
# The rate lock series uses the /ratelock page's orange and Anton. Emails flagged brand=True
# get the main Oak Cliff Pilates palette instead, matching /upgrade25.
BRAND_SWAP = {ACCENT: "#C9A24A", INK: "#0B0B0B", RULE: "#40351D", MUTED: "#57534A",
              FD: "Khand,'Arial Narrow',Arial,sans-serif",
              FB: "Montserrat,'Helvetica Neue',Helvetica,Arial,sans-serif",
              "family=Anton&family=Archivo:wght@400;600;700": "family=Khand:wght@600;700&family=Montserrat:wght@400;600;700"}


def brand(html):
    import re
    for old, new in BRAND_SWAP.items():
        html = html.replace(old, new)
    # Khand is light at 400, so every display-type style runs at 700.
    def bold(m):
        st = re.sub(r"font-weight:\d+;?", "", m.group(1))
        return f'style="{st.rstrip(";")};font-weight:700"'
    return re.sub(r'style="([^"]*font-family:Khand[^"]*)"', bold, html)


EMAILS = [
    dict(id="e1a", file="01a-unlimited-members", phase=1, send="Tue Nov 3 · All-Studio Unlimited members", build=e1_unlimited,
         subjects=[f"Keep {ALL_STUDIO} for all of 2027", f"Unlimited goes to {NEW_RATE}. You don't have to.", "Your rate, locked"],
         preheader=f"All-Studio Unlimited is {NEW_RATE} from January 1. Lock in {ALL_STUDIO} before {DEADLINE}."),
    dict(id="e1b", file="01b-class-members", phase=1, send="Tue Nov 3 · 4, 8 and 12-class members", build=e1_classes,
         subjects=["Ready to stop counting classes?", "Thinking about unlimited?", "Unlimited, locked for 2027"],
         preheader=f"No pressure. If you've wondered about unlimited, lock a 2027 rate before {DEADLINE}."),
    dict(id="e1c", file="01c-couples-members", phase=1, send="Tue Nov 3 · Unlimited Couples members", build=e1_couples,
         subjects=[f"Keep {COUPLES} for the two of you", "Two of you. One locked rate.", f"Couples goes to {COUPLES_NEW} in January"],
         preheader=f"Lock in Unlimited Couples at {COUPLES} before {DEADLINE} and keep it through 2027."),
    dict(id="e1", file="01-announcement", phase=1, send="Tue Nov 3 · Everyone else", build=e1,
         subjects=["Prices change January 1. Yours doesn't have to.", "Lock your rate for all of 2027", "You get first move"],
         preheader=f"Choose a membership before {DEADLINE} and keep your rate through 2027."),
    dict(id="e2", file="02-which-plan", phase=1, send="Tue Nov 17", build=e2,
         subjects=["Which plan is yours?", "Two ways to stay unlimited", "Pick the plan that fits your week"],
         preheader="All-Studio or Home Studio. Whichever you choose keeps today's price in 2027."),
    dict(id="e3", file="03-prepay", phase=1, send="Tue Dec 1", build=e3,
         subjects=["Full unlimited for under $200 a month", "Pay ahead, pay less", "$549 off a year of unlimited"],
         preheader=f"Prepay All-Studio Unlimited and skip the {NEW_RATE} rate entirely."),
    dict(id="e4", file="04-if-you-do-nothing", phase=1, send="Wed Dec 9", build=e4,
         subjects=["What happens if you do nothing", "The fine print, made short", "Your membership on January 1"],
         preheader=f"Memberships that don't choose move to {NEW_RATE} a month on January 1."),
    dict(id="e5", file="05-five-days-left", phase=2, send="Sun Dec 27", build=e5,
         subjects=["5 days left to lock your rate", "After December 31, it's gone", "One minute, all of 2027"],
         preheader=f"Choose before {DEADLINE} and keep today's price through 2027."),
    dict(id="e6", file="06-last-day", phase=2, send="Thu Dec 31, 9am", build=e6,
         subjects=["Last day to lock your rate", "Tonight's the night", "Midnight"],
         preheader=f"Tomorrow All-Studio Unlimited is {NEW_RATE} a month."),
    dict(id="e7", file="07-intro-offers", phase=3, brand=True, send="Intro offer clients who haven't bought a membership", build=e7_intro,
         subjects=["$25 off, and your rate locked for 2027", f"{INTRO_CODE}: $25 off your first month",
                   "Liked it? Lock it in before January."],
         preheader=f"Use {INTRO_CODE} for $25 off, and join before {DEADLINE} to keep today's price all of 2027."),
    dict(id="e8", file="08-prepay-members", phase=4, send="Current 3, 6 and 12-month prepay members", build=e8_prepay_renew,
         subjects=["Your next prepay, at this year's price", "Prepay goes up January 1. Yours doesn't have to.",
                   "Lock your renewal before December 31"],
         preheader=f"Buy your next prepay before {DEADLINE}. It starts when yours renews, at today's price."),
    dict(id="e9", file="09-class-packs", phase=5, send="Clients who buy class packs (no membership)", build=e9_packs,
         subjects=["Done buying class packs?", "Twice a week? Unlimited costs less.", f"Unlimited for {HOME_STUDIO}, locked through 2027"],
         preheader=f"At two classes a week, unlimited costs less than your pack. Lock today's price before {DEADLINE}."),
]

MOBILE = """
  .container{width:100%!important}
  .px{padding-left:20px!important;padding-right:20px!important}
  .card{padding:22px 20px!important}
  .stack{display:block!important;width:100%!important;box-sizing:border-box}
  .card-m{padding:0 0 12px!important}
  .btn{display:block!important;min-width:0!important}
  .pill{display:none!important}
  .count{font-size:150px!important}
""" + "".join(f"  .d{s}{{font-size:{s}px!important}}\n" for s in (28, 30, 34, 42, 44, 46, 52, 58))


def page(e, body):
    pre = e["preheader"] + "&#847;&zwnj;&nbsp;" * 60
    return f"""<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="format-detection" content="telephone=no, date=no, address=no, email=no">
<meta name="robots" content="noindex">
<title>{e['subjects'][0]}</title>
<!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Archivo:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  body{{margin:0;padding:0;width:100%!important;-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}}
  table{{border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0}}
  img{{border:0;outline:none;text-decoration:none;-ms-interpolation-mode:bicubic}}
  a[x-apple-data-detectors]{{color:inherit!important;text-decoration:none!important}}
  @media only screen and (max-width:620px){{{MOBILE}  }}
</style>
</head>
<body style="margin:0;padding:0;background:{INK}" bgcolor="{INK}">
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;font-size:1px;line-height:1px;color:{INK}">{pre}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{INK}" style="background:{INK}">
<tr><td align="center" style="padding:0">
<!--[if mso]><table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0"><tr><td><![endif]-->
<table role="presentation" class="container" width="600" cellpadding="0" cellspacing="0" border="0" bgcolor="{INK}" style="width:600px;max-width:600px;background:{INK}">
{body}</table>
<!--[if mso]></td></tr></table><![endif]-->
</td></tr>
</table>
</body>
</html>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for e in EMAILS:
        html = page(e, e["build"]())
        (OUT / f"{e['file']}.html").write_text(brand(html) if e.get("brand") else html)
        manifest.append({k: e[k] for k in ("id", "file", "phase", "send", "subjects", "preheader")})
    (OUT / "emails.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(EMAILS)} emails to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
