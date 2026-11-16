#!/usr/bin/env python3
"""Build the review request email sent after a client's third class.

The main button opens /review, where the client picks a studio. Each studio also
has its own row in the email that goes straight to that studio's review link.

Visual source: the updated brand (Khand + Montserrat, gold on black). The building
blocks come from tools/build-trial-emails.py so every lifecycle email looks the same.

Output: emails/review.html (table-based, inline styles).

    python3 tools/build-review-email.py
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "emails" / "review.html"

_spec = importlib.util.spec_from_file_location("trial", ROOT / "tools" / "build-trial-emails.py")
T = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(T)

BLACK, CREAM, GOLD = T.BLACK, T.CREAM, T.GOLD
TEXT, TEXT_LIGHT, DIM = T.TEXT, T.TEXT_LIGHT, T.DIM
RULE_GOLD, RULE_SOFT, CARD = T.RULE_GOLD, T.RULE_SOFT, T.CARD
FD, FB = T.FD, T.FB
row, spacer, eyebrow, display, p, strong, gold, button, header, footer, vpad = (
    T.row, T.spacer, T.eyebrow, T.display, T.p, T.strong, T.gold, T.button, T.header, T.footer, T.vpad)

NAME = "{{clientFirstName}}"                     # Arketa merge tag
REVIEW_PAGE = "https://lp.oakcliffpilates.com/review"
CONTACT = "kiel@oakcliffpilates.com"
STUDIOS = [("Bishop Arts", "196 W Davis St", "https://go.revublast.com/ocp-bishop"),
           ("Uptown", "2222 McKinney Ave", "https://go.revublast.com/ocp-uptown"),
           ("Lower Greenville", "2000 Greenville Ave", "https://go.revublast.com/ocp-lower-greenville")]

META = dict(
    subjects=["Three classes in. How's it going?", "Got a minute for a quick review?", "You've officially got the hang of it"],
    preheader="If you're enjoying OCP, a quick review helps your neighbors find us. Pick your studio, it takes a minute.",
)


def stars():
    return (f'<div style="font-family:Arial,sans-serif;font-size:22px;line-height:1;letter-spacing:4px;color:{GOLD};'
            'margin:0 0 18px" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</div>')


def studio_rows():
    """One tappable row per studio, straight to its review link."""
    out = []
    for name, addr, href in STUDIOS:
        out.append(
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0 0 10px"><tr>'
            f'<td bgcolor="{CARD}" style="background:{CARD};border:1px solid {RULE_GOLD};border-radius:8px;padding:0">'
            f'<a href="{href}" style="display:block;text-decoration:none;color:{CREAM};padding:18px 20px">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td valign="middle"><div style="font-family:{FD};font-size:24px;line-height:1;font-weight:700;'
            f'text-transform:uppercase;color:{CREAM}">{name}</div>'
            f'<div style="font-family:{FB};font-size:13px;line-height:1.4;color:{DIM};padding-top:5px">{addr}</div></td>'
            f'<td valign="middle" align="right" style="white-space:nowrap;font-family:{FD};font-size:16px;line-height:1;'
            f'font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:{GOLD}">Review &rarr;</td>'
            "</tr></table></a></td></tr></table>")
    return "".join(out)


def build():
    t, tm = vpad(32, 9, 56)
    g, gm = vpad(32, 9, 48)
    return (
        header("Three classes in")
        + row(stars()
              + eyebrow(f"{NAME}, three classes down.", mb=18)
              + display(f"How's it {gold('going?')}", 52, 14, 92, ".86", mb=20)
              + p("Three classes is about when the reformer stops feeling new and starts feeling like yours. If you're "
                  "enjoying it, would you leave us a quick review?", 17, TEXT_LIGHT, 16)
              + p("It helps your neighbors find their way to OCP, and our trainers read every single one. It takes about "
                  "a minute.", mb=24)
              + button("Leave a review", REVIEW_PAGE), t, 0, tm)
        + row(eyebrow("Or tap your studio", mb=14) + studio_rows()
              + p("Been to more than one? Pick the one you go to most.", 13, DIM, 0, "1.5")
                .replace("margin:0 0 0px", "margin:4px 0 0"), g, 0, gm)
        + row(f'<div style="border-top:1px solid {RULE_SOFT};font-size:0;line-height:0">&nbsp;</div>'
              + display("Not sure what to say?", 26, 0, 26, "1", "h2", mb=12, ls="0")
                .replace("margin:0 0 12px", "margin:24px 0 12px")
              + p("Your favorite class or trainer by name, how you felt walking in the first time, or what you'd tell a "
                  "friend who's thinking about trying it.", 15, mb=0, lh="1.6"), g, 0, gm)
        + row(f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
              f'<td bgcolor="#161514" style="background:#161514;border:1px solid {RULE_SOFT};border-radius:8px;padding:20px">'
              + display("Something not right?", 24, 0, 24, "1", "h3", mb=8, ls="0")
              + p(f'Tell us directly and a real person will make it right: '
                  f'<a href="mailto:{CONTACT}?subject=Feedback%20about%20my%20classes" style="color:{GOLD};font-weight:600">{CONTACT}</a>',
                  15, mb=0, lh="1.6")
              + "</td></tr></table>", g, 0, gm)
        + spacer(g, gm) + footer()
    )


def main():
    T.M = T.Mobile()
    body = build()
    OUT.write_text(T.page(META, body, BLACK))
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
