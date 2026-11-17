"""Generates the OCP Holiday Campaigns canvas: project/canvas.json + one .dc.html per artboard."""
import json, math, os, re, datetime, html

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canvas')
DS = 'oakcliffpilatesdesignsystem_8359ad'
DS_URL = 'https://claude.ai/artifact/MBvDv7ANZwSLTVvCQ3K3ke'
PUCK = f'ds/{DS}/assets/logos/ocp-logo-gold-circle.png'

B = '#0B0B0B'; INK = '#161514'; G = '#C9A24A'; GW = '#E9C977'; GD = '#8E6B2A'
C = '#F4EFE6'; PK = '#E63995'; S2 = '#E2DED3'; S3 = '#C9C6BC'; S5 = '#84827B'; S7 = '#3D3C39'; S8 = '#2A2A28'
GRAY = '#A8A69E'
KH = 'font-family: Khand, Impact, sans-serif; font-weight: 700; text-transform: uppercase'
MO = 'font-family: Montserrat, Helvetica, Arial, sans-serif'
CV = "font-family: 'Caveat Brush', cursive; font-weight: 400"
HAIR = 'rgba(201,162,74,0.45)'

LOCK_URL = 'lp.oakcliffpilates.com/ratelock'
BF_URL = 'lp.oakcliffpilates.com/black-friday [confirm]'


def esc(s):
    return html.escape(s, quote=False)


