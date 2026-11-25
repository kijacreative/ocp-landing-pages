# OCP landing pages

Static landing pages served at `lp.oakcliffpilates.com`. Each page lives in its own folder and is served at that path.

| Path | Page |
| --- | --- |
| `/59unlimited` | $59 one week unlimited, Arketa checkout embedded |
| `/daylightunlimited` | Daylight Unlimited, $139/mo weekday 10 to 4, Arketa checkout embedded |
| `/ratelock` | Members-only 2027 rate lock: choose a plan before Dec 31, 2026, links to Arketa checkout |
| `/blackfriday` | Black Friday Nov 17 to Dec 1, 2026: all five offers with Arketa checkout links, a countdown, and a "That's a wrap" state after the sale (preview with `?ended=1`) |
| `/smallbusinesssaturday` | Shop Small with OCP: free Small Business Saturday (Nov 28, 2026) feature sign-up for Dallas businesses, with logo and photo upload. Closes 12:00 AM Central, Thu Nov 26 (preview the closed state with `?closed=1`). `/shop-small` redirects here |
| `/cliffclub` | Cliff Club invite list sign-up plus every upcoming Cliff Club event, rendered from `cliffclub/events.json` |
| `/signatures` | Team email signatures (Kiel, Isabel, Charley, Stephanie, Amanda, general OCP) to copy into Gmail, Apple Mail or Outlook. `?p=isabel` opens one person. Not indexed |

### Email signatures

`/signatures` builds each signature from the list at the top of the script in `signatures/index.html` (names, titles, phones, emails, default booking links). Anyone can type a booking link before copying; it is remembered in that browser only. Photos are 300x300 JPEGs in `signatures/img/`, and `signatures/photos.json` says which file each signature uses.

"Change photo" crops the new photo in the browser and sends it to `api/signature-photo.js`, a Vercel function that commits it to `main` as `signatures/img/{person}-{timestamp}.jpg` and updates `photos.json` in the same commit. Vercel redeploys and the page unlocks Copy once the photo is live (about a minute). Old photos stay so emails already sent keep loading them. To turn it on (once), in Vercel > Project > Settings > Environment Variables (Production), add:

1. `SIGNATURE_UPLOAD_KEY`: a team passcode. People type it on the page to save a photo.
2. `GITHUB_TOKEN`: a fine-grained GitHub token limited to `kijacreative/ocp-landing-pages` with Contents: Read and write.

Then redeploy. Until both are set, saving a photo says "Photo saving is not set up yet".

### Cliff Club events

Add, edit or remove events in `cliffclub/events.json`; the page never needs touching. Past dates hide themselves (Dallas time) and the list sorts by date. Any value in `[brackets]` shows as written, and a bracketed `url` shows a disabled "Link coming soon" button. Optional `booked` (a number) fills the spots-left meter; without it the meter shows every spot open. Drop event photos (1200x540) into `cliffclub/img/` at the path in `image`; until a file exists, the card shows a labeled photo slot. The share image `cliffclub/img/og.jpg` comes from `tools/cliff-club-og.html`; re-render it with `./tools/render-cliff-club-og.sh`.

### Cliff Club invite list

