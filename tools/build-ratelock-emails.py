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


def header():
    return row(
        '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td style="vertical-align:middle"><a href="{PAGE}" style="text-decoration:none">'
        f'<img src="{IMG}/logo-puck-80.png" width="40" height="40" alt="Oak Cliff Pilates logo" '
        'style="display:inline-block;vertical-align:middle;border:0;width:40px;height:40px">'
        f'<span style="display:inline-block;vertical-align:middle;padding-left:12px;font-family:{FD};font-size:22px;'
        f'line-height:1;letter-spacing:.04em;text-transform:uppercase;color:{CREAM}">Oak Cliff Pilates</span></a></td>'
        f'<td align="right" style="vertical-align:middle"><span class="pill" style="display:inline-block;border:1px solid {CREAM};'
        f'border-radius:999px;padding:7px 14px;font-family:{FB};font-size:11px;line-height:1;font-weight:600;'
        f'letter-spacing:.12em;text-transform:uppercase;color:{CREAM};white-space:nowrap">Members only</span></td>'
        '</tr></table>', 22, 22, extra=f"border-bottom:1px solid {RULE};")


def footer():
    locs = "Bishop Arts &middot; Uptown &middot; Lower Greenville"
    return (row(display("Questions? Ask a real person.", 36, 30, INK, 10, "div", "1")
                + f'<a href="mailto:{CONTACT}" style="font-family:{FB};font-size:18px;line-height:1.4;font-weight:700;'
                  f'color:{INK};text-decoration:underline">{CONTACT}</a>'
                + f'<div style="padding-top:22px;font-family:{FB};font-size:12px;line-height:18px;font-weight:700;'
                  f'letter-spacing:.12em;text-transform:uppercase;color:{INK}">{locs}</div>', 44, 0, ACCENT)
            + row(f'<div style="font-family:{FB};font-size:12px;line-height:20px;color:{INK}">You\'re getting this because '
                  f'you\'re an Oak Cliff Pilates member. <a href="{UNSUBSCRIBE}" style="color:{INK};text-decoration:underline">'
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
        (OUT / f"{e['file']}.html").write_text(page(e, e["build"]()))
        manifest.append({k: e[k] for k in ("id", "file", "phase", "send", "subjects", "preheader")})
    (OUT / "emails.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(EMAILS)} emails to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