def page(title, w, h, inner, bg, clip=True):
    ov = 'overflow: hidden; ' if clip else ''
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{esc(title)}</title>
<script src="./support.js"></script>
<link rel="stylesheet" href="ds/{DS}/colors_and_type.css">
</head>
<body>
<x-dc>
<helmet>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat+Brush&amp;display=swap">
<style>
body{{margin:0}}
a{{color:{G}}}a:hover{{color:{GW}}}
</style>
</helmet>
<div style="position: relative; width: {w}px; height: {h}px; box-sizing: border-box; {ov}background: {bg}; color: {C}; {MO}; display: flex; flex-direction: column">
{inner}
</div>
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{{"$preview":{{"width":{w},"height":{h}}}}}'>
class Component extends DCLogic {{
  renderVals() {{ return {{}}; }}
}}
</script>
</body>
</html>
'''


# ---------- atoms ----------
def frame(inset=36, color=HAIR):
    return f'<div aria-hidden="true" style="position: absolute; top: {inset}px; left: {inset}px; right: {inset}px; bottom: {inset}px; border: 1px solid {color}; pointer-events: none"></div>'


def eyebrow(text, color=G, size=22, track='0.28em'):
    return f'<p style="margin: 0; {MO}; font-weight: 700; font-size: {size}px; line-height: 1.2; letter-spacing: {track}; text-transform: uppercase; color: {color}">{esc(text)}</p>'


def head(lines, size, colors, lh=0.86, track='-0.01em', align='left', extra=''):
    spans = []
    for i, l in enumerate(lines):
        col = colors[i] if i < len(colors) else colors[-1]
        spans.append(f'<span style="color: {col}">{esc(l)}</span>')
    return f'<h1 style="margin: 0; {KH}; font-size: {size}px; line-height: {lh}; letter-spacing: {track}; text-align: {align}; {extra}">{"<br>".join(spans)}</h1>'


def para(text, size, color, weight=400, lh=1.45, extra=''):
    return f'<p style="margin: 0; {MO}; font-size: {size}px; font-weight: {weight}; line-height: {lh}; color: {color}; {extra}">{esc(text)}</p>'


def puck(size, extra=''):
    return f'<img src="{PUCK}" alt="Oak Cliff Pilates" style="display: block; width: {size}px; height: {size}px; flex-shrink: 0; {extra}">'


def handle(color=G, size=22):
    return f'<p style="margin: 0; {MO}; font-weight: 700; font-size: {size}px; letter-spacing: 0.08em; color: {color}">@oakcliffpilates</p>'


IMG = {
    'greenville84': '/_blob/2ae07d381446a424a3e619dbeee6c0c2',
    'overhead': '/_blob/2ff128cedab652dac5d045a255c650fd',
    'neon': '/_blob/743468d23726ec07a652a405f4772bf6',
    'trainer': '/_blob/072eacaf45a23c57459c4f6c10b675f9',
    'firstclass': '/_blob/b3e84d3703a1142d05c5ae7f5533bb10',
    'lowergreenville': '/_blob/b21c919eebcc3d86974b01a167ee538d',
    'socks': '/_blob/39d2acf1ae3be278afba648d65fee711',
    'hoodie': '/_blob/c926cb6cb4afffcf27741e20b8a4b3bb',
    'tote': '/_blob/962e15304f50125ab5bfa77946c9b104',
}
PHOTO_MAP = [  # label substring -> (image, alt)
    ('member mid-class on reformer', 'greenville84', 'Members mid-class on reformers in warm light'),
    ('two members side by side', 'overhead', 'Members side by side on reformers'),
    ('member laughing between sets', 'lowergreenville', 'Member mid-movement on the reformer'),
    ('class mid-movement, warm light, close crop', 'lowergreenville', 'Member mid-movement on the reformer'),
    ('full class mid-movement', 'greenville84', 'A full class mid-movement'),
    ('class mid-movement, warm light', 'overhead', 'Class mid-movement on reformers'),
    ('gift card handoff', 'neon', 'Member on the reformer under the neon OCP sign'),
    ('midday class', 'trainer', 'Daytime class with sun through the windows'),
    ('first-timer on the reformer', 'firstclass', 'Instructor helping a new client on the reformer'),
    ('gift card and grip socks', 'socks', 'OCP grip socks'),
    ('merch hoodie', 'hoodie', 'OCP Anti-Pilates Pilates Club hoodie'),
    ('merch tote', 'tote', 'OCP Anti-Pilates Pilates Club tote'),
]
VID = {
    'studio': ('/_blob/0dc00cf647cc5504354d187dad4b5d49', '/_blob/b8b3bc06add78175bb44606538c60e79'),
    'classloop': ('/_blob/10e4fef6eeaa05d16414d843e7ebd232', '/_blob/a6048bf12ad563c354f265f0d38929e8'),
}


def video(key, w, h, frame_color=G, extra=''):
    src, poster = VID[key]
    wcss = f'{w}px' if isinstance(w, int) else w
    return (f'<video src="{src}" poster="{poster}" autoplay muted loop playsinline aria-label="OCP class footage" '
            f'style="display: block; width: {wcss}; height: {h}px; box-sizing: border-box; border: 3px solid {frame_color}; object-fit: cover; flex-shrink: 0; background: {B}; {extra}"></video>')


def photo(label, w, h, frame_color=G, extra=''):
    for key, img, alt in PHOTO_MAP:
        if key in label:
            wcss = f'{w}px' if isinstance(w, int) else w
            return (f'<img src="{IMG[img]}" alt="{alt}" style="display: block; width: {wcss}; height: {h}px; box-sizing: border-box; '
                    f'border: 3px solid {frame_color}; object-fit: cover; flex-shrink: 0; background: {GRAY}; {extra}">')
    fs = max(11, min(30, int(min(w if isinstance(w, int) else 900, h) / 14)))
    wcss = f'{w}px' if isinstance(w, int) else w
    return (f'<div style="width: {wcss}; height: {h}px; box-sizing: border-box; border: 3px solid {frame_color}; background: {GRAY}; '
            f'display: flex; align-items: center; justify-content: center; padding: 16px; flex-shrink: 0; {extra}">'
            f'<p style="margin: 0; {MO}; font-weight: 700; font-size: {fs}px; line-height: 1.3; letter-spacing: 0.04em; text-align: center; color: {B}">{esc(label)}</p></div>')


def button(text, size=30, bg=G, fg=B, pad='26px 52px', radius=14, extra='', href='#'):
    return (f'<a href="{href}" style="display: inline-flex; align-items: center; justify-content: center; align-self: flex-start; padding: {pad}; '
            f'background: {bg}; color: {fg}; border-radius: {radius}px; text-decoration: none; {KH}; font-size: {size}px; letter-spacing: 0.06em; line-height: 1; {extra}">{esc(text)}</a>')


def chip(text, size=26, bg=PK, fg=B, pad='12px 22px', extra=''):
    return (f'<p style="margin: 0; display: inline-block; align-self: flex-start; padding: {pad}; background: {bg}; color: {fg}; border-radius: 999px; '
            f'{KH}; font-size: {size}px; letter-spacing: 0.08em; line-height: 1; {extra}">{esc(text)}</p>')


def qr(size, label, extra=''):
    return (f'<div style="width: {size}px; height: {size}px; box-sizing: border-box; border: 3px solid {G}; background: #FFFFFF; display: flex; '
            f'align-items: center; justify-content: center; padding: 14px; flex-shrink: 0; {extra}">'
            f'<p style="margin: 0; {MO}; font-weight: 700; font-size: {max(11, size // 14)}px; line-height: 1.3; text-align: center; color: {B}">{esc(label)}</p></div>')


def sticker(label, w=640, extra=''):
    return (f'<div style="width: {w}px; height: 120px; box-sizing: border-box; border: 3px dashed {G}; border-radius: 24px; display: flex; '
            f'align-items: center; justify-content: center; padding: 0 24px; align-self: center; {extra}">'
            f'<p style="margin: 0; {MO}; font-weight: 700; font-size: 26px; letter-spacing: 0.04em; text-align: center; color: {G}">{esc(label)}</p></div>')


def row(items, gap=24, align='center', justify='space-between', extra=''):
    return f'<div style="display: flex; align-items: {align}; justify-content: {justify}; gap: {gap}px; {extra}">{"".join(items)}</div>'


def col(items, gap=24, extra=''):
    return f'<div style="display: flex; flex-direction: column; gap: {gap}px; {extra}">{"".join(items)}</div>'


def spacer():
    return '<div style="flex: 1 1 auto"></div>'


# ---------- facts ----------
NOW_RATE, NEW_RATE = '$209', '$229'
PREPAY = [('3 MONTHS', '$599', 'About $200 a month', 'Goes to $649 on Jan 1'),
          ('6 MONTHS', '$1,159', 'About $193 a month', 'Goes to $1,249 on Jan 1'),
          ('12 MONTHS', '$2,199', 'About $183 a month', 'Goes to $2,459 on Jan 1')]
PERK = 'One late-cancel fee waived every month you are locked in. [confirm]'

OFFERS = {
    'gift': dict(n='01', name='GIFT CARD BONUS', head=['GIVE THE GIFT', 'OF THE CLASS.'],
                 line='Buy a $100 gift card, get a $100 bonus gift card to give a friend.',
                 short='Buy $100, get a $100 bonus for a friend',
                 url='https://app.arketa.co/oakcliffpilates/pricing/checkout/wcQCbnFwzO4lzu0V9jMX',
                 fine='We email you the bonus code right after checkout. Code valid through [date]. Through Dec 1 only.',
                 cta='SHOP GIFT CARDS', photo='[PHOTO: gift card handoff at the front desk, warm light]',
                 ad=['GIVE $100.', 'GIVE $100 MORE.'], adline='Buy a $100 gift card, get a $100 bonus to gift a friend.',
                 b728='BUY A $100 GIFT CARD, GIFT A FRIEND $100 MORE.',
                 b320='GIVE $100, GIFT $100 MORE.'),
    'day': dict(n='02', name='10-CLASS PACK', head=['10 CLASSES.', '$150.'],
                line='10 classes for $150. Regularly $290. Any studio.',
                short='10 classes for $150, regularly $290',
                fine='Expires 90 days from purchase. One per person [confirm].',
                url='https://app.arketa.co/oakcliffpilates/pricing/checkout/Tf43tiF4VA7QEmjK7XTT',
                cta='GRAB THE PACK', photo='[PHOTO: midday class, sun through the windows]',
                ad=['10 CLASSES.', '$150.'], adline='Regularly $290. Any studio.',
                b728='10 CLASSES FOR $150. REG. $290. THRU 12/1.',
                b320='10 CLASSES, $150. THRU 12/1.'),
    'start': dict(n='03', name='NEW-CLIENT STARTER', head=['START', 'HERE.'],
                  line='1 week unlimited for $39 with code BLACKFRIDAY. New clients only.',
                  short='1 week unlimited, $39 with code BLACKFRIDAY',
                  fine='Unlimited classes at all 3 studios for 7 days.',
                  url='https://lp.oakcliffpilates.com/59unlimited',
                  bridge="Join by Dec 31 and keep today's membership rates for all of 2027.",
                  cta='START HERE', photo='[PHOTO: first-timer on the reformer with an instructor]',
                  ad=['START HERE.'], adline='1 week unlimited, $39. Code BLACKFRIDAY.',
                  b728='NEW? 1 WEEK UNLIMITED, $39. CODE BLACKFRIDAY.',
                  b320='$39 WEEK. CODE BLACKFRIDAY.'),
    'bundle': dict(n='04', name='GIFT BUNDLE', head=['WRAP', 'IT UP.'],
                   line='20 classes plus OCP grip socks, the hoodie and the tote. $400.',
                   short='20 classes + socks, hoodie and tote for $400',
                   fine='20 classes alone are regularly $560. Classes expire 12 months from purchase. Merch while supplies last.',
                   url='https://app.arketa.co/oakcliffpilates/pricing/checkout/RDpt4HDP8DAIVmBP1koF',
                   cta='SHOP THE BUNDLE', photo='[PHOTO: gift card and grip socks, wrapped, close crop]'),
    'unl': dict(n='05', name='ALL-STUDIO UNLIMITED', head=['UNLIMITED.', '$199/MO.'],
                line='All-Studio Unlimited for $199 a month. Commit to your first 3 months and it stays $199 after. Plus a $50 gift card.',
                short='$199/mo, stays $199 + a $50 gift card',
                fine='New members only. 3-month minimum commitment.',
                url='https://app.arketa.co/oakcliffpilates/pricing/checkout/DtAhCsd2DtIhVLNGaag6',
                cta='JOIN NOW', photo='[PHOTO: full class mid-movement, warm light]'),
}
ORDER = ['gift', 'day', 'start', 'bundle', 'unl']
ENDS = 'ENDS TUE 12/1 AT MIDNIGHT'

# =============================================================
# EMAIL SYSTEM (600px)
# =============================================================
EW = 600
CH = 0.6  # Montserrat avg char width in em


def est(text, size, width, lh=1.6):
    lines = max(1, math.ceil(len(text) * size * CH / width))
    return math.ceil(lines * size * lh)


def m_meta(send, subject, preview):
    h = 32 + est(subject, 15, 520, 1.4) + est(preview, 13, 520, 1.45) + 18 + 20
    inner = (f'<div style="background: {S2}; padding: 16px 40px; display: flex; flex-direction: column; gap: 6px; color: {B}">'
             f'{para("SENDS  " + send, 11, S7, 700, 1.4, "letter-spacing: 0.12em; text-transform: uppercase")}'
             f'<p style="margin: 0; {MO}; font-size: 15px; line-height: 1.4; color: {B}"><strong>Subject:</strong> {esc(subject)}</p>'
             f'<p style="margin: 0; {MO}; font-size: 13px; line-height: 1.45; color: {S7}"><strong>Preview:</strong> {esc(preview)}</p></div>')
    return inner, h


def m_label(n, text):
    return (f'<div style="background: {S8}; padding: 5px 40px">'
            f'{para(f"MODULE {n} · {text}", 10, S3, 700, 1.3, "letter-spacing: 0.2em")}</div>'), 23


def m_header(theme):
    tag = 'MEMBERS ONLY' if theme == 'li' else 'NOV 17 TO DEC 1'
    name = 'OAK CLIFF PILATES' if theme == 'li' else 'BLACK FRIDAY AT OCP'
    return (f'<div style="background: {B}; padding: 20px 40px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid {HAIR}">'
            f'<div style="display: flex; align-items: center; gap: 14px">{puck(56)}'
            f'<p style="margin: 0; {KH}; font-size: 24px; letter-spacing: 0.06em; color: {C}">{name}</p></div>'
            f'{para(tag, 11, G, 700, 1.2, "letter-spacing: 0.24em")}</div>'), 97


def m_hero(eb, lines, gold_from=1, ph=None, sub=None, bg=B, size=84):
    colors = [C] * gold_from + [G] * (len(lines) - gold_from)
    parts = [eyebrow(eb, G, 12, '0.24em'), head(lines, size, colors)]
    h = 48 + 15 + 18 + math.ceil(len(lines) * size * 0.86)
    if sub:
        parts.append(para(sub, 17, S2, 400, 1.6))
        h += 18 + est(sub, 17, 520)
    if ph:
        parts.append(photo(ph, 520, 300))
        h += 24 + 300
    h += 36
    return f'<div style="background: {bg}; padding: 48px 40px 36px; display: flex; flex-direction: column; gap: 18px">{"".join(parts)}</div>', h + 10


def m_text(paras, bg=B, color=S2, size=16, pad='0 40px 28px'):
    h = 28
    ps = []
    for p in paras:
        ps.append(para(p, size, color, 400, 1.6))
        h += est(p, size, 520) + 14
    return f'<div style="background: {bg}; padding: {pad}; display: flex; flex-direction: column; gap: 14px">{"".join(ps)}</div>', h


def m_rate():
    cell = lambda lab, val, col_: (f'<div style="flex: 1 1 0; padding: 20px 24px; display: flex; flex-direction: column; gap: 6px">'
                                   f'{para(lab, 11, S3, 700, 1.2, "letter-spacing: 0.22em")}'
                                   f'<p style="margin: 0; {KH}; font-size: 64px; line-height: 0.85; color: {col_}">{val}<span style="font-size: 26px">/MO</span></p></div>')
    return (f'<div style="background: {B}; padding: 0 40px 28px"><div style="display: flex; border: 1px solid {HAIR}">'
            f'{cell("NOW · YOURS TO KEEP", NOW_RATE, G)}<div style="width: 1px; background: {HAIR}"></div>{cell("FROM JAN 1, 2027", NEW_RATE, S3)}'
            f'</div>{para("All-Studio Unlimited", 12, S5, 600, 1.4, "margin-top: 10px; letter-spacing: 0.06em")}</div>'), 170


def m_ways(items):
    rows = []
    h = 28
    for n, t, d in items:
        rows.append(f'<div style="display: flex; gap: 18px; padding: 18px 0; border-top: 1px solid {HAIR}">'
                    f'<p style="margin: 0; {KH}; font-size: 40px; line-height: 0.9; color: {G}; width: 44px; flex-shrink: 0">{n}</p>'
                    f'<div style="display: flex; flex-direction: column; gap: 6px">'
                    f'<p style="margin: 0; {KH}; font-size: 26px; line-height: 1; letter-spacing: 0.02em; color: {C}">{esc(t)}</p>'
                    f'{para(d, 15, S2, 400, 1.55)}</div></div>')
        h += 36 + 26 + 6 + est(d, 15, 450, 1.55)
    return f'<div style="background: {B}; padding: 0 40px 28px">{"".join(rows)}</div>', h


def m_prepay():
    cards = []
    for i, (t, p, per, up) in enumerate(PREPAY):
        feat = i == 2
        border = f'3px solid {G}' if feat else f'1px solid {HAIR}'
        tag = chip('BEST VALUE', 11, G, B, '6px 10px') if feat else '<div style="height: 23px"></div>'
        cards.append(f'<div style="flex: 1 1 0; border: {border}; padding: 16px 14px; display: flex; flex-direction: column; gap: 8px">'
                     f'{tag}<p style="margin: 0; {KH}; font-size: 22px; letter-spacing: 0.04em; color: {C}">{t}</p>'
                     f'<p style="margin: 0; {KH}; font-size: 42px; line-height: 0.85; color: {G}">{p}</p>'
                     f'{para(per, 12, S2, 600, 1.4)}{para(up, 11, S5, 400, 1.4)}</div>')
    return (f'<div style="background: {B}; padding: 0 40px 28px; display: flex; flex-direction: column; gap: 12px">'
            f'{eyebrow("PREPAY ALL-STUDIO UNLIMITED AT TODAY’S PRICES", G, 11, "0.2em")}'
            f'<div style="display: flex; gap: 10px">{"".join(cards)}</div></div>'), 262


def m_perk(caveat=False):
    acc = f'<span style="{CV}; text-transform: none; color: {GW}; font-size: 40px"> on us.</span>' if caveat else ''
    return (f'<div style="background: {B}; padding: 0 40px 28px"><div style="background: {INK}; border: 1px solid {G}; padding: 24px; display: flex; flex-direction: column; gap: 10px">'
            f'{eyebrow("THE PERK", G, 11, "0.24em")}'
            f'<p style="margin: 0; {KH}; font-size: 36px; line-height: 0.9; color: {C}">One late-cancel fee waived. Every month.{acc}</p>'
            f'{para("For members who lock in. Doesn’t roll over. [confirm terms]", 13, S3, 400, 1.5)}</div></div>'), 196


def m_button(text, sub=None, bg=B, btn_bg=G, btn_fg=B, sub_color=S3):
    s = para(sub, 13, sub_color, 400, 1.5, 'text-align: center') if sub else ''
    return (f'<div style="background: {bg}; padding: 12px 40px 36px; display: flex; flex-direction: column; align-items: center; gap: 14px">'
            f'{button(text, 22, btn_bg, btn_fg, "18px 40px", 12, "align-self: center")}{s}</div>'), 104 + (34 if sub else 0)


def m_signoff(text, bg=B):
    return (f'<div style="background: {bg}; padding: 28px 40px; border-top: 1px solid {HAIR}">'
            f'<p style="margin: 0; {KH}; font-size: 34px; line-height: 0.9; text-align: center; color: {G}">{esc(text)}</p></div>'), 100


def m_footer(fine=None):
    f = para(fine, 11, S5, 400, 1.5, 'text-align: center') if fine else ''
    h = 236 + (est(fine, 11, 520, 1.5) + 14 if fine else 0)
    return (f'<div style="background: {B}; padding: 32px 40px 36px; display: flex; flex-direction: column; align-items: center; gap: 14px; border-top: 1px solid {HAIR}">'
            f'{puck(56)}{handle(G, 14)}'
            f'{para("Bishop Arts · Uptown · Lower Greenville", 12, S3, 600, 1.4, "letter-spacing: 0.06em; text-align: center")}'
            f'{f}{para("[Unsubscribe] · [Update preferences]", 11, S5, 400, 1.4, "text-align: center")}</div>'), h


def m_endstrip(text):
    return (f'<div style="background: {PK}; padding: 16px 40px">'
            f'<p style="margin: 0; {KH}; font-size: 28px; line-height: 1; letter-spacing: 0.06em; text-align: center; color: {B}">{esc(text)}</p></div>'), 60


def m_offer(o, with_photo=False, bg=C, extended=False):
    line = o['line'] if not extended else 'Buy a $100 gift card, get a $[XX] bonus gift card for a friend. Through Dec 24 [confirm].'
    fine = o['fine'] if not extended else 'Bonus card valid through [date].'
    parts = []
    h = 64
    if with_photo:
        parts.append(photo(o['photo'], 520, 260, B))
        h += 260 + 16
    parts.append(f'<div style="display: flex; align-items: baseline; gap: 14px"><p style="margin: 0; {KH}; font-size: 56px; line-height: 0.85; color: {GD}">{o["n"]}</p>'
                 f'<p style="margin: 0; {KH}; font-size: 22px; letter-spacing: 0.12em; color: {B}">{o["name"]}</p></div>')
    parts.append(head(o['head'], 52, [B, B], 0.88))
    parts.append(para(line, 17, B, 700, 1.45))
    parts.append(para(fine, 13, S7, 400, 1.5))
    h += 48 + 16 + math.ceil(2 * 52 * 0.88) + 16 + est(line, 17, 520, 1.45) + 16 + est(fine, 13, 520, 1.5) + 16
    if o.get('bridge'):
        parts.append(f'<p style="margin: 0; padding-top: 12px; border-top: 1px solid {GD}; {MO}; font-size: 13px; font-weight: 600; line-height: 1.5; color: {B}">{esc(o["bridge"])}</p>')
        h += 13 + est(o['bridge'], 13, 520, 1.5) + 16
    parts.append(button(o['cta'], 20, B, C, '16px 32px', 12, href=o.get('url', '#')))
    h += 52 + 6
    return (f'<div style="background: {bg}; padding: 32px 40px; display: flex; flex-direction: column; gap: 16px; border-bottom: 1px solid {S3}">{"".join(parts)}</div>'), h


def m_compact(o, with_btn=True, bg=C):
    btn = button(o['cta'], 15, B, C, '12px 18px', 10, 'align-self: center; flex-shrink: 0', href=o.get('url', '#')) if with_btn else ''
    return (f'<div style="background: {bg}; padding: 20px 40px; display: flex; align-items: center; gap: 18px; border-bottom: 1px solid {S3}">'
            f'<p style="margin: 0; {KH}; font-size: 44px; line-height: 0.85; color: {GD}; width: 52px; flex-shrink: 0">{o["n"]}</p>'
            f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 4px">'
            f'<p style="margin: 0; {KH}; font-size: 24px; letter-spacing: 0.04em; color: {B}">{o["name"]}</p>'
            f'{para(o["short"], 14, S7, 600, 1.4)}</div>{btn}</div>'), 104


BF_FINE = ('Black Friday offers run Nov 17, 2026 at 12:00am CT through Dec 1, 2026 at 11:59pm CT. '
           'Bonus gift card valid through [date]. 10-class pack expires 90 days from purchase, one per person. New-client starter: new clients only. '
           'Gift bundle classes expire 12 months from purchase, merch while supplies last. Unlimited: new members only, $199 a month with a 3-month minimum, '
           'rate stays $199 after. [refund policy]. Offers cannot be combined.')
LI_FINE = ('For active Oak Cliff Pilates members. Lock-in closes Dec 31, 2026 at 11:59pm CT. All-Studio Unlimited moves to $229 a month on Jan 1, 2027. '
           'Prepaid plans are charged in full at purchase. Late-cancel waiver: one per month while locked in [confirm terms].')


def email(title, modules, bg=B):
    h = sum(m[1] for m in modules) + 40
    inner = ''.join(m[0] for m in modules[:-1]) + spacer() + modules[-1][0]
    return page(title, EW, h, inner, bg, clip=False), h


BOARDS = []  # (page, row_title, filename, title, w, h, html)


def add(pg, rowt, fname, title, w, h, src):
    BOARDS.append((pg, rowt, fname, title, w, h, src))


# =============================================================
# LOCK-IN EMAILS
# =============================================================
R = 'Lock-In · Email (members only)'
mods = [m_label('01', 'HEADER · EVERY SEND'), m_header('li'),
        m_label('02', 'HERO · EYEBROW, 2-LINE HEADLINE, OPTIONAL PHOTO'),
        m_hero('[EYEBROW] · MEMBERS ONLY', ['[HEADLINE LINE 1]', '[LINE 2 IN GOLD]'], ph='[PHOTO: member mid-class on reformer, warm light]'),
        m_label('03', 'BODY COPY · 1 TO 3 SHORT PARAGRAPHS'), m_text(['[Body copy. Short, direct, speak to you as we. One idea per paragraph.]']),
        m_label('04', 'RATE BLOCK · NOW VS JAN 1'), m_rate(),
        m_label('05', 'NUMBERED LIST · 2 TO 3 ITEMS'), m_ways([('01', '[ITEM TITLE]', '[One line of detail.]'), ('02', '[ITEM TITLE]', '[One line of detail.]')]),
        m_label('06', 'PREPAY CARDS · 3 / 6 / 12'), m_prepay(),
        m_label('07', 'PERK CALLOUT'), m_perk(),
        m_label('08', 'BUTTON · ONE PER SEND'), m_button('[BUTTON LABEL]', '[Optional line under the button]'),
        m_label('09', 'SIGN-OFF LINE'), m_signoff('[SIGN-OFF LINE]'),
        m_label('10', 'FOOTER · EVERY SEND'), m_footer(LI_FINE)]
src, h = email('Lock-In email template', mods)
add('lockin', R, 'Main.dc.html', 'Lock-In · Email template (modules)', EW, h, src)

mods = [m_meta('Tue Nov 24 · Current members only', 'Your rate. Locked.', 'Prices go up January 1. Yours doesn’t have to.'),
        m_header('li'),
        m_hero('MEMBERS ONLY · LOCK IN BY DEC 31', ['YOUR RATE.', 'LOCKED.'], ph='[PHOTO: member mid-class on reformer, warm light]'),
        m_text(['You showed up all year. This is our thank-you.',
                'On January 1, All-Studio Unlimited goes from $209 to $229 a month. Choose your membership before December 31 and you keep $209 through all of 2027.']),
        m_rate(),
        m_ways([('01', 'STAY MONTHLY', 'Choose your membership before Dec 31 and your rate holds through Dec 31, 2027.'),
                ('02', 'PREPAY', '3, 6 or 12 months of All-Studio Unlimited at today’s prices.')]),
        m_text(['Home Studio Unlimited ($189) and Unlimited Couples ($359) lock the same way. 4, 8 and 12-class memberships go up $10 a month on January 1.'], size=13, color=S3),
        m_button('LOCK IN MY RATE', 'Or ask the front desk next time you’re in.'),
        m_signoff('SAME STUDIO. SAME RATE. ALL OF 2027.'),
        m_footer(LI_FINE)]
src, h = email('L1 Your rate. Locked.', mods)
add('lockin', R, 'LI-email-L1.dc.html', 'L1 · Nov 24 · Your rate. Locked.', EW, h, src)

mods = [m_meta('Tue Dec 8 · Current members only', '3, 6 or 12 months. Your call.', 'Prepay at today’s prices and get a late-cancel fee waived every month.'),
        m_header('li'),
        m_hero('MEMBERS ONLY · YOUR OPTIONS', ['PICK YOUR', 'LOCK.'], ph='[PHOTO: two members side by side on reformers, mid-movement]'),
        m_text(['Prices go up in January. Yours doesn’t have to. Here’s every way to keep today’s rate, laid out simple.']),
        m_prepay(),
        m_ways([('', 'RATHER STAY MONTHLY?', 'Choose your membership before Dec 31 and $209 a month holds through 2027.')]),
        m_perk(caveat=True),
        m_button('SEE MY OPTIONS', LOCK_URL),
        m_signoff('YOU SHOWED UP ALL YEAR. KEEP YOUR RATE.'),
        m_footer(LI_FINE)]
src, h = email('L2 Your options', mods)
add('lockin', R, 'LI-email-L2.dc.html', 'L2 · Dec 8 · Prepay options + perk', EW, h, src)

mods = [m_meta('Tue Dec 22 · Current members only', 'One week left.', 'Lock in $209 before December 31. After that, it’s $229.'),
        m_header('li'),
        m_hero('MEMBERS ONLY · DEADLINE DEC 31', ['ONE WEEK', 'LEFT.'], ph='[PHOTO: member checking in at the front desk, warm light]'),
        m_text(['Quick one from us. Your rate holds only if you lock in by December 31.',
                'Stay monthly or prepay. It takes a minute online or at the front desk.']),
        m_rate(),
        m_button('LOCK IN NOW', LOCK_URL),
        m_signoff('LOCK IN BY DEC 31.'),
        m_footer(LI_FINE)]
src, h = email('L3 One week left', mods)
add('lockin', R, 'LI-email-L3.dc.html', 'L3 · Dec 22 · One week left', EW, h, src)

mods = [m_meta('Wed Dec 30 · Current members only', 'Last day tomorrow.', 'Lock in by 11:59pm Dec 31 and keep $209 for all of 2027.'),
        m_header('li'),
        m_hero('MEMBERS ONLY', ['LAST DAY', 'TOMORROW.'], size=96),
        m_text(['Lock in by 11:59pm on Thursday, December 31 and keep $209 a month for all of 2027. On January 1 it’s $229.']),
        m_button('LOCK IN MY RATE'),
        m_footer(LI_FINE)]
src, h = email('L4 Last day tomorrow', mods)
add('lockin', R, 'LI-email-L4.dc.html', 'L4 · Dec 30 · Last day tomorrow', EW, h, src)

# =============================================================
# LOCK-IN SOCIAL
# =============================================================
R = 'Lock-In · Social (members who follow us)'


def li_top(left, right, size=22):
    return row([eyebrow(left, G, size), eyebrow(right, S3, size)])


def li_rate_strip(size=44):
    return row([f'<p style="margin: 0; {KH}; font-size: {size}px; line-height: 1; color: {G}">NOW {NOW_RATE}/MO</p>',
                f'<p style="margin: 0; {KH}; font-size: {size}px; line-height: 1; color: {S3}">JAN 1 {NEW_RATE}/MO</p>'],
               24, 'center', 'flex-start', f'padding: 22px 28px; border: 1px solid {HAIR}; align-self: flex-start; gap: 40px')


inner = (frame() + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; gap: 34px; padding: 84px 84px 80px">'
         + li_top('MEMBERS ONLY', '2027 RATE LOCK')
         + photo('[PHOTO: member mid-class on reformer, warm light]', '100%', 470)
         + head(['YOUR RATE.', 'LOCKED.'], 168, [C, G])
         + para('Prices go up in January. Yours doesn’t have to.', 36, S2, 500, 1.3)
         + spacer()
         + row([col([f'<p style="margin: 0; {KH}; font-size: 48px; line-height: 1; color: {G}">LOCK IN BY DEC 31</p>', handle(S3, 22)], 10), puck(124)], 24, 'flex-end')
         + '</div>')
add('lockin', R, 'LI-post-announce.dc.html', 'Announcement post · 1080×1350', 1080, 1350, page('Lock-In announcement post', 1080, 1350, inner, B))

inner = (video('studio', '100%', 820, G, 'border-width: 0 0 3px 0')
         + frame(36)
         + f'<div style="position: relative; display: flex; flex-direction: column; gap: 30px; padding: 48px 84px 250px; flex: 1 1 auto">'
         + eyebrow('MEMBERS ONLY · 2027 RATE LOCK', G, 24)
         + head(['YOUR RATE.', 'LOCKED.'], 160, [C, G])
         + para('Prices go up in January. Yours doesn’t have to.', 38, S2, 500, 1.3)
         + li_rate_strip(40)
         + spacer()
         + row([sticker(f'[LINK STICKER: {LOCK_URL}]', 600, 'align-self: auto'), puck(120)], 24, 'center')
         + '</div>')
add('lockin', R, 'LI-story-announce.dc.html', 'Announcement story · 1080×1920', 1080, 1920, page('Lock-In announcement story', 1080, 1920, inner, B))


def li_slide(n, body, title):
    return (frame() + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; gap: 36px; padding: 84px">'
            + li_top('MEMBERS ONLY · RATE LOCK', f'{n:02d} / 04') + body + '</div>')


body = (head(["WHAT'S", 'CHANGING.'], 190, [C, G])
        + para('On January 1, 2027, All-Studio Unlimited goes up. Members who lock in keep today’s rate for all of 2027.', 36, S2, 500, 1.35)
        + spacer()
        + col([row([para('NOW', 26, S3, 700, 1, 'letter-spacing: 0.24em; width: 200px'), f'<p style="margin: 0; {KH}; font-size: 150px; line-height: 0.85; color: {G}">{NOW_RATE}<span style="font-size: 54px">/MO</span></p>'], 30, 'baseline', 'flex-start'),
               f'<div style="height: 1px; background: {HAIR}"></div>',
               row([para('JAN 1', 26, S3, 700, 1, 'letter-spacing: 0.24em; width: 200px'), f'<p style="margin: 0; {KH}; font-size: 150px; line-height: 0.85; color: {S3}">{NEW_RATE}<span style="font-size: 54px">/MO</span></p>'], 30, 'baseline', 'flex-start')], 28)
        + row([para('Swipe for your options  →', 26, S3, 600), handle(G, 22)], 24, 'center'))
add('lockin', R, 'LI-carousel-1.dc.html', "Carousel 1 · What's changing", 1080, 1350, page('Lock-In carousel 1', 1080, 1350, li_slide(1, body, ''), B))

opt_rows = [('STAY MONTHLY', '$209/MO', 'Choose your membership by Dec 31.')] + [(t, p, per) for t, p, per, _ in PREPAY]
rows_html = ''.join(
    f'<div style="display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 26px 0; border-top: 1px solid {HAIR}">'
    f'<div style="display: flex; flex-direction: column; gap: 8px"><p style="margin: 0; {KH}; font-size: 54px; line-height: 0.9; color: {C}">{t}</p>{para(d, 26, S3, 500, 1.3)}</div>'
    f'<p style="margin: 0; {KH}; font-size: 92px; line-height: 0.85; color: {G}">{p}</p></div>' for t, p, d in opt_rows)
body = (head(['YOUR', 'OPTIONS.'], 170, [C, G]) + f'<div style="display: flex; flex-direction: column">{rows_html}</div>'
        + spacer() + row([para('Prepay is All-Studio Unlimited, all 3 studios.', 24, S3, 500), handle(G, 22)], 24, 'center'))
add('lockin', R, 'LI-carousel-2.dc.html', 'Carousel 2 · Your options', 1080, 1350, page('Lock-In carousel 2', 1080, 1350, li_slide(2, body, ''), B))

body = (photo('[PHOTO: member laughing between sets, close crop]', '100%', 430)
        + head(['THE', 'PERK.'], 170, [C, G])
        + f'<p style="margin: 0; {KH}; font-size: 74px; line-height: 0.88; color: {C}">One late-cancel fee waived. Every month.<span style="{CV}; text-transform: none; color: {GW}; font-size: 80px"> on us.</span></p>'
        + spacer() + row([para('For members who lock in. [confirm terms]', 26, S3, 500), handle(G, 22)], 24, 'center'))
add('lockin', R, 'LI-carousel-3.dc.html', 'Carousel 3 · The perk', 1080, 1350, page('Lock-In carousel 3', 1080, 1350, li_slide(3, body, ''), B))

body = (head(['LOCK IN', 'BY DEC 31.'], 200, [C, G])
        + para('Same studio. Same rate. All of 2027.', 44, C, 600, 1.25)
        + spacer()
        + row([col([para(LOCK_URL, 30, G, 700, 1.3), para('or ask the front desk.', 30, S3, 500, 1.3), handle(S3, 22)], 12), puck(200)], 24, 'flex-end'))
add('lockin', R, 'LI-carousel-4.dc.html', 'Carousel 4 · Lock in by Dec 31', 1080, 1350, page('Lock-In carousel 4', 1080, 1350, li_slide(4, body, ''), B))

R = 'Lock-In · Countdown stories'
for days, date, big2 in [(14, 'Thu Dec 17', 'DAYS LEFT'), (7, 'Thu Dec 24', 'DAYS LEFT'), (1, 'Wed Dec 30', 'DAY LEFT')]:
    line = 'Last day is tomorrow. Lock in by 11:59pm Dec 31.' if days == 1 else 'to lock your rate. Deadline Dec 31.'
    inner = (frame() + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; gap: 32px; padding: 250px 96px 250px">'
             + eyebrow('MEMBERS ONLY · 2027 RATE LOCK', G, 24)
             + f'<p style="margin: 0; {KH}; font-size: 560px; line-height: 0.78; letter-spacing: -0.03em; color: {G}">{days}</p>'
             + f'<p style="margin: 0; {KH}; font-size: 150px; line-height: 0.84; color: {C}">{big2}</p>'
             + para(line, 40, S2, 500, 1.3)
             + li_rate_strip(40)
             + spacer()
             + row([sticker(f'[LINK STICKER: {LOCK_URL}]', 600, 'align-self: auto'), puck(120)], 24, 'center')
             + '</div>')
    add('lockin', R, f'LI-story-countdown-{days}.dc.html', f'Countdown story · {days} {"day" if days == 1 else "days"} · {date}', 1080, 1920, page(f'Lock-In countdown {days}', 1080, 1920, inner, B))

R = 'Lock-In · In-studio print'
inner = (frame(24) + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; gap: 26px; padding: 64px 64px 56px">'
         + row([eyebrow('MEMBERS ONLY', G, 16), eyebrow('2027 RATE LOCK', S3, 16)])
         + head(['YOUR RATE.', 'LOCKED.'], 116, [C, G])
         + para('Prices go up in January. Yours doesn’t have to.', 22, S2, 500, 1.4)
         + li_rate_strip(34)
         + row([col([f'<p style="margin: 0; {KH}; font-size: 30px; color: {C}">01 · STAY MONTHLY</p>', para('Choose your membership by Dec 31.', 18, S3, 500, 1.4),
                     f'<p style="margin: 0; {KH}; font-size: 30px; color: {C}">02 · PREPAY 3, 6 OR 12</p>', para('$599 · $1,159 · $2,199 at today’s prices.', 18, S3, 500, 1.4),
                     f'<p style="margin: 0; {KH}; font-size: 30px; color: {C}">THE PERK</p>', para(PERK, 18, S3, 500, 1.4)], 8, 'flex: 1 1 auto'),
                qr(230, f'[QR: {LOCK_URL}]')], 36, 'flex-start')
         + spacer()
         + row([para('Scan it or ask us at the desk.', 22, G, 700, 1.3), puck(96)], 24, 'center')
         + '</div>')
add('lockin', R, 'LI-print-sign.dc.html', 'Front desk sign · 8.5×11 (816×1056)', 816, 1056, page('Lock-In front desk sign', 816, 1056, inner, B))

inner = (frame(16) + f'<div style="position: relative; flex: 1 1 auto; display: flex; gap: 28px; padding: 36px 36px 32px; align-items: stretch">'
         + col([eyebrow('MEMBERS ONLY', G, 12),
                head(['YOUR RATE.', 'LOCKED.'], 66, [C, G]),
                para('Lock in by Dec 31. Keep $209 a month for all of 2027.', 15, S2, 500, 1.4),
                spacer(), row([puck(52), handle(S3, 12)], 12, 'center', 'flex-start')], 14, 'flex: 1 1 auto')
         + col([qr(230, f'[QR: {LOCK_URL}]'), para('Scan to lock in', 13, G, 700, 1.2, 'text-align: center; letter-spacing: 0.1em; text-transform: uppercase')], 10)
         + '</div>')
add('lockin', R, 'LI-print-card.dc.html', '4×6 card (576×384)', 576, 384, page('Lock-In 4x6 card', 576, 384, inner, B))

# =============================================================
# BLACK FRIDAY EMAILS
# =============================================================
R = 'Black Friday · Email'
mods = [m_label('01', 'HEADER · EVERY SEND'), m_header('bf'),
        m_label('02', 'HERO · EYEBROW, 2-LINE HEADLINE, SUB, OPTIONAL PHOTO'),
        m_hero('[EYEBROW] · NOV 17 TO DEC 1', ['[HEADLINE LINE 1]', '[LINE 2 IN GOLD]'], sub='[One or two short lines. Bold, punchy.]', ph='[PHOTO: class mid-movement, warm light]'),
        m_label('03', 'END-DATE STRIP · THE ONE PINK MOMENT'), m_endstrip('ENDS TUESDAY, DEC 1 AT MIDNIGHT'),
        m_label('04', 'OFFER BLOCK · NUMBER, NAME, HEADLINE, PRICE, FINE PRINT, BUTTON'), m_offer(OFFERS['gift'], with_photo=True),
        m_label('05', 'OFFER BLOCK + BRIDGE LINE · STARTER ONLY'), m_offer(OFFERS['start']),
        m_label('06', 'COMPACT ROW · ONE LINE + ONE BUTTON'), m_compact(OFFERS['day']),
        m_label('07', 'FOOTER · EVERY SEND, WITH FINE PRINT'), m_footer(BF_FINE)]
src, h = email('Black Friday email template', mods)
add('bf', R, 'BF-email-template.dc.html', 'Black Friday · Email template (modules)', EW, h, src)

AUD = 'Non-members, lapsed clients, intro buyers who didn’t convert, full list for gift cards'
mods = [m_meta('Tue Nov 17 · Full list: non-members, lapsed clients, intro buyers, gift buyers', 'Early access: Black Friday at OCP', 'You’re first. Five offers, live now through Dec 1.'),
        m_header('bf'),
        m_hero('EARLY ACCESS · NOV 17 TO DEC 1', ['EARLY ACCESS', 'TO BLACK FRIDAY.'], sub='You’re on our list, so you go first. Every Black Friday offer is live right now, ten days before everyone else starts shopping. Gift it, start it, or stock up.', ph='[PHOTO: full class mid-movement, warm light]', size=72),
        m_endstrip('LIVE NOW THROUGH TUE, DEC 1'),
        m_offer(OFFERS['gift'], with_photo=True), m_offer(OFFERS['day']), m_offer(OFFERS['start']), m_offer(dict(OFFERS['bundle'], photo='[PHOTO: merch tote]'), with_photo=True), m_offer(OFFERS['unl']),
        m_footer(BF_FINE)]
src, h = email('Early access to Black Friday', mods, C)
add('bf', R, 'BF-email-EA.dc.html', 'EA · Nov 17 · Early access', EW, h, src)

mods = [m_meta('Fri Nov 20 · Full list, gift buyers', 'Give $100. Then give $100 more.', 'Buy a gift card, get a $100 bonus to gift a friend. Through Dec 1.'),
        m_header('bf'),
        m_hero('BLACK FRIDAY AT OCP · GIFTS', ['GIVE $100.', 'GIVE $100 MORE.'], sub='Give the gift of the class they keep talking about. Buy a $100 gift card and we email you a code for a bonus gift card, up to $100, to give a friend. Got someone who’s all in? Wrap up 20 classes and the merch.', ph='[PHOTO: gift card handoff at the front desk, warm light]', size=72),
        m_endstrip('THROUGH TUE, DEC 1 AT MIDNIGHT'),
        m_offer(OFFERS['gift']), m_offer(dict(OFFERS['bundle'], photo='[PHOTO: merch tote]'), with_photo=True),
        m_footer(BF_FINE)]
src, h = email('Gift focus', mods, C)
add('bf', R, 'BF-email-gifts.dc.html', 'Nov 20 · Give $100. Give $100 more.', EW, h, src)

mods = [m_meta('Mon Nov 23 · Non-members, lapsed clients, intro buyers who didn’t convert', '$199 unlimited. And it stays $199.', 'New members: commit to 3 months, keep $199 after. Plus a $50 gift card.'),
        m_header('bf'),
        m_hero('BLACK FRIDAY AT OCP · NEW MEMBERS', ['UNLIMITED.', '$199/MO.'], sub='Every class, all 3 studios. Commit to your first 3 months and your rate stays $199 after that. We’ll throw in a $50 gift card too.', ph='[PHOTO: full class mid-movement, warm light]', size=110),
        m_endstrip('THROUGH TUE, DEC 1 AT MIDNIGHT'),
        m_offer(OFFERS['unl']),
        m_text(['Not ready to commit? Start with a week.'], bg=C, color=B, size=16, pad='28px 40px 0'),
        m_offer(OFFERS['start']),
        m_footer(BF_FINE)]
src, h = email('Unlimited focus', mods, C)
add('bf', R, 'BF-email-unl.dc.html', 'Nov 23 · $199 unlimited', EW, h, src)

mods = [m_meta('Wed Nov 25 · ' + AUD, 'Black Friday is Friday.', 'Every offer is already live. Through Tuesday, Dec 1.'),
        m_header('bf'),
        m_hero('OAK CLIFF PILATES · NOV 17 TO DEC 1', ['BLACK FRIDAY', 'IS FRIDAY.'], sub='Early access is open. All five offers are live right now through Tuesday, Dec 1. Black Friday at OCP is for the people you’re bringing in.', ph='[PHOTO: full class mid-movement, warm light]', size=72),
        m_compact(OFFERS['gift'], False), m_compact(OFFERS['day'], False), m_compact(OFFERS['start'], False), m_compact(OFFERS['bundle'], False), m_compact(OFFERS['unl'], False),
        m_text([OFFERS['start']['bridge']], bg=C, color=B, size=13, pad='20px 40px 8px'),
        m_button('SHOP THE DEALS', 'Five offers. One page.', C, B, C, S7),
        m_endstrip('LIVE NOW THROUGH TUE, DEC 1'),
        m_footer(BF_FINE)]
src, h = email('B1 Black Friday starts Friday', mods, C)
add('bf', R, 'BF-email-B1.dc.html', 'B1 · Nov 25 · Black Friday is Friday', EW, h, src)

mods = [m_meta('Fri Nov 27 · ' + AUD, 'It’s Black Friday.', 'A $100 bonus to gift, 10 classes for $150, unlimited for $199. Through Dec 1.'),
        m_header('bf'),
        m_hero('BLACK FRIDAY AT OCP · NOV 17 TO DEC 1', ["IT'S", 'BLACK FRIDAY.'], sub='Five ways in, live through Tuesday, Dec 1. Gift it, start it, or stock up.', size=80),
        m_endstrip('ENDS TUESDAY, DEC 1 AT MIDNIGHT'),
        m_offer(OFFERS['gift'], with_photo=True), m_offer(OFFERS['day']), m_offer(OFFERS['start']), m_offer(dict(OFFERS['bundle'], photo='[PHOTO: merch tote]'), with_photo=True), m_offer(OFFERS['unl']),
        m_footer(BF_FINE)]
src, h = email('B2 It is live', mods, C)
add('bf', R, 'BF-email-B2.dc.html', 'B2 · Nov 27 · It’s Black Friday', EW, h, src)

mods = [m_meta('Sun Nov 29 · Non-members, lapsed clients, intro buyers who didn’t convert', 'Never trained with us? Start here.', 'Two ways in this weekend. Both end Tuesday, Dec 1 at midnight.'),
        m_header('bf'),
        m_hero('BLACK FRIDAY AT OCP', ['START', 'HERE.'], sub='Real Dallas people. Loud music. Instructors who actually see your form. If you’ve been meaning to try OCP, this is the weekend.', ph='[PHOTO: first-timer on the reformer with an instructor]', size=110),
        m_offer(OFFERS['start']),
        m_offer(OFFERS['day'], with_photo=True),
        m_endstrip('BOTH END TUESDAY, DEC 1'),
        m_footer(BF_FINE)]
src, h = email('B3 Start here', mods, C)
add('bf', R, 'BF-email-B3.dc.html', 'B3 · Nov 29 · Starter + 10-class pack', EW, h, src)

mods = [m_meta('Mon Nov 30 · ' + AUD, 'One more day.', 'Every Black Friday offer ends tomorrow at midnight.'),
        m_header('bf'),
        m_hero('BLACK FRIDAY AT OCP · CYBER MONDAY', ['ONE MORE', 'DAY.'], sub='Black Friday at OCP ends tomorrow, Tuesday Dec 1, at midnight. Stock up before it’s gone.', size=110),
        m_endstrip('ENDS TOMORROW, DEC 1 AT MIDNIGHT'),
        m_offer(OFFERS['day'], with_photo=True), m_offer(dict(OFFERS['bundle'], photo='[PHOTO: gift card and grip socks, wrapped, close crop]'), with_photo=True),
        m_compact(OFFERS['gift']), m_compact(OFFERS['start']), m_compact(OFFERS['unl']),
        m_footer(BF_FINE)]
src, h = email('Cyber Monday', mods, C)
add('bf', R, 'BF-email-cyber.dc.html', 'Nov 30 · Cyber Monday · One more day', EW, h, src)

mods = [m_meta('Tue Dec 1 · ' + AUD, 'Ends tonight.', 'Midnight. Then it’s gone.'),
        m_header('bf'),
        m_hero('BLACK FRIDAY AT OCP · LAST DAY', ['ENDS', 'TONIGHT.'], sub='At midnight, Black Friday at OCP is done. One line each. Pick yours.', size=110),
        m_compact(OFFERS['gift']), m_compact(OFFERS['day']), m_compact(OFFERS['start']), m_compact(OFFERS['bundle']), m_compact(OFFERS['unl']),
        m_text([OFFERS['start']['bridge']], bg=C, color=B, size=13, pad='20px 40px 20px'),
        m_endstrip('ENDS TONIGHT AT 11:59PM CT'),
        m_footer(BF_FINE)]
src, h = email('B4 Ends tonight', mods, C)
add('bf', R, 'BF-email-B4.dc.html', 'B4 · Dec 1 · Ends tonight', EW, h, src)


# =============================================================
# BLACK FRIDAY SOCIAL
# =============================================================
R = 'Black Friday · Teaser + launch + carousel'


def bf_top(left='BLACK FRIDAY AT OCP', right='NOV 17 TO DEC 1', c1=G, c2=S3, size=22):
    return row([eyebrow(left, c1, size), eyebrow(right, c2, size)])


inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 30px; padding: 84px">'
         + bf_top()
         + spacer()
         + head(['BLACK FRIDAY', 'AT OCP.'], 150, [C, C])
         + f'<p style="margin: 0; {KH}; font-size: 330px; line-height: 0.78; letter-spacing: -0.03em; color: {G}">EARLY.</p>'
         + row([para('Early access opens tomorrow.', 40, S2, 600, 1.2), chip('NOV 17', 34)], 24, 'center', 'flex-start')
         + spacer()
         + row([handle(S3, 24), puck(130)], 24, 'flex-end')
         + '</div>')
add('bf', R, 'BF-post-teaser.dc.html', 'Teaser post · Nov 16 · 1080×1350', 1080, 1350, page('Black Friday teaser post', 1080, 1350, inner, B))

inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 30px; padding: 250px 84px">'
         + bf_top(size=24)
         + spacer()
         + head(['BLACK FRIDAY', 'AT OCP.'], 160, [C, C])
         + f'<p style="margin: 0; {KH}; font-size: 340px; line-height: 0.78; letter-spacing: -0.03em; color: {G}">EARLY.</p>'
         + row([para('Early access opens tomorrow.', 44, S2, 600, 1.2), chip('NOV 17', 36)], 24, 'center', 'flex-start')
         + spacer()
         + row([sticker('[REMINDER STICKER: Black Friday at OCP]', 620, 'align-self: auto'), puck(120)], 24, 'center')
         + '</div>')
add('bf', R, 'BF-story-teaser.dc.html', 'Teaser story · Nov 16 · 1080×1920', 1080, 1920, page('Black Friday teaser story', 1080, 1920, inner, B))

rows_html = ''.join(
    f'<div style="display: flex; align-items: center; gap: 28px; padding: 18px 0; border-top: 1px solid {HAIR}">'
    f'<p style="margin: 0; {KH}; font-size: 90px; line-height: 0.8; color: {G}; width: 110px; flex-shrink: 0">{OFFERS[k]["n"]}</p>'
    f'<div style="display: flex; flex-direction: column; gap: 4px"><p style="margin: 0; {KH}; font-size: 50px; line-height: 0.9; color: {C}">{OFFERS[k]["name"]}</p>'
    f'{para(OFFERS[k]["short"], 26, S3, 500, 1.3)}</div></div>' for k in ORDER)
inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 30px; padding: 84px">'
         + bf_top()
         + head(['EARLY ACCESS.', 'FIVE WAYS IN.'], 130, [C, G])
         + f'<div style="display: flex; flex-direction: column">{rows_html}</div>'
         + spacer()
         + row([chip('ENDS TUE 12/1 AT MIDNIGHT', 30), puck(120)], 24, 'center')
         + '</div>')
add('bf', R, 'BF-post-launch.dc.html', 'Launch post · Nov 17 · 01 to 05', 1080, 1350, page('Black Friday launch post', 1080, 1350, inner, B))

inner = (photo('[PHOTO: class mid-movement, warm light, close crop]', '100%', 640, G, 'border-width: 0 0 3px 0')
         + f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 26px; padding: 56px 84px 84px">'
         + bf_top(right='01 / 06')
         + head(['BLACK FRIDAY', 'AT OCP.'], 160, [C, G])
         + row([para('Nov 17 to Dec 1. Five offers. Swipe  →', 34, S2, 600, 1.2), chip('EARLY ACCESS', 30)], 24, 'center')
         + spacer() + row([handle(S3, 22), puck(110)], 24, 'flex-end')
         + '</div>')
add('bf', R, 'BF-carousel-1.dc.html', 'Carousel 1 · Cover', 1080, 1350, page('Black Friday carousel cover', 1080, 1350, inner, B))

for i, k in enumerate(ORDER):
    o = OFFERS[k]
    dark = i % 2 == 1
    bg, fg, sub, num = (B, C, S3, G) if dark else (C, B, S7, GD)
    bridge = (f'<p style="margin: 0; padding-top: 18px; border-top: 2px solid {num}; {MO}; font-size: 28px; font-weight: 600; line-height: 1.35; color: {fg}">{esc(o["bridge"])}</p>') if o.get('bridge') else ''
    inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 30px; padding: 84px">'
             + bf_top(right=f'0{i + 2} / 06', c1=num, c2=sub)
             + f'<p style="margin: 0; {KH}; font-size: 330px; line-height: 0.76; letter-spacing: -0.03em; color: {num}">{o["n"]}</p>'
             + eyebrow(o['name'], fg, 28, '0.16em')
             + head(o['head'], 110 if len(o['head'][0]) > 12 else 130, [fg, fg])
             + para(o['line'], 38, fg, 700, 1.3)
             + para(o['fine'], 26, sub, 500, 1.4)
             + bridge
             + spacer()
             + row([chip(ENDS, 26), puck(110)], 24, 'center')
             + '</div>')
    add('bf', R, f'BF-carousel-{i + 2}.dc.html', f'Carousel {i + 2} · {o["n"]} {o["name"].title()}', 1080, 1350, page(f'Black Friday carousel {i + 2}', 1080, 1350, inner, bg))

R = 'Black Friday · One post + one story per offer'
for i, k in enumerate(ORDER):
    o = OFFERS[k]
    dark = i % 2 == 1
    bg, fg, sub, num = (B, C, S3, G) if dark else (C, B, S7, GD)
    bridge = para(o['bridge'], 24, fg, 600, 1.35) if o.get('bridge') else ''
    inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 24px; padding: 72px">'
             + bf_top(c1=num, c2=sub)
             + f'<div style="position: relative">{photo(o["photo"], "100%", 500, num)}'
             + f'<p style="position: absolute; left: 24px; bottom: -40px; margin: 0; {KH}; font-size: 220px; line-height: 0.8; color: {num}">{o["n"]}</p></div>'
             + f'<div style="height: 16px"></div>'
             + head(o['head'], 116, [fg, fg])
             + para(o['line'], 34, fg, 700, 1.3)
             + bridge
             + spacer()
             + row([row([button(o['cta'], 30, B if not dark else G, C if not dark else B, '22px 34px', 12), chip('ENDS TUE 12/1', 24)], 18, 'center', 'flex-start'), puck(100)], 24, 'center')
             + '</div>')
    add('bf', R, f'BF-post-{k}.dc.html', f'Post · {o["n"]} {o["name"].title()}', 1080, 1350, page(f'Black Friday post {o["name"]}', 1080, 1350, inner, bg))

for i, k in enumerate(ORDER):
    o = OFFERS[k]
    dark = i % 2 == 1
    bg, fg, sub, num = (B, C, S3, G) if dark else (C, B, S7, GD)
    bridge = para(o['bridge'], 28, fg, 600, 1.35) if o.get('bridge') else ''
    inner = ((video('classloop', '100%', 760, num, 'border-width: 0 0 3px 0') if k == 'day' else photo('[PHOTO: merch hoodie]' if k == 'bundle' else o['photo'], '100%', 760, num, 'border-width: 0 0 3px 0'))
             + f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 24px; padding: 40px 84px 250px">'
             + row([f'<p style="margin: 0; {KH}; font-size: 150px; line-height: 0.8; color: {num}">{o["n"]}</p>', eyebrow('BLACK FRIDAY AT OCP', sub, 24)], 24, 'flex-end')
             + head(o['head'], 104 if len(o['head'][0]) > 12 else 128, [fg, fg])
             + para(o['line'], 38, fg, 700, 1.3)
             + bridge
             + chip('ENDS TUE 12/1 AT MIDNIGHT', 28)
             + spacer()
             + row([sticker(f'[LINK STICKER: {o["cta"].title()}]', 600, 'align-self: auto'), puck(110)], 24, 'center')
             + '</div>')
    add('bf', R, f'BF-story-{k}.dc.html', f'Story · {o["n"]} {o["name"].title()}', 1080, 1920, page(f'Black Friday story {o["name"]}', 1080, 1920, inner, bg))

R = 'Black Friday · Ends tonight + reel cover'
short_rows = ''.join(
    f'<div style="display: flex; align-items: baseline; gap: 24px; padding: 18px 0; border-top: 1px solid {HAIR}">'
    f'<p style="margin: 0; {KH}; font-size: 64px; line-height: 0.8; color: {G}; width: 84px">{OFFERS[k]["n"]}</p>'
    f'<p style="margin: 0; {KH}; font-size: 48px; line-height: 0.9; color: {C}">{OFFERS[k]["name"]}</p></div>' for k in ORDER)
inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 30px; padding: 84px">'
         + bf_top(right='TUE DEC 1')
         + head(['ENDS', 'TONIGHT.'], 200, [C, G])
         + chip('MIDNIGHT. THEN IT’S GONE.', 34)
         + f'<div style="display: flex; flex-direction: column">{short_rows}</div>'
         + spacer() + row([handle(S3, 24), puck(110)], 24, 'flex-end')
         + '</div>')
add('bf', R, 'BF-post-ends-tonight.dc.html', 'Ends tonight post · Dec 1', 1080, 1350, page('Black Friday ends tonight post', 1080, 1350, inner, B))

inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 30px; padding: 250px 84px">'
         + bf_top(right='TUE DEC 1', size=24)
         + head(['ENDS', 'TONIGHT.'], 230, [C, G])
         + chip('MIDNIGHT. THEN IT’S GONE.', 36)
         + f'<div style="display: flex; flex-direction: column">{short_rows}</div>'
         + spacer()
         + row([sticker('[LINK STICKER: Shop the deals]', 600, 'align-self: auto'), puck(110)], 24, 'center')
         + '</div>')
add('bf', R, 'BF-story-ends-tonight.dc.html', 'Ends tonight story · Dec 1', 1080, 1920, page('Black Friday ends tonight story', 1080, 1920, inner, B))

o = OFFERS['gift']
inner = (photo('[PHOTO: gift card handoff at the front desk, warm light, full bleed]', '100%', 1920, G, 'position: absolute; inset: 0; border-width: 0')
         + f'<div aria-hidden="true" style="position: absolute; left: 0; right: 0; bottom: 0; height: 1100px; background: linear-gradient(to top, rgba(11,11,11,0.92), rgba(11,11,11,0) 100%)"></div>'
         + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; justify-content: flex-end; gap: 28px; padding: 285px 84px 300px">'
         + eyebrow('BLACK FRIDAY AT OCP · 01 GIFT CARD BONUS', G, 26)
         + head(['GIVE THE GIFT', 'OF THE CLASS.'], 150, [C, G])
         + para('Buy $100, gift a friend $100 more.', 46, C, 700, 1.25)
         + row([chip('ENDS TUE 12/1', 32), puck(120)], 24, 'center')
         + '</div>')
add('bf', R, 'BF-reel-cover-gift.dc.html', 'Gift card reel cover · 1080×1920', 1080, 1920, page('Black Friday gift card reel cover', 1080, 1920, inner, B))

# =============================================================
# BLACK FRIDAY PAID ADS
# =============================================================
AD_SIZES = [(1080, 1350), (1080, 1080), (1080, 1920), (300, 250), (728, 90), (160, 600), (320, 50)]
END_SHORT = 'ENDS TUE 12/1'


def ad(k, w, h):
    o = OFFERS[k]
    bridge = o.get('bridge')
    hl = o['ad']
    if (w, h) == (320, 50):
        return (f'<div style="flex: 1 1 auto; display: flex; align-items: center; gap: 10px; padding: 0 12px 0 6px">{puck(40)}'
                f'<p style="margin: 0; {KH}; font-size: 19px; line-height: 1; letter-spacing: 0.02em; color: {C}; white-space: nowrap">{esc(o["b320"])}</p></div>')
    if (w, h) == (728, 90):
        return (f'<div style="flex: 1 1 auto; display: flex; align-items: center; gap: 18px; padding: 0 24px 0 10px">{puck(72)}'
                f'<p style="margin: 0; {KH}; font-size: 30px; line-height: 1; letter-spacing: 0.02em; color: {C}; white-space: nowrap">{esc(o["b728"])}</p></div>')
    if (w, h) == (300, 250):
        return (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 8px; padding: 18px 18px 16px">'
                + row([eyebrow('BLACK FRIDAY AT OCP', G, 10, '0.18em'), puck(40)], 8, 'flex-start')
                + head(hl, 38 if len(hl) == 1 else 32, [C, G][:len(hl)] if len(hl) > 1 else [G], 0.86)
                + para(o['adline'], 13, C, 700, 1.3)
                + spacer()
                + row([button(o['cta'], 15, G, B, '10px 14px', 8), chip(END_SHORT, 12, PK, B, '6px 10px', 'align-self: center')], 8, 'center')
                + '</div>')
    if (w, h) == (160, 600):
        return (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 14px; padding: 18px 14px 18px; align-items: stretch">'
                + puck(64, 'align-self: center')
                + eyebrow('BLACK FRIDAY AT OCP', G, 10, '0.16em')
                + head(hl, 44 if len(hl) == 1 else 32, [C, G] if len(hl) > 1 else [G], 0.86)
                + photo(o['photo'].split(',')[0] + ']', '100%', 90 if bridge else 130, G)
                + para(o['adline'], 14, C, 700, 1.3)
                + (para(bridge, 11, S3, 500, 1.35) if bridge else '')
                + spacer()
                + chip(END_SHORT, 12, PK, B, '6px 10px', 'align-self: center')
                + button(o['cta'], 15, G, B, '12px 10px', 8, 'align-self: stretch')
                + '</div>')
    # Meta sizes
    story = h == 1920
    square = w == h
    pad = '250px 84px 250px' if story else '72px'
    ph_h = 700 if story else ((280 if (bridge or len(hl) > 1) else 360) if square else 520)
    hs = 170 if story else (130 if square else 150)
    if len(hl) > 1:
        hs = int(hs * 0.78)
    parts = [row([eyebrow('BLACK FRIDAY AT OCP', G, 24), puck(96 if not square else 84)], 24, 'center')]
    if not square or True:
        parts.append(video({'gift': 'studio', 'day': 'classloop'}[k], '100%', ph_h, G) if (story and k in ('gift', 'day')) else photo(o['photo'], '100%', ph_h, G))
    parts.append(head(hl, hs, [C, G] if len(hl) > 1 else [G]))
    parts.append(para(o['adline'], 46 if not square else 40, C, 700, 1.2))
    if bridge:
        parts.append(para(bridge, 26, S3, 500, 1.35))
    parts.append(spacer())
    parts.append(row([button(o['cta'], 40, G, B, '28px 44px', 14), chip(END_SHORT, 30)], 24, 'center', 'space-between'))
    return f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: {22 if square else 30}px; padding: {pad}">' + ''.join(parts) + '</div>'


AD_NAMES = {'gift': 'Gift card', 'day': '10-class pack', 'start': 'New-client starter'}
for k in ['gift', 'day', 'start']:
    R = f'Black Friday · Paid ads · {AD_NAMES[k]}'
    for (w, h) in AD_SIZES:
        plat = 'Meta' if w == 1080 else 'Google'
        add('bf', R, f'BF-ad-{k}-{w}x{h}.dc.html', f'{AD_NAMES[k]} · {plat} {w}×{h}', w, h,
            page(f'{AD_NAMES[k]} ad {w}x{h}', w, h, ad(k, w, h), B))

# =============================================================
# BLACK FRIDAY PRINT
# =============================================================
R = 'Black Friday · In-studio print'
cells = []
for i, k in enumerate(ORDER):
    o = OFFERS[k]
    br = para(o['bridge'], 15, B, 600, 1.4, f'padding-top: 10px; border-top: 1px solid {GD}') if o.get('bridge') else ''
    cells.append(f'<div style="display: flex; flex-direction: column; gap: 10px; padding: 24px; border: 1px solid {GD}; background: #FFFFFF00">'
                 f'<div style="display: flex; align-items: baseline; gap: 14px"><p style="margin: 0; {KH}; font-size: 64px; line-height: 0.8; color: {GD}">{o["n"]}</p>'
                 f'<p style="margin: 0; {KH}; font-size: 30px; letter-spacing: 0.06em; color: {B}">{o["name"]}</p></div>'
                 f'{para(o["line"], 18, B, 700, 1.4)}{para(o["fine"], 14, S7, 500, 1.45)}{br}</div>')
cells[-1] = cells[-1].replace('<div style="display: flex; flex-direction: column; gap: 10px;', '<div style="grid-column: 1 / -1; display: flex; flex-direction: column; gap: 10px;', 1)
inner = (f'<div style="flex: 1 1 auto; display: flex; flex-direction: column; gap: 28px; padding: 64px 60px 60px">'
         + row([eyebrow('BLACK FRIDAY AT OCP', B, 18), chip('NOV 17 TO DEC 1', 24)], 24, 'center')
         + head(['BLACK FRIDAY.', 'FIVE WAYS IN.'], 120, [B, GD])
         + f'<div style="display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px">{"".join(cells)}</div>'
         + spacer()
         + row([col([f'<p style="margin: 0; {KH}; font-size: 54px; line-height: 0.9; color: {B}">SCAN TO SHOP.</p>',
                     para('Ends Tuesday, Dec 1 at midnight. Or ask us at the desk.', 20, S7, 600, 1.4),
                     para(BF_URL, 16, S7, 500, 1.4), row([puck(84), handle(B, 18)], 14, 'center', 'flex-start')], 12, 'flex: 1 1 auto'),
                qr(300, f'[QR: {BF_URL}]')], 36, 'flex-end')
         + '</div>')
add('bf', R, 'BF-print-poster.dc.html', '11×17 poster (1056×1632)', 1056, 1632, page('Black Friday poster', 1056, 1632, inner, C))

inner = (frame(18) + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; gap: 16px; padding: 44px 40px 40px">'
         + row([eyebrow('GIFT CARDS', G, 13), chip('THRU TUE 12/1', 15, PK, B, '7px 12px')], 12, 'center')
         + head(['GIVE THE GIFT', 'OF THE CLASS', 'THEY KEEP', 'TALKING ABOUT.'], 60, [C, C, G, G], 0.86)
         + f'<p style="margin: 0; {MO}; font-size: 19px; font-weight: 700; line-height: 1.4; color: {C}">Buy a $100 gift card, get a $100 bonus gift card <span style="{CV}; font-size: 26px; color: {GW}">for a friend.</span></p>'
         + para('Bonus gift card valid through [date].', 13, S3, 500, 1.45)
         + spacer()
         + row([col([para('Scan or ask us at the desk.', 15, G, 700, 1.3), puck(64)], 12), qr(150, '[QR: gift card link]')], 16, 'flex-end')
         + '</div>')
add('bf', R, 'BF-print-counter-card.dc.html', 'Gift card counter card · 5×7 (480×672)', 480, 672, page('Gift card counter card', 480, 672, inner, B))

# =============================================================
# ARKETA PRODUCT IMAGES (780x438, export at 50% for 390x219)
# =============================================================
R = 'Black Friday · Arketa product images (780×438, export at 50% for 390×219)'
FOIL = 'background: linear-gradient(135deg, #8E6B2A 0%, #E9C977 25%, #FFE9A8 45%, #C9A24A 65%, #7A5520 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; color: transparent'
AW, AH = 780, 438
ARK_NOTES = {}


def ark_photo(img_key, eb, lines, sub, price, alt):
    return (f'<img src="{IMG[img_key]}" alt="{alt}" style="position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block">'
            f'<div aria-hidden="true" style="position: absolute; inset: 0; background: linear-gradient(to right, rgba(11,11,11,0.94) 0%, rgba(11,11,11,0.78) 45%, rgba(11,11,11,0.35) 100%)"></div>'
            + frame(20)
            + f'<div style="position: relative; flex: 1 1 auto; display: flex; flex-direction: column; gap: 10px; padding: 48px 54px 40px">'
            + eyebrow(eb, G, 15, '0.24em')
            + head(lines, 82, [C, C], 0.86, extra='margin-top: 12px')
            + f'<p style="margin: 6px 0 0; {KH}; font-size: 30px; letter-spacing: 0.06em; color: {G}">{esc(sub)}</p>'
            + f'<p style="margin: 0; {KH}; font-size: 64px; line-height: 0.9; color: {G}">{esc(price)}</p>'
            + '</div>' + puck(78, 'position: absolute; right: 54px; bottom: 46px'))


def ark_number(num, eb, word, price, small):
    return (frame(20)
            + f'<div style="position: relative; flex: 1 1 auto; display: flex; align-items: center; gap: 40px; padding: 40px 54px 40px 60px">'
            + f'<p style="margin: 0; {KH}; font-size: 260px; line-height: 0.8; letter-spacing: -0.02em; {FOIL}">{num}</p>'
            + '<div style="display: flex; flex-direction: column; gap: 8px; flex: 1 1 auto">'
            + eyebrow(eb, G, 15, '0.24em')
            + f'<p style="margin: 18px 0 0; {KH}; font-size: 64px; line-height: 0.88; color: {C}">{esc(word)}</p>'
            + f'<p style="margin: 0; {KH}; font-size: 54px; line-height: 0.9; color: {G}">{price}</p>'
            + para(small, 17, S2, 400, 1.45, 'margin-top: 22px')
            + '</div></div>' + puck(52, 'position: absolute; right: 50px; top: 46px'))


ARK = [
    ('gift', ark_photo('neon', 'BLACK FRIDAY · GIFT CARD', ['BUY ONE.', 'GIFT ONE.'], '$100 BONUS FOR A FRIEND', '$100', 'Member on the reformer under the neon OCP sign'),
     'Black Friday Gift Card: Buy $100, Gift a Friend $100',
     'Give the gift of the class they keep talking about. Buy a $100 OCP gift card and we email you code GIFTCARD100 for a bonus gift card, up to $100, to send a friend. Good at Bishop Arts, Uptown and Lower Greenville. Through Dec 1 only. Ends Tue, Dec 1 at midnight. Bonus gift card valid through [date]. Delivered [confirm: by email / printed in studio].'),
    ('day', ark_number('10', 'BLACK FRIDAY · CLASS PACK', 'SESSIONS', '$150 <span style="font-size: 30px; color: #84827B; text-decoration: line-through">$290</span>', '$15 a class. Any studio. 90 days to use them.'),
     'Black Friday 10-Class Pack',
     '10 classes for $150. That is $15 a class, regularly $290. Use them at any of our 3 studios. Expires 90 days from purchase. One per person [confirm]. Through Dec 1 only. Ends Tue, Dec 1 at midnight.'),
    ('start', ark_photo('firstclass', 'BLACK FRIDAY · NEW CLIENTS', ['1 WEEK', 'UNLIMITED'], 'CODE BLACKFRIDAY', '$39', 'Instructor helping a new client on the reformer'),
     'Black Friday New Client Week: 1 Week Unlimited',
     'New to OCP? Start here. One week of unlimited classes at all 3 studios for $39 with code BLACKFRIDAY (regularly $59). Real Dallas people, loud music, instructors who actually see your form. New clients only. Your week starts [at purchase / at first class: confirm]. Join a membership by Dec 31 and keep today’s membership rates for all of 2027. Ends Tue, Dec 1 at midnight.'),
    ('bundle', ark_number('20', 'BLACK FRIDAY · GIFT BUNDLE', 'SESSIONS + MERCH', '$400', 'Grip socks, hoodie and tote included. 12 months to use the classes.'),
     'Black Friday Gift Bundle: 20 Classes + Merch',
     '20 classes plus OCP grip socks, the Anti-Pilates Pilates Club hoodie and the Anti-Pilates Pilates Club tote. All for $400. 20 classes alone are regularly $560. Classes expire 12 months from purchase. Merch picked up in studio [confirm], while supplies last. Give it or keep it. Ends Tue, Dec 1 at midnight.'),
    ('unl', ark_photo('greenville84', 'NEW MEMBERS · 3-MONTH COMMITMENT', ['ALL-STUDIO', 'UNLIMITED'], 'STAYS $199 · + $50 GIFT CARD', '$199/MO', 'A full class mid-movement'),
     'Black Friday All-Studio Unlimited: $199/mo',
     'Unlimited classes at all 3 studios for $199 a month, plus a $50 OCP gift card. Commit to your first 3 months and your rate stays $199 after that. Includes 14-day booking and a free guest pass every month [confirm]. New members only. Ends Tue, Dec 1 at midnight.'),
]
for k, inner, name, desc in ARK:
    fn = f'BF-arketa-{k}.dc.html'
    add('bf', R, fn, f'Arketa · {name}', AW, AH, page(f'Arketa image {name}', AW, AH, inner, B))
    price = {'gift': '$100 (buyer gets code GIFTCARD100 by email for a bonus gift card up to $100 to send a friend)', 'day': '$150 (compare at $290)', 'start': '$59, $39 with code BLACKFRIDAY',
             'bundle': '$400 (20-class pack compare at $560)', 'unl': '$199/mo, 3-month minimum, stays $199 after'}[k]
    link = OFFERS[k].get('url', '[Arketa checkout link: send it over]')
    ARK_NOTES[fn] = f'ARKETA NAME\n{name}\n\nPRICE\n{price}\n\nCHECKOUT LINK\n{link}\n\nDESCRIPTION\n{desc}'

# =============================================================
# WRITE + LAYOUT
# =============================================================
PAGES = [{'id': 'lockin', 'name': 'Lock-In (members only)'}, {'id': 'bf', 'name': 'Black Friday (non-members + gifts)'}]
boards, order, notes = {}, [], {}
for pg in ['lockin', 'bf']:
    y = 300
    rows_ = []
    for b in BOARDS:
        if b[0] != pg:
            continue
        if not rows_ or rows_[-1][0] != b[1]:
            rows_.append((b[1], []))
        rows_[-1][1].append(b)
    for ri, (rt, items) in enumerate(rows_):
        x = 0
        maxh = 0
        for (_, _, fname, title, w, h, _) in items:
            boards[fname] = {'x': x, 'y': y, 'w': w, 'h': h, 'title': title, 'page': pg}
            order.append(fname)
            x += w + 80
            maxh = max(maxh, h)
        nid = f'{pg}-row{ri + 1}'
        notes[nid] = {'x': 0, 'y': y - 260, 'text': rt, 'kind': 'title1', 'maxW': max(1200, x - 80), 'page': pg}
        extra = 0
        for (_, _, fname, _, w, h, _) in items:
            if fname in ARK_NOTES:
                nk = fname.replace('.dc.html', '').replace('BF-', '') + '-desc'
                notes[nk] = {'x': boards[fname]['x'], 'y': y + h + 60, 'text': ARK_NOTES[fname], 'w': w, 'size': 's', 'page': pg}
                extra = 1100
        y += maxh + 420 + extra

now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
index = {'v': 3, 'createdOnFiles': {'v': 1, 'at': now}, 'title': 'OCP Holiday Campaigns 2026',
         'launch': {'view': 'canvas', 'page': 'lockin'}, 'pages': PAGES, 'boards': boards, 'order': order, 'notes': notes,
         'designSystems': [{'title': 'Oak Cliff Pilates Design System', 'namespace': DS, 'artifact': DS_URL, 'version': '1794855853-cadb', 'copiedAt': now}]}

os.makedirs(os.path.join(OUT, 'project'), exist_ok=True)
# Keep the published canvas's creation stamp and design-system record so a republish doesn't reset them.
_prev = os.path.join(OUT, 'project', 'canvas.json')
if os.path.exists(_prev):
    _old = json.load(open(_prev))
    index['createdOnFiles'] = _old.get('createdOnFiles', index['createdOnFiles'])
    index['designSystems'] = _old.get('designSystems', index['designSystems'])
bad = []
for (_, _, fname, _, _, _, src) in BOARDS:
    for ch in ['—', '–']:
        if ch in src:
            bad.append((fname, 'dash'))
    for phrase in ['wellness journey', 'find your zen', 'transform your body', 'new year new you', 'discount']:
        if phrase in src.lower():
            bad.append((fname, phrase))
    open(os.path.join(OUT, 'project', fname), 'w', encoding='utf-8').write(src)
json.dump(index, open(os.path.join(OUT, 'project', 'canvas.json'), 'w'), indent=1)
print('boards', len(BOARDS), 'bad', bad)
for b in BOARDS:
    print(b[0], b[2], b[4], b[5])