Sign-ups land in the Google Sheet [Cliff Club List Sign-ups](https://docs.google.com/spreadsheets/d/1hp-_Xs9iiST08QYspq-KrlQyHbxIS_jg0vPQSO6n464/edit), tab `Sign-ups`, one row per person. A Google Apps Script web app receives the form and writes the row. To connect it (once):

1. Open the Sheet, then Extensions > Apps Script.
2. Replace the editor contents with `tools/cliff-club-list-apps-script.gs` and save.
3. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Deploy and approve the access prompt.
4. Copy the web app URL (ends in `/exec`) into `CLIFF_CLUB_LIST_ENDPOINT` at the top of the script in `cliffclub/index.html`, then deploy the site.

After editing the script, use Deploy > Manage deployments > Edit > New version so the same URL keeps working.

### Shop Small sign-ups

Each sign-up from `/smallbusinesssaturday` goes to a Google Apps Script web app (`tools/shop-small-apps-script.gs`) that adds a row to the "Sign-ups" tab of the Shop Small Sheet, saves the logo and photo to the Drive folder "Shop Small 2026 uploads" as `{business-slug}-logo.ext` and `{business-slug}-photo.ext`, emails isabel@oakcliffpilates.com every field with links to both files (subject `Shop Small sign-up: {Business name}`), and emails the business its confirmation. It turns away anything after 12:00 AM Central, Thu Nov 26. To connect it (once):

1. Make a Google Sheet named "Shop Small 2026 Sign-ups", then Extensions > Apps Script.
2. Replace the editor contents with `tools/shop-small-apps-script.gs` and save.
3. Choose `setup` in the function menu and Run it. Approve the access prompt. It makes the tab and the Drive folder and shares both with Isabel.
4. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone. Deploy.
5. Copy the web app URL (ends in `/exec`) into `SBS_FORM_ENDPOINT` at the top of the script in `smallbusinesssaturday/index.html`, then deploy the site.

Until step 5 is done the live form shows "That didn't go through". Emails send from the Google account that deployed the script.

Exporting on Wednesday night: in the Sheet, File > Download > Comma-separated values (.csv). In Drive, right-click the "Shop Small 2026 uploads" folder > Download, and Drive zips every file.

The share image `smallbusinesssaturday/img/og.jpg` comes from `tools/shop-small-og.html`; re-render it with `./tools/render-shop-small-og.sh`.

The Instagram feed post `smallbusinesssaturday/social/post.jpg` (1080x1350) and story `smallbusinesssaturday/social/story.jpg` (1080x1920) come from `tools/shop-small-social.html`; re-render both with `./tools/render-shop-small-social.sh`.

The root `/` redirects to oakcliffpilates.com. No build step: Vercel serves the folder as-is.

`blackfriday/` also holds the source for the holiday 2026 Lock-In and Black Friday campaign assets. Only `index.html` and `media/` are served; `.vercelignore` keeps the generator, canvas and drafts off the site. See `blackfriday/README.md`.

## Emails

| Path | What |
| --- | --- |
| `/emails/trial/` | Preview of the 1-week unlimited trial conversion sequence (9 emails) |
| `/emails/trial/<name>.html` | Each email's HTML, ready to paste into the sending platform |
| `/emails/ratelock/` | Preview of the 2027 rate lock series to members (6 sends Nov 3 to Dec 31, the first in 4 versions by membership) |
| `/emails/first-visit.html` | Thank-you email sent after a client's first class, with Amanda's animated wave |
| `/emails/sad-to-see-you-go.html` | Goodbye email for cancelled members, with the COMEBACK $10-off offer |
| `/emails/happy-birthday.html` | Birthday email with a free 7-day guest pass for a friend |
| `/emails/we-miss-you.html` | Win-back email for lapsed clients, with the $10 gift card offer |
| `/emails/black-friday-early-access.html` | Black Friday early access, Tue Nov 17: all five offers with photos and their checkout links, plus a button to `/blackfriday`. Photos are `emails/img/bf-*.jpg` |
| `/emails/black-friday-gifts.html` | Black Friday gifts send, Fri Nov 20: the $100 gift card bonus (with how it works) and the 20-class gift bundle, plus a link to all five offers. Hero is `emails/img/bf-gifts-hero.jpg` |
| `/emails/black-friday-friday.html` | Black Friday "Black Friday is Friday" send, Wed Nov 25, to the full list: all five offers as a compact linked list with one Shop the deals button. Hero is `emails/img/bf-friday-hero.jpg` |
| `/emails/amanda-expired-pack.html` | Personal note from Amanda to clients with expired class packs: the Black Friday 10-class pack, $150 through Dec 1. Plain letter style with her signature photo. Uses the `{{clientFirstName}}` merge tag |
| `/emails/black-friday-unlimited.html` | Black Friday unlimited send, Mon Nov 23, to non-members, lapsed clients and intro buyers: $199 All-Studio Unlimited for new members, then the $39 new-client week as the softer option. Hero is `emails/img/bf-unlimited-hero.jpg` |
| `/emails/black-friday-all-offers.html` | Black Friday all-offers send, Sat Nov 21, to the full list: all five offers with checkout buttons. Hero is `emails/img/bf-all-offers-hero.jpg` |
| `/emails/black-friday-start-here.html` | Black Friday "Start here" send, Sun Nov 29, to non-members: the $39 new-client week (code BLACKFRIDAY) and the 10-class pack, plus a link to all five offers. Hero is `emails/img/bf-start-here-hero.jpg` |
| `/emails/black-friday-gift-card-bonus.html` | Black Friday: sends automatically after a $100 gift card purchase. Thanks the buyer and gives code GIFTCARD100 for a bonus gift card up to $100 for a friend, via the Arketa gifting page |
| `/emails/black-friday-gift-card-bonus-50.html` | Same as the $100 version for a $50 gift card purchase: code GIFTCARD50 for a bonus gift card up to $50 for a friend |
| `/emails/black-friday-bundle-pickup.html` | Black Friday: sends after the 20-class gift bundle is bought. Shows the grip socks, hoodie and tote and asks the buyer to email info@oakcliffpilates.com with their pickup studio and hoodie size |
| `/emails/gift-card-delivery.html` | Follow-up to "We miss you": delivers the $10 gift card (code BOOKED) once a lapsed client books |
| `/emails/pilates-in-the-park.html` | Free mat Pilates with Daisy at Halperin Park, Sun Oct 25, 9 AM, with the Arketa RSVP link |
| `/emails/pilates-and-pours.html` | Pilates + Pours evening edition with Amanda at Sixty Vines Uptown, Sun Nov 15, 5/6/7 PM, with the Triple Seat ticket links |
| `/emails/cliff-club-dj-mat-class.html` | Blast for the first Cliff Club pop-up: DJ mat class with Amber and DJ IAMYU, Fri Nov 20, 6 PM, OCP Lower Greenville, with the Arketa booking link |
| `/emails/cliff-club-dj-unlimited-vip.html` | Unlimited members only: free spot at the Nov 20 DJ mat class as a thank-you, with code CLIFFCLUBVIP |
| `/emails/shop-small.html` | Shop Small with OCP invite to local businesses: free spot in the Fri Nov 27 email and on Instagram, with a $0.00 receipt and a button to `/smallbusinesssaturday`. Form closes before Thu Nov 26 |
| `/emails/img/` | Images the emails load, so they can use absolute URLs |

The email HTML is generated. Edit `tools/build-trial-emails.py`, then run `python3 tools/build-trial-emails.py`.
The rate lock emails work the same way: edit `tools/build-ratelock-emails.py`, then run `python3 tools/build-ratelock-emails.py`.
Never rename or delete anything in `/emails/img/` once an email has been sent: inboxes keep loading it.
