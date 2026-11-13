#!/usr/bin/env python3
"""Build the new client welcome series: 4 emails plus the texts that go with them.

Email 00 goes to every new client added in Arketa and sells the intro offers.
Emails 01 to 03 are triggered by the purchase of any New Client Special in Arketa (3 classes for $25,
1-Week Unlimited for $59, 10 classes for $145). Every email points first timers to
the /welcome landing page.

Visual source: the updated brand (welcome/css/tokens.css, Khand + Montserrat, gold on
black). The building blocks (row, button, header, locations, page shell...) are shared
with tools/build-trial-emails.py so both series stay identical in look.

Output: emails/welcome/*.html (table-based, inline styles) and emails.json for the
preview page, which also lists the texts.

    python3 tools/build-welcome-emails.py
"""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "emails" / "welcome"

_spec = importlib.util.spec_from_file_location("trial", ROOT / "tools" / "build-trial-emails.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

# Shared tokens and blocks
BLACK, CREAM, GOLD, GOLD_WARM = T.BLACK, T.CREAM, T.GOLD, T.GOLD_WARM
TEXT, TEXT_LIGHT, DIM = T.TEXT, T.TEXT_LIGHT, T.DIM
RULE_GOLD, RULE_SOFT, GOLD_TINT, CARD = T.RULE_GOLD, T.RULE_SOFT, T.GOLD_TINT, T.CARD
FD, FB, PX_D = T.FD, T.FB, T.PX_D
IMG = T.IMG
row, spacer, eyebrow, display, p, strong, gold, button = (
    T.row, T.spacer, T.eyebrow, T.display, T.p, T.strong, T.gold, T.button)
header, locations, footer, numbered, vpad, rule = T.header, T.locations, T.footer, T.numbered, T.vpad, T.rule

# ── Links ────────────────────────────────────────────────────────────────
NAME = "{{clientFirstName}}"                     # Arketa merge tag
WELCOME = "https://lp.oakcliffpilates.com/welcome"
FIRST_CLASS = f"{WELCOME}#first-class"
CLASSES = f"{WELCOME}#classes"
AFTER = f"{WELCOME}#after"                       # UPGRADE25 memberships + class packs
SCHEDULE = T.SCHEDULE
CHECKOUT = "https://app.arketa.co/oakcliffpilates/pricing/checkout/"
CODE = "UPGRADE25"

# ── Offer facts (Arketa catalog, 2026-11-12) ─────────────────────────────
# name, detail, monthly price, first month with UPGRADE25
MEMBERSHIPS = [("All-Studio Unlimited", "Every class, all 3 studios", "$209", "$184"),
               ("Home Studio Unlimited", "Unlimited at one studio", "$189", "$164"),
               ("12 classes a month", "The Regular", "$189", "$164"),
               ("8 classes a month", "Perfect Balance", "$159", "$134"),
               ("4 classes a month", "OCP Lite", "$99", "$74")]
PACKS = [("5 classes", "$145", "$29 a class"), ("10 classes", "$290", "$29 a class"),
         ("20 classes", "$560", "$28 a class"), ("40 classes", "$1,080", "$27 a class")]
# Class guide: name, pace (1 easy, 2 steady, 3 high), one line. Mirrors /welcome.
CLASS_GUIDE = [
    ("OG Reformer", 2, "The foundation. Full body, and every other class builds on it."),
    ("Classical AF", 2, "The classical Pilates order. Precise, flowing, deep core."),
    ("Arms, Ass &amp; Abs", 3, "Sculpting for arms, glutes and core. Lots of burn."),
    ("Jumpboard", 3, "Cardio intervals lying down. Heart rate up, easy on joints."),
    ("Tabata Pilates", 3, "Short, all-out intervals. The fastest 45 on the schedule."),
    ("Restorative", 1, "Slower and stretchier. Mobility, breath and recovery."),
]
PACE = {1: "Easy", 2: "Steady", 3: "High"}
OFFERS = f"{WELCOME}#offers"
# tag, name, price, detail, link label, checkout. Mirrors the /welcome offer cards.
INTRO_OFFERS = [
    ("Most popular", "3 classes", "$25", "Use within 30 days. About $8 a class.", "Get 3 classes for $25",
     CHECKOUT + "CX8QBVvU6bdj31zrkZbR"),
    ("Go all in", "1 week unlimited", "$59", "Unlimited classes for 7 days, starting at your first class.", "Get the week for $59",
     CHECKOUT + "08dxQyFUSU4GA782eKIz"),
    ("Best per class", "10 classes", "$145", "Use within 90 days. $14.50 a class.", "Get 10 classes for $145",
     CHECKOUT + "1oNxHZVRsxdC7ZWnwTBl"),
]


# ── Blocks for this series ───────────────────────────────────────────────

def pace_bar(n):
    cells = "".join(f'<td width="14" height="4" bgcolor="{GOLD if i < n else RULE_GOLD}" style="font-size:0;line-height:0">&nbsp;</td>'
                    + ('<td width="3" style="font-size:0">&nbsp;</td>' if i < 2 else "") for i in range(3))
    return f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>{cells}</tr></table>'


def class_guide():
    out = []
    for i, (name, pace, line) in enumerate(CLASS_GUIDE):
        start = i == 0
        bg = f' bgcolor="{GOLD_TINT}"' if start else ""
        bgc = f"background:{GOLD_TINT};" if start else ""
        badge = (f'<span style="display:inline-block;margin-left:10px;vertical-align:middle;background:{GOLD};color:{BLACK};'
                 f'font-family:{FB};font-size:9px;line-height:1;font-weight:700;letter-spacing:.18em;text-transform:uppercase;'
                 f'padding:5px 7px;border-radius:2px">Start here</span>') if start else ""
        out.append(
            f'<tr><td{bg} style="{bgc}padding:16px {16 if start else 0}px;border-top:1px solid {RULE_GOLD}">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td valign="top"><div style="font-family:{FD};font-size:22px;line-height:1;font-weight:700;text-transform:uppercase;'
            f'color:{CREAM}"><span style="vertical-align:middle">{name}</span>{badge}</div>'
            f'<div style="font-family:{FB};font-size:14px;line-height:1.5;color:{TEXT};padding-top:6px">{line}</div></td>'
            f'<td valign="top" align="right" width="64" style="padding-top:5px">{pace_bar(pace)}'
            f'<div style="font-family:{FB};font-size:9px;line-height:1;font-weight:600;letter-spacing:.18em;text-transform:uppercase;'
            f'color:{DIM};padding-top:6px;text-align:right">{PACE[pace]}</div></td>'
            "</tr></table></td></tr>")
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="border-bottom:1px solid {RULE_GOLD}">' + "".join(out) + "</table>")


def class_card(eyebrow_text, name, copy):
    return (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 12px"><tr>'
            f'<td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE_GOLD};border-radius:8px;padding:22px 22px 20px">'
            + eyebrow(eyebrow_text, mb=10)
            + f'<div style="font-family:{FD};font-size:30px;line-height:.95;font-weight:700;text-transform:uppercase;color:{CREAM};margin:0 0 10px">{name}</div>'
            + p(copy, 15, mb=0, lh="1.6") + "</td></tr></table>")


def code_box(dark=True):
    """The promo code in a dashed gold box, selectable in one tap."""
    fg, bg = (GOLD, BLACK) if dark else (BLACK, GOLD_WARM)
    border = GOLD if dark else BLACK
    return (f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td bgcolor="{bg}" style="background:{bg};border:2px dashed {border};border-radius:2px;padding:16px 22px 12px">'
            f'<div class="code" style="font-family:{FD};font-size:52px;line-height:.9;font-weight:700;letter-spacing:.02em;color:{fg}">{CODE}</div>'
            "</td></tr></table>")


def gold_band(inner, pt=36, pb=36):
    return (f'<tr><td class="px" bgcolor="{GOLD}" style="background:{GOLD};padding:{pt}px {PX_D}px {pb}px">{inner}</td></tr>\n')


def membership_table(first_month=True):
    rows = []
    for i, (name, sub, price, first) in enumerate(MEMBERSHIPS):
        top = i == 0
        bg = f' bgcolor="{GOLD_TINT}"' if top else ""
        bgc = f"background:{GOLD_TINT};" if top else ""
        bb = f"border-bottom:1px solid {RULE_SOFT};" if i < len(MEMBERSHIPS) - 1 else ""
        size = 26 if top else 22
        right = (f'<span style="font-family:{FD};font-size:{30 if top else 26}px;line-height:1;font-weight:700;color:{GOLD}">{first}</span>'
                 f'<div style="font-family:{FB};font-size:11px;line-height:1.3;color:{DIM};padding-top:4px">first month, then {price}</div>'
                 if first_month else
                 f'<span style="font-family:{FD};font-size:26px;line-height:1;font-weight:700;color:{GOLD}">{price}</span>'
                 f'<span style="font-family:{FB};font-size:12px;font-weight:600;color:{TEXT}">/mo</span>')
        rows.append(
            f'<tr><td{bg} valign="middle" style="{bgc}padding:16px 18px;{bb}">'
            f'<div style="font-family:{FD};font-size:{size}px;line-height:.95;font-weight:700;text-transform:uppercase;color:{CREAM}">{name}</div>'
            f'<div style="font-family:{FB};font-size:13px;line-height:1.4;color:{DIM};padding-top:4px">{sub}</div></td>'
            f'<td{bg} valign="middle" align="right" style="{bgc}padding:16px 18px;{bb}white-space:nowrap">{right}</td></tr>')
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="border:1px solid {GOLD};border-radius:2px;border-collapse:separate">' + "".join(rows) + "</table>")


def pack_table():
    rows = []
    for i, (name, price, each) in enumerate(PACKS):
        bb = f"border-bottom:1px solid {RULE_SOFT};" if i < len(PACKS) - 1 else ""
        rows.append(
            f'<tr><td valign="middle" style="padding:14px 0;{bb}"><div style="font-family:{FD};font-size:22px;line-height:1;'
            f'font-weight:700;text-transform:uppercase;color:{CREAM}">{name}</div></td>'
            f'<td valign="middle" align="right" style="padding:14px 0;{bb}white-space:nowrap">'
            f'<span style="font-family:{FD};font-size:24px;line-height:1;font-weight:700;color:{CREAM}">{price}</span>'
            f'<span style="font-family:{FB};font-size:12px;color:{DIM};padding-left:10px">{each}</span></td></tr>')
    return ('<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
            f'style="border-top:1px solid {RULE_GOLD};border-bottom:1px solid {RULE_GOLD}">' + "".join(rows) + "</table>")


def perks():
    items = ["Book 14 days ahead", "A free guest pass every month", "Pause up to twice a year",
             "20% off retail with All-Studio Unlimited, 10% with Home Studio"]
    return "".join(
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td width="22" valign="top" style="padding:2px 0 8px;font-family:{FB};font-size:15px;line-height:22px;font-weight:700;color:{GOLD}">&mdash;</td>'
        f'<td valign="top" style="padding:2px 0 8px 6px;font-family:{FB};font-size:15px;line-height:22px;color:{TEXT}">{t}</td>'
        "</tr></table>" for t in items)


def text_link(label, href, color=GOLD, mt=16):
    return (f'<div style="margin-top:{mt}px;font-family:{FB};font-size:14px;line-height:1.5;font-weight:600">'
            f'<a href="{href}" style="color:{color};text-decoration:underline">{label} &rarr;</a></div>')


# ── Emails ───────────────────────────────────────────────────────────────

def offer_rows():
    """The three New Client Specials, 3 for $25 on top with weight. Each row opens its checkout."""
    out = []
    for i, (tag, name, price, detail, cta, href) in enumerate(INTRO_OFFERS):
        top = i == 0
        bg = f' bgcolor="{GOLD_TINT}"' if top else ""
        bgc = f"background:{GOLD_TINT};" if top else ""
        border = GOLD if top else RULE_GOLD
        out.append(
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 12px"><tr>'
            f'<td{bg} style="{bgc}border:1px solid {border};border-radius:2px;padding:20px 20px 18px">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td valign="bottom">' + eyebrow(tag, GOLD if top else DIM, 8)
            + f'<div style="font-family:{FD};font-size:{28 if top else 24}px;line-height:.95;font-weight:700;text-transform:uppercase;color:{CREAM}">{name}</div>'
            f'<div style="font-family:{FB};font-size:13px;line-height:1.45;color:{TEXT};padding-top:6px">{detail}</div></td>'
            f'<td valign="bottom" align="right" style="white-space:nowrap;padding-left:12px">'
            f'<span style="font-family:{FD};font-size:{56 if top else 44}px;line-height:.85;font-weight:700;color:{GOLD}">{price}</span></td>'
            f'</tr></table>'
            f'<div style="padding-top:14px"><a href="{href}" style="font-family:{FB};font-size:14px;line-height:20px;font-weight:700;'
            f'color:{GOLD if top else CREAM};text-decoration:underline">{cta} &rarr;</a></div>'
            "</td></tr></table>")
    return "".join(out)


def e0():
    t, tm = vpad(32, 9, 56)
    g, gm = vpad(32, 9, 48)
    expect = numbered([
        p(f"{strong('45 minutes on the reformer.')} 12 people max, lights down, music up.", 15, mb=0, lh="1.6"),
        p(f"{strong('Never done Pilates? Perfect.')} A trainer sets up your reformer and cues every move, with an easier "
          "option for all of them.", 15, mb=0, lh="1.6"),
        p(f"{strong('Three studios, 250+ classes a week.')} Bishop Arts, Uptown and Lower Greenville. Your intro works at all "
          "three.", 15, mb=0, lh="1.6"),
    ])
    return (
        header("New here")
        + row(eyebrow(f"Hi {NAME}, welcome to OCP.", mb=20)
              + display(f"Your first class is {gold('$25 away.')}", 44, 11.5, 74, mb=20)
              + p("Thanks for joining us. The best way to find out if Oak Cliff Pilates is for you is to come try it, so we "
                  "made it easy: pick an intro offer below and book your first class.", 17, TEXT_LIGHT, 24)
              + button("Choose my intro offer", OFFERS), t, 0, tm)
        + spacer(g, gm)
        + f'<tr><td style="padding:0"><a href="{OFFERS}"><img src="{IMG}/trial-first-class-setup.jpg" width="600" height="375" class="fluid" '
          f'alt="A trainer setting up a client on the reformer" style="display:block;width:600px;height:auto;max-width:100%;border:0"></a></td></tr>\n'
        + row(eyebrow("New client specials", mb=14)
              + display(f"Three ways {gold('to start')}", 34, 9, 44, ".9", "h2", mb=14, ls="-.01em")
              + p("One-time offers for your first visit. Every one works at all three studios, on every class.", 15, mb=20, lh="1.6")
              + offer_rows()
              + p("New clients only, one intro offer per person.", 12, DIM, 0, "1.5").replace("margin:0 0 0px", "margin:4px 0 0"),
              g, 0, gm)
        + row(display("What to expect", 34, 0, 34, ".9", "h2", mb=18, ls="-.01em") + expect
              + button("Get 3 classes for $25", INTRO_OFFERS[0][5], mt=24)
              + text_link("Read the first-timer guide", FIRST_CLASS), g, 0, gm)
        + spacer(g, gm) + locations() + footer()
    )


def e1():
    t, tm = vpad(32, 9, 56)
    g, gm = vpad(32, 9, 48)
    tips = numbered([
        p(f"{strong('Arrive 10 minutes early.')} Tell the front desk it's your first time and a trainer will set your "
          "springs and footbar and walk you through the reformer.", 15, mb=0, lh="1.6"),
        p(f"{strong('Bring grip socks.')} They're required on the reformer. No pair? Grab one at the front desk.", 15, mb=0, lh="1.6"),
        p(f"{strong('Wear something fitted.')} Leggings and a fitted top. Loose clothes catch on the springs and straps.", 15, mb=0, lh="1.6"),
        p(f"{strong('Eat light, bring water.')} Skip the big meal in the hour before class.", 15, mb=0, lh="1.6"),
        p(f"{strong('Go at your own pace.')} Every move has an easier option, and nobody is watching you. They're all busy "
          "with their own reformer.", 15, mb=0, lh="1.6"),
    ])
    return (
        header("Welcome")
        + row(eyebrow(f"{NAME}, you're in.", mb=20)
              + display(f"We're so glad {gold('you&rsquo;re here.')}", 44, 11.5, 74, mb=20)
              + p("Welcome to Oak Cliff Pilates. Your intro offer is ready at all three studios, on every class on the "
                  "schedule. All that's left is the fun part: picking your first class.", 17, TEXT_LIGHT, 24)
              + button("Book your first class", SCHEDULE), t, 0, tm)
        + spacer(g, gm)
        + f'<tr><td style="padding:0"><a href="{FIRST_CLASS}"><img src="{IMG}/trial-first-class-setup.jpg" width="600" height="375" class="fluid" '
          f'alt="A trainer setting up a client on the reformer" style="display:block;width:600px;height:auto;max-width:100%;border:0"></a></td></tr>\n'
        + row(display("Before your first class", 34, 0, 34, ".9", "h2", mb=18, ls="-.01em") + tips, g, 0, gm)
        + row(eyebrow("Which class?", mb=14)
              + display(f"Same reformer. {gold('Six ways to sweat.')}", 34, 9, 44, ".9", "h2", mb=14, ls="-.01em")
              + p("Every class is 45 minutes on the reformer, 12 people max. Start with OG Reformer, then work your way "
                  "across the schedule.", 15, mb=20, lh="1.6")
              + class_guide()
              + button("Find your class", SCHEDULE, mt=24)
              + text_link("Read the full first-timer guide", FIRST_CLASS), g, 0, gm)
        + spacer(g, gm) + locations() + footer()
    )


def e2():
    t, tm = vpad(32, 9, 56)
    g, gm = vpad(32, 9, 48)
    big = (f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" '
           f'style="border-top:1px solid {RULE_GOLD};border-bottom:1px solid {RULE_GOLD}"><tr>'
           f'<td class="stack" valign="middle" width="190" style="padding:20px 24px 20px 0">'
           f'<div class="{T.M.cls("font-size:120px!important")}" style="font-family:{FD};font-size:150px;line-height:.78;'
           f'font-weight:700;letter-spacing:-.04em;color:{GOLD};white-space:nowrap">2&ndash;3</div></td>'
           f'<td class="stack" valign="middle" style="padding:20px 0">'
           + eyebrow("Classes a week", mb=10)
           + f'<div style="font-family:{FD};font-size:34px;line-height:.92;font-weight:700;text-transform:uppercase;color:{CREAM};margin:0 0 10px">That&rsquo;s the rhythm that sticks.</div>'
           + p("Book a few days apart so your body gets a break in between. Put them on the calendar now, while it's fresh.", 15, mb=0, lh="1.6")
           + "</td></tr></table>")
    return (
        header("Keep it up")
        + row(display(f"One class is a visit. {gold('Three is a habit.')}", 44, 11.5, 70, mb=20)
              + p(f"{NAME}, the second class is always easier than the first. You know where to park, how the reformer works "
                  "and what the springs feel like. Now the secret is simple: keep showing up.", 17, TEXT_LIGHT, 0), t, 0, tm)
        + row(big, *vpad(28, 8, 40)[:1], 0, vpad(28, 8, 40)[1])
        + row(button("Book your next class", SCHEDULE), *vpad(24, 7, 32)[:1], 0, vpad(24, 7, 32)[1])
        + row(display(f"Two classes {gold('to try next')}", 34, 9, 44, ".9", "h2", mb=18, ls="-.01em")
              + class_card("If you liked OG Reformer", "Classical AF",
                           "The classical Pilates order, done with precision. Slower, flowing, and the deepest core work on the "
                           "schedule. It sneaks up on you.")
              + class_card("If you want to sweat", "Jumpboard",
                           "Cardio on the reformer. Jumping intervals lying down, so your heart rate climbs without the pounding "
                           "on your knees.")
              + text_link("See every class", CLASSES, mt=8), g, 0, gm)
        + spacer(g, gm)
        + gold_band(eyebrow("Ready to get started?", BLACK, 12).replace("font-weight:600", "font-weight:700")
                    + display("Save $25 on your first month.", 40, 10, 56, ".9", "h2", BLACK, 18)
                    + code_box(dark=False)
                    + p(f"Use code {strong(CODE, BLACK)} at checkout for $25 off the first month of any membership, from "
                        "4 classes a month to All-Studio Unlimited.", 15, BLACK, 0, "1.6").replace("margin:0 0 0px", "margin:18px 0 0")
                    + button("See memberships", AFTER, "outline", mt=20).replace(f"background:{BLACK};border:1px solid {GOLD}", f"background:{BLACK};border:1px solid {BLACK}"))
        + spacer(g, gm) + locations() + footer()
    )


def e3():
    t, tm = vpad(32, 9, 56)
    g, gm = vpad(32, 9, 48)
    return (
        header(CODE)
        + row(eyebrow(f"{NAME}, this one's for you.", mb=20)
              + display(f"Make OCP {gold('part of your week.')}", 44, 11.5, 74, mb=20)
              + p("Your intro was the warm-up. A membership is how it turns into a routine, and right now UPGRADE25 takes "
                  "$25 off your first month.", 17, TEXT_LIGHT, 24)
              + code_box()
              + p("Enter it at checkout. Works on every monthly membership.", 13, DIM, 0, "1.5").replace("margin:0 0 0px", "margin:12px 0 0"),
              t, 0, tm)
        + row(membership_table()
              + button("Claim $25 off", AFTER, mt=22), *vpad(28, 8, 40)[:1], 0, vpad(28, 8, 40)[1])
        + row(eyebrow("Every membership includes", mb=14) + perks(), *vpad(28, 8, 40)[:1], 0, vpad(28, 8, 40)[1])
        + spacer(g, gm)
        + row(display(f"Not ready {gold('to commit?')}", 34, 9, 44, ".9", "h2", mb=14, ls="-.01em")
              + p("Totally fair. Class packs have no monthly commitment, work at any studio and are good for a full year. "
                  "The bigger the pack, the less each class costs.", 15, mb=20, lh="1.6")
              + pack_table()
              + button("Buy a class pack", AFTER, "outline", mt=22)
              + p("Or drop in any time for $30 a class.", 13, DIM, 0, "1.5").replace("margin:0 0 0px", "margin:12px 0 0"),
              g, 0, gm, extra=f"border-top:1px solid {RULE_GOLD};")
        + spacer(g, gm)
        + row(rule(RULE_SOFT)
              + p(f"Not sure which one fits? Email {strong('kiel@oakcliffpilates.com')} or ask at the front desk next time "
                  "you're in. A real person will help you pick.", 14, DIM, 0, "1.6").replace("margin:0 0 0px", "margin:20px 0 0"), 0, 0)
        + spacer(g, gm) + locations() + footer()
    )


# Texts go out from Arketa alongside each email. Keep each under 160 characters
# (one SMS segment, with room for a first name) and skip emoji: one emoji drops
# the segment limit to 70 characters.
EMAILS = [
    dict(id="e0", file="00-new-client", phase=0, trigger="On new client added, no purchase yet", build=e0,
         subjects=["Welcome to OCP. Your first class is $25 away.", "3 classes for $25, just for new clients",
                   "Ready for your first class?"],
         preheader="Pick an intro offer and book your first reformer class. 3 classes for $25 to start.",
         sms=[dict(when="On new client added, with email 0",
                   text=f"Hi {NAME}, welcome to Oak Cliff Pilates! New clients get 3 classes for $25. Grab yours + book: "
                        "lp.oakcliffpilates.com/welcome Reply STOP to opt out")]),
    dict(id="e1", file="01-welcome", phase=1, trigger="On purchase of a New Client Special", build=e1,
         subjects=["You're in. Welcome to OCP.", "We're so glad you're here", "Your first class starts here"],
         preheader="Tips for your first class, which class to take first, and the link to book it.",
         sms=[dict(when="On purchase, with email 1",
                   text=f"Hi {NAME}, welcome to Oak Cliff Pilates! Your intro is ready. First-timer tips + booking: "
                        "lp.oakcliffpilates.com/welcome Reply STOP to opt out"),
              dict(when="Day before first booked class (optional)",
                   text=f"See you tomorrow, {NAME}! Arrive 10 min early, wear fitted clothes + bring grip socks. "
                        "Tell the desk it's your first class and we'll set you up.")]),
    dict(id="e2", file="02-keep-it-up", phase=1, trigger="Purchase + 4 days", build=e2,
         subjects=["One class is a visit. Three is a habit.", "Keep it up", "Two classes to try next"],
         preheader="Why 2 to 3 classes a week works, two classes to try next, and $25 off with UPGRADE25.",
         sms=[dict(when="Purchase + 4 days, with email 2",
                   text=f"{NAME}, the 2nd class is where it clicks. Book your next one: oakcliffpilates.com/class-schedule "
                        "Ready to commit? UPGRADE25 = $25 off a membership.")]),
    dict(id="e3", file="03-upgrade25", phase=1, trigger="Purchase + 10 days, no membership", build=e3,
         subjects=["$25 off your first month", "Make OCP part of your week", "UPGRADE25 is waiting for you"],
         preheader="Use UPGRADE25 for $25 off any membership. Or grab a class pack, no commitment.",
         sms=[dict(when="Purchase + 10 days, with email 3",
                   text=f"{NAME}, make OCP part of your week. Code UPGRADE25 = $25 off your first month of membership. "
                        "Packs too: lp.oakcliffpilates.com/welcome#after")]),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for e in EMAILS:
        T.M = T.Mobile()
        body = e["build"]()
        (OUT / f"{e['file']}.html").write_text(T.page(e, body, BLACK))
        manifest.append({k: e[k] for k in ("id", "file", "phase", "trigger", "subjects", "preheader", "sms")})
        for s in e["sms"]:
            n = len(s["text"].replace(NAME, "Alexandra"))
            if n > 160:
                print(f"  warning: {e['file']} text is {n} characters with a long first name: {s['text'][:40]}...")
    (OUT / "emails.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Wrote {len(EMAILS)} emails to {OUT.relative_to(ROOT)} (images from {IMG})")


if __name__ == "__main__":
    main()
