// Receives The Key waitlist form (lp.oakcliffpilates.com/thekey) and appends a row to the
// "The Key Waitlist" Google Sheet.
//
// Setup, once:
// 1. Open the sheet > Extensions > Apps Script, paste this file in, save.
// 2. Deploy > New deployment > Web app. Execute as: Me. Who has access: Anyone.
// 3. Copy the /exec URL into WAITLIST_ENDPOINT in thekey/index.html.
// After editing this script, use Deploy > Manage deployments > Edit > New version, so the URL stays the same.

const SHEET_ID = '1oBEXo5v2TGiyGNTyDv0hwt2e0GV4UMJ_rnvDVvyEifY';
const FIELDS = ['first_name', 'last_name', 'email', 'phone', 'home_studio', 'source'];

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p.company) return json({ ok: true }); // honeypot: bots fill the hidden field
  if (!p.email || !p.first_name) return json({ ok: false, error: 'missing fields' });

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sheet = SpreadsheetApp.openById(SHEET_ID).getSheets()[0];
    sheet.appendRow([new Date()].concat(FIELDS.map(function (f) { return clean(p[f]); })));
  } finally {
    lock.releaseLock();
  }
  return json({ ok: true });
}

// Keep values short and stop them being read as spreadsheet formulas.
function clean(v) {
  v = String(v || '').trim().slice(0, 200);
  return /^[=+\-@]/.test(v) ? "'" + v : v;
}

function json(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
