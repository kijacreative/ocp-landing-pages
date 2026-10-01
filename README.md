# OCP landing pages

Static landing pages served at `lp.oakcliffpilates.com`. Each page lives in its own folder and is served at that path.

| Path | Page |
| --- | --- |
| `/59unlimited` | $59 one week unlimited, Arketa checkout embedded |

The root `/` redirects to oakcliffpilates.com. No build step: Vercel serves the folder as-is.

## Emails

| Path | What |
| --- | --- |
| `/emails/trial/` | Preview of the 1-week unlimited trial conversion sequence (9 emails) |
| `/emails/trial/<name>.html` | Each email's HTML, ready to paste into the sending platform |
| `/emails/img/` | Images the emails load, so they can use absolute URLs |

The email HTML is generated. Edit `tools/build-trial-emails.py`, then run `python3 tools/build-trial-emails.py`.
Never rename or delete anything in `/emails/img/` once an email has been sent: inboxes keep loading it.
