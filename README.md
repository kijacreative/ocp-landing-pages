# OCP landing pages

Static landing pages served at `lp.oakcliffpilates.com`. Each page lives in its own folder and is served at that path.

| Path | Page |
| --- | --- |
| `/59unlimited` | $59 one week unlimited, Arketa checkout embedded |
| `/daylightunlimited` | Daylight Unlimited, $139/mo weekday 10 to 4, Arketa checkout embedded |
| `/ratelock` | Members-only 2027 rate lock: choose a plan before Dec 31, 2026, links to Arketa checkout |

The root `/` redirects to oakcliffpilates.com. No build step: Vercel serves the folder as-is.

## Emails

| Path | What |
| --- | --- |
| `/emails/trial/` | Preview of the 1-week unlimited trial conversion sequence (9 emails) |
| `/emails/trial/<name>.html` | Each email's HTML, ready to paste into the sending platform |
| `/emails/first-visit.html` | Thank-you email sent after a client's first class, with Amanda's animated wave |
| `/emails/sad-to-see-you-go.html` | Goodbye email for cancelled members, with the COMEBACK $10-off offer |
| `/emails/happy-birthday.html` | Birthday email with a free 7-day guest pass for a friend |
| `/emails/we-miss-you.html` | Win-back email for lapsed clients, with the $10 gift card offer |
| `/emails/gift-card-delivery.html` | Follow-up to "We miss you": delivers the $10 gift card (code BOOKED) once a lapsed client books |
| `/emails/pilates-in-the-park.html` | Free mat Pilates with Daisy at Halperin Park, Sun Oct 25, 9 AM, with the Arketa RSVP link |
| `/emails/img/` | Images the emails load, so they can use absolute URLs |

The email HTML is generated. Edit `tools/build-trial-emails.py`, then run `python3 tools/build-trial-emails.py`.
Never rename or delete anything in `/emails/img/` once an email has been sent: inboxes keep loading it.
