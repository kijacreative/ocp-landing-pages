# OCP landing pages

Static landing pages served at `lp.oakcliffpilates.com`. Each page lives in its own folder and is served at that path.

| Path | Page |
| --- | --- |
| `/59unlimited` | $59 one week unlimited, Arketa checkout embedded |
| `/daylightunlimited` | Daylight Unlimited, $139/mo weekday 10 to 4, Arketa checkout embedded |
| `/ratelock` | Members-only 2027 rate lock: choose a plan before Dec 31, 2026, links to Arketa checkout |
| `/upgrade25` | Intro offer clients: $25 off the first month with code UPGRADE25, plus the 2027 rate lock if they join before Dec 31, 2026 |
| `/welcome` | First-timer landing page for New Client Special buyers: the three intro offers, first-class tips, a class guide, the studios, and UPGRADE25 memberships plus class packs for after the intro |
| `/cliffclub` | Cliff Club invite list sign-up plus every upcoming Cliff Club event, rendered from `cliffclub/events.json` |

### Cliff Club events

Add, edit or remove events in `cliffclub/events.json`; the page never needs touching. Past dates hide themselves (Dallas time) and the list sorts by date. Any value in `[brackets]` shows as written, and a bracketed `url` shows a disabled "Link coming soon" button. Optional `booked` (a number) fills the spots-left meter; without it the meter shows every spot open. Drop event photos (1200x540) into `cliffclub/img/` at the path in `image`; until a file exists, the card shows a labeled photo slot. The share image `cliffclub/img/og.jpg` comes from `tools/cliff-club-og.html`; re-render it with `./tools/render-cliff-club-og.sh`.

### Cliff Club invite list

Sign-ups land in the Google Sheet [Cliff Club List Sign-ups](https://docs.google.com/spreadsheets/d/1hp-_Xs9iiST08QYspq-KrlQyHbxIS_jg0vPQSO6n464/edit), tab `Sign-ups`, one row per person. A Google Apps Script web app receives the form and writes the row. To connect it (once):

1. Open the Sheet, then Extensions > Apps Script.
2. Replace the editor contents with `tools/cliff-club-list-apps-script.gs` and save.
3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Deploy and approve the access prompt.
4. Copy the web app URL (ends in `/exec`) into `CLIFF_CLUB_LIST_ENDPOINT` at the top of the script in `cliffclub/index.html`, then deploy the site.

After editing the script, use Deploy > Manage deployments > Edit > New version so the same URL keeps working.

The root `/` redirects to oakcliffpilates.com. No build step: Vercel serves the folder as-is.

## Emails

| Path | What |
| --- | --- |
| `/emails/trial/` | Preview of the 1-week unlimited trial conversion sequence (9 emails) |
| `/emails/trial/<name>.html` | Each email's HTML, ready to paste into the sending platform |
| `/emails/welcome/` | Preview of the new client welcome series (3 emails, each with its text message), triggered by any New Client Special purchase and pointing to `/welcome` |
| `/emails/ratelock/` | Preview of the 2027 rate lock series to members (6 sends Nov 3 to Dec 31, the first in 4 versions by membership), plus one-off sends to intro offer clients (UPGRADE25, links to `/upgrade25`), prepay members and class pack buyers |
| `/emails/first-visit.html` | Thank-you email sent after a client's first class, with Amanda's animated wave |
| `/emails/sad-to-see-you-go.html` | Goodbye email for cancelled members, with the COMEBACK $10-off offer |
| `/emails/happy-birthday.html` | Birthday email with a free 7-day guest pass for a friend |
| `/emails/we-miss-you.html` | Win-back email for lapsed clients, with the $10 gift card offer |
| `/emails/gift-card-delivery.html` | Follow-up to "We miss you": delivers the $10 gift card (code BOOKED) once a lapsed client books |
| `/emails/pilates-in-the-park.html` | Free mat Pilates with Daisy at Halperin Park, Sun Oct 25, 9 AM, with the Arketa RSVP link |
| `/emails/pilates-and-pours.html` | Pilates + Pours evening edition with Amanda at Sixty Vines Uptown, Sun Nov 15, 5/6/7 PM, with the Triple Seat ticket links |
| `/emails/img/` | Images the emails load, so they can use absolute URLs |

The email HTML is generated. Edit `tools/build-trial-emails.py`, then run `python3 tools/build-trial-emails.py`.
The welcome series works the same way: edit `tools/build-welcome-emails.py` (it reuses the trial builder's blocks), then run `python3 tools/build-welcome-emails.py`. The texts live in that file too.
The rate lock emails work the same way: edit `tools/build-ratelock-emails.py`, then run `python3 tools/build-ratelock-emails.py`.
Never rename or delete anything in `/emails/img/` once an email has been sent: inboxes keep loading it.
